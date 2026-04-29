# CODEX Current Handoff

Last updated: 2026-04-24 18:48:03 -07:00

## Current Status

Completed:

- Read the PG Testing + Audit MVP spec doc.
- Created separate Codex workspace: `C:\CODEX PG`.
- Established workspace rule: all Codex-created folders stay inside `C:\CODEX PG` and start with `CODEX`.
- Created initial visual mockups in `C:\CODEX PG\CODEX Visual Mockups`.
- Created detailed step-by-step storyboard in `C:\CODEX PG\CODEX Interface Storyboards`.
- Created project memory and handoff docs in `C:\CODEX PG\CODEX Docs`.
- Created backup automation script in `C:\CODEX PG\CODEX Automation`.
- Initialized local git repository at `C:\CODEX PG`.
- Ran local git backup commits successfully.

Not started yet:

- Real Python desktop app scaffold.
- PySide6 implementation.
- Unit tests.
- Packaging/session backend modules.
- Dropbox integration.
- AI issue extraction service boundary.
- GitHub remote setup and cloud push.

## Best Next Steps

1. Review `CODEX_step_by_step_ui_storyboard_v1.html` visually.
2. Decide which screen becomes the first real PySide6 implementation target.
3. Create `C:\CODEX PG\CODEX Desktop App` for Python source code.
4. Scaffold a modern PySide6 app with typed modules and reusable UI components.
5. Connect the backup script to a GitHub remote once Darrin provides a repository URL.

## Backup Status

Local git repository has been initialized at `C:\CODEX PG`.

Recent local backup commits:

- `7c42f29` - backup script remote-detection fix committed.
- `740672d` - initial Codex project files committed.

Current branch: `main`.

GitHub remote status: no `origin` remote configured yet, so cloud push is pending a GitHub repository URL.

To attach GitHub and push:

`powershell -ExecutionPolicy Bypass -File "C:\CODEX PG\CODEX Automation\CODEX_backup_to_github.ps1" -RemoteUrl "https://github.com/OWNER/REPO.git"`

After the remote is configured, normal backups can run with:

`powershell -ExecutionPolicy Bypass -File "C:\CODEX PG\CODEX Automation\CODEX_backup_to_github.ps1"`

## New Chat Startup

Tell Codex:

`Read C:\CODEX PG\CODEX Docs\CODEX_PROJECT_MEMORY.md and C:\CODEX PG\CODEX Docs\CODEX_CURRENT_HANDOFF.md first.`

Then continue from this handoff.

## Important Open Question

A GitHub remote does not exist yet for `C:\CODEX PG`. Darrin should provide either an existing GitHub repository URL or details/permission for creating a new private GitHub repository outside this environment.

## GitHub Sync Status

Updated: 2026-04-24 18:51:53 -07:00

GitHub remote is configured and pushed successfully.

- Repository: `https://github.com/DarrinRap/CODEX-PG.git`
- Local branch: `main`
- Tracking branch: `origin/main`
- Normal backup command: `powershell -ExecutionPolicy Bypass -File "C:\CODEX PG\CODEX Automation\CODEX_backup_to_github.ps1"`

## Panda Gallery Read-Only Reference Status

Updated: 2026-04-24 18:56:29 -07:00

Codex read-only reference access is documented for `C:\panda-gallery`.

- Policy: `C:\CODEX PG\CODEX Panda Gallery Readonly Reference\CODEX_READONLY_POLICY.md`
- Inventory summary: `C:\CODEX PG\CODEX Panda Gallery Readonly Reference\CODEX_PANDA_GALLERY_INVENTORY.md`
- Inventory CSV: `C:\CODEX PG\CODEX Panda Gallery Readonly Reference\CODEX_PANDA_GALLERY_FILE_INDEX.csv`
- Indexed files: 6,249

Important: do not write into `C:\panda-gallery`; all Codex-derived files belong under `C:\CODEX PG`.

<!-- CODEX_AUTOMATED_HANDOFF_START -->
## Automated Handoff Snapshot

Generated: 2026-04-28 11:54:28 -07:00
Mode: `Handoff`

- Last automated handoff: `C:\CODEX PG\CODEX Docs\CODEX_LAST_AUTOMATED_HANDOFF.md`
- Fresh chat resume prompt: `C:\CODEX PG\CODEX Docs\CODEX_RESUME_PROMPT.txt`
- GitHub repo: `https://github.com/DarrinRap/CODEX-PG.git`
- Current branch: `main`
- Origin: `https://github.com/DarrinRap/CODEX-PG.git`

