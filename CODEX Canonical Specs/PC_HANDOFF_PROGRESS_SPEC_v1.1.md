# PANDA Collaborator — Handoff Protocol & Progress Window Spec
# Version: 1.1
# Date: 2026-05-04 (revised after Codex cross-spec conflict audit)
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
- Full-screen modal overlay on a dark Bible surface (`#1a1a2e` / `#161625`)
- Outgoing user identity color (amber for User 1, cyan for User 2) appears as a top border stripe, header accent, and role badge only — never as a full-surface fill or button background
- Cannot be dismissed by clicking outside, pressing Escape, or any passive gesture
- Single large rectangular action button: "Hand Off to [Incoming User Display Name]" — green when ready, grey when locked

**Required copy (exact wording):**
> Handoff package created successfully.
>
> Before you hand over:
> 1. Close your Claude Desktop session.
> 2. Close your Claude Code session.
> 3. Log out of your GitHub account if you remain at the workstation.
>
> When done, click the button below.

**[ Hand Off to [User Name] ]**

**What the button does (in order):**
1. Writes the queued-incoming-user state to disk (§5.2) — this happens first, before any UI change.
2. Saves outgoing user state.
3. Applies incoming user defaults (repository path, agent, title).
4. Switches the identity accent (border stripe, header, badge) to the incoming user's identity color on a dark Bible surface.
5. Scans the repository.
6. Logs the user switch to the timeline.
7. Shows the Incoming User Confirmation Screen (§4.3).

### 4.3 Incoming User Confirmation Screen

**Trigger:** Fires immediately after the outgoing user clicks "Hand Off to [User Name]" on the outgoing confirmation screen (§4.2) and all state transitions complete (settings written, theme switched, repository scanned).

**Appearance:**
- Full-screen screen on a dark Bible surface (`#1a1a2e` / `#161625`)
- Incoming user identity color appears as a top border stripe, header accent, and role badge only — never as a full-surface fill
- Displays the incoming user's display name in large uppercase text
- Shows a plain-English summary of the latest handoff package (what was done, concerns, recommended next action)
- Plain-English / Technical toggle available
- Single large rectangular action button: "Start Session" — green when all prerequisites pass (§8.3), grey with visible reason when blocked

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

PC must persist the queued-incoming-user state to disk immediately when the outgoing user clicks "Hand Off to [User Name]" on the outgoing confirmation screen (§4.2). This state must survive:
- App close and reopen
- Browser tab close and reopen
- Workstation sleep and wake
- Workstation restart

### 5.2 Implementation

**Schema:** The `handover_state` data is stored as a dedicated sub-object within the existing PC local settings file, nested under a `"handover_state"` key. This avoids conflicting with the PC settings API validator, which rejects payloads that do not contain exactly two user profiles at the top level.

```json
{
  "user_1": { ... },
  "user_2": { ... },
  "handover_state": {
    "handover_pending": true,
    "incoming_user_slot": "user_1",
    "handover_timestamp": "<ISO 8601 timestamp>",
    "handoff_package_id": "<stable package ID>",
    "failed_package_id": null
  }
}
```

Note: `incoming_user_slot` is either `"user_1"` or `"user_2"`. `failed_package_id` is populated if the escape hatch is used (§8.3) for timeline logging purposes.

**Write trigger:** When the outgoing user clicks "Hand Off to [User Name]" on the outgoing confirmation screen (§4.2), write the updated settings file (with `handover_state` populated) before any UI transition occurs. A timestamped backup of the prior settings file must be written first (§5.3).

**Read trigger:** On every PC launch, read `handover_state.handover_pending` before rendering any UI. If `true`, show the Incoming User Confirmation Screen (§4.3) immediately. No other UI is shown first.

**Clear trigger:** Set `handover_state.handover_pending` to `false` only when the incoming user clicks Start Session and all required checks pass (§8.3). Write the updated settings file with a timestamped backup before replacement.

### 5.3 Settings File Safety

