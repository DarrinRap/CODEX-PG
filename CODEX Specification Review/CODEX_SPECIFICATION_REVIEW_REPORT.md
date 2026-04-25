# CODEX Specification Review Report

Generated: 2026-04-24 19:18 PT

## Scope Reviewed

Reviewed the canonical Panda Gallery specification corpus in `C:\CODEX PG\CODEX CLAUDE PG DATA`, plus the external `PG_Testing_Audit_MVP_v1_Spec.docx` extracted into this review folder.

Included:

- 22 canonical text/specification/planning documents.
- 1 external MVP DOCX extract.
- Region-capture design spec.
- Testing results schema and guided-testing specs.
- Remote-testing, workflow-capture, transcription, Dropbox/upload, MCP ingest, compliance, architecture, style, and v4 planning docs.

Excluded from substantive review:

- Duplicate snapshot files under `workflows\project_knowledge_sync_2026-04-23` unless needed for drift awareness.
- PyInstaller `.spec` build files because they are build configuration, not product specification.
- HTML visual mockups as implementation inspiration; they are referenced as design artifacts but not treated as normative spec text.

Generated support files:

- `CODEX_SPEC_REVIEW_MANIFEST.csv`
- `CODEX_SPEC_HEADING_DIGEST.md`
- `CODEX_PG_TESTING_AUDIT_MVP_SPEC_EXTRACT.txt`

## Executive Verdict

The specification corpus is unusually rich and often technically precise. The strongest documents are `TESTING_SECTION_SPEC.md`, `PANDA_GALLERY_REMOTE_TESTING_SPEC_draft4.md`, `PANDA_GALLERY_TRANSCRIPT_V2_SPEC.md`, and `workflows\design\region_capture_v1_DRAFT.md`; they define concrete flows, schemas, and acceptance criteria.

The main weakness is not lack of detail. It is source-of-truth fragmentation. Several documents are excellent in isolation but now describe overlapping or superseded worlds: core PG v4 product planning, remote testing tooling, Claude-side ingest, compliance posture, and the newer Testing + Audit MVP. The next high-value step is not to write more feature prose. It is to create a short master index and a canonical Testing + Audit v1 architecture/data-contract spec that reconciles the existing pieces.

## Highest-Priority Findings

### P0 - Testing + Audit MVP changes the compliance posture immediately

The compliance spec currently says third-party processor risk is clean because Whisper runs locally and no PHI leaves the machine. The Testing + Audit MVP requires Dropbox transfer, backend audit processing, AI issue extraction, shared team email, and a searchable archive. Those are not small implementation details; they trigger the compliance spec's own cloud-service warnings.

Action needed before external or real-PHI use:

- Define whether tester sessions may contain PHI.
- Decide whether captures/transcripts must be de-identified before upload.
- Add a subprocessor list: Dropbox, AI provider, email provider, hosting/database provider.
- Determine BAA requirements before any real practice data leaves the workstation.
- Define retention, deletion, access control, and audit logging for uploaded sessions and archived issues.

### P0 - There are two different MVPs that must be kept separate

`PG_V4_MVP_PLAN.md` says v4.0 has no visible AI features, no installer, no HIPAA-basics, and distribution-layer work deferred. The Testing + Audit MVP says MVP v1 depends on Dropbox transfer, backend AI triage, approval workflow, email, and searchable archive.

These can both be true only if they are treated as different product tracks:

- PG core app v4.0: internal clinical imaging product, AI plumbing only.
- PG Testing + Audit MVP v1: testing pipeline/audit workflow, allowed to use AI/cloud because it is a separate audit system with its own compliance controls.

Action needed: create a one-page product-track boundary so implementers do not import the v4.0 no-visible-AI/no-cloud-distribution rule into the audit module, or accidentally use audit cloud assumptions inside the clinical app.

### P1 - No canonical end-to-end data contract exists for Testing + Audit v1

