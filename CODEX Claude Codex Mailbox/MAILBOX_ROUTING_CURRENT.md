# Current PG Mailbox Routing

Updated: 2026-05-08 10:05:20 -07:00

This is the current routing map. It is intended to stop CC/CD/Codex from chasing old or duplicate inboxes.

## Canonical Active Lanes

1. Codex <-> Desktop Claude/CD
   - CD to Codex: C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\
   - Codex to CD: C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\

2. Desktop Claude/CD <-> Claude Code/CC
   - CD to CC: C:\panda-gallery\workflows\cc_mailbox\CC Inbox\
   - CC to CD: C:\panda-gallery\workflows\cc_mailbox\CLAUDE Inbox\

## Authorization Rule

Codex must not send implementation-go or commit-go tokens directly to CC. If Darrin says go for CC work in Codex chat, Codex routes that request to CD through the Codex-to-CD inbox. CD owns formal CC authorization tokens.

## Legacy Paths Eliminated From Active Workflow

These folders are not active workflow lanes and must not receive new dispatches:

- C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX_CLAUDE_CODE Inbox\
- C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Claude Code Inbox\

PAH may still monitor these folders as legacy traps so accidental or historical mail is visible and flagged. Monitoring is not authorization to use them. New mail found there should be treated as misrouted and reissued through the canonical lane.

## Operational Rule

Mailbox check = list first. Read only files present in the current canonical lane. If a legacy lane contains new mail, report it as misrouted and ask CD to reissue through the canonical lane.
