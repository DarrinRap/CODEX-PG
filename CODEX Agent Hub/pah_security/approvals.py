"""Approval record contracts for protected PAH actions."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pah_core.schema import content_hash
from pah_mailbox.atomic import atomic_write_text
from pah_mailbox.paths import APPROVAL_RECORDS_PATH
from pah_security.path_scope import classify_path


APPROVAL_REQUIRED_FIELDS = {
    "approval_id",
    "scope",
    "exact_paths",
    "command_or_provider",
    "budget",
    "expires_at",
    "one_time_use",
    "approver",
    "revoked",
    "request_hash",
}
PROTECTED_ACTION_TYPES = {
    "write_panda_gallery",
    "destructive_filesystem",
    "git_commit",
    "git_push",
    "package_install",
    "external_api_call",
    "sms_email_send",
    "headless_agent_run",
    "paid_provider_setup",
}
PROTECTED_PATH_SCOPES = {"panda_gallery_requires_darrin", "outside_known_scope"}
ACTION_SCOPE_BY_TYPE = {
    "write_panda_gallery": "panda_gallery_requires_darrin",
    "destructive_filesystem": "destructive_filesystem_requires_darrin",
    "git_commit": "git_commit_requires_darrin",
    "git_push": "git_push_requires_darrin",
    "package_install": "package_install_requires_darrin",
    "external_api_call": "external_api_requires_darrin",
    "sms_email_send": "external_communication_requires_darrin",
    "headless_agent_run": "headless_agent_requires_darrin",
    "paid_provider_setup": "paid_provider_requires_darrin",
}


def canonical_request_hash(scope: str, exact_paths: list[str], command_or_provider: str, budget: str = "") -> str:
    payload = json.dumps(
        {
            "scope": scope,
            "exact_paths": sorted(str(path) for path in exact_paths),
            "command_or_provider": command_or_provider,
            "budget": budget,
        },
        sort_keys=True,
    )
    return content_hash(payload)


def command_hash(command_preview: str) -> str:
    return content_hash(command_preview)


def approval_hash(request_hash: str, command_hash_value: str, approved_by: str, approved_at: str) -> str:
    return content_hash(f"{normalize_hash(request_hash)}{normalize_hash(command_hash_value)}{approved_by}{approved_at}")


def normalize_hash(value: Any) -> str:
    text = str(value or "").strip()
    return text[7:] if text.startswith("sha256:") else text


def hash_matches(record_value: Any, expected_hash: str) -> bool:
    return normalize_hash(record_value) == normalize_hash(expected_hash)


def read_jsonl(path: Path = APPROVAL_RECORDS_PATH) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            records.append({"_invalid": True, "raw": line})
            continue
        if isinstance(value, dict):
            records.append(value)
    return records


def parse_expiry(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def validate_approval_record(record: dict[str, Any]) -> list[str]:
    if record.get("_invalid"):
        return ["Approval record is not valid JSON"]
    missing = sorted(field for field in APPROVAL_REQUIRED_FIELDS if field not in record)
    errors = [f"Missing approval field: {field}" for field in missing]
    if record.get("approver") and str(record.get("approver")).lower() != "darrin":
        errors.append("Protected approvals must name Darrin as approver")
    if record.get("revoked") is True:
        errors.append("Approval record is revoked")
    if str(record.get("revoked_at", "")).strip():
        errors.append("Approval record is revoked")
    if record.get("one_time_use") is True and str(record.get("consumed_at", "")).strip():
        errors.append("Approval record is already consumed")
    if record.get("one_time_use") not in {True, False, None}:
        errors.append("one_time_use must be a boolean")
    if "exact_paths" in record and not isinstance(record.get("exact_paths"), list):
        errors.append("exact_paths must be a list")
    if "command_hash" in record and "command_preview" in record:
        if not hash_matches(record.get("command_hash"), command_hash(str(record.get("command_preview", "")))):
            errors.append("command_hash does not match command_preview")
    if {"approval_hash", "request_hash", "command_hash", "approved_by", "approved_at"}.issubset(record):
        expected_approval_hash = approval_hash(
            str(record.get("request_hash", "")),
            str(record.get("command_hash", "")),
            str(record.get("approved_by", "")),
            str(record.get("approved_at", "")),
        )
        if not hash_matches(record.get("approval_hash"), expected_approval_hash):
            errors.append("approval_hash does not match approval record binding")
    if "expires_at" in record:
        expiry = parse_expiry(record.get("expires_at"))
        if not expiry:
            errors.append("expires_at must be ISO-8601")
        elif expiry <= datetime.now(timezone.utc):
            errors.append("Approval record is expired")
    return errors


def approval_status(path: Path = APPROVAL_RECORDS_PATH) -> dict[str, Any]:
    records = read_jsonl(path)
    invalid = 0
    active = 0
    revoked = 0
    expired = 0
    consumed = 0
    for record in records:
        errors = validate_approval_record(record)
        if record.get("revoked") is True or str(record.get("revoked_at", "")).strip():
            revoked += 1
        if str(record.get("consumed_at", "")).strip():
            consumed += 1
        expiry = parse_expiry(record.get("expires_at"))
        if expiry and expiry <= datetime.now(timezone.utc):
            expired += 1
        if errors:
            invalid += 1
        else:
            active += 1
    return {
        "records_path": str(path),
        "records": len(records),
        "active": active,
        "invalid": invalid,
        "revoked": revoked,
        "expired": expired,
        "consumed": consumed,
        "required_fields": sorted(APPROVAL_REQUIRED_FIELDS),
        "protected_action_types": sorted(PROTECTED_ACTION_TYPES),
        "enforcement": "active_for_protected_action_checks",
    }


def protected_scope_for(action_type: str, exact_paths: list[str] | None = None) -> str:
    normalized_action = str(action_type or "").strip().lower()
    if normalized_action in ACTION_SCOPE_BY_TYPE:
        return ACTION_SCOPE_BY_TYPE[normalized_action]
    for path_value in exact_paths or []:
        if classify_path(Path(path_value)) in PROTECTED_PATH_SCOPES:
            return "protected_action_requires_darrin"
    return ""


def find_matching_approval(
    scope: str,
    exact_paths: list[str],
    command_or_provider: str,
    budget: str = "",
    path: Path = APPROVAL_RECORDS_PATH,
) -> dict[str, Any] | None:
    expected_hash = canonical_request_hash(scope, exact_paths, command_or_provider, budget)
    for record in read_jsonl(path):
        if validate_approval_record(record):
            continue
        if str(record.get("scope")) != scope:
            continue
        if sorted(str(item) for item in record.get("exact_paths", [])) != sorted(str(item) for item in exact_paths):
            continue
        if str(record.get("command_or_provider")) != command_or_provider:
            continue
        if not hash_matches(record.get("request_hash"), expected_hash):
            continue
        return record
    return None


def approval_check(
    action_type: str,
    exact_paths: list[str],
    command_or_provider: str,
    budget: str = "",
    path: Path = APPROVAL_RECORDS_PATH,
) -> dict[str, Any]:
    scope = protected_scope_for(action_type, exact_paths)
    if not scope:
        return {
            "required": False,
            "allowed": True,
            "scope": "",
            "reason": "Action is not classified as protected by PAH policy.",
            "approval_id": "",
        }
    record = find_matching_approval(scope, exact_paths, command_or_provider, budget, path)
    if not record:
        return {
            "required": True,
            "allowed": False,
            "scope": scope,
            "reason": "No active hash-bound approval record matches this protected action.",
            "approval_id": "",
        }
    return {
        "required": True,
        "allowed": True,
        "scope": scope,
        "reason": "Protected action has an active matching approval record.",
        "approval_id": str(record.get("approval_id", "") or record.get("id", "")),
        "request_hash": str(record.get("request_hash", "")),
    }


def enforce_protected_action(
    action_type: str,
    exact_paths: list[str],
    command_or_provider: str,
    budget: str = "",
    path: Path = APPROVAL_RECORDS_PATH,
) -> dict[str, Any]:
    check = approval_check(action_type, exact_paths, command_or_provider, budget, path)
    if check["required"] and not check["allowed"]:
        raise PermissionError(check["reason"])
    return check


def mark_approval_consumed(
    approval_id: str,
    *,
    consumed_at: str | None = None,
    path: Path = APPROVAL_RECORDS_PATH,
) -> dict[str, Any]:
    records = read_jsonl(path)
    timestamp = consumed_at or datetime.now(timezone.utc).isoformat(timespec="seconds")
    updated: dict[str, Any] | None = None
    for record in records:
        if str(record.get("approval_id", "") or record.get("id", "")) == approval_id:
            record["consumed_at"] = timestamp
            updated = record
            break
    if updated is None:
        raise KeyError(f"Unknown approval record: {approval_id}")
    path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_text(path, "".join(json.dumps(record, sort_keys=True) + "\n" for record in records))
    return updated
