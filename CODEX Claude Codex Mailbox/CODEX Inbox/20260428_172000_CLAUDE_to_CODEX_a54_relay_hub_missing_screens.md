---
schema_version: 1
id: CLAUDE-20260428-172000-a54-relay-hub-missing-screens
thread_id: A54-RELAY-HUB-MISSING-SCREENS
created_at: '2026-04-28T17:20:00-07:00'
from: claude_desktop
to: codex
type: dispatch
priority: high
status: shipped
thread_status: active
action_owner: codex
requires_darrin_decision: false
approval_boundary: darrin_go_required_before_implementation
tier: extra_high
---

# Claude Desktop -> Codex: A54 — Relay Hub Missing Screens

## Context

A52 delivered 5 Relay hub screens (By Tester, Sent, Templates, Duplicate
detection, Tester My Reports). A53 delivered 9 tester setup screens.

The following screens have NO mockup anywhere in the design system:

1. **Developer hub — All Reports tab** (the primary landing screen Darrin sees
   every day — the most important screen in the entire Relay module)
2. **Report detail panel** — transcript, screenshots, capture card, compose entry
3. **Archive** — closed/resolved/won't-fix reports
4. **Empty states** — for All Reports (no reports yet), Updates (no updates),
   Sent (nothing sent yet)
5. **Full navigation flow diagram** — how all Relay screens connect

This is A54. Deliver all of the above in a single HTML file.

---

## Mandatory reading — ALL before writing one line of HTML

1. `C:\panda-gallery\workflows\design\PG_DESIGN_BIBLE_v1.md` — full read
2. `C:\CODEX PG\CODEX Canonical Specs\RELAY_SPEC_v0.2.md` — full read
3. `C:\panda-gallery\workflows\design\RELAY_SCREEN_C_DESIGN_v1.md` — full read
4. `C:\panda-gallery\workflows\design\pg_general_mockups\relay_module_v1.html`
   — visual baseline, study before writing
