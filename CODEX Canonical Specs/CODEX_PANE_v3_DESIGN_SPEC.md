# CODEX_PANE_v3_DESIGN_SPEC

## 1. Status / Metadata

Status: Draft v1 for Claude implementation planning

Owner: Codex

Requested by: Claude dispatch to Codex mailbox

Primary output: `C:\CODEX PG\CODEX Canonical Specs\CODEX_PANE_v3_DESIGN_SPEC.md`

Created: 2026-04-25

Scope: Instruction Pane v3 design, schema, UX behavior, lint expectations, and implementation sequencing.

Decision posture: This document is a fresh v3 design contract. It preserves shipped safety behavior and proven architecture, but it does not treat v2.1.1 as the layout or content template.

## 2. Read-Only Source References

The following files were read as references only. This spec does not modify any file under `C:\panda-gallery`.

- `C:\panda-gallery\workflows\audit\PANE_v3_REDESIGN_BRIEF_v1.md`
- `C:\panda-gallery\workflows\audit\PANE_UX_DIAGNOSTIC_v1.md`
- `C:\panda-gallery\workflows\audit\INSTRUCTION_AUTHORING_BEST_PRACTICES_v1.md`
- `C:\CODEX PG\CODEX Canonical Specs\CODEX_INSTRUCTION_PANE_UX_v2_SPEC.md`
- `C:\panda-gallery\TESTING_SECTION_SPEC.md`
- `C:\panda-gallery\workflows\audit\AM_v0_smoke_checklist.html`
- `C:\panda-gallery\instruction_pane.py`
- `C:\panda-gallery\results_writer.py`
- `C:\panda-gallery\BUGS.md`

Reference interpretation:

- `PANE_v3_REDESIGN_BRIEF_v1.md` is the controlling brief for v3.
- `PANE_UX_DIAGNOSTIC_v1.md` explains why v2 felt stressful and where the v3 design must change.
- `INSTRUCTION_AUTHORING_BEST_PRACTICES_v1.md` defines the content quality bar for authored instructions.
- `CODEX_INSTRUCTION_PANE_UX_v2_SPEC.md` supplies retained safety behavior and prior unresolved ideas, but is not a v3 template.
- `TESTING_SECTION_SPEC.md` supplies current schema and result persistence context.
- `AM_v0_smoke_checklist.html` is the paper-mode baseline v3 must beat.
- `instruction_pane.py`, `results_writer.py`, and `BUGS.md` ground the spec in shipped behavior and known issues.

## 3. Boundary Statement

Codex writes this spec only under `C:\CODEX PG`.

`C:\panda-gallery` remains read-only reference material unless Darrin explicitly authorizes a separate implementation pass there.

This document is not permission to edit implementation files. It is a design and sequencing artifact for Claude or a later implementation agent.

## 4. Purpose

Pane v3 exists to make guided manual testing feel calm, clear, and trustworthy for Darrin while preserving the useful automation and result structure already built into the pane.

The previous pane had the right strategic concept: keep the tester inside the app, record structured outcomes, and guide the run step by step. The failure was not the concept. The failure was the authoring shape and interaction feel. Dense body text, weak visual anchoring, modal FAIL-only notes, silent advancement, and separated action controls made the pane feel like a chore instead of a companion.

Pane v3 must do three things at once:

- Beat the paper checklist by keeping the full run navigable, notes always available, and progress visible.
- Keep structured results that Claude can consume without scraping prose.
- Reduce tester stress through voice, pacing, and confirmation clarity.

The design center is one tester in one moment. The pane should answer:

- Why am I doing this?
- What exactly do I do now?
- How do I know whether it worked?
- Where can I leave an observation without losing my place?

## 5. Retain List

The following behavior and architecture must be retained.

1. Esc dispatcher behavior

   Retain the shipped `_dispatch_escape` priority order from v2.1.1 section 6.2. Esc walks the active closeable surface stack. Bare Esc is a no-op when no panel is open. This shipped in commit `d73598b` and closed bug #135.

