# RESIZE_AUDIT_v1 - Codex pass

**Date:** 2026-04-26
**Author:** Codex
**Scope:** PG Bible Section 13 compliance - every resizable surface in the PG codebase
**Reference:** `PG_DESIGN_BIBLE_v1.md` Section 13.1 through Section 13.8

## Summary

Codex audited 18 top-level or potentially top-level Qt surfaces: 8 production
resizable windows/dialogs, 8 fixed or transient modal/tool surfaces, and 2
dev/test harness windows called out because they are `QMainWindow` subclasses.
No audited production resizable surface is fully Section 13 compliant today.
The common failure is architectural: there is no `_compute_min_size()` /
`_compute_default_size()` implementation anywhere in the production Python
source, so most windows rely on hardcoded minimums, hardcoded default sizes,
Qt size hints, or maximized startup.

The highest-priority surfaces are `InstructionPane`, `TestingSettingsDialog`,
`AuditModuleWindow`, `TemplateLibraryDialog`, `TemplateEditorDialog`, and
`MainWindow`. These are user-facing, resizable, and either have hardcoded
minimum/default sizes or missing geometry persistence. `InstructionPane` is
closest to the locked #129 invariant because its button clusters use 10px gaps
and it already persists geometry, but it still has hardcoded `MIN_SIZE` /
`DEFAULT_SIZE`, no multi-monitor restore sanity, and a fixed 60px multiline
input floor.

The app-level reset path also misses Section 13.4. `View -> Reset Layout`
exists, but its implementation only re-docks and re-shows dock widgets; it does
not remove geometry keys or reset all persisted windows. Until a true
`View -> Reset window layout` action exists, every resizable surface fails
check 8 even if it has a local reset affordance.

Legend: `PASS`, `FAIL`, `N/A`, `UNKNOWN`. Summary table uses `P`, `F`, `N`,
and `?`.

## App-level findings

1. **No Section 13 min/default-size implementation exists.**
   Evidence: source search across production `.py` files found no
   `_compute_min_size`, `compute_min_size`, `_compute_default_size`, or
   `compute_default_size`. This is a global gap for every resizable surface.

2. **`View -> Reset Layout` is not Section 13.4 reset.**
   Evidence: `panda_gallery.py:889-891` adds `Reset &Layout`; `panda_gallery.py:1087-1092`
   only sets `QDockWidget` children non-floating and visible. It does not
   remove `InstructionPane/geometry`, `testingSettingsDialog/geometry`, AM
   geometry, template geometry, or main-window geometry.

3. **Only instruction-pane surfaces currently persist geometry.**
   Evidence: geometry keys appear in `instruction_pane.py:73` and
   `instruction_pane.py:2537`; restore/save calls appear at
   `instruction_pane.py:2494-2521` and `instruction_pane.py:2593-3089`.
   No other production source had `saveGeometry()` / `restoreGeometry()` hits.

4. **No audited restore path performs the Section 13.3 multi-monitor sanity
   check.**
   Evidence: `InstructionPane.showEvent()` calls `restoreGeometry(saved)` at
   `instruction_pane.py:2497`; `TestingSettingsDialog.__init__()` calls
   `restoreGeometry(saved)` at `instruction_pane.py:2595`. Neither checks
   `QGuiApplication.screens()` / `QRect.intersects()` before restore.

5. **BUGS.md #129 remains the rule source.**
   Evidence: `BUGS.md:119-126` defines the locked four invariants; `BUGS.md:132-133`
   recommends computed floor and default-size policy. The Bible Section 13
   generalizes this to all resizable surfaces.

## Per-surface findings

### `MainWindow` (`panda_gallery.py`)

- **File:** `panda_gallery.py`
- **Class:** `MainWindow(QMainWindow)`
- **Window type:** main app window

| Check | Status | Evidence |
|---|---|---|
| 1. compute_min_size derivation | FAIL | `panda_gallery.py:145` hardcodes `setMinimumSize(1024, 680)`; no compute method found. |
| 2. Buttons visible at min | UNKNOWN | Main chrome has many child clusters; no floor derivation proves the active clusters fit at 1024x680. |
| 3. Spacing fixed 10px | FAIL | Example toolbar/tab clusters use 6px or 8px: `panda_gallery.py:262`, `480`; no documented narrow variant. |
| 4. Text not clipped | PASS | No `setTextElideMode` / `Elide*` usage found in production Python. |
| 5. Multi-line inputs >= 2 lines | N/A | MainWindow owns no top-level multiline input; child dialogs/panes audited separately. |
| 6. Default size content-driven | FAIL | Startup calls `window.showMaximized()` at `panda_gallery.py:2904`; no content-driven default after first launch. |
| 7. Persistence + multi-monitor | FAIL | No `saveGeometry()` / `restoreGeometry()` found for MainWindow. |
| 8. Reset path | FAIL | App menu reset exists but resets docks only (`panda_gallery.py:1087-1092`), not window geometry keys. |

