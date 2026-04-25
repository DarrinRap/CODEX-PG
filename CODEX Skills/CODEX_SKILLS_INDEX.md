# CODEX PG Skills Index

Created for the Panda Gallery project under `C:\CODEX PG`.

These are project-owned skill source files. They are designed to keep Codex consistent when working with Panda Gallery, Claude handoffs, code review, and implementation prompts.

## Skills Created

### CODEX PG Project Orientation

Path:

`C:\CODEX PG\CODEX Skills\CODEX PG Project Orientation\SKILL.md`

Use when:

- starting or resuming a Panda Gallery chat,
- reading project memory or handoff,
- confirming read/write boundaries,
- deciding which Codex artifacts to load.

### CODEX PG Code Review

Path:

`C:\CODEX PG\CODEX Skills\CODEX PG Code Review\SKILL.md`

Use when:

- reviewing Panda Gallery Python/PySide6 code,
- judging code quality with the 6 C's,
- reviewing Claude's implementation work,
- turning findings into specific fix requests.

### CODEX PG Claude Task Writer

Path:

`C:\CODEX PG\CODEX Skills\CODEX PG Claude Task Writer\SKILL.md`

Use when:

- converting specs or reviews into Claude prompts,
- writing implementation tasks for `C:\panda-gallery`,
- defining scope, acceptance criteria, and verification steps.

## Activation Note

Because Darrin asked Codex-created folders to stay under `C:\CODEX PG`, these skills were created as project-owned source files here first.

To make them automatically discoverable by Codex as live skills in future sessions, they may need to be copied into Codex's live skills directory. The helper script below can do that, but it intentionally requires an explicit user-approved action because it writes outside `C:\CODEX PG`:

`C:\CODEX PG\CODEX Skills\CODEX_install_project_skills.ps1`

Until installed, a user can still ask Codex to use one directly by naming its path.

Example:

`Use the skill at C:\CODEX PG\CODEX Skills\CODEX PG Claude Task Writer\SKILL.md to write a Claude prompt for bug #131.`

## Recommended First Use

For a fresh Codex chat, say:

`Use the CODEX PG Project Orientation skill at C:\CODEX PG\CODEX Skills\CODEX PG Project Orientation\SKILL.md, then read C:\CODEX PG\CODEX Docs\CODEX_PROJECT_MEMORY.md and C:\CODEX PG\CODEX Docs\CODEX_CURRENT_HANDOFF.md.`
