# PANDA Collaborator — Data Safety & GitHub Backup Spec
# Version: 1.0
# Date: 2026-05-04
# Owner: Darrin (PandaPerio)
# Audience: CC, CD, Codex, testers

---

## 1. Core Principle

**No work performed in a PANDA Collaborator session shall ever be permanently lost.**

This is not a guideline. It is an inviolable constraint that overrides convenience, speed, and implementation simplicity at every decision point.

The existing PRODUCTION_SPEC.md addresses data safety within a single handoff: protection branches, patch files, and file copies guard committed and uncommitted work during the transfer between users. This spec extends that guarantee to the level of the GitHub repository itself — ensuring that if the local workstation fails, if a repository becomes corrupted, or if a push to the main remote fails, all work remains recoverable from a backup source.

---

## 2. Identified Gaps in Current Protection Model

The current PC production safety model has three gaps this spec closes:

**Gap 1 — Protection branches are local only.**
PRODUCTION_SPEC.md creates a protection branch at HEAD without checking it out. That branch exists only on the local machine. If the workstation fails before the incoming user's first push, the protection branch — and the commit history it points to — may be unrecoverable.

**Gap 2 — Handoff packages are local only.**
The patch files, file copies, manifest.json, and HANDOFF.md live in a local package directory. They are not pushed anywhere. A disk failure between handoff creation and the incoming user reading the package destroys the recovery data.

**Gap 3 — No backup repository.**
The main PANDA-Gallery GitHub repository is the single authoritative remote. If it becomes unavailable (GitHub outage, accidental deletion, repository corruption, or account compromise), there is no secondary source to recover from.

---

## 3. Backup Architecture

### 3.1 Three-layer model

| Layer | What it protects | Where it lives |
|---|---|---|
| L1 — Session commits | All committed work during a session | Local repo + main GitHub remote |
| L2 — Handoff package | Committed HEAD + uncommitted changes at handoff time | Local package dir + backup GitHub remote |
| L3 — Repository mirror | Full repository history and all branches | Backup GitHub remote (auto-synced) |

### 3.2 Backup GitHub remote

A dedicated backup repository must be configured as a second remote (`backup`) alongside the existing `origin`. This is a separate GitHub repository, either:
- Under a dedicated backup GitHub account (e.g. `PandaPerio-backup`)
- Or under a GitHub Organization set up specifically for backup purposes

The backup remote is not a fork. It is a separate repository that receives explicit pushes from PC at defined trigger points. It is private.

```
origin  → github.com/DarrinRap/PANDA-Gallery     (primary — existing)
backup  → github.com/PandaPerio-backup/PANDA-Gallery-backup  (new)
```

Both remotes must be configured in the local `.git/config` of the PANDA-Gallery repository on the shared workstation.

### 3.3 Handoff package backup

In addition to local storage, every handoff package is pushed to the backup remote as a uniquely named branch immediately after local package creation succeeds (before the outgoing confirmation screen is shown). The branch name encodes the package ID and timestamp for traceability.

Format: `handoff/<package_id>/<YYYYMMDD_HHMMSS>`

Example: `handoff/pkg-2026-05-04-001/20260504_194532`

The handoff package branch contains a single commit with all package artifacts committed (patches, file copies, manifest, HANDOFF.md). Handoff branches are append-only — they are never rebased or force-pushed.

---

## 4. Save-Before-Publish Workflow

### 4.1 Principle

Work is always saved to the backup remote before being considered durable. The incoming user does not start work until they can confirm the handoff data is retrievable from a source independent of the local disk.

### 4.2 Session commit workflow (outgoing user)

Before creating a handoff package, the outgoing user must have all session work committed and pushed to both remotes. PC enforces this in Steps 2b and 2c of the progress window:

1. **Commit gate:** PC checks that the working tree is clean (or the user has explicitly acknowledged uncommitted changes that will be captured by the patch mechanism).
2. **Step 2b — Push to origin:** `git push origin HEAD` (pushes the current branch, regardless of name). Must succeed before handoff package creation begins.
3. **Step 2c — Push to backup:** `git push backup HEAD` (pushes the same current branch to the backup remote). Must succeed before handoff package creation begins.
4. If either push fails, PC displays the failure in the progress window (Step 2b: Push to origin; Step 2c: Push to backup) with specific remediation and blocks handoff package creation until both succeed.

After Steps 2b and 2c succeed, a full mirror (`git push backup --mirror`) is run automatically (see §5.1) to sync all branches and refs to the backup remote — not just the current branch.

### 4.3 Handoff package push to backup

After the local artifact steps complete (Steps 3–7b per §7 of this spec and HANDOFF_PROGRESS_SPEC_v1.1), the progress window runs one final step before marking the handoff complete:

**Step 8 — Push handoff package to backup remote (NEW)**

- Creates a branch `handoff/<package_id>/<timestamp>` in the local repo
- Commits all package artifacts to that branch (patches as binary blobs, file copies, manifest, HANDOFF.md)
- Pushes that branch to `backup` remote: `git push backup handoff/<package_id>/<timestamp>`
- Marks PASS only when the remote push is confirmed

This step is classified as **Component** (same as Steps 3-7b): failure does not stop other steps from running, but it does classify the handoff as INCOMPLETE and blocks "Hand Off to [User Name]" per the hard-block rule.

**Rationale:** Step 8 is the bridge between the local-only guarantee and the off-machine guarantee. A handoff is not fully safe until its package exists on a remote that survives workstation failure.

### 4.4 Incoming user session start

When the incoming user clicks Start Session, PC performs an additional verification step before enabling Start Work:

- Fetches from backup remote: `git fetch backup`
- Confirms the expected `handoff/<package_id>/<timestamp>` branch exists on backup
- Reports: "✅ Handoff package verified on backup remote" or "⚠️ Handoff package not found on backup — local copy only"

If only local copy is confirmed (backup push failed or was skipped), the incoming user sees a warning banner but is not blocked from starting — the local package still exists and work can proceed. This is a degraded-but-not-blocked state, not a hard block.

---

## 5. Repository Mirroring

### 5.1 Full mirror on every push

Every push to `origin` is accompanied by a mirror push to `backup`. PC adds this as an automatic step after every successful `git push origin` command it initiates. The mirror push uses:

```
git push backup --mirror
```

This copies all branches, tags, and refs (not just main) to the backup remote.

### 5.2 Mirror cadence

| Event | Origin push | Backup mirror |
|---|---|---|
| Session-start push (Steps 2b/2c) | working branch pushed | working branch pushed |
| Handoff package creation (Step 8) | nothing new (branch already pushed in 2b) | handoff package branch pushed |
| Any explicit `git push` via PC | ✓ | ✓ |

PC does NOT run background or scheduled mirrors without user action. Every mirror is triggered by an explicit PC workflow step.

### 5.3 Mirror failure handling

If a mirror push to `backup` fails:
- PC logs the failure to the activity timeline with timestamp and error text
- PC shows an amber warning in the status bar: "⚠️ Backup mirror failed — [error summary]. Local and origin are current."
- PC does NOT block the user from continuing work
- PC recommends retrying the mirror: a "Retry backup push" button appears in the working-tree panel

Mirror failure is never a hard block. Origin is the authoritative remote. Backup is a safety layer — its failure degrades safety but does not halt work.

---

## 6. Recovery Procedures

### 6.1 Scenario: workstation disk failure before incoming user starts

**Recovery path:**
1. Set up git on replacement machine.
2. Clone from `origin` (primary GitHub): `git clone https://github.com/DarrinRap/PANDA-Gallery`
3. Add the backup remote: `git remote add backup https://github.com/<backup-account>/PANDA-Gallery-backup.git`
4. Fetch all backup branches: `git fetch backup`
5. Locate the latest handoff branch: `git branch -r | grep handoff/`
6. Check out the handoff branch and extract package artifacts (patches, file copies) from the committed content.
7. Apply patches manually if needed: `git apply unstaged-working-tree.patch`
8. Resume work from the recovered state.

