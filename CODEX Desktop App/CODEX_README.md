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

## Boundaries

- Do not mutate `C:\panda-gallery`.
- Do not upload to Dropbox.
- Do not call AI providers.
- Do not send email.
- Treat privacy state as unknown unless explicitly reviewed.
- Generated packages under `CODEX Audit Prototype/` are local output and ignored by git.
