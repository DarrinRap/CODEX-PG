# PG Image Mount Architecture Spec v1

Status: Draft for CD review
Created: 2026-05-08
Owner: Codex
Project: Panda Gallery
Spec type: Data model and implementation rules
Canonical spec path: C:\CODEX PG\CODEX Canonical Specs\PG_IMAGE_MOUNT_ARCHITECTURE_SPEC_v1.md

Primary decision: Option A - images first.

Approval route:
- This spec is for Claude Desktop review before any Claude Code implementation dispatch.
- Codex must not send implementation-go or commit-go tokens directly to Claude Code.
- Claude Desktop owns formal Claude Code authorization.

Primary implementation targets if approved later: see Section 8.2.

Reference artifacts reviewed: v4 spec, v4 MVP plan, template specs, freeform spec, image info spec, and overhaul mockups under C:\panda-gallery.

Terms used in this spec:
- ImageRecord: one imported clinical image and its metadata.
- Arrangement: a saved mount, FMX, series, freeform board, comparison board, or named layout.
- Slot: one placement location inside an Arrangement.
- Placement: the Slot-level instruction for how an ImageRecord is displayed inside a Slot.
- Render: a generated pixel output for preview, print, or export.
- Broken slot: a Slot whose referenced ImageRecord is deleted, missing, or unavailable.
- Loose image: an ImageRecord that is not referenced by any active Arrangement slot.

Non-negotiable principle:
- The imported image is the durable clinical object.
- Arrangements are named collections of references to imported images.
- Moving an image into an FMX slot does not create a second clinical image.
- Deleting or archiving an arrangement does not delete the original images.
- Archiving an image does not destroy the arrangement; it leaves the slot visible as archived-linked.

Why this matters:
- The library remains the source of truth for patient images.
- The same image can appear in several clinical contexts without duplicate files.
- Develop edits remain non-destructive and can be shared across displays.
- Exports can be reproduced because every layout points back to stable image identifiers.
- The model matches the way dental image software treats images, mounts, templates, and series.

## 1. Data Model

1.1 Canonical relationship
- One patient can own many ImageRecords.
- One patient can own many Arrangements.
- One Arrangement can own many Slots.
- One Slot can reference zero or one ImageRecord.
- One ImageRecord can be referenced by many Slots.
- One ImageRecord can appear in many Arrangements.
- One ImageRecord can appear more than once in the same Arrangement, but the UI must show a duplicate-use warning.

1.2 ImageRecord identity
- Every ImageRecord must have a stable public UUID.
- Existing integer database identifiers can remain as internal legacy IDs.
- UI code, Arrangement data, exports, and handoff data must use UUIDs for references.
- File paths must not be used as identity.
- Display labels must not be used as identity.
- Content hashes must not be used as identity because two intentional imports may share the same hash.

1.3 ImageRecord logical schema

```text
ImageRecord
  uuid: string UUID, required, stable
  legacy_id: integer, optional, migration bridge from PatientImage.id
  patient_id: integer or patient UUID, nullable only for unassigned images
  original_filename: string, required
  stored_filename: string, required
  original_path: string relative to originals directory, required
  thumbnail_path: string relative path, optional but expected after import
  preview_path: string relative path, optional
  content_hash: string, optional but recommended
  width: integer, optional until image probe completes
  height: integer, optional until image probe completes
  file_size: integer, optional until image probe completes
  mime_type: string, optional
  image_type: enum, required, defaults to unknown
  category: enum or string, optional
  captured_date: datetime, optional
  imported_at: datetime, required
  imported_by: string, optional
  import_source: string, optional
  display_label: string, optional
  notes: string, optional
  tags: list of strings, optional
  tooth_numbers: list of strings, optional
  status: enum active | archived | deleted | missing, required
  archived_at: datetime, optional
  archived_by: string, optional
  deleted_at: datetime, optional
  deleted_by: string, optional
  edit_state_json: JSON object, required, defaults to empty object
  annotation_state_json: JSON object, optional
  audit_state_json: JSON object, optional
  created_at: datetime, required
  updated_at: datetime, required
```

