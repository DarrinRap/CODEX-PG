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
APP_VERSION = "0.9.0"
APP_ROOT = Path(__file__).resolve().parent
WEB_ROOT = APP_ROOT / "web"
DEFAULT_PACKAGE_ROOT = APP_ROOT / "CODEX handoff packages"
DEFAULT_SETTINGS_PATH = APP_ROOT / "CODEX settings" / "panda_collaborator_settings.local.json"
DEFAULT_HISTORY_ROOT = APP_ROOT / "CODEX project history"

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
USER_PROFILE_REQUIRED_FIELDS = (
    "display_name",
    "default_repo_path",
    "handoff_agent",
    "handoff_title",
    "codex_account",
    "claude_account",
    "git_author_name",
    "git_author_email",
)
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


def settings_path() -> Path:
    return Path(os.environ.get("PANDA_COLLABORATOR_SETTINGS_PATH", DEFAULT_SETTINGS_PATH)).resolve()


def history_root_path() -> Path:
    return Path(os.environ.get("PANDA_COLLABORATOR_HISTORY_ROOT", DEFAULT_HISTORY_ROOT)).resolve()


def default_settings() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "setup_completed": False,
        "active_user_id": "user1",
        "users": [
            {
                "id": "user1",
                "display_name": "User 1",
                "default_repo_path": r"C:\CODEX PG",
                "handoff_agent": "Codex",
                "handoff_title": "AI workstation handoff",
                "codex_account": "",
                "claude_account": "",
                "git_author_name": "",
                "git_author_email": "",
            },
            {
                "id": "user2",
                "display_name": "User 2",
                "default_repo_path": r"C:\CODEX PG",
                "handoff_agent": "Claude",
                "handoff_title": "AI workstation handoff",
                "codex_account": "",
                "claude_account": "",
                "git_author_name": "",
                "git_author_email": "",
            },
        ],
    }


def clean_setting_text(value: Any, fallback: str, max_length: int) -> str:
    cleaned = str(value if value is not None else "").replace("\0", "").strip()
    return (cleaned or fallback)[:max_length]


def normalize_settings(payload: dict[str, Any], *, strict: bool = True, mark_completed: bool = False) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise CollaboratorError("Settings request must be an object.")

    defaults = default_settings()
    incoming_users = payload.get("users", defaults["users"])
    if not isinstance(incoming_users, list):
        raise CollaboratorError("Settings users must be a list.")
    if strict and len(incoming_users) != 2:
        raise CollaboratorError("Settings must contain exactly two user profiles.")

    normalized_users: list[dict[str, str]] = []
    for index, default_user in enumerate(defaults["users"]):
        source = incoming_users[index] if index < len(incoming_users) and isinstance(incoming_users[index], dict) else {}
        display_name = clean_setting_text(source.get("display_name"), default_user["display_name"], 40)
        normalized_users.append(
            {
                "id": default_user["id"],
                "display_name": display_name,
                "default_repo_path": clean_setting_text(
                    source.get("default_repo_path"), default_user["default_repo_path"], 260
                ),
                "handoff_agent": clean_setting_text(source.get("handoff_agent"), display_name, 60),
                "handoff_title": clean_setting_text(
                    source.get("handoff_title"), default_user["handoff_title"], 90
                ),
                "codex_account": clean_setting_text(source.get("codex_account"), "", 120),
                "claude_account": clean_setting_text(source.get("claude_account"), "", 120),
                "git_author_name": clean_setting_text(source.get("git_author_name"), "", 80),
                "git_author_email": clean_setting_text(source.get("git_author_email"), "", 120),
            }
        )

    active_user_id = clean_setting_text(payload.get("active_user_id"), defaults["active_user_id"], 16)
    if active_user_id not in {"user1", "user2"}:
        active_user_id = defaults["active_user_id"]

    profiles_ready = all(all(user.get(field) for field in USER_PROFILE_REQUIRED_FIELDS) for user in normalized_users)
    setup_completed = bool(payload.get("setup_completed")) and profiles_ready
    if mark_completed:
        setup_completed = profiles_ready

    normalized = {
        "schema_version": 1,
        "setup_completed": setup_completed,
        "active_user_id": active_user_id,
        "users": normalized_users,
    }
    updated_at = payload.get("updated_at")
    if isinstance(updated_at, str) and updated_at.strip():
        normalized["updated_at"] = updated_at.strip()[:64]
    return normalized


