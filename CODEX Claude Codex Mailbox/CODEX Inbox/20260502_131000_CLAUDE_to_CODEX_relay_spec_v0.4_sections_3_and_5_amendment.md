---
schema_version: 1
id: CD-20260502-131000-RELAY-V0.4-SECTIONS-3-AND-5
thread_id: RELAY-V0.4-SECTIONS-3-AND-5-AUTHORING
from: claude_desktop
to: codex
type: dispatch
priority: high
status: actionable
thread_status: active
action_owner: codex
requires_darrin_decision: true
approval_boundary: directive
tier_recommendation: High
tier_rationale: >
  Spec authoring against an existing skeleton with strict Pattern 22
  discipline. ~2-3K LOC of spec content across §3 and §5 plus minor
  amendments to neighboring sections where lock decisions intersect.
  Lower tier than Dispatch B because the skeleton, lock decisions, and
  predecessor spec are already authored \u2014 this is reconciliation work,
  not greenfield architecture.
sequencing: After Dispatch B (`20260502_130500_CLAUDE_to_CODEX_roundtrip_v1.1_lock.md`) ships.
---

# RELAY_SPEC v0.4 — author §3 (tester capture pipeline) and §5 (settings panel)

This dispatch is **second in queue** behind the round-trip v1.1 lock
(Dispatch B). Execute v1.1 first; then this one. Both dispatches land in
your inbox at the same time.

---

## 0. Procedural preamble — Pattern 22 retrospective

A previous attempt at this work shipped a dispatch that had 5
canonical-source failures. Listing them so this dispatch doesn't recur:

1. Cited `§3.6` of v0.3 with a wrong section identifier.
2. Invented `severity` and `linked_relay_ids` fields in the v0.3 §5.3
   metadata.json schema. Both were fabricated; the canonical schema does
   not have them.
3. Fabricated `from_developer` / `to_tester` field names in the v0.3 §5.4
   status update schema. The canonical schema uses `sender_name` /
   `recipient_name`.
4. Contradicted B-29 (subsequently OVERRIDDEN to v0.3 §5.1 canonical
   format).
5. Missed B-11 through B-32 lock decisions (22 entries) by reading only
   the top 60 lines of `RELAY_SPEC_LOCK_DECISIONS.md`.

Pattern 22 corrective measures for this dispatch:

- Read `RELAY_SPEC_v0.3.md` in full, end to end. No partial reads.
- Read `RELAY_SPEC_LOCK_DECISIONS.md` in full, all 32 entries (B-01
  through B-32). No reading a partial range.
- Read `RELAY_SPEC_v0.4.md` in full. The skeleton CD authored is the
  delivery target.
- Schema fields are quoted verbatim from v0.3 §5.3 / §5.4. No memory.
  No paraphrase. If you don't have the canonical text in front of you,
  reread.
- B-29 is OVERRIDDEN — the v0.3 §5.1 format
  (`relay_YYYYMMDD_HHMMSS_<sender_slug>`) is canonical. The override
  marker in `RELAY_SPEC_LOCK_DECISIONS.md` is the authority.

If during authoring you find that a dispatch instruction or my paraphrase
disagrees with your verbatim canonical read, your canonical read wins.
Surface in Codex inbox.

---

## 1. Goal in one paragraph

`RELAY_SPEC_v0.4.md` is a CD-authored skeleton at
`C:\panda-gallery\workflows\design\RELAY_SPEC_v0.4.md` with §0 drafted and
§1–§12 + A–C stubbed. v0.4 supersedes v0.3 once locked, but lock criteria
require all sections to reach `[VERIFIED]` status. This dispatch asks
Codex to author **§3 (Tester capture pipeline)** and **§5 (Settings
panel)** from `[STUB]` to `[DRAFTED]`, applying every lock decision in
`RELAY_SPEC_LOCK_DECISIONS.md` that bears on those sections, and
verifying every schema reference verbatim against v0.3. After §3 and §5
are drafted, surface any cross-section dependencies (locks that touch
§2, §4, §6, §7, §10, §11, etc.) for CD to schedule follow-up dispatches.

