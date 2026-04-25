# CODEX Chunk 04 - Data Contracts

## Package Manifest

File:

`session_package_manifest.json`

Schema:

`pg.session_package.v1`

Must include:

- `package_id`
- `session_id`
- `run_id`
- `package_state`
- `source_system`
- `tester_session`
- `sources[]`
- `evidence[]`
- `steps[]`
- `integrity`
- `missing_sources[]`
- `warnings[]`

## Evidence IDs

Format:

`ev_<kind>_<zero_padded_sequence>`

Examples:

- `ev_region_0001`
- `ev_step_auto_0001`
- `ev_workflow_frame_0017`
- `ev_transcript_span_0003`

Every issue must reference valid evidence IDs unless it is explicitly a test-authoring exception.

## Evidence Object Required Fields

- `evidence_id`
- `kind`
- `label`
- `step_n`
- `source_path`
- `package_path`
- `remote_path`
- `mime_type`
- `sha256`
- `bytes`
- `created_at`
- `capture`
- `transcript_ref`
- `discarded`
- `privacy`

## Issue Extraction

File:

`audit_issue_extraction_v1.json`

Schema:

`pg.audit_issue_extraction.v1`

Issue fields:

- `issue_id`
- `package_id`
- `session_id`
- `run_id`
- `title`
- `summary`
- `category`
- `priority`
- `confidence`
- `status`
- `source_steps`
- `evidence_ids`
- `transcript_refs`
- `observed_behavior`
- `expected_behavior`
- `impact`
- `suggested_response`
- `reviewer`
- `lineage`
- `audit.events[]`

## Canonical Sources

- `C:\CODEX PG\CODEX Canonical Specs\CODEX_SESSION_PACKAGE_SCHEMA_v1.md`
- `C:\CODEX PG\CODEX Canonical Specs\CODEX_AUDIT_ISSUE_SCHEMA_v1.md`
- `C:\CODEX PG\CODEX Audit MVP Starter Pack\CODEX samples\expected_package\session_package_session_20260424_194422\session_package_manifest.json`
- `C:\CODEX PG\CODEX Audit MVP Starter Pack\CODEX samples\expected_package\session_package_session_20260424_194422\derived\sample_evidence_objects_v1.json`
- `C:\CODEX PG\CODEX Audit MVP Starter Pack\CODEX samples\sample_audit_issue_extraction_v1.json`
