"""Capture S1-S4 screenshots for PC manual build. Backs up settings JSON,
flips setup_completed:true + active_user_id:user1, captures, restores."""
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
BACKUP = PC_ROOT / "tmp_pdf_build" / "settings_backup.json"
OUT = PC_ROOT / "tmp_pdf_build"
SCRIPT = PC_ROOT / "panda_collaborator.py"
URL = "http://127.0.0.1:8788/"


def click_handover_for(page, user_label: str) -> str:
    """Click the Handover button for the named user.
    Strategy: find all Handover buttons and pick the one whose CLOSEST
    ancestor card contains the user label as a heading (USER 1 or USER 2)."""
    js = """
    (label) => {
      const buttons = Array.from(document.querySelectorAll('button'));
      const handover = buttons.filter(b => /^\\s*handover\\s*$/i.test((b.textContent || '').trim()));
      if (handover.length === 0) return {error: 'no handover buttons'};
      // Pair each button with the y-coord and the closest ancestor that
      // contains a small 'USER 1' or 'USER 2' heading element.
      const tagged = handover.map(b => {
        let cur = b;
        let userId = null;
        for (let i = 0; i < 8 && cur; i++) {
          const t = (cur.textContent || '').toUpperCase();
          // Card-level test: ancestor that mentions exactly one of USER 1 / USER 2
          const has1 = /USER 1\\b/.test(t);
          const has2 = /USER 2\\b/.test(t);
          if (has1 !== has2) { userId = has1 ? 'user1' : 'user2'; break; }
          cur = cur.parentElement;
        }
        const r = b.getBoundingClientRect();
        return {x: r.x + r.width/2, y: r.y + r.height/2, userId, text: (b.textContent||'').trim()};
      });
      const wantUser = /pam/i.test(label) ? 'user2' : 'user1';
      const match = tagged.find(t => t.userId === wantUser);
      if (match) return match;
      // Fallback: pick by x-coord — rightmost for Pam, leftmost for Darrin
      tagged.sort((a, b) => a.x - b.x);
      return /pam/i.test(label) ? tagged[tagged.length - 1] : tagged[0];
    }
    """
    coord = page.evaluate(js, user_label)
    if coord and "x" in coord:
        page.mouse.click(coord["x"], coord["y"])
        return f"clicked at ({coord['x']:.0f},{coord['y']:.0f}) userId={coord.get('userId')} text={coord.get('text')!r}"
    return f"no handover button: {coord}"


def capture_handoff_clip(page) -> dict | None:
    """Find the Create Handoff section bounding box."""
    js = """
    () => {
      const all = Array.from(document.querySelectorAll('*'));
      // Find a panel/section whose direct text contains "CREATE HANDOFF"
      const target = all.find(el => {
        const t = (el.textContent || '').toUpperCase();
        if (!t.includes('CREATE HANDOFF')) return false;
        // Want the panel container, not just text node — look for a sized box
        const r = el.getBoundingClientRect();
        return r.width > 200 && r.width < 900 && r.height > 200;
      });
      if (!target) return null;
      const r = target.getBoundingClientRect();
      return {x: r.x, y: r.y, w: r.width, h: r.height};
    }
    """
    return page.evaluate(js)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)

    shutil.copy2(SETTINGS, BACKUP)
    print(f"[capture] backup: {BACKUP}")

    data = json.loads(SETTINGS.read_text(encoding="utf-8"))
    data["setup_completed"] = True
    data["active_user_id"] = "user1"
    SETTINGS.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print("[capture] settings flipped: setup_completed=true, active_user_id=user1")

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
            time.sleep(1.2)

            # S1 — hub as-found (Darrin active per JSON)
            page.screenshot(path=str(OUT / "shot_hub.png"), full_page=False)
            print("[capture] S1 shot_hub.png saved")

            # S2 — Darrin-active hub. Already Darrin; copy S1.
            shutil.copy2(OUT / "shot_hub.png", OUT / "shot_darrin_active.png")
            print("[capture] S2 shot_darrin_active.png (= S1, already Darrin)")

            # S3 — switch to Pam
            status = click_handover_for(page, "PAM")
            print(f"[capture] S3 click: {status}")
            time.sleep(1.5)
            page.wait_for_load_state("networkidle")
            time.sleep(1)
            page.screenshot(path=str(OUT / "shot_pam_active.png"), full_page=False)
            print("[capture] S3 shot_pam_active.png saved")

            # S4 — handoff form. Use bounding-box discovery + page.screenshot clip.
            box = capture_handoff_clip(page)
            if box:
                pad_top = 8
                pad_x = 8
                clip = {
                    "x": max(0, box["x"] - pad_x),
                    "y": max(0, box["y"] - pad_top),
                    "width": min(box["w"] + 2 * pad_x, 1366 - max(0, box["x"] - pad_x)),
                    "height": min(box["h"] + pad_top * 2, 768 - max(0, box["y"] - pad_top)),
                }
                page.screenshot(path=str(OUT / "shot_handoff_form.png"), clip=clip)
                print(f"[capture] S4 shot_handoff_form.png clipped (box={box}, clip={clip})")
            else:
                # Fallback — full hub for downstream cropping
                page.screenshot(path=str(OUT / "shot_handoff_form.png"), full_page=False)
                print("[capture] S4 fallback full-frame")

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
        shutil.copy2(BACKUP, SETTINGS)
        print("[capture] settings restored from backup")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
