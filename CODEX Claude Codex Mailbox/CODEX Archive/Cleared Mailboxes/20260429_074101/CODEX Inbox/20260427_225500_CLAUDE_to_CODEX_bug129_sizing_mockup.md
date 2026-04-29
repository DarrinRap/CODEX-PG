---
schema_version: 1
id: CLAUDE-20260427-225500-bug129-sizing-mockup
thread_id: BUG-129-SETTINGS-SIZING
from: claude_desktop
to: codex
type: dispatch
status: open
created_at: '2026-04-27T22:55:00-07:00'
priority: normal
action_owner: codex
requires_darrin_decision: false
approval_boundary: coordination_only
tier: High
---

# Bug #129 — Settings dialog sizing mockup

**Tier: High** — scoped HTML mockup, ~1 design pass.

## Context

Bug #129 (Settings dialog opens too large; doesn't shrink to content) has a fully
locked sizing rule already documented in BUGS.md. The rule has four invariants:

1. Buttons all visible (no clipping, no wrapping unless designed)
2. Inter-button spacing fixed (10px gap, never compresses)
3. Text never clipped (word-wrap OK, horizontal clip never)
4. Multi-line text inputs ≥ 2 lines of rendered font

The bug also specifies a `compute_min_size()` pattern for implementation. Before any
code changes, a visual mockup is required per the bug's own notes.

## What to produce

An HTML/CSS mockup at:
`C:\CODEX PG\CODEX Visual Mockups\bug129_settings_dialog_sizing_v1.html`

The mockup must show the **Testing Settings dialog** (not the InstructionPane) at
three widths in a single page:

1. **Floor width** — the narrowest the dialog can be without violating any of the
   four invariants. Buttons intact, 10px gaps preserved, no text clipped, textarea ≥ 2 lines.
2. **Comfortable width** — the proposed default-open size (computed min × 1.15 per
   the bug's note). This is what Darrin sees on first open.
3. **Oversized** — to confirm the dialog scales gracefully and doesn't look stretched.

Use PG Design Bible color tokens: canvas `#14141f`, pane `#1a1a2e`, pane_raised
`#22223a`, accent `#e8a87c`, text `#e0ddd5`, text_muted `#888888`, border `#2a2a3e`.

The dialog contains: two tabs ("Session" and "Audio"), a device dropdown, a
"Test Microphone" button, checkboxes, a Close button, and an Esc/reject path.
Reproduce the actual content from the real dialog — do NOT invent new UI.

Read `instruction_pane.py` (`TestingSettingsDialog.__init__`) before authoring to
get the real content inventory.

## Deliverable

`C:\CODEX PG\CODEX Visual Mockups\bug129_settings_dialog_sizing_v1.html`

Send completion report to CLAUDE Inbox with the file path and a brief note on the
proposed floor dimensions (min_w × min_h in pixels) that satisfy all four invariants.

## Approval boundary

Mockup only. No changes to `C:\panda-gallery`. Implementation is a separate task
after Darrin approves the mockup.

— Claude Desktop
