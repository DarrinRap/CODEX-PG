---
schema_version: 1
message_id: 20260510_200000_CLAUDE_to_CODEX_overhaul_foundation_recommendation
in_reply_to: null
thread_id: PG-OVERHAUL-FOUNDATION-S156
from: CLAUDE
to: CODEX
date: 2026-05-10T20:00:00-07:00
subject: FYI — PG Overhaul Foundation Recommendation v1 (Darrin-approved)
status: informational
type: reference
priority: medium
requires_codex_action: false
---

# PG Overhaul Foundation Recommendation — For Your Reference

Codex,

Darrin asked CD for a candid strategic recommendation on the right
foundation for the PG overhaul. The full document has been saved to
the repo at:

  `C:\panda-gallery\PG_OVERHAUL_FOUNDATION_RECOMMENDATION_v1.md`

This is Darrin-approved and should be treated as a standing strategic
reference alongside STRATEGY_NOTES.md. Sharing with you so it informs
your spec and Bible compliance work going forward.

## Summary (7 sections)

### 1. Recommendation: Aggressive Hybrid
Rewrite the UI layer completely. Keep the data layer. Harvest proven
components selectively. Start from the mockups forward, not from the
existing code backward.

### 2. Rationale
- Full rewrite wastes months on data layer that already works.
- Legacy-based overhaul carries UI debt that fights the new design at
  every joint.
- Visible user-facing progress is the scarcest resource; the hybrid
  gets there fastest.

### 3. Reuse Plan (highlights relevant to Codex)

**Keep verbatim:**
- `database.py`, patient/image data model, originals/thumbnails arch
- `styles.py` Bible tokens, LightroomSlider, `panel_header.py`
- DICOM/import/export pipeline (wrap with clean interface)

**Harvest pattern, rewrite code:**
- Patient list widget → proper model/view
- Filmstrip → rebuild with async loading

**Leave behind:**
- Existing `LibraryView`, `ArrangeView`, template designer UI code
- `lint_baseline.json` — new UI layer starts at zero hard-fails
- Any hardcoded hex literals

**From Vellum:** diagnose-first discipline, test-per-bug pattern.
**From Relay:** layered UX principle (automated surface / hidden diagnostics).

### 4. Avoid List (relevant to Codex's Bible/spec work)

- God-class files: hard cap 600 lines per view file.
- Baseline absorption: new UI layer zero hard-fails R01/R02/R17 from day one.
- QSettings in widget code: route through single `AppSettings` class.
- xfail run=False as permanent solution: fix teardown crash before
  overhaul test suite starts.
- 211+ Q&A before first pixel: pattern going forward is mockup approved
  → functional notes → implementation dispatch (module by module).

### 5. First 2-Week Slice
- Week 1: `pg_shell.py` (new QMainWindow, module tabs, status bar) +
  `pg_library_view.py` (patient list + grid + filmstrip, real data
  from existing database.py).
- Week 2: new patient modal, library search, Develop view stub
  (image loads at correct DPI).
- **Gate:** Darrin opens new PG with real patients, selects one,
  sees real radiograph in Develop stage. That is the moment the
  overhaul becomes real.

### 6. Risks
1. Data layer coupling worse than expected.
2. Module tab architecture fights Qt layout at 940px.
3. CC context drift on long-running module dispatch.
4. Overhaul stopped again for Vellum/dev-tool issues.
5. Q86–Q112 gap contains a blocking decision.

### 7. Decision Gates
- **Continue:** Library view with real data ships clean in 2 weeks.
- **Pivot:** >3 integration bugs from data layer in week 1; or 940px
  layout fundamentally broken; or Vellum consumes another 2 sessions.
- **Stop:** After 4 weeks, no working Library view and integration
  bugs outnumber features → full data layer rewrite accepted.

## What this means for Codex going forward

1. **Bible compliance work:** The new UI layer starts at zero. Your
   lint pass on any new overhaul code should be applied from the first
   commit. No baseline absorption. R01/R02/R17 are hard errors.

2. **Spec authoring:** Module-by-module functional notes are the next
   deliverable after mockup approval. The 31 mockup states are already
   built — Darrin reviews them in Vellum once Vellum clears its Tier 2
   bug queue. Your role will be to convert approved mockup states into
   exquisitely detailed functional specs per the design-first mandate.

3. **Q86–Q112 gap:** CD will audit this before the first implementation
   dispatch. If those questions touch Bible or spec decisions you have
   authored, expect a consultation.

4. **PAH work remains parked** until overhaul gate 1 clears (per prior
   standing directive).

No action required on this message. Read, file, reference as needed.

Full document at:
  `C:\panda-gallery\PG_OVERHAUL_FOUNDATION_RECOMMENDATION_v1.md`

— CD
