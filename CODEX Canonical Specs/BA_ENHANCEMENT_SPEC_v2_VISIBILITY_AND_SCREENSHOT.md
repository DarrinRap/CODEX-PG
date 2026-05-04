# BA Enhancement Spec v2 — State-Conditional Visibility Scanner + Screenshot Baseline Comparison

Status: Draft for Darrin review
Date: 2026-05-03
Owner: Codex
Scope: Two new BA scanners targeting the classes of bugs BA currently cannot detect
Output path: `C:\CODEX PG\CODEX Canonical Specs\BA_ENHANCEMENT_SPEC_v2_VISIBILITY_AND_SCREENSHOT.md`

Reference artifacts:
- `C:\panda-gallery\workflows\design\BA_RUNBOOK_v1.2.md`
- `C:\panda-gallery\workflows\design\BA_APP_REGISTRY_SPEC_v1.2.1.md`
- `C:\panda-gallery\workflows\design\BA_RUNTIME_CHECK_PACK_SPEC_v1.3.md`
- `C:\panda-gallery\scripts\ba_audit_runner.py`
- `C:\panda-gallery\workflows\design\ba_audit_manifest.json`
- `C:\panda-gallery\relay\developer_hub.py` (evidence source for V-scanner rules)
- `C:\panda-gallery\workflow_capture.py` (mss screenshot infrastructure reference)

---

## 1. Executive Summary

BA v1.2 finds structurally unwired buttons and design-lint violations. It cannot find:

1. Widgets that are `setEnabled(False)` when they should be `setVisible(False)` — producing ghost outlines, phantom interactive affordances, or layout artifacts when the app is in a no-selection state.
2. Visual regressions — layout changes, clipping, background bleeds, or shifted elements — that are invisible to any static scanner but immediately obvious to a human eye.

Both gaps were confirmed this session. Bug #187 (Archive button ghost outline) would have been caught by scanner 1. Bugs #185 (Captured pill clipped) and #186 (dark area below report list) would have been caught by scanner 2.

This spec adds two scanners to BA:

- **`visibility_state_scanner`** — static analysis of state-conditional visibility patterns in registered Python source files.
- **`screenshot_baseline`** — runtime screenshot capture and pixel-level comparison against stored approved baselines.

---

## 2. Problem Statement

### 2.1 Visibility Gap

BA's `action_feedback_static` scanner checks whether every interactive widget has a `.connect()` call, a tooltip, or an explicit `setEnabled(False)` call. It treats `setEnabled(False)` as correct UX — the widget is accounted for.

This is insufficient. `setEnabled(False)` makes a widget non-interactive but leaves it visible. When a widget's QSS `:disabled` rule has a visible border (which is correct for most secondary buttons that remain anchored in the layout), the disabled widget occupies visual space and may render as a ghost affordance even when it has no meaningful context.

The correct pattern for context-dependent widgets — those that only exist when a specific piece of data is selected — is `setVisible(False)` in the no-data state and `setVisible(True)` when data is present. `setEnabled(False)` is correct only for permanently visible widgets whose enabled state depends on data.

Concrete evidence: `relay/developer_hub.py` `_rp_archive_btn` uses `setEnabled(False)` in init and `setEnabled(True)` on report selection, but never calls `setVisible`. Its `:disabled` QSS rule has `border: 1px solid RELAY_COLOR_BORDER_SOFT` which renders as a visible ghost border at the bottom of the Relay window when no report is selected. This is Bug #187 and it was shipped in v4.88.0 without detection.

### 2.2 Visual Regression Gap

Static analysis cannot observe rendered output. Three bugs found in this session are in this class:

- **#185**: "Captured" filter pill text clipped at right edge of chip row. The QSS and Python source are both structurally correct; the bug manifests when the window is at certain widths.
- **#186**: Report list scroll area shows raw dark background below sparse content. A pre-existing layout characteristic that worsens at small report counts.
- **#187**: Ghost button outline (also has a static detection path via scanner 1).

The only structural path to automated detection of this class of bug is comparing rendered screenshots against approved baselines. Any pixel-level delta that exceeds a threshold is a candidate finding.

### 2.3 Evidence From 311 Parked Failures

BA's most recent full-app audit of Panda Gallery produced 311 action-feedback findings. These are parked because the signal-to-noise ratio is too low — too many are heuristic false positives where a widget IS handled via an ancestor signal or event filter that BA's static scanner cannot trace.

The visibility scanner defined here is more precise than action-feedback-static for the ghost-widget class, and will produce fewer false positives because it looks for a specific structural mismatch (enabled-only vs. visible-toggling) rather than a simple absence of `.connect()`.

The screenshot baseline scanner provides a complementary truth surface: when a visual change occurs, BA can report it with pixel-level evidence regardless of whether any Python source changed.

---

## 3. Goals

1. Detect QPushButton, QLabel, QFrame, and QWidget subclass instances that use `setEnabled(False)` as their only state guard when context-dependent hiding (`setVisible(False)`) is the correct pattern.
2. Detect QSS `:disabled` rules on context-dependent buttons that have a non-transparent visible border, which produces ghost outlines.
3. Capture screenshots of registered app primary states when the app is running and compare against stored approved baselines.
4. Report visual diffs as BA findings with pixel-level evidence (diff image, changed region bounding box, changed pixel count and percentage).
5. Allow Darrin to approve a new screenshot as the baseline from the BA UI with a single click.
6. Integrate both scanners cleanly into the existing BA manifest, runner, report model, and UI without breaking any existing behavior.
7. Keep both scanners honest: visibility scanner does not claim to find all ghost widgets (it finds the structural pattern), and screenshot scanner does not claim to find all visual bugs (it finds deviations from approved baselines).