1.4 ImageRecord status rules
- active means the image is available for normal Library, Develop, Arrange, and Export use.
- archived means the image is hidden from normal Library browsing unless the archive filter is enabled.
- deleted means the image is soft-deleted and must not be exported unless an administrator explicitly restores it first.
- missing means the database record exists but the stored file cannot be found.
- Archived, deleted, and missing images must keep their UUIDs.
- Archived, deleted, and missing images must not be silently removed from Arrangements.
- A restore operation must reconnect all Slots that still reference the restored UUID.

1.5 ImageRecord edit rules
- Develop edits are stored on the ImageRecord as non-destructive parameters.
- The original stored file remains unchanged.
- Arrangement Slots display the current ImageRecord render by default.
- Slot-specific display choices belong to the Slot, not the ImageRecord.
- Global edits include operations such as invert, brightness, contrast, grayscale, rotation correction, crop intended as clinical image edit, annotations, and label changes.
- Placement edits include fit mode, slot crop, slot zoom, slot pan, slot rotation, mirror display if permitted, and local label visibility.
- If a future workflow needs a frozen historical view, it must use a named snapshot reference rather than copy the original image.

1.6 Arrangement identity
- Every Arrangement must have a stable public UUID.
- Existing TemplateInstance IDs can remain as internal legacy IDs.
- The Arrangement UUID is the identity used by exports, Library cards, Arrange tabs, and handoff packages.
- A reusable blank template is not an Arrangement.
- An Arrangement is a patient-specific saved instance of a template or freeform layout.

1.7 Arrangement logical schema

```text
Arrangement
  uuid: string UUID, required, stable
  legacy_template_instance_id: integer, optional
  patient_id: integer or patient UUID, required
  name: string, required
  arrangement_type: enum fmx | bitewing_series | pano_series | comparison | freeform | custom | imported_session
  template_id: string or integer, optional
  template_version: string or integer, optional
  visit_date: date or datetime, optional
  source_session_id: string UUID, optional
  status: enum active | archived | deleted, required
  layout_json: JSON object, required
  slots: list of Slot objects or normalized slot rows, required
  thumbnail_path: string relative path, optional
  export_preset_json: JSON object, optional
  notes: string, optional
  tags: list of strings, optional
  created_by: string, optional
  created_at: datetime, required
  updated_at: datetime, required
```

1.8 Slot logical schema

```text
Slot
  slot_id: string, required, stable inside the Arrangement
  placement_id: string UUID, required, stable for this Slot placement
  label: string, optional
  image_ref: string ImageRecord UUID, nullable
  expected_image_type: enum or string, optional
  tooth_numbers: list of strings, optional
  region_hint: string, optional
  required: boolean, required, defaults to false
  position: object { x, y }, required
  size: object { width, height }, required
  rotation_degrees: number, required, defaults to 0
  z_index: integer, required
  fit_mode: enum contain | cover | stretch | original_size, required
  slot_crop: object, optional
  slot_zoom: number, optional
  slot_pan: object { x, y }, optional
  slot_rotation_degrees: number, optional
  local_label_visible: boolean, required, defaults to true
  duplicate_use_acknowledged: boolean, required, defaults to false
  locked: boolean, required, defaults to false
  created_at: datetime, required
  updated_at: datetime, required
```

1.9 Slot reference rules
- A Slot with image_ref null is empty.
- A Slot with image_ref set to an active ImageRecord is occupied.
- A Slot with image_ref set to an archived ImageRecord is archived-linked.
- A Slot with image_ref set to a deleted or missing ImageRecord is broken-linked.
- Slot state must be derived from the referenced ImageRecord status when possible.
- The Slot must keep image_ref even when the referenced image is archived, deleted, or missing.
- Clearing a Slot removes image_ref from the Slot only; it does not change the ImageRecord.
- Replacing a Slot changes image_ref only; it does not copy or move files.

1.10 Duplicate image use
- The same ImageRecord may be used in more than one Arrangement without warning.
- The same ImageRecord may be used in more than one Slot within one Arrangement only with a visible duplicate indicator.
- The duplicate indicator must show which Slots reference the same ImageRecord.
- The user may acknowledge duplicate use when it is intentional.
- Export metadata must preserve duplicate Slot references as separate Slot placements pointing to the same ImageRecord UUID.

