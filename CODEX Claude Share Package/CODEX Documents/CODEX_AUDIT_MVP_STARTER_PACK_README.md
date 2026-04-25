# CODEX Audit MVP Starter Pack

Purpose: provide Claude with contracts, examples, sample code, and visual references for the Panda Gallery Testing + Audit MVP without editing the live Panda Gallery source tree.

Status: local reference implementation starter pack. This is not the final dashboard and not live app integration.

## Boundaries

- Do not edit `C:\panda-gallery` from this starter pack.
- Do not build the final dashboard yet.
- Do not add Dropbox, AI provider calls, email sending, or archive search until the local package contract is stable.
- Use synthetic/de-identified data only until a compliance addendum explicitly allows real PHI.

## Folder Map

```text
CODEX Audit MVP Starter Pack/
  CODEX docs/
    CODEX_CLAUDE_INTEGRATION_PROMPT.md
    CODEX_MOCKUP_AND_SPEC_REFERENCES.md
  CODEX samples/
    sample_source_session/
      results_latest.json
      LATEST.txt
      metadata/metadata.json
      transcripts/transcript.md
      screenshots/*.png
    sample_audit_issue_extraction_v1.json
    expected_package/
      session_package_session_20260424_194422/
        session_package_manifest.json
        source/
        evidence/
        derived/
        logs/
  CODEX scripts/
    audit_mvp_reference_builder.py
    validate_audit_mvp_contracts.py
  CODEX validation output/
    CODEX_validation_report.json
```

## What This Pack Demonstrates

1. How an existing Panda Gallery testing session can become a local audit package.
2. How evidence IDs remain stable and link screenshots/transcripts to steps.
3. How a future AI extraction input can be generated without calling any AI provider yet.
4. How a sample issue links back to package evidence IDs.
5. How Claude can integrate this into `C:\panda-gallery` later with lower ambiguity.

## Key Sample Files

- Sample source results: `CODEX samples\sample_source_session\results_latest.json`
- Generated manifest: `CODEX samples\expected_package\session_package_session_20260424_194422\session_package_manifest.json`
- Generated evidence objects: `CODEX samples\expected_package\session_package_session_20260424_194422\derived\sample_evidence_objects_v1.json`
- Generated AI input: `CODEX samples\expected_package\session_package_session_20260424_194422\derived\ai_extraction_input_v1.json`
- Sample issue extraction: `CODEX samples\sample_audit_issue_extraction_v1.json`
- Validation report: `CODEX validation output\CODEX_validation_report.json`

## Rebuild Expected Package

```powershell
& 'C:\Users\drrap\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'C:\CODEX PG\CODEX Audit MVP Starter Pack\CODEX scripts\audit_mvp_reference_builder.py' `
  --source 'C:\CODEX PG\CODEX Audit MVP Starter Pack\CODEX samples\sample_source_session' `
  --out 'C:\CODEX PG\CODEX Audit MVP Starter Pack\CODEX samples\expected_package' `
  --overwrite
```

## Validate Sample Package And Issue

```powershell
& 'C:\Users\drrap\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'C:\CODEX PG\CODEX Audit MVP Starter Pack\CODEX scripts\validate_audit_mvp_contracts.py' `
  --manifest 'C:\CODEX PG\CODEX Audit MVP Starter Pack\CODEX samples\expected_package\session_package_session_20260424_194422\session_package_manifest.json' `
  --issues 'C:\CODEX PG\CODEX Audit MVP Starter Pack\CODEX samples\sample_audit_issue_extraction_v1.json' `
  --report 'C:\CODEX PG\CODEX Audit MVP Starter Pack\CODEX validation output\CODEX_validation_report.json'
```

Expected result:

```json
{
  "ok": true,
  "error_count": 0,
  "warning_count": 0,
  "errors": [],
  "warnings": []
}
```

## Recommended Claude Integration Order

1. Read the canonical specs.
2. Read this starter pack.
3. Inspect current live PG outputs in `C:\panda-gallery` read-only first.
4. Create a small live app integration plan before editing code.
5. Wire a local-only package builder command/menu/hook.
6. Generate packages under a local `workflows` output folder.
7. Add validation and smoke checks.
8. Only then discuss transfer, AI extraction, dashboard, email, or archive UI.

## Current Non-Goals

- No final dashboard.
- No live Dropbox upload.
- No real AI model call.
- No shared email send.
- No real PHI.
- No direct Codex edits to `C:\panda-gallery`.