The building blocks exist: `results_latest.json`, screenshots, transcript format, Dropbox folder layout, `test_report.md`, `manual_screenshots`, and region capture paths. What is missing is a single package contract that says exactly what the backend receives and what the audit dashboard produces.

Missing canonical schemas:

- `session_package_manifest.json`
- transcript metadata contract
- screenshot/evidence object model
- AI extracted issue schema
- issue priority/category taxonomy
- response draft schema
- approval audit log schema
- archive search record schema

Without this, backend/audit work will infer from local app implementation details and drift quickly.

### P1 - Evidence identity is underspecified across screenshot, transcript, and issue extraction

`TESTING_SECTION_SPEC.md` has `screenshot` and `manual_screenshots[]`. Region capture adds `region_<step_n>_<seq>.png`. Transcript v2 ties speech to frame windows. But the audit module needs durable evidence IDs that survive upload, discard, retry, archiving, and search.

Action needed: introduce evidence records with stable IDs, not just file paths. Each evidence object should include local path, remote path, capture type, step number, transcript timestamp span, hash, created_at, discarded flag, and display label.

### P1 - Dropbox upload is well thought out but not enough for audit-grade transfer

`PANDA_GALLERY_REMOTE_TESTING_SPEC_draft4.md` has strong upload/retry/error handling. For the audit MVP, add durability and verification:

- local upload queue persisted across app restart
- per-file checksums or content hashes
- upload completion manifest
- idempotency keys to avoid duplicate backend sessions
- retry state visible after app relaunch
- explicit behavior when transcript finishes after package upload
- clear ready-for-backend-processing marker, not just Dropbox upload complete

### P1 - AI triage is specified as a workflow step, not as a product contract

The MVP says AI splits and categorizes issues. It does not yet specify issue taxonomy, confidence, deduplication, evidence linking, priority mapping, reviewer override, or how failures are represented.

Action needed: define `audit_issue_v1` with fields such as `issue_id`, `session_id`, `title`, `summary`, `category`, `priority`, `confidence`, `evidence_ids`, `transcript_refs`, `suggested_response`, `status`, `reviewer_edits`, and `created_by_model`.

### P1 - Approval/email/archive workflow needs an audit log spec

The MVP calls for PG approval, shared team email, close/archive. The current corpus does not yet define:

- who can approve
- what approve records
- how edited AI drafts are preserved
- email recipient source
- email threading/reply handling
- resend/failure behavior
- close reasons
- archive immutability versus editable notes

Action needed: define `approval_event_v1` and `email_delivery_v1` schemas before building the dashboard.

### P2 - Spec supersession is not consistently machine-readable

Some documents clearly state status and supersession. Others are older but still look authoritative. Example: `PG_V4_MVP_PLAN.md` explicitly retires older template/freeform specs as design authorities for v4.0 unified canvas, but those older specs still exist as large standalone documents.

Action needed: create `CODEX_MASTER_SPEC_INDEX.md` with each document marked as one of: canonical, current reference, superseded, historical, implementation artifact, or duplicate snapshot.

## Recommended New Canonical Documents

Create these before major implementation:

1. `CODEX_MASTER_SPEC_INDEX.md`
   - One table listing every spec, owner, status, supersedes/superseded-by, and whether it applies to PG core app, testing module, audit backend, or Claude tooling.

2. `CODEX_TESTING_AUDIT_ARCHITECTURE_v1.md`
   - The canonical end-to-end architecture for Testing + Audit MVP v1.
   - Should explicitly say audio/transcription are already working and are treated as upstream inputs.

3. `CODEX_SESSION_PACKAGE_SCHEMA_v1.md`
   - Defines local package, Dropbox package, manifest, checksums, evidence IDs, transcript refs, and upload completion semantics.

4. `CODEX_AUDIT_ISSUE_SCHEMA_v1.md`
   - Defines AI issue extraction output, categories, priorities, reviewer edits, and approval states.