A timestamped backup of the settings file must be written before any replacement. This follows the existing PC settings persistence contract in PRODUCTION_SPEC.md.

---

## 6. Progress Window

### 6.1 Purpose

Every operation PC performs must be visible to the user in real time. No black boxes. This applies to: handoff creation, session start, repository scan, and restore safety preview.

### 6.2 Appearance

- Opens automatically whenever PC begins a multi-step operation
- Remains visible after completion until the user takes a deliberate action:
  - **All PASS:** a "Done" button appears. "Done" is a dismiss-and-reveal control only — it closes the progress window and reveals (but does not trigger) the next explicit action (e.g. the outgoing confirmation screen becomes visible for handoff creation; Start Work button becomes enabled for session start). Done performs no hidden work, state transitions, or data operations beyond closing the progress view.
  - **Any FAIL:** a "Retry [failed steps]" button appears — clicking it re-runs only failed steps (§6.3); "Done" does not appear until all steps PASS
- Never auto-closes on failure
- Single scrollable panel — no nested scroll regions

**Layout and focus requirements:**
The progress window is a new UI component not yet defined in `CODEX_PC_UI_UX_RED_DESIGN_SPEC_v1.md`. That spec must be updated (or a v2 addendum added) to define: focus trap behavior while the window is open, narrow-width layout (min 820px), button sizing and states (Done / Retry), and screenshot/BA verification requirements for the progress component. This update is required before implementation is considered complete. All visual grammar (dark surfaces, rectangular buttons, semantic colors) follows the existing redesign spec rules.

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
Step 1   Resolve git root ..................... ✅ PASS
Step 2   Read branch / HEAD / status .......... ✅ PASS
Step 3   Create protection branch ............. ✅ PASS
Step 4   Write unstaged patch ................. 🔴 FAIL
          → C:\ has less than 200 MB free. Free disk space, then retry.
Step 5   Write staged patch ................... 🔴 FAIL
          → C:\ has less than 200 MB free. Free disk space, then retry.
Step 6   Copy changed files ................... ✅ PASS
Step 7a  Write manifest.json .................. ✅ PASS
Step 7b  Write HANDOFF.md ..................... ✅ PASS

[ Retry Steps 4–5 ]     [ View Full Log ]

