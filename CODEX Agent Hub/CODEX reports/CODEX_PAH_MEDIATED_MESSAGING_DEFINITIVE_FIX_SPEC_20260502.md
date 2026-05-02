# CODEX PAH Mediated Messaging Incident Report And Definitive Fix Spec

Date: 2026-05-02
Author: Codex
Scope: PANDA Agent Hub mediated messaging, mailbox bridge, active dispatch authority, live dashboard/status endpoints
Status: report/spec, not yet implemented

## 1. Executive Summary

PAH mediated messaging is partially working, but it is not operationally trustworthy in its current state.

The physical mailbox bridge is working: files are being written, discovered, ledgered, and classified. The latest Codex-to-Claude RTC message was detected by PAH in the interaction ledger. However, the live PAH dashboard mediation layer is stale and slow enough that Claude Desktop can reasonably appear to be missing, delayed, or confused by messages.

The immediate incident is not primarily a file-write failure. It is a state-and-classification failure plus a performance failure:

- PAH physical mail scan sees messages.
- PAH interaction ledger records recent traffic.
- PAH routes and core UI wiring pass offline checks.
- But live `/api/status` and `/api/cockpit` take about 29.5 seconds.
- Relay Health reports `0 active_rows` even though there is a current active BA Applet v2 dispatch.
- `CODEX_ACTIVE_DISPATCH_INDEX.md` and `CODEX_CURRENT_AUTHORITY.md` are stale.
- PAH classification/queue state is out of sync with current work.
- The latest Codex-to-Claude RTC was discovered, but the classifier marked it as `closed` with owner `message`, meaning PAH may not present it as an open Claude Desktop action even though the file exists.

Definitive fix: PAH needs a dedicated mediated-mail state service and snapshot layer. The live dashboard must consume a fast, precomputed, self-validating message state snapshot. Slow scans, diagnostics, relay-health checks, active-index reconciliation, and classifier recomputation must run asynchronously or on explicit refresh, with stale-but-labeled cached data served immediately. The hand-maintained active dispatch index should become a rendered/exported artifact from canonical state, not the source of truth that can silently drift.

## 2. Evidence From Current Tests

Commands run on 2026-05-02:

- `python C:\CODEX PG\CODEX Agent Hub\CODEX_run_smoke_tests.py`
- `C:\CODEX PG\CODEX Automation\CODEX_relay_health_check.ps1 -Json -NoFail`
- `python C:\CODEX PG\CODEX Agent Hub\CODEX_pah_inspector.py --offline --json`
- Live localhost probes against `http://127.0.0.1:8765`
- Recent interaction ledger tail inspection
- Active dispatch index and current authority snapshot inspection

### 2.1 Passed Signals

- PAH smoke tests passed.
- Offline PAH inspector summary: `23 pass`, `1 warn`, `0 fail`.
- Physical mailbox scan passed: 385 markdown files represented in PAH scan.
- Required dashboard controls and GET/POST routes are present.
- Interaction ledger exists, is valid JSONL, and includes recent `message_discovered` and classifier events.
- File bridge routes are configured:
  - Codex to Claude Desktop: `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox`
  - Claude Desktop to Codex: `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox`
  - Claude Desktop to Claude Code: `C:\panda-gallery\workflows\cc_mailbox\CC Inbox`
  - Claude Code to Claude Desktop: `C:\panda-gallery\workflows\cc_mailbox\CLAUDE Inbox`

### 2.2 Failed Or Degraded Signals

Live PAH on `127.0.0.1:8765`:

- Root page `/`: about `0.03s`.
- `/api/message-read-state`: about `0.05s`.
- `/api/status`: about `29.66s`.
- `/api/cockpit`: about `29.47s`.
- `/api/health`: timed out at 5 seconds during the first probe.
- `CODEX_run_server_smoke.ps1`: failed because `/api/status` exceeded its 10 second timeout.

Relay Health:

- Overall: `warn`.
- `active_rows`: `0`.
- `unindexed_recent_codex_mail`: `1`.
- `recent_unread_incoming`: `1`.
- New unindexed mail: `20260502_092000_CLAUDE_to_CODEX_ba_applet_v2_final.md`.

State files:

- `CODEX_ACTIVE_DISPATCH_INDEX.md` last updated: 2026-05-01 23:12 PT.
- `CODEX_CURRENT_AUTHORITY.md` last updated: 2026-04-28 19:16 PT.
- Active index says no Codex-owned active dispatch rows, which is false for the current BA Applet v2 work.

Process:

- Live PAH process on port `8765`: `python`, PID `48976`, started 2026-05-02 06:57.
- Process is responding but has high CPU time and slow expensive endpoints.

Ledger evidence:

- Latest Codex-to-Claude message was discovered:
  - `20260502_073619_CODEX_to_CLAUDE_ba_applet_v2_rtc_and_conflict_question.md`
  - event type: `message_discovered`
  - direction: `Codex -> Claude`
  - thread: `BA-APPLET-V2-ENHANCEMENTS`
- Classifier then produced:
  - owner: `message`
  - state: `closed`
  - previous_owner: `codex`
  - previous_state: `open_on_agent`

That classification may be correct for a completed Codex RTC in some views, but it is not sufficient for CD-mediated review. CD needs a visible incoming item or review-required state for `complete_pending_cd_review`.

## 3. Expected Behavior

PAH mediated messaging should provide these guarantees:

1. If a message file exists in a routed inbox, PAH sees it within a bounded time.
2. If PAH sees a message, it records a ledger event exactly once per content version.
3. If a message requires an agent review, PAH shows it as open on the correct agent.
4. If a message is complete/report/RTC but still asks the receiving agent to confirm, PAH must not bury it as merely closed.
5. The visible dashboard/cockpit should refresh quickly enough to feel live.
6. Health must distinguish:
   - file bridge healthy
   - classifier healthy
   - authority/index healthy
   - endpoint performance healthy
   - delivery confirmation healthy
7. A stale active-index or authority file should not be able to hide a real current dispatch.
8. `/api/health` should never block behind a full expensive state rebuild.

Performance targets:

- `/api/ping`: under 50 ms.
- `/api/health`: under 250 ms, always serves cached/stale status if expensive checks are running.
- `/api/message-read-state`: under 250 ms.
- `/api/cockpit`: under 500 ms normal, under 1000 ms worst-case with 500+ messages.
- `/api/status`: under 1000 ms normal, with explicit `freshness` and `expensive_refresh_state` fields.
- Full rescan/diagnostics may exceed 1 second only on explicit refresh endpoints or background jobs, never on the default dashboard refresh path.

## 4. Root Cause Analysis

### 4.1 Synchronous Full-State Rebuild On Hot Endpoints

Current route behavior in `CODEX_agent_hub.py`:

- `/api/cockpit` calls `cockpit_payload()`.
- `cockpit_payload()` calls `state()`.
- `/api/status` calls `state()` directly.
- `/api/health` appears to rely on the same heavy cockpit/status path.

Current `state()` does all of this synchronously:

- `load_messages()` across all mailbox surfaces.
- `load_read_state()`.
- `load_thread_archive_state()`.
- `build_decision_queue()` twice.
- `urgent_codex_request_rows()`.
- `build_agent_progress_monitor()`.
- `validate_mailbox()`.
- `build_threads()`.
- `build_thread_focus()`.
- `audit_messages_and_thread_states()`.
- `cached_communication_diagnostics()`.
- `route_test_status(refresh=True)`.
- `work_board_status()`.
- `approval_status()`.
- `adapter_status()`.
- `quarantine_status()`.
- `decision_state_summary()`.
- `build_agent_status()`.
- `build_watcher_status()`.
- large response assembly.

This makes the dashboard path dependent on every slow subsystem. The 5-second expensive-status cache helps only after a completed build; it does not help when the build itself takes about 30 seconds. It also does not provide stale-while-refresh behavior.

