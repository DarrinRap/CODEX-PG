# CODEX Security, Approvals, And Secrets

## No Secrets In Source

Never commit:

- Dropbox refresh tokens
- Dropbox app secrets
- Microsoft client secrets
- Microsoft refresh/access tokens
- patient data or PHI
- real sender/recipient lists

Use environment variables, Windows Credential Manager, or a secure local secrets store.

## Suggested Environment Variables

Dropbox:

- PG_DROPBOX_APP_KEY
- PG_DROPBOX_APP_SECRET, only if using confidential app flow
- PG_DROPBOX_REFRESH_TOKEN
- PG_DROPBOX_INCOMING_FOLDER

Microsoft Graph:

- PG_GRAPH_TENANT_ID
- PG_GRAPH_CLIENT_ID
- PG_GRAPH_ACCESS_TOKEN for local development only
- PG_GRAPH_DRAFT_MAILBOX, optional later

## Approval Gates

Ask Darrin before:

- initiating OAuth sign-in or granting scopes,
- storing long-lived refresh tokens,
- uploading files externally,
- sending Outlook email,
- including sensitive data in messages,
- changing Dropbox sharing permissions,
- processing real PHI.

## Data Minimization

Sender response drafts should summarize findings. Do not include raw transcript, full screenshots, or PHI unless explicitly approved and necessary.

## Local Development

Use synthetic packages first. The sample code in this pack is designed to run in dry-run/sample mode unless credentials are explicitly provided.
