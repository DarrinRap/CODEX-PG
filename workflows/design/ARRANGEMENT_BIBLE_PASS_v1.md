# Arrangement Bible Compliance Pass v1

Date: 2026-04-26
Author: Codex
Scope: Arrange module, unified arrangement canvas, arrangement library, persistence, and handoff to Review/Present.

## 0. Executive Summary

The Arrange module should collapse the old Template/Freeform split into one canonical mental model:

> Every saved layout is an Arrangement. Some arrangements begin from a grid preset. Some begin empty. All are edited on the same canvas.

This pass keeps the live strengths already present in Panda Gallery:

- `freeform_view.py` already has the correct QGraphicsScene foundation, filmstrip drag/drop, smart guide manager, snap/chain placement, keyboard panning, delete, rotate, and state serialization.
- `template_view.py` already has mature slot interaction, annotations/adjustments display, zoom behavior, drag/drop, and slot edit state.
- `template_data.py` already has a clean data layer that can become the seed for `Arrangement` and `ArrangementItem`.
- `panda_gallery.py` already persists freeform work through the template instance path, which gives migration a real bridge instead of a cold start.

The main design change is language and structure:

- The module is `Arrange`.
- The saved object is a `Mount`.
- The backend model may be named `Arrangement` for clarity and versioning.
- Template Library becomes `My Mounts` or `Mount Library` in user-facing UI.
- Built-in layouts are starting points, not a separate module or separate editor.

The pass also carries forward the Bible rules that matter most here:

- Section 1.4: no idle chrome, no decorative whitespace, every visible control earns its presence.
- Section 1.5: controls must be operational, not explanatory filler.
- Section 1.6: every primary affordance needs empty, hover, active, disabled, loading, and error states.
- Section 2: no white or near-white UI backgrounds; colors must use tokens.
- Section 6.22: module headers use the shared PG module header grammar.
- Section 13: resize, persistence, cleanup, and state restoration are part of the feature, not polish.

## 1. Surface Inventory

### 1.1 Arrange Module Header

Current state:

- The app has historical Template/Freeform entry points.
- The v4 strategy locks the module set to Library / Arrange / Review / Present.

Target:

- The top-level module header says `Arrange`.
- Header actions are limited to real work: `New Mount`, `Open`, `Save`, `Present`, and overflow.
- No explanatory subtitle such as "create beautiful templates" belongs in the chrome.
- Unsaved state appears as a compact `Unsaved` status chip near the title or save control.

Required states:

- No mount open.
- Mount open and clean.
- Mount open and dirty.
- Saving.
- Save failed.
- Export/present preparation running.

### 1.2 Mount Library

Current state:

- `TemplateLibraryDialog` has a working card grid, search, archive toggle, slider, and a Freeform card at index 0.
- It still exposes the old split between templates and freeform.

Target:

- Rename the surface to Mount Library.
- Cards represent user mounts and built-in starting layouts in one grid.
- Filters separate `All`, `Saved`, `Built-in`, and `Archived`.
- The first card is `Blank Mount`, not "Freeform".
- Built-in FMS, Bitewing Set, Periapical Series, and Custom 2x3 remain useful starting points for v4.0.
- Archived mounts appear only when `Show archived` is enabled.

Card taxonomy:

- `Saved mount`: user-owned, editable, archivable, duplicateable.
- `Built-in starting layout`: shipped preset, not archived, duplicate-on-edit.
- `Blank mount`: creates an empty freeform canvas.
- `Draft mount`: unsaved local object with a temporary id and clear dirty state.

Empty states:

- Search empty: "No mounts match this search."
- Saved empty: "No saved mounts yet."
- Archived empty: "No archived mounts."

Removal test:

- Remove the card-size slider if it does not materially improve the dense operational workflow. If retained, it belongs in overflow or view options, not primary toolbar.
- Remove any freeform/template explanatory banners. Users choose a mount and edit it.

### 1.3 Canvas Shell

Current state:

