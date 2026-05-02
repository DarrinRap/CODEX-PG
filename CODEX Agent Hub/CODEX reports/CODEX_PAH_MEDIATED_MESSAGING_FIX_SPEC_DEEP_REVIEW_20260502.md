# CODEX PAH Mediated Messaging Fix Spec Deep Review

Date: 2026-05-02
Reviewer: Codex
Reviewed spec: `C:\CODEX PG\CODEX Agent Hub\CODEX reports\CODEX_PAH_MEDIATED_MESSAGING_DEFINITIVE_FIX_SPEC_20260502.md`
Status: deep review, no implementation changes made

## Executive Assessment

The fix spec has the right core instinct: PAH should not rebuild expensive mailbox/dashboard state synchronously on hot endpoints, and it should not treat stale active-index files as trustworthy live mediation. The snapshot-backed direction is sound.

However, the current spec is not yet definitive. It has several important errors and underspecified areas that could create a second generation of PAH drift if implemented literally. The biggest risks are:

1. It overclaims that the physical bridge is working end-to-end when only PAH-side file discovery was proven.
2. It proposes generated authority/index state without a trust model strong enough for mailbox content, which is third-party agent-authored material.
3. It does not model multi-gate thread ownership: CD review and Darrin commit approval can both exist in sequence.
4. It specifies background refresh and canary behavior without enough concurrency safety for `ThreadingHTTPServer`.
5. It duplicates existing parse-cache work and postpones profiling until after major architecture choices.
6. It does not provide a safe compatibility/migration plan for `/api/status`, even though the current UI and tests depend on that route.

The spec should be treated as a strong incident report plus a draft architecture, not as an implementation-ready blueprint.

## Review Method

Reviewed against:

- `CODEX_PAH_MEDIATED_MESSAGING_DEFINITIVE_FIX_SPEC_20260502.md`
- `CODEX_agent_hub.py`
- `CODEX_run_smoke_tests.py`
- `CODEX_relay_health_check.ps1`
- `CODEX_PAH_RELIABILITY_AND_DESIGN_SPEC.md`
- `CODEX_PAH_MAIL_AND_INSPECTOR_UX_SPEC.md`
- `CODEX_PAH_TODO.md`

Important code evidence:

- `CODEX_agent_hub.py:3547-3655`: `/api/health` calls `health_payload()`, which calls `health_payload_from_cockpit(cockpit_payload())`; this confirms health is currently coupled to the cockpit path.
- `CODEX_agent_hub.py:3988-4095`: `cockpit_payload()` calls `state()` and then builds routes, feed, thread focus, action queue, diagnostics, and health summary.
- `CODEX_agent_hub.py:3284-3366`: `state()` synchronously loads messages and builds many subsystems.
- `CODEX_agent_hub.py:496-548`: an mtime/size message parse cache already exists.
- `CODEX_agent_hub.py:769-806`: classifier closes completion evidence unless `thread_status` is `ready_for_review` or `waiting_review`.
- `CODEX_agent_hub.py:1934-2013`: current mailroom canary mutates module globals inside a temporary directory.
- `CODEX_run_smoke_tests.py:575-631`: current tests expect cockpit and health contracts directly from current payload functions.
- `CODEX_relay_health_check.ps1:423-435`: unindexed mail warning depends on active-index write time plus absence from active index/authority text.

## Severity Legend

- P0: Could cause PAH to misroute, hide, or corrupt coordination state.
- P1: Could cause major implementation churn, unreliable health, or false confidence.
- P2: Important ambiguity or missing acceptance detail.
- P3: Editorial or lower-risk clarification.

## Findings

### P0-1: End-to-end CD pickup was not proven, but the spec says the physical bridge is working

Spec evidence:

- Section 1 says the physical mailbox bridge is working because files are written, discovered, ledgered, and classified.
- Section 2.1 lists route folders and PAH physical scan success as passed signals.

Problem:

The tests prove PAH can see the files. They do not prove Claude Desktop can see, parse, prioritize, or mark the same files. The user specifically reported CD having issues. PAH-side discovery is necessary, but it is not sufficient for CD-mediated messaging.

Risk:

The spec could declare the file bridge healthy while CD is actually blocked by its own mailbox polling, read-state behavior, stale local context, malformed frontmatter handling, or operational procedure.