Use trigger word `CODEX RESUME PG` in a fresh chat and paste the contents of `CODEX_RESUME_PROMPT.txt` if needed.
<!-- CODEX_AUTOMATED_HANDOFF_END -->

## PAH Speedup Task Update

Updated: 2026-04-28 14:52:14 -07:00

Current PAH compact cockpit speedup slice is implemented and smoke-tested.

- Reopened the read-only PAH action-console lane after Darrin resumed PAH development.
- Tightened contract implementation in `C:\CODEX PG\CODEX Agent Hub\CODEX_agent_hub.py`: actual git last-commit metadata, schema-ordered action queue, and threshold-derived wake safety text.
- Tightened `C:\CODEX PG\CODEX Agent Hub\CODEX_agent_hub_ui.html`: UI now preserves payload queue order after filtering/search, derives the stale threshold label from `cockpit_state.stale_unread_threshold_seconds`, and includes Enter/Ctrl+R in keyboard behavior/help.
- Added smoke coverage in `C:\CODEX PG\CODEX Agent Hub\CODEX_run_smoke_tests.py` for queue ordering, git commit metadata, and stale-threshold label derivation.
- Verification: `python "C:\CODEX PG\CODEX Agent Hub\CODEX_run_smoke_tests.py"` passed.
- Live API spot-check: current-code PAH server started at `http://127.0.0.1:8766`; `/api/cockpit` returned populated git last-commit metadata, `stale_unread_threshold_seconds: 60`, and wake-first action queue rows.
- Completion report written to `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\20260428_145214_CODEX_to_CLAUDE_pah_compact_cockpit_speedup_complete.md`.

Boundary: still read-only. No compose/send pipeline, standing permission grant, watcher startup, or `C:\panda-gallery` writes were added.

## Relay Health Checker

Updated: 2026-04-28 15:06:28 -07:00

Added read-only relay health checker:

`C:\CODEX PG\CODEX Automation\CODEX_relay_health_check.ps1`

Purpose: fast validation of the compact relay protocol before rereading mailbox history.

It checks:

- required index/authority files
- active queue state labels and duplicate thread rows
- source/completion paths
- stale `new`, `in_progress`, or `blocked` rows
- newer CODEX Inbox mail not reflected in index/authority
- PAH read-state unread incoming mail
- recent Darrin-gated messages

Verification:

- `& "C:\CODEX PG\CODEX Automation\CODEX_relay_health_check.ps1" -NoFail` returned `Status: OK`.
- `& "C:\CODEX PG\CODEX Automation\CODEX_relay_health_check.ps1" -Json -NoFail | ConvertFrom-Json` parsed successfully.

## Relay Health In PAH Diagnostics

Updated: 2026-04-28 15:12:24 -07:00

Wired the relay health checker into PAH diagnostics.

- `C:\CODEX PG\CODEX Agent Hub\pah_diagnostics\checks.py` now runs `CODEX_relay_health_check.ps1 -Json -NoFail` as a read-only `relay_health` diagnostic check.
- `C:\CODEX PG\CODEX Agent Hub\CODEX_agent_hub.py` exposes compact relay status at `diagnostics.relay_health` in the read-only cockpit payload.
- `C:\CODEX PG\CODEX Agent Hub\CODEX_agent_hub_ui.html` shows Relay Health as its own Diagnostics queue row.
- `C:\CODEX PG\CODEX Agent Hub\CODEX_run_smoke_tests.py` covers the relay diagnostic and compact payload field.
- `C:\CODEX PG\CODEX Canonical Specs\CODEX_PAH_COMPACT_COCKPIT_READONLY_SCHEMA_v1.md` documents `diagnostics.relay_health`.

Verification:

- `python "C:\CODEX PG\CODEX Agent Hub\CODEX_run_smoke_tests.py"` passed.
- Standalone checker still returned `Status: OK`.
- Direct `cockpit_payload()` check returned `diagnostics.relay_health.ok: True`.
- Refreshed current-code PAH verification server at `http://127.0.0.1:8766`; `/api/cockpit` returned `diagnostics.relay_health.ok: true`.

## Relay Cache / Latest Mail Cursors

