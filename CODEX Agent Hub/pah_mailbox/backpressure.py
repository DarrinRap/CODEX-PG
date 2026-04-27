"""Mailbox backpressure detection for PAH threads."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


BACKPRESSURE_WINDOW_SECONDS = 300
MAX_MESSAGES_PER_THREAD_WINDOW = 25
MAX_MESSAGES_PER_THREAD_TOTAL = 50


@dataclass(frozen=True)
class MailboxMessageRef:
    thread_id: str
    path: Path
    modified: float


@dataclass(frozen=True)
class BackpressureFinding:
    thread_id: str
    path: Path
    level: str
    message: str
    reason_code: str = "flood_threshold_exceeded"


def detect_backpressure(
    records: Iterable[MailboxMessageRef],
    *,
    now: float | None = None,
    window_seconds: int = BACKPRESSURE_WINDOW_SECONDS,
    max_per_window: int = MAX_MESSAGES_PER_THREAD_WINDOW,
    max_total_per_thread: int = MAX_MESSAGES_PER_THREAD_TOTAL,
) -> list[BackpressureFinding]:
    """Return one finding per thread that exceeds PAH flood thresholds."""

    current_time = time.time() if now is None else now
    by_thread: dict[str, list[MailboxMessageRef]] = {}
    for record in records:
        thread_id = record.thread_id.strip() or record.path.name
        by_thread.setdefault(thread_id, []).append(record)

    findings: list[BackpressureFinding] = []
    for thread_id, thread_records in by_thread.items():
        latest = max(thread_records, key=lambda item: item.modified)
        recent_count = sum(1 for item in thread_records if current_time - item.modified <= window_seconds)
        total_count = len(thread_records)
        if recent_count > max_per_window:
            findings.append(
                BackpressureFinding(
                    thread_id=thread_id,
                    path=latest.path,
                    level="warning",
                    message=(
                        f"Backpressure: thread has {recent_count} messages in "
                        f"{window_seconds // 60} minutes"
                    ),
                )
            )
            continue
        if total_count > max_total_per_thread:
            findings.append(
                BackpressureFinding(
                    thread_id=thread_id,
                    path=latest.path,
                    level="info",
                    message=f"Backpressure: thread has {total_count} visible messages",
                )
            )
    return findings
