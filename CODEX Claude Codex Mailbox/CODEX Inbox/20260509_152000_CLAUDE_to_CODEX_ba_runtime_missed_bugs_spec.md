---
schema_version: 1
message_id: 20260509_152000_CLAUDE_to_CODEX_ba_runtime_missed_bugs_spec
in_reply_to: null
thread_id: BA-RUNTIME-MISSED-BUGS-20260509
from: CLAUDE
to: CODEX
date: 2026-05-09T15:20:00-07:00
subject: DISPATCH -- Research + author exquisite BA spec to catch all hands-on missed bugs; deliver to CC directly (BA carve-out)
status: directive
priority: high
reasoning_tier: Extra-High
---

# BA Runtime Coverage Spec — Missed-Bug Detection

## Mission

Darrin completed hands-on Vellum testing today and found 12 bugs that
passed every automated test (pytest 1329/1329, smoke 239/239, BA 0
hard-fails, pg_design_lint 0 errors). Every bug is a runtime or
behavioral issue invisible to static analysis. Your task is to research
the BA codebase, SPEC_0007 (already approved), and the missed-bug
descriptions below, then author an exquisite companion spec that tells
CC exactly what new BA checks to implement so this class of bug is
never missed again.

**Deliver directly to CC Inbox (BA carve-out — no CD gate required).**
Also notify CD inbox when filed.

---

## Research sources (read all before drafting)

1. `scripts/ba_audit_runner.py` — current BA runner, scanners, manifest
2. `scripts/ba_audit_manifest.json` — current app registration
   (find exact path: `grep -r "ba_audit_manifest" scripts/ workflows/ --include="*.py" -l`)
3. `workflows/specs/SPEC_PYSIDE6_RUNTIME_BA_v1.md` (SPEC_0007) —
   approved runtime BA framework; your spec is a companion/extension
4. `workflows/design/applets/am_mockup_review.py` — Vellum source
5. `workflows/design/applets/vellum_approval/widgets.py` — panel source
6. `workflows/specs/SPEC_INDEX.md` — assign this spec SPEC_0008
7. Any existing BA rule definitions and check schemas

---

## The 12 missed bugs — what BA must detect

### Category 1 — Text truncation / label elision

**Bug #220:** Toolbar button labels ("Select", "Callout", "Region",
"Eraser", "Arrow") are truncated to "S...t", "Ca...ut", "R...n",
"Er...er", "A...w" because `QToolButton` widgets have no
`setMinimumWidth()` call. Qt silently elides the label at paint time.

**Required BA check:**
For every `QToolButton` and `QPushButton` that has a text label,
at runtime: instantiate the widget, measure `QFontMetrics.horizontalAdvance(label)`,
compare against `widget.width()`. If advance > width − padding, the
label WILL be clipped. Report as FAIL with the label text, the
measured advance, and the widget width.

The check must also verify that NO `QLabel`, `QLineEdit` placeholder,
or `QComboBox` text is elided anywhere in the window at the canonical
window width (1366px — the narrowest supported per Bible §13).

---

### Category 2 — Widget background color at runtime

**Bug #229:** `ApprovalReviewPanel` renders a white background because
the `QScrollArea` viewport child widget uses Qt's default system palette
(white on Windows) instead of the app's dark theme. The QSS covers the
scroll area frame but not the viewport children. BA static analysis
sees the QSS rule is present and passes — but the runtime widget is
visibly white.

**Required BA check:**
At runtime, after the window is fully constructed and shown (with an
`offscreen` QPA platform), query the effective background color of
every major panel widget: `widget.palette().color(widget.backgroundRole())`.
Compare against the Bible's canonical dark palette. Any widget whose
effective background resolves to Qt's default white (#ffffff or
system palette Window color) outside of explicitly white-background
areas (e.g., a text input field) is a FAIL.

This check must cover: the top-level window, all major panel widgets
(stencil panel, approval panel, canvas area, filmstrip container,
right panel), and the viewport children of all `QScrollArea` instances.

---

### Category 3 — Tooltip completeness on interactive elements

**Bug #225:** Many interactive elements (stencil tiles, filmstrip
items, color swatches, rating stars, approval buttons) have no tooltip.
The tool buttons DO have tooltips, but most other interactive elements
do not. Static BA cannot detect absent tooltips because the check
would need to know which widgets ARE interactive.

**Required BA check:**
At runtime, enumerate all visible interactive widgets: `QPushButton`,
`QToolButton`, `QListWidgetItem` (via `item.toolTip()`), custom
tile widgets. For each, call `.toolTip()` (for widgets) or `.toolTip()`
(for items). Any interactive widget with an empty string tooltip is a
FAIL. Non-interactive widgets (layout spacers, separators, labels that
are not clickable) are exempt.

The check must distinguish interactive from decorative: a `QLabel`
that is not clickable is exempt; a `QLabel` that has a `mousePressEvent`
or is inside a clickable container is not.

---

### Category 4 — Context menu availability

