# CODEX PAH Mediated Messaging Superseding Implementation Spec

Date: 2026-05-02
Author: Codex
Status: superseding implementation spec, not yet implemented
Scope: PANDA Agent Hub mediated messaging, Mail-first PAH state projection, authority reconciliation, hot endpoint performance, CD/Codex mailbox review flow

## Supersession Notice

This document supersedes:

- `C:\CODEX PG\CODEX Agent Hub\CODEX reports\CODEX_PAH_MEDIATED_MESSAGING_DEFINITIVE_FIX_SPEC_20260502.md`

It incorporates the deep review findings from:

- `C:\CODEX PG\CODEX Agent Hub\CODEX reports\CODEX_PAH_MEDIATED_MESSAGING_FIX_SPEC_DEEP_REVIEW_20260502.md`

The earlier report remains useful as incident evidence, but implementation should follow this superseding spec. If this document conflicts with the earlier report, this document wins.

This spec also preserves the active PAH rules in:

- `C:\CODEX PG\CODEX Agent Hub\CODEX_PAH_RELIABILITY_AND_DESIGN_SPEC.md`
- `C:\CODEX PG\CODEX Agent Hub\CODEX_PAH_MAIL_AND_INSPECTOR_UX_SPEC.md`
- `C:\CODEX PG\CODEX Agent Hub\CODEX_PAH_TODO.md`

## Non-Negotiable Decisions

These decisions were confirmed by Darrin on 2026-05-02 and are hard requirements.

1. A revised implementation spec is required before PAH code changes for this incident.
2. Darrin approval is the only authority that can move work into implementation-approved, commit-approved, backup-approved, publish-approved, or protected-write-approved states.
3. Claude Desktop readiness, Claude Code readiness, Codex readiness, mailbox phrasing, and PAH classifier results are advisory evidence. They are not Darrin approval.
4. PAH remains a dashboard and reconciler over mailbox files, ledgers, read state, archive state, and explicit approvals. PAH does not become the sole source-of-truth workflow engine in this fix.
5. PAH may add sanitized local snapshot and index files under `C:\CODEX PG\CODEX Agent Hub`, with `.gitignore` coverage when files are volatile or runtime-derived.
6. Snapshot files must not duplicate raw mailbox bodies by default.
7. `C:\panda-gallery` remains read-only unless Darrin explicitly authorizes a concrete fix there.
8. This spec does not authorize committing, pushing, deleting, reverting, archiving production mailbox files, or bypassing approval gates.

## Executive Summary

PAH mediated messaging is degraded because the human-visible mediation layer is slow, stale, and semantically ambiguous. The physical mailbox files are visible to PAH, and PAH has recorded ledger evidence for recent messages. That does not prove end-to-end Claude Desktop pickup, and it does not prove the PAH dashboard is presenting the correct action owner.

The definitive fix is not to make PAH more magical. The definitive fix is to make PAH more explicit:

- separate physical facts from derived state and approval authority;
- compute a sanitized, auditable snapshot of mediated mail state;
- use that snapshot to serve hot endpoints quickly;
- preserve Mail as the primary user surface;
- expose Inspector as the health and evidence surface;
- keep Advanced/cockpit available for deep operational detail;
- classify review, approval, read, archive, and supersedence states with precise precedence rules;
- prove delivery in levels instead of using a vague healthy/unhealthy flag;
- reconcile authority through previewed projections, not blind generated writes;
- retain compatibility routes while introducing fast snapshot-backed replacements;
- add rollback, shadow mode, profiling, and visual/browser verification.

The implementation should proceed in shadow mode first. PAH should build the new snapshot beside the legacy state path, compare them, report differences, and only switch hot endpoints after tests and live verification show the snapshot is accurate and faster.

## Incident Facts And Confidence Levels

### Proven

- PAH can scan the relevant mailbox directories.
- PAH smoke tests passed during the incident window.
- The offline inspector reported pass-heavy results with warning-only findings.
- PAH interaction ledger recorded discovery of the latest Codex-to-Claude RTC message.
- `/api/status` and `/api/cockpit` were slow on the live server, around 29 seconds in observed probes.
- `/api/health` is coupled to cockpit generation in current code through `health_payload_from_cockpit(cockpit_payload())`.
- `CODEX_ACTIVE_DISPATCH_INDEX.md` and `CODEX_CURRENT_AUTHORITY.md` were stale relative to recent mailbox traffic.
- The current classifier path can close completion evidence unless thread status is exactly ready/waiting review.
- Existing `MESSAGE_PARSE_CACHE` already caches parsed messages by path signature.
- Current mailroom canary uses temporary mailboxes but mutates module globals while PAH runs on `ThreadingHTTPServer`.

### Not Proven

- Claude Desktop actually saw and processed the latest Codex-to-Claude RTC.
- Claude Desktop prioritized the RTC as an action item.
- The visible PAH action queue represented the correct owner/state.
- A generated active index is safe to write without preview and approval.
- The 29-second endpoint cost comes from markdown parsing specifically. Profiling must identify the actual slow blocks.

### Operational Diagnosis

The physical file bridge is probably working at the PAH side. The mediated messaging product is not trustworthy yet because PAH conflates expensive state rebuilds, advisory mailbox evidence, stale authority files, and user-visible action ownership.

## Target Product Behavior

PAH should answer five questions quickly and defensibly.

1. What mail needs attention?
2. Who owns the next action?
3. What evidence supports that owner/state?
4. Is PAH's evidence fresh?
5. Has Darrin approved any protected action?

