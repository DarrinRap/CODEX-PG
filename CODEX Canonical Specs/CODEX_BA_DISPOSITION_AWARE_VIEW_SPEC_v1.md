# CODEX BA Disposition-Aware View Spec v1

Status: Draft for Darrin review
Created: 2026-05-03
Owner: Codex
Project: Panda Gallery / Bible Audit
Spec type: reviewed-finding disposition overlay

Canonical spec path:

`C:\CODEX PG\CODEX Canonical Specs\CODEX_BA_DISPOSITION_AWARE_VIEW_SPEC_v1.md`

Primary implementation targets if approved later:

- `C:\panda-gallery\scripts\ba_audit_runner.py`
- `C:\panda-gallery\scripts\ba_report_validator.py`
- `C:\panda-gallery\workflows\design\applets\PG_Design_Bible_Audit_v1.html`
- `C:\panda-gallery\tests\test_ba_audit_runner.py`
- `C:\panda-gallery\tests\test_ba_report_validator.py`
- Optional future project-side disposition file under `C:\panda-gallery\workflows\design\applets\`

Reference artifacts:

- `C:\CODEX PG\CODEX BA Disposition Ledger\CODEX_BA_DISPOSITION_LEDGER.json`
- `C:\CODEX PG\CODEX Canonical Specs\CODEX_BA_REPORT_VALIDATION_SPEC_v1.md`
- `C:\panda-gallery\workflows\design\BA_APP_REGISTRY_SPEC_v1.2.1.md`
- `C:\panda-gallery\workflows\design\applets\ba_audit_latest.json`
- Vellum / `PG Design Ledger` BA investigation from 2026-05-03

## 1. Purpose

Bible Audit currently reports raw scanner findings. After human/Codex investigation, some findings may be confirmed defects, false positives, coverage gaps, accepted risks, or low-priority cleanup candidates.

This spec defines a disposition-aware layer so BA can show both:

1. Raw scanner counts: what BA saw.
2. Active reviewed counts: what still needs action after investigation.

The goal is to reduce repeat panic and repeat investigation without hiding raw evidence.

## 2. Core Principle

Raw BA reports must remain immutable evidence.

Disposition data is an overlay. It must never erase, rewrite, or silently downgrade the original BA result.

Every view that uses dispositions must clearly separate:

- `Raw BA`: original pass/fail/warn/unknown/evidenced counts.
- `Reviewed overlay`: human/Codex disposition labels.
- `Active remaining`: unresolved confirmed or unreviewed work.

## 3. In Scope

- Disposition schema for BA finding review.
- Merging a raw BA report with disposition entries.
- Adjusted summary counts.
- UI display for investigated flags.
- CLI/validator summary output for disposition-aware reports.
- Guardrails that prevent false claims such as “all clean” when only findings were dispositioned.
- Tests for matching, stale disposition detection, count math, and UI wording.

## 4. Out of Scope

- Auto-fixing app code.
- Auto-closing mailbox dispatches.
- Changing BA scanner behavior in this pass.
- Deleting or mutating raw BA report history.
- Treating dispositioned findings as proof that an app is perfect.
- Continuous background monitoring of BA reports.
- Resolving Relay dirty work.

## 5. Terms

`Raw finding` means one check row from a BA report.

`Disposition` means a reviewed judgment attached to a raw finding or finding group.

`Disposition ledger` means a JSON file containing reviewed judgments.

`Active urgent finding` means a raw fail/warn that remains unresolved after dispositions are applied. Coverage gaps and cleanup candidates remain visible work buckets, but they are not urgent confirmed failures.

`Confirmed issue` means a finding dispositioned as `confirmed_issue`; it can become a fix task after normal approval/spec rules.

`Cleanup candidate` means a finding that appears real but low-risk and should be handled in a future scoped cleanup spec, not as urgent breakage.

`Coverage gap` means BA cannot prove the behavior or layout. It is not a pass and not a confirmed defect.

## 6. Disposition Values

Allowed values:

- `new`
- `investigating`
- `confirmed_issue`
- `false_positive`
- `coverage_gap`
- `investigated_no_action`
- `parked`
- `fixed`
- `accepted_risk`
- `cleanup_candidate`

Meanings:

`new`: no review has happened yet.

`investigating`: review is in progress.

`confirmed_issue`: investigation confirmed that the finding represents a real problem.

`false_positive`: investigation showed BA flagged something that is not a real problem.

`coverage_gap`: BA lacks enough evidence or runtime capability to prove the claim.

`investigated_no_action`: reviewed and not worth action now; not necessarily a scanner bug.

`parked`: valid enough to retain but blocked by scope, paused area, ownership, or timing.

`fixed`: resolved by a later code/spec change and verified.

`accepted_risk`: known issue intentionally accepted by Darrin or an approved spec.

`cleanup_candidate`: likely real but low-risk; should be grouped into a future cleanup spec.

## 7. Ledger Schema

A disposition ledger must be JSON with this shape:

```json
{
  "schema_version": "CODEX_BA_DISPOSITION_LEDGER_v1",
  "created_at": "2026-05-03T20:55:00-07:00",
  "updated_at": "2026-05-03T20:55:00-07:00",
  "purpose": "Human/Codex disposition layer for BA findings.",
  "source_report": "C:\\panda-gallery\\workflows\\design\\applets\\ba_audit_latest.json",
  "source_report_generated_at": "2026-05-03T20:51:00-07:00",
  "source_report_target_app": "PG Design Ledger",
  "source_runner_version": "1.4.0",
  "app_aliases": {
    "PG Design Ledger": "Vellum"
  },
  "disposition_values": ["new", "investigating", "confirmed_issue", "false_positive", "coverage_gap", "investigated_no_action", "parked", "fixed", "accepted_risk", "cleanup_candidate"],
  "entries": []
}
```

Each entry must include:

```json
{
  "finding_id": "BA-ACTION-PG-DESIGN-LEDGER-0008",
  "app": "Vellum",
  "ba_target": "PG Design Ledger",
  "original_status": "fail",
  "scanner": "action_feedback_static",
  "disposition": "false_positive",
  "confidence": "high",
  "reviewed_by": "Codex",
  "reviewed_at": "2026-05-03T20:55:00-07:00",
  "evidence_reviewed": ["panda_ledger/styles.py:203"],
  "finding_fingerprint": "scanner+finding_id+target+primary_evidence_path+primary_evidence_line+message_hash",
  "reason": "BA matched QPushButton inside generated QSS stylesheet text.",
  "recommended_next_action": "Improve BA scanner; no Vellum app-code fix."
}
```

Required matching metadata:

- Top-level `source_report_generated_at`, `source_report_target_app`, and `source_runner_version` when available.
- Entry-level `finding_fingerprint`, derived from scanner, finding ID, target, primary evidence path, primary evidence line, and message hash.

Optional fields:

- `expires_at`: when the disposition should be reconsidered.
- `review_source`: chat, mailbox message, PR, test artifact, or manual note.
- `superseded_by`: finding ID or disposition entry that replaced this entry.
- `verification_command`: command used to confirm a fix or reproduce behavior.

## 8. Matching Rules

A disposition entry may match a finding by exact `finding_id` or by a grouped ID pattern ending in `*`.

Exact match examples:

- `BA-ACTION-PG-DESIGN-LEDGER-0008`

Grouped match examples:

- `BA-WORKFLOW-ORDER-PG-DESIGN-LEDGER-*`
- `BA-LINT-PG-DESIGN-LEDGER-0024/0025/0026/0027`

Slash-group IDs are ledger shorthand only. Implementations must expand slash groups into the listed exact finding IDs before applying count math.

Matching must also check:

- selected BA target or app alias,
- scanner,
- original status when present,
- evidence path when present.

If a finding ID matches but the evidence path, evidence line, target, scanner, or message hash changed, BA must mark the disposition as `stale_disposition` instead of applying it silently.

If multiple dispositions match the same finding, exact ID wins over grouped ID. If two exact entries match, the newest non-superseded entry wins and the UI must expose a duplicate-disposition warning.

## 9. Adjusted Count Rules

BA must continue to show raw totals exactly as produced by the scanner.

Disposition-aware summaries add these separate counts:

- `active_confirmed_issues`
- `active_unreviewed_fails`
- `active_unreviewed_warnings`
- `active_cleanup_candidates`
- `coverage_gaps`
- `false_positives`
- `investigated_no_action`
- `parked`
- `accepted_risk`
- `fixed`
- `stale_dispositions`

A raw fail with disposition `false_positive` is removed from active fail count but remains in raw fail count.

A raw fail with disposition `investigated_no_action` is removed from active fail count but remains visible under reviewed/no-action.

A raw fail or warning with disposition `cleanup_candidate` is not an active urgent failure; it is counted under cleanup candidates and remains eligible for a future scoped cleanup spec.

A raw unknown with disposition `coverage_gap` remains a coverage gap and must not become a pass.

A raw fail/warn with disposition `confirmed_issue` remains active until fixed or accepted.

## 10. UI Requirements

The BA applet must display three summary bands for a selected report:

1. Raw BA counts.
2. Reviewed overlay counts.
3. Active remaining counts.

Example:

```text
Raw BA: 2 fail / 15 warn / 35 unknown / 14 evidenced
Reviewed overlay: 2 fails dispositioned, 15 warnings reviewed/grouped, 35 coverage gaps
Active remaining: 0 confirmed issues / 0 unreviewed fails / 0 unreviewed warnings / 3 cleanup candidates
```

Each finding row must show a disposition chip when one applies.

Disposition chips must not look like action buttons. They are status labels.

Suggested chip text:

- `False positive`
- `Investigated - no action`
- `Coverage gap`
- `Cleanup candidate`
- `Parked`
- `Confirmed issue`
- `Fixed`

Rows with stale dispositions must show `Disposition stale` and remain active until reviewed again.

The UI must include a filter for:

- all raw findings,
- active only,
- confirmed issues,
- cleanup candidates,
- false positives,
- coverage gaps,
- stale dispositions.

## 11. CLI / Validator Requirements

The validator should accept an optional disposition ledger path:

```powershell
python scripts\ba_report_validator.py --report workflows\design\applets\ba_audit_latest.json --expected-app "PG Design Ledger" --dispositions path\to\ledger.json
```

The validator output should add:

```json
{
  "disposition_overlay": {
    "ledger_path": "...",
    "entries_loaded": 11,
    "entries_applied": 11,
    "findings_covered": 52,
    "stale_dispositions": 0,
    "active_remaining": {
      "confirmed_issues": 0,
      "unreviewed_fails": 0,
      "unreviewed_warnings": 0,
      "cleanup_candidates": 3
    }
  }
}
```

`entries_applied` counts ledger entries. `findings_covered` counts raw BA rows matched by exact or grouped dispositions. The validator must not change `validation_verdict` from `report_trusted_with_findings` to `report_trusted` just because findings were dispositioned. A cleaner phrase such as `report_trusted_with_dispositioned_findings` may be added later, but the raw report still contains findings.

## 12. Storage Location

For current Codex-side investigation, the ledger lives under:

`C:\CODEX PG\CODEX BA Disposition Ledger\`

For production BA use, no Panda Gallery write is authorized by this spec. A future approved implementation should choose one of these storage models:

1. Keep the ledger project-local and ignored unless Darrin chooses to share it.
2. Store a reviewed team ledger under `C:\panda-gallery\workflows\design\applets\` only after explicit approval.

No implementation may silently copy Codex-side dispositions into Panda Gallery.

## 13. Vellum Baseline Example

The first reviewed target is Vellum, currently named `PG Design Ledger` in BA.

Raw BA result:

```text
2 fail / 15 warn / 35 unknown / 14 evidenced
```

Reviewed outcome:

- `BA-ACTION-PG-DESIGN-LEDGER-0001`: investigated no action.
- `BA-ACTION-PG-DESIGN-LEDGER-0008`: false positive.
- `BA-ACTION-PG-DESIGN-LEDGER-0002`: investigated no action.
- `BA-ACTION-PG-DESIGN-LEDGER-0009`: investigated no action.
- spacing/radius lint rows: cleanup candidates.
- centralized token/font placeholder rows: investigated no action or scanner context issue.
- PySide workflow order rows: coverage gaps.

Adjusted active result:

```text
0 confirmed issues
0 unreviewed fails
0 unreviewed warnings
3 cleanup candidate groups
35 coverage/context gaps
```

This adjusted result must not be phrased as `Vellum passed BA`. Better wording:

`Vellum BA findings have been reviewed; no urgent confirmed defects remain, with cleanup candidates and coverage gaps tracked.`

## 14. Safety Rules

- Do not hide raw fail/warn/unknown counts.
- Do not convert unknowns into passes.
- Do not auto-fix anything from a disposition.
- Do not use dispositions as commit authorization.
- Do not apply dispositions across apps unless the app alias is explicit.
- Do not apply stale dispositions silently.
- Do not treat a false positive as proof that the scanner is useless.
- Do not treat cleanup candidates as emergencies.

## 15. Tests Required Before Implementation Is Complete

Minimum tests:

1. Exact finding ID disposition applies correctly.
2. Grouped wildcard disposition applies correctly.
3. Exact finding beats wildcard finding.
4. Evidence path drift marks disposition stale.
5. Raw counts remain unchanged.
6. Active counts exclude false positives and investigated-no-action rows.
7. Cleanup candidates are counted separately from urgent failures.
8. Coverage gaps remain not-pass.
9. Validator output includes disposition overlay summary.
10. UI renders raw and adjusted bands with no misleading `all clean` language.
11. Vellum sample ledger produces 0 active urgent failures and 3 cleanup candidate groups.

## 16. Acceptance Criteria

A future implementation is acceptable only if:

- BA still runs single-target only.
- Raw report files remain unchanged by disposition overlay logic.
- Validator can load a disposition ledger and report active remaining counts.
- BA UI can show investigated flags and active remaining counts.
- Vellum reviewed findings display as dispositioned, not raw unresolved failures.
- Stale or conflicting dispositions are visible.
- Tests cover count math and misleading-language prevention.
- Documentation explains that dispositioned does not mean perfect.

## 17. Non-Authorization Notice

This spec does not authorize implementation or edits to `C:\panda-gallery`. It is a vetted-spec candidate. Implementation requires Darrin approval and should be scoped separately.




