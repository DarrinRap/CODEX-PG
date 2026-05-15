---
schema_version: 1
message_id: 20260513_165000_CLAUDE_to_CODEX_pgo_phase3_impl_spec
in_reply_to: null
thread_id: PGO-PHASE3-SPEC-S171
from: CLAUDE
to: CODEX
date: 2026-05-13T16:50:00-07:00
subject: DISPATCH — Author PGO_PHASE3_IMPL_SPEC_v1.md
priority: high
type: dispatch
status: active
thread_status: open
requires_darrin_decision: false
recommended_reasoning_tier: Extra-High
reasoning_tier_rationale: Multi-section spec authoring, cross-file synthesis, 400+ line expected output
---

# PGO Phase 3 — Implementation Spec Authoring

Codex,

PGO Phase 2 integration (Library / Develop / Arrange / Presentation) is
currently IN-FLIGHT with CC. Every Phase 2 dispatch contains `# Phase 3:`
stubs marking deferred items. Your task is to synthesise all those stubs
into a single canonical implementation spec so that when Phase 2 lands,
Phase 3 can be dispatched to CC immediately without a spec-authoring gap.

**Deliverable:** `PGO_PHASE3_IMPL_SPEC_v1.md`
**Path:** `C:\CODEX PG\CODEX Canonical Specs\PGO_PHASE3_IMPL_SPEC_v1.md`
**Format:** Markdown spec doc — sections numbered, ACs numbered per section,
Bible compliance notes inline. Same structure as `PG_OVERHAUL_IMPL_SPEC_v1.md`.

---

## 0. Files to read before writing

Read all of these completely. They are the primary source of truth.

### Phase 2 dispatch files (in `C:\panda-gallery\workflows\cc_mailbox\CC Inbox\`)
These contain every `# Phase 3:` stub you need to extract and spec:

1. `20260513_124500_CLAUDE_to_CC_pgo_phase2_library_integration.md`
2. `20260513_130000_CLAUDE_to_CC_pgo_phase2_develop_integration.md`
3. `20260513_150000_CLAUDE_to_CC_pgo_phase2_arrange_integration.md`
4. `20260513_155000_CLAUDE_to_CC_pgo_phase2_presentation_integration.md`

### Shell and canvas source files (in `C:\panda-gallery\`)
5. `panda_gallery_shell.py` — PGMainWindow signal list, existing wiring
6. `ui/arrange_canvas.py` — PGArrangeCanvas, SlotSpec, FMX_SLOTS
7. `ui/develop_canvas.py` — PGDevelopCanvas, toolstrip wiring
8. `ui/presentation_canvas.py` — PGPresentationCanvas, PGPatientWindow
9. `ui/filmstrip_wrapper.py` — PGFilmstripWrapper, set_inner_widget API
10. `adjustments.py` — EditState dataclass; all current fields
11. `canvas.py` — CanvasView, ToolType enum (7 values), set_tool() API
12. `history.py` — AdjustImageCommand, undo/redo manager
13. `filmstrip.py` — FilmstripWidget; confirm public API (signals, load_patient())
14. `template_designer.py` — TemplateDesigner; constructor signature

### Overhaul spec (architecture authority)
15. `workflows/design/PG_OVERHAUL_IMPL_SPEC_v1.md` — Phase 1 spec; read
    §0 (scope), §1 (file structure), §5 (module switching) for context

### Design Bible
16. PG Design Bible (canonical location in your skills) — check
    §6.9 (LightroomSlider), §13 (resizable surfaces), §4.3 (animation),
    §8 (empty states), §15 (section grammar) for any Phase 3 surface.

After reading, extract every `# Phase 3:` comment from files 1–4 and
group them into the 10 sections below before writing the spec.

---

## 1. Spec sections (10 required)

### §1 — EditState expansion (10 new adjustment fields)

The Develop right panel currently has 4 live sliders (Exposure/Contrast/
Saturation/Sharpen) and 10 disabled stubs (Highlights / Shadows / Whites /
Blacks / Clarity / Texture / Dehaze / Vibrance / Noise / Grain).

