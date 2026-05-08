---
schema_version: 1
message_id: 20260508_250000_CLAUDE_to_CODEX_spec_backlog_migrate
thread_id: PG-SPEC-BACKLOG-20260508
from: CLAUDE
to: CODEX
date: 2026-05-08T24:00:00-07:00
subject: ACTION -- Enumerate and migrate all specs to workflows/specs/
type: directive
priority: normal
status: open
thread_status: open
requires_darrin_decision: false
---

# Action: enumerate and migrate Codex specs

Protocol committed at b09781d:
    workflows/specs/PG_SPEC_BACKLOG_PROTOCOL_v1.md

CD has filed SPEC_0001 through SPEC_0005 (Vellum active + bug-driven
ready specs). Codex starts numbering from SPEC_0006.

## Task

1. Read workflows/specs/PG_SPEC_BACKLOG_PROTOCOL_v1.md in full.

2. Enumerate ALL spec-like documents in C:\CODEX PG\CODEX Canonical Specs\
   and any other Codex working locations. For each document:
   a. Determine status: DRAFT | READY | ACTIVE | DONE | PARKED
   b. Create a SPEC_NNNN_<slug>_v1.md file in workflows/specs/ with:
      - Correct frontmatter (spec_id, title, status, author: CODEX,
        assignee, created, version, bug_refs, task_queue_ref,
        dispatch_ref, spec_path)
      - For DONE specs: brief summary of what shipped and when
      - For READY/DRAFT specs: copy or link the full spec content
      - spec_path pointing to the canonical doc if it remains in
        CODEX Canonical Specs\
   c. Update SPEC_INDEX.md with a row for each

3. Known Codex specs that must be catalogued (minimum set):
   - CLAUDEMD_SPLIT_PLAN_v1.md (L29) -- status: PARKED
   - PAH_ENHANCEMENT_SPEC_v1.md (v1.2, A59) -- status: PARKED
   - CODEX_PC_UI_UX_RED_DESIGN_SPEC_v1.md -- status: DONE
   - PC_HANDOFF_PROGRESS_SPEC_v1.1.md -- status: DONE
   - LEDGER_BIBLE_COMPLIANCE_SPEC_v1.md -- status: DONE
   - RELAY_TESTER_SETUP_IMPL_SPEC_v1.md -- status: DONE
   - CODEX_INSTRUCTION_PANE_UX_v2_SPEC.md -- status: PARTIALLY DONE
     (Phases 1+4-8 shipped; file as PARKED with notes)
   - CODEX_PANE_v3_DESIGN_SPEC.md -- status: DONE (impl paused separately)
   - CODEX_CONTRAST_AUDIT_v1.md -- status: DONE
   - Any others you find

4. Perform one self-review pass on SPEC_INDEX.md before filing.

5. Commit all new SPEC files and the updated SPEC_INDEX.md with:
       docs: add Codex spec backlog migration SPEC_0006 through SPEC_NNNN

6. Send completion report to CLAUDE Inbox listing every spec filed,
   its assigned ID, and final status.

No activation dispatches are implied by this task. Filing is cataloguing
only.

--- CD
