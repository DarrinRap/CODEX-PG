"""Standalone PAH path contracts."""

from __future__ import annotations

from pathlib import Path


HUB_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = HUB_ROOT.parent
MAILBOX_ROOT = PROJECT_ROOT / "CODEX Claude Codex Mailbox"
CODEX_INBOX = MAILBOX_ROOT / "CODEX Inbox"
CLAUDE_INBOX = MAILBOX_ROOT / "CLAUDE Inbox"
PANDA_GALLERY_ROOT = PROJECT_ROOT.parent / "panda-gallery"
CC_MAILBOX_ROOT = PANDA_GALLERY_ROOT / "workflows" / "cc_mailbox"
CC_INBOX = CC_MAILBOX_ROOT / "CC Inbox"
CC_CLAUDE_INBOX = CC_MAILBOX_ROOT / "CLAUDE Inbox"
CC_SENT = CC_MAILBOX_ROOT / "CC Sent"
CC_CLAUDE_SENT = CC_MAILBOX_ROOT / "CLAUDE Sent"
PAH_CLAUDE_CODE_INBOX = MAILBOX_ROOT / "CODEX_CLAUDE_CODE Inbox"
CLAUDE_CODE_INBOX = CC_INBOX if CC_MAILBOX_ROOT.exists() else PAH_CLAUDE_CODE_INBOX
CLAUDE_CODE_INBOX_LEGACY = MAILBOX_ROOT / "CODEX Claude Code Inbox"
CODEX_SENT = MAILBOX_ROOT / "CODEX Sent"
CLAUDE_SENT = MAILBOX_ROOT / "CLAUDE Sent"
LEDGER_PATH = MAILBOX_ROOT / "CODEX_MAILBOX_LEDGER.md"
DECISION_QUEUE_PATH = MAILBOX_ROOT / "CODEX_DARRIN_DECISIONS_NEEDED.md"
REPORTS_DIR = HUB_ROOT / "CODEX reports"
CONFIG_DIR = HUB_ROOT / "CODEX config"
NOTIFICATIONS_DIR = HUB_ROOT / "CODEX notifications"
DIAGNOSTICS_DIR = HUB_ROOT / "CODEX diagnostics"
APPROVALS_DIR = HUB_ROOT / "CODEX approvals"
ADAPTERS_DIR = HUB_ROOT / "CODEX adapters"
STATE_DIR = HUB_ROOT / "CODEX state"
PROCESSED_MESSAGES_DIR = STATE_DIR / "processed_messages"
QUARANTINE_DIR = MAILBOX_ROOT / "PAH Quarantine"
APPROVAL_RECORDS_PATH = APPROVALS_DIR / "CODEX_approval_records.local.jsonl"
DECISION_STATE_PATH = STATE_DIR / "CODEX_decision_state.local.json"
READ_STATE_PATH = STATE_DIR / "CODEX_read_state.local.json"
THREAD_ARCHIVE_STATE_PATH = STATE_DIR / "CODEX_thread_archive_state.local.json"
VALIDATION_STATE_PATH = STATE_DIR / "CODEX_validation_state.local.json"
ROUTE_TEST_STATE_PATH = STATE_DIR / "CODEX_route_test_state.local.json"
WORK_ITEMS_STATE_PATH = STATE_DIR / "CODEX_work_items.local.json"

MESSAGE_DIRS = [
    ("Claude -> Codex", CODEX_INBOX),
    ("Codex -> Claude", CLAUDE_INBOX),
    ("To Claude Code", CLAUDE_CODE_INBOX),
    ("Claude Code -> Claude", CC_CLAUDE_INBOX),
    ("Claude Code Sent", CC_SENT),
    ("Claude Sent (CC mailbox)", CC_CLAUDE_SENT),
    ("Codex -> Claude Code (PAH local legacy)", PAH_CLAUDE_CODE_INBOX),
    ("Codex -> Claude Code (legacy)", CLAUDE_CODE_INBOX_LEGACY),
    ("Codex Sent", CODEX_SENT),
    ("Claude Sent", CLAUDE_SENT),
]

ROUTE_INBOXES = {
    "codex_to_claude": CLAUDE_INBOX,
    "codex_to_claude_code": CLAUDE_CODE_INBOX,
    "claude_to_codex": CODEX_INBOX,
}


def ensure_runtime_dirs() -> None:
    for path in (
        CONFIG_DIR,
        NOTIFICATIONS_DIR,
        DIAGNOSTICS_DIR,
        APPROVALS_DIR,
        ADAPTERS_DIR,
        STATE_DIR,
        PROCESSED_MESSAGES_DIR,
        PAH_CLAUDE_CODE_INBOX,
    ):
        path.mkdir(parents=True, exist_ok=True)
