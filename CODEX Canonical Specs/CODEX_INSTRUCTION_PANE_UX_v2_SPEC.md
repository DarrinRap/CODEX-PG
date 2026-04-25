# CODEX Instruction Pane UX v2 Spec

Status: Proposed delta spec for Claude/CC review
Date: 2026-04-25
Author: Codex
Output path: `C:\CODEX PG\CODEX Canonical Specs\CODEX_INSTRUCTION_PANE_UX_v2_SPEC.md`

Read-only source references:

- `C:\panda-gallery\TESTING_SECTION_SPEC.md` Draft 6
- `C:\panda-gallery\GUIDED_TESTING_STYLE.md`
- `C:\panda-gallery\skills\pg-instruction-pane-author\SKILL.md`
- `C:\panda-gallery\BUGS.md` #135 and #136
- `C:\panda-gallery\workflows\instructions_latest.json`
- `C:\panda-gallery\workflows\audit\AM_v0_smoke_checklist.html`
- `C:\panda-gallery\instruction_pane.py` read-only orientation

Boundary: this document proposes UX/spec deltas only. It does not authorize implementation and does not edit `C:\panda-gallery`.

## 1. Purpose

The Instruction Pane is the primary manual-test venue for Panda Gallery. Draft 6 already defines the right foundation: local UI, MCP passive-read, schema v2, strict XOR validation, results archive, screenshot capture, editable prior answers, checklist steps, action steps, review-all, and Claude-authored follow-up questions.

The real-use failure on 2026-04-25 was not architectural absence. It was tester abandonment. A 15-step AM v0 polish run became easier to do on paper because the pane could not safely handle accidental Esc, could not record a caveated pass, did not give enough mid-run orientation, and made action-only steps feel like noise.

This spec proposes a v2.1 delta that keeps Draft 6 intact and fixes those daily-loop failures.

## 2. Current Failure Evidence

### 2.1 Reported tester pain

Darrin reported, in substance:

- Too many tests.
- No way to make notes on steps that broadly pass but have small errors.
- Too many click-only questions.
- Pressing Esc can force the questionnaire to restart.
- Some questions are unclear, such as references to "table B".
- The Instruction system is clunky enough that a paper checklist was preferable.

### 2.2 Concrete triggering plan

`workflows/instructions_latest.json` currently contains a 15-step AM v0 polish smoke. The plan mixes:

- `kind: "action"` setup/navigation steps: launch dev mode, open AM, open bug #132, dismiss move dialog.
- Single-expected checks: filter behavior, triage run, dark-dialog substitution, build prompt, close window.
- Checklist visual checks: menu placement, window shell, bug list, header, stage rail, triage panel.

The plan is valid under Draft 6, but it exposes the UX gap: valid does not necessarily mean humane at the keyboard.

### 2.3 Paper workaround signal

`workflows/audit/AM_v0_smoke_checklist.html` collapsed the run into a printable table with PASS/FAIL boxes and a notes column. That table removed friction in three ways:

- It made the full run visible at once.
- It allowed passing rows to carry notes.
- It let the tester skip around and mark observations without losing orientation.

The pane should absorb those advantages instead of treating paper as failure outside the system.

## 3. Design Goals For v2.1

1. Never silently lose progress.
2. Let a tester say "passed, but note this" without corrupting pass-rate metrics.
3. Make a 10-15 step run navigable without needing memory or paper.
4. Keep action/setup steps visually distinct and low-friction.
5. Catch likely authoring mistakes before the tester reaches them.
6. Provide paper-mode export as a supported fallback, not an ad hoc workaround.
7. Preserve backward compatibility with existing schema v1 and v2 instruction files.

## 4. Non-Goals

- No implementation in this pass.
- No rewrite of `TESTING_SECTION_SPEC.md`.
- No change to the MCP passive-read architecture.
- No AI or LLM inside the pane.
- No automatic photo/OCR re-ingestion requirement for paper-mode v2.1.
- No schema break for existing `workflows/*.json` v2 files.

## 5. Recommended Delta Summary

Recommended implementation shape:

1. Add a safe Esc dispatcher that never resets run state without explicit confirmation.
2. Extend result outcome support with `PASS_WITH_NOTE` for step-level caveated passes.
3. Add a persistent compact run header with progress, remaining count, and outcome dots.
4. Add a mid-run index/review drawer reachable from the header.
5. Keep `kind: "action"`, but restyle it as setup/navigation and lint overuse.
6. Add non-blocking authoring lint warnings surfaced in About and optionally on load.
7. Add paper-mode export to `workflows/audit/<run_id>_paper.html`.
8. Keep all changes backward-compatible under schema v2.1.