- Freeform and template use separate QGraphicsView-based editors.
- Freeform persistence exists, but through a minimal template instance shim.
- Template designer is retired and should not return as a separate user-facing module.

Target:

- One Arrange canvas shell hosts all mounts.
- Built-in grid layouts and blank freeform mounts share the same toolbar, filmstrip, properties panel, and status model.
- The canvas itself is the primary surface, not a dialog floating above another workflow.

Default desktop anatomy:

- Top: module header.
- Left: mount navigator, compact and collapsible.
- Center: canvas viewport.
- Right: properties/inspector panel.
- Bottom: filmstrip.
- Bottom status line: save/export/navigation feedback.

Narrow anatomy:

- Header stays visible.
- Navigator and inspector become tabbed drawers.
- Filmstrip remains reachable as a horizontal tray.
- Canvas remains first-priority and must not be squeezed below usefulness.

Wide anatomy:

- Canvas expands.
- Navigator and inspector retain maximum readable widths.
- Filmstrip uses the extra width for more visible images, not taller chrome.

### 1.4 No Mount Open

Target state:

- The canvas area shows the Mount Library grid or a compact start panel.
- Primary action: `New Mount`.
- Secondary action: `Open Saved`.
- Built-in starting layouts are visible without a modal if there is room.

No empty filler:

- Do not show decorative illustrations, marketing text, or large blank instructional cards.
- Do not explain what arrangement means in the app surface.

### 1.5 Empty Mount Open

Target state:

- A blank canvas is open.
- The filmstrip is populated from the current image set.
- The right inspector shows mount-level fields: name, canvas size, background, grid/snap, default spacing.
- The status line says `Drop images to place them` only if no image has been placed.

Allowed visible aids:

- Low-contrast canvas boundary.
- Optional dot/grid texture using tokenized subtle colors.
- Snap indicator only while dragging or moving.

Disallowed:

- White canvas background.
- Permanent rulers by default.
- Static instructional banners.

### 1.6 FMS Starting Layout, No Images

Target state:

- Slots are pre-placed and visibly empty.
- Slot labels are concise: UR1, UR2, etc. or numeric positions if the source layout lacks dental naming.
- Empty slots use a tokenized quiet fill and border, not white.
- The right inspector shows selected slot details only after slot selection.

Interaction:

- Drag from filmstrip to slot.
- Click image, then click slot is supported for trackpad/accessibility.
- Double-click slot opens image chooser only if the existing app already has a chooser pattern; otherwise avoid adding another modal path.

### 1.7 Partially Populated Mount

Target state:

- Placed images render using the real radiograph thumbnail/image when available.
- Empty slots remain readable.
- The user can see which images have been placed from the filmstrip through used badges or reduced emphasis.
- The status line indicates saved/unsaved state, not instructional filler.

Primary operations:

- Replace image in slot.
- Remove from slot.
- Rotate image within slot.
- Adjust fit/fill.
- Open Review for selected image when Review is available.

### 1.8 Custom Freeform Mount

Target state:

- Images are freeform items on the same canvas.
- Dragging shows smart guides only when relevant.
- Collision/snap logic remains derived from existing `FreeformScene` behavior.
- The properties panel exposes x/y/width/height/rotation for selected items.

Important distinction:

- Freeform items have resize handles.
- Template/slot items do not get arbitrary resize handles in normal edit mode; they use slot-level fit/scale controls.
- Slot geometry can be edited only when the mount is explicitly in layout-edit mode.

### 1.9 Properties Panel

Current state:

