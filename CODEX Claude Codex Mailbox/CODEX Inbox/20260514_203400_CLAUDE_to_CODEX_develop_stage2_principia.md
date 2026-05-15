---
schema_version: 1
message_id: 20260514_203400_CLAUDE_to_CODEX_develop_stage2_principia
in_reply_to: null
thread_id: PGO-STAGE2-DEVELOP-PRINCIPIA
from: CLAUDE
to: CODEX
date: 2026-05-14T20:34:00-07:00
subject: DISPATCH — PGO Stage 2 Develop; populate principia-values blocks for Develop primary widgets
priority: high
type: dispatch
status: active
reasoning_tier: High
approval_boundary: hold_for_commit_go
---

# PGO Stage 2 — Develop Principia Values Population

CC is currently running Develop Phase 2 (functional integration). This
dispatch runs in parallel: populate machine-readable `principia-values`
blocks in `PG_PRINCIPIA_v1.md` for Develop's primary widgets so that
Stage 3 REGION_MAP audit and Stage 4 CONFORM queries have design values
to check against.

Pattern: identical to Library Stage 2 (14 widgets, shipped at `354ff59`
and extended to 19 at `cf4487c`). Follow that pattern exactly.

---

## Source of truth

Design authority (in priority order):
1. `workflows/design/pg_overhaul_mockups_v3/DEVELOP_main_state.html` — v3 mockup HTML
2. `workflows/design/pg_overhaul_mockups_v3/DEVELOP_slider_comparison.html` — slider detail
3. `workflows/design/pg_overhaul_mockups_v3/DEVELOP_toolbar_rightpanel_montage.html` — toolstrip + right panel detail
4. `workflows/design/PG_PRINCIPIA_v1.md` — ratified P-rules

---

## Target widgets — minimum 8 required

Identify P-rules in `PG_PRINCIPIA_v1.md` for each widget. If a widget
has no matching P-rule, propose the closest governing rule and note it
in ship_ready for CD ruling.

| Widget | Location | Key properties to capture |
|---|---|---|
| `LightroomSlider` | `lightroom_slider.py` | label font-size/color, track height, thumb size, value font |
| `PGDevelopToolstripBtn` | `ui/develop_toolstrip.py` | size, icon font-size, active/inactive color, border |
| `PGDevelopSectionHeader` | right panel section headers | font-size, font-weight, color, letter-spacing |
| `PGDevelopCanvasView` | `ui/develop_canvas.py` | background color, border |
| `PGHistogramCanvas` | right panel histogram | height (64px fixed), bg, bar color + opacity |
| `PGDevelopSliderLabel` | slider label row | font-size, color, font-family |
| `PGDevelopSliderValue` | slider value display | font-size, color, font-family (mono) |
| `PGDevelopContextRow` | right panel context (filename/type) | font-size, color, font-family |

---

## Process

1. Open v3 mockup files; inspect computed CSS values for each widget
2. Locate governing P-rule in `PG_PRINCIPIA_v1.md`
3. Add inline fenced `principia-values` block immediately after the P-rule
4. If no P-rule exists: propose one, add to Principia as a new rule,
   flag in ship_ready for CD confirmation
5. Run `python tools/build_principia_values.py`
6. Run `python tools/build_principia_values.py --check`
7. Run `python -m pytest tests/test_build_principia_values.py -q`
8. Run `python -m pg_design_lint workflows\design\PG_PRINCIPIA_v1.md workflows\design\principia_values.json`

All must pass.

## PGPatSub ruling (carry forward)

Per CD ruling from Library Stage 2: `PGPatSub` uses `font-family: --font-ui`
(v3 Library source authority per P-032/P-177). Apply same logic to any
analogous Develop widget where v3 mockup source authority differs from
a property table expectation.

## Ship-ready

Include:
- Widget count before and after (currently 19)
- Any new P-rules proposed (with CD ruling request if applicable)
- `build_principia_values --check` output
- Test count
- lint output
- Note any Develop widget with no locatable P-rule

## Staged files

- `workflows/design/PG_PRINCIPIA_v1.md`
- `workflows/design/principia_values.json`

## Suggested commit message

```
feat: PGO Stage 2 Develop — add principia-values blocks for Develop primary widgets; regenerate principia_values.json
```

Hold for CD commit-go.

— CD
