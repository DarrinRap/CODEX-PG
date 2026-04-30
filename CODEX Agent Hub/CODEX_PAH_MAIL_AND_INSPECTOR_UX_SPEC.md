# PAH Mail and Inspector UX Spec

Status: active product and implementation spec
Last updated: 2026-04-30 07:47 -07:00
Audience: Codex, Claude Desktop, Claude Code, and future PAH maintainers
Primary user: Darrin

## Purpose

This document is the durable design reference for turning PANDA Agent Hub (PAH) into a clear, fast, mail-first user console.

Darrin's stated need on 2026-04-30:

> I need a simple way to see my mail and respond to it. I was hoping that PAH would be that way but the interface is beyond confusing and limiting.

The current PAH cockpit has valuable machinery, but it exposes too much of that machinery at once. The target product is not "a dashboard full of internal state." The target product is:

1. Open PAH.
2. See what mail needs attention.
3. Read the selected message without hunting through folders.
4. Reply or mark handled from the same surface.
5. Use Inspector only when system health needs review.

This spec treats "UC" as "user console": the user-facing command center for reading, replying, verifying health, and coordinating with AI agents.

## Current Screenshot Evidence

Screenshots captured from live PAH at `http://127.0.0.1:8765/` on 2026-04-30.

Storage folder:

```text
C:\CODEX PG\CODEX Agent Hub\CODEX reports\CODEX_pah_ux_spec_20260430\screenshots
```

### Current Cockpit

![PAH cockpit](CODEX%20reports/CODEX_pah_ux_spec_20260430/screenshots/01_pah_cockpit.png)

Observed issue: the cockpit exposes participants, steward state, mailbox cards, filters, queue detail, wake lines, routes, sessions, diagnostics, cleanup controls, and git state in the first viewport. This is powerful but cognitively expensive. It does not feel like "read mail and reply."

### Simple Mail Surface

![PAH simple mail](CODEX%20reports/CODEX_pah_ux_spec_20260430/screenshots/02_pah_simple_mail.png)

Current direction: a full-screen Mail surface with a message list, reader, and reply box. This is the right conceptual direction. It still needs polish before it becomes the default landing experience.

### Inspector Overlay

![PAH inspector](CODEX%20reports/CODEX_pah_ux_spec_20260430/screenshots/03_pah_inspector.png)

Observed value: Inspector has the right role as an evidence surface. It needs a clearer hierarchy between "overall health," "actionable warning," "evidence," and "raw report."

## Product North Star

PAH should feel like a dependable local mailroom, not an engineering incident console by default.

The first screen should answer:

- What mail needs me?
- What is unread?
- Who sent it?
- What thread is this part of?
- What should I do next?
- Can I reply right here?
- Is PAH itself trustworthy right now?

Everything else is secondary.

## Primary Modes

PAH should have three top-level modes.

### 1. Mail

Default landing surface. Optimized for reading and replying.

Mail owns:

- Inbox filtering
- Thread/message reading
- Reply compose
- Read/unread state
- Needs-me triage
- Agent sender/recipient clarity
- Search
- Safe open-file fallback

### 2. Inspector

Health and reliability evidence. Optimized for trust and debugging.

Inspector owns:

- Overall PAH health
- Pass/warn/fail counts
- Freshness of evidence
- Route health
- Mailroom canary status
- Backlog and stale-unread warnings
- Server/API health
- Actionable remediation list
- Raw report only as a secondary evidence drawer

### 3. Advanced

The current cockpit and operational panels. Optimized for agents and advanced troubleshooting.

Advanced owns:

- Participant cards
- Work board
- Wake-line bridge
- Detailed diagnostics
- Cleanup/archive controls
- Agent progress internals
- Git and backup status
- Adapter and approval details

Advanced must remain available, but it must not be the first experience for Darrin.

## Information Architecture

Recommended top navigation:

```text
Mail | Inspector | Advanced
```

The top bar should always show:

- PAH status dot
- Last refresh time
- Unread count
- Needs-me count
- Refresh button
- Optional auto-refresh toggle

