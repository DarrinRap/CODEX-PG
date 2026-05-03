# PAH Communication Speed Test Spec

Created: 2026-05-02
Owner: Codex
Status: Approved for V1 implementation
Scope: Local PAH communication-speed harness, dashboard button, and dated local logs.

## 1. Close-Review Corrections To Initial Proposal

This document supersedes the quick inline proposal. The closer review found
several places that needed tightening before implementation:

1. The phrase "communication speed" was ambiguous. In v1 this must mean PAH
   local mailroom and dashboard communication speed, not live human/agent
   response latency.
2. The original "150 ms total mailroom transaction" threshold was too strict
   because the existing target is for one local mailbox reply write, while the
   canary exercises multiple operations: source write, read-state write, reply
   write, reply tombstone, ledger write, and evidence readback.
3. "Post the results" must mean posting inside PAH and appending a local log.
   It must not send a mailbox message, SMS, webhook, email, or external post.
4. Date-stamped comparison needs both a latest summary and append-only history.
   JSONL alone is good for audit, but the dashboard also needs a cheap latest
   read path.
5. Slow communication should mean duration above an accepted threshold. The UI
   may say "slow", but the implementation should compare milliseconds against
   explicit threshold constants.
6. Existing PAH specs already reserve a Phase 4 performance harness with P50,
   P95, P99 pickup-latency display. This feature should become the first local
   performance harness slice, not a separate diagnostic island.

## 2. Product Goal

Add a PAH dashboard control that lets Darrin run a repeatable communication
speed test on demand, see the result immediately, compare it with recent runs,
and spot slow PAH communication without opening logs.

The first implementation must answer:

- Is PAH's local mailroom path fast?
- Is PAH's dashboard state refresh fast?
- Is the latest run slower than the recent baseline?
- Did any correctness check fail?
- Where is the dated evidence log?

## 3. Non-Goals For V1

V1 must not measure live model/human reply latency. It must not create real
messages in active Claude, Codex, CC, or Darrin inboxes.

Deferred to v2:

- Agent pickup latency: time from file write to another agent discovering it.
- Agent reply latency: time from dispatch to response message.
- Route-specific live ping/reply tests.
- Periodic scheduled speed tests.
- Health gating on live pickup P50/P95/P99.

## 4. Existing Building Blocks

PAH already has useful primitives:

- `run_mailroom_transaction_canary()` exercises an isolated temp mailroom.
- `/api/mailroom-canary` exposes that canary behind the existing write-token
  and origin protection.
- `CODEX_pah_mail_state_perf.local.jsonl` records state-build timings.
- Existing performance targets define:
  - warm `/api/cockpit` p95 under 300 ms,
  - warm `/api/health` p95 under 250 ms,
  - send local mailbox reply p95 under 150 ms,
  - dashboard refreshes over a few hundred ms as profile-worthy.

## 5. V1 Test Definition

The Communication Speed Test is a local, isolated benchmark made of two parts.

### 5.1 Isolated Mailroom Transaction

Use the existing temp-mailbox canary pattern, but add timing around each step:

- create source message
- mark source message read in isolated read-state
- create reply message
- write reply tombstone
- append interaction ledger events
- read back canary evidence

The canary must continue to restore all globals and clear parse caches in
`finally`, as it does today.

### 5.2 Warm Cockpit Refresh

Measure one warm `cockpit_payload()` build immediately after the canary. This
tests the dashboard data path that users feel after a run.

The UI-triggered API response may include the measured cockpit duration without
forcing the browser to make a second `/api/cockpit` request before showing the
result.

## 6. Thresholds

Thresholds are initial accepted limits, derived from existing PAH targets. They
should live as named constants, not anonymous numbers inside the UI.

### 6.1 Per-Step Mailroom Thresholds

