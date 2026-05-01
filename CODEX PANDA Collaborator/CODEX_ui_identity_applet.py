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
        'id="user1Transition"': "User 1 completion confirmation panel exists",
        'id="continueUser2Btn"': "User 2 is opened by an explicit continue action",
        "setRegistrationStage('user1Complete')": "User 1 registration no longer jumps straight to User 2",
        "transitionOpen && panelStage !== 'user1'": "Future registration panels are hidden during User 1 confirmation",
        '.setup-dialog[data-registration-stage="user1Complete"] .setup-project-step': "Confirmation mode hides prior setup sections",
        ".sequence-panel[data-user-tone].is-current": "Current workflow panel uses owned tone",
        ".registration-panel[data-user-tone].is-current": "Current registration panel uses owned tone",
        "var(--tone-accent, var(--user-accent))": "Register card name color prefers owned tone",
    }
    for needle, message in tone_checks.items():
        require(needle in html, message, failures)

    for user_id in ("user1", "user2"):
        require(f'data-hub-name="{user_id}"' in html, f"{user_id} display name binding exists", failures)

    if failures:
        print(f"\nIdentity applet failed {len(failures)} check(s).")
        return 1
    print("\nIdentity applet passed all name and color guard checks.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