---

## 2. Step 0 — canonical reads BEFORE drafting (Pattern 22)

Required reads (in this exact order; no skipping):

1. **`C:\CODEX PG\CODEX Canonical Specs\RELAY_SPEC_v0.3.md`** — read in
   full, all 16 sections (§1 Overview through §16 Tester Setup Flow).
   This is the authoritative predecessor. Every schema field, every
   recommended API method signature, every state value comes from this
   document — verbatim.
2. **`C:\panda-gallery\workflows\design\RELAY_SPEC_LOCK_DECISIONS.md`** —
   read all 32 entries (B-01 through B-32). NOTE the OVERRIDE on B-29.
   Lock decisions take precedence over v0.3 wording where they conflict.
3. **`C:\panda-gallery\workflows\design\RELAY_SPEC_v0.4.md`** — read in
   full. Confirm exact section numbering, draft state, and sub-bullets
   already drafted vs stubbed.
4. **`C:\panda-gallery\workflows\design\RELAY_GATE1_DEFERRED_FEATURES.md`** —
   read in full. Cuts apply to v0.4 scope; do not include features
   listed here in §3 or §5.
5. **`C:\panda-gallery\workflows\design\RELAY_COMPLETION_PLAN_v1.md`** —
   read in full (this is the v1 file; v1.1 / v1.2 may exist; read
   whichever is canonical at this moment per the file's own header).
6. **`C:\panda-gallery\workflows\design\RELAY_HUB_IMPL_SPEC_v1.1.md`** —
   read in full. Hub UI shipped at v4.74.1 + v4.73.0 polish + BUG160
   structural rebuild. §3 and §5 must compose with the shipped hub.
7. **`C:\panda-gallery\workflows\design\RELAY_TESTER_SETUP_IMPL_SPEC_v1.md`** —
   read in full. Setup wizard shipped via L26+L27. §5 settings panel
   composes with the wizard (D5 / B-26 — wizard handshake unchanged).
8. **`C:\panda-gallery\workflows\design\PG_DESIGN_BIBLE_v1.md`** — read
   §6 (Component grammar), §10 (Patient/data fixtures, especially #11
   the fixture set for B-03 PHI gate), §11 (Vocabulary).
9. **`C:\panda-gallery\BUGS.md` #157, #158, #159, #160, #161, #162, #163,
   #164** — read each entry. Open Relay polish items inform §3 (capture
   pipeline UX) and §5 (settings panel UX) compliance.
10. **`C:\panda-gallery\relay\active_capture.py`** — read in full.
    Shipped at v4.75.0 / `440f390`. The B1 capture engine is the §3
    code reference; spec must match shipped behavior or explicitly
    flag divergence with rationale.
11. **`C:\panda-gallery\relay\package_writer.py`** — read in full.
    Shipped at v4.75.0. metadata.json schema implementation.
12. **`C:\panda-gallery\relay\transcription.py`** — read in full.
    Shipped at v4.75.0.
13. **`C:\panda-gallery\relay\phi_gate.py`** — read in full. Shipped
    at v4.75.0. The B-03 PHI fixture-set enforcement.
14. **`C:\panda-gallery\relay\settings_panel.py`** — read in full.
    Current settings panel implementation. §5 spec must reflect the
    shipped surface or flag divergence.
15. **`C:\panda-gallery\workflows\audit\REPEATED_ERRORS.md`** — Pattern
    22 in full (the pattern this dispatch enforces).
16. **`C:\panda-gallery\workflows\audit\WORKING_RULES_v1.md`** — read
    v5 dispatch authoring gate.

If any read disagrees with this dispatch, surface in Codex inbox before
drafting.

---

## 3. CD's findings from the deep review (handoff)

### 3.1 v0.4 §3 (Tester capture pipeline) — sub-section authoring map

v0.4 §3 has the following sub-section stubs (verbatim from the
skeleton):

