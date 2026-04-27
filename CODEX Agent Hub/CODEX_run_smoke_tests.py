"""Smoke tests for PANDA Agent Hub core contracts.

These tests are intentionally dependency-free and avoid live agent, SMS, API,
or Panda Gallery writes.
"""

from __future__ import annotations

from pathlib import Path
import json
import subprocess
import sys
from tempfile import TemporaryDirectory

from pah_core import MESSAGE_SCHEMA_VERSION
from pah_core.decisions import decision_is_active, decision_state_summary, set_decision_state
from pah_core.participants import route_participants
from pah_core.schema import extract_message_metadata, metadata_waits_on_darrin, render_message_markdown, validate_message_text
from pah_core.validation_state import (
    set_validation_state,
    validation_is_active,
    validation_key,
    validation_state_summary,
)
from pah_core.work_items import create_work_item, update_work_item, work_board_status
from pah_mailbox.atomic import atomic_write_text
from pah_mailbox.backpressure import MailboxMessageRef, detect_backpressure
from pah_mailbox.idempotency import processed_message_event_status, record_processed_message_event
from pah_adapters.registry import adapter_status
from pah_diagnostics.checks import run_communication_diagnostics
from pah_diagnostics.route_tests import route_test_status, save_route_test_state
from pah_mailbox.quarantine import validate_quarantine_candidate, validate_quarantine_reason
from pah_security.approvals import canonical_request_hash, validate_approval_record
from pah_security.path_scope import classify_path


def assert_true(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)


def test_schema_roundtrip() -> None:
    text = render_message_markdown(
        {
            "schema_version": MESSAGE_SCHEMA_VERSION,
            "id": "PAH-TEST-001",
            "thread_id": "PAH-THREAD-001",
            "created_at": "2026-04-27T02:00:00-07:00",
            "from": "codex",
            "to": "claude-code",
            "type": "response_request",
            "priority": "high",
            "status": "open",
            "thread_status": "waiting_on_agent",
            "approval_boundary": "coordination_only",
            "requires_darrin_decision": False,
            "reply_to": ["PAH-PARENT-001"],
        },
        "Codex to Claude Code: test",
        "Roundtrip test",
        "No live adapter involved.",
    )
    metadata = extract_message_metadata(text)
    issues = validate_message_text(text, "smoke.md")
    assert_true(metadata["id"] == "PAH-TEST-001", "schema id roundtrip")
    assert_true(metadata["message_id"] == "PAH-TEST-001", "schema message_id roundtrip")
    assert_true(metadata["to"] == "claude-code", "schema participant canonicalization")
    assert_true(not any(issue.level == "warning" for issue in issues), "schema should not warn on valid v1")


def test_current_mailbox_schema_aliases() -> None:
    text = """---
schema_version: 1
id: CC-20260427-020000-pah-v1-final-review
thread_id: AGENT-HUB-V1
from: cc
to: codex
type: recommendation
status: review_complete
created_at: 2026-04-27T02:00:00-07:00
priority: high
action_owner: codex
requires_darrin_decision: true
approval_boundary: coordination_only
---

# CC -> Codex: review
"""
    metadata = extract_message_metadata(text)
    issues = validate_message_text(text, "cc_review.md")
    assert_true(metadata["message_id"] == "CC-20260427-020000-pah-v1-final-review", "id aliases to message_id")
    assert_true(metadata["from"] == "claude-code", "cc alias canonicalizes")
    assert_true(not any(issue.level == "warning" for issue in issues), "current mailbox schema should not warn")


def test_frontmatter_does_not_parse_body_headings() -> None:
    text = """---
schema_version: 1
id: CODEX-TEST-BODY-HEADINGS
thread_id: AGENT-HUB-V1
from: codex
to: claude_desktop
type: report
status: complete
created_at: 2026-04-27T02:00:00-07:00
priority: normal
requires_darrin_decision: false
approval_boundary: coordination_only
---

# Report

Updated file:

- C:\\CODEX PG\\example.md
"""
    metadata = extract_message_metadata(text)
    assert_true("updated_file" not in metadata, "frontmatter parser must not treat body labels as metadata")


