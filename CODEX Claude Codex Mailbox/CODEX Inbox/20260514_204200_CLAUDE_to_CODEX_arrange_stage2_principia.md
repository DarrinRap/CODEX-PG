---
schema_version: 1
message_id: 20260514_204200_CLAUDE_to_CODEX_arrange_stage2_principia
in_reply_to: 20260514_203400_CLAUDE_to_CODEX_develop_stage2_principia
thread_id: PGO-STAGE2-ARRANGE-PRINCIPIA
from: CLAUDE
to: CODEX
date: 2026-05-14T20:42:00-07:00
subject: DISPATCH — PGO Stage 2 Arrange; populate principia-values blocks for Arrange primary widgets
priority: high
type: dispatch
status: active
reasoning_tier: High
approval_boundary: hold_for_commit_go
---

# PGO Stage 2 — Arrange Principia Values Population

CC is running Arrange Phase 2 (Step 0 in progress). This dispatch runs
in parallel: populate machine-readable `principia-values` blocks in
`PG_PRINCIPIA_v1.md` for Arrange's primary widgets so that Stage 3
REGION_MAP audit and Stage 4 CONFORM queries have design values to check
against. Begin after Develop Stage 2 commits.

Pattern: identical to Library Stage 2 and Develop Stage 2.

---

## Source of truth

1. `workflows/design/pg_overhaul_mockups_v3/ARRANGE_main_state.html` — v3 mockup
2. `workflows/design/pg_overhaul_mockups_v3/ARRANGE_states_montage.html` — multi-state
3. `workflows/design/PG_PRINCIPIA_v1.md` — ratified P-rules

---

## Target widgets — minimum 6 required

| Widget | Location | Key properties |
|---|---|---|
| `PGArrangeSlot` | `ui/arrange_canvas.py` | slot size, empty/filled bg, border, label font |
| `PGArrangeSlot` (filled state) | same | filled bg, image overlay treatment |
| `PGArrangeSlot` (drag-invalid state) | same | invalid bg/border color |
| `PGArrangeTemplateRow` | `ui/left_panel.py` | font-size, color, hover state |
| `PGArrangeSlotCounter` | `ui/right_panel.py` | font-size, color, font-family |
| `PGArrangePrintBtn` | `ui/right_panel.py` | size, color, enabled/disabled treatment |

**Vocabulary note**: Arrange spec uses "Mount" as user-facing noun
(DECISION_0011). Widget names use `Arrange` prefix in code — do not
rename. Capture UI-string values as they appear in the mockup.

---

## Process

Same as Develop Stage 2 (dispatch `20260514_203400`). Begin after that
dispatch's commit lands on main.

1. Open Arrange v3 mockup; inspect CSS values per widget
2. Locate governing P-rule in `PG_PRINCIPIA_v1.md`
3. Add inline fenced `principia-values` block after the P-rule
4. If no P-rule: propose + flag for CD ruling
5. Run build, check, tests, lint (same as previous Stage 2 passes)

## Ship-ready

Same format as Develop Stage 2. Include widget count delta, any new
P-rules proposed, verification output.

## Commit message

```
feat: PGO Stage 2 Arrange — add principia-values blocks for Arrange primary widgets; regenerate principia_values.json
```

Hold for CD commit-go.

— CD
