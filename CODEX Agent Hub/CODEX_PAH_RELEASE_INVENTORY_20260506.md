# CODEX PAH Release Inventory - 2026-05-06

Status: Draft inventory, no cleanup performed
Scope: `C:\CODEX PG\CODEX Agent Hub`
Generated from: `git status --short -- "CODEX Agent Hub"`

## Purpose

Classify current PAH-scoped dirty and untracked items before any release commit. This file does not stage, delete, move, or authorize cleanup.

## Summary

- Tracked modified PAH files: 6
- Untracked PAH paths: 7
- Items requiring owner confirmation before release: 3
- Items expected in the PAH final-state patch: 10

## Inventory

| Path | State | Classification | Release recommendation |
| --- | --- | --- | --- |
| `CODEX Agent Hub/CODEX_agent_hub.py` | modified | implementation change | Include after review. Contains PAH health/advisory/backup-scope changes. |
| `CODEX Agent Hub/CODEX_pah_inspector.py` | modified | implementation change | Include after review. Contains CC idle-sidecar advisory clarification. |
| `CODEX Agent Hub/CODEX_pah_periodic_health_check.py` | modified | implementation change | Include after review. Contains advisory backlog health classification. |
| `CODEX Agent Hub/CODEX_run_smoke_tests.py` | modified | test coverage | Include after review. Covers append-only ledger, advisory health, accepted advisories, and CC sidecar behavior. |
| `CODEX Agent Hub/pah_mailbox/atomic.py` | modified | implementation change | Include after review. Fixes append-only ledger write contention. |
| `CODEX Agent Hub/CODEX config/CODEX_pah_accepted_advisories.json` | untracked | configuration | Include after review if accepted-advisory policy remains desired. Review date is present. |
| `CODEX Agent Hub/CODEX_PAH_HEALTH_POLICY.md` | untracked | documentation | Include after review. Documents `ok` / `warn` / `err` policy. |
| `CODEX Agent Hub/CODEX_pah_repeat_health_verify.py` | untracked | verification tool | Include after review. Live integration verifier; not part of default smoke tests. |
| `CODEX Agent Hub/CODEX_PAH_EXCELLENT_FINAL_STATE_SPEC_v1.0.md` | untracked | spec/documentation | Include or supersede after review. Broader final-state spec. |
| `CODEX Agent Hub/CODEX_PAH_MINIMAL_REMAINING_FIXES_SPEC_v1.0.md` | untracked | spec/documentation | Include after review if this minimal path remains the canonical release note. |
| `CODEX Agent Hub/CODEX_agent_hub_ui.html` | modified | owner-confirmation needed | Do not include blindly. I did not edit this in the minimal PAH pass; verify whether it belongs to earlier approved PAH UI work or should stay parked. |
| `CODEX Agent Hub/CODEX mockups/` | untracked | owner-confirmation needed | Do not include blindly. Contains PAH health button mockup HTML/PNG artifacts from 2026-05-05. |
| `CODEX Agent Hub/tmp_capture_pah_header.py` | untracked | owner-confirmation needed | Do not include blindly. Looks temporary; confirm before deleting or excluding. |

## Release Recommendation

Safe release set, pending review:

- `CODEX_agent_hub.py`
- `CODEX_pah_inspector.py`
- `CODEX_pah_periodic_health_check.py`
- `CODEX_run_smoke_tests.py`
- `pah_mailbox/atomic.py`
- `CODEX config/CODEX_pah_accepted_advisories.json`
- `CODEX_PAH_HEALTH_POLICY.md`
- `CODEX_pah_repeat_health_verify.py`
- final chosen PAH spec document(s)

Hold until owner confirmation:

- `CODEX_agent_hub_ui.html`
- `CODEX mockups/`
- `tmp_capture_pah_header.py`

No cleanup has been performed.
