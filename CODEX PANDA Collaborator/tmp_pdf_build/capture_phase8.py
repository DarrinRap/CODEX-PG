"""Phase 8 screenshots — emergency pause active, escape hatch state 1 modal, test mode active.
Backs up settings, sets setup_completed, captures, restores."""
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
BACKUP = PC_ROOT / "tmp_pdf_build" / "settings_backup_phase8.json"
OUT = PC_ROOT / "tmp_pdf_build"
SCRIPT = PC_ROOT / "panda_collaborator.py"
URL = "http://127.0.0.1:8788/"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    if SETTINGS.exists():
        shutil.copy2(SETTINGS, BACKUP)

    proc = None
    try:
        proc = subprocess.Popen(
            [sys.executable, str(SCRIPT), "--port", "8788"],
            cwd=str(PC_ROOT),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(4)

        with sync_playwright() as p:
            browser = p.chromium.launch()
            ctx = browser.new_context(viewport={"width": 1366, "height": 768})
            page = ctx.new_page()
            page.goto(URL)
            page.wait_for_load_state("networkidle")
            time.sleep(2.0)
            # Drop launch gate if Phase 7 left it up (auto-removes after 4s in fallback).
            page.evaluate("() => { const g = document.getElementById('pcLaunchGate'); if (g) g.remove(); }")
            time.sleep(0.4)

            # --- Shot 1: Emergency Pause active — apply UI directly for deterministic visual ---
            page.evaluate("""
              () => {
                if (typeof applyEmergencyPauseUi === 'function') {
                  applyEmergencyPauseUi(true, 'Darrin');
                } else {
                  document.body.classList.add('is-paused');
                  const btn = document.getElementById('pauseBtn');
                  if (btn) {
                    btn.classList.add('danger');
                    const lbl = btn.querySelector('.pause-label');
                    if (lbl) lbl.textContent = 'Paused';
                  }
                  const detail = document.getElementById('emergencyPauseDetail');
                  if (detail) detail.textContent = 'Triggered by Darrin at ' + new Date().toISOString().replace('T',' ').slice(0,16) + ' UTC';
                }
              }
            """)
            time.sleep(0.4)
            page.screenshot(path=str(OUT / "PHASE8_EMERGENCY_PAUSE.png"), full_page=False)
            print("[capture] PHASE8_EMERGENCY_PAUSE.png saved")

            # --- Clear the pause for the next shot ---
            page.evaluate("""
              () => {
                if (typeof applyEmergencyPauseUi === 'function') applyEmergencyPauseUi(false, '');
                else document.body.classList.remove('is-paused');
              }
            """)
            time.sleep(0.4)

            # --- Shot 2: Test mode active — toggle body.test-mode class directly ---
            page.evaluate("() => document.body.classList.add('test-mode')")
            time.sleep(0.4)
            page.screenshot(path=str(OUT / "PHASE8_TEST_MODE.png"), full_page=False)
            print("[capture] PHASE8_TEST_MODE.png saved")
            page.evaluate("() => document.body.classList.remove('test-mode')")
            time.sleep(0.3)

            # --- Shot 3: Escape hatch state 1 modal — force-open via JS for a deterministic visual ---
            page.evaluate("""
              () => {
                const o = document.getElementById('escapeStep1Overlay');
                if (o) {
                  o.classList.add('is-open');
                  o.setAttribute('aria-hidden', 'false');
                }
              }
            """)
            time.sleep(0.4)
            page.screenshot(path=str(OUT / "PHASE8_ESCAPE_HATCH_STATE1.png"), full_page=False)
            print("[capture] PHASE8_ESCAPE_HATCH_STATE1.png saved")

            ctx.close()
            browser.close()

    finally:
        if proc is not None:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except Exception:
                proc.kill()
        if BACKUP.exists():
            shutil.copy2(BACKUP, SETTINGS)
            print("[capture] settings restored")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
