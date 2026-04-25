---
name: codex-pg-project-orientation
description: Use when working on the Panda Gallery / PG project, especially at the start of a fresh Codex chat, after a handoff, when asked to resume, when project boundaries matter, or before reading specs/code. Loads Codex project memory, current handoff, live-source boundaries, GitHub backup expectations, and the minimum relevant context for the user's newest request.
metadata:
  short-description: Orient Codex to Panda Gallery project state and boundaries
---

# CODEX PG Project Orientation

## Purpose

Use this skill before substantive Panda Gallery work. It keeps Codex aligned with the project layout, live-source boundaries, handoff process, and current durable memory.

This skill is intentionally procedural. Do not turn orientation into a broad reread of everything. Read the minimum durable context needed for the user's newest request.

## Non-Negotiable Project Boundaries

- Codex-owned work belongs under `C:\CODEX PG`.
- New Codex-created folders should start with `CODEX`.
- The live Panda Gallery / Claude workspace is `C:\panda-gallery`.
- Treat `C:\panda-gallery` as read-only unless Darrin explicitly asks Codex to edit it.
- The local Claude data copy is `C:\CODEX PG\CODEX CLAUDE PG DATA`.
- Do not push the local Claude data copy to GitHub.
- `C:\CODEX PG\CODEX CLAUDE PG DATA` should remain ignored by git.
- When meaningful Codex artifacts change, run the Codex GitHub backup script if allowed.

## Default Read-First Files

For a normal fresh start or resume, read these first:

1. `C:\CODEX PG\CODEX Docs\CODEX_PROJECT_MEMORY.md`
2. `C:\CODEX PG\CODEX Docs\CODEX_CURRENT_HANDOFF.md`

Then read only what the request requires:

- Codebase orientation: `C:\CODEX PG\CODEX Codebase Orientation\CODEX_PG_CODEBASE_ORIENTATION_SUMMARY.md`
- Claude recommendations: `C:\CODEX PG\CODEX Claude Review Recommendations\CODEX_CLAUDE_CODE_QUALITY_RECOMMENDATIONS.md`
- Spec review: `C:\CODEX PG\CODEX Specification Review\CODEX_SPECIFICATION_REVIEW_REPORT.md`
- UI storyboards: `C:\CODEX PG\CODEX Interface Storyboards`
- Visual mockups: `C:\CODEX PG\CODEX Visual Mockups`
- Read-only inventory: `C:\CODEX PG\CODEX Panda Gallery Readonly Reference`

## Orientation Workflow

1. Restate the user's newest request in one sentence.
2. Confirm whether the task is analysis-only, artifact creation under `C:\CODEX PG`, or live code work.
3. Read `CODEX_PROJECT_MEMORY.md` and `CODEX_CURRENT_HANDOFF.md` unless this has already happened in the current turn.
4. If code context is needed, read from `C:\panda-gallery` read-only or from the copied reference data.
5. Identify which project artifacts are source of truth for the task.
6. If edits are needed, keep them inside `C:\CODEX PG` unless Darrin explicitly authorizes another location.
7. After creating meaningful artifacts, update memory/handoff if the result should survive a fresh chat.
8. Run GitHub backup when appropriate.

## Current High-Level Project Facts

- Panda Gallery is a desktop Python application.
- The live app has a guided testing/capture system, screenshots, audio capture, local transcription, result JSON, and session-aware region capture.
- The Testing + Audit MVP should define durable contracts before adding Dropbox transfer, AI triage, dashboard approval, shared email, or archive/search workflows.
- Current recommended next architecture work centers on package/evidence/issue/approval/archive schemas and small testable modules.

## Handoff Trigger Words

Recognize these Darrin-level triggers:

- `CODEX HANDOFF`: update handoff snapshot, generate resume prompt, run GitHub backup.
- `CODEX CHECKPOINT`: same workflow mid-project.
- `CODEX BACKUP`: run GitHub backup only.
- `CODEX RESUME PG`: fresh-chat startup; read memory and current handoff first.

## GitHub Backup

Normal backup command:

`& 'C:\CODEX PG\CODEX Automation\CODEX_backup_to_github.ps1'`

Remote:

`https://github.com/DarrinRap/CODEX-PG.git`

After successful stage, commit, or push actions, emit the Codex desktop git directives in the final answer when applicable.

## Response Style

When orienting Darrin, be concise and specific:

- Say what you read.
- Say what you learned.
- Say what the next action is.
- Do not bury him in internal context unless he asks for detail.
