# PANDA Agent Hub Product and Technical Specification v0.1

Generated: 2026-04-26 18:50:00 -07:00
Status: Draft v0.1
Owner: Darrin
Primary implementer: Codex
Review partners: Claude Desktop, Claude Code, CC
Project label: PANDA Agent Hub (PAH)
Local implementation folder: `C:\CODEX PG\CODEX Agent Hub`
Spec folder: `C:\CODEX PG\CODEX PANDA Agent Hub Spec`

## 1. Executive Summary

PANDA Agent Hub is a local coordination cockpit for parallel AI-assisted development.

Its purpose is to streamline and automate multi-agent development with minimal Darrin input while preserving Darrin as the approval authority for risky actions.

PAH coordinates Codex, Claude Desktop, Claude Code, CC, and future API-backed agents through a local control plane:

- shared message queues
- structured task metadata
- active thread tracking
- Darrin decision queue
- validation/linting
- notification alerts
- approval gates
- audit logs
- optional future direct agent adapters

The current prototype is a local web app at `http://127.0.0.1:8765`. It reads/writes the existing mailbox under `C:\CODEX PG\CODEX Claude Codex Mailbox`, shows dashboard data, lets Codex send messages, tracks Darrin decisions, validates mailbox hygiene, and supports local notification providers.

The next version should become a reliable local-first orchestration layer before it attempts direct model API calls.

## 2. Product Purpose

### 2.1 Core purpose

PAH exists to reduce Darrin's coordination load when multiple agents are working in parallel.

The app should answer, at a glance:

- Who needs to do what next?
- Which tasks are blocked?
- Which decisions truly need Darrin?
- Which agent is waiting on another agent?
- Which deliverables exist and have been validated?
- Which tasks can safely proceed without Darrin?
- Which actions require explicit approval?

### 2.2 Product promise

PAH should let Darrin supervise a parallel development system without manually reading every mailbox file, reconciling every thread, or remembering which agent owns which task.

### 2.3 Success statement

PAH is successful when Darrin can step away, receive only necessary phone alerts, return to a dashboard, and understand:

- current project state
- open agent work
- recommended next decisions
- unsafe or blocked actions
- latest validated deliverables

within 60 seconds.

## 3. Operating Principles

1. Local-first before cloud.
   PAH starts as a local control plane using files and localhost. Direct APIs are later adapters, not the foundation.

2. Darrin remains the approval authority.
   Agent messages may request, recommend, or report. They do not authorize protected actions.

3. No silent dangerous actions.
   Writes to `C:\panda-gallery`, commits, pushes, installs, email sends, SMS sends, deletions, and external API calls must be gated by policy and explicit configuration.

4. Every automated action is logged.
   PAH must record what happened, who initiated it, what files were touched, and whether validation passed.

5. Schema before autonomy.
   PAH should standardize message metadata and lint it before relying on agents to self-route tasks.

6. Minimal Darrin input, not zero Darrin authority.
   PAH should reduce interruptions, but it should not hide decisions or make judgment calls that belong to Darrin.

7. No PHI, secrets, or credentials in mailbox messages.
   Credentials belong in ignored local config or a future secure credential store.

8. Existing project boundaries remain.
   All Codex-created PAH files stay under `C:\CODEX PG` and use CODEX-prefixed folders unless Darrin approves a rename strategy.

9. Agents decide technical details where they are better qualified.
   Darrin does not want to answer low-level implementation-detail questions where Codex, Claude Desktop, and Claude Code / CC can vote, converge, and recommend. PAH should reserve Darrin consultation for UX appearance/functionality, dental/product judgment, safety boundaries, credentials/cost, external communication, and protected actions.

## 4. Current Prototype Inventory

### 4.1 Current app files

- `C:\CODEX PG\CODEX Agent Hub\CODEX_agent_hub.py`
- `C:\CODEX PG\CODEX Agent Hub\CODEX_start_agent_hub.ps1`
- `C:\CODEX PG\CODEX Agent Hub\CODEX_README.md`
- `C:\CODEX PG\CODEX Agent Hub\CODEX config\CODEX_notification_config.template.json`

### 4.2 Current mailbox folders

- `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox`
- `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox`
- `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Sent`
- `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Sent`
- `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Archive`
- `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Claude Code Inbox`

### 4.3 Current implemented capabilities

- Local web dashboard on `127.0.0.1`
- Mailbox parsing
- Latest-message list
- Thread grouping
- Darrin decision queue
- Mailbox validator
- Compose path for Codex to Claude
- Compose path for Codex to Claude Code
- Git status panel
- Notification config template
- Log-only notification test
- Token-protected write endpoints
- Origin/Host check for write requests
- No default inbound Claude spoofing

### 4.4 Known prototype limitations

- No formal YAML frontmatter schema yet.
- No participant registry yet.
- Claude Code inbox folder name may need to change to `CODEX_CLAUDE_CODE Inbox` for consistency.
- No direct Claude Code headless invocation yet.
- No direct OpenAI or Anthropic API lanes yet.
- No app-level permission review UI yet.
- No packaged desktop shell yet.
- No persistent database; current state is derived from files.
- No full task lifecycle engine yet.

## 5. Research-Informed Decisions

### 5.1 Direct API lanes are not v1

OpenAI Responses API and Anthropic Messages API are viable future agent lanes, but PAH should first stabilize the local mailbox/schema/control plane.

