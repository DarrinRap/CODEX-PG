# PANDA Collaborator — Handoff Protocol & Progress Window Spec
# Version: 1.0
# Date: 2026-05-04
# Owner: Darrin (PandaPerio)
# Audience: CC, CD, Codex, testers

---

## 1. Scope

This spec covers three tightly related PC design decisions confirmed in the 2026-05-04 design session:

1. The outgoing/incoming user handoff confirmation screens
2. The progress window (real-time step visibility, 1–100%, PASS/FAIL)
3. Failure handling during handoff package creation (stop vs. continue vs. hard block)

It does NOT cover the full PC production safety model (see PRODUCTION_SPEC.md) or the UI/UX redesign (see CODEX_PC_UI_UX_RED_DESIGN_SPEC_v1.md). Those documents remain authoritative for their domains. This spec adds to them; it does not supersede them.

---

## 2. Confirmed Environment Facts

These facts are locked. All design decisions in this spec derive from them.

| Fact | Detail |
|---|---|
| Workstation | Single shared Windows PC |
| Simultaneous use | Never — one user works at a time |
| Codex / Claude Desktop / Claude Code | Same installation; each user logs in with their own account |
| GitHub accounts | Separate per user |
| Shared repo | Both users push/pull from the same PANDA-Gallery repository |
| Gap between sessions | May be hours or days — PC must survive restarts |

---

## 3. Nomenclature (Locked)

| Term | Definition |
|---|---|
| Outgoing user | The developer finishing their work and handing off |
| Incoming user | The developer taking over and starting work |
| Handoff package | Protection branch + patch files + file copies + manifest + HANDOFF.md |
| Foundational step | A step whose failure makes all subsequent steps meaningless |
| Component step | An independently executable protection layer that should run regardless of sibling step outcomes |
| Hard block | A state where PC refuses to proceed; no override path exists |

---

## 4. Handoff Confirmation Screens

### 4.1 Rationale

PC cannot close Claude Desktop or Claude Code — it is a browser-based local web app with no OS-level process control. The outgoing user must manually close their sessions. This must be made explicit and unbypassable.

### 4.2 Outgoing User Confirmation Screen

**Trigger:** Fires immediately after the handoff package is created successfully (all steps PASS or all failures resolved per §7).

**Appearance:**
- Full-screen modal overlay in the outgoing user's identity color
- Cannot be dismissed by clicking outside, pressing Escape, or any passive gesture
- Single large rectangular action button: "Hand off to [Incoming User Display Name]"

**Required copy (exact wording):**
> Handoff package created successfully.
>
> Before you hand over:
> 1. Close your Claude Desktop session.
> 2. Close your Claude Code session.
> 3. Log out of your GitHub account if you remain at the workstation.
>
> When done, click the button below.

**[ Hand off to [User Name] ]**

**What the button does (in order):**
1. Writes the queued-incoming-user state to disk (§5.2) — this happens first, before any UI change.
2. Saves outgoing user state.
3. Applies incoming user defaults (repository path, agent, title).
4. Switches the UI color theme to the incoming user's identity color.
5. Scans the repository.
6. Logs the user switch to the timeline.
7. Shows the Incoming User Confirmation Screen (§4.3).

### 4.3 Incoming User Confirmation Screen

**Trigger:** Fires immediately after the outgoing user clicks "Hand off to [User Name]" on the outgoing confirmation screen (§4.2) and all state transitions complete (settings written, theme switched, repository scanned).

**Appearance:**
- Full-screen screen in the incoming user's identity color
- Displays the incoming user's display name in large uppercase text
- Shows a plain-English summary of the latest handoff package (what was done, concerns, recommended next action)
- Plain-English / Technical toggle available
- Single large rectangular action button: "Start Session"

**Required copy (exact wording):**
> Ready for [Incoming User Display Name] to start.
>
> 1. Open Claude Desktop and log in with YOUR account.
> 2. Open Claude Code and log in with YOUR account.
> 3. Review the handoff summary below.
>
> When ready, click Start Session.

**[Handoff summary — auto-loaded from latest package]**

**[ Start Session ]**

**What auto-show means:** This screen appears automatically when PC is opened after a handover — even if hours or days have passed (see §5). The incoming user sees it the instant they open the browser, before any other UI is reachable.

**Rationale for auto-show:** If there has been a gap, the incoming user sits down cold. Making them click a button before seeing the handoff summary creates a moment where they can skip it and open Claude Code without reading context. Auto-show removes that risk. The handoff summary IS the entry point. The only reachable action is Start Session.

---

## 5. Gap Period State Persistence

### 5.1 Requirement

PC must persist the queued-incoming-user state to disk immediately when the outgoing user clicks "Hand off to [User Name]" on the outgoing confirmation screen (§4.2). This state must survive:
- App close and reopen
- Browser tab close and reopen
- Workstation sleep and wake
- Workstation restart

