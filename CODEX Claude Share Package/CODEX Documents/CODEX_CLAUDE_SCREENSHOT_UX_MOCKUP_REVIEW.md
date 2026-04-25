# CODEX Review: Claude Screenshot UX Mockups for Dental Imaging

Generated: 2026-04-24
Reviewer: Codex
Scope: Claude's Panda Gallery UX mockups in `C:\panda-gallery\workflows\design`
Output folder: `C:\CODEX PG\CODEX Claude UX Mockup Review`

## Executive Opinion

Claude's mockups are directionally very strong. They are not just pretty screens. They show real product thinking: persistent context, visible state, bottom filmstrips, module-level workflows, always-reachable action bars, dental series mounting, clinical comparison, non-destructive adjustments, and a right-panel model that borrows the best of Lightroom without blindly copying it.

My opinion: this is the right design direction, but it needs to become more explicitly dental. The Adobe influence should be structural, not cosmetic. Panda Gallery should borrow Lightroom's image workflow architecture and Photoshop's tool clarity, then translate both into dental concepts: radiographs, intraoral/extraoral photos, FMX mounting, tooth/region metadata, before/after treatment review, referral exports, patient-safe presentation, and evidence/audit trails.

The strongest mockups are:

1. `v4_0_arrange_canvas_mockup.html` - best dental-specific screen; this should become the Mount/Series workflow.
2. `v4_0_edit_image_mockup.html` - strong Lightroom/Photoshop hybrid for image review and annotation.
3. `v4_0_comparison_mockup.html` - excellent clinical before/after concept.
4. `v4_0_template_editor_mockup.html` - very applicable to dental radiograph templates.
5. `v4_0_right_panel_study.html` - the most mature design rationale; keep this as a reference document.
6. `instruction_pane_redesign_v1.html` and `pane_action_bar_v2_mockup_v1.html` - strong for internal testing UX, but should stay separate from the clinical imaging UI.

The biggest risk: the app could become an Adobe-looking interface that is visually sophisticated but too dense for fast dental use. The design must keep the image and patient context dominant, keep dental actions named in dental language, and avoid filling the right panel with generic photo controls that most dentists will not use.

In one sentence:

Panda Gallery should feel like Lightroom's organization and review discipline plus Photoshop's focused tools, but with dental imaging vocabulary, clinical defaults, and fewer distractions.

## What I Reviewed

I rendered 32 local HTML mockups into screenshots using Microsoft Edge and reviewed the resulting contact sheets plus key individual screens.

Rendered screenshots:

- `C:\CODEX PG\CODEX Claude UX Mockup Review\CODEX rendered screenshots`
- `C:\CODEX PG\CODEX Claude UX Mockup Review\CODEX_recent_mockups_contact_sheet.png`
- `C:\CODEX PG\CODEX Claude UX Mockup Review\CODEX_v4_0_mockups_contact_sheet.png`
- `C:\CODEX PG\CODEX Claude UX Mockup Review\CODEX_all_claude_mockups_contact_sheet.png`

Primary mockups reviewed:

- `113_avatar_rewrite_mockup_v1.html`
- `action_bar_mockup_v1.html`
- `checklist_mockup_v1.html`
- `checklist_mockup_v2.html`
- `dialog_sizing_v1.html`
- `focus_indicator_v1.html`
- `instruction_pane_redesign_v1.html`
- `pane_action_bar_v2_mockup_v1.html`
- `pane_fail_panel_mockup_v1.html`
- `pane_fail_panel_mockup_v2.html`
- `region_capture_v1.html`
- `review_dialog_sizing_v1.html`
- `single_expected_mockup_v1.html`
- `single_expected_mockup_v2.html`
- `stats_row_mic_bar_mockup_v1.html`
- `v3_71_ui_vocabulary.html`
- `v4_0/INDEX.html`
- `v4_0/v4_0_ALL.html`
- `v4_0/v4_0_arrange_canvas_mockup.html`
- `v4_0/v4_0_comparison_mockup.html`
- `v4_0/v4_0_edit_image_mockup.html`
- `v4_0/v4_0_INDEX.html`
- `v4_0/v4_0_library_empty_mockup.html`
- `v4_0/v4_0_menu_reference.html`
- `v4_0/v4_0_palette_typography.html`
- `v4_0/v4_0_present_mockup.html`
- `v4_0/v4_0_right_panel_study.html`
- `v4_0/v4_0_shell_mockup_v1_library.html`
- `v4_0/v4_0_splash_mockup.html`
- `v4_0/v4_0_template_editor_mockup.html`
- `v4_0/v4_0_toolbar_reference.html`
- `v4_0/v4_1_preferences_mockup.html`