Rationale:

- Local file queues already work across the current tools.
- Direct APIs add cost, credentials, privacy, and state-management complexity.
- The highest time savings are from dashboarding, routing, linting, notifications, and reducing Darrin context checks.

### 5.2 Claude Code is a participant, not just Claude

Claude Desktop and Claude Code must be separate participants.

Claude Desktop:

- reviews
- synthesizes
- dispatches
- coordinates

Claude Code:

- can execute local development tasks
- can use tools
- can run in headless mode later
- can be governed by hooks and allowed/disallowed tool policies

### 5.3 Security/provenance before metadata convenience

Claude agreed that write-token protection, no spoofing, explicit decision detection, and provenance hardening should land before broader protocol metadata.

PAH v0.2 therefore prioritizes:

- write endpoint hardening
- participant separation
- decision detection
- local-only secrets
- no silent writes

### 5.4 CC schema proposal should converge with PAH schema

CC proposed YAML frontmatter with fields such as:

- `id`
- `from`
- `to`
- `type`
- `status`
- `re_dispatch`
- `target_version`
- `commit`
- `risk`
- `open_questions`

PAH should support this shape rather than inventing a competing one.

## 6. Users and Participants

### 6.1 Human user

#### Darrin

Role:

- product owner
- final approval authority
- exception handler
- decision maker

Needs:

- minimal interruptions
- high-signal phone alerts
- dashboard clarity
- explicit decisions with recommendation and consequence
- confidence that agents cannot bypass approval gates

### 6.2 Agent participants

#### Codex

Role:

- coding/research/spec agent
- PAH implementation owner
- local `C:\CODEX PG` writer
- read-only `C:\panda-gallery` reviewer unless explicitly approved

Allowed by default:

- write under `C:\CODEX PG`
- write Codex-to-Claude mailbox messages
- read `C:\panda-gallery`
- draft specs and scripts under CODEX folders

Blocked by default:

- write to `C:\panda-gallery`
- commit/push without Darrin approval
- send external messages without configured approval

#### Claude Desktop

Role:

- synthesis/review/dispatch partner
- product/design reasoning partner
- mailbox participant

Allowed by default in PAH:

- receive Codex messages
- send Claude-to-Codex messages
- propose tasks and decisions

Blocked by default:

- authorizing Codex implementation alone
- bypassing Darrin approval boundary

#### Claude Code

Role:

- tool-using local coding participant
- potential headless automation lane
- potential cross-check partner with Codex

Allowed by default in PAH v0.2:

- receive messages in a separate inbox
- return reports through explicit mailbox files

Future allowed actions:

- run bounded tasks through `claude -p`
- operate with allowed/disallowed tools
- emit hooks/logs to PAH

Blocked by default:

- write to `C:\panda-gallery` from Codex-originated messages without Darrin approval
- execute arbitrary shell/install/commit/push through PAH without policy approval

#### CC

Role:

- existing Claude Code track in `C:\panda-gallery`
- source of dispatch/lint/schema proposals

PAH stance:

- read CC proposal artifacts as reference
- do not mutate CC workspace without Darrin approval
- converge schema proposals before adopting a direct channel

## 7. Functional Scope

### 7.1 MVP v1 scope

PAH v1 should include:

- mailbox dashboard
- participant lanes
- active thread list
- structured message parser
- Darrin decision queue
- validation/lint page
- notification subsystem
- compose/send with provenance
- Claude Code inbox support
- local audit log
- settings page
- manual export/report

### 7.2 v1 non-goals

PAH v1 should not include:

- direct OpenAI API execution
- direct Anthropic API execution
- automatic writes to `C:\panda-gallery`
- autonomous commits/pushes
- PHI handling
- email sending to project stakeholders
- multi-user cloud access
- remote browser access
- production installer

### 7.3 v2+ scope candidates

- Claude Code headless adapter
- Claude Code hook integration
- CC-Codex cross-check channel
- direct OpenAI Responses adapter
- direct Anthropic Messages adapter
- app-level approval workflows
- git commit/push approval flow
- PowerShell automation runner
- packaged PySide6 desktop shell
- project portfolio support

## 8. Core Workflows

### 8.1 Morning / resume workflow

Trigger:

- Darrin opens PAH.

PAH actions:

1. Scan mailbox roots.
2. Load latest messages.
3. Parse structured metadata.
4. Build active thread list.
5. Build Darrin decision queue.
6. Identify stale waiting items.
7. Show latest git state.
8. Show notification health.
9. Recommend next action.

Output:

- dashboard state
- one-line status summary
- ranked queue of decisions and blocked work

### 8.2 Agent dispatch workflow

Trigger:

- Darrin or Codex sends a task to Claude or Claude Code.

PAH actions:

1. Require write token.
2. Require participant route.
3. Generate message ID.
4. Apply schema.
5. Write message to target inbox.
6. Append ledger entry for important messages.
7. Update thread state.
8. Log event.

Acceptance:

- message appears in target inbox
- ledger contains entry
- dashboard updates
- no unrelated files mutate

### 8.3 Darrin decision workflow

Trigger:

- message has `requires_darrin_decision: true`
- or `thread_status: waiting_on_darrin`
- or `action_owner: darrin`
- or status explicitly equals `Decision Needed`

PAH actions:

1. Add item to Darrin decision queue.
2. Show decision prompt:
   - question
   - options
   - recommendation
   - consequence
   - owner
   - blocked threads
3. Send notification if enabled and dedupe allows.
4. Wait for Darrin decision.
5. Record decision as a decision record.
6. Resume dependent work.

### 8.4 Claude Code task workflow v1

Trigger:

- Codex sends message to Claude Code inbox.

PAH actions:

1. Write file to Claude Code inbox.
2. Mark thread as `waiting_on_claude_code`.
3. Notify Darrin only if task is blocked or needs approval.
4. Await Claude Code or user-driven reply file.

Constraint:

- v1 does not launch Claude Code automatically.

### 8.5 Claude Code headless workflow v2

Trigger:

- Darrin approves PAH to run Claude Code headless for a bounded task.

PAH actions:

1. Build prompt from task message.
2. Select allowed tools.
3. Select disallowed tools.
4. Set working directory.
5. Run `claude -p` with output format JSON or stream JSON.
6. Capture stdout/stderr.
7. Write transcript/report into PAH log.
8. If tool use is deferred or permission needed, mark waiting on Darrin.
9. If files changed, show diff before commit/push.

Safety constraints:

- no bypass permissions by default
- no destructive shell commands without approval
- no write to `C:\panda-gallery` unless Darrin has explicitly approved the task

### 8.6 Cross-check workflow v2

Trigger:

- Codex and Claude Code both review a spec, mockup, or code change.

PAH actions:

1. Dispatch cross-check to both agents.
2. Parse structured `agrees_with`, `disagrees_with`, and `caught_by_one` fields.
3. Auto-resolve low-risk agreement items.
4. Escalate disagreements to Claude Desktop or Darrin.
5. Record synthesis result.

Constraint:

- Auto-resolved items cannot cross protected boundaries.

### 8.7 Notification workflow

Trigger:

- new decision-needed item
- new response-requested item
- stale thread
- failed validation
- long idle waiting state
- explicit test notification

PAH actions:

1. Generate event fingerprint.
2. Check notification settings.
3. Check cooldown and dedupe.
4. Redact sensitive content.
5. Send through configured provider.
6. Log result.

## 9. Message Schema

### 9.1 Compatibility requirement

PAH must support two metadata formats during transition:

1. Existing mailbox headers:
   - `Message-ID:`
   - `Reply-To:`
   - `Generated:`
   - `From:`
   - `To:`
   - `Status:`
2. Proposed YAML frontmatter:
   - machine-readable block at top of Markdown file

PAH should prefer YAML frontmatter when present and fall back to existing headers.

### 9.2 Recommended YAML frontmatter

```yaml
---
id: CODEX-20260426-183001-agent-hub-defaults
thread_id: AGENT-HUB-V1
from: codex
to: claude-desktop
type: response_request
status: open
created_at: 2026-04-26T18:30:01-07:00
priority: normal
action_owner: claude-desktop
requires_darrin_decision: false
approval_boundary: coordination_only
related:
  - CODEX-20260426-182516-agent-hub-prototype
deliverables: []
referenced_paths:
  - C:\CODEX PG\CODEX Agent Hub\CODEX_agent_hub.py
validation:
  commands: []
  status: not_run
risk: low
---
```

### 9.3 Required common fields

- `id`
- `thread_id`
- `from`
- `to`
- `type`
- `status`
- `created_at`

### 9.4 Participant IDs

Allowed v1 values:

- `darrin`
- `codex`
- `claude-desktop`
- `claude-code`
- `cc`
- `pah`

Future:

- `openai-api`
- `anthropic-api`
- `github`
- `twilio`

### 9.5 Message types

Allowed v1 values:

- `info`
- `dispatch`
- `response_request`
- `decision_request`
- `decision_record`
- `implementation_report`
- `status`
- `blocker`
- `cross_check`
- `counter_proposal`
- `escalation`
- `notification`
- `validation_report`

### 9.6 Thread statuses

Allowed v1 values:

- `open`
- `waiting_on_codex`
- `waiting_on_claude_desktop`
- `waiting_on_claude_code`
- `waiting_on_darrin`
- `in_progress`
- `blocked`
- `ready_for_review`
- `closed`
- `archived`

### 9.7 Approval boundary values

Allowed v1 values:

- `coordination_only`
- `read_only_review`
- `codex_pg_write_allowed`
- `panda_gallery_write_requires_darrin`
- `external_send_requires_darrin`
- `git_commit_requires_darrin`
- `git_push_requires_darrin`
- `destructive_action_forbidden`

### 9.8 Body sections

Recommended body sections:

- `## Summary`
- `## Context`
- `## Request`
- `## Deliverables`
- `## Validation`
- `## Open Questions`
- `## Approval Boundary`

Dispatch messages should also include:

- `## Scope`
- `## Out Of Scope`
- `## Acceptance Criteria`
- `## Verification Commands`

Implementation reports should also include:

- `## Changed Files`
- `## Verification Results`
- `## Residual Risk`

Decision requests should also include:

- `## Decision Needed`
- `## Options`
- `## Recommendation`
- `## Consequence`

## 10. Storage Model

### 10.1 File storage

PAH v1 uses the filesystem as the durable source of truth.

Primary stores:

