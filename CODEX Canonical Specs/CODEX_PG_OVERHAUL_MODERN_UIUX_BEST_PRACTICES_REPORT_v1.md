# PG Overhaul Modern UI/UX Best Practices Report v1

Status: READY / Bible amendment candidate
Owner: Codex
Created: 2026-05-10
Scope: Research-backed UI/UX strategy for Panda Gallery overhaul. This report is advisory/specification material only. It does not authorize implementation, commits, PAH activity, or direct edits to `C:\panda-gallery`.

## 1. Recommendation

Build the PG overhaul as a clinical imaging command center, not as an Adobe clone. Borrow Lightroom's workflow modules, filmstrip continuity, before/after review, panel discipline, solo/collapse behavior, presets, history, and lights-out viewing. Borrow Photoshop's contextual task bar and precise tool/options model. Borrow dental platforms' patient-centered imaging hub, multi-modality case view, AI as evidence overlay, and case communication. Keep PG's own Design Bible voice: dark, restrained, dense, clinical, peach only for meaning, every pixel earning its place.

No blocking question for Darrin. My recommendation is to prioritize the Develop/Review image-work surface first because that is where PG's value is most visible and where Adobe/dental references most directly apply. Library and Arrange should be designed around supporting that surface, not as generic asset-management screens.

## 2. Research Sources Used

### Adobe / Creative Tools

- Adobe Lightroom Classic workspace basics: modules, panels, filmstrip, module picker, toolbar, panel show/hide, Lights Out.
  Source: https://helpx.adobe.com/lightroom-classic/help/workspace-basics.html
- Adobe Lightroom Classic Develop module: left preview/history/presets panels, right adjustment panels, histogram, tool strip, before/after, presets, amount slider, incompatible presets shown faded.
  Source: https://helpx.adobe.com/lightroom-classic/help/develop-module-tools.html
- Adobe Photoshop workspace overview: application bar, document window, options bar, tools panel, panels, customizable workspaces.
  Source: https://helpx.adobe.com/photoshop/using/workspace-basics.html
- Adobe Photoshop Contextual Task Bar: dynamic task-specific actions, dock/float/hide, selection-aware next actions.
  Source: https://helpx.adobe.com/photoshop/using/contextual-task-bar.html

### General UI/UX Standards

- Apple Human Interface Guidelines toolbar guidance: deliberate toolbar items, useful titles, standard symbols, avoid overcrowding, actions that support main tasks.
  Source: https://developer.apple.com/design/human-interface-guidelines/toolbars
- Microsoft NavigationView: adaptive top/left navigation, consistent app navigation, preserving screen space, organizing many categories, responsive breakpoints.
  Source: https://learn.microsoft.com/windows/apps/design/controls/navigationview
- Microsoft CommandBar: primary commands by importance, overflow behavior, consistent placement for cross-page commands.
  Source: https://learn.microsoft.com/windows/apps/design/controls/command-bar
- Nielsen Norman usability heuristics: status visibility, match real world, user control, consistency, error prevention, recognition over recall, efficiency, minimalist design, recovery, help.
  Source: https://www.nngroup.com/articles/ten-usability-heuristics/
- W3C WCAG 2.2: dragging alternatives, target size, focus visibility/focus not obscured.
  Sources:
  - https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements.html
  - https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum
  - https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html
  - https://www.w3.org/WAI/WCAG22/Understanding/focus-appearance.html

### Dental Imaging / Dental Workflow References

- Carestream Dental CS Imaging 8: single imaging platform for 2D/3D/CAD/CAM, dashboard image gallery, side-by-side case review, auto-arrange, darkroom mode, simultaneous enhancement.
  Source: https://www.carestreamdental.com/en-us/discover/clinical-software/imaging-software/cs-imaging-v8/
- Planmeca Romexis: 2D/3D all-in-one imaging, study templates, AI tooth-number detection, image processing, measurement, annotations, DICOM/export, audit trails, patient search by image/date/comment.
  Source: https://www.planmeca.com/dental-software/planmeca-romexis/specifications/
