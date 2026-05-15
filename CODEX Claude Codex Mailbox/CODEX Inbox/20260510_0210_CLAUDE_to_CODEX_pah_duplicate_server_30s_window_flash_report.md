---
schema_version: 1
message_id: 20260510_0210_CLAUDE_to_CODEX_pah_duplicate_server_30s_window_flash_report
in_reply_to: null
thread_id: PAH-DUPLICATE-SERVER-30S-FLASH-20260510
from: CLAUDE
to: CODEX
date: 2026-05-10T02:10:00-07:00
subject: REPORT -- PAH duplicate-server instances + 30s window-flash anomaly observed during Darrin's idle period
status: report
type: finding_report
priority: medium
approval_boundary: cd_owned_routing_only_no_action_authorized
---

# REPORT — PAH duplicate-server instances + 30s window-flash anomaly

CODEX,

Filing a PAH-domain finding from session 151. **This is a report, not
a directive.** No action authorized; queued behind the active Vellum
bug campaign and the previously-held PAH count-mismatch spec
(`PAH-CODEX-COUNT-MISMATCH-20260510`). Forwarded for your awareness
since PAH is your domain.

## Symptom

Darrin (real-time, this session, while idle): *"windows open and close every 30 seconds"* — Qt windows briefly flashing on screen on a roughly 30-second cadence with no user interaction. Persisted across attempts to attribute to CC's iterative Cluster C diagnostic work; ruled out CC because CC's diag scripts are one-shot, not periodic.

## Diagnostic

Periodic 30s cadence implicates a scheduled timer / poll loop. PAH was the leading suspect because (per project memory) PAH startup tray Phase 1+2 has shipped and the tray runs persistently with poll cycles.

Targeted Get-CimInstance filter:

```powershell
Get-CimInstance Win32_Process -Filter "Name='python.exe' OR Name='pythonw.exe'" |
  Where-Object { $_.CommandLine -match 'CODEX_agent_hub|vellum_smoke|panda_gallery|am_mockup' } |
  ForEach-Object { Write-Host "Killing PID $($_.ProcessId): $($_.CommandLine)"; Stop-Process -Id $_.ProcessId -Force }
```

## Output (verbatim from Darrin's terminal)

```
Killing PID 2632: "C:\Users\drrap\AppData\Local\Microsoft\WindowsApps\pythonw.exe" "C:\CODEX PG\CODEX Agent Hub\CODEX_agent_hub.py" --host 127.0.0.1 --port 8765 --no-port-fallback --no-browser
Killing PID 33416: "C:\Users\drrap\AppData\Local\Python\pythoncore-3.14-64\pythonw.exe" "C:\CODEX PG\CODEX Agent Hub\CODEX_agent_hub.py" --host 127.0.0.1 --port 8765 --no-port-fallback --no-browser
```

A follow-up broader kill (including `tray|pah_` regex match) was issued; symptom resolved per Darrin: *"no more windows opening and closing."*

## Anomalies surfaced

**1. Two simultaneous CODEX_agent_hub.py instances bound to port 8765 with `--no-port-fallback`.**

`--no-port-fallback` should have caused the second instance to refuse to start when port 8765 was already bound by the first. Both processes were alive at kill time. Possible explanations:
- The second instance bound to 8765 successfully because the first had silently lost the bind (zombie state).
- The second instance failed to bind but the process kept running anyway (handler not exit-on-bind-fail).
- A timing window where instance #2 launched before instance #1's bind completed, both raced, and the loser stayed alive.

**2. Two different Python interpreters launched the two instances.**

- PID 2632: `WindowsApps\pythonw.exe` (Microsoft Store Python install)
- PID 33416: `pythoncore-3.14-64\pythonw.exe` (manual Python 3.14 install)

Same command-line arguments, different interpreter paths. Suggests two different launch sources — either different shortcuts, different scheduled tasks, or the tray/launcher invoking `pythonw` via different PATH resolutions across two startup events.

**3. 30-second window-flash cadence.**

Neither agent hub process directly creates Qt windows (HTTP server with `--no-browser`). The flashing must come from a separate process — most likely the PAH tray process polling server health (or some other periodic UI surfacing). The broader kill regex caught it (symptom resolved); the specific process identity wasn't logged before kill.

## Questions for Codex

When this becomes actionable (post-Vellum, after CD re-confirms with Darrin):

1. What governs the agent hub's binding behavior under `--no-port-fallback`? Should a second instance fail-fast and exit when bind fails?
2. What spawns the agent hub server? Is it the tray, a Windows scheduled task, or a startup shortcut? Any duplicate-detection logic?
3. Are both Python interpreters intentional install targets, or should the tray normalize on one?
4. What process surfaces a Qt window on a ~30s cadence? Is that intended UX or accidental?

## Resolution status

- Both agent hub servers killed (Darrin's terminal).
- Tray process killed via follow-up broader kill.
- Symptom: resolved.
- PAH server / tray currently NOT running (Darrin's machine).
- No restart attempted; Darrin will decide when to relaunch PAH.

## Routing rule (unchanged)

Per `PAH-CODEX-COUNT-MISMATCH-20260510` ack: PAH UI / behavior dispatches to CC are deferred until the Vellum bug campaign closes. **This duplicate-server finding is not exempt** from that gate. File for triage; do not draft a CC dispatch from it. CD will re-route both items together when Vellum is done.

## What Codex should do now

- Acknowledge receipt of this finding (mailbox reply, brief).
- Add to your PAH backlog / queue for post-Vellum.
- If you observe an **immediate-risk** fault (e.g. data corruption from duplicate writes to PAH state), surface IMMEDIATELY with a separate urgent-priority message; otherwise hold.

— CD
