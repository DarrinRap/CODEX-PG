# DESIGN_AUDIT_v1 - Codex pass

**Date:** 2026-04-26
**Author:** Codex
**Scope:** PG Bible Section 1.4, Section 1.5, Section 13 compliance - every user-visible surface in PG codebase
**Reference:** `PG_DESIGN_BIBLE_v1.md` Section 1.4, Section 1.5, Section 13.1 through Section 13.8

## Summary

Codex audited the live PG Python UI surfaces named in Claude's dispatch, plus the reusable dialogs and major panels reachable through the main app shell. The pass uses the earlier `RESIZE_AUDIT_v1.md` as the Section 13 baseline, then adds Section 1.4 and Section 1.5 checks for every user-visible surface: main shell, Library, Edit panels, Arrange/template surfaces, Comparison, Instruction Pane, Settings, Audit Module, region capture, patient panel, and reusable modal dialogs.

No production resizable top-level surface is fully Section 13 compliant today. The systemic gap is still architectural: no production surface has a `_compute_min_size()` / `_compute_default_size()` pair, most defaults are hardcoded, and geometry persistence is present only in the instruction-pane family. The app-level `View -> Reset Layout` action resets dock widgets only, not persisted window geometry, so it fails Section 13.4 as the app-wide reset path.

Section 1.4/1.5 findings are more localized. The highest-confidence design violation is AM Screen A: the right-pane header repeats teaching already present in the left status pane and workflow stepper, while Severity/State/Files columns waste horizontal table width and force title truncation. Other recurring patterns are oversized or under-derived fixed panels, simple modal dialogs with hardcoded minimum widths, and empty states or banners that mix useful next actions with descriptive prose.

Headline fix clusters: add shared Section 13 window sizing helpers; replace the app reset action with a true reset-window-layout path; fix AM Screen A header/columns as a coherent v4.42.3 design ship; then batch templates, reusable dialogs, and main-shell panel floors.

Legend: `PASS`, `FAIL`, `N/A`, `UNKNOWN`. Summary tables use `P`, `F`, `N`, `?`.

## App-level findings

1. **No shared Section 13 sizing implementation exists.**
   Evidence: the prior resize audit found no `_compute_min_size`, `compute_min_size`, `_compute_default_size`, or `compute_default_size` implementation in production Python. Bible Section 13.5 requires runtime derivation.

2. **`View -> Reset Layout` is not the Section 13.4 reset.**
   Evidence: `panda_gallery.py:889-891` creates `Reset &Layout`; `panda_gallery.py:1089-1092` only sets docks non-floating and visible. It does not remove geometry keys for InstructionPane, TestingSettingsDialog, AuditModuleWindow, templates, or MainWindow.

3. **Geometry persistence is incomplete.**
   Evidence: `instruction_pane.py:2497` restores InstructionPane geometry, `instruction_pane.py:2521` saves it, `instruction_pane.py:2595` restores TestingSettingsDialog geometry, and `instruction_pane.py:3039/3054/3089` save it. Other production top-level windows have no matching save/restore.

4. **No audited restore path has a multi-monitor sanity check.**
   Evidence: InstructionPane and TestingSettingsDialog call `restoreGeometry(saved)` directly at `instruction_pane.py:2497` and `2595`; no screen-intersection guard is visible.

5. **Section 1.5 ownership boundaries are emerging but not yet enforced.**
   Evidence: AM Screen A has left-pane status, workflow stepper, and bottom statusbar, but also repeats the same teaching in the right header (`audit_module_window.py:801-807`) and mirrors summary/statusbar data (`1326-1341`).

## Per-surface findings

### `MainWindow` (`panda_gallery.py`)

- **File:** `panda_gallery.py`
- **Class:** `MainWindow(QMainWindow)`
- **Window type:** main app window, resizable

#### Section 13 checks

| Check | Status | Evidence |
|---|---|---|
| 13.1 compute_min_size derivation | FAIL | `panda_gallery.py:145` hardcodes `setMinimumSize(1024, 680)`; no compute method. |
| 13.2 Buttons visible at min | UNKNOWN | Top/dock chrome has many clusters; no floor derivation proves fit at 1024x680. |
| 13.3 Inter-button spacing fixed 10px | FAIL | Example clusters use 6px at `panda_gallery.py:262` and `480`; no narrow variant is documented. |
| 13.4 Text never clipped | PASS | No elide call found in main shell scan. |
| 13.5 Multiline inputs >= 2 lines | N/A | MainWindow owns no top-level multiline input; children audited separately. |
| 13.6 Default size content-driven | FAIL | Startup calls `window.showMaximized()` at `panda_gallery.py:2904`. |
| 13.7 Geometry persistence | FAIL | No MainWindow save/restore geometry path found. |
| 13.8 Reset path | FAIL | `Reset &Layout` resets docks only at `panda_gallery.py:1089-1092`. |

#### Section 1.4 checks

| Check | Status | Evidence |
|---|---|---|
| 1.4.A No oversized fixed columns | N/A | Main shell has no table columns. |
| 1.4.B No decorative margins | UNKNOWN | Several panel margins are token-like; no full visual fit assertion. |
| 1.4.C No range-based dimensions | FAIL | Hardcoded min/default shell dimensions at `145` and maximized startup at `2904`. |
| 1.4.D No wrapper widgets where one suffices | UNKNOWN | Dock/title wrappers are extensive; needs visual refactor pass. |

#### Section 1.5 checks

| Check | Status | Evidence |
|---|---|---|
| 1.5.A No redundant teaching | UNKNOWN | Main shell delegates teaching to child panels. |
| 1.5.B No descriptive prose where operational data belongs | PASS | Main shell statusbar appears operational, not descriptive. |
| 1.5.C No filler | UNKNOWN | Dock title strips may be chrome filler, but not audited visually. |
| 1.5.D No status-bar duplication | UNKNOWN | Child surfaces repeat status in places; see AM Screen A. |
| 1.5.E Component sub-elements justified | UNKNOWN | Shell predates Bible component inventory. |

**Severity:** High.

**Fix recommendation:** Add shared geometry helper and true `View -> Reset window layout`; then compute shell floor from active child surface and dock chrome.

### `LibraryView` (`library_view.py`)

- **File:** `library_view.py`
- **Class:** `LibraryView(QWidget)`
- **Window type:** main child surface inside MainWindow

#### Section 13 checks

| Check | Status | Evidence |
|---|---|---|
| 13.1 compute_min_size derivation | N/A | Child view; MainWindow owns top-level floor. |
| 13.2 Buttons visible at min | UNKNOWN | Filter/action row has icon buttons at `library_view.py:483-498`; parent floor absent. |
| 13.3 Inter-button spacing fixed 10px | N/A | Child surface; relevant to parent floor only. |
| 13.4 Text never clipped | UNKNOWN | Empty-state labels wrap partly; thumbnails/tooltips carry long filenames. |
| 13.5 Multiline inputs >= 2 lines | N/A | No multiline input. |
| 13.6 Default size content-driven | N/A | Child view. |
| 13.7 Geometry persistence | N/A | Child view. |
| 13.8 Reset path | N/A | Child view. |

