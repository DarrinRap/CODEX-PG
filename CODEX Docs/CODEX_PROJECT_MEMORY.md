# CODEX Project Memory

Last updated: 2026-05-02 19:13:00 -07:00

This file is the durable memory for Codex work on the PG Testing + Audit desktop project. Future Codex chats should read this file first before making plans or edits.

## Permanent Workspace Rules

- Codex workspace parent: C:\CODEX PG
- Every folder Codex creates must live inside C:\CODEX PG.
- Every folder Codex creates must start with the word CODEX.
- Claude / existing Panda Gallery workspace: C:\panda-gallery
- Treat C:\panda-gallery as read-only reference unless Darrin explicitly says otherwise.
- Keep Codex files separate from Claude files.


## PAH Coordination Rule

Updated: 2026-04-30 07:45:00 -07:00

Claude Desktop (CD) is Codex's project manager for all PANDA Agent Hub (PAH) work. Codex must automatically communicate with CD on all PAH-related matters, including diagnostics, incidents, speed/reliability findings, architecture decisions, implementation plans, verification results, blockers, and handoff/status updates.

Operational rule: for PAH work, Codex should file a concise CD-visible mailbox update before making substantive code changes when practical, and after verification before claiming completion. This coordination rule does not override Darrin's approval gate for protected actions, commits, pushes, writes to `C:\panda-gallery`, external services, or other approval-sensitive work.

## PAH Mail And Inspector UX Canon

Updated: 2026-04-30 07:45:00 -07:00

The canonical detailed PAH Mail + Inspector UX spec is:

`C:\CODEX PG\CODEX Agent Hub\CODEX_PAH_MAIL_AND_INSPECTOR_UX_SPEC.md`

It includes current live screenshots, the Mail-first user-console direction, Inspector redesign requirements, performance targets, data contracts, safety rules, and CC collaboration guidance. Future PAH/Inspector UI work should read this spec before implementation.

## Codex Operating Efficiency Rules

Updated: 2026-04-30 07:50:00 -07:00

- Evidence before confidence: never claim PAH or other coordination infrastructure is fixed, fast, or reliable without current verification evidence.
- PAH performance expectation: mailbox write and pickup should feel near-instant. Treat full dashboard refresh over a few hundred milliseconds as a performance concern and profile before guessing.
- Default PAH verification gate: before calling PAH work complete, run `CODEX_run_smoke_tests.py`, `CODEX_pah_inspector.py`, server smoke, `/api/health`, and any relevant latency/perf probe.
- Commit-go discipline: Codex must not commit or push without an explicit Darrin trigger such as `go`, `approved`, `ship it`, `fire`, or named-task confirmation. Generic `ok`, `continue`, `yes`, or similar replies are not commit authorization.
- PAH/CD reporting pattern: for PAH, notify CD before substantive changes when practical, then send CD a concise verification summary after testing.
- Resume priority order: check current mail first, read the latest handoff/resume context, check git status, check PAH/relay health when PAH is relevant, then work the highest-priority active dispatch.
- Definition of done: work is not done until code, docs, tests, mailbox reports, and git state match the actual state, with remaining risk named plainly.
- Completion coordination: whenever Codex completes a task, send CD a concise completion/report message and ask for help, direction, or the next action instead of going quiet.
- Communication style preference: be direct, brief, evidence-based, and do not overstate certainty. Say `not proven yet` when that is the truth.
- Safety hygiene: never write credentials, tokens, PHI, patient data, or approval-sensitive secrets into memory, mailbox, logs, reports, or test fixtures.
- PAH performance harness direction: PAH needs a real pickup-latency, concurrency, endurance, and failure-injection harness. Smoke tests alone are not sufficient proof of reliability.

## Launcher Tab Reuse Rule

Updated: 2026-05-02 19:00:00 -07:00

PC and PAH launchers must not rely on browser process `MainWindowTitle`, `SendKeys`, or cache-buster query strings to find an existing tab. That only works when the app tab is the active tab and causes duplicate tabs when the app is open in the background.

