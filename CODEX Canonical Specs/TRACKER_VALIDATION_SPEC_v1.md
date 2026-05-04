# Tracker Validation Spec v1

**Status:** Draft — pending Darrin review
**Date:** 2026-05-04
**Author:** Claude Desktop (CD)
**Session:** 132
**Scope:** Manual and automated validation of Tracker UX bugs #179–#183
shipped in v4.87.1 (commit 7b75e49 + a1c1340)
**Reference spec:** `C:\panda-gallery\workflows\design\TRACKER_UX_SPEC_v1.md`
**Reference tests:** `C:\panda-gallery\tests\audit_module\test_tracker_ux_session129.py`

---

## 1. Purpose

This spec defines the complete validation protocol for the five Tracker UX
improvements shipped in session 129. Validation has two tracks:

- **Track A — Automated:** Run the existing pytest suite. All tests must
  pass. Specific test IDs listed per bug below.
- **Track B — Live manual:** Launch PG with `--dev`, open the Tracker
  (Ctrl+T or AM button), and exercise each feature by eye. Specific steps
  and pass/fail criteria defined per bug below.

Both tracks must pass before a bug is marked VALIDATED. A bug that passes
automated tests but fails live manual inspection is not validated.

---

## 2. Pre-Validation Setup

### 2.1 Launch command

```powershell
cd C:\panda-gallery
Get-Process python -EA SilentlyContinue | Stop-Process -Force
Start-Sleep 1
python .\panda_gallery.py --dev
```

### 2.2 Open Tracker

From the PG main window: click the AM/Tracker button in the sidebar.
The Tracker window opens. Confirm version shows v4.88.0 (or later) in
the title bar.

### 2.3 Required state

BUGS.md must contain at least 5 open bugs across UNTRIAGED, DESIGN,
CLARIFY, and READY state categories so all count rows show non-zero values.
The `--dev` flag loads the repo's own BUGS.md automatically.

### 2.4 Run automated suite first

```powershell
cd C:\panda-gallery
Get-ChildItem -Path . -Filter __pycache__ -Recurse -Directory |
  Where-Object {$_.FullName -notlike '*\.git\*'} |
  Remove-Item -Recurse -Force
python -m pytest tests/audit_module/test_tracker_ux_session129.py -v
```

Expected: all tests pass. Any failure is a blocker — do not proceed to
manual validation until the automated suite is green.

---

## 3. Bug #179 — Horizontal Step-Tour Bar

### 3.1 What shipped

- Removed `_WorkflowStepper` (vertical, 4 steps) from `SummaryPane`.
- Added compact horizontal `_StepTourBar` widget (28px tall) in `ScreenA`,
  between the module header and the filter strip.
- Bar is reference-only (non-interactive).

### 3.2 Automated tests

| Test ID | Description |
|---|---|
| `test_179_step_tour_bar_method_exists` | `_build_step_tour_bar()` exists, `setFixedHeight(28)` set |
| `test_179_step_tour_bar_inserted_between_header_and_filter` | Order: header → separator → bar → filter strip |
| `test_179_workflow_stepper_removed_from_summary_pane` | `_WorkflowStepper` gone from `summary_pane.py` |
| `test_179_step_tour_bar_qss_uses_canonical_tokens` | No hardcoded hex in bar QSS |

### 3.3 Manual validation steps

**V179-1:** Open ScreenA (the bug list view). Confirm a single horizontal
bar appears between the TRACKER header bar and the filter strip. Bar must
read: `① Select  →  ② Triage  →  ③ Decide  →  ④ Fix`.

**Pass:** Four steps visible, left-to-right, with arrows between them.

**Fail:** Bar missing, steps out of order, steps truncated, or vertical
stepper still visible in the left column.

**V179-2:** Hover over each step circle and each step label. No visual
change should occur (no hover highlight, no cursor change, no tooltip).

**Pass:** Bar is visually inert on hover.

**Fail:** Any hover effect visible on the bar.

**V179-3:** Inspect the left `SummaryPane` column. Confirm the "ABOUT
THIS VIEW" caps header and the vertical stepper (previously showing
Select / Triage / Decide / Fix vertically) are gone.

**Pass:** No vertical stepper visible in the left column.

**Fail:** Vertical stepper or "ABOUT THIS VIEW" header present.