This section must spec:
- New fields to add to the `EditState` dataclass in `adjustments.py`.
  Confirm existing field names from your Step 0 read. Add 10 new fields
  with sensible defaults and ranges. Match the names to what
  `ImageProcessor.process()` can plausibly consume — do not invent
  rendering pipeline; just name and range the fields.
- DB migration: `edit_state_json` is a `Text` column storing serialised
  EditState. Adding new fields with defaults is non-breaking (JSON
  deserialisation with defaults). Document this explicitly.
- Slider wire-up: for each new field, the corresponding disabled
  `LightroomSlider` stub in `_DevelopRightPage` is enabled and
  connected to `_on_slider_changed(field, val)`. Spec the field→slider
  mapping table.
- ACs: EditState has 14 fields; 14 sliders active; `ast.parse` clean.

### §2 — AdjustImageCommand undo integration

Phase 2 writes EditState directly to DB on each slider change. Phase 3
adds undo/redo support via `history.py`.

This section must spec:
- Read `history.py` AdjustImageCommand API (old_state / new_state /
  image_id). Confirm the coalescing strategy: slider drags should
  coalesce into a single undo step (not one per valueChanged event).
  Specify a 400ms idle-coalesce window (debounce on the `_on_slider_changed`
  call before pushing to history).
- Integration point in `_on_slider_changed`: after DB write, push
  AdjustImageCommand to the history manager. Spec the history manager
  access path from `_DevelopRightPage` (likely via signal → PGMainWindow
  → history instance).
- ACs: slider drag produces one undo step; Ctrl+Z restores previous state;
  Ctrl+Y redoes; undo does NOT corrupt DB.

### §3 — ToolType expansion (6 unmapped tools)

Phase 2 maps 7 of 13 toolstrip tools to CanvasView. The 6 unmapped tools
(callout / pan / zoom / ruler / erase / adj_brush) need CanvasView support.

This section must spec:
- New ToolType enum members to add to `canvas.py`. Name them to match the
  toolstrip key strings (CALLOUT, PAN, ZOOM, RULER, ERASE, ADJ_BRUSH).
- Canvas handler stubs for each: what CanvasView does when set_tool() is
  called with each new type. For Phase 3, these can be real but minimal
  (pan = drag-to-scroll, zoom = click-to-zoom, ruler = click-drag measures
  distance, erase = rubber eraser on annotations, callout = wire to
  PGCalloutDrawer already present in right panel, adj_brush = Phase 4).
- Update `_TOOL_KEY_TO_TYPE` mapping table in `PGDevelopCanvas`.
- ACs: all 13 tools route through `set_tool()`; no no-ops remain; each
  tool produces observable canvas behavior.

### §4 — Filmstrip real widget integration

`PGFilmstripWrapper._inner_slot` currently holds a placeholder QLabel.
Phase 3 replaces it with the real `FilmstripWidget` from `filmstrip.py`.

This section must spec:
- Confirm `FilmstripWidget` constructor signature and `load_patient(patient_id)`
  API from your Step 0 read of `filmstrip.py`.
- Integration in `PGMainWindow`: after LibraryView `_on_library_image_selected`
  fires, call `filmstrip.set_inner_widget(FilmstripWidget())` once and
  `filmstrip.inner_widget().load_patient(patient_id)` on patient change.
  Guard with isinstance to avoid double-construction.
- Filmstrip → Develop canvas: clicking a filmstrip thumbnail while in
  Develop calls `develop_canvas.load_image(file_path)`. Spec the signal
  chain (FilmstripWidget signal → PGFilmstripWrapper passthrough →
  PGMainWindow handler).
- Filmstrip → Arrange slot drag: FilmstripWidget thumbnails are drag
  sources with MIME type `application/x-pg-image-type:<TYPE>:<uuid>`.
  Spec the drag-start implementation in FilmstripWidget (or a thin
  PGFilmstripWrapper subclass).
- ACs: filmstrip shows patient thumbnails; clicking in Develop loads the
  image in canvas; dragging to an Arrange slot fills it with the correct
  UUID.

