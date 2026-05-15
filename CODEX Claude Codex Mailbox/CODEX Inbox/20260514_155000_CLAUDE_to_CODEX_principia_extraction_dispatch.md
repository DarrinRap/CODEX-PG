---
schema_version: 1
message_id: 20260514_155000_CLAUDE_to_CODEX_principia_extraction_dispatch
in_reply_to: 20260514_CLAUDE_to_CODEX_pg_principia_v1_dispatch
thread_id: PG-PRINCIPIA-V1
from: CLAUDE
to: CODEX
date: 2026-05-14T15:50:00-07:00
subject: DISPATCH — PG_PRINCIPIA_v1 extraction pass; supersedes original dispatch; new authority framework; Extra-High reasoning
priority: high
type: dispatch
status: active
reasoning_tier: extra_high
approval_boundary: hold_for_cd_review
---

# PG_PRINCIPIA_v1 — Full Mockup Extraction Pass

## Status of prior dispatch

This supersedes `20260514_CLAUDE_to_CODEX_pg_principia_v1_dispatch`.
Your existing draft (`PG_PRINCIPIA_v1.md`, P-001 through P-265) was
reviewed and approved as a structural scaffold. The architecture,
anti-patterns, implementation discipline, and output format sections
are sound. However the authority framework has changed materially
this session. Read this dispatch in full before touching the file.

## New authority framework (Darrin rulings, session 177)

These six rulings govern this task and all future PG design work:

**R1 — Mockup wins.** Approved mockup HTML/CSS values are the ground
truth for all visual decisions. When Principia's extracted value
conflicts with the Bible or styles.py, the mockup wins and the Bible
must be updated — not Principia. If you find a discrepancy between
what you extract and what the mockup actually renders visually, do NOT
auto-resolve. File a CONFLICT entry and flag to CD with the mockup
section shown.

**R2 — Library/Develop conflicts documented, not resolved.** Library
and Develop mockups were designed independently. Where they disagree
on the same design element, document BOTH values under a
`CONFLICT-[N]` entry and do not pick a winner. CD will rule on each
conflict after reviewing your list.

**R3 — This task preempts all other Codex work.** Do not start any
other spec or audit task until Principia extraction is complete and
CD has reviewed.

**R4 — Companion tools use practical subset only.** Clipper, Prompt
Miner, PAH, Relay, BA, CONFORM are exempt from full Principia
pixel-precision verification. They must meet: correct palette tokens,
approved font chains, hover states on every button, no clipping, no
raw color literals.

**R5 — PG_TRUTH_v1.md stays frozen.** Add one bridging note in
Principia: "Where PG_TRUTH_v1.md says Review, read
Develop/Presentation — see Bible for current module names."

**R6 — CONFORM enhancement specced now.** Include a new section
`§CONFORM_ENHANCEMENT_SPEC` in Principia that specifies how CONFORM
should be enhanced to do mockup-vs-live screenshot diffing. This is
specced now; implementation is a separate future CC task.

## Purpose

PG_PRINCIPIA_v1.md must become the single authoritative design
reference for PG — trained on mockup data, not authored from memory.
Every CC implementer and CD reviewer should be able to open Principia,
find the exact expected value for any surface in any state, and verify
the live app against it without looking at the mockup HTML directly.

CONFORM's primary directive (per Darrin session 177): detect every
meaningful difference between approved mockup screenshots and the live
build UI, then produce AI-ready findings that are precise enough to
fix without guesswork: affected file, widget/component, observed
mismatch, expected mockup behavior, exact recommended change, and
verification step.

Principia is the reference document that makes this possible.

## Source files to read (in order)

### Tier 1 — Token and shell foundation (read first)
```
workflows/design/pg_overhaul_mockups_v2/tokens.css
workflows/design/pg_overhaul_mockups_v2/shell.css
workflows/design/pg_overhaul_mockups_v2/TYPOGRAPHY_SPEC.html
```

### Tier 2 — Library mockups (gold standard, primary extraction target)
```
workflows/design/pg_overhaul_mockups_v2/01_launch_patient_select.html
workflows/design/pg_overhaul_mockups_v2/02_patient_list_search.html
workflows/design/pg_overhaul_mockups_v2/03_new_patient_modal.html
workflows/design/pg_overhaul_mockups_v2/04_library_patient_selected.html
workflows/design/pg_overhaul_mockups_v2/05_library_import_flow.html
workflows/design/pg_overhaul_mockups_v2/06_library_empty_patient.html
workflows/design/pg_overhaul_mockups_v2/07_library_image_selected.html
workflows/design/pg_overhaul_mockups_v2/20_menus_right_click.html
```

