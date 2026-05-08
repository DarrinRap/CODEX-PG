# CODEX PAH Owner Decisions - 2026-05-06

Status: Decision-ready report, no cleanup performed
Scope: `C:\CODEX PG\CODEX Agent Hub`

## Purpose

Classify PAH artifacts whose release status should not be guessed by Codex. This file does not stage, delete, move, or authorize cleanup.

## Current Evidence

- `CODEX_agent_hub_ui.html` is tracked and currently clean in `git status --short -- "CODEX Agent Hub"`.
- `CODEX mockups/` is untracked and contains PAH health-button mockup HTML/PNG files from 2026-05-05.
- `tmp_capture_pah_header.py` is untracked and is a Playwright screenshot helper for before/after PAH header verification. It writes screenshots under `C:\CODEX PG\CODEX PANDA Collaborator\tmp_pdf_build`, so it is not appropriate to run or include casually under the current PAH-only rule.

## Decisions Needed

| Path | Evidence | Recommended decision | Reason |
| --- | --- | --- | --- |
| `CODEX_agent_hub_ui.html` | Tracked, clean, 206741 bytes, last written 2026-05-06 11:38 | No release action needed | It is not dirty now, so the PAH backend release should not stage or discuss it unless Darrin separately asks for UI work. |
| `CODEX mockups/` | Untracked folder with `pah_health_buttons_straight_line_v1.html`, `pah_health_buttons_straight_line_v1.png`, and `pah_health_buttons_straight_line_live.png` | Park outside release | These are useful visual evidence artifacts, not required for the PAH backend/advisory fix release. Keep them uncommitted unless Darrin wants design evidence preserved. |
| `tmp_capture_pah_header.py` | Untracked temporary Playwright capture helper; targets PAH but writes to Panda Collaborator temp output | Exclude from release; delete later only with approval | It is a task-specific scratch helper and crosses into Panda Collaborator output. Do not include in a PAH-only release. |

## Batch Recommendation

For the PAH excellence release candidate:

- Include no owner-confirmation artifacts by default.
- Leave `CODEX_agent_hub_ui.html` untouched.
- Leave `CODEX mockups/` parked and untracked.
- Leave `tmp_capture_pah_header.py` parked and untracked until Darrin approves deletion.

No files were cleaned, staged, or deleted.
