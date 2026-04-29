"""Smoke tests for PANDA Agent Hub core contracts.

These tests are intentionally dependency-free and avoid live agent, SMS, API,
or Panda Gallery writes.
"""

from __future__ import annotations

from pathlib import Path
import json
import os
import socket
import subprocess
import sys
import time
from tempfile import TemporaryDirectory

import CODEX_agent_hub as agent_hub
import CODEX_pah_inspector as inspector
import CODEX_pah_periodic_health_check as periodic_health
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


def test_create_message_dry_run_does_not_write_mail() -> None:
    with TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        inbox = root / "CLAUDE Inbox"
        ledger = root / "CODEX_MAILBOX_LEDGER.md"
        interaction_ledger = root / "CODEX logs" / "CODEX_pah_interaction_ledger.jsonl"
        original_values = {
            "CLAUDE_INBOX": agent_hub.CLAUDE_INBOX,
            "LEDGER_PATH": agent_hub.LEDGER_PATH,
            "INTERACTION_LEDGER_PATH": agent_hub.INTERACTION_LEDGER_PATH,
        }
        try:
            agent_hub.CLAUDE_INBOX = inbox
            agent_hub.LEDGER_PATH = ledger
            agent_hub.INTERACTION_LEDGER_PATH = interaction_ledger
            result = agent_hub.create_message(
                {
                    "route": "codex_to_claude",
                    "subject": "Dry run route probe",
                    "body": "This should not be written.",
                    "dry_run": True,
                }
            )
            assert_true(result["dry_run"] is True, "create_message reports dry-run mode")
            assert_true(not Path(str(result["path"])).exists(), "create_message dry-run does not write mailbox file")
            assert_true(not inbox.exists(), "create_message dry-run does not create inbox directory")
            assert_true(not ledger.exists(), "create_message dry-run does not write mailbox ledger")
            assert_true(not interaction_ledger.exists(), "create_message dry-run does not write interaction ledger")
        finally:
            for key, value in original_values.items():
                setattr(agent_hub, key, value)


def test_create_message_writes_reply_tombstone_for_active_message() -> None:
    with TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        codex_inbox = root / "CODEX Inbox"
        claude_inbox = root / "CLAUDE Inbox"
        codex_inbox.mkdir()
        claude_inbox.mkdir()
        original_path = codex_inbox / "original.md"
        ledger = root / "CODEX_MAILBOX_LEDGER.md"
        interaction_ledger = root / "CODEX logs" / "CODEX_pah_interaction_ledger.jsonl"
        original_text = render_message_markdown(
            {
                "schema_version": MESSAGE_SCHEMA_VERSION,
                "message_id": "PAH-ORIGINAL-001",
                "thread_id": "PAH-REPLY-TOMBSTONE",
                "created_at": "2026-04-29T10:00:00-07:00",
                "from": "claude-desktop",
                "to": "codex",
                "type": "directive",
                "status": "open",
                "thread_status": "active",
                "action_owner": "codex",
                "priority": "normal",
                "requires_darrin_decision": False,
                "approval_boundary": "coordination_only",
            },
            "Original active request",
            "Needs reply",
            "Please reply to this message.",
        )
        original_path.write_text(original_text, encoding="utf-8")
        original_values = {
            "MESSAGE_DIRS": agent_hub.MESSAGE_DIRS,
            "CODEX_INBOX": agent_hub.CODEX_INBOX,
            "CLAUDE_INBOX": agent_hub.CLAUDE_INBOX,
            "LEDGER_PATH": agent_hub.LEDGER_PATH,
            "INTERACTION_LEDGER_PATH": agent_hub.INTERACTION_LEDGER_PATH,
        }
        try:
            agent_hub.clear_message_parse_cache()
            agent_hub.MESSAGE_DIRS = (("Claude -> Codex", codex_inbox), ("Codex -> Claude", claude_inbox))
            agent_hub.CODEX_INBOX = codex_inbox
            agent_hub.CLAUDE_INBOX = claude_inbox
            agent_hub.LEDGER_PATH = ledger
            agent_hub.INTERACTION_LEDGER_PATH = interaction_ledger
            result = agent_hub.create_message(
                {
                    "route": "codex_to_claude",
                    "subject": "Reply tombstone probe",
                    "body": "Replying so the original should stop looking live.",
                    "thread_id": "PAH-REPLY-TOMBSTONE",
                    "reply_to": "PAH-ORIGINAL-001",
                }
            )
            assert_true(Path(str(result["path"])).exists(), "reply message is written")
            assert_true(len(result["reply_tombstones"]) == 1, "create_message reports one reply tombstone")
            tombstone_path = agent_hub.reply_tombstone_path(original_path)
            assert_true(tombstone_path.exists(), "reply tombstone is written beside the original message")
            tombstone = json.loads(tombstone_path.read_text(encoding="utf-8"))
            assert_true(tombstone["original_message_id"] == "PAH-ORIGINAL-001", "tombstone identifies original message")
            assert_true(tombstone["reply_message_id"] == result["message_id"], "tombstone identifies reply message")
            original_message = next(msg for msg in agent_hub.load_messages() if msg.message_id == "PAH-ORIGINAL-001")
            assert_true(agent_hub.classify_thread_state(original_message) == "closed", "replied original classifies closed")
            ledger_events = [
                json.loads(line)
                for line in interaction_ledger.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            assert_true(
                any(event.get("event_type") == "message_reply_tombstoned" for event in ledger_events),
                "interaction ledger records reply tombstone creation",
            )
        finally:
            for key, value in original_values.items():
                setattr(agent_hub, key, value)
            agent_hub.clear_message_parse_cache()


def test_cockpit_payload_contract() -> None:
    payload = agent_hub.cockpit_payload()
    assert_true(payload["schema_version"] == 1, "cockpit schema version")
    assert_true(payload["cockpit_state"]["read_only"], "cockpit v1 is read-only")
    assert_true("routes_summary" in payload["cockpit_state"], "cockpit has route summary")
    assert_true("stale_unread" in payload["cockpit_state"]["counts"], "cockpit counts stale unread")
    assert_true(len(payload["agents"]) == 4, "cockpit exposes four agents")
    assert_true("action_queue" in payload, "cockpit exposes action queue")
    assert_true("wake_candidates" in payload, "cockpit exposes wake candidates")
    assert_true(payload["routes"], "cockpit exposes route health")
    held_routes = [route for route in payload["routes"] if route.get("status") == "held"]
    if held_routes:
        assert_true(held_routes[0].get("latency_ms") is None, "held route latency is null")
    if payload["feed"]:
        assert_true("age_seconds" in payload["feed"][0], "feed includes age seconds")
        assert_true("stale_unread" in payload["feed"][0], "feed includes stale unread flag")
        assert_true("wake_candidate_label" not in payload["feed"][0], "feed derives wake labels from agent IDs")
    decision_items = [item for item in payload["action_queue"] if item.get("kind") == "decision"]
    if decision_items:
        assert_true("scope_text" in decision_items[0], "decision queue carries scope text")
        assert_true("actions" in decision_items[0], "decision queue carries action metadata")
    if payload["selected_thread"].get("cards"):
        assert_true("kind" in payload["selected_thread"]["cards"][0], "selected thread cards are typed")
    actions = {item["id"]: item for item in payload["read_only_actions"]}
    assert_true(not actions["compose"]["enabled"], "compose disabled in read-only cockpit")
    assert_true(not actions["send"]["enabled"], "send disabled in read-only cockpit")
    assert_true(actions["compose"]["destructive"] is False, "read-only actions carry destructive flag")
    assert_true("last_commit_message" in payload["git"], "git payload carries commit message field")
    assert_true("relay_health" in payload["diagnostics"], "cockpit diagnostics carries relay health summary")
    assert_true("status_label" in payload["diagnostics"]["relay_health"], "relay health summary carries status label")
    assert_true("cache" in payload["diagnostics"]["relay_health"], "relay health summary carries cache metadata")
    assert_true("health" in payload, "cockpit carries canonical health summary")
    assert_true("components" in payload["health"], "health summary carries components")
    assert_true("server" in payload["health"]["components"], "health summary carries server component")
    assert_true("routes" in payload["health"]["components"], "health summary carries routes component")
    assert_true("diagnostics" in payload["health"]["components"], "health summary carries diagnostics component")
    if (agent_hub.PROJECT_ROOT / ".git").exists():
        assert_true(payload["git"]["last_commit"], "git payload carries last commit hash when repo metadata is available")
        assert_true(payload["git"]["last_commit_message"], "git payload carries last commit message when repo metadata is available")
        assert_true(payload["git"]["last_commit_iso"], "git payload carries last commit timestamp when repo metadata is available")
    ui_text = Path(__file__).with_name("CODEX_agent_hub_ui.html").read_text(encoding="utf-8")
    assert_true("unread over 60s" not in ui_text, "UI derives stale threshold labels from cockpit_state")


def test_health_payload_contract() -> None:
    payload = agent_hub.health_payload()
    assert_true(payload["schema_version"] == 1, "health schema version")
    assert_true(payload["overall"] in {"ok", "warn", "err", "unknown"}, "health overall level is normalized")
    assert_true(isinstance(payload["ok"], bool), "health ok is boolean")
    components = payload["components"]
    for name in ("server", "routes", "mailboxes", "unanswered", "agent_progress", "archive", "diagnostics", "periodic_monitor", "github_backup"):
        assert_true(name in components, f"health carries {name} component")
        assert_true(components[name]["level"] in {"ok", "warn", "err", "unknown"}, f"{name} health level is normalized")
        assert_true(bool(components[name]["label"]), f"{name} health has label")
        assert_true(bool(components[name]["detail"]), f"{name} health has detail")


def test_agent_progress_monitor_contract() -> None:
    with TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        pg_root = root / "panda-gallery"
        target = pg_root / "panda_ledger" / "shared"
        state_dir = pg_root / "workflows" / "cc_mailbox" / "_state"
        target.mkdir(parents=True)
        state_dir.mkdir(parents=True)
        sidecar = state_dir / "active_dispatch.json"
        file_path = target / "ipc.py"
        file_path.write_text("print('ok')\n", encoding="utf-8")
        stale_time = time.time() - (50 * 60)
        os.utime(file_path, (stale_time, stale_time))
        now_iso = agent_hub.datetime.now().astimezone().isoformat(timespec="seconds")
        old_iso = agent_hub.datetime.fromtimestamp(time.time() - (50 * 60)).astimezone().isoformat(timespec="seconds")
        original_values = {
            "CC_ACTIVE_DISPATCH_PATH": agent_hub.CC_ACTIVE_DISPATCH_PATH,
            "PANDA_GALLERY_ROOT": agent_hub.PANDA_GALLERY_ROOT,
        }
        try:
            agent_hub.CC_ACTIVE_DISPATCH_PATH = sidecar
            agent_hub.PANDA_GALLERY_ROOT = pg_root
            sidecar.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "agent": "claude-code",
                        "dispatch_id": "PG-LEDGER-PHASE2",
                        "thread_id": "PG-LEDGER-PHASE2",
                        "phase": "Layer 1 shared/",
                        "status": "active",
                        "started_at": old_iso,
                        "updated_at": now_iso,
                        "expected_target_paths": [str(target)],
                        "stale_warn_minutes": 30,
                        "stale_error_minutes": 45,
                    }
                ),
                encoding="utf-8",
            )
            stale = agent_hub.cc_active_dispatch_progress()
            assert_true(stale["severity"] == "err", "stale active dispatch becomes red")
            assert_true("Interrupt CC" in stale["recommended_action"], "stale active dispatch recommends interrupt")

            fresh_time = time.time()
            os.utime(file_path, (fresh_time, fresh_time))
            fresh = agent_hub.cc_active_dispatch_progress()
            assert_true(fresh["severity"] == "ok", "recent target mtime becomes green")
            assert_true(fresh["recommended_action"], "fresh progress card still has a recommended action")

            sidecar.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "agent": "claude-code",
                        "dispatch_id": "PG-LEDGER-PHASE2",
                        "phase": "Composing module",
                        "status": "compose",
                        "started_at": old_iso,
                        "updated_at": old_iso,
                        "expected_target_paths": [str(target)],
                    }
                ),
                encoding="utf-8",
            )
            compose = agent_hub.cc_active_dispatch_progress()
            assert_true(compose["severity"] == "err", "overlong compose state becomes red")
            assert_true("compose state exceeded" in compose["recommended_action"], "compose state explains action")
        finally:
            for key, value in original_values.items():
                setattr(agent_hub, key, value)