Updated: 2026-04-28 15:20:07 -07:00

Added a cache/cursor layer to speed repeated relay checks.

- `C:\CODEX PG\CODEX Automation\CODEX_relay_health_check.ps1` now supports `-UpdateCache` and `-NoCache`.
- Cache path: `C:\CODEX PG\CODEX Agent Hub\CODEX state\CODEX_relay_health_cache.local.json` (ignored by git).
- Cache stores parsed recent-mail frontmatter plus newest-mail cursors for `CODEX Inbox`, `CLAUDE Inbox`, and `CODEX_CLAUDE_CODE Inbox`.
- PAH diagnostics now calls the checker with `-UpdateCache` so normal cockpit refreshes keep the cache warm.
- Compact cockpit payload includes `diagnostics.relay_health.cache`.

Verification:

- Cold cache update: `0` hits / `38` misses, cache written.
- Warm check: `38` hits / `0` misses.
- `python "C:\CODEX PG\CODEX Agent Hub\CODEX_run_smoke_tests.py"` passed.

## Local Claude PG Data Copy

Created: 2026-04-24 19:06:20 -07:00

- Source: `C:\panda-gallery`
- Destination: `C:\CODEX PG\CODEX CLAUDE PG DATA`
- Files copied: 6,249
- Size copied: approximately 2.34 GB
- Copy method: `robocopy` with hidden files and empty directories included, junctions excluded.
- GitHub backup status: destination is intentionally ignored by `.gitignore` and is local-only.
- Copy log: `C:\CODEX PG\CODEX Backup Logs\CODEX_copy_claude_pg_data_20260424_190538.log`

## Specification Review Completed

Completed: 2026-04-24 19:13:05 -07:00

- Review folder: `C:\CODEX PG\CODEX Specification Review`
- Main report: `C:\CODEX PG\CODEX Specification Review\CODEX_SPECIFICATION_REVIEW_REPORT.md`
- Manifest: `CODEX_SPEC_REVIEW_MANIFEST.csv`
- Heading digest: `CODEX_SPEC_HEADING_DIGEST.md`
- External MVP DOCX extract: `CODEX_PG_TESTING_AUDIT_MVP_SPEC_EXTRACT.txt`

Key conclusion: the spec corpus is rich but fragmented. Next best step is to create a master spec index and canonical Testing + Audit data contracts before implementation.

## Canonical Testing + Audit Specs Started

Created: 2026-04-24 20:20:52 -07:00

- Folder: `C:\CODEX PG\CODEX Canonical Specs`
- `CODEX_MASTER_SPEC_INDEX.md`: maps current, historical, superseded, implementation, and process specs; separates PG Core v4 from Testing + Audit MVP v1.
- `CODEX_SESSION_PACKAGE_SCHEMA_v1.md`: defines package manifest, package states, source records, evidence IDs, transcript refs, upload marker, integrity, and local vertical slice.
- `CODEX_AUDIT_ISSUE_SCHEMA_v1.md`: defines AI issue extraction output, category/priority taxonomy, review lifecycle, approval records, email draft records, and archive search records.

Immediate next best step:

1. Draft `CODEX_TESTING_AUDIT_ARCHITECTURE_v1.md`.
2. Then build the smallest local-only package generator under `C:\CODEX PG`, using `C:\panda-gallery` only as read-only input.

## Codebase Orientation Completed

Completed: 2026-04-24 19:21:32 -07:00

Codex read the live C:\panda-gallery runtime modules, current specs, current handoff/bugs, and Codex spec review artifacts. Durable self-summary written here:

- C:\CODEX PG\CODEX Codebase Orientation\CODEX_PG_CODEBASE_ORIENTATION_SUMMARY.md

Important result: PG v4.23 already implements guided test results, full workflow capture/audio/transcription, and #130 Shift+F12 region capture with session JSON integration. The Testing + Audit MVP should next define package/evidence/AI issue/approval/archive schemas before implementation.

## Claude Code Quality Recommendations Document

Created: 2026-04-24 19:41:06 -07:00