- mailbox Markdown files
- ledger Markdown
- local notification config
- local notification state/log
- generated decision queue
- generated dashboard status cache if needed

### 10.2 Suggested folder layout

```text
C:\CODEX PG\
  CODEX Agent Hub\
    CODEX_agent_hub.py
    CODEX_start_agent_hub.ps1
    CODEX_README.md
    CODEX config\
      CODEX_notification_config.template.json
      CODEX_notification_config.local.json   # ignored
      CODEX_pah_config.local.json            # future ignored
    CODEX notifications\
      CODEX_notification_state.local.json    # ignored
      CODEX_notification_log.jsonl           # ignored
    CODEX reports\
  CODEX PANDA Agent Hub Spec\
    CODEX_PANDA_AGENT_HUB_PRODUCT_TECH_SPEC_v0_1.md
    CODEX_PAH_RESEARCH_NOTES_v0_1.md
  CODEX Claude Codex Mailbox\
    CODEX Inbox\
    CLAUDE Inbox\
    CODEX_CLAUDE_CODE Inbox\                # recommended eventual name
    CODEX_SENT\
    CLAUDE_SENT\
    CODEX Archive\
```

### 10.3 Folder naming decision

Current prototype created:

```text
C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Claude Code Inbox
```

Claude suggested:

```text
CODEX_CLAUDE_CODE Inbox
```

Recommendation:

- Rename to `CODEX_CLAUDE_CODE Inbox` in the next cleanup pass for consistency with machine parsing and CODEX prefix expectations.
- Keep a migration alias/compatibility check for the current folder if it contains files.

## 11. Permissions and Approval Model

### 11.1 Protected action classes

Protected actions require explicit Darrin approval:

- writing to `C:\panda-gallery`
- deleting files
- moving files across project boundaries
- committing
- pushing
- running dependency installs
- sending email to external recipients
- sending real SMS
- calling paid external APIs
- launching Claude Code with write tools
- running shell commands outside allowed policy
- uploading data to cloud services

### 11.2 Default allow policy

Allowed without extra Darrin approval:

- read `C:\CODEX PG`
- write under `C:\CODEX PG`
- read `C:\panda-gallery`
- read mailbox files
- write Codex-to-Claude coordination messages
- write Codex-to-Claude-Code coordination messages
- generate local specs
- run local validators
- send log-only notifications

### 11.3 Default deny policy

Denied unless explicitly approved:

- real SMS notifications
- external API-backed agents
- `C:\panda-gallery` writes
- git push
- destructive filesystem operations
- simulated inbound messages from another agent
- unattended headless Claude Code writes

## 12. Web/API Surface

### 12.1 Local server

Default bind:

```text
127.0.0.1:8765
```

Remote access:

- disabled by default
- not in v1 scope

### 12.2 Security requirements

- Write endpoints must require a per-run write token.
- Write endpoints must be POST-only.
- GET endpoints must be read-only.
- If Origin is present, Origin host must match Host.
- No token in URL query strings.
- No secrets in logs.
- High-risk operations require explicit confirmation in UI.

### 12.3 Endpoint specification v1

#### `GET /api/status`

Purpose:

- Return dashboard state.

Must not:

- write files
- update timestamps
- append logs
- mutate state

Returns:

- counts
- latest messages
- active threads
- Darrin decision queue
- validation summary
- notification status
- git status

#### `POST /api/send`

Purpose:

- Create an outbound mailbox message.

Requires:

- write token
- same-origin or trusted origin
- route
- subject
- body

Must reject:

- inbound spoof routes unless simulation mode enabled
- unknown route
- missing token

#### `POST /api/test-notification`

Purpose:

- Send or log a test notification.

Requires:

- write token

Must:

- never include secrets
- use provider config
- return provider result

#### `POST /api/write-decision-queue`

Purpose:

- Explicitly regenerate `CODEX_DARRIN_DECISIONS_NEEDED.md`.

Requires:

- write token

Rationale:

- Decision queue file writes should be explicit, not caused by status polling.

#### Future endpoints

- `POST /api/threads/{thread_id}/close`
- `POST /api/threads/{thread_id}/assign`
- `POST /api/decisions/record`
- `POST /api/validate`
- `POST /api/dispatch/claude-code`
- `POST /api/run/headless-claude-code`
- `POST /api/export/handoff`

## 13. Notification Specification

### 13.1 Providers

Supported v1 providers:

- `log_only`
- `twilio`
- `email_to_sms`
- `webhook`

### 13.2 Config files

Template:

```text
C:\CODEX PG\CODEX Agent Hub\CODEX config\CODEX_notification_config.template.json
```

Local ignored config:

```text
C:\CODEX PG\CODEX Agent Hub\CODEX config\CODEX_notification_config.local.json
```

### 13.3 Notification triggers

Supported v1 triggers:

- `darrin_decision_needed`
- `claude_response_requested`
- `validation_warning` (off by default)

Future triggers:

- stale thread
- failed headless run
- approval requested
- commit ready
- CI failed
- new Claude Code report

### 13.4 Notification dedupe

Every notification event must have a fingerprint:

```text
{kind}:{message_id_or_path}:{thread_id}
```

PAH must not resend an event if the fingerprint is already sent, unless Darrin manually resets notification state.

### 13.5 Notification message content

SMS body should include only:

- product prefix
- event type
- thread or task title
- one short action hint

SMS body must not include:

- API keys
- patient data
- PHI
- long file contents
- full stack traces
- private URLs unless approved

Example:

```text
PANDA Agent Hub: Darrin decision needed - Screen B target mockup selection is blocking v4.44.
```

## 14. UI Specification

### 14.1 Visual direction

PAH should use the Panda Gallery desktop visual vocabulary:

- dark shell
- compact panes
- low-radius controls
- muted borders
- peach active accent `#e8a87c`
- restrained typography
- dense but readable information
- no marketing hero screen
- no decorative gradients/orbs

### 14.2 Primary layout

Recommended desktop layout:

```text
Left rail: project/status/navigation
Center: active work surface
Right rail: compose/actions/context
Bottom: optional live activity/log strip
```

### 14.3 Primary screens

#### Overview

Purpose:

- Answer "what needs attention?"

Panels:

- Darrin decisions
- blocked threads
- active agent work
- latest reports
- notification state
- git state

#### Threads

Purpose:

- Show active and historical coordination threads.

Capabilities:

- filter by status
- filter by participant
- search by message ID/path
- show timeline
- close/archive thread

#### Agent Lanes

Purpose:

- Show each participant's queue.

Lanes:

- Codex
- Claude Desktop
- Claude Code
- CC
- Darrin

#### Darrin Queue

Purpose:

- Show only decisions that genuinely need Darrin.

Each item:

- question
- options
- recommendation
- consequence
- blocked threads
- source files
- action buttons

#### Dispatch Board

Purpose:

- Create and send structured tasks.

Capabilities:

- choose target agent
- choose message type
- choose priority
- choose approval boundary
- choose deliverable path
- validate before send

#### Validation

Purpose:

- Run mailbox and dispatch lint.

Validation categories:

- schema
- thread status
- missing reply links
- missing deliverables
- stale requests
- dangerous approval boundary
- bad paths

#### Notifications

Purpose:

- Configure phone/SMS/push behavior.

Capabilities:

- show provider
- test notification
- show last sent
- show cooldown
- show log-only mode
- reset sent fingerprints

#### Settings

Purpose:

- Manage local config safely.

Capabilities:

- project paths
- participant folders
- provider settings
- permission policy
- simulation mode
- export/import config

### 14.4 UI acceptance criteria

- Darrin can identify the top needed action within 5 seconds.
- Darrin can see whether a phone notification would fire.
- Darrin can distinguish agent suggestions from approved actions.
- Write/send buttons clearly show target participant and approval boundary.
- Disabled actions explain why they are disabled.
- Long paths do not break layout.

## 15. Validation and Lint Specification

### 15.1 Validation goals

PAH validation should catch coordination errors before they become lost work.

### 15.2 Initial validation rules

Message validation:

- missing ID
- duplicate ID
- missing thread ID on new schema messages
- missing participant
- unknown participant
- unknown message type
- unknown status
- important message absent from ledger
- response/report missing reply reference
- deliverable path missing
- source path missing
- path outside allowed root

Thread validation:

- open thread with no owner
- waiting thread older than threshold
- closed thread with open decision
- Darrin decision with no options
- implementation report with no validation

Safety validation:

- message requests `C:\panda-gallery` write without Darrin approval
- message requests commit/push without approval
- message includes possible secret pattern
- message includes phone/API credential fields

### 15.3 Integration with CC lint proposal

PAH should absorb or call `pg_dispatch_lint` once it is reviewed.

Potential PAH integration:

- show lint results in Validation screen
- run lint before sending dispatch
- block only high-confidence errors initially
- warn on schema drift
- support lenient mode during adoption

## 16. Claude Code Bridge Specification

### 16.1 v1 file bridge

PAH writes structured messages to Claude Code inbox.

Claude Code or Darrin manually checks:

```text
C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX_CLAUDE_CODE Inbox
```

PAH reads reports from whichever return path is adopted.

### 16.2 v1.5 watcher bridge

Optional watcher:

- watches Claude Code inbox
- surfaces new tasks
- optionally launches a prompt in Claude Code if user approves
- logs result

### 16.3 v2 headless bridge

PAH can run:

```text
claude -p "<task>" --output-format json --allowedTools "<tools>" --disallowedTools "<tools>"
```

Requirements:

- explicit Darrin approval to enable
- local path policy
- tool allowlist
- command log
- diff review before any protected action

### 16.4 Hook bridge

Claude Code hooks can:

- notify PAH when Claude Code needs permission
- log tool usage
- block unapproved writes
- feed context from PAH at session start
- write final reports at stop

Hook integration must be reviewed because hooks run automatically and can access the user's environment.

## 17. Direct API Adapter Specification

### 17.1 OpenAI adapter, future

Use OpenAI Responses API.

Adapter responsibilities:

- convert PAH task into model input
- include PAH policy as developer/system instructions
- expose PAH actions as strict function tools
- require approval before write-capable function tools execute
- store response ID / conversation ID / metadata
- log token/cost estimates where available

Do not expose:

- arbitrary shell
- arbitrary filesystem writes
- secrets
- unapproved external sends

### 17.2 Anthropic adapter, future

Use Anthropic Messages API for direct Claude model calls.

Adapter responsibilities:

- convert PAH messages into Anthropic message format
- pass system prompt separately
- set `max_tokens`
- capture request ID if available
- support streaming later

