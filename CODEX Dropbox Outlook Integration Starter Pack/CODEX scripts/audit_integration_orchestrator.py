"""Dry-run orchestrator for Dropbox intake + Outlook draft flow.

This script intentionally supports a local sample mode so Claude can implement
and test the orchestration before real Dropbox/Outlook credentials exist.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class AuditIntegrationError(RuntimeError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_sender_response(package_id: str, findings: list[dict[str, Any]]) -> dict[str, Any]:
    fix_now = [f for f in findings if f.get("disposition") == "fix_now"]
    amend = [f for f in findings if f.get("disposition") == "amend"]
    add = [f for f in findings if f.get("disposition") == "add"]
    clarify = [f for f in findings if f.get("disposition") == "clarify"]
    lines = ["Thanks. We reviewed your Panda Gallery testing package."]
    if fix_now:
        lines.append("\nWe will fix now:")
        lines.extend(f"- {item['title']}" for item in fix_now)
    if amend:
        lines.append("\nWe will amend:")
        lines.extend(f"- {item['title']}" for item in amend)
    if add:
        lines.append("\nWe will add to the feature list:")
        lines.extend(f"- {item['title']}" for item in add)
    if clarify:
        lines.append("\nWe need clarification:")
        lines.extend(f"- {item['title']}" for item in clarify)
    return {
        "schema": "pg.sender_response_draft.v1",
        "package_id": package_id,
        "to": ["tester@example.invalid"],
        "subject": "Panda Gallery testing report reviewed",
        "body_markdown": "\n".join(lines),
        "state": "draft_pending_human_review",
        "requires_human_send_approval": True,
    }


def run_local_sample(out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    findings = [
        {"title": "Instruction pane action row is clipped", "priority": "P0", "disposition": "fix_now"},
        {"title": "Region review dialog placement should be anchored", "priority": "P1", "disposition": "amend"},
        {"title": "Clearer capture status after region save", "priority": "P2", "disposition": "add"},
        {"title": "Wrong mount comment needs another screenshot", "priority": "P3", "disposition": "clarify"},
    ]
    response = build_sender_response("pkg_local_sample", findings)
    path = out_dir / "sender_response_draft_generated.json"
    path.write_text(json.dumps(response, indent=2), encoding="utf-8")
    return path


def main() -> int:
    output = run_local_sample(Path("C:/CODEX PG/CODEX Dropbox Outlook Integration Starter Pack/CODEX samples/generated"))
    print(f"Generated local sender response draft: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
