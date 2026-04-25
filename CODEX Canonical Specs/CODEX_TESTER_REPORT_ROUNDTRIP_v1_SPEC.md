# CODEX Tester-Report Round-Trip v1 Spec

Status: Proposed architecture spec for Claude/CC review
Date: 2026-04-25
Author: Codex
Output path: `C:\CODEX PG\CODEX Canonical Specs\CODEX_TESTER_REPORT_ROUNDTRIP_v1_SPEC.md`

Read-only source references:

- `C:\panda-gallery\workflows\audit\TESTER_REPORT_ROUNDTRIP_BRIEF_v1.md`
- `C:\panda-gallery\workflow_capture.py`
- `C:\panda-gallery\scripts\transcribe_latest.py`
- `C:\panda-gallery\PANDA_GALLERY_AUTOTRANSCRIBE_SPEC.md`
- `C:\panda-gallery\PANDA_GALLERY_TRANSCRIPT_V2_SPEC.md`
- `C:\panda-gallery\PANDA_GALLERY_COMPLIANCE_SPEC.md`
- `C:\panda-gallery\codex_audit\`
- `C:\panda-gallery\audit_module\`
- `C:\panda-gallery\BUGS.md` #134 and #97
- `C:\panda-gallery\workflows\audit\PG_TRUTH_v1.md`

Boundary: this document proposes architecture only. It does not authorize implementation and does not edit `C:\panda-gallery`.

## 1. Goal Statement

Panda Gallery needs a structured round-trip between testers and Darrin. During a normal PG session, a tester captures audio narration and screenshots, reviews the session artifacts, names the issue, and ships a portable bundle. Darrin's developer-mode Audit Module polls for new bundles, ingests them, reviews the evidence, and sends a structured response back. The tester sees that response inside their own PG.

The cloud transport is only a pipe. Both tester PG and developer AM keep their own local sent/received databases as the durable systems of record.

## 2. Same Binary, Different Mode

There is one PG binary.

Tester mode is normal PG launched without `--dev`:

- AM is invisible.
- Tester report features live in user-facing modules.
- Candidate code homes: `tester_reports/` as a peer module, plus small workflow-capture hooks.
- Tester-side code must not import or live under `audit_module/`.

Developer mode is PG launched with `--dev`:

- AM is accessible from the Testing menu per the #97 `--dev` separation.
- Developer-side report queue, response composer, and archive tools live inside AM as a new Reports section peer to the existing Bugs surface.

`PG_TRUTH_v1.md` hard-locks AM as dev-only. This spec does not surface AM to clinical users.

## 3. Locked Decisions

These decisions come from the brief and are not re-debated here.

### 3.1 Tiered Patient-Data Architecture

Tier A ships first:

- Synthetic test data only.
- Testers use fixture/sandbox patients.
- Regular Dropbox/local-sync transport is acceptable.
- Bundles must still avoid unnecessary local path leakage.

Tier B is designed for later:

- Real-PHI mode is gated and opt-in.
- Transport must be HIPAA-capable, such as Dropbox Business with signed BAA or AWS S3 with server-side encryption.
- Encryption at rest and in transit, access audit logging, and clinician-tester agreements are required.
- AI redaction is defense in depth, not the primary control.

Tier C is fallback:

- If Tier B is impractical, real-PHI workflow is disallowed or hard-blocked by redaction confidence.

Architectural consequence: transport and redaction are interfaces. Tier A to Tier B must be a configuration/provider swap plus compliance enablement, not a rewrite.

### 3.2 Transcript Sync Is Locked

Transcript v2 already provides sentence-level timestamp alignment to F12 frames. The round-trip system consumes `transcript.md` and `metadata.json` as shipped. It does not redesign transcription.

### 3.3 Per-Tester Folder Topology

Each tester has a shared local-sync folder:

```text
<Tester>-PG-Reports/
  outbox/       # tester PG writes, AM reads
  inbox/        # AM writes, tester PG reads
  archive/      # terminal bundles/responses moved by AM
