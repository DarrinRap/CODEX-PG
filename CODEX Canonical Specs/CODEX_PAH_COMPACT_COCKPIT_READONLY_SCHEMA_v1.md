# CODEX PAH Action Console Read-Only Schema v1

Status: draft for CC review before live implementation.

Scope: data contract for the first live PAH action-console slice. This slice is read-only: it renders agent state, an action queue, mailbox feed, selected-thread detail, route health, wake preview, diagnostics summary, and local git state. It does not send messages, grant approvals, start watchers, or write to Panda Gallery.

## Design Goals

- Single source of truth for every visible status.
- No disagreement between summary chips and detail panels.
- All potentially risky action affordances can render as disabled or confirmation-required from structured fields.
- The default screen answers: "What needs action right now?"
- Long raw Markdown is not required for the default console view.
- Unread messages older than 60 seconds are promoted to wake candidates.
- Feed, selected thread, route health, and decisions can be refreshed independently later without changing the schema.

## Top-Level Payload

```json
{
  "schema_version": 1,
  "generated_at": "2026-04-28T07:24:18-07:00",
  "cockpit_state": {},
  "agents": [],
  "action_queue": [],
  "wake_candidates": [],
  "feed": [],
  "selected_thread": {},
  "decisions": [],
  "routes": [],
  "wake": {},
  "diagnostics": {},
  "git": {},
  "read_only_actions": []
}
```

## cockpit_state

```json
{
  "as_of_iso": "2026-04-28T07:24:18-07:00",
  "mode": "live",
  "read_only": true,
  "active_filter": "needs_action",
  "density": "medium",
  "search_query": "PAH watcher",
  "routes_summary": {
    "total": 4,
    "pass": 3,
    "held": 1,
    "failed": 0,
    "untested": 0,
    "label": "3/4 routes pass; 1 held",
    "severity": "warn"
  },
  "counts": {
    "messages": 220,
    "unread": 12,
    "stale_unread": 2,
    "decisions_needed": 1,
    "actionable_checks": 7
  }
}
```

Rules:

- Top-bar route chip and route panel must both use `routes_summary`.
- `as_of_iso` must update on every successful refresh.
- `read_only: true` disables compose/send/write actions in v1.

## agents[]

```json
{
  "id": "claude_code",
  "code": "CC",
  "display_name": "Claude Code",
  "status": "warn",
  "status_label": "queued",
  "summary_line": "watcher awaits permission",
  "count_value": 5,
  "count_label": "queued",
  "meter_pct": 82,
  "meter_color": "warn",
  "last_activity_iso": "2026-04-28T08:06:00-07:00",
  "pulse": false
}
```

Allowed `status`: `active`, `idle`, `ok`, `warn`, `err`.

Rules:

- Bare numbers are not allowed in the UI; render `count_value` with `count_label`.
- `pulse: true` is reserved for real agent activity, not generic unread counts.

## feed[]

```json
{
  "id": "CC-PAH-COMPACT-COCKPIT-UX-REVIEW-20260428-073000",
  "thread_id": "PAH-COMPACT-COCKPIT-UX-20260428",
  "title": "PAH compact cockpit UX review",
  "sub": "Claude Code -> Codex / P0-P2 recommendations",
  "time_iso": "2026-04-28T07:30:00-07:00",
  "route_id": "claude_code_to_codex",
  "from_agents": ["claude_code"],
  "to_agents": ["codex"],
  "unread": true,
  "age_seconds": 74,
  "stale_unread": true,
  "wake_candidate_agent": "claude_code",
  "wake_candidate_label": "Claude Code",
  "badges": [
    {"kind": "wake", "label": "needs wake-up"},
    {"kind": "status", "label": "waiting_on_codex"},
    {"kind": "priority", "label": "high"}
  ],
  "message_path": "C:\\CODEX PG\\CODEX Claude Codex Mailbox\\CODEX Inbox\\20260428_073000_CC_to_CODEX_pah_compact_cockpit_ux_review.md"
}
```

Rules:

- Feed item title is one line.
- `sub` is one line and should include route or thread context.
- `stale_unread: true` means the message is unread and at least 60 seconds old.
- Stale unread messages must be visually promoted in the action queue.
- Raw message body is available through `message_path`, not displayed by default.

## action_queue[]

```json
{
  "id": "CC-PAH-COMPACT-COCKPIT-UX-REVIEW-20260428-073000",
  "kind": "wake",
  "severity": "warn",
  "title": "PAH compact cockpit UX review",
  "summary": "Unread 74s. Wake Claude Code.",
  "primary_action": "Wake Claude Code",
  "secondary_action": "Mark read",
  "message_path": "C:\\CODEX PG\\CODEX Claude Codex Mailbox\\CODEX Inbox\\20260428_073000_CC_to_CODEX_pah_compact_cockpit_ux_review.md",
  "thread_id": "PAH-COMPACT-COCKPIT-UX-20260428",
  "wake_line": "Read PAH-COMPACT-COCKPIT-UX-20260428 and reply to CODEX."
}
```

Allowed `kind`: `wake`, `decision`, `unread`.

Rules:

- `wake` items render first.
- Action copy must be plain language.
- The queue is the primary user workflow; route health and diagnostics stay secondary.