- Template Designer had a right panel that could hide selected properties below the fold (#76).
- Freeform has little inspector surface.

Target:

- The right panel is dense, scrollable, and grouped into collapsible sections.
- It must never hide the active selection's primary controls below the fold.
- The first section always reflects current selection:
  - No selection: mount properties.
  - One freeform item: image placement and transform.
  - One slot: slot content and fit.
  - Multi-select: align, distribute, group operations where supported.

Sections:

- Selection.
- Image.
- Placement.
- Fit and rotation.
- Annotations display.
- Mount metadata.

### 1.10 Filmstrip

Current state:

- Filmstrip drag/drop exists and should remain the primary image source.

Target:

- The filmstrip is the only primary drag source.
- Used images show a placed marker.
- Missing files show an error marker.
- Drag preview uses tokenized focus/accent styling.
- Filmstrip height is fixed by density class and cannot grow because of filename length.

### 1.11 Save Flow

Current state:

- `SaveLayoutDialog` and template instance persistence exist.

Target:

- `Ctrl+S` saves current mount.
- First save opens a compact save dialog for name and optional description.
- `Ctrl+Shift+S` duplicates/saves as.
- Saving disables the save button and writes `Saving...` in the status line.
- Success writes `Saved`.
- Failure writes `Save failed` with retry action.

No toast-only save result. The state must be discoverable after the transient animation ends.

### 1.12 Export and Present Handoff

Target:

- Export is not a full PDF/pro-grade export feature for v4.0.
- Present handoff creates a `PresentationState` that contains a rendered mount plus enough metadata for Review/Present navigation.
- Export/present preparation uses a restrained activity state:
  - Under 500ms: disable initiating action only.
  - Over 500ms: show status-line progress and a subtle inline shimmer in the action area.

### 1.13 Error States

Required errors:

- Missing source image.
- Failed image load.
- Failed save.
- Failed migration.
- Unsupported arrangement schema version.
- Renderer failed to create output.
- Unsaved changes conflict when switching mounts.

Error presentation:

- Use tokenized error border/text.
- Keep the canvas usable when only one item has failed.
- Use modal confirmation only for destructive or conflict decisions.

## 2. Interaction Model

### 2.1 Pointer Model

Primary pointer actions:

- Drag image from filmstrip to canvas or slot.
- Drag placed freeform item to move.
- Drag resize handles on freeform item.
- Drag rotation handle on freeform item.
- Click slot to select.
- Double-click placed image to inspect/zoom if the existing Review path is available.

Drag performance rule:

- During `dragMoveEvent`, show ghost position and candidate guides.
- Run expensive collision and chain resolution on drop or throttled move, not every raw event.

### 2.2 Click-To-Place Model

Click-to-place exists for accessibility and trackpad use:

1. Click a filmstrip image.
2. The image receives a selected-for-placement state.
3. Click an empty slot or canvas location.
4. The image is placed.
5. Placement selection clears.

Esc clears selected-for-placement before it attempts to leave the screen.

### 2.3 Selection Model

Single selection:

- Shows focus ring and item controls.
- Opens selection section in inspector.
- Enables remove, rotate, and fit controls as applicable.

Multi-selection:

- Ctrl-click toggles.
- Shift-click range selection may apply only in filmstrip, not canvas.
- Multi-select freeform items show a bounding box and align/distribute operations.
- Multi-select slots allows clear/remove only in v4.0 unless the grid editor explicitly supports batch layout edits.

No selection:

- Inspector returns to mount settings.
- Delete and rotate are disabled.

### 2.4 Handle Component

Freeform selected item:

- 8 resize handles.
- 1 rotation handle above the top edge.
- Handles use tokenized accent border and muted fill.
- Minimum hit target is 12px even if visual handle is smaller.
- Handles do not resize the item when hovered.

Slot selected item:

- Slot focus outline only.
- No free-resize handles in normal edit mode.
- Fit/scale controls appear in inspector.

Layout edit mode:

- Slot geometry handles may appear only after explicit `Edit Layout`.
- Built-in presets duplicate before edit.

### 2.5 Snap and Guide Feedback

Freeform snap:

- Preserve the current smart guide manager and chain resolver.
- Use tokenized guide color, not hard-coded blue.
- Valid snap/selection border must not use `#FFFFFF`.
- Invalid overlap/drop must use the error token, not raw red.

Slot snap:

- A slot under drag receives a target highlight.
- Valid target uses accent border.
- Invalid target uses error border.
- Occupied slot supports replace preview only if replacement is allowed.

Guide lifetime:

- Guides appear only while moving, resizing, or dropping.
- Guides disappear immediately when interaction ends.

### 2.6 Keyboard Model

Required keys:

- Esc: cancel drag; if no drag, clear placement selection; if none, clear canvas selection; if dirty and leaving, ask to save/discard/cancel; otherwise return to Mount Library or prior screen.
- Delete/Backspace: remove selected item or clear selected slot.
- Arrow keys: nudge selected freeform item by 1px.
- Shift+Arrow: nudge by 10px.
- Space held: pan canvas.
- Home: fit canvas.
- R: rotate selected image 90 degrees.
- Ctrl+S: save.
- Ctrl+Shift+S: save as/duplicate.
- Ctrl+Z/Ctrl+Y: undo/redo when undo stack lands.

Esc is stateful; it must not close the main window from Screen A/no-open state.

### 2.7 Navigation Model

Back behavior:

- From open mount to Mount Library.
- If dirty, ask Save / Discard / Cancel.
- If export/present is running, ask only if cancellation is meaningful; otherwise disable Back until the operation resolves.

Navigation stack:

- Record open mount id, scroll/zoom, selected item, dirty state, and active inspector section.
- Restore the mount state when returning from Review/Present.

## 3. Visual Spec

### 3.1 Token Rules

Immediate cleanup required in Arrange code:

- `freeform_view.py` selection valid color currently uses `#FFFFFF`; replace with a tokenized accent/focus color.
- `freeform_view.py` invalid color currently uses `#FF4444`; replace with the error token.
- Existing `#4488FF` guide color and `#e8a87c` selection color should move behind tokens or an Arrange token alias.

No near-white surfaces:

- Canvas background may be dark neutral, graphite, or muted working gray.
- Empty slots use subtle fill and border.
- Image matte can be dark but should not hide radiograph edges.

### 3.2 Canvas Chrome

Default:

- Dark working surface.
- Canvas boundary visible.
- No permanent ruler.
- No decorative grid unless snap/grid mode is enabled.

When grid/snap enabled:

- Dot or line grid at low opacity.
- Grid color tokenized and subordinate to image content.

### 3.3 Density

Default desktop:

- Header 48-56px.
- Bottom filmstrip 112-144px.
- Left navigator 220-260px.
- Right inspector 280-340px.

Narrow:

- Side panels become drawers/tabs.
- Minimum canvas working height must remain at least 360px when possible.

Wide:

- Canvas grows.
- Inspector maxes out rather than stretching text controls.

### 3.4 Activity States

Saving:

- Disable Save.
- Status line: `Saving...`.
- No spinner unless over 500ms.

Export/present:

- Disable conflicting actions.
- Status line reports action.
- Subtle shimmer only after 500ms.

Loading mount:

- Preserve shell.
- Skeleton the canvas items only if data load is long enough to be perceived.

## 4. Data Model

### 4.1 Canonical Arrangement Object

The durable model should be versioned and renderer-friendly.

```python
@dataclass
class Arrangement:
    arrangement_id: str
    arrangement_schema_version: int
    patient_id: str | None
    name: str
    description: str
    layout_type: Literal["grid", "freeform", "mixed"]
    canvas_width: int
    canvas_height: int
    background_token: str
    gap_px: int
    items: list[ArrangementItem]
    is_builtin_preset: bool
    is_user_starting_point: bool
    archived: bool
    thumbnail_path: str | None
    ai_metadata: dict
    created_at: datetime
    updated_at: datetime
```

### 4.2 Arrangement Item

```python
@dataclass
class ArrangementItem:
    item_id: str
    source_image_id: str | None
    image_path: str | None
    role: Literal["slot", "freeform"]
    slot_index: int | None
    grid_row: int | None
    grid_col: int | None
    x: float
    y: float
    width: float
    height: float
    rotation_deg: float
    z_order: int
    sensor_size: str | None
    orientation: str | None
    label: str
    fit_mode: Literal["fit", "fill", "stretch"]
    adjustments: dict
    annotations: dict
    ai_metadata: dict
    locked: bool
```

### 4.3 Versioning

Rules:

- `arrangement_schema_version` is required for every saved mount.
- Unknown future versions open read-only with a clear unsupported-version state.
- Migrations are explicit functions and are covered by smoke tests.
- AI metadata is reserved but invisible in v4.0.

### 4.4 Migration From Current Template Data

Existing `TemplateLayout`:

- Becomes an `Arrangement` with `layout_type="grid"`.
- Each `TemplateSlot` becomes an `ArrangementItem` with `role="slot"`.
- `TemplateInstance.slot_states` populate source image and fit data.
- Built-in templates seed built-in starting layouts.

Existing freeform state:

- Current freeform persistence in `panda_gallery.py` stores a `layout_json={"layout_type": "freeform"}` plus serialized slot state.
- Migrate those records into `Arrangement(layout_type="freeform")`.
- Each freeform image becomes `ArrangementItem(role="freeform")`.
- Run the existing chain resolver on migration if stale overlap is detected (#105).
- Preserve the existing instance id where feasible; otherwise store an old-id mapping.

Template Designer:

- Retired as a separate user-facing surface.
- Its grid math can be reused.
- Its old dialog frame should not be preserved as a v4.0 feature.

### 4.5 Renderer Contract

Keep this intentionally small for v4.0.

```python
class ArrangementRenderer:
    def render(
        self,
        arrangement: Arrangement,
        target: RenderTarget,
        annotation_filter: AnnotationFilter,
    ) -> QPixmap:
        ...
```

Render targets:

- Screen preview.
- Thumbnail.
- Presentation handoff.
- Basic image export if already supported by the app.

Do not add pro-grade PDF/export controls in v4.0.

Annotation filter:

- Use an enum, not a boolean.
- Suggested values: `none`, `clinical`, `all`.

### 4.6 Presentation State

Present handoff should pass an immutable snapshot:

```python
@dataclass(frozen=True)
class PresentationState:
    arrangement_id: str
    arrangement_name: str
    rendered_pixmap: QPixmap
    source_item_ids: tuple[str, ...]
    annotation_filter: AnnotationFilter
    created_at: datetime
```

The Present module owns monitor/fullscreen behavior. Arrange owns only preparation and handoff.

## 5. State Machine

Required states:

- `no_mount_open`
- `library_open`
- `mount_empty_clean`
- `mount_empty_dirty`
- `mount_populated_clean`
- `mount_populated_dirty`
- `single_item_selected`
- `multi_item_selected`
- `drag_in_progress`
- `resize_in_progress`
- `rotate_in_progress`
- `save_dialog_open`
- `saving`
- `save_failed`
- `export_in_progress`
- `migration_failed`
- `unsupported_schema_readonly`

Critical transitions:

- Library card -> open clean mount.
- Blank mount -> empty dirty draft.
- Drop image -> populated dirty.
- Save success -> clean.
- Back while dirty -> save/discard/cancel.
- Esc follows the same staged cancellation order as section 2.6.

## 6. Implementation Sequencing

### Batch A: Canonical Model and Migration

Deliverables:

- Add `Arrangement` and `ArrangementItem`.
- Add DB persistence with schema version.
- Migrate templates and current freeform instances.
- Add migration tests for grid, freeform, and stale overlap.

Gate:

- Existing saved freeform work opens as a mount.
- Existing templates open as built-in starting layouts.

### Batch B: Mount Library

Deliverables:

- Rename/reframe `TemplateLibraryDialog` into Mount Library.
- Merge blank, built-in, saved, and archived cards.
- Add filters and corrected empty states.
- Remove obsolete template/freeform split language.

Gate:

- User can create blank mount, open built-in layout, open saved mount, archive/restore user mount.

### Batch C: Unified Canvas Shell

Deliverables:

- Shared Arrange shell with header, canvas, inspector, filmstrip, and status line.
- Route freeform and grid arrangements through the same screen.
- Preserve current filmstrip drag/drop.

Gate:

- No separate freeform/template editor choice is visible to the user.

### Batch D: Canvas Editing

Deliverables:

- Freeform move/resize/rotate handles.
- Slot placement and replacement.
- Tokenized snap/selection/error guides.
- Keyboard model, including Esc state order.
- Inspector panel states.

Gate:

- Mouse and keyboard can complete a simple FMS and a custom freeform mount.

### Batch E: Save, Renderer, and Handoff

Deliverables:

- Save/save-as flow.
- Thumbnail rendering.
- Renderer contract.
- PresentationState handoff.
- Export/present progress states.

Gate:

- Arrange can pass a rendered mount to Present without adding PDF/pro export scope.

### Batch F: Cleanup, Resize, and Regression

Deliverables:

- QGraphicsScene/QUndoStack shutdown cleanup for #79.
- Navigation stack restoration for #116.
- Right panel fold/scroll fix for #76 replacement surface.
- Resize smoke tests across narrow/default/wide.

Gate:

- App closes without QGraphics cleanup warnings.
- Canvas state survives navigation away and back.

## 7. Bible Amendments Recommended

### 7.1 New Section: Arrangement Canvas

Add a canonical component for the Arrange canvas:

- Anatomy: module header, navigator, canvas viewport, inspector, filmstrip, status line.
- Default/narrow/wide sizing.
- Canvas color rules.
- Empty/dirty/saving/error states.
- Keyboard and Esc behavior.

### 7.2 New Section: Selection Handles

Define:

- Freeform handle count and hit target.
- Rotation handle placement.
- Slot selection outline.
- Disabled/locked item presentation.
- Tokenized colors.

### 7.3 New Section: Smart Guides and Snap Feedback

Define:

- Guide lifetime.
- Valid/invalid target styling.
- Performance rule for drag move vs drop.
- No permanent guide clutter.

### 7.4 Mount Library Card Taxonomy

Define:

- Saved mount.
- Built-in starting layout.
- Blank mount.
- Draft mount.
- Archived mount.

### 7.5 Shared Activity Indicator

Carry forward the AM pass recommendation:

- Under 500ms, disable initiating control only.
- Over 500ms, show restrained inline progress.
- Success/failure must leave discoverable state.

## 8. Open Questions for Claude/Darrin

1. Should user-facing saved arrangements be called `Mounts` everywhere, while code uses `Arrangement`, or should the UI also say `Arrangement` outside internal docs?
2. Do any real user freeform saves exist in Darrin's current working database that must be preserved exactly, including ids and thumbnails?
3. Should layout-edit mode ship in v4.0, or should built-in starting layouts duplicate to editable freeform/grid mounts without exposing a full slot designer?
4. Should the first v4.0 Present handoff include annotation rendering, or should annotations be visible only in Review until the Present module lands?
5. Should `Blank Mount` be a permanent first card or a header button only? My recommendation is both: header button for speed, card for discoverability.

## 9. Non-Goals

- No return of Template Designer as a separate primary feature.
- No pro PDF/export suite in v4.0.
- No AI-visible arrangement suggestions in v4.0 UI.
- No DICOM/HIPAA/installer commitments.
- No decorative education panels.
- No new visual language outside Bible tokens.

## 10. Acceptance Checklist

- Arrange module opens to a useful Mount Library or current mount, not a split Template/Freeform decision.
- Built-in FMS and blank mounts open in the same canvas shell.
- Empty, partially populated, and custom freeform states are all designed.
- Save, saving, saved, and failed states are explicit.
- Esc behavior is stateful and does not close the app unexpectedly.
- Freeform selection does not use white or raw red literals.
- Migration preserves current template and freeform saved work.
- Present handoff has a renderer snapshot contract.
- Narrow/default/wide layouts keep the canvas usable.
- The Bible receives Arrangement Canvas, Handles, Smart Guides, Mount Card, and Activity Indicator amendments.
