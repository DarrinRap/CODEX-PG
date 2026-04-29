---
Message-ID: CLAUDE-20260428-AM-SCREEN-B-REDESIGN-CODEX
Date: 2026-04-28
From: claude-desktop
To: codex
Type: dispatch
Tier: extra-high
Re: AM Screen B UX redesign mockup
---

# CLAUDE → CODEX: AM Screen B redesign mockup

## Context

The Audit Module Screen B (per-bug detail + triage screen) shipped in v4.57
and received direct user feedback that it is "the most confusing UX I've
seen." Bug #140 is open High-severity. No further AM code changes are
permitted until a winning mockup is approved.

You and CC are each producing ONE independent mockup. Do not collaborate —
we want divergent ideas. Darrin will compare and pick.

## Brief

Read `C:\panda-gallery\workflows\design\AM_UX_REDESIGN_BRIEF_v1.md` in full
before starting. It contains the verbatim user feedback, all design
principles, the list of required flow states, and reference file paths.

Key constraints (do not violate any of these):
- Must match PG v4 design language. Read `PG_DESIGN_BIBLE_v1.md` first.
- Plain language over jargon. Tooltips for industry terms.
- Top-of-screen step guidance (Darrin asked for this explicitly).
- Gray out unavailable actions at each state.
- Persistent status pane — always visible, never lies.
- Beautiful, intuitive, not intimidating. Make the next action obvious.

## Required flow states in the mockup

1. First-time user opens a bug (untriaged, no result, no gaps yet).
2. During the 30-second API call (what changes? what's disabled? progress?).
3. Post-triage with 5 gaps, none resolved.
4. Single gap resolved — show what one resolved gap looks like inline.
5. All gaps resolved — one click from Build Fix Prompt.
6. Reclassify flow (Move → Feature / Amendment) — how does this surface?
7. Status pane — show 3–4 example states (idle / working / success / error).

## Deliverable

Single-file HTML at:
`C:\panda-gallery\workflows\design\pg_general_mockups\AM_screen_b_v2_codex.html`

Dark theme matching PG_DESIGN_BIBLE_v1.md. No JS interactivity required —
static states stacked vertically, each labeled. Every novel UI element gets
a 1–2 sentence caption explaining the design rationale.

## Reference files to read before starting

- `C:\panda-gallery\workflows\design\AM_UX_REDESIGN_BRIEF_v1.md` (primary brief)
- `C:\panda-gallery\workflows\design\PG_DESIGN_BIBLE_v1.md` (color, type, spacing, components)
- `C:\panda-gallery\workflows\design\pg_general_mockups\AM_screen_b_v4_rebuild.html` (current shipped state — context only, not a template)
- `C:\panda-gallery\audit_module\audit_module_window.py` (current implementation — context only)
- `C:\panda-gallery\instruction_pane.py` — skim `_ChecklistRow` and `ChecklistStepView` (canonical PG pattern for actionable side-panel rows)
- Skim 3–4 OPEN bugs in `C:\panda-gallery\BUGS.md` to understand real triage data

## Out of scope

- No Python code. No Qt-specific markup. No BUGS.md changes.
- Screen A and Archive screen — unchanged.
- Triage logic, API contract, BUGS.md format — unchanged.

## Tier

Extra-High. Multi-state design + spec reasoning + grounding in an existing
design language. Do not shortcut.

— Claude Desktop
