# CODEX Current Authority Snapshot

Last updated: 2026-04-28 19:16 PT
Owner: Codex, maintained cooperatively by Claude/CC/Codex
Purpose: one short authority file so dispatches can cite deltas instead of forcing full rereads.

## Global State

- PAH development is paused by Darrin.
- Relay design/spec work is waiting on Claude/Darrin review.
- PG Design Ledger v11 lint build dispatch is live, but Codex must finish the CODEX PG checkpoint first.
- Ledger lint implementation base is v1.1 plan + v2.2 spec; v2.3 efficacy upgrades remain deferred.
- No commits have been made for the current Relay mockup/spec batch.

## PG Design Ledger Authority

| Scope | Current Authority | Notes |
| --- | --- | --- |
| Ledger review dispatch | `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\20260428_200500_CLAUDE_to_CODEX_recall_and_review_ledger_spec.md` | Review-only dispatch. Canceled earlier `pg_design_lint.py` build request. |
| Codex Ledger review deliverable | `C:\CODEX PG\CODEX Canonical Specs\PG_DESIGN_LEDGER_SPEC_v1_CODEX_REVIEW.md` | Verdict: hold v1 for major rework; reconcile v1 vs v2 before implementation. |
| Codex completion report | `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\20260428_144800_CODEX_to_CLAUDE_pg_design_ledger_v1_review_complete.md` | Sent to Claude for review. |
| Ledger lint build dispatch | `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\20260428_204500_CLAUDE_to_CODEX_ledger_lint_build_v11.md` | Live Phase 1 dispatch. Read all six authority docs before acking; build after checkpoint sequence. |
| Ledger lint write clarification | `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\20260428_211500_CLAUDE_to_CODEX_ledger_lint_clarifications_response.md` | Darrin-authorized scoped `C:\panda-gallery` writes are recorded by Claude, but Codex still waits for direct Codex-thread authorization before writing there. |
| Ledger lint clarification v2 | `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\20260428_223200_CLAUDE_to_CODEX_ledger_lint_clarifications_response_v2.md` | Hold until direct Codex-thread `C:\panda-gallery` write authorization; use stdlib parser; ack after authority-doc read. |
| Darrin Ledger go context | `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\20260428_230600_DARRIN_via_CLAUDE_to_CODEX_ledger_go_context.md` | v2.3 approved/decoupled; Phase 0 lint v11 cleared after checkpoint and direct write authorization. |
| Checkpoint refresh go | `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\20260428_213000_CLAUDE_to_CODEX_checkpoint_go_with_refresh.md` | Darrin directly said "go" in Codex thread; refresh, verify, stage, commit, push CODEX PG only. |
| Checkpoint refresh unblock | `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\20260428_223300_CLAUDE_to_CODEX_checkpoint_refresh_unblock.md` | Update index/snapshot, rerun six checks, then stage/commit/push if clean. |
| Checkpoint plan confirmation | `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\20260428_225000_CLAUDE_to_CODEX_checkpoint_plan_confirmed.md` | Confirms four-step checkpoint plan and PAH priority boundary. |
| A54 archive decision | `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\20260428_214500_CLAUDE_to_CODEX_a54_archive_decision_fifth_tab.md` | Archive stays as fifth tab; no amendment required. |
| PAH pause directive | `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\20260428_223900_CLAUDE_to_CODEX_pah_paused_until_ledger_complete.md` | Stop all PAH work until PG Design Ledger completes. |

## Relay Canonical Authority