## The Adobe Question

You are right to look at Lightroom and Photoshop. They solved several problems that dental imaging also has:

- organizing large image libraries,
- keeping image context visible,
- presenting thumbnails without losing the active image,
- separating modes without opening many windows,
- editing non-destructively,
- preserving before/after comparison,
- making tools discoverable,
- allowing fast keyboard-driven work,
- using panels for advanced controls without cluttering the canvas.

But dental imaging is not general photography. The clinical task is not to make art. The clinical task is to see, compare, explain, document, and export evidence.

So the design rule should be:

Copy Adobe's workflow architecture, not Adobe's full complexity.

## What To Borrow From Lightroom

Borrow these aggressively:

1. Module-based workflow.
   Use top-level modes for distinct mental tasks. The user should know whether they are organizing, mounting, reviewing, comparing, or presenting.

2. Filmstrip.
   A persistent bottom filmstrip is highly applicable. It gives quick patient-history navigation without hiding the active image.

3. Right-side adjustment panels.
   The right panel works well for histogram, enhancement, metadata, notes, tags, and export state.

4. Collapsible sections.
   A dentist should not see every advanced tool all the time. Collapsible panels are the right compromise.

5. Presets.
   Dental presets are very valuable: PA endo, BW caries, perio bone, intraoral photo, smile photo, insurance export, referral export.

6. Copy / Paste / Previous adjustments.
   This is directly useful for full-mouth series where several images need the same radiograph enhancement.

7. Before / after comparison.
   Dental users need this constantly: pre/post treatment, different dates, enhanced/original, radiograph over time.

8. Non-destructive edits.
   The original clinical image must remain intact. All enhancements and annotations should be reversible or stored as overlays/metadata.

9. Metadata-driven filtering.
   Tooth, region, image category, visit date, sensor type, series, and tags matter more than generic star ratings.

10. Keyboard shortcuts.
   Power users will value them, but they should accelerate workflows rather than become required knowledge.

## What To Borrow From Photoshop

Borrow these selectively:

1. Left vertical tool strip.
   This is excellent for Review/Edit and Mount modes. It should not be visible everywhere.

2. Tool-specific options.
   When Crop, Measure, Brush, Text, or Annotation is selected, show only the relevant settings.

3. Layers for annotations.
   Annotation layers are useful: labels, arrows, circles, measurements, before/after notes.

4. History panel.
   Useful, but keep it simpler than Photoshop. Dentists need confidence, not a full creative editing stack.

5. Swatches and recent colors.
   Useful for annotation colors, especially if the practice uses consistent colors for endo/perio/referral notes.

6. Brush size and opacity controls.
   Useful for annotations. Less important than image clarity tools.

7. Crop and measurement tools.
   Highly relevant, especially if calibration is supported.

## What Not To Copy From Adobe

Do not copy these:

1. Too many modules.
   Adobe can afford many modes. Panda Gallery should avoid making the dentist choose among too many abstractions.

2. Raw-photo terminology.
   Avoid making dentists think about generic camera development unless it maps to a clinical outcome.

3. Dense generic menus.
   Menus should exist, but the main path should be visible through the interface.

4. Complex layer blending.
   Annotation layers yes. Photoshop-like blending modes no, at least not early.

5. Tone curve as a core feature.
   A small percentage of users may want it. It should be deferred.

6. Decorative visual polish before clinical speed.
   The splash screen and brand polish are nice, but productivity screens matter more.

7. Hidden state.
   Dental users must know which patient, which date, which image, whether they are viewing original/enhanced, and whether annotations are on.

8. Low-contrast text.
   Dark UI is right for radiographs, but metadata and buttons must remain readable on office monitors.

## Recommended Panda Gallery Information Architecture

Claude's v4.0 module direction is good, but I would adjust the module names and hierarchy to be more dental-specific.

