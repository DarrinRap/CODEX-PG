# PANDA Collaborator Production Spec

## Critical Design Principle

This system is designed for maximum data safety.

No user work, committed or uncommitted, must ever be lost.

The app keeps these responsibilities separate:

- Committed data protection: git branch refs.
- Uncommitted data protection: patch files plus file copies.

## Absolute Safety Rules

The app must never:

- discard uncommitted changes;
- overwrite files without backup;
- force push;
- auto-merge or auto-resolve conflicts;
- delete branches;
- rely on stash for safety;
- move user work between branches without clear explanation.

Forbidden git commands:

```text
git reset --hard
git clean -fd
git clean -xdf
git push --force
git push -f
git checkout .
git restore .
git branch -D
git branch -d
git push origin --delete
```

## Implemented MVP Contract

When creating a handoff, PANDA Collaborator:

1. Resolves the selected path to a git root.
2. Reads branch, `HEAD`, and porcelain status.
3. Creates a protection branch at the current `HEAD` without checking it out.
4. Writes `unstaged-working-tree.patch` using `git diff --binary`.
5. Writes `staged-index.patch` using `git diff --cached --binary`.
6. Copies changed tracked files and untracked files into `file_copies`.
7. Writes `manifest.json` and `HANDOFF.md`.
8. Leaves the working tree untouched.

## Implemented Read-Only Inspection

PANDA Collaborator can list and inspect previously created packages.

The package inspector:

- accepts stable package IDs, not arbitrary filesystem paths;
- resolves package IDs inside the configured package root only;
- rejects package ID traversal attempts;
- reads `manifest.json` and previews `HANDOFF.md`;
- reports protection branch presence when the source repository is available;
- performs no restore, apply, delete, checkout, merge, or branch operation.

## Implemented Two-User Setup

PANDA Collaborator supports exactly two local user profiles.

The setup flow:

- opens a full setup wizard automatically when setup is incomplete;
- guides the operator through naming both users;
- lets the operator choose the active user;
- shows the active user's custom name in large uppercase text at the top of the screen;
- uses clearly different complementary color themes for User 1 and User 2;
- provides a checklist that shows which setup steps are complete;
- stores per-user defaults for repository path, handoff agent, and handoff title;
- applies the active user's defaults to the repository and handoff controls;
- blocks scan and handoff actions until required setup fields are complete;
- offers a save-and-scan action that saves setup, applies defaults, and scans the repository;
- persists settings in a local ignored `CODEX settings` file;
- writes a timestamped backup before replacing an existing settings file.

The settings API rejects payloads that do not contain exactly two profiles. Settings persistence is separate from repository handoff packages and never runs git operations.

## Implemented Restore Safety Preview

PANDA Collaborator can preview restore safety for a handoff package and target repository.

The preview:

- resolves the target path to a git root;
- checks whether the recorded protection branch exists;
- runs `git apply --check --binary` for package patch files only;
- compares copied files with target files using SHA-256;
- reports blockers, warnings, patch checks, and copy checks;
- marks automated restore as unavailable.

The preview is explicitly non-mutating. It does not apply patches, copy files into the repo, switch branches, delete data, or perform conflict resolution.

## Implemented Operator Scripts

The project includes Windows helper scripts:

- `CODEX_start_panda_collaborator.ps1` starts the local server and checks `/api/health`.
- `CODEX_test_panda_collaborator.ps1` runs syntax checks, unit tests, and a live health probe when the server is running.

## Non-Goals For This MVP

- No restore automation.
- No branch switching.
- No merge/rebase/conflict automation.
- No remote push orchestration.
- No deletion of packages or branches from the UI.