### 4.2 Hand-Maintained Active Index Drift

Relay Health treats `CODEX_ACTIVE_DISPATCH_INDEX.md` and `CODEX_CURRENT_AUTHORITY.md` as compact authority. That is useful for humans, but current behavior allows these files to drift behind real mailbox traffic.

Observed drift:

- Active index says no active rows.
- Current CODEX Inbox contains active dispatch `20260502_092000_CLAUDE_to_CODEX_ba_applet_v2_final.md`.
- Relay Health correctly warns that newer CODEX Inbox mail is not reflected in active index or authority.

The active index should not be a manually-maintained source of truth for live PAH routing. It should be generated from canonical message state, or at minimum reconciled automatically before PAH claims health.

### 4.3 Classifier Misfit For Review-Pending RTC Messages

The latest Codex-to-Claude RTC has:

- type: `rtc`
- status: `complete_pending_cd_review`
- thread_status: `active`
- action_owner: `claude_desktop`

PAH discovered it, but classifier state became `closed` with owner `message`. That can hide or downgrade an item that CD should review.

Rule gap: completion evidence can close the sender side of a task, but if the completion evidence is addressed to an agent and asks for review/confirmation, it must create or preserve an open-on-recipient review state.

### 4.4 Health Model Is Too Aggregate

Current diagnostics can say routes pass while the operator-visible dashboard is effectively unusable due to 30 second endpoint latency. Health needs component separation:

- route existence
- physical file bridge
- delivery ledger
- classifier correctness
- active authority freshness
- endpoint latency
- dashboard render freshness

A single `diagnostics.ok` or `warn` does not sufficiently explain mediated messaging failure.

### 4.5 Server Smoke Test Uses A Slow Endpoint As Startup Proof

`CODEX_run_server_smoke.ps1` starts PAH and then waits for `/api/status`. Because `/api/status` is heavy, the smoke test fails even if the server starts and simple routes work.

Startup readiness should use `/api/ping` or a fast `/api/ready` endpoint. Full status should be a separate performance/health test.

## 5. Definitive Fix: Target Architecture

### 5.1 Introduce PAH Mediated Mail State Service

Add a small internal service layer, conceptually `pah_core.mediated_mail_state`, responsible for producing a canonical message-state snapshot.

Inputs:

- physical inbox files
- frontmatter metadata
- read state
- archive state
- interaction ledger sidecars
- active dispatch rows when present
- current authority snapshot when present

Outputs:

- `mail_state_snapshot.local.json`
- `mail_state_snapshot.latest.md` for human review
- in-memory snapshot object
- generated active dispatch index view
- health component metrics

The snapshot must include:

- `generated_at`
- `duration_ms`
- `source_counts`
- `latest_cursors`
- `messages[]`
- `threads[]`
- `open_by_owner`
- `review_pending_by_owner`
- `stale_or_unindexed`
- `classifier_warnings`
- `active_authority_drift`
- `delivery_state`
- `latency_budget_status`

### 5.2 Make Hot Endpoints Snapshot-Backed

Change endpoint behavior:

- `/api/ping`: pure static response.
- `/api/ready`: fast server readiness and snapshot age, no full scan.
- `/api/health`: fast component summary from latest snapshot plus endpoint latency metrics.
- `/api/cockpit`: render from latest snapshot, not from `state()` full rebuild.
- `/api/status`: either snapshot-backed or clearly marked as heavy/debug.
- `/api/status?refresh=true`: explicit expensive refresh, token-protected if it mutates caches.
- `/api/run-diagnostics`: explicit expensive diagnostics.
- `/api/reconcile-authority`: explicit read/write operation to refresh generated active index/current authority artifacts, gated by existing write-token rules.

Hot endpoints must never synchronously run full diagnostics unless explicitly asked.

### 5.3 Add Background Snapshot Refresh

Add a background worker that refreshes the snapshot:

- on startup
- on interval, default every 5 seconds while dashboard is open
- on filesystem mtime change where practical
- on explicit user refresh
- after create-message, read-state mark, archive, or cleanup actions

Use stale-while-refresh:

- If refresh is in progress, return the last good snapshot immediately.
- Include `snapshot_age_seconds` and `refresh_in_progress` in responses.
- If no snapshot exists, return a degraded but fast health payload with `snapshot_missing` warning.
- If refresh fails, keep last good snapshot and expose `last_refresh_error`.

### 5.4 Generate Active Dispatch Index From Canonical State

Make `CODEX_ACTIVE_DISPATCH_INDEX.md` a generated/exported artifact, not the primary live source of truth.

Canonical rule:

- Active rows are derived from current message thread classification.
- Active index is a human-readable projection of the snapshot.
- Manual edits may be accepted, but PAH must detect divergence and offer reconciliation.

Reconciliation logic:

- If a new active dispatch exists in CODEX Inbox and is absent from index, PAH creates a proposed row.
- If a completion/RTC exists and thread is waiting review, PAH moves row to `waiting_review`.
- If ack/accept/shipped/closed evidence exists, PAH moves row to `accepted` or `closed`.
- Superseded messages should be ignored for active state but kept in thread history.

For this incident, reconciliation should produce a row similar to:

| Thread | State | Owner | Next Action | Source Mail | Completion / Ack |
| --- | --- | --- | --- | --- | --- |
| BA-APPLET-V2-ENHANCEMENTS | waiting_review | Claude Desktop | Review Codex RTC and conflict question | `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\20260502_092000_CLAUDE_to_CODEX_ba_applet_v2_final.md` | `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\20260502_073619_CODEX_to_CLAUDE_ba_applet_v2_rtc_and_conflict_question.md` |

### 5.5 Fix Classifier Semantics For Review-Pending Completion Messages

Add classifier rule:

Completion/report/RTC messages close the sender work only if no recipient review is required. If a completion message has any of these signals, it must be open on the recipient/reviewer:

- `status` contains `pending_cd_review`, `ready_for_review`, `waiting_review`, `complete_pending_review`, or equivalent.
- `thread_status: active` and `action_owner` is a real agent other than the sender.
- body contains a direct review/confirm question and frontmatter does not say no reply needed.

For `complete_pending_cd_review`:

- owner should be `claude_desktop`.
- state should be `open_on_agent` or `waiting_review`.
- dashboard title should indicate review needed.
- sender-side task can be complete, but recipient-side review remains open.

Add tests for:

- Codex RTC to CD with `complete_pending_cd_review`.
- CC ready-to-commit report to CD/Darrin.
- Claude ack with `closed` should close.
- Informational no-action reports should close.
- Superseded dispatch should not reopen.

### 5.6 Split Health Into Components

`/api/health` should return fast component health:

```json
{
  "ok": false,
  "generated_at": "...",
  "snapshot_age_seconds": 2.1,
  "components": {
    "server": {"ok": true, "latency_ms": 20},
    "physical_mailbox": {"ok": true, "messages_seen": 385},
    "delivery_ledger": {"ok": true, "recent_events": 30},
    "classifier": {"ok": false, "review_pending_misclassified": 1},
    "authority_index": {"ok": false, "unindexed_active_mail": 1, "active_rows": 0},
    "dashboard_payload": {"ok": false, "last_latency_ms": 29470},
    "diagnostics": {"ok": true, "last_run_age_seconds": 120}
  }
}
```

This lets CD/Darrin distinguish “mail file exists” from “PAH dashboard queue is correct.”

### 5.7 Add A Mediated Messaging Canary

Existing canary concepts should be extended to cover CD/Codex mediated messaging semantics.

Canary must run in an isolated temporary mailbox, not real inboxes.

It should test:

1. Create message from Codex to Claude Desktop.
2. Discover message in snapshot.
3. Classify as open on Claude Desktop.
4. Mark read.
5. Create RTC/reply.
6. Preserve review-pending state when specified.
7. Ledger all steps.
8. Archive only when close evidence exists.

Acceptance target:

- Canary completes under 2 seconds.
- No real mailbox files are modified.
- Failure gives exact failing stage.

### 5.8 Add Endpoint Latency Budgets And Tests

Add automated tests that fail if hot endpoints regress:

- `/api/ping` under 50 ms.
- `/api/ready` under 100 ms.
- `/api/health` under 250 ms.
- `/api/message-read-state` under 250 ms.
- `/api/cockpit` under 1000 ms with current real mailbox size.
- `/api/status` under 1000 ms if snapshot-backed, or explicitly excluded/renamed as debug-heavy.

Update `CODEX_run_server_smoke.ps1`:

1. Start server.
2. Check `/api/ping` for startup readiness.
3. Check `/api/ready` for snapshot availability.
4. Check `/api/health` latency and component warnings.
5. Check `/api/cockpit` latency separately.
6. Fail with endpoint-specific latency, not a generic timeout.

### 5.9 Add Controlled Restart And Stuck-Process Handling

PAH should expose operational status for the live process:

- process id
- start time
- request latency samples
- last snapshot refresh duration
- current refresh in progress duration
- pending requests count if available

Controlled restart procedure:

1. Verify no write operation is active.
2. Save last health snapshot and recent logs.
3. Stop only the known PAH process for the configured port.
4. Start PAH with stable logs.
5. Wait on `/api/ping`, not `/api/status`.
6. Force one snapshot refresh.
7. Report health and warnings.

Do not make the dashboard pretend a restart is a fix. Restart is a mitigation; the definitive fix is snapshot-backed endpoints plus reconciled authority.

## 6. Implementation Plan

### Phase 0: Immediate Stabilization

Purpose: restore operator clarity without rewriting PAH.

Tasks:

1. Refresh active dispatch index and current authority to include BA Applet v2 current state.
2. Add a visible Relay Health warning in dashboard that says active index is stale.
3. Add a temporary warning if `/api/cockpit` generation exceeds 1000 ms.
4. Update server smoke to use `/api/ping` for readiness.
5. Restart PAH only after preserving logs and confirming with Darrin if needed.

Acceptance:

- Relay Health no longer says `0 active_rows` when active dispatch exists.
- BA Applet v2 RTC appears as waiting review for Claude Desktop.
- `/api/ping` works after restart.
- `/api/cockpit` still may be slow, but UI warns accurately.

### Phase 1: Snapshot Service

Tasks:

1. Create mediated mail snapshot builder.
2. Persist `CODEX state\CODEX_pah_mail_state_snapshot.local.json`.
3. Add in-memory snapshot cache.
4. Add stale-while-refresh lock.
5. Port cockpit payload to read from snapshot.
6. Port health payload to read from snapshot.

Acceptance:

- `/api/health` under 250 ms.
- `/api/cockpit` under 1000 ms.
- Refresh in progress does not block dashboard.
- Snapshot includes current active BA thread and RTC state.

### Phase 2: Classifier And Authority Reconciliation

Tasks:

1. Add review-pending completion classifier rules.
2. Add tests for `complete_pending_cd_review`.
3. Generate active dispatch index projection from snapshot.
4. Add reconcile preview and write action.
5. Update Relay Health to check generated/proposed state, not only manual index text.

Acceptance:

- Latest Codex RTC to CD is open on CD until CD replies/acks.
- Superseded dispatches do not create active queue clutter.
- Active index drift is reported with a proposed row.
- Reconciliation is idempotent.

### Phase 3: Performance Hardening

Tasks:

1. Profile `load_messages`, `build_thread_focus`, diagnostics, route tests, git status, and work board calls.
2. Add incremental file-signature cache keyed by full path, mtime, and length.
3. Parse only changed files on refresh.
4. Avoid recomputing thread focus from scratch if no message signatures changed.
5. Move route tests and diagnostics to explicit/background refresh.