The first screen remains Mail-first. Inspector is the evidence and health surface. Advanced keeps legacy cockpit internals and deep diagnostics.

## Trust Model

PAH must maintain a strict trust boundary.

### Layer 1: Physical Facts

Physical facts are observed directly from disk or controlled local state.

Examples:

- message file path exists;
- content hash;
- mtime and size;
- parsed frontmatter fields;
- read-state entry;
- archive-state entry;
- interaction ledger event;
- route configuration;
- endpoint timing sample.

Physical facts are evidence, not authority.

### Layer 2: Derived State

Derived state is PAH's best computed interpretation of physical facts.

Examples:

- message belongs to thread X;
- message supersedes prior message Y;
- thread appears open on Claude Desktop;
- thread appears waiting on Darrin approval;
- delivery level is visible but not acknowledged;
- active index appears stale.

Derived state must carry provenance and confidence. It can guide the UI. It must not silently grant protected permissions.

### Layer 3: Authority Projection

Authority projection is the human-readable operational view PAH presents for coordination.

Examples:

- active dispatch index row;
- current authority row;
- ready-to-commit queue;
- approval-required banner.

Authority projection may be generated from derived state, but writes must be previewed and gated. Manual overrides and Darrin gates must survive regeneration.

### Layer 4: Darrin Authority

Darrin authority is explicit approval from Darrin for protected actions.

Protected actions include:

- implementation go when Darrin has not already authorized it;
- commit;
- push;
- backup;
- publish;
- destructive cleanup;
- production archive/delete;
- writing to `C:\panda-gallery`;
- overriding a Darrin approval boundary.

Claude Desktop, Claude Code, Codex, PAH, and mailbox files cannot independently create Darrin authority.

## Core Data Model

### Agent IDs

Canonical machine ids:

- `codex`
- `claude-desktop`
- `claude-code`
- `darrin`
- `system`
- `message`
- `unknown`

Compatibility aliases may be accepted at parse time:

- `cd`, `claude_desktop`, `claude desktop` -> `claude-desktop`
- `cc`, `claude_code`, `claude code` -> `claude-code`
- `CODEX`, `codex-agent` -> `codex`

Wire contracts should use canonical hyphenated ids. UI bucket names may use underscore keys only for backward compatibility, and must be documented as display/JS compatibility fields rather than canonical ids.

### Message Record

A snapshot message record contains sanitized metadata only.

Required fields:

```json
{
  "message_id": "string",
  "thread_id": "string",
  "path": "absolute path string",
  "file_name": "string",
  "content_hash": "sha256 string",
  "mtime": "iso timestamp",
  "size_bytes": 0,
  "from_agent": "canonical agent id",
  "to_agent": "canonical agent id",
  "status": "normalized status",
  "thread_status": "normalized thread status",
  "type": "normalized message type",
  "priority": "normalized priority",
  "reply_to": "message id or path",
  "supersedes": ["message ids or paths"],
  "approval_boundary": "string or empty",
  "requires_darrin_decision": false,
  "read_state": "read|unread|unknown",
  "archived": false,
  "title": "sanitized title",
  "summary": "sanitized summary, body-free or body-limited",
  "parse_warnings": []
}
```

Forbidden by default in persisted snapshots:

- raw body;
- full raw frontmatter block;
- long body excerpts;
- unbounded quoted mailbox content;
- secret/token-like values;
- generated instructions copied from mailbox body text.

Raw body remains in the source mailbox file and may be read on demand by a detail route.

### Thread Projection

A thread projection is a derived state object, not authority by itself.

Required fields:

```json
{
  "thread_id": "string",
  "state": "open_on_agent|waiting_review|waiting_darrin|closed|parked|superseded|owner_unknown|blocked|error",
  "current_owner": "canonical agent id",
  "current_action": "short action string",
  "review_owner": "canonical agent id or empty",
  "approval_owner": "darrin or empty",
  "approval_boundary": "ready_to_commit|write_to_panda_gallery|commit|push|backup|publish|none",
  "next_gate_after_review": "darrin_approval|agent_review|none",
  "delivery_level": "written|discovered|visible|read|acknowledged|unknown",
  "source_message": "absolute path",
  "latest_message": "absolute path",
  "active_messages": [],
  "superseded_messages": [],
  "archive_state": {},
  "provenance": [],
  "confidence": "high|medium|low",
  "warnings": []
}
```

For BA Applet v2 in the observed state, the correct projection is not simply closed. It is:

- current gate: Claude Desktop review of Codex RTC/conflict answer;
- current owner: `claude-desktop`;
- downstream gate: Darrin approval if CD accepts and commit/backup/publish is requested;
- Darrin approval: not granted by CD readiness.

### Delivery Levels

Delivery state is not boolean.

Levels:

1. `written`: a file exists in the routed inbox.
2. `discovered`: PAH observed the file and recorded or can derive a first-seen event.
3. `visible`: PAH snapshot exposes the item to the correct owner/filter.
4. `read`: PAH read state or an explicit recipient read receipt says the message was read.
5. `acknowledged`: recipient reply, ack, or resolution evidence exists.

Health should report the highest proven level for important messages. It must not claim end-to-end CD pickup unless the level is at least `read` or `acknowledged` by evidence from CD or a route canary explicitly testing that side.

## Classifier Rules

Classifier behavior must be metadata-first, deterministic, and explainable. Body text may produce a hint or warning, but body text must not become authoritative owner/state.