⚠️ HANDOFF INCOMPLETE — Hand Off to [User] is locked until all steps pass.
```

### 6.3 Retry Scope

Retry is scoped to failed steps only. It does not re-run steps that already passed. Re-running PASS steps would risk overwriting already-written protection artifacts.

### 6.4 Operations That Show the Progress Window

| Operation | Steps shown |
|---|---|
| Create Safe Handoff | Steps 1–7b (§7) |
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
| 7a | Write manifest.json | Component |
| 7b | Write HANDOFF.md | Component |

Note: Steps 7a and 7b correspond to what PRODUCTION_SPEC.md calls "step 7" (writing manifest.json and HANDOFF.md). They are split here to enable independent PASS/FAIL reporting in the progress window. They share the same class and retry rules. PRODUCTION_SPEC.md step numbering is unchanged; this spec's 7a/7b is an implementation-level split of that single production step.

### 7.2 Foundational Failure Behavior

If Step 1 or Step 2 fails:
- Stop immediately. Do not run any subsequent steps.
- No partial package is created.
- Progress bar halts and turns red.
- Show a single clear explanation of the failure.
- Show a Retry button (retries from Step 1).
- The "Hand Off to [User Name]" button remains locked.

**Rationale:** Steps 1 and 2 establish what is being protected. Without a valid git root and a readable HEAD, no protection mechanism can reference the correct state. Running component steps against an unknown or incorrect git state is worse than running nothing — it produces a package that may silently reference the wrong commit.

### 7.3 Component Failure Behavior

If any of Steps 3–7b fail:
- Continue running all remaining steps regardless.
- Do not stop on first component failure.
- Record each result (PASS or FAIL) independently.
- After all steps complete, evaluate the overall result.

**Rationale:** The protection layers are intentionally independent per PRODUCTION_SPEC.md: the Git branch ref (Step 3), patch files (Steps 4–5), file copies (Step 6), and documentation layer (Steps 7a–7b) each protect different aspects of the work. A failed patch write does not prevent file copies from completing. A failed manifest write does not undo the protection branch. The user needs the full picture — which layers succeeded and which failed — to understand how protected their work actually is and what manual recovery steps may be needed.

### 7.4 Hard Block on Incomplete Handoff

If any component step fails after all steps have run:
- The handoff is classified as INCOMPLETE.
- The "Hand Off to [User Name]" button is locked and visually greyed out.
- The lock cannot be overridden. There is no acknowledgment bypass.
- The progress window shows the full PASS/FAIL result with per-failure remediation.
- A Retry button is shown for failed steps. Exact grouping logic when multiple non-adjacent steps fail is unresolved — see §10.
- The outgoing user must resolve all failures and achieve a full-PASS run before the "Hand Off to [User Name]" button activates.

**Rationale:** The production spec's first principle is absolute: no user work, committed or uncommitted, must ever be lost. An override path — even with written acknowledgment — creates a mechanism by which data loss becomes user-sanctioned. This contradicts the safety model. On a single shared workstation, every foreseeable component failure (disk space, permissions, git path) has a fast local fix. There is no scenario urgent enough to justify bypassing protection.

**On manual instructions:** PRODUCTION_SPEC.md states that when PC cannot directly perform a safe action, it should prepare required text or commands for the user. In the context of an INCOMPLETE handoff, this means PC may show remediation instructions (e.g. "Free disk space on C:\, then click Retry") or copy a command to the clipboard. These are recovery instructions only. They never unlock "Hand Off to [User Name]" or bypass the full-PASS requirement. The only path to unlocking the button is a successful full-PASS run of all failed steps.

### 7.5 Retry Behavior

- Retry is scoped to failed steps only.
- Retry does not re-run steps that already passed.
- Exception: if Step 3 (protection branch) failed, retry re-runs Step 3 even if a branch of that name already exists — it must verify the branch points to the correct HEAD before marking PASS.
- After a successful retry (all steps PASS), the progress window updates all rows to ✅ PASS and the "Hand Off to [User Name]" button activates.

### 7.6 Retry Idempotency Rules

Each component step must be safe to retry without corrupting already-written artifacts. The following rules govern retry behavior per step:

| Step | Idempotency rule |
|---|---|
| 3 | If a protection branch of the correct name already exists at the correct HEAD, mark PASS without re-creating. If it exists but points to a different commit, fail with a clear message. |
| 4 | Write to a temp file first, then atomically rename to `unstaged-working-tree.patch`. If the temp file exists from a prior failed attempt, overwrite it. |
| 5 | Same as Step 4 for `staged-index.patch`. |
| 6 | File copies are written to a temp subdirectory first, then atomically moved into `file_copies/`. Partially written files from a prior attempt are overwritten. |
| 7a | Write `manifest.json` to a temp file, then atomically rename. Overwrite any prior temp or partial file. |
| 7b | Write `HANDOFF.md` to a temp file, then atomically rename. Overwrite any prior temp or partial file. |

**Package is not finalized until all steps PASS.** The package directory is considered incomplete and must not be made available to the Package Inspector until a full-PASS run is confirmed.

---

## 8. Start Session Auto-Show

### 8.1 Decision

The Incoming User Confirmation Screen (§4.3) shows automatically on PC launch when `handover_state.handover_pending` is `true`. The incoming user cannot reach any other PC UI until they click Start Session or use the explicit escape hatch (§8.3).

### 8.2 Rationale

After a gap of hours or days, the incoming user has no ambient awareness of where the project was left. Making them click a button before seeing the handoff summary introduces a moment where they can skip it. Auto-show makes the handoff summary the mandatory entry point. There is no path from launch to Claude Code that bypasses it.

### 8.3 Start Session Prerequisites

The Start Session button activates only after:
- Incoming user profile is confirmed complete
- Incoming user's defaults are applied
- Repository scan completes (shown in progress window)
- Latest handoff package is located and summarized

If any prerequisite fails, the Start Session button remains grey with a visible reason. The progress window shows the failed prerequisite step with a Retry button scoped to the failed step.

If a prerequisite cannot be resolved (e.g. the handoff package file is missing from disk), PC must offer an explicit escape. The escape is not automatic — it requires a deliberate confirmed action:

> "The handoff package could not be loaded. This may mean the package file was moved, deleted, or the settings file is corrupted. You can proceed without it, but you will have no handoff summary and may be missing context."
>
> **[ Proceed without handoff ]**   **[ Cancel — try again ]**

Clicking "Proceed without handoff":
- Requires an explicit second confirmation: "Are you sure? Work with caution — no handoff summary is available."
- Sets `handover_state.handover_pending` to `false` and populates `handover_state.failed_package_id` with the ID of the package that could not be loaded (for timeline history).
- Logs a "handoff load failed — escaped" event to the project timeline.
- Drops the user into the standard PC main view with a persistent amber warning banner: "⚠️ Handoff load failed — no handoff summary available. Create or obtain a fresh handoff before serious work begins."
- The amber banner persists until the user creates or loads a valid handoff package.

This escape does not bypass the hard block on package creation (§7.4) — it only handles the case where a pending handoff package cannot be read on the incoming user's side.

---

## 9. Design Constraints (Non-Negotiable)

These constraints apply to all implementation work derived from this spec.

- PC cannot close Claude Desktop, Claude Code, or any other OS process.
- PC cannot switch GitHub credentials or perform Git hosting login.
- The working tree must never be modified during handoff package creation.
- The "Hand Off to [User Name]" button must never activate while the handoff is classified as INCOMPLETE (§7.4).
- No override path exists for hard-blocked states. Manual remediation instructions are recovery guidance only — they never unlock the "Hand Off to [User Name]" button.
- Retry must never re-run already-passed steps (except Step 3 branch verification — see §7.5).
- The progress window must never auto-close on failure.
- The settings file must be backed up before replacement.
- All confirmation screens must be dismissible only by the intended action button — not by Escape, click-outside, or any passive gesture.
- Identity colors (amber for User 1, cyan for User 2) are used as border stripes, header accents, and role badges only — never as full surface fills or action button backgrounds.

**Locked button naming map (canonical across all PC specs and UI):**

| Context | Canonical label |
|---|---|
| Hub user-switching | Switch to [Name] |
| Handoff package creation | Create Safe Handoff |
| Post-creation outgoing modal | Hand Off to [Name] |
| Incoming session entry | Start Session |
| Incoming session confirmation | Start Work |
| Repository scan | Scan Working Tree |
| Emergency stop | Emergency Pause |

---

## 10. Open Items (Not Resolved in This Spec)

- Exact disk-space threshold that triggers the "free disk space" remediation message for patch/copy failures.
- Whether the progress window for Session Start uses the same visual component as the handoff creation progress window, or a lighter variant.
- Exact retry grouping logic when multiple non-adjacent steps fail (e.g. Step 3 and Step 6 both fail — one Retry button or two?).
- Maximum package size or file count before PC warns that file copy (Step 6) may be slow.

## 11. Required Downstream Spec Updates

The following existing specs must be updated after implementation direction is approved. These are not optional — they are part of the definition of done for this workstream.

**CODEX_PC_UI_UX_RED_DESIGN_SPEC_v1.md** — Add a progress window section defining: placement, focus trap behavior, narrow-width layout (min 820px), Done/Retry button sizing and states, and BA/screenshot verification requirements.

**PC_MANUAL_SPEC_v1.md** — Add a v2 addendum or update §3.3–§3.4 to cover: pending-handover auto-show on launch, outgoing/incoming confirmation screens, progress window PASS/FAIL states, missing-package escape hatch, and the locked button naming map (§9).

**PRODUCTION_SPEC.md** — Acknowledge the 7a/7b sub-step split in the progress window context (no behavioral change to the production contract; documentation only).
