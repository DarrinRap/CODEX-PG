# PANDA Agent Hub Integration Access Research v0.2

Generated: 2026-04-26 20:05:00 -07:00
Status: Design research addendum
Scope: Claude Desktop, Claude Code / CC, Codex, PAH local mailbox, SMS/push notification lanes

## Executive Finding

PAH can support practical two-way coordination among Codex, Claude Desktop, and Claude Code, but it should not pretend that all three have identical integration surfaces.

The safe v1 architecture is a local control plane with:

- file-backed message queues as the source of truth
- schema/lint validation before routing
- explicit participant registry
- PAH-owned routing and provenance
- optional adapter lanes that are enabled only after approval

Direct "app to app chat" is not one API. It is a set of adapters with different trust boundaries.

## Local Evidence Collected

### Claude Code CLI

Local command:

- `claude --version` returned `2.1.120 (Claude Code)`.
- `claude --help` confirmed headless print mode, JSON/stream-JSON output, tool allow/deny flags, permission modes, settings, MCP config, no-session-persistence, max budget, hooks stream events, and worktree flags.
- `claude mcp --help` confirmed MCP add/list/get/remove plus `claude mcp serve`.
- `claude agents --help` confirmed a configured/background agent surface.

Local config directory exists at:

- `C:\Users\drrap\.claude`

Only filenames were inspected. Secret-bearing contents were not read.

### CC Lint Tool

Canonical lint tool:

- `C:\panda-gallery\workflows\tools\pg_dispatch_lint.py`

Read-only help confirms:

```text
pg_dispatch_lint.py [-h] [--strict] [--json] path
```

Read-only lint run against CC's PAH review returned `ok: true`, `n_errors: 0`, `n_warnings: 4`.

Important integration implication:

- PAH should call this tool by subprocess and render JSON.
- PAH should not fork/rewrite lint rules internally.
- Current warnings indicate schema vocabulary convergence is still needed: `cc` participant alias, `review_complete` status value, Bible lookup root, and one cited example path.

## Official Integration Surfaces

### Claude Desktop / Claude Code Desktop

Official Claude Code Desktop docs describe a Code tab inside Claude Desktop with:

- local sessions
- remote cloud sessions
- SSH sessions
- parallel sessions with Git worktree isolation
- connectors
- scheduled tasks
- Dispatch from phone
- push notifications when sessions finish or need approval
- shared Claude Code settings and project memory between CLI and Desktop Code sessions

Design implication:

- Claude Desktop is not merely a passive mailbox reader.
- It can become a first-class PAH participant through mailbox messages now and through an MCP/extension lane later.
- Claude Desktop chat MCP configuration and Claude Code Code-tab MCP configuration are separate surfaces and must not be conflated.

### Claude Code Headless

Official CLI and Agent SDK docs support non-interactive automation through:

- `claude -p`
- `--output-format text|json|stream-json`
- `--input-format text|stream-json`
- `--allowedTools`
- `--disallowedTools`
- `--tools`
- `--permission-mode`
- `--max-budget-usd`
- `--max-turns`
- `--mcp-config`
- `--strict-mcp-config`
- `--settings`
- `--no-session-persistence`
- `--include-hook-events` with stream JSON

Design implication:

- PAH can eventually call Claude Code headlessly.
- First headless tasks must be read-only review jobs.
- Every live Claude Code run is a cost/external-agent action and needs explicit Darrin approval until PAH has a signed approval record flow.
- Recommended first command class:

```text
claude -p "<review task>" --output-format json --permission-mode plan --allowedTools "Read,Grep,Glob,WebFetch" --disallowedTools "Edit,Write,Bash,NotebookEdit" --no-session-persistence --max-budget-usd <approved cap>
```

No live headless Claude Code run was executed during this research because it could spend tokens or invoke external services.

### Claude Code MCP

Official MCP docs confirm:

- Claude Code can connect to external MCP servers.
- Claude Code itself can run as an MCP server with `claude mcp serve`.
- Claude Desktop can be configured to use Claude Code as an MCP server.
- The MCP client is responsible for user confirmation for individual tool calls when Claude Code's tools are exposed through MCP.

Design implication:

- PAH can later expose its own MCP server so Claude Desktop or Claude Code can ask PAH for thread state, decision state, and message routing.
- PAH can also orchestrate Codex or Claude Code through MCP server modes, but that should be Phase 4+ because approvals, session identity, and audit logs must be solid first.

### Claude Code Hooks

Official hooks docs confirm lifecycle events including:

- `PreToolUse`
- `PostToolUse`
- `PostToolUseFailure`
- `Notification`
- `PermissionRequest`
- `UserPromptSubmit`
- `Stop`
- `SessionStart`
- `SessionEnd`
- `FileChanged`

Hooks can block or influence tool calls depending on event and JSON output.

Design implication:

- Hooks are powerful and risky.
- PAH must follow CC's recommendation: hooks are Phase 4 only, opt-in per Claude Code session, logging-only first, kill-switch required, and no `PreToolUse` blocking until logging has run clean for a week.
- Hook configuration must avoid polluting CC's normal Panda Gallery work.

### Claude Code Remote Control and Dispatch

Official Remote Control docs confirm:

- local Claude Code sessions can be controlled from claude.ai/code or the Claude mobile app
- the local process keeps running locally
- mobile push notifications can fire when Claude needs a decision or finishes long-running work
- Remote Control requires Claude Code v2.1.51+ and Claude.ai subscription authentication
- mobile push requires v2.1.110+
- connections use outbound HTTPS and do not open inbound machine ports

Official Desktop docs confirm Dispatch can send tasks from phone into Desktop Code sessions and push when finished or needing approval.

Design implication:

- PAH does not need to own every notification channel immediately.
- Claude Code native mobile push is useful for Claude Code sessions.
- PAH still needs its own notification lane for cross-agent mailbox state, because Codex/Claude/PAH decisions are not automatically Claude Code session events.

### Codex Integration

Official OpenAI Codex docs confirm:

- `codex exec` supports non-interactive script/CI mode.
- JSON Lines output is available with `codex exec --json`.
- default non-interactive sandbox is read-only.
- broader permissions are explicit flags.
- Codex SDK can programmatically control local Codex agents.
- Codex can run as an MCP server via `codex mcp-server`.

Design implication:

- PAH should eventually support Codex as a callable adapter.
- For current Codex Desktop collaboration, mailbox plus human-visible dashboard is safer than trying to drive this active Codex session externally.
- Future Codex adapter can mirror the Claude Code adapter shape: read-only first, explicit approval, JSON/structured output, audit record.

### SMS Notifications

Official Twilio Programmable Messaging docs confirm:

- outbound SMS uses the Messages resource through HTTPS APIs
- Twilio recommends API keys for production authentication
- Account SID/Auth Token can be used for local testing
- SMS compliance and user consent matter
- deprecated Twilio Notify should not be used for new SMS work

Design implication:

- PAH should use Programmable Messaging, not Twilio Notify.
- SMS must be opt-in and local-configured.
- Secrets must live outside mailbox files and be gitignored.
- The default provider remains `log_only`.
- Darrin decides which events deserve phone interruption.

## Adapter Ranking

### Phase 1: File Bridge

Status: use now.

Capabilities:

- works with current mailbox habits
- readable by all agents
- easy to audit
- no paid API calls
- no hidden external action

Requirements:

- atomic write `.tmp` then rename
- schema v1 frontmatter
- quarantine malformed files
- idempotent processing
- participant registry
- separate `CODEX_CLAUDE_CODE Inbox`

### Phase 2: Watcher Bridge

Status: after schema lands.

Capabilities:

- near-real-time dashboard updates
- stale-thread alerts
- notification triggers

Requirements:

- read-only watcher first
- no auto-processing replies without policy
- dedupe and cooldown table

### Phase 3: Headless Agent Bridge

Status: approval-gated.

Capabilities:

- PAH can ask Claude Code or Codex for structured review
- supports agent voting without Darrin manually moving files

Requirements:

- per-run approval record
- cost cap
- tool allow/deny list
- working directory scope
- no-session-persistence by default
- JSON output capture
- timeout and cancellation
- audit log

### Phase 4: MCP and Hooks

Status: future.

Capabilities:

- PAH can be queried as a tool by Claude Desktop / Claude Code
- Codex/Claude Code can be orchestrated by MCP clients
- hook events can feed PAH state

Requirements:

- paranoid review
- kill switch
- logging-only first
- local/project/user scope control
- session opt-in
- no global hook pollution

## Direct Two-Way Conversation Answer

Yes, PAH can enable practical two-way conversation between Codex, Claude Desktop, and Claude Code, but the first reliable implementation should be message-router based rather than real-time chat transport.

Recommended v1 behavior:

- PAH owns message identity, thread identity, routing, and audit.
- Agents exchange structured messages through participant inboxes.
- Dashboard displays the conversation as a unified thread.
- Darrin sees only decision-worthy items.
- CC/Codex direct collaboration becomes PAH message types: `cross_check`, `counter_proposal`, and `escalation`.

Recommended future behavior:

- Claude Desktop can use a PAH MCP server to query/send messages.
- Claude Code can be invoked headlessly for approved review tasks.
- Codex can be invoked through `codex exec`, Codex SDK, or Codex MCP server after the same approval model exists.
- Remote Control/Dispatch can be documented as an adjacent Claude-native lane, not the PAH core.

## Sources

- Claude Code CLI reference: https://code.claude.com/docs/en/cli-usage
- Claude Agent SDK overview: https://code.claude.com/docs/en/agent-sdk/overview
- Claude Code hooks reference: https://code.claude.com/docs/en/hooks
- Claude Code MCP: https://code.claude.com/docs/en/mcp
- Claude Code Desktop: https://code.claude.com/docs/en/desktop
- Claude Code Remote Control: https://code.claude.com/docs/en/remote-control
- Claude Desktop local MCP support: https://support.claude.com/en/articles/10949351-getting-started-with-model-context-protocol-mcp-on-claude-for-desktop
- OpenAI Codex non-interactive mode: https://developers.openai.com/codex/noninteractive
- OpenAI Codex SDK: https://developers.openai.com/codex/sdk
- OpenAI Codex MCP server guide: https://developers.openai.com/codex/guides/agents-sdk
- Twilio Programmable Messaging API: https://www.twilio.com/docs/sms/api

