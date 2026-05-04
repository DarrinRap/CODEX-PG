# Inspector / Instruction Pane Validation Spec v1

**Status:** Draft — pending Darrin review
**Date:** 2026-05-05
**Author:** Claude Desktop (CD)
**Session:** 132
**Scope:** Full validation of Inspector / Instruction Pane v4.86.0 (I1–I3),
all 8 phases of `CODEX_INSTRUCTION_PANE_UX_v2_SPEC.md` v2.1.1
**Reference spec:** `C:\CODEX PG\CODEX Canonical Specs\CODEX_INSTRUCTION_PANE_UX_v2_SPEC.md`
**Reference tests:**
- `tests/test_inspector_i1_rename.py`
- `tests/test_inspector_i2_phases1_3.py`
- `tests/test_inspector_i3_phases4_8.py`
**Shipped in:** v4.84.7 (I1), v4.85.0 (I2), v4.86.0 (I3)

---

## 1. Purpose

This spec defines the complete validation protocol for the Instruction Pane
(Inspector) UX v2.1.1 implementation. Eight phases were shipped across three
ship events (I1, I2, I3). Validation has two tracks:

**Track A — Automated:** Run the three existing pytest files. All tests must
pass. Specific test IDs listed per phase.

**Track B — Live manual:** Launch the app with `--dev`, open the Inspector
(`Ctrl+Alt+I`), load `workflows/instructions_latest.json`, and exercise each
feature by eye. Specific steps and pass/fail criteria defined per phase.

Both tracks must pass. A phase that passes automated tests but fails live
manual inspection is not validated.

---

## 2. Pre-Validation Setup

### 2.1 Launch command

**PASTE INTO POWERSHELL**
```powershell
cd C:\panda-gallery; Get-Process python -EA SilentlyContinue | Stop-Process -Force; Start-Sleep 1; python .\panda_gallery.py --dev
```

### 2.2 Open Inspector

Press `Ctrl+Alt+I` from the PG main window. The Inspector dialog opens.
The default instruction file is `workflows/instructions_latest.json`.

### 2.3 Automated suite

**PASTE INTO POWERSHELL**
```powershell
cd C:\panda-gallery; Get-ChildItem -Path . -Filter __pycache__ -Recurse -Directory | Where-Object {$_.FullName -notlike '*\.git\*'} | Remove-Item -Recurse -Force; python -m pytest tests/test_inspector_i1_rename.py tests/test_inspector_i2_phases1_3.py tests/test_inspector_i3_phases4_8.py -v
```

Expected: all tests pass. Any failure is a blocker — do not proceed to
manual validation until the suite is green.

### 2.4 Required fixture

For live manual testing, `workflows/instructions_latest.json` must contain
a valid instruction plan with:
- At least 5 steps
- A mix of `kind: "check"` (single-expected), `kind: "checklist"`, and
  `kind: "action"` steps
- At least one step with a checklist of more than 3 items

The AM v0 polish plan currently in `instructions_latest.json` satisfies
all of these requirements.

### 2.5 Known pre-ship issue

`dev_mode = True` is hardcoded in `panda_gallery.py` with a `REVERT` comment
(tracked by `test_i1_dev_mode_always_on_with_revert_comment`). This must be
reverted before any external ship. It does NOT affect validation — validation
runs with `--dev` flag regardless.

---

## 3. Phase 1 — Surface Rename (I1, v4.84.7)

### 3.1 What shipped

All surfaces that previously said "Testing", "Test Pane", or "Instruction Pane"
were renamed to "Inspector". Developer menu moved under a `Developer` submenu.

### 3.2 Automated tests

| Test ID | Description |
|---|---|
| `test_i1_about_button_tooltip_renamed` | About button tooltip says "Inspector" |
| `test_i1_keyboard_help_dialog_row_renamed` | Keyboard help shows "Inspector" |
| `test_i1_about_dialog_title_renamed` | About dialog title uses "Inspector" |
| `test_i1_settings_window_title_renamed` | Settings window title uses "Inspector" |
| `test_i1_show_inspector_qaction_renamed` | QAction text says "Inspector" |
| `test_i1_top_level_menu_renamed` | Menu label updated |
| `test_i1_dev_mode_always_on_with_revert_comment` | dev_mode=True + REVERT comment |

### 3.3 Manual validation

