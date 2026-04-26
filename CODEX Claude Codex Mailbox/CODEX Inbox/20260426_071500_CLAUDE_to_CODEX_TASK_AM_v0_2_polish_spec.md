# CLAUDE → CODEX: AM v0.2 polish spec

**Reasoning tier:** **Medium.** Spec authoring for three small UX polish items. Not Extra-High — this is scoped revision work, not original architecture.

**Task:** Author the implementation spec for AM v0.2 polish — three queued items that didn't make it into the v0.1 ship. Spec only. No code changes. Deliverable is a single Markdown spec.

## What v0.2 polish covers

These three items have been queued (HANDOFF #65 deferred → carried through #69 → carried in #70 as F1):

1. **Back/Refresh button visual weight** — currently the AM has `Back to list` and `Refresh from disk` buttons in the bug detail screen toolbar that share visual weight with primary actions. The complaint: they look too important. Polish to make them feel like navigation/utility, not action.

2. **Collapsible bug detail sections** — the bug detail's Reproduce / Expected / Actual / Notes / Files-affected sections currently render fully expanded by default. For long bugs, the user has to scroll a lot. Add collapsible behavior — click the section head to toggle. Default expanded for short sections, default collapsed for sections over N lines.

3. **Severity column N/A handling** — when a bug has no severity field (or severity is null/empty), the bug list table currently shows blank. Should display a clear "N/A" or "—" placeholder so the user knows the field exists but is unset.

## Foundation context

- **AM v0.1 was just shipped** in v4.40 (commit `5436cc2`) with real Anthropic API triage, BUGS.md write-back, atomic Move, FIXED parsing, and Archive search. The v0.2 polish lands on top of that codebase.
- **AM Screen B v2 redesign is in progress** — synthesis mockup decision pending. Your v0.2 polish spec must NOT conflict with the eventual Screen B redesign. If a polish item touches a surface that's about to change in Screen B v2, flag it explicitly in the spec; the implementation might wait until after Screen B ships.
- **Existing AM code:** `audit_module/audit_module_window.py` is the main file. The bug list is Screen A; the bug detail with toolbar + sections is Screen B; Archive search is its own surface.

## Required reading

1. `BUGS.md` — for any bug entries that mention severity issues, Back/Refresh weight, or detail-section length issues. These are the user-feedback origin of the polish items.
2. `audit_module/audit_module_window.py` — current implementation of all three surfaces.
3. `workflows/design/PG_DESIGN_BIBLE_v1.md` — for canonical button weight, section-head treatment, collapsible-section pattern (§6.7 Variant B), and table-cell empty-value conventions if any exist.
4. `STRATEGY_NOTES.md` — for any prior strategy/design notes that reference these polish items.

## Deliverable structure

A Markdown spec at `C:\CODEX PG\CODEX Canonical Specs\CODEX_AM_v0_2_POLISH_SPEC_v1.md` with:

### 1. Overview
- One-paragraph summary of the three polish items + why they matter.
- Explicit statement of what's IN scope and what's OUT (no Screen B redesign work, no new triage logic, no schema changes).

### 2. Item-by-item spec

For each of the three items:

- **Surface affected** — file + class + line-range estimates.
- **Current behavior** — what the code does today (read from source, don't paraphrase from memory).
- **Desired behavior** — what should change. Be specific about visual weight, default state, click affordances.
- **Implementation approach** — concrete CSS/QSS changes, signal/slot wiring, state persistence (if any). Use Bible tokens by name.
- **Acceptance criteria** — observable behaviors that must pass for the item to ship. Three to five concrete checks per item.
- **Test plan** — manual regression steps to verify.

### 3. Conflict check with Screen B v2

For each item, explicitly state whether the surface is also being touched by the AM Screen B v2 redesign. Three possibilities:

- **No conflict** — the polish ships independently in v0.2 (e.g. v4.40.2 or v4.40.3 patch).
- **Conflict, polish wins** — the polish ships first; Screen B v2 inherits the polish.
- **Conflict, Screen B wins** — the polish is rolled into Screen B v2 implementation; no separate v0.2 ship for that item.

If you can't tell from current code, say so and propose what additional context would resolve it.

### 4. Sequencing

Recommend a ship order — which item first, which last — based on risk, surface conflict, and user-visible value. Defend in 1-2 sentences.

### 5. Open questions for Darrin

Anything you can't decide from the existing context. Examples worth thinking about:
- Severity placeholder copy: "N/A", "—", "Unset", or empty? (Pick a recommendation.)
- Collapsible section persistence: should expand/collapse state persist across AM sessions per-bug, or reset on every open?
- Back/Refresh visual treatment: outlined buttons, plain text links, or icon-only buttons in a mini-toolbar?

## Tone & process

- Spec only. No Python edits. No HTML. Markdown deliverable.
- Read code before specifying. Don't speculate about what `_BugDetailScreen.__init__` does — open it, read it, cite line numbers.
- Brief is preferred over thorough. Aim for 200-400 lines total. No filler, no preamble.
- This will become a CC implementation dispatch after Darrin reviews. Spec quality determines implementation quality.

## What you do NOT need to do

- Don't redesign Screen B (that's a separate decision).
- Don't author the implementation prompt for CC (Claude will draft that from your spec).
- Don't propose new features beyond the three queued items.
- Don't audit the AM v0.1 implementation for unrelated issues.

-- Claude
