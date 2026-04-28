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

import CODEX_agent_hub as agent_hub
from pah_core import MESSAGE_SCHEMA_VERSION
from pah_core.decisions import decision_is_active, decision_state_summary, set_decision_state
from pah_core.participants import route_participants
from pah_core.read_state import message_read_status, read_state_summary, set_message_read_state
from pah_core.schema import extract_message_metadata, metadata_waits_on_darrin, render_message_markdown, validate_message_text
from pah_core.thread_archive import archive_thread, thread_archive_status, thread_archive_summary, unarchive_thread
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
from pah_adapters.headless_contract import (
    HEADLESS_DEFAULT_TIMEOUT_SECONDS,
    HEADLESS_SIGKILL_GRACE_SECONDS,
    canonical_headless_command_args,
    canonical_headless_command_preview,
    headless_capture_contract,
    validate_headless_command_contract,
)
from pah_adapters.registry import adapter_status
from pah_core.cross_check import cross_check_auto_resolution_status
from pah_diagnostics.checks import run_communication_diagnostics
from pah_diagnostics.route_tests import reply_search_dirs_for_route, route_test_status, save_route_test_state
from pah_mailbox.paths import CC_CLAUDE_INBOX, CC_INBOX, CLAUDE_CODE_INBOX, MESSAGE_DIRS, ROUTE_INBOXES
from pah_mailbox.quarantine import quarantine_message, validate_quarantine_candidate, validate_quarantine_reason
from pah_security.approvals import (
    MCP_READONLY_CONFIG_PATH,
    approval_record_hash,
    approval_check,
    bind_approval_record_hashes,
    canonical_request_hash,
    canonical_mcp_config_hash,
    command_hash,
    enforce_protected_action,
    mark_approval_consumed,
    validate_approval_record,
)
from pah_security.path_scope import classify_path


def assert_true(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)


def darrin_decision_source(message_id: str = "DARRIN-DECISION-TEST-001") -> dict[str, str]:
    return {
        "source_message_id": message_id,
        "source_message_type": "decision_record",
        "source_message_from": "darrin",
        "source_message_to": "pah",
    }


def stamp_approval_record(record: dict[str, object], approved_at: str = "2026-04-27T02:00:00-07:00") -> dict[str, object]:
    return bind_approval_record_hashes(
        {
            **record,
            "approved_by": "Darrin",
            "approved_at": approved_at,
        }
    )


def headless_approval_record(message_id: str = "DARRIN-DECISION-HEADLESS-001") -> dict[str, object]:
    scope = "headless_agent_requires_darrin"
    record: dict[str, object] = {
        "approval_id": "APPROVAL-HEADLESS-001",
        "scope": scope,
        "exact_paths": [],
        "command_or_provider": "",
        "command_preview": "",
        "budget": "0",
        "budget_usd": "0",
        "expires_at": "2099-01-01T00:00:00+00:00",
        "one_time_use": True,
        "approver": "Darrin",
        "revoked": False,
        "request_hash": "",
        "strict_mcp_config": True,
        "mcp_config_path": str(MCP_READONLY_CONFIG_PATH),
        "mcp_config_expected_hash": canonical_mcp_config_hash(),
        "prompt_file": "C:/CODEX PG/CODEX Agent Hub/CODEX state/headless/prompts/APPROVAL-HEADLESS-001.md",
        "allowed_tools": ["Read", "Grep", "Glob", "WebFetch"],
        "disallowed_tools": ["Bash", "Write", "Edit", "MultiEdit"],
        "settings_path": "C:/CODEX PG/CODEX Agent Hub/CODEX config/CODEX_pah_headless_settings.json",
        "worktree_path": "C:/CODEX PG/CODEX Agent Hub/CODEX state/headless/worktrees/APPROVAL-HEADLESS-001",
        "audit_stdout_path": "C:/CODEX PG/CODEX Agent Hub/CODEX logs/headless/APPROVAL-HEADLESS-001.stdout.jsonl",
        "audit_stderr_path": "C:/CODEX PG/CODEX Agent Hub/CODEX logs/headless/APPROVAL-HEADLESS-001.stderr.log",
        "audit_exit_code_path": "C:/CODEX PG/CODEX Agent Hub/CODEX logs/headless/APPROVAL-HEADLESS-001.exit_code.json",
        **darrin_decision_source(message_id),
    }
    command = canonical_headless_command_preview(record)
    record["command_or_provider"] = command
    record["command_preview"] = command
    record["request_hash"] = canonical_request_hash(scope, [], command, "0")
    return stamp_approval_record(record)


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


