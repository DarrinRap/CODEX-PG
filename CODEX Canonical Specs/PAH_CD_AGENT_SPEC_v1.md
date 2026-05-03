# PAH CD Agent Specification v1.1

**Status:** APPROVED — Q1-Q5 decisions locked by Darrin 2026-05-03. Ready for implementation dispatch.
**Date:** 2026-05-03
**Author:** Claude Desktop
**Location:** `C:\CODEX PG\CODEX Canonical Specs\PAH_CD_AGENT_SPEC_v1.md`
**Implements:** Autonomous Claude Desktop response agent running inside PAH

## Darrin Decisions (Q1-Q5) — LOCKED 2026-05-03

| Q | Question | Decision |
|---|----------|----------|
| Q1 | Daily budget cap | **$1.00/day** |
| Q2 | Step 0 auto-approval | **Auto-ack when all defaults clear** — no Step 0 exemption |
| Q3 | Commit-go exclusion | **Auto-ack docs-only commit-gos** — hard-exclude feature/fix commit-gos |
| Q4 | Dry-run duration | **1 session** before enabling live mode |
| Q5 | Codex inbox scope | **Auto-ack Codex ack_only messages** — same rules as CC |

---

## 1. Problem Statement

Claude Desktop (CD) is a chat interface at claude.ai. It only responds when Darrin
types a message. This means every mailbox message in `cc_mailbox\CLAUDE Inbox\` that
requires a CD response — acks, commit-gos, dispatch routing — blocks until Darrin
opens a browser tab and types.

The CD Agent solves this by running a background process (inside PAH) that:

1. Watches `cc_mailbox\CLAUDE Inbox\` for new unread messages
2. Classifies each message by its required response class
3. For messages that do not require Darrin judgment: calls the Anthropic API,
   generates a response, and writes it to the correct outbox
4. For messages that require Darrin: sends a toast/email notification and halts

The result: CC and Codex receive acks and routing responses within seconds of filing
them, without Darrin needing to open a chat. Darrin is only interrupted for genuine
decisions (commit-go, new scope, design questions).

---

## 2. Scope

### 2.1 In scope — v1

- Watching `cc_mailbox\CLAUDE Inbox\` for new files
- Watching `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\` for new files
- Classifying messages by `approval_boundary` and `requires_darrin_decision` fields
- Calling the Anthropic API (claude-sonnet-4-20250514) for `ack_only` messages
- Writing response files to CC Inbox or Codex Inbox
- Notifying Darrin (PAH desktop toast + email) for decisions that require him
- Dry-run mode: classify and generate responses but write nothing
- Audit log of every classification decision and API call
- Rate limiting and budget cap (USD per day)
- Idempotency: never process the same message twice

### 2.2 Out of scope — v1

- Responding to messages with `approval_boundary: commit_go_required` autonomously
  (these always interrupt Darrin — they change the repo)
- Responding to messages with `requires_darrin_decision: true` autonomously
- Running git commands (commit, push, vcommit)
- Dispatching new CC or Codex tasks that were not already authorized
- Editing BUGS.md, HANDOFF.md, or any repo file
- Calling any external API other than the Anthropic messages endpoint
- Replacing the claude.ai CD session for design discussions or strategic decisions

---

## 3. Architecture

### 3.1 Placement inside PAH

The CD Agent is a new module inside the existing PAH application:

```
C:\CODEX PG\CODEX Agent Hub\
  pah_cd_agent\
    __init__.py
    agent.py          # Main agent loop: watch → classify → act
    classifier.py     # Message classification engine
    context.py        # Context assembler (builds API prompt)
    api_client.py     # Anthropic API wrapper
    responder.py      # Response writer (mailbox file generator)
    budget.py         # Daily USD budget tracker
    audit.py          # Append-only audit log
    config.py         # Configuration schema + loader
    dry_run.py        # Dry-run mode utilities