### Classifier Precedence

Apply these rules in order.

1. Parse validity and source trust. If the file cannot be parsed safely, classify as `owner_unknown` or `error` with warnings.
2. Supersedence. If a message is superseded by a newer valid message in the same thread, it cannot create active work by itself.
3. Explicit Darrin gate. `requires_darrin_decision`, `approval_boundary`, `ready_to_commit`, protected-write requests, commit/push/backup/publish requests, and equivalent explicit metadata create or preserve a Darrin gate unless newer Darrin approval/closure exists.
4. Explicit recipient review gate. Exact review-pending metadata creates or preserves a review gate on the recipient.
5. Explicit no-action informational share. No-action/no-reply/FYI coordination messages close as informational if they have no Darrin gate and no exact review gate.
6. Explicit close/ack/accepted/shipped evidence closes the relevant gate only if no higher-priority Darrin or review gate remains.
7. Explicit action owner. Open messages with a real `action_owner` or actionable recipient become open on that owner.
8. Unknown or contradictory metadata becomes `owner_unknown` with warnings.
9. Body text hints may add warnings such as `body_mentions_review_without_metadata`, but may not assign owner/state.

### Exact Review-Pending Statuses

The following statuses are review gates when addressed to or owned by a real recipient:

- `complete_pending_cd_review`
- `ready_for_cd_review`
- `waiting_cd_review`
- `complete_pending_review`
- `ready_for_review`
- `waiting_review`
- `ready_for_human_loop` when review owner is an agent

For `complete_pending_cd_review`:

- sender work may be complete;
- recipient review remains open;
- owner is `claude-desktop` unless explicit metadata says otherwise;
- state is `waiting_review` or `open_on_agent` depending on current UI compatibility;
- closure requires CD ack/reply or explicit Darrin override.

### Darrin Approval Statuses

The following statuses or boundaries create a Darrin gate:

- `ready_to_commit`
- `ready_for_commit`
- `ready_for_backup`
- `ready_for_publish`
- `ready_for_human_loop` when approval owner is Darrin
- `approval_boundary: ready_to_commit`
- `approval_boundary: write_to_panda_gallery`
- `requires_darrin_decision: true`
- any protected-write boundary explicitly recorded in frontmatter

A Darrin gate can coexist with an agent review gate as a downstream gate. Example: CD reviews an artifact first; if accepted, Darrin decides whether to commit or publish.

### Informational Closure

Explicit no-action coordination shares close as informational only when no higher-priority gate exists.

Examples:

- `no_action_required`
- `no_reply_required`
- `fyi`
- `coordination_only`
- frontmatter or known metadata saying the message is only awareness mail

### Completion And Ack Closure

Completion/ack evidence closes only the gate it is allowed to close.

Examples:

- A Codex RTC can close Codex implementation work while leaving CD review open.
- A CD `accepted` reply can close CD review while opening a Darrin commit gate if the dispatch had `approval_boundary: ready_to_commit`.
- A Darrin explicit approval can close the approval gate and allow implementation/commit action as specified.
- A generic `done` or `closed` message from an agent cannot approve protected operations.

### Required Classifier Explanations

Every non-closed thread projection should include a concise `why` field and a structured evidence list.

Example:

```json
{
  "why": "Latest Codex RTC has status complete_pending_cd_review and action_owner claude_desktop; no CD ack exists yet.",
  "evidence": [
    {"kind": "message", "path": "...073619_CODEX_to_CLAUDE...md", "field": "status", "value": "complete_pending_cd_review"},
    {"kind": "absence", "field": "cd_ack", "value": "not found"}
  ]
}
```

## Supersedence Rules

Supersedence must be explicit and graph-based.

Accepted fields:

- `supersedes`
- `supersedes_also`
- `replaces`
- `in_reply_to`
- `reply_to`
- same-thread newer dispatch metadata when explicitly marked final/latest

Rules:

1. Supersedence should normally apply only inside the same `thread_id`.
2. Cross-thread supersedence is allowed only with explicit frontmatter and should produce a warning.
3. A superseded message stays in history but cannot create an active row by itself.
4. If two non-superseded messages claim to be latest active work in the same thread, classify the thread as conflict/warn until resolved.
5. If a superseding message is malformed, the prior valid message may remain active with a warning.
6. If a superseding message is later accepted/closed, it does not resurrect older superseded messages unless a newer reopen message exists.
7. `reply_to` alone does not imply supersedence; it only links conversation chronology.

BA Applet v2 fixture expectation:

- earlier v2 request messages remain thread history;
- the `20260502_092000` CD-to-Codex final dispatch is the active source dispatch;
- Codex RTC back to CD is completion/review evidence;
- CD review response is required before the CD review gate closes.

## Read, Unread, Archive, And Action State

Read state is visibility state. It is not action closure.

Rules:

1. Marking a message read must not close a thread.
2. Marking a message unread must not reopen a closed thread by itself.
3. A read message can still be actionable until reply/ack/archive/approval/closure evidence exists.
4. If message content changes after being read, content-hash-aware read state should treat it as unread again.
5. Archive hides a message from default active views but does not delete it.
6. Archived thread activity can reopen if a newer non-archived actionable message appears.
7. Auto-archive must not move owner-unknown, active, Darrin-gated, review-pending, or protected-boundary messages.
8. Production archive/delete operations remain protected and require explicit approval when destructive or broad.

