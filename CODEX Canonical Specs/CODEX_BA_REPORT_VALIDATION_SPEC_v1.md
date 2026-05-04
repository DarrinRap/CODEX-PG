# CODEX BA Report Validation Spec v1

Status: Draft for Darrin review
Created: 2026-05-04
Owner: Codex
Project: Panda Gallery / Bible Audit
Spec type: validation and trust-gate design

Canonical spec path:

`C:\CODEX PG\CODEX Canonical Specs\CODEX_BA_REPORT_VALIDATION_SPEC_v1.md`

Primary implementation targets if approved later:

- `C:\panda-gallery\scripts\ba_audit_runner.py`
- `C:\panda-gallery\tests\test_ba_audit_runner.py`
- `C:\panda-gallery\workflows\design\applets\PG_Design_Bible_Audit_v1.html`
- New validator module or script under `C:\panda-gallery\scripts\`

Reference surfaces reviewed for this spec:

- `C:\panda-gallery\scripts\ba_audit_runner.py`
- `C:\panda-gallery\tests\test_ba_audit_runner.py`
- `C:\panda-gallery\workflows\design\BA_TRUTH_SPLIT_COVERAGE_RUNTIME_SPEC_v1.md`
- `C:\panda-gallery\workflows\design\BA_RUNTIME_CHECK_PACK_SPEC_v1.3.md`
- `C:\panda-gallery\workflows\design\BA_RUNTIME_TRUST_PACK_PHASE1_SPEC_v1.md`
- `C:\panda-gallery\workflows\design\BA_AUTO_DISPATCH_AFTER_RUN_SPEC_v1.md`
- `C:\panda-gallery\workflows\design\BA_REPORT_FORMAT_DEFERRED_FINDING_AMENDMENT_SPEC_v1.md`
- `C:\panda-gallery\workflows\design\BA_TEST_MODE_FIXTURE_SPEC_v1.md`
- Recent BA dispatch diagnostic thread `BA-FIX-PANDA-AGENT-HUB`

## 1. Purpose

This spec defines what is required to validate Bible Audit reports before Darrin, Codex, Claude Desktop, or Claude Code treats a BA report as trustworthy.

BA report validation means proving that a BA report:

1. Uses the canonical BA schema.
2. Is internally consistent.
3. Has evidence for every status claim.
4. Correctly separates proven failures, heuristic suspects, coverage gaps, and informational evidence.
5. Does not overstate runtime or cross-app coverage.
6. Is fresh enough for its claimed purpose.
7. Can be reproduced or has its drift explained.
8. Produces dispatch packets whose machine-readable annex matches the canonical report.
9. Makes false positives, stale runtime state, and scanner limitations visible instead of hiding them.

This spec does not authorize implementation. It is a vetted-spec candidate for future implementation.

## 2. Background

BA has become a high-leverage coordination surface. It can produce clean reports, actionable fix dispatches, runtime trust packs, PAH Inspector wrappers, test-mode fixture reports, and auto-dispatch mailbox packets.

That power creates a risk: a BA report can look authoritative even when part of its evidence is stale, environment-dependent, or only heuristic.

The PAH diagnostic case on 2026-05-03 demonstrated the failure mode:

- Original BA dispatch for `Panda Agent Hub` reported endpoint connection failures.
- A reproduction run changed totals from `25 fail / 15 warn / 1 unknown / 53 evidenced` to `16 fail / 16 warn / 1 unknown / 71 evidenced`.
- Direct probes initially targeted `127.0.0.1:8788`, but PAH Inspector's default URL is `127.0.0.1:8765`.
- Endpoint failures were not reproduced on the correct inspector URL.
- Static action-feedback findings remained as heuristic suspects, not confirmed app bugs.

Conclusion: BA reports need a validation layer that can answer:

- Is this report structurally valid?
- Is this report current?
- Did the reported runtime evidence actually run against the intended target?
- Did reproduction produce the same findings?
- Which findings are confirmed, stale, heuristic, or coverage gaps?
- Is the report trusted for decision-making, or only useful as a diagnostic lead?

## 3. Scope

In scope:

- BA JSON report validation.
- BA text report validation.
- BA dispatch packet and JSON annex validation.
- BA latest/history/progress artifact validation.
- Test Mode fixture validation.
- Runtime Trust Pack validation for `Bible Audit`.
- Runtime Check Pack validation for `Panda Agent Hub`.
- Evidence existence and evidence-line validation.
- Freshness and drift validation.
- Validator CLI/API output contract.
- Required tests and acceptance criteria.

Out of scope:

- Fixing target-app defects found by BA.
- Changing BA scanner logic.
- Changing BA report format beyond validation metadata.
- Replacing PAH Inspector.
- Universal PySide runtime click testing.
- Full visual regression baseline comparison.
- Auto-resolving or auto-closing BA dispatch threads.
- Marking mailbox messages read.
- Writing to `C:\panda-gallery` except through a future explicitly approved implementation task.

## 4. Terms

`BA report` means a `BA_AUDIT_RESULT_v1` JSON object produced by `scripts\ba_audit_runner.py`.

`Canonical latest report` means:

`C:\panda-gallery\workflows\design\applets\ba_audit_latest.json`

`Dispatch packet` means a BA mailbox Markdown packet using protocol `BA_FIX_DISPATCH_v1.1`, `BA_SUMMARY_DISPATCH_v1.0`, or `BA_TEST_DISPATCH_v1.0`.

`Fix dispatch packet` means an actionable BA packet with `type: ba_fix_dispatch` and protocol `BA_FIX_DISPATCH_v1.1`.

`Summary dispatch packet` means a non-actionable BA summary packet with `type: ba_summary_dispatch` and protocol `BA_SUMMARY_DISPATCH_v1.0`, usually produced when auto-dispatch mode is `always_send_summary` and the report has zero actionable findings.

`Test dispatch packet` means a route-test packet with `type: ba_test_dispatch` and protocol `BA_TEST_DISPATCH_v1.0`; it is never a fix request.

`Validation` means checking the report and its artifacts. It does not mean fixing app code.

`Reproduction` means running BA again for the same selected app and comparing the new report with the report being validated.

`Drift` means the reproduced report differs from the original report in totals, finding IDs, scanner versions, runtime verdict, runtime target URL, or evidence paths.

`Trusted report` means a report passes the structural, consistency, evidence, freshness, runtime, and optional reproduction gates required by the selected validation profile.

`Diagnostic-only report` means a report has useful evidence but cannot be used as a fix authority without further investigation.

`Validation profile` means the requested validation depth. Profiles are defined in section 6.1 and determine whether reproduction and live probes are required.

## 5. Validation Truth Rules

The validator must enforce these rules:

1. PASS requires scanner evidence.
2. UNKNOWN is never PASS.
3. A missing scanner is a coverage gap, not success.
4. `action_feedback_static` fail/warn rows are heuristic suspects until confirmed by handler trace or runtime evidence.
5. Runtime evidence applies only to the exact target, URL, scanner, and timestamp that produced it.
6. A report can be structurally valid and still not be trusted for fixes.
7. Reproduction drift must be visible.
8. A stale runtime failure is not automatically an app bug.
9. A report cannot certify all apps. BA is single-target.
10. A dispatch packet cannot be trusted unless its annex matches the canonical report it claims to represent.
11. A clean summary dispatch is not proof that all Panda apps are clean.
12. A validator must report limitations as first-class output.

## 6. Validation Levels

The validator must output one top-level `validation_verdict`.

Allowed values:

- `report_trusted`
- `report_trusted_with_findings`
- `diagnostic_only`
- `stale_or_drifted`
- `schema_invalid`
- `evidence_invalid`
- `runtime_untrusted`
- `dispatch_invalid`
- `blocked`

Meaning:

`report_trusted`

- No fail/warn/unknown findings.
- Schema, totals, truth split, evidence, runtime trust, freshness, and all checks required by the selected validation profile pass.
- Applies only to the selected target.

`report_trusted_with_findings`

- The report is structurally and evidentially trustworthy.
- It contains findings that require disposition.
- The validator is not saying the app is clean.

`diagnostic_only`

- The report has useful evidence but cannot authorize fixes yet.
- Common reasons: heuristic-only findings, runtime environment uncertainty, unvalidated external inspector state, or reproduction required by the selected profile but not run.

`stale_or_drifted`

- Reproduction changed important values or the report age exceeds policy.
- The report may still be useful history.

`schema_invalid`

- Required fields are missing or malformed.

`evidence_invalid`

- Evidence files, lines, artifact folders, screenshot paths, or referenced source paths are missing or inconsistent.

`runtime_untrusted`

- Runtime trust claims are unsupported, missing, stale, or contradicted by direct probes.

`dispatch_invalid`

- A BA dispatch packet has malformed frontmatter, mismatched annex data, wrong recipient metadata, missing response contract, or finding-index mismatch.

`blocked`

- Validation could not complete because a required local file, script, permission, or runtime dependency was unavailable.

### 6.1 Validation Profiles

The validator must support three validation profiles:

`structural`

- Default profile.
- Non-mutating except for an optional validator output JSON path.
- Checks schema, totals, metrics, truth split, scope, evidence paths, report text, runtime trust-pack structure, freshness, and dispatch structure if supplied.
- Does not rerun BA.
- Does not perform live HTTP probes unless the user explicitly supplies `--live-probes`.

`reproducible`

- Runs the exact BA command for the selected app and compares the new report to the original.
- May update `ba_audit_latest.json`, `ba_audit_history.jsonl`, `ba_audit_progress.json`, and runtime artifact folders because BA itself writes those artifacts.
- Required before using a stale, high-impact, or externally dispatched BA report as fix authority.

`gate`

- Includes `reproducible`.
- Applies gate-mode freshness and runtime requirements.
- Missing required runtime proof is blocking for targets with implemented runtime adapters.

The validator output must include `validation_profile`.

`report_trusted` and `report_trusted_with_findings` are allowed in the `structural` profile, but the output must also include `reproduction.status: "not_requested"`. Consumers must not treat structural validation as proof that findings are still current.

## 7. Required Validator Inputs

The validator must support these inputs:

1. Report JSON path.
2. Optional dispatch packet path.
3. Optional expected app name.
4. Optional reproduction mode.
5. Optional gate mode.
6. Optional runtime URL override.
7. Optional maximum age policy.
8. Optional output path.
9. Optional validation profile.
10. Optional live-probes flag.

Proposed CLI:

```powershell
python scripts\ba_report_validator.py --report workflows\design\applets\ba_audit_latest.json
python scripts\ba_report_validator.py --report workflows\design\applets\ba_audit_latest.json --expected-app "Panda Agent Hub" --reproduce
python scripts\ba_report_validator.py --dispatch "C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\...\*.md" --reproduce
python scripts\ba_report_validator.py --report workflows\design\applets\ba_audit_latest.json --gate
```

The validator must not mutate app source files.

If `--reproduce` is supplied, it may run:

```powershell
python scripts\ba_audit_runner.py --app "<target_app>" --summary
```

The reproduction run may update BA latest/history artifacts because that is normal BA behavior. The validator must state that side effect plainly.

## 8. Required Validator Output

The validator must emit JSON with this root shape:

```json
{
  "schema_version": "BA_REPORT_VALIDATION_v1",
  "generated_at": "2026-05-04T00:00:00-07:00",
  "validation_verdict": "report_trusted_with_findings",
  "validation_profile": "structural",
  "target_app": "Panda Agent Hub",
  "report_path": "workflows/design/applets/ba_audit_latest.json",
  "dispatch_path": "",
  "summary": {
    "errors": 0,
    "warnings": 0,
    "infos": 0,
    "drift": 0
  },
  "checks": [],
  "finding_disposition_requirements": {},
  "reproduction": {},
  "runtime_validation": {},
  "limitations": []
}
```

Each validation check row must include:

- `id`
- `status`: `pass`, `warn`, `fail`, or `blocked`
- `category`
- `title`
- `message`
- `evidence`
- `recommendation`

Required categories:

- `schema`
- `totals`
- `metrics`
- `truth_split`
- `scope`
- `evidence`
- `runtime`
- `freshness`
- `reproduction`
- `dispatch`
- `history`
- `progress`
- `limitations`

## 9. Schema Validation

The report must include:

- `schema_version`
- `generated_at`
- `repo_root`
- `runner_version`
- `manifest_path`
- `progress_snapshot_path`
- `target_app`
- `available_apps`
- `scope`
- `totals`
- `metrics`
- `app_metrics`
- `bible_coverage_matrix`
- `runtime_trust_pack`
- `checks`
- `run_state`
- `progress_percent`
- `run_progress`
- `staleness_policy`
- `scanner_versions`
- `limitations`
- `truth_split`
- `report_text`

Hard failures:

- `schema_version` is not `BA_AUDIT_RESULT_v1`.
- `checks` is missing or not an array.
- `target_app` is empty.
- `scope` is empty or has more than one selected target.
- `totals` is missing.
- `truth_split` is missing.
- `runtime_trust_pack` is missing.
- `report_text` is missing or not a string.

Warnings:

- `app_run_summaries` is missing.
- `auto_dispatch` is missing from a server job result.
- `scanner_versions` omits a known scanner.

## 10. Internal Consistency Validation

The validator must recompute:

- `totals.pass`
- `totals.fail`
- `totals.warn`
- `totals.unknown`
- `totals.checks`
- `metrics.evidence_score`
- `metrics.evidence_score_percent`
- `metrics.coverage_debt`
- `metrics.coverage_debt_percent`
- `app_metrics`
- `truth_split`

Required formulas:

- `evidence_score = pass / (pass + fail + warn)`
- `coverage_debt = unknown / (pass + fail + warn + unknown)`

Required checks:

1. Sum of status counts equals `len(checks)`.
2. `totals.checks` equals `len(checks)`.
3. `truth_split` counts sum to `len(checks)`.
4. Truth bucket `by_status` values match check statuses.
5. Every check has `truth_bucket`, `truth_label`, and `confidence`.
6. `report_text` headline totals match JSON totals.
7. `report_text` includes mandatory truth header.
8. `report_text` includes `WHAT BA ACTUALLY TESTED`.
9. `report_text` includes `TRUTH SPLIT`.
10. `report_text` includes `BIBLE COVERAGE MATRIX`.

Any mismatch in totals, metrics, truth split, or report text totals is a hard fail.

## 11. Scope Validation

The validator must prove the report is single-target.

Required checks:

1. `target_app` matches the expected app if supplied.
2. `totals.target_apps == 1`.
3. `scope` has exactly one target row.
4. `scope[0].app == target_app`.
5. `scope[0].status` is `scanned` or explicitly `missing`.
6. `report_text` must not claim all-app coverage.
7. Dispatch packets must say selected app only.

If a report implies all-app certification, validation fails.

## 12. Evidence Validation

Every non-summary check row must have evidence unless the scanner is explicitly allowed to produce no file evidence.

Required evidence row fields:

- `file`
- optional `line`
- optional `detail`

Validation rules:

1. Evidence paths must resolve under an allowed project root:
   - `C:\panda-gallery`
   - `C:\CODEX PG`
2. Evidence paths must exist unless the row title explicitly describes a missing file or missing artifact.
3. If `line` is present, it must be a positive integer.
4. If `line` is present for a text file, the file must contain at least that many lines.
5. Runtime screenshot evidence paths must exist and have nonzero length.
6. Runtime artifact folders must exist when `runtime_trust_pack.artifact_folder` is non-empty.
7. PAH Inspector evidence must include original `pah_check_id` in detail when scanner is `runtime_check_pack`.
8. Machine-generated temporary test-mode evidence may be marked ephemeral, but live reports must not depend on deleted temp files.

Allowed no-file-evidence cases:

1. `report_consistency` rows that explicitly validate derived in-memory totals.
2. `bible_coverage_matrix` rows that validate matrix generation metadata rather than a source file.
3. `staleness` rows whose evidence is the current report timestamp and whose message names the generated timestamp.
4. Validator-generated checks in `BA_REPORT_VALIDATION_v1` output.

Any no-file-evidence row must still include a clear message explaining what was checked. A fail/warn/unknown row without file evidence and without one of the allowed explanations is invalid.

Evidence failures make the report `evidence_invalid` unless the finding is intentionally about missing evidence. Missing evidence findings can be valid if they are clearly reported as fail/warn/unknown.

## 13. Truth Classification Validation

The validator must recompute the expected truth bucket for each check using the BA classifier:

1. `status == pass` -> `informational_evidence`
2. `status == unknown` -> `coverage_gaps`
3. `severity in {"coverage-gap", "scanner-gap"}` -> `coverage_gaps`
4. `scanner == "action_feedback_static"` -> `heuristic_suspects`
5. otherwise -> `proven_failures`

The validator must recompute confidence:

1. pass or informational -> `informational`
2. coverage gap -> `coverage_gap`
3. `action_feedback_static` or heuristic -> `heuristic`
4. otherwise -> `high`

Hard failures:

- Report truth bucket differs from recomputed bucket.
- Report confidence differs from recomputed confidence.
- `action_feedback_static` fail/warn is classified as proven.
- UNKNOWN is classified as pass or informational.

## 14. Runtime Trust Validation

Runtime validation is target-specific.

### 14.1 Bible Audit

For `target_app == "Bible Audit"`:

Required for `runtime_trusted`:

1. `runtime_trust_pack.runtime_required == true`.
2. `runtime_trust_pack.runtime_applicable == true`.
3. `runtime_trust_pack.runtime_complete == true`.
4. `runtime_trust_pack.verdict == "runtime_trusted"`.
5. Required scanners include `runtime_action_feedback` and `runtime_geometry`.
6. Executed scanners include both required scanners.
7. `missing_evidence` is empty.
8. `runtime_findings` is empty.
9. Six required screenshots are listed.
10. All screenshot files exist and have nonzero length.
11. `server_url` is non-empty.
12. Runtime findings in `checks` agree with runtime trust pack summary.

If these fail in standard mode, the report is `runtime_untrusted`.

If gate mode is enabled, missing runtime evidence is a blocking fail.

### 14.2 Panda Agent Hub

For `target_app == "Panda Agent Hub"`:

BA must validate `runtime_check_pack` as a PAH Inspector wrapper, not as a BA browser runtime trust pack.

Required checks:

1. `runtime_check_pack` appears in the selected target scanner list.
2. At least one `runtime_check_pack` finding exists.
3. Every `runtime_check_pack` row maps to a PAH Inspector finding or an explicit inspector import/execution failure.
4. PAH Inspector evidence file exists.
5. Evidence detail includes original `pah_check_id` where applicable.
6. The inspector default or configured URL must be captured.
7. The validator must not assume port `8788`.
8. The canonical PAH Inspector default is `http://127.0.0.1:8765` unless overridden by BA configuration.