5. All delivered A52 mockups in `C:\panda-gallery\workflows\design\pg_general_mockups\`
   matching `relay_*` — study for consistency
6. `C:\panda-gallery\workflows\design\pg_general_mockups\relay_tester_setup_v1.html`
   — A53 delivered mockup, study for shell grammar consistency

---

## Deliverable

`C:\panda-gallery\workflows\design\pg_general_mockups\relay_hub_missing_v1.html`

Single self-contained HTML file. 1280×800px design viewport for full-screen
renders. All Bible tokens only. No external dependencies.

---

## Screen 1 — Developer Hub: All Reports tab (PRIMARY SCREEN)

This is the screen Darrin lands on every time he opens Relay. It must be
exceptional. It is the nerve center of the entire Relay module.

**State to render:** 3 reports in the list. One selected and open in the
right panel. One has a DUPLICATE? badge. One is unread.

### Left rail (260px fixed)

Header row:
- `RELAY` module label (peach caps, Bible §6.22)
- View toggle: `≡ All Reports` (active) | `⊞ By Tester` (inactive)
- `⚙ Settings` button (`.vc-btn`)
- `1px --border-soft` separator below

Tab strip below header:
- `All Reports (2)` — active, unread badge showing 2
- `By Tester`
- `Sent`
- `Templates`

Search + filter bar below tabs:
- Search input: `--canvas` bg, `1px --border`, `4px` radius, `12px` font,
  placeholder "Search reports…" in `--text-dim`
- Filter chip row: `All` (active) · `Unread` · `Pending` · `Captured`

Report list rows (3 reports, standard report-list-row grammar from A52 spec):

Row 1 — **Selected, In Progress:**
- Avatar: `RC` (Rebecca Chen), `--accent` bg
- Title: "Single-click image viewer fails after patient switch"
- `IN PROGRESS` badge (amber)
- Unread dot: hidden (already read)
- Timestamp: `2:30 PM`
- No DUPLICATE badge

Row 2 — **Unread, Pending, DUPLICATE flagged:**
- Avatar: `MS` (Maria Santos), `--pane-raised` bg
- Title: "Image viewer loses focus on patient switch"
- `PENDING` badge (peach)
- Unread dot: visible (`--accent`, 6px)
- `DUPLICATE? 84%` badge (`--warn`)
- Timestamp: `1:45 PM`

Row 3 — **Read, Fixed:**
- Avatar: `RC` (Rebecca Chen), `--pane-raised` bg
- Title: "Toolbar drag handle unresponsive on Windows"
- `FIXED` badge (green)
- Timestamp: `Yesterday`

### Right panel (1fr)

Show the full detail panel for Row 1 (Rebecca's selected report).

**Report header (48px):**
- Avatar `RC` (accent bg) + title text + `IN PROGRESS` badge
- Meta strip: `Rebecca Chen · via Relay · 2026-04-27 2:30 PM · 3 screenshots · 0:42 audio`
  (all in `--text-muted` `11px` mono)

**Horizontal stepper (developer, 4 steps):**
```
① Received ━━▶ ② Review ━━▶ ③ Capture (optional) ━━▶ ④ Respond
```
Step 1: Complete (green ✓). Step 2: Active (peach). Steps 3+4: Pending.

**Status pane (32px, always visible):**
`Report received. Review transcript and screenshots, then click ✦ Capture to BUGS.md.`

**Evidence block (collapsed):**
`EVIDENCE  📎 Screenshots · 3  |  🎙 Transcript · 0:42  ▾ show`
(matches A48 evidence block grammar exactly)

**Capture card:**
Section head: `BUGS.MD DRAFT` (peach caps) + `auto-generated` (dim mono right)
Draft preview (first 5 lines, truncated):
```
**Bug #143:** Single-click image viewer fails after patient switch
**Reporter:** Rebecca Chen (via Relay)
**Severity:** Medium
**Status:** OPEN
**Reproduce:** Switch patient while image viewer is open…
```
Primary button: `✦ Capture to BUGS.md` (`.gbtn.primary`, full width)

**Footer action bar (44px, `--chrome` bg, `1px --border-soft` top):**
Left: `⋯ More` (`.gbtn`). Right: `✦ Send update` (`.gbtn.primary`).

---

## Screen 2 — Report detail: Transcript expanded

Same report as Screen 1 but the evidence block is expanded, showing:

**Filmstrip** (3 image tiles, 180×120px each, `10px` gap):
- Tile 1: `001_buttons.png` — placeholder gradient (`--canvas` bg, `--border` border)
- Tile 2: `002_panel.png`
- Tile 3: `003_viewer.png`
- No `+ add` tile (post-triage locked state, matches A22 spec §D8)

**Transcript section** below filmstrip:
- Section head: `TRANSCRIPT · Rebecca Chen · 0:42` (peach caps)
- Inline preview (italic, `--text-muted`, 12px, 3 lines):
  *"So the issue I'm seeing is that when I switch patients mid-session, the
  image viewer sort of loses focus — it stops responding to single clicks.
  I have to double-click everything after that…"*
- `▶ Play audio` (`.gbtn`, 24px) + `↗ Expand` (`.gbtn`, 24px) side by side

---

## Screen 3 — Archive tab

A fourth tab in the developer hub: `Archive`. Shows resolved/closed reports.

**Tab strip updated:** `All Reports (2)` · `By Tester` · `Sent` · `Templates` · `Archive`

**Archive list (left rail):**
3 archived rows. Each row visually distinct from active reports:
- Row background: `--canvas` (one tone darker than `--pane`)
- All text: `--text-muted` (muted, not primary)
- Status badges use dim variants: `FIXED` (muted green), `WON'T FIX` (dim)
- Archive date shown right-aligned: `Archived Apr 27` (`10px` mono `--text-dim`)

Rows:
1. `RC` · "Submit button unresponsive in Chrome" · `FIXED` · `Archived Apr 27`
2. `MS` · "Toolbar overlaps on 1366px screens" · `WON'T FIX` · `Archived Apr 26`
3. `RC` · "Audio playback fails on first load" · `FIXED` · `Archived Apr 25`

