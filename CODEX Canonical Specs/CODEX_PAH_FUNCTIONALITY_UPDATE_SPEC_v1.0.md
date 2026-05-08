# CODEX PAH Functionality Update Spec v1.0

Created: 2026-05-06
Owner: Codex for draft/spec maintenance; Darrin remains approval gate
Scope: PANDA Agent Hub (PAH) coordination reliability, mailbox state trust, health diagnostics, and operational recovery
Status: Draft for review
Review state: Self-reviewed by Codex through inline correction passes

## 1. Purpose

This spec defines the next PAH update needed after the 2026-05-06 health review. The goal is to make PAH reliable as a coordination cockpit again: current agent/mail state should be accurate, stale/unread warnings should be trustworthy, the Agent Hub server should expose live diagnostics when expected, and broad backup/staging hazards should be avoided while dirty UI/UX or parked artifacts exist.

This is not a visual redesign spec. It does not authorize UI/UX implementation changes. It focuses on state correctness, diagnostic trust, operational procedure, and safe cleanup.

## 2. Current Evidence

Recent verification found:

- `http://127.0.0.1:8788/api/health` returned healthy JSON for PANDA Collaborator, not PAH Agent Hub.
- An earlier check against `http://127.0.0.1:8766` refused connections, but backend research later confirmed PAH Agent Hub defaults to port `8765`; `8766` was the wrong target for current PAH health.
- `C:\CODEX PG\CODEX Automation\CODEX_relay_health_check.ps1 -Json -NoFail` returned `status: warn`, with `0 errors`, `16 warnings`, `16 recent_unread_incoming`, and `16 unindexed_recent_codex_mail`.
- The relay health checker reported no active queue rows.
- CD confirmed Codex was not the bottleneck; CC had recent active dispatches and Codex should stand by.
- `C:\CODEX PG` was dirty, including mailbox archive changes, handoff/memory/resume prompt updates, PC web changes, PAH mockup artifacts, temporary captures, and newly filed mailbox messages.
- Existing project memory records a hard no-UI/UX-touch rule and a broad backup/staging hazard while dirty UI files are present.

## 3. Problem Statement

PAH is partially functioning but not fully trustworthy as the primary coordination cockpit.

The main issues are:

1. The live PAH Agent Hub service is not confirmed running when expected.
2. Mailbox read-state and active index data are stale enough to produce noisy warnings.
3. Resolved, acknowledged, or superseded mailbox items can still appear as unread or unindexed.
4. The difference between PANDA Collaborator health and PAH Agent Hub health is easy to confuse.
5. Broad backup scripts are risky while dirty UI/UX, PC, mailbox archive, or temporary artifacts are present.
6. The current system lacks a crisp operator checklist for deciding whether PAH is green, yellow, or red.

## 4. Goals

- Restore PAH cockpit trust by making diagnostics reflect current coordination state.
- Separate health checks for PANDA Collaborator and PAH Agent Hub.
- Reconcile mailbox read-state and active dispatch index without altering historical mail content.
- Make stale/unread warnings actionable instead of noisy.
- Preserve Darrin approval gates and CC/CD authorization boundaries.
- Provide a repeatable verification checklist before claiming PAH is functioning well.
- Keep all changes narrow, reversible, and evidence-based.

## 5. Non-Goals

- No UI/UX redesign or visual polish.
- No edits to Relay files.
- No cleanup, staging, committing, deleting, or reverting parked dirty artifacts without explicit Darrin approval.
- No direct implementation-go or commit-go tokens from Codex to CC.
- No broad backup run that stages all changes while dirty UI/UX or parked files are present.
- No clinical/PHI data handling changes.
- No replacement of mailbox protocol with a new coordination system.

## 6. Definitions

- PAH Agent Hub: The local Agent Hub cockpit/API under `C:\CODEX PG\CODEX Agent Hub`, expected on port `8765` by default when running. If that port is busy, PAH may choose a fallback port unless launched with `--no-port-fallback`.
- PANDA Collaborator: The separate PC service currently reporting health on port `8788`.
- Relay health checker: `C:\CODEX PG\CODEX Automation\CODEX_relay_health_check.ps1`.
- Active dispatch index: `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX_ACTIVE_DISPATCH_INDEX.md`.
- Current authority snapshot: `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX_CURRENT_AUTHORITY.md`.
- Read-state file: `C:\CODEX PG\CODEX Agent Hub\CODEX state\CODEX_read_state.local.json`.
- Four mailbox lanes:
  - `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox`
  - `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox`
  - `C:\panda-gallery\workflows\cc_mailbox\CC Inbox`
  - `C:\panda-gallery\workflows\cc_mailbox\CLAUDE Inbox`

