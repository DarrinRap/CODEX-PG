# CLAUDE → CODEX: Combined dispatch — two parallel jobs

You have **two independent jobs** in this single message. Run them in any order or in parallel. Each has its own deliverable, output path, and reply file. They share Bible-section foundations but are otherwise unrelated; do not blend findings between them.

> **Important:** Today (2026-04-26) the Bible got two new principles plus a new section. Read these first; both jobs reference them:
> - **§1.4 — Every pixel earns its presence**
> - **§1.5 — Every design feature reflects a true purpose**
> - **§13 — Resize and persistence behavior** (eight subsections)

All three live in `C:\panda-gallery\workflows\design\PG_DESIGN_BIBLE_v1.md`.

---

# JOB 1 of 2 — AM Screen A header + columns design pass

**Tier: High.** Visual + structural design recommendation with 2-3 sketches (HTML mockup or ASCII, your call). ~400-600 line response expected. Output feeds v4.42.3.

This is a meaningful screen-layout change to AM Screen A. Two §1.4/§1.5 violations have been identified in the live build; we want a designed answer rather than a patched one.

## Two violations to address

### Violation 1 — Header area is mostly redundant teaching (§1.5)

The current AM Screen A right-pane header reads:

```
AUDIT MODULE
Personal bug tracker — BUGS.md OPEN section
Click a row to triage. Resolve gaps. Build a fix prompt.
                                                    [↻ Refresh]
```

Three problems:

1. The two prose lines under "AUDIT MODULE" duplicate teaching that's *already* delivered by:
   - The `InboxStatusPane` in the left summary pane: "26 open · 23 to triage. Open a row to triage. Untriaged bugs are the next step."
   - The Workflow Stepper (Bible §6.21) directly below the InboxStatusPane: "1. Click a row to open it / 2. Triage with AI to surface gaps / 3. Resolve each gap with a decision / 4. Build the fix prompt for Claude Code."
   - The bottom status bar: "26 OPEN bugs. Source: BUGS.md · last parsed 10:08:48 · 26 OPEN · 23 untriaged."

2. The header zone is roughly 120px tall × full pane width (~2,000+ square pixels) delivering ~0 net new information.

3. Per §1.5 explicitly: the descriptive prose "Click a row to triage. Resolve gaps. Build a fix prompt." is called out *by name* in the §1.5 prose as a worked example of redundant teaching that should be removed or replaced with operational status.

### Violation 2 — SEVERITY / STATE / FILES columns waste horizontal space (§1.4)

Live build observations:
- SEVERITY column: pills are ~80-110px wide ("HIGH" / "MEDIUM" / "LOW"), but the column is ~250px → ~140-170px empty space per row.
- STATE column: pills are ~110-140px wide ("UNTRIAGED" / "READY" / "DESIGN" / "CLARIFY"), column ~250px → ~110-140px empty space.
- FILES column: 1-3 digit number, column ~80px → ~50-70px empty space.

That's roughly **300-380px of horizontal real estate wasted per row × ~12 visible rows ≈ 4,000+ square pixels** on the bug list alone.

Bonus violation: the TITLE column truncates with `…` ("AM Screen B…", "Settings …", "Active-…"). Bible §13.6 forbids label truncation on chrome content (mono metadata is OK, prose labels are not). Bug titles are prose. So the TITLE column needs to *grow* into the recovered space and word-wrap, not truncate.

## What I want from you

A coherent design pass addressing both violations as one v4.42.3 ship.

### Part A — Header redesign

Three options I've considered, plus your own:

**Option A1 — Delete prose lines, keep title only.**
```
AUDIT MODULE                                          [↻ Refresh]
─────────────────────────────────────────────────────────────────
FILTER  Severity [all ▾]  State [all ▾]  □ Show fixed   26 of 26 bugs
```
Most aggressive §1.4. Recovers ~80px of vertical space. Header becomes one line.

**Option A2 — Replace prose with live operational status.**
```
AUDIT MODULE                                          [↻ Refresh]
Source: BUGS.md · last parsed 10:08:48 · 0 changes pending
─────────────────────────────────────────────────────────────────
```
Subtitle carries operational meaning (source freshness, change tracking). Bottom status bar would need reconciliation to avoid duplication.

