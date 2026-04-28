# CLAUDE → CODEX: Author RELAY_SPEC_v0.1.md

**Message-ID:** CLAUDE-20260427-181500-relay-spec
**Reply-To:** C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\
**Date:** 2026-04-27
**From:** Desktop Claude
**To:** Codex
**Priority tier:** High
**Reason for tier:** Scoped spec authoring from a complete design session. All decisions locked. No architecture invention required — transcribe, structure, and fill out the spec from the material provided.

---

## Task

Author `RELAY_SPEC_v0.1.md` — the initial specification for the Relay module in Panda Gallery.

Write it to: `C:\CODEX PG\Canonical Specs\RELAY_SPEC_v0.1.md`

---

## What Relay is

Relay is a two-sided asynchronous communication module built into PG. It lets a remote tester (Rebecca) record audio descriptions of bugs she finds, attach screenshots, review the transcript, and send the package to the developer (Darrin). On the developer's side, Relay receives the report, auto-acknowledges receipt, auto-drafts a BUGS.md entry for one-click capture, and provides a status update channel back to the tester.

Dropbox is the sync transport layer between the two installs. No self-hosted server. No real-time connection required.

---

## Locked decisions — bake all of these into the spec

**D1 — Name:** The module is called **Relay**. This name was chosen over: Field Reports, Collaboration, Collaborator. Rationale: one syllable, two-directional, works for both sender and receiver without implying a single-direction role.

**D2 — Configurable recipients (not hardcoded):** Each PG install configures one or more named recipients in Relay Settings (name + Dropbox folder path). The default recipient shown in the send UI is the primary configured contact — not a hardcoded string. This flows from the general PG design philosophy: prefer configurability over hard-coding (STRATEGY_NOTES.md 2026-04-27).

**D3 — Semi-automatic BUGS.md capture:** On the developer's side, when a report arrives, Relay auto-generates a draft bug entry from the transcript (auto-parsed title, description, reporter name, attachments linked). The developer sees the draft in a "Capture to BUGS.md" card and clicks one button to commit it. Fully automatic risks garbage entries from unclear transcripts; fully manual is unnecessary friction.

**D4 — Separate Inbox tab for tester:** The tester's Relay window has two tabs: Sent and Inbox. Status updates from the developer arrive in Inbox as new message rows, not collapsed inline on the sent item. This scales cleanly when multiple updates arrive on the same report over time.

**D5 — Dropbox transport:** Same OAuth2 PKCE flow pattern as the Remote Testing spec Phase 4 (`dropbox_sync.py`). No new auth approach — reuse and extend the existing Dropbox auth module.

**D6 — Auto-acknowledgment:** On the developer's side, receipt of a report triggers an automatic acknowledgment back to the tester's Relay Inbox. No manual step required. The ack text is configurable (default: "Received & acknowledged — [developer name] received your report at [time]. A bug entry has been created and linked to your name.").

**D7 — Status update flow:** Developer-initiated. Status options: Acknowledged / In Progress / Fixed / Won't Fix. Each status update optionally includes a freeform text message. Routes via Dropbox to the tester's Relay Inbox as a new message row.

**D8 — General philosophy (applies to all future spec decisions within this document):** Prefer configurability over hard-coding. When a value could vary per user, practice, or workflow — it is a setting with a sensible default, not a constant.

---

## Screens to spec (5 total)

The canonical visual reference is the mockup at:
`C:\panda-gallery\workflows\design\pg_general_mockups\relay_module_v1.html`

Open it in a browser before writing. It is the visual truth. Spec prose describes behaviour; mockup pixels describe appearance.

### Screen 1 — Tester: Active Capture
- Relay window open, recording in progress
- Audio waveform display (live level bar)
- Screenshot thumbnails accumulating (manual capture button + auto-capture option)
- Timer showing recording duration
- "Stop & Process" primary CTA, "Discard" secondary
- Keyboard shortcut: Ctrl+Shift+S to stop
- Statusbar: "Recording · 0:42" with red live dot

### Screen 2 — Tester: Review & Send
- Post-transcription review screen
- Transcript displayed in a readable block with timestamp cues (e.g. [0:08])
- "Edit" affordance on transcript card (opens inline editable text field)
- "Play audio" button (in screen header and in action bar)
- Screenshot thumbnails shown as read-only grid
- Action bar: "Send to [configured recipient]" (primary), "Edit transcript", "Play audio", "Discard" (destructive, right-aligned)
- Statusbar: "Ready to send" · "Dropbox · connected"

### Screen 3 — Tester: Sent + Inbox (post-send)
- Tab bar: Inbox (with unread count badge) / Sent (active tab after send)
- Left rail: list of sent items. Selected item shows green unread dot (indicating new update received)
- Right panel: selected sent item showing:
  - Auto-ack confirmation card (green left border, "Received & acknowledged" heading)
  - Status update cards below (one per developer update, newest last)
  - Original transcript (collapsed or below updates)