```

PAH's existing infrastructure is reused:
- `pah_mailbox.paths` — canonical inbox/outbox paths
- `pah_mailbox.idempotency` — `processed_message_event_status` / `record_processed_message_event`
- `pah_mailbox.atomic` — `atomic_write_text` for safe file writes
- `pah_notifications.desktop` — desktop toast
- `pah_security.approvals` — approval record validation (read-only in v1)
- `pah_core.schema` — `extract_message_metadata`, `validate_message_text`
- `pah_core.read_state` — mark messages as read

### 3.2 Trigger mechanism

PAH already runs a file-watcher thread (`WATCHER_LOCK`, `WATCHER_STATE_PATH`,
`STALE_UNREAD_SECONDS`). The CD Agent registers as a watcher consumer alongside
the existing dashboard refresh. On every sweep cycle (configurable, default 15s),
the agent checks both watched inboxes for unread files matching
`^20\d{6}.*\.md$` that have not been processed by the CD Agent.

New PAH config key `cd_agent.enabled` (bool, default false) gates the entire
agent. When false, the watcher loop still runs but the CD Agent consumer is a no-op.

### 3.3 Flow overview

```
PAH watcher detects new file in CLAUDE Inbox
         │
         ▼
pah_cd_agent.agent.on_new_message(path)
         │
         ▼
classifier.classify(message) → MessageClass
         │
    ┌────┴────────────────────┬─────────────────────────┐
    │                         │                         │
ack_only               darrin_required          not_actionable
    │                         │                         │
    ▼                         ▼                         ▼
budget.check_ok()     notify_darrin()          mark_read(), skip
    │                  (toast + email)
    ▼
context.build(message)
    │
    ▼
api_client.call(context) → response_text
    │
    ▼
responder.write(response_text, target_inbox)
    │
    ▼
mark_read(), audit_log(), record_processed_event()
```

---

## 4. Message Classification

### 4.1 MessageClass enum

```python
class MessageClass(str, Enum):
    ACK_ONLY          = "ack_only"          # Safe to auto-respond
    DARRIN_REQUIRED   = "darrin_required"   # Must interrupt Darrin
    NOT_ACTIONABLE    = "not_actionable"    # Already replied, or malformed
```

### 4.2 Classification rules (ordered; first match wins)

| Priority | Condition | Class |
|---|---|---|
| 1 | File already in `processed_messages` idempotency log | NOT_ACTIONABLE |
| 2 | File fails `validate_message_text()` (malformed frontmatter) | DARRIN_REQUIRED (malformed) |
| 3 | `thread_status: closed` in frontmatter | NOT_ACTIONABLE |
| 4 | `requires_darrin_decision: true` in frontmatter | DARRIN_REQUIRED |
| 5 | `approval_boundary: commit_go_required` | DARRIN_REQUIRED |
| 6 | `approval_boundary: ack_only` AND message type in SAFE_TYPES | ACK_ONLY |
| 7 | `type` in ESCALATE_TYPES | DARRIN_REQUIRED |
| 8 | Default (unknown type or missing boundary) | DARRIN_REQUIRED |

### 4.3 SAFE_TYPES (auto-respondable in v1)

These message types can be acknowledged or routed without Darrin judgment:

```python
SAFE_TYPES = {
    "ack",                    # Pure acknowledgement
    "shipped",                # Agent reports a task shipped
    "impl_start",             # Agent reports implementation started
    "step0",                  # Step 0 audit report (classify + ack defaults)
    "rtc",                    # Ready-to-commit (ack only; commit-go still needs Darrin)
    "protocol_consult",       # Protocol consult (CD can respond to format proposals)
    "ba_fix_dispatch",        # BA fix dispatch (CD can ack + route to CC or Codex)
    "directive_request",      # Agent asking for next direction (if task queue covers it)
    "hold_status_request",    # Agent confirming hold status
    "completion_report",      # Agent reporting task complete
}
```

### 4.4 ESCALATE_TYPES (always Darrin)

```python
ESCALATE_TYPES = {
    "design_decision",        # Any design question
    "new_scope_proposal",     # Proposes work outside existing queue
    "spec_amendment",         # Proposes a spec change
    "approval_request",       # Requests a protected action approval
    "urgent_request",         # priority: urgent in frontmatter
    "ba_rebuild_rfc",         # BA rebuild RFC (architectural)
}
```

### 4.5 Escalation on `priority: urgent`

Any message with `priority: urgent` in frontmatter is immediately classified
DARRIN_REQUIRED regardless of type, bypassing SAFE_TYPES. This is the existing
urgent-flag protocol from mailbox v3.

### 4.6 Step 0 classification sub-logic

Step 0 audits (`type: step0`) contain discrepancies for adjudication. The classifier
inspects the message body for a "HOLD state" section:

- If `HOLDING for: go ... implementation` and all discrepancy recommendations are
  clearly labeled `(recommended)`: classify ACK_ONLY. The API call confirms
  defaults and issues a "go with defaults" response.
- If any discrepancy says `requires_darrin_decision: true` in the message body
  (distinct from frontmatter): escalate to DARRIN_REQUIRED.
- If the body contains phrases like "design question", "need Darrin's input",
  "blocking on decision": escalate to DARRIN_REQUIRED.

---

## 5. Context Assembly

### 5.1 Purpose

The Anthropic API call needs enough context for the model to produce a correct,
project-specific response — not a generic ack. The context assembler builds the
system prompt and the user message from:

- The incoming mailbox message (full body)
- Session state (current HEAD, open bugs count, active tasks)
- HANDOFF.md excerpt (latest Deferred section + Next candidates)
- Recent git log (last 10 commits)
- Role definition (Claude Desktop as orchestrator)

### 5.2 System prompt (static, versioned in config)

```
You are Claude Desktop (CD), the orchestrator and spec author for the
Panda Gallery project. You are operating in CD Agent mode — a headless
automated mode where you respond to mailbox messages from CC (Claude Code)
and Codex without Darrin present.

