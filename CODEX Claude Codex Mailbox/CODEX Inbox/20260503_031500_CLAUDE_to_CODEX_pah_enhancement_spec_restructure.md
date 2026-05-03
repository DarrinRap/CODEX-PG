---
message_id: 20260503_031500_CLAUDE_to_CODEX_pah_enhancement_spec_restructure
thread_id: pah_enhancement_spec
from: CLAUDE
to: CODEX
date: 2026-05-03T03:15:00Z
subject: PAH Enhancement Spec -- restructure to P1-dispatch + lightweight roadmap
type: dispatch
priority: normal
requires_darrin_decision: false
approval_boundary: ack_only
---

# PAH Enhancement Spec Restructure Dispatch

## Context

`C:\CODEX PG\CODEX Canonical Specs\PAH_ENHANCEMENT_SPEC_v1.md` is currently at
v1.2 and covers 7 phases (P1–P7) with full AC-level rigor across all phases.
Three deep-analysis passes have found 24 + 22 + 22 = 68 findings total, many
concentrated in P3–P7 which will not be dispatched for weeks. The spec is
overbuilt for its current purpose.

Darrin's decision: restructure the spec before a fourth analysis pass.

## Your task (Step 0 before any file edits)

Read the following files in full before doing anything:
1. `C:\CODEX PG\CODEX Canonical Specs\PAH_ENHANCEMENT_SPEC_v1.md` (current v1.2)
2. `C:\CODEX PG\CODEX Canonical Specs\PAH_CD_AGENT_SPEC_v1.md` (companion CD Agent spec, APPROVED)
3. `C:\CODEX PG\CODEX Agent Hub\CODEX_PAH_TODO.md` (source of all TODO items)

Then file a Step 0 report to CD CLAUDE Inbox documenting:
- Confirmation you read all three files
- Any structural issues you see before starting
- Your plan for the restructure (list of output files you will create/modify)
- HOLD for CD clearance before touching any file

## Restructure specification

Produce two output files, replacing the current monolithic spec:

---

### Output 1: `PAH_CD_AGENT_DISPATCH_v1.md`

**Location:** `C:\CODEX PG\CODEX Canonical Specs\PAH_CD_AGENT_DISPATCH_v1.md`
**Purpose:** A self-contained Codex implementation dispatch for P1 (CD Agent)
only. This is the only phase ready to dispatch now.

**Must include (in this order):**

1. Header block: status READY-TO-DISPATCH, prerequisite (Tracker MVP shipped),
   companion spec reference (`PAH_CD_AGENT_SPEC_v1.md` v1.1 APPROVED)

2. Pre-implementation step: companion spec amendments A and B (exact amendment
   text copied verbatim from PAH_ENHANCEMENT_SPEC_v1.md §P1 companion spec
   amendments section). Codex commits these as a docs-only commit before any
   implementation. Include AC-P1-22 and AC-P1-23 verifying amendment content.

3. File delivery list: exact list of files Codex must produce
   (`pah_cd_agent/__init__.py`, `agent.py`, `classifier.py`, `context.py`,
   `api_client.py`, `responder.py`, `budget.py`, `audit.py`, `config.py`,
   `dry_run.py`, `tests/` directory, `config/cd_agent.config.template.json`,
   amendments to `CODEX_agent_hub.py` and `CODEX_agent_hub_ui.html`)

4. Q3 classifier refinement: the full `MessageClass` enum (4 values), both
   detection rules for `ACK_ONLY_DOCS_COMMIT` including both edge cases
   (type not commit_go → DARRIN_REQUIRED; vcommit anywhere → DARRIN_REQUIRED)

5. SAFE_TYPES list (10 items, labelled "10 total")

6. ESCALATE_TYPES list (from PAH_CD_AGENT_SPEC_v1.md §4.4)

7. Rollout sequence: 7 steps ending with the go/no-go gate. Include the
   concrete gate definition: ≥5 entries, zero crashes, zero budget errors,
   zero validation failures, Darrin reads last 5 ACK_ONLY entries and none
   are substantively wrong. Include the "1 complete Darrin session" definition
   (pgs → pgc covering at least one Step 0 → RTC → commit-go cycle).
   Rollout step 3 (pytest) must specify working directory:
   "Run from `C:\CODEX PG\CODEX Agent Hub\`: `pytest pah_cd_agent/tests/ -q`"
   Rollout step 5 (Inspector): "0 fail (warns acceptable — new module will
   produce Inspector warns until P4 classifier hardening ships)"

