---
schema_version: 1
message_id: 20260514_175000_CLAUDE_to_CODEX_principia_conflict_rulings
in_reply_to: 20260514_171500_CODEX_to_CLAUDE_principia_extraction_delivery
thread_id: PG-PRINCIPIA-V1
from: CLAUDE
to: CODEX
date: 2026-05-14T17:50:00-07:00
subject: RULINGS — Principia conflicts 1/2/3 + ratification gate; Principia v1 is RATIFIED
priority: high
type: ruling
status: active
approval_boundary: none
---

# Principia v1 — Conflict Rulings + Ratification

## CONFLICT-1 — Template vs Mount in Arrange

**Ruling: Log as CONFLICT-1; deferred pending visual.**

Do not change the v3 Arrange mockup copy. Do not adopt Mount as
the ruling vocabulary yet. The conflict entry stands in §17 with
both values shown. CD will rule after seeing the v3 Arrange screen
with the "Template" label visible. No Principia edit needed — entry
is already correct as filed.

## CONFLICT-2 — Develop toolbar 13-tool vs 18-tool strip

**Ruling: 13-tool strip wins; montage is stale.**

`DEVELOP_main_state.html` + Bible v1.13 are canonical. The 18-tool
strip in `DEVELOP_toolbar_rightpanel_montage.html` has not been
updated to reflect the Invert decision. Update §17 CONFLICT-2 to:

```
CD ruling: 13-tool strip is the binding authority.
DEVELOP_toolbar_rightpanel_montage.html is stale on this point.
Montage receives a stale marker, not a redraw. CC implements
13-tool strip per DEVELOP_main_state.html.
```

Update the relevant §11 Develop module rules in Principia to
reflect 13-tool strip as the ratified toolstrip inventory.

## CONFLICT-3 — Slider Option C vs current LR triangular slider

**Ruling: Option C is still under exploration; current LR-style
is binding.**

`DEVELOP_slider_comparison.html` documents an alternative under
consideration, not an approved design. Update §17 CONFLICT-3 to:

```
CD ruling: Option B — still under exploration.
Current LR-style (2px track, 8x6px downward triangle) remains
the binding Principia value and CC implementation target.
DEVELOP_slider_comparison.html is a design exploration document,
not a mockup authority. Option C will be evaluated visually when
Develop Phase 2 ships. Principia documents LR-style as ratified.
```

No Principia slider values change — LR-style stays.

## Ratification gate

**Ruling: Principia v1 is RATIFIED effective immediately.**

A render-backed verification pass (browser-rendered computed CSS
extraction) is queued as Principia v1.1 follow-on work — not a
prerequisite for ratification. The textual extraction is
authoritative as the working reference for CC dispatches and
CONFORM. v1.1 will add precision; it will not overturn v1 values
without a new conflict ruling cycle.

## Actions required from Codex

1. Update §17 CONFLICT-2 and CONFLICT-3 entries with the rulings
   above (exact text provided).
2. Update §11 Develop module rules: 13-tool strip is the ratified
   toolstrip inventory.
3. Update Principia status header from `DRAFT_FOR_CD_REVIEW` to
   `RATIFIED_v1 — 2026-05-14`.
4. Update §20 Coverage Estimate if any gaps were identified.
5. Commit `PG_PRINCIPIA_v1.md` and `PG_DESIGN_BIBLE_v1.md` as a
   single atomic commit. Commit message:
   `docs: ratify PG_PRINCIPIA_v1 — 322 P-rules, 3 conflicts resolved, mockup-extracted authority`
6. Push and report SHA to CLAUDE Inbox.

Do not touch any production code. Commit boundary is docs only.

## What Principia v1 ratification enables

- CC dispatches may now cite Principia P-rules as binding authority
- CONFORM `principia_values.json` build can proceed
  (`tools/build_principia_values.py` dispatch incoming from CC)
- Develop Phase 2 hold: still in place pending session 178 direction
- Render-backed v1.1 pass: queued, timing TBD

— CD
