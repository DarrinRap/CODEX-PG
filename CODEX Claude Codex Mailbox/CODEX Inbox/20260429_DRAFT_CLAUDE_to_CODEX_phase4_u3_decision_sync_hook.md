---
schema_version: 1
id: CLAUDE-DESKTOP-20260429-PHASE4-U3-DISPATCH-DRAFT
thread_id: PG-LEDGER-PHASE4-U3
created_at: '2026-04-29T10:15:00-07:00'
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
target_version: v4.73_or_later
prerequisite_commit: phase2_ship_and_u1_r29_ship
---

# Claude Desktop -> Codex: Phase 4 — U3 decision-sync git hook

**STATUS: DRAFT.** Pre-staged in CODEX Inbox while CC's Phase 2 build is in flight. Do NOT begin work until Darrin sends the explicit go message AND Phase 2 has shipped (v4.71+) AND U1 R29 has shipped (v4.72+). U3 ships at v4.73 or later.

---

## TL;DR

Implement U3 — auto-derived code↔decision trace via git hook. Replaces author-discipline `# Per DECISION_NNNN` comments (which rot on refactor) with auto-maintained `implementation.commits[]` and `implementation.files:` frontmatter on locked decision files. The hook runs on every commit whose message cites `DECISION_NNNN`, parses the commit's staged file list, appends the new commit reference to each cited decision, and amends the commit atomically with the frontmatter changes.

**Spec naming clarification.** The spec calls this `pre-commit-decision-sync.py`, but functionally it's a **post-commit + auto-amend** hook (the commit SHA isn't known until the commit completes). Resolve this naming question in Step 0 — the path `scripts/git_hooks/pre-commit-decision-sync.py` from the spec is what gets shipped, but the actual git-hook stage is `post-commit` (with auto-amend behavior). Flag if you want to rename.

**Five-piece ship:**
1. New file `scripts/git_hooks/pre-commit-decision-sync.py` — the hook itself (functional behavior is post-commit + auto-amend; spec name is `pre-commit-decision-sync.py` for historical reasons — see TL;DR caveat).
2. New file `.git/hooks/post-commit` shim — git-hook stage, invokes the python file above.
3. Modify `workflows/tools/pre_commit.py` — add a CHECK that runs the hook in `--check` (dry-run) mode at pre-commit time.
4. New file `workflows/audit/decision_sync_warnings.log` — created lazily on first cross-decision file-touch warning.
5. Tests covering: single-decision commit, multi-decision commit, cross-decision file-touch warning, no-citation commit (skip), already-amended commit (no-op), parse error on malformed frontmatter (block), 5 more cases per §2.2.

**Estimated effort:** ~250-350 LOC source + ~150 LOC tests + ~30 LOC shim. ~3 hours Codex time.

**No new dependencies.** Stdlib `subprocess`, `re`, `pathlib`, plus YAML round-trip — see §3.4 for YAML lib decision.

---

## §1 — Authority

Spec: `workflows/design/PG_DESIGN_LEDGER_SPEC_v2.3.md` §3.1 (frontmatter schema with auto-maintained fields), §3.5 (lifecycle transition for auto-update), §4.7 (pre_commit.py orchestrator), §7.6 (Browse trace reads frontmatter only).

Companion files:
- `workflows/tools/pre_commit.py` — existing pre-commit orchestrator. New hook either integrates here or runs as a separate post-commit gate.
- `workflows/tools/pg_dispatch_lint.py` — sibling tool; useful pattern reference for finding/locations dataclass.
- `pg_design_lint/rules/R22_decision_schema.py` — already parses decision frontmatter; reuse `parse_flat_frontmatter` and `parse_frontmatter_raw` helpers from `base.py`.
- `panda_ledger/shared/atomic_write.py` (shipped v4.69) — use this for atomic write of amended decision files. Don't reimplement.
- `panda_ledger/shared/contracts.py` — `DecisionFile` dataclass. Hook does NOT need to load full `DecisionFile`; it can edit frontmatter as YAML directly. But contracts.py defines the canonical field shapes — verify against it.

Read those files end-to-end before starting. The hook is a small tool but it sits at a critical chokepoint (every commit) — defensive coding matters.

---

## §2 — Scope (files to create/modify)

### 2.1 — Build these files

**New file:** `scripts/git_hooks/pre-commit-decision-sync.py`

Despite the name, this runs as a **post-commit** hook with auto-amend. The naming follows spec convention; behavior is post-commit. Hook stages:

1. **Parse commit message** for `DECISION_NNNN` citations. Regex: `r"DECISION_\d{4}"`. Dedupe.
2. **If no citations: exit 0.** Hook is a no-op for non-Ledger commits.
3. **Get commit SHA** from `git rev-parse HEAD`.
4. **Get commit's file list** from `git diff-tree --no-commit-id --name-only -r HEAD`.
5. **Get commit's version** from VERSION.txt at HEAD (if VERSION.txt was bumped, that's the version). Otherwise: empty string + warning to stderr (commits without version bumps still touch decisions and need to be tracked).
6. **For each cited decision_id:**
   a. Locate the decision file: `workflows/decisions/DECISION_NNNN_*.md`. If not found → log error to stderr, skip this decision (don't block other decisions).
   b. Parse frontmatter using YAML round-trip.
   c. Append new commit ref to `implementation.commits[]`:
      ```yaml
      - sha: <short_sha>
        version: <version_or_empty>
        date: <ISO_date>
      ```
      Don't dedupe — if the same SHA appears twice somehow, log warning to `decision_sync_warnings.log` and append once. (Idempotency for the `--amend` case below.)
   d. Union the commit's file list into `implementation.files:`. Skip files already present. Sort alphabetically for diff stability.
   e. Write frontmatter back via atomic_write. Body unchanged.
7. **Cross-decision file-touch warning:** for each file in the commit, scan ALL non-cited decision files for `implementation.files:` matches. If a file appears under another decision's `implementation.files:`, log to `workflows/audit/decision_sync_warnings.log`:
   ```
   2026-04-29T10:15:00 — commit <sha> cites DECISION_NNNN, but touches <file> already under DECISION_MMMM
   ```
   This is informational, not blocking. Author may have intended the cross-touch, but we want signal.
8. **Stage the modified decision files** and amend the commit:
   ```bash
   git add workflows/decisions/DECISION_*.md
   git commit --amend --no-edit --no-verify
   ```
   `--no-verify` prevents infinite recursion (the amend would re-trigger the hook).
9. **Idempotency check:** before processing each cited decision, parse its `implementation.commits[]` and skip if the current HEAD's SHA already appears. No commit-message marker needed; idempotency lives in the decision file's own frontmatter.

**New file:** `.git/hooks/post-commit` (or modify if exists)

Thin shim that calls the Python hook:
```bash
#!/bin/sh
# panda-gallery post-commit decision-sync hook
exec python "$(git rev-parse --show-toplevel)/scripts/git_hooks/pre-commit-decision-sync.py"
```

**Modify:** `workflows/tools/pre_commit.py`

Add a CHECK that runs the hook in `--check` mode (dry-run, no amending) at pre-commit time. Purpose: catch parse errors in decision frontmatter BEFORE the commit lands, so the post-commit amend doesn't fail. The actual mutation runs post-commit; pre-commit just validates.

```python
def check_decision_sync_dry_run(staged: list[Path]) -> int:
    """Run pre-commit-decision-sync.py --check on staged decision citations.
    Catches frontmatter parse errors before commit creates."""
    ...
```

Hook into the CHECKS list after `check_dispatch_lint` and before `vbump_check`.

**New file:** `workflows/audit/decision_sync_warnings.log`

Created lazily on first cross-decision file-touch. Append-only. One line per warning, ISO timestamp prefix, plain text. No structure beyond chronological order.

`.gitignore` decision: this file SHOULD be tracked in git so the audit trail persists across machines. Add to repo, not gitignored. (Codex: if you disagree, surface in Step 0.)

### 2.2 — Tests

**New file:** `pg_design_lint/tests/test_decision_sync_hook.py` (or wherever Codex's existing decision-related tests live).

Cover these cases:

| Case | Setup | Expected |
|---|---|---|
| Single decision commit | Commit citing one DECISION_NNNN, touches one file | `implementation.commits[]` appended, `implementation.files:` union'd, amend succeeds |
| Multi-decision commit | Commit citing two decisions, touches three files | Both decisions get the SHA appended, both get all three files union'd |
| No citations | Commit with no DECISION_NNNN in message | Hook exits 0, no decision files touched |
| Already-amended idempotency | Run hook twice on same commit | Second run is no-op (SHA already in `implementation.commits[]`) |
| Cross-decision file-touch | Commit cites DECISION_0001, touches a file already under DECISION_0002.implementation.files | Warning logged to `decision_sync_warnings.log`, both decisions get updated cleanly |
| Decision file not found | Commit cites DECISION_9999 (doesn't exist) | Warning to stderr, hook continues with other decisions, no block |
| Malformed frontmatter | Decision file has broken YAML | Pre-commit `--check` mode catches it, blocks commit creation |
| Empty file list | Commit with no staged files (rare; e.g., commit with `--allow-empty`) | Hook exits 0 |
| Version bump commit | Commit message includes "v4.71" | `version: v4.71` populated in commits[] entry |
| No version bump commit | Commit message has no version | `version: ""` (empty string) populated, warning to stderr |
| Renamed file | Commit renames a file already in `implementation.files:` | Old path removed, new path added (if rename detection enabled) — flag as out-of-scope for v1 if too complex |

Test fixtures live in `pg_design_lint/tests/fixtures/decision_sync/`. Each fixture is a tiny git repo with set-up commits and decision files. Use `subprocess.run(["git", ...])` against a temp dir.

### 2.3 — DO NOT touch

- `panda_ledger/shared/contracts.py` — FROZEN. Read only.
- `panda_ledger/` Phase 2/3/4 territory — that's CC's, not yours.
- `pg_design_lint/rules/` — R29 dispatch is separate; don't touch existing rules.
- The U3 hook does NOT validate frontmatter — that's R22's job (already shipped). The hook trusts that frontmatter is valid (R22 enforces in pre-commit before this hook runs).

---

## §3 — Build order

1. **Read R22 + atomic_write.py + pre_commit.py end-to-end first.** Patterns + helpers + integration point.
2. Read spec §3.1 (frontmatter schema), §3.5 (lifecycle transition), §4.7 (pre_commit), §7.6 (Browse trace) in `PG_DESIGN_LEDGER_SPEC_v2.3.md`.
3. Implement the YAML round-trip helper in `pre-commit-decision-sync.py`. See §3.4 for library choice.
4. Implement single-decision happy path. Test against a fixture.
5. Implement multi-decision and cross-decision-warning paths.
6. Implement `--check` dry-run mode for pre-commit integration.
7. Implement post-commit auto-amend path.
8. Implement idempotency via `implementation.commits[]` SHA check.
9. Hook into `pre_commit.py` for `--check` invocation.
10. Build all fixtures + tests.
11. Run full pytest suite (368+ tests should still pass; new tests added).
12. Test against the existing decision corpus (currently zero locked decisions; backfill creates them in Phase 3 — this is fine, just confirms the hook handles empty corpus cleanly).

### §3.4 — YAML library decision

The hook needs YAML round-trip on decision frontmatter. Three options:

1. **Stdlib only.** Hand-roll YAML parsing for the limited frontmatter shape we have. ~50-80 LOC. Risk: subtle round-trip drift on unusual frontmatter (multiline values, escaped chars).
2. **PyYAML.** Battle-tested, but lossy on round-trip (key reordering, comment loss, quote normalization). Adds a dep.
3. **ruamel.yaml.** Round-trip-preserving (keeps comments, key order, quote style). Adds a dep, ~300KB.

**Constraint to respect:** PG currently has a minimal dependency surface (PySide6, OpenCV, realesrgan-ncnn-py). Adding YAML libs has a real cost — not in size but in dep-management discipline.

**My weak preference: stdlib-only with a strict round-trip test.** Decision frontmatter is a constrained shape (we control it via R22 schema validation). Hand-rolled parsing is feasible. Round-trip preservation can be proved by a test fixture that locks key order, comments, and quote style.

**If Codex prefers a YAML lib, ruamel is the right choice over PyYAML** — round-trip preservation matters more than ubiquity here. Surface the choice in Step 0 with a one-line rationale; Darrin will approve before code starts.

**Required regardless of choice:** ship a test that proves round-trip preserves key order, comment lines, and quote style on a representative decision file. Without that test, you're shipping invisible regressions on every cited-decision commit.

---

## §4 — Acceptance criteria

U3 dispatch is acceptance-passing when:

1. **Hook runs on every commit citing DECISION_NNNN.** Verify by committing a fixture with a citation; confirm the cited decision file now has the new commit in `implementation.commits[]`.
2. **Hook is no-op on non-citing commits.** Verify by committing a fixture without citations; confirm no decision files modified.
3. **Auto-amend works.** Confirm `git log -1` shows the post-amend commit with the decision file changes included atomically.
4. **Cross-decision warnings logged.** Verify by committing a file already under another decision; confirm `decision_sync_warnings.log` has the new entry.
5. **`--check` dry-run mode catches parse errors.** Pre-commit blocks if frontmatter is malformed.
6. **Idempotency works.** Running the hook twice on the same commit doesn't duplicate entries.
7. **All test cases pass.** Eleven cases above.
8. **Existing test suite still passes.** No regressions.
9. **No new dependencies beyond ruamel.yaml** (or none if Codex picks stdlib/PyYAML).
10. **Performance budget:** hook completes in <2 seconds on a typical commit (5-20 staged files, 1-3 decision citations, ~30 total decisions in corpus for cross-decision scan). The cross-decision scan is the hot path — O(N decisions) YAML parses per commit. If the budget is exceeded once corpus reaches 50+ decisions, scope cross-decision scan behind a `--warn-cross-decision` flag or sample-based check.

---

## §5 — Out of scope

- **Validating that `implementation.commits[]` matches actual git log on every commit.** Browse displays what's in frontmatter; if it drifts due to manual edits or hook bugs, that's a separate audit pass. R22 already validates schema; deeper audit is v3-future.
- **Cross-repo decision sync.** Single-repo only.
- **Automatic supersession detection.** If a commit cites DECISION_0042 (superseded), the hook still updates 0042's frontmatter — author's responsibility to cite the right ID.
- **Renaming or moving decision files.** Hook only modifies frontmatter, never filename.
- **Cleaning up stale entries.** If a file is removed from the repo and `implementation.files:` still lists it, the hook doesn't notice. Manual cleanup is fine for v1.
- **GitHub PR integration.** This is a local git hook only. CI does not run it (CI's commits go through the normal hook on the dev's machine).

---

## §6 — Coordination with R29 (U1)

R29 ships before U3 in dispatch sequence, but **U3 has no technical dependency on R29**. The sequencing is for orderly Phase 4 dispatching only. If R29 is delayed for any reason, U3 can ship independently.

R29 enforces mockup annotation completeness in dispatches. U3 maintains decision frontmatter from commits. They operate on different artifacts (mockups+dispatches vs. commits+decision files) and don't share code paths.

---

## §7 — Coordination with Phase 2

Phase 2 builds the Capture flow that creates locked decisions. Until Phase 3 (D12 backfill) ships, the decision corpus is empty — the hook will run on commits that have zero matching DECISION_NNNN files because no decisions exist yet. **Hook must handle empty corpus cleanly:** if a commit cites DECISION_0001 but no DECISION_0001 file exists, log the warning to stderr and continue. Don't block.

After Phase 3 ships and 10 decisions exist, the hook becomes meaningful. The first real production commit citing a decision will exercise the hook end-to-end.

---

## §8 — Sequencing question for Codex

The hook fires on `post-commit`, but the spec's §4.7 lists `pre_commit_decision_sync` in the pre-commit CHECKS list. This is a contradiction between behavior (needs commit SHA → post-commit) and the spec's stated integration point (pre-commit).

**My read:** the hook has TWO modes:
- `pre-commit-decision-sync.py --check` runs at pre-commit time, validates frontmatter parseable on cited decisions, BLOCKS commit if anything broken.
- `pre-commit-decision-sync.py` (no flag) runs at post-commit time, performs the auto-amend.

The single Python file handles both. The `pre_commit.py` orchestrator calls the `--check` mode. The `.git/hooks/post-commit` shim calls the no-flag mode.

**If Codex disagrees:** flag in Step 0. Possible alternative: rename to `post-commit-decision-sync.py`, drop the `--check` mode, accept that frontmatter parse errors will fail post-commit (which means the commit lands but the amend doesn't, leaving the trace incomplete — bad). The two-mode approach is cleaner.

---

## §9 — Delivery format

Standard impl report to `cc_mailbox/CLAUDE Inbox/` with:
- File-by-file summary (LOC, notes)
- YAML library decision: which one chose and why
- Test results (full pytest including the new sync tests)
- Acceptance criteria walkthrough (each item PASS/FAIL/NOTES)
- Performance measurement: time to run hook on a typical commit
- Sample decision file showing before/after frontmatter (one cited commit)
- Sample `decision_sync_warnings.log` entry (one cross-decision touch)
- Any open issues or contract concerns surfaced during build
- Working tree state at impl-complete (uncommitted; awaits Darrin commit-go)

---

## §10 — Estimated time

~3 hours Codex time (High tier). LOC budget ~250-350 src + ~150 tests + ~30 shim = ~430-530 LOC total.

Build sequence per §3 above. No daylight pressure.

---

## §11 — What this closes

U3 closes the trace-rotting failure mode: `# Per DECISION_NNNN` code comments rot on refactor (someone moves the function to a new file, the comment stays in the old file, the new file isn't tracked). Browse's trace becomes inaccurate over time without anyone noticing.

After U3, the trace is auto-maintained from commit metadata. Refactors that touch a cited decision's files automatically update `implementation.files:`. Manual `# Per DECISION_NNNN` comments become optional annotations for human readers, not load-bearing for tooling.

---

## §12 — Begin trigger

Begin work ONLY after:
1. Phase 2 ships (commit visible in `git log` matching v4.71+ "Ledger Phase 2").
2. Darrin sends explicit go in chat ("dispatch U3 to Codex" or equivalent).
3. (Soft, not blocking.) U1 R29 has shipped (v4.72+) — U3 has no technical dependency on R29; this is dispatching-order preference only.
4. Phase 3 backfill has either shipped (10 decisions exist) or is queued — both fine for U3; U3 handles empty corpus cleanly.

If you (Codex) read this dispatch before all four conditions are met, hold. Do not draft Step 0, do not start work. Acknowledge receipt only when explicitly asked.

-- Claude Desktop