**Severity:** High. This is the app shell; reset and persistence should be
centralized here.

**Fix recommendation:** Add app-level `View -> Reset window layout`, main-window
geometry key, off-screen restore guard, and a shell-specific default policy
that respects the Bible's app-shell exception while avoiding permanent
hardcoded launch behavior.

### `InstructionPane` (`instruction_pane.py`)

- **File:** `instruction_pane.py`
- **Class:** `InstructionPane(QDialog)`
- **Window type:** floating testing pane, top-level dialog/tool window

| Check | Status | Evidence |
|---|---|---|
| 1. compute_min_size derivation | FAIL | `instruction_pane.py:69-70` defines hardcoded `DEFAULT_SIZE` / `MIN_SIZE`; `802-803` applies them. |
| 2. Buttons visible at min | PASS | Action clusters have explicit min widths (`1066-1101`) and two-row containers; BUGS.md #124 says manual verification passed. |
| 3. Spacing fixed 10px | PASS | Main nav/action rows use `setSpacing(10)` at `instruction_pane.py:1110` and `1121`. |
| 4. Text not clipped | PASS | No elide calls found; main labels are wrapped in the step renderer. |
| 5. Multi-line inputs >= 2 lines | FAIL | `_FailNoteEdit` uses fixed `setMinimumHeight(60)` at `instruction_pane.py:168`, not fontMetrics-derived. |
| 6. Default size content-driven | FAIL | `instruction_pane.py:803` hardcodes `resize(*DEFAULT_SIZE)`; fallback position uses `DEFAULT_SIZE[0]` at `1321`. |
| 7. Persistence + multi-monitor | FAIL | Persists/restores at `2494-2521`, but no screen-intersection sanity check before `restoreGeometry`. |
| 8. Reset path | FAIL | Local settings reset removes only pane geometry (`3015-3016`); app-level reset is missing. |

**Severity:** High. This surface is the canonical #129 consumer and the most
important reference implementation candidate.

**Fix recommendation:** Promote the existing button math comment into
`_compute_min_size()`, derive `_FailNoteEdit` height from font metrics, add
`_compute_default_size()`, and add off-screen restore fallback.

### `TestingSettingsDialog` (`instruction_pane.py`)

- **File:** `instruction_pane.py`
- **Class:** `TestingSettingsDialog(QDialog)`
- **Window type:** testing settings dialog

| Check | Status | Evidence |
|---|---|---|
| 1. compute_min_size derivation | FAIL | No compute method; #129 cites this dialog as the original hardcoded-sizing surface. |
| 2. Buttons visible at min | UNKNOWN | Close/reset controls are present, but no computed floor proves button clusters fit at minimum. |
| 3. Spacing fixed 10px | UNKNOWN | Several layouts use 10px/12px; no focused button-cluster audit or derivation exists. |
| 4. Text not clipped | PASS | No elide calls found in the file. |
| 5. Multi-line inputs >= 2 lines | N/A | Settings controls are checkboxes/combos/buttons; no QTextEdit input in the dialog. |
| 6. Default size content-driven | UNKNOWN | There is no hardcoded `resize()`, so Qt sizeHint may drive first open; no Section 13 `_compute_default_size()`. |
| 7. Persistence + multi-monitor | FAIL | Restores at `instruction_pane.py:2593-2595`; saves in accept/reject/close at `3038-3089`; no off-screen sanity check. |
| 8. Reset path | FAIL | Dialog has pane reset (`3015-3016`) but no reset for `testingSettingsDialog/geometry`; app reset is missing. |

**Severity:** High. BUGS.md #128 fixed persistence, but Section 13 adds sizing
and multi-monitor obligations not yet met.

**Fix recommendation:** Add dialog-local min/default computation and validate
restored geometry before applying it.

### `AuditModuleWindow` (`audit_module/audit_module_window.py`)

- **File:** `audit_module/audit_module_window.py`
- **Class:** `AuditModuleWindow(QMainWindow)`
- **Window type:** dev Audit Module main window

