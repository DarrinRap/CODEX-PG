# CODEX Recommendations for Claude: Panda Gallery Code Quality and Modernization

Generated: 2026-04-24
Audience: Claude / Claude Code working in `C:\panda-gallery`
Author: Codex, based on read-only review of the live Panda Gallery codebase and project rule files

## How To Use This Document

This is not a request to rewrite Panda Gallery. It is a prioritized, concrete improvement guide.

Claude should use this document to:

1. Understand where the codebase is strong.
2. Understand where the codebase is risky.
3. Pick tightly scoped modernization tasks.
4. Avoid broad refactors that destabilize shipped behavior.
5. Convert recommendations into single-purpose prompts or commits.

Important boundary:

- `C:\panda-gallery` is the live Panda Gallery / Claude workspace.
- Codex reviewed it read-only.
- Codex-owned work remains under `C:\CODEX PG`.
- Claude should continue using its normal Panda Gallery workflow, `BUGS.md`, `HANDOFF.md`, `STYLE.md`, and versioned commit process.

## Executive Summary

Panda Gallery is significantly better than a casual prototype. It has real product thinking, careful bug history, domain-specific UX rules, a working guided testing system, and unusually detailed lessons learned. The recent testing/capture subsystem is especially thoughtful.

However, the codebase is not yet clean, modern, commercial-grade architecture throughout. It has grown organically. Several core files are very large, UI styling is scattered, some UI widgets reach directly into persistence, automated test coverage is thin, and documentation often mixes API intent with historical bug narrative.

The correct path is not a rewrite. The correct path is disciplined incremental modernization:

- keep shipped behavior stable,
- extract only around active work,
- add tests around pure logic,
- define contracts before building new Testing + Audit layers,
- gradually move style and persistence concerns to cleaner boundaries.

In one sentence:

> The code is capable and thoughtfully evolved, but it needs architectural tightening before it can support a larger Testing + Audit product without accumulating serious change risk.

## Evidence Basis

Files inspected included, at minimum:

- `panda_gallery.py`
- `instruction_pane.py`
- `workflow_capture.py`
- `region_capture.py`
- `results_writer.py`
- `database.py`
- `canvas.py`
- `panels.py`
- `library_view.py`
- `scripts/transcribe_latest.py`
- `skills/panda-gallery-testing/scripts/smoke.py`
- `STYLE.md`
- `skills/pg-prompt-drafting/CODE_QUALITY.md`
- `skills/pg-rules/DEVELOPMENT_DISCIPLINE.md`
- `skills/pg-rules/UX_PRINCIPLES.md`
- `BUGS.md`
- `HANDOFF.md`

Objective signals gathered from top-level Python files:

| File | Approx. lines | Comment |
|---|---:|---|
| `instruction_pane.py` | 2,734 | Too large; multiple responsibilities; recent work is careful but file size is a risk |
| `panda_gallery.py` | 2,526 | Main orchestration hub; expected to be large, but now carrying too much behavior |
| `panels.py` | 1,622 | Heavy UI/control module with many inline style/control concerns |
| `canvas.py` | 1,252 | Core editor behavior; cohesive but large and event-heavy |
| `library_view.py` | 1,092 | UI plus persistence leakage; known debt |
| `template_designer.py` | 1,064 | Large UI module; likely future extraction target |
| `dialogs.py` | 1,000 | Many dialog concepts in one module |
| `database.py` | 820 | Reasonable as DB boundary but could use narrower service methods |
| `workflow_capture.py` | 797 | Stronger recent module; cohesive enough |
| `region_capture.py` | 630 | Strong recent module; good isolation |
| `results_writer.py` | 343 | Good size, clear responsibility |

Pattern counts across top-level `.py` files:

| Pattern | Count | Interpretation |
|---|---:|---|
| `except Exception` | 65 | Some justified for Qt/session robustness; too common overall |
| bare `except:` | 1 | Should be removed or converted to a named exception |
| `print(` | 52 | Some CLI scripts are fine; app modules should prefer logging/status paths |
| `TODO` | 13 | Manageable, but should map to `BUGS.md` or spec entries |
| `setStyleSheet(` | 278 | Styling is heavily inline/scattered; palette/style consolidation needed |
| `QSettings(` | 27 | QSettings access scattered; settings helper exists and should be used more |
| `pass` in exception/placeholder contexts | 37 | Some safe; several should become explicit logging or comments |

## 6 C's Evaluation

The local 6 C's are: Correct, Complete, Clear, Clean, Checkable, Contextual.

### Correct: Strong, With Local Caveats

The code often matches the actual shipped behavior. Recent modules cite real bugs, specs, and edge cases. `workflow_capture.py`, `region_capture.py`, and `results_writer.py` show good state consistency and defensive handling.

Examples:

- `workflow_capture.py` rolls back failed frame captures and preserves session consistency.
- `region_capture.py` handles Qt widget lifetime issues by holding Python references to flash/toast widgets.
- `results_writer.py` preserves `manual_screenshots[]` when later outcome writes overwrite a step.

Caveat:

Some docs and bugs lag code. For example, some `BUGS.md` entries describe pane problems that may have been partly resolved by later v3.71/v3.99 changes. Claude should verify current code before implementing from a bug title.

