# CODEX Audit Module Interaction Spec v1

Generated: 2026-04-24
Owner: Codex design/spec draft for Panda Gallery Testing + Audit MVP
Status: implementation-ready draft for Claude Code planning, not live app code
Live source boundary: do not edit C:\panda-gallery from this spec package

## Purpose

The Audit Module turns a Panda Gallery testing session into a structured, reproducible evidence package. It is not only a dashboard. It is the workflow that captures what happened, what was expected, where it failed, what evidence proves it, and what Claude Code should fix.

Primary user: Darrin or a PG tester running guided test instructions.
Secondary user: Claude/Claude Code consuming validated packages and issue records.

## Visual And Vocabulary Alignment

The Audit Module must match Claude's established PG testing mockup language, especially:

- Dark shell: #0d0d18, #14141f, #1a1a2e, #22223a
- Borders: #2a2a3e, #232336
- Text: #e0ddd5, #c8c5bb, #888, #6a6a78
- Accent: #e8a87c, #d4945a
- PASS: #5ab87a or #7fb069
- FAIL: #d46a6a for dots/counts; peach #e8a87c for fail action emphasis where existing mockups do so
- SKIP: #8a8a9a
- Warning/silent: #f39c12 when needed
- Font: Segoe UI, SF Pro, Noto Sans fallback
- Body text: 13px; compact uppercase labels for state/meta text
- Radius: 4 to 6px, not large rounded cards

Reference mockups:

- C:\panda-gallery\workflows\design\region_capture_v1.html
- C:\panda-gallery\workflows\design\review_dialog_sizing_v1.html
- C:\panda-gallery\workflows\design\checklist_mockup_v2.html
- C:\panda-gallery\workflows\design\action_bar_mockup_v1.html
- C:\panda-gallery\workflows\design\v3_71_ui_vocabulary.html
- C:\CODEX PG\CODEX Audit UX Fullscreen Walkthrough PG Aligned\CODEX_audit_ux_fullscreen_walkthrough_PG_aligned_v2.html

## Non-Goals For MVP

- No Dropbox upload in the first local implementation.
- No AI provider call in the first local implementation.
- No email sending in the first local implementation.
- No real PHI processing until a compliance addendum explicitly permits it.
- No broad rewrite of Panda Gallery testing UI.
- No destructive evidence deletion during ordinary testing. Use `discarded: true` rather than deleting captured files.

## Canonical Data Objects

The interaction spec writes to the existing v1 contracts:

- `session_package_manifest.json`, schema `pg.session_package.v1`
- `derived/ai_extraction_input_v1.json`, schema `pg.ai_extraction_input.v1`
- `audit_issue_extraction_v1.json`, schema `pg.audit_issue_extraction.v1`
- `logs/packaging_log.jsonl`
- Optional local UI/session state file for in-progress audit work: `audit_session_state.json`

Recommended first local storage:

```text
CODEX Audit Prototype/
  CODEX Session Packages/
  CODEX Issue Extractions/
  CODEX Approval Records/
  CODEX Email Drafts/
  CODEX Archive/
```

Inside live PG later, Claude Code may adapt the folder names to an existing `workflows/` output convention, but evidence IDs and schema fields must remain stable.

## State Names

Use these state names internally. The UI labels can be friendlier, but logs and tests should use stable names.

| State | Meaning |
| --- | --- |
| `audit_idle` | Testing audit panel is open, no session selected. |
| `audit_session_selected` | A source testing session is selected and scanned. |
| `audit_step_ready` | A specific test step is ready for PASS/FAIL/SKIP capture. |
| `audit_capture_armed` | Capture tools are enabled and waiting for screenshot/region action. |
| `audit_capture_in_progress` | System is taking screenshot/region capture. |
| `audit_region_review` | Region capture review dialog is open. |
| `audit_decision_pending` | Evidence exists and tester must choose PASS, FAIL, or SKIP. |
| `audit_fail_detail_editing` | FAIL panel is open for observed/expected/details. |
| `audit_issue_draft` | Structured issue exists but is not approved for package. |
| `audit_package_draft` | Package folder exists but validation is not complete. |
| `audit_package_local_ready` | Manifest and files validate locally. |
| `audit_handoff_ready` | Claude-ready prompt and issue package are ready. |
| `audit_error_recoverable` | Error shown with retry/recover path. |
| `audit_archived` | Local package is closed/archived. |

## Global Interaction Rules

