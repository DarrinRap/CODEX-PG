# Vellum validation summary - 2026-05-11 18:23:43 -07:00

No app code changed. Validation only.

## Commands / Artifacts

- Pytest: pytest_tests_k_vellum.log
- BA audit: a_audit_vellum_plain.json, a_audit_vellum_plain_summary.log
- BA validator: a_report_validator_vellum_gate.json, a_report_validator_vellum_gate.log
- Direct applet lint: pg_design_lint_vellum_approval.json
- Smoke: ellum_smoke_test.log

## Results

| Check | Result |
|---|---|
| python -m pytest tests -k vellum -q | PASS: 149 passed, 4 xfailed, 1055 deselected |
| python scripts\ba_audit_runner.py --app Vellum --summary | TRUSTED WITH FINDINGS: 0 fail / 147 warn / 32 unknown / 9 evidenced |
| python scripts\ba_report_validator.py ... --gate | report_trusted_with_findings; reproduction drift none |
| python -m pg_design_lint workflows\design\applets\vellum_approval --json | 0 errors / 25 warnings / 10 info |
| python scripts\vellum_smoke_test.py | FAIL: 20/31 passed, 11 failed, then AttributeError on missing MarkupToolbar._width_combo |

## Actionable Bug / Risk List

1. BLOCKER FOR SMOKE GATE: scripts/vellum_smoke_test.py is stale against current toolbar API.
   - Evidence: ellum_smoke_test.log.
   - Failure: AttributeError: 'MarkupToolbar' object has no attribute '_width_combo' in 	est_width_combo().
   - Also fails tooltip-length checks for Select/Pen/Line/Rect/Oval/Arrow/Text/Callout/Snippet/Eraser.
   - Recommendation: repair smoke script or restore width-control contract before using smoke as a ship gate.

2. NOT BA-GREEN: BA Vellum target is trusted/reproducible but findings-heavy.
   - Evidence: a_audit_vellum_plain.json, validator verdict $(@{checks=System.Object[]; dispatch_path=; disposition_overlay=; finding_disposition_requirements=; generated_at=05/11/2026 18:24:36; limitations=System.Object[]; report_path=C:\CODEX PG\CODEX Vellum Reset\evidence\vellum_validation_20260511_182343\ba_audit_vellum_plain.json; reproduction=; runtime_validation=; schema_version=BA_REPORT_VALIDATION_v1; summary=; target_app=Vellum; validation_profile=gate; validation_verdict=report_trusted_with_findings}.validation_verdict).
   - Recommendation: keep broad BA cleanup deferred unless explicitly reopened; do not claim Vellum is BA clean.

3. DIRECT APPLET LINT WARNINGS: approval applet has no lint errors, but warnings remain.
   - Top direct lint groups:
- R04, warning: 11
- R18, warning: 7
- R19, info: 7
- R26, warning: 4
- R03b, warning: 3
- R28, info: 3

4. KNOWN PRODUCT-VISIBLE ISSUE STILL OPEN: one-screen ApprovalReviewPanel proof remains queued from prior report.
   - Required controls/status areas are not all visible in one 1280x699 screenshot until the approved layout fix lands.

## Top BA Finding Groups

- R26 warning, warn: 73
- R04 warning, warn: 34
- R18 warning, warn: 18
- R28 info, unknown: 17
- R03b warning, warn: 13
- R19 info, unknown: 7
- R05a warning, warn: 5
- PySide workflow order unproven, unknown: 3
- R16 warning, warn: 3
- R25 info, unknown: 3
- R07 warning, warn: 1
- R11 info, unknown: 1
