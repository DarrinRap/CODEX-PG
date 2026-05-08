# CODEX PAH Excellent Final State Spec v1.0

Status: Self-reviewed draft
Owner: Codex
Scope: PAH only (`C:\CODEX PG\CODEX Agent Hub`)
Created: 2026-05-06

## Purpose

This spec defines the remaining work required to move PANDA Agent Hub (PAH) from operational and improving to excellent, final, and trustworthy as a project coordination cockpit.

The current state is functional but not final. PAH now runs on `http://127.0.0.1:8765`, smoke tests pass, the periodic health check exits successfully, and Inspector reports zero failures. Remaining warnings and transitional architecture mean PAH should be treated as operational but not complete.

## Non-Goals

- Do not change Panda Gallery app code.
- Do not change Relay files.
- Do not authorize Claude Code implementation or commit tokens from Codex.
- Do not stage, commit, revert, or clean parked unrelated files without explicit Darrin approval.
- Do not convert advisory backlog visibility into silence; coordination backlog must remain visible.

## Current Known State

Observed during the 2026-05-06 PAH backend verification pass. Counts are live operational values and may change as agents read, reply, or archive mail.

- PAH server listens on `127.0.0.1:8765`.
- PAH smoke tests pass.
- PAH periodic health check reports `ok: true`.
- Live `/api/health` reports `overall: warn`, not `ok`.
- PAH Inspector reports `42 pass, 2 warn, 0 fail`.
- Communication backlog remains present and advisory:
  - Open on agents: about 15
  - Open on Darrin: about 8
  - Owner unknown: 0
- Mail-state health uses `phase1_shadow_snapshot`, which is transitional.
- Git/GitHub backup health warns because the broader worktree is dirty.

## Final-State Definition

PAH is excellent and final only when all of the following are true:

1. Backend Reliability
   - PAH starts consistently on `127.0.0.1:8765`.
   - No duplicate or orphaned PAH server processes bind or contend for the canonical port.
   - Append-only ledgers do not use replace-based writes.
   - Periodic maintenance can run repeatedly without access-denied errors.

2. Health Semantics
   - `/api/health` distinguishes infrastructure failures from operational advisories.
   - Advisory backlog remains visible but does not produce infrastructure failure.
   - `overall: ok` is possible only when no warnings remain or every warning is explicitly accepted by policy.
   - `overall: warn` clearly explains non-blocking conditions.
   - `overall: err` is reserved for broken PAH infrastructure, failed critical diagnostics, missing required files, or stale core monitors.

3. Inspector Quality
   - Inspector reports `0 fail`.
   - Remaining warnings are either resolved or explicitly classified as accepted advisory conditions.
   - CC sidecar readiness warning is either fixed or documented as expected when CC has no active dispatch.

4. Mail-State Model
   - `phase1_shadow_snapshot` is replaced or formally accepted as the final projection model.
   - Snapshot warnings are not vague; each warning has a clear owner, meaning, and resolution path.
   - The snapshot file is small, sanitized, fresh, and sufficient for fast health, cockpit, and tray status.

5. Communication Backlog UX
   - PAH presents agent-owned, Darrin-owned, and owner-unknown work as separate operational queues.
   - Agent backlog produces nudge recommendations, not infrastructure errors.
   - Owner-unknown work remains a stronger warning because it indicates classification ambiguity; it becomes an error only if a documented threshold or critical-route rule is crossed.
   - Darrin-owned work remains visible without being treated as an agent failure.

6. Data Safety
   - Ledger, read-state, snapshot, and archive writes are append-safe or atomic as appropriate.
   - PAH has a documented recovery path for corrupt local JSON state.
   - PAH can run health checks while the server is live without file contention.

7. Backup and Release Hygiene
   - PAH-only changes are reviewed, backed up, committed, and pushed separately from unrelated parked work.
   - Dirty unrelated project files do not permanently obscure PAH-scoped backup status, while whole-repo dirt remains visible elsewhere.
   - PAH exposes whether its own changed files are backed up separately from broader repository dirt.

8. Test Coverage
   - Smoke tests cover health classification, advisory checks, append-only ledgers, snapshot contract, Inspector freshness, and route-critical diagnostics.
   - A repeat-run integration verification verifies two consecutive periodic checks pass while the live server is running.
   - Tests remain dependency-light and do not write to Panda Gallery app code.

## Required Enhancements

### E1: PAH-Scoped Backup Status

Problem:
The current health payload reports dirty Git/GitHub status for the whole `C:\CODEX PG` tree. This is useful but noisy when judging PAH itself.

Requirement:
Add a PAH-scoped backup component that reports whether files under `CODEX Agent Hub` are clean, dirty, staged, untracked, committed, and pushed.

Acceptance Criteria:
- `/api/health` includes a PAH-scoped backup subsection or separate component.
- The current whole-repo backup status remains available.
- PAH can report "PAH clean / broader repo dirty" distinctly.
- Untracked PAH files and folders are included in the PAH-scoped status with explicit path summaries.

### E2: Accepted Advisory Registry

Problem:
Inspector and health warnings are hard to interpret if they are expected transitional states.

