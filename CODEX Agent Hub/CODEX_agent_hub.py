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
from email.message import EmailMessage
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
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
UI_PATH = HUB_ROOT / "CODEX_agent_hub_ui.html"
WRITE_TOKEN = secrets.token_urlsafe(32)
ALLOW_SIMULATED_INBOUND = False
NOTIFICATION_LOCK = threading.Lock()
WATCHER_LOCK = threading.Lock()
WATCHER_SNOOZE_DEFAULT_MINUTES = 15
STALE_UNREAD_SECONDS = 60

IMPORTANT_STATUSES = {"Decision Needed", "Response Requested", "Implementation Report"}
IMPORTANT_TYPES = {"dispatch", "complete", "decision", "blocker", "response-request", "implementation"}
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
    msg.from_agent = metadata.get("from", "")
    msg.to_agent = metadata.get("to", "")
    msg.generated = metadata.get("generated", "")
    msg.priority = metadata.get("priority", "")
    msg.action_owner = metadata.get("action-owner", "") or metadata.get("action_owner", "")
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
    for direction, folder in MESSAGE_DIRS:
        if not folder.exists():
            continue
        for path in folder.glob("*.md"):
            try:
                messages.append(parse_message(path, direction))
            except OSError:
                continue
    messages.sort(key=lambda item: item.modified, reverse=True)
    return messages


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
        if not config.get("enabled"):
            return {"sent": 0, "enabled": False}

        messages = load_messages()
        message_by_path = {str(msg.path): msg for msg in messages}
        decisions = build_decision_queue(messages, write_file=False)
        enabled_kinds = {key for key, enabled in dict(config.get("notify_on", {})).items() if enabled}
        events = [event for event in attention_events(messages, decisions) if event["kind"] in enabled_kinds]

        sent = dict(state_data.get("sent", {}))
        if not state_data.get("baseline_initialized") and not config.get("send_existing_on_start"):
            for event in events:
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
            return {"sent": 0, "baseline_initialized": True}

        cooldown_seconds = max(0, int(config.get("cooldown_minutes", 30))) * 60
        last_sent_epoch = float(state_data.get("last_sent_epoch", 0) or 0)
        sent_count = 0
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
            if cooldown_seconds and now - last_sent_epoch < cooldown_seconds:
                continue
            try:
                result = send_notification(config, event["subject"], event["body"])
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
                sent_count += 1
                append_notification_log({"time": state_data["last_sent_at"], "event": event, "result": result})
            except (HTTPError, URLError, OSError, RuntimeError, ValueError, smtplib.SMTPException) as exc:
                state_data["last_error"] = str(exc)
                append_notification_log({"time": datetime.now().isoformat(timespec="seconds"), "event": event, "error": str(exc)})
                break
        state_data["sent"] = sent
        state_data["baseline_initialized"] = True
        write_json(NOTIFICATION_STATE_PATH, state_data)
        return {"sent": sent_count, "enabled": True}


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


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", value.strip()).strip("-").lower()
    return slug[:42] or "message"


def create_message(payload: dict[str, Any]) -> dict[str, str]:
    route = str(payload.get("route", "codex_to_claude"))
    subject = compact(str(payload.get("subject", "Agent Hub message")).strip(), 90)
    body = str(payload.get("body", "")).strip()
    ui_status = str(payload.get("status", "Info")).strip() or "Info"
    thread_id = str(payload.get("thread_id", "")).strip()
    reply_to = str(payload.get("reply_to", "")).strip()

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

    inbox.mkdir(parents=True, exist_ok=True)
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
    atomic_write_text(path, text)

    if ui_status in IMPORTANT_STATUSES or "request" in ui_status.lower() or "decision" in ui_status.lower():
        ledger_line = (
            f"{generated} | {from_agent}->{to_agent} | {ui_status.lower()} | "
            f"{subject} | {inbox.name}\\{filename} | {path}\n"
        )
        atomic_append_text(LEDGER_PATH, ledger_line)

    return {"path": str(path), "message_id": message_id}


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
    return set_message_read_state(msg.path, msg.message_id, msg.body, state_name, actor=actor)


def mark_all_messages_read(actor: str = "codex") -> dict[str, Any]:
    messages = load_messages()
    for msg in messages:
        set_message_read_state(msg.path, msg.message_id, msg.body, READ_STATE, actor=actor)
    return {"count": len(messages), "state_path": str(READ_STATE_PATH)}


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


