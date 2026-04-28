"""Cross-check auto-resolution safety rules for PAH messages."""

from __future__ import annotations

import re
from typing import Any


RISK_VALUES = {"low", "medium", "high", "critical"}
RISK_RE = re.compile(r"\brisk\s*[:=]\s*(low|medium|high|critical)\b", re.IGNORECASE)


def _as_list(value: Any) -> list[Any]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return value
    return [value]


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"true", "yes", "1", "y", "auto", "auto_resolve"}


def cross_check_auto_resolution_requested(metadata: dict[str, Any]) -> bool:
    recommendation = str(metadata.get("recommendation", "")).strip().lower().replace("-", "_")
    return _as_bool(metadata.get("auto_resolution")) or recommendation in {"auto_resolve", "auto_resolution"}


def approval_boundary_requires_darrin(metadata: dict[str, Any]) -> bool:
    return "_requires_darrin" in str(metadata.get("approval_boundary", "")).strip().lower()


def caught_item_risk(item: Any) -> str:
    if isinstance(item, dict):
        return str(item.get("risk", "")).strip().lower()
    text = str(item or "").strip()
    if text.lower() in RISK_VALUES:
        return text.lower()
    match = RISK_RE.search(text)
    return match.group(1).lower() if match else ""


def cross_check_auto_resolution_status(
    cross_check_metadata: dict[str, Any],
    involved_metadata: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    reasons: list[str] = []
    disagrees_with = [item for item in _as_list(cross_check_metadata.get("disagrees_with")) if str(item).strip()]
    if disagrees_with:
        reasons.append("disagrees_with must be empty")

    caught_by_one = _as_list(cross_check_metadata.get("caught_by_one"))
    caught_risks = [caught_item_risk(item) for item in caught_by_one]
    missing_risks = len([risk for risk in caught_risks if not risk])
    elevated_risks = sorted({risk for risk in caught_risks if risk and risk != "low"})
    if missing_risks:
        reasons.append("every caught_by_one entry must include a risk")
    if elevated_risks:
        reasons.append(f"caught_by_one risk must be low only; found {', '.join(elevated_risks)}")

    involved = [cross_check_metadata, *(involved_metadata or [])]
    if any(approval_boundary_requires_darrin(item) for item in involved):
        reasons.append("approval_boundary requiring Darrin blocks auto-resolution")

    return {
        "eligible": not reasons,
        "reasons": reasons,
        "disagrees_with": disagrees_with,
        "caught_risks": caught_risks,
    }


def validate_cross_check_auto_resolution(metadata: dict[str, Any]) -> list[str]:
    if str(metadata.get("type", "")).strip().lower() != "cross_check":
        return []
    if not cross_check_auto_resolution_requested(metadata):
        return []
    status = cross_check_auto_resolution_status(metadata)
    return [] if status["eligible"] else [
        "cross_check auto-resolution blocked: " + "; ".join(status["reasons"])
    ]
