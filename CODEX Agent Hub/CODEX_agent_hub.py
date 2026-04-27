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
from pah_core.schema import (
    content_hash,
    extract_message_metadata,
    metadata_waits_on_darrin,
    render_message_markdown,
    validate_message_text,
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
from pah_mailbox.paths import (
    CLAUDE_CODE_INBOX,
    CLAUDE_CODE_INBOX_LEGACY,
    CLAUDE_INBOX,
    CLAUDE_SENT,
    CODEX_INBOX,
    CODEX_SENT,
    CONFIG_DIR,
    DECISION_QUEUE_PATH,
    HUB_ROOT,
    LEDGER_PATH,
    MAILBOX_ROOT,
    MESSAGE_DIRS,
    NOTIFICATIONS_DIR,
    PROJECT_ROOT,
    REPORTS_DIR,
    ensure_runtime_dirs,
)
from pah_mailbox.quarantine import quarantine_message
from pah_notifications.desktop import desktop_popup_status
from pah_security.approvals import approval_status

NOTIFICATION_CONFIG_TEMPLATE_PATH = CONFIG_DIR / "CODEX_notification_config.template.json"
NOTIFICATION_CONFIG_LOCAL_PATH = CONFIG_DIR / "CODEX_notification_config.local.json"
NOTIFICATION_STATE_PATH = NOTIFICATIONS_DIR / "CODEX_notification_state.local.json"
NOTIFICATION_LOG_PATH = NOTIFICATIONS_DIR / "CODEX_notification_log.jsonl"
WRITE_TOKEN = secrets.token_urlsafe(32)
ALLOW_SIMULATED_INBOUND = False
NOTIFICATION_LOCK = threading.Lock()

IMPORTANT_STATUSES = {"Decision Needed", "Response Requested", "Implementation Report"}
IMPORTANT_TYPES = {"dispatch", "complete", "decision", "blocker", "response-request", "implementation"}

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


def build_threads(messages: list[Message]) -> list[dict[str, Any]]:
    grouped: dict[str, list[Message]] = {}
    for msg in messages:
        grouped.setdefault(msg.stable_thread, []).append(msg)
    rows: list[dict[str, Any]] = []
    for thread_id, items in grouped.items():
        items.sort(key=lambda item: item.modified)
        latest = items[-1]
        status = latest.thread_status or latest.status or ("Open" if latest.is_request else "Info")
        rows.append(
            {
                "thread_id": thread_id,
                "count": len(items),
                "latest_title": latest.title,
                "latest_direction": latest.direction,
                "latest_path": str(latest.path),
                "latest_modified": latest.modified,
                "status": status,
                "owner": latest.action_owner or latest.to_agent or "",
                "waiting_on_darrin": latest.is_waiting_on_darrin,
                "summary": latest.summary or latest.body_preview,
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
            add("warning", msg, "Missing Message-ID")
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
            if schema_issue.message == "Missing message_id / Message-ID" and not msg.message_id:
                continue
            add(schema_issue.level, msg, schema_issue.message)

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
    return issues[:100]


def validation_category(text: str) -> str:
    lowered = text.lower()
    if "provenance conflict" in lowered or "duplicate message-id" in lowered:
        return "provenance"
    if "message-id" in lowered or "message_id" in lowered:
        return "identity"
    if "schema" in lowered or "unsupported" in lowered:
        return "schema"
    if "ledger" in lowered:
        return "ledger"
    if "reply-to" in lowered:
        return "threading"
    if "referenced path" in lowered or "path not found" in lowered:
        return "path_reference"
    return "general"


def validation_is_actionable(level: str, category: str) -> bool:
    if level == "error":
        return True
    return category in {"provenance", "ledger"}


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


def load_notification_config() -> dict[str, Any]:
    ensure_notification_template()
    local = read_json(NOTIFICATION_CONFIG_LOCAL_PATH, {})
    return deep_merge(DEFAULT_NOTIFICATION_CONFIG, local)


def notification_status() -> dict[str, Any]:
    config = load_notification_config()
    state_data = read_json(NOTIFICATION_STATE_PATH, {})
    provider = str(config.get("provider", "log_only"))
    configured = provider == "log_only" or provider_is_configured(config, provider)
    return {
        "enabled": bool(config.get("enabled")),
        "provider": provider,
        "configured": configured,
        "config_path": str(NOTIFICATION_CONFIG_LOCAL_PATH),
        "template_path": str(NOTIFICATION_CONFIG_TEMPLATE_PATH),
        "log_path": str(NOTIFICATION_LOG_PATH),
        "last_sent_at": state_data.get("last_sent_at", ""),
        "last_error": state_data.get("last_error", ""),
        "baseline_initialized": bool(state_data.get("baseline_initialized")),
        "desktop_popups": desktop_popup_status(config),
    }


def quarantine_status() -> dict[str, Any]:
    from pah_mailbox.paths import QUARANTINE_DIR

    quarantined = list(QUARANTINE_DIR.glob("*.md")) if QUARANTINE_DIR.exists() else []
    tombstones = list(MAILBOX_ROOT.glob("**/*.pah_tombstone.json"))
    return {
        "quarantine_dir": str(QUARANTINE_DIR),
        "messages": len(quarantined),
        "tombstones": len(tombstones),
        "automatic_moves": False,
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
    return provider == "log_only"


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
            state_data["last_sent_at"] = datetime.now().isoformat(timespec="seconds")
            state_data["last_error"] = ""
            write_json(NOTIFICATION_STATE_PATH, state_data)
            append_notification_log({"time": state_data["last_sent_at"], "manual_test": True, "result": result})
            return {"sent": 1, "result": result}
        if not config.get("enabled"):
            return {"sent": 0, "enabled": False}

        messages = load_messages()
        decisions = build_decision_queue(messages, write_file=False)
        enabled_kinds = {key for key, enabled in dict(config.get("notify_on", {})).items() if enabled}
        events = [event for event in attention_events(messages, decisions) if event["kind"] in enabled_kinds]

        sent = dict(state_data.get("sent", {}))
        if not state_data.get("baseline_initialized") and not config.get("send_existing_on_start"):
            for event in events:
                sent[event["fingerprint"]] = {"baseline": True, "time": datetime.now().isoformat(timespec="seconds")}
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
            if cooldown_seconds and now - last_sent_epoch < cooldown_seconds:
                continue
            try:
                result = send_notification(config, event["subject"], event["body"])
                sent[event["fingerprint"]] = {"time": datetime.now().isoformat(timespec="seconds"), "path": event["path"]}
                state_data["last_sent_at"] = sent[event["fingerprint"]]["time"]
                state_data["last_sent_epoch"] = now
                state_data["last_error"] = ""
                sent_count += 1
                append_notification_log({"time": state_data["last_sent_at"], "event": event, "result": result})
            except (HTTPError, URLError, OSError, RuntimeError, smtplib.SMTPException) as exc:
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
    decisions = build_decision_queue(messages, write_file=False)
    all_decisions = build_decision_queue(messages, write_file=False, include_inactive=True)
    validation = validate_mailbox(messages)
    validation_actionable, validation_inactive = apply_validation_state(validation)
    validation_summary = summarize_validation(validation)
    threads = build_threads(messages)
    diagnostics = run_communication_diagnostics(write_report=False)
    route_tests = route_test_status(refresh=True)
    work_board = work_board_status()
    approvals = approval_status()
    adapters = adapter_status()
    quarantine = quarantine_status()
    decision_state = decision_state_summary()
    return {
        "project_root": str(PROJECT_ROOT),
        "mailbox_root": str(MAILBOX_ROOT),
        "decision_queue_path": str(DECISION_QUEUE_PATH),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "counts": {
            "messages": len(messages),
            "threads": len(threads),
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
        "latest": [message_to_json(msg) for msg in messages[:40]],
        "threads": threads[:80],
        "decisions": decisions,
        "decision_history": [item for item in all_decisions if item.get("decision_state") != ACTIVE_STATE],
        "decision_state": decision_state,
        "validation": validation,
        "validation_actionable": validation_actionable,
        "validation_inactive": validation_inactive,
        "validation_summary": validation_summary,
        "validation_state": validation_state_summary(),
        "diagnostics": diagnostics,
        "route_tests": route_tests,
        "work_board": work_board,
        "approvals": approvals,
        "adapters": adapters,
        "quarantine": quarantine,
        "notifications": notification_status(),
        "git": git_status(),
    }


def message_to_json(msg: Message) -> dict[str, Any]:
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
        "summary": msg.summary or msg.body_preview,
    }


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
.item-title { display: flex; justify-content: space-between; gap: 10px; font-weight: 650; }
.pill { display: inline-block; border: 1px solid var(--line); border-radius: 999px; padding: 2px 7px; color: var(--muted); font-size: 11px; white-space: nowrap; }
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
    <div id="latest" class="pane"><div class="list" id="latestList"></div></div>
    <div id="threads" class="pane hidden"><div class="list" id="threadList"></div></div>
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
      <p class="muted">Uses local notification config. Secrets stay in ignored <code>*.local.json</code>.</p>
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
  list('latestList', data.latest, m => item(m.title, m.status || m.direction, m.summary, m.path));
  list('threadList', data.threads, t => item(t.thread_id, t.status, t.summary, t.latest_path));
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
    {title:'Approval records', pill:data.approvals.records, summary:`active ${data.approvals.active}, invalid ${data.approvals.invalid}, revoked ${data.approvals.revoked}, expired ${data.approvals.expired}`, path:data.approvals.records_path},
    {title:'Required fields', pill:'schema', summary:data.approvals.required_fields.join(', '), path:''}
  ], a => item(a.title, a.pill, a.summary, a.path));
  list('adapterList', data.adapters.adapters, a => item(a.display_name, a.enabled ? 'ENABLED' : 'DISABLED', `${a.safety_status} · ${a.notes}`, a.adapter_id));
  list('quarantineList', [
    {title:'Quarantine', pill:data.quarantine.automatic_moves ? 'AUTO' : 'EXPLICIT', summary:`${data.quarantine.messages} quarantined messages, ${data.quarantine.tombstones} tombstones. ${data.quarantine.detail}`, path:data.quarantine.quarantine_dir}
  ], q => item(q.title, q.pill, q.summary, q.path));
}
function list(id, rows, fn) { document.getElementById(id).innerHTML = rows.length ? rows.map(fn).join('') : '<div class="item muted">Nothing to show.</div>'; }
function item(title, pill, summary, path) { return `<div class="item"><div class="item-title"><span>${esc(title)}</span><span class="pill">${esc(pill)}</span></div><div class="summary">${esc(summary || '')}</div><div class="path">${esc(path || '')}</div></div>`; }
function decisionItem(d) {
  return `<div class="item"><div class="item-title"><span>${esc(d.title)}</span><span class="pill">${esc(d.status || 'Decision')}</span></div><div class="summary">${esc(d.summary || '')}</div><div class="path">${esc(d.path || '')}</div><p><button onclick="setDecisionState('${encodeURIComponent(d.path)}','resolved')">Resolved</button> <button onclick="setDecisionState('${encodeURIComponent(d.path)}','superseded')">Superseded</button> <button onclick="setDecisionState('${encodeURIComponent(d.path)}','dismissed')">Dismiss</button></p></div>`;
}
function validationItem(v) {
  const payload = encodeURIComponent(JSON.stringify({fingerprint:v.fingerprint, path:v.path, category:v.category, message:v.message, title:v.title}));
  return `<div class="item"><div class="item-title"><span>${esc(v.message)}</span><span class="pill">${esc(v.level)} · ${esc(v.category)}</span></div><div class="summary">${esc(v.title || '')}</div><div class="path">${esc(v.path || '')}</div><p><button onclick="setValidationState('${payload}','resolved')">Resolved</button> <button onclick="setValidationState('${payload}','accepted_legacy')">Accept Legacy</button> <button onclick="setValidationState('${payload}','dismissed')">Dismiss</button></p></div>`;
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
  const popup = n.desktop_popups?.enabled ? '<span class="good">enabled</span>' : '<span class="muted">tray-ready</span>';
  return `<div class="metric"><span>Status</span><strong>${enabled}</strong></div><div class="metric"><span>Provider</span><span>${esc(n.provider)} · ${configured}</span></div><div class="metric"><span>Desktop popups</span><span>${popup}</span></div><div class="metric"><span>Last sent</span><span class="muted">${esc(n.last_sent_at || 'never')}</span></div><div class="metric"><span>Config</span><span class="path">${esc(n.config_path)}</span></div>${n.last_error ? `<div class="bad">${esc(n.last_error)}</div>` : ''}`;
}
function validationSummaryBlock(v) {
  const cats = Object.entries(v.by_category || {}).map(([k,val]) => `${esc(k)} ${val}`).join(' · ');
  return `<div class="metric"><span>Actionable</span><strong>${esc(v.actionable)}</strong></div><div class="metric"><span>Legacy/info</span><span>${esc(v.informational_or_legacy)}</span></div><div class="metric"><span>Categories</span><span class="muted">${cats || 'none'}</span></div>`;
}
document.querySelectorAll('.tab').forEach(btn => btn.addEventListener('click', () => { document.querySelectorAll('.tab').forEach(b => b.classList.remove('active')); btn.classList.add('active'); document.querySelectorAll('.pane').forEach(p => p.classList.add('hidden')); document.getElementById(btn.dataset.tab).classList.remove('hidden'); }));
document.getElementById('refresh').onclick = load;
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
load(); setInterval(load, 8000);
</script>
</body>
</html>"""


def html_page() -> str:
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
        if parsed.path == "/api/status":
            self.send_json(state())
            return
        if parsed.path == "/api/open":
            query = parse_qs(parsed.query)
            target = Path(query.get("path", [""])[0])
            if target.exists() and str(target).lower().startswith(str(PROJECT_ROOT).lower()):
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
            "/api/work-item",
            "/api/dispatch-work-item",
        }:
            self.send_json({"ok": False, "error": "Not found"}, 404)
            return
        if not self.trusted_write_request():
            self.send_json({"ok": False, "error": "Write token or Origin check failed"}, 403)
            return
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
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
                reason = str(payload.get("reason", "manual_quarantine"))
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