#### Section 1.4 checks

| Check | Status | Evidence |
|---|---|---|
| 1.4.A No oversized fixed columns | N/A | Grid cards, no table columns. |
| 1.4.B No decorative margins | PASS | Toolbar/grid margins are compact: `456-457`, `537-538`, `583-584`. |
| 1.4.C No range-based dimensions | UNKNOWN | Thumbnail size persists and clamps 80-300 at `587-589`; useful but should be documented. |
| 1.4.D No wrapper widgets where one suffices | PASS | Scroll/grid/empty-state wrappers carry distinct states. |

#### Section 1.5 checks

| Check | Status | Evidence |
|---|---|---|
| 1.5.A No redundant teaching | PASS | Import prompt and empty states teach distinct next actions. |
| 1.5.B No descriptive prose where operational data belongs | FAIL | Empty state `No images yet / Click + Import to add images` at `543-544` is useful but not Bible Section 8 styled; second line may be redundant with import icon/tooltip. |
| 1.5.C No filler | PASS | Hidden prompt card only appears after import (`520-524`, `1142-1146`). |
| 1.5.D No status-bar duplication | PASS | No evidence of statusbar duplication. |
| 1.5.E Component sub-elements justified | UNKNOWN | Import banner card needs Bible Section 8/6 mapping. |

**Severity:** Medium.

**Fix recommendation:** Rework Library empty states to canonical Section 8 wording once the module overhaul begins.

### `PatientListPanel` (`patient_panel.py`)

- **File:** `patient_panel.py`
- **Class:** `PatientListPanel(QWidget)`
- **Window type:** main-shell left panel

#### Section 13 checks

| Check | Status | Evidence |
|---|---|---|
| 13.1 compute_min_size derivation | N/A | Child dock panel. |
| 13.2 Buttons visible at min | UNKNOWN | Add/import action row uses 4px spacing at `423`; parent floor absent. |
| 13.3 Inter-button spacing fixed 10px | N/A | Child panel, but cluster should inform MainWindow floor. |
| 13.4 Text never clipped | UNKNOWN | Patient names/metadata may clip in 240px rail. |
| 13.5 Multiline inputs >= 2 lines | N/A | No multiline input. |
| 13.6 Default size content-driven | N/A | Child panel. |
| 13.7 Geometry persistence | N/A | Child panel/dock. |
| 13.8 Reset path | N/A | Child panel/dock. |

#### Section 1.4 checks

| Check | Status | Evidence |
|---|---|---|
| 1.4.A No oversized fixed columns | N/A | No table. |
| 1.4.B No decorative margins | PASS | Header/detail margins are compact: `403-404`, `468-469`. |
| 1.4.C No range-based dimensions | UNKNOWN | `setMinimumWidth(240)` at `392` needs parent floor documentation. |
| 1.4.D No wrapper widgets where one suffices | PASS | Header, card list, detail card carry distinct roles. |

#### Section 1.5 checks

| Check | Status | Evidence |
|---|---|---|
| 1.5.A No redundant teaching | PASS | Patient panel is mostly operational list/search. |
| 1.5.B No descriptive prose where operational data belongs | PASS | Headers are section labels. |
| 1.5.C No filler | UNKNOWN | Patient info card empty states need visual pass. |
| 1.5.D No status-bar duplication | PASS | No statusbar duplication found. |
| 1.5.E Component sub-elements justified | PASS | Patient card elements are data-bearing. |

**Severity:** Medium.

**Fix recommendation:** Include patient rail in MainWindow computed minimum and add long-name fit checks.

### `PatientFormDialog` (`patient_panel.py`)

- **File:** `patient_panel.py`
- **Class:** `PatientFormDialog(QDialog)`
- **Window type:** fixed patient create/edit modal

#### Section 13 checks

| Check | Status | Evidence |
|---|---|---|
| 13.1 compute_min_size derivation | N/A | Fixed modal via `setFixedSize(440, 520)` at `212`. |
| 13.2 Buttons visible at min | UNKNOWN | Button row relies on defaults at `321-335`; no fit assertion. |
| 13.3 Inter-button spacing fixed 10px | UNKNOWN | No explicit button-row `setSpacing(10)`. |
| 13.4 Text never clipped | UNKNOWN | Fixed form size; no longest-label fit assertion. |
| 13.5 Multiline inputs >= 2 lines | UNKNOWN | Notes uses `QTextEdit` at `312` with `setMaximumHeight(60)` at `313`; no derived two-line floor. |
| 13.6 Default size content-driven | N/A | Fixed modal. |
| 13.7 Geometry persistence | N/A | Fixed modal; persistence not expected. |
| 13.8 Reset path | N/A | Fixed modal. |

#### Section 1.4 checks

| Check | Status | Evidence |
|---|---|---|
| 1.4.A No oversized fixed columns | N/A | Form layout, no table. |
| 1.4.B No decorative margins | PASS | Form margins `225-226` are normal dialog spacing. |
| 1.4.C No range-based dimensions | FAIL | Fixed 440x520 and notes 60px max are not derived. |
| 1.4.D No wrapper widgets where one suffices | PASS | Form structure is direct. |

#### Section 1.5 checks

| Check | Status | Evidence |
|---|---|---|
| 1.5.A No redundant teaching | PASS | Dialog is data entry, not instructional. |
| 1.5.B No descriptive prose where operational data belongs | PASS | Header is mode title. |
| 1.5.C No filler | PASS | Fields and actions have clear purpose. |
| 1.5.D No status-bar duplication | N/A | Modal has no statusbar. |
| 1.5.E Component sub-elements justified | PASS | Fields map to patient data. |

**Severity:** Low.

**Fix recommendation:** Either document as fixed/content-sized with fit tests, or convert to computed modal sizing.

### `AdjustmentsPanel` (`panels.py`)

- **File:** `panels.py`
- **Class:** `AdjustmentsPanel(QWidget)`
- **Window type:** Edit right-panel tab

#### Section 13 checks

| Check | Status | Evidence |
|---|---|---|
| 13.1 compute_min_size derivation | N/A | Child panel inside MainWindow. |
| 13.2 Buttons visible at min | UNKNOWN | Reset/crop rows use 6px spacing at `457-482`; parent floor absent. |
| 13.3 Inter-button spacing fixed 10px | N/A | Child cluster; should inform parent floor if active. |
| 13.4 Text never clipped | UNKNOWN | Fixed-width row labels at `365-391` need narrow fit check. |
| 13.5 Multiline inputs >= 2 lines | N/A | No multiline input. |
| 13.6 Default size content-driven | N/A | Child panel. |
| 13.7 Geometry persistence | N/A | Child panel. |
| 13.8 Reset path | N/A | Child panel. |

#### Section 1.4 checks

| Check | Status | Evidence |
|---|---|---|
| 1.4.A No oversized fixed columns | N/A | No table. |
| 1.4.B No decorative margins | PASS | Comments explicitly justify uniform 8px spacing at `256-264`. |
| 1.4.C No range-based dimensions | PASS | No range dimensions found in panel body. |
| 1.4.D No wrapper widgets where one suffices | PASS | Sections separate adjustment groups. |

