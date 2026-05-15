---
spec_id: SPEC_0010
title: "Vellum Primary Purpose Completion and Quality-of-Life Upgrades"
status: READY_FOR_CD_REVIEW
author: CODEX
assignee: CC
created: 2026-05-09
version: 1
bug_refs: []
task_queue_ref: null
dispatch_ref: 20260509_1801_CODEX_to_CLAUDE_vellum_primary_purpose_qol_spec
spec_path: workflows/specs/SPEC_0010_vellum_primary_purpose_completion_qol_v1.md
source_user_request: "Write detailed spec for missing Vellum primary-purpose functionality and recommended quality-of-life upgrades; send to CD for CC routing."
approval_boundary: CD routes to CC; Codex does not issue implementation-go or commit-go.
related_specs:
  - SPEC_0001 Vellum approval viewer upgrade
  - SPEC_0008 Vellum Presentation Review Mode
  - SPEC_0009 BA Runtime Vellum Missed-Bug Checks
  - workflows/design/VELLUM_APPROVAL_VIEWER_TECHNICAL_UPGRADE_SPEC_v1.md
---

# SPEC_0010 - Vellum Primary Purpose Completion and Quality-of-Life Upgrades

## 1. Purpose

Vellum's primary job is not merely to display mockup images. Its primary job is to let Darrin review a packet, make durable decisions, identify blockers, and produce a CD-owned handoff artifact that can safely become CC implementation scope.

This spec defines the missing, partially shipped, or still-at-risk functionality needed for Vellum to become a reliable approval-to-handoff tool, plus quality-of-life improvements that reduce review friction without expanding implementation authority.

This is a CC-facing implementation spec for CD review and routing. Codex is not sending implementation-go or commit-go.

## 2. Current Context and Non-Duplication Rule

Existing authority already covers much of this ground:

- SPEC_0001 / `VELLUM_APPROVAL_VIEWER_TECHNICAL_UPGRADE_SPEC_v1.md` covers packet workflow, decisions, queueing, version history, handoff-ready logic, export, fixtures, smoke coverage, inbox loading, and validation.
- SPEC_0008 covers Presentation Review Mode.
- SPEC_0009 covers future BA runtime detection of Vellum missed-bug classes.
- Recent v5.3.0 work appears to have fixed or advanced several hands-on issues, including help/search, inbox packet loading, filmstrip sizing, background, shortcuts, and context menu defects.

Therefore CC must not blindly reimplement work that already shipped. The first required step is an implementation-state audit that marks each item in this spec as:

- `already complete and verified`
- `implemented but needs hardening`
- `partially implemented`
- `missing`
- `defer with CD approval`

The purpose of this spec is to close the product gap, not create duplicate UI paths.

## 3. Product North Star

A complete Vellum workflow should answer these questions without manual interpretation:

1. What packet am I reviewing?
2. Which items still need my decision?
3. Which items are approved for direction?
4. Which items are explicitly rejected, declined, future/not-approved, or out of coding scope?
5. Which approved items are current versus superseded?
6. What exactly blocks handoff readiness?
7. When everything is ready, what artifact should CD review before authorizing CC implementation?
8. Can I review quickly, full screen, with minimal chrome, without losing context or decision durability?

If Vellum cannot answer those questions, it is still a viewer with notes, not yet a dependable approval system.

## 4. Scope Summary

This spec has five workstreams:

1. Primary-purpose state model audit and completion.
2. Handoff-ready and blocker explanation hardening.
3. Export package and CD-review scope candidate hardening.
4. Presentation/review speed layer and keyboard-first review integration.
5. Quality-of-life upgrades for repeated review sessions.

The work should be sequenced after any in-flight v5.3.0/v5.3.1 work is committed and clean, unless CD explicitly inserts this into an existing Vellum phase.

Priority rule:

- P0: prove or repair the primary approval-to-handoff path: packet load, durable decisions, blocker explanation, handoff-ready state, and CD-review export.
- P1: integrate Presentation Review Mode with the same durable decision path.
- P2: add queue, search, session recovery, filmstrip, tooltip, and context-menu QoL only after P0 is proven or when CD explicitly schedules those items.

## 5. Non-Goals

This spec does not authorize:

- CC implementation from a Vellum export without CD approval.
- Automatic mailbox dispatch of implementation-go or commit-go.
- Broad redesign of Vellum's visual language.
- Replacement of existing packet format unless a Step 0 audit proves it cannot support the workflow.
- New background watchers or tray processes.
- Patient data or PHI in fixtures.
- Bypassing existing smoke, pytest, BA, or design-lint gates.

## 6. Step 0 Required Audit

Before code changes, CC must file Step 0 RTC to CD with these findings.

### 6.1 Current Implementation Map

Read and summarize:

- `workflows/design/VELLUM_APPROVAL_VIEWER_TECHNICAL_UPGRADE_SPEC_v1.md`
- `C:\CODEX PG\CODEX Canonical Specs\VELLUM_PRESENTATION_REVIEW_MODE_SPEC_v1.md`
- `workflows/design/applets/am_mockup_review.py`
- `workflows/design/applets/vellum_approval/models.py`
- `workflows/design/applets/vellum_approval/widgets.py`
- `workflows/design/applets/vellum_approval/packet_io.py`
- `workflows/design/applets/vellum_approval/queueing.py`
- `workflows/design/applets/vellum_approval/exporter.py`
- `scripts/vellum_smoke_test.py`
- `scripts/build_vellum_packet.py` if present
- `BUGS.md` entries for current Vellum OPEN and recently FIXED items
- current repository state, including relevant v5.3.0/v5.3.1 commit or branch status, so CD can tell whether CC is auditing shipped work, parked work, or uncommitted work

For each feature below, report exact file/function/class locations and current status.

### 6.2 Required Status Matrix

CC must include this table in Step 0 RTC:

| Area | Expected source | Current file/function | Status | Evidence | Proposed action |
| --- | --- | --- | --- | --- | --- |
| Packet load/reload | SPEC_0001 / #232 | TBD | TBD | TBD | TBD |
| Decision persistence | SPEC_0001 Phase 3 | TBD | TBD | TBD | TBD |
| Handoff-ready computation | SPEC_0001 Phase 4 | TBD | TBD | TBD | TBD |
| Handoff blocker reasons | SPEC_0001 Phase 4 | TBD | TBD | TBD | TBD |
| Queue filters | SPEC_0001 Phase 4 | TBD | TBD | TBD | TBD |
| Version history/superseded | SPEC_0001 Phase 4 | TBD | TBD | TBD | TBD |
| DECISION_SUMMARY export | SPEC_0001 Phase 5 | TBD | TBD | TBD | TBD |
| CD scope candidate export | SPEC_0001 Phase 5 | TBD | TBD | TBD | TBD |
| Export button state | SPEC_0001 Phase 5 | TBD | TBD | TBD | TBD |
| Presentation mode | SPEC_0008 | TBD | TBD | TBD | TBD |
| Full-screen decision keys | SPEC_0008 | TBD | TBD | TBD | TBD |
| Autosave/backup visibility | SPEC_0001 | TBD | TBD | TBD | TBD |
| Smoke/fixture coverage | SPEC_0001 Phase 6 | TBD | TBD | TBD | TBD |
| BA runtime coverage | SPEC_0009 | TBD | TBD | TBD | TBD |

### 6.3 Sequencing Decision

Step 0 must recommend one of these:

- Option A: This spec is already covered by Vellum Phases 4-6 plus SPEC_0008; no new implementation spec needed, only validation/hardening.
- Option B: Some primary-purpose items remain missing; implement the missing subset as the next Vellum phase.
- Option C: Presentation Mode should ship first because Darrin's review speed is the bottleneck, then handoff/export hardening follows.
- Option D: Handoff/export should ship first because approval authority is the bottleneck, then Presentation Mode follows.

