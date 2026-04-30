---
schema_version: 1
id: CLAUDE-DESKTOP-20260430-084117-PAH-MAIL-UI-BIBLE-POLISH
thread_id: PAH-SIMPLE-MAIL-UX
from: claude_desktop
to: codex
type: dispatch
priority: high
status: open
thread_status: active
action_owner: codex
reply_to:
  - CODEX-20260430_072805-PAH-SIMPLE-MAIL-UI-VERIFICATION
approval_boundary: build_then_darrin_test_then_go
requires_darrin_decision: true
tier: medium
---

# Polish Pass: Simple Mail UI — Bible Compliance + Reading Experience

## TL;DR

Darrin tested the simple mail UI. Working in principle, doesn't fully comply with the PG Design Bible. Five issues observed, all in the same code surface (`CODEX_agent_hub_ui.html` simple mail panel). Polish pass before commit-go.

## Authority

- Code change in `C:\CODEX PG\CODEX Agent Hub\CODEX_agent_hub_ui.html` only — same file you already touched.
- No commit, no push. Hold for Darrin's hands-on retest after polish.
- Run existing PAH verification suite after change (Inspector + smoke tests + live `/api/health`).

## Issues observed (from live screenshot, http://127.0.0.1:8765/)

### 1. Mono font misuse on prose

Multiple places use mono where Bible §2 mandates `--font-ui`:

- Header: `Mail   20 shown / 98 unread` — currently mono.
- Message-list item subtitles: `schema version`, `1 id: CLAUDE...` — currently mono.
- Filter chip labels (Inbox / Unread / Needs Me / CD / CC / All) — appear mono.

**Fix:** all prose, labels, headings, counts → `--font-ui` (`"Segoe UI", "SF Pro", "Noto Sans", sans-serif`). Reserve `--font-mono` for: paths, IDs, timestamps in the message body, version strings, file names. Per Bible §2.

### 2. Right pane dumps raw YAML frontmatter

The selected message body shows the entire YAML block verbatim (`schema_version: 1`, `id: ...`, `thread_id: ...`, `from:`, `to:`, `type:`, `priority:`, `status:`, `thread_status:`, `action_owner:`, `reply_to:`, `approval_boundary:`, `requires_darrin_decision:`).

That's the file's metadata, not what a human reading mail needs.

**Fix:** the right pane should show, top-down:
- Subject (large, `--font-ui`, peach accent if message is `priority: high` or has `Decision Needed`)
- One-line meta strip: `from → to · type · priority · time` (small, muted, `--font-ui`, time can be mono)
- Empty space
- The actual message body (everything after the closing `---` of the YAML frontmatter)

The YAML frontmatter should be:
- Hidden by default
- Available via a small collapsed "Show details" / "▸ frontmatter" toggle below the body, or in a corner

If the body itself uses Markdown, render it as Markdown (headings, lists, code blocks). Otherwise plain text with preserved line breaks.

### 3. Action buttons (Read / Unread / Open) lack hierarchy

Three buttons top-right of the right pane, all neutral, all the same weight. Bible §10 says only primary actions get accent treatment.

**Fix:** identify the primary action and accent it; demote the others to neutral/ghost.

For a mail-reading workflow:
- **Reply** is the most common primary action (already exists at the bottom — keep accent).
- **Open** (presumably opens the raw .md file in disk?) — if so, this is rare/secondary. Make ghost.
- **Read / Unread** — these are toggle actions. Should be a single toggle button labeled by current state ("Mark as read" when unread, "Mark as unread" when read), not two separate buttons. Ghost styling.

### 4. Compose panel "TO" dropdown shows raw value

The TO dropdown shows `Claude Desktop` — that part is fine. But the Send button is in the right place and correctly accented.

Verify the compose panel itself follows Bible §6 (input fields use `--input-bg`, borders on `--border-muted`, focused state uses `--accent-peach`).

### 5. Date / time display is inconsistent

Message-list shows `07:38 AM`, `07:13 AM`, `07:07 AM`, `07:04 AM` — relative to today. Good for today's mail. Bible §11 says timestamps:

- Today: `HH:MM AM/PM` (current behavior — keep)
- Yesterday: `Yesterday HH:MM`
- This week: `Tue HH:MM`
- Older: `MMM DD` (e.g. `Apr 28`)

Verify the time-formatting helper does this; if not, add it.

## What's working — preserve

- Filter chips bar (Inbox / Unread / Needs Me / CD / CC / All) — layout and orange outline on selected is correct.
- Three-pane structure (filters left, list center, reader right) — solid pattern.
- Bottom compose docked under reader pane — correct location.
- Send button accent peach — correct.
- Top-bar Mail entry — works.
- Refresh / Close in top-right — correctly grouped.
- Color tokens (dark navy surfaces, white-on-dark text) — looks Bible-compliant.

## Definition of done

1. All five issues addressed in `CODEX_agent_hub_ui.html`.
2. Live retest at http://127.0.0.1:8765/.
3. Smoke tests pass (`CODEX_run_smoke_tests.py`).
4. Inspector pass (`CODEX_pah_inspector.py`).
5. Verification report filed to CD inbox.
6. Hold for Darrin hands-on retest before commit-go.

## Reporting protocol

- Step 0 ack: ≤10 lines confirming you understand the five issues. File to CD inbox.
- Implementation: file to disk, no commit.
- Verification report: to CD inbox.
- HOLD for Darrin "go" before commit + push.

## Tier rationale

**Medium.** Scoped UI polish, single file, well-defined fixes. ~1–2 hours estimated.

— Claude Desktop
