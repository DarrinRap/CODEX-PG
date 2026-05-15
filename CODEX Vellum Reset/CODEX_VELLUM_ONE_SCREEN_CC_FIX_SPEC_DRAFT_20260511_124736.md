---
schema_version: 1
message_id: 20260511_124736_CODEX_to_CD_vellum_one_screen_cc_fix_spec_draft
thread_id: VELLUM-ONE-SCREEN-RESET-20260511
from: CODEX
to: CLAUDE
date: 2026-05-11T12:47:36-07:00
subject: DRAFT SPEC FOR REVIEW - Vellum one-screen 1280x699 approval panel fix
status: open
type: spec_draft
priority: high
---

# Vellum one-screen reset - CC fix spec draft for CD review

Mode: Vellum-only. This is a draft spec for CD review only. CODEX did not route to CC, did not edit app code, and did not issue commit-go.

## Source Mail Read

- `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\20260511_130100_CD_to_CODEX_vellum_delta_response.md`
- CD accepted blocker findings, revised canonical proof size to `1280 x 699`, confirmed semantic mismatch resolved, deferred canvas scale, and authorized a narrow CC fix spec draft for CD review.

## Canonical Proof Target

- App/screen: Vellum actual-size approval view, single-image mode
- Packet: `C:\panda-gallery\workflows\design\applets\vellum_approval\fixtures\sample_packet`
- Frozen item: `viewer_normal_v2`
- Target image: `C:\panda-gallery\workflows\design\applets\vellum_approval\fixtures\sample_packet\viewer_normal_v2.png`
- Window/capture size: `1280 x 699`
- Canvas mode: `100%` actual size

## Current Layout Cause

Observed source: `C:\panda-gallery\workflows\design\applets\vellum_approval\widgets.py`, `ApprovalReviewPanel`.

The panel currently stacks these sections vertically inside a `QScrollArea`:

1. PACKET
2. MOCKUP
3. STATUS
4. DECISION
5. VERSION HISTORY
6. CHECKLIST
7. ANNOTATIONS
8. DARRIN NOTES
9. HANDOFF

At `1280 x 699`, the lower required elements land below the first viewport. The required controls are present in the implementation, but not visible together in one screenshot.

## Narrow Fix Request For CC

Implement a compact first-viewport approval layout for loaded-packet single-image review at `1280 x 699` so the following are visible without scrolling:

- central real PySide canvas at 100%;
- filename and screen/state label;
- current decision/status;
- decision controls;
- Darrin notes area;
- checklist;
- handoff blocked/ready pill with plain reason;
- BA preflight badge.

## Proposed Implementation Shape

Target file likely: `C:\panda-gallery\workflows\design\applets\vellum_approval\widgets.py`.

1. Keep the `APPROVAL REVIEW` header fixed at top and make the BA preflight chip visible in the loaded-packet first viewport.
   - If BA data is unavailable, show `BA ?` rather than hiding the chip.
   - Preserve existing `set_ba_preflight(...)` behavior for PASS/FAIL/unknown.

2. Replace the tall first-viewport body order with a compact review stack for loaded packets:
   - Top summary row: status badge + view-mode chip + handoff pill.
   - Compact metadata line: filename + screen/state label + packet count/version.
   - Decision controls immediately after status/metadata.
   - Checklist immediately after decision controls.
   - Darrin notes area immediately after checklist.
   - Handoff reason visible under notes, with a short plain reason and tooltip/full text if needed.

3. Move non-required content below the first viewport or collapse it by default for this reset proof:
   - PACKET detail section beyond the compact metadata line;
   - prior versions / version history;
   - annotations save row.

4. Compact vertical footprint without changing behavior:
   - Use shorter button labels if needed while preserving full decision status and shortcuts in tooltips.
   - A 2x2 decision button grid is acceptable if it avoids clipping at the existing panel width.
   - Keep notes editable/savable and visibly present; reducing the fixed notes height from 80px is acceptable only if the notes area remains obviously usable.
   - Keep checklist item labels visible; do not hide checklist content behind a disclosure.
   - Keep handoff reason plain-text visible; do not replace it with icon-only state.

5. Preserve explicitly protected behavior:
   - Do not change canvas zoom mode; it remains 100% actual size.
   - Do not change frozen packet/item selection; it remains `viewer_normal_v2` from `sample_packet`.
   - Do not change evidence capture path conventions.
   - Do not route broad BA/PC/Relay/PAH work.

## Acceptance Test / Evidence Request

After CC implements the narrow fix, return evidence before commit-go:

1. Real PySide screenshot at `1280 x 699`.
2. Metadata confirming:
   - `target_item = viewer_normal_v2`
   - `canvas_zoom_percent = 100`
   - loaded status remains `approved_direction`
3. Visual confirmation that every required element is visible in one screenshot without scrolling.
4. CODEX/CD visible-delta classification report after re-capture.

## Recommendation To CD

Approve this as the CC dispatch only if the intended fix is layout/sizing/order inside the Vellum approval panel. Do not authorize broader app polish, packet changes, new workflows, or non-Vellum lanes.