```

AM watches all configured tester roots. Tester PG only watches its own root.

### 3.4 Polling

Both sides poll every 5 minutes by default while PG is running. Poll interval is QSettings-configurable but not exposed in normal UI. PG reads and writes only the local sync mirror. It does not call Dropbox APIs, use OAuth, or require webhooks in v1.

### 3.5 Response Shape

Each response includes:

- status from a configurable set
- optional free-text message
- referenced bundle/report ID

No threaded replies in v1. Follow-up information is a new report that references the prior report ID.

### 3.6 Lifecycle States

The eight locked states are:

1. Drafted
2. Shipped
3. Acknowledged-by-pipe
4. Seen
5. Ingested
6. Responded
7. Response-received
8. Closed

Discarded is a sibling terminal local-only tester state that never enters the pipe.

## 4. Architecture Overview

```text
Tester PG, normal mode
  workflow_capture.py  ->  session folder
  transcribe_latest.py ->  transcript.md
  tester_reports/
    pre-send review
    bundle builder
    local tester_reports.db
    transport poller
       |
       | local folder write/read
       v
<Tester>-PG-Reports/outbox + inbox + archive
       ^
       | local folder read/write
       |
Developer PG, --dev mode
  audit_module/
    Reports section
    report ingest service
    response composer
    local am_reports.db
    transport poller
```

The design adds a new report layer. It composes with workflow capture and AM; it does not move their existing responsibilities.

## 5. Module Breakdown

### 5.1 Tester-Side Module: `tester_reports/`

Recommended new peer package:

```text
tester_reports/
  __init__.py
  bundle_builder.py
  bundle_manifest.py
  bundle_validator.py
  db.py
  poller.py
  redaction.py
  transport.py
  ui_review.py
  ui_my_reports.py
```

Responsibilities:

- discover completed workflow sessions
- wait for transcript readiness when audio exists
- build report bundles from selected session artifacts
- own tester identity and local report DB
- write bundles to outbox atomically
- poll inbox for responses
- surface My Reports and inbound notifications

This module may call into workflow-capture metadata and file layout, but workflow capture remains the capture/session owner.

### 5.2 Workflow Capture Integration

`workflow_capture.py` remains the source of session artifacts:

- session directory under `workflows/session_YYYYMMDD_HHMMSS/`
- numbered PNG screenshots
- optional `audio.wav`
- `metadata.json`
- `LATEST.txt`
- auto-transcribe subprocess that creates `transcript.md`

New hook recommendation:

- after stop-session save completes, emit or call a small report-service notification: `ReportService.on_session_saved(session_dir)`
- if `transcript.md` is pending, show the pre-send review as `Drafted (transcript pending)` or defer until transcript completion
- do not block workflow capture stop on bundle assembly or Dropbox sync

### 5.3 Developer-Side AM Reports Section

AM gets a Reports section peer to Bugs.

Recommended additions:

```text
audit_module/
  reports_store.py
  reports_ingest.py
  reports_transport.py
  reports_window.py or reports_panel.py
```

Responsibilities:

- poll every configured tester outbox
- verify atomic-write marker, manifest, checksums, schema, and redaction gate
- copy accepted bundles into local AM storage
- register inbound rows in `am_reports.db`
- render report inbox/detail/response composer inside AM
- write responses to tester inbox atomically
- move terminal artifacts to shared archive by month

### 5.4 Shared Transport Interface

Use one interface consumed by both tester and AM.

```python
class ReportTransport:
    def list_incoming(self, channel: str) -> list[RemoteItem]: ...
    def stage_outgoing(self, local_path: Path, channel: str, remote_name: str) -> StagedWrite: ...
    def commit(self, staged: StagedWrite) -> None: ...
    def fetch(self, item: RemoteItem, dest_dir: Path) -> Path: ...
    def archive(self, item: RemoteItem, archive_relpath: str) -> None: ...
    def health_check(self) -> TransportHealth: ...
