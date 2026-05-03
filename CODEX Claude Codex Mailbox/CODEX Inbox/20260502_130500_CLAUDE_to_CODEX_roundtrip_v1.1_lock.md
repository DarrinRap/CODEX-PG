---
schema_version: 1
id: CD-20260502-130500-ROUNDTRIP-V1.1-LOCK
thread_id: ROUNDTRIP-V1.1-LOCK-AND-PHASE-1
from: claude_desktop
to: codex
type: dispatch
priority: high
status: actionable
thread_status: active
action_owner: codex
requires_darrin_decision: true
approval_boundary: directive
tier_recommendation: Extra-High
tier_rationale: >
  Multi-document spec authoring with locked-defaults synthesis from a
  Proposed predecessor, plus authoring a Phase 1 implementation manifest
  that CC will use as a build spec. Cross-references PG_TRUTH, AM Bible,
  AM_SPEC v1.1, transport layer interfaces. Output is a canonical spec
  that downstream implementation depends on. >300 lines expected.
---

# Round-trip spec v1.1 — lock the 13 open questions + author Phase 1 implementation manifest

This is parallel work to CC's Relay Phase B B2 dispatch. CC and Codex
operate on disjoint scopes; nothing in this dispatch touches Relay code
or RELAY_SPEC.

---

## 1. Goal in one paragraph

The existing `CODEX_TESTER_REPORT_ROUNDTRIP_v1_SPEC.md` (dated 2026-04-25,
status: Proposed architecture) is the canonical Codex spec for the tester
report round-trip system — the architecture that connects tester-side
session capture (workflow_capture + transcribe + bundle build) through
Dropbox-as-pipe to developer-side AM Reports section ingest, response,
and archive. v1 ends with 13 open questions explicitly flagged for Darrin
decision (§18). For each question, v1 includes Codex's own concrete
recommendation. This dispatch asks Codex to author **v1.1 of the spec**
that takes those v1 recommendations as default locks and adds a
**Phase 1 Implementation Manifest** detailing modules, files, line
budgets, test surfaces, and AC-shape so that a future CC dispatch can
implement Phase 1 without further spec authoring.

---

## 2. Step 0 — canonical reads BEFORE drafting (Pattern 22)

Per WORKING_RULES_v1 v5 + REPEATED_ERRORS Pattern 22: read the canonical
sources verbatim and in full before drafting. Do not work from secondhand
citations or memory. If your read disagrees with this dispatch's
characterizations, surface in the Codex inbox before drafting.

Required reads:

1. **`C:\CODEX PG\CODEX Canonical Specs\CODEX_TESTER_REPORT_ROUNDTRIP_v1_SPEC.md`** —
   read in full, all 20 sections. This is your own prior work; v1.1 is
   a direct successor.
