# CODEX Testing + Audit Architecture v1

Generated: 2026-04-24

Status: Codex canonical draft for PG Testing + Audit MVP v1.

Scope: defines the implementation architecture for turning an already completed Panda Gallery tester session into a packaged, transferred, AI-triaged, human-approved, emailed, and searchable audit record. This document depends on `CODEX_SESSION_PACKAGE_SCHEMA_v1.md` and `CODEX_AUDIT_ISSUE_SCHEMA_v1.md`.

## Architecture Goals

- Keep Panda Gallery capture/transcription behavior upstream and unchanged for MVP v1.
- Build the Testing + Audit path as a deterministic pipeline with explicit state transitions.
- Preserve evidence lineage from source session output through package, AI issue, approval, email draft, and archive record.
- Start with a local-only prototype under `C:\CODEX PG`, then add Dropbox, AI, and email adapters behind stable interfaces.
- Avoid writing to `C:\panda-gallery`; it remains a read-only reference/source input unless Darrin explicitly changes that boundary.

## MVP Boundary

Included in MVP v1:

- Read completed tester session outputs.
- Normalize session steps, screenshots, transcript references, and metadata into a session package.
- Validate package integrity and mark it local-ready.
- Prepare deterministic AI extraction input.
- Transfer immutable packages to Dropbox only after local readiness exists.
- Extract evidence-linked issues with AI.
- Let a human reviewer approve, reject, defer, or revise issues and response drafts.
- Generate shared team email records from approved text.
- Write searchable archive records that preserve audit lineage.

Excluded from MVP v1:

- Rebuilding audio capture or transcription.
- Broad changes to the clinical Panda Gallery desktop app.
- Processing real PHI without a Testing + Audit compliance addendum and explicit operating decision.
- Live email sending before local draft records and approval records are proven.
- AI issues that do not cite package evidence IDs.

## System Context

```text
Panda Gallery capture outputs (read-only for Codex)
  -> Local session packager
  -> Local package validator
  -> AI extraction input builder
  -> Dropbox transfer adapter
  -> Backend processing worker
  -> AI issue extractor
  -> PG audit dashboard
  -> Approval workflow
  -> Shared email adapter
  -> Searchable audit archive
```

For the first prototype, Dropbox, backend processing, AI, and email may be replaced by local file adapters that write deterministic JSON records under `C:\CODEX PG`.

## Component Responsibilities

| Component | Responsibility | First Prototype Form |
| --- | --- | --- |
| Source Session Reader | Locate and read `results_latest.json`, session metadata, screenshots, transcript, and latest markers. | Python module reading copied/sample session folders or read-only PG outputs. |
| Package Builder | Copy source artifacts, assign evidence IDs, normalize steps, create manifest, and write derived AI input. | Local CLI/script under a Codex folder. |
| Package Validator | Enforce schema, evidence references, file hashes, relative paths, and missing source records. | Local Python validator. |
| Transfer Queue | Move local-ready packages to upload queue and preserve immutability. | Local queue JSON first, Dropbox later. |
| Dropbox Adapter | Upload package files and write `_PACKAGE_READY.json` only after successful transfer. | Deferred adapter boundary. |
| Processing Worker | Detect remote-ready package and launch extraction. | Local watcher or manual command first. |
| AI Extraction Adapter | Submit deterministic package input to selected AI provider and parse issue output. | Local fixture/mock first. |
| Issue Store | Persist issue extraction results and reviewer edits without overwriting AI fields. | JSON files first; SQLite acceptable for dashboard prototype. |
| Audit Dashboard | Let PG reviewer inspect packages, evidence, issue drafts, status, and final response text. | PySide6 desktop module. |
| Approval Store | Preserve approval records, status events, reviewer identity, and approved text. | JSON records first. |
| Email Adapter | Generate/send shared team email from approved issue response. | Draft-only records first; provider adapter later. |
| Archive Writer | Write immutable searchable records after closure. | JSONL first; SQLite/search index later. |

## Local Folder Layout

Recommended Codex-owned prototype root:

```text
C:\CODEX PG\CODEX Audit Prototype\
  CODEX Session Packages\
  CODEX Issue Extractions\
  CODEX Approval Records\
  CODEX Email Drafts\
  CODEX Archive\
  CODEX Logs\
  CODEX Config\
```

Recommended source code root when implementation begins:

```text
C:\CODEX PG\CODEX Desktop App\
  pyproject.toml
  src\codex_pg_audit\
    package_builder\
    validation\
    transfer\
    extraction\
    review\
    archive\
    ui\
  tests\
```

## Pipeline States

The package state machine is owned by `session_package_manifest.json`:

```text
draft
  -> local_ready
  -> queued_for_upload
  -> uploading
  -> uploaded_pending_verification
  -> remote_ready
  -> processing
  -> triage_ready
  -> archived
```

Failure states:

```text
processing_failed
email_failed
```

Rules:

- Only `local_ready` packages can be queued for upload.
- Dropbox writes `_PACKAGE_READY.json` last.
- Backend processing starts only after remote readiness is confirmed.
- AI extraction cannot create reviewable issues without evidence IDs from the package manifest.
- Archive records are written only from closed, approved/rejected/deferred issue state.

## Evidence Lineage

Evidence ID is the durable join key across the whole system.

```text
source screenshot/transcript/frame
  -> package evidence record: ev_<kind>_<sequence>
  -> AI issue evidence_ids[]
  -> reviewer approved evidence_ids[]
  -> email record issue_id/approval_id
  -> archive record evidence_ids[]
```

Rules:

- Never use bare screenshot paths as primary issue references.
- Never allow AI output to reference evidence not present in the package manifest.
- Preserve discarded evidence as an evidence record only when it is relevant to audit integrity, and mark `discarded: true`.
- Store short transcript excerpts only for context; link back with transcript refs.

## Data Stores

Local prototype storage can use flat files for clarity:

| Store | Format | Purpose |
| --- | --- | --- |
| Session packages | Folder plus JSON manifest | Immutable session artifact set. |
| Issue extractions | JSON | AI output and warnings. |
| Approval records | JSON | Reviewer-approved text and evidence. |
| Email drafts | JSON and optional Markdown | Shared team response drafts. |
| Archive | JSONL | Append-friendly searchable audit records. |
| Logs | JSONL | Packaging, validation, transfer, extraction, email events. |

SQLite becomes useful when the dashboard needs faster filtering, multi-package search, or cross-session issue views. It should mirror canonical JSON records, not replace them as the only source of truth in early MVP.

## Adapter Boundaries

Adapters should be small, replaceable classes or modules.

| Adapter | Stable Input | Stable Output |
| --- | --- | --- |
| Dropbox transfer | `local_ready` package folder | Upload record plus completion marker. |
| AI extraction | `ai_extraction_input_v1.json` | `audit_issue_extraction_v1.json`. |
| Email | Approval record | Email delivery record. |
| Archive search | Closed issue plus approval/email records | Archive JSONL/SQLite record. |

Each adapter must support a no-network local mode for tests and demos.

## Dashboard UX Architecture

The audit dashboard should be a PySide6 desktop surface with the Panda Gallery visual vocabulary:

- Dark desktop shell.
- Compact panes and dense rows.
- Low-radius controls.
- Muted separators and quiet secondary text.
- Peach active accent `#e8a87c`.
- Green pass/approved state.
- Red fail/high-risk state.
- Stable bottom action bar for approve/reject/defer/email/archive actions.
- Evidence preview remains attached to the selected issue and step.

Recommended first dashboard views:

| View | Purpose |
| --- | --- |
| Package Inbox | Shows local-ready, triage-ready, and archived packages. |
| Issue Review | Shows extracted issues, evidence, transcript refs, reviewer edits, and approval actions. |
| Email Draft | Shows approved team response before send/queue. |
| Archive Search | Searches closed issue records by title, category, priority, text, and tags. |

## Compliance And Privacy Guardrails

Until the compliance addendum exists:

- Treat all real patient data as out of scope.
- Prefer synthetic/de-identified sessions for development.
- Mark evidence privacy as `unknown` unless a reviewer or redaction process has confirmed it.
- Do not upload real data to Dropbox, AI providers, or email systems.
- Do not log long transcript text, PHI, access tokens, or provider secrets.
- Keep local prototype config separate from records and exclude secrets from git.

## Error Handling

Every pipeline step writes structured events to JSONL logs.

Minimum event fields:

```json
{
  "created_at": "2026-04-24T21:30:00-07:00",
  "component": "package_builder",
  "level": "info",
  "event_type": "package_created",
  "package_id": "pkg_example",
  "session_id": "session_example",
  "message": "Package reached local_ready."
}
```

Rules:

- Missing optional source files become manifest warnings.
- Missing required source files either block `local_ready` or appear in `missing_sources[]` with a clear reason.
- Hash mismatches block upload.
- AI extraction parse failures create warnings/errors, not partial silent issues.
- Email failures preserve the approved text and allow retry without re-approval unless approved content changes.

## Testing Strategy

Minimum tests for first implementation:

- Package builder creates stable folder layout from sample session input.
- Manifest validates after package build.
- Evidence IDs are unique and referenced step IDs exist.
- Missing optional transcript produces a warning, not a crash.
- Missing required results JSON prevents `local_ready`.
- AI extraction fixture cannot reference unknown evidence IDs.
- Approval events preserve AI fields and append reviewer fields separately.
- Archive writer produces searchable JSONL records with hashes.

Use synthetic sample sessions under Codex-owned folders. Do not mutate `C:\panda-gallery` during tests.

## Implementation Sequence

1. Create the `CODEX Desktop App` Python scaffold with package builder and validation modules.
2. Promote the starter-pack reference builder/validator into typed modules with tests.
3. Build local prototype storage under `CODEX Audit Prototype`.
4. Add deterministic fixture-based AI extraction output and validation.
5. Add simple PySide6 dashboard reading local JSON records.
6. Add approval, email draft, and archive writer flows.
7. Add Dropbox transfer adapter after local package immutability is proven.
8. Add real AI and email adapters only after compliance and provider decisions.

## Open Decisions

| Decision | Default Until Decided |
| --- | --- |
| Real PHI allowed? | No. Synthetic/de-identified only. |
| Dropbox account and remote folder? | Local transfer adapter only. |
| AI provider/model? | Fixture/mock extraction only. |
| Shared email provider/inbox? | Draft-only local email records. |
| Reviewer identity source? | Manual display name string. |
| Dashboard database? | JSON files first; SQLite when filtering/search requires it. |
| Archive retention policy? | Append-only local JSONL until compliance addendum defines retention. |

## Definition Of Done For Local Architecture Slice

The architecture slice is complete when a synthetic completed session can be converted into:

1. A validated `local_ready` package.
2. A deterministic AI extraction input file.
3. A fixture-based issue extraction result with valid evidence IDs.
4. A reviewer approval record.
5. A draft-only email record.
6. An archive JSONL record searchable by title/category/priority/text.

All artifacts must stay under `C:\CODEX PG`, and `C:\panda-gallery` must remain unchanged.
