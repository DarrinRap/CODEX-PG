# CODEX Panda Gallery Read-Only Reference Policy

Last updated: 2026-04-24 18:55:30 -07:00

## Purpose

Codex may use `C:\panda-gallery` as a read-only reference source for design, architecture, specs, and existing implementation patterns.

## Source Folder

`C:\panda-gallery`

## Hard Boundary

- Codex should not create, edit, delete, move, rename, format, stage, commit, push, or otherwise mutate files inside `C:\panda-gallery` unless Darrin explicitly overrides this boundary in a future message.
- Codex may read files from `C:\panda-gallery` for context.
- Codex-created files must stay under `C:\CODEX PG`.
- Every Codex-created folder must start with `CODEX`.
- Derived notes, inventories, summaries, implementation plans, and reference snapshots belong in `C:\CODEX PG`, not in `C:\panda-gallery`.

## Preferred Workflow

1. Read relevant files directly from `C:\panda-gallery` when context is needed.
2. Write Codex notes or extracted summaries under this folder.
3. Build new code only under `C:\CODEX PG`.
4. Back up Codex work to `https://github.com/DarrinRap/CODEX-PG.git`.

## Why Not A Symlink?

A symlink would make `C:\panda-gallery` look like part of the Codex workspace and could make accidental writes easier. This setup intentionally avoids symlinks. The boundary stays visible.