5. `CODEX_AUDIT_DASHBOARD_UX_SPEC_v1.md`
   - Converts the storyboards into a buildable desktop/web dashboard spec with states and acceptance criteria.

6. `CODEX_COMPLIANCE_ADDENDUM_TESTING_AUDIT_v1.md`
   - Updates cloud, AI, email, archive, and retention posture for the audit pipeline.

## Document-by-Document Review

### PG Testing + Audit MVP v1 DOCX

Strongest value: excellent MVP constraint. It cleanly states that audio capture and timestamped transcription already work, so v1 begins after transcription exists.

Gaps:

- No data schemas.
- No role/permission model.
- No compliance posture for cloud/AI/email.
- No backend processing contract.
- No archive/search schema.

Recommendation: keep it as the product brief, not the developer spec. It should point to the new canonical architecture/schema docs.

### `PANDA_GALLERY_v4_SPEC_1.md`

Strongest value: broad original product vision and UI quality bar.

Risk: too broad and older than the v4 MVP plan. It should not be used as current scope authority.

Recommendation: mark as historical/vision reference. Use for taste and long-term direction, not for current implementation scope.

### `PG_V4_MVP_PLAN.md`

Strongest value: current authoritative scope for PG core v4.0. Excellent gating language and sequencing.

Risk: conflicts with Testing + Audit MVP if both are treated as one product. It defers visible AI and distribution-layer work, while audit MVP requires cloud/AI/email/archive.

Recommendation: keep authoritative for PG core app only. Add a product-track boundary note.

### `PANDA_GALLERY_REMOTE_TESTING_SPEC_draft4.md`

Strongest value: extremely concrete phased spec for floating pane, session capture, microphone, Dropbox upload, and reporting.

Risks:

- Status says for Darrin review and target versions v3.50-v3.54; implementation has moved on.
- Dropbox phase is oriented around uploading session folders, not audit-grade package contracts.
- Some details are now superseded by `TESTING_SECTION_SPEC.md` and region-capture work.

Recommendation: mine it for implementation detail, especially upload/retry and mic behavior, but promote only current sections into the new Testing + Audit architecture spec.

### `TESTING_SECTION_SPEC.md`

Strongest value: best current specification for guided PASS/FAIL/checklist flow, result persistence, and authoring rules. The results JSON schema is a strong foundation.

Risks:

- Results file is local-pane oriented, not audit-backend oriented.
- `manual_screenshots[]` are paths, not durable evidence records.
- Open questions remain around resume behavior, failing action versus failing state, multi-user testing, and live chat limitations.

Recommendation: treat as canonical for tester-pane behavior; extend with package/evidence schema rather than overloading `results_latest.json`.

### `workflows\design\region_capture_v1_DRAFT.md`

Strongest value: implementation-ready. It has clear states, edge cases, acceptance criteria, path policy, and UI rules.

Risks:

- Active-session definition combines recording state and instruction-pane current step; audit packaging needs one canonical session identity.
- Recording timeline integration is deferred, which can leave region captures linked to `manual_screenshots[]` but not the main frame timeline.
- Cursor inclusion and discard cleanup need privacy/security review if screenshots can contain PHI.

Recommendation: implement, but introduce evidence IDs and package manifest hooks at the same time.

### `drafts\WORKFLOW_CAPTURE_SPEC.md`

Strongest value: mature capture-session foundation.

Risk: should be reconciled with shipped implementation and later remote-testing/transcription specs.

Recommendation: use as a lower-level capture reference. The audit module should depend on a public session package contract, not internals.

### `PANDA_GALLERY_TRANSCRIPTION_SPEC.md` and `PANDA_GALLERY_TRANSCRIPT_V2_SPEC.md`

Strongest value: transcript v2 gives machine-readable screen trace and frame duration context, exactly what AI issue extraction will need.

Risk: the Testing + Audit MVP says transcription already works, so further transcription changes should not creep into v1 unless they directly support evidence alignment.

