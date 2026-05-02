# PAH Reliability and Design Spec

Status: active reminder spec
Last updated: 2026-04-30 22:10 -07:00

## Purpose

PAH must not look healthy while the communication path is stale, partially broken, or visually misleading. This spec records the rules learned from the 2026-04-29 communication and styling incident.

For detailed product/UX direction, including live screenshots and the Mail-first user-console target, use:

```text
C:\CODEX PG\CODEX Agent Hub\CODEX_PAH_MAIL_AND_INSPECTOR_UX_SPEC.md
```

That file is now the canonical PAH Mail + Inspector UX reference. This reliability/design spec remains the compact rulebook for health, safety, and visual guardrails.

## Critical Regression Rule

The current PAH state must be treated as suspect until proven otherwise. The user reported a MASSIVE REGRESSION: PAH functionality appears broken and the Inspector screen fonts are wrong. Future PAH debugging must diagnose before changing code:

1. Do not guess. Gather concrete evidence from code, live endpoints, live browser DOM/CSS, screenshots, and PG Design Bible references.
2. Double-check the diagnosis before applying a fix. Record expected behavior, observed behavior, likely root cause, and the files/surfaces involved.
3. Verify fixes in the live browser and live Inspector. Smoke tests alone do not prove the Inspector screen is visually or operationally correct.
4. If targeted fixes do not quickly restore known-good behavior, consider reverting PAH to an earlier known-good version and re-applying only verified changes.

## Mailroom Reliability Rules

1. A passing Inspector must include a live transaction canary, not only endpoint existence or dry-run checks.
2. The transaction canary must exercise send, read-state, reply tombstone, and interaction-ledger writes.
3. Canary writes must be isolated from real mailboxes and clean up after themselves.
4. `/api/send`, `/api/message-read-state`, and `/api/mark-all-read` remain supported compatibility routes until all clients and operator habits are migrated.
5. `/api/health` must expose stale Inspector evidence as a warning. Old green reports are not current health.
6. Route health must expose problem route details, not only aggregate pass counts.

Acceptance:

- `python -m py_compile` passes for PAH source files.
- `CODEX_run_smoke_tests.py` passes.
- Live Inspector includes `endpoint.mailroom_transaction_canary`.
- Live `/api/health` includes `components.inspector` and `components.routes.problem_routes`.

## Mediated Messaging Reliability Rules

2026-05-02 implementation addendum:

1. PAH must separate physical mailbox facts, derived PAH state, authority projections, and Darrin approval authority.
2. Darrin approval is the only authority for implementation-approved, commit-approved, backup-approved, publish-approved, protected-write-approved, or `C:\panda-gallery` write states.
3. PAH may write sanitized local shadow snapshots under `CODEX Agent Hub\CODEX state`, but snapshot files must not persist raw mailbox bodies by default.
4. `/api/ready` is the fast readiness contract. Server smoke must not use heavyweight `/api/status` as startup proof.
5. The `mediated_messaging` health component must report delivery/visibility state as evidence, not as proof of Claude Desktop pickup unless read/ack evidence exists.
6. `complete_pending_cd_review` and equivalent explicit review-pending metadata remain open on the reviewing agent until ack/reply evidence exists.
7. `ready_to_commit` and other protected boundaries remain Darrin-gated even when an agent says the work is ready.
8. State-builder profiles must stay available until hot endpoints are snapshot-backed. The 2026-05-02 pass moved full schema validation off cockpit's hot path and reduced hot-path `validate_mailbox` time from about 7.4s to about 22ms.
9. Cockpit hot refresh must not run side-effectful message discovery/classifier audit writes. Use `message_audit_summary` on the cockpit path; reserve full `audit_messages_and_thread_states` ledgering for explicit full-state or audit flows.
10. Stale periodic monitor reports must be visible but must not masquerade as current failures. Reports older than the freshness window are warnings with preserved failed-check detail, not current `/api/health` errors.

## Classifier And Wake Rules

1. Explicit coordination-only shares that say no action or no reply is required are closed/informational, even if their frontmatter still says `status: open` for traceability.
2. Stale-unread wake candidates must be classifier-aware. PAH may wake on unread `open_on_agent` or `owner_unknown` messages; it must not wake on closed, parked, or Darrin-waiting items.
3. Stale-unread wake candidates must be thread-aware. Older unread messages in a thread with later completion/shipped/closed evidence must not stay on the wake list.
4. The Inspector communication backlog warning is for real unresolved agent work, not every physically unread historical mailbox artifact.

Acceptance:

- No-action coordination shares classify as `closed`.
- Completed threads suppress older stale-unread wake candidates.
- Tray stale-unread count matches cockpit wake candidates.
- Live Inspector shows no communication backlog or stale-unread warning when only closed/no-action/completed-thread mail remains unread.

## Agent Activity Tracking Rules