### Tier 3 — Develop mockups (gold standard, primary extraction target)
```
workflows/design/pg_overhaul_mockups_v2/DEVELOP/README.html
workflows/design/pg_overhaul_mockups_v2/DEVELOP/TYPOGRAPHY_SPEC.html
workflows/design/pg_overhaul_mockups_v2/DEVELOP/08_develop_full_panel.html
workflows/design/pg_overhaul_mockups_v2/DEVELOP/09_develop_before_after.html
workflows/design/pg_overhaul_mockups_v2/DEVELOP/10_develop_lights_out.html
workflows/design/pg_overhaul_mockups_v2/DEVELOP/11_develop_annotation_active.html
workflows/design/pg_overhaul_mockups_v2/DEVELOP/11b_develop_toolbar_tool_states_montage.html
workflows/design/pg_overhaul_mockups_v2/DEVELOP/11c_toolbar_rightpanel_montage.html
workflows/design/pg_overhaul_mockups_v2/DEVELOP/11d_toolbar_rightpanel_full_lr_sliders.html
workflows/design/pg_overhaul_mockups_v2/DEVELOP/12_develop_crop_active.html
workflows/design/pg_overhaul_mockups_v2/DEVELOP/20b_menu_bar_complete_reference.html
```

### Tier 4 — Arrange and Presentation (secondary; extract what exists)
```
workflows/design/pg_overhaul_mockups_v2/13_arrange_empty_slots.html
workflows/design/pg_overhaul_mockups_v2/14_arrange_slots_filled.html
workflows/design/pg_overhaul_mockups_v2/19_arrange_drag_feedback.html
workflows/design/pg_overhaul_mockups_v2/15_presentation_control.html
workflows/design/pg_overhaul_mockups_v2/16_presentation_patient_facing.html
workflows/design/pg_overhaul_mockups_v2/17_export_dialog.html
workflows/design/pg_overhaul_mockups_v2/18_export_states.html
```

### Tier 5 — Live implementation reference (for comparison only)
```
styles.py                                    (live token registry)
styles/pg_shell.qss                          (live shell QSS)
workflows/design/LIBRARY_DESIGN_SPEC_v1.md  (ratified Library amendment)
workflows/design/PG_DESIGN_BIBLE_v1.md      (core grammar — secondary to mockups)
```

## Extraction methodology

For each mockup file:

1. Read the entire file. Do not skim.
2. Extract every CSS rule that defines a visual property:
   color, background, border, font-family, font-size, font-weight,
   letter-spacing, padding, margin, width, height, border-radius,
   gap, opacity, transition.
3. Map each value to the relevant Principia section (color, typography,
   spacing, component).
4. Record: property → value → mockup file + selector.
5. Where a token variable is used (e.g. `var(--color-accent)`),
   resolve it via tokens.css and record the resolved hex.
6. Where Library and Develop define the same property with different
   values, create a `CONFLICT-[N]` entry with:
   - The property and surface
   - Library value + source selector
   - Develop value + source selector
   - Your assessment of which is more consistent with the overall
     design language (do not pick — CD rules)

## Required Principia sections

Rebuild `PG_PRINCIPIA_v1.md` with these sections. Retain the
scaffold's P-numbering system; renumber if needed for coherence.

### §0 Authority, Scope, And Conflict Resolution
Keep from scaffold. Add R1–R6 rulings as canonical P-rules.
Add PG_TRUTH_v1.md bridging note (R5).

### §1 Core Product Principles
Keep from scaffold. No changes needed.

### §2 Source-Of-Truth Files
Update to reflect new authority order:
  1. Darrin ruling
  2. Approved mockup HTML (Tier 1–4 above)
  3. PG_PRINCIPIA_v1.md (this document, once ratified)
  4. Ratified module spec (e.g. LIBRARY_DESIGN_SPEC_v1.md)
  5. PG_DESIGN_BIBLE_v1.md
  6. styles.py / pg_shell.qss

### §3 Color System
Replace with mockup-extracted values. For every color token:
  - Hex value from tokens.css
  - Usage evidence: which mockup surfaces use it, what selector
  - Where Library and Develop differ: CONFLICT entry

### §4 Typography
Replace with mockup-extracted values. For every text role:
  - font-family chain
  - font-size (px)
  - font-weight
  - letter-spacing
  - line-height where specified
  - Source mockup file + selector

