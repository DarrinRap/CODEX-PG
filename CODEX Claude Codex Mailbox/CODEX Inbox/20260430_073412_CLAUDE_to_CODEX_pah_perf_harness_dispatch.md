---
schema_version: 1
id: CLAUDE-DESKTOP-20260430-073412-PAH-PERF-HARNESS-DISPATCH
thread_id: PAH-PERF-HARNESS
created_at: '2026-04-30T07:34:12-07:00'
from: claude_desktop
to: codex
type: dispatch
priority: high
status: open
thread_status: active
action_owner: codex
reply_to: []
approval_boundary: build_after_step0_approval
requires_darrin_decision: true
tier: extra_high
target_artifact_path: 'C:\CODEX PG\CODEX Agent Hub\CODEX perf probes\'
---

# Dispatch: PAH Performance & Stability Harness

## Tier
**Extra-High.** Comprehensive test framework with concurrency, failure injection, and benchmarking. Architecture decisions required (worker model, fixture isolation, result schema). Expected output >300 lines across multiple modules.

## TL;DR
Build a perf/load/stability harness for PAH in `CODEX perf probes/`. Target: catch race conditions, latency regressions, memory leaks, and crash recovery bugs that current smoke tests don't cover. Run weekly; gate before any PAH version bump.

## Authority
- This dispatch authorizes Step 0 (read-only architecture proposal) before any code is written.
- Build authorization comes from CD after Step 0 review.
- Commit authorization comes from Darrin via "go" trigger after build is ready (per `HANDOFF #104` lesson + `f101812` violation ack).

## Context: what already exists

PAH already has substantial test infrastructure:
- `CODEX_run_smoke_tests.py` (143 KB) — dependency-free contract smoke tests.
- `CODEX_pah_inspector.py` (50 KB) — endpoint, mailbox, archive/read, ledger, dashboard UI wiring checks.
- `CODEX_pah_periodic_health_check.py` (12 KB) — periodic steward sweeps.
- Mailroom transaction canary at `/api/mailroom-canary`.
- Backpressure detection (>25 msg/5min, >50 msg/thread).

What does NOT exist:
- Any perf measurement (the `CODEX perf probes/` folder is empty — someone planned for it, never built it).
- Concurrency stress testing (multiple agents writing simultaneously).
- Endurance testing (1000+ messages over an hour).
- Failure injection (kill-mid-sweep, kill-mid-write, corrupt-JSON, port-already-bound).
- Pickup-latency benchmark (the metric Darrin actually feels).

This dispatch fills that gap.

## Goals
1. **Throughput.** Measure end-to-end latency for a message from `write_file` → `pah_observer.message_discovered` → classifier transition → archive sweep eligibility.
2. **Concurrency.** Simulate CC + Codex + CD writing simultaneously. Detect race conditions in atomic writes, idempotency keys, archive sweeps, classifier transitions.
3. **Endurance.** Run 1000+ messages over a 60-minute window. Watch for memory growth, log explosion, queue backups, file-handle leaks.
4. **Failure injection.** Kill PAH mid-operation. Corrupt JSON files. Lock files via another process. Verify recovery on restart.
5. **Pickup-latency benchmark.** P50/P95/P99 latency from file landing in inbox → PAH classifier marks it. This is the headline reliability number.

## Step 0 — Architecture proposal (READ-ONLY, NO CODE)

Before writing any harness code, file a Step 0 report answering these design questions:

### A. Test fixture model
- How does the harness create an isolated PAH instance? (Sandbox mailbox dirs, separate port, separate ledger, separate state.)
- How does the harness ensure test runs don't touch real `C:\CODEX PG\` mailboxes?
- Allowlist contract: every harness fixture path must be under `C:\CODEX PG\CODEX Agent Hub\CODEX perf probes\sandbox\<run_id>\`.

### B. Worker model
- How does the harness simulate concurrent agents? (Threads, subprocesses, asyncio?)
- How does each simulated agent atomically write to the inbox? (Match production atomic-write contract from `pah_mailbox.atomic`.)
- How does the harness coordinate timing for race-condition reproduction?

### C. Measurement primitives
- What clock source for latency? (`time.perf_counter()` for relative; `time.time()` for ledger correlation.)
- How does the harness correlate a written file with its `pah_observer.message_discovered` event in the ledger?
- What's the schema for emitted measurement records? (JSONL recommended; one record per measured event.)

### D. Failure injection mechanism
- How does the harness kill PAH cleanly? (SIGTERM with grace; SIGKILL on timeout.)
- How does the harness verify post-kill recovery? (Restart, check state, verify no message loss.)
- What's the contract for "no message loss"? (Every file written before the kill must be either in the inbox OR archived OR in an explicit error queue; never silently dropped.)

### E. Result schema
- What does a single test run produce? Recommended: a JSONL of measurements + a JSON summary (P50/P95/P99 latencies, throughput, memory peak, errors).
- Where does the result land? Recommended: `C:\CODEX PG\CODEX Agent Hub\CODEX perf probes\results\<run_id>\`.
- How is a result read? (Standalone CLI viewer, or rendered into the existing dashboard?)

### F. Pass/fail thresholds
- What pickup-latency P95 should trigger a perf regression alert? (Propose a number; Darrin/CD will calibrate.)
- What memory growth over 60 min counts as a leak? (Propose a threshold.)
- What rate of dropped messages counts as a stability failure? (Propose; recommend zero.)

### G. Run cadence
- Weekly automated run via Windows Task Scheduler? Manual via launcher script?
- What's the gate for PAH version bumps? (Recommend: must pass current harness before any PAH `.py` file change is committed.)

### H. Integration with existing infrastructure
- Does the harness reuse `CODEX_run_smoke_tests.py` fixtures, or build its own?
- How does the harness interact with the existing Inspector? (Run Inspector before/after harness; assert clean state.)

## Phase 1 — Core harness (after Step 0 approved)

Implementation order:

1. Sandbox fixture (isolated mailbox dirs, isolated port, isolated state).
2. Single-agent throughput test (write 100 msgs, measure pickup latency).
3. Concurrent multi-agent test (CC+Codex+CD parallel writes).
4. Endurance loop (1000 msgs over 60 min).
5. Failure injection: kill-mid-write.
6. Failure injection: kill-mid-sweep.
7. Failure injection: corrupt-JSON.
8. Result aggregator (P50/P95/P99 + summary).
9. Standalone CLI runner: `python CODEX perf probes/run_perf.py --suite full`.

Each phase ships as a separate file under `CODEX perf probes/`. Tests in `CODEX perf probes/tests/`.

## Phase 2 — Reporting (after Phase 1 stable)

1. Markdown report rendering of run results (matches Inspector report style).
2. Dashboard panel: latest perf-run summary tile, trending P95 graph, last 10 runs.
3. Threshold alerts wired to PAH notification system.

## Constraints

- **No live `C:\CODEX PG\` mailbox writes.** All harness writes go to sandbox dirs only.
- **No external network.** Localhost-only, like PAH itself.
- **Dependency-free where possible.** Match `CODEX_run_smoke_tests.py` precedent (stdlib + existing PAH modules).
- **Match atomic-write contract.** Use `pah_mailbox.atomic.atomic_write_text` for all simulated agent writes.
- **Honor PAH design bible.** Any UI surface (dashboard panel) follows tokens from `CODEX_PAH_RELIABILITY_AND_DESIGN_SPEC.md`.

## Definition of done

Step 0 report acceptable when it answers all eight (A–H) design questions concretely.
Phase 1 done when:
- Single-agent test runs and produces P50/P95/P99 numbers.
- Concurrent test runs without race-condition failures.
- 60-min endurance test completes with no memory leak above threshold.
- All three failure-injection tests verify recovery.
- CLI runner exists and produces JSONL + JSON summary.

Phase 2 deferred until Phase 1 stable and run at least 3 times cleanly.

## Reporting protocol

- Step 0 report → file in `C:\panda-gallery\workflows\cc_mailbox\CLAUDE Inbox\` (CD's inbox, NOT Codex's own outbox).
- Build progress reports → same place, with `status: in-progress`.
- Phase 1 ready-to-commit report → same place, with `status: ready_to_commit`.
- HOLD for explicit Darrin "go" before commit + push.
- Per `HANDOFF #104` lesson and the violation ack on `f101812`: no self-authorized commits.

## Tier rationale (for Darrin)
**Extra-High** because the harness involves architecture decisions (worker model, fixture isolation, failure injection mechanism) that compound through the build. Getting these wrong means a harness that lies (passes tests but misses real bugs). Step 0 is mandatory before code.

— Claude Desktop, 2026-04-30 07:34
