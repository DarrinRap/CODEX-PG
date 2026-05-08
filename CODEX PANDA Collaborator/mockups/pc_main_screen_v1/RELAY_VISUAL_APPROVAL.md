---
# PC MAIN SCREEN VISUAL APPROVAL
# Version: v1.1
# Locked: 2026-05-04
# Approver: Darrin (PandaPerio)

## Approved mockup

File: C:\CODEX PG\CODEX PANDA Collaborator\mockups\pc_main_screen_v1\pc_main_screen_v1.html
States: A (Setup needed) / B (Operational) / C (Emergency Pause) / D (Registration modal)

## Approval record

Darrin reviewed all four states live in browser at 1366×768 and stated "all approved."

Approved elements:
- 3-column layout (280px left / flex-grow center / 360px right)
- Status Messages as dominant center surface (~70% of center height)
- User identity sections (amber for User 1, cyan for User 2) as collapsible left column panels
- Working Tree section compact in left column
- Create Safe Handoff as 48px dominant primary action in right panel
- Last Package collapsible (28px collapsed strip)
- Saves-on-blur Quick Message (no explicit Save Message button)
- 2-line stacked blocked-reason inside disabled Start Session and Create Safe Handoff buttons
- State D registration modal with side-by-side User 1/User 2 forms
- Emergency Pause footer band (40px red) with Clear Pause action
- Identity color usage (border stripe, dot, name text only — never button fill)
- Token values per spec §5.1: --user2 #4dd9e0, --ok #6da850

## This mockup supersedes

- All previous pc_redesign_v1 main operational mockups
- The 8-phase planning RTC (revised plan required before Phase 2 implementation)
- Phase 2 "setup modal + hub cards" as previously scoped (now re-scoped to 3-column layout)

## Implementation contract

CC must implement web/index.html to match this mockup exactly.
Any deviation from the approved layout must be flagged to CD and approved by Darrin before shipping.
