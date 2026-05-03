# PAH Enhancement Specification v1.3

**Status:** PROPOSED — awaiting Darrin review before dispatch
**Date:** 2026-05-03
**Author:** Claude Desktop
**Location:** `C:\CODEX PG\CODEX Canonical Specs\PAH_ENHANCEMENT_SPEC_v1.md`
**Companion spec:** `PAH_CD_AGENT_SPEC_v1.md` (APPROVED — CD Agent implementation)
**Prerequisite:** Tracker MVP ships tonight. Inspector dispatch tomorrow. This spec
dispatches to Codex after those are stable.

**v1.3 changes from v1.2:** 22 findings corrected (4 errors, 7 omissions,
5 inconsistencies, 6 ambiguities). See §Revision notes at bottom.

---

## Purpose

This spec consolidates all outstanding PAH enhancements into a single prioritized
roadmap. It is organized by phase so Codex has a clear implementation sequence.
Each phase is self-contained and ships independently.

Sources consumed:
- `CODEX_PAH_TODO.md` — all open TODO items (classified by phase below)
- `PAH_CD_AGENT_SPEC_v1.md` — CD Agent v1.1 (APPROVED, Q1-Q5 locked)
- `CODEX_agent_hub.py` — current PAH runtime (architecture review)
- `pah_security/approvals.py` — approval contract review
- `pah_adapters/headless_contract.py` — headless CC contract review
- Session 123 live review findings

---

## Phase Map

| Phase | Name | Owner | Size | Prerequisite |
|---|---|---|---|---|
| **P1** | CD Agent v1 | Codex | Large | Tracker MVP shipped |
| **P2** | Dashboard completeness | Codex | Medium | P1 shipped |
| **P3** | Mailroom protocol v3 | Codex | Medium | P1 shipped (concurrent with P2) |
| **P4** | Classifier hardening | Codex | Small | P3 shipped |
| **P5** | Archive + steward | Codex | Medium | P4 shipped |
| **P6** | CC progress watchdog | Codex | Medium | P5 shipped |
| **P7** | Ledger retention + hygiene | Codex | Small | P6 shipped |

**Prerequisite clarification:** P2 and P3 both require P1 *shipped*. They share
the same gate and can be dispatched concurrently — there is no code overlap
between dashboard UI work (P2) and mailroom protocol enforcement (P3).

**Cadence note:** The external PAH watchdog script (P5) checks liveness every
5 minutes via a lock-guarded PowerShell invocation. The internal PAH steward
(M4 pings, discrepancy checks, retention pruning) runs every 30 minutes. These
are separate processes with different cadences. The watchdog checks port liveness
only; the steward handles protocol enforcement and periodic maintenance.

Each phase has: goal, acceptance criteria, and explicit links to
`CODEX_PAH_TODO.md` items it closes.

---

## Phase 1 — CD Agent v1

**Owner:** Codex
**Goal:** Implement `pah_cd_agent\` per `PAH_CD_AGENT_SPEC_v1.md` (APPROVED).
**Working directory for all P1 commands:** `C:\CODEX PG\CODEX Agent Hub\`
**Size:** Large (~600 LOC source, ~400 LOC tests)
**Prerequisite:** Tracker MVP shipped tonight

### Companion spec amendments required

Before implementing P1, Codex must apply two amendments to `PAH_CD_AGENT_SPEC_v1.md`
as a docs commit. Implementation may not begin until both amendments are committed.

**Amendment A — §2.2 Out of scope correction:**
Replace the first §2.2 bullet with:

> "Responding to feature/fix commit-go messages (`approval_boundary:
> commit_go_required` where suggested commit message uses `git vcommit` or a
> non-docs/chore prefix) autonomously. Docs-only commit-gos (`git commit -m "docs:"`
> or `chore:` prefix, no `vcommit` anywhere in the body) are in scope per Q3."

**Amendment B — §3.3 Flow diagram update:**
The §3.3 flow diagram shows two branches from `classifier.classify()`: `ack_only`
and `darrin_required`. Two additional branches must be added:
- `ack_only_docs_commit` → routes to `budget.check_ok()` → `api_client.call()` →
  `responder.write()` (same execution path as `ack_only`)
- `not_actionable` → routes to `mark_read(), skip`

The amended diagram must show all four MessageClass values explicitly.

### What gets built

Full implementation as specified in `PAH_CD_AGENT_SPEC_v1.md` (as amended):

- `pah_cd_agent/agent.py` — main watcher loop, sweep consumer
- `pah_cd_agent/classifier.py` — MessageClass engine
- `pah_cd_agent/context.py` — context assembler
- `pah_cd_agent/api_client.py` — Anthropic API wrapper (claude-sonnet-4-20250514)
- `pah_cd_agent/responder.py` — response validator + atomic mailbox writer
- `pah_cd_agent/budget.py` — daily USD budget tracker ($1.00/day default)
- `pah_cd_agent/audit.py` — append-only JSONL audit log
- `pah_cd_agent/config.py` — config schema + loader (`cd_agent.local.json`)
- `pah_cd_agent/dry_run.py` — dry-run utilities
- `config/cd_agent.config.template.json` — committed template (no API key)
- `CODEX_agent_hub.py` — amended: register CD Agent watcher consumer + new HTTP endpoints
- `CODEX_agent_hub_ui.html` — amended: new "CD Agent" tab

### Darrin decisions locked (from PAH_CD_AGENT_SPEC_v1.md §18)

| Q | Decision |
|---|----------|
| Q1 Budget | $1.00/day |
| Q2 Step 0 | Auto-ack when all defaults clear |
| Q3 Commit-go | Auto-ack docs-only; hard-exclude feature/fix |
| Q4 Dry-run | 1 session before live |
| Q5 Codex | Auto-ack Codex ack_only messages |

### Q3 classifier refinement

```python
class MessageClass(str, Enum):
    ACK_ONLY             = "ack_only"             # SAFE_TYPES — auto-respond
    ACK_ONLY_DOCS_COMMIT = "ack_only_docs_commit"  # Q3: docs-only commit-go only
    DARRIN_REQUIRED      = "darrin_required"       # Must interrupt Darrin
    NOT_ACTIONABLE       = "not_actionable"        # Already processed, or malformed
