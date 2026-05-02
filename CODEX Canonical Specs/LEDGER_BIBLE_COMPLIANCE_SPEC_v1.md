# Ledger Bible Compliance Fix Spec v1

Author: Codex  
Date: 2026-05-01  
Audience: Claude Code implementation pass  
Scope: `C:\panda-gallery\panda_ledger\`  
Mode: specification only; do not treat this file as source edits.

## Authority and Guardrails

- This spec implements CD dispatch `CLAUDE-DESKTOP-20260501-132000-LEDGER-COMPLIANCE-DISPATCH`.
- Do not edit `panda_ledger/verify/reference_panel.py`; it is fully exempt by `# pg-lint:disable-file`.
- Do not edit files outside the listed `panda_ledger/` scope unless the implementation discovers a test-only update is required.
- `panda_ledger/verify/verify_screen.py` already contains an R03b waiver for its fallback `QFileDialog`; document it as an acknowledged exception, not a surprise violation.
- Run lint before and after the fix with:

```powershell
python -m pg_design_lint --ide-output --severity-floor info panda_ledger/styles.py panda_ledger/capture/_capture_widgets.py panda_ledger/capture/_dark_dialogs.py panda_ledger/capture/capture_screen.py panda_ledger/verify/checklist_widget.py panda_ledger/verify/mockup_viewer.py panda_ledger/verify/verify_screen.py panda_ledger/browse/decision_detail.py panda_ledger/capture/snippet_widget.py panda_ledger/window.py
```

Baseline from Codex read-only run on 2026-05-01 14:34 PT: 10 files scanned, 34 errors, 76 warnings, 10 info findings.

## Canonical Bible Tokens

Use these exact Bible sources:

- `workflows/design/PG_DESIGN_BIBLE_v1.md` lines 410-423: spacing scale is `4, 8, 12, 16, 24, 32`; off-scale `11px` and `14px` are explicitly called out as smells.
- `workflows/design/PG_DESIGN_BIBLE_v1.md` lines 427-433: radius scale is `2, 4, 6, 8, 999`.
- `workflows/design/PG_DESIGN_BIBLE_v1.md` lines 731-745: status bar `.sb-mode` is the allowed mode-zone color locality.
- `workflows/design/PG_DESIGN_BIBLE_v1.md` lines 1371-1379: resize invariants require visible buttons, fixed inter-button spacing, no horizontal text clipping, and 2 visible lines for multiline fields.
- `workflows/design/PG_DESIGN_BIBLE_v1.md` lines 1433-1478: use `_compute_min_size()` and `_compute_default_size()` to derive floors and defaults.
- `workflows/design/pg_design_spec.json`: closest canonical semantic tokens are `ok=#7fb069`, `warn=#f39c12`, `text_muted=#888888`, `accent=#e8a87c`, `accent_hover=#d4945a`, `accent_ink=#1a1a2e`.

## R17 - Inline Styles and Local QSS Islands

Fix pattern: all QSS moves into `panda_ledger/styles.py::build_app_stylesheet()`. Widgets receive stable object names and, where needed, dynamic properties. Replace constructor `setStyleSheet(...)` calls with `setObjectName(...)`, `setProperty(...)`, and central QSS selectors. If a widget needs a small role variant, create a named selector in `styles.py`; do not leave local string QSS in the widget file.

