# PANDA Collaborator — Repository Protection & Credential Scope Spec
# Version: 1.0
# Date: 2026-05-04
# Owner: Darrin (PandaPerio)
# Audience: CC, CD, Codex, testers
# Depends on: PRODUCTION_SPEC.md, PC_DATA_SAFETY_BACKUP_SPEC_v1.0.md

---

## 1. Purpose and Scope

This spec defines two independent protection layers that prevent any PG-related application from deleting, force-overwriting, or corrupting a GitHub repository:

**Layer A — GitHub server-side enforcement:** Branch protection rules and a scoped Personal Access Token (PAT) ensure that even if all local software were bypassed, the GitHub server would reject destructive operations.

**Layer B — PC client-side runtime validation:** PANDA Collaborator validates at startup and at session start that its own safety enforcement is active and that the git credential in use is not admin-scoped. A failed startup self-test prevents PC from starting entirely. An over-privileged credential surfaces a persistent non-dismissible red banner but does not block git operations — PC's code-level enforcement remains active regardless of credential scope.

This spec does NOT restate the `FORBIDDEN_GIT_COMMANDS` enforcement already implemented in `panda_collaborator.py`. That enforcement is assumed to be in place and is referenced here as the baseline.

---

## 2. What Is Already Protected (Baseline)

The following protections are already implemented in the live codebase and require no new work:

| Protection | Implementation | Location |
|---|---|---|
| Forbidden git commands blocked | `assert_git_args_safe()` raises `SafetyError` | `panda_collaborator.py` |
| Dangerous git verbs blocked | `DANGEROUS_GIT_VERBS` set checked before every `safe_git()` call | `panda_collaborator.py` |
| No passwords or tokens stored | `normalize_settings()` strips all non-label fields; `normalize_operator_context()` documents this contract | `panda_collaborator.py` |
| No automated restore | `automated_restore_available: False` in all restore preview responses | `panda_collaborator.py` |

This spec adds protection that holds even when PC is not running.

---

## 3. Layer A — GitHub Server-Side Enforcement

### 3.1 Scoped Personal Access Token (PAT)

#### 3.1.1 Why a scoped PAT is required

When git authenticates to GitHub with full account credentials (username + password, or a full-scope OAuth token), those credentials carry admin permissions. Admin permissions allow repository deletion, settings changes, and force-push overrides of branch protection rules — even if branch protection is enabled. A scoped PAT removes these permissions at the source.

#### 3.1.2 PAT generation (one-time, done by Darrin in GitHub)

1. Go to `github.com` → Settings → Developer Settings → Personal access tokens → Fine-grained tokens → Generate new token.
2. Token name: `PANDA Collaborator — PANDA-Gallery repo access`
3. Expiration: 1 year (set a calendar reminder to rotate before expiry)
4. Repository access: **Only selected repositories** → select `DarrinRap/PANDA-Gallery` and `<backup-account>/PANDA-Gallery-backup`
5. Permissions — set exactly:

| Permission | Level |
|---|---|
| Contents | Read and write |
| Metadata | Read (auto-selected) |
| All other permissions | No access |

6. Click Generate token. Copy the token immediately — it will not be shown again.
7. Store the token in Windows Credential Manager (see §3.1.3). Do NOT paste it into any PC settings file, any chat, or any document.

#### 3.1.3 Configure git to use the PAT (PowerShell, one-time per user)

Run this once for each Windows user account on the shared workstation. Replace `<token>` with the actual PAT value and `<github-username>` with the GitHub username for that user.

```powershell
git config --global credential.helper manager
"protocol=https`nhost=github.com`nusername=<github-username>`npassword=<token>`n" | git credential approve
```

This stores the PAT in Windows Credential Manager under the `git:https://github.com` entry. Git uses it automatically for all HTTPS operations. The PAT is never written to disk in plaintext by PC or by git config.

**Verify the credential is stored:**
```powershell
"protocol=https`nhost=github.com`n" | git credential fill
```
Expected output includes `username=<github-username>` and `password=<token>`. If it prompts interactively, the credential was not stored correctly.

#### 3.1.4 PAT rotation

PATs expire. Expired PATs cause push failures. PC will surface these as Step 2b failures in the progress window with a specific error message: *"Authentication failed — your GitHub token may have expired. Rotate your PAT in GitHub Settings."*

When rotating: generate a new PAT with identical scope, store it via `git credential approve` as above, then delete the old token from GitHub Settings → Developer Settings → Personal access tokens.

### 3.2 GitHub Branch Protection Rules

These rules are configured once in GitHub's web UI. They apply server-side and cannot be overridden by any local git command, regardless of what software is running on the workstation.

Navigate to: `github.com/DarrinRap/PANDA-Gallery` → Settings → Branches → Add branch protection rule.

Apply to branch name pattern: `main`

| Rule | Setting | Why |
|---|---|---|
| Require a pull request before merging | Off | Two-person project; PRs add friction without benefit |
| Require status checks to pass | Off | No CI configured |
| Require conversation resolution | Off | Not applicable |
| Require signed commits | Off | Adds complexity without benefit for this project |
| **Require linear history** | Off | Merge commits are acceptable |
| **Do not allow bypassing the above settings** | On | Prevents admin from force-overriding their own rules |
| **Allow force pushes** | Off | Prevents `git push --force` to `main` reaching GitHub even if run outside PC |
| **Allow deletions** | Off | Prevents `git branch -d main` or `git push origin --delete main` |