1. Every captured evidence file gets an `evidence_id` before it is shown as package-ready.
2. Every FAIL must have at least one valid evidence ID unless the tester explicitly marks it as `test_authoring` or `unobservable`.
3. Region review can save, recapture, or discard. Discard sets `discarded: true`; do not physically delete the file in MVP.
4. PASS can save optional evidence but does not require a note.
5. FAIL requires observed behavior and expected behavior before issue approval.
6. SKIP requires a short reason.
7. Package validation must run before Claude Handoff is enabled.
8. All write operations append an event to the local audit log.
9. If a data write fails, keep the UI state recoverable and display the target path and suggested action.
10. The module should never infer missing evidence or silently relabel evidence IDs.

## Screen 1: Testing Audit Panel

Purpose: choose a testing session, inspect current status, and enter the capture workflow.

Primary PG-aligned frame:
`01_testing_audit_panel_PG_aligned.png`

### Layout Regions

- Left: Session Queue
- Center: Audit Run Summary
- Right: Open Issues / quality gate notes
- Top: compact stepper: Plan -> Capture -> Review -> Package -> Handoff

### Interactions

| State | User action | System response | Data written | Error handling | Next state |
| --- | --- | --- | --- | --- | --- |
| `audit_idle` | Open Testing Audit Panel | Scan configured testing output locations for latest results/session files. Show empty state if none found. | Append `panel_opened` event to optional `audit_session_state.json`. | If output folder missing, show setup hint with path and `Retry scan`. | `audit_idle` or `audit_session_selected` |
| `audit_idle` | Select session from Session Queue | Load `results_latest.json`, metadata, transcript pointers, screenshot folder, and current run ID. Populate summary counts. | Update `audit_session_state.json`: `selected_session_id`, `source_paths`, `scan_result`. | If JSON unreadable, show `Session cannot be loaded`, keep session row with warning badge. | `audit_session_selected` or `audit_error_recoverable` |
| `audit_session_selected` | Press `RUN STEP` | Select first incomplete or highlighted step. Show instruction content and expected result. | Append `step_opened` event with `step_n`. | If no steps exist, show `No test steps found` and offer `Open source file`. | `audit_step_ready` |
| `audit_session_selected` | Press `VALIDATE` before package exists | Run preflight only: check sources/evidence references, do not build final package. | Write `preflight_validation` event with warnings. | If required files missing, list missing source kinds. | `audit_session_selected` |
| `audit_session_selected` | Open an existing issue row | Load issue details and linked evidence preview. | Append `issue_opened` event. | If evidence file missing, show broken evidence placeholder and validation warning. | `audit_issue_draft` |
| Any panel state | Press `Refresh` | Rescan source paths and preserve selected session when possible. | Append `source_rescan` event. | If selected session disappeared, mark it stale and ask tester to choose another. | Current valid state or `audit_idle` |

### Required Empty States

- No sessions found: show path searched, `Retry scan`, and `Open output folder`.
- Session found but no failures: show PASS summary and allow package build for audit record.
- Session found with invalid JSON: show filename, parse error line when available, and no destructive action.

## Screen 2: Workflow Capture

Purpose: guide tester through the active step and capture evidence without forcing them to remember the contract.

Primary PG-aligned frame:
`02_workflow_capture_PG_aligned.png`

### Layout Regions

- Left: Current Test Step and expected outcome
- Center: PG app/canvas context with capture overlay
- Right: Tester Panel and Evidence Checklist
- Bottom: filmstrip/timeline of evidence for current run

### Interactions