| File | Line(s) | Current code | Fix |
|---|---:|---|---|
| `panda_ledger/capture/_capture_widgets.py` | 71-156 | `_STEPPER_QSS` and `self.setStyleSheet(_STEPPER_QSS)` | Move `#horizontal_stepper`, `#hstep_label`, `#hstep_num`, `#hstep_line`, and `#stepper_status` rules to `styles.py`; keep state via `state` property. |
| `panda_ledger/capture/_capture_widgets.py` | 254-317 | `_SECTION_QSS` and `self.setStyleSheet(_SECTION_QSS)` | Move `#collapsible_section`, `#section_header`, `#section_chev`, and `#section_warn_marker` to `styles.py`. |
| `panda_ledger/capture/_capture_widgets.py` | 340-343 | `title_label.setStyleSheet(...)` | Give label object name `section_title`; style centrally. |
| `panda_ledger/capture/_capture_widgets.py` | 392-440 | `_STATUSBAR_QSS` and `self.setStyleSheet(_STATUSBAR_QSS)` | Move Capture status bar selectors to `styles.py`; keep `CaptureStatusbar` as a structural widget only. |
| `panda_ledger/capture/_capture_widgets.py` | 480-534 | `_DRAFTCARD_QSS` and `self.setStyleSheet(_DRAFTCARD_QSS)` | Move `#draft_card`, `#draft_title`, `#draft_subtitle`, `#draft_meta` to `styles.py`. |
| `panda_ledger/capture/_dark_dialogs.py` | 32-65, 94 | `_DIALOG_BASE_QSS`; `self.setStyleSheet(_DIALOG_BASE_QSS)` | Move dark dialog rules to `styles.py`; use `#dark_dialog`, button role names, and `#dark_section_label`. |
| `panda_ledger/capture/_dark_dialogs.py` | 151-154 | `DarkSectionLabel.setStyleSheet(...)` | Remove local QSS; object name already exists. Centralize `#dark_section_label`. |
| `panda_ledger/capture/capture_screen.py` | 802, 808 | subtitle and scroll-area `setStyleSheet(...)` in `StagingPickerDialog` | Use object names such as `staging_picker_subtitle` and `staging_picker_scroll`; style centrally. |
| `panda_ledger/verify/checklist_widget.py` | 247-259 | row-level QSS for buttons and reason field | Move `_ChecklistRow`, result button, and reason field selectors to `styles.py`; use button object names/properties. |
| `panda_ledger/verify/checklist_widget.py` | 273 | label `setStyleSheet(...)` | Set object name `checklist_row_label`; centralize. |
| `panda_ledger/verify/checklist_widget.py` | 351, 355-358 | divider/header inline QSS | Use object names `checklist_state_divider` and `checklist_state_header`; centralize. |
| `panda_ledger/verify/checklist_widget.py` | 400, 406 | scroll/body inline QSS | Use `checklist_scroll` and `checklist_inner`; centralize. |
| `panda_ledger/verify/mockup_viewer.py` | 137-154 | heading, scroll, image label inline QSS | Set object names and move to `styles.py`. |
| `panda_ledger/verify/mockup_viewer.py` | 231-235 | paste fallback instructions inline QSS | Set object name `mockup_viewer_instructions`; centralize. |
| `panda_ledger/verify/mockup_viewer.py` | 280-287 | toolbar local QSS | Move toolbar and toolbar button rules to `styles.py`; assign button roles/object names. |
| `panda_ledger/verify/mockup_viewer.py` | 322-324 | splitter handle inline QSS | Move splitter selector to `styles.py`; use object name on splitter. |
| `panda_ledger/verify/verify_screen.py` | 102-105 | splitter handle inline QSS | Use object name on splitter and central selector. |
| `panda_ledger/verify/verify_screen.py` | 245-259 | toolbar, buttons, combo, label local QSS | Move all toolbar selectors to `styles.py`; assign object names and button roles. |
| `panda_ledger/verify/verify_screen.py` | 289-291 | status bar inline QSS | Move status bar selector to `styles.py`; set object name. |

## R02 - Off-Palette Hex Literals

Fix pattern: replace hardcoded off-palette hex values with canonical token lookups in `styles.py`. Use `_hex(palette, group, key, default=...)` only inside `styles.py`; widgets should not contain palette literals.

| File | Line(s) | Current code | Fix |
|---|---:|---|---|
| `panda_ledger/verify/checklist_widget.py` | 253 | `#5ab87a` for PASS checked state | Replace with `ok` token (`#7fb069`) through central selector. |
| `panda_ledger/verify/checklist_widget.py` | 255 | `#e8c87c` for SKIP checked state | Replace with `warn` token (`#f39c12`) through central selector. |
| `panda_ledger/verify/mockup_viewer.py` | 138, 232 | `#888` | Replace with `text_muted` token via central selector. |
| `panda_ledger/verify/verify_screen.py` | 251, 255 | `#555` disabled text | Replace with `text_dim` token if present; otherwise use `text_muted` with disabled opacity/property. |
| `panda_ledger/verify/verify_screen.py` | 258, 290 | `#888` | Replace with `text_muted` token via central selector. |