def test_codex_mailbox_sla_progress() -> None:
    with TemporaryDirectory() as temp_dir:
        inbox = Path(temp_dir) / "CODEX Inbox"
        inbox.mkdir()
        path = inbox / "urgent.md"
        path.write_text("urgent body", encoding="utf-8")
        original_values = {
            "AGENT_INBOX_DIRS": agent_hub.AGENT_INBOX_DIRS,
            "ALL_AGENT_INBOX_DIRS": agent_hub.ALL_AGENT_INBOX_DIRS,
        }
        try:
            agent_hub.AGENT_INBOX_DIRS = {**agent_hub.AGENT_INBOX_DIRS, "codex": (inbox,)}
            agent_hub.ALL_AGENT_INBOX_DIRS = (inbox,)
            msg = agent_hub.Message(
                direction="smoke",
                path=path,
                name=path.name,
                modified=time.time() - 180,
                title="Urgent pickup test",
                summary="urgent",
                body="urgent body",
                message_id="PAH-SLA-URGENT",
                thread_id="PAH-SLA-URGENT",
                from_agent="claude-desktop",
                to_agent="codex",
                message_type="urgent_request",
                priority="urgent",
                status="open",
                thread_status="active",
                schema_version="1",
            )
            progress = agent_hub.codex_mailbox_sla_progress([msg], {})
            assert_true(progress["severity"] == "err", "urgent unread beyond SLA becomes red")
            assert_true(progress["urgent_breached"] == 1, "urgent SLA breach is counted")
            assert_true(progress["recommended_action"] == "Read urgent Codex mail now.", "urgent SLA recommends immediate read")
        finally:
            for key, value in original_values.items():
                setattr(agent_hub, key, value)


def test_health_payload_unanswered_component() -> None:
    cockpit = {
        "generated_at": "2026-04-29T09:30:00",
        "cockpit_state": {
            "counts": {
                "open_on_darrin": 2,
                "open_on_agent": 3,
                "owner_unknown": 0,
                "stale_unread": 1,
            },
            "routes_summary": {"severity": "ok", "label": "4/4 routes pass"},
        },
        "diagnostics": {"checks_fail": 0, "checks_warn": 0, "actionable_validation_issues": 0},
        "git": {"clean": True, "branch": "main", "tracking": "origin/main"},
    }
    health = agent_hub.health_payload_from_cockpit(cockpit)
    unanswered = health["components"]["unanswered"]
    assert_true(unanswered["level"] == "warn", "open answered work is a warning")
    assert_true(unanswered["total"] == 5, "unanswered total sums Darrin, agent, and unknown owners")

    cockpit["cockpit_state"]["counts"]["owner_unknown"] = 1
    health = agent_hub.health_payload_from_cockpit(cockpit)
    assert_true(health["components"]["unanswered"]["level"] == "err", "owner-unknown unanswered work is an error")


def test_periodic_archive_sweep_contract() -> None:
    original = periodic_health.agent_hub.archive_read_codex_inbox_messages

    def fake_archive_read(actor: str = "codex", dry_run: bool = False) -> dict[str, object]:
        assert_true(actor == "periodic_health_monitor", "periodic archive sweep uses steward actor")
        assert_true(dry_run is False, "periodic archive sweep performs real read-mail archiving")
        return {
            "protocol_version": 2,
            "count": 2,
            "skipped_waiting_on_darrin": 1,
            "skipped_pending_dispatch": 1,
            "skipped_unstructured": 1,
            "archive_conflicts": 1,
            "inbox_summary": [{"name": "CLAUDE Inbox", "moved": 2}],
        }

    try:
        periodic_health.agent_hub.archive_read_codex_inbox_messages = fake_archive_read
        result = periodic_health.archive_read_sweep()
        assert_true(result["ok"], "periodic archive sweep wrapper reports ok")
        assert_true(result["protocol_version"] == 2, "periodic archive sweep preserves protocol version")
        assert_true(result["moved"] == 2, "periodic archive sweep reports moved read mail")
        assert_true(result["archive_conflicts"] == 1, "periodic archive sweep reports archive conflicts")
        assert_true(result["inbox_summary"][0]["moved"] == 2, "periodic archive sweep reports per-inbox moved count")
    finally:
        periodic_health.agent_hub.archive_read_codex_inbox_messages = original


def test_periodic_steward_schedule_metadata() -> None:
    started_at = "2026-04-29T10:00:00-07:00"
    original = periodic_health.os.environ.get("PAH_PERIODIC_HEALTH_INTERVAL_MINUTES")
    try:
        periodic_health.os.environ["PAH_PERIODIC_HEALTH_INTERVAL_MINUTES"] = "15"
        schedule = periodic_health.steward_schedule(started_at)
        assert_true(schedule["interval_minutes"] == 15, "steward schedule honors interval override")
        assert_true(schedule["last_run_started_at"] == started_at, "steward schedule records last run start")
        assert_true(schedule["next_run_after"] == "2026-04-29T10:15:00-07:00", "steward schedule records next run")
        periodic_health.os.environ["PAH_PERIODIC_HEALTH_INTERVAL_MINUTES"] = "invalid"
        fallback = periodic_health.steward_schedule(started_at)
        assert_true(
            fallback["interval_minutes"] == periodic_health.DEFAULT_RUN_INTERVAL_MINUTES,
            "steward schedule falls back to default interval",
        )
    finally:
        if original is None:
            periodic_health.os.environ.pop("PAH_PERIODIC_HEALTH_INTERVAL_MINUTES", None)
        else:
            periodic_health.os.environ["PAH_PERIODIC_HEALTH_INTERVAL_MINUTES"] = original


def test_pah_inspector_detects_retired_ui_routes() -> None:
    with TemporaryDirectory() as temp_dir:
        ui_path = Path(temp_dir) / "ui.html"
        ui_path.write_text(
            """<!doctype html><div id=\"stewardPanel\"></div><div id=\"trustStrip\"></div><div id=\"summaryStrip\"></div><button id=\"archiveRead\"></button><button id=\"cleanupInboxes\"></button><button id=\"refresh\"></button><button id=\"openInspector\"></button><section id=\"inspectorPanel\"><div id=\"inspectorSummary\"></div><div id=\"inspectorFindings\"></div><pre id=\"inspectorMarkdown\"></pre></section><div id=\"agentList\"></div><div id=\"actionList\"></div><div id=\"inboxStrip\"></div><div id=\"detailTitle\"></div><div id=\"detailSummary\"></div><div id=\"messagePreview\"></div><div id=\"queueCount\"></div><input id=\"queueSearch\"><button id=\"deleteVisible\"></button><button id=\"openMessage\"></button><button id=\"openFolder\"></button><button id=\"copyPath\"></button><button id=\"snoozeAlert\"></button><script>postJson('/api/archive-read-codex-inbox', {}); fetch('/api/send');</script>""",
            encoding="utf-8",
        )
        original = inspector.agent_hub.UI_PATH
        try:
            inspector.agent_hub.UI_PATH = ui_path
            findings = inspector.inspect_ui_wiring()
            by_id = {finding.check_id: finding for finding in findings}
            assert_true(by_id["ui.required_controls"].status == "pass", "inspector sees required controls")
            assert_true(by_id["ui.no_retired_routes"].status == "fail", "inspector flags retired UI endpoint")
        finally:
            inspector.agent_hub.UI_PATH = original