- DEXIS Imaging Suite: easy diagnostic image hub, fast x-ray workflow, 1-click full-mouth series, AI finding labels, sensor/open integration.
  Source: https://dexis.com/en-us/software-dexis-imaging-suite
- DTX Studio Clinic: all 2D/3D/photos/scans in one patient-centered imaging software, practice-management interlink, multi-room access.
  Source: https://www.dtxstudio.com/en-int/dtx-studio-clinic
- 3Shape Unite: workflow engine, guided workflows, case management, lab/provider communication, app ecosystem, cloud case availability.
  Source: https://www.3shape.com/en-us/software/unite

## 3. Existing PG Rules This Report Must Preserve

This report must add to, not overwrite, these current PG rules:

- `PG_DESIGN_BIBLE_v1.md`: medical not playful, restraint over flourish, clinical precision via mono, every pixel earns its presence, progressive disclosure, left-to-right workflow order.
- `UX_PRINCIPLES.md`: Escape goes one level back, obvious in 30 seconds, primary actions one click from context, empty states teach, duplicate data prevented or explicitly accepted.
- `PG_UX_UI_Overhaul_v1.2_clarifying_questions.md`: keep PG's current identity with selective Adobe-style improvements; whole-shell mockup first; use real-looking safe dental imagery; approval based on full-size mockups; Vellum default actual-size review.
- `STATE_MATRIX_v2.md`: current module set is Library / Arrange / Develop / Presentation; existing v2 states already include real dental imagery, lights-out, before/after, panel stacks, export states, and presentation privacy gates.

## 4. Core Product Model For PG Overhaul

PG should be organized around clinical jobs, not around implementation modules.

Recommended top-level modules:

1. Library: patient/case/image intake, search, filter, selection, and clinical image history.
2. Arrange: mount/grid/freeform organization for diagnostic sequences and presentation layouts.
3. Develop: diagnostic viewing, adjustment, annotation, measurement, comparison, AI overlays, and evidence review.
4. Presentation: patient-safe case display, treatment communication, privacy gates, export/share.

Do not add a top-level AI module, Tool module, Template Studio module, or Settings module unless a future workflow proves they deserve top-level navigation. AI is an evidence layer. Tools are contextual. Template editing belongs inside Arrange. Settings is secondary chrome.

## 5. Lightroom-Inspired Practices To Add To PG Bible

### 5.1 Module Discipline

Lightroom's strength is that modules match workflow stages. PG should preserve module boundaries and make module switches intentional.

Rules:

- Each module gets a distinct primary job and a narrow visible command set.
- Module-specific tools should be hidden outside their module, not disabled.
- Cross-module continuity comes from patient/case context, filmstrip, selected image, and status bar.
- Module switch must preserve the user's selected patient and selected image unless an explicit workflow reset occurs.

### 5.2 Filmstrip As Continuity Spine

The filmstrip should be available anywhere the user is operating on a selected case or image. It is not decoration; it is the user's continuity spine.

Rules:

- Filmstrip always shows the current patient/case scope, not an unrelated folder.
- Filmstrip thumbnails show modality, date/time, selection state, review state, and warning/AI badge only when meaningful.
- Multi-select state must be visually unmistakable and must change the contextual action set.
- Filmstrip can collapse to preserve image space, but it must remain recoverable in one click or one keyboard shortcut.

### 5.3 Panels, Solo Mode, And Collapse

Lightroom's panel model works because it lets users manage density without losing control.

Rules:

- Right panels should use semantic sections: Histogram/Quality, Adjust, Annotate, Measure, AI Findings, Metadata, History.
- Support solo mode for dense adjustment panels.
- Persist panel collapse state per module, but provide a reset-to-default workspace action.
- Never place decorative cards inside panels. Panels are compact control surfaces.

### 5.4 Lights-Out / Diagnostic Focus Mode