- 3.1 Active capture screen (Screen 1) — UI, hotkeys, recording state
  machine, screenshot trigger
- 3.2 Review & send screen (Screen 2) — transcript edit, filmstrip,
  discard, send
- 3.3 Capture-time PHI enforcement (per B-03)
- 3.4 Transcription integration (per B-21 + B-29)
- 3.5 Package writer (per B-14)
- 3.6 State transitions and rollback

Author each sub-section with detail comparable to v0.3 equivalents:

**§3.1 Active capture screen.** Map to v0.3 §3.1 (Screen 1 - Tester:
Active Capture). Carry forward v0.3's required-elements list and behavior
list verbatim where unchanged. Apply locks: B-03 (PHI gate at start), B-12
(audio soft cap 600s, screenshot warn at 20 / hard cap at 50), B-14
(single folder layout). Cross-reference shipped active_capture.py state
machine (IDLE → RECORDING → STOPPED / ABORTED).

**§3.2 Review & send screen.** Map to v0.3 §3.2 (Screen 2 - Tester:
Review & Send). Carry forward v0.3's required elements verbatim where
unchanged. Apply locks: B-05 (fail loud + manual retry on send failure),
B-10 (discard + editable transcript on Screen 2), B-29 OVERRIDDEN
(`relay_YYYYMMDD_HHMMSS_<sender_slug>` format). Note: this section will
be implemented by CC's Phase B B2 dispatch landing in parallel; the spec
text and the implementation contract should match.

**§3.3 Capture-time PHI enforcement.** Map to v0.3 — there is no v0.3
section for this; the PHI gate is a Gate 1 addition per B-03. Author
fresh: cite Bible §10 #11 fixture set; cite shipped `phi_gate.py` for
the implementation; describe the refusal UX (PG returns
`PhiGateError`; `active_capture` does not emit a Qt Signal — uses
plain Python error per B1 AC3). Hard-coded; no toggle; no dialog
per B-03.

**§3.4 Transcription integration.** Map to v0.3 §6 (Relationship to
Existing Modules) sub-bullets on transcription. Reuse policy via
`scripts/transcribe_latest.py` is the v0.4 lock per B-baked during plan
v1.2 revision. Note: v0.3 references `transcribe_latest.py` but locked
behavior is faster-whisper local; B1 actually shipped library-import
transcription via `relay/transcription.py` (faster-whisper directly).
Reconcile this divergence in the spec — flag the change explicitly.

**§3.5 Package writer.** Map to v0.3 §5.1 (Local Folder Layout) +
§5.3 (metadata.json schema). Carry forward both schemas verbatim.
Apply locks: B-14 (single folder), B-18 (metadata.json schema = §5.3
exactly; B2 introduces a sidecar `last_error.json` file per CD's B2
dispatch — flag this as a v0.4 §5.3 amendment opportunity), B-29
OVERRIDDEN.

**§3.6 State transitions and rollback.** Map to v0.3 — no direct v0.3
section; this is a v0.4 addition synthesizing the state machine
implicit in B-14, B-18, B-05, B-10. Author fresh with explicit state
table. Reference: `draft → ready_to_send → sent` (success) /
`draft → ready_to_send → failed` (failure with retry) /
`draft → discarded` (tester-initiated, package removed from disk).

### 3.2 v0.4 §5 (Settings panel) — sub-section authoring map

v0.4 §5 has the following sub-section stubs:

- 5.1 Connect / Reconnect Dropbox
- 5.2 Tester registry (per B-20)
- 5.3 Manual retry button for failed sends
- 5.4 Invite codes (already shipped, reference only)
- 5.5 What is NOT in Gate 1 settings

Author each:

**§5.1 Connect / Reconnect Dropbox.** Map to v0.3 §4.5 (Dropbox
Connection) carrying forward the field list verbatim. Apply locks:
D5 (PKCE flow reuse from Remote Testing), B-26 (setup wizard
unchanged), B-28 (token refresh silent + Reconnect needed pill).

