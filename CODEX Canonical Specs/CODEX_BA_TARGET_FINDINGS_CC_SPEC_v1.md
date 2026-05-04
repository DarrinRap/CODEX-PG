# CODEX BA Target Findings CC Spec v1

Status: Draft for Claude Code implementation planning
Date: 2026-05-04
Owner: Codex
Audience: Claude Code
Primary repo: `C:\panda-gallery`
Coordination repo: `C:\CODEX PG`

## 1. Purpose

This spec gives Claude Code a gated, high-detail plan for resolving and triaging the current Bible Audit target findings after Codex added direct BA targets for Tracker and Inspector.

It covers four workstreams:

1. PAH runtime BA failures.
2. PANDA Collaborator action-control coverage gap.
3. Relay RS-7 ESC-close failure.
4. Tracker and Inspector BA lint/action finding triage.

This spec does not authorize implementation by itself. Claude Code must complete Step 0, file an RTC, and wait for Darrin's explicit `go` for each implementation phase unless Darrin gives a narrower direct instruction.

## 2. Current Baseline

### 2.0 Push Prerequisite

Before dispatching implementation that depends on the new `Tracker` and `Inspector` BA targets, confirm whether commit `bd1b377` has been pushed. If it has not been pushed, Darrin should either push it or explicitly tell CC to work from the local unpushed commit.

Do not assume CC/CD can see the new BA targets in a fresh session until the commit is pushed or the local workspace state is confirmed.

### 2.1 Commit Baseline

The BA manifest target registration is committed in Panda Gallery:

`bd1b377 Add BA targets for Tracker and Inspector`

That commit adds:

- `Tracker` target: `audit_module/v1`
- `Inspector` target: `instruction_pane.py`, `instruction_pane_index_drawer.py`, `instruction_lint.py`

`C:\panda-gallery` may contain unrelated dirty work and validation artifacts. Claude Code must not clean, stage, revert, or fold unrelated dirty files into these tasks.

### 2.2 Latest BA Sweep

Codex ran the direct five-target BA sweep after adding Tracker and Inspector targets:

| Target | Result | Interpretation |
|---|---:|---|
| `PANDA Collaborator` | `0 fail / 0 warn / 1 unknown / 7 evidenced` | Trusted with findings; action-control coverage gap |
| `Panda Agent Hub` | `9 fail / 18 warn / 1 unknown / 63 evidenced` | Trusted with findings; runtime pack failing |
| `Relay` | `0 fail / 218 warn / 26 unknown / 15 evidenced` | Trusted with findings; large lint backlog |
| `Tracker` | `122 fail / 139 warn / 27 unknown / 12 evidenced` | Trusted with findings; large lint/action backlog |
| `Inspector` | `34 fail / 81 warn / 8 unknown / 8 evidenced` | Trusted with findings; large lint backlog |

BA infrastructure tests passed:

`64 passed`

Panda Gallery pre-commit passed during the manifest commit:

`1263 passed, 1 skipped`

### 2.3 Validation Context

CC's validation-completion RTC reported:

- Tracker: partially validated, expected failures for open bugs `#191` and `#184`.
- Inspector: validated, `98/98` pytest and `12/12` named V-ID checks.
- Relay: partially validated, `459/459` pytest and `6/7` RS checks; RS-7 unexpected failure.

Known Relay follow-up:

`RelayWindow` does not close on ESC, likely because `relay/relay_window.py` has no ESC handler. This is not currently fixed.

## 3. Global Rules

### 3.1 Approval and Commit Discipline

Claude Code must not:

- Commit without a Darrin commit-go.
- Push without explicit Darrin push-go.
- Batch unrelated dirty files into any commit.
- Use mailbox messages as implementation approval unless Darrin clearly granted that scope.
- Treat this spec as permission to modify all listed areas at once.

Each workstream needs its own RTC and its own explicit go unless Darrin intentionally combines them.

### 3.2 Repository Hygiene

Before any workstream:

1. Run `git status --short --branch` in `C:\panda-gallery`.
2. Identify unrelated dirty files.
3. Record which files the workstream is allowed to touch.
4. Do not clean generated validation artifacts unless Darrin explicitly authorizes cleanup.
5. Do not revert or overwrite work from other agents.

### 3.3 BA Truth Rules

BA output must remain evidence-backed.

Do not:

- Change thresholds to hide failures.
- Mark unknown evidence as trusted without a real scanner, runtime probe, or disposition.
- Delete lint findings from the report without fixing the underlying condition or narrowing the target intentionally.
- Convert a runtime failure into a pass unless the endpoint/probe actually passes.
- Weaken validator checks.

Do:

- Preserve selected-app boundaries.
- Keep `ba_report_validator.py` passing.
- Use disposition overlays only for honest classification: `confirmed_current`, `likely_current`, `heuristic_requires_trace`, `coverage_gap`, `expected_fail`, or equivalent existing values.

### 3.4 Test Commands

Unless a workstream says otherwise, run:

```powershell
cd C:\panda-gallery
python -m pytest tests\test_ba_audit_runner.py tests\test_ba_report_validator.py -q
```

After any BA target/scanner change, also run:

```powershell
python scripts\ba_audit_runner.py --list-apps
python scripts\ba_audit_runner.py --app "<TARGET>" --summary
python scripts\ba_report_validator.py --report workflows\design\applets\ba_audit_latest.json --expected-app "<TARGET>"
```

Use exact target names:

- `PANDA Collaborator`
- `Panda Agent Hub`
- `Relay`
- `Tracker`
- `Inspector`

## 4. Workstream A — PAH Runtime BA Failures

### 4.1 Goal

Resolve or correctly disposition the PAH runtime BA failures:

- `BA-RUNTIME-PANDA-AGENT-HUB-0001` Endpoint `/api/status`
- `BA-RUNTIME-PANDA-AGENT-HUB-0002` Endpoint `/api/cockpit`
- `BA-RUNTIME-PANDA-AGENT-HUB-0003` Endpoint `/api/health`
- `BA-RUNTIME-PANDA-AGENT-HUB-0004` Endpoint `/api/tray-status`
- `BA-RUNTIME-PANDA-AGENT-HUB-0005` Endpoint `/api/inspector-report`
- `BA-RUNTIME-PANDA-AGENT-HUB-0006` Endpoint `/api/cc-activity`
- `BA-RUNTIME-PANDA-AGENT-HUB-0007` Write protection
- `BA-RUNTIME-PANDA-AGENT-HUB-0008` Create-message dry-run endpoint
- `BA-RUNTIME-PANDA-AGENT-HUB-0009` Mailroom transaction canary

### 4.2 Hypothesis

The failures likely mean the PAH runtime check pack is probing `http://127.0.0.1:8765` while PAH is not running, is running on another port, or is running but not healthy. The validator trusts the report structure; the app itself is not proven healthy by this BA run.

The BA runner's default PAH Inspector URL is controlled by `BA_PAH_INSPECTOR_URL`; if unset, it defaults to `http://127.0.0.1:8765`. PAH's independent health checks in recent sessions have also used `http://127.0.0.1:8788/api/health`, so port mismatch must be checked before treating endpoint failures as application regressions.

### 4.3 Step 0 Required Reads

Claude Code must read:

- `C:\panda-gallery\scripts\ba_audit_runner.py`
- `C:\panda-gallery\scripts\ba_report_validator.py`
- `C:\CODEX PG\CODEX Agent Hub\CODEX_pah_inspector.py`
- `C:\CODEX PG\CODEX Agent Hub\CODEX_agent_hub.py`
- `C:\CODEX PG\CODEX Agent Hub\CODEX_agent_hub_ui.html`
- The latest PAH BA report at `C:\panda-gallery\workflows\design\applets\ba_audit_latest.json` if it still targets PAH; otherwise rerun PAH BA first.

### 4.4 Step 0 Questions To Answer

File an RTC answering:

- Is PAH running?
- Which port is live?
- Does `BA_PAH_INSPECTOR_URL` match the live PAH URL?
- Does PAH Inspector itself pass, warn, or fail when run directly?
- Are the nine runtime failures true app failures, environment failures, or probe/config failures?
- Are any of the static action warnings newly actionable, or are they heuristic-only?

### 4.5 Investigation Commands

Recommended commands:

```powershell
cd C:\CODEX PG\CODEX Agent Hub
python CODEX_pah_inspector.py
```

```powershell
cd C:\panda-gallery
$env:CODEX_PG_ROOT='C:\CODEX PG'
python scripts\ba_audit_runner.py --app "Panda Agent Hub" --summary
python scripts\ba_report_validator.py --report workflows\design\applets\ba_audit_latest.json --expected-app "Panda Agent Hub"
```

If the server should be live but is not, use the established PAH launch/smoke scripts from `C:\CODEX PG\CODEX Agent Hub`. Do not invent a new PAH launch path without reading local docs.