Canonical behavior: app pages register a live browser client with their local server; launchers request `/api/launch-refresh/request`; the open tab acknowledges through `/api/launch-refresh/ack` and refreshes itself. Launchers must also track whether the acknowledging client is foreground/visible. A hidden/background/offscreen client must not suppress a visible launch; if only hidden clients acknowledge, open the canonical app URL. Future launcher fixes must diagnose with this app-mediated refresh contract before changing browser-opening code.

## Visual Regression Rule

Updated: 2026-05-02 19:13:00 -07:00

Any PAH or PC change that adds header/topbar buttons, status chips, filters, tabs, or other persistent controls must include a responsive overflow check before closeout. Do not add controls into a fixed-height shell row without either bounded columns, wrapping, or a deliberate overflow menu. Required PAH check: run BA from PAH `/ba-applet`, open Layout Safety, and run `Probe PAH Layout`; it must pass at 1750, 1366, 1100, 940, and 820 px with no document/topbar/action horizontal overflow.

## Product Direction

- Target platform: desktop.
- Preferred implementation stack: Python with PySide6 / Qt.
- Product area: PG Testing + Audit module for guided tester sessions and PG review workflow.
- Important existing condition from the MVP spec: audio capture and timestamped transcription already work.
- MVP starts after transcription exists.

## MVP Scope From Spec

The remaining MVP work is:

- Screenshot capture alignment.
- Session packaging.
- Dropbox transfer.
- AI issue extraction.
- PG audit dashboard.
- Approval workflow.
- Shared team email communication.
- Searchable audit archive.

Final MVP rule: if a feature does not directly improve session capture, Dropbox transfer, AI triage, PG approval speed, or searchable audit integrity, it does not belong in MVP v1.

## Design Direction

Use the existing Panda Gallery visual vocabulary as reference:

- Dark desktop shell.
- Compact floating panes.
- Low-radius controls.
- Muted borders and row separators.
- Peach active accent: #e8a87c.
- Green pass state.
- Red fail state.
- Quiet grey secondary text.
- Stable bottom action bars.
- Evidence stays attached to decisions.

## Recurring Design Error Prevention Rule

Updated: 2026-05-01 10:55:00 -07:00

Darrin has repeatedly flagged Codex for design and formatting regressions. Future Codex sessions must review this section before any UI, mockup, applet, or frontend work and must treat it as a standing quality gate, not optional polish.

Recurring mistakes to avoid:

- Do not ship visual changes based only on code inspection. Run the relevant applet/checker and inspect the live browser or rendered mockup before saying the UI is fixed.
- Do not let buttons overlap, touch, clip text, or stack unreadably at narrow widths. Check actual rendered screenshots, not just CSS intent.
- Do not confuse action buttons with informational pills. Rectangular/square controls do work. Pillbox/chip controls are informational/status only. A clickable pill-looking control is a visual bug.
- Do not use user identity colors as readiness colors. Green means an enabled safe action. Grey means disabled. Warning/red is reserved for danger, fail, or emergency states.
- Do not create duplicate or competing controls for the same action. If multiple controls look similar, simplify the flow before adding more labels.
- Do not call PC/PAH UI work complete until the written spec, applet checks, automated tests, and live visual review agree.

For PANDA Collaborator specifically, run and review `C:\CODEX PG\CODEX PANDA Collaborator\CODEX_ui_layout_applet.py` before and after UI changes. It must include Bible checks for action-button shape, passive pill behavior, responsive stacking, and known overlap regressions.

## Codex Artifacts Created

- C:\CODEX PG\CODEX Visual Mockups
  - Initial visual mockups for audit dashboard, tester capture panel, and region review dialog.
- C:\CODEX PG\CODEX Interface Storyboards
  - Step-by-step UI storyboard with nine user-interface states.
  - Companion design notes.
- C:\CODEX PG\CODEX Docs
  - Project memory and handoff documents.
- C:\CODEX PG\CODEX Automation
  - Backup automation script.
- C:\CODEX PG\CODEX Backup Logs
  - Backup logs generated by the automation script.

## Recommended Future Chat Startup

