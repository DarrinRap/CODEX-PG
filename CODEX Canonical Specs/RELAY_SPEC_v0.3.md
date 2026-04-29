# Relay Specification v0.3

Date: 2026-04-28
Author: Codex
Status: Canonical spec amendment. No Panda Gallery runtime code changed.

Canonical visual references:

- `C:\panda-gallery\workflows\design\pg_general_mockups\relay_module_v1.html`
- `C:\panda-gallery\workflows\design\RELAY_SCREEN_C_DESIGN_v1.md`

Sources read:

- `C:\CODEX PG\CODEX Canonical Specs\RELAY_SPEC_v0.1.md`
- `C:\panda-gallery\workflows\design\RELAY_SCREEN_C_DESIGN_v1.md`
- `C:\panda-gallery\workflows\design\pg_general_mockups\relay_module_v1.html`
- `C:\panda-gallery\STRATEGY_NOTES.md`
- `C:\panda-gallery\scripts\dropbox_integration_test.py`
- `C:\panda-gallery\workflows\design\RELAY_TESTER_SETUP_QA_ADDENDUM_v1.html`

## §1 Overview and Design Philosophy

Relay is a two-sided asynchronous communication module built into Panda Gallery.
It lets a remote tester record an audio description of a bug, attach screenshots,
review the transcript, and send that package to a configured developer recipient.
On the developer side, Relay receives the report, sends an automatic receipt
acknowledgment, drafts a BUGS.md entry for one-click capture, and provides a
status-update channel back to the tester.

Relay is not chat. It is a structured bug-report handoff surface. Its job is to
move a real tester observation from "Rebecca saw something wrong" to "Darrin has
a clean, captured BUGS.md entry and can send progress updates back" with the
fewest possible ambiguous manual steps.

Relay is asynchronous by design:

- No self-hosted server.
- No realtime socket or live presence requirement.
- Dropbox is the transport layer between installs.
- Each install stores a local archive of sent and received packages.
- Reports and status updates can arrive while the other person is offline.

Relay is separate from Remote Testing. Remote Testing packages a workflow-capture
session for later triage. Relay is a bidirectional communication module for bug
reports and status messages. They reuse the same Dropbox transport/auth pattern,
but they are separate product surfaces.

Relay inherits the 2026-04-27 PG design posture from `STRATEGY_NOTES.md`:
make values configurable, not hard-coded, when they could reasonably vary per
user, practice, or workflow.

Applied to Relay:

- Recipient names are settings, not constants.
- Dropbox recipient folder paths are settings, not constants.
- A primary/default recipient is a setting, not a hardcoded "Darrin".
- Auto-acknowledgment is a setting with a sensible default.
- Acknowledgment and status-update copy is template-driven and editable.
- Duplicate detection threshold is configurable.
- Delivery receipt verbosity is configurable.
- Developer/tester role behavior is configured in Relay Settings.

Constants remain appropriate for schema field names, package versioning, status
enums, storage filenames, and data integrity rules.

## §2 Locked Decisions

### D1 - Name

The module name is **Relay**.

UI usage:

- Window title: `Panda Gallery - Relay`.
- Module label: `Relay`.
- Statusbar prefix: `Relay`.
- Package IDs use `relay_...`.

### D2 - Configurable Recipients, Not Hardcoded Recipients

Each PG install configures one or more named recipients in Relay Settings.
A recipient record includes display name, Dropbox folder path or channel path,
optional role label, primary/default flag, and enabled/disabled state.

The send UI uses the primary configured recipient:

- Button label pattern: `Send to [configured recipient]`.
- If no recipient is configured, the primary action is disabled and points the
  user to Relay Settings.

### D3 - Semi-Automatic BUGS.md Capture

When a developer receives a bug report, Relay auto-generates a draft BUGS.md
entry from the transcript and package metadata. The developer sees the draft in
a `Capture to BUGS.md` card and clicks one button to commit it.

Relay must not write directly to BUGS.md without this developer action.

### D4 - Separate Tester Updates Surface

The tester's Relay window must surface developer acknowledgments and status
updates in a first-class Updates area, not only inside the original sent report.

In the v0.2 tester hub this is the `Updates (N)` tab. Opening an update marks it
read and clears the unread badge when no unread updates remain.

### D5 - Dropbox Transport

Relay uses Dropbox as the sync transport. It reuses and extends the OAuth2 PKCE
flow pattern from Remote Testing Phase 4 and `dropbox_sync.py`.

Relay must not introduce a new authentication approach.

