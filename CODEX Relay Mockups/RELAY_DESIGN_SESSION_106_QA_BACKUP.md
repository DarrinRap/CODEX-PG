# Relay Design Q&A — Session 106 (2026-04-30)
# Read alongside RELAY_DESIGN_DIRECTION_v1.md before any Relay work.

## What we covered this session

### Q: What is the "developer hub"?
Dropped the jargon. Two screens:
- **Darrin's view** — incoming reports from Rebecca, review + capture + reply
- **Rebecca's view** — her sent reports, status updates from Darrin

### Q: What alternatives exist to the Spark two-pane layout?

Three alternatives evaluated:

**1. Card stack (Linear/Notion-inspired)**
Reports stack vertically as full-width cards. Click a card → expands in place.
- Pro: native to single-tester context, no wasted rail, clean at low volume
- Con: loses "selected report stays open" feel, harder to compare two reports

**2. Focused single-report view (Things/Bear-inspired)**
List → tap → full screen for that report. Back returns to list.
- Pro: maximum space for transcript/screenshots/draft/compose
- Con: no peripheral awareness of other pending reports while inside one

**3. Kanban columns (GitHub Projects-inspired)**
Reports organized in status columns: Pending → In Progress → Fixed. Drag to move.
- Pro: workflow-first, great for multiple testers someday
- Con: overkill for 1 tester, drag-and-drop complex. **CUT.**

### Q: How do we feel about the two-pane design pros/cons?

**The two-pane (Spark) is right for Darrin's view** — for a specific reason:
the left rail provides peripheral awareness. Open Relay and instantly see
"3 pending, 1 in progress, 1 fixed" without clicking anything. That matters
even with one tester. You know at a glance whether Rebecca has been busy.

**The card stack is the real alternative** — cleaner, more modern, scales
fine at low volume. Worth keeping in mind but not pursuing for v1.

**The focused single-report view (HEY model) is right for Rebecca's view.**
Her interaction pattern is always one report at a time. The list is secondary.
She never needs to manage a backlog.

### Locked design decisions this session

**Darrin's view:** Spark-style two-pane.
- Left rail: report list, newest first, status pills, unread dot
- Right panel: full report detail — transcript, screenshots, BUGS.md draft,
  compose slides up from bottom
- One primary button at a time: either "Capture to BUGS.md" OR compose is open
- Compose hidden until "Send update" clicked (keeps panel clean)
- "Capture to BUGS.md" full-width inside the draft card (eye is already there)

**Rebecca's view:** HEY-simple, focused single-report.
- List view (default): her reports as cards, status pill, unread dot, "New report" always visible
- Detail view (on tap): full screen — transcript + screenshots on top, update
  timeline below. Back button returns to list.
- No left rail. No competing tabs. One thing at a time.
- Update timeline: chronological, oldest first, newest marked "New"
- Footer: "Play audio" only — no compose (Rebecca doesn't reply, she tracks)

**Two different interaction models for two different use patterns.**
This matches RELAY_DESIGN_DIRECTION_v1.md: Spark for Darrin, HEY for Rebecca.

### Mockups produced this session

Both are in-chat widget mockups (visual reference only, not HTML files on disk):
- `relay_darrin_view_v2` — Darrin's two-pane view with compose panel
- `relay_rebecca_view_v1` — Rebecca's list view + detail view side by side

### Still Bible-violating in the widget mockups (known, expected)

Widget mockups use the visualizer tool which has its own constraints. Known
violations vs PG Bible:
- Avatar peach bg on all rows (should be muted except selected)
- Section labels not using full §3.3 peach-caps treatment with separators
- Compose status picker uses rectangle chips (should be pills per §6.24)
- Font weights not exactly matching §3.2 scale
- Filmstrip thumbs are placeholder emoji, not §9.1 gradient placeholders

These will be corrected in the CC HTML dispatch. The widget mockups are
for Darrin's layout approval only, not Bible compliance.

### Next steps on Relay

1. Wait for §6.24 to land (CC has the dispatch, order: CLAUDE.md rule 24 first,
   then §6.24 per direction sent this session)
2. Dispatch CC to build two new HTML files:
   - `relay_dev_v2.html` — Darrin's Spark two-pane view
   - `relay_tester_v2.html` — Rebecca's HEY-simple view
   Both are scratch rebuilds. Existing mockups are reference only.
3. Darrin reviews both in browser (§14 live sign-off required)
4. After approval → dropbox_sync.py Phase A dispatch (Relay backbone)

### Tester setup wizard
`relay_tester_setup_v1.html` already exists and was assessed as good.
Keep it. Do not rebuild.
