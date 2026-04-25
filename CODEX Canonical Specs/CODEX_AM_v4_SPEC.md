# CODEX AM v4 Spec - Internal Personal Tracker

Generated: 2026-04-25
Owner: Codex draft under Claude direction
Status: canonical v4 planning spec, not implementation code

## 0. Source Documents Read

This document is grounded in the following files:

- `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\20260425_091500_CLAUDE_to_CODEX_request_AM_v4_specs.md`
- `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\20260425_094500_CLAUDE_to_CODEX_AM_v4_triage_clarification.md`
- `C:\CODEX PG\CODEX Audit Module Interaction Spec\CODEX_AUDIT_MODULE_INTERACTION_SPEC_v1.md`
- `C:\CODEX PG\CODEX Audit Module UX Revision v3\CODEX_AUDIT_MODULE_UX_REVISION_v3.md`
- `C:\CODEX PG\CODEX Audit Module UX Revision v3\CODEX_AUDIT_MODULE_FEATURE_AND_NAVIGATION_SPEC_v3.md`
- `C:\CODEX PG\CODEX Audit Module UX Revision v3\CODEX Claude Handoff v3\CODEX_CHUNK_01_PRODUCT_MODEL_v3.md`
- `C:\CODEX PG\CODEX Audit Module UX Revision v3\CODEX Claude Handoff v3\CODEX_CHUNK_02_MINIMAL_UX_RULES_v3.md`
- `C:\CODEX PG\CODEX Audit Module UX Revision v3\CODEX Claude Handoff v3\CODEX_CHUNK_03_WORKFLOW_STATES_v3.md`
- `C:\CODEX PG\CODEX Audit Module UX Revision v3\CODEX Claude Handoff v3\CODEX_CHUNK_04_IMPLEMENTATION_BOUNDARIES_v3.md`
- `C:\CODEX PG\CODEX Canonical Specs\CODEX_AUDIT_ISSUE_SCHEMA_v1.md`
- `C:\CODEX PG\CODEX Canonical Specs\CODEX_SESSION_PACKAGE_SCHEMA_v1.md`
- `C:\panda-gallery\BUGS.md`
- `C:\panda-gallery\workflows\results_latest.json`

## 1. v4 Product Model

### 1.1 Plain-English Model

AM v4 is Darrin's internal Panda Gallery bug-and-feature tracker.

It is not a product feature for clinical users.

It is not a multi-user testing operation.

It is not a background AI inbox.

It is a local, single-user workbench that helps Darrin turn PG bugs, feature requests, testing evidence, and notes into clear decisions, Claude Code prompts, verification records, and a searchable development memory.

The center of the product is a bug detail view with an on-demand AI triage assistant.

Darrin opens a bug, clicks `Triage with AI`, reviews the answer, and chooses the next action.

AM helps answer:

1. Is this bug description clear enough to fix?
2. Is this really a bug, or is it a feature request?
3. Is this serious work, or just a small amendment?
4. What information is missing before a Claude Code session should start?
5. What exact prompt should Claude Code receive?
6. What status should the reporter or tester receive?
7. What evidence proves the fix?
8. How should this be archived for future search?
9. Which design gaps need a Darrin decision before code work starts?

### 1.2 Comparison To v3

The v3 product model in `C:\CODEX PG\CODEX Audit Module UX Revision v3\CODEX_AUDIT_MODULE_UX_REVISION_v3.md` says the Audit Module is an "intelligent inbox for Panda Gallery testing feedback."

That model is now demoted.

The inbox metaphor still applies to secondary intake sources, such as local package folders or optional Dropbox drops.

It does not describe the day-one value.

The day-one value is personal bug triage.

In v3, AI analyzed arriving packages automatically.

In v4, AI is called only when Darrin asks for help on a specific bug.

In v3, approvals protected sender communication and code handoff.

In v4, approvals become lightweight personal checkpoints.

In v3, the response stage drafted email for an external sender.

In v4, the response stage becomes a disposition note and tester-notification draft.

In v3, Dropbox was the front door.

In v4, `C:\panda-gallery\BUGS.md` is the front door.

### 1.3 What Drops From v3