The top bar should not show destructive or specialized cleanup controls in the first viewport. Cleanup/archive belongs in Advanced or a secondary menu.

## Mail Surface Spec

### Layout

Desktop layout:

```text
-------------------------------------------------------------
Top bar: Mail | Inspector | Advanced | status | refresh
-------------------------------------------------------------
Left rail: filters/search/message list | Right: reader/reply
-------------------------------------------------------------
```

Mobile/narrow layout:

```text
Top bar
Filters
Message list
Reader
Reply
```

The user must never need to understand filesystem folders to answer mail.

### Mail Filters

Required filters:

- `Inbox`: messages addressed to Codex/Darrin's current PAH work surface.
- `Unread`: all unread visible messages.
- `Needs Me`: messages whose classifier says Darrin is the action owner or a decision is required.
- `CD`: messages involving Claude Desktop.
- `CC`: messages involving Claude Code.
- `All`: latest visible messages across PAH mailboxes.

Future filters:

- `Urgent`
- `Decisions`
- `Replied`
- `Archived`
- `Search results`

### Message List Row

Each row must show, in this order:

1. Unread indicator.
2. Sender and recipient.
3. Title.
4. One or two line summary.
5. Thread or message ID in small monospace only when useful.
6. Age or received time.
7. Priority/decision badge when present.

Do not show raw paths in the normal row. Raw paths are for the detail/evidence drawer.

### Message List Typography

Bible compliance update from CD on 2026-04-30:

- Filter chip labels such as `Inbox`, `Unread`, `Needs Me`, `CD`, `CC`, and `All` are prose labels. They must use `--font-ui`, not `--font-mono`.
- Message-list subtitles and summaries are prose. They must use `--font-ui`, not `--font-mono`.
- Counts such as `20 shown / 98 unread` are human-readable status copy. They must use `--font-ui`.
- Reserve `--font-mono` in the list only for true precision values: message IDs, file names, path fragments, exact timestamps, version strings, and compact diagnostic evidence.
- If metadata leaks into the row summary, such as `schema_version`, `id: CLAUDE...`, or YAML keys, that is a reader bug. The row should summarize the body, not the frontmatter.

### Reader Header

The reader header must show:

- Title
- Sender -> recipient
- Thread ID
- Message ID
- Received/modified time
- Read state
- Priority

It must have direct controls:

- Read
- Unread
- Open file
- Copy link/path

### Message Body

The body should preserve Markdown readability but avoid raw source noise where possible.

Minimum acceptable current behavior:

- Display full raw Markdown in a readable wrapping pane.
- Use UI font for prose.
- Use monospace only for IDs, paths, timestamps, and code blocks.

Target behavior:

- Render frontmatter as a compact metadata strip.
- Render body Markdown as readable text.
- Collapse frontmatter and raw evidence by default.
- Provide "Raw" toggle for debugging.

### Frontmatter Handling

Bible polish rule from CD on 2026-04-30:

The right reader pane must not dump YAML frontmatter as the primary reading experience.

Required reader order:

1. Subject, large and set in `--font-ui`.
2. One-line meta strip: `from -> to · type · priority · time`.
3. Body content: everything after the closing `---` of the YAML frontmatter.
4. Collapsed details section for frontmatter/raw metadata.

Priority styling:

- If `priority: high`, `type: decision_request`, or the content clearly indicates a decision is needed, the subject may use the peach accent or an adjacent high-priority badge.
- Do not use bright full-panel warning backgrounds for priority.

Frontmatter display:

- Hidden by default.
- Available through a small collapsed control labeled `Show details`, `Frontmatter`, or equivalent.
- Displayed in monospace only inside that details area.
- Must not occupy the first visible body lines of normal mail reading.

Markdown rendering:

- Headings, lists, blockquotes, and code blocks should render as readable Markdown when practical.
- If Markdown rendering is not yet implemented, plain text with preserved line breaks is acceptable only as a temporary fallback.
- Code blocks and raw metadata may use `--font-mono`; prose uses `--font-ui`.

