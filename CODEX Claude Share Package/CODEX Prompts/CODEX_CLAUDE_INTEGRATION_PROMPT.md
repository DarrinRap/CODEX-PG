# Claude Integration Prompt: Panda Gallery Audit MVP Starter Pack

Copy-ready prompt for Claude / Claude Code.

```text
Claude, work in C:\panda-gallery, but do not edit files yet until you have read the starter pack and given Darrin a concise implementation plan.

Goal:
Integrate the Codex Audit MVP Starter Pack into Panda Gallery as a local-only session packaging capability. Do not build the final dashboard yet. Do not add Dropbox, AI provider calls, email sending, or archive search in this task.

Read first from the share package when available:
- C:\CODEX PG\CODEX Claude Share Package\CODEX_READ_ME_FIRST.md
- C:\CODEX PG\CODEX Claude Share Package\CODEX Documents\CODEX_MASTER_SPEC_INDEX.md
- C:\CODEX PG\CODEX Claude Share Package\CODEX Documents\CODEX_SESSION_PACKAGE_SCHEMA_v1.md
- C:\CODEX PG\CODEX Claude Share Package\CODEX Documents\CODEX_AUDIT_ISSUE_SCHEMA_v1.md
- C:\CODEX PG\CODEX Claude Share Package\CODEX Documents\CODEX_TESTING_AUDIT_ARCHITECTURE_v1.md
- C:\CODEX PG\CODEX Claude Share Package\CODEX Documents\CODEX_AUDIT_DASHBOARD_UX_SPEC_v1.md
- C:\CODEX PG\CODEX Claude Share Package\CODEX Documents\CODEX_COMPLIANCE_ADDENDUM_TESTING_AUDIT_v1.md
- C:\CODEX PG\CODEX Claude Share Package\CODEX Documents\CODEX_MOCKUP_AND_SPEC_REFERENCES.md
- C:\CODEX PG\CODEX Claude Share Package\CODEX Documents\CODEX_CLAUDE_SCREENSHOT_UX_MOCKUP_REVIEW.md
- C:\CODEX PG\CODEX Claude Share Package\CODEX Desktop App Scaffold\CODEX_README.md
- C:\CODEX PG\CODEX Claude Share Package\CODEX Desktop App Scaffold\CODEX_pg_audit\package_builder.py
- C:\CODEX PG\CODEX Claude Share Package\CODEX Desktop App Scaffold\CODEX_pg_audit\validation.py
- C:\CODEX PG\CODEX Claude Share Package\CODEX Desktop App Scaffold\CODEX_pg_audit\issue_extraction.py
- C:\CODEX PG\CODEX Claude Share Package\CODEX Desktop App Scaffold\CODEX_pg_audit\review_records.py
- C:\CODEX PG\CODEX Claude Share Package\CODEX Desktop App Scaffold\CODEX_tests\test_package_builder.py
- C:\CODEX PG\CODEX Claude Share Package\CODEX Prompts\CODEX_CODEX_RESPONSE_TO_CLAUDE_STAGE1_ALIGNMENT.md

Original source copies also exist under `C:\CODEX PG\CODEX Canonical Specs`, `C:\CODEX PG\CODEX Desktop App`, and `C:\CODEX PG\CODEX Audit MVP Starter Pack`, but the share package is the handoff contract.

Also inspect current live PG outputs read-only:
- C:\panda-gallery\workflows\results_latest.json, if present
- C:\panda-gallery\workflows\screenshots, if present
- C:\panda-gallery\workflows\results_archive, if present
- C:\panda-gallery\scripts\transcribe_latest.py
- C:\panda-gallery\results_writer.py
- C:\panda-gallery\workflow_capture.py
- C:\panda-gallery\instruction_pane.py


Design and quality gate:
- Match the redesign direction Claude already developed for Panda Gallery v4 and that Codex reviewed. Use C:\CODEX PG\CODEX Claude UX Mockup Review\CODEX_CLAUDE_SCREENSHOT_UX_MOCKUP_REVIEW.md and the shared full-size mockups as the visual target for any UI-adjacent choices.
- If implementation details conflict with that redesign, the MVP boundary, evidence integrity, privacy/compliance, testability, or maintainability, stop and notify Darrin before editing further.
- Push back clearly on rushed, risky, or over-broad instructions. Excellence takes time; do not trade correctness or audit integrity for speed.
- Do not claim Panda Gallery v4 is complete unless the agreed v4 scope has been implemented, tested, visually checked, and accepted.

Scope for the first integration task:
- Create a new top-level `C:\panda-gallery\codex_audit\` package using the tested Codex scaffold as reference.
- It should read existing PG testing/session outputs and generate a package folder containing session_package_manifest.json, source files, evidence files, derived ai_extraction_input_v1.json, package_summary.md, and logs.
- It should preserve existing PG outputs; do not mutate results_latest.json or screenshots.
- It should generate stable evidence IDs and step records.
- It should hash copied files and record missing sources.
- It should run locally without Dropbox, real AI, or email configuration.
- Add a single narrow `panda_gallery.py --build-audit-package` entry point that routes to `codex_audit.cli.main`.
- Hardcode output to `C:\CODEX PG\CODEX Audit Prototype\CODEX Session Packages\`; do not expose an arbitrary `--out` path to end users.
- Keep Stage 1 package IDs deterministic as `pkg_local_<session_id>`; revisit timestamp/random package IDs before Stage 2 or production history requirements.

Do not:
- Do not build the final audit dashboard.
- Do not add Dropbox upload.
- Do not call an AI provider.
- Do not send email.
- Do not process real PHI.
- Do not rewrite instruction_pane.py, results_writer.py, workflow_capture.py, main_window.py, or panda_gallery.py wholesale. The only expected panda_gallery.py change is one argparse flag and narrow route.
- Do not mix unrelated v4 clinical UI work into this task.

Implementation requirements:
- Keep the package builder mostly pure and testable.
- Prefer a small new module/script over expanding large UI files.
- Use the starter-pack builder and validator as a reference, not as pasted code if existing PG patterns suggest a cleaner local shape.
- Add focused tests or a smoke command that can package a synthetic/local test session.
- Include a validation path that catches missing evidence IDs, broken file hashes, and issue/evidence mismatches.
- Keep paths and schemas versioned.
- Keep package output local-only for this task.

Acceptance criteria:
- A local packaging command or callable function exists in C:\panda-gallery.
- It can package a synthetic or existing non-PHI PG testing session.
- Generated session_package_manifest.json follows pg.session_package.v1.
- Generated evidence objects have stable evidence_id values and valid hashes.
- Generated ai_extraction_input_v1.json contains steps, evidence, transcript references when available, and extraction rules.
- Validation passes for the generated package.
- Existing PG results/screenshots are not modified.
- The implementation summary names every changed file.
- `C:\panda-gallery\workflows\` is byte-identical before and after the smoke run.

Verification:
- Run the new package builder against a safe sample/non-PHI session.
- Run the validator or equivalent checks.
- Show the generated package path.
- Show validation result.
- Confirm git status before and after.
- Confirm `C:\panda-gallery\workflows\` was not modified.

Handoff:
At the end, report:
- files changed,
- package path generated,
- tests/smoke checks run,
- validation result,
- behavior intentionally left out,
- risks/follow-up work.
```

## Codex Notes For Darrin

This prompt intentionally asks Claude to keep Stage 1 narrow: a local-only CLI producer in Panda Gallery. The dashboard is Stage 2. Dropbox, real AI, live email, and PHI workflow remain deferred until explicit compliance and product decisions.