**Option A3 — Replace prose with state-aware next-action nudge.**
```
AUDIT MODULE                                          [↻ Refresh]
Next: 23 bugs need triage. Open a row to begin.
─────────────────────────────────────────────────────────────────
```
Dynamic — changes by state:
- 23 untriaged → "Next: 23 bugs need triage. Open a row to begin."
- 5 design / 0 untriaged → "Next: review 5 design-decision items."
- 1 ready / 0 untriaged / 0 design → "Next: build the fix prompt for #134."
- 0 of any → "Inbox clear. No bugs need attention."

Risk: duplicates what InboxStatusPane already says.

**Option A4 — Your own.** Propose alternative.

For each option, note:
- Whether it earns its presence under §1.5
- How it interacts with InboxStatusPane, the workflow stepper, and the bottom status bar
- Whether the operational status is non-redundant
- Visual treatment (Bible tokens only)

### Part B — Column-width strategy

**Option B1 — Fixed content-sized widths.**
- `#`: ~70px (4-digit + padding)
- TITLE: stretch (fill remaining, word-wrap)
- SEVERITY: ~110px (longest pill "MEDIUM" + padding)
- STATE: ~140px (longest pill "UNTRIAGED" + padding)
- FILES: ~50px (3-digit + padding)

**Option B2 — Proportional widths on a grid.**
- `#`: 6%, TITLE: 50%, SEVERITY: 12%, STATE: 16%, FILES: 6%, scrollbar gutter: 10%
- Grows/shrinks with window; proportions locked.

**Option B3 — Right-cluster the pills, narrow columns.**
Same widths as B1 but pills right-aligned in cells, clustering against table's right edge.

For each option, note:
- Behavior at narrow widths (~1000px bug-list area)
- Behavior at 4K widths
- Whether titles wrap or truncate (§13.6 forbids chrome truncation)
- Visual treatment (cell padding, alignment, header treatment)

### Part C — Sketches

2-3 sketches showing your recommended option(s) — header + table together — at:
- Default window width (~1280px overall)
- Narrow width (~1000px overall — minimum useful width)

ASCII art is fine. HTML mockup at `workflows/design/pg_general_mockups/AM_screen_a_header_columns_v1.html` is also fine if quick.

### Part D — InboxStatusPane wording (left summary pane)

Current:
```
INBOX
[●] 26 open · 23 to triage
Open a row to triage. Untriaged bugs are the next step.
```

Issues:
- "Open a row to triage" duplicates step 1 of the workflow stepper.
- "Untriaged bugs are the next step" is meta-narration about workflow.
- "to triage" reads as queue language; "untriaged" is more precise.

**D1.** `26 open · 23 untriaged` / `23 bugs need triage.`
**D2.** `26 open · 23 untriaged` (no subtitle when state uniform; subtitle only when non-obvious)
**D3.** State-aware dynamic subtitle:
- 23 untriaged: `Start with the 23 untriaged.`
- 0 untriaged, 5 design: `5 design decisions waiting.`
- 0 untriaged, 0 design, 1 ready: `1 ready — build the prompt for #134.`
- 0 of any: `Inbox clear.`
**D4.** Your own.

Coordinates with Parts A-C. If your right-pane header recommendation includes operational status (A2/A3), StatusPane and right-pane header must not duplicate each other. Divide operational labor cleanly between the two surfaces.

For your StatusPane recommendation, note:
- §1.5 earned-presence test
- Coordination with right-pane header (no duplication)
- Static, dynamic, or absent subtitle

### Part E — Bible component candidate

After picking a header treatment, propose: should this become a canonical "Module screen header" pattern in Bible §6 (alongside the workflow stepper as §6.22)? Library / Arrange / Review / Present all need screen headers; getting one canonical pattern locked now saves four ad-hoc designs.

If yes, sketch the §6.22 anatomy (sub-elements, sizing, color tokens, behavior). If no, explain why AM-specific.

## Foundation reading (Job 1)