1. PAH tracks CC activity only when the CC sidecar exists at `C:\panda-gallery\workflows\cc_mailbox\_state\active_dispatch.json`.
2. PAH tracks Codex activity through the Codex mailbox SLA card and unread/urgent state.
3. A missing CC sidecar is a warning about missing live tracking, not proof that CC is idle.
4. `ready_for_human_loop` suppresses stale-file and compose-cap alarms because CC is waiting on Darrin after filing durable mailbox evidence.
5. The dashboard must expose a dedicated Claude Code Activity panel with status, sidecar age, target disk-write age, mailbox fallback disk-write age, target count, scanned-file count, issues, and recommended action.
6. A manual Check Now action must recompute CC activity from disk through `/api/cc-activity` without relying on stale cockpit refresh state.

## Visual Design Rules

PAH inherits the Panda Gallery Design Bible for user-facing surfaces:

1. Body/prose/labels use `--font-ui`: `"Segoe UI", "SF Pro", "Noto Sans", sans-serif`.
2. `--font-mono` is reserved for precision data only: paths, IDs, counts, timestamps, shortcuts, versions, and file names.
3. Surface backgrounds stay on the dark navy scale: `#14141f`, `#161625`, `#1a1a2e`, `#22223a`, `#2a2a4e`.
4. Pale, white, cream, or near-white alert panels are forbidden.
5. Required tokens: text `#e0ddd5`, muted `#888888`, dim `#555555`, accent `#e8a87c`, warning `#f39c12`, error `#e74c3c`.
6. Inspector status must be glanceable: pass/warn/fail/overall counts should be visible in the top band with color-coded status badges, while raw report text remains secondary.
7. Inspector and PAH status controls may use semantic color for borders, text, dots, and glyphs only. Their backgrounds must remain Bible surface tokens; do not use full amber/red/green tinted panels.
8. Inspector status tiles and chips must be actionable. `PASS`, `WARN`, and `FAIL` reorder the findings list by that status; `OVERALL` restores severity order.
9. Colored buttons are allowed only when they encode action meaning: primary refresh/accent, secondary open/report, close/danger. Do not turn every control into a rainbow.
10. PAH action buttons use the Design Bible `.gbtn` grammar: 28px height, 4px radius, Bible surface backgrounds, semantic borders, and UI-font labels.
11. Enabled safe actions must carry a green activatable affordance; disabled safe actions stay grey/muted; destructive or emergency actions retain warning/error treatment.
12. Shape semantics are strict: pills are passive status/category/information; rectangles are actions. A clickable pill-looking control is a visual bug.
13. PAH uses a 26px `--chrome` statusbar with `.statusbar` / `.sb-*` grammar. Oversized footer bars are regressions.
14. PAH must not expose PANDA Collaborator registration, onboarding, or account-creation screens. `Register User`, `Registration`, `Onboarding`, or `Create account` copy inside PAH is a regression.
15. Visual changes that touch fonts, colors, borders, animation, or background require live visual review; headless checks are useful but not sign-off.

## Mail And Inspector UX Rule

Darrin's 2026-04-30 direction is that PAH must become a simple way to see mail and respond to it. The default user experience should be Mail-first:

1. Mail is the primary surface: inbox, unread, needs-me, CD, CC, all, reader, and reply composer.
2. Inspector is the health/evidence surface: pass/warn/fail counts, freshness, actionable findings, and raw report as secondary evidence.
3. The legacy cockpit is Advanced: useful, preserved, but not the default first screen for Darrin.
4. Every visual PAH/Inspector change must update or validate against `CODEX_PAH_MAIL_AND_INSPECTOR_UX_SPEC.md`.
5. Screenshots are required evidence for meaningful PAH/Inspector UX changes.

2026-04-30 Bible polish addendum: Simple Mail must not use monospace for prose; the reader must show subject/meta/body before raw frontmatter; read/unread must be one neutral state-aware toggle; Reply/Send is the primary peach action; timestamps must follow today/yesterday/weekday/older-date formatting. Full details live in `CODEX_PAH_MAIL_AND_INSPECTOR_UX_SPEC.md`.

2026-04-30 PAH visual-reset addendum: PAH is not a registration wizard. Keep PAH mail/inspector surfaces on the PG Design Bible dark surface scale, use `.gbtn` for action buttons, keep enabled safe commands green, reserve primary treatment to one clear action per surface, and verify with smoke tests, Inspector, and live browser inspection before handoff.

## Documentation Rule

Every PAH incident-response or implementation pass must update durable docs before handoff:

- README for operational behavior and support procedures.
- TODO for reminders and deferred work.
- This spec or its successor for product, reliability, UX, safety, protocol, and acceptance rules.
- `CODEX_PAH_MAIL_AND_INSPECTOR_UX_SPEC.md` for Mail/Inspector product behavior, UI structure, screenshots, and CC/CD collaboration context.

Mailbox messages are coordination artifacts. They do not replace durable docs.