Recommended top-level modules:

1. Library
   Patient list, image import, image history, search, filtering, tags, exports, and archive.

2. Mount
   Formerly Arrange. This should be dental language. It handles FMX, bitewing sets, PA series, template slots, sensor placement, slot filling, missing images, and series export.

3. Review
   Formerly Edit/Loupe. This is where a single image is inspected, enhanced, annotated, measured, categorized, and prepared for clinical use.

4. Compare
   Before/after, date-to-date, original/enhanced, side-by-side, stacked, split swipe, and clinical note comparison.

5. Present
   Patient-safe or consult-safe viewing mode for chairside explanation, external display, referral conversation, or case presentation.

Testing and Audit should not be a peer of these clinical modules. It should remain in developer/tester workflow surfaces unless the Audit MVP becomes a separate app/workspace.

My strongest naming recommendation: rename `Arrange` to `Mount` or `Mount Series`. In dentistry, `Arrange` is generic, but `Mount` immediately communicates radiograph series assembly. If the module also handles photo boards later, use `Mount` as the compact label and `Series Mount` in tooltips or headers.

## Global Layout Opinion

The global layout should keep these stable regions:

- Left: patient or tool context, depending on module.
- Center: image, series, grid, or presentation canvas.
- Right: metadata, adjustments, notes, selected item properties, and export/review actions.
- Bottom: filmstrip or series timeline when image navigation matters.
- Top: module tabs, patient breadcrumb, global import/export/present actions.

This mirrors Lightroom enough to be learnable, but it should be more clinically explicit.

Important: avoid competing thumbnail zones. The v4 shell sometimes implies both a top filmstrip and a bottom filmstrip. Pick one persistent filmstrip location for image navigation. My recommendation is bottom filmstrip for Review, Compare, Mount, and Present control views. Library can use a central grid instead.

## Screen-by-Screen Review

### v4.0 Shell / Library

Files:

- `v4_0_shell_mockup_v1_library.html`
- `v4_0_library_empty_mockup.html`
- `v4_0_INDEX.html`

Opinion: strong foundation. The shell feels like a real product. The top module tabs, patient left pane, central content, right properties panel, and bottom filmstrip are all sensible.

Keep:

- Dark radiograph-friendly workspace.
- Patient list on the left.
- Patient count and search.
- Central thumbnail grid for Library.
- Collapsible right panel sections.
- Import, Export, Present as visible global actions.
- Empty states that tell the user what to do next.

Change:

- Make patient identity more clinically useful. Patient name alone is not enough in dental imaging. Add DOB or chart ID depending on privacy/settings.
- Do not let the right panel duplicate the filmstrip's job. The right panel should explain the selected image/patient, not become another navigation surface.
- Do not over-brand the top bar. Panda branding is good, but the patient and image context must dominate in daily clinical use.
- Use one thumbnail navigation model per mode.

Dental-specific additions:

- Filters for image type: Radiograph, intraoral photo, extraoral photo, scan, document.
- Filters for region: FMX, BW, PA, pano, CBCT reference, smile, retracted, occlusal.
- Visit/date grouping.
- Tags such as endo, perio, implant, follow-up, referral, insurance.

Rating: 8.5/10. Excellent direction; needs dental metadata and navigation discipline.

### Arrange Canvas / Mount Workflow

File:

- `v4_0_arrange_canvas_mockup.html`

Opinion: this is one of the best mockups. It is the most dental-specific and has the clearest clinical value. It should become a flagship workflow.

Keep:

- Large central mount canvas.
- Slot selection with selected image preview on the right.
- Sensor/region/slot metadata.
- Quick adjustments per slot.
- Filled/remaining count.
- Bottom filmstrip for available images.
- Export series / template / slot / series views.

Change:

- Rename the module from Arrange to Mount.
- Make slot labels more dental. Instead of only slot numbers, show tooth range/region when available: UR molars, #3-5 PA, BW left, anterior, etc.
- Show missing slots more clinically: Missing PA #15-17, Missing BW right, not just empty placeholder.
- Consider a small quality/status marker per slot: unreviewed, enhanced, annotated, exported.
- Be careful with color coding. Sensor size colors should not be confused with pass/fail or clinical severity.

