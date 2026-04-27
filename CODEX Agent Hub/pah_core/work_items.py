"""Local work-board state for PANDA Agent Hub."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from pah_core.participants import PARTICIPANTS, canonical_participant
from pah_core.schema import content_hash, extract_message_metadata
from pah_mailbox.atomic import atomic_write_text
from pah_mailbox.paths import CODEX_INBOX, WORK_ITEMS_STATE_PATH


WORK_STATES = {"todo", "in_progress", "blocked", "review", "complete", "cancelled"}
WORK_PRIORITIES = {"low", "normal", "high", "urgent"}


def empty_work_state() -> dict[str, Any]:
    return {"version": 1, "updated_at": "", "items": {}}


def load_work_state(path: Path = WORK_ITEMS_STATE_PATH) -> dict[str, Any]:
    if not path.exists():
        return empty_work_state()
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError:
        return empty_work_state()
    if not isinstance(data, dict):
        return empty_work_state()
    data.setdefault("version", 1)
    data.setdefault("updated_at", "")
    data.setdefault("items", {})
    if not isinstance(data["items"], dict):
        data["items"] = {}
    return data


def save_work_state(state: dict[str, Any], path: Path = WORK_ITEMS_STATE_PATH) -> None:
    state["updated_at"] = datetime.now().isoformat(timespec="seconds")
    atomic_write_text(path, json.dumps(state, indent=2, sort_keys=True) + "\n")


def read_text(path: Path) -> str:
    for encoding in ("utf-8-sig", "utf-8", "cp1252"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(errors="replace")


def work_item_id(title: str) -> str:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in title).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return f"PAH-WORK-{stamp}-{slug[:36] or content_hash(title)[:8]}"


def normalize_owner(value: str) -> str:
    owner = canonical_participant(value)
    if owner not in PARTICIPANTS:
        raise ValueError(f"Unknown work owner: {value}")
    return owner


def normalize_state(value: str) -> str:
    state = str(value or "todo").strip().lower()
    if state not in WORK_STATES:
        raise ValueError(f"Unsupported work state: {value}")
    return state


def normalize_priority(value: str) -> str:
    priority = str(value or "normal").strip().lower()
    if priority not in WORK_PRIORITIES:
        raise ValueError(f"Unsupported work priority: {value}")
    return priority


def create_work_item(
    title: str,
    owner: str = "codex",
    priority: str = "normal",
    summary: str = "",
    source: str = "",
    state_path: Path = WORK_ITEMS_STATE_PATH,
) -> dict[str, Any]:
    clean_title = " ".join(str(title or "").split())
    if not clean_title:
        raise ValueError("Work item title is required.")
    item_id = work_item_id(clean_title)
    now = datetime.now().isoformat(timespec="seconds")
    item = {
        "item_id": item_id,
        "title": clean_title,
        "owner": normalize_owner(owner),
        "priority": normalize_priority(priority),
        "state": "todo",
        "summary": summary.strip(),
        "source": source.strip(),
        "created_at": now,
        "updated_at": now,
    }
    state_data = load_work_state(state_path)
    state_data["items"][item_id] = item
    save_work_state(state_data, state_path)
    return item


def update_work_item(
    item_id: str,
    owner: str | None = None,
    state: str | None = None,
    priority: str | None = None,
    summary: str | None = None,
    dispatch: dict[str, Any] | None = None,
    state_path: Path = WORK_ITEMS_STATE_PATH,
) -> dict[str, Any]:
    state_data = load_work_state(state_path)
    if item_id not in state_data["items"]:
        raise KeyError(f"Unknown work item: {item_id}")
    item = dict(state_data["items"][item_id])
    if owner is not None:
        item["owner"] = normalize_owner(owner)
    if state is not None:
        item["state"] = normalize_state(state)
    if priority is not None:
        item["priority"] = normalize_priority(priority)
    if summary is not None:
        item["summary"] = summary.strip()
    if dispatch is not None:
        item["dispatch"] = dispatch
        item["dispatched_at"] = dispatch.get("dispatched_at", datetime.now().isoformat(timespec="seconds"))
    item["updated_at"] = datetime.now().isoformat(timespec="seconds")
    state_data["items"][item_id] = item
    save_work_state(state_data, state_path)
    return item


def reply_matches_work_item(path: Path, item: dict[str, Any]) -> bool:
    try:
        text = read_text(path)
    except OSError:
        return False
    item_id = str(item.get("item_id", ""))
    dispatch = item.get("dispatch", {}) if isinstance(item.get("dispatch"), dict) else {}
    dispatch_message_id = str(dispatch.get("message_id", ""))
    metadata = extract_message_metadata(text)
    if str(metadata.get("thread_id", "")) == item_id:
        return True
    reply_to = metadata.get("reply_to", [])
    if isinstance(reply_to, list):
        joined = "\n".join(str(value) for value in reply_to)
        if item_id and item_id in joined:
            return True
        if dispatch_message_id and dispatch_message_id in joined:
            return True
    probe = text[:2500]
    return bool((item_id and item_id in probe) or (dispatch_message_id and dispatch_message_id in probe))


def refresh_work_item_replies(
    state_path: Path = WORK_ITEMS_STATE_PATH,
    inbox_path: Path = CODEX_INBOX,
) -> dict[str, Any]:
    state_data = load_work_state(state_path)
    if not inbox_path.exists():
        return state_data
    changed = False
    replies = list(inbox_path.glob("*.md"))
    for item_id, item_value in list(state_data.get("items", {}).items()):
        if not isinstance(item_value, dict):
            continue
        item = dict(item_value)
        if item.get("last_reply_path"):
            continue
        if not isinstance(item.get("dispatch"), dict):
            continue
        for reply_path in replies:
            if reply_matches_work_item(reply_path, item):
                item["last_reply_path"] = str(reply_path)
                item["last_reply_seen_at"] = datetime.now().isoformat(timespec="seconds")
                if item.get("state") not in {"complete", "cancelled"}:
                    item["state"] = "review"
                item["updated_at"] = datetime.now().isoformat(timespec="seconds")
                state_data["items"][item_id] = item
                changed = True
                break
    if changed:
        save_work_state(state_data, state_path)
    return state_data


def work_board_status(
    state_path: Path = WORK_ITEMS_STATE_PATH,
    refresh_replies: bool = True,
    inbox_path: Path = CODEX_INBOX,
) -> dict[str, Any]:
    state_data = refresh_work_item_replies(state_path, inbox_path) if refresh_replies else load_work_state(state_path)
    items = [item for item in state_data.get("items", {}).values() if isinstance(item, dict)]
    items.sort(key=lambda item: str(item.get("updated_at", "")), reverse=True)
    by_state = {name: 0 for name in sorted(WORK_STATES)}
    by_owner: dict[str, int] = {}
    for item in items:
        state_name = str(item.get("state", "todo"))
        if state_name not in by_state:
            state_name = "todo"
        by_state[state_name] += 1
        owner = str(item.get("owner", "unknown"))
        by_owner[owner] = by_owner.get(owner, 0) + 1
    return {
        "path": str(state_path),
        "items": items[:100],
        "counts": {"total": len(items), "by_state": by_state, "by_owner": by_owner},
        "updated_at": state_data.get("updated_at", ""),
    }
