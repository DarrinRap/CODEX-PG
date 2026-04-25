# CODEX Chunk 06 - Testing Acceptance

## Definition Of Done For First Local MVP

- Audit Panel opens from PG Testing workflow.
- Tester can select a completed or sample testing session.
- Session summary shows steps, PASS/FAIL/SKIP counts, and evidence availability.
- Full screenshot evidence can be attached to a step.
- Region evidence can be saved, recaptured, or discarded.
- Discard does not delete files; it writes `discarded: true`.
- PASS writes a step outcome.
- SKIP requires a reason.
- FAIL requires observed behavior, expected behavior, source step, and evidence IDs unless explicitly marked as test-authoring.
- Package builder writes `session_package_manifest.json` and `derived/ai_extraction_input_v1.json`.
- Validator catches missing evidence and invalid package paths.
- Claude Handoff remains disabled until validation passes.
- UI matches PG dark palette and PASS/FAIL/SKIP vocabulary.

## Minimum Tests

1. Build a package from the sample source session.
2. Validate the sample package with zero errors.
3. Intentionally remove or mislink one evidence ID and confirm validation fails.
4. Confirm discarded evidence remains in evidence list but is not treated as accepted support.
5. Confirm FAIL approval blocks when observed/expected text is missing.
6. Confirm handoff markdown includes package path, issue ID, evidence path, observed, expected, constraints, and acceptance tests.

## Reference Validation Output

`C:\CODEX PG\CODEX Audit MVP Starter Pack\CODEX validation output\CODEX_validation_report.json`

Expected clean result shape:

```json
{
  "ok": true,
  "error_count": 0,
  "warning_count": 0,
  "errors": [],
  "warnings": []
}
```