### D6 - Auto-Acknowledgment

On the developer side, receipt of a report triggers an automatic acknowledgment
back to the tester's Relay Updates surface when auto-acknowledge is enabled.

Default: on.

Implementation note: the acknowledgment may be represented as a status update
package with `kind: "ack"` and `status: "acknowledged"`.

### D7 - Status Update Flow

Status updates are developer-initiated.

Status options:

- Acknowledged.
- In Progress.
- Fixed.
- Won't Fix.

Each update optionally includes editable message text. Each update routes through
Dropbox to all linked reporters for that report group and also appears in the
developer Sent view.

### D8 - General Configurability

When a value could vary per user, practice, or workflow, it is a setting with a
sensible default, not a constant.

### D9 - Role Architecture

Relay uses a single window layout with role-aware content. The install role is
configured in Relay Settings as developer or tester.

- Developer role: primary tab is All Reports.
- Tester role: primary tab is My Reports.
- Same shell, statusbar, settings access, sync status grammar, and visual
  language are used for both roles.

### D10 - Duplicate Language Rule

Relay always uses the word **Duplicate**.

Never use "dupe", "dupe?", or informal variants in UI labels, badges, banners,
tooltips, templates, specs, or prompts.

## §3 Screen Anatomy

The v1 mockup at `relay_module_v1.html` remains the visual reference for Relay's
palette, typography, chrome, statusbar, list/detail hierarchy, and base
send/receive flow. Screen C extends that model into role-aware hub screens.

### §3.1 Screen 1 - Tester: Active Capture

Purpose: let the tester record a spoken bug report while collecting screenshots.

Required elements:

- Window title `Panda Gallery - Relay`.
- Module header with Relay title and Settings access.
- Recording card with live state, elapsed time, and waveform or level meter.
- Screenshot filmstrip with count, existing thumbnails, and manual capture tile.
- Primary action: `Stop & Process`.
- Secondary/destructive action: `Discard`.
- Statusbar with Relay prefix, recording state, and package folder name.

Behavior:

1. Starting capture creates a local package folder under `workflows/relay/sent/`.
2. Audio is written to `audio.wav`.
3. Screenshots are written as zero-padded PNGs.
4. `metadata.json` is started immediately and updated as capture progresses.
5. `Stop & Process` finalizes audio/screenshots and starts transcription.
6. `Discard` asks for confirmation, then removes or marks the local draft
   package according to the archive policy.

### §3.2 Screen 2 - Tester: Review & Send

Purpose: let the tester verify the transcript and attachments before sending.

Required elements:

- Transcript review card with edit affordance.
- Screenshot grid or filmstrip.
- `Play audio` action.
- Primary button: `Send to [configured recipient]`.
- Secondary action: `Edit transcript`.
- Destructive action: `Discard`.
- Statusbar with Dropbox sync state.

Send is disabled when no primary recipient is configured.

### §3.3 Screen 3 - Tester: Sent + Inbox Legacy Flow

The v0.1 tester flow used Inbox and Sent tabs after send. v0.2 supersedes this
with the tester hub in §14, but this legacy flow remains useful as the behavior
baseline:

- Sent report selected after send.
- Auto-ack and status updates shown in timeline.
- New status updates surface with unread badges.

### §3.4 Screen 4 - Developer: Inbox Legacy Flow

The v0.1 developer Inbox remains the behavior baseline for a single incoming
report:

- Incoming report list.
- Selected report detail with transcript, screenshots, and capture card.
- `Capture to BUGS.md` is developer-clicked.
- `Send update to [tester]` opens compose.
- Auto-ack sent indicator appears locally.

v0.2 supersedes the top-level layout with the developer hub in §9.

### §3.5 Screen 5 - Developer: Send Update Legacy Flow

The v0.1 send-update screen remains the base compose behavior:

- Status picker.
- Message body.
- Destination context.
- Dropbox delivery via status update package.

v0.2 strengthens this flow with template auto-fill, preview, and linked-reporter
fanout in §11.

### §3.6 Screen 6 - Developer Hub

Purpose: let the developer triage all incoming reports across testers, identify
duplicates, capture BUGS.md entries, and send status updates.

Required layout:

```text
Relay Window
├── Title bar
├── Module screen header [RELAY | view toggle: All Reports / By Tester | Settings]
├── Tab strip [All Reports (N) · By Tester · Sent · Templates]
├── Left rail - report list or tester lanes
├── Right panel - selected report detail
└── Statusbar [Relay · sync state · version/channel]
```

