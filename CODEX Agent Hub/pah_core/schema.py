"""Message schema parsing, rendering, and validation for PANDA Agent Hub."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pah_core import MESSAGE_SCHEMA_VERSION
from pah_core.participants import PARTICIPANTS, canonical_participant


STATUS_VALUES = {
    "draft",
    "open",
    "in_progress",
    "blocked",
    "review_complete",
    "complete",
    "shipped",
    "closed",
    "rejected",
}
THREAD_STATUS_VALUES = {
    "active",
    "waiting_on_agent",
    "waiting_on_darrin",
    "blocked",
    "resolved",
    "archived",
}
PRIORITY_VALUES = {"low", "normal", "high", "urgent"}
MESSAGE_TYPES = {
    "coordination",
    "dispatch",
    "response_request",
    "decision_request",
    "decision_record",
    "implementation_report",
    "diagnostic_result",
    "system_event",
}
APPROVAL_BOUNDARIES = {
    "coordination_only",
    "codex_workspace_write_allowed",
    "local_mailbox_write_allowed",
    "external_send_requires_darrin",
    "paid_provider_requires_darrin",
    "credentials_requires_darrin",
    "panda_gallery_write_requires_darrin",
    "protected_action_requires_darrin",
}
REQUIRED_FRONTMATTER_FIELDS = {
    "schema_version",
    "message_id",
    "thread_id",
    "created_at",
    "from",
    "to",
    "type",
    "priority",
    "status",
    "thread_status",
    "approval_boundary",
    "requires_darrin_decision",
}

TOKEN_RE = re.compile(r"^[A-Za-z][A-Za-z0-9 -]{1,40}:\s*(.*)$")
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", re.DOTALL)


@dataclass(frozen=True)
class SchemaIssue:
    level: str
    message: str


def normalize_key(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def normalize_status(value: str) -> str:
    mapping = {
        "info": "open",
        "response requested": "open",
        "decision needed": "blocked",
        "implementation report": "review_complete",
        "waiting on darrin": "blocked",
    }
    return mapping.get(str(value or "").strip().lower(), str(value or "").strip().lower())


def normalize_thread_status(value: str) -> str:
    mapping = {
        "open": "active",
        "info": "active",
        "response requested": "waiting_on_agent",
        "decision needed": "waiting_on_darrin",
        "waiting on darrin": "waiting_on_darrin",
        "waiting_on_darrin": "waiting_on_darrin",
    }
    return mapping.get(str(value or "").strip().lower(), str(value or "").strip().lower())


def coerce_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"true", "yes", "1", "y"}


def scalar_from_text(value: str) -> Any:
    stripped = value.strip()
    if stripped.lower() in {"true", "false"}:
        return stripped.lower() == "true"
    if stripped.startswith("[") and stripped.endswith("]"):
        items = stripped[1:-1].strip()
        if not items:
            return []
        return [item.strip().strip("'\"") for item in items.split(",")]
    return stripped.strip("'\"")


def parse_frontmatter(text: str) -> tuple[dict[str, Any], bool]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, False
    metadata: dict[str, Any] = {}
    lines = match.group(1).splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip() or line.lstrip().startswith("#"):
            index += 1
            continue
        if ":" not in line:
            index += 1
            continue
        key, raw_value = line.split(":", 1)
        normalized = normalize_key(key)
        value = raw_value.strip()
        if value:
            metadata[normalized] = scalar_from_text(value)
            index += 1
            continue
        collected: list[str] = []
        probe = index + 1
        while probe < len(lines) and lines[probe].startswith("  -"):
            collected.append(lines[probe].split("-", 1)[1].strip().strip("'\""))
            probe += 1
        metadata[normalized] = collected
        index = probe
    return metadata, True


def parse_legacy_metadata(text: str) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    lines = text.splitlines()
    for index, line in enumerate(lines[:80]):
        stripped = line.strip()
        if stripped.startswith("Reply-To:"):
            inline_reply = stripped.split(":", 1)[1].strip()
            if inline_reply and inline_reply.lower() not in {"--", "none", "n/a"}:
                metadata["reply_to"] = [inline_reply]
            else:
                replies: list[str] = []
                for reply_line in lines[index + 1 : index + 12]:
                    reply = reply_line.strip()
                    if not reply:
                        continue
                    if TOKEN_RE.match(reply):
                        break
                    if reply.startswith("-"):
                        replies.append(reply[1:].strip())
                metadata["reply_to"] = replies
            continue
        match = TOKEN_RE.match(stripped)
        if match:
            metadata[normalize_key(line.split(":", 1)[0])] = match.group(1).strip()
    return metadata


def extract_message_metadata(text: str) -> dict[str, Any]:
    legacy = parse_legacy_metadata(text)
    frontmatter, has_frontmatter = parse_frontmatter(text)
    metadata = {**legacy, **frontmatter}
    metadata["_has_frontmatter"] = has_frontmatter
    if "from" in metadata:
        metadata["from"] = canonical_participant(str(metadata["from"]))
    if "to" in metadata:
        metadata["to"] = canonical_participant(str(metadata["to"]))
    if "thread_status" in metadata:
        metadata["thread_status"] = normalize_thread_status(str(metadata["thread_status"]))
    if "message_id" not in metadata and "message_id" in legacy:
        metadata["message_id"] = legacy["message_id"]
    return metadata


def metadata_waits_on_darrin(metadata: dict[str, Any]) -> bool:
    if coerce_bool(metadata.get("requires_darrin_decision")):
        return True
    if normalize_thread_status(str(metadata.get("thread_status", ""))) == "waiting_on_darrin":
        return True
    if str(metadata.get("priority", "")).strip().lower() == "urgent":
        return True
    return "_requires_darrin" in str(metadata.get("approval_boundary", "")).strip().lower()


def validate_message_text(text: str, path_name: str = "") -> list[SchemaIssue]:
    metadata = extract_message_metadata(text)
    issues: list[SchemaIssue] = []
    has_frontmatter = bool(metadata.get("_has_frontmatter"))

    if not has_frontmatter:
        return issues

    if not metadata.get("message_id"):
        issues.append(SchemaIssue("warning", "Missing message_id / Message-ID"))

    missing = sorted(field for field in REQUIRED_FRONTMATTER_FIELDS if field not in metadata or metadata[field] == "")
    if missing:
        issues.append(SchemaIssue("warning", f"Schema v1 missing required fields: {', '.join(missing)}"))

    if metadata.get("schema_version") != MESSAGE_SCHEMA_VERSION:
        issues.append(SchemaIssue("warning", f"Unexpected schema_version: {metadata.get('schema_version')}"))

    from_id = str(metadata.get("from", ""))
    to_id = str(metadata.get("to", ""))
    if from_id and from_id not in PARTICIPANTS:
        issues.append(SchemaIssue("warning", f"Unknown from participant: {from_id}"))
    if to_id and to_id not in PARTICIPANTS:
        issues.append(SchemaIssue("warning", f"Unknown to participant: {to_id}"))
    if to_id == "pah" and str(metadata.get("type", "")) not in {"decision_record", "diagnostic_result", "system_event"}:
        issues.append(SchemaIssue("warning", "Direct messages to PAH are reserved for system/decision records"))

    status = normalize_status(str(metadata.get("status", "")))
    thread_status = str(metadata.get("thread_status", "")).strip().lower()
    priority = str(metadata.get("priority", "")).strip().lower()
    msg_type = str(metadata.get("type", "")).strip().lower()
    approval_boundary = str(metadata.get("approval_boundary", "")).strip().lower()
    if status and status not in STATUS_VALUES:
        issues.append(SchemaIssue("warning", f"Unsupported status enum: {status}"))
    if thread_status and thread_status not in THREAD_STATUS_VALUES:
        issues.append(SchemaIssue("warning", f"Unsupported thread_status enum: {thread_status}"))
    if priority and priority not in PRIORITY_VALUES:
        issues.append(SchemaIssue("warning", f"Unsupported priority enum: {priority}"))
    if msg_type and msg_type not in MESSAGE_TYPES:
        issues.append(SchemaIssue("warning", f"Unsupported message type: {msg_type}"))
    if approval_boundary and approval_boundary not in APPROVAL_BOUNDARIES:
        issues.append(SchemaIssue("warning", f"Unsupported approval_boundary enum: {approval_boundary}"))

    if metadata_waits_on_darrin(metadata) and not path_name:
        issues.append(SchemaIssue("info", "Message is an explicit Darrin queue candidate"))

    return issues


def yaml_scalar(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    text = str(value)
    if not text:
        return "''"
    if re.search(r"[:#\[\]\n]", text):
        return "'" + text.replace("'", "''") + "'"
    return text


def render_message_markdown(
    metadata: dict[str, Any],
    title: str,
    summary: str,
    details: str,
    approval_note: str = "Coordination only unless Darrin explicitly approves implementation.",
) -> str:
    ordered_keys = [
        "schema_version",
        "message_id",
        "thread_id",
        "created_at",
        "from",
        "to",
        "type",
        "priority",
        "status",
        "thread_status",
        "approval_boundary",
        "requires_darrin_decision",
        "reply_to",
    ]
    lines = ["---"]
    for key in ordered_keys:
        if key not in metadata:
            continue
        value = metadata[key]
        if isinstance(value, list):
            lines.append(f"{key}:")
            if value:
                lines.extend(f"  - {yaml_scalar(item)}" for item in value)
            continue
        lines.append(f"{key}: {yaml_scalar(value)}")
    lines.extend(
        [
            "---",
            "",
            f"# {title}",
            "",
            "## Summary",
            "",
            summary,
            "",
            "## Details",
            "",
            details,
            "",
            "## Approval Boundary",
            "",
            approval_note,
            "",
        ]
    )
    return "\n".join(lines)


def content_hash(text: str) -> str:
    import hashlib

    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def path_display(path: Path) -> str:
    return str(path)
