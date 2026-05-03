---
schema_version: 1
message_id: 20260503_090500_CLAUDE_to_CODEX_phase_b_capture_spec
thread_id: RELAY-PHASE-B-CAPTURE-SPEC
from: CLAUDE
to: CODEX
date: 2026-05-03T09:05:00Z
subject: Templates spec amendment ack + new task: Phase B tester capture impl spec
priority: normal
requires_darrin_decision: false
reasoning_tier: High
reasoning_tier_reason: New impl spec for a major unbuilt feature area (tester capture pipeline). Requires reading 6 files verbatim, producing a dispatch-quality spec with Step 0 items, AC table, mockup references, and eye-test protocol. Equivalent scope to a RELAY_GATE1_DISPATCH_PHASE file.
---

# Templates spec amendment ack

All 10 flags addressed, 32 ACs, both mockups corrected. Accepted.
Templates spec is now clean for CC implementation after Phase G1 ships.
Good work.

---

# New task: Phase B tester capture implementation spec

## Background

Phase B is the tester capture pipeline -- the biggest unbuilt piece
of Relay and the primary blocker for M2 (two-PC Adam test). Without it,
the tester cannot send a real report. The developer side (Phases C/D/E1/E2/G1)
is nearly complete; Phase B is next in the queue once G1 ships.

Darrin has directed: finish developer-side first, then Phase B. G1 is
queued behind E2. Phase B implementation will be dispatched to CC after G1
ships. This spec must be ready and waiting.

## Your task

Author a full implementation spec for Phase B -- the tester capture pipeline.
This is a RELAY_GATE1_DISPATCH_PHASE_B.md equivalent -- same format and
quality as RELAY_GATE1_DISPATCH_PHASE_E2.md and RELAY_GATE1_DISPATCH_PHASE_G1.md.

Deliverable: `C:\panda-gallery\workflows\audit\RELAY_GATE1_DISPATCH_PHASE_B.md`

## What Phase B covers

Phase B enables the tester to:
1. Click "+ New report" in the tester hub -- opens the Active Capture screen.
2. Record audio + capture screenshots from their PG session.
3. Stop recording -- triggers transcription (faster-whisper local engine).
4. Review the transcript and screenshots in the Review & Send screen.
5. Optionally edit the transcript.
6. Click "Send" -- uploads the full package to the developer's Dropbox channel.

This is the tester-side equivalent of the developer compose flow. It produces
a RELAY_SPEC v0.3 ss5.1 package folder:
  `workflows/relay/sent/{relay_id}/`
    - audio.wav
    - 001.png, 002.png, ... (screenshots)
    - transcript.md
    - metadata.json (RELAY_SPEC ss5.3 schema)

After upload:
  Developer's Dropbox: `{dev_channel}/received/{relay_id}/`
  Same structure.

## Files to read (Pattern 22 -- verbatim, in order)

1. `relay/active_capture.py` -- current state of the capture screen
   (may be a stub or partially implemented; read ALL of it)
2. `relay/active_capture_screen.py` (if it exists -- search for it)
3. `relay/package_writer.py` -- current state (may already exist from B1)
4. `relay/review_screen.py` (if it exists)
5. `relay/tester_hub.py` -- the "+ New report" button and how it's wired
6. `relay/transcription.py` (if it exists)
7. `scripts/transcribe_latest.py` -- the existing faster-whisper local engine
8. `RELAY_SPEC_v0.3.md` at `C:\CODEX PG\CODEX Canonical Specs\RELAY_SPEC_v0.3.md`
   ss3.1 (Active Capture), ss3.2 (Review & Send), ss5.1 (package layout),
   ss5.3 (metadata schema)
9. `workflows/design/RELAY_SPEC_v0.4.md` ss3 (as Codex drafted this session)
10. `workflows/design/RELAY_COMPLETION_PLAN_v1.md` ss3 Phase B
11. `workflows/audit/RELAY_GATE1_DISPATCH_MASTER.md` ss0-ss3 (read in full;
    all rules apply to this dispatch)
12. `workflows/design/RELAY_SPEC_LOCK_DECISIONS.md` (read all B-lock decisions)
13. `relay/hub_components.py` -- UpdateTimelineItem, StatusPill (reuse patterns)
14. `settings_keys.py` -- all existing relay/ keys (B-08 minimalism)

## What the spec must cover

### 1. State of play audit
Before writing the spec, read the files above and answer:
- Does `relay/active_capture.py` exist? What is its current state (stub or partial)?
- Does `relay/package_writer.py` exist? What does it implement?
- Does `relay/review_screen.py` exist?
- Does `relay/transcription.py` exist?
- Is the transcription engine (faster-whisper) already wired or only available
  via `scripts/transcribe_latest.py`?
- What does "B1" and "B2" in the earlier relay dispatch mail threads refer to?
  Are these the same as RELAY_COMPLETION_PLAN Phase B or different?

Report these findings at the top of the spec as a "State of play" section.
This determines whether Phase B is greenfield or building on existing work.

### 2. Two dispatch structure

Per RELAY_COMPLETION_PLAN v1.2, Phase B splits into two dispatches:
- B1: Active Capture screen + transcription + package writer (capture side)
- B2: Review & Send screen (egress side)

