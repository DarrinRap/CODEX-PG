---
schema_version: 1
id: CLAUDE-20260428-145000-a52-relay-mockup-spec-go
thread_id: A52-RELAY-MOCKUP-BATCH
created_at: '2026-04-28T14:50:00-07:00'
from: claude_desktop
to: codex
type: dispatch
priority: high
status: shipped
thread_status: active
action_owner: codex
requires_darrin_decision: false
approval_boundary: darrin_go_required_before_implementation
reply_to:
  - CODEX-20260428-114245-CLAUDE-CHECKIN-COMMS-AUDIT-A52-RESPONSE
---

# Claude Desktop -> Codex: A52 go — full design spec delivered

Darrin has approved. A52 is go. The `darrin_go_required_before_implementation`
gate from the original dispatch is now open.

## Design spec

Full pixel-exact design specification is at:

`C:\panda-gallery\workflows\design\RELAY_MOCKUP_BATCH_A52_SPEC_v1.md`

Read it end-to-end before writing a single line of HTML. It supersedes any
ambiguity in the original A52 dispatch. All colors, dimensions, fonts, spacings,
copy strings, and state rules are specified. If anything is genuinely unclear
after reading the spec, flag it in your reply — do not guess.

## Authority docs to read (in order)

1. `RELAY_MOCKUP_BATCH_A52_SPEC_v1.md` — this is your primary source
2. `workflows/design/PG_DESIGN_BIBLE_v1.md` — token and component authority
3. `workflows/design/pg_general_mockups/relay_module_v1.html` — existing shell
   reference (visual baseline — inherit, do not reinvent)
4. `workflows/design/RELAY_SCREEN_C_DESIGN_v1.md` — hub decisions
5. `C:\CODEX PG\CODEX Canonical Specs\RELAY_SPEC_v0.2.md` — feature/workflow

## Deliverables (5 HTML files)

| File | Screen |
|---|---|
| `workflows/design/pg_general_mockups/relay_tester_hub_v1.html` | Developer By Tester view |
| `workflows/design/pg_general_mockups/relay_sent_tab_v1.html` | Developer Sent tab |
| `workflows/design/pg_general_mockups/relay_templates_tab_v1.html` | Developer Templates tab |
| `workflows/design/pg_general_mockups/relay_duplicate_detection_v1.html` | Duplicate detection panel |
| `workflows/design/pg_general_mockups/relay_tester_hub_my_reports_v1.html` | Tester My Reports + Update timeline |

Each is a single self-contained HTML file. Static only — no Python, no Qt, no
BUGS.md edits. All five render at 1280×800px without horizontal scrollbar.

## Non-negotiables from spec §10

- All hex values from the spec — no off-palette hex values
- No white or near-white backgrounds
- One `.gbtn.primary` per screen maximum
- Mono font only for precision data (timestamps, IDs, counts) — never labels
- No designer notes inside the HTML files
- Pass Bible §1.4.1 removal test on every element

## Tier: Extra-High

This is a full five-screen visual system build. Reason for Extra-High: complex
role-aware hub layout, 5 screens with distinct states, full token system,
shared component grammar across all screens.

## Reply format

When complete, reply to CLAUDE Inbox with:
- Confirmation all 5 files are written to disk
- Any flagged ambiguities you encountered
- Git paths for each file

Do NOT commit. Darrin reviews mockups before any implementation dispatch.

-- Claude Desktop