#### Section 1.5 checks

| Check | Status | Evidence |
|---|---|---|
| 1.5.A No redundant teaching | PASS | Controls are operational. |
| 1.5.B No descriptive prose where operational data belongs | PASS | Section labels separate tool groups. |
| 1.5.C No filler | PASS | Radiograph/photo adaptive sections are conditional and meaningful. |
| 1.5.D No status-bar duplication | PASS | No statusbar duplication. |
| 1.5.E Component sub-elements justified | PASS | Sliders/buttons map to edit operations. |

**Severity:** Low.

**Fix recommendation:** Include active right-panel width in MainWindow floor smoke; otherwise no major Section 1.4/1.5 issue.

### `DrawingPanel` (`panels.py`)

- **File:** `panels.py`
- **Class:** `DrawingPanel(QWidget)`
- **Window type:** Edit right-panel tab

#### Section 13 checks

| Check | Status | Evidence |
|---|---|---|
| 13.1 compute_min_size derivation | N/A | Child panel. |
| 13.2 Buttons visible at min | UNKNOWN | Many fixed icon buttons: `1128`, `1237-1252`, `1373`; parent floor absent. |
| 13.3 Inter-button spacing fixed 10px | N/A | Child cluster; compact swatches intentionally use 2-3px. |
| 13.4 Text never clipped | UNKNOWN | Fixed label widths like `Opacity`/`Size` at `1153-1170` need fit check. |
| 13.5 Multiline inputs >= 2 lines | N/A | No multiline text input identified. |
| 13.6 Default size content-driven | N/A | Child panel. |
| 13.7 Geometry persistence | N/A | Child panel. |
| 13.8 Reset path | N/A | Child panel. |

#### Section 1.4 checks

| Check | Status | Evidence |
|---|---|---|
| 1.4.A No oversized fixed columns | N/A | No table. |
| 1.4.B No decorative margins | PASS | Dense tool panel uses small purposeful spacing: `1067-1070`, `1107-1116`. |
| 1.4.C No range-based dimensions | UNKNOWN | Many fixed tool sizes are intentional but lack Bible mapping. |
| 1.4.D No wrapper widgets where one suffices | PASS | Groups are operational tool clusters. |

#### Section 1.5 checks

| Check | Status | Evidence |
|---|---|---|
| 1.5.A No redundant teaching | PASS | Tool controls are operational. |
| 1.5.B No descriptive prose where operational data belongs | PASS | Labels are control labels. |
| 1.5.C No filler | PASS | No decorative-only items seen. |
| 1.5.D No status-bar duplication | PASS | No statusbar duplication. |
| 1.5.E Component sub-elements justified | PASS | Color, brush, text, selection controls all map to edit tools. |

**Severity:** Low.

**Fix recommendation:** Later Bible mapping for dense tool-strip control sizes; not a priority violation.

### `LayersPanel` (`panels.py`)

- **File:** `panels.py`
- **Class:** `LayersPanel(QWidget)`
- **Window type:** Edit right-panel tab

#### Section 13 checks

| Check | Status | Evidence |
|---|---|---|
| 13.1 compute_min_size derivation | N/A | Child panel. |
| 13.2 Buttons visible at min | UNKNOWN | Move/delete rows use fixed 32x28 buttons and 4px spacing at `1757-1767`; parent floor absent. |
| 13.3 Inter-button spacing fixed 10px | N/A | Child compact icon cluster. |
| 13.4 Text never clipped | UNKNOWN | Layer names may clip; no fit/wrap evidence. |
| 13.5 Multiline inputs >= 2 lines | N/A | No multiline input. |
| 13.6 Default size content-driven | N/A | Child panel. |
| 13.7 Geometry persistence | N/A | Child panel. |
| 13.8 Reset path | N/A | Child panel. |

#### Section 1.4 checks

| Check | Status | Evidence |
|---|---|---|
| 1.4.A No oversized fixed columns | N/A | No table. |
| 1.4.B No decorative margins | PASS | Panel margins follow Edit pattern: `1724-1725`. |
| 1.4.C No range-based dimensions | UNKNOWN | Fixed icon dimensions lack explicit Bible mapping. |
| 1.4.D No wrapper widgets where one suffices | PASS | Scroll/list/button rows are needed. |

#### Section 1.5 checks

| Check | Status | Evidence |
|---|---|---|
| 1.5.A No redundant teaching | PASS | Operational layer management only. |
| 1.5.B No descriptive prose where operational data belongs | PASS | Section headers and controls are direct. |
| 1.5.C No filler | PASS | No obvious filler. |
| 1.5.D No status-bar duplication | PASS | No statusbar duplication. |
| 1.5.E Component sub-elements justified | PASS | Eye/name/order controls have direct purpose. |

**Severity:** Low.

**Fix recommendation:** Add long-layer-name smoke in Edit panel floor tests.

### `FilmstripWidget` and `TemplateViewContainer` (`filmstrip.py`)

- **File:** `filmstrip.py`
- **Class:** `FilmstripWidget(QWidget)`, `TemplateViewContainer(QWidget)`
- **Window type:** bottom filmstrip and template/filmstrip child surface

#### Section 13 checks

| Check | Status | Evidence |
|---|---|---|
| 13.1 compute_min_size derivation | N/A | Child surfaces. |
| 13.2 Buttons visible at min | N/A | Filmstrip is primarily scrollable thumbs. |
| 13.3 Inter-button spacing fixed 10px | N/A | No button cluster. |
| 13.4 Text never clipped | UNKNOWN | Thumb filenames are tooltip-backed; visible label fit not audited. |
| 13.5 Multiline inputs >= 2 lines | N/A | No input. |
| 13.6 Default size content-driven | N/A | Child surface. |
| 13.7 Geometry persistence | N/A | Child surface; splitter state not audited. |
| 13.8 Reset path | N/A | Child surface. |

#### Section 1.4 checks

| Check | Status | Evidence |
|---|---|---|
| 1.4.A No oversized fixed columns | N/A | No table. |
| 1.4.B No decorative margins | PASS | Tight layout: outer `252-253`, thumb row `296-299`, container `450-451`. |
| 1.4.C No range-based dimensions | UNKNOWN | Thumbnail fixed sizes are data-display decisions, not documented here. |
| 1.4.D No wrapper widgets where one suffices | PASS | Splitter/scroll/thumb wrappers have roles. |

#### Section 1.5 checks

| Check | Status | Evidence |
|---|---|---|
| 1.5.A No redundant teaching | PASS | No teaching text. |
| 1.5.B No descriptive prose where operational data belongs | PASS | `IMAGES` section label is structural. |
| 1.5.C No filler | PASS | Dotted splitter/filmstrip are functional. |
| 1.5.D No status-bar duplication | PASS | No statusbar duplication. |
| 1.5.E Component sub-elements justified | PASS | Thumbnails, badges, scroll strip are operational. |

**Severity:** Low.

