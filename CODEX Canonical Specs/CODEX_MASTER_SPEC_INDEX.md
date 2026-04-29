# CODEX Master Spec Index

Generated: 2026-04-28

Purpose: define which Panda Gallery documents are canonical, current reference, historical, superseded, implementation artifacts, or development-process guidance for the PG Testing + Audit track.

This index is Codex-owned and lives outside the live Claude/Panda Gallery source tree. `C:\panda-gallery` remains read-only reference for Codex unless Darrin explicitly says otherwise.

## Status Legend

| Status | Meaning |
| --- | --- |
| Canonical | Current source of truth for the named scope. |
| Current reference | Still useful and mostly current, but not sufficient as the only authority. |
| Historical | Valuable background or product intent, but not current implementation scope authority. |
| Superseded | Replaced for current planning by a newer document or implementation. |
| Implementation artifact | Describes a shipped or draft implementation detail; use after checking current code. |
| Process guidance | Guides development workflow rather than product behavior. |
| Codex canonical | Codex-authored bridge document intended to become the current working contract for Testing + Audit. |

## Product Track Boundary

Panda Gallery now has two related but distinct tracks:

| Track | Scope | Current authority |
| --- | --- | --- |
| PG Core v4 | Clinical desktop imaging app: Library, Mount, Review, Compare, Present, canvas/workflow UX. | `PG_V4_MVP_PLAN.md`, plus current source behavior in `C:\panda-gallery`. |
| PG Testing + Audit MVP v1 | Tester session packaging, Dropbox transfer, AI issue extraction, approval workflow, shared email communication, searchable archive. | `PG_Testing_Audit_MVP_v1_Spec.docx` as product brief, plus Codex canonical specs in this folder as implementation contracts. |
| Claude tooling/process | Claude handoff, session ingest, local testing authoring, dev workflow. | Claude process specs and shipped scripts. |

Rules:

- PG Core v4 rules such as no visible AI and no distribution-layer work apply to the clinical app track, not automatically to Testing + Audit.
- Testing + Audit cloud, AI, email, and archive work must not be silently imported into the clinical app without its own compliance and product decision.
- Audio capture and timestamped transcription are treated as upstream inputs for Testing + Audit MVP v1.

## Canonical Codex Specs

| Document | Status | Applies to | Role |
| --- | --- | --- | --- |
| `CODEX_MASTER_SPEC_INDEX.md` | Codex canonical | Testing + Audit, PG Core boundary | Source-of-truth map and supersession guide. |
| `CODEX_SESSION_PACKAGE_SCHEMA_v1.md` | Codex canonical | Testing + Audit | Session package, manifest, evidence ID, upload readiness, and integrity contract. |
| `CODEX_AUDIT_ISSUE_SCHEMA_v1.md` | Codex canonical | Testing + Audit | AI issue extraction, reviewer state, approval, email, and archive data contract. |
| `CODEX_TESTING_AUDIT_ARCHITECTURE_v1.md` | Codex canonical | Testing + Audit | Pipeline architecture, component boundaries, local prototype sequence, adapter seams, and dashboard/storage responsibilities. |
| `CODEX_AUDIT_DASHBOARD_UX_SPEC_v1.md` | Codex canonical | Testing + Audit | Dashboard views, visual alignment, evidence review workflow, approval/email/archive UX, and local prototype acceptance criteria. |
| `CODEX_COMPLIANCE_ADDENDUM_TESTING_AUDIT_v1.md` | Codex canonical | Testing + Audit | Privacy, PHI, Dropbox, AI, email, archive, logging, and stop-condition guardrails for MVP development. |
| `RELAY_SPEC_v0.3.md` | Codex canonical | PG Core Relay module | Role-aware Relay hub, duplicate detection/resolution, message templates, Dropbox receipts, tester/developer views, tester setup wizard, invite codes, BUGS.md capture, status updates, and settings contract. |
| `RELAY_SPEC_v0.2.md` | Superseded | PG Core Relay module | Superseded by v0.3 after Relay tester setup Q&A decisions and §16 onboarding wizard amendment. |
| `RELAY_SPEC_v0.1.md` | Superseded | PG Core Relay module | Historical base spec for the two-sided asynchronous bug-report relay. Superseded by v0.2 after Screen C hub decisions. |

Recommended next Codex canonical docs:

- None. The next best step is implementation scaffolding for the local-only package builder and validator.

## Reviewed Source Corpus