1.11 Arrangement status rules
- active means the Arrangement appears in normal Library and Arrange views.
- archived means the Arrangement is hidden from normal views unless the archive filter is enabled.
- deleted means the Arrangement is soft-deleted and hidden from all normal views.
- Archiving an Arrangement must not alter any ImageRecord status.
- Deleting an Arrangement must not alter any ImageRecord status.
- Restoring an Arrangement must restore the layout and all Slot references.

1.12 Database migration rule
- v4.0 may keep the existing PatientImage table as the physical backing table for ImageRecord.
- v4.0 may keep TemplateInstance as the physical backing table for Arrangement.
- v4.0 must add stable UUIDs or a compatibility layer that guarantees stable UUID references.
- v4.0 must expose ImageRecord and Arrangement through model adapters even if the physical schema remains partly legacy.
- v4.1 should normalize Arrangement Slots into a dedicated table if v4.0 keeps slot_states_json.

1.13 Physical schema recommendation
- patient_images should add uuid TEXT UNIQUE NOT NULL and keep current original file, thumbnail, metadata, status, and edit-state columns.
- arrangements should store uuid, patient_id, name, arrangement_type, template_id, layout_json, status, thumbnail_path, export_preset_json, created_at, and updated_at.
- arrangement_slots should store arrangement_uuid, slot_id, placement_id, image_uuid, expected_image_type, geometry_json, placement_json, created_at, and updated_at.
- If v4.0 keeps slot_states_json, the adapter must expose the same logical fields and pass the same tests.

1.14 Compatibility requirement
- Existing TemplateInstance records must be readable after migration.
- Existing slot_states_json must be converted or adapted to Slot objects.
- Existing PatientImage IDs must map to ImageRecord UUIDs.
- Existing thumbnails must remain valid.
- Existing exports must not be retroactively rewritten.
- Existing user-visible behavior should change only where it resolves the image-versus-mount ambiguity.

## 2. Library Navigation Rules

2.1 Library source of truth
- The Library is primarily an ImageRecord browser; Arrangements may appear as a separate section but must not replace individual image records.
- A patient with 18 images arranged into one FMX still has 18 Library images and one Arrangement.
- Images that appear in Arrangements remain visible in the Library.

2.2 Default grouping and loose images
- Default grouping is by patient, then visit date or import session, then ImageRecords.
- If visit date is missing, group by imported_at date; if patient is missing, group under Unassigned Images.
- A loose image is an active ImageRecord with zero active Slot references.
- Loose images are valid, should be easy to find, and may be filtered with "Loose only."
- Loose counts ignore archived and deleted Arrangements unless archive filters are active.

2.3 Arrangement indicators
- Each ImageRecord card or row must show whether it is used in Arrangements.
- The indicator should show a count, such as "Used in 2 arrangements."
- Opening the indicator lists Arrangement names and Slot labels.
- Selecting an Arrangement opens Arrange to that Arrangement and highlights the Slot.
- Archived Arrangement references require archive visibility before opening.

2.4 Library search scope
- Default Library search searches ImageRecords.
- Results may include Arrangements as a second result type with clear labels.
- Tooth-number search should find matching ImageRecords and Arrangements containing matching Slots.
- Arrangement-name search must not hide individual ImageRecord results.

2.5 Library actions
- ImageRecord actions: open in Develop, place in Arrangement, create Arrangement from selection, show using Arrangements, archive, restore, replace missing file, and export selected image.
- Arrangement actions: open in Arrange, rename, duplicate, archive, restore, export, show all source images, and rebuild thumbnail.
- Double-clicking an ImageRecord opens Develop by default.
- Double-clicking an Arrangement opens Arrange by default.
- Dragging ImageRecords into Arrange places references.
- Dragging an Arrangement into Arrange opens that saved Arrangement.