```

For Dropbox v1, this is a local filesystem transport pointed at the Dropbox-synced mirror. Later Tier B providers implement the same interface.

## 6. Bundle Format Recommendation

Recommend directory-with-manifest for v1.

Reasons:

- Dropbox syncs individual files efficiently.
- Atomic readiness is easy: write to `.staging`, then write `READY.json` last, then rename or expose the directory.
- Large sessions avoid repeated ZIP rewrites.
- Review/debugging is easy in File Explorer.
- The AM can validate file presence and checksums without unpacking.

ZIP remains a future export format, but not the v1 sync format.

### 6.1 Bundle Directory Shape

```text
report_<tester_id>_<local_seq>_<hash>/
  manifest.json
  READY.json
  source/
    metadata.json
    transcript.md
    transcribe.log
    audio.wav
  screenshots/
    001.png
    002.png
  derived/
    report_summary.md
    redaction_report.json
  logs/
    bundle_events.jsonl
```

`READY.json` is written last and includes the manifest hash. Pollers ignore directories without `READY.json`.

### 6.2 Bundle Cardinality

Recommended v1 rule: one bundle equals one report.

A report may include a full session as evidence, but the tester names one issue/question/suggestion in the pre-send review. If a single session reveals several issues, the tester creates multiple reports that can reference the same `source_session_id`. Deduplication of shared media can wait until bundle size becomes a real problem.

Reason: AM response protocol, lifecycle state, and tester notification are all simpler when one report receives one status.

## 7. Bundle Lifecycle State Machine

### 7.1 Tester-Side States

```text
Drafted
  -> Discarded                 tester discards before shipping
  -> Shipped                   tester clicks Ship to Darrin and local write succeeds
Shipped
  -> Acknowledged-by-pipe      transport health/check observes local sync has accepted file
Acknowledged-by-pipe
  -> Response-received         tester poller sees response in inbox
Response-received
  -> Closed                    terminal response status recorded and read/closed locally
```

Tester DB remains authoritative for the tester side even if Dropbox files are later moved or deleted.

### 7.2 Developer-Side States

```text
Seen
  -> Quarantined               validation/security failure
  -> Ingested                  copied into AM local storage and DB row written
Ingested
  -> Responded                 response JSON written to tester inbox
Responded
  -> Closed                    terminal status archived by AM
```

`Quarantined` is not in the locked eight, but is needed as an AM-local failure state for malformed/malicious bundles. It never tells the tester by default unless Darrin chooses to respond.

### 7.3 Archive Mechanics

When response status is terminal, AM moves both original bundle and response to:

```text
<Tester>-PG-Reports/archive/YYYY-MM/
```

AM records the archive move in its DB. Tester PG records the response and shows the row under Closed reports even if it no longer sees the transport file.

## 8. Data Shapes

### 8.1 Bundle Manifest v1

```json
{
  "schema": "pg.tester_report_bundle.v1",
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
  "warnings": []
}
```

No absolute Windows paths are allowed in external bundle manifest fields. If local provenance is useful, store it in the local DB only, not in the shipped manifest. This directly closes the #134 concern at the transport boundary.

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

Pollers only process a directory when `READY.json` exists, parses, and matches the manifest hash.

### 8.3 Response Payload v1

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

Responses also use a ready marker or atomic temp-then-rename pattern.

### 8.4 Tester DB

Use SQLite, not ad hoc JSON, because this is user-facing state with updates over time.

Tables:

```text
tester_reports(
  report_id text primary key,
  bundle_id text unique,
  tester_id text,
  source_session_id text,
  title text,
  state text,
  created_at text,
  shipped_at text,
  pipe_ack_at text,
  response_received_at text,
  closed_at text,
  local_bundle_path text,
  transport_bundle_path text,
  last_error text
)

report_responses(
  response_id text primary key,
  report_id text,
  bundle_id text,
  status_code text,
  status_label text,
  terminal integer,
  message text,
  received_at text,
  seen_at text,
  payload_path text
)

report_events(
  event_id integer primary key autoincrement,
  report_id text,
  event_type text,
  at text,
  detail_json text
)
```

### 8.5 Developer AM DB

Use a separate SQLite database for reports, even though AM v0 issue state currently uses JSON sidecars. Reports have polling, duplicate detection, response writes, and archive histories; SQLite is the right persistence level.

Suggested path:

`workflows/audit/am_reports.db`

Tables:

```text
inbound_reports(
  bundle_id text primary key,
  report_id text,
  tester_id text,
  title text,
  state text,
  seen_at text,
  ingested_at text,
  responded_at text,
  closed_at text,
  local_ingest_path text,
  source_transport_path text,
  manifest_sha256 text,
  quarantine_reason text
)

