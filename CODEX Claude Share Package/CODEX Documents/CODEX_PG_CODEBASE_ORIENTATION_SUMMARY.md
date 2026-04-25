# CODEX PG Codebase Orientation Summary

Generated: 2026-04-24 19:21:32 -07:00
Rewritten cleanly after literal Markdown verification.

This is Codex's durable self-summary after reading the live `C:\panda-gallery` project and the Codex-owned specification review artifacts. It is written for future Codex chats: read this before changing architecture, writing new code, or deciding what is already implemented.

## Boundaries I Must Remember

- `C:\panda-gallery` is the live Panda Gallery / Claude workspace and should be treated as read-only reference unless Darrin explicitly overrides that boundary.
- Codex-owned work belongs in `C:\CODEX PG`; every Codex-created folder must start with `CODEX`.
- The copied Claude data at `C:\CODEX PG\CODEX CLAUDE PG DATA` is a local snapshot only and is ignored by Git. The live source of truth is still `C:\panda-gallery`.
- GitHub backup for Codex work uses `C:\CODEX PG` with remote `https://github.com/DarrinRap/CODEX-PG.git`.
- Do not push copied Claude/Panda Gallery source data to GitHub.

## Current Live PG State Read

- Source folder inspected: `C:\panda-gallery`.
- Reported version: `VERSION.txt` = `4.23`.
- Live repo branch status seen during orientation: `main...origin/main`, clean at the time of inspection.
- Latest visible live commits included:
  - `22b361e v4.23 - #130 Phase 3: session integration (append/remove_manual_screenshot)`
  - `b44b04b docs: close #124 (v3.99) and #125 (v4.00) in BUGS.md`
  - `8ac6a6e docs: handoff #58`
  - `10227ee session bundle (pre-handoff)`
  - `ec66d37 v4.22 - file #131: active-window focus indicator (color cue)`
- `debug_log.txt` was 0 bytes at read time.
- The live app's current test fixture is `workflows/instructions_latest.json`, titled `#130 Phase 3 test`.
- `workflows/results_latest.json` contained a partial `#130 Phase 3 test` run with manual region screenshot evidence attached to step 1 and PASS on step 2.

## Runtime Architecture Map

Panda Gallery is a PySide6 desktop app with a flat module layout. Main ownership lives in `panda_gallery.py`, and specialized views/widgets are split into large supporting modules.

Important runtime modules:

- `panda_gallery.py`: `MainWindow`; owns top-level app state, central stacked views, patient scope, menus, toolbar, workflow-capture action registration, instruction pane lifecycle, template/freeform/comparison navigation, save/export/print, shutdown handling.
- `canvas.py`: `CanvasView`; QGraphicsView/Scene editor for image rendering, zoom/pan, tool modes, annotations, crop, undo stack, Escape behavior.
- `adjustments.py`: `EditState` and Pillow image-processing pipeline.
- `annotations.py`: QGraphicsItem subclasses for brush/text/rectangle/ellipse/arrow/crop/handles.
- `panels.py`: right-side editing and drawing panels, tool strip, colors, sliders, histogram, layer affordances.
- `library_view.py`: patient image grid/library UX.
- `patient_panel.py`: patient selection/list management.
- `template_view.py`, `template_designer.py`, `template_data.py`, `filmstrip.py`: grid template layouts, template instances, designer, and image filmstrip.
- `freeform_view.py`: freeform arrangement canvas.
- `comparison_view.py`: side-by-side comparison view.
- `dialogs.py`: themed dialogs; local rule says avoid raw native Qt dialogs where PG has themed alternatives.
- `database.py`: SQLite/SQLAlchemy database manager and ORM models.
- `workflow_capture.py`: F12 full-screen screenshot/audio workflow session capture, metadata, audio meter, autotranscribe launch.
- `instruction_pane.py`: floating guided testing pane and Testing Settings dialog.
- `region_capture.py`: Shift+F12 drag-region capture overlay, flash, toast, review dialog, and session-aware screenshot attachment.
- `results_writer.py`: `workflows/results_latest.json` writer and archive-on-load helper.
- `scripts/transcribe_latest.py`: local faster-whisper transcription of latest workflow session.