2.6 Archive and empty states
- Normal Library view hides archived images and archived Arrangements.
- Archive filter shows archived records with subdued styling.
- Archived image references inside active Arrangements still appear as archived-linked Slots.
- Deleted records stay hidden unless an administrative recovery view is active.
- Empty states must distinguish no images, no arrangements, no loose images, and no search matches, with a safe next action when available.

## 3. Arrange Interaction Rules

3.1 Arrange source of truth
- Arrange edits Arrangement records, not original image ownership.
- Arrange Slots store ImageRecord UUID references.
- Arrange must never duplicate an original image file simply because an image is placed into a Slot.
- Arrange must never remove an ImageRecord from Library because it was placed into a Slot.

3.2 Opening an Arrangement
- Open by Arrangement UUID when possible.
- Load metadata and Slots, resolve every image_ref to an ImageRecord, and mark unresolved refs as broken-linked.
- Show archived refs as archived-linked.
- Render active refs with current ImageRecord edit state plus Slot placement state.

3.3 Creating and placing
- A new Arrangement starts from a blank template, selected image batch, or import session.
- Empty Slots must be visible and labeled.
- The user may save a partially filled Arrangement.
- Required Slots must be visually marked, but missing required Slots do not block saving unless the workflow explicitly says "finalize."
- Dragging an ImageRecord into a Slot sets Slot.image_ref to ImageRecord.uuid.
- Dropping onto an occupied Slot asks whether to replace, swap, or cancel.
- Dropping onto an incompatible Slot warns but allows override if permitted.
- Dropping the same image into another Slot in the same Arrangement warns about duplicate use.

3.4 Moving and clearing
- Dragging from one occupied Slot to an empty Slot moves the Slot reference by default.
- Duplicate Placement copies the reference into the target Slot and creates two Slot placements with the same ImageRecord UUID.
- Two independent visual crops of the same source image use two Slot placements, not two ImageRecords.
- Clear Slot sets Slot.image_ref to null, keeps Slot geometry, and does not archive, delete, or modify the ImageRecord.
- Remove from Arrangement must be worded as clearing placement, not deleting image.
- Delete Image must be a separate Library or Develop action with confirmation.

3.5 Broken and archived Slots
- Broken Slots remain visible and display Slot label, missing image UUID, and recovery actions.
- Archived-linked Slots display an archived badge and can be restored if the user has permission.
- Export can block, warn, or include placeholders according to export mode.
- Replacing a missing image must update the ImageRecord file link or Slot image_ref according to user choice.

3.6 Develop edits and placement state
- By default, Arrangements render the current ImageRecord edit state.
- If a user changes an ImageRecord in Develop, all Arrangements using that image show the updated image.
- Arrangement thumbnails must be marked stale after referenced ImageRecord edits; v4.0 may regenerate lazily.
- v4.1 should support pinned snapshots for legally frozen presentations or patient communications.
- Fit mode, pan, zoom, local crop, and local rotation are Slot-level data.
- Slot-level data must not affect Develop or Library image thumbnails.
- Slot-level data must export as placement metadata.

3.7 Save, undo, and wording
- Save writes Arrangement metadata and Slots, not duplicate ImageRecords.
- Save must not update ImageRecord edit_state_json except through explicit Develop or annotation actions.
- Save must validate that every non-null image_ref is a UUID or a legacy ID that can be mapped to a UUID.
- Slot changes are Arrangement history; Develop changes are ImageRecord history.
- Undo within Arrange reverses Slot placement changes.
- Use "Place image," "Clear slot," "Archive arrangement," "Archive image," and "Source image" instead of ambiguous mount or delete wording.

3.8 Template behavior
- A template defines available Slots and geometry defaults; it does not own images.
- Changing a template must not alter existing Arrangements unless the user explicitly migrates them.
- An Arrangement may remember the template version it was created from.
- Freeform layouts are Arrangements with flexible Slot geometry.

## 4. Import Rules

4.1 Import always creates ImageRecords
- Every import creates one ImageRecord per source image.
- Import does not create an Arrangement unless the user selects an arrangement workflow or import preset.
- Import must not require the user to choose a mount before images can exist in the Library.
- Import must assign UUIDs immediately.
- Import must preserve original filenames as metadata while storing collision-safe filenames.

