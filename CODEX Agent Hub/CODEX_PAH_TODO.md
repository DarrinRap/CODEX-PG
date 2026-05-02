# PAH Todo

## Critical Regression Note

- [ ] Treat current PAH functionality as potentially broken until re-diagnosed from first principles. User reports a MASSIVE REGRESSION: PAH behavior is not trustworthy and the Inspector screen fonts are wrong.
- [ ] Do not guess while debugging PAH. Diagnose with concrete evidence first: read the relevant code, inspect live DOM/CSS, compare against the PG Design Bible, run the Inspector, and verify live browser behavior before deciding on a fix.
- [ ] Double-check the diagnosis before applying any fix. Capture expected behavior, observed behavior, root cause, and exact file/surface affected.
- [ ] If targeted fixes do not restore PAH functionality and Inspector styling quickly, consider reverting PAH to an earlier known-good version and re-applying only verified changes.
- [ ] Before declaring PAH fixed, require live browser review of the Inspector screen fonts/palette plus live PAH functional checks. Passing smoke tests alone is not enough.

## Reliability / Audit

- [x] Add append-only PAH interaction ledger v1 (`CODEX_pah_interaction_ledger.jsonl`) for sent messages, read marks, archive sweep start/finish, archive candidates, archived messages, archive skips, mailbox discrepancies, and steward check start/finish events.
- [x] Extend PAH interaction ledger protocol to record explicit agent no-mail claims and compare them to PAH mailbox state.
- [x] Extend PAH interaction ledger protocol to record first-seen/discovered message events and classifier state transition events.
- [x] Add a dashboard discrepancy panel showing latest `mailbox_discrepancy_detected` events, affected agents, thread IDs, and recommended next action.
- [ ] Add a dashboard ledger viewer with filters for message ID, thread ID, agent, event type, and time range.
- [ ] Add ledger retention/export controls so the JSONL audit trail stays compact but remains reviewable.
- [x] Add a PAH Inspector applet for endpoint, mailbox, archive/read, ledger, and dashboard UI wiring checks.
- [x] Add create-message dry-run support so live endpoint probes cannot create stray mailbox messages.
- [x] Restore mailroom compatibility routes (`/api/send`, `/api/message-read-state`, `/api/mark-all-read`) as wrappers around current create/read-state helpers so the dashboard and operator scripts cannot silently fail against retired endpoints.
- [x] Add a token-protected mailroom transaction canary (`/api/mailroom-canary`) that exercises send, read-state, reply tombstone, and interaction-ledger writes in an isolated temporary mailbox.
- [x] Add `/api/health` Inspector freshness reporting so stale Inspector output warns instead of masquerading as current green evidence.
- [x] Add a dashboard callout when the latest Inspector report is stale and a one-click "Run Inspector now" workflow is available.

## Mailroom Protocol

- [ ] Define PAH mailbox protocol v3 for CD/CC/Codex: check mail, report counts, mark read, archive read, and report no-mail claims through PAH-visible events.
- [ ] Require agent replies to include mailbox check summary: inbox scanned count, message IDs read, message IDs archived, skipped IDs, and reason for each skip.
- [ ] Make the mailbox check summary rule explicitly normative for CC as well as Codex/CD-facing PAH workflows; it must catch incomplete enumeration, not only false no-mail claims.
- [x] Add no-mail claim validation: when an agent says "no mail", PAH compares that claim against active inbox state and logs pass/fail.
- [ ] Add explicit read receipt message or state record for each agent-managed inbox read outside the PAH UI.
- [ ] Add route-test ping/reply protocol for CD and CC, with automatic mismatch detection when replies are missing or archived incorrectly.
- [x] Notify CD of the Phase 4 draft restore and `drafted_pending_*` archive-skip rule.
- [x] Notify CC of the `drafted_pending_*` archive-skip rule for the next mailbox protocol sync.

## Classifier / Message State

- [ ] Review current owner-unknown items and either fix malformed frontmatter or add safe classifier rules for known valid legacy formats.
- [ ] Add tests for every completion/ack/report/status combination that should close before generic agent ownership.
- [ ] Add tests for ready-for-review/report combinations that must remain open on the reviewing agent.
- [x] Add classifier transition logging whenever a thread changes between open-on-agent, open-on-Darrin, owner-unknown, parked, and closed.
- [x] Treat explicit coordination-only no-action shares as closed/informational so Inspector does not create false Codex work from awareness mail.
- [x] Make stale-unread wake candidates classifier-aware and thread-aware: only open-on-agent/owner-unknown unread items wake, and older unread messages in completed threads are suppressed.
- [ ] Add a "why classified this way" explanation field in action detail for each open/unknown thread.

