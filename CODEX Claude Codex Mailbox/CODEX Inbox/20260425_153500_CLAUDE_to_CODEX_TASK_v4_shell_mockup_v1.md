# TASK: PG v4.0 UI Shell Mockup v1

Generated: 2026-04-25 15:35:00 -07:00
From: Claude
To: Codex
Status: Response Requested (deliverable: HTML/CSS mockup)
Recommended tier: Extra-High
Sequencing: After current task `20260425_125500_..._instruction_pane_ux_v2_spec.md` (Pane UX) is complete. The previous task `20260425_142500_..._tester_report_roundtrip_v1_spec.md` is **CANCELLED** — skip it.

## Summary

Author the v4.0 UI shell mockup as a self-contained HTML/CSS file at `C:\CODEX PG\CODEX PG Main UX Flow Maps\v4_shell_mockup_v1.html`.

This is **the** Tier 1 Week 1 deliverable from `PG_V4_MVP_PLAN.md`. The entire v4.0 main-window structure is designed as a coherent whole here, iterated until Darrin approves, and then rebuilt in a single landing commit during Tier 1 Week 2 (CC). Per MVP plan §2.3 ("branch-and-burn UI shell"): no incremental shell changes, one cohesive design.

The Month 1 deliverable v3.90 is blocked on this mockup. Get it right; iteration is expected.

## What Codex is designing

The PG main window after the v4.0 shell rewrite. Every aspect of the chrome and panel layout — module tabs, toolbar, side panels, status bar, visual language — rendered as static HTML/CSS that Darrin can open in Chrome and react to.

### Locked structural elements (do NOT redesign)

These come from `PG_V4_MVP_PLAN.md` and `PG_TRUTH_v1.md`. They're inputs, not decisions to revisit:

- **Four top-level modules:** Library / Arrange / Review / Present.
- **Module bar:** top of window, prominent, always visible. (Lightroom-style placement — see UX_DESIGN_SESSION_Apr19.md §2 viewer-first reorient.)
- **Compare lives as a Review submode**, not a top-level module. Compare is reachable via multi-select in Library + a `Compare` action that opens A/B inside Review. Compare visual treatment per existing `v4_0_comparison_mockup.html`.
- **Vocabulary noun:** "Mount" (locked 2026-04-25). User-facing label for saved arrangements. Both Template-flavor and Freeform-flavor saved canvases are Mounts. The Library's Templates section becomes the Mounts section. The Template Library dialog becomes the Mount Library dialog. Code-level `Template` identifiers stay until F3 rename ships separately.
- **Tool placement:** right-side panel for tools (LR/PS convention). Left side hosts the patient list.
- **Keyboard shortcuts:** `Ctrl+1` Library, `Ctrl+2` Arrange, `Ctrl+3` Review, `Ctrl+4` Present. `Ctrl+Shift+P` toggles Presentation mode.
- **Mockup authority:** Darrin alone approves. Rebecca / external clinician feedback is consultation-style at Month 1 end, no veto power on the mockup itself.

### Open design decisions Codex makes in the mockup

These are the actual design work. Codex proposes; iteration with Darrin refines.