### Reply Composer

The reply composer must be visibly attached to the selected message.

Fields:

- To: route selector, defaulting to the other participant in the selected message.
- Subject: default `Re: original subject`.
- Body: multi-line reply.
- Send button.
- Status line for sending, sent, or error.

Required reply behavior:

- Preserve selected `thread_id`.
- Include original `message_id` in `reply_to`.
- Include original source path in `reply_to` when available.
- Write through PAH's existing `/api/create-message` route.
- Mark the original message read only after send succeeds.
- Write reply tombstone through existing PAH behavior.
- Do not write to `C:\panda-gallery`.

### Compose Field Styling

Bible compliance update from CD on 2026-04-30:

- The compose panel location, docked under the reader pane, is correct.
- The Send button is the primary action and should keep accent peach styling.
- Inputs and textareas must use the PAH input surface token, muted borders, and peach focus affordance.
- Labels such as `To`, `Subject`, and `Reply` are UI labels and must use `--font-ui`.
- Route labels shown to the user should be friendly names, such as `Claude Desktop` and `Claude Code`, not raw route IDs.
- Raw route IDs may appear only in advanced details or debugging evidence.

### Draft Behavior

Target draft rules:

- Draft is per selected message.
- Switching messages must not silently destroy a non-empty draft.
- Before switching away from a dirty draft, either preserve it per-message or warn.
- If send fails, keep draft text.
- After successful send, clear only that message's draft.

Current simple Mail v1 clears draft on message switch. That is acceptable only as an early prototype behavior.

### Read/Unread Behavior

Read/unread is local PAH read state, not filesystem movement.

Rules:

- Marking read writes to `CODEX read_state` via `/api/message-read-state`.
- Marking unread writes the same state with `unread`.
- Read state must be content-hash aware. If message content changes after being read, it becomes unread again.
- Read/unread must not archive or delete the message.

### Reader Action Hierarchy

Bible polish rule from CD on 2026-04-30:

- `Reply` is the primary action for normal mail reading and should remain accent peach.
- `Open` is a rare raw-file fallback. It should be secondary or ghost.
- `Read` and `Unread` must not be two equal-weight buttons.
- Use a single state-aware toggle:
  - If unread: `Mark as read`
  - If read: `Mark as unread`
- The read-state toggle should be neutral/ghost, not primary.
- Avoid three or more visually equal action buttons in the reader header.

### Delete/Archive Behavior

Mail should avoid destructive language.

Recommended labels:

- "Archive" means move out of active view, preserving file.
- "Delete" should be hidden from the Mail default surface unless Darrin explicitly asks for destructive cleanup.
- Bulk cleanup belongs in Advanced.

Any true delete requires explicit user confirmation at action time.

### Search

Search should match:

- Title
- Summary/body preview
- Sender
- Recipient
- Thread ID
- Message ID
- Path, but only for matching, not row display

Search must be instant for normal mailbox sizes.

### Timestamp Formatting

Bible compliance update from CD on 2026-04-30:

Message-list and reader timestamps should follow this display ladder:

- Today: `HH:MM AM/PM`
- Yesterday: `Yesterday HH:MM`
- This week: `Tue HH:MM`
- Older: `MMM DD`, for example `Apr 28`

Rules:

- Use `--font-ui` for human-facing relative time phrases.
- Use `--font-mono` only for exact timestamps in details, logs, and raw evidence.
- The same helper should be used across Mail list rows, reader metadata, and Inspector visible status rows where possible.

### Empty States

Empty states must be plain and actionable:

- Inbox: "No inbox mail."
- Unread: "No unread mail."
- Needs Me: "Nothing waiting on you."
- CD/CC: "No matching mail."
- Search: "No mail matches this search."

Avoid instructional paragraphs in the app.

### Error States

Errors must say what failed and what the user can do:

- Message fetch failed: show Open file fallback.
- Reply send failed: keep draft and show error.
- Refresh failed: keep last loaded data and show last successful refresh time.
- PAH server unhealthy: show Inspector CTA.

## Inspector Spec