If a PAH endpoint failure is reported, the validator should optionally run a direct read-only probe against the same URL used by PAH Inspector:

- `/api/health`
- `/api/status`
- `/api/cockpit`

If direct probes pass and the original report claimed connection refusal, classify the original runtime endpoint findings as stale/drifted unless reproduction confirms them.

The validator must distinguish:

- PAH down now.
- PAH was down when BA ran.
- BA/validator probed the wrong port.
- PAH Inspector found non-endpoint warnings such as backlog, sidecar readiness, or ledgering issues.

### 14.3 Non-BA, Non-PAH Targets

For other targets:

1. Runtime trust verdict must be `runtime_not_applicable` unless a future adapter is explicitly registered.
2. Missing BA Runtime Trust Pack must not fail the app by itself.
3. The report must not claim runtime trust.
4. Runtime gaps may appear as coverage gaps.

## 15. Freshness Validation

The validator must parse:

- `generated_at`
- `staleness_policy.mode`
- `staleness_policy.warn_hours`
- `staleness_policy.fail_hours`
- runtime artifact timestamps where available
- PAH Inspector `generated_at` where available
- dispatch frontmatter `date`
- auto-dispatch `run_id` where available

Standard mode:

- Warn if report age exceeds `warn_hours`.
- Fail if report age exceeds `fail_hours`.

