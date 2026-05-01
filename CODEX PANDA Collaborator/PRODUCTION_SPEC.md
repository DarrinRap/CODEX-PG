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

The setup and hub flow:

- opens registration automatically when setup is incomplete;
- requires User 1 registration first;
- requires User 2 registration second;
- opens the Collaborator Hub after both users are registered;
- shows GO / Switch action buttons for User 1 and User 2 in the Hub;
- keeps a persistent Setup Users / Switch User button in the header so the switch workflow is never hidden in a side panel;
- keeps Collaborator Hub user-card buttons clickable before setup is complete, using them to guide the user into setup instead of presenting dead disabled controls;
- makes GO / Switch automate the full switch process: save active user, apply that user's defaults, update the theme, and scan the repository;
- shows the active user's custom name in large uppercase text at the top of the screen;
- uses clearly different complementary color themes for User 1 and User 2;
- follows the PANDA-wide header rule: the header must contain large step text with arrow separators, show the whole workflow path, and visually mark each step as current or done;
- keeps setup instructions progressive: while registering User 1, do not show User 2 or Collaborator Hub checklist rows; reveal User 2 only after User 1 is registered, then reveal the Hub only after User 2 is registered;
- provides a checklist that shows which registration steps are complete;
- stores per-user defaults for repository path, handoff agent, and handoff title;
- provides Browse buttons for the main repository path and each user's default repository path so users can pick the local Git repository folder instead of typing a Windows path;
- stores a shared Project Files Tracker directory, defaulting to `C:\panda-gallery`, with a Browse button;
- treats `C:\panda-gallery\skills\pg-project-sync\MANIFEST.md` as the existing canonical project-files manifest and preserves the existing `pgsync` flow that creates `workflows\project_knowledge_sync_YYYY-MM-DD` bundles for Claude.ai project files;
- requires per-user Codex account label, Claude account label, Git author name, and Git author email during registration;
- requires per-user Claude Desktop path and Claude Code path during registration so each user profile identifies the local tools it is meant to use;
- provides Browse buttons for Claude Desktop and Claude Code paths so users can pick Windows paths instead of typing them by hand;
- stores only account labels, usernames, and emails, never passwords, tokens, API keys, recovery codes, or browser credentials;
- clearly records whether the two users are using the same repository path, which means they share the same git working tree and commit history;
- records Git author identity as context but does not switch Git credentials or perform Git hosting login;
- applies the active user's defaults to the repository and handoff controls;
- blocks scan and handoff actions until required setup fields are complete;
- persists settings in a local ignored `CODEX settings` file;
- writes a timestamped backup before replacing an existing settings file.

The settings API rejects payloads that do not contain exactly two profiles. Settings persistence is separate from repository handoff packages and never runs git operations.

## Implemented Handoff Context Preservation

Every handoff package writes history and account context into both `manifest.json` and `HANDOFF.md`.

The recorded context includes:

- active PANDA user slot and custom display name;
- Codex account label;
- Claude account label;
- Claude Desktop path and Claude Code path;
- Project Files Tracker directory;
- Git author name and email;
- repository path and whether the path is shared with the other user;
- branch, `HEAD`, status snapshot, operator notes, and safety receipt.

The generated docs instruct the next session to continue from `HANDOFF.md` and `manifest.json` before writing code so project history, operator identity, and current repository state are not lost between Claude/Codex sessions.

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

## v0.9 Control Center Design Spec

PANDA Collaborator v0.9 expands the app from a handoff-only tool into the main local control center for one active project.

The control center must stay safety-first. It may automate safe reading, scanning, summarizing, logging, and package creation. It must not automate destructive Git actions, credential entry, branch switching, merge/rebase, conflict resolution, restore, delete, or force push.

### Start Session Workflow

The app must provide a clear Start Session flow after a user presses GO / Switch.

The workflow should automate as much as possible:

1. Confirm the active user profile is complete.
2. Apply the active user's defaults.
3. Scan the repository.
4. Find the latest handoff package for the active repo.
5. Summarize the latest handoff in plain language.
6. Show concerns, achievements, and recommended next action.
7. Log the start-session event.
8. Enable a clear Start Work state only after required checks pass.

If there is no latest handoff, PANDA should say so plainly and recommend creating a fresh handoff before serious work continues.

### Plain-English And Technical Views

PANDA must support two handoff summary views:

- Plain-English view: major events, achievements, concerns, next steps, and active user context.
- Technical view: branch, `HEAD`, package path, patch counts, copied file counts, skipped files, and safety receipt.

The UI must provide a simple toggle between these views.

### Messages And Saved Communication

PANDA must include a simple message/status window.

Messages must:

- be visible in the app;
- be saved to readable local files;
- preserve author, timestamp, kind, text, and active user context;
- be included in project history/search.

The app should support short notes such as what was done, concerns, achievements, and next steps.

### End Session / Create Handoff Workflow

PANDA must provide a guided End Session / Create Handoff workflow.

The workflow should automate:

1. Repository scan.
2. Collection of optional plain-English closeout notes.
3. Safe handoff package creation.
4. Plain-English summary creation.
5. Technical record creation.
6. Timeline logging.
7. Daily report update.
8. Recommended next action update.

Closeout notes are encouraged but not required.

If PANDA cannot directly perform a safe action, it should prepare the required text or command, copy it to the clipboard when possible, and clearly tell the user what it copied and why manual action is required.

### Project Timeline

PANDA must keep a chronological project timeline.

The timeline should record:

- user switches;
- start sessions;
- repo scans;
- handoff packages;
- messages;
- concerns;
- achievements;
- emergency pause/clear events;
- daily report creation.

The timeline should be visible in the UI and searchable.

### Project Manager View

PANDA must include a Project Manager View that summarizes the project in plain language:

- active user;
- repo health;
- latest achievements;
- current concerns;
- recommended next action;
- latest handoff summary;
- recent timeline events;
- Claude/Codex collaborator activity.

### Daily Reports And Archive Logs

PANDA must create a daily plain-English project report when work happens that day.

Reports and logs must be archived locally in readable files. They should preserve enough detail to reconstruct the day without relying on memory.

### Search

PANDA must provide simple search across:

- messages;
- timeline events;
- handoff summaries;
- daily reports;
- concerns;
- achievements;
- collaborator activity.

### Collaborator Activity

PANDA must treat Claude and Codex as visible collaborators when account/agent context is available.

The app should show recent activity such as:

- last active collaborator;
- latest handoff author/agent;
- recent concern count;
- recent message count.

### Recommendations

PANDA must show a simple "What should happen next?" recommendation.

The recommendation should be based on:

- setup completion;
- emergency pause status;
- repo scan status;
- dirty/clean working tree;
- latest handoff availability;
- latest concerns;
- recent timeline activity.

### Emergency Pause / Stop Work

PANDA must provide Emergency Pause / Stop Work mode.

When active:

- the UI must show strong warning language;
- Start Work should be blocked;
- the reason must be logged;
- the user must be able to clear the pause with a clear event.

Emergency Pause must not modify project files.

### Automatic Versus Manual Actions

PANDA must clearly separate:

- safe automatic actions PANDA performs itself;
- manual actions PANDA cannot safely perform.

Manual actions should be shown in plain language with clear instructions.