**V1-1:** In the PG main window menu, find the Inspector option. Confirm it
is labeled "Inspector" (not "Testing", "Test Pane", or "Instruction Pane").

**Pass:** Label reads "Inspector".
**Fail:** Old label or no entry found.

**V1-2:** Open Inspector (`Ctrl+Alt+I`). Confirm the window title bar reads
"Inspector" or "Panda Gallery — Inspector".

**Pass:** Window title contains "Inspector".
**Fail:** Title contains "Testing" or "Pane".

---

## 4. Phase 2 — ESC Dispatcher (I2, v4.85.0)

### 4.1 What shipped

A centralized ESC dispatcher (`_dispatch_escape`) that handles ESC in
priority order per spec §6.2. Bare ESC never resets run state.

**Priority order:**
1. If FAIL/PASS+NOTE note panel is open → close panel, preserve step state
2. If About panel is open → close About
3. If question view is open → return to step view
4. If index drawer is open → close drawer
5. If modal confirmation is open → let dialog handle it
6. Otherwise → no-op (never resets, never closes pane)

### 4.2 Automated tests

Run `tests/test_inspector_i2_phases1_3.py` — all tests cover I2 functionality
including ESC dispatcher, PASS+NOTE, and results schema.

### 4.3 Manual validation

**V2-1 — Bare ESC is a no-op on the step view:**
1. Open Inspector. Start a run (click through to the first step).
2. Answer 2-3 steps with PASS.
3. On the current step, press ESC.
4. Observe: pane stays open, current step remains visible, prior answers preserved.

**Pass:** Nothing changes — step view remains, no dialog, no reset.
**Fail:** Pane closes, run resets, or dialog appears asking to confirm close.

**V2-2 — ESC closes FAIL note panel without writing result:**
1. On any single-expected step, click `FAIL`.
2. The FAIL note panel opens. Do NOT enter any text.
3. Press ESC.
4. Observe: note panel closes, step returns to unanswered state, no FAIL recorded.

**Pass:** Panel closes; step shows as unanswered (no outcome dot).
**Fail:** Panel stays open, or a FAIL outcome is written without a note.

**V2-3 — ESC closes PASS+NOTE panel without writing result:**
1. On any single-expected step, click `PASS + NOTE`.
2. The PASS+NOTE panel opens. Do NOT enter text.
3. Press ESC.
4. Observe: panel closes, step unanswered, no outcome written.

**Pass:** Panel closes cleanly, no PASS_WITH_NOTE recorded.
**Fail:** Outcome written despite ESC.

---

## 5. Phase 3 — PASS + NOTE Outcome (I2, v4.85.0)

### 5.1 What shipped

A third footer button `PASS + NOTE` on single-expected steps. Opens a note
panel, writes outcome `PASS_WITH_NOTE` to results. Treated as pass for
completion metrics. Rendered as green dot with asterisk in outcome strip.

### 5.2 Automated tests

Run `tests/test_inspector_i2_phases1_3.py` in full. Key tests covering
PASS+NOTE specifically include `test_i2_pass_note_button_exists`,
`test_i2_pass_note_panel_title`, `test_i2_pass_note_outcome_string`,
`test_i2_pass_note_treated_as_pass_for_completion`, and
`test_i2_pass_note_dot_has_asterisk`. If these names differ, check the
test file for the equivalent coverage.

### 5.3 Manual validation

**V3-1 — PASS+NOTE button visible on single-expected steps:**
1. Navigate to a `kind: "check"` step (single-expected, with EXPECTED text).
2. Inspect the footer.

**Pass:** Three buttons visible: `PASS`, `PASS + NOTE`, `FAIL`.
**Fail:** Only two buttons, or button labeled differently (e.g. "Pass with note").

**V3-2 — PASS+NOTE panel opens, note required, advance works:**
1. Click `PASS + NOTE`.
2. Panel opens with title containing `PASS + NOTE`.
3. Enter a note: `"Works but contrast is low on the header"`.
4. Click `SAVE NOTE`.

**Pass:** Step advances, outcome dot turns green with asterisk, next step renders.
**Fail:** Step does not advance, or outcome is recorded as plain PASS without note.

**V3-3 — PASS_WITH_NOTE in results file:**
After saving a PASS+NOTE outcome, open the results file written by the run.
Confirm:
- `"outcome": "PASS_WITH_NOTE"` in the step's result entry
- `"note": "<your text>"` field present and non-empty
- The results file root contains a `"capabilities"` array including
  `"pass_with_note"`

