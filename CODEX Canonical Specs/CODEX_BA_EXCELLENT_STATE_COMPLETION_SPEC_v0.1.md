# CODEX BA Excellent State Completion Spec v0.1

Created: 2026-05-06
Owner: Codex draft for Darrin/CD review
Scope: Final BA reliability, gate cleanup, evidence debt, and validation sweep
Status: Draft, not dispatched, not approved

## 1. Purpose

BA is improving but is not yet excellent. This spec defines the remaining work required before BA can be called excellent with a straight face: confirm the shipped F2/F4 fixes, clean or formally accept remaining gate findings, reduce unknown/evidence debt, and establish a repeatable validation sweep.

## 2. Current State

Known positive progress:

- BA QA F4 panel shipped and was Darrin-approved.
- BA QA F2 return-code fix shipped at `18ebd20` on `origin/main`.
- F2 now treats `ba_audit_runner.py` exit code `1` as audit-completed-with-findings, not subprocess crash.
- CC reported `tests/test_ba_qa_tool.py`: 16 passed.
- AM font audit previously passed: 0 font/height issues.
- BA calibration fixture previously passed.

Known remaining concerns:

- Commit `18ebd20` has an auto-bundle subject artifact; functionally acceptable if CD accepts the paper trail.
- Earlier BA validation showed failures or heavy unknown/warn debt in `PG Design Ledger`, `Tracker`, `Inspector`, `Audit Module`, and `Panda Gallery`.
- `Bible Audit` may currently be at `0 fail / 0 warn / 2 unknown`, but unknowns are still not excellence.
- A fresh full BA sweep is required after F2/F4 to establish current truth.

## 3. Non-Goals

- Do not relax BA gates to make results look better.
- Do not hide fail, warn, or unknown findings.
- Do not perform broad rewrites of BA architecture.
- Do not make UI/UX changes without first presenting a mockup to Darrin and receiving approval.
- Do not touch Relay files.
- Do not touch parked dirty files or unrelated UI/UX artifacts.
- Do not send implementation-go or commit-go directly from Codex to CC.

## 4. Required Work

### 4.1 Establish Fresh Baseline

Run a current BA validation sweep after F2/F4 are on `origin/main`:

```powershell
python -m pytest "C:\panda-gallery\tests\test_ba_audit_runner.py"
python -m pytest "C:\panda-gallery\tests\test_ba_qa_tool.py"
python "C:\panda-gallery\scripts\ba_audit_runner.py" --calibrate --summary
python "C:\panda-gallery\scripts\ba_audit_runner.py" --app "Bible Audit" --summary --gate
python "C:\panda-gallery\scripts\ba_audit_runner.py" --app "PG Design Ledger" --summary --gate
python "C:\panda-gallery\scripts\ba_audit_runner.py" --app "Tracker" --summary --gate
python "C:\panda-gallery\scripts\ba_audit_runner.py" --app "Inspector" --summary --gate
python "C:\panda-gallery\scripts\ba_audit_runner.py" --app "Audit Module" --summary --gate
python "C:\panda-gallery\scripts\ba_audit_runner.py" --app "Panda Gallery" --summary --gate
```

Expected exit code `1` from a gate means audit findings remain; it is not a runtime failure. Runtime failure means crash, missing output, traceback, or invalid JSON.

`ba_audit_runner.py` commands may refresh `workflows/design/applets/ba_audit_latest.json` and related calibration/latest artifacts. Treat those as validation artifacts. Do not stage or commit them unless CD/Darrin explicitly requests an evidence-artifact commit.

### 4.2 Classify Findings

For every target, classify top findings as:

- product defect,
- audit-rule defect,
- missing evidence,
- accepted intentional exception,
- duplicate/superseded finding.

Each accepted exception must include evidence, owner, date, and review-after date.

### 4.3 Cleanup Order

Proceed smallest-win first:

1. `Bible Audit`: resolve or accept remaining unknowns.
2. `PG Design Ledger`: remove fail findings and reduce unknown debt.
3. `Tracker`: active workflow target; fix real failures, especially filter or interaction evidence defects.
4. `Inspector`: active workflow target; fix real failures and evidence gaps.
5. `Audit Module`: larger surface, handle after smaller targets stabilize.
6. `Panda Gallery`: largest product surface, handle after audit tooling itself is trustworthy.

Each target gets its own Step 0, patch, verification, and commit decision. Do not batch unrelated targets.

### 4.4 UI/UX Mockup Gate

Any BA change that alters visible layout, controls, labels, colors, spacing, panel states, screenshots, or workflow presentation requires:

1. Mockup first.
2. Darrin approval of the mockup.
3. Only then CD may dispatch implementation to CC.

Pure backend/test/audit logic fixes that do not alter visible UI do not require a mockup.

### 4.5 Evidence Quality Bar

A target can be called excellent only when:

- fail count is zero,
- unknown count is zero or every unknown is explicitly accepted with evidence,
- warning count is either zero or every warning has owner/disposition,
- evidence score is at least 90% for small/internal targets or has an explicit owner-approved exception,
- coverage debt is 5% or lower for small/internal targets or has an explicit owner-approved exception,
- findings are reproducible from documented commands.

### 4.6 Reporting Format

For each target, produce a compact report:

- target name,
- command run,
- exit code meaning,
- totals: fail/warn/unknown/evidenced,
- evidence score and coverage debt,
- top blockers,
- recommended next action,
- whether UI/UX mockup is needed.

## 5. Acceptance Criteria

BA reaches excellent state only when:

- F2/F4 shipped fixes are verified from current `origin/main`.
- Fresh BA sweep is complete.
- `Bible Audit` and `PG Design Ledger` are clean or have documented accepted exceptions.
- `Tracker` and `Inspector` no longer have unresolved high-impact BA failures.
- Larger targets have a documented blocker plan and no misleading panel states.
- BA commands distinguish audit findings from runtime failures.
- Any UI/UX-facing work has Darrin-approved mockups before implementation.
- No Relay, unrelated mailbox, parked UI/UX, or unrelated dirty files are modified.

## 6. Recommended First Next Step

Route to CD for a CD-owned validation-only dispatch first, not coding. Codex must not dispatch this directly to CC:

1. Confirm latest `origin/main` and record the commit SHA being validated.
2. Run the fresh BA sweep in section 4.1 and preserve generated BA artifacts as evidence.
3. Report current target-by-target blocker list.
4. Choose the smallest next coding target from actual fresh data.

No coding should begin until the fresh sweep identifies the current smallest real blocker.