Apply the same rules to the backup repository (`<backup-account>/PANDA-Gallery-backup` → Settings → Branches → `main`).

**For `handoff/*` branches on the backup repo:** Do NOT apply branch protection. Handoff branches are package artifacts with unique names — each is written once and never updated. Branch protection on `handoff/*` would require a separate rule and adds no value since these branches are append-only by PC's own logic.

### 3.3 What server-side protection blocks

With a scoped PAT + branch protection in place, the following operations fail at the GitHub server even if attempted outside PC:

| Operation | Blocked by |
|---|---|
| `git push --force origin main` | Branch protection: Allow force pushes = Off |
| `git push origin --delete main` | Branch protection: Allow deletions = Off |
| Delete repository from GitHub UI | Scoped PAT has no admin permission |
| Change repository settings | Scoped PAT has no admin permission |
| Disable branch protection rules | Scoped PAT has no admin permission |
| Push commits that don't pass checks | Not applicable (no CI configured) |

---

## 4. Layer B — PC Client-Side Runtime Validation

### 4.1 Startup safety self-test

PC runs a self-test that confirms the safety enforcement is live on every startup. This is a lightweight in-process check — no git commands are run.

**Self-test procedure:**

For each command in `FORBIDDEN_GIT_COMMANDS`:
1. Split the command string on whitespace: e.g. `"git reset --hard"` → `["git", "reset", "--hard"]`.
2. Drop `args[0]` (the literal string `"git"`), leaving the subcommand args: `["reset", "--hard"]`.
3. Call `assert_git_args_safe(["reset", "--hard"])`.
4. Expect `SafetyError` to be raised.
5. If `SafetyError` is NOT raised, the safety enforcement has been bypassed — PC must not start.

If any forbidden command passes the safety check without raising:
- Print to stderr: `FATAL: Safety enforcement failure — [command] was not blocked. PANDA Collaborator will not start.`
- Exit with code 2.
- Do not open the HTTP server.

**Self-test integration point:**

The self-test runs in `cli()` as the very first action, before any dispatch branch (`--scan`, `--create-handoff`, or `serve()`). This ensures all execution paths are protected — not just the HTTP server path.

```python
def cli(argv=None):
    # ... argparse setup ...
    run_startup_safety_self_test()   # <-- first, before any branch
    if args.scan:
        ...
    elif args.create_handoff:
        ...
    else:
        serve(args.host, args.port)
```

`run_startup_safety_self_test()` is a new top-level function that encapsulates the self-test logic and calls `sys.exit(2)` on failure. **The self-test is not skippable.** There is no `--skip-safety-test` flag or environment variable bypass.

### 4.2 Credential scope validation

At session start (`start_session()`) and before creating any handoff package (`create_handoff_package()`), PC probes the git credential scope to detect over-privileged tokens.

**Probe procedure:**

PC makes a lightweight authenticated GitHub API call using the configured git credential:

```
GET https://api.github.com/user
Authorization: Bearer <token from git credential store>
```

Parse the response. Extract `"site_admin"` field and the token's OAuth scopes from the `X-OAuth-Scopes` response header.

**Classify the credential:**

| Condition | Classification | PC action |
|---|---|---|
| `site_admin: true` | Admin — over-privileged | Hard warn (§4.3) |
| `X-OAuth-Scopes` includes `delete_repo` | Admin — over-privileged | Hard warn (§4.3) |
| `X-OAuth-Scopes` includes `admin:repo_hook` | Over-privileged | Soft warn (§4.3) |
| `X-OAuth-Scopes` includes `repo` but no admin sub-scopes | Acceptable | No warning |
| `X-OAuth-Scopes` is empty or read-only (`public_repo` only) | Insufficient scope — cannot push | Soft warn: "Token is read-only. Push operations will fail." |
| Fine-grained PAT (no `X-OAuth-Scopes` header present) | Acceptable — fine-grained PATs don't use this header | No warning |
| API call fails (no network, wrong host, timeout) | Unknown | Log to timeline, no banner, do not block |
| API call returns 401 | Token invalid or expired | Surface in progress window as Step 2b/2c failure with PAT rotation instructions |

**Credential retrieval for the probe:**

PC retrieves the stored git credential by calling subprocess directly (not via `safe_git()` or `run_command()`, since this is not a git repository operation and requires stdin input):

```python
result = subprocess.run(
    ["git", "credential", "fill"],
    input="protocol=https\nhost=github.com\n\n",
    capture_output=True,
    text=True,
    timeout=10,
)
```

Parse `username` and `password` fields from `result.stdout` (format: one `key=value` per line). Use the `password` value as the Bearer token for the API probe. Do not log the password field. Discard the token value after the probe — do not store it in memory beyond the single API call. If the command fails or returns no password field, classify as Unknown.

**Multi-user credential note:**

