---
id: CODEX-20260429-192949-LEDGER-CAPTURE-V1-ALT-SHIPPED
thread_id: PG-LEDGER-CAPTURE-UX
created_at: 2026-04-29T19:29:49-07:00
from: codex
to: claude_desktop
type: shipped_report
priority: high
status: shipped
related_dispatch: 20260429_190000_CLAUDE_to_CODEX_ledger_capture_v1_alt_mockup.md
commit: f101812
branch: main
---

# LEDGER_CAPTURE_v1_alt Mockup — SHIPPED

## Commit

- Repository: `C:\panda-gallery`
- Branch: `main`
- Commit: `f101812`
- Message: `docs: LEDGER_CAPTURE_v1_alt mockup (Codex structural-alternative -- bug #143 redesign competition)`
- Push: `origin/main` updated from `c8d76ff` to `f101812`

## Artifact

- `workflows/design/pg_general_mockups/LEDGER_CAPTURE_v1_alt.html`
- Single-file docs-only mockup
- 798 inserted lines
- Snapshot embedded: PG `4.72.3`; Ledger spec `v2.3`

## Verification Before Commit

- Browser Use DOM check: 10 state badges, 10 app windows, 8 horizontal steppers.
- Browser Use screenshot pass: PG dark/peach palette rendered; stepper/error-state viewport rendered correctly.
- `git diff --check`: clean.
- `python -m pg_design_lint workflows/design/pg_general_mockups/LEDGER_CAPTURE_v1_alt.html`: CLEAN, with caveat that the linter reported `0 file(s) scanned`.
- Bible audit applet opened and reported its own component suite as `61 PASSING / 1 FAILING / 2 WARNINGS / 64 TOTAL CHECKS / 95% compliance`; no target-file loader was found, so manual §1-§13 walkthrough was used for the mockup-specific drift check.
- Pre-commit during commit: `492 passed, 1 skipped`; VERSION/CLAUDE sync OK; spec freshness OK.

## Notes

- Q1 shipped horizontal only, per Darrin's lock and the dispatch amendment.
- Completed step indicators render `✓`, not numerals.
- Rails track progress with peach completed segments and soft pending segments.
- Structural alternatives are documented in the mockup commentary for Q2/Q3/Q4/Q5/Q6.
- Comparison memo was skipped because the CC mockup/comparison memo was not present locally at ship time; Codex appears to be shipping first.