def test_pah_inspector_summary_and_markdown_report() -> None:
    findings = [
        inspector.passed("a", "A", "ok"),
        inspector.warn("b", "B", "warn"),
        inspector.fail("c", "C", "fail"),
    ]
    summary = inspector.summarize(findings)
    assert_true(summary["overall"] == "fail", "inspector summary fails when any finding fails")
    report = {
        "generated_at": "2026-04-29T10:00:00-07:00",
        "url": "http://127.0.0.1:8765",
        "summary": summary,
        "findings": [finding.as_dict() for finding in findings],
    }
    text = inspector.markdown_report(report)
    assert_true("# PAH Inspector Report" in text, "inspector markdown has title")
    assert_true("[FAIL] C" in text, "inspector markdown includes failing finding")


def test_interaction_ledger_helper_writes_jsonl() -> None:
    with TemporaryDirectory() as temp_dir:
        ledger_path = Path(temp_dir) / "CODEX_pah_interaction_ledger.jsonl"
        original = agent_hub.INTERACTION_LEDGER_PATH
        try:
            agent_hub.INTERACTION_LEDGER_PATH = ledger_path
            event = agent_hub.append_interaction_ledger_event(
                "smoke_event",
                actor="smoke",
                path=Path(temp_dir) / "message.md",
                nested={"path": Path(temp_dir) / "nested.md"},
            )
            assert_true(event["schema_version"] == 1, "interaction ledger event includes schema version")
            payload = json.loads(ledger_path.read_text(encoding="utf-8").strip())
            assert_true(payload["event_type"] == "smoke_event", "interaction ledger writes event type")
            assert_true(payload["actor"] == "smoke", "interaction ledger writes actor")
            assert_true(isinstance(payload["path"], str), "interaction ledger serializes paths")
            assert_true(isinstance(payload["nested"]["path"], str), "interaction ledger serializes nested paths")
        finally:
            agent_hub.INTERACTION_LEDGER_PATH = original


def test_interaction_ledger_recent_events_and_summary() -> None:
    with TemporaryDirectory() as temp_dir:
        ledger_path = Path(temp_dir) / "CODEX_pah_interaction_ledger.jsonl"
        original = agent_hub.INTERACTION_LEDGER_PATH
        try:
            agent_hub.INTERACTION_LEDGER_PATH = ledger_path
            agent_hub.append_interaction_ledger_event("message_sent", actor="smoke")
            discrepancy = agent_hub.append_interaction_ledger_event(
                "agent_no_mail_claim_discrepancy",
                actor="smoke",
                agent="claude-desktop",
                actionable_unread_count=2,
                physical_unread_count=3,
            )
            agent_hub.append_interaction_ledger_event(
                "agent_no_mail_claim_validated",
                actor="smoke",
                agent="claude-code",
            )

            recent = agent_hub.recent_interaction_ledger_events(limit=2)
            assert_true(len(recent) == 2, "recent interaction ledger honors limit")
            assert_true(recent[0]["event_type"] == "agent_no_mail_claim_validated", "recent interaction ledger is newest first")

            filtered = agent_hub.recent_interaction_ledger_events(
                limit=10,
                event_types={"agent_no_mail_claim_discrepancy"},
            )
            assert_true(len(filtered) == 1, "recent interaction ledger filters event types")
            assert_true(filtered[0]["agent"] == "claude-desktop", "filtered interaction ledger preserves payload fields")

            summary = agent_hub.interaction_ledger_summary()
            assert_true(summary["exists"], "interaction ledger summary reports existing ledger")
            assert_true(summary["discrepancy_count"] == 1, "interaction ledger summary counts discrepancy events")
            assert_true(summary["latest_discrepancy"]["time"] == discrepancy["time"], "interaction ledger summary exposes latest discrepancy")
            assert_true(
                all(event["event_type"] != "message_sent" for event in summary["events"]),
                "interaction ledger summary only includes trust events",
            )
        finally:
            agent_hub.INTERACTION_LEDGER_PATH = original


def test_message_audit_records_discovery_and_classifier_transition() -> None:
    with TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        inbox = root / "CC Inbox"
        inbox.mkdir()
        ledger_path = root / "CODEX logs" / "CODEX_pah_interaction_ledger.jsonl"
        audit_state_path = root / "CODEX state" / "message_audit.json"
        original_values = {
            "INTERACTION_LEDGER_PATH": agent_hub.INTERACTION_LEDGER_PATH,
            "MESSAGE_AUDIT_STATE_PATH": agent_hub.MESSAGE_AUDIT_STATE_PATH,
        }
        try:
            agent_hub.INTERACTION_LEDGER_PATH = ledger_path
            agent_hub.MESSAGE_AUDIT_STATE_PATH = audit_state_path

            first_path = inbox / "open.md"
            first_path.write_text(
                render_message_markdown(
                    {
                        "schema_version": MESSAGE_SCHEMA_VERSION,
                        "id": "PAH-AUDIT-OPEN",
                        "thread_id": "PAH-AUDIT-THREAD",
                        "created_at": "2026-04-29T10:00:00-07:00",
                        "from": "claude-desktop",
                        "to": "claude-code",
                        "type": "dispatch",
                        "priority": "normal",
                        "status": "open",
                        "thread_status": "active",
                        "action_owner": "claude-code",
                        "requires_darrin_decision": False,
                        "approval_boundary": "coordination_only",
                    },
                    "Audit open",
                    "Initial open thread.",
                    "No action.",
                ),
                encoding="utf-8",
            )
            first = agent_hub.parse_message(first_path, "To Claude Code")
            focus = agent_hub.build_thread_focus([first])
            audit = agent_hub.audit_messages_and_thread_states([first], focus, {"messages": {}})
            assert_true(audit["discovered"] == 1, "message audit records first-seen message")
            assert_true(audit["transitions"] == 0, "first classifier observation establishes baseline")

            time.sleep(0.01)
            closed_path = inbox / "closed.md"
            closed_path.write_text(
                render_message_markdown(
                    {
                        "schema_version": MESSAGE_SCHEMA_VERSION,
                        "id": "PAH-AUDIT-CLOSED",
                        "thread_id": "PAH-AUDIT-THREAD",
                        "created_at": "2026-04-29T10:05:00-07:00",
                        "from": "claude-code",
                        "to": "claude-desktop",
                        "type": "report",
                        "priority": "normal",
                        "status": "completed",
                        "thread_status": "closed",
                        "action_owner": "none",
                        "requires_darrin_decision": False,
                        "approval_boundary": "ack_only",
                    },
                    "Audit closed",
                    "Closed thread.",
                    "Done.",
                ),
                encoding="utf-8",
            )
            closed = agent_hub.parse_message(closed_path, "Claude Code -> Claude")
            focus = agent_hub.build_thread_focus([first, closed])
            audit = agent_hub.audit_messages_and_thread_states([first, closed], focus, {"messages": {}})
            assert_true(audit["discovered"] == 1, "message audit records newly discovered follow-up")
            assert_true(audit["transitions"] == 1, "message audit records classifier state transition")

            events = [
                json.loads(line)
                for line in ledger_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            event_types = [event["event_type"] for event in events]
            assert_true(event_types.count("message_discovered") == 2, "ledger records both message discoveries")
            transition = next(event for event in events if event["event_type"] == "classifier_state_changed")
            assert_true(transition["previous_state"] == "open_on_agent", "transition records previous classifier state")
            assert_true(transition["state"] == "closed", "transition records new classifier state")
        finally:
            agent_hub.INTERACTION_LEDGER_PATH = original_values["INTERACTION_LEDGER_PATH"]
            agent_hub.MESSAGE_AUDIT_STATE_PATH = original_values["MESSAGE_AUDIT_STATE_PATH"]


def test_agent_no_mail_claim_validation() -> None:
    with TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        claude_inbox = root / "CLAUDE Inbox"
        claude_inbox.mkdir()
        ledger_path = root / "CODEX logs" / "CODEX_pah_interaction_ledger.jsonl"
        state_path = root / "read_state.json"
        state_path.write_text(json.dumps({"messages": {}}), encoding="utf-8")

        original_values = {
            "MESSAGE_DIRS": agent_hub.MESSAGE_DIRS,
            "AGENT_INBOX_DIRS": agent_hub.AGENT_INBOX_DIRS,
            "ALL_AGENT_INBOX_DIRS": agent_hub.ALL_AGENT_INBOX_DIRS,
            "INTERACTION_LEDGER_PATH": agent_hub.INTERACTION_LEDGER_PATH,
            "load_read_state": agent_hub.load_read_state,
        }
        try:
            agent_hub.MESSAGE_DIRS = (("Claude Inbox", claude_inbox),)
            agent_hub.AGENT_INBOX_DIRS = {"claude-desktop": (claude_inbox,)}
            agent_hub.ALL_AGENT_INBOX_DIRS = (claude_inbox,)
            agent_hub.INTERACTION_LEDGER_PATH = ledger_path
            agent_hub.load_read_state = lambda: json.loads(state_path.read_text(encoding="utf-8"))

            clear = agent_hub.validate_agent_no_mail_claim("claude-desktop", actor="smoke")
            assert_true(clear["ok"], "no-mail claim passes when agent inbox has no unread messages")
            assert_true(clear["actionable_unread_count"] == 0, "clear no-mail claim has no actionable unread")
            assert_true(clear["physical_unread_count"] == 0, "clear no-mail claim has no physical unread")

            message_path = claude_inbox / "unread_for_claude.md"
            message_text = render_message_markdown(
                {
                    "schema_version": MESSAGE_SCHEMA_VERSION,
                    "id": "PAH-NO-MAIL-CLAIM-UNREAD",
                    "thread_id": "PAH-NO-MAIL-CLAIM-UNREAD",
                    "created_at": "2026-04-29T10:00:00-07:00",
                    "from": "codex",
                    "to": "claude-desktop",
                    "type": "coordination",
                    "status": "open",
                    "thread_status": "active",
                    "priority": "normal",
                    "approval_boundary": "coordination_only",
                    "requires_darrin_decision": False,
                },
                "Unread for Claude",
                "Claim mismatch smoke.",
                "Claude Desktop should not be able to claim no mail while this is unread.",
            )
            message_path.write_text(message_text, encoding="utf-8")
            mismatch = agent_hub.validate_agent_no_mail_claim("cd", actor="smoke")
            assert_true(not mismatch["ok"], "no-mail claim fails when actionable unread mail exists")
            assert_true(mismatch["actionable_unread_count"] == 1, "no-mail claim reports actionable unread count")
            assert_true(mismatch["physical_unread_count"] == 1, "no-mail claim reports physical unread count")

            set_message_read_state(message_path, "PAH-NO-MAIL-CLAIM-UNREAD", message_text, "read", actor="smoke", state_path=state_path)
            unstructured_path = claude_inbox / "owner_unknown.md"
            unstructured_path.write_text("# Legacy note\n\nThis lacks PAH frontmatter but still lives in the inbox.\n", encoding="utf-8")
            malformed = agent_hub.validate_agent_no_mail_claim("claude", actor="smoke")
            assert_true(not malformed["ok"], "no-mail claim fails when owner-unknown unread mail exists")
            assert_true(malformed["actionable_unread_count"] == 0, "owner-unknown no-mail mismatch is not counted as actionable")
            assert_true(malformed["physical_unread_count"] == 1, "owner-unknown no-mail mismatch is counted as physical unread")
            assert_true(malformed["owner_unknown_count"] == 1, "no-mail claim reports owner-unknown unread count")

            events = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines() if line.strip()]
            event_types = [event["event_type"] for event in events]
            assert_true("agent_no_mail_claim_validated" in event_types, "ledger records valid no-mail claim")
            assert_true("agent_no_mail_claim_discrepancy" in event_types, "ledger records discrepant no-mail claim")
        finally:
            for key, value in original_values.items():
                setattr(agent_hub, key, value)