CC must wait for CD clearance after Step 0.

## 7. Workstream 1: Primary-Purpose State Model Completion

### 7.1 Required Decision States

Vellum must support and persist at minimum:

- `unreviewed`
- `approved_direction`
- `needs_changes`
- `rejected`
- `future_not_approved`
- `superseded`

If current models use different enum names, CC must map them explicitly in Step 0 and avoid renaming unless CD approves. The user-facing labels may differ, but export semantics must be unambiguous.

### 7.2 Required Per-Record Fields

Every mockup record must have enough data to support review, handoff, and export:

- stable `mockup_id`
- image path or relative packet image reference
- display label/state label
- version identifier or sortable version metadata
- current status
- notes / Darrin notes
- decline/rejection reason when supplied
- overlay/annotation references
- side-by-side-only flag if applicable
- superseded/current relationship when applicable
- required-state membership or explicit non-required reason
- last updated timestamp
- decision history list

CC must preserve unknown fields on write.

### 7.3 Decision History Rules

Every decision write must append an immutable history entry:

- timestamp
- previous status
- new status
- note delta or note snapshot
- view mode used, such as normal, split-view, presentation
- actor/source, such as `darrin_vellum_ui`
- image/mockup id

History entries must be read-only in UI. If a current decision is changed, write a new history row; do not mutate old history.

### 7.4 Acceptance Criteria

- Decisions survive app close/reopen.
- Unknown packet fields survive decision writes.
- Each decision write produces one history entry.
- Current status is clearly derived from the latest current record, not from stale history alone.
- Superseded approvals cannot be exported as current coding scope.

## 8. Workstream 2: Handoff-Ready Hardening

### 8.1 Definition

Vellum is handoff-ready only when every required current mockup state is either:

- `approved_direction`, or
- `future_not_approved` with an explicit out-of-scope marker.

Handoff-ready must be false if any required state is:

- missing
- unreviewed
- needs changes
- rejected without replacement
- superseded with no approved current replacement
- side-by-side-only orientation reference
- malformed or missing required metadata
- blocked by failed packet preflight

### 8.2 Blocker Reason Engine

The blocker reason must be computed from structured data, not assembled from UI strings. It should return:

- `handoff_ready`: boolean
- `blocking_count`: integer
- `first_blocking_reason`: short display string
- `blocking_reasons`: list of structured objects

Each blocker object should include:

- blocker code, e.g. `unreviewed_required_state`
- mockup id or required state id
- display label
- current status
- expected status/action
- whether user action or packet repair is needed

### 8.3 UI Requirements

The approval panel header must show:

- green `Handoff Ready` badge when true
- visible blocked badge when false
- first blocking reason in plain language
- count of remaining blockers

The UI must not imply CD authorization. Suggested blocked text examples:

- `3 states unreviewed`
- `Needs replacement for rejected state: Develop narrow`
- `Superseded approval has no current replacement`
- `Packet preflight failed`

### 8.4 Acceptance Criteria

- Handoff badge recomputes after every decision write.
- Handoff badge recomputes after packet reload.
- Handoff false states list exact blockers.
- Handoff true state requires all required states complete.
- Export button state follows handoff readiness.
- Unit tests cover every blocker code.

## 9. Workstream 3: Export Package and CD Review Candidate

### 9.1 Exported Files

When handoff-ready is true, Vellum must generate or update:

- `DECISION_SUMMARY.md`
- `_scope_candidate.md`

The names may be adjusted only if existing code has already standardized different names. If so, Step 0 must identify the shipped names and CD must confirm.

### 9.2 DECISION_SUMMARY.md Requirements

`DECISION_SUMMARY.md` must include:

- packet name/path
- generated timestamp
- handoff-ready status
- total record count
- counts by status
- table of every current record
- annotations column
- notes snippet column
- blocking reasons if not ready
- version/superseded summary
- explicit statement that this summary is review evidence, not implementation authorization