At the beginning of a new Codex chat, say:

Read C:\CODEX PG\CODEX Docs\CODEX_PROJECT_MEMORY.md and C:\CODEX PG\CODEX Docs\CODEX_CURRENT_HANDOFF.md first.

Then ask Codex to continue from the latest handoff.

## GitHub Backup

Configured: 2026-04-24 18:51:53 -07:00

- GitHub repository: `https://github.com/DarrinRap/CODEX-PG.git`
- Local repo: `C:\CODEX PG`
- Branch: `main` tracks `origin/main`.
- Use `C:\CODEX PG\CODEX Automation\CODEX_backup_to_github.ps1` after meaningful changes.

## Panda Gallery Read-Only Reference Access

Configured: 2026-04-24 18:56:29 -07:00

- Source folder: `C:\panda-gallery`.
- Codex may read all files from `C:\panda-gallery` as reference material.
- Codex must not write, edit, delete, move, stage, commit, push, or mutate anything inside `C:\panda-gallery` unless Darrin explicitly overrides this boundary later.
- Read-only reference policy folder: `C:\CODEX PG\CODEX Panda Gallery Readonly Reference`.
- Inventory generated: `CODEX_PANDA_GALLERY_INVENTORY.md` and `CODEX_PANDA_GALLERY_FILE_INDEX.csv`.
- Last inventory count: 6,249 files.

<!-- CODEX_HANDOFF_AUTOMATION_START -->
## Handoff Automation

Last generated: 2026-05-14 21:38:05 -07:00

Project-local shortcut folder: `C:\CODEX PG\CODEX Handoff Automation`.

Trigger words:

- CODEX HANDOFF: update handoff snapshot, generate resume prompt, run GitHub backup.
- CODEX CHECKPOINT: same as handoff, used mid-project.
- CODEX BACKUP: run GitHub backup only.
- CODEX RESUME PG: fresh-chat startup instruction.
<!-- CODEX_HANDOFF_AUTOMATION_END -->
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
- Master spec index: `C:\CODEX PG\CODEX Canonical Specs\CODEX_MASTER_SPEC_INDEX.md`
- Session package schema: `C:\CODEX PG\CODEX Canonical Specs\CODEX_SESSION_PACKAGE_SCHEMA_v1.md`
- Audit issue schema: `C:\CODEX PG\CODEX Canonical Specs\CODEX_AUDIT_ISSUE_SCHEMA_v1.md`
- Testing + Audit architecture: `C:\CODEX PG\CODEX Canonical Specs\CODEX_TESTING_AUDIT_ARCHITECTURE_v1.md`
- Audit dashboard UX spec: `C:\CODEX PG\CODEX Canonical Specs\CODEX_AUDIT_DASHBOARD_UX_SPEC_v1.md`
- Testing + Audit compliance addendum: `C:\CODEX PG\CODEX Canonical Specs\CODEX_COMPLIANCE_ADDENDUM_TESTING_AUDIT_v1.md`

Purpose: convert the fragmented spec corpus into buildable Testing + Audit contracts before PySide6/backend implementation.

Key decisions captured:

- PG Core v4 and PG Testing + Audit MVP v1 are separate product tracks.
- Audio capture and timestamped transcription remain upstream inputs.
- Session packages use durable evidence IDs instead of bare screenshot paths.
- Dropbox/backend processing must wait for a package-ready marker, not just file upload.
- AI issues must reference valid evidence IDs and preserve AI suggestions separately from reviewer edits.

Recommended next task: if Darrin approves, send Claude the Stage 1 approval prompt for narrow local package-builder integration into `C:\panda-gallery`; otherwise continue Codex-side prep.

## Codebase Orientation Completed

Completed: 2026-04-24 19:21:32 -07:00

- Orientation folder: C:\CODEX PG\CODEX Codebase Orientation
- Main summary: C:\CODEX PG\CODEX Codebase Orientation\CODEX_PG_CODEBASE_ORIENTATION_SUMMARY.md
- Live source inspected: C:\panda-gallery version 4.23.
- Key understanding: PG already has guided local testing, workflow screenshot/audio capture, local faster-whisper transcription, results JSON, and Shift+F12 session-aware region capture. Testing + Audit MVP still needs canonical package/evidence/issue/approval/archive contracts before broad implementation.