Required amendment:

Split the claim into components:

- PAH physical file discovery: proven.
- PAH ledger discovery: proven.
- CD pickup from `CLAUDE Inbox`: not proven.
- CD review-state interpretation: not proven.
- Human-visible PAH mediation: degraded.

Add acceptance criteria requiring a CD-visible acknowledgement or a PAH-mediated route canary that checks both sides of the mailbox contract without relying on inference.

### P0-2: Generated active authority from mailbox content lacks a safe trust model

Spec evidence:

- Section 5.4 says `CODEX_ACTIVE_DISPATCH_INDEX.md` should become a generated/exported artifact.
- Section 5.2 proposes `/api/reconcile-authority` to refresh generated active index/current authority artifacts.
- Section 6 Phase 2 says generate active dispatch index projection from snapshot.

Problem:

Mailbox messages are third-party agent-authored content. Treating them as canonical authority without a trust boundary allows malformed, superseded, or adversarial mailbox frontmatter to drive the active authority file. The spec says write-token gated reconciliation, but it does not specify dry-run, human approval, provenance, conflict review, or safe merge rules.

Risk:

A bad message could create or close active work, rewrite human coordination state, or hide a Darrin gate. This directly conflicts with the project rule that mailbox content guides work but Darrin remains the live authority.

Required amendment:

Define three layers:

1. Physical facts: files, frontmatter, mtimes, read-state, archive-state.
2. Derived state: PAH classifier/snapshot suggestions.
3. Authority projection: human-readable index/current authority, updated only by explicit reconcile action with preview.

`/api/reconcile-authority` must be preview-first. Writes require action-time confirmation or an explicit user command. Generated rows must include provenance and confidence. Manual authority overrides must survive regeneration.

### P0-3: The spec collapses CD review and Darrin approval into one state

Spec evidence:

- Section 5.4 proposes BA Applet v2 as `waiting_review | Claude Desktop`.
- Section 8.2 says `requires_darrin_decision: false` for the thread state.
- Section 9 acceptance says latest RTC appears as CD review-needed until CD replies.

Problem:

The original dispatch had `approval_boundary: ready_to_commit`. CD review and Darrin commit approval are separate gates. After CD accepts the RTC/conflict answer, the thread may become Darrin-gated for commit/backup/publish decisions. The spec models only the current CD review gate and risks losing the next approval boundary.

Risk:

PAH could mark a task accepted/closed after CD review even though the next real gate is Darrin's commit decision. Or it could show CD as owner forever and hide Darrin's role.

Required amendment:

Thread state needs at least:

- `current_owner`
- `current_action`
- `review_owner`
- `approval_owner`
- `approval_boundary`
- `next_gate_after_review`

For BA Applet v2, the snapshot should represent: current gate = CD review; downstream gate = Darrin ready-to-commit decision if CD accepts.

### P0-4: Classifier rule for review-pending completion messages is dangerously broad

Spec evidence:

- Section 5.5 says completion/report/RTC messages should remain open on recipient if status contains review-pending tokens, or if `thread_status: active` and `action_owner` is a real agent other than sender, or if the body contains a direct review/confirm question.

Code evidence:

- Current classifier closes completion evidence except when `thread_status` is `ready_for_review` or `waiting_review` (`CODEX_agent_hub.py:792-795`).
- No-action coordination shares intentionally close when they say no action/no reply (`CODEX_agent_hub.py:655-672`, `790-791`).

Problem:

The proposed body-based rule is ambiguous and can reopen too many messages. The broad `thread_status: active` plus action-owner rule can also convert informational reports into open work. Body text is especially risky because it is third-party content and can contain misleading instructions.

Risk:

PAH may create false open work, resurrect completed threads, or let prompt-like message body text steer coordination state.

Required amendment:

Use metadata-first precedence:

1. Explicit closed/archived/superseded wins unless a newer message reopens.
2. `requires_darrin_decision` and Darrin gates win over agent gates.
3. Explicit review-pending statuses/fields win for recipient review.
4. Completion evidence closes sender work.
5. Body text may produce a warning/hint only, never authoritative owner/state.

Define an exact enum: `complete_pending_cd_review`, `ready_for_cd_review`, `waiting_cd_review`, `ready_for_human_loop`, `ready_to_commit`, etc. Avoid free-form `contains equivalent` language.