**Bug #226:** Right-clicking on the canvas and filmstrip produces no
context menu. No `contextMenuEvent` is implemented on these widgets.
Static analysis cannot verify runtime right-click behavior.

**Required BA check:**
At runtime, simulate a right-click (`QTest.mouseClick` with
`Qt.MouseButton.RightButton`) on:
- The canvas widget (center of the loaded mockup)
- Each filmstrip item

After each right-click, verify that a `QMenu` with at least one
`QAction` was shown. The check can intercept the menu via monkey-patching
`QMenu.exec` (PySide6 uses `exec`, not `exec_` — the latter is
Python 2 era) before the right-click, then restore after:

Report FAIL for any interactive widget class that should have a context
menu but does not respond to right-click.

---

### Category 5 — DPR-aware image quality

**Bug #222:** Filmstrip thumbnails are blurry because they are generated
at 120×80 logical pixels but displayed at 3× DPR without high-res
source data. The `setDevicePixelRatio` call was applied (v5.1.0 fix)
but the source bitmap is still only 120×80, so DPR-awareness cannot
recover lost detail.

**Required BA check:**
At runtime, after the filmstrip is populated, inspect each filmstrip
item's icon pixmap:
1. Get `pixmap.devicePixelRatio()` — must match the screen's DPR
2. Get `pixmap.width()` (physical) — must be ≥ `icon_size.width() × DPR`

If either condition fails, report FAIL with the measured values. The
check must be DPR-aware: on a 1× display all pixmaps pass; on a 3×
display the physical pixel requirement triples.

**Critical caveat:** On a headless/offscreen QPA platform, DPR=1 and
this check trivially passes. The spec must explicitly note this check
requires a real HiDPI display (DPR ≥ 2) to be meaningful. Mark it as
`requires_real_display: true` in the probe registration. Provide a
fallback: if DPR=1 is detected, verify the pixmap physical width is
at least 2× the icon logical width (future-proof minimum).

---

### Category 6 — Filmstrip layout orientation

**Bug #223:** The filmstrip uses `QListWidget.Flow.LeftToRight` (icon
left, label right) instead of `IconMode` (icon above, label below).
The layout is set at construction time and only visible at runtime.

**Required BA check:**
At runtime, read `filmstrip.viewMode()`. Expected:
`QListView.ViewMode.IconMode`. If the value is `ListMode` (the default),
report FAIL with a message: "Filmstrip uses ListMode (icon-left,
label-right); expected IconMode (icon-above, label-below) per UX spec."

Also verify `filmstrip.gridSize().width() >= 180` to confirm adequate
horizontal spacing for the icon+label stack.

---

### Category 7 — Panel resizability (fixed-height anti-pattern)

**Bug #230:** The filmstrip has `setFixedHeight(118)` making it
unresizable. The user cannot adjust filmstrip height. Static analysis
sees a `setFixedHeight` call but cannot know if it is intentional (for
a fixed chrome element) or a mistake (for a user-facing panel).

**Required BA check:**
At runtime, identify panel widgets that should be user-resizable.
A panel is resizable if it is a direct child of a `QSplitter`. The
check should verify:
1. `filmstrip` is a direct or indirect child of a `QSplitter`
   (use `widget.parentWidget()` chain until QSplitter or top-level found)
2. `filmstrip.minimumHeight() < filmstrip.maximumHeight()` — i.e., it
   is NOT fixed (minimumHeight == maximumHeight = setFixedHeight behavior)

If the filmstrip has `minimumHeight() == maximumHeight()` (fixed),
report FAIL: "FilmstripWidget has fixed height — user cannot resize."

Extend this check to any panel widget that is a sibling of a canvas
or primary content area — those panels should never be fixed-height.

---

### Category 8 — Help content completeness

**Bug #231:** Help dialog sections exist as collapsible headings but
some section bodies are empty or contain placeholder text.

**Required BA check:**
At runtime, open the `HelpDialog`, expand every section, and read
the text content of each section body:
1. Count the number of collapsed sections with an empty body (< 50 chars
   of visible text after stripping whitespace and HTML tags).
2. Verify no body contains placeholder strings: "TBD", "TODO",
   "Phase N", "not yet implemented", "coming soon".
3. Verify each section body mentions at least one keyboard shortcut
   (contains a shortcut-like pattern: single uppercase letter, or
   Ctrl+/Shift+/Alt+ prefix).

Report FAIL for each section failing conditions 1 or 2. Report WARN
for sections failing condition 3.

---

### Category 9 — Scene rect pan freedom

**Bug #221/#227:** `QGraphicsView` scene rect is set exactly to the
image dimensions, blocking pan beyond the image boundary. The user
cannot pan rightward or downward when the image is anchored to the
viewport origin.

**Required BA check:**
After loading a packet and displaying a mockup, read
`canvas.sceneRect()` and compare against the loaded pixmap rect.
First research the `ImageCanvas` class to find the actual attribute
name that holds the current pixmap (grep for `_pixmap`, `_image`,
`_current_pix`, or `_pix` in `ImageCanvas` — do NOT assume
`_current_pixmap` is correct):

