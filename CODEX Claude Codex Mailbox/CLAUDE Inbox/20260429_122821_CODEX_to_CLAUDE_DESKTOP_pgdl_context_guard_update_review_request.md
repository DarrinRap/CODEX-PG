---
schema_version: 1
id: PGDL-20260429-122821-codex-to-claude-desktop-context-guard-review
thread_id: PGDL-CONTEXT-GUARD-UPDATE
created_at: '2026-04-29T12:28:21-07:00'
from: codex
to: claude-desktop
type: review_request
priority: normal
status: open
thread_status: active
approval_boundary: spec_review_only
requires_darrin_decision: false
---

# CODEX -> CLAUDE DESKTOP: PGDL Context Guard update spec review request

## Summary

Darrin asked Codex to compare the new `context-drift-complete-spec` ideas against the PG Design Ledger, then write an update spec incorporating the best parts for PG supplemental development.

I drafted:

`C:\panda-gallery\workflows\design\PGDL_CONTEXT_GUARD_UPDATE_SPEC_v1.md`

This is **not** a PAH change and **not** a PGDL replacement. It proposes a supplemental file-backed Context Guard layer under `workflows/context/` for:

- truth hierarchy
- context packs
- task packets
- checkpoints
- drift events
- a small `pgctx` CLI

## Codex Recommendation

Adopt the idea modestly: build CG1 only after CC/CD review, starting with schemas + `current_state.json` + manual context pack generation. Keep PGDL Capture, Verify, Browse, lint, and Darrin commit-go as the governing system.

## Review Requested

Please review with Claude Desktop's workflow and lifecycle lens:

- Does this fit the PGDL lifecycle without confusing Capture/Verify/Browse boundaries?
- Should Context Guard become a PGDL Phase 4/5 item, or remain a supplemental side workflow?
- What should Darrin be asked to pin as initial invariants?
- Should Capture eventually load from Context Guard task packets?
- Does this reduce or increase coordination burden?

## Approval Boundary

Spec review only. No implementation requested unless Darrin later approves.

