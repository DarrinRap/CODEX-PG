# Codex -> Claude: Tester-Report Round-Trip v1 Spec Complete

Generated: 2026-04-25 14:55:00 -07:00
From: Codex
To: Claude
Status: COMPLETE
Re: `20260425_142500_CLAUDE_to_CODEX_TASK_tester_report_roundtrip_v1_spec.md`

## Summary

Completed the requested Tester-Report Round-Trip v1 architecture spec. No files under `C:\panda-gallery\` were modified.

## Deliverable

`C:\CODEX PG\CODEX Canonical Specs\CODEX_TESTER_REPORT_ROUNDTRIP_v1_SPEC.md`

Line count: 859

## Source Context Read

- `C:\panda-gallery\workflows\audit\TESTER_REPORT_ROUNDTRIP_BRIEF_v1.md`
- `C:\panda-gallery\workflow_capture.py`
- `C:\panda-gallery\scripts\transcribe_latest.py`
- `C:\panda-gallery\PANDA_GALLERY_AUTOTRANSCRIBE_SPEC.md`
- `C:\panda-gallery\PANDA_GALLERY_TRANSCRIPT_V2_SPEC.md`
- `C:\panda-gallery\PANDA_GALLERY_COMPLIANCE_SPEC.md`
- `C:\panda-gallery\codex_audit\` package-builder/validator orientation
- `C:\panda-gallery\audit_module\` AM window/state-store orientation
- `C:\panda-gallery\BUGS.md` #134 and #97
- `C:\panda-gallery\workflows\audit\PG_TRUTH_v1.md`

## Core Architecture Proposed

- One PG binary, with tester mode outside `--dev` and developer mode inside AM under `--dev`.
- Tester-side code home: new `tester_reports/` peer package plus small workflow-capture hooks; no tester-side code in `audit_module/`.
- Developer-side Reports section inside AM as a peer to Bugs.
- Directory-with-manifest bundle format for v1, with `READY.json` written last as the atomic commit marker.
- One bundle equals one report for v1; multiple issues from one session become multiple report bundles referencing the same source session.
- Dropbox v1 modeled as local-folder sync through a pluggable `ReportTransport` interface, with Google Drive, OneDrive, SMB, and Tier B providers able to implement the same interface later.
- Redaction hook defined as a pipeline stage; Tier A blocks suspected PHI and prevents absolute Windows paths in shipped manifests.
- Separate local SQLite DBs: tester-side `tester_reports`/`report_responses`/events and developer-side `am_reports.db` tables.
- Polling every 5 minutes while app is open, with manifest/checksum validation and quarantine on malformed or conflicting bundles.
- Response payload includes configurable status, embedded label/terminal flag, optional free text, and links such as BUGS.md references.
- Tier A -> Tier B migration preserves `ReportTransport`, `RedactionStage`, manifest schema, DB state machines, and response schema.

## Darrin Questions Surfaced

1. Confirm bundle format: directory-with-manifest vs ZIP/tar.gz.
2. Confirm manifest schema fields, especially tier/redaction and file records.
3. Confirm status config home: Codex recommends AM-owned `workflows/audit/report_statuses.json` with status labels embedded in responses.
4. Decide tester identity storage: Codex recommends local profile plus QSettings mirror.
5. Confirm AM persistence: Codex recommends separate SQLite `am_reports.db`, not extending existing AM issue JSON.
6. Confirm dedupe behavior: same bundle ID + same hash skips; same ID + different hash quarantines.
7. Confirm failed delivery UX: pending upload with retry and visible `last_error`.
8. Confirm one bundle equals one report for v1.
9. Confirm redaction interface placement: Codex recommends pre-upload inspection, optional AM re-run later.
10. Decide size caps and archive/prune policy; Codex suggests warning at 50 MB and explicit confirmation above 100 MB for Tier A.
11. Confirm Dropbox as v1 transport while keeping alternatives behind interface.
12. Confirm quarantine behavior for schema/security validation failures.
13. Define clinical-tester onboarding before any real-PHI external clinician use.

## Notes

- The spec composes with workflow capture, auto-transcribe, transcript v2, AM v0/v0.1, and codex_audit; it does not propose changes to those shipped pieces.
- `C:\panda-gallery\` remained read-only.
- Harness remains paused.
