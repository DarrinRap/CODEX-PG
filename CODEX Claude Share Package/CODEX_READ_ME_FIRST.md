# CODEX Claude Share Package

This folder collects the Panda Gallery Codex materials that are useful to share with Claude.

Use this folder when you want Claude to see the complete current Codex-side planning, specs, starter code, sample data, and full-size mockup images without hunting through multiple directories.

## Folder To Give Claude

`C:\CODEX PG\CODEX Claude Share Package`

If Claude has local file access, give it that path.

If Claude does not have local file access, zip this folder and upload the zip.

## Read Order For Claude

Tell Claude to read these first:

1. `CODEX Documents\CODEX_MASTER_SPEC_INDEX.md`
2. `CODEX Documents\CODEX_SESSION_PACKAGE_SCHEMA_v1.md`
3. `CODEX Documents\CODEX_AUDIT_ISSUE_SCHEMA_v1.md`
4. `CODEX Documents\CODEX_TESTING_AUDIT_ARCHITECTURE_v1.md`
5. `CODEX Documents\CODEX_AUDIT_DASHBOARD_UX_SPEC_v1.md`
6. `CODEX Documents\CODEX_COMPLIANCE_ADDENDUM_TESTING_AUDIT_v1.md`
7. `CODEX Documents\CODEX_AUDIT_MVP_STARTER_PACK_README.md`
8. `CODEX Prompts\CODEX_CLAUDE_INTEGRATION_PROMPT.md`
9. `CODEX Documents\CODEX_MOCKUP_AND_SPEC_REFERENCES.md`
10. `CODEX Documents\CODEX_CLAUDE_SCREENSHOT_UX_MOCKUP_REVIEW.md`
11. `CODEX Documents\CODEX_CLAUDE_CODE_QUALITY_RECOMMENDATIONS.md`

## What Is Included

### CODEX Documents

Canonical specs, code quality recommendations, UX review, project orientation, spec review, handoff files, and storyboard notes.

### CODEX Prompts

Copy-ready Claude prompts:

- `CODEX_CLAUDE_HANDOFF_PROMPT_STAGED.md` for review/planning handoff.
- `CODEX_CODEX_RESPONSE_TO_CLAUDE_STAGE1_ALIGNMENT.md` for Codex response to Claude Stage 1 alignment.
- `CODEX_CLAUDE_STAGE1_APPROVAL_PROMPT.md` if Darrin approves Claude to implement Stage 1.
- `CODEX_CLAUDE_INTEGRATION_PROMPT.md` for later local package-builder integration into `C:\panda-gallery`.

### CODEX Sample Code

Reference Python package builder and validator.

### CODEX Sample JSON

Important sample JSON files extracted from the starter pack for quick inspection.

### CODEX Sample Package

A complete synthetic sample source session and generated sample package, including evidence image placeholders and package layout.

### CODEX Full Size Mockup Images

Full-size PNG renders, not contact sheets.

- `CODEX Audit Testing`: Codex-created audit/testing mockups and storyboard renders.
- `CODEX Claude UX Review`: full-size renders of Claude's 32 UX mockups.

### CODEX Source HTML Mockups

Original HTML mockups copied into one place:

- Codex audit/testing HTML mockups.
- Codex storyboard HTML.
- Claude original HTML mockups flattened into one CODEX-prefixed folder.

## What Is Not Included

This package intentionally does not include:

- `C:\CODEX PG\CODEX CLAUDE PG DATA` because it is a large local-only copy of Claude's source tree.
- `C:\CODEX PG\CODEX Playwright Browsers` because it contains large downloaded browser binaries.
- Real patient data or PHI.
- Dropbox credentials, AI keys, email credentials, or final dashboard code.

## Best Claude Instruction

Paste this to Claude:

```text
Please review the shared Codex package at:
C:\CODEX PG\CODEX Claude Share Package

Read CODEX_READ_ME_FIRST.md first, then follow the read order. Do not edit C:\panda-gallery yet. First summarize what you understand, identify risks/missing files, and recommend the safest next staged implementation step.
```


## Claude Quality Gate

Claude should match the redesign direction Claude already developed and that Codex reviewed in `CODEX_CLAUDE_SCREENSHOT_UX_MOCKUP_REVIEW.md`. Treat that redesign as the visual target unless Darrin explicitly changes direction.

Claude should notify Darrin before implementing if the plan conflicts with the redesign, the MVP boundary, evidence integrity, privacy/compliance, testability, or maintainability. Push back clearly on rushed or risky implementation choices instead of silently accepting them.

## Important Boundary

`C:\panda-gallery` is the live Panda Gallery / Claude source folder. Codex treats it as read-only unless Darrin explicitly says otherwise.