## Archive / Read Handling

- [x] Add a batch test that creates multiple unread/read messages in every active inbox, marks a subset read, runs archive sweep, and verifies every read item is removed and archived.
- [x] Add a guard that prevents auto-archiving unstructured or owner-unknown messages until PAH can prove the message is safe to archive.
- [x] Add a guard that prevents auto-archiving or alert-deleting `status: drafted_pending_*` pre-staged trigger messages.
- [x] Add a guard that prevents auto-archiving read but still-active agent-owned threads without completion evidence.
- [ ] Add archive restore tooling for accidental archive moves.
- [x] Add archive conflict reporting when destination names collide and PAH has to create a unique filename.
- [ ] Add inbox cleanup dry-run report to the dashboard before manual cleanup actions.

## Steward / Monitoring

- [x] Make the periodic steward emit a concise dashboard status card: last run, result, archived count, discrepancy count, and failed checks.
- [x] Add next scheduled run timestamp once the recurring automation schedule is exposed to PAH.
- [ ] Add automatic escalation rules for repeated discrepancies across two or more steward runs.
- [ ] Add self-healing startup check: if PAH is not listening on 8765, start it with known-good Python runtime and write stdout/stderr to stable logs.
- [ ] Add startup failure diagnostics that surface recent stderr/stdout in the dashboard.
- [ ] Add automated periodic route checks that send test messages to CD and CC and verify reply visibility plus archive behavior.
- [ ] Add test coverage for the periodic automation prompt/protocol so future automation edits preserve archive-read and discrepancy checks.
- [ ] Implement CC active-dispatch progress watchdog from the v0.2 monitoring spec, including `_state/active_dispatch.json`, allowlisted target paths, child-file mtime evidence, warning/error thresholds, and dashboard status cards.
- [ ] Fold CD-approved v0.2 monitoring amendments into implementation: first-class `recommended_action` on progress cards, retained healthy/stalled ASCII tile contract, M1 CC watchdog plus M2 mailbox SLA in MVP-of-MVP, default stale warn/error thresholds of 30/45 minutes, and formal `compose` / `heavy_write` states.
- [x] Add `ready_for_human_loop` to the CC progress sidecar state list so durable ready-to-commit/ready-for-go mailbox evidence can suppress stale-file and compose-cap alarms while CC waits on Darrin.
- [x] Upgrade PAH Inspector to validate `_state/active_dispatch.json` existence/readiness, JSON schema, required fields, allowed status values, and safe target-path allowlisting.
- [x] Add dedicated Claude Code Activity dashboard panel with Check Now, sidecar age, target disk-write age/path, mailbox fallback write age/path, target count, scanned-file count, issues, and recommended action.
- [ ] Upgrade PAH Inspector to validate `_state/active_dispatch.json` sidecar freshness against status-specific thresholds.
- [ ] Upgrade PAH Inspector to test CC progress evidence: newest child-file mtime under target paths, ignored cache/build folders, missing target paths, and stale warning/error threshold transitions.
- [ ] Upgrade PAH Inspector to verify false-positive guards for CC monitoring: paused, blocked, complete, abandoned, heavy-write, and non-file-progress states must not create incorrect stall alerts.
- [ ] Upgrade PAH Inspector to verify Agent Progress dashboard wiring: yellow/red progress cards are clickable, open action detail, show evidence/reason/threshold, and expose copy escalation/open-folder actions where safe.
- [ ] Upgrade PAH Inspector to verify CC-stall escalation behavior: red alerts route correctly, repeated alerts are deduplicated by dispatch/severity/evidence signature, and CD/Codex notification policy is honored.
- [ ] Add smoke-test fixtures for CC progress monitoring in a temporary PAH sandbox so tests never touch real PG target directories.

## UI / UX