4.2 Patient assignment and import sessions
- If a patient is selected, imported images attach to that patient; otherwise they go to Unassigned Images.
- Moving an unassigned image to a patient changes patient assignment but not UUID.
- Cross-patient reassignment must warn if the image is already used in Arrangements and list affected Arrangements before confirmation.
- A batch import should create an import session record or equivalent metadata for review.
- The import session may suggest Arrangements, but it is not itself an Arrangement and deleting the grouping must not delete ImageRecords.

4.3 Auto-arrange from import
- Auto-arrange may create a draft Arrangement using imported ImageRecord UUIDs.
- Auto-arrange must be reviewable before final save and must never hide the individual ImageRecords.
- Auto-arrange confidence should be stored as suggestion metadata, not clinical truth.
- Low-confidence Slot matches must be visibly marked.

4.4 FMX import behavior
- Importing 18 radiographs creates 18 ImageRecords.
- The user may choose "Create FMX from selection" after import.
- The FMX Arrangement uses Slots that reference those UUIDs.
- If only 12 images are available for an 18-slot FMX, the Arrangement can be saved with 12 occupied Slots and 6 empty Slots.
- Missing Slots remain empty, not fake images.

4.5 Duplicate source images
- If a file content hash already exists for the same patient, import should warn.
- The user may still import a duplicate as a separate ImageRecord when clinically appropriate.
- Duplicate ImageRecords receive different UUIDs.
- Duplicate source detection must not collapse two ImageRecords automatically.
- A duplicate file warning is different from duplicate Slot use.

4.6 Import metadata, errors, and archive matches
- Import should capture original filename, file size, dimensions, content hash, captured date if available, import source, and user.
- DICOM or dental imaging metadata should be preserved if available.
- Metadata extraction failure must not block import unless the file itself cannot be read.
- Unsupported files should be skipped with an evidence report.
- Partially successful batch imports should keep successfully imported ImageRecords.
- Failed files should not create active ImageRecords.
- Importing a file that matches an archived ImageRecord should offer restore, import duplicate, or cancel.
- Restore keeps the existing UUID; import duplicate creates a new UUID; cancel leaves the archive unchanged.

## 5. Export Rules

5.1 Export object types
- Export ImageRecord renders one image.
- Export Arrangement renders a layout composed from Slot references.
- Export patient package may include multiple ImageRecords and Arrangements.
- Export metadata must identify which object type was exported.
- Export must not treat a rendered Arrangement as the source ImageRecord unless explicitly saved as a new derived image.

5.2 Arrangement export and incomplete layouts
- Arrangement export renders the current layout.
- Each occupied Slot resolves image_ref to an ImageRecord.
- Slot placement state is applied after ImageRecord edit state.
- Strict mode blocks export if required Slots are empty, archived, deleted, or missing.
- Clinical review mode warns but allows export with visible placeholders.
- Presentation mode may hide empty optional Slots but must not hide broken required Slots without warning.
- Evidence mode includes a metadata JSON sidecar with Slot status for every Slot.
- The chosen export mode must be visible in the export dialog.

5.3 Export metadata sidecar
- Arrangement exports should include metadata that lists Arrangement UUID, patient ID, export timestamp, template ID, Slot IDs, ImageRecord UUIDs, and Slot statuses.
- Image exports should include ImageRecord UUID, original filename, edit state hash, and export timestamp.
- Metadata sidecar should be optional for casual image export but required for evidence, QA, and automated tests.
- Metadata must distinguish ImageRecord UUID from Arrangement UUID.
- Metadata must preserve duplicate Slot placements that point to the same ImageRecord UUID.

5.4 Saving rendered outputs
- A rendered Arrangement output is not automatically a new ImageRecord.
- If the user chooses "Save render to Library," the render becomes a derived ImageRecord.
- A derived ImageRecord must store provenance pointing to the source Arrangement UUID and source ImageRecord UUIDs.
- Derived renders must be labeled clearly so they are not confused with original imports.
- Re-exporting a derived render must preserve provenance.