def archive_read_codex_inbox_messages(actor: str = "codex", dry_run: bool = False) -> dict[str, Any]:
    read_state_data = load_read_state()
    codex_inbox = CODEX_INBOX.resolve()
    archive_dir = CODEX_ARCHIVE / "Read Messages" / datetime.now().strftime("%Y%m%d")
    candidates: list[Message] = []
    skipped_waiting = 0
    for msg in load_messages():
        try:
            if msg.path.parent.resolve() != codex_inbox:
                continue
        except OSError:
            continue
        if msg.is_waiting_on_darrin:
            skipped_waiting += 1
            continue
        read_status = message_read_status(msg.path, msg.message_id, msg.body, read_state_data)
        if read_status["unread"]:
            continue
        candidates.append(msg)

    moved: list[dict[str, str]] = []
    if not dry_run:
        archive_dir.mkdir(parents=True, exist_ok=True)
    for msg in candidates:
        destination = unique_destination(archive_dir / msg.path.name)
        record = {
            "message_id": msg.message_id,
            "thread_id": msg.stable_thread,
            "from": msg.from_agent,
            "to": msg.to_agent,
            "source": str(msg.path),
            "destination": str(destination),
        }
        if not dry_run:
            shutil.move(str(msg.path), str(destination))
        moved.append(record)

    return {
        "actor": actor.strip() or "codex",
        "dry_run": dry_run,
        "count": len(moved),
        "skipped_waiting_on_darrin": skipped_waiting,
        "archive_dir": str(archive_dir),
        "moved": moved,
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
        result = subprocess.run(
            ["git", "-C", str(PROJECT_ROOT), "status", "--short", "--branch"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        return {"ok": str(result.returncode == 0), "text": result.stdout.strip() or result.stderr.strip()}
    except Exception as exc:  # pragma: no cover - status panel should degrade gently
        return {"ok": "False", "text": str(exc)}


def state() -> dict[str, Any]:
    messages = load_messages()
    read_state_data = load_read_state()
    archive_state_data = load_thread_archive_state()
    decisions = build_decision_queue(messages, write_file=False)
    all_decisions = build_decision_queue(messages, write_file=False, include_inactive=True)
    validation = validate_mailbox(messages)
    validation_actionable, validation_inactive = apply_validation_state(validation)
    validation_summary = summarize_validation(validation)
    all_threads = build_threads(messages, read_state_data, archive_state_data)
    active_threads = [thread for thread in all_threads if not thread.get("archived")]
    archived_threads = [thread for thread in all_threads if thread.get("archived")]
    unread_messages = sum(
        1 for msg in messages if message_read_status(msg.path, msg.message_id, msg.body, read_state_data)["unread"]
    )
    diagnostics = run_communication_diagnostics(write_report=False)
    route_tests = route_test_status(refresh=True)
    work_board = work_board_status()
    approvals = approval_status()
    adapters = adapter_status()
    quarantine = quarantine_status()
    decision_state = decision_state_summary()
    agent_status = build_agent_status(messages, read_state_data, work_board, decisions)
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
        },
        "latest": [message_to_json(msg, read_state_data) for msg in messages[:40]],
        "mailboxes": build_mailbox_overview(messages, read_state_data),
        "agent_status": agent_status,
        "watcher": watcher,
        "threads": active_threads[:80],
        "archived_threads": archived_threads[:80],
        "decisions": decisions,
        "decision_history": [item for item in all_decisions if item.get("decision_state") != ACTIVE_STATE],
        "decision_state": decision_state,
        "validation": validation,
        "validation_actionable": validation_actionable,
        "validation_inactive": validation_inactive,
        "validation_summary": validation_summary,
        "validation_state": validation_state_summary(),
        "read_state": read_state_summary(read_state_data),
        "thread_archive": thread_archive_summary(archive_state_data),
        "diagnostics": diagnostics,
        "route_tests": route_tests,
        "work_board": work_board,
        "approvals": approvals,
        "adapters": adapters,
        "quarantine": quarantine,
        "notifications": notification_status(),
        "git": git_status(),
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
            "latency_ms": 0,
        }
    )
    return rows


def summarize_cockpit_routes(routes: list[dict[str, Any]]) -> dict[str, Any]:
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
    return {**counts, "label": label, "severity": severity}


def cockpit_feed_item(row: dict[str, Any]) -> dict[str, Any]:
    is_stale = bool(row.get("stale_unread"))
    badges = [{"kind": "status", "label": str(label)} for label in row.get("status_badges", [])[:3]]
    if is_stale:
        badges.insert(0, {"kind": "wake", "label": "needs wake-up"})
    wake_label = str(row.get("wake_candidate_label", ""))
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
        "wake_candidate_agent": row.get("wake_candidate_agent", ""),
        "wake_candidate_label": wake_label,
        "badges": badges,
        "message_path": row.get("path", ""),
        "summary": row.get("summary", ""),
    }