Thread archive fields:

```json
{
  "archived": false,
  "archived_at": "iso timestamp or empty",
  "archive_reason": "string",
  "reopened_by_new_activity": false,
  "archive_safe": false,
  "archive_blockers": []
}
```

## Snapshot Architecture

### Purpose

The snapshot layer exists to make PAH fast and auditable without making PAH the sole authority engine.

The snapshot should answer:

- what physical facts were observed;
- what PAH derives from them;
- what evidence supports each derived owner/state;
- what authority projection is proposed;
- how fresh the evidence is;
- what warnings or conflicts remain.

### Files

Allowed new local files under `C:\CODEX PG\CODEX Agent Hub\CODEX state`:

- `CODEX_pah_mail_state_snapshot.local.json`
- `CODEX_pah_mail_state_snapshot_shadow_diff.local.json`
- `CODEX_pah_mail_state_perf.local.jsonl`
- `CODEX_pah_mediated_message_canary.local.json`
- `CODEX_pah_authority_reconcile_preview.local.md`

These files should be git-ignored unless a fixture is intentionally committed. If `.gitignore` lacks coverage for these local artifacts, implementation must add precise ignore rules.

### Snapshot Contract

Required top-level fields:

```json
{
  "schema_version": 1,
  "generated_at": "iso timestamp",
  "duration_ms": 0,
  "builder_version": "string",
  "source_counts": {},
  "freshness": {},
  "delivery": {},
  "classifier": {},
  "authority": {},
  "mail": {},
  "threads": [],
  "messages": [],
  "warnings": [],
  "errors": []
}
```

The snapshot may include sanitized summaries. It must not persist raw mailbox body by default.

### Freshness Thresholds

Snapshot freshness states:

- `fresh`: age under 10 seconds.
- `warm`: age 10 to 30 seconds.
- `stale_warn`: age 30 to 60 seconds or one refresh failure.
- `stale_error`: age over 60 seconds, repeated refresh failures, or no last good snapshot after startup grace.
- `missing`: no snapshot exists.

Actions:

- Read-only UI may serve stale snapshots with clear warning labels.
- Protected writes and reconcile writes are disabled or confirmation-gated when snapshot is `stale_error` or `missing`.
- Direct file operations requested explicitly by Darrin may proceed with confirmation and logged provenance.

### Existing Cache Use

Do not create a duplicate markdown parse cache. The implementation must inspect and reuse existing `MESSAGE_PARSE_CACHE` behavior.

Required improvements:

- measure cache hits/misses;
- report cache metrics in perf/health;
- extend caching to derived snapshot/thread projection if profiling supports it;
- preserve existing parse-cache smoke tests;
- avoid global invalidation unless file signatures actually changed.

## Endpoint Plan

### Compatibility Principle

Existing PAH routes must keep working while the new snapshot path is introduced. Breaking `/api/status`, `/api/health`, `/api/cockpit`, `/api/send`, `/api/message-read-state`, or `/api/mark-all-read` without migration is not acceptable.

### Hot Endpoints

`/api/ping`

- static server liveness;
- no mailbox scan;
- target p95 under 100 ms warm.

`/api/ready`

- fast readiness summary;
- no full state rebuild;
- reports server readiness, snapshot availability, snapshot age, and degraded reason.

Example:

```json
{
  "ok": true,
  "server_ready": true,
  "snapshot_available": true,
  "snapshot_fresh_enough": true,
  "snapshot_age_seconds": 3.2,
  "degraded_reason": []
}
```

`/api/health`

- snapshot-backed component health;
- preserve existing component names;
- add `mediated_messaging` component rather than replacing current contract;
- no full state rebuild by default.

`/api/status`

- backward-compatible snapshot-backed status;
- preserve top-level keys needed by existing UI where feasible;
- include `source: snapshot` and freshness fields;
- must not be the default heavy debug path.

`/api/debug/status-full`

- explicit expensive legacy/full state rebuild;
- used for debugging and shadow comparison;
- clearly marked heavy;
- not called by default UI refresh.

`/api/cockpit`

- snapshot-backed payload for Advanced/cockpit;
- preserve `simple_mail` shape for Mail;
- include freshness and warnings;
- no raw bodies in list payload.

`/api/message`

- detail route for one message body and raw/debug view;
- body is read on demand from source file;
- should support sanitized/rendered body first and raw source only behind explicit UI control.

`/api/reconcile-authority`

- default mode is dry run / preview;
- writes require explicit action-time confirmation and existing write-token rules;
- output is a proposed diff with provenance, not blind replacement.

### Health Component Additions

Preserve existing health components and add:

```json
{
  "mediated_messaging": {
    "ok": false,
    "status": "warn",
    "snapshot_freshness": {},
    "physical_mailbox": {},
    "delivery_ledger": {},
    "classifier": {},
    "authority_index": {},
    "endpoint_latency": {},
    "mail_first_surface": {},
    "canary": {}
  }
}
```

Health must distinguish:

- file exists;
- PAH discovered it;
- PAH made it visible to the correct owner;
- recipient read/ack evidence exists;
- authority projection is fresh;
- endpoint latency is within budget.

## Concurrency And Process Safety

PAH runs with `ThreadingHTTPServer`. Background refresh, canary, route tests, and writes must be safe under concurrent requests.

### Required Refactor Before Background Refresh

State-building functions must accept an explicit context/config object for mailbox roots, ledger paths, read-state paths, and route settings. Canary must not mutate production module globals while other request threads can read them.

