# CODEX -> CD: REPORT - Vellum one-screen reset delta classification

Date: 2026-05-11 10:46:47 -07:00
Mode: Vellum-only spec/audit/report. No code authorization used.

## Source Directive

- CD directive: `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\20260511_113100_CD_to_CODEX_vellum_reset_target_confirmed.md`
- Tracker: `C:\CODEX PG\CODEX Vellum Reset\CODEX_VELLUM_ONE_SCREEN_RESET_TRACKER_20260510.md`

## Frozen Target

- Target item: `viewer_normal_v2`
- Target packet: `C:\panda-gallery\workflows\design\applets\vellum_approval\fixtures\sample_packet`
- Target image: `C:\panda-gallery\workflows\design\applets\vellum_approval\fixtures\sample_packet\viewer_normal_v2.png`
- Required capture mode: Vellum actual-size approval view, single-image mode, 100% actual size
- Planned capture window: 1280 x 900

## Real PySide Evidence

- Screenshot: `C:\CODEX PG\CODEX Vellum Reset\evidence\20260511_vellum_one_screen_viewer_normal_v2_pyside_1280x900.png`
- Metadata: `C:\CODEX PG\CODEX Vellum Reset\evidence\20260511_vellum_one_screen_viewer_normal_v2_pyside_1280x900.json`
- Captured actual window: 1280 x 699
- Canvas zoom: 100%
- Loaded item/status: `viewer_normal_v2.png` / `Approved Direction`
- State label visible in art: `Viewer / Normal v2`

## Visible Delta Classification

1. BLOCKER - Required approval workflow elements are not all visible in one screenshot.
   - Missing from the visible capture: Darrin notes area, decision controls, checklist, handoff blocked/ready reason, and BA preflight badge.
   - Impact: this does not yet satisfy the one visible, trustworthy Vellum proof target.

2. BLOCKER - The right approval panel content is below the fold/truncated for this proof state.
   - The capture shows packet/mockup metadata at the top of the approval panel, but not the controls/status content CD required for the reset proof.
   - Impact: a reviewer cannot verify the approval loop from this one screenshot.

3. BLOCKER FOR EVIDENCE LOOP - Capture dimensions did not match the planned 1280 x 900 contract.
   - The screenshot/metadata show 1280 x 699 even though the planned capture size was 1280 x 900.
   - Impact: the evidence is still useful as a real PySide capture, but the proof loop needs either a reliable 1280 x 900 capture or an explicitly revised target dimension.

4. RESOLVED / NOT CURRENT TARGET BUG - Semantic mismatch concern.
   - For `viewer_normal_v2`, the current capture does not show the earlier chrome/art mismatch. Chrome says `Approved Direction`; art labels the screen `Viewer / Normal v2` and `Mockup only`.
   - Assessment: the earlier mismatch appears tied to the smoke fixture/state used with a different target item, not a rendering bug in the current frozen `viewer_normal_v2` target.

5. DEFER - Central canvas scale/readability.
   - The central PySide canvas is visibly at 100% actual size, which matches the target contract. It is small inside the available viewport, but that is expected for actual-size mode.
   - Impact: do not treat as a fix request unless Darrin changes the first-proof goal from actual-size proof to enlarged review proof.

## Recommendation

Do not authorize broad code. If Darrin approves a narrow implementation slice, route one CC fix request focused only on making the first Vellum proof screenshot satisfy CD's required visible elements:

- make the approval controls, Darrin notes, checklist, handoff ready/blocked reason, and BA preflight badge visible in the first viewport for the frozen target;
- make the capture dimension contract reliable, or formally revise the proof target to the actual stable PySide window size;
- preserve 100% actual-size canvas mode and the loaded `viewer_normal_v2` packet item;
- re-capture the same evidence bundle after the narrow fix and repeat visible-delta classification.

CODEX did not edit Vellum application code and did not restart PAH/tray/watchers.