- [x] Surface interaction ledger health in the top status panel with a drilldown link.
- [x] Add a main-screen Inspector button that opens a full-screen PAH Inspector panel with latest report summary, findings, Markdown report, and report-open action.
- [x] Add Inspector at-a-glance status graphics and color-coded action buttons while keeping PG Design Bible colors/fonts.
- [x] Make Inspector status graphics and chips clickable so PASS/WARN/FAIL reorder the findings list and OVERALL restores severity order.
- [x] Add one-click Run Inspector in the Inspector panel and footer stale-report callout, with cached health folded into the top Queue health chip.
- [ ] Add visual status for unresolved communication backlog: open-on-agent, owner-unknown, stale unread, and Darrin-waiting.
- [ ] Add one-click "copy discrepancy summary" for sending concise status to CD/CC.
- [ ] Add collapsible advanced diagnostics so the default dashboard stays clean but the details are nearby.
- [ ] Continue aligning dashboard typography, density, controls, and colors to the PG design system.
- [x] Re-align PAH root font/color tokens with the PG Design Bible: UI prose uses `--font-ui`, mono is reserved for exact data, warning is `#f39c12`, and alert panels stay on the dark navy/error surface instead of pale backgrounds.
- [x] Re-align Inspector and PAH status surfaces with the PG Design Bible: status uses semantic border/text/dot treatment while backgrounds stay on the dark navy surface tokens.
- [ ] Add visual regression screenshots for PAH alert/notice states at live desktop width so font/background drift is caught before handoff.

## Backup / Release Hygiene

- [ ] Commit and push PAH reliability changes after the active mailbox/protocol work is stable.
- [ ] Add a pre-commit or release checklist: py_compile, smoke tests, live `/api/health`, periodic steward run, and GitHub backup status.
- [ ] Keep generated logs/state out of commits unless they are intentional fixtures or docs.
- [x] Document PAH operational protocols in the README: live URL, server start command, health checks, archive-read behavior, and ledger location.
- [ ] At the end of every PAH implementation or incident-response pass, update durable PAH docs with what was learned, what changed, verification run, remaining risk, and any follow-up work. Use README for operations, TODO for follow-ups, and spec docs for product/UX/protocol/acceptance rules.

## Recent PAH Pass Notes

- 2026-05-02 mediated messaging implementation pass: added Phase 0 state-builder timing, message parse-cache and validation-cache metrics, `/api/ready`, snapshot-backed fast `/api/health`, mediated-messaging health component, exact `complete_pending_cd_review` and Darrin authority-boundary classifier tests, readiness-first server smoke, and a sanitized Phase 1 shadow snapshot at `CODEX state\CODEX_pah_mail_state_snapshot.local.json`. Verification passed: `py_compile`, `CODEX_run_smoke_tests.py`, `CODEX_run_server_smoke.ps1`, and offline `CODEX_pah_inspector.py` (`23 pass`, `1 warn`, `0 fail`). Latest profile: `/api/health` around 260ms in server smoke, cockpit state build around 1.6s with fast validation mode, and `validate_mailbox` reduced from about 7.4s to about 22ms on the cockpit hot path. Remaining hot-path targets are message audit, cached diagnostics, load messages, and list serialization before full snapshot switch-over.
- 2026-05-02 follow-up hot-path closeout: cockpit now uses `message_audit_summary` instead of the side-effectful `audit_messages_and_thread_states` step, preserving full audit/ledger behavior for explicit audit flows while keeping dashboard refresh read-only. Stale periodic-health reports older than 30 minutes now surface as stale warnings and no longer keep current `/api/health` red. Final live restart on `8765` returned `/api/ready` 41ms, `/api/health` 50ms from the mail-state snapshot, and `/api/cockpit` 949ms with `validation_mode=fast_no_schema` and `message_audit_mode=skipped_hot_path`.
- Added silent tray behavior for PAH overdue/notification-log popups: tray menu now labels these popup paths as disabled and the notification timer is not started.
- Added `/api/run-inspector` plus a PAH Inspector "Run Inspector" button so the UI can refresh Inspector evidence without a terminal.
- Stale Inspector health now contributes to the top Queue health cue and footer callout, keeping cached evidence from looking current.
- Added a Health Attention strip with the top PAH warning causes, direct jumps to queue/diagnostics/Inspector, and one-click copy of a concise status summary.
- Verification run: Python compile passed, UI JavaScript parse check passed, PAH smoke tests passed, PAH validator passed, temporary-server `/api/run-inspector` returned fresh warn-only Inspector output (`41 pass`, `3 warn`, `0 fail`), restarted live PAH on `8765` returned the same fresh warn-only result, and live Chrome screenshot QA confirmed the Health Attention strip renders without obvious overlap at desktop width.
- Remaining risk: overall PAH health can still be warn/err because real mailbox backlog, owner-unknown items, CC sidecar absence, and stale unread protocol items remain outside this UI/runtime fix.