Adobe connection:

- Lightroom gives the filmstrip and selected-image workflow.
- Photoshop contributes transform/rotate/swap tools.
- But the dental mount itself is unique and should be treated as a core differentiator.

Rating: 9.5/10. This is the clearest place where Panda Gallery can feel better than generic image software.

### Edit Image / Loupe / Review

File:

- `v4_0_edit_image_mockup.html`

Opinion: visually strong and mostly right. It has the correct Photoshop-like left tool strip and Lightroom-like right adjustments.

Keep:

- Large image canvas.
- Left contextual tool strip.
- Right tabbed panel: Info, Adjust, Drawing, Layers, History.
- Histogram.
- Auto Enhance.
- Brightness, Contrast, Sharpness, Invert.
- Radiograph auto-detection note.
- Bottom filmstrip.
- Before/After and Compare access.

Change:

- Rename Loupe/Edit to Review in the main mental model. Dentists do not usually think, "I am editing" a radiograph. They think, "I am reviewing" or "enhancing" it.
- Make Original vs Enhanced state extremely visible. Clinical trust depends on knowing what is raw and what is adjusted.
- Put radiograph controls ahead of generic photo controls when the image is a radiograph.
- For photos, show photo controls instead: exposure, crop, rotate, white balance if needed, retouch only if clinically acceptable.
- Keep saturation disabled for grayscale radiographs, as the mockup notes.

Recommended radiograph control order:

1. Auto Enhance.
2. Strength.
3. Brightness.
4. Contrast.
5. Sharpness.
6. Invert.
7. Fine rotate.
8. Bone/detail enhancement, if supported.
9. Reset / Original.

Rating: 9/10. Strong, but rename the mental model and make clinical state more explicit.

### Right Panel Study

File:

- `v4_0_right_panel_study.html`

Opinion: this is the most expert-level artifact in the mockup set. It is not just a screen; it is a product design spec. Keep it.

Best ideas:

- Lightroom-style sliders with center detent and bidirectional fill.
- Collapsible right-panel sections.
- Section state persistence.
- Per-tab grouping: Info, Adjust, Draw, Layers, History, Series.
- Copy / Paste / Previous / Reset actions.
- Presets, but delayed until the core is stable.
- Dental-specific notes about radiograph defaults.

My recommendations:

- Adopt center detent and bidirectional fill for bipolar sliders.
- Adopt collapsible sections with persisted state.
- Adopt Copy/Paste/Previous for image adjustments.
- Add dental presets, but do it after stable enhancement behavior.
- Defer Tone Curve. It is powerful but not needed for MVP.
- Defer complex annotation stamps/templates until basic annotation layers are solid.

This is exactly the kind of Adobe adaptation Panda Gallery should do: take the mature interaction pattern and replace generic photo assumptions with dental defaults.

Rating: 9.5/10.

### Compare

File:

- `v4_0_comparison_mockup.html`

Opinion: very good and clinically valuable. Dentistry needs before/after more than generic photo apps do.

Keep:

- Side-by-side, stacked, grid, split swipe modes.
- Sync zoom/pan toggle.
- Metadata comparison.
- Adjustment delta display.
- Clinical notes panel.
- Tags.
- Export report / send to Present.

Change:

- Make date/time and image category extremely readable.
- Add tooth/region comparison prominently.
- Add a visible "A" and "B" assignment workflow from the filmstrip.
- Do not make heatmap diff an early priority. It sounds exciting but may be clinically noisy and hard to trust.
- Support original/enhanced comparison as well as date-to-date comparison.

Dental-specific use cases:

- Pre-op vs post-op PA.
- Bone level over time.
- Before/after implant placement.
- Ortho progress photos.
- Retreatment comparison.
- Enhanced vs original radiograph.

Rating: 9/10. This should be a core clinical workflow, not an afterthought.

### Template Editor

File:

- `v4_0_template_editor_mockup.html`

Opinion: excellent. This is highly applicable to dental radiography.

Keep:

- Sensor palette.
- Drag/drop slot creation.
- Grid/snap controls.
- Slot properties on right.
- Sensor size lock.
- Orientation toggle.
- Position and size controls.
- Tooth/region labels.
- Save as New vs Save Template.

Change:

- Make tooth/region labeling central, not secondary.
- Add validation: overlapping slots, impossible series, missing tooth region labels.
- Show intended capture order.
- Support common built-in templates first: FMX 18, FMX 20, BW 4, PA endo, implant series.
- Do not over-invest in freeform design until common templates are polished.

Rating: 9.5/10.

### Present Mode

File:

- `v4_0_present_mockup.html`

Opinion: beautiful, but it needs more clinical/privacy thinking. The minimalism is right for chairside presentation, but dentists also need a control surface.

Keep:

- Large image-first display.
- Minimal external-display chrome.
- Annotation toggle.
- Image count and caption.
- Before/after presentation mode.
- Dentist control screen concept.

Change:

- Add privacy mode: hide chart ID, DOB, or internal notes on patient-facing display.
- Distinguish external display from operator display.
- Support a curated presentation queue, not just current filmstrip order.
- Add quick "show original/enhanced" and "show annotations" controls.
- Make labels patient-friendly when presenting: "Before treatment" instead of internal file names.

Rating: 8.5/10. Visually strong; needs patient-safe workflow rules.

### Menu, Toolbar, Palette, Preferences

Files:

- `v4_0_menu_reference.html`
- `v4_0_toolbar_reference.html`
- `v4_0_palette_typography.html`
- `v4_1_preferences_mockup.html`

Opinion: these are valuable reference artifacts, but they should not drive the product before the main workflows are settled.

Keep:

- A complete menu/shortcut map.
- Toolbar inventory with disabled states.
- Design tokens for colors and typography.
- Preferences grouped by workflow.

Change:

- Avoid exposing too many controls just because they exist.
- Keep toolbar visible but quiet.
- Preferences should not become a dumping ground.
- Design tokens need accessibility checks. Some dim gray text is elegant but may be too low-contrast in a real dental office.

Important design note:

The dark navy/purple palette is attractive and appropriate for radiographs, but it risks becoming too one-note. The app needs neutral grayscale image surfaces, peach for primary selection/action, green for success, red for destructive/error, amber for warning/status, and blue only where it carries real semantic value.

### Splash Screen

File:

- `v4_0_splash_mockup.html`

Opinion: attractive but low priority.

Keep it if it is quick and does not distract from clinical speed. Do not let splash/branding consume time before Library, Mount, Review, Compare, and Present are strong.

Rating: 7/10 as product polish, 3/10 as priority.

### Instruction Pane, Action Bars, Checklist, Fail Panel

Files:

- `instruction_pane_redesign_v1.html`
- `pane_action_bar_v2_mockup_v1.html`
- `action_bar_mockup_v1.html`
- `checklist_mockup_v1.html`
- `checklist_mockup_v2.html`
- `single_expected_mockup_v1.html`
- `single_expected_mockup_v2.html`
- `pane_fail_panel_mockup_v1.html`
- `pane_fail_panel_mockup_v2.html`
- `v3_71_ui_vocabulary.html`

Opinion: these are unusually thoughtful internal testing UX mockups. They solve real tester pain: hidden buttons, cramped panes, oversized fail boxes, unclear state, and poor action placement.

Keep:

- Always-reachable action bar.
- PASS / FAIL / SKIP / Next outside the scroll area.
- Summary strip above action bar.
- FAIL panel with capped height.
- Two-row wrapping below breakpoint.
- Explicit narrow-width behavior.
- UI vocabulary document.
- Action step with Acknowledge for steps that require doing, not checking.

My choice on Acknowledge variants:

Choose Variant B, the primary peach `Acknowledge` button, if the step truly cannot be judged and the user simply needs to advance after doing it. It is clear and reachable.

Do not use `Continue` for action steps if `Next` also exists elsewhere. It blurs two concepts. `Acknowledge` is more honest: the tester is saying, "I did the thing."

Dental relevance:

This testing UX should remain internal. Do not let PASS/FAIL language leak into clinical image review, where the clinician is not passing/failing an image unless they are in a QA workflow.

Rating: 9/10 for internal testing UX.

### Focus Indicator

File:

- `focus_indicator_v1.html`

Opinion: the mockup correctly identifies the tradeoff. My recommendation depends on whether the goal is emergency clarity or long-term elegance.

