from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def stamp() -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y%m%d_%H%M%S")


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def sha256_json(data: Any) -> str:
    encoded = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def first_issue(issue_extraction_path: Path) -> dict[str, Any]:
    extraction = read_json(issue_extraction_path)
    issues = extraction.get("issues") if isinstance(extraction, dict) else None
    if not isinstance(issues, list) or not issues:
        raise ValueError(f"No issues available in {issue_extraction_path}")
    issue = issues[0]
    if not isinstance(issue, dict):
        raise ValueError("First issue is not an object")
    return issue


def create_approval_record(issue_extraction_path: Path, output_dir: Path, reviewer_name: str = "Darrin") -> Path:
    issue = first_issue(issue_extraction_path)
    created_at = now_iso()
    approved_title = issue.get("reviewer", {}).get("edited_title") or issue["title"]
    approved_summary = issue.get("reviewer", {}).get("edited_summary") or issue["summary"]
    approved_response = issue.get("reviewer", {}).get("edited_response_markdown") or issue["suggested_response"]["body_markdown"]
    approval = {
        "schema": "pg.audit_approval_record.v1",
        "approval_id": f"appr_{stamp()}_0001",
        "issue_id": issue["issue_id"],
        "package_id": issue["package_id"],
        "session_id": issue["session_id"],
        "run_id": issue["run_id"],
        "approved_by": {"display_name": reviewer_name, "email": None},
        "approved_at": created_at,
        "approved_title": approved_title,
        "approved_summary": approved_summary,
        "approved_response_markdown": approved_response,
        "evidence_ids": issue["evidence_ids"],
        "approval_notes": "Local prototype approval record; no email sent.",
    }
    output_path = output_dir / f"{approval['approval_id']}.json"
    write_json(output_path, approval)
    return output_path


def create_email_draft_record(approval_path: Path, output_dir: Path) -> Path:
    approval = read_json(approval_path)
    created_at = now_iso()
    email = {
        "schema": "pg.audit_email_record.v1",
        "email_id": f"email_{stamp()}_0001",
        "issue_id": approval["issue_id"],
        "approval_id": approval["approval_id"],
        "package_id": approval["package_id"],
        "session_id": approval["session_id"],
        "run_id": approval["run_id"],
        "provider": "not_configured_local_prototype",
        "shared_inbox": "team@example.invalid",
        "to": ["team@example.invalid"],
        "cc": [],
        "subject": approval["approved_title"],
        "body_markdown": approval["approved_response_markdown"],
        "state": "draft_only",
        "created_at": created_at,
        "queued_at": None,
        "sent_at": None,
        "provider_message_id": None,
        "error": None,
    }
    output_path = output_dir / f"{email['email_id']}.json"
    write_json(output_path, email)
    return output_path


def append_archive_record(approval_path: Path, email_path: Path, archive_path: Path, closed_by: str = "Darrin") -> dict[str, Any]:
    approval = read_json(approval_path)
    email = read_json(email_path)
    closed_at = now_iso()
    source_payload = {"approval": approval, "email": email}
    archive = {
        "schema": "pg.audit_archive_record.v1",
        "archive_id": f"arch_{stamp()}_0001",
        "issue_id": approval["issue_id"],
        "approval_id": approval["approval_id"],
        "email_id": email["email_id"],
        "package_id": approval["package_id"],
        "session_id": approval["session_id"],
        "run_id": approval["run_id"],
        "closed_at": closed_at,
        "closed_by": closed_by,
        "close_reason": "local_prototype_draft_only",
        "title": approval["approved_title"],
        "summary": approval["approved_summary"],
        "category": "unknown",
        "priority": "P3",
        "status": "archived",
        "evidence_ids": approval["evidence_ids"],
        "search_text": f"{approval['approved_title']} {approval['approved_summary']} {approval['approved_response_markdown']}".lower(),
        "tags": ["local-prototype", "draft-only"],
        "immutability": {
            "source_issue_sha256": sha256_json(source_payload),
            "record_sha256": None,
        },
    }
    archive_for_hash = dict(archive)
    archive_for_hash["immutability"] = dict(archive["immutability"])
    archive_for_hash["immutability"]["record_sha256"] = None
    archive["immutability"]["record_sha256"] = sha256_json(archive_for_hash)
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with archive_path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(archive, sort_keys=True, ensure_ascii=False) + "\n")
    return archive


def create_local_review_records(package_dir: Path, reviewer_name: str = "Darrin") -> dict[str, str]:
    issue_path = package_dir / "derived" / "audit_issue_extraction_v1.json"
    approval_path = create_approval_record(issue_path, package_dir / "review" / "approvals", reviewer_name)
    email_path = create_email_draft_record(approval_path, package_dir / "review" / "email_drafts")
    archive_path = package_dir / "review" / "archive" / "audit_archive_records.jsonl"
    append_archive_record(approval_path, email_path, archive_path, reviewer_name)
    return {
        "approval_record": str(approval_path),
        "email_draft_record": str(email_path),
        "archive_jsonl": str(archive_path),
    }


def validate_review_record_chain(approval_path: Path, email_path: Path, archive_path: Path) -> list[str]:
    errors: list[str] = []
    approval = read_json(approval_path)
    email = read_json(email_path)
    if approval.get("schema") != "pg.audit_approval_record.v1":
        errors.append("approval schema is invalid")
    if email.get("schema") != "pg.audit_email_record.v1":
        errors.append("email schema is invalid")
    if email.get("state") != "draft_only":
        errors.append("email state must be draft_only in local prototype")
    for field_name in ["issue_id", "approval_id", "package_id", "session_id", "run_id"]:
        if field_name in email and field_name in approval and email[field_name] != approval[field_name]:
            errors.append(f"email.{field_name} does not match approval.{field_name}")

    records = search_archive_records(archive_path)
    if not records:
        errors.append("archive must contain at least one record")
        return errors
    archive = records[-1]
    if archive.get("schema") != "pg.audit_archive_record.v1":
        errors.append("archive schema is invalid")
    if archive.get("status") != "archived":
        errors.append("archive status must be archived")
    if archive.get("issue_id") != approval.get("issue_id"):
        errors.append("archive.issue_id does not match approval.issue_id")
    immutability = archive.get("immutability")
    if not isinstance(immutability, dict) or not immutability.get("record_sha256"):
        errors.append("archive immutability.record_sha256 is required")
    return errors


def search_archive_records(archive_path: Path, query: str | None = None) -> list[dict[str, Any]]:
    if not archive_path.exists():
        return []
    terms = [term.lower() for term in (query or "").split() if term.strip()]
    matches: list[dict[str, Any]] = []
    with archive_path.open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            if not line.strip():
                continue
            record = json.loads(line)
            if not isinstance(record, dict):
                continue
            haystack = " ".join(str(record.get(key, "")) for key in ["title", "summary", "category", "priority", "search_text"]).lower()
            if all(term in haystack for term in terms):
                matches.append(record)
    return matches
