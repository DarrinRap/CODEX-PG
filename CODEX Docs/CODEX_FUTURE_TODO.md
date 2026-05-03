# CODEX Future TODO

Date created: 2026-04-28
Owner: Codex
Purpose: low-pressure backlog for process improvements, future cleanup, and ideas that should survive thread handoffs without interrupting active development.

## Process Improvements

### Relay protocol speedup

Status: promoted and implemented 2026-04-28.

Implemented files:

- `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX_ACTIVE_DISPATCH_INDEX.md`
- `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX_CURRENT_AUTHORITY.md`
- `C:\CODEX PG\CODEX Docs\CODEX_MAILBOX_RELAY_PROTOCOL_v1.md`
- `C:\CODEX PG\CODEX Relay Mockups\CODEX_RELAY_MOCKUP_DELIVERY_INVENTORY.md`

Original goal: add a tighter Claude/CC/Codex relay protocol to reduce mailbox and file-writing latency without making the work sloppy.

Candidate shape:

- One active-dispatch index file.
- One short current-authority file.
- Claude dispatches include deltas since the current canonical spec, such as `RELAY_SPEC_v0.3`, instead of requiring full rereads every time.
- Standing permission pattern for safe mailbox/spec reads.

Expected benefit: less time spent polling, rereading large authority docs, and reconstructing state from a noisy mailbox.

## Housekeeping

### Preserve current Codex PG work

Status: pending; do not run backup/commit automation until CD clears the PC hold or Darrin explicitly asks for a full backup.

Run the normal PG backup/commit automation after current dispatch work reaches a safe pause. Current uncommitted/untracked state includes accepted Codex specs, mailbox reports/inbox items, PAH tray popup suppression, and PANDA Collaborator icon asset updates.

### Separate PG applet and desktop polish edits from CC work

Status: pending.

Before committing `C:\panda-gallery`, review and separate user-directed Codex edits from any CC/L28 in-flight changes. Known Codex-touched areas include the Bible Audit applet, PG Clip Launcher behavior/icon/shortcut, Vellum icon assets, Bible Applet shortcut/icon, and PAH/desktop shortcut polish.

### Restart PAH tray process

Status: pending.

Restart the running PANDA Agent Hub tray process so the disabled toaster/balloon popup behavior from `C:\CODEX PG\CODEX Agent Hub\CODEX_start_agent_hub_tray.ps1` takes effect.

### Continue queued CD audit

Status: completed 2026-05-01.

Completed the queued read-only `BA-FAILURE-DB-AUDIT` and wrote `C:\CODEX PG\CODEX Canonical Specs\BA_FAILURE_DB_v1.json`. Completion report filed at `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\20260501_200500_CODEX_to_CLAUDE_ba_failure_db_audit_complete.md`.

### BA applet clean rewrite

Status: completed 2026-05-01.

Synced `C:\panda-gallery\workflows\design\applets\PG_Design_Bible_Audit_v1.html` to `BA_FAILURE_DB_v1.json`, verified single script block, one handler per UI element, chip score updates without modal jump, explicit View Report modal, and clipboard button flash behavior. Completion report filed at `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\20260501_204500_CODEX_to_CLAUDE_ba_applet_clean_rewrite_complete.md`.

### Current HOLD state

Status: active as of 2026-05-01.

Codex is on HOLD pending CD next dispatch. Pattern 18 ping-limit rule is active: after a completion report, wait; after two hours with no CD reply, send one follow-up ping only, then HOLD. PC/PANDA Collaborator remains paused; preserved PC working-tree changes must not be committed without explicit Darrin/CD resume.
