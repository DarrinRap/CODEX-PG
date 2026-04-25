from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def compact_timestamp() -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y%m%d_%H%M%S")


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def load_manifest(manifest_path: Path) -> dict[str, Any]:
    with manifest_path.open("r", encoding="utf-8-sig") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected manifest object in {manifest_path}")
    return data


def first_issue_candidate(manifest: dict[str, Any]) -> tuple[dict[str, Any], list[str]] | None:
    evidence_by_step: dict[int, list[str]] = {}
    for evidence in manifest.get("evidence", []):
        if not isinstance(evidence, dict):
            continue
        step_n = evidence.get("step_n")
        evidence_id = evidence.get("evidence_id")
        if isinstance(step_n, int) and isinstance(evidence_id, str):
            evidence_by_step.setdefault(step_n, []).append(evidence_id)

    for step in manifest.get("steps", []):
        if not isinstance(step, dict):
            continue
        step_n = step.get("step_n")
        evidence_ids = step.get("evidence_ids") or evidence_by_step.get(step_n, [])
        if step.get("outcome") == "FAIL" and evidence_ids:
            return step, list(evidence_ids)

    for step in manifest.get("steps", []):
        if not isinstance(step, dict):
            continue
        evidence_ids = step.get("evidence_ids") or []
        if evidence_ids:
            return step, list(evidence_ids)
    return None


def build_mock_issue_extraction(manifest_path: Path, output_path: Path | None = None) -> Path:
    """Create deterministic local fixture issues from package evidence IDs.

    This is a no-network stand-in for future AI extraction. It intentionally
    emits at most one issue so validation and dashboard flows can be developed
    without pretending a real model reviewed the evidence.
    """
    manifest = load_manifest(manifest_path)
    created_at = now_iso()
    package_id = str(manifest["package_id"])
    session_id = str(manifest["session_id"])
    run_id = str(manifest["run_id"])
    candidate = first_issue_candidate(manifest)
    issues: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    if candidate is None:
        warnings.append({
            "warning_type": "no_evidence_issue_created",
            "message": "No evidence-linked step was available for mock extraction.",
        })
    else:
        step, evidence_ids = candidate
        step_n = step.get("step_n")
        title = str(step.get("title") or f"Step {step_n}")
        issue_stamp = compact_timestamp()
        issues.append({
            "issue_id": f"iss_{issue_stamp}_0001",
            "package_id": package_id,
            "session_id": session_id,
            "run_id": run_id,
            "title": f"Review evidence for Step {step_n}: {title}",
            "summary": "Mock extraction created a reviewer placeholder from existing package evidence.",
            "category": "ui_ux" if step.get("outcome") != "FAIL" else "functional_bug",
            "priority": "P2" if step.get("outcome") == "FAIL" else "P3",
            "confidence": 0.5,
            "status": "needs_review",
            "source_steps": [step_n],
            "evidence_ids": evidence_ids,
            "transcript_refs": [],
            "observed_behavior": step.get("note") or "Evidence is available for reviewer inspection.",
            "expected_behavior": "Reviewer confirms whether the evidence represents a valid product issue.",
            "impact": "This placeholder exercises the evidence-linked review workflow without using a real AI provider.",
            "suggested_response": {
                "subject": f"Testing finding: Step {step_n}",
                "body_markdown": "Please review the linked evidence and replace this mock draft with reviewer-approved text.",
                "tone": "clear_direct",
            },
            "reviewer": {
                "assigned_to": None,
                "reviewed_by": None,
                "reviewed_at": None,
                "reviewer_notes": None,
                "edited_title": None,
                "edited_summary": None,
                "edited_response_markdown": None,
            },
            "lineage": {
                "created_by_model": False,
                "model_reasoning_summary": "Local mock extraction; no AI provider was called.",
                "dedupe_group_id": None,
                "supersedes_issue_ids": [],
                "related_issue_ids": [],
            },
            "audit": {
                "created_at": created_at,
                "updated_at": created_at,
                "events": [
                    {
                        "event_id": f"evt_{issue_stamp}_0001",
                        "event_type": "created",
                        "actor": {"actor_type": "system", "display_name": "codex-local-mock", "email": None},
                        "created_at": created_at,
                        "from_status": None,
                        "to_status": "needs_review",
                        "note": "Created by local mock extraction.",
                        "diff_summary": None,
                    }
                ],
            },
        })

    extraction = {
        "schema": "pg.audit_issue_extraction.v1",
        "schema_version": 1,
        "extraction_id": f"extract_mock_{compact_timestamp()}",
        "package_id": package_id,
        "session_id": session_id,
        "run_id": run_id,
        "created_at": created_at,
        "created_by": {
            "type": "local_fixture",
            "provider": "none",
            "model": "none",
            "prompt_version": "pg.audit_extract.mock.v1",
        },
        "issues": issues,
        "dedupe_groups": [],
        "warnings": warnings,
    }
    if output_path is None:
        output_path = manifest_path.parent / "derived" / "audit_issue_extraction_v1.json"
    write_json(output_path, extraction)
    return output_path
