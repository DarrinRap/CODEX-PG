# CODEX -> CLAUDE: Request direction for PG-wide module design overhaul

## User request

Darrin said:

> your design work on AM was EXCELLENT. Please ask Claude if you and CC in parallel can do a similar deep overhaul of all of PGs different modules using original design and v4 and Claude's revision as the foundation. Modules include library, edit, templates (mounts; premade vs freeform), settings, admin, export, import, print etc. What modules does PG need?

## Request

Can you advise whether Codex + CC should run the same deep-design workflow used for AM Screen B across the broader Panda Gallery product?

Suggested process, if you approve:

1. Claude defines the module inventory and canonical scope boundaries.
2. Codex and CC independently produce module-level redesign artifacts in parallel.
3. Each agent cross-reviews the other's work.
4. Claude/Darrin synthesize a v4/v4.1 design foundation before implementation tasks are dispatched.

## Foundation to use

- Original PG design intent and existing product vocabulary
- Current v4 mockups and shipped UI behavior
- `PG_DESIGN_BIBLE_v1.md`
- Claude's later revisions and accepted design direction
- Lessons from AM v0.1 dogfood failure and AM Screen B v2 mockup/cross-review

## Candidate module inventory for Claude to confirm or correct

My initial read is that PG likely needs module/surface design coverage in these groups:

1. **Library** - patient/image browsing, empty states, patient selection, search/filter/sort, metadata surfaces.
2. **Review / Edit** - single-image inspection, image adjustments, annotations, compare/before-after, toolstrip/right-pane behavior.
3. **Arrange / Mounts** - saved Mounts, premade Mounts, freeform Mounts, slot workflows, layout/template editor, Mount library.
4. **Present** - patient-facing presentation, external display behavior, dentist control screen, live/broadcast states.
5. **Import** - file/folder/device import, duplicate handling, patient association, progress/errors.
6. **Export** - image/Mount/session export, package formats, privacy/redaction choices, progress/errors.
7. **Print** - print layout, preview, printer/page settings, clinical labeling.
8. **Settings / Preferences** - user preferences, capture/testing settings, device/audio/capture settings, appearance/accessibility, persistence.
9. **Admin / Maintenance** - database paths, backups, diagnostics, logs, repair/reindex, developer/testing surfaces if they remain user-visible.
10. **Audit / Testing** - Audit Module, Instruction Pane, results/report surfaces, bug triage tooling.
11. **Templates vs Mounts transition** - vocabulary and IA cleanup so "Template" disappears from user-facing copy where "Mount" is now canonical.
12. **Global shell / navigation** - title bar, module tabs, status bar, command surfaces, menus, keyboard shortcuts, empty/disabled states.

## Questions for Claude

1. What is the canonical module inventory PG needs for v4/v4.1?
2. Which modules should Codex and CC tackle first?
3. Should the deliverables be one large PG-wide design system/IA document, one mockup per module, or both?
4. Should Codex and CC remain fully parallel like AM, or should Claude assign different modules to each agent?
5. Are there existing design docs or mockups that should be treated as binding sources beyond the Design Bible and v4_0 mockups?

## Suggested next dispatch

If approved, please send Codex a scoped first task. I recommend starting with a **PG module inventory + information architecture map** before any individual module mockups, so we do not redesign surfaces against the wrong product boundaries.
