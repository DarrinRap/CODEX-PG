---
name: codex-pg-claude-task-writer
description: Use when converting Panda Gallery specs, Codex recommendations, UI mockups, code reviews, bugs, or audit MVP plans into precise Claude / Claude Code prompts. Produces scoped implementation prompts with files, boundaries, acceptance criteria, verification steps, and handoff requirements so Claude can safely work in C:\panda-gallery.
metadata:
  short-description: Write safe, scoped Claude prompts for Panda Gallery work
---

# CODEX PG Claude Task Writer

## Purpose

Use this skill to turn project knowledge into Claude-ready prompts. The output should let Claude implement or review one focused piece of Panda Gallery work without guessing scope, overwriting unrelated changes, or drifting away from the project plan.

A good Claude prompt is specific enough to protect the codebase and flexible enough to let Claude follow the existing implementation patterns.

## Core Rule

One prompt should usually ask for one coherent change.

Avoid prompts that combine UI redesign, schema design, database migration, bug fixes, tests, and documentation in one request. Split those into a sequence.

## Claude Workspace Assumptions

Claude normally works in:

`C:\panda-gallery`

Codex-owned reference and planning artifacts live in:

`C:\CODEX PG`

When writing a prompt for Claude, clearly say which files are source material and which files Claude may edit.

## Standard Claude Prompt Structure

Use this structure unless the user asks for a different form:

```text
Claude, work in C:\panda-gallery.

Goal:
[One or two sentences describing the result.]

Read first:
- [Relevant live file/spec/bug/handoff paths]

Scope:
- [Allowed files or modules]
- [Allowed behavior changes]

Do not:
- [Explicit boundaries]
- [Unrelated refactors to avoid]

Implementation requirements:
- [Specific behavior]
- [Architecture expectations]
- [Style expectations]

Acceptance criteria:
- [Observable pass/fail results]

Verification:
- [Commands/manual smoke steps/output files to inspect]

Handoff:
- Summarize changed files.
- Summarize verification performed.
- Note any risks or follow-up work.
```

## Prompt Writing Workflow

1. Identify the exact desired outcome.
2. Locate the relevant source-of-truth artifacts.
3. Decide whether this is design, schema, implementation, test, review, or fix work.
4. Limit scope to the smallest sensible module or workflow.
5. Include concrete files Claude should read first.
6. Include files Claude may edit if known.
7. Include files Claude should not edit if risk is high.
8. Add acceptance criteria that can be checked.
9. Add verification steps.
10. If the task follows a Codex review, quote the finding in summarized form rather than asking Claude to infer it.

## Source Material To Prefer

Use the newest applicable source material:

- Current live repo: `C:\panda-gallery`
- Current handoff: `C:\panda-gallery\HANDOFF.md` when Claude is implementing live app work
- Current bugs: `C:\panda-gallery\BUGS.md`
- Project style/rules: `C:\panda-gallery\STYLE.md` and relevant skill/rule files if present
- Codex memory: `C:\CODEX PG\CODEX Docs\CODEX_PROJECT_MEMORY.md`
- Codex current handoff: `C:\CODEX PG\CODEX Docs\CODEX_CURRENT_HANDOFF.md`
- Codex review recommendations: `C:\CODEX PG\CODEX Claude Review Recommendations\CODEX_CLAUDE_CODE_QUALITY_RECOMMENDATIONS.md`
- Codex codebase orientation: `C:\CODEX PG\CODEX Codebase Orientation\CODEX_PG_CODEBASE_ORIENTATION_SUMMARY.md`
- Codex spec review: `C:\CODEX PG\CODEX Specification Review\CODEX_SPECIFICATION_REVIEW_REPORT.md`
- Codex UI mockups/storyboards when the task is visual.

## Boundaries To Include Often

For live Panda Gallery code prompts, usually include:

- Do not rewrite large files wholesale.
- Do not mix unrelated cleanup into this change.
- Preserve existing user-facing behavior unless explicitly changing it.
- Preserve session/result/evidence data compatibility.
- Keep UI dense, modern, and consistent with existing Panda Gallery patterns.
- Add focused tests for pure logic when practical.
- If a manual UI smoke test is needed, document the exact path.

## Common Prompt Types

### Implementation Prompt

Use for one feature or bug fix.

Include:

- goal,
- read-first files,
- files likely to edit,
- exact behavioral requirements,
- acceptance criteria,
- tests or smoke steps.

### Review-Fix Prompt

Use after Codex reviews Claude's code.

Include:

- the finding,
- why it matters,
- exact affected file/line if available,
- what to change,
- what not to broaden,
- verification.

### UI Mockup Prompt

Use when visual behavior is ambiguous.

Include:

- target screen/state,
- user workflow,
- constraints from existing UI vocabulary,
- screenshots/mockups to inspect,
- states to show,
- sizing and density requirements.

### Schema/Contract Prompt

Use before audit/backend implementation.

Include:

- contract purpose,
- consumers/producers,
- versioning rule,
- required fields,
- example JSON,
- validation expectations,
- migration/non-goals.

## Acceptance Criteria Pattern

Make acceptance criteria observable:

- A file exists at a specific path.
- A function returns a specific structure.
- A JSON file contains required keys.
- A UI element remains visible at a specific narrow width.
- A command passes.
- A manual smoke flow has explicit steps and expected outcome.

Avoid vague criteria like:

- make it cleaner,
- improve the UI,
- modernize the code,
- handle edge cases.

Translate those into specific checks.

## Good Claude Prompt Ending

End prompts with this style of handoff request:

```text
At the end, report:
- files changed,
- tests or smoke checks run,
- any behavior you intentionally left unchanged,
- any follow-up risks.
```

## Recommended Sequencing For Testing + Audit MVP

When creating Claude tasks for the audit MVP, prefer this order:

1. Master spec index.
2. Session package manifest schema.
3. Evidence object schema.
4. Local package builder.
5. Transfer adapter boundary.
6. AI issue schema and extraction harness.
7. PG approval queue.
8. Shared email draft/send workflow.
9. Searchable archive.

Do not ask Claude to build Dropbox, AI extraction, dashboard, email, and archive together.

## Output Expectations

When Darrin asks for a Claude prompt, provide:

- a short explanation of why this prompt is scoped that way,
- the prompt in a copy-ready text block,
- optional follow-up prompt only if it is clearly the next step.

Keep the copy-ready prompt clean. Do not mix commentary inside it.