### §5 — Cross-module navigation (Library ↔ Develop ↔ Arrange)

Phase 2 stubs several cross-module transitions. Phase 3 wires them fully.

This section must spec:
- **Library → Develop (double-click):** `_on_library_image_opened(file_path)`
  calls `switch_module("develop")` AND `develop_canvas.load_image(file_path)`.
  Also calls `right_panel.page("develop").set_context(db, image)` to load
  the image's EditState into the sliders.
- **Library → Arrange (context menu / button):** `_on_open_in_template(paths)`
  switches to Arrange AND pre-selects the paths as candidates for the first
  empty slots. Spec the pre-selection mechanic (highlight relevant filmstrip
  thumbnails; do not auto-fill slots without user action).
- **Library → Freeform:** `_on_open_in_freeform(paths)` switches to Develop
  and loads the first path; remaining paths queued in filmstrip.
- **Arrange → Develop (slot double-click):** double-clicking a filled slot
  opens the slot's image in Develop. Spec the signal from
  `PGArrangeSlot` → `PGArrangeCanvas` → `PGMainWindow` → `switch_module`.
- ACs: each transition tested with a specific AC verifying the target
  module state after the navigation.

### §6 — Arrangement save-back (drag-fill → DB write)

Phase 2 wires `slotFilled(spec, image_key)` but does not persist to DB.
Phase 3 writes back through `ArrangementAdapter`.

This section must spec:
- In `PGMainWindow._on_arrange_slot_filled()`: call
  `_arrangement_adapter.update_slot(current_arrangement_uuid, spec, image_key)`.
  Spec the `update_slot()` method to add to `ArrangementAdapter` (it does
  not currently exist; spec it as a new write method that updates the
  slot_states_json of the TemplateInstance row).
- Auto-save: Arrangements are auto-saved (no "Save" button — PG has no
  dirty state per design rules). Every slot fill, slot clear, and
  arrangement-name change persists immediately.
- New arrangement creation: when a System Template is clicked and there is
  no existing arrangement of that type for the patient, create a new
  TemplateInstance row. Spec the creation path through `ArrangementAdapter`.
- ACs: slot fill persists across app restart; new arrangements appear in
  "My Templates" on next Arrange entry; no Save button anywhere.

### §7 — Histogram widget (Develop right panel)

The `histogram_section` in `_DevelopRightPage` is a placeholder. Phase 3
replaces it with a real histogram.

This section must spec:
- A `PGHistogramWidget(QWidget)` class (new file: `ui/histogram_widget.py`).
  Input: a file path or QImage. Output: 80px-tall RGBA channel histogram
  matching the mockup in `workflows/design/pg_overhaul_mockups_v3/DEVELOP/`.
  Read the mockup for channel color grammar (R/G/B in their respective
  colors; combined luma as white; overlay mode).
- Integration: `_DevelopRightPage` replaces the histogram placeholder with
  `PGHistogramWidget`. `PGMainWindow._on_library_image_selected` triggers
  `histogram_widget.load(file_path)`. Histogram updates live as
  adjustments change (emit `editStateChanged` → recompute histogram on the
  adjusted image, not the raw file — Phase 3+ if expensive; Phase 3 can
  use raw file; note this explicitly).
- Bible compliance: 80px height per spec §7. Non-collapsible.
- ACs: histogram renders for any JPEG/TIFF/PNG; updates on image change;
  no crash on invalid file.

### §8 — Presentation DB-backed image picker

Phase 2 uses a raw `QFileDialog` file picker and stores file paths as
image keys. Phase 3 replaces this with a Library-integrated picker that
returns `PatientImage.uuid` values.

This section must spec:
- A `PGImagePickerDialog(QDialog)` class (new file: `ui/image_picker_dialog.py`)
  that shows the current patient's images as a scrollable grid of
  thumbnails. Multi-select enabled. Returns a list of `PatientImage` UUIDs.
- Integration: `PGMainWindow._on_presentation_add_images()` opens the
  picker instead of `QFileDialog`. The returned UUIDs become `QueueItem.image_key`
  values. `_resolve_image_path()` already handles UUID → file path lookup.