1. **Visual language.** PG's existing dark theme (`#1a1a2e` background, cream `#e8d9c0` text, peach `#e8a87c` accent, chrome border `#2a2a3e`) extended into the new shell. Type hierarchy, spacing rhythm, button style, focus indicator, hover state. Should read as a coherent system, not a collection of widgets.
2. **Module bar visual treatment.** Top-bar with four labeled tabs. Active state, hover state, keyboard-focus state. Spacing, font, accent. How prominent? How does the active module read at a glance?
3. **Right-side tool panel.** Per-module content. Library shows filters / sort / view-mode toggles. Arrange shows mount controls (slot tools, layout helpers, save-as-Mount). Review shows the existing image-edit controls (mostly inheriting from `v4_0_edit_image_mockup.html` per MVP plan Month 2 Week 6). Present shows minimal chrome — just connection status / display selection. Define a panel-section pattern (header + collapsible body) and apply it consistently.
4. **Left-side patient panel.** Stays similar to today, fits new shell. Patient search, Saved-Arrangements (Mounts) library, archived-toggle. Width, density, divider treatment vs today.
5. **Central canvas area.** Different per module. In Library: thumbnail grid. In Arrange: the unified canvas (Template-flavor and Freeform-flavor share this surface; the difference is whether slots are pre-placed). In Review: single image with adjustment overlay. In Present: kiosk-style. Suggest layouts that show the central area's shape clearly even though feature implementation is later.
6. **Status bar / chrome.** Bottom of window. What does it show? Current patient, current Mount name, zoom level, image dimensions, save state. Or is it minimal?
7. **Loading / empty states for each module.** First-launch (no patient selected) per BUGS.md #114. No images in Library. Empty Arrange canvas. Single-image-not-selected Review. No second monitor for Present. Each gets an empty-state treatment.
8. **Module-switch behavior visualization.** Show how a user knows their patient/image/Mount selection persists across module switches. Visual continuity is critical for Tier 1's mental-model clarity.
9. **Active-window focus indicator** (BUGS.md #131). The shell mockup needs to incorporate the focus indicator design — pick one of the two options proposed in #131 (subtle border accent vs tinted unfocused window) or propose a third option specific to the new shell. CC's mockup `focus_indicator_v1.html` (in flight as part of v4.37 batch) explores this in isolation; use that as input if it's landed by the time this task starts.

### Layout breakpoints

Render the mockup at three widths to verify responsiveness:

- **1920×1080** — typical working monitor, full chrome
- **1366×768** — laptop floor, must remain functional
- **3840×2160** — 4K, ensure no awkward stretching

For each breakpoint, render every module (Library / Arrange / Review / Present) — that's 12 view configurations. Use a multi-page or tabbed HTML structure if needed. Don't compromise depth per view to fit them all on one scroll.

### Mockup features required

- **Self-contained.** All CSS inline or in a single `<style>` block. No external assets, no images that aren't inlined or SVG.
- **Browser-openable.** Chrome on Windows is the target. Verify it renders.
- **Annotated.** Use `<!-- comment -->` blocks throughout to explain design decisions and surface open questions.
- **Comparable.** Where two design options exist (e.g., module bar at top vs left rail), render both side-by-side at one breakpoint with a clear "Option A / Option B" label.
- **No invented features.** If the MVP plan doesn't include a feature in v4.0 scope, don't show it in the mockup. Specifically: no AI features, no installer indicators, no DICOM widgets, no compliance badges. v4.0 ships without those.

### Specific things to surface as open questions

End the mockup file with an `<aside>` of open questions for Darrin decision:

- Module bar position: top-bar (Lightroom-style) vs left-rail-tabs (DaVinci Resolve-style)?
- Mount library: dialog (today's pattern) vs first-class panel slot in Library module's left side?
- Review submode toggle (Compare vs single-image): tab-within-Review vs action-bar button vs URL-style toolbar segment?
- Status bar: minimal (just save state) vs informative (patient/Mount/zoom/dimensions)?
- Module-switch persistence: explicit indicator (e.g., breadcrumb showing patient + Mount + module) or implicit (selection just persists silently)?

## Inputs Codex should read first

In recommended order:

1. `C:\panda-gallery\PG_V4_MVP_PLAN.md` (the plan — full read)
2. `C:\panda-gallery\workflows\audit\PG_TRUTH_v1.md` (locked module set + Mount + §9 resolutions)
3. `C:\panda-gallery\UX_DESIGN_SESSION_Apr19.md` (April-19 stakeholder demo, especially §1 and §2 viewer-first reorient)
4. `C:\panda-gallery\COMPETITIVE_ANALYSIS.md` (PG competitive context)
5. `C:\panda-gallery\styles.py` (existing dark-theme palette and QSS — Codex should match this exactly in the mockup CSS)
6. `C:\CODEX PG\CODEX PG Edit Module UX\CODEX_REVIEW_MODULE_RADIOGRAPH_UX_SPEC_v2.md` (Review module structure — the mockup must accommodate this)
7. `C:\CODEX PG\CODEX PG Main UX Flow Maps\CODEX_PG_USER_PROCESS_STREAMLINING_MAP_v2.md` (user-process flows — the mockup must feel right for these)
8. `C:\CODEX PG\CODEX PG Main UX Flow Maps\CODEX_TEMPLATE_STUDIO_OVERHAUL_SPEC_v2.md` (Template Studio → mount library affordance)
9. `C:\panda-gallery\workflows\design\v4_0_comparison_mockup.html` (Compare submode visual reference — already approved)
10. `C:\panda-gallery\workflows\design\v4_0_edit_image_mockup.html` (Review module image-edit visual reference — already approved)
11. `C:\panda-gallery\workflows\design\focus_indicator_v1.html` (#131 focus indicator — if landed by start of this task; CC v4.37 batch is in flight)
12. `C:\panda-gallery\workflows\design\empty_state_v1.html` (#114 empty-state options — if landed by start of this task; CC v4.37 batch is in flight)

## Constraints

- **Read-only on `C:\panda-gallery\`.** Output spec to `C:\CODEX PG\CODEX PG Main UX Flow Maps\v4_shell_mockup_v1.html`. No code changes.
- **Mockup, not implementation.** Static HTML/CSS that demonstrates the design. CC builds the actual Qt widgets in Tier 1 Week 2 from the approved mockup.
- **Coherent system.** This is the v4.0 visual language defined for the first time. It must feel intentional. Spacing, typography, color usage all follow defined rules. Don't ad-hoc each module.
- **Match existing palette exactly.** Codex must use the dark-theme hex values from `styles.py`. Introduce new tokens only when the existing palette doesn't cover the case (and surface those as open questions).
- **Branch-and-burn implies high commitment to the mockup.** Once approved, CC rebuilds the main window to match. So small flaws compound. Spend cycles getting it right.

## Iteration model

This task ships v1. After Darrin reviews:
- If approved → Tier 1 Week 2 dispatch to CC for shell build.
- If revisions needed → Codex authors v2 with deltas. Don't rewrite v1 wholesale; deliver targeted changes.
- If fundamental disagreement → discussion in chat first; v2 dispatch only after re-alignment.

Anticipate v2 and possibly v3. Build v1 to be revisable.

## Approval Boundary

Spec authoring only. No implementation. Output stays in `C:\CODEX PG\CODEX PG Main UX Flow Maps\`. Claude reviews the mockup before surfacing to Darrin per generator+critic pattern. Darrin approves. Then CC dispatches for build.

— Claude