| Check | Status | Evidence |
|---|---|---|
| 1. compute_min_size derivation | FAIL | `audit_module_window.py:2770` hardcodes `resize(800, 560)`; `2774` hardcodes `setMinimumSize(800, 500)`. |
| 2. Buttons visible at min | UNKNOWN | Child screens have several clusters; no floor derivation proves Screen A/B/Archive clusters fit at 800x500. |
| 3. Spacing fixed 10px | FAIL | Some button/header rows use 10px (`1744`, `2465`), but action clusters use 6px/4px (`1689`, `1894`). |
| 4. Text not clipped | PASS | No elide calls found in production Python. |
| 5. Multi-line inputs >= 2 lines | N/A | AM `QTextEdit`s are read-only displays (`1778`, `1841`, `2551`), not user multiline inputs. |
| 6. Default size content-driven | FAIL | Hardcoded default at `2770`; BUGS.md #138 explains the chosen 800x560 point. |
| 7. Persistence + multi-monitor | FAIL | Comment at `2768-2769` says persistent geometry is a follow-up; no save/restore found. |
| 8. Reset path | FAIL | No AM reset menu; app reset does not clear AM geometry. |

**Severity:** High. AM is actively being redesigned, so this should be folded
into the AM v2 implementation rather than patched later.

**Fix recommendation:** Add AM window geometry key, computed minimum across the
largest active stack screen, first-open default, and off-screen restore. Screen
B v2 should include floor/default smoke checks.

### `TemplateLibraryDialog` (`dialogs.py`)

- **File:** `dialogs.py`
- **Class:** `TemplateLibraryDialog(QWidget)`
- **Window type:** template library browser window

| Check | Status | Evidence |
|---|---|---|
| 1. compute_min_size derivation | FAIL | `dialogs.py:771` hardcodes `setMinimumSize(600, 400)`. |
| 2. Buttons visible at min | UNKNOWN | Toolbar/bottom controls are fixed-height; no computed floor proves all controls fit. |
| 3. Spacing fixed 10px | FAIL | Toolbar/bottom/grid use 8px spacing (`dialogs.py:785`, `841`, `853`) without Section 13 narrow-variant note. |
| 4. Text not clipped | PASS | Empty state wraps at `dialogs.py:833`; no elide calls found. |
| 5. Multi-line inputs >= 2 lines | N/A | No multiline input. |
| 6. Default size content-driven | FAIL | `dialogs.py:772` hardcodes `resize(800, 520)`. |
| 7. Persistence + multi-monitor | FAIL | Only card-width setting exists (`dialogs.py:868-870`); no window geometry save/restore. |
| 8. Reset path | FAIL | App reset does not clear template-library geometry; no per-window reset. |

**Severity:** Medium. Hardcoded floor/default and missing persistence are direct
Section 13 violations.

**Fix recommendation:** Compute floor from toolbar controls, card-size controls,
and minimum useful grid viewport; persist geometry separately from card width.

### `TemplateEditorDialog` (`template_designer.py`)

- **File:** `template_designer.py`
- **Class:** `TemplateEditorDialog(QWidget)`
- **Window type:** template designer window

| Check | Status | Evidence |
|---|---|---|
| 1. compute_min_size derivation | FAIL | `template_designer.py:878` hardcodes `setMinimumSize(950, 700)`. |
| 2. Buttons visible at min | PASS | Bottom button bar is fixed-height and uses stretch before Save buttons (`1060-1097`). |
| 3. Spacing fixed 10px | PASS | Bottom button cluster uses `bb.setSpacing(10)` at `template_designer.py:1068`. |
| 4. Text not clipped | UNKNOWN | Several right-pane labels/combos are fixed within a 360px scroll rail; no floor check proves no clipping. |
| 5. Multi-line inputs >= 2 lines | N/A | Uses single-line `QLineEdit` fields. |
| 6. Default size content-driven | FAIL | Constructor calls `showMaximized()` at `template_designer.py:881`; no default-size policy. |
| 7. Persistence + multi-monitor | FAIL | No `saveGeometry()` / `restoreGeometry()` found. |
| 8. Reset path | FAIL | No per-window reset; app reset does not clear geometry. |

**Severity:** Medium. Large design surface, but not as frequently opened as the
testing pane.

**Fix recommendation:** Replace constructor `showMaximized()` with restore or
content-driven default, persist geometry, and derive the minimum from the
bottom bar plus right rail plus canvas minimum.

### `RegionReviewDialog` (`region_capture.py`)

