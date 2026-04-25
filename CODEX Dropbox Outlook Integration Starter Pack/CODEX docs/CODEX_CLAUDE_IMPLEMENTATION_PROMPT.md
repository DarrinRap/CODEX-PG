# CODEX Claude Implementation Prompt - Dropbox + Outlook

Claude, this pack prepares the Dropbox intake and Outlook draft-response integrations for Panda Gallery Audit Module.

Read first:

1. CODEX docs/CODEX_INTEGRATION_ARCHITECTURE.md
2. CODEX docs/CODEX_DROPBOX_INTAKE_SPEC.md
3. CODEX docs/CODEX_OUTLOOK_RESPONSE_SPEC.md
4. CODEX docs/CODEX_SECURITY_APPROVALS_AND_SECRETS.md
5. CODEX scripts/dropbox_intake_client.py
6. CODEX scripts/outlook_graph_draft_client.py
7. CODEX scripts/audit_integration_orchestrator.py

Implementation boundaries:

- Do not edit C:\panda-gallery until Darrin approves a specific task.
- Start with local/synthetic package simulation.
- Add Dropbox polling before webhooks.
- Create Outlook drafts before any send workflow.
- Never store credentials in source.
- Never send email automatically.
- Keep all real external actions behind explicit approval.

First suggested slice:

1. Build config model for Dropbox incoming folder and local staging path.
2. Implement dry-run package detection against a local sample folder.
3. Add Dropbox client only behind env vars.
4. Build response draft JSON/Markdown locally.
5. Add Graph draft creation only after OAuth setup is explicitly approved.

Definition of done:

- Sample orchestrator can process a synthetic package.
- Dropbox client supports list/download/marker detection in code.
- Outlook client supports draft creation in code but does not send by default.
- Docs clearly state required scopes, env vars, errors, and approval gates.
