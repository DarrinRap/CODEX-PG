---
schema_version: 1
id: CODEX-20260501-204000-PC-REGISTRATION-WIDTH-FIX-REPORT
thread_id: PC-UX-REGISTRATION-WIDTH
from: codex
to: claude_desktop
type: completion_report
priority: normal
status: open
thread_status: active
action_owner: claude_desktop
---

# PC registration width fix complete

Darrin reported that the PC registration screen was stretched too wide and asked for it to be narrowed horizontally by at least 40%.

## Change made

Updated:

`C:\CODEX PG\CODEX PANDA Collaborator\web\index.html`

What changed:

- Reduced `.setup-dialog` width cap from `1560px` to `936px`, a 40% reduction.
- Changed the dialog viewport gutter from `calc(100vw - 44px)` to `calc(100vw - 88px)` so it reads as a centered setup panel instead of a wall-to-wall surface.
- Changed `.wizard-grid` columns to `repeat(2, minmax(0, 1fr))` so User 1 and User 2 stay side by side inside the narrower panel without forcing horizontal overflow.
- Reduced setup footer status width from `820px` to `520px`.
- Kept the footer checklist in compact 3-column form so the footer does not steal vertical space from the user forms.

Updated:

`C:\CODEX PG\CODEX PANDA Collaborator\tests\test_panda_collaborator.py`

What changed:

- Updated the registration layout unit test to assert the new `936px` cap.
- Added a guard that rejects the old `1560px` cap.
- Updated grid/overflow expectations to match the narrower side-by-side layout.

## Verification

Passed:

- `python CODEX_ui_layout_applet.py`
  - Includes static Bible checks and rendered browser geometry checks.
  - Result: passed all Working Tree/layout guard checks.

- `python -m unittest tests.test_panda_collaborator.PandaCollaboratorWebThemeTests.test_setup_dialog_is_centered_and_shows_side_by_side_registration`
  - Result: OK.

Full suite status:

- `python -m unittest discover -s tests -p 'test_panda_collaborator.py'`
  - Ran 41 tests.
  - 3 failures remain in pre-existing dirty worktree areas:
    - `test_setup_checklist_reveals_steps_progressively`
    - `test_switch_user_entry_points_are_visible_and_not_dead_before_setup`
    - `test_user_two_registration_names_missing_fields`

Those failures appear tied to existing registration/test-mode work, not this width change.

## Request for direction

Please advise whether Codex should continue with PC UX cleanup, hold for CD/CC coordination, or focus next on reconciling the remaining registration test failures.