Also test the likely live health URL if PAH is expected on `8788`:

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8788/api/health' -TimeoutSec 5
```

### 4.6 Allowed Fixes

Allowed after go:

- Correct BA runtime probe URL configuration if stale.
- Start PAH using the existing local script if the task is validation-only and Darrin approves.
- Fix PAH endpoint bugs if the endpoint is genuinely broken and the fix is small.
- Improve BA diagnostic wording so "server unavailable" is not confused with "endpoint contract failed."
- Add or update PAH runtime-probe tests if they prove the exact behavior.

Not allowed without separate approval:

- Rewriting PAH routing.
- Changing mailbox write semantics.
- Changing write-protection rules.
- Weakening canary checks.

### 4.7 Acceptance Criteria

PAH workstream is complete when:

- PAH BA rerun produces either zero PAH runtime fails or an evidence-backed disposition explaining why fails are expected/current.
- `ba_report_validator.py` returns no errors/warnings/blocked.
- Any remaining static action warnings are classified as trace-required or fixed.
- No mailbox data, Relay files, or unrelated dirty files are modified.
- RTC lists exact command output and changed files.

## 5. Workstream B — PANDA Collaborator BA Coverage Gap

### 5.1 Goal

Resolve or correctly disposition:

`BA-ACTION-PANDA-COLLABORATOR-0000 PANDA Collaborator: No action controls discovered`

### 5.2 Hypothesis

The PC BA target currently scans only:

`C:\CODEX PG\CODEX PANDA Collaborator\panda_collaborator.py`

The production UI action controls likely live in:

`C:\CODEX PG\CODEX PANDA Collaborator\web\index.html`

Therefore the BA scanner may be looking at the backend entrypoint while missing the UI surface.

There is a timing dependency: PC UI redesign mockups are approved and locked, but implementation is explicitly deferred to a fresh CC session. This workstream must not start the redesign or alter UI behavior; it may only improve BA coverage over the current UI surface.

### 5.3 Step 0 Required Reads

Claude Code must read:

- `C:\panda-gallery\workflows\design\ba_audit_manifest.json`
- `C:\panda-gallery\scripts\ba_audit_runner.py`
- `C:\CODEX PG\CODEX PANDA Collaborator\panda_collaborator.py`
- `C:\CODEX PG\CODEX PANDA Collaborator\web\index.html`
- `C:\CODEX PG\CODEX PANDA Collaborator\PRODUCTION_SPEC.md`
- `C:\CODEX PG\CODEX PANDA Collaborator\PC_ACTION_TEST_SPEC.md`

### 5.4 Step 0 Questions To Answer

File an RTC answering:

- Are PC action controls in `web\index.html` omitted from the BA target?
- Would adding `web\index.html` to the PC BA target resolve the action-control unknown?
- Does the existing BA scanner understand HTML controls in external CODEX PG paths?
- Would a PC-specific scanner be required to avoid false positives?
- Does the PC UI redesign/mockup work change the timing of this fix?

### 5.5 Likely Fix

Preferred minimal fix:

Update the `PANDA Collaborator` BA target paths to include:

`"${env:CODEX_PG_ROOT}/CODEX PANDA Collaborator/web/index.html"`

Then rerun:

```powershell
cd C:\panda-gallery
$env:CODEX_PG_ROOT='C:\CODEX PG'
python scripts\ba_audit_runner.py --app "PANDA Collaborator" --summary
python scripts\ba_report_validator.py --report workflows\design\applets\ba_audit_latest.json --expected-app "PANDA Collaborator"
python -m pytest tests\test_ba_audit_runner.py tests\test_ba_report_validator.py -q
```

If adding `web\index.html` creates many new PC BA findings, that is still progress: it means the scanner now sees the action surface. Do not immediately fix those findings under this workstream unless Darrin explicitly expands scope. Report them as the next PC BA triage batch.

### 5.6 Acceptance Criteria

PC workstream is complete when:

- `PANDA Collaborator` no longer reports `No action controls discovered`, or the gap is explicitly proven to require a scanner enhancement.
- The PC BA report remains single-target and structurally trusted.
- No PC production behavior changes occur.
- No PC UI redesign implementation starts.
- RTC explains whether this was manifest-only or scanner work.

## 6. Workstream C — Relay RS-7 ESC-Close Failure

### 6.1 Goal

Create an evidence-backed follow-up bug and, if approved, fix:

Relay top-level window does not close on ESC.

### 6.2 Current Evidence

CC validation reported:

- `RelayWindow()` visible before ESC.
- `RelayWindow()` still visible after ESC.
- `relay/relay_window.py` contains no `Key_Escape`, `keyPressEvent`, or `QShortcut.*Escape` handling.
- Bible amendment claim says top-level module windows close on ESC.

Relay currently has unrelated dirty files in some sessions. Treat Relay as protected: do not stage, revert, clean, or overwrite existing Relay changes. If RS-7 requires editing a Relay file that is already dirty, inspect the diff first and explicitly state how the fix composes with the existing changes.

### 6.3 Step 0 Required Reads

Claude Code must read:

- `C:\panda-gallery\relay\relay_window.py`
- `C:\panda-gallery\relay\developer_hub.py`
- `C:\panda-gallery\scripts\relay_validate_b.py`
- `C:\panda-gallery\BUGS.md`
- PG Bible section/amendment governing ESC behavior, as referenced in validation RTC.
- Existing Relay tests under `C:\panda-gallery\tests\relay`

### 6.4 Step 0 Questions To Answer

File an RTC answering:

- Does Bible ESC-close rule apply to `RelayWindow`?
- Is `RelayWindow` always top-level, sometimes child-owned, or both?
- Should ESC close the window by `close()`, hide it, or delegate to parent?
- Is this a bug in Relay or a spec/Bible mismatch?
- What test should protect the behavior?

### 6.5 Bug Entry Requirement

Before fixing, create or propose a `BUGS.md` entry unless one already exists:

Title:

`Relay: ESC does not close RelayWindow`

Minimum body:

- Expected: ESC closes top-level Relay window per Bible ESC behavior.
- Actual: ESC leaves `RelayWindow` visible.
- Evidence: validation RTC, RS-7, missing ESC handler in `relay/relay_window.py`.
- Scope: Relay only.
- Risk: low to medium; keyboard accessibility and Bible compliance.

### 6.6 Likely Fix

Preferred implementation after go:

- Add a focused ESC close handler to `RelayWindow`.
- Avoid broad event-filter changes unless existing Relay architecture already uses them.
- Preserve child dialog ESC behavior.
- Add a test in `tests\relay\...` proving ESC closes/hides the top-level `RelayWindow`.
- Rerun Relay tests and Relay BA.

Candidate behavior:

```python
def keyPressEvent(self, event):
    if event.key() == Qt.Key.Key_Escape:
        self.close()
        event.accept()
        return
    super().keyPressEvent(event)