- **File:** `region_capture.py`
- **Class:** `RegionReviewDialog(QDialog)`
- **Window type:** modal review dialog after region capture

| Check | Status | Evidence |
|---|---|---|
| 1. compute_min_size derivation | FAIL | No compute method; preview size caps are constants at `region_capture.py:348-349`. |
| 2. Buttons visible at min | PASS | Button row uses fixed 10px spacing and stretch at `region_capture.py:411-413`. |
| 3. Spacing fixed 10px | PASS | `region_capture.py:412` explicitly cites #129 invariant 2. |
| 4. Text not clipped | PASS | Metadata label is single line; no elide calls found. |
| 5. Multi-line inputs >= 2 lines | N/A | No multiline input. |
| 6. Default size content-driven | PASS | Dialog size is driven by scaled pixmap and layout; no hardcoded `resize()` / `setMinimumSize()` found. |
| 7. Persistence + multi-monitor | FAIL | No geometry save/restore; no off-screen guard. |
| 8. Reset path | FAIL | No per-window reset; app reset does not clear geometry. |

**Severity:** Medium. The dialog already has a content-driven preview cap, but
still lacks the formal Section 13 persistence/reset contract.

**Fix recommendation:** Add geometry persistence and make the preview cap part
of a `_compute_min_size()` / `_compute_default_size()` pair.

### `DarkConfirmDialog` (`dialogs.py`)

- **File:** `dialogs.py`
- **Class:** `DarkConfirmDialog(QDialog)`
- **Window type:** reusable modal confirm dialog

| Check | Status | Evidence |
|---|---|---|
| 1. compute_min_size derivation | FAIL | `dialogs.py:134` hardcodes `setMinimumWidth(420)`. |
| 2. Buttons visible at min | UNKNOWN | Buttons fit visually in simple cases, but no computed floor covers arbitrary labels. |
| 3. Spacing fixed 10px | FAIL | `dialogs.py:149` uses 6px spacing, justified by old focus-ring margins rather than Section 13. |
| 4. Text not clipped | PASS | Message label wraps at `dialogs.py:143-145`. |
| 5. Multi-line inputs >= 2 lines | N/A | No multiline input. |
| 6. Default size content-driven | UNKNOWN | Qt sizeHint drives height, but width floor is hardcoded. |
| 7. Persistence + multi-monitor | N/A | Simple modal popover; persistence likely not desired. |
| 8. Reset path | N/A | Simple modal popover; reset not expected. |

**Severity:** Low. Either make this intentionally fixed/content-sized, or add a
small computed floor for arbitrary button labels.

**Fix recommendation:** Standardize modal-popover policy: fixed/content-sized
dialogs get explicit N/A comments; reusable resizable dialogs get compute
methods.

### `DarkInputDialog` (`dialogs.py`)

- **File:** `dialogs.py`
- **Class:** `DarkInputDialog(QDialog)`
- **Window type:** reusable single-line input modal

| Check | Status | Evidence |
|---|---|---|
| 1. compute_min_size derivation | FAIL | `dialogs.py:190` hardcodes `setMinimumWidth(420)`. |
| 2. Buttons visible at min | UNKNOWN | No floor derivation for Cancel/OK labels. |
| 3. Spacing fixed 10px | FAIL | `dialogs.py:210` uses 6px spacing. |
| 4. Text not clipped | PASS | Optional prompt label wraps at `dialogs.py:197-200`. |
| 5. Multi-line inputs >= 2 lines | N/A | Single-line `QLineEdit` only. |
| 6. Default size content-driven | UNKNOWN | Qt sizeHint plus hardcoded width; no Section 13 default method. |
| 7. Persistence + multi-monitor | N/A | Simple modal input popover; persistence likely not desired. |
| 8. Reset path | N/A | Simple modal input popover; reset not expected. |

**Severity:** Low.

**Fix recommendation:** Same reusable modal policy as `DarkConfirmDialog`.

### `DarkItemDialog` (`dialogs.py`)

- **File:** `dialogs.py`
- **Class:** `DarkItemDialog(QDialog)`
- **Window type:** reusable item-picker modal

| Check | Status | Evidence |
|---|---|---|
| 1. compute_min_size derivation | FAIL | `dialogs.py:247-248` hardcodes minimum width/height. |
| 2. Buttons visible at min | UNKNOWN | No computed floor for arbitrary item/dialog labels. |
| 3. Spacing fixed 10px | FAIL | `dialogs.py:270` uses 6px spacing. |
| 4. Text not clipped | PASS | Optional label wraps at `dialogs.py:255-258`. |
| 5. Multi-line inputs >= 2 lines | N/A | No multiline input. |
| 6. Default size content-driven | FAIL | Hardcoded min height drives the picker instead of content/default policy. |
| 7. Persistence + multi-monitor | N/A | Simple picker modal; persistence likely not desired unless item lists become large. |
| 8. Reset path | N/A | Simple picker modal; reset not expected. |

