# PANDA Collaborator Setup Steps

This is the simple way to open and set up PANDA Collaborator.

## What The Desktop Icon Does

The desktop icon starts PANDA Collaborator and opens it in your browser.

The app runs locally on your computer at:

```text
http://127.0.0.1:8788/
```

Nothing is sent to the internet by the app just because you open it.

## First-Time Setup

1. Double-click the **PANDA Collaborator** icon on your Desktop.
2. Wait a few seconds for your browser to open.
3. Registration should open automatically if setup is not finished.
4. Register **User 1** first.
5. Type the User 1 name.
6. Check the User 1 repo path. For this project it is usually:

```text
C:\CODEX PG
```

7. Check the User 1 agent name and handoff title.
8. Enter the User 1 Codex account label and Claude account label.
9. Enter the User 1 Claude Desktop path and Claude Code path.
10. Enter the User 1 Git author name and Git author email.
11. Click **Register User 1 and continue**.
12. Review the **User 1 registered** confirmation.
13. Click **Continue to User 2** when ready.
14. Register **User 2** next.
15. Type the User 2 name.
16. Check the User 2 repo path, agent name, and handoff title.
17. Enter the User 2 Codex account label and Claude account label.
18. Enter the User 2 Claude Desktop path and Claude Code path.
19. Enter the User 2 Git author name and Git author email.
20. Click **Register User 2 and open Hub**.

If a registration button is grey, setup is still missing something. The footer names the missing fields. Scroll inside the registration window if some account, Claude path, or Git identity fields are below the visible area.

PANDA should not jump straight from User 1 to User 2. It should show the User 1 confirmation first so the handoff point is obvious.

Use account names, login emails, or short labels only. Do not type passwords, API keys, tokens, recovery codes, or browser credentials into PANDA.

When setup is saved, the setup badge changes to **Ready**.

The active user's name appears in big letters at the top of the screen. User 1 uses a warm amber color theme. User 2 uses a cool cyan color theme.

The Collaborator Hub shows a **HANDOVER TO USER 1** button and a **HANDOVER TO USER 2** button. Pressing a handover button changes the active user, applies that user's saved defaults, saves the active user, changes the active-user header theme, and scans the repo.

Across the app, safe buttons turn green when they can be clicked. Grey buttons are unavailable because setup or another prerequisite is incomplete. Emergency Pause may stay red because it is a warning action.

If User 1 and User 2 both use the same repo path, they share the same git working tree and commit history. PANDA records each user's Git author name/email for handoff context, but it does not log in to GitHub or switch Git credentials for you.

## Daily Use

1. Open PANDA Collaborator from the desktop icon.
2. Use the **Collaborator Hub**.
3. Press **HANDOVER TO USER 1** or **HANDOVER TO USER 2** for the person who is using the app.
4. Confirm that the big name at the top of the screen matches that person.
5. Press **Start Session / Start Work**.
6. Let PANDA run the automatic checklist.
7. Review the plain-English latest handoff summary, concerns, achievements, and recommended next action.
8. Review the **Working Tree** numbers and **Changed Files** list after the automatic scan.
9. Use the quick message box for short notes, concerns, achievements, or next steps.
10. If something looks unsafe, click **Emergency Pause**.
11. When work is done, fill in handoff notes if useful.
12. Click **End Session / Handoff**.

The app creates a handoff package with:

- a protection branch for committed work;
- patch files for uncommitted work;
- file copies for changed and new files;
- a `HANDOFF.md` summary;
- a `manifest.json` record with the active user, Codex account label, Claude account label, Git author identity, repo path, branch, `HEAD`, current status, and your notes.

That handoff record is what the next Claude or Codex session should read first so history and context are not lost.

PANDA also saves:

- project messages;
- timeline events;
- daily reports;
- plain-English summaries;
- technical summaries.

Use the **Manager**, **Timeline**, and **Search** views to review old context without digging through folders.

## Reading Old Handoffs

1. Click **Packages**.
2. Pick a package from the list.
3. Click **Inspect package**.

This lets you read what was saved without changing your files.

## Safety In Plain English

PANDA Collaborator is designed not to lose work.

It does not:

- throw away unsaved work;
- clean folders;
- force push;
- delete branches;
- stash work as its safety plan;
- switch branches for you;
- merge or rebase for you.

Its job is to make a safe package that another person or AI can inspect.

## If The Browser Does Not Open

1. Double-click the desktop icon again.
2. If it still does not open, open your browser manually.
3. Type this into the address bar:

```text
http://127.0.0.1:8788/
```

## If The App Says It Is Already Running

That is okay. It means the local PANDA Collaborator server is already open in the background.

Open this address in your browser:

```text
http://127.0.0.1:8788/
```

## Important Files

Desktop shortcut:

```text
C:\Users\drrap\OneDrive\Desktop\PANDA Collaborator.lnk
```

App folder:

```text
C:\CODEX PG\CODEX PANDA Collaborator
```

Settings file:

```text
C:\CODEX PG\CODEX PANDA Collaborator\CODEX settings\panda_collaborator_settings.local.json
```

The settings file is local to this computer and is not committed to git.