All Reports is the default developer tab. It shows a unified inbox, newest first,
with unread count badge on the tab when unread reports exist.

By Tester groups reports into tester-specific lanes. It is available both as a
tab destination and as a view mode within the hub header where the implementation
uses a segmented control.

### §3.7 Screen 7 - Tester Hub

Purpose: let a tester review their own reports, read developer updates, and start
a new report.

Required tab strip:

```text
My Reports · Updates (N) · New Report
```

My Reports is the primary tester tab. Updates shows developer acknowledgments and
status updates with an unread badge. New Report launches Screen 1 Active Capture.

## §4 Relay Settings

Relay Settings are accessible from the gear icon in the Relay screen header.
Settings should use progressive disclosure: common operational settings first,
technical connection details second.

### §4.1 Recipients

Recipient fields:

- Name.
- Dropbox folder path or channel path.
- Optional role label.
- Primary recipient flag.
- Enabled/disabled state.

Actions:

- Add recipient.
- Edit recipient.
- Remove recipient.
- Set primary.
- Test channel path.

### §4.2 Auto-Acknowledge

Setting: `relay/autoAcknowledgeEnabled`

Default: on.

When enabled, receipt of any valid bug report package triggers an acknowledgment
status update.

### §4.3 Acknowledgment Text

Setting: `relay/acknowledgmentText`

Default:

```text
Received & acknowledged - [developer name] received your report at [time]. A bug entry has been drafted and linked to your name.
```

This v0.2 text intentionally says "drafted" because BUGS.md capture remains
semi-automatic until the developer clicks `Capture to BUGS.md`.

### §4.4 Default Status on Capture

Setting: `relay/defaultStatusOnCapture`

Default: `OPEN`.

### §4.5 Dropbox Connection

Settings/controls:

- Connect Dropbox.
- Reconnect Dropbox.
- Connected account name.
- Last sync timestamp.
- Last error.
- Channel test button.

Relay must reuse the existing Dropbox OAuth2 PKCE module/pattern from Remote
Testing. Do not add a new OAuth flow.

### §4.6 Local Archive Folder

Setting: `relay/localArchiveFolder`

Default: `workflows/relay/`.

The user may change it, but Relay must validate that the path is writable and
must not silently migrate existing packages without confirmation.

### §4.7 Duplicate Detection Threshold

Setting: `relay/duplicateSimilarityThreshold`

Default: `80`.

Meaning: AI-assisted duplicate detection flags a possible duplicate when the
similarity score is at or above the threshold percentage.

The setting applies to transcript text, screenshot similarity, and timing signals
as implemented by the duplicate-detection adapter.

### §4.8 Delivery Receipt Verbosity

Setting: `relay/deliveryReceiptVerbosity`

Allowed values:

- `full_detail`
- `failures_only`
- `off`

Default: `failures_only`.

This controls per-message delivery receipt visibility in the Sent tab. The global
Dropbox sync statusbar remains visible regardless of this setting.

### §4.9 Role Configuration

Setting: `relay/installRole`

Allowed values:

- `developer`
- `tester`

Default is selected during Relay setup. The role controls visible tabs, primary
view, default actions, and copy, but does not change the underlying package
schema.

When a tester-role install opens Relay for the first time with no stored Dropbox
token, it enters the tester setup wizard (§16) before the tester hub.

### §4.10 Tester Invite Settings

Settings:

- `relay/installerDownloadUrl` - string, default
  `github.com/[repo]/releases/latest`. This is the installer download URL
  included in invite emails. It is configurable so Darrin can update the
  distribution location without changing code.
- `relay/inviteCodesJson` - JSON blob storing all active invite codes with
  tester name, email, channel path mapping, `created_at`, and revoked flag.

## §5 File/Folder Structure and Metadata Schema

### §5.1 Local Folder Layout

Default local root:

```text
workflows/relay/
  sent/
    relay_20260427_143022_rebecca/
      audio.wav
      001.png
      transcript.md
      metadata.json
      status_updates/
  received/
    relay_20260427_143022_rebecca/
      audio.wav
      001.png
      transcript.md
      metadata.json
      status_updates/
```

Rules:

- Package folder names use `relay_YYYYMMDD_HHMMSS_[sender_slug]`.
- Screenshot filenames use zero-padded sequence numbers.
- `metadata.json` is required.
- `transcript.md` is required before send.
- `audio.wav` is required unless a future no-audio path is explicitly designed.
- `status_updates/` exists even when empty.

### §5.2 Dropbox Layout