**Severity:** Low.

**Fix recommendation:** Either mark as fixed/content-sized by design or compute
floor from list height, label width, and button labels.

### `DarkChoiceDialog` (`dialogs.py`)

- **File:** `dialogs.py`
- **Class:** `DarkChoiceDialog(QDialog)`
- **Window type:** reusable N-button modal

| Check | Status | Evidence |
|---|---|---|
| 1. compute_min_size derivation | FAIL | `dialogs.py:340` hardcodes `setMinimumWidth(460)`. |
| 2. Buttons visible at min | FAIL | Arbitrary `buttons: list[str]` at `dialogs.py:335-336`; no floor computes total button width. |
| 3. Spacing fixed 10px | FAIL | `dialogs.py:358` uses 6px spacing. |
| 4. Text not clipped | PASS | Message label wraps at `dialogs.py:352-354`. |
| 5. Multi-line inputs >= 2 lines | N/A | No multiline input. |
| 6. Default size content-driven | UNKNOWN | Qt sizeHint may grow for button labels, but width floor is a magic number. |
| 7. Persistence + multi-monitor | N/A | Simple modal choice popover; persistence likely not desired. |
| 8. Reset path | N/A | Simple modal choice popover; reset not expected. |

**Severity:** Medium. Generic arbitrary-button surface is more likely to hit
the #129 button-cluster invariant than fixed two-button dialogs.

**Fix recommendation:** Compute minimum width from all active buttons plus
10px gaps and margins, or explicitly wrap to a documented two-row modal
variant.

### `UnsavedChangesDialog` (`dialogs.py`)

- **File:** `dialogs.py`
- **Class:** `UnsavedChangesDialog(QDialog)`
- **Window type:** fixed-size modal prompt

| Check | Status | Evidence |
|---|---|---|
| 1. compute_min_size derivation | N/A | Fixed prompt via `setFixedSize(420, 160)` at `dialogs.py:58`. |
| 2. Buttons visible at min | PASS | Fixed three-button row with 10px spacing at `dialogs.py:76-95`. |
| 3. Spacing fixed 10px | PASS | `dialogs.py:77` uses 10px. |
| 4. Text not clipped | UNKNOWN | Message wraps, but arbitrary `context` can lengthen text inside fixed 420x160 box (`dialogs.py:69-71`). |
| 5. Multi-line inputs >= 2 lines | N/A | No multiline input. |
| 6. Default size content-driven | N/A | Fixed modal, not user-resizable. |
| 7. Persistence + multi-monitor | N/A | Fixed modal; persistence not expected. |
| 8. Reset path | N/A | Fixed modal; reset not expected. |

**Severity:** Low.

**Fix recommendation:** Add a fit assertion for long `context` strings or
derive fixed size from the context label.

### `PatientFormDialog` (`patient_panel.py`)

- **File:** `patient_panel.py`
- **Class:** `PatientFormDialog(QDialog)`
- **Window type:** fixed patient create/edit modal

| Check | Status | Evidence |
|---|---|---|
| 1. compute_min_size derivation | N/A | Fixed-size modal via `setFixedSize(440, 520)` at `patient_panel.py:212`. |
| 2. Buttons visible at min | UNKNOWN | Button row has no explicit spacing; `patient_panel.py:321-335` relies on defaults and stretch. |
| 3. Spacing fixed 10px | UNKNOWN | No `btn_row.setSpacing(10)` on the save/cancel row. |
| 4. Text not clipped | UNKNOWN | Fixed size plus form labels/fields; no fit assertion for longest labels/placeholders. |
| 5. Multi-line inputs >= 2 lines | UNKNOWN | Notes field is `QTextEdit` at `patient_panel.py:312` with max height 60 at `313`; no derived min height. |
| 6. Default size content-driven | N/A | Fixed modal, not user-resizable. |
| 7. Persistence + multi-monitor | N/A | Fixed modal; persistence not expected. |
| 8. Reset path | N/A | Fixed modal; reset not expected. |

**Severity:** Low.

**Fix recommendation:** If it stays fixed, add explicit fit assertions for
button row and notes field; otherwise convert to computed resizable dialog.

