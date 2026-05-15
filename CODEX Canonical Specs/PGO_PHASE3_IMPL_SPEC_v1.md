# PGO Phase 3 Implementation Spec v1

Status: ready for CD review / CC dispatch after Phase 2 lands
Author: Codex
Date: 2026-05-13
Target repo: `C:\panda-gallery`

## 0. Scope And Authority

Phase 3 turns the Phase 2 shell integration into working cross-module
workflow. It is additive: do not redesign Phase 2 APIs unless a small
adapter is required to satisfy an AC.

Primary source files read for this spec:

- Phase 2 Library / Develop / Arrange / Presentation dispatches
- `panda_gallery_shell.py`
- `ui/develop_canvas.py`
- `ui/arrange_canvas.py`
- `ui/presentation_canvas.py`
- `ui/filmstrip_wrapper.py`
- `filmstrip.py`
- `canvas.py`
- `constants.py`
- `adjustments.py`
- `history.py`
- `database.py`
- `template_designer.py`
- `workflows/design/PG_OVERHAUL_IMPL_SPEC_v1.md`

Bible rules to preserve:

- §6.9: adjustment controls use `LightroomSlider`.
- §13: resizable surfaces keep explicit min/default/max derivation.
- §4.3: animation uses approved timing/easing only.
- §8: empty/error states are short, useful, and action-oriented.
- §15: right/left-panel section grammar remains consistent.

Out of scope:

- PAH, Relay, Tracker, PC, and Vellum.
- v4.1 backlog items unless explicitly named here.
- Any change to the legacy `PG_USE_NEW_SHELL=0` path.

Global gates:

| Gate | Requirement |
|---|---|
| Parse | `ast.parse` clean on all modified Python files |
| Tests | full pytest suite, 0 failures |
| Lint | `pg_design_lint --changed-only` clean |
| Legacy | `PG_USE_NEW_SHELL=0` launches legacy MainWindow unchanged |
| Shell | `PG_USE_NEW_SHELL=1 python panda_gallery.py --dev` passes smoke ACs |

---

## §1 — EditState Expansion

Existing `EditState` adjustment fields are `brightness`, `contrast`,
`saturation`, and `sharpness`, plus transform/crop fields. Phase 3 adds
the ten disabled Basic-panel stubs as persisted non-destructive fields.
Missing keys in old JSON must hydrate to defaults.

Add fields to `adjustments.EditState`:

| UI label | Field | Range | Default |
|---|---|---:|---:|
| Highlights | `highlights` | -100..100 | 0.0 |
| Shadows | `shadows` | -100..100 | 0.0 |
| Whites | `whites` | -100..100 | 0.0 |
| Blacks | `blacks` | -100..100 | 0.0 |
| Clarity | `clarity` | -100..100 | 0.0 |
| Texture | `texture` | -100..100 | 0.0 |
| Dehaze | `dehaze` | -100..100 | 0.0 |
| Vibrance | `vibrance` | -100..100 | 0.0 |
| Noise | `noise` | 0..100 | 0.0 |
| Grain | `grain` | 0..100 | 0.0 |

Keep `brightness` as the storage field for the UI label `Exposure`.

Add or update helpers near `EditState`:

- `edit_state_to_json(state: EditState) -> str`
- `edit_state_from_json(payload: str) -> EditState`

The loader must ignore unknown keys and use defaults for absent keys.
`EditState.copy()` and `is_identity()` must include every new field.

Enable all Basic-panel `LightroomSlider` controls in `_DevelopRightPage`.
Wire labels to fields:

| Label | Field |
|---|---|
| Exposure | `brightness` |
| Contrast | `contrast` |
| Saturation | `saturation` |
| Sharpen | `sharpness` |
| Highlights | `highlights` |
| Shadows | `shadows` |
| Whites | `whites` |
| Blacks | `blacks` |
| Clarity | `clarity` |
| Texture | `texture` |
| Dehaze | `dehaze` |
| Vibrance | `vibrance` |
| Noise | `noise` |
| Grain | `grain` |

Grayscale images may dim/disable color controls, but values remain in
`EditState`.

