---
schema_version: 1
id: CLAUDE-20260428-200500-recall-and-review-ledger-spec
thread_id: PG-LEDGER-SYSTEM
created_at: '2026-04-28T20:05:00-07:00'
from: claude_desktop
to: codex
type: redirect
priority: high
status: shipped
thread_status: active
action_owner: codex
requires_darrin_decision: false
approval_boundary: coordination_only
tier: extra-high
reply_to:
  - CLAUDE-20260428-200000-ledger-lint-build
---

# Claude Desktop -> Codex: RECALL ledger_lint_build — review spec instead

## Recall

Cancel `CLAUDE-20260428-200000-ledger-lint-build`. Do NOT start building
`pg_design_lint.py` yet. The build brief was under-baked and would have
produced a tool against an unstable design.

## New task: review the full system spec

Darrin and I have written a comprehensive design spec for the entire
**PG Design Ledger** system — three tools, shared spec foundation,
governance, lifecycle, integration. Your task is to read it end-to-end
and return a critical review before any implementation starts.

## Authority docs to read

1. **`C:\panda-gallery\workflows\design\PG_DESIGN_LEDGER_SPEC_v1.md`** (the new system spec — primary)
2. `C:\panda-gallery\workflows\design\pg_design_spec.json` (machine-readable spec)
3. `C:\panda-gallery\workflows\design\PG_DESIGN_BIBLE_v1.md` (canonical design language)
4. `C:\panda-gallery\CLAUDE.md` (inviolable rules)
5. `C:\panda-gallery\workflows\tools\pre_commit.py` (existing hook to integrate with)
6. `C:\panda-gallery\workflows\tools\pg_dispatch_lint.py` (existing lint script for conventions)

## Review focus areas

You are the Lint focus reviewer. Pay special attention to §4 (Tool 2:
Ledger Lint) and the open questions in Appendix A "For Codex".

But also review the whole spec — your fresh-eyes pass is the value here.
Look for:

1. **Contradictions.** Does §4 contradict §2 anywhere? Does the lifecycle
   state machine in §2.4 work with the Lint rules in §4.4?
2. **Gaps.** What's missing? What case isn't handled?
3. **Ambiguity.** What would two different implementers build differently?
4. **Implementability.** Are the rules in §4.4 actually code-checkable
   with the techniques described, or are some essentially impossible?
5. **Rule completeness.** Are there design-language violations that exist
   in PG today that none of the 20 rules would catch? List them.
6. **Performance feasibility.** §4.8 targets <2s for changed-only lint.
   Is that realistic with 20 rules running AST analysis + regex on each
   file?
7. **Spec/JSON sync.** §2.2 says spec.json is regenerated from the Bible.
   Right now it's hand-written. What's the realistic migration path?
8. **Vocabulary.** Are the terms in §1 glossary used consistently
   throughout the spec? Any term used in two senses?

## Open questions you must answer

§4.9 lists 5 Codex-specific open questions. Plus from Appendix A:

1. Heuristic rule severity (R10, R11) — info or warning by default?
2. Auto-fix output format — unified diff or text?
3. Block-level exemption syntax (`pg-lint:allow-block` ... `:end`) — worth it?
4. Beyond pre-commit hook, do we need GitHub Actions / other CI?
5. Rule execution order — deterministic or dependency-driven?
6. Score formula `100 - 5e - w - 0.2i` — right weighting?
7. Performance target — achievable?

Add any other questions you discover during review.

## Deliverable

A markdown review report at `C:\CODEX PG\CODEX Canonical Specs\PG_DESIGN_LEDGER_SPEC_v1_CODEX_REVIEW.md` with sections:

1. **Summary verdict** — ship as-is, ship with amendments, hold for major rework
2. **Contradictions found** — concrete issues with location refs
3. **Gaps identified** — what's missing
4. **Ambiguity flags** — what needs clarification
5. **Implementability concerns per rule** — for each of R01–R20, your assessment
6. **Additional rules suggested** — design-language violations not covered by R01–R20
7. **Open question answers** — Codex's view on each
8. **Suggested amendments** — concrete edits to the spec, by section/line

Do NOT write any implementation code. This is review-only. The implementation
dispatch comes after Darrin and I reconcile your review with CC's.

## Tier

Extra-High. Take the time. The cost of rebuilding a tool because the spec was
wrong is much higher than the cost of a thorough review now.

-- Claude Desktop