### `SaveLayoutDialog` (`dialogs.py`)

- **File:** `dialogs.py`
- **Class:** `SaveLayoutDialog(QWidget)`
- **Window type:** fixed save-as-template dialog

| Check | Status | Evidence |
|---|---|---|
| 1. compute_min_size derivation | N/A | Fixed dialog via `setFixedSize(450, 420)` at `dialogs.py:1099`. |
| 2. Buttons visible at min | UNKNOWN | Bottom controls not fully audited in this pass. |
| 3. Spacing fixed 10px | PASS | Root layout uses 10px spacing at `dialogs.py:1105`; button row evidence not expanded. |
| 4. Text not clipped | UNKNOWN | Fixed size with variable source layout name/description at `dialogs.py:1118`, `1127`. |
| 5. Multi-line inputs >= 2 lines | N/A | Uses single-line `QLineEdit` fields. |
| 6. Default size content-driven | N/A | Fixed dialog, not user-resizable. |
| 7. Persistence + multi-monitor | N/A | Fixed modal; persistence not expected. |
| 8. Reset path | N/A | Fixed modal; reset not expected. |

**Severity:** Low.

**Fix recommendation:** Add fixed-dialog fit assertions for long template names.

### `RegionCaptureOverlay` (`region_capture.py`)

- **File:** `region_capture.py`
- **Class:** `RegionCaptureOverlay(QWidget)`
- **Window type:** full-screen frameless capture overlay

| Check | Status | Evidence |
|---|---|---|
| 1. compute_min_size derivation | N/A | Overlay is forced to screen geometry, not user-resizable. |
| 2. Buttons visible at min | N/A | No button cluster. |
| 3. Spacing fixed 10px | N/A | No button cluster. |
| 4. Text not clipped | UNKNOWN | Banner text is fixed via `adjustSize()` and centered after resize; see `region_capture.py:79-89`, `91-93`. |
| 5. Multi-line inputs >= 2 lines | N/A | No multiline input. |
| 6. Default size content-driven | N/A | Uses `setGeometry(screen.geometry())` at `region_capture.py:89` by design. |
| 7. Persistence + multi-monitor | N/A | Transient overlay; persistence not expected. |
| 8. Reset path | N/A | Transient overlay; reset not expected. |

**Severity:** None for Section 13 resizable-window purposes.

**Fix recommendation:** Add a comment that full-screen overlays are exempt
from geometry persistence/default-size policy.

### `RegionCaptureToast` (`region_capture.py`)

- **File:** `region_capture.py`
- **Class:** `RegionCaptureToast(QWidget)`
- **Window type:** transient frameless tool toast

| Check | Status | Evidence |
|---|---|---|
| 1. compute_min_size derivation | N/A | Toast is transient and `adjustSize()`-driven, not user-resizable. |
| 2. Buttons visible at min | N/A | No buttons. |
| 3. Spacing fixed 10px | N/A | No button cluster. |
| 4. Text not clipped | UNKNOWN | Width is constrained `240-360` at `region_capture.py:297-298`; title/subtitle labels do not explicitly wrap. |
| 5. Multi-line inputs >= 2 lines | N/A | No multiline input. |
| 6. Default size content-driven | N/A | `adjustSize()` at `region_capture.py:299`. |
| 7. Persistence + multi-monitor | N/A | Transient toast; persistence not expected. |
| 8. Reset path | N/A | Transient toast; reset not expected. |

**Severity:** Low visual-risk only, not a Section 13 resizable-window issue.

**Fix recommendation:** Add wrapping or a width fit assertion for long toast
subtitles.

### `RegionCaptureFlash` (`region_capture.py`)

- **File:** `region_capture.py`
- **Class:** `RegionCaptureFlash(QWidget)`
- **Window type:** 80ms frameless flash overlay

| Check | Status | Evidence |
|---|---|---|
| 1. compute_min_size derivation | N/A | Flash geometry is set to captured rect (`region_capture.py:699`). |
| 2. Buttons visible at min | N/A | No buttons. |
| 3. Spacing fixed 10px | N/A | No button cluster. |
| 4. Text not clipped | N/A | No text. |
| 5. Multi-line inputs >= 2 lines | N/A | No input. |
| 6. Default size content-driven | N/A | Transient overlay. |
| 7. Persistence + multi-monitor | N/A | Transient overlay. |
| 8. Reset path | N/A | Transient overlay. |

**Severity:** None.

**Fix recommendation:** None for Section 13.