```

**Detection rule for `ACK_ONLY_DOCS_COMMIT` (all three conditions must be true):**
1. `approval_boundary: commit_go_required` in frontmatter
2. `type: commit_go` in frontmatter
3. Suggested commit message in body uses `git commit -m "docs:` or `"chore:` prefix
   AND body does NOT contain `git vcommit` anywhere

Any commit-go not matching all three → `DARRIN_REQUIRED`.

**Edge cases:**
- `approval_boundary: commit_go_required` but `type` is not `commit_go` → `DARRIN_REQUIRED`
- Body contains `git vcommit` anywhere → `DARRIN_REQUIRED` even with `docs:` or `chore:` prefix

### Response validator: forbidden commit-go strings

The response validator must reject any API-generated response containing any of
the following strings (case-insensitive):

```
"commit-go"
"go tracker"
"go phase"
"go implementation"
"go inspector"
"approval_boundary: commit_go_required"
"git vcommit"
"git commit -m" (when not inside a quoted example or code block)
```

If any forbidden string is detected: do NOT write the response file. Log the
detection to the audit log. Classify as ESCALATE_TO_DARRIN with reason
"Response contained forbidden commit-go string: <matched string>."

### SAFE_TYPES (10 total)

```python
SAFE_TYPES = {
    "ack", "shipped", "impl_start", "step0", "rtc",
    "protocol_consult", "ba_fix_dispatch", "directive_request",
    "hold_status_request", "completion_report",
}
```

SAFE_TYPES count is **10**. ACs reference "all 10 SAFE_TYPES."

### Rollout sequence

All commands run from `C:\CODEX PG\CODEX Agent Hub\` unless otherwise noted.

1. Codex applies companion spec amendments (Amendment A + B) as docs commit
2. Implement full module in dry-run mode (`dry_run: true` in default config)
3. Run test suite: `pytest pah_cd_agent/tests/ -q` → 90%+ coverage
   (run from `C:\CODEX PG\CODEX Agent Hub\`)
4. Run PAH smoke: `CODEX_run_smoke_tests.py` → all pass
5. Run PAH Inspector: `CODEX_pah_inspector.py` → 0 fail
   (warns acceptable — a new module will produce Inspector warns until P4 ships)
6. CD/Darrin reviews dry-run `cd_agent_audit.jsonl` for 1 complete Darrin session
7. Go/no-go gate (see below) → Darrin sets `dry_run: false` in `cd_agent.local.json`

**Definition of "1 complete Darrin session" for dry-run gate:**
The session must include at least one commit-go message arriving in CLAUDE Inbox
and being processed (classified) by the CD Agent. Step 0 and RTC for the same
task must also appear in the audit log. A session ending before any commit-go
arrives does not satisfy the gate.

**Go/no-go gate for dry-run → live:**
Darrin reads the last 5 ACK_ONLY audit entries in `cd_agent_audit.jsonl`.
Gate passes when ALL of:
- ≥5 classification entries present
- Zero API crashes (ESCALATE_TO_DARRIN entries caused by genuinely ambiguous
  messages are expected and do not fail the gate; crashes do)
- Zero budget tracking errors
- Zero response validation failures
- None of the last 5 ACK_ONLY entries are substantively wrong. Substantively
  wrong = incorrect step 0 defaults acked, wrong target inbox used, key
  acknowledgement omitted. Style differences do not fail the gate.

**Baseline for rollback:** Run `CODEX_run_smoke_tests.py` immediately before
beginning P1 implementation. Record the baseline pass count. A regression is
any test that passed in the baseline that now fails.

### Acceptance criteria

- [ ] AC-P1-1: `pah_cd_agent/` module importable without error from `C:\CODEX PG\CODEX Agent Hub\`
- [ ] AC-P1-2: Classifier correctly routes all **10** SAFE_TYPES to ACK_ONLY
- [ ] AC-P1-3: Classifier correctly routes all ESCALATE_TYPES to DARRIN_REQUIRED
- [ ] AC-P1-4: `requires_darrin_decision: true` always escalates regardless of type
- [ ] AC-P1-5: `priority: urgent` always escalates regardless of type
- [ ] AC-P1-6: Step 0 with all `(recommended)` labels → ACK_ONLY
- [ ] AC-P1-7: Step 0 with any "requires Darrin" body flag → DARRIN_REQUIRED
- [ ] AC-P1-8: Docs-only commit-go (all 3 conditions met, no vcommit in body) → ACK_ONLY_DOCS_COMMIT
- [ ] AC-P1-9: Feature/fix commit-go → DARRIN_REQUIRED
- [ ] AC-P1-10: Commit-go with `vcommit` anywhere in body → DARRIN_REQUIRED (even with `docs:` prefix)
- [ ] AC-P1-11: Response validator rejects all 8 forbidden commit-go strings (case-insensitive)
- [ ] AC-P1-12: Response validator rejects any response with `approval_boundary: commit_go_required`
- [ ] AC-P1-13: Budget exhaustion stops all autonomous responses and sends Darrin toast
- [ ] AC-P1-14: Idempotency: reprocessing same message_id is a no-op
- [ ] AC-P1-15: `dry_run: true` → no files written to any inbox
- [ ] AC-P1-16: Audit log entry written for every message processed (ACK, ESCALATE, SKIP)
- [ ] AC-P1-17: PAH dashboard "CD Agent" tab shows status, budget, last 20 audit entries
- [ ] AC-P1-18: `/api/cd_agent/status` returns JSON with enabled, dry_run, budget, last_n_events
- [ ] AC-P1-19: `/api/cd_agent/enable` and `/api/cd_agent/disable` require WRITE_TOKEN
- [ ] AC-P1-20: Kill switch disables agent within one sweep cycle (≤15s)
- [ ] AC-P1-21: `config/cd_agent.config.template.json` committed with all keys + placeholder comments
- [ ] AC-P1-22: Amendment A committed; §2.2 text correctly carves out docs-only per Q3 wording above
- [ ] AC-P1-23: Amendment B committed; §3.3 flow diagram shows all four MessageClass branches

**Rollback rule:** If P1 causes regressions against the pre-P1 baseline run of
`CODEX_run_smoke_tests.py`, revert the P1 commit and file a bug before re-dispatching.

### TODOs closed by P1

None from the open `CODEX_PAH_TODO.md` list — P1 is additive net-new surface.
The CD Agent tab is new, not a pre-existing TODO item.

---

## Phase 2 — Dashboard Completeness

**Owner:** Codex
**Goal:** Close the remaining open UI/UX TODO items in `CODEX_PAH_TODO.md`.
**Working directory:** `C:\CODEX PG\CODEX Agent Hub\`
**Size:** Medium (~200 LOC)
**Prerequisite:** P1 shipped

**Concurrency note:** P2 and P3 share the same gate (P1 shipped) and have no
code overlap. They may be dispatched and run simultaneously.

### Items from TODO

**Visual status for communication backlog:**
Add a "Communication Queue" widget showing counts for 4 states. Color thresholds
apply **per-state independently** — each count has its own color:
- green = 0, amber = 1–3, red = 4+

State definitions:
- **open-on-agent**: thread where latest message is unread and owned by CC or Codex
- **owner-unknown**: thread where PAH classifier cannot determine ownership
- **stale-unread**: any unread message where `(now − file_mtime) > STALE_UNREAD_SECONDS`
  (default 60s, configurable in PAH config). Uses the existing `STALE_UNREAD_SECONDS`
  constant from `CODEX_agent_hub.py`.
- **Darrin-waiting**: thread where the latest unread message has
  `requires_darrin_decision: true` OR `approval_boundary: commit_go_required`
  (either condition is sufficient)

Each count is clickable. Clicking opens the **existing message list panel** with
a pre-applied filter for that state. No new panel or overlay is created.

**One-click copy discrepancy summary:**
- "Copy status" button in the discrepancy panel
- Output: compact Markdown table of latest discrepancies, agent, thread, recommended action
- Implementation: `navigator.clipboard.writeText()` (browser API — PAH UI is
  HTML/JS; do NOT use `QApplication.clipboard()` which is a Qt API unavailable
  in a browser context)

**Collapsible advanced diagnostics:**
- Default collapsed: raw Inspector JSON, raw ledger JSONL, raw performance logs
- Each panel gets a "▶ Advanced" toggle
- Collapsed state persists in `localStorage` (one key per panel, e.g.
  `pah_adv_inspector`, `pah_adv_ledger`, `pah_adv_perf`)

**Visual regression screenshots:**
- After every Codex PAH pass: capture dashboard at 1440px wide, Inspector panel,
  CD Agent tab, alert/notice states
- Store at `C:\CODEX PG\CODEX Agent Hub\CODEX assets\screenshots\`
- Filename: `pah_<surface>_<YYYYMMDD_HHMMSS>.png` (timestamp mandatory)
- Codex includes file paths in RTC body under `## Screenshots`. CD verifies
  paths exist; Darrin reviews content live.

