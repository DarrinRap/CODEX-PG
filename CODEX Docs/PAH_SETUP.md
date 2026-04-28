# PAH Setup and Operating Notes

Updated: 2026-04-28
Owner: Codex
Status: active

## Purpose

This document records the Panda Agent Hub (PAH) setup used for coordination
between Codex, Desktop Claude, Claude Code, and Darrin.

PAH is a local file-based coordination hub. It indexes the mailbox folders,
validates message hygiene, writes routed messages, runs communication
diagnostics, and tracks route tests.

## Runtime

PAH app:

```text
C:\CODEX PG\CODEX Agent Hub\CODEX_agent_hub.py
```

Default local URL:

```text
http://127.0.0.1:8765
```

Manual start command:

```powershell
python "C:\CODEX PG\CODEX Agent Hub\CODEX_agent_hub.py" --host 127.0.0.1 --port 8765 --no-browser
```

The server should run with one active Python process serving port `8765`.

## Mailbox Roots

Codex / Desktop Claude mailbox:

```text
C:\CODEX PG\CODEX Claude Codex Mailbox\
```

Native Claude Code mailbox:

```text
C:\panda-gallery\workflows\cc_mailbox\
```

Bridge protocol:

```text
C:\CODEX PG\CODEX Claude Codex Mailbox\CC_CODEX_BRIDGE_PROTOCOL_v1.md
```

User manual:

```text
C:\CODEX PG\CODEX Docs\PAH_USER_MANUAL.html
```

## Participants

- `codex`: Codex in the CODEX PG workspace.
- `claude_desktop`: Desktop Claude.
- `claude_code`: Claude Code.
- `darrin`: human approval gate and Claude Code wake bridge.

## Canonical Routes

### Codex -> Desktop Claude

Route id:

```text
codex_to_claude
```

Inbox:

```text
C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\
```

### Desktop Claude -> Codex

Route id:

```text
claude_to_codex
```

Inbox:

```text
C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\
```

### Codex -> Claude Code

Route id:

```text
codex_to_claude_code
```

Canonical PAH inbox:

```text
C:\panda-gallery\workflows\cc_mailbox\CC Inbox\
```

This is the live-tested PAH route and the canonical route for new PAH-routed
Codex -> Claude Code messages.

### Claude Code Replies

PAH watches the native Claude Code reply lane:

```text
C:\panda-gallery\workflows\cc_mailbox\CLAUDE Inbox\
```

Replies should include a structured `thread_id`, `Reply-To`, or `reply_to`
field that references the source message id.

### Secondary / Legacy Direct Lane

The older Codex mailbox lane remains available as a compatibility path:

```text
C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX_CLAUDE_CODE Inbox\
```

It is secondary in PAH v1. New PAH-routed messages should use the native
Claude Code mailbox path above unless a message explicitly names the legacy
path.

## Setup Work Completed

PAH was updated to bridge the real Claude Code mailbox instead of only the
PAH-local legacy inbox.

Changed areas:

- `pah_mailbox\paths.py`
  - Added Panda Gallery / native Claude Code mailbox constants.
  - Routes `codex_to_claude_code` to
    `C:\panda-gallery\workflows\cc_mailbox\CC Inbox\` when available.
  - Keeps the PAH-local Claude Code inbox visible as legacy history.
- `pah_diagnostics\route_tests.py`
  - Route tests now look for Claude Code replies in the native CC reply lane.
  - `codex_to_claude_code` route tests write reply instructions that point to
    the native reply path.
- `pah_diagnostics\checks.py`
  - Adds a native Claude Code mailbox diagnostic.
  - Two-way bridge checks now include Codex, Desktop Claude, and native CC
    paths.
- `CODEX_agent_hub.py`
  - Indexes native CC mailbox traffic.
  - Adds Panda Gallery root to the safe-open allowlist for local navigation.
  - Updates source-route contracts for CC mailbox lanes.
- `CODEX_run_smoke_tests.py`
  - Adds smoke coverage for the native CC mailbox route and reply-search path.

Local PAH bridge backup commit:

```text
9d53c27 CODEX backup 2026-04-28 PAH native Claude Code mailbox bridge
```

Note: that local commit was not pushed directly from `main` during setup
because the local branch also contains mailbox-message commits. The setup
documentation can be pushed independently on a clean documentation branch.

## Live Verification

Local tests completed:

- Python compile check: passed.
- PAH smoke tests: passed.
- PAH server smoke: passed.
- Communication diagnostics: 7/7 passed.
- Dashboard HTML load: passed.
- Safe-open endpoint for Panda Gallery mailbox path: passed.
- Live `/api/status`: diagnostics OK.

Observed live status during setup:

```text
diagnostics_ok: true
messages indexed: 189
route_tests: 1 received_reply, 1 pending_reply
```

Live route tests:

- Codex -> Claude Code:
  - Test id:
    `PAH-ROUTE-TEST-20260427-211258-codex_to_claude_code`
  - Result: `received_reply`.
  - ACK:
    `C:\panda-gallery\workflows\cc_mailbox\CLAUDE Inbox\20260427_211400_CC_to_CODEX_pah_route_test_ack.md`
- Codex -> Desktop Claude:
  - Test id:
    `PAH-ROUTE-TEST-20260427-211258-codex_to_claude`
  - Result: delivered, still pending exact route-test ACK at the time of this
    document.

Claude Code review:

- CC reviewed the PAH bridge code.
- Verdict: no blocking issues.
- Report:
  `C:\panda-gallery\workflows\cc_mailbox\CLAUDE Inbox\20260427_213000_CC_to_CODEX_pah_code_review.md`

CC noted three optional low-risk improvements:

- `CLAUDE_CODE_INBOX` is evaluated at import time.
- Raw-text fallback route-test matching could false-positive if a test id is
  quoted in an unrelated message.
- Native CC directories are not created by `ensure_runtime_dirs()`, though
  they already exist in this setup and are created on demand by message writes.

## Wake Policy

Darrin selected the semi-manual wake model.

PAH/Codex should:

1. Write the CC task/review request to:

   ```text
   C:\panda-gallery\workflows\cc_mailbox\CC Inbox\
   ```

2. If Claude Code appears idle, give Darrin a paste-ready wake line.
3. Darrin pastes that line into the active Claude Code session.
4. Claude Code reads the message and replies through:

   ```text
   C:\panda-gallery\workflows\cc_mailbox\CLAUDE Inbox\
   ```

Default wake line:

```text
Read C:\panda-gallery\workflows\cc_mailbox\CC Inbox now. Darrin asks you to respond to the latest PAH/Codex message.
```

Specific wake line format:

```text
Read C:\panda-gallery\workflows\cc_mailbox\CC Inbox\<message_filename>.md and respond to Darrin's PAH/Codex request.
```

## Safety Policy

Do not use `--dangerously-skip-permissions` for PAH-controlled Claude Code
wakeups.

No unattended headless Claude Code wake adapter is enabled.

Any future automatic wake adapter requires:

- explicit Darrin approval,
- a narrow prompt file,
- restricted tools,
- no permission bypass,
- audit records,
- idempotency / queueing,
- clear path-boundary handling for `C:\panda-gallery`.

Mailbox messages do not authorize:

- repo writes,
- commits,
- pushes,
- destructive filesystem actions,
- package installs,
- paid API calls,
- SMS/email sends,
- unattended headless agent runs.

Darrin's foreground approval remains required for protected actions.

## Notification State

PAH notification support is scaffolded, but live SMS is not enabled.

Current notification mode during setup:

```text
provider: log_only
live_delivery_ready: false
real_sms_ready: false
```

This means PAH can log notification tests locally, but it is not configured to
send a real SMS until Darrin provides and approves a live provider setup.

## Common Commands

Run smoke tests:

```powershell
python "C:\CODEX PG\CODEX Agent Hub\CODEX_run_smoke_tests.py"
```

Run server smoke:

```powershell
& "C:\CODEX PG\CODEX Agent Hub\CODEX_run_server_smoke.ps1"
```

Check live PAH status:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8765/api/status"
```

Check PAH process:

```powershell
Get-CimInstance Win32_Process |
  Where-Object { $_.Name -eq "python.exe" -and $_.CommandLine -like "*CODEX_agent_hub.py*" }
```

## Open Items

- Desktop Claude still needs to send an exact ACK for the PAH
  `codex_to_claude` route test if complete route-test parity is required.
- Consider reconciling `CC_PROTOCOL.md` wording so it clearly matches this
  setup doc's canonical native PAH route.
- Consider adding a hermetic test for `refresh_route_tests()` detecting a real
  reply file in `CC_CLAUDE_INBOX`.
- Consider adding comments or startup handling for the import-time
  `CLAUDE_CODE_INBOX` selection.
- Keep using Darrin-in-the-loop wake until a safer headless adapter is
  explicitly approved.

