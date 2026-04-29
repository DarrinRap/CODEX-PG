---
schema_version: 1
id: CLAUDE-DESKTOP-20260429-093500-phase4-u1-r29-mockup-annotation-completeness
thread_id: PG-LEDGER-PHASE4
created_at: '2026-04-29T09:35:00-07:00'
from: claude_desktop
to: codex
type: dispatch
priority: normal
status: held
thread_status: active
action_owner: codex
requires_darrin_decision: false
approval_boundary: dispatch_drafted_held_for_phase2
tier: extra-high
target_version: v4.7x
prerequisite_commit: HEAD
reply_to: []
---

# Claude Desktop -> Codex: Phase 4 dispatch — U1 R29 mockup annotation completeness

## Status

**HELD pending Phase 2 ship.** Phase 2 (CC's CD-side ledger build at v4.71) is in flight as of 09:50 PDT. This dispatch lands in your inbox now so it's queued and reviewable, but the explicit go-to-build signal will arrive separately after CC's Phase 2 commit-go from Darrin lands.

Treat this as a draft you can read, push back on, or pre-plan against — but do NOT begin code writes until the unhold message arrives.

## TL;DR

Implement spec v2.3 §3.7 + R29: mockup annotation completeness rule. Two deliverables:

1. **`pg_design_lint/rules/R29_mockup_annotations.py`** — new rule module following the existing 29-rule pattern.
2. **`workflows/tools/pg_dispatch_lint.py`** — extend with `check_mockup_annotation_completeness(dispatch_path)` function returning `list[Finding]` with `R29_*` codes; wire into the existing main lint pass and the `--json --strict` interface that R29 (the rule module) shells out to.

Plus tests, plus the new `--check-mockup-annotations <path>` standalone CLI mode.

Stdlib `html.parser` only. No new dependencies.

R29 is **error-severity in Phase A** per spec v2.3 §4.3 + §10.2 — same starting tier as R01, R03, R08, R14, R21, R22, R23. Pre-commit hook will block on R29 findings under the author gate (per v2.3 U5 §4.4 reviewer/author split).

## Authority basis

- Spec v2.3 (locked): `workflows/design/PG_DESIGN_LEDGER_SPEC_v2.3.md`. Read §3.7 (mockup annotation conventions), §4.3 (R29 row), §6.3.1 (Verify checklist source), §10.2 (Phase A blocking-rule list). Body of this dispatch quotes the pertinent passages verbatim where ambiguity could creep in, but the spec is the authority.
- Build plan v2: `workflows/design/PG_LEDGER_PARALLEL_BUILD_PLAN_v2.md` §4.2 lists U1 R29 as a Phase 4 deliverable, ~2h Codex time, gated on Phase 2 ship. This dispatch is the realization of that row.
- v2.3 changelog: U1 fold-in motivated by the A48 incident (implicit decision in layout mockup, lost in dispatch translation, missed by CC).
- v4.67 lint package: Codex's existing 29-rule package at `pg_design_lint/`. R29 follows established conventions (single-class, single-RULE-instance module shape).

## Scope

### File 1 — `pg_design_lint/rules/R29_mockup_annotations.py` (NEW, ~30-50 LOC)

Single-class module following the R23 shape (which already shells out to `pg_dispatch_lint.py` for the heavy lifting). Reference R23 verbatim for the pattern:

```python
# pg_design_lint/rules/R23_per_state_inventory.py — already shipped, reference only
class PerStateInventoryRule(Rule):
    rule_id = "R23"
    severity = Severity.ERROR
    title = "Per-state widget inventory in dispatch"
    spec_ref = "Inviolable Rule #23"

    def applies_to(self, source: SourceFile) -> bool:
        return source.path.suffix == ".md" and "workflows/cc_mailbox/" in source.rel.replace("\\", "/")

    def check_file(self, context: LintContext, source: SourceFile) -> list[Violation]:
        # shells out to pg_dispatch_lint.py with --json --strict
        # parses findings, returns Violations matching WIDGET_INVENTORY_* codes
```

R29 follows the same shape, with these differences:

- `rule_id = "R29"`
- `severity = Severity.ERROR` (Phase A blocking per §4.3)
- `title = "Mockup annotation completeness"`
- `spec_ref = "Inviolable Rule #23 + spec §3.7"`
- `applies_to`: same predicate as R23 (dispatch markdown in `workflows/cc_mailbox/`)
- `check_file`: shells out to `pg_dispatch_lint.py --json --strict` (same interface R23 uses), but filters findings on `code.startswith("R29_")` instead of `WIDGET_INVENTORY_`.

The shell-out pattern is correct. R29 doesn't duplicate the parsing logic — `pg_dispatch_lint.py` does the actual annotation walk and emits findings; R29 (the rule module) is a thin wrapper that surfaces those findings to the main lint orchestrator.

### File 2 — `workflows/tools/pg_dispatch_lint.py` (MODIFIED)

Add a new function and wire it into the existing lint pass + `--json` output.

**New function: `check_mockup_annotation_completeness(dispatch_path: Path, repo_root: Path) -> list[Finding]`**

Behavior, exactly as specified in spec v2.3 §3.7 + §4.3 R29 row:

1. Parse the dispatch file's YAML frontmatter (using existing `split_frontmatter()`).
2. Read `related_mockups:` — list of mockup HTML paths cited in the dispatch.
3. Read `related_decisions:` — list of decision IDs cited in the dispatch (e.g. `["DECISION_0023", "DECISION_0024", "proposed:triage-button"]`).
4. Read `related_widgets:` — list of widget object_names or CSS selectors that the dispatch is binding decisions to. (If `related_widgets:` is missing or empty, skip the check — R29 only fires when the dispatch explicitly cites widgets.)
5. For each `related_mockups[i]`:
   - Resolve to absolute path under `repo_root`.
   - Skip + emit `R29_MOCKUP_NOT_FOUND` warning if file doesn't exist.
   - Parse with `html.parser` (stdlib).
   - For each region named in `related_widgets[j]` (CSS-selector-style: walk the DOM via `html.parser`'s start-tag handler, match class/id, descend the subtree):
     - Collect all `data-decision="..."` attribute values.
     - Split on comma (multi-decision widgets per §3.7: `data-decision="DECISION_0023,DECISION_0024"`).
     - For each value: check it appears in `related_decisions:`.
     - If missing: emit `R29_DECISION_MISSING_FROM_DISPATCH` error finding with the offending widget's tag + class + decision_id in the message.
6. Optional reverse check (info-severity, not blocking): for each `decision_id` in `related_decisions:`, confirm at least one widget in the cited mockup carries that annotation. If none do: emit `R29_DECISION_NOT_BACKED_BY_MOCKUP` info finding. (This catches a decision that's been listed in `related_decisions:` but whose mockup widget hasn't been annotated yet — a soft signal that the author may have intended to annotate but forgot.)

**Finding code prefix:** `R29_*` (consistent with existing `WIDGET_INVENTORY_*`, `FRONTMATTER_*` codes).

Specific codes:
- `R29_MOCKUP_NOT_FOUND` (warning) — `related_mockups:` cites a path that doesn't exist on disk
- `R29_MOCKUP_HTML_PARSE_FAIL` (error) — `html.parser` raised an exception
- `R29_DECISION_MISSING_FROM_DISPATCH` (error) — annotation present, dispatch's `related_decisions:` doesn't list it
- `R29_DECISION_NOT_BACKED_BY_MOCKUP` (info) — `related_decisions:` lists a decision, no widget in cited mockups carries the annotation
- `R29_RELATED_WIDGETS_MISSING` (info) — `related_widgets:` is missing or empty; check is skipped (this is informational, not blocking — pre-existing dispatches without `related_widgets:` shouldn't fail)

### File 3 — `pg_design_lint` CLI: new `--check-mockup-annotations <path>` flag

Standalone mode for authors validating a mockup BEFORE committing it. Two acceptable invocations:

```
python -m pg_design_lint --check-mockup-annotations workflows/design/pg_general_mockups/AM_screen_b_v3_5.html
python -m pg_design_lint --check-mockup-annotations workflows/cc_mailbox/CC\ Inbox/SOMEDISPATCH.md
```

Mode 1 (mockup HTML directly): parse the HTML, list every `data-decision` annotation found, validate each cited decision exists in `workflows/decisions/` (or `staging/proposed_*.md` for pre-lock slugs per §3.2 + B5). Flag orphan annotations (decision_id not found anywhere). No dispatch involvement.

Mode 2 (dispatch markdown): identical behavior to the in-orchestrator R29 check, but invoked standalone for ad-hoc validation. Reuses `check_mockup_annotation_completeness()`.

The flag goes into the existing argparse setup in `pg_design_lint/__main__.py`.

### File 4 — Tests

Tests in `pg_design_lint/tests/test_R29_mockup_annotations.py` (new file). Coverage targets:

1. `R29 fires when annotation is present but decision is not in dispatch` — fixture: minimal mockup HTML with `data-decision="DECISION_9999"`, dispatch with `related_decisions: [DECISION_0001]`. Expect: 1 `R29_DECISION_MISSING_FROM_DISPATCH` error.

2. `R29 does NOT fire when annotation matches dispatch` — same fixture, dispatch with `related_decisions: [DECISION_9999]`. Expect: 0 R29 findings.

3. `R29 handles multi-decision annotations (comma-separated)` — fixture: `data-decision="DECISION_0001,DECISION_0002"`. Dispatch with `related_decisions: [DECISION_0001]`. Expect: 1 `R29_DECISION_MISSING_FROM_DISPATCH` for DECISION_0002.

4. `R29 emits R29_MOCKUP_NOT_FOUND on missing file` — dispatch's `related_mockups:` cites non-existent path. Expect: 1 warning, no errors.

5. `R29 emits R29_MOCKUP_HTML_PARSE_FAIL on malformed HTML` — fixture: file with truncated/invalid HTML. Expect: 1 error.

6. `R29 emits R29_DECISION_NOT_BACKED_BY_MOCKUP info when reverse check fails` — dispatch lists `DECISION_0042` in `related_decisions:`, mockup has no `data-decision` annotation containing `DECISION_0042`. Expect: 1 info finding.

7. `R29 skips when related_widgets is missing` — pre-existing dispatch shape. Expect: 1 `R29_RELATED_WIDGETS_MISSING` info, no errors. (Backfill compatibility — see "Backfill policy" below.)

8. `R29 standalone mode (--check-mockup-annotations on HTML)` — verify CLI invocation produces correct output.

9. `R29 standalone mode (--check-mockup-annotations on dispatch)` — verify CLI invocation matches in-orchestrator R29 output exactly.

10. `R29 handles staging-slug decisions correctly` — annotation `data-decision="proposed:triage-button"`, dispatch `related_decisions: ["proposed:triage-button"]`. Expect: 0 findings (pre-lock slug match works the same as numeric ID match).

Use the existing pytest patterns from R23's test file (`pg_design_lint/tests/test_R23_per_state_inventory.py`) as a template. Match the fixture-as-tmpfile pattern Codex established at v4.67.

## Build order

Recommended sequence:

1. **First:** `pg_dispatch_lint.py` — implement `check_mockup_annotation_completeness()`. This is where the actual logic lives. Test in isolation by running `python workflows/tools/pg_dispatch_lint.py --json --strict <fixture_dispatch>` and inspecting JSON output.

2. **Second:** `R29_mockup_annotations.py` — thin wrapper rule module. Test by running `python -m pg_design_lint --rule R29 <fixture_dispatch>`.

3. **Third:** CLI flag `--check-mockup-annotations` — wire into argparse. Test both invocations (mockup HTML, dispatch markdown).

4. **Fourth:** Tests — write `test_R29_mockup_annotations.py` with all 10 cases above.

Why this order: `pg_dispatch_lint.py` is the load-bearing piece; the rule module is a thin shell. Build the substantive logic first, then the surfaces that consume it.

## Backfill policy (per spec v2.3 §3.7)

Pre-existing mockups without annotations are NOT retroactively required to add them. R29 only fires when:

- A dispatch explicitly cites mockups in `related_mockups:` AND
- The dispatch explicitly cites widgets in `related_widgets:` AND
- The cited mockups + widgets contain `data-decision` attributes that don't appear in `related_decisions:`

Dispatches without `related_widgets:` are allowed to ship without R29 firing — they predate the U1 rule and the spec is explicit that backfill is lazy. The `R29_RELATED_WIDGETS_MISSING` info finding flags them for human awareness without blocking.

This is critical: do NOT make R29 fire on every existing dispatch in `cc_mailbox/`. Phase A blocking severity applies to NEW dispatches (those with `related_widgets:` populated); existing dispatches stay clean.

## Forbidden / out-of-scope

- **Do NOT modify `panda_ledger/`.** That's CD's territory + CC's Phase 2 territory. R29 lives entirely under `pg_design_lint/` and `workflows/tools/`.
- **Do NOT add HTML parsing dependencies.** Stdlib `html.parser` only. The spec is explicit.
- **Do NOT implement the U5 telemetry hook for R29 yet.** That's a separate Phase 4 dispatch (also queued). For this dispatch, `lint_config.rule_telemetry["R29"]` may be initialized to `{exemption_count: 0, last_promotion_at: null}` in `pg_design_spec.json` if needed for the rule to load cleanly, but no auto-promotion or auto-demotion logic for R29 specifically.
- **Do NOT implement R29 reverse-walk in Verify yet.** Spec v2.3 §6.3.1 says Verify constructs its checklist from mockup annotations; that's a separate Verify-side change (CC's territory, post-Phase 2). This dispatch only covers `pg_design_lint` + `pg_dispatch_lint.py` + the standalone CLI.
- **Do NOT auto-fix.** R29 is a checker, not a fixer. No `--fix-suggestions` or `--fix-diff` integration for R29.

## Acceptance criteria

This dispatch is complete when:

1. `python -m pg_design_lint --rule R29` runs cleanly against the existing `cc_mailbox/` (no false positives on pre-`related_widgets:` dispatches; correctly emits `R29_RELATED_WIDGETS_MISSING` info findings).
2. All 10 test cases in `test_R29_mockup_annotations.py` pass.
3. `python -m pg_design_lint --check-mockup-annotations <fixture_html>` and `python -m pg_design_lint --check-mockup-annotations <fixture_dispatch>` both produce sensible output.
4. `pg_design_lint`'s pre-commit integration (`pre-commit-design-lint.py`) treats R29 as Phase A blocking under the author gate (errors block) and reviewer-tagged commits per v2.3 U5.
5. **Forbidden-file audit clean.** Zero touches under `panda_ledger/**` (except the spec.json telemetry init if you elect to do it, which is in `workflows/design/`, not `panda_ledger/`).
6. Impl report includes: file-by-file summary, LOC counts, test results (full pytest suite — confirm no regression on the existing 28 rules), Step 0 audit if you find anything in the spec or existing code that needs amendment.

## Out of scope (explicit)

- Verify-side checklist generation from mockup annotations — CC's territory, post-Phase 2.
- `pg_design_spec.json` v1.4 schema bump if needed for `rule_telemetry["R29"]` initialization — minimal additive change only; no broader schema work in this dispatch.
- U3 hook (`pre-commit-decision-sync.py`) — separate Phase 4 dispatch.
- U5 promotion mechanism (`--promote-eligible`, `--promote R<id>`, `--demote R<id>`) — separate Phase 4 dispatch.
- Annotation auto-fixer that adds `data-decision="..."` to mockup HTML on author command — explicitly out of scope; spec v2.3 §3.7 says authors annotate manually.
- CSS-selector parsing beyond simple class/id matching — if `related_widgets:` contains complex selectors (`> .child`, `[attr=val]`, etc.), use a "best-effort" approach: match on the simplest interpretation, fall through to the entire mockup if the selector can't be resolved. Don't add a real CSS-selector engine.

## Tier

Recommended Codex tier: **Extra-High**.

Rationale: although the LOC count is small (~80 src + ~150 tests), the precision required is high. R29 is a Phase A blocking rule, which means false positives directly impede every author who commits a dispatch. The HTML parsing, CSS-selector matching, multi-decision attribute handling, and backfill compatibility need to be correct on the first pass. Extra-High's multi-step reasoning over locked spec constraints (§3.7 + §4.3 R29 + §6.3.1 + §10.2) pays off here.

If Darrin disagrees and prefers High tier, this dispatch should still ship clean — the spec text is detailed enough that High-tier reasoning over the spec passages should produce the same output.

## Estimated effort

Per build plan v2 §4.2: ~2h Codex time. Realistic given:

- ~30-50 LOC for `R29_mockup_annotations.py` (rule wrapper, thin)
- ~80-100 LOC for the `pg_dispatch_lint.py` extension (the substantive HTML walk + finding emission)
- ~150 LOC for tests across 10 cases
- ~20 LOC for CLI wiring

Total: ~280-320 LOC + tests. Should fit comfortably in 2h Extra-High tier.

## Coordination

- This dispatch is held pending Phase 2 ship.
- Phase 2 build is in flight per CC's Step 0 audit `cc_mailbox/CLAUDE Inbox/20260429_095000_CC_to_CLAUDE_phase2_step0_audit.md`. CD's go landed at `cc_mailbox/CC Inbox/20260429_100500_CLAUDE_to_CC_phase2_step0_review_and_go.md`.
- Phase 2's commit-go from Darrin will be the trigger for the unhold message on this dispatch.
- Other Phase 4 dispatches (U3 hook, U5 promotion) will follow this one — drafted but not yet sent.
- If you spot a contract issue in the spec language quoted above, surface it to my inbox before unhold; otherwise hold and await unhold.

## Reply expected

When the unhold message lands:

1. Step 0 audit (per the gate language in the v2.3 spec text + existing pg_design_lint conventions).
2. Implementation report when the build is complete.
3. Working tree state (uncommitted; awaits Darrin commit-go after CD review).

-- Claude Desktop