**Fix recommendation:** Verify visible filename behavior during MainWindow floor smoke.

### `ComparisonView` (`comparison_view.py`)

- **File:** `comparison_view.py`
- **Class:** `ComparisonView(QWidget)`
- **Window type:** comparison child surface inside MainWindow

#### Section 13 checks

| Check | Status | Evidence |
|---|---|---|
| 13.1 compute_min_size derivation | N/A | Child view. |
| 13.2 Buttons visible at min | UNKNOWN | Top bar has six buttons from `240-270`; no parent floor proof. |
| 13.3 Inter-button spacing fixed 10px | FAIL | Top bar uses `tb_layout.setSpacing(8)` at `231`; Section 13 wants 10px unless narrow variant. |
| 13.4 Text never clipped | UNKNOWN | `Save as Series` and title may clip in narrow shell. |
| 13.5 Multiline inputs >= 2 lines | N/A | No multiline input. |
| 13.6 Default size content-driven | N/A | Child view. |
| 13.7 Geometry persistence | N/A | Child view. |
| 13.8 Reset path | N/A | Child view. |

#### Section 1.4 checks

| Check | Status | Evidence |
|---|---|---|
| 1.4.A No oversized fixed columns | N/A | No table. |
| 1.4.B No decorative margins | PASS | Top bar/grid margins are compact: `230-231`, `278-279`. |
| 1.4.C No range-based dimensions | PASS | Grid dimensions derive from image count at `318-333`. |
| 1.4.D No wrapper widgets where one suffices | PASS | Top bar and grid container are distinct. |

#### Section 1.5 checks

| Check | Status | Evidence |
|---|---|---|
| 1.5.A No redundant teaching | PASS | Toolbar actions are operational. |
| 1.5.B No descriptive prose where operational data belongs | PASS | `Comparison Mode` title orients the surface. |
| 1.5.C No filler | PASS | No decorative-only elements found. |
| 1.5.D No status-bar duplication | PASS | No statusbar duplication. |
| 1.5.E Component sub-elements justified | PASS | Add/Fit/Export/Print/Save/Close actions are justified. |

**Severity:** Medium.

**Fix recommendation:** Add top-bar button cluster to MainWindow active-surface floor; consider icon+tooltip for some actions if width is tight.

### `InstructionPane` (`instruction_pane.py`)

- **File:** `instruction_pane.py`
- **Class:** `InstructionPane(QDialog)`
- **Window type:** floating testing pane, resizable

#### Section 13 checks

| Check | Status | Evidence |
|---|---|---|
| 13.1 compute_min_size derivation | FAIL | `DEFAULT_SIZE`/`MIN_SIZE` hardcoded at `69-70`; applied at `802-803`. |
| 13.2 Buttons visible at min | PASS | Main nav/action rows use 10px spacing and two-row reflow; `1110`, `1121`, `1159-1161`. |
| 13.3 Inter-button spacing fixed 10px | PASS | `nav_lay.setSpacing(10)` at `1110`; `act_lay.setSpacing(10)` at `1121`. |
| 13.4 Text never clipped | PASS | Labels use word wrap: `876`, `881`, `897`, `930`, `956`. |
| 13.5 Multiline inputs >= 2 lines | FAIL | `_FailNoteEdit` hardcodes `setMinimumHeight(60)` at `168`. |
| 13.6 Default size content-driven | FAIL | `resize(*DEFAULT_SIZE)` at `803`; fallback position uses `DEFAULT_SIZE[0]` at `1321`. |
| 13.7 Geometry persistence | FAIL | Restores/saves at `2497` and `2521`, but no multi-monitor sanity check. |
| 13.8 Reset path | FAIL | Local reset removes pane geometry at `3016`; app-level reset missing. |

#### Section 1.4 checks

| Check | Status | Evidence |
|---|---|---|
| 1.4.A No oversized fixed columns | N/A | No table. |
| 1.4.B No decorative margins | PASS | Root/top/action spacing is compact and purposeful. |
| 1.4.C No range-based dimensions | FAIL | `MIN_SIZE`, `DEFAULT_SIZE`, and textarea 60/84px are not runtime-derived. |
| 1.4.D No wrapper widgets where one suffices | PASS | Step rows, expected/action/fail panels carry state. |

#### Section 1.5 checks

| Check | Status | Evidence |
|---|---|---|
| 1.5.A No redundant teaching | PASS | Pane is the teaching surface by product design. |
| 1.5.B No descriptive prose where operational data belongs | PASS | Expected/action/fail blocks are task-specific. |
| 1.5.C No filler | PASS | Conditional panels appear only when active. |
| 1.5.D No status-bar duplication | PASS | Standalone pane; no duplicated app statusbar. |
| 1.5.E Component sub-elements justified | PASS | Step content, action buttons, fail note each have defined purpose. |

**Severity:** High.

**Fix recommendation:** Make InstructionPane the Section 13 reference implementation; promote existing button math into `_compute_min_size()` and derive fail-note height from font metrics.

### `TestingSettingsDialog` (`instruction_pane.py`)

- **File:** `instruction_pane.py`
- **Class:** `TestingSettingsDialog(QDialog)`
- **Window type:** testing settings dialog, resizable

#### Section 13 checks

| Check | Status | Evidence |
|---|---|---|
| 13.1 compute_min_size derivation | FAIL | No compute method; #129 cites settings sizing as originating bug. |
| 13.2 Buttons visible at min | UNKNOWN | Controls and tabs fit visually, but no computed floor. |
| 13.3 Inter-button spacing fixed 10px | UNKNOWN | Layouts use 10/12px (`2622`, `2690`) but no full cluster derivation. |
| 13.4 Text never clipped | PASS | Warning/empty labels wrap at `2698`, `2733`, `2748`, `2762`. |
| 13.5 Multiline inputs >= 2 lines | N/A | No multiline input. |
| 13.6 Default size content-driven | UNKNOWN | No visible hardcoded resize, but no `_compute_default_size()`. |
| 13.7 Geometry persistence | FAIL | Restores at `2595`; saves at `3039`, `3054`, `3089`; no off-screen guard. |
| 13.8 Reset path | FAIL | Reset button clears pane geometry at `3016`, not the dialog key `testingSettingsDialog/geometry`. |

#### Section 1.4 checks

| Check | Status | Evidence |
|---|---|---|
| 1.4.A No oversized fixed columns | N/A | No table. |
| 1.4.B No decorative margins | PASS | Tab layouts are compact. |
| 1.4.C No range-based dimensions | UNKNOWN | No hardcoded resize hit, but no computed floor. |
| 1.4.D No wrapper widgets where one suffices | PASS | Pane/session tabs split distinct concerns. |

#### Section 1.5 checks

| Check | Status | Evidence |
|---|---|---|
| 1.5.A No redundant teaching | PASS | Settings copy is operational. |
| 1.5.B No descriptive prose where operational data belongs | PASS | Warnings/empty device messages are state-based. |
| 1.5.C No filler | PASS | Device/test controls have clear purpose. |
| 1.5.D No status-bar duplication | PASS | No statusbar duplication. |
| 1.5.E Component sub-elements justified | PASS | Remember/reset/device/test controls all map to settings. |