Recommendation:

- Before every fix, do a Step 0 read of current code and latest commits.
- Do not assume `BUGS.md` status text is perfectly synchronized with implementation.

### Complete: Medium

Individual features are often completed deeply, including edge cases. But system contracts for the next product layer are incomplete.

Strong completion examples:

- workflow capture includes audio, metadata, monitor geometry, frame list, frame sizes, mic fallback, and autotranscribe process handling.
- region capture includes overlay, save path selection, flash, toast, review, discard, recapture, and results JSON integration.

Incomplete product-layer areas:

- no canonical session package manifest,
- no durable evidence IDs,
- no audit issue schema,
- no approval/email/archive contract,
- no Testing + Audit compliance addendum for Dropbox/AI/email/cloud storage.

Recommendation:

- Do not build the audit dashboard or Dropbox/AI pipeline directly from `results_latest.json` paths.
- First define package/evidence/issue schemas.

### Clear: Mixed

Local code is often readable. Method names are generally meaningful. Recent comments explain why, not just what.

But clarity suffers from scale:

- `panda_gallery.py` mixes app bootstrapping, menus, toolbar, central view routing, patient scope, template handling, freeform, comparison, workflow testing, save/export/print, shutdown.
- `instruction_pane.py` contains schema validation, pane UI, checklist subview, fail panel, settings dialog, mic test flow, results writer wiring, capture visibility, styling, shortcuts.
- `panels.py` includes multiple unrelated right-panel widgets and detailed styling/control behavior.

Recommendation:

- Avoid big-bang extraction.
- Extract only stable, conceptually complete pieces as active work touches them.
- Prefer small service/helper modules for pure logic before moving Qt widget code.

### Clean: Medium-Low

The project has good cleanup discipline in intent, but code still carries organic-growth residue.

Cleanliness issues:

- large files over STYLE.md guidance,
- inline QSS and repeated color literals,
- historical bug/version commentary in docstrings,
- direct DB sessions inside widgets,
- broad exception handling and silent `pass` blocks,
- mixed print/log/status patterns.

Recommendation:

- Treat cleanup as opportunistic and scoped.
- Every feature commit should leave touched code cleaner than it found it.
- Avoid unrelated cleanup piggybacked into functional commits unless the cleanup is necessary for the change.

### Checkable: Medium

The guided testing system is a real strength. There is a smoke script and structured manual testing culture.

Weakness:

Automated test coverage is thin for pure logic. I found the smoke script and `test_freeform.py`, but not a broad unit test suite for pure modules.

Best places to add tests:

- `results_writer.py`
- `scripts/transcribe_latest.py` alignment helpers
- future package/evidence manifest builder
- slug/run ID generation
- schema validation helpers extracted from `instruction_pane.py`
- file archive behavior

Recommendation:

- Add unit tests before or alongside new pure-logic modules.
- Keep UI testing mostly smoke/manual unless a Qt test harness is deliberately introduced.

### Contextual: Strong

This is one of the codebase's best traits. Code frequently links to bugs, specs, and lessons. The team has a strong habit of writing down why a decision happened.

Risk:

Too much context inside code can become clutter. The right place for some of this is `BUGS.md`, `DEV_LOG.md`, feature specs, or comments near landmines, not docstrings for ordinary methods.

Recommendation:

- Keep landmine comments where they prevent regressions.
- Move historical phase narrative out of docstrings over time.
- Keep module docstrings current with what the module does now, not only what it did when first shipped.

## Major Strengths To Preserve

### 1. The Project Has Strong Debugging Memory

The `DEBUGGING_LESSONS.md` and skill files capture hard-won lessons. This is not typical prototype discipline. It is valuable and should be preserved.

Preserve:

- test applet strategy for hard Qt bugs,
- one failed hypothesis threshold,
- per-event logging discipline,
- bug-first documentation,
- visual-first UI rule.

Do not discard this culture during cleanup.

### 2. Recent Capture/Testing Code Shows Good Engineering Judgment

`workflow_capture.py`, `region_capture.py`, and `results_writer.py` are the strongest implementation examples.

Good patterns:

- explicit state machines and reset paths,
- defensive Qt lifetime handling,
- user-visible transient status rather than silent failures,
- atomic-ish JSON writes,
- crash-tolerant archive behavior,
- session identity via `run_id`,
- active-step integration through a small pane API.

Claude should use these as style references for new Testing + Audit code.

### 3. UX Principles Are Specific And Enforceable

The project is not vague about UX. It has specific principles:

- Escape goes one level back.
- Primary actions are one click from context.
- Empty states teach.
- Non-destructive prompts must not trap users.
- Visual-first before UI changes.

This is a strength. Future UI work should cite these explicitly.

### 4. The Codebase Has A Real Local Testing Loop

The guided instruction pane and `results_latest.json` are valuable not just as a product feature, but as a development process tool.

This means future changes can be validated in the actual app with structured tester feedback. That is a meaningful advantage.

## Major Risks To Address

### Risk 1: Large Files Make Every Change More Expensive

Specific files:

- `instruction_pane.py`
- `panda_gallery.py`
- `panels.py`
- `canvas.py`
- `library_view.py`
- `template_designer.py`
- `dialogs.py`

Why this matters:

Large files increase the chance of:

- hidden coupling,
- accidental regressions,
- merge conflicts,
- duplicated helpers,
- inconsistent UI patterns,
- difficulty onboarding another assistant or developer.

Do not respond with a giant refactor. Instead, create extraction seams.

Recommended extraction order:

1. Pure logic from `instruction_pane.py` into `instruction_schema.py` or similar.
2. Testing settings dialog from `instruction_pane.py` into `testing_settings_dialog.py`.
3. Results/evidence attachment model into new pure modules.
4. MainWindow testing menu/action wiring into a focused helper only if it grows further.
5. Palette/style constants into `palette.py` / focused QSS helpers.

### Risk 2: Inline Styling Blocks Make UI Hard To Modernize

Evidence:

- 278 top-level uses of `setStyleSheet(`.
- Many repeated colors: `#1a1a2e`, `#14141f`, `#22223a`, `#2a2a3e`, `#e8a87c`, `#888`, etc.
- Existing TODOs already mention palette extraction.

Why this matters:

- consistent visual polish is hard,
- focus/hover/disabled states drift,
- dark theme bugs repeat,
- changing palette becomes a search-and-pray operation.

Recommendation:

Do not attempt all styling migration at once. Start with new Testing + Audit surfaces and any touched pane/dialog code.

Suggested first step:

Create `palette.py` with named constants only for colors actively touched by the current task.

Example constants:

```python
BG_APP = "#1a1a2e"
BG_PANEL = "#14141f"
BG_ELEVATED = "#22223a"
BORDER_MUTED = "#2a2a3e"
ACCENT_WARM = "#e8a87c"
ACCENT_WARM_HOVER = "#d4945a"
STATE_PASS = "#5ab87a"
STATE_FAIL = "#d46a6a"
STATE_WARNING = "#f39c12"
TEXT_PRIMARY = "#e0ddd5"
TEXT_SECONDARY = "#888"
```

Then migrate only touched style blocks.

### Risk 3: Persistence Boundary Is Not Clean Everywhere

`database.py` is intended as the DB boundary, but some UI widgets still open sessions and run queries directly.

Concrete example:

- `library_view.py` opens sessions for rename/label-like operations instead of calling named `DatabaseManager` methods.

Why this matters:

- harder to test,
- harder to migrate schema,
- session lifecycle scattered,
- UI code owns business rules that should be centralized.

Recommendation:

Add named DB methods as files are touched.

Examples:

- `DatabaseManager.rename_image(image_id: int, new_original_filename: str) -> bool`
- `DatabaseManager.update_image_label(image_id: int, label: str) -> bool`
- `DatabaseManager.archive_images(image_ids: list[int]) -> list[int]`
- `DatabaseManager.restore_images(image_ids: list[int]) -> list[int]`

Then `library_view.py` calls those methods and refreshes.

### Risk 4: Tests Do Not Yet Match Feature Complexity

The smoke test is good, but the project needs more pure unit tests.

Highest-value unit tests:

1. `results_writer.py`
   - creates fresh file,
   - appends manual screenshot before outcome,
   - PASS preserves manual screenshots,
   - remove deletes empty placeholder,
   - archive moves latest + screenshot folder,
   - archive conflict suffix behavior.

2. `scripts/transcribe_latest.py`
   - segment-to-frame bucketing,
   - pre-F12 segments,
   - crossing frame boundaries,
   - malformed/nonmonotonic frame offsets,
   - transcript formatting.

3. Future package builder
   - manifest contains hashes,
   - missing screenshot is represented deterministically,
   - remote/local paths are normalized,
   - repeated packaging is idempotent.

4. Instruction schema validation if extracted
   - valid single expected step,
   - valid checklist step,
   - valid action step,
   - invalid mixed expected/checklist/action,
   - duplicate checklist IDs,
   - empty expected.

Recommendation:

Add tests only around pure logic. Do not start with a huge Qt UI test harness.

### Risk 5: Testing + Audit MVP Needs Contracts Before UI

The local app now creates evidence. The audit product needs to package, transfer, triage, approve, email, and archive evidence.

Current local evidence model:

- `results_latest.json` entries contain `screenshot` and `manual_screenshots[]` paths.
- workflow sessions contain `metadata.json`, PNG frames, optional `audio.wav`, optional `transcript.md`.
- region captures attach paths under `workflows/screenshots/<run_id>/`.

Missing audit-grade model:

- evidence IDs,
- content hashes,
- remote paths,
- transcript references,
- capture type,
- source step,
- discard status,
- upload state,
- AI issue links,
- approval events,
- email delivery events,
- archive/search record.

Recommendation:

Before dashboard or AI extraction work, create these docs and schemas:

1. `CODEX_MASTER_SPEC_INDEX.md`
2. `CODEX_SESSION_PACKAGE_SCHEMA_v1.md`
3. `CODEX_EVIDENCE_SCHEMA_v1.md` or evidence section inside package schema
4. `CODEX_AUDIT_ISSUE_SCHEMA_v1.md`
5. `CODEX_APPROVAL_EMAIL_ARCHIVE_SCHEMA_v1.md`
6. `CODEX_COMPLIANCE_ADDENDUM_TESTING_AUDIT_v1.md`

