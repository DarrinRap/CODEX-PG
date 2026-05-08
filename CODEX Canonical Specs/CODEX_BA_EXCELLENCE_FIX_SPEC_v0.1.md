# CODEX BA Excellence Fix Spec v0.1

Created: 2026-05-06
Owner: Codex draft for Darrin/CD review
Scope: BA tooling reliability, F2 exit-code handling, BA gate cleanup order, and validation discipline
Status: Draft, not dispatched, not approved

## 1. Purpose

BA should become a reliable truth system, not just a report generator. This spec defines the narrow fixes needed before Codex can honestly call BA excellent: correct the BA QA F2 exit-code interpretation, make BA gate output easier to trust, and clean gates in smallest-win order without broad unrelated refactors.

## 2. Current Evidence

Recent validation and mail show:

- `tests/test_ba_audit_runner.py` passed: 51 tests.
- `audit_module/v1/tests/test_render_smoke.py` passed: 24 tests.
- BA calibration fixture passed.
- AM font audit passed with UTF-8 output: 0 font/height issues.
- `Panda Agent Hub` BA gate passed with warnings/unknowns.
- `PANDA Collaborator` BA gate passed with one unknown.
- Earlier validation showed `Bible Audit`, `PG Design Ledger`, `Tracker`, `Inspector`, `Audit Module`, and `Panda Gallery` with BA gate failures or heavy unknown/warn debt. Newer CC diagnostic evidence says `Bible Audit` can currently report `0 fail / 0 warn / 2 unknown`, so the remaining issue there may now be unknown/evidence debt rather than active fail findings.
- CC diagnosed BA QA F2: `ba_audit_runner.py` exit code 1 means audit completed and found fail findings, not subprocess crash.
- Current `ba_qa_tool` logic treats any non-zero runner return code as an error, which can misreport a valid audit result as panel failure.

## 3. Non-Goals

- Do not rewrite the BA runner architecture.
- Do not relax BA gates to make results look better.
- Do not hide fail/warn/unknown findings.
- Do not touch Relay files.
- Do not modify parked dirty files or UI/UX artifacts unrelated to BA.
- Do not make any UI or UX change unless CC/CD first present a mockup to Darrin and Darrin explicitly approves it.
- Do not send implementation-go or commit-go directly from Codex to CC.
- Do not combine large target cleanups into one unfocused patch.

## 4. Required Fixes

### 4.1 BA QA F2 Exit-Code Handling

`ba_audit_runner.py` uses exit code 1 to signal a completed audit with fail findings. `ba_qa_tool` must treat return codes as:

- `0`: audit completed with no fail findings.
- `1`: audit completed with fail findings; read and diff `ba_audit_latest.json` as normal.
- `2+` or negative: subprocess/tool failure; surface as error.

Preferred implementation:

```python
if completed.returncode not in (0, 1):
    raise RuntimeError(...)
```

Then rely on the latest JSON path only after proving it was produced by the current runner invocation. A minimal freshness check is required: capture start time before invoking the runner and reject `ba_audit_latest.json` if its write time is older than that start time. Do not add a large freshness subsystem beyond this guard.

Tests:

- Return code 1 with valid latest JSON is handled as audit findings, not subprocess error.
- Return code 2 still raises the existing subprocess-error path.
- F2 regression diff still detects new fail findings.
- Panel renders F2 fail/warn/pass/error states accurately.

### 4.2 BA Gate Truthfulness

BA output must distinguish:

- tool/runtime failure,
- audit completed with findings,
- audit completed with no findings,
- unknown/evidence-debt findings.

Do not collapse these into one `ERROR` label. User-facing panel labels should make it clear whether the tool crashed or the audit found problems.

### 4.3 Cleanup Order

Fix BA gates in smallest-win order:

1. `Bible Audit` first, because it currently has the smallest blocker surface and owns the audit UI trust surface.
2. `PG Design Ledger` second, because it has low fail count but high unknown debt.
3. `Tracker` and `Inspector` next, because they are active workflow tools.
4. `Audit Module` and `Panda Gallery` after smaller gates are stable, because they have larger fail/warn surfaces.

Each target should get its own Step 0, patch, verification, and commit decision. Do not batch unrelated targets.

### 4.4 Evidence Debt Rules

A target is not excellent if it passes only because findings are unknown or unproven. For each target, report:

- fail count,
- warn count,
- unknown count,
- evidence score,
- coverage debt,
- top five blocker findings,
- whether blockers are product defects, test/audit defects, or missing evidence.

### 4.5 Validation Requirements

For any BA fix, run the narrow relevant tests plus a gate check for the touched target. For the first two priority targets, expected commands are:

```powershell
python -m pytest "C:\panda-gallery\tests\test_ba_audit_runner.py"
python -m pytest "C:\panda-gallery\tests\test_ba_qa_tool.py"
python "C:\panda-gallery\scripts\ba_audit_runner.py" --app "Bible Audit" --summary --gate
python "C:\panda-gallery\scripts\ba_audit_runner.py" --app "PG Design Ledger" --summary --gate
```

If a command is expected to exit 1 because a BA gate found fail findings, capture that as an audit failure, not as a command/runtime failure.

## 5. CC/CD Protocol

Codex may draft specs, audit results, and recommendations. CC implementation must be authorized by CD. If Darrin approves this spec in Codex chat, Codex must route the approval to CD inbox and wait for CD to issue any formal CC implementation/commit token.

## 6. Acceptance Criteria

BA is not excellent until:

- BA QA F2 no longer mislabels runner exit code 1 as subprocess failure.
- Bible Audit gate is clean or remaining findings are explicitly accepted with evidence.
- PG Design Ledger has no fail findings and materially reduced unknown debt.
- Active workflow targets have documented blocker lists and no misleading panel states.
- BA validation commands produce understandable, reproducible results.
- No unrelated Relay, mailbox, UI/UX, or parked files are changed.
- Any UI/UX-facing BA change has a Darrin-approved mockup before implementation.

## 7. Recommended First CD-to-CC Dispatch

If Darrin approves, Codex should route this recommendation to CD. The first CD-to-CC implementation dispatch should be small:

- Target: BA QA F2 exit-code handling.
- Files likely involved: `scripts/ba_qa_tool.py`, `tests/test_ba_qa_tool.py`.
- Goal: accept runner return code 1 as completed audit-with-findings and keep return code 2+ as true subprocess error.
- Verification: BA QA tests with a mocked or fixture runner return code 1 plus a live `Bible Audit` summary run.

After that lands, re-run BA gates and choose the smallest remaining gate cleanup.




