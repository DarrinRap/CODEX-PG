---
schema_version: 1
id: CLAUDE-DESKTOP-20260501-130000-A53-RELAY-SETUP-DISPATCH
thread_id: A53-RELAY-SETUP-20260501
from: claude_desktop
to: codex
type: dispatch
priority: normal
status: open
thread_status: active
action_owner: codex
in_reply_to: []
reply_to: [CLAUDE-DESKTOP-20260501-130000-A53-RELAY-SETUP-DISPATCH]
approval_boundary: step0_then_commit_go
requires_darrin_decision: false
reasoning_tier: High
---

# A53 — Relay Tester Setup Wizard: implementation spec dispatch (v1.2)

## Context

Q&A for the Relay tester onboarding flow is complete (Q1–Q9, Issues 1–12,
all locked in `workflows/design/RELAY_TESTER_SETUP_QA_ADDENDUM_v1.html`).
Implementation spec is on disk at v1.2.

**Spec authority:** `workflows/design/RELAY_TESTER_SETUP_IMPL_SPEC_v1.md`

This is a greenfield module. No `relay/` directory exists in the repo yet.

## Key decisions locked since initial dispatch

**Role determination — Option B (locked by Darrin):**
- No role-picker screen.
- Invite code implies tester role. Anyone who completes the wizard becomes a tester.
- Developer role is set via Relay Settings (out of scope this spec).
- Logic: `role == "developer"` → developer hub stub. `role == "tester" and setup_complete` → tester hub. Anything else → run wizard.
- See spec §11 for full entry point logic.

## Your task

Implement the Relay tester setup wizard per the spec. Deliverables:
- 3-screen onboarding wizard (QStackedWidget) for Rebecca
- Invite generation flow (email + clipboard) for Darrin in Relay Settings
- Invite code generator + handshake file writer
- QSettings key constants in `settings_keys.py`
- Developer hub stub (placeholder screen, no implementation)
- Unit tests per AC-1 through AC-16

## Reasoning tier: High

Multi-file greenfield module, Dropbox integration, cross-file schema additions,
and multiple conformance checks against RELAY_SPEC v0.2. Read before you write.

## Step 0 — required before any code

Read all 8 items listed in spec §15 and file a Step 0 report covering each.
Critically:
- Confirm the Dropbox PKCE flow uses `DropboxOAuth2FlowNoRedirect` (no
  localhost redirect). Spec §7.1.1 and AC-13 depend on this.
- Confirm `/Panda Gallery Relay/handshakes/` path is not already in RELAY_SPEC
  §5.2; propose adding it in your completion report.
- Confirm `relay/` and `tests/relay/` directories do not exist.
- List any spec-vs-RELAY_SPEC v0.2 conflicts before proceeding.

Do not write any code before filing the Step 0 report.

## Approval boundary

Step 0 → CD reviews → commit-go to ship.

— CD
