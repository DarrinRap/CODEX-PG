# PANDA Agent Hub Final Design Specification v1

Generated: 2026-04-26 20:10:00 -07:00
Last revised: 2026-04-27 02:35:00 -07:00
Status: Design package for Darrin approval, CC final review findings patched
Project name: PANDA Agent Hub
Short name: PAH
Owner: Darrin
Primary spec author: Codex
Review partners: Claude Desktop, Claude Code / CC
Implementation boundary: no PAH app implementation coding until Darrin approves this design

## 1. Purpose

PANDA Agent Hub is a local-first coordination cockpit for parallel AI-assisted development.

Its job is to reduce Darrin's coordination load while Codex, Claude Desktop, Claude Code / CC, and future agents work in parallel.

PAH must answer quickly:

- What is moving?
- What is blocked?
- Which agent owns the next action?
- Which messages are reliable?
- Which deliverables are validated?
- Which decisions truly require Darrin?
- Which work can proceed through agent vote?
- Which protected actions need explicit approval?

PAH is successful when Darrin can step away, receive only high-value notifications, return to the dashboard, and understand current state within 60 seconds.

## 2. Non-Negotiable Boundary

This package is a design and specification package only.

It may include:

- research notes
- architecture decisions
- schemas
- governance rules
- workflow definitions
- static UX mockups
- rendered mockup screenshots
- design reviews

It must not include:

- changes to PAH application runtime code
- new automation that executes agent work
- live Claude Code headless runs
- writes to `C:\panda-gallery`
- commits, pushes, external sends, installs, or paid API calls without explicit approval

### 2.1 Standalone App Boundary

PAH is a totally standalone app, separate from Panda Gallery.

Rules:

- PAH lives under `C:\CODEX PG` for now, not inside `C:\panda-gallery`.
- PAH must not depend on Panda Gallery runtime code.
- PAH may coordinate work about Panda Gallery, but it is not architecturally part of Panda Gallery.
- PG-specific lint/design conventions may be cited as optional reference material, not PAH runtime dependencies.
- PAH must include and run its own standalone schema validator.
- PAH v1 must not import, subprocess, path-link, or otherwise depend on `pg_dispatch_lint.py`; any future PG dispatch validator adapter requires a separate approval and must not be part of PAH core.
- PAH may borrow the discipline of PG's design doctrine, but it should maintain its own design-system layer.
- No write access to `C:\panda-gallery` is allowed unless Darrin explicitly approves a protected action.
- CC may review PAH design and implementation through mailbox messages, but PAH must not depend on CC-authored code that lives in `C:\panda-gallery`.

## 3. Product Principle

PAH should make parallel development feel supervised, not chaotic.

Darrin should not be asked to decide low-level technical details. The agents should vote, converge, and recommend. Darrin should be consulted when the question affects UX, dental/product judgment, safety, cost, credentials, external communication, or protected actions.

## 4. Participants

### Darrin

Role:

- product owner
- UX and dental judgment authority
- approval authority for protected actions
- escalation receiver

Darrin is consulted for:

- UX appearance
- UX functionality
- workflow feel
- what deserves phone/SMS interruption
- dental terminology
- dental workflow assumptions
- clinical/dental correctness
- feature usefulness
- PHI/patient-data questions
- external communication
- paid providers or credentials
- writes to `C:\panda-gallery`
- commits/pushes/publishing

### PAH

Role:

- router
- dashboard
- validator
- audit ledger
- decision queue
- notification coordinator
- future adapter host

PAH does not invent authority. It records authority.

### Codex

Role:

- coding/research/spec agent
- PAH implementation owner after approval
- local `C:\CODEX PG` writer
- read-only `C:\panda-gallery` reviewer unless explicitly approved

### Claude Desktop

Role:

- synthesis partner
- product/design reviewer
- coordination reviewer
- mailbox participant
- possible future PAH MCP client

### Claude Code / CC

Role:

- implementation practicality reviewer
- repo/tooling risk reviewer
- future headless review agent
- possible future MCP participant

Claude Code is separate from Claude Desktop. It needs independent queues, ownership, unread state, safety boundaries, and adapter policy.

## 5. Governance Model

### 5.1 Agent-Decided Technical Questions

Codex, Claude Desktop, and Claude Code / CC vote or recommend on:

- message schema fields
- route and inbox naming
- thread status model
- lint integration
- atomic write mechanics
- idempotency mechanics
- watcher design
- headless bridge safety mechanics
- hook rollout sequence
- direct API adapter sequencing
- validation rules
- implementation roadmap ordering
- code organization
- test strategy

If all three agree, PAH records the recommendation as accepted for implementation planning.

If two agree and one dissents on a low-risk technical question, PAH records the dissent and follows the majority.

If disagreement involves UX, dental, safety, cost, external communication, or protected actions, PAH escalates to Darrin.

### 5.2 Darrin-Consulted Questions

Darrin must be consulted on:

- UX appearance/functionality
- dental and clinical judgment
- notification interruption tolerance
- protected writes
- external sends
- paid providers
- credentials
- safety boundary changes

### 5.3 Decision Queue Rule

Darrin's decision queue must stay narrow.

Do not queue purely technical implementation questions if the agents can decide them.

Do queue:

- any message with `requires_darrin_decision: true`
- any message with `thread_status: waiting_on_darrin`
- any message with `priority: urgent`
- any message whose `approval_boundary` contains `_requires_darrin`
- any UX/dental/safety/cost/external/protected-action question

Do not infer Darrin-needed status merely because a message mentions "Darrin."

## 6. Architecture Summary

PAH v1 is a local-first control plane.

Core layers:

- file-backed mailbox transport
- participant registry
- schema v1 parser
- thread engine
- decision engine
- validation/lint engine
- notification engine
- audit ledger
- static and future dynamic dashboard UI
- optional adapters after approval

PAH should treat direct APIs, MCP, hooks, and headless runs as adapters, not as the foundation.

### 6.1 Modular Build and Assembly Plan

PAH must be built as modules assembled by one app shell, not as a monolith.

Required modules:

- `app_shell`: process lifecycle, local server startup, Windows tray shell, open-dashboard command
- `core`: message schema, participant registry, thread model, decision model
- `mailbox`: file bridge, atomic writes, folder routing, quarantine, tombstones, idempotency
- `validation`: generic PAH schema validator, optional project-specific lint adapters
- `security`: tokens, approval records, protected-action checks, path-scope validation
- `dashboard`: web UI/API, Darrin queue, thread board, validation console
- `notifications`: notification log, desktop popups, tray badge, SMS/log providers
- `diagnostics`: two-way communication tests and route health checks
- `adapters`: disabled-by-default Claude Code, Codex, MCP, hooks, SMS, and future live integrations

Assembly rules:

- each module is independently testable
- risky adapters are feature-flagged off by default
- the app shell wires modules together through explicit interfaces
- CC can review schema/security/adapters without wading through UI code
- implementation must avoid one large all-purpose PAH file
- any module that can spend money, send externally, execute agent work, or write outside PAH's workspace stays disabled until Darrin approves

### 6.2 Parallel Module Ownership Plan

Parallel development is allowed when file ownership is clean.

Recommended split:

- Codex owns app shell, dashboard UI, mailbox parser/router, Windows tray/popup wiring, review/export packets, and standalone packaging.
- CC reviews schema validator details, approval-record enforcement, quarantine/idempotency rules, and Claude Code adapter safety contracts through mailbox feedback; Codex owns all PAH runtime code under `C:\CODEX PG`.
- Claude Desktop reviews UX/workflow coherence, Darrin queue clarity, and synthesis/escalation behavior.

Parallel safety rules:

- schema contracts freeze before multiple agents code against them
- modules have disjoint file ownership during parallel work
- CC does not write to `C:\panda-gallery` for PAH
- live adapters remain disabled/stubbed until reviewed
- integration happens through PAH review packets and explicit merge checkpoints

## 7. Integration Strategy

### Phase 1: File Bridge

Ship first.

Requirements:

- participant inboxes
- atomic writes using `.tmp` then rename
- schema v1 frontmatter
- idempotent processing
- quarantine malformed messages
- parse-failure visibility
- message provenance
- no inbound spoofing in production mode

Participant folders:

- `CODEX Inbox`
- `CLAUDE Inbox`
- `CODEX_CLAUDE_CODE Inbox`

The older `CODEX Claude Code Inbox` may be supported as a one-week migration alias, but new writes should use `CODEX_CLAUDE_CODE Inbox`.

PAH is router-only in v1. It is a participant for audit/provenance purposes, but it is not an addressable mailbox participant until a future PAH command protocol is approved.

### Phase 2: Watcher Bridge

Ship after schema.

Requirements:

- read-only watcher first
- dedupe on restart
- notification cooldowns
- stale-thread detection
- no auto-processing of replies until policy exists

### Phase 3: Headless Agent Bridge

Approval-gated.

Claude Code adapter:

- first task class: read-only spec/code review
- restrictive tool surface: `--tools "Read,Grep,Glob,WebFetch"`
- allowed tools: `Read,Grep,Glob,WebFetch`
- disallowed tools: `Edit,Write,Bash,NotebookEdit`
- permission mode: `plan`
- output format: JSON
- no session persistence by default
- max budget required
- timeout required
- working directory explicit
- temporary worktree required; never run first pilot against the live repo working tree
- strict MCP isolation required: `--strict-mcp-config` with an empty or PAH-owned read-only MCP config
- settings isolation required: no user/project/local settings may silently add tools, hooks, skills, plugins, or MCP servers to the pilot run
- `--add-dir` is prohibited in the first pilot unless the approval record names every added directory
- command preview must be stored in the approval record before execution
- canonical command, capture, timeout, cancellation, MCP config, and hash checks are defined in Section 16.3.2

Codex adapter:

- future `codex exec`, Codex SDK, or Codex MCP server
- read-only sandbox first
- JSON/JSONL output captured
- same approval/audit model as Claude Code

No headless adapter is enabled until Darrin approves the first live paid/external call.

### Phase 4: MCP and Hooks

Future only.

MCP:

- PAH may expose a local MCP server for thread state, decision state, routing, and validation.
- Claude Desktop and Claude Code may call PAH tools after approval.
- Codex and Claude Code MCP server modes may be evaluated after the local core is stable.

Hooks:

- opt-in per Claude Code session
- never global by default
- kill switch required
- logging-only first
- `PostToolUse` logging must run clean for one week before any `PreToolUse` blocking
- separate paranoid review before adoption

## 8. Message Schema v1

All structured PAH messages should use YAML frontmatter plus Markdown body.

### 8.1 Required Common Fields

```yaml
schema_version: 1
id: CODEX-20260426-201000-topic-slug
thread_id: AGENT-HUB-V1
from: codex
to: claude-code
type: dispatch
status: open
thread_status: active
created_at: 2026-04-26T20:10:00-07:00
priority: normal
action_owner: claude-code
requires_darrin_decision: false
approval_boundary: coordination_only
```

### 8.2 Required Field Rules

- `schema_version` must be `1` for this spec.
- `created_at` must be ISO-8601 with explicit timezone offset.
- `priority` enum: `low`, `normal`, `high`, `urgent`.
- `status` enum: `draft`, `open`, `in_progress`, `blocked`, `review_complete`, `complete`, `shipped`, `closed`, `rejected`.
- `thread_status` enum: `active`, `waiting_on_agent`, `waiting_on_darrin`, `blocked`, `resolved`, `archived`.
- `from` and `to` must be participant registry IDs or aliases.
- `id` must be globally unique.
- `thread_id` must be stable for the workstream.
- `thread_status: waiting_on_darrin` is the only thread-status value that automatically enters Darrin's queue.

### 8.3 Optional Linkage Fields

```yaml
replies_to: CLAUDE-20260426-220500-topic-slug
related:
  - CODEX-20260426-183001-agent-hub-defaults
```

Rules:

- `replies_to` is a single direct parent message ID.
- `related` is a list of cross references.
- Thread reconstruction uses `thread_id`, then `replies_to`, then timestamp.

### 8.4 Optional Code-Ship Fields

```yaml
target_version: v4.43
prerequisite_commit: c9178ff
commit: 445e2e4
```

Rules:

- optional, never common-required
- validated when present
- `prerequisite_commit` should resolve in the target repo when available
- `commit` records delivered code or docs work

### 8.5 Validation Block

```yaml
validation:
  commands:
    - "python CODEX_pah_validator.py --json <path>"
  status: complete
  passed: true
  ran_at: 2026-04-26T20:10:00-07:00
  timeout_seconds: 60
```

Rules:

- `validation.status` enum: `not_run`, `running`, `complete`, `failed`
- `passed` is required when status is terminal
- `ran_at` is required when validation has run
- `timeout_seconds` defaults to 60 when omitted
- `validation.status` must transition to `complete` or `failed` within `timeout_seconds`
- a message stuck at `running` past the timeout is flagged as stalled in the Validation Console
- inbound participant messages must have terminal validation state before they can trigger notifications, approvals, adapter runs, or Darrin queue changes

### 8.6 Message Types

Core:

- `dispatch`
- `recommendation`
- `review`
- `status_update`
- `decision_record`
- `cross_check`
- `counter_proposal`
- `escalation`
- `validation_report`
- `handoff`

Special CC/Codex collaboration:

- `cross_check`: second agent reviews first agent's output
- `counter_proposal`: agent disagrees and proposes alternative
- `escalation`: disagreement or risk requires Claude Desktop or Darrin

`cross_check` payload:

```yaml
cross_check:
  checked_message_id: CODEX-20260426-201000-topic-slug
  checked_by: claude-code
  agrees_with:
    - finding_id: F-001
      summary: "Schema versioning is required."
  disagrees_with: []
  caught_by_one:
    - finding_id: F-002
      risk: low
      summary: "Add duplicate-ID hash conflict handling."
  recommendation: synthesize
```

`cross_check` auto-resolution rule:

- if `disagrees_with` is empty
- and every `caught_by_one` entry has `risk: low`
- and no item has an approval boundary containing `_requires_darrin`
- and no involved message has `priority: urgent`
- then PAH may mark the checked items as synthesized and include them in the next digest.

Any disagreement, medium-or-higher `caught_by_one.risk`, protected boundary, urgent priority, or unclear recommendation creates an `escalation` message instead.

### 8.7 Approval Boundary Values

Initial enum:

- `coordination_only`
- `read_only_review`
- `codex_workspace_write_allowed`
- `panda_gallery_read_only`
- `panda_gallery_write_requires_darrin`
- `git_commit_requires_darrin`
- `git_push_requires_darrin`
- `external_send_requires_darrin`
- `paid_api_requires_darrin`
- `sms_send_requires_darrin`

Any value containing `_requires_darrin` automatically enters the Darrin queue.

Every write-capable approval boundary must name explicit path roots in a `write_scope` block. Approval boundaries are invalid if they rely on ambiguous labels such as `PG`.

```yaml
write_scope:
  allowed_roots:
    - C:\CODEX PG
  denied_roots:
    - C:\panda-gallery
  exact_paths: []
```

Path validation rules:

- path matching is case-insensitive on Windows and case-sensitive on POSIX
- all paths are normalized to absolute paths before comparison
- symlinks and junctions are resolved before matching
- a write is allowed only when the normalized target is under at least one `allowed_roots` entry and under no `denied_roots` entry
- `exact_paths` matches only literal file paths, not directories or globs
- deny rules override allow rules
- path validation failure blocks the action and creates an audit ledger entry

