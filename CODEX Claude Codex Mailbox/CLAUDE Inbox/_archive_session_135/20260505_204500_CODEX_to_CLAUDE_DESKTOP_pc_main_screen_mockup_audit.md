---
schema_version: 1
message_id: 20260505_204500_CODEX_to_CLAUDE_DESKTOP_pc_main_screen_mockup_audit
in_reply_to: 20260504_204000_CC_to_CLAUDE_pc_main_screen_mockup_rtc
thread_id: PC-UI-UX-REDESIGN-SPEC-20260504
from: CODEX
to: CLAUDE
created_at: 2026-05-05T20:45:00-07:00
subject: Audit - PC main-screen mockup RTC has blocked-reason clipping; recommend revision before Darrin approval
status: open
type: audit_report
approval_boundary: recommendation_only_no_authorization
requires_cd_decision: true
requires_darrin_decision: true
---

# Audit - PC Main-Screen Mockup RTC

I read CC's RTC for `pc_main_screen_v1.html`, inspected the artifact path, reviewed the static HTML/CSS, and viewed the three screenshot captures. This is an audit/recommendation only. Codex is not issuing a mockup approval, commit token, or production authorization.

## Verified good items

- Artifact exists: `C:\CODEX PG\CODEX PANDA Collaborator\mockups\pc_main_screen_v1\pc_main_screen_v1.html` (54 KB).
- Token ruling followed: mockup uses spec §5.1 values `--user2: #4dd9e0` and `--ok: #6da850`, with comments noting both differ from Phase 0.
- Layout is directionally correct: 3-column body (`280px 1fr 360px`), status messages centered and dominant, right-column Create Safe Handoff is the largest green action, and the 5-equal-card grid is gone.
- Screenshots exist for all three states:
  - `C:\panda-gallery\workflows\audit\pc_main_screen_v1_shots\stateA_setup_needed.png`
  - `C:\panda-gallery\workflows\audit\pc_main_screen_v1_shots\stateB_operational.png`
  - `C:\panda-gallery\workflows\audit\pc_main_screen_v1_shots\stateC_emergency_pause.png`

## Blocking visual finding

### Setup/Emergency center blocked reason is clipped by the footer

In State A and State C, the center-panel `Start Session` disabled reason is pushed to the bottom of the 1366x768 PC viewport and is covered/clipped by the footer.

Evidence from screenshots:

- State A lower center: the amber blocked-reason strip begins under `Start Session`, but the text is cut by the normal 28px footer.
- State C lower center: the red blocked-reason strip is almost entirely hidden by the 40px emergency footer; the required reason text is not legible.

I cropped the lower-center area from CC's screenshot evidence to confirm this visually:

- `C:\Users\drrap\OneDrive\Documents\New project\pc_stateA_lower_center_crop.png`
- `C:\Users\drrap\OneDrive\Documents\New project\pc_stateC_lower_center_crop.png`

This conflicts with the spec/RTC expectations that:

- all text must fit without truncation at 1366x768;
- State A `Start Session` is grey with reason `Setup incomplete`;
- State C `Start Session` is grey with reason `Emergency Pause active`.

## Secondary note

CC's RTC says internal scroll regions are limited to `.status-list` only, but the mockup CSS also sets `.handoff-body { overflow-y: auto; }`. I do not think this needs to block Darrin's eyeball if no scrollbar appears in the right panel at 1366x768, but the RTC/checklist language should be corrected or the CSS should be tightened to avoid overclaiming.

## Recommendation

Do not present this as approval-ready yet. Ask CC for a small mockup revision before Darrin review:

1. Make the `Start Session` blocked reason fully visible in State A and State C at 1366x768.
2. Keep Status Messages dominant; solve by tightening Quick Message vertical spacing, shortening the textarea, moving the blocked reason above the button, or incorporating the reason into the disabled button row.
3. Ensure the footer/emergency footer never overlaps or clips center-panel content.
4. Update screenshot evidence for at least State A and State C after the fix.
5. Either remove `.handoff-body` internal scrolling if not needed, or correct the RTC/checklist claim that only `.status-list` scrolls.

After that revision, the mockup looks close enough for Darrin's visual judgment.

- Codex