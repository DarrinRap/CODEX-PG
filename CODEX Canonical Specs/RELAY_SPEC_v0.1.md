# Relay Specification v0.1

Date: 2026-04-28
Author: Codex
Status: Spec only. No Panda Gallery runtime code changed.

Canonical visual reference:

- `C:\panda-gallery\workflows\design\pg_general_mockups\relay_module_v1.html`

Sources read:

- `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\20260427_CLAUDE_to_CODEX_relay_spec_v0_1.md`
- `C:\panda-gallery\workflows\design\pg_general_mockups\relay_module_v1.html`
- `C:\panda-gallery\BUGS.md`
- `C:\panda-gallery\PANDA_GALLERY_REMOTE_TESTING_SPEC_draft4.md`
- `C:\panda-gallery\STRATEGY_NOTES.md`
- `C:\CODEX PG\CODEX Canonical Specs\CODEX_AM_v0_2_POLISH_SPEC_v1.md`

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

### Design Philosophy

Relay inherits the 2026-04-27 PG design posture from `STRATEGY_NOTES.md`:
make values configurable, not hard-coded, when they could reasonably vary per
user, practice, or workflow.

Applied to Relay:

- Recipient names are settings, not constants.
- Dropbox recipient folder paths are settings, not constants.
- A primary/default recipient is a setting, not a hardcoded "Darrin".
- Auto-acknowledgment is a setting with a sensible default.
- Acknowledgment copy is editable.
- Default capture status is editable.
- Local archive location is editable.

This principle does not mean "settings for everything." Relay keeps true data
integrity rules hard: package schema versioning, immutable relay IDs, required
metadata fields, and BUGS.md capture format must be deterministic.

### In Scope

- Tester capture, review, send, sent history, and inbox views.
- Developer inbox, one-click BUGS.md capture, and send-update flow.
- Relay Settings surface.
- Local package layout and Dropbox mirror layout.
- Metadata schema v1.
- Relationship to Remote Testing, BUGS.md, and Audit Module.
- Behavior of auto-ack and status updates.

### Out of Scope for v0.1

- Implementing runtime Python/PyQt code.
- Replacing Remote Testing.
- Real-time chat, comments, or presence.
- A hosted relay server.
- Fully automatic BUGS.md writes with no developer click.
- New Dropbox authentication design.
- New Audit Module behavior beyond linking captured bug IDs.
- Clinical/compliance policy for PHI-bearing screenshots.

## §2 Locked Decisions

### D1 - Name

The module name is **Relay**.

This name is locked over Field Reports, Collaboration, and Collaborator.
Rationale: it is short, bidirectional, and neutral. It works from both tester and
developer viewpoints without implying that one side is the permanent sender or
receiver.

UI usage:

- Window title: `Panda Gallery - Relay`.
- Module label: `Relay`.
- Statusbar prefix: `Relay`.
- Package IDs use `relay_...`.

### D2 - Configurable Recipients, Not Hardcoded Recipients

Each PG install configures one or more named recipients in Relay Settings.
A recipient record includes:

- Display name.
- Dropbox folder path or channel path.
- Optional role label such as Developer, Tester, QA, or Other.
- Primary/default flag.

The send UI uses the primary configured recipient:

- Button label pattern: `Send to [configured recipient]`.
- If no recipient is configured, the primary action is disabled and points the
  user to Relay Settings.

The visual mockup shows `Send to Darrin` because that is the configured primary
recipient in the reference scenario, not because the string is hardcoded.

### D3 - Semi-Automatic BUGS.md Capture

When a developer receives a bug report, Relay auto-generates a draft BUGS.md
entry from the transcript and package metadata. The developer sees the draft in
a `Capture to BUGS.md` card and clicks one button to commit it.

Relay must not write directly to BUGS.md without this developer action.

Rationale:

- Fully automatic capture risks low-quality or misleading bug entries from
  unclear transcripts.
- Fully manual capture repeats information Relay already has.
- One-click capture preserves developer control while removing mechanical work.

The capture card contains:

- Auto-drafted title.
- Reporter name.
- Relay ID.
- Linked transcript/audio/screenshots.
- Proposed BUGS.md fields.
- Primary button: `Capture to BUGS.md`.

After capture, the card transforms to show:

- Captured bug ID.
- Status pill.
- Link/open affordance for the BUGS.md entry.