## Very Specific Recommendations By Area

## A. Architecture and Module Boundaries

### A1. Do Not Rewrite `panda_gallery.py`; Reduce Future Growth

Current role:

`panda_gallery.py` owns too much, but it is also the central app coordinator. A full split would be risky.

Recommendation:

Adopt a "no new major behavior directly in MainWindow unless it coordinates existing components" rule.

Allowed in `MainWindow`:

- construct components,
- connect signals,
- route high-level view transitions,
- call service/helper methods,
- own app-level state.

Avoid adding:

- new JSON schemas,
- package-building logic,
- Dropbox logic,
- AI extraction logic,
- long validation blocks,
- large custom dialog internals,
- detailed style strings.

Concrete next extraction:

If Testing + Audit packaging is built, create a separate module:

- `testing_audit_package.py`
- `testing_audit_models.py`
- `testing_audit_manifest.py`

MainWindow should at most add a menu action that calls a manager/service.

### A2. Extract Pure Instruction Schema Logic From `instruction_pane.py`

Current issue:

`instruction_pane.py` combines schema parsing, validation, UI rendering, settings, mic test, results writing, shortcuts, and styling.

Recommended extraction:

Create a pure module such as `instruction_schema.py`.

Move or duplicate first as pure helpers:

- load JSON file,
- validate top-level schema,
- validate step XOR among `expected`, `checklist`, and `kind: "action"`,
- normalize checklist items,
- derive test IDs,
- return structured dataclasses or dicts.

Suggested API:

```python
@dataclass(frozen=True)
class InstructionStep:
    n: int
    test_id: str
    title: str
    body: str
    expected: str | None = None
    checklist: tuple[ChecklistItem, ...] = ()
    kind: str = "observation"

@dataclass(frozen=True)
class InstructionPlan:
    schema_version: int
    title: str
    context: str | None
    steps: tuple[InstructionStep, ...]

class InstructionSchemaError(Exception):
    pass

def load_instruction_plan(path: Path) -> InstructionPlan:
    ...
```

Why:

- testable without Qt,
- reduces pane complexity,
- clarifies schema behavior,
- prepares for audit packaging to reference the same plan structure.

Do this only when touching schema work or building package contracts.

### A3. Extract Testing Settings Dialog Later, Not First

`TestingSettingsDialog` is embedded inside `instruction_pane.py`. It is large enough to become its own file.

Recommended timing:

- Do not extract immediately just to reduce line count.
- Extract when fixing #129 dialog sizing or adding settings fields.

Target file:

- `testing_settings_dialog.py`

Keep:

- `InstructionPane` imports it,
- `MainWindow._open_testing_settings()` imports it,
- settings keys remain centralized through `settings_keys.py`.

### A4. Keep `region_capture.py` Separate And Treat It As A Good Pattern

`region_capture.py` is a strong module boundary.

Keep:

- overlay widget,
- flash widget,
- toast widget,
- review dialog,
- manager.

Do not move region capture into `panda_gallery.py` or `instruction_pane.py`.

Next improvement when touched:

- update module docstring to current Phase 3 reality,
- implement cursor compositing or clearly mark include-cursor as unsupported for region capture,
- consider evidence ID hook when package schema exists.

### A5. Keep `results_writer.py` Small, But Add Tests Before Extending

`results_writer.py` has the right shape: one file, one concept, mostly pure JSON persistence.

Before adding audit-grade fields directly to `results_latest.json`, decide whether the audit package should wrap results rather than mutate the pane schema.

Recommendation:

- Keep `results_latest.json` as local pane output.
- Add a separate package manifest builder for audit use.
- Only add fields to `results_latest.json` if the pane itself needs them.

## B. Documentation and Comments

### B1. Separate API Docstrings From Historical Notes

Current pattern:

Many docstrings include phase history, bug IDs, and implementation history.

This is understandable but creates docstring clutter.

Recommendation:

For new code:

- Module docstring: purpose, key entry points, important external behavior.
- Class docstring: responsibility and public signals.
- Public method docstring: caller-facing behavior.
- Historical bug context: regular comments near the risky code or `BUGS.md` / `DEV_LOG.md`.

Example rewrite style:

Current style:

```python
"""Bug #130 Phase 3: append a manual screenshot to the current step.
...
"""
```

Preferred style:

```python
"""Append a manual screenshot path to the active step result."""
# Bug #130 Phase 3: keep this tolerant because region capture should not fail
# just because result persistence is unavailable.
```

Do this opportunistically, not as a separate sweeping docstring cleanup.

### B2. Update Module Headers When Reality Changes

`region_capture.py` and `results_writer.py` still include phase-scope language from earlier versions. Their behavior has moved beyond those phase descriptions.

Recommendation:

When touching these files, update the top docstring to describe current behavior.

Example `region_capture.py` module docstring target:

```python
"""Session-aware region capture for Shift+F12.

Provides a cursor-display overlay, drag-region capture, success flash,
review toast/dialog, and optional attachment to the active instruction-pane
step via ResultsFile.manual_screenshots.
"""
```

