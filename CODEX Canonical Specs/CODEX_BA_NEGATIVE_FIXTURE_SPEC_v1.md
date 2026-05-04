# CODEX BA Negative Fixture Spec v1

Status: Implemented in Panda Gallery commit `c5be0cb`
Created: 2026-05-04
Owner: Codex
Project: Panda Gallery / Bible Audit
Spec type: negative-control test fixture and BA calibration design

Canonical spec path:

`C:\CODEX PG\CODEX Canonical Specs\CODEX_BA_NEGATIVE_FIXTURE_SPEC_v1.md`

Primary implementation targets:

- `C:\panda-gallery\scripts\ba_audit_runner.py`
- `C:\panda-gallery\tests\test_ba_audit_runner.py`
- `C:\panda-gallery\tests\test_ba_report_validator.py`
- `C:\panda-gallery\workflows\design\ba_audit_manifest.json`
- New fixture app files under `C:\panda-gallery\workflows\design\ba_negative_fixture\`
- Optional fixture expectation JSON under `C:\panda-gallery\workflows\design\ba_negative_fixture\ba_negative_fixture_expected.json`

Related completed work:

- `C:\panda-gallery\scripts\ba_report_validator.py`
- `C:\panda-gallery\tests\test_ba_report_validator.py`
- `C:\CODEX PG\CODEX Canonical Specs\CODEX_BA_REPORT_VALIDATION_SPEC_v1.md`
- Panda Gallery commit `c5be0cb Add BA report calibration validator`

## 1. Purpose

This spec defines a deliberately flawed BA fixture app, hereafter `BA Negative Fixture`, whose job is to prove that Bible Audit can detect known-bad conditions.

A clean app proves BA can say "pass" when evidence supports pass. A negative fixture proves the other half: BA can say "fail", "warn", or "unknown" when the target contains planted defects.

The fixture is not a product app. It is a calibration target. It should be ugly, small, isolated, deterministic, and safe to run. Its expected BA findings must be explicit enough that a future BA change cannot silently stop detecting a class of mistakes.

## 2. Problem Statement

BA currently has strong evidence that it can validate the selected `Bible Audit` app when BA is clean. That does not automatically prove that each BA scanner still detects its intended failure modes.

Without a negative fixture, BA can regress in dangerous ways:

1. A scanner can stop firing but reports remain clean.
2. A heuristic can become too permissive.
3. Runtime checks can claim coverage while missing visible defects.
4. A report validator can verify internal consistency but still not know whether BA caught all planted defects.
5. Dispatch or Test Mode behavior can pass happy-path tests while losing failure semantics.

The negative fixture is designed to answer:

- Does BA catch each category of mistake it claims to check?
- Does BA correctly label planted mistakes as proven failures, heuristic suspects, coverage gaps, or informational evidence?
- Does BA preserve single-target boundaries when the target itself contains misleading all-app language?
- Does BA avoid treating planted bad fixture content as production debt?
- Does the report validator catch a BA report that misses expected fixture failures?

## 3. Non-Goals

This spec was drafted before implementation. Darrin later approved implementation; v1 was implemented in Panda Gallery commit `c5be0cb`.

This spec does not require BA to detect every possible UI, report, or runtime bug. It covers only the scanner families BA already runs or has explicitly declared in its coverage matrix.

This spec does not require adding negative cases for future scanners before those scanners exist. Future scanner expectations must be appended when the scanner is implemented.

This spec does not let the fake app participate in normal production quality scoring. A negative fixture is expected to fail; its failures are proof that BA is working.

## 4. Definitions

`Negative fixture`: A deliberately flawed app used to prove BA detects known mistakes.

`Planted defect`: A specific intentional mistake in the fixture, mapped to one expected BA finding.

`Expected finding`: A stable expectation that BA should emit a finding with a defined scanner, status, truth bucket, confidence, and message pattern.

`Calibration pass`: BA detects every required expected finding for the fixture and does not emit unexpected severe findings outside the allowed set.

`Calibration failure`: BA misses a required finding, misclassifies it, or emits unexpected severe findings that indicate the fixture or scanner contract has drifted.

`Production audit`: A normal BA run against a real target app. The negative fixture must not affect production audit totals unless selected explicitly.

## 5. Fixture Identity

The fixture app name should be:

`BA Negative Fixture`

The fixture app slug should be:

`ba-negative-fixture`

The fixture should be registered in the BA manifest with an explicit flag:

```json
{
  "app": "BA Negative Fixture",
  "fixture_role": "negative-control",
  "production_excluded": true
}
```

If the existing manifest schema does not accept these fields, implementation must either extend the schema safely or encode the same meaning in a BA-owned metadata field. The selected design must be documented in tests.

Production exclusion must not mean "unselectable." It means:

- excluded from any default production sweep
- excluded from clean-report product claims
- excluded from automatic fix dispatch
- still selectable by explicit calibration command
- optionally visible in the BA UI only when calibration targets are shown

## 6. Isolation Rules

The negative fixture must be isolated from normal app work.

Required isolation rules:

1. It must not be selected by any "all real apps" workflow.
2. It must not affect production BA clean-report claims.
3. It must not auto-dispatch fix requests to Claude Desktop, Claude Code, or Codex.
4. It must not appear as a product app needing repair.
5. It must be runnable only through explicit fixture/calibration commands or explicit selection in the BA UI.
6. Its intentionally bad content must not be used as evidence of debt in `Panda Gallery`, `Bible Audit`, `Panda Agent Hub`, or any other real app.

Recommended display label in BA UI:

`BA Negative Fixture (calibration only)`

## 7. Required Files

The minimum fixture implementation should create:

```text
C:\panda-gallery\workflows\design\ba_negative_fixture\
  BA_Negative_Fixture.html
  BA_Negative_Fixture.py
  ba_negative_fixture_expected.json
  README.md