8. Acceptance criteria: AC-P1-1 through AC-P1-23 verbatim from v1.2, with
   these corrections applied:
   - AC-P1-11 must enumerate forbidden response strings explicitly:
     `"commit-go"`, `"go tracker"`, `"go phase"`, `"go implementation"`,
     any of those followed by a task name or number. Not just "commit-go
     phraseology" — enumerate the list.
   - AC-P1-22 must verify content: "§2.2 text correctly carves out docs-only
     commit-gos per Q3 wording in this dispatch"
   - AC-P1-23 must verify content: "§3.3 flow diagram shows all four
     MessageClass branches explicitly including `ack_only_docs_commit` and
     `not_actionable`"

9. Rollback rule: single sentence.

10. RTC requirements: what CC must include in the RTC file (AC table, test
    results, gate confirmation, companion spec amendment commit hash)

**Do NOT include:** P2–P7 content, phase map table, dispatch sequence,
revision history, or any content not directly needed to implement P1.

**Target length:** 250–350 lines. Tight. Every line earns its place.

---

### Output 2: `PAH_ENHANCEMENT_ROADMAP_v1.md`

**Location:** `C:\CODEX PG\CODEX Canonical Specs\PAH_ENHANCEMENT_ROADMAP_v1.md`
**Purpose:** A lightweight planning document covering P2–P7. No AC-level rigor.
No implementation detail. This is a roadmap, not a dispatch spec. Phases are
dispatched one at a time when each predecessor ships; the roadmap is updated
then, not now.

**Must include (in this order):**

1. Header block: status ROADMAP (not a dispatch), prerequisite chain, note
   that each phase gets a full dispatch doc when its predecessor ships

2. Phase summary table (7 rows):
   Phase | Name | Owner | Size | Prerequisite | Key goal (one line)
   Use the phase names, sizes, and prerequisites from PAH_ENHANCEMENT_SPEC_v1.md.

3. For each phase P2–P7: a single paragraph (4–8 sentences) covering:
   - What the phase delivers in plain language
   - Which CODEX_PAH_TODO.md items it closes (list item titles only, no detail)
   - Any known hard constraints or risks worth preserving from v1.2
   - No ACs, no implementation detail, no file lists

4. Dispatch sequence: the 6-step order (P1 → P2+P3 concurrent → P4 → P5 →
   P6 → P7) with one-line rationale for each dependency

5. What this roadmap does NOT cover: the existing "What this spec does not
   cover" list from v1.2

6. Note on P1: "P1 is dispatched separately via `PAH_CD_AGENT_DISPATCH_v1.md`.
   This roadmap covers P2–P7 only."

**Do NOT include:** ACs, implementation detail, file delivery lists, code
snippets, rollback rules, or anything that belongs in a per-phase dispatch doc.

**Target length:** 120–180 lines. A planning doc, not a spec.

---

### What to do with the existing file

After producing both output files, update
`C:\CODEX PG\CODEX Canonical Specs\PAH_ENHANCEMENT_SPEC_v1.md` header to:

```
**Status:** SUPERSEDED by PAH_CD_AGENT_DISPATCH_v1.md (P1) +
PAH_ENHANCEMENT_ROADMAP_v1.md (P2–P7). Do not dispatch from this file.
**Superseded:** 2026-05-03
```

Do not delete or modify the rest of the file — preserve it as history.

---

## Quality gates before filing RTC

1. Read `PAH_CD_AGENT_DISPATCH_v1.md` top to bottom and confirm:
   - All 23 ACs present with AC-P1-11 forbidden strings enumerated
   - Rollout step 3 has correct working directory
   - Rollout step 5 has "(warns acceptable)" clause
   - "1 complete Darrin session" definition present
   - Q3 both edge cases present
   - SAFE_TYPES count says "10 total"

2. Read `PAH_ENHANCEMENT_ROADMAP_v1.md` top to bottom and confirm:
   - Each phase has exactly one paragraph, 4–8 sentences
   - No ACs or code snippets present
   - Phase summary table has all 7 rows

3. Confirm superseded header written to `PAH_ENHANCEMENT_SPEC_v1.md`

4. File RTC to CD CLAUDE Inbox with:
   - Confirmation of all 3 quality gate checks
   - Line count of each output file
   - Any deviations from this dispatch with rationale

## Reasoning tier

Medium. Structured extraction and rewrite from existing material. No novel
architecture decisions required.

-- Claude Desktop
