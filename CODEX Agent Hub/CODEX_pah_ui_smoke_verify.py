"""Read-only browser smoke verifier for the PAH dashboard."""

from __future__ import annotations

import json
import sys
import time
from typing import Any


DEFAULT_URL = "http://127.0.0.1:8765/"
REQUIRED_SELECTORS = (
    "#systemState",
    "#serverHealth",
    "#healthApi",
    "#agentList",
    "#actionList",
    "#summaryStrip",
    "#stewardPanel",
    "#simpleMailPanel",
)


def verify_ui(url: str = DEFAULT_URL) -> dict[str, Any]:
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        return {"ok": False, "error": f"playwright unavailable: {exc}", "url": url}

    console_errors: list[str] = []
    page_errors: list[str] = []
    started = time.perf_counter()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1366, "height": 768})
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda exc: page_errors.append(str(exc)))
        response = page.goto(url, wait_until="networkidle", timeout=15_000)
        status = response.status if response else 0
        title = page.title()
        missing = [selector for selector in REQUIRED_SELECTORS if page.locator(selector).count() == 0]
        system_text = page.locator("#systemState").inner_text(timeout=5_000) if not missing else ""
        health_text = page.locator("#serverHealth").inner_text(timeout=5_000) if not missing else ""
        browser.close()

    failed = bool(status < 200 or status >= 300 or missing or console_errors or page_errors or title != "PANDA Agent Hub")
    return {
        "ok": not failed,
        "url": url,
        "http_status": status,
        "title": title,
        "duration_ms": round((time.perf_counter() - started) * 1000, 2),
        "missing_selectors": missing,
        "console_errors": console_errors,
        "page_errors": page_errors,
        "system_state": system_text,
        "server_health_text": health_text,
    }


def main(argv: list[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    url = args[0] if args else DEFAULT_URL
    report = verify_ui(url)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