## R26 - Mode-Zone Color Locality

Fix pattern: mode-zone colors may be declared and used in `styles.py`, but widget constructors and local QSS strings must not contain raw mode-zone hex values. For lint cleanliness, either adjust R26 to explicitly exempt `styles.py` token declarations or add a narrow `pg-lint:allow R26` comment there with the reason "central token authority". Do not add broad file disables.

| File | Line(s) | Current code | Fix |
|---|---:|---|---|
| `panda_ledger/styles.py` | 33, 38 | token fallback defaults `#e8a87c`, `#7fb069` are flagged by current R26 | Preferred: teach R26 that `styles.py` token extraction/defaults are the central allowed locality. If lint-only change is out of scope, add narrow inline allow comments for these token declarations. |
| `panda_ledger/capture/_capture_widgets.py` | 51, 55 | local `_TOKEN_ACCENT`, `_TOKEN_OK` | Delete local token mirror; consume central styles only. |
| `panda_ledger/capture/_dark_dialogs.py` | 51-57, 78, 152 | local `#e8a87c` in dark dialog QSS/comments | Move active/primary styling to `styles.py`; comments may name `accent` without embedding hex. |
| `panda_ledger/verify/checklist_widget.py` | 251, 258, 356 | local accent hex in hover/focus/header | Centralize hover/focus/header selectors; no raw accent in widget file. |
| `panda_ledger/verify/mockup_viewer.py` | 285-286, 324 | local accent hex in toolbar checked/splitter hover | Centralize selectors; no raw accent in widget file. |
| `panda_ledger/verify/verify_screen.py` | 104, 250, 252 | local accent hex in splitter/toolbar primary | Centralize selectors; no raw accent in widget file. |

## R04 - Off-Scale Spacing

Fix pattern: replace off-scale spacing with the closest Bible §4.1 scale value. General mapping: `2px -> 4px` unless it is a 1px divider/border; `6px -> 8px`; `9px/10px -> 8px or 12px` based on visual density; `14px -> 16px`; `18px -> 16px`. Inter-button gaps are a special Bible §13 value: 10px is allowed for button clusters, but R04 currently flags it. Where the value is truly inter-button spacing, either use a named helper/constant plus a narrow R04 allowance, or adjust R04 to honor §13's 10px exception.

| File | Line(s) | Current code | Fix |
|---|---:|---|---|
| `panda_ledger/browse/decision_detail.py` | 51 | `layout.setSpacing(6)` | Use `8`. |
| `panda_ledger/capture/_capture_widgets.py` | 159, 335, 361 | `setSpacing(6)` / 6px layout gaps | Use `8`. |
| `panda_ledger/capture/_capture_widgets.py` | 334, 360, 445, 546 | 10px margins/gaps | Use `8` or `12` unless it is a true inter-button cluster; document any §13 10px exception. |
| `panda_ledger/capture/_capture_widgets.py` | 444 | `setContentsMargins(14, ...)` | Use `16`. |
| `panda_ledger/capture/_capture_widgets.py` | 546 | mixed `9px`/`10px` content margins | Use `8`/`12` consistently. |
| `panda_ledger/capture/_dark_dialogs.py` | 97 | margins `18, 16, 18, 14` | Use `16, 16, 16, 16` or `16, 16, 16, 12` if the bottom needs tighter chrome. |
| `panda_ledger/capture/capture_screen.py` | 659 | `2px` spacing/margin | Use `4`, unless this is a 1px divider. |
| `panda_ledger/capture/snippet_widget.py` | 60 | `setSpacing(6)` | Use `8`. |
| `panda_ledger/verify/checklist_widget.py` | 265, 269, 409 | `6px` row and outer spacing | Use `8`. |
| `panda_ledger/verify/checklist_widget.py` | 346 | `2px` spacing | Use `4`. |
| `panda_ledger/verify/mockup_viewer.py` | 134 | `2px` padding | Use `4`. |

