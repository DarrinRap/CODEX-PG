# CODEX_CONTRAST_AUDIT_v1

## 1. Status / Metadata

Status: Draft v1 for Claude review

Owner: Codex

Created: 2026-04-25

Scope: Static Qt stylesheet contrast audit for `C:\panda-gallery`.

Decision posture: Evidence report only. No implementation edits were made. The report identifies WCAG AA failures and recommends replacements from the PG Design Bible token set where possible.

Summary:

- Static scanner opened 71 Python source/test/helper files under `C:\panda-gallery`, excluding cache, build, dist, workflow/mockup, image, and binary artifact directories.
- 26 files contained QSS, `setStyleSheet`, stylesheet constants, or style-bearing source.
- 171 static contrast pair occurrences were computed.
- Those occurrences collapse into 43 unique foreground/background/context rows.
- 7 text rows fail WCAG AA normal-text contrast.
- 78 non-text/border occurrences fail the 3:1 UI-component threshold, mostly because current PG borders are deliberately subtle.
- Bug #137's shipped v4.36 combo-popup fix passes.

## 2. Read-Only Source References

Primary required references:

- `C:\panda-gallery\workflows\design\PG_DESIGN_BIBLE_v1.md`
- `C:\panda-gallery\STYLE.md`
- `C:\panda-gallery\BUGS.md`
- `C:\panda-gallery\styles.py`
- `C:\panda-gallery\panda_gallery.py`
- `C:\panda-gallery\panels.py`
- `C:\panda-gallery\library_view.py`
- `C:\panda-gallery\freeform_view.py`
- `C:\panda-gallery\template_view.py`
- `C:\panda-gallery\template_designer.py`
- `C:\panda-gallery\comparison_view.py`
- `C:\panda-gallery\audit_module\audit_module_window.py`
- `C:\panda-gallery\instruction_pane.py`
- `C:\panda-gallery\dialogs.py`
- `C:\panda-gallery\splash.py`
- `C:\panda-gallery\history.py`
- `C:\panda-gallery\patient_panel.py`
- `C:\panda-gallery\filmstrip.py`
- `C:\panda-gallery\region_capture.py`

QSS/style-bearing files found by static scan:

- `C:\panda-gallery\annotations.py`
- `C:\panda-gallery\applets\qaction_enable_probe.py`
- `C:\panda-gallery\audit_module\__main__.py`
- `C:\panda-gallery\audit_module\audit_module_window.py`
- `C:\panda-gallery\canvas.py`
- `C:\panda-gallery\comparison_view.py`
- `C:\panda-gallery\constants.py`
- `C:\panda-gallery\dialogs.py`
- `C:\panda-gallery\filmstrip.py`
- `C:\panda-gallery\freeform_view.py`
- `C:\panda-gallery\history.py`
- `C:\panda-gallery\instruction_pane.py`
- `C:\panda-gallery\library_view.py`
- `C:\panda-gallery\lightroom_slider.py`
- `C:\panda-gallery\panda_gallery.py`
- `C:\panda-gallery\panels.py`
- `C:\panda-gallery\patient_panel.py`
- `C:\panda-gallery\region_capture.py`
- `C:\panda-gallery\scripts\debug\probe_banner.py`
- `C:\panda-gallery\scripts\debug\probe_banner_colored.py`
- `C:\panda-gallery\scripts\debug\probe_banner_render.py`
- `C:\panda-gallery\styles.py`
- `C:\panda-gallery\template_designer.py`
- `C:\panda-gallery\template_view.py`
- `C:\panda-gallery\test_freeform.py`
- `C:\panda-gallery\workflow_capture.py`

Additional scanned Python files with no scored static QSS pair:

- `adjustments.py`, `database.py`, `mic_device.py`, `results_writer.py`, `settings_keys.py`, `splash.py`, `template_data.py`, `utils.py`, `wda.py`
- `audit_module\__init__.py`, `audit_module\anthropic_triage.py`, `audit_module\bugs_md_writer.py`, `audit_module\bugs_parser.py`, `audit_module\destinations.py`, `audit_module\issue_store.py`, `audit_module\mock_triage.py`, `audit_module\prompt_builder.py`, `audit_module\triage_service.py`
- `codex_audit\__init__.py`, `codex_audit\cli.py`, `codex_audit\issue_extraction.py`, `codex_audit\package_builder.py`, `codex_audit\review_records.py`, `codex_audit\validation.py`
- `scripts\seed_demo.py`, `scripts\set_audio_device_qsetting.py`, `scripts\transcribe_latest.py`, `scripts\vcommit.py`
- `skills\panda-gallery-testing\scripts\smoke.py`, `skills\pg-session-manager\scripts\next_handoff_number.py`
- `tests\__init__.py`, `tests\audit_module\__init__.py`, `tests\audit_module\test_anthropic_provider.py`, `tests\audit_module\test_bugs_md_writer.py`, `tests\audit_module\test_bugs_parser.py`, `tests\audit_module\test_destinations.py`, `tests\audit_module\test_fixed_parser.py`, `tests\audit_module\test_issue_store.py`, `tests\audit_module\test_mock_triage.py`, `tests\audit_module\test_prompt_builder.py`, `tests\codex_audit\__init__.py`, `tests\codex_audit\fixtures\_make_png.py`, `tests\codex_audit\test_package_builder.py`, `tests\test_results_writer.py`, `tests\test_transcribe_latest.py`

## 3. Boundary Statement

`C:\panda-gallery` was treated as read-only.

No files under `C:\panda-gallery` were edited.

This report is the only C1 deliverable and lives under `C:\CODEX PG`.

## 4. Methodology

Formula:

- WCAG relative luminance was computed per WCAG 2.1: linearize sRGB channels, compute `0.2126 R + 0.7152 G + 0.0722 B`, then contrast ratio `(L1 + 0.05) / (L2 + 0.05)`.
- Hex shorthand was expanded before scoring, so `#888` was scored as `#888888`.
- 8-digit hex values were normalized to their RGB component only. Static alpha compositing was not attempted unless the background was explicitly known.

Thresholds:

- Normal text: 4.5:1.
- Large text: 3:1. Static QSS rarely proves rendered point size and weight across Qt/DPI, so the audit uses the stricter 4.5:1 text threshold unless a context is clearly non-text.
- UI components and graphical objects: 3:1 under WCAG 1.4.11.
- Decorative dividers are listed but severity is Low when they do not carry state, focus, selection, or control-boundary meaning.

What counted as a pair:

- Text pair: `color` on `background`, `background-color`, or `selection-background-color` in the same selector block.
- Selection pair: `selection-color` on `selection-background-color`.
- UI border pair: `border`, `border-color`, `border-left`, `border-bottom`, or related border declarations against a same-block background.
- Inherited/transparent color-only declarations were reviewed manually for common PG surfaces, but the table below is limited to source-visible static pairs where both colors can be tied to the same selector or immediate style string.

Scanner:

- Native `rg` was attempted first but was blocked by the desktop environment.
- A static parser then opened Python files under source/test/helper roots, skipping `.git`, `.pytest_cache`, `__pycache__`, `workflows`, `build`, `dist`, `tmp`, image/artifact directories, and mockup HTML/CSS.
- The scanner extracted QSS-like braced blocks, one-line style strings, `setStyleSheet` content, shared constants in `styles.py`, and literal `color`/`background`/`border` declarations.
- Mockup placeholder gradients, radiograph placeholders, and photo placeholders were not scored, per C1 instructions.

Bible mapping:

- Recommendations use PG Design Bible v1 section 2 token values.
- No new hex values are introduced as recommendations.
- When no Bible token satisfies the desired context cleanly, this report calls that out as a design question.

## 5. Findings Table

Interpretation note: this table groups repeated identical pair/context rows. The `Count` column is the number of static occurrences found; `Locations` lists every occurrence in the group. "Low" border rows are still real 3:1 failures, but many are intentional subtle dividers from the current PG border scale rather than urgent readability defects.

