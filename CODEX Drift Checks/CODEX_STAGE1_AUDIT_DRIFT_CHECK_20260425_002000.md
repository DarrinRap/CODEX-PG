# CODEX Stage 1 Audit Drift Check

Generated: 2026-04-25 00:20:00 -07:00
From: Codex
Scope: compare Codex scaffold `C:\CODEX PG\CODEX Desktop App\CODEX_pg_audit\` against shipped PG v4.34 module `C:\panda-gallery\codex_audit\`, then update Codex canonical schema docs to match Stage 1 reality.

## Summary

Result: no unexpected contract drift found in the shipped PG v4.34 `codex_audit` module.

The differences from the Codex scaffold match the Stage 1 locks and Claude's implementation report:

- Structured `manifest.warnings[]` replaced new-package `missing_sources[]` output.
- Structured `manifest.package_source` replaced the older `source_system`-style source summary.
- Package/folder IDs use `pkg_local_<short-safe-session-id>_<8hex>` and `session_package_<short-safe-session-id>_<8hex>`.
- `steps[].test_id` and `steps[].checklist_results` are preserved from PG guided-test output.
- Mock issue extraction emits additive `source_test_ids[]`.
- Derived files are hash-tracked as `sources[]` records.
- Integrity hash ordering is explicit: compute `manifest_without_integrity_sha256` before assigning final `integrity`.
- `source_dir.parent` resolver behavior is now an implicit contract for PG `workflows/...` screenshot references.
- CLI adds PG-specific output containment validation so package output cannot resolve inside `C:\panda-gallery`.

## Canonical Docs Updated

Updated:

- `C:\CODEX PG\CODEX Canonical Specs\CODEX_SESSION_PACKAGE_SCHEMA_v1.md`
- `C:\CODEX PG\CODEX Canonical Specs\CODEX_AUDIT_ISSUE_SCHEMA_v1.md`

Schema doc changes:

- Added Stage 1 package ID/folder naming rule.
- Added `package_source` object and local-only absolute path note.
- Added structured warning record shape, allowed codes, severity rules, and `missing_sources[]` deprecation.
- Added derived file hash coverage for `ai_extraction_input`, `package_summary`, and `packaging_log`.
- Added `steps[].test_id`, `steps[].checklist_results`, and clarified `source_result_index` 0-based vs `step_n` 1-based.
- Added `source_test_ids[]` to audit issue objects and validation rules.

## Drift Check Details

Compared text modules:

| File | Codex scaffold bytes | PG v4.34 bytes | Notes |
| --- | ---: | ---: | --- |
| `__init__.py` | 614 | 1004 | PG adds shipped-module version/docs. Expected. |
| `cli.py` | 2055 | 3808 | PG adds `argv` support and output containment validation. Expected. |
| `issue_extraction.py` | 6594 | 7066 | PG adds `source_test_ids[]`. Expected. |
| `package_builder.py` | 18938 | 21700 | PG adds structured warnings, package_source, short IDs, PG additive step fields, derived-source hashes, integrity ordering comment. Expected. |
| `review_records.py` | 8599 | 8875 | Minor shipped-module polish; review chain behavior remains aligned. Expected. |
| `validation.py` | 11876 | 15164 | PG adds validation for package_source, warnings block, deprecated missing_sources tolerance, step additive fields, blocking-warning package_state rule, source_test_ids. Expected. |

Ignored:

- `__pycache__` files differ because the two directories were run under different Python versions. Not contract-relevant.

## Ground Truth Manifest

Baseline manifest read directly:

`C:\CODEX PG\CODEX Audit Prototype\CODEX Session Packages\session_package_2026-04-24T20-01-30--130-Phase_87b9568e\session_package_manifest.json`

Important observed facts:

- `package_id`: `pkg_local_2026-04-24T20-01-30--130-Phase_87b9568e`
- Full `session_id` and `run_id` remain `2026-04-24T20-01-30--130-Phase-4-verification`.
- `warnings[]` contains two expected `optional_source_missing` entries: `metadata_json` and `transcript_markdown`.
- `package_state` remains `local_ready` because both warnings are severity `warning`, not `blocking`.
- Derived records `src_ai_input`, `src_package_summary`, and `src_packaging_log` are present in `sources[]`.

Validation command run with bundled Codex Python:

```text
C:\Users\drrap\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -c "... validate_manifest(...) ..."
```

Result:

```text
{'ok': True, 'error_count': 0, 'warning_count': 0, 'errors': [], 'warnings': []}
```

Note: validator warning count is separate from manifest operational `warnings[]`; the manifest warnings remain present and expected.

## Follow-Ups

- No PG code change recommended from this drift check.
- Stage 2 transfer/redaction work must revisit absolute Windows paths before any external transfer.
- If the Codex scaffold remains a reference implementation, either update it to mirror PG v4.34 or clearly mark PG `codex_audit` as the current source of truth.
