# CODEX BA Broken-Wire And Workflow Audit Spec v1

Status: Draft for Darrin review  
Created: 2026-05-09  
Owner: Codex  
Applies to: BA, PANDA Collaborator, PANDA Agent Hub  
Canonical path: `C:\CODEX PG\CODEX Canonical Specs\CODEX_BA_BROKEN_WIRE_WORKFLOW_AUDIT_SPEC_v1.md`

## 1. Authorization Boundary

This spec does not authorize implementation-go, commit-go, staging, committing, or direct CC authorization tokens.

CC authorization still routes through Claude Desktop/CD using:

`C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox`

Codex must not send implementation-go or commit-go tokens directly to CC.

The canonical CC lane remains:

`C:\panda-gallery\workflows\cc_mailbox\CC Inbox`

This spec does not authorize direct CC writes by Codex.

This spec does not authorize Relay-file edits.

## 2. Purpose

The purpose of this spec is to make BA better at finding app failures before Darrin has to discover them by hand.

The target class is "broken-wire" bugs: the UI looks like it has a working path, but some piece of the path is missing, disconnected, confusing, visually misleading, or crashes when used.

Recent examples this spec is designed to cover:

1. PANDA Collaborator showed a message box, but the user could not enter or save the message.
2. PANDA Collaborator RUN TEST crashed with `Cannot read properties of undefined (reading 'repo_root')`.
3. PANDA Collaborator showed an unreadable diagonal TEST MODE ribbon over important controls.
4. PANDA Agent Hub launched an unwanted blank terminal window.
5. PANDA Agent Hub tray/status UI could appear present while PAH server state was offline or unclear.
6. PANDA Agent Hub tray/icon affordances could be missing, ambiguous, or too low-resolution to identify reliably.

BA should not merely ask "does the file parse?" or "does a route exist?" BA should ask "can a normal user complete the intended workflow, and does the app prove that each step is truly usable?"

## 3. Plain-Language Principle

BA should act like a careful assistant walking through the app with a checklist:

1. Look at the screen.
2. Find the next natural action.
3. Check whether the button is actually allowed right now.
4. Click or type when it is safe to do so.
5. Confirm the app changed state in the expected direction.
6. Capture evidence when it did not.

If BA cannot prove a surface, it must say so clearly. A clean BA report is only trusted for the named surfaces and workflows BA actually inspected.

## 4. Scope

This spec covers seven BA upgrades:

1. Workflow simulation.
2. Broken-wire static scanning.
3. Button-state and actionability auditing.
4. Visual rule auditing.
5. Launch-path auditing.
6. Bug-to-BA retrospective intake.
7. Evidence and report schema improvements.

This spec applies first to:

1. `C:\CODEX PG\CODEX PANDA Collaborator`
2. `C:\CODEX PG\CODEX Agent Hub`
3. `C:\panda-gallery\scripts\ba_audit_runner.py`

## 5. Definitions

Broken wire:
A user-visible feature whose visible control, handler, route, state mutation, file write, or feedback path is missing, mismatched, stale, or crashing.

Workflow proof:
Evidence that a user can complete a named app task from start to finish under a known state.

Actionable control:
A button, link, menu item, keyboard action, tray menu command, or form submission that is currently selectable and expected to do useful work.

Disabled safe action:
A safe action that is visible but blocked because prerequisites are missing. It must be grey, inert, and explain what is missing.

Visual truth:
The screen state must match the actual app state. A green button must mean usable. A grey button must mean unavailable. A completed step must show completion. A blocked step must show why it is blocked.

## 6. BA Workflow Simulator

BA should gain a workflow simulator for PC and PAH.

The simulator should run a scripted user journey in a controlled local environment and capture:

1. DOM state before each action.
2. Button enabled/disabled state.
3. Text entry success.
4. Click result.
5. Console errors.
6. Network or backend route failures.
7. File writes or expected artifacts.
8. Screenshot before and after major steps.
9. Final pass/fail evidence.

### 6.1 PANDA Collaborator Workflow

PC workflow simulation should include at minimum:

1. Open PC in normal mode.
2. Enter TEST MODE.
3. Confirm fake users are visible.
4. Register or confirm User 1.
5. Register or confirm User 2.
6. Scan or load the sandbox working tree.
7. Type into Quick Message.
8. Blur or save the message.
9. Confirm the message persists in the visible activity stream or backing state.
10. Start session or start work.
11. Run test.
12. Confirm the status pill says TEST PASS or TEST FAIL.
13. Confirm no uncaught JavaScript errors occurred.
14. Open evidence.
15. Quit TEST MODE.
16. Confirm normal Darrin/Pam mode returns.

The Quick Message step is mandatory because it is the exact failure class Darrin found by hand.

The RUN TEST step must pass an explicit repo state object into UI rendering paths and fail if any renderer assumes an undefined object.

PC simulation must cover both:

1. TEST MODE sandbox flow using fake users.
2. Normal single-workstation shared-user flow using the configured real users.

The normal shared-user flow must prove the same left-to-right progression without relying on fake accounts or sandbox-only affordances.

Normal shared-user proof must use disposable test data, a dedicated test repository, or read-only dry-run checks. It must not modify real active user work unless Darrin explicitly authorizes that test.

### 6.2 PANDA Agent Hub Workflow

PAH workflow simulation should include at minimum:

1. Start PAH without opening a blank terminal window.
2. Confirm the tray can launch while the server is already running.
3. Confirm duplicate launch gives a user-facing "already running" notice without spawning a second server.
4. Open dashboard.
5. Refresh status.
6. Run health check.
7. Confirm PAH server status is online when the server is reachable.
8. Confirm PAH server status is offline when the server is not reachable.
9. Confirm restart is only actionable when restart is actually available.
10. Confirm disabled menu items are grey and inert.
11. Confirm Copy Status Summary returns useful text.

The launch-path step is mandatory because the blank terminal bug was not caught by prior smoke tests.

## 7. Broken-Wire Static Scanner

BA should add a static scanner that maps user-visible controls to the code paths they depend on.

For HTML and JavaScript surfaces, BA should detect:

1. Buttons or links without a reachable handler.
2. Handlers that call undefined functions.
3. Handler functions that dereference required object properties without default guards.
4. Calls that pass fewer required arguments than the callee dereferences.
5. Form inputs that do not update state, emit events, or persist on blur/submit.
6. Fetch calls to backend routes that are not implemented.
7. Backend routes that changed response shape without corresponding frontend guards.
8. Status text that can show success while the underlying route failed.

For Python surfaces, BA should detect:

1. Routes with changed response fields not reflected in frontend expectations.
2. Startup code that opens a console window for background/tray behavior.
3. Bare exceptions swallowed without a visible diagnostic.
4. Health checks that hide detailed route failures behind a misleading aggregate pass.

For PowerShell surfaces, BA should detect:

1. `Start-Process` calls for background tray/server work that omit `-WindowStyle Hidden`.
2. Python server launches that prefer `python.exe` where `pythonw.exe` is available.
3. Startup shortcuts that omit hidden window arguments.
4. Shortcut `WindowStyle` values that leave a visible normal window.
5. Launch scripts that spawn browsers or terminals outside explicit user action.

## 8. Button-State And Actionability Audit

BA should audit button and command behavior app-wide.

Every actionable control must have:

1. A visible label or accessible name.
2. A current state: unavailable, ready, active, complete, blocked, or error.
3. A handler when ready.
4. A reason when unavailable or blocked.
5. A visible state change after successful completion.

Required UI behavior:

1. Safe enabled actions are green.
2. Safe disabled actions are grey or muted.
3. Dangerous or emergency actions use warning/error styling.
4. Completed steps show a check mark or equivalent completion symbol plus a color change.
5. The next step visibly unlocks after its prerequisite is complete.
6. A disabled control must not perform its action when clicked.
7. A visible ready control must either perform the action or emit a clear error.
8. Passive pills must not behave like clickable action buttons.

For PC, BA must enforce the left-to-right workflow:

1. Setup users on the left.
2. Do active work in the center.
3. Create or review the handoff on the right.

For PAH, BA must enforce:

1. Dashboard commands are rectangular action buttons.
2. Status indicators are passive pills.
3. Tray menu commands reflect real server reachability.
4. Offline or stale status is visibly different from online status.

## 9. Visual Rule Audit

BA should add screenshot-backed visual checks for PC and PAH.

The visual audit should check:

1. Text overlap.
2. Text clipped by buttons or panels.
3. Disabled text that is too faint to read.
4. Warning banners covering important controls.
5. Modal or panel content that blocks the user's next required action.
6. Contrast failures for critical labels.
7. One-hue visual drift when app design requires distinct status colors.
8. Misleading color use, such as a green button that is not actionable.
9. Missing left-to-right progress cues in PC.
10. Missing online/offline distinction in PAH.
11. Low-resolution or ambiguous tray/app icons at common Windows tray and taskbar sizes.

Specific required regression:

The PC diagonal TEST MODE ribbon must use yellow background and black text if the ribbon remains diagonal. It must not obscure Emergency Pause text or other high-priority controls.

If BA cannot make a reliable image judgment, it should label the finding as `visual_review_needed` and include the screenshot path.

## 10. Launch-Path Audit

BA should inspect launch paths because some bugs happen before the app UI is usable.

PAH launch checks must verify:

1. Tray startup does not create an unwanted blank terminal.
2. Server launch prefers `pythonw.exe` when available.
3. Startup shortcuts include hidden-window arguments.
4. Startup shortcuts set no-normal-window behavior. A minimized metadata value is acceptable only when it does not present a blank terminal to the user.
5. Duplicate launch reuses or reports the existing server.
6. Browser windows are opened only as part of explicit dashboard/user action.