| # | Severity | Kind | Foreground | Background | Ratio | Threshold | Result | Count | Locations |
|---|---|---|---|---|---:|---:|---|---:|---|
| 1 | Critical | text | #333333 | #111111 | 1.49 | 4.5 | FAIL | 1 | panda_gallery.py:783 |
| 2 | Critical | text | #555555 | #181828 | 2.35 | 4.5 | FAIL | 2 | panda_gallery.py:268<br>panda_gallery.py:592 |
| 3 | Low | ui border | #00ff00 | #ff0000 | 2.91 | 3 | FAIL | 1 | scripts\debug\probe_banner_colored.py:31 |
| 4 | High | text | #ffffff | #e74c3c | 3.82 | 4.5 | FAIL | 1 | styles.py:314 |
| 5 | Low | text | #ffffff | #ff0000 | 4.00 | 4.5 | FAIL | 1 | scripts\debug\probe_banner_colored.py:31 |
| 6 | High | text | #888888 | #22223a | 4.36 | 4.5 | FAIL | 2 | dialogs.py:81<br>template_designer.py:1072 |
| 7 | Low | ui border | #e8a87c | #e8a87c | 1.00 | 3 | FAIL | 5 | dialogs.py:859<br>instruction_pane.py:1266<br>instruction_pane.py:1308<br>instruction_pane.py:2936<br>instruction_pane.py:2937 |
| 8 | Low | ui border | #d4945a | #d4945a | 1.00 | 3 | FAIL | 4 | instruction_pane.py:1269<br>instruction_pane.py:1270<br>instruction_pane.py:1311<br>instruction_pane.py:1312 |
| 9 | Low | ui border | #1a1a2e | #181828 | 1.03 | 3 | FAIL | 2 | panda_gallery.py:268<br>panda_gallery.py:592 |
| 10 | Low | ui border | #1a1a2e | #14141f | 1.07 | 3 | FAIL | 2 | panels.py:1696<br>panels.py:1709 |
| 11 | Low | ui border | #2a2a3e | #22223a | 1.10 | 3 | FAIL | 33 | comparison_view.py:242<br>dialogs.py:81<br>dialogs.py:436<br>dialogs.py:678<br>dialogs.py:786<br>dialogs.py:787<br>dialogs.py:799<br>dialogs.py:1118<br>filmstrip.py:268<br>instruction_pane.py:2948<br>library_view.py:476<br>panda_gallery.py:264<br>panda_gallery.py:588<br>panels.py:477<br>panels.py:1124<br>panels.py:1201<br>panels.py:1229<br>panels.py:1230<br>patient_panel.py:216<br>patient_panel.py:415<br>patient_panel.py:427<br>patient_panel.py:436<br>patient_panel.py:494<br>region_capture.py:427<br>styles.py:65<br>styles.py:121<br>styles.py:136<br>styles.py:166<br>styles.py:276<br>styles.py:281<br>template_designer.py:977<br>template_designer.py:1072<br>template_designer.py:1082 |
| 12 | Low | ui border | #22223a | #14141f | 1.18 | 3 | FAIL | 1 | audit_module\audit_module_window.py:188 |
| 13 | Low | ui border | #2a2a3e | #1a1a2e | 1.22 | 3 | FAIL | 9 | dialogs.py:444<br>freeform_view.py:623<br>history.py:238<br>library_view.py:754<br>library_view.py:801<br>styles.py:12<br>styles.py:147<br>styles.py:352<br>test_freeform.py:486 |
| 14 | Low | ui border | #2a2a3e | #1a1a1a | 1.24 | 3 | FAIL | 1 | comparison_view.py:78 |
| 15 | Low | ui border | #2a2a4e | #1a1a2e | 1.25 | 3 | FAIL | 1 | instruction_pane.py:1221 |
| 16 | Low | ui border | #d4945a | #e8a87c | 1.26 | 3 | FAIL | 1 | styles.py:173 |
| 17 | Low | ui border | #2a2a3e | #161625 | 1.28 | 3 | FAIL | 9 | comparison_view.py:228<br>dialogs.py:779<br>patient_panel.py:401<br>patient_panel.py:466<br>styles.py:22<br>styles.py:47<br>styles.py:74<br>styles.py:241<br>template_designer.py:1065 |
| 18 | Low | ui border | #2a2a3e | #14141f | 1.30 | 3 | FAIL | 5 | audit_module\audit_module_window.py:1326<br>styles.py:31<br>styles.py:85<br>styles.py:463<br>template_designer.py:943 |
| 19 | Low | ui border | #2a2a3e | #0d0d18 | 1.38 | 3 | FAIL | 1 | audit_module\audit_module_window.py:177 |
| 20 | Low | ui border | #2a2a3e | #000000 | 1.50 | 3 | FAIL | 2 | dialogs.py:439<br>dialogs.py:682 |
| 21 | Low | ui border | #2a2a3e | #555555 | 1.88 | 3 | FAIL | 1 | panels.py:317 |
| 22 | Pass | ui border | #5ab87a | #2a4a2a | 4.06 | 3 | PASS | 2 | dialogs.py:1158<br>panels.py:460 |
| 23 | Pass | text | #888888 | #1a1a2e | 4.81 | 4.5 | PASS | 2 | instruction_pane.py:1221<br>instruction_pane.py:1285 |
| 24 | Pass | text | #888888 | #161625 | 5.04 | 4.5 | PASS | 1 | styles.py:74 |
| 25 | Pass | text | #8a8a9a | #0d0d18 | 5.68 | 4.5 | PASS | 1 | audit_module\audit_module_window.py:177 |
| 26 | Pass | text | #e8a87c | #2a2a4e | 6.70 | 4.5 | PASS | 6 | freeform_view.py:624<br>instruction_pane.py:2952<br>panels.py:1232<br>styles.py:69<br>styles.py:283<br>test_freeform.py:487 |
| 27 | Pass | ui border | #e8a87c | #2a2a4e | 6.70 | 3 | PASS | 6 | history.py:266<br>panels.py:1232<br>panels.py:1705<br>patient_panel.py:194<br>styles.py:69<br>styles.py:129 |
| 28 | Pass | ui border | #5ab87a | #1a1a2e | 6.96 | 3 | PASS | 1 | instruction_pane.py:1295 |
| 29 | Pass | text | #e8a87c | #22223a | 7.60 | 4.5 | PASS | 8 | comparison_view.py:242<br>dialogs.py:786<br>dialogs.py:787<br>filmstrip.py:268<br>library_view.py:569<br>library_view.py:570<br>panels.py:298<br>patient_panel.py:427 |
| 30 | Pass | ui border | #e8a87c | #22223a | 7.60 | 3 | PASS | 3 | library_view.py:569<br>library_view.py:570<br>panels.py:298 |
| 31 | Pass | selection text | #e8a87c | #22223a | 7.60 | 4.5 | PASS | 1 | audit_module\audit_module_window.py:165 |
| 32 | Pass | text | #1a1a2e | #e8a87c | 8.39 | 4.5 | PASS | 5 | dialogs.py:96<br>patient_panel.py:329<br>region_capture.py:437<br>styles.py:301<br>template_designer.py:1090 |
| 33 | Pass | selection text | #1a1a2e | #e8a87c | 8.39 | 4.5 | PASS | 3 | audit_module\audit_module_window.py:1326<br>styles.py:147<br>styles.py:276 |
| 34 | Pass | ui border | #e8a87c | #1a1a2e | 8.39 | 3 | PASS | 2 | instruction_pane.py:1302<br>library_view.py:367 |
| 35 | Pass | text | #e8a87c | #1a1a2e | 8.39 | 4.5 | PASS | 1 | history.py:238 |
| 36 | Pass | text | #14141f | #e8a87c | 8.98 | 4.5 | PASS | 2 | instruction_pane.py:1266<br>instruction_pane.py:1308 |
| 37 | Pass | text | #e8a87c | #14141f | 8.98 | 4.5 | PASS | 2 | panda_gallery.py:335<br>panda_gallery.py:553 |
| 38 | Pass | text | #e8a87c | #000000 | 10.32 | 4.5 | PASS | 1 | dialogs.py:682 |
| 39 | Pass | text | #e0ddd5 | #22223a | 11.39 | 4.5 | PASS | 24 | dialogs.py:799<br>dialogs.py:1118<br>instruction_pane.py:1243<br>instruction_pane.py:2948<br>library_view.py:476<br>panda_gallery.py:264<br>panda_gallery.py:588<br>panels.py:477<br>panels.py:1124<br>panels.py:1201<br>panels.py:1229<br>patient_panel.py:216<br>patient_panel.py:217<br>patient_panel.py:415<br>patient_panel.py:436<br>patient_panel.py:494<br>region_capture.py:427<br>styles.py:121<br>styles.py:136<br>styles.py:276<br>styles.py:281<br>styles.py:287<br>template_designer.py:977<br>template_designer.py:1082 |
| 40 | Pass | text | #e8d9c0 | #1a1a2e | 12.28 | 4.5 | PASS | 1 | styles.py:147 |
| 41 | Pass | text | #e0ddd5 | #1a1a2e | 12.57 | 4.5 | PASS | 8 | dialogs.py:444<br>freeform_view.py:623<br>library_view.py:754<br>library_view.py:801<br>region_capture.py:82<br>region_capture.py:360<br>styles.py:12<br>test_freeform.py:486 |
| 42 | Pass | text | #e0ddd5 | #161625 | 13.16 | 4.5 | PASS | 1 | styles.py:22 |
| 43 | Pass | text | #e0ddd5 | #14141f | 13.46 | 4.5 | PASS | 5 | audit_module\audit_module_window.py:188<br>audit_module\audit_module_window.py:1326<br>history.py:264<br>styles.py:31<br>styles.py:463 |

