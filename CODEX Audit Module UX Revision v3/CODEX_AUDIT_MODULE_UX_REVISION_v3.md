# CODEX Audit Module UX Revision v3

## Plain-English Product Model

The Audit Module is an intelligent inbox for Panda Gallery testing feedback. Screenshots, transcript text, step results, and metadata arrive through Dropbox. The module checks completeness, analyzes the contents, groups findings, ranks urgency, drafts a sender response, prepares Claude Code tasks, and later verifies fixes.

The module should feel mostly automated, but not reckless. It analyzes and drafts automatically; Darrin approves communication, priorities, and code handoff.

## Revised Workflow

1. Dropbox Intake
2. Completeness Check
3. Automated Analysis
4. Categorized Findings
5. Priority Triage
6. Human Review
7. Sender Response Draft
8. Claude Code Task Builder
9. Fix Verification
10. Searchable Archive

## Surface Design Rule

Visible by default:

- Review findings
- Approve finding
- Edit wording
- Approve response
- Create Claude Code package
- Verify fixed

Collapsed by default:

- Raw JSON
- Dropbox internals
- Package hashes
- Duplicate candidates
- Model diagnostics
- Archive metadata
- Full transcript
- Delivery metadata

## Urgency Color Spectrum

- P0 urgent/blocking: #d46a6a
- P1 fix now/amend: #e8a87c
- P2 soon/scheduled: #f39c12
- P3 later/clarify: #8a8a9a
- Complete/verified: #5ab87a or #7fb069

Color must identify status and urgency, not decorate.

## Screen Set

1. Dropbox Intake
2. Analysis Review
3. Finding Detail
4. Sender Response Draft
5. Claude Code Task Builder
6. Verification
7. UX Principle Map

## What This Supersedes

This v3 supersedes the earlier local-only mockup emphasis. The local package builder remains important behind the scenes, but the user-facing product should start with incoming Dropbox submissions and their analyzed findings.
