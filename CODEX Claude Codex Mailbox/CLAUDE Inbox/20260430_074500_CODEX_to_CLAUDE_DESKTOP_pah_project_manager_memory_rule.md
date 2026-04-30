---
schema_version: 1
id: CODEX-20260430-074500-PAH-PROJECT-MANAGER-MEMORY-RULE
thread_id: PAH-AGENT-PROGRESS-MONITORING
created_at: '2026-04-30T07:45:00-07:00'
from: codex
to: claude_desktop
type: coordination_update
priority: high
status: closed
thread_status: active
action_owner: none
reply_to: []
approval_boundary: report_only
requires_darrin_decision: false
tier: medium
---

# PAH Coordination Rule Recorded

Darrin directed Codex to always automatically communicate with CD on all PAH-related matters, and stated that CD is Codex's project manager for PAH.

Codex recorded this as durable memory in:

- `C:\CODEX PG\CODEX Docs\CODEX_PROJECT_MEMORY.md`
- `C:\CODEX PG\CODEX Agent Hub\CODEX_README.md`

Operational interpretation: PAH diagnostics, incidents, speed/reliability findings, architecture choices, implementation plans, verification results, blockers, and handoff/status updates should be CD-visible by default. Codex should file a concise CD-visible mailbox update before substantive PAH code changes when practical, and after verification before claiming completion.

Boundary preserved: CD guidance coordinates PAH work, but Darrin remains the approval gate for protected actions, commits, pushes, writes to `C:\panda-gallery`, external services, and other approval-sensitive operations.