## 6. Forbidden-Color List

This is a contextual forbidden list. Some values below are legitimate Bible tokens in other roles. They are forbidden in the failed pair contexts shown here, not globally forbidden.

| Hex | Contextual finding | Worst evidence | Replacement direction |
|---|---|---|---|
| `#333333` | Text on `#111111` fails at 1.49. | `panda_gallery.py:783` disabled edit tabs. | Replace with Bible `--text-muted` `#888888` if the label should remain readable, or use `--text-dim` only on a Bible surface with an explicit inactive-state exemption. |
| `#555555` | Text on `#181828` fails at 2.35; inferred disabled/menu uses on dark surfaces also fail under 4.5. | `panda_gallery.py:268`, `panda_gallery.py:592`; color-only disabled menu items in `styles.py:39`. | Use `--text-muted` `#888888` for readable secondary/disabled labels. Keep `--text-dim` `#555555` only for non-essential disabled placeholders if explicitly accepted. |
| `#181828` | Non-Bible disabled-button background; text and border fail on it. | `panda_gallery.py:268`, `panda_gallery.py:592`. | Replace with `--pane` `#1a1a2e` or `--pane-raised` `#22223a` depending on control state. |
| `#111111` | Non-Bible background behind unreadable disabled tab text. | `panda_gallery.py:783`. | Replace with `--pane` `#1a1a2e`, `--canvas` `#14141f`, or `--pane-raised` `#22223a` based on component role. |
| `#ffffff` | White text on destructive red fails normal text AA at 3.82; debug red also fails at 4.00. | `styles.py:314`; dev-only `scripts\debug\probe_banner_colored.py:31`. | For destructive fill, use `--canvas` `#14141f` text on `--err` `#e74c3c` for 4.78. Or change destructive buttons to outlined `--err` on `--canvas`/`--pane`. |
| `#e74c3c` | Bible `--err` is legitimate, but white text on it fails. | `styles.py:314`. | Keep `--err` for destructive state, but pair with `--canvas` as foreground or use outline treatment. |
| `#888888` | `--text-muted` fails normal-text AA on `--pane-raised` at 4.36. | `dialogs.py:81`, `template_designer.py:1072`. | Use `--text` `#e0ddd5` for button labels on `--pane-raised`, or move muted labels to `--pane`/`--chrome`, where `#888888` passes. |
| `#2a2a3e` | Bible `--border` fails 3:1 against most nearby dark surfaces when used as a required component boundary. | 33 occurrences against `#22223a`, plus menu/pane/chrome occurrences. | For required focus/interactive boundaries use `--accent` `#e8a87c`. For neutral required boundaries, use `--text-muted` `#888888` only if the visual design accepts a brighter neutral border. Decorative dividers may remain low-contrast by design. |
| `#22223a` | Bible `--pane-raised` is legitimate, but low-contrast border pairs fail on it. | `styles.py:121`, `dialogs.py:799`, many controls. | Keep as raised surface; change required borders/focus boundaries rather than the surface. |
| `#1a1a2e` | Bible `--pane` is legitimate, but low-contrast borders fail against it. | `styles.py:12`, `library_view.py:754`, `freeform_view.py:623`. | Keep as pane/dialog body; use `--accent` for focus/selection or accept subtle border as decorative. |
| `#14141f` | Bible `--canvas` is legitimate, but borders like `#1a1a2e`, `#22223a`, and `#2a2a3e` fail against it. | `panels.py:1696`, `styles.py:31`, `audit_module_window.py:188`. | Keep for canvas/scroll bodies; use `--accent` for important boundaries, not adjacent surface-scale borders. |
| `#161625` | Bible `--chrome` is legitimate, but `#2a2a3e` border on it fails at 1.28. | `styles.py:22`, `styles.py:47`, `comparison_view.py:228`. | Use `--accent` for active chrome boundaries; decorative chrome separators may remain subtle if approved. |
| `#e8a87c` | Bible `--accent` is legitimate; fails only when border and fill are identical. | `instruction_pane.py:1266`, `dialogs.py:859`. | Keep accent fill; use no border, transparent border reserve, or `--accent-ink`/`--canvas` for checkmark/inner glyph contrast. |
| `#d4945a` | Bible `--accent-hover` is legitimate; fails when border and fill are identical or near-identical. | `instruction_pane.py:1269`, `styles.py:173`. | Keep hover fill; remove same-color border or use a transparent border reserve. |
| `#2a2a4e` | Bible `--pane-selected` is legitimate; fails as a left border on `--pane`. | `instruction_pane.py:1221`. | Use `--accent` for meaningful state rail; keep selected fill for selected backgrounds. |
| `#1a1a1a` | Stale pre-Bible surface. | `comparison_view.py:78`. | Replace with `--pane` `#1a1a2e` or stage-only `#0a0a14` based on whether it is chrome/pane or image stage. |
| `#0d0d18` | AM-only extra-deep shell surface, not in Bible v1. | `audit_module_window.py:177`, `audit_module_window.py:188`. | Replace with `--canvas` `#14141f` unless AM needs a new Bible token. If it needs a new token, escalate as design question. |
| `#000000` | Fails border contrast with `#2a2a3e` in template thumbnail surfaces and is globally discouraged except splash/stage use. | `dialogs.py:439`, `dialogs.py:682`. | Use stage token `#0a0a14` only for image stage/thumb wells; otherwise use `--canvas` `#14141f`. |
| `#ff0000` | Debug-only saturated red, forbidden by Bible for user-facing surfaces. | `scripts\debug\probe_banner_colored.py:31`. | Use `--err` `#e74c3c` if this ever escapes debug code. |
| `#00ff00` | Debug-only saturated green, forbidden by Bible for user-facing surfaces. | `scripts\debug\probe_banner_colored.py:31`. | Use `--ok` `#7fb069` if this ever escapes debug code. |