- Multi-user reviewer model.
- Reviewer RBAC.
- Shared team inbox requirement.
- External sender as the default case.
- Autonomous package analysis worker.
- Background AI extraction as the primary workflow.
- Human-review-of-AI ceremony as a separate gate.
- PHI/compliance workflow beyond a one-line local-only statement.
- Dropbox as required intake.
- Email sending as a required MVP capability.

### 1.4 What Stays From v3

The following v3 decisions stay:

- Six left-rail workflow stages: Intake, Review, Response/Note, Code, Verify, Archive.
- Minimal visible surface with collapsible advanced panels.
- One primary action per screen.
- Urgency spectrum: P0, P1, P2, P3, verified.
- PG-aligned dark palette and peach active accent.
- Package to evidence to issue to archive lineage.
- Claude Code task builder.
- Searchable archive.

### 1.5 What Is New In v4

- BUGS.md-first navigation.
- Per-bug on-demand AI triage.
- `triage_state` as a first-class issue field.
- Readiness/design-gap tracking with inline Darrin decisions.
- Severity sanity check distinguishing serious bugs from amendments.
- Feature-request redirect path.
- Lazy destination setup for feature requests and amendments.
- Tester-notification model even in solo mode.
- Prompt-generation as the primary productivity payoff.
- Sidecar persistence for AM-only metadata when writing back to BUGS.md is too invasive.

### 1.6 Product Boundaries

AM v4 lives inside the PG development environment.

It may become a PySide6 dev-mode window in `C:\panda-gallery`.

It must not become a fifth PG v4.0 clinical module.

PG v4.0 clinical navigation remains locked to:

- Library
- Arrange
- Review
- Present

AM is internal-only tooling under a Testing or developer surface.

## 2. Workflow Stages v4

### 2.1 Stage Overview

The v4 left rail keeps the six v3 workflow stages, but each stage is reframed for single-user work:

1. Intake
2. Review
3. Note
4. Code
5. Verify
6. Archive

`Response` becomes `Note` in the visible v4 vocabulary.

The broader stage can still generate tester notifications.

### 2.2 Intake

Purpose: collect work items.

Primary source:

- `C:\panda-gallery\BUGS.md`

Secondary sources:

- `C:\panda-gallery\workflows\results_latest.json`
- `C:\panda-gallery\workflows\screenshots\...`
- `C:\panda-gallery\workflows\transcripts\...`
- External session packages under a local watched folder
- Optional Dropbox-completed packages
- Manual Darrin entry

Intake does not run AI automatically.

It parses, normalizes, and lists work items.

### 2.3 Review

Purpose: inspect one bug and run on-demand triage.

Primary action:

- `Triage with AI`

The AI triage output can say:

- Description is clear, ready for fix prompt.
- Description is vague, missing X/Y/Z.
- This is a feature request.
- This is a small amendment.

The readiness output can also flag typed gaps:

- `[Design]` missing UI decision, vocabulary decision, mockup choice, or interaction rule.
- `[Evidence]` missing screenshot, result, transcript, or reproduce proof.
- `[Scope]` missing v4.0/v4.1 placement, module ownership, or implementation boundary.
- `[Test]` missing verification plan.

Review is not a queue of AI-generated findings.

The bug list is the inbox.

The detail view is where triage happens.

### 2.4 Note

Purpose: record Darrin's disposition and prepare any reporter/tester notification.

This replaces v3's `Sender Response Draft` stage.

Examples:

- "Need more detail from tester: exact screen size and capture state."
- "Accepted as bug, fix prompt generated."
- "Small amendment, handle with quick CSS/layout tweak."
- "Feature request, move to backlog."

The notification can be a copy-paste draft in MVP.

No live email send is required in v4 first slice.

### 2.5 Code

Purpose: generate and manage Claude Code work.

Primary action:

- `Build Fix Prompt`

The prompt should walk Claude Code through:

1. Read relevant files.
2. Reproduce or reason from evidence.
3. Implement the minimal fix.
4. Run validation.
5. Report changed files, assumptions, and residual risks.

This is the productivity payoff of AM v4.

### 2.6 Verify

Purpose: confirm the fix against the original bug.

Inputs:

- Claude Code final report.
- Git commit or diff.
- Test command output.
- New guided testing result.
- Manual Darrin verification note.

