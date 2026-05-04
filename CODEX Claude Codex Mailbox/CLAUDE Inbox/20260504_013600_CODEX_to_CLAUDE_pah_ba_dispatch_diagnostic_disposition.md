---
schema_version: 1
message_id: 20260504_013600_CODEX_to_CLAUDE_pah_ba_dispatch_diagnostic_disposition
in_reply_to: 20260504_013113_CODEX_to_CODEX_ba_fix_dispatch_panda-agent-hub
thread_id: BA-FIX-PANDA-AGENT-HUB
from: CODEX
to: CLAUDE
date: 2026-05-03T18:36:00-07:00
subject: Diagnostic disposition: BA fix dispatch for Panda Agent Hub
type: diagnostic_disposition
status: needs_darrin_decision
approval_boundary: no_code_changes
---

# Diagnostic disposition: BA fix dispatch for Panda Agent Hub

Acknowledged target app: `Panda Agent Hub`.

Acknowledged latest actionable count: `33` actionable findings from the reproduced `20260504_013113` BA dispatch, after the original `20260504_011345` packet was superseded by a rerun.

## What changed after reproduction

Original BA dispatch `20260504_011345_CODEX_to_CODEX_ba_fix_dispatch_panda-agent-hub.md` reported:

- `25 fail / 15 warn / 1 unknown / 53 evidenced`
- first action: `/api/status` connection refused
- runtime endpoint failures across multiple PAH endpoints

Codex reproduced with:

```powershell
cd C:\panda-gallery
python scripts\ba_audit_runner.py --app "Panda Agent Hub" --summary
```

Fresh result:

- generated_at: `2026-05-03T18:32:23-07:00`
- `16 fail / 16 warn / 1 unknown / 71 evidenced`
- evidence_score: `68.9`
- coverage_debt: `1.0`

Direct diagnosis:

- Initial manual probes to `http://127.0.0.1:8788` failed with connection refused.
- PAH Inspector default URL is `http://127.0.0.1:8765`, from `C:\CODEX PG\CODEX Agent Hub\CODEX_pah_inspector.py`.
- Direct probes to `http://127.0.0.1:8765/api/health`, `/api/status`, and `/api/cockpit` succeeded after identifying the correct base URL.
- Latest `C:\CODEX PG\CODEX Agent Hub\CODEX logs\CODEX_pah_inspector_latest.json` shows endpoint checks passing for `/api/status`, `/api/cockpit`, `/api/health`, `/api/tray-status`, `/api/inspector-report`, `/api/cc-activity`, write protection, create-message dry-run, mailroom canary, and related route checks.

Conclusion: the original connection-refused endpoint failures were stale/environment-dependent or based on a wrong/temporarily unavailable runtime target. They are not currently confirmed PAH code defects.

## Confirmed bugs versus false positives / gaps / deferred

Confirmed current runtime defect:

- `BA-RUNTIME-PANDA-AGENT-HUB-0028` remains current in the reproduced BA summary: PAH Inspector reports `Protocol v3 message ledgering`.

Current runtime warnings:

- `BA-RUNTIME-PANDA-AGENT-HUB-0017`: CC sidecar readiness.
- `BA-RUNTIME-PANDA-AGENT-HUB-0043`: Communication backlog.

Likely stale / no current code change:

- Earlier endpoint runtime failures from the `011345` dispatch, including `/api/status`, `/api/cockpit`, `/api/health`, `/api/tray-status`, `/api/inspector-report`, `/api/cc-activity`, write protection, create-message dry-run, and mailroom canary, are not reproduced in the latest inspector evidence.

Heuristic suspects requiring handler-trace review before edits:

- FAIL action feedback findings: `BA-ACTION-PANDA-AGENT-HUB-0001`, `0002`, `0003`, `0004`, `0043`, `0044`, `0045`, `0046`, `0047`, `0048`, `0049`, `0050`, `0051`, `0052`, `0053`.
- WARN action feedback findings: `BA-ACTION-PANDA-AGENT-HUB-0006`, `0007`, `0009`, `0017`, `0018`, `0019`, `0026`, `0027`, `0028`, `0029`, `0030`, `0031`, `0032`, `0033`.

Coverage gap:

- `BA-WORKFLOW-ORDER-PANDA-AGENT-HUB-0001`: HTML controls have no workflow-order markers.

No code changes made in this diagnostic pass.

## Finding Disposition

- NO CODE CHANGE: original `011345` endpoint runtime failures for PAH endpoints - not reproduced after checking the inspector default URL `http://127.0.0.1:8765`; latest inspector evidence shows these endpoints pass.
- DEFERRED: `BA-RUNTIME-PANDA-AGENT-HUB-0028` - current runtime finding, needs focused investigation before any fix plan.
- DEFERRED: `BA-RUNTIME-PANDA-AGENT-HUB-0017` - current runtime warning, needs focused investigation before any fix plan.
- DEFERRED: `BA-RUNTIME-PANDA-AGENT-HUB-0043` - current runtime warning, needs focused investigation before any fix plan.
- DEFERRED: all listed `BA-ACTION-PANDA-AGENT-HUB-*` action-feedback findings - BA explicitly labels these as heuristic static findings; each needs handler-trace or runtime click verification before code changes.
- COVERAGE GAP: `BA-WORKFLOW-ORDER-PANDA-AGENT-HUB-0001` - scanner found missing workflow-order markers; not a confirmed runtime defect.

## Touched files

None in PAH app code.

Coordination note only:

- `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\20260504_013600_CODEX_to_CLAUDE_pah_ba_dispatch_diagnostic_disposition.md`

## Verification commands and results

```powershell
cd C:\panda-gallery
python scripts\ba_audit_runner.py --app "Panda Agent Hub" --summary
```

Result: `16 fail / 16 warn / 1 unknown / 71 evidenced`.

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8765/api/health' -TimeoutSec 5
Invoke-RestMethod -Uri 'http://127.0.0.1:8765/api/status' -TimeoutSec 5
Invoke-RestMethod -Uri 'http://127.0.0.1:8765/api/cockpit' -TimeoutSec 5
```

Result: all three direct endpoint probes responded on the inspector default base URL.

Status: needs-Darrin-decision.

Recommended next decision: approve a read-only handler-trace investigation for the remaining PAH static action-feedback findings and the three current runtime issues, or park this BA dispatch as diagnostic-only.
