# PG Major Design Decision: Module Inspirations and Resizable Pro Workspaces v1

Status: MAJOR DESIGN DECISION
Date: 2026-05-11
Owner: Darrin
Recorded by: Codex
Scope: Future Panda Gallery overhaul design direction
Current implementation status: Reference only while the Vellum-only hold remains active

## Executive Decision

Panda Gallery should be designed as a dental-first professional imaging workspace, not as a fixed-pane image viewer. The overhaul should borrow specific strengths from leading professional photography, dental imaging, treatment-planning, and presentation tools, then translate those strengths into PG's clinical workflow.

The dominant design rule is:

**Resizable panels everywhere, always.**

Resizable, persistent, task-specific workspaces are table stakes for a serious professional tool. Capture One built much of its reputation on workspace flexibility: users can resize, move, collapse, reorder, and save panels for different jobs. Panda Gallery should adopt that expectation across the app wherever technically practical.

This decision should guide future PG overhaul design and review. It does not authorize implementation while the Vellum-only hold remains active.

## Source Inspirations By Module

| PG Module | Primary Inspirations | Core Lesson |
|---|---|---|
| Library | Capture One + DEXIS | Patient-centered hub with fast import, search, filters, and flexible panels. |
| Develop | Capture One + Lightroom | Sacred image canvas with customizable tool panels and excellent slider controls. |
| Arrange | Dolphin Imaging | Templates are first-class objects, visible up front, with drag-to-slot layout workflows. |
| Presentation | Dolphin Imaging + Apple Keynote | Full-screen, patient-safe, visually calm presentation with hidden controls. |

## Library

Primary inspirations: Capture One + DEXIS

### Research Lesson

Capture One lets users drag, resize, reorganize, and save panels into custom workspaces per task. DEXIS, as a dominant dental imaging product, is patient-centric first: the patient record is the hub, and images hang off that context. Professional users also need import, filtering, and search to be direct and fast.

### Design Decision

Library must start from the patient record, not from a generic file-browser model. Import must be a first-tier action, and quick filters plus instant search are non-negotiable.

### Requirements For Future Design

- Patient context is the primary organizing object.
- Images, exams, sessions, series, and selected items visually attach to the active patient.
- Import is always prominent and never buried in menus.
- Search is instant and available without changing modes.
- Filter chips support professional narrowing by modality, date, status, rating, case, view type, source, and tags.
- Library panels are resizable and workspace layouts are persistent.
- The app remembers useful Library workspaces by task.

## Develop

Primary inspirations: Capture One + Lightroom

### Research Lesson

Capture One's right panel is fully customizable: panels can reorder, collapse, and solo-expand. Lightroom-style sliders remain the gold standard for adjustment workflows. The filmstrip resizes by drag. Every expert tool should expose its keyboard shortcut in the tooltip. Panels are where power lives, but the image canvas is sacred space.

### Design Decision

Develop must protect the image canvas while offering expert-grade, customizable tools around it.

### Requirements For Future Design

- The image canvas is the visual center and should not be crowded by tool chrome.
- Right-side tool panels are reorderable, collapsible, and support solo-expand behavior.
- Adjustment controls use the proven LightroomSlider interaction pattern.
- Filmstrip size is user-resizable by drag.
- Every major tool exposes its keyboard shortcut in the tooltip.
- Tool panels support expert speed without obscuring the image.
- Workspace layout persists across sessions and can be saved per task.

## Arrange

Primary inspiration: Dolphin Imaging

### Research Lesson

Dolphin Imaging is the gold standard reference for dental patient presentation and treatment planning. Templates are first-class objects: users drag images into slots, preview instantly, then print or export in one click. Users should never have to hunt for templates. They should be front and center.

### Design Decision

Arrange must make templates and slot-based layout creation a primary workflow, not a hidden tool or secondary dialog.

### Requirements For Future Design

- Templates are visible as first-class objects.
- Template browser, source image tray, and layout canvas are direct and prominent.
- Drag-to-slot interaction is the default Arrange workflow.
- Template preview updates immediately.
- Print and export are one-click once a layout is ready.
- Template and layout controls are resizable and task-oriented.
- Arrange should support treatment-planning and patient-communication workflows, not only graphic layout.

## Presentation

Primary inspirations: Dolphin Imaging + Apple Keynote

### Research Lesson

Presentation should be patient-facing, full-screen, privacy-first, and visually calm. The patient should see one image or one layout at a time. Controls should be invisible until hovered or intentionally revealed. Nothing the patient should not see should ever be on screen.

### Design Decision

Presentation must behave like a patient-safe clinical presentation surface, closer to Keynote than to a database or editing screen.

### Requirements For Future Design

- Presentation mode hides internal metadata, file paths, debug text, and clinical-only controls.
- The default view is full-screen image or full-screen layout.
- Controls stay hidden until hover or deliberate input.
- Navigation is simple, stable, and patient-safe.
- Patient-facing content is visually calm and uncluttered.
- Internal review status, implementation notes, and non-patient-safe labels never appear in patient view.

## Cross-Module Workspace Rules

1. Every major pane should be resizable where technically practical.
2. Panel sizes, visibility, and ordering should persist by workspace or task.
3. Users should be able to collapse panels without losing the primary workflow.
4. Important tools should remain discoverable when panels are collapsed.
5. Filmstrips and side panels should use drag handles, not only fixed presets.
6. Canvas or viewer space is sacred; the image or layout being evaluated remains the visual center.
7. Keyboard shortcuts appear in tooltips for expert workflows.
8. Search, filters, import, template access, and export are first-tier actions in their relevant modules.
9. Workspaces should support clinical tasks, not just aesthetic preferences.
10. Fixed-layout panels should be the exception, not the default.

## Review Questions For Future PG Overhaul

Use these questions when evaluating PG redesign proposals:

1. Does this screen preserve patient context?
2. Are primary actions visible without menu hunting?
3. Can the user resize the panels that affect daily work?
4. Does the layout remember the user's workspace choices?
5. Is the image or layout still the visual center?
6. Are expert workflows exposed through shortcuts and tooltips?
7. Are templates first-class in Arrange?
8. Is Presentation safe to show directly to a patient?
9. Does the design feel like a professional imaging workstation rather than a fixed demo shell?

## Non-Goals

- This decision does not authorize immediate implementation.
- This decision does not reopen PG overhaul work while the Vellum-only hold is active.
- This decision does not require literal cloning of Capture One, DEXIS, Dolphin, Lightroom, or Keynote.
- This decision does not supersede the need for real PySide screenshot verification.
- This decision should guide future design choices when Darrin explicitly reopens the PG overhaul lane.

## Product North Star

Panda Gallery should feel like a dental-first professional imaging workspace: patient-centered like DEXIS, flexible like Capture One, precise like Lightroom, layout-forward like Dolphin, and calm/patient-safe like Keynote.
