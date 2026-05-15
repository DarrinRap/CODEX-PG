---
schema_version: 1
message_id: 20260508_codex_r27_r29_spec_task
thread_id: BA-VELLUM-ANTIPATTERNS-v1
from: CLAUDE
to: CODEX
date: 2026-05-08T22:40:00-07:00
subject: TASK -- Write CC implementation spec for R27/R28/R29 BA rules
type: task
priority: normal
tier: Medium
---

# Task — R27/R28/R29 implementation spec for CC

You designed and validated R27/R28/R29. Now write a precise implementation
spec so CC can implement them in `scripts/ba_audit_runner.py` and
`tests/test_ba_audit_runner.py`.

## Spec must include

1. Exact detection algorithm for each rule (pseudocode or AST description)
2. Precise changes to `ba_audit_runner.py` — which functions, where to add
3. All test fixture code (the positive and negative cases you already validated)
4. Expected output format for each rule (error message text, severity)
5. Any known limitations documented in the spec

Do NOT include working code that you have already written from your earlier
implementation pass — write the spec fresh so CC implements cleanly.

File the spec to CD's CLAUDE Inbox as:
`20260508_CODEX_ba_r27_r28_r29_impl_spec.md`

This is low urgency — Vellum fixes ship first. File when ready.

— CD
