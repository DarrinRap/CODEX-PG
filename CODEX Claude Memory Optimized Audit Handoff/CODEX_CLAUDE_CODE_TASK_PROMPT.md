# CODEX Claude Code Task Prompt - Audit MVP First Slice

You are implementing the first local-only Audit MVP slice in Panda Gallery.

Read only these first:

1. `C:\CODEX PG\CODEX Claude Memory Optimized Audit Handoff\CODEX_READ_ME_FIRST.md`
2. `C:\CODEX PG\CODEX Claude Memory Optimized Audit Handoff\CODEX_SEARCHABLE_INDEX.md`
3. The one chunk Darrin/Codex provides for the current task.

Do not load all project history unless a specific referenced file is needed.

## Current Task

Implement the narrow slice described in the provided chunk. Keep changes small and report exactly:

- Files changed
- Behavior added
- Tests or smoke checks run
- Remaining risks
- Next suggested chunk/task

## Boundaries

- No upload.
- No AI API calls.
- No email sending.
- No PHI workflow.
- No broad refactor.
- Preserve existing PG visual language.
- Preserve existing testing/capture behavior where practical.
- Do not delete evidence files during discard; mark `discarded: true`.

## Required Before Editing

1. Inspect current relevant PG files read-only.
2. Identify the smallest integration point.
3. State the planned file changes.
4. Then implement.

## Required After Editing

1. Run targeted smoke/test commands if available.
2. Verify package/evidence behavior if touched.
3. Report exact limitations.