---

## 4. Non-Goals

4.1 The visibility scanner does not replace `action_feedback_static`. Both run independently and may flag the same widget for different reasons.

4.2 The visibility scanner does not do runtime widget inspection. It does not launch PG, does not introspect Qt objects at runtime, and does not interact with the running app.

4.3 The screenshot scanner does not do OCR or semantic understanding of the captured screenshots. It does pixel-level comparison only.

4.4 The screenshot scanner does not capture screenshots automatically without the app running. If the app is not running, the scanner reports UNKNOWN for each registered state and skips the diff.

4.5 The screenshot scanner does not auto-approve baselines. Every new baseline must be explicitly approved by Darrin via the BA UI.

4.6 Neither scanner replaces manual visual inspection. Both augment it.

4.7 This spec does not change or fix the 311 parked action-feedback findings. That triage belongs to a separate handler-trace pass.

4.8 This spec does not add Playwright or browser automation. Screenshot capture uses `mss` against the live PG native window. Browser-based targets (like BA itself) have limited screenshot support in v2.0 per §10 step 14.

---

## 5. Feature A: State-Conditional Visibility Scanner

### 5.1 Overview

Scanner name (canonical): `visibility_state_scanner`

Runner integration: `ba_audit_runner.py` calls `run_visibility_state_scanner(target)` where `target` is the full manifest target dict. The function reads `target["paths"]` for source files and `target.get("visibility_scanner_config", {})` for config overrides. It returns a list of BA finding dicts in the standard schema.

The scanner reads Python source files as text (no import, no exec). It uses regex and AST parsing to identify the structural patterns described in Rules V01–V05 below.

### 5.2 Structural Patterns The Scanner Detects

The scanner looks for a two-part mismatch:

**Part A — Init pattern:** A QPushButton (or QLabel, QFrame, QWidget, or any of their subclasses) that calls `setEnabled(False)` inside a `__init__`, `_build_*`, or `_setup_*` method (the build-time guard), but has NO corresponding `setVisible(False)` call in ANY method of the same class.

**Part B — QSS pattern:** The same widget's `objectName` appears in a QSS block that has `border:` or `border-left:` or `border-right:` or `border-bottom:` or `border-top:` with a non-transparent, non-zero value inside a `:disabled` selector.

When both Part A and Part B match for the same widget, the scanner emits a V01 finding.

The scanner also defines four additional rules that do not require both parts:

### 5.3 Detection Rules

**Rule interaction:** Rules V01–V05 are independent. A single widget may match multiple rules and will generate a finding for each. All findings for the same widget include the same `objectName` in their evidence dict, allowing the BA report to group them if desired. There is no automatic suppression of lower-confidence rules (V03, V04) when a higher-confidence rule (V01, V05) already fired for the same widget.

**Rule V01 — Enabled-only guard with visible disabled border (HIGH confidence)**

Trigger: A widget is `setEnabled(False)` in its build method with no paired `setVisible(False)` anywhere in the class, AND its objectName appears in a QSS `:disabled` block with a non-transparent border.

Severity: WARN

Rationale: This is the exact pattern that produced Bug #187. The widget will render a ghost border outline when the app is in the no-data state. The correct fix is either (a) add `setVisible(False)` in the no-selection state and `setVisible(True)` on selection, or (b) change the `:disabled` QSS to use `border: none` or `border: 1px solid transparent`.

Example match in `relay/developer_hub.py`:
```python
# In _build_right_panel():
self._rp_archive_btn = QPushButton("Archive")
self._rp_archive_btn.setObjectName("relayFooterArchive")
self._rp_archive_btn.setEnabled(False)
# ... no setVisible(False) anywhere in RelayDeveloperHub
```
```
# In relay_footer_qss():
QPushButton#relayFooterArchive:disabled {{
    color: {RELAY_COLOR_TEXT_DIM};
    border: 1px solid {RELAY_COLOR_BORDER_SOFT};   <-- non-transparent
}}
```

**Rule V02 — Context-dependent tooltip with enabled-only guard (MEDIUM confidence)**

Trigger: A widget's `.setToolTip(...)` call contains at least one of the following phrases: `"this report"`, `"selected"`, `"current"`, `"the active"`, `"move this"`, `"archive this"`, `"delete this"`, `"restore this"`, and the widget uses `setEnabled(False)` with no `setVisible(False)` in the same class.

Severity: WARN

Rationale: A tooltip that references "this report" or "selected" implies the widget is only meaningful when a specific data item is selected. Such widgets should toggle visibility with the selection, not just enabled state. Context-dependent tooltips are a reliable textual signal of this pattern.

False positive mitigation: exclude widgets whose tooltip contains `"will be available"` or `"coming soon"` or `"future"` — these are intentionally-disabled future features that should remain visible as stubs.

**Rule V03 — Paired enable-toggle without visibility-toggle (MEDIUM confidence)**

Trigger: A class has at least two methods where the same widget is `setEnabled(True)` in one method and `setEnabled(False)` in another (a toggle pattern), but `setVisible` is never called on the same widget in any method of the class.

Severity: INFO

Rationale: An enabled-toggle without a visibility-toggle is sometimes correct (a submit button that activates when form is valid) and sometimes wrong (an Archive button that should disappear when nothing is selected). V03 flags the pattern for human review without asserting it is always a bug.

