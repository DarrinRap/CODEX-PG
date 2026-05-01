# PANDA Collaborator Acceptance Report

Accepted version: `0.7.0`

Date: 2026-04-30

## Production MVP Scope

PANDA Collaborator is accepted as a safety-first Windows shared AI coding workstation handoff manager when it can:

- scan a git repository and show staged, unstaged, untracked, deleted, and conflicted work;
- create a safe handoff package;
- protect committed work with a branch ref created at the current `HEAD`;
- protect uncommitted work with binary patch files and copied files;
- list handoff packages;
- inspect handoff manifests without arbitrary path reads;
- preview restore safety without mutating the target repository;
- guide registration for exactly two customizable local user profiles in order: User 1, then User 2;
- open a Collaborator Hub with GO / Switch buttons after registration;
- automate the user switch process from the GO / Switch buttons;
- show the active user name in large top-of-screen text;
- visibly differentiate User 1 and User 2 with different color themes;
- run locally through a Windows start script;
- verify itself through a Windows test script.

## Safety Acceptance

The implementation does not provide destructive controls for:

- `git reset --hard`
- `git clean -fd`
- `git clean -xdf`
- `git push --force`
- `git push -f`
- `git checkout .`
- `git restore .`
- `git branch -D`
- `git branch -d`
- `git push origin --delete`

The implementation also blocks stash, merge, rebase, checkout, restore, and clean verbs in its safety wrapper.

## Verification Performed

- Python syntax check: passed.
- Unit tests: `7/7` passed.
- Windows test runner: passed.
- Local health endpoint: passed.
- Browser smoke: passed with zero console errors, including User 1 registration, User 2 registration, Collaborator Hub open, GO / Switch automation for both users, per-user defaults, theme switching, automatic scan, and no page scroll.
- Git checkpoint: committed and pushed.

## Current Runtime

Default local URL:

```text
http://127.0.0.1:8788/
```

Default package root:

```text
C:\CODEX PG\CODEX PANDA Collaborator\CODEX handoff packages
```

## Explicit Non-Goals

The MVP intentionally does not:

- automatically restore files;
- apply patches;
- switch branches;
- merge or rebase;
- delete packages;
- delete branches;
- resolve conflicts.

Those omissions are safety features, not missing shortcuts.