### P0-5: Snapshot persistence may duplicate or expose sensitive mailbox content

Spec evidence:

- Section 5.1 says snapshot outputs include `mail_state_snapshot.local.json`, `mail_state_snapshot.latest.md`, `messages[]`, and `threads[]`.
- Section 8 defines contracts but does not limit body/raw metadata inclusion.

Problem:

A persisted snapshot can become a second copy of mailbox content. Mailboxes may contain private operational details, paths, approval-sensitive text, or injected instructions. The spec does not say whether snapshot files are local-only, ignored by git, sanitized, redacted, or body-free.

Risk:

PAH could multiply sensitive or misleading third-party content into new durable artifacts, reports, or commits.

Required amendment:

Snapshot contract must prohibit raw bodies by default. Store only:

- ids
- paths
- hashes
- normalized metadata
- sanitized title/summary
- state/owner/reason
- timestamps

Raw body should be read on demand from the source file. Snapshot files must live under ignored local state, with explicit `.gitignore` coverage. Any human-readable `.md` projection must avoid raw message body unless requested.

### P0-6: Background refresh and canary design are not thread-safe enough

Spec evidence:

- Section 5.3 proposes background snapshot refresh.
- Section 5.7 proposes mediated messaging canary.

Code evidence:

- PAH runs under `ThreadingHTTPServer` (`CODEX_agent_hub.py:5409`).
- Current canary mutates module globals such as `CLAUDE_INBOX`, `LEDGER_PATH`, `INTERACTION_LEDGER_PATH`, `MESSAGE_DIRS`, and `set_message_read_state` (`CODEX_agent_hub.py:1942-1965`).
- `MAILROOM_CANARY_LOCK` serializes canary runs, but it does not prevent other request threads from reading mutated globals.

Problem:

The spec does not address global-state safety. If background refresh, dashboard requests, or canary run concurrently, global mutation can leak temporary canary paths into live PAH behavior.

Risk:

Intermittent lost messages, false health, or writes to temporary paths during real requests.

Required amendment:

Before adding background refresh, refactor state builders to accept an explicit context/config object instead of mutating globals. Canary must use dependency injection or a separate process/context. Add a global write/read operation registry or reader-writer lock for snapshot refresh and message writes.

### P1-1: The spec says to add an incremental file-signature cache, but one already exists

Spec evidence:

- Section 6 Phase 3 says to add an incremental file-signature cache keyed by full path, mtime, and length.

Code evidence:

- `MESSAGE_PARSE_CACHE` already exists and keys parsed messages by resolved path with `(mtime_ns, size)` signature (`CODEX_agent_hub.py:145-146`, `496-548`).
- Smoke tests already validate unchanged mailbox parse caching (`CODEX_run_smoke_tests.py:2104-2122`).

Problem:

The spec duplicates existing functionality and may lead to a second overlapping cache rather than improving the real bottleneck.

Required amendment:

Replace “add incremental file-signature cache” with:

- profile whether `MESSAGE_PARSE_CACHE` is being invalidated or bypassed;
- extend cache to derived thread/snapshot state;
- preserve existing cache tests;
- add cache metrics to health.

### P1-2: Profiling is scheduled too late

Spec evidence:

- Profiling appears in Phase 3 after Phase 1 snapshot service and Phase 2 classifier/reconciliation.

Problem:

The root cause is inferred from endpoint timing and code shape, but the exact 29-second cost has not been attributed. It could be route tests, git status, diagnostics, thread focus, filesystem enumeration, antivirus/OneDrive file I/O, or lock contention.

Risk:

A large snapshot rewrite might not attack the real bottleneck, or it might hide a slow subroutine that still runs in the background and burns CPU.

Required amendment:

Move profiling to Phase 0. Add instrumentation around each `state()` subsystem before designing the snapshot split. Required output: per-block timing, cache hit/miss counts, message count, thread count, route-test duration, diagnostics duration, git duration, and response serialization size.

### P1-3: `/api/status` compatibility is under-specified

Spec evidence:

- Section 5.2 says `/api/status` should be snapshot-backed or clearly marked heavy/debug.

Code evidence:

- The embedded legacy dashboard fetches `/api/status` (`CODEX_agent_hub.py:4826`).
- Current tests assert the health/cockpit contract but do not define a replacement status compatibility contract (`CODEX_run_smoke_tests.py:575-631`).

Problem:

Changing `/api/status` can break existing dashboard code, operator habits, and compatibility tests. Keeping it heavy preserves the failure. The spec does not define a migration path.

Required amendment:

Define:

- `/api/status`: backward-compatible, snapshot-backed summary with the same top-level keys where feasible.
- `/api/status/full` or `/api/debug/status`: expensive full rebuild, explicit and visually marked.
- `/api/status?refresh=true`: optional explicit refresh, but not the default UI path.
- Test both compatibility and latency.

### P1-4: Health schema in the spec conflicts with existing health contract

Spec evidence:

- Section 5.6 proposes components named `physical_mailbox`, `delivery_ledger`, `classifier`, `authority_index`, and `dashboard_payload`.

Code/test evidence:

- Current health components include `server`, `routes`, `inspector`, `mailboxes`, `unanswered`, `urgent_codex`, `agent_progress`, `archive`, `interaction_ledger`, `diagnostics`, `periodic_monitor`, and `github_backup` (`CODEX_agent_hub.py:3572-3642`).
- Smoke tests expect component names such as `server`, `routes`, `inspector`, `mailboxes`, `unanswered`, `agent_progress`, `archive`, `diagnostics`, `periodic_monitor`, and `github_backup` (`CODEX_run_smoke_tests.py:619-631`).

Problem:

The spec proposes a replacement-looking schema without saying whether these are new components, renamed components, nested subcomponents, or a breaking change.

Required amendment:

Preserve existing health components and add a `mediated_messaging` component with subcomponents:

- `physical_mailbox`
- `delivery_ledger`
- `classifier`
- `authority_index`
- `endpoint_latency`
- `snapshot_freshness`

Do not break the existing health payload contract without an explicit version bump and UI migration.

### P1-5: Endpoint latency budgets are too absolute and measurement method is undefined

Spec evidence:

- Section 3 and 5.8 set targets such as `/api/ping` under 50 ms and `/api/health` under 250 ms.

Problem:

Single-sample timings from PowerShell or a cold process on Windows can be noisy. A hard 50 ms budget can become flaky. The spec does not say warm vs cold, local HTTP client, percentile, sample count, or allowed hardware variance.

Required amendment:

Define budgets by mode:

- readiness cold-start budget
- warm endpoint p50/p95 over N samples
- current real-mailbox budget
- synthetic large-mailbox budget

Example: `/api/ping` p95 under 100 ms over 20 warm samples; `/api/health` p95 under 300 ms when snapshot age under 10 seconds; `/api/cockpit` p95 under 1000 ms with 500 synthetic messages.

### P1-6: Snapshot staleness policy is incomplete

Spec evidence:

- Section 5.3 says serve last good snapshot if refresh is in progress and expose `snapshot_age_seconds`.

Problem:

It does not define when a stale snapshot becomes warning/error, when PAH must block actions, or what happens if no snapshot exists for a long period.

Required amendment:

Define freshness thresholds:

- fresh: under 10 seconds
- warn: 10-60 seconds
- error: over 60 seconds or refresh failed N times
- write actions disabled if snapshot is error-stale unless the action is explicit direct-file operation with confirmation

### P1-7: The active-index drift diagnosis is partly valid but too dependent on file timestamp

Spec evidence:

- Section 4.2 treats active-index drift as core root cause.

Code evidence:

- `CODEX_relay_health_check.ps1` detects unindexed recent CODEX mail by comparing mail last-write time to active-index last-write time and checking absence from active index/current authority text (`CODEX_relay_health_check.ps1:423-435`).

Problem:

Last-write-time comparison is a useful warning, but not a canonical drift test. A message can be absent from index and still be intentionally inactive. A message can be present in text but with wrong state. An index can be edited later but still omit important fields.

Required amendment:

Drift detection should compare derived active thread set to projected active-index rows by thread id, state, owner, source, completion, and gate fields. Use mtime only as a cheap cursor, not the actual correctness condition.

### P1-8: The spec does not define how supersedence works

Spec evidence:

- Section 5.4 says superseded messages should be ignored for active state but kept in thread history.
- Section 8.2 includes superseded source filenames.

Problem:

It does not define how to parse `supersedes`, `supersedes_also`, `in_reply_to`, `reply_to`, or body-only supersedence. It does not define what happens when the superseding message is later withdrawn or closed.

Required amendment:

Add a supersedence contract:

- accepted frontmatter fields
- direction of relationship
- same-thread requirement or cross-thread allowance
- conflict handling when two active superseders exist
- display behavior
- tests using BA Applet v2 071500/082500/092000 as fixtures

### P1-9: “Delivery confirmation healthy” is listed but not defined

Spec evidence:

- Section 3 health components include `delivery confirmation healthy`.
- Later contracts mention delivery ledger, but not delivery confirmation semantics.

Problem:

Delivery confirmation could mean file written, PAH discovered, recipient agent read, recipient agent replied, or human saw it in PAH. The spec uses the phrase as if it is obvious.

Required amendment:

Define delivery levels:

1. `written`: file exists in routed inbox.
2. `discovered`: PAH ledger saw it.
3. `visible`: PAH snapshot exposes it to recipient owner.
4. `read`: PAH read state or recipient read receipt exists.
5. `acknowledged`: recipient reply/ack exists.

Health should report the highest proven level, not a boolean.

### P1-10: The Mail-first UX requirement is not integrated

Spec evidence:

- The reviewed spec focuses on cockpit/status endpoints, active index, and health components.

Parent spec evidence:

- `CODEX_PAH_MAIL_AND_INSPECTOR_UX_SPEC.md` says PAH should default to Mail, with Inspector as health/evidence and Advanced retaining cockpit internals.

Problem:

The new fix spec does not say whether snapshot-backed state feeds Mail, Inspector, Advanced, or all three. It risks optimizing the old cockpit path without advancing the Mail-first product direction.

Required amendment:

Define snapshot consumers:

- Mail: inbox/message list/reader/reply state
- Inspector: health/evidence/freshness
- Advanced: legacy cockpit/action queue

Make Mail list latency and correctness the primary acceptance surface, not only `/api/cockpit`.

### P1-11: The current canary already exists, but the spec does not distinguish old vs new canary

Spec evidence:

- Section 5.7 says add a mediated messaging canary.

Code evidence:

- `run_mailroom_transaction_canary()` already exercises send, read-state, reply tombstone, and ledger writes in a temporary mailbox (`CODEX_agent_hub.py:1934-2013`).
- Existing tests verify this canary (`CODEX_run_smoke_tests.py:561-570`).

Problem:

The spec could lead implementers to duplicate the canary rather than extending it. It also fails to call out the existing canary's concurrency flaw.

Required amendment:

Rename the desired new canary to `mediated_message_state_canary` and specify that it extends, not replaces, `run_mailroom_transaction_canary()`. First refactor canary isolation to avoid mutating globals during concurrent request handling.

### P1-12: Restart handling lacks a concrete in-flight write detector

Spec evidence:

- Section 5.9 says verify no write operation is active before restart.

Problem:

No operation registry is specified. PAH currently has multiple write paths: create message, read-state, mark-all-read, archive, diagnostics report, canary, route tests, work items, approvals, decision state, cache updates. Without a registry, “no write operation active” is hand-waving.

Required amendment:

Add a write-operation registry:

- operation id
- endpoint/action
- actor
- started_at
- target paths
- safe_to_interrupt boolean
- timeout

Restart should be blocked or warning-gated if active unsafe writes exist.

### P2-1: `/api/ready` is proposed but not specified

Spec evidence:

- Section 5.2 and 5.8 introduce `/api/ready`.

Problem:

No schema is provided. It is unclear whether readiness means server process only, snapshot available, snapshot fresh, or full mail mediation trustworthy.

Required amendment:

Define `/api/ready` separately from `/api/health`:

- `server_ready`: process accepting requests
- `snapshot_available`: last good snapshot exists
- `snapshot_fresh_enough`: age below threshold
- `degraded_reason`: string/list

### P2-2: “while dashboard is open” is ambiguous in a simple HTTP app

Spec evidence:

- Section 5.3 says refresh every 5 seconds while dashboard is open.

Problem:

The current PAH server is a simple HTTP server, not a websocket/session-tracked app. It may not know whether the dashboard is open unless heartbeat pings are added.

Required amendment:

Choose one:

- always refresh on interval when server runs;
- refresh only on request with stale-while-refresh;
- add `/api/client-heartbeat` and stop refresh after no heartbeat for N seconds.

### P2-3: Filesystem watch is underspecified for Windows/OneDrive

Spec evidence:

- Section 5.3 says refresh on filesystem mtime change where practical.

Problem:

OneDrive paths and Windows file notifications can be noisy or delayed. PAH uses several mailbox roots across `C:\CODEX PG` and `C:\panda-gallery`.

Required amendment:

Use polling by directory signature first. Filesystem watching can be an optional optimization. Define debounce, dropped-event handling, and fallback to scheduled scan.

### P2-4: Data contracts use underspecified owner/status enums

Spec evidence:

- Section 8 uses `owner: claude_desktop`, `state: waiting_review`, and classifier fields like `open_on_claude_desktop`.

Problem:

Current code normalizes frontmatter agents to hyphenated ids and then thread-focus owners to underscore ids. UI labels use participant labels. The spec mixes human labels, underscore ids, and route labels without declaring canonical wire values.

Required amendment:

Define canonical machine ids:

- `claude-desktop`
- `claude-code`
- `codex`
- `darrin`

Define derived bucket keys separately if underscore keys are retained for JS compatibility. Do not mix labels and ids in contracts.

### P2-5: Acceptance criteria do not include visual/browser review despite parent spec requiring it

Spec evidence:

- Section 9 acceptance criteria are mostly tests and payload behavior.

Parent spec evidence:

- Reliability/design spec requires live browser and live Inspector review before meaningful PAH/Inspector handoff.
- Mail/Inspector UX spec requires screenshots for meaningful visual changes.

Problem:

The fix will touch health cards, Mail/Inspector/Advanced surfaces, and latency warnings. Acceptance must include visual verification if UI changes occur.

Required amendment:

Add:

- live browser review at `http://127.0.0.1:8765/`
- screenshot evidence for Mail, Inspector, and Advanced/health warning states
- text overlap and UI grammar checks against PG Design Bible

### P2-6: The spec does not define rollback or feature flags

Problem:

Snapshot-backed state is a large architectural change. If it misclassifies mail, PAH can become less trustworthy than before.

Required amendment:

Add:

- environment flag or config to use legacy `state()` path
- side-by-side comparison endpoint: `legacy_state` vs `snapshot_state`
- shadow mode before switching the UI
- diff report for thread owner/state differences

### P2-7: “No real mailbox files are modified” conflicts with route-level canary wording unless isolated route context is explicit

Spec evidence:

- Section 5.7 says create message from Codex to Claude Desktop, but also says no real mailbox files are modified.

Problem:

A route-based create-message normally writes to `CLAUDE Inbox`. The spec only later says isolated temporary mailbox. It should be impossible to misread.

Required amendment:

State that canary routes must use injected temporary mailbox roots, never production globals, and must fail closed if isolation cannot be proven.

### P2-8: The spec does not say how read-state interacts with review state

Problem:

A message can be read but still actionable. Current Relay Health reports unread incoming, but action queues are classifier-based. The spec does not define whether marking an RTC read removes it from review-needed, or whether review-needed persists until ack/reply.

Required amendment:

Define read-state as visibility state only. It must not close action state unless accompanied by reply, ack, archive, or explicit handled action.

### P2-9: The spec omits archive behavior for snapshot-derived state

Problem:

Archive/read handling is central to PAH. Snapshot state must account for archive tombstones, reopened-by-new-activity, and archive skips.

Required amendment:

Add archive-state fields to thread contract:

- `archived`
- `archived_at`
- `archive_reason`
- `reopened_by_new_activity`
- `archive_safe`
- `archive_blockers`

### P2-10: The spec does not define response size budgets

Problem:

Even with faster computation, `/api/cockpit` can be slow because of large JSON serialization/transfer. The current payload contains `latest`, `simple_mail`, `agent_mailboxes`, `thread_focus`, `selected_thread`, routes, health, etc.

Required amendment:

Add payload size and pagination budgets:

- Mail list limit
- thread detail lazy-load
- raw body lazy-load
- default cockpit payload max bytes
- `/api/message?id=` for detail

### P2-11: The spec does not address duplicate `normalize_agent_id` definitions