False positive mitigation: exclude widgets whose parent container is itself toggled (if the parent QWidget is hidden, child visibility is implicitly managed). The scanner performs a best-effort check: if the `_build_*` method that creates the widget also calls `col.addWidget(widget)` or `layout.addWidget(widget)` where `col` or `layout` is assigned to a variable that has `setVisible` called on it anywhere in the class, V03 is suppressed for that widget. This check may miss cases where the parent container is determined dynamically at runtime; in those cases a `# ba-vis:ignore V03` suppression comment is the correct resolution.

**Rule V04 — QSS ghost border on disabled widget not in permanent toolbar (LOW confidence)**

Trigger: A QSS `:disabled` block for any objectName has `border:` with a non-transparent value, AND the objectName is NOT in a list of known-permanent-toolbar widgets (i.e., widgets that are always visible in the UI regardless of data state). Known-permanent-toolbar objectNames are registered in the manifest target's `permanent_widgets` list (see §5.6).

Severity: INFO

Rationale: Not every disabled widget with a border is a ghost bug. Toolbar buttons that are always visible (like a Back button that disables on the first page) are correctly disabled with a visible border. V04 is a broad sweep that requires human judgment to distinguish real ghost bugs from legitimate disabled states.

False positive mitigation: the `permanent_widgets` manifest field lets Darrin explicitly exclude known-correct cases without code changes.

**Rule V05 — Missing setVisible pairing in selection handler (HIGH confidence)**

Trigger: A class has a method whose name matches one of the glob patterns `_on_*_selected`, `_on_*_clicked`, `_refresh_*`, or `_update_*` (matched via `fnmatch.fnmatch` against the method name) that calls `setEnabled(True)` on a widget, but the complementary deselection handler (a method that calls `setEnabled(False)` on the same widget) does NOT call `setVisible(False)`.

Severity: WARN

Rationale: Selection handlers that enable a widget should also show it; deselection handlers that disable a widget should also hide it. If only enabled state is managed and not visibility, the widget will linger visually when deselected.

False positive mitigation: if the class has ANY call to `setVisible` anywhere (even on a different widget), V05 confidence is demoted to INFO, because the class author is aware of visibility management and may have made a deliberate choice.

### 5.4 Source Parsing Strategy

The scanner operates in two phases:

**Phase 1 — AST extraction:**
For each Python source file in the target's `paths` list, the scanner calls `ast.parse()` and walks the AST to extract:
- Class definitions and their method trees
- All `setEnabled(False)` and `setEnabled(True)` call sites, with the attribute name of the target object (e.g., `self._rp_archive_btn`)
- All `setVisible(False)` and `setVisible(True)` call sites, with the same attribute name
- All `.setObjectName(...)` calls mapping attribute names to string objectNames
- All `.setToolTip(...)` calls with their string content

If `ast.parse()` fails for a file (syntax error, encoding issue), the scanner emits one UNKNOWN finding per file using the format `BA-VIS-<APP_SLUG>-PARSE-<filename_stem>` (e.g., `BA-VIS-RELAY_HUB-PARSE-developer_hub`) as defined in §5.5.

**Phase 2 — QSS text scan:**
The scanner performs a text scan (not AST) over the same source files to extract QSS strings. QSS in PG is generated by methods named `*_qss()` or `*_stylesheet()` or assigned to string variables containing `QPushButton#`. The scanner uses regex to extract `objectName#... :disabled { ... }` blocks and checks each for non-transparent border values.

Non-transparent border values are any value that is NOT:
- `transparent`
- `none`
- `0`
- `0px`

A border value that uses a color variable (e.g., `{RELAY_COLOR_BORDER_SOFT}`) is treated as non-transparent because the scanner cannot resolve the variable at static analysis time. This may produce false positives for variables that resolve to transparent, but that case is unusual in PG's design system.

### 5.5 Finding Format

Each finding follows the standard BA finding schema. Example:

```json
{
  "check_id": "BA-VIS-RELAY_HUB-0001",
  "app": "Relay Hub",
  "scanner": "visibility_state_scanner",
  "rule": "V01",
  "severity": "warn",
  "title": "relayFooterArchive: setEnabled-only guard with visible :disabled border",
  "message": "QPushButton#relayFooterArchive is setEnabled(False) in _build_right_panel but has no setVisible call anywhere in RelayDeveloperHub. Its :disabled QSS rule has a non-transparent border (border: 1px solid ...). This will render a ghost outline when no report is selected.",
  "evidence": {
    "source_file": "relay/developer_hub.py",
    "build_method": "_build_right_panel",
    "line_setEnabled": 978,
    "objectName": "relayFooterArchive",
    "qss_method": "_relay_footer_qss",
    "qss_disabled_border": "border: 1px solid {RELAY_COLOR_BORDER_SOFT}",
    "setVisible_found": false
  },
  "recommendation": "Call self._rp_archive_btn.setVisible(False) in the no-selection state and setVisible(True) when a report is selected. Alternatively, change the :disabled QSS border to 'border: 1px solid transparent' if the button must remain in the layout when inactive."
}
```

Check ID format: `BA-VIS-<APP_SLUG>-<NNNN>` where APP_SLUG is the app name uppercased with spaces replaced by underscores (e.g., `RELAY_HUB`), and NNNN is a 4-digit sequential number per run. The example above should read `BA-VIS-RELAY_HUB-0001` for a target named `Relay Hub`. Parse-failure findings use the special non-sequential format `BA-VIS-<APP_SLUG>-PARSE-<filename_stem>` (e.g., `BA-VIS-RELAY_HUB-PARSE-developer_hub`) to distinguish them from rule-based findings.