Verification can result in:

- Verified fixed.
- Needs retest.
- Reopened.
- Split into follow-up bug.

### 2.7 Archive

Purpose: make resolved work searchable.

Archive records should preserve:

- Original bug text.
- Triage output.
- Darrin's final decision.
- Fix prompt.
- Verification evidence.
- Closing note.
- Related commit or version.

## 3. Screen Set v4

### 3.1 v3 Screen Mapping

The v3 screen set in `C:\CODEX PG\CODEX Audit Module UX Revision v3\CODEX_AUDIT_MODULE_UX_REVISION_v3.md` lists:

1. Dropbox Intake
2. Analysis Review
3. Finding Detail
4. Sender Response Draft
5. Claude Code Task Builder
6. Verification
7. UX Principle Map

v4 changes the center of gravity.

### 3.2 Screen Disposition Table

| v3 Screen | v4 Disposition | Reason |
| --- | --- | --- |
| `01_dropbox_intake.png` | Modify / demote | Dropbox is optional secondary intake. BUGS.md is primary. |
| `02_analysis_review.png` | Demote | No autonomous findings queue. Use list filters and per-bug triage states instead. |
| `03_finding_detail.png` | Promote | Becomes dominant Bug Detail + Triage Assistant screen. |
| `04_sender_response_draft.png` | Modify | Becomes Note / Tester Notification Draft. |
| `05_claude_code_task_builder.png` | Keep | Still core productivity payoff. |
| `06_verification_archive.png` | Keep / simplify | Single-user verification and archive. |
| `07_minimal_powerful_ux_map.png` | Keep as principle | Not a product screen. Use for design constraints. |

### 3.3 Screen A - AM Home / BUGS.md Intake

Purpose: show current PG bug tracker as a navigable work list.

Primary action:

- Open selected bug.

Secondary actions:

- Refresh BUGS.md.
- New manual entry.
- Import session package.

Collapsed:

- Parse diagnostics.
- Raw Markdown block.
- Source file positions.

Sketch:

```text
+---------------------------------------------------------------------+
| Audit Module - Internal                                             |
+------------------+------------------------------+-------------------+
| Intake           | BUGS.md                       | Filters           |
| Review           | #134 Stage 2 paths       P2   | P0 [ ] P1 [ ]     |
| Note             | #132 Region dialog size  P2   | unclear [ ]       |
| Code             | #131 Focus indicator     P3   | amend [ ]         |
| Verify           | #129 Settings too large  P2   | ready [ ]         |
| Archive          | #116 Back/Forward nav    P2   | feature [ ]       |
+------------------+------------------------------+-------------------+
| Source: C:\panda-gallery\BUGS.md     Last parsed: timestamp         |
+---------------------------------------------------------------------+
```

### 3.4 Screen B - Bug Detail With Triage Assistant

Purpose: inspect one bug and call AI on demand.

Primary action:

- `Triage with AI`

Secondary actions:

- Edit bug text.
- Build fix prompt.
- Draft notification.

Collapsed:

- Raw Markdown.
- Source line offsets.
- AI prompt/response JSON.
- Related package/evidence records.

Sketch:

```text
+---------------------------------------------------------------------+
| #132 Region-capture review dialog: preview too large                |
+------------------+------------------------------+-------------------+
| Intake           | Bug Detail                   | Triage Assistant  |
| Review *         | Status: Open                 | [Triage with AI]  |
| Note             | Severity: Medium             | State: untriaged  |
| Code             | Files: region_capture.py     |                   |
| Verify           | Reproduce                    | AI Result         |
| Archive          | Expected                     | - missing fields  |
|                  | Actual                       | - severity check  |
|                  | Fix direction                | - classification  |
+------------------+------------------------------+-------------------+
| Evidence: screenshots, workflow refs, transcript refs if present    |
+---------------------------------------------------------------------+
```

If the triage panel flags a `[Design]` gap, the row must include:

- `Decide`
- `Mark resolved`

`Decide` opens an inline one-line text input. Saving appends a dated decision to the bug's Notes section in `BUGS.md`:

```markdown
**Decision (YYYY-MM-DD):** [text]
```

