"""Capture the current live PC main view + key states for visual review.
Shows what shipped this session: Phases 6/7/8 + setup-modal-fix + regression
fix + test mode (Issue B) + User 2 register button (Issue A)."""
from __future__ import annotations

import shutil
import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

PC_ROOT = Path(r"C:\CODEX PG\CODEX PANDA Collaborator")
SETTINGS = PC_ROOT / "CODEX settings" / "panda_collaborator_settings.local.json"
BACKUP = PC_ROOT / "tmp_pdf_build" / "settings_backup_pc_final.json"
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
            time.sleep(2)
            page.evaluate("() => { const g = document.getElementById('pcLaunchGate'); if (g) g.remove(); }")
            time.sleep(0.4)

            # Shot 1: main view as launched (current default state)
            page.screenshot(path=str(OUT / "PC_FINAL_01_main_view.png"), full_page=False)
            print("[capture] PC_FINAL_01_main_view.png")

            # Shot 2: setup modal opened (Phase 7 + setup-modal-fix outcome)
            try:
                page.evaluate("() => document.getElementById('openSetupBtn').click()")
                time.sleep(0.6)
                page.screenshot(path=str(OUT / "PC_FINAL_02_setup_modal.png"), full_page=False)
                print("[capture] PC_FINAL_02_setup_modal.png")
                page.evaluate("() => document.getElementById('cancelSetupBtn').click()")
                time.sleep(0.4)
            except Exception as exc:
                print(f"[capture] setup modal capture issue: {exc}")

            # Shot 3: User 2 register button click (Issue A fix verification)
            try:
                page.evaluate("""
                  () => {
                    const sec = document.querySelector('.sec.collapsible.user2-sec');
                    if (sec) { sec.classList.remove('collapsed'); sec.classList.add('expanded'); }
                  }
                """)
                time.sleep(0.3)
                page.evaluate("() => document.getElementById('openSetupBtn2').click()")
                time.sleep(0.6)
                page.screenshot(path=str(OUT / "PC_FINAL_03_user2_register.png"), full_page=False)
                print("[capture] PC_FINAL_03_user2_register.png")
                page.evaluate("() => document.getElementById('cancelSetupBtn').click()")
                time.sleep(0.4)
            except Exception as exc:
                print(f"[capture] user2 register capture issue: {exc}")

            # Shot 4: test mode active with Karen identity (Issue B fix)
            try:
                page.evaluate("""
                  () => {
                    document.body.classList.add('test-mode');
                    document.body.classList.add('user-two');
                  }
                """)
                time.sleep(0.4)
                page.screenshot(path=str(OUT / "PC_FINAL_04_test_mode_karen.png"), full_page=False)
                print("[capture] PC_FINAL_04_test_mode_karen.png")
                page.evaluate("() => { document.body.classList.remove('test-mode'); document.body.classList.remove('user-two'); }")
                time.sleep(0.3)
            except Exception as exc:
                print(f"[capture] test mode capture issue: {exc}")

            # Shot 5: emergency pause active (Phase 8)
            try:
                page.evaluate("""
                  () => {
                    if (typeof applyEmergencyPauseUi === 'function') applyEmergencyPauseUi(true, 'Darrin');
                  }
                """)
                time.sleep(0.4)
                page.screenshot(path=str(OUT / "PC_FINAL_05_emergency_pause.png"), full_page=False)
                print("[capture] PC_FINAL_05_emergency_pause.png")
            except Exception as exc:
                print(f"[capture] emergency pause capture issue: {exc}")

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