### 6.2 Scenario: GitHub origin unavailable

**Recovery path:**
1. Do NOT rename or re-point origin during an outage — keep origin URL intact so it auto-recovers when GitHub restores service.
2. For read-only access to existing work: `git fetch backup` to retrieve the latest mirrored state.
3. Continue working locally and committing locally. Do not push until origin is confirmed reachable.
4. When origin is restored, push all pending commits: `git push origin HEAD`
5. Run a full backup mirror to re-sync: `git push backup --mirror`

### 6.3 Scenario: accidental force-push or branch deletion on origin

**Recovery path:**
1. The backup mirror (last successful sync) contains the deleted branch or pre-force-push state.
2. Fetch from backup: `git fetch backup`
3. Verify the branch exists on backup: `git branch -r | grep backup/<branch-name>`
4. Re-push to origin from the backup remote-tracking ref: `git push origin refs/remotes/backup/<branch-name>:refs/heads/<branch-name>`

### 6.4 Scenario: handoff package missing from local disk

The incoming user's escape hatch flow (per HANDOFF_PROGRESS_SPEC_v1.1 §8.3) is extended:

If the local handoff package is missing, PC automatically checks the backup remote for the expected handoff branch before showing the escape hatch. If found on backup:
- PC downloads the package artifacts from the backup branch.
- PC shows: "✅ Handoff package recovered from backup remote."
- Session start proceeds normally — no escape hatch needed.

If not found on backup either, the escape hatch fires as specified in HANDOFF_PROGRESS_SPEC_v1.1 §8.3.

---

## 7. Step Classification Update

This spec adds new steps to the handoff creation progress window, extending the step table in HANDOFF_PROGRESS_SPEC_v1.1 §7.1:

| Step | Description | Class |
|---|---|---|
| 1 | Resolve selected path to git root | Foundational |
| 2 | Read branch, HEAD, and porcelain status | Foundational |
| 2b | Push current branch to origin | Foundational |
| 2c | Push current branch to backup remote | Component |
| 3 | Create protection branch at HEAD | Component |
| 4 | Write unstaged-working-tree.patch | Component |
| 5 | Write staged-index.patch | Component |
| 6 | Copy changed tracked and untracked files | Component |
| 7a | Write manifest.json | Component |
| 7b | Write HANDOFF.md | Component |
| 8 | Push handoff package branch to backup remote | Component |

**Note on Steps 2b and 2c:** These are new pre-package-creation steps. Step 2b is **Foundational** because a failed push to origin means the outgoing user's session commits are not safely off-machine — creating a handoff package against uncommitted-to-remote work would be misleading. Step 2c is **Component** because backup push failure degrades but does not eliminate safety (origin still has the commits).

**Progress window display:** The total step count shown in the "Step N of M" label is 11. Steps are displayed in order with plain-English labels — the alphanumeric suffixes (2b, 2c, 7a, 7b) are internal spec identifiers only. In the progress window UI, they display as: "Push to GitHub (origin)", "Push to backup remote", ..., "Write manifest", "Write handoff document", "Upload package to backup". The displayed label does not include the step number suffix.

---

## 8. Branch Protection Rules (GitHub Settings)

The following branch protection rules must be configured on the `origin` repository (github.com/DarrinRap/PANDA-Gallery) and mirrored equivalently on `backup`:

| Rule | Setting |
|---|---|
| Protect `main` branch | Enabled |
| Require pull request reviews | Disabled (two-person solo project; PRs not used) |
| Disallow force pushes to `main` | Enabled |
| Disallow branch deletion of `main` | Enabled |
| Require status checks | Disabled (no CI configured) |
| Allow force pushes to `handoff/*` | Disabled — handoff branches are append-only; each package gets a unique branch name and is never updated or rebased |