def test_periodic_communication_backlog_detects_discrepancies() -> None:
    cockpit = {
        "cockpit_state": {
            "counts": {
                "open_on_agent": 1,
                "owner_unknown": 1,
                "open_on_darrin": 0,
            }
        },
        "thread_focus": {
            "open_on_agent": [{"title": "Check your mail", "thread_id": "PAH-E2E-TEST", "owner": "claude_desktop"}],
            "owner_unknown": [{"title": "Legacy unowned message", "thread_id": "legacy.md"}],
        },
    }
    backlog = periodic_health.communication_backlog(cockpit)
    assert_true(not backlog["ok"], "communication backlog fails when agents or unknown owners have work")
    assert_true(backlog["open_on_agent"] == 1, "communication backlog reports open-on-agent count")
    assert_true(backlog["owner_unknown"] == 1, "communication backlog reports owner-unknown count")
    assert_true(backlog["agent_threads"][0]["thread_id"] == "PAH-E2E-TEST", "communication backlog includes agent thread details")

    clear = {
        "cockpit_state": {"counts": {"open_on_agent": 0, "owner_unknown": 0, "open_on_darrin": 2}},
        "thread_focus": {},
    }
    assert_true(periodic_health.communication_backlog(clear)["ok"], "Darrin-only work does not fail agent communication backlog")


def test_periodic_communication_backlog_records_discrepancy_event() -> None:
    backlog = {
        "ok": False,
        "open_on_agent": 1,
        "owner_unknown": 2,
        "open_on_darrin": 0,
        "agent_threads": [{"title": "Needs agent", "thread_id": "THREAD-1", "owner": "claude-desktop"}],
        "owner_unknown_threads": [{"title": "Unknown owner", "thread_id": "THREAD-2"}],
    }
    captured: list[dict[str, object]] = []
    original = periodic_health.agent_hub.append_interaction_ledger_event

    def fake_append(event_type: str, actor: str = "pah", **details: object) -> dict[str, object]:
        payload = {"event_type": event_type, "actor": actor, **details}
        captured.append(payload)
        return payload

    try:
        periodic_health.agent_hub.append_interaction_ledger_event = fake_append
        event = periodic_health.record_communication_backlog_event(backlog)
        assert_true(event is not None, "periodic backlog records discrepancy event")
        assert_true(captured[0]["event_type"] == "mailbox_discrepancy_detected", "discrepancy event type is recorded")
        assert_true(captured[0]["actor"] == "periodic_health_monitor", "discrepancy event actor is steward")
        assert_true(captured[0]["open_on_agent"] == 1, "discrepancy event records agent backlog count")
        assert_true(captured[0]["owner_unknown"] == 2, "discrepancy event records owner-unknown count")
    finally:
        periodic_health.agent_hub.append_interaction_ledger_event = original


def test_cockpit_action_queue_ordering() -> None:
    agents = [
        {"id": "claude_code", "display_name": "Claude Code"},
        {"id": "claude_desktop", "display_name": "Claude Desktop"},
    ]
    feed = [
        {
            "id": "new-wake",
            "message_path": "C:/CODEX PG/new-wake.md",
            "time_iso": "2026-04-28T10:02:00",
            "stale_unread": True,
            "unread": True,
            "age_seconds": 62,
            "wake_candidate_agent": "claude_code",
            "title": "New wake",
            "sub": "new",
            "thread_id": "THREAD-NEW",
        },
        {
            "id": "old-wake",
            "message_path": "C:/CODEX PG/old-wake.md",
            "time_iso": "2026-04-28T10:01:00",
            "stale_unread": True,
            "unread": True,
            "age_seconds": 122,
            "wake_candidate_agent": "claude_desktop",
            "title": "Old wake",
            "sub": "old",
            "thread_id": "THREAD-OLD",
        },
        {
            "id": "plain-unread",
            "message_path": "C:/CODEX PG/plain-unread.md",
            "time_iso": "2026-04-28T10:03:00",
            "stale_unread": False,
            "unread": True,
            "age_seconds": 20,
            "wake_candidate_agent": "claude_code",
            "title": "Plain unread",
            "sub": "plain",
            "thread_id": "THREAD-PLAIN",
        },
    ]
    queue = agent_hub.cockpit_action_queue(feed, [], agents)
    assert_true([item["id"] for item in queue] == ["new-wake", "old-wake", "plain-unread"], "action queue preserves schema order")


