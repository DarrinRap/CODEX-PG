"""Closed-thread archive state for PANDA Agent Hub."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from pah_mailbox.atomic import atomic_write_text
from pah_mailbox.paths import THREAD_ARCHIVE_STATE_PATH


ARCHIVED_STATE = "archived"
ACTIVE_STATE = "active"
ARCHIVE_STATES = {ACTIVE_STATE, ARCHIVED_STATE}


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def empty_archive_state() -> dict[str, Any]:
    return {"version": 1, "updated_at": "", "threads": {}}


def load_thread_archive_state(path: Path = THREAD_ARCHIVE_STATE_PATH) -> dict[str, Any]:
    if not path.exists():
        return empty_archive_state()
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError:
        return empty_archive_state()
    if not isinstance(data, dict):
        return empty_archive_state()
    data.setdefault("version", 1)
    data.setdefault("updated_at", "")
    data.setdefault("threads", {})
    if not isinstance(data["threads"], dict):
        data["threads"] = {}
    return data


def save_thread_archive_state(state: dict[str, Any], path: Path = THREAD_ARCHIVE_STATE_PATH) -> None:
    state["updated_at"] = _now_iso()
    atomic_write_text(path, json.dumps(state, indent=2, sort_keys=True) + "\n")


def thread_archive_record(thread_id: str, state: dict[str, Any] | None = None) -> dict[str, Any]:
    data = state or load_thread_archive_state()
    record = data.get("threads", {}).get(thread_id, {})
    return record if isinstance(record, dict) else {}


def thread_archive_status(
    thread_id: str,
    latest_modified: float,
    state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    record = thread_archive_record(thread_id, state)
    archived_latest = float(record.get("latest_modified", 0) or 0)
    state_name = str(record.get("state", ACTIVE_STATE)).strip().lower()
    if state_name not in ARCHIVE_STATES:
        state_name = ACTIVE_STATE
    reopened = state_name == ARCHIVED_STATE and latest_modified > archived_latest
    archived = state_name == ARCHIVED_STATE and not reopened
    return {
        "archived": archived,
        "reopened_by_new_activity": reopened,
        "state": ACTIVE_STATE if reopened else state_name,
        "archived_at": str(record.get("archived_at", "")),
        "archive_reason": str(record.get("reason", "")),
        "archive_actor": str(record.get("actor", "")),
        "latest_modified_at_archive": archived_latest,
    }


def archive_thread(
    thread_id: str,
    *,
    latest_path: str,
    latest_title: str,
    latest_modified: float,
    reason: str = "",
    actor: str = "codex",
    state_path: Path = THREAD_ARCHIVE_STATE_PATH,
) -> dict[str, Any]:
    clean_thread = thread_id.strip()
    if not clean_thread:
        raise ValueError("Thread ID is required for archive.")
    data = load_thread_archive_state(state_path)
    record = {
        "state": ARCHIVED_STATE,
        "thread_id": clean_thread,
        "latest_path": latest_path,
        "latest_title": latest_title,
        "latest_modified": latest_modified,
        "reason": reason.strip(),
        "actor": actor.strip() or "codex",
        "archived_at": _now_iso(),
    }
    data["threads"][clean_thread] = record
    save_thread_archive_state(data, state_path)
    return record


def unarchive_thread(
    thread_id: str,
    *,
    actor: str = "codex",
    reason: str = "",
    state_path: Path = THREAD_ARCHIVE_STATE_PATH,
) -> dict[str, Any]:
    clean_thread = thread_id.strip()
    if not clean_thread:
        raise ValueError("Thread ID is required for unarchive.")
    data = load_thread_archive_state(state_path)
    record = data.get("threads", {}).get(clean_thread, {})
    if not isinstance(record, dict):
        record = {"thread_id": clean_thread}
    record.update(
        {
            "state": ACTIVE_STATE,
            "actor": actor.strip() or "codex",
            "reason": reason.strip(),
            "unarchived_at": _now_iso(),
        }
    )
    data["threads"][clean_thread] = record
    save_thread_archive_state(data, state_path)
    return record


def thread_archive_summary(state: dict[str, Any] | None = None) -> dict[str, Any]:
    data = state or load_thread_archive_state()
    counts = {ACTIVE_STATE: 0, ARCHIVED_STATE: 0}
    for record in data.get("threads", {}).values():
        if not isinstance(record, dict):
            continue
        state_name = str(record.get("state", ACTIVE_STATE)).strip().lower()
        if state_name not in counts:
            state_name = ACTIVE_STATE
        counts[state_name] += 1
    return {
        "path": str(THREAD_ARCHIVE_STATE_PATH),
        "counts": counts,
        "updated_at": data.get("updated_at", ""),
    }