| State | User action | System response | Data written | Error handling | Next state |
| --- | --- | --- | --- | --- | --- |
| `audit_step_ready` | Press `CAPTURE` | Capture full current PG window or active monitor according to existing PG capture behavior. Show busy state and disable duplicate capture button. | Create evidence object `ev_step_auto_####`; copy image to package draft/staging; append `evidence_added`. | If capture fails, show error and keep step active; offer `Retry capture` and `Mark manually`. | `audit_decision_pending` or `audit_error_recoverable` |
| `audit_step_ready` | Press `MARK REGION` | Arm region capture using existing Shift+F12 workflow. Display overlay/crosshair prompt. | Append `region_capture_armed` event. | If region tool unavailable, show fallback instructions and allow full screenshot only. | `audit_capture_armed` |
| `audit_capture_armed` | Complete region selection | Save region image, generate evidence object, open review dialog. | Create `ev_region_####` with capture bounds if available; append `region_captured`. | If save fails, keep temp preview if possible; show path error and `Retry save`. | `audit_region_review` |
| `audit_capture_armed` | Cancel region selection | Dismiss overlay, return to current step without evidence change. | Append `region_capture_cancelled` event. | None unless tool errors; show nonblocking toast. | `audit_step_ready` |
| `audit_decision_pending` | Press `PASS` | Mark step PASS. If evidence exists, link evidence IDs to the step. Advance to next incomplete step. | Update step record: `outcome: PASS`, `evidence_ids`, optional note; append `step_decided`. | If write fails, keep button disabled until retry completes or restore previous state. | `audit_step_ready` or `audit_session_selected` |
| `audit_decision_pending` | Press `FAIL` | Open FAIL detail panel with evidence prelinked. Require observed and expected fields. | Create issue draft shell with `status: needs_review`, source step, evidence IDs. | If no evidence exists, block with `FAIL requires evidence` unless tester marks `test_authoring`. | `audit_fail_detail_editing` |
| `audit_decision_pending` | Press `SKIP` | Prompt for short reason. Save skip and advance. | Update step record: `outcome: SKIP`, `note`; append `step_decided`. | If reason empty, keep prompt open with inline validation. | `audit_step_ready` or `audit_session_selected` |
| Any capture state | Mic transcript segment arrives | Attach transcript ref to active step when timestamps fit current step window. | Create or update `ev_transcript_span_####` / `transcript_ref`. | If timestamp cannot be aligned, add warning and show in Package Validation. | Current state |

### Required Loading States

- Capture busy: buttons disabled, spinner or compact `Capturing...` label.
- Region armed: clear instruction, ESC cancels, Shift+F12 hint remains visible.
- Transcript processing: nonblocking muted badge; never blocks PASS/FAIL.

## Screen 3: Region capture - Review

Purpose: confirm the region image is useful before it becomes durable evidence.

Primary PG-aligned frame:
`03_region_capture_review_PG_aligned.png`

### Layout Regions

- Large image preview
- Bounds/metadata strip
- Right-side evidence object editor
- Buttons: `SAVE EVIDENCE`, `RE-CAPTURE`, `DISCARD`, optional `CREATE ISSUE`

### Interactions

| State | User action | System response | Data written | Error handling | Next state |
| --- | --- | --- | --- | --- | --- |
| `audit_region_review` | Press `SAVE EVIDENCE` | Mark region as accepted and attach it to active step. Close review dialog. | Evidence object: `discarded: false`; step `evidence_ids += ev_region_####`; append `evidence_accepted`. | If manifest/staging write fails, keep dialog open and show exact file path. | `audit_decision_pending` |
| `audit_region_review` | Press `RE-CAPTURE` | Discard current region logically and re-arm region capture. | Set current evidence `discarded: true`; append `evidence_recapture_requested`. | If state update fails, warn but allow new capture; validation will flag stale record. | `audit_capture_armed` |
| `audit_region_review` | Press `DISCARD` | Mark region discarded and close review. Do not delete physical file in MVP. | Evidence object `discarded: true`; append `evidence_discarded`. | If discard cannot be recorded, keep dialog open and show retry. | `audit_step_ready` or `audit_decision_pending` if other evidence exists |
| `audit_region_review` | Edit label/severity/confidence | Update local evidence metadata preview. Do not create issue until user asks. | Update evidence object metadata fields and audit event `field_edited`. | Inline validation for empty label or invalid severity/confidence. | `audit_region_review` |
| `audit_region_review` | Press `CREATE ISSUE` | Save evidence if not already accepted, then open FAIL detail panel. | Ensure evidence linked; create issue draft shell. | If evidence invalid or discarded, require `SAVE EVIDENCE` first. | `audit_fail_detail_editing` |
| `audit_region_review` | Close dialog using X/ESC | Treat as cancel, not discard. Ask if unsaved metadata edits exist. | If no changes, append `review_closed`. If unsaved edits, no write unless saved. | If unsaved edits exist, show `Save`, `Discard edits`, `Cancel`. | Prior state |

### Evidence Object Requirements

A saved region evidence object must include:

- `evidence_id`
- `kind: region_screenshot`
- `step_n`
- `source_path`
- `package_path`
- `mime_type`
- `sha256`
- `bytes`
- `created_at`
- `capture.capture_type: manual_region`
- `privacy.contains_phi`, initially `unknown` unless synthetic/deidentified sample
- `discarded`

## Screen 4: FAIL Detail Panel

Purpose: turn evidence into a precise issue without requiring Claude Code to infer the problem.