outbound_responses(
  response_id text primary key,
  bundle_id text,
  tester_id text,
  status_code text,
  status_label text,
  terminal integer,
  message text,
  created_at text,
  shipped_at text,
  payload_path text
)

report_bug_links(
  bundle_id text,
  bug_number integer,
  link_kind text,
  created_at text
)

am_report_events(
  event_id integer primary key autoincrement,
  bundle_id text,
  event_type text,
  at text,
  detail_json text
)
```

## 9. Transport Providers

### 9.1 Dropbox Local Folder Provider

Default v1 provider. It requires the Dropbox desktop client to be installed and signed in.

Config:

```json
{
  "provider": "local_sync_folder",
  "provider_label": "Dropbox",
  "tester_roots": [
    {"tester_id": "rebecca", "root": "C:/Users/.../Dropbox/Rebecca-PG-Reports"}
  ],
  "poll_interval_seconds": 300
}
```

Preflight checks:

- root exists
- outbox/inbox/archive exist or can be created
- test write/delete succeeds in a `.pg_preflight` temp folder
- available disk space exceeds configured minimum
- optional Dropbox process/path hint is present, but do not depend on Dropbox API

### 9.2 Google Drive Desktop

Same local-folder model. Watch for placeholder/offline files and delayed hydration. Good future provider, not v1 default.

### 9.3 OneDrive

Same local-folder model. Windows availability is strong, but OneDrive Files On-Demand creates partial/hydration states. Viable if atomic-read checks are strict.

### 9.4 SMB Share

Good for a clinic LAN or office testing. No cloud account dependency. Requires VPN/LAN availability and Windows credential handling. Viable for in-clinic Tier A or controlled Tier B, but weaker for remote beta.

### 9.5 Tier B Providers

Future provider examples:

- Dropbox Business with BAA and team controls
- S3-compatible object storage with server-side encryption, object lock, IAM, and audit logs
- managed HIPAA file transfer platform

All must implement the same `ReportTransport` interface.

## 10. Bundle Pipeline With Redaction Hook

Pipeline stages:

1. Discover session folder.
2. Verify `metadata.json` exists and screenshots referenced by metadata exist.
3. Wait for or detect `transcript.md` when audio was recorded.
4. Build draft manifest with relative package paths only.
5. Run redaction classifier/hook.
6. If Tier A and `contains_phi_declared` or redaction detects likely PHI, block shipping and show tester a clear warning.
7. Copy selected artifacts into a staging bundle directory.
8. Hash files and manifest.
9. Write `READY.json` last.
10. Move/expose staged bundle to transport outbox.
11. Write local DB event.

Redaction hook interface:

```python
class RedactionStage:
    def inspect(self, bundle_dir: Path, manifest: dict) -> RedactionReport: ...
    def apply(self, bundle_dir: Path, manifest: dict) -> RedactionResult: ...
```

Tier A implementation can be conservative:

- require tester declaration: synthetic only
- scan manifest/transcript for obvious patient identifiers if available
- block if absolute local paths or patient DB names appear in shipped payload fields
- produce `derived/redaction_report.json`

Tier B later replaces or extends this hook with real redaction/encryption policy.

## 11. Polling And Atomic-Write Trap

### 11.1 Incoming Bundle Poll

For each tester root/outbox:

1. List directories matching `report_*`.
2. Skip if `.staging` suffix or no `READY.json`.
3. Parse `READY.json`.
4. Parse `manifest.json`.
5. Recompute manifest hash excluding integrity self-fields.
6. Verify every file record exists, is relative, has matching byte count, and sha256 matches.
7. If validation passes, copy to local AM ingest storage using temp-then-rename.
8. Insert or update `inbound_reports` by `bundle_id`.
9. If duplicate `bundle_id` with same hash, log duplicate and skip.
10. If duplicate `bundle_id` with different hash, quarantine.

### 11.2 Incoming Response Poll

Tester PG polls its inbox similarly:

- only process response payloads with ready marker or stable temp-free name
- validate schema, bundle_id, tester_id, and integrity hash
- ignore duplicate same-hash response
- quarantine/log conflicting duplicate response_id
- update tester DB state to Response-received
- show non-modal toast

### 11.3 Atomic Write Pattern

All writers use:

```text
<name>.staging/
  files...