### §5 Spacing, Radii, And Density
Replace with mockup-extracted values. For every component:
  - Padding (px)
  - Margin / gap (px)
  - Border-radius (px)
  - Width/height constraints
  - Source mockup file + selector

### §6 Shell Components
Replace with mockup-extracted values. For every shell widget:
  - All CSS properties in all states (default, hover, active,
    disabled, focus)
  - Source mockup file + selector

### §7 Buttons And Action Controls
Replace with mockup-extracted values. Include:
  - Standard button all states
  - Primary button all states
  - Ghost/transparent button all states
  - Destructive button all states
  - Toolbar/compact button all states

### §8 Sliders, Scrollbars, Splitters, And Resizers
Replace with mockup-extracted values. Critical:
  - `11d_toolbar_rightpanel_full_lr_sliders.html` is the definitive
    LightroomSlider anatomy source. Extract every measurement.
  - Filmstrip size slider exact values
  - Scrollbar exact values
  - Splitter handle exact values

### §9 Text, Labels, Help, And Plain English
Keep from scaffold.

### §10 Layout And Workflow Order
Keep from scaffold.

### §11 Module Rules
Expand with mockup-extracted module-specific rules. One sub-section
per module: Library, Develop, Arrange, Presentation.

### §12 Icons
Keep from scaffold. Add any icon sizes found in mockup CSS not
already captured.

### §13 Implementation Discipline
Keep from scaffold.

### §14 Verification And Evidence
Keep from scaffold.

### §15 Anti-Patterns
Keep from scaffold.

### §16 Required Output Formats For Agents
Keep from scaffold.

### §17 Conflicts For CD Resolution
NEW SECTION. List every CONFLICT-[N] entry found during extraction.
Format per conflict:
```
CONFLICT-[N]
Surface: [what widget/element]
Property: [CSS property]
Library value: [hex/px/etc] (source: [file] [selector])
Develop value: [hex/px/etc] (source: [file] [selector])
Assessment: [which appears more consistent and why — do not pick]
CD ruling: [PENDING]
```

### §18 CONFORM Enhancement Spec
NEW SECTION. Spec the following CONFORM enhancements (implementation
is a future CC task — spec only here):

**Goal:** CONFORM must detect every meaningful difference between an
approved mockup screenshot and the live app screenshot for the same
state, then produce AI-ready findings with:
  - Affected file and widget/objectName
  - Observed value in live app
  - Expected value per mockup
  - Exact recommended change
  - Verification step

**Required capabilities:**
1. Screenshot capture: `panda_gallery.py --screenshot-mode [state]`
   captures live app screenshot at a defined state. Already partially
   implemented (Wave 4 Phase 1 in progress via CC).
2. Mockup rendering: CONFORM renders the approved mockup HTML at the
   same viewport dimensions and captures a reference screenshot.
3. Region-level diffing: CONFORM compares the two screenshots
   region-by-region using the existing REGION_MAP structure.
4. Value extraction: for CRITICAL or WARN regions, CONFORM queries
   the live Qt widget tree for the actual CSS/property values and
   compares against Principia's extracted reference values.
5. AI-ready report: output is a structured finding per region with
   all 6 required fields (file, widget, observed, expected, change,
   verification).

**Out of scope for this spec:** implementation details, pixel
threshold tuning, perceptual hash algorithm selection. Those are CC
implementation decisions.

### §19 Vocabulary Bridging
NEW SECTION. One line: "Where `PG_TRUTH_v1.md` says Review, read
Develop/Presentation — see `PG_DESIGN_BIBLE_v1.md` for current
module names."

### §20 Coverage Estimate
Update from scaffold to reflect actual extraction completion per
section. Be honest about gaps.

### §21 Self-Review
Minimum 5 passes. Report pass count and issues fixed per pass.

## Delivery requirements

File to `C:\panda-gallery\workflows\design\PG_PRINCIPIA_v1.md`.

Mail to CLAUDE Inbox with:
- Authored file path
- Total P-rule count
- Conflict count (CONFLICT-[N] list summary)
- Self-review pass count
- Sections still needing CD input before ratification
- Any mockup files that could not be fully parsed

## Acceptance gate

CD reviews conflict list and rules on each. After conflict rulings
are folded in, Principia is ratified. Once ratified it becomes the
primary authority for all CC dispatches and CONFORM verification.

## What this task is NOT

- Do not write any Python/Qt code.
- Do not commit anything.
- Do not start the CONFORM enhancement implementation.
- Do not amend the Bible until CD reviews conflicts and rules.
- Do not touch any file outside PG_PRINCIPIA_v1.md.

— CD