### `SplashScreen` (`splash.py`)

- **File:** `splash.py`
- **Class:** `SplashScreen(QWidget)`
- **Window type:** fixed splash window

| Check | Status | Evidence |
|---|---|---|
| 1. compute_min_size derivation | N/A | Fixed splash via `setFixedSize(_SPLASH_W, _SPLASH_H)` at `splash.py:103`. |
| 2. Buttons visible at min | N/A | No buttons. |
| 3. Spacing fixed 10px | N/A | No button cluster. |
| 4. Text not clipped | PASS | Version text is controlled overlay, not chrome label. |
| 5. Multi-line inputs >= 2 lines | N/A | No input. |
| 6. Default size content-driven | N/A | Splash asset has fixed logical dimensions. |
| 7. Persistence + multi-monitor | N/A | Splash position is transient. |
| 8. Reset path | N/A | Splash reset not expected. |

**Severity:** None.

**Fix recommendation:** None for Section 13.

### `ComparisonView` (`comparison_view.py`)

- **File:** `comparison_view.py`
- **Class:** `ComparisonView(QWidget)`
- **Window type:** child view inside `MainWindow`, not its own top-level window

| Check | Status | Evidence |
|---|---|---|
| 1. compute_min_size derivation | N/A | Child view; covered by MainWindow's eventual floor. |
| 2. Buttons visible at min | UNKNOWN | Top bar has many buttons (`comparison_view.py:240-270`) with 8px spacing, but parent floor is absent. |
| 3. Spacing fixed 10px | FAIL | Top bar uses `tb_layout.setSpacing(8)` at `comparison_view.py:231`. |
| 4. Text not clipped | PASS | No elide calls found. |
| 5. Multi-line inputs >= 2 lines | N/A | No multiline input. |
| 6. Default size content-driven | N/A | Child view. |
| 7. Persistence + multi-monitor | N/A | Child view. |
| 8. Reset path | N/A | Child view. |

**Severity:** Medium within MainWindow floor work.

**Fix recommendation:** When MainWindow gets a computed floor, include the
Comparison top bar button cluster in the active-surface calculation.

### `FreeformWindow` (`test_freeform.py`)

- **File:** `test_freeform.py`
- **Class:** `FreeformWindow(QMainWindow)`
- **Window type:** dev/test harness window

| Check | Status | Evidence |
|---|---|---|
| 1. compute_min_size derivation | FAIL | `test_freeform.py:761` hardcodes `resize(600, 500)`; no compute method. |
| 2. Buttons visible at min | UNKNOWN | Dev harness not audited visually. |
| 3. Spacing fixed 10px | UNKNOWN | Dev harness not audited deeply. |
| 4. Text not clipped | PASS | No elide calls found in searched production/harness files. |
| 5. Multi-line inputs >= 2 lines | N/A | No known multiline input. |
| 6. Default size content-driven | FAIL | Hardcoded default resize. |
| 7. Persistence + multi-monitor | FAIL | No geometry persistence found. |
| 8. Reset path | N/A | Dev harness; app reset likely not expected. |

**Severity:** Low. Include only if harness windows are kept under Section 13.

**Fix recommendation:** Either mark as excluded dev harness or update to the
same helper used by production windows.

### `ProbeWindow` (`applets/qaction_enable_probe.py`)

- **File:** `applets/qaction_enable_probe.py`
- **Class:** `ProbeWindow(QMainWindow)`
- **Window type:** diagnostic applet window

| Check | Status | Evidence |
|---|---|---|
| 1. compute_min_size derivation | FAIL | Search hit shows class at line 43 and hardcoded `resize(480, 320)` at line 47. |
| 2. Buttons visible at min | UNKNOWN | Diagnostic applet not audited visually. |
| 3. Spacing fixed 10px | UNKNOWN | Diagnostic applet not audited deeply. |
| 4. Text not clipped | PASS | No elide calls found in searched production/harness files. |
| 5. Multi-line inputs >= 2 lines | N/A | No known multiline input. |
| 6. Default size content-driven | FAIL | Hardcoded resize. |
| 7. Persistence + multi-monitor | FAIL | No geometry persistence found. |
| 8. Reset path | N/A | Diagnostic applet; app reset likely not expected. |

**Severity:** Low.

**Fix recommendation:** Exclude applets from Section 13 formally or use shared
window sizing helpers if applets remain maintained.

## Compliance summary table

