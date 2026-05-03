# CODEX Tester Report Round-Trip v1.1 Spec

Status: DRAFT FOR DARRIN REVIEW
Date: 2026-05-02
Author: Codex
Supersedes: `CODEX_TESTER_REPORT_ROUNDTRIP_v1_SPEC.md`
Destination: `C:\CODEX PG\CODEX Canonical Specs\CODEX_TESTER_REPORT_ROUNDTRIP_v1.1_SPEC.md`

## 0. Purpose And Sign-Off Status

This v1.1 spec is the definitive locked successor to the v1 round-trip spec for
the first implementation pass. It keeps the v1 design center: the tester uses
Panda Gallery to capture a workflow, review the generated evidence, ship one
structured report to Darrin, receive a structured response, and preserve a local
audit trail on both sides.

The companion brief is still marked DRAFT and awaiting Darrin confirmation
(`C:\panda-gallery\workflows\audit\TESTER_REPORT_ROUNDTRIP_BRIEF_v1.md:6`).
Therefore these v1.1 locks are conditional on either direct acceptance of this
v1.1 spec or explicit sign-off of the brief. They are written as locks so the
implementation can proceed cleanly once Darrin says yes.

This file does not edit v1. The v1 file remains available for history and for
comparison against the lock decisions made here.

### 0.1 Source Ledger

The following canonical sources were read before authoring this file. Claims in
this spec cite these sources by path and line number where the source has a
stable anchor.

- v1 spec: same binary/different mode at
  `C:\CODEX PG\CODEX Canonical Specs\CODEX_TESTER_REPORT_ROUNDTRIP_v1_SPEC.md:29`,
  locked decisions at line 47, module breakdown at line 148, data shapes at line
  324, open questions at line 811, and first slice at line 829.
- Brief: draft status at
  `C:\panda-gallery\workflows\audit\TESTER_REPORT_ROUNDTRIP_BRIEF_v1.md:6`,
  Tier A/B/C posture at lines 68-72, folder topology at line 83, polling cadence
  at line 95, response shape at line 103, bundle lifecycle at line 115, and
  tester-side code home at line 132.
- PG_TRUTH: no AM clinical surface at
  `C:\panda-gallery\workflows\audit\PG_TRUTH_v1.md:18`; Codex read-only boundary
  at lines 95-97.
- Workflow capture: session file layout at
  `C:\panda-gallery\workflow_capture.py:1`, `LATEST.txt` at line 12,
  `metadata.json` at line 16, `audio.wav` at line 15, schema version at line 389,
  metadata and LATEST writes at lines 403-406, and auto-transcribe/transcribe.log
  behavior at lines 415 and 840.
- Compliance: PHI touchpoints at
  `C:\panda-gallery\PANDA_GALLERY_COMPLIANCE_SPEC.md:29` through line 45, current
  local-only/no-cloud posture at lines 110-112, logging/support-channel PHI risk
  at lines 321-333, and cloud/subprocessor trigger at lines 338-347.
- Auto-transcribe: target behavior at
  `C:\panda-gallery\PANDA_GALLERY_AUTOTRANSCRIBE_SPEC.md:17`, log path at line
  53, file layout at lines 341-348, and verification expectations at lines
  405-431.
- Transcript v2: frame-duration/screen-trace target at
  `C:\panda-gallery\PANDA_GALLERY_TRANSCRIPT_V2_SPEC.md:3` and line 15.
- Audit Module: current ScreenA/ScreenB/Archive stack at
  `C:\panda-gallery\audit_module\v1\window.py:100` through line 108; reload from
  BUGS.md at lines 217-222; status bar ownership at lines 111-112.
- Existing package patterns: file hashing and safe IDs at
  `C:\panda-gallery\codex_audit\package_builder.py:65`, line 73, and line 97;
  manifest integrity sequence at lines 488-500; safe relative path validation at
  `C:\panda-gallery\codex_audit\validation.py:97` through line 112.
- PG Design Bible: canonical visual authority at
  `C:\panda-gallery\workflows\design\PG_DESIGN_BIBLE_v1.md:3`; no new chrome
  at line 16; purposeful operational status at lines 97-130; progressive
  disclosure/action-state rule at lines 132-171; no label clipping and minimum
  size rules at lines 1377-1498; live visual sign-off limits at lines 1544-1615.
- AM synthesis: AM Screen B evidence/transcript/status-pane source at
  `C:\panda-gallery\workflows\design\AM_SCREEN_B_SYNTHESIS_v1.md:28`,
  transcript/audio section at lines 128-155, and status-pane copy rule at lines
  164-169.

### 0.2 Vocabulary

- "Tester" means an external or internal user running Panda Gallery in a
  tester/reporting mode.
- "Developer AM" means Darrin's developer-only Audit Module. PG_TRUTH forbids
  surfacing AM to clinical users.
- "Bundle" means the directory that contains one report, its manifest, its
  evidence files, and its ready marker.
- "Transport" means the pluggable delivery layer. v1.1 ships a local sync
  folder provider, not a cloud API.
- "Tier A" means synthetic-only data. This is the only v1.1 implementation tier.
- "Tier B" means real PHI with HIPAA-grade transport, audit, and agreements. It
  is designed for but not implemented here.
- "Tier C" means real-PHI workflow disallowed unless aggressive redaction passes.
  It is deferred.

## 1. Product Goal

The product goal is an evidence-preserving support loop:

1. A tester captures a workflow session using the existing PG workflow capture.
2. PG creates a draft report bundle from screenshots, metadata, transcript, and
   tester-entered issue details.
3. The tester reviews the report before anything leaves the machine.
4. PG ships the bundle atomically through a local-folder transport.
5. Developer AM ingests, validates, lists, and opens the report.
6. Darrin writes a structured response.
7. The tester receives the response in My Reports.
8. Both sides retain local event records so the state is not dependent on chat,
   email, or memory.

This is not a general chat system, not a replacement for AM bugs, and not a new
clinical module. It is a structured report loop built around real evidence.

## 2. Same Binary, Different Mode

LOCKED v1.1: There is one PG binary, with different mode surfaces. The v1 spec
already identifies "same binary, different mode" as the right architecture
(`CODEX_TESTER_REPORT_ROUNDTRIP_v1_SPEC.md:29`). The brief also frames tester
reporting as part of the same PG application, not a separate application.

Implementation consequence:

- Tester report code is a peer package under `tester_reports/`.
- Workflow capture remains the owner of recording and session artifact creation.
- Developer AM remains developer-only.
- Tester users never see AM or AM navigation.
- Developer users can see an AM Reports section inside the AM shell.

Rationale:

- One binary avoids installer drift and duplicate capture code.
- Mode gating keeps tester UX simple.
- PG_TRUTH explicitly says AM must not surface to clinical users
  (`PG_TRUTH_v1.md:18`).

## 3. Locked Product Decisions

### 3.1 Data Tiers

LOCKED v1.1: Phase 1 ships Tier A only: `A_SYNTHETIC_ONLY`.

Tier definitions:

