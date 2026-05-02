# Ledger Capture Redesign - Codex Comparison Memo

Date: 2026-05-01

## Files

- `capture_redesign_v1_codex.html` - Guided Review Console
- `capture_redesign_v2_codex.html` - Decision Workbench
- `capture_redesign_v1_codex_viewport.png` - 1280x800 render evidence
- `capture_redesign_v2_codex_viewport.png` - 1280x800 render evidence

## Shared fixes in both mockups

- Replaces the native/light staging picker with a PG-dark picker dialog.
- Makes double-click / Enter equivalent to `Open this draft`.
- Uses a top guidance line: open draft -> review/check details -> lock decision.
- Renames jargon-heavy labels:
  - `Title` -> `Decision title`
  - `Rationale` -> `Why we chose this`
  - `Decision Q&A` -> `The conversation that led here`
  - `Bible sections` -> `Linked Design Bible refs`
  - `Paths considered and rejected` -> `What we ruled out and why`
  - `Snippet mode` -> `Visual reference (screenshot or mockup)`
- Keeps `!` as a recommended-field marker and explains it in lay language.
- Uses rectangular buttons for actions and pill shapes only for read-only status.
- Shows all required states C1-C10 from the brief.

## V1 - Guided Review Console

Position: closest to PG v4 console patterns. The user sees the task sequence at the top, the editable form in the center, and visual/lock status in a stable right rail.

Strengths:

- Strongest match to existing AM-style dark console.
- Least risky to implement in Qt because it maps cleanly to the current two-column Capture code.
- More compact: empty optional sections collapse by default.
- Stage words are explicit: Draft / Ready / Locked / Replaced / Retired / Amended.

Risk:

- Still feels like a tool form, even though it is much clearer than current Capture.

Recommendation:

- Pick V1 if the goal is fastest safe implementation and closest Bible continuity.

## V2 - Decision Workbench

Position: treats Capture as reviewing one important decision document. The left rail is a health checklist that separates blockers from recommendations.

Strengths:

- Stronger teaching surface for Darrin: the screen explains what is safe, missing, or optional.
- Better for confidence before locking because readiness is always visible.
- More distinct from the current cluttered form.

Risk:

- Slightly more implementation work. The health rail needs real validation state wiring.
- Softer Stage vocabulary (`Proposed / Current / Changed`) may be less precise than V1's `Locked`.

Recommendation:

- Pick V2 if the priority is maximum clarity during live use and if a little extra implementation work is acceptable.

## Codex recommendation

Use V1 as the implementation base, but borrow V2's readiness checklist language for warnings and lock blockers. That gives the fastest path while preserving the clearest safety feedback.

## Verification performed

- Static count: both mockups contain 10 state badges, C1-C10.
- Static scan: no obvious white-background tokens were found.
- Shape scan: no action button was implemented as a pill class.
- Browser render: both files opened in local Edge through Playwright at 1280x800.
- Render evidence: viewport PNGs saved beside the HTML files.