### Inspector Purpose

Inspector is the truth surface. It must answer:

- Is PAH healthy right now?
- Is the evidence fresh?
- Which checks failed or warned?
- What should be fixed first?
- What exact evidence supports that conclusion?

Inspector is not the default mail reader.

### Inspector Top Band

The first Inspector viewport must contain:

- Overall status: PASS, WARN, FAIL, or UNKNOWN.
- Generated time and age.
- Pass count.
- Warn count.
- Fail count.
- "Run Inspector" or "Refresh" action.
- "Open report" action.

The status band must be glanceable without reading raw Markdown.

### Inspector Finding Row

Each finding row must show:

- Severity
- Short title
- One-line finding summary
- Evidence source
- Recommended action
- Related endpoint/file/path
- Timestamp or age when relevant

Rows must be sortable or filterable by:

- All
- Fail
- Warn
- Pass

### Inspector Detail Pane

Selecting a finding should expose:

- Full evidence text.
- Raw JSON fragment when useful.
- Related file paths.
- Related endpoint results.
- Last known passing evidence if available.
- Suggested next command or next PAH action.

### Inspector Raw Report

Raw Markdown is secondary.

Rules:

- Raw report remains available.
- Raw report should not dominate the first viewport.
- Raw report is useful for agents, not the primary user experience.

### Required Health Checks

Inspector must cover:

- `/api/health`
- `/api/cockpit`
- `/api/status`
- `/api/tray-status`
- `/api/cc-activity`
- `/api/mailroom-canary`
- Route diagnostics
- Mailbox schema validation
- Read-state availability
- Reply tombstone behavior
- Interaction ledger availability
- Inspector report freshness
- Periodic monitor freshness
- PAH server smoke
- Communication backlog
- Stale unread classifier correctness
- UI screenshot freshness after visual changes

### Inspector Acceptance Rules

Inspector cannot pass merely because endpoints exist.

It must prove:

- Mail can be written in isolation.
- Mail can be fetched.
- Read state can be written.
- Reply tombstones are created for replies.
- Ledger events are written.
- No stale green report is being reused as current health.

## Visual Design Rules

PAH inherits the Panda Gallery visual language already recorded in `CODEX_PAH_RELIABILITY_AND_DESIGN_SPEC.md`.

Required tokens:

```css
--canvas: #14141f;
--chrome: #161625;
--pane: #1a1a2e;
--pane-raised: #22223a;
--pane-selected: #2a2a4e;
--text: #e0ddd5;
--text-muted: #888888;
--text-dim: #555555;
--accent: #e8a87c;
--warn: #f39c12;
--err: #e74c3c;
--ok: #7fb069;
--font-ui: "Segoe UI", "SF Pro", "Noto Sans", system-ui, sans-serif;
--font-mono: "Cascadia Mono", Consolas, monospace;
```

Rules:

- Dark navy surfaces only.
- No pale/cream alert cards.
- No decorative gradient blobs or orbs.
- Use semantic color for status dots, borders, text, and small badges.
- Do not use full bright red/amber/green blocks as panel backgrounds.
- Cards stay 6px radius or below unless the design system changes.
- Text must not overlap or clip at desktop or mobile widths.
- Body copy uses UI font.
- Monospace is reserved for paths, IDs, timestamps, counts, and code.
- Display type is for true page titles only, not compact panels.
- Buttons must have stable dimensions and never resize the layout on hover.

## 2026-04-30 Bible Polish Requirements

CD reviewed Darrin's live Simple Mail screenshot and filed five must-fix design items before commit-go.

These requirements are now part of the durable UX canon:

1. **No mono for prose.** Header counts, filter labels, list subtitles, body prose, labels, and headings use `--font-ui`. Monospace is precision-only.
2. **No raw frontmatter-first reading.** The reader must show subject, meta strip, and message body first. YAML/frontmatter is hidden by default behind details.
3. **Clear action hierarchy.** Reply is primary. Open is secondary. Read/unread is one state-aware neutral toggle.
4. **Compose fields follow the Bible.** Friendly route names, UI-font labels, input surface token, muted borders, peach focus, accent Send.
5. **Consistent time ladder.** Today, Yesterday, weekday, older date formatting as specified above.

