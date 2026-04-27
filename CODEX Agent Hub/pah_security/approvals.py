"""Approval record contracts for protected PAH actions."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pah_core.schema import content_hash
from pah_mailbox.paths import APPROVAL_RECORDS_PATH


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
    if record.get("one_time_use") not in {True, False, None}:
        errors.append("one_time_use must be a boolean")
    if "exact_paths" in record and not isinstance(record.get("exact_paths"), list):
        errors.append("exact_paths must be a list")
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
    for record in records:
        errors = validate_approval_record(record)
        if record.get("revoked") is True:
            revoked += 1
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
        "required_fields": sorted(APPROVAL_REQUIRED_FIELDS),
    }


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
        if str(record.get("request_hash")) != expected_hash:
            continue
        return record
    return None
