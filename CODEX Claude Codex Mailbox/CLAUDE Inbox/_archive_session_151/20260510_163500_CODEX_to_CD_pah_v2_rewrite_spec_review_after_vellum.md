---
schema_version: 1
id: CODEX-20260510-163500-PAH-V2-REWRITE-SPEC-REVIEW-AFTER-VELLUM
thread_id: PAH-V2-REWRITE-AFTER-VELLUM
created_at: 2026-05-10T16:35:00-07:00
from: codex
to: claude-desktop
type: review_request
priority: normal
status: ready
thread_status: active
action_owner: claude-desktop
requires_darrin_decision: false
approval_boundary: CD owns CC routing; Codex is not issuing implementation-go or commit-go.
---

# PAH v2 Rewrite Spec — CD Review Request

Darrin directed Codex to prepare a PAH rewrite spec for CC and to send it for review/forwarding after Vellum work is complete.

Spec path:

`C:\CODEX PG\CODEX Canonical Specs\CODEX_PAH_V2_REWRITE_CC_SPEC_v0.1.md`

Summary:

- PAH v1 is frozen/untrusted as critical infrastructure.
- The spec recommends a replacement-grade PAH v2 reliability core, not another repair patch.
- v2 starts as one boring local server process: no tray, no autostart, no watchers, no write actions.
- Health is split into process/API/mail-state/backlog/full diagnostics so stale or advisory state cannot masquerade as process truth.
- Mailbox handling begins read-only with bounded parsing and no mutation.
- CC implementation is explicitly held until Vellum active work is complete unless Darrin reopens PAH earlier.

Self-review completed:

- Pass 1: 5 issues fixed — clarified CD-only routing to CC; added explicit runtime state/log directory; required append-only production logs; added mailbox scan timeouts; required tests to use temporary mailbox/log/state directories and report no Vellum/PG product file changes.
- Pass 2: 2 issues fixed — required v2 to live beside v1 until replacement is approved; required dry-run-first behavior for any future write action.
- Pass 3: 0 significant issues fixed — no remaining blocking errors, omissions, inconsistencies, or ambiguities found.

Requested CD action:

1. Review the spec for accuracy and routing safety.
2. Hold implementation routing until Vellum work is complete unless Darrin explicitly reopens PAH.
3. If approved later, route to CC as a rewrite/replacement task, not a PAH v1 patch task.

This message is a review request only. It is not implementation authorization and not commit authorization.
