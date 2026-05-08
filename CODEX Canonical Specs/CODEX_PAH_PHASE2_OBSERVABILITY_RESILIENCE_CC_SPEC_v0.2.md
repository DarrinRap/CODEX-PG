# CODEX PAH Phase 2 Observability and Resilience Spec v0.2

Created: 2026-05-07
Owner: Codex draft for Darrin/CD review; CC implementation only after CD authorization
Scope: PANDA Agent Hub observability, diagnostics, support bundle, backlog visibility, conflict explanation, and long-run validation
Revision: v0.2 incorporates CD review amendments from 2026-05-07: health-details schema version/access method, deterministic recovery journal retention, and PAH-related process definition.
Status: Draft v0.2 after CD review; not dispatched, not approved

## 1. Purpose

PAH is already close to strong operational shape, and the separate startup/tray/watchdog spec covers login startup, tray ownership, bounded restart, duplicate-process prevention, and lifecycle control. This Phase 2 spec adds the small amount of evidence and diagnostics needed to make PAH excellent in practice: when PAH is not healthy, busy, recovering, or blocked, it should explain why without requiring guesswork or terminal archaeology.

This is intentionally boring infrastructure work. The goal is not a new PAH cockpit, new workflows, or broader automation. The goal is reliable local visibility, safe diagnostics, and proof that PAH remains stable over time.

## 2. Relationship to Existing PAH Work

This spec complements but does not replace:

- `CODEX_PAH_STARTUP_TRAY_CC_SPEC_v0.1.md`, which owns startup, tray, watchdog, ownership, restart, duplicate detection, and tray lifecycle behavior.
- `CODEX_PAH_FUNCTIONALITY_UPDATE_SPEC_v1.0.md`, which owns mailbox-manager freshness rules, unread-dispatch policy, and broader PAH functionality updates.

If this spec conflicts with the startup/tray spec, the startup/tray spec wins for lifecycle behavior. If this spec conflicts with mailbox-manager protocol rules, the mailbox-manager protocol wins. This spec should only add observability and validation surfaces around those behaviors.

## 3. Goals

1. Make health state explainable, not just pass/fail.
2. Make backlog warnings actionable by distinguishing busy, degraded, and stuck states.
3. Record recovery events so restarts and transient failures can be reconstructed.
4. Provide a safe local support bundle for troubleshooting.
5. Detect startup and port conflicts clearly without killing unknown processes.
6. Add a long-run soak harness that proves PAH stays stable over hours.
7. Keep implementation small, testable, and isolated to PAH files.

## 4. Non-Goals

- Do not redesign the PAH dashboard.
- Do not add a new product UI or control panel.
- Do not duplicate startup/tray/watchdog implementation already specified elsewhere.
- Do not touch Relay files.
- Do not change mailbox protocol, CC/CD authorization rules, or commit-go routing.
- Do not stage, commit, revert, archive, or clean parked dirty files.
- Do not add external dependencies or network services; use existing PowerShell/Python/runtime patterns already present in PAH.
- Do not bind PAH outside `127.0.0.1`.
- Do not include mailbox bodies, secrets, tokens, private keys, or credentials in diagnostics or bundles.
- Do not make visible UI/UX changes, including dashboard text, tray labels, tray menu wording, icons, layout, or notification behavior, unless a mockup is presented to Darrin and approved first. CLI output, logs, JSON, and support-bundle text are not considered UI/UX for this rule.

## 5. Definitions

- **Healthy**: readiness and core health endpoints pass within timeout, no stale backlog warning, and no active recovery condition.
- **Busy**: backlog exists but is recent and moving; PAH is responsive.
- **Degraded**: PAH is responsive but one or more non-critical checks are failing or backlog age is concerning.
- **Stuck**: backlog age or repeated failures indicate work is not progressing.
- **Conflict**: expected PAH port is occupied by an unknown process or by a PAH-like process that does not respond correctly.
- **Recovery event**: a restart, failed restart, transition from unhealthy to healthy, or manual recovery action recorded for later diagnosis.
- **Support bundle**: a read-only local diagnostic export with secrets redacted.
- **PAH-related processes**: any process whose executable name or command-line matches CODEX_agent_hub.py, CODEX_start_agent_hub_tray.ps1, or CODEX_launch_agent_hub_dashboard.ps1, identified by name substring match via Get-Process. Command-line arguments must be sanitized before inclusion in support bundles or health details.

## 6. Required Behavior

### 6.1 Health Explainability

Add a structured PAH health-details payload that can be used by tray status, local scripts, soak validation, and support bundles. Access method is explicitly defined below as a local-only HTTP endpoint; existing endpoint consumers must remain backward compatible.

Required fields:

- timestamp
- PAH URL and port
- process PID if known
- ownership mode if known: owned, attached, unknown, conflict, or not_applicable
- version or commit SHA if available
- readiness result
- health result
- tray-status result if available
- cockpit/dashboard reachability if available
- backlog summary
- last successful health check timestamp
- last health failure timestamp
- last error class and sanitized message
- overall classification: healthy, busy, degraded, stuck, down, conflict, or unknown
- short human-readable reason
- timeout used for each probe, defaulting to a bounded local timeout of approximately 5 seconds unless existing PAH conventions differ

