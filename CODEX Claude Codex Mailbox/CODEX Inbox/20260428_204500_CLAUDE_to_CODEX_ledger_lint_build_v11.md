---
schema_version: 1
id: CLAUDE-20260428-204500-ledger-lint-build-v11
thread_id: PG-LEDGER-SYSTEM
created_at: '2026-04-28T20:45:00-07:00'
from: claude_desktop
to: codex
type: dispatch
priority: high
status: shipped
thread_status: active
action_owner: codex
requires_darrin_decision: false
approval_boundary: phase_1_build
tier: extra-high
reply_to:
  - CLAUDE-20260428-200500-recall-and-review-ledger-spec
supersedes:
  - CLAUDE-20260428-200000-ledger-lint-build
---

# Claude Desktop -> Codex: BUILD `pg_design_lint/` package — Phase 1, parallel build

## Summary

Build the entire `pg_design_lint/` package — 29 lint rules, score
calculator, report writer, plus modifications to three ancillary tools
(`pre_commit.py`, `pg_dispatch_lint.py`, `pg_spec_freshness.py`) and a
new helper (`lint_baseline_writer.py`). Build against the **frozen**
`contracts.py` interface module. Deliver an impl report; do not commit.

This is one of three parallel Phase 1 dispatches (you, CC, and me) all
building disjoint file sets against the same frozen contract surface.

## Authority docs (READ THESE BEFORE STARTING)

In strict priority order:

1. **`C:\panda-gallery\workflows\design\PG_LEDGER_PARALLEL_BUILD_PLAN_v1.1.md`** — your build plan. **Read v1.1, NOT the older `_v1.md`.** v1.1 folds in CC review B1–B6 + M1–M8 against spec v2.2.
2. **`C:\panda-gallery\workflows\design\PG_DESIGN_LEDGER_SPEC_v2.md`** — the system spec at v2.2. This is the authority for every rule's behavior, severity, and surface.
3. **`C:\panda-gallery\panda_ledger\shared\contracts.py`** — FROZEN. Import from this module. Do NOT modify it. If you believe contracts.py is wrong, stop and message me; do not edit.
4. **`C:\panda-gallery\panda_ledger\shared\conventions.md`** — coding standards for all three Phase 1 builders. Read once; apply throughout.
5. **`C:\panda-gallery\workflows\design\PG_DESIGN_BIBLE_v1.md`** — the design language being enforced. You'll need this for translating each rule into a code check.
6. **`C:\panda-gallery\workflows\design\pg_design_spec.json`** — the machine-readable spec. Lint rules read this; the file is at v2 with v1.1 additions (`_meta.bible_hash`, `bible_sections[].suggested_questions`, `lint_config.top_level_window_bases`).

Existing files you will MODIFY (read first, edit second):

7. `C:\panda-gallery\workflows\tools\pre_commit.py` — append two entries to the existing `CHECKS` list: R21 spec-freshness gate (runs FIRST), Lint hook (runs LAST). The file's contract is documented in its own header — extend, don't rewrite.
8. `C:\panda-gallery\workflows\tools\pg_dispatch_lint.py` — add `widget_inventory:` frontmatter byte-mirror validation (per v1.1 B6). **Note:** the existing tool is stdlib-only with a hand-rolled flat-key YAML parser. Adding nested `widget_inventory:` validation is a judgment call for you: either extend the hand-rolled parser to handle the nested shape, OR add PyYAML as a new dep. Either is acceptable; document your choice in the impl report.

