"""Adapter registry for future PAH live integrations.

Adapters remain disabled by default. This registry lets the dashboard show what
could exist without launching tools, spending money, or calling external APIs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Adapter:
    adapter_id: str
    display_name: str
    kind: str
    enabled: bool
    safety_status: str
    notes: str


ADAPTERS: tuple[Adapter, ...] = (
    Adapter(
        "claude_code_headless",
        "Claude Code Headless",
        "agent_execution",
        False,
        "disabled_requires_strict_tools_temp_worktree_and_darrin_approval",
        "Must use restrictive tool allowlist, strict MCP config, setting-source isolation, and a temp worktree.",
    ),
    Adapter(
        "claude_desktop_mcp",
        "Claude Desktop MCP",
        "mcp_bridge",
        False,
        "disabled_pending_mcp_contract",
        "Future two-way bridge after explicit MCP tool contracts are approved.",
    ),
    Adapter(
        "openai_api_lane",
        "OpenAI API Lane",
        "api_agent",
        False,
        "disabled_requires_credentials_and_budget_approval",
        "Future direct Codex/OpenAI lane; no credentials or paid calls are configured in this build.",
    ),
    Adapter(
        "anthropic_api_lane",
        "Anthropic API Lane",
        "api_agent",
        False,
        "disabled_requires_credentials_and_budget_approval",
        "Future direct Claude lane; no credentials or paid calls are configured in this build.",
    ),
    Adapter(
        "sms_live_provider",
        "Live SMS Provider",
        "external_notification",
        False,
        "disabled_until_local_config_and_darrin_approval",
        "Template supports Twilio/email/webhook, but live sending remains off until local config is enabled.",
    ),
)


def adapter_status() -> dict[str, Any]:
    rows = [adapter.__dict__ for adapter in ADAPTERS]
    return {
        "enabled": sum(1 for adapter in ADAPTERS if adapter.enabled),
        "disabled": sum(1 for adapter in ADAPTERS if not adapter.enabled),
        "adapters": rows,
    }