### D4 - Separate Tester Inbox Tab

The tester's Relay window has two tabs:

- Inbox.
- Sent.

Status updates from the developer arrive as new Inbox rows. They are not hidden
inside the original sent report row. The selected sent report can still show the
acknowledgment and update timeline, but unread/new status updates must surface
in Inbox so they are not missed.

The mockup's post-send state shows:

- Inbox with unread count badge.
- Sent tab active after send.
- Selected sent report with a green unread/update indicator.
- Right panel timeline containing acknowledgment and status update cards.

### D5 - Dropbox Transport

Relay uses Dropbox as the sync transport. It reuses and extends the OAuth2 PKCE
flow pattern from Remote Testing Phase 4 and `dropbox_sync.py`.

Relay must not introduce a new authentication approach.

Required carryover from the Remote Testing spec:

- Dropbox OAuth2 PKCE flow uses an app key, not an app secret.
- Token storage belongs to the Dropbox sync/auth module and persists through
  QSettings.
- Auth failures surface a reconnect flow.
- Dropbox error handling dispatches by exception class rather than a generic
  failure bool.
- Retryable network/server failures use bounded exponential backoff.
- Bad input and non-retryable API errors fail fast with clear UI feedback.

Relay-specific extension:

- `dropbox_sync.py` should gain Relay package upload/download/list helpers
  rather than duplicating auth, token, retry, or reconnect code.
- Relay Settings stores recipient/channel folder paths that are passed into
  the Dropbox layer.

### D6 - Auto-Acknowledgment

On the developer side, receipt of a report triggers an automatic acknowledgment
back to the tester's Relay Inbox when auto-acknowledge is enabled.

Default: on.

Default acknowledgment text:

```text
Received & acknowledged - [developer name] received your report at [time]. A bug entry has been created and linked to your name.
```

Implementation note:

- The acknowledgment may be represented as a status update package with
  `kind: "ack"` and `status: "acknowledged"`.
- The developer UI should also show a local system row/tag so Darrin can see
  that the ack was sent.
- The ack should be created only after the inbound package has been persisted
  locally and the BUGS.md draft card can be generated.

### D7 - Status Update Flow

Status updates are developer-initiated.

Status options:

- Acknowledged.
- In Progress.
- Fixed.
- Won't Fix.

Each update optionally includes freeform text. Each update routes through Dropbox
to the tester's Relay Inbox as a new message row and also appears in the selected
sent-report timeline.

Developer update packages include:

- Relay ID.
- Optional linked bug ID.
- Status value.
- Message text.
- Sender name.
- Sent timestamp.

The tester sees updates in chronological order, newest last in the selected
report timeline, while the Inbox list surfaces the latest unread update first.

### D8 - General Configurability

When a value could vary per user, practice, or workflow, it is a setting with a
sensible default, not a constant.

Relay settings must cover:

- Recipients.
- Auto-acknowledge.
- Acknowledgment text.
- Default status on capture.
- Dropbox connection.
- Local archive folder.

Constants remain appropriate for schema field names, package versioning, and
required storage filenames.

## §3 Screen Anatomy

The mockup at `relay_module_v1.html` is the visual truth for layout, hierarchy,
and visual tone. This prose describes behavior and required data/state.

### §3.1 Screen 1 - Tester: Active Capture

Purpose: let the tester record a spoken bug report while collecting screenshots.

State:

- Recording is active.
- Timer is running.
- Audio level/waveform is live.
- Screenshot thumbnails accumulate.

Header:

- Window title reads `Panda Gallery - Relay`.
- Module title reads `Relay`.
- A gear/settings control is available in the screen header.

Main content:

- Intro/help copy explains that the tester should describe expected vs actual
  behavior and capture relevant screen states.
- Recording card shows:
  - `Recording`.
  - Elapsed time such as `0:42`.
  - Live red-dot/live indicator.
  - Waveform or live level bar.

Screenshot area:

- Shows count such as `3 captured`.
- Shows thumbnail tiles named `001.png`, `002.png`, `003.png`.
- Includes manual capture button.
- Supports an auto-capture option in settings or an adjacent affordance.

Actions:

- Primary: `Stop & Process`.
- Secondary/destructive: `Discard`.
- Keyboard shortcut: `Ctrl+Shift+S` stops recording and proceeds to processing.

Statusbar:

- `Relay`.
- `Recording - 0:42`.
- Current package folder name such as `relay_20260427_143022_rebecca/`.

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

State:

- Recording has stopped.
- Transcript exists.
- Package is not yet sent.

Header:

- Title: `Panda Gallery - Relay - Review`.
- Subtitle/package ID: e.g. `relay_20260427_143022_rebecca`.
- Header action: `Play audio`.

Transcript card:

- Displays transcript in a readable block.
- Shows timestamp cues such as `[0:08]`.
- Includes `Edit` affordance.
- `Edit` opens inline editable transcript text.
- Saving edits updates `transcript.md` and `metadata.json.transcript_word_count`.

Screenshot grid:

- Read-only thumbnails.
- Count label such as `3 attached`.
- Clicking a thumbnail opens the full image preview.

Action bar:

- Primary: `Send to [configured recipient]`.
- Secondary: `Edit transcript`.
- Secondary: `Play audio`.
- Destructive: `Discard`, right-aligned.

Statusbar:

- `Ready to send`.
- `Dropbox - connected`.

Behavior:

1. Send button is disabled if no primary recipient is configured.
2. Send packages the current audio, screenshots, transcript, and metadata.
3. Send writes/updates local archive state to `status: "sent"`.
4. Send uploads/mirrors the package to the configured Dropbox channel path.
5. After successful send, the UI navigates to Screen 3 with Sent selected.
6. If Dropbox upload fails, package remains local with a retry state.

### §3.3 Screen 3 - Tester: Sent + Inbox

Purpose: let the tester review sent reports and receive acknowledgments/status
updates from the developer.

Tabs:

- Inbox with unread badge.
- Sent.

Default after send:

- Sent tab active.
- Newly sent report selected.

Left rail:

- List of sent items.
- Each row shows:
  - Status label such as `SENT`.
  - Date/time.
  - Auto-generated or edited title.
  - Transcript preview.
  - Unread/update dot when new developer messages exist.

Right panel selected sent item:

- Report title.
- Sent timestamp.
- Recipient name.
- Attachment summary such as `3 screenshots - 0:42 audio`.
- Timeline section labeled Updates.
- Auto-ack confirmation card with green left border.
- Status update cards below the acknowledgment, newest last.
- Original transcript collapsed or shown below updates.

Inbox behavior:

- Developer ack and status update packages appear as Inbox rows.
- Opening an update marks that update read.
- The selected original sent item can still show the full timeline.

Statusbar:

- Connected channel name, e.g. `Connected to Darrin's channel`.
- Dropbox sync timestamp, e.g. `Dropbox - synced 3:15 PM`.

### §3.4 Screen 4 - Developer: Inbox

Purpose: let the developer triage incoming reports, capture a BUGS.md entry, and
send status updates back.

Tabs:

- Inbox active with new count badge.
- Sent.

Left rail:

- Incoming rows tagged:
  - `BUG REPORT`.
  - `ACK` for system acknowledgment records.
  - `STATUS` for status updates.
- Each row shows sender, date/time, and short preview.

Right panel for selected BUG REPORT:

- Report title.
- Reporter name.
- Received timestamp.
- Attachment summary.
- Full transcript block.
- Screenshots grid; thumbnails open full-size preview.
- `Capture to BUGS.md` card.
- Action bar.

Capture to BUGS.md card:

- Shows state `DRAFT` before capture.
- Shows auto-drafted bug title.
- Primary action: `Capture to BUGS.md`.
- After capture, transforms to show:
  - Bug ID.
  - Status pill.
  - Link/open affordance for BUGS.md.

BUGS.md capture format:

- Use the next available bug number from `BUGS.md`.
- Add to the `## OPEN` section.
- Preserve BUGS.md conventions:
  - `### #[number] - [title]`
  - `**Status:** Open - surfaced [date] via Relay from [reporter]`
  - `**Severity:** [default or developer-selected severity]`
  - `**Files:** [affected files if known, otherwise Relay package links]`
  - `**Reproduce:**`
  - `**Expected:**`
  - `**Actual:**`
  - `**Fix direction:**`
  - `**Notes:**`
  - `**Relates:**`

Drafting rules:

- Do not invent facts not supported by transcript or metadata.
- If expected/actual cannot be separated confidently, mark the field as
  `Needs developer review`.