**Ledger dashboard drilldown:**
- Filter controls on interaction ledger panel: message_id, thread_id, agent,
  event_type, time range
- New `/api/ledger` endpoint; filter params: `agent`, `event_type`, `message_id`,
  `thread_id`, `since_hours` (integer; 0 = all). Reads from
  `CODEX_pah_interaction_ledger.jsonl`.

### Acceptance criteria

- [ ] AC-P2-1: Communication Queue shows 4 counts with correct per-state color thresholds
- [ ] AC-P2-2: stale-unread count uses `STALE_UNREAD_SECONDS` threshold
- [ ] AC-P2-3: Clicking any count opens the existing message list panel filtered for that state
- [ ] AC-P2-4: Darrin-waiting count includes `requires_darrin_decision: true` OR `approval_boundary: commit_go_required`
- [ ] AC-P2-5: "Copy status" uses `navigator.clipboard.writeText()`; produces valid Markdown table
- [ ] AC-P2-6: Advanced diagnostics collapsed by default; `localStorage` key per panel persists across refresh
- [ ] AC-P2-7: `/api/ledger` accepts all 5 filter params; returns filtered JSONL entries as JSON array
- [ ] AC-P2-8: Screenshots captured for all named surfaces; paths in RTC body under `## Screenshots`

**Baseline + rollback rule:** Capture `CODEX_run_smoke_tests.py` baseline before
P2 begins. If any previously-passing test fails post-P2, revert and file a bug.

### TODOs closed by P2

- [ ] `Add visual status for unresolved communication backlog`
- [ ] `Add one-click "copy discrepancy summary"`
- [ ] `Add collapsible advanced diagnostics`
- [ ] `Add visual regression screenshots for PAH alert/notice states`
- [ ] `Add a dashboard ledger viewer with filters`

---

## Phase 3 — Mailroom Protocol v3