Recommended next task: Stage 1 integration first; dashboard prototype is Stage 2 after the PG-side local package producer exists.

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
## Local Audit Package Builder Scaffold Created

Created: 2026-04-24 22:18:00 -07:00

- Scaffold folder: `C:\CODEX PG\CODEX Desktop App`
- Python package: `C:\CODEX PG\CODEX Desktop App\CODEX_pg_audit`
- Tests: `C:\CODEX PG\CODEX Desktop App\CODEX_tests`
- README: `C:\CODEX PG\CODEX Desktop App\CODEX_README.md`
- Claude share copy: `C:\CODEX PG\CODEX Claude Share Package\CODEX Desktop App Scaffold`
- Generated smoke package: `C:\CODEX PG\CODEX Audit Prototype\CODEX Session Packages\session_package_session_20260424_194422` local-only and ignored by git.

Verification completed with bundled Codex Python:

- `python -m unittest discover -s CODEX_tests`: 8 tests passed.
- `python -m CODEX_pg_audit.cli ...`: generated sample package and validator returned `ok: true` with zero errors and zero warnings.
- Live PG workflow smoke test completed read-only against `C:\panda-gallery\workflows`: generated 11 evidence records and validator returned `ok: true` with zero errors and zero warnings.
- Mock issue extraction added with `--mock-issues`; issue extraction validation returned `ok: true` with zero errors and zero warnings, and tests verify unknown evidence IDs are blocked.
- Local approval, draft-only email, and archive JSONL scaffolds added with `--review-records`; live read-only smoke generated all records successfully.
- Review-record validation/search helpers added for local approval/email/archive chain and archive JSONL text search.

Important boundary: this is a local-only package builder and validator scaffold. It does not build v4, does not build the final audit dashboard, does not upload to Dropbox, does not call AI, does not send email, and does not mutate `C:\panda-gallery`.

Recommended next task: Stage 1 local package-builder integration in `C:\panda-gallery` if Darrin approves; keep dashboard, Dropbox, real AI, live email, and full editing workflow deferred.
## Claude Stage 1 Alignment Response

Created: 2026-04-24 22:58:00 -07:00