Acceptance:

- Current 385-message mailbox loads under target.
- Repeated dashboard refreshes do not rescan unchanged markdown files.
- High CPU PAH process condition is no longer reproducible under normal refresh.

### Phase 4: Transaction Canary And Operator UX

Tasks:

1. Add isolated mediated-message canary.
2. Add dashboard card: File Bridge / Classifier / Authority / Latency.
3. Add copyable concise status for CD/CC.
4. Add one-click Run Canary.
5. Add one-click Reconcile Active Index preview.

Acceptance:

- CD issue can be diagnosed by component in under one minute.
- Dashboard does not require terminal inspection for normal health triage.
- Canary failure says which stage failed.

## 7. Required Tests

Unit tests:

- frontmatter parse for `complete_pending_cd_review`.
- classifier owner/state for RTC pending CD review.
- classifier close behavior for true closed/ack messages.
- active dispatch derivation from current CODEX Inbox message.
- superseded dispatch suppression.
- index projection generation.
- snapshot stale-while-refresh behavior.

Integration tests:

- temporary mailbox with Codex -> CD dispatch/report flow.
- temporary mailbox with CD -> Codex dispatch and Codex RTC back.
- current real mailbox read-only snapshot build.
- Relay Health drift detection.
- endpoint latency budget check.

Smoke tests:

- server readiness via `/api/ping`.
- `/api/health` fast component response.
- `/api/cockpit` fast snapshot response.
- `/api/run-diagnostics` still works, but not on hot path.

Manual verification:

- Start PAH dashboard.
- Confirm BA Applet v2 thread appears in correct owner/review state.
- Confirm latest Codex-to-Claude RTC is visible as CD review-needed until CD response.
- Confirm no old PAH/Relay dispatches bury current work as first-priority false positives.
- Confirm Health card explains stale authority if drift exists.

## 8. Data Contracts

### 8.1 Snapshot Summary

```json
{
  "schema_version": 1,
  "generated_at": "2026-05-02T07:45:00-07:00",
  "duration_ms": 320,
  "source_counts": {
    "messages": 385,
    "threads": 95,
    "mailboxes": 8
  },
  "freshness": {
    "age_seconds": 2.4,
    "refresh_in_progress": false,
    "last_error": ""
  },
  "authority": {
    "active_rows": 1,
    "unindexed_active_mail": 0,
    "current_authority_age_hours": 0.1,
    "reconcile_available": false
  },
  "classifier": {
    "open_on_codex": 0,
    "open_on_claude_desktop": 1,
    "open_on_claude_code": 0,
    "open_on_darrin": 3,
    "owner_unknown": 0,
    "warnings": []
  }
}
```

### 8.2 Thread State

```json
{
  "thread_id": "BA-APPLET-V2-ENHANCEMENTS",
  "state": "waiting_review",
  "owner": "claude_desktop",
  "source_message": "C:\\CODEX PG\\CODEX Claude Codex Mailbox\\CODEX Inbox\\20260502_092000_CLAUDE_to_CODEX_ba_applet_v2_final.md",
  "latest_message": "C:\\CODEX PG\\CODEX Claude Codex Mailbox\\CLAUDE Inbox\\20260502_073619_CODEX_to_CLAUDE_ba_applet_v2_rtc_and_conflict_question.md",
  "why": "Codex RTC has status complete_pending_cd_review and action_owner claude_desktop.",
  "requires_darrin_decision": false,
  "superseded_sources": [
    "20260502_071500_CLAUDE_to_CODEX_ba_applet_v2_enhancements.md",
    "20260502_082500_CLAUDE_to_CODEX_ba_applet_spec_update.md"
  ]
}
```

### 8.3 Endpoint Health Component

```json
{
  "name": "dashboard_payload",
  "ok": false,
  "severity": "error",
  "latency_ms": 29470,
  "budget_ms": 1000,
  "detail": "Cockpit payload exceeded live dashboard budget; serving stale snapshot is required."
}
```

