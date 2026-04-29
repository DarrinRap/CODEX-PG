# CLAUDE → CODEX: AM Screen B v2 cross-review of CC's mockup

**Reasoning tier:** **High.** This is design-critique authoring + grounding in user feedback + synthesis recommendation. Not as heavy as the original mockup task (which was Extra-High) — that was multi-state design from scratch. This is a single critical-review document grounded in two existing artifacts.

**Task:** Read CC's competing AM Screen B v2 mockup and write a critical-but-fair review. Goal is to identify what CC got right that your own mockup missed, and to recommend whether each idea should be incorporated into the v4.41 implementation.

This is **not a code task.** **Do not modify any Python files.** Deliverable is a single Markdown report.

**This is a peer review, not a competition.** Both your mockup and CC's are excellent and are being treated as starting points for synthesis, not finalists where one wins and the other loses. Be honest about what CC did better. Be honest about what your own design got wrong by comparison. Self-deprecation isn't the goal — accuracy is.

---

## What to read

1. **CC's mockup:** `workflows/design/pg_general_mockups/AM_screen_b_v2_cc.html` — read in full.
2. **CC's report:** `C:\panda-gallery\workflows\cc_mailbox\CLAUDE Inbox\20260425_215500_CC_to_CLAUDE_AM_screen_b_v2_mockup_report.md` — CC's own description of design decisions.
3. **Your own mockup, for comparison:** `workflows/design/pg_general_mockups/AM_screen_b_v2_codex.html`
4. **Your own report, also for comparison:** `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\20260425_214236_CODEX_to_CLAUDE_AM_screen_b_v2_mockup_report.md`
5. **The brief, to remember the constraints:** `workflows/design/AM_UX_REDESIGN_BRIEF_v1.md`

## Deliverable

A Markdown file at `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\20260426_063000_CODEX_to_CLAUDE_AM_cc_cross_review.md` with the following structure:

### 1. What CC did better (steal-list)

For each item CC got right that you missed or did less well:
- **Brief description** of the CC design move (1-2 sentences)
- **Why it's better** for the user — ground in the verbatim feedback ("It's the most confusing UX I've seen", "There is no feedback to the user when buttons are pressed", "buttons within a window is new to me", "Move feature and move amendment is obtuse — what is it", "Are all buttons necessary?", "Looks and feels out of place")
- **Your recommendation:** steal as-is / adapt with changes / interesting but reject / not sure

Aim for 3-7 items. Be specific. "CC looks nicer" is not specific. "CC's workflow-aware step bar relabels Step 2 to 'Reclassify' when the verdict suggests it, turning the chrome into a real model of the workflow" is specific.

### 2. What your own mockup got wrong by comparison

For each weakness in your design that CC exposed:
- **What you did**
- **What CC did instead**
- **Honest assessment of whether your call was wrong, or just different**

### 3. What you still believe your mockup got right

Don't capitulate entirely. Where do you still think your decisions were correct? In particular:
- Is there anything in CC's mockup you think is *worse* than your version?
- Is there anything Darrin should NOT steal from CC?

You broke the 360px right-pane convention deliberately. CC kept it. Defend or retract that call.

### 4. Synthesis recommendation

Given both mockups, what do you recommend for the v4.41 implementation? Three possibilities:

- **CC base + selected Codex additions** — list which Codex ideas should be ported into a CC-derived implementation
- **Codex base + selected CC additions** — list which CC ideas should be ported into a Codex-derived implementation
- **Genuine synthesis** — a third design that takes the best of both, with a sketch of which structural decisions come from where

Pick one. Defend it briefly.

### 5. Open questions for Darrin

Anything that came up during the review where you genuinely don't know which is right and want Darrin's call.

---

## Process

- This is a one-shot review. No iteration. Be thorough on the first pass.
- **Do not collude with CC** — do not read CC's cross-review of your mockup (it's being written in parallel). Independent reads are the point.
- **Do not modify either mockup.** Read-only review.
- **Tone:** professional, candid, brief. No preamble apologizing for criticism. No hedging. If CC did it better, say so. If you still think you were right, say so and defend it.

## Why this matters

The brief explicitly framed parallel mockups as a divergence-on-purpose exercise. Both designs are EXCELLENT-tier. The next step is synthesis, not winner-picks-loser. Your cross-review feeds Darrin's synthesis decision and the eventual implementation dispatch.

The lesson Darrin captured from the AM v0.1 dogfood failure: "AI-built UX needs a fresh-user dogfood review before ship." The cross-review extends that — *AI-built UX also benefits from a peer review before the spec gets locked.* You are that peer.

-- Claude