def test_source_folder_spoofing_detection() -> None:
    with TemporaryDirectory() as temp_dir:
        spoof_path = Path(temp_dir) / "spoof.md"
        spoof_path.write_text(
            render_message_markdown(
                {
                    "schema_version": MESSAGE_SCHEMA_VERSION,
                    "id": "PAH-SPOOF-001",
                    "thread_id": "PAH-SPOOF-THREAD",
                    "created_at": "2026-04-27T02:00:00-07:00",
                    "from": "codex",
                    "to": "codex",
                    "type": "report",
                    "priority": "normal",
                    "status": "complete",
                    "thread_status": "active",
                    "approval_boundary": "coordination_only",
                    "requires_darrin_decision": False,
                },
                "Spoof smoke",
                "Spoof check.",
                "A Codex-claimed message in the Claude to Codex lane should be flagged.",
            ),
            encoding="utf-8",
        )
        spoof_msg = agent_hub.parse_message(spoof_path, "Claude -> Codex")
        spoof_issues = agent_hub.validate_mailbox([spoof_msg])
        assert_true(any(item["category"] == "spoofing" for item in spoof_issues), "source spoofing is detected")
        assert_true(
            any(item["quarantine_reason"] == "spoofing_attempt" for item in spoof_issues),
            "source spoofing maps to quarantine reason",
        )

        valid_path = Path(temp_dir) / "cc_to_codex.md"
        valid_path.write_text(
            render_message_markdown(
                {
                    "schema_version": MESSAGE_SCHEMA_VERSION,
                    "id": "PAH-SPOOF-VALID-001",
                    "thread_id": "PAH-SPOOF-THREAD",
                    "created_at": "2026-04-27T02:00:00-07:00",
                    "from": "cc",
                    "to": "codex",
                    "type": "report",
                    "priority": "normal",
                    "status": "complete",
                    "thread_status": "active",
                    "approval_boundary": "coordination_only",
                    "requires_darrin_decision": False,
                },
                "CC to Codex smoke",
                "Legitimate CC message.",
                "The current mailbox still accepts cc as a Claude Code alias.",
            ),
            encoding="utf-8",
        )
        valid_msg = agent_hub.parse_message(valid_path, "Claude -> Codex")
        valid_issues = agent_hub.validate_mailbox([valid_msg])
        assert_true(not any(item["category"] == "spoofing" for item in valid_issues), "cc alias is not spoofing")

        desktop_legacy_path = Path(temp_dir) / "claude_desktop_legacy.md"
        desktop_legacy_path.write_text(
            render_message_markdown(
                {
                    "schema_version": MESSAGE_SCHEMA_VERSION,
                    "id": "PAH-SPOOF-VALID-002",
                    "thread_id": "PAH-SPOOF-THREAD",
                    "created_at": "2026-04-27T02:00:00-07:00",
                    "from": "Claude (Desktop)",
                    "to": "codex",
                    "type": "report",
                    "priority": "normal",
                    "status": "complete",
                    "thread_status": "active",
                    "approval_boundary": "coordination_only",
                    "requires_darrin_decision": False,
                },
                "Claude Desktop legacy smoke",
                "Legitimate Claude Desktop message.",
                "Legacy display aliases should canonicalize before source-route checks.",
            ),
            encoding="utf-8",
        )
        desktop_legacy_msg = agent_hub.parse_message(desktop_legacy_path, "Claude -> Codex")
        desktop_legacy_issues = agent_hub.validate_mailbox([desktop_legacy_msg])
        assert_true(
            not any(item["category"] == "spoofing" for item in desktop_legacy_issues),
            "Claude Desktop legacy alias is not spoofing",
        )


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


