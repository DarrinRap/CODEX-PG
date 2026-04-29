# CODEX Relay Mockup Delivery Inventory

Date: 2026-04-28
Owner: Codex
Purpose: compact inventory of Relay design deliverables so Claude, CC, Codex, and Darrin do not need to reconstruct the state from scattered mailbox files.

## Current Authority

- `C:\CODEX PG\CODEX Canonical Specs\RELAY_SPEC_v0.3.md` is canonical.
- `RELAY_SPEC_v0.2.md` is superseded.
- PAH development remains paused by Darrin while Relay dispatches are active.

## Delivered Mockups In Panda Gallery

Target folder:

`C:\panda-gallery\workflows\design\pg_general_mockups\`

### Baseline

| File | Source / Scope | Status |
| --- | --- | --- |
| `relay_module_v1.html` | Original Relay baseline mockup | Existing reference |

### A52 - Relay Hub Batch

| File | Scope | Status |
| --- | --- | --- |
| `relay_tester_hub_v1.html` | Tester hub: My Reports, Updates, New Report CTA state | Delivered to target; awaiting Claude/Darrin review |
| `relay_sent_tab_v1.html` | Developer Sent tab: failures-only and full-detail receipt states | Delivered to target; awaiting Claude/Darrin review |
| `relay_templates_tab_v1.html` | Templates list and template editor state | Delivered to target; awaiting Claude/Darrin review |
| `relay_duplicate_detection_v1.html` | Duplicate banner, comparison view, resolved duplicate state | Delivered to target; awaiting Claude/Darrin review |
| `relay_compose_v1.html` | Status-first compose, template auto-fill, sent confirmation | Delivered to target; awaiting Claude/Darrin review |

Additional earlier/provisional artifact left in place:

| File | Scope | Note |
| --- | --- | --- |
| `relay_tester_hub_my_reports_v1.html` | Earlier focused tester My Reports mockup | Not part of the 19:01 A52 authorized five-file set; left untouched |

### A53 - Tester Setup Flow

| File | Scope | Status |
| --- | --- | --- |
| `relay_tester_setup_v1.html` | 9-screen tester setup Q&A mockup | Delivered and accepted by Claude |

### A54 - Missing Hub Screens

| File | Scope | Status |
| --- | --- | --- |
| `relay_hub_missing_v1.html` | All Reports, expanded detail, Archive, empty states, navigation flow diagram | Delivered; awaiting Claude/Darrin review |

## Mailbox Completion Reports

| File | Thread | Status |
| --- | --- | --- |
| `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\20260428_124900_CODEX_to_CLAUDE_a53_relay_setup_mockups_complete.md` | A53 | Accepted by Claude |
| `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\20260428_130800_CODEX_to_CLAUDE_relay_spec_v03_complete.md` | Relay spec v0.3 | Accepted by Claude |
| `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\20260428_133200_CODEX_to_CLAUDE_a54_relay_hub_missing_complete.md` | A54 | Sent; awaiting ack |
| `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\20260428_134800_CODEX_to_CLAUDE_a52_delivery_complete.md` | A52 | Sent; awaiting ack |

## Verification Performed

- A52: source/target SHA256 matched for five authorized files.
- A52: palette check found no off-palette hex values in the five authorized files.
- A52: state/caption/spec-reference spot check passed.
- A53: 9 sections, 9 full render frames, required error copy, palette check, and primary-action discipline passed.
- A54: 5 sections, 5 full render frames, required copy anchors, palette check, and primary-action discipline passed.

Browser/Playwright rendering was not run because the local Node environment does not have Playwright installed.

## Open Review State

- Await Claude/Darrin review of A52.
- Await Claude/Darrin review of A54.
- No commits made.
