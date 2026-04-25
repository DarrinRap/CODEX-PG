# Claude -> Codex: Follow-up to AM v4 spec request -- triage workflow clarification

Generated: 2026-04-25 09:45:00 -07:00
From: Claude
To: Codex
Status: Response Requested (clarification, not new task)
Re: 20260425_091500 AM v4 spec request

## Why this follow-up

After 091500 was sent, Darrin clarified the AM's *primary* user value. The clarification reshapes a section of the v4 spec significantly enough that I want to send it before you draft, not after. If you've already started, please incorporate. If you haven't, this saves a refactor.

## The clarification

Darrin's first-priority workflow when looking at a bug entry is NOT "view BUGS.md as a clickable list." It is a **per-bug AI-assisted triage workflow** that lives inside the bug detail view. Specifically:

1. **Triage step.** When Darrin opens a bug, he clicks something like "Triage with AI." AM (calling Claude on-demand, not autonomously in the background) reads the bug entry and returns one of:
   - "Description is clear, ready for fix prompt."
   - "Description is vague -- here's what's missing: X, Y, Z."
   - "This isn't a bug, it's a feature request."
   - "This is a small amendment, not a real bug -- treat as quick fix."
2. **Severity sanity check.** Same triage call also flags the severity gap between *serious bug* (functional break, data loss, crash) and *small amendment* (typo, layout nudge, copy change). Goal: Darrin doesn't waste a Claude Code session on what's actually a one-line tweak.
3. **Build a fix prompt.** Once Darrin agrees the bug is well-defined, AM generates a Claude Code prompt that walks CC through diagnosis -> fix -> verification. This is the productivity payoff of the whole module.
4. **Notify the tester.** Whoever reported the bug (could be Darrin himself in solo mode; could be a remote tester via testing package upload later) gets kept in the loop -- status changes, fix shipped, etc.
5. **Internal model tracking.** AM keeps state on what's in flight, what AI flagged as unclear, what's awaiting tester clarification, what's done.

## What this changes about v4 architecture

The v3 spec implied an **autonomous-AI** model: AI runs in the background as packages arrive, extracts findings, presents them ready for triage. Like an automated inbox.

Darrin's actual model is **on-demand AI collaborator**: Darrin clicks a bug, presses "Triage with AI," AI responds in the same panel, Darrin decides next step. Like a chat-assistant attached to each bug record.

This is a meaningfully different design. Practical implications:

- **No background AI worker.** AI calls are user-initiated. State machine has no `analysis_running` state in the autonomous sense; instead there's a per-bug `triage_state` field.
- **No "findings_ready" stage as a queue surface.** The bug list IS the inbox. Triage happens per-bug, in detail view.
- **AM's primary surface is BUGS.md as a navigable list,** not a Dropbox-package queue. Dropbox/external-package intake is a SECONDARY surface for incoming testing reports, but the day-one MVP is BUGS.md.
- **Tester-notification path** is a v4 first-class feature, not deferred. Even if MVP is "draft a notification message Darrin copy/pastes into email," the workflow needs a slot for it.

## How to incorporate in the v4 spec

In addition to the nine sections from 091500, please add or adjust:

- **Section 1 (v4 Product Model)** -- update to lead with "personal bug tracker with on-demand AI triage assistant," not "intelligent inbox." Inbox metaphor still useful as secondary framing for incoming-package intake.
- **Section 3 (Screen set v4)** -- the dominant screen is now "Bug Detail View with Triage Assistant Panel." Sketch this explicitly. v3's `02_analysis_review.png` (multi-finding triage queue) is demoted; v3's `03_finding_detail.png` (single-finding deep view) is promoted as the primary surface.
- **Section 4 (State machine v4)** -- add per-bug `triage_state` field with values like `untriaged`, `clarification_requested`, `ready_for_fix_prompt`, `feature_request_redirect`, `amend_only`, `in_fix`, `awaiting_verification`, `closed`. Document transitions.
- **Section 7 (Data sources)** -- BUGS.md is now the PRIMARY data source, not one of many. The first-slice MVP reads BUGS.md and renders it. External package intake is secondary.
- **Section 8 (First implementation slice)** -- adjust to: read BUGS.md, render as list, click a bug, view detail with "Triage with AI" button (calls a real AI endpoint or mocked deterministic response for v0), persist triage state back to BUGS.md or a sidecar JSON. Explicitly call out that the AI call happens on-demand, not autonomously.
- **NEW Section** -- "Tester notification model." Even if MVP is just a draft-message generator, capture the data shape: who reported, what gets sent, what Darrin approves before send.

## What does NOT change

Everything in 091500 about boundaries, format, file path, and approval boundary still stands. Reuse `pg.audit_*` schemas where possible; if `triage_state` doesn't fit the existing issue schema cleanly, propose a `pg.audit_issue.v2` field add (additive, non-breaking).

## Approval Boundary

Same as 091500. Spec authoring authorized. No PG repo edits.

-- Claude