What is already working and must be preserved:

- The filter chip bar is the right pattern.
- The selected filter's orange outline is correct.
- The list-reader-reply structure is the right pattern.
- The compose dock belongs under the reader pane.
- Send as accent peach is correct.
- Dark navy surfaces and white-on-dark text are aligned with the Bible.
- Top-bar Mail entry works and should remain prominent.

## Interaction Design Rules

### Default Action

When a message is selected, the default action is read/reply, not wake, archive, cleanup, or diagnostics.

### Keyboard

Mail should support:

- Up/down or J/K: move selection.
- Enter: focus reader or reply.
- R: focus reply box when Mail is open.
- Ctrl+Enter: send reply when reply box is focused.
- Esc: close modal/overlay or leave reply focus.
- Slash: search.

Keyboard support must not conflict with text entry.

### Refresh

Refresh should:

- Preserve selected message if it still exists.
- Preserve non-empty draft.
- Update counts and read state.
- Show last successful refresh time.

Auto-refresh should be optional and visible.

### Loading

Loading states:

- App loading: skeleton or quiet "Loading."
- Message body loading: "Loading message."
- Reply sending: "Sending."
- Inspector running: "Running checks."

No spinner-only states.

## Data Contract

The Mail UI consumes `cockpit.simple_mail`.

Current proposed shape:

```json
{
  "simple_mail": {
    "latest": [],
    "mailboxes": [],
    "agent_mailboxes": {}
  }
}
```

Message item fields used by Mail:

```json
{
  "path": "string",
  "name": "string",
  "modified": "iso-ish string",
  "title": "string",
  "summary": "string",
  "message_id": "string",
  "thread_id": "string",
  "thread_status": "string",
  "status": "string",
  "type": "string",
  "priority": "string",
  "from_agent": "string",
  "to_agent": "string",
  "read_state": "read|unread",
  "unread": true,
  "classifier_state": "string",
  "requires_darrin_decision": false
}
```

Canonical sequencing rule:

- Use `message_id`, `reply_to`, and `CODEX_MAILBOX_LEDGER.md`.
- Do not use filename timestamp or `created_at` as source of truth for ordering.

## Performance Targets

These are product targets, not current guarantees.

Mail:

- Open Mail overlay: p95 under 250 ms after cockpit data is loaded.
- Select cached message: p95 under 100 ms.
- Fetch uncached message body: p95 under 500 ms for normal Markdown files.
- Search/filter 500 messages: p95 under 100 ms.
- Send local mailbox reply: p95 under 150 ms for file write path.

Inspector:

- Open Inspector overlay with cached latest report: p95 under 250 ms.
- Refresh latest Inspector report from disk: p95 under 500 ms.
- Full Inspector run: may be slower, but must show progress and freshness.

PAH:

- Warm `/api/cockpit`: p95 under 300 ms.
- Warm `/api/health`: p95 under 250 ms.
- Mail pickup should feel near-instant.
- Any full dashboard refresh over a few hundred milliseconds is a performance concern to profile.

## Reliability and Safety

Rules:

- Darrin remains approval gate for protected actions, commits, pushes, external services, `C:\panda-gallery` writes, and irreversible operations.
- Codex-authored PAH reports go to `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox`.
- Codex does not write reports to `C:\panda-gallery` unless Darrin explicitly overrides for that dispatch.
- Mail replies must go through PAH mailbox routes, not ad hoc paths.
- Sensitive data must not be written into specs, test fixtures, memory, or mailbox reports.
- Mail UI must not auto-send. The user or acting agent must explicitly press Send.
- Inspector must not hide warnings to make PAH look healthy.

## Implementation Roadmap

### Phase 1: Stabilize Simple Mail

Current v1 exists.

Next work:

- Make Mail the default first screen.
- Rename Advanced cockpit if needed.
- Preserve drafts per message.
- Render frontmatter as metadata instead of raw wall of text.
- Add Ctrl+Enter send.
- Add copied/sent/read state feedback.
- Add visible stale/unhealthy warning if `/api/health` is not OK.
- Make open/reply buttons impossible to miss.

### Phase 2: Thread-Aware Mail

- Group messages by `thread_id`.
- Show thread timeline.
- Latest message selected by default.
- Reply to thread, not only individual file.
- Show sent replies in the timeline.
- Show reply tombstone state.

### Phase 3: Inspector Redesign

- Convert Inspector into a split-pane health console.
- Keep status counts pinned.
- Make fail/warn filters prominent.
- Add "why this matters" only in detail pane.
- Add run timestamp/freshness warnings.
- Add latest screenshot evidence links.

### Phase 4: Performance Harness Integration

- Add latest perf-run tile.
- Show pickup-latency P50/P95/P99.
- Show trend over recent runs.
- Gate PAH "healthy" claim on perf evidence.

### Phase 5: Production Polish

- Mobile QA.
- Accessibility QA.
- Visual regression screenshots.
- Keyboard pass.
- Error injection pass.
- Documentation and CC/CD handoff.

## Verification Gate

Before claiming Mail or Inspector UX work complete, run:

```powershell
python -m py_compile "C:\CODEX PG\CODEX Agent Hub\CODEX_agent_hub.py"
python "C:\CODEX PG\CODEX Agent Hub\CODEX_run_smoke_tests.py"
python "C:\CODEX PG\CODEX Agent Hub\CODEX_pah_inspector.py"
& "C:\CODEX PG\CODEX Agent Hub\CODEX_run_server_smoke.ps1"
```

Also verify live:

- `http://127.0.0.1:8765/` loads.
- Mail opens.
- Message list is populated.
- Message body fetch works.
- Reply dry-run works before real sends.
- Read/unread state works.
- Inspector opens.
- Inspector counts are visible.
- Screenshots captured after visual changes.

## Known Current Gaps

As of the 2026-04-30 screenshot/spec pass:

- Mail exists as overlay, but not yet the default landing surface.
- Drafts are not yet safely preserved per message.
- Message body is raw Markdown, not rendered Markdown.
- Inspector still exposes raw report heavily.
- Server smoke has reported `diagnostics_ok:false`; do not claim full PAH health until diagnosed.
- Live screenshot verification exists for desktop viewport only in this pass.

## CC Collaboration Request

Claude Code should use this spec to help design and implement the top-notch PAH user console.

Suggested CC focus:

1. Review the screenshots and identify the highest-impact simplifications.
2. Propose a Mail-first layout that keeps current functionality but hides nonessential cockpit machinery.
3. Improve the Mail reader/reply flow without breaking existing PAH mailbox protocol.
4. Propose Inspector redesign details that make pass/warn/fail evidence obvious.
5. Keep all work local under `C:\CODEX PG`.
6. Do not write to `C:\panda-gallery` without Darrin's explicit override.
7. Do not commit or push without Darrin's explicit go.

## Durable References

Primary files:

- `C:\CODEX PG\CODEX Agent Hub\CODEX_agent_hub.py`
- `C:\CODEX PG\CODEX Agent Hub\CODEX_agent_hub_ui.html`
- `C:\CODEX PG\CODEX Agent Hub\CODEX_PAH_RELIABILITY_AND_DESIGN_SPEC.md`
- `C:\CODEX PG\CODEX Agent Hub\CODEX_PAH_MAIL_AND_INSPECTOR_UX_SPEC.md`

Screenshot assets:

- `C:\CODEX PG\CODEX Agent Hub\CODEX reports\CODEX_pah_ux_spec_20260430\screenshots\01_pah_cockpit.png`
- `C:\CODEX PG\CODEX Agent Hub\CODEX reports\CODEX_pah_ux_spec_20260430\screenshots\02_pah_simple_mail.png`
- `C:\CODEX PG\CODEX Agent Hub\CODEX reports\CODEX_pah_ux_spec_20260430\screenshots\03_pah_inspector.png`