- Folder: C:\CODEX PG\CODEX Claude Review Recommendations
- Main document: C:\CODEX PG\CODEX Claude Review Recommendations\CODEX_CLAUDE_CODE_QUALITY_RECOMMENDATIONS.md
- Purpose: detailed, Claude-facing recommendations for Panda Gallery code quality, modernization, 6 C's evaluation, architecture boundaries, testing strategy, UI modernization, audit MVP data contracts, and prompt-ready implementation tasks.
- Basis: read-only review of live C:\panda-gallery version 4.23 plus existing specs, bugs, handoff, style guidance, and Codex review artifacts.
- File verified: 1,030 lines, no hidden control characters detected.

Recommended use: share this Markdown file directly with Claude before asking for Panda Gallery modernization work. It is intentionally specific and task-oriented, with recommendations designed to avoid broad rewrites.

## CODEX PG Skills Created

Created: 2026-04-24 19:49:53 -07:00

- Skills folder: C:\CODEX PG\CODEX Skills
- Project Orientation skill: C:\CODEX PG\CODEX Skills\CODEX PG Project Orientation\SKILL.md
- Code Review skill: C:\CODEX PG\CODEX Skills\CODEX PG Code Review\SKILL.md
- Claude Task Writer skill: C:\CODEX PG\CODEX Skills\CODEX PG Claude Task Writer\SKILL.md
- Index: C:\CODEX PG\CODEX Skills\CODEX_SKILLS_INDEX.md
- Optional installer script: C:\CODEX PG\CODEX Skills\CODEX_install_project_skills.ps1

Purpose: make Codex more consistent on Panda Gallery orientation, 6 C's code review, and Claude-ready task prompt writing. Skills were created under C:\CODEX PG first to respect the project folder rule. Installing them into Codex's live skills directory should be a separate explicit action because that writes outside C:\CODEX PG.

## Claude UX Mockup Review Completed

Created: 2026-04-24 20:04:34 -07:00

- Review folder: C:\CODEX PG\CODEX Claude UX Mockup Review
- Main document: C:\CODEX PG\CODEX Claude UX Mockup Review\CODEX_CLAUDE_SCREENSHOT_UX_MOCKUP_REVIEW.md
- Rendered screenshot folder: C:\CODEX PG\CODEX Claude UX Mockup Review\CODEX rendered screenshots
- Contact sheets:
  - C:\CODEX PG\CODEX Claude UX Mockup Review\CODEX_recent_mockups_contact_sheet.png
  - C:\CODEX PG\CODEX Claude UX Mockup Review\CODEX_v4_0_mockups_contact_sheet.png
  - C:\CODEX PG\CODEX Claude UX Mockup Review\CODEX_all_claude_mockups_contact_sheet.png

Scope: reviewed 32 Claude UX mockups from C:\panda-gallery\workflows\design, including recent testing-pane mockups and the v4.0 shell/library/mount/review/compare/present/template/right-panel studies.

Key opinion: Claude's visual direction is strong enough to be the foundation for Panda Gallery v4, but it should be made more explicitly dental. Borrow Lightroom's workflow architecture and Photoshop's focused tools, while using dental vocabulary and clinical defaults. Recommended module set: Library, Mount, Review, Compare, Present.

## Playwright Browser Installed

Installed: 2026-04-24 20:09:42 -07:00

- Playwright Chromium browser cache: C:\CODEX PG\CODEX Playwright Browsers
- Setup note: C:\CODEX PG\CODEX Playwright Setup\CODEX_PLAYWRIGHT_SETUP.md
- Verification: launched Chromium headless successfully and read page title CODEX Playwright Check.
- GitHub backup policy: CODEX Playwright Browsers/ is intentionally ignored in .gitignore because it contains large downloaded browser binaries.

Use Playwright for local HTML mockup screenshots, contact sheets, responsive checks, and future browser-style dashboard/spec testing. It is not the primary test tool for the live Python/PySide desktop app.



## Audit MVP Starter Pack Created

Created: 2026-04-24 20:43:16 -07:00