Required table columns:

```text
mockup_id | label | version | status | view_mode | annotations | notes_snippet | current_or_superseded
```

### 9.3 _scope_candidate.md Requirements

`_scope_candidate.md` is a CD-review candidate only. It must include the mandatory authority header:

```text
FORMAL CC AUTHORIZATION REMAINS CD-OWNED.
Codex must not send implementation-go or commit-go directly to CC.
This is a CD-review scope candidate pending CD review and authorization.
```

It must include in coding candidate scope only records with current `approved_direction` status.

It must explicitly exclude and label:

- `future_not_approved`
- `rejected`
- `needs_changes`
- `unreviewed`
- `superseded`
- side-by-side-only orientation references
- malformed records

### 9.4 Export UX

The export control must:

- be disabled when handoff-ready is false
- show the first blocking reason near the disabled state
- be enabled when handoff-ready is true
- write both files atomically
- create backups before overwrite
- show success feedback with exact filenames
- show clear error feedback if write fails

### 9.5 Acceptance Criteria

- Export false/true states are covered in smoke tests.
- Files are written inside the packet folder only.
- Path traversal is rejected.
- Existing source images are not modified.
- Existing overlay files are not deleted by export.
- Scope candidate contains the mandatory authority header verbatim.
- Non-approved items never appear in the coding-scope section.

## 10. Workstream 4: Presentation Review Mode Integration

SPEC_0008 remains the authority for Presentation Review Mode. This spec adds integration requirements so Presentation Mode supports Vellum's primary workflow rather than becoming a separate viewing-only mode with a separate decision path.

### 10.1 Entry and Visibility

- `F11` toggles Presentation Review Mode.
- Normal chrome is hidden.
- Markup overlays are hidden by default and restored on exit.
- Floating metadata panel remains visible.
- Metadata panel shows filename, index/total, date, current decision, and short note/decline summary.

### 10.2 Decision Keys

- Left/Right navigate.
- Up Arrow first press enters pending keep/lock state.
- Pending keep/lock state must show a very prominent Up Arrow visual confirmation affordance over the image, with enough contrast and size to be unmistakable at review distance.
- Second Up Arrow confirms keep/lock.
- Down Arrow first press opens optional decline text entry.
- Pending decline state must show a very prominent Down Arrow visual confirmation affordance and a focused optional text field for the decline description.
- Second Down Arrow confirms declined/rejected with optional note.
- While the decline text field is focused, the second Down Arrow still means confirm decline; it must not navigate away, insert stray text, or silently dismiss the note.
- Esc cancels pending action or exits mode.
- 5-second timeout cancels pending confirmation.

### 10.3 Persistence Integration

Presentation Mode decisions must use the same decision persistence path as normal mode. They must:

- update current status
- append decision history with `view_mode_used = presentation`
- recompute handoff readiness
- update floating metadata immediately
- preserve notes and overlays

### 10.4 Acceptance Criteria

- Presentation decisions are visible in normal mode after exit.
- Normal-mode decisions are visible in Presentation Mode metadata.
- Confirmation timeout prevents accidental writes.
- Navigation cancels pending confirmations.
- Handoff-ready updates after presentation decisions.
- Smoke or Qt tests cover entry/exit, navigation, keep, decline, cancel, timeout, and persistence.

## 11. Workstream 5: Quality-of-Life Upgrades

These upgrades are recommended because Vellum will be used repeatedly for large review packets. They should be implemented only after primary-purpose items are complete or when CD explicitly schedules them.

### 11.1 Review Queue Ergonomics

Recommended:

- filter chips: All, Unreviewed, Needs Changes, Approved, Rejected, Future, Blockers
- unresolved-first sort
- stable packet order inside each group
- current item counter
- jump to next unresolved
- jump to next blocker
- status counts always visible

Acceptance:

- Filters never change persisted packet order.
- Clearing filters restores packet order.
- Current selection survives filter changes when still visible.
- If current item becomes hidden, selection moves to nearest visible item with clear feedback.

### 11.2 Version and Superseded Clarity

Recommended:

- version history panel per mockup
- `Current` badge
- `Superseded` badge
- warning when user views a superseded approved item
- direct jump from superseded item to current replacement

Acceptance:

- Superseded record cannot be exported as coding scope.
- Current replacement relationship is visible.
- Version history is chronological and read-only.

### 11.3 Review Session Recovery

Recommended:

- recent packets list
- reopen last packet
- restore selected mockup, filter, splitter sizes, and zoom mode
- remember whether the prior session ended in Presentation Mode, but reopen in normal mode and offer a clear `Resume Presentation` action instead of surprising the user with immediate full-screen restore
- show last autosave/backup timestamp
- recovery prompt if a newer backup exists

Acceptance:

- Session restore never overwrites packet data.
- Session restore never enters full-screen Presentation Mode without an explicit user action.
- If last packet path is missing, Vellum shows clear recovery UI.
- Backup restore requires confirmation.

### 11.4 Decision Feedback and Trust

Recommended:

- brief toast after every decision write
- visible dirty/saving/saved state
- exact backup path in advanced/details view
- error banner if save fails
- no silent failures

Acceptance:

- Save failure leaves UI decision state unchanged or clearly marked unsaved.
- User can tell when the packet is saved.
- Tests simulate write failure.

### 11.5 Keyboard-First Review

Recommended shortcuts:

- Left/Right: previous/next
- Home/End: first/last if already present
- `N`: next unresolved
- `B`: next blocker
- `/` or `Ctrl+F`: focus filter/search
- `F11`: Presentation Mode
- `Esc`: cancel modal/pending action/exit presentation

Acceptance:

- Shortcut collision audit required before implementation.
- Shortcuts disabled or redirected when text entry is focused.
- Help dialog lists all active shortcuts.

### 11.6 Filmstrip and Image Inspection QoL

Recommended:

- larger crisp thumbnails with DPR-aware pixmaps
- status badges on thumbnails
- tooltip with filename, status, note snippet, modified date
- optional filename/date below thumbnail
- persistent filmstrip height
- quick toggle for filmstrip visibility

Acceptance:

- No thumbnail text clipping at 1366px and 1750px.
- Status badge is visible but does not obscure the image content meaningfully.
- Filmstrip height restore is bounded to current window size.

### 11.7 Context Menus

Recommended context menu targets:

- canvas empty area
- selected markup/stencil
- filmstrip item
- approval panel record/state row

Expected actions may include:

- copy filename/path
- reveal in folder
- mark decision
- clear pending decision
- jump to current version
- show history
- export summary when allowed

Acceptance:

- Context menus never expose destructive actions without confirmation.
- Menu actions respect current handoff/export state.
- Tests monkeypatch `QMenu.exec` to avoid blocking.

### 11.8 Search and Findability

Recommended:

- packet-wide search by filename, label, status, note, version
- help search already exists or should be verified complete
- search result count
- keyboard focus shortcut

Acceptance:

- Search does not mutate data.
- Search updates visible queue/filter only.
- Clearing search restores prior filter state.

## 12. Validation Requirements

### 12.1 Automated Tests

Required test categories:

- pure unit tests for handoff blocker engine
- packet read/write tests preserving unknown fields
- decision history append tests
- export generation tests
- path traversal rejection tests
- presentation mode state machine tests
- shortcut collision tests
- filter/sort tests
- context menu availability tests with `QMenu.exec` monkeypatch
- write failure tests

### 12.2 Smoke Tests

Update `scripts/vellum_smoke_test.py` or current Vellum smoke equivalent to cover:

- load packet
- review unreviewed item
- write decision
- filter by status
- see handoff false blocker
- make packet handoff-ready using fixture
- export summary/candidate
- verify files written
- enter/exit Presentation Mode
- presentation keep decision
- presentation decline with note
- reload packet and verify decisions/history persist