Lights Out is highly relevant to radiograph review.

Rules:

- Add a diagnostic focus mode that dims or hides chrome while preserving current image, zoom, annotations, and warning state.
- Partial mode: chrome dimmed, image full brightness.
- Full mode: image/canvas dominates; essential safety/privacy indicators remain visible only if clinically or legally necessary.
- Shortcut should cycle Normal -> Dim -> Full -> Normal.

### 5.5 Before/After, Reference, And Compare

PG should support before/after and reference comparison as first-class clinical review primitives.

Rules:

- Before/after split must preserve synchronized pan/zoom where useful.
- Reference view should support previous visit, pre-op/post-op, same tooth over time, and current adjusted vs original.
- Labels must be clinical and exact: `BEFORE`, `AFTER`, `2026-03-14`, `Pre-op`, `Post-op`, `Original`, `Adjusted`.
- No comparison mode should hide patient identity/privacy state.

### 5.6 Presets, Amount, And Non-Destructive Adjustments

Lightroom's preset pattern maps well to dental image enhancement if PG stays clinically honest.

Rules:

- Provide named diagnostic presets such as `Perio bone`, `Endo detail`, `Caries contrast`, `Panoramic clarity`, and `Photo shade`.
- Every preset must be reversible and non-destructive.
- Use an amount/intensity slider where a preset is a stack of adjustments.
- Incompatible presets should be visible but muted with a clear reason, e.g. `Photo-only preset` on x-ray.
- The original image is immutable; exports must record adjustment recipe metadata.

### 5.7 History And Snapshots

Rules:

- Develop needs a visible history/snapshot model for clinical auditability.
- History entries should use clinical verbs: `Adjusted contrast`, `Added measurement`, `Accepted AI finding`, `Exported referral PDF`.
- Snapshots should be named and timestamped; do not rely on invisible undo stacks for clinical decisions.

## 6. Photoshop-Inspired Practices To Add To PG Bible

### 6.1 Contextual Task Bar

Photoshop's Contextual Task Bar is the right model for PG's next-best action behavior.

Rules:

- Show a compact contextual action bar near the image or active selection.
- Content changes by selection state: no image, image selected, annotation selected, crop active, measurement active, AI finding selected, export blocked.
- Keep it dockable/hideable so experts can preserve screen space.
- Include only actions that apply now; future or blocked actions belong in side panel status, not floating clutter.

### 6.2 Tool + Options Separation

Rules:

- Tool rail chooses the active tool; options bar configures that tool.
- Do not mix tool selection, tool settings, and final actions in one undifferentiated row.
- Active tool must be visible in at least two places: highlighted tool and status bar / context bar label.
- Escape exits the active tool one level back.

### 6.3 Layers Without Creative-App Confusion

PG needs evidence overlays, not Photoshop-style freeform creative layers.

Rules:

- Use `Evidence Layers` or `Overlays`, not generic `Layers`, unless the implementation truly supports layer editing.
- Separate source image, adjustments, annotations, measurements, AI findings, and presentation masks.
- Allow show/hide per overlay type and per individual finding.
- Exports must record which overlays were visible.

### 6.4 Non-Destructive Editing Standard

Rules:

- Every adjustment, crop, markup, measurement, and AI overlay is non-destructive unless explicitly exported as a flattened copy.
- Show dirty state when unsaved overlay/recipe changes exist.
- Provide clear reset for adjustment recipe without deleting annotations or source image.

## 7. Dental-App Practices To Add To PG Bible

### 7.1 Patient-Centered Imaging Hub

Dental imaging tools converge on one patient-centered hub. PG should make patient/case identity and image history the anchor.

Rules:

- Patient/case context must remain visible enough to prevent wrong-patient/wrong-case work.
- Library should show image type, date, clinical status, and source device/import path where useful.
- Patient search should support name, ID, image type, date, modality, comment, and review status.
- Multi-room/cloud patterns from dental apps are strategic references, but PG should not imply cloud sync unless implemented.

