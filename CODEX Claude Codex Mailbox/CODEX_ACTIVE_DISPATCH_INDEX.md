# CODEX Active Dispatch Index

Last updated: 2026-05-01 23:12 PT
Owner: Codex, maintained cooperatively by Claude/CC/Codex
Purpose: one short file that answers "what is active now?" without rereading the whole mailbox.

## How To Use This File

1. Read this file before scanning old mailbox entries.
2. Read `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX_CURRENT_AUTHORITY.md` for the short authority snapshot.
3. If a dispatch is listed as `waiting_review`, do not rework it unless a newer mail item asks for changes.
4. If a new dispatch arrives, add it to `Active Queue` before starting implementation.
5. When work completes, update its row and write the normal mailbox completion report.
6. Keep rows short. Link to the source file instead of copying the dispatch.

## Active Queue

| Thread | State | Owner | Next Action | Source Mail | Completion / Ack |
| --- | --- | --- | --- | --- | --- |

No Codex-owned active dispatch rows are indexed at this time. Current action is Darrin-directed PAH cleanup.

## Recently Closed

| Thread | Closed State | Authority / Output |
| --- | --- | --- |
| PG-LEDGER-SYSTEM | archived_historical | Source and ack mail were swept to `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Archive\Cleared Mailboxes\20260429_074101\`; not active in current Codex session. |
| RELAY-MOCKUP-BATCH-A52 | archived_historical | Source mail is under `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Archive\Cleared Mailboxes\20260429_074101\CODEX Inbox\`; delivery report is under `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Archive\Deleted Alerts\20260428\`. |
| A54-RELAY-HUB-MISSING-SCREENS | archived_historical | Source and completion mail were swept to `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Archive\Cleared Mailboxes\20260429_074101\`; archive-as-fifth-tab decision remains accepted. |
| CODEX-UNCOMMITTED-WORK-DIRECTION | archived_historical | Checkpoint work completed in later backup/checkpoint commits; source mail was swept to `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Archive\Cleared Mailboxes\20260429_074101\`. |
| MAILBOX-RELAY-PROTOCOL-V1 | seeded_for_claude | `C:\CODEX PG\CODEX Docs\CODEX_MAILBOX_RELAY_PROTOCOL_v1.md`; coordination note sent to Claude. |
| RELAY-SPEC-V03 | accepted_by_claude | `C:\CODEX PG\CODEX Canonical Specs\RELAY_SPEC_v0.3.md` is canonical. |
| A53-RELAY-TESTER-SETUP-UX | accepted_by_claude | `C:\panda-gallery\workflows\design\pg_general_mockups\relay_tester_setup_v1.html` accepted. |

## Indexed Recent CODEX Mail

These newer CODEX Inbox items were read during the 2026-05-01 PAH cleanup pass and are intentionally not active queue rows:

- `20260501_203000_CLAUDE_to_CODEX_directives_and_next_task.md` - PC paused, BA accepted, Pattern 18 standing rule.
- `20260501_201500_CLAUDE_to_CODEX_pattern18_ping_limit_rule.md` - one ping only, then HOLD.
- `20260502_022000_CLAUDE_to_CODEX_current_task_clarification.md` - BA accepted, PC width on hold, stand by after BA audit.
- `20260502_021500_CLAUDE_to_CODEX_session115_directive.md` - HOLD unless new dispatch.
- `20260502_011000_CLAUDE_to_CODEX_ba_applet_fix.md` - BA applet fix dispatch already completed and reported.
- `20260502_010000_CLAUDE_to_CODEX_ba_failure_db_audit.md` - BA failure DB audit already completed and reported.
- `20260501_185500_CLAUDE_to_CODEX_claudemd_split_ack.md` - analysis acknowledged.
- `20260501_184500_CLAUDE_to_CODEX_bugs150_151_ack.md` - spec acknowledged.
- `20260501_183100_CLAUDE_to_CODEX_claudemd_split_analysis.md` - read-only analysis dispatch completed.
- `20260501_183000_CLAUDE_to_CODEX_bugs150_151_spec.md` - read-only spec dispatch completed.
- `20260501_181100_CLAUDE_to_CODEX_l27_ack.md` - L27 spec ack.
- `20260501_175000_CLAUDE_to_CODEX_l27_relay_fix_spec.md` - L27 spec completed and handed to CC.
- `20260501_173200_CLAUDE_to_CODEX_l26_relay_audit_ack.md` - L26 relay audit accepted; no more Codex audit work.
- `20260501_173100_CLAUDE_to_CODEX_pc_reg_width_hold.md` - PC registration width fix on hold unless Darrin resumes.
- `20260501_132300_CLAUDE_to_CODEX_l26_relay_audit.md` - L26 relay audit completed and accepted.
- `20260501_132000_CLAUDE_to_CODEX_ledger_compliance_dispatch.md` - Ledger compliance spec completed.

## Paused / Do Not Resume Without Darrin

| Thread | State | Note |
| --- | --- | --- |
| PAH development | paused_by_darrin | Darrin paused PAH while Claude dispatches arrive. Do not continue PAH unless Darrin explicitly reopens it. |
| PAH-PAUSE-DIRECTIVE | paused_by_darrin | `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\20260428_223900_CLAUDE_to_CODEX_pah_paused_until_ledger_complete.md` parks all PAH development until Ledger ships. |

## Current Relay Deliverable Inventory

Use this compact inventory before reading individual mockup completion notes:

`C:\CODEX PG\CODEX Relay Mockups\CODEX_RELAY_MOCKUP_DELIVERY_INVENTORY.md`

## Next Mail Check Rule

When asked to "read mail" or "continue":

1. Read this index.
2. Read `CODEX_CURRENT_AUTHORITY.md`.
3. List newest files in `CODEX Inbox`.
4. Read only files newer than the latest row here, unless a row points to a needed source.
5. Update this index if the new mail changes active state.



