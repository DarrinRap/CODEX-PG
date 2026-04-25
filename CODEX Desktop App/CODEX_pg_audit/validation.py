from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

MANIFEST_SCHEMA = "pg.session_package.v1"
EVIDENCE_ID_RE = re.compile(r"^ev_[a-z0-9_]+_\d{4}$")
ALLOWED_PACKAGE_STATES = {"draft", "local_ready", "queued_for_upload", "uploading", "uploaded_pending_verification", "remote_ready", "processing", "processing_failed", "triage_ready", "archived"}
ALLOWED_OUTCOMES = {"PASS", "FAIL", "SKIP", "ACK", "PARTIAL", None}


@dataclass
class ValidationReport:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def as_dict(self) -> dict[str, Any]:
        return {"ok": self.ok, "error_count": len(self.errors), "warning_count": len(self.warnings), "errors": self.errors, "warnings": self.warnings}


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_json(data: Any) -> str:
    encoded = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def require_fields(report: ValidationReport, obj: dict[str, Any], fields: list[str], path: str) -> None:
    for field_name in fields:
        if field_name not in obj:
            report.error(f"{path}.{field_name} is required")


def validate_file_record(report: ValidationReport, package_dir: Path, record: dict[str, Any], path: str, id_field: str) -> None:
    require_fields(report, record, [id_field, "kind", "package_path", "sha256", "bytes"], path)
    package_path = record.get("package_path")
    if not isinstance(package_path, str):
        report.error(f"{path}.package_path must be a string")
        return
    if Path(package_path).is_absolute() or ".." in Path(package_path).parts:
        report.error(f"{path}.package_path must be a safe relative path: {package_path}")
        return
    file_path = package_dir / package_path
    if not file_path.exists():
        report.error(f"{path}.package_path does not exist: {package_path}")
        return
    if record.get("bytes") != file_path.stat().st_size:
        report.error(f"{path}.bytes mismatch for {package_path}")
    if record.get("sha256") != sha256_file(file_path):
        report.error(f"{path}.sha256 mismatch for {package_path}")


def validate_manifest(manifest_path: Path) -> ValidationReport:
    report = ValidationReport()
    manifest = read_json(manifest_path)
    if not isinstance(manifest, dict):
        report.error("manifest must be an object")
        return report
    package_dir = manifest_path.parent
    require_fields(report, manifest, ["schema", "schema_version", "package_id", "session_id", "run_id", "package_state", "created_at", "sources", "evidence", "steps", "integrity", "missing_sources", "warnings"], "manifest")
    if manifest.get("schema") != MANIFEST_SCHEMA:
        report.error(f"manifest.schema must be {MANIFEST_SCHEMA}")
    if manifest.get("schema_version") != 1:
        report.error("manifest.schema_version must be 1")
    if manifest.get("package_state") not in ALLOWED_PACKAGE_STATES:
        report.error(f"manifest.package_state is not allowed: {manifest.get('package_state')}")

    evidence_ids: set[str] = set()
    for index, source in enumerate(manifest.get("sources") or []):
        if isinstance(source, dict):
            validate_file_record(report, package_dir, source, f"manifest.sources[{index}]", "source_id")
        else:
            report.error(f"manifest.sources[{index}] must be an object")

    for index, evidence in enumerate(manifest.get("evidence") or []):
        if not isinstance(evidence, dict):
            report.error(f"manifest.evidence[{index}] must be an object")
            continue
        evidence_id = evidence.get("evidence_id")
        if not isinstance(evidence_id, str) or not EVIDENCE_ID_RE.match(evidence_id):
            report.error(f"manifest.evidence[{index}].evidence_id has invalid format: {evidence_id}")
        elif evidence_id in evidence_ids:
            report.error(f"Duplicate evidence_id: {evidence_id}")
        else:
            evidence_ids.add(evidence_id)
        validate_file_record(report, package_dir, evidence, f"manifest.evidence[{index}]", "evidence_id")

    for index, step in enumerate(manifest.get("steps") or []):
        if not isinstance(step, dict):
            report.error(f"manifest.steps[{index}] must be an object")
            continue
        require_fields(report, step, ["step_n", "kind", "title", "outcome", "evidence_ids", "source_result_index"], f"manifest.steps[{index}]")
        if step.get("outcome") not in ALLOWED_OUTCOMES:
            report.error(f"manifest.steps[{index}].outcome is not allowed: {step.get('outcome')}")
        for evidence_id in step.get("evidence_ids") or []:
            if evidence_id not in evidence_ids:
                report.error(f"manifest.steps[{index}] references unknown evidence_id: {evidence_id}")

    integrity = manifest.get("integrity") or {}
    if not isinstance(integrity, dict):
        report.error("manifest.integrity must be an object")
    else:
        if integrity.get("hash_algorithm") != "sha256":
            report.error("manifest.integrity.hash_algorithm must be sha256")
        manifest_without_integrity = dict(manifest)
        manifest_without_integrity["integrity"] = {}
        if integrity.get("manifest_without_integrity_sha256") != sha256_json(manifest_without_integrity):
            report.error("manifest.integrity.manifest_without_integrity_sha256 mismatch")
    return report
