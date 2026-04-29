---
thread_id: PG-LEDGER-SYSTEM
reply_to: CLAUDE-20260428-204500-ledger-lint-build-v11
type: implementation_report
from: codex
to: claude_desktop
status: complete
---

# Ledger lint v11 implementation report

## Summary
Implemented Phase 0 Ledger lint v11 in Codex-owned paths only. No commit made.

## Files written with LOC
Total Python LOC, excluding generated __pycache__: 1320.

- `pg_design_lint/__init__.py` - 5
- `pg_design_lint/__main__.py` - 46
- `pg_design_lint/lint.py` - 68
- `pg_design_lint/report.py` - 30
- `pg_design_lint/score.py` - 23
- `pg_design_lint/violations.py` - 14
- `pg_design_lint/rules/base.py` - 206
- `pg_design_lint/rules/R01_forbidden_colors.py` through `R28_inline_counts.py` plus R03b/R05a/R05b - 402 combined across 29 rule modules
- `pg_design_lint/tests/test_lint_core.py` - 53
- `pg_design_lint/tests/test_tools.py` - 23
- `workflows/tools/pg_spec_freshness.py` - 33
- `workflows/tools/lint_baseline_writer.py` - 24

## Files modified
- `workflows/tools/pre_commit.py` - added `pg_spec_freshness` and changed-only `pg_design_lint` checks after pytest, non-strict/error-floor behavior per v2.2.
- `workflows/tools/pg_dispatch_lint.py` - extended the stdlib frontmatter parser and added Rule #23 `widget_inventory` mirror validation: required on UI dispatches, `body_table: |` mirror, byte-match against body table, at least one state row.
- Existing scaffold files under `pg_design_lint/` were replaced/filled out in the Codex-owned package.

## Rule coverage
Implemented all 29 modules named in v1.1 §3.2:
R01, R02, R03, R03b, R04, R05a, R05b, R06-R28.

Phase A blocking rules are error severity: R01, R03, R08, R14, R21, R22, R23. Other rules are warning/info report-only as specified.

Notable contract points:
- R21 runs first and aborts other checks if stale.
- R16 uses AST class-base detection and `lint_config.top_level_window_bases`; QWidget only counts when `setWindowFlags(Qt.Window)` is detected.
- R23 delegates dispatch validation to `pg_dispatch_lint.py` so the mirror logic has one authority.
- `pg_spec_freshness.py --update` atomically writes the Bible hash.
- `lint_baseline_writer.py` writes the JSON baseline format, but I did not write `workflows/decisions/lint_baseline.json` because `workflows/decisions/**` is outside Codex's authorized write set.

## Tests / coverage
- `python -m compileall -q pg_design_lint workflows\tools\pre_commit.py workflows\tools\pg_dispatch_lint.py workflows\tools\pg_spec_freshness.py workflows\tools\lint_baseline_writer.py` - PASS
- `python -m pytest -q pg_design_lint\tests` - PASS, 5 passed in 0.08s
- `python -m pytest -q` - PASS, 368 passed, 1 skipped in 2.71s
- `python workflows\tools\pg_spec_freshness.py` - PASS, current hash `be6aab427a379d53b951c0414a047dd236448672785cec194e292393e3f90f2c`

## Performance
- Full repo lint: 373 files, 14.374s, 1598 findings.
- Changed-only with zero staged files: 0 files, 0.199s.
- Changed-only-since HEAD on current tracked modifications: 6 files, 0.392s.

## Baseline counts
Full repo current findings, without baseline suppression:
- Errors: 56
- Warnings: 992
- Info: 550
- Total: 1598

No baseline file was written to `workflows/decisions/lint_baseline.json` due ownership boundary. The writer is implemented and ready for CD integration or Darrin-authorized baseline creation.

## Open issues
- Full-repo lint includes legacy findings by design. Baseline creation is the next integration step.
- Some current tracked modifications outside Codex scope (`panda_gallery.py`, `panda_ledger/verify/__init__.py`) are present and can affect changed-only-since-HEAD counts. They pre-existed my build and appear to be CC-owned work.
- The implementation is intentionally stdlib-only and compact. Several heuristic rules are conservative first-pass detectors, appropriate for Phase A/report-only burn-in.

## Forbidden-file audit
Codex wrote/modified only:
- `pg_design_lint/**`
- `workflows/tools/pre_commit.py`
- `workflows/tools/pg_dispatch_lint.py`
- `workflows/tools/pg_spec_freshness.py`
- `workflows/tools/lint_baseline_writer.py`

Did not edit:
- `panda_ledger/shared/contracts.py`
- `panda_ledger/shared/conventions.md`
- `panda_ledger/**` (CC/CD-owned; existing dirty files were already present)
- `ledger_bridge.py`
- `workflows/decisions/**`
- `workflows/design/pg_design_spec.json`
- v2.3 draft files

Working tree still contains pre-existing CC/CD changes in forbidden areas; I did not revert or modify them.