Dropbox layout mirrors `workflows/relay/` under:

```text
/Panda Gallery Relay/[channel_name]/
  sent/
  received/
```

Recipient settings may store a full channel path. The sync layer maps local
sent/received direction appropriately for each install.

### §5.3 metadata.json Schema v1

Minimum schema:

```json
{
  "schema_version": 1,
  "relay_id": "relay_20260427_143022_rebecca",
  "sender_name": "Rebecca Chen",
  "recipient_name": "Darrin",
  "recorded_at": "2026-04-27T14:30:22-07:00",
  "sent_at": "2026-04-27T14:30:55-07:00",
  "received_at": null,
  "audio_duration_sec": 42,
  "screenshot_count": 3,
  "transcript_word_count": 89,
  "bugs_md_entry": null,
  "status": "sent"
}
```

Recommended `status` enum:

- `draft`
- `ready_to_send`
- `sent`
- `received`
- `acknowledged`
- `captured`
- `in_progress`
- `fixed`
- `wont_fix`
- `failed`

When BUGS.md capture succeeds, `bugs_md_entry` becomes:

```json
{
  "bug_id": 142,
  "title": "Single-click image viewer fails after patient switch",
  "captured_at": "2026-04-27T14:35:10-07:00",
  "bugs_md_path": "C:\\panda-gallery\\BUGS.md"
}
```

### §5.4 Status Update Schema v1

Ack/status updates live in `status_updates/`.

Acknowledgment example:

```json
{
  "schema_version": 1,
  "kind": "ack",
  "update_id": "ack_20260427_143100",
  "relay_id": "relay_20260427_143022_rebecca",
  "sender_name": "Darrin",
  "recipient_name": "Rebecca Chen",
  "status": "acknowledged",
  "message": "Received & acknowledged - Darrin received your report at 2:31 PM. A bug entry has been drafted and linked to your name.",
  "sent_at": "2026-04-27T14:31:00-07:00",
  "delivery_receipt": "queued"
}
```

Developer update example:

```json
{
  "schema_version": 1,
  "kind": "status_update",
  "update_id": "update_20260427_151500",
  "relay_id": "relay_20260427_143022_rebecca",
  "bug_id": 142,
  "sender_name": "Darrin",
  "recipient_name": "Rebecca Chen",
  "status": "in_progress",
  "message": "Root cause identified: Qt focus acquisition on Windows swallows the first click after switching patients.",
  "sent_at": "2026-04-27T15:15:00-07:00",
  "delivery_receipt": "queued"
}
```

Rules:

- Update IDs are immutable.
- Updates are append-only.
- UI sorts by `sent_at`.
- Duplicate update IDs are ignored unless content differs; content mismatch is a
  validation error.
- Delivery receipt states are defined in §13.

## §6 Relationship to Existing Modules

### §6.1 Remote Testing

Relay reuses Remote Testing's Dropbox transport/auth pattern but remains a
separate feature.

Remote Testing captures a test-session package and produces `test_report.md`.
Relay captures a bug-report communication package and produces `transcript.md`,
`metadata.json`, and status update JSON.

The v0.2 hub layout does not change the transport boundary: Remote Testing and
Relay may share Dropbox sync infrastructure, but their UI surfaces and package
lifecycles remain separate.

Required reuse:

- OAuth2 PKCE flow.
- QSettings token storage.
- Reconnect behavior.
- Retry/error taxonomy.
- Bounded backoff.
- No duplicate auth implementation.

### §6.2 BUGS.md

`BUGS.md` remains the single source of truth for bugs. Relay is an intake and
drafting surface, not a replacement.

`Capture to BUGS.md` must:

- Read the next available bug number from BUGS.md.
- Insert into `## OPEN`.
- Preserve BUGS.md's field conventions.
- Link back to Relay package artifacts.
- Preserve reporter identity.
- Avoid inventing uncertain expected/actual/fix-direction details.

### §6.3 Audit Module

Relay can open the captured bug in Audit Module when a bug ID exists. Relay
should not redesign AM Screen B.

### §6.4 Dropbox Sync Module

`dropbox_sync.py` should own OAuth2 PKCE flow, token storage, upload/download/list
operations, retry/error handling, and reconnect flow.

Relay should call this module through a small Relay-specific adapter rather than
embedding Dropbox SDK calls inside UI widgets.

Recommended public API extensions:

```python
class DropboxSync:
    def upload_relay_package(self, local_folder: Path, remote_channel: str) -> UploadResult: ...
    def upload_relay_update(self, update_path: Path, remote_channel: str, relay_id: str) -> UploadResult: ...
    def list_relay_inbox(self, remote_channel: str) -> list[RemoteRelayItem]: ...
    def download_relay_package(self, remote_item: RemoteRelayItem, local_root: Path) -> DownloadResult: ...
```

### §6.5 Settings/QSettings

Recommended keys:

```text
relay/localArchiveFolder
relay/autoAcknowledgeEnabled
relay/acknowledgmentText
relay/defaultStatusOnCapture
relay/primaryRecipientId
relay/recipientsJson
relay/lastSyncAt
relay/windowGeometry
relay/installRole
relay/duplicateSimilarityThreshold
relay/deliveryReceiptVerbosity
relay/templatesJson
relay/templateMostRecentlyUsedJson
relay/installerDownloadUrl
relay/inviteCodesJson
```

Dropbox token keys remain owned by `dropbox_sync.py`.

## §7 Open Questions

1. **Canonical spec path mismatch.** Specs currently live under
   `C:\CODEX PG\CODEX Canonical Specs\`. Continue using this canonical folder
   unless Darrin asks for a second alias path.

2. **Relay capture/transcription ownership.** Confirm whether Relay should reuse
   Workflow Capture's audio/screenshot/transcription machinery or implement a
   separate smaller capture manager. Default recommendation: share low-level
   capture/transcription utilities while keeping Relay package lifecycle separate.

3. **PHI/compliance boundary for remote screenshots.** Relay can transmit
   screenshots through Dropbox. If testers can capture real patient images or
   PHI-bearing UI, Relay needs a compliance/redaction rule before live use.

4. **Bug severity default.** BUGS.md requires Severity. Relay locks default
   status on capture but does not lock default severity. Recommended default:
   `Medium` with a developer-editable control in the capture card.

## §8 Hub Layout and Role Architecture

Relay uses the same window layout for developer and tester roles. The install
role determines content, tabs, and actions.

Developer configuration:

- Primary tab: All Reports.
- Secondary tabs: By Tester, Sent, Templates.
- Primary actions: review report, capture to BUGS.md, respond, duplicate review.

Tester configuration:

- Primary tab: My Reports.
- Secondary tabs: Updates, New Report.
- Primary actions: start report, review report status, read updates.

Role is configured in Relay Settings via `relay/installRole`. Switching roles
must be explicit and should warn if unsent drafts or local-only updates exist.

A tester-role install that has not completed setup (no stored Dropbox token and
no verified invite code) enters the §16 setup wizard on first launch rather than
the tester hub.

## §9 Developer Hub: All Reports View

Developer tab strip:

```text
All Reports · By Tester · Sent · Templates
```

All Reports shows a unified inbox across testers, newest first. The tab label
shows an unread badge when new reports have arrived.

The hub header includes a segmented view toggle:

- Unified: one chronological report list.
- Tester lanes: reports grouped by tester lane.

Left rail report rows include:

- tester avatar initials
- title
- unread dot when unread
- `DUPLICATE?` badge when similarity flag is active
- status badge
- timestamp
- short preview

Right panel anatomy:

- report header with title, tester, metadata strip, status, and duplicate badge
- developer workflow stepper
- status pane that names the exact next button
- duplicate banner when flagged
- evidence block with screenshot filmstrip and transcript/audio preview
- capture card with BUGS.md draft and `Capture to BUGS.md`
- compose/status update area or `Send update` entry point
- footer/statusbar with Dropbox sync state

Sent shows developer-authored acknowledgments and status updates. Templates opens
the template manager described in §12.

## §10 Duplicate Detection and Resolution

Relay supports AI-assisted and manual duplicate handling.

AI-assisted detection:

- Compares transcript text, screenshot similarity, and timing.
- Uses configurable threshold `relay/duplicateSimilarityThreshold`.
- Default threshold: 80%.
- When threshold is met, shows `DUPLICATE? [N]% match` on the row and an inline
  banner in the detail panel.
- Darrin confirms or dismisses the match.

Manual duplicate handling:

- Right-click any report.
- Choose `Mark as duplicate of...`.
- Pick the primary report.
- Available regardless of AI flagging.

Primary report selection:

- First received is the default primary.
- Darrin can override with `Set as primary`.
- Primary status changes drive linked-reporter notifications.

Cross-tester duplicates:

- Preserve every reporter.
- Use the cross-tester Duplicate template by default.
- All linked reporters are notified on any status change.

Same-tester duplicates:

- Preserve both submissions unless Darrin explicitly archives one.
- Use the same-tester Duplicate template by default.
- Language stays gentle and non-punitive.

Duplicate language rule:

- Always use "Duplicate".
- Never use "dupe".

## §11 Message Compose and Status Updates

Compose order:

1. Darrin selects status: Acknowledged, In Progress, Fixed, or Won't Fix.
2. Relay auto-fills the default template for that status.
3. Darrin may switch template from `Use template`.
4. Darrin may choose `Write custom` for freeform text.
5. Darrin previews the final message.
6. Darrin sends to all linked reporters.

Status selection is first because it determines template, wording, and package
status.

Template override:

- `Use template` shows templates associated with the selected status.
- If multiple templates exist, most recently used for that status is preselected.
- `Write custom` clears the field for freeform entry.

Preview:

- Shows exactly what each recipient will see after placeholder substitution.
- Must surface missing placeholder fallbacks before send.

Send scope:

- For non-duplicate reports, send to the reporter.
- For duplicate groups, send to all linked reporters.
- Linked reporters are notified on every status change.

## §12 Template System

Relay ships six default templates. All are editable and resettable to default.

| Template name | Status | Default text |
| --- | --- | --- |
| Acknowledged | Acknowledged | `Hi [tester name], thanks for sending this in. We've received your report on [bug title] and it's been logged. We'll keep you posted as we work through it. - [developer name]` |
| In Progress | In Progress | `Hi [tester name], we're actively working on [bug title]. We'll update you when there's progress. - [developer name]` |
| Fixed | Fixed | `Hi [tester name], [bug title] has been fixed and will be included in the next update (v[version]). Thank you for reporting it. - [developer name]` |
| Won't Fix | Won't Fix | `Hi [tester name], after reviewing [bug title] we've decided not to fix this in the current version. Thank you for taking the time to report it. - [developer name]` |
| Duplicate (cross-tester) | Acknowledged | `Hi [tester name], thank you for sending this in. Your report matches one we've already received from another tester. We're tracking this issue and will keep you posted. - [developer name]` |
| Duplicate (same tester) | Acknowledged | `Hi [tester name], it looks like this report may have been submitted twice. We've linked them together so nothing is lost - no action needed on your end. - [developer name]` |