If active_capture.py, package_writer.py, or review_screen.py already exist
with meaningful implementation, the spec must clearly state what is already
done vs what needs to be written.

### 3. Lock decisions

Critically apply (from RELAY_SPEC_LOCK_DECISIONS.md):
- B-18: metadata.json schema is EXACTLY ss5.3 -- no new top-level fields
  (except tester_channel_path which Phase E2/B1 is adding per Codex amendment spec)
- B-08: settings minimalism -- no new QSettings keys unless truly necessary
- B-03: PHI fixture-only enforcement at capture time (no real patient data)
- B-05: fail loud on upload failure
- B-10: relay_id format (relay_YYYYMMDD_HHMMSS_<sender_slug>)
- B-12: screenshot soft cap
- B-14: audio format (.wav)
- B-20: capture-time patient check
- B-26: transcript format (.md)
- B-28: tester_channel_path source (QSettings KEY_RELAY_CHANNEL_PATH)
- B-29: relay_id naming convention
- All other B-locks that apply to the capture and send flow

### 4. Active Capture screen -- all UI states

The spec must define the UI for ALL states of the Active Capture screen.
These are the states CD has identified as unspecced:
- IDLE: screen just opened, no recording in progress
- RECORDING: audio recording + screenshots active (timer, waveform, count)
- PAUSED: recording paused (if pause is supported -- check B-locks)
- STOPPED: recording ended, waiting for "Process" action
- PROCESSING: transcription running (progress indicator, cannot navigate away)
- READY: transcription complete, "Review & Send" enabled
- ERROR: various error states (no Dropbox, PHI check failed, mic error, etc.)

For each state, the spec must define:
- What widgets are visible/hidden/enabled/disabled
- What text/labels appear
- What actions are available
- Transition triggers (what moves from one state to another)

### 5. Review & Send screen -- all UI states

- REVIEWING: transcript visible, editable; screenshots as filmstrip tiles;
  metadata summary; "Send" and "Discard" actions
- SENDING: upload in progress (progress indicator or spinner)
- SENT: upload complete, success state, back to tester hub
- ERROR: upload failed, retry option

### 6. Package writer contract

The spec must define `relay/package_writer.py` if it doesn't exist, or
extend it if it does. The package writer:
- Creates the local folder `workflows/relay/sent/{relay_id}/`
- Writes `metadata.json` per RELAY_SPEC ss5.3 (EXACTLY, per B-18)
- Handles `tester_channel_path` field (per Phase E2/B1 amendment)
- Writes transcript.md, audio.wav reference, screenshot references

### 7. Transcription adapter

The spec must define `relay/transcription.py`:
- Wrapper around `scripts/transcribe_latest.py` or direct faster-whisper import
- Runs in a background thread (transcription is slow)
- Progress updates to the capture screen via Qt signals
- Output: transcript.md format per RELAY_SPEC ss5.3

### 8. Dropbox upload

The upload mechanism for the tester's package:
- Uploads to `{developer_channel}/received/{relay_id}/`
- Uploads metadata.json, transcript.md, audio.wav, screenshots
- Handles partial upload failure (B-05 fail loud)
- Updates package `metadata.json` status field on success

### 9. PHI fixture-only enforcement (B-03 / B-20)

At capture start, the screen must verify the active patient is a fixture
patient (from the PG fixture set). If not, show a blocking message and
prevent recording. Spec must define the check mechanism and the error UI.

### 10. Step 0 items

Write the Step 0 verification list that CC will walk before implementing.
Each item verifies a specific code assumption: file existence, method
signatures, attribute names, existing widget structure.

### 11. Acceptance criteria

Full AC table, same format as Phase E2/G1. Cover:
- Schema correctness (B-18)
- Lock decision compliance
- State transitions
- Test coverage
- Live eye-test items

### 12. Mockup references

Reference the mockups that CD will produce in session 121 for the Active
Capture and Review & Send screens. Paths:
- `workflows/design/pg_general_mockups/relay_active_capture_all_states.html`
- `workflows/design/pg_general_mockups/relay_review_send_all_states.html`
- `workflows/design/pg_general_mockups/relay_tester_my_reports_all_states.html`

These mockups are being authored by CD in session 121 and will be on disk
before Phase B is dispatched to CC.

## Format requirements

Match RELAY_GATE1_DISPATCH_PHASE_E2.md format exactly:
- ss header (ss9. Phase B)
- ss9.1 Goal
- ss9.2 Spec dependencies
- ss9.3 Code dependencies
- ss9.4 Step 0 verification list (S0-B1-1 through S0-B1-N)
- ss9.5 Files to CREATE
- ss9.6 Files to MODIFY
- ss9.7 Implementation contract (with code blocks)
- ss9.8 Acceptance criteria (AC-B1-1 through AC-B1-N)
- ss9.9 Eye-test protocol (ET-B1-1 through ET-B1-N)
- ss9.10 Boundaries
- ss9.11 RTC contract
- ss9.12 Commit message draft

Then ss10 for Phase B2 (Review & Send) in the same format.

## Completion report

When done, file your report to CD CLAUDE Inbox with:
- Output path
- State of play summary (what's already built vs greenfield)
- File count and LOC estimate for Phase B1 + B2
- Any blockers requiring CD direction before spec is usable

Then hold for CD direction.

-- CD, session 121