## 6. Esc Handling Delta

### 6.1 Current problem

Bug #135 records that pressing Esc mid-run can return the pane to step 1 and discard prior PASS/FAIL/SKIP answers without confirmation. This violates Draft 6 goal 3: no data loss under any condition.

### 6.2 Required behavior

Esc must route through one dispatcher. The dispatcher resolves intent in this order:

1. If a FAIL/PASS note panel is open, close that panel and preserve the existing step state.
2. If the About panel is open, close About.
3. If a question view is open, return to the step view and leave the question pending unless an answer was explicitly submitted.
4. If the mid-run index/review drawer is open, close the drawer.
5. If a modal confirmation dialog is open, let the dialog handle Esc according to its own button policy.
6. If no inline panel or drawer is open, Esc is a no-op by default.

Reset/restart must not be reachable from bare Esc. If restart remains available, it must be a named command such as "Run same test again" or "Restart run" and must show `DarkConfirmDialog`.

### 6.3 Confirmation copy

If reset/restart is requested intentionally:

Title: `Restart this run?`

Body: `This will archive the current answers and start again at step 1. Nothing will be deleted, but your current run will be closed.`

Buttons: `Restart` and `Keep working`

Default: `Keep working`

Esc in this dialog selects `Keep working`.

### 6.4 Spec amendment target

Amend `TESTING_SECTION_SPEC.md` section 5.4 keyboard map:

- Step view: `Esc` = close inline surface if one is open; otherwise no-op.
- FAIL/note panel: `Esc` = close panel, no result written.
- Review/index drawer: `Esc` = return to current step.
- Summary view: `Esc` = close summary only if that is already the dialog-wide close convention; never restart.

## 7. Outcome Model Delta: PASS_WITH_NOTE

### 7.1 Current problem

Bug #136 records that a tester cannot mark a step as passed while preserving a caveat. The current choices force bad data:

- Press PASS: pass-rate is correct, observation is lost.
- Press FAIL: observation is preserved, pass-rate is wrong.

### 7.2 Recommendation

Add a step-level outcome: `PASS_WITH_NOTE`.

This is explicit enough to discover in the UI and unambiguous enough in results. Prefer a third footer button over a small icon-only note affordance.

Recommended footer for single-expected steps:

- `PASS`
- `PASS + NOTE`
- `FAIL`

Recommended footer for checklist steps:

- Keep per-item `PASS / FAIL / SKIP` unchanged.
- Add a step-level `+ Note` affordance in the footer once at least one item has been answered, or beside the checklist summary strip.
- If all checklist items are PASS/SKIP and the step-level note is non-empty, derived step outcome becomes `PASS_WITH_NOTE`.
- If any checklist item FAILs, derived step outcome remains `FAIL`; the step-level note may still exist as context but does not override failure.

### 7.3 Why a third button

A visible `PASS + NOTE` button solves the discoverability problem Darrin hit. A pencil icon next to PASS is compact, but easy to miss under stress. This pane is a manual test cockpit, not a dense toolbar; the outcome path should be obvious.

### 7.4 UI flow

Pressing `PASS + NOTE` opens the same note panel family as FAIL, but with different title and submit copy.

Panel title: `PASS WITH NOTE - what should Claude know?`

Textarea: required, 2-3 line default height, same capped behavior as `_FailNoteEdit`.

Buttons: `SAVE NOTE` and `Back`

Submit behavior:

- Writes outcome `PASS_WITH_NOTE`.
- Writes `note` string.
- Does not auto-capture a FAIL screenshot by default.
- Advances like PASS.

Manual `Capture now` remains available before saving the note if visual evidence matters.

### 7.5 Results semantics

For pass-rate and progress:

- Treat `PASS_WITH_NOTE` as pass for advance, completion, and green dot math.
- Preserve it as a distinct outcome for summary and report rendering.
- Summary text should show both counts, for example: `12 pass - 2 pass with note - 1 fail`.

For dot strips:

- Default recommendation: render `PASS_WITH_NOTE` as green dot with a small note marker in text rows, not amber.
- Do not use amber for pass-with-note unless Darrin decides caveated passes should visually warn like skipped/failed states.

