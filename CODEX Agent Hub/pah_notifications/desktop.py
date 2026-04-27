"""Desktop popup/tray notification scaffolding.

The first PAH build records desktop notification intent without invoking a
platform notification dependency. Live tray/toast behavior can be enabled by the
app shell once packaging choices are approved.
"""

from __future__ import annotations

from typing import Any


def desktop_popup_status(config: dict[str, Any] | None = None) -> dict[str, Any]:
    cfg = config or {}
    return {
        "enabled": bool(cfg.get("desktop_popups", {}).get("enabled", False)),
        "provider": cfg.get("desktop_popups", {}).get("provider", "tray_balloon"),
        "live": "when_tray_launcher_is_running",
        "detail": "Tray launcher watches the PAH notification log and shows Windows balloon popups for new entries.",
    }