| Scope | Current Authority | Notes |
| --- | --- | --- |
| Relay product/spec contract | `C:\CODEX PG\CODEX Canonical Specs\RELAY_SPEC_v0.3.md` | Canonical. Claude accepted v0.3. |
| Superseded Relay spec | `C:\CODEX PG\CODEX Canonical Specs\RELAY_SPEC_v0.2.md` | Superseded by v0.3. Do not use as the base unless a dispatch explicitly asks for historical comparison. |
| Relay hub decisions | `C:\panda-gallery\workflows\design\RELAY_SCREEN_C_DESIGN_v1.md` | Still valid where not superseded by v0.3. |
| PG visual language | `C:\panda-gallery\workflows\design\PG_DESIGN_BIBLE_v1.md` | Canonical visual authority. Use tokens exactly. |
| Relay baseline mockup | `C:\panda-gallery\workflows\design\pg_general_mockups\relay_module_v1.html` | Visual/shell baseline. |
| Relay delivered mockup inventory | `C:\CODEX PG\CODEX Relay Mockups\CODEX_RELAY_MOCKUP_DELIVERY_INVENTORY.md` | Read before scanning individual A52/A53/A54 reports. |

## Relay Delivered Visual Set

| Batch | File(s) | Review State |
| --- | --- | --- |
| A52 | `relay_tester_hub_v1.html`, `relay_sent_tab_v1.html`, `relay_templates_tab_v1.html`, `relay_duplicate_detection_v1.html`, `relay_compose_v1.html` | Delivered; awaiting Claude/Darrin review. |
| A53 | `relay_tester_setup_v1.html` | Accepted by Claude. |
| A54 | `relay_hub_missing_v1.html` | Delivered; awaiting Claude/Darrin review. |

Target folder:

`C:\panda-gallery\workflows\design\pg_general_mockups\`

## Reread Policy

Default for future Relay dispatches:

1. Read this authority snapshot.
2. Read `CODEX_ACTIVE_DISPATCH_INDEX.md`.
3. Read the new dispatch.
4. Read only the specific authority files or sections that the dispatch changes or cites as new.

Full reread is still required when:

- Claude/Darrin marks a dispatch `full_authority_read_required: true`.
- The canonical spec changes.
- The Design Bible changes.
- The task touches a new product area outside Relay.
- A conflict or ambiguity appears.
- Darrin explicitly asks for a full reread.

## Relay Health Checker

Read-only checker:

`C:\CODEX PG\CODEX Automation\CODEX_relay_health_check.ps1`

Use this before deciding whether a full mailbox reread is necessary. It validates the active dispatch index, current authority snapshot, source/completion paths, unindexed recent CODEX mail, PAH read-state unread counts, and recent Darrin-gated messages.

Use `-UpdateCache` to refresh:

`C:\CODEX PG\CODEX Agent Hub\CODEX state\CODEX_relay_health_cache.local.json`

The cache stores parsed frontmatter plus latest-mail cursors per inbox. It is ignored local state, not authority.

PAH diagnostics now runs the same checker with `-UpdateCache` and exposes the compact result as `diagnostics.relay_health` in the read-only cockpit payload.

## Dispatch Delta Convention

Future Claude dispatches should prefer this shape:

```yaml
authority_base: RELAY_SPEC_v0.3
authority_snapshot: C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX_CURRENT_AUTHORITY.md
delta_since_base:
  - section_or_file: "§16.4 Invite Delivery"
    change: "..."
  - section_or_file: "relay_hub_missing_v1.html"
    change: "..."
full_authority_read_required: false
```

If `full_authority_read_required` is false, Codex should not spend time rereading unchanged large docs unless needed for local verification.

## Safe Read Permission Pattern

This file does not grant OS permissions by itself. It defines the intended safe-read category for future approval/prefix rules:

- `Get-Content -LiteralPath` for files under:
  - `C:\CODEX PG\CODEX Claude Codex Mailbox\`
  - `C:\CODEX PG\CODEX Canonical Specs\`
  - `C:\CODEX PG\CODEX Docs\`
  - `C:\CODEX PG\CODEX Relay Mockups\`
  - `C:\panda-gallery\workflows\design\`
- `Get-ChildItem -LiteralPath` for mailbox folders and design mockup folders.
- `git -C ... status --short --branch` and scoped `git -C ... status --short -- <path>`.

Writes still require normal care:

- Mockup writes to `C:\panda-gallery` require Darrin/dispatch authorization.
- Mailbox completion reports are allowed when they directly answer an active dispatch.
- No commits unless Darrin explicitly asks.
