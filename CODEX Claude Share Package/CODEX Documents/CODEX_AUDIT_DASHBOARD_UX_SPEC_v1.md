# CODEX Audit Dashboard UX Spec v1

Generated: 2026-04-24

Status: Codex canonical draft for PG Testing + Audit MVP v1.

Scope: defines the first audit dashboard user experience for reviewing packaged tester sessions, AI-extracted issues, evidence, approval decisions, draft team emails, and searchable archive records. This dashboard belongs to the Testing + Audit workflow. It should align with Claude's Panda Gallery v4 redesign language without becoming a clinical v4 module.

Depends on:

- `CODEX_MASTER_SPEC_INDEX.md`
- `CODEX_SESSION_PACKAGE_SCHEMA_v1.md`
- `CODEX_AUDIT_ISSUE_SCHEMA_v1.md`
- `CODEX_TESTING_AUDIT_ARCHITECTURE_v1.md`
- `CODEX_CLAUDE_SCREENSHOT_UX_MOCKUP_REVIEW.md`

## Product Position

The audit dashboard is an evidence review and approval workspace for PG testing output.

It is not:

- a replacement for the clinical Panda Gallery v4 Library, Mount, Review, Compare, or Present modules,
- a generic issue tracker,
- a Dropbox file browser,
- an AI chat surface,
- a place to edit clinical images,
- a live email client in the first local prototype.

It is:

- a queue for packaged tester sessions,
- a reviewer surface for AI-suggested findings,
- an evidence browser tied to package evidence IDs,
- an approval workflow for issue text and response drafts,
- a local archive/search surface for closed audit records.

## Design Alignment

The dashboard should match the redesign direction Claude already developed and Codex reviewed:

- dark desktop shell,
- compact panes,
- low-radius controls,
- dense but readable rows,
- muted borders and separators,
- peach active accent `#e8a87c`,
- green success/approved state,
- red failure/high-risk state,
- amber warning/deferred state,
- stable top context and bottom action bars,
- evidence previews attached to decisions,
- right-panel detail model inspired by v4 without copying generic photo-editing controls.

Borrow from the v4 redesign:

- stable shell regions,
- right-side detail panel,
- bottom filmstrip/evidence strip where useful,
- clear module-like navigation,
- restrained dark UI optimized for visual inspection.

Do not borrow:

- generic Adobe photo vocabulary,
- clinical image adjustment tools,
- clinical PASS/FAIL language outside the testing context,
- decorative splash/brand moments,
- complex panels before evidence and approval state are reliable.

## Primary Users

| User | Goal | Dashboard Support |
| --- | --- | --- |
| PG reviewer | Approve, reject, revise, or defer extracted issues. | Issue Review view with evidence, transcript refs, and editable approval fields. |
| QA/test lead | See which packages are ready, blocked, or archived. | Package Inbox with status filters and package health. |
| Developer/Claude | Understand evidence-linked bugs without guessing. | Approved issue summaries, evidence IDs, package links, and archive records. |
| Darrin/admin | Maintain audit integrity and avoid rushed decisions. | Explicit validation, warnings, and pushback states. |

## Global Shell

Recommended first desktop shell:

```text
Top bar
  Product label: PG Audit
  Package/session context
  Search field
  Status filters

Left pane
  Package list or issue queue

Center pane
  Evidence preview and selected step/issue context

Right pane
  Issue detail, reviewer edits, approval/email/archive state

Bottom bar
  Primary workflow actions for the active view
```

Rules:

- Patient or PHI-like data must not be visually emphasized until compliance is settled.
- Package ID, session ID, run ID, state, validation status, and issue counts must be visible.
- The selected issue and selected evidence must stay visually linked.
- Bottom actions must remain available without scrolling.
- Rows and panes should be compact enough for repeated work, but not so dense that evidence context disappears.

## Navigation Model

Use four primary views:

| View | Purpose | MVP Priority |
| --- | --- | --- |
| Package Inbox | Review package state, validation, and extraction readiness. | First |
| Issue Review | Inspect and approve AI-extracted findings. | First |
| Email Draft | Review approved shared-team response before queue/send. | Second |
| Archive Search | Search closed audit records. | Second |

Optional later views:

- Transfer Queue
- Processing Monitor
- Settings/Provider Config
- Compliance Review

Avoid making Testing + Audit a peer clinical module unless the product explicitly becomes a separate PG workspace. In the clinical v4 shell, this would belong under developer/admin/audit surfaces, not next to Library, Mount, Review, Compare, Present for everyday dental users.

## View 1: Package Inbox

Purpose: let the reviewer see which sessions exist, whether packages are valid, and what needs attention.

Layout:

```text
Left/center list: packages
Right panel: selected package summary
Bottom bar: Validate, Open Issues, Queue Upload, Archive, Reveal Package
```

Package row fields:

- package state,
- validation state,
- session title,
- session ID,
- created time,
- issue count,
- evidence count,
- warning count,
- upload/processing state when available.