## 7. Severity Tiers

Critical:

- Fails WCAG AA normal text at 4.5:1 and appears in a user-readable label or control label that is part of normal app comprehension.
- Current critical rows: `#333333` on `#111111`; `#555555` on `#181828`.

High:

- Fails WCAG AA normal text but is localized to an action/control surface rather than prose, or fails a meaningful interactive-control contrast target.
- Current high rows: white text on destructive red; muted text on raised buttons.

Medium:

- Would fail AA for large text or specific visual objects where static source cannot prove size/weight.
- No distinct medium group was found in the static same-block scan.

Low:

- Fails 3:1 non-text contrast for decorative or structural borders, separators, scrollbar handles, subtle panel boundaries, dev-only debug styles, or same-color fill/border pairs where the border is not the only affordance.
- Most failures are Low because Bible surface/border tokens are intentionally close. They should be fixed only where the border carries state, focus, selection, or control boundary meaning.

Disabled-state caveat:

- WCAG exempts inactive controls from contrast requirements. The audit still flags disabled labels because the PG Design Bible says disabled tabs and buttons stay visible, dimmed to `--text-dim`, rather than hidden. If the team accepts true disabled-text exemption, those rows can be downgraded, but they remain Bible/readability risks.

## 8. Recommendations

1. Fix unreadable disabled edit-tab styling in `panda_gallery.py`.

   Current failure: `#333333` on `#111111` at 1.49 and `#555555` on `#181828` at 2.35.

   Recommendation: replace non-Bible `#111111` and `#181828` with Bible surfaces. Use `--text-muted` `#888888` for labels that Darrin still needs to read. Use `--pane` `#1a1a2e` or `--pane-raised` `#22223a` as the background based on whether the control is flat or raised.