- Claude reviewed the share package and recommended Stage 1 as narrow local package-builder integration into `C:\panda-gallery` via a CLI command.
- Codex agrees with Stage 1 as the next implementation step, with no dashboard, Dropbox, real AI, live email, PHI workflow, or broad v4 clinical UI work.
- Codex locked Stage 1 package IDs to deterministic `pkg_local_<session_id>` and documented that timestamp/random package IDs should be revisited before Stage 2 or production-like package history.
- Codex updated integration prompt paths to prefer the share package layout.
- Codex added a Stage 1 approval prompt for Darrin to send Claude only if implementation is approved.
- Backlog added: after Stage 1 ships, perform a drift check between `C:\CODEX PG\CODEX Desktop App\CODEX_pg_audit\` and `C:\panda-gallery\codex_audit\`.
- Stage 2 heads-up: Claude should produce HTML/CSS mockups first for the read-only audit dashboard, and Codex should review those mockups before PySide6 implementation.

Prompt files:

- `C:\CODEX PG\CODEX Claude Share Package\CODEX Prompts\CODEX_CODEX_RESPONSE_TO_CLAUDE_STAGE1_ALIGNMENT.md`
- `C:\CODEX PG\CODEX Claude Share Package\CODEX Prompts\CODEX_CLAUDE_STAGE1_APPROVAL_PROMPT.md`
## Claude Codex Mailbox Created

Created: 2026-04-24 23:00:00 -07:00

- Mailbox root: `C:\CODEX PG\CODEX Claude Codex Mailbox`
- Protocol: `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX_PROTOCOL.md`
- Claude-to-Codex messages: `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox`
- Codex-to-Claude messages: `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox`
- First message to Claude: `20260424_230000_CODEX_to_CLAUDE_mailbox_protocol_and_q1_decision.md`

Rules: mailbox is for coordination only, cannot authorize implementation by itself, and must not contain PHI, secrets, credentials, or patient data. Darrin remains the approval gate for Stage 1 implementation.

Latest schema decisions sent to Claude through mailbox:

- Q1 = Option B: structured `warnings[]` is canonical; no `missing_sources[]` in new Stage 1 output.
- Q2 = Option A: shortened package/folder IDs with 8-character SHA256 suffix; full session_id/run_id remain in manifest.
- Q3 = Option A: absolute local paths acceptable for Stage 1 local-only output, deferred redaction/relativization before external transfer.


























## Development Spec Gate Rule

Created: 2026-05-03

- Never start building, coding, implementation, refactoring, or development work without a properly vetted spec.
- "Properly vetted" means the spec is written down, checked for errors, oversights, conflicts, and ambiguities, and approved by Darrin or by an explicit current directive that names the vetted spec.
- Diagnostics, mail checks, read-only investigation, and reporting can happen before the spec, but code/file implementation starts only after the vetted-spec gate is satisfied.

## No UI/UX Touch Rule

Created: 2026-05-06

- Darrin gave a hard rule after a PAH header regression: Codex must not touch UI or UX files.
- Do not make UI/UX design feature recommendations for any app unless Darrin explicitly approves that exact work in the current context.
- For visual previews that are explicitly requested, open the target directly in Microsoft Edge; do not rely on local clickable/web links.
- Do not stage, commit, revert, or clean dirty UI/UX files unless Darrin explicitly overrides this rule.

## CC/CD Mailbox Follow-Up Rule

Created: 2026-05-04

- Codex must regularly check PAH-visible Claude Desktop (CD) and Claude Code (CC) mailbox state, especially unread, open-on-agent, stale, pending-dispatch, and waiting-on-Darrin threads.
- When CC or CD appears not to have fully read, acknowledged, or responded appropriately to assigned mail, Codex should send a concise PAH-visible follow-up/nag asking them to read the relevant mailbox item fully, respond in-thread, and state completion, blocker, or requested decision.
- Follow-ups must be evidence-based: include thread/message IDs or paths when useful, avoid vague "check your mail" pings, and do not overstate certainty if the state is inferred from stale mailbox/read-state evidence.
- Do not write PHI, secrets, credentials, or patient data into follow-ups.
- Prefer PAH mailbox routes/protocols over ad hoc file writes. Writing into `C:\panda-gallery` remains protected unless Darrin explicitly authorizes that specific CC mailbox action.
- Keep nag volume low and useful: one consolidated follow-up per agent per check cycle unless there is an urgent or Darrin-blocking thread.
## Mailbox Manager Heartbeat Rule

Created: 2026-05-06

- Codex should act as a PG mailbox manager during active PG coordination windows.
- Check all four mailbox lanes regularly: `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox`, `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox`, `C:\panda-gallery\workflows\cc_mailbox\CC Inbox`, and `C:\panda-gallery\workflows\cc_mailbox\CLAUDE Inbox`.
- Report any dispatched message that remains unread more than 60 minutes after dispatch. Include message path/id, apparent sender, intended recipient/lane, dispatch timestamp if available, current age, and recommended nudge.
- When a nudge is needed, route it to the appropriate mailbox lane and ask the recipient to read fully, respond in-thread, and state START/RTC/SHIPPED, completion, blocker, or requested decision.
- Protocol boundary remains active: Codex must not send implementation-go or commit-go tokens directly to CC. If Darrin says "go" for CC work in Codex chat, route the authorization request/status through Claude Desktop/CD via `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox`.
- Do not touch Relay files, dirty parked files, UI/UX files, or stage/commit/revert anything while performing mailbox-manager checks unless Darrin explicitly authorizes that action in the current chat.










## Memory - Vellum Approval Viewer Planning (2026-05-07 19:03:19 -07:00)

Darrin established a mockup-first approval workflow and Vellum planning thread. Preserve these files and use them as the source of truth for future Vellum/PG UI approval work:

- Clarifications and Darrin answers: $clarifications
- Focused Vellum default mockup approval viewer spec draft: $spec
- Standing approval workflow preferences: $pref

Protocol reminder: these files are planning/status artifacts only. They do not authorize CC implementation or commits. Codex must not send implementation-go or commit-go directly to CC; formal CC authorization remains CD-owned. Vellum spec requires focused Vellum workflow mockups approved by Darrin before any CC coding.

## Memory - Vellum Technical Upgrade Spec (2026-05-07 19:16:46 -07:00)

Darrin completed clarification Q1-Q11 for the Vellum technical upgrade spec and approved drafting. New source files:

- Technical spec: $tech
- Clarifying questions: $techQs
- CD review request: $cdPath

Important protocol: Codex asked CD to review all new Vellum work and make changes as needed. Codex did not send coding instructions to CC. CD owns any future CC communication/authorization.

Self-review summary: Pass 1 fixed 5 issues, Pass 2 fixed 4, Pass 3 fixed 2, Pass 4 found 0 significant issues.

## Memory - 
THE PG UI UX OVERHAUL SPECS with VELLUM UPGRADES
 (
2026-05-07 19:18:10 -07:00
)

Darrin named the combined document group **
THE PG UI UX OVERHAUL SPECS with VELLUM UPGRADES
**. Use this exact name for the PG UI/UX overhaul plus Vellum approval-viewer upgrade planning set.

Included files:
- `C:\Users\drrap\Downloads\PG_UX_UI_Overhaul_Strategy_v1.2.docx`
- `C:\panda-gallery\workflows\design\approval_packets\PG_UX_UI_Overhaul_v1.2_clarifying_questions.md`
- `C:\panda-gallery\workflows\design\VELLUM_DEFAULT_MOCKUP_APPROVAL_VIEWER_SPEC_v1.md`
- `C:\panda-gallery\workflows\design\approval_packets\VELLUM_TECHNICAL_UPGRADE_SPEC_clarifying_questions.md`
- `C:\panda-gallery\workflows\design\VELLUM_APPROVAL_VIEWER_TECHNICAL_UPGRADE_SPEC_v1.md`
- `C:\panda-gallery\workflows\design\approval_packets\Darrin_approval_workflow_preferences.md`

CD naming clarification sent: `
C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\20260507_191810_CODEX_to_CD_pg_ui_ux_overhaul_specs_with_vellum_upgrades_NAMING_CLARIFICATION.md
`

Protocol reminder: this naming clarification is status only, not implementation-go or commit-go. Codex must not directly authorize CC coding; CD owns future CC routing/authorization.

## Memory Correction - 
THE PG UI UX OVERHAUL SPECS with VELLUM UPGRADES
 Paths (
2026-05-07 20:02:06 -07:00
)

Corrected prior placeholder-path issue in mailbox/status notes. Use these actual paths for the grouped specs:
- PG UX/UI Overhaul v1.2 DOCX: `C:\Users\drrap\Downloads\PG_UX_UI_Overhaul_Strategy_v1.2.docx`
- PG UX/UI Overhaul clarification record: `C:\panda-gallery\workflows\design\approval_packets\PG_UX_UI_Overhaul_v1.2_clarifying_questions.md`
- Vellum approval viewer planning spec: `C:\panda-gallery\workflows\design\VELLUM_DEFAULT_MOCKUP_APPROVAL_VIEWER_SPEC_v1.md`
- Vellum technical upgrade clarification record: `C:\panda-gallery\workflows\design\approval_packets\VELLUM_TECHNICAL_UPGRADE_SPEC_clarifying_questions.md`
- Vellum technical upgrade spec: `C:\panda-gallery\workflows\design\VELLUM_APPROVAL_VIEWER_TECHNICAL_UPGRADE_SPEC_v1.md`
- Approval workflow preferences: `C:\panda-gallery\workflows\design\approval_packets\Darrin_approval_workflow_preferences.md`

Correction notices sent:
- CD: `
C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\20260507_200206_CODEX_to_CD_pg_ui_ux_vellum_paths_CORRECTION_STATUS_ONLY.md
`
- CC: `
C:\panda-gallery\workflows\cc_mailbox\CC Inbox\20260507_200206_CODEX_to_CC_pg_ui_ux_vellum_paths_CORRECTION_STATUS_ONLY.md
`

Protocol: status/location only, not implementation-go or commit-go. CD owns future CC routing/authorization.

## Memory - CD Finalization Request for 
THE PG UI UX OVERHAUL SPECS with VELLUM UPGRADES
 (
2026-05-07 20:13:11 -07:00
)

Darrin asked Codex to share **
THE PG UI UX OVERHAUL SPECS with VELLUM UPGRADES
** with CD, ask CD to check/update as recommended, ask Darrin questions if needed, finalize the spec package, and share finalized specs with CC through CD-owned routing.

CD request sent: `
C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\20260507_201311_CODEX_to_CD_pg_ui_ux_overhaul_specs_with_vellum_upgrades_FINALIZE_REQUEST.md
`

Files included:
- PG UX/UI Overhaul v1.2 DOCX: `C:\Users\drrap\Downloads\PG_UX_UI_Overhaul_Strategy_v1.2.docx`
- PG UX/UI Overhaul clarification record: `C:\panda-gallery\workflows\design\approval_packets\PG_UX_UI_Overhaul_v1.2_clarifying_questions.md`
- Vellum approval viewer planning spec: `C:\panda-gallery\workflows\design\VELLUM_DEFAULT_MOCKUP_APPROVAL_VIEWER_SPEC_v1.md`
- Vellum technical upgrade clarification record: `C:\panda-gallery\workflows\design\approval_packets\VELLUM_TECHNICAL_UPGRADE_SPEC_clarifying_questions.md`
- Vellum technical upgrade spec: `C:\panda-gallery\workflows\design\VELLUM_APPROVAL_VIEWER_TECHNICAL_UPGRADE_SPEC_v1.md`
- Approval workflow preferences: `C:\panda-gallery\workflows\design\approval_packets\Darrin_approval_workflow_preferences.md`

Protocol: Codex did not send coding instructions to CC. CD owns future CC routing/authorization.

## Memory - PAH Phase 2 Spec Shared With CD (
2026-05-07 20:56:48 -07:00
)

Darrin asked Codex to share the PAH update spec with CD for opinion and recommended enhancements.

Primary spec: `
C:\CODEX PG\CODEX Canonical Specs\CODEX_PAH_PHASE2_OBSERVABILITY_RESILIENCE_CC_SPEC_v0.1.md
`
CD review request: `
C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\20260507_205648_CODEX_to_CD_pah_phase2_spec_review_enhancement_REQUEST.md
`

Protocol: review/opinion only; not implementation-go, commit-go, or CC dispatch. CD owns future CC routing/authorization.

## Memory - PAH Phase 2 v0.2 Returned To CD (
2026-05-07 21:00:58 -07:00
)

Created PAH Phase 2 v0.2 with CD-requested amendments and routed back to CD only.

- Spec: `
C:\CODEX PG\CODEX Canonical Specs\CODEX_PAH_PHASE2_OBSERVABILITY_RESILIENCE_CC_SPEC_v0.2.md
`
- CD return: `
C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\20260507_210058_CODEX_to_CD_pah_phase2_v0.2_review_return.md
`

Boundary: PAH remains paused; no CC dispatch or implementation authorization.

## Memory - BA Dead-Code Detection Future Enhancement (
2026-05-08
)

Darrin asked whether BA can identify dead code. Future BA development should add this only as a conservative, backend/report-only capability.

Recommended scope:
- Detect likely unused imports, unreachable branches, orphaned scripts/components, unreferenced helpers, stale files outside active manifests/routes/tests, and duplicate or superseded utilities.
- Report findings with confidence levels such as `safe`, `likely`, and `needs human review`.
- Include evidence for every finding, such as reference search results, manifest/route/test absence, and known dynamic-entrypoint caveats.
- Never auto-delete, auto-stage, or auto-commit dead-code removals.
- Treat dynamic imports, reflection, CLI/manual scripts, fixtures, archives, and workflow/mailbox files as human-review unless there is strong evidence.

Protocol: BA dead-code detection should become an advisory quality gate first, not a removal tool. Any deletion requires explicit Darrin/CD/CC approval through the normal routing rules.

## Memory - BA Finding And BA Bug Classification Rule (
2026-05-09
)

Darrin approved a BA records convention: potential bugs found by Bible Audit should not automatically become normal product bugs.

Use these buckets:
- `Product Bug`: BA found a real issue in the target app/code.
- `BA Bug`: BA itself is wrong, misleading, noisy, incomplete, or untrustworthy, including false positives, false negatives, bad evidence, confusing severity, or scanner/report defects.
- `BA Advisory`: BA found something plausible but not yet proven and needing human review.
- `BA Calibration Finding`: expected output from a fixture or validator/calibration run.

Default intake label: `BA Candidate Bug` or `BA Finding`, with structured metadata such as:

```yaml
source: BA
finding_type: candidate_product_bug
confidence: medium
validation_status: unconfirmed
```

After review, promote to `product_bug`, `ba_bug`, `ba_advisory`, `ba_calibration_finding`, `false_positive`, or `no_action`. Preserve BA evidence and source metadata; do not let BA alone declare a product bug without validation.

Canonical record updated: `C:\CODEX PG\CODEX Canonical Specs\CODEX_BA_DISPOSITION_AWARE_VIEW_SPEC_v1.md`.

## Memory - BA Audit Surface Coverage Lesson (
2026-05-09
)

The PANDA Collaborator BA pass on 2026-05-08 was useful because it exposed a BA coverage/scanner problem, not because it found confirmed PC product bugs.

Issue found and fixed:
- BA registered `PANDA Collaborator` against only `panda_collaborator.py`, which is the launcher/wrapper surface.
- The active PC UI lives in `C:\CODEX PG\CODEX PANDA Collaborator\web\index.html`, so BA initially reported `No action controls discovered`.
- BA also did not understand PC's `$()` helper or delegated button groups, creating noisy action-feedback warnings after the HTML file was added.

Durable rule:
- A clean BA result is meaningful only when the app manifest covers the active UI/runtime surface, not just a launcher or wrapper.
- If BA says `No action controls discovered` for an app known to have controls, classify it first as a likely `BA Bug` / coverage gap and inspect manifest scope before changing product code.
- External CODEX PG apps with browser/HTML UI must keep both the launcher/backend entrypoint and primary UI file in BA manifest/default manifest coverage.
- Scanner changes must include regression tests for the app's real wiring idioms.

Regression protection added in `C:\panda-gallery\tests\test_ba_audit_runner.py`:
- PANDA Collaborator manifest includes both `panda_collaborator.py` and `web/index.html`.
- Default manifest fallback keeps the same PC scope.
- `action_feedback_static` recognizes `$()` click listeners, named JS handlers, and PC delegated button groups.

## Memory - Bug-Triggered BA Retrospective Protocol (
2026-05-09
)

Darrin directed that every bug found by Codex, CC, or CD must notify Codex going forward.

When Codex is notified of a bug, perform a BA retrospective before treating the bug as fully closed:
- Could BA have detected this bug before a human or agent found it?
- If yes, propose or implement the smallest BA upgrade that would have caught it, such as manifest/scope coverage, scanner recognition, runtime probe, fixture, regression test, report wording, or disposition logic.
- If no, record why the bug is outside current BA reach, such as needing human visual judgment, unavailable runtime state, missing adapter capability, or an intentionally non-BA domain.
- Preserve the original bug evidence and the BA-upgrade evidence together.
- Never treat this retrospective, bug notice, or BA-upgrade idea as implementation-go, commit-go, or CC authorization.

Notification route: CC/CD bug notices to Codex should use `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\` unless Darrin is actively handling it in the current Codex thread.