2. Restart confirmation helper

   Retain the `DarkChoiceDialog` restart confirmation helper and v2.1.1 section 6.3 copy pattern. Restart remains a deliberate destructive action.

3. Schema-level XOR validation

   Retain strict per-step mode validation. Each step has exactly one of:

   - `kind: "action"`
   - `expected`
   - `checklist`

   A step with none or more than one is invalid.

4. Structured result persistence

   Retain `workflows/results_latest.json` as the current-run result artifact. Continue writing structured outcome entries with step number, test id, title, outcome, note, screenshot fields, manual screenshot fields, Claude QA fields, and timestamps.

5. MCP passive-read architecture

   Retain passive-read behavior. The pane can guide, record, and export, but it should not mutate app state through hidden automation.

6. Existing instruction read compatibility

   Continue reading existing v1 and v2 instruction files. Legacy files should remain testable without forced conversion.

7. Action/setup step support

   Retain action/setup steps. They are real steps, not comments or headings, and they continue to record a structured acknowledgement.

8. Paper-mode export concept

   Retain an export path for printable review. v3 should improve it to match the new schema rather than dropping it.

## 6. Replace List

Pane v3 replaces the following v2 patterns.

1. Replace the `body` blob

   The v3 instruction unit is no longer a body paragraph. It is `why`, `what_to_do`, and `confirmation`, with optional anchors and notes guidance.

2. Replace FAIL-only modal notes

   Notes are persistent and inline. They are available before and after an outcome, including PASS, FAIL, SKIP, checklist items, and action steps.

3. Replace silent advancement

   Advancing records a visible acknowledgement before or during the move to the next step. The tester should never wonder whether the click was accepted.

4. Replace the separated Next row

   PASS, FAIL, SKIP, and DONE controls live in the action bar and perform the advance for terminal single-step outcomes. There is no extra Next click for single expected or action steps.

5. Replace internal placeholders and jargon

   Authoring lint rejects internal implementation terms, placeholder labels, schema leakage, file path instructions to the tester, and vague UI references.

6. Replace `expected` as the only success-language field

   Success language lives in `confirmation`. `expected` remains a machine-readable single-observation mode field, but the user-facing pane explains success through confirmation copy.

7. Replace long body paragraphs

   v3 enforces compact instruction text. Any single `why`, `what_to_do`, or `confirmation` field over 80 words is a warning; over 120 words is invalid unless a future exception mechanism is explicitly added.

8. Replace hidden full-run context

   v3 must provide an index drawer and progress surface so the tester can see where they are, what is done, what has notes, and what remains.

## 7. The Four Foundations

### Foundation 1: Voice

Goal: The pane should sound like calm guidance from a competent partner, not like implementation notes.

Schema implications:

- Steps require `why`, `what_to_do`, and `confirmation`.
- Titles must be short and task-facing.
- Optional `note_prompt` can customize the inline note placeholder, but cannot replace the note field.
- Authoring metadata may contain implementation details, but tester-visible fields may not.

UX implications:

- Section labels are plain and consistent:
  - `Why this matters`
  - `Do this`
  - `You can mark pass when`
  - `Note`
- The pane avoids scolding language. FAIL is a valid observation, not a mistake.
- Acknowledgement copy is brief and confidence-building, such as `Recorded PASS` or `Saved note and marked FAIL`.

Lint implications:

- Reject terms that expose implementation mechanics to the tester, including schema field names, class names, method names, raw file paths, "Screen A/B" placeholders, and engineering-only verbs.
- Reject empty reassurance and filler, such as "simply", "obviously", or "just" when it weakens the instruction.
- Warn when a title describes an internal artifact instead of the visible task.

### Foundation 2: Why -> What -> Confirmation

Goal: Every step tells the tester why they are doing it, what to do, and how to confirm the result.

