# CODEX Active Dispatch Index

Last updated: 2026-04-28 19:16 PT
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
| PG-LEDGER-SYSTEM | blocked | Codex | Finish checkpoint first, then read authority docs, ack, and build Ledger lint package after Darrin's direct `C:\panda-gallery` authorization. | `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\20260428_204500_CLAUDE_to_CODEX_ledger_lint_build_v11.md`; `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\20260428_211500_CLAUDE_to_CODEX_ledger_lint_clarifications_response.md`; `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\20260428_223200_CLAUDE_to_CODEX_ledger_lint_clarifications_response_v2.md`; `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\20260428_230600_DARRIN_via_CLAUDE_to_CODEX_ledger_go_context.md` | `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\20260428_185424_CODEX_to_CLAUDE_ledger_lint_build_clarifications.md` |
| RELAY-MOCKUP-BATCH-A52 | waiting_review | Claude/Darrin | Review 5 delivered A52 mockups. Codex has no action unless review requests changes. | `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\20260428_190100_CLAUDE_to_CODEX_a52_go.md` | `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\20260428_134800_CODEX_to_CLAUDE_a52_delivery_complete.md` |
| A54-RELAY-HUB-MISSING-SCREENS | accepted | none | Archive-as-fifth-tab decision locked; no mockup amendment required. | `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\20260428_214500_CLAUDE_to_CODEX_a54_archive_decision_fifth_tab.md` | `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\20260428_133200_CODEX_to_CLAUDE_a54_relay_hub_missing_complete.md` |
| CODEX-UNCOMMITTED-WORK-DIRECTION | in_progress | Codex | Refresh manifest, pass six checks, then stage/commit/push approved CODEX PG checkpoint. | `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\20260428_152300_CLAUDE_to_CODEX_uncommitted_work_direction.md`; `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\20260428_204500_CLAUDE_to_CODEX_followup_direction_prep_during_block.md`; `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\20260428_205000_CLAUDE_to_CODEX_checkpoint_prep_authorized.md`; `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\20260428_213000_CLAUDE_to_CODEX_checkpoint_go_with_refresh.md`; `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\20260428_223300_CLAUDE_to_CODEX_checkpoint_refresh_unblock.md`; `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\20260428_225000_CLAUDE_to_CODEX_checkpoint_plan_confirmed.md` | `C:\CODEX PG\CODEX Docs\CODEX_CHECKPOINT_PREP_2026-04-28.md`; `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\20260428_174104_CODEX_to_CLAUDE_checkpoint_prep_ready.md`; `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\20260428_191206_CODEX_to_CLAUDE_checkpoint_refresh_blocked.md` |

## Recently Closed

| Thread | Closed State | Authority / Output |
| --- | --- | --- |
| MAILBOX-RELAY-PROTOCOL-V1 | seeded_for_claude | `C:\CODEX PG\CODEX Docs\CODEX_MAILBOX_RELAY_PROTOCOL_v1.md`; coordination note sent to Claude. |
| RELAY-SPEC-V03 | accepted_by_claude | `C:\CODEX PG\CODEX Canonical Specs\RELAY_SPEC_v0.3.md` is canonical. |
| A53-RELAY-TESTER-SETUP-UX | accepted_by_claude | `C:\panda-gallery\workflows\design\pg_general_mockups\relay_tester_setup_v1.html` accepted. |

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



