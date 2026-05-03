# CLAUDE.md Split Plan v1

Date: 2026-05-01
Owner: Codex
Status: proposed / read-only analysis

## Source Files Reviewed

- `C:\panda-gallery\CLAUDE.md` — 44,683 bytes / 43.64 KB / 722 lines.
- `C:\panda-gallery\OWNERSHIP.md` — 6.67 KB.
- `C:\panda-gallery\ARCHITECTURE.md` — 31.43 KB.
- `C:\panda-gallery\workflows\audit\WORKING_RULES_v1.md` — 9.92 KB.
- `C:\panda-gallery\workflows\audit\AI_ROLES_v1.md` — 9.67 KB.

## Executive Recommendation

Split `CLAUDE.md` into a lean startup file plus two practical destinations:

1. Keep `CLAUDE.md` as the always-loaded command file under 25 KB.
2. Create `C:\panda-gallery\CLAUDE_REFERENCE.md` for file maps, spec maps, tooling, terminology, palette, and sensor-size reference.
3. Move detailed operating-procedure material into `C:\panda-gallery\workflows\audit\WORKING_RULES_v1.md`, preserving only a compact mandatory checklist in `CLAUDE.md`.

Do not move the `SKILLS` section, `INVIOLABLE RULES`, `DATA INVIOLABLES`, critical git workflow / commit-go rules, or essential session-start routing reminders.

Projected post-split `CLAUDE.md`: approximately 22.5-24.0 KB, depending on how much reporting frontmatter detail remains inline.

## Content Inventory

| Lines | Approx size | Section | Label | Recommendation |
|---:|---:|---|---|---|
| 1-14 | 1.25 KB | Header plus Codex audit ownership note | core | Keep, but condense Codex audit note to 3-4 lines and point to `OWNERSHIP.md` / `AI_ROLES_v1.md` for full role context. |
| 15-100 | 4.34 KB | File map | reference | Move detailed map to new `CLAUDE_REFERENCE.md`; keep a 5-8 line pointer in `CLAUDE.md` telling CC to read it before unfamiliar work. |
| 101-164 | 3.17 KB | Default answers | mixed core / redundant | Keep commit/versioning, dialog, testing, scope, backup defaults in compact form. Move expanded rationale and workflow phrasing to `WORKING_RULES_v1.md`. |
| 165-204 | 2.57 KB | Skill-file pointers | core | Keep. This is startup routing for on-demand rules and should remain near `SKILLS`. |
| 205-216 | 0.89 KB | Project identity | core | Keep. |
| 217-298 | 5.48 KB | SKILLS | core | Keep unchanged except for mechanical pruning of duplicate wording if any. Dispatch explicitly forbids moving this. |
| 299-346 | 2.70 KB | Spec files / read-on-demand list | reference | Move full list to `CLAUDE_REFERENCE.md`; keep a short pointer to the reference file and the most critical current spec path only if needed. |
| 347-360 | 0.90 KB | Tech stack | reference / redundant | Move to `CLAUDE_REFERENCE.md`; optionally cross-link `ARCHITECTURE.md` because architecture details already live there. |
| 361-396 | 2.28 KB | Repo tooling | reference | Move to `CLAUDE_REFERENCE.md`; keep only the primary command/run rule if CC truly needs it every session. |
| 397-409 | 0.97 KB | Terminology | reference | Move to `CLAUDE_REFERENCE.md`; keep a short pointer if terms are commonly misused. |
| 410-483 | 5.11 KB | Inviolable rules | core | Keep inline. This includes data inviolables, no native Qt dialogs, UI dispatch fidelity, no large-file direct writes, and audit boundaries. |
| 484-494 | 0.78 KB | Color palette | reference | Move to `CLAUDE_REFERENCE.md` or a design reference if one becomes the canonical style home. |
| 495-505 | 0.78 KB | Sensor sizes | reference | Move to `CLAUDE_REFERENCE.md` with palette/design references. |
| 506-517 | 0.90 KB | Repo-first project state | core | Keep. It prevents stale memory and should load every session. |
| 518-537 | 1.33 KB | Session close | mixed core / redundant | Keep compact mandatory close checklist. Move expanded discipline to `WORKING_RULES_v1.md`. |
| 538-646 | 5.71 KB | Reporting discipline, durable mailbox reports, inbox checks | mixed core / history/audit | Keep a compact mandatory mailbox checklist plus required filename/frontmatter fields. Move examples, rationale, and detailed transition rules to `WORKING_RULES_v1.md`. |
| 647-668 | 1.37 KB | Paste / run protocol | core / redundant | Keep short version in `CLAUDE.md`; move detailed explanation to `WORKING_RULES_v1.md`. |
| 669-720 | 2.77 KB | Response output | core / redundant | Keep mandatory `cc_latest` / final-output requirements that affect every CC session. Move elaboration and examples to `WORKING_RULES_v1.md`. |
| 721-722 | 0.31 KB | End marker | core | Keep tiny end marker / read-on-demand reminder. |

## Split Proposal

### Keep In `CLAUDE.md`