## R15 - WA_StyledBackground

Fix pattern: when a widget renders a `background` or `background-color` QSS rule and relies on Qt stylesheet painting, call `setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)` on that widget. If R17 centralization removes local `background` QSS, still add the attribute where the widget receives a central background rule and is a `QWidget`/`QFrame` surface.

| File | Line(s) | Current code | Fix |
|---|---:|---|---|
| `panda_ledger/capture/_dark_dialogs.py` | 151 | `DarkSectionLabel.setStyleSheet(... background: transparent ...)` | Prefer central transparent label styling and no attribute. If a background fill remains, add WA. |
| `panda_ledger/capture/capture_screen.py` | 802, 808 | subtitle and scroll area background QSS | If central style keeps a background on these widgets, add WA to the target widget. |
| `panda_ledger/verify/checklist_widget.py` | 247, 351, 400, 406 | row/divider/scroll/inner background QSS | Add WA to `_ChecklistRow`, divider if applicable, `_scroll`, and `_inner` after centralization. |
| `panda_ledger/verify/mockup_viewer.py` | 147, 154, 231, 280, 322 | scroll, image label, instructions, toolbar, splitter background QSS | Add WA to widgets with central background selectors. |
| `panda_ledger/verify/verify_screen.py` | 102, 245, 289 | splitter, toolbar, status bar background QSS | Add WA to splitter/toolbar/status widget if central background selectors require Qt stylesheet painting. |

## R25 - Resizable Surface Compliance

Fix pattern: implement `_compute_min_size()` and `_compute_default_size()` per Bible §13.5. Apply `setMinimumSize(self._compute_min_size())`, then use `_compute_default_size()` for first open; persist/restore geometry with `QSettings`. Reference `instruction_pane.py::TestingSettingsDialog` lines 2607-2624 and 2626-2640 as the current codebase pattern, but use the Bible method names with underscores because R25 expects them.

| File | Line(s) | Current code | Fix |
|---|---:|---|---|
| `panda_ledger/window.py` | 29, 44 | `LedgerWindow(QMainWindow)` with `self.resize(1280, 800)` | Add `_compute_min_size()`, `_compute_default_size()`, QSettings geometry restore/save, and replace hardcoded resize with default-size derivation. |
| `panda_ledger/capture/_dark_dialogs.py` | 68 | `DarkDialogBase(QDialog)` lacks sizing methods and geometry persistence | Add `_compute_min_size()` and `_compute_default_size()` to the base so `StagingPickerDialog` inherits the behavior. Add QSettings geometry key based on dialog objectName/class. |
| `panda_ledger/capture/capture_screen.py` | 833 | `self.resize(700, 520)` in `StagingPickerDialog` | Remove hardcoded dialog default after `DarkDialogBase` grows `_compute_default_size()`; call inherited sizing after body construction. |

## R03 - Forbidden QGroupBox

Fix pattern: replace `QGroupBox` section framing with a `QFrame` container plus `QLabel` header. The structural pattern may follow `CollapsibleSection` in `_capture_widgets.py` (QFrame + header + body layout), but its local QSS must be fixed through R17 before copying any styling.

| File | Line(s) | Current code | Fix |
|---|---:|---|---|
| `panda_ledger/browse/decision_detail.py` | 19 | `QGroupBox` import | Remove import. |
| `panda_ledger/browse/decision_detail.py` | 67 | `QGroupBox("Frontmatter", self)` | Replace with `QFrame#decision_detail_section`; add `QLabel#decision_detail_section_header` text `FRONTMATTER`; body uses `QFormLayout`. |
| `panda_ledger/browse/decision_detail.py` | 73 | `QGroupBox("Body", self)` | Replace with section frame/header/body layout. |
| `panda_ledger/browse/decision_detail.py` | 80 | `QGroupBox("Chain", self)` | Replace with section frame/header/body layout. |