- Always include Relay ID and local package path in Notes.
- Always link transcript, audio, and screenshots in Notes or Files.
- Reporter name must be preserved.

Action bar:

- `Open in Audit Module`.
- `Play audio`.
- `Send update to [tester]`.

Statusbar:

- `Auto-ack sent - [time]`.
- Dropbox sync state.

Behavior:

1. New report is mirrored from Dropbox into `workflows/relay/received/`.
2. Relay validates `metadata.json`.
3. Relay generates a local draft BUGS.md entry.
4. Relay sends auto-ack if enabled.
5. Developer clicks `Capture to BUGS.md` to commit the entry.
6. Capture updates `metadata.json.bugs_md_entry` and package status.
7. `Open in Audit Module` opens AM Screen B or the relevant AM bug detail once
   a bug ID exists.

### §3.5 Screen 5 - Developer: Send Update

Purpose: send a developer-authored status update back to the tester.

Entry point:

- Screen 4 action bar: `Send update to [tester]`.

Header:

- `Panda Gallery - Relay - Send Update`.
- Destination line: `to [tester name] - Bug #[id]`.
- Cancel action.

Bug context card:

- Read-only bug ID.
- Bug title.
- Current status pill.

Status picker:

- Segmented row:
  - Acknowledged.
  - In Progress.
  - Fixed.
  - Won't Fix.
- Active state highlighted in peach per visual mockup.

Message card:

- Optional freeform text field.
- Empty message is allowed, but status must be selected.

Action bar:

- Primary: `Send update`.

Statusbar:

- `Via Dropbox - [tester name] will see this in their Relay inbox`.
- `Dropbox - connected`.

Behavior:

1. Developer selects status and optional text.
2. Relay writes update JSON into the source report's `status_updates/`.
3. Relay uploads/mirrors the update to the tester channel.
4. Developer Sent view records the update.
5. Tester Inbox receives a new unread row.

## §4 Relay Settings

Relay Settings are accessible from the gear icon in the Relay screen header.
Settings should use progressive disclosure: common operational settings first,
technical connection details second.

### §4.1 Recipients

Recipients are configured contacts.

Fields:

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

Validation:

- Name required.
- Dropbox path required.
- Only one primary recipient.
- If the primary recipient is removed, user must select a new primary before
  sending is enabled.

### §4.2 Auto-Acknowledge

Setting:

- `relay/autoAcknowledgeEnabled`

Default:

- On.

Behavior:

- When enabled, receipt of any valid BUG REPORT package triggers an ack update.
- When disabled, no automatic ack is sent; developer can manually send an
  Acknowledged status update.

### §4.3 Acknowledgment Text

Setting:

- `relay/acknowledgmentText`

Default:

```text
Received & acknowledged - [developer name] received your report at [time]. A bug entry has been created and linked to your name.
```

Supported placeholders:

- `[developer name]`
- `[tester name]`
- `[time]`
- `[relay id]`
- `[bug id]` when available

If a placeholder is unavailable, Relay should either omit the sentence fragment
or show a safe fallback. It must not send raw placeholder text to the tester.

### §4.4 Default Status on Capture

Setting:

- `relay/defaultStatusOnCapture`

Default:

- `OPEN`

This controls the status written when `Capture to BUGS.md` is clicked.

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

Setting:

- `relay/localArchiveFolder`

Default:

- `workflows/relay/`

The archive folder contains both sent and received packages. User may change it,
but Relay must validate that the path is writable and must not silently migrate
existing packages without confirmation.

## §5 File/Folder Structure and Metadata Schema

### §5.1 Local Folder Layout

Default local root:

```text
workflows/relay/
  sent/
    relay_20260427_143022_rebecca/
      audio.wav
      001.png
      002.png
      003.png
      transcript.md
      metadata.json
      status_updates/
        ack_20260427_143100.json
        update_20260427_151500.json
  received/
    relay_20260427_143022_rebecca/
      audio.wav
      001.png
      002.png
      003.png
      transcript.md
      metadata.json
      status_updates/
        ack_20260427_143100.json
        update_20260427_151500.json
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

Recipient settings may store a full channel path. The default convention is:

```text
/Panda Gallery Relay/[configured_channel_name]/
```

The sync layer maps local sent/received direction appropriately for each install.
For example, Rebecca's local `sent/relay_...` appears as an incoming package in
Darrin's received view after sync.

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

Field requirements:

- `schema_version`: integer, required, current value `1`.
- `relay_id`: string, required, immutable.
- `sender_name`: string, required.
- `recipient_name`: string, required.
- `recorded_at`: ISO-8601 string, required.
- `sent_at`: ISO-8601 string or null until sent.
- `received_at`: ISO-8601 string or null until received.
- `audio_duration_sec`: integer or float, required.
- `screenshot_count`: integer, required.
- `transcript_word_count`: integer, required after transcript exists.
- `bugs_md_entry`: object or null.
- `status`: enum.

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
  "message": "Received & acknowledged - Darrin received your report at 2:31 PM. A bug entry has been created and linked to your name.",
  "sent_at": "2026-04-27T14:31:00-07:00"
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
  "sent_at": "2026-04-27T15:15:00-07:00"
}
```

