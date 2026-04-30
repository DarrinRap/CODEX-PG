#!/usr/bin/env python3
"""
PANDA Collaborator - Windows shared AI coding workstation handoff manager.

Design contract:
- committed work is protected by branch refs;
- uncommitted work is protected by patch files plus file copies;
- destructive git commands are not available through this app.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import urllib.parse
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


APP_TITLE = "PANDA Collaborator"
APP_VERSION = "0.4.1"
APP_ROOT = Path(__file__).resolve().parent
WEB_ROOT = APP_ROOT / "web"
DEFAULT_PACKAGE_ROOT = APP_ROOT / "CODEX handoff packages"

FORBIDDEN_GIT_COMMANDS = [
    "git reset --hard",
    "git clean -fd",
    "git clean -xdf",
    "git push --force",
    "git push -f",
    "git checkout .",
    "git restore .",
    "git branch -D",
    "git branch -d",
    "git push origin --delete",
]

DANGEROUS_GIT_VERBS = {"stash", "merge", "rebase", "checkout", "restore", "clean"}
COPY_EXCLUDE_PREFIXES = {
    ".git",
    ".panda-collaborator",
    "CODEX PANDA Collaborator/CODEX handoff packages",
    "CODEX PANDA Collaborator\\CODEX handoff packages",
}


class CollaboratorError(Exception):
    """User-facing application error."""


class SafetyError(CollaboratorError):
    """Raised when an operation violates the safety contract."""


@dataclass(frozen=True)
class CommandResult:
    args: list[str]
    cwd: str
    returncode: int
    stdout: str
    stderr: str


def utc_stamp() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def local_timestamp() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def slugify(value: str, fallback: str = "handoff") -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip()).strip("-._")
    return cleaned[:64] or fallback


def package_root_path() -> Path:
    return Path(os.environ.get("PANDA_COLLABORATOR_PACKAGE_ROOT", DEFAULT_PACKAGE_ROOT)).resolve()


def run_command(args: list[str], cwd: Path | None = None, timeout: int = 30) -> CommandResult:
    try:
        completed = subprocess.run(
            args,
            cwd=str(cwd) if cwd else None,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError as exc:
        raise CollaboratorError(f"Required command not found: {args[0]}") from exc
    except subprocess.TimeoutExpired as exc:
        raise CollaboratorError(f"Command timed out: {' '.join(args)}") from exc
    return CommandResult(
        args=args,
        cwd=str(cwd) if cwd else os.getcwd(),
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def assert_git_args_safe(args: list[str]) -> None:
    lowered = [part.lower() for part in args]
    if not lowered:
        raise SafetyError("Empty git command rejected.")

    verb = lowered[0]
    if verb in DANGEROUS_GIT_VERBS:
        raise SafetyError(f"Rejected dangerous git verb: git {verb}")

    if verb == "reset" and "--hard" in lowered:
        raise SafetyError("Rejected forbidden command: git reset --hard")

    if verb == "push" and ("--force" in lowered or "-f" in lowered):
        raise SafetyError("Rejected forbidden command: git push --force")

    if verb == "push" and "--delete" in lowered:
        raise SafetyError("Rejected forbidden command: git push origin --delete")

    if verb == "branch" and ("-d" in lowered or "-D".lower() in lowered):
        raise SafetyError("Rejected forbidden command: git branch -d/-D")

    joined = " ".join(lowered)
    for forbidden in FORBIDDEN_GIT_COMMANDS:
        if joined == forbidden.removeprefix("git ").lower():
            raise SafetyError(f"Rejected forbidden command: {forbidden}")


def safe_git(repo: Path, args: list[str], timeout: int = 30, allow_failure: bool = False) -> CommandResult:
    assert_git_args_safe(args)
    result = run_command(["git", *args], cwd=repo, timeout=timeout)
    if result.returncode != 0 and not allow_failure:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        raise CollaboratorError(f"git {' '.join(args)} failed: {detail}")
    return result


def resolve_git_root(path_text: str) -> Path:
    if not path_text:
        raise CollaboratorError("Repository path is required.")
    candidate = Path(path_text).expanduser().resolve()
    if not candidate.exists():
        raise CollaboratorError(f"Path does not exist: {candidate}")
    result = run_command(["git", "rev-parse", "--show-toplevel"], cwd=candidate)
    if result.returncode != 0:
        raise CollaboratorError(f"Not a git repository: {candidate}")
    root = Path(result.stdout.strip()).resolve()
    if not root.exists():
        raise CollaboratorError(f"Git root does not exist: {root}")
    return root


def parse_porcelain(status_text: str) -> dict[str, Any]:
    files: list[dict[str, str]] = []
    counts = {"staged": 0, "unstaged": 0, "untracked": 0, "deleted": 0, "conflicted": 0}

    for raw in status_text.splitlines():
        if not raw:
            continue
        code = raw[:2]
        path = raw[3:] if len(raw) > 3 else ""
        entry = {"code": code, "path": path}
        files.append(entry)
        if code == "??":
            counts["untracked"] += 1
            continue
        x, y = code[0], code[1]
        if x != " ":
            counts["staged"] += 1
        if y != " ":
            counts["unstaged"] += 1
        if "D" in code:
            counts["deleted"] += 1
        if "U" in code or code in {"AA", "DD"}:
            counts["conflicted"] += 1

    return {"counts": counts, "files": files}


def repo_status(path_text: str) -> dict[str, Any]:
    root = resolve_git_root(path_text)
    branch = safe_git(root, ["branch", "--show-current"]).stdout.strip() or "(detached)"
    head = safe_git(root, ["rev-parse", "HEAD"]).stdout.strip()
    short_head = safe_git(root, ["rev-parse", "--short", "HEAD"]).stdout.strip()
    porcelain = safe_git(root, ["status", "--porcelain=v1", "-uall"]).stdout
    branch_status = safe_git(root, ["status", "--short", "--branch"]).stdout.strip()
    parsed = parse_porcelain(porcelain)
    dirty = any(value > 0 for value in parsed["counts"].values())

    return {
        "app": APP_TITLE,
        "version": APP_VERSION,
        "repo_root": str(root),
        "branch": branch,
        "head": head,
        "short_head": short_head,
        "dirty": dirty,
        "status_short": branch_status,
        "counts": parsed["counts"],
        "files": parsed["files"],
        "safety": {
            "committed_protection": "branch ref",
            "uncommitted_protection": "binary patches plus file copies",
            "stash_used": False,
            "forbidden_git_commands": FORBIDDEN_GIT_COMMANDS,
        },
        "generated_at": local_timestamp(),
    }


def safe_rel_path(repo_root: Path, rel_text: str) -> Path | None:
    if not rel_text or "\0" in rel_text:
        return None
    normalized_text = rel_text.replace("\\", "/")
    if any(
        normalized_text == prefix.replace("\\", "/")
        or normalized_text.startswith(prefix.replace("\\", "/").rstrip("/") + "/")
        for prefix in COPY_EXCLUDE_PREFIXES
    ):
        return None
    rel = Path(normalized_text)
    if rel.is_absolute() or ".." in rel.parts:
        return None
    resolved = (repo_root / rel).resolve()
    try:
        resolved.relative_to(repo_root)
    except ValueError:
        return None
    return rel


def git_lines(repo: Path, args: list[str]) -> list[str]:
    text = safe_git(repo, args).stdout
    return [line.strip() for line in text.splitlines() if line.strip()]


def changed_paths_for_copies(repo: Path) -> list[str]:
    paths: set[str] = set()
    for args in (
        ["diff", "--name-only", "--diff-filter=ACMRT"],
        ["diff", "--cached", "--name-only", "--diff-filter=ACMRT"],
        ["ls-files", "--others", "--exclude-standard"],
    ):
        paths.update(git_lines(repo, args))
    return sorted(paths, key=str.lower)


def ensure_unique_dir(base: Path) -> Path:
    candidate = base
    suffix = 2
    while candidate.exists():
        candidate = base.with_name(f"{base.name}-{suffix}")
        suffix += 1
    candidate.mkdir(parents=True, exist_ok=False)
    return candidate


def ensure_unique_branch(repo: Path, desired: str) -> str:
    branch = desired
    suffix = 2
    while True:
        check = safe_git(repo, ["show-ref", "--verify", f"refs/heads/{branch}"], allow_failure=True)
        if check.returncode != 0:
            return branch
        branch = f"{desired}-{suffix}"
        suffix += 1


def create_protection_branch(repo: Path, title: str) -> str:
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    branch = ensure_unique_branch(repo, f"panda-collab/handoff-{stamp}-{slugify(title)}")
    head = safe_git(repo, ["rev-parse", "HEAD"]).stdout.strip()
    safe_git(repo, ["branch", branch, head])
    return branch


def write_text_no_overwrite(path: Path, content: str) -> None:
    if path.exists():
        raise SafetyError(f"Refusing to overwrite existing file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def write_bytes_no_overwrite(path: Path, content: bytes) -> None:
    if path.exists():
        raise SafetyError(f"Refusing to overwrite existing file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def write_patch(repo: Path, package_dir: Path, filename: str, args: list[str]) -> dict[str, Any]:
    result = safe_git(repo, args)
    data = result.stdout.encode("utf-8", errors="replace")
    patch_path = package_dir / "patches" / filename
    write_bytes_no_overwrite(patch_path, data)
    return {"path": str(patch_path), "bytes": len(data), "empty": len(data) == 0}


def copy_changed_files(repo: Path, package_dir: Path, rel_paths: list[str]) -> dict[str, Any]:
    copied: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []
    copy_root = package_dir / "file_copies"
    copy_root.mkdir(parents=True, exist_ok=False)

    for rel_text in rel_paths:
        safe_rel = safe_rel_path(repo, rel_text)
        if safe_rel is None:
            skipped.append({"path": rel_text, "reason": "unsafe or excluded path"})
            continue
        src = (repo / safe_rel).resolve()
        if not src.exists():
            skipped.append({"path": rel_text, "reason": "source missing or deleted"})
            continue
        if not src.is_file():
            skipped.append({"path": rel_text, "reason": "not a file"})
            continue
        dst = (copy_root / safe_rel).resolve()
        try:
            dst.relative_to(copy_root.resolve())
        except ValueError:
            skipped.append({"path": rel_text, "reason": "copy target escaped package root"})
            continue
        if dst.exists():
            raise SafetyError(f"Refusing to overwrite copied file: {dst}")
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied.append({"repo_path": rel_text, "copy_path": str(dst), "bytes": dst.stat().st_size})

    return {"copied": copied, "skipped": skipped}


def handoff_markdown(manifest: dict[str, Any]) -> str:
    copied = manifest["uncommitted_protection"]["file_copies"]["copied"]
    skipped = manifest["uncommitted_protection"]["file_copies"]["skipped"]
    patches = manifest["uncommitted_protection"]["patches"]
    return "\n".join(
        [
            f"# {manifest['title']}",
            "",
            f"Created: {manifest['created_at']}",
            f"Repository: `{manifest['repo_root']}`",
            f"Branch at creation: `{manifest['branch_at_creation']}`",
            f"HEAD: `{manifest['head']}`",
            f"Protection branch: `{manifest['committed_protection']['branch']}`",
            "",
            "## Safety Contract",
            "",
            "- Committed work is protected by the protection branch above.",
            "- Uncommitted work is protected by patch files and file copies in this package.",
            "- The working tree was not reset, cleaned, stashed, merged, rebased, checked out, or restored.",
            "- The protection branch was created without switching the user's current branch.",
            "",
            "## Patch Files",
            "",
            *[f"- `{patch['path']}` ({patch['bytes']} bytes)" for patch in patches],
            "",
            "## File Copies",
            "",
            f"- Copied files: {len(copied)}",
            f"- Skipped files: {len(skipped)}",
            "",
            "## Operator Notes",
            "",
            manifest.get("notes", "").strip() or "(none)",
            "",
            "## Restore Guidance",
            "",
            "Inspect patches and file copies before applying anything. Do not apply patches over unsaved work.",
            "Use `git apply --check` before any manual patch application.",
        ]
    )


def create_handoff_package(path_text: str, title: str, agent: str = "", notes: str = "") -> dict[str, Any]:
    status = repo_status(path_text)
    repo = Path(status["repo_root"])
    package_root = package_root_path()
    package_base = package_root / slugify(repo.name, "repo") / f"{utc_stamp()}-{slugify(title)}"
    package_dir = ensure_unique_dir(package_base)

    protection_branch = create_protection_branch(repo, title)
    patches = [
        write_patch(repo, package_dir, "unstaged-working-tree.patch", ["diff", "--binary"]),
        write_patch(repo, package_dir, "staged-index.patch", ["diff", "--cached", "--binary"]),
    ]
    rel_paths = changed_paths_for_copies(repo)
    copies = copy_changed_files(repo, package_dir, rel_paths)

    manifest = {
        "schema_version": 1,
        "app": APP_TITLE,
        "version": APP_VERSION,
        "title": title.strip() or "PANDA Collaborator handoff",
        "agent": agent.strip(),
        "notes": notes,
        "created_at": local_timestamp(),
        "package_dir": str(package_dir),
        "repo_root": str(repo),
        "branch_at_creation": status["branch"],
        "head": status["head"],
        "short_head": status["short_head"],
        "status_at_creation": status,
        "committed_protection": {
            "type": "git branch ref",
            "branch": protection_branch,
            "created_without_checkout": True,
        },
        "uncommitted_protection": {
            "type": "binary patches plus file copies",
            "patches": patches,
            "file_copies": copies,
            "changed_paths_considered": rel_paths,
        },
        "forbidden_git_commands": FORBIDDEN_GIT_COMMANDS,
        "stash_used": False,
        "safety_receipt": {
            "branch_created_without_checkout": True,
            "working_tree_destructive_commands_used": [],
            "stash_used": False,
            "patches_written_before_file_copies": True,
            "file_copies_overwrite_existing_files": False,
            "restore_or_apply_performed": False,
            "operator_must_review_before_restore": True,
        },
    }

    write_text_no_overwrite(package_dir / "manifest.json", json.dumps(manifest, indent=2))
    write_text_no_overwrite(package_dir / "HANDOFF.md", handoff_markdown(manifest))
    return manifest


def package_id_for_manifest(package_root: Path, manifest_path: Path) -> str:
    return manifest_path.parent.resolve().relative_to(package_root).as_posix()


def resolve_package_manifest(package_id: str) -> Path:
    if not package_id or "\0" in package_id:
        raise CollaboratorError("Package id is required.")
    normalized = package_id.replace("\\", "/").strip("/")
    rel = Path(normalized)
    if rel.is_absolute() or ".." in rel.parts:
        raise SafetyError("Package id must stay inside the package root.")
    manifest = package_root_path() / rel
    if manifest.name != "manifest.json":
        manifest = manifest / "manifest.json"
    manifest = manifest.resolve()
    root = package_root_path()
    try:
        manifest.relative_to(root)
    except ValueError as exc:
        raise SafetyError("Package id escapes the package root.") from exc
    if not manifest.exists() or not manifest.is_file():
        raise CollaboratorError("Package manifest not found.")
    return manifest


def read_package_detail(package_id: str) -> dict[str, Any]:
    manifest_path = resolve_package_manifest(package_id)
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CollaboratorError("Package manifest is not valid JSON.") from exc

    package_dir = manifest_path.parent
    handoff_path = package_dir / "HANDOFF.md"
    handoff_preview = ""
    if handoff_path.exists() and handoff_path.is_file():
        handoff_preview = handoff_path.read_text(encoding="utf-8", errors="replace")[:12000]

    repo_root = data.get("repo_root", "")
    branch = data.get("committed_protection", {}).get("branch", "")
    branch_exists = None
    if repo_root and branch and Path(repo_root).exists():
        branch_check = safe_git(Path(repo_root), ["show-ref", "--verify", f"refs/heads/{branch}"], allow_failure=True)
        branch_exists = branch_check.returncode == 0

    patches = data.get("uncommitted_protection", {}).get("patches", [])
    copies = data.get("uncommitted_protection", {}).get("file_copies", {})
    return {
        "id": package_id_for_manifest(package_root_path(), manifest_path),
        "manifest": data,
        "handoff_preview": handoff_preview,
        "branch_exists": branch_exists,
        "counts": {
            "patches": len(patches),
            "patch_bytes": sum(int(patch.get("bytes", 0) or 0) for patch in patches),
            "copied": len(copies.get("copied", [])),
            "skipped": len(copies.get("skipped", [])),
        },
    }


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_package_child(package_dir: Path, path_text: str) -> Path | None:
    if not path_text:
        return None
    path = Path(path_text).resolve()
    try:
        path.relative_to(package_dir.resolve())
    except ValueError:
        return None
    return path


def git_apply_check(repo: Path, patch_path: Path) -> dict[str, Any]:
    result = run_command(["git", "apply", "--check", "--binary", str(patch_path)], cwd=repo, timeout=30)
    return {
        "patch_path": str(patch_path),
        "ok": result.returncode == 0,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "returncode": result.returncode,
    }


def preview_restore_plan(package_id: str, path_text: str) -> dict[str, Any]:
    target = resolve_git_root(path_text)
    manifest_path = resolve_package_manifest(package_id)
    package_dir = manifest_path.parent
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    target_status = repo_status(str(target))

    recorded_repo = data.get("repo_root", "")
    repo_matches = bool(recorded_repo) and str(Path(recorded_repo).resolve()).lower() == str(target).lower()
    branch = data.get("committed_protection", {}).get("branch", "")
    branch_exists = False
    if branch:
        branch_check = safe_git(target, ["show-ref", "--verify", f"refs/heads/{branch}"], allow_failure=True)
        branch_exists = branch_check.returncode == 0

    blockers: list[str] = []
    warnings: list[str] = []
    if target_status["dirty"]:
        blockers.append("Target repository has uncommitted work; automated restore must stay unavailable.")
    if not repo_matches:
        warnings.append("Target repository does not match the repository recorded in the package manifest.")
    if branch and not branch_exists:
        warnings.append("Protection branch recorded in the package is not present in the target repository.")

    patch_checks: list[dict[str, Any]] = []
    for patch in data.get("uncommitted_protection", {}).get("patches", []):
        patch_path = resolve_package_child(package_dir, str(patch.get("path", "")))
        if patch_path is None or not patch_path.exists():
            patch_checks.append({"patch_path": str(patch.get("path", "")), "ok": False, "stderr": "Patch file missing or outside package."})
            blockers.append("One or more patch files are missing or outside the package.")
            continue
        if int(patch.get("bytes", 0) or 0) == 0:
            patch_checks.append({"patch_path": str(patch_path), "ok": True, "empty": True, "stdout": "", "stderr": ""})
            continue
        check = git_apply_check(target, patch_path)
        patch_checks.append(check)
        if not check["ok"]:
            blockers.append(f"Patch check failed: {Path(patch_path).name}")

    copy_checks: list[dict[str, Any]] = []
    copied = data.get("uncommitted_protection", {}).get("file_copies", {}).get("copied", [])
    for item in copied:
        repo_path = str(item.get("repo_path", ""))
        safe_rel = safe_rel_path(target, repo_path)
        copy_path = resolve_package_child(package_dir, str(item.get("copy_path", "")))
        if safe_rel is None:
            copy_checks.append({"repo_path": repo_path, "status": "blocked", "reason": "Unsafe target path."})
            blockers.append("One or more copied files have unsafe target paths.")
            continue
        if copy_path is None or not copy_path.exists() or not copy_path.is_file():
            copy_checks.append({"repo_path": repo_path, "status": "missing-copy", "reason": "Copied file missing or outside package."})
            blockers.append("One or more copied files are missing or outside the package.")
            continue
        target_path = (target / safe_rel).resolve()
        copy_hash = file_sha256(copy_path)
        if not target_path.exists():
            copy_checks.append(
                {
                    "repo_path": repo_path,
                    "target_path": str(target_path),
                    "copy_path": str(copy_path),
                    "status": "target-missing",
                    "copy_sha256": copy_hash,
                    "copy_bytes": copy_path.stat().st_size,
                }
            )
            continue
        if not target_path.is_file():
            copy_checks.append({"repo_path": repo_path, "target_path": str(target_path), "status": "target-not-file"})
            blockers.append("One or more restore targets are not files.")
            continue
        target_hash = file_sha256(target_path)
        copy_checks.append(
            {
                "repo_path": repo_path,
                "target_path": str(target_path),
                "copy_path": str(copy_path),
                "status": "identical" if target_hash == copy_hash else "different",
                "copy_sha256": copy_hash,
                "target_sha256": target_hash,
                "copy_bytes": copy_path.stat().st_size,
                "target_bytes": target_path.stat().st_size,
            }
        )

    return {
        "package_id": package_id_for_manifest(package_root_path(), manifest_path),
        "package_title": data.get("title", ""),
        "target_repo": str(target),
        "repo_matches_manifest": repo_matches,
        "target_status": target_status,
        "protection_branch": branch,
        "protection_branch_exists": branch_exists,
        "patch_checks": patch_checks,
        "copy_checks": copy_checks,
        "blockers": sorted(set(blockers)),
        "warnings": sorted(set(warnings)),
        "automated_restore_available": False,
        "allowed_next_actions": [
            "Review HANDOFF.md",
            "Review patch checks",
            "Review copied file comparisons",
            "Use manual restore steps only after creating a fresh backup",
        ],
        "generated_at": local_timestamp(),
    }


def list_packages(path_text: str | None = None) -> dict[str, Any]:
    package_root = package_root_path()
    packages: list[dict[str, Any]] = []
    if package_root.exists():
        for manifest_path in package_root.glob("*/*/manifest.json"):
            try:
                data = json.loads(manifest_path.read_text(encoding="utf-8"))
            except Exception:
                continue
            if path_text and str(Path(data.get("repo_root", "")).resolve()).lower() != str(resolve_git_root(path_text)).lower():
                continue
            packages.append(
                {
                    "id": package_id_for_manifest(package_root, manifest_path),
                    "title": data.get("title", ""),
                    "created_at": data.get("created_at", ""),
                    "package_dir": data.get("package_dir", str(manifest_path.parent)),
                    "repo_root": data.get("repo_root", ""),
                    "branch": data.get("committed_protection", {}).get("branch", ""),
                    "copied": len(data.get("uncommitted_protection", {}).get("file_copies", {}).get("copied", [])),
                    "skipped": len(data.get("uncommitted_protection", {}).get("file_copies", {}).get("skipped", [])),
                    "patches": len(data.get("uncommitted_protection", {}).get("patches", [])),
                }
            )
    packages.sort(key=lambda item: item.get("created_at", ""), reverse=True)
    return {"package_root": str(package_root), "packages": packages[:50]}


def json_response(handler: BaseHTTPRequestHandler, payload: Any, status: int = 200) -> None:
    data = json.dumps(payload, indent=2).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


def text_response(handler: BaseHTTPRequestHandler, payload: bytes, content_type: str, status: int = 200) -> None:
    handler.send_response(status)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Content-Length", str(len(payload)))
    handler.end_headers()
    handler.wfile.write(payload)


class PandaHandler(BaseHTTPRequestHandler):
    server_version = f"PANDA Collaborator/{APP_VERSION}"

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003 - BaseHTTPRequestHandler API
        sys.stderr.write("[%s] %s\n" % (self.log_date_time_string(), format % args))

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/health":
            return json_response(
                self,
                {
                    "ok": True,
                    "app": APP_TITLE,
                    "version": APP_VERSION,
                    "package_root": str(package_root_path()),
                    "generated_at": local_timestamp(),
                },
            )
        if parsed.path == "/api/packages":
            params = urllib.parse.parse_qs(parsed.query)
            repo = params.get("path", [""])[0] or None
            try:
                return json_response(self, list_packages(repo))
            except CollaboratorError as exc:
                return json_response(self, {"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)
        if parsed.path == "/api/package":
            params = urllib.parse.parse_qs(parsed.query)
            package_id = params.get("id", [""])[0]
            try:
                return json_response(self, {"ok": True, "package": read_package_detail(package_id)})
            except CollaboratorError as exc:
                return json_response(self, {"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)
        if parsed.path in {"/", "/index.html"}:
            return self.serve_file(WEB_ROOT / "index.html", "text/html; charset=utf-8")
        return json_response(self, {"ok": False, "error": "Not found"}, HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        try:
            payload = self.read_json()
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path == "/api/repo/scan":
                return json_response(self, {"ok": True, "repo": repo_status(str(payload.get("path", "")))})
            if parsed.path == "/api/handoff/create":
                manifest = create_handoff_package(
                    str(payload.get("path", "")),
                    str(payload.get("title", "PANDA Collaborator handoff")),
                    str(payload.get("agent", "")),
                    str(payload.get("notes", "")),
                )
                return json_response(self, {"ok": True, "handoff": manifest})
            if parsed.path == "/api/restore/preview":
                plan = preview_restore_plan(str(payload.get("package_id", "")), str(payload.get("path", "")))
                return json_response(self, {"ok": True, "plan": plan})
            return json_response(self, {"ok": False, "error": "Not found"}, HTTPStatus.NOT_FOUND)
        except CollaboratorError as exc:
            return json_response(self, {"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)
        except Exception as exc:  # pragma: no cover - guardrail for local UI
            return json_response(self, {"ok": False, "error": f"Unexpected error: {exc}"}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def serve_file(self, path: Path, content_type: str) -> None:
        if not path.exists() or not path.is_file():
            return json_response(self, {"ok": False, "error": "Asset missing"}, HTTPStatus.NOT_FOUND)
        text_response(self, path.read_bytes(), content_type)

    def read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length > 1_000_000:
            raise CollaboratorError("Request body too large.")
        raw = self.rfile.read(length)
        if not raw:
            return {}
        try:
            data = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise CollaboratorError("Invalid JSON request.") from exc
        if not isinstance(data, dict):
            raise CollaboratorError("JSON request must be an object.")
        return data


def serve(host: str, port: int) -> None:
    server = ThreadingHTTPServer((host, port), PandaHandler)
    print(f"{APP_TITLE} listening at http://{host}:{port}/")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping PANDA Collaborator.")
    finally:
        server.shutdown()
        server.server_close()


def cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=f"{APP_TITLE} local safety handoff manager")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8788)
    parser.add_argument("--scan")
    parser.add_argument("--create-handoff")
    parser.add_argument("--title", default="PANDA Collaborator handoff")
    parser.add_argument("--agent", default="")
    parser.add_argument("--notes", default="")
    args = parser.parse_args(argv)

    try:
        if args.scan:
            print(json.dumps(repo_status(args.scan), indent=2))
            return 0
        if args.create_handoff:
            print(json.dumps(create_handoff_package(args.create_handoff, args.title, args.agent, args.notes), indent=2))
            return 0
        serve(args.host, args.port)
        return 0
    except CollaboratorError as exc:
        print(f"Error: {html.escape(str(exc))}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(cli())
