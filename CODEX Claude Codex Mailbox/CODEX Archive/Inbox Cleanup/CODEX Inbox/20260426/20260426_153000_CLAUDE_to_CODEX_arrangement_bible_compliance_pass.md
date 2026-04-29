# CLAUDE → CODEX: Unified Arrangement Canvas — v4.0 Bible compliance pass

**Tier: Extra-High.** Multi-section design synthesis — the largest and most consequential design job for v4.0. Output is a complete spec doc plus HTML mockups for every state of the unified canvas, at three widths. ~1000-2000 line response expected.

This is the v4.0 successor to today's AM Bible pass. Same depth, different module.

## Why this job

Per `PG_V4_MVP_PLAN.md` §2.2 (locked 2026-04-23):

> Template and freeform collapse into one concept. Every arrangement is a canvas. A "Full Mouth Series" is a saved arrangement with 18 pre-placed slots; a custom layout is a saved arrangement with user-placed images. Users save their own arrangements as reusable starting points. The Template Library becomes "My Saved Arrangements."
> 
> Architectural implication: one arrangement data model, one view module, one persistence path. Existing template_* code consolidates into the freeform_* code; the freeform surface becomes the canonical arrangement surface.

This ships in **Month 2 Week 5-6** of the v4.0 plan (2026-05-23 to 2026-06-06 window). Today's job is **the design pass that makes that implementation possible** — not the implementation itself.

The current state of the existing surfaces:
- `template_designer.py` — TemplateEditorDialog. Will be retired.
- `template_data.py` — template data model. Will be consolidated.
- `template_view.py` — template rendering. Will be consolidated.
- `freeform_view.py` — freeform canvas. Becomes the canonical arrangement surface.
- `dialogs.py` `TemplateLibraryDialog` — becomes `ArrangementLibraryDialog`.

PG has **no current users** (Darrin is the sole developer; v4.0 ships internally first). This means:
- Backwards-compatibility for the current template UX is NOT a constraint
- We can design what the unified canvas SHOULD be, not what's compatible with what is
- The Bible is the authority on visual + behavioral grammar
- The MVP plan is the authority on scope + sequencing

## The design problem

Design "the canonical arrangement surface for v4.0" — the single Arrange module that replaces both the template designer and the freeform view. Every relevant Bible section applies.

### What an arrangement is

An arrangement is a saved, named layout of zero or more images on a canvas. Pre-built arrangements ship as starting points (Full Mouth Series, Bitewing Series, Periapical Series, etc.). User-saved arrangements appear in the same library as the pre-built ones — the data model treats them identically.

### What the user does in the Arrange module

- Open an existing arrangement (pre-built or saved)
- Place images from the patient's filmstrip onto the canvas
- Move, resize, rotate images
- Save the current canvas as a new arrangement
- Export the arrangement (basic PNG/JPG/TIFF — distribution-quality exports are v4.1)
- Send the arrangement to the Present module for full-screen second-monitor display

### What's deliberately NOT in scope

- AI-suggested arrangements (v4.1+)
- Multi-patient arrangements (v4.1+)
- Arrangement sharing across users (v4.1+)
- Distribution-grade export (referral letters, insurance PDFs — v4.1+)
- Annotation tools beyond what the Edit/Review modules already provide

## Foundation reading (MANDATORY)

Read in order. Don't skim.

1. **`PG_DESIGN_BIBLE_v1.md`** — entire document. The binding contract. Pay particular attention to:
   - §1.1 Medical, not playful
   - §1.2 Restraint over flourish
   - §1.3 Clinical precision via monospace
   - §1.4 Every pixel earns its presence
   - §1.5 Every design feature reflects a true purpose
   - §1.6 Progressive disclosure (added today)
   - §2 Color system
   - §3 Typography
   - §4 Spacing scale
   - §6 Components — particularly §6.13 buttons, §6.21 workflow stepper, §6.22 module screen header
   - §7 Module-zone semantics
   - §8 Empty states
   - §13 Resize and persistence