2. Fix destructive button text contrast in `styles.py`.

   Current failure: `#ffffff` on `#e74c3c` at 3.82.

   Recommendation: either:

   - keep `--err` `#e74c3c` as fill and use `--canvas` `#14141f` as text, which scores 4.78; or
   - change destructive buttons to outlined red: `--canvas`/`--pane` background with `--err` text. `#e74c3c` on `#14141f` scores 5.11.

   Design question: Bible v1 does not define an explicit "ink on err" token. If destructive filled buttons are retained, Claude should decide whether `--canvas` can serve that role.

3. Replace muted text on raised cancel buttons where the label is readable UI text.

   Current failure: `#888888` on `#22223a` at 4.36 in `dialogs.py:81` and `template_designer.py:1072`.

   Recommendation: use `--text` `#e0ddd5` for button labels on `--pane-raised`, or move truly muted text to `--pane`/`--chrome`, where `#888888` passes.

4. Treat `--border` on `--pane-raised` as decorative only.

   Current failure: `#2a2a3e` on `#22223a` at 1.10 across 33 occurrences.

   Recommendation: do not try to make every card/input border 3:1 by default; that would fight the Bible's restrained chrome. Instead:

   - use `--accent` `#e8a87c` for focus, hover, active, selected, or user-actionable boundaries;
   - use transparent border reserves to prevent layout shift;
   - leave purely decorative separators low-contrast if the component still reads through fill, spacing, or typography.

