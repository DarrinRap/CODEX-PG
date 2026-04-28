# CODEX PAH Compact Cockpit Design Notes v1

Mockup:

`C:\CODEX PG\CODEX Visual Mockups\CODEX_pah_compact_cockpit_mockup_v1.html`

Read-only schema:

`C:\CODEX PG\CODEX Canonical Specs\CODEX_PAH_COMPACT_COCKPIT_READONLY_SCHEMA_v1.md`

## Product Intent

PAH should feel like a desktop control cockpit, not a scrolling status webpage. The default screen should answer three questions in under five seconds:

- Who needs attention?
- What is the single next decision or action?
- Which route or mailbox is involved?

## Layout Contract

- No page-level vertical scrolling in normal desktop use.
- Fixed top bar for identity, global state, search, refresh, and compose.
- Left rail is agent state only: Codex, Claude Desktop, Claude Code, Darrin.
- Center left pane is the operational feed with filters and density controls.
- Center right pane is the selected thread/action detail.
- Right rail is the action queue: Darrin decisions, route health, and CC wake line.
- Bottom bar is a stable command/safety bar that always shows the destination path before send.
- V1 bottom bar is read-only: validate and backup can be active, compose/send remain disabled.

## UX Principles

- Prefer one selected thread with clear next action over exposing every object at once.
- Keep global counts visible, but make them secondary to action state.
- Route health should be glanceable: pass, held, failed, untested.
- Safety boundaries must be visible where actions happen, not buried in docs.
- CC wake is copy-ready only; no headless wake or window automation.
- Compose must preview the destination folder before a message can be sent.
- Archive and explorer views are read-only unless a separate explicit action mode is active.
- Route summary chips and route panel must derive from one source of truth.
- Standing permission decisions open scope review; they are never one-click approves.
- Agent rail counts must include labels such as `open`, `unread`, `queued`, or `decision`.
- Pulsing status dots are reserved for active agents only.

## PG Visual Vocabulary

- Canvas: `#14141f`
- Pane: `#1a1a2e`
- Raised pane: `#22223a`
- Border: `#2a2a3e`
- Text: `#e0ddd5`
- Muted text: `#888888`
- Active accent: `#e8a87c`
- Pass: `#7fb069`
- Warning: `#d7b86b`
- Error: `#e74c3c`

Controls stay compact with low-radius corners and muted borders. Peach is reserved for active selection or high-value actions, not general decoration.

## Live App Conversion Notes

- Replace the current stacked panel page with a viewport grid.
- Move long lists into internal virtualized panes.
- Feed items should cap at one-line title and one-line metadata by default.
- The selected thread detail should render structured summaries before raw Markdown.
- Raw message body belongs behind an `Open Message` action, not in the default cockpit.
- Preserve all current APIs; this mockup is a presentation layer redesign.
- First implementation slice should be read-only: agent cards, feed, selected thread, decision queue, route health, wake preview.
- Compose/send can follow after the read-only cockpit is stable.
- Do not ship undefined Plan/Review modes in the first live slice.
- Add `as_of_iso` refresh time to the live payload and visible cockpit.
- Use the schema file as the implementation contract before touching live UI code.