## 7. Required Behavior

### 7.0 Freshness and Evidence Rules

Any PAH status claim must include when each source was checked. A cockpit payload is current only if its generated timestamp is within the same active review window and not older than 10 minutes unless explicitly labeled stale. File `LastWriteTime` may be used as supporting evidence, but message frontmatter `date`, `message_id`, `thread_id`, `status`, `in_reply_to`, and follow-up messages are the authority for workflow state. When file time and frontmatter disagree, report both and avoid treating the item as stale solely from file time.

Every reconciliation proposal must include a before snapshot path, the exact files proposed for edit, the reason for each edit, and a rollback note.

### 7.1 Health Classification

PAH status must be reported as one of:

- Green: Agent Hub server is reachable, `/api/cockpit` returns current diagnostics, relay health has zero errors and no unresolved actionable warnings, active mailbox state matches current work, and no over-60-minute unread dispatch is unresolved.
- Yellow: Agent Hub server is down or relay health has warnings, but mailbox-manager checks can still determine current state and no urgent blocked work is missed.
- Red: Agent Hub server is down and mailbox state is ambiguous, relay health has errors, active dispatches are stale beyond their threshold, or Darrin/agent-blocking mail is not being surfaced.

Current status based on the 2026-05-06 check is Yellow.

### 7.2 Service Health Separation

PAH checks must not treat the PC health endpoint as proof that PAH Agent Hub is healthy.

Required checks:

1. PC health: `http://127.0.0.1:8788/api/health` only proves PANDA Collaborator health.
2. PAH health: `http://127.0.0.1:8765/api/health` proves Agent Hub health only if reachable and current, unless PAH printed a fallback port at launch.
3. PAH cockpit: `http://127.0.0.1:8765/api/cockpit` proves cockpit diagnostics only if reachable and current, unless PAH printed a fallback port at launch.
4. Relay health checker remains the fallback diagnostic when Agent Hub is not running.

### 7.3 Mailbox Read-State Reconciliation

A reconciliation pass must compare recent mailbox files against:

- File frontmatter status fields.
- Thread IDs.
- In-reply-to relationships.
- Active dispatch index rows.
- Current authority snapshot.
- Known superseding messages.
- Known completion or shipped messages.

The pass must identify items in these categories:

- Active and awaiting recipient response.
- Active and awaiting Darrin decision.
- Superseded by a newer dispatch or ruling.
- Closed by ACK, RTC, SHIPPED, or explicit CD closure.
- Informational only.
- Historical archived/no action.
- Ambiguous and requiring human review.

Resolved, superseded, closed, and informational items should not appear as urgent unread work. If they remain unread in local read-state, they may be listed as housekeeping warnings, not action blockers.

### 7.4 Over-60-Minute Unread Dispatch Rule

Codex mailbox-manager behavior must report any dispatched message that appears unread more than 60 minutes after dispatch.

The report must include:

- Message path or ID.
- Apparent sender.
- Intended recipient/lane.
- Dispatch timestamp from frontmatter `date`; if absent, infer from filename or file time and label the timestamp as inferred.
- Current age.
- Evidence for unread/stale conclusion.
- Recommended nudge.

If a later RTC, ACK, SHIPPED, superseding dispatch, or closure exists, the item is not considered unresolved unread, even if local read-state is stale.

### 7.5 Active Dispatch Index Update Rules

The active dispatch index should remain concise and current.

- Add rows only for truly active Codex-owned dispatches or current coordination obligations.
- Do not add stale FYI, resolved, or superseded messages as active rows.
- Closed rows should either move to Recently Closed or be omitted if already historical.
- Index updates must not rewrite another agent's sent message.
- Index changes must be committed only after Darrin approves a scoped cleanup/backup action.

### 7.6 Backup and Git Safety

Before any backup or commit:

1. Run `git -C "C:\CODEX PG" status --short --branch`.
2. Identify dirty files by ownership and risk category.
3. Do not run broad backup scripts while dirty UI/UX, PC, mailbox archive, or temporary artifacts are present unless Darrin explicitly authorizes that scope.
4. Prefer a scoped commit plan over staging all changes.
5. Never stage, commit, delete, revert, or clean Relay files or parked artifacts without explicit authorization.

