# CODEX Official Source Notes - Dropbox + Outlook

These notes summarize the official references used for this starter pack.

## Dropbox

- OAuth guide: https://developers.dropbox.com/oauth-guide
  - Dropbox uses OAuth 2.0.
  - Desktop/background apps should use code flow with PKCE and refresh tokens for offline/background access.
  - Access tokens are short-lived; refresh tokens obtain new access tokens.

- File access guide: https://developers.dropbox.com/dbx-file-access-guide
  - Dropbox files/folders have metadata.
  - Folder listing returns pagination with has_more and cursor.
  - Continue listing with list_folder/continue.
  - File IDs are more stable than paths when files may move.

- Detecting changes guide: https://developers.dropbox.com/detecting-changes-guide
  - Apps can detect changes with list_folder cursors, longpolling, or webhooks.
  - MVP recommendation here is polling/cursors first; webhooks later.

- Error handling guide: https://developers.dropbox.com/error-handling-guide
  - Handle HTTP and API errors explicitly.
  - Rate limits and malformed requests need clear recovery paths.

## Microsoft Graph / Outlook

- Outlook create/send messages overview: https://learn.microsoft.com/en-us/graph/outlook-create-send-messages
  - Messages can be created/sent in one call or created as drafts and sent later.
  - Drafts are saved in the Drafts folder by default.

- Send mail process overview: https://learn.microsoft.com/graph/outlook-things-to-know-about-send-mail
  - sendMail returns 202 Accepted when accepted for processing.
  - Exchange/Outlook processing continues after the API response.

- Create message API: https://learn.microsoft.com/en-us/graph/api/user-post-messages?view=graph-rest-1.0
  - Creates a draft message.
  - Sending can be a subsequent operation.

- Graph permissions overview: https://learn.microsoft.com/en-us/graph/permissions-overview
  - Delegated permissions act on behalf of a signed-in user.
  - Application permissions act as the application itself.

- Graph permissions reference: https://learn.microsoft.com/en-us/graph/permissions-reference
  - Mail.ReadWrite supports creating/updating drafts.
  - Mail.Send supports sending mail.

## Design Decision From Sources

Dropbox intake can be automated after OAuth/token configuration and with least-privilege folder access.

Outlook response generation should start by creating drafts. Sending must remain a separate, explicitly approved action.
