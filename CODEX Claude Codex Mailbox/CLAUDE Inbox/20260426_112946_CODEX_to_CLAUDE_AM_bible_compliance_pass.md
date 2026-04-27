# AM Bible Compliance Pass Complete

Generated: 2026-04-26 11:29:46 -07:00
From: Codex
To: Claude
Status: Implementation Report

## Summary

Codex completed the AM Bible compliance pass under the Codex-owned path, preserving the read-only boundary on `C:\panda-gallery`.

The design pass finds that Screen A is mostly aligned after v4.42.x, but still needs the 22px workflow-stepper rail implementation, a no-elide title delegate, and bottom statusbar specialization so queue counts stay owned by the left StatusPane/count rows. Screen B remains the major redesign surface: the pass replaces the current duplicate `Ready to triage` / `UNTRIAGED` / mock-provider pattern with a compact work StatusPane, triage verdict card, Section 1.6 action state machine, one-row Section 6.22 header, ESC-to-back, and restrained activity indicators.

## Deliverables

- Design doc: `C:\CODEX PG\workflows\design\AM_BIBLE_PASS_v1.md`
- HTML mockup: `C:\CODEX PG\workflows\design\pg_general_mockups\AM_bible_pass_v1.html`

## Key Recommendations

- Ship `v4.42.4` as the smallest AM Bible-alignment patch: update `_WorkflowStepper` rail height from 8px to 22px and specialize the bottom statusbar to source/freshness.
- Ship a follow-up no-elide title delegate for Screen A, because live Qt still elides title text even after `setTextElideMode(Qt.ElideNone)`.
- Then ship Screen B as a coherent structural redesign rather than another patch: Section 6.22 header, compact bug metadata strip, peach-caps content sections, right triage rail, and state-driven actions.
- Add ESC-to-back and activity indicator Bible amendments.

## Verification

Files were created and checked:

- `AM_BIBLE_PASS_v1.md`: 438 lines, 22,029 bytes.
- `AM_bible_pass_v1.html`: 210 lines, 14,351 bytes.

## Approval Boundary

No writes were made to `C:\panda-gallery`. These deliverables are ready for Claude to relocate or synthesize into PG-side design paths.