**Owner:** Codex
**Goal:** Formalize and enforce the mailbox protocol so agents cannot silently
skip messages or make unchecked no-mail claims.
**Working directory:** `C:\CODEX PG\CODEX Agent Hub\`
**Size:** Medium (~150 LOC + protocol doc)
**Prerequisite:** P1 shipped (same gate as P2; concurrent)

### Protocol rules

**Rule M1 — Mailbox check summary (normative for CC, Codex, and CD Agent):**
Every agent mailbox check must POST a structured summary to PAH via
`/api/mailbox-check-summary` (WRITE_TOKEN required):

```json
{
  "agent": "CC",
  "ts": "2026-05-03T02:00:00Z",
  "inbox_scanned_count": 3,
  "message_ids_read": ["20260503_111000_...", "20260503_113000_..."],
  "message_ids_archived": ["20260503_105600_..."],
  "message_ids_skipped": [],
  "skip_reasons": {}
}
```

M1 is normative for **CC, Codex, and the CD Agent**. CD Agent submits
automatically on every sweep. Human-driven CD sessions (Darrin at claude.ai)
are **exempt**.

**M1 validation:** PAH validates `inbox_scanned_count` against its own file
count for that inbox at the moment the POST arrives. A static tolerance of ±1
is applied — mismatches of 1 are treated as race conditions and suppressed.
Mismatches of 2+ log `mailbox_discrepancy_detected`. No time-window re-check
is performed; the single POST snapshot is the evidence.

**Rule M2 — No-mail claim validation (already partially implemented):**
When an agent claims "no mail", PAH cross-checks CLAUDE Inbox unread count.
If unread > 0: log `mailbox_discrepancy_detected`, surface in discrepancy panel.
P3 extends this to also enforce M1 counts.

**Rule M3 — Read receipt for externally-managed reads:**
When CC reads a message via filesystem (not PAH UI), CC writes a read-receipt
file to `cc_mailbox/CC Sent/`.

Read-receipt file format:
```
---
schema_version: 1
message_id: YYYYMMDD_HHMMSS_CC_read_receipt
type: read_receipt
from: CC
to: CLAUDE
date: <ISO8601>
marks_read:
  - <message_id_1>
  - <message_id_2>