Status chips:

| State | Color Intent |
| --- | --- |
| `local_ready` | green |
| `triage_ready` | peach accent |
| `processing_failed` | red |
| `queued_for_upload` | blue/neutral, subdued |
| `archived` | muted grey |
| warnings present | amber |

Package detail panel:

- package identity,
- source summary,
- validation summary,
- missing sources,
- evidence summary,
- transcript availability,
- AI extraction availability,
- privacy status summary.

Acceptance criteria:

- Reviewer can identify packages that are ready, blocked, or archived without opening files manually.
- Validation warnings are visible before upload/AI/review actions.
- Upload actions are disabled until package state and validation allow them.

## View 2: Issue Review

Purpose: review AI-extracted issues against evidence and approve final response text.

Layout:

```text
Left pane: issue queue
Center pane: evidence preview plus step/transcript context
Right pane: issue detail and reviewer fields
Bottom bar: Approve, Request Changes, Reject, Defer, Create Email Draft
```

Issue queue row fields:

- priority,
- status,
- category,
- concise title,
- confidence,
- evidence count,
- source step numbers,
- warning indicator if evidence/privacy concerns exist.

Center evidence pane:

- selected image or derived evidence preview,
- evidence ID and kind,
- source step context,
- transcript ref excerpt when available,
- navigation for evidence linked to selected issue,
- warning if evidence is discarded, missing, privacy unknown, or hash invalid.

Right issue detail:

- AI title and summary as read-only source fields,
- observed behavior,
- expected behavior,
- impact,
- category/priority/confidence,
- linked evidence IDs,
- reviewer edited title,
- reviewer edited summary,
- reviewer edited response draft,
- reviewer notes,
- status/event history.

Critical rule:

Reviewer edits must not overwrite AI-suggested fields. The UI should show AI source text and reviewer-approved text as distinct fields.

Evidence interaction rules:

- Clicking an evidence ID selects the preview.
- Evidence preview always shows the evidence ID, not only filename.
- If an issue references evidence not present in the manifest, the issue is blocked from approval.
- If evidence privacy is `unknown`, approval may continue only with an explicit warning in local prototype, and must be governed by the compliance addendum before real PHI use.

Approval rules:

- Approve requires an approved title, approved summary, approved response, and at least one valid evidence ID.
- Reject requires a note.
- Defer requires a reason or tag.
- Changes Requested moves issue back to `needs_review` and records an event.
- Create Email Draft is enabled only after approval.

Acceptance criteria:

- Reviewer can approve an issue without losing the original AI suggestion.
- Reviewer can see exactly which evidence supports the issue.
- Reviewer cannot accidentally approve an issue with missing evidence.
- Every material decision appends an audit event.

## View 3: Email Draft

Purpose: turn an approved issue into a shared-team communication record.

MVP local mode:

- draft-only,
- no live send,
- no provider credentials,
- no real team email until provider and compliance decisions exist.

Layout:

```text
Left pane: approved issues needing draft/queue
Center pane: email body preview
Right pane: approval and evidence summary
Bottom bar: Save Draft, Mark Ready, Queue Send, Cancel Draft
```

Fields:

- subject,
- body markdown,
- recipient/shared inbox placeholder,
- issue ID,
- approval ID,
- evidence IDs,
- delivery state,
- error state when applicable.

Rules:

- Email text must come from approved reviewer fields, not raw AI fields.
- Changing approved text after draft creation requires either a new approval event or a clear revision event.
- Send/queue actions remain disabled until shared inbox configuration and compliance decisions exist.

Acceptance criteria:

- Dashboard can create a draft-only email record from approved issue data.
- The draft preserves issue ID and approval ID.
- No live email is sent in the local prototype.

## View 4: Archive Search

Purpose: search and inspect closed audit records.

Layout:

```text
Top search/filter row
Left/center archive results
Right archive detail panel
Bottom bar: Open Package, Open Evidence, Export Record
```

Search fields:

- title/summary text,
- category,
- priority,
- status,
- tags,
- session ID,
- package ID,
- date range,
- evidence ID.

Archive result fields:

- closed date,
- title,
- category,
- priority,
- close reason,
- tags,
- evidence count,
- immutability/hash status.

Rules:

- Archive records are read-only in the dashboard.
- Edits after archive require a new superseding record, not mutation of the old record.
- Search should not require AI/provider access.

Acceptance criteria:

- Reviewer can find an archived issue by title, category, priority, tag, or evidence ID.
- Archive detail exposes package/session lineage.
- Record hash/immutability state is visible.

## Visual Density And Typography

Use compact desktop sizing:

- page-level headings small and restrained,
- row text readable at normal desktop distance,
- strong contrast for issue titles, state, and action labels,
- quiet grey for secondary metadata,
- no oversized marketing-style cards,
- no nested cards,
- cards only for repeated issue/package rows or modal content,
- stable pane widths with resizable splitters where appropriate.

