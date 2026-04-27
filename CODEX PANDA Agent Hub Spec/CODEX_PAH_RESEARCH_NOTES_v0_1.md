# PANDA Agent Hub Research Notes v0.1

Generated: 2026-04-26 18:50:00 -07:00
Status: Draft research brief
Scope: Implementation research for PANDA Agent Hub (PAH), a local multi-agent coordination cockpit for parallel development with minimal Darrin input.

## Research Goal

Identify the current integration surfaces, risks, and implementation choices needed to turn the current PAH prototype into a reliable local-first agent coordination product.

The research is focused on time-saving implementation choices, not broad market exploration.

## Local Context Reviewed

- Current PAH prototype: `C:\CODEX PG\CODEX Agent Hub`
- Current mailbox root: `C:\CODEX PG\CODEX Claude Codex Mailbox`
- Claude holding reply: `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\20260427_000100_CLAUDE_to_CODEX_panda_hub_holding_reply.md`
- CC schema/direct-channel proposal, read-only reference:
  `C:\panda-gallery\workflows\cc_mailbox\CLAUDE Inbox\20260426_233000_CC_to_CLAUDE_proposal_dispatch_schema_and_direct_channel.md`

## Key Findings

### 1. Local-first file orchestration is the right v1 backbone

PAH's main value is not "chat with two models." It is reducing Darrin's coordination burden while preserving approval boundaries. The file mailbox is already durable, inspectable, git-trackable, and compatible with Codex, Claude Desktop, Claude Code, and CC.

Recommendation:

- Keep v1 file-first.
- Add schema, lint, dashboard, routing, notifications, and audit log before adding direct model APIs.
- Treat direct OpenAI/Anthropic API lanes as phase 3+, not the foundation.

### 2. OpenAI integration should target Responses API first

OpenAI's Responses API is the current general-purpose model response interface for stateful interactions, multimodal inputs, custom function calls, and built-in tools. Official OpenAI docs describe it as supporting text/image inputs, text outputs, conversation state through previous responses or conversations, and tools such as function calling, file search, web search, code interpreter, MCP, shell, and apply patch.

Implications for PAH:

- If PAH later creates its own Codex-like API lane, use Responses API.
- Represent PAH operations as explicit function tools with strict schemas.
- Disable or gate write-capable tools behind Darrin approval.
- Use metadata fields to tag PAH thread IDs, participant IDs, and task IDs.
- Use conversation state only where the trace/history remains bounded and auditable.

Sources:

- OpenAI Responses API reference: https://platform.openai.com/docs/api-reference/responses/compact?api-mode=responses
- OpenAI tools guide: https://platform.openai.com/docs/guides/tools?api-mode=responses
- OpenAI migration guidance: https://platform.openai.com/docs/guides/migrate-to-responses
- OpenAI authentication guidance: https://platform.openai.com/docs/api-reference/authentication?api-mode=responses

### 3. OpenAI Agents SDK is useful later for managed handoffs, guardrails, and traces

The OpenAI Agents SDK supports handoffs between agents, guardrails, and tracing. Its official docs call out guardrails around model input/output and tools, and tracing for model generations, tool calls, handoffs, and guardrails.

Implications for PAH:

- Do not make Agents SDK a v1 dependency.
- Consider it when PAH moves from passive mailbox coordination to active multi-agent runs.
- Guardrails map well to PAH's safety policy: no secrets, no PHI, no unapproved writes, no external sends without confirmation.
- Tracing maps well to PAH's audit log and post-run review.

Sources:

- OpenAI Agents SDK overview: https://platform.openai.com/docs/guides/agents-sdk/
- OpenAI Agents SDK guardrails: https://openai.github.io/openai-agents-python/guardrails/
- OpenAI Agents SDK handoffs: https://openai.github.io/openai-agents-python/handoffs/
- OpenAI Agents SDK tracing: https://openai.github.io/openai-agents-python/tracing/

### 4. Anthropic direct API lane should use Messages API, but Claude Code is a separate integration

Anthropic's API overview identifies the Messages API (`POST /v1/messages`) as the primary conversational API. Authentication uses `x-api-key`; JSON is accepted and returned. Direct model prompting through the Messages API is different from Claude Code automation.

Implications for PAH:

- If PAH later adds a "Claude API" lane, use Anthropic Messages API.
- This does not replace Claude Code integration.
- Claude Code should be treated as a tool-running local participant, not just a model endpoint.

Sources:

- Anthropic API overview: https://docs.anthropic.com/en/api/overview
- Anthropic client SDKs: https://docs.anthropic.com/en/api/client-sdks
- Anthropic streaming Messages docs: https://docs.anthropic.com/claude/reference/messages-streaming

### 5. Claude Code can integrate through headless mode and hooks

Official Claude Code docs describe headless mode using `claude -p` / `--print` for non-interactive automation and options such as `--output-format`, `--resume`, `--continue`, `--allowedTools`, `--disallowedTools`, and `--permission-mode`.

