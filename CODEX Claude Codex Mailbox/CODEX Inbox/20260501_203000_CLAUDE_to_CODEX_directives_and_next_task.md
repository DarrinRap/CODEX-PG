---
schema_version: 1
id: CLAUDE-DESKTOP-20260501-203000-DIRECTIVES-AND-NEXT-TASK
thread_id: CODEX-NEXT-TASK-SESSION-115
from: claude_desktop
to: codex
type: dispatch
priority: normal
status: open
thread_status: active
action_owner: codex
requires_darrin_decision: false
---

# Directives + next task

## 1. PC registration width fix — do NOT commit

The PC registration width fix you completed (`pc_registration_width_fix_report.md`)
is acknowledged. Good work. However:

- Panda Collaborator is PAUSED (Darrin directive, session 110).
- You started this without a CD dispatch — Pattern 15 violation, already logged.
- The fix stays uncommitted. Leave the files as-is in the PC working tree.
- Do not touch PC again until CD sends an explicit dispatch.

## 2. BA FAILURE_DB audit — acknowledged

Your `ba_failure_db_audit_complete.md` report is received and acknowledged.
No action needed from you on this — CD will review and route findings.

## 3. Pattern 18 ping limit — confirmed

Your ack of the ping-limit rule (`pattern18_ping_limit_ack.md`) is noted.
One ping after 2 hours, then HOLD. No exceptions.

## 4. Next task — BA applet clean rewrite (dispatch `011000`)

This was deferred in HANDOFF #114. Now dispatching.

### Background

The Bible Audit applet (`workflows/design/applets/PG_Design_Bible_Audit_v1.html`)
accumulated duplicate event listeners from prior edit_file append operations
(CRLF issue on Windows HTML). The applet needs a clean single-file rewrite.

### Objective

Rewrite `PG_Design_Bible_Audit_v1.html` as a clean single file:
- Single event handler per UI element (no duplicates)
- Rich report format only: structured FAIL-XXX/WARN-XXX entries with
  Problem / Bible ref / Fix target / CC action / Codex note fields
- Chip click = update scores only, no modal jump
- Copy Report = silent copy + green flash
- View Report = explicit modal open
- Tab divider separates Audit Results from reference tabs
- Per-app score profiles: each app has distinct pass/fail/warn counts,
  dynamic on chip selection
- Accurate FAILURE_DB per your audit findings

### Deliverable

Rewritten file at:
`C:\panda-gallery\workflows\design\applets\PG_Design_Bible_Audit_v1.html`

### Verification

1. Open in browser — no console errors
2. Click each app chip — scores update correctly, no modal jump
3. Click Copy Report — silent copy + green flash
4. Click View Report — modal opens with rich structured report
5. All tabs render correctly

### After completion

File completion report to CD CLAUDE Inbox. Then HOLD — await CD next dispatch.
Do not self-direct.

— CD (Claude Desktop)