---
```

**`message_id` format:** Must use the standard mailbox timestamp:
`YYYYMMDD_HHMMSS_CC_read_receipt` (e.g., `20260503_020000_CC_read_receipt`).
This ensures PAH's `TIMESTAMPED_MESSAGE_RE = re.compile(r"^20\d{6}.*\.md$")`
matches the file and does not skip it.

PAH sweep discovery: PAH scans `CC Sent/` for files matching `type: read_receipt`
using the existing `processed_messages` idempotency log
(`record_processed_message_event(path, "m3_read_receipt_apply")`) to skip
already-applied files. For each unprocessed file, PAH checks each `marks_read`
ID against `read_state` before applying (idempotent write). After applying,
the file is recorded as processed.

CD does NOT use M3 — CD Agent calls `pah_core.read_state.set_message_read_state()`
directly via Python import on each sweep.

**Rule M4 — Route-test ping (steward-triggered):**
The PAH steward sends a synthetic `type: route_test_ping` message to CC inbox
on each steward run (every 30 minutes).

**Reply window:** CC must reply before the next steward run (30 min).
PAH checks for a reply at the start of the following steward run.
Missing reply → `mailbox_discrepancy_detected`.

**M4 de-duplication:** If CC is offline and sends no reply across multiple
consecutive steward runs, only the first miss and every 5th subsequent miss
for the same ping `thread_id` generate a new discrepancy event. Intermediate
misses are counted but do not create duplicate alerts.

**Cleanup:** After PAH verifies the reply (pass or fail), both the ping file
and reply file are archived immediately, preventing accumulation across runs.

### Protocol document

Codex authors `C:\CODEX PG\CODEX Canonical Specs\PAH_MAILROOM_PROTOCOL_v3.md`
with: rule text, example JSON/YAML, agent applicability table
(CC ✓, Codex ✓, CD Agent ✓, human-CD ✗ M1-exempt), and enforcement behavior.

### Acceptance criteria

- [ ] AC-P3-1: `/api/mailbox-check-summary` accepts M1 JSON; requires WRITE_TOKEN
- [ ] AC-P3-2: M1 mismatch ≥2 → `mailbox_discrepancy_detected` + dashboard surfaced
- [ ] AC-P3-3: M1 mismatch of exactly ±1 → suppressed (not logged)
- [ ] AC-P3-4: M2 no-mail validation extended to enforce M1 counts simultaneously
- [ ] AC-P3-5: PAH scans `CC Sent/` for unprocessed `type: read_receipt` files via idempotency log
- [ ] AC-P3-6: M3 marks_read IDs checked against read_state before applying
- [ ] AC-P3-7: M3 read-receipt `message_id` uses `YYYYMMDD_HHMMSS_CC_read_receipt` format
- [ ] AC-P3-8: M4 route-test ping written to CC inbox on every steward run
- [ ] AC-P3-9: M4 reply check at start of *next* steward run (not same run)
- [ ] AC-P3-10: M4 miss de-duplication: first miss + every 5th subsequent miss generate events; intermediates counted only
- [ ] AC-P3-11: M4 ping + reply files archived immediately after verification
- [ ] AC-P3-12: `PAH_MAILROOM_PROTOCOL_v3.md` authored with agent applicability table and enforcement behavior
- [ ] AC-P3-13: human-CD M1-exemption documented in protocol doc

**Rollback rule:** If M1 validation produces false discrepancies for legacy
pre-schema_version messages, add a classifier exemption and re-ship. Do not
disable M1 globally.

### TODOs closed by P3

- [ ] `Define PAH mailbox protocol v3 for CD/CC/Codex`
- [ ] `Require agent replies to include mailbox check summary`
- [ ] `Make the mailbox check summary rule explicitly normative for CC`
- [ ] `Add explicit read receipt message for each agent-managed inbox read`
- [ ] `Add route-test ping/reply protocol for CC` (human-CD is M1-exempt; Codex auto-submits M1)

---

## Phase 4 — Classifier Hardening

**Owner:** Codex
**Goal:** Close open classifier TODO items; make classifier self-documenting.
**Working directory:** `C:\CODEX PG\CODEX Agent Hub\`
**Size:** Small (~80 LOC)
**Prerequisite:** P3 shipped

### Items from TODO

**Owner-unknown audit:**
- Review all current owner-unknown items in the live mailbox
- For each: add a safe classifier rule for the known-valid legacy format, OR
  document in `classifier_exceptions.md` as uncategorizable
- **Codex may NOT edit any live inbox file.** All fixes are classifier rule
  additions only.
- RTC must confirm no file under `cc_mailbox\CLAUDE Inbox\`, `cc_mailbox\CC Inbox\`,
  or `C:\CODEX PG\CODEX Claude Codex Mailbox\` was modified during P4
- `classifier_exceptions.md` location:
  `C:\CODEX PG\CODEX Agent Hub\CODEX state\classifier_exceptions.md`

**"Why classified this way" explanation:**
- Add `classification_reason` string to every thread's action detail in dashboard
- Examples: `"Frontmatter: approval_boundary=ack_only, type=ack → ACK_ONLY"`,
  `"Body contains 'requires Darrin' keyword → DARRIN_REQUIRED"`

**Test completeness:**
- Tests for every completion/ack/report/status combination that should close
  before generic agent ownership transitions
- Tests for ready-for-review/report combinations that must remain open

### Acceptance criteria

- [ ] AC-P4-1: Zero owner-unknown items for messages with valid `schema_version`
- [ ] AC-P4-2: `classification_reason` shown in action detail for every thread
- [ ] AC-P4-3: All completion/ack/report combinations have test coverage
- [ ] AC-P4-4: All ready-for-review/report combinations have test coverage
- [ ] AC-P4-5: `classifier_exceptions.md` at canonical path; documents all unfixable items
- [ ] AC-P4-6: RTC confirms no live inbox file was modified during P4

**Rollback rule:** If classifier rule additions cause regressions in existing
thread classifications, revert the rule and document the conflict in
`classifier_exceptions.md`.

### TODOs closed by P4

- [ ] `Review current owner-unknown items`
- [ ] `Add tests for every completion/ack/report/status combination`
- [ ] `Add tests for ready-for-review/report combinations`
- [ ] `Add a "why classified this way" explanation field in action detail`

---

## Phase 5 — Archive + Steward

**Owner:** Codex
**Goal:** Close remaining archive reliability and steward escalation gaps.
**Working directory:** `C:\CODEX PG\CODEX Agent Hub\`
**Size:** Medium (~180 LOC)
**Prerequisite:** P4 shipped

### Items from TODO

**Archive restore tooling:**
- POST `/api/archive/restore` body: `{message_id, target_inbox}`
- `target_inbox` is always required. Codex first audits whether the current
  archive sidecar records `source_inbox`:
  - If yes: dashboard Restore button pre-fills `target_inbox` from it (Darrin
    can override before confirming)
  - If no: Codex adds `source_inbox` to the archive sidecar schema; populated
    on all new archive operations going forward. Existing archived messages
    without `source_inbox` require Darrin to enter the inbox manually.
- Requires WRITE_TOKEN
- Dashboard Restore button opens a modal; Darrin confirms before POST fires
- Feature flag: `archive_restore_enabled: true` in
  `C:\CODEX PG\CODEX Agent Hub\config\pah.local.json`. Set to `false` to
  disable the endpoint for rollback.

**`discrepancy_state.json` (new in P5):**
P5 introduces `C:\CODEX PG\CODEX Agent Hub\CODEX state\discrepancy_state.json`
to track active discrepancies for the repeated-escalation feature and for
P7's prune guard. Schema:

```json
{
  "open_discrepancies": [
    {
      "key": "(CC, mailbox_count_mismatch, thread_20260503_111000)",
      "agent": "CC",
      "discrepancy_type": "mailbox_count_mismatch",
      "thread_id": "20260503_111000",
      "inbox_path": null,
      "first_seen": "2026-05-03T02:00:00Z",
      "last_seen": "2026-05-03T02:30:00Z",
      "consecutive_count": 2,
      "last_clean_run": null
    }
  ]
}
```

Key format: `"(agent, discrepancy_type, thread_id_or_inbox_path)"`.
`thread_id` takes priority; `inbox_path` used when `thread_id` is absent.

**Inbox cleanup dry-run:**
- GET `/api/inbox/cleanup-dryrun`
- Returns: `{would_archive: [{message_id, inbox_path, last_modified, age_days}], would_delete: [], total_count: N}`
- No side effects — read-only
- Dashboard "Preview cleanup" button shows this report in a modal before any
  cleanup action proceeds

**Automatic escalation for repeated discrepancies:**
- Uses `discrepancy_state.json` to track consecutive occurrence counts
- If `consecutive_count >= 2` with no intervening clean run for that key:
  escalate via Darrin toast + email (if configured)
- **Consecutive definition:** A single steward run that does NOT detect the
  discrepancy resets `consecutive_count` to 0 and records `last_clean_run`.
  Run sequence Fail/Clean/Fail = count resets at Clean; second Fail starts at 1.

**External startup watchdog:**
PAH cannot self-start. The watchdog is an external PowerShell script:

- `CODEX_pah_watchdog.ps1` in PAH hub root
- Scheduled via Windows Task Scheduler every 5 minutes
- **Concurrency guard:** Script writes `pah_watchdog.lock` at start; deletes
  at completion. If lock exists and is < 2 minutes old at script start: skip
  this run entirely (previous run still in progress). If lock is ≥ 2 minutes
  old: treat as stale, delete it, and proceed.
- Checks `GET /api/ready` on port 8765
- If `/api/ready` fails AND `CODEX_start_agent_hub.ps1` exists at expected path:
  attempt one restart via that script. If script is missing: log
  `WATCHDOG ERROR: start script missing at <path>`, send Darrin toast, skip restart.
- If restart attempt fails (exit code non-zero or `/api/ready` still fails after
  30s): log failure to `CODEX logs/pah_startup.log` with timestamp, send Darrin
  toast, stop. Do not retry until next scheduled run.
- If restart succeeds: log success with timestamp.
- PAH `CODEX_agent_hub.py` contains NO self-start logic.

`CODEX_WATCHDOG_SETUP.md` (committed to hub root) provides Task Scheduler
registration steps. Darrin registers the task manually.

**Route-test pings:** Covered by M4 (P3). P5 adds no separate route-check.

### Acceptance criteria

- [ ] AC-P5-1: POST `/api/archive/restore` accepts `{message_id, target_inbox}`; moves message correctly
- [ ] AC-P5-2a: RTC documents whether archive sidecar currently records `source_inbox`
- [ ] AC-P5-2b: If absent: `source_inbox` added to schema; populated on all new archive operations
- [ ] AC-P5-3: Restore modal pre-fills `target_inbox` from `source_inbox` when available
- [ ] AC-P5-4: Restore modal requires Darrin confirmation before POSTing
- [ ] AC-P5-5: `archive_restore_enabled` flag in `pah.local.json` disables endpoint when false
- [ ] AC-P5-6: `discrepancy_state.json` created with schema above; updated on each steward run
- [ ] AC-P5-7: GET `/api/inbox/cleanup-dryrun` returns `{would_archive, would_delete, total_count}` with no side effects
- [ ] AC-P5-8: Cleanup modal shows dry-run report before any action proceeds
- [ ] AC-P5-9: Discrepancy key uses thread_id when present; falls back to inbox_path
- [ ] AC-P5-10: `consecutive_count >= 2` with no clean run → Darrin toast + email
- [ ] AC-P5-11: Single clean steward run resets `consecutive_count` to 0 for that key
- [ ] AC-P5-12: `CODEX_pah_watchdog.ps1` writes/checks lock file before each run
- [ ] AC-P5-13: Stale lock (≥ 2 min) deleted and run proceeds; fresh lock (< 2 min) skips run
- [ ] AC-P5-14: Watchdog checks `/api/ready`; attempts one restart if down and start script exists
- [ ] AC-P5-15: Missing start script → log + toast, skip restart attempt
- [ ] AC-P5-16: Failed restart → log + toast; no further retry until next scheduled run
- [ ] AC-P5-17: `CODEX_WATCHDOG_SETUP.md` includes Task Scheduler registration steps
- [ ] AC-P5-18: `pah_startup.log` written with timestamp on each restart attempt (pass or fail)
- [ ] AC-P5-19: `CODEX_agent_hub.py` contains no self-start logic

**Rollback rule:** If `/api/archive/restore` moves a message to the wrong inbox:
set `archive_restore_enabled: false` in `pah.local.json` and file a bug before
re-enabling.

### TODOs closed by P5

- [ ] `Add archive restore tooling`
- [ ] `Add inbox cleanup dry-run report before manual cleanup actions`
- [ ] `Add automatic escalation for repeated discrepancies`
- [ ] `Add self-healing startup check` (closed via external watchdog)
- [ ] `Add startup failure diagnostics`

---

## Phase 6 — CC Progress Watchdog

**Owner:** Codex
**Goal:** Implement the CC active-dispatch progress watchdog (v0.2 monitoring
spec, already approved by CD in session 101).
**Working directory:** `C:\CODEX PG\CODEX Agent Hub\`
**Size:** Medium (~200 LOC)
**Prerequisite:** P5 shipped (P5 introduces `discrepancy_state.json` which P6 also reads)

### What gets built

**`_state/active_dispatch.json` sidecar** (written by CC, read by PAH):
All `target_paths` are **relative to `C:\panda-gallery\`** (PANDA_GALLERY_ROOT).
Both watchdog and Inspector resolve paths against PANDA_GALLERY_ROOT.

```json
{
  "status": "active",
  "task_id": "tracker_t3",
  "target_paths": ["audit_module/v1/"],
  "started_at": "2026-05-03T12:00:00Z",
  "last_write_at": "2026-05-03T12:15:00Z",
  "last_write_path": "audit_module/v1/screen_b.py",
  "scanned_files": 14,
  "recommended_action": null
}
```

Allowed `status` values: `active`, `compose`, `heavy_write`, `paused`,
`blocked`, `ready_for_human_loop`, `complete`, `abandoned`

**PAH stall thresholds (concrete — do not derive):**

| Status | Warn | Error |
|---|---|---|
| `active` | **30 min** | **45 min** |
| `compose` | **60 min** | **90 min** |
| `heavy_write` | **60 min** | **90 min** |
| `paused` | no alert | no alert |
| `blocked` | no alert | no alert |
| `ready_for_human_loop` | no alert | no alert |
| `complete` | no alert | no alert |
| `abandoned` | no alert | no alert |

All five no-alert statuses — `paused`, `blocked`, `ready_for_human_loop`,
`complete`, and `abandoned` — suppress stall alerts for the duration of that
status. This applies to all five equally; none are treated differently.

**Stale-complete sidecar rule:** A sidecar with `status: complete` or
`status: abandoned` older than **24 hours** (measured from `last_write_at`)
triggers Inspector WARN: "No active dispatch sidecar — possible missed update
(last status: complete, age: Xh)."

**Dashboard sidecar age display:**
- **"Sidecar age"** = time since `last_write_at` (compared against stall thresholds)
- **"Task running for"** = time since `started_at` (displayed separately, informational only)
- Yellow card (warn crossed) and red card (error crossed) → clickable action detail
- Action detail: evidence path, `last_write_at` mtime, threshold crossed,
  `recommended_action` from sidecar if present

**PAH Inspector upgrades:**
- Validate sidecar schema / required fields / allowed status values
- Test CC progress evidence: newest child mtime under target paths (PANDA_GALLERY_ROOT-anchored)
- Verify false-positive guards for all 5 no-alert statuses: `paused`, `blocked`,
  `ready_for_human_loop`, `complete`, `abandoned`
- Verify stale-complete sidecar rule fires at 24h
- Smoke tests use `tempfile.mkdtemp(prefix="pah_test_")` created at test setup,
  deleted at teardown. If teardown fails: log path to test output, do not raise.
  Zero reads/writes to real `C:\panda-gallery\` in tests.

### Acceptance criteria

- [ ] AC-P6-1: Sidecar schema validated; missing required fields → Inspector WARN
- [ ] AC-P6-2: `active` status: stall warn fires at 30 min no write
- [ ] AC-P6-3: `active` status: stall error fires at 45 min no write
- [ ] AC-P6-4: `compose`/`heavy_write`: warn at 60 min, error at 90 min (explicit — not derived)
- [ ] AC-P6-5: All 5 no-alert statuses (`paused`, `blocked`, `ready_for_human_loop`, `complete`, `abandoned`) → no stall alert
- [ ] AC-P6-6: `complete`/`abandoned` sidecar with `last_write_at` > 24h → Inspector WARN
- [ ] AC-P6-7: Yellow/red progress cards clickable → action detail with evidence path + mtime + threshold
- [ ] AC-P6-8: Dashboard shows "Sidecar age" (from `last_write_at`) and "Task running for" (from `started_at`) separately
- [ ] AC-P6-9: All target_paths resolved relative to PANDA_GALLERY_ROOT
- [ ] AC-P6-10: Smoke fixtures use `tempfile.mkdtemp(prefix="pah_test_")`; no real PG paths in tests
- [ ] AC-P6-11: Inspector validates sidecar freshness against status-specific thresholds
- [ ] AC-P6-12: Inspector verifies false-positive guards for all 5 no-alert statuses

**Rollback rule:** If P6 produces false stall alerts on the live CC dispatch,
add the status to the no-alert table and re-ship before disabling the watchdog.

### TODOs closed by P6

- [ ] `Implement CC active-dispatch progress watchdog from v0.2 monitoring spec`
- [ ] `Fold CD-approved v0.2 monitoring amendments into implementation`
- [ ] `Upgrade PAH Inspector to validate active_dispatch.json sidecar freshness`
- [ ] `Upgrade PAH Inspector to test CC progress evidence`
- [ ] `Upgrade PAH Inspector to verify false-positive guards`
- [ ] `Upgrade PAH Inspector to verify Agent Progress dashboard wiring`
- [ ] `Upgrade PAH Inspector to verify CC-stall escalation behavior`
- [ ] `Add smoke-test fixtures for CC progress monitoring`

---

## Phase 7 — Ledger Retention + Hygiene

**Owner:** Codex
**Goal:** Prevent unbounded ledger growth; establish durable release hygiene.
**Working directory:** `C:\CODEX PG\CODEX Agent Hub\`
**Size:** Small (~100 LOC)
**Prerequisite:** P6 shipped (P5 introduces `discrepancy_state.json` used by prune guard)

### Items from TODO

**Ledger retention:**
- Configurable retention window (default: 7 days) in PAH config
- Steward prunes `CODEX_pah_interaction_ledger.jsonl` and `cd_agent_audit.jsonl`
  on each steward run (same step, same window)
- **Retention age** calculated from the `ts` field of each JSONL entry (ISO8601
  UTC). Entries without a `ts` field are kept indefinitely and flagged in the
  steward health card as "missing ts — cannot prune."
- **Prune guard:** Before pruning any entry, check `discrepancy_state.json`
  (introduced in P5) for active discrepancies referencing that entry's
  `message_id` or `thread_id`. If referenced: skip that entry; log the skip
  count to the steward health card.
- Steward health card shows: pruned count per file, skipped count per file,
  "missing ts" count per file

**Release hygiene checklist:**
New file: `C:\CODEX PG\CODEX Agent Hub\CODEX_release_checklist.md`

Six checklist items:
1. `py_compile` passes on all PAH Python files
2. `CODEX_run_smoke_tests.py` — all pass (against pre-phase baseline)
3. Live `/api/health` — green
4. Periodic steward run — clean
5. GitHub backup confirmed (method defined at P7 dispatch — see below)
6. Screenshots captured per P2 protocol; paths recorded

**GitHub backup method (resolved at P7 dispatch):**
PAH does not currently have a GitHub repo. At P7 dispatch, Codex asks CD:
"Does a PAH GitHub repo exist?" If yes: backup = `git push` to that repo.
If no: backup = timestamped zip of `C:\CODEX PG\CODEX Agent Hub\` to a
location Darrin specifies. Method is recorded in the checklist file itself
after resolution.

**Checklist protocol:** Codex runs this checklist before every RTC. RTC body
must include `## Release checklist` with each item marked ✓ or ✗ + brief note.

