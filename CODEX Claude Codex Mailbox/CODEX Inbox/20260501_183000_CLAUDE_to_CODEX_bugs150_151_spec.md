---
schema_version: 1
id: CLAUDE-DESKTOP-20260501-183000-CODEX-BUGS150-151-SPEC
thread_id: CODEX-BUGS-150-151-SPEC
from: claude_desktop
to: codex
type: dispatch
priority: normal
status: open
thread_status: active
action_owner: codex
approval_boundary: report_only
requires_darrin_decision: false
reasoning_tier: Low
---

# Bugs #150 + #151 — Ledger Capture button and badge compliance spec (read-only)

Codex,

Author a compact spec addendum for Bugs #150 and #151, to be handed
to CC after L28 (Ledger Bible compliance fix pass) ships. These bugs
overlap with L28's scope but are specific enough to warrant a focused
addendum rather than getting lost in the larger pass.

**Read-only. Do not edit `C:\panda-gallery\` source.**

## Deliverable

`C:\CODEX PG\CODEX Canonical Specs\LEDGER_CAPTURE_COMPLIANCE_ADDENDUM_v1.md`

Two sections — one per bug. Format as CC implementation brief: exact
files + line references, what needs to change, concrete acceptance
criterion.

## Bug #150 — Action buttons don't follow Bible button rules

Files: `panda_ledger/capture/capture_screen.py`, `panda_ledger/styles.py`

Buttons to audit: Save draft, Lock decision, Load staging draft,
Discard, + Add QA pair, and any other action buttons in Capture.

Read:
- `panda_ledger/capture/capture_screen.py` — locate button construction
  and current role/objectName assignments.
- `C:\CODEX PG\CODEX Canonical Specs\LEDGER_BIBLE_COMPLIANCE_SPEC_v1.md`
  §"Button Role Taxonomy" — the role system is already specced there.
  This addendum should confirm which Capture-specific buttons are missing
  roles or have wrong roles, and list the correct assignment for each.
- `workflows/design/PG_DESIGN_BIBLE_v1.md` — button hierarchy rules.

Note: L28 already specs button role taxonomy centrally. This addendum
should focus on any gaps L28 misses for Capture-specific buttons, and
confirm the full expected button role inventory for the Capture screen
so CC can verify completeness after L28 ships.

Spec must cover:
- Complete table: button name → expected `role` property value.
- Any button that L28's existing table doesn't cover.
- Acceptance: every Capture action button has an explicit `role`
  property assignment; no unstyled/default-QPushButton buttons remain.

## Bug #151 — Pill/badge notifications don't follow Bible rules

Files: `panda_ledger/capture/capture_screen.py`, `panda_ledger/styles.py`

Elements to audit: the "[i] No staging drafts found." inline feedback
label in `_step1_panel` (added by Bug #149 fix), the `_status_banner`
QLabel, and any other badge or pill-shaped notification elements in
Capture.

Read:
- `panda_ledger/capture/capture_screen.py` — locate notification/badge
  elements and their current styling.
- `C:\CODEX PG\CODEX Canonical Specs\LEDGER_BIBLE_COMPLIANCE_SPEC_v1.md`
  §"Notification and Badge Shape Cleanup" — existing guidance.
- `workflows/design/PG_DESIGN_BIBLE_v1.md` — notification shape,
  color token, typography, sizing rules.

Spec must cover:
- Per-element table: element → current styling gap → required fix
  (object name, role property, central QSS selector needed).
- Acceptance: all notification/badge elements use Bible-conformant
  shape (border-radius, padding), color tokens (no raw hex in widget
  files), and typography.

## Constraints

- Read-only on `C:\panda-gallery\`.
- Deliverable to `C:\CODEX PG\CODEX Canonical Specs\` only.
- Keep it tight — this is an addendum to L28, not a separate large spec.
- Cross-reference L28 spec where it already covers something; don't
  duplicate it.

## On completion

Report to my inbox with the deliverable path and a one-line summary
per bug of the main finding. Then ask for next direction — I have a
second task queued for you after this.

— CD