Requirement:
Add a PAH-local registry for accepted advisory conditions. Each accepted advisory must include a condition id, reason, owner, timestamp, review-after date, and source evidence.

Acceptance Criteria:
- Accepted advisories are shown as accepted warnings, not hidden.
- Expired accepted advisories return to normal warning state.
- The registry lives under PAH state/config, not Panda Gallery app code.

### E3: CC Sidecar Readiness Clarification

Problem:
Inspector warns when `C:\panda-gallery\workflows\cc_mailbox\_state\active_dispatch.json` is absent. That may be a real problem during active CC dispatch, but expected when no dispatch is active.

Requirement:
Classify the sidecar warning based on whether PAH sees an active CC dispatch requiring sidecar state.

Acceptance Criteria:
- Missing sidecar with no active dispatch becomes `ok` or accepted advisory.
- Missing sidecar during active dispatch remains `warn` or `err` depending on severity.
- Inspector text explains the distinction.

### E4: Finalize Mail-State Snapshot Contract

Problem:
Fast health uses `phase1_shadow_snapshot`, which reads as transitional.

Requirement:
Either promote the snapshot model to a final named contract or define the next implementation step that replaces it.

Acceptance Criteria:
- Snapshot health no longer emits vague `shadow_snapshot_from_legacy_state` warnings without a clear final-state plan or accepted advisory record.
- Snapshot schema version and builder version are documented.
- Smoke tests cover the final contract name and authority model.

### E5: Repeat-Run Health Verification

Problem:
One successful periodic health run does not prove file contention is gone.

Requirement:
Add a PAH-only integration verification script that runs periodic health twice while PAH is live and confirms both runs succeed. Keep the default smoke suite dependency-light and usable without a live server.

Acceptance Criteria:
- The repeat-run check produces clear output.
- It does not require staging, commits, or Panda Gallery app writes.
- It catches append/replace contention regressions without making the default smoke suite depend on live local server state.

### E6: Health Level Policy Documentation

Problem:
The difference between `ok`, `warn`, and `err` is currently distributed across code.

Requirement:
Document the canonical PAH health policy in a PAH-local markdown file and link or reference it from relevant tests.

Acceptance Criteria:
- Policy states what is infrastructure failure versus operational advisory.
- Communication backlog is explicitly advisory unless owner-unknown work or stale critical routes cross a documented threshold.
- Critical route diagnostics remain hard failures.

### E7: UI Clarity For Non-Final State

Problem:
PAH can be operational while not final. Users need to see this without mistaking warning state for broken state.

Requirement:
Update PAH UI labels so health states communicate "operational with advisories" separately from "broken."

Acceptance Criteria:
- `warn` state copy is calm and specific.
- `err` state copy is reserved for real breakage.
- No new app code outside PAH is touched.

## Implementation Order

1. Add health policy documentation.
2. Add PAH-scoped backup status.
3. Add accepted advisory registry.
4. Clarify CC sidecar readiness.
5. Finalize or rename snapshot contract.
6. Add repeat-run health verification.
7. Polish PAH UI health wording.
8. Run full PAH smoke tests, Inspector, periodic health, and live `/api/health`.
9. With Darrin approval, commit and push PAH-only changes.

## Regression Risks

- Misclassifying a real infrastructure failure as advisory.
- Hiding actionable communication work.
- Making health `ok` while important state is stale.
- Allowing broader repo dirt to mask PAH-specific backup risk.
- Creating tests that depend on live local state and become flaky.

## Validation Plan

Run:

```powershell
python -m py_compile "C:\CODEX PG\CODEX Agent Hub\CODEX_agent_hub.py" "C:\CODEX PG\CODEX Agent Hub\CODEX_pah_periodic_health_check.py" "C:\CODEX PG\CODEX Agent Hub\CODEX_run_smoke_tests.py"
python "C:\CODEX PG\CODEX Agent Hub\CODEX_run_smoke_tests.py"
python "C:\CODEX PG\CODEX Agent Hub\CODEX_pah_inspector.py"
python "C:\CODEX PG\CODEX Agent Hub\CODEX_pah_periodic_health_check.py"
Invoke-RestMethod -Uri "http://127.0.0.1:8765/api/health" -TimeoutSec 8 | ConvertTo-Json -Depth 8
```

Expected:
- Smoke tests pass.
- Inspector has zero failures.
- Periodic health exits `0`.
- `/api/health` is `ok` or `warn` only for documented accepted advisories.
- Implementation edits remain under `C:\CODEX PG\CODEX Agent Hub`; validation may update existing PAH-managed logs/state and existing mailbox maintenance artifacts according to current PAH behavior.

## Done Definition

PAH can be called excellent and final when:

- PAH-only tests and health checks pass repeatedly.
- Live `/api/health` has no unexplained warnings.
- Inspector has no failures and no unexplained warnings.
- PAH-scoped backup status is clean, or every dirty/untracked PAH item is intentionally documented before release.
- Communication backlog is visible, actionable, and separated from infrastructure health.
- Darrin has reviewed and approved the final PAH state.