- `A_SYNTHETIC_ONLY`: synthetic data only. Bundles must not contain real PHI.
- `B_PHI_GATED`: real-PHI mode behind explicit future compliance work.
- `C_REDACTION_ONLY`: fallback mode where real-PHI workflow is disallowed unless
  redaction passes. Deferred.

The brief explicitly makes Tier A the first-shipped tier and sketches Tier B and
Tier C as later paths (`TESTER_REPORT_ROUNDTRIP_BRIEF_v1.md:68-72`). The
compliance spec identifies workflow screenshots, audio, transcript, metadata,
logs, and exported files as PHI risk surfaces when real patient data is in scope
(`PANDA_GALLERY_COMPLIANCE_SPEC.md:29-45`).

Implementation consequence:

- Tier A blocks shipping if the tester declares real PHI.
- Tier A includes a conservative redaction/preflight stage even though synthetic
  data is expected.
- Tier B provider, encryption, BAA, audit logging, access logs, and subprocessor
  tracking are v2 work.

### 3.2 Bundle Format

LOCKED v1.1: v1.1 uses a directory bundle with `manifest.json` and `READY.json`.
It does not use ZIP or tar for Phase 1.

Rationale:

- Local sync folders handle ordinary files well.
- Atomic ready-marker semantics are easier to reason about than partially synced
  archives.
- Developers can inspect failed/quarantined bundles without extraction.
- The v1 spec already recommends directory-with-manifest in open question Q1.

Directory grammar:

```text
report_<tester_id>_<report_id>_<short_hash>/
  manifest.json
  READY.json
  source/
    metadata.json
    transcript.md
    transcribe.log
    audio.wav
    screenshot_0001.png
  derived/
    report_summary.md
    redaction_report.json
    bundle_events.jsonl
```

Files are included only when present and allowed by tier. For example,
`audio.wav` is optional when no audio was recorded.

### 3.3 Manifest Schema

LOCKED v1.1: The manifest schema is `pg.tester_report_bundle.v1.1`, with the
field polish specified in this document.

Important locks:

- `tester.tester_id` is lowercase ASCII alphanumerics plus underscores only,
  max length 32.
- `report.kind` is one of `bug`, `question`, `suggestion`, `other`.
- `tier.data_tier` is one of `A_SYNTHETIC_ONLY`, `B_PHI_GATED`,
  `C_REDACTION_ONLY`.
- `files[].kind` is from the closed set in section 8.1.
- `warnings[]` entries use the structured shape in section 8.1.
- Manifest file paths are bundle-relative POSIX-style paths.
- No external manifest field may contain an absolute Windows path.

Rationale:

- v1 already forbids absolute Windows paths in shipped manifest fields and ties
  that to Bug #134.
- Existing `codex_audit.validation` already validates file records as safe
  relative paths (`validation.py:97-112`), which is the right local precedent.

### 3.4 Status Set Authoring

LOCKED v1.1: AM owns `workflows/audit/report_statuses.json`. Responses embed
both status code and status label at send time.

Rationale:

- Darrin needs configurable response language in AM.
- Testers need stable historical response display even if AM labels change later.
- v1 open question Q3 already recommends AM-owned status config.

### 3.5 Tester Identity

LOCKED v1.1: Tester identity is stored in local
`tester_reports/tester_profile.json`, mirrored into QSettings for UI convenience.

Rationale:

- The v1 recommendation was local profile plus QSettings mirror.
- The profile file is inspectable and portable.
- QSettings is useful for recent UI selections and migration, but should not be
  the only durable identity source.

### 3.6 AM-Side Database

LOCKED v1.1: Developer report state uses a separate SQLite DB at
`workflows/audit/am_reports.db`. It does not extend the current AM issue JSON.

Rationale:

- Reports have polling, deduplication, ingestion, response writes, quarantine,
  and archive history.
- SQLite is the right persistence level for user-visible mutable state.
- v1 open question Q5 already recommends a separate SQLite DB.

### 3.7 Deduplication

LOCKED v1.1:

- Same `bundle_id` and same manifest hash: first ingested row wins; later copies
  are logged as duplicate and ignored.
- Same `bundle_id` and different manifest hash: quarantine.
- Same semantic title/summary but different `bundle_id`: treat as a separate
  report. Darrin can link or close manually.

### 3.8 Failed Delivery

LOCKED v1.1: Failed delivery stays visible as a draft or pending upload with
`last_error`, retry affordance, and timestamp.

No silent failure is acceptable. A button that writes or sends must produce at
least one of:

- visible state change,
- timestamped status text,
- structured event row,
- button label/activity change while work is running,
- explicit error state.

This aligns with the Design Bible rule that operational status earns its
presence and should prevent the user from guessing what is happening
(`PG_DESIGN_BIBLE_v1.md:97-130`).

### 3.9 Cardinality

LOCKED v1.1: One bundle equals one report.

Bundling multiple reports in one directory is deferred. Linking one report to
multiple AM bugs is allowed through `report_bug_links`.

### 3.10 Redaction Interface

LOCKED v1.1: Redaction/preflight runs pre-upload on the tester side. AM may
offer a later optional post-download re-run, but Phase 1 does not require it.

Rationale:

- Pre-upload protects cloud/local-sync transport boundaries.
- Tier A can still catch obvious mistakes before shipping.
- The brief raised pre-upload versus post-download as the redaction interface
  question (`TESTER_REPORT_ROUNDTRIP_BRIEF_v1.md:255`); v1.1 resolves it for
  Phase 1.

### 3.11 Size Limits

LOCKED v1.1 for Tier A:

- Warn above 50 MB.
- Require explicit confirmation above 100 MB.
- Hard block above 250 MB unless developer override is enabled.

Rationale:

- Workflow capture can include audio and screenshots.
- Local sync folders may work slowly with large bundles.
- Tier A should remain easy to test and debug.

### 3.12 Transport Choice

LOCKED v1.1: Phase 1 uses a local filesystem transport pointed at a test sync
folder. The default real-world provider is Dropbox desktop local folder, but the
code depends only on local filesystem semantics.

Future compatible providers:

- Google Drive desktop local folder.
- OneDrive local folder.
- SMB share.
- HIPAA-grade Tier B provider.

The transport interface must stay provider-neutral.

### 3.13 Validation Security

LOCKED v1.1: Failed validation quarantines. It never crashes the app and never
auto-ingests.

Quarantine rows must include reason, timestamp, source path, and enough context
for Darrin to inspect the failed bundle without accepting it as a real report.

### 3.14 Clinical Tester Onboarding

DEFERRED v2: Clinical tester onboarding is out of v1.1 implementation. It must
be defined before any external clinician uses real patient data.

This is v1 question Q13. It remains intentionally deferred because Tier B
compliance, tester agreements, access controls, and transport controls are not
Phase 1.

## 4. Architecture

The system has five cooperating parts:

1. Workflow capture creates source artifacts.
2. `tester_reports/` builds, validates, ships, and displays tester reports.
3. `ReportTransport` moves bundles and responses through a local folder.
4. AM Reports ingests, stores, displays, and responds to reports.
5. Shared schemas and validators keep both sides honest.

Data flow:

```text
Workflow Capture
  -> tester_reports bundle builder
  -> local staging directory
  -> transport outbox
  -> AM poller
  -> am_reports.db + AM Reports UI
  -> response writer
  -> tester inbox
  -> My Reports response view
```

The first implementation slice stops after minimal AM list/detail and ingest
state. Response writing can be enabled if already cheap, but is not required for
Phase 1 acceptance unless explicitly included by Darrin.

## 5. Module Breakdown

### 5.1 Tester Package

The v1 file lists 10 `tester_reports/` entries:
`__init__.py`, `bundle_builder.py`, `bundle_manifest.py`,
`bundle_validator.py`, `db.py`, `poller.py`, `redaction.py`, `transport.py`,
`ui_review.py`, and `ui_my_reports.py` (`CODEX_TESTER_REPORT_ROUNDTRIP_v1_SPEC.md:150-163`).

The v1.1 dispatch described "9 files from v1 section 5.1." Cross-validation
shows that is accurate only if `__init__.py` is treated as a package marker
rather than a functional file. This spec uses:

- 9 functional tester files.
- 1 package marker.

No implementation may delete `__init__.py` to satisfy a count.

### 5.2 Workflow Capture Integration

Workflow capture stays the source of session artifacts. It writes session
folders, metadata, `LATEST.txt`, optional `audio.wav`, and auto-transcription
outputs (`workflow_capture.py:1-16`, `workflow_capture.py:403-415`).

Required hook:

```python
ReportService.on_session_saved(session_dir: Path) -> None
```

Rules:

- The hook never blocks session stop.
- If transcript is pending, the report review UI shows "transcript pending" or
  waits for completion before enabling Ship.
- Missing optional transcript/audio produces a warning, not a crash.
- Missing required `metadata.json` blocks bundle creation.

### 5.3 Developer AM Reports

AM gets a Reports section peer to Bugs. The current AM window uses a stack with
ScreenA, ScreenB, and Archive (`audit_module\v1\window.py:100-108`). Reports may
be a new stacked screen, tab, or child panel, but must remain inside the
developer-only AM shell.

Required Phase 1 AM files:

- `audit_module/reports_store.py`
- `audit_module/reports_ingest.py`
- `audit_module/reports_transport.py`
- `audit_module/reports_window.py` or `audit_module/v1/reports_panel.py`

Preference: if implementation is under the current v1 AM shell, use
`audit_module/v1/reports_panel.py` and keep data-layer files at package root
only if that matches existing AM import patterns.

### 5.4 Shared Transport

`ReportTransport` is the shared abstraction used by tester and AM. The Phase 1
implementation is `LocalSyncFolderTransport`.

All providers must preserve:

- atomic stage then commit,
- ready marker semantics,
- archive operation,
- health check,
- safe relative names,
- no direct dependency on Dropbox, OneDrive, or Google Drive APIs in Phase 1.

## 6. Bundle Lifecycle

LOCKED v1.1 lifecycle states:

1. `Drafted`: tester stopped a session and a draft report exists.
2. `Reviewing`: tester is editing title/kind/summary and inspecting evidence.
3. `ReadyToShip`: validation passes and Ship is enabled.
4. `Shipped`: bundle committed to transport outbox.
5. `Received`: AM ingested bundle successfully.
6. `Responded`: Darrin wrote a response.
7. `Closed`: report terminal on both sides.
8. `Quarantined`: validation/security failure.

State ownership:

- Tester owns Drafted, Reviewing, ReadyToShip, Shipped.
- AM owns Received, Responded, Closed, Quarantined.
- Both local DBs maintain their own event history.

State transition rules:

- Drafted -> Reviewing: user opens report review.
- Reviewing -> ReadyToShip: required fields valid, bundle validates, tier gate
  passes.
- ReadyToShip -> Shipped: transport commit succeeds.
- ReadyToShip -> Drafted: user saves draft.
- Any pre-ship state -> Quarantined: validation or tier gate blocks.
- Shipped -> Received: AM poller ingests.
- Received -> Responded: Darrin sends response.
- Responded -> Closed: terminal status or user closes.

No automatic deletion occurs in Phase 1.

## 7. User Experience Requirements

### 7.1 Tester Review UI

Tester review UI includes:

- report title,
- kind selector (`bug`, `question`, `suggestion`, `other`),
- optional summary,
- source session identity,
- screenshot filmstrip or list,
- transcript preview if present,
- audio duration/file indicator if present,
- tier declaration,
- validation status,
- action row: Ship, Save Draft, Discard.

Ship is enabled only when all required checks pass. Disabled Ship must expose a
reason through adjacent status text or tooltip, following the Design Bible
progressive-disclosure rule (`PG_DESIGN_BIBLE_v1.md:132-171`).

### 7.2 My Reports UI

My Reports shows:

- Drafted/Pending/Shipped/Received/Responded/Closed/Quarantined rows.
- Last state timestamp.
- Last error, if any.
- Response preview when received.
- Open source folder for local drafts.
- Retry for failed pending upload.

### 7.3 AM Reports List

Minimal AM Reports list shows:

- report title,
- tester,
- kind,
- state,
- created timestamp,
- received timestamp,
- validation/quarantine status,
- response status.

It must be scan-friendly and quiet. Avoid decorative explanatory prose. Use
status and timestamps rather than instruction blocks.

### 7.4 AM Report Detail

AM detail shows:

- compact report header,
- tester/source metadata strip,
- transcript/audio section grouped with evidence,
- screenshot thumbnails,
- manifest facts,
- validation warnings,
- response composer.

AM Screen B synthesis says transcript/audio evidence needs its own section
within the evidence block (`AM_SCREEN_B_SYNTHESIS_v1.md:128-155`). AM Reports
should reuse that mental model without copying bug-triage-only controls.

### 7.5 Button Feedback

Every action button in tester_reports and AM Reports must provide visible
feedback on activation. Minimum accepted feedback:

- label swap while running, such as "Shipping..."
- disabled state while work is in progress,
- timestamped one-line status after completion,
- error text with timestamp on failure,
- database event row,
- optional border/color state change using existing tokens.

No button may appear to do nothing.

### 7.6 Visual And Bible Compliance

UI implementation must cite and obey the PG Design Bible:

- no new chrome or button shapes unless required,
- purposeful operational status only,
- progressive disclosure for unavailable actions,
- no clipped labels,
- computed minimum sizes after state changes,
- live visual sign-off for QSS/widget/layout/color work.

The Bible applet can catch token/rule drift, but it does not prove live Qt
rendering correctness (`PG_DESIGN_BIBLE_v1.md:1594-1598`). Any UI work touching
layout or QSS needs live-app verification.

## 8. Schemas

### 8.1 Bundle Manifest v1.1

