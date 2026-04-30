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
3. The setup wizard should open automatically if setup is not finished.
4. Type the name for the first user.
5. Type the name for the second user.
6. Click the user button for the person who is using the app right now.
7. Check the repo path. For this project it is usually:

```text
C:\CODEX PG
```

8. Check the agent name. This is the name that will be written into handoff packages.
9. Check the handoff title. This is the default title for a new handoff.
10. Click **Save setup and scan**.

When setup is saved, the setup badge changes to **Ready**.

The active user's name appears in big letters at the top of the screen. User 1 uses a warm amber color theme. User 2 uses a cool cyan color theme.

## Daily Use

1. Open PANDA Collaborator from the desktop icon.
2. Make sure the correct user is selected in the **Setup** panel.
3. Confirm that the big name at the top of the screen matches the person using the app.
4. Click **Apply defaults** if you want to load that user's saved repo and handoff defaults.
5. Click **Scan**.
6. Review the **Working Tree** numbers and **Changed Files** list.
7. If you need to hand work to another AI or another user, fill in the handoff notes.
8. Click **Create safe handoff**.

The app creates a handoff package with:

- a protection branch for committed work;
- patch files for uncommitted work;
- file copies for changed and new files;
- a `HANDOFF.md` summary.

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
