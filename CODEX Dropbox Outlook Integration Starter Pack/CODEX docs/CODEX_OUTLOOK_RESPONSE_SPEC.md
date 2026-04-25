# CODEX Outlook / Microsoft Graph Response Spec

## Official API Concepts Used

Outlook mail is accessed through Microsoft Graph. Messages can be created as drafts or sent in one operation. For Audit MVP, create drafts first and require Darrin approval before sending.

Microsoft Graph supports delegated permissions, where the app acts on behalf of a signed-in user, and application permissions, where the app acts without a signed-in user. For this project, start with delegated permissions unless there is a strong reason and admin approval for app-only access.

## Recommended Permissions

For draft creation and editing:

- Mail.ReadWrite delegated

For sending after explicit approval:

- Mail.Send delegated

If using a shared mailbox, shared-mail scopes or mailbox-specific policies may be required. Avoid broad application permissions unless absolutely necessary.

## Response Workflow

1. Audit Module drafts sender response from approved findings.
2. Darrin reviews and edits the response inside PG.
3. The module creates an Outlook draft through Microsoft Graph.
4. Darrin reviews the actual Outlook draft if desired.
5. Sending remains disabled unless Darrin explicitly approves.
6. On approval, the module sends the existing draft or instructs the user to send manually.

## Draft Message Object

Draft should include:

- to recipients
- subject
- HTML or text body
- optional links to package/evidence if safe
- no raw PHI unless explicitly approved

## Attachment Policy

Avoid attaching large evidence files to outbound mail in MVP. Prefer references to the local/approved package or summary. If attachments are later needed, use Graph attachment/upload-session patterns and PHI review.

## Error Handling

- 401 unauthorized: refresh/sign-in required.
- 403 insufficient permissions: show missing Graph scope.
- 404 mailbox/message not found: draft may have been moved/deleted.
- 413 payload too large: remove attachments or use upload session.
- 429 throttled: obey Retry-After/backoff.
- 5xx service error: retry with backoff and preserve local draft.

## Human Approval Rule

Creating a draft writes to Outlook. Sending is representational communication to a third party and requires explicit final approval at action time.
