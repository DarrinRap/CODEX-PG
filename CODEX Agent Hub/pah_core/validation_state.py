"""Validation finding state for PANDA Agent Hub."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from pah_core.schema import content_hash
from pah_mailbox.atomic import atomic_write_text
from pah_mailbox.paths import VALIDATION_STATE_PATH


ACTIVE_STATE = "active"
VALIDATION_STATES = {"active", "resolved", "accepted_legacy", "dismissed"}
INACTIVE_VALIDATION_STATES = VALIDATION_STATES - {ACTIVE_STATE}


def validation_key(path: str, category: str, message: str) -> str:
    return content_hash(json.dumps({"path": path, "category": category, "message": message}, sort_keys=True))


def empty_state() -> dict[str, Any]:
    return {"version": 1, "updated_at": "", "items": {}}


def load_validation_state(path: Path = VALIDATION_STATE_PATH) -> dict[str, Any]:
    if not path.exists():
        return empty_state()
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError:
        return empty_state()
    if not isinstance(data, dict):
        return empty_state()
    data.setdefault("version", 1)
    data.setdefault("updated_at", "")
    data.setdefault("items", {})
    if not isinstance(data["items"], dict):
        data["items"] = {}
    return data


def save_validation_state(state: dict[str, Any], path: Path = VALIDATION_STATE_PATH) -> None:
    state["updated_at"] = datetime.now().isoformat(timespec="seconds")
    atomic_write_text(path, json.dumps(state, indent=2, sort_keys=True) + "\n")


def validation_record_for(fingerprint: str, state: dict[str, Any] | None = None) -> dict[str, Any]:
    data = state or load_validation_state()
    record = data.get("items", {}).get(fingerprint, {})
    return record if isinstance(record, dict) else {}


def validation_state_for(fingerprint: str, state: dict[str, Any] | None = None) -> str:
    record = validation_record_for(fingerprint, state)
    value = str(record.get("state", ACTIVE_STATE)).strip().lower()
    return value if value in VALIDATION_STATES else ACTIVE_STATE


def validation_is_active(fingerprint: str, state: dict[str, Any] | None = None) -> bool:
    return validation_state_for(fingerprint, state) == ACTIVE_STATE


def set_validation_state(
    fingerprint: str,
    state_name: str,
    note: str = "",
    actor: str = "codex",
    title: str = "",
    path_value: str = "",
    category: str = "",
    message: str = "",
    state_path: Path = VALIDATION_STATE_PATH,
) -> dict[str, Any]:
    normalized_state = str(state_name).strip().lower()
    if normalized_state not in VALIDATION_STATES:
        raise ValueError(f"Unsupported validation state: {state_name}")
    data = load_validation_state(state_path)
    if normalized_state == ACTIVE_STATE:
        data["items"].pop(fingerprint, None)
        save_validation_state(data, state_path)
        return {"state": ACTIVE_STATE}
    record = {
        "state": normalized_state,
        "note": note.strip(),
        "actor": actor.strip() or "codex",
        "title": title.strip(),
        "path": path_value.strip(),
        "category": category.strip(),
        "message": message.strip(),
        "updated_at": datetime.now().isoformat(timespec="seconds"),
    }
    data["items"][fingerprint] = record
    save_validation_state(data, state_path)
    return record


def validation_state_summary(state: dict[str, Any] | None = None) -> dict[str, Any]:
    data = state or load_validation_state()
    counts = {name: 0 for name in sorted(VALIDATION_STATES)}
    rows: list[dict[str, Any]] = []
    for fingerprint, record in data.get("items", {}).items():
        if not isinstance(record, dict):
            continue
        state_name = str(record.get("state", ACTIVE_STATE)).strip().lower()
        if state_name not in counts:
            state_name = ACTIVE_STATE
        counts[state_name] += 1
        rows.append({"fingerprint": fingerprint, **record})
    rows.sort(key=lambda item: str(item.get("updated_at", "")), reverse=True)
    return {
        "path": str(VALIDATION_STATE_PATH),
        "counts": counts,
        "items": rows,
        "updated_at": data.get("updated_at", ""),
    }

