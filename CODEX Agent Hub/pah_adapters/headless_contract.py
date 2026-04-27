"""Headless Claude Code command contract for PAH.

This module defines the command shape only. It does not launch Claude Code.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


CANONICAL_CLAUDE_BINARY = "claude"
HEADLESS_ALLOWED_TOOLS = ("Read", "Grep", "Glob", "WebFetch")
HEADLESS_ALLOWED_TOOL_SET = set(HEADLESS_ALLOWED_TOOLS)
HEADLESS_DEFAULT_TIMEOUT_SECONDS = 600
HEADLESS_SIGKILL_GRACE_SECONDS = 30
HEADLESS_COMMAND_REQUIRED_FIELDS = {
    "prompt_file",
    "allowed_tools",
    "disallowed_tools",
    "settings_path",
    "worktree_path",
    "budget_usd",
    "command_preview",
    "audit_stdout_path",
    "audit_stderr_path",
    "audit_exit_code_path",
}


def _string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value or "").strip()
    if not text:
        return []
    return [item.strip() for item in text.split(",") if item.strip()]


def _tool_arg(value: Any) -> str:
    return ",".join(_string_list(value))


def _allowed_tool_arg(value: Any) -> str:
    selected = set(_string_list(value))
    return ",".join(tool for tool in HEADLESS_ALLOWED_TOOLS if tool in selected)


def _positive_int(value: Any, default: int) -> int:
    if value in {None, ""}:
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return -1
    return parsed


def canonical_headless_command_args(record: dict[str, Any]) -> list[str]:
    return [
        CANONICAL_CLAUDE_BINARY,
        "-p",
        str(record.get("prompt_file", "")),
        "--output-format",
        "json",
        "--permission-mode",
        "plan",
        "--allowedTools",
        _allowed_tool_arg(record.get("allowed_tools")),
        "--disallowedTools",
        _tool_arg(record.get("disallowed_tools")),
        "--strict-mcp-config",
        "--mcp-config",
        str(record.get("mcp_config_path", "")),
        "--settings",
        str(record.get("settings_path", "")),
        "--cwd",
        str(record.get("worktree_path", "")),
        "--max-budget-usd",
        str(record.get("budget_usd", "")),
        "--no-session-persistence",
    ]


def canonical_headless_command_preview(record: dict[str, Any]) -> str:
    return subprocess.list2cmdline(canonical_headless_command_args(record))


def headless_capture_contract(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "stdout_path": str(record.get("audit_stdout_path", "")),
        "stderr_path": str(record.get("audit_stderr_path", "")),
        "exit_code_path": str(record.get("audit_exit_code_path", "")),
        "consume_approval_on_exit": True,
        "process_timeout_seconds": _positive_int(
            record.get("process_timeout_seconds"),
            HEADLESS_DEFAULT_TIMEOUT_SECONDS,
        ),
        "sigterm_on_timeout": True,
        "sigkill_grace_seconds": _positive_int(
            record.get("sigkill_grace_seconds"),
            HEADLESS_SIGKILL_GRACE_SECONDS,
        ),
    }


def validate_headless_command_contract(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = sorted(field for field in HEADLESS_COMMAND_REQUIRED_FIELDS if field not in record)
    errors.extend(f"Missing headless command field: {field}" for field in missing)

    allowed_tools = set(_string_list(record.get("allowed_tools")))
    if not allowed_tools:
        errors.append("allowed_tools must name at least one read-only tool")
    unexpected_tools = sorted(allowed_tools - HEADLESS_ALLOWED_TOOL_SET)
    if unexpected_tools:
        errors.append(f"allowed_tools contains non-read-only tools: {', '.join(unexpected_tools)}")

    if not _string_list(record.get("disallowed_tools")):
        errors.append("disallowed_tools must be nonempty for headless agent runs")

    if "budget_usd" in record and str(record.get("budget_usd")) != str(record.get("budget", "")):
        errors.append("budget_usd must match approval budget")

    for field in ("prompt_file", "settings_path", "worktree_path", "audit_stdout_path", "audit_stderr_path", "audit_exit_code_path"):
        if field in record and not str(record.get(field, "")).strip():
            errors.append(f"{field} must be nonempty")

    capture = headless_capture_contract(record)
    if capture["process_timeout_seconds"] <= 0:
        errors.append("process_timeout_seconds must be a positive integer")
    if capture["sigkill_grace_seconds"] <= 0:
        errors.append("sigkill_grace_seconds must be a positive integer")

    preview = canonical_headless_command_preview(record)
    if "command_preview" in record and str(record.get("command_preview", "")) != preview:
        errors.append("command_preview must match canonical headless command")
    if str(record.get("command_or_provider", "")) and str(record.get("command_or_provider", "")) != preview:
        errors.append("command_or_provider must match canonical headless command")

    # Keep this as a literal path check only; path existence is an executor concern.
    if "worktree_path" in record and Path(str(record.get("worktree_path", ""))).name == "":
        errors.append("worktree_path must identify a temporary worktree path")
    return errors
