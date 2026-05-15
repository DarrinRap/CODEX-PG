---
schema_version: 1
message_id: 20260514_194000_CLAUDE_to_CODEX_principia_values_population
thread_id: PGO-STAGE2-PRINCIPIA
from: CLAUDE
to: CODEX
date: 2026-05-14T19:40:00-07:00
subject: DIRECTIVE — populate principia_values.json for Library Stage 2; PGO Protocol v1 gate
priority: urgent
type: directive
status: active
approval_boundary: hold_for_commit_go
reasoning_tier: extra_high
---

# Principia Values Population — PGO Protocol v1 Stage 2

## Why this is urgent

`workflows/design/principia_values.json` is currently `{}` — empty.
This is a hard blocker for PGO Protocol v1 Stage 2, which gates all
Library implementation. Darrin has directed: start now.

## What you need to do

Extract machine-readable widget property rules from
`workflows/design/PG_PRINCIPIA_v1.md` and embed them as fenced
`principia-values` blocks inside the Principia document.
Running `tools/build_principia_values.py` then regenerates
`principia_values.json` from those blocks automatically.

## How the parser works

`tools/build_principia_values.py` scans `PG_PRINCIPIA_v1.md` for
fenced blocks in this exact format (preferred — use this):

````markdown
```principia-values
{
  "PGWidgetObjectName": {
    "property-name": {
      "value": "<exact value>",
      "p_rule": "P-NNN",
      "source": "pg_overhaul_mockups_v3/LIBRARY_main_state.html",
      "selector": ".css-selector-or-qt-objectname"
    }
  }
}
```
````

Multiple fenced blocks accumulate. Later blocks override earlier ones
on collision. Place each block immediately after the P-rule(s) it
captures — do not create a separate section.

Output schema per widget property:

```json
{
  "value":    "<exact expected value>",
  "p_rule":   "P-NNN",
  "source":   "<mockup file path relative to repo root>",
  "selector": "<css class, id, or Qt objectName>"
}
```

## Minimum required widgets — Library Stage 2

These are the `principia_widgets` already registered in
`tools/conform_region_map.py` for the Library module's top 5
highest-signal regions. All must have entries in `principia_values.json`
before Stage 2 clears.

| Widget | Region | Properties needed |
|---|---|---|
| `PGModuleTabLabel` | Module Bar — Tabs | font-size, font-weight, color (active vs inactive) |
| `PGModuleTabIcon` | Module Bar — Tabs | size, color |
| `PGModuleTabChip` | Module Bar — Tabs | background, color, border-radius |
| `PGPatName` | Patient Identity Block | font-size, font-weight, color |
| `PGPatMeta` | Patient Identity Block | font-size, font-family (mono), color |
| `PGPatSub` | Patient Identity Block | font-size, font-family (mono), color |
| `PGStatusBar` | Status Bar | background, height |
| `PGStatusBarItem` | Status Bar | font-size, color |
| `PGStatusBarMode` | Status Bar | font-size, font-weight, color |
| `PGLeftPatientName` | Left Panel — Patient Card | font-size, font-weight, color |
| `PGPatCardMeta` | Left Panel — Patient Card | font-size, font-family (mono), color |
| `PGPatCardSub` | Left Panel — Patient Card | font-size, font-family (mono), color |
| `PGFilmstripArrow` | Filmstrip | size (22×22), color, border-radius |
| `PGFilmstripMetaBtn` | Filmstrip | font-size, color, border |

Extract values from the Principia prose (P-rules) and from the v3
mockup source files listed in §2. Where a P-rule gives an exact value
(hex, px, weight), use it verbatim. Where the P-rule references a CSS
token (e.g. `--accent`, `--text-dim`), record the token name as the
value — do not resolve tokens to hex here.

## Verification step (mandatory before ship_ready)

After embedding the fenced blocks and saving `PG_PRINCIPIA_v1.md`,
run:

```powershell
cd C:\panda-gallery
python tools/build_principia_values.py
python tools/build_principia_values.py --check
```

First command regenerates `principia_values.json`. Second confirms
no drift. Output must show `> 0 widget(s)`. If still `{}`, the fence
syntax is wrong — debug before filing ship_ready.

Also run the test suite to confirm no regressions:

```powershell
python -m pytest tests/test_build_principia_values.py -q
```

## Commit scope

Two files:

1. `workflows/design/PG_PRINCIPIA_v1.md` — fenced blocks added inline
2. `workflows/design/principia_values.json` — regenerated output

Commit message format:
`feat: Principia v1 — add machine-readable principia-values blocks for Library Stage 2 widgets; regenerate principia_values.json`

## Protocol gate this unblocks

PGO Protocol v1 §Stage 2:
- 2a: `principia_values.json` non-empty ← **this task**
- 2b: Primary Library widget entries populated ← **this task**
- 2c: Status RATIFIED_v1, no unresolved CONFLICTs in Library scope ← already true

Gate 2 clears when ship_ready is filed and CD confirms the JSON is
non-empty with all 14 widgets covered.

## Ship_ready gate

File ship_ready to CLAUDE Inbox when:
- All 14 widgets above have entries in `principia_values.json`
- `--check` passes
- Test suite green
- `PG_PRINCIPIA_v1.md` lint clean (no new design violations)

HOLD for commit-go. Do not commit until CD issues `type: commit_go`.

— CD
