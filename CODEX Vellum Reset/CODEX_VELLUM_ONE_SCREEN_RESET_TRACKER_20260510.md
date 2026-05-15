# CODEX Vellum One-Screen Reset Tracker

Created: 2026-05-10
Mode: Vellum only; housekeeping note; no implementation authorization

## Governing Rule

- Hold all work except Vellum until Darrin explicitly says otherwise.
- Stay spec/audit/report only unless Darrin explicitly authorizes code.
- Do not continue PAH, PC, BA, PG demo/seed, mail cleanup, duplicate cleanup, or broad UI/UX work.
- C:\panda-gallery remains read-only reference unless Darrin explicitly authorizes a specific write.
- Do not send implementation-go or commit-go directly to CC; CD owns CC routing.

## First Visible Target

Target screen: Vellum actual-size approval view with one packet item loaded.

This is the smallest trustworthy visible result because it proves Vellum can act as an approval tool, not just an image viewer.

Required visible elements:

- central real PySide image canvas at actual size / 100%
- filename and screen/state label
- current decision/status
- Darrin notes area
- decision controls
- handoff blocked/ready indicator with a plain reason

Explicitly deferred from this first result:

- split-view
- screenshot inbox
- export package generation
- presentation mode
- keyboard decision shortcuts
- version history
- queue filters
- BA integration
- CC routing
- PG product UI changes

## Proof Workflow

1. Freeze one mockup target as the visual contract.
2. Capture the real running PySide Vellum screen at the same window size.
3. Compare mockup target vs real PySide screenshot.
4. Record visible deltas only.
5. Fix only those deltas if/when Darrin authorizes code.
6. Re-capture and repeat until the real screen earns trust.

## Artifact Slots

- Mockup target screenshot: TBD
- Real PySide screenshot: TBD
- Delta report: TBD

## Done Definition

This reset slice is done only when the tracker points to:

- an approved/frozen mockup target screenshot
- a real PySide screenshot of the same Vellum screen
- a short delta report listing remaining visible differences or stating that no material visible deltas remain

## Notes

- HTML mockups are a visual contract, not implementation proof.
- Real PySide screenshots are the evidence source for visible accuracy.
- No broad cleanup, backup, commit, or mailbox coordination was performed as part of this housekeeping step.

## CD-Confirmed Frozen Target — 2026-05-11

Recorded: 2026-05-11 10:44:24 -07:00
Source directive: `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\20260511_113100_CD_to_CODEX_vellum_reset_target_confirmed.md`

- Frozen target item: `viewer_normal_v2`
- Frozen target packet: `C:\panda-gallery\workflows\design\applets\vellum_approval\fixtures\sample_packet`
- Frozen target screenshot/image path: `C:\panda-gallery\workflows\design\applets\vellum_approval\fixtures\sample_packet\viewer_normal_v2.png`
- Required capture mode: Vellum actual-size approval view, single-image mode, 100% actual size
- Planned capture window dimensions: 1280 x 900
- Required visible elements: central canvas at 100%; filename/screen-state label; current decision/status; Darrin notes; decision controls; checklist; handoff blocked/ready reason; BA preflight badge
- Code authorization: none. Steps authorized are freeze, capture, visual delta comparison, and delta classification only.


## Evidence Capture - 2026-05-11

Recorded: 2026-05-11 10:46:47 -07:00

- Mockup target screenshot/image path: `C:\panda-gallery\workflows\design\applets\vellum_approval\fixtures\sample_packet\viewer_normal_v2.png`
- Real PySide screenshot: `C:\CODEX PG\CODEX Vellum Reset\evidence\20260511_vellum_one_screen_viewer_normal_v2_pyside_1280x900.png`
- Real PySide metadata: `C:\CODEX PG\CODEX Vellum Reset\evidence\20260511_vellum_one_screen_viewer_normal_v2_pyside_1280x900.json`
- Delta report: `C:\CODEX PG\CODEX Vellum Reset\CODEX_VELLUM_ONE_SCREEN_DELTA_REPORT_20260511_104647.md`
- CD mailbox report: `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\20260511_104647_CODEX_to_CD_vellum_one_screen_delta_report.md`
- Capture result: real PySide screenshot captured at 100% canvas zoom.
- Requested/planned window: 1280 x 900.
- Actual captured window: 1280 x 699.
- Result classification: one-screen proof not yet satisfied; missing required visible approval workflow elements remain blockers.

