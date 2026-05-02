from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
HTML_PATH = ROOT / "web" / "index.html"


def require(condition: bool, message: str, failures: list[str]) -> None:
    if condition:
        print(f"PASS {message}")
    else:
        print(f"FAIL {message}")
        failures.append(message)


def css_block(source: str, selector: str) -> str:
    match = re.search(rf"{re.escape(selector)}\s*\{{(?P<body>.*?)\n\s*\}}", source, re.S)
    return match.group("body") if match else ""


def function_body(source: str, name: str, next_name: str) -> str:
    try:
        return source.split(f"function {name}()", 1)[1].split(f"function {next_name}()", 1)[0]
    except IndexError:
        return ""


def main() -> int:
    html = HTML_PATH.read_text(encoding="utf-8")
    failures: list[str] = []

    user_one_css = css_block(html, "body.user-one").lower()
    user_two_css = css_block(html, "body.user-two").lower()
    theme_body = function_body(html, "effectiveThemeUserId", "applyUserTheme")

    require("--user-accent: #f2b36d" in user_one_css, "User 1 active theme is warm amber", failures)
    require("--user-accent: #68d8e8" in user_two_css, "User 2 active theme is cool cyan", failures)
    require("registrationStage" not in theme_body, "Registration stage does not impersonate the active user", failures)

    tone_checks = {
        'data-flow-panel="user1" data-user-tone="user1"': "User 1 workflow panel owns warm tone",
        'data-flow-panel="user2" data-user-tone="user2"': "User 2 workflow panel owns cyan tone",
        'class="setup-dialog" data-user-tone="user1"': "Setup dialog starts with User 1 tone",
        'data-registration-stage="user1" data-user-tone="user1"': "User 1 registration panel owns warm tone",
        'data-registration-stage="user2" data-user-tone="user2"': "User 2 registration panel owns cyan tone",
        "setupDialog.dataset.userTone = userTone": "Setup dialog tone follows registration stage",
        '[data-user-tone="user1"]': "User 1 tone variables exist",
        '[data-user-tone="user2"]': "User 2 tone variables exist",
        "--tone-accent: #f2b36d": "Warm tone accent is amber",
        "--tone-accent: #68d8e8": "Cool tone accent is cyan",
        "color: var(--tone-accent, var(--user-accent))": "Setup dialog title prefers owned tone",
        ".setup-dialog[data-user-tone] .setup-checklist li.current": "Setup checklist current row uses dialog tone",
        "button:not(:disabled):not(.danger)": "Enabled safe action buttons use the green active grammar",
        "background: linear-gradient(180deg, #8ccf6f, #6da850)": "Green enabled-button background exists",
        "function registrationMissingFields(userId)": "Registration reports missing fields",
        "$('registerUser2FinishBtn').dataset.missingFields": "User 2 finish button explains missing fields",
        "users: 'REGISTER USERS'": "Setup registration uses one shared two-user stage",
        "grid-template-columns: repeat(2, minmax(360px, 1fr))": "User 1 and User 2 registration panels sit side by side on desktop",
        "User 1 saved. User 2 remains visible on the same setup screen.": "User 1 save stays on the shared registration screen",
        "await saveCurrentSettings();": "User 1 registration persists before User 2 can finish",
        ".status-panel .panel-body": "Status Messages panel owns one hidden outer overflow layer",
        "scrollbar-gutter: stable": "Status Messages scrolling has a stable single gutter",
        "grid-template-columns: repeat(2, minmax(0, 1fr))": "Working Tree scan actions use separated two-column controls",
        ".repo-scan-controls label": "Working Tree repository picker owns its own row",
        "grid-column: 1 / -1": "Working Tree repository picker spans above scan actions",
        "overflow-x: hidden": "Working Tree panel blocks stray horizontal divider scroll",
        "document.addEventListener('keydown', event =>": "Escape recovery wiring exists",
        "event.key !== 'Escape'": "Escape recovery only handles Escape",
        "document.activeElement?.blur?.()": "Escape clears stuck button/input focus",
        "document.querySelector('.repo-panel .panel-body')?.scrollTo?.({top: 0, left: 0});": "Escape returns Working Tree scroll position",
        'id="testModeBtn"': "TEST MODE button exists",
        'id="quitTestModeBtn"': "QUIT TEST MODE header button exists",
        'id="quitTestModeBannerBtn"': "QUIT TEST MODE banner button exists",
        "body.test-mode": "TEST MODE alert theme exists",
        "function enterTestMode()": "TEST MODE entry function exists",
        "function quitTestMode(result = '')": "TEST MODE quit/restore function exists",
        "display_name: 'Bob'": "TEST MODE uses Bob as fake User 1",
        "display_name: 'Karen'": "TEST MODE uses Karen as fake User 2",
        "localStorage.setItem('pandaCollaborator.testModeSnapshot'": "TEST MODE captures a normal-state snapshot",
        "localStorage.removeItem('pandaCollaborator.testModeActive')": "QUIT TEST MODE clears active test state",
        "TEST MODE quit complete. Normal Darrin and Pam state restored": "QUIT TEST MODE reports Darrin/Pam restore",
        ".sequence-panel[data-user-tone].is-current": "Current workflow panel uses owned tone",
        ".registration-panel[data-user-tone].is-current": "Current registration panel uses owned tone",
        "var(--tone-accent, var(--user-accent))": "Register card name color prefers owned tone",
    }
    for needle, message in tone_checks.items():
        require(needle in html, message, failures)

    forbidden_checks = {
        'id="user1Transition"': "Old User 1 confirmation panel is removed",
        'id="continueUser2Btn"': "Old Continue to User 2 jump button is removed",
        "user1Complete": "Old User 1 completion stage is removed",
        "document.querySelector('.wizard-grid')?.scrollTo?.({top: 0});": "Registration no longer jumps the wizard scroll position",
        ".registration-panel:not(.is-current) .wizard-step-body": "Inactive registration bodies stay visible",
    }
    for needle, message in forbidden_checks.items():
        require(needle not in html, message, failures)

    for user_id in ("user1", "user2"):
        require(f'data-hub-name="{user_id}"' in html, f"{user_id} display name binding exists", failures)

    if failures:
        print(f"\nIdentity applet failed {len(failures)} check(s).")
        return 1
    print("\nIdentity applet passed all name and color guard checks.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
