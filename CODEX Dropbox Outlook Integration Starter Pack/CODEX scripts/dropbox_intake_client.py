"""Dropbox intake reference client for Panda Gallery Audit MVP.

This module is sample/reference code only. It uses environment variables and
standard-library HTTP calls so Claude can see the intended behavior without
pulling dependencies into Panda Gallery prematurely.

No real credentials are included. Do not commit tokens.
"""

from __future__ import annotations

import dataclasses
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

DROPBOX_API = "https://api.dropboxapi.com/2"
DROPBOX_CONTENT = "https://content.dropboxapi.com/2"
TOKEN_URL = "https://api.dropboxapi.com/oauth2/token"


class DropboxIntakeError(RuntimeError):
    """Raised when Dropbox intake cannot proceed safely."""


@dataclasses.dataclass(frozen=True)
class DropboxConfig:
    app_key: str
    refresh_token: str
    incoming_folder: str
    app_secret: str | None = None
    local_staging_root: Path = Path("C:/CODEX PG/CODEX Audit Intake Staging")
    completion_marker: str = "_PACKAGE_READY.json"

    @classmethod
    def from_env(cls) -> "DropboxConfig":
        app_key = os.environ.get("PG_DROPBOX_APP_KEY", "").strip()
        refresh_token = os.environ.get("PG_DROPBOX_REFRESH_TOKEN", "").strip()
        incoming = os.environ.get("PG_DROPBOX_INCOMING_FOLDER", "/Panda Gallery Audit/Incoming").strip()
        secret = os.environ.get("PG_DROPBOX_APP_SECRET") or None
        staging = Path(os.environ.get("PG_AUDIT_INTAKE_STAGING", "C:/CODEX PG/CODEX Audit Intake Staging"))
        if not app_key or not refresh_token:
            raise DropboxIntakeError(
                "Dropbox credentials are not configured. Set PG_DROPBOX_APP_KEY and "
                "PG_DROPBOX_REFRESH_TOKEN, or use dry-run/local sample mode."
            )
        return cls(app_key=app_key, refresh_token=refresh_token, incoming_folder=incoming, app_secret=secret, local_staging_root=staging)


@dataclasses.dataclass(frozen=True)
class DropboxEntry:
    name: str
    path_lower: str
    path_display: str
    tag: str


class DropboxIntakeClient:
    def __init__(self, config: DropboxConfig):
        self.config = config
        self._access_token: str | None = None

    def refresh_access_token(self) -> str:
        body = {
            "grant_type": "refresh_token",
            "refresh_token": self.config.refresh_token,
            "client_id": self.config.app_key,
        }
        if self.config.app_secret:
            body["client_secret"] = self.config.app_secret
        response = self._post_form(TOKEN_URL, body)
        token = response.get("access_token")
        if not token:
            raise DropboxIntakeError("Dropbox token response did not include access_token.")
        self._access_token = token
        return token

    def list_folder(self, folder_path: str | None = None) -> tuple[list[DropboxEntry], str | None]:
        payload = {"path": folder_path or self.config.incoming_folder, "recursive": False, "include_deleted": False}
        data = self._api_post("/files/list_folder", payload)
        entries = [self._entry_from_json(item) for item in data.get("entries", [])]
        cursor = data.get("cursor")
        while data.get("has_more"):
            data = self._api_post("/files/list_folder/continue", {"cursor": cursor})
            entries.extend(self._entry_from_json(item) for item in data.get("entries", []))
            cursor = data.get("cursor")
        return entries, cursor

    def find_ready_packages(self) -> list[DropboxEntry]:
        entries, _ = self.list_folder(self.config.incoming_folder)
        folders = [entry for entry in entries if entry.tag == "folder"]
        ready: list[DropboxEntry] = []
        for folder in folders:
            marker_path = f"{folder.path_display.rstrip('/')}/{self.config.completion_marker}"
            try:
                self.get_metadata(marker_path)
            except DropboxIntakeError:
                continue
            ready.append(folder)
        return ready

    def get_metadata(self, dropbox_path: str) -> dict[str, Any]:
        return self._api_post("/files/get_metadata", {"path": dropbox_path})

    def download_text(self, dropbox_path: str) -> str:
        data = self.download_file(dropbox_path)
        return data.decode("utf-8")

    def download_file(self, dropbox_path: str) -> bytes:
        token = self._token()
        request = urllib.request.Request(
            DROPBOX_CONTENT + "/files/download",
            headers={
                "Authorization": f"Bearer {token}",
                "Dropbox-API-Arg": json.dumps({"path": dropbox_path}),
            },
            method="POST",
        )
        return self._urlopen_bytes(request)

    def download_ready_package_manifest(self, package_folder: DropboxEntry) -> dict[str, Any]:
        marker_path = f"{package_folder.path_display.rstrip('/')}/{self.config.completion_marker}"
        marker = json.loads(self.download_text(marker_path))
        manifest_name = marker.get("manifest_path", "session_package_manifest.json")
        manifest_path = f"{package_folder.path_display.rstrip('/')}/{manifest_name}"
        manifest = json.loads(self.download_text(manifest_path))
        if marker.get("package_id") and manifest.get("package_id") and marker["package_id"] != manifest["package_id"]:
            raise DropboxIntakeError("Completion marker package_id does not match manifest package_id.")
        return manifest

    def _token(self) -> str:
        return self._access_token or self.refresh_access_token()

    def _api_post(self, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        token = self._token()
        request = urllib.request.Request(
            DROPBOX_API + endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            method="POST",
        )
        raw = self._urlopen_bytes(request)
        return json.loads(raw.decode("utf-8"))

    @staticmethod
    def _post_form(url: str, form: dict[str, str]) -> dict[str, Any]:
        request = urllib.request.Request(
            url,
            data=urllib.parse.urlencode(form).encode("utf-8"),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        raw = DropboxIntakeClient._urlopen_bytes(request)
        return json.loads(raw.decode("utf-8"))

    @staticmethod
    def _urlopen_bytes(request: urllib.request.Request) -> bytes:
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return response.read()
        except urllib.error.HTTPError as exc:
            if exc.code == 429:
                retry_after = exc.headers.get("Retry-After")
                if retry_after and retry_after.isdigit():
                    time.sleep(min(int(retry_after), 30))
            detail = exc.read().decode("utf-8", errors="replace")
            raise DropboxIntakeError(f"Dropbox HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise DropboxIntakeError(f"Dropbox network error: {exc}") from exc

    @staticmethod
    def _entry_from_json(item: dict[str, Any]) -> DropboxEntry:
        return DropboxEntry(
            name=item.get("name", ""),
            path_lower=item.get("path_lower", ""),
            path_display=item.get("path_display", ""),
            tag=item.get(".tag", "unknown"),
        )


def main() -> int:
    config = DropboxConfig.from_env()
    client = DropboxIntakeClient(config)
    ready = client.find_ready_packages()
    print(json.dumps([dataclasses.asdict(entry) for entry in ready], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