Keep the detailed phase history in `BUGS.md` or comments only where it prevents regression.

### B3. Keep Landmine Comments

Some long comments are justified. Do not remove comments explaining:

- Qt Python-wrapper lifetime,
- `WA_DeleteOnClose` hazards,
- Windows Display Affinity behavior,
- shutdown `RuntimeError` guards,
- high-DPI event delta lessons,
- sceneRect vs itemsBoundingRect render bug.

These are not noise. They prevent expensive regressions.

## C. Testing Strategy

### C1. Add Unit Tests For `results_writer.py`

This is the highest-value first automated test target.

Why:

- pure-ish logic,
- important evidence persistence,
- small file,
- easy temporary directory tests,
- likely to evolve for Testing + Audit.

Suggested test file:

- `test_results_writer.py`

Suggested tests:

1. `test_new_results_file_has_schema_run_id_and_empty_results`
2. `test_record_single_pass_writes_result`
3. `test_append_manual_screenshot_creates_placeholder`
4. `test_record_single_preserves_manual_screenshots`
5. `test_remove_manual_screenshot_drops_empty_placeholder`
6. `test_remove_manual_screenshot_preserves_real_result`
7. `test_archive_previous_run_moves_latest_json`
8. `test_archive_previous_run_moves_screenshot_dir`
9. `test_archive_previous_run_tolerates_invalid_json`
10. `test_write_is_atomic_enough_for_success_path`

Acceptance:

- no Qt imports,
- uses `tmp_path`,
- no dependency on live `C:\panda-gallery\workflows`,
- runs quickly.

### C2. Add Unit Tests For Transcript Alignment Helpers

`scripts/transcribe_latest.py` has pure helpers that can be tested without loading Whisper.

Suggested test file:

- `test_transcribe_alignment.py`

Suggested tests:

1. segments before first frame go to `pre`,
2. segments after first frame bucket to correct frame,
3. no frames puts all segments in `pre`,
4. segment crossing frame boundary gets screen trace,
5. non-crossing segment has no trace,
6. last-frame duration uses audio duration,
7. malformed missing offsets fallback deterministically.

Important:

Do not import or load `faster_whisper` in these tests. Keep model loading behind `main()` / `_load_model()` only.

### C3. Add Tests For Future Package Builder Before Dropbox

When the package manifest module is created, write tests first or same commit.

Test scenarios:

- complete session with results + screenshots + transcript,
- missing optional transcript,
- missing screenshot path referenced by results,
- duplicate evidence path,
- content hash changes,
- idempotent re-run produces same evidence IDs for same files,
- package manifest validates against schema.

### C4. Keep UI Verification Manual/Smoke For Now

Do not introduce a large Qt test framework unless a feature truly requires it.

For UI:

- keep smoke launch test,
- use instruction pane guided tests,
- use screenshots/mockups for visual review,
- use small applets for hard event bugs.

## D. Error Handling and Logging

### D1. Audit The Single Bare `except:`

There is one bare `except:` in the scanned top-level Python files.

Recommendation:

Find it, replace with named exception(s), or document why it must catch `BaseException`. Almost certainly it should not catch `KeyboardInterrupt` / `SystemExit`.

Acceptance:

- zero bare `except:` in app code.

### D2. Classify Broad `except Exception` Blocks

Not all broad catches are bad. In this app, some are correct:

- Qt shutdown cleanup,
- long-running capture session resilience,
- optional visual flash failure,
- best-effort archive movement,
- signal handler guard.

But each broad catch should have one of:

- a narrow reason in a nearby comment,
- logging/status message,
- a known Qt lifetime pattern,
- outermost operation boundary.

Recommendation:

Do not do a blanket replacement. Instead, when touching a file:

1. Search broad catches in that file.
2. Narrow easy ones.
3. Add a reason comment to justified ones.
4. Log nontrivial failures unless they are intentionally silent and harmless.

### D3. Prefer Logging/Status Over `print` In App Modules

`print` is fine in CLI scripts like `transcribe_latest.py`, smoke tests, and debug applets.

In app modules, prefer:

- `log.warning(...)` / `log.exception(...)` for developer diagnostics,
- `show_transient(...)` for user-facing recoverable status,
- dialogs for user decisions.

Priority cleanup targets:

- `workflow_capture.py` prints to stderr in several error paths; some are acceptable because subprocess/tee logging uses stderr, but consider logging where app logging is already configured.
- `freeform_view.py` has many debug-style prints; decide if these are still needed or should be converted to logger calls or removed.
- `database.py` migration prints could become logger info.

### D4. Preserve User Work On Failure

This is already a strong pattern. Keep it.

Examples to preserve:

- capture frame failure rolls back count and deletes partial file,
- stop session writes artifacts before `LATEST.txt`,
- shutdown stops active recording rather than discarding,
- results writer uses temp file and replace.

For new package/upload code:

- never delete local evidence after failed upload,
- write manifest after files are verified,
- record upload attempts durably,
- use idempotency keys,
- prefer orphan valid package over pointer to incomplete package.

## E. UI and Design Modernization

### E1. Create A Palette Module, But Only Use It Opportunistically

