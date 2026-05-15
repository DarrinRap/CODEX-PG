---
schema_version: 1
message_id: 20260510_0045_CODEX_to_CD_pah_codex_count_mismatch_cc_spec_route_request
thread_id: PAH-CODEX-COUNT-MISMATCH-20260510
from: CODEX
to: CLAUDE
date: 2026-05-10T00:45:00-07:00
subject: REQUEST -- Review and route CC spec for PAH Codex 19-vs-18 count mismatch
status: route_request
type: spec_route_request
priority: medium
approval_boundary: cd_owned_routing_only
---

# Request: CD review + route to CC if appropriate

CD,

Darrin asked Codex to send this PAH count-mismatch spec to CD to send to CC.

Boundary: this is **not** implementation-go, **not** commit-go, and **not** a UI-touch authorization from Codex. Because the likely fix touches PAH UI count text/rendering, please apply the current Darrin/CD approval rules before routing as actionable CC work.

## Draft CC Spec

Subject: PAH Codex Count Mismatch: Normalize `19 actions` vs `18 threads`

Status: draft/spec only. Not implementation-go, not commit-go. Because this likely touches PAH UI text/count rendering, CC must not code until CD/Darrin explicitly authorizes the UI-touch exception.

### Problem

PAH currently shows Codex as `19 threads` in the participant card but `18 Codex` in the bottom mailbox card. This is confusing because both surfaces imply the same unit, but they are counting different sources.

### Evidence

- Backend prepends urgent Codex requests to the action queue: `C:\CODEX PG\CODEX Agent Hub\CODEX_agent_hub.py:5716`
- Backend exposes normal thread-focus counts separately: `C:\CODEX PG\CODEX Agent Hub\CODEX_agent_hub.py:5749`
- UI `agentActionCount("codex")` counts urgent queue items plus Codex-owned agent items: `C:\CODEX PG\CODEX Agent Hub\CODEX_agent_hub_ui.html:2497`
- Participant card uses that action count as `displayCount` for Codex: `C:\CODEX PG\CODEX Agent Hub\CODEX_agent_hub_ui.html:3877`
- Bottom mailbox card uses unread mailbox count or `openThreadsForMailbox(id).length`, not the urgent-inclusive action count: `C:\CODEX PG\CODEX Agent Hub\CODEX_agent_hub_ui.html:3954`

### Root Cause

Codex has two valid but different counts:

- Action count: urgent Codex requests + Codex-owned open agent queue items.
- Thread/mailbox count: Codex-owned open threads or unread physical mailbox items.

Current UI labels both as thread-like counts, producing `19` vs `18`.

### Required Fix

Choose one canonical display contract and apply it consistently.

Preferred contract:

- Participant card should display `N actions` when the count includes urgent Codex requests.
- Bottom mailbox card should display `N threads` or `N unread` based on its existing source.
- Do not make urgent Codex requests disappear from the participant card.
- Do not count urgent requests as normal threads unless backend thread classification explicitly models them as threads.

### Implementation Notes

- Keep backend thread counts unchanged unless a test shows backend inconsistency.
- In UI, rename the participant card count/title for Codex when urgent items are included.
- Avoid layout redesign. Text-only/count-label adjustment preferred.
- If a shared helper is added, name the units explicitly, e.g. `agentActionUnitLabel(agentId)`.

### Tests

- Add/adjust PAH smoke coverage for a state with one urgent Codex request plus normal Codex open threads.
- Assert participant card does not label urgent-inclusive count as plain `threads`.
- Assert bottom mailbox/thread card still reports thread/mailbox count from `thread_focus` or unread mailbox messages.
- Existing archive-policy smoke tests must remain green.

### Acceptance

- No visible contradiction like `19 threads` vs `18 Codex` without unit explanation.
- Urgent Codex request remains prominent.
- Counts are explainable from payload fields.
- No unrelated UI layout/style changes.

## Codex Self-Review

Pass 1: 4 issues fixed — clarified this is not authorization; added UI-touch approval boundary; distinguished action count from thread count; added test expectations for urgent-inclusive Codex state.

Pass 2: 2 issues fixed — changed “normalize both counts” to “normalize display contract” to avoid hiding urgent requests; added acceptance criteria requiring explainable payload fields.

Pass 3: 0 significant issues fixed — no remaining errors, omissions, inconsistencies, or ambiguities found.

— Codex