def cockpit_selected_thread(
    status_data: dict[str, Any], feed: list[dict[str, Any]], wake_candidates: list[dict[str, Any]] | None = None
) -> dict[str, Any]:
    decisions = status_data.get("decisions", [])
    decision = decisions[0] if decisions else {}
    wake_item = (wake_candidates or [None])[0] or {}
    selected = wake_item or decision or (feed[0] if feed else {})
    title = str(selected.get("title", "No active thread"))
    path_value = str(selected.get("path") or selected.get("message_path") or "")
    thread_id = str(selected.get("thread_id") or selected.get("id") or safe_slug(title))
    route_id = str(selected.get("route_id") or route_id_for_direction(str(selected.get("direction", ""))))
    if wake_item:
        state = "needs_wake"
        owner = str(wake_item.get("wake_candidate_label") or "Agent")
        source = "Unread over 60 seconds"
        next_action = f"Wake {owner}"
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
            {"label": "State", "value": "Needs wake-up" if wake_item else "Waiting on Darrin" if decisions else "Active"},
            {"label": "Next action", "value": next_action},
            {"label": "Writes", "value": "None in read-only v1"},
            {"label": "Wake model", "value": "Copy line only"},
        ],
        "cards": [
            {
                "title": "Unread alert" if wake_item else "Current gate" if decisions else "Latest message",
                "body": str(selected.get("summary", "No summary available.")),
            },
            {
                "title": "Read-only v1",
                "body": "Compose, send, permission grants, and watcher startup are disabled in this cockpit slice.",
            },
            {
                "title": "Safety boundary",
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
        if agent.get("id") == "darrin":
            count_value = status_data.get("counts", {}).get("decisions", 0)
            count_label = "decision" if count_value == 1 else "decisions"
        elif agent.get("waiting", 0):
            count_value = agent.get("waiting", 0)
            count_label = "queued"
        else:
            count_value = agent.get("unread", 0)
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
                "meter_pct": min(100, max(10, int(count_value or 1) * 16)),
                "meter_color": "warn" if state_name in {"waiting", "needs_wake"} else "err" if state_name == "needs_attention" else "ok",
                "last_activity_iso": str((agent.get("current_work") or {}).get("modified", "")),
                "pulse": state_name == "active",
            }
        )
    return rows