def test_standalone_validator_cli() -> None:
    with TemporaryDirectory() as temp_dir:
        message_path = Path(temp_dir) / "message.md"
        message_path.write_text(
            render_message_markdown(
                {
                    "schema_version": MESSAGE_SCHEMA_VERSION,
                    "id": "PAH-VALIDATOR-CLI-001",
                    "thread_id": "PAH-THREAD-001",
                    "created_at": "2026-04-27T02:00:00-07:00",
                    "from": "codex",
                    "to": "claude-code",
                    "type": "report",
                    "priority": "normal",
                    "status": "complete",
                    "approval_boundary": "coordination_only",
                    "requires_darrin_decision": False,
                },
                "Validator CLI smoke",
                "Smoke test",
                "No external validator involved.",
            ),
            encoding="utf-8",
        )
        validator = Path(__file__).with_name("CODEX_pah_validator.py")
        completed = subprocess.run(
            [sys.executable, str(validator), "--json", str(message_path)],
            check=False,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        assert_true(completed.returncode == 0, "validator CLI exits cleanly for valid message")
        assert_true(payload["ok"], "validator CLI reports ok")
        assert_true(payload["results"][0]["metadata"]["id"] == "PAH-VALIDATOR-CLI-001", "validator CLI returns metadata")


def test_decision_gate() -> None:
    mention_only = {"summary": "Ask Darrin later only as context."}
    explicit = {"requires_darrin_decision": True}
    thread_wait = {"thread_status": "waiting_on_darrin"}
    assert_true(not metadata_waits_on_darrin(mention_only), "mention-only metadata must not trigger Darrin queue")
    assert_true(metadata_waits_on_darrin(explicit), "explicit Darrin flag should trigger queue")
    assert_true(metadata_waits_on_darrin(thread_wait), "waiting_on_darrin should trigger queue")


def test_routes_and_scope() -> None:
    assert_true(route_participants("codex_to_claude_code") == ("codex", "claude-code"), "Claude Code route")
    assert_true(classify_path(Path("C:/panda-gallery/test.txt")) == "panda_gallery_requires_darrin", "PG path boundary")


def test_diagnostics() -> None:
    diagnostics = run_communication_diagnostics(write_report=False)
    assert_true("checks" in diagnostics, "diagnostics returns checks")
    assert_true(any(item["name"] == "two_way_file_bridge" for item in diagnostics["checks"]), "diagnostics includes bridge test")


def test_safety_surfaces() -> None:
    request_hash = canonical_request_hash(
        "protected_action_requires_darrin",
        ["C:/CODEX PG/example.txt"],
        "example-command",
        "0",
    )
    errors = validate_approval_record(
        {
            "approval_id": "APPROVAL-TEST-001",
            "scope": "protected_action_requires_darrin",
            "exact_paths": ["C:/CODEX PG/example.txt"],
            "command_or_provider": "example-command",
            "budget": "0",
            "expires_at": "2099-01-01T00:00:00+00:00",
            "one_time_use": True,
            "approver": "Darrin",
            "revoked": False,
            "request_hash": request_hash,
        }
    )
    assert_true(not errors, "valid approval record should pass")
    adapters = adapter_status()
    assert_true(adapters["enabled"] == 0, "live adapters must stay disabled by default")
    try:
        validate_quarantine_candidate(Path("C:/panda-gallery/not-mailbox.md"))
    except ValueError:
        pass
    else:
        raise AssertionError("quarantine must reject files outside the PAH mailbox")
    assert_true(validate_quarantine_reason("schema_invalid") == "schema_invalid", "valid quarantine reason passes")
    try:
        validate_quarantine_reason("manual_quarantine")
    except ValueError:
        pass
    else:
        raise AssertionError("quarantine reason enum must be closed")


def test_backpressure_detection() -> None:
    now = 1_000_000.0
    records = [
        MailboxMessageRef(thread_id="THREAD-FLOOD", path=Path(f"C:/CODEX PG/msg_{index}.md"), modified=now - 10)
        for index in range(26)
    ]
    findings = detect_backpressure(records, now=now)
    assert_true(len(findings) == 1, "backpressure emits one finding per flooded thread")
    assert_true(findings[0].reason_code == "flood_threshold_exceeded", "backpressure reason code is stable")
    assert_true("26 messages" in findings[0].message, "backpressure finding includes message count")


def test_processed_message_sidecar_idempotency() -> None:
    with TemporaryDirectory() as temp_dir:
        state_dir = Path(temp_dir) / "processed_messages"
        message_path = Path(temp_dir) / "message.md"
        text = render_message_markdown(
            {
                "schema_version": MESSAGE_SCHEMA_VERSION,
                "id": "PAH-IDEMPOTENCY-001",
                "thread_id": "PAH-THREAD-001",
                "created_at": "2026-04-27T02:00:00-07:00",
                "from": "claude-code",
                "to": "codex",
                "type": "decision_request",
                "priority": "high",
                "status": "blocked",
                "thread_status": "waiting_on_darrin",
                "approval_boundary": "coordination_only",
                "requires_darrin_decision": True,
            },
            "Idempotency smoke",
            "Smoke test",
            "No duplicate notification should be sent for the same content.",
        )
        message_path.write_text(text, encoding="utf-8")

        initial = processed_message_event_status(
            "PAH-IDEMPOTENCY-001",
            message_path,
            text,
            event="notification:darrin_decision_needed",
            state_dir=state_dir,
        )
        assert_true(initial.status == "unseen", "new message event starts unseen")

        record = record_processed_message_event(
            "PAH-IDEMPOTENCY-001",
            message_path,
            text,
            event="notification:darrin_decision_needed",
            outcome="sent",
            state_dir=state_dir,
        )
        assert_true(record["message_id"] == "PAH-IDEMPOTENCY-001", "processed sidecar stores message id")
        assert_true("first_seen_at" in record, "processed sidecar stores first seen timestamp")
        assert_true(initial.sidecar_path.exists(), "processed sidecar is written")

        duplicate = processed_message_event_status(
            "PAH-IDEMPOTENCY-001",
            message_path,
            text,
            event="notification:darrin_decision_needed",
            state_dir=state_dir,
        )
        assert_true(duplicate.status == "already_processed", "same event and content is already processed")

        next_event = processed_message_event_status(
            "PAH-IDEMPOTENCY-001",
            message_path,
            text,
            event="adapter:dry_run",
            state_dir=state_dir,
        )
        assert_true(next_event.status == "new_event", "same message can process a different event")

        changed = text + "\nchanged\n"
        mismatch = processed_message_event_status(
            "PAH-IDEMPOTENCY-001",
            message_path,
            changed,
            event="notification:darrin_decision_needed",
            state_dir=state_dir,
        )
        assert_true(mismatch.status == "content_mismatch", "same message id with changed content is blocked")
        try:
            record_processed_message_event(
                "PAH-IDEMPOTENCY-001",
                message_path,
                changed,
                event="notification:darrin_decision_needed",
                state_dir=state_dir,
            )
        except ValueError:
            pass
        else:
            raise AssertionError("processed sidecar must reject changed content for the same message id")


def test_decision_state() -> None:
    with TemporaryDirectory() as temp_dir:
        state_path = Path(temp_dir) / "decision_state.json"
        item_path = "C:/CODEX PG/CODEX Claude Codex Mailbox/CODEX Inbox/example.md"
        set_decision_state(item_path, "superseded", "smoke test", "codex", "Example", state_path=state_path)
        assert_true(not decision_is_active(item_path, {"items": {item_path: {"state": "superseded"}}}), "superseded item inactive")
        summary = decision_state_summary({"items": {item_path: {"state": "superseded", "updated_at": "2099"}}})
        assert_true(summary["counts"]["superseded"] == 1, "decision summary counts superseded")


def test_validation_state() -> None:
    with TemporaryDirectory() as temp_dir:
        state_path = Path(temp_dir) / "validation_state.json"
        fingerprint = validation_key("C:/CODEX PG/example.md", "ledger", "Important message not found in mailbox ledger")
        set_validation_state(
            fingerprint,
            "accepted_legacy",
            "smoke test",
            "codex",
            "Example",
            "C:/CODEX PG/example.md",
            "ledger",
            "Important message not found in mailbox ledger",
            state_path=state_path,
        )
        assert_true(
            not validation_is_active(fingerprint, {"items": {fingerprint: {"state": "accepted_legacy"}}}),
            "accepted legacy validation inactive",
        )
        summary = validation_state_summary({"items": {fingerprint: {"state": "accepted_legacy", "updated_at": "2099"}}})
        assert_true(summary["counts"]["accepted_legacy"] == 1, "validation summary counts accepted legacy")


def test_route_test_state() -> None:
    with TemporaryDirectory() as temp_dir:
        state_path = Path(temp_dir) / "route_tests.json"
        save_route_test_state(
            {
                "version": 1,
                "tests": {
                    "PAH-ROUTE-TEST-SMOKE": {
                        "test_id": "PAH-ROUTE-TEST-SMOKE",
                        "route": "codex_to_claude_code",
                        "state": "pending_reply",
                        "created_at": "2099-01-01T00:00:00+00:00",
                    }
                },
            },
            state_path,
        )
        status = route_test_status(refresh=False, state_path=state_path)
        assert_true(status["counts"]["pending_reply"] == 1, "route test status counts pending reply")


def test_work_board_state() -> None:
    with TemporaryDirectory() as temp_dir:
        state_path = Path(temp_dir) / "work_items.json"
        inbox_path = Path(temp_dir) / "CODEX Inbox"
        inbox_path.mkdir()
        item = create_work_item("Smoke work item", owner="claude-code", priority="high", state_path=state_path)
        updated = update_work_item(
            item["item_id"],
            state="in_progress",
            dispatch={"route": "codex_to_claude_code", "message_id": "PAH-SMOKE", "path": "C:/CODEX PG/test.md"},
            state_path=state_path,
        )
        reply = inbox_path / "reply.md"
        atomic_write_text(reply, f"# Reply\n\nThread-ID: {item['item_id']}\nReply-To: PAH-SMOKE\n")
        board = work_board_status(state_path, inbox_path=inbox_path)
        assert_true(updated["state"] == "in_progress", "work item state updates")
        assert_true(updated["dispatch"]["message_id"] == "PAH-SMOKE", "work item stores dispatch metadata")
        assert_true(board["counts"]["total"] == 1, "work board counts item")
        assert_true(board["counts"]["by_owner"]["claude-code"] == 1, "work board counts owner")
        assert_true(board["items"][0]["state"] == "review", "reply moves work item to review")
        assert_true(board["items"][0]["last_reply_path"] == str(reply), "reply path is stored")


def main() -> None:
    test_schema_roundtrip()
    test_current_mailbox_schema_aliases()
    test_frontmatter_does_not_parse_body_headings()
    test_standalone_validator_cli()
    test_decision_gate()
    test_routes_and_scope()
    test_diagnostics()
    test_safety_surfaces()
    test_backpressure_detection()
    test_processed_message_sidecar_idempotency()
    test_decision_state()
    test_validation_state()
    test_route_test_state()
    test_work_board_state()
    print("PAH smoke tests passed")


if __name__ == "__main__":
    main()
