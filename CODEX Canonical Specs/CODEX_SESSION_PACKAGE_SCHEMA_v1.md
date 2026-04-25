# CODEX Session Package Schema v1

Generated: 2026-04-24

Status: Codex canonical draft for PG Testing + Audit MVP v1.

Scope: defines the deterministic local package produced after a Panda Gallery tester session has already captured guided results, screenshots, workflow frames, audio, and timestamped transcript. This schema does not redefine audio capture or transcription.

## Goals

- Package one tester session into a portable, integrity-checkable folder.
- Introduce durable evidence IDs so screenshots, transcript spans, and AI issues link to evidence objects rather than fragile paths.
- Support local-only prototype first, then Dropbox upload and backend processing.
- Preserve the existing PG outputs as source artifacts instead of mutating them.

## Non-Goals

- No live Dropbox API requirement in schema v1.
- No AI extraction requirement in package v1 beyond a clean extraction input.
- No PHI permission implied. Real-PHI use requires the Testing + Audit compliance addendum.
- No edits to `C:\panda-gallery` by Codex.

## Package Folder Layout

```text
session_package_<session_id>/
  session_package_manifest.json
  source/
    results_latest.json
    metadata.json
    transcript.md
    LATEST.txt
  evidence/
    ev_<kind>_<sequence>.<ext>
  derived/
    ai_extraction_input_v1.json
    package_summary.md
  logs/
    packaging_log.jsonl
```

Optional source files may be omitted only when their absence is recorded in structured `manifest.warnings[]` entries with code `optional_source_missing`. Required source omissions use code `required_source_missing` and block `local_ready`.

## Manifest Object

File: `session_package_manifest.json`

```json
{
  "schema": "pg.session_package.v1",
  "schema_version": 1,
  "package_id": "pkg_local_2026-04-24T20-01-30--130-Phase_87b9568e",
  "session_id": "2026-04-24T20-01-30--130-Phase-4-verification",
  "run_id": "2026-04-24T20-01-30--130-Phase-4-verification",
  "package_state": "local_ready",
  "created_at": "2026-04-24T20:12:55-07:00",
  "created_by": "codex-pg-audit-local",
  "package_source": {
    "source_kind": "panda_gallery_workflows",
    "source_root": "C:\\panda-gallery\\workflows",
    "results_path": "C:\\panda-gallery\\workflows\\results_latest.json",
    "latest_pointer_path": "C:\\panda-gallery\\workflows\\LATEST.txt",
    "packaged_from_live_pg": true,
    "source_mutation_policy": "read_only"
  },
  "tester_session": {
    "title": "#130 Phase 3 test",
    "instructions_source": "workflows/instructions_latest.json",
    "started_at": "2026-04-24T19:44:22-07:00",
    "completed_at": "2026-04-24T19:48:10-07:00"
  },
  "sources": [],
  "evidence": [],
  "steps": [],
  "upload": null,
  "integrity": {},
  "warnings": []
}
```

Stage 1 package IDs use `pkg_local_<short_safe_session_id>_<8-char-sha256-suffix>`. The folder name uses the same shortened session form: `session_package_<short_safe_session_id>_<8-char-sha256-suffix>`. The full `session_id` and `run_id` remain untruncated in the manifest.

## Package States

| State | Meaning |
| --- | --- |
| `draft` | Package folder exists but manifest is incomplete. |
| `local_ready` | Manifest validates, all required local evidence is copied, hashes are recorded. |
| `queued_for_upload` | Package is immutable locally and waiting for transfer. |
| `uploading` | Transfer is in progress. |
| `uploaded_pending_verification` | Remote copy exists but completion marker is not confirmed. |
| `remote_ready` | Upload manifest and completion marker are present. Backend may process. |
| `processing` | Backend/AI extraction is running. |
| `processing_failed` | Backend processing failed; error record required. |
| `triage_ready` | AI issue extraction completed and is ready for PG review. |
| `archived` | Review workflow closed and archive record exists. |

## Source File Records

Each source file copied into `source/` is recorded in `sources[]`.

```json
{
  "source_id": "src_results_latest",
  "kind": "results_json",
  "original_path": "C:\\panda-gallery\\workflows\\results_latest.json",
  "package_path": "source/results_latest.json",
  "required": true,
  "sha256": "hex",
  "bytes": 12345,
  "captured_at": "2026-04-24T20:12:55-07:00"
}
```