PC launch checks must verify:

1. Test mode restores from prior sessions without trapping the user.
2. Quit TEST MODE returns to normal Darrin/Pam mode.
3. Sandbox paths do not overwrite real user work.
4. Test-mode banners are visible but not obstructive.

## 11. Bug-To-BA Retrospective Intake

Every confirmed bug or credible candidate bug found by Codex, CC, CD, BA, or Darrin must trigger a BA retrospective note.

Codex must be notified when CC, CD, BA, or Darrin records a bug that could affect BA coverage. Notification should use the active thread when present or the CODEX Inbox when asynchronous:

`C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox`

The note must ask:

1. Could BA reasonably have caught this before Darrin found it?
2. If yes, what is the smallest BA upgrade that would catch it next time?
3. If no, why is it outside BA's practical reach?
4. Which fixture, workflow, static rule, runtime probe, screenshot check, or report wording should change?
5. What regression test proves the BA upgrade works?

The retrospective result should classify the bug as one of:

1. `candidate_product_bug`
2. `product_bug`
3. `ba_bug`
4. `ba_advisory`
5. `ba_calibration_finding`
6. `false_positive`
7. `no_action`

This preserves the existing BA disposition model while adding a required learning loop.

## 12. Evidence Schema

BA reports should add structured evidence for workflow and broken-wire findings.

Required fields:

1. `finding_id`
2. `finding_type`
3. `surface`
4. `app`
5. `workflow`
6. `step`
7. `severity`
8. `confidence`
9. `expected_state`
10. `actual_state`
11. `control_selector`
12. `handler`
13. `route`
14. `console_error`
15. `screenshot_path`
16. `artifact_path`
17. `ba_upgrade_recommendation`
18. `codex_notification_path`
19. `disposition`

For active-thread notification, `codex_notification_path` should be `active_thread`. For asynchronous notification, it should contain the mailbox path or message file used.

Required finding types:

1. `broken_wire`
2. `workflow_blocker`
3. `state_mismatch`
4. `visual_misleading`
5. `launch_path_bug`
6. `route_contract_mismatch`
7. `coverage_gap`
8. `visual_review_needed`

## 13. Severity

BA should use these severities:

P0:
Data loss, real user work overwritten, unsafe commit/stage behavior, or broken authorization boundaries.

P1:
Core workflow cannot be completed, app crashes, handoff evidence cannot be produced, or launch creates disruptive unwanted windows.

P2:
Feature appears available but is disconnected, misleading, stale, or silently fails.

P3:
Confusing visual state, incomplete evidence, weak wording, or non-blocking polish issue.

## 14. Minimum Acceptance Criteria

The upgrade is acceptable only when BA can prove the following:

1. PC Quick Message accepts typed text and persists it through the expected save path.
2. PC RUN TEST does not throw `repo_root` or undefined-object renderer errors.
3. PC TEST MODE visual treatment is yellow/black or otherwise high contrast and non-obstructive.
4. PC left-to-right workflow shows completed, ready, unavailable, and blocked states clearly.
5. PC normal single-workstation shared-user flow works without relying on TEST MODE.
6. PAH tray/server startup does not open an unwanted blank terminal.
7. PAH startup shortcut uses hidden/no-normal-window behavior.
8. PAH tray menu status changes between online and offline truthfully.
9. PAH tray/app icons remain legible at common Windows tray and taskbar sizes.
10. Disabled PAH commands are grey and inert.
11. BA report names exactly which PC and PAH workflows were proven.
12. BA report names any surfaces that were not proven.

## 15. Implementation Notes

Recommended implementation order:

1. Add fixtures for the recent PC and PAH bugs.
2. Add static broken-wire scanner rules.
3. Add PC workflow simulation.
4. Add PAH launch-path simulation.
5. Add visual screenshot checks.
6. Add evidence schema fields.
7. Add retrospective intake template.

BA should fail closed for core workflow blockers. If a core PC or PAH workflow cannot be proven, the report should not read as clean.

BA may use advisory warnings for visual checks that are not deterministic, but it must still attach screenshots and explain what it could not prove.

## 16. Non-Goals

This spec does not require BA to replace hands-on testing.

This spec does not require BA to solve subjective design taste.

This spec does not authorize changing PC, PAH, BA, Relay, or CC mailbox behavior by itself.

This spec does not permit BA to stage, commit, clean, revert, or modify parked dirty files.

## 17. Done Definition

The spec is ready for implementation planning when:

1. Darrin accepts the direction.
2. CD has had a chance to review if formal routing is needed.
3. Each known recent bug has a matching proposed BA detection method.
4. The implementation can be split into small, testable changes.
5. The report output clearly separates product bugs, BA bugs, advisories, and coverage gaps.