5. Remove stale pre-Bible surfaces opportunistically.

   Current examples: `#1a1a1a`, `#111111`, `#181828`, `#0d0d18`.

   Recommendation: replace with Bible surfaces:

   - `--canvas` `#14141f`
   - `--chrome` `#161625`
   - `--pane` `#1a1a2e`
   - `--pane-raised` `#22223a`
   - `--pane-selected` `#2a2a4e`
   - stage-only `#0a0a14` where the surface is actually image/radiograph stage.

6. Keep debug-only saturated colors out of user-facing paths.

   Current failure: `scripts\debug\probe_banner_colored.py` uses `#ff0000`, `#00ff00`, and `#ffffff`.

   Recommendation: no product fix required if this remains a debug probe. If copied into product code, replace red with `--err`, green with `--ok`, and white with `--text` or a dark ink token appropriate to the fill.

7. Add a future palette pass rather than piecemeal visual fixes.

   STYLE section 6 says palette migration is opportunistic and `palette.py` does not exist yet. Given the number of repeated border pairs, a future implementation pass should seed `palette.py` with Bible section 2 tokens and fix the highest-risk text rows first. Do not open a broad all-colors migration in this C1 scope.

## 9. Exhibit A: Bug #137

Bug #137: QComboBox dropdown popup had pale text on a light popup background and was illegible.

