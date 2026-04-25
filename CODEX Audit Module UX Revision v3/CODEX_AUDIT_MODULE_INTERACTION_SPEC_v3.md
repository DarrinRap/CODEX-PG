# CODEX Audit Module Interaction Spec v3

Status: Revised around Dropbox intake and automated analysis.

## Core State Flow

`dropbox_waiting -> package_detected -> completeness_check -> analysis_running -> findings_ready -> finding_review -> response_draft -> response_approved -> code_task_ready -> fix_waiting -> verification_review -> archived`

## State Matrix

| State | User action | System response | Data written | Error handling | Next state |
| --- | --- | --- | --- | --- | --- |
| dropbox_waiting | New package appears | Detect completion marker and show intake row | intake event, package pointer | If marker missing show partial package | package_detected |
| package_detected | Open package | Run completeness check | completeness report | Missing files grouped by screenshots/transcript/metadata | completeness_check |
| completeness_check | Analyze package | Read transcript, screenshots, results, metadata | analysis job record | If analysis fails preserve package and show retry | analysis_running |
| analysis_running | Analysis completes | Create categorized findings | findings JSON, evidence links | Low-confidence items go to clarification group | findings_ready |
| findings_ready | Select finding | Show minimal finding detail and evidence | opened event | Missing evidence creates validation warning | finding_review |
| finding_review | Approve finding | Accept category, priority, wording, evidence | approved finding event | Missing observed/expected blocks approval | findings_ready |
| finding_review | Edit finding | Update title/category/priority/disposition | field edit events | Invalid category/priority blocked inline | finding_review |
| finding_review | Merge/split finding | Update related finding records | merge/split events | Preserve source evidence on every resulting finding | findings_ready |
| findings_ready | Draft response | Generate sender response from approved dispositions | response draft markdown/json | If no approved items, create clarification-only draft | response_draft |
| response_draft | Approve response | Lock response for sending/export | approval event | Delivery requires explicit human approval later | response_approved |
| response_approved | Create Claude task | Generate implementation package from approved code findings | task prompt, evidence links, acceptance tests | If validation fails return to findings | code_task_ready |
| code_task_ready | Mark sent to Claude Code | Update task status | code handoff event | If export fails keep task ready | fix_waiting |
| fix_waiting | Add verification evidence | Attach before/after screenshot and result | verification evidence object | If evidence missing keep waiting | verification_review |
| verification_review | Verify fixed | Close finding and archive | archive record | If not fixed reopen with reason | archived |

## Minimal UI Rule

Each screen has one primary action and at most three visible secondary actions. Everything diagnostic or infrequent belongs in collapsed drawers.

## Human Gates

Human approval is required before:

- sending or exporting a sender response
- handing a task to Claude Code for live code changes
- closing a finding as verified
- archiving a package as final

## First Implementation Slice

The first slice should implement intake and analysis review scaffolding without real upload or AI calls if those services are not ready. Use local sample packages as stand-ins for Dropbox arrivals and deterministic sample analysis output as stand-ins for AI.