### 17.3 Agent SDK / managed agent option, future

Only consider after:

- local schema stable
- approval model stable
- validation stable
- logging stable

Potential use:

- multi-agent handoffs
- guardrails
- traces
- managed tool policy

## 18. Audit Log Specification

### 18.1 Events to log

- app start/stop
- message sent
- message parsed
- validation run
- validation failure
- notification sent
- notification failed
- decision recorded
- task dispatched
- task completed
- protected action requested
- protected action approved
- protected action denied
- headless run started
- headless run completed

### 18.2 Event fields

```json
{
  "event_id": "PAH-EVT-20260426-185000-abc123",
  "time": "2026-04-26T18:50:00-07:00",
  "actor": "codex",
  "action": "message_sent",
  "thread_id": "AGENT-HUB-V1",
  "message_id": "CODEX-...",
  "target": "claude-desktop",
  "paths": [],
  "approval_id": null,
  "result": "ok"
}
```

### 18.3 Log storage

Recommended:

```text
C:\CODEX PG\CODEX Agent Hub\CODEX logs\CODEX_pah_events.local.jsonl
```

Should be ignored by git if it may include sensitive local operational details.

## 19. Configuration Specification

### 19.1 Config files

Committed templates:

- `CODEX_pah_config.template.json`
- `CODEX_notification_config.template.json`

Ignored local files:

- `CODEX_pah_config.local.json`
- `CODEX_notification_config.local.json`
- `CODEX_secret_store.local.json`

### 19.2 Config categories

- project paths
- participant folders
- notification providers
- write token settings
- allowed routes
- approval policy
- stale thresholds
- API adapter settings
- Claude Code command path
- tool allowlists
- tool denylists

### 19.3 Secrets

Secrets must not be committed.

Secret examples:

- OpenAI API key
- Anthropic API key
- Twilio auth token
- SMTP password
- phone number
- webhook bearer token

Future improvement:

- Windows Credential Manager integration.

## 20. Implementation Roadmap

### Phase 0: Prototype

Status: mostly complete

Done:

- local app
- dashboard
- basic parser
- compose
- notification config
- token-protected write endpoints
- separate Claude Code inbox

Remaining cleanup:

- rename Claude Code inbox to preferred final name
- stop/replace duplicate old running server process if any
- add explicit decision queue write button
- finish schema parser

### Phase 1: Local hardening

Estimated effort: 1-2 focused days

Deliverables:

- full read-only status guarantee
- token and origin checks completed
- inbound spoofing disabled
- local config templates
- notification page
- log-only notification test
- explicit Darrin decision detection
- improved Reply-To parsing
- participant route model

Acceptance:

- no dashboard polling creates git diffs
- tokenless writes fail
- no simulated inbound routes in normal UI
- notification secrets ignored by git

### Phase 2: Schema and lint

Estimated effort: 2-4 focused days

Deliverables:

- YAML frontmatter parser
- compatibility parser for existing headers
- schema validator
- CC proposal alignment document
- dispatch preflight lint
- active thread status model
- message migration helper for active threads

Acceptance:

- new PAH messages include schema
- old messages still parse
- validation page separates errors/warnings/info
- Darrin queue only shows explicit Darrin decisions

### Phase 3: Dashboard and workflow UI

Estimated effort: 3-5 focused days

Deliverables:

- revised UI matching PG design grammar
- overview screen
- thread detail screen
- participant lanes
- Darrin decision cards
- dispatch composer with validation
- notification settings/test panel

Acceptance:

- Darrin can identify top action within 5 seconds
- all write actions show target and boundary
- disabled actions explain why

### Phase 4: Claude Code bridge

Estimated effort: 3-7 focused days depending on local Claude Code behavior

Deliverables:

- Claude Code inbox watcher
- optional headless runner
- allowed/disallowed tool policy
- hooks draft
- run transcript capture
- diff review before protected actions

Acceptance:

- PAH can dispatch a read-only Claude Code analysis task
- PAH can ingest Claude Code report
- PAH never triggers unapproved `C:\panda-gallery` write

### Phase 5: Direct API lanes

Estimated effort: 1-2 weeks

Deliverables:

- OpenAI Responses adapter
- Anthropic Messages adapter
- provider config and secret handling
- cost/rate controls
- tool schemas
- approval gates around tool calls

Acceptance:

- direct model calls are optional
- local file workflow remains primary
- API keys stay out of git
- all tool calls are logged

### Phase 6: Packaged desktop app

Estimated effort: 2-4 weeks

Deliverables:

- PySide6 shell or packaged local web app
- tray/background watcher
- startup registration option
- polished UI
- installer/update strategy

## 21. Testing Strategy

### 21.1 Unit tests

Test:

- metadata parser
- YAML frontmatter parser
- existing header parser
- thread grouping
- decision detection
- notification dedupe
- path validation
- route validation
- write-token rejection

### 21.2 Integration tests

Test:

- send message to Claude inbox
- send message to Claude Code inbox
- parse Claude reply
- generate Darrin queue
- run validation
- log-only notification
- invalid token write rejection

### 21.3 Manual tests

Test:

- open dashboard
- refresh without file mutations
- compose message
- test SMS in log-only mode
- verify git status panel
- verify no secrets in git status

### 21.4 Safety tests

Test:

- attempt inbound spoofing
- attempt tokenless POST
- attempt cross-origin POST
- attempt path outside `C:\CODEX PG`
- attempt protected action without approval

## 22. Acceptance Criteria for PAH v1

PAH v1 is acceptable when:

- all active threads are visible
- Darrin decision queue is high-signal
- phone notifications can be configured safely
- no polling mutates files
- write endpoints are protected
- Claude Code has a separate route
- mailbox schema/lint catches common drift
- all protected actions are gated
- no `C:\panda-gallery` writes happen from PAH
- Darrin can resume project status in under 60 seconds

## 23. Open Decisions

Governance update:

Darrin has stated that he is not qualified to answer many technical PAH implementation questions and will generally follow the Codex / Claude Desktop / Claude Code recommendation. Therefore, purely technical PAH decisions should be agent-voted and recommended, not pushed to Darrin, unless they affect UX/functionality, dental correctness, safety, cost, external communication, or protected actions.

Decision governance reference:

```text
C:\CODEX PG\CODEX PANDA Agent Hub Spec\CODEX_PAH_DECISION_GOVERNANCE_v0_1.md
```

### PAH-DEC-001: Claude Code inbox folder name

Options:

- `CODEX Claude Code Inbox` (current)
- `CODEX_CLAUDE_CODE Inbox` (Claude preference)
- `CLAUDE_CODE Inbox`

Recommendation:

- Use `CODEX_CLAUDE_CODE Inbox`.

### PAH-DEC-002: Schema strictness

Options:

- lenient for all messages
- strict for new PAH messages only
- strict for all messages after migration date

Recommendation:

- strict for new PAH-generated messages; lenient warnings for historic messages.

### PAH-DEC-003: Direct CC-Codex channel

Options:

- no direct channel
- low-risk cross-check only
- full agent-to-agent routing

Recommendation:

- low-risk cross-check only after schema/lint is stable.

### PAH-DEC-004: SMS provider

Options:

- Twilio
- email-to-SMS
- webhook relay
- log-only only

Recommendation:

- keep log-only now; add Twilio if Darrin wants reliable phone SMS.

### PAH-DEC-005: UI shell

Options:

- browser-local web app
- PySide6 desktop shell
- hybrid PySide6 shell wrapping local web UI

Recommendation:

- browser-local through v1; PySide6 shell after workflow stabilizes.

### PAH-DEC-006: Direct API adapters

Options:

- no direct APIs
- OpenAI only
- Anthropic only
- both

Recommendation:

- defer until Phase 5; implement both only if local orchestration is proving useful.

## 24. Source References

OpenAI:

- Responses API reference: https://platform.openai.com/docs/api-reference/responses/compact?api-mode=responses
- Tools guide: https://platform.openai.com/docs/guides/tools?api-mode=responses
- Migrate to Responses: https://platform.openai.com/docs/guides/migrate-to-responses
- Agents SDK overview: https://platform.openai.com/docs/guides/agents-sdk/
- Agents SDK guardrails: https://openai.github.io/openai-agents-python/guardrails/
- Agents SDK handoffs: https://openai.github.io/openai-agents-python/handoffs/
- Agents SDK tracing: https://openai.github.io/openai-agents-python/tracing/

Anthropic / Claude:

- API overview: https://docs.anthropic.com/en/api/overview
- Client SDKs: https://docs.anthropic.com/en/api/client-sdks
- Messages streaming: https://docs.anthropic.com/claude/reference/messages-streaming
- Claude Code headless mode: https://docs.claude.com/en/docs/claude-code/sdk/sdk-headless
- Claude Code SDK: https://docs.anthropic.com/s/claude-code-sdk
- Claude Code hooks reference: https://docs.anthropic.com/en/docs/claude-code/hooks
- Claude Code hooks guide: https://docs.anthropic.com/en/docs/claude-code/hooks-guide

Twilio:

- SMS quickstart: https://www.twilio.com/docs/messaging/quickstart
- Messages resource: https://www.twilio.com/docs/sms/api/message
- SMS tutorial: https://www.twilio.com/docs/messaging/tutorials/how-to-send-sms-messages

Security:

- OWASP CSRF Prevention Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html

Local coordination references:

- `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\20260427_000100_CLAUDE_to_CODEX_panda_hub_holding_reply.md`
- `C:\panda-gallery\workflows\cc_mailbox\CLAUDE Inbox\20260426_233000_CC_to_CLAUDE_proposal_dispatch_schema_and_direct_channel.md`

## 25. Immediate Next Implementation Slice

Recommended next slice:

1. Rename or alias Claude Code inbox to final folder name.
2. Add YAML frontmatter parser.
3. Make PAH-generated messages emit both YAML frontmatter and legacy headers.
4. Add participant route table.
5. Add explicit decision queue write button.
6. Add notification settings UI fields.
7. Add validation page filters.
8. Add PAH event log.
9. Add spec link panel in app.
10. Send Claude a spec-review request after Screen B / v4.44 urgency clears.

This slice improves parallel development speed without introducing direct model API risk.

## 26. CC Review Addendum

Source review:

```text
C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\20260427_010000_CC_to_CODEX_pah_v0_1_review.md
```

Digest:

```text
C:\CODEX PG\CODEX PANDA Agent Hub Spec\CODEX_PAH_CC_REVIEW_DIGEST_AND_DECISIONS_v0_1.md
```

