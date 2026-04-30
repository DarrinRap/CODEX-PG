# PANDA Collaborator Acceptance Report

Accepted version: `0.4.0`

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
- Unit tests: `4/4` passed.
- Windows test runner: passed.
- Local health endpoint: passed.
- Browser smoke: passed with zero console errors.
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