**Severity:** High.

**Fix recommendation:** Add `_compute_min_size()`, `_compute_default_size()`, and off-screen restore guard; fix reset to include the dialog geometry key.

### `AuditModuleWindow` (`audit_module/audit_module_window.py`)

- **File:** `audit_module/audit_module_window.py`
- **Class:** `AuditModuleWindow(QMainWindow)`
- **Window type:** Audit Module top-level window, resizable

#### Section 13 checks

| Check | Status | Evidence |
|---|---|---|
| 13.1 compute_min_size derivation | FAIL | Hardcoded `resize(800, 560)` at `2770`; `setMinimumSize(800, 500)` at `2774`. |
| 13.2 Buttons visible at min | UNKNOWN | Screen A/B/Archive clusters are not proven by floor derivation. |
| 13.3 Inter-button spacing fixed 10px | FAIL | Some clusters are 10px, but AM also uses 6px/4px clusters (`1689`, `1894`). |
| 13.4 Text never clipped | FAIL | Screen A title column visibly truncates; title item set at `1397-1406` without wrap strategy. |
| 13.5 Multiline inputs >= 2 lines | N/A | AM text areas are read-only displays in audited path. |
| 13.6 Default size content-driven | FAIL | Hardcoded default at `2770`; #138 acknowledges this as a temporary fix. |
| 13.7 Geometry persistence | FAIL | No AM save/restore; comment near `2768-2769` defers it. |
| 13.8 Reset path | FAIL | No AM reset geometry path; app reset does not clear AM geometry. |

#### Section 1.4 checks

| Check | Status | Evidence |
|---|---|---|
| 1.4.A No oversized fixed columns | FAIL | Screen A metadata columns are fixed 140/180 at `917-918`, wasting width for small badges. |
| 1.4.B No decorative margins | PASS | AM layouts are generally compact; issue is column/header allocation. |
| 1.4.C No range-based dimensions | FAIL | 800x560/800x500 are hardcoded temporary sizes. |
| 1.4.D No wrapper widgets where one suffices | UNKNOWN | Screen B layout is being redesigned; no final call here. |

#### Section 1.5 checks

| Check | Status | Evidence |
|---|---|---|
| 1.5.A No redundant teaching | FAIL | Header hint at `807` repeats workflow stepper at `989-995`. |
| 1.5.B No descriptive prose where operational data belongs | FAIL | Subtitle at `801` describes screen identity rather than operational status. |
| 1.5.C No filler | FAIL | Header second/third lines add visual mass with no net new information. |
| 1.5.D No status-bar duplication | FAIL | StatusPane/statusbar mirror summary and source at `1303-1341`; needs ownership cleanup. |
| 1.5.E Component sub-elements justified | FAIL | Screen A header sub-elements fail the per-subfeature test from Section 1.5. |

**Severity:** High.

**Fix recommendation:** Fold Section 13 sizing/persistence into AM v2; ship Screen A A1/B1/D2 design from the companion Job 1 report.

### `_BugListScreen` / AM Screen A (`audit_module/audit_module_window.py`)

- **File:** `audit_module/audit_module_window.py`
- **Class:** `_BugListScreen(QWidget)`
- **Window type:** AM Screen A child screen

#### Section 13 checks

| Check | Status | Evidence |
|---|---|---|
| 13.1 compute_min_size derivation | N/A | Child screen; top-level AM owns floor. |
| 13.2 Buttons visible at min | UNKNOWN | Filter row and refresh button need AM floor test. |
| 13.3 Inter-button spacing fixed 10px | UNKNOWN | Filter/header rows use 6px/12px; no formal floor. |
| 13.4 Text never clipped | FAIL | Title item set at `1397-1406`; table title truncates in live build. |
| 13.5 Multiline inputs >= 2 lines | N/A | No multiline input. |
| 13.6 Default size content-driven | N/A | Child screen. |
| 13.7 Geometry persistence | N/A | Child screen. |
| 13.8 Reset path | N/A | Child screen. |

#### Section 1.4 checks

| Check | Status | Evidence |
|---|---|---|
| 1.4.A No oversized fixed columns | FAIL | `Severity` 140 and `State` 180 at `917-918`; `Files` ResizeToContents at `916` can still reserve more than content. |
| 1.4.B No decorative margins | PASS | Pane layout uses compact margins: `772-793`, `960-1006`. |
| 1.4.C No range-based dimensions | FAIL | Column widths are magic safety numbers, not content-derived. |
| 1.4.D No wrapper widgets where one suffices | PASS | Summary/list/statusbar regions are distinct. |

#### Section 1.5 checks

| Check | Status | Evidence |
|---|---|---|
| 1.5.A No redundant teaching | FAIL | `Click a row...` at `807` repeats workflow stepper at `989-995`. |
| 1.5.B No descriptive prose where operational data belongs | FAIL | `Personal bug tracker - BUGS.md OPEN section` at `801`. |
| 1.5.C No filler | FAIL | Header lines add height with no non-redundant status. |
| 1.5.D No status-bar duplication | FAIL | Summary/statusbar ownership overlap at `1303-1341`. |
| 1.5.E Component sub-elements justified | FAIL | Header title earns presence; subtitle/hint do not. |

**Severity:** High.

**Fix recommendation:** A1 header, fixed compact metadata columns, wrapped Title, D2 StatusPane wording.

### `_BugDetailScreen` / AM Screen B (`audit_module/audit_module_window.py`)

- **File:** `audit_module/audit_module_window.py`
- **Class:** `_BugDetailScreen(QWidget)`
- **Window type:** AM Screen B child screen

#### Section 13 checks

| Check | Status | Evidence |
|---|---|---|
| 13.1 compute_min_size derivation | N/A | Child screen. |
| 13.2 Buttons visible at min | UNKNOWN | Header/action/gap rows need AM floor test. |
| 13.3 Inter-button spacing fixed 10px | UNKNOWN | Header row uses 10px at `1744`; other rows use 4/6px. |
| 13.4 Text never clipped | UNKNOWN | Screen B is actively being redesigned; current long gap/details need visual smoke. |
| 13.5 Multiline inputs >= 2 lines | N/A | Read-only detail panes, not input floor. |
| 13.6 Default size content-driven | N/A | Child screen. |
| 13.7 Geometry persistence | N/A | Child screen. |
| 13.8 Reset path | N/A | Child screen. |

#### Section 1.4 checks

| Check | Status | Evidence |
|---|---|---|
| 1.4.A No oversized fixed columns | N/A | No table columns. |
| 1.4.B No decorative margins | UNKNOWN | Current Screen B has known UX redesign work; no final visual verdict. |
| 1.4.C No range-based dimensions | UNKNOWN | Active redesign may replace current numbers. |
| 1.4.D No wrapper widgets where one suffices | UNKNOWN | Existing three-column layout under review. |

#### Section 1.5 checks

