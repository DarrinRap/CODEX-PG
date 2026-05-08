"""Participant registry and route contracts for PANDA Agent Hub."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Participant:
    participant_id: str
    display_name: str
    role: str
    inbox_name: str | None = None
    can_receive_direct_mail: bool = True


PARTICIPANTS: dict[str, Participant] = {
    "darrin": Participant("darrin", "Darrin", "owner", None, False),
    "pah": Participant("pah", "PANDA Agent Hub", "router", "PAH Inbox", False),
    "codex": Participant("codex", "Codex", "agent", "CODEX Inbox"),
    "claude-desktop": Participant("claude-desktop", "Claude Desktop", "agent", "CLAUDE Inbox"),
    "claude-code": Participant("claude-code", "Claude Code", "agent", "CC Inbox"),
}

ALIASES: dict[str, str] = {
    "cc": "claude-code",
    "claude code": "claude-code",
    "claude-code": "claude-code",
    "claude_code": "claude-code",
    "claude desktop": "claude-desktop",
    "claude (desktop)": "claude-desktop",
    "claude": "claude-desktop",
    "claude-desktop": "claude-desktop",
    "codex": "codex",
    "pah": "pah",
    "panda agent hub": "pah",
    "darrin": "darrin",
}

ROUTES: dict[str, tuple[str, str]] = {
    "codex_to_claude": ("codex", "claude-desktop"),
    "codex_to_claude_code": ("codex", "claude-code"),
    "claude_to_codex": ("claude-desktop", "codex"),
}


def canonical_participant(value: str) -> str:
    key = str(value or "").strip().lower().replace("_", " ")
    return ALIASES.get(key, str(value or "").strip())


def participant_label(participant_id: str) -> str:
    participant = PARTICIPANTS.get(canonical_participant(participant_id))
    return participant.display_name if participant else participant_id


def route_participants(route: str) -> tuple[str, str]:
    try:
        return ROUTES[route]
    except KeyError as exc:
        raise ValueError(f"Unsupported PAH route: {route}") from exc