## R03b - QFileDialog

Fix pattern: do not add a dark custom file picker unless product need warrants it. File picking is warning-level debt. If a native file picker is retained, add a narrow `# noqa: pg-lint:allow R03b` with a reason comment on the call site and make sure the import line is not flagged as an unwaived surprise.

| File | Line(s) | Current code | Fix |
|---|---:|---|---|
| `panda_ledger/capture/snippet_widget.py` | 25-26, 160-162 | `QFileDialog` import and `getOpenFileName(...)` with no waiver | Recommended: retain native picker for image snippet selection and add narrow waiver at the call site: `# noqa: pg-lint:allow R03b -- image file picker, no dark replacement exists yet; warning-level debt`. If lint still flags import, add import-line waiver too. |
| `panda_ledger/verify/verify_screen.py` | 34-36, 313-316 | `QFileDialog` fallback with existing waiver at line 315 | Acknowledged exception, waiver in place. Do not spec a source fix. If lint still reports the import line, add an import-line waiver matching the existing call-site reason. |

## R18 - Off-Scale Radius

Fix pattern: use Bible §4.2 radius values only: 2, 4, 6, 8, 999. The current 3px values should generally become 4px for buttons/inputs because `radius-md` is the default for buttons, inputs, view-controls, and info cards.

| File | Line(s) | Current code | Fix |
|---|---:|---|---|
| `panda_ledger/verify/checklist_widget.py` | 250, 257 | `border-radius: 3px` | Use central `radius-md` / 4px. |
| `panda_ledger/verify/mockup_viewer.py` | 284 | `border-radius: 3px` | Use central `radius-md` / 4px. |
| `panda_ledger/verify/verify_screen.py` | 249, 257 | `border-radius: 3px` | Use central `radius-md` / 4px. |

## Button Role Taxonomy

Fix pattern: `styles.py` needs objectName/property-based roles instead of one generic `QPushButton` rule plus `#capture_lock_button`. Keep the generic `QPushButton` as the safe secondary default, then add explicit role selectors. Use dynamic property `role` where many buttons share a role; use objectName only for one-off special components.

Recommended central roles:

- `role="primary"`: one main action per screen/dialog. Peach fill, accent ink text. Examples: `capture_lock_button`, `verify_signoff_button`, `dark_dialog_primary`.
- `role="secondary"`: normal actions. Raised pane background, border, text. Examples: load, save draft, connect, add.
- `role="destructive"`: irreversible or removal actions. Error border/text or restrained error fill on active/confirm states. Examples: `capture_discard_button`, `capture_retire_button`, `qa_pair_remove`.
- `role="utility"`: browse, refresh, zoom, mode/toggle utilities. Compact but still rectangular action controls. Examples: `snippet_paste_browse`, `mockup_viewer_refresh`, zoom buttons.
- `role="recovery"`: undo-like action. Success/warn-outline treatment, not destructive. Example: `capture_unlock_button`.

