"""Mailbox route tests for PANDA Agent Hub.

These tests create explicit diagnostic ping messages through the file bridge and
track whether a reply appears later. They do not launch agents or call APIs.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from pah_core import MESSAGE_SCHEMA_VERSION
from pah_core.participants import participant_label, route_participants
from pah_core.schema import extract_message_metadata, render_message_markdown
from pah_mailbox.atomic import atomic_write_text
from pah_mailbox.paths import CC_CLAUDE_INBOX, CODEX_INBOX, ROUTE_INBOXES, ROUTE_TEST_STATE_PATH


ROUTE_TEST_ROUTES = {"codex_to_claude", "codex_to_claude_code"}


def empty_route_test_state() -> dict[str, Any]:
    return {"version": 1, "updated_at": "", "tests": {}}


def load_route_test_state(path: Path = ROUTE_TEST_STATE_PATH) -> dict[str, Any]:
    if not path.exists():
        return empty_route_test_state()
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError:
        return empty_route_test_state()
    if not isinstance(data, dict):
        return empty_route_test_state()
    data.setdefault("version", 1)
    data.setdefault("updated_at", "")
    data.setdefault("tests", {})
    if not isinstance(data["tests"], dict):
        data["tests"] = {}
    return data


def save_route_test_state(state: dict[str, Any], path: Path = ROUTE_TEST_STATE_PATH) -> None:
    state["updated_at"] = datetime.now().isoformat(timespec="seconds")
    atomic_write_text(path, json.dumps(state, indent=2, sort_keys=True) + "\n")


def route_test_id(route: str) -> str:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"PAH-ROUTE-TEST-{stamp}-{route}"


def create_route_test(route: str, note: str = "", state_path: Path = ROUTE_TEST_STATE_PATH) -> dict[str, Any]:
    if route not in ROUTE_TEST_ROUTES:
        raise ValueError(f"Unsupported route test: {route}")
    from_id, to_id = route_participants(route)
    target_inbox = ROUTE_INBOXES[route]
    target_inbox.mkdir(parents=True, exist_ok=True)
    reply_targets = reply_search_dirs_for_route(route)
    reply_instruction = str(reply_targets[0]) if reply_targets else str(CODEX_INBOX)

    test_id = route_test_id(route)
    created_at = datetime.now().astimezone().isoformat(timespec="seconds")
    subject = f"PAH route test: {participant_label(from_id)} to {participant_label(to_id)}"
    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{from_id.upper().replace('-', '_')}_to_{to_id.upper().replace('-', '_')}_pah_route_test.md"
    path = target_inbox / filename
    metadata = {
        "schema_version": MESSAGE_SCHEMA_VERSION,
        "message_id": test_id,
        "thread_id": test_id,
        "created_at": created_at,
        "from": from_id,
        "to": to_id,
        "type": "diagnostic_result",
        "priority": "normal",
        "status": "open",
        "thread_status": "waiting_on_agent",
        "approval_boundary": "coordination_only",
        "requires_darrin_decision": False,
    }
    details = "\n".join(
        [
            "This is a PANDA Agent Hub communication diagnostic ping.",
            "",
            f"Please reply into `{reply_instruction}` with:",
            f"- Reply-To: {test_id}",
            f"- Thread-ID: {test_id}",
            "- A short confirmation that you received the route test.",
            "",
            note.strip() or "No additional note.",
        ]
    )
    text = render_message_markdown(metadata, subject, "Diagnostic ping for PAH file-bridge routing.", details)
    atomic_write_text(path, text)

    state = load_route_test_state(state_path)
    record = {
        "test_id": test_id,
        "route": route,
        "from": from_id,
        "to": to_id,
        "created_at": created_at,
        "message_path": str(path),
        "state": "pending_reply",
        "reply_path": "",
        "reply_seen_at": "",
        "note": note.strip(),
    }
    state["tests"][test_id] = record
    save_route_test_state(state, state_path)
    return record


def reply_search_dirs_for_route(route: str) -> list[Path]:
    if route == "codex_to_claude_code" and CC_CLAUDE_INBOX.exists():
        return [CC_CLAUDE_INBOX, CODEX_INBOX]
    return [CODEX_INBOX]


def read_text(path: Path) -> str:
    for encoding in ("utf-8-sig", "utf-8", "cp1252"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(errors="replace")


def message_replies_to_test(path: Path, test_id: str) -> bool:
    try:
        text = read_text(path)
    except OSError:
        return False
    metadata = extract_message_metadata(text)
    if str(metadata.get("thread_id", "")) == test_id:
        return True
    reply_to = metadata.get("reply_to", [])
    if isinstance(reply_to, list) and any(test_id in str(item) for item in reply_to):
        return True
    return test_id in text[:2000]


def refresh_route_tests(state_path: Path = ROUTE_TEST_STATE_PATH) -> dict[str, Any]:
    state = load_route_test_state(state_path)
    changed = False
    for test_id, record in list(state.get("tests", {}).items()):
        if not isinstance(record, dict):
            continue
        if record.get("state") == "received_reply":
            continue
        for inbox in reply_search_dirs_for_route(str(record.get("route", ""))):
            if not inbox.exists():
                continue
            for path in inbox.glob("*.md"):
                if message_replies_to_test(path, test_id):
                    record["state"] = "received_reply"
                    record["reply_path"] = str(path)
                    record["reply_seen_at"] = datetime.now().isoformat(timespec="seconds")
                    changed = True
                    break
            if record.get("state") == "received_reply":
                break
    if changed:
        save_route_test_state(state, state_path)
    return state


def route_test_status(refresh: bool = True, state_path: Path = ROUTE_TEST_STATE_PATH) -> dict[str, Any]:
    state = refresh_route_tests(state_path) if refresh else load_route_test_state(state_path)
    tests = [record for record in state.get("tests", {}).values() if isinstance(record, dict)]
    tests.sort(key=lambda item: str(item.get("created_at", "")), reverse=True)
    counts: dict[str, int] = {}
    for record in tests:
        state_name = str(record.get("state", "unknown"))
        counts[state_name] = counts.get(state_name, 0) + 1
    return {
        "path": str(state_path),
        "counts": counts,
        "tests": tests[:30],
        "updated_at": state.get("updated_at", ""),
    }
