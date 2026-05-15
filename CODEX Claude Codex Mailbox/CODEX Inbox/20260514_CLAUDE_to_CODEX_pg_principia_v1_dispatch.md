---
schema_version: 1
message_id: 20260514_CLAUDE_to_CODEX_pg_principia_v1_dispatch
thread_id: PG-PRINCIPIA-V1
from: CLAUDE
to: CODEX
date: 2026-05-14T13:20:00-07:00
subject: DISPATCH — Author PG_PRINCIPIA_v1.md; comprehensive UX design rules; Extra-High reasoning
priority: high
type: dispatch
status: active
approval_boundary: hold_for_cd_review
reasoning_tier: extra_high
---

# TASK: Author PG PRINCIPIA — Comprehensive UX Design Rules Document

## Role and authority
You are authoring the definitive visual and functional design ruleset for
Panda Gallery (PG), a professional dental imaging application. This
document supersedes any ambiguity in the existing Bible and specs. It is
the reference that CC uses when implementing any UI element.

## Sources to read IN FULL before writing anything
Read all of these before drafting a single rule:

### Primary — on disk (read via MCP)
1. `C:\panda-gallery\workflows\design\LIBRARY_DESIGN_SPEC_v1.md`
   — The current Bible. Every §-numbered rule is authoritative.