| File | Line(s) | Current code | Fix |
|---|---:|---|---|
| `panda_ledger/styles.py` | 66-83 | one generic `QPushButton` plus `#capture_lock_button` | Add role selectors: `QPushButton[role="primary"]`, `[role="secondary"]`, `[role="destructive"]`, `[role="utility"]`, `[role="recovery"]`, checked/toggled variants, disabled variants. |
| `panda_ledger/styles.py` | 47 | `font-family: {ui_family}` triggers R06 because lint sees the placeholder | Resolve by formatting the literal family into a lint-acceptable family string, or add a narrow R06 allow on the central generated-family line. Do not change widgets to local font families. |
| `panda_ledger/capture/_dark_dialogs.py` | 117-123 | both cancel and primary use objectName `dark_btn`; primary uses `primary=True` | Replace with role properties: cancel `secondary`, primary `primary`; keep only one primary per dialog. |
| `panda_ledger/capture/capture_screen.py` | 287-344 | load/discard/save/lock/unlock/amend/supersede/retire have object names but only lock is styled | Assign roles: load/save/amend/supersede secondary; lock primary; discard/retire destructive; unlock recovery. |
| `panda_ledger/capture/capture_screen.py` | 291 | `button_row.addStretch(1)` inside action cluster | Avoid stretch inside the actual button cluster. Split left utility action and right decision cluster into separate layouts or keep fixed gaps so buttons do not drift/compress. |
| `panda_ledger/capture/capture_screen.py` | 695-696 | `related_picker_add` lacks role | Assign `utility` or `secondary`; style centrally. |
| `panda_ledger/capture/bible_picker.py` | 60-61 | `bible_picker_add` lacks role | Assign `secondary` or `utility`; style centrally. |
| `panda_ledger/capture/qa_pair_widget.py` | 65-67, 119-120 | remove and add Q&A buttons lack roles | Assign remove `destructive`; add `secondary`. |
| `panda_ledger/capture/snippet_widget.py` | 139-140 | browse button lacks role | Assign `utility`; style centrally. |
| `panda_ledger/verify/checklist_widget.py` | 281-287 | PASS/FAIL/SKIP result buttons have only `result` property and local QSS | Add objectName or `role="result"` plus `result` property. Central QSS maps pass to `ok`, fail to `err`, skip to `warn`. |
| `panda_ledger/verify/mockup_viewer.py` | 296-316 | mode, zoom, refresh buttons lack roles | Mode/zoom: `utility` with checked state; refresh: `secondary` or `utility`. |
| `panda_ledger/verify/verify_screen.py` | 267-283 | load/connect/sign-off lack objectName roles; sign-off uses `primary=True` | Set object names and roles. Sign off is the one `primary`; load/connect are secondary or utility. |

## Notification and Badge Shape Cleanup

This is not a separate lint category in the dispatch format, but it is required by the audit rows for status banner and warning badge.

| File | Line(s) | Current code | Fix |
|---|---:|---|---|
| `panda_ledger/capture/capture_screen.py` | 279-283, 621-628 | `QLabel#capture_status_banner` only receives color by level | Convert to central semantic notification selector with border/background/radius/padding; retain level property. Add WA if it paints a background. |
| `panda_ledger/browse/decision_detail.py` | 58-60, 105-108 | `decision_detail_warning_badge` is color/italic only | Style as a semantic warning badge/pill centrally: warn text/border/soft fill, radius-sm or pill depending final visual. |

## Implementation Order

1. Update `styles.py` with tokens, button role taxonomy, notification/badge selectors, and moved selectors from local QSS islands.
2. Remove local token mirrors and local QSS strings from `_capture_widgets.py`, `_dark_dialogs.py`, Capture staging picker, Verify checklist, Mockup viewer, and Verify screen.
3. Assign object names and `role` properties to buttons and styled surfaces.
4. Replace QGroupBox sections in `decision_detail.py`.
5. Add R03b waiver to `snippet_widget.py`; document existing Verify waiver.
6. Implement `_compute_min_size()` / `_compute_default_size()` and geometry persistence in `LedgerWindow` and `DarkDialogBase`; remove hardcoded dialog resize.
7. Run the lint command above. Expected target: no R17 errors, no R02 errors, no unwaived R03b surprises, and no R25/R16 findings on the targeted resizable surfaces. Any remaining warnings must be explicit, narrow waivers with reasons.

## Acceptance Checklist

- `reference_panel.py` remains untouched and skipped by `pg-lint:disable-file`.
- No `setStyleSheet(...)` remains in constructors for the listed files, except if a narrow documented lint exception is approved.
- No raw off-palette hex remains in widget files.
- No raw `#e8a87c`, `#7fb069`, or other mode-zone hex remains in widget files.
- Button roles are visible in source via objectName/property assignments, not inferred from labels.
- `snippet_widget.py` has a narrow R03b waiver or a dark replacement picker; recommendation is waiver.
- `verify_screen.py` R03b is documented as acknowledged exception with waiver already in place.
- `LedgerWindow` and dark dialogs derive minimum/default sizes and persist geometry.
- The post-fix lint run is attached to CC's completion report.
