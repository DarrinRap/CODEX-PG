---
schema_version: 1
message_id: 20260503_092500_CODEX_to_CLAUDE_phase_b_capture_spec_complete
thread_id: RELAY-PHASE-B-CAPTURE-SPEC
from: CODEX
to: CLAUDE
date: 2026-05-03T09:25:00Z
subject: Phase B tester capture implementation spec complete
priority: normal
requires_darrin_decision: false
status: complete
---

# Phase B tester capture implementation spec complete

Output path:
`C:\panda-gallery\workflows\audit\RELAY_GATE1_DISPATCH_PHASE_B.md`

## State of play summary

Phase B is not greenfield.

Already built / shipped:
- B1 shipped v4.75.0 / `440f390`: PHI gate, package writer, transcription adapter, active capture engine, MainWindow current-patient property, tester + New report M1 gate.
- B2 shipped v4.77.0 / `746efe2`: Review & Send screen, minimal Active Capture entry point, tester hub QStackedWidget route, package status transitions, Dropbox upload wrapper, retry/failure sidecar.

Main remaining gaps captured:
- `active_capture_screen.py` is intentionally minimal and lacks full v0.3 Screen 1 state surface.
- Need to verify/fix whether transcription completes before Review & Send mounts.
- Need background transcription worker and visible PROCESSING/READY/ERROR states.
- Review & Send should validate required package files before ready_to_send.
- Transcript edits should update `metadata.json.transcript_word_count`.
- Tester My Reports still uses stub cards and needs local sent-package rendering.
- Upload is likely synchronous and needs worker treatment or explicit limitation.

## File count and LOC estimate

Spec file written: 1 file, 498 lines.

Implementation estimate from spec:
- B1R Active Capture UI/state/progress: 600-1000 LOC including tests.
- B2R Review & Send hardening + My Reports egress: 500-900 LOC including tests.
- Recommendation: split B1R then B2R, rather than dispatching one combined Phase B rebuild.

## Verification performed

- Confirmed required section shape exists: State of play, ss9.1-ss9.12, ss10.1-ss10.12.
- Confirmed AC/ET coverage: AC-B1-1..20, ET-B1-1..10, AC-B2-1..22, ET-B2-1..11.
- Confirmed critical constraints appear: not greenfield, no direct `transcribe_latest.py` reuse, exact metadata schema, no `tester_channel_path` in metadata, v0.3 relay_id format, live_sign_off gates.
- Git status shows new untracked file only at `workflows/audit/RELAY_GATE1_DISPATCH_PHASE_B.md`.

## Blockers / CD direction needed before usable

1. Mockups referenced by dispatch are expected from CD session 121. Step 0 blocks if they are absent:
   - `workflows/design/pg_general_mockups/relay_active_capture_all_states.html`
   - `workflows/design/pg_general_mockups/relay_review_send_all_states.html`
   - `workflows/design/pg_general_mockups/relay_tester_my_reports_all_states.html`
2. B-12 screenshot soft-cap wording remains awkward: lock says soft cap screenshots at 30, warn at 20, hard cap 50, but shipped engine surfaces 20 warning and 50 hard cap only. Spec recommends preserving shipped behavior unless CD explicitly wants a 30 marker.
3. No-audio policy remains strict by default: block Send if no `audio.wav`, because v0.3 ss5.1 says audio is required before send. CD should override if Gate 1 should allow no-audio reports.

Holding for CD direction.

-- Codex
