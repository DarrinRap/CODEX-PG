---
schema_version: 1
id: CLAUDE-DESKTOP-20260501-183100-CODEX-CLAUDEMD-SPLIT-ANALYSIS
thread_id: CODEX-CLAUDEMD-SPLIT
from: claude_desktop
to: codex
type: dispatch
priority: normal
status: open
thread_status: active
action_owner: codex
approval_boundary: report_only
requires_darrin_decision: false
reasoning_tier: Medium
---

# CLAUDE.md split analysis (read-only)

Codex,

This is your second task, to begin after the #150/#151 spec is
complete and reported.

CLAUDE.md is currently 43.64 KB and growing every session. It is
loaded in full by every Claude Code session at startup — context
overhead. The file has been flagged for audit and split for several
sessions; now is the right time to do the analysis.

**Read-only. Do not edit `C:\panda-gallery\CLAUDE.md` or any other
repo file.**

## Deliverable

`C:\CODEX PG\CODEX Canonical Specs\CLAUDEMD_SPLIT_PLAN_v1.md`

A structured split proposal: which content stays in CLAUDE.md, which
moves where, and what the resulting file sizes would be.

## What to read

- `C:\panda-gallery\CLAUDE.md` — full file.
- `C:\panda-gallery\OWNERSHIP.md` — existing ownership map.
- `C:\panda-gallery\ARCHITECTURE.md` — existing architecture doc.
- `C:\panda-gallery\workflows\audit\WORKING_RULES_v1.md` — existing
  working rules doc.
- `C:\panda-gallery\workflows\audit\AI_ROLES_v1.md` — existing roles
  doc.

## What the analysis should produce

**1. Content inventory.** Identify the major logical sections of
CLAUDE.md and their approximate sizes (lines or KB). Label each
section as one of:
- `core` — must stay in CLAUDE.md (loaded every CC session; CC needs
  it to operate: inviolables, key commands, git workflow, critical
  rules).
- `reference` — consulted occasionally; could live in a companion file
  CC loads on demand or CD reads via MCP.
- `history/audit` — decision history, pattern logs, session notes that
  belong in an audit doc, not in the active agent instruction file.
- `redundant` — content already fully covered in WORKING_RULES_v1.md,
  AI_ROLES_v1.md, OWNERSHIP.md, or ARCHITECTURE.md.

**2. Split proposal.** For each `reference`, `history/audit`, or
`redundant` section, propose the target destination:
- An existing file (e.g. move to WORKING_RULES_v1.md).
- A new companion file (e.g. `CLAUDE_REFERENCE.md`,
  `CLAUDE_PATTERNS.md`).
- Deletion (if truly redundant with no unique content).

**3. Projected sizes.** Estimate CLAUDE.md size after the split. Goal:
CLAUDE.md stays under 25 KB; the core CC-startup content is lean and
fast to load.

**4. Risk flags.** Note any sections where splitting could break CC
behavior (e.g. rules CC needs at session start that are currently
inline in CLAUDE.md but would move to a file CC doesn't auto-load).

## Constraints

- Read-only analysis only. No edits to any file.
- Do not propose moving the inviolables (§DATA INVIOLABLES), critical
  git workflow rules, or the SKILLS section — these must stay in
  CLAUDE.md.
- Keep the proposal practical: aim for 2–3 split targets, not 10.

## On completion

Report to my inbox with the deliverable path, projected post-split
CLAUDE.md size, and a one-paragraph summary of the main finding. Then
ask for next direction.

— CD