**Durable PAH docs update after every pass:**
Standing protocol — not a one-time deliverable. After every PAH implementation
or incident-response pass, Codex updates:
- `CODEX_README.md`: live URL, start command, health checks, archive-read,
  watchdog setup, ledger location
- `CODEX_PAH_TODO.md`: mark completed; add newly surfaced follow-ups
- Relevant spec: any product/UX/protocol/acceptance rule changes found

RTC must include: "Docs updated: README ✓, TODO ✓, [spec if changed] ✓"

### Acceptance criteria

- [ ] AC-P7-1: Ledger entries older than 7 days pruned on steward run (calculated from `ts` field)
- [ ] AC-P7-2: Entries without `ts` field kept indefinitely; flagged in health card as "missing ts"
- [ ] AC-P7-3: `cd_agent_audit.jsonl` pruned same window, same steward step
- [ ] AC-P7-4: Entries referenced by `discrepancy_state.json` open discrepancies skipped; skip count logged
- [ ] AC-P7-5: Steward health card shows pruned/skipped/missing-ts counts per file
- [ ] AC-P7-6: `CODEX_release_checklist.md` committed with all 6 items
- [ ] AC-P7-7: P7 RTC includes `## Release checklist` with each item ✓/✗
- [ ] AC-P7-8: GitHub backup method resolved at dispatch; recorded in checklist file
- [ ] AC-P7-9: README updated; TODO updated; spec updated if applicable