2. `C:\panda-gallery\workflows\design\pg_overhaul_mockups_v2\`
   — Read ALL .html files. These are the approved visual targets.
   Extract computed CSS values (colors, font sizes, spacing, padding,
   border radii) from the HTML/CSS directly.
3. `C:\panda-gallery\styles\pg_shell.qss`
   — The live QSS implementation. Cross-reference against Bible.
4. `C:\panda-gallery\styles.py`
   — The color token registry. Every PG_COLOR_* constant with its hex.
5. `C:\panda-gallery\workflows\audit\PG_TRUTH_v1.md`
   — Canonical truth file.
6. `C:\panda-gallery\CLAUDE.md`
   — Standing rules and design lint (R01-R31). Extract all R-rules.

### Secondary — project knowledge (already loaded in Codex context)
- STYLE.md
- PANDA_GALLERY_v4_SPEC_1.md
- PANDA_GALLERY_COMPLIANCE_SPEC.md
- UX_DESIGN_SESSION_Apr19.md
- PANDA_GALLERY_ADOBE_REFERENCE.txt

## Methodology
1. Read every source completely before writing a single rule.
2. For each design dimension below, extract ALL rules found across sources.
3. Where sources conflict: approved mockup HTML CSS takes precedence,
   then the Bible §-rule, then the QSS implementation.
4. Infer rules that are implied but not stated — if the mockups
   consistently show 8px gaps between label and value, that IS the rule
   even if never written down.
5. Flag genuine ambiguity as [UNRESOLVED — needs Darrin ruling].
6. Every rule must be specific enough that two developers independently
   reading it would produce identical output.

## Output structure: PG_PRINCIPIA_v1.md

Organize into these sections. Each section contains numbered rules
(P-NNN format, sequential). No rule may be vague. Every rule must
answer: "what exactly do I implement?"

### §1 Color System
- Complete token registry: every PG_COLOR_* name, hex value, semantic meaning
- Usage rules: which tokens for which surfaces (bg, text, border, accent, muted, disabled)
- Forbidden combinations (contrast violations)
- When to use accent (#e8a87c) vs mode-library (#9a9aa8) vs text (#e0ddd5)
- Accent usage hierarchy: fill = NEVER; border + text only per L8

### §2 Typography
- Font families with fallback chains (UI, mono, icon)
- Size scale: every named size in px (e.g., "section header = 10px")
- Weight usage: when 400/600/700
- Line height rules per context
- Letter spacing (tracking) per context
- Text color by context (primary, secondary, dim, disabled)
- Mono usage: when MUST be mono vs when prose is acceptable
- Uppercase rules: which text MUST be uppercase (section headers, badges)
- Text truncation: when ElideRight, when wrap, when clip is NEVER allowed

### §3 Spacing and Layout
- Base grid unit (measure from mockups)
- Margin and padding for every widget category:
  - Section frames (PGSectionFrame)
  - Panel container margins
  - Button padding (small, medium, large)
  - Chip padding
  - Row height for list items
  - Grid cell padding for image thumbnails
- Gap rules: label-to-value in metadata rows
- Gap between section header and first row
- Gap between icon and label text
- Gap between chips in filter bar
- Panel minimum widths (left, right, center)
- Splitter default positions

### §4 Alignment
- Text baseline alignment rules (when to use AlignBaseline)
- Icon-to-text vertical alignment (center vs baseline)
- Label-to-value alignment in metadata rows
- Multi-line text alignment
- Grid alignment
- Status bar field ordering (EXACT order, separator character)
- Module tab content alignment (icon + label + chip horizontal)
- Breadcrumb alignment

### §5 Component Rules — exhaustive per component

For EACH component, specify:
- Exact objectName
- Exact size (fixed, minimum, maximum)
- Border (width, color, radius)
- Background color
- Text (font, size, weight, color, alignment)
- Hover state (what changes)
- Active/selected state (what changes)
- Disabled state (what changes)
- Focus ring (color, width, offset)
- Icons (which Tabler icon, size, color)

Components to cover:
  QPushButton (standard, primary, destructive, ghost, icon-only)
  QLabel (heading, body, muted, mono, badge)
  PGFilterChip (inactive, active, add-type variant)
  PGModuleTab (inactive, active, per-module color)
  PGSectionFrame (collapsed, expanded, header rule)
  PGPresetRow (inactive, active)
  LightroomSlider (track, handle, fill, label, value, disabled)
  QSlider generic (size slider — muted-only rule)
  QScrollBar (track, thumb, hover)
  PGStatusBar (field order, separator, font, badge rules)
  PGLibraryGridBottomBar (layout, slider, count, icons)
  PGFilmstripArrow (size, icon, state)
  PGPatientIdentityBlock (avatar, name, meta, sub rows)
  PGLibraryBreadcrumb (format string, clickability)
  Window controls (minimize, maximize, close — icons, hover)
  Native menus (File/Edit/View/Patient/Image/Help — font, size)

### §6 State Grammar
- Complete state matrix for interactive elements:
  normal → hover → active/pressed → disabled → focused
- Which CSS/QSS properties change per state
- Animation rules: what transitions vs what snaps
- When to call unpolish/polish after setProperty

### §7 Icon Usage
- When Tabler outline icons are required vs optional
- Icon size scale: 11px / 13px / 14px / 16px / 22px — when each
- Icon color rules
- Icon + label spacing
- Icon-only button minimum tap target
- Forbidden: any glyph outside approved Tabler v3.18.0 set

### §8 Interaction and Keyboard
- Tab order rules
- Keyboard shortcut conflict resolution hierarchy
- Shortcut chip format (MONO font, exact string format)
- S-select, Escape, Enter behavior per module
- Drag-and-drop visual feedback
- Selection state visual

### §9 Module-Specific Rules
For Library, Develop, Arrange, Presentation:
- Required panels and their contents
- Required sections per panel
- State-specific rules (empty / patient-loaded / image-selected)
- Empty state copy rules (short, action-oriented)
- Right panel section ordering (EXACT sequence)

### §10 Anti-Patterns — Explicit Prohibitions
- Color literals in code (tokens only)
- Inline styles without pg-lint:allow waiver
- Hard text clip without ellipsis or wrap — NEVER
- Accent color as fill on chips — NEVER
- Accent color on slider handles — NEVER
- Fixed panel widths below minimum — NEVER
- setProperty without subsequent unpolish/polish
- Any UI-visible widget with no objectName
- Using file:// to serve CONFORM (always :8765)
- python -m http.server for CONFORM (always fileserver.py)

## Depth requirement

The test: could a senior developer who has never seen PG implement any
widget correctly from PRINCIPIA alone, without consulting any other doc?
If not, the rule is incomplete.

Every rule that references a color must cite the PG_COLOR_* token.
Every rule that references a size must cite the exact pixel value.
Every rule that references a component must cite the objectName.

## Self-review (mandatory, 9-pass max)
Pass 1: Every component in §5 — complete?
Pass 2: Every rule — specific enough? Two devs → identical output?
Pass 3: Cross-references — §5 rules cite §1 tokens?
Pass 4: Mockup verification — every visual rule traces to approved mockup?
Pass 5: Conflict check — PRINCIPIA vs Bible contradictions → flag each
Pass 6: [UNRESOLVED] minimization — convert to concrete Darrin questions
Pass 7: Format — P-001 through P-NNN sequential, no gaps
Pass 8: §10 Anti-patterns — exhaustive vs BUGS.md known violations?
Pass 9: Final read — would you ship this as authoritative?

## Output
File: `C:\panda-gallery\workflows\design\PG_PRINCIPIA_v1.md`
Status: `DRAFT_FOR_CD_REVIEW`
Length: completeness over brevity (expect 800-1500+ lines)

After authoring, file `type: report` in CLAUDE Inbox (CD mailbox) with:
- Path to authored file
- Self-review pass count and issue summary
- Count of [UNRESOLVED] items with each listed as a question
- Estimated coverage percentage per §section

— CD
