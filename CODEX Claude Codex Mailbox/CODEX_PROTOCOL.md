# CODEX Claude Codex Mailbox Protocol

Purpose: lightweight file-based coordination between Codex and Claude for the Panda Gallery Testing + Audit work.

Location:

`C:\CODEX PG\CODEX Claude Codex Mailbox`

## Folders

- `CODEX Inbox`: messages from Claude to Codex.
- `CLAUDE Inbox`: messages from Codex to Claude.
- `CODEX Sent`: optional copies of messages Codex sent.
- `CLAUDE Sent`: optional copies of messages Claude sent.
- `CODEX Archive`: resolved/old message copies or decision records.

## Rules

1. This mailbox is for coordination, questions, decision records, and implementation reports.
2. It does not authorize implementation by itself. Darrin remains the approval gate.
3. Do not place secrets, API keys, PHI, patient data, or private credentials in mailbox files.
4. Messages should be Markdown files.
5. Use timestamped filenames so ordering is obvious.
6. Prefer short, explicit questions and answers.
7. If a message requests a decision, mark it clearly with `Decision Needed`.
8. If a message reports implementation, list changed files and verification commands.
9. Do not edit another agent's sent message. Reply with a new file.
10. If Claude and Codex disagree, record the disagreement and ask Darrin to decide.
11. Filename timestamps are labels only. Agents must not use filename timestamps as the source of truth for unread detection because agent clocks may differ across machines and sessions.
12. The durable cross-reference is the body's `Message-ID` and `Reply-To` fields. Every message body must include a `Message-ID`. Every reply must include a `Reply-To` listing the source `Message-ID` or source filename when no `Message-ID` exists. Filesystem `LastWriteTime` is a fallback ordering hint, not a source of truth.
13. Replies must include a `Reply-To` section listing source `Message-ID` values and filename paths when available.
14. Implementation reports must include a `Deliverables` section with absolute paths.
15. Important messages must be appended to `CODEX_MAILBOX_LEDGER.md`. Important means dispatches that initiate work, completion reports, decisions, blockers, and boundary questions. Routine acknowledgements and status pings are excluded. Format: `timestamp | sender->receiver | type | topic | source-file | deliverable-path`.

## Filename Pattern

```text
YYYYMMDD_HHMMSS_FROM_to_TO_short-topic.md
```

Examples:

```text
20260424_230000_CODEX_to_CLAUDE_stage1_q1_decision.md
20260424_231500_CLAUDE_to_CODEX_stage1_implementation_report.md
```

Use 24-hour local time where practical.

## Message Template

```markdown
# Short Subject

Message-ID: CODEX-YYYYMMDD-HHMMSS-short-topic
Reply-To:
- CLAUDE-YYYYMMDD-HHMMSS-source-topic
- CODEX Inbox\source_filename.md

Generated: YYYY-MM-DD HH:MM:SS -07:00
From: Codex or Claude
To: Claude or Codex
Status: Info | Decision Needed | Response Requested | Implementation Report

## Summary

Short summary.

## Details

Relevant details.

## Questions / Decisions

- Question or decision needed.

## Approval Boundary

State whether this is informational only or whether Darrin approval is required before implementation.
```

## Current Approval Boundary

Stage 1 implementation in `C:\panda-gallery` requires Darrin's explicit approval. Mailbox messages may clarify Stage 1 details but cannot start implementation without that approval.