```json
{
  "schema": "pg.tester_report_bundle.v1.1",
  "schema_version": 1,
  "bundle_id": "rpt_rebecca_000042_a1b2c3d4",
  "report_id": "report_000042",
  "tester": {
    "tester_id": "rebecca",
    "display_name": "Rebecca",
    "pg_install_id": "uuid"
  },
  "source_session": {
    "session_id": "session_20260425_141500",
    "session_dir_name": "session_20260425_141500",
    "started_at": "2026-04-25T14:15:00-07:00",
    "ended_at": "2026-04-25T14:29:00-07:00",
    "app_version": "v4.35",
    "capture_mode": "audio_and_screenshots"
  },
  "report": {
    "title": "AM filter dropdown contrast",
    "kind": "bug",
    "summary": "Tester-entered optional summary.",
    "relates": [],
    "created_at": "2026-04-25T14:32:00-07:00"
  },
  "tier": {
    "data_tier": "A_SYNTHETIC_ONLY",
    "contains_phi_declared": false,
    "redaction_required": false,
    "redaction_state": "not_required"
  },
  "files": [
    {
      "file_id": "src_metadata",
      "kind": "metadata_json",
      "path": "source/metadata.json",
      "sha256": "...",
      "bytes": 1234,
      "required": true
    }
  ],
  "integrity": {
    "hash_algorithm": "sha256",
    "manifest_without_integrity_sha256": "...",
    "file_count": 8,
    "total_bytes": 2411721
  },
  "warnings": [
    {
      "code": "optional_source_missing",
      "severity": "warn",
      "message": "No transcript.md was present.",
      "at": "2026-04-25T14:32:10-07:00"
    }
  ]
}
```

Closed sets:

- `tester.tester_id`: regex `^[a-z0-9_]{1,32}$`.
- `report.kind`: `bug`, `question`, `suggestion`, `other`.
- `tier.data_tier`: `A_SYNTHETIC_ONLY`, `B_PHI_GATED`,
  `C_REDACTION_ONLY`.
- `files[].kind`: `metadata_json`, `transcript_md`, `transcribe_log`,
  `audio_wav`, `screenshot_png`, `report_summary_md`,
  `redaction_report_json`, `bundle_events_jsonl`.
- `warnings[].severity`: `info`, `warn`, `error`.

Validation rules:

- `manifest.json` is UTF-8 JSON.
- `schema` exactly matches `pg.tester_report_bundle.v1.1`.
- `schema_version` is integer `1`.
- `bundle_id` and `report_id` are required.
- All file paths are relative and cannot contain `..`.
- All file hashes are sha256.
- `integrity.manifest_without_integrity_sha256` is computed with the integrity
  object empty.
- `integrity.file_count` equals the number of file records.
- `integrity.total_bytes` equals the sum of file bytes.
- No absolute Windows paths in the manifest.

### 8.2 READY Marker

```json
{
  "schema": "pg.tester_report_ready.v1",
  "schema_version": 1,
  "bundle_id": "rpt_rebecca_000042_a1b2c3d4",
  "manifest_path": "manifest.json",
  "manifest_sha256": "...",
  "created_at": "2026-04-25T14:32:10-07:00"
}
```

Pollers process a directory only when `READY.json` exists, parses, and matches
the manifest hash.

### 8.3 Response Payload

```json
{
  "schema": "pg.tester_report_response.v1",
  "schema_version": 1,
  "response_id": "resp_20260425_153000_000042",
  "bundle_id": "rpt_rebecca_000042_a1b2c3d4",
  "report_id": "report_000042",
  "tester_id": "rebecca",
  "created_by": "Darrin",
  "created_at": "2026-04-25T15:30:00-07:00",
  "status": {
    "code": "fix_in_progress",
    "label": "Fix in progress",
    "terminal": false
  },
  "message": "I reproduced this. It is tracked as bug #136.",
  "links": [
    {"kind": "bug", "id": "136", "label": "BUGS.md #136"}
  ],
  "integrity": {
    "hash_algorithm": "sha256",
    "payload_without_integrity_sha256": "..."
  }
}
```

### 8.4 `report_statuses.json`

Path: `workflows/audit/report_statuses.json`

```json
{
  "schema": "pg.report_statuses.v1",
  "schema_version": 1,
  "statuses": [
    {
      "code": "acknowledged",
      "label": "Acknowledged",
      "terminal": false,
      "default_message": "I received this and will review it.",
      "sort_order": 10
    },
    {
      "code": "fixed",
      "label": "Fixed",
      "terminal": true,
      "default_message": "This has been fixed.",
      "sort_order": 90
    }
  ]
}
```

Rules:

- `code` is lowercase ASCII alphanumerics plus underscores.
- `label` is user-visible and embedded into each response.
- Removing a status from config does not rewrite historical responses.

### 8.5 `tester_profile.json`

Path: `tester_reports/tester_profile.json` or user-config path selected by
implementation.

```json
{
  "schema": "pg.tester_profile.v1",
  "schema_version": 1,
  "tester_id": "rebecca",
  "display_name": "Rebecca Chen",
  "pg_install_id": "uuid",
  "data_tier_default": "A_SYNTHETIC_ONLY",
  "transport_profile": "local_sync_default",
  "created_at": "2026-04-25T14:00:00-07:00",
  "updated_at": "2026-04-25T14:00:00-07:00"
}
```

Rules:

- `tester_id` uses the same regex as the manifest.
- `data_tier_default` is Tier A for Phase 1.
- `pg_install_id` is stable per PG installation.

## 9. Databases

### 9.1 Tester DB

Path: implementation-owned local app data path, not shipped in bundles.

```sql
create table tester_reports (
  report_id text primary key,
  bundle_id text unique,
  tester_id text not null,
  source_session_id text,
  title text not null,
  kind text not null,
  state text not null,
  data_tier text not null,
  created_at text not null,
  updated_at text not null,
  shipped_at text,
  pipe_ack_at text,
  response_received_at text,
  closed_at text,
  local_bundle_path text,
  transport_bundle_path text,
  manifest_sha256 text,
  last_error text
);

create table report_responses (
  response_id text primary key,
  report_id text not null,
  bundle_id text not null,
  status_code text not null,
  status_label text not null,
  terminal integer not null,
  message text,
  received_at text not null,
  seen_at text,
  payload_path text not null
);

create table report_events (
  event_id integer primary key autoincrement,
  report_id text not null,
  event_type text not null,
  at text not null,
  detail_json text
);
```

Required indexes:

```sql
create index idx_tester_reports_state on tester_reports(state);
create index idx_tester_reports_updated on tester_reports(updated_at);
create index idx_report_events_report on report_events(report_id, at);
```

### 9.2 AM Reports DB

Path: `workflows/audit/am_reports.db`

```sql
create table inbound_reports (
  bundle_id text primary key,
  report_id text not null,
  tester_id text not null,
  title text not null,
  kind text not null,
  state text not null,
  seen_at text,
  ingested_at text not null,
  responded_at text,
  closed_at text,
  local_ingest_path text not null,
  source_transport_path text not null,
  manifest_sha256 text not null,
  quarantine_reason text
);

create table outbound_responses (
  response_id text primary key,
  bundle_id text not null,
  tester_id text not null,
  status_code text not null,
  status_label text not null,
  terminal integer not null,
  message text,
  created_at text not null,
  shipped_at text,
  payload_path text not null
);

create table report_bug_links (
  bundle_id text not null,
  bug_number integer not null,
  link_kind text not null,
  created_at text not null
);

create table am_report_events (
  event_id integer primary key autoincrement,
  bundle_id text not null,
  event_type text not null,
  at text not null,
  detail_json text
);
```

