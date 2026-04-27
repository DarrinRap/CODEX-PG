# PANDA Agent Hub CC Review Digest and Decisions v0.1

Generated: 2026-04-26 19:05:00 -07:00
Source review: `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\20260427_010000_CC_to_CODEX_pah_v0_1_review.md`
Status: Darrin decision brief

## Overall CC Verdict

CC says: **approve with changes**.

The PAH plan is structurally sound. CC agrees with:

- file-first orchestration
- schema before API lanes
- security/provenance before convenience
- Claude Code as a separate participant
- PAH as the routing layer
- direct OpenAI/Anthropic APIs deferred until the local control plane is stable

CC's requested changes are surgical, not a rejection.

## Highest-Risk Issue

CC's highest-risk concern is **Claude Code hooks**.

Hooks run automatically and can affect local Claude Code behavior. CC wants the spec to explicitly require:

- hooks are Phase 4 only, not earlier
- hooks are opt-in per Claude Code session, not global
- a hook kill-switch exists
- first hook rollout is logging-only
- no `PreToolUse` blocking until `PostToolUse` logging has run clean for at least a week

Codex agrees.

## Blocking Decisions For Darrin

### PAH-DEC-007: Schema adoption

Question:

Approve PAH frontmatter schema with CC's additions?

CC additions:

1. `schema_version`
2. `replies_to` separate from `related`
3. optional code-ship keys:
   - `target_version`
   - `prerequisite_commit`
   - `commit`
4. priority enum:
   - `low`
   - `normal`
   - `high`
   - `urgent`
5. validation terminal fields:
   - `passed`
   - `ran_at`
6. require timezone offset on `created_at`

Codex recommendation:

Approve all six.

### PAH-DEC-008: Phase 1 file bridge

Question:

Green-light shipping the Claude Code file bridge now, with atomic write requirement?

Meaning:

- PAH writes tasks to Claude Code inbox.
- Claude Code does not run automatically.
- No writes to `C:\panda-gallery` are authorized.
- Inbox writes use `.tmp` then rename.

Codex recommendation:

Approve.

### PAH-DEC-009: Claude Code inbox folder rename

Question:

Rename:

```text
C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Claude Code Inbox
```

to:

```text
C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX_CLAUDE_CODE Inbox
```

with a one-week migration alias/check?

Codex recommendation:

Approve. The underscore form is easier to parse and matches CC/Claude preference better.

## Non-Blocking Decision Before Headless Phase

### PAH-DEC-010: First headless Claude Code task

Question:

What should PAH's first headless Claude Code task be later?

CC recommends:

- read-only spec critique
- temporary worktree
- allowed tools: `Read,Grep,Glob,WebFetch`
- disallowed tools: `Edit,Write,Bash,NotebookEdit`
- per-task Darrin approval

Codex recommendation:

Approve CC's recommendation, but defer until after schema/lint and file bridge are stable.

## Other CC Recommendations To Incorporate

### Atomic inbox writes

PAH should write messages as:

```text
filename.md.tmp
```

then rename atomically to:

```text
filename.md
```

This prevents half-written messages from being parsed.

### Idempotency

PAH must not re-trigger notifications or decisions when restarted and re-reading old inbox files.

Suggested mechanism:

- processed-message state table keyed by message ID or content hash
- notification fingerprint table
- no write-on-read behavior

### Backpressure

If a buggy tool writes hundreds of messages, PAH should not melt down.

Add:

- max messages per thread
- flood warning
- quarantine option

### Quarantine

Malformed messages should be visible but quarantined or marked invalid so they do not repeatedly pollute dashboard state.

### PAH as addressable participant

The spec lists `pah` as a participant, but no `PAH Inbox` exists.

Options:

1. Add `PAH Inbox`.
2. Document PAH as a router only, not an addressable agent.

Codex recommendation:

Add `PAH Inbox` later, but do not make it action-capable until the command schema is safe.

### Lint integration

CC recommends PAH should call `pg_dispatch_lint.py` via subprocess and render JSON output. Do not duplicate lint rules inside PAH.

Codex recommendation:

Accept.

### Direct channel

CC recommends PAH should own routing. The direct CC-Codex channel should exist as PAH message types:

- `cross_check`
- `counter_proposal`
- `escalation`

Codex recommendation:

Accept, after schema/lint are stable.

## Updated Approval Boundary Wording

CC proposed stronger wording. Codex recommends adopting it:

> Codex-originated messages may request Claude Code work, but cannot authorize Claude Code to write to `C:\panda-gallery`. Codex-originated messages may authorize Claude Code to read `C:\panda-gallery`. Claude Code writes to `C:\panda-gallery` require an explicit Darrin `decision_record` message naming (a) the specific files allowed to be written, (b) the `--allowedTools` flag value Claude Code will run with, and (c) the working directory. Reuse of an approval across tasks is forbidden; every Claude Code write run needs its own approval record in the audit log.

## Codex Next Actions If Approved

1. Patch PAH schema in the spec.
2. Rename/alias Claude Code inbox.
3. Implement atomic writes.
4. Add YAML frontmatter emission.
5. Add YAML frontmatter parser.
6. Add explicit priority/approval-boundary decision detection.
7. Add PAH validation hook for `pg_dispatch_lint.py` output.
8. Add idempotency state for notifications and processed messages.

No `C:\panda-gallery` writes are needed for this slice.