```

Use the repo's actual Qt import style and existing class patterns.

If the existing Relay dirty state makes a clean focused fix impossible, stop and ask Darrin whether to defer RS-7 until the Relay branch/worktree is clean.

### 6.7 Acceptance Criteria

Relay RS-7 workstream is complete when:

- `RelayWindow` closes on ESC in the applet/test.
- Relay tests pass.
- Relay BA still validates structurally.
- Any new `BUGS.md` entry is updated with disposition if fixed.
- No unrelated Relay dirty work is staged or reverted.

## 7. Workstream D — Tracker and Inspector BA Finding Triage

### 7.1 Goal

Do not mass-fix all Tracker and Inspector BA lint findings immediately. First classify them into actionable groups so fixes can be safely scoped.

Current direct BA results:

- Tracker: `122 fail / 139 warn / 27 unknown / 12 evidenced`
- Inspector: `34 fail / 81 warn / 8 unknown / 8 evidenced`

### 7.2 Step 0 Required Reads

Claude Code must read:

- `C:\panda-gallery\workflows\design\ba_audit_manifest.json`
- `C:\panda-gallery\scripts\ba_audit_runner.py`
- `C:\panda-gallery\workflows\design\applets\ba_audit_latest.json` after rerunning Tracker and Inspector separately.
- Tracker source under `C:\panda-gallery\audit_module\v1`
- Inspector source:
  - `C:\panda-gallery\instruction_pane.py`
  - `C:\panda-gallery\instruction_pane_index_drawer.py`
  - `C:\panda-gallery\instruction_lint.py`
- Relevant tests:
  - `tests\audit_module\test_tracker_ux_session129.py`
  - `tests\test_inspector_i1_rename.py`
  - `tests\test_inspector_i2_phases1_3.py`
  - `tests\test_inspector_i3_phases4_8.py`

### 7.3 Triage Output Required

Before fixes, produce a Markdown triage report with:

- Top 10 Tracker BA failure patterns by rule ID.
- Top 10 Inspector BA failure patterns by rule ID.
- Which findings are likely true UI/Bible defects.
- Which findings are scanner noise.
- Which findings are broad legacy style debt.
- Which findings are safe to fix mechanically.
- Which findings require design/spec decisions.
- Which findings overlap with known open bugs `#184` and `#191`.

