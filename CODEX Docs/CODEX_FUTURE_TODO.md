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
