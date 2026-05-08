# CODEX Chat 22 Handoff

Generated: 2026-05-06 09:58 -07:00

## Read First In Next Chat

1. `C:\CODEX PG\CODEX Docs\CODEX_PROJECT_MEMORY.md`
2. `C:\CODEX PG\CODEX Docs\CODEX_CURRENT_HANDOFF.md`
3. `C:\CODEX PG\CODEX Docs\CODEX_LAST_AUTOMATED_HANDOFF.md`
4. This file: `C:\CODEX PG\CODEX Docs\CODEX_CHAT22_HANDOFF_20260506_0958.md`

## Critical Current Rules

- Do not touch UI or UX files. Darrin said: "dont touch the ui or ux EVER!!!!"
- Do not make UX/UI design feature recommendations for any app unless Darrin explicitly approves that exact design/recommendation work.
- For visual previews, open the target directly in Microsoft Edge. Do not rely on local clickable/web links; Darrin said the links are broken.
- Do not send implementation-go or commit-go tokens directly to CC. If Darrin says "go" for CC work in Codex chat, route it to Claude Desktop/CD through `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox`.
- CD owns formal CC authorization tokens. Codex can read mail, audit, recommend, summarize, and route status, but not authorize CC implementation/commits.
- `C:\panda-gallery` remains read-only unless Darrin explicitly authorizes a specific write.
- Do not touch Relay files unless explicitly authorized.
- Do not clean, stage, commit, revert, or archive parked dirty files unless explicitly authorized.

## Handoff Action Taken

- Ran `C:\CODEX PG\CODEX Handoff Automation\CODEX_run_handoff.ps1 -Mode ResumePrompt`.
- This updated generated handoff/resume docs only.
- Full `Handoff` mode was intentionally not run because it invokes `CODEX_backup_to_github.ps1`, which runs `git add -A` and would stage all dirty files, including PAH UI changes.
- No backup commit was created.
- No push was performed.

## Current Git State To Preserve

`C:\CODEX PG`

```text
## main...origin/main
 M "CODEX Agent Hub/CODEX_agent_hub_ui.html"
 M "CODEX Agent Hub/CODEX_run_smoke_tests.py"
 D "CODEX Claude Codex Mailbox/CLAUDE Inbox/20260503_152000_CLAUDE_to_CODEX_ba_audit_layout_fix.md"
 D "CODEX Claude Codex Mailbox/CLAUDE Inbox/20260503_152500_CLAUDE_to_CODEX_ba_audit_module_parked.md"
 D "CODEX Claude Codex Mailbox/CLAUDE Inbox/20260503_222111_CODEX_to_CLAUDE_ba_fix_dispatch_audit-module.md"
 D "CODEX Claude Codex Mailbox/CLAUDE Inbox/20260504_013600_CODEX_to_CLAUDE_pah_ba_dispatch_diagnostic_disposition.md"
 D "CODEX Claude Codex Mailbox/CLAUDE Inbox/20260504_094335_CODEX_to_CLAUDE_DESKTOP_pah-follow-up-please-fully-read-cc-inbox-i.md"
 D "CODEX Claude Codex Mailbox/CLAUDE Inbox/20260504_104007_CODEX_to_CLAUDE_DESKTOP_mail-read-ack.md"
 D "CODEX Claude Codex Mailbox/CLAUDE Inbox/20260504_152300_CODEX_to_CLAUDE_DESKTOP_protocol_ack_and_ba_status_route.md"
 D "CODEX Claude Codex Mailbox/CLAUDE Inbox/20260504_153400_CODEX_to_CLAUDE_DESKTOP_tracker_mockup_and_ba_mail_readout.md"
 ?? "CODEX Agent Hub/CODEX mockups/"
 ?? "CODEX Agent Hub/tmp_capture_pah_header.py"
 ?? "CODEX Canonical Specs/PC_DATA_SAFETY_BACKUP_SPEC_v1.0.md"
 ?? "CODEX Canonical Specs/PC_HANDOFF_PROGRESS_SPEC_v1.1.md"
 ?? "CODEX Canonical Specs/PC_HANDOFF_PROGRESS_SPEC_v1.md"
 ?? "CODEX Canonical Specs/PC_MAIN_SCREEN_REDESIGN_SPEC_v1.0.md"
 ?? "CODEX Canonical Specs/PC_REPO_PROTECTION_SPEC_v1.0.md"
 ?? "CODEX Claude Codex Mailbox/CLAUDE Inbox/_archive_session_135/"
 ?? "CODEX Claude Codex Mailbox/CODEX Inbox/20260504_002100_CLAUDE_to_CODEX_pc_handoff_progress_spec_fyi.md"
 ?? "CODEX Claude Codex Mailbox/CODEX Inbox/20260504_002500_CLAUDE_to_CODEX_pc_handoff_spec_conflict_audit.md"
 ?? "CODEX Claude Codex Mailbox/CODEX Inbox/20260504_003000_CLAUDE_to_CODEX_pc_handoff_spec_v1.1_notify.md"
 ?? "CODEX Claude Codex Mailbox/CODEX Inbox/20260504_003600_CLAUDE_to_CODEX_alert_ack.md"
 ?? "CODEX Claude Codex Mailbox/CODEX Inbox/20260504_004100_CLAUDE_to_CODEX_phase0_protocol_ack.md"
 ?? "CODEX Claude Codex Mailbox/CODEX Inbox/20260504_004600_CLAUDE_to_CODEX_schema_ack.md"
 ?? "CODEX Claude Codex Mailbox/CODEX Inbox/20260504_005600_CLAUDE_to_CODEX_phase1_audit_ack.md"
 ?? "CODEX Claude Codex Mailbox/CODEX Inbox/20260504_007200_CLAUDE_to_CODEX_phase1_revision_ack.md"
 ?? "CODEX Claude Codex Mailbox/CODEX Inbox/20260504_007900_CLAUDE_to_CODEX_phase2_phase3_audit_ack.md"
 ?? "CODEX Claude Codex Mailbox/CODEX Inbox/20260504_008200_CLAUDE_to_CODEX_phase4_phase5_ack.md"
 ?? "CODEX Claude Codex Mailbox/CODEX Inbox/20260505_003100_CLAUDE_to_CODEX_session134_audit_ack.md"
 ?? "CODEX PANDA Collaborator/mockups/pc_main_screen_v1/RELAY_VISUAL_APPROVAL.md"
 ?? "CODEX PANDA Collaborator/tmp_pdf_build/"
```

`C:\panda-gallery`

```text
## main...origin/main
 M workflows/audit/PG_TASK_QUEUE_v1.md
```

Do not alter either dirty tree without explicit instruction from Darrin.

## PAH Regression Context

- Darrin reported a PAH header graphical glitch where `QUEUE` was clipped.
- A visual mockup was created and opened in Edge.
- Production PAH UI was then touched and Darrin reported a major regression.
- Darrin then gave a hard rule: Codex must not touch UI or UX ever.
- Remaining dirty PAH files are `C:\CODEX PG\CODEX Agent Hub\CODEX_agent_hub_ui.html` and `C:\CODEX PG\CODEX Agent Hub\CODEX_run_smoke_tests.py`.
- Do not revert, fix, commit, stage, or further inspect these as implementation work unless Darrin explicitly says to do that despite the UI/UX rule.

## Safe Next Action

In the new chat, acknowledge the handoff and ask what non-UI/UX work Darrin wants next, or read mail/status if requested. Avoid UI/UX recommendations and avoid UI/UX implementation.
