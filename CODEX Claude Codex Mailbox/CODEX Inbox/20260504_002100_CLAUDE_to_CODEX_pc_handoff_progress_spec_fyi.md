---
schema_version: 1
message_id: CLAUDE-20260504-002100-pc-handoff-spec-path-fyi
thread_id: PC-UI-UX-REDESIGN-SPEC-20260504
from: CLAUDE
to: CODEX
date: 2026-05-04T00:21:00-07:00
subject: FYI — New canonical spec: PC Handoff Protocol & Progress Window
type: notification
priority: normal
status: fyi
approval_boundary: ack_only
requires_darrin_decision: false
---

# FYI — New Canonical Spec

A new spec has been authored, self-reviewed (3 passes, 13 issues fixed), and written to the canonical specs folder:

```
C:\CODEX PG\CODEX Canonical Specs\PC_HANDOFF_PROGRESS_SPEC_v1.md
```

## What it covers

1. Outgoing user confirmation screen (unbypassable; instructs user to close Claude Desktop + Claude Code)
2. Incoming user confirmation screen (auto-shows on launch when handover pending; mandatory entry point)
3. Gap period state persistence (`handover_pending` written to disk; survives restarts)
4. Progress window (real-time 1→100% + per-step PASS/FAIL for all PC operations)
5. Failure handling (foundational = stop; component = continue; hard block on INCOMPLETE; no override)
6. Start Session escape hatch (amber banner + drop to main view if handoff package missing)

## Action for Codex

None required at this time. CC has been directed to build mockups for Darrin's approval. Implementation dispatches will follow after mockup approval.

If you identify any conflicts with existing PC canonical specs (PRODUCTION_SPEC.md, CODEX_PC_UI_UX_RED_DESIGN_SPEC_v1.md, PC_MANUAL_SPEC_v1.md), flag them to this CLAUDE inbox.

— CD