- Header: "New report" utility button

### Screen 4 — Developer: Inbox
- Tab bar: Inbox (active, with new count badge) / Sent
- Left rail: incoming messages tagged BUG REPORT, ACK (system), STATUS
- Right panel for selected BUG REPORT:
  - Transcript block (full text, readable)
  - Screenshots grid (thumbnails, click to open full-size)
  - "Capture to BUGS.md" card: shows auto-drafted bug title + one-click capture button
  - After capture: card transforms to show linked bug ID + status pill
- Action bar: "Open in Audit Module" / "Play audio" / "Send update to [tester]"
- Statusbar hint: "Auto-ack sent · [time]"

### Screen 5 — Developer: Send Update (compose)
- Triggered from Screen 4 action bar "Send update to [tester]"
- Bug context card (read-only: bug ID, title, current status)
- Status picker: segmented button row — Acknowledged / In Progress / Fixed / Won't Fix
  - Active state highlighted in peach
- Message card: optional freeform text field
- Action bar: "Send update" primary CTA
- Statusbar hint: "Via Dropbox · [tester name] will see this in their Relay inbox"

---

## Relay Settings (spec the settings surface)

Accessible from the gear icon in the Relay screen header. Settings that must be specced:

- **Recipients:** list of configured contacts (name + Dropbox folder path). Add / remove. Primary recipient shown in send UI.
- **Auto-acknowledge:** toggle (default on). When on, receipt of any report triggers auto-ack immediately.
- **Acknowledgment text:** configurable freeform text (default provided). Shown in the tester's Inbox ack card.
- **Default status on capture:** the status set when "Capture to BUGS.md" is clicked (default: OPEN).
- **Dropbox connection:** connect / reconnect. Shows connected account name and sync status.
- **Local archive folder:** where Relay stores sent/received packages locally (default: `workflows/relay/`).

---

## File/folder structure

Spec the local folder layout for relay packages:

```
workflows/relay/
  sent/
    relay_20260427_143022_rebecca/
      audio.wav
      001.png  002.png  003.png
      transcript.md
      metadata.json
      status_updates/
        ack_20260427_143100.json
        update_20260427_151500.json
  received/
    relay_20260427_143022_rebecca/
      [same structure]
```

Dropbox layout mirrors `workflows/relay/` under `/Panda Gallery Relay/[channel_name]/`.

---

## metadata.json schema (v1)

Spec the schema. Minimum fields:

```json
{
  "schema_version": 1,
  "relay_id": "relay_20260427_143022_rebecca",
  "sender_name": "Rebecca Chen",
  "recipient_name": "Darrin",
  "recorded_at": "2026-04-27T14:30:22-07:00",
  "sent_at": "2026-04-27T14:30:55-07:00",
  "audio_duration_sec": 42,
  "screenshot_count": 3,
  "transcript_word_count": 89,
  "bugs_md_entry": null,
  "status": "sent"
}
```

---

## Relationship to existing specs

- **Remote Testing spec (PANDA_GALLERY_REMOTE_TESTING_SPEC_draft4.md):** Relay reuses the Dropbox OAuth2 PKCE flow from Phase 4 of that spec. The `dropbox_sync.py` module is extended, not replaced. Note the difference in purpose: Remote Testing uploads workflow-capture sessions (screenshots + audio from a test run) for Darrin to triage. Relay is a two-way communication channel for bug reports. They are separate features using the same transport.
- **BUGS.md:** The "Capture to BUGS.md" action in Screen 4 must produce an entry that conforms to BUGS.md's existing template and field conventions. Read BUGS.md for field names and format before speccing this — do not invent a new schema.
- **Audit Module (AM):** "Open in Audit Module" in Screen 4 links the captured bug to AM Screen B for triage. The link is by bug ID. No new AM changes required for v0.1.

---

## Deliverable

`C:\CODEX PG\Canonical Specs\RELAY_SPEC_v0.1.md`

Structure the spec with numbered sections matching the AM_SPEC_v1.1 pattern:
- §1 Overview and design philosophy
- §2 Locked decisions (D1–D8 above, expanded)
- §3 Screen anatomy (one sub-section per screen, 1–5)
- §4 Relay Settings
- §5 File/folder structure and metadata schema
- §6 Relationship to existing modules
- §7 Open questions (anything Codex identifies that requires Darrin's decision)

When complete, reply to this message via:
`C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\20260427_CODEX_to_CLAUDE_relay_spec_v0_1_complete.md`

Include in reply: file path of delivered spec, section count, word count estimate, and any open questions surfaced during authoring (§7 items).

---

**Deliverables:**
- `C:\CODEX PG\Canonical Specs\RELAY_SPEC_v0.1.md`