**V179-4:** Window resize. Drag the Tracker window wider and narrower
down to its minimum size (900px wide, per #176). Confirm the step-tour
bar scales horizontally and remains fully readable at 900px — no steps
clipped, no arrows overlapping.

**Pass:** All four steps and three arrows fully visible at 900px width.

**Fail:** Any step label or arrow clips or overlaps at minimum width.

---

## 4. Bug #180 — Filter Strip Vertical Padding

### 4.1 What shipped

- Filter strip vertical margin reduced from 8px top/bottom to 4px
  top/bottom (`setContentsMargins(16, 4, 16, 4)`).
- Target strip height: 28–30px (previously ~38px).

### 4.2 Automated tests

| Test ID | Description |
|---|---|
| `test_180_filter_strip_padding_compacted` | `setContentsMargins(16, 4, 16, 4)` present; old `16, 8, 16, 8` absent |

### 4.3 Manual validation steps

**V180-1:** Observe the filter strip row (contains: FILTER eyebrow label,
Severity combo, State combo, Show fixed checkbox, result count label).
Confirm the strip is visually compact — approximately equal in height to
the step-tour bar above it (28–30px range).

**Pass:** Filter strip is noticeably thinner than a standard toolbar height.

**Fail:** Filter strip appears as tall as before (approximately 38px); or
content is clipped (combos cut off).

**V180-2:** Activate a filter (e.g., set State to "Untriaged"). Confirm
the filter strip height does not change when a filter is active vs. default.

**Pass:** Height stable with and without active filter.

**Fail:** Strip expands or shifts when filter is active.

---

## 5. Bug #181 — Count Rows as Filter Shortcuts

### 5.1 What shipped

- All five `_CountRow` widgets in `SummaryPane` are now clickable.
- Clicking a row sets the State combo filter to the matching state.
- Clicking the active row a second time clears the filter (toggle-off).
- TOTAL OPEN always resets all filters (Severity + State to "All",
  unchecks Show Fixed). It is never shown as "active."
- Active row renders with `accent_soft` background fill.
- Hover renders with brightened `border_hover` left border.
- Cursor changes to `PointingHandCursor` on all five rows.

### 5.2 Automated tests

| Test ID | Description |
|---|---|
| `test_181_count_row_clicked_signal` | `clicked = Signal(str)` on `_CountRow` |
| `test_181_count_row_pointing_hand_cursor` | `PointingHandCursor` set |
| `test_181_count_row_set_active_method` | `set_active()` forces `_active = False` for TOTAL rows |
| `test_181_summary_pane_filter_signal` | `filter_by_state_requested = Signal(str)` on `SummaryPane` |
| `test_181_summary_pane_set_active_filter_row_clears_total` | None/"total" clears all active rows |
| `test_181_screen_a_state_filter_key_changed_signal` | `state_filter_key_changed = Signal(str)` emits from `_on_filter_changed` |
| `test_181_window_wires_signals_both_directions` | Both signal directions wired in `window.py` |
| `test_181_total_open_resets_all_filters` | TOTAL OPEN sets both combos to "All" + unchecks Show Fixed |
| `test_181_kind_row_toggles_off_on_repeat_click` | Repeat click clears active filter |
| `test_181_integration_count_row_click_emits_key` | Live widget click emits correct key |
| `test_181_integration_set_active_paints_accent_soft` | `set_active(True)` on non-total; TOTAL ignores |
| `test_181_integration_summary_pane_re_emits_row_click` | SummaryPane re-emits row click signal |
| `test_181_integration_set_active_filter_row_paints_one` | `set_active_filter_row("ready")` activates only READY |

### 5.3 Manual validation steps

**V181-1:** Hover over each of the five count rows (TOTAL OPEN, UNTRIAGED,
DESIGN, CLARIFY, READY). Confirm the cursor changes to a pointing hand on
all five.

**Pass:** Hand cursor on all five rows.

**Fail:** Default arrow cursor on any row.

**V181-2:** Click the UNTRIAGED row. Confirm:
- The State combo in the filter strip changes to "Untriaged."
- The bug list reloads showing only untriaged bugs.
- The UNTRIAGED count row shows an `accent_soft` (peach-tinted) background.
- All other count rows remain at their normal background.

**Pass:** All four conditions met.

**Fail:** Any condition not met.

**V181-3:** With UNTRIAGED active, click UNTRIAGED again. Confirm:
- State combo returns to "All."
- Bug list shows all open bugs again.
- UNTRIAGED row returns to its normal background (no accent_soft).

**Pass:** Toggle-off clears filter and background.

**Fail:** Second click has no effect, or filter/background remains.

**V181-4:** Click DESIGN, then click CLARIFY. Confirm:
- DESIGN row clears its active state when CLARIFY is clicked.
- CLARIFY row shows accent_soft.
- Only one row is active at a time.

**Pass:** Only one active row at a time.

**Fail:** Multiple rows active simultaneously.

**V181-5:** With any filter active, click TOTAL OPEN. Confirm:
- State combo → "All."
- Severity combo → "All."
- Show Fixed checkbox → unchecked.
- All count rows show their normal background (TOTAL OPEN never shows
  accent_soft).
- Bug list shows all open bugs.

**Pass:** All resets occur; TOTAL OPEN row has no accent background.

**Fail:** Any combo/checkbox not reset, or TOTAL OPEN shows accent fill.

**V181-6:** Use the State combo directly (not via count row click) to set
a filter. Confirm the matching count row in SummaryPane shows the
accent_soft background automatically.

**Pass:** SummaryPane active state tracks the combo selection bidirectionally.

**Fail:** Count rows do not reflect combo-driven filter changes.

---

## 6. Bug #182 — OWNER Column

### 6.1 What shipped

- New OWNER column at table index 4 (between STATE and FILES).
- 72px fixed width, centered text alignment.
- Cascadia Mono 8px, `text_muted` color (or `text_dim` for FIXED rows and
  absent owner).
- Absent/empty owner renders as `—` (em dash).
- `**Owner:**` field added to `bugs_parser.py` (`_KNOWN_LABELS` +
  `_empty_bug()`).
- FILES column shifted to index 5.

### 6.2 Automated tests

| Test ID | Description |
|---|---|
| `test_182_bugs_parser_owner_field` | `"owner": "owner"` in `_KNOWN_LABELS`; `_empty_bug` seeds it |
| `test_182_bugs_parser_extracts_owner_value` | End-to-end parse: `**Owner:** CC` → `bug["owner"] == "CC"` |
| `test_182_screen_a_table_has_six_columns_owner_at_4` | `QTableWidget(0, 6)`, header labels include "OWNER" at index 4 |
| `test_182_owner_column_72px_fixed_centered` | `setSectionResizeMode(4, Fixed)`, `setColumnWidth(4, 72)`, `AlignCenter` |
| `test_182_owner_absent_renders_em_dash` | Empty `owner_raw` → `"—"` in `text_dim` |
| `test_182_files_column_centered_now_at_index_5` | FILES at index 5, `AlignCenter` |

### 6.3 Manual validation steps

**V182-1:** Open ScreenA (bug list). Confirm the table header row reads:
`#  |  TITLE  |  SEVERITY  |  STATE  |  OWNER  |  FILES`

**Pass:** Six columns in that exact order, left to right.

**Fail:** Five columns, OWNER missing, or column order incorrect.

**V182-2:** Inspect bug rows. Confirm the OWNER column shows values
(CC, CODEX, CLAUDE, DARRIN). Bugs that have no `**Owner:**` field in
BUGS.md must show `—` (em dash) in a dimmer color.

**Pass:** Owner values displayed or `—` for absent; text is monospaced
and smaller than TITLE text.

**Fail:** OWNER column blank (not `—`), wrong values, or wrong font.

**V182-3:** Scroll to FIXED bugs (below the FIXED divider row). Confirm
that OWNER column text renders in a dimmer color than open-bug rows.

**Pass:** FIXED row owner text visibly dimmer.

**Fail:** Same color as open bugs.

**V182-4:** Resize the OWNER column by dragging its header edge. Confirm
the column does not resize (it is Fixed mode).

**Pass:** Column width stays at 72px regardless of drag.

**Fail:** Column resizes when dragged.

---

## 7. Bug #183 — Collapse Layout Stability

### 7.1 What shipped

- `_BugCard.set_collapsed(True)` pins `setFixedHeight` to the natural
  collapsed height (header row only: severity pill + meta strip +
  collapse toggle).
- `set_collapsed(False)` restores natural size via `setMinimumHeight(0)` +
  `setMaximumHeight(16777215)`.
- The `_BugContentRenderer` (FILES / ATTACHMENTS section heads) does not
  shift vertically when the card is toggled.

### 7.2 Automated tests

| Test ID | Description |
|---|---|
| `test_183_set_collapsed_pins_fixed_height_on_collapse` | `set_collapsed(True)` calls `layout().invalidate()`, reads `sizeHint().height()`, calls `setFixedHeight(collapsed_h)` |
| `test_183_set_collapsed_restores_natural_size_on_expand` | `set_collapsed(False)` calls `setMinimumHeight(0)` + `setMaximumHeight(16777215)` |

### 7.3 Manual validation steps

**V183-1:** From ScreenA, click any bug to open ScreenB (the detail view).
Confirm the bug card is visible with a collapse toggle (▲ collapse or
▾ expand) in the top-right area of the card.

**Pass:** Bug card present with visible toggle.

**Fail:** No bug card or no toggle visible.

**V183-2:** While the card is expanded, note the vertical position of the
"FILES" section head below the card. Click the collapse toggle. Confirm:
- The bug card contracts to show only the header row in a single
  clean instant step (no two-phase stutter or intermediate size flicker).
- The "FILES" section head moves up smoothly in one step to sit below
  the now-shorter card. It must NOT jump twice or settle from a wrong
  intermediate position.

**Pass:** "FILES" label moves cleanly in one layout pass with no
visual stutter.

**Fail:** "FILES" label visibly jumps/stutters (moves, pauses at wrong
position, then jumps again) — the pre-fix symptom.

**V183-3:** Click the expand toggle (▾ expand). Confirm:
- The bug card returns to its full height.
- The "FILES" section head returns to its original position (or moves down
  slightly to accommodate the expanded card — this is acceptable as long
  as the collapse→expand cycle is stable and does not introduce
  progressive drift).

**Pass:** Card expands cleanly; no vertical drift across multiple
collapse/expand cycles.

**Fail:** "FILES" label position drifts progressively with each toggle.

**V183-4:** Rapid toggle test. Click collapse and expand five times in
succession. Confirm the layout remains stable with no cumulative shift.

**Pass:** Layout identical after 5 rapid toggles.

**Fail:** Any drift, flicker, or misalignment after rapid toggling.

---

## 8. Regression Checks

These items were working before session 129 and must continue to work.
Spot-check each after validating #179–#183.

| # | Check | Pass condition |
|---|---|---|
| R1 | Tracker ESC closes window | Pressing ESC on ScreenA closes the Tracker window (§7.5 amendment #4) |
| R2 | Severity combo filters bug list | Setting Severity combo to "High" shows only High bugs |
| R3 | Show Fixed checkbox | Checking "Show Fixed" reveals FIXED bugs below the divider |
| R4 | Bug row click opens ScreenB | Clicking any bug row opens the detail view for that bug |
| R5 | Back to list returns to ScreenA | Clicking "← Back to list" from ScreenB returns to the bug list |
| R6 | UNTRIAGED count accurate | UNTRIAGED count row number matches the actual number of Untriaged bugs displayed after clicking the row (also covered by V181-2) |
| R7 | Archive link works | "View Archive" at the bottom of SummaryPane opens the archive screen |
| R8 | Triage with AI button present in ScreenB | Bug detail view shows "✦ Triage with AI" button |
| R9 | Build fix prompt generates file | Clicking "✦ Build fix prompt" writes a file to `workflows/audit/prompts/` |

---

## 9. Known Open Issues (do not re-test as regressions)

These are already logged in BUGS.md and are NOT regression failures:

- **#184** — "Build fix prompt" has no visual confirmation after click.
  The file IS written; the button just doesn't update. Expected to fail
  visual confirmation. Logged, not a blocker for this validation.

---

## 10. Validation Sign-Off

When all of the following are true, this validation is complete:

- [ ] All automated tests in `test_tracker_ux_session129.py` pass (Track A)
- [ ] V179-1 through V179-4 pass (Track B, #179)
- [ ] V180-1 through V180-2 pass (Track B, #180)
- [ ] V181-1 through V181-6 pass (Track B, #181)
- [ ] V182-1 through V182-4 pass (Track B, #182)
- [ ] V183-1 through V183-4 pass (Track B, #183)
- [ ] All regression checks R1–R9 pass
- [ ] Bug #184 observed and confirmed matching BUGS.md description (not a new regression)

Validator: Darrin Rap
Date: ___________
Version tested: v4.88.0