| AC-1 | Description |
|---|---|
| AC-1.1 | `EditState` has 14 adjustment fields: 4 existing + 10 new. |
| AC-1.2 | Old `edit_state_json` loads with defaults for new fields. |
| AC-1.3 | Unknown JSON keys do not crash deserialization. |
| AC-1.4 | All 14 Basic sliders are active unless grayscale rules disable a color control. |
| AC-1.5 | `copy()` and `is_identity()` account for all new fields. |
| AC-1.6 | `ast.parse` passes for `adjustments.py` and right-panel files. |

---

## §2 — AdjustImageCommand Undo Integration

Phase 2 writes slider changes directly to DB. Phase 3 adds undo/redo
without creating one undo step per `valueChanged` event.

Current `history.AdjustImageCommand` is canvas-oriented:
`AdjustImageCommand(canvas, old_state, new_state, description="Adjust Image")`.
If it remains legacy-window-bound, create a shell-safe command such as
`ShellAdjustImageCommand` that updates DB, sliders, and canvas without
calling legacy-only window methods.

Required coalescing:

1. First slider movement captures `old_state`.
2. Slider changes update `pending_new_state`.
3. A 400 ms idle timer pushes one undo command.
4. Undo/redo writes DB and updates preview/sliders.

Integration:

- `_DevelopRightPage._on_slider_changed(field, value)` writes DB and
  emits `editStateChanged(EditState)`.
- `PGMainWindow._on_develop_edit_state_changed(new_state)` owns the
  coalescing timer and history push.
- Apply undo/redo with a guard such as `_syncing_sliders` to avoid
  recursive writes.

| AC-2 | Description |
|---|---|
| AC-2.1 | One continuous slider drag produces one undo step. |
| AC-2.2 | Separate slider edits produce separate undo steps. |
| AC-2.3 | `Ctrl+Z` restores visual state and DB state. |
| AC-2.4 | `Ctrl+Y` reapplies visual state and DB state. |
| AC-2.5 | Undo/redo does not recursively emit new slider writes. |
| AC-2.6 | Undo after image switch is safely blocked or scoped to the correct image. |

---

## §3 — ToolType Expansion

Existing `constants.ToolType` has:
`SELECT`, `BRUSH`, `RECT`, `ELLIPSE`, `ARROW`, `TEXT`, `CROP`, `INVERT`.

Phase 2 deliberately left six Develop toolstrip tools unmapped. Phase 3
adds enum members and observable canvas behavior.

Add:

| Tool key | New ToolType | Phase 3 behavior |
|---|---|---|
| `callout` | `CALLOUT` | show callout drawer and enter callout placement |
| `pan` | `PAN` | drag-to-scroll viewport; hand cursor |
| `zoom` | `ZOOM` | click zoom in; Alt/right-click zoom out |
| `ruler` | `RULER` | click-drag temporary measurement line in pixels |
| `erase` | `ERASE` | click/near-click removes annotation with undo support |
| `adj_brush` | `ADJ_BRUSH` | visible adjustment-brush mode with controls/status |

Update `PGDevelopCanvas._TOOL_KEY_TO_TYPE` so all 13 tools map to
`CanvasView.set_tool()`. Wire bidirectional sync:

`CanvasView.tool_changed -> PGDevelopToolstrip.set_active_tool(...)`.

Ignore sync calls when the tool is already active to avoid loops.

| AC-3 | Description |
|---|---|
| AC-3.1 | All 13 toolstrip tools route through `CanvasView.set_tool()` or equivalent. |
| AC-3.2 | No visible tool is a silent no-op. |
| AC-3.3 | Pan/zoom/ruler/erase/callout/adj_brush each show observable behavior. |
| AC-3.4 | Toolstrip and canvas active-tool states stay synchronized both ways. |
| AC-3.5 | Existing crop and legacy canvas shortcuts still work. |

---

## §4 — Filmstrip Real Widget Integration

`PGFilmstripWrapper` must host a real `FilmstripWidget`. Current
`FilmstripWidget` supports `image_selected`, `add_images`, `clear`,
`mark_placed`, `refresh_thumbnail`, and `image_paths`, but no
patient-aware loader.