Required source kinds for a complete audit package:

- `results_json`
- at least one `evidence` record, unless session has no failures and no manual screenshots
- `metadata_json` when workflow capture session exists
- `transcript_markdown` when audio/transcription exists

Stage 1 also hash-tracks derived package files as source records after they are generated:

- `ai_extraction_input`
- `package_summary`
- `packaging_log`

## Package Source

`package_source` records where the package was built from and preserves the local-only mutation boundary.

```json
{
  "source_kind": "panda_gallery_workflows",
  "source_root": "C:\\panda-gallery\\workflows",
  "results_path": "C:\\panda-gallery\\workflows\\results_latest.json",
  "latest_pointer_path": "C:\\panda-gallery\\workflows\\LATEST.txt",
  "packaged_from_live_pg": true,
  "source_mutation_policy": "read_only"
}
```

`latest_pointer_path` may be `null`. For Stage 1, absolute Windows paths are acceptable because package output is local-only under `C:\CODEX PG`; redaction or relativization is required before external transfer.

Implementation note: the PG v4.34 builder assumes `BuildContext.source_dir` points at the PG `workflows/` directory. Screenshot references that begin with `workflows/...` are resolved by checking `source_dir`, `source_dir.parent`, and `source_dir.parent.parent`.

## Warning Records

`warnings[]` is the canonical missing-source and package-readiness warning surface. `missing_sources[]` is deprecated and must not be emitted by new Stage 1 packages.

```json
{
  "code": "optional_source_missing",
  "severity": "warning",
  "message": "Optional source not found: transcript_markdown",
  "path": "manifest.sources[transcript_markdown]",
  "action": "review_before_external_transfer",
  "context": {
    "kind": "transcript_markdown",
    "required": false,
    "candidates": ["transcript.md", "transcripts/transcript.md"]
  }
}
```

Allowed warning codes:

| Code | Required Severity | Meaning |
| --- | --- | --- |
| `optional_source_missing` | `warning` | Optional source artifact was not found. Common in real sessions. |
| `required_source_missing` | `blocking` | Required source artifact was not found. Package cannot be `local_ready`. |
| `source_unreadable` | `blocking` | Source artifact exists but cannot be read or copied. |
| `evidence_missing` | `blocking` | Referenced evidence cannot be resolved. |
| `checklist_results_missing` | `warning` | Step is `kind=checklist` but has no checklist result payload. |

## Evidence Records

Every screenshot, frame, transcript span, or derived artifact that can support an issue gets an `evidence_id`.

Evidence ID format:

```text
ev_<kind>_<zero_padded_sequence>
```

Examples:

- `ev_region_0001`
- `ev_step_auto_0002`
- `ev_workflow_frame_0017`
- `ev_transcript_span_0003`

Evidence object:

```json
{
  "evidence_id": "ev_region_0001",
  "kind": "region_screenshot",
  "label": "Step 1 manual region capture",
  "step_n": 1,
  "source_path": "C:\\panda-gallery\\workflows\\screenshots\\run_abc\\region_1_001.png",
  "package_path": "evidence/ev_region_0001.png",
  "remote_path": null,
  "mime_type": "image/png",
  "sha256": "hex",
  "bytes": 456789,
  "created_at": "2026-04-24T19:46:05-07:00",
  "capture": {
    "capture_type": "manual_region",
    "include_cursor": false,
    "monitor_index": null,
    "bounds": null
  },
  "transcript_ref": null,
  "discarded": false,
  "privacy": {
    "contains_phi": "unknown",
    "deidentified": false,
    "redaction_state": "not_reviewed"
  }
}
```

Evidence kinds:

| Kind | Source |
| --- | --- |
| `step_auto_screenshot` | Auto screenshot captured on FAIL. |
| `region_screenshot` | Shift+F12 manual region capture. |
| `workflow_frame` | F12 workflow frame from session folder. |
| `transcript_span` | Time-bounded transcript segment or phrase range. |
| `audio_clip` | Optional future derived clip, not required in v1. |
| `package_summary` | Derived Markdown or JSON summary. |

## Transcript References

Transcript references are evidence-linked objects rather than raw line numbers only.

