# CODEX PAH Minimal Remaining Fixes Spec v1.0

Status: Self-reviewed draft
Owner: Codex
Scope: PAH only
Created: 2026-05-06

## Purpose

Define only the remaining fixes that are genuinely needed before PAH can honestly be called excellent and final.

This spec intentionally excludes broad redesign, speculative automation, UI polish, and non-PAH work.

## Honest Current State

PAH is operational and substantially improved, but not final.

Known good:

- PAH runs on `127.0.0.1:8765`.
- Smoke tests pass.
- Periodic health exits successfully.
- Repeat live health verification passes.
- Inspector reports zero failures.
- Ledger append contention is fixed.
- Health semantics now separate infrastructure failures from advisories.

Remaining blockers before calling PAH final:

- PAH still reports agent-owned communication backlog.
- PAH backup scope is dirty/uncommitted, which is expected during this uncommitted work but must be resolved or documented before release.
- There are untracked PAH artifacts whose purpose is not clearly documented.
- Accepted advisory state is transitional but already review-dated; the remaining need is to preserve that guardrail.

## Non-Goals

- Do not change Panda Gallery app code.
- Do not change Relay files.
- Do not add new features unless they directly reduce the blockers above.
- Do not add broad UI polish.
- Do not hide real backlog or backup warnings.
- Do not stage, commit, push, delete, or clean files without explicit approval.
- Do not create new monitors, dashboards, or background jobs for this spec.

## Required Fixes

### F1: Classify PAH-Scoped Dirty State Before Any Commit

Problem:
PAH now correctly reports its own dirty scope, but the scope includes changed source files plus untracked artifacts. Some may be useful; some may be parked or temporary.

Required action:
Create a short PAH-local release inventory that classifies each PAH-scoped dirty/untracked item as one of:

- implementation change
- spec/documentation
- generated verification artifact
- temporary artifact to delete later
- unrelated parked artifact

Acceptance criteria:

- Every PAH-scoped dirty/untracked path is listed.
- No file is deleted or staged by this inventory step.
- The PAH backup warning becomes actionable without requiring cleanup in this step.
- The inventory can be removed or superseded after the approved release commit.

### F2: Reduce Communication Backlog To Actionable Nudge List

Problem:
PAH reports open-on-agent backlog, but the user needs concise next actions, not a raw warning.

Required action:
Produce a PAH-visible backlog triage report that groups open-on-agent threads by owner and recommended nudge. This should be a report, not a new automation or broad workflow change.

Acceptance criteria:

- Report lists thread id, title, owner, and recommended nudge.
- Report does not authorize CC implementation or commits.
- Any CC implementation/commit authorization recommendation routes through Claude Desktop, not directly to CC.
- Report can recommend a nudge but must not write the nudge unless explicitly approved.
- Owner-unknown remains zero or is flagged as a stronger warning if it changes.

### F3: Timebox Accepted Advisories

Problem:
Accepted advisories are useful, but they become dangerous if they silently persist.

Required action:
Keep accepted advisories review-dated and visible. Do not add more accepted advisories unless they represent a real expected transitional state.

Acceptance criteria:

- Existing accepted advisories include owner, reason, evidence, and review-after date.
- `/api/health` exposes accepted and unaccepted snapshot advisories.
- Expired advisories return to warning behavior.

### F4: Preserve Repeat Health Verification

Problem:
The prior ledger contention bug was only visible under live periodic checks.

Required action:
Keep the repeat live health verifier as an integration check, not part of default smoke tests.

Acceptance criteria:

- Default smoke tests remain dependency-light.
- Repeat verifier runs two live periodic health checks and fails if either report is not ok.
- Verification output remains concise JSON.

## Implementation Order

1. Create PAH dirty-scope release inventory.
2. Create PAH backlog triage report.
3. Confirm accepted advisory review dates and health exposure; do not add advisory records unless verification finds a real expected transitional condition.
4. Keep repeat verifier and smoke coverage as-is unless tests expose a bug.
5. Run PAH smoke tests, Inspector, periodic health, repeat health verifier, and live `/api/health`.

## Done Definition

PAH can be called excellent/final only when:

- PAH smoke tests pass.
- Inspector has zero failures.
- Periodic health and repeat health verification pass.
- PAH backup scope is either clean or every dirty PAH item is documented for release.
- Agent backlog is either resolved or represented as a clear owner/nudge report.
- No accepted advisory is open-ended.
- No non-PAH files are changed by this work.
