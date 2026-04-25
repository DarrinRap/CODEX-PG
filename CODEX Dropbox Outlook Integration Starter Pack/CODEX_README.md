# CODEX Dropbox + Outlook Integration Starter Pack

Purpose: prepare Claude for the future Panda Gallery Audit Module integrations without touching C:\panda-gallery.

This pack covers:

- Dropbox intake architecture for incoming audit packages.
- Package completeness and completion-marker workflow.
- Outlook/Microsoft Graph sender-response drafting.
- Python reference clients using placeholders and environment variables.
- Safety/approval rules for messages and sensitive data.

This pack does not contain real credentials, real tokens, or PHI.

## Recommended Read Order

1. CODEX docs/CODEX_INTEGRATION_ARCHITECTURE.md
2. CODEX docs/CODEX_DROPBOX_INTAKE_SPEC.md
3. CODEX docs/CODEX_OUTLOOK_RESPONSE_SPEC.md
4. CODEX docs/CODEX_SECURITY_APPROVALS_AND_SECRETS.md
5. CODEX docs/CODEX_CLAUDE_IMPLEMENTATION_PROMPT.md
6. CODEX scripts/dropbox_intake_client.py
7. CODEX scripts/outlook_graph_draft_client.py
8. CODEX scripts/audit_integration_orchestrator.py

## MVP Philosophy

Dropbox intake may be automated after credentials are configured. Outlook should create drafts first. Actual sending requires explicit human approval at action time.