Do not run a global color migration. That would be noisy and risky.

Create `palette.py` when a real UI task touches styling.

First candidate tasks:

- #129 Settings dialog sizing,
- #131 active-window focus indicator,
- new Testing + Audit package/audit UI.

Rules:

- New UI uses palette constants.
- Touched style blocks migrate only the colors they touch.
- Existing untouched QSS stays as-is.

### E2. Fix #131 With A Mockup First

Active-window focus indicator is an ideal small UI modernization task.

Reason:

- user-visible confusion,
- small conceptual scope,
- reinforces focus/accessibility discipline,
- affects MainWindow and InstructionPane.

Recommended design options:

1. Focused top stripe or left border in `#e8a87c`.
2. Inactive subtle border/dim state.
3. Avoid heavy overlays that change screenshot/capture behavior.

Implementation likely touches:

- `panda_gallery.py` for MainWindow focus/activation handling,
- `instruction_pane.py` for pane focus/activation handling,
- possibly `styles.py` or new helper style constants.

Acceptance:

- focus indicator follows active PG window,
- no impact on Shift+F12 shortcut behavior,
- no pane capture-visibility regression,
- screenshots still respect WDA setting,
- mockup approved first.

### E3. Fix #129 As A Sizing System, Not Just One Width

Settings dialog/pane sizing should follow locked invariants:

- all buttons visible,
- fixed inter-button spacing,
- text never clipped,
- multi-line inputs show at least two lines.

Recommended approach:

- compute content-driven minimum sizes where practical,
- avoid hard-coded height defaults where content should drive size,
- preserve two-row action bar behavior at narrow widths,
- test at floor width, comfortable width, and oversized state.

Create/update mockup first:

- `workflows/design/dialog_sizing_v<N>.html`

Then implement.

### E4. Keep Tool/Panel UI Dense But Not Cramped

Panda Gallery is an operational desktop tool, not a marketing app. Dense UI is appropriate.

But dense does not mean cramped.

Use:

- stable action bars,
- clear grouping,
- scroll only for content, not primary actions,
- fixed button spacing,
- consistent low-radius controls,
- visible focus/hover states.

Avoid:

- oversized hero-like UI,
- nested cards,
- purely decorative gradients/orbs,
- hiding primary actions in menus,
- making tester workflows require file management.

## F. Data Contracts for Testing + Audit MVP

This is the most important product-level recommendation.

### F1. Do Not Treat `results_latest.json` As The Backend Contract

`results_latest.json` is local pane output. It is not yet an audit-grade package contract.

Problems if used directly:

- screenshot references are paths only,
- no evidence IDs,
- no content hashes,
- no remote/upload state,
- no transcript refs per evidence item,
- no approval/email/archive model,
- no schema version for audit pipeline.

Recommendation:

Create a separate package manifest.

### F2. Define `session_package_manifest.json`

Suggested top-level fields:

```json
{
  "schema_version": 1,
  "package_id": "pkg_...",
  "source_app": "Panda Gallery",
  "source_app_version": "4.23",
  "created_at": "...",
  "created_by": "...",
  "local_source": {
    "repo_root": "C:/panda-gallery",
    "results_path": "workflows/results_latest.json",
    "workflow_session_dir": "workflows/session_..."
  },
  "instruction_run": {
    "run_id": "...",
    "title": "...",
    "instructions_source": "...",
    "started_at": "...",
    "completed_at": "..."
  },
  "workflow_capture": {
    "session_id": "session_...",
    "metadata_path": "...",
    "audio_path": "...",
    "transcript_path": "..."
  },
  "results": [],
  "evidence": [],
  "package_files": [],
  "validation": {
    "status": "ready",
    "warnings": []
  }
}
```

### F3. Define Evidence Objects

Suggested evidence fields:

```json
{
  "evidence_id": "ev_step001_region001",
  "kind": "region_screenshot",
  "step_n": 1,
  "test_id": "P1",
  "local_path": "workflows/screenshots/.../region_1_1.png",
  "package_path": "evidence/ev_step001_region001.png",
  "remote_path": null,
  "sha256": "...",
  "bytes": 123456,
  "created_at": "...",
  "source": "manual_region_capture",
  "discarded": false,
  "transcript_refs": [],
  "frame_refs": [],
  "display_label": "Step 1 region capture 1"
}
```

Evidence kinds:

- `workflow_frame`
- `auto_fail_screenshot`
- `manual_region_capture`
- `manual_full_capture`
- `audio`
- `transcript_segment`
- `metadata`

### F4. Define AI Issue Schema Before AI Work

Suggested issue fields:

```json
{
  "issue_id": "iss_...",
  "package_id": "pkg_...",
  "session_id": "...",
  "title": "Short issue title",
  "summary": "What happened",
  "category": "ui_layout",
  "priority": "medium",
  "confidence": 0.82,
  "status": "needs_pg_review",
  "evidence_ids": ["ev_..."],
  "transcript_refs": [],
  "affected_files_guess": [],
  "suggested_response": "...",
  "created_by_model": {
    "provider": "...",
    "model": "...",
    "prompt_version": "..."
  },
  "reviewer_edits": [],
  "approval_events": []
}
```