## 8. Proposed Update Workstreams

### Workstream A: Agent Hub Runtime Verification

Purpose: prove whether PAH Agent Hub can start and serve current diagnostics.

Tasks:

1. Identify the canonical PAH launch command from existing docs/scripts.
2. Start Agent Hub only when Darrin authorizes local service startup.
3. Verify `/api/health` and `/api/cockpit` on the printed Agent Hub URL, normally port `8765`.
4. Confirm cockpit payload includes relay health, active queue, mailbox cursors, and current timestamps.
5. Record exact command, port, response summary, and failure mode if any.

Acceptance criteria:

- Agent Hub starts without traceback.
- `/api/health` responds within 5 seconds.
- `/api/cockpit` responds within 5 seconds.
- Cockpit diagnostics include relay health and current generated timestamp.
- If server cannot start, failure reason is documented with logs.

### Workstream B: Read-State and Index Reconciliation

Purpose: reduce false unread/unindexed warnings and restore trust in PAH diagnostics.

Tasks:

1. Export current relay health JSON as a before snapshot.
2. Build a classification table for the recent 20-50 mailbox items across the four lanes.
3. Mark each item active, closed, superseded, FYI, Darrin-gated, or ambiguous.
4. Propose specific read-state/index updates without changing files first.
5. After Darrin approval, apply only the minimal changes needed to remove false action warnings.
6. Re-run relay health checker and compare before/after counts.
7. Save a reconciliation report under `C:\CODEX PG\CODEX Agent Hub\CODEX reports\` or another Darrin-approved `CODEX` folder before applying edits.
8. Keep a rollback note identifying the previous read-state/index files or the exact git diff needed to undo the reconciliation.

Acceptance criteria:

- No active or Darrin-blocking mail is hidden.
- Closed/superseded/FYI items no longer appear as action blockers.
- Relay health warning count is reduced or every remaining warning is justified.
- Active dispatch index reflects current active work only.
- A before/after report exists and can explain every changed warning count.

### Workstream C: Mailbox Manager Rule Hardening

Purpose: keep the heartbeat/check behavior useful without generating noisy pings.

Tasks:

1. Preserve the every-2-minute heartbeat while Darrin wants active monitoring.
2. Report only material changes or over-60-minute unread dispatches.
3. Keep quiet heartbeat responses when no action is needed.
4. Send at most one consolidated nudge per agent per check cycle unless urgent.
5. Route CC authorization-sensitive matters through CD, not directly to CC.

Acceptance criteria:

- No duplicate nag storms.
- No implementation-go or commit-go token is sent by Codex to CC.
- Over-60-minute unread dispatches are surfaced with enough evidence to act.
- Closed/superseded threads are not repeatedly escalated.

### Workstream D: Dirty-State Safety Plan

Purpose: prevent accidental broad staging or backup while sensitive dirty files exist.

Tasks:

1. Categorize dirty files as docs/specs, mailbox coordination, PC UI/UX, PAH UI/UX, temp artifacts, archive moves, or unknown.
2. Identify files that should remain parked.
3. Identify files that are safe candidates for a later scoped commit.
4. Produce a proposed staging list before any commit/backup action.
5. Do not execute the staging plan until Darrin explicitly approves.

Acceptance criteria:

- No parked dirty file is modified or staged by accident.
- No UI/UX file is staged without explicit current approval.
- Backup/handoff scripts are not run when they would stage unintended files.

## 9. Implementation Order

1. Run read-only diagnostics: git status, relay health checker, mailbox latest scan, PAH endpoint checks.
2. Produce a current PAH status classification: Green/Yellow/Red.
3. If Agent Hub is down, request or use approved authorization to start it and capture health results.
4. Prepare read-state/index reconciliation proposal without edits.
5. Ask Darrin for approval before applying reconciliation edits.
6. Re-run diagnostics and compare before/after.
7. Only after clean or justified status, consider scoped commit/backup plan.

## 10. Verification Checklist

Before saying PAH is functioning well:

- `git -C "C:\CODEX PG" status --short --branch` reviewed.
- PAH Agent Hub `/api/health` checked, not confused with PC health.
- PAH Agent Hub `/api/cockpit` checked and payload freshness recorded.
- Relay health checker run and summarized.
- Four mailbox lanes scanned for current active work.
- Over-60-minute unread dispatch rule applied.
- Active dispatch index reviewed.
- Current authority snapshot reviewed if active state is unclear.
- Dirty-state backup hazard reviewed.
- Remaining warnings named plainly.

## 11. Reporting Template

Use this short format for PAH status reports:

```text
PAH status: Green/Yellow/Red
Evidence:
- Agent Hub: reachable/not reachable; endpoint results
- Relay health: status/counts
- Mailbox: active threads, stale/unread over 60 minutes, blockers
- Git safety: clean/dirty and backup risk
Recommendation:
- Next action
- Actions not safe yet
```

## 12. Approval Gates

Darrin approval is required before:

- Starting long-running local services if not already approved in the current session.
- Editing read-state, active index, authority snapshots, or mailbox files.
- Cleaning, moving, deleting, staging, committing, or backing up dirty files.
- Touching UI/UX files.
- Touching Relay files.
- Sending any authorization-sensitive instruction toward CC.

CD owns formal CC authorization tokens. Codex may audit, summarize, recommend, and route status, but must not send implementation-go or commit-go tokens directly to CC.

## 13. Risks

- Stale read-state can hide real urgency if cleanup is too aggressive.
- Over-indexing old mail can make PAH noisy again.
- Broad backup scripts can stage unintended UI/UX or parked artifacts.
- Agent Hub may appear unhealthy simply because it is intentionally not running.
- Mail timestamps can be misleading if file write time and frontmatter date differ.
- Suppressing old warnings without a clear classification record can reduce auditability.
- A reconciliation bug could mark an unresolved dispatch as closed; this is why proposals must be reviewed before write actions.

## 14. Open Questions

1. Should Agent Hub be expected to run continuously, or only during active coordination windows?
2. Should PAH own read-state cleanup automatically, or should cleanup remain manual/approved?
3. Should the active dispatch index track only Codex-owned work, or all current cross-agent dispatches?
4. Should the mailbox heartbeat remain at 2 minutes, or move to a slower cadence after CC clears current dispatches?
5. Should there be a dedicated non-staging backup path for memory/spec/mailbox heartbeat updates?

## 15. Recommended Decision

Approve Workstream A and a read-only version of Workstream B first.

Do not approve broad cleanup or backup yet. The safest next move is to prove Agent Hub runtime health, produce a concrete mailbox classification table, and then decide whether a minimal read-state/index reconciliation is warranted.

## 16. Backend Research Findings Added 2026-05-06

Read-only/backend diagnostics before code work found:

- Canonical PAH default URL is `http://127.0.0.1:8765/`, per `CODEX_README.md`, `CODEX_run_server_smoke.ps1`, and `CODEX_agent_hub.py` argument default. Earlier `8766` checks were not valid evidence that PAH was down.
- PAH Agent Hub was live on `8765`; `/api/health` and `/api/cockpit` responded.
- Current Inspector run: `42 pass / 2 warn / 0 fail`. Warnings were CC sidecar readiness and communication backlog.
- Periodic health run failed overall because `archive_read_sweep` hit `[WinError 5] Access is denied` replacing `.CODEX_pah_interaction_ledger.jsonl.tmp` with `CODEX_pah_interaction_ledger.jsonl`; communication backlog also remained open.
- Smoke tests passed during periodic health: `PAH smoke tests passed`.
- Health overall became `err` after the fresh periodic health run because the periodic monitor now records `archive_read_sweep` and `communication_backlog` failures.
- Inspector confirms PAH write endpoints reject missing write token/cookie and mailroom canary passes in an isolated temp mailbox.
- CC active dispatch sidecar `C:\panda-gallery\workflows\cc_mailbox\_state\active_dispatch.json` is absent, so PAH cannot prove live CC activity beyond mailbox writes.
- Multiple Python processes exist, including PAH launched through the WindowsApps python shim and the actual Python runtime. This may be normal shim behavior, but process/ledger contention should be ruled out before changing ledger write behavior.

Backend prerequisites before source-code changes:

1. Reproduce or isolate the ledger replace access-denied issue with a minimal diagnostic that does not mutate source code.
2. Determine whether the periodic health process and live PAH server contend for the same append-only ledger on Windows.
3. Decide whether the right fix is append-only file locking/retry behavior, avoiding ledger writes during read-only periodic health, or a per-process ledger event queue.
4. Confirm whether CC should be responsible for creating `active_dispatch.json`, or whether PAH should downgrade the missing sidecar warning when fresh mailbox RTC/SHIPPED evidence exists.
5. Produce a read-only mailbox classification table for the 15 open-on-agent and 9 open-on-Darrin threads before any read-state/index cleanup.