Recommended semantic color roles:

| Role | Color Direction |
| --- | --- |
| Active/selected | `#e8a87c` peach |
| Approved/pass/local ready | green |
| Failed/high risk/blocking | red |
| Warning/deferred/privacy unknown | amber |
| Processing/queued | subdued blue or neutral |
| Archived/inactive | muted grey |

The palette should not become one-note purple/blue. Use neutral charcoal and graphite surfaces, peach selection, and semantic states sparingly.

## Component Inventory

Minimum component set:

- shell frame,
- top context bar,
- status chip,
- package row,
- issue row,
- evidence preview,
- evidence strip,
- transcript excerpt block,
- reviewer edit form,
- event timeline,
- validation warning panel,
- bottom action bar,
- confirmation modal,
- archive result row,
- search/filter row.

Use icons for compact actions when the meaning is standard, with tooltips. Use text buttons for approval workflow actions where clarity matters.

## Empty, Loading, And Error States

Package Inbox:

- empty: no packages found in configured local folder,
- loading: scanning packages,
- error: package unreadable or manifest invalid.

Issue Review:

- empty: package has no extracted issues,
- blocked: extraction references missing evidence,
- warning: privacy state unknown,
- error: extraction JSON invalid.

Email Draft:

- empty: no approved issues ready for draft,
- disabled send: provider/compliance not configured,
- error: draft cannot be written.

Archive Search:

- empty: no records match filters,
- error: archive JSONL unreadable or hash mismatch.

## Keyboard And Workflow Ergonomics

Recommended shortcuts for later implementation:

| Shortcut | Action |
| --- | --- |
| Up/Down | Move issue/package selection. |
| Enter | Open selected package/issue. |
| A | Approve when form is valid. |
| R | Reject with note prompt. |
| D | Defer with reason prompt. |
| E | Create email draft from approved issue. |
| Ctrl+F | Focus search/filter. |
| Ctrl+L | Copy selected evidence ID. |

Shortcuts must not be required to complete the workflow.

## Safety And Pushback States

The dashboard should make risky states visible enough that a reviewer pauses.

Show blocking alerts for:

- missing evidence IDs,
- invalid package hash,
- issue references evidence not in manifest,
- package not `local_ready` or `triage_ready` for the requested action,
- email send attempted without explicit provider/compliance configuration.

Show warnings for:

- privacy state unknown,
- transcript missing,
- optional metadata missing,
- AI confidence below threshold,
- deferred or unresolved validation warnings.

The UI should push back through disabled actions, warning panels, and required notes. It should not allow speed to erase audit integrity.

## First Local Prototype Scope

Build only enough dashboard UI to prove the review loop against local files:

1. Load local packages and issue extraction JSON.
2. Show package inbox.
3. Show issue queue.
4. Preview linked evidence.
5. Edit reviewer title/summary/response fields.
6. Approve/reject/defer issues into local JSON records.
7. Create draft-only email records.
8. Write archive JSONL records.
9. Search archive text and metadata.

Explicitly leave out:

- live Dropbox upload,
- live AI calls,
- live email send,
- real PHI use,
- clinical image editing,
- full v4 clinical shell integration.

## Implementation Notes For Claude

When Claude receives this work:

- Match Claude's own v4 redesign discipline.
- Use the dashboard as a compact evidence review tool, not a new visual experiment.
- Notify Darrin if any requirement conflicts with the redesign, MVP boundary, compliance, testability, or evidence integrity.
- Push back before implementing risky shortcuts.
- Do not claim v4 is complete because this dashboard exists. This is Testing + Audit MVP support, not the full clinical v4 product.

## Acceptance Criteria

The dashboard UX spec is satisfied when a reviewer can complete this local-only story:

1. Open the Package Inbox.
2. Select a validated package.
3. Open extracted issues.
4. Select an issue.
5. Inspect its evidence by evidence ID.
6. Compare AI source fields with reviewer-edited fields.
7. Approve or reject the issue with required notes/fields.
8. Generate a draft-only email record for approved issues.
9. Archive the closed issue.
10. Search the archive and reopen the read-only record.

All records must preserve package ID, session ID, run ID, issue ID, approval ID where applicable, evidence IDs, status events, and immutable archive lineage.

## Open UX Decisions

| Decision | Default For Prototype |
| --- | --- |
| Is the dashboard a separate app or PG admin surface? | Separate local PySide6 app/prototype under Codex until integration is chosen. |
| Should audit appear in clinical v4 top modules? | No. Keep separate from Library, Mount, Review, Compare, Present. |
| Can reviewer approve with privacy `unknown`? | Local prototype may allow with warning; real PHI use needs compliance addendum. |
| Should email send be enabled? | No. Draft-only until provider/compliance decisions. |
| Should package upload be exposed in dashboard first version? | Not until package validation and local review loop are proven. |
| Should AI confidence auto-prioritize issues? | It may sort as secondary signal, but must not replace reviewer judgment. |
