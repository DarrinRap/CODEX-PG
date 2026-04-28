# CC <-> Codex Bridge Protocol v1

Created: 2026-04-27 local time
Owner: Codex
Status: active
Related thread: PAH-COMMS-WIRING

## Purpose

This document defines the bridge protocol for direct coordination between Codex
and Claude Code (CC) during Panda Gallery / PAH work.

The bridge exists so Codex and CC can exchange scoped coordination messages
without requiring Desktop Claude to relay every message. Desktop Claude remains
available as planner, reviewer, and escalation point for architecture, UX,
clinical, safety, or disagreement items.

## Participants

- `codex`: Codex in the CODEX PG workspace.
- `claude_code`: Claude Code operating on Panda Gallery.
- `claude_desktop`: Desktop Claude, optional reviewer / coordinator.
- `darrin`: human approval and wake bridge.

## Current Operating Decision

Darrin selected the semi-manual wake model:

1. Codex / PAH writes work or review requests to the Claude Code inbox.
2. If Claude Code appears idle, Codex gives Darrin a paste-ready wake line.
3. Darrin pastes the wake line into the active Claude Code session.
4. Claude Code reads the requested inbox message and replies through the
   agreed reply lane.

No unattended PAH headless Claude Code wake adapter is enabled in v1.
Any future automated wake adapter requires explicit Darrin approval.

## Canonical PAH Route

This is the route that PAH currently uses and that has been live-tested.

### Codex -> Claude Code

Canonical inbound path for PAH-routed Codex messages to CC:

```text
C:\panda-gallery\workflows\cc_mailbox\CC Inbox\
```

PAH route id:

```text
codex_to_claude_code
```

This route was verified by live route test:

```text
PAH-ROUTE-TEST-20260427-211258-codex_to_claude_code
```

### Claude Code -> Codex / PAH Reply Detection

Canonical PAH reply-detection path for CC replies to Codex-originated PAH
messages:

```text
C:\panda-gallery\workflows\cc_mailbox\CLAUDE Inbox\
```

When replying to a Codex PAH message, CC must include either:

- `thread_id` equal to the PAH route or work thread id, or
- `Reply-To` / `reply_to` containing the source `message_id`, or
- the source `message_id` in the message body when a structured field is not
  possible.

Structured fields are preferred. Raw body matching is a fallback only.

## Secondary / Legacy Direct Lane

The CODEX mailbox contains a legacy / secondary CC inbox:

```text
C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX_CLAUDE_CODE Inbox\
```

Desktop Claude's CC protocol v2 currently asks CC to check this folder at
session start. That is acceptable as a secondary compatibility lane, but it is
not the canonical PAH route in v1.

Use this secondary lane only when a message explicitly names it, or when
reviewing old bridge-history messages. New PAH-routed Codex -> CC messages
should use the canonical native CC mailbox path:

```text
C:\panda-gallery\workflows\cc_mailbox\CC Inbox\
```

## Optional Codex Archive Copy

For CC replies that must be visible in Codex's primary mailbox, CC may also
copy or send a report to:

```text
C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\
```

This is useful for durable Codex inbox history, but PAH v1 already indexes the
native CC reply lane above.

## Filename Pattern

Use timestamped Markdown filenames:

```text
YYYYMMDD_HHMMSS_FROM_to_TO_short-topic.md
```

Examples:

```text
20260427_212855_CODEX_to_CLAUDE_CODE_darrin-request-pah-code-review-report.md
20260427_213000_CC_to_CODEX_pah_code_review.md
```

Filename timestamps are ordering hints only. The durable references are
`message_id`, `id`, `thread_id`, and `Reply-To` / `reply_to`.

## Message Schema

New messages should use YAML frontmatter where possible:

```markdown
---
schema_version: 1
id: CODEX-YYYYMMDD-HHMMSS-short-topic
thread_id: THREAD-ID
created_at: 'YYYY-MM-DDTHH:MM:SS-07:00'
from: codex
to: claude_code
type: request
priority: normal
status: open
thread_status: active
approval_boundary: coordination_only
requires_darrin_decision: false
reply_to:
  - SOURCE-MESSAGE-ID
---

# Short Subject

## Summary

One paragraph summary.

## Details

Actionable detail, paths, constraints, and expected response.

## Approval Boundary

State whether this is coordination only, Darrin approval required, or a report.
```

PAH accepts both `id` and `message_id` as message identity aliases.

## Approval Boundary

Messages in this bridge are coordination only.

They do not authorize:

- repo writes,
- commits,
- pushes,
- destructive filesystem actions,
- package installs,
- paid API calls,
- SMS/email sends,
- unattended headless Claude Code runs,
- edits outside each agent's standing workspace boundary.

Darrin's foreground approval remains required for any protected action.

## Wake Policy

Current wake policy:

```text
Read C:\panda-gallery\workflows\cc_mailbox\CC Inbox now. Darrin asks you to respond to the latest PAH/Codex message.
```

Codex should provide Darrin a specific paste-ready line whenever CC needs to
act, ideally naming the exact message path.

Do not use `--dangerously-skip-permissions` for PAH-controlled wakeups.

Future automatic CC wake work must be designed as a PAH adapter with:

- explicit Darrin approval,
- a narrow prompt file,
- restricted tools,
- no bypass permissions,
- audit records,
- idempotency / queueing.

## Desktop Claude Role

Desktop Claude should be included when:

- the message affects architecture, UX, clinical workflows, safety, or design,
- CC and Codex disagree,
- the channel path convention changes,
- Darrin decision items are surfaced,
- a review report should be visible to all agents.

Routine Codex <-> CC review requests and acknowledgements do not require
Desktop Claude as an intermediary.

## Known v1 Caveat

There is a naming mismatch between:

- Desktop Claude's CC protocol v2 secondary lane:
  `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX_CLAUDE_CODE Inbox\`
- PAH's verified canonical route:
  `C:\panda-gallery\workflows\cc_mailbox\CC Inbox\`

This protocol resolves the mismatch for PAH v1 by making the native CC mailbox
path canonical for new PAH-routed messages and preserving
`CODEX_CLAUDE_CODE Inbox` as a secondary / legacy compatibility lane.

## Verification Status

Verified:

- PAH diagnostics: passing.
- Codex -> Claude Code route: live route test received.
- Claude Code -> PAH reply detection: live ACK detected.
- Claude Code PAH code review report: received.
- Darrin-in-the-loop wake model: manually tested.

Pending:

- Desktop Claude exact route-test ACK to Codex.
- Optional future reconciliation of `CC_PROTOCOL.md` wording to match this
  canonical PAH route.