1. `PG_DESIGN_BIBLE_v1.md` §1.4 + §1.5 — the two binding principles. §1.5 explicitly cites the "Click a row to triage…" line as a worked example of what to remove.
2. `PG_DESIGN_BIBLE_v1.md` §6.21 — workflow stepper. Reference so your header doesn't duplicate it.
3. `PG_DESIGN_BIBLE_v1.md` §13 — column-width recommendation must satisfy §13.1 invariants.
4. `audit_module/audit_module_window.py` `_BugListScreen._build_summary_pane()` (don't change) and `_build_table_pane()` (the surface that contains header + table).

## Out of scope (Job 1)

- Don't touch the left summary pane structure (StatusPane, workflow stepper, count rows are working — but you ARE asked to recommend wording for StatusPane in Part D).
- Don't touch Screen B (separate ticket).
- Don't propose new tokens — Bible §2 only.
- Don't recommend animations.
- Don't draft implementation dispatch — Claude does that after synthesis.

## Reply (Job 1)

Write your recommendation to:
`C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\20260426_HHMMSS_CODEX_to_CLAUDE_am_screen_a_header_and_columns.md`

If you produce an HTML mockup, save it to:
`C:\panda-gallery\workflows\design\pg_general_mockups\AM_screen_a_header_columns_v1.html`

---
---

# JOB 2 of 2 — DESIGN_AUDIT_v1 (§1.4, §1.5, §13 across all surfaces)

**Tier: High.** Mechanical audit of every user-visible surface in the PG codebase against three Bible sections. Output is a structured violations list with line numbers. ~600-1000 line response expected.

**Parallel:** CC will receive the same audit task in parallel. Your output and CC's will be cross-checked for completeness — overlap expected and welcomed; differences will be triaged together.

## Why this audit

PG has had recurring defects across three related domains:
1. **Resize behavior** (§13) — text hidden behind buttons, controls colliding, dialogs that open larger than content needs.
2. **Wasted real estate** (§1.4) — chrome that doesn't earn its presence.
3. **Redundant / purposeless features** (§1.5) — descriptive prose duplicating teaching from another surface.

This audit identifies every PG surface that should obey the rules, evaluates each against the relevant subsections, and reports findings in a structured doc that becomes the input to a triage + fix pass.

## Foundation reading (Job 2)

1. `PG_DESIGN_BIBLE_v1.md` §1.4 — "Every pixel earns its presence."
2. `PG_DESIGN_BIBLE_v1.md` §1.5 — "Every design feature reflects a true purpose."
3. `PG_DESIGN_BIBLE_v1.md` §13 — entire section. Eight subsections.
4. `BUGS.md` #129 — the originating sizing bug. §13.1 invariants are lifted from it.
5. `BUGS.md` #138 — AM window default size.
6. `BUGS.md` #128 — Settings dialog geometry persistence (already shipped). Gold-standard reference for §13.7.

## Scope: in-scope surfaces

For §13 (resize/persistence): every Python class that
- Is `QMainWindow`, `QDialog`, `QWidget` with `setWindowFlags(Qt.Window|Qt.Tool)`, or other top-level visible widget, AND
- Can be resized by the user.

For §1.4 + §1.5 (space + features): expands to **every user-visible surface**:
- All resizable surfaces from §13 scope
- Plus every distinct sub-screen or major panel (AM Screen A, AM Screen B, Library grid, Edit Adjust panel, Arrange canvas, Comparison view, Present mode chrome)
- Plus every empty state (per §8) the user might encounter

Specifically include (non-exhaustive):
- `panda_gallery.py` — `MainWindow`, plus major panel subclasses
- `instruction_pane.py` — `InstructionPane`, `TestingSettingsDialog`, `ChecklistStepView`, any other distinct UI surface
- `audit_module/audit_module_window.py` — `AuditModuleWindow`, `_BugListScreen` (Screen A), `_BugDetailScreen` (Screen B). **AM Screen A is the trigger surface** — pre-known header + column violations; flag with line-number evidence.
- `region_capture.py` — region capture overlay
- `template_editor.py` / `template_designer.py`
- `comparison_view.py`, `library_view.py`
- Any QDialog subclass anywhere

**Out of scope:** sub-widgets that are children of audited surfaces. Trivial fixed-size dialogs get a row but most checks are N/A — note them.

## Audit checklists

For each in-scope surface, run the §13 checklist (only if resizable) AND the §1.4/§1.5 checklist (always). Each check is PASS / FAIL / N/A / UNKNOWN with a one-line evidence note (line number where possible).

### §13 checklist (resizable surfaces only)

| # | Check | What to look for |
|---|---|---|
| 13.1 | `_compute_min_size()` derivation | Method derives §13.1 floor at runtime. Hardcoded `setMinimumSize(w,h)` without derivation comment fails. |
| 13.2 | Buttons all visible at min size (Rule 1) | Active button cluster fits at min size. `addStretch()` between buttons passes; `setSpacing(N)` that compresses fails. |
| 13.3 | Inter-button spacing fixed at 10px (Rule 2) | `setSpacing(N)` on button rows. Should be 10. |
| 13.4 | Text never clipped (Rule 3) | `setTextElideMode`, `Qt.ElideMiddle`, `Qt.ElideRight` on chrome labels. Mono metadata exempt. |
| 13.5 | Multi-line inputs ≥ 2 lines (Rule 4) | `QTextEdit`/`QPlainTextEdit` minimum height should derive from `fontMetrics().lineSpacing()*2 + padding`. |
| 13.6 | Default size content-driven (§13.2) | First-open path calls `_compute_default_size()`. Hardcoded `resize(W,H)` fails. |
| 13.7 | Geometry persistence (§13.3) | `showEvent` reads `QSettings().value(GEOMETRY_KEY)`; `closeEvent` writes `saveGeometry()`. Multi-monitor sanity check on restore is sub-check. |
| 13.8 | Reset path exists (§13.4) | `View → Reset window layout` (app-level) or per-window menu. If `_build_menu_bar` has no reset entry, every surface fails. |

### §1.4 checklist (all surfaces)

| # | Check | What to look for |
|---|---|---|
| 1.4.A | No oversized fixed columns | Tables/grids with columns much wider than content. AM Screen A SEVERITY/STATE/FILES is the worked example. |
| 1.4.B | No decorative margins | `setSpacing(N)` and `setContentsMargins(...)` larger than §4.1 spacing-scale tokens without semantic meaning. |
| 1.4.C | No range-based dimensions | "6-12px" in spec or magic numbers without derivation. |
| 1.4.D | No wrapper widgets where one suffices | Redundant containers where outer container only exists for indentation. |

### §1.5 checklist (all surfaces)

| # | Check | What to look for |
|---|---|---|
| 1.5.A | No redundant teaching | Multiple surfaces on same screen teaching same thing. AM Screen A header's "Click a row to triage…" duplicates workflow stepper. |
| 1.5.B | No descriptive prose where operational data belongs | Headers/subtitles describing what a screen *is* rather than surfacing operational status. |
| 1.5.C | No filler | Empty section headers, decorative dividers, status indicators always showing same value. |
| 1.5.D | No status-bar duplication | Surfaces inside a window repeating what application status bar says. |
| 1.5.E | Component sub-elements justified | Per §6: every sub-element in component anatomy must have documented purpose. |

## Output format (Job 2)

Write your audit to:
`C:\panda-gallery\workflows\audit\DESIGN_AUDIT_v1.md`

Structure:

```markdown
# DESIGN_AUDIT_v1 — Codex pass

**Date:** 2026-04-26
**Author:** Codex
**Scope:** PG Bible §1.4, §1.5, §13 compliance — every user-visible surface in PG codebase
**Reference:** `PG_DESIGN_BIBLE_v1.md` §1.4, §1.5, §13.1 through §13.8

## Summary

(2-4 paragraph summary: surfaces audited, fully compliant count, top patterns of violation across three domains, headline findings.)

## App-level findings

(Findings that apply to whole app. E.g. "View menu has no `Reset window layout` entry — fails §13.8 for every surface." Or: "Bottom status bar duplicates per-screen headers in three places — §1.5.D systemic issue.")

## Per-surface findings

### `MainWindow` (`panda_gallery.py`)

- **File:** `panda_gallery.py`
- **Class:** `MainWindow(QMainWindow)`
- **Window type:** main app window (resizable)

#### §13 checks

| Check | Status | Evidence |
|---|---|---|
| 13.1 compute_min_size derivation | FAIL | line 234: `setMinimumSize(800, 600)` — hardcoded. |
| 13.2 Buttons visible at min | PASS | toolbar uses QHBoxLayout with addStretch. |
| ... | ... | ... |

#### §1.4 checks

| Check | Status | Evidence |
|---|---|---|
| 1.4.A No oversized columns | N/A | no tables. |
| ... | ... | ... |

#### §1.5 checks

| Check | Status | Evidence |
|---|---|---|
| 1.5.A No redundant teaching | UNKNOWN | empty-state guidance not yet implemented (#114) — re-audit after #114. |
| ... | ... | ... |

**Severity:** Medium.

**Fix recommendation:** Add `_compute_min_size()` and `_compute_default_size()`; replace hardcoded values; add `View → Reset window layout` entry. ~80 LOC.

### `_BugListScreen` (`audit_module/audit_module_window.py`)

(Pre-known violations to confirm with line-number evidence:)
- §1.4.A: SEVERITY/STATE/FILES columns waste ~300-380px per row of horizontal real estate.
- §13.6: TITLE column truncates with `…` on bug titles (chrome content, not metadata).
- §1.5.A: Header prose "Click a row to triage. Resolve gaps. Build a fix prompt." duplicates workflow stepper teaching.
- §1.5.B: Header subtitle "Personal bug tracker — BUGS.md OPEN section" describes what the screen *is* rather than surfacing operational status.

Audit these and any others with line-number evidence.

... (one section per surface)
```

After all per-surface sections:

```markdown
## Compliance summary tables

### §13 compliance (resizable surfaces)

| Surface | 13.1 | 13.2 | 13.3 | 13.4 | 13.5 | 13.6 | 13.7 | 13.8 | Severity |
|---|---|---|---|---|---|---|---|---|---|
| MainWindow | F | P | ? | P | N | F | P | F | M |
| ... |

### §1.4 compliance (all surfaces)

| Surface | 1.4.A | 1.4.B | 1.4.C | 1.4.D | Severity |
|---|---|---|---|---|---|
| _BugListScreen | F | P | P | P | H |
| ... |

### §1.5 compliance (all surfaces)

| Surface | 1.5.A | 1.5.B | 1.5.C | 1.5.D | 1.5.E | Severity |
|---|---|---|---|---|---|---|
| _BugListScreen | F | F | P | P | P | H |
| ... |

## Triage recommendations

(Group findings into ship-ready clusters: "v4.43 should fix all §13.6 column-width FAILs across all table surfaces as one coherent ship." Don't draft dispatches; identify clusters.)

## Open questions for Darrin

(Anything wanting Darrin call.)

## Cross-check note for CC

(If you went first, leave a paragraph for CC summarizing your approach so CC's pass focuses on what you missed rather than redoing.)
```

## Out of scope (Job 2)

- Don't write fixes. Audit, not code change.
- Don't speculate about future Bible additions. Stick to §1.4, §1.5, §13 as written.
- Don't audit non-user-visible code.
- Don't open BUGS.md entries — audit doc IS the report.

## Reply (Job 2)

1. Audit doc at `C:\panda-gallery\workflows\audit\DESIGN_AUDIT_v1.md`.
2. Reply summary to:
   `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\20260426_HHMMSS_CODEX_to_CLAUDE_design_audit_complete.md`
   (2-3 paragraphs + pointer at audit doc; don't paste whole audit into reply.)

---

# Final note

Both jobs share Bible §1.4, §1.5, §13 as foundations but produce **independent deliverables with separate reply files**. Don't blend findings between them. If you discover something in Job 2 that affects Job 1's recommendations (e.g. a §1.5 violation pattern you also see on Screen A), reference it across — but keep the deliverables clean.

-- Claude