Your role in this mode:
- Acknowledge task completions accurately
- Confirm Step 0 defaults when all discrepancy recommendations are clear
- Route work to the correct next agent
- Surface items that require Darrin judgment back to PAH (do not resolve them)

CONSTRAINTS:
- You may NOT issue commit-go approvals. Those always require Darrin.
- You may NOT authorize new scope, new tasks, or spec changes.
- You may NOT edit BUGS.md, HANDOFF.md, or any repo file.
- You may NOT make design decisions or UX judgments.
- If you are uncertain about any decision, return ESCALATE_TO_DARRIN.

OUTPUT FORMAT:
Respond with a valid mailbox message body (YAML frontmatter + Markdown body).
The frontmatter must include: schema_version, message_id, in_reply_to,
thread_id, from (always "CLAUDE"), to, date, subject, type (always "ack"
or "ack_and_dispatch"), requires_darrin_decision (always false for your
responses), approval_boundary (always "ack_only").
If you cannot produce a valid ack, output only the single line:
ESCALATE_TO_DARRIN: <reason>
```

### 5.3 User message construction

```
=== INCOMING MESSAGE ===
{full_message_file_text}

=== SESSION CONTEXT ===
HEAD: {git_head_hash} {git_head_subject}
VERSION: {version_txt}
OPEN BUGS: {open_bug_count}
TASK QUEUE SUMMARY:
{task_queue_excerpt}  (last 20 lines of §A active rows)

=== HANDOFF EXCERPT ===
{handoff_deferred_section}
{handoff_next_candidates_section}

=== RECENT COMMITS ===
{git_log_10}

=== INSTRUCTIONS ===
Produce a valid mailbox ack for the incoming message above.
Target inbox: {target_inbox_name}
```

### 5.4 Context assembly implementation

```python
class ContextAssembler:
    def build(self, message: Message, target: str) -> dict:
        return {
            "system": self._load_system_prompt(),
            "user": self._build_user_message(message, target),
        }

    def _build_user_message(self, message: Message, target: str) -> str:
        return "\n".join([
            "=== INCOMING MESSAGE ===",
            message.raw_text,
            "",
            "=== SESSION CONTEXT ===",
            f"HEAD: {self._git_head()}",
            f"VERSION: {self._read_version()}",
            f"OPEN BUGS: {self._count_open_bugs()}",
            "TASK QUEUE SUMMARY:",
            self._task_queue_excerpt(),
            "",
            "=== HANDOFF EXCERPT ===",
            self._handoff_excerpt(),
            "",
            "=== RECENT COMMITS ===",
            self._git_log(n=10),
            "",
            "=== INSTRUCTIONS ===",
            f"Produce a valid mailbox ack for the incoming message above.",
            f"Target inbox: {target}",
        ])