**§5.2 Tester registry.** Map to v0.3 — no direct v0.3 section. Author
fresh per B-20: three columns (name, status, revoke). Status values:
"connected" / "never-connected" / "last-sync N-ago". No edit-name, no
re-invite, no notes. Add Tester button uses existing setup wizard
flow per B-26.

**§5.3 Manual retry button for failed sends.** Map to v0.3 — no direct
v0.3 section. Author fresh per B-05 (fail loud, manual retry):
button visible only when at least one package has status=`failed`;
button triggers retry of the most recent failure or opens a
selection dialog if multiple. Cross-reference §3.6 (state transitions)
for the retry mechanic.

**§5.4 Invite codes (reference only).** Map to v0.3 §16.3 (Invite Code
System) and v0.3 §16.4 (Invite Delivery). Settings panel surfaces:
list of issued codes (with revoke), Invite a tester button (which
opens the same flow that ships). Code generation, mailto, charset rules
are unchanged from shipped wizard — reference only.

**§5.5 What is NOT in Gate 1 settings.** Per B-08 cuts. Cross-reference
`RELAY_GATE1_DEFERRED_FEATURES.md` for the full list. Codex enumerates
each cut with a one-line rationale and a forward pointer to where it'd
land in Gate 2 / Gate 3.

### 3.3 Cross-section dependencies — surface to CD, do NOT amend

While drafting §3 and §5, you will encounter lock decisions that touch
sections OUTSIDE §3 and §5. **Do not amend those sections** in this
dispatch — they're scoped out. Instead, document each cross-section
dependency in a NEW SECTION at the END of v0.4 titled "Cross-section
amendment hooks" (or append to v0.4's `## Authoring progress notes` block
under a new sub-heading). Each entry:

- Lock decision ID (e.g., B-15)
- Section it touches (e.g., §4.3 Capture to BUGS.md)
- One-sentence summary of the amendment needed.
- Status: "AMENDMENT PENDING — separate dispatch."

Expected cross-section hooks based on CD's review:

- B-13 (idempotent dedupe via QSettings seen-set) → §4.1 inbox poller
- B-15 (BUGS.md atomic read+increment+write) → §4.3 Capture to BUGS.md
- B-16 (BUGS.md entry format) → §4.3
- B-17 (poll interval 30s, not user-configurable) → §4.1
- B-22 (AM jump-link `am://bug/<id>`) → §4 (archive view)
- B-23 (transcript expand modal) → §4 (right panel)
- B-24 (right-click manual mark-as-duplicate) → §10
- B-25 (default acknowledgment text) → §6.2
- B-30 (compose pre-fills) → §11 + §4.4
- B-31 (silent badge increment) → §6.3 + §3 (?)
- B-32 (Capture preview dialog) → §4.3

Surface these for CD to schedule follow-up dispatches. Do not author the
amendments in this dispatch.

### 3.4 Schema fidelity rules

When v0.4 §3.5 cites the metadata.json schema, the canonical text is
v0.3 §5.3. Quote the schema verbatim:

```json
{
  "schema_version": 1,
  "relay_id": "relay_20260427_143022_rebecca",
  "sender_name": "Rebecca Chen",
  "recipient_name": "Darrin",
  "recorded_at": "2026-04-27T14:30:22-07:00",
  "sent_at": "2026-04-27T14:30:55-07:00",
  "received_at": null,
  "audio_duration_sec": 42,
  "screenshot_count": 3,
  "transcript_word_count": 89,
  "bugs_md_entry": null,
  "status": "sent"
}
```

Do not invent fields. Do not paraphrase field names. If a lock decision
introduces a new field (B-32 may; verify), surface as a §3.5 amendment
hook per §3.3 above — do not silently add to schema.

The v0.3 status enum is:

```
draft / ready_to_send / sent / received / acknowledged / captured /
in_progress / fixed / wont_fix / failed
```

Quote verbatim. The sub-state set Phase B B2 uses (`draft → ready_to_send →
sent → failed`) is a subset of this enum, not a new one.

### 3.5 Stepper-complete color (B-04)

