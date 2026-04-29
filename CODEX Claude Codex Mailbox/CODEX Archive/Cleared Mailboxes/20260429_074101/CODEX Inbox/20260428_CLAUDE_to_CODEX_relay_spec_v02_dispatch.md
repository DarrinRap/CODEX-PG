---
Message-ID: CLAUDE-20260428-RELAY-SPEC-V02-DISPATCH
Date: 2026-04-28
From: claude-desktop
To: codex
Type: dispatch
Tier: extra-high
Re: A51 — Relay spec v0.2
---

# CLAUDE → CODEX: Relay spec v0.2 (A51)

## Task

Update `C:\CODEX PG\CODEX Canonical Specs\RELAY_SPEC_v0.1.md` to v0.2,
incorporating all Screen C hub design decisions from a Q&A session with
Darrin on 2026-04-28.

## Primary source

`C:\panda-gallery\workflows\design\RELAY_SCREEN_C_DESIGN_v1.md`

Read this in full before starting. It is the canonical record of all
decisions. Every decision in that document must appear in the spec.

## Also read

- `C:\CODEX PG\CODEX Canonical Specs\RELAY_SPEC_v0.1.md` (current spec to update)
- `C:\panda-gallery\workflows\design\pg_general_mockups\relay_module_v1.html`
- `C:\panda-gallery\STRATEGY_NOTES.md` (2026-04-28 entries)
- `C:\panda-gallery\scripts\dropbox_integration_test.py` (verified Dropbox behavior)

## What to add to the spec

New sections required (add after existing §7 Open Questions):

### §8 — Hub layout and role architecture
Cover: same window layout, role-aware content, developer vs tester
role configuration in Relay Settings.

### §9 — Developer hub: All Reports view
Cover: tab strip (All Reports · By Tester · Sent · Templates),
view toggle (unified / tester lanes), left rail report rows,
right panel anatomy, unread count badges.

### §10 — Duplicate detection and resolution
Cover: AI-assisted similarity flagging (configurable threshold, default 80%),
manual marking, "DUPLICATE?" badge and inline banner, language rule
(always "Duplicate" never "dupe"), primary report selection (first received
default, Darrin can override), cross-tester vs same-tester duplicate handling,
all linked reporters notified on any status change.

### §11 — Message compose and status updates
Cover: status picker first (Acknowledged / In Progress / Fixed / Won't Fix),
auto-fill template on status selection, template override dropdown,
freeform write custom option, preview, send to all linked reporters,
placeholder substitution rules.

### §12 — Template system
Cover: six default templates (names, status associations, default text),
supported placeholders ([tester name] · [bug title] · [developer name] ·
[bug id] · [version] · [date] · [relay id]), unlimited custom templates,
multiple templates per status, global scope (not per-tester), most-recently-
used pre-selection at compose time, editable + resettable to default.

### §13 — Dropbox sync status and delivery receipts
Cover: four sync states (Connected · Syncing · Waiting to retry · Disconnected),
statusbar always visible, auto-dismissible banner on warning/error,
per-message delivery receipt states (Queued → Uploading → Delivered · Failed),
three-way verbosity toggle (Full detail / Failures only / Off, default Failures
only), Retry now button on failed messages. Ground all Dropbox behavior in
verified applet results (15/15 PASS, app key gyudg4ri3pcay3b, PKCE offline token,
SDK >= 12.0.2).

### §14 — Tester hub view
Cover: My Reports as primary tab, status badges on each report row, Updates
tab with unread badge, update timeline in report detail, New Report trigger.
Tab strip: My Reports · Updates (N) · New Report.

### §15 — Workflow steppers
Cover both steppers with full detail:

Developer stepper (per selected report):
① Received (auto) ━━▶ ② Review ━━▶ ③ Capture (optional) ━━▶ ④ Respond
Steps 3 and 4 non-blocking — can be completed in any order.
When no report selected: neutral state message.

Tester stepper (per active report):
① Record ━━▶ ② Review ━━▶ ③ Send ━━▶ ④ Track
Fully sequential — cannot skip steps.

Status pane copy rule: every idle message names the exact button label
verbatim. Include the canonical examples table from RELAY_SCREEN_C_DESIGN_v1.md.

Visual grammar: same as AM Screen B — numbered circles, connecting arrows
(━━▶), peach active step, green completed (✓), grey pending.

## What to update in existing sections

- §2 Locked Decisions: add D9 (role architecture), D10 (duplicate language
  rule — always "Duplicate")
- §3 Screen Anatomy: add §3.6 Screen 6 — Developer Hub, §3.7 Screen 7 —
  Tester Hub
- §4 Relay Settings: add §4.7 Duplicate detection threshold, §4.8 Delivery
  receipt verbosity, §4.9 Role configuration
- §6 Relationship to Existing Modules: update §6.1 to reference hub layout

## Deliverable

`C:\CODEX PG\CODEX Canonical Specs\RELAY_SPEC_v0.2.md`

Update the master spec index:
`C:\CODEX PG\CODEX Canonical Specs\CODEX_MASTER_SPEC_INDEX.md`

## Tier

Extra-High. Full spec revision, multi-section authoring, grounding in
verified Dropbox behavior, complete consistency check against v0.1.

— Claude Desktop
