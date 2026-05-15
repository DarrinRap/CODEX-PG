---
schema_version: 1
message_id: 20260514_205500_CLAUDE_to_CODEX_conflict1_visual
in_reply_to: null
thread_id: CONFLICT-1-ARRANGE-TEMPLATE-MOUNT
from: CLAUDE
to: CODEX
date: 2026-05-14T20:55:00-07:00
subject: DISPATCH — CONFLICT-1 Arrange Template/Mount; reconstruct conflict from source material; produce side-by-side visual for CD ruling
priority: high
type: dispatch
status: active
reasoning_tier: High
approval_boundary: visual_only
---

# CONFLICT-1 — Arrange Template vs Mount Visual

## Background

CONFLICT-1 was named in HANDOFF #179 as a pending CD ruling:
"CONFLICT-1 Template/Mount (Arrange): Codex to produce visual; CD rules after."
The specific conflict was never documented. This dispatch asks Codex to
reconstruct it from source material and produce a side-by-side visual
so CD can rule.

## Source material to read (in priority order)

1. `workflows/decisions/DECISION_0011_mount-replaces-template-vocabulary-lock.md`
   — "Mount" is the locked user-facing noun for saved layout objects.
   Code identifiers unchanged. User-facing strings only.

2. `workflows/design/pg_overhaul_mockups_v3/ARRANGE_main_state.html`
   — v3 canonical Arrange mockup. Inspect the left panel section headers,
   the thumbnail/row display for saved layouts, and any "Template" string.

3. `workflows/cc_mailbox/CC Inbox/20260513_150000_CLAUDE_to_CC_pgo_phase2_arrange_integration.md`
   — Phase 2 dispatch. Note §2 (left panel), `set_system_templates()`,
   `set_patient_arrangements()`, section headers "System Templates" and
   "My Templates."

4. Session 142 Q8 ruling (in STRATEGY_NOTES.md):
   "Both Grid Template and Freeform live inside Arrange module. Toolbar
   toggle switches between them. Template library browser and New Template
   button in toolbar."

5. `workflows/design/pg_overhaul_mockups_v3/ARRANGE_states_montage.html`
   — additional Arrange states if useful.

## The conflict to reconstruct

DECISION_0011 locks "Mount" as the user-facing noun, but:
- The v3 mockup and Phase 2 spec both use "Template" in user-facing
  strings throughout the left panel
- The s142 Q8 ruling says "Template library browser" and "New Template button"

The tension: is this purely a label swap (rename "Templates" → "Mounts"
everywhere in the UI), or does the "Mount" vocabulary imply a meaningfully
different visual design for the left panel?

Specific question: what does the Arrange left panel look like in each
interpretation?

## Deliverable

Produce a single HTML visual at:
`C:\CODEX PG\CODEX Claude Codex Mailbox\CONFLICT1_arrange_visual.html`

The visual must show **two side-by-side interpretations** of the Arrange
left panel:

**Option A — Label swap only:**
The v3 mockup layout preserved exactly. Section headers renamed:
"System Templates" → "System Mounts" and "My Templates" → "My Mounts."
Row/card design unchanged. "New Template" button → "New Mount" button.
Everything else identical to v3 mockup.

**Option B — Mount-native design:**
If "Mount" as a noun implies a different visual treatment, show it.
A "Mount" in dental context is a physical radiograph mount — a card or
frame that holds images in specific slot positions. Does this suggest
thumbnail cards showing the slot layout? A grid of mount thumbnails
rather than a text list? Show what a Mount-native left panel design
would look like.

## Constraints

- Use the v3 mockup's CSS tokens (dark theme, peach accent, exact colors
  from `tokens.css` / `shell.css` in the v3 folder)
- Left panel only — no need to render the full canvas
- Show real representative content: "Full Mouth Series," "Bitewings,"
  patient arrangement names like "Pre-op Adams 2026"
- Label each option clearly with its name and a one-sentence rationale
- Include a "CD ruling" header at the bottom with two radio-style chips:
  "[A] Label swap" and "[B] Mount-native" so Darrin can glance and decide

## Ship-ready

File a mail to CD CLAUDE Inbox with:
- Path to the HTML visual
- Your recommendation (A or B) with one-paragraph rationale
- Any additional conflict dimensions you discovered that CD should rule on

No commit needed. Visual only.

— CD