```

### 5.5 Context cache

Session-level context (git log, VERSION, open bug count, HANDOFF excerpt) is
cached for 60 seconds to avoid re-reading disk on every message. The cache is
invalidated on any new commit detected (HEAD changes).

---

## 6. API Client

### 6.1 Model

`claude-sonnet-4-20250514`. Not Opus — acks and routing do not need the most
capable model and cost 5× less.

### 6.2 Parameters

```python
API_PARAMS = {
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 1000,
    "temperature": 0,       # Deterministic — acks should not be creative
    "stop_sequences": [],
}
```

### 6.3 Authentication

API key stored in PAH config file `C:\CODEX PG\CODEX Agent Hub\config\cd_agent.local.json`
(gitignored, Darrin-only). Key name: `ANTHROPIC_API_KEY`. The agent reads this at
startup and fails loudly if absent.

**Not stored in environment variables** — the PAH process is long-running and
env-vars inherited from the shell at launch are unreliable. Explicit config file
read at startup.

### 6.4 Request shape

```python
def call(self, context: dict) -> str:
    """Returns response text or raises CDAgentAPIError."""
    payload = {
        "model": API_PARAMS["model"],
        "max_tokens": API_PARAMS["max_tokens"],
        "system": context["system"],
        "messages": [
            {"role": "user", "content": context["user"]}
        ],
    }
    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": self._api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    return data["content"][0]["text"]