def load_settings() -> dict[str, Any]:
    path = settings_path()
    if not path.exists():
        return default_settings()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise CollaboratorError(f"Could not read settings: {exc}") from exc
    return normalize_settings(data, strict=False)


def save_settings(payload: dict[str, Any]) -> dict[str, Any]:
    settings = normalize_settings(payload, strict=True, mark_completed=True)
    settings["updated_at"] = local_timestamp()
    path = settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        backup = path.with_name(f"{path.stem}.{utc_stamp()}.bak{path.suffix}")
        counter = 1
        while backup.exists():
            backup = path.with_name(f"{path.stem}.{utc_stamp()}.{counter}.bak{path.suffix}")
            counter += 1
        shutil.copy2(path, backup)
    temp_path = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temp_path.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
    os.replace(temp_path, path)
    return settings


def history_file(name: str) -> Path:
    root = history_root_path()
    root.mkdir(parents=True, exist_ok=True)
    return root / name


def read_jsonl(path: Path, limit: int = 100) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            rows.append(value)
    return rows[-limit:]


def append_jsonl(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    row = dict(payload)
    row.setdefault("id", f"{utc_stamp()}-{hashlib.sha1(json.dumps(row, sort_keys=True, default=str).encode('utf-8')).hexdigest()[:10]}")
    row.setdefault("created_at", local_timestamp())
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")
    return row


def backup_existing_file(path: Path) -> None:
    if not path.exists():
        return
    backup = path.with_name(f"{path.stem}.{utc_stamp()}.bak{path.suffix}")
    counter = 1
    while backup.exists():
        backup = path.with_name(f"{path.stem}.{utc_stamp()}.{counter}.bak{path.suffix}")
        counter += 1
    shutil.copy2(path, backup)


def control_state_path() -> Path:
    return history_file("control_state.local.json")


def load_control_state() -> dict[str, Any]:
    path = control_state_path()
    if not path.exists():
        return {
            "schema_version": 1,
            "paused": False,
            "pause_reason": "",
            "start_work_enabled": False,
            "last_started_at": "",
            "last_ended_at": "",
            "updated_at": "",
        }
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        data = {}
    if not isinstance(data, dict):
        data = {}
    return {
        "schema_version": 1,
        "paused": bool(data.get("paused", False)),
        "pause_reason": clean_setting_text(data.get("pause_reason"), "", 240),
        "start_work_enabled": bool(data.get("start_work_enabled", False)),
        "last_started_at": clean_setting_text(data.get("last_started_at"), "", 64),
        "last_ended_at": clean_setting_text(data.get("last_ended_at"), "", 64),
        "updated_at": clean_setting_text(data.get("updated_at"), "", 64),
    }


def save_control_state(state: dict[str, Any]) -> dict[str, Any]:
    normalized = {
        "schema_version": 1,
        "paused": bool(state.get("paused", False)),
        "pause_reason": clean_setting_text(state.get("pause_reason"), "", 240),
        "start_work_enabled": bool(state.get("start_work_enabled", False)),
        "last_started_at": clean_setting_text(state.get("last_started_at"), "", 64),
        "last_ended_at": clean_setting_text(state.get("last_ended_at"), "", 64),
        "updated_at": local_timestamp(),
    }
    path = control_state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    backup_existing_file(path)
    temp_path = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temp_path.write_text(json.dumps(normalized, indent=2) + "\n", encoding="utf-8")
    os.replace(temp_path, path)
    return normalized


def record_event(kind: str, title: str, detail: str = "", context: dict[str, Any] | None = None, severity: str = "info") -> dict[str, Any]:
    context = normalize_operator_context(context or {})
    event = {
        "kind": clean_setting_text(kind, "event", 40),
        "title": clean_setting_text(title, "PANDA event", 160),
        "detail": clean_setting_text(detail, "", 1200),
        "severity": clean_setting_text(severity, "info", 16),
        "operator_context": context,
    }
    return append_jsonl(history_file("timeline.jsonl"), event)


def create_message(payload: dict[str, Any]) -> dict[str, Any]:
    text = clean_setting_text(payload.get("text"), "", 2000)
    if not text:
        raise CollaboratorError("Message text is required.")
    context = normalize_operator_context(payload.get("operator_context", {}))
    message = append_jsonl(
        history_file("messages.jsonl"),
        {
            "kind": clean_setting_text(payload.get("kind"), "note", 32),
            "author": clean_setting_text(payload.get("author"), context.get("display_name") or "PANDA", 80),
            "text": text,
            "operator_context": context,
        },
    )
    record_event("message", f"Message from {message['author']}", text, context, "info")
    return message


def normalize_operator_context(value: Any, repo_root: str = "") -> dict[str, Any]:
    source = value if isinstance(value, dict) else {}

    user_id = clean_setting_text(source.get("user_id"), "", 16)
    if user_id not in {"user1", "user2"}:
        user_id = ""

    context = {
        "user_id": user_id,
        "display_name": clean_setting_text(source.get("display_name"), "", 80),
        "codex_account": clean_setting_text(source.get("codex_account"), "", 120),
        "claude_account": clean_setting_text(source.get("claude_account"), "", 120),
        "git_author_name": clean_setting_text(source.get("git_author_name"), "", 80),
        "git_author_email": clean_setting_text(source.get("git_author_email"), "", 120),
        "repo_path": clean_setting_text(source.get("repo_path"), repo_root, 260),
        "shared_git_working_tree": bool(source.get("shared_git_working_tree", True)),
        "credential_storage": "Account labels, usernames, and emails only. Passwords, tokens, API keys, and browser credentials are not stored.",
        "history_context_rule": "Continue from HANDOFF.md plus manifest.json so branch, HEAD, status, notes, and operator context are not lost.",
    }
    return context


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
    operator = manifest.get("operator_context", {})
    git_author = operator.get("git_author_name", "")
    git_email = operator.get("git_author_email", "")
    git_author_line = f"{git_author} <{git_email}>".strip() if git_author or git_email else "(not recorded)"
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
            "## Session / Account Context",
            "",
            f"- Active PANDA user: {operator.get('display_name') or '(not recorded)'}",
            f"- PANDA user slot: {operator.get('user_id') or '(not recorded)'}",
            f"- Codex account label: {operator.get('codex_account') or '(not recorded)'}",
            f"- Claude account label: {operator.get('claude_account') or '(not recorded)'}",
            f"- Git author identity: {git_author_line}",
            f"- Git working tree: `{operator.get('repo_path') or manifest['repo_root']}`",
            f"- Shared git working tree: {'yes' if operator.get('shared_git_working_tree', True) else 'no'}",
            f"- Credential storage: {operator.get('credential_storage') or 'No passwords, tokens, or API keys are stored.'}",
            "",
            "## History / Continuation Context",
            "",
            "- Continue from this `HANDOFF.md` and `manifest.json` before writing code.",
            "- Preserve the branch, HEAD, status snapshot, operator notes, and account context above.",
            "- If both users use the same repository path, they share the same git working tree and commit history.",
            "- Use the recorded Git author identity as context; PANDA does not switch Git credentials or browser logins.",
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


def create_handoff_package(
    path_text: str,
    title: str,
    agent: str = "",
    notes: str = "",
    operator_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
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
        "operator_context": normalize_operator_context(operator_context, str(repo)),
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

    plain_summary = summarize_handoff_plain(manifest)
    technical_summary = summarize_handoff_technical(manifest)
    manifest["plain_summary"] = plain_summary
    manifest["technical_summary"] = technical_summary
    write_text_no_overwrite(package_dir / "manifest.json", json.dumps(manifest, indent=2))
    write_text_no_overwrite(package_dir / "HANDOFF.md", handoff_markdown(manifest))
    write_text_no_overwrite(package_dir / "PLAIN_SUMMARY.md", plain_summary_markdown(plain_summary))
    write_text_no_overwrite(package_dir / "TECHNICAL_SUMMARY.md", technical_summary_markdown(technical_summary))
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


def latest_package_detail(path_text: str) -> dict[str, Any] | None:
    packages = list_packages(path_text).get("packages", [])
    if not packages:
        return None
    return read_package_detail(packages[0]["id"])


def summarize_handoff_plain(manifest: dict[str, Any]) -> dict[str, Any]:
    status = manifest.get("status_at_creation", {})
    counts = status.get("counts", {})
    copies = manifest.get("uncommitted_protection", {}).get("file_copies", {})
    copied = copies.get("copied", [])
    skipped = copies.get("skipped", [])
    patches = manifest.get("uncommitted_protection", {}).get("patches", [])
    operator = manifest.get("operator_context", {})
    notes = str(manifest.get("notes", "")).strip()

    achievements = [
        f"Protected committed work with branch {manifest.get('committed_protection', {}).get('branch', '(unknown)')}.",
        f"Saved {len(patches)} patch files and copied {len(copied)} changed/new files.",
    ]
    if notes:
        achievements.append("Captured operator notes for the next session.")

    concerns: list[str] = []
    if counts.get("conflicted", 0):
        concerns.append(f"{counts.get('conflicted')} conflicted file(s) need human review.")
    if skipped:
        concerns.append(f"{len(skipped)} changed path(s) were skipped during file copy protection.")
    if status.get("dirty"):
        concerns.append("The working tree had uncommitted work when the handoff was created.")
    if not concerns:
        concerns.append("No major handoff concerns were recorded.")

    next_steps = [
        "Read this plain-English summary first.",
        "Review the technical details before applying any patch or copied file.",
        "Run a fresh repository scan before making changes.",
    ]

    return {
        "title": manifest.get("title", "PANDA handoff"),
        "created_at": manifest.get("created_at", ""),
        "active_user": operator.get("display_name", ""),
        "major_events": [
            f"Created handoff for repo {manifest.get('repo_root', '(unknown repo)')}.",
            f"Recorded branch {manifest.get('branch_at_creation', '(unknown)')} at HEAD {manifest.get('short_head', '')}.",
        ],
        "achievements": achievements,
        "concerns": concerns,
        "next_steps": next_steps,
        "notes": notes or "(none)",
    }


def summarize_handoff_technical(manifest: dict[str, Any]) -> dict[str, Any]:
    protection = manifest.get("committed_protection", {})
    uncommitted = manifest.get("uncommitted_protection", {})
    copies = uncommitted.get("file_copies", {})
    return {
        "package_dir": manifest.get("package_dir", ""),
        "repo_root": manifest.get("repo_root", ""),
        "branch_at_creation": manifest.get("branch_at_creation", ""),
        "head": manifest.get("head", ""),
        "short_head": manifest.get("short_head", ""),
        "protection_branch": protection.get("branch", ""),
        "created_without_checkout": bool(protection.get("created_without_checkout")),
        "patch_count": len(uncommitted.get("patches", [])),
        "copied_count": len(copies.get("copied", [])),
        "skipped_count": len(copies.get("skipped", [])),
        "safety_receipt": manifest.get("safety_receipt", {}),
    }


def plain_summary_markdown(summary: dict[str, Any]) -> str:
    def bullets(items: list[str]) -> list[str]:
        return [f"- {item}" for item in items]

    return "\n".join(
        [
            f"# Plain-English Summary: {summary.get('title', 'PANDA handoff')}",
            "",
            f"Created: {summary.get('created_at', '')}",
            f"Active user: {summary.get('active_user') or '(not recorded)'}",
            "",
            "## Major Events",
            "",
            *bullets(summary.get("major_events", [])),
            "",
            "## Achievements",
            "",
            *bullets(summary.get("achievements", [])),
            "",
            "## Concerns",
            "",
            *bullets(summary.get("concerns", [])),
            "",
            "## Recommended Next Steps",
            "",
            *bullets(summary.get("next_steps", [])),
            "",
            "## Notes",
            "",
            str(summary.get("notes", "(none)")),
        ]
    )


def technical_summary_markdown(summary: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Technical Summary",
            "",
            f"Package: `{summary.get('package_dir', '')}`",
            f"Repository: `{summary.get('repo_root', '')}`",
            f"Branch at creation: `{summary.get('branch_at_creation', '')}`",
            f"HEAD: `{summary.get('head', '')}`",
            f"Protection branch: `{summary.get('protection_branch', '')}`",
            f"Created without checkout: {summary.get('created_without_checkout')}",
            f"Patch count: {summary.get('patch_count', 0)}",
            f"Copied files: {summary.get('copied_count', 0)}",
            f"Skipped files: {summary.get('skipped_count', 0)}",
            "",
            "## Safety Receipt",
            "",
            "```json",
            json.dumps(summary.get("safety_receipt", {}), indent=2),
            "```",
        ]
    )


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


def recent_messages(limit: int = 20) -> list[dict[str, Any]]:
    return read_jsonl(history_file("messages.jsonl"), limit)


def recent_timeline(limit: int = 30) -> list[dict[str, Any]]:
    return read_jsonl(history_file("timeline.jsonl"), limit)


def dashboard_for(path_text: str, operator_context: dict[str, Any] | None = None) -> dict[str, Any]:
    context = normalize_operator_context(operator_context or {}, path_text)
    state = load_control_state()
    repo: dict[str, Any] | None = None
    latest: dict[str, Any] | None = None
    warnings: list[str] = []
    blockers: list[str] = []

    if state["paused"]:
        blockers.append(f"Emergency Pause is active: {state['pause_reason'] or 'No reason recorded.'}")

    try:
        repo = repo_status(path_text)
    except CollaboratorError as exc:
        warnings.append(str(exc))

    if repo:
        if repo["dirty"]:
            warnings.append("Repository has uncommitted work. Create a safe handoff before switching away.")
        if repo["counts"].get("conflicted", 0):
            blockers.append("Repository has conflicted files that need manual review.")
        try:
            latest = latest_package_detail(repo["repo_root"])
        except CollaboratorError as exc:
            warnings.append(f"Latest handoff could not be read: {exc}")
    else:
        blockers.append("Repository scan has not passed.")

    if repo and latest is None:
        warnings.append("No handoff package found for this repository yet.")

    messages = recent_messages(12)
    timeline = recent_timeline(16)
    concern_count = sum(1 for item in messages + timeline if str(item.get("kind", "")).lower() == "concern")
    achievement_count = sum(1 for item in messages + timeline if str(item.get("kind", "")).lower() == "achievement")

    if blockers:
        next_action = "Stop and resolve the blocker before starting work."
    elif warnings:
        next_action = "Review the warning, then use Start Session before editing files."
    elif not state["start_work_enabled"]:
        next_action = "Press Start Session / Start Work to run the automated checklist."
    else:
        next_action = "Work may begin. Keep notes, then use End Session / Create Handoff when finished."

    latest_manifest = latest.get("manifest") if latest else None
    return {
        "ok": True,
        "version": APP_VERSION,
        "control_state": state,
        "operator_context": context,
        "repo": repo,
        "latest_handoff": {
            "id": latest.get("id"),
            "plain": summarize_handoff_plain(latest_manifest),
            "technical": summarize_handoff_technical(latest_manifest),
        } if latest and latest_manifest else None,
        "warnings": warnings,
        "blockers": blockers,
        "project_manager": {
            "active_user": context.get("display_name") or "(not recorded)",
            "repo_health": "Blocked" if blockers else "Needs review" if warnings else "Ready",
            "latest_achievements": [item.get("text") or item.get("title") for item in messages + timeline if str(item.get("kind", "")).lower() == "achievement"][-3:],
            "current_concerns": [item.get("text") or item.get("title") for item in messages + timeline if str(item.get("kind", "")).lower() == "concern"][-3:],
            "recommended_next_action": next_action,
            "collaborator_activity": {
                "latest_agent": latest_manifest.get("agent", "") if latest_manifest else "",
                "recent_messages": len(messages),
                "recent_concerns": concern_count,
                "recent_achievements": achievement_count,
            },
        },
        "messages": messages,
        "timeline": timeline,
    }


def start_session(payload: dict[str, Any]) -> dict[str, Any]:
    path_text = str(payload.get("path", ""))
    context = normalize_operator_context(payload.get("operator_context", {}), path_text)
    dashboard = dashboard_for(path_text, context)
    checklist = [
        {"label": "Active user profile recorded", "ok": bool(context.get("display_name"))},
        {"label": "Repository scan completed", "ok": dashboard.get("repo") is not None},
        {"label": "Latest handoff reviewed or absence noted", "ok": True},
        {"label": "Emergency Pause is not active", "ok": not dashboard["control_state"]["paused"]},
        {"label": "No conflicted files detected", "ok": not any("conflicted" in item.lower() for item in dashboard["blockers"])},
    ]
    passed = all(item["ok"] for item in checklist)
    state = dashboard["control_state"]
    state["start_work_enabled"] = passed
    state["last_started_at"] = local_timestamp()
    save_control_state(state)
    record_event("start-session", "Start session checklist ran", "Start Work enabled." if passed else "Start Work blocked.", context, "info" if passed else "warning")
    dashboard = dashboard_for(path_text, context)
    dashboard["checklist"] = checklist
    dashboard["start_work_enabled"] = passed
    return dashboard


def write_daily_report(context: dict[str, Any], handoff: dict[str, Any] | None = None) -> dict[str, Any]:
    root = history_root_path() / "daily_reports"
    root.mkdir(parents=True, exist_ok=True)
    day = dt.datetime.now().astimezone().strftime("%Y-%m-%d")
    day_dir = root / day
    day_dir.mkdir(parents=True, exist_ok=True)
    path = day_dir / f"{utc_stamp()}-daily-report.md"
    messages = recent_messages(50)
    timeline = recent_timeline(80)
    achievements = [item.get("text") or item.get("title", "") for item in messages + timeline if str(item.get("kind", "")).lower() == "achievement"]
    concerns = [item.get("text") or item.get("title", "") for item in messages + timeline if str(item.get("kind", "")).lower() == "concern"]
    content = "\n".join(
        [
            f"# PANDA Daily Report - {day}",
            "",
            f"Generated: {local_timestamp()}",
            f"Active user: {context.get('display_name') or '(not recorded)'}",
            "",
            "## Major Events",
            "",
            *[f"- {item.get('title', item.get('kind', 'Event'))}: {item.get('detail', '')}" for item in timeline[-12:]],
            "",
            "## Achievements",
            "",
            *(f"- {item}" for item in (achievements[-8:] or ["No achievements recorded yet."])),
            "",
            "## Concerns",
            "",
            *(f"- {item}" for item in (concerns[-8:] or ["No concerns recorded yet."])),
            "",
            "## Latest Handoff",
            "",
            f"- {handoff.get('title', 'No handoff created in this report.') if handoff else 'No handoff created in this report.'}",
        ]
    )
    write_text_no_overwrite(path, content)
    event = record_event("daily-report", "Daily report created", str(path), context, "info")
    return {"path": str(path), "event": event}


def end_session(payload: dict[str, Any]) -> dict[str, Any]:
    path_text = str(payload.get("path", ""))
    context = normalize_operator_context(payload.get("operator_context", {}), path_text)
    title = clean_setting_text(payload.get("title"), "PANDA end-session handoff", 90)
    notes = clean_setting_text(payload.get("notes"), "", 4000)
    agent = clean_setting_text(payload.get("agent"), context.get("display_name") or "PANDA", 80)
    manifest = create_handoff_package(path_text, title, agent, notes, context)
    state = load_control_state()
    state["start_work_enabled"] = False
    state["last_ended_at"] = local_timestamp()
    save_control_state(state)
    report = write_daily_report(context, manifest)
    record_event("handoff", f"Handoff created: {manifest['title']}", manifest["package_dir"], context, "info")
    return {"ok": True, "handoff": manifest, "daily_report": report, "control_state": load_control_state()}


def set_pause(payload: dict[str, Any], paused: bool) -> dict[str, Any]:
    context = normalize_operator_context(payload.get("operator_context", {}))
    state = load_control_state()
    state["paused"] = paused
    state["pause_reason"] = clean_setting_text(payload.get("reason"), "", 240) if paused else ""
    if paused:
        state["start_work_enabled"] = False
    state = save_control_state(state)
    record_event("pause" if paused else "pause-clear", "Emergency Pause activated" if paused else "Emergency Pause cleared", state["pause_reason"], context, "warning" if paused else "info")
    return {"ok": True, "control_state": state}


def search_history(query: str) -> dict[str, Any]:
    needle = query.strip().lower()
    results: list[dict[str, Any]] = []
    sources = [
        ("message", history_file("messages.jsonl")),
        ("timeline", history_file("timeline.jsonl")),
    ]
    for source, path in sources:
        for item in read_jsonl(path, 500):
            text = json.dumps(item, sort_keys=True).lower()
            if not needle or needle in text:
                item = dict(item)
                item["source"] = source
                results.append(item)
    reports_root = history_root_path() / "daily_reports"
    if reports_root.exists():
        for report in reports_root.glob("*/*.md"):
            text = report.read_text(encoding="utf-8", errors="replace")
            if not needle or needle in text.lower():
                results.append({"source": "daily-report", "path": str(report), "created_at": local_timestamp(), "text": text[:1200]})
    results.sort(key=lambda item: item.get("created_at", ""), reverse=True)
    return {"query": query, "results": results[:50]}


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
        if parsed.path == "/favicon.ico":
            return text_response(self, b"", "image/x-icon", HTTPStatus.NO_CONTENT)
        if parsed.path == "/api/health":
            return json_response(
                self,
                {
                    "ok": True,
                    "app": APP_TITLE,
                    "version": APP_VERSION,
                    "package_root": str(package_root_path()),
                    "settings_path": str(settings_path()),
                    "generated_at": local_timestamp(),
                },
            )
        if parsed.path == "/api/settings":
            try:
                return json_response(self, {"ok": True, "settings": load_settings()})
            except CollaboratorError as exc:
                return json_response(self, {"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)
        if parsed.path == "/api/packages":
            params = urllib.parse.parse_qs(parsed.query)
            repo = params.get("path", [""])[0] or None
            try:
                return json_response(self, list_packages(repo))
            except CollaboratorError as exc:
                return json_response(self, {"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)
        if parsed.path == "/api/control-center":
            params = urllib.parse.parse_qs(parsed.query)
            repo = params.get("path", [""])[0]
            context = {
                "user_id": params.get("user_id", [""])[0],
                "display_name": params.get("display_name", [""])[0],
                "codex_account": params.get("codex_account", [""])[0],
                "claude_account": params.get("claude_account", [""])[0],
                "git_author_name": params.get("git_author_name", [""])[0],
                "git_author_email": params.get("git_author_email", [""])[0],
                "repo_path": repo,
            }
            try:
                return json_response(self, dashboard_for(repo, context))
            except CollaboratorError as exc:
                return json_response(self, {"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)
        if parsed.path == "/api/messages":
            return json_response(self, {"ok": True, "messages": recent_messages(50)})
        if parsed.path == "/api/timeline":
            return json_response(self, {"ok": True, "timeline": recent_timeline(80)})
        if parsed.path == "/api/search":
            params = urllib.parse.parse_qs(parsed.query)
            query = params.get("q", [""])[0]
            return json_response(self, {"ok": True, **search_history(query)})
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
            if parsed.path == "/api/settings":
                return json_response(self, {"ok": True, "settings": save_settings(payload)})
            if parsed.path == "/api/repo/scan":
                return json_response(self, {"ok": True, "repo": repo_status(str(payload.get("path", "")))})
            if parsed.path == "/api/handoff/create":
                manifest = create_handoff_package(
                    str(payload.get("path", "")),
                    str(payload.get("title", "PANDA Collaborator handoff")),
                    str(payload.get("agent", "")),
                    str(payload.get("notes", "")),
                    payload.get("operator_context", {}),
                )
                return json_response(self, {"ok": True, "handoff": manifest})
            if parsed.path == "/api/session/start":
                return json_response(self, {"ok": True, "session": start_session(payload)})
            if parsed.path == "/api/session/end":
                return json_response(self, end_session(payload))
            if parsed.path == "/api/message":
                return json_response(self, {"ok": True, "message": create_message(payload)})
            if parsed.path == "/api/pause":
                return json_response(self, set_pause(payload, True))
            if parsed.path == "/api/pause/clear":
                return json_response(self, set_pause(payload, False))
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