| Document | Status | Applies to | Use Now | Notes |
| --- | --- | --- | --- | --- |
| `PG_Testing_Audit_MVP_v1_Spec.docx` extract | Canonical | Testing + Audit product brief | Defines MVP goal and exclusions. | Product brief only; lacks schemas and compliance detail. Audio/transcription already exist. |
| `TESTING_SECTION_SPEC.md` | Canonical | Guided tester pane | Current authority for pane behavior, instruction authoring, PASS/FAIL/checklist/action flow, and local results JSON. | Extend through package/evidence schema rather than overloading `results_latest.json`. |
| `PANDA_GALLERY_REMOTE_TESTING_SPEC_draft4.md` | Current reference | Testing + Audit, upload/session concepts | Mine for Dropbox upload, retry, mic/session flow, and dashboard concepts. | Older target versions; some behavior superseded by shipped pane/region code. |
| `PANDA_GALLERY_TRANSCRIPT_V2_SPEC.md` | Current reference | Testing + Audit evidence alignment | Use as transcript/evidence input model. | Treat transcription as upstream; avoid rebuilding unless alignment breaks. |
| `PANDA_GALLERY_COMPLIANCE_SPEC.md` | Current reference | Compliance baseline | Baseline risk register. | Outdated once Dropbox/AI/email/archive are introduced; needs Testing + Audit addendum. |
| `workflows\design\region_capture_v1_DRAFT.md` | Implementation artifact | Screenshot evidence | Use for region capture states, UX, edge cases, and path policy. | Current live v4.23 implementation should be checked before relying on draft details. |
| `drafts\WORKFLOW_CAPTURE_SPEC.md` | Current reference | Workflow capture | Use for lower-level session capture concepts. | Audit package should depend on manifest contract, not internals. |
| `PANDA_GALLERY_AUTOTRANSCRIBE_SPEC.md` | Historical / implementation artifact | Transcription automation | Use only to understand shipped autotranscribe intent. | Mostly implemented upstream. |
| `PANDA_GALLERY_TRANSCRIPTION_SPEC.md` | Historical | Transcription | Background reference. | Transcript v2 is the stronger current reference. |
| `PANDA_GALLERY_MCP_SESSION_INGEST_SPEC_draft2.md` | Process guidance / implementation artifact | Claude tooling | Useful for Claude-side session ingest and frame selection ideas. | Not an audit backend contract. |
| `PANDA_GALLERY_SESSION_MANAGER_SKILL_SPEC.md` | Process guidance | Claude workflow | Development continuity only. | Do not use as product UX/backend authority. |
| `HANDOFF_FORMAT_SPEC.md` | Process guidance | Claude workflow | Handoff quality rules. | Not product behavior. |
| `GUIDED_TESTING_STYLE.md` | Process guidance / canonical authoring guidance | Guided testing | Use for writing observable pane tests. | Important for future testing-authoring UI. |
| `ARCHITECTURE.md` | Current reference | PG Core engineering | Use for existing edit/render/storage/panel architecture. | Check source before relying on any aged assessment. |
| `STYLE.md` | Current reference | PG Core engineering | Use for coding style and architectural guardrails. | Applies most strongly when editing live PG, which Codex is not doing by default. |
| `PG_V4_MVP_PLAN.md` | Canonical | PG Core v4 | Authority for clinical app MVP scope. | Does not define Testing + Audit cloud/AI/email scope. |
| `PANDA_GALLERY_v4_SPEC_1.md` | Historical | PG Core vision | Taste, ambition, long-term product context. | Too broad for current scope authority. |
| `workflows\design\v4_0\PG_V4_CUSTOMIZATION_PLAN.md` | Current reference | PG Core v4 UI | Supporting design input under v4 plan. | Not independent scope authority. |
| `PANDA_GALLERY_TEMPLATE_SPEC.txt` | Historical / superseded | PG Core arrangement | Mine edge cases only. | Unified canvas planning supersedes much of this as current direction. |
| `PANDA_GALLERY_SPLIT_TEMPLATE_SPEC.txt` | Historical / superseded | PG Core arrangement | Mine edge cases only. | Superseded by newer v4 planning. |
| `PANDA_GALLERY_FREEFORM_SPEC.txt` | Historical / superseded | PG Core arrangement | Mine edge cases only. | Superseded as standalone current authority. |
| `PANDA_GALLERY_MULTIMONITOR_SPEC.txt` | Current reference | PG Core / capture UX | Use for multi-monitor edge cases. | Check current code for actual behavior. |
| `PANDA_GALLERY_IMAGE_INFO_SPEC.txt` | Historical / current reference | PG Core metadata | Reference for image metadata ideas. | Not part of Testing + Audit MVP v1 unless evidence metadata requires it. |

## Implementation Priority

1. Freeze package, evidence, issue, architecture, dashboard UX, and compliance contracts.
2. Build a local-only session package generator against existing `results_latest.json`, screenshots, transcript, and metadata.
3. Add deterministic AI-extraction input JSON.
4. Add Dropbox transfer only after package readiness and integrity markers exist.
5. Add AI issue extraction, approval, shared email, and searchable archive after the package contract is stable.

## Open Canonical Decisions

| Decision | Needed Before | Default For Local Prototype |
| --- | --- | --- |
| May test data include real PHI? | Dropbox, AI, email, archive | No. Use synthetic/de-identified data. |
| Dropbox account/folder contract | Dropbox integration | Local package output only. |
| AI provider/model and BAA posture | AI extraction | Generate provider-neutral extraction input. |
| Email provider and shared inbox source | Approval/email workflow | Draft email records only; no send. |
| Durable backend/search store | Searchable archive | Local JSONL/SQLite archive prototype under Codex folder. |
| Approval roles and identities | Dashboard workflow | Single reviewer identity string in schema. |
