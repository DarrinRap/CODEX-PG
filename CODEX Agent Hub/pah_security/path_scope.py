"""Path scope checks for PAH protected writes."""

from __future__ import annotations

from pathlib import Path

from pah_mailbox.paths import CC_MAILBOX_ROOT, HUB_ROOT, MAILBOX_ROOT, PROJECT_ROOT


CODEX_WORKSPACE_ROOT = PROJECT_ROOT
PANDA_GALLERY_ROOT = Path("C:/panda-gallery")


def is_inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def classify_path(path: Path) -> str:
    resolved = path.resolve()
    if is_inside(resolved, HUB_ROOT):
        return "pah_app"
    if is_inside(resolved, MAILBOX_ROOT):
        return "mailbox"
    if is_inside(resolved, CC_MAILBOX_ROOT):
        return "panda_gallery_cc_mailbox_approved"
    if is_inside(resolved, PANDA_GALLERY_ROOT):
        return "panda_gallery_requires_darrin"
    if is_inside(resolved, CODEX_WORKSPACE_ROOT):
        return "codex_workspace"
    return "outside_known_scope"
