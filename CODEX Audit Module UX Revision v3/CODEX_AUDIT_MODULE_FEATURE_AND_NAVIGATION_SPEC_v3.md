# CODEX Audit Module Feature And Navigation Spec v3

## Product Promise

The Audit Module should feel like a calm intelligent inbox. It receives messy testing submissions, organizes them, and guides Darrin through the few decisions that matter.

The interface should appear minimal even though the system underneath is powerful.

## Primary Navigation

Left rail modules:

1. Intake
2. Review
3. Response
4. Code
5. Verify
6. Archive

These are workflow stages, not feature buckets.

## Main Visible Actions By Screen

| Screen | Primary visible action | Secondary visible actions | Hidden/collapsed actions |
| --- | --- | --- | --- |
| Dropbox Intake | Review findings | Refresh | Dropbox logs, raw package, hashes, completion marker |
| Analysis Review | Approve selected | Edit, Defer, Reject | Model diagnostics, duplicate candidates, raw JSON |
| Finding Detail | Approve finding | Edit wording, Ask sender, Defer | Audit trail, source metadata, confidence details |
| Sender Response | Approve response | Edit response, Clarification only | Tone settings, delivery metadata, full change list |
| Claude Code Task Builder | Create package | Export | Raw evidence refs, implementation risk, package JSON |
| Verification | Verify fixed | Reopen, Needs retest | Archive hashes, sender follow-up, search tags |
| UX Map | Ready for review | Index | Not applicable |

## Collapsible Panel Rule

Show by default only what supports the next human decision.

Collapse by default:

- Raw JSON
- Dropbox internals
- File hashes
- Package logs
- AI/model diagnostics
- Full transcript
- Duplicate matching details
- Archive metadata
- Delivery metadata
- Long implementation notes

## Urgency Spectrum

Use color as meaning, not decoration.

| Meaning | Color | Use |
| --- | --- | --- |
| P0 urgent/blocking | #d46a6a | Blocks testing, safety, data integrity, or critical workflow |
| P1 fix now/amend | #e8a87c | Important fix or amendment before MVP confidence |
| P2 soon/scheduled | #f39c12 | Useful improvement with workaround |
| P3 later/clarify | #8a8a9a | Lower priority, unclear, or needs sender detail |
| Verified/complete | #5ab87a / #7fb069 | Fixed, complete, accepted, or validated |

## Core Features

1. Dropbox Intake Queue
2. Package Completeness Check
3. Automated Analysis
4. Categorized Findings
5. Priority Triage
6. Evidence Linking
7. Human Review Workspace
8. Sender Response Drafting
9. Claude Code Task Builder
10. Status Tracking
11. Fix Verification Loop
12. Searchable Archive
13. Summary/Command View

## First Implementation Principle

If an interaction does not help Darrin decide what to approve, defer, clarify, send to Claude Code, or verify, it should probably be hidden behind a collapsible panel.
