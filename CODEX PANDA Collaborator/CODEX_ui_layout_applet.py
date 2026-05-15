from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
HTML_PATH = ROOT / "web" / "index.html"


def css_block(source: str, selector: str) -> str:
    match = re.search(rf"{re.escape(selector)}\s*\{{(?P<body>.*?)\n\s*\}}", source, re.S)
    return match.group("body") if match else ""


def require(condition: bool, message: str, failures: list[str]) -> None:
    if condition:
        print(f"PASS {message}")
    else:
        print(f"FAIL {message}")
        failures.append(message)


def _first_existing(paths: list[Path]) -> Path | None:
    for path in paths:
        if path.exists():
            return path
    return None


def rendered_layout_failures() -> list[str]:
    """Use a real browser to catch geometry bugs CSS string checks cannot see."""
    home = Path.home()
    runtime_root = home / ".cache" / "codex-runtimes" / "codex-primary-runtime" / "dependencies"
    node_exe = runtime_root / "node" / "bin" / "node.exe"
    node_modules = runtime_root / "node" / "node_modules"
    browser_exe = _first_existing(
        [
            Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
            Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
            Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        ]
    )
    if not node_exe.exists():
        return [f"Rendered check unavailable: missing bundled Node runtime at {node_exe}"]
    if not (node_modules / "playwright").exists():
        return [f"Rendered check unavailable: missing bundled Playwright at {node_modules}"]
    if browser_exe is None:
        return ["Rendered check unavailable: no local Edge/Chrome executable found"]

    script = r"""
const { chromium } = require('playwright');
const path = require('path');
const browserPath = process.argv[1];
const htmlPath = process.argv[2];

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: browserPath });
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 }, deviceScaleFactor: 1 });
  const url = 'file:///' + path.resolve(htmlPath).replace(/\\/g, '/').replace(/ /g, '%20');
  await page.goto(url, { waitUntil: 'domcontentloaded' });
  const failures = await page.evaluate(() => {
    const out = [];
    const profile = (id, displayName) => ({
      id,
      display_name: displayName,
      default_repo_path: 'C:\\CODEX PG',
      handoff_agent: id === 'user1' ? 'Codex' : 'Claude',
      handoff_title: `${displayName} handoff`,
      codex_account: `${displayName.toLowerCase()}-codex@example.invalid`,
      claude_account: `${displayName.toLowerCase()}-claude@example.invalid`,
      claude_desktop_path: `C:\\Fake\\${displayName}\\Claude Desktop.exe`,
      claude_code_path: `C:\\Fake\\${displayName}\\Claude Code.cmd`,
      git_author_name: displayName,
      git_author_email: `${displayName.toLowerCase()}@example.invalid`
    });
    if (typeof state === 'undefined' || typeof updateHubCards !== 'function') {
      return ['Rendered check could not access PC frontend state/updateHubCards.'];
    }
    state.settings = {
      active_user_id: 'user2',
      project_files_directory: 'C:\\panda-gallery',
      users: [profile('user1', 'Darrin'), profile('user2', 'Pam')]
    };
    state.busy = false;
    if (typeof renderSettings === 'function') renderSettings();
    updateHubCards();
    if (typeof openSetupWizard === 'function') openSetupWizard();
    if (typeof setRegistrationStage === 'function') setRegistrationStage('users');

    const intersects = (a, b) => (
      a.left < b.right && a.right > b.left && a.top < b.bottom && a.bottom > b.top
    );
    const visible = element => {
      const style = getComputedStyle(element);
      const rect = element.getBoundingClientRect();
      return style.display !== 'none' && style.visibility !== 'hidden' && rect.width > 0 && rect.height > 0;
    };
    document.querySelectorAll('.hub-card').forEach((card, index) => {
      if (!visible(card)) return;
      const inRegistrationHub = Boolean(card.closest('#registrationHubGrid'));
      const cardRect = card.getBoundingClientRect();
      const name = card.querySelector('strong');
      const button = card.querySelector('button[data-switch-go]');
      if (!name || !button || !visible(button)) return;
      const nameRect = name.getBoundingClientRect();
      const buttonRect = button.getBoundingClientRect();
      const label = button.textContent.trim();
      if (/USER\s*[12]|DARRIN|PAM|KAREN|BOB/.test(label.toUpperCase())) {
        out.push(`Hub card ${index + 1}: handover button repeats user identity in visible text (${label}).`);
      }
      if (!inRegistrationHub && buttonRect.height > 36) {
        out.push(`Hub card ${index + 1}: handover button is too tall (${Math.round(buttonRect.height)}px).`);
      }
      if (inRegistrationHub && buttonRect.height > 48) {
        out.push(`Registration hub card ${index + 1}: handover button is too tall (${Math.round(buttonRect.height)}px).`);
      }
      if (button.scrollWidth > button.clientWidth + 1 || button.scrollHeight > button.clientHeight + 1) {
        out.push(`Hub card ${index + 1}: handover button text is clipped or overflowing.`);
      }
      if (intersects(nameRect, buttonRect)) {
        out.push(`Hub card ${index + 1}: user name and handover button overlap.`);
      }
      if (buttonRect.left < cardRect.left + 1 || buttonRect.right > cardRect.right - 1 || buttonRect.bottom > cardRect.bottom - 1) {
        out.push(`Hub card ${index + 1}: handover button escapes card bounds.`);
      }
    });

    const setupDialog = document.querySelector('.setup-dialog');
    const wizardGrid = document.querySelector('.wizard-grid');
    const setupFoot = document.querySelector('.setup-dialog-foot');
    if (!setupDialog || !wizardGrid || !setupFoot || !visible(setupDialog)) {
      out.push('Setup dialog is not visible for registration geometry checks.');
      return out;
    }
    const gridRect = wizardGrid.getBoundingClientRect();
    const footRect = setupFoot.getBoundingClientRect();
    if (gridRect.bottom > footRect.top + 1) {
      out.push('Setup footer overlaps the registration content area.');
    }
    if (wizardGrid.scrollWidth > wizardGrid.clientWidth + 1) {
      out.push('Setup grid has horizontal overflow.');
    }

    const user1Panel = document.querySelector('[data-registration-stage="user1"]');
    const user2Panel = document.querySelector('[data-registration-stage="user2"]');
    if (!user1Panel || !user2Panel || !visible(user1Panel) || !visible(user2Panel)) {
      out.push('Both User 1 and User 2 registration panels must be visible together.');
    } else {
      const user1Rect = user1Panel.getBoundingClientRect();
      const user2Rect = user2Panel.getBoundingClientRect();
      if (Math.abs(user1Rect.top - user2Rect.top) > 2) {
        out.push('User 1 and User 2 panels are not aligned side by side.');
      }
      if (intersects(user1Rect, user2Rect)) {
        out.push('User 1 and User 2 panels overlap.');
      }
    }

    document.querySelectorAll('[data-collapse-panel]').forEach(button => {
      if (button.getAttribute('aria-expanded') === 'false') button.click();
    });
    const expandedUser1Rect = user1Panel?.getBoundingClientRect();
    const expandedUser2Rect = user2Panel?.getBoundingClientRect();
    if (expandedUser1Rect && expandedUser2Rect && (expandedUser1Rect.height < 220 || expandedUser2Rect.height < 220)) {
      out.push('Expanded user registration panels are too short to work in comfortably.');
    }

    ['user1Name', 'profileRepoPath', 'profileAgent', 'user2Name', 'profileRepoPathUser2', 'profileAgentUser2'].forEach(id => {
      const element = document.getElementById(id);
      if (!element || !visible(element)) {
        out.push(`Registration field #${id} is not visible without scrolling the whole dialog.`);
        return;
      }
      const rect = element.getBoundingClientRect();
      if (rect.bottom > footRect.top - 1) {
        out.push(`Registration field #${id} is hidden behind the setup footer.`);
      }
    });

    Array.from(setupDialog.querySelectorAll('button')).filter(visible).forEach(button => {
      const rect = button.getBoundingClientRect();
      if (button.scrollWidth > button.clientWidth + 1 || button.scrollHeight > button.clientHeight + 1) {
        out.push(`Setup button text overflows: ${button.textContent.trim()}`);
      }
      if (rect.bottom > footRect.bottom + 1 || rect.right > setupDialog.getBoundingClientRect().right + 1) {
        out.push(`Setup button escapes dialog bounds: ${button.textContent.trim()}`);
      }
    });
    return out;
  });
  await browser.close();
  console.log(JSON.stringify(failures));
})().catch(error => {
  console.error(error && error.stack ? error.stack : String(error));
  process.exit(2);
});
"""
    completed = subprocess.run(
        [str(node_exe), "-e", script, str(browser_exe), str(HTML_PATH)],
        capture_output=True,
        text=True,
        timeout=45,
        env={**os.environ, "NODE_PATH": str(node_modules)},
        check=False,
    )
    if completed.returncode != 0:
        return [f"Rendered check failed to run: {completed.stderr.strip() or completed.stdout.strip()}"]
    try:
        return list(json.loads(completed.stdout.strip() or "[]"))
    except json.JSONDecodeError:
        return [f"Rendered check returned unreadable output: {completed.stdout.strip()}"]


