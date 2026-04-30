---
schema_version: 1
id: CLAUDE-DESKTOP-20260430-073924-PAH-SELF-HEAL-WATCHDOG-DISPATCH
thread_id: PAH-SELF-HEAL-WATCHDOG
created_at: '2026-04-30T07:39:24-07:00'
from: claude_desktop
to: codex
type: dispatch
priority: normal
status: open
thread_status: active
action_owner: codex
reply_to: []
approval_boundary: build_after_step0_ack
requires_darrin_decision: true
tier: medium
target_artifact_path: 'C:\CODEX PG\CODEX Agent Hub\'
---

# Dispatch: PAH Self-Healing Watchdog Process

## Tier
**Medium.** Scoped feature, ~100–200 lines. Already in `CODEX_PAH_TODO.md` ("Add self-healing startup check: if PAH is not listening on 8765, start it with known-good Python runtime and write stdout/stderr to stable logs"). This dispatch promotes it from TODO to active work.

## TL;DR
Build a tiny standalone watchdog process that monitors PAH's HTTP endpoint and auto-restarts PAH if it dies. No redundancy, no failover server — just a guardian process that keeps PAH alive.

## Authority
- Step 0 ack required before code (≤20 lines).
- Build authorization comes from CD after Step 0.
- Commit authorization comes from Darrin via "go" trigger after build is ready.

## Context

PAH is a localhost service. When it crashes (process exit, port binding failure, Python error during startup), it stays dead until Darrin manually restarts it via `CODEX_start_agent_hub.ps1`.

Today's MASSIVE REGRESSION (per `CODEX_PAH_TODO.md` top item) is a content/UI regression, not a process death. But process death IS a real failure mode that has happened (per logs in `CODEX logs/`, several restart cycles visible across `CODEX_agent_hub_codex_restart_*` filenames on 2026-04-28).

The watchdog gives PAH a heartbeat-and-restart loop without requiring Darrin's attention.

## Goals

1. **Detect PAH death.** Poll `http://127.0.0.1:8765/api/health` every N seconds. If response missing or unhealthy for M consecutive checks, declare PAH dead.
2. **Restart PAH cleanly.** Kill any zombie `python` processes bound to port 8765. Wait for port release. Start PAH via the known-good launcher.
3. **Bound restart attempts.** If PAH dies more than X times in Y minutes, stop trying and emit a notification — likely a code bug, not a transient crash.
4. **Logging.** Watchdog writes to its own log file (`CODEX logs/watchdog_stdout.log`, `watchdog_stderr.log`), separate from PAH's logs.
5. **Tray integration (optional, Phase 2).** If the PAH tray is running, watchdog signals "PAH restarted at HH:MM" via tray balloon (off by default).

## Step 0 — Brief design ack (NO CODE)

≤20 lines. Confirm:
- Watchdog runs as a separate Python process (not a thread inside PAH).
- Polling interval (default proposed: 30s).
- Failed-check threshold (default proposed: 3 consecutive misses = dead).
- Restart cooldown (default proposed: 60s between restart attempts).
- Restart bound (default proposed: 5 restarts in 30 min triggers stop + notify).
- Where the watchdog process is launched from (recommend: same launcher script as PAH, or separate `start_watchdog.ps1`).
- Whether watchdog auto-installs at Windows startup (recommend: explicit tray-menu opt-in, mirroring PAH's existing pattern).

## Phase 1 — Core watchdog (after Step 0 ack)

Implementation order:

1. `pah_watchdog.py` — single-file standalone Python script.
2. `start_watchdog.ps1` — launcher.
3. `tests/test_watchdog.py` — unit tests for: detect-dead, restart-clean, hit-restart-bound, log-rotation.
4. README section: how to start watchdog, how to stop, how to read its logs, how to install at Windows startup.

## Phase 2 — Tray integration (after Phase 1 stable)

1. Watchdog writes restart events to a state file PAH's tray reads.
2. Optional balloon popup for "PAH restarted" with a toggle in the tray menu.

## Constraints

- **Watchdog must NOT depend on PAH being alive.** It runs independently. If PAH is down, watchdog still functions.
- **Watchdog must NOT restart PAH faster than the cooldown.** If PAH crashes 10 times in 1 second (e.g., Python syntax error), watchdog must back off and notify, not enter an infinite restart loop.
- **Watchdog must NOT modify PAH state.** No reading mailbox dirs, no writing ledger entries. Process-level only.
- **No external network.** Localhost-only.
- **Dependency-free.** Stdlib only (`urllib`, `subprocess`, `time`, `pathlib`, `logging`).

## Definition of done

Step 0 ack: filed, parameters confirmed.
Phase 1 done when:
- Watchdog detects a deliberately-killed PAH within configured threshold.
- Watchdog restarts PAH and verifies `/api/health` responds.
- Watchdog hits the restart bound on a deliberately-broken PAH and emits notification.
- All four unit tests pass.
- README section added.

Phase 2 deferred until Phase 1 has run for at least 1 week without incident.

## Reporting protocol
- Step 0 ack → CD inbox.
- Phase 1 ready-to-commit → CD inbox.
- HOLD for Darrin "go" before commit.

## Tier rationale
**Medium** because scoped feature, well-defined, single file + tests + launcher. No architecture decisions beyond defaults already proposed.

— Claude Desktop, 2026-04-30 07:39