def test_cross_check_auto_resolution_rule() -> None:
    base_metadata = {
        "schema_version": MESSAGE_SCHEMA_VERSION,
        "id": "PAH-CROSS-CHECK-001",
        "thread_id": "PAH-CROSS-CHECK-THREAD",
        "created_at": "2026-04-27T02:00:00-07:00",
        "from": "codex",
        "to": "claude-code",
        "type": "cross_check",
        "priority": "normal",
        "status": "review_complete",
        "thread_status": "active",
        "approval_boundary": "coordination_only",
        "requires_darrin_decision": False,
        "agrees_with": ["CC-LOW-RISK-001"],
        "disagrees_with": [],
        "caught_by_one": ["CC-LOW-RISK-001 risk=low"],
        "recommendation": "auto_resolve",
        "auto_resolution": True,
    }
    eligible_text = render_message_markdown(
        base_metadata,
        "Cross-check smoke",
        "Low-risk agreement.",
        "No Darrin-gated boundary involved.",
    )
    eligible_metadata = extract_message_metadata(eligible_text)
    eligible_status = cross_check_auto_resolution_status(eligible_metadata)
    eligible_issues = validate_message_text(eligible_text, "cross_check.md")
    assert_true(eligible_status["eligible"], "low-risk cross_check is auto-resolution eligible")
    assert_true(
        not any("cross_check auto-resolution blocked" in issue.message for issue in eligible_issues),
        "eligible cross_check does not warn",
    )

    medium_text = render_message_markdown(
        dict(base_metadata, caught_by_one=["CC-MEDIUM-RISK-001 risk=medium"]),
        "Cross-check medium risk",
        "Medium risk.",
        "Medium risk blocks auto-resolution.",
    )
    medium_issues = validate_message_text(medium_text, "cross_check.md")
    assert_true(
        any("risk must be low only" in issue.message for issue in medium_issues),
        "medium caught_by_one risk blocks auto-resolution",
    )

    disagreement_text = render_message_markdown(
        dict(base_metadata, disagrees_with=["CLAUDE-DISAGREE-001"]),
        "Cross-check disagreement",
        "Disagreement.",
        "Any disagreement blocks auto-resolution.",
    )
    disagreement_issues = validate_message_text(disagreement_text, "cross_check.md")
    assert_true(
        any("disagrees_with must be empty" in issue.message for issue in disagreement_issues),
        "nonempty disagrees_with blocks auto-resolution",
    )

    darrin_boundary_text = render_message_markdown(
        dict(base_metadata, approval_boundary="protected_action_requires_darrin"),
        "Cross-check protected boundary",
        "Protected boundary.",
        "Darrin-gated boundaries block auto-resolution.",
    )
    darrin_boundary_issues = validate_message_text(darrin_boundary_text, "cross_check.md")
    assert_true(
        any("approval_boundary requiring Darrin" in issue.message for issue in darrin_boundary_issues),
        "Darrin-gated approval boundary blocks auto-resolution",
    )
    involved_status = cross_check_auto_resolution_status(
        eligible_metadata,
        [{"approval_boundary": "protected_action_requires_darrin"}],
    )
    assert_true(
        not involved_status["eligible"]
        and any("approval_boundary requiring Darrin" in reason for reason in involved_status["reasons"]),
        "Darrin-gated involved messages block auto-resolution",
    )


def test_routes_and_scope() -> None:
    assert_true(route_participants("codex_to_claude_code") == ("codex", "claude-code"), "Claude Code route")
    assert_true(ROUTE_INBOXES["codex_to_claude_code"] == CLAUDE_CODE_INBOX, "Claude Code route uses configured inbox")
    active_message_paths = [path for _, path in MESSAGE_DIRS]
    assert_true(CC_INBOX in active_message_paths, "active mailbox list includes native CC inbox")
    assert_true(
        not any("legacy" in label.lower() for label, _ in MESSAGE_DIRS),
        "active mailbox list excludes legacy CC inboxes",
    )
    if CC_CLAUDE_INBOX.exists():
        assert_true(
            CC_CLAUDE_INBOX in reply_search_dirs_for_route("codex_to_claude_code"),
            "Claude Code route watches native CC reply inbox",
        )
    assert_true(
        classify_path(CC_INBOX / "message.md") == "panda_gallery_cc_mailbox_approved",
        "CC mailbox path is approved for PAH coordination writes",
    )
    assert_true(classify_path(Path("C:/panda-gallery/test.txt")) == "panda_gallery_requires_darrin", "PG path boundary")


def test_diagnostics() -> None:
    diagnostics = run_communication_diagnostics(write_report=False)
    assert_true("checks" in diagnostics, "diagnostics returns checks")
    assert_true(any(item["name"] == "two_way_file_bridge" for item in diagnostics["checks"]), "diagnostics includes bridge test")


