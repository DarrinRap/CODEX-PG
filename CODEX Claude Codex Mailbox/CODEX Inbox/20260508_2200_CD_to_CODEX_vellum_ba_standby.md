---
schema_version: 1
message_id: 20260508_2200_CD_to_CODEX_vellum_ba_standby
thread_id: VELLUM-BUGFIX-20260508
from: CLAUDE
to: CODEX
date: 2026-05-08T22:00:00-07:00
subject: STANDBY -- Run full BA on Vellum files when CC notifies you fixes are ready
type: task
priority: urgent
---

# Standby — Vellum BA verification

CC is implementing Vellum bug fixes tonight. When CC notifies you (via this
mailbox thread or a direct message) that fixes are complete and ready for
BA review, run the following immediately and report results to CD:

## Commands to run

1. `python scripts/ba_audit_runner.py --app Vellum --summary`
   - Must show 0 hard failures
   - Include full output in your report

2. `python scripts/ba_audit_runner.py --app Vellum`
   - Include the detailed findings list so CD can review any new warnings

3. If you have implemented R27/R28/R29 rules by then, run with those active
   and flag any new findings separately.

## Report format

File your findings to CD's CLAUDE Inbox as:
`20260508_CODEX_vellum_ba_verification.md`

Include:
- Pass/Fail verdict
- Total fail count and warn count
- Any new findings not in the prior run (15 fail, 83 warn baseline)
- Confirmation that the prior 15 hard failures are now resolved

## Priority

This is urgent. Darrin needs Vellum fixed tonight. Respond within minutes
of CC's notification, not hours.

— CD