## wake_candidates[]

Same item shape as `feed[]`, filtered to stale unread messages. The first item drives the default wake line.

## selected_thread

```json
{
  "id": "PAH-WATCHER-WAKE-SERVICE-20260428",
  "title": "PAH watcher wake service",
  "state": "waiting_on_darrin",
  "owner": "darrin",
  "source": "Claude Code feedback",
  "route_id": "codex_to_claude_code",
  "next_action": "Review standing read scope",
  "facts": [
    {"label": "State", "value": "Waiting on Darrin"},
    {"label": "Next action", "value": "Approve read scope"},
    {"label": "Writes", "value": "None planned"},
    {"label": "Wake model", "value": "Copy line only"}
  ],
  "cards": [
    {
      "title": "Current gate",
      "body": "Confirm whether PAH may continuously read the native Claude Code mailbox under C:\\panda-gallery\\workflows\\cc_mailbox."
    }
  ],
  "primary_message_path": "C:\\CODEX PG\\CODEX Claude Codex Mailbox\\CODEX Inbox\\20260428_080000_CC_to_CODEX_pah_watcher_spec_feedback.md"
}
```

Rules:

- Detail cards can scroll inside the detail pane.
- No content is silently hidden based on viewport height.

## decisions[]

```json
{
  "id": "PAH-DECISION-STANDING-READ-CC-MAILBOX",
  "title": "Standing read permission",
  "sub": "PAH watcher reads CC mailbox continuously",
  "badge": "needed",
  "severity": "warn",
  "blocked_by": [],
  "actions": [
    {
      "id": "review_scope",
      "label": "Review scope",
      "kind": "confirm_required",
      "enabled": true,
      "requires_confirm": true
    },
    {
      "id": "route_outside_pg",
      "label": "Route outside PG",
      "kind": "secondary",
      "enabled": true,
      "requires_confirm": false
    }
  ],
  "scope_text": {
    "path": "C:\\panda-gallery\\workflows\\cc_mailbox\\",
    "read_frequency": "watchdog events plus 30 second reconciliation sweep",
    "writes": "watcher event log under C:\\CODEX PG only",
    "will_not_do": [
      "No headless wake",
      "No window automation",
      "No Panda Gallery writes outside approved coordination messages"
    ]
  }
}
```

Rules:

- Standing permissions never render as one-click approve.
- If `requires_confirm` is true, live UI must show scope text before final grant.
- Blocked rows use `blocked_by` IDs, not prose-only references.

## routes[]

```json
{
  "id": "codex_to_claude_code",
  "name": "Codex -> Claude Code",
  "source_path": "C:\\CODEX PG\\CODEX Claude Codex Mailbox\\CODEX_CLAUDE_CODE Inbox\\",
  "dest_path": "C:\\panda-gallery\\workflows\\cc_mailbox\\CC Inbox\\",
  "status": "pass",
  "hold_reason": "",
  "last_check_iso": "2026-04-28T07:24:18-07:00",
  "latency_ms": 420
}
```

Allowed `status`: `pass`, `held`, `failed`, `untested`.

Rules:

- Route panel and top summary derive from this list.
- `held` is not `pass`; it contributes to warning state.

## wake

```json
{
  "target_agent": "claude_code",
  "line": "Read PAH-WATCHER-WAKE-SERVICE-20260428 and reply to CODEX.",
  "route_status": "wake_candidate",
  "last_copy_iso": "",
  "direct_wake_supported": false,
  "safety_label": "Copy line only; Darrin pastes into Claude Code."
}
```

Rules:

- Direct wake remains unsupported.
- Copying the wake line does not send it anywhere.
- `wake_candidate` means a stale unread message is ready for Darrin to wake the target agent.

## diagnostics

```json
{
  "ok": true,
  "checks_total": 7,
  "checks_pass": 7,
  "checks_warn": 0,
  "checks_fail": 0,
  "actionable_validation_issues": 7,
  "last_run_iso": "2026-04-28T07:24:18-07:00"
}
```

## git

```json
{
  "branch": "main",
  "tracking": "origin/main",
  "clean": true,
  "status_label": "main synced with origin",
  "last_commit": "7ca1896"
}
```

## read_only_actions[]

```json
[
  {"id": "refresh", "label": "Refresh", "enabled": true},
  {"id": "validate", "label": "Validate", "enabled": true},
  {"id": "backup", "label": "Backup", "enabled": true},
  {"id": "compose", "label": "Compose", "enabled": false, "reason": "disabled in read-only v1"},
  {"id": "send", "label": "Send", "enabled": false, "reason": "no draft staged in read-only v1"}
]
```

## V1 Keyboard Map

- `/`: focus search.
- `J`: move feed selection down.
- `K`: move feed selection up.
- `Enter`: open selected message detail.
- `Ctrl+R`: refresh.
- `Esc`: clear selection or collapse expanded detail.
- `?`: show shortcut overlay.

## Explicitly Out of Scope for Read-Only v1

- Compose/send pipeline.
- Permission grant persistence.
- Watcher startup or continuous mailbox polling.
- Plan/Review modes.
- Headless wake or window automation.
- Any Panda Gallery write except already-approved coordination messages in a later non-read-only slice.
