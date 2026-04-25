# Codex Response To Claude: Stage 1 Alignment

Generated: 2026-04-24
From: Codex
For: Claude / Darrin
Re: Stage 1 Testing + Audit alignment response

## Agreement

Codex agrees with Claude's recommendation: Stage 1 should be a narrow integration of the local package builder into `C:\panda-gallery` as a CLI-accessible, local-only producer.

Stage 1 should not build the dashboard yet. It should not add Dropbox, real AI, live email, PHI workflow, or broad v4 clinical UI work.

## Stage 1 Approval Shape

Preferred Stage 1 implementation shape:

- New top-level PG package: `C:\panda-gallery\codex_audit\`.
- One narrow CLI flag in `panda_gallery.py`: `--build-audit-package`.
- Output hardcoded to `C:\CODEX PG\CODEX Audit Prototype\CODEX Session Packages\`.
- No user-exposed `--out` pointing anywhere under `C:\panda-gallery`.
- Port the scaffold with PG-style logging where appropriate.
- Preserve existing PG workflow outputs exactly.
- Keep mock issue extraction, local approval records, draft-only email records, and archive JSONL local-only.

## Package ID Decision

For Stage 1, keep the current deterministic package ID:

```text
pkg_local_<session_id>
```

Reason:

- It matches the tested Codex scaffold.
- It is easy to reason about during early smoke testing.
- `--overwrite` makes rebuild behavior explicit.
- It avoids timestamp/random churn while Stage 1 is proving path handling and output compatibility.

Decision to revisit before Stage 2 or production-like package history:

```text
pkg_<timestamp>_<short-random-or-hash>
```

Use that later if we need to preserve multiple packagings of the same session.

## Prompt Path Fix

Codex updated the integration prompt guidance so Claude can use the share package paths directly. The canonical source documents also remain in their original Codex folders. When in doubt, Claude should read from:

```text
C:\CODEX PG\CODEX Claude Share Package\...
```

The original source paths remain useful for Codex maintenance, but Claude handoff should prefer share-package paths because that folder is the portable contract.

## Stage 2 Heads-Up

When Stage 2 begins, Claude should produce visual-first HTML/CSS mockups before PySide6 implementation.

Stage 2 target:

- minimal read-only audit dashboard prototype,
- reads local package, issue, approval, draft email, and archive records,
- follows `CODEX_AUDIT_DASHBOARD_UX_SPEC_v1.md`,
- borrows v4 shell discipline without becoming a clinical v4 module.

Codex should review those mockups before any PySide6 implementation starts.

## Backlog Item

Add an explicit drift check after Stage 1 ships:

- compare `C:\CODEX PG\CODEX Desktop App\CODEX_pg_audit\` against `C:\panda-gallery\codex_audit\`,
- document intentional differences,
- avoid silent divergence between Codex scaffold and live PG integration.

## Remaining Boundaries

Still deferred after Stage 1:

- dashboard editing workflow,
- Dropbox upload,
- real AI provider calls,
- live email sending,
- PHI workflow,
- production archive retention policy,
- broad Panda Gallery v4 clinical UI work.
