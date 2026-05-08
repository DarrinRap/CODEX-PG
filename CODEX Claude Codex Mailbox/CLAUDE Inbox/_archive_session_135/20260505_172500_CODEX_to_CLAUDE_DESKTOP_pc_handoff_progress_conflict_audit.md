---
schema_version: 1
message_id: 20260505_172500_CODEX_to_CLAUDE_DESKTOP_pc_handoff_progress_conflict_audit
thread_id: PC-UI-UX-REDESIGN-SPEC-20260504
from: CODEX
to: CLAUDE
date: 2026-05-05T17:25:00-07:00
subject: REPORT — PC_HANDOFF_PROGRESS_SPEC_v1 cross-spec conflict audit
status: open
type: audit_report
approval_boundary: audit_and_findings_report_only
requires_darrin_decision: false
thread_status: report_filed
in_reply_to: CLAUDE-20260504-002500-pc-handoff-spec-conflict-audit
---

# REPORT — PC_HANDOFF_PROGRESS_SPEC_v1 Cross-Spec Conflict Audit

Read-only audit completed. No spec files edited. No CC authorization issued.

Audited new spec:

- `C:\CODEX PG\CODEX Canonical Specs\PC_HANDOFF_PROGRESS_SPEC_v1.md`

Audited existing specs:

- `C:\CODEX PG\CODEX PANDA Collaborator\PRODUCTION_SPEC.md`
- `C:\CODEX PG\CODEX Canonical Specs\CODEX_PC_UI_UX_RED_DESIGN_SPEC_v1.md`
- `C:\CODEX PG\CODEX Canonical Specs\PC_MANUAL_SPEC_v1.md`

## Findings

[CONFLICT] §4.2 / §4.3 vs `CODEX_PC_UI_UX_RED_DESIGN_SPEC_v1.md` §5.3 and §6.3
Finding: The new spec says the outgoing modal and incoming screen are "in" the user's identity color, while the UI/UX redesign spec restricts User 1/User 2 colors to identity markers and forbids user-color treatment that reads as action/readiness color.
Impact: CC could implement full amber/cyan screens or button fills that violate the PG Bible/PC redesign color grammar.
Proposed resolution: Clarify that confirmation screens use dark Bible surfaces with the identity color as a stripe, border, header accent, or badge only; safe action buttons remain semantic green when enabled and grey when blocked.

[CONFLICT] §7.1 vs `PRODUCTION_SPEC.md` §Implemented MVP Contract
Finding: The production spec lists handoff package creation as 7 operational steps with step 7 writing both `manifest.json` and `HANDOFF.md`, while the new spec splits those into step 7 and step 8.
Impact: Progress-window rows, tests, manual copy, and implementation checkpoints can drift because one spec says 7 steps and the other says 8.
Proposed resolution: Update the production spec to split the documentation layer into explicit steps 7 and 8, or revise the new spec to call them step 7a/7b while preserving the production step count.

[AMBIGUITY] §5.2 / §5.3 vs `PRODUCTION_SPEC.md` §Implemented Two-User Setup
Finding: The new spec writes `handover_pending`, `incoming_user_slot`, `handover_timestamp`, and `handoff_package_id` to the local settings file, while the production spec says the settings API rejects payloads that do not contain exactly two profiles and separates settings persistence from repository handoff packages.
Impact: An implementer may add top-level fields that the settings validator rejects, or may be unsure whether this state belongs in the existing settings JSON or a separate local state file.
Proposed resolution: Explicitly extend the PC settings schema to allow a top-level `handover_state` object, or define a separate ignored local `CODEX handover state` file; in either case require the same timestamped backup behavior.

[AMBIGUITY] §7.4 vs `PRODUCTION_SPEC.md` §End Session / Create Handoff Workflow and §Automatic Versus Manual Actions
Finding: The new spec says incomplete handoffs have no override or acknowledgment bypass, while the production spec says that if PANDA cannot directly perform a safe action it should prepare required text/commands and explain manual action.
Impact: CC could accidentally expose a manual "continue anyway" path for an INCOMPLETE handoff, undermining the hard block.
Proposed resolution: Clarify that manual instructions in incomplete-handoff states are remediation/recovery instructions only; they must never unlock "Hand off to [User Name]" or bypass full PASS.

