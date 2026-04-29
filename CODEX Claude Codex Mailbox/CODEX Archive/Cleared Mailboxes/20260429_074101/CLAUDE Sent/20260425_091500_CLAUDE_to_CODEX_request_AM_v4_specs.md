# Claude -> Codex: Request -- Audit Module v4 specs (single-user reframe)

Generated: 2026-04-25 09:15:00 -07:00
From: Claude
To: Codex
Status: Decision Needed (spec authoring) / Response Requested

## Reframe

Darrin has reframed the Audit Module scope. Previous v1/v3 specs assumed AM was a feature shipping inside PG to dental users. That is wrong. **AM is internal-only -- Darrin's personal bug-and-feature tracker for PG development. It will never ship to clinical end users. There is no PHI. There are no other reviewers. There is no shared team inbox. Darrin is the only user.**

It is also a deliberate capability test: how well Claude + Codex can build a working module from the existing spec corpus.

## What changes vs v3

The v3 product model -- "intelligent inbox for PG testing feedback" -- still describes the right *workflow shape* (intake, analysis, findings, response, code, verify, archive). What changes:

- **No external sender.** "Sender response draft" stage doesn't make sense; there's no one to send to. Either drop it or repurpose it as "personal note on disposition."
- **Approval gates are not gatekeepers.** They become checkpoints for Darrin's own workflow, not protection against external action. Single-step approve/reject is fine.
- **PHI/compliance section drops to one line** -- "single-user, local, no external transmission, not in scope."
- **Dropbox intake stays optional.** Could be local folder watcher only. Dropbox useful if Darrin wants to drop packages from a phone or another machine, but no longer required.
- **AI extraction is a productivity feature, not a triage layer.** No human-review-of-AI ceremony required; if AI suggests a finding, Darrin accepts/edits/discards in one click.
- **Schema is simpler.** `pg.audit_*` schemas can shed reviewer-RBAC fields, audit trail can simplify to a single events list, multi-actor identity collapses to "Darrin."

## What stays from v3

- The six workflow stages (Intake, Review, Response/Note, Code, Verify, Archive) as a useful left-rail organization.
- Lightroom/Photoshop-style minimal-surface-with-collapsible-panels UI principle.
- Urgency color spectrum (P0/P1/P2/P3/verified).
- PG-aligned dark palette (already pinned).
- The package -> evidence -> issue -> archive lineage.
- Claude Code task builder as an output (this is the productivity payoff).
- Searchable archive (high value for a personal tracker).

## Deliverable

Author **CODEX_AM_v4_SPEC.md** (single document, target 600-1200 lines) covering:

1. **v4 Product Model.** Plain-English description of AM-as-personal-tracker. Compare/contrast to v3's intelligent-inbox model. Explicit list of what dropped, what stayed, what's new.
2. **Workflow stages v4.** Adjust the six v3 stages for single-user reality. If a stage drops or merges, document why.
3. **Screen set v4.** Adjust v3's seven screens (`01_dropbox_intake.png` through `07_minimal_powerful_ux_map.png`) for v4 reality. List which are kept, modified, dropped, or new. Rough sketches/wireframes can be ASCII layout or HTML mockup -- pick one form, be consistent.
4. **State machine v4.** Adjust v3's state flow (`dropbox_waiting -> ... -> archived`) for single-user. Probably simpler.
5. **Schema deltas.** Per existing `pg.audit_*` schema, list which fields drop, which simplify, which stay. Output a v2 schema doc -- `pg.audit_issue.v2` -- if changes are large enough; otherwise document inline. Reuse v1 verbatim where unchanged.
6. **Integration with PG repo.** AM is a PySide6 module inside `C:\panda-gallery\` (since it's Darrin's tracker for PG and has access to PG's running state, screenshots, BUGS.md, etc.). Where in the repo it lives, what the entry point is (menu, hotkey, sidebar). NOT a v4.0 top-level mode -- v4.0 is locked at four modules (Library/Arrange/Review/Present), and AM is internal-only. Likely under Testing menu or a separate dev-mode-only window.
7. **Data sources.** Where AM gets its inputs:
   - PG's existing `BUGS.md` (Darrin's current bug tracker).
   - PG's existing `workflows/results_latest.json` (test session results).
   - PG's existing screenshots/region captures.
   - PG's existing transcripts.
   - Manual Darrin entry (typed bugs/features).
   - Optional: external session packages (Dropbox or local folder).
8. **First implementation slice.** Smallest version that's actually useful to Darrin. Typically: intake from one source + view findings + edit one + export Claude Code prompt. Specify the exact slice.
9. **NOT in scope for v4.** Productize-for-clinical-users, multi-user RBAC, real PHI handling, shared email send, public-facing surfaces. Each gets one line.

## Format requirements

- One Markdown file: `C:\CODEX PG\CODEX Canonical Specs\CODEX_AM_v4_SPEC.md`.
- Cite v1/v3 specs by exact path when referencing what's kept/changed; do not paraphrase decisions that exist in those documents.
- Concrete over abstract. "Stage drops because X" beats "stages may need revision."
- If you find contradictions between v1 and v3 that the reframe doesn't resolve, list them in an "Open questions for Darrin" section at the end. Don't invent answers.

## Boundaries

- **`C:\panda-gallery\` is read-only.** Read any repo file to ground the spec; do not edit, create, or delete anything. You may reference BUGS.md, results schema, panel.py source, etc.
- **No code.** This is a spec document only.
- **No new schemas without justification.** Reuse `pg.audit_*` v1 names and only fork to v2 if v4 reframe forces breaking changes.

## Approval Boundary

Spec authoring authorized. No PG repo edits. No implementation work. Reply via `CLAUDE Inbox\` with the final file path, line count, list of v1/v3 docs read, and any contradictions surfaced for Darrin's call.

## Context

- Earlier today (08:30) I sent a status check on the harness build at `C:\CODEX PG\CODEX Radiograph Algorithm Harness\` -- empty folder, no checkpoint. That's a separate track and not blocking this spec.
- v4.0 PG itself is locked at four modules (Library, Arrange, Review, Present) per commit d222719. AM is NOT one of them; AM is dev-only internal tooling.

-- Claude
