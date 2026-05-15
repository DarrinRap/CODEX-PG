---
schema_version: 1
id: CODEX-20260512_213457-pc-ux-rebuild-for-cc
thread_id: PAM-CHLOE-PUBLISHING-UX-REBUILD
from: codex
to: claude_desktop
type: relay_request
status: requested
created_at: '2026-05-12T21:34:57-07:00'
priority: high
action_owner: claude_desktop
requires_darrin_decision: true
approval_boundary: coordination_only
---

# Relay Request: Ask CC To Rebuild Pam&Chloe Publishing UX From Scratch

## Summary

Darrin says the current Pam&Chloe Publishing app looks terrible and wants CC to remake the UX from scratch, using Codex's current implementation only as functional scaffolding. Please dispatch this to CC through the canonical Desktop Claude -> CC lane if you approve the boundary.

## User Direction

User request: "the app looks terrible. ask CC to remake the UX from scratch using your design as a starting point"

## Current App Files

- Main app: C:\Users\drrap\OneDrive\Documents\Coloring Books\coloring_book_tracker.html
- Helper server: C:\Users\drrap\OneDrive\Documents\Coloring Books\pam_chloe_server.py
- Helper worker: C:\Users\drrap\OneDrive\Documents\Coloring Books\pam_chloe_helper.py
- Mac copy notes: C:\Users\drrap\OneDrive\Documents\Coloring Books\MAC_COPY_README.md
- Portable ZIP currently refreshed by Codex: C:\Users\drrap\OneDrive\Documents\PamChloe_Publishing_Mac_Portable.zip

## Why This Needs CC

The app is functionally rich but visually and interactionally overgrown. It now contains many useful flows: project tracking, 50-page planning, AI drafting, image handoff paths, book visualizer, KDP packet building, cover-wrap handling, helper integration, final submit panel, and Mac portability. The problem is the UX: it feels intimidating, dense, visually heavy, and patched together.

## UX Rebuild Goal

Rebuild the front-end experience into a calm, friendly, powerful production studio for Pam, who has limited computer skills. The visual design should feel like a guided publishing cockpit, not a developer dashboard.

Use current Codex app behavior as the functional source of truth, but do not preserve the current layout unless it genuinely helps. A ground-up UX remake is wanted.

## Must Preserve Functionality

- Multiple book projects stored locally.
- Starter and custom templates.
- Friendly guided workflow from idea -> plan -> images -> review -> cover -> upload.
- 50-page manifest, with fixed final Pam & Chloe black-and-white page.
- One-image-at-a-time Codex handoff: prompt + required save path.
- Image path tracking, substitution, deletion, verification.
- Book visualizer with page flipping, keyboard navigation, drag reorder.
- KDP metadata and packet generation.
- Local helper controls.
- Cover workflow with toggle:
  - preferred KDP mode: one full wraparound cover file containing back + spine + front
  - optional design mode: separate front/back art before building a wrap
- Final upload/submit readiness panel that clearly says Amazon final submission still happens in KDP.
- F1 help and tooltips, but no clipped or blank tooltips.
- Mac portability should still work.

## Design Direction

Recommended structure:

1. Persistent left rail: books, progress, current book status.
2. Top stepper: big friendly sequence with green done states, red/amber blockers, and a clear next action.
3. Main stage: only one primary workflow visible at a time.
4. Right assistant/help drawer: plain-English guidance, warnings, and next action.
5. Advanced tools tucked behind an obvious expandable panel.

Avoid:

- Giant dark panels stacked endlessly.
- Toolbars full of equally weighted buttons.
- Tiny arrows or decorative indicators.
- Clipped tooltips.
- Ambiguous labels like "packet" without explaining the outcome.
- Multiple competing instructions visible at once.
- Anything that makes Pam hunt for the next button.

## Visual Acceptance Criteria

- First viewport must make the next step obvious within 3 seconds.
- The UI should fit common laptop screens without constant vertical scrolling for core tasks.
- Buttons should have hierarchy: primary next action, secondary actions, advanced actions.
- Every major action needs a short plain-English label plus tooltip/help text.
- Use green checkmarks for completed, amber for in progress/warning, red for blocking.
- The cover section must teach KDP's one-wrap-cover requirement visually.
- Book visualizer should look like a book/workbench, not a debug grid.
- The interface should feel warm, peach/cream/Pam&Chloe branded, but not childish.
- Preserve accessibility basics: keyboard navigation, focus states, sufficient contrast, readable font sizes.

## Implementation Notes

- If possible, keep the app as a single portable HTML file plus the existing helper scripts.
- CC may refactor HTML/CSS/JS inside coloring_book_tracker.html heavily.
- CC should avoid changing helper behavior unless needed to keep the UX wired correctly.
- If CC cannot edit outside C:\panda-gallery\ under its current boundary, CD/Darrin must grant a specific exception for C:\Users\drrap\OneDrive\Documents\Coloring Books\ or copy the app into a CC-accessible working area.

## Verification Required

- Open/reload http://127.0.0.1:8766/coloring_book_tracker.html.
- Confirm no browser console errors.
- Verify the main flows still work at least at smoke-test level:
  - create/select book
  - set title/theme
  - generate or seed 50 rows
  - copy current Codex image instruction
  - switch cover modes
  - see KDP readiness warnings
  - use visualizer previous/next keyboard controls
  - open F1 help
- Write a completion report back to Desktop Claude's inbox with changed files and screenshots if possible.

## Approval Boundary

This is a relay request only. Codex is not issuing a direct CC implementation-go token. CD should decide whether to dispatch to CC and whether Darrin's latest instruction is sufficient to authorize CC edits in the OneDrive app folder.