Construction:

- Create one `FilmstripWidget` and install it via
  `PGFilmstripWrapper.set_inner_widget(widget)`.
- Do not recreate it on every patient change.
- Add a wrapper passthrough signal for `image_selected`.

Patient loading:

- Add `PGFilmstripWrapper.load_patient(patient_id, db=None)` or
  `FilmstripWidget.load_patient(patient_id, db)`.
- Query patient images from DB.
- Add thumbnail paths/display names to the inner widget.
- Show an empty state when the patient has no images.

Click routing by active module:

| Module | Behavior |
|---|---|
| Develop | load clicked image into Develop canvas |
| Arrange | mark/select as drag candidate |
| Presentation Build | available for queue/free-browse selection |
| Presentation Live | update patient display in Free Browse mode |

Drag payload:

- Prefer typed MIME: `application/x-pg-image-type:<TYPE>:<uuid-or-path>`.
- Also set text fallback: `<TYPE>:<uuid-or-path>`.

| AC-4 | Description |
|---|---|
| AC-4.1 | Filmstrip wrapper hosts a real `FilmstripWidget`. |
| AC-4.2 | Patient selection loads that patient's thumbnails. |
| AC-4.3 | Develop filmstrip click loads the image. |
| AC-4.4 | Arrange drag/drop fills compatible slots and rejects incompatible slots. |
| AC-4.5 | Filmstrip construction is one-time, not per selection. |
| AC-4.6 | Standalone filmstrip behavior remains intact. |

---

## §5 — Cross-Module Navigation

Phase 2 switches modules but often drops the payload. Phase 3 wires the
payloads.

Library -> Develop:

- `_on_library_image_opened(file_path)` switches to Develop.
- Resolve DB image when possible.
- Load image into Develop canvas.
- Load the image's `EditState` into right-panel sliders.
- Sync filmstrip selection.

Library -> Arrange:

- `_on_open_in_template(paths)` switches to Arrange.
- Load patient arrangements.
- Highlight passed paths in the filmstrip as candidates.
- Do not auto-fill slots.

Library -> Freeform:

- `_on_open_in_freeform(paths)` switches to Develop.
- Load the first path.
- Keep remaining paths in filmstrip.

Arrange -> Develop:

- Add slot double-click signal.
- Filled slot double-click resolves image key and opens Develop.

Series open:

- `_on_series_opened(instance_id)` switches to Arrange.
- Load the `TemplateInstance`.
- Populate slots and right-panel arrangement details.

| AC-5 | Description |
|---|---|
| AC-5.1 | Library double-click opens Develop with image loaded. |
| AC-5.2 | Open in Template switches to Arrange and marks candidates only. |
| AC-5.3 | Open in Freeform switches to Develop and loads first image. |
| AC-5.4 | Filled Arrange slot double-click opens image in Develop. |
| AC-5.5 | Saved series opens the correct `TemplateInstance`. |
| AC-5.6 | Missing/deleted images show a safe message and do not crash. |
| AC-5.7 | Patient switch clears stale cross-module payload state. |

---

## §6 — Arrangement Save-Back

Phase 2 updates visible slots and counters. Phase 3 persists arrangement
state through `TemplateInstance`.

Current DB support includes `TemplateInstance`, `save_template_instance`,
`get_template_instances`, `get_template_instance`, rename, duplicate, and
delete helpers.

Add a narrow write method:

`update_slot(instance_id, slot_spec, image_key) -> None`

Location may be `ArrangementAdapter` if it exists after Phase 2, or
`DatabaseManager` if no adapter exists. Persist at least:

| Field | Purpose |
|---|---|
| `slot_label` | e.g. `PA1` |
| `expected_type` | e.g. `PA`, `BW` |
| `image_key` | UUID preferred; path fallback allowed |
| `updated_at` | ISO timestamp |

Auto-save immediately on slot fill, slot clear, arrangement rename, and
new patient arrangement creation. Do not add a Save button.