Primary PG-aligned frame:
`04_fail_detail_panel_PG_aligned.png`

### Layout Regions

- Left: Evidence Stack
- Center: Structured FAIL/issue editor
- Right: JSON Preview / validation hints

### Interactions

| State | User action | System response | Data written | Error handling | Next state |
| --- | --- | --- | --- | --- | --- |
| `audit_fail_detail_editing` | Enter observed behavior | Save draft field after debounce or on blur. | Issue draft `observed_behavior`; append `field_edited` event. | If text too long, warn but do not truncate silently. | `audit_fail_detail_editing` |
| `audit_fail_detail_editing` | Enter expected behavior | Save draft field after debounce or on blur. | Issue draft `expected_behavior`; append `field_edited`. | Empty expected behavior blocks approval. | `audit_fail_detail_editing` |
| `audit_fail_detail_editing` | Select category | Validate against canonical category list. | Issue draft `category`. | Invalid category reverts and logs UI warning. | `audit_fail_detail_editing` |
| `audit_fail_detail_editing` | Select priority | Validate P0-P3 and show impact hint. | Issue draft `priority`. | P0 requires explicit impact note in MVP. | `audit_fail_detail_editing` |
| `audit_fail_detail_editing` | Add/remove evidence link | Update evidence chip list and preview. | Issue draft `evidence_ids`; append `evidence_added` or `evidence_removed`. | Removing final evidence from a FAIL blocks approval unless category is `test_authoring`. | `audit_fail_detail_editing` |
| `audit_fail_detail_editing` | Press `APPROVE ISSUE` | Validate required fields, generate issue ID if needed, freeze draft into extraction result. | Write/update `audit_issue_extraction_v1.json` issue object with `status: needs_review` or `approved` depending workflow; append `status_changed`. | Show field-level errors and keep focus on first missing field. | `audit_issue_draft` |
| `audit_fail_detail_editing` | Press `REQUEST CHANGES` | Mark draft incomplete and return to editing. | `status: changes_requested`; event note required. | Empty note prompts inline error. | `audit_fail_detail_editing` |
| `audit_fail_detail_editing` | Press `REJECT` | Mark issue rejected but keep archive trail. | `status: rejected`; event with reason. | Reason required. | `audit_issue_draft` |
| `audit_fail_detail_editing` | Press `CANCEL` | If unsaved changes exist, prompt to keep draft, discard edits, or return. | Optional `issue_edit_cancelled` event. | If draft already linked to step, cancellation must not remove evidence. | Prior state |

### Required Issue Fields Before Approval

- `issue_id`
- `package_id`
- `session_id`
- `run_id`
- `title`
- `summary`
- `category`
- `priority`
- `confidence` if AI-generated; human-only draft can default to `1.0`
- `status`
- `source_steps`
- `evidence_ids` or explicit `test_authoring` exception
- `observed_behavior`
- `expected_behavior`
- `impact`
- `audit.events[]`

## Screen 5: Session Package

Purpose: build a deterministic local package and validate it before any handoff.

Primary PG-aligned frame:
`05_session_package_PG_aligned.png`

### Layout Regions

- Left: Generated package tree
- Center: Contract Validation
- Right: Manifest preview

### Interactions

| State | User action | System response | Data written | Error handling | Next state |
| --- | --- | --- | --- | --- | --- |
| `audit_issue_draft` | Press `BUILD PACKAGE` | Create package folder, copy source files, copy accepted evidence, generate manifest and AI extraction input. | `session_package_manifest.json`, `derived/ai_extraction_input_v1.json`, copied `source/`, copied `evidence/`, `logs/packaging_log.jsonl`. | If folder exists, create deterministic new package ID or prompt to overwrite only in dev mode. | `audit_package_draft` |
| `audit_package_draft` | Automatic validation after build | Validate manifest schema, evidence links, hashes, source paths, missing sources. | `logs/validation_report.json`; manifest `warnings[]`; package state. | Errors keep package state `draft`; warnings may allow `local_ready` only when nonblocking. | `audit_package_local_ready` or `audit_error_recoverable` |
| `audit_package_draft` | Press `VALIDATE` | Re-run validation without copying files again unless requested. | Updated validation report and log event. | Show errors grouped by schema, missing file, hash, privacy, transcript. | `audit_package_local_ready` or `audit_package_draft` |
| `audit_package_local_ready` | Press `OPEN FOLDER` | Open package folder in file explorer. | Append `package_folder_opened` event. | If folder missing, mark package stale and offer rebuild. | `audit_package_local_ready` |
| `audit_package_local_ready` | Press `REBUILD PACKAGE` | Recompute manifest and package from current source/drafts. | New package ID recommended; old package remains unless explicit cleanup. | If rebuild fails, preserve previous valid package. | `audit_package_draft` then validation state |
| Any package state | Validation finds PHI uncertainty | Show privacy warning and keep local-only state. | Evidence `privacy.contains_phi: unknown`; report warning. | Disable upload/email/future external transfer until reviewed. | `audit_package_local_ready` with warning or `audit_package_draft` |

