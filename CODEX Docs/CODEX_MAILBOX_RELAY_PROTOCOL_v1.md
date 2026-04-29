# CODEX Mailbox Relay Protocol v1

Date: 2026-04-28
Owner: Codex
Purpose: reduce Claude/CC/Codex latency by replacing repeated full mailbox/spec reconstruction with a small operational protocol.

## Problem

The previous workflow was slow because each agent had to:

- Poll noisy mailbox folders.
- Guess which dispatch was still active.
- Reread large authority docs even when nothing had changed.
- Reconstruct canonical state from old completion notes.
- Ask for filesystem approval on the same safe read patterns repeatedly.

## New Files

| File | Role |
| --- | --- |
| `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX_ACTIVE_DISPATCH_INDEX.md` | Single active queue and review-state index. |
| `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX_CURRENT_AUTHORITY.md` | Short canonical authority snapshot and reread policy. |
| `C:\CODEX PG\CODEX Relay Mockups\CODEX_RELAY_MOCKUP_DELIVERY_INVENTORY.md` | Current Relay visual deliverable inventory. |
| `C:\CODEX PG\CODEX Automation\CODEX_relay_health_check.ps1` | Read-only health checker for the compact relay protocol. |

## Required Agent Behavior

### Before starting work

1. Read `CODEX_ACTIVE_DISPATCH_INDEX.md`.
2. Read `CODEX_CURRENT_AUTHORITY.md`.
3. Read only the newest dispatches that are not reflected in the index.
4. If the dispatch says it is a delta, read only the cited delta files/sections.
5. If the dispatch changes active state, update the index before implementation.

### When writing a dispatch

Claude/CC should include:

```yaml
authority_base: RELAY_SPEC_v0.3
authority_snapshot: C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX_CURRENT_AUTHORITY.md
delta_since_base:
  - section_or_file: "..."
    change: "..."
full_authority_read_required: false
```

Use `full_authority_read_required: true` only when there is a real reason:

- canonical spec changed
- Design Bible changed
- new product area
- safety/compliance issue
- known conflict between docs

### When completing work

1. Write the normal mailbox completion report.
2. Update `CODEX_ACTIVE_DISPATCH_INDEX.md`.
3. Update any compact inventory affected by the work.
4. Do not commit unless Darrin asks.

## State Labels

Use these in the active index:

| State | Meaning |
| --- | --- |
| `new` | Mail arrived; not yet read or triaged. |
| `in_progress` | Codex/CC is actively working. |
| `blocked` | Needs Darrin/Claude/CC input before proceeding. |
| `delivered` | Output written, completion report sent. |
| `waiting_review` | Delivered and waiting on Claude/Darrin review. |
| `accepted` | Review accepted; no further action. |
| `superseded` | Replaced by a newer dispatch or authority. |
| `paused_by_darrin` | Explicitly paused by Darrin. |

## Health Check Command

Run this before a handoff, after a dispatch-index edit, or whenever "what is active?" feels ambiguous:

```powershell
& "C:\CODEX PG\CODEX Automation\CODEX_relay_health_check.ps1"
```

Use JSON mode for future PAH diagnostics integration:

```powershell
& "C:\CODEX PG\CODEX Automation\CODEX_relay_health_check.ps1" -Json
```

Refresh the ignored local cache and newest-mail cursors:

```powershell
& "C:\CODEX PG\CODEX Automation\CODEX_relay_health_check.ps1" -UpdateCache
```

Cache path:

`C:\CODEX PG\CODEX Agent Hub\CODEX state\CODEX_relay_health_cache.local.json`

The checker is read-only unless `-UpdateCache` is passed. Cache update mode writes only the ignored local cache file. It validates:

- required relay files exist
- active queue states are recognized
- duplicate active dispatch rows
- source/completion paths exist
- stale `new`, `in_progress`, or `blocked` rows
- newer CODEX Inbox mail not reflected in the index or authority snapshot
- recent unread incoming mailbox items from PAH read state
- recent Darrin-gated messages

PAH diagnostics also runs this checker and exposes the compact result as `diagnostics.relay_health` in the read-only cockpit payload.
PAH diagnostics uses `-UpdateCache`, so normal cockpit refreshes keep the cache warm.

## Safe Read Pattern

Preferred safe read operations:

- list mailbox/design folders
- read markdown/html authority files
- check git status
- compute file hashes for delivered artifacts

These operations should be treated as low-risk, read-only support work. If the desktop sandbox asks for escalation, request a narrow persistent prefix rule where available. Do not use this as permission for writes, deletes, commits, pushes, installs, downloads, or web submissions.

## Current Relay Baseline

As of 2026-04-28:

- `RELAY_SPEC_v0.3.md` is canonical.
- A53 is accepted.
- A52 and A54 are delivered and awaiting review.
- PAH remains paused.

## Maintenance Rule

This protocol only stays fast if the small files stay current. Any agent that changes dispatch state must update the active index in the same turn.
