# BA Applet Fix Spec v1

Status: Draft for Darrin review
Date: 2026-05-02
Owner: Codex
Scope: Bible Audit applet reporting and scanner correctness
Primary target, when implementation is authorized: C:\panda-gallery\workflows\design\applets\PG_Design_Bible_Audit_v1.html
Reference artifact: C:\CODEX PG\CODEX BA Applet v2\PG_Design_Bible_Audit_v2.html

## 1. Problem Statement

The current tracked BA v1 all-app report is not trustworthy. It can report aggregate fail/warn counts that do not correspond to any FAILURE_DB or WARN_DB rows. The observed report showed:

- 633 pass / 2 fail / 5 warn / 640 total
- FAILURES (2), followed by None
- WARNINGS (5), with only one warning row
- 5 apps marked never audited while still contributing pass/fail/warn counts

The root cause is mixed sources of truth:

- Hardcoded APP_PROFILES for some apps
- Empty or sparse FAILURE_DB/WARN_DB rows
- Missing apps falling back to the BA applet's own self-check counters
- Saved UI state allowing Unknown targets to inherit self-check counters

BA must separate app-source audit results from BA self-check results and must never imply an app was audited unless it has verified app data.

## 2. Fix Goals

1. Make all report counts reconcile exactly with report rows.
2. Treat never-audited apps as unknown/not-audited, not passing.
3. Preserve BA self-checks, but label them as BA self-checks only.
4. Promote the v2 scanner lessons into the canonical BA fix path.
5. Add an explicit action-feedback audit requirement for every interactive action.
6. Keep scanner limitations visible: static checks may flag risk, but runtime feedback must be verified by a live/manual or automated interaction check.

## 3. Required Report Model

BA must use one canonical result object per target app:

- app_name
- audit_status: verified | partial | not_audited | not_implemented | self_check
- last_audited: ISO date or null
- pass_count
- fail_count
- warn_count
- failure_rows[]
- warning_rows[]
- evidence_notes[]

Rules:

- pass_count + fail_count + warn_count must equal the target's declared check_total.
- fail_count must equal failure_rows.length unless the target is explicitly marked partial with missing row evidence.
- warn_count must equal warning_rows.length unless the target is explicitly marked partial with missing row evidence.
- not_audited and not_implemented apps must not contribute pass, fail, or warn counts to compliance percentages.
- All-app score must be computed only from verified and partial app records.
- All-app report must list excluded apps under a separate Not Audited / Not Implemented section.
- If an app has no valid profile, BA must show Not audited, not Unknown and not BA self-check counters.

## 4. Existing BA v1 Defects To Fix

### BA-FIX-001: fallback self-check leakage

Current behavior: apps omitted from APP_PROFILES fall through to { pass: passes, fail: fails, warn: warns }, where those counters belong to the BA applet's rendered component self-checks.

Required behavior: missing app profiles return audit_status = not_audited and do not affect compliance totals.

### BA-FIX-002: count/row mismatch

Current behavior: report headers use aggregate profile counters, but detail sections render FAILURE_DB/WARN_DB rows. These can diverge.

Required behavior: report generation must validate count/row consistency before rendering. Any mismatch is itself a BA integrity failure and must be shown as BA-INTEGRITY-001.

### BA-FIX-003: Unknown target state

Current behavior: saved or malformed scope can produce Target: Unknown while still emitting pass/fail/warn counts.

Required behavior: invalid selected scope must reset to All Panda Apps or the first known app, and the report must never render Unknown as a scored target.

### BA-FIX-004: stale/stub data presented as verified

Current behavior: stub 64/0/0 app profiles are visually indistinguishable from real audits unless the reader notices last_audited is missing.

Required behavior: stub and missing records must be labeled not_audited or not_implemented and excluded from score math.

## 5. New Required Check: Action Feedback Audit

### BA-FB-001: every action must acknowledge activation

Every enabled action control must produce observable user feedback when activated. This applies to at least:

- PySide6 QPushButton, QToolButton, QAction, clickable custom widgets, and menu actions
- HTML button elements and elements with button-like role/classes in BA applets
- Toolbar actions, footer actions, inspector buttons, refresh/check/run buttons, copy/export buttons, archive/clean/open buttons, and wizard/navigation actions

Minimum acceptable feedback:

- A visible border, background, foreground, or active-state change on activation; or
- A visible status line, toast, banner, inline message, or one-line report; or
- A visible timestamp such as Last checked, Last run, Copied at, Refreshed at, or Completed at; or
- A visible target-state change such as a refreshed list, selected row, opened detail panel, disabled busy state, new result row, or updated counter.

For diagnostic, test, refresh, scan, inspect, sync, or mailbox actions, a timestamp or one-line result is required in addition to any momentary button styling. The user must be able to tell at a glance whether the action ran recently and what happened.

Hover-only styling does not satisfy this requirement. Console logs, hidden state, silent clipboard writes, and changes visible only after scrolling do not satisfy it. Disabled future/stub actions are exempt only if they are visibly disabled and have an explanatory tooltip or adjacent status text.

### BA-FB-002: timing requirement

Feedback must begin quickly enough that the user knows the click registered:

- Immediate visual acknowledgment: within 250 ms of activation.
- Long-running action: show Running / Checking / Scanning / Sending state within 250 ms, then replace it with a completion or failure summary.
- Completion status: show final status and timestamp when the action finishes.

### BA-FB-003: durable result requirement

For actions whose result matters after the button returns to rest, BA must require durable feedback:

- Check now / Run inspector / Scan / Test / Refresh: timestamp plus pass/fail/warn or one-line result.
- Copy / Export: copied/exported confirmation, preferably with timestamp or destination/format.
- Open / Navigate: visible panel change, opened path/message indicator, or selected state.
- Clean / Archive / Delete-like actions: confirmation/result count. Destructive actions still require user confirmation under normal safety rules.
- Send / Dispatch / Mail actions: status text showing queued/sent/failed and the target.

### BA-FB-004: static scanner contract

The BA scanner should flag possible feedback gaps with a new rule family R-FB.

Static pass indicators include a connected handler or event listener that updates one or more of:

- setText, setPlainText, append, insertRow, setData, setProperty, setStyleSheet, setEnabled, setChecked, setCurrentIndex, setVisible
- A named status/feedback/timestamp label or field
- A report/result pane
- A table/list/model refresh
- A modal/detail panel open
- Clipboard confirmation text
- A timestamp string generated at action time

Static risk indicators include:

- Button/action has a click handler but the handler only logs, returns, passes, or calls a backend function with no visible UI update nearby.
- Button/action opens work silently with no status label, result row, timestamp, or changed selected/opened state.
- Copy/export actions call clipboard APIs without visible success/failure feedback.
- Refresh/check/scan actions do not update a Last run/Last checked timestamp.
- A control has hover QSS but no pressed/active state and no durable status target.

Static scanner severity:

- FAIL: enabled action is wired but no observable feedback path can be found, and the action is not explicitly exempt.
- WARN: feedback may be indirect or runtime-only and needs manual verification.
- PASS: static evidence shows immediate visual feedback and required durable result feedback for the action type.

### BA-FB-005: manual/runtime checklist contract

Because static analysis cannot prove every UI state change, BA must include an Action Feedback checklist/table with these columns:

- app
- control_label
- object_name_or_id
- action_type
- enabled_or_stub
- feedback_type: visual | status_text | timestamp | target_state | report_row | modal | disabled_tooltip
- feedback_target
- expected_timing
- verified_by
- result: pass | fail | warn | not_tested
- notes

The report must include a summary:

- Action feedback: N pass / N fail / N warn / N not tested
- Slow/missing feedback entries must appear as FAIL/WARN rows, not hidden checklist notes.

## 6. Fix Dispatch Buttons And PAH Workflow

BA must provide explicit controls that convert a verified BA finding or report into a tracked repair workflow:

- SEND FIX TO CC
- SEND FIX TO CD
- SEND FIX VIA PAH

Button behavior:

- The buttons operate on the currently selected BA finding, report section, or full report.
- The button must open a draft/preview panel before anything is sent.
- The draft must include target recipient, source report id, finding ids, app name, severity, evidence rows, proposed owner, and the requested repair workflow.
- The draft must be editable before send.
- Actual send must go through PAH's mailbox/dispatch API or canonical mailbox writer, never by ad hoc file writes from the UI.
- The send action must show immediate visual feedback and a durable timestamped result per BA-FB.
- If PAH is unavailable, the button must not silently fail; it must show a one-line error and keep the draft available.

Recipient intent:

- SEND FIX TO CC: task Claude Code to inspect the report, formulate or refine an implementation plan, apply code changes in the correct repo/worktree when authorized, run tests, and report RTC/SHIPPED status back through PAH.
- SEND FIX TO CD: task Claude Desktop to review the finding/report, formulate the fix spec, resolve ambiguity, perform a heavy-duty review of the proposed fix path, and decide whether CC or Codex should implement.
- SEND FIX VIA PAH: open a routing chooser that can target CC, CD, Codex, or a future configured agent route. It must preserve the same draft preview and tracking requirements.

Required repair workflow in the generated dispatch:

1. Read the BA report and cited source evidence.
2. Confirm whether the finding is real, stale, false positive, or needs manual verification.
3. Formulate a fix spec with scope, files, acceptance criteria, risks, and rollback/standdown conditions.
4. Perform a double heavy-duty review of the spec before implementation:
   - Review pass A: correctness against source, Bible, and current app behavior.
   - Review pass B: ambiguity/conflict/oversight pass, including stale data and ownership conflicts.
5. Apply changes only within authorized scope.
6. Run relevant static, unit, browser, or manual verification checks.
7. Post status updates back to PAH and BA.
8. Finish with RTC/commit-go/SHIPPED, or a blocked report with exact next decision needed.

BA tracking window:

- BA must include a Fix Dispatch / Repair Tracking panel.
- Each dispatch creates or updates a tracked BA repair record.
- The panel must show: dispatch id, finding ids, recipient, owner, status, created_at, last_update_at, current step, last result, blockers, report path/message path, and latest PAH status.
- Status values: draft, queued, sent, acknowledged, spec_review, implementation, verifying, rtc, commit_go_needed, shipped, blocked, rejected, false_positive, superseded.
- The tracking panel must be able to show multiple active repairs and filter by status/recipient/app/severity.
- Clicking a tracking row must show the original BA evidence and the latest PAH message summary.
- Tracking must be durable across reloads using a local JSON data file or PAH-backed state, not volatile DOM state only.
- A stale-dispatch warning must appear if no PAH status update has arrived within the configured SLA.

Safety and confirmation rules:

- BA may draft fix dispatches without confirmation.
- BA must require explicit user confirmation before sending a dispatch/message through PAH.
- BA must not send if the underlying BA report has integrity failures, unless the draft clearly labels the report as integrity-failed and asks for a BA repair rather than an app repair.
- BA must not route a fix to an agent that is currently marked HOLD or conflict-owned in PAH.
- BA must preserve recipient boundaries: Relay/CC-owned work must not be assigned to another agent without an explicit override.

Additional BA integrity checks:

- Every SEND FIX button must have action feedback, timestamped send status, and error reporting.
- Every generated dispatch must include a machine-readable frontmatter block and a human-readable repair brief.
- Every dispatch must include a BA source-report fingerprint so later report changes cannot silently rewrite the evidence.
- BA must expose "Copy draft" and "Open in PAH" actions for the repair record, each with visible feedback.

## 7. BA Applet Self-Requirements

The BA applet itself must comply with BA-FB before it can be trusted to audit other apps:

- Copy Report changes button/status text after success/failure.
- View Report opens a visible modal with the selected target name.
- All apps and app chips update score cards and selected target text.
- Scan updates a status line with fail/warn counts and timestamp.
- Refresh report updates a visible Last refreshed timestamp.
- Export CSV/checklist actions show copied/exported confirmation.
- Layout checklist reset shows reset confirmation and timestamp.
- Any check/run/inspector action must show last-run date/time.
- SEND FIX controls open a draft preview first, then show timestamped queued/sent/failed status after user-confirmed send.
- Fix Dispatch / Repair Tracking panel updates when a repair is drafted, sent, acknowledged, blocked, or shipped.

## 8. Acceptance Criteria

| AC | Requirement | Verification |
|---|---|---|
| AC-BA-001 | Missing app profile is rendered as not_audited, not scored | Remove/omit a profile and confirm all-app score excludes it |
| AC-BA-002 | fail_count/warn_count match rendered rows | Generated report has no FAILURES(n)/None contradiction |
| AC-BA-003 | Unknown target cannot be scored | Corrupt saved scope and reload; report resets to valid target |
| AC-BA-004 | Stub data is labeled not_audited/not_implemented | Apps without last_audited are not presented as 64/0/0 verified |
| AC-BA-005 | BA v2 scanner lessons retained | No docstring QTabWidget false positive; real unwired buttons still detected |
| AC-BA-006 | Action Feedback Audit exists | BA has R-FB findings plus Action Feedback checklist/report section |
| AC-BA-007 | Every enabled BA action has observable feedback | Click every BA control; each gives visual or status feedback |
| AC-BA-008 | Run/check/scan/refresh actions show timestamp | User can see last-run/last-check date/time at a glance |
| AC-BA-009 | Copy/export actions show success/failure feedback | Clipboard/export actions never fail silently |
| AC-BA-010 | All-app report separates excluded apps | Not-audited apps listed separately from scored apps |
| AC-BA-011 | Browser smoke test has zero BA console errors | Open file in browser and inspect console for this file |
| AC-BA-012 | Report integrity failure is visible | Deliberately mismatched fixture creates BA-INTEGRITY finding |
| AC-BA-013 | SEND FIX buttons exist and open draft preview | Select a finding/report and verify CC/CD/PAH routing drafts render before send |
| AC-BA-014 | PAH send requires confirmation and records timestamp | Confirm one test dispatch route and verify sent/failed status plus timestamp |
| AC-BA-015 | Repair Tracking panel records workflow state | Draft/send/ack/block/shipped states are visible and durable across reload |
| AC-BA-016 | Integrity-failed reports cannot masquerade as app fixes | Mismatched report generates BA repair draft, not app repair draft |
| AC-BA-017 | Generated dispatch includes double-review workflow | Draft includes spec pass, heavy review A, heavy review B, implementation, verification, RTC |

## 9. Recommended Implementation Sequence

1. Repair data model and report integrity first.
2. Add not_audited/not_implemented handling and all-app score exclusions.
3. Add target-scope validation to eliminate Unknown scored reports.
4. Add Action Feedback checklist and R-FB scanner checks.
5. Make BA's own controls satisfy BA-FB.
6. Add SEND FIX draft generation, PAH routing contracts, and Repair Tracking panel.
7. Re-run browser verification and source scanner fixtures.
8. Only then consider replacing the tracked v1 applet or promoting v2 into panda-gallery.

## 10. Open Questions

1. Should BA-FB be a hard fail for all enabled production actions, or warn first for legacy apps during the first audit pass?
2. Should timestamps use local time only, or local time plus ISO data attributes for machine checking?
3. Should copy/export actions require a timestamp, or is a visible success/failure status enough?
4. Should SEND FIX TO CC and SEND FIX TO CD be separate always-visible buttons, or should BA show one SEND FIX button with CC/CD/PAH route choices after click?
5. What PAH status SLA should trigger a stale-dispatch warning for BA repair records?

Codex recommendation: make BA-FB a hard fail for BA itself and for new/changed production code, but report legacy app gaps as WARN on the first all-app reconciliation pass unless the action is important enough that silent failure could mislead the user.