- Option A, solid peach title bar: best if users are repeatedly acting in the wrong window and the cost of ambiguity is high.
- Option B, 2px top stripe: too subtle. I would not choose it.
- Option C, left border plus title text: best long-term product compromise.

My recommendation:

Use Option C as the product default. Use Option A only if #131 remains a serious testing workflow problem after Option C is implemented.

Why: Option A is impossible to miss, but it changes the personality of the whole window. Option C gives two cues without making the title bar feel like an alarm.

### Region Capture and Review Dialog

Files:

- `region_capture_v1.html`
- `review_dialog_sizing_v1.html`
- `dialog_sizing_v1.html`

Opinion: strong for testing/audit capture. The region-capture flow is clear, staged, and practical.

Keep:

- Shift+F12 region capture.
- Dim outside rectangle, preserve selected area at full brightness.
- Live dimensions label.
- Capture flash.
- Toast notification.
- Review dialog with Save / Discard / Re-capture.
- Anchored review dialog near instruction pane.
- Smaller preview cap.
- Dialog sizing rules with button visibility invariants.

Change:

- Consider a keyboard path to open the review dialog after capture. Toast-only is clean, but keyboard-driven testers may expect Enter or a shortcut.
- For PHI safety, captured screenshots need audit metadata and possibly redaction rules if this later touches real patient data.
- Review dialog should clearly show whether the capture is associated with a test step/session.

Rating: 8.5/10.

### Stats Row / Mic Level Bar

File:

- `stats_row_mic_bar_mockup_v1.html`

Opinion: this is a good microinteraction. It makes audio capture status visible without consuming a large area.

Keep:

- Fixed row height.
- Animated mic bar only during active audio capture.
- Text fallback for silent/disconnected/failed states.
- Ellipsis behavior at narrow widths.

Change:

- Make failed state visually distinct from silent/disconnected if testers confuse them.
- Do not over-animate. It should reassure, not distract.

Rating: 8.5/10.

### Avatar Rewrite

File:

- `113_avatar_rewrite_mockup_v1.html`

Opinion: sensible engineering cleanup, but not a product priority.

Initials-based patient avatars are fine. I would not use real patient face thumbnails in the patient list by default because of privacy and because dental users often identify by name/chart/visit, not profile photo.

Priority: low unless the current avatar implementation is causing rendering bugs.

## Clinical Workflow Recommendations

### Radiographs

Radiographs should get their own defaults and tools.

Primary radiograph tools:

- Invert.
- Auto Enhance / CLAHE.
- Brightness.
- Contrast.
- Sharpness.
- Local contrast / bone detail.
- Fine rotate.
- Crop.
- Measure, eventually with calibration.
- Tooth/region labels.
- Original/enhanced toggle.
- Before/after comparison.

Radiograph metadata should include:

- image type,
- sensor size,
- date captured,
- region,
- tooth range,
- mount slot,
- series name,
- enhancement preset,
- original/enhanced state,
- annotations present,
- export/report status.

### Photographs

Photos should have a related but different control set.

Primary photo tools:

- Crop.
- Rotate/straighten.
- Exposure/brightness.
- Contrast.
- White balance if clinically useful.
- Basic color correction.
- Annotation/text/arrows.
- Before/after presentation.

Avoid making photo editing feel like cosmetic retouching. In dental context, the goal is documentation and communication.

### Dental Mounts

Mounts are a major differentiator. Treat them as first-class, not as a side feature.

Needed mount behaviors:

- Common template library.
- Capture/fill order.
- Missing-slot visibility.
- Drag/drop fill.
- Swap slots.
- Rotate/flip per slot.
- Slot-level enhancement.
- Series export.
- Printable/referral layout.
- Audit trail of which source image filled which slot.

### Comparison

Comparison should be treated as clinical evidence.

Core comparison requirements:

- A/B assignment from filmstrip.
- Synchronized pan/zoom.
- Toggle annotations.
- Toggle original/enhanced.
- Before/after dates.
- Tooth/region match warning if images do not align clinically.
- Clinical note field.
- Export report.

## Adopt / Adapt / Defer / Avoid

### Adopt Now

