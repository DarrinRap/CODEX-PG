# CODEX PAH Action Console Design Features

Status: v1 design documentation  
Last updated: 2026-04-28  
Primary app: `C:\CODEX PG\CODEX Agent Hub\CODEX_agent_hub_ui.html`  
Live local URL: `http://127.0.0.1:8765/`

## Purpose

The PAH Action Console is a screen-fit command center for coordinating Codex, Claude Desktop, Claude Code, and Darrin through local PAH mailboxes.

The interface is designed to answer one question first:

> What needs action right now?

It is not a generic dashboard. It is a guided triage surface for wake-ups, unread mailbox messages, Darrin decisions, route health, diagnostics, and safe next actions.

## Design Principles

### Action-first, not data-first

The console prioritizes action queue items over raw mailbox volume. Counts remain visible, but the central task is choosing the next item that needs a wake-up, decision, or review.

### Recognition over recall

The UI keeps operational instructions visible in context. Darrin should not need to remember how PAH wake-ups work, which mailbox was checked, or what line to paste into which AI.

### Progressive disclosure

The first view shows only the urgent work surface:

- agent state
- Start Here guidance
- filtered action queue
- selected item instructions
- wake line
- mailbox checks

Raw paths, message details, route diagnostics, and secondary actions appear only where they support the selected item.

### Safety before automation

The current PAH console is a read-only coordination surface. It can detect, explain, and prepare wake lines, but it does not directly wake agents, start watchers, send messages, or grant standing permissions.

Risky future actions must be disabled or confirmation-required from structured fields.

### Screen-fit operation

The app is designed to fit a normal desktop viewport without huge scrolling. Panels scroll internally where needed, but the primary workflow remains visible:

- left: agents
- center: Start Here and queue
- right: selected item and wake instructions
- bottom: diagnostics and git status

## Main Layout

### Top Bar

The top bar provides global orientation:

- app identity: `PANDA Agent Hub`
- current system state, such as `19 messages need wake-up`
- refresh timestamp
- refresh button
- disabled compose button in read-only v1

The system state uses a plain-language sentence instead of a vague status badge. It tells Darrin what kind of work is waiting.

### Left Panel: Agents

The Agents panel shows each participant as a compact status tile:

- Codex
- Claude Desktop
- Claude Code
- Darrin

Each tile includes:

- initials/avatar code
- status dot
- status label
- short current summary
- count value with a label, such as `53 queued`

Bare numbers are intentionally avoided. Every number has a label so the UI does not require interpretation.

### Center Panel: Start Here

The center panel is the primary workflow surface.

It contains:

- Start Here guidance card
- agent wake-up breakdown
- three-step operating instructions
- summary metrics
- filters
- action queue

The panel is named `Start Here` instead of `Action Queue` because the first-time user needs orientation before data.

### Right Panel: Selected Item

The Selected Item panel explains the currently highlighted queue item.

It includes:

- title
- plain-language summary
- structured facts
- wake line
- how-to-use-this-item steps
- mailbox checks
- action buttons

This panel is the "what do I do next?" area. It should always explain the next physical action Darrin needs to take.

### Footer

The footer shows:

- diagnostics summary
- git state

It is intentionally quiet. It exists for confidence and auditability, not primary workflow.

## Start Here Guidance

The guidance card is the main anti-overwhelm feature.

It includes:

1. A title describing the current work state.
2. A short operational explanation.
3. A breakdown of waiting wake-ups by target AI.
4. A three-step workflow.

Example:

```text
19 overdue messages need wake-up
Oldest first. A wake-up is unread for 1m or longer.
The selected item gives you the exact line to paste into the right AI.
Oldest is 10h 51m overdue.
```

### Wake-up breakdown

Mini pills summarize urgent work by target:

```text
8 claude-code
6 claude-desktop
4 codex
4 Darrin decisions
```

This prevents Darrin from having to scan every row just to understand which AI is behind.

The target mini pills are clickable. Selecting a pill filters the wake-up queue to that AI, and a Clear Agent button returns the queue to all overdue wake-ups.

### Three-step guide

The visible guide is:

1. Pick: click the oldest urgent item below.
2. Copy: use the wake line on the right.
3. Paste: paste it into the named AI session.

The guide uses verbs rather than system terminology.

## Queue Filters

The queue has three primary filters:

- Wake-ups
- Decisions
- Diagnostics
- All

### Wake-ups

This is the default filter. It shows only unread messages that have passed the stale-unread threshold.

Wake-up items are sorted oldest first so the longest-overdue message appears at the top.

### Decisions

This filter isolates items that require Darrin decision or review. It prevents approval-related work from being buried among wake-ups.

### All

This shows the complete action queue for broader review.

### Diagnostics

This view transforms route, diagnostics, and git health into queue-style review items. It answers:

- are mailboxes being checked?
- is the watcher held?
- are diagnostics quiet?
- is git clean?

Diagnostic items are read-only and carry no wake line.

## Wake-up Detection

The backend promotes unread messages to wake candidates after:

```text
cockpit_state.stale_unread_threshold_seconds
```

Current value:

```text
60 seconds
```

This threshold is exposed through the API so the UI does not hardcode or guess the definition of overdue.

Relevant backend field:

```json
"stale_unread_threshold_seconds": 60
```

Relevant schema:

`C:\CODEX PG\CODEX Canonical Specs\CODEX_PAH_COMPACT_COCKPIT_READONLY_SCHEMA_v1.md`

## Action Queue Items

Queue rows are designed for quick scanning.

Each row includes:

- item type tag, such as `Needs wake-up`
- title
- human-readable age and target AI
- thread id or path hint

Example summary:

```text
Overdue 34m - paste wake line into claude-code.
```

Raw seconds are intentionally converted into human-readable time such as:

- `45s`
- `3m`
- `2h 14m`
- `1d 3h`

## Selected Item Details

When a queue item is selected, the right panel shows:

- title
- summary
- primary action
- secondary action
- thread id
- write behavior

The design goal is to make the selected item self-contained. Darrin should not have to cross-reference the row, the raw message, and the mailbox folder to know what to do.

## Wake Line

The wake line is the safest current wake mechanism.

Example:

```text
Read CLAUDE-20260428-AM-SCREEN-B-CC-ACK and reply to CODEX.
```

The app can copy the wake line to the clipboard, but Darrin remains the bridge who pastes it into the appropriate AI session.

### Copy feedback

After clicking `Copy wake line`, the button briefly changes to:

```text
Copied
```

This confirms that the action happened without adding a noisy notification.

## How To Use This Item

The selected item includes step-by-step guidance.

For wake-up items:

1. Open or switch to the named AI.
2. Click Copy wake line.
3. Paste the line into that AI and send it.
4. After the AI responds, click Refresh here.

For decision items:

1. Read the summary and message path.
2. Open the message if more context is needed.
3. Decide, defer, or ask Codex to handle the follow-up.

This section is intentionally repeated per selected item. It reduces cognitive load and avoids forcing Darrin to memorize the workflow.

## Mailbox Checks

The selected item panel includes a Mailbox Checks box.

Each route row shows:

- route name
- route status
- hold reason when present
- last checked time

Routes currently include:

- Codex -> Claude Desktop
- Codex -> Claude Code
- Claude Desktop -> Codex
- Watcher

The route check table answers:

> When did PAH last inspect each mailbox route?

This is separate from message age. A message can be old even if the mailbox was checked recently.

## Summary Metrics

The summary strip shows three compact cards:

- Needs wake
- Unread
- Diagnostics

These metrics are visible at a glance but do not dominate the page.

### Needs wake

Count of unread messages older than the stale threshold.

### Unread

All unread mailbox messages, including non-stale messages.

### Diagnostics

Warn/fail count from PAH diagnostics.

## Diagnostics

Diagnostics are surfaced in the footer and summary strip.

The console uses diagnostics as reassurance unless there is a warning or failure. This keeps the main screen focused on human action rather than system internals.

## Read-only Safety Model

The console exposes:

- `cockpit_state.read_only: true`
- disabled compose/send actions
- read-only action metadata
- direct wake disabled
- watcher held until permission

Current explicit boundary:

```text
No direct wake.
No watcher startup without standing read permission.
No compose/send in read-only v1.
No permission grant from a single click.
```

## Current Limitations

The app currently does not:

- directly wake Claude Desktop, Claude Code, or Codex
- send messages
- compose messages
- grant standing permissions
- start the watcher
- mark messages read through shell-origin requests without write-token/origin validation

