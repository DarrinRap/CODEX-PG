---
schema_version: 1
message_id: 20260508_2120_CODEX_to_CLAUDE_ba_vellum_antipattern_rules_rtc
thread_id: BA-VELLUM-ANTIPATTERNS-v1
from: CODEX
to: CLAUDE
date: 2026-05-08T21:20:00-07:00
subject: RTC - BA Vellum antipattern rules R27-R29 implemented
type: rtc
priority: high
tier: High
---

# RTC - BA Vellum antipattern rules R27-R29

CD task completed. No commit was made. No implementation-go or commit-go token was sent to CC.

## Files changed

- `C:\panda-gallery\scripts\ba_audit_runner.py`
- `C:\panda-gallery\tests\test_ba_audit_runner.py`
- Refreshed BA output: `C:\panda-gallery\workflows\design\applets\ba_audit_latest.json`
- Full BA output sidecar copied for CD: `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\20260508_2120_CODEX_to_CLAUDE_ba_vellum_antipattern_rules_full_ba_output.json`

## Implementation

- Added R27 FAIL: same-method `setWidgetResizable(True)` plus `addStretch()` now emits `R27 error`.
- Added R28 WARN: literal `setToolTip(...)` and `tooltip=` strings containing unimplemented markers now emit `R28 warning`.
- Added R29 WARN: hardcoded count `QLabel(...)` with no update path now emits `R29 warning`.
- Wired supplemental AST rules through `pg_design_lint` so they run wherever `pg_design_lint` is enabled, not only on Vellum.
- Added fixtures for R27 positive/negative, R28 positive/negative, R29 local-label positive, R29 unassigned/nested-label positive, R29 self-label-with-update negative, and R29 non-count-label negative.

## Baseline BA Before R27-R29

Baseline command run before implementation:

`python scripts\ba_audit_runner.py --app Vellum --summary`

Baseline console result:

- Exit: 1, expected because Vellum already had findings.
- Output JSON path: `C:\panda-gallery\workflows\design\applets\ba_audit_latest.json`
- Totals: `15 fail / 83 warn / 20 unknown / 9 evidenced`
- Evidence score: `8.4%`
- Coverage debt: `15.7%`
- Existing hard failures were R02 palette violations and R17 inline-style violations in `workflows/design/applets/am_mockup_review.py`.

## Final BA After R27-R29

Final command:

`python scripts\ba_audit_runner.py --app Vellum --summary`

Final console result:

- Exit: 1, expected because Vellum still has fail/warn/unknown findings.
- Full structured output: `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\20260508_2120_CODEX_to_CLAUDE_ba_vellum_antipattern_rules_full_ba_output.json`
- Source output: `C:\panda-gallery\workflows\design\applets\ba_audit_latest.json`
- Generated: `2026-05-08T21:16:41-07:00`
- Target: `Vellum`
- Files found by canonical BA target: `15`
- Totals: `21 fail / 86 warn / 20 unknown / 9 evidenced`
- Checks: `136`
- Evidence score: `7.8%`
- Coverage debt: `14.7%`

New rule findings:

- FAIL `BA-LINT-VELLUM-0117` R27: `workflows/design/applets/am_mockup_review.py:3065` - `addStretch()` in a `QScrollArea` body method.
- FAIL `BA-LINT-VELLUM-0120` R27: `workflows/design/applets/vellum_approval/widgets.py:559` - `addStretch()` in a `QScrollArea` body method.
- FAIL `BA-LINT-VELLUM-0121` R27: `workflows/design/applets/vellum_approval/widgets.py:642` - `addStretch()` in a `QScrollArea` body method.
- FAIL `BA-LINT-VELLUM-0122` R27: `workflows/design/applets/vellum_approval/widgets.py:730` - `addStretch()` in a `QScrollArea` body method.
- FAIL `BA-LINT-VELLUM-0123` R27: `workflows/design/applets/vellum_approval/widgets.py:750` - `addStretch()` in a `QScrollArea` body method.
- WARN `BA-LINT-VELLUM-0118` R28: `workflows/design/applets/am_mockup_review.py:3941` - tooltip contains `phase 2`.
- WARN `BA-LINT-VELLUM-0119` R28: `workflows/design/applets/am_mockup_review.py:4127` - tooltip contains `phase 3`.
- WARN `BA-LINT-VELLUM-0124` R28: `workflows/design/applets/vellum_approval/widgets.py:553` - tooltip contains `phase 2`.
- R29 produced no current Vellum findings after the latest working-tree state, but synthetic positive fixtures pass and will catch the pattern going forward.

## Validation

- `python -m py_compile scripts\ba_audit_runner.py`: pass
- `python -m pytest tests\test_ba_audit_runner.py -q`: `68 passed`
- `python -m pytest -q`: `1343 passed, 1 skipped`
- `python scripts\ba_audit_runner.py --app Vellum --summary`: completed and wrote final red BA report above

Earlier Vellum validation also run before the final R27-R29 patch:

- `python -m pytest tests\test_vellum_export.py -q`: `5 passed`
- `python scripts\vellum_smoke_test.py`: `239/239 passed`, but emitted path-relative tracebacks for temp packet paths outside `C:\panda-gallery`.
- `python scripts\vellum_drag_diagnostic.py`: `ALL DRAGS PASS`
- `python scripts\vellum_stencil_drop_diagnostic.py`: `ALL 16 DROPS PASS`

## Self-review

Pass 1: 1 issue fixed - `broken_wire_static` was registered in scanner metadata/default manifest but was not invoked by `run_audit`; added dispatch and progress row.

Pass 2: 1 issue fixed - R29 missed unassigned/nested count labels such as `layout.addWidget(QLabel("Count: 0"))`; added detection and a regression fixture.

Pass 3: 0 significant issues fixed - reran focused BA tests, full pytest, and Vellum BA; no further task-scope inconsistencies found.

## Known limits

- R27 follows CD's simplified same-method detection; it does not fully trace direct helper-call layout ownership yet.
- R28 detects literal tooltip strings and `tooltip=` keyword strings; dynamically composed tooltip text remains out of scope.
- R29 covers class-scoped assigned or directly nested count labels; broad module-level builder correlation remains future coverage.
- Final Vellum BA remains red and should not be treated as pass: `21 fail / 86 warn / 20 unknown / 9 evidenced`.

Requesting CD review and commit-go if this implementation/report is acceptable.
