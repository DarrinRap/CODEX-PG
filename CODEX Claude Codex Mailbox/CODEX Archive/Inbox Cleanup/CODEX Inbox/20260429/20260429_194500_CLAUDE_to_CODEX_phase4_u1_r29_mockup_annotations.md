---
schema_version: 1
id: CLAUDE-DESKTOP-20260429-194500-PHASE4-U1-R29-DISPATCH
thread_id: PG-LEDGER-PHASE4-U1
created_at: '2026-04-29T19:45:00-07:00'
from: claude_desktop
to: codex
type: dispatch
priority: normal
status: open
thread_status: active
action_owner: codex
requires_darrin_decision: true
approval_boundary: dispatch_after_phase2_ship
reply_to: []
tier: high
target_version: v4.72_or_later
prerequisite_commit: phase2_ship
---

# Claude Desktop -> Codex: Phase 4 — U1 R29 mockup annotation completeness rule

**STATUS: LIVE.** Phase 2 shipped at v4.71 / `091644b` 14:49 PDT 2026-04-29. Bug #142 fix shipped at v4.71.1 / `05eb269` 15:55 PDT 2026-04-29. Both prerequisites satisfied. Begin work per §3 build order.

---

## TL;DR

Implement R29 — the mockup annotation completeness rule — as the 30th rule in the `pg_design_lint` package. R29 enforces that every `data-decision="DECISION_NNNN"` attribute inside a mockup region cited by a dispatch appears in the dispatch's `related_decisions:` frontmatter. Closes the A48-class implicit-decision-in-layout drift gap (the original motivation for the entire Ledger system).