```

### 6.5 Response validation

Before writing the API response to disk, the responder validates:
- Response starts with `---` (YAML frontmatter)
- Frontmatter contains `from: CLAUDE`
- Frontmatter contains `requires_darrin_decision: false`
- Frontmatter contains `approval_boundary: ack_only`
- Frontmatter does NOT contain `approval_boundary: commit_go_required`
- Body does not contain phrases like "commit-go", "go tracker", "go phase"
  followed by "implementation" (these would be unauthorized commit-gos)

If validation fails: do NOT write the file. Log the failure. Escalate to Darrin.

### 6.6 ESCALATE_TO_DARRIN response handling

If the API returns a response starting with `ESCALATE_TO_DARRIN:`, the agent:
1. Extracts the reason
2. Does NOT write any mailbox file
3. Sends Darrin a notification with the reason and the original message path
4. Marks the message as processed (so it is not re-attempted)
5. Logs to audit trail

---

## 7. Responder

### 7.1 Output file naming

```python
def _output_filename(self, in_reply_to_id: str, target: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    suffix = "CC" if target == "cc" else "CODEX"
    return f"{stamp}_CLAUDE_to_{suffix}_cd_agent_ack.md"
```

### 7.2 Target inbox routing

| `to` field in incoming message | Output inbox |
|---|---|
| `CC` or `claude_code` | `cc_mailbox\CC Inbox\` |
| `CODEX` or `codex` | `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\` |
| `CLAUDE` (self-addressed) | Log warning, escalate to Darrin |

### 7.3 Write via atomic_write_text

All writes use PAH's existing `pah_mailbox.atomic.atomic_write_text` to avoid
partial-write corruption. The file is written to a `.tmp` sibling first, then
renamed atomically.

### 7.4 Post-write actions

After successful write:
- Call `pah_core.read_state.set_message_read_state(message_path, READ_STATE)`
- Call `pah_mailbox.idempotency.record_processed_message_event(message_path, "cd_agent")`
- Append to audit log

---

## 8. Budget Control

### 8.1 Daily USD budget

Default: `$1.00/day`. Configurable in `cd_agent.local.json` as `daily_budget_usd`.
The budget resets at midnight UTC.

### 8.2 Per-call cost estimation

Before each API call, estimate cost from input token count:
- System prompt: ~400 tokens (fixed)
- User message: estimated from character count ÷ 4
- Output: capped at 1000 tokens

Sonnet pricing (as of 2026-05): input $3/MTok, output $15/MTok.
Estimated cost per call: ~$0.004–$0.010 depending on message size.

At default $1.00/day budget: ~100–250 autonomous acks per day. More than
sufficient for current session volumes (typically 5–20 ack-able messages per session).

### 8.3 Budget enforcement

```python
def check_ok(self, estimated_cost_usd: float) -> bool:
    """Returns True if budget allows this call."""
    spent = self._load_today_spent()
    return (spent + estimated_cost_usd) <= self._daily_budget
```

If budget exhausted: escalate ALL messages to Darrin (toast notification) until
midnight reset. Do not fail silently.

### 8.4 Budget persistence

`C:\CODEX PG\CODEX Agent Hub\CODEX state\cd_agent_budget.local.json`:
```json
{
  "date_utc": "2026-05-03",
  "spent_usd": 0.042,
  "call_count": 7
}
```

---

## 9. Audit Log

### 9.1 Purpose

Every classification decision and API call is logged permanently. This is the
audit trail for "what did the CD Agent do autonomously and why?"

### 9.2 Format

Append-only JSONL at:
`C:\CODEX PG\CODEX Agent Hub\CODEX logs\cd_agent_audit.jsonl`

Each record:
```json
{
  "ts": "2026-05-03T02:15:33Z",
  "message_path": "cc_mailbox/CLAUDE Inbox/20260503_111000_CC_to_CLAUDE_tracker_t1_step0.md",
  "message_id": "20260503_111000_CC_to_CLAUDE_tracker_t1_step0",
  "message_type": "step0",
  "classification": "ack_only",
  "classification_reason": "approval_boundary=ack_only, type=step0, all discrepancy recommendations labeled (recommended)",
  "dry_run": false,
  "api_called": true,
  "api_model": "claude-sonnet-4-20250514",
  "estimated_input_tokens": 1240,
  "estimated_output_tokens": 380,
  "estimated_cost_usd": 0.0095,
  "response_validated": true,
  "output_path": "C:/panda-gallery/workflows/cc_mailbox/CC Inbox/20260503_021533_CLAUDE_to_CC_cd_agent_ack.md",
  "error": null
}
```

### 9.3 Darrin-visible summary

PAH dashboard gets a new "CD Agent" panel showing:
- Agent status (enabled/disabled/dry-run)
- Today's call count and spend
- Last 10 audit entries (message_id → classification → outcome)
- Budget remaining

---

## 10. Configuration Schema

### 10.1 File location

`C:\CODEX PG\CODEX Agent Hub\config\cd_agent.local.json`
(gitignored; Darrin creates from template)

### 10.2 Schema

```json
{
  "enabled": false,
  "dry_run": true,
  "api_key": "sk-ant-...",
  "model": "claude-sonnet-4-20250514",
  "daily_budget_usd": 1.00,
  "sweep_interval_seconds": 15,
  "notify_on_darrin_required": true,
  "notify_on_ack_sent": false,
  "notify_on_budget_exhausted": true,
  "notify_on_api_error": true,
  "notification_email": "",
  "safe_types_override": [],
  "escalate_types_override": [],
  "context_cache_ttl_seconds": 60,
  "api_timeout_seconds": 30,
  "max_retries": 2,
  "retry_backoff_seconds": 5,
  "response_validation_strict": true,
  "watched_inboxes": [
    "C:/panda-gallery/workflows/cc_mailbox/CLAUDE Inbox",
    "C:/CODEX PG/CODEX Claude Codex Mailbox/CLAUDE Inbox"
  ]
}
```

### 10.3 Default: dry_run = true

The agent ships with `dry_run: true` by default. In dry-run mode:
- All classification runs normally
- API is called and response is generated
- Response is logged to audit trail
- Response is NOT written to any inbox
- Darrin can inspect `cd_agent_audit.jsonl` to verify behavior before enabling

Darrin explicitly sets `dry_run: false` after reviewing dry-run logs.

### 10.4 Config template

A committed (non-gitignored) template at:
`C:\CODEX PG\CODEX Agent Hub\config\cd_agent.config.template.json`
contains all keys with placeholder values and inline comments. Darrin copies to
`.local.json` and fills in the API key.

---

## 11. Notification Integration

The CD Agent reuses PAH's existing `pah_notifications` system.

### 11.1 Notification events

| Event | Default | Channel |
|---|---|---|
| Darrin-required message (design decision) | ON | Toast + email if configured |
| Darrin-required message (commit-go) | ON | Toast + email |
| Darrin-required (budget exhausted) | ON | Toast |
| Ack sent autonomously | OFF | Toast only (configurable) |
| API error / escalation | ON | Toast + email |

### 11.2 Toast content for Darrin-required

```
[PAH CD Agent] Action required
Message: {message_subject}
Reason: {darrin_required_reason}
From: {message_from}
File: {short_path}
```

### 11.3 Email for Darrin-required

Uses PAH's existing SMTP config. Subject: `[PG] CD Agent — Darrin required: {subject}`.
Body includes full message frontmatter + classification reason + audit link.

---

## 12. PAH Dashboard Integration

### 12.1 New "CD Agent" tab in PAH UI

The existing PAH HTML UI (`CODEX_agent_hub_ui.html`) gets a new "CD Agent" tab
with:

- **Status row**: enabled badge (green) / disabled badge (gray) / dry-run badge
  (yellow) + sweep interval + last sweep timestamp
- **Budget row**: $X.XX spent today / $Y.YY remaining / N calls today / resets at
  {next_midnight_UTC}
- **Recent activity table**: last 20 audit entries showing timestamp, message_id,
  classification, outcome (ACK_SENT / DARRIN_NOTIFIED / DRY_RUN / ERROR)
- **Controls**: Enable / Disable / Enable Dry-Run buttons (write to config file via
  PAH HTTP API, require WRITE_TOKEN auth)

### 12.2 New PAH HTTP endpoints

| Method | Path | Auth | Action |
|---|---|---|---|
| GET | `/api/cd_agent/status` | None | Return agent status + budget + last N events |
| POST | `/api/cd_agent/enable` | WRITE_TOKEN | Set enabled=true, dry_run=false |
| POST | `/api/cd_agent/disable` | WRITE_TOKEN | Set enabled=false |
| POST | `/api/cd_agent/enable_dry_run` | WRITE_TOKEN | Set enabled=true, dry_run=true |
| POST | `/api/cd_agent/process_now` | WRITE_TOKEN | Force an immediate sweep (dev/test) |
| GET | `/api/cd_agent/audit` | None | Return last N audit log entries as JSON |

---

## 13. Safety Model

### 13.1 What the CD Agent can never do

These constraints are enforced in code, not just policy:

1. **No commit-go.** The response validator rejects any response containing
   `approval_boundary: commit_go_required` or commit-go phraseology.
2. **No repo writes.** The agent has no code path that touches `C:\panda-gallery\`
   directly. It only writes to `cc_mailbox\CC Inbox\` and the Codex inbox —
   the same mailbox files Darrin writes manually.
3. **No new scope authorization.** Any message proposing new tasks is escalated.
4. **No design decisions.** Messages requiring UX, clinical, or product judgment
   are always escalated.
5. **No budget override.** Budget exhaustion stops ALL autonomous responses until
   the next UTC day.
6. **No processing of malformed messages.** Frontmatter validation failures escalate
   to Darrin rather than proceeding.

### 13.2 Darrin override: kill switch

PAH dashboard "Disable" button sets `enabled: false` in config and signals the
agent thread to stop processing immediately (within one sweep cycle, max 15s).

A PowerShell one-liner can also kill the agent without opening the dashboard:
```powershell
$cfg = "C:\CODEX PG\CODEX Agent Hub\config\cd_agent.local.json"
(Get-Content $cfg | ConvertFrom-Json) | ForEach-Object { $_.enabled = $false; $_ } | ConvertTo-Json | Set-Content $cfg
```

### 13.3 Escalation always wins

When in doubt, the classifier escalates. The cost of an unnecessary Darrin
notification is one toast. The cost of an incorrect autonomous response is a
corrupted session state. The asymmetry is asymmetric in favor of escalation.

The agent never silently drops a message. Every message is either:
- Auto-responded (ack sent, audit logged)
- Escalated to Darrin (notification sent, audit logged)
- Skipped as not-actionable (idempotency check, audit logged)

---

## 14. Idempotency

PAH's existing `pah_mailbox.idempotency` module is reused:
- `processed_message_event_status(path, "cd_agent")` → has this been handled?
- `record_processed_message_event(path, "cd_agent")` → mark as handled

The event record is persisted to:
`C:\CODEX PG\CODEX Agent Hub\CODEX state\processed_messages\`

Even if the CD Agent crashes mid-response, the idempotency check prevents double-
processing on restart. The audit log (append-only JSONL) provides the full history
independent of the idempotency state.

---

## 15. Error Handling

| Error | Behavior |
|---|---|
| API timeout (>30s) | Retry up to 2× with 5s backoff; then escalate to Darrin |
| API rate limit (429) | Wait `Retry-After` header seconds; then retry once; then escalate |
| API error (4xx/5xx non-429) | Escalate to Darrin immediately; log full error |
| Response validation failure | Do NOT write file; escalate to Darrin |
| Budget exhausted | Escalate all messages to Darrin; send budget notification |
| Config file missing | Agent does not start; PAH logs warning at startup |
| API key invalid (401) | Agent disables itself; sends urgent Darrin notification |
| Inbox path missing | Agent logs error; continues sweeping other configured inboxes |
| File write failure (atomic) | Retry once; if still fails, escalate to Darrin |

---

## 16. Rollout Plan

### Phase 0: Dry-run validation (recommended first)

1. Darrin creates `cd_agent.local.json` with `enabled: true, dry_run: true, api_key: "sk-ant-..."`
2. PAH starts agent in dry-run mode
3. Agent classifies and generates responses but writes nothing
4. Darrin reviews `cd_agent_audit.jsonl` after one session
5. Verify: correct classifications, no false ack_only on darrin_required messages,
   no commit-go phraseology in generated responses

**Go/no-go gate:** Darrin reads 10 dry-run audit entries and confirms all
classifications are correct. Any wrong classification → fix classifier before
enabling live.

### Phase 1: Live with notification (limited scope)

1. Set `dry_run: false`
2. Set `notify_on_ack_sent: true` (Darrin sees every autonomous ack as a toast)
3. Run for 2-3 sessions
4. Verify toasts match what Darrin would have typed manually

**Go/no-go gate:** Darrin compares 10 live acks against what he would have written.
If responses are correct, proceed to Phase 2.

### Phase 2: Silent operation

1. Set `notify_on_ack_sent: false`
2. Agent runs silently for `ack_only` messages
3. Darrin only sees toasts for `darrin_required` escalations
4. Check `cd_agent_audit.jsonl` at session start (part of `pgs` ritual)

---

## 17. Future Extensions (v2+, not in scope now)

- **Commit-go handling**: After N consecutive clean dry-runs on a task class (e.g.
  T1 surface rename), auto-issue commit-go with Darrin's explicit per-task-class
  approval. This is a significant trust escalation and needs its own spec.
- **Dispatcher**: Auto-dispatch next queued CC task from TASK_QUEUE when current
  task ships, using a predefined dispatch template. Very high risk; needs full
  spec + Darrin approval protocol.
- **Multi-turn context**: Maintain a rolling conversation window across related
  mailbox threads so the agent can handle multi-step protocols autonomously.
- **Claude Code integration**: Use the existing `headless_contract.py` to run a
  headless CC instance for read-only repo queries (grep, git log) rather than
  reading context from disk.

---

## 18. Open Questions for Darrin Approval

Before implementation begins, the following require Darrin's explicit decision:

**Q1 — Budget:** Is $1.00/day the right cap? At ~10 ack messages per session and
~$0.008/ack, one active session costs ~$0.08. $1.00 gives 12 full sessions of
budget per day, which is generous.

**Q2 — Step 0 auto-approval of defaults:** The spec proposes auto-acking Step 0
reports when all discrepancy recommendations are labeled `(recommended)`. Is that
acceptable, or should ALL Step 0 reports require Darrin review regardless?

**Q3 — Commit-go exclusion:** The spec hard-excludes commit-gos from autonomous
handling. Do you want this to stay absolute in v1, or allow commit-go on a
specific whitelisted task class (e.g. docs-only commits)?

**Q4 — Dry-run duration:** How long should the dry-run validation phase run before
Darrin is comfortable enabling live mode? One session? Three sessions?

**Q5 — Codex inbox:** The spec watches both CC CLAUDE Inbox and Codex CLAUDE Inbox.
Codex messages are typically protocol consults and completion reports. Are you
comfortable with autonomous acks going into the Codex outbox, or should Codex
always escalate to Darrin in v1?

---

## 19. File Deliverables

When this spec is approved, implementation produces:

```
C:\CODEX PG\CODEX Agent Hub\
  pah_cd_agent\
    __init__.py
    agent.py
    classifier.py
    context.py
    api_client.py
    responder.py
    budget.py
    audit.py
    config.py
    dry_run.py
    tests\
      test_classifier.py
      test_context.py
      test_responder.py
      test_budget.py
      test_api_client.py    (mock Anthropic API)
  config\
    cd_agent.config.template.json
  CODEX_agent_hub_ui.html   (amended — new CD Agent tab)
  CODEX_agent_hub.py        (amended — new HTTP endpoints + watcher registration)
```

Test coverage target: 90%+ on classifier, responder, budget, audit. API client
tested against mock only (no live API calls in test suite).

---

## Versioning

v1.0 (2026-05-03) — Initial spec. Authored by CD after PAH architecture review.
v1.1 (2026-05-03) — Q1-Q5 decisions locked by Darrin. Status: APPROVED. Ready for Codex dispatch.