def test_urgent_codex_request_protocol() -> None:
    with TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        codex_inbox = root / "CODEX Inbox"
        codex_inbox.mkdir()
        path = codex_inbox / "urgent.md"
        text = render_message_markdown(
            {
                "schema_version": MESSAGE_SCHEMA_VERSION,
                "message_id": "PAH-URGENT-CODEX-001",
                "thread_id": "PAH-URGENT-CODEX-001",
                "created_at": "2026-04-29T12:20:00-07:00",
                "from": "claude-code",
                "to": "codex",
                "type": "urgent_request",
                "priority": "urgent",
                "status": "open",
                "thread_status": "waiting_on_agent",
                "action_owner": "codex",
                "approval_boundary": "coordination_only",
                "requires_darrin_decision": False,
            },
            "URGENT: Codex help needed",
            "Claude Code is blocked and needs Codex now.",
            "Please interrupt lower-priority work and respond.",
        )
        path.write_text(text, encoding="utf-8")
        original_values = {
            "MESSAGE_DIRS": agent_hub.MESSAGE_DIRS,
            "AGENT_INBOX_DIRS": agent_hub.AGENT_INBOX_DIRS,
            "ALL_AGENT_INBOX_DIRS": agent_hub.ALL_AGENT_INBOX_DIRS,
            "NOTIFICATION_STATE_PATH": agent_hub.NOTIFICATION_STATE_PATH,
            "NOTIFICATION_LOG_PATH": agent_hub.NOTIFICATION_LOG_PATH,
            "load_notification_config": agent_hub.load_notification_config,
            "send_notification": agent_hub.send_notification,
            "processed_message_event_status": agent_hub.processed_message_event_status,
            "record_processed_message_event": agent_hub.record_processed_message_event,
        }
        try:
            agent_hub.clear_message_parse_cache()
            agent_hub.MESSAGE_DIRS = (("Claude -> Codex", codex_inbox),)
            agent_hub.AGENT_INBOX_DIRS = {"codex": (codex_inbox,), "claude-desktop": (), "claude-code": ()}
            agent_hub.ALL_AGENT_INBOX_DIRS = (codex_inbox,)
            notification_state = root / "notification_state.json"
            notification_log = root / "notification_log.jsonl"
            processed_sidecar = root / "processed" / "urgent.json"
            sent_notifications = []
            processed_events: set[tuple[str, str]] = set()

            class FakeProcessedStatus:
                def __init__(self, status: str, sidecar_path: Path) -> None:
                    self.status = status
                    self.sidecar_path = sidecar_path

            def fake_load_notification_config() -> dict[str, object]:
                config = json.loads(json.dumps(agent_hub.DEFAULT_NOTIFICATION_CONFIG))
                config["enabled"] = False
                config["provider"] = "log_only"
                config["send_existing_on_start"] = False
                config["notify_on"].pop("urgent_codex_request", None)
                return config

            def fake_send_notification(config: dict[str, object], subject: str, body: str) -> dict[str, object]:
                sent_notifications.append({"config": dict(config), "subject": subject, "body": body})
                return {"ok": True, "provider": config.get("provider", "log_only"), "detail": "fake"}

            def fake_processed_message_event_status(message_id: str, source_path: Path, body: str, event: str) -> FakeProcessedStatus:
                status = "already_processed" if (message_id, event) in processed_events else "unseen"
                return FakeProcessedStatus(status, processed_sidecar)

            def fake_record_processed_message_event(
                message_id: str, source_path: Path, body: str, event: str, outcome: str = "sent"
            ) -> dict[str, str]:
                processed_events.add((message_id, event))
                processed_sidecar.parent.mkdir(parents=True, exist_ok=True)
                return {"content_hash": "fake-hash", "outcome": outcome}

            agent_hub.NOTIFICATION_STATE_PATH = notification_state
            agent_hub.NOTIFICATION_LOG_PATH = notification_log
            agent_hub.load_notification_config = fake_load_notification_config
            agent_hub.send_notification = fake_send_notification
            agent_hub.processed_message_event_status = fake_processed_message_event_status
            agent_hub.record_processed_message_event = fake_record_processed_message_event
            messages = agent_hub.load_messages()
            urgent = agent_hub.urgent_codex_request_rows(messages, {})
            assert_true(len(urgent) == 1, "urgent Codex request is detected")
            assert_true(agent_hub.classify_thread_state(messages[0]) == "open_on_agent", "urgent Codex request is active until replied or closed")
            assert_true(urgent[0]["kind"] == "urgent", "urgent Codex request becomes urgent queue item")
            assert_true(urgent[0]["severity"] == "err", "urgent Codex request is error-severity")
            assert_true("URGENT for Codex" in urgent[0]["wake_line"], "urgent Codex request carries an interrupt line")
            read_state_path = root / "read_state.json"
            agent_hub.set_message_read_state(path, messages[0].message_id, messages[0].body, agent_hub.READ_STATE, actor="smoke", state_path=read_state_path)
            read_state_data = agent_hub.load_read_state(read_state_path)
            read_urgent = agent_hub.urgent_codex_request_rows(messages, read_state_data)
            assert_true(len(read_urgent) == 1, "read-but-unreplied urgent Codex request stays active")
            assert_true(read_urgent[0]["read_state"] == agent_hub.READ_STATE, "urgent row exposes read state")
            assert_true(read_urgent[0]["unread"] is False, "urgent row can be read without being hidden")
            assert_true(not messages[0].is_waiting_on_darrin, "urgent Codex request does not become Darrin decision work")
            boxes = agent_hub.build_agent_mailbox_messages(messages, {})
            assert_true(len(boxes["codex"]) == 1, "urgent Codex request appears in Codex mailbox")
            assert_true(len(boxes["darrin"]) == 0, "urgent Codex request does not pollute Darrin mailbox")
            events = agent_hub.attention_events(messages, [])
            assert_true(events[0]["kind"] == "urgent_codex_request", "urgent Codex request is first notification event")
            tray = agent_hub.tray_status_payload(
                {
                    "generated_at": "2026-04-29T12:20:00",
                    "cockpit_state": {
                        "counts": {"urgent_codex_requests": 1, "stale_unread": 0, "unread": 1, "decisions_needed": 0},
                        "routes_summary": {"failed": 0, "held": 0},
                    },
                    "diagnostics": {"checks_warn": 0, "checks_fail": 0},
                    "wake_candidates": [],
                    "agents": [],
                }
            )
            assert_true(tray["level"] == "urgent", "tray status prioritizes urgent Codex requests")
            cockpit = agent_hub.cockpit_payload()
            assert_true(cockpit["action_queue"][0]["kind"] == "urgent", "cockpit queue places urgent Codex requests first")
            assert_true(cockpit["urgent_breakthrough"]["active"], "cockpit exposes active urgent breakthrough state")
            assert_true(cockpit["wake"]["route_status"] == "urgent_codex_request", "wake block prioritizes urgent Codex route")
            assert_true("URGENT for Codex" in cockpit["wake"]["line"], "wake block carries urgent Codex line")

            result = agent_hub.run_notification_scan()
            assert_true(result["enabled"] is False, "urgent scan reports optional notification config disabled")
            assert_true(result["logged"] == 1, "disabled notification config still logs urgent Codex breakthrough")
            assert_true(result["urgent_breakthrough_logged"] == 1, "urgent Codex breakthrough bypasses disabled notifications")
            assert_true(len(sent_notifications) == 1, "urgent Codex breakthrough sends one hard-channel log notification")
            assert_true(sent_notifications[0]["subject"] == "URGENT request for Codex", "urgent breakthrough subject is explicit")
            assert_true(sent_notifications[0]["config"]["provider"] == "log_only", "disabled urgent breakthrough uses log-only delivery")
            state_data = json.loads(notification_state.read_text(encoding="utf-8"))
            assert_true(
                any(key.startswith("urgent-codex:") for key in state_data.get("sent", {})),
                "urgent breakthrough records sent state",
            )
            assert_true("urgent_codex_request" in notification_log.read_text(encoding="utf-8"), "urgent breakthrough is logged")
            result_again = agent_hub.run_notification_scan()
            assert_true(result_again["urgent_breakthrough_logged"] == 0, "urgent breakthrough scan is idempotent")
            assert_true(len(sent_notifications) == 1, "urgent breakthrough does not duplicate notifications")
        finally:
            for key, value in original_values.items():
                setattr(agent_hub, key, value)
            agent_hub.clear_message_parse_cache()


def test_tray_status_payload_contract() -> None:
    status = agent_hub.tray_status_payload()
    assert_true(status["schema_version"] == 1, "tray status schema version")
    assert_true(status["ok"], "tray status reports ok")
    assert_true(status["level"] in {"ok", "urgent", "attention", "decision", "diagnostic"}, "tray status level enum")
    assert_true("stale_unread" in status["counts"], "tray status includes stale unread count")
    assert_true("diagnostic_problems" in status["counts"], "tray status includes diagnostic count")
    assert_true(isinstance(status["target_counts"], dict), "tray status target counts are structured")
    assert_true(not status["direct_wake_supported"], "tray status does not imply direct wake support")
    assert_true("Human-in-the-loop" in status["safety_label"], "tray status carries safety label")
    stale_status = agent_hub.tray_status_payload(
        {
            "generated_at": "2026-04-29T08:00:00",
            "cockpit_state": {
                "counts": {"stale_unread": 1, "unread": 2, "decisions_needed": 0},
                "routes_summary": {"failed": 0, "held": 0},
                "stale_unread_threshold_seconds": 60,
            },
            "diagnostics": {"checks_warn": 0, "checks_fail": 0},
            "wake_candidates": [{"age_seconds": 90, "wake_candidate_agent": "claude_code"}],
            "agents": [{"id": "claude_code", "display_name": "Claude Code"}],
        }
    )
    assert_true(stale_status["level"] == "attention", "tray status prioritizes stale unread messages")
    assert_true(stale_status["counts"]["stale_unread"] == 1, "tray status reports stale unread count")
    assert_true(stale_status["oldest_stale_unread_seconds"] == 90, "tray status reports oldest stale unread age")


def test_diagnostics() -> None:
    diagnostics = run_communication_diagnostics(write_report=False)
    assert_true("checks" in diagnostics, "diagnostics returns checks")
    assert_true(any(item["name"] == "two_way_file_bridge" for item in diagnostics["checks"]), "diagnostics includes bridge test")
    relay = next((item for item in diagnostics["checks"] if item["name"] == "relay_health"), None)
    assert_true(relay is not None, "diagnostics includes relay health check")
    assert_true("Relay health" in relay["detail"], "relay health check carries summary detail")


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

        renamed_path = Path(temp_dir) / "renamed-message.md"
        renamed_status = message_read_status(renamed_path, "PAH-READ-STATE-001", text, data)
        assert_true(not renamed_status["unread"], "same message id and content remains read after path drift")

        changed_status = message_read_status(message_path, "PAH-READ-STATE-001", text + "\nchanged\n", data)
        assert_true(changed_status["unread"], "changed content becomes unread")
        assert_true(changed_status["content_changed"], "changed content is flagged")

        summary = read_state_summary(data)
        assert_true(summary["counts"]["read"] == 1, "read state summary counts read records")


def test_message_parse_cache_reuses_unchanged_files_and_invalidates_changes() -> None:
    with TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        inbox = root / "CODEX Inbox"
        inbox.mkdir(parents=True)
        path = inbox / "message.md"
        first_text = render_message_markdown(
            {
                "schema_version": MESSAGE_SCHEMA_VERSION,
                "message_id": "PAH-PARSE-CACHE-001",
                "thread_id": "PAH-PARSE-CACHE-001",
                "from": "claude-desktop",
                "to": "codex",
                "type": "coordination",
                "status": "open",
                "thread_status": "active",
            },
            "First cache title",
            "Cache smoke",
            "Body.",
        )
        second_text = render_message_markdown(
            {
                "schema_version": MESSAGE_SCHEMA_VERSION,
                "message_id": "PAH-PARSE-CACHE-001",
                "thread_id": "PAH-PARSE-CACHE-001",
                "from": "claude-desktop",
                "to": "codex",
                "type": "coordination",
                "status": "open",
                "thread_status": "active",
            },
            "Second cache title",
            "Cache smoke",
            "Body changed.",
        )
        atomic_write_text(path, first_text)
        original_dirs = agent_hub.MESSAGE_DIRS
        original_parse = agent_hub.parse_message
        parse_calls = {"count": 0}

        def counting_parse(message_path: Path, direction: str) -> agent_hub.Message:
            parse_calls["count"] += 1
            return original_parse(message_path, direction)

        try:
            agent_hub.clear_message_parse_cache()
            agent_hub.MESSAGE_DIRS = (("Codex -> Claude", inbox),)
            agent_hub.parse_message = counting_parse
            first = agent_hub.load_messages()
            second = agent_hub.load_messages()
            assert_true(parse_calls["count"] == 1, "unchanged mailbox file is served from parse cache")
            assert_true(first[0].title == second[0].title == "First cache title", "cached message preserves parsed fields")

            time.sleep(0.02)
            atomic_write_text(path, second_text)
            third = agent_hub.load_messages()
            assert_true(parse_calls["count"] == 2, "changed mailbox file invalidates parse cache")
            assert_true(third[0].title == "Second cache title", "changed mailbox file is reparsed")

            path.unlink()
            empty = agent_hub.load_messages()
            assert_true(not empty, "deleted mailbox file is absent from loaded messages")
            assert_true(not agent_hub.MESSAGE_PARSE_CACHE, "deleted mailbox file is pruned from parse cache")
        finally:
            agent_hub.MESSAGE_DIRS = original_dirs
            agent_hub.parse_message = original_parse
            agent_hub.clear_message_parse_cache()