### 5.2 Implementation

**Write trigger:** When the outgoing user clicks "Hand off to [User Name]" on the outgoing confirmation screen (§4.2), write the following to the local settings file before any UI transition occurs:

```json
{
  "handover_pending": true,
  "incoming_user_slot": "user_1",
  "handover_timestamp": "<ISO 8601 timestamp>",
  "handoff_package_id": "<stable package ID>"
}
```

Note: `incoming_user_slot` is a string value — either `"user_1"` or `"user_2"` depending on which user is the incoming user.

**Read trigger:** On every PC launch, read this state before rendering any UI. If `handover_pending: true`, show the Incoming User Confirmation Screen (§4.3) immediately. No other UI is shown first.

**Clear trigger:** Written to `handover_pending: false` only when the incoming user clicks Start Session and all required checks pass (§8.3).

### 5.3 Settings File Safety

A timestamped backup of the settings file must be written before any replacement. This follows the existing PC settings persistence contract in PRODUCTION_SPEC.md.

---

## 6. Progress Window

### 6.1 Purpose

Every operation PC performs must be visible to the user in real time. No black boxes. This applies to: handoff creation, session start, repository scan, and restore safety preview.

### 6.2 Appearance

- Opens automatically whenever PC begins a multi-step operation
- Remains visible after completion until the user takes a deliberate action:
  - **All PASS:** a "Done" button appears — clicking it dismisses the progress window and activates the next action (e.g. the outgoing confirmation screen for handoff creation, or Start Work for session start)
  - **Any FAIL:** a "Retry [failed steps]" button appears — clicking it re-runs only failed steps (§6.3); "Done" does not appear until all steps PASS
- Never auto-closes on failure
- Single scrollable panel — no nested scroll regions

**Each step row contains:**
- Step number (monospace)
- Plain-English label (UI font)
- Live status: spinner while running → ✅ PASS (green) or 🔴 FAIL (red) on completion
- On FAIL: one-line plain-English remediation directly beneath the failed row (no jargon, no git command output in primary view — raw log available via "View Full Log" link)

**Overall progress bar:**
- Single horizontal bar, 1→100%, advances as steps complete
- On foundational failure (§7.2): bar halts at current step percentage, turns red, does not advance further
- On component failure (§7.3): bar advances to 100% (all steps ran), but turns amber to signal INCOMPLETE rather than full green
- On all PASS: bar reaches 100% and turns fully green
- Label shows: "Step N of M — [Step Name]"

**Example (component failure state):**
```
Step 1  Resolve git root ...................... ✅ PASS
Step 2  Read branch / HEAD / status ........... ✅ PASS
Step 3  Create protection branch .............. ✅ PASS
Step 4  Write unstaged patch .................. 🔴 FAIL
         → C:\ has less than 200 MB free. Free disk space, then retry.
Step 5  Write staged patch .................... 🔴 FAIL
         → C:\ has less than 200 MB free. Free disk space, then retry.
Step 6  Copy changed files .................... ✅ PASS
Step 7  Write manifest.json ................... ✅ PASS
Step 8  Write HANDOFF.md ...................... ✅ PASS

[ Retry Steps 4–5 ]     [ View Full Log ]

⚠️ HANDOFF INCOMPLETE — Handover to [User] is locked until all steps pass.
```

### 6.3 Retry Scope

Retry is scoped to failed steps only. It does not re-run steps that already passed. Re-running PASS steps would risk overwriting already-written protection artifacts.

### 6.4 Operations That Show the Progress Window

| Operation | Steps shown |
|---|---|
| Create Safe Handoff | Steps 1–8 (§7) |
| Session Start | Profile check, apply defaults, scan repo, find latest package, summarize |
| Repository Scan | Resolve root, read status, read branch/HEAD |
| Restore Safety Preview | Resolve target, check protection branch, run git apply --check, compare file hashes |

---

## 7. Failure Handling — Handoff Package Creation

### 7.1 Step Classification

Steps are classified as foundational or component. Classification determines failure behavior.

| Step | Description | Class |
|---|---|---|
| 1 | Resolve selected path to git root | Foundational |
| 2 | Read branch, HEAD, and porcelain status | Foundational |
| 3 | Create protection branch at HEAD | Component |
| 4 | Write unstaged-working-tree.patch | Component |
| 5 | Write staged-index.patch | Component |
| 6 | Copy changed tracked and untracked files | Component |
| 7 | Write manifest.json | Component |
| 8 | Write HANDOFF.md | Component |

### 7.2 Foundational Failure Behavior

If Step 1 or Step 2 fails:
- Stop immediately. Do not run any subsequent steps.
- No partial package is created.
- Progress bar halts and turns red.
- Show a single clear explanation of the failure.
- Show a Retry button (retries from Step 1).
- The "Hand off to [User Name]" button remains locked.

