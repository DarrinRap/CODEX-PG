# PANDA Agent Hub

Local-first cockpit for the Codex / Claude mailbox under `C:\CODEX PG`.

This is intentionally small and dependency-free. It does not call the OpenAI API, Anthropic API, or Claude Code directly yet. It watches and writes mailbox Markdown files so humans, Codex, Claude, and Claude Code can coordinate through shared state.

PAH is standalone. It lives under `C:\CODEX PG` for now and does not depend on Panda Gallery runtime code.

## Launch

From PowerShell:

```powershell
& "C:\CODEX PG\CODEX Agent Hub\CODEX_start_agent_hub.ps1"
```

Windows tray launcher:

```powershell
& "C:\CODEX PG\CODEX Agent Hub\CODEX_start_agent_hub_tray.ps1"
```

Or directly:

```powershell
python "C:\CODEX PG\CODEX Agent Hub\CODEX_agent_hub.py"
```

Default URL:

```text
http://127.0.0.1:8765
```

If that port is busy, the app picks a free local port and prints it.

## Current Features

- Dashboard counts for messages, threads, Darrin decisions, and validation issues.
- Latest mailbox messages across `CODEX Inbox`, `CLAUDE Inbox`, and sent folders.
- Thread grouping using `Thread-ID` when present, falling back to `Reply-To` / `Message-ID`.
- Modular PAH core packages for participant registry, schema parsing, mailbox paths, security helpers, notification scaffolding, and diagnostics.
- Schema v1 frontmatter for newly composed PAH messages.
- First-class Claude Code route writing to `CODEX_CLAUDE_CODE Inbox`; the older `CODEX Claude Code Inbox` is still read as legacy history.
- Darrin decision queue generated at:
  `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX_DARRIN_DECISIONS_NEEDED.md`
- Mailbox validator for missing message IDs, schema v1 issues, duplicate IDs, duplicate-ID provenance conflicts, important messages missing from the ledger, and some missing referenced paths.
- Standalone validator CLI at `C:\CODEX PG\CODEX Agent Hub\CODEX_pah_validator.py`; it validates PAH messages without calling Panda Gallery tools.
- Compose panel for:
  - Codex to Claude
  - Codex to Claude Code
  - Claude to Codex only when launched with explicit simulation mode
- Important composed messages append to `CODEX_MAILBOX_LEDGER.md`.
- Git status panel for `C:\CODEX PG`.
- Local notification subsystem for SMS-style alerts when Darrin attention is needed.
- Windows tray launcher with Open Dashboard, Open PAH Folder, Open Logs, and Exit actions.
- Tray balloon popups for new PAH notification log entries while the tray launcher is running.
- Communication diagnostics tab and endpoint for file-bridge readiness across Codex, Claude Desktop, and Claude Code.
- Route-test pings for Codex to Claude and Codex to Claude Code. PAH writes a traceable diagnostic ping and watches `CODEX Inbox` for a matching reply.
- Work Board for local parallel development coordination, with owner, priority, state, summary, and source fields.
- Work item dispatch from PAH into Claude Desktop or Claude Code mailbox routes, with dispatch metadata linked back to the work item.
- Safety tab showing protected-action approval record status, disabled live-adapter registry, and quarantine/tombstone status.
- Explicit quarantine API for mailbox messages. It requires the local write token and `confirmed: true`; PAH never auto-quarantines during refresh.
- Decision queue hygiene state for active/resolved/superseded/dismissed items. PAH keeps stale decisions in history without interrupting Darrin.
- Validator categorization with actionable issues separated from legacy/info mailbox hygiene noise.
- Validation finding state for accepted legacy, resolved, and dismissed findings. Historical ledger issues can be preserved without staying active.
- Backpressure detection for flooded threads; PAH flags more than 25 messages in 5 minutes or more than 50 visible messages in one thread.
- Processed-message sidecars for idempotency. PAH records message content hashes and processed event names so restart/refresh cannot resend the same notification for the same message content.
- Read/unread state and status badges for mailbox messages. PAH stores read state locally and marks changed message content unread again.
- Token-protected write endpoints for compose and notification tests.

## Claude Code Bridge Model

The current bridge is asynchronous and file-based:

1. Agent Hub writes a timestamped Markdown message into the target inbox.
2. Claude Code checks or watches that folder.
3. Claude Code writes a reply Markdown file back into the corresponding inbox.
4. Agent Hub refreshes and displays the reply.

This is practical two-way communication if Claude Code can access `C:\CODEX PG\CODEX Claude Codex Mailbox`. It is not live socket-style chat and does not make Claude Code always-on by itself. For always-on behavior, add a small watcher process or run Claude Code in a mode that periodically checks the mailbox.

## Communication Diagnostics

The dashboard includes a Diagnostics tab and a Communication Test panel.

The current diagnostic test verifies:

- required PAH participants exist in the registry
- Codex to Claude route exists
- Codex to Claude Code route exists
- Claude/Claude Code back to Codex file-bridge inbox exists
- live API/headless adapters remain disabled by default

The diagnostic test is intentionally file-bridge only. It does not launch Claude Code, send SMS, call paid APIs, or write to Panda Gallery.