Supported placeholders:

- `[tester name]`
- `[bug title]`
- `[developer name]`
- `[bug id]`
- `[version]`
- `[date]`
- `[relay id]`

Rules:

- Unlimited custom templates are allowed.
- Multiple templates per status are allowed.
- Templates are global, not per-tester.
- Most recently used template for each status is preselected at compose time.
- Missing placeholders must not be sent literally. Relay either substitutes a
  safe fallback or omits the sentence fragment.

## §13 Dropbox Sync Status and Delivery Receipts

Dropbox behavior is grounded in verified applet results from
`scripts/dropbox_integration_test.py`: 15/15 PASS, app key `gyudg4ri3pcay3b`,
PKCE offline token, and SDK `dropbox>=12.0.2`.

Sync statusbar is always visible.

Sync states:

- Connected: green dot and last sync text.
- Syncing: peach animated state.
- Waiting to retry: amber state with countdown and `Retry now`.
- Disconnected: red state with `Reconnect`.

Warning/error banner:

- Appears automatically on warning or error.
- Auto-dismisses when sync recovers.
- No user preference is needed for this banner.

Delivery receipt states:

```text
Queued -> Uploading -> Delivered
Queued -> Uploading -> Failed
```

Failed messages show `Retry now`.

Sent tab verbosity:

- Full detail: show all delivery receipt transitions on every sent message.
- Failures only: hide successful deliveries and surface failed messages.
- Off: hide per-message receipts; global sync statusbar remains.

Default: Failures only.

Verified implementation requirements:

- Use `DropboxOAuth2FlowNoRedirect`.
- Set `use_pkce=True`.
- Set `token_access_type='offline'`.
- No app secret.
- Store refresh token through QSettings in production.
- Use `files_upload()` with `WriteMode.overwrite` for files under 150 MB.
- Handle HTTP 429 with `Retry-After` and bounded exponential backoff.
- Treat `dropbox.exceptions.ApiError` as clean bad-path/permission failure.
- Treat connection/network failures as retry state, not crash state.
- Require Dropbox SDK `>= 12.0.2`.
- Mirror Relay packages under `/Panda Gallery Relay/[channel_name]/`.

## §14 Tester Hub View

Tester tab strip:

```text
My Reports · Updates (N) · New Report
```

My Reports:

- Primary tester tab.
- Shows tester's own sent reports.
- Each row shows title, current status badge, sent date, delivery confirmation,
  screenshot/audio count, and unread/update indicator when relevant.
- Selecting a report opens the detail panel.

Status badges:

- Acknowledged: muted.
- In Progress: amber.
- Fixed: green.
- Won't Fix: dim.
- Pending: peach.

Updates:

- Shows all status updates received from the developer, newest first.
- Tab label shows unread badge.
- Rows show related bug title, status change, message preview, and timestamp.
- Reading an update marks it read and clears the badge count as appropriate.

Report detail:

- Header with title, status badge, and metadata.
- Tester workflow stepper.
- Evidence block with screenshots and transcript preview.
- Update timeline, newest last.

New Report:

- Launches Screen 1 Active Capture.

## §15 Workflow Steppers

Both role steppers use the same visual grammar as AM Screen B:

- numbered circles
- connecting arrows `━━▶`
- peach active step
- green completed step with `✓`
- grey pending step

Status pane copy rule: every idle message names the exact button label verbatim.

### Developer Stepper

Per selected report:

```text
① Received ━━▶ ② Review ━━▶ ③ Capture (optional) ━━▶ ④ Respond
```

Rules:

- Step 1 completes automatically when the report arrives.
- Step 2 is active when a report is selected.
- Step 3 is optional and non-blocking.
- Step 4 is non-blocking.
- Steps 3 and 4 can be completed in any order.
- When no report is selected, show: `Select a report from the list to begin.`

Developer status pane examples:

| State | Status pane message |
| --- | --- |
| Step 2 | `Report received. Review transcript and screenshots, then click ✦ Capture to BUGS.md.` |
| Step 3 pending | `Ready to capture. Click ✦ Capture to BUGS.md to log this bug.` |
| Step 4 pending | `Ready to respond. Click ✦ Send update to notify the tester.` |
| Duplicate flagged | `Possible Duplicate detected. Click Review match › to compare reports.` |

### Tester Stepper

Per active report:

```text
① Record ━━▶ ② Review ━━▶ ③ Send ━━▶ ④ Track
```

Rules:

- Fully sequential.
- Tester cannot skip steps.
- Step 4 activates after send and shows incoming status updates.

Tester status pane examples:

| State | Status pane message |
| --- | --- |
| Step 3 | `Ready to send. Click ✦ Send to [developer name] to deliver your report.` |
| Step 4 | `Report delivered. Updates from [developer name] will appear here.` |

## §16 Tester Setup Flow

### §16.1 Overview

The tester setup flow is a standalone 3-step wizard window, not the full PG app
shell. It runs once on first Relay use by a tester-role install.

Wizard steps:

```text
Connect Dropbox → Enter invite code → Say hello
```

The setup wizard exists to get a non-technical tester connected to Darrin's Relay
channel without exposing paths, tokens, transport mechanics, or settings.

### §16.2 Prerequisites

The tester requires a Dropbox account only. The Dropbox desktop app is not
required.

Authentication uses the same PKCE flow as Remote Testing:

- `DropboxOAuth2FlowNoRedirect`
- `use_pkce=True`
- `token_access_type='offline'`
- no app secret

The browser opens for Dropbox authorization. The user signs in, clicks Allow,
and pastes the authorization code back into PG. This is step 1 of the wizard.

### §16.3 Invite Code System

Darrin generates an invite code for each tester in Relay Settings.

| Field | Value |
| --- | --- |
| Prefix | `PG-` |
| Body | 2 uppercase letters + 2 digits |
| Length | 7 characters including prefix |
| Case | Always uppercase; no case sensitivity |
| Excluded characters | O, I (letters) and 0, 1 (digits) |
| Charset | A-Z minus O and I; digits 2-9 |
| Keyspace | 24² × 8² = 36,864 combinations |
| Example | `PG-X4K9` |

Codes are permanent until Darrin explicitly revokes them. Permanent codes allow
Rebecca to reconnect after reinstalling PG without requesting a new code from
Darrin.

Darrin can revoke any code from the Testers section of Relay Settings.

PG decodes the channel path from the code internally. The tester never sees or
types a Dropbox folder path.

### §16.4 Invite Delivery

Darrin invites a tester by entering their name and email address in Relay
Settings -> Invite a tester.

PG generates the invite code and opens Darrin's default email client via a
`mailto:` link using Python `webbrowser.open("mailto:...")`. The To, Subject,
and body fields are pre-filled.

