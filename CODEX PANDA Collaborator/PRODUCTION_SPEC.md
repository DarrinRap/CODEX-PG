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

- prompts for registration when setup is incomplete without blocking repository-only Working Tree scanning;
- keeps the Working Tree panel usable before setup is complete, with scan controls that remain reachable and a scan summary area that can scroll instead of clipping repository status;
- keeps Working Tree Browse, Scan repository, and Packages controls visually separated: the repository path picker owns its own row, Scan repository and Packages occupy separate action columns, and narrow screens stack them rather than letting buttons touch;
- supports Escape as a recovery key after scan/status interactions by clearing stuck focus and returning scrollable Working Tree and Status regions to the top;
- presents User 1 and User 2 registration together on the same setup screen;
- lets either user's registration action become activatable when that user's required fields are ready;
- opens the Collaborator Hub after both users are registered;
- shows a visible Handover action button on each Hub user card, with a target-specific aria label such as `Handover to User 1`, `Handover to User 2`, or `Handover to {display_name}`;
- keeps a persistent Setup Users / Handover Users button in the header so the handover workflow is never hidden in a side panel;
- keeps Collaborator Hub user-card buttons clickable before setup is complete, using them to guide the user into setup instead of presenting dead disabled controls;
- makes each Hub Handover button automate the full handover process for its target user: save active user, apply that user's defaults, update the theme, and scan the repository;
- shows the active user's custom name in large uppercase text at the top of the screen;
- uses clearly different complementary color themes for User 1 and User 2;
- follows the PANDA-wide workflow rule without duplicating text: the five left-to-right workflow panels are the visible step guide, use arrow separators in their headers, and visually mark state with semantic header colors: user/current accent for the active step, yellow for pending, green for ready/done, and muted treatment for locked future steps;
- keeps User 1 and User 2 registration side by side on one screen, so the user can compare names, colors, repository defaults, account labels, Claude paths, and Git identity without a surprise page jump;
- keeps the setup wizard visually compact but wide enough for the paired forms: the Project Files Tracker row spans the dialog, User 1 and User 2 occupy equal columns on desktop, and the layout collapses to one column on small screens;
- keeps the setup wizard body scrollable so all required User 1 and User 2 fields remain reachable on smaller or zoomed viewports;
- saves each user in place and leaves both user forms visible on the same setup screen; User 1 and User 2 registration actions must each become activatable when that user's own required fields are ready;
- groups registration inputs into readable Profile and Accounts/tools/Git sections instead of presenting one unstructured slab of fields;
- names missing required registration fields in the setup footer and on disabled registration action tooltips so a user can tell why User 1 or User 2 cannot yet be registered;
- keeps User 1 and User 2 identity colors independent from the currently active workstation user: User 1 registration/workflow surfaces stay warm amber and User 2 registration/workflow surfaces stay cool cyan even when the other user is active in the header;
- provides a checklist that shows which registration steps are complete;
- stores per-user defaults for repository path, handoff agent, and handoff title;
- provides Browse buttons for the main repository path and each user's default repository path so users can pick the local Git repository folder instead of typing a Windows path;
- keeps the main repository picker and rectangular Scan repository button directly inside the Working Tree panel so the user can see how to choose and scan a repo from the panel that displays repo state;
- stores a shared Project Files Tracker directory, defaulting to `C:\panda-gallery`, with a Browse button;
- opens Windows path picker dialogs with high-DPI awareness so Browse windows render crisply on high-resolution displays whenever Windows allows it;
- treats `C:\panda-gallery\skills\pg-project-sync\MANIFEST.md` as the existing canonical project-files manifest and preserves the existing `pgsync` flow that creates `workflows\project_knowledge_sync_YYYY-MM-DD` bundles for Claude.ai project files;
- requires per-user Codex account label, Claude account label, Git author name, and Git author email during registration;
- requires per-user Claude Desktop path and Claude Code path during registration so each user profile identifies the local tools it is meant to use;
- provides Browse buttons for Claude Desktop and Claude Code paths so users can pick Windows paths instead of typing them by hand;
- stores only account labels, usernames, and emails, never passwords, tokens, API keys, recovery codes, or browser credentials;
- clearly records whether the two users are using the same repository path, which means they share the same git working tree and commit history;
- records Git author identity as context but does not switch Git credentials or perform Git hosting login;
- applies the active user's defaults to the repository and handoff controls;
- keeps the Repository panel Scan repository button available as a direct repository-only action; it must scan the typed or picked path and must not open registration;
- blocks handover, session start, and handoff creation until required setup fields are complete;
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
- `CODEX_open_panda_collaborator.ps1` starts the local server if needed and opens PC in the browser when the user explicitly launches PC. Automation, development restarts, and tests should pass `-NoBrowser` so they refresh the existing tab instead of spawning duplicate tabs.
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

### Control Shape Visual Grammar

PANDA must visually separate passive information from user actions.

- Information/status values must render as passive rounded pill chips. Examples: ready, idle, safe, branch, no repo, not scanned, counts, safety labels, active user labels, and other state-only indicators.
- Action controls must render as squared or lightly rectangular buttons. Examples: Handover, Register, Browse, Scan repo, Start Session, Create safe handoff, Save Message, Search, Preview restore safety, and setup navigation.
- A pill must never perform work when clicked. If an element performs work, changes state, opens a picker, switches a user, saves data, scans, or creates a package, it must be a rectangular action button.
- Disabled future actions may be visually dimmed or locked, but they must retain action-button shape so the user can tell they are unavailable commands, not passive information.
- Tabs and segmented controls are still actions; keep them rectangular even when compact.
- Every action button and every passive pill must provide a plain-language tooltip that tells the user what the item means or what will happen if clicked.
- The Create safe handoff button is the primary purpose action. It must be full-width or otherwise visually dominant in the Create Handoff panel, stay visible above secondary handoff actions, render grey when prerequisites are incomplete, and turn green only when the app state is ready to create the protected handoff package.
- Across the app, safe action buttons that can currently be clicked must render green. Disabled safe actions must render grey. Dangerous actions such as Emergency Pause may retain warning/red treatment while enabled.
- User identity colors are not button-ready colors. Amber and cyan identify User 1/User 2 surfaces; green identifies an activatable safe command.

### Mandatory UI Review Gate

Darrin has repeatedly flagged formatting and Bible regressions in PC. Every PC UI change must pass this gate before handoff:

1. Read the current Design Bible / Bible-derived PC rules before editing UI.
2. Run `python CODEX_ui_layout_applet.py` before and after the change.
3. Run `python -m unittest -v tests.test_panda_collaborator`.
4. Inspect the live browser at the actual viewport size being discussed.
5. Look specifically for repeated failure modes: overlapping buttons, button text clipping, hidden horizontal overflow, duplicate controls for one action, clickable pill-looking controls, green applied to non-actions, user identity colors used as readiness colors, and narrow-width grids that still force desktop columns.
6. Update this spec or the applet whenever Darrin identifies a new repeated visual failure.

Completion language must be evidence-based: name the applet, tests, and visual review performed. If a live browser check was not performed, say so plainly.

### Start Session Workflow

The app must provide a clear Start Session flow after a user presses a Hub Handover button for User 1 or User 2.

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
- use a single visible scrollbar in the Status Messages panel: the outer panel body clips overflow and the message body owns scrolling;
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