Minimum context object fields:

- mailbox roots;
- ledger paths;
- read-state path;
- archive-state path;
- snapshot output path;
- clock function;
- dry-run/write mode;
- route labels.

### Snapshot Refresh Locking

Rules:

1. Build snapshots copy-on-write.
2. Readers get the last complete snapshot immediately.
3. A refresh lock prevents concurrent builders from trampling each other.
4. Refresh failure preserves last good snapshot.
5. `last_refresh_error` is visible in health.
6. No request should see a half-written snapshot file.
7. Persist by writing to a temporary file and atomic replace where practical.

### Operation Registry

Before restart or protected writes, PAH needs an operation registry.

Fields:

```json
{
  "operation_id": "string",
  "endpoint": "string",
  "actor": "codex|darrin|system|unknown",
  "started_at": "iso timestamp",
  "target_paths": [],
  "kind": "read|write|refresh|canary|diagnostic|reconcile|archive|send",
  "safe_to_interrupt": false,
  "status": "running|finished|failed|timed_out"
}
```

Controlled restart must check this registry and block or warn if unsafe writes are active.

## Authority Reconciliation

### Principle

Mailbox messages propose active state. They do not overwrite authority.

### Reconcile Preview

A reconcile preview should show:

- current active-index row;
- derived snapshot row;
- proposed action: add/update/close/no-op/conflict;
- provenance paths;
- confidence;
- Darrin gate impact;
- manual override impact;
- exact file(s) that would be written;
- whether write requires Darrin approval.

### Reconcile Write Rules

1. Default reconcile is dry-run only.
2. Writes require explicit UI action or explicit Darrin instruction.
3. Darrin gates cannot be removed by agent messages.
4. Manual overrides are preserved unless Darrin explicitly clears them.
5. Generated sections should be clearly marked as generated.
6. Human-authored notes should remain outside generated blocks.
7. Reconcile writes must be idempotent.
8. Every reconcile write logs an interaction ledger event.

### Active Index Projection

The active dispatch index should become a projection of derived state plus preserved manual authority.

A row should include:

- thread id;
- state;
- current owner;
- current action;
- review owner;
- approval owner;
- approval boundary;
- next gate after review;
- source dispatch;
- latest evidence;
- delivery level;
- confidence;
- warnings.

For BA Applet v2, a correct projection should preserve both CD review and possible downstream Darrin approval.

## Mail-First UX Integration

The snapshot exists to support the product direction, not only the legacy cockpit.

### Mail Surface

Mail consumes snapshot-derived list state and on-demand message detail.

Requirements:

- Mail is the default user surface once stable.
- Message list rows show sender, recipient, title, summary, thread, age, unread, and needs-action state.
- Raw paths do not dominate normal rows.
- Reader shows subject, metadata strip, body, then collapsed details.
- YAML/frontmatter is not the first visible reading experience.
- Reply composer preserves selected thread and reply target.
- Send uses PAH mailbox routes and existing compatibility behavior.
- Mark read/unread remains a neutral state-aware toggle.
- Read/unread does not close action state.
- Drafts should be preserved per selected message before broader UX completion is claimed.

### Inspector Surface

Inspector consumes health and evidence from the snapshot and canary.

Requirements:

- top band shows PASS/WARN/FAIL/UNKNOWN, freshness, pass/warn/fail counts;
- mediated messaging component shows file bridge, delivery level, classifier, authority, latency, canary;
- warnings must be actionable and evidence-backed;
- raw report is available but secondary;
- stale green evidence is not allowed.

### Advanced Surface

Advanced keeps the cockpit and operational detail.

Requirements:

- legacy action queue remains available;
- diagnostics and route tests move off hot refresh path;
- heavy debug state is explicit;
- copyable concise status for CD/CC should be available.

## Performance And Measurement

### Required Profiling Before Major Refactor

Phase 0 must instrument current `state()` and related builders before architecture switch-over.

Measure at least:

- `load_messages` duration;
- message parse cache hits/misses;
- read-state load duration;
- archive-state load duration;
- decision queue build duration;
- thread build duration;
- thread focus build duration;
- diagnostics duration;
- route-test duration;
- work-board duration;
- approval/adapters/quarantine/watcher durations;
- JSON serialization size and duration;
- response byte size;
- endpoint p50/p95 over repeated samples.

Profiling output should go to a local JSONL file under `CODEX state` and a concise report under `CODEX reports`.

### Latency Budget Method

Use warm local HTTP samples unless the test explicitly says cold start.

Recommended measurement:

- 20 warm samples per endpoint after one warm-up call;
- report p50, p95, max, and failure count;
- record mailbox message count and snapshot age;
- record process start time and Python version;
- keep cold startup budget separate from warm endpoint budget.

Targets:

- `/api/ping`: p95 under 100 ms warm.
- `/api/ready`: p95 under 150 ms warm.
- `/api/health`: p95 under 300 ms when snapshot age under 10 seconds.
- `/api/message-read-state`: p95 under 250 ms.
- `/api/cockpit`: p95 under 1000 ms with current real mailbox size.
- Mail filter/search for 500 messages: p95 under 100 ms after snapshot loaded.
- Message detail fetch: p95 under 500 ms for normal markdown files.
- Full debug state may exceed these budgets only on explicit debug routes.

The prior observed 29-second status/cockpit responses are failures under this spec.

### Response Size Budgets

Hot list payloads must avoid unbounded bodies.