def cockpit_action_queue(
    feed: list[dict[str, Any]], decisions: list[dict[str, Any]], limit: int = 12
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in feed:
        key = str(item.get("id") or item.get("message_path"))
        if item.get("stale_unread"):
            seen.add(key)
            label = str(item.get("wake_candidate_label") or "agent")
            rows.append(
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
        rows.append(
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
            }
        )
    for item in feed:
        key = str(item.get("id") or item.get("message_path"))
        if key in seen or not item.get("unread"):
            continue
        rows.append(
            {
                "id": key,
                "kind": "unread",
                "severity": "open",
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
    return rows[:limit]


def cockpit_payload() -> dict[str, Any]:
    status_data = state()
    generated_at = str(status_data.get("generated_at", datetime.now().isoformat(timespec="seconds")))
    routes = build_cockpit_routes(status_data)
    route_summary = summarize_cockpit_routes(routes)
    feed = [cockpit_feed_item(row) for row in status_data.get("latest", [])[:24]]
    decisions = cockpit_decisions(status_data)
    wake_candidates = [item for item in feed if item.get("stale_unread")]
    action_queue = cockpit_action_queue(feed, decisions)
    selected_thread = cockpit_selected_thread(status_data, feed, wake_candidates)
    diagnostics = status_data.get("diagnostics", {})
    validation_summary = status_data.get("validation_summary", {})
    git = status_data.get("git", {})
    git_text = str(git.get("text", ""))
    return {
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
                "decisions_needed": status_data.get("counts", {}).get("decisions", 0),
                "actionable_checks": status_data.get("counts", {}).get("actionable_validation_issues", 0),
            },
        },
        "agents": cockpit_agents(status_data),
        "action_queue": action_queue,
        "wake_candidates": wake_candidates,
        "feed": feed,
        "selected_thread": selected_thread,
        "decisions": decisions,
        "routes": routes,
        "wake": {
            "target_agent": wake_candidates[0].get("wake_candidate_agent", "claude_code") if wake_candidates else "claude_code",
            "line": action_queue[0].get("wake_line") if action_queue and action_queue[0].get("wake_line") else f"Read {selected_thread.get('id', 'the PAH thread')} and reply to CODEX.",
            "route_status": "wake_candidate" if wake_candidates else "held" if route_summary["held"] else "pass",
            "last_copy_iso": "",
            "direct_wake_supported": False,
            "safety_label": f"{len(wake_candidates)} unread over 60s. Copy line only." if wake_candidates else "Copy line only; Darrin pastes into Claude Code.",
        },
        "diagnostics": {
            "ok": bool(diagnostics.get("ok")),
            "checks_total": len(diagnostics.get("checks", [])),
            "checks_pass": sum(1 for check in diagnostics.get("checks", []) if check.get("ok")),
            "checks_warn": sum(1 for check in diagnostics.get("checks", []) if not check.get("ok") and check.get("severity") == "warning"),
            "checks_fail": sum(1 for check in diagnostics.get("checks", []) if not check.get("ok") and check.get("severity") != "warning"),
            "actionable_validation_issues": validation_summary.get("actionable", 0),
            "last_run_iso": generated_at,
        },
        "git": {
            "branch": "main",
            "tracking": "origin/main",
            "clean": "## main...origin/main" in git_text and "\n" not in git_text,
            "status_label": "main synced with origin" if "## main...origin/main" in git_text and "\n" not in git_text else git_text,
            "last_commit": "",
        },
        "read_only_actions": [
            {"id": "refresh", "label": "Refresh", "enabled": True},
            {"id": "validate", "label": "Validate", "enabled": True},
            {"id": "backup", "label": "Backup", "enabled": True},
            {"id": "compose", "label": "Compose", "enabled": False, "reason": "disabled in read-only v1"},
            {"id": "send", "label": "Send", "enabled": False, "reason": "no draft staged in read-only v1"},
        ],
    }


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
    stale = int(counts.get("stale_unread", 0) or 0)
    unread = int(counts.get("unread", 0) or 0)
    diag_problems = int(diagnostics.get("checks_warn", 0) or 0) + int(diagnostics.get("checks_fail", 0) or 0)
    oldest = max((int(item.get("age_seconds", 0) or 0) for item in wake_candidates), default=0)
    target_counts: dict[str, int] = {}
    for item in wake_candidates:
        target = str(item.get("wake_candidate_label") or item.get("wake_candidate_agent") or "Agent")
        target_counts[target] = target_counts.get(target, 0) + 1

    if stale:
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


def message_to_json(msg: Message, read_state_data: dict[str, Any] | None = None) -> dict[str, Any]:
    read_status = message_read_status(msg.path, msg.message_id, msg.body, read_state_data)
    age_seconds = max(0, int(time.time() - msg.modified))
    stale_unread = bool(read_status["unread"] and age_seconds >= STALE_UNREAD_SECONDS)
    wake_candidate_agent = safe_slug(msg.to_agent).replace("-", "_") if msg.to_agent else ""
    wake_candidate_label = msg.to_agent or ""
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
        "wake_candidate_agent": wake_candidate_agent,
        "wake_candidate_label": wake_candidate_label,
        "content_changed_since_read": read_status["content_changed"],
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


def build_agent_status(
    messages: list[Message],
    read_state_data: dict[str, Any] | None,
    work_board: dict[str, Any],
    decisions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    now = datetime.now().timestamp()
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
            inbound = [msg for msg in messages if msg.is_waiting_on_darrin]
            outbound: list[Message] = []
            waiting_messages = inbound
            agent_work = decisions[:4]
        else:
            inbound = [msg for msg in messages if msg.to_agent == agent_id]
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

        if agent_id == "darrin" and decisions:
            state = "needs_attention"
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
        return read_text(UI_PATH).replace("__WRITE_TOKEN__", WRITE_TOKEN)
    return HTML_PAGE.replace("__WRITE_TOKEN__", WRITE_TOKEN)


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
        if self.headers.get("X-Agent-Hub-Token") != WRITE_TOKEN:
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
        if parsed.path == "/api/tray-status":
            self.send_json(tray_status_payload())
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
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self) -> None:
        parsed_path = urlparse(self.path).path
        if parsed_path not in {
            "/api/send",
            "/api/test-notification",
            "/api/write-decision-queue",
            "/api/run-diagnostics",
            "/api/create-route-test",
            "/api/quarantine-message",
            "/api/decision-state",
            "/api/validation-state",
            "/api/message-read-state",
            "/api/mark-all-read",
            "/api/archive-read-codex-inbox",
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
        if parsed_path == "/api/message-read-state":
            try:
                record = set_read_state_for_message(
                    str(payload.get("path", "")),
                    str(payload.get("state", READ_STATE)),
                    actor=str(payload.get("actor", "codex")),
                )
            except Exception as exc:
                self.send_json({"ok": False, "error": str(exc)}, 400)
                return
            self.send_json({"ok": True, "record": record})
            return
        if parsed_path == "/api/mark-all-read":
            try:
                record = mark_all_messages_read(actor=str(payload.get("actor", "codex")))
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


def find_free_port(preferred: int) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        if sock.connect_ex(("127.0.0.1", preferred)) != 0:
            return preferred
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def main() -> None:
    global ALLOW_SIMULATED_INBOUND
    parser = argparse.ArgumentParser(description="Run the CODEX Agent Hub local cockpit.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--allow-simulated-inbound", action="store_true")
    args = parser.parse_args()
    ALLOW_SIMULATED_INBOUND = args.allow_simulated_inbound
    ensure_runtime_dirs()
    ensure_notification_template()

    port = find_free_port(args.port)
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