**Right panel — archived report selected (Row 1):**
Same anatomy as active report detail but:
- Stepper: all 4 steps complete (green ✓)
- Status pane: hidden (FIXED state — per A48 OQ1 decision: hide status pane in FIXED state)
- Capture card replaced by: `BUGS.MD ENTRY` section head + `Bug #141 — captured 2026-04-27` in green
- Footer: `↗ Open in Audit Module` (`.gbtn`) only. No `Send update` (report is closed).
- A subtle `ARCHIVED` watermark label in the report header (`--text-dim`, `11px` mono, right-aligned)

---

## Screen 4 — Empty states (3 variants, shown as a panel)

Show all three empty states as a triptych (3 panels side by side, each
representing a different tab in its empty condition).

Use Bible §8 empty-state voice: welcoming, walkthrough, not error-toned.

**Empty state A — All Reports (no reports received yet):**
- Eyebrow: `ALL REPORTS · EMPTY` (mono caps, `--text-dim`)
- Hero: "No reports yet."
- Sub: "When Rebecca sends her first report, it will appear here."
- No action button (Darrin can't create reports — they come from testers)
- Keyboard hint: `⚙ Settings` to manage testers

**Empty state B — Updates (tester view, no updates received):**
- Eyebrow: `UPDATES · EMPTY`
- Hero: "No updates yet."
- Sub: "When Darrin sends a status update, it will appear here."
- No action button

**Empty state C — Sent (nothing sent yet):**
- Eyebrow: `SENT · EMPTY`
- Hero: "Nothing sent yet."
- Sub: "Status updates you send to testers will appear here."
- No action button

Each empty state panel: `--pane-raised` background, `1px --border` border,
`6px` radius, `xl` padding (`24px`). Center-aligned content.

---

## Screen 5 — Full navigation flow diagram

A visual map showing how all Relay screens connect. Not a mockup of a screen —
a diagram showing the user journey.

Show as a flow diagram rendered in PG dark palette:

**Developer path (left column):**
```
Open Relay
    ↓
All Reports hub
    ↓ (select report)
Report detail
    ↓ (capture)          ↓ (send update)
BUGS.md captured     Status update sent
    ↓                    ↓
Archive              Sent tab
```

**Tester path (right column):**
```
First open → Setup wizard (3 steps)
    ↓
My Reports hub
    ↓ (new report)
Active Capture (Screen 1)
    ↓
Review & Send (Screen 2)
    ↓
Sent / Track (Step 4)
    ↓ (receives update)
Updates tab
```

**Cross-path connections (dotted lines between columns):**
- Tester sends report → appears in Developer All Reports
- Developer sends update → appears in Tester Updates tab
- Developer captures → creates Bug in AM (link to AM)

Style the diagram using PG tokens: nodes are `--pane-raised` boxes with
`1px --border` borders, `--text` labels, `--accent` for primary action paths,
`--text-dim` for supporting paths, `--border-soft` for dotted cross-connections.
The diagram must be readable at a glance — not cluttered.

---

## Design constraints (identical to A52/A53)

All Bible §10 non-negotiables. All hex values from token table only.
One `.gbtn.primary` per screen maximum. Mono for data only.
Report-list-row grammar must match A52 exactly.
Evidence block grammar must match A48/A53 exactly.
Section heads: peach caps, `11px`, `700`, `1.2px` letter-spacing.
No decorative elements. No off-palette colors. No designer notes in HTML.

---

## Format

Q&A format per screen (same structure as A53):
1. Screen title and number
2. The UX question it answers
3. Full-screen render (1280×800px)
4. UX analysis block (what decision it makes, single obvious action, failure paths)
5. New-user / Darrin-user test verdict

---

## Tier: Extra-High

5 distinct screens, navigation flow diagram, empty state triptych, consistency
with A52+A53+relay_module_v1. Full Bible compliance required.

---

## Reply format

Write to `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\`:
- Confirmation all 6 source files read
- Path to deliverable
- Bible compliance notes
- Any open questions for Darrin
- Your assessment: does the All Reports screen give Darrin everything he needs
  at a glance without hunting?

Do NOT commit. Darrin reviews before implementation.

-- Claude Desktop
