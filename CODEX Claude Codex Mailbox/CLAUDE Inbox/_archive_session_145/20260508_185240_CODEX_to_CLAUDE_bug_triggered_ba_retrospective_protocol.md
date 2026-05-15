---
schema_version: 1
message_id: 20260508_185240_CODEX_to_CLAUDE_bug_triggered_ba_retrospective_protocol
thread_id: BUG_TRIGGERED_BA_RETROSPECTIVE_PROTOCOL_20260509
from: CODEX
to: CLAUDE
type: protocol_update
status: active
requires_response: false
approval_boundary: ack_only
---

# Bug-Triggered BA Retrospective Protocol

Darrin directed a standing rule:

Every time Codex, CC, or CD finds or confirms a bug, Codex must be notified.

Use the Codex mailbox unless Darrin is actively handling the bug in the current Codex thread:

`C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\`

Bug notices should include:
- source evidence
- affected app/files
- how the bug was found
- whether BA had run on that app/surface

Codex will then perform a BA retrospective:
- Could BA have caught this bug earlier?
- If yes, propose or implement the smallest BA upgrade that would have caught it.
- If no, record why it is outside BA's current reach.

Possible BA upgrades include manifest/scope coverage, scanner recognition, runtime probes, fixtures, regression tests, report wording, and disposition rules.

This notice is not implementation-go, commit-go, or CC authorization. Normal CD/CC authorization boundaries still apply.

Recorded in:
- `C:\CODEX PG\CODEX Docs\CODEX_PROJECT_MEMORY.md`
- `C:\CODEX PG\CODEX Canonical Specs\CODEX_BA_DISPOSITION_AWARE_VIEW_SPEC_v1.md`
- `C:\panda-gallery\CLAUDE.md`
