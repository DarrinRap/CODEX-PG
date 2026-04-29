---
schema_version: 1
id: CODEX-20260428-124900-a53-relay-setup-mockups-complete
thread_id: A53-RELAY-TESTER-SETUP-UX
created_at: '2026-04-28T12:49:00-07:00'
from: codex
to: claude_desktop
type: completion
priority: high
status: complete
thread_status: ready_for_review
action_owner: darrin
requires_darrin_decision: true
---

# Codex -> Claude: A53 Relay Tester Setup UX Mockups Complete

## Authority docs

Confirmed read before writing the deliverable:

1. `C:\panda-gallery\workflows\design\PG_DESIGN_BIBLE_v1.md`
2. `C:\panda-gallery\workflows\design\RELAY_TESTER_SETUP_QA_ADDENDUM_v1.html`
3. `C:\CODEX PG\CODEX Canonical Specs\RELAY_SPEC_v0.2.md`
4. `C:\panda-gallery\workflows\design\pg_general_mockups\relay_module_v1.html`
5. `C:\panda-gallery\workflows\design\RELAY_SCREEN_C_DESIGN_v1.md`
6. `C:\panda-gallery\scripts\dropbox_integration_test.py`

## Delivered path

`C:\panda-gallery\workflows\design\pg_general_mockups\relay_tester_setup_v1.html`

## Verification

- 9 Q&A screen sections present.
- 9 full `1280x800` render frames present.
- Required error variants present:
  - `Dropbox didn't authorise PG`
  - `Code not recognised`
  - `No internet connection`
  - `Darrin hasn't confirmed yet`
- Required setup copy present:
  - `github.com/[repo]/releases/latest`
  - `Paste the authorisation code here`
  - `📬 Relay setup test`
- Palette check passed: no off-palette hex values found.
- Per-screen primary-action check passed: no screen has more than one `.gbtn.primary`.
- No commit was made.

## UX assessment

Rebecca passes the new-user test at every screen. The setup flow keeps one visible job per screen, avoids technical copy in Rebecca-visible states, and moves diagnostics into Darrin's Settings. The Dropbox browser handoff is the only inherently unfamiliar moment, so the mockup treats it as a calm copy/paste continuation instead of a technical authorization flow.

## Open questions for Darrin

1. Confirm the final installer URL once the public release location is locked.
2. Confirm whether the invite email should include practice branding or stay plain text.
3. Confirm whether Darrin's manual hello confirmation remains required when auto-ack is enabled.

## Bible compliance notes

- Light email screen resolved by using Bible tokens only: `#e0ddd5` background with dark Bible-token text.
- Rebecca-visible setup screens avoid module tabs, tool strips, and full PG shell chrome.
- Darrin's Settings screen uses the PG shell and carries tester management plus diagnostics.
- Advanced diagnostics are presented as a disclosure with expanded-detail snippet, preserving the layered UX principle.
- Browser rendering was not run because the local Node environment does not have Playwright installed; static structural and palette checks passed.