```python
scene_rect = canvas.sceneRect()
pix_rect = QRectF(canvas.<actual_pixmap_attribute>.rect())
margin_left = pix_rect.left() - scene_rect.left()
margin_right = scene_rect.right() - pix_rect.right()
margin_top = pix_rect.top() - scene_rect.top()
margin_bottom = scene_rect.bottom() - pix_rect.bottom()
min_margin = 100  # Bible minimum for pan freedom
```

If any margin < `min_margin`, report FAIL: "Scene rect has insufficient
margin on [side]: [value]px < 100px minimum. User cannot pan [side]ward."

---

### Category 10 — Stencil-move crash safety

**Bug #228:** App crashes when a non-primary stencil (Ghost/Danger
button) is placed on the canvas and immediately dragged. The crash
is specific to that stencil type — placing a `primary_button` stencil
and dragging does not crash.

**Required BA check:**
This is a crash-safety probe, not a style check. At runtime:
1. Place one stencil of each registered subtype (iterate
   `MarkupToolbar.TOOLS` or the stencil registry) onto the canvas
   using `QTest.mouseDrag` or programmatic `_commit_stencil_drop`.
2. Immediately attempt to drag each placed stencil using
   `QTest.mousePress` + `QTest.mouseMove` + `QTest.mouseRelease`.
3. Catch any unhandled exception or Qt fatal error during the drag.
4. Report FAIL if any stencil subtype crashes on move.

This probe must run inside the per-step stderr capture (per the #214
fix) so any crash traceback is recorded as a FAIL. After the probe,
verify all stencils can be moved without exception.

---

### Category 11 — Widget row height / excessive padding

**Bug #224:** Help dialog section rows have excessive vertical padding
(estimated 44-56px per row for 15 sections), making the section list
require excessive scrolling. The row height is set at construction time
and only measurable at runtime.

**Required BA check:**
At runtime, after opening `HelpDialog`, measure the height of each
collapsible section header button or row widget:
```python
for section_btn in help_dialog.findChildren(QAbstractButton):
    if section_btn.isVisible() and section_btn.height() > 40:
        report_fail(f"{section_btn.objectName()} row height "
                    f"{section_btn.height()}px exceeds 40px maximum")
```
Expected maximum: 40px per collapsed section row. If any row is taller,
report FAIL: "HelpDialog section row [name] is [N]px; maximum 40px for
all 15 sections to fit in a half-screen dialog."

Also verify that the total height of all collapsed section rows ≤
`dialog.height() * 0.8` — i.e., 80% of the dialog height is available
for the section list without scrolling.

---

## Spec requirements

### Must cover

1. All 11 check categories above with concrete implementation patterns.
2. How each check integrates into the existing `ba_audit_runner.py`
   runner and `ba_audit_manifest.json` registration.
3. Worker isolation: which checks run in the existing process vs. the
   SPEC_0007 subprocess worker (runtime checks requiring a live Qt window
   must run in the worker; static checks can run in the runner).
4. Check ID scheme: `BA-RUNTIME-VELLUM-NNN` for Vellum-specific checks.
5. Evidence requirements: each FAIL must include widget class, object
   name, measured value, expected value, and a screenshot of the
   offending state where applicable.
6. Gate behavior: which checks are hard-fail gates vs. warnings.
   Crashes (#228), Bible violations (#229), and elision (#220) are
   hard-fail. Layout/content issues are warnings pending design lock.
7. Relationship to SPEC_0007: which checks are new probes WITHIN the
   SPEC_0007 Vellum registration, and which are new scanners.
8. Unit test coverage for the new check logic (not just happy-path).
9. No real patient data, no production mailbox writes during probes.
10. All checks must be reproducible on a headless display (`offscreen`
    QPA platform) or explicitly noted as requiring a real display with
    documented reason.

### Must not

- Duplicate checks already in SPEC_0007 without extension.
- Require production-code changes in Vellum to enable the checks.
- Produce false positives on the existing BA 86-warning baseline.
- Use hardcoded hex colors — compare against Bible palette tokens only.

---

## Self-review requirement

Apply your standard self-review protocol (3-pass minimum, 9-pass
maximum). Report each pass result. Do not deliver until Pass N finds
zero significant issues.

---

## Delivery

1. Assign `SPEC_0008` (next ID per SPEC_INDEX.md).
2. Write spec to `workflows/specs/SPEC_0008_ba_runtime_vellum_missed_bugs_v1.md`.
3. Update `workflows/specs/SPEC_INDEX.md` to add the row.
4. File the spec directly to CC Inbox:
   `C:\panda-gallery\workflows\cc_mailbox\CC Inbox\`
   with subject: "SPEC READY — SPEC_0008 BA runtime missed-bug checks;
   research thoroughly and implement per spec."
5. File a brief notification to CD inbox:
   `C:\panda-gallery\workflows\cc_mailbox\CLAUDE Inbox\`
   confirming spec delivered and the SPEC_INDEX updated.
6. Status `APPROVED` in frontmatter — this dispatch constitutes
   CD authorization. CD review is waived per BA carve-out.

— CD