Required indexes:

```sql
create index idx_inbound_reports_state on inbound_reports(state);
create index idx_inbound_reports_ingested on inbound_reports(ingested_at);
create index idx_outbound_responses_bundle on outbound_responses(bundle_id);
create index idx_am_report_events_bundle on am_report_events(bundle_id, at);
```

## 10. Interfaces

### 10.1 ReportTransport

```python
from pathlib import Path
from typing import Protocol


class RemoteItem:
    """Transport item discovered in an incoming channel."""
    name: str
    path: Path
    modified_at: str | None
    bytes: int | None


class StagedWrite:
    """Pending outgoing write that becomes visible only after commit."""
    staging_path: Path
    final_path: Path
    channel: str


class TransportHealth:
    """Transport health result for UI status and diagnostics."""
    ok: bool
    provider: str
    checked_at: str
    message: str


class ReportTransport(Protocol):
    def list_incoming(self, channel: str) -> list[RemoteItem]:
        """Return incoming items for a channel."""

    def stage_outgoing(self, local_path: Path, channel: str, remote_name: str) -> StagedWrite:
        """Copy an outgoing item into hidden staging."""

    def commit(self, staged: StagedWrite) -> None:
        """Atomically expose a staged outgoing item."""

    def fetch(self, item: RemoteItem, dest_dir: Path) -> Path:
        """Copy an incoming item into local ingest storage."""

    def archive(self, item: RemoteItem, archive_relpath: str) -> None:
        """Move a processed item into archive storage."""

    def health_check(self) -> TransportHealth:
        """Check root existence, writeability, and basic provider health."""
```

### 10.2 LocalSyncFolderTransport

```python
class LocalSyncFolderTransport:
    """Filesystem transport for Dropbox/Drive/OneDrive style synced folders."""

    def __init__(self, root: Path, provider_label: str = "Local sync folder") -> None: ...
    def list_incoming(self, channel: str) -> list[RemoteItem]: ...
    def stage_outgoing(self, local_path: Path, channel: str, remote_name: str) -> StagedWrite: ...
    def commit(self, staged: StagedWrite) -> None: ...
    def fetch(self, item: RemoteItem, dest_dir: Path) -> Path: ...
    def archive(self, item: RemoteItem, archive_relpath: str) -> None: ...
    def health_check(self) -> TransportHealth: ...
```

LocalSyncFolderTransport rules:

- root must exist,
- `outbox`, `inbox`, `archive`, and `.staging` are created if allowed,
- staged writes use a hidden or suffixed staging path,
- commit uses atomic rename within the same filesystem,
- fetch rejects paths outside root,
- health check writes and deletes a small temp file.

### 10.3 RedactionStage

```python
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass
class RedactionFinding:
    """Single redaction/preflight finding."""
    code: str
    severity: str
    message: str
    file_id: str | None = None


@dataclass
class RedactionReport:
    """Redaction/preflight report persisted with each bundle."""
    ok_to_ship: bool
    data_tier: str
    findings: list[RedactionFinding]


class RedactionStage(Protocol):
    def inspect(self, bundle_dir: Path, manifest: dict) -> RedactionReport:
        """Inspect a staged bundle before shipping."""

    def apply(self, bundle_dir: Path, manifest: dict) -> RedactionReport:
        """Apply redaction when the tier allows mutation."""
```

### 10.4 Tier A Redaction Stage

```python
class TierASyntheticPreflight:
    """Conservative Tier A gate that blocks likely real-PHI bundles."""

    def __init__(self, known_patient_tokens: list[str] | None = None) -> None: ...
    def inspect(self, bundle_dir: Path, manifest: dict) -> RedactionReport: ...
    def apply(self, bundle_dir: Path, manifest: dict) -> RedactionReport: ...
```

Tier A behavior:

- require `tier.data_tier == "A_SYNTHETIC_ONLY"`;
- require tester declaration `contains_phi_declared == false`;
- block absolute paths in manifest;
- scan title, summary, transcript, and report summary for known patient tokens
  if provided;
- write `derived/redaction_report.json`;
- never modify screenshots or audio in Phase 1;
- if risk is found, block shipment instead of attempting redaction.

## 11. Polling And Atomic Writes

### 11.1 Bundle Write

Write sequence:

1. Create local draft directory outside transport outbox.
2. Copy source files into draft bundle.
3. Run Tier A preflight.
4. Write `derived/redaction_report.json`.
5. Write `derived/report_summary.md`.
6. Write `derived/bundle_events.jsonl`.
7. Write `manifest.json` with empty integrity.
8. Compute file hashes and manifest hash.
9. Rewrite `manifest.json` with populated integrity.
10. Validate entire bundle.
11. Write `READY.json` last.
12. Stage into transport `.staging`.
13. Commit to visible outbox.
14. Mark DB Shipped.

### 11.2 AM Ingest

Ingest sequence:

1. List tester outbox directories.
2. Skip hidden/staging directories.
3. Skip directories without `READY.json`.
4. Validate ready marker.
5. Validate manifest.
6. Validate files.
7. Check dedupe.
8. Copy into local ingest storage via temp directory.
9. Insert/update AM DB.
10. Optionally archive source after terminal status in a later phase.

### 11.3 Response Write

Response write mirrors bundle write:

1. Build response payload.
2. Hash payload without integrity.
3. Write payload into staging.
4. Write response ready marker or commit by atomic rename.
5. Mark AM DB shipped.
6. Tester poller validates before applying.

## 12. Compliance And Security

Phase 1 is not approved for real PHI. Tier A is synthetic-only.

Hard rules:

- Do not ship real patient screenshots.
- Do not ship real patient audio.
- Do not ship real patient transcripts.
- Do not paste workflow capture content into external support channels without
  PHI review.
- Do not add cloud APIs in Phase 1.
- Do not depend on consumer cloud accounts as HIPAA controls.

The compliance spec says PG is local-only today and no audio/transcript leaves
the machine (`PANDA_GALLERY_COMPLIANCE_SPEC.md:110-112`). This round-trip system
changes that once bundles are synced; therefore Tier A synthetic-only gating is
mandatory.

## 13. Validation And Test Plan

### 13.1 Unit Tests

Required:

- tester id validation;
- manifest closed sets;
- manifest hash determinism;
- safe relative file paths;
- ready marker validation;
- bundle validator happy path;
- bundle validator missing required file;
- optional transcript warning;
- Tier A declared PHI block;
- local transport health check;
- transport stage/commit/fetch/archive;
- tester DB state events;
- AM DB ingest/quarantine events.

### 13.2 Integration Tests

Required synthetic fixture:

```text
tmp/
  workflows/
    session_20260502_120000/
      metadata.json
      screenshot_0001.png
      transcript.md
      transcribe.log
```

Test flow:

1. Build bundle from fixture.
2. Validate bundle.
3. Ship to temp local sync outbox.
4. AM poller ingests.
5. AM store lists one inbound report.
6. AM detail opens manifest/evidence.
7. Optional response writes to tester inbox.
8. Tester poller records response.

### 13.3 UI Smoke

Required:

- tester review dialog constructs;
- My Reports constructs;
- AM Reports panel constructs inside AM shell or test harness;
- action buttons have feedback;
- Check Now/Refresh style actions show timestamp;
- disabled actions expose reason;
- min/default/large sizes do not clip labels.

### 13.4 Live Visual Verification

Required for any UI implementation touching QSS, layout, widget construction, or
colors:

- open live PG on Windows;
- verify tester review and My Reports;
- open live AM Reports in developer AM;
- capture min/default/large screenshots;
- confirm no label clipping, button collision, blank panels, or invisible
  background.

Offscreen/headless smoke is useful for construction but is not visual sign-off.

## 14. Failure Modes

### 14.1 Transcript Pending

If `audio.wav` exists and `transcript.md` is not ready:

- show transcript pending;
- allow Save Draft;
- disable Ship unless Darrin explicitly accepts audio-without-transcript;
- record warning in local DB.

### 14.2 Sync Folder Missing

If transport root is missing:

- health check fails;
- Ship disabled or retry fails visibly;
- last_error records root path label, not PHI content;
- no bundle is deleted.

### 14.3 Partial Sync

If AM sees a directory without READY:

- skip silently or log info;
- do not quarantine yet;
- do not ingest.

If READY exists but files are missing or hashes fail:

- quarantine with reason.

### 14.4 Duplicate Bundle

- Same id/same hash: event `duplicate_seen`, no new row.
- Same id/different hash: quarantine.

### 14.5 Oversize Bundle

- Above 50 MB: warning.
- Above 100 MB: confirmation required.
- Above 250 MB: hard block unless developer override.

### 14.6 UI Action Failure

Every action failure must be reflected in:

- one-line visible status,
- timestamp,
- DB event if state-related,
- actionable message that avoids stack dumps in normal UI.

## 15. Boundaries

In scope:

- new round-trip spec;
- tester_reports package in future implementation;
- AM Reports minimal ingest/list/detail in future implementation;
- local-folder transport;
- Tier A synthetic-only.

Out of scope:

- Relay implementation;
- PAH implementation;
- real PHI transport;
- Dropbox/Google/OneDrive API integration;
- clinical tester onboarding;
- AM bug triage redesign;
- modifying existing workflow capture recording semantics beyond a small
  non-blocking hook.

## 16. Implementation Sequence

Recommended order:

1. Shared manifest and validator.
2. Local transport with temp-directory tests.
3. Tester DB.
4. Bundle builder against synthetic session fixture.
5. AM DB.
6. AM ingest poller.
7. Minimal AM Reports panel.
8. Tester review dialog.
9. My Reports response view.
10. Response writer/poller.

Reason:

- Schemas and validator are the foundation.
- Transport can be tested without UI.
- DB state proves button feedback and status records.
- UI lands after the underlying state can be trusted.

## 17. Resolved v1 Questions

### Q1. Bundle Format

LOCKED v1.1: Directory-with-manifest plus READY marker.

Default from v1 accepted. ZIP/tar are deferred.

### Q2. Manifest Schema

LOCKED v1.1: Use section 8.1 schema with v1.1 closed sets and field polish.

Default from v1 accepted, with the dispatch-requested additions.

### Q3. Status Set Authoring

LOCKED v1.1: AM-owned `workflows/audit/report_statuses.json`, with response
labels embedded into each response payload.

### Q4. Tester Identity

LOCKED v1.1: local `tester_profile.json` plus QSettings mirror.

### Q5. AM-Side Database

LOCKED v1.1: separate SQLite `workflows/audit/am_reports.db`.

### Q6. Bundle Deduplication

LOCKED v1.1: first same-id/same-hash wins; same-id/different-hash quarantines.

### Q7. Failed Delivery Handling

LOCKED v1.1: save draft or pending upload with retry, visible last_error, and
timestamped status.

### Q8. Bundle-To-Report Cardinality

LOCKED v1.1: one bundle equals one report.

### Q9. Redaction Interface

LOCKED v1.1: pre-upload Tier A preflight on tester side; optional AM rerun later.

### Q10. Bundle Size/Archive Lifecycle

LOCKED v1.1: warn above 50 MB, confirm above 100 MB, hard block above 250 MB
unless developer override. Archive move is not required in Phase 1.

### Q11. Transport Choice

LOCKED v1.1: local filesystem transport pointed at a test sync folder; Dropbox
desktop local folder is the default real-world provider, but not a code
dependency.

### Q12. Schema Validation Security

LOCKED v1.1: quarantine on failed validation; never crash or auto-ingest.

### Q13. Clinical Tester Onboarding

DEFERRED v2: not implemented in v1.1. Must be specified before real patient data
or external clinician use.

## 18. Acceptance Criteria

AC1: v1 remains untouched.

AC2: v1.1 spec exists at the canonical CODEX PG path.

AC3: v1.1 states brief sign-off condition clearly.

AC4: Q1-Q12 are locked with v1.1 annotations.

AC5: Q13 is deferred to v2.

AC6: Manifest schema includes the requested closed sets and warning shape.

AC7: Phase 1 implementation manifest enumerates the tester package and AM
Reports files.

AC8: The tester package count discrepancy is documented as 9 functional files
plus `__init__.py`.

AC9: `ReportTransport`, `LocalSyncFolderTransport`, `RedactionStage`, and Tier A
preflight are specified.

AC10: Tester DB and AM DB schemas are specified.

AC11: UI action feedback is a requirement.

AC12: Compliance boundaries forbid real PHI in Phase 1.

AC13: AM stays developer-only.

AC14: No Relay work is included.

AC15: ASCII-only document body.

AC16: Implementation risks and validation findings are documented in section 23.

## 19. Cross-Validation Summary

The authoring pass validated source paths, section anchors, schema closed sets, implementation manifest coverage, and known dispatch ambiguities. The two non-blocking source issues are preserved in section 23: the tester_reports file-count ambiguity and current AM file-name drift from older design text.

## 20. Final Recommendation

Build the v1.1 first slice exactly as a boring local-folder system with strict
manifest validation and excellent local status feedback. The important product
is not Dropbox and not a transport brand. The product is a reliable evidence
loop: tester captures context, Darrin receives structured evidence, Darrin can
respond, and both sides can prove what happened from local records.

Do not start with UI polish. Start with manifest, validator, local transport,
and DB events. Once those are solid, the UI can be simple and trustworthy.

## 21. Phase 1 Implementation Manifest

Phase 1 covers exactly:

- tester profile config;
- directory bundle builder from completed synthetic session;
- manifest + READY marker + validator;
- local filesystem transport pointed at a test folder;
- tester SQLite DB through Drafted and Shipped;
- AM ingest poller into `am_reports.db`;
- minimal AM Reports list/detail view.

No Relay work is included. No Tier B work is included. No real PHI workflow is
included.

### 21.1 `tester_reports/__init__.py`

LOC budget: 5-20.

Public surface:

```python
"""Tester report round-trip package."""

__all__ = [
    "BundleBuilder",
    "BundleValidator",
    "LocalReportStore",
    "LocalSyncFolderTransport",
]
```

Dependencies: none beyond local imports.

Boundary: package marker only. It must not perform filesystem work at import
time.