**Pass:** All three fields present with correct values.
**Fail:** Outcome recorded as `"PASS"` (note lost), or note field absent.

**V3-4 — PASS_WITH_NOTE treated as pass for completion:**
Complete a run where one step is PASS_WITH_NOTE and all others are PASS.
Observe the run-end summary.

**Pass:** Summary shows completion, PASS_WITH_NOTE step counted in the pass
column, shown separately (e.g. "12 pass · 1 pass with note · 0 fail").
**Fail:** Run never completes (PASS_WITH_NOTE treated as incomplete), or
PASS_WITH_NOTE counted as fail.

---

## 6. Phase 4 — Outcome Strip + Remaining Count (I3, v4.86.0)

### 6.1 What shipped

A persistent compact header showing:
- `Step N of M` progress
- `R remaining` count
- An outcome dot strip for all steps with color-coded state

### 6.2 Automated tests

| Test ID | Description |
|---|---|
| `test_i3_phase4_remaining_lbl_constructed` | Remaining label widget exists |
| `test_i3_phase4_index_button_constructed_with_glyph` | Index button exists |
| `test_i3_phase4_outcome_strip_host_constructed` | Strip host widget exists |
| `test_i3_phase4_outcome_constants_defined` | All outcome constant strings defined |
| `test_i3_phase4_outcome_for_step_helper_exists` | Helper method exists |
| `test_i3_phase4_compute_remaining_helper_exists` | Remaining count helper exists |
| `test_i3_phase4_update_remaining_lbl_phrasing` | Label phrasing correct |
| `test_i3_phase4_render_outcome_strip_handles_compressed_mode` | Strip compresses >10 steps |
| `test_i3_phase4_outcome_dot_tooltip_format` | Dot tooltips show step+title+outcome |
| `test_i3_phase4_render_step_calls_strip_and_remaining_updaters` | Strip updates on render |
| `test_i3_phase4_render_summary_calls_updaters` | Strip updates at summary |

### 6.3 Manual validation

**V4-1 — Strip appears and progress updates:**
1. Open Inspector and start a run.
2. Observe the header area.

**Pass:** Outcome strip visible, dots for each step shown, current step
indicated with peach/accent ring, remaining count label visible.
**Fail:** No strip, no dots, no remaining count.

**V4-2 — Dot colors correct per outcome:**
1. Answer step 1 with PASS (green dot).
2. Answer step 2 with FAIL (red dot).
3. Answer step 3 with PASS+NOTE (green dot with asterisk).
4. Leave step 4 unanswered and navigate to step 5 via the index drawer
   (dot stays in pending/grey-ring state — unanswered gap).

**Pass:** Dot colors match: green, red, green+asterisk, grey ring.
**Fail:** Any dot color mismatch, or no asterisk on PASS_WITH_NOTE dot.

**V4-3 — Dot tooltip shows step info:**
Hover over any answered dot.

**Pass:** Tooltip shows step number, title, and outcome.
**Fail:** No tooltip, or tooltip shows generic text.

---

## 7. Phase 5 — Mid-Run Index Drawer (I3, v4.86.0)

### 7.1 What shipped

An index drawer (modal dialog) reachable from the header button. Shows all
steps with badges, outcomes, and jump targets. Allows navigation to any step
without losing answers.

### 7.2 Automated tests

| Test ID | Description |
|---|---|
| `test_i3_phase5_drawer_module_exists` | `instruction_pane_index_drawer.py` exists |
| `test_i3_phase5_drawer_class_is_qdialog_with_jump_signal` | Class is QDialog, has `jump_to` signal |
| `test_i3_phase5_drawer_modal_minimum_size_matches_step0` | Minimum size ≥ 400px wide |
| `test_i3_phase5_drawer_kind_badge_text_setup_for_action` | Action step shows "Setup" badge |
| `test_i3_phase5_drawer_outcome_badge_labels` | All outcome badge labels correct |
| `test_i3_phase5_drawer_resume_button_hidden_by_default` | Resume hint hidden initially |
| `test_i3_phase5_drawer_jump_to_future_shows_resume_hint` | Jump to future shows resume |
| `test_i3_phase5_has_note_helper_distinguishes_blank` | Note indicator logic correct |
| `test_i3_phase5_pane_open_drawer_handler_imports_module` | Pane imports drawer module |
| `test_i3_phase5_jump_to_step_renders_target` | Jump renders correct step |
| `test_i3_phase5_drawer_lookup_first_unanswered` | Finds first unanswered step |
| `test_i3_ac7_drawer_jump_back_does_not_lose_progress` | Jump doesn't lose answers |