- Starter pack folder: C:\CODEX PG\CODEX Audit MVP Starter Pack
- README: C:\CODEX PG\CODEX Audit MVP Starter Pack\CODEX_AUDIT_MVP_STARTER_PACK_README.md
- Claude prompt: C:\CODEX PG\CODEX Audit MVP Starter Pack\CODEX docs\CODEX_CLAUDE_INTEGRATION_PROMPT.md
- Mockup/spec references: C:\CODEX PG\CODEX Audit MVP Starter Pack\CODEX docs\CODEX_MOCKUP_AND_SPEC_REFERENCES.md
- Reference builder: C:\CODEX PG\CODEX Audit MVP Starter Pack\CODEX scripts\audit_mvp_reference_builder.py
- Validator: C:\CODEX PG\CODEX Audit MVP Starter Pack\CODEX scripts\validate_audit_mvp_contracts.py
- Sample source session: C:\CODEX PG\CODEX Audit MVP Starter Pack\CODEX samples\sample_source_session
- Generated expected package: C:\CODEX PG\CODEX Audit MVP Starter Pack\CODEX samples\expected_package\session_package_session_20260424_194422
- Sample issue extraction JSON: C:\CODEX PG\CODEX Audit MVP Starter Pack\CODEX samples\sample_audit_issue_extraction_v1.json
- Validation report: C:\CODEX PG\CODEX Audit MVP Starter Pack\CODEX validation output\CODEX_validation_report.json

Verification completed: Python scripts compile, builder generated the expected package, and validator returned ok: true with zero errors and zero warnings. C:\panda-gallery was not edited.

## Claude Share Package Created

Created: 2026-04-24 20:52:21 -07:00

- Share folder: C:\CODEX PG\CODEX Claude Share Package
- Read-first file: C:\CODEX PG\CODEX Claude Share Package\CODEX_READ_ME_FIRST.md
- Manifest: C:\CODEX PG\CODEX Claude Share Package\CODEX_SHARE_MANIFEST.md
- Portable ZIP: C:\CODEX PG\CODEX Claude Share Package.zip local-only and ignored by git.

Contents summary: 120 files total, including 42 full-size PNG images, 37 HTML mockups, 19 Markdown docs, 2 Python sample scripts, 16 JSON files, the complete synthetic sample source session, and the generated Audit MVP sample package. Contact sheets are intentionally not included in the full-size mockup images folder.

Purpose: one folder Darrin can point Claude to for Codex docs, canonical specs, Audit MVP starter pack, full-size mockup renders, source HTML mockups, sample code, sample JSON, and Claude-ready prompts.

## Claude Codex Mailbox Protocol

Created: 2026-04-24 23:00:00 -07:00

Codex and Claude now coordinate through a shared mailbox under `C:\CODEX PG`:

- Mailbox root: `C:\CODEX PG\CODEX Claude Codex Mailbox`
- Protocol: `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX_PROTOCOL.md`
- Claude-to-Codex messages: `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox`
- Codex-to-Claude messages: `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox`
- Sent copies:
  - `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Sent`
  - `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Sent`

Rules:

- Check `CODEX Inbox` early in every resumed session.
- Use timestamped Markdown files for messages.
- Do not edit another agent's sent message; reply with a new file.
- Mailbox is for coordination only and does not authorize implementation.
- No PHI, patient data, secrets, credentials, tokens, or approval-sensitive material.
- Darrin remains the approval gate for edits to `C:\panda-gallery`.

Recent mailbox topics:

- Stage 1 audit integration contract decisions and implementation report.
- Claude's correction that live manifest `warnings[]` contains two expected `optional_source_missing` entries.
- Claude guidance for main PG UX mapping.
- Claude/Codex agreement that Template and Freeform should unify inside the Arrange module, using per-slot constraints and an Edit Layout affordance rather than a separate Template Studio module.
- Codex asked Claude to review whether Arrange layout editing should use a visible `Edit Layout` affordance, right-click affordance, or both. Await Claude response if not already superseded by later PG-side work.
- Codex asked Claude to review the Review-module radiograph enhancement toolset, including Window/Level, Clarity, diagnostic presets, Measurement priority, and Lightroom/Photoshop-derived tools filtered for dentistry.
- Codex asked Claude to review whole-app process streamlining, especially the proposed global context action bar and click-reduction flow.
- Claude sent a decision lock from Darrin: v4.0 module set is **Library / Arrange / Review / Present**. Compare is a submode inside Review, not a top-level module. Use these names in all future flow mapping.
- Codex asked Claude to review newer radiograph enhancement algorithm candidates: SwinIR/transformer restoration, adaptive guided filtering, Retinex/homomorphic normalization, multi-scale morphology, wavelet/shearlet methods, super-resolution, panoramic de-shadowing, and diffusion/generative approaches. Codex position: simple dentist-facing controls, algorithm comparison harness before production choice, no generative replacement of clinical evidence.





