Both users share the same Windows Credential Manager on the shared workstation. The credential stored under `git:https://github.com` applies to all git operations regardless of which PC user is active. However, since User 1 and User 2 may have different GitHub accounts (and therefore different PATs), each user must store their own PAT when they log into their Windows user session.

If the credential scope probe returns a different result for different Windows user accounts:
- Each user's scope result is stored separately in the per-server-process cache, keyed by the `username` field returned from `git credential fill`.
- The banner shown reflects the scope of the currently active Windows session's credential — not the other user's credential.

If both users share a single Windows user account (same Windows login), only one PAT is in play and the above distinction does not apply.

### 4.3 Scope warning behavior

**Hard warn (admin credential detected):**
- PC shows a prominent red banner at the top of the main view: *"⚠️ Over-privileged credential detected — your GitHub token has admin or delete-repo access. This means PC's local safety enforcement can be bypassed at the GitHub level. Switch to a scoped PAT immediately."*
- Banner persists until the credential scope check passes — either after the user triggers "Re-check credential scope" (§5) or after PC restarts with the correct PAT in place.
- PC does NOT block git operations — enforcement is still PC's code-level checks. The warning is informational, not a hard block, because the user may be in the middle of a session. However, the banner must not be dismissible — it stays until the credential scope check passes.

**Soft warn (elevated but not admin):**
- Amber banner: *"⚠️ Your GitHub token has elevated permissions. Consider switching to a scoped PAT with Contents read/write only."*
- Dismissible by the user.

**Unknown (API unreachable):**
- Log to activity timeline: `"Credential scope check skipped — GitHub API unreachable."`
- No user-visible banner.

### 4.4 Credential scope check — what PC never does

- PC never stores the token value retrieved from `git credential fill`.
- PC never sends the token to any service other than `api.github.com`.
- PC never modifies, deletes, or replaces git credentials.
- PC never prompts the user to enter credentials directly.

---

## 5. Session-Start Checklist Updates

The existing `start_session()` checklist is extended with two new items:

| Check | Pass condition | Fail behavior |
|---|---|---|
| Safety self-test passed at startup | `FORBIDDEN_GIT_COMMANDS` test passed on server start | PC would have exited at startup if failed; this check is always PASS at runtime |
| Git credential scope acceptable | Scope check returned Acceptable or Unknown | Start Work remains available; hard/soft banner shown per §4.3 |

The credential scope check result is cached for the lifetime of the server process — it runs once at session start and is not re-checked on subsequent `start_session()` calls within the same server run. It re-runs on the next PC server restart or if the user explicitly triggers "Re-check credential scope" in the Working Tree panel.

---

## 6. Setup Checklist Summary (Darrin)

One-time actions required outside of PC:

| # | Action | Where | Est. time |
|---|---|---|---|
| 0 | Create backup GitHub repository (prerequisite — see `PC_DATA_SAFETY_BACKUP_SPEC_v1.0.md` §9.1 for instructions) | github.com | 3 min |
| 1 | Generate fine-grained PAT (Contents read/write, both repos scoped, no admin) | github.com → Settings | 5 min |
| 2 | Store PAT in Windows Credential Manager via `git credential approve` | PowerShell | 2 min |
| 3 | Enable branch protection on `main` (PANDA-Gallery origin repo) | github.com → Repo Settings | 5 min |
| 4 | Enable branch protection on `main` (backup repo) | github.com → Backup Repo Settings | 5 min |
| 5 | Verify PAT is stored correctly via `git credential fill` | PowerShell | 2 min |
| 6 | Set calendar reminder for PAT rotation (1 year from creation) | Calendar | 1 min |

Total: approximately 23 minutes.

---

## 7. Design Constraints (Non-Negotiable)

- Startup self-test cannot be skipped or disabled.
- PC never stores git credentials; it only reads them transiently for the scope probe.
- Hard warn banner for over-privileged credentials cannot be dismissed.
- Credential scope probe results are never logged at a level that captures the token value.
- PAT generation and storage are user actions; PC provides instructions but never generates, stores, or rotates PATs.
- Branch protection configuration is a GitHub web UI action; PC cannot configure remote repository settings.

---

## 8. Open Items

- Whether the credential scope check should run on a background thread or block the session-start response until complete. Recommendation: background thread with a 5-second timeout; if it times out, classify as Unknown and surface in the activity log only.
- Whether to expose a "Re-check credential scope" button in the UI or only allow re-check on server restart. Recommendation: expose the button in the Working Tree panel alongside "Scan Working Tree".
- Whether PAT rotation reminders should be surfaced inside PC (e.g., 30 days before expiry) by storing the PAT creation date in settings. Recommendation: yes — store PAT creation date (not the token) in the settings file and surface an amber reminder 30 days before expiry.

---

## 9. Downstream Spec Updates Required

**PRODUCTION_SPEC.md** — Add a note that the forbidden command list is verified at startup via the self-test described in §4.1 of this spec.

**PC_DATA_SAFETY_BACKUP_SPEC_v1.0.md** — §8 (Branch Protection Rules) is now superseded by §3.2 of this spec which is more complete. Reference this spec for the authoritative branch protection table.