| Check | Status | Evidence |
|---|---|---|
| 1.5.A No redundant teaching | UNKNOWN | StatusPane wording explains triage at `1797-1800`; needs post-redesign audit. |
| 1.5.B No descriptive prose where operational data belongs | PASS | StatusPane detail is an actionable state cue. |
| 1.5.C No filler | UNKNOWN | Current v0.1/v0.2 redesign still in motion. |
| 1.5.D No status-bar duplication | UNKNOWN | Screen B does not use same bottom statusbar pattern as A. |
| 1.5.E Component sub-elements justified | UNKNOWN | Re-audit after AM Screen B v2 implementation. |

**Severity:** Medium.

**Fix recommendation:** Re-audit after Claude's Screen B v2 synthesis is implemented.

### `_ArchiveScreen` (`audit_module/audit_module_window.py`)

- **File:** `audit_module/audit_module_window.py`
- **Class:** `_ArchiveScreen(QWidget)`
- **Window type:** AM archive child screen

#### Section 13 checks

| Check | Status | Evidence |
|---|---|---|
| 13.1 compute_min_size derivation | N/A | Child screen. |
| 13.2 Buttons visible at min | UNKNOWN | Archive controls need AM floor smoke. |
| 13.3 Inter-button spacing fixed 10px | UNKNOWN | Header row uses 10px at `2465`; other rows 4px. |
| 13.4 Text never clipped | UNKNOWN | Archive list/search not visually audited. |
| 13.5 Multiline inputs >= 2 lines | N/A | Read-only text displays. |
| 13.6 Default size content-driven | N/A | Child screen. |
| 13.7 Geometry persistence | N/A | Child screen. |
| 13.8 Reset path | N/A | Child screen. |

#### Section 1.4 checks

| Check | Status | Evidence |
|---|---|---|
| 1.4.A No oversized fixed columns | UNKNOWN | Archive list structure not deeply audited. |
| 1.4.B No decorative margins | PASS | Compact layout: `2460-2465`, `2522-2539`. |
| 1.4.C No range-based dimensions | UNKNOWN | Needs focused archive pass. |
| 1.4.D No wrapper widgets where one suffices | PASS | Left/right archive areas carry search/detail roles. |

#### Section 1.5 checks

| Check | Status | Evidence |
|---|---|---|
| 1.5.A No redundant teaching | PASS | No repeated workflow teaching found. |
| 1.5.B No descriptive prose where operational data belongs | PASS | Archive is read/search surface. |
| 1.5.C No filler | UNKNOWN | Status label at `2531` needs visual/context check. |
| 1.5.D No status-bar duplication | UNKNOWN | Uses status label; no bottom statusbar. |
| 1.5.E Component sub-elements justified | UNKNOWN | Re-audit with Archive design brief. |

**Severity:** Low.

**Fix recommendation:** Include Archive in AM top-level floor smoke; not a v4.42.3 blocker.

### `TemplateLibraryDialog` (`dialogs.py`)

- **File:** `dialogs.py`
- **Class:** `TemplateLibraryDialog(QWidget)`
- **Window type:** template browser window, resizable

#### Section 13 checks

| Check | Status | Evidence |
|---|---|---|
| 13.1 compute_min_size derivation | FAIL | `dialogs.py:771` hardcodes `setMinimumSize(600, 400)`. |
| 13.2 Buttons visible at min | UNKNOWN | Toolbar/bottom controls need floor derivation. |
| 13.3 Inter-button spacing fixed 10px | FAIL | Toolbar/grid/bottom use 8px at `785`, `841`, `853`. |
| 13.4 Text never clipped | UNKNOWN | Empty state wraps at `833`; card names need fit check. |
| 13.5 Multiline inputs >= 2 lines | N/A | No multiline input. |
| 13.6 Default size content-driven | FAIL | `dialogs.py:772` hardcodes `resize(800, 520)`. |
| 13.7 Geometry persistence | FAIL | Only card width persists; no window geometry save/restore. |
| 13.8 Reset path | FAIL | No per-window reset; app reset misses it. |

#### Section 1.4 checks

| Check | Status | Evidence |
|---|---|---|
| 1.4.A No oversized fixed columns | N/A | Card grid, no table. |
| 1.4.B No decorative margins | PASS | Toolbar/grid/bottom spacing compact. |
| 1.4.C No range-based dimensions | FAIL | Hardcoded 600x400 and 800x520. |
| 1.4.D No wrapper widgets where one suffices | PASS | Toolbar, scroll grid, bottom bar have clear roles. |

#### Section 1.5 checks

| Check | Status | Evidence |
|---|---|---|
| 1.5.A No redundant teaching | UNKNOWN | Empty-state wording not expanded in this pass. |
| 1.5.B No descriptive prose where operational data belongs | UNKNOWN | Template empty states need Bible Section 8 pass. |
| 1.5.C No filler | PASS | Browse/create/edit/select controls are functional. |
| 1.5.D No status-bar duplication | N/A | No statusbar. |
| 1.5.E Component sub-elements justified | PASS | Toolbar, grid, archive toggle, select/cancel actions have purpose. |

**Severity:** Medium.

**Fix recommendation:** Batch with TemplateEditorDialog for template module Section 13 pass.

### `TemplateEditorDialog` (`template_designer.py`)

- **File:** `template_designer.py`
- **Class:** `TemplateEditorDialog(QWidget)`
- **Window type:** template designer window, resizable

#### Section 13 checks

| Check | Status | Evidence |
|---|---|---|
| 13.1 compute_min_size derivation | FAIL | `template_designer.py:878` hardcodes `setMinimumSize(950, 700)`. |
| 13.2 Buttons visible at min | PASS | Bottom bar uses stretch and 10px spacing at `1067-1068`. |
| 13.3 Inter-button spacing fixed 10px | PASS | Bottom button cluster uses `bb.setSpacing(10)` at `1068`. |
| 13.4 Text never clipped | UNKNOWN | Right properties rail labels/fields need narrow smoke. |
| 13.5 Multiline inputs >= 2 lines | N/A | Single-line fields only. |
| 13.6 Default size content-driven | FAIL | Constructor calls `showMaximized()` at `881`. |
| 13.7 Geometry persistence | FAIL | No save/restore geometry path found. |
| 13.8 Reset path | FAIL | No per-window reset; app reset misses it. |

#### Section 1.4 checks

| Check | Status | Evidence |
|---|---|---|
| 1.4.A No oversized fixed columns | N/A | Canvas/palette/properties, no table. |
| 1.4.B No decorative margins | PASS | Content layout is dense: `890-912`, `948-1000`, `1067-1068`. |
| 1.4.C No range-based dimensions | FAIL | 950x700 floor and maximized default are not derived. |
| 1.4.D No wrapper widgets where one suffices | PASS | Palette/canvas/properties/bottom bar have separate roles. |

#### Section 1.5 checks

| Check | Status | Evidence |
|---|---|---|
| 1.5.A No redundant teaching | PASS | Surface is tool controls, not repeated instruction. |
| 1.5.B No descriptive prose where operational data belongs | PASS | Section labels are operational tool groups. |
| 1.5.C No filler | PASS | Controls are tied to template editing. |
| 1.5.D No status-bar duplication | N/A | No statusbar. |
| 1.5.E Component sub-elements justified | PASS | Palette, canvas, properties, save actions are justified. |