| Metric | OK | WARN | SLOW |
| --- | ---: | ---: | ---: |
| source_write_ms | <= 150 | 151-300 | > 300 |
| read_state_write_ms | <= 100 | 101-250 | > 250 |
| reply_write_ms | <= 150 | 151-300 | > 300 |
| tombstone_write_ms | <= 100 | 101-250 | > 250 |
| ledger_evidence_ms | <= 100 | 101-250 | > 250 |

### 6.2 Aggregate Thresholds

| Metric | OK | WARN | SLOW |
| --- | ---: | ---: | ---: |
| mailroom_total_ms | <= 500 | 501-1000 | > 1000 |
| cockpit_ms | <= 300 | 301-1000 | > 1000 |
| end_to_end_ms | <= 800 | 801-1500 | > 1500 |

### 6.3 Trend Thresholds

Calculate baselines from the last 20 successful local runs:

- WARN if latest `end_to_end_ms` is at least 2x recent p50.
- SLOW if latest `end_to_end_ms` is at least 3x recent p50.
- SLOW if any aggregate metric crosses its SLOW threshold.
- ERR if any correctness check fails, regardless of duration.

If fewer than 3 previous successful runs exist, show "baseline warming" and do
not apply trend warnings.

## 7. Result Classification

Overall result is the worst of:

- correctness severity
- per-step severity
- aggregate severity
- trend severity

Severity order:

`ok < warn < slow < err`

Suggested UI labels:

- OK: "Comm speed OK"
- WARN: "Comm speed warning"
- SLOW: "Comm speed slow"
- ERR: "Comm speed failed"

## 8. Logs And Files

Append each run to:

`C:\CODEX PG\CODEX Agent Hub\CODEX logs\CODEX_pah_comm_speed_tests.jsonl`

Write latest summary to:

`C:\CODEX PG\CODEX Agent Hub\CODEX state\CODEX_pah_comm_speed_latest.local.json`

The JSONL log is the date-stamped comparison record. The latest JSON is the
fast dashboard read path.

Retention:

- Keep JSONL append-only.
- Latest JSON may be overwritten every run.
- Do not auto-delete history in v1.

## 9. Log Schema

Each JSONL row. The `run_id` includes a millisecond suffix so repeated manual
runs inside the same second remain distinct:

```json
{
  "schema_version": 1,
  "run_id": "PAH-COMM-SPEED-20260502-120000-123",
  "created_at": "2026-05-02T12:00:00-07:00",
  "actor": "darrin_or_codex",
  "trigger": "dashboard_button",
  "overall": "ok",
  "baseline_state": "ready",
  "durations_ms": {
    "source_write": 42,
    "read_state_write": 18,
    "reply_write": 47,
    "tombstone_write": 9,
    "ledger_evidence": 21,
    "mailroom_total": 172,
    "cockpit": 244,
    "end_to_end": 431
  },
  "checks": {
    "source_written": true,
    "read_state_written": true,
    "reply_written": true,
    "reply_tombstone_written": true,
    "ledger_sent_event": true,
    "ledger_read_event": true,
    "ledger_tombstone_event": true
  },
  "thresholds": {
    "mailroom_total_warn_ms": 500,
    "mailroom_total_slow_ms": 1000,
    "cockpit_warn_ms": 300,
    "cockpit_slow_ms": 1000,
    "end_to_end_warn_ms": 800,
    "end_to_end_slow_ms": 1500
  },
  "comparison": {
    "previous_end_to_end_ms": 462,
    "delta_vs_previous_ms": -31,
    "recent_p50_end_to_end_ms": 448,
    "recent_p95_end_to_end_ms": 690,
    "trend": "faster"
  },
  "notes": []
}
```

## 10. API Contract

### 10.1 Run Test

`POST /api/run-communication-speed-test`

Protected by existing PAH write-token and Origin checks because it writes local
logs.

Request:

```json
{
  "actor": "darrin_or_codex"
}
```

Response:

```json
{
  "ok": true,
  "overall": "ok",
  "run": {},
  "history": {
    "latest": {},
    "previous": {},
    "last_10": [],
    "p50_end_to_end_ms": 448,
    "p95_end_to_end_ms": 690,
    "p99_end_to_end_ms": 732
  },
  "log_path": "C:\\CODEX PG\\CODEX Agent Hub\\CODEX logs\\CODEX_pah_comm_speed_tests.jsonl"
}
```

### 10.2 Read History

`GET /api/communication-speed-tests?limit=20`

Returns latest summary plus recent log rows. This endpoint is read-only and
does not require a write token.

## 11. UI Design

Add a small button in the Steward & Mailboxes area:

`Speed test`

On click:

1. Disable the button and show "Testing...".
2. POST `/api/run-communication-speed-test`.
3. Render the result card without a full page reload.
4. Re-enable the button.

Result card fields:

- status label
- latest end-to-end duration
- mailroom total duration
- cockpit duration
- previous run delta
- p50/p95/p99 recent baseline
- timestamp
- log path copy/open affordance

Example:

`Comm speed OK - 431 ms - 31 ms faster than previous`

Slow state example:

`Comm speed slow - 1720 ms - above 1500 ms threshold`

History display:

- show last 10 runs as compact rows
- color-code OK/WARN/SLOW/ERR
- make the newest row visually pinned
- keep raw JSON hidden unless opened through Inspector/action detail

## 12. Safety Rules

The feature must not:

- write to live active mailboxes,
- send SMS/email/webhooks,
- mark real messages read/unread,
- delete or archive anything,
- create route-test pings in v1,
- claim to measure human/agent response latency.

Allowed writes:

- append one JSONL row to the comm speed log,
- overwrite latest comm speed JSON,
- optionally append one local interaction-ledger event of type
  `communication_speed_test_finished`.

## 13. Inspector And Health Integration

V1 should expose the latest run as informational in PAH health, not as a hard
health gate.

Recommended health behavior:

- latest OK/WARN/SLOW shown in Steward & Mailboxes.
- ERR can raise diagnostics attention.
- SLOW does not make PAH "down"; it means performance degraded.

V2 may gate "PAH healthy" on performance evidence after enough baseline data
exists.

## 14. Implementation Plan

1. Add threshold constants and log paths in `CODEX_agent_hub.py`.
2. Refactor `run_mailroom_transaction_canary()` so it can return step timings
   while preserving current correctness behavior.
3. Add `run_communication_speed_test()`.
4. Add JSONL append and latest JSON write helpers.
5. Add `POST /api/run-communication-speed-test`.
6. Add `GET /api/communication-speed-tests`.
7. Add the dashboard button and result/history card.
8. Add smoke tests for classification, log schema, API shape, and UI wiring.

## 15. Test Plan

Smoke/unit coverage:

- classification returns OK/WARN/SLOW/ERR correctly.
- fewer than 3 prior runs produces `baseline_state = "warming"`.
- JSONL append writes one row per run.
- latest JSON overwrite works.
- `/api/run-communication-speed-test` rejects missing/invalid write token.
- `/api/communication-speed-tests` returns bounded history.
- UI contains the `Speed test` button.
- UI click handler calls the expected endpoint.

Manual verification:

- click button in PAH.
- result appears without reload.
- log row appears with current timestamp.
- second click shows delta against previous.
- artificially slow one metric in test mode and confirm SLOW flag.

## 16. Darrin Decisions

1. SLOW runs appear only in Steward & Mailboxes in v1. They must not create a
   queue item.
2. The log path should be exposed through an "Open log" action in v1.
3. V2 live route ping/reply tests remain deferred. V1 is local-only and
   isolated.

## 17. Recommendation

Implement v1 as a local isolated PAH communication-speed harness. It gives a
real signal about PAH's own mailroom and dashboard responsiveness, avoids live
mailbox noise, and creates the date-stamped trend log needed for comparison.

Do not implement live agent pickup/reply benchmarking until the mailbox route
protocol has an explicit test-message convention and Darrin approves the live
artifact behavior.