After save, AM removes that gap from triage state.

`Mark resolved` removes the gap from triage state without modifying `BUGS.md`. Use it for stale gaps, such as when a mockup or decision already exists but AI did not notice it.

### 3.5 Screen C - Note / Tester Notification

Purpose: write Darrin's disposition and draft reporter updates.

Primary action:

- Save note.

Secondary actions:

- Draft tester update.
- Copy message.
- Mark clarification requested.

Sketch:

```text
+---------------------------------------------------------------------+
| Note / Notification                                                 |
+------------------+------------------------------+-------------------+
| Note             | Disposition                  | Notification      |
|                  | [Accepted as real bug...]    | To: tester/self   |
|                  |                              | Draft message     |
|                  | Decision: ready_for_prompt   | [Copy] [Save]     |
+---------------------------------------------------------------------+
```

### 3.6 Screen D - Claude Code Task Builder

Purpose: convert a triaged bug into a Claude Code prompt.

Primary action:

- Export prompt.

Secondary actions:

- Copy prompt.
- Add verification steps.
- Attach evidence.

Prompt sections:

- Goal.
- Files to inspect.
- Boundaries.
- Reproduce.
- Expected behavior.
- Implementation constraints.
- Validation commands.
- Report-back format.

### 3.7 Screen E - Verification

Purpose: close the loop after Claude Code work.

Primary action:

- Verify fixed.

Secondary actions:

- Reopen.
- Needs retest.
- Add verification evidence.

### 3.8 Screen F - Archive Search

Purpose: search closed bugs, generated prompts, decisions, and verification notes.

Primary action:

- Open archive result.

Secondary actions:

- Copy prior prompt.
- Reopen as new issue.
- Export summary.

### 3.9 Screen G - External Package Intake

Purpose: secondary intake from local packages or optional Dropbox.

Primary action:

- Import package findings.

This screen is not day-one primary.

It exists because v1/v3 package lineage remains useful for guided testing sessions.

## 4. State Machine v4

### 4.1 v3 State Chain Replaced

The v3 state chain in `C:\CODEX PG\CODEX Audit Module UX Revision v3\CODEX Claude Handoff v3\CODEX_CHUNK_03_WORKFLOW_STATES_v3.md` was:

```text
dropbox_waiting -> package_detected -> completeness_check -> analysis_running -> findings_ready -> finding_review -> response_draft -> response_approved -> code_task_ready -> fix_waiting -> verification_review -> archived
```

v4 replaces the autonomous package chain with per-bug state.

### 4.2 Issue Status

The v1 issue schema already has a broad status lifecycle in `C:\CODEX PG\CODEX Canonical Specs\CODEX_AUDIT_ISSUE_SCHEMA_v1.md`.

AM v4 should simplify the visible status set:

| Status | Meaning |
| --- | --- |
| `open` | Work item exists and is not closed. |
| `in_review` | Darrin is actively inspecting or triaging. |
| `in_fix` | Claude Code or Darrin is fixing it. |
| `awaiting_verification` | Fix exists but needs confirmation. |
| `closed` | Closed and ready for archive/search. |
| `archived` | Archived immutable/search record exists. |

### 4.3 Triage State

Add `triage_state` as first-class v4 issue metadata.

Allowed values:

| Triage State | Meaning |
| --- | --- |
| `untriaged` | No AI triage has been run for this bug. |
| `triage_running` | On-demand AI call is currently in progress. |
| `clarification_requested` | AI or Darrin found missing information. |
| `design_decision_needed` | A `[Design]` readiness gap needs Darrin's inline decision. |
| `ready_for_fix_prompt` | Description is clear enough for Claude Code. |
| `feature_request_redirect` | Item is better tracked as feature/backlog. |
| `amend_only` | Small amendment or one-line correction. |
| `in_fix` | A fix prompt was exported or fix work began. |
| `awaiting_verification` | Fix reported complete, not yet verified. |
| `closed` | Darrin closed the item. |

### 4.4 Triage Transitions