Rules:

- default Mail list returns metadata and summaries only;
- raw body is loaded through detail route;
- message list should support limit/offset or cursor if list grows;
- cockpit payload should have a documented max default item count;
- heavy full-thread timelines can be lazy-loaded;
- health payload should be compact and component-oriented.

## Canary Requirements

### Existing Canary

`run_mailroom_transaction_canary()` already exists and should not be duplicated blindly. It should be refactored or extended.

Current issue: it mutates module globals while the server is threaded. That must be fixed before adding background refresh or production-facing canary confidence.

### New Mediated Message State Canary

Name: `mediated_message_state_canary`.

Required properties:

- uses injected temporary mailbox context;
- never writes production inboxes;
- never mutates production globals visible to concurrent requests;
- fails closed if isolation cannot be proven;
- writes a local canary result file;
- exposes exact failing stage.

Stages:

1. Create temporary routed inboxes.
2. Write Codex -> Claude Desktop test message.
3. Build snapshot from temporary context.
4. Confirm delivery level `visible` for Claude Desktop.
5. Mark message read in temporary read state.
6. Write Claude Desktop ack/reply in temporary context.
7. Confirm delivery level `acknowledged`.
8. Write Codex RTC with review-pending metadata.
9. Confirm review-pending state remains open on recipient until ack.
10. Confirm ledger events exist in temporary ledger.
11. Confirm archive/read rules do not close action state incorrectly.
12. Clean up temporary context.

Acceptance target: under 2 seconds warm on local machine, with exact failure reason if slower or failed.

## Rollback And Shadow Mode

Snapshot-backed state must be introduced in shadow mode before UI switch-over.

### Shadow Mode

In shadow mode PAH computes:

- legacy state from current `state()` path;
- new snapshot state;
- diff by thread id, owner, state, delivery level, read state, archive state, and active index projection.

Diff output:

- `CODEX_pah_mail_state_snapshot_shadow_diff.local.json`
- concise human-readable summary in Inspector or Advanced.

### Feature Flags

Add configuration to choose:

- legacy hot endpoints;
- snapshot hot endpoints;
- shadow compare;
- debug full state enabled/disabled.

The flag can be environment/config based if that matches current PAH style. The important requirement is that Darrin/Codex can return to the legacy path without reverting code if snapshot state misclassifies mail.

### Rollback Criteria

Revert hot endpoint usage to legacy path if:

- snapshot hides active Darrin-gated work;
- snapshot assigns protected approval without Darrin authority;
- snapshot loses messages visible in legacy state;
- Mail cannot load current inbox;
- Inspector cannot explain warnings;
- p95 endpoint latency regresses beyond current accepted baseline after switch-over.

## Implementation Phases

### Phase 0: Measurement And Stabilization

Purpose: stop guessing and make the current failure measurable.

Tasks:

1. Add timing instrumentation around current hot state builders.
2. Measure warm endpoint p50/p95/max for `/api/ping`, `/api/ready` if present, `/api/health`, `/api/status`, `/api/cockpit`, and `/api/message-read-state`.
3. Record message count, thread count, response size, cache hits/misses, and slow subsystem durations.
4. Update server smoke readiness to use `/api/ping`; keep status/cockpit latency as separate performance assertions.
5. Add or expose a visible stale-authority warning if active index/current authority trails current mailbox evidence.
6. Produce a reconcile dry-run for BA Applet v2 without writing authority files unless explicitly approved.

Acceptance:

- baseline perf report exists;
- slow subsystem is identified rather than assumed;
- server readiness is no longer blocked solely on heavy status;
- no production mailbox files are moved/deleted;
- Darrin gates remain intact.

### Phase 1: Trust-Safe Snapshot Shadow Mode

Purpose: build the new model beside the existing one.

Tasks:

1. Add explicit context/config object for mailbox state building.
2. Build sanitized snapshot from physical facts and derived classifier state.
3. Persist local snapshot under ignored `CODEX state` path.
4. Add freshness/staleness fields.
5. Add delivery levels.
6. Add provenance and confidence to thread projections.
7. Add shadow diff comparing legacy and snapshot results.
8. Reuse existing `MESSAGE_PARSE_CACHE` and report metrics.

Acceptance:

- snapshot builds without raw bodies;
- snapshot includes current BA Applet v2 thread;
- shadow diff explains any owner/state differences;
- no hot endpoint depends on snapshot yet unless explicitly flagged;
- snapshot files are local/ignored or explicitly documented.

### Phase 2: Classifier And Gate Semantics

Purpose: fix the state machine before switching user-visible routes.

Tasks:

1. Implement metadata-first classifier precedence.
2. Add exact review-pending statuses.
3. Add exact Darrin approval statuses and boundaries.
4. Add dual-gate representation: current review gate plus downstream Darrin gate.
5. Add read-state vs action-state tests.
6. Add archive-state tests.
7. Add supersedence graph tests using BA Applet v2 fixture filenames.
8. Consolidate duplicate `normalize_agent_id` definitions into one tested normalization path.

Acceptance:

- `complete_pending_cd_review` remains open on CD until ack;
- `ready_to_commit` remains Darrin-gated until Darrin approval;
- no-action coordination messages close informationally;
- read does not close action;
- superseded messages do not create active clutter;
- owner normalization is deterministic.

### Phase 3: Health And Mail-First Integration

Purpose: make the user-facing surfaces consume the safer state.

Tasks:

1. Add `/api/ready` if missing.
2. Make `/api/health` fast and snapshot-backed while preserving current component names.
3. Add `mediated_messaging` health subcomponent.
4. Feed Mail list from snapshot metadata.
5. Keep message body detail on demand.
6. Add freshness warning in Mail when snapshot is stale.
7. Add Inspector rows for delivery level, classifier, authority, latency, canary, and stale snapshot.
8. Keep Advanced/cockpit available.

Acceptance:

- Mail opens quickly from snapshot state;
- Inspector explains mediated messaging health;
- `/api/health` does not call full cockpit by default;
- existing compatibility routes still work;
- stale evidence cannot look green.

### Phase 4: Authority Reconciliation

Purpose: make active index/current authority projections auditable and safe.

Tasks:

1. Add dry-run reconcile preview endpoint/action.
2. Project active dispatch rows from snapshot plus preserved manual authority.
3. Include Darrin gates and downstream gates.
4. Preserve manual overrides.
5. Require explicit confirmation/write token for writes.
6. Log reconciliation events.
7. Update Relay Health to compare derived active thread set to projected rows, not only mtime/text.

Acceptance:

- BA Applet v2 dry-run shows CD review gate and downstream Darrin gate;
- no reconcile write occurs without explicit approval/action;
- drift detection compares thread/state/owner/gate fields;
- reconcile is idempotent.

### Phase 5: Performance Switch-Over

Purpose: move hot endpoints to snapshot-backed responses after proving correctness.

Tasks:

1. Switch `/api/status` to snapshot-backed compatibility payload.
2. Switch `/api/cockpit` to snapshot-backed Advanced payload.
3. Keep `/api/debug/status-full` for full legacy rebuild.
4. Add endpoint latency tests to server smoke.
5. Add response size checks.
6. Keep rollback flag available.

Acceptance:

- `/api/status` and `/api/cockpit` no longer block for 10+ seconds on current mailbox size;
- warm p95 targets pass;
- rollback flag works;
- legacy debug endpoint remains available for diagnostics.

### Phase 6: Canary, Visual QA, And Durable Docs

Purpose: prove the behavior end to end and leave maintainable records.

Tasks:

1. Refactor existing canary isolation away from global mutation.
2. Add mediated message state canary.
3. Add Run Canary action in Inspector/Advanced where appropriate.
4. Add copyable concise status for CD/CC.
5. Run smoke tests, inspector, server smoke, and py_compile.
6. Verify live browser Mail, Inspector, and Advanced surfaces.
7. Capture screenshots for meaningful visual changes.
8. Update README, TODO, reliability spec, Mail/Inspector UX spec, and incident/spec manifest.

Acceptance:

- canary passes in isolated temp context;
- visual/browser QA confirms no obvious overlap, font regression, or pale alert panels;
- documentation is updated;
- PAH can explain mediated messaging status without terminal spelunking.

## Required Tests

### Unit Tests

- agent id normalization aliases;
- frontmatter parse for exact review-pending statuses;
- Darrin approval boundary parse;
- metadata-first classifier precedence;
- no-action informational closure;
- completion with downstream review gate;
- completion with downstream Darrin gate;
- read-state does not close action;
- archive-state does not erase active gate;
- content-hash-aware read invalidation;
- supersedence graph construction;
- active index projection;
- snapshot sanitization excludes raw body;
- snapshot freshness thresholds;
- operation registry behavior.

### Integration Tests

- temp mailbox Codex -> CD -> Codex ack flow;
- temp mailbox CD -> Codex dispatch and Codex RTC pending CD review;
- temp mailbox ready-to-commit gate waiting on Darrin;
- current real mailbox read-only snapshot build;
- shadow diff generation;
- Relay Health drift comparison by thread/state/gate;
- `/api/health` fast component response;
- `/api/status` compatibility payload;
- `/api/cockpit` snapshot payload;
- `/api/debug/status-full` explicit heavy path;
- canary isolation under threaded request simulation if practical.

### Smoke And Manual Tests

Commands:

```powershell
python -m py_compile "C:\CODEX PG\CODEX Agent Hub\CODEX_agent_hub.py"
python "C:\CODEX PG\CODEX Agent Hub\CODEX_run_smoke_tests.py"
python "C:\CODEX PG\CODEX Agent Hub\CODEX_pah_inspector.py" --offline --json
& "C:\CODEX PG\CODEX Agent Hub\CODEX_run_server_smoke.ps1"
```

Live checks:

- `http://127.0.0.1:8765/` loads.
- Mail list is populated.
- Needs Me/CD/CC filters reflect snapshot state.
- Selected message body loads through detail route.
- Read/unread toggle works without closing action state.
- Reply compose preserves thread/reply fields.
- Inspector shows mediated messaging component.
- Advanced/cockpit remains available.
- Health does not appear green when snapshot, authority, or delivery evidence is stale.
- Screenshots are captured if UI changed.

## Definitive Acceptance Criteria

The fix is accepted only when all of these are true.