5.5 Export and Develop edits
- Export uses current ImageRecord edit state by default.
- If an Arrangement references a pinned snapshot in v4.1, export uses that snapshot.
- v4.0 exports should record edit_state_json hash at export time.
- A stale Arrangement thumbnail must not be used as final export output.
- Export must render from current source data, not from cached thumbnails.

5.6 Export and archive
- Exporting an Arrangement with archived-linked Slots requires a warning.
- Exporting an Arrangement with deleted or missing Slots requires strict handling based on export mode.
- Exporting archived ImageRecords directly requires archive visibility and confirmation.
- Export must never silently omit a broken required Slot.
- Export reports must list any omitted or placeholder Slots.

5.7 Print behavior
- Print is an export target and follows the same Slot resolution rules as file export.
- Print preview must show empty, archived, and broken Slot states before printing.
- Printing a Library image prints an ImageRecord render.
- Printing an Arrangement prints an Arrangement render.

## 6. Edge Cases Decision Table

| Case | Decision | UI state | Data state | Export behavior | Scope |
| --- | --- | --- | --- | --- | --- |
| Image appears in two Arrangements | Allowed | Image card shows used count | Two Slots reference same ImageRecord UUID | Metadata lists both Arrangement UUIDs | v4.0 |
| Image appears twice in one Arrangement | Allowed with warning | Duplicate badge on both Slots | Two Slots reference same ImageRecord UUID | Metadata lists two Slot placements with same image UUID | v4.0 |
| User clears a Slot | Clear placement only | Slot becomes empty | Slot.image_ref becomes null | Empty Slot follows export mode | v4.0 |
| User deletes an Arrangement | Soft-delete Arrangement only | Arrangement hidden | ImageRecords unchanged | Deleted Arrangement not exportable until restored | v4.0 |
| User archives an Arrangement | Hide Arrangement from normal view | Archive badge when archive filter active | ImageRecords unchanged | Export requires archive visibility | v4.0 |
| User archives an image used in active Arrangement | Preserve Arrangement with archived-linked Slot | Slot shows archived image badge | ImageRecord.status archived, Slot.image_ref preserved | Warn or placeholder by export mode | v4.0 |
| User deletes an image used in active Arrangement | Preserve Arrangement with broken Slot | Slot shows deleted or missing warning | ImageRecord soft-deleted, Slot.image_ref preserved | Strict blocks; review mode uses placeholder | v4.0 |
| Image file missing on disk | Mark ImageRecord missing | Slot and Library show missing state | UUID preserved, status missing | Strict blocks; review mode placeholder | v4.0 |
| Restored archived image | Reconnect automatically | Slots become normal occupied | Same UUID status active | Export normal | v4.0 |
| Reimport same file as archived image | Offer restore or duplicate | Decision dialog | Restore keeps UUID; duplicate new UUID | Based on chosen record | v4.0 |
| Import 18 FMX images | Create 18 ImageRecords | Optional draft FMX suggestion | Arrangement Slots reference UUIDs | Full FMX export if all required filled | v4.0 |
| Import 12 images into 18-slot FMX | Save partial Arrangement | Six Slots visible as empty | Empty Slots remain null | Strict blocks if required; review mode placeholders | v4.0 |
| Auto-arrange wrong Slot | User can drag to correct Slot | Low-confidence badge or manual correction | Only Slot.image_ref changes | Corrected layout exports normally | v4.0 |
| Develop invert applied after Arrangement save | Arrangement updates live | Thumbnail marked stale | ImageRecord edit_state_json changed | Export uses current edit state | v4.0 |
| Need legally frozen Arrangement view | Use pinned snapshot | Snapshot badge | Slot points to ImageRecord UUID plus snapshot ref | Export uses snapshot | v4.1 |
| Template geometry changes after Arrangement save | Existing Arrangement stays stable | Migration prompt only if user requests | Arrangement keeps stored layout_json | Existing export unchanged | v4.0 |
| Patient reassignment for image used in Arrangement | v4.0 blocks unless safe; v4.1 adds guided workflow | Confirmation dialog | ImageRecord patient_id changes only after confirm | Arrangement patient conflict handled before export | v4.0 guard, v4.1 workflow |
| Arrangement contains image from another patient | Block by default | Cross-patient warning | Slot not saved unless override permitted | Export must show cross-patient warning | v4.0 guard, v4.1 workflow |
| Derived rendered Arrangement saved to Library | Create derived ImageRecord | Derived badge | New ImageRecord with provenance | Exports as derived image with provenance | v4.1 |
| User searches Arrangement name | Show Arrangement result and image results | Separate result types | No data change | No export change | v4.0 |
| Loose image never arranged | Valid state | Loose image filter includes it | ImageRecord has zero active Slot refs | Image export normal | v4.0 |
| Archived Arrangement referenced by image used count | Excluded by default | Count changes when archive filter active | Slot refs still exist | Export only through archived Arrangement view | v4.0 |
| Slot references legacy integer ID after migration | Resolve through mapping | No user-visible error if mapping works | Adapter returns UUID | Export metadata uses UUID | v4.0 |
| Slot references unknown legacy ID | Broken Slot | Broken reference warning | image_ref unresolved | Strict blocks | v4.0 |
| Thumbnail generation fails | Keep source usable | Thumbnail placeholder | ImageRecord active with thumbnail error metadata | Export renders from source, not thumbnail | v4.0 |