def main() -> int:
    html = HTML_PATH.read_text(encoding="utf-8")
    failures: list[str] = []

    button_css = css_block(html, "button")
    chip_css = css_block(html, ".chip")
    test_status_pill = css_block(html, ".test-status-pill")
    test_mode_button = css_block(html, ".test-mode-btn")
    quit_test_button = css_block(html, ".quit-test-btn")
    header_top = css_block(html, ".header-top")
    workflow_row = css_block(html, ".workflow-row")
    support_grid = css_block(html, ".support-grid")
    repo_panel = css_block(html, ".repo-panel")
    repo_body = css_block(html, ".repo-panel .panel-body")
    repo_controls = css_block(html, ".repo-scan-controls")
    repo_label = css_block(html, ".repo-scan-controls label")
    repo_picker = css_block(html, ".repo-scan-controls .inline-picker")
    repo_button = css_block(html, ".repo-scan-controls button")
    hub_card = css_block(html, ".hub-card")
    hub_button = css_block(html, ".hub-card button")
    setup_dialog = css_block(html, ".setup-dialog")
    wizard_grid = css_block(html, ".wizard-grid")
    registration_panel = css_block(html, ".registration-panel")
    registration_body = css_block(html, ".registration-panel .wizard-step-body")
    small_media = html.split("@media (max-width: 1200px)", 1)[1] if "@media (max-width: 1200px)" in html else ""
    narrow_media = html.split("@media (max-width: 1200px)", 1)[1] if "@media (max-width: 1200px)" in html else ""
    escape_handler = html.split("document.addEventListener('keydown', event =>", 1)[1].split("$('resultBox').addEventListener", 1)[0] if "document.addEventListener('keydown', event =>" in html else ""

    require("border-radius: 999px;" not in button_css, "Bible: global action buttons are rectangular, not pills", failures)
    require("border-radius: 999px;" not in test_mode_button, "Bible: TEST action buttons are rectangular, not pills", failures)
    require("border-radius: 999px;" not in quit_test_button, "Bible: QUIT TEST MODE action is rectangular, not pills", failures)
    require("border-radius: 999px;" in chip_css, "Bible: status chips use pill geometry", failures)
    require("cursor: default;" in chip_css, "Bible: status chips are informational, not action controls", failures)
    require("border-radius: 999px;" in test_status_pill or "border-radius: 999px;" in chip_css, "Bible: TEST PASS/FAIL is a status pill", failures)
    require("cursor: default;" in test_status_pill, "Bible: TEST PASS/FAIL pill does not do work", failures)
    require('id="openTestEvidenceBtn"' in html, "Bible: evidence opens through a rectangular action button", failures)
    require("$('openTestEvidenceBtn').addEventListener('click', openTestEvidence)" in html, "Bible: Open Evidence action has explicit click wiring", failures)
    require("$('testStatusPill').addEventListener" not in html, "Bible: TEST status pill has no click handler", failures)
    require("flex-wrap: wrap;" in small_media and ".header-top" in small_media, "Responsive: header wraps instead of overlaying controls", failures)
    require("grid-template-columns: minmax(0, 1fr);" in small_media and ".workflow-row" in small_media, "Responsive: workflow cards stack on narrow screens", failures)
    require("grid-template-columns: minmax(0, 1fr);" in small_media and ".support-grid" in small_media, "Responsive: support panels stack on narrow screens", failures)
    require(".repo-panel," in small_media and ".status-panel," in small_media and ".files-panel," in small_media and ".safety-panel" in small_media, "Responsive: fixed support panel grid placements are overridden", failures)
    require("grid-row: auto;" in small_media, "Responsive: support panels use natural row flow when stacked", failures)
    require("overflow-y: auto;" in small_media and "overflow-x: hidden;" in small_media, "Responsive: narrow main view scrolls vertically without horizontal clipping", failures)
    require("grid-template-columns: minmax(78px" not in small_media, "Responsive: old too-wide five-column narrow grid is removed", failures)
    require("grid-template-columns: minmax(220px" not in small_media, "Responsive: old too-wide support-grid narrow layout is removed", failures)
    require("grid-template-columns: minmax(145px" in workflow_row, "Desktop: workflow keeps five-column dashboard grammar", failures)
    require("grid-template-columns: minmax(300px" in support_grid, "Desktop: support grid keeps dashboard grammar", failures)
    require("display: flex;" in header_top, "Header uses a flexible row on desktop", failures)

    require("overflow: hidden;" in hub_card, "Hub cards clip internal overflow instead of spilling into neighboring UI", failures)
    require("grid-template-rows: auto auto minmax(0, 1fr) auto;" in hub_card, "Hub cards reserve a stable bottom row for handover actions", failures)
    require("max-height: 34px;" in hub_button, "Hub handover buttons are bounded to prevent oversized blocks", failures)
    require("white-space: nowrap;" in hub_button, "Hub handover buttons use one-line labels", failures)
    require("return {text: 'Handover'" in html, "Hub handover visible labels stay short; user identity lives on the card and aria-label", failures)
    require("button.textContent = 'Set up';" in html, "Hub setup visible labels stay short; user identity lives on the card and aria-label", failures)

    require("max-height: min(900px, calc(100vh - 44px));" in setup_dialog, "Registration dialog has a stable height so its footer cannot cover fields", failures)
    require("grid-template-areas:" in wizard_grid and '"user1 user2"' in wizard_grid, "Registration setup uses a real side-by-side two-user grid", failures)
    require('"hub hub"' not in wizard_grid, "Registration hub is not mixed into the setup form flow", failures)
    require("overflow: hidden;" in wizard_grid or "minmax(0, 1fr)" in wizard_grid, "Registration outer grid blocks whole-dialog scroll traps", failures)
    require("min-height: 0;" in registration_panel or "overflow: hidden;" in registration_panel, "Registration panels reserve a bounded scrollable body", failures)
    require("overflow-y: auto;" in registration_body, "Each user form scrolls inside its own panel", failures)
    require("overflow-x: hidden;" in registration_body, "Registration forms block horizontal overflow", failures)
    require('id="saveSettingsBtn"' in html, "Registration uses one clear Save Settings action", failures)
    require("syncAllRegistrationFieldsToState();" in html, "Save Settings reads both visible user panels before saving", failures)
    require("$('saveSettingsBtn').disabled = state.busy || !readiness.allReady;" in html, "Save Settings stays grey until both users are ready", failures)
    require("data-wg-step=\"setup\"" in html and "data-wg-step=\"handoff\"" in html, "Workflow guide spans setup through handoff", failures)
    require("step.done ? '✓' : String(index + 1)" in html, "Workflow guide shows check marks when steps complete", failures)
    require("node.classList.add(step.state)" in html, "Workflow guide applies live state colors", failures)

    require("overflow: hidden;" in repo_panel, "Working Tree panel clips stray horizontal divider/scrollbar", failures)
    require("overflow-x: hidden;" in repo_body, "Working Tree body blocks horizontal overflow", failures)
    require("overflow-y: auto;" in repo_body, "Working Tree body scrolls only vertically", failures)
    require("grid-template-rows: auto minmax(44px, 1fr);" in repo_body, "Working Tree result area keeps usable height after scan", failures)
    require("grid-template-columns: repeat(2, minmax(0, 1fr));" in repo_controls, "Scan and Packages are separated into equal action columns", failures)
    require("gap: 8px;" in repo_controls, "Working Tree controls keep visible spacing", failures)
    require("grid-column: 1 / -1;" in repo_label, "Repository path picker is above scan actions, not touching them", failures)
    require("grid-template-columns: minmax(0, 1fr) minmax(96px, auto);" in repo_picker, "Browse button has a stable width beside the repository path", failures)
    require("min-height: 38px;" in repo_button, "Working Tree action buttons are large but bounded", failures)
    require(".repo-scan-controls { grid-template-columns: minmax(0, 1fr); }" in narrow_media, "Narrow screens stack Working Tree actions instead of colliding", failures)
    require(".repo-scan-controls button { width: 100%; }" in narrow_media, "Narrow Working Tree buttons fill their own rows", failures)
    require("event.key !== 'Escape'" in escape_handler, "Escape key handler is installed", failures)
    require("document.activeElement?.blur?.();" in escape_handler, "Escape clears stuck scan-button focus", failures)
    require("document.querySelector('.repo-panel .panel-body')?.scrollTo?.({top: 0, left: 0});" in escape_handler, "Escape returns Working Tree scroll to origin", failures)

    for message in rendered_layout_failures():
        print(f"FAIL Rendered geometry: {message}")
        failures.append(f"Rendered geometry: {message}")

    if failures:
        print(f"\nLayout applet failed {len(failures)} check(s).")
        return 1
    print("\nLayout applet passed all Working Tree layout guard checks.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
