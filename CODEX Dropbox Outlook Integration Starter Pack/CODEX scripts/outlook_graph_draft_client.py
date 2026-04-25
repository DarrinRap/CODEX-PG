"""Microsoft Graph Outlook draft client for Panda Gallery Audit MVP.

This is reference code. It creates drafts by default. Sending is intentionally
separate and guarded because sending email is external communication and must
be explicitly approved by a human at action time.
"""

from __future__ import annotations

import dataclasses
import json
import os
import urllib.error
import urllib.request
from typing import Any

GRAPH_ROOT = "https://graph.microsoft.com/v1.0"


class OutlookDraftError(RuntimeError):
    """Raised when Outlook draft/send work cannot proceed safely."""


@dataclasses.dataclass(frozen=True)
class GraphConfig:
    access_token: str
    user_path: str = "/me"

    @classmethod
    def from_env(cls) -> "GraphConfig":
        token = os.environ.get("PG_GRAPH_ACCESS_TOKEN", "").strip()
        user_path = os.environ.get("PG_GRAPH_USER_PATH", "/me").strip() or "/me"
        if not token:
            raise OutlookDraftError(
                "Microsoft Graph access token is not configured. Use OAuth/MSAL later, "
                "or run this client only in dry-run mode."
            )
        if not user_path.startswith("/"):
            user_path = "/" + user_path
        return cls(access_token=token, user_path=user_path)


@dataclasses.dataclass(frozen=True)
class SenderResponseDraft:
    to: list[str]
    subject: str
    body_markdown: str
    cc: list[str] = dataclasses.field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SenderResponseDraft":
        return cls(
            to=list(data.get("to", [])),
            cc=list(data.get("cc", [])),
            subject=str(data.get("subject", "Panda Gallery testing report reviewed")),
            body_markdown=str(data.get("body_markdown", "")),
        )


class OutlookGraphDraftClient:
    def __init__(self, config: GraphConfig):
        self.config = config

    def create_message_draft(self, draft: SenderResponseDraft) -> dict[str, Any]:
        payload = self._message_payload(draft)
        return self._graph_post(f"{self.config.user_path}/messages", payload)

    def send_existing_draft(self, message_id: str, *, human_approved: bool) -> None:
        if not human_approved:
            raise OutlookDraftError("Refusing to send Outlook message without explicit human approval.")
        self._graph_post(f"{self.config.user_path}/messages/{message_id}/send", {})

    def send_mail_single_call(self, draft: SenderResponseDraft, *, human_approved: bool) -> None:
        if not human_approved:
            raise OutlookDraftError("Refusing to send Outlook mail without explicit human approval.")
        payload = {"message": self._message_payload(draft), "saveToSentItems": True}
        self._graph_post(f"{self.config.user_path}/sendMail", payload)

    @staticmethod
    def _message_payload(draft: SenderResponseDraft) -> dict[str, Any]:
        return {
            "subject": draft.subject,
            "body": {"contentType": "Text", "content": draft.body_markdown},
            "toRecipients": [{"emailAddress": {"address": address}} for address in draft.to],
            "ccRecipients": [{"emailAddress": {"address": address}} for address in draft.cc],
        }

    def _graph_post(self, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        request = urllib.request.Request(
            GRAPH_ROOT + endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.config.access_token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                raw = response.read()
                if not raw:
                    return {}
                return json.loads(raw.decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise OutlookDraftError(f"Microsoft Graph HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise OutlookDraftError(f"Microsoft Graph network error: {exc}") from exc


def render_local_preview(draft: SenderResponseDraft) -> str:
    recipients = ", ".join(draft.to) or "(no recipient)"
    return f"To: {recipients}\nSubject: {draft.subject}\n\n{draft.body_markdown}\n"


def main() -> int:
    sample_path = os.environ.get("PG_SENDER_RESPONSE_DRAFT_JSON")
    if not sample_path:
        raise OutlookDraftError("Set PG_SENDER_RESPONSE_DRAFT_JSON to preview or create a draft.")
    with open(sample_path, "r", encoding="utf-8") as handle:
        draft = SenderResponseDraft.from_dict(json.load(handle))
    if os.environ.get("PG_GRAPH_DRY_RUN", "1") != "0":
        print(render_local_preview(draft))
        return 0
    client = OutlookGraphDraftClient(GraphConfig.from_env())
    created = client.create_message_draft(draft)
    print(json.dumps(created, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
