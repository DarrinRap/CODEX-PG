"""Capture PAH header screenshot at 1366x768. Used for BEFORE/AFTER comparison
of the header-fix dispatch. Saves to tmp_pdf_build under sibling directory."""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

PAH_ROOT = Path(r"C:\CODEX PG\CODEX Agent Hub")
PC_TMP = Path(r"C:\CODEX PG\CODEX PANDA Collaborator\tmp_pdf_build")
SCRIPT = PAH_ROOT / "CODEX_agent_hub.py"
URL = "http://127.0.0.1:8765/"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True, help="BEFORE or AFTER")
    args = ap.parse_args()
    PC_TMP.mkdir(parents=True, exist_ok=True)

    proc = subprocess.Popen(
        [sys.executable, str(SCRIPT), "--port", "8765"],
        cwd=str(PAH_ROOT),
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
            out = PC_TMP / f"PAH_HEADER_{args.label}.png"
            page.screenshot(path=str(out), full_page=False)
            print(f"[capture] saved {out.name}")
            ctx.close()
            browser.close()
    finally:
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            proc.kill()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
