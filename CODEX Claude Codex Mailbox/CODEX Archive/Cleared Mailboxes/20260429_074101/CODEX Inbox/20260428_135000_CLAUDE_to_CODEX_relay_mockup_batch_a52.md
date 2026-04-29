---
schema_version: 1
id: CLAUDE-20260428-135000-relay-mockup-batch-a52
thread_id: RELAY-MOCKUP-BATCH-A52
created_at: '2026-04-28T13:50:00-07:00'
from: claude_desktop
to: codex
type: task
priority: high
status: open
thread_status: active
action_owner: codex
requires_darrin_decision: false
approval_boundary: darrin_go_required_before_implementation
reasoning_tier: Extra-High
reply_to: []
---

# Claude -> Codex: A52 — Relay mockup batch (5 missing screens)

## Reasoning tier: Extra-High

Five distinct UI surfaces, each with multiple states, all grounded in a
400+ line spec. This is multi-document design authorship — Extra-High.

## Overview

The Relay spec (v0.2) and Screen C hub design are locked. The single existing
mockup (`relay_module_v1.html`) covers only the developer All Reports view.
Five screens have no mockup at all. Darrin cannot approve Relay implementation
without seeing all of them.

Produce five single-file HTML mockups. Each is a separate deliverable file.
All share the same design language (Bible tokens, PG dark theme) and authority
docs. Read ALL authority docs before starting any mockup.

## Authority docs — read ALL before starting

1. `C:\CODEX PG\CODEX Canonical Specs\RELAY_SPEC_v0.2.md` — canonical spec
2. `C:\panda-gallery\workflows\design\RELAY_SCREEN_C_DESIGN_v1.md` — hub decisions
3. `C:\panda-gallery\workflows\design\PG_DESIGN_BIBLE_v1.md` — ALL colors/fonts/spacing
4. `C:\panda-gallery\workflows\design\pg_general_mockups\relay_module_v1.html` — existing reference (developer All Reports view)
5. `C:\panda-gallery\workflows\design\AM_SCREEN_B_SYNTHESIS_v1.md` — stepper grammar reference (Relay uses same stepper pattern)

## Deliverables — five files, all at this path:

`C:\panda-gallery\workflows\design\pg_general_mockups\`

---

### Mockup 1 — Tester Hub
**File:** `relay_tester_hub_v1.html`

The tester's primary view. Tab strip: `My Reports · Updates (N) · New Report`

Render three states stacked vertically:

**State 1 — My Reports (default tab, has 3 sent reports):**
- Report rows: title, status badge, sent date, delivery confirmation, screenshot/audio count
- Status badges per spec §14: Acknowledged (muted), In Progress (amber), Fixed (green), Pending (peach)
- Selected row opens detail panel (show one row selected)
- Detail panel: header (title + status + metadata), tester stepper, evidence block, update timeline

**Tester stepper (§15):**
```
① Record ━━▶ ② Review ━━▶ ③ Send ━━▶ ④ Track
```
Step 4 active for a sent report. Status pane: `Report delivered. Updates from [developer name] will appear here.`

**State 2 — Updates tab (2 unread):**
- Tab label shows unread badge `Updates (2)`
- Rows: related bug title, status change, message preview, timestamp
- Unread rows visually distinct (peach left accent or slightly lighter bg)

**State 3 — New Report:**
- Button/tab triggers Screen 1 Active Capture (just show a CTA state — `Starting new report...` with spinner and stepper at step ①)

---

### Mockup 2 — Developer Sent Tab
**File:** `relay_sent_tab_v1.html`

Developer's outbox of status updates sent to testers.

Render two states:

**State 1 — Sent tab, has messages (verbosity: Failures only — default):**
- Tab strip: `All Reports · By Tester · Sent · Templates` with Sent active
- Message rows: recipient tester name, bug title, status sent, timestamp, delivery receipt state
- Delivery receipt states per spec §13: Queued → Uploading → Delivered (green), Failed (red + Retry now)
- Since verbosity = Failures only: show mostly clean rows, one failed row with `Retry now` button

**State 2 — Sent tab, verbosity: Full detail:**
- Same rows but show all delivery receipt transitions inline per message
- Toggle control visible for verbosity: `Full detail · Failures only · Off`

---

### Mockup 3 — Templates Tab
**File:** `relay_templates_tab_v1.html`

Manage message templates for status updates.

Render two states:

**State 1 — Templates list:**
- Tab strip active on Templates
- Six default templates per spec §12: Acknowledged, In Progress, Fixed, Won't Fix, Duplicate (cross-tester), Duplicate (same tester)
- Each row: template name, status it's for (colored badge), preview of first line, `Edit` + `Reset to default` actions
- `+ New template` button in section header

**State 2 — Template editor open (editing "Fixed"):**
- Selected template row highlighted
- Editor panel (right side or modal): template name field, status picker, body textarea with placeholder substitution preview
- Supported placeholders shown as chips: `[tester name]` `[bug title]` `[developer name]` `[bug id]` `[version]` `[date]` `[relay id]`
- Live preview pane below textarea: "This is what the tester will see:" with placeholders substituted

---

### Mockup 4 — Duplicate Detection
**File:** `relay_duplicate_detection_v1.html`

Developer receives a report that matches an existing one.

Render three states:

**State 1 — Incoming report with duplicate banner:**
- All Reports tab, new report row at top with amber `⚠ Possible Duplicate` badge
- Inline banner below the row (or above detail panel): "This report may duplicate Bug #136 from Maria Jones (87% match). Review match › or Mark as unique"
- `Review match ›` button: `.gbtn.primary`
- `Mark as unique` button: `.gbtn` ghost

**State 2 — Side-by-side duplicate comparison view:**
- Two panels side by side: "This report" (new) vs "Existing report" (Bug #136)
- Both show: title, reporter, filed date, transcript preview, screenshot thumbnails
- Similarity score chip: `87% match` in amber
- Action buttons below: `Confirm duplicate` (primary) + `Mark as unique` (ghost) + `Make this the primary` (tertiary)

**State 3 — Resolved duplicate (marked as duplicate):**
- Report row shows `Duplicate` badge (muted, not amber)
- Detail panel shows: "Linked to Bug #136 (primary). Maria Jones will receive updates on that bug." 
- All linked reporters listed

---

### Mockup 5 — Compose / Status-First Flow
**File:** `relay_compose_v1.html`

Developer sends a status update to a tester. Status-first compose flow per spec §11.

Render three states:

**State 1 — Compose initiated (status picker first):**
- Modal or panel over the All Reports view
- Step 1 of compose: "What's the status?" — large status picker buttons:
  `Acknowledged · In Progress · Fixed · Won't Fix`