### 7.6 Schema delta

This should be schema v2.1, backward compatible with v2:

Single-expected result entry:

```json
{
  "step_n": 6,
  "test_id": "T6_filter_change",
  "title": "Filter behavior",
  "outcome": "PASS_WITH_NOTE",
  "note": "List updated correctly, but dropdown popup text contrast was too low.",
  "screenshot": null,
  "manual_screenshots": [],
  "claude_qa": [],
  "timestamp": "2026-04-25T13:22:10"
}
```

Checklist item result entries may also accept `PASS_WITH_NOTE` later, but v2.1 should avoid per-item note buttons unless real use proves they are needed. Start with step-level notes to keep checklist UI usable.

## 8. Long-Run Navigation Delta

### 8.1 Current problem

Draft 6 has a review-all screen, but it appears after the last step is answered. That is too late for a long run. During step 5 of 15, the tester needs to know:

- Where am I?
- How many are left?
- What did I already mark?
- Can I jump back without losing answers?
- Can I skim the rest before committing attention?

### 8.2 Persistent compact header

Amend the persistent header to show:

- `Step N of M`
- `R remaining`
- Current `test_id`
- A compact outcome strip for all steps
- An index button

Example text shape:

`Step 8 of 15 - 7 remaining - T8_screen_b_header`

Outcome strip states:

- pending: muted ring
- current: peach ring
- pass: green fill
- pass with note: green fill plus tiny note marker in tooltip/text
- fail: red fill
- skip: grey dash
- action acknowledged: muted check or neutral fill

Tooltips should show `Step N - title - outcome`.

### 8.3 Mid-run index drawer

Add an index drawer or compact review panel reachable from the header. It can reuse the review-all row model but must be available at any time.

Each row should show:

- step number
- test_id
- title
- kind badge: `Check`, `Checklist`, or `Setup`
- outcome badge
- note indicator if present
- jump/review action

Rules:

- Jumping to an answered step shows editable prior-answer state.
- Jumping to an unanswered future step is allowed for skimming, but the footer should show `Resume first unanswered` if the tester is about to create gaps.
- No answer is lost by navigation.
- The first unanswered step remains the default resume target.

### 8.4 Remaining count

The pane should show a simple count independent of dot parsing:

- `7 remaining` on in-progress step view.
- `All answered - review before finish` once complete.

Action steps count as remaining until acknowledged, but should be visually lightweight.

## 9. Action Step Kind Delta

### 9.1 Current state

`kind: "action"` was added to solve bug #125: PASS/FAIL is wrong for pure setup/navigation. The current result shape records action steps as `kind: "action"`, `outcome: "ACK"`.

The kind should survive. The failure was not the concept. The failure was that action steps felt like low-value click questions in a long run.

### 9.2 Recommended UX

Restyle action steps as setup/navigation, not as test questions.

Visual treatment:

- Title prefix or badge: `SETUP`
- Muted body block, no EXPECTED box
- Single primary footer button: `Done`
- Outcome strip state: neutral acknowledged, not green pass
- Summary/report: collapsed by default under `Setup steps acknowledged`

Copy recommendation:

- Prefer `Done` over `Got it` for tester flow. `Got it` reads like reading comprehension; `Done` reads like a completed setup action.

### 9.3 Authoring constraints

Action steps are allowed only when all are true:

- The step changes app state needed for a later observation.
- There is no meaningful observable assertion on this step.
- Combining it into the adjacent observation step would make the body too dense or sequentially ambiguous.

If an action step is immediately followed by one checklist step and the action is a single short command, authoring lint should suggest folding it into the checklist body.

### 9.4 Migration

Existing v2 files with `kind: "action"` continue to load unchanged. The v2.1 UI simply renders them with the improved setup treatment.

No schema migration is required for action steps.

## 10. Authoring Guardrails Delta

### 10.1 Current problem

The loader enforces structural validity, but not human clarity. The AM plan was schema-valid while still containing unclear references such as `Screen B` and template-ish labels that were not meaningful to the tester.

### 10.2 Lint, not rejection

Add a non-blocking lint pass after schema validation and before render. Structural errors still reject. Lint warnings do not block the run.

Warnings should surface in:

- About panel under `Authoring warnings`.
- Optional first-load banner: `3 authoring warnings - Review`.
- Results metadata so Claude can see that the plan itself had quality concerns.