If `QT_QPA_PLATFORM=offscreen` still hangs (see #236), keep windowed smoke but minimize popups and document the limitation.

### 12.3 Visual Evidence

Capture screenshots for CD review:

- queue with unresolved-first ordering
- blocker banner/blocked handoff state
- handoff-ready state
- export success state
- version history panel
- Presentation Mode normal metadata panel
- Presentation Mode pending Up confirmation
- Presentation Mode Down note entry
- filmstrip with status badges
- recent/recovery panel if implemented

Manual visual pass requirements:

- capture at 1366px-wide and 1750px-wide desktop windows
- capture at least one high-DPI or scaled-display run if available
- verify no clipping in filmstrip labels, status chips, decision buttons, metadata panels, export controls, or blocker banners
- verify Presentation Mode image framing, floating panel placement, pending Up confirmation symbol, and Down note entry are readable without hiding the reviewed image's essential content

### 12.4 BA Requirements

After SPEC_0009 is implemented, BA should be able to detect regressions in:

- text clipping
- runtime background palette
- crash safety
- filmstrip DPR quality
- filmstrip layout
- resizability
- tooltip coverage
- context menu availability
- help content
- scene pan freedom

Until SPEC_0009 is implemented, CC must provide manual screenshot evidence for visual and runtime claims.

## 13. Suggested Implementation Sequence

Recommended sequencing after current in-flight work is clean:

1. Step 0 implementation-state audit.
2. Handoff-ready blocker engine hardening.
3. Export package hardening.
4. Version/superseded clarity hardening.
5. Presentation Mode from SPEC_0008, integrated with decision persistence.
6. Queue/filter/search QoL.
7. Session recovery and backup visibility.
8. Filmstrip/status/tooltip/context-menu polish.
9. Smoke/fixture/visual evidence pass.
10. CD review package.

If CD decides Phases 4-6 already cover items 2-4, CC should treat this spec as a validation and gap-closure checklist rather than a new implementation branch.

## 14. Done Definition

Vellum can be considered primary-purpose complete when:

- A packet can be loaded or generated from an inbox folder.
- Darrin can review every required item quickly.
- Decisions persist with history.
- The app clearly shows unresolved items and blockers.
- Handoff-ready status is trustworthy and explainable.
- Export generates `DECISION_SUMMARY.md` and `_scope_candidate.md`.
- Scope candidate cannot be mistaken for CD authorization.
- Presentation Mode supports fast review without losing metadata or persistence.
- Smoke tests and screenshots prove the workflow.
- No known data-loss crash or ordinary-review crash remains.
- Any shutdown-only or environment-limited crash that CD allows to remain must be documented as nonblocking with reproduction notes and explicit CD acceptance.

## 15. CD Routing Notes

Recommended CD action:

- Route to CC as a Step 0 audit/hardening dispatch after v5.3.0/v5.3.1 state is settled.
- Instruct CC to identify which pieces are already shipped before coding.
- Keep SPEC_0008 and SPEC_0001 as authority for their covered areas.
- Treat this spec as the product-completion checklist and QoL prioritization layer.

## 16. Self-Review Log

Pass 1: 6 issues fixed — clarified missing versus partially shipped scope; added P0/P1/P2 priority rule; required v5.3.0/v5.3.1 repository-state audit; made Presentation Mode session restore opt-in; added 1366px/1750px/high-DPI visual pass requirements; strengthened crash done definition.

Pass 2: 2 issues fixed — required prominent Up/Down confirmation affordances; defined Down Arrow behavior while decline text entry is focused.

Pass 3: 1 issue fixed — replaced casual "visual toy" wording with precise decision-path integration language.

Pass 4: 1 issue fixed — assigned official SPEC_0010 metadata and registry path instead of leaving the spec as an unindexed Codex-local document.

Pass 5: 0 significant issues fixed.