Claude Code hooks can run shell commands at lifecycle events, including `PreToolUse`, `PostToolUse`, `Notification`, `UserPromptSubmit`, `Stop`, `SubagentStop`, `SessionStart`, and `SessionEnd`. Hooks receive JSON via stdin and can return exit codes or structured JSON. The docs specifically call out notifications, automatic formatting, logging, feedback, and custom permissions as hook use cases.

Implications for PAH:

- Best v1.5 bridge: file mailbox plus optional watcher.
- Best v2 bridge: Claude Code headless adapter for bounded tasks.
- Best v2 safety layer: hooks that log tool use and block unapproved writes.
- Do not let Codex messages directly authorize Claude Code writes to `C:\panda-gallery`.
- If PAH launches Claude Code, it must pass explicit allowed/disallowed tools and write policies.

Sources:

- Claude Code headless mode: https://docs.claude.com/en/docs/claude-code/sdk/sdk-headless
- Claude Code SDK overview: https://docs.anthropic.com/s/claude-code-sdk
- Claude Code hooks reference: https://docs.anthropic.com/en/docs/claude-code/hooks
- Claude Code hooks quickstart: https://docs.anthropic.com/en/docs/claude-code/hooks-guide

### 6. SMS can be implemented safely with Twilio, email-to-SMS, or webhook relay

Twilio's Messages resource creates outbound messages via `POST https://api.twilio.com/2010-04-01/Accounts/{AccountSid}/Messages.json`. Twilio requires recipient, sender, and content, and notes trial-mode recipient verification and queue/rate behavior.

Implications for PAH:

- Keep SMS optional and disabled by default.
- Store credentials only in ignored local config.
- Implement notification cooldown, dedupe fingerprints, and first-run baseline suppression.
- Use short messages that do not include secrets, PHI, or sensitive file contents.

Sources:

- Twilio SMS quickstart: https://www.twilio.com/docs/messaging/quickstart
- Twilio Messages resource: https://www.twilio.com/docs/sms/api/message
- Twilio SMS tutorial: https://www.twilio.com/docs/messaging/tutorials/how-to-send-sms-messages

### 7. Local web write endpoints still need CSRF-style defenses

OWASP describes CSRF as a malicious site tricking an authenticated browser into performing unwanted actions on a trusted site. Even a localhost app can be targeted if it accepts unauthenticated writes from a browser. OWASP recommends token-based mitigation, custom headers for API requests, origin verification, avoiding state-changing GET requests, and defense in depth.

Implications for PAH:

- Keep write endpoints POST-only.
- Require a per-run secret write token sent in a custom header.
- Check Origin/Host when Origin is present.
- Do not expose secrets in URLs or logs.
- Add explicit confirmation for high-impact operations.

Sources:

- OWASP CSRF Prevention Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html

### 8. CC's schema proposal should be merged, not ignored

CC independently proposed YAML frontmatter, a direct CC-Codex channel, and `pg_dispatch_lint`. The schema proposal has strong overlap with PAH's metadata needs.

Implications for PAH:

- PAH should not invent a conflicting schema.
- PAH v0.2 should adopt a schema that is compatible with CC's proposed frontmatter while preserving the existing `Message-ID` / `Reply-To` fields during transition.
- Lint should be integrated into PAH as an explicit validation page and preflight check.
- Direct agent-to-agent channel should be gated by message type and escalation rules.

## Implementation Guidance From Research

### Build Order

1. Harden local prototype:
   - read-only status endpoint
   - token-protected writes
   - no inbound spoofing
   - separate Claude Code inbox
   - local-only notification config
2. Add message schema:
   - YAML frontmatter parser
   - existing header compatibility
   - thread status model
   - participant IDs
   - approval fields
3. Add validation/lint:
   - missing metadata
   - stale open threads
   - unresolved Darrin decisions
   - unapproved write requests
   - deliverable path checks
4. Add PAH dashboard:
   - Darrin decision queue
   - active threads
   - participant lanes
   - notification state
   - validation panel
5. Add Claude Code bridge:
   - separate inbox
   - optional watcher
   - optional headless `claude -p`
   - hooks for logging and write blocking
6. Add API lanes only after the above is stable:
   - OpenAI Responses adapter
   - Anthropic Messages adapter
   - guardrails and cost controls

### Risks To Avoid

- Letting agent messages imply Darrin approval.
- Allowing Codex to trigger Claude Code writes to `C:\panda-gallery`.
- Creating competing metadata schemas across PAH and CC.
- Sending SMS notifications for old backlog items on first startup.
- Polling endpoints that mutate files.
- Storing API keys, phone numbers, or tokens in git.
- Adding direct model APIs before the local control plane is trustworthy.

## Open Research Questions

1. Which Claude Code installation/version is present locally, and does it support the newest hook/defer features?
2. Should PAH use PySide6 as a desktop shell around the local server, or keep a browser UI for v1?
3. Which SMS provider will Darrin prefer: Twilio, email-to-SMS, webhook relay, or phone push via another service?
4. Should PAH eventually be repo-local per project, or one global app with multiple project workspaces?
5. Should direct OpenAI/Anthropic API lanes run locally with Darrin's keys or route through a managed service later?