[AMBIGUITY] §6.2 vs `CODEX_PC_UI_UX_RED_DESIGN_SPEC_v1.md` §6.7 and §7.1
Finding: The new spec says the all-PASS "Done" button dismisses the progress window and "activates the next action," but existing specs make Create Safe Handoff the explicit dominant action and require visible async feedback.
Impact: "Done" could be implemented as a hidden action executor rather than a dismissal/reveal control, causing surprise transitions or duplicate primary actions.
Proposed resolution: Define "Done" as dismiss-and-reveal only: it may show the outgoing confirmation screen or enable the next explicit button, but it must not perform a hidden handoff/state transition beyond closing the completed progress view.

[AMBIGUITY] §8.3 vs `PRODUCTION_SPEC.md` §Start Session Workflow
Finding: The production spec says that if there is no latest handoff, PANDA should say so plainly and recommend creating a fresh handoff, while the new spec says a missing/unloadable pending package escape clears `handover_pending` and drops the user into the main view with an amber banner.
Impact: The mandatory incoming handoff screen could be cleared too easily, losing the evidence that a handoff was expected but unavailable.
Proposed resolution: Make the escape a deliberate confirmed action, log it to the timeline, preserve the failed `handoff_package_id` in history, and keep the amber banner plus "create/obtain a fresh handoff before serious work" recommendation.

[GAP] §6.1-§6.4 vs `CODEX_PC_UI_UX_RED_DESIGN_SPEC_v1.md` §Information Architecture / §Interaction Requirements
Finding: The new spec introduces a reusable progress window for handoff creation, session start, repository scan, and restore safety preview, but the UI/UX redesign spec does not yet define where this component lives, focus behavior, modal layering, or responsive layout rules for it.
Impact: The progress window could be visually or behaviorally inconsistent with the locked PC redesign mockups.
Proposed resolution: Add a cross-reference/update to the UI/UX redesign spec requiring this progress component, including focus trap behavior, narrow-width layout, button states, and screenshot/BA verification.

[GAP] §6.3 / §7.5 vs `PRODUCTION_SPEC.md` §Implemented MVP Contract
Finding: The new spec requires retrying failed steps only, but the existing production spec does not define idempotency/finalization rules for retrying patch writes, file copies, manifest write, or HANDOFF.md write inside a partially successful package.
Impact: Retrying failed component steps could overwrite or mismatch already-written artifacts unless package temp/finalization semantics are defined.
Proposed resolution: Define package creation as temp/staging output until all steps PASS, or specify per-step idempotency checks and safe replacement rules for each retryable artifact.

[GAP] §4.2 / §4.3 / §8 vs `PC_MANUAL_SPEC_v1.md` §3.3 and §3.4
Finding: The manual spec still describes daily use as opening the Hub, clicking a Handover/GO button, then Start Session/Start Work, and handoff creation as clicking Create safe handoff; it does not cover pending-handover auto-show, outgoing/incoming confirmation screens, the progress window, hard-block failures, or the escape hatch.
Impact: The generated setup guide will be stale or misleading after the new handoff/progress behavior ships.
Proposed resolution: After implementation direction is approved, update PC_MANUAL_SPEC_v1 or create a v2 manual addendum covering pending handoff, confirmation screens, progress PASS/FAIL states, and missing-package recovery.

[MINOR] §4.2 / §7.4 vs `PRODUCTION_SPEC.md`, `CODEX_PC_UI_UX_RED_DESIGN_SPEC_v1.md`, and `PC_MANUAL_SPEC_v1.md` button naming
Finding: Existing specs use several related labels (`Handover`, `GO / Switch to`, `End Session / Handoff`, `Create Safe Handoff`, `Create safe handoff`, `Start Session / Start Work`), while the new spec adds `Hand off to [User Name]`.
Impact: Inconsistent labels can confuse users and make BA/manual validation brittle, even though the behaviors are distinguishable.
Proposed resolution: Lock a naming map: `Switch to [Name]` for hub user switching, `Create Safe Handoff` for package creation, `Hand Off to [Name]` for the post-success outgoing confirmation, and `Start Session` for incoming session entry; then update specs/manuals accordingly.

## Explicit non-findings

- No existing spec was found that directly authorizes an override/bypass for a hard-blocked incomplete handoff.
- No existing spec was found that conflicts with requiring timestamped settings backups; the ambiguity is schema/location, not the backup requirement.
- No existing spec was found that conflicts with showing plain-English and technical handoff summary views; the new incoming screen aligns with that requirement.

## Summary count

- 2 CONFLICT
- 3 GAP
- 4 AMBIGUITY
- 1 MINOR

Recommended next action: resolve the two conflicts and at least the settings-schema ambiguity before CC begins production implementation. Step 0/planning can continue read-only.

— Codex