- Dark radiograph-friendly workspace.
- Top module tabs.
- Bottom filmstrip.
- Right-side collapsible panels.
- Mount canvas and template editor direction.
- Review/Edit screen structure.
- Comparison screen structure.
- Auto Enhance plus basic sliders.
- Invert radiograph toggle.
- Annotation tool strip in Review only.
- Always-visible action bars in testing pane.
- Dialog sizing invariants.

### Adapt Before Building

- Rename `Arrange` to `Mount`.
- Promote `Review` as the mental model for single-image work.
- Make Compare either a primary module or a very visible Review mode. My preference: primary module.
- Make metadata dental-first.
- Make radiograph and photo control sets context-sensitive.
- Use one filmstrip location per mode.
- Make Original/Enhanced/Annotated state always visible.
- Adjust contrast for real dental office monitors.

### Defer

- Tone curve.
- Heatmap diff.
- Complex annotation templates/stamps.
- Deep layer grouping.
- Real patient avatars.
- Extensive preferences.
- Splash polish beyond basic loading screen.
- Full Adobe-like shortcut coverage.

### Avoid

- Generic photo-editing language as the primary vocabulary.
- Too many visible controls on first launch.
- Multiple competing thumbnail/filmstrip regions.
- Decorative brand moments inside productivity workflows.
- Low-contrast helper text for critical state.
- Mixing internal testing PASS/FAIL language with clinical workflows.
- Building Dropbox/AI/audit dashboard UI before evidence contracts are stable.

## Highest-Value Implementation Sequence

Recommended v4 design implementation order:

1. Lock global shell and design tokens.
2. Rename/refine modules: Library, Mount, Review, Compare, Present.
3. Build Library patient/image context cleanly.
4. Build Mount canvas and core templates.
5. Build Review screen with right-panel adjustments.
6. Add original/enhanced state model.
7. Add bottom filmstrip consistency.
8. Add Compare A/B workflow.
9. Add Present mode privacy rules.
10. Add template editor refinement.
11. Add presets and Copy/Paste/Previous.
12. Add advanced annotation/history features.

This sequence avoids the biggest trap: implementing beautiful panels before the data/state model knows what an image, series, enhancement, annotation, and export actually are.

## Concrete Requests I Would Give Claude

### Prompt 1 - Rename And Clarify v4 Modules

Ask Claude to update the v4 mockup language so the primary module set is Library, Mount, Review, Compare, Present. Replace Arrange with Mount and Loupe/Edit with Review terminology where appropriate. Do not change behavior yet; this is vocabulary alignment.

### Prompt 2 - Define Dental Image State Badges

Ask Claude to design a small state badge system for Original, Enhanced, Annotated, Mounted, Exported, and Needs Review. The badges should appear in Library thumbnails, Review header, Mount slots, and Compare metadata.

### Prompt 3 - Make Radiograph vs Photo Panels Contextual

Ask Claude to design two right-panel variants: Radiograph Adjust and Photo Adjust. Radiograph gets invert/CLAHE/contrast/sharpness/fine rotate. Photo gets crop/rotate/exposure/contrast/color. Shared controls stay visually consistent.

### Prompt 4 - Unify Filmstrip Rules

Ask Claude to specify exactly where filmstrip appears by module, what it contains, and how it interacts with selection. Avoid top and bottom filmstrips competing.

### Prompt 5 - Mount Workflow Spec

Ask Claude to turn the Arrange/Mount mockup into a functional spec: data model, slot states, fill order, missing slot behavior, export behavior, and verification steps.

### Prompt 6 - Compare Workflow Spec

Ask Claude to turn the Compare mockup into a functional spec: A/B assignment, sync pan/zoom, metadata, notes, export report, original/enhanced comparison, and date-to-date comparison.

## Bottom Line

Claude's mockups are good enough to serve as the visual foundation for Panda Gallery v4, but the next pass should make them less "Adobe-inspired image app" and more "dental imaging command center."

The best parts to keep are the shell discipline, filmstrip, right panels, Mount canvas, Review tools, Compare workflow, and template editor. The parts to restrain are generic photo-editing complexity, too many controls, low-contrast text, decorative branding, and anything that does not help a dentist see, compare, explain, document, or export clinical evidence.

My overall score: 8.8/10.

With dental vocabulary and a tighter implementation sequence, this can become a very strong, modern, intuitive interface.
