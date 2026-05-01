# PANDA Collaborator

Windows shared AI coding workstation handoff manager.

Current version: `0.8.0`.

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
- Git author name;
- Git author email.

PANDA stores account labels, usernames, and emails only. Do not enter passwords, API keys, tokens, recovery codes, or browser credentials.

If both users use the same repository path, they share the same git working tree and commit history. PANDA records the per-user Git author identity for context and handoff docs, but it does not switch Git credentials or log in to Git hosting accounts.

The active user is shown in large text at the top of the screen. User 1 uses a warm amber/coral theme. User 2 uses a cool cyan/teal theme. The color change is intentional so the operator can tell which user is active at a glance.

On first run, registration opens automatically. The required order is User 1 registration, then User 2 registration, then the Collaborator Hub. The Hub has GO / Switch buttons for both users. A GO / Switch action saves the active user, applies that user's defaults, changes the screen theme, and scans the repository automatically.

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
