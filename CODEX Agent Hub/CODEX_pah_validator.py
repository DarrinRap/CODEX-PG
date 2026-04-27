"""Standalone PAH message validator CLI.

This validates PAH mailbox Markdown messages without importing or calling any
Panda Gallery runtime code.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from pah_core.schema import content_hash, extract_message_metadata, validate_message_text


def validate_path(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    issues = validate_message_text(text, path.name)
    warnings = [issue for issue in issues if issue.level == "warning"]
    errors = [issue for issue in issues if issue.level == "error"]
    return {
        "path": str(path),
        "ok": not warnings and not errors,
        "content_hash": content_hash(text),
        "metadata": {
            key: value
            for key, value in extract_message_metadata(text).items()
            if not key.startswith("_")
        },
        "issues": [{"level": issue.level, "message": issue.message} for issue in issues],
        "summary": {
            "errors": len(errors),
            "warnings": len(warnings),
            "info": sum(1 for issue in issues if issue.level == "info"),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate PAH v1 Markdown mailbox messages.")
    parser.add_argument("paths", nargs="+", help="Markdown message path(s) to validate.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args(argv)

    results: list[dict[str, Any]] = []
    for raw_path in args.paths:
        path = Path(raw_path)
        if not path.exists():
            results.append(
                {
                    "path": str(path),
                    "ok": False,
                    "metadata": {},
                    "issues": [{"level": "error", "message": "File does not exist"}],
                    "summary": {"errors": 1, "warnings": 0, "info": 0},
                }
            )
            continue
        results.append(validate_path(path))

    ok = all(result["ok"] for result in results)
    payload = {"ok": ok, "results": results}
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        for result in results:
            status = "OK" if result["ok"] else "CHECK"
            print(f"{status} {result['path']}")
            for issue in result["issues"]:
                print(f"  {issue['level']}: {issue['message']}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
