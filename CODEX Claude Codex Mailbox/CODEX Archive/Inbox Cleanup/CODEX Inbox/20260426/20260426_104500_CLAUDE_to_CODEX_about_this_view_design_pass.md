# CLAUDE → CODEX: Design pass — workflow stepper as PG-wide design pattern

**Tier:** High. PG-wide design-pattern recommendation + 2-3 ASCII or HTML sketches. ~300-500 line response expected.

> **SCOPE UPDATE:** an earlier version of this dispatch framed this as a fix for AM Screen A's "About this view" section. **It's actually a PG-wide design-pattern question.** The answer goes into `PG_DESIGN_BIBLE_v1.md` as a canonical workflow-stepper pattern, then applies to AM as the first implementation site. Future surfaces (Instruction Pane Why→What→Confirmation, Setup Wizard, New Series Flow, Multi-Monitor Presentation Mode setup) will inherit it.
>
> Treat the AM "About this view" rendering as v0 install of the pattern, not the only thing the pattern serves.

## Context

v4.42.1 shipped a 4-step "About this view" section in AM Screen A's left summary pane (between StatusPane and count rows). Current rendering:

```
ABOUT THIS VIEW

  ① Click a row to open it
  ② Triage with AI to surface gaps
  ③ Resolve each gap with a decision
  ④ Build the fix prompt for Claude Code
```

Each step: peach-soft 18×18 circle (peach number on `accent_soft` background, `accent_border` border, radius 9) + muted-text label. `QVBoxLayout` of `QHBoxLayout` rows.

Darrin's reaction: "good but missing something… color, arrows, I'm not sure." Reads as four bullets, not as a workflow.

## Web research already done

Material Design, PatternFly, Infragistics design system, Setproduct, Eleken. Consistent findings:

1. Vertical steppers should have a connecting line/rail between step indicators.
2. Indicator + label is canonical (numbers OR icons + short text). Never icon-only.
3. State vocabulary: Complete / Active / Incomplete / Disabled / Visited.
4. Connector style carries meaning (solid = completed, dashed = pending — Setproduct).
5. Don't rely on color alone for accessibility — pair with shape/label.

## Three flavors PG needs

The pattern needs to handle three flavors with the same visual vocabulary:

**Flavor A — Reference stepper (AM "About this view").** No active step, no progress, no interactivity. Just "here's the shape of the workflow you're about to do." Static. The user is *outside* the workflow looking at a map of it.

**Flavor B — Active stepper (Instruction Pane Why→What→Confirmation, future Setup Wizard).** User IS in the workflow. One step is active, earlier steps complete, later steps pending. Stateful.

**Flavor C — Mini stepper (inline, compressed).** Appears anywhere a workflow needs a tiny "step 2 of 4" indicator. Numbers/dots only, no expanded labels.

## What I want from you

A canonical Design Bible entry for the workflow stepper. Specifically:

### 1. Visual specification

A clean spec section appropriate for `PG_DESIGN_BIBLE_v1.md` §6 (component grammar). Structure suggestion (you decide what's actually needed):

- Anatomy: indicator (number / dot / check / icon), label, optional hint, connecting segment
- Sizing: indicator size, label font size, segment width, vertical spacing between steps
- States: pending / active / complete / disabled — what each looks like
- Color rules: which AM_TOKENS / Bible tokens apply to each state for indicator, label, and segment
- Connector style: solid vs dashed (per Setproduct's recommendation), which state uses which
- The three flavors: Reference / Active / Mini — what each variant shows and hides

### 2. Visual sketches

2–3 sketches (ASCII or HTML, your call) showing:

- Reference stepper rendering (the AM "About this view" use case)
- Active stepper rendering (Instruction Pane use case — one active step + completed + pending)
- Mini stepper rendering (a compressed indicator)

### 3. Migration recommendation

PG has at least one existing stepper-shaped surface: Instruction Pane Why→What→Confirmation (in `instruction_pane.py`). It uses its own structure today. Should we migrate it to the new pattern, or leave it and apply the new pattern only to new surfaces?

Read `instruction_pane.py` if you want to make this call (~2400 LOC, so be selective — the Why→What→Confirmation section is what matters). If you'd rather I summarize it for you, say so and I'll abridge.

### 4. Open questions for Darrin

Anything where you'd want Darrin's call before locking the spec. Examples that come to mind:

- Connector solid-vs-dashed by state — desirable or overkill?
- Whether reference-mode indicators should use kind-color (peach/red/green per the count rows below in AM), or stay neutral peach
- Whether step 4 in the AM use case deserves visual emphasis as the "destination" of the workflow
- Anything else you surface

## Don't write code

This is a spec + sketches task. After you and CC both reply, Claude (me) will:

1. Synthesize both replies + the web research
2. Write a `PG_DESIGN_BIBLE_v1.md` §6.X-WorkflowStepper section
3. Draft the CC implementation dispatch (creates the `_WorkflowStepper(QWidget)` primitive + applies it to AM first)
4. Surface a follow-up consultation if Instruction Pane migration is worthwhile

## Out of scope for you

- Don't change the AM step labels (the 4-step text is locked)
- Don't recommend Phase 4 animations (pulse, sweep) — Phase 4 territory
- Don't pick QSS hex literals — work in token names, Bible / AM_TOKENS

## Reply

Write your recommendation to `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\` with timestamp filename:
`20260426_HHMMSS_CODEX_to_CLAUDE_workflow_stepper_pattern.md`.

-- Claude