Access method:

- Provide GET /health/details on the PAH server as a local-only endpoint bound to 127.0.0.1 only.
- Return the health-details payload as JSON.
- Step 0 must verify this does not conflict with the startup/tray spec or existing PAH endpoint conventions.
- The support bundle script and soak validation script should use this endpoint when PAH is running, while still producing useful local evidence when PAH is down.

Acceptance criteria:

- A user can tell why PAH is not simply healthy.
- A failure state includes the failing subsystem and last known good timestamp when available.
- Error messages are sanitized and do not include secrets, mailbox bodies, or full environment dumps.

### 6.2 Backlog Visibility

Add lightweight backlog metrics to the health-details payload if PAH has backlog-like work to track.

Required metrics when available:

- total pending count
- oldest pending age
- newest pending age
- age buckets: `<5m`, `5-30m`, `30-60m`, `60m+`
- failed/error count
- last completed timestamp if available
- moving/not moving indicator if comparable across samples; if no reliable prior sample exists, report `unknown` rather than guessing

Classification guidance, with exact thresholds to be confirmed in CC Step 0 if existing PAH conventions differ:

- `busy`: pending work exists, oldest age is below warning threshold, and completion is moving.
- `degraded`: backlog is aging, errors are present, or motion is unclear; default threshold suggestion is oldest pending item over 30 minutes.
- `stuck`: oldest item exceeds the stale threshold or repeated samples show no progress; default threshold suggestion is oldest pending item over 60 minutes or 3 consecutive unchanged samples.

Acceptance criteria:

- Existing generic backlog warnings become actionable.
- The implementation must tolerate missing backlog data and report `not_available` rather than failing health checks.

### 6.3 Recovery Journal

Write recovery and health-transition events to a local JSONL journal under the PAH logs area.

Required event fields:

- timestamp
- event type: health_transition, restart_attempt, restart_success, restart_failed, manual_recovery, conflict_detected
- prior classification
- new classification
- trigger reason
- PID and port if known
- action attempted, if any
- action result
- first successful health timestamp after recovery, if applicable
- sanitized error summary, if applicable

Rules:

- Log only transitions and recovery events, not every poll.
- Retain the most recent 1,000 recovery journal events using rotate-on-write semantics: when writing event 1,001, drop the oldest event and keep the newest 1,000. Do not use file-size-based retention for this phase.
- Do not log secrets, mailbox bodies, raw environment variables, or full stack traces unless sanitized.
- If the startup/tray spec already adds a lifecycle or health transition log, reuse or extend that file format rather than creating duplicate journals.

Acceptance criteria:

- After a restart or recovery, the reason and result are visible in one place.
- A support bundle includes the recent recovery journal.

### 6.4 Support Bundle

Add a local support-bundle script or command. It must be read-only with respect to PAH runtime state.

Suggested file:

- `C:\CODEX PG\CODEX Agent Hub\CODEX_collect_pah_support_bundle.ps1`

Bundle contents:

- current health-details JSON
- recent PAH server log excerpts, if present; missing logs must not fail bundle generation
- recent tray/lifecycle/recovery log excerpts, if present; missing logs must not fail bundle generation
- config summary with secrets redacted
- process snapshot for PAH-related processes, with command-line arguments sanitized before bundle export
- port snapshot for the configured PAH port
- version/commit SHA if available
- recent validation report paths if present
- README text explaining what is included

Rules:

- Write bundle under a local diagnostics/output folder, not a mailbox.
- Redact secrets and credentials.
- Do not include mailbox message bodies.
- Do not include raw process command lines if they contain tokens, credentials, or private paths beyond the PAH/CODEX PG working tree; summarize or redact instead.
- Do not start, stop, restart, or mutate PAH while collecting the bundle.
- Keep bundle size bounded by limiting log excerpts.

Acceptance criteria:

- Running the support-bundle command succeeds when PAH is healthy.
- Running it when PAH is down still produces useful process, port, and log evidence.
- The bundle path is printed clearly at the end.

### 6.5 Startup and Port Conflict Explanation

The startup/tray spec owns conflict handling. This spec adds clearer diagnostics around those conflicts.

Required conflict classifications:

- configured port free
- configured port occupied by expected PAH process
- configured port occupied by unknown process
- PAH process exists but health endpoint unreachable
- multiple PAH-like processes detected
- tray attached to already-running PAH

Acceptance criteria:

- Conflict diagnostics never kill or restart unknown processes.
- The status summary recommends the next safe action, such as close unknown process, change configured port, or inspect logs.
- If startup/tray code already reports the conflict, health-details and support bundle must include the same classification.

### 6.6 Long-Run Soak Validation

Add a non-invasive soak validation script.

Suggested file:

- `C:\CODEX PG\CODEX Agent Hub\CODEX_pah_soak_check.ps1`