## 9. Participant Registry

Initial participants:

```yaml
participants:
  darrin:
    display: Darrin
    kind: human
    inbox: null
  pah:
    display: PANDA Agent Hub
    kind: router
    inbox: null
    addressable: false
  codex:
    display: Codex
    kind: agent
    inbox: CODEX Inbox
    aliases: [CODEX]
  claude-desktop:
    display: Claude Desktop
    kind: agent
    inbox: CLAUDE Inbox
    aliases: [claude, CLAUDE]
  claude-code:
    display: Claude Code / CC
    kind: agent
    inbox: CODEX_CLAUDE_CODE Inbox
    aliases: [cc, CC, claude_code, Claude Code]
```

Registry duties:

- route messages
- normalize aliases
- prevent spoofing
- control unread state
- support agent-specific safety policy

## 10. Routing Model

PAH owns routing.

Rules:

- In v1, PAH is router-only; messages addressed directly to `pah` are invalid unless they are internal ledger/system records.
- The only v1 exception is an explicit Darrin `decision_record` generated by PAH UI to create an approval record.
- Outbound messages are created by PAH on behalf of an authenticated local actor.
- Inbound agent messages are read from inbox files.
- File-based inbound messages must use canonical participant IDs in `from` and `to`; aliases are display-only and invalid in frontmatter.
- PAH cross-checks the source folder against the route: inbox folders must match `to`, sent folders must match `from`, and mismatches are quarantined as `spoofing_attempt`.
- Production UI does not allow "Claude to Codex" spoofed composition.
- Simulation mode may allow fake inbound messages, but they must be labeled `simulation: true`.
- Every routed message gets a ledger entry.

## 11. Validation and Lint

PAH core validation is standalone.

Core PAH validator:

- parses YAML frontmatter and Markdown body
- validates schema version, required fields, enums, participant IDs, path scopes, approval boundaries, timestamps, content hashes, and validation terminal state
- does not depend on Panda Gallery
- ships as part of PAH
- is the only validator PAH v1 runs for PAH messages

Panda Gallery dispatch lint is external reference material only in PAH v1.

PAH v1 must not call `C:\panda-gallery\workflows\tools\pg_dispatch_lint.py`, import Panda Gallery code, or require `C:\panda-gallery` to exist. If PAH later needs to validate Panda Gallery dispatches, that work is a separate external-adapter ticket with its own approval and boundary review. Shared rule patterns may be documented in prose or pseudocode under `C:\CODEX PG`, then reimplemented inside PAH's standalone validator.

Validation categories:

- schema
- participant
- route
- timestamp
- priority
- approval boundary
- file paths
- design/source citations where relevant
- prerequisite commit
- validation block terminal state
- PHI/secrets pattern scan

Compose-time validation:

- the Dispatch screen runs PAH core validation before Send is enabled
- P0/P1 validation failures block dispatch
- warnings are shown but do not block unless the thread policy says otherwise

## 12. Idempotency and Backpressure

### Idempotency

PAH must not retrigger notifications or actions after restart.

Recommended state:

- `.pah_state/processed_messages/<message-id>.json`
- `.pah_state/notifications/<message-id>-<event>.json`
- content hash stored with first-seen timestamp

Content hash algorithm:

- `content_hash` is SHA-256
- input bytes are canonical YAML frontmatter bytes plus raw Markdown body bytes
- no trailing-whitespace normalization is applied
- if YAML cannot be parsed, hash the original raw file bytes and quarantine as parse/schema invalid

Duplicate handling:

- same `id` and same content hash: treat as already processed; do not retrigger notifications or actions.
- same `id` and different content hash: quarantine the later file as `duplicate_id_hash_mismatch`, flag the original message, and create a safety finding.
- missing `id`: quarantine as schema-invalid before routing.
- no quarantined message can trigger notifications, adapter runs, approval consumption, or decision queue changes.

### Backpressure

Flood handling:

- max visible messages per thread defaults to 50
- beyond limit, collapse older messages
- if one producer writes more than 25 messages in 5 minutes, flag flood warning
- if malformed-message rate exceeds threshold, pause notifications for that participant and show safety finding

Backpressure thresholds are configuration defaults, not hardcoded constants. They live in local PAH config and default to:

```yaml
backpressure:
  max_visible_messages_per_thread: 50
  flood_message_count: 25
  flood_window_minutes: 5
```

## 13. Quarantine

Malformed messages must be atomically moved into:

```text
CODEX Claude Codex Mailbox\CODEX Quarantine
```

Each quarantine entry gets a sidecar:

```json
{
  "message_path": "...",
  "reason": "...",
  "detected_at": "2026-04-26T20:10:00-07:00",
  "parser_version": "pah-schema-v1"
}
```

No malformed message should poison every refresh forever.

Quarantine rules:

- write sidecar first as `.tmp`, then rename into place
- atomically move the malformed message out of the inbox
- leave a parser-ignored tombstone next to the original path, named `<original>.quarantined.json`
- never leave the malformed `.md` file in an active inbox
- preserve original file bytes and content hash
- quarantine reasons must use this closed enum:

