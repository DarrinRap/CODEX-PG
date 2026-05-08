"""Run repeat PAH periodic health checks against the live server."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parent
URL = "http://127.0.0.1:8765"


def fetch_health() -> dict[str, object]:
    with urlopen(f"{URL}/api/health", timeout=8) as response:
        return json.loads(response.read().decode("utf-8", errors="replace"))


def run_periodic_once(index: int) -> dict[str, object]:
    result = subprocess.run(
        [sys.executable, str(ROOT / "CODEX_pah_periodic_health_check.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=240,
        check=False,
    )
    payload: dict[str, object] = {
        "run": index,
        "ok": result.returncode == 0,
        "returncode": result.returncode,
        "stdout_tail": result.stdout.strip()[-1000:],
        "stderr_tail": result.stderr.strip()[-1000:],
    }
    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError:
        report = {}
    if isinstance(report, dict):
        payload["report_ok"] = bool(report.get("ok"))
        payload["warnings"] = report.get("warnings", [])
        payload["duration_ms"] = report.get("duration_ms", 0)
    return payload


def main() -> int:
    before = fetch_health()
    runs = [run_periodic_once(1), run_periodic_once(2)]
    after = fetch_health()
    ok = all(bool(run.get("ok")) and bool(run.get("report_ok")) for run in runs)
    output = {
        "ok": ok,
        "url": URL,
        "before_overall": before.get("overall", ""),
        "after_overall": after.get("overall", ""),
        "runs": runs,
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