When a System Template is selected and no patient instance exists, create
a `TemplateInstance`, copy layout JSON, assign patient id, and show it
under My Templates.

| AC-6 | Description |
|---|---|
| AC-6.1 | Slot fill persists to the current `TemplateInstance`. |
| AC-6.2 | Slot clear persists immediately. |
| AC-6.3 | Arrangement state survives restart. |
| AC-6.4 | New patient arrangements appear under My Templates. |
| AC-6.5 | No Save button is introduced. |
| AC-6.6 | Write failure shows a safe message and avoids DB corruption. |
| AC-6.7 | Filmstrip placed badges sync with persisted slot state. |

---

## §7 — Histogram Widget

Replace the Develop histogram placeholder with `PGHistogramWidget`.

New file:

`ui/histogram_widget.py`

Public API:

- `load(path: str) -> None`
- `load_image(image: QImage) -> None`
- `clear(message: str = "Select an image to show histogram.") -> None`

Render rules:

- fixed 80 px height with a §13 derivation comment
- 256 bins
- luma in soft white
- red/green/blue channels in muted channel colors
- transparent overlay blending
- downsample large images before binning

Integration:

- `_DevelopRightPage` owns the widget.
- `PGMainWindow._on_library_image_selected` and Library -> Develop call
  `histogram_widget.load(file_path)`.
- On edit changes, Phase 3 may recompute from raw file; add a comment if
  adjusted-preview histogram is deferred.

| AC-7 | Description |
|---|---|
| AC-7.1 | `PGHistogramWidget` exists in `ui/histogram_widget.py`. |
| AC-7.2 | Histogram renders for JPEG, PNG, TIFF, and BMP. |
| AC-7.3 | Histogram updates when selected image changes. |
| AC-7.4 | Invalid files show safe empty/error state. |
| AC-7.5 | Widget height is 80 px with derivation comment. |
| AC-7.6 | Right-panel section grammar remains consistent. |

---

## §8 — Presentation DB-Backed Image Picker

Phase 2 uses file paths as `QueueItem.image_key`. Phase 3 uses DB UUIDs.

New file:

`ui/image_picker_dialog.py`

Class:

`PGImagePickerDialog(db, patient_id: int, parent=None)`

Required API:

- multi-select thumbnail grid for current patient
- `selected_image_uuids() -> list[str]`
- OK disabled until one image is selected

`PGMainWindow._on_presentation_add_images()` opens the dialog. For each
selected uuid, resolve `PatientImage`, then create:

`QueueItem(image_key=uuid, filename=display_name, thumbnail_path=thumbnail_path)`.

Update `_resolve_image_path()` to prefer UUID lookup. Keep path fallback
for Phase 2 queue items.

Presentation left panel:

- show 48 x 48 thumbnail per slide row
- include position number and compact filename/type/date
- maintain active-slide styling

Free Browse Live:

`FilmstripWidget.image_selected -> PGMainWindow -> presentation_canvas.slideImageRequested -> PGPatientWindow`.

| AC-8 | Description |
|---|---|
| AC-8.1 | Picker shows current patient thumbnails. |
| AC-8.2 | Multi-select returns `PatientImage.uuid` values. |
| AC-8.3 | New queue items use UUID keys. |
| AC-8.4 | Left-panel slide rows show 48 x 48 thumbnails. |
| AC-8.5 | Free Browse filmstrip click updates patient window in Live state. |
| AC-8.6 | Path fallback remains for older queue items. |
| AC-8.7 | No-image patient state is clear and non-crashing. |

---

## §9 — Print And Export Pipelines

Phase 3 enables Arrange Print/Export, Presentation Export Session,
Presentation Stop, and auto-advance.

Arrange page settings:

- paper size: Letter / A4 / A5
- orientation: Portrait / Landscape
- margin spinbox
- defaults: Letter, Portrait, 0.25 in

Arrange Print:

- enabled when at least one slot is filled
- use `QPrinter` + `QPrintDialog`
- shared render helper draws grid, slot images, labels if visible

Arrange Export PDF:

- use `QPdfWriter`
- no external PDF dependency
- default to last export folder, else `exports/arrangements`