- Left panel slide thumbnails: the `_PresentationLeftPage` slide list
  currently shows filenames. Phase 3 shows a 48×48px thumbnail for each
  queue item (load from `PatientImage.thumbnail_path`).
- Free Browse mode: clicking a filmstrip thumbnail while in Presentation
  Live state → `slideImageRequested.emit(image_key)` → patient window
  updates. Spec the filmstrip click signal routing for Presentation.
- ACs: picker shows patient thumbnails; selected images have UUID keys;
  slide thumbnails render in left panel; Free Browse filmstrip click
  updates patient window.

### §9 — Print and Export pipelines (Arrange + Presentation)

Phase 2 ships Print and Export as disabled stubs.

**Arrange Print:**
- Spec a `PGArrangePrintDialog` or direct `QPrinter` integration. The
  template grid renders to a `QPagedPaintDevice`. Page size from the right
  panel "Page" section (`_ArrangeRightPage.page_section`). Slot images
  are drawn at their pixel sizes with labels if visible.
- Spec `_ArrangeRightPage.page_section` real content: paper size
  QComboBox (Letter / A4 / A5), orientation chips (Portrait / Landscape),
  margin spinbox.
- AC: Print enabled when all required slots are filled; dialog opens;
  page renders slot images in grid order.

**Arrange Export PDF:**
- Spec PDF export via `QPdfWriter` (Qt built-in; no external library).
  Same render path as Print. Output path: `QFileDialog.getSaveFileName`.
- AC: PDF file created; opens in system PDF viewer without error.

**Presentation Export Session:**
- Spec a session log export: a simple PDF listing each slide (filename,
  patient name, date, position) in order. No image thumbnails — text
  only. `QPdfWriter` or plain text file.
- AC: Export Session produces a file with all queued slides listed.

### §10 — Template designer integration (Arrange new template)

Phase 2 stubs the `new_template_btn` in the Arrange left panel.

This section must spec:
- Opening `TemplateDesigner` (from `template_designer.py`) when
  `new_template_btn` is clicked. Confirm `TemplateDesigner` constructor
  and modal vs modeless behaviour from your Step 0 read.
- On `TemplateDesigner` accepted: save the new `TemplateLayout` to the
  DB `templates` table; add it to the left panel "My Templates" section
  (not System Templates — user-created layouts are always "My Templates").
- Spec a `save_custom_template(layout: TemplateLayout)` method on
  `DatabaseManager` or a `TemplateRepository` helper.
- AC: new template appears in "My Templates" after designer closes;
  persists across app restart; can be selected to load in the canvas.

---

## 2. Spec format requirements

- Number every section (§1–§10) with a short title line.
- Within each section: prose description of the approach, then an
  AC table (| AC-N | Description |).
- Call out Bible rules explicitly when a new surface is introduced
  (e.g., §7 histogram: "non-collapsible per Bible §6.7 Variant A").
- Note any decisions that require Darrin approval in a `> CD DECISION:` blockquote.
- Total length target: 400–600 lines. Prioritise clarity over brevity.
- No stub or placeholder sections. Every section must be actionable.

---

## 3. What NOT to include

- Do not spec PAH, Relay, Tracker, or PC modules — not in scope.
- Do not expand the Vellum BA work — separate track.
- Do not redesign Phase 2 APIs — spec Phase 3 as additive.
- Do not spec v4.1 backlog items (solo mode, multi-monitor breakpoints,
  pen tool, partial lights out) — those live in `v4.1_BACKLOG.md`.

---

## 4. Delivery

File the spec at `C:\CODEX PG\CODEX Canonical Specs\PGO_PHASE3_IMPL_SPEC_v1.md`.

File a completion report to CD's CLAUDE Inbox:
`C:\panda-gallery\workflows\cc_mailbox\CLAUDE Inbox\`
with filename `<date>_CODEX_to_CLAUDE_pgo_phase3_spec_complete.md`.
Report must include: section count, AC count, any CD DECISION items
that need Darrin approval before Phase 3 can be dispatched to CC.

Recommended tier: **Extra-High**.

— CD