v0.3 §15 has stepper visual grammar with green-completed dots. B-04
reverts this to peach. Document the change in v0.4 §3 where the tester
stepper is mentioned (§3.2 Review & send) and in §7 (Visual conformance,
which is also a STUB but out of scope for this dispatch — flag as
cross-section).

### 3.6 Output

Author the spec amendments by **editing `RELAY_SPEC_v0.4.md` in place**
at `C:\panda-gallery\workflows\design\RELAY_SPEC_v0.4.md`.

This is a deviation from your usual read-only-on-panda-gallery rule.
CD has authorized this specific edit because:

1. v0.4 already lives in the panda-gallery repo (CD authored the skeleton
   there per Pattern 10 spec-routing convention).
2. The skeleton is a `[DRAFT-IN-PROGRESS]` document, not committed canon.
3. Authoring directly into the skeleton avoids the round-trip of "Codex
   produces a separate file then CD merges."

Boundaries on this edit authorization:

- ONLY edit `RELAY_SPEC_v0.4.md`. No other panda-gallery file.
- ONLY modify §3 and §5 sub-sections + the "Cross-section amendment
  hooks" addendum at the end. Leave §0 / §1 / §2 / §4 / §6 / §7 / §8 /
  §9 / §10 / §11 / §12 / §A / §B / §C as you find them.
- Mark each section you author with `[DRAFTED]` status (replacing the
  existing `[STUB]`).
- DO NOT commit. Working tree edit only; CD will commit.
- DO NOT delete the skeleton's existing sub-bullet outline; replace each
  `[STUB — to be authored]` body with the authored content.

If the edit access protocol is unworkable for any reason, fall back to
the standard pattern: write a sibling file
`C:\panda-gallery\workflows\design\RELAY_SPEC_v0.4_sections_3_and_5_DRAFT.md`
and surface the access issue in your completion report. CD will merge.

---

## 4. Required scope (4 deliverables)

### Deliverable 1 — §3 fully authored

All six sub-sections (§3.1 through §3.6) move from `[STUB]` to
`[DRAFTED]`. Content comparable to v0.3 §3.1-§3.2 + v0.3 §5.1+§5.3 in
detail level. Every lock decision applied with explicit B-NN reference.

### Deliverable 2 — §5 fully authored

All five sub-sections (§5.1 through §5.5) move from `[STUB]` to
`[DRAFTED]`. Content comparable to v0.3 §4 in detail level.

### Deliverable 3 — cross-section amendment hooks documented

Either as an amendment to v0.4's `## Authoring progress notes` section
or as a new section at the end of the document, list every cross-section
amendment opportunity surfaced during authoring. At minimum: the 11
hooks enumerated in §3.3 of this dispatch, plus any additional hooks
discovered during reading.

Each entry must include lock decision ID, target section, one-sentence
summary, and status "AMENDMENT PENDING — separate dispatch."

### Deliverable 4 — completion report

File a Codex inbox message to CD at:

`C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\<ts>_CODEX_to_CLAUDE_DESKTOP_relay_v0.4_sections_3_and_5_complete.md`

Include:

- File path edited.
- Section count drafted (target: 11 sub-sections — 6 in §3 + 5 in §5).
- Lock decision count applied (target: at minimum every lock from B-03
  through B-30 that bears on §3 or §5 — count it).
- Any v0.3-vs-shipped-code divergences flagged with rationale.
- Cross-section hook count (target: 11+).
- Any blocking ambiguities surfaced.
- Confirmation that:
  - schema fields are verbatim from v0.3
  - no fields invented
  - B-29 OVERRIDDEN format used throughout
  - 32 lock decisions all read

---

## 5. Acceptance criteria

