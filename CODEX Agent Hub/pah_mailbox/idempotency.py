"""Idempotency and duplicate message detection."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pah_core.schema import content_hash


@dataclass(frozen=True)
class DuplicateIdConflict:
    message_id: str
    first_path: Path
    second_path: Path
    first_hash: str
    second_hash: str


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