Code evidence:

- `normalize_agent_id` is defined near `CODEX_agent_hub.py:233` and again near `CODEX_agent_hub.py:2123`; the later definition overrides the earlier one.

Problem:

This is confusing technical debt in the code path the spec wants to harden. It may not cause the current incident, but it makes classifier/owner work riskier.

Required amendment:

Add a cleanup item to consolidate participant normalization into one module/function and test aliases for `cd`, `cc`, `claude_desktop`, `claude-code`, etc.

### P3-1: The spec says `/api/health` “appears” to rely on cockpit, but code proves it does

Spec evidence:

- Section 4.1 says `/api/health` appears to rely on the same heavy cockpit/status path.

Code evidence:

- `health_payload()` returns `health_payload_from_cockpit(cockpit_payload())`.

Required amendment:

Change “appears to rely” to “currently calls”.

### P3-2: The report line count and artifact status should be recorded in a manifest

Problem:

This incident now has multiple generated reports and screenshots. There is no small manifest tying together test outputs, report paths, and next actions.

Required amendment:

Add a `CODEX_PAH_INCIDENT_20260502_MANIFEST.md` or append to an existing report index.

## Required Spec Amendments Before Implementation

1. Add a trust-boundary section: mailbox content is evidence, not authority.
2. Add a three-layer state model: physical facts, derived snapshot, human authority projection.
3. Add dual-gate ownership: current owner, review owner, approval owner, next gate.
4. Replace broad body-based classifier rule with metadata-first exact enum rules.
5. Move profiling to Phase 0.
6. Build on existing `MESSAGE_PARSE_CACHE`; do not add a duplicate cache.
7. Define snapshot security: no raw bodies by default, ignored local state, sanitized projections.
8. Define thread-safe refresh/canary architecture before adding background workers.
9. Preserve `/api/status` compatibility or version it explicitly.
10. Add `mediated_messaging` as a health subcomponent rather than replacing current health components.
11. Define `/api/ready` schema.
12. Define endpoint latency measurement methodology.
13. Add stale snapshot thresholds and fail modes.
14. Add reconcile preview/approval workflow.
15. Add supersedence rules and fixtures.
16. Add read-state vs action-state semantics.
17. Add archive-state semantics.
18. Add payload size/pagination budgets.
19. Add visual/browser acceptance checks from parent PAH specs.
20. Add rollback/shadow-mode plan.

## Proposed Corrected Phase Order

### Phase 0: Measurement And Stabilization

- Instrument `state()` sub-block durations.
- Measure endpoint p50/p95 locally over repeated warm samples.
- Reconcile BA Applet v2 manually or via dry-run preview.
- Add explicit warning for stale active authority.
- Update server smoke readiness to use `/api/ping`, while keeping status latency as a separate failure.

### Phase 1: Trust-Safe Snapshot Shadow Mode

- Build snapshot from physical facts and classifier output.
- Persist sanitized local-only snapshot.
- Do not switch UI yet.
- Add diff report: legacy state vs snapshot state.
- Add exact classifier tests for review-pending RTC and Darrin-gated ready-to-commit.

### Phase 2: Health And Mail UI Integration

- Add `mediated_messaging` health component.
- Feed Mail surface from snapshot in shadow/preview mode.
- Keep `/api/status` compatible.
- Add `/api/ready` and fast `/api/health`.

### Phase 3: Authority Reconciliation

- Add dry-run reconcile proposal.
- Preview generated active-index row changes.
- Require explicit write approval/action.
- Preserve manual overrides and Darrin gates.

### Phase 4: Performance Switch-Over

- Move cockpit/advanced dashboard to snapshot-backed payload.
- Keep legacy debug endpoint.
- Enforce latency and payload-size budgets.
- Add rollback flag.

### Phase 5: Canary And Operational UX

- Refactor canary isolation to avoid globals.
- Add mediated-message state canary.
- Add dashboard actions: Run Canary, Copy Status, Reconcile Preview.
- Verify live browser Mail/Inspector/Advanced states.

## Bottom Line

The reviewed spec is directionally correct but too confident. It should not be implemented literally until the trust model, classifier precedence, concurrency design, endpoint compatibility, and profiling order are corrected.

A safe definitive fix is still achievable, but the next step should be a spec revision, not code changes.
