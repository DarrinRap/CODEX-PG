"""Phase 8 fix Issue B verification — capture test-mode visual at 1366x768
to confirm Bob yellow / Karen magenta + viewport box-shadow + identity colors."""
from __future__ import annotations

import shutil
import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

PC_ROOT = Path(r"C:\CODEX PG\CODEX PANDA Collaborator")
SETTINGS = PC_ROOT / "CODEX settings" / "panda_collaborator_settings.local.json"
BACKUP = PC_ROOT / "tmp_pdf_build" / "settings_backup_testmode_fix.json"
OUT = PC_ROOT / "tmp_pdf_build"
SCRIPT = PC_ROOT / "panda_collaborator.py"
URL = "http://127.0.0.1:8788/"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    settings_existed = SETTINGS.exists()
    if settings_existed:
        shutil.copy2(SETTINGS, BACKUP)

    proc = subprocess.Popen(
        [sys.executable, str(SCRIPT), "--port", "8788"],
        cwd=str(PC_ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(4)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            ctx = browser.new_context(viewport={"width": 1366, "height": 768})
            page = ctx.new_page()
            page.goto(URL)
            page.wait_for_load_state("networkidle")
            time.sleep(1.5)
            page.evaluate("() => { const g = document.getElementById('pcLaunchGate'); if (g) g.remove(); }")
            time.sleep(0.4)

            # Activate test mode + force user-one for Bob identity colors
            page.evaluate("""
              () => {
                document.body.classList.add('test-mode');
                document.body.classList.add('user-one');
              }
            """)
            time.sleep(0.4)
            page.screenshot(path=str(OUT / "PHASE8_FIX_ISSUE_B_BOB_ACTIVE.png"), full_page=False)
            print("[capture] PHASE8_FIX_ISSUE_B_BOB_ACTIVE.png")

            # Switch to user-two for Karen
            page.evaluate("""
              () => {
                document.body.classList.remove('user-one');
                document.body.classList.add('user-two');
              }
            """)
            time.sleep(0.3)
            page.screenshot(path=str(OUT / "PHASE8_FIX_ISSUE_B_KAREN_ACTIVE.png"), full_page=False)
            print("[capture] PHASE8_FIX_ISSUE_B_KAREN_ACTIVE.png")

            ctx.close()
            browser.close()
    finally:
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            proc.kill()
        if settings_existed:
            shutil.copy2(BACKUP, SETTINGS)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
