# CODEX Message To Claude - Audit MVP Handoff

## Message To Send Claude Chat First

Claude, I am giving you a Codex-prepared, memory-optimized handoff package for the Panda Gallery Audit MVP.

The package is here:

`C:\CODEX PG\CODEX Claude Memory Optimized Audit Handoff`

Please read only these two files first:

1. `C:\CODEX PG\CODEX Claude Memory Optimized Audit Handoff\CODEX_READ_ME_FIRST.md`
2. `C:\CODEX PG\CODEX Claude Memory Optimized Audit Handoff\CODEX_SEARCHABLE_INDEX.md`

Do not edit `C:\panda-gallery` yet.

What you are receiving:

- A staged read protocol so you are not overloaded with too much context at once.
- A searchable index that tells you which small chunk to read for each task.
- Small focused chunks for orientation, UX target, interaction states, data contracts, implementation sequence, and testing acceptance.
- PG-aligned fullscreen Audit UX mockups using the established Panda Gallery dark palette and PASS/FAIL/SKIP vocabulary.
- A full interaction spec that defines `state -> user action -> system response -> data written -> error handling -> next state`.
- JSON/package/evidence contracts and reference Python builder/validator code from Codex.

What we need from you first:

1. Summarize your understanding of the Audit MVP in plain English.
2. Confirm the boundaries: local-only first, no upload, no AI API calls, no email sending, no PHI workflow, no broad refactor.
3. Tell us which single chunk you want next from the index.
4. Propose the safest first implementation slice for Claude Code.

Do not start implementation until you have summarized the plan and identified the one chunk needed next.

## Message To Send Claude Code After Claude Chat Plans

Claude Code, implement only the first local-only Audit MVP slice for Panda Gallery.

Start with these files:

1. `C:\CODEX PG\CODEX Claude Memory Optimized Audit Handoff\CODEX_CLAUDE_CODE_TASK_PROMPT.md`
2. The one chunk selected by Claude Chat from `C:\CODEX PG\CODEX Claude Memory Optimized Audit Handoff`

Do not read the entire Codex package unless a specific file is referenced by the selected chunk.

Do not edit broadly.

Implementation boundaries:

- Local-only Audit MVP first.
- No Dropbox/upload.
- No AI provider calls.
- No email sending.
- No real PHI workflow.
- No broad UI rewrite.
- Preserve existing Panda Gallery testing/capture behavior where practical.
- Match the established PG dark testing UI vocabulary.
- Do not delete evidence files during discard; mark `discarded: true`.
- Copy source testing artifacts into package output; do not mutate source artifacts.

First preferred slice:

1. Inspect relevant current PG files read-only.
2. Identify the smallest Testing menu / audit panel integration point.
3. Add or prepare a read-only Audit Panel/session scan path.
4. Load a selected/latest testing session and show summary metadata.
5. Do not implement upload, AI extraction, email, or final dashboard.
6. Report files changed, behavior added, tests run, and risks.

Definition of done for this first slice:

- The implementation is narrow and reversible.
- Existing PG behavior is not broken.
- The Audit MVP can identify/load a testing session or sample session source.
- Any new state/data written follows the Codex interaction/data contracts.
- You report exact files changed and tests/smoke checks run.

## What Not To Do

- Do not ingest every Codex document at once.
- Do not implement all screens in one pass.
- Do not redesign Panda Gallery globally.
- Do not create upload/email/AI integration yet.
- Do not use real patient data or PHI.
- Do not ignore the PG-aligned visual language.

## Where The Supporting Materials Live

Memory-optimized handoff:

`C:\CODEX PG\CODEX Claude Memory Optimized Audit Handoff`

Full interaction spec:

`C:\CODEX PG\CODEX Audit Module Interaction Spec\CODEX_AUDIT_MODULE_INTERACTION_SPEC_v1.md`

State matrix:

`C:\CODEX PG\CODEX Audit Module Interaction Spec\CODEX_AUDIT_INTERACTION_STATE_MATRIX_v1.csv`

PG-aligned mockups:

`C:\CODEX PG\CODEX Audit UX Fullscreen Walkthrough PG Aligned`

Audit MVP starter pack:

`C:\CODEX PG\CODEX Audit MVP Starter Pack`

Canonical schemas:

`C:\CODEX PG\CODEX Canonical Specs\CODEX_SESSION_PACKAGE_SCHEMA_v1.md`

`C:\CODEX PG\CODEX Canonical Specs\CODEX_AUDIT_ISSUE_SCHEMA_v1.md`