Recommendation: freeze transcript as an input contract. Define what fields the audit pipeline relies on and avoid reworking Whisper/transcription unless evidence alignment breaks.

### `PANDA_GALLERY_AUTOTRANSCRIBE_SPEC.md`

Strongest value: clear autotranscribe implementation outline and failure behavior.

Risk: now mostly historical if audio/transcription are already shipped.

Recommendation: mark as implemented/reference. Testing + Audit should cite it only as upstream behavior.

### `PANDA_GALLERY_COMPLIANCE_SPEC.md`

Strongest value: candid risk register and good inflection-point framing.

Risk: materially outdated the moment Dropbox, AI, email, or backend archive are introduced.

Recommendation: create a Testing + Audit compliance addendum before building cloud transfer beyond local/demo data.

### `PANDA_GALLERY_MCP_SESSION_INGEST_SPEC_draft2.md`

Strongest value: excellent Claude-side tooling spec. It explains latest-session ingest, transcript-aware frame selection, and graceful degradation.

Risk: it is not a product backend. Do not confuse Claude ingest for audit ingestion.

Recommendation: keep as dev/testing tooling. The audit backend should have its own deterministic ingestion contract.

### `PANDA_GALLERY_SESSION_MANAGER_SKILL_SPEC.md` and `HANDOFF_FORMAT_SPEC.md`

Strongest value: strong session continuity/handoff discipline.

Risk: Claude-specific process specs should not drive product UI or backend schema.

Recommendation: keep as development process docs. Mirror useful concepts in Codex handoff automation where appropriate.

### `ARCHITECTURE.md` and `STYLE.md`

Strongest value: architecture and engineering quality guardrails.

Risk: some assessments may age quickly as implementation changes.

Recommendation: keep as active engineering references; update when new modules become real.

### `GUIDED_TESTING_STYLE.md`

Strongest value: practical authoring rules for tests that are actually observable through the pane.

Recommendation: keep as canonical for writing test scripts. It should be referenced by any future testing-authoring UI.

### Template, split-template, freeform, multimonitor, image-info specs

Strongest value: detailed original feature thinking and edge cases.

Risk: `PG_V4_MVP_PLAN.md` supersedes template/freeform as current design authority via unified canvas.

Recommendation: mark as historical or reference-only where superseded. Extract reusable edge cases into the new arrangement-canvas spec when implementation begins.

### `workflows\design\v4_0\PG_V4_CUSTOMIZATION_PLAN.md`

Strongest value: design planning adjunct for v4.0 UI customization.

Recommendation: treat as supporting design input under `PG_V4_MVP_PLAN.md`, not as independent scope authority.

## Immediate Implementation Guidance

If the next step is building code, start with the narrowest vertical slice:

1. Define `session_package_manifest.json`.
2. Implement evidence IDs for screenshots and transcript references.
3. Package an existing completed session locally without Dropbox.
4. Add a deterministic local AI-extraction-input JSON file.
5. Only then wire Dropbox transfer.
6. Only then build AI issue extraction and dashboard approval.

This order respects the MVP rule: session capture -> transfer -> AI triage -> PG approval speed -> searchable audit integrity.

## Proposed Next Codex Tasks

1. Create `CODEX_MASTER_SPEC_INDEX.md`.
2. Draft `CODEX_SESSION_PACKAGE_SCHEMA_v1.md`.
3. Draft `CODEX_AUDIT_ISSUE_SCHEMA_v1.md`.
4. Update the interface storyboard to include evidence IDs and package states.
5. Begin PySide6 implementation only after schemas are stable enough to code against.

## Bottom Line

The project has enough specification material to proceed, but not yet enough canonical integration material. The fastest path is to consolidate, not expand: index the specs, draw boundaries between PG core and Testing + Audit, define the package/evidence/issue schemas, then implement the smallest local vertical slice.