Darrin reviews the pre-filled email and hits Send. No copy-paste is required in
the normal path.

The pre-filled email body includes:

1. The installer download URL. This is configurable in Relay Settings and
   defaults to `github.com/[repo]/releases/latest`.
2. The invite code rendered prominently.
3. The instruction: "Open Relay and enter your code. PG will walk you through
   the rest."

If no default email client is configured, a clipboard fallback button copies the
full invite text so Darrin can paste it anywhere.

Installer download URL setting:

- Key: `relay/installerDownloadUrl`
- Default: `github.com/[repo]/releases/latest`
- Purpose: included in invite emails. Darrin updates this once if distribution
  moves, and all future invites use the new URL automatically.

### §16.5 Auto-Verification (Step 2)

When Rebecca finishes typing her invite code, PG auto-tests the connection
immediately. There is no "Test connection" button.

Two checks run in sequence and are invisible to Rebecca:

1. PG decodes the channel path from the code. This fails if the code is invalid
   or revoked.
2. PG verifies Rebecca's Dropbox token can write to that channel path. This
   fails if Dropbox authorization did not complete successfully.

Rebecca sees only success or a specific red/amber failure message. She never
sees the channel path or the internal two-check sequence.

### §16.6 End-to-End Confirmation (Step 3)

On code verification success, PG automatically sends a visible test report to
Darrin's Relay inbox labelled "Relay setup test."

If `relay/autoAcknowledgeEnabled` is true (default), Darrin's PG instance
automatically sends an acknowledgment back to Rebecca.

Rebecca's wizard shows a waiting state:

```text
Waiting for Darrin to confirm…
```

On receipt of the acknowledgment, Rebecca sees:

```text
Darrin got it — you're all set!
```

Expected time is under 10 seconds when Darrin has PG running. If PG is closed,
the acknowledgment fires on next PG launch.

If acknowledgment is not received within 60 seconds, Rebecca sees the amber
warning state in §16.7 and is directed to ask Darrin to open PG.

### §16.7 Error Messages

Each failure state has a specific plain-English message and exactly one next
step. Relay must not show generic "something went wrong" messages.

| Failure | Message | One next step |
| --- | --- | --- |
| Dropbox auth failed | "Dropbox didn't authorise PG" | Click "Open Dropbox in browser" again and make sure you click Allow on the Dropbox page |
| Wrong or revoked code | "Code not recognised" | Double-check the code Darrin sent. Ask Darrin to resend it if needed |
| No internet | "No internet connection" | Connect to wifi and try again |
| Ack not received (60s timeout) | "Darrin hasn't confirmed yet" (amber, not red) | Ask Darrin to open Panda Gallery and check his Relay inbox |

### §16.8 Wizard Presentation

The wizard presents one step at a time. Each step receives a full setup screen.
The flow has three setup steps total:

1. Connect Dropbox.
2. Enter invite code.
3. Say hello.

A wizard progress bar at the top shows all three steps with connectors:

- Active step: peach circle.
- Complete step: green `✓`.
- Pending step: muted circle.

The standalone wizard window has:

- PG title bar with brand mark and `Relay Setup`.
- Wizard content.
- Statusbar.

The setup wizard must not show module tabs, tool strip, filmstrip, right panel,
or the full PG app shell.

### §16.9 Final Screen

After successful connection, the wizard shows a completion screen with:

- Large green checkmark.
- `You're all set!`
- `Darrin got your hello. You're connected.`
- A `WHEN YOU FIND A BUG` section showing exactly three plain steps:
  1. Open Relay and tap the New Report tab.
  2. Record what you saw — just speak naturally.
  3. Tap Send to Darrin — done.
- Primary button: `Open Relay →`

These three steps are shown once only on this final screen. They do not repeat.

### §16.10 Layered UX Principle

All Relay surfaces follow a two-layer UX architecture.

Surface layer (tester/default view):

- Fully automatic.
- Zero decisions.
- Zero jargon.
- Every step happens without the user choosing anything technical.
- Errors are plain English with one next step.

Hidden layer (Darrin's diagnostics):

- Lives behind an `Advanced diagnostics` collapsible in Relay Settings.
- Includes raw Dropbox sync log, token status, channel path, SDK version,
  force re-test, and manual retry.
- Present but invisible unless needed.

This principle applies across all of Relay, not just setup. Every Relay screen
defaults to the simplest possible surface. Troubleshooting tools exist but are
disclosed progressively.
