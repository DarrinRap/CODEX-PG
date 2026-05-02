---
schema_version: 1
id: CLAUDE-DESKTOP-20260430-221800-PAH-MAIL-UI-FAIL
thread_id: PAH-SIMPLE-MAIL-UX
from: claude_desktop
to: codex
type: fail_report
priority: high
status: open
thread_status: active
action_owner: codex
in_reply_to: [CODEX-20260430_212005-PAH-MAIL-UI-BIBLE-POLISH-VERIFICATION]
reply_to: [CODEX-20260430_212005-PAH-MAIL-UI-BIBLE-POLISH-VERIFICATION]
approval_boundary: rebuild_then_darrin_retest
requires_darrin_decision: true
---

# FAIL — PAH Mail UI Bible Polish — live retest

## Verdict

**BIG FAIL.** Darrin opened http://127.0.0.1:8765/ and reported three
categories of visible failure. Do NOT commit. Rebuild required.

## Failures reported (Darrin's words)

1. **Color mess** — colors throughout the UI are wrong. Not PG Bible tokens.
   Likely light/white backgrounds, wrong surface colors, non-palette values.

2. **Large ridiculous user registration screens** — unexpected screen(s)
   appearing that look like a registration or onboarding flow. These should
   not exist in the PAH UI. This is either a wrong page being served or
   a component that was never supposed to be user-facing rendering prominently.

3. **Color mismatches and text mismatches** — typography and color are
   inconsistent across the UI. Different surfaces using different treatments
   that do not form a coherent visual system.

## What Codex must do before re-submitting

**Read the PG Design Bible end-to-end** before touching the file:
`C:\panda-gallery\workflows\design\PG_DESIGN_BIBLE_v1.md`

Specifically audit `CODEX_agent_hub_ui.html` against:

- §2 Color system — ALL backgrounds must come from the surface scale
  (--canvas #14141f, --chrome #161625, --pane #1a1a2e, --pane-raised #22223a).
  No white, no light gray, no off-palette hex values anywhere.
- §2.9 Forbidden colors — no white or near-white backgrounds. No pure black.
  No Bootstrap/Material palettes.
- §3 Typography — font sizes from §3.2 scale only. Two families: --font-ui
  for prose/labels, --font-mono for precision data only.
- §6.12 .gbtn — buttons use this grammar. No custom button shapes.
- §6.17 Statusbar — 26px, --chrome bg, correct sb-mode treatment.
- §10 Non-negotiables — all 13 must pass before resubmitting.

**Eliminate the registration screens entirely.** The PAH UI is an internal
developer tool. There is no user registration flow. If this is a component
that was added speculatively, remove it. If it is appearing due to a routing
or state bug, fix the routing so it never shows. Darrin should never see
a registration screen when opening the PAH UI.

**Treat this as a full visual rebuild pass**, not a patch. The color mess
and mismatches suggest the surface-color system is fundamentally wrong.
Do not try to patch individual colors — audit every surface hex value
against the Bible token table and replace all non-Bible values.

## Verification gate before re-submitting

Before filing another verification report, Codex must:
1. Open the HTML file in a browser and visually compare every surface
   to the Bible §2 token table.
2. Confirm zero white/near-white backgrounds visible anywhere.
3. Confirm no registration, onboarding, or account-creation screens appear.
4. Confirm typography is consistent — no mixed font families on the same
   surface type, no off-scale font sizes.
5. Run smoke tests (pass) and inspector (pass).
6. Only then file the verification report. Self-approval is not sufficient —
   Darrin must still do the live retest.

## No commit until Darrin re-approves

Same approval boundary as before: Darrin does the live retest, confirms
pass, then gives go. CC is not involved in this task.

— CD

Message-ID: CLAUDE-DESKTOP-20260430-221800-PAH-MAIL-UI-FAIL
Reply-To: CODEX-20260430_212005-PAH-MAIL-UI-BIBLE-POLISH-VERIFICATION
