# CODEX -> CLAUDE: AM Screen B v2 mockup complete

## Deliverable

Created:

`C:\panda-gallery\workflows\design\pg_general_mockups\AM_screen_b_v2_codex.html`

Render-check artifact:

`C:\CODEX PG\CODEX AM Screen B v2 Render Check 1440x1200.png`

## Read before designing

- `workflows/design/AM_UX_REDESIGN_BRIEF_v1.md`
- `workflows/design/PG_DESIGN_BIBLE_v1.md`
- `workflows/design/v4_0/v4_0_edit_image_mockup.html`
- `audit_module/audit_module_window.py`
- `instruction_pane.py` (`_ChecklistRow`, `ChecklistStepView`)
- `BUGS.md`
- `workflows/audit/audit_issue_state.json` for real #129 triage data

## What the mockup contains

Seven vertically stacked static states:

1. Bug opened, ready to triage
2. Triage running
3. Triage complete, 5 gaps unresolved
4. Mid-resolution, decision saved
5. All gaps resolved
6. Reclassify path
7. Status pane examples

## Key design decisions

- Replaced the dense right-column button stack with a guided workflow: top step guidance, status pane, scan list, selected-gap action area.
- Kept one visually primary peach action per state. Other actions remain visible but dimmed or neutral.
- Used real #129 gap data for the five-gap flow so the mockup reflects actual AM output instead of invented placeholder content.
- Kept "readiness gap" as a surface label, but paired it with visible help affordances and plain-language tooltip copy.
- Replaced "Move - Feature" with "File as feature request" and showed the destination-confirmation dialog in context.
- Moved completion/error feedback into a persistent status pane and larger visible toast treatment for file-writing actions.

## Trade-offs considered

- I did not preserve the current fixed 360px right column. That layout is the core source of the cramped UX. The mockup gives Screen B a wider assistant workspace while still keeping the left bug content readable.
- I avoided per-row action buttons in the main gap list. Rows are now for scanning and selecting; the selected-gap footer owns actions. This is a deliberate answer to the "buttons within a window" confusion.
- I kept the UI restrained instead of decorative. "Magical" here is meant as confidence, obvious next action, and no silent state changes.

## Verification

- Confirmed 7 states are present.
- Confirmed no `<script>` or JavaScript.
- Confirmed no obvious forbidden palette values (`#fff`, `#ffffff`, `#f5f5f5`, `#eee`, `#000`).
- Confirmed each state has at most one `.btn.primary` visual primary action.
- Rendered with headless Edge at 1440x1200. The first state, annotations, top guidance, status pane, and disabled controls render cleanly.

## Open questions for Darrin

- Should AM Screen B remain a standalone Audit window, or eventually become a standard PG module shell?
- Should reclassification be one "Reclassify..." chooser or two direct actions when the classification strongly suggests one path?
- Should "Record decision" always append to BUGS.md, or should AM offer an explicit "sidecar only" decision path for temporary notes?
