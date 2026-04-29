---
schema_version: 1
id: CLAUDE-DESKTOP-20260429-PHASE4-U5-DISPATCH-DRAFT
thread_id: PG-LEDGER-PHASE4-U5
created_at: '2026-04-29T10:30:00-07:00'
from: claude_desktop
to: codex
type: dispatch
priority: normal
status: drafted_pending_phase2_ship
thread_status: draft
action_owner: claude_desktop
requires_darrin_decision: true
approval_boundary: dispatch_after_phase2_ship
reply_to: []
tier: high
target_version: v4.74_or_later
prerequisite_commit: phase2_ship_and_u1_r29_ship
---

# Claude Desktop -> Codex: Phase 4 — U5 per-rule auto-promotion based on telemetry

**STATUS: DRAFT.** Pre-staged in CODEX Inbox while CC's Phase 2 build is in flight. Do NOT begin work until Darrin sends the explicit go AND Phase 2 has shipped (v4.71+) AND U1 R29 has shipped (v4.72+). U5 ships at v4.74 or later (after U3 v4.73, OR concurrent with U3 if Darrin parallelizes — both are Codex-owned, no overlap).

---

## TL;DR

Implement U5 — per-rule auto-promotion based on telemetry data, replacing v2.2's calendar-based "one month of clean Phase A runs before promoting more rules" gate. Adds **four** new CLI flags: `--update-telemetry`, `--promote-eligible`, `--promote R<id>`, `--demote R<id>`.

**Telemetry mechanism:** each rule has two counters in `pg_design_spec.json.lint_config.rule_telemetry[<rule_id>]`:
- `exemption_count: int` — number of `pg-lint:allow R<id>` comments active in codebase
- `last_promotion_at: ISO timestamp` — when the rule last changed severity

A rule becomes **promotion-eligible** when both:
1. Currently `severity=warning` (not already an error)
2. `exemption_count` has been stable for 2 consecutive telemetry updates (≥2 weeks if updated weekly)

**Promotion is opt-in.** Eligible rules surface via `--promote-eligible`. Darrin runs `--promote R<id>` to actually promote. Demotion is manual: `--demote R<id>`.

**Five-piece ship:**
1. Modify `pg_design_lint/__main__.py` — add the four new CLI flags (mutually exclusive with each other and with lint-run flags).
2. New module `pg_design_lint/telemetry.py` — telemetry computation + read/write helpers.
3. Modify each rule module under `pg_design_lint/rules/R*.py` — change `severity` from a class constant to a runtime lookup against spec.json. (Or per §3.4 design choice; recommend Option C runtime lookup.)
4. Modify `pg_design_spec.json` — verify and possibly extend `lint_config.rule_telemetry` block (already in v1.3 per amendment §S4 — see §2.1 verification step).
5. Tests covering: telemetry update from clean codebase, telemetry update with new exemptions, eligibility computation with stable counter, eligibility computation with growing counter, promote happy path, promote when ineligible (refuse), demote happy path, 5 more cases per §2.2.

**Estimated effort:** ~200-280 LOC source + ~150 LOC tests. ~2 hours Codex time.

**No new dependencies.** Stdlib + reuse PyYAML/ruamel decision from U3 (if U3 ships first). Else stdlib JSON only — telemetry lives in spec.json, which is already JSON.

---

## §1 — Authority

Spec: `workflows/design/PG_DESIGN_LEDGER_SPEC_v2.3.md` §4.4 (severity scale and exit codes — author/reviewer gate split, already shipped), §4.6 (CLI flags), §10.2 (Phase 1 phased rollout — per-rule auto-promotion).

Companion files:
- `pg_design_lint/__main__.py` — CLI entry; new flags hook here.
- `pg_design_lint/rules/base.py` — `Rule` base class; `severity` constant pattern.
- `pg_design_lint/rules/R*.py` — every rule module; one severity constant each.
- `workflows/design/pg_design_spec.json` v1.3 — has `lint_config.rule_telemetry` block per amendment §S4. Verify the shape matches what U5 expects (might already be live, might need tweaking).

