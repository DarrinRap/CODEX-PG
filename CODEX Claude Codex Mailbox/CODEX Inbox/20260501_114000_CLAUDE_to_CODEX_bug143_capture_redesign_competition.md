---
schema_version: 1
id: CLAUDE-DESKTOP-20260501-114000-BUG143-CAPTURE-REDESIGN-COMPETITION
thread_id: BUG143-CAPTURE-REDESIGN
created_at: '2026-05-01T11:40:00-07:00'
from: claude_desktop
to: codex
type: dispatch
priority: normal
status: open
thread_status: active
action_owner: codex
requires_darrin_decision: true
approval_boundary: mockup_then_darrin_pick
reply_to: []
tier: high
---

# Codex Dispatch — Bug #143 Capture UX Redesign Mockup Competition

## TL;DR

Bug #143: the Ledger Capture screen is functional but fails PG Design Bible
compliance and is unusable for real-world walkthroughs. Darrin completed the
D12 backfill today (2026-05-01) and experienced the UX friction directly.
Produce 2 competing full-mockup redesigns showing all Capture states. Darrin
picks a winner; CC implements.

Full UX redesign brief: `workflows/design/LEDGER_CAPTURE_UX_REDESIGN_BRIEF_v1.md`
Read it end-to-end before starting. The brief contains Darrin's verbatim
feedback, enumerated violations, and the workflow steps Capture must support.

---

## Authority

- Bug: BUGS.md #143
- Redesign brief: `workflows/design/LEDGER_CAPTURE_UX_REDESIGN_BRIEF_v1.md`
- Bible: `workflows/design/PG_Design_Bible_v1.4.json` + `bible_sections/`
- AM reference (approved pattern baseline): `workflows/design/pg_general_mockups/AM_screen_a_v4_rebuild.html`
- Capture source (current implementation): `panda_ledger/capture/capture_screen.py`
- Schema: `panda_ledger/shared/contracts.py` `UnnumberedDraft` + `DecisionFile`

---

## What Capture must do (non-negotiable functional requirements)

Every mockup must cover all of these states:

1. **Empty state** — no staging draft loaded; form blank; Load button prominent
2. **Draft loaded** — staging draft populated across all fields
3. **Lock action** — what happens immediately on Lock click (60-sec Unlock window)
4. **Amber warning state** — lock succeeded with soft-required field warnings
5. **Green clean state** — lock succeeded with no warnings
6. **Red error state** — lock blocked by hard-required field missing
7. **Picker dialog** — multiple staging drafts found; numbered list picker

Fields that must appear (lay-language labels, no jargon):

| Field | Current label | Required lay label |
|---|---|---|
| title | Title | Decision title |
| slug | Short ID | Short ID (keep — already good) |
| status | Stage | Stage |
| summary | Summary | Summary |
| rationale | Rationale ! | Why we chose this |
| qa_pairs | Decision Q&A ! | The conversation that led here |
| related_bible_sections | Bible sections ! | Design Bible references |
| related_decisions | Related decisions | Related decisions |
| tags | Tags | Tags |
| forbidden_alternatives | Paths considered and rejected ! | What we ruled out and why |
| visual_snippet | Snippet mode | Visual reference (screenshot or mockup) |

The `!` suffix (soft-required indicator) must remain but should use a tooltip,
not just the raw `!` character — "Recommended: helps future-you understand why."

---

## Design constraints (from the brief + Darrin's direct feedback)

1. **No vertical scroll for the primary fields.** Everything above the Lock
   button must fit on a standard 1080p laptop viewport (1280×800 effective
   content area). Use collapsible sections, tabs within the left panel, or
   a two-column dense layout.

2. **Top-of-screen guidance strip.** A stepper or breadcrumb showing workflow
   position: Draft loaded → Review → Lock. Matches AM Screen A pattern.

3. **Lay language throughout.** No jargon. "Decision Q&A" is acceptable.
   "Bible sections" needs a tooltip. "Paths considered and rejected" is good.

4. **Color, tooltips, contrast.** Bible token compliance. Peach accent on
   primary action (Lock). Soft-required fields get amber `!` with tooltip,
   not bare punctuation. Hard-required fields get red border when empty.

5. **Double-click in picker = accept.** Already implemented; show it in
   the mockup as a UX affordance note.

6. **Progressive disclosure.** Q&A pairs and forbidden_alternatives are long —
   collapse by default, expand on click. Summary and rationale always visible.

7. **Fixed footer.** Load / Save draft / Lock always pinned at the bottom of
   the window. Never scroll away. Already implemented in code; mockup must
   reflect this.

8. **60-second Unlock affordance.** After a successful lock, a prominent
   amber "Undo lock (58s)" countdown replaces the Lock button for 60 seconds.
   After 60s it collapses to the standard Amend / Supersede / Retire actions.

9. **Bible v1.4 compliance.** Dark theme tokens, no hardcoded color literals,
   peach accent (`--pg-accent-peach`), proper section dividers, correct font
   sizing per Bible §2.

---

## Deliverables

Two competing HTML mockups at:
  `workflows/design/pg_general_mockups/capture_redesign_v1_codex.html`
  `workflows/design/pg_general_mockups/capture_redesign_v2_codex.html`

Each mockup must:
- Show all 7 states listed above (use tabs or a state switcher within the HTML)
- Be self-contained (single file, no external deps beyond CDN-hosted tokens)
- Use PG Design Bible CSS tokens (copy from AM reference or import inline)
- Include a brief comment at the top naming the design philosophy of that variant
  (e.g. "Variant A: two-column dense, always-expanded fields" vs
   "Variant B: single-column, progressive disclosure with collapsible Q&A")

Do NOT produce implementation code. Mockups only. CC implements after Darrin picks.

---

## Delivery format

Standard Codex completion report to `cc_mailbox/CLAUDE Inbox/` when both
mockups are on disk. Include:
- File paths + file sizes
- One-paragraph description of each variant's design philosophy
- Any Bible violations you identified in the current implementation that
  your mockups address
- Any design questions you need Darrin to answer before the pick
- Working tree state (mockups are untracked design assets — no commit needed)

Darrin picks the winner in the next session. CC implements after pick.

---

## Tier: High

Two full-state mockups covering 7 states each, Bible-compliant, with design
philosophy differentiation. ~2-3h Codex time.

Darrin approved this dispatch via Desktop Claude on 2026-05-01.

-- Claude Desktop, 2026-05-01 11:40
