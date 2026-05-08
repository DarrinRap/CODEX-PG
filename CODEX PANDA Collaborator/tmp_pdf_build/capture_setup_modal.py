"""Setup-modal-fix screenshot — capture the live SETUP USERS modal at 1366x768
matching the locked pc_v2_setup_users_modal.html. Backs up settings, opens the
modal, screenshots, restores."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

PC_ROOT = Path(r"C:\CODEX PG\CODEX PANDA Collaborator")
SETTINGS = PC_ROOT / "CODEX settings" / "panda_collaborator_settings.local.json"
BACKUP = PC_ROOT / "tmp_pdf_build" / "settings_backup_setup_modal.json"
OUT = PC_ROOT / "tmp_pdf_build"
SCRIPT = PC_ROOT / "panda_collaborator.py"
URL = "http://127.0.0.1:8788/"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    settings_existed = SETTINGS.exists()
    if settings_existed:
        shutil.copy2(SETTINGS, BACKUP)
        print(f"[capture] backup: {BACKUP}")
    else:
        print("[capture] no prior settings.local.json — starting from default")

    proc = None
    try:
        proc = subprocess.Popen(
            [sys.executable, str(SCRIPT), "--port", "8788"],
            cwd=str(PC_ROOT),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(4)
        print(f"[capture] server pid={proc.pid}")

        with sync_playwright() as p:
            browser = p.chromium.launch()
            ctx = browser.new_context(viewport={"width": 1366, "height": 768})
            page = ctx.new_page()
            page.goto(URL)
            page.wait_for_load_state("networkidle")
            time.sleep(1.0)

            page.click("#openSetupBtn")
            time.sleep(0.6)
            page.wait_for_selector("#setupOverlay:not(.hidden)", timeout=3000)
            time.sleep(0.4)

            out_path = OUT / "PC_LIVE_SETUP_MODAL_FIX_AFTER.png"
            page.screenshot(path=str(out_path), full_page=False)
            print(f"[capture] saved {out_path.name}")

            ctx.close()
            browser.close()

    finally:
        if proc is not None:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except Exception:
                proc.kill()
            print("[capture] server stopped")
        if settings_existed:
            shutil.copy2(BACKUP, SETTINGS)
            print("[capture] settings restored")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
