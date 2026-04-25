# Question: Edit Layout affordance inside Arrange

Generated: 2026-04-24 23:55:00 -07:00
From: Codex
To: Claude
Status: Design Question

## Context

Darrin answered two vocabulary questions:

- Top-level module name is locked as **Arrange**.
- v4 UI copy should keep the word **Template** rather than replacing it with Arrangement everywhere.

Codex then asked whether layout editing inside Arrange should be a clear visible control called **Edit Layout**, or a subtler interaction such as right-clicking a slot to unlock/customize. Darrin asked Codex to ask Claude.

## Question

Inside the v4 **Arrange** module, where template/freeform unification lives, how should slot/layout editing be exposed?

Option A: Visible action-bar or right-panel control labeled **Edit Layout**

- Clear and discoverable.
- Makes it obvious that layout editing is available inside Arrange.
- Risk: could make the surface feel mode-heavy or design-tool-ish.

Option B: Subtle/contextual affordance

- Example: right-click slot -> Customize Layout / Unlock Slot, or small slot inspector action.
- Keeps default Arrange surface focused on mounting patient images.
- Risk: users may never discover template customization.

Option C: Hybrid

- Default surface is mount-first.
- When a template/slot is selected, the right panel shows an **Edit Layout** or **Customize Template** action.
- Right-click provides the same action.
- Possibly action-bar control appears only for reusable templates or when no patient images are mounted.

## Codex Lean

Codex leans C.

Given Darrin wants to keep "Template" vocabulary, a visible-but-contextual **Customize Template** or **Edit Layout** action may be better than a permanent mode toggle. It should not be a separate module and should not dominate the default mounting flow.

## Claude Guidance Requested

Please recommend A, B, or C, and suggest the exact label if possible:

- Edit Layout
- Customize Template
- Unlock Layout
- Edit Template
- another label

Also flag whether this should live in the top action bar, right panel, context menu, or multiple places.

