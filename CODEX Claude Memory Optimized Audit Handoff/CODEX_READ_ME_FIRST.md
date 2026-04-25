# CODEX Claude Memory Optimized Audit Handoff

Purpose: give Claude and Claude Code a staged, low-overwhelm way to implement the Panda Gallery Audit MVP.

Do not paste every project document into Claude at once. Start with this folder and follow the read protocol.

## Best Protocol

1. Give Claude Chat only `CODEX_READ_ME_FIRST.md` and `CODEX_SEARCHABLE_INDEX.md`.
2. Ask Claude to summarize the goal and name which chunk it needs next.
3. Provide exactly one chunk at a time.
4. After Claude understands the chunk, ask for a concrete implementation plan.
5. Only then give Claude Code the relevant chunk plus `CODEX_CLAUDE_CODE_TASK_PROMPT.md`.
6. Keep each Claude Code task narrow: one module, one behavior slice, one validation target.
7. After each task, ask Claude Code to report files changed, tests run, and unresolved risks.

## Do Not Start With

- The full interaction spec.
- The full starter pack.
- All screenshots.
- All previous reviews.
- Multiple unrelated goals.

That creates memory pressure and increases the chance Claude will mix old guidance with current instructions.

## Recommended First Message To Claude Chat

```text
Please read these two files first:

C:\CODEX PG\CODEX Claude Memory Optimized Audit Handoff\CODEX_READ_ME_FIRST.md
C:\CODEX PG\CODEX Claude Memory Optimized Audit Handoff\CODEX_SEARCHABLE_INDEX.md

Do not edit C:\panda-gallery yet. First summarize the Audit MVP goal, the implementation boundaries, and which single chunk you want next.
```

## Recommended First Message To Claude Code

Use only after Claude Chat has summarized the plan:

```text
Implement only the first local Audit MVP slice described in:

C:\CODEX PG\CODEX Claude Memory Optimized Audit Handoff\CODEX_CLAUDE_CODE_TASK_PROMPT.md

Also read the one chunk I provide with it. Do not read unrelated project history unless you need a specific referenced file. Keep changes narrow and report files changed plus tests run.
```