```

Purpose of each file:

- `BA_Negative_Fixture.html`: Browser-style fixture for BA HTML/static/runtime scanners.
- `BA_Negative_Fixture.py`: Python/PySide-like fixture for static scanner coverage and future PySide runtime adapters.
- `ba_negative_fixture_expected.json`: Machine-readable expected BA results.
- `README.md`: Human warning that every defect is intentional and must not be fixed as production work.

If implementation can cover all current scanners with fewer files, it may do so only if the expected-results file still maps every scanner family to a concrete planted defect or an explicit "not applicable yet" record.

`BA_Negative_Fixture.py` must be inert fixture text unless a future PySide adapter explicitly runs it. It must not open windows, start servers, write files, delete files, send messages, or perform network calls during normal tests. Static scanners may read it as source text.

## 8. Required Expected-Results Contract

The fixture must include a machine-readable expectation file. The file should be treated as the oracle for fixture calibration.

Recommended schema:

```json
{
  "schema_version": "BA_NEGATIVE_FIXTURE_EXPECTED_v1",
  "fixture_app": "BA Negative Fixture",
  "fixture_role": "negative-control",
  "expected_ba_runner_version_min": "1.4.0",
  "expectation_mode": "exact_required_subset",
  "expected_findings": [],
  "allowed_extra_findings": [],
  "must_not_emit": [],
  "production_isolation": {
    "auto_dispatch_allowed": false,
    "production_clean_report_impact_allowed": false
  }
}
```

`expected_findings` rows must include:

```json
{
  "fixture_case_id": "NEG-ACTION-001",
  "scanner": "action_feedback_static",
  "allowed_statuses": ["fail", "warn"],
  "expected_truth_bucket": "heuristic_suspects",
  "expected_confidence": "heuristic",
  "expected_id_pattern": "BA-ACTION-BA-NEGATIVE-FIXTURE-*",
  "expected_message_pattern": "missing visible feedback",
  "source_file": "workflows/design/ba_negative_fixture/BA_Negative_Fixture.html",
  "source_marker": "data-ba-negative-case=\"NEG-ACTION-001\"",
  "reason": "Button has a click handler but no visible status, toast, label change, or timestamp feedback."
}
```

The expectation mode should start as `exact_required_subset`, meaning:

- Every expected finding must appear.
- Extra findings are allowed only if listed in `allowed_extra_findings`.
- Unexpected fail/warn/unknown findings should fail calibration unless explicitly allowed.
- Pass rows may be allowed if they are unrelated informational evidence, but they must not mask missed expected findings.
- During the first implementation baseline, a row may use `allowed_statuses` for scanners whose current severity is heuristic. After the first accepted calibration baseline, the expectation file should be tightened to exact `expected_status` values wherever scanner behavior is stable.

Matching priority:

1. Prefer `fixture_case_id` carried through BA evidence detail when available.
2. Otherwise match by `source_marker` in evidence detail, evidence line text, or nearby source text.
3. Then match by scanner plus source file plus expected message pattern.
4. Treat `expected_id_pattern` as helpful but not the only proof, because BA finding IDs may evolve when scanner names or app slugs change.

## 9. Required Planted Defects by Scanner Family

Scanner-family ownership rule:

- Target-app defects belong in `BA Negative Fixture`.
- Report-artifact defects belong in `ba_report_validator.py` tests.
- Dispatch-routing defects belong in dispatch/validator tests, with the fixture used only as the target label.
- Future runtime adapter defects must stay recorded as `not_applicable_until_adapter` until BA can actually run them against this fixture.

### 9.1 App Inventory

Purpose: prove BA can register and scan the fixture as exactly one selected app.

Planted condition:

- The fixture must contain at least one valid source file and one intentionally referenced missing optional file.

Expected behavior:

- BA should pass inventory for readable fixture files.
- BA should emit a controlled fail/warn/unknown only if the manifest intentionally includes a missing required path.

Default v1 choice:

- Do not plant a missing required manifest path in v1. Use inventory as a control pass, not a defect, because a missing required path can block other scanners.

Required expectation:

- One `app_inventory` pass confirming the fixture was selected and scanned.

### 9.2 Static Action Feedback

Purpose: prove BA detects controls that appear interactive but do not provide visible user feedback.

Planted defects:

1. Button with click handler but no status text, toast, timestamp, label change, disabled state, or visible output.
2. Button with a handler that only writes to `console.log`.
3. Button with a handler that changes hidden state only.

Expected behavior:

- BA should emit action-feedback fail or warn rows for each planted control.
- Expected truth bucket should be `heuristic_suspects` unless BA has runtime proof.
- Expected confidence should be `heuristic`.

Example markers:

```html
<button id="neg-no-feedback" data-ba-negative-case="NEG-ACTION-001">Run Silent</button>
<button id="neg-console-only" data-ba-negative-case="NEG-ACTION-002">Console Only</button>
<button id="neg-hidden-only" data-ba-negative-case="NEG-ACTION-003">Hidden Only</button>
```

### 9.3 Workflow Order Static

Purpose: prove BA detects out-of-order or malformed workflow ordering markers.

Planted defects:

1. A workflow group whose `data-workflow-order` values decrease.
2. Duplicate order values where the scanner expects strict order.
3. A required step label missing from the declared flow.

Expected behavior:

- BA should emit fail/warn/unknown rows from `workflow_order_static`.
- Expected truth bucket should be `coverage_gaps` if BA cannot prove visual order, or `proven_failures` if the scanner deterministically detects malformed declared order.

The expected file must specify which classification is required once implementation confirms current BA behavior.

### 9.4 Forbidden Language / BA Self-Integrity

Purpose: prove BA detects legacy blanket language and fake all-app claims.

Planted defects:

1. Visible text: `All Panda Apps are certified`.
2. Visible text or comment resembling old fake report language, such as `All Panda Apps is clean`.
3. A fake hardcoded pass marker similar to `check(true)`.

Expected behavior:

- BA should emit deterministic fail rows for forbidden legacy tokens if this scanner is enabled for the fixture.
- Expected truth bucket should be `proven_failures`.
- Expected confidence should be `high`.

Scanner naming rule:

- If implementation keeps this logic inside the existing `ba_self_integrity` scanner, the expected-results file may use `ba_self_integrity`.
- If implementation splits this into target-app scanning, the scanner should be named `forbidden_language_static`.
- The expectation file must record the actual scanner name used by BA; calibration should not accept either name silently unless both are explicitly listed in `allowed_scanners`.

Important ambiguity rule:

- The fixture may contain forbidden phrases as planted defects.
- BA report validation must still allow BA's own evidence phrase saying a forbidden token "is absent" in clean BA reports. The negative fixture must not reintroduce the earlier false positive where absence proof is mistaken for a blanket claim.

### 9.5 Runtime Action Feedback

Purpose: prove BA runtime probes can catch visible behavior failures, not only static wiring failures.

Current limitation:

- BA runtime action feedback currently browser-probes Bible Audit controls only.
- The negative fixture should not claim runtime action calibration until BA supports runtime probing for this fixture target.

V1 requirement:

- Add a non-app expectation row with mode `not_applicable_until_adapter`; do not put this row in `expected_findings`, because no BA finding is expected until an adapter exists.
- Do not require runtime action feedback defects to be detected until a fixture runtime adapter exists.

Future requirement once adapter exists:

- Button that can be clicked but produces no visible feedback.
- Button that shows feedback only outside the viewport.
- Button that changes text too briefly to observe under the configured timeout.

Expected behavior after adapter:

- Runtime scanner emits fail/warn rows with concrete runtime evidence, screenshots, selector, viewport, and URL.
- Truth bucket should be `proven_failures` or `heuristic_suspects` according to BA's runtime scanner contract.

### 9.6 Runtime Geometry

Purpose: prove BA detects clipping, overlap, overflow, and hidden controls when runtime geometry scanning supports the fixture.

Current limitation:

- BA runtime geometry currently browser-probes Bible Audit only at `1920x1080` and `1000x900`.

V1 requirement:

- Add a non-app expectation row with mode `not_applicable_until_adapter`; do not put this row in `expected_findings`, because no BA finding is expected until an adapter exists.

Future planted defects:

1. Horizontal page overflow.
2. Button partly outside viewport.
3. Text clipped inside fixed-width button.
4. Overlay that covers a critical control.
5. Help/modal close button outside viewport.

Expected behavior after adapter:

- Runtime geometry scanner emits fail/warn rows with screenshot evidence.
- Runtime Trust Pack includes non-empty screenshots for each configured viewport and stage.

### 9.7 Report Consistency

Purpose: prove BA catches report totals or report text mismatches.

Important design constraint:

- The fixture app should not directly mutate BA's generated report totals. That belongs to `ba_report_validator.py`, not to the target app fixture.

V1 requirement:

- Keep report consistency negative cases in validator tests, not in the app fixture.
- The expected-results file should include a `not_applicable_in_target_fixture` row explaining that report consistency is tested by synthetic report validator fixtures.

### 9.8 Staleness

Purpose: prove stale timestamps are rejected.

Important design constraint:

- Staleness is a report artifact property, not a target app behavior.

V1 requirement:

- Keep stale-report negative cases in validator tests.
- Do not put stale timestamp behavior inside `BA Negative Fixture` unless BA later supports fixture-level synthetic report generation.

### 9.9 Truth Split and Confidence Classification

Purpose: prove BA classifies planted defects correctly.

Required expectations:

- Deterministic forbidden-token findings should classify as `proven_failures` with `high` confidence.
- Static action-feedback findings should classify as `heuristic_suspects` with `heuristic` confidence unless runtime-confirmed.
- Unsupported/future runtime adapter expectations should classify as fixture calibration gaps, not production unknowns.
- Informational inventory pass should classify as `informational_evidence`.

Calibration must fail if BA detects a planted defect but assigns the wrong truth bucket or confidence class.

If the first implementation discovers that the current scanner cannot produce a deterministic truth bucket for a planted defect, the expectation may temporarily use `allowed_truth_buckets` with a tracking note. The long-term target is exact classification for every stable scanner.

### 9.10 Dispatch and Auto-Dispatch

Purpose: prevent fixture failures from becoming accidental real work packets.

Required behavior:

- The negative fixture must not auto-dispatch fix packets by default.
- If a dispatch packet is generated manually for the fixture, it must be labeled calibration-only.
- The dispatch body must state that planted defects are intentional and must not be fixed as production bugs.
- The machine-readable annex must include `fixture_role: negative-control` or equivalent metadata.
- A manual fixture dispatch must never be addressed as a normal "please fix this app" task. It is either a calibration summary or a request to improve BA itself.

Expected behavior:

- BA should either block auto-dispatch for this fixture or convert it into a calibration summary packet.
- `ba_report_validator.py` should reject a normal fix dispatch for `BA Negative Fixture` unless it contains calibration-only metadata.

## 10. Fixture Calibration Algorithm

Implementation should add a calibration helper, conceptually:

```text
python scripts\ba_audit_runner.py --app "BA Negative Fixture" --calibrate-negative-fixture
```

or a separate script:

```text
python scripts\ba_negative_fixture_calibrator.py
```

The helper should:

1. Run BA against `BA Negative Fixture`.
2. Load `ba_negative_fixture_expected.json`.
3. Compare BA findings to expected findings.
4. Fail if any expected finding is missing.
5. Fail if any expected finding has the wrong status, scanner, truth bucket, or confidence.
6. Fail if an unexpected actionable finding appears and is not listed in `allowed_extra_findings`.
7. Fail if the fixture produces a production-style fix dispatch.
8. Emit a compact calibration report with:
   - calibration verdict
   - matched expected findings
   - missed expected findings
   - unexpected findings
   - scanner classifications
   - isolation checks

The helper must return a non-zero exit code for every verdict except `fixture_calibrated`.

Recommended exit codes:

- `0`: `fixture_calibrated`
- `1`: missed, unexpected, or misclassified findings
- `2`: blocked run, invalid expectation file, invalid BA report, or isolation failure

The helper must print a compact summary by default. Full JSON should require an explicit `--json` or `--output` argument to avoid oversized tool output.

Recommended calibration verdicts:

- `fixture_calibrated`
- `fixture_missed_expected_findings`
- `fixture_unexpected_findings`
- `fixture_misclassified_findings`
- `fixture_isolation_failed`
- `fixture_blocked`

## 11. Relationship to `ba_report_validator.py`

`ba_report_validator.py` validates whether a BA report is structurally trustworthy.

The negative fixture validates whether BA detected planted bad app behavior.

These are related but not interchangeable.

Required integration:

1. `ba_report_validator.py` should support an optional expected-results input:

   ```text
   python scripts\ba_report_validator.py --report workflows\design\applets\ba_audit_latest.json --expected-fixture workflows\design\ba_negative_fixture\ba_negative_fixture_expected.json
   ```

2. When `--expected-fixture` is supplied, the validator should:
   - run normal report validation first
   - verify target app equals `BA Negative Fixture`
   - compare findings against the fixture expectation file
   - use fixture calibration verdicts when expected findings are missed

3. A fixture report can be structurally valid while still failing calibration. Example:
   - JSON totals match.
   - Evidence paths exist.
   - Runtime trust pack is honest.
   - But BA missed `NEG-ACTION-001`.
   - Result should be `fixture_missed_expected_findings`, not `report_trusted`.

4. The validator must not require runtime screenshots for `BA Negative Fixture` in v1 unless the report claims `runtime_trusted` for the fixture. A fixture report with no runtime adapter should be honest as `runtime_not_applicable`, not failed for missing runtime screenshots.

## 12. BA UI Behavior

If the fixture appears in the BA UI app selector:

- It must be visually labeled as calibration-only.
- Selecting it should not imply production app repair work.
- Auto-send controls should be disabled or ignored for this target.
- The report header should clearly say:

```text
Target: BA Negative Fixture. Calibration fixture: expected to fail.
```

The UI should still show normal report sections so humans can inspect scanner output.

## 13. Test Requirements

Implementation must add tests for:

1. The fixture is registered and selectable only as a calibration target.
2. Production app lists exclude the fixture unless calibration mode is active.
3. BA detects each v1 static planted defect.
4. BA emits the expected scanner, status, truth bucket, and confidence for each required finding.
5. BA fails calibration when one expected finding is removed from a synthetic report.
6. BA fails calibration when a finding is present but misclassified.
7. BA fails calibration when unexpected actionable findings appear.
8. BA blocks or relabels auto-dispatch for the fixture.
9. `ba_report_validator.py --expected-fixture` rejects structurally valid reports that miss planted defects.
10. Clean `Bible Audit` reports remain unaffected by the negative fixture.

Test names should be explicit enough to explain the contract. Example:

```text
test_ba_negative_fixture_catches_static_action_feedback_failures
test_ba_negative_fixture_catches_forbidden_all_app_language
test_ba_negative_fixture_does_not_auto_dispatch_fix_packets
test_ba_report_validator_rejects_fixture_report_with_missing_expected_finding
```

## 14. Safety Rules

Implementation must include a README or file header warning:

```text
This app is intentionally broken. Do not fix these defects as product bugs.
It exists only to calibrate Bible Audit scanners.
```

The planted defects must be obvious and marked with stable IDs:

```html
data-ba-negative-case="NEG-ACTION-001"
```

or:

```python
# BA_NEGATIVE_CASE: NEG-PYSIDE-001
```

No fixture defect should perform destructive actions, network writes, credential access, filesystem deletion, or real mailbox dispatch.

## 15. Acceptance Criteria

The spec is implemented correctly when:

1. `BA Negative Fixture` can be selected explicitly.
2. BA emits expected findings for every v1 required planted defect.
3. Calibration fails if an expected finding is missing.
4. Calibration fails if an expected finding is misclassified.
5. Calibration fails if unexpected actionable findings appear.
6. Fixture dispatch is blocked or clearly marked calibration-only.
7. Normal `Bible Audit` clean reports still validate as trusted.
8. The fixture does not alter production app audit totals.
9. Tests prove both the passing calibration case and at least three failing calibration cases.

Minimum verification commands:

```powershell
cd C:\panda-gallery
python -m pytest tests\test_ba_audit_runner.py tests\test_ba_report_validator.py -q
python scripts\ba_audit_runner.py --app "BA Negative Fixture" --calibrate-negative-fixture
python scripts\ba_report_validator.py --report workflows\design\applets\ba_audit_latest.json --expected-app "BA Negative Fixture" --expected-fixture workflows\design\ba_negative_fixture\ba_negative_fixture_expected.json
python scripts\ba_audit_runner.py --app "Bible Audit" --summary
python scripts\ba_report_validator.py --report workflows\design\applets\ba_audit_latest.json --expected-app "Bible Audit"
```

If implementation chooses a separate calibrator script, substitute that script for the `--calibrate-negative-fixture` command and document the final command in this spec before handoff.

## 16. Initial v1 Expected Finding Set

The initial v1 set should avoid future/runtime adapters that BA does not yet support for this fixture.

Required v1 expected findings:

| Case ID | Scanner | Allowed Statuses | Allowed Truth Buckets | Allowed Confidence | Purpose |
|---|---|---:|---|---|---|
| NEG-INV-001 | app_inventory | pass | informational_evidence | informational | Fixture selected and scanned. |
| NEG-ACTION-001 | action_feedback_static | fail or warn | heuristic_suspects | heuristic | Click handler has no visible feedback. |
| NEG-ACTION-002 | action_feedback_static | fail or warn | heuristic_suspects | heuristic | Handler logs only to console. |
| NEG-ACTION-003 | action_feedback_static | fail or warn | heuristic_suspects | heuristic | Handler updates hidden state only. |
| NEG-WORKFLOW-001 | workflow_order_static | fail or warn | allowed set: proven_failures, coverage_gaps | allowed set: high, coverage_gap | Declared workflow order decreases; tighten after first baseline. |
| NEG-WORKFLOW-002 | workflow_order_static | fail or warn | allowed set: proven_failures, coverage_gaps | allowed set: high, coverage_gap | Duplicate workflow order where strict order is expected; tighten after first baseline. |
| NEG-SELF-001 | forbidden_language_static or ba_self_integrity | fail | proven_failures | high | Visible blanket all-app certification language. |
| NEG-SELF-002 | forbidden_language_static or ba_self_integrity | fail | proven_failures | high | Fake hardcoded pass marker. |

Explicit v1 non-app expectations:

| Case ID | Area | Expected Mode | Reason |
|---|---|---|---|
| NEG-RUNTIME-ACTION-ADAPTER | runtime_action_feedback | not_applicable_until_adapter | Runtime action feedback currently probes Bible Audit only. |
| NEG-RUNTIME-GEOMETRY-ADAPTER | runtime_geometry | not_applicable_until_adapter | Runtime geometry currently probes Bible Audit only. |
| NEG-REPORT-CONSISTENCY | report_consistency | validator_test_only | Report consistency is a report artifact, not target app content. |
| NEG-STALENESS | staleness | validator_test_only | Staleness is a report timestamp artifact, not target app content. |

## 17. Open Decisions for Darrin

1. Should the fixture be visible in the BA UI by default with a calibration label, or hidden behind a calibration toggle?
2. Should calibration be run as part of every BA test suite, or only in a targeted test command?
3. Should fixture failures use exact statuses, or allow either fail/warn where BA scanner semantics are currently heuristic?
4. Should BA block fixture dispatch completely, or allow calibration-only summary packets?

## 18. Recommended Implementation Order

1. Add fixture files with stable case markers and README warning.
2. Add manifest registration with calibration-only metadata.
3. Add expected-results JSON.
4. Add calibration comparator in tests first.
5. Update BA scanner logic only where required to detect the planted static defects.
6. Add `ba_report_validator.py --expected-fixture`.
7. Add dispatch isolation behavior.
8. Run full BA tests and a calibration run.
9. Validate clean `Bible Audit` latest report remains trusted.

## 19. Plain-Language Summary

Build one fake app that is intentionally bad.

Tell BA exactly which mistakes are planted.

Run BA against the fake app.

BA passes calibration only if it catches the planted mistakes and labels them honestly.

If BA misses one, the problem is BA, not the fake app.

The fake app must be fenced off so nobody treats its intentional defects as real production bugs.