**Severity:** Medium.

**Fix recommendation:** Replace maximized startup with persisted geometry or content-driven default; derive floor from right rail + canvas + bottom bar.

### `RegionCaptureOverlay`, `RegionCaptureToast`, `RegionCaptureFlash` (`region_capture.py`)

- **File:** `region_capture.py`
- **Classes:** `RegionCaptureOverlay(QWidget)`, `RegionCaptureToast(QWidget)`, `RegionCaptureFlash(QWidget)`
- **Window type:** transient overlay/toast/flash surfaces

#### Section 13 checks

| Check | Status | Evidence |
|---|---|---|
| 13.1 compute_min_size derivation | N/A | Transient non-user-resizable surfaces. |
| 13.2 Buttons visible at min | N/A | No buttons in overlay/flash/toast. |
| 13.3 Inter-button spacing fixed 10px | N/A | No button cluster. |
| 13.4 Text never clipped | UNKNOWN | Toast constrains width 240-360 at `region_capture.py:297-298`; title/subtitle wrap not proven. |
| 13.5 Multiline inputs >= 2 lines | N/A | No input. |
| 13.6 Default size content-driven | N/A | Transient geometry/adjustSize driven. |
| 13.7 Geometry persistence | N/A | Persistence not expected. |
| 13.8 Reset path | N/A | Reset not expected. |

#### Section 1.4 checks

| Check | Status | Evidence |
|---|---|---|
| 1.4.A No oversized fixed columns | N/A | No table. |
| 1.4.B No decorative margins | PASS | Toast margins are compact: `283-284`. |
| 1.4.C No range-based dimensions | UNKNOWN | Toast width range is purposeful but should have fit assertion. |
| 1.4.D No wrapper widgets where one suffices | PASS | Overlay/toast/flash each carry separate feedback role. |

#### Section 1.5 checks

| Check | Status | Evidence |
|---|---|---|
| 1.5.A No redundant teaching | PASS | Capture feedback is state-specific. |
| 1.5.B No descriptive prose where operational data belongs | PASS | Toast communicates capture result. |
| 1.5.C No filler | PASS | Flash/toast are transient feedback, not decoration. |
| 1.5.D No status-bar duplication | PASS | No statusbar duplication. |
| 1.5.E Component sub-elements justified | PASS | Overlay/cutout/toast/flash each have direct function. |

**Severity:** Low.

**Fix recommendation:** Add explicit Section 13 exemption comment for transient overlay surfaces and fit-check toast text.

### `RegionReviewDialog` (`region_capture.py`)

- **File:** `region_capture.py`
- **Class:** `RegionReviewDialog(QDialog)`
- **Window type:** modal review dialog

#### Section 13 checks

| Check | Status | Evidence |
|---|---|---|
| 13.1 compute_min_size derivation | FAIL | Preview caps are constants; no `_compute_min_size()` method. |
| 13.2 Buttons visible at min | PASS | Button row uses stretch and fixed 10px spacing at `412-413`. |
| 13.3 Inter-button spacing fixed 10px | PASS | `btn_row.setSpacing(10)` explicitly cites #129 at `412`. |
| 13.4 Text never clipped | PASS | Metadata is simple; no elide found. |
| 13.5 Multiline inputs >= 2 lines | N/A | No input. |
| 13.6 Default size content-driven | PASS | Size follows scaled pixmap/layout; no hardcoded resize hit. |
| 13.7 Geometry persistence | FAIL | No save/restore geometry. |
| 13.8 Reset path | FAIL | No reset path; app reset misses it. |

#### Section 1.4 checks

| Check | Status | Evidence |
|---|---|---|
| 1.4.A No oversized fixed columns | N/A | No table. |
| 1.4.B No decorative margins | PASS | Dialog margins/spacing `365-366` are appropriate for image review. |
| 1.4.C No range-based dimensions | UNKNOWN | Preview cap constants should be folded into compute/default policy. |
| 1.4.D No wrapper widgets where one suffices | PASS | Preview, metadata, action row each has purpose. |

#### Section 1.5 checks

| Check | Status | Evidence |
|---|---|---|
| 1.5.A No redundant teaching | PASS | Save/discard/recapture actions are direct. |
| 1.5.B No descriptive prose where operational data belongs | PASS | Review dialog is operational confirmation. |
| 1.5.C No filler | PASS | No decorative-only element seen. |
| 1.5.D No status-bar duplication | N/A | Modal has no statusbar. |
| 1.5.E Component sub-elements justified | PASS | Preview, metadata, and buttons are justified. |

**Severity:** Medium.

**Fix recommendation:** Decide whether RegionReviewDialog should persist geometry; if yes, add full Section 13 helper path.

### Reusable dark modal dialogs (`dialogs.py`)

- **File:** `dialogs.py`
- **Classes:** `UnsavedChangesDialog`, `DarkConfirmDialog`, `DarkInputDialog`, `DarkItemDialog`, `DarkChoiceDialog`, `dark_message`
- **Window type:** reusable modal popovers

#### Section 13 checks

| Check | Status | Evidence |
|---|---|---|
| 13.1 compute_min_size derivation | FAIL | Hardcoded `setMinimumWidth` at `134`, `190`, `247`, `301`, `340`; fixed size at `58`. |
| 13.2 Buttons visible at min | UNKNOWN | Arbitrary labels/buttons not derived; `DarkChoiceDialog` accepts `buttons: list[str]`. |
| 13.3 Inter-button spacing fixed 10px | FAIL | Several button rows use 6px: `149`, `210`, `270`, `358`; `UnsavedChangesDialog` uses 10px at `77`. |
| 13.4 Text never clipped | PASS | Message labels wrap at `71`, `144`, `199`, `257`, `307`, `353`. |
| 13.5 Multiline inputs >= 2 lines | N/A | These are single-line/no-input modals. |
| 13.6 Default size content-driven | UNKNOWN | Qt size hints plus hardcoded widths; no formal default method. |
| 13.7 Geometry persistence | N/A | Simple modal popovers likely exempt if documented. |
| 13.8 Reset path | N/A | Simple modal popovers likely exempt if documented. |

#### Section 1.4 checks

| Check | Status | Evidence |
|---|---|---|
| 1.4.A No oversized fixed columns | N/A | No tables. |
| 1.4.B No decorative margins | PASS | Dialog spacing is normal compact modal spacing. |
| 1.4.C No range-based dimensions | FAIL | Magic widths/heights are repeated across modal classes. |
| 1.4.D No wrapper widgets where one suffices | PASS | Layouts are direct. |

#### Section 1.5 checks

| Check | Status | Evidence |
|---|---|---|
| 1.5.A No redundant teaching | PASS | Modal messages are context-specific prompts. |
| 1.5.B No descriptive prose where operational data belongs | PASS | Confirm/input/item/choice roles are explicit. |
| 1.5.C No filler | PASS | No filler surfaces seen. |
| 1.5.D No status-bar duplication | N/A | Modals have no statusbar. |
| 1.5.E Component sub-elements justified | PASS | Message, input/list, and button rows are justified. |