### 7.3 Manual validation

**V5-1 — Drawer opens from header:**
1. Start a run, answer 2 steps.
2. Click the index button in the header.

**Pass:** Index drawer opens, all steps listed with step number, title, kind
badge (Check/Checklist/Setup), and outcome badge.
**Fail:** Drawer doesn't open, or shows empty/incomplete list.

**V5-2 — Jump to answered step, return, no data loss:**
1. In the drawer, click a previously answered step.
2. The pane renders that step showing the prior answer.
3. Without changing anything, return to the current step (via Resume or close drawer).
4. Confirm all prior answers are intact.

**Pass:** Prior answer visible on jumped-to step; return preserves all answers.
**Fail:** Answer is cleared on jump, or other answers lost.

**V5-3 — Jump to future unanswered step shows resume hint:**
1. Open drawer, click a future step not yet answered.
2. Observe footer.

**Pass:** Footer shows a "Resume first unanswered" hint or similar.
**Fail:** No hint, or step is rendered as if it's the current step with no indication of a gap.

**V5-4 — ESC closes drawer:**
1. Open the index drawer.
2. Press ESC.

**Pass:** Drawer closes, pane returns to the step it was on before.
**Fail:** Drawer stays open, or pane state changes.

---

## 8. Phase 6 — Action Step Restyle (I3, v4.86.0)

### 8.1 What shipped

`kind: "action"` steps render with a `SETUP` badge, muted body block, and a
`Done` button only (no PASS/FAIL options). Outcome strip shows action-step
dots in a neutral acknowledged state, distinct from green PASS.

### 8.2 Automated tests

| Test ID | Description |
|---|---|
| `test_i3_phase6_action_header_label_setup` | Header label shows "SETUP" |
| `test_i3_phase6_action_body_setup_phrasing` | Body uses setup visual treatment |
| `test_i3_phase6_ack_button_label_done` | Button label is "Done" not "Got it" |

### 8.3 Manual validation

**V6-1 — Action steps render as Setup:**
1. Navigate to a `kind: "action"` step in the run.

**Pass:** Step shows a `SETUP` badge or header label, muted/dimmed body text,
and a single `Done` button. No PASS/FAIL/SKIP buttons.
**Fail:** Action step looks like a regular check step with PASS/FAIL buttons.

**V6-2 — Done advances step, dot is neutral:**
1. On an action step, click `Done`.
2. Step advances to the next step.
3. Check the outcome strip dot for the action step.

**Pass:** Run advances; action dot is a neutral color (not green), distinct
from PASS dots.
**Fail:** Step does not advance, or action dot is green (same as PASS).

---

## 9. Phase 7 — Authoring Lint Warnings (I3, v4.86.0)

### 9.1 What shipped

A non-blocking lint pass (`instruction_lint.py`) runs after schema validation.
Warnings surface in the About panel. They do not block the run.

Lint rules: `placeholder_title`, `unknown_reference`, `compound_body`,
`action_overuse`, `action_can_fold`, `long_run`, `long_checklist`,
`paraphrased_expected` (info), `external_dependency` (info).

### 9.2 Automated tests

| Test ID | Description |
|---|---|
| `test_i3_phase7_lint_module_exists` | `instruction_lint.py` exists |
| `test_i3_phase7_lint_public_api` | `lint_instructions` and `split_by_severity` exported |
| `test_i3_phase7_lint_no_steps_returns_empty_list` | Empty steps → no warnings |
| `test_i3_phase7_lint_warning_shape_complete` | Warning objects have all required fields |
| `test_i3_phase7_split_by_severity_separates_lists` | Severity splitting correct |
| `test_i3_phase7_*_positive/negative` — all rules | All `test_i3_phase7_` prefixed tests for rule firing |
| `test_i3_phase7_lint_integration_load_path` | Lint called during pane load |
| `test_i3_phase7_about_panel_surfaces_warning_severity_only` | Only warning (not info) shown in About |
| `test_i3_phase7_results_writer_persists_authoring_warnings` | Warnings written to results |

