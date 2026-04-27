"""Idempotency and duplicate message detection."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from pah_core.schema import content_hash
from pah_mailbox.atomic import atomic_write_text
from pah_mailbox.paths import PROCESSED_MESSAGES_DIR


DEFAULT_PROCESSED_EVENT = "message_seen"


@dataclass(frozen=True)
class DuplicateIdConflict:
    message_id: str
    first_path: Path
    second_path: Path
    first_hash: str
    second_hash: str


@dataclass(frozen=True)
class ProcessedMessageEventStatus:
    status: str
    message_id: str
    event: str
    sidecar_path: Path
    content_hash: str
    existing_hash: str = ""


def detect_duplicate_conflict(
    seen: dict[str, tuple[Path, str]], message_id: str, path: Path, text: str
) -> DuplicateIdConflict | None:
    digest = content_hash(text)
    if message_id not in seen:
        seen[message_id] = (path, digest)
        return None
    first_path, first_hash = seen[message_id]
    if first_hash == digest:
        return None
    return DuplicateIdConflict(message_id, first_path, path, first_hash, digest)


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def normalize_processed_event(event: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9_.:-]+", "_", event.strip().lower()).strip("_")
    return normalized or DEFAULT_PROCESSED_EVENT


def processed_message_sidecar_path(message_id: str, state_dir: Path = PROCESSED_MESSAGES_DIR) -> Path:
    normalized_id = message_id.strip()
    if not normalized_id:
        raise ValueError("Processed message sidecar requires a message id.")
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "-", normalized_id).strip(".-")[:80]
    digest = content_hash(normalized_id)[:12]
    return state_dir / f"{slug or 'message'}-{digest}.json"


def _empty_record(message_id: str, digest: str, source_path: Path, timestamp: str) -> dict[str, Any]:
    return {
        "version": 1,
        "message_id": message_id,
        "content_hash": digest,
        "first_seen_at": timestamp,
        "last_seen_at": timestamp,
        "first_path": str(source_path),
        "last_path": str(source_path),
        "events": {},
    }


def load_processed_message_record(message_id: str, state_dir: Path = PROCESSED_MESSAGES_DIR) -> dict[str, Any] | None:
    sidecar_path = processed_message_sidecar_path(message_id, state_dir)
    if not sidecar_path.exists():
        return None
    try:
        data = json.loads(sidecar_path.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    data.setdefault("version", 1)
    data.setdefault("message_id", message_id)
    data.setdefault("content_hash", "")
    data.setdefault("first_seen_at", "")
    data.setdefault("last_seen_at", "")
    data.setdefault("first_path", "")
    data.setdefault("last_path", "")
    data.setdefault("events", {})
    if not isinstance(data["events"], dict):
        data["events"] = {}
    return data


def processed_message_event_status(
    message_id: str,
    source_path: Path,
    text: str,
    event: str = DEFAULT_PROCESSED_EVENT,
    state_dir: Path = PROCESSED_MESSAGES_DIR,
) -> ProcessedMessageEventStatus:
    event_name = normalize_processed_event(event)
    digest = content_hash(text)
    sidecar_path = processed_message_sidecar_path(message_id, state_dir)
    record = load_processed_message_record(message_id, state_dir)
    if record is None:
        return ProcessedMessageEventStatus("unseen", message_id, event_name, sidecar_path, digest)
    existing_hash = str(record.get("content_hash", ""))
    if existing_hash != digest:
        return ProcessedMessageEventStatus(
            "content_mismatch",
            message_id,
            event_name,
            sidecar_path,
            digest,
            existing_hash=existing_hash,
        )
    if event_name in record.get("events", {}):
        return ProcessedMessageEventStatus(
            "already_processed",
            message_id,
            event_name,
            sidecar_path,
            digest,
            existing_hash=existing_hash,
        )
    return ProcessedMessageEventStatus("new_event", message_id, event_name, sidecar_path, digest, existing_hash=existing_hash)


def record_processed_message_event(
    message_id: str,
    source_path: Path,
    text: str,
    event: str = DEFAULT_PROCESSED_EVENT,
    outcome: str = "processed",
    state_dir: Path = PROCESSED_MESSAGES_DIR,
) -> dict[str, Any]:
    status = processed_message_event_status(message_id, source_path, text, event, state_dir)
    if status.status == "content_mismatch":
        raise ValueError(
            f"Processed sidecar hash mismatch for message id {message_id}: "
            f"{status.existing_hash} != {status.content_hash}"
        )
    if status.status == "already_processed":
        record = load_processed_message_record(message_id, state_dir)
        return record if record is not None else {}

    timestamp = _now_iso()
    record = load_processed_message_record(message_id, state_dir)
    if record is None:
        record = _empty_record(message_id, status.content_hash, source_path, timestamp)
    record["last_seen_at"] = timestamp
    record["last_path"] = str(source_path)
    events = record.setdefault("events", {})
    events[status.event] = {
        "outcome": outcome.strip() or "processed",
        "processed_at": timestamp,
        "path": str(source_path),
    }
    status.sidecar_path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_text(status.sidecar_path, json.dumps(record, indent=2, sort_keys=True) + "\n")
    return record
