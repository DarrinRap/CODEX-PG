# PANDA Collaborator

Windows shared AI coding workstation handoff manager.

Current version: `0.9.0`.

## Safety Model

PANDA Collaborator separates committed and uncommitted work:

- Committed protection: creates a git branch ref at the current `HEAD`.
- Uncommitted protection: writes binary patch files and copies changed/untracked files into a unique package directory.

The app does not switch branches, stash changes, reset files, clean files, merge, rebase, force push, delete branches, or auto-resolve conflicts.

Forbidden commands:

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

## Run

For plain-language setup and daily-use steps, read:

```text
C:\CODEX PG\CODEX PANDA Collaborator\PANDA_COLLABORATOR_SETUP_STEPS.md
```

The Desktop shortcut is:

```text
C:\Users\drrap\OneDrive\Desktop\PANDA Collaborator.lnk
```

```powershell
python "C:\CODEX PG\CODEX PANDA Collaborator\panda_collaborator.py" --port 8788
```

Open:

```text
http://127.0.0.1:8788/
```

Or use the Windows launcher:

```powershell
& "C:\CODEX PG\CODEX PANDA Collaborator\CODEX_start_panda_collaborator.ps1"
```

## CLI

Scan a repository:

```powershell
python "C:\CODEX PG\CODEX PANDA Collaborator\panda_collaborator.py" --scan "C:\CODEX PG"
```

Create a handoff package:

```powershell
python "C:\CODEX PG\CODEX PANDA Collaborator\panda_collaborator.py" --create-handoff "C:\CODEX PG" --title "AI workstation handoff" --agent "Codex"
```

## Handoff Package Contents

Each package contains:

- `manifest.json`
- `HANDOFF.md`
- `patches\unstaged-working-tree.patch`
- `patches\staged-index.patch`
- `file_copies\...`

`manifest.json` and `HANDOFF.md` include session/account context for the active PANDA user: display name, Codex account label, Claude account label, Git author identity, repository path, branch, `HEAD`, status snapshot, notes, and safety receipt. This is how the next session keeps history and context instead of guessing from memory.

Default package root:

```text
C:\CODEX PG\CODEX PANDA Collaborator\CODEX handoff packages
```

Default project history root:

```text
C:\CODEX PG\CODEX PANDA Collaborator\CODEX project history
```

Override with:

```powershell
$env:PANDA_COLLABORATOR_PACKAGE_ROOT = "D:\Safe Handoffs"
```

## Package Inspector

The web UI can list recent packages and inspect a package manifest. This is read-only:

- shows protection branch and whether it still exists;
- shows patch count and patch bytes;
- shows copied/skipped file counts;
- shows the safety receipt;
- previews `HANDOFF.md`.

It does not apply patches, restore files, delete packages, or switch branches.

## Two-User Setup

The web UI includes a guided registration flow for exactly two local user profiles.

Each profile stores:

- custom display name;
- default repository path;
- default handoff agent name;
- default handoff title;
- Codex account label;
- Claude account label;
- Claude Desktop path;
- Claude Code path;
- Git author name;
- Git author email.

PANDA stores account labels, usernames, and emails only. Do not enter passwords, API keys, tokens, recovery codes, or browser credentials.

If both users use the same repository path, they share the same git working tree and commit history. PANDA records the per-user Git author identity for context and handoff docs, but it does not switch Git credentials or log in to Git hosting accounts.

The active user is shown in large text at the top of the screen. User 1 uses a warm amber theme. User 2 uses a cool cyan theme. User identity colors stay attached to their own registration and workflow surfaces even when the other user is the active operator.

On first run, registration opens automatically. The required order is User 1 registration, User 1 confirmation, User 2 registration, then the Collaborator Hub. The setup window is compact and scrollable, groups fields into readable sections, and disabled registration actions explain which required fields are still missing. PANDA does not silently jump from User 1 into User 2; the user chooses **Continue to User 2** from the confirmation panel. The Hub has HANDOVER TO USER 1 and HANDOVER TO USER 2 buttons. A handover action saves the active user, applies that user's defaults, changes the active-user header theme, and scans the repository automatically.

Safe action buttons turn green when they can be activated. Disabled actions are grey. Warning actions such as Emergency Pause may stay red.

## v0.9 Control Center

PANDA now includes a one-project control center.

The control center adds:

- Start Session / Start Work automation;
- End Session / Handoff automation;
- plain-English and technical handoff summary views;
- saved project messages;
- Project Manager view;
- project timeline;
- daily report archive;
- search across messages, timeline, and reports;
- Claude/Codex activity context;
- Emergency Pause / Stop Work mode.

PANDA automates safe actions such as scanning, reading handoffs, summarizing, logging, and creating safe handoff packages. It still does not automate destructive Git work, branch switching, credential entry, restore, merge, rebase, conflict resolution, force push, or deletion.

Settings are saved locally outside git:

```text
C:\CODEX PG\CODEX PANDA Collaborator\CODEX settings\panda_collaborator_settings.local.json
```

Before replacing an existing settings file, the app writes a timestamped backup beside it.

## Restore Safety Preview

The package detail view includes a read-only restore safety preview.

The preview:

- checks whether the protection branch still exists;
- runs `git apply --check --binary` against package patches;
- compares copied files to the target repo by SHA-256;
- reports blockers and warnings;
- keeps automated restore unavailable by design.

The preview does not modify the target repository.

## Tests

```powershell
python -m unittest discover -s "C:\CODEX PG\CODEX PANDA Collaborator\tests"
```

Or use the Windows test runner:

```powershell
& "C:\CODEX PG\CODEX PANDA Collaborator\CODEX_test_panda_collaborator.ps1"
```