2. **`PG_V4_MVP_PLAN.md`** — entire document. Pay particular attention to:
   - §2.2 Unified arrangement canvas (binding architectural decision)
   - §3 Tier 2 Heart of PG
   - §4 Month 2 Week 5-6 detail
   - §5.2 Arrangement extensibility (versioning, pluggable rendering)
   - §6 Hard gates (what's NOT in v4.0)
   - Appendix B file impact map

3. **`STRATEGY_NOTES.md`** — recent entries about the unified canvas decision and the Review module addition (2026-04-25).

4. **Existing arrangement code** (read as context for what to retire/consolidate):
   - `freeform_view.py` — the canonical surface for v4.0
   - `template_designer.py` — TemplateEditorDialog
   - `template_data.py`, `template_view.py`
   - `dialogs.py` `TemplateLibraryDialog`
   - `panda_gallery.py` — current entry points to template/freeform

5. **Today's AM Bible pass dispatch** at `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\20260426_150000_CLAUDE_to_CODEX_AM_bible_compliance_pass.md` and its amendment at `20260426_151000_CLAUDE_to_CODEX_AM_bible_pass_amendment.md` — the pattern for what this job's output should look like.

6. **`workflows/audit/DESIGN_AUDIT_v1.md`** Decisions log (2026-04-26) — the eight binding decisions made today. They apply.

## What I want from you

Six deliverables in one combined output.

### Part A — Comprehensive surface inventory

For the unified arrangement canvas, list every distinct user-visible surface:

- The Arrange module canvas itself (default state, with empty arrangement, with placed images)
- The arrangement library / picker (replaces TemplateLibraryDialog → ArrangementLibraryDialog)
- The save-arrangement flow (replacing SaveLayoutDialog)
- The arrangement properties panel (right-side)
- The arrangement filmstrip (bottom — image source for placement)
- All empty states (no arrangement open, no images in patient, no saved arrangements)
- All transient states (drag-in-progress, save-in-progress, export-in-progress)
- All error states (image load failure, save failure, etc.)

For each surface, identify which Bible sections govern it.

### Part B — Design specification (per surface)

For each surface in Part A, write what it should look like, behave like, and respond to.

For each, specify:
- Bible tokens used (no new tokens unless Part F amendment)
- Component grammar (which §6 components apply — including §6.21, §6.22 already shipped to AM)
- Behavior at three widths: narrow (~1000px Arrange canvas area), default (~1280px), wide (~1800px)
- Affordance states per §1.6 (which buttons are visible/hidden/disabled in which states)
- Acceptance test: §1.5 removal test for every sub-element
- Empty state per §8 (the "no arrangement open" state is loadbearing — it's the first thing a user sees)
- Transient/work-activity states per the new "activity indicator" pattern (likely Bible amendment from AM pass; coordinate with that pass)

The Arrange canvas itself is the centerpiece. Spec it deeply:
- Canvas chrome (rulers? grid? alignment guides? what earns its presence?)
- Image placement affordance (drag from filmstrip? click + place? both?)
- Image manipulation (move, scale, rotate handles — apply §6.13 grammar)
- Selection state (one image, multiple images, none)
- Snap behavior (to other images, to grid, to canvas edges)
- Zoom/pan (preserves Bible §1.2 restraint)
- Keyboard model (arrows, Esc, Delete, modifiers — coordinate with AM ESC-to-back rule)

### Part C — HTML mockups

Render your design pass at:
`C:\panda-gallery\workflows\design\pg_general_mockups\arrangement_canvas_v1.html`

Single self-contained HTML file. Include each surface from Part A at narrow / default / wide widths. Show:
- Canvas with empty arrangement
- Canvas with full-mouth-series pre-placed slots, no images placed yet
- Canvas with full-mouth-series partially populated
- Canvas with custom layout (user-placed images)
- Arrangement library / picker (with both pre-built and user-saved arrangements)
- Save-arrangement modal flow
- Empty states for each
- Transient states (drag-in-progress, save-in-progress)

Use Bible tokens. Use the §6.22 module screen header anatomy already shipped to AM. Use the workflow stepper if there's a multi-step flow that benefits from it. Use the activity indicator pattern (coordinate with AM Bible pass).

### Part D — Data model spec

The MVP plan requires a versioned arrangement data model (`arrangement_schema_version` field, pluggable renderers). Spec the data model:

- Schema for an arrangement (fields, types, constraints)
- Schema versioning approach
- Migration plan from current template_data + freeform persistence to unified
- Pluggable renderer contract (so PDF, presentation mode, exports all consume the same descriptor)
- AI metadata fields (per MVP §5.1 — empty in v4.0 but reserved)

Don't write the migration script. Spec what the script must do.

### Part E — Implementation sequencing

Recommend the order in which the unified arrangement canvas ships during Month 2 Week 5-6 of the MVP plan. Likely 4-6 batches:

- Data model + DB schema migration (Week 5)
- Arrangement library / picker (replacing TemplateLibraryDialog)
- Canvas core (drag, place, move, scale)
- Pre-built arrangements seed data
- Save/load/export flows
- Edge cases + reliability

For each batch:
- Ship name (e.g. v4.43, v4.44, v4.45 — guess at version numbers based on current v4.42.3)
- Surfaces touched
- Bible sections addressed
- Estimated LOC
- Dependencies (which batches must ship first)
- Acceptance gates (smoke + visual)

### Part F — Bible amendments needed

Some live findings or design needs may require Bible amendments:
- Arrangement-canvas-specific component (§6.x — likely a new "canvas" component spec)
- Possibly a new pattern for image-manipulation handles
- Possibly extensions to §6.13 (button grammar) for canvas tool affordances
- Coordinate with the AM Bible pass — if it adds an activity-indicator pattern, this pass uses it

For each amendment, propose the Bible text. Claude will apply unilaterally per Q3=A decision.

## Out of scope

- Don't fix `template_designer.py` — it's being retired. Don't propose patches to it.
- Don't write actual code or migration scripts — output is design + sequencing.
- Don't propose new modules. Arrange is one of the four locked v4.0 modules (Library / Arrange / Review / Present).
- Don't expand to v4.1+ features (AI suggestions, multi-patient, etc.).
- Don't redesign Library, Review, or Present — they get their own Bible passes later.
- Don't second-guess the v4.0 module decision — it's locked.

## Reply

Write your full design doc to:
`C:\panda-gallery\workflows\design\ARRANGEMENT_BIBLE_PASS_v1.md`

Reply summary (2-4 paragraphs + pointers at the design doc, the HTML mockup, and the data model spec) to:
`C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\20260426_HHMMSS_CODEX_to_CLAUDE_arrangement_bible_compliance_pass.md`

This is parallel to your three other in-flight jobs (DESIGN_AUDIT triage ordering — already returned; AM Bible compliance pass; AM Bible pass amendment). Run independently.

-- Claude
