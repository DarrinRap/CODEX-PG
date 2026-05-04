# CODEX Vellum Cleanup Candidates Spec v1

Status: Draft for Darrin review
Created: 2026-05-04
Owner: Codex
Project: Panda Gallery / Vellum
Spec type: low-risk visual cleanup

Canonical spec path:

`C:\CODEX PG\CODEX Canonical Specs\CODEX_VELLUM_CLEANUP_CANDIDATES_SPEC_v1.md`

Primary app target if approved later:

- `C:\panda-gallery\panda_ledger\browse\trace_view.py`
- `C:\panda-gallery\panda_ledger\capture\qa_pair_widget.py`
- `C:\panda-gallery\panda_ledger\styles.py`

Reference artifacts:

- `C:\CODEX PG\CODEX BA Disposition Ledger\CODEX_BA_DISPOSITION_LEDGER.json`
- `C:\CODEX PG\CODEX BA Disposition Ledger\CODEX_LAST_VALIDATION_WITH_DISPOSITIONS.json`
- `C:\panda-gallery\workflows\design\applets\ba_audit_latest.json`

## 1. Purpose

Vellum has no unreviewed BA fails, warnings, or unknowns after the disposition overlay. The only active Vellum items are seven `cleanup_candidate` findings.

This spec defines a small visual cleanup pass for those candidates only. These are polish items, not urgent functionality bugs.

## 2. Current State

Raw Vellum BA remains:

- `2 fail`
- `15 warn`
- `35 unknown`
- `14 evidenced`

Disposition-aware Vellum state is:

- `0` unreviewed fails
- `0` unreviewed warnings
- `0` unreviewed unknowns
- `7` cleanup candidates
- `0` unmatched disposition entries

## 3. Scope

In scope:

- Replace off-scale spacing/radius literals called out by BA cleanup candidates.
- Keep behavior unchanged.
- Keep visual impact minimal and consistent with PG design tokens.
- Rerun focused BA validation after the cleanup.

Out of scope:

- Functional Vellum changes.
- BA scanner changes.
- Runtime/action-feedback probe work.
- Relay work.
- Broad style refactors.
- Reworking typography, color tokens, or generated QSS architecture.

## 4. Cleanup Candidate Inventory

| BA finding(s) | Target | Current issue | Recommended action |
| --- | --- | --- | --- |
| `BA-LINT-PG-DESIGN-LEDGER-0006` | `panda_ledger/browse/trace_view.py:48` | `2px` spacing literal is off the PG spacing scale. | Replace with the nearest approved PG spacing token/value used locally. Prefer an existing constant/helper if one is already nearby. |
| `BA-LINT-PG-DESIGN-LEDGER-0015/0016` | `panda_ledger/capture/qa_pair_widget.py:59` | `6px` margins are off the PG spacing scale and are duplicated by BA. | Replace with the nearest approved PG spacing token/value that preserves the compact QA-pair layout. |
| `BA-LINT-PG-DESIGN-LEDGER-0024/0025/0026/0027` | `panda_ledger/styles.py:141`, `145`, `158`, `162` | `5px` scrollbar radius values are off the PG radius scale. | Replace with the nearest approved PG radius token/value used by Vellum styles. |

## 5. Implementation Rules

- Do not change interaction behavior.
- Do not rename widgets, signals, classes, modules, or public API.
- Do not introduce new style systems.
- Prefer existing Vellum style constants or PG design helpers over new literals.
- If an exact approved token is unclear, stop and report the ambiguity instead of guessing.
- Keep edits to the three target files only unless direct local context proves a shared token file must be used.

## 6. Acceptance Criteria

A cleanup implementation is acceptable only if all are true:

- The seven cleanup candidates no longer appear as active cleanup candidates in the disposition-aware Vellum validation output, or each remaining item has a clear reason recorded.
- Raw BA evidence remains available and unmodified.
- No new Vellum fail/warn findings are introduced.
- No Relay files are touched.
- Focused validator tests still pass.
- A Vellum BA rerun still validates as `report_trusted_with_findings` or better, with zero validator errors.

## 7. Suggested Verification Commands

Run after implementation, not during this draft-only spec pass:

```powershell
python -m pytest tests/test_ba_report_validator.py -q
python scripts\ba_audit_runner.py --app "PG Design Ledger" --summary
python scripts\ba_report_validator.py --report workflows\design\applets\ba_audit_latest.json --dispositions "C:\CODEX PG\CODEX BA Disposition Ledger\CODEX_BA_DISPOSITION_LEDGER.json" --output "C:\CODEX PG\CODEX BA Disposition Ledger\CODEX_LAST_VALIDATION_WITH_DISPOSITIONS.json"
```

## 8. Recommended Action

Do not rush this cleanup into a larger feature branch. If Darrin approves implementation, make it as one tiny Vellum-only patch and commit it separately from BA disposition infrastructure.