Gate mode:

- Warn if report age exceeds 1 hour.
- Fail if report age exceeds 4 hours.

Runtime evidence must not be older than the report unless it is explicitly imported as historical evidence and labeled as such.

For PAH Inspector:

- Inspector report age should be compared with BA report age.
- If the inspector report is older than the BA report by more than 10 minutes, warn.
- If the inspector report is stale according to PAH health metadata, warn or fail according to validation mode.

## 16. Reproduction Validation

When `--reproduce` is enabled, the validator must:

1. Extract `target_app`.
2. Run BA for that exact app.
3. Capture exit code.
4. Load the new latest report.
5. Compare original and reproduced reports.

Required comparison keys:

- `schema_version`
- `target_app`
- `runner_version`
- `scanner_versions`
- `totals`
- `metrics`
- `truth_split`
- set of non-pass finding IDs
- set of non-pass finding titles
- runtime verdict
- runtime server URL
- PAH Inspector evidence path and generated timestamp
- dispatch actionable count if validating a dispatch

Drift categories:

- `none`: important values match.
- `timestamp_only`: generated timestamps differ but findings/totals match.
- `evidence_path_only`: artifact paths differ but findings/totals match.
- `runtime_environment`: runtime endpoint or runtime trust changed.
- `scanner_output`: finding IDs/totals changed.
- `schema_or_version`: schema, runner, or scanner versions changed.
- `target_mismatch`: reproduced target differs.