## CD Delta Response + Draft Fix Spec - 2026-05-11

Recorded: 2026-05-11 12:47:36 -07:00

- CD response read: `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\20260511_130100_CD_to_CODEX_vellum_delta_response.md`
- Canonical proof dimension revised by CD: 1280 x 699.
- Prior 1280 x 900 plan superseded; the 1280 x 699 evidence is valid.
- Semantic mismatch: resolved / not a current target bug.
- Canvas scale: deferred; 100% actual-size remains required.
- Narrow CC fix authorized by CD for spec drafting only: make all required approval workflow elements visible in first viewport.
- Draft spec for CD review: `C:\CODEX PG\CODEX Vellum Reset\CODEX_VELLUM_ONE_SCREEN_CC_FIX_SPEC_DRAFT_20260511_124736.md`
- CD mailbox copy: `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\20260511_124736_CODEX_to_CD_vellum_one_screen_cc_fix_spec_draft.md`
- CODEX did not route to CC and did not edit app code.

## Spec Approved; CODEX Hold - 2026-05-11

Recorded: 2026-05-11 12:53:48 -07:00

- CD approval/hold directive read: `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\20260511_155000_CD_to_CODEX_vellum_one_screen_spec_approved.md`
- Result: CODEX draft spec approved as submitted.
- Scope remains: ApprovalReviewPanel layout/ordering only; no broader polish, no packet changes, no non-Vellum lanes.
- Sequencing: CC Vellum fix dispatch is queued behind state 06; estimated queue position next.
- CODEX state: hold on all Vellum tracks until CC fix is shipped and evidence is returned.
- ACK sent to CD: `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\20260511_125348_CODEX_to_CD_vellum_spec_approval_hold_ack.md`
- CODEX did not route to CC, edit code, or issue commit-go.

## Full Test + BA Validation Report - 2026-05-11

Recorded: 2026-05-11 14:20:59 -07:00

- Darrin authorized full Vellum test/report pass.
- Evidence folder: `C:\CODEX PG\CODEX Vellum Reset\evidence\full_test_20260511`
- Pytest Vellum selection: PASS, 149 passed / 4 xfailed / 1055 deselected.
- BA Vellum plain: trusted with findings, 0 fail / 146 warn / 32 unknown / 9 evidenced.
- BA validator gate: PASS verdict `report_trusted_with_findings`, no reproduction drift on plain report.
- BA mockup preflight: `fix_before_showing`, warning `BA-MOCKUP-PREFLIGHT-0005` about missing approval/review context in package naming.
- Direct applet design lint: 0 errors / 24 warnings / 10 info.
- Vellum smoke script: FAIL, 20/31 passed, 11 failed, aborts on missing `MarkupToolbar._width_combo`.
- Report to CD: `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\20260511_142059_CODEX_to_CD_vellum_full_test_ba_validation_report.md`
- Local report: `C:\CODEX PG\CODEX Vellum Reset\CODEX_VELLUM_FULL_TEST_AND_BA_REPORT_20260511_142059.md`
- CODEX made no app code changes and issued no CC commit-go.

## CD Test/BA Routing Decisions - 2026-05-11

Recorded: 2026-05-11 14:25:10 -07:00

- CD routing/ruling read: `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\20260511_200500_CLAUDE_to_CODEX_vellum_test_report_routing.md`
- Pytest Vellum selection: accepted as regression floor; no action.
- BA Vellum: accepted as trusted-with-findings, not BA-green; broad BA cleanup deferred until after one-screen proof is fixed and re-captured.
- Smoke script: accepted as stale validation infrastructure; not a ship gate in current form; CD will add BUGS.md entry / future CC validation dispatch after multi-select ships.
- Mockup preflight warning `BA-MOCKUP-PREFLIGHT-0005`: WAIVED for the Vellum approval fixture because ApprovalReviewPanel supplies review context.
- One-screen ApprovalReviewPanel fix: still queued after multi-select cluster #283/#279/#280; no queue priority change.
- ACK sent to CD: `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\20260511_142510_CODEX_to_CD_vellum_test_report_routing_ack.md`
- CODEX remains on hold for this thread until one-screen fix is dispatched/shipped and evidence returns.
- CODEX did not edit app code, `ba_audit_manifest.json`, BUGS.md, or issue CC routing/commit-go.