Presentation Export Session:

- text-only PDF via `QPdfWriter`
- include patient display name, timestamp, slide position, filename,
  image type, and image date when known
- no thumbnails in Phase 3

Auto-advance:

- compact interval control in Presentation right panel
- `QTimer` advances only in Live + Curated mode
- stops on End, Escape, mode switch, or empty queue

Stop/End:

- enabled in Live state
- uses same `endRequested` path as Escape

| AC-9 | Description |
|---|---|
| AC-9.1 | Arrange page settings have real controls. |
| AC-9.2 | Arrange Print opens dialog and renders slot images in grid order. |
| AC-9.3 | Arrange Export PDF creates a readable PDF. |
| AC-9.4 | Presentation Export Session creates text-only PDF. |
| AC-9.5 | Export path remembers last folder where supported. |
| AC-9.6 | Auto-advance works only in Live + Curated. |
| AC-9.7 | Auto-advance stops on End/Escape/mode switch/empty queue. |
| AC-9.8 | Stop/End button returns to Build. |
| AC-9.9 | No external PDF dependency is introduced. |

---

## §10 — Template Designer Integration

Phase 3 wires `PGArrangeCanvas.new_template_btn` to the existing
`TemplateDesigner`.

Confirmed API:

- `TemplateDesigner(layout: TemplateLayout = None, parent=None)`
- `template_saved = Signal(TemplateLayout)`
- Save and Save As emit `template_saved`

Flow:

1. Add `PGArrangeCanvas.newTemplateRequested`.
2. Button click emits the signal.
3. `PGMainWindow._on_arrange_new_template_requested()` opens
   `TemplateDesigner(parent=self)`.
4. Connect `template_saved` to a shell handler.
5. Save via `DatabaseManager.save_template(layout)` or repository
   equivalent.
6. Refresh My Templates.

User-created templates always appear under My Templates, not System
Templates. If no arrangement is open, the new template may be selected
after save. If an arrangement is open, refresh the list and leave canvas
state unchanged.

| AC-10 | Description |
|---|---|
| AC-10.1 | `+ New Template` opens `TemplateDesigner`. |
| AC-10.2 | Save persists through `save_template` or repository equivalent. |
| AC-10.3 | Saved templates appear under My Templates. |
| AC-10.4 | Saved templates survive restart. |
| AC-10.5 | Selecting the saved template loads it in Arrange canvas. |
| AC-10.6 | Save failure shows safe message and does not crash. |

---

## 11. Recommended Implementation Order

1. EditState expansion and slider enablement.
2. Library -> Develop payload loading.
3. Filmstrip real widget and patient loading.
4. Arrange typed drag/drop and save-back.
5. Presentation DB image picker and UUID queue entries.
6. Histogram widget.
7. Print/export and auto-advance.
8. TemplateDesigner integration.
9. ToolType expansion and bidirectional sync.
10. Undo coalescing.

This order lands workflow identity and persistence before deeper editing
behavior.

## 12. CD Decision Items

Defaults in this spec:

| Item | Default |
|---|---|
| Arrange Print readiness | enabled with at least one filled slot |
| Presentation Export Session | text-only PDF, no thumbnails |
| TemplateDesigner window mode | modeless |
| Adjustment processor support | fields persist now; renderer may no-op unsupported fields with comments |
| `ADJ_BRUSH` | observable mode required; full mask editing may be separately dispatched |

> CD DECISION: If any default above needs Darrin approval or a different ruling, amend before dispatch.

## 13. Roll-Up Acceptance Criteria

| AC-R | Description |
|---|---|
| AC-R1 | All ten sections are implemented or explicitly deferred by CD ruling. |
| AC-R2 | Library -> Develop, Library -> Arrange, Arrange -> Develop, and Presentation queue setup work. |
| AC-R3 | DB-backed image identity uses UUIDs where available. |
| AC-R4 | `PG_USE_NEW_SHELL=0` remains unchanged. |
| AC-R5 | `ast.parse`, pytest, and `pg_design_lint --changed-only` are clean. |
| AC-R6 | Completion report lists any CD-approved deferrals. |
