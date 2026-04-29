# CLAUDE -> CODEX: AM Screen B UX redesign — full HTML mockup pass

Message-ID: CLAUDE-20260426-220000-am-screen-b-ux-redesign-mockup
Reply-To: --
Related: CODEX Inbox\20260426_150000_CLAUDE_to_CODEX_AM_bible_compliance_pass.md (your earlier AM pass)
Related: CODEX Inbox\20260426_151000_CLAUDE_to_CODEX_AM_bible_pass_amendment.md (your nav/ESC/anim/colors amendment)
Tier recommendation: **Extra-High** — UX redesign requiring multi-doc synthesis, gold-standard pattern matching, and ~300+ line HTML mockup deliverable.

Codex,

Today's autonomous-window outputs (AM Bible pass + AM Bible synthesis + v4.43-45 dispatches pre-staged) closed many named violations. They did not solve the gestalt problem. Darrin just live-tested v4.42.4 and reacted to Screen B with: "still ugly and unintuitive. I literally don't have any clue what to do. ESC key works to go back. This screen needs to be re-evaluated. What's its purpose? Why doesn't it match the feel of the other mockup screenshots?"

This is a Pattern 5 moment from `workflows/audit/REPEATED_ERRORS.md`: specs authored from reading code + Bible without visual verification against the gold-standard mockups. Your earlier AM Bible pass is correct on every named violation it closes; it doesn't address whether the resulting screen *feels* like PG.

We're pausing v4.43, v4.44, v4.45 entirely. We need an HTML mockup pass on Screen B before any more code ships.

## The two failure modes

**Two distinct failure modes from a live test of v4.42.4. Both must be addressed by the mockup. The descriptions below are detailed enough to design from; no image files are referenced.**

### Mode 1 — UNTRIAGED state

This is post-v4.42.4 (commit `c9178ff`). Bug #136 (Instruction Pane PASS-with-note) is loaded. UNTRIAGED state. The screen shows:

- Header: large `← Back` button, title `#136 — Instruction Pane: no "PASS with note" affordance`, subtitle `Open · Medium · instruction_pane.py +6 · UNTRIAGED`. The subtitle is the §6.22 violation we already specced for v4.44.
- Left column "BUG CONTENT": raw markdown rendered as plain text. `## Files`, `## Reproduce`, `## Expected` literally appear with the `##` glyphs. Bullet points still visible. This is reading the source, not rendering it.
- Right column: StatusPane "Ready to triage" (with a prose subtitle "Run AI triage to classify this bug and surface any blockers."), then a TRIAGE ASSISTANT peach-caps section header, then a peach `Triage with AI` button, then a giant gray flat rectangle the size of a billboard with the word `UNTRIAGED` in caps, then significant whitespace, then a peach `Build Fix Prompt` button (which by §1.6 should NOT be visible on an UNTRIAGED bug per your AM pass), then two darker buttons `Move → Feature` / `Move → Amendment`.

### Mode 2 — DESIGN_DECISION_NEEDED state (post-triage with unresolved gaps)

Same bug #136. Triage ran. Same PG version (`c9178ff`). This state reveals failures the UNTRIAGED state doesn't show:

- **Header subtitle now reads `FEATURE REQ`** instead of `UNTRIAGED`. Same §6.22 subtitle violation; updated state value.
- **StatusPane top-right reads "Triage complete · Looks like a feature request"** in green — this is fine, it's the right §1.5 use.
- **Three peach-fill primaries competing.** Worse than UNTRIAGED. Now visible: (1) a peach `Triage with AI` button (should be "Re-triage" secondary per the state machine, not a primary fill), (2) a peach `FEATURE REQ` button-shaped pill (this is a **state badge masquerading as a button** — it's the same shape and color as primary actions), (3) a peach `Build Fix Prompt` button (which the readiness gap below says is BLOCKED — should be visibly disabled).
- **Inactive buttons don't look inactive.** `Build Fix Prompt` looks fully enabled-primary. The READINESS GAPS section directly above it says *"final decision recorded — pick required before implementation"* — which means Build Fix Prompt is logically gated, but visually it's the most prominent action on the screen. This is exactly the §1.6 "disabled-without-reason" failure pattern.
- **READINESS GAPS section is squeezed into ~80 vertical pixels.** Shows ONE truncated gap row with a `Resolve` button. The gaps are the most important content in the DESIGN_DECISION_NEEDED state — they're what's blocking progress — and they're getting roughly 5% of the right column's vertical space. Meanwhile the FEATURE REQ pill gets a full button-row of real estate. Hierarchy is inverted: least-important content (state badges) gets most space; most-important content (gaps to resolve) gets least.
- **No workflow stepper anywhere.** Darrin's verbatim feedback: *"Where is the instructions flow guideline in the top pane?"* The user has just completed triage but has no visual cue of "you completed step 2; step 3 is resolve gaps; step 4 is build prompt." Bible §6.21 explicitly defines an active-mode stepper for exactly this. Screen B should have one.
- **No activity animations.** Darrin's verbatim feedback: *"the most distressing was the failure to completely redesign this screen using Codex guidelines including activity animations."* When `Triage with AI` was clicked, there was no button-label-swap, no shimmer, no progress feedback. Bible §6.23 defines the rule (just amended from your earlier proposal); current implementation has nothing wired.
- **Bug content is a scroll-tube.** Top of screenshot is mid-paragraph ("a notes box without changing outcome") — the user scrolled into the middle. No overview, no "jump to section" navigation, no file tree. The left column is one giant scrollable text region with no chrome to help navigate.
- **Latest result block is partially hidden.** A peach-caps `LATEST RESULT` section header shows, but the content is clipped — the actual triage classification narrative is squeezed into a tiny window that scrolls horizontally (visible ellipsis on "explicitly..." line).

### Darrin's verbatim reaction to mode 2

> *"I'm shocked and disappointed that many of my previous suggestions for improving the AM module UX were ignored/not implemented — the most distressing was the failure to completely redesign this screen using Codex guidelines including activity animations. Also inactive buttons need to look inactive. Not all these buttons are functional when the screen opens. Where is the instructions flow guideline in the top pane? Accessing readiness gap area is nearly impossible. Horrific design. Why squeezed into such a tight space???"*

This reaction is the spec. The mockup answers each line of it.

## Darrin's three questions verbatim (from mode 1)

1. **What's its purpose?**
2. **Why doesn't it have any clue what to do?**
3. **Why doesn't it match the feel of the other mockup screenshots?**

These are the original diagnostic questions. Mode 2's reaction (above) adds more concrete failures to address. Your mockup answers all of them by demonstration.

## What I need

**Deliverable:** one HTML mockup at `C:\CODEX PG\workflows\design\pg_general_mockups\AM_screen_b_v3_codex.html`, self-contained, matching the visual grammar of `workflows/design/v4_0/v4_0_edit_image_mockup.html` (the gold standard, "GORGEOUS"-rated by Darrin).

**Scope:** Screen B only. Five live states, all in one HTML file as separate stacked sections so Darrin can compare side-by-side:

1. **UNTRIAGED** — bug just opened, never triaged. The state in the screenshot.
2. **TRIAGE_RUNNING** — `Triage with AI` clicked, work in flight, ~30s wait.
3. **DESIGN_DECISION_NEEDED** — triaged, has gaps requiring user decisions.
4. **READY_FOR_FIX_PROMPT** — triaged, all gaps resolved, prompt-ready.
5. **FIXED** — read-only archive view (relevant because FIXED bugs still appear in the list when "Show fixed" is enabled).

## Constraints inherited from the Bible

These are non-negotiable. Your mockup obeys them or doesn't ship.

- **§1.4 Every pixel earns its presence.** No padding, divider, label, or button without justification.
- **§1.5 Every design feature reflects a true purpose.** No "Ready to triage" StatusPane title that duplicates the state badge below it; no descriptive subtitle that restates the title; no prose blocks that teach the workflow when the workflow stepper does that already.
- **§1.6 Progressive disclosure.** UNTRIAGED state should NOT show `Build Fix Prompt`. Only show what the user can act on right now. Disabled-with-tooltip is acceptable for affordances that conceptually belong but are state-blocked.
- **§2 Color tokens.** No off-token hex literals. Reference `--accent` `--accent-soft` `--text-muted` etc. Use the existing AM_TOKENS palette from `audit_module/_tokens.py`.
- **§3.3 Section headers** (peach all-caps with letter-spacing) bracket every section. No prose where a section-head should be.
- **§6.12 One peach-fill primary per screen, maximum.** The current screen has TWO (`Triage with AI` AND `Build Fix Prompt`). One must lose.
- **§6.13 Utility buttons** are quiet (transparent, hover-reveal). Move-actions belong here, not in peach-fill territory.
- **§6.21 Workflow stepper** is the canonical workflow-teaching component. If you want to teach the user "where you are in the triage flow," use the stepper; don't invent a new pattern.
- **§6.22 Module screen header** is one row only. No subtitle.
- **§6.23 Activity indicator** (just amended into the Bible from your earlier proposal). Use button-label-swap or shimmer; no spinners, no GIFs.
- **§7.5 ESC-to-back** works (verified in screenshot). Don't break it.
- **§13 Resize behavior.** Mockup demonstrates narrow / default / wide widths if the layout differs across them; otherwise show default.

## Constraints from your earlier AM Bible pass that remain valid

These are the affordance state machine rows from `AM_BIBLE_PASS_v1.md` Part A "Screen B":

| Bug state | Triage with AI | Build Fix Prompt | Move actions |
|---|---|---|---|
| Untriaged | Visible enabled | **Hidden** | Hidden |
| Triage running | Visible disabled with activity | Hidden | Hidden |
| Design/clarify gaps | Visible secondary "Re-triage" | Visible disabled with reason | Conditional |
| Ready, no unresolved gaps | Visible secondary "Re-triage" | Visible enabled primary | Conditional secondary |
| Amend only | Hidden or secondary re-triage | Visible enabled primary "Build Amendment Prompt" | Hidden |
| Feature request redirect | Hidden | Hidden | Visible enabled "Move to Backlog" |
| Fixed | Hidden | Hidden | Hidden; read-only archive affordance if needed |

Synthesis (per `AM_BIBLE_SYNTHESIS_v1.md` AR-DI-1 through AR-DI-7) reconciled small differences with CC's reactions. The final state-machine sketch is in CC's reactions §4. Your mockup should render at minimum the five states above.

## What I think the screen is for

The screen has TWO purposes that the current layout doesn't separate:

1. **Read the bug.** Files, repro, expected, actual, notes. Diagnostic, dense.
2. **Triage and act on the bug.** Run AI triage, resolve gaps, build a fix prompt, or move it elsewhere.

Right now both purposes share the screen with no visual hierarchy. The bug content takes ~50% width as a wall of raw markdown; the action zone takes the other 50% as a sparse stack of buttons. Neither is doing its job. The right column needs section grammar (`.section-head` peach caps + `--border-soft` separators) the same way the Edit screen's right pane does.

The bug content (left column) needs to be *parsed and rendered as PG section grammar*, not raw markdown. `## Files` becomes a peach-caps `.section-head` with the file list as info-rows or a list. `## Reproduce` becomes another section. `## Expected` and `## Actual` become a side-by-side comparison if the screen's wide enough, or stacked sections if narrow.

I'm not telling you the layout — that's your design problem. I'm telling you the framing.

## Reference files (read these before authoring)

Gold-standard mockups:

- `workflows/design/v4_0/v4_0_edit_image_mockup.html` — THE reference for component grammar, section rhythm, info-row cadence, button hierarchy.
- `workflows/design/v4_0/v4_0_palette_typography.html` — token swatch deck.
- `workflows/design/v4_0/v4_0_right_panel_study.html` — right-pane variants.
- `workflows/design/v4_0/v4_0_arrange_canvas_mockup.html` — another module screen's voice.

PG Bible (canonical):

- `workflows/design/PG_DESIGN_BIBLE_v1.md` v1.1 — read end to end. §1.4, §1.5, §1.6, §2, §3.3, §6.12, §6.13, §6.21, §6.22, §6.23, §7.5 are most relevant.

Existing AM source-of-truth:

- `audit_module/audit_module_window.py` — current implementation. `_BugDetailScreen` class is the screen in question.
- `audit_module/_components.py` — StatusPane, _WorkflowStepper, AM-shared widgets.
- `audit_module/_tokens.py` — AM_TOKENS palette.

Earlier passes (folded into current synthesis):

- `workflows/audit/AM_BIBLE_SYNTHESIS_v1.md` — synthesis of your earlier AM Bible pass + CC's reactions. Section 1 (agreements), Section 2 (disagreements with Claude judgments), Section 4 (Bible amendments applied today).
- `C:\CODEX PG\workflows\design\AM_BIBLE_PASS_v1.md` — your earlier AM Bible pass.
- `workflows/cc_mailbox/CLAUDE Inbox/20260426_140000_CC_to_CLAUDE_AM_bible_compliance_reactions.md` — CC's earlier reactions.

Pre-staged dispatch (now paused) for context:

- `workflows/prompts/v4_44_dispatch.md` — what we WERE going to ship for Screen B Phase 3 redesign. Read this to see what was being specced; your mockup may agree, disagree, or replace it.



## What CC is also doing

I'm dispatching CC the same task in parallel. CC will produce its own HTML mockup at `workflows/design/pg_general_mockups/AM_screen_b_v3_cc.html`. Two independent passes. Darrin compares. The goal is convergence on what good looks like before any code ships.

## Don't do

- Don't write code. No `audit_module_window.py` changes.
- Don't try to update the Bible. v1.1 is current; if you think a Bible amendment is needed, propose it in the mockup's own commentary section, not by editing the Bible.
- Don't redesign Screen A or Archive. Screen B only.
- Don't propose new component grammar (new chrome, new button shape, new section-header treatment). Inherit from the gold standards.
- Don't propose `QMovie` / GIF animations (existing constraint from §6.23).
- Don't reproduce stale chat history — every line of mockup commentary must be accurate as of right now.

## Open questions for your judgment

These are real choices the redesign has to make. Your mockup commits to one answer for each; if Darrin disagrees, he overrides on review.

1. **Two-column or stacked?** The current screen is two-column (bug content left, actions right). Is that right, or does Screen B work better as a stacked single-column at narrow widths and split at wide?
2. **Workflow stepper on Screen B — required, not optional.** Darrin's mode 2 reaction explicitly asks for it: *"Where is the instructions flow guideline in the top pane?"* Your mockup includes a §6.21 active-mode stepper somewhere on Screen B. Open question is *placement* (top of right column? top of full screen below header? inline with content?), not whether.
3. **Bug content rendering depth.** Raw markdown is wrong. But how much rendering? Section heads + info-rows + paragraph cadence is one option. Full markdown rendering with code-block monospace, links, and embedded screenshots is another. v4.0 scope. Plus: the current scroll-tube has no "jump to section" navigation — should there be a left-rail mini-TOC of the bug's sections (Files, Reproduce, Expected, Actual, Notes)?
4. **What replaces the giant gray UNTRIAGED rectangle and the FEATURE REQ pill?** Your earlier pass proposed a verdict/state card. CC's reactions sketched the same. The mockup makes it concrete. Critical: state badges must NOT look like buttons. Different shape, different color treatment, different position.
5. **`Move → Feature` / `Move → Amendment` button text.** Darrin's verbatim feedback from BUGS.md #140: *"Move feature and move amendment is obtuse — what is it."* Rename or annotate or restructure as you see fit.
6. **READINESS GAPS as the focus when DESIGN_DECISION_NEEDED.** When the bug state is DESIGN_DECISION_NEEDED, gaps ARE the work. They should dominate the right column visually — not get squeezed into 80px of vertical space. Your mockup designs gap rows that earn substantial real estate when relevant.
7. **Activity animation wiring.** Bible §6.23 defines three accepted forms (button label swap, status dot, 3px shimmer). Your mockup commits to which form for which operation: triage call (~30s), prompt build (~100-500ms), refresh (~50ms).
8. **Disabled-state visual treatment.** Bible §1.6 requires disabled affordances to look disabled AND answer "why?" Your mockup commits to a specific disabled style (greyed fill? reduced opacity? muted border?) and a specific way of surfacing the precondition (tooltip? adjacent status text? gap-row reference?).

## Acceptance

The mockup ships when:

- Five states are renderable (UNTRIAGED, TRIAGE_RUNNING, DESIGN_DECISION_NEEDED, READY_FOR_FIX_PROMPT, FIXED).
- A user looking at UNTRIAGED can answer "what do I do next" within 3 seconds.
- A user looking at DESIGN_DECISION_NEEDED can immediately see the unresolved gaps and the path to unblock Build Fix Prompt.
- The screen reads as part of the same app as `v4_0_edit_image_mockup.html`. Section grammar matches. Button grammar matches. Type rhythm matches.
- All §1.4 / §1.5 / §1.6 / §6.12 / §6.21 / §6.22 violations from BOTH failure modes are gone.
- No off-token color literals.
- No subtitle under the screen header.
- One peach-fill primary per screen, maximum (the failure modes show 2-3 currently).
- State badges are visually distinct from buttons (different shape, different color treatment).
- Disabled buttons look disabled AND show why (tooltip, adjacent status, or gap-row reference).
- A workflow stepper teaches the per-bug triage flow somewhere on the screen.
- Activity animation forms are committed for triage / prompt-build / refresh.
- READINESS GAPS gets first-class real estate when state is DESIGN_DECISION_NEEDED.

## Time budget

This is Extra-High tier work. Take the time you need. Quality > speed. Last AM mockup ship cycle (`AM_screen_b_v2_codex.html`, 2026-04-25) was ~3-4 hours of focused work; expect similar or longer.

When done, send a CODEX_to_CLAUDE report with:

- Path to the mockup file.
- Brief summary of design decisions you made and why.
- Open questions you couldn't resolve and parked for Darrin.
- Any Bible amendments you want to propose (don't apply them — propose).

Deliverables:
- `C:\CODEX PG\workflows\design\pg_general_mockups\AM_screen_b_v3_codex.html` (the mockup)

— Claude
