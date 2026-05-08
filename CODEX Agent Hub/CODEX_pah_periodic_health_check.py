"""Run periodic PAH server and mailbox coordination health checks."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parent
LOG_DIR = ROOT / "CODEX logs"
LATEST_PATH = LOG_DIR / "CODEX_pah_periodic_health_latest.json"
HISTORY_PATH = LOG_DIR / "CODEX_pah_periodic_health.jsonl"
URL = "http://127.0.0.1:8765"
DEFAULT_RUN_INTERVAL_MINUTES = 10
CRITICAL_CHECKS = {
    "participant_registry",
    "route:codex_to_claude",
    "route:codex_to_claude_code",
    "route:claude_to_codex",
    "native_claude_code_mailbox",
    "two_way_file_bridge",
}


import CODEX_agent_hub as agent_hub


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def run_interval_minutes() -> int:
    raw = os.environ.get("PAH_PERIODIC_HEALTH_INTERVAL_MINUTES", "").strip()
    if not raw:
        return DEFAULT_RUN_INTERVAL_MINUTES
    try:
        return max(1, int(raw))
    except ValueError:
        return DEFAULT_RUN_INTERVAL_MINUTES


def steward_schedule(run_started_at: str) -> dict[str, Any]:
    interval_minutes = run_interval_minutes()
    try:
        next_run_after = (datetime.fromisoformat(run_started_at) + timedelta(minutes=interval_minutes)).isoformat(
            timespec="seconds"
        )
    except ValueError:
        next_run_after = ""
    return {
        "interval_minutes": interval_minutes,
        "last_run_started_at": run_started_at,
        "next_run_after": next_run_after,
        "source": "PAH_PERIODIC_HEALTH_INTERVAL_MINUTES",
    }


def fetch_json(path: str, timeout: int = 8) -> dict[str, Any]:
    with urlopen(f"{URL}{path}", timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8", errors="replace"))


def run_command(args: list[str], timeout: int = 120) -> dict[str, Any]:
    started = time.perf_counter()
    result = subprocess.run(
        args,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    return {
        "ok": result.returncode == 0,
        "returncode": result.returncode,
        "duration_ms": int((time.perf_counter() - started) * 1000),
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def listener_check() -> dict[str, Any]:
    command = [
        "powershell",
        "-NoProfile",
        "-Command",
        (
            "$conn = Get-NetTCPConnection -LocalPort 8765 -State Listen -ErrorAction SilentlyContinue | "
            "Select-Object -First 1; "
            "if ($conn) { "
            "$proc = Get-CimInstance Win32_Process -Filter \"ProcessId=$($conn.OwningProcess)\" "
            "-ErrorAction SilentlyContinue; "
            "[PSCustomObject]@{ok=$true; pid=$conn.OwningProcess; commandLine=$proc.CommandLine} | ConvertTo-Json -Compress "
            "} else { [PSCustomObject]@{ok=$false; pid=''; commandLine=''} | ConvertTo-Json -Compress }"
        ),
    ]
    result = run_command(command, timeout=20)
    if not result["ok"]:
        return {"ok": False, "error": result["stderr"] or result["stdout"]}
    try:
        payload = json.loads(result["stdout"])
    except json.JSONDecodeError:
        return {"ok": False, "error": "Could not parse listener check output.", "raw": result["stdout"]}
    command_line = str(payload.get("commandLine", ""))
    return {
        "ok": bool(payload.get("ok")) and "CODEX_agent_hub.py" in command_line,
        "pid": payload.get("pid", ""),
        "command_line": command_line,
    }


def critical_diagnostics(status: dict[str, Any]) -> dict[str, Any]:
    checks = status.get("diagnostics", {}).get("checks", [])
    by_name = {str(item.get("name", "")): item for item in checks if isinstance(item, dict)}
    failed = [
        {
            "name": name,
            "detail": str(by_name.get(name, {}).get("detail", "missing check")),
        }
        for name in sorted(CRITICAL_CHECKS)
        if not bool(by_name.get(name, {}).get("ok"))
    ]
    return {"ok": not failed, "failed": failed}


def tray_consistency(cockpit: dict[str, Any], tray: dict[str, Any]) -> dict[str, Any]:
    wake_candidates = cockpit.get("wake_candidates", [])
    expected_stale = len(wake_candidates) if isinstance(wake_candidates, list) else 0
    tray_stale = int(tray.get("counts", {}).get("stale_unread", 0) or 0)
    return {
        "ok": expected_stale == tray_stale,
        "expected_stale_unread": expected_stale,
        "tray_stale_unread": tray_stale,
    }


def communication_backlog(cockpit: dict[str, Any]) -> dict[str, Any]:
    counts = cockpit.get("cockpit_state", {}).get("counts", {})
    open_on_agent = int(counts.get("open_on_agent", 0) or 0)
    owner_unknown = int(counts.get("owner_unknown", 0) or 0)
    open_on_darrin = int(counts.get("open_on_darrin", 0) or 0)
    items = cockpit.get("thread_focus", {})
    has_owner_unknown = owner_unknown > 0
    return {
        "ok": not has_owner_unknown,
        "advisory": True,
        "level": "warn" if has_owner_unknown else "ok",
        "open_on_agent": open_on_agent,
        "owner_unknown": owner_unknown,
        "open_on_darrin": open_on_darrin,
        "agent_threads": [
            {"title": item.get("title", ""), "thread_id": item.get("thread_id", ""), "owner": item.get("owner", "")}
            for item in items.get("open_on_agent", [])[:10]
        ],
        "owner_unknown_threads": [
            {"title": item.get("title", ""), "thread_id": item.get("thread_id", "")}
            for item in items.get("owner_unknown", [])[:10]
        ],
    }


def record_communication_backlog_event(backlog: dict[str, Any]) -> dict[str, Any] | None:
    if backlog.get("ok"):
        return None
    return agent_hub.append_interaction_ledger_event(
        "mailbox_discrepancy_detected",
        actor="periodic_health_monitor",
        open_on_agent=backlog.get("open_on_agent", 0),
        owner_unknown=backlog.get("owner_unknown", 0),
        open_on_darrin=backlog.get("open_on_darrin", 0),
        agent_threads=backlog.get("agent_threads", []),
        owner_unknown_threads=backlog.get("owner_unknown_threads", []),
    )


def periodic_checks_ok(checks: dict[str, Any]) -> bool:
    return all(
        bool(item.get("ok"))
        for item in checks.values()
        if isinstance(item, dict) and not bool(item.get("advisory"))
    )


def archive_read_sweep() -> dict[str, Any]:
    try:
        result = agent_hub.archive_read_codex_inbox_messages(actor="periodic_health_monitor", dry_run=False)
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
    return {
        "ok": True,
        "protocol_version": result.get("protocol_version", 0),
        "moved": result.get("count", 0),
        "skipped_waiting_on_darrin": result.get("skipped_waiting_on_darrin", 0),
        "skipped_pre_staged_pending_trigger": result.get("skipped_pre_staged_pending_trigger", 0),
        "skipped_pending_dispatch": result.get("skipped_pending_dispatch", 0),
        "skipped_active_thread": result.get("skipped_active_thread", 0),
        "skipped_unstructured": result.get("skipped_unstructured", 0),
        "archive_conflicts": result.get("archive_conflicts", 0),
        "inbox_summary": result.get("inbox_summary", []),
    }


def write_report(report: dict[str, Any]) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    LATEST_PATH.write_text(text, encoding="utf-8")
    with HISTORY_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(report, sort_keys=True) + "\n")


def main() -> int:
    started = time.perf_counter()
    run_started_at = now_iso()
    agent_hub.append_interaction_ledger_event(
        "steward_check_started",
        actor="periodic_health_monitor",
        url=URL,
        started_at=run_started_at,
    )
    report: dict[str, Any] = {
        "generated_at": run_started_at,
        "url": URL,
        "ok": False,
        "schedule": steward_schedule(run_started_at),
        "checks": {},
        "warnings": [],
    }
    archive_sweep = archive_read_sweep()
    try:
        status = fetch_json("/api/status")
        tray = fetch_json("/api/tray-status")
        cockpit = fetch_json("/api/cockpit")
        health = fetch_json("/api/health")
    except (OSError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        report["checks"]["server_endpoints"] = {"ok": False, "error": str(exc)}
        report["duration_ms"] = int((time.perf_counter() - started) * 1000)
        agent_hub.append_interaction_ledger_event(
            "steward_check_finished",
            actor="periodic_health_monitor",
            ok=False,
            error=str(exc),
            duration_ms=report["duration_ms"],
        )
        write_report(report)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1

    smoke = run_command([sys.executable, str(ROOT / "CODEX_run_smoke_tests.py")], timeout=180)
    listener = listener_check()
    diagnostics = critical_diagnostics(status)
    tray_match = tray_consistency(cockpit, tray)
    backlog = communication_backlog(cockpit)
    discrepancy_event = record_communication_backlog_event(backlog)

    report["checks"] = {
        "server_endpoints": {"ok": True},
        "archive_read_sweep": archive_sweep,
        "health_endpoint": {
            "ok": health.get("schema_version") == 1 and health.get("overall") in {"ok", "warn", "err", "unknown"},
            "overall": health.get("overall", ""),
            "components": sorted((health.get("components") or {}).keys()),
        },
        "listener": listener,
        "smoke_tests": smoke,
        "critical_diagnostics": diagnostics,
        "communication_backlog": backlog,
        "tray_consistency": tray_match,
    }
    if discrepancy_event is not None:
        report["interaction_ledger"] = {
            "event_type": discrepancy_event.get("event_type", ""),
            "time": discrepancy_event.get("time", ""),
            "path": str(agent_hub.INTERACTION_LEDGER_PATH),
        }
    report["status_summary"] = {
        "messages": status.get("counts", {}).get("messages", 0),
        "open_on_agent": backlog.get("open_on_agent", 0),
        "owner_unknown": backlog.get("owner_unknown", 0),
        "open_on_darrin": backlog.get("open_on_darrin", 0),
        "unread": status.get("counts", {}).get("unread_messages", 0),
        "archived_read_messages": archive_sweep.get("moved", 0),
        "tray_level": tray.get("level", ""),
        "health_overall": health.get("overall", ""),
        "stale_unread": tray.get("counts", {}).get("stale_unread", 0),
        "diagnostic_problems": tray.get("counts", {}).get("diagnostic_problems", 0),
    }
    if int(tray.get("counts", {}).get("stale_unread", 0) or 0) > 0:
        report["warnings"].append("PAH has stale unread mailbox items that may need attention.")
    if int(tray.get("counts", {}).get("diagnostic_problems", 0) or 0) > 0:
        report["warnings"].append("PAH reports diagnostic warnings/errors; critical route checks are evaluated separately.")
    if int(archive_sweep.get("moved", 0) or 0) > 0:
        report["warnings"].append(f"PAH archived {archive_sweep.get('moved')} read mailbox item(s) during this maintenance run.")
    if not backlog.get("ok"):
        report["warnings"].append(
            f"PAH has unanswered communication backlog: {backlog.get('open_on_agent')} open on agents; "
            f"{backlog.get('owner_unknown')} owner unknown."
        )

    report["ok"] = periodic_checks_ok(report["checks"])
    report["duration_ms"] = int((time.perf_counter() - started) * 1000)
    agent_hub.append_interaction_ledger_event(
        "steward_check_finished",
        actor="periodic_health_monitor",
        ok=report["ok"],
        duration_ms=report["duration_ms"],
        warnings=report["warnings"],
        status_summary=report["status_summary"],
    )
    write_report(report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
