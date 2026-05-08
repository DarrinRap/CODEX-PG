"""Read-only live endpoint verifier for PAH.

This script intentionally avoids POST routes and message-specific GET routes
that can open files or depend on user-selected paths.
"""

from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


DEFAULT_BASE_URL = "http://127.0.0.1:8765"


@dataclass(frozen=True)
class EndpointCheck:
    path: str
    required_keys: tuple[str, ...] = ("ok",)
    ok_values: tuple[bool, ...] | None = None


READ_ONLY_ENDPOINTS: tuple[EndpointCheck, ...] = (
    EndpointCheck("/api/ping", ("ok", "service"), (True,)),
    EndpointCheck("/api/ready", ("schema_version", "server_ready")),
    EndpointCheck("/api/launch-refresh/state", ("ok", "token", "active_clients")),
    EndpointCheck("/api/cockpit", ("generated_at", "health", "cockpit_state")),
    EndpointCheck("/api/health", ("schema_version", "overall", "operational", "blocking_failure", "components")),
    EndpointCheck("/api/tray-status", ("ok", "level", "counts")),
    EndpointCheck("/api/inspector-report", ("ok", "report")),
    EndpointCheck("/api/cc-activity", ("ok", "card")),
    EndpointCheck("/api/communication-speed-tests?limit=3", ("ok", "history"), (True,)),
    EndpointCheck("/api/status", ("generated_at", "counts", "watcher")),
    EndpointCheck("/api/watcher/status", ("ok", "mode", "alerts", "counts"), (True,)),
    EndpointCheck("/api/watcher/events?limit=3", ("ok", "events"), (True,)),
    EndpointCheck("/api/interaction-ledger?limit=3", ("ok", "events"), (True,)),
)


def fetch_json(base_url: str, path: str, timeout: float = 10.0) -> tuple[int, dict[str, Any]]:
    url = base_url.rstrip("/") + path
    with urlopen(url, timeout=timeout) as response:
        status = int(getattr(response, "status", 200))
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} returned non-object JSON")
    return status, payload


def verify_endpoint(base_url: str, check: EndpointCheck) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        status, payload = fetch_json(base_url, check.path)
        missing = [key for key in check.required_keys if key not in payload]
        ok_value = payload.get("ok")
        ok_allowed = check.ok_values is None or ok_value in check.ok_values
        passed = 200 <= status < 300 and not missing and ok_allowed
        return {
            "path": check.path,
            "ok": passed,
            "http_status": status,
            "duration_ms": round((time.perf_counter() - started) * 1000, 2),
            "missing_keys": missing,
            "ok_value": ok_value,
            "required_ok_values": list(check.ok_values) if check.ok_values is not None else None,
        }
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, ValueError) as exc:
        return {
            "path": check.path,
            "ok": False,
            "error": str(exc),
            "duration_ms": round((time.perf_counter() - started) * 1000, 2),
        }


def verify_live_endpoints(base_url: str = DEFAULT_BASE_URL) -> dict[str, Any]:
    results = [verify_endpoint(base_url, check) for check in READ_ONLY_ENDPOINTS]
    failed = [item for item in results if not item.get("ok")]
    return {
        "ok": not failed,
        "base_url": base_url,
        "checked": len(results),
        "failed": len(failed),
        "results": results,
    }


def main(argv: list[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    base_url = args[0] if args else DEFAULT_BASE_URL
    report = verify_live_endpoints(base_url)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