Rules:

1. `none`, `timestamp_only`, and `evidence_path_only` can still be trusted.
2. `runtime_environment` makes the report diagnostic-only unless a current runtime check confirms the original state.
3. `scanner_output` makes the original report stale/drifted.
4. `schema_or_version` requires manual review.
5. `target_mismatch` is a hard fail.

## 17. Dispatch Packet Validation

For BA fix dispatch packets:

Frontmatter must include:

- `schema_version: 1`
- `message_id`
- `thread_id`
- `from`
- `to`
- `date`
- `subject`
- `type: ba_fix_dispatch`
- `protocol: BA_FIX_DISPATCH_v1.1`

Required sections:

- `## Target`
- `## Totals`
- `## Truth Split`
- `## Bible Coverage Matrix`
- `## What BA Actually Tested`
- `## Receiver Quick Start`
- `## Scope And Boundaries`
- `## Reproduce / Verify Commands`
- `## Finding Index`
- `## Automated Deep Investigation Protocol`
- `## Requested Work`
- `## Expected Response Contract`
- `## Finding Disposition`
- `## Findings`
- `## Machine-Readable Annex`

Annex validation:

1. Annex JSON parses.
2. `protocol == "BA_FIX_DISPATCH_v1.1"`.
3. `target_app` matches frontmatter and report target.
4. `totals` match the report.
5. `truth_split` matches the report.
6. `bible_coverage_matrix` matches the report.
7. `runtime_trust_pack` matches the report.
8. `actionable_count` equals count of findings with status `fail`, `warn`, or `unknown`.
9. Every finding in `Finding Index` appears in annex `findings`.
10. Every annex finding appears in the human findings section.
11. Every actionable finding includes `truth_bucket`, `confidence`, and `primary_evidence`.
12. `response_contract.deferred_finding_required` is true when actionable count is nonzero.
13. The exact deferred-finding rule appears in text when actionable count is nonzero.