def test_notification_provider_status() -> None:
    config = json.loads(json.dumps(agent_hub.DEFAULT_NOTIFICATION_CONFIG))
    assert_true(
        not agent_hub.provider_is_configured(config, "log_only"),
        "log_only is not a configured live notification provider",
    )
    result = agent_hub.send_notification(config, "Smoke", "Log-only notification should still be testable")
    assert_true(result["provider"] == "log_only", "log_only notification returns log-only provider")

    twilio_config = json.loads(json.dumps(config))
    twilio_config["provider"] = "twilio"
    assert_true(not agent_hub.provider_is_configured(twilio_config, "twilio"), "incomplete Twilio config is not ready")
    twilio_config["twilio"].update(
        {
            "account_sid": "AC00000000000000000000000000000000",
            "auth_token": "secret",
            "from_number": "+15550000001",
            "to_number": "+15550000002",
        }
    )
    assert_true(agent_hub.provider_is_configured(twilio_config, "twilio"), "complete Twilio config is ready")

    email_config = json.loads(json.dumps(config))
    email_config["provider"] = "email_to_sms"
    assert_true(not agent_hub.provider_is_configured(email_config, "email_to_sms"), "incomplete email-to-SMS config is not ready")
    email_config["email_to_sms"].update(
        {
            "smtp_host": "smtp.example.test",
            "from_email": "pah@example.test",
            "to_email": "5550000002@carrier.example",
        }
    )
    assert_true(agent_hub.provider_is_configured(email_config, "email_to_sms"), "complete email-to-SMS config is ready")


def test_safety_surfaces() -> None:
    request_hash = canonical_request_hash(
        "protected_action_requires_darrin",
        ["C:/CODEX PG/example.txt"],
        "example-command",
        "0",
    )
    errors = validate_approval_record(
        stamp_approval_record(
            {
            "approval_id": "APPROVAL-TEST-001",
            "scope": "protected_action_requires_darrin",
            "exact_paths": ["C:/CODEX PG/example.txt"],
            "command_or_provider": "example-command",
            "command_preview": "example-command",
            "budget": "0",
            "expires_at": "2099-01-01T00:00:00+00:00",
            "one_time_use": True,
            "approver": "Darrin",
            "revoked": False,
            "request_hash": request_hash,
            **darrin_decision_source(),
            }
        )
    )
    assert_true(not errors, "valid approval record should pass")
    chained_errors = validate_approval_record(
        stamp_approval_record(
            {
            "approval_id": "APPROVAL-CHAINED-001",
            "scope": "git_commit_requires_darrin",
            "exact_paths": ["C:/CODEX PG/example.txt"],
            "command_or_provider": "example-command",
            "command_preview": "example-command",
            "budget": "0",
            "expires_at": "2099-01-01T00:00:00+00:00",
            "one_time_use": True,
            "approver": "Darrin",
            "revoked": False,
            "request_hash": request_hash,
            "source_message_id": "AUTO-CROSS-CHECK-001",
            "source_message_type": "cross_check",
            "source_message_from": "codex",
            "source_message_to": "pah",
            }
        )
    )
    assert_true(any("decision_record" in error for error in chained_errors), "chained approval source is rejected")
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


def test_quarantine_move_writes_tombstone() -> None:
    with TemporaryDirectory() as temp_dir:
        mailbox_root = Path(temp_dir) / "mailbox"
        inbox = mailbox_root / "CODEX Inbox"
        quarantine_dir = mailbox_root / "PAH Quarantine"
        inbox.mkdir(parents=True)
        message_path = inbox / "bad_message.md"
        message_path.write_text("# Bad message\n\nMissing required metadata.\n", encoding="utf-8")

        try:
            quarantine_message(
                message_path,
                "schema_invalid",
                mailbox_root=mailbox_root,
                quarantine_dir=quarantine_dir,
            )
        except ValueError:
            pass
        else:
            raise AssertionError("quarantine move must require confirmed=true")

        record = quarantine_message(
            message_path,
            "schema_invalid",
            confirmed=True,
            mailbox_root=mailbox_root,
            quarantine_dir=quarantine_dir,
        )
        quarantine_path = Path(record.quarantine_path)
        tombstone_path = Path(record.tombstone_path)
        assert_true(not message_path.exists(), "quarantine move removes original message")
        assert_true(quarantine_path.exists(), "quarantine move writes quarantined copy")
        assert_true(tombstone_path.exists(), "quarantine move writes tombstone")
        tombstone = json.loads(tombstone_path.read_text(encoding="utf-8"))
        assert_true(tombstone["reason"] == "schema_invalid", "tombstone stores reason")
        assert_true(tombstone["original_path"] == str(message_path), "tombstone stores original path")
        try:
            validate_quarantine_candidate(quarantine_path, mailbox_root=mailbox_root, quarantine_dir=quarantine_dir)
        except ValueError:
            pass
        else:
            raise AssertionError("quarantine must reject files already in quarantine")


