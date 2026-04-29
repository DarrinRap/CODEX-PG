"""Communication diagnostics for PAH routes and local bridge readiness."""

from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from pah_core.participants import PARTICIPANTS, ROUTES
from pah_mailbox.atomic import atomic_write_text
from pah_mailbox.paths import (
    CC_CLAUDE_INBOX,
    CC_INBOX,
    CC_MAILBOX_ROOT,
    CODEX_INBOX,
    DIAGNOSTICS_DIR,
    PROJECT_ROOT,
    ROUTE_INBOXES,
)


def check_result(name: str, ok: bool, detail: str, severity: str = "info") -> dict[str, Any]:
    return {"name": name, "ok": ok, "severity": severity, "detail": detail}


def route_detail(route: str) -> str:
    source, target = ROUTES[route]
    inbox = ROUTE_INBOXES[route]
    return f"{source} -> {target} via {inbox}"


def run_relay_health_check() -> dict[str, Any]:
    script_path = PROJECT_ROOT / "CODEX Automation" / "CODEX_relay_health_check.ps1"
    if not script_path.exists():
        return check_result(
            "relay_health",
            False,
            f"Relay health checker is missing: {script_path}",
            "warning",
        )

    powershell = shutil.which("powershell") or shutil.which("pwsh")
    if not powershell:
        return check_result(
            "relay_health",
            False,
            "PowerShell is not available; relay health checker could not run.",
            "warning",
        )

    try:
        completed = subprocess.run(
            [
                powershell,
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(script_path),
                "-Json",
                "-NoFail",
                "-UpdateCache",
            ],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
    except Exception as exc:  # pragma: no cover - diagnostics should degrade gently
        return check_result("relay_health", False, f"Relay health checker failed to run: {exc}", "warning")

    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or f"exit code {completed.returncode}"
        return check_result("relay_health", False, f"Relay health checker failed: {detail}", "warning")

    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        detail = completed.stdout.strip()[:500]
        return check_result(
            "relay_health",
            False,
            f"Relay health checker returned invalid JSON: {exc}. Output: {detail}",
            "warning",
        )

    counts = payload.get("counts", {})
    cache = payload.get("cache", {})
    errors = int(counts.get("errors", 0) or 0)
    warnings = int(counts.get("warnings", 0) or 0)
    status = str(payload.get("status", "warn"))
    ok = status == "ok" and errors == 0 and warnings == 0
    severity = "error" if errors else "warning" if warnings else "info"
    detail = (
        f"Relay health {status}: {counts.get('active_rows', 0)} active row(s), "
        f"{counts.get('unindexed_recent_codex_mail', 0)} unindexed recent CODEX mail, "
        f"{counts.get('recent_unread_incoming', 0)} unread recent incoming, "
        f"{counts.get('recent_darrin_gates', 0)} recent Darrin gate(s), "
        f"cache {cache.get('hits', 0)} hit(s)/{cache.get('misses', 0)} miss(es)."
    )
    result = check_result("relay_health", ok, detail, severity)
    result["relay_health"] = payload
    return result


def run_communication_diagnostics(write_report: bool = False) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    required = {"darrin", "pah", "codex", "claude-desktop", "claude-code"}
    missing = sorted(required.difference(PARTICIPANTS))
    checks.append(
        check_result(
            "participant_registry",
            not missing,
            "All required participants registered." if not missing else f"Missing participants: {', '.join(missing)}",
            "error" if missing else "info",
        )
    )

    for route in ("codex_to_claude", "codex_to_claude_code", "claude_to_codex"):
        inbox = ROUTE_INBOXES[route]
        exists = inbox.exists()
        checks.append(
            check_result(
                f"route:{route}",
                exists,
                route_detail(route) if exists else f"Route inbox is missing: {inbox}",
                "warning" if not exists else "info",
            )
        )

    checks.append(
        check_result(
            "native_claude_code_mailbox",
            CC_MAILBOX_ROOT.exists() and CC_INBOX.exists() and CC_CLAUDE_INBOX.exists(),
            f"Claude Code native mailbox is available at {CC_MAILBOX_ROOT}"
            if CC_MAILBOX_ROOT.exists() and CC_INBOX.exists() and CC_CLAUDE_INBOX.exists()
            else f"Claude Code native mailbox is missing or incomplete: {CC_MAILBOX_ROOT}",
            "warning" if not (CC_MAILBOX_ROOT.exists() and CC_INBOX.exists() and CC_CLAUDE_INBOX.exists()) else "info",
        )
    )

    codex_ready = CODEX_INBOX.exists()
    outbound_ready = all(ROUTE_INBOXES[route].exists() for route in ("codex_to_claude", "codex_to_claude_code"))
    claude_code_reply_ready = CC_CLAUDE_INBOX.exists()
    checks.append(
        check_result(
            "two_way_file_bridge",
            codex_ready and outbound_ready and claude_code_reply_ready,
            "Codex, Claude Desktop, and native Claude Code mailbox paths are present for two-way file bridge testing."
            if codex_ready and outbound_ready and claude_code_reply_ready
            else "One or more mailbox paths are missing; live agent roundtrip is not ready.",
            "warning" if not (codex_ready and outbound_ready and claude_code_reply_ready) else "info",
        )
    )

    checks.append(
        check_result(
            "live_adapters",
            True,
            "OpenAI/Anthropic/Claude Code headless adapters are disabled by default; diagnostics are file-bridge only.",
        )
    )
    checks.append(run_relay_health_check())

    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "ok": all(item["ok"] for item in checks),
        "checks": checks,
    }
    if write_report:
        DIAGNOSTICS_DIR.mkdir(parents=True, exist_ok=True)
        report = DIAGNOSTICS_DIR / "CODEX_last_communication_diagnostics.md"
        lines = ["# PAH Communication Diagnostics", "", f"Generated: {summary['generated_at']}", ""]
        for item in checks:
            marker = "PASS" if item["ok"] else "FAIL"
            lines.extend([f"## {marker}: {item['name']}", "", item["detail"], ""])
        atomic_write_text(report, "\n".join(lines))
        summary["report_path"] = str(report)
    return summary