Dispatch validation must fail if the human body and annex disagree.

### 17.1 Summary And Test Dispatch Validation

Summary dispatch packets must:

1. Include valid YAML frontmatter.
2. Include `type: ba_summary_dispatch`.
3. Include `protocol: BA_SUMMARY_DISPATCH_v1.0`.
4. State that no actionable findings are present.
5. Omit the automated deep investigation and finding disposition obligations.
6. If they include a machine-readable annex, set `actionable_count` to `0` and `response_contract.deferred_finding_required` to `false`.

Test dispatch packets must:

1. Include valid YAML frontmatter.
2. Include `type: ba_test_dispatch`.
3. Include `protocol: BA_TEST_DISPATCH_v1.0`.
4. State that no work is requested.
5. Omit fix-request language, automated deep investigation obligations, and finding disposition obligations.

Any BA packet that mixes test/summary semantics with fix-dispatch obligations is invalid.

## 18. Progress And History Validation

The validator must optionally inspect:

- `ba_audit_progress.json`
- `ba_audit_history.jsonl`
- `ba_audit_latest.json`

Progress validation:

1. `schema_version == "BA_AUDIT_PROGRESS_v1"`.
2. `target_app` matches latest report target.
3. `progress_percent == 100` for completed reports.
4. `run_state` is compatible with latest report totals.
5. Last progress phase is `Complete`.

