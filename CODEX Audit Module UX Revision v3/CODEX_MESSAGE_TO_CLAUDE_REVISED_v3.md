# CODEX Message To Claude - Revised Audit Module v3

Claude, the Audit Module direction has been revised. The product is not primarily a local testing dashboard. It is an intelligent intake and triage system for Panda Gallery testing submissions arriving through Dropbox.

Read first:

1. C:\CODEX PG\CODEX Audit Module UX Revision v3\CODEX_AUDIT_MODULE_UX_REVISION_v3.md
2. C:\CODEX PG\CODEX Audit Module UX Revision v3\CODEX_AUDIT_MODULE_INTERACTION_SPEC_v3.md
3. C:\CODEX PG\CODEX Audit Module UX Revision v3\CODEX_audit_module_ux_revision_v3.html

What we need:

- Keep the surface minimal and intuitive.
- Show the main actions only.
- Put raw logs, JSON, hashes, duplicate candidates, and model diagnostics into collapsible panels.
- Use urgency colors consistently: P0 red, P1 peach, P2 amber, P3 gray, verified green.
- Treat Dropbox intake as the front door.
- Treat automated analysis as draft/recommendation until Darrin approves.
- Generate sender response drafts and Claude Code task packages, but keep human approval gates.

Do not build upload, email sending, or AI provider calls until the local scaffold and contracts are stable.