Required behavior:

- Poll PAH health at a configurable interval.
- Default interval: 5 minutes.
- Default duration: 8 hours.
- Record response latency, HTTP/result status, classification, PID if known, and memory/process snapshot if available.
- Record failures without stopping the soak unless explicitly configured.
- Produce a final summary with sample count, failure count, min/median/max latency, longest unhealthy streak, classification counts, and output path.

Rules:

- The soak script must not restart PAH.
- The soak script must not modify mailbox files.
- The soak script must not require administrator rights.
- The output must be small enough for routine review.

Acceptance criteria:

- A multi-hour run can distinguish stable PAH, intermittent endpoint failure, memory growth, and persistent down state.
- The report is useful even if PAH is down for the entire run.

## 7. Proposed Files

Likely implementation files, subject to CC Step 0 confirmation:

- `C:\CODEX PG\CODEX Agent Hub\CODEX_agent_hub.py`
- `C:\CODEX PG\CODEX Agent Hub\CODEX_start_agent_hub_tray.ps1` only if needed to expose existing tray/lifecycle evidence; do not reimplement lifecycle behavior owned by the startup/tray spec
- `C:\CODEX PG\CODEX Agent Hub\CODEX_launch_agent_hub_dashboard.ps1` only if needed to surface diagnostics; do not change launch semantics owned by the startup/tray spec
- `C:\CODEX PG\CODEX Agent Hub\CODEX_collect_pah_support_bundle.ps1`
- `C:\CODEX PG\CODEX Agent Hub\CODEX_pah_soak_check.ps1`
- focused tests or validation scripts under the PAH folder if existing patterns support them

Do not modify Relay files or unrelated CODEX PG files.

## 8. Implementation Order

1. Step 0 RTC only: CC reports exact files, existing health endpoints, proposed log/bundle names, and any ambiguity.
2. Add health-details data model and local retrieval path.
3. Add backlog metrics where data exists; tolerate unavailable data.
4. Add recovery journal extension, reusing startup/tray logs if available.
5. Add conflict explanation to health details and bundle output.
6. Add support-bundle script.
7. Add soak validation script.
8. Run focused validation and report evidence before any commit request.

## 9. Validation Plan

Required checks:

- Existing PAH smoke tests still pass.
- Existing server smoke still passes.
- Existing live endpoint verification still passes when PAH is running.
- Health-details output validates as structured JSON.
- Support bundle can be generated while PAH is running.
- Support bundle can be generated while PAH is down.
- Support bundle, health-details, and soak validation do not install/remove startup shortcuts, change tray config, or mutate mailbox files.
- Conflict classifier can identify a non-PAH listener on the PAH port without killing it, if safely reproducible; any test listener must be created and cleaned up by the test itself, never by terminating an unrelated existing process.
- Soak script can run a short test mode, such as 3 samples at 10-second intervals, before any overnight run.

Recommended commands, adjusted by CC Step 0 if file names differ:

```powershell
python "C:\CODEX PG\CODEX Agent Hub\CODEX_run_smoke_tests.py"
& "C:\CODEX PG\CODEX Agent Hub\CODEX_run_server_smoke.ps1"
python "C:\CODEX PG\CODEX Agent Hub\CODEX_pah_live_endpoint_verify.py"
& "C:\CODEX PG\CODEX Agent Hub\CODEX_collect_pah_support_bundle.ps1"
& "C:\CODEX PG\CODEX Agent Hub\CODEX_pah_soak_check.ps1" -DurationMinutes 1 -IntervalSeconds 10
```

## 10. Acceptance Criteria

PAH Phase 2 is acceptable only if:

- Health status explains the reason for unhealthy, degraded, busy, stuck, conflict, and down states.
- Backlog warnings include counts or explicitly say backlog data is unavailable.
- Recovery events are recorded without log spam.
- Support bundle is read-only, redacted, bounded, and useful when PAH is both up and down; it must not expose sensitive command-line arguments.
- Conflict explanation is conservative and never kills unknown processes.
- Soak script produces a concise stability report.
- Existing PAH smoke/live checks still pass.
- No Relay files, mailbox authorization files, parked dirty files, or unrelated files are modified.
- Any visible UI/UX change had a mockup approved by Darrin first; command-line output, logs, support-bundle README text, and JSON fields are allowed without a visual mockup.

## 11. Risks

- Health explainability can become noisy if every transient timeout becomes a major warning.
- Backlog data may not exist in a clean structured form; implementation must not invent unreliable metrics.
- Support bundles can accidentally collect too much; redaction and size limits are required.
- Conflict detection on Windows can be brittle; unknown processes must be treated conservatively.
- Soak checks can create misleading confidence if only run briefly; short mode is for script validation, long mode is for confidence.

## 12. Approval Boundary

This spec is draft-only until Darrin approves it and CD dispatches CC. Codex may audit, recommend, summarize, and route through CD, but Codex must not send implementation-go or commit-go directly to CC for PAH work.