Schema implications:

- `why`: required string, 1 to 80 words, hard invalid above 120 words.
- `what_to_do`: required string, 1 to 80 words, hard invalid above 120 words.
- `confirmation`: required string, 1 to 80 words, hard invalid above 120 words.
- `expected`, `checklist`, or `kind: "action"` chooses result mode, not the prose structure.

UX implications:

- The three fields are always shown in order.
- `why` is visually quieter than `what_to_do`; it orients but does not compete.
- `confirmation` is visually tied to outcome controls so the tester sees the pass/fail basis before clicking.
- For action steps, `confirmation` is rendered as `Ready for next step when`.

Lint implications:

- Reject steps where `what_to_do` contains multiple independent tasks that should be separate steps.
- Warn when `why` merely repeats the title.
- Reject missing confirmation.
- Reject confirmation text that does not contain observable evidence.

### Foundation 3: Anchored Content

Goal: Any instruction that points at UI must say what text to find, where it is, and what it should look like or do.

Schema implications:

- Steps may include an `anchors` array.
- Each anchor has:
  - `text`: exact visible UI text, icon label, or control label.
  - `where`: visible region or container, such as `top menu bar` or `left filter strip`.
  - `expect`: what the tester should see or how the element behaves.
- Checklist items may also include anchors when the anchor is item-specific.

UX implications:

- Anchors render as small reference rows under `Do this`, not as decorative tags alone.
- Anchor rows should be scan-friendly and not interrupt the main instruction.
- If an anchor references exact UI text, use quotation marks in the rendered copy.

Lint implications:

- Warn when a step names a UI surface without `anchors`.
- Reject placeholder anchors such as `Screen A`, `left thing`, `button`, or `panel`.
- Warn when `where` is not spatial enough for a tester to find the element.

### Foundation 4: Frictionless Interaction

Goal: The pane should minimize needless clicks while keeping the tester aware of what was recorded.

Schema implications:

- Outcome buttons can derive directly from the step mode.
- Notes are orthogonal to outcomes. A note never changes PASS into a different result type.
- Action steps use `kind: "action"` and record an acknowledgement outcome.

UX implications:

- Single expected steps show PASS, FAIL, and SKIP in the sticky action bar.
- Action steps show DONE in the same action-bar location.
- Checklist steps keep row outcomes close to each row and keep the step-level action area stable.
- The note field is always visible, compact by default, and persists while navigating.
- PASS, FAIL, SKIP, and DONE record immediately and advance for single expected and action steps.
- A persistent acknowledgement strip confirms the recorded result.

Lint implications:

- Warn when a step requires an extra confirmation click in prose, such as "then click Next."
- Reject instruction text that tells the tester to record results somewhere outside the pane.
- Warn when checklist rows are too long to keep row controls visible.

## 8. Open Questions Resolved

### 8.1 PASS Note Field Structure

Decision: A PASS with a note remains `outcome: "PASS"` with a separate `note` field. Do not introduce `PASS_WITH_NOTE` as a new persisted outcome enum in v3.

Rationale:

- A note is metadata, not an outcome.
- The current result writer already models single-step results as `outcome` plus `note`.
- Keeping PASS as PASS avoids forcing every downstream reader to understand a fourth success-like state.
- The UI can still label the summary as `PASS + note` when `note` is non-empty.

Required structure:

```json
{
  "step_n": 3,
  "test_id": "testing-menu-placement",
  "title": "Check the Testing menu",
  "outcome": "PASS",
  "note": "Menu is present; spacing is tighter than the mockup.",
  "screenshot": null,
  "manual_screenshots": [],
  "claude_qa": [],
  "timestamp": "2026-04-25T19:10:00"
}
```

Rules:

- `note` is `null` or a trimmed string.
- Empty strings persist as `null`.
- Recommended note limit: 500 characters stored, with a 300 character soft warning in UI.
- Notes are plain text only.
- The summary/export layer may derive `has_note: true`, but this does not need to be persisted.