### 10.3 Warning shape

Proposed warning object:

```json
{
  "step_n": 8,
  "test_id": "T8_screen_b_header",
  "code": "ambiguous_reference",
  "severity": "warning",
  "message": "Title/body references 'Screen B' without defining it in this step.",
  "field": "title"
}
```

### 10.4 Initial lint rules

Start with these rules:

- `placeholder_title`: title matches common template patterns such as `B1 - ...`, `Step N - ...`, `Screen A/B`, or table references without local definition.
- `unknown_reference`: body or expected references `table`, `screen`, `panel`, `section`, `B`, `C`, etc. without prior context in the same step or top-level context.
- `compound_body`: body contains multiple imperatives joined by `and`, `then`, semicolon chains, or numbered substeps.
- `action_overuse`: more than 20 percent of steps are action steps in a run with more than 5 steps.
- `action_can_fold`: an action step is followed by a checklist/single-expected step and could fit as the first sentence of that step body.
- `long_run`: more than 10 steps; suggest paper export and mid-run index.
- `long_checklist`: checklist has more than 6 items; Draft 6 says checklist becomes a wall.
- `paraphrased_expected`: expected uses vague phrases such as `looks right`, `works`, `updates correctly`, `message appears` without exact text when exact UI text should be known.
- `external_dependency`: body mentions PowerShell, shell, browser, file explorer, registry, scripts, or debug tools.

### 10.5 Where to amend existing rules

Amend `TESTING_SECTION_SPEC.md`:

- Section 4.4: keep strict XOR errors, then add lint pass.
- Section 9.10: add self-review items matching the automated lints.
- Section 10: add Claude-side memory rule that Claude reads authoring warnings when present and treats them as plan-quality feedback.

## 11. Paper-Mode Export

### 11.1 Purpose

Paper-mode is not a retreat from the pane. It is a supported fallback for long, visual, or high-friction smoke runs.

The must-have is export, not re-ingestion.

### 11.2 Output

Generate:

`workflows/audit/<run_id>_paper.html`

The file should be print-styled, single-document HTML, with no network dependencies.

### 11.3 Layout

Recommended columns:

- `#`
- `Step`
- `PASS / PASS+NOTE / FAIL / SKIP / DONE`
- `Notes`

Rendering rules:

- Single-expected step: show body, expected, PASS/PASS+NOTE/FAIL boxes.
- Checklist step: show body plus checkbox bullets for each checklist item; row-level outcome boxes remain at the right.
- Action step: show body and a `DONE` box only.
- Include run title, generated timestamp, tester/date blanks, and source file path.
- Notes column should be wide enough for handwritten caveats.

### 11.4 UI entry points

Add a header action with tooltip:

- Button: print/export icon if available, otherwise `Paper`
- Tooltip: `Export printable checklist`

Also allow a CLI/dev command for Claude/CC:

`python -m workflows.export_instruction_paper workflows/instructions_latest.json`

Exact module name can change during implementation; the capability matters more than the name.

### 11.5 Re-ingestion

Deferred. Acceptable v2.1 loop:

1. Tester prints or opens paper HTML.
2. Tester fills by hand or annotates digitally.
3. Tester photographs or screenshots the completed sheet.
4. Claude reads the image from chat or local file if Darrin provides it.

Future v2.2 may add manual transcription back into `results_latest.json`, but that should not block export.

## 12. Compatibility And Migration

### 12.1 Instruction schema

Do not break existing v1 or v2 instruction files.

Recommended top-level behavior:

- `schema_version: 1`: load as today.
- `schema_version: 2`: load as today, with v2.1 UI improvements available.
- `schema_version: 2.1`: optional future marker if authored files need to declare new instruction-side capabilities.

The `PASS_WITH_NOTE` change is primarily a results schema extension, not an instruction schema requirement. Existing instruction files can produce the new result outcome without changing their JSON.

### 12.2 Results schema

Bump results file to schema version 1.1 or add a capabilities block while preserving existing readers.

Backward-compatible shape:

```json
{
  "schema_version": 1,
  "result_schema_minor": 1,
  "capabilities": ["pass_with_note", "authoring_warnings", "paper_export"],
  "results": []
}
```

Existing readers that only inspect `results[]` continue to work. New readers can use `result_schema_minor` or `capabilities`.

### 12.3 Existing outcomes

Existing consumers must continue to accept:

- `PASS`
- `FAIL`
- `SKIP`
- `ACK`

New consumers should accept:

- `PASS_WITH_NOTE`

If an older report generator sees unknown outcome, it should render it as text rather than crash.

### 12.4 Existing action files

No migration needed. Existing `kind: "action"` steps continue to load; v2.1 changes visual treatment and lint warnings only.

## 13. Implementation Notes For CC

This is not an implementation order requirement, but a safe decomposition would be:

1. Esc dispatcher and regression test first, because it prevents data loss.
2. PASS_WITH_NOTE for single-expected steps.
3. PASS_WITH_NOTE/report rendering in results and summary.
4. Header outcome strip and remaining count.
5. Mid-run index drawer.
6. Action-step restyle.
7. Authoring lint warnings.
8. Paper-mode export.

Potential touch points:

- `instruction_pane.py`: footer buttons, note panel reuse, Esc dispatch, header/index UI, action rendering, About warnings.
- `results_writer.py`: outcome enum handling, note field, pass-rate summary, capabilities/minor schema.
- `TESTING_SECTION_SPEC.md`: section deltas only.
- `GUIDED_TESTING_STYLE.md`: authoring guardrail updates.
- New exporter module under `workflows` or another repo-approved location.

Do not implement by special-casing the AM v0 plan. The pane needs general tester resilience.

## 14. Acceptance Criteria

A v2.1 implementation should pass these manual checks:

1. Start a 5+ step run, answer several steps, press Esc on the step view. Progress remains intact and current step remains visible.
2. Open FAIL panel, press Esc. Panel closes and no result is written.
3. Press `PASS + NOTE`, enter a caveat, save. Step advances; results contain `PASS_WITH_NOTE` and the note.
4. Complete a run with one pass-with-note. Summary separates pass-with-note from fail and treats it as pass for completion.
5. Open a 15-step run. Header shows current step, remaining count, and outcome strip.
6. Open mid-run index, jump to an answered step, return/resume without losing answers.
7. Action steps render as setup/done, not as normal observation questions.
8. Load the AM v0 polish plan. About panel shows relevant authoring warnings without blocking the run.
9. Export paper mode. HTML contains all non-action checks, action setup rows, PASS/PASS+NOTE/FAIL boxes, and notes column.
10. Existing v2 instruction files still load and can produce ordinary PASS/FAIL/SKIP/ACK results.

## 15. Open Questions For Darrin

1. Should `PASS_WITH_NOTE` render as green with note marker, or amber as a caution state?
2. Should the footer button label be `PASS + NOTE`, `PASS WITH NOTE`, or `PASS, note`?
3. Should checklist items eventually support item-level `PASS_WITH_NOTE`, or is step-level note enough?
4. Should `kind: "action"` survive long-term, or should authors be pushed harder to fold setup into adjacent observation steps?
5. Should paper export be automatic on every run load, or opt-in from the pane/header/CLI?
6. Should future paper re-ingestion create structured `results_latest.json`, or is Claude reading the photographed checklist sufficient?
7. Should bare Esc on an idle step view close the pane, or remain a no-op? This spec recommends no-op to avoid data loss.

## 16. Proposed Draft 6 Amendment Map

If accepted, amend Draft 6 as follows:

- Section 1 Goals: add caveated pass capture and mid-run orientation.
- Section 4.4 Loader strictness: add non-blocking lint warnings after strict validation.
- Section 5.1 Step view: add persistent outcome strip, remaining count, index entry point, and PASS + NOTE footer.
- Section 5.2 FAIL flow: generalize panel to note panel family; add pass-note variant.
- Section 5.4 Keyboard map: replace Esc reset/cancel behavior with safe dispatcher.
- Section 5.5 Navigation model: add mid-run index and safe jump rules.
- Section 5.7 Review-all screen: make the same row model available mid-run.
- Section 7.1 Results file: add `PASS_WITH_NOTE`, note semantics, warning/capabilities metadata.
- Section 9 Authoring rules: add lint-backed anti-patterns surfaced by today's AM v0 pain.
- New section: Paper-mode export.

## 17. Final Recommendation

Ship v2.1 as a resilience pass, not a cosmetic pass. The highest priority is data safety plus pass-with-note. Without those, the pane cannot be trusted. Next comes long-run orientation. Paper export should follow quickly because Darrin already proved it is the fallback he reaches for when the pane gets in his way.

