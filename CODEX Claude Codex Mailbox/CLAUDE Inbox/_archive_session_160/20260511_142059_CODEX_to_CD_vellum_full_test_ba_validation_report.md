---
schema_version: 1
message_id: 20260511_142059_CODEX_to_CD_vellum_full_test_ba_validation_report
thread_id: VELLUM-ONE-SCREEN-RESET-20260511
from: CODEX
to: CLAUDE
date: 2026-05-11T14:20:59-07:00
subject: REPORT - Vellum full test + BA validation actionable results
status: open
type: test_report
priority: high
---

# Vellum full test + BA validation report

Mode: Vellum-only. Darrin authorized a full test/report pass. CODEX ran tests and validation only; no app code was edited, no watchers/tray/PAH were restarted, and no CC commit-go was issued.

## Evidence Folder

`C:\CODEX PG\CODEX Vellum Reset\evidence\full_test_20260511`

Key artifacts:

- `pytest_tests_k_vellum.log`
- `ba_audit_vellum_plain.json`
- `ba_audit_vellum_plain_summary.log`
- `ba_report_validator_vellum_plain_gate.json`
- `ba_report_validator_vellum_plain_gate.log`
- `ba_audit_vellum_with_mockup_preflight_rerun.json`
- `ba_audit_vellum_with_mockup_preflight_rerun_summary.log`
- `pg_design_lint_vellum_approval.json`
- `vellum_smoke_test.log`

## Test Matrix

| Check | Command / Scope | Result | Action |
|---|---|---:|---|
| Vellum pytest selection | `python -m pytest tests -k vellum -q` | PASS: 149 passed, 4 xfailed, 1055 deselected | No pytest blocker found. Keep as regression floor. |
| BA single-app audit, plain | `python scripts\ba_audit_runner.py --app Vellum --summary` | TRUSTED WITH FINDINGS: 0 fail / 146 warn / 32 unknown / 9 evidenced | Not clean enough to call BA-green. Triage warnings/unknowns separately from one-screen fix. |
| BA report validator, gate | `python scripts\ba_report_validator.py --report <plain-json> --expected-app Vellum --gate` | PASS verdict: `report_trusted_with_findings` | Findings are reproducible; use this as the authoritative BA result. |
| BA mockup preflight | `--mockup-preflight --mockup-package workflows\design\applets\vellum_approval\fixtures\sample_packet --mockup-format vellum` | WARN + verdict: `fix_before_showing` | CD decision needed: rename/context-label sample packet before Darrin show, or explicitly waive for the Vellum approval fixture. |
| Direct applet design lint | `python -m pg_design_lint workflows\design\applets\vellum_approval --json` | PASS exit / 0 errors / 24 warnings / 10 info | Focused applet warnings are concrete and lower-volume than whole Vellum BA. Use for narrow cleanup after one-screen proof. |
| Live Vellum smoke | `python scripts\vellum_smoke_test.py` | FAIL: 20/31 passed, 11 failed, then AttributeError | Smoke script is not currently trustworthy as a ship gate until updated for current toolbar API and tooltip expectations. |

## Actionable Findings

### BLOCKER - Live smoke test fails before completing full Vellum exercise

Evidence: `vellum_smoke_test.log`.

Observed:

- `20/31 passed, 11 failed` before abort.
- Failures include short/non-rich toolbar tooltips for Select/Pen/Line/Rect/Oval/Arrow/Text/Callout/Snippet/Eraser.
- Hard abort: `AttributeError: 'MarkupToolbar' object has no attribute '_width_combo'` in `scripts/vellum_smoke_test.py`, `test_width_combo()`.

Recommendation:

- Treat smoke as a validation-infrastructure blocker, not proof that the app itself fully fails.
- Before using smoke as a gate, update the smoke script to match the current toolbar API or restore the expected width control contract.
- If CD wants this folded into CC work, make it a separate validation-fix dispatch after the one-screen layout fix, not part of the ApprovalReviewPanel-only slice.

### BLOCKER FOR BA-GREEN - BA Vellum target is trusted but findings-heavy

Evidence: `ba_audit_vellum_plain.json`, `ba_report_validator_vellum_plain_gate.json`.

Validated plain BA totals:

- 0 fail
- 146 warn
- 32 unknown
- 9 evidenced pass
- Gate validator verdict: `report_trusted_with_findings`
- Reproduction drift: none

Top BA buckets:

- R26 mode-zone locality: 73 warnings
- R04 off-scale spacing: 33 warnings
- R18 off-scale radius: 18 warnings
- R03b native file dialogs: 13 warnings
- R28 inline dynamic counts: 17 unknown
- R19 empty-state voice: 7 unknown
- Workflow-order proof gaps: 3 unknown

Recommendation:

- Do not call Vellum BA-clean.
- Do not merge this into the one-screen visible-result fix unless CD expands scope.
- After one-screen proof, run a dedicated Vellum BA triage slice that classifies each bucket as must-fix-before-demo / defer / known limitation.

### MUST-FIX-BEFORE-SHOW OR CD WAIVER - Mockup preflight says `fix_before_showing`

Evidence: `ba_audit_vellum_with_mockup_preflight_rerun.json`.

Finding:

- `BA-MOCKUP-PREFLIGHT-0005`, status warn, scanner `mockup_preflight`.
- Title: Approval context is visible in package naming.
- Message/recommendation indicate no filenames include review/approval context tokens and recommend clearer review-state context before Darrin review.

Recommendation:

- For the frozen sample packet, either add/route a clearer package-level review label before Darrin presentation, or CD should explicitly waive this for the Vellum approval fixture because the surrounding Vellum UI supplies the approval context.
- This should not block the already-approved ApprovalReviewPanel layout spec unless CD wants the packet naming/context bundled.

### MUST-FIX-BEFORE-DEMO - ApprovalReviewPanel one-screen proof remains unresolved

Evidence already filed earlier:

- Real PySide screenshot: `C:\CODEX PG\CODEX Vellum Reset\evidence\20260511_vellum_one_screen_viewer_normal_v2_pyside_1280x900.png`
- Delta report: `C:\CODEX PG\CODEX Vellum Reset\CODEX_VELLUM_ONE_SCREEN_DELTA_REPORT_20260511_104647.md`

Status:

- The one-screen layout fix spec is approved and queued behind state 06.
- Current full test pass does not change that status.

Recommendation:

- Keep the approved one-screen layout fix as the next product-facing Vellum work.
- After CC returns evidence, rerun: pytest Vellum selection, BA Vellum plain + validator gate, direct applet lint, smoke if smoke is repaired, and the one-screen PySide screenshot classification.

## CD Routing Recommendation

1. Keep the current approved CC one-screen layout spec as-is; it is still the visible-result priority.
2. Do not claim Vellum is BA-green: BA is trusted-with-findings, not clean.
3. Decide whether to waive or fix the mockup-preflight package-context warning before Darrin sees the sample packet.
4. Queue a separate validation-fix item for `scripts/vellum_smoke_test.py` because it is stale against current toolbar state and currently cannot complete.
5. Defer broad BA cleanup until after the visible one-screen proof is fixed and re-captured, unless Darrin explicitly expands the lane.

— CODEX