rename to <name>/ or write READY.json last
```

If Windows/Dropbox makes directory rename unreliable across sync boundaries, keep the final directory name from the start but omit `READY.json` until every file is written and closed. The marker is the true commit.

## 12. UX Shape

### 12.1 Tester Pre-Send Review

Trigger: session stop plus bundle draft readiness.

Screen content:

- session duration
- screenshot count
- total size
- transcript preview, collapsible
- screenshot thumbnails
- issue title field
- optional summary/details field
- synthetic-data declaration checkbox for Tier A
- buttons: Ship to Darrin, Save draft, Discard

No auto-ship.

### 12.2 Tester My Reports

Normal-mode PG gets a My Reports view. Candidate location: Workflow Capture menu or a new Reports menu; final UI placement is a downstream UX decision.

Rows show:

- local report number
- title
- sent time
- current status
- unread response marker
- closed marker

Detail view shows original transcript/screenshot evidence plus Darrin response.

### 12.3 Inbound Tester Notification

When a response arrives:

- show a small non-modal toast: `Darrin responded to Report #NNN.`
- click opens report detail
- do not interrupt current clinical/test workflow

### 12.4 Developer AM Reports

AM Reports section includes:

- inbox queue: New, Seen, Ingested
- in-flight: Responded, awaiting tester read or non-terminal
- archived recent
- detail panel with tester ID, title, manifest metadata, transcript preview, screenshots
- response composer with status dropdown, free text, links to BUGS.md numbers, send/save draft controls

AM dashboard counter:

`3 NEW REPORTS - 1 RESPONSE PENDING UPLOAD - 2 IN-FLIGHT`

### 12.5 BUGS.md Cross-Link

When status is `Duplicate of #N` or Darrin links a report to a bug:

- AM writes a row to `report_bug_links`
- AM bug detail can show `Reported by <tester> on <date> (report <id>)`
- Direct BUGS.md mutation is deferred unless Darrin separately approves an AM write path

## 13. Status Configuration

Recommended v1 config home:

`workflows/audit/report_statuses.json`

AM owns this file and bootstraps defaults if missing. Responses embed `status.code`, `status.label`, and `status.terminal` so tester PG can render status even if it does not have the config file.

Default statuses:

```json
[
  {"code": "acknowledged", "label": "Acknowledged", "terminal": false},
  {"code": "investigating", "label": "Investigating", "terminal": false},
  {"code": "duplicate", "label": "Duplicate of #N", "terminal": true, "requires_bug_number": true},
  {"code": "fix_in_progress", "label": "Fix in progress", "terminal": false},
  {"code": "shipped", "label": "Shipped in vX.Y", "terminal": true, "requires_version": true},
  {"code": "wont_fix", "label": "Won't fix", "terminal": true},
  {"code": "need_more_info", "label": "Need more info", "terminal": false}
]
```

## 14. Failure Modes

- Dropbox client missing: preflight fails; tester can save draft but cannot ship.
- Dropbox offline: bundle remains Shipped/Pending local upload; retry on next poll.
- Disk full: staging write fails; DB records last_error; no READY marker written.
- Partial sync: missing READY or checksum mismatch means skip until next poll.
- Duplicate bundle same hash: log and skip.
- Duplicate bundle different hash: quarantine and surface to Darrin.
- Malformed manifest: quarantine, no crash.
- Absolute path in shipped manifest: validation failure; block or quarantine.
- PHI suspected in Tier A: block shipping and require Darrin/tester decision.
- Response references unknown bundle_id: quarantine in tester PG.
- Response status not in embedded shape/config: render as unknown status and log warning.
- Archive move fails: leave files in place, keep DB state, retry next poll.
- Bundle exceeds size budget: warn before ship; require explicit confirmation or block if over hard cap.

## 15. Security And Compliance Posture

Tier A is synthetic-only. That is the safety model.

Still required in v1:

- no raw absolute paths in shipped manifests
- no tokens/secrets/Dropbox credentials in PG config
- checksums for every shipped file
- schema validation before ingest
- local DB event logs for state transitions
- preflight messaging that Dropbox desktop client is required
- clear warning that real patient data is not allowed in Tier A

Tier B requires a separate spec before any real-PHI use.

## 16. Tier A To Tier B Migration

The migration path must preserve these interfaces:

- `ReportTransport`
- `RedactionStage`
- bundle manifest schema with tier block
- local DB state machines
- response payload schema

Tier B adds:

- HIPAA-capable transport provider config
- per-tester authorization and agreements
- encryption key management
- stronger redaction/pre-upload policy
- access audit logs
- retention/destruction policy
- healthcare attorney review

No Tier B implementation should begin from this v1 spec alone.

## 17. Smoke-Test Shape

A successful v1 demo:

1. Configure Darrin-as-tester root and Darrin-as-dev AM root locally.
2. Launch PG without `--dev`.
3. Record a short synthetic workflow session with audio and two F12 screenshots.
4. Stop session; transcript completes.
5. Pre-send review opens; tester enters title and confirms synthetic-only.
6. Tester clicks Ship to Darrin.
7. Bundle appears in tester outbox with `READY.json`.
8. Launch PG with `--dev`; open AM Reports.
9. AM poll ingests bundle and shows it as New/Ingested.
10. Darrin opens report, sees transcript and screenshots, sends response `Acknowledged` with message.
11. Response appears in tester inbox.
12. Tester PG polls, shows toast, and My Reports row updates.
13. Darrin sends terminal response `Duplicate of #136` or `Shipped in vX.Y`.
14. AM archives bundle/response under `archive/YYYY-MM/`; both local DBs keep history.

## 18. Open Questions For Darrin

The brief required these to remain explicit.

1. Bundle format: this spec recommends directory-with-manifest for v1; confirm or choose ZIP/tar.gz.
2. Manifest schema: confirm the v1 fields above, especially tier/redaction and file records.
3. Status set authoring: this spec recommends AM-owned `workflows/audit/report_statuses.json` with embedded status labels in responses.
4. Tester identity: choose QSettings, local `tester_profile.json`, launch flag, or installer setup. Codex recommends local profile plus QSettings mirror.
5. AM-side database schema: this spec recommends separate SQLite `am_reports.db`, not extension of the existing AM issue JSON.
6. Bundle deduplication: this spec recommends first bundle ID plus same hash wins; same ID with different hash quarantines.
7. Failed delivery handling: this spec recommends save draft / pending upload with retry and visible last_error.
8. Bundle-to-report cardinality: this spec recommends one bundle equals one report for v1.
9. Redaction interface: this spec recommends pre-upload inspection for Tier A/Tier B, with optional post-download re-run later.
10. Bundle size/archive lifecycle: decide soft and hard caps; Codex suggests warn at 50 MB and require confirmation above 100 MB for Tier A.
11. Transport choice for v1: this spec uses Dropbox local-folder provider while keeping Google Drive, OneDrive, and SMB as compatible future providers.
12. Schema validation security: this spec recommends quarantine on failed validation, never crash or auto-ingest.
13. Clinical-tester onboarding: out of v1 implementation, but must be defined before any external clinician uses real patient data.

## 19. Recommended First Implementation Slice

Do not implement the whole system in one pass.

First slice:

- tester profile config
- directory bundle builder from a completed synthetic session
- manifest + READY marker + validator
- local filesystem transport pointed at a test folder
- tester SQLite DB state updates through Drafted/Shipped
- AM ingest poller into `am_reports.db`
- minimal AM Reports list/detail view

Second slice:

- response writer
- tester inbox poller
- My Reports response view
- archive move on terminal status

Third slice:

- redaction blocker hardening
- status config editor or documented config
- size-budget UX
- alternate transport providers

## 20. Final Recommendation

Build the v1 around a boring local-folder transport and strong local records. The important product is not Dropbox; it is the evidence-preserving loop: tester captures context, Darrin receives structured evidence, Darrin responds, and both sides can prove what happened without relying on chat memory or cloud folder state.