History validation:

1. History file exists after at least one persistent BA run.
2. Last history entry target matches latest report target.
3. Last history entry totals match latest report totals.
4. `runner_version` is recorded.
5. `evidence_score_percent` and `coverage_debt_percent` are recorded.

History mismatch is a warning unless the validated report path is the canonical latest report or the report contains auto-dispatch/server-job metadata indicating it came from a persistent server run. In those cases, latest/history/progress disagreement is a validation failure because the persisted artifact chain is part of the trust claim.

## 19. Test Mode Validation

Test Mode is the primary known-answer oracle for scanner correctness.

Validator requirements:

1. Support a `--test-mode` validation mode.
2. Run fixture types:
   - `BIBLE_ERROR`
   - `FORMAT_ERROR`
   - `STRUCTURE_ERROR`
3. Confirm expected count equals detected count.
4. Confirm matched count equals expected count.
5. Confirm `missed` is empty.
6. Confirm `unexpected` is empty.
7. Confirm result schema is `BA_AUDIT_RESULT_v1`.
8. Confirm Test Mode does not write normal latest/history/mailbox outputs.

If Test Mode fails, validator must mark BA scanner reliability as blocked.

## 20. False Positive And Scanner Limitation Handling

The validator must not auto-convert BA findings into app bugs.

For every actionable finding, the validator should assign a disposition hint:

- `confirmed_current`
- `likely_current`
- `heuristic_requires_trace`
- `coverage_gap`
- `stale_or_not_reproduced`
- `invalid_evidence`
- `needs_manual_review`

Default mapping:

- `runtime_check_pack` fail reproduced by PAH Inspector -> `confirmed_current`.
- `runtime_check_pack` fail not reproduced by direct same-URL probe -> `stale_or_not_reproduced`.
- `runtime_action_feedback` fail with screenshot/probe evidence -> `confirmed_current`.
- `runtime_geometry` fail with screenshot/probe evidence -> `confirmed_current`.
- `pg_design_lint` fail -> `likely_current`.
- `app_inventory` missing path -> `likely_current`.
- `action_feedback_static` fail/warn -> `heuristic_requires_trace`.
- `workflow_order_static` unknown/coverage-gap -> `coverage_gap`.
- missing evidence -> `invalid_evidence`.

The validator output must make this distinction visible.

## 21. Required Report Validation Checks

Minimum check IDs:

- `BA-VAL-SCHEMA-0001`: schema version valid
- `BA-VAL-SCHEMA-0002`: required root fields present
- `BA-VAL-SCOPE-0001`: exactly one selected target
- `BA-VAL-TOTALS-0001`: status totals match checks
- `BA-VAL-METRICS-0001`: evidence score formula matches
- `BA-VAL-METRICS-0002`: coverage debt formula matches
- `BA-VAL-TRUTH-0001`: truth buckets match classifier
- `BA-VAL-TRUTH-0002`: confidence values match classifier
- `BA-VAL-EVIDENCE-0001`: evidence paths resolve
- `BA-VAL-EVIDENCE-0002`: evidence line references are valid
- `BA-VAL-RUNTIME-BA-0001`: BA runtime trust pack valid when target is Bible Audit
- `BA-VAL-RUNTIME-PAH-0001`: PAH runtime check pack maps to inspector evidence
- `BA-VAL-FRESHNESS-0001`: report age within policy
- `BA-VAL-REPORTTEXT-0001`: mandatory report truth header present
- `BA-VAL-REPORTTEXT-0002`: report text totals match JSON totals
- `BA-VAL-DISPATCH-0001`: dispatch frontmatter valid
- `BA-VAL-DISPATCH-0002`: dispatch annex parses
- `BA-VAL-DISPATCH-0003`: dispatch annex matches report
- `BA-VAL-DISPATCH-0004`: response contract matches actionable count
- `BA-VAL-REPRO-0001`: reproduction completed
- `BA-VAL-REPRO-0002`: reproduction drift classified
- `BA-VAL-PROFILE-0001`: selected validation profile recorded and applied
- `BA-VAL-TESTMODE-0001`: Test Mode fixtures match expected findings

## 22. Implementation Shape

If approved, implement a new script:

`C:\panda-gallery\scripts\ba_report_validator.py`

Recommended internal modules or functions:

- `load_report(path)`.
- `validate_schema(report)`.
- `validate_scope(report, expected_app)`.
- `validate_totals(report)`.
- `validate_metrics(report)`.
- `validate_truth_split(report)`.
- `validate_evidence(report)`.
- `validate_runtime(report, options)`.
- `validate_freshness(report, options)`.
- `parse_dispatch_packet(path)`.
- `validate_dispatch(packet, report)`.
- `run_reproduction(target_app, options)`.
- `compare_reports(original, reproduced)`.
- `run_test_mode_oracle()`.
- `finalize_validation(checks)`.

The validator should import the BA runner when practical to reuse constants and formulas, but it must not rely blindly on BA functions for the same logic being validated. At minimum, totals, metrics, truth classifier, and dispatch annex comparison should be recomputed independently enough to catch BA regressions.

## 23. CLI Exit Codes

Required exit codes:

- `0`: validation verdict is `report_trusted` or `report_trusted_with_findings`.
- `1`: validation verdict is `diagnostic_only`, `stale_or_drifted`, or `runtime_untrusted`.
- `2`: validation verdict is `schema_invalid`, `evidence_invalid`, `dispatch_invalid`, or `blocked`.

Rationale:

- Exit `0` means the report structure and evidence are trusted, even if it contains app findings.
- Exit `1` means the report is useful but not enough for fix authority.
- Exit `2` means the report or validation process is invalid.

## 24. UI Integration

If UI integration is approved later, the BA applet should expose a validation panel with:

- validation verdict
- schema status
- totals consistency status
- evidence status
- runtime status
- freshness status
- reproduction status
- dispatch annex status
- latest validation timestamp
- link/path to validation JSON

The UI must not hide BA findings behind a green validation badge. A report can be validated and still contain real defects.

Recommended labels:

- `Report trusted`
- `Report trusted with findings`
- `Diagnostic only`
- `Stale or drifted`
- `Evidence invalid`
- `Runtime untrusted`
- `Dispatch invalid`

## 25. Acceptance Criteria

AC-1: Schema validation catches missing required fields.

Evidence: Unit test deletes `truth_split` from a valid report and validator returns `schema_invalid`.

AC-2: Totals validation catches mismatched counts.

Evidence: Unit test changes `totals.fail` without changing `checks`; validator emits `BA-VAL-TOTALS-0001` fail.

AC-3: Metrics validation catches formula drift.

Evidence: Unit test changes `evidence_score_percent`; validator emits `BA-VAL-METRICS-0001` fail.

AC-4: Truth validation catches misclassified `action_feedback_static`.

Evidence: Unit test sets a static action fail to `proven_failures`; validator emits `BA-VAL-TRUTH-0001` fail.

AC-5: Evidence validation catches missing files.

Evidence: Unit test points evidence to a nonexistent path; validator returns `evidence_invalid`.