```text
untriaged -> triage_running
triage_running -> ready_for_fix_prompt
triage_running -> clarification_requested
triage_running -> design_decision_needed
triage_running -> feature_request_redirect
triage_running -> amend_only
design_decision_needed -> ready_for_fix_prompt
design_decision_needed -> clarification_requested
ready_for_fix_prompt -> in_fix
amend_only -> in_fix
feature_request_redirect -> closed
clarification_requested -> untriaged
in_fix -> awaiting_verification
awaiting_verification -> closed
awaiting_verification -> untriaged
closed -> archived
```

### 4.5 No Background AI State

There is no autonomous `analysis_running` queue state in v4.

`triage_running` exists only after Darrin presses `Triage with AI` on a bug.

AM must not silently triage every new bug in the background.

### 4.6 Package Intake State

External packages can keep package states from `C:\CODEX PG\CODEX Canonical Specs\CODEX_SESSION_PACKAGE_SCHEMA_v1.md`.

Those states are secondary.

They should not drive the main AM work list.

## 5. Schema Deltas

### 5.1 Reuse Strategy

Reuse `pg.audit_*` concepts where possible.

Do not invent a completely separate tracker schema.

The v4 reframe is large enough to justify documenting `pg.audit_issue.v2` as an issue-record shape.

This is not a demand to migrate the Stage 1 package schema.

`pg.session_package.v1` remains valid for testing-session packages.

### 5.2 Fields That Stay From v1

From `C:\CODEX PG\CODEX Canonical Specs\CODEX_AUDIT_ISSUE_SCHEMA_v1.md`, keep:

- `issue_id`
- `title`
- `summary`
- `category`
- `priority`
- `status`
- `source_steps`
- `source_test_ids`
- `evidence_ids`
- `transcript_refs`
- `observed_behavior`
- `expected_behavior`
- `impact`
- `lineage`
- `audit.events[]`

### 5.3 Fields That Simplify

Simplify:

- `reviewer` collapses to Darrin fields or disappears into events.
- `approved_by` becomes a local checkpoint, not external approval.
- `suggested_response` becomes `notification_draft`.
- `email_*` records become optional notification drafts.
- `created_by.provider/model` stays only inside AI triage records.

### 5.4 Fields That Drop For MVP

Drop from day-one MVP:

- Multi-reviewer assignment.
- Shared inbox address.
- CC list.
- Provider message ID.
- Email queue state.
- RBAC fields.
- PHI/compliance review fields beyond local-only note.

### 5.5 New v2 Fields

Add:

- `source_kind`
- `source_ref`
- `bug_number`
- `triage_state`
- `triage_runs[]`
- `readiness_gaps[]`
- `destination_moves[]`
- `disposition_note`
- `notification_drafts[]`
- `fix_prompt`
- `fix_state`
- `verification`
- `archive`

### 5.6 Proposed `pg.audit_issue.v2`

```json
{
  "schema": "pg.audit_issue.v2",
  "schema_version": 2,
  "issue_id": "bug_0132",
  "source_kind": "bugs_md",
  "source_ref": {
    "path": "C:\\panda-gallery\\BUGS.md",
    "heading": "### #132 - Region-capture review dialog: preview too large and positioned over the pane",
    "line_start": 31,
    "line_end": 57
  },
  "bug_number": 132,
  "title": "Region-capture review dialog: preview too large and positioned over the pane",
  "summary": "Dialog preview is too large and overlaps the instruction pane.",
  "category": "ui_ux",
  "priority": "P2",
  "status": "open",
  "triage_state": "untriaged",
  "observed_behavior": "Current BUGS.md Actual section.",
  "expected_behavior": "Current BUGS.md Expected section.",
  "reproduce_steps": ["Open pane", "Capture region", "Click toast"],
  "files": ["region_capture.py"],
  "evidence_ids": [],
  "source_steps": [],
  "source_test_ids": [],
  "triage_runs": [],
  "readiness_gaps": [],
  "destination_moves": [],
  "disposition_note": null,
  "notification_drafts": [],
  "fix_prompt": null,
  "verification": null,
  "archive": null,
  "audit": {
    "created_at": "2026-04-25T09:15:00-07:00",
    "updated_at": "2026-04-25T09:15:00-07:00",
    "events": []
  }
}
```

### 5.7 Readiness Gap Object