Tests: import smoke.

Acceptance:

- importing `tester_reports` has no side effects;
- package exports remain stable.

### 21.2 `tester_reports/bundle_manifest.py`

LOC budget: 140-220.

Public surface:

```python
def make_bundle_id(tester_id: str, report_id: str, manifest_seed: str) -> str:
    """Build a stable bundle id from tester, report, and seed."""

def validate_tester_id(tester_id: str) -> None:
    """Reject tester ids outside the v1.1 closed grammar."""

def build_manifest(...) -> dict:
    """Create a v1.1 bundle manifest with relative file records."""

def manifest_hash(manifest: dict) -> str:
    """Hash the manifest with integrity fields empty."""

def write_manifest(bundle_dir: Path, manifest: dict) -> Path:
    """Write manifest.json using deterministic UTF-8 JSON."""

def write_ready_marker(bundle_dir: Path, manifest: dict) -> Path:
    """Write READY.json last after manifest and files are stable."""
```

Dependencies:

- `hashlib`,
- `json`,
- `pathlib`,
- `re`,
- existing project patterns from `codex_audit.package_builder`.

Boundaries:

- no Qt imports;
- no transport writes;
- no SQLite writes;
- no absolute paths in manifest file records.

Tests:

- tester id validation;
- manifest hash excludes integrity;
- file records reject absolute paths;
- closed sets enforced.

Acceptance:

- manifest matches section 8.1;
- READY marker matches section 8.2;
- output is deterministic across repeated runs from same inputs.

### 21.3 `tester_reports/bundle_validator.py`

LOC budget: 160-260.

Public surface:

```python
class ValidationError(Exception):
    """Bundle validation failure."""

def validate_manifest(manifest_path: Path) -> ValidationReport:
    """Validate manifest schema, file records, hashes, and integrity."""

def validate_ready_marker(bundle_dir: Path) -> ValidationReport:
    """Validate READY.json and its manifest hash."""

def validate_bundle(bundle_dir: Path) -> ValidationReport:
    """Validate a complete bundle directory before ship or ingest."""
```

Dependencies:

- `dataclasses`,
- `hashlib`,
- `json`,
- `pathlib`,
- `typing`.

Boundaries:

- no UI;
- no transport mutation;
- no database mutation;
- no auto-repair.

Tests:

- happy-path synthetic bundle;
- missing required metadata;
- optional missing transcript warning;
- bad sha quarantine/error;
- absolute path rejection;
- duplicate warnings shape rejection.

Acceptance:

- AM and tester can use the same validator;
- errors are structured enough for UI and quarantine rows.

### 21.4 `tester_reports/bundle_builder.py`

LOC budget: 220-360.

Public surface:

```python
class BundleBuilder:
    """Build a tester report bundle from a completed workflow session."""

    def build_draft(self, session_dir: Path, report_input: ReportInput) -> BuildResult:
        """Create a local draft bundle without exposing it to transport."""

    def finalize_for_ship(self, draft_dir: Path) -> BuildResult:
        """Validate, hash, and write READY.json for shipping."""
```

Dependencies:

- `shutil`,
- `pathlib`,
- `bundle_manifest`,
- `bundle_validator`,
- `redaction`.

Boundaries:

- reads workflow session artifacts;
- writes only to tester report staging/draft directory;
- does not write transport outbox directly;
- does not block workflow capture stop.

Tests:

- builds from synthetic session with metadata and screenshots;
- includes transcript/log/audio when present;
- warns for optional missing transcript;
- blocks missing metadata;
- writes redaction report.

Acceptance:

- source session remains unchanged;
- bundle has only relative paths;
- required files hash correctly;
- READY marker appears only after validation passes.

### 21.5 `tester_reports/db.py`

LOC budget: 160-260.

Public surface:

```python
class LocalReportStore:
    """SQLite-backed tester report state store."""

    def ensure_schema(self) -> None:
        """Create or migrate tester report tables."""

    def create_draft(self, draft: DraftReport) -> None:
        """Insert a Drafted report row and event."""

    def mark_shipped(self, report_id: str, bundle_id: str, transport_path: str) -> None:
        """Mark a report Shipped after transport commit."""

    def record_error(self, report_id: str, message: str) -> None:
        """Persist a visible last_error and event."""

    def list_reports(self) -> list[ReportRow]:
        """Return reports for My Reports."""
```

Dependencies:

- `sqlite3`,
- `json`,
- `pathlib`,
- `datetime`.

Boundaries:

- no Qt;
- no transport operations;
- no manifest building.

Tests:

- schema creation;
- Drafted -> Shipped update;
- event rows;
- last_error visible;
- idempotent migration.

Acceptance:

- DB uses section 9.1 schema;
- every state-changing action writes an event.

### 21.6 `tester_reports/transport.py`

LOC budget: 180-300.

Public surface:

```python
class LocalSyncFolderTransport:
    """Filesystem transport for local synced report folders."""

def load_transport_config(path: Path) -> TransportConfig:
    """Load local sync transport configuration."""
```

Dependencies:

- `pathlib`,
- `shutil`,
- `tempfile`,
- `os`.

Boundaries:

- no bundle schema knowledge except directory names;
- no UI;
- no DB writes.

Tests:

- health check success/failure;
- stage and commit;
- fetch rejects traversal;
- archive moves processed item;
- same-filesystem rename.

Acceptance:

- can run against a temp directory in tests;
- never exposes partial outgoing bundle without commit.

### 21.7 `tester_reports/redaction.py`

LOC budget: 140-240.

Public surface:

```python
class TierASyntheticPreflight:
    """Conservative Tier A gate that blocks likely real-PHI bundles."""

def write_redaction_report(bundle_dir: Path, report: RedactionReport) -> Path:
    """Persist redaction findings in derived/redaction_report.json."""
```

Dependencies:

- `json`,
- `pathlib`,
- `re`.

Boundaries:

- no cloud AI call in Phase 1;
- no screenshot/audio mutation;
- no PHI upload.

Tests:

- synthetic declaration passes;
- declared PHI blocks;
- absolute path blocks;
- known patient token in transcript blocks;
- report JSON written.

Acceptance:

- Tier A redaction cannot silently pass declared real PHI;
- findings map to manifest warnings/errors.

### 21.8 `tester_reports/poller.py`

LOC budget: 120-220.

Public surface:

```python
class ResponsePoller:
    """Poll tester inbox for AM responses."""

    def poll_once(self) -> PollResult:
        """Fetch and validate new responses once."""
```

Dependencies:

- `transport`,
- `db`,
- response validator.

Boundaries:

- Phase 1 may include a stub if response writer is deferred;
- no AM imports;
- no workflow capture imports.

Tests:

- no inbox exists;
- duplicate same response ignored;
- conflicting duplicate quarantined/logged;
- valid response updates DB.

Acceptance:

- polling failure records visible last_error;
- no crash on malformed response.

### 21.9 `tester_reports/ui_review.py`

LOC budget: 220-420.

Public surface:

```python
class TesterReportReviewDialog(QDialog):
    """Pre-send review dialog for a captured tester report."""

    def load_session(self, session_dir: Path) -> None:
        """Populate review fields and evidence preview."""

    def build_draft(self) -> None:
        """Create or refresh the draft bundle from current inputs."""
```

