#!/usr/bin/env python3
"""PANDA Collaborator local-only action test inspector."""

from __future__ import annotations

import sys
from pathlib import Path

import panda_collaborator as pc


def fail(message: str) -> None:
    print(f"FAIL {message}")
    raise SystemExit(1)


def check(condition: bool, message: str) -> None:
    if not condition:
        fail(message)
    print(f"PASS {message}")


def main() -> int:
    result = pc.run_pc_action_test()
    run_root = Path(result["run_root"]).resolve()
    print(f"RUN {result['run_id']}")
    print(f"EVIDENCE {result.get('evidence_markdown_path', '')}")

    check(result["status"] == "PASS", "PC action test returns PASS")
    check(result["phase"] == "local-only", "Action test is local-only")
    check(not result["external_side_effects"], "No external side effects were performed")
    check(not result["destructive_git_commands_run"], "No destructive Git commands were run")
    check(not result["github_repo_created"], "No GitHub repo was created")
    check(result["real_values_redacted"], "Real normal-state values are redacted")
    check(result["users"] == ["Bob", "Karen"], "Action test uses Bob and Karen")
    check(all(item["ok"] for item in result["checkpoints"]), "All action-test checkpoints passed")
    check(Path(result["handoff_package_path"], "manifest.json").exists(), "Handoff package manifest exists")
    check(Path(result["daily_report_path"]).exists(), "Daily report exists")
    check(Path(result["evidence_json_path"]).exists(), "JSON evidence report exists")
    check(Path(result["evidence_markdown_path"]).exists(), "Markdown evidence report exists")

    for key in ("handoff_package_path", "daily_report_path", "evidence_json_path", "evidence_markdown_path"):
        Path(result[key]).resolve().relative_to(run_root)
    print("PASS All generated evidence stays inside the timestamped run folder")

    print("\nAction test applet passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
