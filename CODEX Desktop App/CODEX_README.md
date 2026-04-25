# CODEX Desktop App Scaffold

Local-only Python scaffold for the Panda Gallery Testing + Audit package builder.

This is not the full Panda Gallery v4 app and not the final audit dashboard. It promotes the starter-pack package builder into a testable local module under `C:\CODEX PG`.

## Folder Rule

All Codex-created folders in this scaffold are CODEX-prefixed:

- `CODEX_pg_audit`
- `CODEX_tests`
- `CODEX_test_output` when tests run

## Run Tests

Use the bundled Codex Python runtime if `python` is not on PATH:

```powershell
& 'C:\Users\drrap\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest discover -s CODEX_tests
```

## Build A Sample Package

```powershell
& 'C:\Users\drrap\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m CODEX_pg_audit.cli --source 'C:\CODEX PG\CODEX Audit MVP Starter Pack\CODEX samples\sample_source_session' --out 'C:\CODEX PG\CODEX Audit Prototype\CODEX Session Packages' --overwrite
```

Expected validation result:

```json
{
  "ok": true,
  "error_count": 0,
  "warning_count": 0
}
```

## Live-Shape Smoke Check

The builder has also been smoke-tested against the current read-only PG workflow output:

```powershell
& 'C:\Users\drrap\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m CODEX_pg_audit.cli --source 'C:\panda-gallery\workflows' --out 'C:\CODEX PG\CODEX Audit Prototype\CODEX Session Packages' --overwrite --mock-issues --review-records
```

Latest result:

```json
{
  "validation": {
    "ok": true,
    "error_count": 0,
    "warning_count": 0
  },
  "issue_validation": {
    "ok": true,
    "error_count": 0,
    "warning_count": 0
  },
  "review_records": {
    "approval_record": "...appr_YYYYMMDD_HHMMSS_0001.json",
    "email_draft_record": "...email_YYYYMMDD_HHMMSS_0001.json",
    "archive_jsonl": "...audit_archive_records.jsonl"
  }
}
```

This reads `C:\panda-gallery\workflows` only and writes generated output under the ignored `C:\CODEX PG\CODEX Audit Prototype` folder.

## Mock Issue Extraction

`--mock-issues` creates `derived/audit_issue_extraction_v1.json` as a local fixture. It does not call an AI provider. The validator blocks issues that reference evidence IDs not present in the generated package manifest.

## Local Review Records

`--review-records` requires `--mock-issues` and creates:

- approval JSON,
- draft-only email JSON,
- archive JSONL.

These records are local fixtures for the future dashboard. They do not send email, upload data, or close real issues.

The scaffold also includes helpers to validate the local approval/email/archive chain and search archive JSONL records by text. These are intended as read-side primitives for a future dashboard prototype.

## Boundaries

- Do not mutate `C:\panda-gallery`.
- Do not upload to Dropbox.
- Do not call AI providers.
- Do not send email.
- Treat privacy state as unknown unless explicitly reviewed.
- Generated packages under `CODEX Audit Prototype/` are local output and ignored by git.