Dependencies:

- PySide6,
- `bundle_builder`,
- `db`,
- `transport`.

Boundaries:

- no AM imports;
- no raw QSS hex literals;
- no direct workflow capture mutation.

Tests:

- widget construction smoke;
- Ship disabled reason;
- successful Ship updates status timestamp;
- failed validation displays error.

Acceptance:

- Ship/Save/Discard all provide visible feedback;
- label text does not clip at minimum size;
- visual changes require live-app verification.

### 21.10 `tester_reports/ui_my_reports.py`

LOC budget: 180-320.

Public surface:

```python
class MyReportsPanel(QWidget):
    """Tester-facing list/detail view for sent reports and responses."""

    def refresh(self) -> None:
        """Reload report rows from local DB."""
```

Dependencies:

- PySide6,
- `db`,
- optional `poller`.

Boundaries:

- no transport writes except explicit retry action;
- no AM imports.

Tests:

- empty state;
- row rendering by state;
- response preview;
- retry action feedback.

Acceptance:

- unread/responded items are visible at a glance;
- refresh shows timestamp;
- no button silently does nothing.

### 21.11 `audit_module/reports_store.py`

LOC budget: 170-280.

Public surface:

```python
class AmReportStore:
    """SQLite-backed AM Reports state store."""

    def ensure_schema(self) -> None:
        """Create or migrate AM report tables."""

    def upsert_inbound(self, report: InboundReport) -> None:
        """Insert or update an inbound report row."""

    def quarantine(self, bundle_id: str, reason: str, source_path: str) -> None:
        """Persist quarantine state without ingesting as accepted."""

    def list_inbound(self) -> list[InboundReport]:
        """Return inbound report rows for the AM Reports list."""
```

Dependencies:

- `sqlite3`,
- `json`,
- `pathlib`,
- `datetime`.

Boundaries:

- no Qt;
- no transport mutation;
- no BUGS.md mutation.

Tests:

- schema creation;
- accepted inbound insert;
- quarantine insert;
- event rows;
- indexes exist.

Acceptance:

- DB matches section 9.2;
- duplicate same hash does not create duplicate visible reports.

### 21.12 `audit_module/reports_transport.py`

LOC budget: 60-120.

Public surface:

```python
def build_am_transport(config_path: Path) -> ReportTransport:
    """Build AM report transport from local config."""
```

Dependencies:

- `tester_reports.transport` if package sharing is allowed,
- otherwise a thin wrapper around the same local transport implementation.

Boundaries:

- no UI;
- no DB.

Tests:

- config load;
- health check surfaces root missing.

Acceptance:

- AM and tester use equivalent transport behavior;
- provider-neutral interface remains intact.

### 21.13 `audit_module/reports_ingest.py`

LOC budget: 220-360.

Public surface:

```python
class AmReportIngestPoller:
    """Poll tester outboxes and ingest validated bundles into AM."""

    def poll_once(self) -> IngestResult:
        """Process visible ready bundles once."""
```

Dependencies:

- `reports_store`,
- `reports_transport`,
- shared bundle validator,
- `shutil`,
- `pathlib`.

Boundaries:

- no UI mutation directly;
- no response writing in Phase 1;
- no BUGS.md mutation.

Tests:

- no roots configured;
- happy-path ingest;
- no READY skip;
- bad hash quarantine;
- duplicate same hash skip;
- duplicate different hash quarantine.

Acceptance:

- malformed bundles never crash AM;
- accepted bundles copy into local ingest storage via temp-then-rename;
- ingest writes status event and timestamp.

### 21.14 `audit_module/v1/reports_panel.py`

LOC budget: 260-480.

Public surface:

```python
class ReportsPanel(QWidget):
    """AM Reports list/detail surface for tester report bundles."""

    def refresh(self) -> None:
        """Reload report list and timestamp the refresh."""

    def show_report(self, bundle_id: str) -> None:
        """Open report detail from AM report store."""
```

Dependencies:

- PySide6,
- `reports_store`,
- optional `reports_ingest`.

Boundaries:

- developer-only AM shell;
- no clinical module navigation;
- no direct transport mutation except explicit Check Now / Ingest action;
- no Relay work.

Tests:

- widget construction smoke;
- empty state;
- row open/detail;
- Check Now timestamp and result line;
- malformed/quarantined row visible.

Acceptance:

- list/detail works with a synthetic ingested bundle;
- Check Now gives dated/timed feedback;
- Inspector/Open Folder style actions either work or are disabled with reason;
- no clipped labels at min/default/large sizes.

## 22. Completion Checklist For Implementers

- Read this v1.1 spec end-to-end.
- Confirm Darrin accepted the brief or this spec.
- Confirm work is not Relay.
- Create schema/validator first.
- Use synthetic fixture data only.
- Run unit tests before UI.
- Run integration test through local temp transport.
- Run live visual verification for UI.
- Confirm every action button produces feedback.
- Confirm no absolute paths in shipped manifest.
- Confirm no real PHI in test bundles.
- Report pass/fail with exact commands and timestamps.

## 23. Implementation Risks And Cross-Validation

### R1. Dispatch File Count Mismatch

The dispatch says "9 files from v1 section 5.1"; v1 lists 10 entries when
`__init__.py` is counted. This spec resolves the ambiguity as 9 functional files
plus the package marker. If a future implementer counts differently, they must
not delete `__init__.py`; they should preserve the package marker and report the
functional count explicitly.

### R2. AM Screen Path Drift

The expected AM surfaces are now under `audit_module/v1/` for the window stack.
Legacy names such as `audit_module_window.py` appear in older design text, but
current code uses `window.py`, `screen_a.py`, `screen_b.py`, and
`screen_archive.py`. Implementation must target the current files.

### R3. Workflow Capture Must Not Block

Auto-transcription can finish after session stop. The round-trip hook must not
block stop/save or assume transcript exists immediately. The review UI must show
pending transcript or defer Ship.

### R4. Absolute Path Leakage

Existing audit package code can resolve absolute source paths internally, but
the round-trip manifest must not ship absolute Windows paths. Local DBs may keep
local provenance; external bundle fields may not.

### R5. UI Feedback Regression

Darrin has repeatedly found buttons/tools that look wired but give no feedback.
This spec makes button feedback acceptance-critical. BA or future audit checks
should include an "action feedback" rule for every interactive button in tester
and AM Reports surfaces.

### R6. Offscreen Verification Gap

Qt offscreen smoke tests cannot prove live rendering. UI implementation must
include live visual verification. This is especially important for AM Reports
because status panes, evidence blocks, and action rows can look correct in code
and still fail visually.

### R7. Tier B Temptation

The architecture is Tier B compatible, but Phase 1 is Tier A only. Adding real
PHI transport, cloud APIs, encryption policy, or onboarding is a scope breach.

### R8. Response Writer Scope

The Phase 1 list from v1 stops at minimal AM Reports list/detail. Response
writer is part of the full loop but may be Phase 2 unless Darrin explicitly
expands Phase 1. Do not silently expand the implementation slice.