```json
{
  "gap_id": "gap_20260425_103000_0001",
  "kind": "design",
  "label": "Need Darrin decision on dialog anchor behavior",
  "state": "open",
  "source": "triage_run_id",
  "resolution": null,
  "resolved_at": null,
  "bugs_md_decision_appended": false
}
```

Allowed `kind` values:

- `design`
- `evidence`
- `scope`
- `test`
- `description`

For `kind: design`, AM must offer `Decide` and `Mark resolved` actions in the readiness panel.

`Decide` appends a dated decision line to BUGS.md Notes and sets:

```json
{
  "state": "resolved",
  "resolution": "Decision text",
  "bugs_md_decision_appended": true
}
```

`Mark resolved` sets:

```json
{
  "state": "resolved",
  "resolution": "Marked resolved without BUGS.md edit",
  "bugs_md_decision_appended": false
}
```

### 5.8 Triage Run Object

```json
{
  "triage_run_id": "triage_20260425_091500_0001",
  "created_at": "2026-04-25T09:15:00-07:00",
  "created_by": {
    "type": "ai_model",
    "provider": "claude",
    "model": "configured_by_runtime"
  },
  "input_ref": {
    "issue_id": "bug_0132",
    "source_hash": "sha256 of normalized bug markdown"
  },
  "classification": "ready_for_fix_prompt",
  "readiness_gaps": [],
  "severity_sanity": {
    "declared_priority": "P2",
    "suggested_priority": "P2",
    "gap": "none",
    "reason": "Impacts every capture review but has workaround."
  },
  "missing_information": [],
  "recommended_next_action": "build_fix_prompt",
  "summary": "Description is clear enough to draft a fix prompt.",
  "confidence": 0.86
}
```

### 5.9 Notification Draft Object

```json
{
  "notification_id": "note_20260425_091500_0001",
  "issue_id": "bug_0132",
  "recipient_kind": "tester_or_self",
  "recipient_label": "Darrin",
  "state": "draft",
  "subject": "Update on #132 region capture review dialog",
  "body_markdown": "I accepted this as a UI bug and generated a fix prompt.",
  "created_at": "2026-04-25T09:15:00-07:00",
  "approved_by_darrin": false,
  "sent_or_copied_at": null
}
```

### 5.10 Destination Preference Object

Do not hard-code feature or amendment destinations.

When Darrin first clicks `Move to feature request` or `Move to amendment`, AM asks where that category should go and saves the answer.

```json
{
  "category": "feature_request",
  "destination_kind": "existing_file",
  "destination_path": "C:\\panda-gallery\\v4.1_BACKLOG.md",
  "section": null,
  "created_at": "2026-04-25T10:30:00-07:00",
  "created_by": "Darrin"
}
```

Suggested first-time defaults:

- Feature requests: existing file `C:\panda-gallery\v4.1_BACKLOG.md`.
- Amendments: tagged section in `BUGS.md`, such as `## OPEN -- Amendments`.

The setup prompt options:

```text
Where should [category] go?
  ( ) New file: [proposed name]
  ( ) Existing file: [intelligent suggestion if any]
  ( ) Tagged section in BUGS.md: ## [SECTION NAME]
  ( ) Other: [path input]
  [Save my choice]
```

Future moves to the same category use the saved destination silently.

### 5.11 Persistence Recommendation

MVP should use a sidecar JSON file rather than rewriting `BUGS.md` for every state change.

Recommended:

```text
C:\panda-gallery\workflows\audit_module\
  audit_issue_state.json
  audit_triage_runs.jsonl
  destinations.json
  audit_prompt_exports\
  audit_archive.jsonl
```

This path is a future implementation recommendation only.

This spec does not create or edit files in `C:\panda-gallery`.

## 6. Integration With PG Repo

### 6.1 Location