Keep a lean startup file containing:

- Header and version.
- Compact ownership and routing reminders, including Codex audit boundary.
- Compact file/reference pointer section.
- Default answers that must govern every turn.
- Skill pointers and full `SKILLS` section.
- Project identity and essential run command.
- `INVIOLABLE RULES`, including `DATA INVIOLABLES`.
- Critical git workflow / commit-go / no-commit-without-eye-test rules.
- Repo-first project-state rule.
- Compact session-close, mailbox, paste/run, and response-output checklists.

Target retained size: about 22.5-24.0 KB.

### New `CLAUDE_REFERENCE.md`

Create a single companion reference file for material that is useful but should not be loaded on every CC startup:

- Detailed file map / concept-to-file index.
- Spec files / read-on-demand list.
- Tech stack.
- Repo tooling helper list.
- Terminology.
- Color palette.
- Sensor sizes.

Estimated new file size: about 14.0-15.0 KB, including headings and backlinks.

Rationale: these sections are lookup tables. They help orient implementation work, but CC can load them on demand when touching an unfamiliar area.

### Existing `WORKING_RULES_v1.md`

Expand the existing working-rules doc with detailed operating procedure content:

- Expanded default-answer rationale.
- Detailed session-close discipline.
- Detailed mailbox report / inbox-check examples.
- Paste/run protocol details.
- Response-output expectations and examples.

Estimated additions: about 5.5-7.0 KB.

Rationale: `WORKING_RULES_v1.md` already covers communication, decision handling, UI dispatch compliance, commit-go eye-test rules, cross-agent dispatch hygiene, and Codex deliverable routing. It is the natural home for process detail that does not need to consume startup context every session.

### Existing Role / Architecture Docs

Do not duplicate what these already own:

- `OWNERSHIP.md` remains the detailed ownership map for CD, CC, and Codex-owned surfaces.
- `AI_ROLES_v1.md` remains the detailed role/routing policy for Desktop Claude, Claude Code, and Codex.
- `ARCHITECTURE.md` remains the detailed architecture reference.

`CLAUDE.md` should only carry enough of these topics to enforce startup behavior and then link out.

## Projected Sizes

| File | Current size | Projected size | Notes |
|---|---:|---:|---|
| `CLAUDE.md` | 43.64 KB | 22.5-24.0 KB | Under the 25 KB goal if reference tables and expanded reporting detail move out. |
| `CLAUDE_REFERENCE.md` | new | 14.0-15.0 KB | New lookup-only companion file. |
| `WORKING_RULES_v1.md` | 9.92 KB | 15.5-17.0 KB | Absorbs process detail and examples. |
| `OWNERSHIP.md` | 6.67 KB | no change | Referenced, not expanded. |
| `AI_ROLES_v1.md` | 9.67 KB | no change | Referenced, not expanded. |
| `ARCHITECTURE.md` | 31.43 KB | no change | Referenced, not expanded. |

Approximate savings in `CLAUDE.md`:

- Move detailed file/spec maps: 5.5-6.2 KB saved after short pointers remain.
- Move tech/tooling/terminology/palette/sensors: 4.8-5.2 KB saved after short pointers remain.
- Compress default/session/reporting/paste/response procedure: 6.0-7.5 KB saved after mandatory checklists remain.
- Condense duplicated role/ownership/audit wording: 0.5-1.0 KB saved.

## Risk Flags

1. Do not move `SKILLS`, `INVIOLABLE RULES`, `DATA INVIOLABLES`, or critical git workflow rules. These are load-bearing and must remain in the startup file.
2. Reporting discipline is partly process detail and partly active safety rail. If too much moves out, CC may skip durable mailbox reports, `cc_latest`, or inbox checks. Keep a compact mandatory checklist and frontmatter requirements inline.
3. The detailed file map currently prevents wasted grepping and accidental edits in the wrong subsystem. If moved, `CLAUDE.md` must include an explicit startup instruction: read `CLAUDE_REFERENCE.md` before unfamiliar implementation work.
4. `WORKING_RULES_v1.md` is not automatically loaded by CC unless instructed. `CLAUDE.md` must preserve a short rule saying when to load it.
5. `ARCHITECTURE.md` is large and mostly architecture-specific. Do not route all reference material there; a dedicated `CLAUDE_REFERENCE.md` is lower-risk for agent instructions and lookup tables.
6. Avoid over-splitting. More than two split targets increases the chance CC loads the wrong file or skips a needed rule.

## Proposed Minimal Edit Sequence For CC

1. Create `CLAUDE_REFERENCE.md` with moved reference sections and backlinks to `CLAUDE.md`.
2. Add moved process detail to `WORKING_RULES_v1.md` under clear headings.
3. Replace moved sections in `CLAUDE.md` with compact pointers and mandatory checklists.
4. Verify `CLAUDE.md` byte size is under 25 KB.
5. Run a quick text audit for required phrases: `DATA INVIOLABLES`, `SKILLS`, `commit-go`, `cc_latest`, `WORKING_RULES_v1.md`, and `CLAUDE_REFERENCE.md`.