Large-file reality:

- `panda_gallery.py`, `instruction_pane.py`, `panels.py`, `canvas.py`, and `library_view.py` are large and carry significant historical behavior. New work should be conservative and local unless a planned extraction is part of the task.
- `STYLE.md` has a soft target of 600-800 lines per module but accepts existing large modules with opportunistic cleanup.

## Data and Persistence

Database:

- `database.py` uses SQLite via SQLAlchemy.
- Main models: `Patient`, `PatientImage`, `TemplateInstance`, `Template`, `AdminConfig`, `AuditLog`.
- Image rows store original file paths, thumbnail paths, category/status, content hash, annotation JSON, edit-state JSON, and display labels.
- `DatabaseManager` is the DB boundary. UI should call named DB methods, not open ad-hoc SQLAlchemy sessions inside widgets.
- Existing DB path is app-local: `C:\panda-gallery\panda_gallery.db`.

Image editing:

- `CanvasView.edit_state` is the in-memory authority for image adjustment state.
- Edit state is serialized through `_auto_save_annotations` into `PatientImage.edit_state_json`.
- Annotations are vector QGraphicsItems and are serialized separately as JSON.
- Exports/thumbnails composite rendered pixmaps with annotations as needed.

Testing/results:

- Guided test instructions are loaded from `workflows/instructions_latest.json`.
- Test results are written to `workflows/results_latest.json` by `ResultsFile`.
- Previous results and run-keyed artifacts are archived into `workflows/results_archive/` on pane show before a new run overwrites `results_latest.json`.
- Screenshots for test evidence live under `workflows/screenshots/<run_id>/`.

Workflow sessions:

- Full workflow capture sessions live under `workflows/session_YYYYMMDD_HHMMSS/`.
- A session writes `metadata.json`, numbered PNG frames, optional `audio.wav`, optional `transcript.md`, and updates `workflows/LATEST.txt`.
- `metadata.json` schema version currently expected by transcription is 6.

## Guided Testing Pane Reality

The local guided-testing system is already substantial.

Implemented in `instruction_pane.py`:

- Floating always-on-top pane opened by `Ctrl+Alt+I`.
- Reads JSON instructions, supports schema versions 1 and 2.
- Supports three step modes:
  - single expected observation: PASS/FAIL flow
  - checklist steps: per-item PASS/FAIL/SKIP with derived step outcome
  - `kind: "action"`: acknowledgment-only setup/navigation steps
- Writes `results_latest.json` through `ResultsFile`.
- PASS writes a single result.
- FAIL opens an inline note panel, captures an automatic step screenshot of PG, then writes result.
- Checklist completion writes `kind: "checklist"`, `checklist_results`, derived outcome, optional fail screenshot.
- Action steps write `kind: "action"` and outcome `ACK` in code, though `BUGS.md` has one historical note saying `ACKED`; trust current code when implementing.
- The pane can be hidden from screen capture via Windows Display Affinity unless the user opts into showing it in captures.
- Testing Settings includes capture visibility, include-cursor preference, microphone device UI, and mic test flow.
- The stats row reflects workflow recording state and audio/mic state.

Important implementation hooks:

- `InstructionPane.active_step_n` exposes the current step number for outside consumers such as region capture.
- `InstructionPane.append_manual_screenshot(rel_path)` appends region captures to the active step and emits `step_state_changed`.
- `InstructionPane.remove_manual_screenshot(step_n, rel_path)` removes a previously attached manual capture and emits `step_state_changed`.
- `step_state_changed` currently has no in-process consumer; it exists for the external/Claude auto-read model and file-mtime watchers.

UX debt still visible:

- The current pane has already absorbed some v3.71 UI redesign work: root padding, stable bottom action bar, capped body/context areas, unified checklist summary strip, capped fail textarea.
- `BUGS.md` still keeps several pane/UI issues open or partly superseded, so code and bug text need careful reconciliation before fixing.

## Workflow Capture and Transcription Reality

`workflow_capture.py` already does the upstream capture/transcription foundation that the Testing + Audit MVP assumes exists.

Implemented:

- `Ctrl+Alt+R`: start workflow recording, prompts for audio vs screenshots-only.
- `F12`: captures full virtual desktop screenshot to numbered PNG file when recording.
- `Ctrl+Alt+S`: stops and saves metadata, audio if available, and latest-session pointer.
- `Ctrl+Alt+A`: aborts active session and deletes its folder.
- `Ctrl+Alt+Backspace`: deletes latest saved session.
- Audio recording uses `sounddevice` at 16kHz mono, with mic fallback handling, silent/disconnected states, and a meter signal.
- Capture metadata records frame timestamps, mouse positions, audio sample offsets, monitor geometry, app version, audio info, and frame list.
- After successful audio save, `scripts/transcribe_latest.py` is spawned as a subprocess and writes `transcript.md`.

Transcription:

- Uses `faster-whisper` model `large-v3-turbo`, CPU int8.
- Requires metadata schema version 6.
- Aligns transcript segments to F12 frames using `audio_sample_offset` and writes frame-aware transcript output.

MVP implication:

- Audio/transcription are a real upstream input, not something Codex should rebuild for Testing + Audit v1 unless evidence alignment breaks.

## Region Capture Reality (#130)

`region_capture.py` is now implemented through Phase 3 in live v4.23.

Implemented behavior:

- `Shift+F12` opens a Win+Shift+S-style overlay on the cursor's display.
- Overlay dims the screen, shows a clear drag cutout, peach outline, and live dimensions label.
- Esc/right-click/undersized drag cancels.
- Release captures the selected region to PNG.
- Success shows a green flash and peach-accent toast.
- Clicking the toast opens a review dialog with Save, Discard, and Re-capture.
- Discard deletes the PNG and, if the capture was attached to a session step, removes it from `results_latest.json`.
- Re-capture schedules a new overlay after the modal closes.
- Active-session captures save under `workflows/screenshots/<run_id>/region_<step_n>_<seq>.png` and append to the current step's `manual_screenshots[]`.
- Manual fallback captures save under `workflows/screenshots/manual/<timestamp>.png` and do not affect JSON.

Important implementation details:

- `RegionCaptureManager` is eager-constructed in `MainWindow._register_workflow_capture_actions` so overlay active state can disable the menu action.
- Shortcut context is `ApplicationShortcut`, so Shift+F12 works even when the floating instruction pane has focus.
- The manager holds Python references to flash/toast widgets to avoid Qt wrapper garbage collection problems.
- Toast intentionally does not use `WA_DeleteOnClose`; a previous crash came from the C++ object being deleted before the Python slot cleared.
- Cursor compositing for region capture is still TODO even though the include-cursor QSettings key is read.
- The discard path only knows the most recent session capture tuple. It deliberately avoids removing older JSON paths if the review dialog is for a capture that no longer matches the last stored tuple.

Verification status from handoff/bugs:

- #130 Phase 3 shipped in v4.23.
- Manual test T6 passed.
- T7/T8 were not rerun and need re-authoring around re-trigger guard/toast race.

## Results Writer Reality

`results_writer.py` is small and important. It is the current local evidence ledger.

Implemented:

- Creates a fresh run with schema version 1, `run_id`, title, start time, instructions source, results list, and completed timestamp.
- `record_single`: PASS/FAIL/single expected outcome.
- `record_checklist`: checklist result with per-item rows and derived outcome.
- `record_action`: action-kind acknowledgment, outcome `ACK`.
- `append_manual_screenshot`: appends to per-step `manual_screenshots`, creating a placeholder entry with `outcome: null` if needed.
- `remove_manual_screenshot`: removes manual screenshot references and deletes empty placeholder entries.
- All writes are atomic-ish via temp file plus `os.replace`.
- Writer preserves `manual_screenshots[]` when later PASS/FAIL/checklist/action writes overwrite a step entry.