The web UI has controls for some local actions, but write-protected endpoints enforce safety checks.

## Research Rationale

### Action-centric dashboards

The console follows action-centric dashboard principles:

- tailor the screen to the user goal
- include only essential information
- organize around the most actionable insight
- keep important metrics visible at a glance

Source:

`https://www.qualtrics.com/articles/customer-experience/action-centric-dashboard-design/`

### Message design

The app uses section-level messages and inline guidance rather than generic alerts. The goal is to guide Darrin through the task with copy that says what happened and what to do next.

Source:

`https://atlassian.design/foundations/content/designing-messages/`

### Navigation and task focus

The layout emphasizes important destinations and de-emphasizes less important content. Filters act as task destinations rather than generic data categories.

Source:

`https://m1.material.io/patterns/navigation.html`

### Recognition over recall

The interface keeps required information visible:

- what needs attention
- who to wake
- how overdue it is
- what to paste
- where to paste it
- when mailboxes were checked

This follows the recognition-over-recall heuristic: reduce memory load by making actions and options visible.

Source:

`https://media.nngroup.com/media/articles/attachments/Heuristic_6_A4_compressed.pdf`

## Implementation Files

Primary UI:

```text
C:\CODEX PG\CODEX Agent Hub\CODEX_agent_hub_ui.html
```

Backend payload:

```text
C:\CODEX PG\CODEX Agent Hub\CODEX_agent_hub.py
```

Schema:

```text
C:\CODEX PG\CODEX Canonical Specs\CODEX_PAH_COMPACT_COCKPIT_READONLY_SCHEMA_v1.md
```

Smoke tests:

```text
C:\CODEX PG\CODEX Agent Hub\CODEX_run_smoke_tests.py
```

## Design Feature Checklist

- [x] Screen-fit three-panel layout
- [x] Plain-language top system state
- [x] Agent status tiles with labeled counts
- [x] Start Here guidance card
- [x] Three-step Pick -> Copy -> Paste workflow
- [x] Wake-up breakdown by target AI
- [x] Clickable agent-specific wake-up filters
- [x] Wake-ups filter
- [x] Decisions filter
- [x] Diagnostics filter
- [x] All actions filter
- [x] Oldest-overdue-first wake sorting
- [x] Human-readable overdue ages
- [x] Selected-item detail panel
- [x] Wake line copy surface
- [x] Copy feedback
- [x] Per-item usage instructions
- [x] Mailbox check times
- [x] Route status and hold reason display
- [x] Diagnostic route/git/check suite view
- [x] Summary metrics
- [x] Quiet diagnostics footer
- [x] Read-only compose/send safety
- [x] Direct wake disabled
- [x] Stale-unread threshold exposed by API
- [x] Schema updated for stale-unread threshold

## Recommended Next Enhancements

### 1. Guided Empty State

When no wake-ups exist, show a calm success state:

```text
No overdue wake-ups. All agents are caught up.
```

Include the last mailbox check time in the same empty state.

### 2. Read/Unread UX Clarification

Separate "unread" from "unseen" semantics if PAH later distinguishes:

- mailbox item read state
- notification seen state
- action handled state

### 3. Decision Review Panel

Decision items should eventually render structured scope text first:

- path
- read frequency
- writes
- will not do
- confirmation requirement

### 4. Safer Mark Read

Keep the write-token/origin guard, but make UI failures visible if Mark Read is rejected.

### 5. Route Health Detail Drawer

Add a small route detail view that expands from Mailbox Checks:

- source path
- destination path
- last checked
- latency
- hold reason
- latest error

### 6. Schema Cleanup From CC Review

Address remaining CC schema review items:

- clarify or remove ambiguous `route_outside_pg` action
- resolve single-source-of-truth concerns around wake labels and action queue titles
- enumerate severity/filter/density/action values
- clarify top-level `wake` vs per-item `wake_line`
- add schema-version compatibility rules

## Operating Summary

Use the PAH Action Console like this:

1. Open `http://127.0.0.1:8765/`.
2. Start in the center panel.
3. Use the default Wake-ups filter.
4. Click the first item.
5. Read the right panel.
6. Copy the wake line.
7. Paste it into the named AI.
8. Refresh after the AI responds.

If the queue feels overwhelming, use the mini pills to understand which agent has the largest backlog, then work oldest-first.
