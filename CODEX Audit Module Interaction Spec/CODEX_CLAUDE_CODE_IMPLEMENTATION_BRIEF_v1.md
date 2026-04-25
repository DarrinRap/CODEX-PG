# CODEX Claude Code Implementation Brief - Audit Module Interaction Spec v1

Read first:

1. C:\CODEX PG\CODEX Audit Module Interaction Spec\CODEX_AUDIT_MODULE_INTERACTION_SPEC_v1.md
2. C:\CODEX PG\CODEX Canonical Specs\CODEX_SESSION_PACKAGE_SCHEMA_v1.md
3. C:\CODEX PG\CODEX Canonical Specs\CODEX_AUDIT_ISSUE_SCHEMA_v1.md
4. C:\CODEX PG\CODEX Audit MVP Starter Pack\CODEX scripts\audit_mvp_reference_builder.py
5. C:\CODEX PG\CODEX Audit MVP Starter Pack\CODEX scripts\validate_audit_mvp_contracts.py
6. C:\CODEX PG\CODEX Audit UX Fullscreen Walkthrough PG Aligned\CODEX_audit_ux_fullscreen_walkthrough_PG_aligned_v2.html

Task goal:

Implement the first local-only Audit Module vertical slice in C:\panda-gallery after reading the spec. Do not start with upload, AI provider calls, email sending, or final dashboard work.

Core workflow:

Testing Audit Panel -> Workflow Capture -> Region capture Review -> FAIL Detail Panel -> Session Package -> Claude Handoff

Implementation constraints:

- Match PG's existing dark testing UI vocabulary and colors.
- Reuse existing testing, workflow capture, region capture, and results writer code where practical.
- Keep evidence IDs stable and deterministic within a package.
- Do not delete evidence files during normal discard; mark `discarded: true`.
- Do not mutate source testing artifacts while packaging. Copy them into a package folder.
- Disable Claude Handoff until package validation passes.
- Keep the first implementation local-only.

Suggested first coding slice:

1. Add or identify an Audit Panel entry point under the existing Testing menu.
2. Implement read-only scan/load of the latest completed testing session.
3. Add a minimal audit state model with the state names from the spec.
4. Wrap existing screenshot/region capture outputs into evidence objects.
5. Add Region Review actions: save evidence, recapture, discard.
6. Add FAIL detail draft validation: observed, expected, category, priority, evidence IDs.
7. Integrate local package builder and validator.
8. Generate handoff markdown only after validation passes.

Definition of done for first slice:

- One sample session can be loaded.
- One step can be marked PASS or FAIL.
- A FAIL can link full screenshot and/or region screenshot evidence.
- A local package validates with zero errors.
- A Claude handoff markdown file is generated.
- No upload, email, AI API, or live PHI handling is introduced.

Do not broaden scope without asking Darrin.
