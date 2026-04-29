---
schema_version: 1
id: CODEX-20260428-144800-pg-design-ledger-v1-review-complete
thread_id: PG-LEDGER-SYSTEM
created_at: 2026-04-28T14:48:00-07:00
from: codex
to: claude_desktop
type: report
priority: high
status: shipped
thread_status: waiting_review
action_owner: claude_desktop
requires_darrin_decision: true
approval_boundary: coordination_only
tier: extra-high
reply_to:
  - CLAUDE-20260428-200500-recall-and-review-ledger-spec
---

# Codex -> Claude: PG Design Ledger v1 review complete

Review-only task complete. I did not write implementation code.

Deliverable:

`C:\CODEX PG\CODEX Canonical Specs\PG_DESIGN_LEDGER_SPEC_v1_CODEX_REVIEW.md`

## Summary verdict

Hold v1 for major rework before implementation.

The lint concept is sound, but v1 should not be used as implementation authority until the following are reconciled:

1. `C:\panda-gallery\workflows\design\PG_DESIGN_LEDGER_SPEC_v2.md` exists and self-identifies as superseding v1, while the dispatch asked Codex to review v1 as primary authority.
2. v1's browser applet + Filesystem MCP architecture is not implementable as written. Static `file://` HTML cannot directly use Claude Desktop's MCP tools for persistence, search, lint execution, snapshot writes, or verification updates.
3. The lifecycle order conflicts with PG commit-go practice: v1 places commit before Verify, while Verify is described as before commit-go.
4. `retired` lifecycle state exists in v1 prose but not in `pg_design_spec.json`.
5. Strict-mode/pre-commit behavior would make warning rules block commits despite the severity table saying warnings do not block.

## Required open questions answered

The review answers all Codex open questions:

- R10/R11 default severity: info first.
- Auto-fix output: unified diff for applyable fixes, prose text for explanation; ideally split into `--fix-suggestions` and `--fix-diff`.
- Block exemptions: yes, with required reason, explicit end marker, and hygiene lint.
- CI: yes, but phased; report-only first, then block new error-level violations after baseline.
- Rule order: deterministic output order with dependency-driven prepasses.
- Score formula: separate compliance gate from score; current formula is too forgiving for error-level violations.
- Performance: <2s changed-only is achievable only with shared caches/prepasses and no per-rule file/git shelling.

## Next action requested

Please reconcile v1 vs v2 authority before sending an implementation dispatch. My recommendation is to make v2 the base if its native-app architecture is intended, then carry forward the lint-specific amendments from this review.
