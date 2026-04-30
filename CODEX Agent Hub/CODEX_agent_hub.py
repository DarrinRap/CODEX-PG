"""CODEX Agent Hub: local mailbox cockpit for Codex, Claude, and Claude Code.

Zero-dependency local web app. It watches the shared mailbox folders, renders a
small dashboard, validates message hygiene, and writes timestamped Markdown
messages into the selected agent inbox.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import secrets
import shutil
import socket
import smtplib
import threading
import time
import webbrowser
from dataclasses import dataclass, field
from datetime import datetime
from http.cookies import SimpleCookie
from email.message import EmailMessage
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import Request, urlopen

from pah_adapters.registry import adapter_status
from pah_core import MESSAGE_SCHEMA_VERSION
from pah_core.decisions import (
    ACTIVE_STATE,
    decision_is_active,
    decision_record_for,
    decision_state_summary,
    load_decision_state,
    set_decision_state,
)
from pah_core.participants import participant_label, route_participants
from pah_core.read_state import (
    READ_STATE,
    UNREAD_STATE,
    load_read_state,
    message_read_status,
    read_state_summary,
    set_message_read_state,
)
from pah_core.schema import (
    content_hash,
    extract_message_metadata,
    metadata_waits_on_darrin,
    render_message_markdown,
    validate_message_text,
)
from pah_core.thread_archive import (
    archive_thread,
    load_thread_archive_state,
    thread_archive_status,
    thread_archive_summary,
    unarchive_thread,
)
from pah_core.validation_state import (
    ACTIVE_STATE as ACTIVE_VALIDATION_STATE,
    load_validation_state,
    set_validation_state,
    validation_is_active,
    validation_record_for,
    validation_state_summary,
    validation_key,
)
from pah_core.work_items import create_work_item, update_work_item, work_board_status
from pah_diagnostics.checks import run_communication_diagnostics
from pah_diagnostics.route_tests import create_route_test, route_test_status
from pah_mailbox.atomic import atomic_append_text, atomic_write_text
from pah_mailbox.backpressure import MailboxMessageRef, detect_backpressure
from pah_mailbox.idempotency import processed_message_event_status, record_processed_message_event
from pah_mailbox.paths import (
    CC_CLAUDE_INBOX,
    CLAUDE_CODE_INBOX,
    CLAUDE_CODE_INBOX_LEGACY,
    CLAUDE_INBOX,
    CLAUDE_SENT,
    CC_MAILBOX_ROOT,
    CODEX_ARCHIVE,
    CODEX_INBOX,
    CODEX_SENT,
    CONFIG_DIR,
    DECISION_QUEUE_PATH,
    HUB_ROOT,
    LEDGER_PATH,
    MAILBOX_ROOT,
    MESSAGE_DIRS,
    NOTIFICATIONS_DIR,
    PANDA_GALLERY_ROOT,
    PROCESSED_MESSAGES_DIR,
    PROJECT_ROOT,
    READ_STATE_PATH,
    REPORTS_DIR,
    THREAD_ARCHIVE_STATE_PATH,
    ensure_runtime_dirs,
)
from pah_mailbox.quarantine import QUARANTINE_REASON_CODES, quarantine_message, validate_quarantine_candidate
from pah_notifications.desktop import desktop_popup_status
from pah_security.approvals import approval_status

NOTIFICATION_CONFIG_TEMPLATE_PATH = CONFIG_DIR / "CODEX_notification_config.template.json"
NOTIFICATION_CONFIG_LOCAL_PATH = CONFIG_DIR / "CODEX_notification_config.local.json"
NOTIFICATION_STATE_PATH = NOTIFICATIONS_DIR / "CODEX_notification_state.local.json"
NOTIFICATION_LOG_PATH = NOTIFICATIONS_DIR / "CODEX_notification_log.jsonl"
WATCHER_STATE_PATH = HUB_ROOT / "CODEX state" / "CODEX_watcher_state.local.json"
WATCHER_EVENT_LOG_PATH = HUB_ROOT / "CODEX logs" / "CODEX_watcher_events.jsonl"
SWEEP_AUDIT_LOG_PATH = HUB_ROOT / "CODEX logs" / "CODEX_pah_sweep_audit.md"
INTERACTION_LEDGER_PATH = HUB_ROOT / "CODEX logs" / "CODEX_pah_interaction_ledger.jsonl"
MESSAGE_AUDIT_STATE_PATH = HUB_ROOT / "CODEX state" / "CODEX_message_audit_state.local.json"
PERIODIC_HEALTH_LATEST_PATH = HUB_ROOT / "CODEX logs" / "CODEX_pah_periodic_health_latest.json"
INSPECTOR_LATEST_JSON_PATH = HUB_ROOT / "CODEX logs" / "CODEX_pah_inspector_latest.json"
INSPECTOR_LATEST_MARKDOWN_PATH = HUB_ROOT / "CODEX logs" / "CODEX_pah_inspector_latest.md"
CC_ACTIVE_DISPATCH_PATH = CC_MAILBOX_ROOT / "_state" / "active_dispatch.json"
UI_PATH = HUB_ROOT / "CODEX_agent_hub_ui.html"
WRITE_TOKEN = secrets.token_urlsafe(32)
ALLOW_SIMULATED_INBOUND = False
LEGACY_MESSAGE_ENDPOINTS: set[str] = set()
MESSAGE_RETENTION_HOURS = 36
TIMESTAMPED_MESSAGE_RE = re.compile(r"^20\d{6}.*\.md$", re.IGNORECASE)
NOTIFICATION_LOCK = threading.Lock()
MAILROOM_CANARY_LOCK = threading.Lock()
WATCHER_LOCK = threading.Lock()
MESSAGE_AUDIT_LOCK = threading.Lock()
WATCHER_SNOOZE_DEFAULT_MINUTES = 15
STALE_UNREAD_SECONDS = 60
MAILBOX_SLA_NORMAL_SECONDS = 15 * 60
MAILBOX_SLA_URGENT_SECONDS = 2 * 60
COMPOSE_STATE_MAX_SECONDS = 20 * 60
DEFAULT_PROGRESS_WARN_MINUTES = 30
DEFAULT_PROGRESS_ERROR_MINUTES = 45
EXPENSIVE_STATUS_CACHE_SECONDS = 5.0
GIT_STATUS_CACHE_SECONDS = 5.0
EXPENSIVE_STATUS_CACHE_LOCK = threading.Lock()
EXPENSIVE_STATUS_CACHE: dict[str, tuple[float, dict[str, Any]]] = {}
MESSAGE_PARSE_CACHE_LOCK = threading.Lock()
MESSAGE_PARSE_CACHE: dict[str, tuple[tuple[int, int], Message]] = {}
PROGRESS_MONITOR_STATUSES = {
    "active",
    "compose",
    "heavy_write",
    "paused",
    "blocked",
    "ready_for_human_loop",
    "complete",
    "abandoned",
}
PROGRESS_MONITOR_IGNORE_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
    "cache",
    "logs",
}

IMPORTANT_STATUSES = {"Decision Needed", "Response Requested", "Implementation Report"}
IMPORTANT_TYPES = {"dispatch", "complete", "decision", "blocker", "response-request", "implementation"}
DISPATCH_MESSAGE_TYPES = {"dispatch", "task", "build_go", "build-go"}
PRE_STAGED_PENDING_STATUS_PREFIXES = ("drafted_pending_",)
REPLIED_TOMBSTONE_SUFFIX = ".replied_tombstone.json"
URGENT_CODEX_REQUEST_TYPES = {"urgent_request", "urgent-request", "blocker", "emergency_request"}
URGENT_CODEX_REQUEST_STATUSES = {"urgent", "urgent_request", "blocked"}
URGENT_CODEX_SENDERS = {"claude-desktop", "claude-code"}
COMPLETION_EVIDENCE_TYPES = {
    "implementation_report",
    "implementation-report",
    "impl_report",
    "impl-report",
    "coordination_response",
    "coordination-response",
    "completion",
    "complete",
    "completed",
    "report",
    "response",
    "ack",
    "acknowledgment",
}
COMPLETION_EVIDENCE_STATUSES = {
    "acknowledged",
    "closed",
    "complete",
    "completed",
    "delivered",
    "response_delivered",
    "review_complete",
    "shipped",
}
SOURCE_ROUTE_CONTRACTS: dict[str, tuple[set[str], set[str]]] = {
    "Claude -> Codex": ({"claude-desktop", "claude-code"}, {"codex"}),
    "Codex -> Claude": ({"codex"}, {"claude-desktop"}),
    "To Claude Code": ({"codex", "claude-desktop"}, {"claude-code"}),
    "Claude Code -> Claude": ({"claude-code"}, {"claude-desktop"}),
    "Claude Code Sent": ({"claude-code"}, {"claude-desktop"}),
    "Claude Sent (CC mailbox)": ({"claude-desktop"}, {"claude-code"}),
    "Codex -> Claude Code (PAH local legacy)": ({"codex"}, {"claude-code"}),
    "Codex -> Claude Code (legacy)": ({"codex"}, {"claude-code"}),
    "Codex Sent": ({"codex"}, {"claude-desktop", "claude-code"}),
    "Claude Sent": ({"claude-desktop", "claude-code"}, {"codex"}),
}
AGENT_ID_ALIASES = {
    "claude": "claude-desktop",
    "claude-desktop": "claude-desktop",
    "claude-code": "claude-code",
    "codex": "codex",
    "darrin": "darrin",
}
ROUTE_DIRECTION_BY_AGENTS = {
    ("claude-desktop", "codex"): "Claude -> Codex",
    ("claude-code", "codex"): "Claude -> Codex",
    ("codex", "claude-desktop"): "Codex -> Claude",
    ("codex", "claude-code"): "To Claude Code",
    ("claude-code", "claude-desktop"): "Claude Code -> Claude",
    ("claude-desktop", "claude-code"): "To Claude Code",
}


def normalize_agent_id(value: Any) -> str:
    token = re.sub(r"[\s_]+", "-", str(value or "").strip().lower())
    if not token:
        return ""
    return AGENT_ID_ALIASES.get(token, token)


def direction_accepts_agents(direction: str, from_agent: str, to_agent: str) -> bool:
    contract = SOURCE_ROUTE_CONTRACTS.get(direction)
    if not contract:
        return True
    allowed_from, allowed_to = contract
    return (not from_agent or from_agent in allowed_from) and (not to_agent or to_agent in allowed_to)


def normalize_message_direction(direction: str, from_agent: str, to_agent: str) -> str:
    if direction_accepts_agents(direction, from_agent, to_agent):
        return direction
    return ROUTE_DIRECTION_BY_AGENTS.get((from_agent, to_agent), direction)

AGENT_INBOX_DIRS: dict[str, tuple[Path, ...]] = {
    "codex": (CODEX_INBOX,),
    "claude-desktop": (CLAUDE_INBOX, CC_CLAUDE_INBOX),
    "claude-code": (CLAUDE_CODE_INBOX, CLAUDE_CODE_INBOX_LEGACY),
}
ALL_AGENT_INBOX_DIRS = tuple(dict.fromkeys(path for paths in AGENT_INBOX_DIRS.values() for path in paths))
CLEANUP_MAILBOX_TARGETS: dict[str, tuple[Path, ...]] = {
    "all": ALL_AGENT_INBOX_DIRS,
    "codex": (CODEX_INBOX,),
    "claude-desktop": (CLAUDE_INBOX, CC_CLAUDE_INBOX),
    "claude-code": (CLAUDE_CODE_INBOX, CLAUDE_CODE_INBOX_LEGACY),
}
CLEANUP_ARCHIVE_ROOTS: dict[Path, Path] = {
    CODEX_INBOX: CODEX_ARCHIVE / "Inbox Cleanup",
    CLAUDE_INBOX: MAILBOX_ROOT / "CLAUDE Archive" / "Inbox Cleanup",
    CLAUDE_CODE_INBOX: (CC_MAILBOX_ROOT / "CC Archive" / "Inbox Cleanup")
    if CLAUDE_CODE_INBOX == CC_MAILBOX_ROOT / "CC Inbox"
    else (MAILBOX_ROOT / "CODEX_CLAUDE_CODE Archive" / "Inbox Cleanup"),
    CLAUDE_CODE_INBOX_LEGACY: MAILBOX_ROOT / "CODEX Claude Code Archive" / "Inbox Cleanup",
    CC_CLAUDE_INBOX: CC_MAILBOX_ROOT / "CLAUDE Archive" / "Inbox Cleanup",
}

TOKEN_RE = re.compile(r"^[A-Za-z][A-Za-z0-9 -]{1,40}:\s*(.*)$")
PATH_RE = re.compile(r"[A-Za-z]:\\[^\n`*]+")
DEFAULT_NOTIFICATION_CONFIG = {
    "enabled": False,
    "provider": "log_only",
    "cooldown_minutes": 30,
    "send_existing_on_start": False,
    "message_prefix": "PANDA Agent Hub",
    "notify_on": {
        "darrin_decision_needed": True,
        "claude_response_requested": True,
        "urgent_codex_request": True,
        "validation_warning": False,
    },
    "desktop_popups": {
        "enabled": False,
        "provider": "scaffold",
    },
    "twilio": {
        "account_sid": "",
        "auth_token": "",
        "from_number": "",
        "to_number": "",
    },
    "email_to_sms": {
        "smtp_host": "",
        "smtp_port": 587,
        "use_starttls": True,
        "username": "",
        "password": "",
        "from_email": "",
        "to_email": "",
    },
    "webhook": {
        "url": "",
        "headers": {},
    },
}
LIVE_NOTIFICATION_PROVIDERS = {"twilio", "email_to_sms", "webhook"}
SMS_NOTIFICATION_PROVIDERS = {"twilio", "email_to_sms"}


@dataclass
class Message:
    direction: str
    path: Path
    name: str
    modified: float
    title: str = "Untitled"
    message_id: str = ""
    reply_to: list[str] = field(default_factory=list)
    thread_id: str = ""
    thread_status: str = ""
    status: str = ""
    from_agent: str = ""
    to_agent: str = ""
    generated: str = ""
    priority: str = ""
    action_owner: str = ""
    requires_approval: str = ""
    requires_darrin_decision: str = ""
    approval_boundary: str = ""
    schema_version: str = ""
    message_type: str = ""
    summary: str = ""
    body_preview: str = ""
    body: str = ""

    @property
    def is_request(self) -> bool:
        status = self.status.lower()
        return "request" in status or "decision" in status or "needed" in status

    @property
    def is_waiting_on_darrin(self) -> bool:
        if is_urgent_codex_request_message(self):
            return False
        return metadata_waits_on_darrin(
            {
                "requires_darrin_decision": self.requires_darrin_decision,
                "thread_status": self.thread_status,
                "priority": self.priority,
                "approval_boundary": self.approval_boundary,
            }
        )

    @property
    def stable_thread(self) -> str:
        if self.thread_id:
            return self.thread_id
        if self.reply_to:
            first = self.reply_to[0]
            match = re.search(r"(?:CODEX|CLAUDE|CC)-\d{8}-\d{6}-[A-Za-z0-9_-]+", first)
            if match:
                return match.group(0)
        return self.message_id or self.name


def read_text(path: Path) -> str:
    for encoding in ("utf-8-sig", "utf-8", "cp1252"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(errors="replace")


def section_text(text: str, heading: str) -> str:
    pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*$", re.IGNORECASE | re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return ""
    start = match.end()
    next_match = re.search(r"^##\s+", text[start:], re.MULTILINE)
    end = start + next_match.start() if next_match else len(text)
    return text[start:end].strip()


def parse_reply_to(lines: list[str], start_index: int) -> list[str]:
    replies: list[str] = []
    for line in lines[start_index + 1 : start_index + 12]:
        stripped = line.strip()
        if not stripped:
            continue
        if TOKEN_RE.match(stripped):
            break
        if stripped.startswith("-"):
            replies.append(stripped[1:].strip())
    return replies


def parse_message(path: Path, direction: str) -> Message:
    text = read_text(path)
    lines = text.splitlines()
    title = next((line[2:].strip() for line in lines if line.startswith("# ")), path.stem)
    msg = Message(direction=direction, path=path, name=path.name, modified=path.stat().st_mtime, title=title, body=text)

    metadata = extract_message_metadata(text)
    reply_to = metadata.get("reply_to", [])
    if isinstance(reply_to, list):
        msg.reply_to = [str(item) for item in reply_to if str(item).strip()]
    elif reply_to:
        msg.reply_to = [str(reply_to)]
    msg.message_id = str(metadata.get("message_id", ""))
    msg.thread_id = str(metadata.get("thread_id", ""))
    msg.thread_status = str(metadata.get("thread_status", ""))
    msg.status = metadata.get("status", "")
    msg.from_agent = normalize_agent_id(metadata.get("from", ""))
    msg.to_agent = normalize_agent_id(metadata.get("to", ""))
    msg.direction = normalize_message_direction(msg.direction, msg.from_agent, msg.to_agent)
    msg.generated = metadata.get("generated", "")
    msg.priority = metadata.get("priority", "")
    msg.action_owner = normalize_agent_id(metadata.get("action-owner", "") or metadata.get("action_owner", ""))
    msg.requires_approval = metadata.get("requires-approval", "") or metadata.get("requires_approval", "")
    msg.requires_darrin_decision = (
        metadata.get("requires-darrin-decision", "") or metadata.get("requires_darrin_decision", "")
    )
    msg.approval_boundary = str(metadata.get("approval_boundary", ""))
    msg.schema_version = str(metadata.get("schema_version", ""))
    msg.message_type = str(metadata.get("type", ""))

    summary = section_text(text, "Summary")
    msg.summary = compact(summary, 260)
    body_plain = re.sub(r"[#>*_`\[\]()-]", " ", text)
    msg.body_preview = compact(" ".join(body_plain.split()), 320)
    return msg


def message_cache_key(path: Path) -> str:
    try:
        return str(path.resolve())
    except OSError:
        return str(path)


def parse_message_cached(path: Path, direction: str) -> Message:
    stat_result = path.stat()
    signature = (int(getattr(stat_result, "st_mtime_ns", int(stat_result.st_mtime * 1_000_000_000))), stat_result.st_size)
    cache_key = message_cache_key(path)
    with MESSAGE_PARSE_CACHE_LOCK:
        cached = MESSAGE_PARSE_CACHE.get(cache_key)
        if cached and cached[0] == signature:
            return cached[1]
    msg = parse_message(path, direction)
    with MESSAGE_PARSE_CACHE_LOCK:
        MESSAGE_PARSE_CACHE[cache_key] = (signature, msg)
    return msg


def prune_message_parse_cache(active_keys: set[str]) -> None:
    with MESSAGE_PARSE_CACHE_LOCK:
        stale_keys = [key for key in MESSAGE_PARSE_CACHE if key not in active_keys]
        for key in stale_keys:
            MESSAGE_PARSE_CACHE.pop(key, None)


def clear_message_parse_cache() -> None:
    with MESSAGE_PARSE_CACHE_LOCK:
        MESSAGE_PARSE_CACHE.clear()


def compact(value: str, limit: int) -> str:
    value = " ".join(value.split())
    return value if len(value) <= limit else value[: limit - 1].rstrip() + "..."


def local_timestamp() -> str:
    now = datetime.now().astimezone()
    offset = now.strftime("%z")
    formatted_offset = f"{offset[:3]}:{offset[3:]}" if offset else ""
    return f"{now:%Y-%m-%d %H:%M:%S} {formatted_offset}".strip()


def load_messages() -> list[Message]:
    messages: list[Message] = []
    active_cache_keys: set[str] = set()
    for direction, folder in MESSAGE_DIRS:
        if not folder.exists():
            continue
        for path in folder.glob("*.md"):
            active_cache_keys.add(message_cache_key(path))
            try:
                messages.append(parse_message_cached(path, direction))
            except OSError:
                continue
    prune_message_parse_cache(active_cache_keys)
    messages.sort(key=lambda item: item.modified, reverse=True)
    return messages


def message_parent_in(msg: Message, folders: tuple[Path, ...]) -> bool:
    try:
        parent = msg.path.parent.resolve()
    except OSError:
        parent = msg.path.parent
    for folder in folders:
        try:
            if parent == folder.resolve():
                return True
        except OSError:
            if str(parent) == str(folder):
                return True
    return False


def message_in_agent_inbox(msg: Message, agent_id: str) -> bool:
    return message_parent_in(msg, AGENT_INBOX_DIRS.get(agent_id, ()))


def message_in_any_agent_inbox(msg: Message) -> bool:
    return message_parent_in(msg, ALL_AGENT_INBOX_DIRS)


def is_dispatch_message(msg: Message) -> bool:
    msg_type = str(msg.message_type or "").strip().lower()
    if msg_type in DISPATCH_MESSAGE_TYPES:
        return True
    text = " ".join([msg.title, msg.summary]).lower()
    return "dispatch" in text


def message_is_flagged_urgent(msg: Message) -> bool:
    priority = str(msg.priority or "").strip().lower()
    status = str(msg.status or "").strip().lower()
    msg_type = str(msg.message_type or "").strip().lower()
    title = str(msg.title or "").strip().lower()
    return (
        priority == "urgent"
        or msg_type in URGENT_CODEX_REQUEST_TYPES
        or status in URGENT_CODEX_REQUEST_STATUSES
        or title.startswith("urgent:")
        or title.startswith("[urgent]")
    )


def is_urgent_codex_request_message(msg: Message) -> bool:
    return (
        msg.to_agent == "codex"
        and msg.from_agent in URGENT_CODEX_SENDERS
        and message_in_agent_inbox(msg, "codex")
        and message_is_flagged_urgent(msg)
        and not boolish(msg.requires_darrin_decision)
        and str(msg.thread_status or "").strip().lower() != "waiting_on_darrin"
        and "_requires_darrin" not in str(msg.approval_boundary or "").strip().lower()
    )


def is_pre_staged_pending_trigger(msg: Message) -> bool:
    status = str(msg.status or "").strip().lower()
    return any(status.startswith(prefix) for prefix in PRE_STAGED_PENDING_STATUS_PREFIXES)


def is_structured_mailbox_message(msg: Message) -> bool:
    has_schema_id = bool(str(msg.schema_version or "").strip() and str(msg.message_id or "").strip())
    has_route_id = bool(str(msg.message_id or "").strip() and msg.from_agent and msg.to_agent)
    return has_schema_id or has_route_id


def reply_tombstone_path(message_path: Path) -> Path:
    return message_path.with_name(message_path.name + REPLIED_TOMBSTONE_SUFFIX)


def load_reply_tombstone_for_path(message_path: Path) -> dict[str, Any] | None:
    path = reply_tombstone_path(message_path)
    if not path.exists():
        return None
    payload = read_json(path, {})
    if not isinstance(payload, dict):
        return None
    if str(payload.get("tombstone_type", "")).strip().lower() != "replied":
        return None
    return payload


def load_reply_tombstone(message: Message) -> dict[str, Any] | None:
    return load_reply_tombstone_for_path(message.path)


def message_has_reply_tombstone(message: Message) -> bool:
    return load_reply_tombstone(message) is not None


def is_completion_evidence_message(msg: Message) -> bool:
    msg_type = str(msg.message_type or "").strip().lower()
    status = str(msg.status or "").strip().lower()
    if is_dispatch_message(msg):
        return False
    return msg_type in COMPLETION_EVIDENCE_TYPES or status in COMPLETION_EVIDENCE_STATUSES


def completed_thread_ids(messages: list[Message]) -> set[str]:
    return {msg.stable_thread for msg in messages if is_completion_evidence_message(msg)}


def is_no_action_coordination_message(msg: Message) -> bool:
    msg_type = str(msg.message_type or "").strip().lower()
    approval_boundary = str(msg.approval_boundary or "").strip().lower()
    body = str(msg.body or "").lower()
    title = str(msg.title or "").lower()
    if msg_type not in {"share", "coordination", "coordination_share", "info", "ack"}:
        return False
    if approval_boundary and approval_boundary != "coordination_only":
        return False
    if boolish(msg.requires_darrin_decision):
        return False
    no_action_tokens = (
        "no action required",
        "no reply required",
        "not a dispatch",
        "coordination / awareness share",
    )
    return any(token in body or token in title for token in no_action_tokens)


def load_ledger_text() -> str:
    return read_text(LEDGER_PATH) if LEDGER_PATH.exists() else ""


def source_route_issue(msg: Message) -> str:
    contract = SOURCE_ROUTE_CONTRACTS.get(msg.direction)
    if not contract:
        return ""
    allowed_from, allowed_to = contract
    if msg.from_agent and msg.from_agent not in allowed_from:
        expected = ", ".join(sorted(allowed_from))
        return f"Spoofing check failed: {msg.direction} message claims from={msg.from_agent}; expected {expected}"
    if msg.to_agent and msg.to_agent not in allowed_to:
        expected = ", ".join(sorted(allowed_to))
        return f"Spoofing check failed: {msg.direction} message claims to={msg.to_agent}; expected {expected}"
    return ""


def message_status_badges(msg: Message, unread: bool = False) -> list[str]:
    badges: list[str] = []
    if unread:
        badges.append("unread")
    if msg.is_waiting_on_darrin:
        badges.append("waiting_on_darrin")
    if msg.is_request:
        badges.append("request")
    priority = msg.priority.lower().strip()
    if priority in {"high", "urgent"}:
        badges.append(priority)
    for value in (msg.thread_status, msg.message_type):
        normalized = value.lower().strip()
        if normalized and normalized not in badges:
            badges.append(normalized)
    return badges[:5]


def build_threads(
    messages: list[Message],
    read_state_data: dict[str, Any] | None = None,
    archive_state_data: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    grouped: dict[str, list[Message]] = {}
    for msg in messages:
        grouped.setdefault(msg.stable_thread, []).append(msg)
    rows: list[dict[str, Any]] = []
    for thread_id, items in grouped.items():
        items.sort(key=lambda item: item.modified)
        latest = items[-1]
        unread_count = sum(
            1 for item in items if message_read_status(item.path, item.message_id, item.body, read_state_data)["unread"]
        )
        archive_status = thread_archive_status(thread_id, latest.modified, archive_state_data)
        badges = message_status_badges(latest, unread_count > 0)
        if archive_status["archived"] and "archived" not in badges:
            badges.append("archived")
        if archive_status["reopened_by_new_activity"] and "new_activity" not in badges:
            badges.append("new_activity")
        status = latest.thread_status or latest.status or ("Open" if latest.is_request else "Info")
        rows.append(
            {
                "thread_id": thread_id,
                "count": len(items),
                "unread": unread_count,
                "latest_title": latest.title,
                "latest_direction": latest.direction,
                "latest_path": str(latest.path),
                "latest_modified": latest.modified,
                "status": status,
                "status_badges": badges[:6],
                "owner": latest.action_owner or latest.to_agent or "",
                "waiting_on_darrin": latest.is_waiting_on_darrin,
                "summary": latest.summary or latest.body_preview,
                "archived": archive_status["archived"],
                "archived_at": archive_status["archived_at"],
                "archive_reason": archive_status["archive_reason"],
                "reopened_by_new_activity": archive_status["reopened_by_new_activity"],
            }
        )
    rows.sort(key=lambda item: item["latest_modified"], reverse=True)
    return rows


def boolish(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"true", "yes", "1", "y"}


def thread_owner_label(owner: str) -> str:
    if owner == "darrin":
        return "Darrin"
    return participant_label(owner) if owner else "Unassigned"


def classify_thread_state(latest: Message, archived: bool = False) -> str:
    owner = safe_slug(latest.action_owner).replace("-", "_")
    status = str(latest.status or "").strip().lower()
    thread_status = str(latest.thread_status or "").strip().lower()
    msg_type = str(latest.message_type or "").strip().lower()
    if message_has_reply_tombstone(latest):
        return "closed"
    if not is_structured_mailbox_message(latest) and message_in_any_agent_inbox(latest):
        return "owner_unknown"
    if archived or thread_status in {"archived", "closed", "resolved"}:
        return "closed"
    if is_pre_staged_pending_trigger(latest):
        return "parked"
    if thread_status in {"parked", "paused"}:
        return "parked"
    if is_urgent_codex_request_message(latest):
        return "open_on_agent"
    if owner == "darrin":
        return "open_on_darrin"
    if boolish(latest.requires_darrin_decision):
        return "open_on_darrin"
    if is_no_action_coordination_message(latest):
        return "closed"
    if msg_type in COMPLETION_EVIDENCE_TYPES or status in COMPLETION_EVIDENCE_STATUSES:
        if thread_status in {"ready_for_review", "waiting_review"}:
            return "open_on_agent"
        return "closed"
    if owner in {"codex", "claude_desktop", "claude_code", "claude-code", "claude-desktop"}:
        return "open_on_agent"
    if thread_status in {"waiting_on_agent", "waiting_review", "ready_for_review"}:
        return "open_on_agent"
    if thread_status == "waiting_on_darrin" and status in {"open", "blocked"} and msg_type == "decision_request":
        return "open_on_darrin"
    if status in {"complete", "shipped", "review_complete", "closed"}:
        return "closed"
    if latest.is_request and latest.to_agent:
        return "open_on_agent"
    return "closed"


def build_thread_focus(messages: list[Message], archive_state_data: dict[str, Any] | None = None) -> dict[str, Any]:
    grouped: dict[str, list[Message]] = {}
    for msg in messages:
        grouped.setdefault(msg.stable_thread, []).append(msg)
    rows: list[dict[str, Any]] = []
    missing_thread_id = 0
    missing_action_owner = 0
    for thread_id, items in grouped.items():
        items.sort(key=lambda item: item.modified)
        latest = items[-1]
        if not latest.thread_id:
            missing_thread_id += 1
        if not latest.action_owner:
            missing_action_owner += 1
        archive_status = thread_archive_status(thread_id, latest.modified, archive_state_data)
        state_name = classify_thread_state(latest, bool(archive_status.get("archived")))
        owner = safe_slug(latest.action_owner).replace("-", "_")
        if state_name == "open_on_agent" and owner == "darrin":
            owner = safe_slug(latest.to_agent or latest.from_agent).replace("-", "_")
        if not owner:
            if state_name == "open_on_darrin":
                owner = "darrin"
            elif state_name == "open_on_agent":
                owner = safe_slug(latest.to_agent).replace("-", "_")
        age_seconds = max(0, int(time.time() - latest.modified))
        rows.append(
            {
                "id": thread_id,
                "thread_id": thread_id,
                "state": state_name,
                "state_label": {
                    "open_on_darrin": "Open on you",
                    "open_on_agent": "Open on agents",
                    "owner_unknown": "Owner unknown",
                    "parked": "Parked",
                    "closed": "Closed",
                }.get(state_name, state_name),
                "owner": owner,
                "owner_label": thread_owner_label(owner),
                "agent": latest.from_agent or latest.to_agent or owner,
                "agent_label": participant_label(latest.from_agent or latest.to_agent or owner),
                "title": latest.title,
                "summary": latest.summary or latest.body_preview,
                "message_id": latest.message_id,
                "message_path": str(latest.path),
                "latest_modified": latest.modified,
                "age_seconds": age_seconds,
                "count": len(items),
                "requires_darrin_decision": boolish(latest.requires_darrin_decision),
                "is_urgent": is_urgent_codex_request_message(latest),
                "latest_from": latest.from_agent,
                "latest_to": latest.to_agent,
                "latest_status": latest.status,
                "latest_thread_status": latest.thread_status,
                "latest_type": latest.message_type,
                "primary_action": "Open message" if state_name == "open_on_darrin" else "Review thread",
                "secondary_action": "Browse thread",
                "wake_line": "",
            }
        )
    rows.sort(key=lambda item: item["latest_modified"], reverse=True)
    buckets = {
        "open_on_darrin": [row for row in rows if row["state"] == "open_on_darrin"],
        "open_on_agent": [row for row in rows if row["state"] == "open_on_agent"],
        "owner_unknown": [row for row in rows if row["state"] == "owner_unknown"],
        "parked": [row for row in rows if row["state"] == "parked"],
        "closed": [row for row in rows if row["state"] == "closed"],
    }
    return {
        "counts": {key: len(value) for key, value in buckets.items()} | {"all": len(rows)},
        "open_on_darrin": buckets["open_on_darrin"],
        "open_on_agent": buckets["open_on_agent"],
        "owner_unknown": buckets["owner_unknown"],
        "parked": buckets["parked"],
        "closed": buckets["closed"],
        "all": rows,
        "diagnostics": {
            "threads": len(rows),
            "messages": len(messages),
            "missing_thread_id": missing_thread_id,
            "missing_action_owner": missing_action_owner,
            "model": "latest-message thread classifier",
        },
    }


def validate_mailbox(messages: list[Message]) -> list[dict[str, Any]]:
    ledger = load_ledger_text()
    issues: list[dict[str, Any]] = []
    seen_issue_keys: set[tuple[str, str, str]] = set()
    seen_ids: dict[str, tuple[Path, str]] = {}

    def add(level: str, msg: Message, text: str) -> None:
        item = issue(level, msg, text)
        key = (item["path"], item["category"], item["message"])
        if key in seen_issue_keys:
            return
        seen_issue_keys.add(key)
        issues.append(item)

    for msg in messages:
        if not msg.message_id:
            add("warning", msg, "Missing id / Message-ID")
        elif msg.message_id in seen_ids:
            first_path, first_hash = seen_ids[msg.message_id]
            this_hash = content_hash(msg.body)
            if first_hash != this_hash:
                add(
                    "error",
                    msg,
                    f"Provenance conflict: Message-ID also appears with different content in {first_path.name}",
                )
            else:
                add("warning", msg, f"Duplicate Message-ID also in {first_path.name}")
        else:
            seen_ids[msg.message_id] = (msg.path, content_hash(msg.body))

        for schema_issue in validate_message_text(msg.body, msg.name):
            if schema_issue.message == "Missing id / message_id / Message-ID" and not msg.message_id:
                continue
            add(schema_issue.level, msg, schema_issue.message)

        route_issue = source_route_issue(msg)
        if route_issue:
            add("error", msg, route_issue)

        if msg.status.lower() in {"response requested", "implementation report"} and not msg.reply_to:
            add("info", msg, "No Reply-To list on request/report")

        if msg.status in IMPORTANT_STATUSES and msg.name not in ledger:
            add("warning", msg, "Important message not found in mailbox ledger")

        for candidate in PATH_RE.findall(msg.body):
            cleaned = candidate.strip().rstrip(".;,)")
            if "C:\\CODEX PG" in cleaned and len(cleaned) < 240:
                path = Path(cleaned)
                if any(label in cleaned.lower() for label in ("deliverable", "path", "file", "mockup")) and not path.exists():
                    add("info", msg, f"Referenced path not found: {cleaned}")

    by_path = {str(msg.path): msg for msg in messages}
    backpressure_records = [
        MailboxMessageRef(thread_id=msg.stable_thread, path=msg.path, modified=msg.modified)
        for msg in messages
    ]
    for finding in detect_backpressure(backpressure_records):
        target = by_path.get(str(finding.path))
        if target is not None:
            add(finding.level, target, finding.message)
    return issues[:100]


def validation_category(text: str) -> str:
    lowered = text.lower()
    if "spoofing" in lowered:
        return "spoofing"
    if "provenance conflict" in lowered or "duplicate message-id" in lowered:
        return "provenance"
    if "message-id" in lowered or "message_id" in lowered:
        return "identity"
    if "schema" in lowered or "unsupported" in lowered:
        return "schema"
    if "ledger" in lowered:
        return "ledger"
    if "backpressure" in lowered or "flood" in lowered:
        return "backpressure"
    if "reply-to" in lowered:
        return "threading"
    if "referenced path" in lowered or "path not found" in lowered:
        return "path_reference"
    return "general"


def validation_is_actionable(level: str, category: str) -> bool:
    if level == "error":
        return True
    return category in {"provenance", "ledger", "backpressure", "spoofing"}


def issue(level: str, msg: Message, text: str) -> dict[str, Any]:
    category = validation_category(text)
    fingerprint = validation_key(str(msg.path), category, text)
    return {
        "level": level,
        "category": category,
        "actionable": validation_is_actionable(level, category),
        "fingerprint": fingerprint,
        "message": text,
        "file": msg.name,
        "path": str(msg.path),
        "title": msg.title,
        "quarantine_allowed": quarantine_candidate_allowed(msg.path),
        "quarantine_reason": default_quarantine_reason(category, text),
    }


def summarize_validation(issues: list[dict[str, Any]]) -> dict[str, Any]:
    by_level: dict[str, int] = {}
    by_category: dict[str, int] = {}
    actionable = 0
    for item in issues:
        by_level[item["level"]] = by_level.get(item["level"], 0) + 1
        by_category[item["category"]] = by_category.get(item["category"], 0) + 1
        if item.get("actionable"):
            actionable += 1
    return {
        "total": len(issues),
        "actionable": actionable,
        "informational_or_legacy": len(issues) - actionable,
        "by_level": by_level,
        "by_category": by_category,
    }


def apply_validation_state(issues: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    state_data = load_validation_state()
    active: list[dict[str, Any]] = []
    inactive: list[dict[str, Any]] = []
    for item in issues:
        record = validation_record_for(str(item.get("fingerprint", "")), state_data)
        state_name = str(record.get("state", ACTIVE_VALIDATION_STATE))
        enriched = {
            **item,
            "validation_state": state_name,
            "state_note": str(record.get("note", "")),
            "state_actor": str(record.get("actor", "")),
            "state_updated_at": str(record.get("updated_at", "")),
        }
        if item.get("actionable") and validation_is_active(str(item.get("fingerprint", "")), state_data):
            active.append(enriched)
        elif item.get("actionable"):
            inactive.append(enriched)
    return active, inactive


def deep_merge(default: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(default)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def read_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return dict(default)
    try:
        value = json.loads(read_text(path))
    except (json.JSONDecodeError, OSError):
        return dict(default)
    return value if isinstance(value, dict) else dict(default)


def write_json(path: Path, value: dict[str, Any]) -> None:
    atomic_write_text(path, json.dumps(value, indent=2) + "\n")


def load_message_audit_state() -> dict[str, Any]:
    return read_json(MESSAGE_AUDIT_STATE_PATH, {"messages": {}, "threads": {}})


def write_message_audit_state(state_data: dict[str, Any]) -> None:
    write_json(MESSAGE_AUDIT_STATE_PATH, state_data)


def ledger_json_safe(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): ledger_json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [ledger_json_safe(item) for item in value]
    return value


def message_ledger_fields(message: Message) -> dict[str, Any]:
    return {
        "message_id": message.message_id,
        "thread_id": message.stable_thread,
        "title": message.title,
        "from": message.from_agent,
        "to": message.to_agent,
        "type": message.message_type,
        "status": message.status,
        "thread_status": message.thread_status,
        "action_owner": message.action_owner,
        "path": str(message.path),
        "content_hash": content_hash(message.body) if message.body else "",
    }


def append_interaction_ledger_event(
    event_type: str,
    actor: str = "pah",
    message: Message | None = None,
    **details: Any,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema_version": 1,
        "time": datetime.now().astimezone().isoformat(timespec="seconds"),
        "event_type": event_type,
        "actor": actor.strip() or "pah",
    }
    if message is not None:
        payload.update({key: value for key, value in message_ledger_fields(message).items() if value not in ("", None)})
    payload.update({key: ledger_json_safe(value) for key, value in details.items() if value is not None})
    INTERACTION_LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    atomic_append_text(INTERACTION_LEDGER_PATH, json.dumps(payload, sort_keys=True) + "\n")
    return payload


def message_discovery_key(message: Message) -> str:
    clean_id = str(message.message_id or "").strip()
    if clean_id:
        return f"id:{clean_id}"
    return f"path:{message_cache_key(message.path)}"


def normalize_reply_ref(value: str) -> str:
    return str(value or "").strip().strip("`").strip()


def find_messages_by_reply_ref(reply_ref: str, messages: list[Message]) -> list[Message]:
    ref = normalize_reply_ref(reply_ref)
    if not ref:
        return []
    by_message_id = [msg for msg in messages if msg.message_id == ref]
    if by_message_id:
        return by_message_id
    by_path = [
        msg
        for msg in messages
        if msg.name == ref or str(msg.path) == ref or str(msg.path.resolve()) == ref
    ]
    if by_path:
        return by_path
    by_thread = [msg for msg in messages if msg.stable_thread == ref]
    return by_thread if len(by_thread) == 1 else []


def write_reply_tombstones(
    reply_refs: list[str],
    *,
    reply_message_id: str,
    reply_thread_id: str,
    reply_path: Path,
    reply_from: str,
    reply_to: str,
    route: str,
    replied_at: str,
    actor: str,
) -> list[dict[str, Any]]:
    messages = load_messages()
    records: list[dict[str, Any]] = []
    seen_originals: set[str] = set()
    for raw_ref in reply_refs:
        reply_ref = normalize_reply_ref(raw_ref)
        if not reply_ref:
            continue
        matches = find_messages_by_reply_ref(reply_ref, messages)
        if not matches:
            record = {"reply_ref": reply_ref, "status": "missing"}
            records.append(record)
            append_interaction_ledger_event(
                "message_reply_tombstone_missing",
                actor=actor,
                reply_ref=reply_ref,
                reply_message_id=reply_message_id,
                reply_thread_id=reply_thread_id,
                reply_path=reply_path,
                route=route,
            )
            continue
        for original in matches:
            if original.path == reply_path:
                continue
            original_key = message_cache_key(original.path)
            if original_key in seen_originals:
                continue
            seen_originals.add(original_key)
            tombstone_path = reply_tombstone_path(original.path)
            tombstone = {
                "schema_version": 1,
                "tombstone_type": "replied",
                "reason": "reply_sent",
                "original_message_id": original.message_id,
                "original_thread_id": original.stable_thread,
                "original_path": str(original.path),
                "reply_ref": reply_ref,
                "reply_message_id": reply_message_id,
                "reply_thread_id": reply_thread_id,
                "reply_path": str(reply_path),
                "reply_from": reply_from,
                "reply_to": reply_to,
                "route": route,
                "actor": actor,
                "replied_at": replied_at,
            }
            atomic_write_text(tombstone_path, json.dumps(tombstone, indent=2, sort_keys=True) + "\n")
            record = {
                "reply_ref": reply_ref,
                "status": "written",
                "original_message_id": original.message_id,
                "original_thread_id": original.stable_thread,
                "original_path": str(original.path),
                "tombstone_path": str(tombstone_path),
            }
            records.append(record)
            append_interaction_ledger_event(
                "message_reply_tombstoned",
                actor=actor,
                message=original,
                reply_ref=reply_ref,
                reply_message_id=reply_message_id,
                reply_thread_id=reply_thread_id,
                reply_path=reply_path,
                tombstone_path=tombstone_path,
                route=route,
            )
    return records


def audit_messages_and_thread_states(
    messages: list[Message],
    thread_focus: dict[str, Any],
    read_state_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    with MESSAGE_AUDIT_LOCK:
        state_data = load_message_audit_state()
        seen_messages = state_data.setdefault("messages", {})
        seen_threads = state_data.setdefault("threads", {})
        if not isinstance(seen_messages, dict):
            seen_messages = {}
            state_data["messages"] = seen_messages
        if not isinstance(seen_threads, dict):
            seen_threads = {}
            state_data["threads"] = seen_threads

        discovered = 0
        transitions = 0
        for msg in messages:
            key = message_discovery_key(msg)
            current = {
                "message_id": msg.message_id,
                "thread_id": msg.stable_thread,
                "path": str(msg.path),
                "content_hash": content_hash(msg.body) if msg.body else "",
                "modified": msg.modified,
            }
            if key not in seen_messages:
                append_interaction_ledger_event(
                    "message_discovered",
                    actor="pah_observer",
                    message=msg,
                    direction=msg.direction,
                    read_state=message_read_status(msg.path, msg.message_id, msg.body, read_state_data)["state"],
                )
                discovered += 1
            seen_messages[key] = {**current, "last_seen_at": datetime.now().astimezone().isoformat(timespec="seconds")}

        for row in thread_focus.get("all", []):
            if not isinstance(row, dict):
                continue
            thread_id = str(row.get("thread_id") or row.get("id") or "")
            if not thread_id:
                continue
            current = {
                "state": str(row.get("state", "")),
                "owner": str(row.get("owner", "")),
                "message_id": str(row.get("message_id", "")),
                "message_path": str(row.get("message_path", "")),
                "latest_modified": row.get("latest_modified", 0),
            }
            previous = seen_threads.get(thread_id)
            if isinstance(previous, dict) and (
                previous.get("state") != current["state"] or previous.get("owner") != current["owner"]
            ):
                append_interaction_ledger_event(
                    "classifier_state_changed",
                    actor="pah_classifier",
                    thread_id=thread_id,
                    previous_state=previous.get("state", ""),
                    state=current["state"],
                    previous_owner=previous.get("owner", ""),
                    owner=current["owner"],
                    message_id=current["message_id"],
                    path=current["message_path"],
                )
                transitions += 1
            seen_threads[thread_id] = {
                **current,
                "last_seen_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            }

        write_message_audit_state(state_data)
        return {
            "path": str(MESSAGE_AUDIT_STATE_PATH),
            "messages_tracked": len(seen_messages),
            "threads_tracked": len(seen_threads),
            "discovered": discovered,
            "transitions": transitions,
        }


def ensure_notification_template() -> None:
    ensure_runtime_dirs()
    if not NOTIFICATION_CONFIG_TEMPLATE_PATH.exists():
        write_json(NOTIFICATION_CONFIG_TEMPLATE_PATH, DEFAULT_NOTIFICATION_CONFIG)


def ensure_notification_local_config() -> None:
    ensure_notification_template()
    if not NOTIFICATION_CONFIG_LOCAL_PATH.exists():
        write_json(NOTIFICATION_CONFIG_LOCAL_PATH, DEFAULT_NOTIFICATION_CONFIG)


def load_notification_config() -> dict[str, Any]:
    ensure_notification_local_config()
    local = read_json(NOTIFICATION_CONFIG_LOCAL_PATH, {})
    return deep_merge(DEFAULT_NOTIFICATION_CONFIG, local)


def notification_status() -> dict[str, Any]:
    config = load_notification_config()
    state_data = read_json(NOTIFICATION_STATE_PATH, {})
    provider = str(config.get("provider", "log_only"))
    configured = provider_is_configured(config, provider)
    enabled = bool(config.get("enabled"))
    live_delivery_ready = enabled and configured and provider in LIVE_NOTIFICATION_PROVIDERS
    if provider == "log_only":
        setup_hint = "Log-only mode is for local testing. Choose twilio or email_to_sms in the local config to send a real SMS."
    elif provider in LIVE_NOTIFICATION_PROVIDERS and not configured:
        setup_hint = f"Provider {provider} is selected but missing required local config values."
    elif provider in LIVE_NOTIFICATION_PROVIDERS and not enabled:
        setup_hint = f"Provider {provider} is configured but notifications are disabled."
    else:
        setup_hint = "Live notification delivery is ready."
    return {
        "enabled": enabled,
        "provider": provider,
        "configured": configured,
        "live_delivery_ready": live_delivery_ready,
        "real_sms_ready": live_delivery_ready and provider in SMS_NOTIFICATION_PROVIDERS,
        "delivery_mode": "live" if live_delivery_ready else "log_only",
        "setup_required": not live_delivery_ready,
        "setup_hint": setup_hint,
        "local_config_exists": NOTIFICATION_CONFIG_LOCAL_PATH.exists(),
        "config_path": str(NOTIFICATION_CONFIG_LOCAL_PATH),
        "template_path": str(NOTIFICATION_CONFIG_TEMPLATE_PATH),
        "log_path": str(NOTIFICATION_LOG_PATH),
        "last_sent_at": state_data.get("last_sent_at", ""),
        "last_error": state_data.get("last_error", ""),
        "baseline_initialized": bool(state_data.get("baseline_initialized")),
        "processed_sidecars": str(PROCESSED_MESSAGES_DIR),
        "desktop_popups": desktop_popup_status(config),
    }


def quarantine_candidate_allowed(path: Path | str) -> bool:
    try:
        validate_quarantine_candidate(Path(path))
    except (FileNotFoundError, OSError, ValueError):
        return False
    return True


def default_quarantine_reason(category: str = "", message: str = "") -> str:
    lowered = f"{category} {message}".lower()
    if "spoof" in lowered:
        return "spoofing_attempt"
    if "backpressure" in lowered or "flood" in lowered:
        return "flood_threshold_exceeded"
    if "provenance" in lowered or "duplicate" in lowered:
        return "duplicate_id_hash_mismatch"
    if "unknown participant" in lowered:
        return "unknown_participant"
    if "frontmatter" in lowered:
        return "malformed_yaml_frontmatter"
    if "missing" in lowered:
        return "missing_required_field"
    if "unsafe" in lowered:
        return "unsafe_boundary"
    return "schema_invalid"


def recent_quarantine_records(limit: int = 8) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for tombstone in MAILBOX_ROOT.glob("**/*.pah_tombstone.json"):
        try:
            payload = json.loads(read_text(tombstone))
        except (json.JSONDecodeError, OSError):
            continue
        original_path = str(payload.get("original_path", ""))
        records.append(
            {
                "original_path": original_path,
                "original_name": Path(original_path).name if original_path else tombstone.name,
                "quarantine_path": str(payload.get("quarantine_path", "")),
                "reason": str(payload.get("reason", "")),
                "moved_at": str(payload.get("moved_at", "")),
                "tombstone_path": str(payload.get("tombstone_path", tombstone)),
                "tombstone_modified": tombstone.stat().st_mtime,
            }
        )
    records.sort(key=lambda item: (item.get("moved_at") or "", item.get("tombstone_modified") or 0), reverse=True)
    return records[:limit]


def quarantine_status() -> dict[str, Any]:
    from pah_mailbox.paths import QUARANTINE_DIR

    quarantined = list(QUARANTINE_DIR.glob("*.md")) if QUARANTINE_DIR.exists() else []
    tombstones = list(MAILBOX_ROOT.glob("**/*.pah_tombstone.json"))
    return {
        "quarantine_dir": str(QUARANTINE_DIR),
        "messages": len(quarantined),
        "tombstones": len(tombstones),
        "automatic_moves": False,
        "reason_codes": sorted(QUARANTINE_REASON_CODES),
        "recent": recent_quarantine_records(),
        "detail": "Quarantine is explicit only: API requires token and confirmed=true.",
    }


def provider_is_configured(config: dict[str, Any], provider: str) -> bool:
    if provider == "twilio":
        twilio = config.get("twilio", {})
        return all(twilio.get(key) for key in ("account_sid", "auth_token", "from_number", "to_number"))
    if provider == "email_to_sms":
        email_config = config.get("email_to_sms", {})
        return all(email_config.get(key) for key in ("smtp_host", "from_email", "to_email"))
    if provider == "webhook":
        return bool(config.get("webhook", {}).get("url"))
    return False


def append_notification_log(event: dict[str, Any]) -> None:
    NOTIFICATIONS_DIR.mkdir(parents=True, exist_ok=True)
    atomic_append_text(NOTIFICATION_LOG_PATH, json.dumps(event, sort_keys=True) + "\n")


def send_notification(config: dict[str, Any], subject: str, body: str) -> dict[str, Any]:
    provider = str(config.get("provider", "log_only"))
    prefix = str(config.get("message_prefix", "PANDA Agent Hub")).strip()
    text = compact(f"{prefix}: {subject} - {body}", 1500)
    if provider == "log_only":
        return {"ok": True, "provider": provider, "detail": "Logged only", "text": text}
    if not provider_is_configured(config, provider):
        raise RuntimeError(f"Notification provider is not configured: {provider}")
    if provider == "twilio":
        return send_twilio_sms(config, text)
    if provider == "email_to_sms":
        return send_email_to_sms(config, subject, text)
    if provider == "webhook":
        return send_webhook_notification(config, subject, text)
    raise RuntimeError(f"Unsupported notification provider: {provider}")


def send_twilio_sms(config: dict[str, Any], text: str) -> dict[str, Any]:
    twilio = config["twilio"]
    account_sid = twilio["account_sid"]
    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
    payload = urlencode({"From": twilio["from_number"], "To": twilio["to_number"], "Body": text}).encode("utf-8")
    token = base64.b64encode(f"{account_sid}:{twilio['auth_token']}".encode("utf-8")).decode("ascii")
    request = Request(url, data=payload, method="POST", headers={"Authorization": f"Basic {token}"})
    with urlopen(request, timeout=20) as response:
        return {"ok": True, "provider": "twilio", "status": response.status}


def send_email_to_sms(config: dict[str, Any], subject: str, text: str) -> dict[str, Any]:
    email_config = config["email_to_sms"]
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = email_config["from_email"]
    msg["To"] = email_config["to_email"]
    msg.set_content(text)
    port = int(email_config.get("smtp_port") or 587)
    with smtplib.SMTP(email_config["smtp_host"], port, timeout=20) as smtp:
        if email_config.get("use_starttls", True):
            smtp.starttls()
        if email_config.get("username"):
            smtp.login(email_config["username"], email_config.get("password", ""))
        smtp.send_message(msg)
    return {"ok": True, "provider": "email_to_sms"}


def send_webhook_notification(config: dict[str, Any], subject: str, text: str) -> dict[str, Any]:
    webhook = config["webhook"]
    payload = json.dumps({"subject": subject, "message": text, "source": "PANDA Agent Hub"}).encode("utf-8")
    headers = {"Content-Type": "application/json", **dict(webhook.get("headers", {}))}
    request = Request(webhook["url"], data=payload, method="POST", headers=headers)
    with urlopen(request, timeout=20) as response:
        return {"ok": True, "provider": "webhook", "status": response.status}


def attention_events(messages: list[Message], decisions: list[dict[str, str]]) -> list[dict[str, str]]:
    events: list[dict[str, str]] = []
    for msg in messages[:40]:
        if is_urgent_codex_request_message(msg):
            events.append(
                {
                    "kind": "urgent_codex_request",
                    "fingerprint": f"urgent-codex:{msg.message_id or msg.path}",
                    "subject": "URGENT request for Codex",
                    "body": compact(f"{msg.title} | {msg.summary or msg.body_preview}", 500),
                    "path": str(msg.path),
                }
            )
    for item in decisions[:5]:
        events.append(
            {
                "kind": "darrin_decision_needed",
                "fingerprint": f"decision:{item['path']}",
                "subject": "Darrin decision needed",
                "body": compact(f"{item['title']} | {item['summary']}", 500),
                "path": item["path"],
            }
        )
    for msg in messages[:20]:
        if msg.direction == "Claude -> Codex" and msg.is_request and not msg.is_waiting_on_darrin:
            events.append(
                {
                    "kind": "claude_response_requested",
                    "fingerprint": f"response:{msg.message_id or msg.path}",
                    "subject": "Claude response requested",
                    "body": compact(f"{msg.title} | {msg.summary or msg.body_preview}", 500),
                    "path": str(msg.path),
                }
            )
    return events


def run_notification_scan(manual_test: bool = False) -> dict[str, Any]:
    with NOTIFICATION_LOCK:
        config = load_notification_config()
        state_data = read_json(NOTIFICATION_STATE_PATH, {})
        now = time.time()
        if manual_test:
            result = send_notification(config, "Test notification", "Your PANDA Agent Hub SMS notification path is connected.")
            real_delivery_attempted = str(result.get("provider", "log_only")) != "log_only"
            state_data["last_sent_at"] = datetime.now().isoformat(timespec="seconds")
            state_data["last_error"] = ""
            write_json(NOTIFICATION_STATE_PATH, state_data)
            append_notification_log({"time": state_data["last_sent_at"], "manual_test": True, "result": result})
            return {
                "sent": 1 if real_delivery_attempted else 0,
                "logged": 0 if real_delivery_attempted else 1,
                "real_delivery_attempted": real_delivery_attempted,
                "result": result,
            }
        messages = load_messages()
        message_by_path = {str(msg.path): msg for msg in messages}
        decisions = build_decision_queue(messages, write_file=False)
        enabled_kinds = {key for key, enabled in dict(config.get("notify_on", {})).items() if enabled}
        all_events = attention_events(messages, decisions)
        urgent_events = [event for event in all_events if event["kind"] == "urgent_codex_request"]
        enabled_events = [
            event
            for event in all_events
            if config.get("enabled") and event["kind"] in enabled_kinds and event["kind"] != "urgent_codex_request"
        ]
        events = [*urgent_events, *enabled_events]
        if not events:
            return {"sent": 0, "logged": 0, "enabled": bool(config.get("enabled")), "urgent_breakthrough_logged": 0}

        sent = dict(state_data.get("sent", {}))
        if config.get("enabled") and not state_data.get("baseline_initialized") and not config.get("send_existing_on_start"):
            baseline_events = [event for event in events if event["kind"] != "urgent_codex_request"]
            for event in baseline_events:
                sent[event["fingerprint"]] = {"baseline": True, "time": datetime.now().isoformat(timespec="seconds")}
                target = message_by_path.get(event["path"])
                if target and target.message_id:
                    try:
                        record_processed_message_event(
                            target.message_id,
                            target.path,
                            target.body,
                            event=f"notification:{event['kind']}",
                            outcome="baseline",
                        )
                    except (OSError, ValueError) as exc:
                        append_notification_log(
                            {
                                "time": datetime.now().isoformat(timespec="seconds"),
                                "event": event,
                                "error": str(exc),
                            }
                        )
            state_data["sent"] = sent
            state_data["baseline_initialized"] = True
            write_json(NOTIFICATION_STATE_PATH, state_data)
            events = [event for event in events if event["kind"] == "urgent_codex_request"]
            if not events:
                return {
                    "sent": 0,
                    "logged": 0,
                    "enabled": True,
                    "baseline_initialized": True,
                    "urgent_breakthrough_logged": 0,
                }

        cooldown_seconds = max(0, int(config.get("cooldown_minutes", 30))) * 60
        last_sent_epoch = float(state_data.get("last_sent_epoch", 0) or 0)
        delivery_config = json.loads(json.dumps(config))
        if not delivery_config.get("enabled"):
            delivery_config["provider"] = "log_only"
        sent_count = 0
        logged_count = 0
        urgent_breakthrough_logged = 0
        for event in events:
            if event["fingerprint"] in sent:
                continue
            target = message_by_path.get(event["path"])
            if target and target.message_id:
                idempotency_status = processed_message_event_status(
                    target.message_id,
                    target.path,
                    target.body,
                    event=f"notification:{event['kind']}",
                )
                if idempotency_status.status == "already_processed":
                    sent[event["fingerprint"]] = {
                        "time": datetime.now().isoformat(timespec="seconds"),
                        "path": event["path"],
                        "sidecar": str(idempotency_status.sidecar_path),
                    }
                    continue
                if idempotency_status.status == "content_mismatch":
                    state_data["last_error"] = (
                        f"Notification skipped: processed sidecar hash mismatch for {target.message_id}"
                    )
                    append_notification_log(
                        {
                            "time": datetime.now().isoformat(timespec="seconds"),
                            "event": event,
                            "error": state_data["last_error"],
                        }
                    )
                    continue
            if event["kind"] != "urgent_codex_request" and cooldown_seconds and now - last_sent_epoch < cooldown_seconds:
                continue
            try:
                result = send_notification(delivery_config, event["subject"], event["body"])
                sent[event["fingerprint"]] = {"time": datetime.now().isoformat(timespec="seconds"), "path": event["path"]}
                if target and target.message_id:
                    record = record_processed_message_event(
                        target.message_id,
                        target.path,
                        target.body,
                        event=f"notification:{event['kind']}",
                        outcome="sent",
                    )
                    sent[event["fingerprint"]]["sidecar"] = str(
                        processed_message_event_status(
                            target.message_id,
                            target.path,
                            target.body,
                            event=f"notification:{event['kind']}",
                        ).sidecar_path
                    )
                    sent[event["fingerprint"]]["content_hash"] = str(record.get("content_hash", ""))
                state_data["last_sent_at"] = sent[event["fingerprint"]]["time"]
                state_data["last_sent_epoch"] = now
                state_data["last_error"] = ""
                if str(result.get("provider", "log_only")) == "log_only":
                    logged_count += 1
                else:
                    sent_count += 1
                if event["kind"] == "urgent_codex_request":
                    urgent_breakthrough_logged += 1
                    state_data["last_urgent_breakthrough_at"] = sent[event["fingerprint"]]["time"]
                append_notification_log({"time": state_data["last_sent_at"], "event": event, "result": result})
            except (HTTPError, URLError, OSError, RuntimeError, ValueError, smtplib.SMTPException) as exc:
                state_data["last_error"] = str(exc)
                append_notification_log({"time": datetime.now().isoformat(timespec="seconds"), "event": event, "error": str(exc)})
                break
        state_data["sent"] = sent
        state_data["baseline_initialized"] = True
        write_json(NOTIFICATION_STATE_PATH, state_data)
        return {
            "sent": sent_count,
            "logged": logged_count,
            "enabled": bool(config.get("enabled")),
            "urgent_breakthrough_logged": urgent_breakthrough_logged,
        }


def notification_loop() -> None:
    while True:
        run_notification_scan()
        time.sleep(30)


def build_decision_queue(
    messages: list[Message], write_file: bool = True, include_inactive: bool = False
) -> list[dict[str, str]]:
    decisions: list[dict[str, str]] = []
    state_data = load_decision_state()
    for msg in messages:
        if msg.is_waiting_on_darrin or "decision needed" in msg.status.lower():
            record = decision_record_for(msg.path, state_data)
            state_name = str(record.get("state", ACTIVE_STATE))
            if not include_inactive and not decision_is_active(msg.path, state_data):
                continue
            decisions.append(
                {
                    "title": msg.title,
                    "status": msg.status or msg.thread_status,
                    "summary": msg.summary or msg.body_preview,
                    "path": str(msg.path),
                    "generated": msg.generated,
                    "decision_state": state_name,
                    "state_note": str(record.get("note", "")),
                    "state_actor": str(record.get("actor", "")),
                    "state_updated_at": str(record.get("updated_at", "")),
                }
            )
    decisions = decisions[:30]
    if write_file:
        lines = [
            "# CODEX Darrin Decisions Needed",
            "",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
        ]
        if not decisions:
            lines.append("No explicit Darrin decision items found in current mailbox metadata.")
        for index, item in enumerate(decisions, 1):
            lines.extend(
                [
                    f"## {index}. {item['title']}",
                    "",
                    f"Status: {item['status'] or 'Unspecified'}",
                    f"Source: `{item['path']}`",
                    "",
                    item["summary"] or "No summary found.",
                    "",
                ]
            )
        atomic_write_text(DECISION_QUEUE_PATH, "\n".join(lines))
    return decisions


def urgent_codex_request_rows(
    messages: list[Message], read_state_data: dict[str, Any] | None = None, limit: int = 20
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for msg in messages:
        if not is_urgent_codex_request_message(msg):
            continue
        if message_has_reply_tombstone(msg) or classify_thread_state(msg) == "closed":
            continue
        read_status = message_read_status(msg.path, msg.message_id, msg.body, read_state_data)
        age_seconds = max(0, int(time.time() - msg.modified))
        from_label = participant_label(msg.from_agent)
        rows.append(
            {
                "id": f"urgent:{msg.message_id or message_cache_key(msg.path)}",
                "kind": "urgent",
                "severity": "err",
                "state": "urgent_codex_request",
                "state_label": "URGENT to Codex",
                "title": msg.title,
                "summary": msg.summary or msg.body_preview,
                "primary_action": "Open now",
                "secondary_action": "Urgent",
                "message_path": str(msg.path),
                "thread_id": msg.stable_thread,
                "message_id": msg.message_id,
                "age_seconds": age_seconds,
                "message_count": 1,
                "agent_label": from_label,
                "owner_label": "Codex",
                "owner": "codex",
                "from_agent": msg.from_agent,
                "to_agent": msg.to_agent,
                "priority": msg.priority,
                "read_state": read_status["state"],
                "unread": read_status["unread"],
                "requires_darrin_decision": False,
                "wake_line": (
                    f"URGENT for Codex: read {msg.message_id or msg.stable_thread} "
                    f"from {from_label} and reply before lower-priority work."
                ),
            }
        )
    rows.sort(key=lambda item: (-int(item.get("age_seconds", 0) or 0), str(item.get("title", ""))))
    return rows[:limit]


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", value.strip()).strip("-").lower()
    return slug[:42] or "message"


def create_message(payload: dict[str, Any]) -> dict[str, Any]:
    route = str(payload.get("route", "codex_to_claude"))
    subject = compact(str(payload.get("subject", "Agent Hub message")).strip(), 90)
    body = str(payload.get("body", "")).strip()
    ui_status = str(payload.get("status", "Info")).strip() or "Info"
    thread_id = str(payload.get("thread_id", "")).strip()
    reply_to = str(payload.get("reply_to", "")).strip()
    dry_run = bool(payload.get("dry_run", False))

    now = datetime.now()
    stamp = now.strftime("%Y%m%d_%H%M%S")
    created_at = now.astimezone().isoformat(timespec="seconds")
    generated = local_timestamp()

    if route == "claude_to_codex" and not ALLOW_SIMULATED_INBOUND:
        raise RuntimeError("Inbound Claude simulation is disabled outside test mode.")

    from_id, to_id = route_participants(route)
    from_agent = participant_label(from_id)
    to_agent = participant_label(to_id)

    if route == "claude_to_codex":
        inbox = CODEX_INBOX
    elif route == "codex_to_claude_code":
        inbox = CLAUDE_CODE_INBOX
    else:
        inbox = CLAUDE_INBOX

    file_from = from_id.upper().replace("-", "_")
    file_to = to_id.upper().replace("-", "_")
    slug = safe_slug(subject)
    filename = f"{stamp}_{file_from}_to_{file_to}_{slug}.md"
    message_id = f"PAH-{stamp.replace('_', '-')}-{from_id}-to-{to_id}-{slug}"
    thread_id = thread_id or f"PAH-{stamp.replace('_', '-')}-{slug}"

    status_lower = ui_status.lower()
    msg_type = "coordination"
    schema_status = "open"
    thread_status = "active"
    priority = "normal"
    requires_darrin_decision = False
    if "response" in status_lower:
        msg_type = "response_request"
        thread_status = "waiting_on_agent"
        priority = "high"
    elif "decision" in status_lower:
        msg_type = "decision_request"
        schema_status = "blocked"
        thread_status = "waiting_on_darrin"
        priority = "high"
        requires_darrin_decision = True
    elif "implementation" in status_lower:
        msg_type = "implementation_report"
        schema_status = "review_complete"

    path = inbox / filename
    title = f"{from_agent.upper()} -> {to_agent.upper()}: {subject}"
    reply_lines = [line.strip() for line in reply_to.splitlines() if line.strip()]
    metadata = {
        "schema_version": MESSAGE_SCHEMA_VERSION,
        "message_id": message_id,
        "thread_id": thread_id,
        "created_at": created_at,
        "from": from_id,
        "to": to_id,
        "type": msg_type,
        "priority": priority,
        "status": schema_status,
        "thread_status": thread_status,
        "approval_boundary": "coordination_only",
        "requires_darrin_decision": requires_darrin_decision,
    }
    if reply_lines:
        metadata["reply_to"] = reply_lines
    text = render_message_markdown(
        metadata,
        title,
        compact(body, 280) if body else subject,
        body or "No additional detail supplied.",
    )
    reply_tombstones: list[dict[str, Any]] = []
    if not dry_run:
        inbox.mkdir(parents=True, exist_ok=True)
        atomic_write_text(path, text)
        append_interaction_ledger_event(
            "message_sent",
            actor=from_id,
            route=route,
            message_id=message_id,
            thread_id=thread_id,
            subject=subject,
            status=schema_status,
            thread_status=thread_status,
            message_type=msg_type,
            from_agent=from_id,
            to_agent=to_id,
            path=path,
            created_at=created_at,
            content_hash=content_hash(text),
        )
        if reply_lines:
            reply_tombstones = write_reply_tombstones(
                reply_lines,
                reply_message_id=message_id,
                reply_thread_id=thread_id,
                reply_path=path,
                reply_from=from_id,
                reply_to=to_id,
                route=route,
                replied_at=created_at,
                actor=from_id,
            )

    if not dry_run and (ui_status in IMPORTANT_STATUSES or "request" in ui_status.lower() or "decision" in ui_status.lower()):
        ledger_line = (
            f"{generated} | {from_agent}->{to_agent} | {ui_status.lower()} | "
            f"{subject} | {inbox.name}\\{filename} | {path}\n"
        )
        atomic_append_text(LEDGER_PATH, ledger_line)

    return {
        "path": str(path),
        "message_id": message_id,
        "thread_id": thread_id,
        "dry_run": dry_run,
        "reply_tombstones": reply_tombstones,
    }


def run_mailroom_transaction_canary(actor: str = "pah_inspector") -> dict[str, Any]:
    """Exercise send, read-state, reply tombstone, and ledger writes in isolation."""
    with MAILROOM_CANARY_LOCK, TemporaryDirectory(prefix="pah_mailroom_canary_") as temp_dir:
        root = Path(temp_dir)
        inbox = root / "CLAUDE Inbox"
        ledger_path = root / "CODEX_MAILBOX_LEDGER.md"
        interaction_ledger_path = root / "CODEX logs" / "CODEX_pah_interaction_ledger.jsonl"
        read_state_path = root / "read_state.json"
        original_set_message_read_state = set_message_read_state
        original_values = {
            "CLAUDE_INBOX": CLAUDE_INBOX,
            "LEDGER_PATH": LEDGER_PATH,
            "INTERACTION_LEDGER_PATH": INTERACTION_LEDGER_PATH,
            "MESSAGE_DIRS": MESSAGE_DIRS,
        }

        def isolated_set_message_read_state(
            path_value: Path | str,
            message_id: str,
            text: str,
            state_name: str,
            actor: str = "codex",
            state_path: Path = read_state_path,
        ) -> dict[str, Any]:
            return original_set_message_read_state(path_value, message_id, text, state_name, actor=actor, state_path=read_state_path)

        try:
            globals()["CLAUDE_INBOX"] = inbox
            globals()["LEDGER_PATH"] = ledger_path
            globals()["INTERACTION_LEDGER_PATH"] = interaction_ledger_path
            globals()["MESSAGE_DIRS"] = (("Codex -> Claude", inbox),)
            globals()["set_message_read_state"] = isolated_set_message_read_state
            clear_message_parse_cache()

            original = create_message(
                {
                    "route": "codex_to_claude",
                    "status": "Response",
                    "subject": "PAH mailroom canary source",
                    "thread_id": "PAH-MAILROOM-CANARY",
                    "body": "Isolated canary source message.",
                }
            )
            original_path = Path(str(original["path"]))
            original_exists = original_path.exists()
            read_result = set_read_state_for_message(str(original_path), READ_STATE, actor=actor)
            reply = create_message(
                {
                    "route": "codex_to_claude",
                    "status": "Info",
                    "subject": "PAH mailroom canary reply",
                    "thread_id": "PAH-MAILROOM-CANARY",
                    "reply_to": str(original["message_id"]),
                    "body": "Isolated canary reply message.",
                }
            )
            tombstones = list(reply.get("reply_tombstones", []))
            tombstone_path = Path(str(tombstones[0].get("tombstone_path", ""))) if tombstones else Path("")
            ledger_events = []
            if interaction_ledger_path.exists():
                for line in interaction_ledger_path.read_text(encoding="utf-8").splitlines():
                    if line.strip():
                        ledger_events.append(json.loads(line))
            event_types = {str(event.get("event_type", "")) for event in ledger_events}
            checks = {
                "source_written": original_exists,
                "read_state_written": read_result.get("state") == READ_STATE and read_state_path.exists(),
                "reply_written": Path(str(reply["path"])).exists(),
                "reply_tombstone_written": bool(tombstones) and tombstone_path.exists(),
                "ledger_sent_event": "message_sent" in event_types,
                "ledger_read_event": "message_read_marked" in event_types,
                "ledger_tombstone_event": "message_reply_tombstoned" in event_types,
            }
            return {
                "ok": all(checks.values()),
                "checks": checks,
                "source_path": str(original_path),
                "reply_path": str(reply["path"]),
                "tombstone_path": str(tombstone_path) if tombstones else "",
                "read_state_path": str(read_state_path),
                "interaction_ledger_path": str(interaction_ledger_path),
                "event_types": sorted(event_types),
            }
        finally:
            for key, value in original_values.items():
                globals()[key] = value
            globals()["set_message_read_state"] = original_set_message_read_state
            clear_message_parse_cache()


def dispatch_work_item(item_id: str) -> dict[str, Any]:
    board = work_board_status()
    item = next((row for row in board["items"] if row.get("item_id") == item_id), None)
    if not item:
        raise KeyError(f"Unknown work item: {item_id}")
    owner = str(item.get("owner", "codex"))
    if owner == "claude-desktop":
        route = "codex_to_claude"
    elif owner == "claude-code":
        route = "codex_to_claude_code"
    elif owner == "codex":
        dispatch = {
            "route": "local_codex",
            "message_id": "",
            "path": "",
            "dispatched_at": datetime.now().isoformat(timespec="seconds"),
            "note": "Local Codex work item marked in progress; no mailbox dispatch needed.",
        }
        return update_work_item(item_id, state="in_progress", dispatch=dispatch)
    else:
        raise ValueError(f"Work item owner cannot receive dispatch: {owner}")

    result = create_message(
        {
            "route": route,
            "status": "Response Requested",
            "subject": f"Work item: {item.get('title', item_id)}",
            "thread_id": item_id,
            "reply_to": item_id,
            "body": "\n".join(
                [
                    "PAH work item dispatch.",
                    "",
                    f"Work Item: {item_id}",
                    f"Owner: {owner}",
                    f"Priority: {item.get('priority', 'normal')}",
                    "",
                    "Summary:",
                    str(item.get("summary", "") or "No summary supplied."),
                    "",
                    "Please reply to this thread with status, blockers, or completion details.",
                ]
            ),
        }
    )
    dispatch = {
        "route": route,
        "message_id": result["message_id"],
        "path": result["path"],
        "dispatched_at": datetime.now().isoformat(timespec="seconds"),
        "note": "Mailbox dispatch created from PAH Work Board.",
    }
    return update_work_item(item_id, state="in_progress", dispatch=dispatch)


def find_loaded_message(path_value: str, messages: list[Message] | None = None) -> Message:
    target = Path(path_value)
    try:
        resolved = target.resolve()
    except OSError:
        resolved = target
    for msg in messages or load_messages():
        try:
            if msg.path.resolve() == resolved:
                return msg
        except OSError:
            if str(msg.path) == str(target):
                return msg
    raise KeyError(f"Unknown PAH mailbox message: {path_value}")


def set_read_state_for_message(path_value: str, state_name: str, actor: str = "codex") -> dict[str, Any]:
    msg = find_loaded_message(path_value)
    result = set_message_read_state(msg.path, msg.message_id, msg.body, state_name, actor=actor)
    append_interaction_ledger_event(
        "message_read_marked" if state_name == READ_STATE else "message_unread_marked",
        actor=actor,
        message=msg,
        read_state=state_name,
        state_path=READ_STATE_PATH,
    )
    return result


def mark_all_messages_read(actor: str = "codex") -> dict[str, Any]:
    messages = load_messages()
    for msg in messages:
        set_message_read_state(msg.path, msg.message_id, msg.body, READ_STATE, actor=actor)
        append_interaction_ledger_event(
            "message_read_marked",
            actor=actor,
            message=msg,
            read_state=READ_STATE,
            source="mark_all_messages_read",
            state_path=READ_STATE_PATH,
        )
    return {"count": len(messages), "state_path": str(READ_STATE_PATH)}


def normalize_agent_id(value: str) -> str:
    normalized = safe_slug(value).replace("_", "-")
    aliases = {
        "cc": "claude-code",
        "claude": "claude-desktop",
        "claude-desktop": "claude-desktop",
        "claude-code": "claude-code",
        "cd": "claude-desktop",
        "codex": "codex",
        "darrin": "darrin",
    }
    return aliases.get(normalized, normalized)


def validate_agent_no_mail_claim(
    agent_id: str,
    actor: str = "pah",
    claim: str = "no_mail",
    note: str = "",
) -> dict[str, Any]:
    agent = normalize_agent_id(agent_id)
    if agent not in AGENT_INBOX_DIRS:
        raise ValueError(f"Unknown agent for no-mail claim: {agent_id}")

    messages = load_messages()
    read_state_data = load_read_state()
    agent_mailboxes = build_agent_mailbox_messages(messages, read_state_data)
    visible_items = list(agent_mailboxes.get(agent, []))
    physical_unread: list[dict[str, Any]] = []
    waiting_on_darrin: list[dict[str, Any]] = []
    owner_unknown: list[dict[str, Any]] = []

    for msg in messages:
        if not message_in_agent_inbox(msg, agent):
            continue
        if not message_read_status(msg.path, msg.message_id, msg.body, read_state_data)["unread"]:
            continue
        item = {
            "message_id": msg.message_id,
            "thread_id": msg.stable_thread,
            "title": msg.title,
            "path": str(msg.path),
            "from": msg.from_agent,
            "to": msg.to_agent,
            "classifier_state": classify_thread_state(msg),
        }
        physical_unread.append(item)
        if msg.is_waiting_on_darrin:
            waiting_on_darrin.append(item)
        if item["classifier_state"] == "owner_unknown":
            owner_unknown.append(item)

    visible_ids = {str(item.get("message_id") or item.get("path", "")) for item in visible_items}
    physical_ids = {str(item.get("message_id") or item.get("path", "")) for item in physical_unread}
    unexpected_items = [
        item
        for item in physical_unread
        if str(item.get("message_id") or item.get("path", "")) not in visible_ids
    ]
    ok = not visible_items and not physical_unread
    event_type = "agent_no_mail_claim_validated" if ok else "agent_no_mail_claim_discrepancy"
    event = append_interaction_ledger_event(
        event_type,
        actor=actor,
        agent=agent,
        claim=claim,
        note=note,
        ok=ok,
        actionable_unread_count=len(visible_items),
        physical_unread_count=len(physical_unread),
        waiting_on_darrin_count=len(waiting_on_darrin),
        owner_unknown_count=len(owner_unknown),
        visible_message_ids=sorted(visible_ids),
        physical_message_ids=sorted(physical_ids),
        unexpected_items=unexpected_items[:20],
    )
    return {
        "schema_version": 1,
        "ok": ok,
        "agent": agent,
        "claim": claim,
        "note": note,
        "actionable_unread_count": len(visible_items),
        "physical_unread_count": len(physical_unread),
        "waiting_on_darrin_count": len(waiting_on_darrin),
        "owner_unknown_count": len(owner_unknown),
        "visible_items": visible_items[:20],
        "physical_unread_items": physical_unread[:20],
        "unexpected_items": unexpected_items[:20],
        "ledger_event": {"event_type": event.get("event_type", ""), "time": event.get("time", "")},
        "ledger_path": str(INTERACTION_LEDGER_PATH),
    }


def unique_destination(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    for index in range(1, 1000):
        candidate = path.with_name(f"{stem}_{index:03d}{suffix}")
        if not candidate.exists():
            return candidate
    raise FileExistsError(f"Could not find unique archive destination for {path}")


def cleanup_archive_root_for(path: Path) -> Path:
    parent = path.parent
    for inbox_dir, archive_root in CLEANUP_ARCHIVE_ROOTS.items():
        try:
            if parent.resolve() == inbox_dir.resolve():
                return archive_root
        except OSError:
            if parent == inbox_dir:
                return archive_root
    return CODEX_ARCHIVE / "Inbox Cleanup"


def cleanup_inbox_dirs() -> tuple[Path, ...]:
    return tuple(dict.fromkeys(path for paths in CLEANUP_MAILBOX_TARGETS.values() for path in paths))


def cleanup_target_dirs(mailbox: str) -> tuple[Path, ...]:
    target = safe_slug(mailbox or "all")
    if target not in CLEANUP_MAILBOX_TARGETS:
        raise ValueError(f"Unknown mailbox cleanup target: {mailbox}")
    return tuple(dict.fromkeys(CLEANUP_MAILBOX_TARGETS[target]))


def sweep_audit_header() -> str:
    return "\n".join(
        [
            "# PAH Sweep Audit Log",
            "",
            "Append-only log of archive-read sweeps. PAH writes; Darrin, CC, and CD can read.",
            "",
            "Format: `- TIMESTAMP_ISO  [action]  source_path  -> detail`",
            "",
            "## Entries",
            "",
        ]
    )


def sweep_audit_safe(value: str) -> str:
    return " ".join(str(value or "").replace("`", "'").split()) or "-"


def append_sweep_audit_entries(entries: list[tuple[str, str, str]]) -> None:
    if not entries:
        return
    lines: list[str] = []
    if not SWEEP_AUDIT_LOG_PATH.exists():
        lines.append(sweep_audit_header())
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    for action, source, detail in entries:
        lines.append(
            f"- `{timestamp}`  `[{sweep_audit_safe(action)}]`  `{sweep_audit_safe(source)}`  -> {sweep_audit_safe(detail)}\n"
        )
    atomic_append_text(SWEEP_AUDIT_LOG_PATH, "".join(lines))


def cleanup_inbox_accumulation(
    actor: str = "codex",
    older_than_hours: int = MESSAGE_RETENTION_HOURS,
    dry_run: bool = True,
    mailbox: str = "all",
) -> dict[str, Any]:
    _ = older_than_hours
    inbox_dirs = cleanup_target_dirs(mailbox)
    moved: list[dict[str, Any]] = []
    skipped = {"missing_inbox": 0, "non_markdown": 0}

    for inbox_dir in inbox_dirs:
        if not inbox_dir.exists():
            skipped["missing_inbox"] += 1
            continue
        for path in sorted(inbox_dir.iterdir(), key=lambda item: item.name.lower()):
            if not path.is_file():
                continue
            if path.suffix.lower() != ".md":
                skipped["non_markdown"] += 1
                continue
            modified = path.stat().st_mtime
            date_dir = datetime.fromtimestamp(modified).strftime("%Y%m%d")
            archive_dir = cleanup_archive_root_for(path) / inbox_dir.name / date_dir
            destination = unique_destination(archive_dir / path.name)
            record = {
                "source": str(path),
                "destination": str(destination),
                "inbox": str(inbox_dir),
                "archive": str(archive_dir),
            }
            if not dry_run:
                archive_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(str(path), str(destination))
            moved.append(record)

    return {
        "actor": actor.strip() or "codex",
        "dry_run": dry_run,
        "mailbox": safe_slug(mailbox or "all"),
        "count": len(moved),
        "moved": moved,
        "skipped": skipped,
    }


def archive_read_codex_inbox_messages(actor: str = "codex", dry_run: bool = False) -> dict[str, Any]:
    started = time.perf_counter()
    actor_name = actor.strip() or "codex"
    append_interaction_ledger_event(
        "archive_read_sweep_started",
        actor=actor_name,
        dry_run=dry_run,
        classifier="owner_unknown_guard",
    )
    audit_entries: list[tuple[str, str, str]] = [
        (
            "sweep-started",
            "-",
            f"actor={actor_name}; dry_run={str(bool(dry_run)).lower()}; classifier=owner_unknown_guard",
        )
    ]
    read_state_data = load_read_state()
    inbox_dirs = cleanup_inbox_dirs()
    inbox_summary: dict[str, dict[str, Any]] = {}
    for inbox_dir in inbox_dirs:
        key = str(inbox_dir)
        inbox_summary[key] = {
            "path": key,
            "name": inbox_dir.name,
            "scanned": 0,
            "candidates": 0,
            "moved": 0,
            "skipped_unread": 0,
            "skipped_waiting_on_darrin": 0,
            "skipped_pre_staged_pending_trigger": 0,
            "skipped_pending_dispatch": 0,
            "skipped_active_thread": 0,
            "skipped_unstructured": 0,
            "replied_tombstone": 0,
            "archive_conflicts": 0,
        }

    def summary_for(path: Path) -> dict[str, Any]:
        key = str(path.parent)
        if key not in inbox_summary:
            inbox_summary[key] = {
                "path": key,
                "name": path.parent.name,
                "scanned": 0,
                "candidates": 0,
                "moved": 0,
                "skipped_unread": 0,
                "skipped_waiting_on_darrin": 0,
                "skipped_pre_staged_pending_trigger": 0,
                "skipped_pending_dispatch": 0,
                "skipped_active_thread": 0,
                "skipped_unstructured": 0,
                "replied_tombstone": 0,
                "archive_conflicts": 0,
            }
        return inbox_summary[key]

    messages = load_messages()
    completed_threads = completed_thread_ids(messages)
    candidates: list[Message] = []
    skipped_waiting = 0
    skipped_pre_staged = 0
    skipped_pending_dispatch = 0
    skipped_active_thread = 0
    skipped_unstructured = 0
    replied_tombstone_candidates = 0
    candidate_reasons: dict[str, str] = {}
    for msg in messages:
        if not message_parent_in(msg, inbox_dirs):
            continue
        summary = summary_for(msg.path)
        summary["scanned"] += 1
        reply_tombstone = load_reply_tombstone(msg)
        if reply_tombstone:
            replied_tombstone_candidates += 1
            summary["replied_tombstone"] += 1
            summary["candidates"] += 1
            candidate_reasons[message_cache_key(msg.path)] = "replied_tombstone"
            candidates.append(msg)
            continue
        thread_state = classify_thread_state(msg)
        if thread_state == "owner_unknown" or not is_structured_mailbox_message(msg):
            skipped_unstructured += 1
            summary["skipped_unstructured"] += 1
            audit_entries.append(
                (
                    "archive-skipped",
                    str(msg.path),
                    "reason=owner_unknown_or_unstructured; no parseable frontmatter/message_id; never auto-archive",
                )
            )
            append_interaction_ledger_event(
                "message_archive_skipped",
                actor=actor_name,
                message=msg,
                dry_run=dry_run,
                reason="owner_unknown_or_unstructured",
                classifier_state=thread_state,
            )
            continue
        if is_pre_staged_pending_trigger(msg):
            skipped_pre_staged += 1
            summary["skipped_pre_staged_pending_trigger"] += 1
            audit_entries.append(("archive-skipped", str(msg.path), "reason=pre_staged_pending_trigger"))
            append_interaction_ledger_event(
                "message_archive_skipped",
                actor=actor_name,
                message=msg,
                dry_run=dry_run,
                reason="pre_staged_pending_trigger",
                classifier_state=thread_state,
            )
            continue
        if msg.is_waiting_on_darrin:
            skipped_waiting += 1
            summary["skipped_waiting_on_darrin"] += 1
            audit_entries.append(("archive-skipped", str(msg.path), "reason=waiting_on_darrin"))
            append_interaction_ledger_event(
                "message_archive_skipped",
                actor=actor_name,
                message=msg,
                dry_run=dry_run,
                reason="waiting_on_darrin",
                classifier_state=thread_state,
            )
            continue
        if is_dispatch_message(msg) and msg.stable_thread not in completed_threads:
            skipped_pending_dispatch += 1
            summary["skipped_pending_dispatch"] += 1
            audit_entries.append(("archive-skipped", str(msg.path), "reason=pending_dispatch_without_completion_evidence"))
            append_interaction_ledger_event(
                "message_archive_skipped",
                actor=actor_name,
                message=msg,
                dry_run=dry_run,
                reason="pending_dispatch_without_completion_evidence",
                classifier_state=thread_state,
            )
            continue
        if thread_state in {"open_on_agent", "open_on_darrin", "parked"}:
            skipped_active_thread += 1
            summary["skipped_active_thread"] += 1
            audit_entries.append(("archive-skipped", str(msg.path), f"reason=active_thread_without_completion_evidence; state={thread_state}"))
            append_interaction_ledger_event(
                "message_archive_skipped",
                actor=actor_name,
                message=msg,
                dry_run=dry_run,
                reason="active_thread_without_completion_evidence",
                classifier_state=thread_state,
            )
            continue
        read_status = message_read_status(msg.path, msg.message_id, msg.body, read_state_data)
        if read_status["unread"]:
            summary["skipped_unread"] += 1
            continue
        summary["candidates"] += 1
        candidates.append(msg)

    moved: list[dict[str, str]] = []
    archive_conflicts = 0
    for msg in candidates:
        archive_reason = candidate_reasons.get(message_cache_key(msg.path), "read")
        archive_dir = cleanup_archive_root_for(msg.path) / msg.path.parent.name / datetime.fromtimestamp(
            msg.path.stat().st_mtime
        ).strftime("%Y%m%d")
        requested_destination = archive_dir / msg.path.name
        destination = unique_destination(requested_destination)
        destination_conflict = destination != requested_destination
        tombstone_source = reply_tombstone_path(msg.path)
        tombstone_destination = destination.with_name(destination.name + REPLIED_TOMBSTONE_SUFFIX)
        tombstone_exists = tombstone_source.exists()
        if tombstone_exists:
            tombstone_destination = unique_destination(tombstone_destination)
        record = {
            "message_id": msg.message_id,
            "thread_id": msg.stable_thread,
            "from": msg.from_agent,
            "to": msg.to_agent,
            "archive_reason": archive_reason,
            "source": str(msg.path),
            "requested_destination": str(requested_destination),
            "destination": str(destination),
            "archive": str(archive_dir),
            "destination_conflict": destination_conflict,
        }
        if tombstone_exists:
            record["tombstone_source"] = str(tombstone_source)
            record["tombstone_destination"] = str(tombstone_destination)
        if destination_conflict:
            archive_conflicts += 1
            summary_for(msg.path)["archive_conflicts"] += 1
        if not dry_run:
            archive_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(msg.path), str(destination))
            if tombstone_exists:
                shutil.move(str(tombstone_source), str(tombstone_destination))
            summary_for(msg.path)["moved"] += 1
            audit_entries.append(
                (
                    "archive-moved",
                    str(msg.path),
                    (
                        f"destination={destination}; requested_destination={requested_destination}; "
                        f"destination_conflict={str(destination_conflict).lower()}; "
                        f"archive_reason={archive_reason}; thread_id={msg.stable_thread}"
                    ),
                )
            )
            append_interaction_ledger_event(
                "message_archived",
                actor=actor_name,
                message=msg,
                source_path=msg.path,
                requested_destination=requested_destination,
                destination_path=destination,
                archive_dir=archive_dir,
                destination_conflict=destination_conflict,
                archive_reason=archive_reason,
                tombstone_source=tombstone_source if tombstone_exists else None,
                tombstone_destination=tombstone_destination if tombstone_exists else None,
            )
        else:
            audit_entries.append(
                (
                    "archive-candidate",
                    str(msg.path),
                    (
                        f"destination={destination}; requested_destination={requested_destination}; "
                        f"destination_conflict={str(destination_conflict).lower()}; "
                        f"archive_reason={archive_reason}; thread_id={msg.stable_thread}"
                    ),
                )
            )
            append_interaction_ledger_event(
                "message_archive_candidate",
                actor=actor_name,
                message=msg,
                source_path=msg.path,
                requested_destination=requested_destination,
                destination_path=destination,
                archive_dir=archive_dir,
                destination_conflict=destination_conflict,
                archive_reason=archive_reason,
                tombstone_source=tombstone_source if tombstone_exists else None,
                tombstone_destination=tombstone_destination if tombstone_exists else None,
                dry_run=True,
            )
        moved.append(record)

    duration_ms = int((time.perf_counter() - started) * 1000)
    audit_entries.append(
        (
            "sweep-finished",
            "-",
            (
                f"moved={len(moved)}; skipped_waiting_on_darrin={skipped_waiting}; "
                f"skipped_pre_staged_pending_trigger={skipped_pre_staged}; "
                f"skipped_pending_dispatch={skipped_pending_dispatch}; skipped_active_thread={skipped_active_thread}; "
                f"skipped_unstructured={skipped_unstructured}; replied_tombstone={replied_tombstone_candidates}; "
                f"archive_conflicts={archive_conflicts}; "
                f"duration_ms={duration_ms}"
            ),
        )
    )
    append_sweep_audit_entries(audit_entries)
    append_interaction_ledger_event(
        "archive_read_sweep_finished",
        actor=actor_name,
        dry_run=dry_run,
        moved=len(moved),
        skipped_waiting_on_darrin=skipped_waiting,
        skipped_pre_staged_pending_trigger=skipped_pre_staged,
        skipped_pending_dispatch=skipped_pending_dispatch,
        skipped_active_thread=skipped_active_thread,
        skipped_unstructured=skipped_unstructured,
        replied_tombstone=replied_tombstone_candidates,
        archive_conflicts=archive_conflicts,
        duration_ms=duration_ms,
    )
    return {
        "protocol_version": 2,
        "actor": actor_name,
        "dry_run": dry_run,
        "count": len(moved),
        "skipped_waiting_on_darrin": skipped_waiting,
        "skipped_pre_staged_pending_trigger": skipped_pre_staged,
        "skipped_pending_dispatch": skipped_pending_dispatch,
        "skipped_active_thread": skipped_active_thread,
        "skipped_unstructured": skipped_unstructured,
        "replied_tombstone": replied_tombstone_candidates,
        "archive_conflicts": archive_conflicts,
        "inbox_summary": sorted(inbox_summary.values(), key=lambda item: item["path"].lower()),
        "moved": moved,
    }


def archive_selected_alert(path_value: str, actor: str = "codex", dry_run: bool = False) -> dict[str, Any]:
    msg = find_loaded_message(path_value)
    if is_pre_staged_pending_trigger(msg):
        raise ValueError("Pre-staged pending-trigger messages cannot be deleted; promote or archive them by protocol.")
    archive_dir = CODEX_ARCHIVE / "Deleted Alerts" / datetime.now().strftime("%Y%m%d")
    destination = unique_destination(archive_dir / msg.path.name)
    read_record = set_message_read_state(msg.path, msg.message_id, msg.body, READ_STATE, actor=actor)
    record = {
        "actor": actor.strip() or "codex",
        "dry_run": dry_run,
        "message_id": msg.message_id,
        "thread_id": msg.stable_thread,
        "from": msg.from_agent,
        "to": msg.to_agent,
        "source": str(msg.path),
        "destination": str(destination),
        "read_record": read_record,
    }
    if not dry_run:
        archive_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(msg.path), str(destination))
    return record


def clear_diagnostic_reports(actor: str = "codex", dry_run: bool = True) -> dict[str, Any]:
    archive_root = CODEX_ARCHIVE / "Deleted Diagnostics" / datetime.now().strftime("%Y%m%d")
    moved: list[dict[str, str]] = []
    skipped = {"missing_dir": 0, "non_file": 0}
    if not DIAGNOSTICS_DIR.exists():
        skipped["missing_dir"] = 1
        return {"actor": actor.strip() or "codex", "dry_run": dry_run, "count": 0, "moved": moved, "skipped": skipped}
    for path in sorted(DIAGNOSTICS_DIR.iterdir(), key=lambda item: item.name.lower()):
        if not path.is_file():
            skipped["non_file"] += 1
            continue
        destination = unique_destination(archive_root / path.name)
        record = {"source": str(path), "destination": str(destination)}
        if not dry_run:
            archive_root.mkdir(parents=True, exist_ok=True)
            shutil.move(str(path), str(destination))
        moved.append(record)
    return {
        "actor": actor.strip() or "codex",
        "dry_run": dry_run,
        "count": len(moved),
        "moved": moved,
        "skipped": skipped,
    }


def inspector_report_payload() -> dict[str, Any]:
    report: dict[str, Any] = {}
    markdown = ""
    json_exists = INSPECTOR_LATEST_JSON_PATH.exists()
    markdown_exists = INSPECTOR_LATEST_MARKDOWN_PATH.exists()
    max_age_seconds = 10 * 60
    age_seconds = max(0, int(time.time() - INSPECTOR_LATEST_JSON_PATH.stat().st_mtime)) if json_exists else None
    stale = bool(age_seconds is not None and age_seconds > max_age_seconds)
    if json_exists:
        try:
            loaded = json.loads(read_text(INSPECTOR_LATEST_JSON_PATH))
            if isinstance(loaded, dict):
                report = loaded
        except Exception as exc:
            report = {
                "summary": {"overall": "err", "counts": {"pass": 0, "warn": 0, "fail": 1}},
                "findings": [
                    {
                        "status": "fail",
                        "title": "Inspector report unreadable",
                        "summary": str(exc),
                        "check_id": "inspector.report_unreadable",
                        "recommendation": "Run PAH Inspector again from the terminal.",
                        "detail": {"path": str(INSPECTOR_LATEST_JSON_PATH)},
                    }
                ],
            }
    if markdown_exists:
        markdown = read_text(INSPECTOR_LATEST_MARKDOWN_PATH)
    if stale and report:
        report = dict(report)
        findings = list(report.get("findings", []))
        findings.insert(
            0,
            {
                "status": "warn",
                "title": "Inspector report stale",
                "summary": f"Latest Inspector cache is {human_duration(int(age_seconds or 0))} old.",
                "check_id": "inspector.report_stale",
                "recommendation": "Run Inspector now before trusting cached findings.",
                "detail": {
                    "age_seconds": age_seconds,
                    "max_age_seconds": max_age_seconds,
                    "json_path": str(INSPECTOR_LATEST_JSON_PATH),
                },
            },
        )
        summary = dict(report.get("summary", {}))
        counts = dict(summary.get("counts", {}))
        counts["warn"] = int(counts.get("warn", 0) or 0) + 1
        if int(counts.get("fail", 0) or 0) == 0:
            summary["overall"] = "warn"
        summary["counts"] = counts
        report["summary"] = summary
        report["findings"] = findings
    generated = report.get("generated_at") or (
        datetime.fromtimestamp(INSPECTOR_LATEST_JSON_PATH.stat().st_mtime).isoformat(timespec="seconds")
        if json_exists
        else ""
    )
    return {
        "ok": bool(report),
        "generated_at": generated,
        "json_exists": json_exists,
        "markdown_exists": markdown_exists,
        "fresh": not stale,
        "stale": stale,
        "age_seconds": age_seconds,
        "max_age_seconds": max_age_seconds,
        "json_path": str(INSPECTOR_LATEST_JSON_PATH),
        "markdown_path": str(INSPECTOR_LATEST_MARKDOWN_PATH),
        "report": report,
        "markdown": markdown,
    }


def parse_iso_datetime(value: str) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None


def seconds_since_iso(value: str, now: datetime | None = None) -> int:
    parsed = parse_iso_datetime(value)
    if not parsed:
        return 0
    current = now or (datetime.now(parsed.tzinfo) if parsed.tzinfo else datetime.now())
    try:
        delta = current - parsed
    except TypeError:
        delta = datetime.now() - parsed.replace(tzinfo=None)
    return max(0, int(delta.total_seconds()))


def safe_int(value: Any, fallback: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def path_within(root: Path, path: Path) -> bool:
    try:
        resolved_root = root.resolve()
        resolved_path = path.resolve()
        return resolved_path == resolved_root or resolved_root in resolved_path.parents
    except OSError:
        root_text = str(root).lower().rstrip("\\/")
        path_text = str(path).lower().rstrip("\\/")
        return path_text == root_text or path_text.startswith(root_text + "\\") or path_text.startswith(root_text + "/")


def allowed_progress_target_path(path: Path) -> tuple[bool, str]:
    allowed_roots = (PANDA_GALLERY_ROOT, HUB_ROOT, MAILBOX_ROOT)
    if not any(path_within(root, path) for root in allowed_roots):
        return False, "outside_allowed_roots"
    for root in allowed_roots:
        if path_within(root, path):
            try:
                if path.resolve() == root.resolve():
                    return False, "target_is_project_root"
            except OSError:
                if str(path).lower().rstrip("\\/") == str(root).lower().rstrip("\\/"):
                    return False, "target_is_project_root"
    return True, ""


def newest_child_file_evidence(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"path": str(path), "exists": False, "latest_path": "", "latest_mtime": 0.0, "scanned_files": 0}
    if path.is_file():
        stat_result = path.stat()
        return {
            "path": str(path),
            "exists": True,
            "latest_path": str(path),
            "latest_mtime": float(stat_result.st_mtime),
            "scanned_files": 1,
        }
    latest_path = ""
    latest_mtime = 0.0
    scanned = 0
    for root, dirs, files in os.walk(path):
        dirs[:] = [name for name in dirs if name not in PROGRESS_MONITOR_IGNORE_DIRS]
        for name in files:
            candidate = Path(root) / name
            try:
                stat_result = candidate.stat()
            except OSError:
                continue
            scanned += 1
            if stat_result.st_mtime > latest_mtime:
                latest_mtime = float(stat_result.st_mtime)
                latest_path = str(candidate)
    return {
        "path": str(path),
        "exists": True,
        "latest_path": latest_path,
        "latest_mtime": latest_mtime,
        "scanned_files": scanned,
    }


def mtime_iso(timestamp: float) -> str:
    if not timestamp:
        return ""
    return datetime.fromtimestamp(timestamp).astimezone().isoformat(timespec="seconds")


def cc_active_dispatch_progress(now: datetime | None = None) -> dict[str, Any]:
    current = now or datetime.now().astimezone()
    mailbox_evidence = newest_child_file_evidence(CC_MAILBOX_ROOT)
    mailbox_latest_mtime = float(mailbox_evidence.get("latest_mtime", 0.0) or 0.0)
    mailbox_evidence.update(
        {
            "latest_mtime_iso": mtime_iso(mailbox_latest_mtime),
            "latest_age_seconds": max(0, int(current.timestamp() - mailbox_latest_mtime)) if mailbox_latest_mtime else None,
        }
    )
    if not CC_ACTIVE_DISPATCH_PATH.exists():
        return {
            "id": "cc_active_dispatch",
            "agent": "claude-code",
            "label": "CC Progress",
            "severity": "ok",
            "status": "idle",
            "phase": "No active dispatch",
            "evidence_summary": "CC sidecar not present yet.",
            "recommended_action": "Wait - no active CC dispatch sidecar.",
            "sidecar_path": str(CC_ACTIVE_DISPATCH_PATH),
            "issues": [],
            "targets": [],
            "sidecar_exists": False,
            "checked_at": current.isoformat(timespec="seconds"),
            "mailbox_evidence": mailbox_evidence,
        }
    raw = read_json(CC_ACTIVE_DISPATCH_PATH, {})
    sidecar_stat = CC_ACTIVE_DISPATCH_PATH.stat()
    sidecar_age = max(0, int(current.timestamp() - sidecar_stat.st_mtime))
    if not isinstance(raw, dict) or not raw:
        return {
            "id": "cc_active_dispatch",
            "agent": "claude-code",
            "label": "CC Progress",
            "severity": "warn",
            "status": "invalid",
            "phase": "Invalid sidecar",
            "evidence_summary": "active_dispatch.json could not be parsed as an object.",
            "recommended_action": "Fix CC sidecar JSON.",
            "sidecar_path": str(CC_ACTIVE_DISPATCH_PATH),
            "issues": ["invalid_json_object"],
            "targets": [],
            "sidecar_exists": True,
            "sidecar_age_seconds": sidecar_age,
            "sidecar_mtime_iso": mtime_iso(float(sidecar_stat.st_mtime)),
            "checked_at": current.isoformat(timespec="seconds"),
            "mailbox_evidence": mailbox_evidence,
        }

    status_name = str(raw.get("status", "active")).strip().lower() or "active"
    phase = compact(str(raw.get("phase") or raw.get("dispatch_id") or "CC active dispatch"), 80)
    warn_minutes = safe_int(raw.get("stale_warn_minutes"), DEFAULT_PROGRESS_WARN_MINUTES)
    error_minutes = safe_int(raw.get("stale_error_minutes"), DEFAULT_PROGRESS_ERROR_MINUTES)
    if status_name == "heavy_write":
        warn_minutes *= 2
        error_minutes *= 2
    issues: list[str] = []
    if status_name not in PROGRESS_MONITOR_STATUSES:
        issues.append("invalid_status")
    target_values = raw.get("expected_target_paths", [])
    if isinstance(target_values, str):
        target_values = [target_values]
    if not isinstance(target_values, list):
        target_values = []
        issues.append("expected_target_paths_not_list")

    targets: list[dict[str, Any]] = []
    newest_mtime = 0.0
    newest_path = ""
    for value in target_values:
        target = Path(str(value))
        allowed, reason = allowed_progress_target_path(target)
        evidence = newest_child_file_evidence(target) if allowed else {
            "path": str(target),
            "exists": target.exists(),
            "latest_path": "",
            "latest_mtime": 0.0,
            "scanned_files": 0,
        }
        evidence["allowed"] = allowed
        evidence["invalid_reason"] = reason
        latest_mtime = float(evidence.get("latest_mtime", 0.0) or 0.0)
        evidence["latest_mtime_iso"] = mtime_iso(latest_mtime)
        evidence["latest_age_seconds"] = max(0, int(current.timestamp() - latest_mtime)) if latest_mtime else None
        targets.append(evidence)
        if not allowed:
            issues.append(f"unsafe_target:{reason}")
        elif not evidence.get("exists"):
            issues.append("missing_target")
        elif float(evidence.get("latest_mtime", 0.0) or 0.0) > newest_mtime:
            newest_mtime = float(evidence.get("latest_mtime", 0.0) or 0.0)
            newest_path = str(evidence.get("latest_path", ""))
    if status_name in {"active", "heavy_write"} and not targets:
        issues.append("missing_targets")
    human_loop_evidence: dict[str, Any] = {}
    if status_name == "ready_for_human_loop":
        evidence_path = str(raw.get("human_loop_evidence_path") or raw.get("approval_evidence_path") or "").strip()
        if evidence_path:
            evidence_target = Path(evidence_path)
            allowed, reason = allowed_progress_target_path(evidence_target)
            human_loop_evidence = {
                "path": str(evidence_target),
                "exists": evidence_target.exists(),
                "allowed": allowed,
                "invalid_reason": reason,
            }
            if not allowed:
                issues.append(f"unsafe_human_loop_evidence:{reason}")
            elif not evidence_target.exists():
                issues.append("missing_human_loop_evidence")
        else:
            issues.append("missing_human_loop_evidence")

    started_age = seconds_since_iso(str(raw.get("started_at", "")), current)
    updated_age = seconds_since_iso(str(raw.get("updated_at", "")), current)
    evidence_age = max(0, int(current.timestamp() - newest_mtime)) if newest_mtime else max(started_age, updated_age, sidecar_age)

    severity = "ok"
    recommended_action = "Wait - within threshold."
    evidence_summary = "No disk target evidence yet."
    if newest_path:
        evidence_summary = f"Last file evidence {human_duration(evidence_age)} ago: {compact(newest_path, 72)}"
    elif status_name in {"active", "heavy_write"}:
        evidence_summary = f"No target file evidence for {human_duration(evidence_age)}."

    if status_name in {"paused", "blocked"}:
        severity = "warn"
        recommended_action = "Review blocker or pause reason."
        evidence_summary = compact(str(raw.get("paused_reason") or raw.get("last_known_blocker") or f"CC state is {status_name}."), 110)
    elif status_name in {"complete", "abandoned"}:
        severity = "ok"
        recommended_action = "No action - dispatch is not active."
        evidence_summary = f"CC sidecar status is {status_name}."
    elif status_name == "ready_for_human_loop":
        if issues:
            severity = "warn"
            recommended_action = "Fix CC human-loop evidence before trusting wait state."
            evidence_summary = f"Human-loop sidecar issue: {', '.join(sorted(set(issues)))[:120]}"
        else:
            severity = "ok"
            recommended_action = "Wait - human-loop decision pending; do not interrupt for stale file mtimes."
            evidence_summary = compact(
                str(
                    raw.get("human_loop_reason")
                    or raw.get("last_known_blocker")
                    or "CC is waiting for Darrin's commit/go/ack word."
                ),
                110,
            )
    elif issues:
        severity = "warn"
        recommended_action = "Fix CC sidecar before trusting progress status."
        evidence_summary = f"Sidecar issue: {', '.join(sorted(set(issues)))[:120]}"
    elif status_name == "compose":
        evidence_age = updated_age or sidecar_age
        evidence_summary = f"Compose state for {human_duration(evidence_age)}."
        if evidence_age >= COMPOSE_STATE_MAX_SECONDS:
            severity = "err"
            recommended_action = "Interrupt CC: compose state exceeded 20 minutes."
        else:
            recommended_action = "Wait - CC is composing within cap."
    elif evidence_age >= error_minutes * 60:
        severity = "err"
        recommended_action = "Interrupt CC: ask current tool state, last completed file, blocker."
    elif evidence_age >= warn_minutes * 60:
        severity = "warn"
        recommended_action = "Review CC progress when convenient."

    return {
        "id": "cc_active_dispatch",
        "agent": "claude-code",
        "label": "CC Progress",
        "severity": severity,
        "status": status_name,
        "dispatch_id": str(raw.get("dispatch_id", "")),
        "thread_id": str(raw.get("thread_id", "")),
        "phase": phase,
        "evidence_summary": evidence_summary,
        "recommended_action": recommended_action,
        "sidecar_path": str(CC_ACTIVE_DISPATCH_PATH),
        "sidecar_exists": True,
        "sidecar_age_seconds": sidecar_age,
        "sidecar_mtime_iso": mtime_iso(float(sidecar_stat.st_mtime)),
        "checked_at": current.isoformat(timespec="seconds"),
        "started_age_seconds": started_age,
        "updated_age_seconds": updated_age,
        "evidence_age_seconds": evidence_age,
        "latest_disk_write_path": newest_path,
        "latest_disk_write_iso": mtime_iso(newest_mtime),
        "latest_disk_write_age_seconds": max(0, int(current.timestamp() - newest_mtime)) if newest_mtime else None,
        "scanned_files": sum(int(target.get("scanned_files", 0) or 0) for target in targets),
        "warn_minutes": warn_minutes,
        "error_minutes": error_minutes,
        "targets": targets,
        "human_loop_evidence": human_loop_evidence,
        "mailbox_evidence": mailbox_evidence,
        "issues": sorted(set(issues)),
        "raw_status": raw,
    }


def cc_activity_payload() -> dict[str, Any]:
    card = cc_active_dispatch_progress()
    return {
        "ok": True,
        "checked_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "card": card,
    }


def codex_mailbox_sla_progress(messages: list[Message], read_state_data: dict[str, Any]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    now_ts = time.time()
    for msg in messages:
        if msg.to_agent != "codex" or not message_in_agent_inbox(msg, "codex"):
            continue
        read_status = message_read_status(msg.path, msg.message_id, msg.body, read_state_data)
        if not read_status["unread"]:
            continue
        age = max(0, int(now_ts - msg.modified))
        urgent = is_urgent_codex_request_message(msg)
        sla = MAILBOX_SLA_URGENT_SECONDS if urgent else MAILBOX_SLA_NORMAL_SECONDS
        breached = age >= sla
        rows.append(
            {
                "message_id": msg.message_id,
                "thread_id": msg.stable_thread,
                "title": msg.title,
                "path": str(msg.path),
                "age_seconds": age,
                "sla_seconds": sla,
                "urgent": urgent,
                "breached": breached,
            }
        )
    urgent_breached = sum(1 for row in rows if row["urgent"] and row["breached"])
    normal_breached = sum(1 for row in rows if not row["urgent"] and row["breached"])
    severity = "err" if urgent_breached else "warn" if normal_breached else "ok"
    oldest = max((row["age_seconds"] for row in rows), default=0)
    if urgent_breached:
        action = "Read urgent Codex mail now."
    elif normal_breached:
        action = "Review Codex mailbox SLA breach."
    else:
        action = "Wait - Codex mailbox within SLA."
    summary = f"{len(rows)} unread; {urgent_breached} urgent breach / {normal_breached} normal breach"
    return {
        "id": "codex_mailbox_sla",
        "agent": "codex",
        "label": "Codex SLA",
        "severity": severity,
        "status": "active" if rows else "idle",
        "phase": "Mailbox pickup",
        "evidence_summary": f"{summary}; oldest {human_duration(oldest)}" if rows else "No unread Codex mail.",
        "recommended_action": action,
        "unread": len(rows),
        "urgent_breached": urgent_breached,
        "normal_breached": normal_breached,
        "oldest_unread_seconds": oldest,
        "items": sorted(rows, key=lambda row: (-int(row["breached"]), -int(row["urgent"]), -int(row["age_seconds"])))[:10],
    }


def build_agent_progress_monitor(messages: list[Message], read_state_data: dict[str, Any]) -> dict[str, Any]:
    cards = [cc_active_dispatch_progress(), codex_mailbox_sla_progress(messages, read_state_data)]
    severity = health_level(*(str(card.get("severity", "unknown")).replace("fail", "err") for card in cards))
    return {
        "schema_version": 1,
        "severity": severity,
        "cards": cards,
        "counts": {
            "red": sum(1 for card in cards if card.get("severity") == "err"),
            "yellow": sum(1 for card in cards if card.get("severity") == "warn"),
            "green": sum(1 for card in cards if card.get("severity") == "ok"),
        },
    }


def messages_for_thread(thread_id: str, messages: list[Message] | None = None) -> list[Message]:
    clean_thread = thread_id.strip()
    if not clean_thread:
        raise ValueError("Thread ID is required.")
    matches = [msg for msg in messages or load_messages() if msg.stable_thread == clean_thread]
    if not matches:
        raise KeyError(f"Unknown PAH thread: {clean_thread}")
    return matches


def set_thread_archive_state(
    thread_id: str,
    state_name: str,
    reason: str = "",
    actor: str = "codex",
) -> dict[str, Any]:
    thread_messages = messages_for_thread(thread_id)
    latest = max(thread_messages, key=lambda item: item.modified)
    normalized_state = state_name.strip().lower()
    if normalized_state == "archived":
        if any(msg.is_waiting_on_darrin for msg in thread_messages):
            raise ValueError("Threads waiting on Darrin cannot be archived.")
        return archive_thread(
            latest.stable_thread,
            latest_path=str(latest.path),
            latest_title=latest.title,
            latest_modified=latest.modified,
            reason=reason,
            actor=actor,
        )
    if normalized_state == "active":
        return unarchive_thread(latest.stable_thread, actor=actor, reason=reason)
    raise ValueError(f"Unsupported thread archive state: {state_name}")


def git_status() -> dict[str, str]:
    import subprocess

    try:
        status_result = subprocess.run(
            ["git", "-C", str(PROJECT_ROOT), "status", "--short", "--branch"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        log_result = subprocess.run(
            ["git", "-C", str(PROJECT_ROOT), "log", "-1", "--format=%h%x09%s%x09%cI"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        status_text = status_result.stdout.strip() or status_result.stderr.strip()
        branch = ""
        tracking = ""
        first_line = status_text.splitlines()[0] if status_text else ""
        if first_line.startswith("## "):
            branch_text = first_line[3:].split(" [", 1)[0]
            if "..." in branch_text:
                branch, tracking = branch_text.split("...", 1)
            else:
                branch = branch_text
        commit_parts = (log_result.stdout.strip() if log_result.returncode == 0 else "").split("\t", 2)
        return {
            "ok": str(status_result.returncode == 0),
            "text": status_text,
            "branch": branch,
            "tracking": tracking,
            "last_commit": commit_parts[0] if len(commit_parts) >= 1 else "",
            "last_commit_message": commit_parts[1] if len(commit_parts) >= 2 else "",
            "last_commit_iso": commit_parts[2] if len(commit_parts) >= 3 else "",
        }
    except Exception as exc:  # pragma: no cover - status panel should degrade gently
        return {
            "ok": "False",
            "text": str(exc),
            "branch": "",
            "tracking": "",
            "last_commit": "",
            "last_commit_message": "",
            "last_commit_iso": "",
        }


def cached_expensive_status(name: str, ttl_seconds: float, builder: Any) -> dict[str, Any]:
    now = time.monotonic()
    with EXPENSIVE_STATUS_CACHE_LOCK:
        cached = EXPENSIVE_STATUS_CACHE.get(name)
        if cached and now - cached[0] <= ttl_seconds:
            return dict(cached[1])
    value = builder()
    with EXPENSIVE_STATUS_CACHE_LOCK:
        EXPENSIVE_STATUS_CACHE[name] = (now, dict(value))
    return value


def cached_communication_diagnostics() -> dict[str, Any]:
    return cached_expensive_status(
        "communication_diagnostics",
        EXPENSIVE_STATUS_CACHE_SECONDS,
        lambda: run_communication_diagnostics(write_report=False),
    )


def cached_git_status() -> dict[str, Any]:
    return cached_expensive_status("git_status", GIT_STATUS_CACHE_SECONDS, git_status)


def state() -> dict[str, Any]:
    messages = load_messages()
    read_state_data = load_read_state()
    archive_state_data = load_thread_archive_state()
    decisions = build_decision_queue(messages, write_file=False)
    all_decisions = build_decision_queue(messages, write_file=False, include_inactive=True)
    urgent_codex_requests = urgent_codex_request_rows(messages, read_state_data)
    agent_progress = build_agent_progress_monitor(messages, read_state_data)
    validation = validate_mailbox(messages)
    validation_actionable, validation_inactive = apply_validation_state(validation)
    validation_summary = summarize_validation(validation)
    all_threads = build_threads(messages, read_state_data, archive_state_data)
    thread_focus = build_thread_focus(messages, archive_state_data)
    message_audit = audit_messages_and_thread_states(messages, thread_focus, read_state_data)
    active_threads = [thread for thread in all_threads if not thread.get("archived")]
    archived_threads = [thread for thread in all_threads if thread.get("archived")]
    completed_threads = completed_thread_ids(messages)
    unread_messages = sum(
        1 for msg in messages if message_read_status(msg.path, msg.message_id, msg.body, read_state_data)["unread"]
    )
    diagnostics = cached_communication_diagnostics()
    route_tests = route_test_status(refresh=True)
    work_board = work_board_status()
    approvals = approval_status()
    adapters = adapter_status()
    quarantine = quarantine_status()
    decision_state = decision_state_summary()
    agent_status = build_agent_status(messages, read_state_data, work_board, decisions, thread_focus)
    watcher = build_watcher_status(agent_status, route_tests)
    return {
        "project_root": str(PROJECT_ROOT),
        "mailbox_root": str(MAILBOX_ROOT),
        "panda_gallery_root": str(PANDA_GALLERY_ROOT),
        "decision_queue_path": str(DECISION_QUEUE_PATH),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "counts": {
            "messages": len(messages),
            "unread_messages": unread_messages,
            "threads": len(active_threads),
            "archived_threads": len(archived_threads),
            "decisions": len(decisions),
            "validation_issues": len(validation),
            "actionable_validation_issues": len(validation_actionable),
            "inactive_validation_issues": len(validation_inactive),
            "diagnostic_checks": len(diagnostics["checks"]),
            "route_tests_pending": route_tests["counts"].get("pending_reply", 0),
            "work_items": work_board["counts"]["total"],
            "approval_records": approvals["records"],
            "enabled_adapters": adapters["enabled"],
            "inactive_decisions": max(0, len(all_decisions) - len(decisions)),
            "urgent_codex_requests": len(urgent_codex_requests),
            "agent_progress_red": agent_progress.get("counts", {}).get("red", 0),
            "agent_progress_yellow": agent_progress.get("counts", {}).get("yellow", 0),
        },
        "latest": [message_to_json(msg, read_state_data, completed_threads) for msg in messages[:40]],
        "mailboxes": build_mailbox_overview(messages, read_state_data),
        "agent_mailboxes": build_agent_mailbox_messages(messages, read_state_data),
        "agent_status": agent_status,
        "watcher": watcher,
        "threads": active_threads[:80],
        "archived_threads": archived_threads[:80],
        "thread_focus": thread_focus,
        "urgent_codex_requests": urgent_codex_requests,
        "agent_progress": agent_progress,
        "decisions": decisions,
        "decision_history": [item for item in all_decisions if item.get("decision_state") != ACTIVE_STATE],
        "decision_state": decision_state,
        "validation": validation,
        "validation_actionable": validation_actionable,
        "validation_inactive": validation_inactive,
        "validation_summary": validation_summary,
        "validation_state": validation_state_summary(),
        "read_state": read_state_summary(read_state_data),
        "message_audit": message_audit,
        "thread_archive": thread_archive_summary(archive_state_data),
        "diagnostics": diagnostics,
        "route_tests": route_tests,
        "work_board": work_board,
        "approvals": approvals,
        "adapters": adapters,
        "quarantine": quarantine,
        "notifications": notification_status(),
        "git": cached_git_status(),
    }


def route_id_for_direction(direction: str) -> str:
    lowered = direction.lower()
    if "to claude code" in lowered:
        return "codex_to_claude_code"
    if "claude code" in lowered and "codex" in lowered:
        return "claude_code_to_codex"
    if "codex -> claude" in lowered:
        return "codex_to_claude"
    if "claude -> codex" in lowered:
        return "claude_to_codex"
    return safe_slug(direction).replace("-", "_")


def cockpit_status_from_agent_state(state_name: str) -> str:
    normalized = state_name.lower()
    if normalized in {"active", "needs_wake"}:
        return "active" if normalized == "active" else "warn"
    if normalized in {"recent", "idle"}:
        return "ok" if normalized == "recent" else "idle"
    if normalized in {"waiting", "unknown"}:
        return "warn"
    if normalized == "needs_attention":
        return "err"
    return "idle"


def build_cockpit_routes(status_data: dict[str, Any]) -> list[dict[str, Any]]:
    diagnostics = status_data.get("diagnostics", {})
    check_by_name = {str(item.get("name", "")): item for item in diagnostics.get("checks", [])}
    route_specs = [
        ("codex_to_claude", "Codex -> Claude Desktop", MAILBOX_ROOT, CLAUDE_INBOX, "route:codex_to_claude"),
        ("codex_to_claude_code", "Codex -> Claude Code", MAILBOX_ROOT, CLAUDE_CODE_INBOX, "route:codex_to_claude_code"),
        ("claude_to_codex", "Claude Desktop -> Codex", CLAUDE_INBOX, CODEX_INBOX, "route:claude_to_codex"),
    ]
    rows: list[dict[str, Any]] = []
    now_iso = status_data.get("generated_at", datetime.now().isoformat(timespec="seconds"))
    for route_id, name, source_path, dest_path, check_name in route_specs:
        check = check_by_name.get(check_name, {})
        ok = bool(check.get("ok"))
        rows.append(
            {
                "id": route_id,
                "name": name,
                "source_path": str(source_path),
                "dest_path": str(dest_path),
                "status": "pass" if ok else "failed",
                "hold_reason": "" if ok else str(check.get("detail", "Route check failed")),
                "last_check_iso": now_iso,
                "latency_ms": 0,
            }
        )
    rows.append(
        {
            "id": "watcher",
            "name": "Watcher",
            "source_path": str(CC_MAILBOX_ROOT),
            "dest_path": str(WATCHER_EVENT_LOG_PATH),
            "status": "held",
            "hold_reason": "Waiting for Darrin standing read permission",
            "last_check_iso": now_iso,
            "latency_ms": None,
        }
    )
    return rows


def summarize_cockpit_routes(routes: list[dict[str, Any]]) -> dict[str, Any]:
    problem_routes = [
        {
            "id": str(route.get("id", "")),
            "name": str(route.get("name", "")),
            "status": str(route.get("status", "")),
            "hold_reason": str(route.get("hold_reason", "")),
        }
        for route in routes
        if str(route.get("status", "")) in {"held", "failed", "untested"}
    ]
    counts = {
        "total": len(routes),
        "pass": sum(1 for route in routes if route.get("status") == "pass"),
        "held": sum(1 for route in routes if route.get("status") == "held"),
        "failed": sum(1 for route in routes if route.get("status") == "failed"),
        "untested": sum(1 for route in routes if route.get("status") == "untested"),
    }
    if counts["failed"]:
        severity = "err"
    elif counts["held"] or counts["untested"]:
        severity = "warn"
    else:
        severity = "ok"
    if counts["held"] or counts["failed"] or counts["untested"]:
        label = f"{counts['pass']}/{counts['total']} routes pass"
        details = []
        if counts["held"]:
            details.append(f"{counts['held']} held")
        if counts["failed"]:
            details.append(f"{counts['failed']} failed")
        if counts["untested"]:
            details.append(f"{counts['untested']} untested")
        label = f"{label}; {', '.join(details)}"
    else:
        label = f"{counts['pass']}/{counts['total']} routes pass"
    return {**counts, "label": label, "severity": severity, "problem_routes": problem_routes}


def health_level(*levels: str) -> str:
    rank = {"unknown": 0, "ok": 1, "warn": 2, "err": 3}
    clean = [level if level in rank else "unknown" for level in levels]
    return max(clean or ["unknown"], key=lambda level: rank[level])


def health_component(level: str, label: str, detail: str, **extra: Any) -> dict[str, Any]:
    normalized = level if level in {"ok", "warn", "err", "unknown"} else "unknown"
    return {"level": normalized, "label": label, "detail": detail, **extra}


def inspector_freshness_component() -> dict[str, Any]:
    max_age_seconds = 10 * 60
    if not INSPECTOR_LATEST_JSON_PATH.exists():
        return health_component(
            "warn",
            "Inspector freshness",
            "No Inspector report has been generated yet.",
            latest_json_path=str(INSPECTOR_LATEST_JSON_PATH),
            age_seconds=None,
            max_age_seconds=max_age_seconds,
            run_now_hint="Run CODEX_pah_inspector.py or use the PAH Inspector action before trusting cached findings.",
        )
    age_seconds = max(0, int(time.time() - INSPECTOR_LATEST_JSON_PATH.stat().st_mtime))
    return health_component(
        "ok" if age_seconds <= max_age_seconds else "warn",
        "Inspector freshness",
        f"Latest Inspector report is {human_duration(age_seconds)} old.",
        latest_json_path=str(INSPECTOR_LATEST_JSON_PATH),
        latest_markdown_path=str(INSPECTOR_LATEST_MARKDOWN_PATH),
        age_seconds=age_seconds,
        max_age_seconds=max_age_seconds,
        stale=age_seconds > max_age_seconds,
        run_now_hint="Run CODEX_pah_inspector.py or use the PAH Inspector action before trusting cached findings.",
    )


def periodic_health_monitor_summary() -> dict[str, Any]:
    report = read_json(PERIODIC_HEALTH_LATEST_PATH, {})
    if not report:
        return health_component(
            "unknown",
            "Periodic monitor not reported",
            "No latest periodic health report is available yet.",
            path=str(PERIODIC_HEALTH_LATEST_PATH),
        )
    checks = report.get("checks", {})
    failed = [
        name
        for name, check in checks.items()
        if isinstance(check, dict) and not bool(check.get("ok"))
    ]
    level = "err" if failed else "ok" if report.get("ok") else "warn"
    generated_at = str(report.get("generated_at", ""))
    schedule = report.get("schedule", {}) if isinstance(report.get("schedule", {}), dict) else {}
    detail = "Periodic monitor passed." if level == "ok" else f"Periodic monitor needs attention: {', '.join(failed) or 'report warning'}."
    return health_component(
        level,
        "Periodic monitor",
        detail,
        generated_at=generated_at,
        next_run_after=str(schedule.get("next_run_after", "")),
        schedule=schedule,
        path=str(PERIODIC_HEALTH_LATEST_PATH),
        failed_checks=failed,
        duration_ms=report.get("duration_ms", 0),
        archive_read_sweep=checks.get("archive_read_sweep", {}),
        status_summary=report.get("status_summary", {}),
        warnings=report.get("warnings", []),
    )


def health_payload_from_cockpit(cockpit: dict[str, Any]) -> dict[str, Any]:
    state_data = cockpit.get("cockpit_state", {})
    counts = state_data.get("counts", {})
    diagnostics = cockpit.get("diagnostics", {})
    agent_progress = cockpit.get("agent_progress", {})
    routes_summary = state_data.get("routes_summary", {})
    git = cockpit.get("git", {})
    generated_at = str(cockpit.get("generated_at", datetime.now().isoformat(timespec="seconds")))
    routes_level = str(routes_summary.get("severity", "unknown"))
    stale_unread = int(counts.get("stale_unread", 0) or 0)
    urgent_codex = int(counts.get("urgent_codex_requests", 0) or 0)
    open_on_darrin = int(counts.get("open_on_darrin", 0) or 0)
    open_on_agent = int(counts.get("open_on_agent", 0) or 0)
    owner_unknown = int(counts.get("owner_unknown", 0) or 0)
    unanswered_total = open_on_darrin + open_on_agent + owner_unknown
    failed_checks = int(diagnostics.get("checks_fail", 0) or 0)
    warn_checks = int(diagnostics.get("checks_warn", 0) or 0)
    actionable_validation = int(diagnostics.get("actionable_validation_issues", 0) or 0)
    monitor = periodic_health_monitor_summary()
    progress_counts = agent_progress.get("counts", {}) if isinstance(agent_progress, dict) else {}
    progress_level = str(agent_progress.get("severity", "unknown")) if isinstance(agent_progress, dict) else "unknown"
    progress_cards = agent_progress.get("cards", []) if isinstance(agent_progress, dict) else []
    git_clean = bool(git.get("clean"))
    git_status = str(git.get("status_label") or "")

    components = {
        "server": health_component("ok", "Server API online", f"PAH API generated this payload at {generated_at}."),
        "routes": health_component(
            routes_level,
            "Mailbox routes",
            str(routes_summary.get("label", "No route summary.")),
            counts=routes_summary,
            problem_routes=routes_summary.get("problem_routes", []),
        ),
        "inspector": inspector_freshness_component(),
        "mailboxes": health_component(
            "warn" if owner_unknown else "ok",
            "Mailboxes",
            f"{owner_unknown} owner-unknown thread(s); {stale_unread} stale unread message(s).",
            owner_unknown=owner_unknown,
            stale_unread=stale_unread,
        ),
        "unanswered": health_component(
            "err" if owner_unknown else "warn" if unanswered_total else "ok",
            "Unanswered work",
            f"{open_on_darrin} open on Darrin; {open_on_agent} open on agents; {owner_unknown} owner unknown.",
            open_on_darrin=open_on_darrin,
            open_on_agent=open_on_agent,
            owner_unknown=owner_unknown,
            total=unanswered_total,
        ),
        "urgent_codex": health_component(
            "err" if urgent_codex else "ok",
            "Urgent Codex requests",
            f"{urgent_codex} urgent request(s) flagged for Codex.",
            urgent_codex_requests=urgent_codex,
        ),
        "agent_progress": health_component(
            progress_level if progress_level in {"ok", "warn", "err", "unknown"} else "unknown",
            "Agent progress",
            f"{progress_counts.get('red', 0)} red; {progress_counts.get('yellow', 0)} yellow progress monitor card(s).",
            counts=progress_counts,
            cards=progress_cards,
        ),
        "archive": health_component(
            "ok" if SWEEP_AUDIT_LOG_PATH.exists() else "unknown",
            "Archive sweep",
            "Read-mail sweep audit log is present." if SWEEP_AUDIT_LOG_PATH.exists() else "No sweep audit log has been written yet.",
            audit_log_path=str(SWEEP_AUDIT_LOG_PATH),
        ),
        "interaction_ledger": health_component(
            "ok" if INTERACTION_LEDGER_PATH.exists() else "unknown",
            "Interaction ledger",
            "Append-only PAH interaction ledger is present."
            if INTERACTION_LEDGER_PATH.exists()
            else "No interaction ledger events have been written yet.",
            ledger_path=str(INTERACTION_LEDGER_PATH),
        ),
        "diagnostics": health_component(
            "err" if failed_checks else "warn" if warn_checks or actionable_validation else "ok",
            "Diagnostics",
            f"{failed_checks} failed checks; {warn_checks} warnings; {actionable_validation} actionable validation issue(s).",
            failed_checks=failed_checks,
            warn_checks=warn_checks,
            actionable_validation_issues=actionable_validation,
        ),
        "periodic_monitor": monitor,
        "github_backup": health_component(
            "ok" if git_clean else "warn",
            "Git/GitHub backup",
            "Working tree is clean." if git_clean else git_status or "Working tree has uncommitted or unsynced changes.",
            branch=str(git.get("branch", "")),
            tracking=str(git.get("tracking", "")),
            clean=git_clean,
        ),
    }
    overall = health_level(*(str(item.get("level", "unknown")) for item in components.values()))
    return {
        "ok": overall == "ok",
        "schema_version": 1,
        "generated_at": generated_at,
        "overall": overall,
        "summary": "PAH healthy." if overall == "ok" else "PAH needs attention.",
        "components": components,
    }


def health_payload() -> dict[str, Any]:
    return health_payload_from_cockpit(cockpit_payload())


def cockpit_feed_item(row: dict[str, Any]) -> dict[str, Any]:
    is_stale = bool(row.get("stale_unread"))
    is_urgent = bool(row.get("urgent_codex_request"))
    badges = [{"kind": "status", "label": str(label)} for label in row.get("status_badges", [])[:3]]
    if is_urgent:
        badges.insert(0, {"kind": "urgent", "label": "urgent"})
    if is_stale:
        badges.insert(0, {"kind": "wake", "label": "needs wake-up"})
    return {
        "id": row.get("message_id") or row.get("name", ""),
        "thread_id": row.get("thread_id") or row.get("message_id") or row.get("name", ""),
        "title": row.get("title", "Untitled"),
        "sub": f"{row.get('from_agent') or '?'} -> {row.get('to_agent') or '?'} / {row.get('thread_id') or row.get('direction')}",
        "time_iso": row.get("modified", ""),
        "route_id": route_id_for_direction(str(row.get("direction", ""))),
        "from_agents": [row.get("from_agent", "")],
        "to_agents": [row.get("to_agent", "")],
        "unread": bool(row.get("unread")),
        "age_seconds": int(row.get("age_seconds", 0) or 0),
        "stale_unread": is_stale,
        "urgent_codex_request": is_urgent,
        "wake_candidate_agent": row.get("wake_candidate_agent", ""),
        "badges": badges,
        "message_path": row.get("path", ""),
        "summary": row.get("summary", ""),
    }


def cockpit_agent_name(agent_id: str, agents: list[dict[str, Any]]) -> str:
    for agent in agents:
        if agent.get("id") == agent_id:
            return str(agent.get("display_name") or agent_id)
    return agent_id or "agent"


def cockpit_selected_thread(
    status_data: dict[str, Any],
    feed: list[dict[str, Any]],
    agents: list[dict[str, Any]],
    wake_candidates: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    decisions = status_data.get("decisions", [])
    decision = decisions[0] if decisions else {}
    wake_item = (wake_candidates or [None])[0] or {}
    thread_item = feed[0] if feed else {}
    selected = wake_item or thread_item or decision or {}
    title = str(selected.get("title", "No active thread"))
    path_value = str(selected.get("path") or selected.get("message_path") or "")
    thread_id = str(selected.get("thread_id") or selected.get("id") or safe_slug(title))
    route_id = str(selected.get("route_id") or route_id_for_direction(str(selected.get("direction", ""))))
    if wake_item:
        state = "needs_wake"
        owner = cockpit_agent_name(str(wake_item.get("wake_candidate_agent", "")), agents)
        source = "Unread over 60 seconds"
        next_action = f"Wake {owner}"
    elif thread_item:
        state = str(thread_item.get("state") or thread_item.get("kind") or "thread")
        owner = str(thread_item.get("owner_label") or thread_item.get("agent_label") or "")
        source = str(thread_item.get("state_label") or "Thread classifier")
        next_action = str(thread_item.get("primary_action") or "Open message")
    elif decisions:
        state = "waiting_on_darrin"
        owner = "darrin"
        source = "Decision queue"
        next_action = "Review standing read scope" if "watcher" in title.lower() else "Review decision"
    else:
        state = "active"
        owner = "codex"
        source = "Latest mailbox"
        next_action = "Open message"
    return {
        "id": thread_id,
        "title": title,
        "state": state,
        "owner": owner,
        "source": source,
        "route_id": route_id,
        "next_action": next_action,
        "facts": [
            {
                "label": "State",
                "value": "Needs wake-up" if wake_item else source if thread_item else "Waiting on Darrin" if decisions else "Active",
            },
            {"label": "Next action", "value": next_action},
            {"label": "Owner", "value": owner or "Unassigned"},
            {"label": "Writes", "value": "None from this screen"},
        ],
        "cards": [
            {
                "title": "Unread alert" if wake_item else "Current gate" if decisions else "Latest message",
                "kind": "text",
                "body": str(selected.get("summary", "No summary available.")),
            },
            {
                "title": "Read-only v1",
                "kind": "text",
                "body": "Compose, send, permission grants, and watcher startup are disabled in this cockpit slice.",
            },
            {
                "title": "Safety boundary",
                "kind": "text",
                "body": "Standing permissions must show scope before any future grant can be recorded.",
            },
        ],
        "primary_message_path": path_value,
    }


def cockpit_decisions(status_data: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, item in enumerate(status_data.get("decisions", [])[:6]):
        title = str(item.get("title", "Decision needed"))
        requires_scope = "watcher" in title.lower() or "read" in str(item.get("summary", "")).lower()
        rows.append(
            {
                "id": safe_slug(title) or f"decision-{index + 1}",
                "title": title,
                "sub": compact(str(item.get("summary", "")), 120),
                "badge": "needed",
                "severity": "warn",
                "blocked_by": [],
                "path": str(item.get("path", "")),
                "actions": [
                    {
                        "id": "review_scope" if requires_scope else "open_message",
                        "label": "Review scope" if requires_scope else "Open",
                        "kind": "confirm_required" if requires_scope else "secondary",
                        "enabled": True,
                        "requires_confirm": requires_scope,
                    },
                    {
                        "id": "defer",
                        "label": "Defer",
                        "kind": "secondary",
                        "enabled": True,
                        "requires_confirm": False,
                    },
                ],
                "scope_text": {
                    "path": str(CC_MAILBOX_ROOT),
                    "read_frequency": "Not started in read-only v1.",
                    "writes": f"Future watcher logs would stay under {HUB_ROOT}.",
                    "will_not_do": [
                        "No headless wake",
                        "No window automation",
                        "No Panda Gallery writes outside approved coordination messages",
                    ],
                }
                if requires_scope
                else {},
            }
        )
    if not rows:
        rows.append(
            {
                "id": "no-decisions",
                "title": "No Darrin decisions",
                "sub": "Decision queue is clear.",
                "badge": "clear",
                "severity": "ok",
                "blocked_by": [],
                "path": "",
                "actions": [],
                "scope_text": {},
            }
        )
    return rows


def cockpit_agents(status_data: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for agent in status_data.get("agent_status", []):
        state_name = str(agent.get("state", "idle"))
        unread_count = int(agent.get("unread", 0) or 0)
        waiting_count = int(agent.get("waiting", 0) or 0)
        inbound_count = int(agent.get("inbound", 0) or 0)
        outbound_count = int(agent.get("outbound", 0) or 0)
        if agent.get("id") == "darrin":
            count_value = int(status_data.get("thread_focus", {}).get("counts", {}).get("open_on_darrin", 0) or 0)
            count_label = "thread" if count_value == 1 else "threads"
        elif waiting_count:
            count_value = waiting_count
            count_label = "queued"
        else:
            count_value = unread_count
            count_label = "unread"
        rows.append(
            {
                "id": agent.get("id", ""),
                "code": agent.get("initials", ""),
                "display_name": agent.get("label", ""),
                "status": cockpit_status_from_agent_state(state_name),
                "status_label": str(agent.get("state_label", state_name)),
                "summary_line": str((agent.get("current_work") or {}).get("title") or agent.get("status_note", "")),
                "count_value": count_value,
                "count_label": count_label,
                "unread_count": unread_count,
                "waiting_count": waiting_count,
                "inbound_count": inbound_count,
                "outbound_count": outbound_count,
                "meter_pct": min(100, max(10, int(count_value or 1) * 16)),
                "meter_color": "warn" if state_name in {"waiting", "needs_wake"} else "err" if state_name == "needs_attention" else "ok",
                "last_activity_iso": str((agent.get("current_work") or {}).get("modified", "")),
                "pulse": state_name == "active",
            }
        )
    return rows


def cockpit_action_queue(
    feed: list[dict[str, Any]], decisions: list[dict[str, Any]], agents: list[dict[str, Any]], limit: int = 72
) -> list[dict[str, Any]]:
    wake_rows: list[dict[str, Any]] = []
    decision_rows: list[dict[str, Any]] = []
    unread_rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in feed:
        key = str(item.get("id") or item.get("message_path"))
        if item.get("stale_unread"):
            seen.add(key)
            agent_id = str(item.get("wake_candidate_agent", ""))
            label = cockpit_agent_name(agent_id, agents)
            wake_rows.append(
                {
                    "id": key,
                    "kind": "wake",
                    "severity": "warn",
                    "title": item.get("title", "Unread message"),
                    "summary": f"Unread {item.get('age_seconds', 0)}s. Wake {label}.",
                    "primary_action": f"Wake {label}",
                    "secondary_action": "Mark read",
                    "message_path": item.get("message_path", ""),
                    "thread_id": item.get("thread_id", ""),
                    "wake_line": f"Read {item.get('thread_id') or item.get('id')} and reply to CODEX.",
                }
            )
    for decision in decisions:
        if decision.get("id") == "no-decisions":
            continue
        key = str(decision.get("id"))
        decision_rows.append(
            {
                "id": key,
                "kind": "decision",
                "severity": decision.get("severity", "warn"),
                "title": decision.get("title", "Decision needed"),
                "summary": decision.get("sub", ""),
                "primary_action": "Review",
                "secondary_action": "Defer",
                "message_path": decision.get("path", ""),
                "thread_id": key,
                "wake_line": "",
                "actions": decision.get("actions", []),
                "scope_text": decision.get("scope_text", {}),
                "blocked_by": decision.get("blocked_by", []),
            }
        )
    for item in feed:
        key = str(item.get("id") or item.get("message_path"))
        if key in seen or not item.get("unread"):
            continue
        unread_rows.append(
            {
                "id": key,
                "kind": "unread",
                "severity": "ok",
                "title": item.get("title", "Unread message"),
                "summary": item.get("sub", ""),
                "primary_action": "Open",
                "secondary_action": "Mark read",
                "message_path": item.get("message_path", ""),
                "thread_id": item.get("thread_id", ""),
                "wake_line": "",
            }
        )
        seen.add(key)
    feed_rank: dict[str, int] = {}
    for index, item in enumerate(feed):
        for key in {str(item.get("id") or ""), str(item.get("message_path") or "")}:
            if key:
                feed_rank.setdefault(key, index)

    def sort_key(row: dict[str, Any]) -> tuple[int, int, int, str]:
        kind_rank = {"wake": 0, "decision": 1, "unread": 2}.get(str(row.get("kind", "")), 9)
        severity_rank = {"err": 0, "warn": 1, "ok": 2}.get(str(row.get("severity", "")), 9)
        row_rank = feed_rank.get(str(row.get("id") or row.get("message_path") or ""), len(feed_rank) + 1)
        return (kind_rank, severity_rank, row_rank, str(row.get("title", "")))

    wake_rows.sort(key=sort_key)
    decision_rows.sort(key=sort_key)
    unread_rows.sort(key=sort_key)
    wake_limit = max(0, limit - len(decision_rows))
    unread_limit = max(0, limit - len(decision_rows) - min(len(wake_rows), wake_limit))
    return [*wake_rows[:wake_limit], *decision_rows, *unread_rows[:unread_limit]]


def cockpit_thread_queue(thread_focus: dict[str, Any], limit: int = 80) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for bucket, kind, severity in (
        ("open_on_darrin", "you", "ok"),
        ("open_on_agent", "agent", "ok"),
        ("owner_unknown", "unknown", "warn"),
        ("parked", "parked", "ok"),
        ("closed", "closed", "ok"),
    ):
        for item in thread_focus.get(bucket, []):
            rows.append(
                {
                    "id": item.get("id", ""),
                    "kind": kind,
                    "state": item.get("state", bucket),
                    "state_label": item.get("state_label", ""),
                    "severity": severity,
                    "title": item.get("title", "Untitled thread"),
                    "summary": item.get("summary", ""),
                    "primary_action": item.get("primary_action", "Open message"),
                    "secondary_action": item.get("secondary_action", "Browse thread"),
                    "message_path": item.get("message_path", ""),
                    "thread_id": item.get("thread_id", item.get("id", "")),
                    "agent_label": item.get("agent_label", ""),
                    "owner_label": item.get("owner_label", ""),
                    "age_seconds": item.get("age_seconds", 0),
                    "message_count": item.get("count", 1),
                    "requires_darrin_decision": item.get("requires_darrin_decision", False),
                    "wake_line": item.get("wake_line", ""),
                }
            )
    return rows[:limit]


def cockpit_payload() -> dict[str, Any]:
    status_data = state()
    generated_at = str(status_data.get("generated_at", datetime.now().isoformat(timespec="seconds")))
    routes = build_cockpit_routes(status_data)
    route_summary = summarize_cockpit_routes(routes)
    feed = [cockpit_feed_item(row) for row in status_data.get("latest", [])[:24]]
    thread_focus = status_data.get("thread_focus", {})
    thread_counts = thread_focus.get("counts", {})
    urgent_codex_requests = list(status_data.get("urgent_codex_requests", []))
    agent_progress = status_data.get("agent_progress", {})
    decisions = cockpit_decisions(status_data)
    agents = cockpit_agents(status_data)
    wake_candidates = [item for item in feed if item.get("stale_unread")]
    action_queue = [*urgent_codex_requests, *cockpit_thread_queue(thread_focus)]
    selected_thread = cockpit_selected_thread(status_data, action_queue or feed, agents, [])
    diagnostics = status_data.get("diagnostics", {})
    diagnostic_checks = diagnostics.get("checks", [])
    relay_health_check = next((check for check in diagnostic_checks if check.get("name") == "relay_health"), {})
    relay_health_payload = relay_health_check.get("relay_health", {}) if isinstance(relay_health_check, dict) else {}
    validation_summary = status_data.get("validation_summary", {})
    git = status_data.get("git", {})
    git_text = str(git.get("text", ""))
    git_lines = [line for line in git_text.splitlines() if line.strip()]
    git_branch = str(git.get("branch") or "main")
    git_tracking = str(git.get("tracking") or "origin/main")
    git_clean = len(git_lines) == 1 and git_lines[0].startswith("## ")
    git_synced = git_clean and "[" not in git_lines[0]
    stale_threshold_label = f"{STALE_UNREAD_SECONDS}s"
    primary_wake_item = urgent_codex_requests[0] if urgent_codex_requests else (wake_candidates[0] if wake_candidates else {})
    urgent_breakthrough_line = str(primary_wake_item.get("wake_line", "")) if primary_wake_item else ""
    payload = {
        "schema_version": 1,
        "generated_at": generated_at,
        "cockpit_state": {
            "as_of_iso": generated_at,
            "mode": "live",
            "read_only": True,
            "active_filter": "needs_action",
            "density": "medium",
            "search_query": "",
            "stale_unread_threshold_seconds": STALE_UNREAD_SECONDS,
            "routes_summary": route_summary,
            "counts": {
                "messages": status_data.get("counts", {}).get("messages", 0),
                "unread": status_data.get("counts", {}).get("unread_messages", 0),
                "stale_unread": len(wake_candidates),
                "decisions_needed": thread_counts.get("open_on_darrin", 0),
                "open_on_darrin": thread_counts.get("open_on_darrin", 0),
                "open_on_agent": thread_counts.get("open_on_agent", 0),
                "owner_unknown": thread_counts.get("owner_unknown", 0),
                "parked": thread_counts.get("parked", 0),
                "closed": thread_counts.get("closed", 0),
                "threads_all": thread_counts.get("all", 0),
                "actionable_checks": status_data.get("counts", {}).get("actionable_validation_issues", 0),
                "urgent_codex_requests": status_data.get("counts", {}).get("urgent_codex_requests", 0),
                "agent_progress_red": status_data.get("counts", {}).get("agent_progress_red", 0),
                "agent_progress_yellow": status_data.get("counts", {}).get("agent_progress_yellow", 0),
            },
        },
        "thread_focus": thread_focus,
        "urgent_codex_requests": urgent_codex_requests,
        "agent_progress": agent_progress,
        "simple_mail": {
            "latest": status_data.get("latest", [])[:120],
            "mailboxes": status_data.get("mailboxes", []),
            "agent_mailboxes": status_data.get("agent_mailboxes", {}),
        },
        "mailbox_messages": status_data.get("agent_mailboxes", {}),
        "agents": agents,
        "action_queue": action_queue,
        "wake_candidates": wake_candidates,
        "feed": feed,
        "selected_thread": selected_thread,
        "decisions": decisions,
        "routes": routes,
        "wake": {
            "target_agent": "codex" if urgent_codex_requests else (wake_candidates[0].get("wake_candidate_agent", "") if wake_candidates else ""),
            "line": urgent_breakthrough_line,
            "route_status": "urgent_codex_request" if urgent_codex_requests else ("wake_candidate" if wake_candidates else ""),
            "last_copy_iso": "",
            "direct_wake_supported": False,
            "safety_label": f"{len(urgent_codex_requests)} urgent Codex request(s). Open now." if urgent_codex_requests else (f"{len(wake_candidates)} unread over {stale_threshold_label}. Copy line only." if wake_candidates else "Copy line only; Darrin pastes into Claude Code."),
        },
        "urgent_breakthrough": {
            "active": bool(urgent_codex_requests),
            "count": len(urgent_codex_requests),
            "line": urgent_breakthrough_line,
            "delivery_mode": "always-on log channel plus dashboard focus",
        },
        "message_audit": status_data.get("message_audit", {}),
        "interaction_ledger": interaction_ledger_summary(),
        "diagnostics": {
            "ok": bool(diagnostics.get("ok")),
            "checks_total": len(diagnostic_checks),
            "checks_pass": sum(1 for check in diagnostic_checks if check.get("ok")),
            "checks_warn": sum(1 for check in diagnostic_checks if not check.get("ok") and check.get("severity") == "warning"),
            "checks_fail": sum(1 for check in diagnostic_checks if not check.get("ok") and check.get("severity") != "warning"),
            "actionable_validation_issues": validation_summary.get("actionable", 0),
            "last_run_iso": generated_at,
            "thread_classifier": thread_focus.get("diagnostics", {}),
            "relay_health": {
                "ok": bool(relay_health_check.get("ok")) if relay_health_check else False,
                "severity": str(relay_health_check.get("severity", "warning")) if relay_health_check else "warning",
                "status_label": str(relay_health_check.get("detail", "Relay health checker has not run.")),
                "counts": relay_health_payload.get("counts", {}) if isinstance(relay_health_payload, dict) else {},
                "cache": relay_health_payload.get("cache", {}) if isinstance(relay_health_payload, dict) else {},
            },
        },
        "git": {
            "branch": git_branch,
            "tracking": git_tracking,
            "clean": git_clean,
            "status_label": f"{git_branch} synced with {git_tracking}" if git_synced else git_text,
            "last_commit": str(git.get("last_commit", "")),
            "last_commit_message": str(git.get("last_commit_message", "")),
            "last_commit_iso": str(git.get("last_commit_iso", "")),
        },
        "read_only_actions": [
            {"id": "refresh", "label": "Refresh", "enabled": True, "destructive": False},
            {"id": "validate", "label": "Validate", "enabled": True, "destructive": False},
            {"id": "backup", "label": "Backup", "enabled": True, "destructive": False},
            {"id": "compose", "label": "Compose", "enabled": False, "destructive": False, "reason": "disabled in read-only v1"},
            {"id": "send", "label": "Send", "enabled": False, "destructive": False, "reason": "no draft staged in read-only v1"},
        ],
    }
    payload["health"] = health_payload_from_cockpit(payload)
    return payload


def human_duration(seconds: int) -> str:
    seconds = max(0, int(seconds or 0))
    if seconds < 60:
        return f"{seconds}s"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes}m"
    hours = minutes // 60
    if hours < 24:
        return f"{hours}h {minutes % 60}m"
    days = hours // 24
    return f"{days}d {hours % 24}h"


def tray_status_payload(cockpit: dict[str, Any] | None = None) -> dict[str, Any]:
    cockpit = cockpit or cockpit_payload()
    state = cockpit.get("cockpit_state", {})
    counts = state.get("counts", {})
    diagnostics = cockpit.get("diagnostics", {})
    routes_summary = state.get("routes_summary", {})
    wake_candidates = cockpit.get("wake_candidates", [])
    decisions = int(counts.get("decisions_needed", 0) or 0)
    urgent_codex = int(counts.get("urgent_codex_requests", 0) or 0)
    stale = int(counts.get("stale_unread", 0) or 0)
    unread = int(counts.get("unread", 0) or 0)
    diag_problems = int(diagnostics.get("checks_warn", 0) or 0) + int(diagnostics.get("checks_fail", 0) or 0)
    oldest = max((int(item.get("age_seconds", 0) or 0) for item in wake_candidates), default=0)
    agents = cockpit.get("agents", [])
    target_counts: dict[str, int] = {}
    for item in wake_candidates:
        target = cockpit_agent_name(str(item.get("wake_candidate_agent", "")), agents)
        target_counts[target] = target_counts.get(target, 0) + 1

    if urgent_codex:
        level = "urgent"
        title = f"{urgent_codex} URGENT Codex request{'s' if urgent_codex != 1 else ''}"
        body = "Open PAH now; CC/CD flagged work that should interrupt lower-priority Codex tasks."
    elif stale:
        level = "attention"
        title = f"{stale} overdue PAH message{'s' if stale != 1 else ''}"
        body = f"Oldest unread is {human_duration(oldest)}. Open PAH and paste the prepared wake line into the named AI."
    elif decisions:
        level = "decision"
        title = f"{decisions} Darrin decision{'s' if decisions != 1 else ''} pending"
        body = "Open PAH to review approval or deferral work."
    elif diag_problems:
        level = "diagnostic"
        title = f"{diag_problems} PAH diagnostic item{'s' if diag_problems != 1 else ''}"
        body = "Open PAH diagnostics to review route, watcher, or validation health."
    else:
        level = "ok"
        title = "PAH quiet"
        body = "No overdue wake-ups right now."

    tooltip = title if len(title) <= 60 else title[:57] + "..."
    return {
        "ok": True,
        "schema_version": 1,
        "generated_at": cockpit.get("generated_at", ""),
        "level": level,
        "title": title,
        "body": body,
        "tooltip": tooltip,
        "counts": {
            "stale_unread": stale,
            "urgent_codex_requests": urgent_codex,
            "unread": unread,
            "decisions_needed": decisions,
            "diagnostic_problems": diag_problems,
            "routes_failed": int(routes_summary.get("failed", 0) or 0),
            "routes_held": int(routes_summary.get("held", 0) or 0),
        },
        "oldest_stale_unread_seconds": oldest,
        "oldest_stale_unread_label": human_duration(oldest) if oldest else "",
        "target_counts": target_counts,
        "stale_unread_threshold_seconds": state.get("stale_unread_threshold_seconds", STALE_UNREAD_SECONDS),
        "direct_wake_supported": False,
        "safety_label": "Human-in-the-loop. Tray alerts only; Darrin still pastes wake lines.",
    }


def message_to_json(
    msg: Message,
    read_state_data: dict[str, Any] | None = None,
    completed_threads: set[str] | None = None,
) -> dict[str, Any]:
    read_status = message_read_status(msg.path, msg.message_id, msg.body, read_state_data)
    age_seconds = max(0, int(time.time() - msg.modified))
    classifier_state = classify_thread_state(msg)
    thread_has_completion_evidence = bool(
        completed_threads is not None and msg.stable_thread in completed_threads and not is_completion_evidence_message(msg)
    )
    stale_unread = bool(
        read_status["unread"]
        and age_seconds >= STALE_UNREAD_SECONDS
        and not thread_has_completion_evidence
        and classifier_state in {"open_on_agent", "owner_unknown"}
    )
    wake_candidate_agent = safe_slug(msg.to_agent).replace("-", "_") if msg.to_agent else ""
    wake_candidate_label = msg.to_agent or ""
    urgent_codex_request = is_urgent_codex_request_message(msg)
    return {
        "direction": msg.direction,
        "path": str(msg.path),
        "name": msg.name,
        "modified": datetime.fromtimestamp(msg.modified).isoformat(timespec="seconds"),
        "title": msg.title,
        "message_id": msg.message_id,
        "thread_id": msg.thread_id,
        "thread_status": msg.thread_status,
        "status": msg.status,
        "type": msg.message_type,
        "priority": msg.priority,
        "approval_boundary": msg.approval_boundary,
        "from_agent": msg.from_agent,
        "to_agent": msg.to_agent,
        "read_state": read_status["state"],
        "unread": read_status["unread"],
        "age_seconds": age_seconds,
        "stale_unread": stale_unread,
        "urgent_codex_request": urgent_codex_request,
        "wake_candidate_agent": wake_candidate_agent,
        "wake_candidate_label": wake_candidate_label,
        "content_changed_since_read": read_status["content_changed"],
        "classifier_state": classifier_state,
        "thread_has_completion_evidence": thread_has_completion_evidence,
        "status_badges": message_status_badges(msg, read_status["unread"]),
        "quarantine_allowed": quarantine_candidate_allowed(msg.path),
        "quarantine_reason": default_quarantine_reason("schema", msg.summary or msg.title),
        "summary": msg.summary or msg.body_preview,
    }


def build_mailbox_overview(messages: list[Message], read_state_data: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    groups: dict[str, dict[str, Any]] = {}
    for msg in messages:
        row = groups.setdefault(
            msg.direction,
            {
                "name": msg.direction,
                "count": 0,
                "unread": 0,
                "latest_modified": "",
                "latest_title": "",
                "messages": [],
            },
        )
        item = message_to_json(msg, read_state_data)
        row["count"] += 1
        if item["unread"]:
            row["unread"] += 1
        if not row["latest_modified"]:
            row["latest_modified"] = item["modified"]
            row["latest_title"] = item["title"]
        if len(row["messages"]) < 80:
            row["messages"].append(item)
    return sorted(groups.values(), key=lambda row: row["latest_modified"], reverse=True)


def build_agent_mailbox_messages(
    messages: list[Message], read_state_data: dict[str, Any] | None = None, limit: int = 80
) -> dict[str, list[dict[str, Any]]]:
    boxes: dict[str, list[dict[str, Any]]] = {
        "darrin": [],
        "codex": [],
        "claude-desktop": [],
        "claude-code": [],
    }
    for msg in messages:
        read_status = message_read_status(msg.path, msg.message_id, msg.body, read_state_data)
        if not read_status["unread"]:
            continue
        targets: list[str] = []
        if msg.is_waiting_on_darrin and message_in_any_agent_inbox(msg):
            targets.append("darrin")
        if msg.to_agent in boxes and message_in_agent_inbox(msg, msg.to_agent):
            targets.append(msg.to_agent)
        for target in dict.fromkeys(targets):
            if len(boxes[target]) < limit:
                boxes[target].append(message_to_json(msg, read_state_data))
    return boxes


def build_agent_status(
    messages: list[Message],
    read_state_data: dict[str, Any] | None,
    work_board: dict[str, Any],
    decisions: list[dict[str, Any]],
    thread_focus: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    now = datetime.now().timestamp()
    thread_focus = thread_focus or {}
    active_work_states = {"todo", "in_progress", "review", "blocked"}
    agent_rows = [
        {"id": "codex", "label": "Codex", "initials": "CX", "role": "builder / sender"},
        {"id": "claude-desktop", "label": "Claude Desktop", "initials": "CL", "role": "planner / reviewer"},
        {"id": "claude-code", "label": "Claude Code", "initials": "CC", "role": "native mailbox worker"},
        {"id": "darrin", "label": "Darrin", "initials": "DR", "role": "human approval / wake bridge"},
    ]

    def compact_message(msg: Message | None, role: str = "") -> dict[str, Any] | None:
        if msg is None:
            return None
        return {
            "role": role,
            "title": msg.title,
            "thread_id": msg.thread_id or msg.stable_thread,
            "path": str(msg.path),
            "direction": msg.direction,
            "modified": datetime.fromtimestamp(msg.modified).isoformat(timespec="seconds"),
            "age_minutes": max(0, round((now - msg.modified) / 60)),
            "status": msg.status,
            "thread_status": msg.thread_status,
            "priority": msg.priority,
            "type": msg.message_type,
        }

    rows: list[dict[str, Any]] = []
    work_items = [
        item for item in work_board.get("items", []) if str(item.get("state", "")).lower() in active_work_states
    ]
    for agent in agent_rows:
        agent_id = agent["id"]
        if agent_id == "darrin":
            open_on_darrin = list(thread_focus.get("open_on_darrin", []))
            open_thread_ids = {str(row.get("thread_id") or row.get("id")) for row in open_on_darrin}
            inbound = [
                msg
                for msg in messages
                if msg.stable_thread in open_thread_ids and message_in_any_agent_inbox(msg)
            ]
            outbound: list[Message] = []
            waiting_messages = inbound
            agent_work: list[dict[str, Any]] = []
        else:
            inbound = [msg for msg in messages if msg.to_agent == agent_id and message_in_agent_inbox(msg, agent_id)]
            outbound = [msg for msg in messages if msg.from_agent == agent_id]
            waiting_messages = [
                msg
                for msg in inbound
                if message_read_status(msg.path, msg.message_id, msg.body, read_state_data)["unread"]
                or msg.thread_status.lower() in {"waiting_on_agent", "waiting_on_darrin"}
                or msg.status.lower() in {"open", "blocked"}
                or msg.message_type.lower() in {"response_request", "dispatch", "decision_request"}
            ]
            agent_work = [item for item in work_items if str(item.get("owner", "")) == agent_id]

        latest_inbound = inbound[0] if inbound else None
        latest_outbound = outbound[0] if outbound else None
        latest_activity = max([msg.modified for msg in inbound + outbound], default=0)
        latest_age = max(0, round((now - latest_activity) / 60)) if latest_activity else None

        current_work: dict[str, Any] | None = None
        if agent_work:
            item = agent_work[0]
            current_work = {
                "role": "work_item",
                "title": str(item.get("title", "Work item")),
                "thread_id": str(item.get("item_id", "")),
                "path": str(item.get("dispatch", {}).get("path", "")),
                "direction": "PAH Work Board",
                "modified": str(item.get("updated_at", "")),
                "age_minutes": latest_age,
                "status": str(item.get("state", "")),
                "thread_status": str(item.get("state", "")),
                "priority": str(item.get("priority", "")),
                "type": "work_item",
                "summary": str(item.get("summary", "")),
            }
        elif waiting_messages:
            current_work = compact_message(waiting_messages[0], "waiting_for_agent")
        elif latest_outbound and (not latest_inbound or latest_outbound.modified >= latest_inbound.modified):
            current_work = compact_message(latest_outbound, "latest_output")
        else:
            current_work = compact_message(latest_inbound, "latest_input")

        unread = sum(
            1
            for msg in inbound
            if message_read_status(msg.path, msg.message_id, msg.body, read_state_data)["unread"]
        )
        urgent_waiting = [
            msg
            for msg in waiting_messages
            if msg.priority.lower() in {"high", "urgent"} or msg.thread_status.lower() == "waiting_on_agent"
        ]

        if agent_id == "darrin" and waiting_messages:
            state = "needs_attention"
        elif agent_id == "darrin":
            state = "idle"
        elif urgent_waiting:
            state = "needs_wake" if agent_id == "claude-code" else "waiting"
        elif waiting_messages:
            state = "waiting"
        elif latest_age is None:
            state = "unknown"
        elif latest_age <= 10:
            state = "active"
        elif latest_age <= 45:
            state = "recent"
        else:
            state = "idle"

        rows.append(
            {
                **agent,
                "state": state,
                "state_label": state.replace("_", " "),
                "inbound": len(inbound),
                "outbound": len(outbound),
                "unread": unread,
                "waiting": len(waiting_messages),
                "latest_age_minutes": latest_age,
                "latest_inbound": compact_message(latest_inbound, "latest_input"),
                "latest_outbound": compact_message(latest_outbound, "latest_output"),
                "current_work": current_work,
                "status_source": "mailbox_derived",
                "status_note": "Derived from mailbox/work-board activity; it is not direct process presence.",
            }
        )
    return rows


def load_watcher_state() -> dict[str, Any]:
    return read_json(WATCHER_STATE_PATH, {"acknowledged": {}, "snoozed": {}, "copied": {}})


def write_watcher_state(state_data: dict[str, Any]) -> None:
    write_json(WATCHER_STATE_PATH, state_data)


def append_watcher_event(event: dict[str, Any]) -> None:
    WATCHER_EVENT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {"time": datetime.now().isoformat(timespec="seconds"), **event}
    atomic_append_text(WATCHER_EVENT_LOG_PATH, json.dumps(payload, sort_keys=True) + "\n")


def recent_watcher_events(limit: int = 50) -> list[dict[str, Any]]:
    if not WATCHER_EVENT_LOG_PATH.exists():
        return []
    events: list[dict[str, Any]] = []
    for line in read_text(WATCHER_EVENT_LOG_PATH).splitlines()[-limit:]:
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            events.append(payload)
    return list(reversed(events))


TRUST_LEDGER_EVENT_TYPES = {
    "agent_no_mail_claim_discrepancy",
    "agent_no_mail_claim_validated",
    "mailbox_discrepancy_detected",
    "steward_check_finished",
}
DISCREPANCY_LEDGER_EVENT_TYPES = {
    "agent_no_mail_claim_discrepancy",
    "mailbox_discrepancy_detected",
}


def recent_interaction_ledger_events(
    limit: int = 50,
    event_types: set[str] | None = None,
) -> list[dict[str, Any]]:
    limit = max(1, min(500, int(limit or 50)))
    if not INTERACTION_LEDGER_PATH.exists():
        return []
    events: list[dict[str, Any]] = []
    for line in reversed(read_text(INTERACTION_LEDGER_PATH).splitlines()):
        if len(events) >= limit:
            break
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(payload, dict):
            continue
        if event_types and str(payload.get("event_type", "")) not in event_types:
            continue
        events.append(payload)
    return events


def interaction_ledger_summary(limit: int = 8) -> dict[str, Any]:
    events = recent_interaction_ledger_events(limit=limit, event_types=TRUST_LEDGER_EVENT_TYPES)
    discrepancies = [
        event
        for event in events
        if str(event.get("event_type", "")) in DISCREPANCY_LEDGER_EVENT_TYPES
    ]
    return {
        "path": str(INTERACTION_LEDGER_PATH),
        "exists": INTERACTION_LEDGER_PATH.exists(),
        "events": events,
        "discrepancy_count": len(discrepancies),
        "latest_discrepancy": discrepancies[0] if discrepancies else None,
    }


def watcher_default_path(agent_id: str) -> str:
    if agent_id == "claude-code":
        return str(CLAUDE_CODE_INBOX)
    if agent_id == "claude-desktop":
        return str(CLAUDE_INBOX)
    if agent_id == "codex":
        return str(CODEX_INBOX)
    if agent_id == "darrin":
        return str(DECISION_QUEUE_PATH)
    return str(MAILBOX_ROOT)


def watcher_fingerprint(agent: dict[str, Any], path_value: str) -> str:
    work = agent.get("current_work") if isinstance(agent.get("current_work"), dict) else {}
    parts = [
        str(agent.get("id", "agent")),
        str(agent.get("state", "unknown")),
        str(work.get("thread_id", "")),
        str(work.get("title", "")),
        path_value,
    ]
    label = safe_slug(str(work.get("title") or agent.get("label") or "alert"))
    return f"watcher-{label}-{content_hash('|'.join(parts))[:12]}"


def watcher_wake_prompt(agent: dict[str, Any], path_value: str) -> str:
    agent_id = str(agent.get("id", ""))
    label = str(agent.get("label", "Agent"))
    work = agent.get("current_work") if isinstance(agent.get("current_work"), dict) else {}
    title = compact(str(work.get("title", "latest PAH mailbox item")), 120)
    state = str(agent.get("state_label", agent.get("state", "waiting")))
    if agent_id == "claude-code":
        return (
            f"Read {path_value or CLAUDE_CODE_INBOX} now. PAH shows Claude Code is {state} on: "
            f"{title}. Reply through the PAH/CC mailbox when done."
        )
    if agent_id == "claude-desktop":
        return (
            f"Read {path_value or CLAUDE_INBOX} now. PAH shows Claude Desktop is {state} on: "
            f"{title}. Reply through the PAH mailbox when done."
        )
    if agent_id == "codex":
        return f"Read {path_value or CODEX_INBOX} now. PAH shows Codex has pending mailbox work: {title}."
    if agent_id == "darrin":
        return f"Review PAH decisions at {path_value or DECISION_QUEUE_PATH}. PAH shows Darrin attention is needed: {title}."
    return f"Read {path_value or MAILBOX_ROOT} now. PAH shows {label} is {state} on: {title}."


def build_watcher_status(
    agent_status: list[dict[str, Any]],
    route_tests: dict[str, Any],
    state_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    state_data = state_data or load_watcher_state()
    acknowledged = state_data.get("acknowledged", {}) if isinstance(state_data.get("acknowledged"), dict) else {}
    snoozed = state_data.get("snoozed", {}) if isinstance(state_data.get("snoozed"), dict) else {}
    copied = state_data.get("copied", {}) if isinstance(state_data.get("copied"), dict) else {}
    now_epoch = time.time()
    actionable_states = {"needs_wake", "needs_attention", "waiting"}
    alerts: list[dict[str, Any]] = []

    for agent in agent_status:
        agent_state = str(agent.get("state", "unknown"))
        if agent_state not in actionable_states:
            continue
        work = agent.get("current_work") if isinstance(agent.get("current_work"), dict) else {}
        path_value = str(work.get("path") or watcher_default_path(str(agent.get("id", ""))))
        fingerprint = watcher_fingerprint(agent, path_value)
        snooze_record = snoozed.get(fingerprint, {}) if isinstance(snoozed.get(fingerprint), dict) else {}
        snoozed_until_epoch = float(snooze_record.get("until_epoch") or 0)
        acknowledged_record = acknowledged.get(fingerprint, {}) if isinstance(acknowledged.get(fingerprint), dict) else {}
        copied_record = copied.get(fingerprint, {}) if isinstance(copied.get(fingerprint), dict) else {}
        severity = "critical" if agent_state == "needs_wake" else "high" if agent_state == "needs_attention" else "normal"
        alert = {
            "fingerprint": fingerprint,
            "agent": agent.get("id", ""),
            "agent_label": agent.get("label", "Agent"),
            "state": agent_state,
            "state_label": agent.get("state_label", agent_state.replace("_", " ")),
            "severity": severity,
            "title": (
                f"{agent.get('label', 'Agent')} needs a wake line"
                if agent_state == "needs_wake"
                else f"{agent.get('label', 'Agent')} needs attention"
                if agent_state == "needs_attention"
                else f"{agent.get('label', 'Agent')} has waiting mailbox work"
            ),
            "reason": compact(
                f"{agent.get('waiting', 0)} waiting, {agent.get('unread', 0)} unread, "
                f"latest activity {agent.get('latest_age_minutes', 'unknown')} minutes ago.",
                180,
            ),
            "wake_prompt": watcher_wake_prompt(agent, path_value),
            "path": path_value,
            "thread_id": str(work.get("thread_id", "")),
            "work_title": str(work.get("title", "")),
            "age_minutes": agent.get("latest_age_minutes"),
            "acknowledged": bool(acknowledged_record),
            "acknowledged_at": acknowledged_record.get("time", ""),
            "copied_at": copied_record.get("time", ""),
            "snoozed": snoozed_until_epoch > now_epoch,
            "snoozed_until": snooze_record.get("until", ""),
            "active": snoozed_until_epoch <= now_epoch,
            "source": "mailbox_agent_status",
        }
        alerts.append(alert)

    route_waits = [
        test
        for test in route_tests.get("tests", [])
        if str(test.get("state", "")).lower() not in {"received_reply", "ok", "passed"}
    ]
    alerts.sort(key=lambda row: (not row["active"], row["severity"] != "critical", row["agent_label"]))
    active_alerts = [alert for alert in alerts if alert["active"]]
    return {
        "mode": "human_in_loop",
        "direct_wake_supported": False,
        "policy": "PAH can detect, notify, prepare wake prompts, and log actions. Darrin remains the wake bridge for CC/Claude UI focus.",
        "state_path": str(WATCHER_STATE_PATH),
        "event_log_path": str(WATCHER_EVENT_LOG_PATH),
        "alerts": alerts,
        "counts": {
            "alerts": len(alerts),
            "active_alerts": len(active_alerts),
            "snoozed_alerts": sum(1 for alert in alerts if alert["snoozed"]),
            "acknowledged_alerts": sum(1 for alert in alerts if alert["acknowledged"]),
            "needs_wake": sum(1 for alert in active_alerts if alert["state"] == "needs_wake"),
            "needs_attention": sum(1 for alert in active_alerts if alert["state"] == "needs_attention"),
            "waiting": sum(1 for alert in active_alerts if alert["state"] == "waiting"),
            "route_tests_waiting": len(route_waits),
        },
    }


def record_watcher_action(payload: dict[str, Any]) -> dict[str, Any]:
    fingerprint = str(payload.get("fingerprint", "")).strip()
    action = str(payload.get("action", "")).strip().lower()
    if not fingerprint:
        raise ValueError("Watcher fingerprint is required.")
    if action not in {"ack", "snooze", "copy"}:
        raise ValueError("Watcher action must be ack, snooze, or copy.")
    actor = str(payload.get("actor", "darrin_or_codex"))
    now_iso = datetime.now().isoformat(timespec="seconds")
    record: dict[str, Any] = {"time": now_iso, "actor": actor, "action": action}
    with WATCHER_LOCK:
        state_data = load_watcher_state()
        state_data.setdefault("acknowledged", {})
        state_data.setdefault("snoozed", {})
        state_data.setdefault("copied", {})
        if action == "ack":
            state_data["acknowledged"][fingerprint] = record
        elif action == "copy":
            state_data["copied"][fingerprint] = record
        elif action == "snooze":
            minutes = max(1, min(480, int(payload.get("minutes") or WATCHER_SNOOZE_DEFAULT_MINUTES)))
            until_epoch = time.time() + minutes * 60
            record = {
                **record,
                "minutes": minutes,
                "until_epoch": until_epoch,
                "until": datetime.fromtimestamp(until_epoch).isoformat(timespec="seconds"),
            }
            state_data["snoozed"][fingerprint] = record
        write_watcher_state(state_data)
        append_watcher_event({"fingerprint": fingerprint, "record": record})
    return record


HTML_PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PANDA Agent Hub</title>
<style>
:root {
  --bg: #151719;
  --panel: #1d2023;
  --panel-2: #23272b;
  --line: #343a40;
  --soft: #2a2f34;
  --text: #e8eaec;
  --muted: #9ca4aa;
  --accent: #e8a87c;
  --green: #78c58b;
  --red: #e06d6d;
  --yellow: #d8bf72;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--text); font: 13px/1.45 "Segoe UI", system-ui, sans-serif; }
header { height: 54px; border-bottom: 1px solid var(--line); display: flex; align-items: center; justify-content: space-between; padding: 0 18px; background: #101214; position: sticky; top: 0; z-index: 2; }
h1 { font-size: 15px; margin: 0; font-weight: 650; letter-spacing: 0; }
button, select, input, textarea { font: inherit; }
button { border: 1px solid var(--line); background: transparent; color: var(--text); padding: 7px 10px; border-radius: 6px; cursor: pointer; }
button.primary { background: var(--accent); color: #20140f; border-color: var(--accent); font-weight: 650; }
button:hover { border-color: var(--accent); }
main { display: grid; grid-template-columns: 280px 1fr 360px; min-height: calc(100vh - 54px); }
aside, section { min-width: 0; }
.left { border-right: 1px solid var(--line); padding: 14px; background: #171a1d; }
.center { padding: 14px; }
.right { border-left: 1px solid var(--line); padding: 14px; background: #171a1d; }
.card { background: var(--panel); border: 1px solid var(--line); border-radius: 8px; margin-bottom: 12px; overflow: hidden; }
.card-head { padding: 9px 11px; border-bottom: 1px solid var(--line); color: var(--accent); text-transform: uppercase; font-size: 11px; letter-spacing: .08em; font-weight: 700; }
.card-body { padding: 11px; }
.metric { display: grid; grid-template-columns: 1fr auto; padding: 7px 0; border-bottom: 1px solid var(--soft); gap: 12px; }
.metric:last-child { border-bottom: 0; }
.muted { color: var(--muted); }
.good { color: var(--green); }
.warn { color: var(--yellow); }
.bad { color: var(--red); }
.tabs { display: flex; gap: 6px; margin-bottom: 12px; flex-wrap: wrap; }
.tab.active { background: var(--panel-2); border-color: var(--accent); }
.list { display: grid; gap: 8px; }
.item { background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 10px; }
.item.unread { border-color: var(--accent); background: #211f1d; }
.item-title { display: flex; justify-content: space-between; gap: 10px; font-weight: 650; }
.pill { display: inline-block; border: 1px solid var(--line); border-radius: 999px; padding: 2px 7px; color: var(--muted); font-size: 11px; white-space: nowrap; }
.badges { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 7px; }
.badge { display: inline-block; border: 1px solid var(--soft); border-radius: 999px; padding: 1px 7px; color: var(--text); background: #181b1e; font-size: 10px; text-transform: uppercase; }
.badge.unread { color: #20140f; background: var(--accent); border-color: var(--accent); font-weight: 700; }
.actions { margin: 8px 0 0; display: flex; flex-wrap: wrap; gap: 6px; }
.actions select { width: auto; max-width: 210px; padding: 6px 8px; }
.path { color: var(--muted); font-family: Consolas, monospace; font-size: 11px; word-break: break-all; margin-top: 6px; }
.summary { color: var(--muted); margin-top: 7px; }
.grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
label { display: block; color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: .06em; margin: 8px 0 4px; }
input, select, textarea { width: 100%; background: #111315; color: var(--text); border: 1px solid var(--line); border-radius: 6px; padding: 8px; }
textarea { min-height: 150px; resize: vertical; }
pre { white-space: pre-wrap; word-break: break-word; margin: 0; color: var(--muted); font-family: Consolas, monospace; font-size: 12px; }
.hidden { display: none; }
@media (max-width: 1120px) { main { grid-template-columns: 1fr; } .left, .right { border: 0; } }
</style>
</head>
<body>
<header>
  <h1>PANDA Agent Hub</h1>
  <div><button id="refresh">Refresh</button> <button class="primary" id="composeJump">Compose</button></div>
</header>
<main>
  <aside class="left">
    <div class="card"><div class="card-head">Dashboard</div><div class="card-body" id="metrics"></div></div>
    <div class="card"><div class="card-head">Notifications</div><div class="card-body" id="notificationStatus"></div></div>
    <div class="card"><div class="card-head">Git</div><div class="card-body"><pre id="gitStatus">Loading...</pre></div></div>
    <div class="card"><div class="card-head">Paths</div><div class="card-body"><div class="path" id="paths"></div></div></div>
  </aside>
  <section class="center">
    <div class="tabs">
      <button class="tab active" data-tab="latest">Latest</button>
      <button class="tab" data-tab="threads">Threads</button>
      <button class="tab" data-tab="decisions">Darrin Queue</button>
      <button class="tab" data-tab="validation">Validator</button>
      <button class="tab" data-tab="diagnostics">Diagnostics</button>
      <button class="tab" data-tab="work">Work</button>
      <button class="tab" data-tab="safety">Safety</button>
    </div>
    <div id="latest" class="pane"><p><button id="markAllRead">Mark All Read</button></p><div class="list" id="latestList"></div></div>
    <div id="threads" class="pane hidden"><div class="list" id="threadList"></div><div class="card"><div class="card-head">Archived Threads</div><div class="card-body"><div class="list" id="archivedThreadList"></div></div></div></div>
    <div id="decisions" class="pane hidden"><div class="list" id="decisionList"></div><div class="card"><div class="card-head">Resolved / Superseded</div><div class="card-body"><div class="list" id="decisionHistoryList"></div></div></div></div>
    <div id="validation" class="pane hidden"><div class="card"><div class="card-head">Actionable Validation</div><div class="card-body"><div id="validationSummary"></div><div class="list" id="validationActionableList"></div></div></div><div class="card"><div class="card-head">Accepted / Resolved Validation</div><div class="card-body"><div class="list" id="validationInactiveList"></div></div></div><div class="card"><div class="card-head">All Validation History</div><div class="card-body"><div class="list" id="validationList"></div></div></div></div>
    <div id="diagnostics" class="pane hidden"><div class="card"><div class="card-head">Health Checks</div><div class="card-body"><div class="list" id="diagnosticList"></div></div></div><div class="card"><div class="card-head">Route Tests</div><div class="card-body"><div class="list" id="routeTestList"></div></div></div></div>
    <div id="work" class="pane hidden"><div class="list" id="workList"></div></div>
    <div id="safety" class="pane hidden"><div class="grid2"><div class="list" id="approvalList"></div><div class="list" id="adapterList"></div></div><div class="list" id="quarantineList"></div></div>
  </section>
  <aside class="right" id="composePanel">
    <div class="card"><div class="card-head">Compose</div><div class="card-body">
      <label>Route</label>
      <select id="route"><option value="codex_to_claude">Codex to Claude</option><option value="codex_to_claude_code">Codex to Claude Code</option></select>
      <label>Status</label>
      <select id="status"><option>Info</option><option>Response Requested</option><option>Decision Needed</option><option>Implementation Report</option></select>
      <label>Subject</label><input id="subject" placeholder="Short topic">
      <label>Thread ID</label><input id="threadId" placeholder="Optional, e.g. AGENT-HUB-V1">
      <label>Reply To</label><textarea id="replyTo" placeholder="Optional Message-ID or source path"></textarea>
      <label>Message</label><textarea id="body" placeholder="Write the coordination note..."></textarea>
      <p><button class="primary" id="send">Send Message</button></p>
      <pre id="sendResult"></pre>
    </div></div>
    <div class="card"><div class="card-head">SMS Test</div><div class="card-body">
      <p class="muted">Sends a real SMS only when Twilio or email-to-SMS is enabled in the ignored local config. Otherwise it logs the test.</p>
      <p><button id="testSms">Send Test Notification</button></p>
      <pre id="smsResult"></pre>
    </div></div>
    <div class="card"><div class="card-head">Communication Test</div><div class="card-body">
      <p class="muted">Checks file-bridge readiness for Codex, Claude Desktop, and Claude Code. Live adapters stay disabled.</p>
      <p><button id="testComm">Run Diagnostics</button></p>
      <label>Route Test</label>
      <select id="routeTestRoute"><option value="codex_to_claude">Codex to Claude</option><option value="codex_to_claude_code">Codex to Claude Code</option></select>
      <p><button id="createRouteTest">Create Test Ping</button></p>
      <pre id="commResult"></pre>
    </div></div>
    <div class="card"><div class="card-head">Work Item</div><div class="card-body">
      <label>Owner</label>
      <select id="workOwner"><option value="codex">Codex</option><option value="claude-desktop">Claude Desktop</option><option value="claude-code">Claude Code</option></select>
      <label>Priority</label>
      <select id="workPriority"><option value="normal">Normal</option><option value="high">High</option><option value="urgent">Urgent</option><option value="low">Low</option></select>
      <label>Title</label><input id="workTitle" placeholder="Work item">
      <label>Summary</label><textarea id="workSummary" placeholder="Scope, expected output, or blocker"></textarea>
      <p><button id="createWorkItem">Create Work Item</button></p>
      <pre id="workResult"></pre>
    </div></div>
  </aside>
</main>
<script>
const WRITE_TOKEN = "__WRITE_TOKEN__";
let current = null;
function esc(value) { return String(value ?? '').replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c])); }
async function load() {
  const res = await fetch('/api/status'); current = await res.json(); render(current);
}
function render(data) {
  document.getElementById('metrics').innerHTML = Object.entries(data.counts).map(([k,v]) => `<div class="metric"><span>${esc(k)}</span><strong>${v}</strong></div>`).join('') + `<div class="metric"><span>updated</span><span class="muted">${esc(data.generated_at)}</span></div>`;
  document.getElementById('notificationStatus').innerHTML = notificationBlock(data.notifications);
  document.getElementById('gitStatus').textContent = data.git.text || 'No git status available';
  document.getElementById('paths').innerHTML = `Mailbox:<br>${esc(data.mailbox_root)}<br><br>Decision queue:<br>${esc(data.decision_queue_path)}`;
  list('latestList', data.latest, m => messageItem(m));
  list('threadList', data.threads, t => threadItem(t));
  list('archivedThreadList', data.archived_threads || [], t => threadItem(t));
  list('decisionList', data.decisions, d => decisionItem(d));
  list('decisionHistoryList', data.decision_history || [], d => item(d.title, d.decision_state || 'inactive', `${d.state_note || ''} ${d.summary || ''}`, d.path));
  document.getElementById('validationSummary').innerHTML = validationSummaryBlock(data.validation_summary);
  list('validationActionableList', data.validation_actionable || [], v => validationItem(v));
  list('validationInactiveList', data.validation_inactive || [], v => item(v.message, v.validation_state || 'inactive', `${v.state_note || ''} ${v.title || ''}`, v.path));
  list('validationList', data.validation, v => item(v.message, `${v.level} · ${v.category}`, v.title, v.path));
  list('diagnosticList', data.diagnostics.checks, d => item(d.name, d.ok ? 'PASS' : 'CHECK', d.detail, data.diagnostics.report_path || ''));
  list('routeTestList', data.route_tests.tests || [], t => item(t.test_id, t.state, `${t.from} → ${t.to} · ${t.created_at}${t.reply_seen_at ? ' · replied ' + t.reply_seen_at : ''}`, t.reply_path || t.message_path));
  list('workList', data.work_board.items || [], w => workItem(w));
  list('approvalList', [
    {title:'Approval records', pill:data.approvals.records, summary:`active ${data.approvals.active}, invalid ${data.approvals.invalid}, revoked ${data.approvals.revoked}, expired ${data.approvals.expired}, consumed ${data.approvals.consumed}`, path:data.approvals.records_path},
    {title:'Protected-action enforcement', pill:data.approvals.enforcement || 'unknown', summary:(data.approvals.protected_action_types || []).join(', '), path:''},
    {title:'Strict MCP config', pill:data.approvals.canonical_mcp_config_hash ? 'pinned' : 'missing', summary:(data.approvals.headless_mcp_required_fields || []).join(', '), path:data.approvals.canonical_mcp_config_path || ''},
    {title:'Headless command contract', pill:'disabled', summary:(data.approvals.headless_command_required_fields || []).join(', '), path:''},
    {title:'Approval hash mutability', pill:'locked', summary:`mutable after approval: ${(data.approvals.approval_mutable_after_approval_fields || []).join(', ')}`, path:''},
    {title:'Required fields', pill:'schema', summary:data.approvals.required_fields.join(', '), path:''}
  ], a => item(a.title, a.pill, a.summary, a.path));
  list('adapterList', data.adapters.adapters, a => item(a.display_name, a.enabled ? 'ENABLED' : 'DISABLED', `${a.safety_status} · ${a.notes}`, a.adapter_id));
  const quarantineRows = [
    {title:'Quarantine', pill:data.quarantine.automatic_moves ? 'AUTO' : 'EXPLICIT', summary:`${data.quarantine.messages} quarantined messages, ${data.quarantine.tombstones} tombstones. ${data.quarantine.detail}`, path:data.quarantine.quarantine_dir},
    ...(data.quarantine.recent || []).map(r => ({title:r.original_name || 'Tombstone', pill:r.reason || 'quarantined', summary:`Moved ${r.moved_at || ''}`, path:r.tombstone_path || r.quarantine_path}))
  ];
  list('quarantineList', quarantineRows, q => item(q.title, q.pill, q.summary, q.path));
}
function list(id, rows, fn) { document.getElementById(id).innerHTML = rows.length ? rows.map(fn).join('') : '<div class="item muted">Nothing to show.</div>'; }
function item(title, pill, summary, path) { return `<div class="item"><div class="item-title"><span>${esc(title)}</span><span class="pill">${esc(pill)}</span></div><div class="summary">${esc(summary || '')}</div><div class="path">${esc(path || '')}</div></div>`; }
function badgeBlock(row) {
  return (row.status_badges || []).length ? `<div class="badges">${(row.status_badges || []).map(b => `<span class="badge ${b === 'unread' ? 'unread' : ''}">${esc(b)}</span>`).join('')}</div>` : '';
}
function quarantineReasonSelect(defaultReason) {
  const reasons = current?.quarantine?.reason_codes || ['schema_invalid'];
  return `<select aria-label="Quarantine reason">${reasons.map(reason => `<option value="${esc(reason)}" ${reason === defaultReason ? 'selected' : ''}>${esc(reason)}</option>`).join('')}</select>`;
}
function quarantineControls(payload, defaultReason) {
  return `${quarantineReasonSelect(defaultReason || 'schema_invalid')}<button onclick="quarantineMessage('${payload}', this.previousElementSibling.value)">Quarantine</button>`;
}
function messageItem(m) {
  const payload = encodeURIComponent(JSON.stringify({path:m.path}));
  const readAction = m.unread ? `<button onclick="setReadState('${payload}','read')">Mark Read</button>` : `<button onclick="setReadState('${payload}','unread')">Mark Unread</button>`;
  const quarantineAction = m.quarantine_allowed ? quarantineControls(payload, m.quarantine_reason) : '';
  const action = `${readAction}${quarantineAction}`;
  return `<div class="item ${m.unread ? 'unread' : ''}"><div class="item-title"><span>${esc(m.title)}</span><span class="pill">${esc(m.status || m.direction)}</span></div>${badgeBlock(m)}<div class="summary">${esc(m.summary || '')}</div><div class="path">${esc(m.path || '')}</div><p class="actions">${action}</p></div>`;
}
function threadItem(t) {
  const unread = t.unread ? ` · unread ${t.unread}` : '';
  const payload = encodeURIComponent(JSON.stringify({thread_id:t.thread_id}));
  const action = t.archived ? `<button onclick="setThreadArchiveState('${payload}','active')">Unarchive</button>` : `<button onclick="setThreadArchiveState('${payload}','archived')">Archive</button>`;
  const archiveNote = t.archived ? `<div class="summary">Archived ${esc(t.archived_at || '')}${t.archive_reason ? ' · ' + esc(t.archive_reason) : ''}</div>` : '';
  return `<div class="item ${t.unread ? 'unread' : ''}"><div class="item-title"><span>${esc(t.thread_id)}</span><span class="pill">${esc(t.status)}${esc(unread)}</span></div>${badgeBlock(t)}${archiveNote}<div class="summary">${esc(t.summary || '')}</div><div class="path">${esc(t.latest_path || '')}</div><p class="actions">${action}</p></div>`;
}
function decisionItem(d) {
  return `<div class="item"><div class="item-title"><span>${esc(d.title)}</span><span class="pill">${esc(d.status || 'Decision')}</span></div><div class="summary">${esc(d.summary || '')}</div><div class="path">${esc(d.path || '')}</div><p><button onclick="setDecisionState('${encodeURIComponent(d.path)}','resolved')">Resolved</button> <button onclick="setDecisionState('${encodeURIComponent(d.path)}','superseded')">Superseded</button> <button onclick="setDecisionState('${encodeURIComponent(d.path)}','dismissed')">Dismiss</button></p></div>`;
}
function validationItem(v) {
  const payload = encodeURIComponent(JSON.stringify({fingerprint:v.fingerprint, path:v.path, category:v.category, message:v.message, title:v.title}));
  const qPayload = encodeURIComponent(JSON.stringify({path:v.path}));
  const quarantineAction = v.quarantine_allowed ? quarantineControls(qPayload, v.quarantine_reason) : '';
  return `<div class="item"><div class="item-title"><span>${esc(v.message)}</span><span class="pill">${esc(v.level)} · ${esc(v.category)}</span></div><div class="summary">${esc(v.title || '')}</div><div class="path">${esc(v.path || '')}</div><p class="actions"><button onclick="setValidationState('${payload}','resolved')">Resolved</button> <button onclick="setValidationState('${payload}','accepted_legacy')">Accept Legacy</button> <button onclick="setValidationState('${payload}','dismissed')">Dismiss</button>${quarantineAction}</p></div>`;
}
function workItem(w) {
  const payload = encodeURIComponent(JSON.stringify({item_id:w.item_id}));
  const dispatchPath = w.dispatch?.path || '';
  const dispatchText = dispatchPath ? `Dispatch: ${dispatchPath}` : (w.dispatch?.note || '');
  const replyText = w.last_reply_path ? `Reply: ${w.last_reply_path} · ${w.last_reply_seen_at || ''}` : '';
  return `<div class="item"><div class="item-title"><span>${esc(w.title)}</span><span class="pill">${esc(w.state)} · ${esc(w.owner)}</span></div><div class="summary">${esc(w.summary || '')}</div><div class="path">${esc(w.priority)} · ${esc(w.source || w.item_id)}${dispatchText ? '<br>' + esc(dispatchText) : ''}${replyText ? '<br>' + esc(replyText) : ''}</div><p><button onclick="dispatchWorkItem('${payload}')">Dispatch</button> <button onclick="setWorkState('${payload}','in_progress')">Start</button> <button onclick="setWorkState('${payload}','review')">Review</button> <button onclick="setWorkState('${payload}','complete')">Complete</button> <button onclick="setWorkState('${payload}','blocked')">Blocked</button></p></div>`;
}
function notificationBlock(n) {
  const enabled = n.enabled ? '<span class="good">enabled</span>' : '<span class="muted">disabled</span>';
  const configured = n.configured ? '<span class="good">configured</span>' : '<span class="warn">needs config</span>';
  const liveReady = n.live_delivery_ready ? '<span class="good">live ready</span>' : '<span class="warn">setup required</span>';
  const popup = n.desktop_popups?.enabled ? '<span class="good">enabled</span>' : '<span class="muted">tray-ready</span>';
  return `<div class="metric"><span>Status</span><strong>${enabled}</strong></div><div class="metric"><span>Provider</span><span>${esc(n.provider)} · ${configured}</span></div><div class="metric"><span>Delivery</span><span>${liveReady}</span></div><div class="metric"><span>Desktop popups</span><span>${popup}</span></div><div class="metric"><span>Last sent</span><span class="muted">${esc(n.last_sent_at || 'never')}</span></div><div class="metric"><span>Config</span><span class="path">${esc(n.config_path)}</span></div>${n.setup_hint ? `<div class="warn">${esc(n.setup_hint)}</div>` : ''}${n.last_error ? `<div class="bad">${esc(n.last_error)}</div>` : ''}`;
}
function validationSummaryBlock(v) {
  const cats = Object.entries(v.by_category || {}).map(([k,val]) => `${esc(k)} ${val}`).join(' · ');
  return `<div class="metric"><span>Actionable</span><strong>${esc(v.actionable)}</strong></div><div class="metric"><span>Legacy/info</span><span>${esc(v.informational_or_legacy)}</span></div><div class="metric"><span>Categories</span><span class="muted">${cats || 'none'}</span></div>`;
}
document.querySelectorAll('.tab').forEach(btn => btn.addEventListener('click', () => { document.querySelectorAll('.tab').forEach(b => b.classList.remove('active')); btn.classList.add('active'); document.querySelectorAll('.pane').forEach(p => p.classList.add('hidden')); document.getElementById(btn.dataset.tab).classList.remove('hidden'); }));
document.getElementById('refresh').onclick = load;
document.getElementById('markAllRead').onclick = async () => {
  const res = await fetch('/api/mark-all-read', {method:'POST', headers:{'Content-Type':'application/json', 'X-Agent-Hub-Token': WRITE_TOKEN}, body: JSON.stringify({actor:'darrin_or_codex'})});
  const json = await res.json();
  if (!json.ok) alert(json.error || 'Mark all read failed');
  await load();
};
document.getElementById('composeJump').onclick = () => document.getElementById('subject').focus();
document.getElementById('send').onclick = async () => {
  const payload = { route: route.value, status: status.value, subject: subject.value, thread_id: threadId.value, reply_to: replyTo.value, body: body.value };
  const res = await fetch('/api/send', {method:'POST', headers:{'Content-Type':'application/json', 'X-Agent-Hub-Token': WRITE_TOKEN}, body: JSON.stringify(payload)});
  const json = await res.json(); sendResult.textContent = JSON.stringify(json, null, 2); if (json.ok) { subject.value=''; body.value=''; replyTo.value=''; await load(); }
};
document.getElementById('testSms').onclick = async () => {
  const res = await fetch('/api/test-notification', {method:'POST', headers:{'Content-Type':'application/json', 'X-Agent-Hub-Token': WRITE_TOKEN}, body: '{}'});
  smsResult.textContent = JSON.stringify(await res.json(), null, 2);
  await load();
};
document.getElementById('testComm').onclick = async () => {
  const res = await fetch('/api/run-diagnostics', {method:'POST', headers:{'Content-Type':'application/json', 'X-Agent-Hub-Token': WRITE_TOKEN}, body: '{}'});
  commResult.textContent = JSON.stringify(await res.json(), null, 2);
  await load();
};
document.getElementById('createRouteTest').onclick = async () => {
  const res = await fetch('/api/create-route-test', {method:'POST', headers:{'Content-Type':'application/json', 'X-Agent-Hub-Token': WRITE_TOKEN}, body: JSON.stringify({route: routeTestRoute.value, note: 'Created from PAH dashboard.'})});
  commResult.textContent = JSON.stringify(await res.json(), null, 2);
  await load();
};
document.getElementById('createWorkItem').onclick = async () => {
  const payload = {title: workTitle.value, owner: workOwner.value, priority: workPriority.value, summary: workSummary.value};
  const res = await fetch('/api/work-item', {method:'POST', headers:{'Content-Type':'application/json', 'X-Agent-Hub-Token': WRITE_TOKEN}, body: JSON.stringify(payload)});
  const json = await res.json();
  workResult.textContent = JSON.stringify(json, null, 2);
  if (json.ok) { workTitle.value=''; workSummary.value=''; await load(); }
};
async function setWorkState(payloadEncoded, state) {
  const item = JSON.parse(decodeURIComponent(payloadEncoded));
  const res = await fetch('/api/work-item', {method:'POST', headers:{'Content-Type':'application/json', 'X-Agent-Hub-Token': WRITE_TOKEN}, body: JSON.stringify({...item, state})});
  const json = await res.json();
  if (!json.ok) alert(json.error || 'Work item update failed');
  await load();
}
async function dispatchWorkItem(payloadEncoded) {
  const item = JSON.parse(decodeURIComponent(payloadEncoded));
  const res = await fetch('/api/dispatch-work-item', {method:'POST', headers:{'Content-Type':'application/json', 'X-Agent-Hub-Token': WRITE_TOKEN}, body: JSON.stringify(item)});
  const json = await res.json();
  if (!json.ok) alert(json.error || 'Work item dispatch failed');
  await load();
}
async function setDecisionState(pathEncoded, state) {
  const path = decodeURIComponent(pathEncoded);
  const note = state === 'resolved' ? 'Marked resolved from PAH dashboard.' : state === 'superseded' ? 'Marked superseded from PAH dashboard.' : 'Dismissed from PAH dashboard.';
  const res = await fetch('/api/decision-state', {method:'POST', headers:{'Content-Type':'application/json', 'X-Agent-Hub-Token': WRITE_TOKEN}, body: JSON.stringify({path, state, note, actor:'darrin_or_codex'})});
  const json = await res.json();
  if (!json.ok) alert(json.error || 'Decision update failed');
  await load();
}
async function setValidationState(payloadEncoded, state) {
  const finding = JSON.parse(decodeURIComponent(payloadEncoded));
  const note = state === 'accepted_legacy' ? 'Accepted as legacy mailbox history from PAH dashboard.' : state === 'resolved' ? 'Marked resolved from PAH dashboard.' : 'Dismissed from PAH dashboard.';
  const res = await fetch('/api/validation-state', {method:'POST', headers:{'Content-Type':'application/json', 'X-Agent-Hub-Token': WRITE_TOKEN}, body: JSON.stringify({...finding, state, note, actor:'darrin_or_codex'})});
  const json = await res.json();
  if (!json.ok) alert(json.error || 'Validation update failed');
  await load();
}
async function setReadState(payloadEncoded, state) {
  const item = JSON.parse(decodeURIComponent(payloadEncoded));
  const res = await fetch('/api/message-read-state', {method:'POST', headers:{'Content-Type':'application/json', 'X-Agent-Hub-Token': WRITE_TOKEN}, body: JSON.stringify({...item, state, actor:'darrin_or_codex'})});
  const json = await res.json();
  if (!json.ok) alert(json.error || 'Read-state update failed');
  await load();
}
async function quarantineMessage(payloadEncoded, reason) {
  const item = JSON.parse(decodeURIComponent(payloadEncoded));
  if (!confirm('Move this mailbox message to PAH Quarantine and write a tombstone?')) return;
  const res = await fetch('/api/quarantine-message', {method:'POST', headers:{'Content-Type':'application/json', 'X-Agent-Hub-Token': WRITE_TOKEN}, body: JSON.stringify({...item, reason, confirmed:true, actor:'darrin_or_codex'})});
  const json = await res.json();
  if (!json.ok) alert(json.error || 'Quarantine failed');
  await load();
}
async function setThreadArchiveState(payloadEncoded, state) {
  const item = JSON.parse(decodeURIComponent(payloadEncoded));
  const reason = state === 'archived' ? 'Archived from PAH dashboard.' : 'Unarchived from PAH dashboard.';
  const res = await fetch('/api/thread-archive-state', {method:'POST', headers:{'Content-Type':'application/json', 'X-Agent-Hub-Token': WRITE_TOKEN}, body: JSON.stringify({...item, state, reason, actor:'darrin_or_codex'})});
  const json = await res.json();
  if (!json.ok) alert(json.error || 'Thread archive update failed');
  await load();
}
load(); setInterval(load, 8000);
</script>
</body>
</html>"""


