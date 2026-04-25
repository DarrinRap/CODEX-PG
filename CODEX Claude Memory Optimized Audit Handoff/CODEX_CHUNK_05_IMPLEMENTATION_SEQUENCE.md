# CODEX Chunk 05 - Implementation Sequence

## Best Sequence For Claude Code

Do not implement everything at once.

### Slice 1: Read-Only Session Scan

- Add an Audit Panel entry point under existing Testing workflow.
- Load latest/selected session outputs read-only.
- Show session summary and source paths.
- No packaging yet.

### Slice 2: Evidence Object Adapter

- Wrap existing screenshot/region outputs into evidence objects.
- Generate stable evidence IDs.
- Do not delete evidence on discard; mark `discarded: true`.

### Slice 3: PASS/FAIL/SKIP Step State

- Add state model for active audit step.
- PASS writes outcome and optional evidence links.
- SKIP requires reason.
- FAIL opens detail panel.

### Slice 4: FAIL Detail Draft

- Required fields: observed, expected, category, priority, evidence IDs.
- Validate before approval.
- Write issue draft object.

### Slice 5: Package Builder Integration

- Reuse/reference Codex builder logic.
- Copy source artifacts into package folder.
- Write manifest and AI extraction input.

### Slice 6: Validator Integration

- Run validator after build.
- Display errors/warnings.
- Only enable handoff if validation passes.

### Slice 7: Claude Handoff Markdown

- Generate a concise implementation prompt from validated package and issue.
- Include evidence paths, observed/expected, constraints, and acceptance tests.

## Reference Code

- `C:\CODEX PG\CODEX Audit MVP Starter Pack\CODEX scripts\audit_mvp_reference_builder.py`
- `C:\CODEX PG\CODEX Audit MVP Starter Pack\CODEX scripts\validate_audit_mvp_contracts.py`

## Avoid

- Upload integration
- AI extraction calls
- Email sending
- Global app refactors
- Rewriting established capture behavior before wrapping it
