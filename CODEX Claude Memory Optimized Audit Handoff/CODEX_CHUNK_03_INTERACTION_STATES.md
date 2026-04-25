# CODEX Chunk 03 - Interaction States

Use these stable internal state names.

## Core States

- `audit_idle`: panel open, no session selected
- `audit_session_selected`: source session selected and scanned
- `audit_step_ready`: step ready for PASS/FAIL/SKIP
- `audit_capture_armed`: capture tool armed
- `audit_capture_in_progress`: screenshot/region capture running
- `audit_region_review`: review dialog open
- `audit_decision_pending`: evidence exists, tester must choose PASS/FAIL/SKIP
- `audit_fail_detail_editing`: FAIL detail panel open
- `audit_issue_draft`: structured issue exists
- `audit_package_draft`: package folder exists, not validated
- `audit_package_local_ready`: package validates locally
- `audit_handoff_ready`: Claude handoff prompt ready
- `audit_error_recoverable`: user can retry/recover
- `audit_archived`: local package closed/archived

## Critical Flow

1. `audit_idle` -> user selects session -> `audit_session_selected`
2. `audit_session_selected` -> RUN STEP -> `audit_step_ready`
3. `audit_step_ready` -> CAPTURE -> `audit_decision_pending`
4. `audit_step_ready` -> MARK REGION -> `audit_capture_armed`
5. `audit_capture_armed` -> complete region -> `audit_region_review`
6. `audit_region_review` -> SAVE EVIDENCE -> `audit_decision_pending`
7. `audit_decision_pending` -> FAIL -> `audit_fail_detail_editing`
8. `audit_fail_detail_editing` -> APPROVE ISSUE -> `audit_issue_draft`
9. `audit_issue_draft` -> BUILD PACKAGE -> `audit_package_draft`
10. validation passes -> `audit_package_local_ready`
11. open handoff -> `audit_handoff_ready`

## Rule Summary

- FAIL requires evidence unless explicitly marked as a test-authoring/unobservable issue.
- FAIL requires observed behavior and expected behavior.
- SKIP requires a reason.
- Discarded evidence is retained but marked `discarded: true`.
- Handoff is disabled until validation passes.

Full state/action table:

`C:\CODEX PG\CODEX Audit Module Interaction Spec\CODEX_AUDIT_INTERACTION_STATE_MATRIX_v1.csv`

Full detailed spec:

`C:\CODEX PG\CODEX Audit Module Interaction Spec\CODEX_AUDIT_MODULE_INTERACTION_SPEC_v1.md`