def html_page() -> str:
    if UI_PATH.exists():
        return read_text(UI_PATH).replace("__WRITE_TOKEN__", "")
    return """<!doctype html>
<html><head><meta charset="utf-8"><title>PANDA Agent Hub</title></head>
<body style="font-family: system-ui; background: #151526; color: #e0ddd5;">
<h1>PANDA Agent Hub</h1>
<p>The mailroom UI file is missing. Legacy compose/read-state fallback is retired.</p>
</body></html>"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        return

    def send_json(self, payload: Any, status: int = 200) -> None:
        data = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def trusted_write_request(self) -> bool:
        cookie = SimpleCookie()
        cookie.load(self.headers.get("Cookie", ""))
        cookie_token = cookie.get("pah_write_token")
        token_value = cookie_token.value if cookie_token else ""
        if token_value != WRITE_TOKEN and self.headers.get("X-Agent-Hub-Token") != WRITE_TOKEN:
            return False
        origin = self.headers.get("Origin")
        if origin:
            origin_host = urlparse(origin).netloc
            request_host = self.headers.get("Host", "")
            if origin_host and origin_host != request_host:
                return False
        return True

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/cockpit":
            self.send_json(cockpit_payload())
            return
        if parsed.path == "/api/health":
            self.send_json(health_payload())
            return
        if parsed.path == "/api/tray-status":
            self.send_json(tray_status_payload())
            return
        if parsed.path == "/api/inspector-report":
            self.send_json(inspector_report_payload())
            return
        if parsed.path == "/api/cc-activity":
            self.send_json(cc_activity_payload())
            return
        if parsed.path == "/api/status":
            self.send_json(state())
            return
        if parsed.path == "/api/watcher/status":
            self.send_json({"ok": True, **state()["watcher"]})
            return
        if parsed.path == "/api/watcher/events":
            query = parse_qs(parsed.query)
            limit = int(query.get("limit", ["50"])[0] or "50")
            self.send_json({"ok": True, "events": recent_watcher_events(max(1, min(200, limit)))})
            return
        if parsed.path == "/api/interaction-ledger":
            query = parse_qs(parsed.query)
            limit = int(query.get("limit", ["50"])[0] or "50")
            event_types = {value for value in query.get("event_type", []) if value}
            self.send_json(
                {
                    "ok": True,
                    "path": str(INTERACTION_LEDGER_PATH),
                    "events": recent_interaction_ledger_events(
                        max(1, min(500, limit)),
                        event_types=event_types or None,
                    ),
                }
            )
            return
        if parsed.path == "/api/message":
            query = parse_qs(parsed.query)
            target = Path(query.get("path", [""])[0])
            allowed_roots = (PROJECT_ROOT, PANDA_GALLERY_ROOT)
            if target.exists() and target.is_file() and any(
                str(target).lower().startswith(str(root).lower()) for root in allowed_roots
            ):
                self.send_json({"ok": True, "path": str(target), "content": read_text(target)})
            else:
                self.send_json({"ok": False, "error": "Path not found or outside project"}, 404)
            return
        if parsed.path == "/api/open":
            query = parse_qs(parsed.query)
            target = Path(query.get("path", [""])[0])
            allowed_roots = (PROJECT_ROOT, PANDA_GALLERY_ROOT)
            if target.exists() and any(str(target).lower().startswith(str(root).lower()) for root in allowed_roots):
                os.startfile(target)  # type: ignore[attr-defined]
                self.send_json({"ok": True})
            else:
                self.send_json({"ok": False, "error": "Path not found or outside project"}, 404)
            return
        data = html_page().encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Set-Cookie", f"pah_write_token={WRITE_TOKEN}; HttpOnly; SameSite=Strict; Path=/")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self) -> None:
        parsed_path = urlparse(self.path).path
        if parsed_path not in {
            "/api/test-notification",
            "/api/write-decision-queue",
            "/api/run-diagnostics",
            "/api/clear-diagnostics",
            "/api/cleanup-inbox-accumulation",
            "/api/archive-read-codex-inbox",
            "/api/agent-no-mail-claim",
            "/api/send",
            "/api/create-message",
            "/api/mailroom-canary",
            "/api/message-read-state",
            "/api/mark-all-read",
            "/api/create-route-test",
            "/api/quarantine-message",
            "/api/decision-state",
            "/api/validation-state",
            "/api/archive-selected-alert",
            "/api/thread-archive-state",
            "/api/work-item",
            "/api/dispatch-work-item",
            "/api/watcher-alert",
        }:
            self.send_json({"ok": False, "error": "Not found"}, 404)
            return
        if not self.trusted_write_request():
            self.send_json({"ok": False, "error": "Write token or Origin check failed"}, 403)
            return
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
        if parsed_path == "/api/watcher-alert":
            try:
                record = record_watcher_action(payload)
            except Exception as exc:
                self.send_json({"ok": False, "error": str(exc)}, 400)
                return
            self.send_json({"ok": True, "record": record})
            return
        if parsed_path == "/api/test-notification":
            try:
                self.send_json({"ok": True, **run_notification_scan(manual_test=True)})
            except Exception as exc:
                self.send_json({"ok": False, "error": str(exc)}, 400)
            return
        if parsed_path == "/api/write-decision-queue":
            messages = load_messages()
            decisions = build_decision_queue(messages, write_file=True)
            self.send_json({"ok": True, "path": str(DECISION_QUEUE_PATH), "decisions": len(decisions)})
            return
        if parsed_path == "/api/run-diagnostics":
            diagnostics = run_communication_diagnostics(write_report=True)
            self.send_json({"ok": diagnostics["ok"], **diagnostics})
            return
        if parsed_path == "/api/clear-diagnostics":
            try:
                record = clear_diagnostic_reports(
                    actor=str(payload.get("actor", "codex")),
                    dry_run=bool(payload.get("dry_run", True)),
                )
            except Exception as exc:
                self.send_json({"ok": False, "error": str(exc)}, 400)
                return
            self.send_json({"ok": True, **record})
            return
        if parsed_path == "/api/cleanup-inbox-accumulation":
            try:
                record = cleanup_inbox_accumulation(
                    actor=str(payload.get("actor", "codex")),
                    older_than_hours=int(payload.get("older_than_hours", MESSAGE_RETENTION_HOURS)),
                    dry_run=bool(payload.get("dry_run", True)),
                    mailbox=str(payload.get("mailbox", "all")),
                )
            except Exception as exc:
                self.send_json({"ok": False, "error": str(exc)}, 400)
                return
            self.send_json({"ok": True, **record})
            return
        if parsed_path == "/api/archive-read-codex-inbox":
            try:
                record = archive_read_codex_inbox_messages(
                    actor=str(payload.get("actor", "codex")),
                    dry_run=bool(payload.get("dry_run", False)),
                )
            except Exception as exc:
                self.send_json({"ok": False, "error": str(exc)}, 400)
                return
            self.send_json({"ok": True, **record})
            return
        if parsed_path == "/api/agent-no-mail-claim":
            try:
                record = validate_agent_no_mail_claim(
                    str(payload.get("agent", "")),
                    actor=str(payload.get("actor", "pah")),
                    claim=str(payload.get("claim", "no_mail")),
                    note=str(payload.get("note", "")),
                )
            except Exception as exc:
                self.send_json({"ok": False, "error": str(exc)}, 400)
                return
            self.send_json(record)
            return
        if parsed_path in {"/api/send", "/api/create-message"}:
            try:
                result = create_message(payload)
            except Exception as exc:
                self.send_json({"ok": False, "error": str(exc)}, 400)
                return
            self.send_json({"ok": True, **result})
            return
        if parsed_path == "/api/mailroom-canary":
            try:
                result = run_mailroom_transaction_canary(actor=str(payload.get("actor") or "pah_inspector"))
            except Exception as exc:
                self.send_json({"ok": False, "error": str(exc)}, 500)
                return
            self.send_json(result, 200 if result.get("ok") else 500)
            return
        if parsed_path == "/api/message-read-state":
            try:
                path_value = str(payload.get("path") or payload.get("message_path") or "")
                state_name = str(payload.get("state") or READ_STATE)
                actor = str(payload.get("actor") or "codex")
                result = set_read_state_for_message(path_value, state_name, actor=actor)
            except Exception as exc:
                self.send_json({"ok": False, "error": str(exc)}, 400)
                return
            self.send_json({"ok": True, **result})
            return
        if parsed_path == "/api/mark-all-read":
            try:
                result = mark_all_messages_read(actor=str(payload.get("actor") or "codex"))
            except Exception as exc:
                self.send_json({"ok": False, "error": str(exc)}, 400)
                return
            self.send_json({"ok": True, **result})
            return
        if parsed_path == "/api/create-route-test":
            try:
                record = create_route_test(str(payload.get("route", "")), note=str(payload.get("note", "")))
            except Exception as exc:
                self.send_json({"ok": False, "error": str(exc)}, 400)
                return
            self.send_json({"ok": True, "record": record})
            return
        if parsed_path == "/api/quarantine-message":
            try:
                target = Path(str(payload.get("path", "")))
                reason = str(payload.get("reason", "schema_invalid"))
                confirmed = bool(payload.get("confirmed"))
                record = quarantine_message(target, reason=reason, confirmed=confirmed)
            except Exception as exc:
                self.send_json({"ok": False, "error": str(exc)}, 400)
                return
            self.send_json({"ok": True, "record": record.__dict__})
            return
        if parsed_path == "/api/decision-state":
            try:
                record = set_decision_state(
                    str(payload.get("path", "")),
                    str(payload.get("state", ACTIVE_STATE)),
                    note=str(payload.get("note", "")),
                    actor=str(payload.get("actor", "codex")),
                    title=str(payload.get("title", "")),
                )
            except Exception as exc:
                self.send_json({"ok": False, "error": str(exc)}, 400)
                return
            self.send_json({"ok": True, "record": record})
            return
        if parsed_path == "/api/validation-state":
            try:
                record = set_validation_state(
                    str(payload.get("fingerprint", "")),
                    str(payload.get("state", ACTIVE_VALIDATION_STATE)),
                    note=str(payload.get("note", "")),
                    actor=str(payload.get("actor", "codex")),
                    title=str(payload.get("title", "")),
                    path_value=str(payload.get("path", "")),
                    category=str(payload.get("category", "")),
                    message=str(payload.get("message", "")),
                )
            except Exception as exc:
                self.send_json({"ok": False, "error": str(exc)}, 400)
                return
            self.send_json({"ok": True, "record": record})
            return
        if parsed_path == "/api/archive-selected-alert":
            try:
                record = archive_selected_alert(
                    str(payload.get("path", "")),
                    actor=str(payload.get("actor", "codex")),
                    dry_run=bool(payload.get("dry_run", False)),
                )
            except Exception as exc:
                self.send_json({"ok": False, "error": str(exc)}, 400)
                return
            self.send_json({"ok": True, "record": record})
            return
        if parsed_path == "/api/thread-archive-state":
            try:
                record = set_thread_archive_state(
                    str(payload.get("thread_id", "")),
                    str(payload.get("state", "archived")),
                    reason=str(payload.get("reason", "")),
                    actor=str(payload.get("actor", "codex")),
                )
            except Exception as exc:
                self.send_json({"ok": False, "error": str(exc)}, 400)
                return
            self.send_json({"ok": True, "record": record})
            return
        if parsed_path == "/api/work-item":
            try:
                item_id = str(payload.get("item_id", "")).strip()
                if item_id:
                    record = update_work_item(
                        item_id,
                        owner=str(payload["owner"]) if "owner" in payload else None,
                        state=str(payload["state"]) if "state" in payload else None,
                        priority=str(payload["priority"]) if "priority" in payload else None,
                        summary=str(payload["summary"]) if "summary" in payload else None,
                    )
                else:
                    record = create_work_item(
                        str(payload.get("title", "")),
                        owner=str(payload.get("owner", "codex")),
                        priority=str(payload.get("priority", "normal")),
                        summary=str(payload.get("summary", "")),
                        source=str(payload.get("source", "")),
                    )
            except Exception as exc:
                self.send_json({"ok": False, "error": str(exc)}, 400)
                return
            self.send_json({"ok": True, "record": record})
            return
        if parsed_path == "/api/dispatch-work-item":
            try:
                record = dispatch_work_item(str(payload.get("item_id", "")))
            except Exception as exc:
                self.send_json({"ok": False, "error": str(exc)}, 400)
                return
            self.send_json({"ok": True, "record": record})
            return
        try:
            result = create_message(payload)
        except Exception as exc:
            self.send_json({"ok": False, "error": str(exc)}, 400)
            return
        self.send_json({"ok": True, **result})


def find_free_port(preferred: int, host: str = "127.0.0.1", allow_fallback: bool = True) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind((host, preferred))
            return preferred
        except OSError:
            pass
    if not allow_fallback:
        raise OSError(f"Port {preferred} is already in use on {host}.")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))
        return int(sock.getsockname()[1])


def main() -> None:
    global ALLOW_SIMULATED_INBOUND
    parser = argparse.ArgumentParser(description="Run the CODEX Agent Hub local cockpit.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--no-port-fallback", action="store_true")
    parser.add_argument("--allow-simulated-inbound", action="store_true")
    args = parser.parse_args()
    ALLOW_SIMULATED_INBOUND = args.allow_simulated_inbound
    ensure_runtime_dirs()
    ensure_notification_template()

    port = find_free_port(args.port, args.host, allow_fallback=not args.no_port_fallback)
    server = ThreadingHTTPServer((args.host, port), Handler)
    url = f"http://{args.host}:{port}"
    print(f"PANDA Agent Hub running at {url}", flush=True)
    print(f"Mailbox: {MAILBOX_ROOT}", flush=True)
    print(f"Notification config: {NOTIFICATION_CONFIG_LOCAL_PATH}", flush=True)
    threading.Thread(target=notification_loop, daemon=True).start()
    if not args.no_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    server.serve_forever()


if __name__ == "__main__":
    main()
