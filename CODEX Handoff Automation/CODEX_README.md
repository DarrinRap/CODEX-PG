# CODEX Handoff Automation

Project-local shortcut system for automating Codex handoff and backup.

## Double-click shortcuts

- `CODEX_HANDOFF.cmd`: update handoff snapshot, generate resume prompt, commit, and push to GitHub.
- `CODEX_CHECKPOINT.cmd`: same workflow, used during active work.
- `CODEX_BACKUP.cmd`: run GitHub backup only after refreshing generated files.
- `CODEX_RESUME_PROMPT.cmd`: regenerate and open the fresh-chat resume prompt.

## Trigger words in chat

- `CODEX HANDOFF`
- `CODEX CHECKPOINT`
- `CODEX BACKUP`
- `CODEX RESUME PG`

## Main script

`CODEX_run_handoff.ps1`

This script writes only under `C:\CODEX PG` and uses the existing GitHub backup script.