```json
{
  "transcript_ref_id": "tr_0003",
  "transcript_source": "source/transcript.md",
  "start_seconds": 12.4,
  "end_seconds": 18.9,
  "text_excerpt": "short excerpt only",
  "frame_ids": ["ev_workflow_frame_0014", "ev_workflow_frame_0015"]
}
```

Do not store long transcript text redundantly inside issue records. Store short excerpts for review context and link back to the source transcript.

## Step Records

Manifest `steps[]` normalizes existing `results_latest.json` into package form.

```json
{
  "step_n": 1,
  "kind": "checklist",
  "title": "Overlay + drag + flash + toast",
  "outcome": "FAIL",
  "note": "Tester note if present",
  "evidence_ids": ["ev_step_auto_0001", "ev_region_0001"],
  "source_result_index": 0,
  "test_id": "T1",
  "checklist_results": [
    {
      "id": "item_0",
      "label": "Screen dimmed (translucent black overlay)",
      "outcome": "PASS",
      "note": null
    }
  ]
}
```

`source_result_index` is 0-based and is for correlation back to `results_latest.json`. `step_n` is 1-based and is for display and reviewer-facing references. `test_id` is optional and may include lineage suffixes such as `T8_REAUTH`. `checklist_results` is a list for `kind=checklist` and `null` for `kind=single` or `kind=action`.

Allowed outcomes:

- `PASS`
- `FAIL`
- `SKIP`
- `ACK`
- `PARTIAL`
- `null` for placeholder evidence records before final tester outcome

## Upload Contract

Dropbox upload writes package files without changing evidence IDs.

```json
{
  "provider": "dropbox",
  "queue_id": "upl_20260424_201300_991c",
  "remote_root": "/Panda Gallery Audit/session_package_session_20260424_194422",
  "state": "remote_ready",
  "started_at": "2026-04-24T20:13:00-07:00",
  "completed_at": "2026-04-24T20:14:10-07:00",
  "files": [],
  "completion_marker": {
    "path": "_PACKAGE_READY.json",
    "sha256": "hex"
  }
}
```

Remote processing must wait for `_PACKAGE_READY.json`, not merely the presence of uploaded files.

## Integrity Contract

`integrity` includes:

```json
{
  "hash_algorithm": "sha256",
  "manifest_without_integrity_sha256": "hex",
  "file_count": 17,
  "total_bytes": 12345678,
  "generated_by_version": "pg-package-contract-v1"
}
```

The packager must hash every copied or derived file and record missing or unreadable files in structured `warnings[]`. To avoid self-referential hashing, `manifest_without_integrity_sha256` is computed from a copy of the manifest whose `integrity` field is `{}`, then the final `integrity` block is assigned.

## AI Extraction Input

File: `derived/ai_extraction_input_v1.json`

This is a provider-neutral deterministic input for issue extraction.

```json
{
  "schema": "pg.ai_extraction_input.v1",
  "package_id": "pkg_20260424_201255_8f3b2a",
  "session_id": "session_20260424_194422",
  "run_id": "run_20260424_194435",
  "steps": [],
  "evidence": [],
  "transcript_refs": [],
  "constraints": {
    "do_not_invent_evidence": true,
    "issue_must_reference_evidence_id": true,
    "prefer_concise_titles": true
  }
}
```

## Validation Rules

Minimum validation for `local_ready`:

1. `schema` equals `pg.session_package.v1`.
2. `package_id`, `session_id`, and `run_id` are present.
3. Every `evidence_id` is unique.
4. Every `steps[].evidence_ids[]` value exists in `evidence[]`.
5. Every copied file has `sha256` and `bytes`.
6. Required sources are present; any missing required source is represented by a `warnings[]` entry with `severity: "blocking"`.
7. Package paths are relative and do not escape the package folder.
8. `C:\panda-gallery` source files are never modified by packaging.
9. `manifest.missing_sources` is deprecated; validators may soft-warn for legacy samples, but new packages must use `warnings[]`.
10. `package_state` cannot be `local_ready` when `warnings[]` contains a blocking warning.

## First Local Vertical Slice

The first implementation should:

1. Read a completed `results_latest.json`.
2. Copy referenced screenshots into `evidence/`.
3. Copy latest session `metadata.json` and `transcript.md` when available.
4. Generate evidence IDs and normalized step records.
5. Write `session_package_manifest.json`.
6. Write `derived/ai_extraction_input_v1.json`.
7. Validate `local_ready`.
