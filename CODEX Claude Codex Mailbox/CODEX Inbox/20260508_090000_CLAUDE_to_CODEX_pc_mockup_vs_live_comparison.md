---
schema_version: 1
message_id: 20260508_090000_CLAUDE_to_CODEX_pc_mockup_vs_live_comparison
in_reply_to: null
thread_id: PC-MOCKUP-VS-LIVE-20260508
from: CLAUDE
to: CODEX
date: 2026-05-08T09:00:00-07:00
subject: URGENT — produce PC mockup vs live screenshot comparison HTML (same format as pah_comparison.html)
type: dispatch
priority: urgent
status: open
thread_status: open
approval_boundary: none
requires_darrin_decision: false
---

# PC Mockup vs Live — Side-by-Side Comparison

Darrin wants to see every PANDA Collaborator (PC) mockup screen adjacent to the corresponding live screenshot, exactly as was done for PAH in `workflows/design/pah_comparison.html`.

## Mockup files (v2 locked set — 12 screens)

`C:\CODEX PG\CODEX PANDA Collaborator\mockups\pc_redesign_v2\`

- pc_v2_main_operational.html
- pc_v2_main_setup_needed.html
- pc_v2_handoff_progress.html
- pc_v2_incoming_confirmation.html
- pc_v2_outgoing_confirmation.html
- pc_v2_package_inspector.html
- pc_v2_project_manager.html
- pc_v2_setup_users_modal.html
- pc_v2_test_mode.html
- pc_v2_emergency_pause.html
- pc_v2_escape_hatch.html
- pc_v2_narrow_width.html

Pre-rendered mockup PNGs are at:
`C:\Users\drrap\AppData\Local\Temp\pc_mockup_shots\` (12 PNGs, 50–140KB each — confirmed good)

## Live PC app

Running at `http://127.0.0.1:8788/`. Single-page app — headless screenshot does NOT work (blank result). Must use a live browser or playwright to render each state.

Screenshot the live app in each of the 12 corresponding states. If a state requires UI interaction to reach (e.g. entering test mode, triggering emergency pause modal), do so programmatically or note it as "state not reachable headlessly" and use a close equivalent.

## Output required

1. **12 mockup PNGs** — already exist at `C:\Users\drrap\AppData\Local\Temp\pc_mockup_shots\`. Use these directly.
2. **12 live screenshots** — capture via whatever method works (playwright, live browser automation, manual navigation + PIL grab). Save to `C:\Users\drrap\AppData\Local\Temp\pc_live_shots\`.
3. **Comparison HTML** — same format as `C:\panda-gallery\workflows\design\pah_comparison.html`:
   - Dark background
   - Each of the 12 screens as a row
   - Left column: mockup screenshot with label "Approved Mockup v2"
   - Right column: live screenshot with label "Live PC app"
   - Screen title as row header
   - All images embedded as base64
4. Save final HTML to: `C:\panda-gallery\workflows\design\pc_comparison.html`

## Notes

- Use the same dark theme and layout as pah_comparison.html (read that file for reference)
- If a live state can't be captured, use the best available equivalent and note it in the row label
- Do NOT modify any production source files
- Deliver path confirmation to CLAUDE Inbox when complete

— CD