```yaml
quarantine_reason_enum:
  - schema_invalid
  - missing_required_field
  - malformed_yaml_frontmatter
  - parse_error
  - duplicate_id_hash_mismatch
  - unknown_participant
  - unsafe_boundary
  - spoofing_attempt
  - flood_threshold_exceeded
```

Adding a new quarantine reason requires a schema version bump.

## 14. Notifications

Default provider:

- `log_only`

Notification tiers:

- tray status: always-on quiet signal
- desktop popup/toast: attention-needed while Darrin is at the computer
- SMS/phone: high-value interruption only after Darrin configures and approves provider use

Supported providers:

- Windows system tray badge/status
- Windows desktop popup/toast
- local notification log
- Twilio Programmable Messaging SMS
- email SMTP or provider API
- local desktop notification
- Claude Code native mobile push via Remote Control/Dispatch where applicable

Notification principles:

- no secrets in mailbox
- no old backlog blast on first enable
- cooldown per thread/event
- dedupe on restart
- quiet hours supported
- Darrin chooses interruption tolerance

Notification cycle protection:

- notification events are not routable messages
- notifications are written to a separate log: `C:\CODEX PG\CODEX Agent Hub\CODEX notifications\CODEX_notification_log.jsonl`
- notification events have no participant inbox side effects
- backpressure flags, flood warnings, and malformed-message rate alerts are log-only unless Darrin explicitly chooses popup/SMS for them
- failed notification provider calls are logged and surfaced on the Notify screen
- failed notifications do not retry by writing messages into the mailbox

Windows tray behavior:

- PAH should launch as a local standalone app with a Windows system tray icon
- left-click opens the dashboard
- right-click menu includes Open PAH, Pause popups, Pause SMS, Send test notification, View logs, and Quit
- closing the dashboard minimizes to tray by default
- quitting from tray stops PAH after confirmation
- auto-start on boot is disabled by default and requires Darrin approval
- tray icon state reflects healthy, attention-needed, paused, and error states

Desktop popup behavior:

- popup notifications are first-class v1 functionality
- popups appear for Darrin decision-needed, protected action approval, urgent message, agent disagreement/escalation, long-running task failure, and diagnostic failures
- popups do not appear for routine agent chatter, low-risk validation warnings, or old backlog
- every popup has a dedupe key and cooldown
- popup click opens the relevant PAH thread or decision

Recommended notification triggers:

- Darrin UX decision needed
- Darrin dental/product judgment needed
- protected action approval needed
- all agents disagree on a material decision
- urgent message
- long-running agent work failed
- stale high-priority thread

Not recommended for SMS:

- routine technical votes that agents can decide
- every mailbox message
- low-risk validation warnings
- historical backlog

## 15. UX Design

### 15.1 Design Mood

PAH should feel like a clinical development cockpit:

- dense but readable
- restrained
- local and trustworthy
- operational
- low prose
- no marketing feel
- no decorative hero layout

### 15.2 PG Design Bible Alignment

The mockup follows Panda Gallery visual grammar:

- dark chrome/canvas/pane hierarchy
- peach accent for active/primary emphasis
- green/warn/error semantic statuses
- Segoe UI for interface text
- Cascadia/Consolas mono for IDs, paths, timestamps, and precise values
- 4/8/12/16 spacing rhythm
- 4-6 px component radius
- section headers in accent, uppercase, 11 px, letter-spaced
- toolstrip, viewport, rightpane, statusbar structure
- one primary action per screen
- progressive disclosure through tabs and rightpane

### 15.3 Screens

#### Command Center

Purpose:

- first screen
- current state at a glance
- attention items
- agent lanes
- throughput
- active work table

Key elements:

- Attention now
- Agent lanes
- Throughput
- Current work
- rightpane governance state

#### Thread Board

Purpose:

- grouped conversation state
- owner/risk/status
- selected thread timeline

Key elements:

- thread cards
- latest timeline
- machine grouping
- owner and decision mode

#### Darrin Queue

Purpose:

- only questions Darrin should answer
- clear recommendation and alternative
- explicit UX/dental/safety framing

Key elements:

- decision cards
- recommended option
- agent-decided technical items separated from Darrin queue

#### Structured Dispatch

Purpose:

- compose structured outbound messages
- preflight schema, route, approval, and atomic write checks

Key elements:

- target participant
- message type
- approval boundary
- frontmatter/body preview
- preflight workflow stepper

#### Validation Console

Purpose:

- show schema/lint/safety findings from PAH's standalone validator
- render validator JSON without calling Panda Gallery tools
- surface hook and adapter risks

Key elements:

- schema pass/fail
- safety warnings
- lint source
- highest severity findings

#### Notification Settings

Purpose:

- configure phone/SMS/push policy
- keep Darrin in control of interruption tolerance

Key elements:

- provider state
- cooldown
- backlog suppression
- secrets ignored
- trigger toggles
- recent notification log

#### Communication Diagnostics

Purpose:

- confirm two-way communication between PAH and every configured AI participant
- identify route, validation, provenance, and timeout failures before real work depends on the lane

Key elements:

- Codex to PAH round trip
- Claude Desktop to PAH mailbox round trip
- Claude Code / CC to PAH file-bridge round trip
- agent-to-agent via PAH test paths where available
- route type labels: simulated, mailbox, MCP, headless, live adapter
- sent timestamp, received timestamp, message ID, `replies_to`, validation result, provenance check, timeout/failure reason