### 5.6 Manifest Integration

The `visibility_state_scanner` scanner name is added to the allowed scanner set in `ba_audit_manifest.json`.

Manifest target fields added by this scanner:

```json
{
  "name": "Relay Hub",
  "paths": ["${repo_root}/relay/developer_hub.py", "${repo_root}/relay/hub_components.py"],
  "scanners": ["app_inventory", "action_feedback_static", "visibility_state_scanner"],
  "visibility_scanner_config": {
    "permanent_widgets": ["relayTabStrip", "relayModuleHeader", "relayDevHeader"],
    "tooltip_context_phrases": ["this report", "selected", "current"],
    "exclude_files": []
  }
}
```

`permanent_widgets` (optional, default `[]`): list of objectName strings for widgets that are always visible regardless of data state. V04 suppresses findings for these names. The list is manually maintained by Darrin or CD.

`tooltip_context_phrases` (optional, default: the V02 phrase list in §5.3): override the phrase list for V02 matching per target. Useful when an app uses different wording.

`exclude_files` (optional, default `[]`): list of relative paths within the target's `paths` list to skip entirely. Useful for generated or third-party files.

### 5.7 Suppression Comments

Individual findings can be suppressed in source code via inline comments. A line ending with `# ba-vis:ignore` suppresses all V-scanner findings originating from that line. A line ending with `# ba-vis:ignore V01` suppresses only V01 findings from that line.

Suppression comments are scanned as text (not AST) after Phase 1. The scanner records the suppression in the finding's `suppressed` field and excludes the finding from fail/warn counts but includes it in the evidence log for auditability.

---

## 6. Feature B: Screenshot Baseline Comparison

### 6.1 Overview

Scanner name (canonical): `screenshot_baseline`

The screenshot baseline scanner captures screenshots of registered app states using `mss` (the same library used by `workflow_capture.py`) and compares them pixel-by-pixel against stored approved baseline images. Deviations above a configurable threshold are reported as BA findings.

The scanner operates in two modes:

**Capture mode** (`--screenshot-capture`): capture screenshots of all registered states for a target and write them as pending baselines. Darrin reviews pending baselines in the BA UI and approves or rejects each.

**Compare mode** (default, runs automatically when `screenshot_baseline` is in the scanner list): load the approved baseline for each registered state, capture a fresh screenshot, diff, and emit findings for any state with pixel delta above threshold.

### 6.2 State Registry

Each manifest target that includes `screenshot_baseline` must define a `screenshot_states` list. Each state entry defines one screen configuration the scanner will capture and compare.

```json
{
  "name": "Relay Hub",
  "scanners": ["app_inventory", "action_feedback_static", "screenshot_baseline"],
  "screenshot_states": [
    {
      "state_id": "all_reports_empty",
      "label": "All Reports — empty (no reports)",
      "window_title_contains": "Relay",
      "baseline_path": "${repo_root}/workflows/design/ba_baselines/relay_hub/all_reports_empty.png",
      "capture_region": "window",
      "threshold_pct": 0.5
    },
    {
      "state_id": "all_reports_populated_no_selection",
      "label": "All Reports — 2+ reports, none selected",
      "window_title_contains": "Relay",
      "baseline_path": "${repo_root}/workflows/design/ba_baselines/relay_hub/all_reports_populated_no_selection.png",
      "capture_region": "window",
      "threshold_pct": 1.0
    },
    {
      "state_id": "all_reports_selected",
      "label": "All Reports — report selected, right panel populated",
      "window_title_contains": "Relay",
      "baseline_path": "${repo_root}/workflows/design/ba_baselines/relay_hub/all_reports_selected.png",
      "capture_region": "window",
      "threshold_pct": 1.0
    }
  ]
}
```

**State entry fields:**

`state_id` (required): unique string identifier within the target. Used as the finding check_id suffix and the baseline filename key.

`label` (required): human-readable description of the screen state. Used in the BA UI and findings.

`window_title_contains` (required): substring that must appear in the window title of the running app. Used by the scanner to locate the correct window via `mss.mss().monitors` and platform window enumeration (see §6.3).

`baseline_path` (required): absolute or `${repo_root}`-relative path to the PNG baseline image. If the file does not exist, the scanner treats this state as UNKNOWN (no baseline registered) and emits an UNKNOWN-severity finding (consistent with §6.5 UNKNOWN finding format).

`capture_region` (required): one of `"window"` (capture the full window bounding box), `"left_rail"` (left half of the window), `"right_panel"` (right half of the window). Additional named regions can be added in future versions. For v2.0, only `"window"` is required. `"left_rail"` and `"right_panel"` are MUST-NOT-CRASH but may fall back to `"window"` with a log warning if the window layout cannot be split reliably.

`threshold_pct` (required): the percentage of pixels that must differ before a finding is emitted. A value of `0.5` means 0.5% of total pixels must differ. Lower values are more sensitive. The default for new states is `1.0`. Darrin can lower the threshold for high-fidelity states (e.g., the empty state where nothing should ever change) and raise it for states with dynamic content (e.g., timestamps).

### 6.3 Window Discovery

The scanner discovers the target window using the following strategy:

1. Enumerate all open windows on the current desktop using `pygetwindow` (import as `import pygetwindow as gw`). This is a Windows-specific library; the scanner is Windows-only in v2.0, consistent with PG's Windows-only deployment. If `pygetwindow` is not installed, do NOT fall back to `win32gui` (which would require an unlisted `pywin32` dependency) — instead emit the library-missing UNKNOWN finding and skip all states for this target.
2. Filter windows by `window_title_contains`. If zero matches: emit UNKNOWN finding (`app not running — cannot compare`). If multiple matches: use the most recently focused window (sort by z-order if available, otherwise use the first match).
3. Obtain the window bounding box (left, top, width, height) in screen coordinates.
4. Use `mss.mss().grab({"left": left, "top": top, "width": width, "height": height})` to capture the window region.
5. Convert the captured image to a PIL Image for comparison.

If `mss` or `pygetwindow` cannot be imported, the scanner emits one UNKNOWN finding for the entire target (not per state) with title `screenshot_baseline: required library not available — install mss and pygetwindow` and a note that all N registered states were skipped. This avoids N identical library-missing findings cluttering the report.

### 6.4 Pixel-Level Comparison

For each state, the scanner:

1. Loads the approved baseline PNG as a PIL Image in RGBA mode.
2. Captures the current screenshot as a PIL Image in RGBA mode.
3. Resizes the captured image to match the baseline dimensions if they differ (using `PIL.Image.LANCZOS`). A size mismatch of more than `resize_tolerance_pct`% (default: 10%, configurable via `screenshot_scanner_config.resize_tolerance_pct`) in either dimension is itself a finding (`BA-SS-<APP_SLUG>-<NNNN>: window size changed — baseline was WxH, current is WxH`), emitted at WARN severity before the pixel comparison.
4. Computes the absolute per-pixel difference using `PIL.ImageChops.difference()`.
5. Converts the difference image to grayscale and thresholds at value 15 (out of 255) to ignore JPEG/PNG compression artifacts and sub-pixel anti-aliasing noise.
6. Counts the number of pixels above the threshold.
7. Computes `changed_pct = (changed_pixels / total_pixels) * 100`.
8. If `changed_pct > threshold_pct`: emit a FAIL finding (see §6.5).
9. Saves the diff image to `${repo_root}/workflows/design/ba_baselines/<app_slug>/<state_id>_diff_latest.png` for the BA UI to display.
10. Saves the current screenshot to `${repo_root}/workflows/design/ba_baselines/<app_slug>/<state_id>_current_latest.png` for side-by-side display in the BA UI.

The diff image uses the standard visual diff rendering: pixels above threshold are colored red, pixels below threshold are darkened (multiplied by 0.3) to recede.

### 6.5 Finding Format

```json
{
  "check_id": "BA-SS-RELAY_HUB-0001",
  "app": "Relay Hub",
  "scanner": "screenshot_baseline",
  "state_id": "all_reports_populated_no_selection",
  "severity": "fail",
  "title": "Visual regression: all_reports_populated_no_selection — 3.2% pixels changed",
  "message": "Screenshot of 'All Reports — 2+ reports, none selected' differs from approved baseline by 3.2% (threshold: 1.0%). Changed region is concentrated in the lower portion of the window (y: 680–740).",
  "evidence": {
    "baseline_path": "workflows/design/ba_baselines/relay_hub/all_reports_populated_no_selection.png",
    "current_screenshot_path": "workflows/design/ba_baselines/relay_hub/all_reports_populated_no_selection_current_latest.png",
    "diff_image_path": "workflows/design/ba_baselines/relay_hub/all_reports_populated_no_selection_diff_latest.png",
    "baseline_dimensions": [1100, 700],
    "current_dimensions": [1100, 700],
    "changed_pixels": 22400,
    "total_pixels": 770000,
    "changed_pct": 3.2,
    "changed_region_bbox": [0, 680, 1100, 740],
    "threshold_pct": 1.0
  },
  "recommendation": "Review the diff image. If the change is intentional (new feature, approved redesign), run BA in capture mode and approve the new screenshot as the baseline. If the change is a regression, fix the layout and re-run."
}
```

Check ID format: `BA-SS-<APP_SLUG>-<NNNN>`.

UNKNOWN findings (app not running, no baseline registered, library missing):

```json
{
  "check_id": "BA-SS-RELAY_HUB-0002",
  "app": "Relay Hub",
  "scanner": "screenshot_baseline",
  "state_id": "all_reports_empty",
  "severity": "unknown",
  "title": "No baseline registered: all_reports_empty",
  "message": "No approved baseline PNG found at workflows/design/ba_baselines/relay_hub/all_reports_empty.png. Run BA in capture mode (--screenshot-capture) with the app in the correct state, then approve the baseline in the BA UI.",
  "evidence": {
    "expected_baseline_path": "workflows/design/ba_baselines/relay_hub/all_reports_empty.png",
    "baseline_exists": false
  },
  "recommendation": "Put the Relay Hub in the 'all_reports_empty' state, then run: python scripts/ba_audit_runner.py --app 'Relay Hub' --screenshot-capture --state all_reports_empty. Open the BA UI and approve the captured screenshot."
}
```

### 6.6 Baseline Registration Flow

**Step 1 — Capture:** Darrin puts the app in the target state manually. He then runs:

```powershell
cd C:\panda-gallery
python scripts\ba_audit_runner.py --app "Relay Hub" --screenshot-capture --state all_reports_empty
```

The runner captures a screenshot, saves it to `workflows/design/ba_baselines/relay_hub/all_reports_empty_pending.png`, and reports: `Pending baseline saved. Open BA UI to approve.`

