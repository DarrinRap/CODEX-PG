# CODEX PAH Health Policy

Status: Active
Owner: Codex
Scope: PAH only

## Levels

- `ok`: PAH infrastructure is operating and no unresolved warning requires user attention.
- `warn`: PAH is operational, but an advisory, backlog, stale report, dirty backup scope, or accepted transitional condition should remain visible.
- `err`: PAH infrastructure is broken or a critical contract failed.
- `unknown`: PAH does not have enough current evidence to classify the component.

## Infrastructure Failures

Use `err` for:

- PAH server endpoint failures.
- Failed critical route diagnostics.
- Unreadable or corrupt required PAH JSON state.
- Missing required live-monitor sidecars during active dispatch.
- Periodic health reports with non-advisory failed checks.
- Owner-unknown work that crosses a documented escalation threshold.

## Operational Advisories

Use `warn` for:

- Agent-owned or Darrin-owned communication backlog.
- Dirty PAH-scoped backup status.
- Accepted transitional warnings whose review date has not expired.
- Stale but non-critical reports.
- Missing optional sidecars when no active dispatch is being monitored.

## Accepted Advisories

Accepted advisories live in:

`C:\CODEX PG\CODEX Agent Hub\CODEX config\CODEX_pah_accepted_advisories.json`

Each record must include:

- `condition_id`
- `accepted`
- `owner`
- `accepted_at`
- `review_after`
- `reason`
- `source_evidence`

Expired accepted advisories return to normal warning behavior.

## Communication Backlog

Communication backlog is visible operational work, not infrastructure failure, unless owner-unknown work or stale critical routes cross a documented threshold.

Agent-owned backlog should drive concise PAH-visible nudges. Darrin-owned backlog should remain visible but must not be classified as an agent failure.
