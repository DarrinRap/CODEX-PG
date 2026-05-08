"""Issue A verification — capture User 2 section showing Register User 2 button
and verify it opens the setup modal."""
from __future__ import annotations

import shutil
import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

PC_ROOT = Path(r"C:\CODEX PG\CODEX PANDA Collaborator")
SETTINGS = PC_ROOT / "CODEX settings" / "panda_collaborator_settings.local.json"
BACKUP = PC_ROOT / "tmp_pdf_build" / "settings_backup_user2_reg.json"
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

            # Expand User 2 section so its register button is visible
            page.evaluate("""
              () => {
                const u2sec = document.querySelector('.sec.collapsible.user2-sec');
                if (u2sec) { u2sec.classList.remove('collapsed'); u2sec.classList.add('expanded'); }
              }
            """)
            time.sleep(0.4)
            page.screenshot(path=str(OUT / "PC_FIX_ISSUE_A_USER2_EXPANDED.png"), full_page=False)
            print("[capture] PC_FIX_ISSUE_A_USER2_EXPANDED.png")

            # Click Register User 2 to verify it opens the setup wizard
            try:
                page.evaluate("() => document.getElementById('openSetupBtn2').click()")
                time.sleep(0.6)
                page.screenshot(path=str(OUT / "PC_FIX_ISSUE_A_AFTER_CLICK.png"), full_page=False)
                print("[capture] PC_FIX_ISSUE_A_AFTER_CLICK.png (modal should be open)")
            except Exception as exc:
                print(f"[capture] click failed: {exc}")

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
