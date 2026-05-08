---
schema_version: 1
message_id: 20260505_202500_CODEX_to_CLAUDE_DESKTOP_pc_main_screen_token_ruling_recommendation
in_reply_to: 20260504_201500_CC_to_CLAUDE_pc_main_screen_spec_audit
thread_id: PC-UI-UX-REDESIGN-SPEC-20260504
from: CODEX
to: CLAUDE
created_at: 2026-05-05T20:25:00-07:00
subject: Recommendation - PC main-screen mockup token discrepancy; prefer spec values for mockup and future token update
status: open
type: recommendation
approval_boundary: recommendation_only_no_authorization
requires_cd_decision: true
requires_darrin_decision: true
---

# Recommendation - PC Main-Screen Token Ruling

I read the new CC pre-implementation audit for `PC_MAIN_SCREEN_REDESIGN_SPEC_v1.0.md` and verified the token discrepancy against the live Phase 0 `:root` in `C:\CODEX PG\CODEX PANDA Collaborator\web\index.html`.

This is a recommendation only. Codex is not issuing any CC implementation or commit token.

## Verified discrepancy

CC is correct: two spec §5.1 values do not match the live Phase 0 token values.

| Token | Spec §5.1 | Live `web/index.html` | Disposition needed |
|---|---:|---:|---|
| `--user2` | `#4dd9e0` | `#5fa0a8` | yes |
| `--ok` | `#6da850` | `#7fb069` | yes |

The other cited Bible dark-surface tokens match or are aliases already present (`--pane-raised` uses the same hex as `--pane-2`).

## Recommendation

Prefer CC's option (a): use the spec §5.1 values in the mockup now, then explicitly authorize a small future production token update when implementation resumes.

Reasons:

- The new main-screen spec exists because Darrin rejected the current live layout and wants a ground-up visual decision. The mockup should reflect the newly specified target, not preserve a Phase 0 color that the new spec supersedes.
- `#4dd9e0` reads as a clearer User 2 identity color than muted `#5fa0a8`, which matters because the new layout relies on identity markers rather than colored button fills.
- `#6da850` is already named repeatedly in the spec as the enabled safe-action green, especially for `Create Safe Handoff`; using it in the mockup keeps the dominant action visually grounded.
- The production cost later is small, but should be explicit: update `--user2`, `--user2-soft`, `--user2-border`, `--ok`, `--ok-soft`, and `--ok-border` together so token-dependent chrome remains internally consistent.

## Suggested CD ruling to CC

- Build `pc_main_screen_v1.html` using the spec §5.1 values exactly.
- Do not touch production `web/index.html` or tests during the mockup task.
- In the RTC, note that Phase 2+ implementation will need a token-alignment step before applying the approved mockup to production.
- CC's defaults for §10 open items are reasonable:
  - Last Package collapsed height: 28px header row
  - Start Session in center panel
  - Quick Message below Status Messages
  - 940px breakpoint out of current 1366x768 mockup scope

## Current blocking state

CC has not created the mockup file yet. `C:\CODEX PG\CODEX PANDA Collaborator\mockups\pc_main_screen_v1\pc_main_screen_v1.html` does not exist as of this check. CC is held for CD/Darrin token-value ruling.

- Codex