| Surface | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | Severity |
|---|---|---|---|---|---|---|---|---|---|
| MainWindow | F | ? | F | P | N | F | F | F | H |
| InstructionPane | F | P | P | P | F | F | F | F | H |
| TestingSettingsDialog | F | ? | ? | P | N | ? | F | F | H |
| AuditModuleWindow | F | ? | F | P | N | F | F | F | H |
| TemplateLibraryDialog | F | ? | F | P | N | F | F | F | M |
| TemplateEditorDialog | F | P | P | ? | N | F | F | F | M |
| RegionReviewDialog | F | P | P | P | N | P | F | F | M |
| DarkConfirmDialog | F | ? | F | P | N | ? | N | N | L |
| DarkInputDialog | F | ? | F | P | N | ? | N | N | L |
| DarkItemDialog | F | ? | F | P | N | F | N | N | L |
| DarkChoiceDialog | F | F | F | P | N | ? | N | N | M |
| UnsavedChangesDialog | N | P | P | ? | N | N | N | N | L |
| PatientFormDialog | N | ? | ? | ? | ? | N | N | N | L |
| SaveLayoutDialog | N | ? | P | ? | N | N | N | N | L |
| RegionCaptureOverlay | N | N | N | ? | N | N | N | N | None |
| RegionCaptureToast | N | N | N | ? | N | N | N | N | L |
| RegionCaptureFlash | N | N | N | N | N | N | N | N | None |
| SplashScreen | N | N | N | P | N | N | N | N | None |
| ComparisonView child surface | N | ? | F | P | N | N | N | N | M-in-parent |
| FreeformWindow dev harness | F | ? | ? | P | N | F | F | N | L |
| ProbeWindow diagnostic applet | F | ? | ? | P | N | F | F | N | L |

## Triage recommendations

1. **Create shared Section 13 helpers first.**
   Add a small window-geometry helper that centralizes:
   `_geometry_on_current_screen()`, `_restore_or_default_geometry()`,
   `_persist_geometry_not_below_floor()`, and `reset_all_window_geometry()`.
   This avoids each surface inventing a slightly different QSettings pattern.

2. **Ship app-level reset as its own small patch.**
   `View -> Reset Layout` should either be renamed to clarify dock-only
   behavior, or replaced/augmented with `View -> Reset window layout`.
   The new action should remove all known geometry keys and confirm with the
   Section 13 wording.

3. **Make `InstructionPane` the reference implementation.**
   It already has the richest comments for button-cluster math and the most
   direct #129 lineage. Fix checks 1, 5, 6, and 7 here first, then reuse the
   pattern in Testing Settings.

4. **Fold AM sizing into AM v2.**
   AM is currently moving through v4.42/v4.43 redesign work. Add computed
   floor/default/persistence/reset while Screen A/B layouts are already being
   touched, rather than patching the legacy hardcoded 800x560/800x500 state.

5. **Batch template windows together.**
   `TemplateLibraryDialog` and `TemplateEditorDialog` both have hardcoded
   floors/defaults and no geometry persistence. Fix them as one Template
   module resize pass.

6. **Set a policy for reusable modal dialogs.**
   Decide whether `DarkConfirmDialog`, `DarkInputDialog`, `DarkItemDialog`,
   and `DarkChoiceDialog` are intentionally fixed/content-sized popovers
   exempt from persistence, or resizable dialogs subject to Section 13. Today
   they are in between: minimum widths are hardcoded, but no fixed-size or
   computed-floor contract documents the intent.

7. **Do not spend production time on transient overlays.**
   `RegionCaptureOverlay`, `RegionCaptureFlash`, `RegionCaptureToast`, and
   `SplashScreen` are not user-resizable surfaces. Add exemption comments if
   desired, but they should not block Section 13 rollout.

## Open questions for Darrin

1. Should `View -> Reset Layout` be repurposed into the Section 13 reset, or
   should PG keep both `Reset Layout` for docks and `Reset window layout` for
   persisted geometries?

2. Should simple reusable modal dialogs be explicitly fixed/content-sized and
   exempt from geometry persistence, or should every `QDialog` subclass adopt
   the full Section 13 compute/persist/reset pattern?

3. Does `MainWindow.showMaximized()` remain a product decision for first
   launch, or should MainWindow follow the same content-driven default after
   splash?

4. Are dev/test harnesses (`test_freeform.py`, `applets/qaction_enable_probe.py`)
   inside Section 13 enforcement, or should the audit formally exclude them?

5. For `RegionReviewDialog`, should geometry persistence be useful, or should
   the dialog remain content-driven and transient with an explicit exemption?

