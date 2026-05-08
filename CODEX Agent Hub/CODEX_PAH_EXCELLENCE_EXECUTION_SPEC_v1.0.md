# CODEX PAH Excellence Execution Spec v1.0

Status: Self-reviewed draft
Owner: Codex
Scope: PAH only
Created: 2026-05-06

## Purpose

Define the smallest honest path to make PAH excellent without adding fluff, speculative features, or broad cleanup.

Excellent means PAH is reliable, understandable, verifiable, and release-candidate-ready in its own scope. It does not mean every historical mailbox thread is solved, but any remaining warning must be intentional, actionable, and clearly owned.

## Current Honest State

PAH is operational but not final.

Strong points:

- Server runs on `127.0.0.1:8765`.
- Smoke tests pass.
- Periodic health passes.
- Repeat live health verification passes.
- Inspector reports zero failures.
- Health semantics now separate infrastructure failure from operational advisory.
- PAH-scoped dirty state and backlog have been documented.

Remaining blockers:

- `/api/health` is still `warn`, mainly because PAH correctly reports backup scope and backlog advisories.
- `pah_backup` is dirty because the PAH work is not committed and because some PAH artifacts need owner confirmation.
- Inspector has a communication backlog warning.
- Open-on-agent backlog contains many stale or superseded-looking threads.
- Snapshot model is accepted transitional, not final authority.

## Rules

- PAH only: edit only under `C:\CODEX PG\CODEX Agent Hub`.
- Do not touch Relay files.
- Do not touch Panda Gallery app code.
- Do not send CC implementation-go or commit-go tokens.
- Do not route or send backlog nudges during this spec pass.
- Do not stage, commit, push, delete, or clean files without explicit approval.
- Do not change files outside `C:\CODEX PG\CODEX Agent Hub` during execution.
- Do not add new monitors, dashboards, or background jobs.
- Prefer classification, clarity, and verification over new functionality.

## Excellence Criteria

PAH can be called excellent when all are true:

1. Infrastructure Health
   - Smoke tests pass.
   - Periodic health passes.
   - Repeat live health verification passes.
   - Inspector reports zero failures.
   - No access-denied or file contention errors appear in live health.

2. Health Honesty
   - `/api/health` explains every `warn`.
   - No `err` is present unless PAH infrastructure is broken.
   - Accepted advisories have owner, reason, evidence, and review-after date.
   - Expired advisories return to warning behavior.

3. Release Hygiene
   - PAH-scoped dirty state is either approved for commit, deliberately parked, or explicitly excluded.
   - `CODEX_agent_hub_ui.html`, `CODEX mockups/`, and `tmp_capture_pah_header.py` are owner-confirmed before release inclusion or exclusion.
   - No unclassified PAH artifact remains.

4. Backlog Hygiene
   - Open-on-agent backlog is not allowed to be a vague warning.
   - Each open-on-agent item is either active, superseded, parked, or needs Darrin/CD decision.
   - CC-owned items requiring formal direction are identified for Claude Desktop routing after separate approval.
   - Codex does not directly authorize CC implementation or commit actions.

5. Snapshot Honesty
   - Transitional snapshot status is either accepted with review date or promoted by explicit future work.
   - The current accepted snapshot advisory remains visible and review-dated.
   - This pass does not attempt to replace the snapshot model.

## Needed Work

### E1: Owner Confirmation List

Create a concise owner-decision list for PAH artifacts whose release status is uncertain:

- `CODEX_agent_hub_ui.html`
- `CODEX mockups/`
- `tmp_capture_pah_header.py`

Acceptance:

- No deletion or staging occurs.
- Each uncertain item has a recommended decision: include, exclude, park, or delete later.
- Recommendation is based on evidence from file names, timestamps, and current PAH needs.

### E2: Backlog Closure Recommendation

Turn the backlog triage into a closure recommendation list.

Acceptance:

- Each open-on-agent thread has one recommended state: active, supersede, park, or Darrin/CD decision.
- Recommendations are grouped so Darrin can approve a batch.
- Commit-go and implementation-go threads are marked Darrin/CD decision only.
- No mailbox nudge is written unless separately approved.

### E3: PAH Release Candidate Checklist

Create one PAH-local release candidate checklist that references:

- test results required
- dirty-scope inventory
- backlog recommendation report
- accepted advisories
- explicit hold list

Acceptance:

- Checklist is short.
- Checklist does not duplicate full reports.
- Checklist makes final release decision obvious.
- Checklist separates operational excellence from release-final approval.

### E4: Verify Without Creating New Risk

Run only existing verification plus the already-created repeat health verifier:

- Python syntax check
- PAH smoke tests
- PAH Inspector
- PAH periodic health
- PAH repeat live health verifier
- live `/api/health`

Acceptance:

- Report exact pass/fail and remaining warnings.
- Do not treat known accepted advisories as hidden.

## Not Needed Now

- New UI polish.
- New workflow automation.
- New background jobs.
- New mailbox writes.
- Cleanup or deletion.
- Commit or push before explicit release approval.

## Done Definition

This pass is complete when:

- The uncertain PAH artifact list is decision-ready.
- The backlog has a clear closure recommendation list.
- A release candidate checklist exists.
- Verification passes.
- Remaining warnings are only backup/commit state, backlog pending approval, or accepted advisory state.
- No files outside PAH scope are changed.

If those conditions are met, PAH can be called excellent operationally but not release-final until Darrin approves the release scope and commit.
