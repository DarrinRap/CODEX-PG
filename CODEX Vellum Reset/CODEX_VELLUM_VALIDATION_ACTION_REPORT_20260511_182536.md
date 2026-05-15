---
schema_version: 1
message_id: 20260511_182536_CODEX_to_CD_vellum_validation_action_report
thread_id: VELLUM-VALIDATION-20260511
from: CODEX
to: CLAUDE
date: 2026-05-11T18:25:36-07:00
subject: ACTION REPORT - Fresh Vellum validation, bugs, BA status, and recommended routing
status: open
type: validation_report
priority: high
---

# Fresh Vellum Validation - Actionable Report

CD,

Darrin asked CODEX to check Vellum for bugs/validation. I ran a fresh Vellum-only validation pass and preserved all logs/artifacts. No app code was edited, no watchers/tray/PAH were restarted, and no CC routing or commit-go was issued.

## Evidence Root

`C:\CODEX PG\CODEX Vellum Reset\evidence\vellum_validation_20260511_182343`

Key files:

- `VELLUM_VALIDATION_SUMMARY_20260511_182343.md`
- `pytest_tests_k_vellum.log`
- `ba_audit_vellum_plain.json`
- `ba_audit_vellum_plain_summary.log`
- `ba_report_validator_vellum_gate.json`
- `ba_report_validator_vellum_gate.log`
- `pg_design_lint_vellum_approval.json`
- `vellum_smoke_test.log`

## Executive Status

Vellum is not currently validation-clean.

Good news: the targeted pytest Vellum regression floor is green, and BA report validation says the BA report is trusted/reproducible.

Bad news: BA is trusted-with-findings, direct applet lint still has warnings, the live Vellum smoke script fails and aborts early, and the known one-screen ApprovalReviewPanel visible proof remains unresolved until the queued layout fix lands.

## Test Matrix

| Validation | Command | Result | Meaning |
|---|---|---:|---|
| Targeted Vellum pytest | `python -m pytest tests -k vellum -q` | PASS: 149 passed, 4 xfailed, 1055 deselected | Code-level Vellum regression floor is intact. |
| BA single-app Vellum audit | `python scripts\ba_audit_runner.py --app Vellum --summary` | 0 fail / 147 warn / 32 unknown / 9 evidenced | BA found no hard failures, but Vellum is not BA-green. |
| BA gate validation | `python scripts\ba_report_validator.py --report <artifact> --expected-app Vellum --gate` | PASS verdict: `report_trusted_with_findings`, no reproduction drift | BA findings are current/reproducible; not stale noise. |
| Direct approval applet lint | `python -m pg_design_lint workflows\design\applets\vellum_approval --json` | 0 errors / 25 warnings / 10 info | Focused applet has no lint errors but real warning debt. |
| Live Vellum smoke | `python scripts\vellum_smoke_test.py` | FAIL: 20/31 passed, 11 failed, then AttributeError | Smoke cannot be used as a ship gate until repaired. |

## BLOCKERS

### BLOCKER 1 - Vellum smoke script is stale and aborts before completing validation

Evidence: `vellum_smoke_test.log`

Observed result:

- Smoke reached only 31 checks before aborting.
- Result before abort: `20/31 passed, 11 failed`.
- Hard exception:
  - `AttributeError: 'MarkupToolbar' object has no attribute '_width_combo'`
  - Location: `scripts/vellum_smoke_test.py`, `test_width_combo()`.

Failed smoke checks before abort:

- `Default width is 1280` failed. Actual this run: `1281x900`.
- Tooltip length checks failed for these toolbar tools:
  - Select: tooltip length 10
  - Pen: length 7
  - Line: length 8
  - Rect: length 8
  - Oval: length 8
  - Arrow: length 9
  - Text: length 8
  - Callout: length 7
  - Snippet: length 11
  - Eraser: length 10

Assessment:

- This is primarily a validation-infrastructure blocker, not proof that every related app behavior is broken.
- The script expects an older toolbar API/contract (`_width_combo`) that is absent from current `MarkupToolbar`.
- The tooltip assertions may reveal real UX/help debt, but the hard abort means the smoke suite cannot complete enough of the app to serve as a trusted gate.

Actionable recommendation:

- Create/route a separate CC validation-fix ticket after current higher-priority Vellum sequencing allows it.
- Scope should be one of:
  1. Update `scripts/vellum_smoke_test.py` to match the current toolbar API, including the replacement for `_width_combo`; or
  2. Restore a width-control contract on `MarkupToolbar` if the app is supposed to expose that control.
- Keep this separate from the ApprovalReviewPanel one-screen layout fix. Mixing smoke-infra repair into product layout work will blur evidence.
- Acceptance: smoke script completes all intended sections without traceback and reports deterministic pass/fail counts.

