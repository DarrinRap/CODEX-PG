"""PAH Inspector: deep consistency and UX wiring checks for PANDA Agent Hub.

The inspector is intentionally dependency-light. It uses PAH's local Python
contracts for internal checks and HTTP endpoints for live checks, then writes a
JSON and Markdown report that can be read by Darrin, Codex, CD, or CC.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from http.cookiejar import CookieJar
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import HTTPCookieProcessor, Request, build_opener, urlopen


ROOT = Path(__file__).resolve().parent
LOG_DIR = ROOT / "CODEX logs"
LATEST_JSON_PATH = LOG_DIR / "CODEX_pah_inspector_latest.json"
LATEST_MD_PATH = LOG_DIR / "CODEX_pah_inspector_latest.md"
HISTORY_PATH = LOG_DIR / "CODEX_pah_inspector.jsonl"
DEFAULT_URL = "http://127.0.0.1:8765"
DEFAULT_HTTP_TIMEOUT_SECONDS = 60


import CODEX_agent_hub as agent_hub


@dataclass
class Finding:
    check_id: str
    title: str
    status: str
    summary: str
    detail: dict[str, Any] = field(default_factory=dict)
    recommendation: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "check_id": self.check_id,
            "title": self.title,
            "status": self.status,
            "summary": self.summary,
            "detail": self.detail,
            "recommendation": self.recommendation,
        }


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def fetch_json(url: str, path: str, timeout: int = DEFAULT_HTTP_TIMEOUT_SECONDS) -> dict[str, Any]:
    with urlopen(f"{url.rstrip('/')}{path}", timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8", errors="replace"))


def post_json_with_write_cookie(
    url: str,
    path: str,
    payload: dict[str, Any],
    timeout: int = DEFAULT_HTTP_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    base_url = url.rstrip("/")
    cookie_jar = CookieJar()
    opener = build_opener(HTTPCookieProcessor(cookie_jar))
    opener.open(f"{base_url}/", timeout=timeout).read()
    request = Request(
        f"{base_url}{path}",
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={"Content-Type": "application/json", "Origin": base_url},
    )
    with opener.open(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8", errors="replace"))


def post_json_without_write_cookie(
    url: str,
    path: str,
    payload: dict[str, Any],
    timeout: int = DEFAULT_HTTP_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    base_url = url.rstrip("/")
    request = Request(
        f"{base_url}{path}",
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={"Content-Type": "application/json", "Origin": base_url},
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
            try:
                parsed = json.loads(body)
            except json.JSONDecodeError:
                parsed = {"raw": body[:500]}
            return {"http_status": response.status, "payload": parsed}
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            parsed = {"raw": body[:500]}
        return {"http_status": exc.code, "payload": parsed}


def check(status: bool, check_id: str, title: str, ok_summary: str, fail_summary: str, **detail: Any) -> Finding:
    return Finding(
        check_id=check_id,
        title=title,
        status="pass" if status else "fail",
        summary=ok_summary if status else fail_summary,
        detail=detail,
    )


def warn(check_id: str, title: str, summary: str, recommendation: str = "", **detail: Any) -> Finding:
    return Finding(check_id, title, "warn", summary, detail, recommendation)


def fail(check_id: str, title: str, summary: str, recommendation: str = "", **detail: Any) -> Finding:
    return Finding(check_id, title, "fail", summary, detail, recommendation)


CC_PROGRESS_CARD_REQUIRED_FIELDS = {
    "id",
    "agent",
    "label",
    "severity",
    "status",
    "phase",
    "evidence_summary",
    "recommended_action",
    "sidecar_path",
    "issues",
    "targets",
}
CC_PROGRESS_ALLOWED_STATUSES = {
    "idle",
    "invalid",
    "active",
    "compose",
    "heavy_write",
    "paused",
    "blocked",
    "ready_for_human_loop",
    "complete",
    "abandoned",
}
CC_PROGRESS_REQUIRED_SIDECAR_FIELDS = {
    "schema_version",
    "agent",
    "dispatch_id",
    "status",
    "updated_at",
}


def inspect_cc_active_dispatch_contract(card: dict[str, Any] | None) -> list[Finding]:
    findings: list[Finding] = []
    if not isinstance(card, dict):
        return [
            fail(
                "endpoint.cc_active_dispatch_card_contract",
                "CC progress card contract",
                "Cockpit does not expose a structured CC progress card.",
                "Restore the cc_active_dispatch card in cockpit agent_progress.",
            )
        ]

    missing_fields = sorted(field for field in CC_PROGRESS_CARD_REQUIRED_FIELDS if field not in card)
    status_name = str(card.get("status", "")).strip().lower()
    severity = str(card.get("severity", "")).strip().lower()
    bad_status = status_name not in CC_PROGRESS_ALLOWED_STATUSES
    bad_severity = severity not in {"ok", "warn", "err"}
    findings.append(
        check(
            not missing_fields and not bad_status and not bad_severity,
            "endpoint.cc_active_dispatch_card_contract",
            "CC progress card contract",
            "CC progress card exposes required fields, status, severity, and recommended action.",
            "CC progress card is missing required fields or exposes an unsupported status/severity.",
            missing_fields=missing_fields,
            card_status=status_name,
            card_severity=severity,
            allowed_statuses=sorted(CC_PROGRESS_ALLOWED_STATUSES),
        )
    )

    sidecar_path = Path(str(card.get("sidecar_path") or agent_hub.CC_ACTIVE_DISPATCH_PATH))
    if not sidecar_path.exists():
        if status_name in {"idle", "complete", "abandoned"} and agent_hub.advisory_is_accepted("cc_sidecar_absent_idle"):
            findings.append(
                passed(
                    "endpoint.cc_active_dispatch_sidecar_readiness",
                    "CC sidecar readiness",
                    "active_dispatch.json is absent while CC is not live-active; this idle sidecar condition is accepted by PAH policy.",
                    sidecar_path=str(sidecar_path),
                    status=status_name,
                    accepted_advisory="cc_sidecar_absent_idle",
                )
            )
            return findings
        findings.append(
            warn(
                "endpoint.cc_active_dispatch_sidecar_readiness",
                "CC sidecar readiness",
                "CC progress card is present, but active_dispatch.json is absent; PAH can only report CC as idle until CC writes the sidecar.",
                "Have the CC sidecar writer create active_dispatch.json before treating CC activity as live-monitored.",
                sidecar_path=str(sidecar_path),
                status=status_name,
            )
        )
        return findings

    try:
        sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        findings.append(
            fail(
                "endpoint.cc_active_dispatch_sidecar_readiness",
                "CC sidecar readiness",
                "active_dispatch.json exists but cannot be read as JSON.",
                "Repair or replace the CC active dispatch sidecar.",
                sidecar_path=str(sidecar_path),
                error=str(exc),
            )
        )
        return findings

    if not isinstance(sidecar, dict):
        findings.append(
            fail(
                "endpoint.cc_active_dispatch_sidecar_readiness",
                "CC sidecar readiness",
                "active_dispatch.json exists but is not a JSON object.",
                "Write the CC active dispatch sidecar as a JSON object.",
                sidecar_path=str(sidecar_path),
                value_type=type(sidecar).__name__,
            )
        )
        return findings

    sidecar_status = str(sidecar.get("status", "active")).strip().lower() or "active"
    required = set(CC_PROGRESS_REQUIRED_SIDECAR_FIELDS)
    if sidecar_status in {"active", "heavy_write"}:
        required.add("expected_target_paths")
    if sidecar_status == "ready_for_human_loop":
        required.add("human_loop_evidence_path")
    missing_sidecar_fields = sorted(field for field in required if field not in sidecar)
    bad_sidecar_status = sidecar_status not in (CC_PROGRESS_ALLOWED_STATUSES - {"idle", "invalid"})
    findings.append(
        check(
            not missing_sidecar_fields and not bad_sidecar_status,
            "endpoint.cc_active_dispatch_sidecar_readiness",
            "CC sidecar readiness",
            "active_dispatch.json has the required fields for live CC progress monitoring.",
            "active_dispatch.json is missing required fields or uses an unsupported status.",
            sidecar_path=str(sidecar_path),
            missing_fields=missing_sidecar_fields,
            sidecar_status=sidecar_status,
            allowed_statuses=sorted(CC_PROGRESS_ALLOWED_STATUSES - {"idle", "invalid"}),
        )
    )

    targets = card.get("targets", [])
    if not isinstance(targets, list):
        targets = []
    unsafe_targets = [
        {"path": target.get("path"), "reason": target.get("invalid_reason", "unknown")}
        for target in targets
        if isinstance(target, dict) and not bool(target.get("allowed", False))
    ]
    issues = [str(issue) for issue in card.get("issues", [])] if isinstance(card.get("issues", []), list) else []
    safety_issues = [issue for issue in issues if issue.startswith("unsafe_target") or issue in {"missing_targets", "missing_target"}]
    findings.append(
        check(
            not unsafe_targets and not safety_issues,
            "endpoint.cc_active_dispatch_target_safety",
            "CC progress target safety",
            "CC progress targets are allowlisted and usable for file-mtime evidence.",
            "CC progress targets are missing or outside the safe allowlist.",
            sidecar_path=str(sidecar_path),
            unsafe_targets=unsafe_targets,
            safety_issues=safety_issues,
        )
    )
    return findings


def passed(check_id: str, title: str, summary: str, **detail: Any) -> Finding:
    return Finding(check_id, title, "pass", summary, detail)


def count_physical_mailbox_markdown() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    total = 0
    for label, directory in agent_hub.MESSAGE_DIRS:
        count = 0
        if directory.exists():
            count = sum(1 for path in directory.iterdir() if path.is_file() and path.suffix.lower() == ".md")
        rows.append({"label": label, "path": str(directory), "markdown_files": count, "exists": directory.exists()})
        total += count
    return {"total": total, "rows": rows}


def inspect_live_endpoints(url: str) -> tuple[list[Finding], dict[str, Any]]:
    findings: list[Finding] = []
    payloads: dict[str, Any] = {}
    endpoints = {
        "status": "/api/status",
        "cockpit": "/api/cockpit",
        "health": "/api/health",
        "tray": "/api/tray-status",
        "inspector_report": "/api/inspector-report",
        "cc_activity": "/api/cc-activity",
    }
    for name, path in endpoints.items():
        started = time.perf_counter()
        try:
            payload = fetch_json(url, path)
        except (OSError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            findings.append(
                fail(
                    f"endpoint.{name}",
                    f"Endpoint {path}",
                    f"{path} is not returning valid JSON.",
                    "Confirm the PAH server is running and inspect stderr/stdout logs.",
                    error=str(exc),
                )
            )
            continue
        duration_ms = int((time.perf_counter() - started) * 1000)
        payloads[name] = payload
        findings.append(passed(f"endpoint.{name}", f"Endpoint {path}", f"{path} returned JSON.", duration_ms=duration_ms))

    try:
        blocked = post_json_without_write_cookie(
            url,
            "/api/create-message",
            {
                "route": "codex_to_claude",
                "subject": "PAH inspector unauthorized write probe",
                "body": "This probe must be rejected before any write.",
                "dry_run": True,
            },
        )
        findings.append(
            check(
                int(blocked.get("http_status", 0) or 0) == 403 and blocked.get("payload", {}).get("ok") is False,
                "endpoint.write_protection",
                "Write protection",
                "Write endpoints reject requests without the PAH write cookie/token.",
                "A write endpoint accepted a request without the PAH write cookie/token.",
                response=blocked,
            )
        )
    except Exception as exc:
        findings.append(
            fail(
                "endpoint.write_protection",
                "Write protection",
                "Could not verify unauthenticated write rejection.",
                error=str(exc),
            )
        )

    try:
        probe = post_json_with_write_cookie(
            url,
            "/api/create-message",
            {
                "route": "codex_to_claude",
                "subject": "PAH inspector dry-run probe",
                "body": "Inspector route validation only; should never write a mailbox file.",
                "dry_run": True,
            },
        )
        probe_path = Path(str(probe.get("path", "")))
        findings.append(
            check(
                bool(probe.get("ok")) and bool(probe.get("dry_run")) and not probe_path.exists(),
                "endpoint.create_message_dry_run",
                "Create-message dry-run endpoint",
                "/api/create-message supports non-destructive dry-run validation.",
                "/api/create-message dry-run failed or wrote a mailbox file.",
                response=probe,
                path_exists=probe_path.exists(),
            )
        )
    except Exception as exc:
        findings.append(
            fail(
                "endpoint.create_message_dry_run",
                "Create-message dry-run endpoint",
                "/api/create-message dry-run probe failed.",
                error=str(exc),
            )
        )

    try:
        canary = post_json_with_write_cookie(
            url,
            "/api/mailroom-canary",
            {"actor": "pah_inspector"},
            timeout=DEFAULT_HTTP_TIMEOUT_SECONDS,
        )
        checks = canary.get("checks", {}) if isinstance(canary.get("checks"), dict) else {}
        missing_checks = sorted(name for name, ok in checks.items() if not ok)
        findings.append(
            check(
                bool(canary.get("ok")) and not missing_checks,
                "endpoint.mailroom_transaction_canary",
                "Mailroom transaction canary",
                "Live PAH can send, mark read, write reply tombstones, and ledger the transaction in an isolated mailbox.",
                "PAH mailroom transaction canary failed; send/read/reply-tombstone/ledger may be unreliable.",
                response=canary,
                missing_checks=missing_checks,
            )
        )
    except Exception as exc:
        findings.append(
            fail(
                "endpoint.mailroom_transaction_canary",
                "Mailroom transaction canary",
                "Could not run the live PAH mailroom transaction canary.",
                "Check /api/mailroom-canary and PAH server stderr/stdout before trusting mailroom status.",
                error=str(exc),
            )
        )

    status = payloads.get("status", {})
    cockpit = payloads.get("cockpit", {})
    health = payloads.get("health", {})
    tray = payloads.get("tray", {})
    if cockpit:
        queue = cockpit.get("action_queue", []) or []
        required_fields = {"id", "title", "kind", "state", "severity", "thread_id", "message_path"}
        queue_issues = []
        for index, item in enumerate(queue[:25]):
            missing = sorted(field for field in required_fields if not item.get(field))
            message_path = Path(str(item.get("message_path", "")))
            path_exists = bool(item.get("message_path")) and message_path.exists()
            if missing or not path_exists:
                queue_issues.append(
                    {
                        "index": index,
                        "id": item.get("id", ""),
                        "missing": missing,
                        "message_path": str(message_path) if item.get("message_path") else "",
                        "path_exists": path_exists,
                    }
                )
        findings.append(
            check(
                not queue_issues,
                "endpoint.action_queue_contract",
                "Action queue item contract",
                "Visible action-queue items expose the fields needed for accurate review and preview wiring.",
                "Some visible action-queue items are missing required fields or point at missing files.",
                checked=min(len(queue), 25),
                issues=queue_issues,
            )
        )
        preview_target = next((item for item in queue if item.get("message_path")), None)
        if preview_target:
            try:
                message_payload = fetch_json(url, f"/api/message?path={quote(str(preview_target.get('message_path', '')))}")
                findings.append(
                    check(
                        bool(message_payload.get("ok")) and bool(message_payload.get("content")),
                        "endpoint.message_preview_fetch",
                        "Message preview fetch",
                        "/api/message returns content for the selected action-queue item path.",
                        "/api/message did not return readable content for a visible action-queue item.",
                        id=preview_target.get("id", ""),
                        path=str(preview_target.get("message_path", "")),
                        content_chars=len(str(message_payload.get("content", ""))),
                    )
                )
            except Exception as exc:
                findings.append(
                    fail(
                        "endpoint.message_preview_fetch",
                        "Message preview fetch",
                        "/api/message fetch failed for a visible action-queue item.",
                        id=preview_target.get("id", ""),
                        path=str(preview_target.get("message_path", "")),
                        error=str(exc),
                    )
                )
        else:
            findings.append(
                warn(
                    "endpoint.message_preview_fetch",
                    "Message preview fetch",
                    "No action-queue item with message_path was available for preview-fetch validation.",
                    "Run again when PAH has at least one visible mailbox-backed queue item.",
                )
            )
    if status and cockpit:
        status_counts = status.get("counts", {})
        status_thread_counts = status.get("thread_focus", {}).get("counts", {})
        cockpit_counts = cockpit.get("cockpit_state", {}).get("counts", {})
        comparisons = {
            "messages": status_counts.get("messages"),
            "open_on_darrin": status_thread_counts.get("open_on_darrin"),
            "open_on_agent": status_thread_counts.get("open_on_agent"),
            "owner_unknown": status_thread_counts.get("owner_unknown"),
        }
        mismatches = {
            field: {"status": expected, "cockpit": cockpit_counts.get(field)}
            for field, expected in comparisons.items()
            if expected != cockpit_counts.get(field)
        }
        findings.append(
            check(
                not mismatches,
                "endpoint.status_cockpit_counts",
                "Status/cockpit count agreement",
                "Status and cockpit counts agree.",
                "Status and cockpit counts disagree.",
                mismatches=mismatches,
            )
        )
    if health:
        required = {"server", "routes", "mailboxes", "archive", "interaction_ledger", "periodic_monitor", "agent_progress", "inspector"}
        components = set((health.get("components") or {}).keys())
        missing = sorted(required - components)
        findings.append(
            check(
                not missing,
                "endpoint.health_components",
                "Health component coverage",
                "Health endpoint exposes the expected PAH components.",
                "Health endpoint is missing expected components.",
                missing=missing,
                components=sorted(components),
            )
        )
    if cockpit and tray:
        expected_stale = len(cockpit.get("wake_candidates", []) or [])
        tray_stale = int(tray.get("counts", {}).get("stale_unread", 0) or 0)
        findings.append(
            check(
                expected_stale == tray_stale,
                "endpoint.tray_stale_unread",
                "Tray stale unread consistency",
                "Tray stale unread count matches cockpit wake candidates.",
                "Tray stale unread count does not match cockpit wake candidates.",
                expected_stale_unread=expected_stale,
                tray_stale_unread=tray_stale,
            )
        )
    if cockpit:
        progress = cockpit.get("agent_progress", {})
        cards = progress.get("cards", []) if isinstance(progress, dict) else []
        card_by_id = {str(card.get("id", "")): card for card in cards if isinstance(card, dict)}
        card_ids = set(card_by_id)
        missing_cards = sorted({"cc_active_dispatch", "codex_mailbox_sla"} - card_ids)
        missing_actions = [
            str(card.get("id", "unknown"))
            for card in cards
            if isinstance(card, dict) and not str(card.get("recommended_action", "")).strip()
        ]
        findings.append(
            check(
                not missing_cards and not missing_actions,
                "endpoint.agent_progress_contract",
                "Agent progress payload",
                "Cockpit exposes CC progress and Codex mailbox SLA cards with recommended actions.",
                "Cockpit agent progress payload is missing required cards or recommended actions.",
                missing_cards=missing_cards,
                missing_actions=missing_actions,
                card_ids=sorted(card_ids),
            )
        )
        findings.extend(inspect_cc_active_dispatch_contract(card_by_id.get("cc_active_dispatch")))
    return findings, payloads


def inspect_internal_contracts(status_payload: dict[str, Any] | None = None) -> list[Finding]:
    findings: list[Finding] = []
    messages = agent_hub.load_messages()
    read_state = agent_hub.load_read_state()
    physical = count_physical_mailbox_markdown()
    findings.append(
        check(
            len(messages) == physical["total"],
            "internal.physical_message_count",
            "Physical mailbox scan",
            "Every active mailbox markdown file is represented in PAH's message scan.",
            "PAH's message scan count differs from active mailbox markdown files.",
            loaded_messages=len(messages),
            physical_markdown=physical["total"],
            mailboxes=physical["rows"],
        )
    )
    if status_payload:
        status_count = int(status_payload.get("counts", {}).get("messages", -1) or 0)
        findings.append(
            check(
                status_count == len(messages),
                "internal.status_message_count",
                "Status message count",
                "Live status count matches PAH's internal message scan.",
                "Live status count differs from PAH's internal message scan.",
                status_messages=status_count,
                loaded_messages=len(messages),
            )
        )
    backend_source = Path(agent_hub.__file__).read_text(encoding="utf-8", errors="replace")
    urgent_breakthrough_tokens = [
        'urgent_events = [event for event in all_events if event["kind"] == "urgent_codex_request"]',
        'delivery_config["provider"] = "log_only"',
        'baseline_events = [event for event in events if event["kind"] != "urgent_codex_request"]',
        '"urgent_breakthrough_logged": urgent_breakthrough_logged',
        '"urgent_breakthrough":',
        '"route_status": "urgent_codex_request"',
        'if is_urgent_codex_request_message(latest):',
        'return "open_on_agent"',
        '"read_state": read_status["state"]',
        '"unread": read_status["unread"]',
    ]
    missing_urgent_tokens = [token for token in urgent_breakthrough_tokens if token not in backend_source]
    findings.append(
        check(
            not missing_urgent_tokens,
            "internal.urgent_breakthrough_hard_channel",
            "Urgent Codex breakthrough channel",
            "Urgent Codex requests bypass optional notification disablement and normal baseline suppression.",
            "Urgent Codex requests may still be treated as optional notifications.",
            missing_tokens=missing_urgent_tokens,
        )
    )
    archive_state = agent_hub.load_thread_archive_state()
    focus = agent_hub.build_thread_focus(messages, archive_state)
    focus_counts = focus.get("counts", {})
    actual_focus = {
        "open_on_darrin": len(focus.get("open_on_darrin", []) or []),
        "open_on_agent": len(focus.get("open_on_agent", []) or []),
        "owner_unknown": len(focus.get("owner_unknown", []) or []),
    }
    focus_mismatches = {
        key: {"count": focus_counts.get(key), "actual": value}
        for key, value in actual_focus.items()
        if int(focus_counts.get(key, 0) or 0) != value
    }
    findings.append(
        check(
            not focus_mismatches,
            "internal.thread_focus_counts",
            "Thread focus count integrity",
            "Thread focus counts match the rendered thread lists.",
            "Thread focus counts do not match the rendered thread lists.",
            mismatches=focus_mismatches,
        )
    )
    boxes = agent_hub.build_agent_mailbox_messages(messages, read_state)
    visible_ids = {item.get("message_id", "") for items in boxes.values() for item in items}
    loaded_ids = {message.message_id for message in messages}
    unknown_visible = sorted(visible_ids - loaded_ids)
    findings.append(
        check(
            not unknown_visible,
            "internal.agent_mailbox_ids",
            "Agent mailbox IDs",
            "All visible agent-mailbox cards map back to loaded messages.",
            "Some visible agent-mailbox cards do not map back to loaded messages.",
            unknown_visible_ids=unknown_visible[:20],
        )
    )
    archive_preview = agent_hub.archive_read_codex_inbox_messages(actor="pah_inspector", dry_run=True)
    findings.append(
        check(
            archive_preview.get("protocol_version") == 2,
            "internal.archive_protocol",
            "Archive-read protocol",
            "Archive-read dry-run returns protocol v2.",
            "Archive-read dry-run did not return protocol v2.",
            preview={key: archive_preview.get(key) for key in sorted(archive_preview) if key != "moved"},
        )
    )
    if int(archive_preview.get("count", 0) or 0) > 0:
        findings.append(
            warn(
                "internal.archive_candidates",
                "Archive-read candidates",
                f"Archive-read dry-run found {archive_preview.get('count')} movable read message(s).",
                "Review the candidates, then use PAH Archive read if the moves are expected.",
                count=archive_preview.get("count", 0),
                moved=archive_preview.get("moved", [])[:10],
            )
        )
    else:
        findings.append(passed("internal.archive_candidates", "Archive-read candidates", "No read messages are currently movable."))
    return findings


def parse_jsonl(path: Path, max_lines: int | None = 5000) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    selected_lines = lines if max_lines is None else lines[-max_lines:]
    events: list[dict[str, Any]] = []
    for line in selected_lines:
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            payload = {"event_type": "invalid_jsonl", "raw": line[:240]}
        events.append(payload)
    return events


def inspect_ledger() -> list[Finding]:
    findings: list[Finding] = []
    events = parse_jsonl(agent_hub.INTERACTION_LEDGER_PATH)
    all_events = parse_jsonl(agent_hub.INTERACTION_LEDGER_PATH, max_lines=None)
    findings.append(
        check(
            bool(events),
            "ledger.exists",
            "Interaction ledger readability",
            "Interaction ledger exists and contains readable events.",
            "Interaction ledger is missing or empty.",
            path=str(agent_hub.INTERACTION_LEDGER_PATH),
            event_count=len(events),
        )
    )
    invalid = [event for event in events if event.get("event_type") == "invalid_jsonl"]
    findings.append(
        check(
            not invalid,
            "ledger.jsonl_valid",
            "Interaction ledger JSONL validity",
            "Recent interaction ledger lines are valid JSON.",
            "Recent interaction ledger contains invalid JSON lines.",
            invalid_count=len(invalid),
            examples=invalid[:3],
        )
    )
    event_types = {str(event.get("event_type", "")) for event in events}
    required = {"message_sent", "archive_read_sweep_started", "archive_read_sweep_finished", "steward_check_finished"}
    missing = sorted(required - event_types)
    findings.append(
        check(
            not missing,
            "ledger.required_events",
            "Interaction ledger event coverage",
            "Recent ledger includes core send/archive/steward events.",
            "Recent ledger is missing one or more core event types.",
            missing=missing,
            recent_event_types=sorted(event_types),
        )
    )
    protocol_events = [
        event
        for event in all_events
        if str(event.get("thread_id", "")) == "PAH-MAILBOX-PROTOCOL-V3"
        and str(event.get("event_type", "")) == "message_sent"
    ]
    findings.append(
        check(
            len(protocol_events) >= 2,
            "ledger.protocol_v3_messages",
            "Protocol v3 message ledgering",
            "CD and CC protocol-v3 coordination messages are present in the ledger.",
            "Expected protocol-v3 CD/CC messages were not found in the ledger.",
            found=len(protocol_events),
            messages=[event.get("message_id", "") for event in protocol_events[-4:]],
        )
    )
    return findings


def supported_post_routes() -> set[str]:
    return {
        "/api/test-notification",
        "/api/write-decision-queue",
        "/api/run-diagnostics",
        "/api/run-inspector",
        "/api/run-communication-speed-test",
        "/api/clear-diagnostics",
        "/api/launch-refresh/heartbeat",
        "/api/launch-refresh/request",
        "/api/launch-refresh/ack",
        "/api/cleanup-inbox-accumulation",
        "/api/archive-read-codex-inbox",
        "/api/agent-no-mail-claim",
        "/api/send",
        "/api/create-message",
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
    }


def supported_get_routes() -> set[str]:
    return {
        "/",
        "/api/status",
        "/api/cockpit",
        "/api/health",
        "/api/tray-status",
        "/api/inspector-report",
        "/api/cc-activity",
        "/api/open",
        "/api/message",
        "/api/interaction-ledger",
    }


def inspect_ui_wiring() -> list[Finding]:
    findings: list[Finding] = []
    html = agent_hub.UI_PATH.read_text(encoding="utf-8", errors="replace") if agent_hub.UI_PATH.exists() else ""
    findings.append(
        check(
            bool(html),
            "ui.file_readable",
            "Dashboard UI file",
            "Dashboard UI file is present and readable.",
            "Dashboard UI file is missing or unreadable.",
            path=str(agent_hub.UI_PATH),
        )
    )
    required_ids = [
        "stewardPanel",
        "trustStrip",
        "summaryStrip",
        "archiveRead",
        "cleanupInboxes",
        "agentList",
        "actionList",
        "inboxStrip",
        "detailTitle",
        "detailSummary",
        "messagePreview",
        "queueCount",
        "queueSearch",
        "deleteVisible",
        "openInspector",
        "inspectorPanel",
        "inspectorSummary",
        "inspectorFindings",
        "inspectorMarkdown",
        "openMessage",
        "openFolder",
        "copyPath",
        "snoozeAlert",
        "refresh",
    ]
    missing_ids = [dom_id for dom_id in required_ids if f'id="{dom_id}"' not in html and f"id='{dom_id}'" not in html]
    findings.append(
        check(
            not missing_ids,
            "ui.required_controls",
            "Required dashboard controls",
            "Required dashboard panels and controls are present.",
            "Dashboard is missing required controls or panels.",
            missing_ids=missing_ids,
        )
    )
    post_paths = set(re.findall(r"postJson\(\s*['\"]([^'\"]+)['\"]", html))
    fetch_paths = set(re.findall(r"fetch\(\s*`?['\"]?(/api/[A-Za-z0-9?&=/${}._\\-]+)", html))
    static_fetch_paths = {path.split("?")[0].split("${")[0] for path in fetch_paths}
    unsupported_posts = sorted(path for path in post_paths if path not in supported_post_routes())
    unsupported_gets = sorted(
        path for path in static_fetch_paths
        if path and path not in supported_get_routes() and path not in supported_post_routes()
    )
    findings.append(
        check(
            not unsupported_posts,
            "ui.post_routes_supported",
            "Dashboard POST route support",
            "Every dashboard postJson route is supported by the backend.",
            "Dashboard calls unsupported POST routes.",
            unsupported_posts=unsupported_posts,
            post_paths=sorted(post_paths),
        )
    )
    findings.append(
        check(
            not unsupported_gets,
            "ui.fetch_routes_supported",
            "Dashboard fetch route support",
            "Every static dashboard fetch route is supported by the backend.",
            "Dashboard calls unsupported fetch routes.",
            unsupported_gets=unsupported_gets,
            fetch_paths=sorted(static_fetch_paths),
        )
    )
    compatibility_routes = sorted({"/api/send", "/api/message-read-state", "/api/mark-all-read"} & (post_paths | static_fetch_paths))
    unsupported_compatibility = sorted(path for path in compatibility_routes if path not in supported_post_routes())
    findings.append(
        check(
            not unsupported_compatibility,
            "ui.compatible_mailroom_routes",
            "Mailroom route compatibility",
            "Dashboard mailroom compatibility routes are supported by the backend.",
            "Dashboard calls mailroom compatibility routes the backend does not support.",
            compatibility_routes=compatibility_routes,
            unsupported_compatibility=unsupported_compatibility,
        )
    )
    inspector_panel_tokens = [
        'id="openInspector"',
        'id="inspectorPanel"',
        'class="inspector-overlay"',
        "async function openInspectorPanel",
        "function renderInspectorPanel",
        "fetch('/api/inspector-report')",
        "id=\"openInspectorReport\"",
        "id=\"closeInspector\"",
        "closeInspectorPanel();",
    ]
    missing_inspector_tokens = [token for token in inspector_panel_tokens if token not in html]
    findings.append(
        check(
            not missing_inspector_tokens,
            "ui.inspector_panel_actionable",
            "Inspector panel actionability",
            "Main-screen Inspector button opens a full-screen report panel wired to the latest Inspector report.",
            "Inspector button or full-screen panel wiring is incomplete.",
            missing_tokens=missing_inspector_tokens,
        )
    )
    steward_required_tokens = [
        "Steward & Mailboxes",
        "const progress = cockpit?.agent_progress || {};",
        "const progressCards = Array.isArray(progress.cards) ? progress.cards : [];",
        "recommended_action",
        "diag-progress-",
        "function focusQueueItem",
        "data-diagnostic-id",
        "data-action-target",
        "steward-card-action",
        "diag-periodic-monitor",
        "diag-archive-sweep",
        "diag-discrepancy",
        'id="ccActivityPanel"',
        "function renderCcActivityPanel",
        "async function checkCcActivityNow",
        "fetch('/api/cc-activity')",
        "latest_disk_write_age_seconds",
        "mailbox_evidence",
        "label: 'Queue'",
        "focusPanel('all')",
        "focusQueueItem('diagnostics'",
    ]
    missing_steward_tokens = [token for token in steward_required_tokens if token not in html]
    steward_cards_are_buttons = '<button class="steward-card' in html
    findings.append(
        check(
            steward_cards_are_buttons and not missing_steward_tokens,
            "ui.steward_cards_actionable",
            "Steward summary card actionability",
            "Steward summary cards expose actionable diagnostic navigation.",
            "Steward summary cards may look clickable without being wired to diagnostic detail.",
            cards_are_buttons=steward_cards_are_buttons,
            missing_tokens=missing_steward_tokens,
        )
    )
    queue_severity_tokens = [
        "const urgentCount",
        "const diagnosticsProblems",
        "urgentCount || ownerUnknown || unansweredTotal",
        "? 'err'",
        ": diagnosticsProblems || staleUnread",
        "? 'warn'",
        "const urgentCodex",
        "urgentCodex || openOnAgent || ownerUnknown",
        "failedChecks || warnChecks || staleUnread",
    ]
    missing_queue_severity_tokens = [token for token in queue_severity_tokens if token not in html]
    findings.append(
        check(
            not missing_queue_severity_tokens,
            "ui.queue_chip_severity_semantics",
            "Queue chip severity semantics",
            "Queue chip reserves red for critical communication risk and yellow for diagnostics or stale-read concerns.",
            "Queue chip severity may no longer match PAH's green/yellow/red status contract.",
            missing_tokens=missing_queue_severity_tokens,
        )
    )
    health_chip_tokens = [
        '<button class="gbtn health-chip unknown" id="healthApi"',
        'data-health-target="api"',
        'data-health-target="routes"',
        'data-health-target="queue"',
        'data-health-target="ledger"',
        "setHealthChip('healthLedger'",
        "function focusHealthChip",
        "function focusRoutesHealth",
        "focusQueueItem('diagnostics', 'diag-discrepancy')",
        "focusQueueItem('diagnostics', 'diag-suite')",
        "focusPanel('all')",
    ]
    missing_health_chip_tokens = [token for token in health_chip_tokens if token not in html]
    findings.append(
        check(
            not missing_health_chip_tokens,
            "ui.health_chips_actionable",
            "Top status chip actionability",
            "Top API, Routes, Queue, and Ledger status chips are real buttons wired to drilldown views.",
            "Top status chips may look interactive without opening the relevant detail view.",
            missing_tokens=missing_health_chip_tokens,
        )
    )
    footer_failure_tokens = [
        ".diag-action",
        'data-diagnostics-action="failure"',
        "Failure</button>",
        "class=\"diag-text\"",
        "Diagnostics need review: ${esc(fail)} failed",
        "focusQueueItem('diagnostics', 'diag-suite')",
    ]
    missing_footer_failure_tokens = [token for token in footer_failure_tokens if token not in html]
    findings.append(
        check(
            not missing_footer_failure_tokens,
            "ui.footer_failure_actionable",
            "Footer failure actionability",
            "Footer diagnostic failures render as a red Failure pill wired to the diagnostic detail view.",
            "Footer diagnostic failures may still be passive text instead of an actionable alert.",
            missing_tokens=missing_footer_failure_tokens,
        )
    )
    agent_status_tokens = [
        ".agent-note.status-warn",
        ".agent-note.status-ok",
        "border: 1px solid rgba(243, 156, 18, .50)",
        "border: 1px solid rgba(127, 176, 105, .48)",
        "background: var(--field)",
        "color: var(--warn)",
        "color: var(--ok)",
        "const mailboxWaiting",
        "function mailboxWaitingCount",
        "const statusPillClass",
        "const dotStatus",
        "? `${mailboxWaiting} unread mail`",
        "? 'review mailbox'",
        "status-warn",
        "statusClass(dotStatus)",
    ]
    missing_agent_status_tokens = [token for token in agent_status_tokens if token not in html]
    findings.append(
        check(
            not missing_agent_status_tokens,
            "ui.agent_status_explains_mailbox_waiting",
            "Participant status label clarity",
            "Participant cards explain mailbox-waiting states with Bible-compliant semantic border/text treatment.",
            "Participant cards may show warning lights without clear unread-mail pill treatment.",
            missing_tokens=missing_agent_status_tokens,
        )
    )
    mailbox_navigation_tokens = [
        "function mailboxMessagesFor",
        "cockpit?.mailbox_messages?.[id]",
        "function mailboxQueue",
        "physicalMessages.concat(threadItems)",
        "data-agent-mailbox-waiting",
        "focusMailbox(agentId)",
        "['darrin', 'Darrin', 'open on you']",
        "const mailboxWaiting = id === 'darrin' ? 0 : mailboxWaitingCount(id)",
        "mailboxWaiting || openThreadsForMailbox(id).length",
    ]
    missing_mailbox_navigation_tokens = [token for token in mailbox_navigation_tokens if token not in html]
    findings.append(
        check(
            not missing_mailbox_navigation_tokens,
            "ui.mailbox_waiting_navigation",
            "Unread mailbox navigation wiring",
            "Unread physical mailbox items are rendered as selectable mailbox cards and participant clicks route to them.",
            "Participant or mailbox-grid clicks may not open unread physical mailbox items.",
            missing_tokens=missing_mailbox_navigation_tokens,
        )
    )
    urgent_breakthrough_tokens = [
        "const urgent = (cockpit?.action_queue || []).find(item => item.kind === 'urgent')",
        "URGENT Codex request active",
        "if (item.kind === 'urgent')",
        "Urgent Codex requests cannot be snoozed",
        "const isUrgent = kind === 'urgent'",
        "const isWake = kind === 'wake' || isUrgent",
        "&& !isUrgent",
        "queueFilter = 'you';",
    ]
    missing_urgent_breakthrough_tokens = [token for token in urgent_breakthrough_tokens if token not in html]
    findings.append(
        check(
            not missing_urgent_breakthrough_tokens,
            "ui.urgent_breakthrough_focus",
            "Urgent Codex dashboard breakthrough",
            "Urgent Codex requests force the dashboard into the My threads view and cannot be hidden by snooze.",
            "Urgent Codex requests may be hidden by the current dashboard view, search, or local snooze state.",
            missing_tokens=missing_urgent_breakthrough_tokens,
        )
    )
    try:
        script_match = re.search(r"<script>(.*)</script>", html, re.DOTALL | re.IGNORECASE)
        if script_match:
            # This is a structural sanity check, not a full JavaScript parser.
            script = script_match.group(1)
            findings.append(
                check(
                    script.count("{") == script.count("}") and script.count("(") == script.count(")"),
                    "ui.script_balance",
                    "Dashboard script structure",
                    "Dashboard script delimiters look structurally balanced enough for a smoke check.",
                    "Dashboard script delimiter balance looks suspicious.",
                    braces={"open": script.count("{"), "close": script.count("}")},
                    parens={"open": script.count("("), "close": script.count(")")},
                )
            )
    except re.error as exc:
        findings.append(fail("ui.script_balance", "Dashboard script structure", "Could not inspect dashboard script.", error=str(exc)))
    return findings


def inspect_protocol_state(payloads: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    cockpit = payloads.get("cockpit")
    if not cockpit:
        findings.append(
            warn(
                "protocol.live_state_unavailable",
                "Live protocol state",
                "Live cockpit payload was unavailable, so communication backlog checks were skipped.",
                "Run the inspector against the live PAH server before relying on protocol/backlog status.",
            )
        )
        return findings
    counts = cockpit.get("cockpit_state", {}).get("counts", {})
    open_on_agent = int(counts.get("open_on_agent", 0) or 0)
    owner_unknown = int(counts.get("owner_unknown", 0) or 0)
    stale_unread = int(counts.get("stale_unread", 0) or 0)
    if owner_unknown:
        findings.append(
            warn(
                "protocol.communication_backlog",
                "Communication backlog",
                f"PAH reports {open_on_agent} open-on-agent and {owner_unknown} owner-unknown thread(s).",
                "Ask the owning agent for a concise PAH-visible reply or use Codex/PAH reconciliation before manual archaeology.",
                open_on_agent=open_on_agent,
                owner_unknown=owner_unknown,
                threads=(cockpit.get("thread_focus", {}).get("open_on_agent", []) or [])[:8],
            )
        )
    else:
        findings.append(
            passed(
                "protocol.communication_backlog",
                "Communication backlog",
                f"Ownership is known. Open-on-agent backlog is advisory only: {open_on_agent}.",
            )
        )
    if stale_unread:
        findings.append(
            warn(
                "protocol.stale_unread",
                "Stale unread mailbox items",
                f"PAH reports {stale_unread} stale unread item(s).",
                "Use PAH thread focus and mailbox grids to drive CD/CC replies instead of manual folder searching.",
                stale_unread=stale_unread,
            )
        )
    else:
        findings.append(passed("protocol.stale_unread", "Stale unread mailbox items", "No stale unread items."))
    return findings


def summarize(findings: list[Finding]) -> dict[str, Any]:
    counts = {"pass": 0, "warn": 0, "fail": 0}
    for finding in findings:
        counts[finding.status] = counts.get(finding.status, 0) + 1
    if counts["fail"]:
        overall = "fail"
    elif counts["warn"]:
        overall = "warn"
    else:
        overall = "pass"
    return {"overall": overall, "counts": counts}


def markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# PAH Inspector Report",
        "",
        f"- Generated: `{report['generated_at']}`",
        f"- URL: `{report['url']}`",
        f"- Overall: `{report['summary']['overall']}`",
        f"- Counts: pass `{report['summary']['counts']['pass']}`, warn `{report['summary']['counts']['warn']}`, fail `{report['summary']['counts']['fail']}`",
        "",
        "## Findings",
        "",
    ]
    for finding in report["findings"]:
        lines.append(f"### [{finding['status'].upper()}] {finding['title']}")
        lines.append("")
        lines.append(f"{finding['summary']}")
        if finding.get("recommendation"):
            lines.append("")
            lines.append(f"Recommendation: {finding['recommendation']}")
        detail = finding.get("detail") or {}
        if detail:
            lines.append("")
            lines.append("```json")
            lines.append(json.dumps(detail, indent=2, sort_keys=True))
            lines.append("```")
        lines.append("")
    return "\n".join(lines)


def write_reports(report: dict[str, Any]) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    LATEST_JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    LATEST_MD_PATH.write_text(markdown_report(report), encoding="utf-8")
    with HISTORY_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(report, sort_keys=True) + "\n")


def run_inspector(url: str = DEFAULT_URL, live: bool = True) -> dict[str, Any]:
    started = time.perf_counter()
    findings: list[Finding] = []
    payloads: dict[str, Any] = {}
    if live:
        live_findings, payloads = inspect_live_endpoints(url)
        findings.extend(live_findings)
    findings.extend(inspect_internal_contracts(payloads.get("status")))
    findings.extend(inspect_ledger())
    findings.extend(inspect_ui_wiring())
    if live:
        findings.extend(inspect_protocol_state(payloads))
    report = {
        "schema_version": 1,
        "generated_at": now_iso(),
        "url": url,
        "duration_ms": int((time.perf_counter() - started) * 1000),
        "summary": summarize(findings),
        "findings": [finding.as_dict() for finding in findings],
        "paths": {
            "latest_json": str(LATEST_JSON_PATH),
            "latest_markdown": str(LATEST_MD_PATH),
            "history": str(HISTORY_PATH),
        },
    }
    write_reports(report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deep PAH internal, endpoint, mailbox, ledger, and UX wiring checks.")
    parser.add_argument("--url", default=DEFAULT_URL, help="PAH base URL for live endpoint checks.")
    parser.add_argument("--offline", action="store_true", help="Skip live HTTP endpoint checks.")
    parser.add_argument("--json", action="store_true", help="Print full JSON report.")
    args = parser.parse_args()
    report = run_inspector(url=args.url, live=not args.offline)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        summary = report["summary"]
        print(
            f"PAH Inspector {summary['overall']}: "
            f"{summary['counts']['pass']} pass, {summary['counts']['warn']} warn, {summary['counts']['fail']} fail"
        )
        print(f"JSON: {report['paths']['latest_json']}")
        print(f"Markdown: {report['paths']['latest_markdown']}")
    return 1 if report["summary"]["counts"]["fail"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