### Validation Error Types

| Error type | UI message | Recovery |
| --- | --- | --- |
| Missing required source | `Required source not found` | Choose source folder or rebuild after session completes. |
| Evidence ID missing | `Step references missing evidence` | Relink evidence or remove stale reference. |
| Hash mismatch | `Evidence changed after package build` | Rebuild package or mark package stale. |
| Invalid JSON | `Manifest cannot be parsed` | Show line/column and keep package draft. |
| Privacy unresolved | `PHI status not reviewed` | Mark synthetic/deidentified/unknown; external transfer remains disabled. |
| Transcript drift | `Transcript timing outside step window` | Allow warning; show transcript correction path. |

## Screen 6: Claude Handoff

Purpose: produce a concise, bounded implementation brief after local validation passes.

Primary PG-aligned frame:
`06_claude_handoff_PG_aligned.png`

### Layout Regions

- Left: Claude-ready prompt
- Right: Handoff Quality Gate
- Buttons: `COPY PROMPT`, `EXPORT .MD`, `OPEN EVIDENCE`

### Interactions

| State | User action | System response | Data written | Error handling | Next state |
| --- | --- | --- | --- | --- | --- |
| `audit_package_local_ready` | Open Handoff screen | Generate prompt preview from package manifest and approved/open issues. | `handoff/claude_implementation_prompt.md`; append `handoff_preview_generated`. | If no approved issues exist, show `No implementation issue selected`. | `audit_handoff_ready` or `audit_package_local_ready` |
| `audit_handoff_ready` | Press `COPY PROMPT` | Copy prompt text to clipboard and show toast. | Append `prompt_copied` event only; no package mutation. | If clipboard unavailable, show text selected and offer `EXPORT .MD`. | `audit_handoff_ready` |
| `audit_handoff_ready` | Press `EXPORT .MD` | Write or refresh markdown prompt inside package handoff folder. | `handoff/claude_implementation_prompt.md`; hash/log update. | If file write fails, show path and keep preview. | `audit_handoff_ready` |
| `audit_handoff_ready` | Press `OPEN EVIDENCE` | Open package evidence folder or selected evidence image. | Append `evidence_folder_opened` event. | If evidence missing, return to validation screen with error. | `audit_handoff_ready` or `audit_package_draft` |
| `audit_handoff_ready` | Mark handoff complete | Close package for local MVP; optionally archive. | Manifest state can remain `local_ready`; write local `handoff_completed` event. | If archive write fails, keep handoff ready and show retry. | `audit_archived` or `audit_handoff_ready` |

### Handoff Prompt Must Include

- Task title
- Package path
- Issue ID(s)
- Evidence file paths
- Observed behavior
- Expected behavior
- Impact
- Constraints
- Non-goals
- Acceptance tests
- Explicit instruction to inspect `C:\panda-gallery` read-only before editing
- Explicit instruction not to make broad refactors

## Screen 7: End-To-End Flow Map

Purpose: documentation and reviewer orientation, not an operational screen in MVP.

Primary PG-aligned frame:
`07_end_to_end_flow_map_PG_aligned.png`

### Interactions

| State | User action | System response | Data written | Error handling | Next state |
| --- | --- | --- | --- | --- | --- |
| Any non-capture state | Open flow map/help | Show read-only workflow map and glossary. | Optional `help_opened` event. | If asset missing, show text fallback. | Return to prior state |
| Any non-capture state | Click a workflow stage | Navigate to the corresponding screen if allowed by current state. | Optional `help_stage_clicked` event. | If target unavailable, show required prerequisite. | Target state or prior state |

## Cross-Cutting Error Recovery

### `audit_error_recoverable` Pattern

Every recoverable error screen/panel must show:

- What failed, in plain language
- Exact file/path/resource when relevant
- Whether data was written or not
- Primary recovery action
- Secondary safe action
- Link back to prior safe state

Example:

```text
Could not write validation_report.json
Path: C:\...\logs\validation_report.json
No package state was changed.
Actions: Retry validation | Open package folder | Return to package draft
```

### Nonrecoverable Errors

If PG crashes or capture cannot continue:

- Preserve all already-written evidence.
- Append best-effort `session_interrupted` event on next launch.
- Mark current package `draft` unless validation already passed.
- Show `Resume audit session` when source package/session state is found.

## Keyboard And Focus MVP

Minimum keyboard behavior:

| Key | Behavior |
| --- | --- |
| `F12` | Existing workflow frame capture, if already present in PG. |
| `Shift+F12` | Existing/manual region capture, where current PG supports it. |
| `Esc` | Cancel armed region capture or close non-dirty dialog. |
| `Ctrl+Enter` | Save current FAIL/detail form when valid. |
| `Alt+P` | PASS current step when decision pending. |
| `Alt+F` | Open FAIL panel when decision pending. |
| `Alt+S` | SKIP current step when decision pending. |

Focus rules:

- After capture completes, focus moves to PASS/FAIL/SKIP action row.
- After opening FAIL panel, focus moves to observed behavior field.
- Validation errors move focus to the first invalid field.
- Region review buttons must be reachable by Tab in this order: Save evidence, Re-capture, Discard, Create issue, Close.

## Logging Rules

Every event should use this shape where practical:

```json
{
  "event_id": "evt_YYYYMMDD_HHMMSS_####",
  "event_type": "evidence_added",
  "actor": { "actor_type": "human", "display_name": "Darrin", "email": null },
  "created_at": "ISO-8601 local timestamp",
  "state_before": "audit_capture_armed",
  "state_after": "audit_region_review",
  "entity_refs": { "step_n": 1, "evidence_ids": ["ev_region_0001"], "issue_id": null },
  "note": "Short human-readable note"
}
```

Append-only event logging is preferred. Do not rewrite historical events except in development fixtures.

## Implementation Sequence For Claude Code

1. Add a small state model for audit session UI state.
2. Wire Testing Audit Panel read-only session scan.
3. Add evidence ID generation and evidence object creation around existing screenshot/region outputs.
4. Add Region Review accept/recapture/discard state handling.
5. Add FAIL detail draft object and field validation.
6. Integrate package builder from the Codex reference code.
7. Add validation report display.
8. Generate Claude handoff markdown from validated package and issue draft.
9. Add focused smoke checks for package build and evidence-link validation.
10. Only after local MVP works, discuss upload/AI/email/archive extensions.

## Acceptance Criteria For MVP

- Tester can open Audit Panel and select a completed testing session.
- Tester can capture full screenshot evidence and manual region evidence.
- Region evidence can be saved, recaptured, or discarded without deleting files.
- PASS, FAIL, and SKIP write valid step outcomes.
- FAIL cannot be approved without observed behavior, expected behavior, source step, and evidence or explicit test-authoring exception.
- Package builder writes schema-valid manifest and AI extraction input.
- Validator catches missing evidence references and invalid package paths.
- Claude Handoff is disabled until package validation passes.
- All generated local folders/files stay outside `C:\panda-gallery` unless Darrin explicitly authorizes live integration.
- UI follows PG dark palette and established testing vocabulary.

## Open Questions Before Final Live Integration

1. Should the Audit Panel live inside the existing Testing menu or become a separate dock/pane?
2. Should package build be manual only, or automatic after session completion?
3. Should FAIL issue approval happen inside PG, or should first MVP only generate drafts?
4. What is the minimum supported viewport for the audit UI: current PG minimum, 1366x768, or larger?
5. How should real PHI review be represented if/when real patient screenshots enter the workflow?
6. Should Claude Handoff support one issue per prompt or multi-issue package prompts?
7. Should discarded evidence remain visible in the UI as a collapsed audit trail?

## Related Files

- C:\CODEX PG\CODEX Audit MVP Starter Pack\CODEX scripts\audit_mvp_reference_builder.py
- C:\CODEX PG\CODEX Audit MVP Starter Pack\CODEX scripts\validate_audit_mvp_contracts.py
- C:\CODEX PG\CODEX Canonical Specs\CODEX_SESSION_PACKAGE_SCHEMA_v1.md
- C:\CODEX PG\CODEX Canonical Specs\CODEX_AUDIT_ISSUE_SCHEMA_v1.md
- C:\CODEX PG\CODEX Audit UX Fullscreen Walkthrough PG Aligned\CODEX_audit_ux_fullscreen_walkthrough_PG_aligned_v2.html
