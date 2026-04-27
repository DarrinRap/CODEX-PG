"""Decision queue state for PANDA Agent Hub."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from pah_mailbox.atomic import atomic_write_text
from pah_mailbox.paths import DECISION_STATE_PATH


ACTIVE_STATE = "active"
VALID_DECISION_STATES = {"active", "resolved", "superseded", "dismissed", "agent_decided"}
INACTIVE_DECISION_STATES = VALID_DECISION_STATES - {ACTIVE_STATE}


def decision_key(path: str | Path) -> str:
    return str(path)


def empty_state() -> dict[str, Any]:
    return {"version": 1, "updated_at": "", "items": {}}


def load_decision_state(path: Path = DECISION_STATE_PATH) -> dict[str, Any]:
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


def save_decision_state(state: dict[str, Any], path: Path = DECISION_STATE_PATH) -> None:
    state["updated_at"] = datetime.now().isoformat(timespec="seconds")
    atomic_write_text(path, json.dumps(state, indent=2, sort_keys=True) + "\n")


def decision_record_for(path: str | Path, state: dict[str, Any] | None = None) -> dict[str, Any]:
    data = state or load_decision_state()
    record = data.get("items", {}).get(decision_key(path), {})
    return record if isinstance(record, dict) else {}


def decision_state_for(path: str | Path, state: dict[str, Any] | None = None) -> str:
    record = decision_record_for(path, state)
    value = str(record.get("state", ACTIVE_STATE)).strip().lower()
    return value if value in VALID_DECISION_STATES else ACTIVE_STATE


def decision_is_active(path: str | Path, state: dict[str, Any] | None = None) -> bool:
    return decision_state_for(path, state) == ACTIVE_STATE


def set_decision_state(
    path: str | Path,
    state_name: str,
    note: str = "",
    actor: str = "codex",
    title: str = "",
    state_path: Path = DECISION_STATE_PATH,
) -> dict[str, Any]:
    normalized_state = str(state_name).strip().lower()
    if normalized_state not in VALID_DECISION_STATES:
        raise ValueError(f"Unsupported decision state: {state_name}")
    data = load_decision_state(state_path)
    key = decision_key(path)
    record = {
        "state": normalized_state,
        "note": note.strip(),
        "actor": actor.strip() or "codex",
        "title": title.strip(),
        "updated_at": datetime.now().isoformat(timespec="seconds"),
    }
    if normalized_state == ACTIVE_STATE:
        data["items"].pop(key, None)
    else:
        data["items"][key] = record
    save_decision_state(data, state_path)
    return record


def decision_state_summary(state: dict[str, Any] | None = None) -> dict[str, Any]:
    data = state or load_decision_state()
    counts = {name: 0 for name in sorted(VALID_DECISION_STATES)}
    rows: list[dict[str, Any]] = []
    for path, record in data.get("items", {}).items():
        if not isinstance(record, dict):
            continue
        state_name = str(record.get("state", ACTIVE_STATE)).strip().lower()
        if state_name not in counts:
            state_name = ACTIVE_STATE
        counts[state_name] += 1
        rows.append({"path": path, **record})
    rows.sort(key=lambda item: str(item.get("updated_at", "")), reverse=True)
    return {
        "path": str(DECISION_STATE_PATH),
        "counts": counts,
        "items": rows,
        "updated_at": data.get("updated_at", ""),
    }