### 9.3 Manual validation

**V7-1 — About panel shows warnings for AM v0 plan:**
1. Load `workflows/instructions_latest.json` (the AM v0 polish plan).
2. Click the About button in the pane header.
3. Scroll to "Authoring warnings" section.

**Pass:** At least one warning visible (the AM v0 plan has known authoring
issues like ambiguous references). Warnings are readable with step number,
code, and message.
**Fail:** No warnings shown, or section absent from About.

**V7-2 — Warnings do not block the run:**
1. With the same plan loaded, start the run.

**Pass:** Run begins normally; first step renders.
**Fail:** Warnings block the run or force confirmation.

**V7-3 — Info-level findings NOT shown in About:**
Inspect the About panel warnings. Confirm only `warning`-severity entries
appear. Info-severity entries (like `paraphrased_expected`, `external_dependency`)
should NOT appear in the About panel — they are for author tooling only.

**Pass:** About panel shows only `warning` severity; no `info` items.
**Fail:** Info items appear in About panel, cluttering tester view.

---

## 10. Phase 8 — Paper Export (I3, v4.86.0)

### 10.1 What shipped

A paper-mode HTML export: `workflows/audit/<run_id>_paper.html`. Self-contained,
print-styled, 4 columns (# / Step / Outcome boxes / Notes). Available via
pane header button and CLI.

### 10.2 Automated tests

| Test ID | Description |
|---|---|
| `test_i3_phase8_paper_module_exists` | Paper export module exists |
| `test_i3_phase8_paper_public_api` | Export function exported |
| `test_i3_phase8_paper_exports_to_audit_dir` | Output in `workflows/audit/` |
| `test_i3_phase8_paper_has_four_columns` | HTML has #/Step/Outcome/Notes columns |
| `test_i3_phase8_paper_action_step_renders_setup_badge_and_done_box` | Action rows correct |
| `test_i3_phase8_paper_checklist_step_renders_items_and_outcome_boxes` | Checklist rows correct |
| `test_i3_phase8_paper_single_expected_renders_three_outcome_boxes` | P/PN/F boxes on check steps |
| `test_i3_phase8_paper_header_includes_run_metadata` | Title, timestamp, source path |
| `test_i3_phase8_paper_print_styled_with_page_rules` | Print CSS present |
| `test_i3_phase8_paper_self_contained_no_network` | No external URLs in HTML |
| `test_i3_phase8_paper_cli_smoke` | CLI invocation works |
| `test_i3_phase8_paper_cli_rejects_missing_file` | CLI rejects missing input |
| `test_i3_phase8_paper_cli_rejects_no_steps` | CLI rejects empty plan |
| `test_i3_ac9_paper_html_renders_all_step_kinds` | All step kinds in one export |

### 10.3 Manual validation

**V8-1 — Export from pane header:**
1. Open Inspector with `instructions_latest.json` loaded.
2. Find and click the paper/export button in the pane header (tooltip:
   "Export printable checklist").
3. Confirm the file appears in `workflows/audit/`.

**Pass:** HTML file created with a timestamp-based name.
**Fail:** No file created, or button not found.

**V8-2 — Export via CLI:**

Do NOT use the command below literally — the exact module name may differ.
First read `test_i3_phase8_paper_cli_smoke` to find the correct invocation
and module path. The test will show the exact command that passes.

Once you have the correct command from the test:
**PASTE INTO POWERSHELL**
```powershell
cd C:\panda-gallery; python -m <module_name_from_test> workflows\instructions_latest.json
```

**Pass:** HTML file created in `workflows/audit/`.
**Fail:** Module not found, import error, or no file created.

**V8-3 — Open exported HTML in browser:**
Open the generated `_paper.html` file in a browser. Confirm:
- 4 columns: `#`, step body/title, outcome checkboxes (PASS/PASS+NOTE/FAIL),
  Notes
- Action steps show a `Done` box only, with "SETUP" label
- Checklist steps show individual checklist items with checkbox bullets
- Header shows run title, source file path, and generation timestamp
- No external images, fonts, or scripts loaded from network

**Pass:** All elements present; file opens without network errors.
**Fail:** Missing columns, broken layout, or network requests fired.

---

## 11. Backward Compatibility (I2/I3)

### 11.1 What was promised

Existing `schema_version: 1` and `schema_version: 2` instruction files must
load and run without change. New outcomes (`PASS_WITH_NOTE`) are not required
from old files.

### 11.2 Automated tests

`test_i3_ac5_results_writer_capabilities_block_full` — capabilities block
present with correct entries.

`test_i3_ac8_authoring_warnings_default_empty` — warnings default to empty
list on fresh results.

### 11.3 Manual validation

**V11-1 — v2 file loads and runs normally:**
Create a minimal fixture instruction file at `workflows/instructions_v2_compat.json`
with schema_version 2 and 2 steps (one `kind: "check"`, one `kind: "action"`):
```json
{"schema_version": 2, "title": "Compat test", "steps": [
  {"step_n": 1, "test_id": "T1", "kind": "check", "title": "Verify app loads",
   "body": "Open the app.", "expected": "App opens without error."},
  {"step_n": 2, "test_id": "T2", "kind": "action", "title": "Close app",
   "body": "Close the app."}
]}
```
Load this file via the Inspector settings. Confirm it loads, starts, and
produces ordinary PASS/FAIL/ACK results without errors.

**Pass:** File loads and runs normally.
**Fail:** Load error, validation failure, or crash.

---

## 12. Results Schema (I2/I3)

### 12.1 Automated tests

| Test ID | Description |
|---|---|
| `test_i3_ac5_results_writer_capabilities_block_full` | Capabilities includes pass_with_note, authoring_warnings |
| `test_i3_ac6_set_authoring_warnings_persists` | Warnings persisted to results file |

### 12.2 Manual validation

**V12-1 — Results file has capabilities block:**
After completing at least one step (any outcome), locate the results file
written to `workflows/audit/`. Open it and confirm:
```json
{
  "capabilities": ["pass_with_note", "authoring_warnings"],
  ...
}
```

**Pass:** Capabilities array present with at least these two entries.
**Fail:** Capabilities absent, or wrong values.

---

## 13. Regression Checks

These behaviors were working before I1–I3 and must continue to work.

| # | Check | Pass condition |
|---|---|---|
| R1 | Inspector opens | `Ctrl+Alt+I` opens the pane dialog |
| R2 | Capture shortcut | During an active capture session (started with `Ctrl+Alt+R`), `Ctrl+Alt+C` captures a frame without error (check debug_log.txt for confirmation if the UI shows no feedback) |
| R3 | Start capture | `Ctrl+Alt+R` starts a screen capture session — a capture region or countdown indicator appears |
| R4 | Abort capture | After starting capture with `Ctrl+Alt+R`, `Ctrl+Alt+A` aborts the session and returns to idle state |
| R5 | PASS advances | Clicking PASS on a step advances to next step |
| R6 | FAIL writes note | Clicking FAIL, entering text, clicking Save writes FAIL outcome with note |
| R7 | SKIP on checklist | SKIP button on checklist items marks item as skipped |
| R8 | Review-all at end | Reaching the last step shows a summary/review screen |
| R9 | Settings dialog | Clicking About or settings opens the correct panel |
| R10 | Results archive | Results are written to `workflows/audit/` on run completion |

---

## 14. Validation Sign-Off

When all of the following are true, this validation is complete:

- [ ] All automated tests pass (`test_inspector_i1_rename.py`, `test_inspector_i2_phases1_3.py`, `test_inspector_i3_phases4_8.py`)
- [ ] V1-1 through V1-2 pass (Phase 1 — rename)
- [ ] V2-1 through V2-3 pass (Phase 2 — ESC dispatcher)
- [ ] V3-1 through V3-4 pass (Phase 3 — PASS+NOTE)
- [ ] V4-1 through V4-3 pass (Phase 4 — outcome strip)
- [ ] V5-1 through V5-4 pass (Phase 5 — index drawer)
- [ ] V6-1 through V6-2 pass (Phase 6 — action steps)
- [ ] V7-1 through V7-3 pass (Phase 7 — lint warnings)
- [ ] V8-1 through V8-3 pass (Phase 8 — paper export)
- [ ] V11-1 passes (backward compatibility)
- [ ] V12-1 passes (results schema)
- [ ] All regression checks R1–R10 pass

Validator: ___________
Date: ___________
Version tested: v4.88.1
