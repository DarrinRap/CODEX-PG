# STATUS ONLY - Vellum Approval Viewer Planning File Locations

From: Codex
To: CC/CD
Timestamp: 2026-05-07 19:03:19 -07:00

This is a status/location notice only. It is not implementation-go, commit-go, or authorization to code.
Formal CC authorization remains CD-owned.

## Files to preserve/read

1. Clarifying questions and Darrin answers:
   $clarifications

2. Focused Vellum default mockup approval viewer spec draft:
   $spec

3. Standing Darrin approval workflow preferences:
   $pref

## Current state

Darrin approved the clarification round through Q24 and authorized Codex to draft the focused Vellum upgrade spec.
The spec is still a draft for Darrin review. It requires Vellum workflow mockups before any CC coding.

Key rules captured:

- Vellum should become the planned default mockup approval viewer.
- Default approval view should be actual-size / 100 percent.
- Fit-to-screen is secondary and approval from non-actual-size view should warn but not hard-block.
- Side-by-side images are orientation aids only; full-size individual mockups are the approval artifacts.
- Each mockup needs short readable filename/title, visible status badge, screen/state label, version history, checklist, optional Darrin notes, and one-click decision state.
- Vellum must use non-destructive overlays only and must not alter source mockup images.
- Approval packet export should create/update DECISION_SUMMARY.md and related packet metadata.
- Handoff-ready only when required mockups are approved direction or explicitly marked Future/not approved (not-for-coding).
- CC-ready scope candidates must include approved mockups only and remain pending CD authorization.

No action is requested from CC unless CD later dispatches a formal task.
