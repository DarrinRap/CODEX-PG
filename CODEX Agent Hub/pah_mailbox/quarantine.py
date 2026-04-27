"""Quarantine/tombstone mechanics for malformed mailbox files."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from pah_mailbox.atomic import atomic_write_text
from pah_mailbox.paths import MAILBOX_ROOT, QUARANTINE_DIR


@dataclass(frozen=True)
class QuarantineRecord:
    original_path: str
    quarantine_path: str
    reason: str
    moved_at: str
    tombstone_path: str = ""


def quarantine_target(path: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return QUARANTINE_DIR / f"{stamp}_{path.name}"


def write_tombstone(original_path: Path, record: QuarantineRecord) -> Path:
    tombstone = original_path.with_name(f"{original_path.name}.pah_tombstone.json")
    payload = {**record.__dict__, "tombstone_path": str(tombstone)}
    atomic_write_text(tombstone, json.dumps(payload, indent=2) + "\n")
    return tombstone


def validate_quarantine_candidate(path: Path, mailbox_root: Path = MAILBOX_ROOT) -> None:
    resolved = path.resolve()
    root = mailbox_root.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError("Quarantine candidate must be inside the PAH mailbox root.") from exc
    if QUARANTINE_DIR.resolve() in resolved.parents:
        raise ValueError("File is already inside quarantine.")
    if resolved.suffix.lower() != ".md":
        raise ValueError("Only Markdown mailbox messages can be quarantined.")
    if not resolved.exists():
        raise FileNotFoundError(str(resolved))


def quarantine_message(path: Path, reason: str, confirmed: bool = False) -> QuarantineRecord:
    if not confirmed:
        raise ValueError("Quarantine requires confirmed=true.")
    validate_quarantine_candidate(path)
    QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)
    target = quarantine_target(path)
    record = QuarantineRecord(
        original_path=str(path),
        quarantine_path=str(target),
        reason=reason.strip() or "manual_quarantine",
        moved_at=datetime.now().isoformat(timespec="seconds"),
    )
    os.replace(path, target)
    tombstone = write_tombstone(path, record)
    return QuarantineRecord(
        original_path=record.original_path,
        quarantine_path=record.quarantine_path,
        reason=record.reason,
        moved_at=record.moved_at,
        tombstone_path=str(tombstone),
    )