def test_port_fallback_can_be_disabled_for_tray_launches() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        sock.listen(1)
        occupied = int(sock.getsockname()[1])
        fallback = agent_hub.find_free_port(occupied, "127.0.0.1", allow_fallback=True)
        assert_true(fallback != occupied, "normal server launch can fall back from occupied port")
        try:
            agent_hub.find_free_port(occupied, "127.0.0.1", allow_fallback=False)
        except OSError:
            pass
        else:
            raise AssertionError("tray launch must fail instead of silently falling back to a random port")


def test_archive_read_mail_moves_read_messages_from_active_inboxes() -> None:
    with TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        codex_inbox = root / "CODEX Inbox"
        claude_inbox = root / "CLAUDE Inbox"
        claude_code_inbox = root / "CC Inbox"
        codex_archive = root / "CODEX Archive" / "Inbox Cleanup"
        claude_archive = root / "CLAUDE Archive" / "Inbox Cleanup"
        claude_code_archive = root / "CC Archive" / "Inbox Cleanup"
        codex_inbox.mkdir()
        claude_inbox.mkdir()
        claude_code_inbox.mkdir()
        state_path = root / "read_state.json"

        read_codex = codex_inbox / "read_codex.md"
        unread_codex = codex_inbox / "unread_codex.md"
        read_claude = claude_inbox / "read_claude.md"
        read_claude_second = claude_inbox / "read_claude_second.md"
        read_claude_code = claude_code_inbox / "read_claude_code.md"
        waiting_darrin = claude_inbox / "waiting_darrin.md"
        pre_staged_draft = claude_inbox / "pre_staged_draft.md"
        pending_dispatch = claude_inbox / "pending_dispatch.md"
        active_directive = claude_code_inbox / "active_directive.md"
        unstructured = claude_inbox / "unstructured_amendment.md"

        messages = [
            (
                read_codex,
                "PAH-ARCHIVE-READ-CODEX",
                {
                    "from": "claude-code",
                    "to": "codex",
                    "type": "report",
                    "status": "complete",
                    "thread_status": "closed",
                },
            ),
            (
                unread_codex,
                "PAH-ARCHIVE-UNREAD-CODEX",
                {
                    "from": "claude-code",
                    "to": "codex",
                    "type": "report",
                    "status": "complete",
                    "thread_status": "closed",
                },
            ),
            (
                read_claude,
                "PAH-ARCHIVE-READ-CLAUDE",
                {
                    "from": "codex",
                    "to": "claude-desktop",
                    "type": "report",
                    "status": "complete",
                    "thread_status": "closed",
                    "thread_id": "PAH-ARCHIVE-CLAUDE-MULTI",
                },
            ),
            (
                read_claude_second,
                "PAH-ARCHIVE-READ-CLAUDE-SECOND",
                {
                    "from": "codex",
                    "to": "claude-desktop",
                    "type": "report",
                    "status": "complete",
                    "thread_status": "closed",
                    "thread_id": "PAH-ARCHIVE-CLAUDE-MULTI",
                },
            ),
            (
                read_claude_code,
                "PAH-ARCHIVE-READ-CLAUDE-CODE",
                {
                    "from": "codex",
                    "to": "claude-code",
                    "type": "report",
                    "status": "complete",
                    "thread_status": "closed",
                },
            ),
            (
                waiting_darrin,
                "PAH-ARCHIVE-WAITING-DARRIN",
                {
                    "from": "claude-code",
                    "to": "claude-desktop",
                    "type": "decision_request",
                    "status": "open",
                    "thread_status": "waiting_on_darrin",
                    "requires_darrin_decision": True,
                },
            ),
            (
                pre_staged_draft,
                "PAH-ARCHIVE-PRE-STAGED-DRAFT",
                {
                    "from": "claude-desktop",
                    "to": "codex",
                    "type": "dispatch",
                    "status": "drafted_pending_phase2_ship",
                    "thread_status": "draft",
                    "action_owner": "claude_desktop",
                    "requires_darrin_decision": True,
                    "approval_boundary": "dispatch_after_phase2_ship",
                },
            ),
            (
                pending_dispatch,
                "PAH-ARCHIVE-PENDING-DISPATCH",
                {
                    "from": "claude-desktop",
                    "to": "claude-code",
                    "type": "dispatch",
                    "status": "active",
                    "thread_status": "active",
                },
            ),
            (
                active_directive,
                "PAH-ARCHIVE-ACTIVE-DIRECTIVE",
                {
                    "from": "claude-desktop",
                    "to": "claude-code",
                    "type": "directive",
                    "status": "authorized",
                    "thread_status": "active",
                    "action_owner": "claude_code",
                    "approval_boundary": "build_go",
                },
            ),
        ]
        for path, message_id, overrides in messages:
            metadata = {
                "schema_version": MESSAGE_SCHEMA_VERSION,
                "id": message_id,
                "thread_id": message_id,
                "created_at": "2026-04-29T10:00:00-07:00",
                "priority": "normal",
                "approval_boundary": "coordination_only",
                "requires_darrin_decision": False,
                **overrides,
            }
            text = render_message_markdown(metadata, "Archive read smoke", "Smoke test", "Body.")
            path.write_text(text, encoding="utf-8")
            if path != unread_codex:
                set_message_read_state(path, message_id, text, "read", actor="smoke", state_path=state_path)
        unstructured.write_text(
            "# Dispatch Amendment\n\n**Message-ID:** `PAH-UNSTRUCTURED-AMENDMENT`\n**From:** Claude Desktop\n**To:** Claude Code\n",
            encoding="utf-8",
        )
        conflict_date_dir = agent_hub.datetime.fromtimestamp(read_codex.stat().st_mtime).strftime("%Y%m%d")
        conflicting_requested_destination = codex_archive / "CODEX Inbox" / conflict_date_dir / read_codex.name
        conflicting_requested_destination.parent.mkdir(parents=True, exist_ok=True)
        conflicting_requested_destination.write_text("existing archive copy\n", encoding="utf-8")

        original_values = {
            "MESSAGE_DIRS": agent_hub.MESSAGE_DIRS,
            "CLEANUP_MAILBOX_TARGETS": agent_hub.CLEANUP_MAILBOX_TARGETS,
            "CLEANUP_ARCHIVE_ROOTS": agent_hub.CLEANUP_ARCHIVE_ROOTS,
            "SWEEP_AUDIT_LOG_PATH": agent_hub.SWEEP_AUDIT_LOG_PATH,
            "INTERACTION_LEDGER_PATH": agent_hub.INTERACTION_LEDGER_PATH,
            "load_read_state": agent_hub.load_read_state,
        }
        try:
            agent_hub.MESSAGE_DIRS = (
                ("Codex Inbox", codex_inbox),
                ("Claude Inbox", claude_inbox),
                ("CC Inbox", claude_code_inbox),
            )
            agent_hub.CLEANUP_MAILBOX_TARGETS = {
                "all": (codex_inbox, claude_inbox, claude_code_inbox),
                "codex": (codex_inbox,),
                "claude-desktop": (claude_inbox,),
                "claude-code": (claude_code_inbox,),
            }
            agent_hub.CLEANUP_ARCHIVE_ROOTS = {
                codex_inbox: codex_archive,
                claude_inbox: claude_archive,
                claude_code_inbox: claude_code_archive,
            }
            agent_hub.SWEEP_AUDIT_LOG_PATH = root / "CODEX logs" / "CODEX_pah_sweep_audit.md"
            agent_hub.INTERACTION_LEDGER_PATH = root / "CODEX logs" / "CODEX_pah_interaction_ledger.jsonl"
            agent_hub.load_read_state = lambda: json.loads(state_path.read_text(encoding="utf-8"))

            preview = agent_hub.archive_read_codex_inbox_messages(actor="smoke", dry_run=True)
            assert_true(preview["protocol_version"] == 2, "archive read returns protocol v2 summary")
            assert_true(preview["count"] == 4, "dry run finds every read message across active inboxes")
            assert_true(preview["archive_conflicts"] == 1, "dry run reports archive destination conflicts")
            assert_true(
                read_codex.exists() and read_claude.exists() and read_claude_second.exists() and read_claude_code.exists(),
                "dry run does not move files",
            )
            preview_by_name = {item["name"]: item for item in preview["inbox_summary"]}
            assert_true(preview_by_name["CODEX Inbox"]["archive_conflicts"] == 1, "dry run reports Codex archive conflict")
            assert_true(preview_by_name["CLAUDE Inbox"]["scanned"] == 6, "dry run scans every Claude Desktop inbox message")
            assert_true(preview_by_name["CLAUDE Inbox"]["candidates"] == 2, "dry run finds both read Claude Desktop candidates")
            assert_true(preview_by_name["CLAUDE Inbox"]["moved"] == 0, "dry run reports no moved Claude Desktop files")
            assert_true(preview["skipped_pre_staged_pending_trigger"] == 1, "dry run skips pre-staged pending-trigger drafts")
            assert_true(preview["skipped_pending_dispatch"] == 1, "dry run skips read pending dispatches")
            assert_true(preview["skipped_active_thread"] == 1, "dry run skips active agent-owned directive threads")
            assert_true(preview["skipped_unstructured"] == 1, "dry run skips unstructured mailbox messages")

            result = agent_hub.archive_read_codex_inbox_messages(actor="smoke", dry_run=False)
            assert_true(result["protocol_version"] == 2, "archive read move returns protocol v2 summary")
            assert_true(result["count"] == 4, "archive read moves all read non-Darrin-waiting messages")
            assert_true(result["archive_conflicts"] == 1, "archive read move reports archive destination conflicts")
            assert_true(not read_codex.exists(), "read Codex inbox message is removed")
            assert_true(not read_claude.exists(), "read Claude inbox message is removed")
            assert_true(not read_claude_second.exists(), "second read Claude inbox message is removed")
            assert_true(not read_claude_code.exists(), "read Claude Code inbox message is removed")
            assert_true(unread_codex.exists(), "unread message stays active")
            assert_true(waiting_darrin.exists(), "Darrin-waiting message stays active")
            assert_true(pre_staged_draft.exists(), "pre-staged draft stays active even when read")
            assert_true(pending_dispatch.exists(), "pending dispatch stays active even when read")
            assert_true(active_directive.exists(), "active directive stays active even when read")
            assert_true(unstructured.exists(), "unstructured mailbox message stays active")
            assert_true(any((codex_archive / "CODEX Inbox").rglob("read_codex.md")), "Codex read mail lands in archive")
            assert_true(any((claude_archive / "CLAUDE Inbox").rglob("read_claude.md")), "Claude read mail lands in archive")
            assert_true(
                any((claude_archive / "CLAUDE Inbox").rglob("read_claude_second.md")),
                "second Claude read mail lands in archive",
            )
            assert_true(
                any((claude_code_archive / "CC Inbox").rglob("read_claude_code.md")),
                "Claude Code read mail lands in archive",
            )
            codex_move = next(item for item in result["moved"] if item["message_id"] == "PAH-ARCHIVE-READ-CODEX")
            assert_true(codex_move["destination_conflict"] is True, "archive move record reports destination conflict")
            assert_true(
                codex_move["requested_destination"] == str(conflicting_requested_destination),
                "archive move record preserves requested destination",
            )
            assert_true(codex_move["destination"].endswith("read_codex_001.md"), "archive move record reports unique renamed destination")
            assert_true(Path(codex_move["destination"]).exists(), "conflicted archive move lands at unique destination")
            assert_true(conflicting_requested_destination.exists(), "existing archive destination is not overwritten")
            result_by_name = {item["name"]: item for item in result["inbox_summary"]}
            assert_true(result_by_name["CODEX Inbox"]["moved"] == 1, "Codex inbox reports one moved read message")
            assert_true(result_by_name["CODEX Inbox"]["archive_conflicts"] == 1, "Codex inbox reports archive conflict")
            assert_true(result_by_name["CLAUDE Inbox"]["moved"] == 2, "Claude Desktop inbox reports both read messages moved")
            assert_true(result_by_name["CC Inbox"]["moved"] == 1, "Claude Code inbox reports one moved read message")
            assert_true(result_by_name["CC Inbox"]["skipped_active_thread"] == 1, "Claude Code inbox reports active directive skip")
            assert_true(result_by_name["CLAUDE Inbox"]["skipped_waiting_on_darrin"] == 1, "Claude Desktop summary reports Darrin skip")
            assert_true(
                result_by_name["CLAUDE Inbox"]["skipped_pre_staged_pending_trigger"] == 1,
                "Claude Desktop summary reports pre-staged pending-trigger skip",
            )
            assert_true(result_by_name["CLAUDE Inbox"]["skipped_pending_dispatch"] == 1, "Claude Desktop summary reports pending dispatch skip")
            assert_true(result_by_name["CLAUDE Inbox"]["skipped_unstructured"] == 1, "Claude Desktop summary reports unstructured skip")
            assert_true(result["skipped_waiting_on_darrin"] == 1, "Darrin-waiting skip is reported")
            assert_true(result["skipped_pre_staged_pending_trigger"] == 1, "pre-staged pending-trigger skip is reported")
            assert_true(result["skipped_pending_dispatch"] == 1, "pending dispatch skip is reported")
            assert_true(result["skipped_active_thread"] == 1, "active thread skip is reported")
            assert_true(result["skipped_unstructured"] == 1, "unstructured skip is reported")
            active_messages = agent_hub.load_messages()
            active_ids = {message.message_id for message in active_messages}
            assert_true("PAH-ARCHIVE-READ-CODEX" not in active_ids, "archived read Codex mail leaves active message scan")
            assert_true("PAH-ARCHIVE-READ-CLAUDE" not in active_ids, "archived read Claude mail leaves active message scan")
            assert_true(
                "PAH-ARCHIVE-READ-CLAUDE-SECOND" not in active_ids,
                "second archived read Claude mail leaves active message scan",
            )
            assert_true("PAH-ARCHIVE-READ-CLAUDE-CODE" not in active_ids, "archived read Claude Code mail leaves active message scan")
            assert_true("PAH-ARCHIVE-UNREAD-CODEX" in active_ids, "unread mail remains in active message scan")
            assert_true("PAH-ARCHIVE-WAITING-DARRIN" in active_ids, "Darrin-waiting mail remains in active message scan")
            assert_true("PAH-ARCHIVE-PRE-STAGED-DRAFT" in active_ids, "pre-staged draft remains in active message scan")
            assert_true("PAH-ARCHIVE-ACTIVE-DIRECTIVE" in active_ids, "active directive remains in active message scan")
            active_read_state = json.loads(state_path.read_text(encoding="utf-8"))
            active_overview = agent_hub.build_mailbox_overview(active_messages, active_read_state)
            active_overview_count = sum(int(row.get("count", 0) or 0) for row in active_overview)
            assert_true(active_overview_count == len(active_messages), "mailbox overview count matches active messages after archive")
            active_mailboxes = agent_hub.build_agent_mailbox_messages(active_messages, active_read_state)
            visible_ids = {
                item["message_id"]
                for items in active_mailboxes.values()
                for item in items
            }
            assert_true("PAH-ARCHIVE-READ-CODEX" not in visible_ids, "archived read Codex mail leaves active agent mailbox")
            assert_true("PAH-ARCHIVE-READ-CLAUDE" not in visible_ids, "archived read Claude mail leaves active agent mailbox")
            assert_true(
                "PAH-ARCHIVE-READ-CLAUDE-SECOND" not in visible_ids,
                "second archived read Claude mail leaves active agent mailbox",
            )
            assert_true("PAH-ARCHIVE-READ-CLAUDE-CODE" not in visible_ids, "archived read Claude Code mail leaves active agent mailbox")
            audit_text = agent_hub.SWEEP_AUDIT_LOG_PATH.read_text(encoding="utf-8")
            assert_true("[sweep-started]" in audit_text, "sweep audit records run start")
            assert_true("[archive-moved]" in audit_text, "sweep audit records moved files")
            assert_true("owner_unknown_or_unstructured" in audit_text, "sweep audit records unstructured skip reason")
            assert_true("pre_staged_pending_trigger" in audit_text, "sweep audit records pre-staged pending-trigger skip reason")
            assert_true("active_thread_without_completion_evidence" in audit_text, "sweep audit records active thread skip reason")
            assert_true("[sweep-finished]" in audit_text, "sweep audit records run finish")
            ledger_events = [
                json.loads(line)
                for line in agent_hub.INTERACTION_LEDGER_PATH.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            ledger_event_types = {event["event_type"] for event in ledger_events}
            assert_true("archive_read_sweep_started" in ledger_event_types, "interaction ledger records sweep start")
            assert_true("message_archive_candidate" in ledger_event_types, "interaction ledger records dry-run archive candidates")
            assert_true("message_archive_skipped" in ledger_event_types, "interaction ledger records archive skips")
            assert_true("message_archived" in ledger_event_types, "interaction ledger records archived messages")
            assert_true("archive_read_sweep_finished" in ledger_event_types, "interaction ledger records sweep finish")
            assert_true(
                any(
                    event.get("event_type") == "message_archived"
                    and event.get("message_id") == "PAH-ARCHIVE-READ-CLAUDE-SECOND"
                    for event in ledger_events
                ),
                "interaction ledger records the second Claude Desktop archived read message",
            )
            assert_true(
                any(
                    event.get("event_type") == "message_archive_skipped"
                    and event.get("reason") == "pre_staged_pending_trigger"
                    for event in ledger_events
                ),
                "interaction ledger records pre-staged pending-trigger skip reason",
            )
            assert_true(
                any(
                    event.get("event_type") == "message_archive_skipped"
                    and event.get("reason") == "pending_dispatch_without_completion_evidence"
                    for event in ledger_events
                ),
                "interaction ledger records pending dispatch skip reason",
            )
            assert_true(
                any(
                    event.get("event_type") == "message_archive_skipped"
                    and event.get("reason") == "active_thread_without_completion_evidence"
                    for event in ledger_events
                ),
                "interaction ledger records active thread skip reason",
            )
        finally:
            for key, value in original_values.items():
                setattr(agent_hub, key, value)


def test_archive_read_moves_replied_tombstoned_unread_messages() -> None:
    with TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        codex_inbox = root / "CODEX Inbox"
        codex_archive = root / "CODEX Archive" / "Inbox Cleanup"
        codex_inbox.mkdir()
        state_path = root / "read_state.json"
        state_path.write_text("{}", encoding="utf-8")
        original_path = codex_inbox / "tombstoned_unread.md"
        original_text = render_message_markdown(
            {
                "schema_version": MESSAGE_SCHEMA_VERSION,
                "message_id": "PAH-TOMBSTONED-UNREAD",
                "thread_id": "PAH-TOMBSTONED-UNREAD",
                "created_at": "2026-04-29T10:00:00-07:00",
                "from": "claude-desktop",
                "to": "codex",
                "type": "directive",
                "status": "open",
                "thread_status": "active",
                "action_owner": "codex",
                "priority": "normal",
                "requires_darrin_decision": False,
                "approval_boundary": "coordination_only",
            },
            "Tombstoned unread request",
            "Already replied",
            "This original was answered elsewhere.",
        )
        original_path.write_text(original_text, encoding="utf-8")
        tombstone_path = agent_hub.reply_tombstone_path(original_path)
        tombstone_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "tombstone_type": "replied",
                    "reason": "reply_sent",
                    "original_message_id": "PAH-TOMBSTONED-UNREAD",
                    "original_thread_id": "PAH-TOMBSTONED-UNREAD",
                    "original_path": str(original_path),
                    "reply_message_id": "PAH-REPLY-001",
                    "reply_thread_id": "PAH-TOMBSTONED-UNREAD",
                    "reply_path": str(root / "CLAUDE Inbox" / "reply.md"),
                    "reply_from": "codex",
                    "reply_to": "claude-desktop",
                    "replied_at": "2026-04-29T10:05:00-07:00",
                    "actor": "codex",
                    "route": "codex_to_claude",
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        original_values = {
            "MESSAGE_DIRS": agent_hub.MESSAGE_DIRS,
            "CLEANUP_MAILBOX_TARGETS": agent_hub.CLEANUP_MAILBOX_TARGETS,
            "CLEANUP_ARCHIVE_ROOTS": agent_hub.CLEANUP_ARCHIVE_ROOTS,
            "SWEEP_AUDIT_LOG_PATH": agent_hub.SWEEP_AUDIT_LOG_PATH,
            "INTERACTION_LEDGER_PATH": agent_hub.INTERACTION_LEDGER_PATH,
            "load_read_state": agent_hub.load_read_state,
        }
        try:
            agent_hub.clear_message_parse_cache()
            agent_hub.MESSAGE_DIRS = (("Claude -> Codex", codex_inbox),)
            agent_hub.CLEANUP_MAILBOX_TARGETS = {"all": (codex_inbox,), "codex": (codex_inbox,)}
            agent_hub.CLEANUP_ARCHIVE_ROOTS = {codex_inbox: codex_archive}
            agent_hub.SWEEP_AUDIT_LOG_PATH = root / "CODEX logs" / "CODEX_pah_sweep_audit.md"
            agent_hub.INTERACTION_LEDGER_PATH = root / "CODEX logs" / "CODEX_pah_interaction_ledger.jsonl"
            agent_hub.load_read_state = lambda: json.loads(state_path.read_text(encoding="utf-8"))

            preview = agent_hub.archive_read_codex_inbox_messages(actor="smoke", dry_run=True)
            assert_true(preview["count"] == 1, "dry run treats replied tombstone as archive candidate")
            assert_true(preview["replied_tombstone"] == 1, "dry run reports replied tombstone candidate")
            assert_true(preview["moved"][0]["archive_reason"] == "replied_tombstone", "dry run reports tombstone archive reason")
            assert_true(original_path.exists(), "dry run leaves tombstoned original in place")
            assert_true(tombstone_path.exists(), "dry run leaves tombstone in place")

            result = agent_hub.archive_read_codex_inbox_messages(actor="smoke", dry_run=False)
            assert_true(result["count"] == 1, "archive read moves replied tombstoned unread original")
            assert_true(result["replied_tombstone"] == 1, "archive read reports replied tombstone move")
            assert_true(not original_path.exists(), "tombstoned unread original is removed from inbox")
            assert_true(not tombstone_path.exists(), "tombstone sidecar is removed from inbox")
            move = result["moved"][0]
            assert_true(Path(move["destination"]).exists(), "tombstoned original lands in archive")
            assert_true(Path(move["tombstone_destination"]).exists(), "tombstone sidecar lands in archive")
            ledger_events = [
                json.loads(line)
                for line in agent_hub.INTERACTION_LEDGER_PATH.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            assert_true(
                any(
                    event.get("event_type") == "message_archived"
                    and event.get("archive_reason") == "replied_tombstone"
                    for event in ledger_events
                ),
                "interaction ledger records tombstone archive reason",
            )
        finally:
            for key, value in original_values.items():
                setattr(agent_hub, key, value)
            agent_hub.clear_message_parse_cache()


def test_classifier_darrin_precedence_beats_completion_fallback() -> None:
    message = agent_hub.Message(
        direction="smoke",
        path=Path("C:/CODEX PG/smoke.md"),
        name="smoke.md",
        modified=1.0,
        title="Darrin decision beats report fallback",
        message_id="PAH-CLASSIFIER-DARRIN-PRECEDENCE",
        thread_id="PAH-CLASSIFIER-DARRIN-PRECEDENCE",
        thread_status="active",
        status="shipped",
        from_agent="claude-code",
        to_agent="claude-desktop",
        action_owner="darrin",
        requires_darrin_decision=True,
        message_type="report",
    )
    state = agent_hub.classify_thread_state(message)
    assert_true(state == "open_on_darrin", "Darrin ownership wins before completion/report fallback")


def test_classifier_pre_staged_pending_trigger_is_parked() -> None:
    message = agent_hub.Message(
        direction="smoke",
        path=Path("C:/CODEX PG/draft.md"),
        name="draft.md",
        modified=1.0,
        title="Phase 4 dispatch draft",
        message_id="PAH-CLASSIFIER-DRAFTED-PENDING",
        thread_id="PAH-CLASSIFIER-DRAFTED-PENDING",
        thread_status="draft",
        status="drafted_pending_phase2_ship",
        from_agent="claude-desktop",
        to_agent="codex",
        action_owner="darrin",
        requires_darrin_decision=True,
        message_type="dispatch",
        schema_version="1",
    )
    state = agent_hub.classify_thread_state(message)
    assert_true(state == "parked", "pre-staged pending-trigger drafts stay parked instead of open on Darrin")


def test_classifier_completion_messages_close_before_agent_owner() -> None:
    shipped_report = agent_hub.Message(
        direction="smoke",
        path=Path("C:/CODEX PG/shipped.md"),
        name="shipped.md",
        modified=1.0,
        title="Shipped report should close",
        message_id="PAH-CLASSIFIER-SHIPPED-REPORT",
        thread_id="PAH-CLASSIFIER-SHIPPED-REPORT",
        thread_status="active",
        status="shipped",
        from_agent="claude-code",
        to_agent="claude-desktop",
        action_owner="claude_desktop",
        requires_darrin_decision=False,
        message_type="report",
        schema_version="1",
    )
    state = agent_hub.classify_thread_state(shipped_report)
    assert_true(state == "closed", "shipped report closes before generic agent ownership")

    delivered_response = agent_hub.Message(
        direction="smoke",
        path=Path("C:/CODEX PG/response.md"),
        name="response.md",
        modified=1.0,
        title="Delivered response should close",
        message_id="PAH-CLASSIFIER-DELIVERED-RESPONSE",
        thread_id="PAH-CLASSIFIER-DELIVERED-RESPONSE",
        thread_status="active",
        status="response_delivered",
        from_agent="claude-desktop",
        to_agent="claude-code",
        action_owner="claude_code",
        requires_darrin_decision=False,
        message_type="coordination_response",
        schema_version="1",
    )
    state = agent_hub.classify_thread_state(delivered_response)
    assert_true(state == "closed", "response-delivered coordination response closes before generic agent ownership")

    review_report = agent_hub.Message(
        direction="smoke",
        path=Path("C:/CODEX PG/review.md"),
        name="review.md",
        modified=1.0,
        title="Review report should stay open",
        message_id="PAH-CLASSIFIER-REVIEW-REPORT",
        thread_id="PAH-CLASSIFIER-REVIEW-REPORT",
        thread_status="ready_for_review",
        status="shipped",
        from_agent="claude-code",
        to_agent="claude-desktop",
        action_owner="claude_desktop",
        requires_darrin_decision=False,
        message_type="report",
        schema_version="1",
    )
    state = agent_hub.classify_thread_state(review_report)
    assert_true(state == "open_on_agent", "ready-for-review report remains open on the reviewing agent")


def test_classifier_unstructured_inbox_message_is_owner_unknown() -> None:
    with TemporaryDirectory() as temp_dir:
        inbox = Path(temp_dir) / "CODEX Inbox"
        inbox.mkdir()
        path = inbox / "unstructured.md"
        path.write_text("# Unstructured amendment\n\n**Message-ID:** `PAH-NO-FRONTMATTER`\n", encoding="utf-8")
        original_dirs = agent_hub.ALL_AGENT_INBOX_DIRS
        try:
            agent_hub.ALL_AGENT_INBOX_DIRS = (inbox,)
            message = agent_hub.parse_message(path, "Codex Inbox")
            state = agent_hub.classify_thread_state(message)
            assert_true(state == "owner_unknown", "unstructured active inbox message is owner_unknown")
        finally:
            agent_hub.ALL_AGENT_INBOX_DIRS = original_dirs


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
    test_create_message_dry_run_does_not_write_mail()
    test_create_message_writes_reply_tombstone_for_active_message()
    test_cockpit_payload_contract()
    test_health_payload_contract()
    test_agent_progress_monitor_contract()
    test_codex_mailbox_sla_progress()
    test_health_payload_unanswered_component()
    test_periodic_archive_sweep_contract()
    test_periodic_steward_schedule_metadata()
    test_pah_inspector_detects_retired_ui_routes()
    test_pah_inspector_summary_and_markdown_report()
    test_interaction_ledger_helper_writes_jsonl()
    test_interaction_ledger_recent_events_and_summary()
    test_message_audit_records_discovery_and_classifier_transition()
    test_agent_no_mail_claim_validation()
    test_periodic_communication_backlog_detects_discrepancies()
    test_periodic_communication_backlog_records_discrepancy_event()
    test_cockpit_action_queue_ordering()
    test_urgent_codex_request_protocol()
    test_tray_status_payload_contract()
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
    test_message_parse_cache_reuses_unchanged_files_and_invalidates_changes()
    test_port_fallback_can_be_disabled_for_tray_launches()
    test_archive_read_mail_moves_read_messages_from_active_inboxes()
    test_archive_read_moves_replied_tombstoned_unread_messages()
    test_classifier_darrin_precedence_beats_completion_fallback()
    test_classifier_pre_staged_pending_trigger_is_parked()
    test_classifier_completion_messages_close_before_agent_owner()
    test_classifier_unstructured_inbox_message_is_owner_unknown()
    test_thread_archive_state_reopens_on_new_activity()
    test_decision_state()
    test_validation_state()
    test_route_test_state()
    test_work_board_state()
    print("PAH smoke tests passed")


if __name__ == "__main__":
    main()