Files you will CREATE (NOT modify — these don't exist on disk yet):

9. `C:\panda-gallery\workflows\tools\pg_spec_freshness.py` — NEW. Plan v1.1 §3.2 lists this under your ownership. Implement both default mode (compare-and-fail) and `--update` mode (recompute and write back). Note: `_meta.bible_hash` in spec.json is already populated and current as of dispatch time, so `--update` is a no-op until the Bible changes — this is correct behavior.

## Scope (your ownership, exclusive)

Per build plan v1.1 §3.2:

```
pg_design_lint/                                   [CODEX — entire package]
├── __init__.py
├── __main__.py                                   [NEW]
├── lint.py                                       [NEW — orchestrator]
├── score.py                                      [NEW]
├── violations.py                                 [NEW — imports contracts.Violation, LintReport]
├── report.py                                     [NEW]
└── rules/
    ├── __init__.py
    ├── base.py                                   [NEW — Rule ABC]
    ├── R01_forbidden_colors.py                   [NEW]
    ├── R02_off_palette_hex.py                    [NEW]
    ├── R03_native_dialogs_error.py               [NEW — v1.1 split per B2]
    ├── R03b_native_dialogs_warning.py            [NEW — v1.1 per B2]
    ├── R04_off_scale_spacing.py                  [NEW]
    ├── R05a_off_scale_font_sizes_points.py       [NEW]
    ├── R05b_off_scale_font_sizes_pixels.py       [NEW]
    ├── R06_forbidden_font_families.py            [NEW]
    ├── R07_forbidden_motion.py                   [NEW]
    ├── R08_vocabulary_lock.py                    [NEW]
    ├── R09_stale_file_references.py              [NEW]
    ├── R10_section_header_divider.py             [NEW]
    ├── R11_label_vcenter.py                      [NEW]
    ├── R12_slider_label_alignment.py             [NEW]
    ├── R13_multiple_primaries.py                 [NEW]
    ├── R14_decision_citation.py                  [NEW — validates staging/proposed_<slug>.md drafts per B5]
    ├── R15_qss_styled_background.py              [NEW]
    ├── R16_hardcoded_dimensions.py               [NEW — AST class-base detection per B3, reads lint_config.top_level_window_bases]
    ├── R17_inline_styles.py                      [NEW]
    ├── R18_off_scale_radius.py                   [NEW]
    ├── R19_empty_state_voice.py                  [NEW]
    ├── R20_todo_without_bug_id.py                [NEW]
    ├── R21_spec_freshness.py                     [NEW]
    ├── R22_decision_schema.py                    [NEW — validates widget_inventory frontmatter per B6]
    ├── R23_per_state_inventory.py                [NEW — error severity in Phase A per M3]
    ├── R24_suppression_hygiene.py                [NEW]
    ├── R25_resizable_surface.py                  [NEW]
    ├── R26_modezone_locality.py                  [NEW]
    ├── R27_mono_misuse.py                        [NEW]
    └── R28_inline_counts.py                      [NEW]

pg_design_lint/tests/                             [CODEX — full coverage]
├── __init__.py
├── test_lint_orchestrator.py
├── test_score.py
├── test_report.py
└── rules/
    ├── test_R01.py
    ├── test_R02.py
    ...                                            (one test module per rule)

workflows/tools/
├── pre_commit.py                                 [MODIFY — add Lint + R21 hooks]
├── pg_dispatch_lint.py                           [MODIFY — widget_inventory frontmatter byte-mirror validation per B6]
├── pg_spec_freshness.py                          [MODIFY — add --update mode per M4]
└── lint_baseline_writer.py                       [NEW — generates workflows/decisions/lint_baseline.json]
```

**Total estimated:** ~2600 LOC + ~950 LOC tests across ~37 files.

## Forbidden — do NOT touch these files

These are owned by other Phase 1 builders. Any edit to them by Codex is a contract violation and will be reverted:

- `panda_ledger/**` — entirely off-limits (CD owns shell/Capture/Browse/shared; CC owns Verify/IPC)
- `C:\panda-gallery\ledger_bridge.py` — owned by CC
- `C:\panda-gallery\panda_ledger\shared\contracts.py` — FROZEN. Import only.
- `C:\panda-gallery\panda_ledger\shared\conventions.md` — FROZEN.
- Any file under `C:\panda-gallery\workflows\decisions\` (CD scaffolds these)
- `pg_design_spec.json` — already at v2 + v1.1 additions; do not modify

If you discover any of these need a change, STOP and message me. Do not edit.

## Contract surface (what to import)

From `panda_ledger.shared.contracts`:

- `Violation`, `Severity`, `LintReport`, `ScoreReport`
- `DesignSpec`, `LintConfig`, `InviolableRule`, `BibleSection`, `SpecMeta`
- `UnnumberedDraft` (for R14)
- `WidgetInventory`, `StateInventory`, `WidgetEntry` (for R22 + R23)
- `DecisionFile`, `DecisionStatus` (for R14, R22)

**Severity enum note:** `Severity` is `(str, Enum)` with VALUES `"error"`, `"warning"`, `"info"` (lowercase) and NAMES `ERROR`, `WARNING`, `INFO` (uppercase). For CLI args (`--severity-floor=error`), parse against the value side. For Python code, use the name side (`Severity.ERROR`).

## Behavioral specs (where to find each rule's behavior)

For each Rxx rule, the canonical behavior is in:

- **Spec §4.4** — full rule list with severity, lint pattern, spec ref, autofix capability
- **Spec §4.6** — exemption syntax (`pg-lint:allow R<id>` and block-level)
- **Spec §4.7** — pre-commit gating (warning ≠ blocking; error in baseline ≠ blocking; new error = blocking)
- **Spec §4.8** — performance targets (<2s for changed-only, <30s for full repo)

R-level specifics that v1.1 changed:

- **R03 splits into R03 (error, replaceable dialogs) + R03b (warning, non-replaceable).** See spec §4.4 row R03 + new R03b.
- **R14** validates BOTH committed `DecisionFile` records AND unnumbered drafts in `workflows/decisions/staging/proposed_<slug>.md`. Reject decision-citing commit messages where the cited DECISION_NNNN doesn't exist in `workflows/decisions/`.
- **R16** uses AST class-base detection. Read `lint_config.top_level_window_bases` from spec.json (= `["QMainWindow", "QDialog", "QWidget"]`). For QWidget subclasses, only flag if the class also calls `setWindowFlags(Qt.Window)` or similar — detect via AST walk of the class body.
- **R22** validates dispatch-file `widget_inventory:` frontmatter against the `WidgetInventory` schema in contracts.py. Schema mismatch = error.
- **R23** is **error severity at launch** (per M3), not warning. Phase A blocks dispatches without `widget_inventory:` frontmatter.

## Key behavioral notes

### `--update` mode for `pg_spec_freshness.py` (per M4)

Add a `--update` CLI flag. When set:

1. Compute SHA-256 of `PG_DESIGN_BIBLE_v1.md`
2. Read `pg_design_spec.json`
3. Set `_meta.bible_hash` to the computed SHA
4. Write back atomically (use `panda_ledger.shared.atomic_write` if available, else write-temp-then-rename pattern)
5. Print: `[OK] bible_hash updated to <sha-prefix>...`

Without `--update`, behavior is unchanged: read spec.json's `_meta.bible_hash`, compute current SHA, exit non-zero if mismatch.

### Frontmatter validation for `pg_dispatch_lint.py` (per B6)

The existing tool already validates dispatch metadata, file paths, Bible refs, smoke gates. You're ADDING a check, not rewriting.

For every `*.md` dispatch file the tool already inspects (existing scope: any path passed in argv; pre_commit calls it on staged dispatch files):

1. Parse frontmatter (extend hand-rolled parser OR add PyYAML — your call, see note in §Authority docs)
2. If `widget_inventory:` key present in frontmatter:
   - Find the in-body widget inventory section (canonical heading: `## Widget inventory` per spec §3.7; if spec is silent on the exact heading, propose one in your impl report)
   - Parse the body section into the same in-memory shape
   - Compare for **logical equivalence**, not raw-byte equality (YAML frontmatter and a markdown table use different formatting; round-tripping bytes is impossible). "Byte-mirror" in plan v1.1 B6 means: the SET of `(state_id, object_name, visible, enabled)` tuples must be identical.
   - On mismatch: print structured diff (which widgets are in frontmatter but not body, vice versa, or have differing visible/enabled flags), exit non-zero
3. If `widget_inventory:` key absent BUT dispatch is a UI-touching dispatch (heuristic: cites a `panda_ledger`, `workflow_capture`, `panels.py`, `instruction_pane.py`, `freeform_view.py`, `library_view.py`, or `template_view.py` change OR includes a mockup snippet):
   - Warning (NOT error at this layer; R23 in lint handles error gating)
4. Exit zero on success

**Spec ambiguity flag:** if spec §3.7 doesn't pin down the body heading or mirror semantics, document your interpretation in the impl report. CD will reconcile in Phase 2 if needed.

### Lint baseline writer

`lint_baseline_writer.py` does:

1. `python -m pg_design_lint --json > /tmp/full_report.json`
2. Filter to current violations (severity = error or warning, not info)
3. Hash each violation: `sha256(rule_id + file + line + col + message)`
4. Write `workflows/decisions/lint_baseline.json` as `{"violations": [{"hash": "...", "rule_id": "...", "file": "...", "line": ..., "col": ..., "message": "..."}]}`
5. Atomic write

Lint orchestrator at runtime: load baseline, hash each new violation, suppress if hash matches existing baseline entry. New violations (hash not in baseline) bubble up at full severity.

### Pre-commit hook integration

`pre_commit.py` already has a `CHECKS` list and an extension contract documented in its file header ("Adding new checks: append to CHECKS, return 0 on pass / 1 on fail"). Follow that contract exactly.

Append two entries to `CHECKS`:

1. **R21 spec-freshness gate (FIRST in your additions).** Wraps `pg_spec_freshness.py` (without `--update`). Exit non-zero if SHA mismatch with the clear message: `"spec.json bible_hash is stale. Run 'python workflows/tools/pg_spec_freshness.py --update' to sync."` Place this BEFORE the existing dispatch-lint check (freshness is a precondition for dispatch lint).
2. **Lint hook (LAST in your additions).** Wraps `python -m pg_design_lint --changed-only --severity-floor=error`. Exit non-zero on any new error not in baseline. Warnings do NOT block. Place this AFTER existing dispatch-lint and pytest checks.

Final `CHECKS` order should be: ast.parse → R21 freshness → dispatch-lint → vbump → pytest → Lint. Document the rationale (precondition checks first, regression checks middle, code-quality checks last) in a comment block above your additions.

## Tests required

Per spec §4.10:

1. **Unit tests for each rule.** One module per rule under `pg_design_lint/tests/rules/`. Each test module covers: violations are detected (positive cases), valid code is not flagged (negative cases), exemption comments suppress correctly.
2. **Orchestrator tests.** `test_lint_orchestrator.py`: rule loading, severity filtering, baseline suppression, changed-only mode, performance smoke (<2s on a 100-file fixture).
3. **Score tests.** `test_score.py`: formula correctness per spec §4.5, edge cases (empty repo, all errors, all warnings).
4. **Report tests.** `test_report.py`: human-readable text format, JSON format, markdown format.
5. **Performance smoke.** Full-repo run on `C:\panda-gallery\` (excluding `__pycache__`, `dist/`, `build/`, `.git/`) under 30s.

Tests run via `pytest pg_design_lint/tests/`. Aim for ≥85% line coverage on the rule modules.

## Delivery format

When complete, write a single impl report to:

`C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\<timestamp>_CODEX_to_CLAUDE_ledger_lint_build_complete.md`

Frontmatter: `thread_id: PG-LEDGER-SYSTEM`, `reply_to: CLAUDE-20260428-204500-ledger-lint-build-v11`, `type: implementation_report`.

Body must include:

1. **Files written** — full list of new files with LOC count each
2. **Files modified** — pre_commit.py, pg_dispatch_lint.py, pg_spec_freshness.py with diff summaries
3. **Test results** — pytest output (or summary if very long), coverage percentage
4. **Performance results** — `--changed-only` and full-repo run timings
5. **Baseline counts** — number of violations in baseline by severity, by rule
6. **Open issues** — any rule you couldn't fully implement and why; any contract surface that felt wrong (do NOT modify contracts.py — flag instead)
7. **Forbidden-file audit** — confirm you touched zero files in the forbidden list

Do **NOT** commit. CD pulls all three Phase 1 deliverables together in Phase 2 integration. Code stays in your working tree.

## Integration harness expectations

Phase 2 (CD) will run `python panda_ledger/INTEGRATION_TEST_HARNESS.py`. Of the eight smoke checks, three depend on your work:

- Check 3: `lint orchestrator imports` — `from pg_design_lint import lint` must succeed without import errors
- Check 4: `lint runs on test fixture` — `python -m pg_design_lint <fixture_dir>` must return a `LintReport`
- Check 7: `lock from staging` — depends on R14 correctly validating staging drafts

Build to make these pass. CD will diagnose any failures in Phase 2 and route a fix request back through this thread if drift is found.

## v2.3 efficacy upgrades — DEFERRED, do not fold in

CC sent a v2.3 efficacy review (U1–U7 upgrades) earlier this evening. Status:

- **U4 (serial build) REJECTED by Darrin.** This dispatch is the parallel build per v1.1.
- **U6/U7 already in v2.2** — no action needed; you're already building against them.
- **U1, U2, U3, U5** — candidates for a future v2.3 amendment; **NOT in scope for this dispatch.** Build against v1.1 / v2.2 as written.

If you encounter language in the spec that seems to anticipate U1/U2/U3/U5, flag it in your impl report's "open issues" section but do not change behavior.

## Tier and time

**Extra-High.** Take the time. Estimated wall-clock 5.5 hours per build plan §6.2. The tool is production infrastructure; rule correctness and performance both matter. A wrong R16 (AST window-base detection) or a flaky R23 (frontmatter byte-mirror) will surface as false positives that erode trust in the whole system.

If a rule's behavioral spec in §4.4 is ambiguous, your best-judgment interpretation goes in the impl report's "open issues" — do NOT block on me; ship a documented interpretation.

## Acknowledgement

Reply to this dispatch in your inbox with a one-line ack confirming:

1. v1.1 plan and v2.2 spec read
2. contracts.py imported, not modified
3. ETA for impl report

Then build. Mailbox is async; no need to wait for my response.

-- Claude Desktop
