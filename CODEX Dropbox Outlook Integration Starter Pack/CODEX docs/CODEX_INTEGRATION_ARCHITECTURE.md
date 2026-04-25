# CODEX Integration Architecture - Dropbox + Outlook

## Plain-English Flow

1. Tester uploads a completed audit package to Dropbox.
2. The package includes screenshots, transcript text, metadata, results, and a completion marker.
3. The Audit Module detects the package.
4. The module downloads/copies the package into local intake staging.
5. The module validates completeness and hashes.
6. The module analyzes contents and creates categorized findings.
7. Darrin reviews/edits/approves findings.
8. The module drafts a sender response in Outlook/Microsoft Graph.
9. Darrin approves before any message is sent.
10. Approved findings become Claude Code task packages.

## Recommended Architecture

Use a small integration layer, not UI code directly calling cloud APIs.

Suggested modules later inside PG:

- dropbox_auth.py: OAuth/token handling.
- dropbox_intake.py: list/download/marker detection.
- audit_package_validator.py: package completeness and schema validation.
- outlook_auth.py: Microsoft Graph auth/token handling.
- outlook_response.py: draft creation and optional send after approval.
- audit_integration_service.py: orchestration and state transitions.

## Dropbox Intake Model

Use a completion marker such as _PACKAGE_READY.json. The module should ignore a folder until this marker is present. This prevents processing half-uploaded packages.

States:

- dropbox_waiting
- package_detected
- package_downloading
- package_downloaded
- completeness_check
- analysis_ready
- intake_error

## Outlook Response Model

First MVP should create Outlook drafts, not send automatically.

States:

- response_not_started
- response_draft_ready
- response_draft_created_in_outlook
- response_approved_to_send
- response_sent
- response_send_failed

## Human Approval Gates

Human approval is required before:

- granting OAuth access,
- transmitting sensitive data externally,
- sending an Outlook message,
- changing sharing settings,
- uploading real PHI-containing packages,
- archiving final sender communication.