**Severity:** Medium.

**Fix recommendation:** Set policy: either fixed/content-sized modal popovers with fit assertions, or true Section 13 resizable dialogs. Today they sit between the two.

## Compliance summary tables

### Section 13 compliance (resizable/top-level surfaces)

| Surface | 13.1 | 13.2 | 13.3 | 13.4 | 13.5 | 13.6 | 13.7 | 13.8 | Severity |
|---|---|---|---|---|---|---|---|---|---|
| MainWindow | F | ? | F | P | N | F | F | F | H |
| InstructionPane | F | P | P | P | F | F | F | F | H |
| TestingSettingsDialog | F | ? | ? | P | N | ? | F | F | H |
| AuditModuleWindow | F | ? | F | F | N | F | F | F | H |
| TemplateLibraryDialog | F | ? | F | ? | N | F | F | F | M |
| TemplateEditorDialog | F | P | P | ? | N | F | F | F | M |
| RegionReviewDialog | F | P | P | P | N | P | F | F | M |
| Reusable dark modals | F | ? | F | P | N | ? | N | N | M |
| PatientFormDialog | N | ? | ? | ? | ? | N | N | N | L |
| SaveLayoutDialog | N | ? | P | ? | N | N | N | N | L |
| Region transient surfaces | N | N | N | ? | N | N | N | N | L |
| SplashScreen | N | N | N | P | N | N | N | N | None |

### Section 1.4 compliance (all audited surfaces)

| Surface | 1.4.A | 1.4.B | 1.4.C | 1.4.D | Severity |
|---|---|---|---|---|---|
| MainWindow | N | ? | F | ? | H |
| LibraryView | N | P | ? | P | M |
| ImportPromptBanner | N | P | P | P | L |
| PatientListPanel | N | P | ? | P | M |
| PatientFormDialog | N | P | F | P | L |
| AdjustmentsPanel | N | P | P | P | L |
| DrawingPanel | N | P | ? | P | L |
| LayersPanel | N | P | ? | P | L |
| Filmstrip/TemplateViewContainer | N | P | ? | P | L |
| ComparisonView | N | P | P | P | M |
| InstructionPane | N | P | F | P | H |
| TestingSettingsDialog | N | P | ? | P | H |
| AuditModuleWindow | F | P | F | ? | H |
| _BugListScreen | F | P | F | P | H |
| _BugDetailScreen | N | ? | ? | ? | M |
| _ArchiveScreen | ? | P | ? | P | L |
| TemplateLibraryDialog | N | P | F | P | M |
| TemplateEditorDialog | N | P | F | P | M |
| Region transient surfaces | N | P | ? | P | L |
| RegionReviewDialog | N | P | ? | P | M |
| Reusable dark modals | N | P | F | P | M |
| SaveLayoutDialog | N | P | F | P | L |
| SplashScreen | N | P | N | P | None |

### Section 1.5 compliance (all audited surfaces)

| Surface | 1.5.A | 1.5.B | 1.5.C | 1.5.D | 1.5.E | Severity |
|---|---|---|---|---|---|---|
| MainWindow | ? | P | ? | ? | ? | H |
| LibraryView | P | F | P | P | ? | M |
| ImportPromptBanner | P | P | P | P | P | L |
| PatientListPanel | P | P | ? | P | P | M |
| PatientFormDialog | P | P | P | N | P | L |
| AdjustmentsPanel | P | P | P | P | P | L |
| DrawingPanel | P | P | P | P | P | L |
| LayersPanel | P | P | P | P | P | L |
| Filmstrip/TemplateViewContainer | P | P | P | P | P | L |
| ComparisonView | P | P | P | P | P | M |
| InstructionPane | P | P | P | P | P | H |
| TestingSettingsDialog | P | P | P | P | P | H |
| AuditModuleWindow | F | F | F | F | F | H |
| _BugListScreen | F | F | F | F | F | H |
| _BugDetailScreen | ? | P | ? | ? | ? | M |
| _ArchiveScreen | P | P | ? | ? | ? | L |
| TemplateLibraryDialog | ? | ? | P | N | P | M |
| TemplateEditorDialog | P | P | P | N | P | M |
| Region transient surfaces | P | P | P | P | P | L |
| RegionReviewDialog | P | P | P | N | P | M |
| Reusable dark modals | P | P | P | N | P | M |
| SaveLayoutDialog | P | P | P | N | P | L |
| SplashScreen | P | P | P | N | P | None |

## Triage recommendations

1. **Ship AM Screen A header/columns first.**
   This is the clearest Section 1.4/1.5 violation and already has design direction: delete redundant right-header prose, keep the left pane as state/teaching owner, compact metadata columns, and wrap titles.

2. **Create shared Section 13 helpers before fixing individual windows.**
   Add reusable geometry restore/persist/reset helpers with off-screen sanity checks. Then each top-level window can implement only its floor/default calculation.

3. **Replace app reset with a true geometry reset.**
   `View -> Reset Layout` should either be renamed to dock reset or expanded into `View -> Reset window layout` that removes all known geometry keys.

4. **Make InstructionPane the reference Section 13 implementation.**
   It has the richest button-cluster math and is closest to #129. Fix it first, then apply the pattern to TestingSettingsDialog.

5. **Batch template windows.**
   `TemplateLibraryDialog` and `TemplateEditorDialog` both fail hardcoded default/floor and missing geometry persistence. Treat them as one Template module resize pass.

6. **Define a reusable-modal policy.**
   If dark modal dialogs remain fixed/content-sized, document that exemption and add fit assertions. If they are resizable, bring them into full Section 13 compliance.

7. **Fold MainWindow floors into module overhaul.**
   Child panels are mostly reasonable individually, but MainWindow has no active-surface floor proof. When Library/Edit/Comparison module overhauls happen, compute floors from the active module chrome.

## Open questions for Darrin

1. Should `Reset Layout` become the Section 13 geometry reset, or should PG keep separate `Reset dock layout` and `Reset window layout` actions?

2. Should simple modal popovers be formally exempt from geometry persistence if they are fixed/content-sized with fit assertions?

3. Should MainWindow continue first-launch maximized, or should it follow the same content-driven default policy as the other resizable windows?

4. Should AM's bottom statusbar keep queue summary, or should it specialize in source/freshness while StatusPane owns queue state?

5. Are dev/test harness windows outside Section 13 enforcement, or should they adopt the same helpers for consistency?

## Cross-check note for CC

I used `RESIZE_AUDIT_v1.md` as the Section 13 baseline and focused this pass on adding Section 1.4/1.5 coverage for major user-visible surfaces. The highest-confidence findings are AM Screen A, app-level reset, missing compute/default sizing, and template/instruction-pane geometry. The weaker areas worth cross-checking are Library empty-state wording, Patient/Layer long-text clipping, Archive screen details, and whether reusable modal dialogs should be treated as exempt fixed/content-sized popovers or full Section 13 windows.

-- Codex