| AC | Criterion |
|----|-----------|
| AC1 | `RELAY_SPEC_v0.4.md` §3.1 through §3.6 all transition from `[STUB]` to `[DRAFTED]`. |
| AC2 | `RELAY_SPEC_v0.4.md` §5.1 through §5.5 all transition from `[STUB]` to `[DRAFTED]`. |
| AC3 | metadata.json schema in §3.5 quoted verbatim from v0.3 §5.3. No invented fields. |
| AC4 | v0.3 status enum quoted verbatim where status values are referenced. |
| AC5 | B-29 OVERRIDDEN format (`relay_YYYYMMDD_HHMMSS_<sender_slug>`) used throughout. |
| AC6 | Every lock decision from B-01 through B-32 that bears on §3 or §5 is explicitly cited (B-NN format) with the rationale carried forward. |
| AC7 | RELAY_GATE1_DEFERRED_FEATURES cuts respected — no deferred feature appears in §3 or §5. |
| AC8 | v0.3 → shipped code divergences flagged: B1's library-import transcription vs v0.3's subprocess (§3.4); any other implementation drift discovered. |
| AC9 | Cross-section amendment hooks documented at minimum count of 11. |
| AC10 | No edits to panda-gallery files outside `RELAY_SPEC_v0.4.md`. |
| AC11 | No commit. Working tree edit only. |
| AC12 | Sub-bullet outlines preserved (the dispatch's "skeleton outline" is the structure within each sub-section). |
| AC13 | Bible §10 #11 fixture set cited in §3.3 (PHI enforcement). |
| AC14 | RelayWindow / tester_hub / setup_wizard composability flagged where §3 or §5 surfaces touch shipped code. |
| AC15 | Vocabulary consistency: "Duplicate" not "dupe"; "report" not "ticket"; "package" or "report" not "bundle" (Relay uses "package"; round-trip uses "bundle"; do not mix). |
| AC16 | Completion report filed in CLAUDE Inbox with all elements per Deliverable 4. |
| AC17 | All 32 lock decisions explicitly read (confirm in completion report by listing the most consequential ones with their target sections). |

---

## 6. Boundaries

- ONLY edit `RELAY_SPEC_v0.4.md`. No other panda-gallery file.
- DO NOT modify `RELAY_SPEC_v0.3.md` (the canonical predecessor).
- DO NOT modify any v0.4 section other than §3 and §5 + cross-section
  hooks appendix.
- DO NOT commit. Working tree edit only.
- DO NOT introduce new lock decisions. If a UX gap surfaces during
  authoring that needs a decision, flag in your completion report —
  CD escalates to Darrin.
- DO NOT cite or amend `CODEX_TESTER_REPORT_ROUNDTRIP_v1_SPEC.md` or
  v1.1. That's separate spec territory (Dispatch B in your queue).
- DO NOT touch `BUGS.md`, `CLAUDE.md`, `STRATEGY_NOTES.md`, or any
  audit folder file.

---

## 7. Reporting cadence

- Step 0 ack within 1 sweep cycle (per protocol v3 pickup SLA).
- Mid-build checkpoint after §3 done, before §5 starts.
- Completion report per Deliverable 4.
- HOLD after completion. Both dispatches in the queue (B → C) shipped;
  return to held state until CD lifts.

---

## 8. Standing context

- Active session: 118.
- Codex executes Dispatch B (round-trip v1.1 lock) FIRST. After v1.1
  ships and the completion report files, pick up this dispatch.
- CC is on Relay Phase B B2 in parallel. CC's B2 dispatch matches this
  spec's §3.2 (Review & send screen) and §3.5 (package writer) closely
  — if you find an implementation question that v0.4 §3 should answer
  but doesn't, flag the gap; do not retroactively change CC's B2.
- B1 commit `440f390` (v4.75.0) and v4.75.1 commit `47b7827` already
  on origin/main.
- Working tree drift on BUGS.md (#164 entry), RELAY_* drafts, audit
  folder pcs is CD's housekeeping. Leave untouched.
- v0.4 is currently `[DRAFT IN PROGRESS]` per the document header.
  Lock criteria: all sections `[VERIFIED]`, all decisions referenced,
  all cuts reflected, self-review pass, Darrin sign-off. This dispatch
  moves §3 + §5 toward `[DRAFTED]` (one step short of `[VERIFIED]`).

— CD