**Step 2 — Review and approve:** Darrin opens the BA UI. In the Screenshot Baselines panel (new sidebar section, see §7.3), he sees the pending screenshot alongside the state label. He clicks `Approve as baseline`. The UI calls `POST /api/screenshot/approve` with body `{"app": "Relay Hub", "state_id": "all_reports_empty"}`. The runner renames `<state_id>_pending.png` to the canonical path `<state_id>.png` atomically (write temp file + rename). The API returns `{"ok": true, "baseline_path": "..."}` on success.

**Step 3 — Verification:** Darrin runs the normal BA audit. The `screenshot_baseline` scanner loads the approved baseline and emits PASS for that state (assuming the app is still in the same visual state).

**Rejection flow:** If Darrin clicks `Reject` on a pending baseline, the pending file is deleted and the state remains UNKNOWN. No change to the approved baseline (if one existed before).

**Update flow:** When the UI is intentionally changed (new feature, approved redesign), Darrin must update the baseline. He re-runs the capture step. The new capture is saved as `_pending.png` alongside the existing approved baseline. The BA UI shows a side-by-side comparison of old baseline vs. pending. Darrin clicks `Approve — replace baseline` to update.

### 6.7 Capture Mode CLI Reference

```powershell
# Capture all states for a target (app must be running)
python scripts\ba_audit_runner.py --app "Relay Hub" --screenshot-capture

# Capture a specific state only
python scripts\ba_audit_runner.py --app "Relay Hub" --screenshot-capture --state all_reports_empty

# List all registered states for a target
python scripts\ba_audit_runner.py --app "Relay Hub" --list-states

# List all pending baselines awaiting approval (all targets)
python scripts\ba_audit_runner.py --list-pending-baselines
```

### 6.8 Baseline Storage

All baseline images and diff artifacts are stored under:
`${repo_root}/workflows/design/ba_baselines/<app_slug>/`

Where `app_slug` is the app name lowercased with spaces replaced by underscores (e.g., `relay_hub`).

File naming conventions:
- Approved baseline: `<state_id>.png`
- Pending baseline: `<state_id>_pending.png`
- Latest captured screenshot: `<state_id>_current_latest.png`
- Latest diff image: `<state_id>_diff_latest.png`

The `ba_baselines/` directory is tracked in git. Approved baseline PNGs are committed as part of the design artifact record. Pending, current_latest, and diff_latest files are excluded from git via `.gitignore` pattern `workflows/design/ba_baselines/**/*_pending.png`, `workflows/design/ba_baselines/**/*_latest.png`.

The `.gitignore` additions must be made in the same commit that ships this scanner.

### 6.9 Manifest Integration

New manifest target fields for `screenshot_baseline`:

```json
{
  "name": "Relay Hub",
  "scanners": ["app_inventory", "action_feedback_static", "visibility_state_scanner", "screenshot_baseline"],
  "screenshot_states": [ ... ],
  "screenshot_scanner_config": {
    "pixel_diff_threshold_value": 15,
    "resize_tolerance_pct": 10,
    "diff_highlight_color": [255, 0, 0, 255],
    "diff_darken_factor": 0.3
  }
}
```

`screenshot_scanner_config` is optional. All fields have the defaults shown in §6.4. Darrin can override per-target defaults here without touching source code.

---

## 7. Shared Infrastructure

### 7.1 Scanner Registry

`ba_audit_runner.py` maintains a `SCANNER_REGISTRY` dict mapping scanner name strings to runner functions. The following additions are required:

```python
SCANNER_REGISTRY = {
    "app_inventory": run_app_inventory_scanner,
    "pg_design_lint": run_pg_design_lint_scanner,
    "action_feedback_static": run_action_feedback_static_scanner,
    "runtime_check_pack": run_runtime_check_pack_scanner,
    "visibility_state_scanner": run_visibility_state_scanner,   # NEW
    "screenshot_baseline": run_screenshot_baseline_scanner,      # NEW
}
```

The manifest validation layer must be updated to accept both new scanner names. Unknown scanner names continue to produce a manifest validation error, not a silent skip.

### 7.2 Report Model

The existing BA report model is extended minimally:

- `screenshot_baseline` findings contribute to `fail`, `warn`, `unknown`, and `pass` totals using the same counting rules as all other scanners.
- `visibility_state_scanner` findings with severity `warn` contribute to the existing `warn` total. Findings with severity `info` are included in the evidence log and findings list but do NOT contribute to `fail`, `warn`, or `unknown` counts — they are advisory only. If the existing BA report model has no `info` count field, Codex must add one (default 0) without changing existing count semantics.
- The evidence score formula is unchanged. Screenshot baseline PASS findings contribute to `evidenced` count. UNKNOWN findings do not.

### 7.3 BA UI Changes

Three UI additions are required in `PG_Design_Bible_Audit_v1.html`:

**7.3.1 Screenshot Baselines Panel**

A new collapsible section in the left sidebar, below `Register App`, labeled `Screenshot Baselines`. The panel is visible only when a target with `screenshot_baseline` scanner is selected.

Contents:
- List of registered states for the selected target
- Per-state: state label, baseline status (Approved / Pending / No baseline), last-capture timestamp
- `Capture now` button: disabled if the target app is not detected as running; enabled when the window title match is found (poll every 5 seconds via `GET /api/screenshot/status?app=<app_name>`)
- `Review pending` link: navigates to the pending baseline review modal

`GET /api/screenshot/status?app=<app_name>` returns `{"ok": true, "app_running": bool, "pending_states": ["state_id1", ...]}`. The `app_running` field is determined by calling the same window-title-match logic used in §6.3. This endpoint is lightweight (no screenshot capture) and safe to poll.