2. **`C:\panda-gallery\workflows\audit\TESTER_REPORT_ROUNDTRIP_BRIEF_v1.md`** —
   read in full. The goal-lock CD authored, currently DRAFT-status. Your
   v1 spec was authored against this brief; v1.1 should treat the brief
   as locked input (per §11 the brief asks Darrin to "confirm or correct
   §1, §2, §4, §5, §6, §8" — those are now treated as locked).
3. **`C:\panda-gallery\workflows\audit\PG_TRUTH_v1.md`** — read in full.
   Specifically: AM is dev-only; harness paused; vocabulary unresolved.
4. **`C:\panda-gallery\workflows\audit\AM_SPEC_v1.1.md`** — read in full.
   Existing AM v1 architecture. Reports section integrates as a peer to
   Bugs surface; must not redesign Bugs.
5. **`C:\panda-gallery\workflows\audit\AM_SCREEN_B_SYNTHESIS_v1.md`** —
   read in full. Locked v1 Screen B decisions; Reports section must be
   visually continuous.
6. **`C:\panda-gallery\workflows\audit\AM_BIBLE_SYNTHESIS_v1.md`** —
   read in full. Bible compliance for any new AM surface.
7. **`C:\panda-gallery\BUGS.md` #134, #97, #140**, plus the recent
   range #157–#164 — read each entry. Cross-references for compliance
   posture and recent UX patterns.
8. **`C:\panda-gallery\audit_module\`** — directory listing + read at
   minimum the `screen_b.py` (or current main bug-detail screen),
   `audit_module_window.py`, `bugs_view.py` or equivalent. Establish
   exact extension points for adding a Reports section without modifying
   Bugs.
9. **`C:\panda-gallery\workflow_capture.py`** — read top to bottom (you
   read this for v1; re-read because schema_v6 + auto-transcribe shipped
   since). Confirm session artifact locations, transcript lifecycle, and
   `LATEST.txt` semantics.
10. **`C:\panda-gallery\PANDA_GALLERY_AUTOTRANSCRIBE_SPEC.md`** and
    **`PANDA_GALLERY_TRANSCRIPT_V2_SPEC.md`** — read in full. Bundle
    builder consumes transcript v2 output as locked input.
11. **`C:\panda-gallery\PANDA_GALLERY_COMPLIANCE_SPEC.md`** — read in
    full. Tier A baseline; Tier B implications for v1.1 sketch.
12. **`C:\panda-gallery\codex_audit\`** — directory listing + key files.
    Existing package builder pattern is a reuse candidate for the bundle
    builder.
13. **`C:\panda-gallery\STRATEGY_NOTES.md`** — read recent entries
    (last 30 days). Strategic posture for round-trip context.
14. **`C:\panda-gallery\workflows\audit\WORKING_RULES_v1.md`** — read
    in full. v5 includes the dispatch authoring gate + Pattern 22.
15. **`C:\panda-gallery\workflows\audit\REPEATED_ERRORS.md`** Pattern 22 —
    explicit read. The pattern this dispatch enforces.

If any read disagrees with this dispatch, surface in Codex inbox before
drafting.

---

## 3. CD's findings from the deep review (handoff)

These are the design points CD locked while authoring this dispatch.
They are guidance for v1.1, not constraints — Codex retains spec
authority. If any of these conflicts with your verbatim canonical read,
your read wins; flag the conflict.

### 3.1 The 13 open questions and their locking strategy

v1's §18 lists 13 open questions. v1 also provides a concrete
recommendation for each. The locking strategy for v1.1:

| # | Question | v1 recommendation | v1.1 lock |
|---|----------|-------------------|-----------|
| 1 | Bundle format | Directory-with-manifest | LOCK as recommended |
| 2 | Manifest schema | v1 §8.1 fields | LOCK as recommended (with v1.1 polish per §3.2 below) |
| 3 | Status set authoring | AM-owned `workflows/audit/report_statuses.json`; embedded labels in responses | LOCK as recommended |
| 4 | Tester identity | Local `tester_profile.json` + QSettings mirror | LOCK as recommended |
| 5 | AM-side database schema | Separate SQLite `am_reports.db` | LOCK as recommended |
| 6 | Bundle deduplication | First bundle ID + same hash wins; same ID + different hash quarantines | LOCK as recommended |
| 7 | Failed delivery | Save draft / pending upload with retry + visible last_error | LOCK as recommended |
| 8 | Bundle-to-report cardinality | 1:1 | LOCK as recommended |
| 9 | Redaction interface | Pre-upload Tier A/B + optional post-download | LOCK as recommended |
| 10 | Bundle size / archive lifecycle | Warn at 50 MB; require confirmation above 100 MB | LOCK as recommended (codify in spec) |
| 11 | Transport choice for v1 | Dropbox local-folder provider | LOCK as recommended |
| 12 | Schema validation security | Quarantine on validation failure, never crash | LOCK as recommended |
| 13 | Clinical-tester onboarding | Out of v1 scope | DEFER (acknowledge as v2 question) |

For each lock, v1.1 should include:

- A short rationale paragraph (1–3 sentences) explaining why the
  recommendation is the locked answer.
- A pointer back to the v1 §18 entry where the recommendation was
  proposed (audit trail).
- For Q13 specifically: explicit statement that v1.1 defers and a
  forward reference to a future v2 spec dispatch ("clinical-tester
  onboarding spec v1") that Codex will be asked to author when Tier B
  becomes active work.

### 3.2 v1.1 polish on the manifest schema (Q2 follow-up)

While locking Q2, take a fresh pass on the manifest schema in v1 §8.1:

- The `tester.tester_id` slug should be normalized — define exactly:
  lowercase, ASCII alphanumerics + underscores only, max length 32. v1
  doesn't lock this; v1.1 should.
- `report.kind` enum should be locked: at minimum `bug`, `question`,
  `suggestion`, `other`. v1 says "kind: bug" without enumerating.
- `tier.data_tier` enum: `A_SYNTHETIC_ONLY`, `B_PHI_GATED`, `C_REDACTION_ONLY`.
  v1 has `A_SYNTHETIC_ONLY` only.
- `files[].kind` enum: `metadata_json`, `transcript_md`, `transcribe_log`,
  `audio_wav`, `screenshot_png`, `report_summary_md`, `redaction_report_json`,
  `bundle_events_jsonl`. v1 has `metadata_json` only.
- `warnings` array entry shape: `{"code": str, "severity": "info|warn|error",
  "message": str, "at": ISO}` — v1 leaves this open.

### 3.3 Phase 1 Implementation Manifest — the new section

Add a NEW section §21 (or wherever fits the spec's structure) titled
**"Phase 1 Implementation Manifest"**. This is a build-spec for CC,
not architecture. Required content:

For each module the spec proposes (`tester_reports/`, AM Reports
section), enumerate:

- Files to create (full path within the repo).
- Each file's size budget (LOC range, e.g. "200-400 LOC").
- Public surface (class names, public method signatures) — Python type
  hints, docstrings as one-sentence stubs.
- Dependencies (what other modules / libraries / settings keys it
  consumes).
- Test surface: which `tests/<area>/test_<file>.py` files cover it,
  approximate test count, key behaviors covered.
- Boundary statements: what this module MUST NOT touch (cross-reference
  PG_TRUTH locks).
- Acceptance criteria for the file (compilable, public API surface
  intact, tests passing, no `--no-verify`, lint CLEAN against current
  baseline).

For the tester-side `tester_reports/` package, the v1 spec already
proposes 9 files at §5.1. Expand each to manifest detail.

For the AM Reports section, the v1 spec proposes 4 new audit_module
files at §5.3. Expand each to manifest detail.

Also include in the manifest:

- The `report_statuses.json` config schema (Q3 lock fully realized).
- The `tester_profile.json` schema (Q4 lock fully realized).
- The `am_reports.db` schema (Q5 lock; v1 §8.5 starts this — extend to
  CREATE TABLE statements + index recommendations + migration shape if
  the schema ever grows).
- The `tester_reports.db` schema (v1 §8.4 starts this — same extension).
- The `ReportTransport` interface formally with method docstrings and
  a `LocalSyncFolderTransport` reference implementation sketch (the v1
  Dropbox provider).
- The `RedactionStage` interface formally with method docstrings.
- A Tier A baseline `RedactionStage` implementation sketch.

Phase 1 in this manifest covers v1 §19's "First slice" exactly:

> tester profile config; directory bundle builder from a completed
> synthetic session; manifest + READY marker + validator; local
> filesystem transport pointed at a test folder; tester SQLite DB state
> updates through Drafted/Shipped; AM ingest poller into am_reports.db;
> minimal AM Reports list/detail view.

Phases 2 and 3 are NOT in scope for the manifest — flag them as
"manifest follows in a v1.2 dispatch when Phase 1 ships."

### 3.4 Cross-cutting checks during v1.1 authoring

Verify these hold throughout v1.1:

- **Vocabulary consistency.** PG_TRUTH locks AM as dev-only; v1.1 must
  not propose any tester-facing AM surface. The Reports section is
  developer-only.
- **Bible compliance for proposed AM Reports UX.** §12.4 of v1 sketches
  AM Reports inbox. v1.1 should explicitly cite Bible v1.4 sections
  governing the proposed visual elements (cards / pills / steppers /
  status pane copy / etc.).
- **Round-trip brief sign-off audit.** The brief is DRAFT in
  `workflows/audit/`. CD will surface to Darrin separately for explicit
  sign-off before CC implements; v1.1 should NOT presume the brief is
  locked yet — frame v1.1 itself as "lock when Darrin signs off the
  brief or accepts v1.1 directly."
- **Tier B forward reference.** v1.1 stays Tier A only. Tier B is
  acknowledged as a future v2 spec.

### 3.5 Output path

Write v1.1 to:

`C:\CODEX PG\CODEX Canonical Specs\CODEX_TESTER_REPORT_ROUNDTRIP_v1.1_SPEC.md`

Do NOT modify the v1 file. v1 stays as the Proposed predecessor for
audit trail.

### 3.6 Spec conventions to maintain

- ASCII characters only (your standard convention).
- Section numbers continue from v1's structure where reasonable;
  add new sections (§21 manifest) at the end.
- Cite v1 sections explicitly when carrying forward content.
- Mark every lock decision with a "**LOCKED v1.1**" annotation so future
  readers can grep.

---

## 4. Required scope (5 deliverables)

### Deliverable 1 — `CODEX_TESTER_REPORT_ROUNDTRIP_v1.1_SPEC.md`

Full spec document. Structure:

- Header: identical conventions to v1, version bumped to 1.1, supersedes
  pointer to v1.
- §0 ABOUT: brief diff vs v1 + sign-off status note.
- §1–§17: carry forward v1 content as the spec base, with **LOCKED v1.1**
  annotations on each Q1-Q12 answer woven in at the relevant section
  (not just §18). e.g. "Q3 status set authoring is LOCKED v1.1 to
  AM-owned `workflows/audit/report_statuses.json`" appears at §13 where
  status configuration is discussed.
- §18 (open questions): retitle to "Resolved questions" and document
  each Q1-Q12 lock with rationale + v1 recommendation pointer. Q13 stays
  open with explicit defer.
- §19 (recommended first implementation slice): retitle / expand to
  "Phase 1 — definitive scope" reflecting the locked decisions.
- §20 (final recommendation): retitle / refresh.
- NEW §21: Phase 1 Implementation Manifest (per §3.3 above).
- NEW §22: schema dictionary — formal CREATE TABLE statements, JSON
  schema for config files, type hints for interfaces.

Target length: 40-60 KB (v1 is 27 KB; v1.1 adds ~15-30 KB of manifest
detail).

### Deliverable 2 — manifest cross-validation

After the spec is drafted, verify by re-reading each Phase 1 file
specification against the existing PG codebase:

- Does the proposed file path collide with anything that exists?
- Are the proposed dependencies (settings keys, modules, libraries)
  actually available?
- Are the proposed test files reachable with current pytest config?
- Do the proposed CREATE TABLE schemas match the patterns of existing
  PG SQLite usage?

If any check fails, document in the spec under a §23 "Implementation
risks" section with concrete suggestions for resolution.

### Deliverable 3 — completion report

File a Codex inbox message to CD at:

`C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\<ts>_CODEX_to_CLAUDE_DESKTOP_roundtrip_v1.1_complete.md`

Include:

- File path and final size.
- Section count and lock count (Q1-Q12 = 12 locks; Q13 deferred).
- Phase 1 manifest module count + LOC budget total.
- A summary of any spec adjustments made beyond the v1.1 polish points
  in §3.2 of this dispatch (CD wants the audit trail).
- Explicit flag if any cross-validation check (per Deliverable 2)
  failed.

### Deliverable 4 — read-only on `C:\panda-gallery\`

Per existing protocol: Codex does not modify any file under
`C:\panda-gallery\`. Reads only. v1.1 lives at
`C:\CODEX PG\CODEX Canonical Specs\` exclusively.

### Deliverable 5 — boundary on Relay

This dispatch is for the round-trip system (tester-report). It is NOT
about Relay (the bug-comms tool). Per RELAY_SPEC v0.3 §6.1, Relay and
Remote Testing are separate features. Do NOT cite or modify
RELAY_SPEC v0.3 in v1.1. CC's Relay Phase B B2 dispatch is the parallel
work; do not confuse the two.

---

## 5. Acceptance criteria

| AC | Criterion |
|----|-----------|
| AC1 | `CODEX_TESTER_REPORT_ROUNDTRIP_v1.1_SPEC.md` exists at the canonical specs folder. v1 file untouched. |
| AC2 | All 12 lockable open questions (Q1-Q12) have explicit "LOCKED v1.1" annotations with rationale (1-3 sentences each) and v1 §18 pointers. |
| AC3 | Q13 is explicitly DEFERRED with forward reference to a future v2 dispatch. |
| AC4 | v1.1 polish on Q2 manifest schema applied per §3.2: tester_id slug normalization, report.kind enum, tier.data_tier enum, files[].kind enum, warnings entry shape. |
| AC5 | §21 Phase 1 Implementation Manifest exists with detail per §3.3 of this dispatch (files, sizes, public surface, deps, tests, boundaries). |
| AC6 | tester_reports/ package files manifested: 9 from v1 §5.1 expanded. |
| AC7 | AM Reports section files manifested: 4 from v1 §5.3 expanded. |
| AC8 | §22 schema dictionary exists with CREATE TABLE for am_reports.db and tester_reports.db, JSON schema for report_statuses.json and tester_profile.json, formal type hints for ReportTransport and RedactionStage interfaces. |
| AC9 | Bible compliance citations woven into §12.4 (or wherever AM Reports UX is described) — Bible v1.4 section references for cards/pills/steppers/status copy. |
| AC10 | PG_TRUTH compliance: no tester-facing AM surface proposed anywhere. |
| AC11 | Tier B forward reference in place; Tier A is the only tier in scope. |
| AC12 | Brief sign-off framing: v1.1 explicitly notes the brief is DRAFT and that v1.1 lock is conditional on Darrin's brief sign-off or direct v1.1 acceptance. |
| AC13 | Cross-validation per Deliverable 2 done; any failures documented in §23. |
| AC14 | ASCII-only, vocabulary-consistent ("Duplicate" not "dupe"; "report" not "ticket"), section numbering coherent. |
| AC15 | Output spec file size 40-60 KB. |
| AC16 | Completion report filed in CLAUDE Inbox. |

---

## 6. Boundaries

- DO NOT modify any file under `C:\panda-gallery\`.
- DO NOT modify v1 file `CODEX_TESTER_REPORT_ROUNDTRIP_v1_SPEC.md`.
- DO NOT cite or amend RELAY_SPEC. Relay is a separate product surface.
- DO NOT propose tester-facing AM surfaces (PG_TRUTH locked).
- DO NOT introduce a new transport authentication path. Reuse PKCE
  no-redirect (the round-trip uses local-folder transport, no Dropbox
  API auth needed for v1, but if v1.1 surfaces an auth concern, defer
  to existing Dropbox sync module).
- DO NOT lock Q13 (clinical-tester onboarding). Defer to v2.
- DO NOT include implementation code (Python). The manifest documents
  surface (signatures, schemas) but the implementation is CC's later
  dispatch.

---

## 7. Reporting cadence

- Step 0 ack within 1 sweep cycle (per protocol v3 pickup SLA): a brief
  "starting v1.1 lock" message to CLAUDE Inbox confirming reads
  underway.
- Mid-build checkpoint optional but useful (one message per major
  section block — e.g., one after lock annotations done, one after
  manifest done).
- Completion report per Deliverable 3.
- HOLD after completion. Do not self-direct to next work.

---

## 8. Standing context

- Active session: 118.
- Codex is currently HELD per CD direction `20260502_115500_CLAUDE_to_CODEX_direction_continue_hold.md`.
  This dispatch lifts the hold for v1.1 lock work specifically.
- After v1.1 ships, Codex picks up the second parallel dispatch (Dispatch
  C in CD's queue: `20260502_131000_CLAUDE_to_CODEX_relay_spec_v0.4_sections_3_and_5_amendment.md`)
  which is for Relay §3+§5 amendment work — a separate spec surface
  (RELAY_SPEC v0.4 vs CODEX_TESTER_REPORT_ROUNDTRIP). Both dispatches
  land in your inbox at the same time; the order of execution is v1.1
  first, then §3+§5 amendment.
- After both ship, Codex returns to held state.
- CC is on Relay Phase B B2 in parallel. Different scope; no
  collision.
- B1 commit `440f390` and v4.75.1 commit `47b7827` already on
  origin/main. Working-tree drift in BUGS.md / RELAY_* drafts /
  audit pcs is CD's housekeeping, not Codex's concern.

— CD

