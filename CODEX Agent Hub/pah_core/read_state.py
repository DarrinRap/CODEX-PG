"""Read/unread state for PANDA Agent Hub messages."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from pah_core.schema import content_hash
from pah_mailbox.atomic import atomic_write_text
from pah_mailbox.paths import READ_STATE_PATH


READ_STATE = "read"
UNREAD_STATE = "unread"
READ_STATES = {READ_STATE, UNREAD_STATE}


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def message_read_key(path: Path | str) -> str:
    return str(path)


def empty_read_state() -> dict[str, Any]:
    return {"version": 1, "updated_at": "", "items": {}}


def load_read_state(path: Path = READ_STATE_PATH) -> dict[str, Any]:
    if not path.exists():
        return empty_read_state()
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError:
        return empty_read_state()
    if not isinstance(data, dict):
        return empty_read_state()
    data.setdefault("version", 1)
    data.setdefault("updated_at", "")
    data.setdefault("items", {})
    if not isinstance(data["items"], dict):
        data["items"] = {}
    return data


def save_read_state(state: dict[str, Any], path: Path = READ_STATE_PATH) -> None:
    state["updated_at"] = _now_iso()
    atomic_write_text(path, json.dumps(state, indent=2, sort_keys=True) + "\n")


def read_record_for(path: Path | str, state: dict[str, Any] | None = None) -> dict[str, Any]:
    data = state or load_read_state()
    record = data.get("items", {}).get(message_read_key(path), {})
    return record if isinstance(record, dict) else {}


def message_read_status(path: Path | str, message_id: str, text: str, state: dict[str, Any] | None = None) -> dict[str, Any]:
    digest = content_hash(text)
    record = read_record_for(path, state)
    state_name = str(record.get("state", UNREAD_STATE)).strip().lower()
    if state_name not in READ_STATES:
        state_name = UNREAD_STATE
    stored_hash = str(record.get("content_hash", ""))
    changed = bool(stored_hash and stored_hash != digest)
    unread = state_name != READ_STATE or changed
    return {
        "state": UNREAD_STATE if unread else READ_STATE,
        "unread": unread,
        "content_hash": digest,
        "stored_hash": stored_hash,
        "content_changed": changed,
        "read_at": str(record.get("read_at", "")),
        "updated_at": str(record.get("updated_at", "")),
        "actor": str(record.get("actor", "")),
        "message_id": message_id,
    }


def set_message_read_state(
    path_value: Path | str,
    message_id: str,
    text: str,
    state_name: str,
    actor: str = "codex",
    state_path: Path = READ_STATE_PATH,
) -> dict[str, Any]:
    normalized = state_name.strip().lower()
    if normalized not in READ_STATES:
        raise ValueError(f"Unsupported read state: {state_name}")
    data = load_read_state(state_path)
    timestamp = _now_iso()
    record = {
        "state": normalized,
        "message_id": message_id,
        "content_hash": content_hash(text),
        "actor": actor.strip() or "codex",
        "updated_at": timestamp,
    }
    if normalized == READ_STATE:
        record["read_at"] = timestamp
    data["items"][message_read_key(path_value)] = record
    save_read_state(data, state_path)
    return record


def read_state_summary(state: dict[str, Any] | None = None) -> dict[str, Any]:
    data = state or load_read_state()
    counts = {READ_STATE: 0, UNREAD_STATE: 0}
    for record in data.get("items", {}).values():
        if not isinstance(record, dict):
            continue
        state_name = str(record.get("state", UNREAD_STATE)).strip().lower()
        if state_name not in counts:
            state_name = UNREAD_STATE
        counts[state_name] += 1
    return {
        "path": str(READ_STATE_PATH),
        "counts": counts,
        "updated_at": data.get("updated_at", ""),
    }
