"""Atomic file write helpers for local mailbox state."""

from __future__ import annotations

import os
from pathlib import Path


def atomic_write_text(path: Path, text: str, encoding: str = "utf-8") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f".{path.name}.tmp")
    temp_path.write_text(text, encoding=encoding)
    os.replace(temp_path, path)


def atomic_append_text(path: Path, text: str, encoding: str = "utf-8") -> None:
    existing = ""
    if path.exists():
        existing = path.read_text(encoding=encoding, errors="replace")
    atomic_write_text(path, existing + text, encoding=encoding)