These rules must be set manually in GitHub Settings. PC cannot configure remote repository settings.

---

## 9. Setup Requirements (One-Time)

### 9.1 Create backup repository

Done once by Darrin outside of PC:
1. Create a new private GitHub repository: `PandaPerio-backup/PANDA-Gallery-backup` (or chosen account/name).
2. Do not initialize with any files.

### 9.2 Add backup remote to local repo

Done once in PowerShell on the shared workstation:

```powershell
cd "C:\CODEX PG\CODEX PANDA Collaborator"
git remote add backup https://github.com/<backup-account>/PANDA-Gallery-backup.git
git push backup --mirror
```

Verify: `git remote -v` should show both `origin` and `backup`.

**Note:** The `C:\panda-gallery` repository (the PG app code) is a separate repo. If Darrin also wants backup protection for `C:\panda-gallery`, repeat the above steps from `C:\panda-gallery` pointing to a second backup repo. The two repos require two separate backup remotes.

### 9.3 PC setup screen additions

PC's registration/setup screen must include a "Backup Remote" field:
- Label: "Backup GitHub remote URL"
- Validated against: `git ls-remote <url>` at registration time (confirms the remote exists and is reachable)
- Stored per-project in settings (not per-user — both users share the same backup remote for the same repo)
- Browse is not applicable (URL field only)
- Required before handoff package creation is enabled — PC must know the backup remote URL to perform Step 8

**First-sync state:** If the backup remote is newly configured and has never been synced (empty repository), PC detects this at the first Step 2c push and runs an initial full mirror automatically: `git push backup --mirror`. This is the one time PC initiates a mirror without an explicit user trigger, and it is shown in the progress window as Step 2c: "Initial sync to backup remote (first-time setup)". Subsequent mirrors follow the standard trigger model (§5.2).

---

## 10. Design Constraints (Non-Negotiable)

- The backup remote URL is required before handoff creation is enabled. There is no bypass.
- Step 2b (push to origin) is Foundational — failed origin push blocks handoff package creation.
- Step 8 (push to backup) is Component — failed backup push classifies handoff as INCOMPLETE and blocks "Hand Off to [User Name]" per the hard-block rule in HANDOFF_PROGRESS_SPEC_v1.1 §7.4.
- Mirror pushes never run in the background without a triggering user action in PC.
- All git commands forbidden in PRODUCTION_SPEC.md §Absolute Safety Rules are equally forbidden in this spec against both `origin` and `backup` remotes. This includes but is not limited to: `git reset --hard`, `git clean -fd`, `git push --force`, `git push -f`, `git branch -D`, `git push origin --delete`.
- Handoff branches on backup are append-only: PC never deletes, force-pushes, or rebases them.
- Recovery procedures are manual. PC provides the information and commands; it never auto-applies patches or auto-resolves conflicts.
- Credentials for the backup remote are never stored in plaintext in settings files. Git's own credential manager (Windows Credential Manager on the shared workstation) handles authentication.

---

## 11. Open Items

- **Credential handling (resolved):** Backup remote credentials are managed by Windows Credential Manager on the shared workstation — the same mechanism Git uses for `origin`. PC does not store, prompt for, or rotate credentials. Each user authenticates to the backup remote through their own Windows session. No settings-file changes required for credential management.
- Whether handoff package branches on the backup remote should be auto-pruned after N days. Recommendation: never auto-pruned — storage is cheap; recovery history is invaluable.
- Whether PC should display a running count of successful backup mirrors in the Project Manager view (e.g. "Last backup: 4 minutes ago"). Recommendation: yes — visible backup recency builds operator confidence.
- Whether Step 2b/2c (push to remotes) should be gated on a "commit all pending work" prompt if the working tree is dirty. Recommendation: yes — PC should offer a "Commit all with message" quick-commit flow before Step 2b fires, to ensure dirty work is captured in the push.