Read those files end-to-end. Telemetry is a fast feature to mis-implement — get the read/write semantics right and the rest follows.

---

## §2 — Scope (files to create/modify)

### 2.1 — Build these files

**Modify:** `pg_design_lint/__main__.py`

Add four new CLI flags:

```
--update-telemetry          recompute exemption_count for every rule, write to spec.json
--promote-eligible          list rules ready for promotion (current severity=warning, stable 2 weeks)
--promote R<id>             promote specified rule from warning to error (and update spec.json + rule module)
--demote R<id>              demote specified rule from error to warning (manual rollback path)
```

Each flag is mutually exclusive with the others (and with the existing lint-run flags). They're admin operations, not lint runs.

**New file:** `pg_design_lint/telemetry.py`

Module containing:

```python
def update_telemetry(repo_root: Path, spec_path: Path) -> dict:
    """Scan codebase for pg-lint:allow R<id> comments. Update exemption_count
    for every rule in spec.json. Return dict of rule_id -> new count.
    """

def promotion_eligible_rules(spec_path: Path) -> list[str]:
    """Return list of rule IDs that are currently severity=warning AND have
    had stable exemption_count for >=2 telemetry updates.
    """

def promote_rule(rule_id: str, repo_root: Path, spec_path: Path) -> None:
    """Promote a rule from warning to error. Update spec.json telemetry +
    update rule module's severity constant. Refuse if ineligible.
    """

def demote_rule(rule_id: str, repo_root: Path, spec_path: Path) -> None:
    """Demote a rule from error to warning. Always allowed.
    """

def read_telemetry(spec_path: Path) -> dict:
    """Read lint_config.rule_telemetry from spec.json. Return as dict."""

def write_telemetry(spec_path: Path, telemetry: dict) -> None:
    """Write lint_config.rule_telemetry to spec.json atomically."""
```