**7.3.2 Pending Baseline Review Modal**

A full-width modal dialog that opens when Darrin clicks `Review pending` or when a UNKNOWN screenshot finding is clicked in the report.

Contents:
- State label and state_id
- Full-size pending screenshot image (scrollable if larger than viewport)
- Side-by-side comparison if a prior approved baseline exists: `[Baseline] [Pending]` with a toggle to overlay or diff
- `Approve as baseline` button (primary, accent-colored)
- `Reject` button (secondary)
- `Capture again` button (secondary, captures a new pending screenshot for the same state)

**7.3.3 Findings Card Enhancement**

Screenshot baseline FAIL findings in the report card show an inline thumbnail of the diff image (max height 120px, full width). Clicking the thumbnail opens the pending baseline review modal.

Visibility scanner findings in the report card show the source file path, the line number of the `setEnabled(False)` call, and the QSS objectName, formatted as a code block.

### 7.4 CLI Runner Version

The runner version is bumped to `2.0.0` upon shipping this spec. If v1.3 (`runtime_check_pack`) has not shipped when this spec is implemented, Codex must ship v1.3 first (or include it in the same ship), then bump to `2.0.0`. The version string is used in BA self-check tests and report headers.

### 7.5 Help Menu Updates

The BA Help menu `Scanners` section adds:

```
visibility_state_scanner — Static analysis of enabled/visible state mismatches in Python source files.
  Rules: V01 (enabled-only + visible border), V02 (context tooltip + no visibility toggle),
         V03 (paired enable toggle without visibility toggle), V04 (ghost border sweep),
         V05 (selection handler mismatch).
  Suppression: append # ba-vis:ignore or # ba-vis:ignore V01 to the source line.

screenshot_baseline — Pixel-level comparison against approved baseline screenshots.
  Requires: mss, pygetwindow, pillow.
  Limitations: requires target app to be running; does not launch the app; does not do semantic understanding.
  Capture: python scripts/ba_audit_runner.py --app "..." --screenshot-capture [--state <state_id>]
  Approve: open BA UI → Screenshot Baselines panel → Review pending.
```

---

## 8. Dependencies

### 8.1 New Python Libraries

`mss` is believed to be in `requirements.txt` (used by `workflow_capture.py`). Codex must verify this in the §11 pre-implementation checklist before assuming no new dependency. If `mss` is absent, add it at the same version already used by `workflow_capture.py`.

`pygetwindow` is NOT currently in `requirements.txt`. It must be added:
```
pygetwindow>=0.0.9
```

`Pillow` is NOT currently in `requirements.txt`. It must be added:
```
Pillow>=10.0.0
```

If either library is missing at runtime, the `screenshot_baseline` scanner emits one UNKNOWN finding per target (not per state) noting that all states were skipped, then continues. It does not crash the runner.

`ast` is a Python standard library module. No new dependency for the visibility scanner.

### 8.2 Existing Libraries Used

`re` (standard library) — regex scanning for QSS blocks.
`pathlib` (standard library) — path resolution.
`json` (standard library) — manifest reading.
`mss` — screenshot capture.

---

## 9. Acceptance Criteria

**A1.** `python -m py_compile scripts/ba_audit_runner.py` passes with no errors.

**A2.** `python -m pytest tests/test_ba_audit_runner.py -q` passes, including new tests for V01-V05 rules and screenshot baseline scanner.