Recommended report path:

`C:\panda-gallery\workflows\audit\BA_TRACKER_INSPECTOR_TRIAGE_YYYYMMDD.md`

The triage report is an artifact, not a fix. It may be committed only with an explicit commit-go and should not be mixed with source-code changes unless Darrin approves a combined commit.

### 7.4 Triage Commands

Rerun each target and save copies of results before summarizing:

```powershell
cd C:\panda-gallery
$env:CODEX_PG_ROOT='C:\CODEX PG'
python scripts\ba_audit_runner.py --app "Tracker" --summary
Copy-Item workflows\design\applets\ba_audit_latest.json workflows\audit\ba_tracker_latest.json
python scripts\ba_audit_runner.py --app "Inspector" --summary
Copy-Item workflows\design\applets\ba_audit_latest.json workflows\audit\ba_inspector_latest.json
```

Use structured JSON parsing, not manual copy/paste, to count rule patterns.

### 7.5 Fix Strategy After Triage

Preferred order:

1. Scanner-noise reductions that improve BA precision without weakening truth.
2. Small mechanical PG Bible fixes with low behavioral risk.
3. Action-feedback trace improvements where controls are real but scanner cannot prove feedback.
4. Larger UI refactors only after a separate design spec.

Do not do a broad visual restyle of Tracker or Inspector under this triage task.

### 7.6 Acceptance Criteria

Tracker/Inspector triage is complete when:

- Both targets have saved latest JSON snapshots.
- Triage report exists and groups findings by rule/pattern.
- No code fixes are made unless separately approved.
- The report recommends a next fix batch small enough to review.
- Existing Tracker and Inspector tests still pass if any code touched.

## 8. Suggested Execution Order

Recommended order:

1. Workstream A: PAH runtime BA failures.
2. Workstream B: PC action-control coverage gap.
3. Workstream C: Relay RS-7 ESC-close bug entry and fix proposal.
4. Workstream D: Tracker/Inspector BA triage report.

Reasoning:

- PAH runtime failures are concrete and operational.
- PC coverage gap is likely a small manifest/scanner issue.
- Relay RS-7 is a focused bug with validation evidence.
- Tracker/Inspector have large finding volumes and need triage before fixes.

## 9. Combined Final Deliverables

If Darrin authorizes all workstreams as one grouped effort, Claude Code must still produce sectioned output:

- PAH runtime findings/fixes and command results.
- PC BA coverage-gap disposition and command results.
- Relay RS-7 bug/fix disposition and command results.
- Tracker/Inspector triage report path and summary.
- Full changed-file list.
- Test commands and exact pass/fail summaries.
- Remaining risks.
- Commit recommendation with exact files to stage and exact files to leave untouched.

For every BA rerun, preserve the relevant target result before running the next target, because `workflows\design\applets\ba_audit_latest.json` is overwritten on each run. Use target-specific copies under `workflows\audit\` or another clearly named evidence folder.

## 10. Stop Conditions

Stop and ask Darrin before proceeding if:

- PAH runtime probes would require changing mailbox write behavior.
- PC action-control fix would require production UI changes.
- Relay RS-7 fix conflicts with an explicit Relay spec.
- Tracker/Inspector triage reveals hundreds of true visual defects that imply redesign rather than fixes.
- Any command would require cleaning, reverting, or deleting unrelated dirty work.
- Any fix would touch `C:\CODEX PG` generated mockups/manual artifacts outside the intended scope.

## 11. Suggested Dispatch Text

Use this when sending the task to CC:

```text
Read C:\CODEX PG\CODEX Canonical Specs\CODEX_BA_TARGET_FINDINGS_CC_SPEC_v1.md in full. Start with Step 0 only. Confirm whether bd1b377 is visible/pushed in your workspace, read the required files for Workstream A, and file an RTC with your classification of PAH runtime BA failures before making code changes. Do not touch unrelated dirty files, do not fix Relay RS-7 yet, and do not start Tracker/Inspector lint cleanup until explicitly authorized.
```
