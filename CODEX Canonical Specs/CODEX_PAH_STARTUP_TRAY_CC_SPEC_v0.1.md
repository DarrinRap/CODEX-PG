# CODEX PAH Startup Tray and Watchdog CC Spec v0.1

Created: 2026-05-06
Owner: Codex draft for Darrin/CD review; CC implementation only after CD authorization
Scope: PANDA Agent Hub startup tray, login startup, server lifecycle, local health/watchdog behavior
Status: Draft, not dispatched, not approved

## 1. Purpose

PAH should be available without manual terminal babysitting. This spec upgrades the existing PAH tray launcher into a safer startup/watchdog surface that can start PAH at Windows login, show honest status, recover from simple server failures, and avoid duplicate or hidden server processes.

This is not a PAH cockpit redesign. It is an operational reliability feature around the existing PAH server and existing tray script.

## 2. Existing Evidence

Existing files under `C:\CODEX PG\CODEX Agent Hub`:

- `CODEX_start_agent_hub_tray.ps1` already provides a Windows tray icon, context menu, startup shortcut install/remove actions, status polling, dashboard open action, and limited restart behavior.
- `CODEX_launch_agent_hub_dashboard.ps1` starts the tray if needed, attaches tray-only mode when a server is already listening, and opens the dashboard.
- `CODEX_run_server_smoke.ps1` starts a temporary PAH server and checks `/api/ping`, `/api/ready`, `/api/health`, and `/api/cockpit`.
- `CODEX_agent_hub.py` is the PAH server, normally on `127.0.0.1:8765`.

Recent validation showed PAH normally performs well, but one heartbeat saw `/api/health` refused while TCP port `8765` still reported a listener on PID `81836`. That should be treated as a recoverable service-health signal, not as a reason to hide the problem or spawn duplicate processes.

## 3. Non-Goals

- Do not redesign the PAH dashboard UI.
- Do not touch Relay files.
- Do not stage, commit, revert, archive, or clean parked dirty files.
- Do not send implementation-go or commit-go directly from Codex to CC.
- Do not add network services, external dependencies, scheduled tasks requiring administrator rights, or broad machine changes.
- Do not auto-open browser tabs at login unless explicitly configured.
- Do not enable intrusive popups by default.

## 4. Required Behavior

### 4.1 Startup Mode

Add a guarded startup mode to the existing tray script or a small companion script.

Requirements:

1. Startup is opt-in only through the tray menu or explicit command.
2. Startup creates a user-level Windows Startup shortcut only; no admin service or machine-wide install.
3. Startup shortcut launches PowerShell hidden, STA, with the PAH tray script and explicit port.
4. Startup shortcut must be removable from the tray menu.
5. The tray menu must clearly indicate startup state: installed or not installed.
6. Installing startup must not immediately create a second tray/server if one is already running.

### 4.2 Single-Instance Guard

Before starting any server or tray instance, the launcher must check:

1. Is another `CODEX_start_agent_hub_tray.ps1` already running for the same port?
2. Is `127.0.0.1:8765` listening?
3. If listening, do `/api/ping` and `/api/ready` respond as PAH?
4. If listening but not PAH, treat as port conflict and do not start a new server.
5. If tray exists and server is healthy, bring/open existing dashboard instead of starting another tray.

Acceptance: double-clicking launcher repeatedly should not create duplicate tray icons or duplicate PAH Python servers.

### 4.3 Server Ownership Rules

The tray must distinguish these states:

- `owned_server`: tray started this PAH Python process and may restart/stop it.
- `attached_server`: PAH was already running; tray may monitor it but must not kill it on exit.
- `port_conflict`: port is occupied by something that is not PAH; tray must show conflict and avoid starting.
- `offline`: no listener and server start failed or was disabled.

On tray exit:

- Kill only a server process this tray started.
- Never kill a server the tray merely attached to.

### 4.4 Health Classification

The tray must poll `/api/tray-status` for normal status. If that fails, it must degrade through these checks:

1. TCP listener check.
2. `/api/ping` readiness check.
3. `/api/ready` readiness check.
4. `/api/health` full health check only after readiness passes.

Display states:

- Running: PAH tray-status reachable.
- Warn: tray-status reachable with warnings, or readiness works but health/cockpit fails.
- Starting: server process exists but readiness has not passed yet.
- Down: no listener and no owned process.
- Conflict: listener exists but does not identify as PAH.
- Restarting: tray is attempting bounded recovery.

### 4.5 Restart Policy

Automatic restart is allowed only for an `owned_server`.

Rules:

1. Maximum 3 restart attempts within 10 minutes.
2. After 3 failed attempts, stop restarting and show Down/Warn with log path.
3. Restart only after confirming the owned process exited or readiness has failed for at least 2 consecutive polls.
4. Do not restart on a single slow `/api/health` response while `/api/ping` and `/api/ready` still pass.
5. Write every restart attempt to a JSONL log with timestamp, reason, pid, port, and outcome.

### 4.6 Tray Menu

Required menu items:

- Open Dashboard
- Refresh Status
- Run Health Check
- Restart PAH Server, enabled only for `owned_server`; attached servers may show `Open Dashboard` and `Run Health Check` but must not be restarted or killed by the tray
- Open PAH Folder
- Open Logs
- Install at Windows Startup / Remove Windows Startup
- Copy Status Summary
- Exit Tray

Menu labels should avoid implying Darrin authorization or CC work approval.

### 4.7 Run Health Check Action

The tray `Run Health Check` action must run a bounded local check against the current PAH URL without starting a second temporary server:

1. `/api/ping`
2. `/api/ready`
3. `/api/tray-status`
4. `/api/health`