### 7.2 Multi-Modality In One Case View

Rules:

- Treat PA, BW, panoramic, intraoral photo, scan, CBCT, PDF, and document attachments as case assets with modality-specific viewers.
- The same patient/case filmstrip may include multiple modalities, but the Develop toolset must adapt to modality.
- Do not show x-ray enhancement controls on intraoral photos unless they have a clinical reason.

### 7.3 Dental Study Templates And Auto-Placement

Planmeca-style study templates and AI tooth numbering are strong PG opportunities.

Rules:

- Arrange should support named dental mounts/study templates.
- Slots should know expected tooth/region/modality.
- Auto-place should be explainable and reversible.
- Wrong-slot warnings should be visual, concise, and non-destructive.

### 7.4 AI As Evidence Overlay, Not Authority

Rules:

- AI findings should appear as reviewable overlays with confidence, category, source image, and timestamp.
- The user must accept, reject, edit, or hide AI findings; AI should not silently alter diagnosis or records.
- AI overlays should be batch-filterable by finding type and confidence.
- AI labels must not obscure diagnostic anatomy at default zoom.

### 7.5 Case Communication And Export

Rules:

- Presentation mode should support patient-safe display with privacy gates.
- Referral/export should use templates: patient-safe JPEG, archive TIFF, referral PDF, presentation packet, DICOM export where available.
- Export dialogs must show what identifiers and overlays will be included before export.
- Every export should create a summary record for auditability.

## 8. General Modern UI Practices To Add To PG Bible

### 8.1 Command Hierarchy

Rules:

- Primary actions live in predictable places and are one click from context.
- Keep at most 3-5 primary commands visible per toolbar region; overflow secondary commands.
- Order commands by workflow importance, not alphabetically.
- Destructive commands should be spatially separated and visually distinct.

### 8.2 Adaptive Navigation Without Reflow Chaos

Rules:

- Desktop default: left module rail or top module switcher, but do not use both as equal top-level nav.
- At narrower widths, collapse nav to icons or a minimal rail before shrinking the image stage below useful review size.
- Never let toolbar controls wrap over the image stage or obscure focus.

### 8.3 Recognition Over Recall

Rules:

- Use visible mode labels, selected tool labels, short keyboard hints, and persistent state indicators.
- Do not require the user to remember whether a filter, preset, or privacy mask is active.
- Show a plain-language reason for disabled controls.

### 8.4 Accessibility And Precision Input

Rules:

- Any drag operation must have a single-pointer or keyboard alternative: nudge buttons, numeric fields, move-up/down commands, slot menu, or click-to-set endpoints.
- Interactive targets should meet at least 24x24 CSS px equivalent or have sufficient spacing; clinical desktop controls may be compact, but tiny adjacent targets require an alternate larger affordance.
- Keyboard focus must not be obscured by sticky panels, floating task bars, or overlays.
- Focus indicators should be visible and high contrast, especially in dark UI.
- Sliders need numeric value fields or stepper controls for precise clinical adjustment.

### 8.5 Error Prevention And Recovery

Rules:

- Prevent wrong-patient, wrong-image, wrong-export, and destructive-delete mistakes before they happen.
- Show export privacy warnings before output, not after.
- Undo/redo must cover overlay, adjustment, arrangement, crop, and annotation changes where feasible.
- Recovery messages should state the problem and the next action, not just `failed`.

## 9. PG-Specific Bible Amendment Candidates

Add these as candidate Bible/strategy rules after CD/Darrin review:

1. PG is a clinical imaging command center; Adobe is an interaction reference, not a visual identity transplant.
2. The image stage is the product. Chrome must serve image review, case organization, or patient communication.
3. Filmstrip is the continuity spine for active case/image work.
4. Contextual task bar is the preferred pattern for next-best actions on selected images, annotations, measurements, AI findings, and crop regions.
5. AI appears as evidence overlays requiring human review, never as silent authority.
6. Dental study templates should make expected tooth/region/modality visible and validate auto-placement.
7. Diagnostic presets are non-destructive recipes with visible amount/intensity and export metadata.
8. Before/after/reference comparison is a core Develop capability, not a secondary feature.
9. Presentation mode must be patient-safe by default, with explicit privacy gates for identifiers and annotations.
10. Every drag-first interaction requires a non-drag alternative.
11. Every disabled action must answer why through tooltip, adjacent status, or workflow context.
12. Any new toolbar must pass an overcrowding check at laptop widths before approval.
13. Any screen with radiographs must support a focus mode that reduces chrome without losing safety context.
14. Every export should declare included identifiers, overlays, adjustments, and output destination before final confirmation.
15. Clinical auditability is part of the UX: history, snapshots, export records, and AI review decisions must be visible enough to trust.

## 10. Actionable Mockup Requirements

Future PG overhaul mockups should include these states before coding:

- Library loaded with patient image history and modality filters.
- Library search/no-results/duplicate import.
- Develop normal x-ray review with histogram, filmstrip, right panel, selected image metadata.
- Develop with contextual task bar for active annotation.
- Develop with AI findings overlay accepted/rejected/hidden states.
- Develop before/after split and reference comparison.
- Develop lights-out partial and full.
- Develop preset applied with amount slider and history entry.
- Arrange empty mount, auto-placement suggestion, wrong-slot warning, drag alternative menu.
- Presentation patient-safe screen with privacy gate and export preview.
- Export dialog showing identifiers/overlays/adjustments included.
- Error/recovery state for blocked export or missing patient.

Each mockup must be full-size approval-ready, use safe realistic dental imagery, include short readable filename/title and status badge, and avoid side-by-side shrinkage as final approval evidence.

## 11. Verification Checklist For Bible/Strategy Adoption

Before any rule from this report becomes implementation scope:

- CD or Darrin marks it as accepted/adopted.
- Conflicts with `PG_DESIGN_BIBLE_v1.md` are resolved explicitly.
- Affected mockups are generated at full size and reviewed in Vellum or equivalent actual-size viewer.
- The rule is tested against at least one Library, Develop, Arrange, and Presentation state.
- Accessibility checks cover focus visibility, target spacing, drag alternatives, keyboard path, and no text overlap.
- No real PHI/patient data appears in mockups or examples.

## 12. Not Recommended

Do not:

- Copy Adobe's visual chrome wholesale.
- Add a top-level AI module before AI has a proven daily workflow.
- Hide clinical state behind pretty cards or marketing-style hero screens.
- Make side-by-side comparison images the approval artifact.
- Treat dental AI detections as final diagnoses.
- Put every possible tool in the toolbar.
- Use drag-only arrangement, crop, slider, or annotation interactions.
- Let export happen without visible privacy/identifier/overlay summary.
- Use decorative gradients, bokeh, rounded marketing cards, or playful motion in clinical screens.

## 13. Self-Review Record

Pass 1: 6 issues fixed - added explicit advisory/no-implementation boundary; added source list with URLs; corrected Adobe guidance from visual imitation to selective interaction borrowing; added dental-specific AI-as-evidence rule; added accessibility drag-alternative requirements; added PHI-safe mockup constraint.
Pass 2: 5 issues fixed - aligned module names to Library/Arrange/Develop/Presentation; added existing PG rule preservation section; added export privacy/overlay summary; added no-top-level-AI recommendation; added verification checklist before Bible adoption.
Pass 3: 4 issues fixed - clarified filmstrip scope as patient/case continuity spine; added non-destructive preset/history/export metadata requirements; added modality-specific tool adaptation; added command overcrowding check.
Pass 4: 2 issues fixed - removed ambiguity around direct edits to `C:\panda-gallery`; added statement that no blocking Darrin question is needed and recommended Develop/Review priority.
Pass 5: 0 significant issues fixed - no remaining blocking errors, omissions, inconsistencies, or ambiguities found.