Priority values should be finite:

- `blocker`
- `high`
- `medium`
- `low`
- `cosmetic`

Categories should be finite:

- `crash`
- `data_loss`
- `capture_failure`
- `transcription_failure`
- `ui_layout`
- `ux_confusion`
- `performance`
- `accessibility`
- `documentation`
- `other`

### F5. Define Approval, Email, And Archive Events

Approval event:

```json
{
  "event_id": "appr_...",
  "issue_id": "iss_...",
  "actor": "Darrin",
  "action": "approved_for_email",
  "timestamp": "...",
  "before_status": "needs_pg_review",
  "after_status": "approved",
  "notes": "..."
}
```

Email delivery:

```json
{
  "email_id": "email_...",
  "issue_id": "iss_...",
  "to": ["..."],
  "from": "team email",
  "subject": "...",
  "body_final": "...",
  "sent_at": "...",
  "delivery_status": "sent",
  "provider_message_id": "...",
  "error": null
}
```

Archive record:

```json
{
  "archive_id": "arch_...",
  "issue_id": "iss_...",
  "closed_at": "...",
  "closed_by": "Darrin",
  "close_reason": "resolved",
  "search_text": "normalized text blob",
  "tags": ["region-capture", "pane"],
  "evidence_ids": [],
  "email_ids": []
}
```

## G. Performance and Efficiency

### G1. The Code Is Reasonably Efficient For A Desktop App, But Has Hotspots

Good performance choices:

- preview/full render split in image processing,
- cached repo root in workflow capture,
- deferred thumbnail/freeform rendering via `QTimer.singleShot(0, ...)`,
- using `mss` for screen capture,
- audio offsets captured cheaply during callback.

Potential concerns:

- UI-thread rendering for large images can still block,
- repeated style recalculation from dynamic QSS may become expensive if overused,
- direct scene rendering mistakes have caused huge pixmap bugs before,
- N+1 DB loops in library operations are known debt.

Recommendations:

- Keep simple UI-thread work if under ~100ms.
- Avoid adding threads prematurely.
- Batch bulk UI mutations.
- Use `itemsBoundingRect()` for render/export contexts where scene margins exist.
- Add package-building progress only if package size makes UI pause visible.

### G2. Add Hashing Carefully For Package Evidence

Audit packaging needs SHA-256 hashes, but hashing large files can block UI.

Recommendation:

- For initial local prototype, synchronous hashing is acceptable if package sizes are small.
- If hashing becomes visible, run package build in a worker thread or process with progress updates.
- Keep hashing code pure and testable.

## H. Security, Privacy, And Compliance

### H1. Testing + Audit Changes Compliance Posture

Current compliance docs assume local Whisper and no PHI leaving the machine. Testing + Audit MVP introduces Dropbox, AI processing, shared email, and searchable archive.

This is a material change.

Before real patient data or external practice use:

- decide if screenshots/transcripts may contain PHI,
- decide whether de-identification is required before upload,
- list subprocessors: Dropbox, AI provider, email provider, hosting/database provider,
- determine BAA requirements,
- define retention/deletion policy,
- define access controls,
- define audit logging,
- define breach/incident procedure.

### H2. Evidence Capture Can Accidentally Include PHI

Region capture and full workflow screenshots may capture:

- patient name,
- chart number,
- image labels,
- notes,
- email/phone/address if patient panel visible,
- desktop notifications or other app windows in full capture.

Recommendation:

- Add a privacy warning to package/upload workflow.
- Consider pre-upload review or de-identification mode.
- Store `contains_phi_unknown` or `phi_review_status` in package manifest.

Possible manifest field:

```json
"privacy": {
  "contains_phi": "unknown",
  "reviewed_by": null,
  "reviewed_at": null,
  "deidentification_applied": false
}
```

## I. Specific Claude Task Prompts

These are prompt-ready task slices. Use one at a time.

### Prompt 1: Results Writer Unit Tests

Goal:

Add focused unit tests for `results_writer.py` without touching UI behavior.

Scope:

- create `test_results_writer.py`,
- use temporary directories,
- cover manual screenshot preservation and archive behavior,
- do not modify `instruction_pane.py` unless a real bug is discovered.

Acceptance:

- tests pass locally,
- no writes to live `workflows/`,
- no Qt dependency,
- no behavior change unless a failing test exposes a bug.

### Prompt 2: Instruction Schema Extraction Step 0

Goal:

Draft a safe extraction plan for instruction schema validation from `instruction_pane.py`.

Scope:

- read current loader/normalization code,
- identify pure functions,
- propose `instruction_schema.py` API,
- do not implement until plan is approved.

Acceptance:

- plan lists exact functions/blocks to move,
- plan lists tests that will protect behavior,
- plan avoids UI changes.

### Prompt 3: Package Manifest Schema Document

Goal:

Create a canonical `session_package_manifest.json` schema spec for Testing + Audit MVP.

Scope:

- use existing `results_latest.json`, workflow `metadata.json`, transcript, and screenshots as inputs,
- define evidence IDs,
- define hashes and package paths,
- define validation warnings,
- do not write code yet.

Acceptance:

- schema includes examples,
- handles missing transcript and missing screenshot,
- separates local source path from packaged path and future remote path.

### Prompt 4: Local Package Builder Prototype

Prerequisite:

Package schema approved.

Goal:

Implement a local-only package builder that reads existing PG artifacts and writes a package folder.

Scope:

- new pure module,
- no Dropbox,
- no AI,
- no UI except optional CLI script,
- tests included.

Acceptance:

- deterministic package output,
- manifest validates,
- evidence files copied,
- hashes generated,
- missing optional artifacts become warnings, not crashes.

### Prompt 5: Palette Seed For New UI Only

Goal:

Create `palette.py` and migrate only the style block touched by a current UI task.

Scope:

- no global style migration,
- define only needed constants,
- update touched QSS block,
- visual verify.

Acceptance:

- no broad diff,
- UI unchanged except intended task,
- constants names are readable.

### Prompt 6: #131 Active Focus Indicator Mockup

Goal:

Create a visual mockup for active-window focus indicator.

Scope:

- MainWindow active/inactive,
- InstructionPane active/inactive,
- show Shift+F12 mental model,
- no Python implementation yet.

Acceptance:

- Darrin can compare at least two variants,
- mockup demonstrates focus shift,
- design preserves dark PG vocabulary.

### Prompt 7: #129 Dialog Sizing Mockup And Rules

Goal:

Turn the sizing rules into an implementable visual/spec target.

Scope:

- Settings dialog at floor width,
- comfortable width,
- oversized width,
- all button clusters visible,
- multiline inputs at minimum two-line height,
- no code yet.

Acceptance:

- mockup approved,
- minimum-size formula documented,
- implementation path clear.

### Prompt 8: DB Boundary Cleanup For Library Rename/Label

Goal:

Move direct DB session usage for image rename/label operations out of `library_view.py`.

Scope:

- add named methods to `DatabaseManager`,
- update only the corresponding UI call sites,
- no UI redesign,
- no unrelated archive/restore cleanup unless same exact pattern is included intentionally.

Acceptance:

- behavior unchanged,
- session lifecycle centralized,
- manual rename/label test passes.

### Prompt 9: Transcription Alignment Unit Tests

Goal:

Add pure tests for transcript/frame alignment helpers.

Scope:

- no Whisper model load,
- no audio files,
- synthetic segment/frame dicts only.

Acceptance:

- tests run fast,
- cover pre-F12 and frame-crossing behavior,
- no changes to transcription output unless tests expose a bug.

### Prompt 10: Audit Compliance Addendum Draft

Goal:

Draft Testing + Audit compliance addendum.

Scope:

- Dropbox,
- AI provider,
- shared email,
- searchable archive,
- PHI/de-identification,
- retention/deletion,
- access control,
- audit logs.

Acceptance:

- clearly separates internal/demo data from real PHI use,
- lists decisions Darrin must make,
- does not claim legal compliance without review.

## Recommended Sequencing

### Phase 0: Stabilize Knowledge

1. Create master spec index.
2. Confirm product-track boundary: PG core v4.0 vs Testing + Audit MVP.
3. Decide whether Testing + Audit prototype handles real PHI or synthetic/demo data only.

### Phase 1: Contracts Before Code

1. Package manifest schema.
2. Evidence schema.
3. Audit issue schema.
4. Approval/email/archive schema.
5. Compliance addendum.

### Phase 2: Pure Local Vertical Slice

1. Unit-test `results_writer.py`.
2. Build local package builder.
3. Generate deterministic package from existing `workflows/` artifacts.
4. Validate manifest and evidence hashes.

### Phase 3: Minimal UI

1. Show package status in a simple desktop panel/dialog.
2. Keep it local-only.
3. No Dropbox yet.
4. No AI yet.

### Phase 4: Transfer

1. Add upload queue.
2. Add retry/idempotency.
3. Add upload-complete marker.
4. Add remote-path fields to manifest.

### Phase 5: AI Triage

1. Feed package manifest and transcript/evidence into AI extraction.
2. Generate issue JSON.
3. Keep PG approval required.
4. Preserve model metadata and prompt version.

### Phase 6: Dashboard / Approval / Archive

1. Issue queue.
2. Evidence preview.
3. Draft response editor.
4. Approval event log.
5. Shared email send.
6. Searchable archive.

## What Not To Do

Do not:

- rewrite `panda_gallery.py` wholesale,
- move all QSS to a new system in one commit,
- add Dropbox before package manifest exists,
- add AI extraction before issue schema exists,
- use `results_latest.json` as the final backend schema,
- build a dashboard before evidence identity is stable,
- clean every broad `except Exception` without understanding Qt/session failure modes,
- treat old specs as current without a master index,
- implement UI changes without mockups when visual behavior is ambiguous,
- mix multiple bugs/features in one prompt.

## Bottom Line For Claude

The strongest path is disciplined incrementalism.

Panda Gallery has enough structure and lessons to mature well, but the next layer will punish ambiguity. The Testing + Audit MVP needs contracts first, then pure local package generation, then transfer, then AI, then dashboard approval/archive.

For code quality, do not chase abstract cleanliness. Improve the codebase by making each next feature smaller, more testable, and less entangled than the last.
