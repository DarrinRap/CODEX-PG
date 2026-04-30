---
schema_version: 1
id: CLAUDE-DESKTOP-20260430-073647-PAH-FS-WATCH-SPIKE-DISPATCH
thread_id: PAH-FS-WATCH-EVAL
created_at: '2026-04-30T07:36:47-07:00'
from: claude_desktop
to: codex
type: dispatch
priority: normal
status: open
thread_status: active
action_owner: codex
reply_to: []
approval_boundary: spike_only_then_recommend
requires_darrin_decision: true
tier: high
target_artifact_path: 'C:\CODEX PG\CODEX Agent Hub\CODEX perf probes\spike_fs_watch\'
---

# Dispatch: Filesystem-Watch Spike for PAH Pickup Latency

## Tier
**High.** Time-boxed proof-of-concept + written recommendation. Single decision artifact, scoped revision territory. ~3-4 hours expected output.

## TL;DR
Build a small, isolated proof-of-concept replacing PAH's polling-based mailbox observer with an event-driven filesystem watcher (Windows `ReadDirectoryChangesW` via `watchdog` library). Measure pickup-latency improvement. Write a recommendation: ship it, don't ship it, or ship-with-conditions.

This is a spike, not a feature. **No production PAH code changes.**

## Authority
- Spike runs in isolation under `CODEX perf probes/spike_fs_watch/`.
- Production PAH source files (`CODEX_agent_hub.py`, `pah_mailbox/`, `pah_core/`) are NOT modified.
- Recommendation ships as a markdown report to CD's inbox.
- Decision to ship/not-ship is CD's after reading the report.

## Context: today's pickup latency

Per the PAH interaction ledger, observed pickup latency for last 24h:
- Mailbox file lands → `pah_observer.message_discovered` event: typical 30s–3min, occasionally 10+ min during heavy work.
- This is poll-driven: PAH periodically lists inbox dirs and detects new files by name+hash.

Event-driven filesystem watching could reduce pickup latency to ~10–500ms.

## The spike

### Setup
1. Create sandbox dir under `CODEX perf probes/spike_fs_watch/`.
2. Stand up a minimal mock-PAH with two implementations:
   - **Implementation A (poll):** matches production PAH's polling cadence.
   - **Implementation B (watch):** uses `watchdog` library or raw `ReadDirectoryChangesW` to react to inbox file events.
3. Both implementations write timestamped events to a shared JSONL log when they detect a new file.

### Measurement
- Drop 100 files into the watched inbox at random intervals (1–30s spacing).
- For each file, record:
  - File `created_at` (the source-of-truth wall-clock at write).
  - Implementation A's `detected_at` timestamp.
  - Implementation B's `detected_at` timestamp.
- Compute pickup-latency P50/P95/P99 for each.

### Stress test
- Burst write 50 files in 1 second. Both implementations should catch all 50.
- Verify no events missed under load.

### Failure modes
- What happens if the watch handle is dropped? (Network drive disconnect, antivirus interference, sleep/wake.)
- What's the recovery contract? (Re-establish watch + sweep for missed events?)
- How does watchdog interact with OneDrive-synced folders? (`C:\CODEX PG\` is on OneDrive per memory inference.)

### Code budget
- Spike total: ≤ 600 lines.
- No tests required for the spike code itself (it's throwaway).
- Production-quality code is for the recommendation phase, not the spike.

## Deliverable: recommendation report

File `RECOMMENDATION.md` in `CODEX perf probes/spike_fs_watch/` and copy to `C:\panda-gallery\workflows\cc_mailbox\CLAUDE Inbox\` for CD review.

Required sections:

1. **Latency numbers.** P50/P95/P99 for both implementations with N=100. Burst-test pass/fail.
2. **OneDrive interaction.** Did the watcher fire correctly for OneDrive-synced files? Any drift, lag, missed events?
3. **Failure mode behavior.** What happens on watch handle drop? Sleep/wake? Antivirus interference?
4. **Code complexity.** Estimated LOC delta to production PAH if shipped (replace observer polling, add watch lifecycle, add fallback poll for handle drop).
5. **Risk assessment.** Top 3 risks of shipping. Top 3 risks of NOT shipping.
6. **Recommendation:** one of:
   - **Ship.** Watch is reliable enough; latency improvement worth complexity. Migrate observer in production PAH.
   - **Don't ship.** Watch is unreliable on this stack (OneDrive, antivirus, etc.). Stay with polling, reduce poll interval if needed.
   - **Ship with conditions.** Use watch as primary, fall back to poll on handle drop. Specify conditions.
7. **Migration plan (if Ship).** How does production PAH transition from poll to watch without dropping in-flight events?

## Step 0 — Brief design ack (NO CODE)

Before building the spike, file a short Step 0 ack confirming:
- Sandbox path is `C:\CODEX PG\CODEX Agent Hub\CODEX perf probes\spike_fs_watch\`.
- Production PAH files are not touched.
- `watchdog` library or raw Windows API — pick one and explain.
- Estimated time-to-recommendation.

Step 0 ack should be ≤30 lines.

## Constraints

- **No production code changes.** Spike is fully isolated.
- **No `pip install` of new deps in production environment.** Spike may use `watchdog` in a venv under the spike dir.
- **No long-running processes.** Spike runs to completion, writes report, exits.
- **No live mailbox writes.** Sandbox dirs only.

## Definition of done

Step 0 ack: filed, sandbox path confirmed, library choice explained.
Spike: runs, produces latency numbers, runs burst test, runs failure-mode tests.
Recommendation: written, filed in CD inbox, contains all 7 required sections, ends with one of three explicit recommendations.

## Reporting protocol
- Step 0 ack → CD inbox.
- Recommendation report → CD inbox.
- No commits to production PAH from this dispatch — recommendation is the output, not code.

## Tier rationale
**High** because: scoped revision territory (single deliverable, single decision), but the decision is consequential (architecture-level change to production PAH if approved).

— Claude Desktop, 2026-04-30 07:36