Severity: BLOCKER for smoke-as-gate. MUST-FIX-BEFORE-DEMO only if CD intends smoke to be a demo gate.

### BLOCKER 2 - One-screen ApprovalReviewPanel proof remains unresolved

Evidence already on disk:

- Screenshot: `C:\CODEX PG\CODEX Vellum Reset\evidence\20260511_vellum_one_screen_viewer_normal_v2_pyside_1280x900.png`
- Metadata: `C:\CODEX PG\CODEX Vellum Reset\evidence\20260511_vellum_one_screen_viewer_normal_v2_pyside_1280x900.json`
- Delta report: `C:\CODEX PG\CODEX Vellum Reset\CODEX_VELLUM_ONE_SCREEN_DELTA_REPORT_20260511_104647.md`
- Approved spec draft: `C:\CODEX PG\CODEX Vellum Reset\CODEX_VELLUM_ONE_SCREEN_CC_FIX_SPEC_DRAFT_20260511_124736.md`

Current known status:

- Canonical proof size is `1280 x 699`.
- Frozen target is `viewer_normal_v2`, 100% actual-size mode.
- Current screenshot proves the canvas/item/decision state, but not the complete one-screen approval workflow.
- Required elements still not all visible in one screenshot until the approved ApprovalReviewPanel layout fix lands:
  - Darrin notes area
  - decision controls
  - checklist
  - handoff ready/blocked reason
  - BA preflight badge

Assessment:

- This remains the primary product-visible Vellum blocker.
- CD previously approved the narrow fix spec, queued after the relevant CC sequencing.
- Fresh validation does not change the scope: the next product-facing Vellum work should still be ApprovalReviewPanel layout/ordering only.

Actionable recommendation:

- Keep the approved one-screen layout spec as the next Vellum product fix.
- After CC returns the fix, re-run exactly:
  - fresh PySide screenshot at `1280 x 699`
  - `python -m pytest tests -k vellum -q`
  - `python scripts\ba_audit_runner.py --app Vellum --summary`
  - `python scripts\ba_report_validator.py --report <report> --expected-app Vellum --gate`
  - direct `pg_design_lint` on `workflows\design\applets\vellum_approval`
  - smoke only if smoke script has been repaired or CD explicitly accepts its current stale status.

Severity: BLOCKER for one visible, trustworthy Vellum result.

## MUST-FIX / TRIAGE FINDINGS

### Finding 3 - Vellum BA is trusted-with-findings, not BA-green

Evidence:

- `ba_audit_vellum_plain.json`
- `ba_report_validator_vellum_gate.json`

Fresh BA totals:

- Fail: 0
- Warn: 147
- Unknown: 32
- Evidenced pass: 9
- Evidence score: 5.8%
- Coverage debt: 17.0%
- Gate validator verdict: `report_trusted_with_findings`
- Reproduction drift: none

Meaning:

- BA report structure and evidence chain are valid.
- The non-pass findings are reproducible/current under BA's own validator.
- Vellum must not be described as BA-green.

Top BA finding groups from this run:

- R26 warning: mode-zone color locality warnings
- R04 warning: off-scale spacing values
- R18 warning: off-scale border-radius values
- R03b warning: native `QFileDialog` usage
- R28 info/unknown: inline dynamic counts should be split to second line
- R19 info/unknown: empty-state copy may lack Bible tutorial voice pattern
- Workflow-order proof gaps: unknown coverage rows

Actionable recommendation:

- Do not expand scope to broad BA cleanup before the one-screen proof fix unless Darrin/CD explicitly chooses BA cleanup as the next lane.
- After one-screen proof, triage BA warnings into:
  - must-fix-before-demo: native dialogs if user-visible in demo path, any visible mode-zone/color problem in ApprovalReviewPanel proof path
  - defer: broad spacing/radius polish not affecting first proof
  - known limitation: intentionally deferred native dialog replacement if already documented

Severity: MUST-FIX-BEFORE-BA-GREEN. Defer broad cleanup until after one-screen proof unless CD reorders.

### Finding 4 - Direct Vellum approval applet lint has no errors but warning debt increased slightly

Evidence: `pg_design_lint_vellum_approval.json`

Fresh result:

- Files scanned: 10
- Errors: 0
- Warnings: 25
- Info: 10

Notable direct lint groups:

- R04 spacing warnings in `widgets.py` and `split_view.py`
- R18 radius warnings in `widgets.py`
- R26 mode-zone color locality in fixture generator / split view / widgets
- R03b native `QFileDialog` in `split_view.py`
- R19 empty-state voice info across exporter/inbox/models/packet_io/queueing/split_view/widgets
- R28 inline dynamic count info in exporter/split_view/widgets