Source status:

- `BUGS.md` says the fix shipped in v4.36 on 2026-04-25.
- Fixed file: `styles.py`, `DARK_THEME_QSS`.
- Fixed selectors: `QComboBox QAbstractItemView`, `::item`, and `::item:hover`.

Original failure:

- The exact native popup background color was not source-visible because the bug came from Qt popup widgets resolving their own palette.
- The visible symptom was pale PG text on a light native popup background.
- Using the common fallback of PG cream `#e0ddd5` on native white `#ffffff`, the ratio is 1.36, a clear AA failure.

Post-fix pairs:

| Pair | Ratio | Threshold | Result | Source |
|---|---:|---:|---|---|
| `#e8d9c0` text on `#1a1a2e` popup background | 12.28 | 4.5 | PASS | `styles.py:147` |
| `#1a1a2e` selection text on `#e8a87c` selection background | 8.39 | 4.5 | PASS | `styles.py:147` |
| `#2a2a3e` popup border on `#1a1a2e` popup background | 1.22 | 3 | FAIL/Low | `styles.py:147` |

Conclusion:

- v4.36 resolves the readability defect for dropdown option text.
- The remaining popup border contrast is a Low non-text/subtle-boundary issue, not the #137 illegibility bug.

## 10. Methodology Limitations

1. Static QSS cannot perfectly model Qt cascade and palette inheritance.

   The scanner scores same-block static pairs and obvious one-line styles. It does not fully resolve parent widget backgrounds, dynamic properties, runtime object names, or platform palette defaults.

2. Transparent and rgba values were not alpha-composited.

   The scanner logged many rgba-tinted surfaces as limitations rather than pretending a single backdrop is known. Examples include accent-soft and fail-panel red tints.

3. Dynamic QColor painting and item foreground APIs were not fully scored.

   The task targeted Qt stylesheets. The repo also uses `QColor`, `QPainter`, `QBrush`, `QPen`, and item foreground calls for annotations, canvas primitives, sensor colors, AM table rows, and template thumbnails. Those should be a C2 visual-token audit if needed.

4. Disabled controls are ambiguous.

   WCAG exempts inactive components, but the Design Bible says disabled controls remain visible. This report flags them when they are the only visible label for a future or unavailable action.

5. Debug/test styles are included but downgraded.

   `scripts\debug\probe_banner_colored.py` and `test_freeform.py` contain style strings, but they are not product runtime surfaces. They are included for completeness and should not drive product work unless copied into user-facing code.

6. Bible tokens can fail strict non-text contrast when used as subtle borders.

   `--border` and related border tokens are part of the canonical visual language, yet they fail 3:1 against adjacent dark surfaces. This is a design-system tension, not merely a code defect. The pragmatic rule should be: subtle borders are allowed for decoration; focus, hover, selected, active, and required control boundaries need higher contrast.

7. AM uses non-Bible colors.

   `audit_module_window.py` uses `#0d0d18`, `#8a8a9a`, `#5ab87a`, and `#d46a6a`. Some pass; some are outside Bible v1. If AM is user-facing long-term, either map these to Bible tokens or ask Claude/Darrin whether AM needs a small approved extension set.

## 11. Bottom Line

The urgent fixes are small:

1. Replace unreadable disabled tab/button text and non-Bible dark backgrounds in `panda_gallery.py`.
2. Fix destructive button text contrast in `styles.py`.
3. Use `--text`, not `--text-muted`, for normal cancel button labels on `--pane-raised`.

The broad noisy finding is architectural:

- PG's current `--border` on raised/pane/chrome surfaces fails strict 3:1 non-text contrast almost everywhere.
- Do not brighten every border indiscriminately. Reserve high-contrast boundaries for focus, active, selected, hover, and required component edges; allow decorative separators to remain subtle if the Bible's restrained-chrome direction holds.