1. The implementation follows this superseding spec rather than the earlier draft.
2. Physical file discovery, PAH discovery, PAH visibility, read, and ack are reported as separate delivery levels.
3. CD pickup is not claimed unless CD read/ack evidence or an equivalent route canary proves it.
4. Darrin approval is the only source of protected-action authority.
5. PAH remains a reconciler with auditable state projections.
6. Snapshot files are sanitized, local, and ignored when volatile.
7. No raw mailbox bodies are persisted in snapshot files by default.
8. Existing `MESSAGE_PARSE_CACHE` is reused or consciously extended, not duplicated.
9. Background refresh and canary do not mutate production globals under threaded requests.
10. `/api/health` preserves existing component compatibility and adds mediated messaging details.
11. `/api/status` remains compatible but becomes snapshot-backed for default use.
12. Heavy full-state rebuild is available only through explicit debug route/action.
13. BA Applet v2 style RTC messages with `complete_pending_cd_review` remain open on CD until ack.
14. Ready-to-commit or protected-write states remain Darrin-gated until Darrin approval.
15. Read/unread state does not close action state.
16. Superseded messages remain visible in history but do not create active queue clutter.
17. Active index reconciliation is preview-first and idempotent.
18. Warm endpoint p95 latency targets pass or documented exceptions are approved.
19. Server smoke uses fast readiness and separately reports performance failures.
20. Mail-first UI remains aligned with the PAH Mail/Inspector UX spec.
21. Inspector exposes stale evidence and mediated messaging warnings clearly.
22. Live browser verification is performed for meaningful UI changes.
23. `C:\panda-gallery` is not written unless Darrin explicitly authorizes a concrete fix.
24. No commit/push/backup/publish occurs without explicit Darrin approval.
25. Durable docs are updated before handoff.

## Files Likely In Scope

Primary implementation files:

- `C:\CODEX PG\CODEX Agent Hub\CODEX_agent_hub.py`
- `C:\CODEX PG\CODEX Agent Hub\CODEX_run_smoke_tests.py`
- `C:\CODEX PG\CODEX Agent Hub\CODEX_run_server_smoke.ps1`
- `C:\CODEX PG\CODEX Automation\CODEX_relay_health_check.ps1`

Possible new support module if the existing codebase shape permits it:

- `C:\CODEX PG\CODEX Agent Hub\CODEX_pah_mediated_state.py`

State/cache files:

- `C:\CODEX PG\CODEX Agent Hub\CODEX state\CODEX_pah_mail_state_snapshot.local.json`
- `C:\CODEX PG\CODEX Agent Hub\CODEX state\CODEX_pah_mail_state_snapshot_shadow_diff.local.json`
- `C:\CODEX PG\CODEX Agent Hub\CODEX state\CODEX_pah_mail_state_perf.local.jsonl`
- `C:\CODEX PG\CODEX Agent Hub\CODEX state\CODEX_pah_mediated_message_canary.local.json`
- `C:\CODEX PG\CODEX Agent Hub\CODEX state\CODEX_pah_authority_reconcile_preview.local.md`

Authority/human projection files:

- `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX_ACTIVE_DISPATCH_INDEX.md`
- `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX_CURRENT_AUTHORITY.md`

Docs to update after implementation:

- `C:\CODEX PG\CODEX Agent Hub\CODEX_README.md`
- `C:\CODEX PG\CODEX Agent Hub\CODEX_PAH_RELIABILITY_AND_DESIGN_SPEC.md`
- `C:\CODEX PG\CODEX Agent Hub\CODEX_PAH_MAIL_AND_INSPECTOR_UX_SPEC.md`
- `C:\CODEX PG\CODEX Agent Hub\CODEX_PAH_TODO.md`
- `C:\CODEX PG\CODEX Agent Hub\CODEX reports\CODEX_PAH_INCIDENT_20260502_MANIFEST.md`

## Non-Goals

This spec does not authorize:

- replacing the mailbox protocol with an external service;
- making PAH the sole workflow authority engine;
- granting protected action authority from agent-authored messages;
- persisting raw mailbox bodies into snapshots by default;
- deleting production mail;
- moving production mail to archive without explicit approved logic;
- writing into `C:\panda-gallery`;
- hiding warnings to make PAH look healthy;
- removing compatibility routes before migration;
- committing or pushing changes.

## Implementation Warnings

1. Do not start by rewriting the whole server. Measure first.
2. Do not add a second parse cache without proving the existing cache is insufficient.
3. Do not let body text decide authority.
4. Do not turn CD readiness into Darrin approval.
5. Do not let read state close active work.
6. Do not let a generated active index overwrite manual authority notes.
7. Do not run canary logic against production globals in a threaded server.
8. Do not use `/api/status` as startup readiness if it can call expensive state.
9. Do not claim CD pickup from PAH-side discovery alone.
10. Do not treat a restart as the fix. Restart is only mitigation.

## Open Assumptions

These are not blockers for the spec, but implementation should keep them visible.

1. Actual Claude Desktop pickup may require a real CD acknowledgement outside automated PAH tests.
2. The best module boundary depends on how much risk is acceptable in splitting `CODEX_agent_hub.py`.
3. Existing UI consumers of `/api/status` and `/api/cockpit` must be checked before changing payload details.
4. Windows/OneDrive filesystem watching may be unreliable; polling by directory signature is the default safe plan.
5. If Darrin wants PAH to become a stronger workflow engine later, that should be a separate design phase after the reconciler proves reliable.

## Final Implementation Directive

The optimal fix is a trust-safe, snapshot-backed reconciler with explicit authority boundaries. It should be implemented in measured phases: profile, shadow, fix classifier gates, integrate Mail/Inspector health, preview authority reconciliation, then switch hot endpoints with rollback.

The success condition is not that PAH looks green. The success condition is that PAH can quickly and accurately explain what mail exists, who needs to act, what evidence proves it, and whether Darrin has approved the protected next step.