It should show a concise result in the tray status fields and write details to the health transition/lifecycle log. It must not run `CODEX_run_server_smoke.ps1` from the tray because that script starts its own temporary server for verification.

### 4.8 Logging

Add or extend logs under `C:\CODEX PG\CODEX Agent Hub\CODEX logs`:

- Tray lifecycle log: starts, exits, ownership state, startup shortcut changes.
- Server lifecycle log: pid, port, command, stdout/stderr paths, restart attempts.
- Health transition log: only on state changes, not every poll.

Logs must not include secrets or mailbox message bodies.

### 4.9 Configuration

Use a small local config file, preferably under `CODEX Agent Hub\CODEX config`, for non-sensitive tray settings:

- port, default `8765`
- poll seconds, default `15`
- startup installed state, observed from shortcut existence rather than trusted blindly
- alert popups enabled, default `false`
- auto open dashboard at login, default `false`
- restart attempts and cooldown parameters

Do not store absolute Python interpreter assumptions unless discovered at runtime.

### 4.10 Security and Permission Boundaries

- Use user-level Startup folder only.
- No scheduled task unless Darrin separately approves.
- No admin elevation.
- No public network binding; PAH remains `127.0.0.1` only.
- No changes to firewall rules.
- No automatic mailbox mutation from tray.

### 4.11 Backward Compatibility

The current dashboard launcher must keep working:

- If PAH is down, it starts tray + server and opens dashboard once ready.
- If PAH server is running but no tray exists, it starts tray in attach/no-server mode.
- If tray and server are running, it opens or refreshes the existing dashboard.

Existing command parameters should remain compatible:

- `-Port`
- `-PollSeconds`
- `-AlertCooldownMinutes`
- `-NoServer`

Any new parameters must be optional.

## 5. Implementation Plan for CC

### Phase 0: Step 0 RTC Only

CC must first file a Step 0 RTC to CD with:

1. Exact files proposed for modification.
2. Whether CC will modify only PowerShell scripts or also Python tests.
3. Proposed single-instance detection method.
4. Proposed config/log file names.
5. Verification command list.
6. Any ambiguity about killing attached servers.

No implementation before CD answers and issues the appropriate CC authorization.

### Phase 1: Tray Hardening

Likely files:

- `C:\CODEX PG\CODEX Agent Hub\CODEX_start_agent_hub_tray.ps1`
- `C:\CODEX PG\CODEX Agent Hub\CODEX_launch_agent_hub_dashboard.ps1`

Tasks:

1. Add explicit ownership state.
2. Add startup shortcut state detection.
3. Harden duplicate tray detection.
4. Add conflict detection.
5. Add bounded restart state machine.
6. Add Copy Status Summary and Run Health Check actions.
7. Add lifecycle/transition logging.

### Phase 2: Verification Harness

Add or extend a focused script if needed, for example:

- `C:\CODEX PG\CODEX Agent Hub\CODEX_pah_tray_startup_verify.ps1`

Verification should avoid requiring actual Windows login. It can validate shortcut creation/removal, single-instance predicates, port conflict behavior where safe, and launcher readiness behavior.

### Phase 3: Manual Startup Test

Manual validation checklist:

1. Remove startup shortcut.
2. Install startup from tray.
3. Verify shortcut exists in user Startup folder and points to expected script.
4. Launch the shortcut manually.
5. Confirm only one tray exists; if the tray launched the server, exactly one owned PAH Python server exists; if attaching, no ownership is claimed.
6. Open dashboard from tray.
7. Run Health Check from tray.
8. Exit tray and confirm owned server stops; attached server is not killed.
9. Remove startup from tray unless Darrin explicitly asks to leave it installed.

## 6. Acceptance Criteria

Implementation is acceptable only if:

- No duplicate tray/server processes after repeated launcher clicks.
- Startup shortcut install/remove works without admin rights.
- Validation does not leave startup installed unless Darrin explicitly asks to leave it installed.
- Port conflict is surfaced clearly and tray startup uses `--no-port-fallback`; it must not start PAH on a surprise fallback port.
- Owned vs attached server behavior is correct.
- Restart is bounded and logged.
- Dashboard launcher remains backward compatible.
- Existing PAH smoke tests still pass.
- `CODEX_run_server_smoke.ps1` still passes.
- Live endpoint verification still passes when PAH is running.
- No Relay files, mailbox protocol files, parked UI/UX artifacts, or unrelated dirty files are modified.

## 7. Recommended Verification Commands

Run from `C:\CODEX PG` or the PAH folder as appropriate:

```powershell
python "C:\CODEX PG\CODEX Agent Hub\CODEX_run_smoke_tests.py"
& "C:\CODEX PG\CODEX Agent Hub\CODEX_run_server_smoke.ps1"
python "C:\CODEX PG\CODEX Agent Hub\CODEX_pah_live_endpoint_verify.py"
python "C:\CODEX PG\CODEX Agent Hub\CODEX_pah_periodic_health_check.py"
```

Also manually test tray actions because tray behavior cannot be fully proven by headless tests.

## 8. Risks

- PowerShell tray behavior depends on STA and Windows Forms; this must stay explicit.
- Duplicate detection through process command lines can be brittle when quoting changes.
- Killing the wrong process is the highest-risk behavior; ownership state must be conservative.
- Startup shortcut can break if the repo path moves; tray should report this clearly.
- Health endpoint can be transiently slow; restart policy must avoid overreacting.

## 9. Approval Boundary

This spec is draft-only until Darrin approves it and CD dispatches CC. Codex may recommend and route through CD, but Codex must not send implementation-go or commit-go directly to CC.