Checklist note handling:

- Each checklist item may have its own `note`.
- The checklist step may also have a step-level `note` for overall context.
- Step outcome is still derived from item outcomes.

### 8.2 Acknowledgement Persistence

Decision: Acknowledgements persist as a compact recent-activity strip, not as a transient toast only.

UX requirement:

- After a result is recorded, show an acknowledgement such as `Recorded PASS for Step 3`.
- Keep the last three acknowledgements visible in a compact strip or drawer summary.
- Acknowledgements roll off when newer ones arrive; they do not disappear on a timer.
- The current step header should also show the last recorded state when revisiting a completed step.

Rationale:

- The v2 issue was silent advance. A timer-based toast can still be missed.
- Persistent acknowledgement helps the pane feel reliable without adding another click.

Persistence requirement:

- The canonical persisted artifact remains the result entry timestamp and outcome.
- A separate UI-only acknowledgement list may be rebuilt from recent result entries.

### 8.3 Mid-Run Navigation

Decision: v3 includes a pane-native index drawer plus a compact progress header.

UX requirement:

- The header shows current position, such as `Step 4 of 9`.
- The index drawer shows every step in order with:
  - step number
  - short title
  - status: not started, PASS, PASS + note, FAIL, SKIP, DONE, or incomplete checklist
  - note marker
  - failed checklist count when relevant
- Selecting a step jumps to it without clearing draft notes or existing results.
- Returning from a jumped step resumes the visible current step unless the user records a new outcome there.

Rationale:

- The paper checklist won on whole-run visibility. The pane needs full-run awareness without abandoning guided focus.
- Mid-run navigation is also the safer way to edit an earlier answer.

### 8.4 Action / Setup Step Affordance

Decision: Action/setup steps remain `kind: "action"`, render with a SETUP badge, and use a DONE button. They still require `why`, `what_to_do`, and `confirmation`, but the confirmation label changes to `Ready for next step when`.

Schema rule:

- `kind: "action"` must not include `expected` or `checklist`.
- `confirmation` is required and describes the ready state, not a pass criterion.

Result rule:

- UI label: `DONE`
- Stored outcome: `ACK`
- Optional note may be stored if the tester typed one.

Rationale:

- Setup work still needs orientation and a completion condition.
- The tester should not have to choose PASS/FAIL for a step whose purpose is preparation.
- Keeping `ACK` in the machine result preserves current semantics while allowing friendlier UI copy.

### 8.5 Lint Pass Scope / Enforcement

Decision: v3 uses both write-time lint and load-time enforcement.

Write-time:

- Authoring tools should run full v3 lint before publishing instructions.
- Errors block publication.
- Warnings should be visible and fixable before dispatch.

Load-time:

- The pane rejects v3 instruction files with schema errors or lint errors.
- The pane may load v3 files with lint warnings but should show a developer-facing warning in diagnostics, not tester-facing noise.
- Legacy v1/v2 files are not rejected for v3 content lint. They load in legacy mode.

Error examples:

- Missing `why`, `what_to_do`, or `confirmation`.
- More than one of `kind: "action"`, `expected`, or `checklist`.
- Tester-visible file path.
- Placeholder UI labels such as `Screen A` or `TODO`.
- Any single visible field over 120 words.

Warning examples:

- `why` repeats title.
- No anchors for a UI-heavy step.
- Any visible field over 80 words.
- Checklist item label too long for stable row controls.

### 8.6 Schema Version Transition

Decision: v3 introduces `schema_version: 3` for instruction files and keeps v1/v2 readable through legacy rendering.

Rules:

- v3 files use the v3 schema and v3 pane layout.
- v1/v2 files continue to load without forced migration.
- v1/v2 files render in legacy-compatible mode with retained safety fixes.
- The pane should show a small developer-facing legacy indicator outside the tester's main step content.
- No automatic save-back migration occurs when opening a legacy file.
- A separate authoring tool may produce a v2-to-v3 draft, but that is outside pane runtime.

