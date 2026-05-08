"""Atomic file write helpers for local mailbox state."""

from __future__ import annotations

import os
from pathlib import Path
import time


def atomic_write_text(path: Path, text: str, encoding: str = "utf-8") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f".{path.name}.tmp")
    temp_path.write_text(text, encoding=encoding)
    os.replace(temp_path, path)


def atomic_append_text(path: Path, text: str, encoding: str = "utf-8") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    last_error: OSError | None = None
    for attempt in range(5):
        try:
            with path.open("a", encoding=encoding, newline="") as handle:
                handle.write(text)
            return
        except OSError as exc:
            last_error = exc
            time.sleep(0.05 * (attempt + 1))
    if last_error is not None:
        raise last_error