AC-6: BA runtime trust validation catches missing screenshot artifacts.

Evidence: Unit test removes one runtime screenshot path from a Bible Audit report; validator emits `BA-VAL-RUNTIME-BA-0001` fail.

AC-7: PAH runtime validation uses inspector URL, not hard-coded `8788`.

Evidence: Unit test creates PAH report evidence using `http://127.0.0.1:8765`; validator probes or records that URL and does not probe `8788` unless explicitly configured.

AC-8: Reproduction validation detects runtime drift.

Evidence: Original fixture has endpoint failures; reproduced fixture has endpoint passes; validator returns `stale_or_drifted` with drift category `runtime_environment`.

AC-9: Dispatch validation catches annex/body mismatch.

Evidence: Unit test changes dispatch annex `actionable_count`; validator returns `dispatch_invalid`.

AC-10: Dispatch validation enforces deferred-finding response contract.

Evidence: Actionable fix dispatch without the deferred-finding rule fails; clean summary or test dispatch containing fix-dispatch deferred-finding obligations fails as mixed packet semantics.

AC-11: Test Mode validates known-answer scanner behavior.

Evidence: Validator runs Test Mode with all three fixture types and reports matched count 3, missed 0, unexpected 0.

AC-12: Validator distinguishes trusted report from clean app.

Evidence: Report with real fail findings but valid evidence returns `report_trusted_with_findings`, not `report_trusted`.

AC-13: Validator does not mutate app source.

Evidence: Git status before and after validation shows no source changes except expected BA latest/history artifacts when `--reproduce` is explicitly used.

## 26. Verification Commands For Future Implementation

Minimum implementation verification:

```powershell
cd C:\panda-gallery
python -m py_compile scripts\ba_report_validator.py
python -m pytest tests\test_ba_audit_runner.py -q
python scripts\ba_report_validator.py --report workflows\design\applets\ba_audit_latest.json
python scripts\ba_report_validator.py --report workflows\design\applets\ba_audit_latest.json --reproduce
python scripts\ba_report_validator.py --test-mode
```

Recommended PAH-specific verification when PAH dev is not paused:

```powershell
cd C:\panda-gallery
python scripts\ba_audit_runner.py --app "Panda Agent Hub" --summary
python scripts\ba_report_validator.py --report workflows\design\applets\ba_audit_latest.json --expected-app "Panda Agent Hub" --reproduce
```

## 27. Open Questions

OQ-1: Should the validator be part of BA proper or a separate script?

Recommendation: separate script first, then UI integration.

OQ-2: Should reproduction be default?

Recommendation: no. Default validation should be non-mutating. `--reproduce` should be explicit.

OQ-3: Should dispatch validation require a canonical report path?

Recommendation: yes when available. If not available, validate dispatch internally and mark report cross-check as skipped.

OQ-4: Should validator output be written to BA history?

Recommendation: no for v1. Write a separate validation JSON artifact to avoid mixing audit results and validator results.

OQ-5: Should static heuristic findings ever become trusted defects automatically?

Recommendation: no. They require handler-trace or runtime confirmation.

OQ-6: Should PAH endpoint validation start PAH if it is down?

Recommendation: no for v1. The validator can report PAH down; starting services is a separate operational action.

## 28. Non-Goals And Safety

The validator must not:

- edit app source files
- auto-fix BA findings
- auto-dispatch new BA packets unless explicitly approved by a separate spec
- mark mail read
- archive mail
- delete BA artifacts
- push commits
- claim all-app certification
- hide reproduction drift
- treat heuristic findings as confirmed defects

## 29. Recommended Work Sequence

If Darrin approves implementation later:

1. Implement non-mutating report JSON validation first.
2. Add unit tests for malformed reports.
3. Add dispatch packet validation.
4. Add Test Mode validator oracle.
5. Add explicit reproduction mode.
6. Add PAH runtime URL provenance checks.
7. Add optional BA applet validation panel.
8. Only then consider using the validator as a commit or dispatch gate.

## 30. Definition Of Done

The BA report validation effort is done when:

1. A validator can classify a report as trusted, trusted-with-findings, diagnostic-only, stale/drifted, invalid, or blocked.
2. It catches schema, totals, metrics, truth split, evidence, runtime, freshness, reproduction, and dispatch annex defects.
3. It proves BA Test Mode known-answer fixtures.
4. It correctly handles PAH endpoint drift and wrong-port confusion.
5. It never claims a report is clean just because the report is structurally valid.
6. It has tests for every acceptance criterion.
7. Documentation explains how Darrin, Codex, CD, and CC should interpret each validator verdict.