Rules:

- diagnostics default to simulated or mailbox-only tests
- diagnostics must not spend money, call live headless agents, send SMS, or use external APIs unless Darrin approves that specific diagnostic run
- failed diagnostics produce desktop popup by default, not SMS

### 15.4 Mockup Artifacts

Static UX mockup:

- `C:\CODEX PG\CODEX PANDA Agent Hub Final Design Package\CODEX_PAH_UX_MOCKUPS_v1.html`

Screenshot folder:

- `C:\CODEX PG\CODEX PANDA Agent Hub Final Design Package\CODEX mockup screenshots`

Expected screenshots:

- `CODEX_PAH_mockup_overview_1440x1000.png`
- `CODEX_PAH_mockup_threads_1440x1000.png`
- `CODEX_PAH_mockup_decisions_1440x1000.png`
- `CODEX_PAH_mockup_dispatch_1440x1000.png`
- `CODEX_PAH_mockup_validation_1440x1000.png`
- `CODEX_PAH_mockup_notifications_1440x1000.png`

## 16. Security Model

### 16.1 Localhost Write Security

Any future PAH write endpoint must require:

- per-run token
- Origin/Host check
- POST only
- JSON content type
- route allowlist
- CSRF-resistant nonce or token
- audit ledger entry

### 16.2 Provenance

Messages must record:

- actor
- route
- source UI/API
- created timestamp
- message hash
- target inbox
- validation state

Inbound spoofing is disabled outside simulation mode.

### 16.3 Protected Actions

Protected actions:

- write to `C:\panda-gallery`
- destructive filesystem operations
- git commit
- git push
- package install
- external API call
- SMS/email send
- live headless Claude Code/Codex run
- paid provider setup

Protected actions require explicit approval record.

### 16.3.1 Approval Record Schema

Protected actions are authorized only by a single-use approval record.

Required fields:

```yaml
approval_record:
  id: APPROVAL-20260426-210500-topic-slug
  requested_by: codex
  approved_by: darrin
  approved_at: 2026-04-26T21:05:00-07:00
  expires_at: 2026-04-27T21:05:00-07:00
  one_time_use: true
  status: approved
  approval_boundary: paid_api_requires_darrin
  target_agent: claude-code
  action_type: headless_review
  command_preview: "claude -p ... --tools \"Read,Grep,Glob,WebFetch\" ..."
  provider: anthropic_claude_code
  cwd: C:\CODEX PG
  worktree_path: C:\CODEX PG\.pah_worktrees\approval-20260426-210500
  settings_path: C:\CODEX PG\CODEX Agent Hub\CODEX config\CODEX_pah_headless_settings.json
  prompt_file: C:\CODEX PG\CODEX Agent Hub\CODEX prompts\APPROVAL-20260426-210500-topic-slug.txt
  prompt_hash: sha256:...
  allowed_tools:
    - Read
    - Grep
    - Glob
    - WebFetch
  disallowed_tools:
    - Edit
    - Write
    - Bash
    - NotebookEdit
  allowed_paths:
    - C:\CODEX PG
  denied_paths:
    - C:\panda-gallery
  budget_usd: 0.25
  request_hash: sha256:...
  command_hash: sha256:...
  approval_hash: sha256:...
  mcp_config_path: C:\CODEX PG\CODEX Agent Hub\CODEX config\CODEX_pah_mcp_readonly.json
  mcp_config_expected_hash: sha256:...
  process_timeout_seconds: 600
  consumed_at: null
  revoked_at: null
  revoke_reason: null
```

Rules:

- approval records expire; default maximum is 24 hours unless Darrin explicitly approves a shorter or longer window
- approval records are one-time-use by default
- action execution must bind to `request_hash` and `command_hash`; if the command changes, approval is invalid
- approvals must name exact paths or path roots, not broad prose
- approval records may only be created by an explicit Darrin `decision_record` generated by PAH UI and addressed to `pah`
- headless execution output may request follow-up approval through a `decision_request`, but it cannot create an approval record
- auto-synthesized `cross_check` resolutions cannot create approval records
- approval records can mark existing approvals as consumed or annotate threads, but cannot authorize a new protected action
- approval records may be revoked before consumption
- consumed or revoked approvals cannot be reused
- every protected-action ledger entry must reference the approval record ID and approval hash
- hash algorithm is SHA-256
- `request_hash` is SHA-256 of the canonical YAML frontmatter plus body of the decision request message
- `command_hash` is SHA-256 of the `command_preview` string verbatim
- `approval_hash` is SHA-256 of `request_hash + command_hash + approved_by + approved_at`
- after approval, only `consumed_at`, `revoked_at`, and `revoke_reason` may be modified
- any other edit invalidates the approval and PAH rejects execution if hashes fail to recompute and match

### 16.3.2 Headless Execution Contract

Live headless execution is disabled until Darrin approves a specific run.

Canonical Claude Code command contract:

```text
claude -p
  --input-format text
  --output-format json
  --permission-mode plan
  --tools "<approval.allowed_tools>"
  --allowedTools "<approval.allowed_tools>"
  --disallowedTools "<approval.disallowed_tools>"
  --strict-mcp-config
  --mcp-config "<approval.mcp_config_path>"
  --settings "<approval.settings_path>"
  --cwd "<approval.worktree_path>"
  --max-budget-usd "<approval.budget_usd>"
  --no-session-persistence
```

Prompt handling:

- PAH writes the prompt to a local prompt file under PAH app data
- PAH passes prompt bytes through stdin, not shell string interpolation
- PAH launches the process through argv/subprocess APIs, not through a shell command string
- prompt file path and prompt hash are stored in the approval record

Mandatory capture:

- stdout is captured to the audit ledger
- stderr is captured to the audit ledger
- exit code is captured to the audit ledger and approval record
- start time, end time, duration, process ID, command hash, prompt hash, approval hash, and worktree path are recorded
- `consumed_at` is set only after the process is launched

Timeout and cancellation:

- `process_timeout_seconds` defaults to 600
- PAH sends graceful termination when timeout expires
- PAH sends hard kill 30 seconds later if the process is still running
- cancellation records stdout/stderr captured so far
- cancellation cannot create follow-up approval records

MCP config enforcement:

- canonical read-only MCP config path is `C:\CODEX PG\CODEX Agent Hub\CODEX config\CODEX_pah_mcp_readonly.json`
- approval `mcp_config_path` must exactly match the canonical path, case-insensitive on Windows
- executor asserts the file exists before launch
- executor asserts SHA-256 of the MCP config matches `mcp_config_expected_hash`
- if the path or hash check fails, PAH refuses to launch
- updates to the canonical MCP config require Darrin re-approval before live use

Settings isolation:

- approval must name `settings_path`
- settings file must be PAH-owned and read-only for the run
- settings must not load user/project/local hooks, skills, plugins, or MCP servers unless explicitly approved
- any detected unapproved settings source blocks launch

### 16.4 Secrets

Secrets must live in ignored local config or environment variables.

Never put secrets in:

- mailbox files
- screenshots
- spec examples
- git-tracked templates except placeholder names

## 17. Data Model

Core entities:

- Participant
- Message
- Thread
- Decision
- RecommendationVote
- ValidationRun
- NotificationEvent
- ApprovalRecord
- AuditLedgerEntry
- QuarantineEntry
- CommunicationDiagnostic
- ModuleHealth
- TrayState

Thread computed state:

- owner
- status
- latest message
- risk
- priority
- waiting on
- Darrin needed
- validation state
- stale age

## 18. Audit Ledger

Every action gets a ledger entry:

```yaml
id: PAH-LEDGER-20260426-201000
event_type: message_routed
actor: codex
source: pah_ui
target: claude-code
message_id: CODEX-20260426-201000-topic-slug
created_at: 2026-04-26T20:10:00-07:00
approval_record: null
result: success
hash: sha256:...
```

Ledger must be append-only except for explicit compaction/export operations.

## 19. Implementation Roadmap After Approval

### Milestone 0: Design Approval

Deliverables:

- final spec
- integration research addendum
- UX mockup HTML
- screenshot set
- 6 C / Bible design review

### Milestone 1: Schema and Safety Foundation

Work:

- modular app skeleton and assembly interfaces
- participant registry
- schema v1 parser
- strict decision detection
- read-only status endpoint
- atomic write helper
- CSRF/token hardening
- no inbound spoofing
- separate Claude Code inbox
- durable documentation update checkpoint for every PAH behavior/protocol/safety change

Acceptance:

- viewing dashboard does not dirty files
- malformed messages cannot break refresh forever
- write routes require token
- Darrin queue is narrow and explicit
- `status` and `thread_status` enums are enforced
- PAH is router-only and direct `to: pah` messages are rejected in v1
- write-capable boundaries require explicit path roots
- PAH runs as standalone app code without Panda Gallery runtime dependencies
- each implemented behavior or incident fix updates the nearest durable PAH doc with what changed, what was learned, verification run, residual risk, and follow-up work

### Milestone 2: Validation and Inbox Reliability

Work:

- standalone PAH schema validator
- quarantine
- idempotency sidecars
- backpressure policy
- unread state
- status badges

Acceptance:

- core schema validation works when `C:\panda-gallery` is absent
- validation JSON renders from PAH's standalone validator
- restart does not resend notifications
- malformed messages move to quarantine
- duplicate message IDs with different hashes are quarantined as provenance conflicts
- active inboxes contain tombstones only, never malformed `.md` files

### Milestone 3: Notification UX

Work:

- notification settings UI
- log-only provider
- Windows tray launcher/status
- desktop popup/toast provider
- Twilio provider config template
- cooldowns
- baseline suppression
- test notification flow

Acceptance:

- no notification sent without configuration
- old backlog suppressed
- Darrin can decide SMS trigger categories
- tray icon opens dashboard and shows healthy/attention/error/paused state
- desktop popups work for decision/protected-action/escalation events
- notification events are log-only and cannot create mailbox loops

### Milestone 4: Communication Diagnostics

Work:

- Communication Diagnostics screen
- mailbox-based round-trip tests
- simulated route tests
- provenance and `replies_to` checks
- timeout/failure reporting
- live-adapter test gating

Acceptance:

- Codex to PAH round trip can be tested
- Claude Desktop to PAH mailbox route can be tested when available
- Claude Code / CC to PAH file-bridge route can be tested when available
- every diagnostic clearly labels simulated, mailbox, MCP, headless, or live adapter mode
- diagnostics cannot spend money, call live agents, send SMS, or use external APIs without Darrin approval
- Inspector distinguishes Agent Progress card presence from live CC tracking: `cc_active_dispatch` may warn when `active_dispatch.json` is absent, must pass valid sidecar schema and status checks when present, and must fail unsafe or missing target-path evidence.
- CC progress sidecar state list includes `ready_for_human_loop` for work that is complete enough to wait on Darrin's commit/go/ack word; this state requires durable mailbox evidence via `human_loop_evidence_path` and must not trigger stale-file or compose-cap alarms.

### Milestone 5: Agent Voting and Review Packets

Work:

- recommendation records
- vote capture
- cross_check workflow
- daily digest to Claude Desktop
- review packet export

Acceptance:

- technical decisions can be agent-decided
- Darrin sees UX/dental/safety/protected decisions only

### Milestone 6: Headless Read-Only Adapter Pilot

Work:

- approval record UI
- live run preview
- Claude Code read-only spec-review command
- output capture
- timeout and budget cap

Acceptance:

- first live call only after Darrin approves
- no write tools exposed
- report is captured as structured PAH message
- approval record is single-use and hash-bound to the exact command preview
- command uses restrictive `--tools`, strict MCP isolation, settings isolation, and a temporary worktree
- approval record cannot be created by agent output or auto-synthesized cross-checks

### Milestone 7: MCP/Hook Exploration

Work:

- PAH MCP server design
- Claude Desktop local MCP extension review
- Claude Code hook logging-only pilot
- kill switch

Acceptance:

- no hook blocks tools
- hooks are opt-in per session
- logging runs clean before any enforcement

## 20. Open Questions For Darrin

Only these need Darrin input before implementation:

1. Does the PAH visual direction feel like the right amount of density?
2. Which notification events are worth SMS/phone interruption?
3. Should the Darrin Queue use stronger wording around dental/product decisions?
4. Is `PANDA Agent Hub` the final name and `PAH` the acceptable short name?
5. Should closing the dashboard always minimize to tray, or should Quit be easier to reach?
6. Which popup notification severities should appear even when PAH is paused?

Technical defaults are agent-recommended and do not need Darrin to pick from architecture options unless he wants to.

## 21. Acceptance Criteria For v1 Build

PAH v1 build is acceptable when:

- PAH is a standalone app with no Panda Gallery runtime dependency
- modules are assembled through an app shell and can be tested independently
- dashboard refresh is read-only
- message writes are token-protected
- no route can spoof inbound agent provenance in production mode
- Claude Desktop and Claude Code are separate participants
- Darrin queue requires explicit metadata or protected-action policy
- schema v1 supports CC additions
- approval records are schema-defined, single-use, expiring, and hash-bound
- approval records cannot be generated by agent output, auto-synthesis, or chained headless runs
- write-capable boundaries require exact paths or explicit path roots
- PAH core validation works without `C:\panda-gallery`
- PAH v1 has no runtime dependency on `pg_dispatch_lint.py` or any Panda Gallery code
- malformed messages are quarantined
- processing is idempotent
- notification events cannot route into participant inboxes
- duplicate-ID content conflicts are quarantined
- `cross_check` auto-resolution has no undefined thread-risk dependency
- `validation.status: running` times out and cannot trigger actions past timeout
- write-scope path validation handles normalization, symlinks/junctions, case rules, and deny-overrides-allow
- quarantine reason codes are closed enum values
- content hashes and approval hashes use specified SHA-256 semantics
- Windows tray launch/status works
- desktop popup notifications work for configured attention-needed events
- Communication Diagnostics can verify supported two-way routes without live paid calls by default
- headless adapter pilot cannot run without strict tool/MCP/settings isolation
- notification system starts log-only and suppresses old backlog
- UX follows PG Design Bible visual grammar
- Darrin can understand current state within 60 seconds
- PAH docs stay current with implementation reality: every protocol, UI, monitor, safety, or operational behavior change updates the README, TODO, final spec, or successor spec before handoff

## 22. Research Sources

- `C:\CODEX PG\CODEX PANDA Agent Hub Final Design Package\CODEX_PAH_INTEGRATION_ACCESS_RESEARCH_v0_2.md`
- Claude Code CLI reference: https://code.claude.com/docs/en/cli-usage
- Claude Agent SDK overview: https://code.claude.com/docs/en/agent-sdk/overview
- Claude Code hooks reference: https://code.claude.com/docs/en/hooks
- Claude Code MCP: https://code.claude.com/docs/en/mcp
- Claude Code Desktop: https://code.claude.com/docs/en/desktop
- Claude Code Remote Control: https://code.claude.com/docs/en/remote-control
- OpenAI Codex non-interactive mode: https://developers.openai.com/codex/noninteractive
- OpenAI Codex SDK: https://developers.openai.com/codex/sdk
- OpenAI Codex MCP server guide: https://developers.openai.com/codex/guides/agents-sdk
- Twilio Programmable Messaging API: https://www.twilio.com/docs/sms/api
