#!/usr/bin/env python3
"""Reference local package builder for the Panda Gallery Testing + Audit MVP.

This is starter-pack code, not live Panda Gallery integration code. It shows Claude
how to produce a local, integrity-checkable session package from existing session
outputs without editing C:\\panda-gallery.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PACKAGE_SCHEMA = "pg.session_package.v1"
PACKAGE_SCHEMA_VERSION = 1
GENERATED_BY_VERSION = "codex-audit-mvp-starter-pack-v1"


def now_iso() -> str:
    """Return a local timezone ISO timestamp with seconds precision."""
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def file_time_iso(path: Path) -> str:
    """Return a file modification timestamp as an ISO string."""
    return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).astimezone().isoformat(timespec="seconds")


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_json(data: Any) -> str:
    encoded = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def mime_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".png":
        return "image/png"
    if suffix in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if suffix == ".json":
        return "application/json"
    if suffix == ".md":
        return "text/markdown"
    if suffix == ".txt":
        return "text/plain"
    return "application/octet-stream"


def normalize_rel(path_text: str) -> Path:
    return Path(path_text.replace("\\", "/"))


def safe_remove_tree(target: Path, allowed_parent: Path) -> None:
    """Remove a generated package folder only after confirming it is inside output root."""
    resolved_target = target.resolve()
    resolved_parent = allowed_parent.resolve()
    if resolved_target == resolved_parent or resolved_parent not in resolved_target.parents:
        raise ValueError(f"Refusing to remove path outside output root: {resolved_target}")
    shutil.rmtree(resolved_target)


@dataclass
class BuildContext:
    source_dir: Path
    output_root: Path
    overwrite: bool = False
    created_at: str = field(default_factory=now_iso)
    missing_sources: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    evidence_counts: dict[str, int] = field(default_factory=dict)

    def next_evidence_id(self, kind: str) -> str:
        self.evidence_counts[kind] = self.evidence_counts.get(kind, 0) + 1
        return f"ev_{kind}_{self.evidence_counts[kind]:04d}"


def find_optional(source_dir: Path, candidates: list[str]) -> Path | None:
    for candidate in candidates:
        path = source_dir / candidate
        if path.exists():
            return path
    return None


def copy_record(src: Path, package_dir: Path, package_path: str, source_id: str, kind: str, required: bool) -> dict[str, Any]:
    dest = package_dir / package_path
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    return {
        "source_id": source_id,
        "kind": kind,
        "original_path": str(src),
        "package_path": package_path.replace("\\", "/"),
        "required": required,
        "sha256": sha256_file(dest),
        "bytes": dest.stat().st_size,
        "captured_at": file_time_iso(src),
    }


def build_sources(ctx: BuildContext, package_dir: Path) -> tuple[list[dict[str, Any]], dict[str, Path]]:
    source_dir = ctx.source_dir
    found: dict[str, Path] = {}
    records: list[dict[str, Any]] = []

    source_specs = [
        ("results", ["results_latest.json"], "source/results_latest.json", "src_results_latest", "results_json", True),
        ("metadata", ["metadata.json", "metadata/metadata.json"], "source/metadata.json", "src_metadata", "metadata_json", False),
        ("transcript", ["transcript.md", "transcripts/transcript.md"], "source/transcript.md", "src_transcript", "transcript_markdown", False),
        ("latest", ["LATEST.txt"], "source/LATEST.txt", "src_latest", "latest_pointer", False),
    ]

    for key, candidates, package_path, source_id, kind, required in source_specs:
        src = find_optional(source_dir, candidates)
        if src is None:
            if required:
                ctx.missing_sources.append({"kind": kind, "required": True, "candidates": candidates})
            continue
        found[key] = src
        records.append(copy_record(src, package_dir, package_path, source_id, kind, required))

    return records, found


def step_list(results: dict[str, Any]) -> list[dict[str, Any]]:
    steps = results.get("steps") or results.get("results") or []
    if not isinstance(steps, list):
        raise ValueError("results_latest.json must contain a list under 'steps' or 'results'")
    return [step for step in steps if isinstance(step, dict)]


def copy_evidence_file(ctx: BuildContext, package_dir: Path, src: Path, step: dict[str, Any], kind: str, label: str) -> dict[str, Any]:
    evidence_id = ctx.next_evidence_id(kind)
    dest_suffix = src.suffix.lower() or ".bin"
    package_path = f"evidence/{evidence_id}{dest_suffix}"
    dest = package_dir / package_path
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)

    return {
        "evidence_id": evidence_id,
        "kind": "region_screenshot" if kind == "region" else "step_auto_screenshot",
        "label": label,
        "step_n": step.get("step_n") or step.get("n"),
        "source_path": str(src),
        "package_path": package_path,
        "remote_path": None,
        "mime_type": mime_type(dest),
        "sha256": sha256_file(dest),
        "bytes": dest.stat().st_size,
        "created_at": file_time_iso(src),
        "capture": {
            "capture_type": "manual_region" if kind == "region" else "auto_fail_screenshot",
            "include_cursor": False,
            "monitor_index": None,
            "bounds": None,
        },
        "transcript_ref": None,
        "discarded": False,
        "privacy": {
            "contains_phi": "no",
            "deidentified": True,
            "redaction_state": "synthetic_sample",
        },
    }


def build_steps_and_evidence(ctx: BuildContext, package_dir: Path, results: dict[str, Any], found: dict[str, Path]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    steps_out: list[dict[str, Any]] = []
    evidence_out: list[dict[str, Any]] = []
    transcript_refs: list[dict[str, Any]] = []

    for index, step in enumerate(step_list(results)):
        step_n = step.get("step_n") or step.get("n") or index + 1
        evidence_ids: list[str] = []

        for rel_text in step.get("manual_screenshots", []) or []:
            src = ctx.source_dir / normalize_rel(str(rel_text))
            if not src.exists():
                ctx.missing_sources.append({"kind": "region_screenshot", "required": False, "path": str(src), "step_n": step_n})
                continue
            evidence = copy_evidence_file(ctx, package_dir, src, step, "region", f"Step {step_n} manual region capture")
            evidence_out.append(evidence)
            evidence_ids.append(evidence["evidence_id"])

        for rel_text in step.get("auto_screenshots", []) or []:
            src = ctx.source_dir / normalize_rel(str(rel_text))
            if not src.exists():
                ctx.missing_sources.append({"kind": "step_auto_screenshot", "required": False, "path": str(src), "step_n": step_n})
                continue
            evidence = copy_evidence_file(ctx, package_dir, src, step, "step_auto", f"Step {step_n} automatic failure screenshot")
            evidence_out.append(evidence)
            evidence_ids.append(evidence["evidence_id"])

        steps_out.append({
            "step_n": step_n,
            "kind": step.get("kind", "single"),
            "title": step.get("title", f"Step {step_n}"),
            "outcome": step.get("outcome"),
            "note": step.get("note"),
            "evidence_ids": evidence_ids,
            "source_result_index": index,
        })

    transcript_path = found.get("transcript")
    if transcript_path is not None:
        evidence_id = ctx.next_evidence_id("transcript_span")
        transcript_ref = {
            "transcript_ref_id": "tr_0001",
            "transcript_source": "source/transcript.md",
            "start_seconds": 12.4,
            "end_seconds": 18.9,
            "text_excerpt": "I captured a region, and the review dialog opened in the center.",
            "frame_ids": [eid for eid in ["ev_region_0001"] if any(ev["evidence_id"] == eid for ev in evidence_out)],
        }
        transcript_refs.append(transcript_ref)
        evidence_out.append({
            "evidence_id": evidence_id,
            "kind": "transcript_span",
            "label": "Transcript span describing Step 1 placement issue",
            "step_n": 1,
            "source_path": str(transcript_path),
            "package_path": "source/transcript.md",
            "remote_path": None,
            "mime_type": "text/markdown",
            "sha256": sha256_file(package_dir / "source/transcript.md"),
            "bytes": (package_dir / "source/transcript.md").stat().st_size,
            "created_at": file_time_iso(transcript_path),
            "capture": {
                "capture_type": "transcript_span",
                "include_cursor": None,
                "monitor_index": None,
                "bounds": None,
            },
            "transcript_ref": transcript_ref,
            "discarded": False,
            "privacy": {
                "contains_phi": "no",
                "deidentified": True,
                "redaction_state": "synthetic_sample",
            },
        })

    return steps_out, evidence_out, transcript_refs


def write_derived_files(package_dir: Path, manifest: dict[str, Any], transcript_refs: list[dict[str, Any]]) -> None:
    ai_input = {
        "schema": "pg.ai_extraction_input.v1",
        "schema_version": 1,
        "package_id": manifest["package_id"],
        "session_id": manifest["session_id"],
        "run_id": manifest["run_id"],
        "created_at": manifest["created_at"],
        "purpose": "Provider-neutral input for future AI issue extraction.",
        "steps": manifest["steps"],
        "evidence": manifest["evidence"],
        "transcript_refs": transcript_refs,
        "rules": [
            "Do not invent evidence IDs.",
            "Every issue must reference at least one evidence_id.",
            "Keep observed behavior separate from expected behavior.",
            "Use compliance_privacy only for real privacy concerns, not generic UI bugs.",
        ],
    }
    write_json(package_dir / "derived/ai_extraction_input_v1.json", ai_input)
    write_json(package_dir / "derived/sample_evidence_objects_v1.json", manifest["evidence"])

    lines = [
        f"# Package Summary: {manifest['package_id']}",
        "",
        f"Session: `{manifest['session_id']}`",
        f"Run: `{manifest['run_id']}`",
        f"State: `{manifest['package_state']}`",
        "",
        "## Steps",
        "",
    ]
    for step in manifest["steps"]:
        ids = ", ".join(step.get("evidence_ids", [])) or "none"
        lines.append(f"- Step {step['step_n']}: {step['outcome']} - {step['title']} (evidence: {ids})")
    lines.extend(["", "## Evidence", ""])
    for evidence in manifest["evidence"]:
        lines.append(f"- `{evidence['evidence_id']}` - {evidence['kind']} - {evidence['label']}")
    write_text(package_dir / "derived/package_summary.md", "\n".join(lines) + "\n")


def write_log(package_dir: Path, event: dict[str, Any]) -> None:
    log_path = package_dir / "logs/packaging_log.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")


def package_file_stats(package_dir: Path) -> tuple[int, int]:
    files = [p for p in package_dir.rglob("*") if p.is_file() and p.name != "session_package_manifest.json"]
    return len(files), sum(p.stat().st_size for p in files)


def build_package(ctx: BuildContext) -> Path:
    results_path = ctx.source_dir / "results_latest.json"
    results = read_json(results_path)
    session_id = str(results.get("session_id") or "session_unknown")
    run_id = str(results.get("run_id") or "run_unknown")
    package_id = f"pkg_sample_{session_id}"
    package_dir = ctx.output_root / f"session_package_{session_id}"

    if package_dir.exists():
        if not ctx.overwrite:
            raise FileExistsError(f"Package already exists: {package_dir}. Pass --overwrite to replace it.")
        safe_remove_tree(package_dir, ctx.output_root)

    package_dir.mkdir(parents=True, exist_ok=True)
    sources, found = build_sources(ctx, package_dir)
    steps, evidence, transcript_refs = build_steps_and_evidence(ctx, package_dir, results, found)

    manifest: dict[str, Any] = {
        "schema": PACKAGE_SCHEMA,
        "schema_version": PACKAGE_SCHEMA_VERSION,
        "package_id": package_id,
        "session_id": session_id,
        "run_id": run_id,
        "package_state": "local_ready",
        "created_at": ctx.created_at,
        "created_by": "codex-audit-mvp-starter-pack",
        "source_system": {
            "app_name": "Panda Gallery",
            "app_version": str(results.get("app_version") or "unknown"),
            "source_root": str(ctx.source_dir),
            "source_root_policy": "synthetic_sample_or_read_only_reference",
        },
        "tester_session": {
            "title": results.get("title"),
            "instructions_source": results.get("instructions_source"),
            "started_at": results.get("started_at"),
            "completed_at": results.get("completed_at"),
        },
        "sources": sources,
        "evidence": evidence,
        "steps": steps,
        "upload": None,
        "integrity": {},
        "missing_sources": ctx.missing_sources,
        "warnings": ctx.warnings,
    }

    write_derived_files(package_dir, manifest, transcript_refs)
    write_log(package_dir, {"event": "package_built", "created_at": ctx.created_at, "package_id": package_id})

    manifest_without_integrity = dict(manifest)
    manifest_without_integrity["integrity"] = {}
    file_count, total_bytes = package_file_stats(package_dir)
    manifest["integrity"] = {
        "hash_algorithm": "sha256",
        "manifest_without_integrity_sha256": sha256_json(manifest_without_integrity),
        "file_count": file_count,
        "total_bytes": total_bytes,
        "generated_by_version": GENERATED_BY_VERSION,
    }
    write_json(package_dir / "session_package_manifest.json", manifest)
    return package_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a local PG Audit MVP session package from sample or live-copied session outputs.")
    parser.add_argument("--source", required=True, type=Path, help="Source session folder containing results_latest.json and optional evidence files.")
    parser.add_argument("--out", required=True, type=Path, help="Output folder for generated session_package_<session_id>.")
    parser.add_argument("--overwrite", action="store_true", help="Replace the generated package folder if it already exists.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ctx = BuildContext(source_dir=args.source.resolve(), output_root=args.out.resolve(), overwrite=args.overwrite)
    package_dir = build_package(ctx)
    print(f"Built package: {package_dir}")
    print(f"Manifest: {package_dir / 'session_package_manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