Route tests are explicit and token-protected. Creating a route test writes a diagnostic Markdown message into the selected target inbox and records the test at:

```text
C:\CODEX PG\CODEX Agent Hub\CODEX state\CODEX_route_test_state.local.json
```

The test passes only when PAH later sees a matching reply in `CODEX Inbox` by `Thread-ID`, `Reply-To`, or test ID reference.

## Work Board

Work items are local PAH coordination records. They do not launch agents or authorize external work. The dashboard can create and update work items assigned to Codex, Claude Desktop, or Claude Code.

Dispatching a work item creates a schema v1 mailbox message to the assigned agent's inbox and marks the work item `in_progress`. Dispatch still does not launch a live adapter; the recipient agent must read or watch its mailbox.

PAH also watches `CODEX Inbox` for replies linked to dispatched work items. If a reply references the work item ID or dispatch message ID, PAH records the reply path and moves the item to `review` unless it was already complete or cancelled.

Work item state lives at:

```text
C:\CODEX PG\CODEX Agent Hub\CODEX state\CODEX_work_items.local.json
```

## SMS / Phone Notifications

PANDA Agent Hub can notify your phone when it detects attention events, such as:

- explicit Darrin decision items
- Claude messages requesting a Codex response

Secrets are not committed. Copy this template:

```text
C:\CODEX PG\CODEX Agent Hub\CODEX config\CODEX_notification_config.template.json
```

to this ignored local file:

```text
C:\CODEX PG\CODEX Agent Hub\CODEX config\CODEX_notification_config.local.json
```

Then set:

```json
{
  "enabled": true,
  "provider": "twilio"
}
```

and fill in either the `twilio`, `email_to_sms`, or `webhook` section.

Supported providers:

- `log_only`: records notification attempts locally, useful for testing without sending SMS.
- `twilio`: sends SMS through Twilio's Messages API.
- `email_to_sms`: sends to a carrier email-to-SMS gateway through SMTP.
- `webhook`: posts JSON to a notification relay you control.

Notification state and logs are local-only and ignored by git:

```text
C:\CODEX PG\CODEX Agent Hub\CODEX notifications
```

The app does not send old existing messages on first startup unless `send_existing_on_start` is set to `true`.

## Safety Boundary

Agent Hub messages are coordination only. They do not authorize implementation, writes to `C:\panda-gallery`, commits, pushes, installs, email sends, or any PHI-sensitive action. Darrin remains the approval gate.

Protected-action approval records live at:

```text
C:\CODEX PG\CODEX Agent Hub\CODEX approvals\CODEX_approval_records.local.jsonl
```

They are local/ignored records and must include scope, exact paths, command/provider, budget, expiry, one-time-use flag, approver, revocation state, and hash binding.

Live adapters are registered but disabled by default. The app exposes their safety status without launching Claude Code headless, calling APIs, sending paid SMS, or writing outside PAH.

Decision queue state lives at:

```text
C:\CODEX PG\CODEX Agent Hub\CODEX state\CODEX_decision_state.local.json
```

This file records local queue hygiene decisions, such as old mailbox items marked superseded. It does not edit the original mailbox messages.

Validation finding state lives at:

```text
C:\CODEX PG\CODEX Agent Hub\CODEX state\CODEX_validation_state.local.json
```

This file records local validator triage, such as old ledger findings accepted as legacy history.

Processed-message idempotency sidecars live at:

```text
C:\CODEX PG\CODEX Agent Hub\CODEX state\processed_messages
```

Each sidecar records the message ID, content hash, first-seen timestamp, last-seen timestamp, source path, and processed event names. Same ID plus same hash is treated as already processed for that event; same ID plus a different hash is blocked as a provenance mismatch.

Read/unread state lives at:

```text
C:\CODEX PG\CODEX Agent Hub\CODEX state\CODEX_read_state.local.json
```

This file stores local dashboard read markers only. If a message is edited after it is marked read, PAH shows it as unread again because the stored content hash no longer matches.

## Smoke Tests

Run dependency-free smoke tests:

```powershell
python "C:\CODEX PG\CODEX Agent Hub\CODEX_run_smoke_tests.py"
```

These tests cover schema roundtrip, Darrin decision gating, Claude Code routing, Panda Gallery path classification, and communication diagnostics.
They also cover current mailbox schema aliases, standalone validation, quarantine reason codes, backpressure detection, and processed-message idempotency sidecars.
Read/unread state is covered as well, including the changed-content-becomes-unread rule.

Validate one or more PAH mailbox messages directly:

```powershell
python "C:\CODEX PG\CODEX Agent Hub\CODEX_pah_validator.py" --json "C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\example.md"
```

Run the local server smoke test:

```powershell
& "C:\CODEX PG\CODEX Agent Hub\CODEX_run_server_smoke.ps1"
```

This starts PAH hidden, checks `/api/status`, prints a compact JSON result, and shuts the server down.

## Suggested Next Enhancements

1. Add a packaged Windows tray app with live desktop toasts.
2. Add explicit quarantine actions with tombstones.
3. Add direct API-backed agent lanes for OpenAI and Anthropic.
4. Add file/diff preview for deliverables.
5. Add approval-record enforcement for protected actions.
6. Add a closed-thread archive workflow.