## 7. v4.0 and v4.1 Scope

7.1 v4.0 in scope
- Establish images-first architecture as the app rule.
- Add or expose stable ImageRecord UUIDs.
- Add or expose stable Arrangement UUIDs.
- Keep individual images visible in Library even when used in Arrangements.
- Support loose images.
- Support Arrangements as named Slot collections.
- Store Slot references to ImageRecord UUIDs.
- Preserve Arrangements when referenced images are archived, deleted, or missing.
- Support partial Arrangements.
- Support duplicate image use warnings.
- Update Arrange save/load to avoid file copies and path identity.
- Update export metadata to distinguish ImageRecord UUIDs from Arrangement UUIDs.
- Add tests for archive, duplicate reference, partial FMX, and export metadata.

7.2 v4.0 allowed compromises
- Physical storage may keep PatientImage and TemplateInstance tables.
- Slot storage may remain JSON if adapter tests guarantee stable behavior.
- Arrangement thumbnails may regenerate lazily.
- Auto-arrange may be heuristic and conservative.
- Snapshot pinning may be deferred.
- Cross-patient advanced workflows may be deferred if the app blocks unsafe cases.

7.3 v4.0 out of scope
- Full DICOM conformance.
- Cloud sync.
- Multi-clinic conflict resolution.
- Cryptographic legal record signing.
- Advanced AI image classification.
- Fully normalized search index.
- Full visual template designer rewrite.
- Automatic patient merge workflows.

7.4 v4.1 recommended scope
- Normalize Arrangement Slots into a dedicated table if not done in v4.0.
- Add pinned ImageRecord snapshots for frozen Arrangement views.
- Add richer import sessions and visit records.
- Add advanced cross-patient reassignment controls.
- Add provenance view for derived renders.
- Add better arrangement-aware search.
- Add template version migration tools.
- Add evidence-grade export package validation.

7.5 Compatibility target
- v4.0 should be a model clarity release, not a full database rewrite.
- Existing user data must remain readable.
- Existing visual workflows should feel familiar.
- Ambiguous words and destructive actions should be corrected even if schema normalization waits until v4.1.

## 8. Implementation Notes for Claude Code

8.1 Architectural direction
- Build or expose model adapters named ImageRecord, Arrangement, and Slot before broad UI rewrites.
- Route Library, Arrange, Develop, and Export through those adapters.
- Keep existing physical tables where practical for v4.0.
- Do not let UI components pass raw file paths as image identity.
- Do not let template code treat placed images as owned by the template.