**A3.** Running BA on the `Bible Audit` target produces zero FAIL findings from `visibility_state_scanner` (Bible Audit's registered paths contain only HTML, not Python; the scanner must handle this gracefully by emitting zero findings rather than crashing or emitting false positives). For `screenshot_baseline`, Bible Audit screenshot capture targets a browser window (not a native PySide window) — the `window_title_contains` field must match the browser tab title. If browser-window capture is not reliable with `pygetwindow`, the Bible Audit target may omit `screenshot_baseline` from its scanner list until browser screenshot support is explicitly added. A3 is satisfied if the runner completes without error for Bible Audit.

**A4.** Running BA on `Relay Hub` with `relay/developer_hub.py` in its current state (v4.88.0) produces at minimum one V01 WARN finding for `relayFooterArchive`.

**A5.** The BA UI shows the Screenshot Baselines panel when `Relay Hub` is selected.

**A6.** Running `--screenshot-capture` with the Relay Hub window open produces a pending PNG at the correct path.

**A7.** Approving a pending baseline via the BA UI moves the file to the canonical path and removes the `_pending` suffix.

**A8.** After baseline approval, running a normal BA audit with the app unchanged produces PASS for that state.

**A9.** After baseline approval, introducing an intentional visual change (e.g., temporarily widening a border) produces a FAIL finding with changed_pct above threshold and a saved diff image.

**A10.** All V-scanner findings include: check_id, app, scanner, rule, severity, title, message, evidence dict (with source_file, line_setEnabled, objectName, qss_disabled_border, setVisible_found), recommendation.

**A11.** All screenshot baseline findings include: check_id, app, scanner, state_id, severity, title, message, evidence dict (with baseline_path, current_screenshot_path, diff_image_path, baseline_dimensions, current_dimensions, changed_pixels, total_pixels, changed_pct, changed_region_bbox, threshold_pct), recommendation.

**A12.** The runner version string is `2.0.0`.

**A13.** `ba-vis:ignore` and `ba-vis:ignore V01` suppression comments work correctly — suppressed findings appear in the evidence log with `suppressed: true` and are excluded from fail/warn counts.

**A14.** The `permanent_widgets` manifest config suppresses V04 findings for listed objectNames.

**A15.** If `pygetwindow` or `Pillow` is not installed, `screenshot_baseline` emits one UNKNOWN finding per affected target (not per state) and the runner exits cleanly (no crash, no exception propagation).

**A16.** The `.gitignore` patterns for `*_pending.png` and `*_latest.png` under `ba_baselines/` are added in the same commit as the scanner code.

**A17.** The BA Help menu lists both new scanners with their rule sets, limitations, and CLI commands.

**A18.** Running `python scripts/ba_audit_runner.py --app "Relay Hub" --list-states` prints the registered state_ids and labels.

**A19.** Running `python scripts/ba_audit_runner.py --list-pending-baselines` prints all pending baselines across all targets.

**A20.** The BA self-check (`--app "Bible Audit"`) still exits with 0 fail after this spec is implemented.

---

## 10. Implementation Order

Codex should implement in this order to minimize risk and enable incremental testing:

1. **AST extraction utilities** — the Phase 1 parser for `setEnabled`, `setVisible`, `setObjectName`, `setToolTip` calls. Unit test with synthetic Python source strings.

2. **QSS text scanner** — the Phase 2 regex scanner for `:disabled` blocks with border values. Unit test with synthetic QSS strings.

3. **Rule V01** — the two-part match combining AST and QSS results. Unit test with a synthetic class that mirrors the `_rp_archive_btn` pattern.

4. **Rules V02, V03, V04, V05** — implement sequentially, unit test each.

5. **Runner integration** — wire `visibility_state_scanner` into `SCANNER_REGISTRY`, update manifest validation, update tests.

6. **Manifest update** — add `visibility_state_scanner` to the `Relay Hub` target in `ba_audit_manifest.json`. Verify A4.

7. **pygetwindow + Pillow dependencies** — add to `requirements.txt`, verify import-failure graceful degradation.

8. **Screenshot capture utility** — the mss window grab function. Test with a real running window.

9. **Pixel comparison engine** — the PIL diff, threshold, changed_pct, and bbox computation. Unit test with synthetic image pairs.

10. **`screenshot_baseline` scanner runner** — integrates capture utility + comparison engine + finding emitter. Wire into `SCANNER_REGISTRY`.

11. **Baseline registration flow** — `--screenshot-capture` CLI, pending file naming, `--list-states`, `--list-pending-baselines`.

12. **BA UI** — Screenshot Baselines panel, pending review modal, findings card thumbnail, Help menu updates.

13. **`.gitignore` additions** — add exclusion patterns for pending and latest files.

14. **Bible Audit baseline** — Bible Audit runs in a browser (not as a native window). If `pygetwindow` can reliably locate the browser tab showing BA, capture and commit the baseline. If browser-window location is unreliable, document this limitation and omit `screenshot_baseline` from the Bible Audit manifest entry for v2.0; native-window targets (Relay Hub, Panda Gallery, etc.) take priority. Verify A3 regardless.

15. **Relay Hub baselines** — Darrin manually captures and approves baselines for the registered Relay Hub states after the UI ships.

16. **Full test suite pass** — verify all 20 acceptance criteria.

---

## 11. Deep Review Checklist (Codex Self-Check Before Implementation)

Before writing any code, Codex must verify:

- [ ] `pygetwindow` version `>=0.0.9` is compatible with the current Python version in use (`python --version` in the repo environment). If not, document the alternative window-discovery strategy.
- [ ] `mss` version currently in `requirements.txt` supports the `grab(dict)` API used in §6.3. If a newer version is required, document the version bump.
- [ ] `ast.parse()` on `relay/developer_hub.py` (v4.88.0, ~3700 lines) completes without error. If the file uses any syntax not supported by the installed Python version, document.
- [ ] The `_relay_footer_qss()` method (or equivalent QSS source) is detectable by the Phase 2 QSS text scanner using the described regex. If QSS is generated differently, document the adaptation.
- [ ] No existing BA test asserts that `visibility_state_scanner` and `screenshot_baseline` are NOT in the allowed scanner set. If any test does, it must be updated.
- [ ] The `ba_baselines/` directory does not already exist in the repo. If it does, document its current contents and whether they conflict with this spec.

---

## 12. Limitations Acknowledgment

This spec does not claim omniscience. The limitations of each scanner must be preserved in the BA Help text and limitations section:

`visibility_state_scanner` limitations:
- Static analysis only. Cannot detect runtime-computed visibility patterns (e.g., visibility toggled by a lambda that calls a non-obvious method).
- QSS color variable resolution is not performed. Variables that resolve to transparent are treated as non-transparent.
- Does not detect ghost widgets whose parent container is toggled (V03 partially mitigates this).
- Does not detect rendering artifacts caused by Qt's own compositor (e.g., a widget that is `setVisible(False)` but still paints due to a Qt bug).

`screenshot_baseline` limitations:
- Requires the target app to be running and in the correct state. BA cannot navigate the app to reach the state.
- Timestamp-containing regions of the UI will always diff. Use the `threshold_pct` field to accommodate acceptable change.
- Pixel comparison does not understand UI semantics. A pixel-identical screenshot may still contain a UX bug; a pixel-different screenshot may reflect an intentional improvement.
- On multi-monitor setups, window discovery uses the first window matching the title substring. If multiple windows match (e.g., two Relay Hub instances), results are unpredictable.
- HiDPI / fractional scaling may cause the captured screenshot dimensions to differ from the logical window dimensions. The resize step in §6.4 mitigates this but may introduce interpolation artifacts in the diff.
