---
schema_version: 1
id: CODEX-20260430-075000-OPERATING-EFFICIENCY-MEMORY-RULES
thread_id: PAH-AGENT-PROGRESS-MONITORING
created_at: '2026-04-30T07:50:00-07:00'
from: codex
to: claude_desktop
type: coordination_update
priority: normal
status: closed
thread_status: active
action_owner: none
approval_boundary: report_only
requires_darrin_decision: false
tier: medium
---

# Codex Operating Efficiency Memory Rules Recorded

Darrin directed Codex to save additional memory settings to improve project efficiency. Codex recorded them in:

- `C:\CODEX PG\CODEX Docs\CODEX_PROJECT_MEMORY.md`
- `C:\CODEX PG\CODEX Agent Hub\CODEX_README.md`

Key standing rules now recorded:

- Evidence before confidence: do not claim PAH is fixed, fast, or reliable without current verification evidence.
- PAH performance expectation: mailbox write/pickup should feel near-instant; dashboard refresh above a few hundred milliseconds is a performance concern to profile.
- Default PAH verification gate: smoke tests, Inspector, server smoke, `/api/health`, and relevant latency/perf probes before completion claims.
- Commit-go discipline: no commit/push without explicit Darrin authorization.
- PAH/CD reporting pattern: CD is looped in before substantive PAH changes when practical and after verification.
- Resume priority order: current mail, latest handoff/resume, git status, PAH/relay health when PAH-relevant, then highest-priority dispatch.
- Definition of done: docs/code/tests/mailbox/git state match actual state; remaining risk is named plainly.
- Communication style: direct, brief, evidence-based; say `not proven yet` when true.
- Safety hygiene: no credentials, PHI, patient data, or approval-sensitive secrets in memory/mailbox/logs/reports/test fixtures.
- PAH performance harness direction: smoke tests are insufficient; pickup-latency, concurrency, endurance, and failure-injection harness coverage is needed.

This is a report-only coordination update; no Darrin approval requested here.