Rationale:

- Existing testing assets remain usable.
- v3 can enforce a higher bar without breaking historical instructions.
- Runtime auto-migration risks changing testing meaning invisibly.

### 8.7 Paper-Mode Export

Decision: Keep and improve paper-mode export.

Paper export must include:

- step number
- title
- why
- what to do
- confirmation
- anchors, if present
- PASS/FAIL/SKIP or DONE boxes
- note space
- checklist item rows for checklist steps

Rules:

- Paper export is opt-in.
- Paper export does not become the source of truth.
- The pane does not need to re-ingest handwritten paper results.
- Export should preserve the same language the tester sees in the pane.

Rationale:

- The paper checklist is the competitive baseline.
- Export helps review, archival, and fallback testing.
- A good paper export forces the v3 schema to stay clear and scannable.

## 9. Schema v3

### 9.1 Top-Level Shape

```json
{
  "schema_version": 3,
  "title": "Audit Manager smoke check",
  "instructions_id": "am-smoke-2026-04-25",
  "audience": "Darrin",
  "created_by": "Claude",
  "created_at": "2026-04-25T19:00:00",
  "lint_profile": "pane_v3",
  "steps": []
}
```

Required top-level fields:

- `schema_version`: integer, exactly `3`.
- `title`: non-empty string.
- `steps`: non-empty array.

Recommended top-level fields:

- `instructions_id`: stable slug for result linking.
- `audience`: intended tester.
- `created_by`: authoring agent or person.
- `created_at`: ISO timestamp.
- `lint_profile`: `pane_v3`.

### 9.2 Common Step Shape

```json
{
  "id": "testing-menu-placement",
  "title": "Check the Testing menu",
  "why": "This confirms the tester can find the new testing workflow from the main app chrome.",
  "what_to_do": "Look at the top menu bar and open the Testing menu.",
  "confirmation": "The Testing menu is visible in the top menu bar and opens without shifting the window.",
  "anchors": [
    {
      "text": "Testing",
      "where": "top menu bar",
      "expect": "A menu label between the existing app menus"
    }
  ],
  "expected": "The Testing menu opens and shows the testing commands.",
  "note_prompt": "Optional observation about placement or spacing."
}
```

Required common fields:

- `id`: stable kebab-case string unique within file.
- `title`: tester-facing short title.
- `why`: tester-facing orientation.
- `what_to_do`: tester-facing action.
- `confirmation`: tester-facing observable completion condition.

Optional common fields:

- `anchors`: array of anchor objects.
- `note_prompt`: custom note placeholder.
- `evidence_hint`: short tester-facing hint for screenshots or evidence, if needed.
- `tags`: authoring or reporting tags, not shown as primary tester copy.

Visible word limits:

- `title`: recommended 3 to 8 words; hard invalid over 14 words.
- `why`: warning over 80 words; invalid over 120 words.
- `what_to_do`: warning over 80 words; invalid over 120 words.
- `confirmation`: warning over 80 words; invalid over 120 words.
- `note_prompt`: warning over 20 words; invalid over 40 words.

### 9.3 Step Mode XOR

Every step must satisfy exactly one mode.

Single expected mode:

```json
{
  "id": "window-shell-sanity",
  "title": "Check the window shell",
  "why": "The testing workflow depends on a stable app shell before deeper panes are judged.",
  "what_to_do": "Look at the main window after launch.",
  "confirmation": "The window is dark themed, correctly sized, and not showing a startup error.",
  "expected": "The main window is visible and stable."
}
```

Checklist mode:

```json
{
  "id": "screen-b-header-stage-rail",
  "title": "Check Screen B orientation",
  "why": "This screen carries the tester through triage, so its landmarks need to be obvious.",
  "what_to_do": "Review the header and stage rail before interacting with the triage panel.",
  "confirmation": "The header, current stage, and next available action are all visible.",
  "checklist": [
    {
      "id": "header-visible",
      "label": "Header names the current workflow",
      "confirmation": "The header is readable without opening another panel."
    },
    {
      "id": "stage-rail-visible",
      "label": "Stage rail shows the current stage",
      "confirmation": "The active stage is visually distinct from the others."
    }
  ]
}
```

Action mode:

```json
{
  "id": "open-triage-panel",
  "title": "Open the triage panel",
  "kind": "action",
  "why": "The next observations require the triage controls to be visible.",
  "what_to_do": "Open the triage panel from the visible testing workflow controls.",
  "confirmation": "The triage panel is open and ready for review."
}
```

Invalid combinations:

- `kind: "action"` plus `expected`
- `kind: "action"` plus `checklist`
- `expected` plus `checklist`
- no `kind`, no `expected`, and no `checklist`

### 9.4 Anchors

Anchor object:

```json
{
  "text": "Testing",
  "where": "top menu bar",
  "expect": "A visible menu label"
}
```

Required anchor fields:

- `text`: exact visible text, accessible label, or icon name.
- `where`: visible region.
- `expect`: what the tester should see or what the element does.

Anchor rules:

- If `text` is not exact visible text, the author must say why through `expect`.
- `where` must be spatial or structural, not implementation-oriented.
- Anchors must not include file paths, widget class names, object ids, or schema names.

### 9.5 Checklist Items

Checklist item fields:

- `id`: stable kebab-case id unique within the step.
- `label`: visible row text.
- `confirmation`: observable pass condition.
- `anchors`: optional item-specific anchors.
- `note_prompt`: optional item note placeholder.

Checklist rules:

- Each item should test one observation.
- Item labels warn over 16 words and are invalid over 28 words.
- Item confirmation is required.
- Item-level PASS/FAIL/SKIP is stored separately from the parent step outcome.

Checklist outcome derivation:

- If any required item is FAIL, parent step outcome is FAIL.
- If all required items are PASS, parent step outcome is PASS.
- If every item is SKIP, parent step outcome is SKIP.
- If PASS and SKIP are mixed with no FAIL, parent step outcome is PASS with skipped item metadata retained.
- Incomplete checklist steps cannot be marked complete unless the user explicitly skips unresolved items.

### 9.6 Notes

Notes are available on all step modes.

Instruction schema:

- `note_prompt`: optional tester-facing placeholder.
- No authored default note text.

Runtime state:

- Draft note is keyed by step id and survives navigation.
- Recorded note is committed with the result entry when an outcome is chosen.
- Editing a completed step updates the note and timestamp with the replacement result.

Result structure:

- `note: null` when absent.
- `note: "plain text"` when present.
- Summary label derives from note presence, such as `PASS + note`.

### 9.7 Results Mapping

Single expected result:

```json
{
  "step_n": 1,
  "test_id": "window-shell-sanity",
  "title": "Check the window shell",
  "outcome": "PASS",
  "note": null,
  "screenshot": null,
  "manual_screenshots": [],
  "claude_qa": [],
  "timestamp": "2026-04-25T19:20:00"
}
```

Action result:

```json
{
  "step_n": 2,
  "test_id": "open-triage-panel",
  "title": "Open the triage panel",
  "kind": "action",
  "outcome": "ACK",
  "note": null,
  "screenshot": null,
  "manual_screenshots": [],
  "claude_qa": [],
  "timestamp": "2026-04-25T19:21:00"
}
```

Checklist result:

```json
{
  "step_n": 3,
  "test_id": "screen-b-header-stage-rail",
  "title": "Check Screen B orientation",
  "kind": "checklist",
  "outcome": "PASS",
  "note": "Stage rail is readable but tight at narrow width.",
  "checklist_results": [
    {
      "id": "header-visible",
      "label": "Header names the current workflow",
      "outcome": "PASS",
      "note": null,
      "timestamp": "2026-04-25T19:22:00"
    }
  ],
  "screenshot": null,
  "manual_screenshots": [],
  "claude_qa": [],
  "timestamp": "2026-04-25T19:22:00"
}
```

The existing result schema can remain compatible if consumers already tolerate optional notes and unknown fields. If implementation adds new required fields, bump result schema separately from instruction `schema_version`.

## 10. Backward Compatibility

### 10.1 Legacy Read Behavior

The pane must continue reading v1 and v2 instruction files.

Legacy behavior:

- v1/v2 files load in legacy-compatible mode.
- Esc dispatcher and restart confirmation fixes remain active.
- v1/v2 files do not receive v3 content lint rejection.
- v1/v2 files may show developer diagnostics about legacy format.

### 10.2 No Runtime Auto-Migration

Opening a v1/v2 file must not rewrite it as v3.

Reasons:

- Migration can change meaning.
- Old files may be useful as historical artifacts.
- A runtime pane should not become an authoring transformer.

### 10.3 Optional Authoring Conversion

A separate authoring tool may generate a v3 draft from v1/v2 by:

- splitting `body` into `why`, `what_to_do`, and `confirmation`
- converting `expected` text into confirmation copy where appropriate
- preserving checklist rows
- flagging ambiguous UI anchors for manual repair
- running full v3 lint before publication

The conversion output must be reviewed before use.

### 10.4 Results Compatibility

Existing result consumers should continue treating `outcome` as the primary machine state and `note` as optional metadata.

The v3 UI may display:

- `PASS`
- `PASS + note`
- `FAIL`
- `FAIL + note`
- `SKIP`
- `DONE`

But persisted machine outcomes remain:

- `PASS`
- `FAIL`
- `SKIP`
- `ACK`

## 11. Visual Specs

### 11.1 Overall Pane

Recommended default size: 720 by 680.

Recommended minimum size: 520 by 560.

The pane must remain usable at the current minimum if implementation cannot immediately raise it, but v3 should be designed around more comfortable reading space.

Layout zones:

1. Header
2. Step content
3. Note field
4. Sticky action bar
5. Acknowledgement strip

The design should avoid nested cards. Use clear bands, spacing, and dividers instead of stacking framed boxes.

### 11.2 Header

Header contents:

- run title
- `Step N of M`
- compact progress indicator
- index drawer button
- restart control
- close control

Header rules:

- The current step title appears in the content area, not crowded into the window chrome.
- Restart remains visually secondary.
- The index drawer button must be reachable by keyboard.

### 11.3 Step Content

Content order:

1. Step title
2. `Why this matters`
3. `Do this`
4. Anchors, if present
5. `You can mark pass when` or `Ready for next step when`
6. Checklist rows, if applicable
7. Note

Text behavior:

- Avoid viewport-scaled font sizes.
- Do not use negative letter spacing.
- Long words and labels must wrap within their container.
- No outcome controls should move because a row label wraps.

### 11.4 Anchors

Anchor rows render as compact reference rows:

- exact text first
- location second
- expected appearance or behavior third

Example visual content:

`"Testing" | top menu bar | visible menu label`

Anchor rows are not interactive unless implementation later adds focus/highlight integration.

### 11.5 Notes

The note field is always visible.

Behavior:

- Default height: 2 lines.
- Expanded height: up to 4 lines.
- Manual resize is optional.
- Draft note persists when moving between steps.
- Completed step note can be edited by revisiting the step and updating the result.

Placeholder:

- Default: `Optional note for Claude`
- Custom: `note_prompt`

The note field must not be hidden behind a FAIL modal.

### 11.6 Action Bar

The action bar is sticky at the bottom of the pane content.

Single expected steps:

- PASS
- FAIL
- SKIP

Action steps:

- DONE

Checklist steps:

- Row-level PASS/FAIL/SKIP controls stay aligned with each checklist item.
- The bottom action bar shows checklist completion state and any required skip-unresolved affordance.

Rules:

- Terminal buttons record and advance for single expected and action steps.
- No separate Next row appears after PASS, FAIL, SKIP, or DONE.
- Buttons must have stable dimensions across label changes.
- Narrow layouts may wrap controls into two rows, but they must not scroll out of reach.

### 11.7 Acknowledgement Strip

The acknowledgement strip is compact and persistent.

It shows recent recorded actions, such as:

- `Recorded PASS for Step 2`
- `Saved note and marked FAIL for Step 3`
- `Marked DONE for setup step`

Placement:

- Immediately above or below the sticky action bar.
- Must not cover the note field.
- Must not require dismissal.

### 11.8 Index Drawer

The index drawer opens from the header.

It contains:

- ordered step list
- status marker
- note marker
- failure count for checklist steps
- jump action

Keyboard:

- Esc closes the drawer through the retained dispatcher.
- Arrow navigation is recommended.
- Enter jumps to selected step.

### 11.9 Paper Export

Paper export uses a table-like layout inspired by `AM_v0_smoke_checklist.html`, but with the v3 fields visible.

Suggested columns:

- #
- Step
- Why
- What to do
- Confirmation
- Outcome
- Notes

Checklist steps expand item rows beneath the parent step.

## 12. Implementation Sequencing Recommendation

1. Add schema and lint fixtures first

   Implement v3 parsing, required fields, XOR validation, word limits, forbidden visible terms, and anchor validation before UI work. Include positive and negative fixture files.

2. Add result-note compatibility

   Ensure single, checklist, and action result entries can persist optional notes without changing outcome enums. Keep `ACK` for action machine results and render it as DONE in the UI.

3. Build the v3 step renderer behind version gating

   If `schema_version == 3`, render the new field layout. If v1/v2, use legacy-compatible rendering with retained safety fixes.

4. Replace modal FAIL notes with inline notes

   Make note draft state durable across navigation. Commit note text on outcome recording.

5. Implement action bar advancement and acknowledgements

   PASS, FAIL, SKIP, and DONE should record and advance for single/action steps while leaving a persistent recent acknowledgement.

6. Implement checklist row stability

   Keep row controls visible and stable even when labels wrap. Ensure final checklist completion does not require a hidden or separated Next row.

7. Add index drawer

   Provide full-run visibility, jump behavior, and note/status markers.

8. Update paper export

   Export v3 fields and notes in a printable layout. Keep it opt-in.

9. Regression test retained behavior

   Verify Esc dispatcher priority, bare Esc no-op, restart confirmation, legacy file loading, schema XOR rejection, and `results_latest.json` writing.

## 13. Adjacent Concerns

These are worth tracking, but they should not block the v3 core unless Claude chooses to expand scope.

Accessibility:

- Provide keyboard access to all controls.
- Preserve visible focus.
- Do not rely on color alone for PASS/FAIL/SKIP/DONE.

Authoring tooling:

- A v3 authoring preview would help catch voice and anchoring problems before runtime.
- A lint report should point to field paths, not only step numbers.

Migration:

- A draft converter from v2 to v3 is useful, but it must mark uncertain splits for human or agent review.

Analytics:

- Time-per-step and note frequency could help future design, but should stay out of v3 unless already supported.

Screenshots:

- Existing manual screenshot preservation should continue.
- v3 should avoid coupling screenshot capture to PASS notes; notes and evidence are separate concepts.

Claude handoff:

- Claude can implement this in phases as long as schema/lint decisions land before visual-only changes.
- The minimum useful v3 is schema v3 plus inline notes plus acknowledged advance.
- The full v3 is schema v3 plus inline notes, action bar advancement, index drawer, stable checklist rows, legacy mode, and paper export.