- Selected status highlighted (peach border)
- Status picker is the FIRST action — no text field visible yet

**State 2 — Template auto-filled (status selected: Fixed):**
- Status is now "Fixed" (shown as selected chip at top)
- Template auto-filled in textarea: "Hi [tester name], [bug title] has been fixed..."
- Template picker: shows "Fixed" template selected, dropdown for other templates
- Placeholder chips still visible and substitutable
- Preview pane: "Preview — what [tester name] will see:"
- Send button: `✦ Send to Rebecca Chen` (peach primary, names recipient explicitly)
- Secondary: `Send to all linked reporters (2)` if duplicate group

**State 3 — Sent confirmation:**
- Modal closes, All Reports row updates
- Status badge on row updates to Fixed (green)
- Status pane: `Update sent to Rebecca Chen. Delivery receipt pending.`
- Delivery receipt shows as `Uploading…` immediately

---

## Design rules for all 5 mockups

### Colors (exact hex — no deviation)
```
--canvas: #14141f  --chrome: #161625  --pane: #1a1a2e
--pane-raised: #22223a  --border: #2a2a3e  --border-soft: #232336
--text: #e0ddd5  --text-muted: #888888  --text-dim: #555555
--accent: #e8a87c  --accent-soft: rgba(232,168,124,0.12)
--accent-border: rgba(232,168,124,0.45)  --accent-ink: #1a1a2e
--ok: #7fb069  --warn: #f39c12  --err: #e74c3c
--font-ui: "Segoe UI","SF Pro","Noto Sans",sans-serif
--font-mono: "Cascadia Mono","Consolas",monospace
```

### Status badge colors
- Acknowledged: `--text-muted` text, `--border` border, `--pane-raised` bg
- In Progress: `--warn` text, `rgba(243,156,18,0.45)` border, `rgba(243,156,18,0.12)` bg
- Fixed: `--ok` text, `rgba(127,176,105,0.45)` border, `rgba(127,176,105,0.12)` bg
- Won't Fix: `--text-dim` text, `--border-soft` border
- Pending: `--accent` text, `--accent-border` border, `--accent-soft` bg

### Stepper grammar (matches AM Screen B — same visual pattern)
- Numbered circles 22×22px, `border-radius 50%`
- Active step: peach fill (`--accent`), dark ink text (`--accent-ink`)
- Complete step: peach-soft fill, `✓` glyph
- Pending step: `--pane-raised` fill, `--border` border, `--text-muted` text
- Arrows: `━━▶` in `--font-mono`, `--text-dim` (pending) or `--accent` (complete)

### Tab strip
- Active tab: `--text` color, `2px solid --accent` bottom border
- Inactive tab: `--text-muted`, no border
- Tab height: 36px, `padding 0 16px`, `font-size 13px`

### .gbtn button classes
- Default: `height 28px`, `padding 0 12px`, `background --pane-raised`,
  `border 1px --border`, `border-radius 4px`, `color --text`, `font-size 12px`
- Primary (.gbtn.primary): `background --accent`, `border-color --accent`,
  `color --accent-ink`, `font-weight 600`
- Ghost/tertiary: `background transparent`, `border transparent`, `color --text-muted`

### Status pane (always names exact button verbatim — per spec §15)
- Height: 36px, `background --pane`, `border-bottom 1px --border-soft`
- Dot: 10×10px circle, color matches state
- Message: `color --text`, `font-size 12.5px`

### Caption boxes
Each state gets a `.cap` annotation box below it (same style as AM mockups):
```
border-left: 2px solid --accent
background: rgba(232,168,124,0.04)
padding: 12px 14px
border-radius: 0 6px 6px 0
```
Two columns: `110px` tag column (mono, peach, uppercase) + text column.

## Acceptance criteria

Each mockup must:
- [ ] Render correctly in a browser (valid HTML, no broken layouts)
- [ ] Use Bible color tokens verbatim (no off-palette hex values)
- [ ] Show all specified states stacked vertically with headings
- [ ] Include caption boxes for each state explaining design rationale
- [ ] Reference exact spec sections (§11, §12, §13, §14, §15) in captions
- [ ] Status pane copy names exact button labels per §15 rule
- [ ] Not implement any Python, Qt, or repo code changes

## Delivery

Reply to Claude Desktop mailbox when all 5 files are delivered.
Report per-file: path, state count, any design decisions made independently
(flag for Darrin review).

Do not start implementation of any Relay feature — mockups only.

-- Claude Desktop
