# CODEX PAH Release Candidate Checklist - 2026-05-06

Status: Release-candidate checklist
Scope: PAH only

## Include Candidate

- `CODEX_agent_hub.py`
- `CODEX_pah_inspector.py`
- `CODEX_pah_periodic_health_check.py`
- `CODEX_run_smoke_tests.py`
- `pah_mailbox/atomic.py`
- `CODEX config/CODEX_pah_accepted_advisories.json`
- `CODEX_PAH_HEALTH_POLICY.md`
- `CODEX_pah_repeat_health_verify.py`
- `CODEX_PAH_EXCELLENT_FINAL_STATE_SPEC_v1.0.md`
- `CODEX_PAH_MINIMAL_REMAINING_FIXES_SPEC_v1.0.md`
- `CODEX_PAH_EXCELLENCE_EXECUTION_SPEC_v1.0.md`
- `CODEX_PAH_RELEASE_INVENTORY_20260506.md`
- `CODEX_PAH_BACKLOG_TRIAGE_20260506.md`
- `CODEX_PAH_OWNER_DECISIONS_20260506.md`
- `CODEX_PAH_BACKLOG_CLOSURE_RECOMMENDATIONS_20260506.md`
- `CODEX_PAH_RELEASE_CANDIDATE_CHECKLIST_20260506.md`
- `CODEX_PAH_VERIFICATION_REPORT_20260506.md`
- `CODEX_pah_live_endpoint_verify.py`
- `CODEX_pah_ui_smoke_verify.py`

## Hold Out

- `CODEX mockups/` pending owner decision.
- `tmp_capture_pah_header.py` pending owner decision or deletion approval.
- `CODEX_agent_hub_ui.html` because it is currently clean and not part of this backend release.

## Required Verification

- Python syntax check passes for changed PAH Python files.
- `CODEX_run_smoke_tests.py` passes.
- `CODEX_pah_inspector.py` reports zero failures.
- `CODEX_pah_periodic_health_check.py` exits successfully.
- `CODEX_pah_repeat_health_verify.py` passes.
- Live `/api/health` responds and explains any remaining warnings.
- Read-only live endpoint verifier passes.
- Browser UI smoke verifier passes.

## Accepted Advisories

- `shadow_snapshot_from_legacy_state`: accepted transitional state, review after 2026-06-15.
- `cc_sidecar_absent_idle`: accepted idle/complete CC sidecar behavior, review after 2026-06-15.

## Release Decision

Operationally excellent if required verification passes and remaining warnings are limited to:

- backup/commit state before release approval
- backlog waiting on Darrin/CD closure decisions
- accepted advisory state with review dates

Release-final only after Darrin approves the release scope and commit.

## Current Verification Result

Verification passed with expected warnings on 2026-05-06 11:49 America/Los_Angeles. See `CODEX_PAH_VERIFICATION_REPORT_20260506.md`.
