# TASK: PG v5 Mockup System — Phase 1 (Design System + Review module + Shell + Template editor dark)

Generated: 2026-04-25 17:30:00 -07:00
From: Claude
To: Codex
Status: Response Requested (deliverable: 1 design-system reference + 3 mockup files)
Recommended tier: **Extra-High**
Sequencing: After current task `20260425_125500_..._instruction_pane_ux_v2_spec.md` (Pane UX) is complete. Previous tasks `20260425_142500_*` (Tester Report) and `20260425_153500_*` (UI shell mockup v1) are **CANCELLED** — skip them.

---

## Summary

Phase 1 of the v5 mockup library locks the v4.0 visual design system and ships the four highest-priority new artifacts. Phase 2 (CC, separate dispatch after Darrin's `go` on Phase 1) handles the mechanical follow-on work.

**The locked brief lives at `C:\panda-gallery\workflows\design\v4_0\BRIEF_v5_DRAFT_for_review.md`.** Read it first. Treat it as inviolable input. Every design token, vocabulary rule, and design rule in the brief is locked — do not re-debate them.

---

## Phase 1 deliverables

All output to a new directory: **`C:\panda-gallery\workflows\design\v5\`**. Codex creates the directory.

### 1. `v5_DESIGN_SYSTEM.md` — normative design system reference

The authoritative document that every future mockup, every CC implementation, and every Codex spec cites for design tokens and rules.

**Required sections:**

- **Frontmatter** — name, version (v5.0), date, status (LOCKED), inheritance source (`v4_0\v4_0_palette_typography.html` 5★-approved + `v4_0\v4_0_edit_image_mockup.html` "GORGEOUS"-approved)
- **Surface palette** — five-step navy scale, with hex + token name + role, restated from brief
- **Border, text, accent, semantic palettes** — restated from brief
- **Typography** — two-family system explained (Segoe UI = readable, Cascadia Mono = clinical precision). Restate the rule "mono is for numbers/IDs/dates/filenames/dimensions/shortcuts; not prose." Include the seven-row specimen table from `v4_0_palette_typography.html` (Display/Heading 2/Heading 3/Body/Small/Mono/Caption).
- **Spacing, radius, motion** — restated from brief.
- **Mode-zone colors** — Library `#9a9aa8`, Arrange `#e8a87c`, **Review `#5fa0a8` (locked 2026-04-25)**, Present `#7fb069`. Applied at: status-bar mode label color, active module-tab underline, optional subtle canvas-surround tint.
- **Sensor color codes** — five sizes, restated from `constants.py` per brief.
- **Vocabulary rules** — Mount as the noun; module set Library/Arrange/Review/Present; Compare as Review submode; keyboard shortcuts Ctrl+1/2/3/4 + Ctrl+Shift+P.
- **8 design rules** — restated from brief with one-paragraph justification each.
- **Component grammar reference** — extract from `v4_0_edit_image_mockup.html`: section-header pattern (label + arrow + optional badge), button treatment (one solid peach primary per screen, others transparent + 1px border, etc per STYLE.md §6), focus-ring pattern, hover-state pattern, slider anatomy reference (cite `v4_0_right_panel_study.html`), tab styling. Reference but do not duplicate the source files; cite.
- **HTML preview block at the end** — render every token as a swatch + every type style as a specimen, in one `<style>` + `<body>` section. Open `v5_DESIGN_SYSTEM.md` in a browser-friendly Markdown viewer (or paired `.html`) and the visuals confirm the prose. If a paired `.html` makes more sense than embedded, ship `v5_DESIGN_SYSTEM.md` (prose) AND `v5_DESIGN_SYSTEM_preview.html` (visual).

**Critical authoring rule:** before writing this file, Codex reads every file in `C:\panda-gallery\workflows\design\v4_0\`. If `v4_0_edit_image_mockup.html` and `v4_0_palette_typography.html` disagree on any token value (button hex, border-radius, type size, etc.), surface the discrepancy explicitly in the design system doc. Pick the value from `v4_0_palette_typography.html` (it's the locked tokens reference per the 5★ rating) and call out the override.

### 2. `v5_review_mockup.html` — Review module (the genuine gap)

The Review module — single-image inspect/adjust/annotate surface — does not yet exist as a mockup. Module set was 3 (Library/Arrange/Present) when v4_0 was authored 2026-04-23; expanded to 4 with Review added 2026-04-25.

**Required content:**

- **Single-image state.** Inherit component grammar from `v4_0_edit_image_mockup.html` (which is the existing Edit-image mockup; that's effectively the Review module's solo-image surface, just with the wrong label). The visual language transfers directly. Apply Review mode-zone color `#5fa0a8` to status bar mode label and module tab underline.
- **Compare submode.** Multi-select in Library + Compare action opens A/B inside Review. Render Compare submode at A/B with sync zoom + before-after slider per `v4_0_comparison_mockup.html`. Submode toggle: a small action-bar button or tab-within-module switching between "Single image" and "Compare" — Codex proposes which feels right; surface as open question if uncertain.
- **Tutorial-tone empty state** for "no image selected" (e.g., when entering Review from Library without a selection). Voice: welcoming, walkthrough, not infantilizing — "Select an image from the filmstrip to begin reviewing" or stronger. Cite the tutorial tone established by Darrin's earlier review of CC's `empty_state_v1.html` Option B.
- **1920×1080 viewport.** Single breakpoint for sub-screens per the brief.

### 3. `v5_shell_overview.html` — master four-module shell

A single file showing the complete v4.0 chrome — title bar with brand + module tabs + global actions, status bar with mode-zone label, optional bottom filmstrip per Library. The four modules render as four breakpoint sections stacked vertically:

- **Library** active state — chrome shows Library tab underlined `#9a9aa8`, status bar mode "LIBRARY" in `#9a9aa8`, central area shows a stub of the Library thumbnail grid
- **Arrange** active state — Arrange tab `#e8a87c`, status bar "ARRANGE" in `#e8a87c`, central area shows a stub of the unified Mount canvas
- **Review** active state — Review tab `#5fa0a8`, status bar "REVIEW" in `#5fa0a8`, central area shows a stub of single-image inspect surface
- **Present** active state — Present tab `#7fb069`, status bar "PRESENT" in `#7fb069`, central area shows a stub of presentation chrome (or "Press Ctrl+Shift+P to start" prompt)

Each section labeled clearly. The chrome itself is identical across the four; only the module tab + status bar mode label + central stub change. **The point of this mockup is to demonstrate consistency:** four modules, one chrome, one app.

**Module-switch persistence visualization.** In each section, show a status-bar fragment indicating "Patient: Adams, Deborah · Mount: Full Mouth Series — Mar 14" persisting across module switches. Optional breadcrumb pattern.

**Three breakpoints.** Render the four sections at 1440×900 (laptop floor), 1920×1080 (default), 3840×2160 (4K). Three viewport widths × four modules = 12 view configurations. Use a tabbed or sectioned HTML structure if needed; don't compromise depth per view.

### 4. `v5_template_editor_dark.html` — replaces white-background Template editor

`v4_0_template_editor_mockup.html` got 4★ with comment "don't like white background." Replace it: same content, dark canvas. The original used a white "sheet" metaphor for the template-design surface (8×5 in @ 300 DPI). v5 keeps the metaphor but the sheet is dark canvas-colored `#14141f` with `#22223a` raised-pane areas for slot outlines. Slot borders use `#2a2a3e`. Active/selected slot uses peach `#e8a87c` border with `#e8a87c @12%` accent-soft fill.

Rename "Template editor" to **"Mount Designer"** in user-facing copy throughout (per the locked Mount vocabulary). Same layout, same controls, same workflow — dark surface, Mount vocabulary.

---

## Open questions Codex must surface (do not invent answers)

1. **Review submode toggle treatment** — tab-within-module ("Single" / "Compare") vs action-bar button ("→ Compare") vs URL-style toolbar segment? Propose; mark as open.
2. **Module bar position** — top-bar (Lightroom-style, what `v4_0_shell_mockup_v1_library.html` uses) vs left-rail-tabs (DaVinci Resolve-style)? The locked brief says "top-bar" implicitly via the existing shell, but if Codex sees a strong reason to revisit, surface as a Phase 1 v2 candidate (do not pick unilaterally).
3. **Status bar density** — minimal (just save state + mode + version) vs informative (add patient + Mount + zoom + dimensions)? Existing shell mockup leans informative; surface for Darrin confirmation.
4. **Module-switch persistence indicator** — implicit (selection just persists silently) vs explicit breadcrumb showing "Patient → Mount → Module"? Propose default; mark as open.
5. **`v5_DESIGN_SYSTEM.md` paired `.html` preview** — embedded in the .md, or separate `v5_DESIGN_SYSTEM_preview.html` companion? Codex picks; explain choice.

End the brief's `v5_DESIGN_SYSTEM.md` and the three mockup files with an "Open questions" section listing these for Darrin decision.

---

## Inputs Codex MUST read

In recommended order. Read them all before authoring; do not skip.

1. **`C:\panda-gallery\workflows\design\v4_0\BRIEF_v5_DRAFT_for_review.md`** — the locked brief (despite "DRAFT_for_review" in filename, the file is now LOCKED per Darrin's 2026-04-25 sign-off; first line confirms LOCKED status)
2. `C:\panda-gallery\workflows\design\v4_0\README.md` — directory map
3. `C:\panda-gallery\workflows\design\v4_0\SESSION_NOTES_2026-04-23.md` — narrative history of the v4_0 mockup library
4. `C:\panda-gallery\workflows\design\v4_0\v4_0_palette_typography.html` — **5★ locked tokens reference**
5. `C:\panda-gallery\workflows\design\v4_0\v4_0_edit_image_mockup.html` — **"GORGEOUS"-approved binding visual vocabulary**
6. `C:\panda-gallery\workflows\design\v4_0\v4_0_splash_mockup.html` — 5★, brand reference
7. `C:\panda-gallery\workflows\design\v4_0\v4_1_preferences_mockup.html` — 5★, dialog/tab pattern reference
8. `C:\panda-gallery\workflows\design\v4_0\v4_0_shell_mockup_v1_library.html` — 4★, current shell mockup; informs `v5_shell_overview.html` (use as starting point, strip the appended designer's-notes section, unify with v5 design system)
9. `C:\panda-gallery\workflows\design\v4_0\v4_0_arrange_canvas_mockup.html` — 4★, central canvas pattern reference
10. `C:\panda-gallery\workflows\design\v4_0\v4_0_comparison_mockup.html` — 4★, Compare submode visual
11. `C:\panda-gallery\workflows\design\v4_0\v4_0_present_mockup.html` — 4★, Present mode reference
12. `C:\panda-gallery\workflows\design\v4_0\v4_0_template_editor_mockup.html` — 4★ with "don't like white background"; v5 replacement is in scope
13. `C:\panda-gallery\workflows\design\v4_0\v4_0_right_panel_study.html` — 4★, slider anatomy + tool inventory; cite from design system
14. `C:\panda-gallery\workflows\design\v4_0\v4_0_library_empty_mockup.html` — 4★, three empty-state variants; informs Phase 2 but useful Phase 1 context
15. `C:\panda-gallery\workflows\design\v4_0\v4_0_menu_reference.html` — 3★ "where does this go?"; Phase 2 will replace this with menus-in-context, but Phase 1 design system can cite menu treatment
16. `C:\panda-gallery\workflows\design\v4_0\vocabulary_notes.md` — chat-log capture from 2026-04-23 design session
17. `C:\panda-gallery\workflows\design\v4_0\PG_V4_CUSTOMIZATION_PLAN.md` — Tier 1/2/3 customization plan
18. `C:\panda-gallery\PG_V4_MVP_PLAN.md` — v4.0 MVP plan (module set, ship gate, Tier 1/2/3 sequencing)
19. `C:\panda-gallery\workflows\audit\PG_TRUTH_v1.md` — locked facts (module set, Mount vocabulary, §9 keyboard shortcuts)
20. `C:\panda-gallery\styles.py` — current QSS palette (verify v5 design system matches what ships in code today)
21. `C:\panda-gallery\STYLE.md` — button rules (§6 referenced by design system)

---

## Constraints

- **Read-only on `C:\panda-gallery\`.** Output to `C:\panda-gallery\workflows\design\v5\` — Codex authoring within `workflows/design/v5/` is allowed per repo standing rule that `workflows/design/**` is the sanctioned design-output location.
- **Inherit, don't invent.** Every design token in v5 traces back to the locked brief. If Codex sees a need for a new token (e.g., a hover-state hex not yet defined), propose in the design system doc with rationale; do not silently introduce.
- **Visual coherence is the primary deliverable goal.** Phase 1 success = Darrin opens any of the 4 deliverables in Chrome, scrolls through, and feels "this is the same app." If even one mockup feels inconsistent with the others, Phase 1 isn't done.
- **No designer's-notes mixed into deliverables.** Per design rule 4. If notes are needed, separate companion `.md` file.
- **No invented features.** No AI features, no installer chrome, no DICOM widgets, no compliance badges. v4.0 ships without those.

---

## Iteration model

This task ships v1. After Darrin reviews:

- If approved → Phase 2 (CC) dispatched, Phase 1 inputs lock for downstream consumers.
- If revisions needed → Codex authors v2 with deltas. Don't rewrite v1 wholesale; deliver targeted changes.
- If fundamental disagreement → discussion in chat first; v2 dispatch only after re-alignment.

Anticipate v2 and possibly v3. Build v1 to be revisable.

---

## Approval Boundary

Spec authoring only. No implementation. Output stays in `C:\panda-gallery\workflows\design\v5\`. Claude reviews v1 per generator+critic pattern before surfacing to Darrin for `go`. After Darrin's `go`, Phase 2 dispatches to CC.

— Claude