## 9. Acceptance Criteria For Definitive Fix

The fix is not accepted until all are true:

1. `CODEX_run_smoke_tests.py` passes.
2. PAH inspector passes with no fail and no unresolved mediated-mail warning.
3. Server smoke passes using `/api/ping`, `/api/health`, and `/api/cockpit` with latency budgets.
4. `/api/status` and `/api/cockpit` do not block for 10+ seconds on current mailbox size.
5. Relay Health reports no unindexed current active CODEX mail after reconciliation.
6. Active dispatch index includes or accurately projects the BA Applet v2 thread state.
7. Latest Codex-to-Claude RTC appears as Claude Desktop review-needed until CD replies.
8. Physical mailbox write, discovery, classifier, read-state, and ledger canary passes.
9. Dashboard shows separate component health for file bridge, classifier, authority, and latency.
10. Restarting PAH is no longer required to make new messages visible.
11. Durable docs are updated: README, TODO, reliability spec, and this report/spec or successor.

## 10. Immediate Operational Recommendation

Do not trust the current PAH dashboard queue as the sole source of truth until this fix lands.

For the current incident:

1. Treat the physical mailbox bridge as working.
2. Treat PAH dashboard mediation as stale/degraded.
3. Use direct mailbox file checks for critical CD/Codex communication until active-index reconciliation is done.
4. Update/reconcile `CODEX_ACTIVE_DISPATCH_INDEX.md` for BA Applet v2.
5. Ensure the latest Codex RTC is surfaced to CD as review-needed.
6. If PAH remains slow, perform a controlled restart as mitigation only.
7. Implement the snapshot-backed endpoint fix before claiming PAH-mediated messaging is definitively repaired.

## 11. Files Implicated

Primary code:

- `C:\CODEX PG\CODEX Agent Hub\CODEX_agent_hub.py`
- `C:\CODEX PG\CODEX Automation\CODEX_relay_health_check.ps1`
- `C:\CODEX PG\CODEX Agent Hub\CODEX_run_server_smoke.ps1`
- `C:\CODEX PG\CODEX Agent Hub\CODEX_run_smoke_tests.py`
- `C:\CODEX PG\CODEX Agent Hub\CODEX_pah_inspector.py`

State/authority:

- `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX_ACTIVE_DISPATCH_INDEX.md`
- `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX_CURRENT_AUTHORITY.md`
- `C:\CODEX PG\CODEX Agent Hub\CODEX state\CODEX_read_state.local.json`
- `C:\CODEX PG\CODEX Agent Hub\CODEX state\CODEX_relay_health_cache.local.json`
- proposed: `C:\CODEX PG\CODEX Agent Hub\CODEX state\CODEX_pah_mail_state_snapshot.local.json`

Docs to update when implemented:

- `C:\CODEX PG\CODEX Agent Hub\CODEX_README.md`
- `C:\CODEX PG\CODEX Agent Hub\CODEX_PAH_RELIABILITY_AND_DESIGN_SPEC.md`
- `C:\CODEX PG\CODEX Agent Hub\CODEX_PAH_TODO.md`
- this report/spec or its successor

## 12. Non-Goals

This spec does not authorize:

- deleting or archiving mailbox files
- committing or pushing changes
- writing into `C:\panda-gallery`
- bypassing Darrin approval gates
- replacing mailbox protocol with an external service
- hiding diagnostics warnings to make PAH look green

## 13. Final Diagnosis

PAH-mediated messaging is degraded because the live mediation layer is doing too much synchronous work on every dashboard/status request and because the compact authority/index files have drifted behind real mailbox traffic. The physical mailbox bridge works. The dashboard/state service is stale, slow, and misclassifies review-pending completion messages.

The definitive fix is to make PAH snapshot-driven, reconcile authority automatically, classify review-pending RTC/report messages correctly, and enforce endpoint latency budgets. Anything less is a partial patch.