**Rollback rule:** If retention pruning removes entries needed for active
discrepancy tracking (prune guard failure): set `retention_enabled: false`
in PAH config and file a bug before re-enabling.

### TODOs closed by P7

- [ ] `Add ledger retention/export controls`
- [ ] `Add a pre-commit or release checklist`
- [ ] `At the end of every PAH pass, update durable PAH docs`

---

## Dispatch sequence

1. **P1** — dispatch immediately after Tracker T5 ships.
2. **P2 + P3** — dispatch concurrently after P1 ships. No code overlap.
3. **P4** — dispatch after P3 ships.
4. **P5** — dispatch after P4 ships.
5. **P6** — dispatch after P5 ships (P5 introduces `discrepancy_state.json` P6 reads).
6. **P7** — dispatch after P6 ships. Closes all TODO items.

Estimated: 3–4 weeks of Codex implementation at current velocity.

---

## What this spec does NOT cover

- PAH runtime code before Darrin approves this spec (Final Design Spec §2 boundary)
- Any write to `C:\panda-gallery\` from PAH (prohibited)
- Vellum, Panda Collaborator, or any paused-module work
- Inspector (Pane/Testing) — separate CC dispatch
- Relay polish bugs #155-#162 — CC queue

---

## Revision notes

**v1.1 (24 findings), v1.2 (22 findings):** See git history.

**v1.3 corrections from v1.2 (22 findings):**

*Errors fixed:*
- E1: M1 race tolerance changed from "2-second time-window re-check" to static ±1 tolerance on the single POST snapshot — implementable in a single request cycle
- E2: Watchdog concurrency guard added — lock file (`pah_watchdog.lock`) written at start, deleted at completion; stale lock (≥2 min) deleted and run proceeds; fresh lock skips run
- E3: AC-P1-11 now references an explicit enumerated list of 8 forbidden commit-go strings in the spec body
- E4: `discrepancy_state.json` introduced and fully defined in P5 with schema; P7 prune guard now has a concrete file to reference

*Omissions fixed:*
- O1: AC-P3-3 revised to match the static ±1 tolerance (not time-window)
- O2: M4 de-duplication rule added — first miss + every 5th subsequent miss; intermediates counted only
- O3: `/api/inbox/cleanup-dryrun` response schema defined: `{would_archive, would_delete, total_count}`
- O4: Baseline run defined for all phases — "run `CODEX_run_smoke_tests.py` immediately before beginning; regression = previously-passing test now fails"
- O5: PAH Inspector narrative corrected to list all 5 no-alert statuses; body now matches ACs
- O6: Missing start script handling added — log + toast, skip restart
- O7: `stale-unread` definition added to P2 widget spec using existing `STALE_UNREAD_SECONDS` constant

*Inconsistencies fixed:*
- I1: All P1 commands now explicitly say "run from `C:\CODEX PG\CODEX Agent Hub\`"
- I2: P3 TODOs closed entry corrected to "for CC" (human-CD exempt; Codex submits M1 automatically)
- I3: AC-P5-8 now includes the full "no intervening clean run" condition
- I4: P1 TODOs closed section clarified — "None from open list; CD Agent tab is additive new surface"
- I5: P6 narrative corrected to list all 5 no-alert statuses equally; "permanently" qualifier removed

*Ambiguities fixed:*
- A1: Dry-run gate "1 complete session" now requires commit-go to appear in audit log, not just session boundary
- A2: Archive restore feature flag named explicitly: `archive_restore_enabled` in `pah.local.json`
- A3: Communication Queue drill-down destination defined: opens existing message list panel with filter
- A4: "Sidecar age" vs "Task running for" distinguished: age = from `last_write_at`; running for = from `started_at`
- A5: M3 read-receipt `message_id` format specified: `YYYYMMDD_HHMMSS_CC_read_receipt`
- A6: Ledger retention age calculated from `ts` field; missing-`ts` entries kept + flagged

---

## Versioning

v1.0 (2026-05-03) — Initial spec.
v1.1 (2026-05-03) — 24 findings corrected.
v1.2 (2026-05-03) — 22 findings corrected.
v1.3 (2026-05-03) — 22 findings corrected. discrepancy_state.json defined.
Watchdog lock guard added. M1 tolerance simplified. Forbidden string list
enumerated. All working directories explicit. Ready for Round 4 analysis.