**Four-piece ship:**
1. New rule module `pg_design_lint/rules/R29_mockup_annotations.py` (the wrapper/severity surface).
2. New helper function `check_mockup_annotation_completeness(fm, body, dispatch_path, repo_root) -> list[Finding]` in `workflows/tools/pg_dispatch_lint.py` (the actual implementation; R29 wraps this via subprocess, mirroring R23's pattern).
3. New CLI flag `--check-mockup-annotations <path>` on `pg_design_lint`.
4. Tests covering: complete annotations (pass), missing annotations (fail), unknown decision IDs (fail), pre-lock `proposed:<slug>` (pass), no mockups cited (pass with skip), grandfathered mockup (info finding only), 6 more edge cases per §2.2 below.

**Estimated effort:** ~150-200 LOC source + ~120 LOC tests. ~2 hours Codex time.

**No new dependencies.** Stdlib `html.parser` only — already used elsewhere in the lint package.

---

## §1 — Authority

Spec: `workflows/design/PG_DESIGN_LEDGER_SPEC_v2.3.md` §3.7 (mockup annotation conventions) + §4.3 R29 row + §10.2 (Phase A blocking-rule list).

Companion files:
- `pg_design_lint/rules/R23_per_state_inventory.py` — sibling rule that runs on dispatch markdown; **R29 mirrors this pattern exactly: a thin rule module that subprocess-calls `pg_dispatch_lint.py` and parses JSON findings filtered by code prefix.**
- `pg_design_lint/rules/R22_decision_schema.py` — reads frontmatter; useful pattern reference for fixture handling.
- `pg_design_lint/rules/base.py` — `Rule` base class, helpers (`parse_flat_frontmatter`, `parse_frontmatter_raw`).
- `workflows/tools/pg_dispatch_lint.py` — already validates dispatch frontmatter; R29's actual logic lives here as a new function.
- `workflows/design/pg_design_spec.json` — read `lint_config` to find or add the blocking-rule list (see §4 acceptance §1).
- `panda_ledger/shared/contracts.py` (FROZEN) — `Severity`, `Violation` dataclasses.

Read all three rule modules + `pg_dispatch_lint.py`'s existing `lint_widget_inventory` end-to-end before starting. R23's pattern is the model R29 follows; R23 the rule module is ~10 lines, the heavy lifting lives in `pg_dispatch_lint.py`'s `--strict` JSON output.

---

## §2 — Scope (files to create/modify)

### 2.1 — Build these files

**New file:** `pg_design_lint/rules/R29_mockup_annotations.py`

Mirror R23's structure:
- Rule class subclassing `pg_design_lint.rules.base.Rule`
- `rule_id = "R29"`, `severity = Severity.ERROR`, `title = "Mockup annotation completeness in dispatch"`, `spec_ref = "Inviolable Rule #23 + §3.7"`
- `applies_to(source)`: dispatch markdown only, same scope as R23 (`source.path.suffix == ".md"` and `"workflows/cc_mailbox/" in source.rel.replace("\\", "/")`)
- `check_file(context, source)`: shells out to `workflows/tools/pg_dispatch_lint.py --json --strict <path>`, parses findings, returns Violation objects for findings with `code` starting with `MOCKUP_ANNOTATION`

**Modify:** `workflows/tools/pg_dispatch_lint.py`

Add new function `check_mockup_annotation_completeness(fm: dict, body: str, dispatch_path: Path, repo_root: Path) -> list[Finding]`:

1. Read `related_mockups:` from frontmatter. If empty → return `[]` (skip — no mockups to validate against).
2. Read `related_widgets:` from frontmatter. If absent → return one Finding with `code="MOCKUP_ANNOTATION_NO_WIDGETS"` warning ("dispatch cites mockups but no `related_widgets:` block; cannot validate annotations"). Don't block — warn.
3. Read `related_decisions:` from frontmatter. Default to `[]` if absent (will likely produce findings).
4. For each mockup path in `related_mockups`:
   a. Resolve relative to `repo_root` (mockup paths in dispatches are repo-relative).
   b. If file doesn't exist → Finding `code="MOCKUP_ANNOTATION_MOCKUP_NOT_FOUND"` error.
   c. Parse the HTML using stdlib `html.parser.HTMLParser`.
   d. For each `related_widgets` entry that scopes into this mockup (entry format: `"path/to/mockup.html#widget_id"` or `"path/to/mockup.html"` for whole-file scope):
      - Walk the subtree under that widget (or whole document if no `#fragment`)
      - Collect every `data-decision` attribute value (comma-split if multiple per element)
   e. Diff collected annotations against `related_decisions:` list. Each missing annotation → Finding `code="MOCKUP_ANNOTATION_MISSING"` error: `"mockup widget '{widget_id}' annotated with '{decision_id}' but '{decision_id}' not in related_decisions:"`.
5. Resolve any `proposed:<slug>` annotations against `workflows/decisions/staging/proposed_*.md` files. If a proposed slug doesn't exist as a staging file → Finding `code="MOCKUP_ANNOTATION_PROPOSED_NOT_FOUND"` warning.
6. Return all findings.

Hook into the main `lint_file()` orchestrator: after `lint_widget_inventory()` and before the final `LintResult` is assembled, call `check_mockup_annotation_completeness()` and extend `findings`.

**Add CLI flag:** `pg_design_lint --check-mockup-annotations <path>`

In `pg_design_lint/__main__.py`, add a new flag that:
- Takes a path (mockup HTML file OR a dispatch markdown file).
- If a mockup HTML: parse, list every `data-decision` attribute. Resolve each against `workflows/decisions/` (and `staging/`). Print one line per annotation: `<widget_id>  <decision_id>  <status>`. Status is "found" (decision file exists), "proposed" (staging file exists), "MISSING" (neither). Exit 1 if any MISSING.
- If a dispatch markdown: equivalent to running the dispatch through `pg_dispatch_lint.py` but filtered to only `MOCKUP_ANNOTATION*` codes. Exit 1 if any error finding.
- Heuristic to distinguish: file extension. `.html` → mockup mode, `.md` → dispatch mode.

This is the standalone validator authors run before committing a mockup edit.

### 2.2 — Tests

**New file:** `pg_design_lint/tests/test_R29_mockup_annotations.py` (or extend `tests/test_pg_dispatch_lint.py` if Codex prefers — pick whichever fits the existing test layout best).

Cover these cases:

| Case | Setup | Expected |
|---|---|---|
| Complete annotations | Mockup with 3 `data-decision` attrs, dispatch's `related_decisions:` lists all 3 | 0 findings |
| Missing one annotation | Mockup with 3 attrs, dispatch lists 2 | 1 error: `MOCKUP_ANNOTATION_MISSING` |
| Unknown decision ID | Mockup attr `DECISION_9999` (non-existent file) | 1 warning: `MOCKUP_ANNOTATION_DECISION_NOT_FOUND` |
| Proposed slug present | Mockup attr `proposed:foo`, staging file `proposed_foo_<ts>.md` exists | 0 findings |
| Proposed slug absent | Mockup attr `proposed:foo`, no staging file | 1 warning: `MOCKUP_ANNOTATION_PROPOSED_NOT_FOUND` |
| No mockups cited | Dispatch with empty `related_mockups:` | 0 findings (skip) |
| Mockups but no widgets | Dispatch with `related_mockups:` but no `related_widgets:` | 1 warning: `MOCKUP_ANNOTATION_NO_WIDGETS` |
| Mockup file missing | Dispatch cites `path/to/missing.html` | 1 error: `MOCKUP_ANNOTATION_MOCKUP_NOT_FOUND` |
| Multi-decision attribute | Element with `data-decision="DECISION_0001,DECISION_0002"`, dispatch lists both | 0 findings |
| Multi-decision attr partial | Element with `data-decision="DECISION_0001,DECISION_0002"`, dispatch lists only first | 1 error |
| Widget fragment scope | `related_widgets: ["foo.html#header"]`, only walk `<div id="header">` subtree | only finds annotations under `#header` |

Test fixtures live in `pg_design_lint/tests/fixtures/R29/` with subdirectories per case. Each fixture is a minimal mockup HTML + matching dispatch markdown.

### 2.3 — DO NOT touch

- `panda_ledger/shared/contracts.py` — FROZEN. Import from it.
- Any existing rule module (R01-R28, R03b). R29 is purely additive.
- `pg_dispatch_lint.py` outside the new function and the orchestrator hook. Don't refactor existing logic.
- `panda_ledger/` — Phase 2 / 3 / 4 territory.

---

## §3 — Build order

1. **Read R23 + R22 + base.py end-to-end first.** R29 mirrors R23's pattern.
2. Read spec §3.7 (mockup annotation conventions) and §4.3 R29 row in `PG_DESIGN_LEDGER_SPEC_v2.3.md`.
3. Implement `check_mockup_annotation_completeness()` in `pg_dispatch_lint.py`. Hook into orchestrator.
4. Implement `R29_mockup_annotations.py` rule module. Mirror R23's subprocess+parse-findings pattern.
5. Add `--check-mockup-annotations <path>` flag to `pg_design_lint/__main__.py`.
6. Build fixtures + tests.
7. Run full pytest suite (438+ tests should still pass; new R29 tests should be added).
8. Run dispatch-corpus check: `python -m pg_design_lint --rule R29 workflows/cc_mailbox/` and the equivalent against `C:\CODEX PG\CODEX Claude Codex Mailbox\`. Expect zero R29 blocking findings on dispatches authored before this rule ships (per §6 grandfathering).

---

## §4 — Acceptance criteria

R29 dispatch is acceptance-passing when:

1. **Phase A blocking.** `pg_design_spec.json.lint_config` gains (or already has) a `phase_a_blocking_rules` array. Add `"R29"` to it. Confirm the pre-commit lint run with `--strict --severity-floor=warning` blocks dispatches with R29 errors.
2. **Standalone CLI works.** `python -m pg_design_lint --check-mockup-annotations workflows/design/pg_general_mockups/<example>.html` lists annotations and resolves each.
3. **All test cases pass.** Eleven+ cases above covered.
4. **Existing test suite still passes.** No regressions in the 438 existing tests (438 passed + 1 skipped at v4.71.1).
5. **No new dependencies added.** Stdlib only.
6. **No false positives on existing dispatch corpus.** Run R29 against every `.md` file under `workflows/cc_mailbox/CC Inbox/`, `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\`, and the matching CLAUDE Inbox / CODEX Sent paths. Expect zero blocking findings (existing dispatches are grandfathered per §6 if their cited mockups have zero `data-decision` attributes; otherwise they should pass cleanly).
7. **Spec freshness check unchanged.** R21 still passes.

---

## §5 — Out of scope

These are explicitly NOT R29's job:

- **U3 hook (`pre-commit-decision-sync.py`).** Separate Phase 4 dispatch (pre-staged in this same inbox folder; gated on U1 R29 ship).
- **U5 telemetry (`--update-telemetry`, `--promote-eligible`).** Separate Phase 4 dispatch (pre-staged in this same inbox folder; gated on U1 R29 ship).
- **Backfilling annotations on existing mockups.** Per spec §3.7 backfill policy: "Pre-existing mockups can be annotated lazily, file by file, when the next dispatch references them." R29 does NOT enforce annotations on mockups not cited by the current dispatch.
- **Validating Verify's checklist generation.** Verify reads annotations at runtime via the v2.3 §6.3.1 logic; that's a Ledger-app concern (CC's territory), not a lint concern.
- **Auto-fixing missing annotations.** R29 reports; it does not insert `data-decision` attributes into mockup HTML.

---

## §6 — Backfill policy (per spec §3.7)

R29 applies prospectively: only to dispatches authored after this rule ships. Pre-existing dispatches in `workflows/cc_mailbox/CC Inbox/` and `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\` that cite mockups without `data-decision` annotations are grandfathered.

Mechanism: R29 only fires on a dispatch when at least one of the cited mockups already has any `data-decision` attribute (check via parse). If a cited mockup has no annotations at all, R29 emits a `MOCKUP_ANNOTATION_GRANDFATHERED` info finding (visible in `--exemption-report`) and does not block.

This grandfathering is a single-pass check — once any annotation appears on a mockup, R29 enforces full completeness on that mockup going forward. (One-half-pregnant prevention.)

Codex: implement this gate in `check_mockup_annotation_completeness()`. Mockup HTML scan happens before the diff pass; if zero `data-decision` attributes are found in any cited mockup, return `[Finding(severity="info", code="MOCKUP_ANNOTATION_GRANDFATHERED", message=...)]` and skip the diff.

---

## §7 — Coordination with Phase 2 (now SHIPPED)

Phase 2 shipped at v4.71 / `091644b`. Capture pre-fill from `data-decision` annotations (per §3.7 Mode B) is in `panda_ledger/capture/`. R29 enforces what Capture pre-fills.

**Step 0 verification required.** As Codex's Step 0 first action (before any code written for R29), read the post-Phase-2 implementation of `data-decision` parsing in `panda_ledger/capture/` (Codex: locate via `grep -r data-decision panda_ledger/`). Confirm the encoding used. Spec §3.7 specifies:

> Multi-decision widgets carry comma-separated IDs: `data-decision="DECISION_0023,DECISION_0024"`.

If Phase 2 implemented a different encoding (JSON array, space-separated, etc.), surface in Step 0 before writing R29's parser. Either Phase 2 amends to match spec, or R29's parser handles whatever Phase 2 actually shipped — that decision is Darrin's, surfaced via Codex Step 0 finding.

---

## §8 — Delivery format

Standard impl report to `cc_mailbox/CLAUDE Inbox/` with:
- File-by-file summary (LOC, notes)
- Test results (full pytest including the new R29 tests)
- Acceptance criteria walkthrough (each item PASS/FAIL/NOTES)
- Sample output of `python -m pg_design_lint --check-mockup-annotations` on at least one real mockup
- Any open issues or contract concerns surfaced during build
- Working tree state at impl-complete (uncommitted; awaits Darrin commit-go)

---

## §9 — Estimated time

~2 hours Codex time (High tier). LOC budget ~150-200 src + ~120 tests = ~270-320 LOC total.

Build sequence per §3 above. No daylight pressure — Phase 2 is shipped, and U3/U5 are pre-staged behind this. Ship at v4.72.

---

## §10 — What this closes

R29 is the rule that, had it existed at A48 dispatch time, would have caught the missing `✦ Triage with AI` button before it shipped. The annotation `data-decision="DECISION_<triage-cta>"` on the mockup would have been required to appear in the dispatch's `related_decisions:` list; missing → block.

That single check, applied uniformly across every UI dispatch from now on, closes the A48-class implicit-decision-in-layout drift gap. This is the most leveraged single rule in the entire Ledger system.

---

## §11 — Begin trigger

**Triggered.** Phase 2 shipped (commit `091644b` v4.71, plus follow-up `05eb269` v4.71.1 for Bug #142 pytest fixture). Darrin gave the go via CD on 2026-04-29 19:45 PDT. Begin per §3 build order.

-- Claude Desktop, 2026-04-29 19:45
