# CODEX Searchable Index - Audit MVP Handoff

Use this as the router. Search by tag, purpose, or file path. Read only the chunk needed for the current task.

## Read Order

| Order | File | Purpose | Read When |
| --- | --- | --- | --- |
| 0 | `CODEX_READ_ME_FIRST.md` | Protocol and guardrails | Always first |
| 1 | `CODEX_SEARCHABLE_INDEX.md` | Routing table | Always second |
| 2 | `CODEX_CHUNK_01_ORIENTATION.md` | What the Audit MVP is | Before any planning |
| 3 | `CODEX_CHUNK_02_VISUAL_UX_TARGET.md` | PG visual language and mockups | Before UI work |
| 4 | `CODEX_CHUNK_03_INTERACTION_STATES.md` | State/action workflow | Before interaction implementation |
| 5 | `CODEX_CHUNK_04_DATA_CONTRACTS.md` | JSON/package/evidence contracts | Before data or package code |
| 6 | `CODEX_CHUNK_05_IMPLEMENTATION_SEQUENCE.md` | Safe coding order | Before Claude Code edits |
| 7 | `CODEX_CHUNK_06_TESTING_ACCEPTANCE.md` | Validation and done criteria | Before PR/checkpoint |
| 8 | `CODEX_CLAUDE_CODE_TASK_PROMPT.md` | Short implementation prompt | Give to Claude Code with one chunk |

## Tags

### #orientation

Read: `CODEX_CHUNK_01_ORIENTATION.md`

Answers: What is the Audit MVP? What is in scope? What is not in scope?

### #visual #ux #palette #mockups

Read: `CODEX_CHUNK_02_VISUAL_UX_TARGET.md`

Key assets:

- `C:\CODEX PG\CODEX Audit UX Fullscreen Walkthrough PG Aligned\CODEX_audit_ux_fullscreen_walkthrough_PG_aligned_v2.html`
- `C:\CODEX PG\CODEX Audit UX Fullscreen Walkthrough PG Aligned\CODEX fullscreen frames\01_testing_audit_panel_PG_aligned.png`
- `C:\CODEX PG\CODEX Audit UX Fullscreen Walkthrough PG Aligned\CODEX fullscreen frames\02_workflow_capture_PG_aligned.png`
- `C:\CODEX PG\CODEX Audit UX Fullscreen Walkthrough PG Aligned\CODEX fullscreen frames\03_region_capture_review_PG_aligned.png`
- `C:\CODEX PG\CODEX Audit UX Fullscreen Walkthrough PG Aligned\CODEX fullscreen frames\04_fail_detail_panel_PG_aligned.png`
- `C:\CODEX PG\CODEX Audit UX Fullscreen Walkthrough PG Aligned\CODEX fullscreen frames\05_session_package_PG_aligned.png`
- `C:\CODEX PG\CODEX Audit UX Fullscreen Walkthrough PG Aligned\CODEX fullscreen frames\06_claude_handoff_PG_aligned.png`
- `C:\CODEX PG\CODEX Audit UX Fullscreen Walkthrough PG Aligned\CODEX fullscreen frames\07_end_to_end_flow_map_PG_aligned.png`

### #states #interaction #workflow

Read: `CODEX_CHUNK_03_INTERACTION_STATES.md`

Full source:

- `C:\CODEX PG\CODEX Audit Module Interaction Spec\CODEX_AUDIT_MODULE_INTERACTION_SPEC_v1.md`
- `C:\CODEX PG\CODEX Audit Module Interaction Spec\CODEX_AUDIT_INTERACTION_STATE_MATRIX_v1.csv`

### #schema #json #package #evidence

Read: `CODEX_CHUNK_04_DATA_CONTRACTS.md`

Full source:

- `C:\CODEX PG\CODEX Canonical Specs\CODEX_SESSION_PACKAGE_SCHEMA_v1.md`
- `C:\CODEX PG\CODEX Canonical Specs\CODEX_AUDIT_ISSUE_SCHEMA_v1.md`
- `C:\CODEX PG\CODEX Audit MVP Starter Pack\CODEX samples\expected_package\session_package_session_20260424_194422\session_package_manifest.json`
- `C:\CODEX PG\CODEX Audit MVP Starter Pack\CODEX samples\expected_package\session_package_session_20260424_194422\derived\sample_evidence_objects_v1.json`
- `C:\CODEX PG\CODEX Audit MVP Starter Pack\CODEX samples\sample_audit_issue_extraction_v1.json`

### #code #builder #validator

Read: `CODEX_CHUNK_05_IMPLEMENTATION_SEQUENCE.md`

Code references:

- `C:\CODEX PG\CODEX Audit MVP Starter Pack\CODEX scripts\audit_mvp_reference_builder.py`
- `C:\CODEX PG\CODEX Audit MVP Starter Pack\CODEX scripts\validate_audit_mvp_contracts.py`

### #testing #acceptance #done

Read: `CODEX_CHUNK_06_TESTING_ACCEPTANCE.md`

Full validation reference:

- `C:\CODEX PG\CODEX Audit MVP Starter Pack\CODEX validation output\CODEX_validation_report.json`

## Search Keywords

- `audit_idle`
- `audit_session_selected`
- `audit_step_ready`
- `audit_capture_armed`
- `audit_region_review`
- `audit_decision_pending`
- `audit_fail_detail_editing`
- `audit_package_local_ready`
- `audit_handoff_ready`
- `evidence_id`
- `ev_region_####`
- `ev_step_auto_####`
- `discarded: true`
- `session_package_manifest.json`
- `ai_extraction_input_v1.json`
- `audit_issue_extraction_v1.json`
- `PASS FAIL SKIP`
- `Region capture - Review`
- `Claude Handoff`