Representative direct findings:

- `workflows/design/applets/vellum_approval/split_view.py:35` - `QFileDialog` forbidden by R03b
- `split_view.py:458` and `split_view.py:474` - additional `QFileDialog` findings
- `widgets.py:151`, `168`, `173`, `183`, `214`, `219`, `221` - off-scale radii
- `widgets.py:340`, `429`, `430`, `614`, `691`, `740`, `817`, `845`, `878` - off-scale spacing
- `widgets.py:57`, `59` - mode-zone color locality warnings

Actionable recommendation:

- For the one-screen fix, avoid adding any new R04/R18/R26 debt inside `ApprovalReviewPanel`.
- If touching `widgets.py`, prefer tokenized/scale values and avoid new raw QSS values that BA will flag.
- Do not attempt to clear all 25 warnings as part of the first visible proof; keep the product fix narrow.

Severity: WARN for current product proof; MUST-NOT-WORSEN during the next layout fix.

## DEFER / KNOWN LIMITATIONS

### Finding 5 - Pytest Vellum suite is green

Evidence: `pytest_tests_k_vellum.log`

Result:

- 149 passed
- 4 xfailed
- 1055 deselected
- Runtime: 11.25s

Recommendation:

- Keep this as the baseline regression floor.
- Run it again after any ApprovalReviewPanel layout fix.
- Do not treat the green pytest result as visual proof; it does not cover the one-screen screenshot requirement.

Severity: PASS / regression floor.

### Finding 6 - BA validator history check warning is artifact-path related, not drift

Evidence: `ba_report_validator_vellum_gate.json`

Validator includes one warning:

- `BA-VAL-HISTORY-0001`: report is not the canonical latest artifact; history/progress check skipped.

Assessment:

- This appears because CODEX validates the copied artifact under the evidence folder, not the canonical live `ba_audit_latest.json` path.
- Reproduction completed with exit code 0 and no drift.

Recommendation:

- Treat the validator verdict as trusted-with-findings.
- No action needed unless CD requires the report path to be canonical for archival semantics.

Severity: INFO.

## Recommended Routing / Sequencing

1. Keep ApprovalReviewPanel one-screen layout fix as the next product-facing Vellum fix.
   - Scope already approved: layout/ordering inside `ApprovalReviewPanel` only.
   - Acceptance: required workflow elements visible in one `1280 x 699` PySide screenshot at 100% actual size.

2. Create a separate validation-infrastructure fix for `scripts/vellum_smoke_test.py`.
   - This should not block the one-screen product fix unless CD requires smoke as a gate.
   - Acceptance: smoke completes without traceback and has updated expectations for current toolbar API.

3. Do not claim Vellum is BA-green.
   - Use phrase: `BA trusted-with-findings`.
   - Broad BA cleanup should remain deferred unless CD/Darrin reopens it.

4. During the ApprovalReviewPanel fix, enforce a no-new-BA-debt constraint.
   - In `widgets.py`, use canonical spacing/radius/color tokens or existing accepted patterns.
   - Avoid adding new raw 6px/9px/12px radius/unsupported color patterns where possible.

5. After CC returns product fix evidence, run the same validation bundle again and compare deltas.

## Suggested CC Dispatch Split

If CD chooses to route work, I recommend two separate dispatches:

### Dispatch A - Product proof fix

Title: Vellum one-screen ApprovalReviewPanel layout proof at 1280x699

Scope:

- `workflows/design/applets/vellum_approval/widgets.py`
- Make required controls visible in one first viewport for loaded `viewer_normal_v2`, single-image approval view, 100% actual-size mode.
- Do not change packet fixture, zoom mode, or evidence path convention.

Acceptance:

- PySide screenshot at `1280 x 699` shows: canvas, filename/screen-state label, current decision/status, decision controls, Darrin notes, checklist, handoff reason, BA badge.
- No new direct applet lint errors.
- Pytest Vellum selection remains green.

### Dispatch B - Validation infrastructure fix

Title: Repair Vellum smoke script against current toolbar API

Scope:

- `scripts/vellum_smoke_test.py`
- Possibly tests/fixture expectations if current toolbar intentionally removed width combo.

Acceptance:

- Smoke completes without `AttributeError`.
- Tooltip expectations either align with current UX standard or are rewritten as explicit UX findings.
- Final smoke report is complete enough to use as a gate.

## Bottom Line

Current Vellum validation posture:

- Unit/regression tests: green.
- BA: trusted, reproducible, not green.
- Direct applet lint: warning debt, no errors.
- Smoke: broken/stale as a validation gate.
- Product visible proof: still blocked pending approved ApprovalReviewPanel layout fix.

— CODEX