**Rationale:** Steps 1 and 2 establish what is being protected. Without a valid git root and a readable HEAD, no protection mechanism can reference the correct state. Running component steps against an unknown or incorrect git state is worse than running nothing — it produces a package that may silently reference the wrong commit.

### 7.3 Component Failure Behavior

If any of Steps 3–8 fail:
- Continue running all remaining steps regardless.
- Do not stop on first component failure.
- Record each result (PASS or FAIL) independently.
- After all steps complete, evaluate the overall result.

**Rationale:** The protection layers are intentionally independent per PRODUCTION_SPEC.md: the Git branch ref (Step 3), patch files (Steps 4–5), file copies (Step 6), and documentation layer (Steps 7–8) each protect different aspects of the work. A failed patch write does not prevent file copies from completing. A failed manifest write does not undo the protection branch. The user needs the full picture — which layers succeeded and which failed — to understand how protected their work actually is and what manual recovery steps may be needed.

### 7.4 Hard Block on Incomplete Handoff

If any component step fails after all steps have run:
- The handoff is classified as INCOMPLETE.
- The "Hand off to [User Name]" button is locked and visually greyed out.
- The lock cannot be overridden. There is no acknowledgment bypass.
- The progress window shows the full PASS/FAIL result with per-failure remediation.
- A Retry button is shown for failed steps. Exact grouping logic when multiple non-adjacent steps fail is unresolved — see §10.
- The outgoing user must resolve all failures and achieve a full-PASS run before the "Hand off to [User Name]" button activates.

**Rationale:** The production spec's first principle is absolute: no user work, committed or uncommitted, must ever be lost. An override path — even with written acknowledgment — creates a mechanism by which data loss becomes user-sanctioned. This contradicts the safety model. On a single shared workstation, every foreseeable component failure (disk space, permissions, git path) has a fast local fix. There is no scenario urgent enough to justify bypassing protection.

### 7.5 Retry Behavior

- Retry is scoped to failed steps only.
- Retry does not re-run steps that already passed.
- Exception: if Step 3 (protection branch) failed, retry re-runs Step 3 even if it creates a branch that already exists — it must verify the branch points to the correct HEAD before marking PASS.
- After a successful retry (all steps PASS), the progress window updates all rows to ✅ PASS and the "Hand off to [User Name]" button activates.

---

## 8. Start Session Auto-Show

### 8.1 Decision

The Incoming User Confirmation Screen (§4.3) shows automatically on PC launch when `handover_pending: true`. The incoming user cannot reach any other PC UI until they click Start Session or use the explicit escape hatch (§8.3).

### 8.2 Rationale

After a gap of hours or days, the incoming user has no ambient awareness of where the project was left. Making them click a button before seeing the handoff summary introduces a moment where they can skip it. Auto-show makes the handoff summary the mandatory entry point. There is no path from launch to Claude Code that bypasses it.

### 8.3 Start Session Prerequisites

The Start Session button activates only after:
- Incoming user profile is confirmed complete
- Incoming user's defaults are applied
- Repository scan completes (shown in progress window)
- Latest handoff package is located and summarized

If any prerequisite fails, the Start Session button remains grey with a visible reason. The progress window shows the failed prerequisite step with a Retry button scoped to the failed step.

If a prerequisite cannot be resolved (e.g. the handoff package file is missing from disk), PC must offer an explicit escape: "Something went wrong loading the handoff. Contact the outgoing user or view the raw settings file." Selecting this escape clears `handover_pending` and drops the user into the standard PC main view with a persistent amber warning banner: "Handoff load failed — work with caution. No handoff summary is available." This escape does not bypass protection — it surfaces the problem and allows the user to seek help or proceed manually rather than being permanently locked out.

---

## 9. Design Constraints (Non-Negotiable)

These constraints apply to all implementation work derived from this spec.

- PC cannot close Claude Desktop, Claude Code, or any other OS process.
- PC cannot switch GitHub credentials or perform Git hosting login.
- The working tree must never be modified during handoff package creation.
- The "Hand off to [User Name]" button must never activate while the handoff is classified as INCOMPLETE (§7.4).
- No override path exists for hard-blocked states.
- Retry must never re-run already-passed steps (except Step 3 branch verification — see §7.5).
- The progress window must never auto-close on failure.
- The settings file must be backed up before replacement.
- All confirmation screens must be dismissible only by the intended action button — not by Escape, click-outside, or any passive gesture.

---

## 10. Open Items (Not Resolved in This Spec)

- Exact disk-space threshold that triggers the "free disk space" remediation message for patch/copy failures.
- Whether the progress window for Session Start uses the same visual component as the handoff creation progress window, or a lighter variant.
- Exact retry grouping logic when multiple non-adjacent steps fail (e.g. Step 3 and Step 6 both fail — one Retry button or two?).
- Maximum package size or file count before PC warns that file copy (Step 6) may be slow.