### 26.1 CC Verdict

CC reviewed PAH v0.1 and returned: **approve with changes**.

CC agrees with the core build order:

- file-first orchestration
- schema before direct API lanes
- PAH as router
- Claude Code as a separate participant
- security/provenance before protocol convenience
- direct OpenAI/Anthropic API lanes deferred

### 26.2 Required Schema Additions

PAH schema v1 should add:

```yaml
schema_version: 1
replies_to: CLAUDE-20260426-220500-am-screen-b-ux-redesign-mockup
target_version: v4.43
prerequisite_commit: c9178ff
commit: 445e2e4
priority: normal
validation:
  commands: []
  status: complete
  passed: true
  ran_at: 2026-04-27T00:00:00-07:00
```

Clarifications:

- `schema_version` is required for new PAH messages.
- `replies_to` is direct ancestry.
- `related` remains a list of non-parent cross-references.
- `target_version`, `prerequisite_commit`, and `commit` are optional, but validated when present.
- `priority` is constrained to `low | normal | high | urgent`.
- `urgent` automatically enters the Darrin decision/attention queue.
- `created_at` must be ISO-8601 with an explicit timezone offset.
- `validation.passed` removes ambiguity between completed-passed and completed-failed.
- `validation.ran_at` lets PAH distinguish fresh validation from stale validation.

### 26.3 Hook Bridge Constraints

Claude Code hooks remain Phase 4 only.

Additional constraints from CC:

- hooks must be opt-in per Claude Code session, not global by default
- a kill-switch must exist
- first hook rollout is logging-only
- start with `PostToolUse` logging after Phase 3 has run clean
- do not add `PreToolUse` blocking until logging has run clean for at least one week
- do not bundle hooks into the watcher bridge

### 26.4 Claude Code Bridge Refinement

Phase 1 file bridge can ship now if approved, with atomic writes.

Phase 2 watcher should wait until schema exists.

Phase 3 headless first task should be read-only spec critique:

```text
allowedTools: Read,Grep,Glob,WebFetch
disallowedTools: Edit,Write,Bash,NotebookEdit
working directory: temporary worktree
approval: one Darrin decision_record per run
```

Lint should not be a Claude Code task. PAH should run lint deterministically via subprocess.

### 26.5 Lint Integration

`pg_dispatch_lint.py` remains the canonical implementation.

PAH should call it, not duplicate it:

```text
python C:\panda-gallery\workflows\tools\pg_dispatch_lint.py --json <message_path>
```

The validation page renders the JSON output.

Future improvement:

- add `--bible-path` to make the lint reusable outside the PG repo context

### 26.6 Direct Channel Convergence

PAH owns routing.

The direct CC-Codex channel exists inside PAH as message types:

- `cross_check`
- `counter_proposal`
- `escalation`

Auto-resolution rule, draft:

- if `disagrees_with` is empty
- and `risk: low`
- and `caught_by_one` contains no high-risk item
- then `agrees_with` items may be marked synthesized
- Claude Desktop receives a digest, batched daily by default

Any disagreement or high-risk item escalates to Claude Desktop.

### 26.7 Approval Boundary Update

Adopt this wording:

> Codex-originated messages may request Claude Code work, but cannot authorize Claude Code to write to `C:\panda-gallery`. Codex-originated messages may authorize Claude Code to read `C:\panda-gallery`. Claude Code writes to `C:\panda-gallery` require an explicit Darrin `decision_record` message naming (a) the specific files allowed to be written, (b) the `--allowedTools` flag value Claude Code will run with, and (c) the working directory. Reuse of an approval across tasks is forbidden; every Claude Code write run needs its own approval record in the audit log.

### 26.8 Additional PAH Requirements From CC

#### Atomic inbox writes

Message writes must use a temporary file and rename:

```text
message.md.tmp -> message.md
```

#### Idempotency

PAH must not re-trigger notifications, decisions, or processing when restarted and re-reading old files.

Suggested state:

```text
C:\CODEX PG\CODEX Agent Hub\CODEX state\CODEX_processed_messages.local.json
```

#### Backpressure

PAH should define:

- max messages per thread
- flood warning threshold
- dashboard degradation behavior

#### Quarantine

Malformed messages should be quarantined or clearly marked invalid so they do not repeatedly pollute active dashboard state.

#### PAH Inbox

Because `pah` is a participant ID, PAH eventually needs either:

- a `PAH Inbox`, or
- explicit documentation that PAH is a router only and not an addressable agent

Recommendation:

- add `PAH Inbox` after command schema is safe
- keep it read/validation-oriented at first, not action-capable

### 26.9 New Open Decisions From CC Review

#### PAH-DEC-007: Schema adoption

Approve PAH frontmatter with CC additions?

Recommendation: yes.

#### PAH-DEC-008: Phase 1 file bridge

Green-light Claude Code file bridge now, with atomic writes and no auto-execution?

Recommendation: yes.

#### PAH-DEC-009: Claude Code inbox folder rename

Rename:

```text
CODEX Claude Code Inbox
```

to:

```text
CODEX_CLAUDE_CODE Inbox
```

with a one-week migration alias?

Recommendation: yes.

#### PAH-DEC-010: First headless task scope

Use read-only spec critique as the first future headless Claude Code task?

Recommendation: yes, but defer until after schema/lint/file bridge are stable.