Rules:

- Update IDs are immutable.
- Updates are append-only.
- UI sorts by `sent_at`.
- Duplicate update IDs are ignored unless content differs; content mismatch is a
  validation error.

## §6 Relationship to Existing Modules

### §6.1 Remote Testing

Relay reuses Remote Testing's Dropbox transport/auth pattern but remains a
separate feature.

Remote Testing:

- Captures a test-session package.
- Uploads a workflow/testing session.
- Produces `test_report.md`.
- Uses `dropbox_sync.py` for OAuth/upload/retry.

Relay:

- Captures a bug-report communication package.
- Sends bidirectional messages and status updates.
- Produces `transcript.md`, `metadata.json`, and status update JSON.
- Extends the same Dropbox sync/auth module.

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

After capture:

- Relay stores bug ID in `metadata.json.bugs_md_entry`.
- Developer view shows captured state.
- `Open in Audit Module` can target the captured bug ID.

### §6.3 Audit Module

Screen 4 includes `Open in Audit Module`.

For v0.1, no AM changes are required beyond opening/linking by bug ID if that
route already exists or is added later. Relay should not redesign AM Screen B.

Expected relationship:

- Relay captures a BUGS.md entry.
- AM can triage that entry.
- Relay package path remains supporting evidence.

### §6.4 Dropbox Sync Module

`dropbox_sync.py` should own:

- OAuth2 PKCE flow.
- Token storage.
- Upload/download/list operations.
- Retry/error handling.
- Reconnect flow.

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

Relay should store user-facing configuration in QSettings using stable keys.

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
```

Dropbox token keys remain owned by `dropbox_sync.py`.

## §7 Open Questions

These are the only items I found that still need Darrin or Claude direction
before implementation. They do not block the v0.1 spec.

1. **Canonical spec path mismatch.**
   Claude's mailbox task requested
   `C:\CODEX PG\Canonical Specs\RELAY_SPEC_v0.1.md`, but the repo's existing
   canonical spec directory is `C:\CODEX PG\CODEX Canonical Specs\`. This spec
   uses the existing repo folder to avoid creating a second canonical-specs
   location. Confirm whether an alias/copy at `C:\CODEX PG\Canonical Specs\`
   is desired.

2. **Auto-ack wording vs semi-automatic BUGS.md capture.**
   D6's default acknowledgment says a bug entry "has been created," while D3
   says BUGS.md capture is semi-automatic and requires a developer click. This
   spec preserves the locked D6 text, but implementation should clarify whether
   "created" means "drafted in Relay" or "committed to BUGS.md." I recommend
   changing the default text to "A bug entry has been drafted and linked to your
   name" unless Darrin explicitly wants the current wording.

3. **Relay capture/transcription ownership.**
   The mockup assumes audio recording, screenshots, and transcript generation.
   Confirm whether Relay should reuse Workflow Capture's audio/screenshot/
   transcription machinery or implement a separate smaller capture manager.
   I recommend sharing low-level capture/transcription utilities while keeping
   Relay package lifecycle separate from Remote Testing sessions.

4. **PHI/compliance boundary for remote screenshots.**
   Relay can transmit screenshots through Dropbox. If testers can capture real
   patient images or PHI-bearing UI, Relay needs a compliance/redaction rule
   before live use. I recommend treating Relay as development/test-only until a
   PHI policy is explicitly written.

5. **Bug severity default.**
   BUGS.md requires Severity. The Relay brief locks default status on capture
   but does not lock default severity. I recommend defaulting to `Medium` with
   a developer-editable control in the capture card.