Future implementation likely belongs under `C:\panda-gallery\audit_module\` or `C:\panda-gallery\dev_tools\audit_module\`.

Claude should choose final repo placement before Claude Code implementation.

### 6.2 Entry Point

AM should be opened as internal tooling.

Acceptable entry points:

- Testing menu item: `View -> Testing -> Audit Module`
- Dev-only hotkey.
- `--dev` gated window.
- Separate internal launcher command.

AM must not appear as a top-level v4.0 module beside Library, Arrange, Review, Present.

### 6.3 Runtime Access

AM can read:

- `BUGS.md`
- `workflows/results_latest.json`
- workflow screenshot folders
- transcript files
- package manifests
- PG version files
- git metadata if available

AM should not mutate PG runtime state except through approved sidecar state files and explicit Darrin actions.

### 6.4 Coupling Boundary

AM should be loosely coupled.

Recommended components:

- `bugs_parser.py`
- `issue_store.py`
- `triage_service.py`
- `prompt_builder.py`
- `notification_drafts.py`
- `archive_store.py`
- `audit_module_window.py`

No component should import clinical Review/Arrange UI code.

AM may reuse PG theme constants if available.

### 6.5 AI Boundary

AI calls are user-initiated.

The UI must show when a triage call is running.

The AI response must be saved as a triage run, not silently merged into the bug.

Darrin chooses whether to accept, edit, discard, or rerun.

## 7. Data Sources

### 7.1 Primary: BUGS.md

`C:\panda-gallery\BUGS.md` is the primary data source.

It contains numbered open bugs and fixed history.

The file itself says to include Reproduce, Expected, and Actual when logging bugs.

AM should parse:

- bug number
- title
- status
- severity
- files
- reproduce steps
- expected
- actual
- fix direction
- notes
- related bugs

### 7.2 Existing Workflow Results

`C:\panda-gallery\workflows\results_latest.json` provides guided-test results.

Observed fields include:

- `schema_version`
- `run_id`
- `title`
- `started_at`
- `instructions_source`
- `results[]`
- `results[].step_n`
- `results[].test_id`
- `results[].kind`
- `results[].outcome`
- `results[].checklist_results`
- `results[].screenshot`
- `results[].manual_screenshots`

AM can use this to attach evidence to bugs.

It should not require workflow results for BUGS.md-first MVP.

### 7.3 Screenshots And Region Captures

Workflow screenshots can become evidence refs.

AM should preserve original files.

Any copied evidence should retain source path, hash, and timestamp.

### 7.4 Transcripts

Transcripts are optional context.

AM should link transcript refs where available.

It should not block triage when transcript is missing.

### 7.5 Manual Entry

Darrin can create a new bug or feature request manually.

Manual entries should follow the same structured fields as parsed BUGS.md entries.

### 7.6 External Packages

External session packages remain supported.

They use `pg.session_package.v1` from `C:\CODEX PG\CODEX Canonical Specs\CODEX_SESSION_PACKAGE_SCHEMA_v1.md`.

They are secondary intake, not the primary AM surface.

### 7.7 Optional Dropbox

Dropbox can be useful if Darrin wants to drop packages from another machine.

It is not required for v4 MVP.

## 8. First Implementation Slice

### 8.1 Goal

Build the smallest useful AM for Darrin:

- Read `BUGS.md`.
- Render open bugs as a list.
- Click a bug.
- Show detail.
- Run on-demand AI triage or deterministic mock triage.
- Persist triage state.
- Generate a Claude Code prompt.

### 8.2 Slice Scope

Implementation slice:

1. Parser for `BUGS.md` open section.
2. Sidecar issue state JSON.
3. PySide6 window with left rail and two panes.
4. Bug list with filters by severity and triage state.
5. Detail view with raw parsed sections.
6. `Triage with AI` button.
7. Mock triage provider if real endpoint is not wired.
8. Triage result panel.
9. Readiness gap panel with `Decide` and `Mark resolved` for `[Design]` gaps.
10. `Build Fix Prompt` button.
11. Prompt preview and copy/export.

### 8.3 Slice Non-Scope

Not in first slice:

- Real Dropbox watcher.
- Email sending.
- Full archive UI.
- Multi-user accounts.
- PHI handling.
- Clinical-user packaging.
- Direct code execution.
- Automatic bug triage on startup.

### 8.4 First Slice State Persistence

Use sidecar JSON to avoid rewriting `BUGS.md` during early development.

`BUGS.md` remains source text.

Sidecar stores:

- issue id
- bug number
- triage state
- triage runs
- readiness gaps
- destination preferences
- disposition note
- generated prompt path
- verification state

### 8.5 First Slice AI Behavior

AI is on-demand only.

If no real AI endpoint is available:

- Use deterministic mock responses.
- Label them clearly as mock.
- Keep interface shape identical to the future real provider.

### 8.6 First Slice Prompt Output

Prompt output should include:

- bug title
- source path
- parsed reproduce/expected/actual
- files listed in BUGS.md
- AI triage summary
- implementation boundary
- verification checklist
- report-back format

## 9. Tester Notification Model

### 9.1 Purpose

Tester notification keeps the reporter informed.

In solo mode, the reporter may be Darrin.

Later, the reporter may be a remote tester whose package or note created the bug.

### 9.2 MVP Shape

MVP does not send email automatically.

It drafts a message Darrin can copy.

### 9.3 Notification Events

Notification-worthy moments:

- clarification requested
- accepted for fix
- fix prompt generated
- fix in progress
- fix shipped
- needs retest
- verified fixed
- closed as feature request
- closed as duplicate

### 9.4 Notification Data

Each notification draft should include:

- `notification_id`
- `issue_id`
- `recipient_kind`
- `recipient_label`
- `trigger_event`
- `subject`
- `body_markdown`
- `created_at`
- `approved_by_darrin`
- `delivery_state`

### 9.5 User Control

Darrin must approve or copy the notification.

AM should not send without explicit action.

## 10. UX Principles

### 10.1 Minimal Surface

Follow the v3 minimal UX rule from `C:\CODEX PG\CODEX Audit Module UX Revision v3\CODEX Claude Handoff v3\CODEX_CHUNK_02_MINIMAL_UX_RULES_v3.md`.

Show only the main decision.

Collapse raw data.

### 10.2 One Primary Action

Each screen should have one dominant action:

- Intake: open bug.
- Review: triage with AI.
- Note: save note.
- Code: export prompt.
- Verify: verify fixed.
- Archive: open archive result.

### 10.3 Visual Vocabulary

Use PG dark shell vocabulary.

Use peach accent for active control.

Use muted borders and compact panes.

Use urgency colors only for status or priority.

### 10.4 Evidence Discipline

AM must never alter original evidence.

Original source files stay unchanged.

Derived evidence is copied or referenced with hashes.

## 11. NOT In Scope For v4

- Productizing AM for clinical users.
- Making AM visible in the clinical module bar.
- Multi-user RBAC.
- Real PHI handling.
- Shared email send.
- Public-facing sender portal.
- Autonomous background AI triage.
- Automatic code execution.
- DICOM workflow.
- Installer/distribution UX.
- Cloud database.

## 12. Open Questions For Darrin

1. Should AM v4 write accepted triage state back into `BUGS.md`, or should sidecar JSON remain the source of AM state?
2. Should `Response` visibly rename to `Note`, or should the left rail keep `Response` for continuity with v3?
3. Should the first move of a feature request prefer `v4.1_BACKLOG.md`, or should AM merely suggest it and wait for Darrin to choose?
4. Should the first real AI provider be Claude through an existing local mechanism, or should v0 ship with mock triage only?
5. Should notifications target email copy-paste, mailbox files, or a generic clipboard draft first?
6. Should AM parse the fixed-bugs history in MVP, or only the OPEN section?
7. Should a Claude Code prompt export be a `.md` file under workflows, copied text, or both?
8. Should AM have a hard `--dev` gate from day one?

## 13. Implementation Notes For Future Claude Code Prompt

This section is not an implementation authorization.

When Claude later writes the implementation prompt, it should specify:

- Read-only parse of `BUGS.md`.
- Sidecar JSON state.
- No edits outside approved AM files.
- No clinical UI changes.
- No autonomous AI calls.
- Mock triage provider allowed if real provider is not ready.
- Inline `[Design]` gap decisions append `**Decision (YYYY-MM-DD):** ...` to BUGS.md Notes only after Darrin saves.
- Feature/amendment destinations are configured on first move and stored in `destinations.json`.
- Unit tests for BUGS.md parser.
- Unit tests for state transitions.
- Unit tests for readiness gap resolution.
- Unit tests for destination preference selection.
- Golden prompt-output fixture.
- Manual smoke test with bug #132 or #134.