Testing + Audit implication:

- `results_latest.json` is a strong local foundation but is not yet an audit-grade backend contract. It uses paths, not durable evidence IDs; package/evidence schemas still need to be defined.

## Spec and Product Track Understanding

Codex has already reviewed the external `PG_Testing_Audit_MVP_v1_Spec.docx` and the main `C:\panda-gallery` specification corpus. The durable review lives at:

- `C:\CODEX PG\CODEX Specification Review\CODEX_SPECIFICATION_REVIEW_REPORT.md`

The most important conclusion remains:

- There are two product tracks that must stay separate.
- PG core v4.0 is a clinical imaging product track. `PG_V4_MVP_PLAN.md` defers visible AI, installer/distribution work, and HIPAA-basics from v4.0.
- PG Testing + Audit MVP v1 is a separate testing/audit pipeline. It needs session packaging, Dropbox transfer, AI issue extraction, approval workflow, shared email, and searchable archive.
- Both can be true only if future docs and code keep the boundary explicit.

Canonical-ish local references:

- `TESTING_SECTION_SPEC.md`: best source for guided pane behavior, instructions schema, results file, and authoring rules.
- `PANDA_GALLERY_REMOTE_TESTING_SPEC_draft4.md`: useful phased reference for pane/session/mic/Dropbox/testing dashboard concepts, but older and partially superseded.
- `PANDA_GALLERY_TRANSCRIPT_V2_SPEC.md`: important transcript/evidence alignment input.
- `PANDA_GALLERY_COMPLIANCE_SPEC.md`: useful but needs a Testing + Audit cloud/AI/email addendum.
- `PG_V4_MVP_PLAN.md`: current authority for PG core v4.0, not for Testing + Audit MVP scope.
- `STYLE.md`, `GUIDED_TESTING_STYLE.md`, `DEBUGGING_LESSONS.md`, `CLAUDE.md`: process, engineering, and UX discipline.

Recommended canonical docs still needed before major Testing + Audit implementation:

1. `CODEX_MASTER_SPEC_INDEX.md`
2. `CODEX_TESTING_AUDIT_ARCHITECTURE_v1.md`
3. `CODEX_SESSION_PACKAGE_SCHEMA_v1.md`
4. `CODEX_AUDIT_ISSUE_SCHEMA_v1.md`
5. `CODEX_AUDIT_DASHBOARD_UX_SPEC_v1.md`
6. `CODEX_COMPLIANCE_ADDENDUM_TESTING_AUDIT_v1.md`

## Design Language I Should Use

Existing PG visual vocabulary:

- Dark desktop shell: `#1a1a2e`, `#161625`, `#14141f`, `#22223a`, `#2a2a3e` appear repeatedly.
- Warm peach accent: `#e8a87c`; hover often `#d4945a`.
- PASS/positive greens: `#5ab87a`, `#7fb069`.
- FAIL/error reds: `#d46a6a`.
- Warning amber: `#f39c12`.
- Muted secondary text: `#888`, `#8a8a9a`, `#c8c5bb`.
- Low radius controls, generally 3-4px in existing Qt styling; avoid pill-heavy UI.
- Stable bottom action bars are a repeated design fix, especially for checklist flow.
- Visual-first rule: UI work should have mockups before code when a design decision is ambiguous.

Codex-created visual planning already exists:

- `C:\CODEX PG\CODEX Visual Mockups`
- `C:\CODEX PG\CODEX Interface Storyboards\CODEX_step_by_step_ui_storyboard_v1.html`
- `C:\CODEX PG\CODEX Interface Storyboards\CODEX_interface_storyboard_notes_v1.md`

## Current Open Bugs/Risks That Matter

Most relevant open issues from `BUGS.md` and `HANDOFF.md`:

- #131 Active-window focus indicator: open UX polish. Shift+F12 works with ApplicationShortcut, but users cannot easily tell whether MainWindow or InstructionPane has focus. Mockup required first.
- #129 Settings dialog and pane sizing: open medium. Needs dynamic content-based sizing and minimum floors tied to visible button/text invariants.
- #130 Region capture: Phase 3 shipped v4.23, but T7/T8 need re-authoring/re-run around re-trigger guard and toast race.
- #111 Instruction Pane feels cramped/not modern: still a historical UX anchor even though parts of the redesign are in code.
- #110 Checklist action buttons scrolling out of view: `BUGS.md` says open/high, but code now has a pane-level action bar. Verify before assuming still live.
- #97 Testing actions buried under View -> Testing: open feature request for dev-gated top-level Testing menu.
- #114 Launch empty state weak, #115 toolbar icon adoption, #116 back/forward patient navigation, #117 focus rectangle, #118 collapsible right-panel subsections, #119 library icon-only labels: lower/medium UX backlog.
- #79 shutdown RuntimeError tracebacks and print-swallow audit: still a pattern to guard against.
- Export-corruption scan for huge PNGs remains deferred.
- Validator auto-test and cursor-toggle re-verification remain deferred.

Risk pattern:

- `BUGS.md` sometimes lags code because fixes happen in phases. Before implementing a bug, inspect the current code and recent commits, not only the bug entry title.

## Engineering Rules I Should Follow

From PG docs and observed code:

- Prefer existing PySide6 patterns and object-name-scoped QSS.
- Add new DB access through `DatabaseManager`, not direct widget sessions.
- New signals use past-tense event names; slots use `_on_*` or private action names.
- Keep state ownership explicit; coordinate via MainWindow or a dedicated manager.
- Do not use raw native Qt dialogs where PG has themed dark dialog patterns.
- For hard Qt event bugs, after one failed hypothesis write a tiny test applet/probe and log numbers before shipping a theory.
- UI tests are mostly smoke/manual today; pure logic should get unit tests when added.
- Avoid broad refactors unless the current task actually needs them.
- For Panda Gallery proper, Claude's workflow says visual mockup first for UI changes and versioned commits via `git vcommit`; Codex should respect the spirit while keeping Codex files separate unless Darrin asks us to edit PG directly.

## What Is Missing For Me To Be Fully Implementation-Ready

I am now familiar with the structure and the testing/capture subsystem, but these are still missing before a confident full build of Testing + Audit MVP:

- A canonical master spec index that marks which specs are current versus historical.
- A concrete session package manifest schema.
- Durable evidence IDs and evidence object model.
- AI issue extraction schema, categories, priority/confidence rules, and dedupe behavior.
- Approval/email/archive data contracts.
- Compliance addendum for Dropbox, AI provider, email provider, retention, access control, and PHI/de-identification.
- A selected implementation target: extend PG itself, build a separate Codex desktop audit app, or create a local package/triage prototype first.
- Confirmation of whether Testing + Audit data may include real patient PHI during development.
- The actual target backend/storage decision beyond Dropbox handoff: local-only prototype, cloud DB, GitHub artifacts, or another service.

## Recommended Next Move

The best next move is not to start broad PySide6 implementation yet. The highest-leverage next step is a small canonicalization pass:

1. Create `CODEX_MASTER_SPEC_INDEX.md`.
2. Draft `CODEX_SESSION_PACKAGE_SCHEMA_v1.md` with evidence IDs and upload/package states.
3. Draft `CODEX_AUDIT_ISSUE_SCHEMA_v1.md`.
4. Update the Codex storyboard to include evidence IDs, manifest states, and approval/archive audit events.
5. Then implement the smallest local vertical slice: package an existing `workflows/results_latest.json` plus screenshots plus transcript into a deterministic local package without Dropbox.

That slice would prove the contract before spending effort on Dropbox, AI extraction, or dashboard UI.
