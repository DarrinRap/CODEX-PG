---
name: codex-pg-code-review
description: Use when reviewing Panda Gallery Python, PySide6, UI, testing, capture, transcription, database, packaging, or audit MVP code for correctness, completeness, clarity, cleanliness, checkability, context fit, documentation quality, maintainability, efficiency, and regression risk. Especially useful before giving Claude implementation feedback.
metadata:
  short-description: Review Panda Gallery code with the 6 C's and project risk lens
---

# CODEX PG Code Review

## Purpose

Use this skill to review Panda Gallery code with a senior-engineering lens and the project's 6 C's:

- Correct
- Complete
- Clear
- Clean
- Checkable
- Contextual

The goal is not abstract perfection. The goal is to protect shipped behavior while making the next change safer, smaller, and more testable.

## Default Stance

If Darrin asks for a review, lead with findings. Prioritize real bugs, regressions, data loss risks, broken workflows, missing tests, and maintainability risks that will affect future work.

Keep summaries secondary. Do not produce a generic praise-heavy review.

## Boundaries

- Read `C:\panda-gallery` as live source of truth.
- Do not edit `C:\panda-gallery` unless Darrin explicitly asks Codex to do so.
- Write review notes and Codex artifacts under `C:\CODEX PG`.
- If reviewing Claude work, compare it against the prompt, the relevant spec, `BUGS.md`, `HANDOFF.md`, and existing project style.

## Evidence Collection Workflow

1. Identify the changed files or target feature.
2. Check git status/log in the relevant repo when needed.
3. Read the smallest useful set of files.
4. Use `rg` for patterns before manual scanning.
5. For UI changes, inspect design mockups/specs before judging the implementation.
6. For code paths involving data writes, identify failure behavior and rollback behavior.
7. For testing/capture/audit work, inspect resulting JSON/contracts, not only UI code.

Useful pattern searches:

- `except Exception`
- `except:`
- `print(`
- `TODO`
- `setStyleSheet(`
- `QSettings(`
- `pass`
- `Session(`
- `json.loads`
- `json.dumps`

## The 6 C's Review Rubric

### Correct

Ask:

- Does it do what the feature or bug says?
- Are edge cases handled?
- Could user work be lost?
- Does the UI state match persisted state?
- Are session files, screenshots, audio, transcripts, and result JSON linked correctly?

### Complete

Ask:

- Did the change cover the whole workflow or just the visible UI?
- Are persistence, cleanup, tests, docs, and handoff updates included when needed?
- Does it handle cancel, close, failure, and retry paths?

### Clear

Ask:

- Can a future maintainer understand the intent quickly?
- Are names specific to the domain?
- Are docstrings current, or do they mostly preserve old phase history?
- Are comments explaining landmines rather than restating code?

### Clean

Ask:

- Is behavior split into reasonable units?
- Did a large module get larger without need?
- Are UI, persistence, styling, and business rules tangled?
- Did the change avoid unrelated refactors?

### Checkable

Ask:

- Is there a deterministic way to verify the behavior?
- Are pure helpers covered by tests?
- Is a manual smoke path described when UI automation is not practical?
- Are output files and data contracts easy to inspect?

### Contextual

Ask:

- Does the change fit Panda Gallery's existing style and constraints?
- Does it respect known bugs and active handoff notes?
- Does it advance the Testing + Audit MVP sequence instead of jumping ahead?
- Does it avoid overwriting Claude/user work?

## Known Risk Areas

Treat these as common review hot spots:

- Very large modules: `panda_gallery.py`, `instruction_pane.py`, `panels.py`, `canvas.py`, `library_view.py`.
- Inline QSS and repeated styling patterns.
- UI widgets directly opening database sessions.
- Broad exception handling that silently swallows failures.
- `print(` calls in app code instead of structured user-visible status or logging.
- JSON/result schema drift.
- Session packaging or screenshot workflows that can orphan evidence.
- UI sizing/layout fixes made without checking narrow pane states.

## Output Format

For normal chat review:

1. Findings first, ordered by severity.
2. Each finding should include file and line reference when possible.
3. Then open questions or assumptions.
4. Then a short 6 C's summary.
5. Then concrete next steps or a Claude-ready fix prompt if useful.

When using Codex desktop review comments, emit `::code-comment{...}` directives for line-specific findings when appropriate.

## Severity Guidance

- P0: data loss, app crash on common path, security/privacy violation, unusable core workflow.
- P1: likely user-facing regression, broken persistence, broken testing/audit evidence, serious maintainability trap in active area.
- P2: edge-case bug, unclear behavior, missing focused tests, avoidable coupling.
- P3: polish, naming, small documentation mismatch, local cleanup.

## Project-Specific Review Preferences

Prefer recommendations that:

- keep behavior stable,
- add tests around pure logic,
- define data contracts before implementation,
- extract only around active work,
- reduce future risk without large rewrites,
- preserve useful historical bug lessons in the right documentation file.

Avoid recommendations that:

- propose rewriting the app,
- ask for sweeping style migration,
- mix multiple bugs/features in one prompt,
- judge UI without checking the design intent,
- treat `results_latest.json` as a final backend contract,
- introduce AI/Dropbox/dashboard work before package and evidence contracts exist.

## Useful Codex Artifacts

Use these when relevant:

- `C:\CODEX PG\CODEX Codebase Orientation\CODEX_PG_CODEBASE_ORIENTATION_SUMMARY.md`
- `C:\CODEX PG\CODEX Claude Review Recommendations\CODEX_CLAUDE_CODE_QUALITY_RECOMMENDATIONS.md`
- `C:\CODEX PG\CODEX Specification Review\CODEX_SPECIFICATION_REVIEW_REPORT.md`
- `C:\CODEX PG\CODEX Interface Storyboards`
- `C:\CODEX PG\CODEX Visual Mockups`