def test_approval_enforcement() -> None:
    with TemporaryDirectory() as temp_dir:
        approvals_path = Path(temp_dir) / "approvals.jsonl"
        target_path = "C:/CODEX PG/example.txt"
        command = "git commit -m example"
        scope = "git_commit_requires_darrin"
        request_hash = canonical_request_hash(scope, [target_path], command, "0")
        approvals_path.write_text(
            json.dumps(
                stamp_approval_record(
                    {
                    "approval_id": "APPROVAL-ENFORCE-001",
                    "scope": scope,
                    "exact_paths": [target_path],
                    "command_or_provider": command,
                    "command_preview": command,
                    "budget": "0",
                    "expires_at": "2099-01-01T00:00:00+00:00",
                    "one_time_use": True,
                    "approver": "Darrin",
                    "revoked": False,
                    "request_hash": request_hash,
                    **darrin_decision_source("DARRIN-DECISION-ENFORCE-001"),
                    }
                ),
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )

        safe = approval_check("coordination_note", ["C:/CODEX PG/example.txt"], "compose", path=approvals_path)
        assert_true(not safe["required"] and safe["allowed"], "coordination action does not need approval")

        denied = approval_check("write_file", ["C:/panda-gallery/app.py"], "write", path=approvals_path)
        assert_true(denied["required"] and not denied["allowed"], "Panda Gallery write requires approval")

        chained = approval_check("approval_record_create", [str(approvals_path)], "create approval", path=approvals_path)
        assert_true(chained["required"] and not chained["allowed"], "approval records cannot authorize approval creation")
        ledger_write = approval_check(
            "write_file",
            ["C:/CODEX PG/CODEX Agent Hub/CODEX approvals/CODEX_approval_records.local.jsonl"],
            "write approval ledger",
            path=approvals_path,
        )
        assert_true(ledger_write["required"] and not ledger_write["allowed"], "approval ledger writes cannot be chained")

        allowed = enforce_protected_action("git_commit", [target_path], command, "0", path=approvals_path)
        assert_true(allowed["allowed"], "matching approval allows protected action")
        assert_true(allowed["approval_id"] == "APPROVAL-ENFORCE-001", "approval id is returned")

        wrong_command = approval_check("git_commit", [target_path], "git commit -m changed", "0", path=approvals_path)
        assert_true(not wrong_command["allowed"], "changed command invalidates approval")

        mark_approval_consumed("APPROVAL-ENFORCE-001", consumed_at="2099-01-01T00:00:00+00:00", path=approvals_path)
        consumed = approval_check("git_commit", [target_path], command, "0", path=approvals_path)
        assert_true(not consumed["allowed"], "consumed one-time approval cannot be reused")


def test_approval_hash_semantics() -> None:
    target_path = "C:/CODEX PG/example.txt"
    command = "git commit -m hash-semantics"
    scope = "git_commit_requires_darrin"
    request_hash = canonical_request_hash(scope, [target_path], command, "0")
    record = stamp_approval_record(
        {
            "approval_id": "APPROVAL-HASH-001",
            "scope": scope,
            "exact_paths": [target_path],
            "command_or_provider": command,
            "command_preview": command,
            "budget": "0",
            "expires_at": "2099-01-01T00:00:00+00:00",
            "one_time_use": True,
            "approver": "Darrin",
            "revoked": False,
            "request_hash": request_hash,
            **darrin_decision_source("DARRIN-DECISION-HASH-001"),
        }
    )
    errors = validate_approval_record(record)
    assert_true(not errors, "hash-bound approval record validates")
    assert_true(record["command_hash"] == command_hash(command), "command_hash binds command_preview")
    assert_true(record["record_hash"] == approval_record_hash(record), "record_hash binds immutable fields")

    changed_command = dict(record, command_preview="git commit -m changed")
    changed_command_errors = validate_approval_record(changed_command)
    assert_true(
        any("command_hash does not match" in error for error in changed_command_errors),
        "changed command_preview invalidates command_hash",
    )

    changed_expiry = dict(record, expires_at="2099-02-01T00:00:00+00:00")
    changed_expiry_errors = validate_approval_record(changed_expiry)
    assert_true(
        any("record_hash does not match" in error for error in changed_expiry_errors),
        "editing immutable approval fields invalidates record_hash",
    )

    changed_approver = dict(record, approved_by="Codex")
    changed_approver_errors = validate_approval_record(changed_approver)
    assert_true(
        any("approved_by must match approver" in error for error in changed_approver_errors),
        "approved_by must match approver",
    )

    mutable_update = dict(
        record,
        consumed_at="2099-01-01T00:00:00+00:00",
        revoked_at="2099-01-01T00:01:00+00:00",
        revoke_reason="smoke test",
    )
    mutable_errors = validate_approval_record(mutable_update)
    assert_true(
        not any("record_hash does not match" in error for error in mutable_errors),
        "allowed mutable fields do not invalidate record_hash",
    )


def test_strict_mcp_config_enforcement() -> None:
    with TemporaryDirectory() as temp_dir:
        approvals_path = Path(temp_dir) / "approvals.jsonl"
        headless_record = headless_approval_record()
        command = str(headless_record["command_or_provider"])
        errors = validate_approval_record(headless_record)
        assert_true(not errors, "headless approval accepts canonical strict MCP config")

        wrong_path = dict(headless_record, mcp_config_path="C:/tmp/unsafe_mcp.json")
        wrong_path_errors = validate_approval_record(wrong_path)
        assert_true(any("canonical PAH read-only MCP config" in error for error in wrong_path_errors), "MCP path is pinned")

        wrong_hash = dict(headless_record, mcp_config_expected_hash="sha256:bad")
        wrong_hash_errors = validate_approval_record(wrong_hash)
        assert_true(any("mcp_config_expected_hash" in error for error in wrong_hash_errors), "MCP config hash is pinned")

        loose_flag = dict(headless_record, strict_mcp_config=False)
        loose_flag_errors = validate_approval_record(loose_flag)
        assert_true(any("strict_mcp_config" in error for error in loose_flag_errors), "strict MCP flag is mandatory")

        approvals_path.write_text(json.dumps(headless_record, sort_keys=True) + "\n", encoding="utf-8")
        allowed = approval_check("headless_agent_run", [], command, "0", path=approvals_path)
        assert_true(allowed["allowed"], "matching headless approval passes strict MCP checks")


def test_headless_command_contract() -> None:
    record = headless_approval_record("DARRIN-DECISION-HEADLESS-CONTRACT-001")
    args = canonical_headless_command_args(record)
    assert_true(args[:6] == ["claude", "-p", str(record["prompt_file"]), "--output-format", "json", "--permission-mode"], "headless command starts with canonical Claude JSON plan mode")
    assert_true("--strict-mcp-config" in args, "headless command includes strict MCP flag")
    assert_true("--no-session-persistence" in args, "headless command disables session persistence")
    assert_true(args[args.index("--mcp-config") + 1] == str(MCP_READONLY_CONFIG_PATH), "headless command pins MCP config path")
    assert_true(args[args.index("--max-budget-usd") + 1] == "0", "headless command carries approved budget")

    capture = headless_capture_contract(record)
    assert_true(capture["stdout_path"] == record["audit_stdout_path"], "stdout capture path is explicit")
    assert_true(capture["stderr_path"] == record["audit_stderr_path"], "stderr capture path is explicit")
    assert_true(capture["exit_code_path"] == record["audit_exit_code_path"], "exit code capture path is explicit")
    assert_true(capture["process_timeout_seconds"] == HEADLESS_DEFAULT_TIMEOUT_SECONDS, "headless timeout defaults to 600 seconds")
    assert_true(capture["sigkill_grace_seconds"] == HEADLESS_SIGKILL_GRACE_SECONDS, "headless kill grace defaults to 30 seconds")
    assert_true(capture["consume_approval_on_exit"], "headless exit consumes approval")

    assert_true(not validate_headless_command_contract(record), "canonical headless command contract validates")

    wrong_preview = dict(record, command_preview="claude unsafe")
    assert_true(
        any("command_preview" in error for error in validate_headless_command_contract(wrong_preview)),
        "changed command preview is rejected",
    )

    unsafe_tools = dict(record, allowed_tools=["Read", "Bash"])
    assert_true(
        any("non-read-only" in error for error in validate_headless_command_contract(unsafe_tools)),
        "write-capable headless tools are rejected",
    )

    missing_capture = dict(record)
    del missing_capture["audit_stdout_path"]
    assert_true(
        any("audit_stdout_path" in error for error in validate_headless_command_contract(missing_capture)),
        "missing stdout capture path is rejected",
    )


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


def test_read_state_marks_changed_content_unread() -> None:
    with TemporaryDirectory() as temp_dir:
        state_path = Path(temp_dir) / "read_state.json"
        message_path = Path(temp_dir) / "message.md"
        text = render_message_markdown(
            {
                "schema_version": MESSAGE_SCHEMA_VERSION,
                "id": "PAH-READ-STATE-001",
                "thread_id": "PAH-THREAD-001",
                "created_at": "2026-04-27T02:00:00-07:00",
                "from": "claude-code",
                "to": "codex",
                "type": "report",
                "priority": "normal",
                "status": "complete",
                "approval_boundary": "coordination_only",
                "requires_darrin_decision": False,
            },
            "Read state smoke",
            "Smoke test",
            "Initial body.",
        )
        message_path.write_text(text, encoding="utf-8")

        initial = message_read_status(message_path, "PAH-READ-STATE-001", text)
        assert_true(initial["unread"], "messages default to unread")

        record = set_message_read_state(
            message_path,
            "PAH-READ-STATE-001",
            text,
            "read",
            actor="smoke",
            state_path=state_path,
        )
        assert_true(record["state"] == "read", "read state is persisted")

        data = {"items": {str(message_path): record}}
        read_status = message_read_status(message_path, "PAH-READ-STATE-001", text, data)
        assert_true(not read_status["unread"], "same content remains read")

        changed_status = message_read_status(message_path, "PAH-READ-STATE-001", text + "\nchanged\n", data)
        assert_true(changed_status["unread"], "changed content becomes unread")
        assert_true(changed_status["content_changed"], "changed content is flagged")

        summary = read_state_summary(data)
        assert_true(summary["counts"]["read"] == 1, "read state summary counts read records")


def test_thread_archive_state_reopens_on_new_activity() -> None:
    with TemporaryDirectory() as temp_dir:
        state_path = Path(temp_dir) / "thread_archive.json"
        record = archive_thread(
            "PAH-THREAD-ARCHIVE-001",
            latest_path="C:/CODEX PG/message.md",
            latest_title="Archive smoke",
            latest_modified=100.0,
            reason="smoke test",
            actor="smoke",
            state_path=state_path,
        )
        assert_true(record["state"] == "archived", "thread archive stores archived state")

        state_data = {
            "threads": {
                "PAH-THREAD-ARCHIVE-001": record,
            }
        }
        archived = thread_archive_status("PAH-THREAD-ARCHIVE-001", 100.0, state_data)
        assert_true(archived["archived"], "thread is archived at same latest modified time")

        reopened = thread_archive_status("PAH-THREAD-ARCHIVE-001", 101.0, state_data)
        assert_true(not reopened["archived"], "newer thread activity surfaces archived thread")
        assert_true(reopened["reopened_by_new_activity"], "newer thread activity is flagged")

        active = unarchive_thread(
            "PAH-THREAD-ARCHIVE-001",
            actor="smoke",
            reason="reopen",
            state_path=state_path,
        )
        assert_true(active["state"] == "active", "thread unarchive stores active state")
        summary = thread_archive_summary({"threads": {"PAH-THREAD-ARCHIVE-001": active}})
        assert_true(summary["counts"]["active"] == 1, "thread archive summary counts active records")


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
    test_source_folder_spoofing_detection()
    test_standalone_validator_cli()
    test_decision_gate()
    test_cross_check_auto_resolution_rule()
    test_routes_and_scope()
    test_diagnostics()
    test_notification_provider_status()
    test_safety_surfaces()
    test_quarantine_move_writes_tombstone()
    test_approval_enforcement()
    test_approval_hash_semantics()
    test_strict_mcp_config_enforcement()
    test_headless_command_contract()
    test_backpressure_detection()
    test_processed_message_sidecar_idempotency()
    test_read_state_marks_changed_content_unread()
    test_thread_archive_state_reopens_on_new_activity()
    test_decision_state()
    test_validation_state()
    test_route_test_state()
    test_work_board_state()
    print("PAH smoke tests passed")


if __name__ == "__main__":
    main()