Implementation notes:
- `update_telemetry` walks all `.py` and `.md` files in the repo (use `pg_design_lint/rules/base.py:discover_files()` if it's reusable; else replicate pattern). For each file, count occurrences of `pg-lint:allow R<id>` and `pg-lint:allow-block R<id>`. Sum per rule. Write count + ISO timestamp to spec.json.
- Stability check: requires telemetry history. Suggest adding an `exemption_history: list[dict]` with last N entries, where each entry is `{at: ISO_ts, count: int}`. Stable means: last 2+ entries have same count, and span ≥2 weeks. (Codex: pick the structure that's easiest to maintain. The simpler the better. If you'd prefer a flat `last_two_counts: [int, int]` field, that works too — surface in Step 0.)
- `promote_rule` modifies the rule module file in place: replaces `severity = Severity.WARNING` with `severity = Severity.ERROR` (preserving formatting). Use `ast` parsing or regex carefully. Spec.json gets `last_promotion_at: <ISO_ts>` updated.
- `demote_rule` is the inverse, always allowed (no eligibility gate).

**Modify:** `pg_design_lint/rules/R*.py` — design choice in §3.4 below.

**Modify:** `workflows/design/pg_design_spec.json` v1.3 → v1.4 (additive bump if shape changes; if existing shape from §S4 already works, no version bump).

Verify the existing `lint_config.rule_telemetry` block. Per spec v2.3 §2.3:

> `lint_config.rule_telemetry[<rule_id>]` — per-rule false-positive tracking, shape `{exemption_count: int, last_promotion_at: ISO timestamp}`. Used by U5 per-rule auto-promotion eligibility check.

If the existing shape doesn't include exemption history, extend it. Codex: surface the shape decision in Step 0 before extending — Darrin should approve schema changes to spec.json.

### 2.2 — Tests

**New file:** `pg_design_lint/tests/test_telemetry.py`.

Cover these cases:

| Case | Setup | Expected |
|---|---|---|
| Update telemetry: clean | Codebase with no `pg-lint:allow` comments | All rules have `exemption_count: 0` |
| Update telemetry: with exemptions | Codebase with 3x `pg-lint:allow R02` and 1x `pg-lint:allow R16` | R02: 3, R16: 1, others: 0 |
| Update telemetry: block exemptions counted | Codebase with `pg-lint:allow-block R04` and `pg-lint:end-allow-block` | R04: 1 (block counts as one exemption, not per-line) |
| Eligibility: stable 2 weeks | Telemetry history: 2 entries with same count, ≥14 days apart | Rule eligible |
| Eligibility: stable 1 week | Telemetry history: 2 entries with same count, ~7 days apart | Rule NOT eligible (need 2 weeks) |
| Eligibility: unstable | Telemetry history: 2 entries with different counts | Rule NOT eligible |
| Eligibility: already error | Rule severity=error | Rule NOT eligible (already promoted) |
| Promote happy path | Eligible warning rule | Rule module updated to ERROR, spec.json updated, last_promotion_at written |
| Promote ineligible | Rule that doesn't meet stability gate | Refuses with clear error message; nothing modified |
| Promote already-error | Rule already at error | Refuses; nothing modified |
| Demote happy path | Error rule | Rule module updated to WARNING, spec.json updated |
| Demote of warning | Rule already at warning | Refuses; nothing modified |

Test fixtures live in `pg_design_lint/tests/fixtures/telemetry/`. Use temp directories with synthetic spec.json + rule modules.

### 2.3 — DO NOT touch

- `panda_ledger/shared/contracts.py` — FROZEN.
- Rule logic (any rule's `check_file()` method body). U5 only changes severity, not behavior.
- `pg_design_lint/rules/R29` (if R29 has shipped — likely yes). U5 may set R29's severity, but doesn't touch its check logic.
- `panda_ledger/` — Phase 2/3 territory.

---

## §3 — Build order

1. **Read base.py + at least 3 rule modules + __main__.py + spec.json end-to-end first.**
2. Read spec §4.4 + §4.6 + §10.2.
3. Verify the existing `lint_config.rule_telemetry` shape in spec.json. Either it works as-is, or extend it.
4. Implement `read_telemetry` and `write_telemetry` first. Atomic-write semantics (use the existing `panda_ledger/shared/atomic_write.py` if reusable).
5. Implement `update_telemetry` (scanning + counting). Test against fixtures.
6. Implement `promotion_eligible_rules` (stability gate). Test edge cases.
7. Implement `promote_rule` and `demote_rule` (rule module mutation). See §3.4 for mutation strategy.
8. Wire CLI flags in `__main__.py`.
9. Build all fixtures + tests.
10. Run full pytest suite (368+ tests should still pass).
11. Run `pg_design_lint --update-telemetry` against the live codebase. Verify spec.json updated. Run `--promote-eligible` — list any eligible rules (probably none today; codebase has no `pg-lint:allow` exemptions yet).

### §3.4 — Rule severity mutation strategy

Two approaches for mutating a rule module's severity:

**Option A: textual patch.** `promote_rule` reads the rule's .py file, regex-replaces `severity = Severity.WARNING` with `severity = Severity.ERROR`, writes back. Pros: simple, no dependencies, preserves comments. Cons: regex on Python code is fragile if formatting drifts (e.g., `severity=Severity.WARNING` no spaces vs `severity = Severity.WARNING`).

**Option B: AST-based patch.** Parse the rule module to AST, find the `Rule` subclass, find the `severity` assignment, modify the AST, unparse to source. Pros: format-tolerant, robust. Cons: more LOC, slightly fragile on unusual class structure.

**Option C: runtime lookup.** Don't mutate the rule file at all. Instead, the `Rule` base class reads its severity from spec.json at runtime via `cls.rule_id` lookup. Promote/demote only updates spec.json; rule modules unchanged.

**Recommendation: Option C (runtime lookup).** Cleanest. Rule modules become stateless w.r.t. severity. Demote/promote is just a spec.json edit. The class-constant `severity` field becomes a property that reads from spec.json with a class-constant default (in case spec.json doesn't have an entry for that rule, the default is used).

Implementation sketch:
```python
# In rules/base.py:
class Rule:
    rule_id: str = "R00"
    _default_severity: Severity = Severity.INFO

    @property
    def severity(self) -> Severity:
        # Read from spec.json telemetry; fall back to default.
        from pg_design_lint.telemetry import current_severity
        return current_severity(self.rule_id, self._default_severity)
```

Each rule module changes from:
```python
class R01ForbiddenColors(Rule):
    severity = Severity.ERROR  # class constant
```
to:
```python
class R01ForbiddenColors(Rule):
    _default_severity = Severity.ERROR  # default; runtime lookup overrides
```

This is a one-line mechanical edit per existing rule module (29 rules at the time of writing this dispatch — R01–R28 + R03b. If R29 ships first per Phase 4 sequencing, the count is 30; either way, scriptize the migration.)

**If Codex disagrees:** Option A or B work, just less elegant. The textual patch in Option A might be the most pragmatic if you'd rather not touch every rule module. Surface in Step 0.

---

## §4 — Acceptance criteria

U5 dispatch is acceptance-passing when:

1. **`--update-telemetry` writes correct counts.** Verify by adding a known number of `pg-lint:allow R02` to a fixture file, running update, confirming spec.json reflects the count.
2. **`--promote-eligible` lists only eligible rules.** Verify with a fixture spec.json showing one rule with stable history (eligible) and another with growing history (not eligible). Output lists only the first.
3. **`--promote R02` promotes correctly.** Verify rule module severity (or spec.json severity, depending on §3.4 choice) shows ERROR after promotion. spec.json `last_promotion_at` updated.
4. **`--promote` refuses ineligible rules.** Clear error message, nothing modified.
5. **`--demote R01` demotes correctly.** Verify rule shows WARNING after demote.
6. **All test cases pass.** Twelve cases above.
7. **Existing test suite still passes.** No regressions in the 368 existing tests.
8. **No new dependencies** beyond what's already in PG.
9. **Performance.** `--update-telemetry` should complete in a reasonable time on the full codebase. Codex Step 0 task: measure on the live codebase, surface the actual time. If >10 seconds, scope down (e.g., parallel scan, or `.gitignore`-style exclusions). `--promote-eligible` is essentially instant (no I/O beyond spec.json read).
10. **`--update-telemetry` is idempotent.** Running it twice doesn't change anything beyond the timestamp.

---

## §5 — Out of scope

- **Auto-promotion without `--promote` invocation.** U5 is opt-in by design. The "auto" in U5 refers to data-driven *eligibility*, not automated promotion. (Per spec §10.2.)
- **Per-file or per-author exemption tracking.** U5 tracks aggregate exemption count only.
- **Demotion eligibility gate.** Demotion is always allowed. If a rule is causing pain, Darrin should be able to demote without ceremony.
- **Notification when a rule becomes eligible.** Polled via `--promote-eligible`, not pushed.
- **Promotion of multiple rules in one command.** `--promote R<id>` takes a single ID. Batch promotion can be a follow-up if desired.
- **Telemetry retention beyond exemption_history.** The `exemption_history: list[dict]` (or whatever shape Codex picks) keeps last N entries; older ones drop off. N=10 reasonable.
- **GUI for telemetry visualization.** CLI-only. Browse tab is a future v3 feature.

---

## §6 — Coordination with R29 (U1) and U3

Dispatch sequence is R29 → U3 → U5, but **U5 has no technical dependency on R29 or U3**. Each Phase 4 dispatch ships independently; the sequencing is dispatching-order preference for Darrin's convenience.

U5 operates on the rule severity layer, orthogonal to what each rule checks (R29) and orthogonal to commit-decision tracing (U3). If R29 hasn't shipped, U5's `--update-telemetry` simply doesn't see R29 in the rule list — no harm. If U3 hasn't shipped, U5 promotion commits don't auto-amend decision frontmatter — promotions can be tracked manually until U3 lands.

If U5 ships before U3, the rule severity flow is: rule has default in module + override in spec.json → telemetry update tracks exemption count → promotion eligibility surfaces → manual `--promote` promotes. Already complete and useful without U3.

If U5 ships after U3, the trace from "decision lands" → "rule promoted" runs end-to-end via the U3 hook auto-amending decision frontmatter when a U5 promotion commit cites a decision. (Promotions ARE decisions and should be captured per the threshold-3 rule.)

---

## §7 — Coordination with author/reviewer gate (already shipped)

§4.4 author/reviewer split is already shipped as part of v2.3 spec. U5 is the next layer above this:
- v2.3 author/reviewer split: WHEN to enforce a rule (which commits trigger blocking).
- U5: WHICH severity the rule has at all.

The two are independent. U5 changes a rule's severity; the gate decides whether that severity blocks for a given commit author.

---

## §8 — Sequencing questions for Codex

Three design questions worth surfacing in Step 0:

1. **Severity mutation: Option A/B/C from §3.4.** I recommend Option C (runtime lookup). Codex may disagree.

2. **Stability window: 2 weeks fixed, or configurable?** Spec §10.2 says "two consecutive weeks." Could be a `lint_config.promotion_stability_weeks: 2` field in spec.json, with default 2. Lets Darrin tune later without re-shipping U5. Recommend: ship as a configurable field with default 2.

3. **Stability gate granularity: telemetry update count vs calendar weeks.** "2 weeks" assumes telemetry runs weekly. If telemetry runs daily (CI run on every commit), "2 weeks" should mean "14+ days," not "2 telemetry updates." Recommend: store ISO timestamps in `exemption_history` and require the difference between first and last to be ≥14 days, regardless of how many entries.

Codex: review these three. Push back on any if you have a better answer.

---

## §9 — Delivery format

Standard impl report to `cc_mailbox/CLAUDE Inbox/` with:
- File-by-file summary (LOC, notes)
- Severity mutation strategy chosen (A/B/C from §3.4) with rationale
- Telemetry shape: actual vs spec
- Test results (full pytest including the new telemetry tests)
- Acceptance criteria walkthrough (each item PASS/FAIL/NOTES)
- Sample `--update-telemetry` output on the live codebase
- Sample `--promote-eligible` output (likely empty list right now — no exemptions in codebase yet — that's fine)
- Any open issues or contract concerns surfaced during build
- Working tree state at impl-complete (uncommitted; awaits Darrin commit-go)

---

## §10 — Estimated time

~2 hours Codex time (High tier). LOC budget ~200-280 src + ~150 tests = ~350-430 LOC total.

Build sequence per §3 above. No daylight pressure.

---

## §11 — What this closes

U5 closes the rule-rigidity failure mode. v2.2's "one month of clean Phase A runs before promoting more rules" was a calendar gate that ignored actual data — a rule could be silent for a month not because it was working but because it was disabled or trivially exempted. U5's per-rule telemetry forces the question: is this rule actually quiet, or is it being silenced via exemptions?

Stable exemption count means the rule is genuinely quiet. Growing exemption count means the rule is producing false positives or hitting legitimate edge cases that warrant exemptions; promotion would just create more friction.

After U5, the rule-promotion pipeline is data-driven, opt-in, and reversible. New rules ship as `warning`, telemetry gathers data, eligibility surfaces, Darrin promotes when comfortable, demotes if it goes wrong. The Phase A blocking-rule list grows organically.

---

## §12 — Begin trigger

Begin work ONLY after:
1. Phase 2 ships (commit visible in `git log` matching v4.71+).
2. Darrin sends explicit go in chat ("dispatch U5 to Codex" or equivalent).
3. (Soft, not blocking.) U1 R29 has shipped (v4.72+) and U3 has shipped (v4.73+) — U5 has no technical dependency on either; this is dispatching-order preference only.

If you (Codex) read this dispatch before conditions 1 and 2 are met, hold. Do not draft Step 0, do not start work. Acknowledge receipt only when explicitly asked.

-- Claude Desktop
