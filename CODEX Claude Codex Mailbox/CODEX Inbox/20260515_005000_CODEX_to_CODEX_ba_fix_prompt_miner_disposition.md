---
schema_version: 1
message_id: 20260515_005000_CODEX_to_CODEX_ba_fix_prompt_miner_disposition
in_reply_to: 20260515_004708_CODEX_to_CODEX_ba_fix_dispatch_prompt-miner
thread_id: BA-FIX-PROMPT-MINER
from: CODEX
to: CODEX
date: 2026-05-14T17:50:00-07:00
subject: DISPOSITION — Prompt Miner BA fix dispatch; workflow-order finding is coverage gap, no app defect confirmed
priority: normal
type: disposition
status: shipped
approval_boundary: ack_only
---

# Prompt Miner BA Fix Dispatch — Disposition

Target app acknowledged: **Prompt Miner**.
Actionable count acknowledged: **1**.

## Summary

Confirmed bugs: **0**
False positives: **0**
Coverage gaps: **1**
Deferred findings: **0**

The BA finding reproduced exactly, but investigation confirms it is a scanner coverage gap rather than an app defect. Prompt Miner is a PySide app with action controls created and added in explicit source order. BA's `workflow_order_static` scanner currently proves HTML controls through `data-pg-order-*` markers, but intentionally reports PySide action-control order as unknown because there is no PySide runtime geometry/order probe yet.

No BA-specific app code change was made.

## Finding Disposition

COVERAGE GAP: BA-WORKFLOW-ORDER-PROMPT-MINER-0001 — PySide workflow order unproven — BA cannot currently prove left-to-right runtime order for PySide source from static text alone. Source inspection shows the Prompt Miner action row is constructed and added in a deterministic order in `scripts/pg_prompt_miner.py`, but the scanner limitation remains until BA gains explicit PySide order metadata support or a runtime PySide geometry/order probe.

## Evidence Checked

- `scripts/pg_prompt_miner.py` action row construction: `Scan Chats`, `Need Radar`, `Quality Gaps`, `AI Top 10`, `Recommend Best`, `Refresh Web Research`, `Add Selected To Clipper`, `Add AI Top 10 To Clipper`, `Copy Improved Prompt`, `Export Candidates...`
- `scripts/ba_audit_runner.py` `workflow_order_checks()` behavior: HTML order markers can pass/fail; PySide controls generate the `PySide workflow order unproven` coverage-gap row.
- `tests/test_ba_audit_runner.py::test_workflow_order_static_marks_pyside_as_coverage_gap` confirms this is expected scanner behavior.

## Touched Files

None for this BA disposition.

Note: `scripts/pg_prompt_miner.py` already has unrelated local Prompt Miner improvements from direct user-reported issues (pill clipping and expanded chat mining). Those are not BA workflow-order fixes and were not expanded for this dispatch.

## Verification

```powershell
python scripts\ba_audit_runner.py --app "Prompt Miner" --summary
```

Result: reproduced canonical BA result: `0 fail / 0 warn / 1 unknown / 7 evidenced`, with `BA-WORKFLOW-ORDER-PROMPT-MINER-0001` as the only unknown.

```powershell
python -m pytest tests\test_ba_audit_runner.py -q
```

Result: `72 passed in 18.10s`.

## Recommended Follow-Up

Improve BA rather than Prompt Miner: add a PySide workflow-order proof path, either via explicit app-side order metadata that BA can parse or an app-specific runtime geometry probe that launches/measures the Prompt Miner top action row.

Status: **shipped** — disposition complete, no Prompt Miner app defect confirmed.

— Codex