8.2 Existing code likely affected
- database.py: add UUID migration, adapter methods, reference lookups, and archive-aware queries.
- library_view.py: show ImageRecords first, arrangement indicators, loose filters, archive filters, and search result types.
- filmstrip.py: use ImageRecord UUID references when dragging to Arrange.
- freeform_view.py: store Slot placement references instead of copied image objects.
- template_data.py: separate reusable template definitions from patient-specific Arrangement instances.
- dialogs.py: update labels and confirmation flows for clear Slot, archive image, archive Arrangement, duplicate use, and missing refs.
- canvas.py: render Slots from resolved ImageRecords and Slot placement state.
- comparison_view.py, adjustments.py, history.py, results_writer.py, constants.py, and panda_gallery.py: align comparison boards, Develop edits, event labels, export metadata, shared constants, and app wiring with the new model layer.

8.3 New modules recommended
- image_record_model.py, arrangement_model.py, arrangement_store.py, placement_rules.py, export_manifest.py, and import_session_model.py are recommended if the current modules cannot hold these responsibilities cleanly.

8.4 Migration sequence
- Add UUID columns or UUID mapping table.
- Backfill ImageRecord UUIDs for existing PatientImage rows.
- Backfill Arrangement UUIDs for existing TemplateInstance rows.
- Build adapter read methods that return ImageRecord and Arrangement objects.
- Build adapter write methods for new saves.
- Convert or adapt existing slot_states_json to Slot objects.
- Update drag/drop to write image UUID references.
- Update Library indicators and loose-image queries.
- Update export sidecar metadata.
- Add tests before enabling schema-destructive cleanup.

8.5 Required tests
- Import creates ImageRecords without an Arrangement.
- Create FMX from selected images creates one Arrangement and preserves individual ImageRecords.
- Same ImageRecord can appear in two Arrangements.
- Same ImageRecord twice in one Arrangement shows duplicate warning and exports two Slot placements.
- Clear Slot does not delete or archive the ImageRecord.
- Archive Arrangement leaves ImageRecords active.
- Archive ImageRecord leaves active Arrangement with archived-linked Slot.
- Missing image file leaves broken Slot and export warning.
- Develop edit updates Arrangement render or stale thumbnail state.
- Arrangement export sidecar includes Arrangement UUID, Slot IDs, and ImageRecord UUIDs.
- Legacy TemplateInstance loads through Arrangement adapter.
- Legacy PatientImage loads through ImageRecord adapter.

8.6 UI and UX acceptance rules
- Users should understand that Library contains images and Arrange contains layouts.
- Buttons must use active, disabled, warning, and complete states consistently.
- Destructive actions must be disabled when not actionable.
- When actions become actionable, their visual state must change clearly.
- Workflows should progress left to right where the screen has staged work.
- Completed stages should receive check marks or equivalent completion color changes.
- Ambiguous clinical actions must use explicit labels.
- The app must not hide the source image after placement.

8.7 BA audit implications
- BA should include static checks for ambiguous delete wording around Slots.
- BA should include UI-state checks for disabled actions that still execute.
- BA should include data-flow checks for path identity passed where UUID identity is required.
- BA should include tests for archive-image breaking Arrangement visibility.
- BA should include export metadata checks for missing UUIDs.
- BA should include screenshot or DOM evidence that duplicate image use is visibly marked.

8.8 Rollout risk
- Highest risk is silent migration of legacy slot_states_json.
- Second risk is UI code still assuming a Slot owns an image file.
- Third risk is export using cached thumbnails instead of fresh renders.
- Fourth risk is accidental deletion of images when deleting Arrangements.
- Fifth risk is confusing users by showing Arrangements but hiding individual images.

8.9 Recommended first implementation slice
- Add UUID compatibility and adapters.
- Update one Arrangement path to use Slot.image_ref UUIDs.
- Add Library used-in-arrangement indicators.
- Add clear Slot and archive image tests.
- Add export sidecar metadata for that path.
- Only then broaden to freeform, comparison, and full template flows.

8.10 Done definition
- A user can import images and see them as individual Library records.
- A user can build an Arrangement from those images without duplicating source files.
- A user can place the same image in multiple Arrangements.
- A user can archive an image and see affected Slots remain visible as archived-linked.
- A user can export an Arrangement with metadata proving which ImageRecord UUIDs were used.
- Legacy data still opens.
- Tests cover the edge cases in Section 6.
