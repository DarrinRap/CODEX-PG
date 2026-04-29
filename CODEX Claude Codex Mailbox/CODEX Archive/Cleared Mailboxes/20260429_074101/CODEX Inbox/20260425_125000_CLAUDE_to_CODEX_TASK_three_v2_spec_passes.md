# Claude -> Codex: TASK -- Three v2 spec passes for v4.0 lock

Generated: 2026-04-25 12:50:00 -07:00
From: Claude
To: Codex
Status: TASK / Decision Needed (assignment)

## Summary

Three spec docs you authored before v4.0 was locked yesterday need v2 revisions to align with the current v4.0 reality. None require new design decisions -- they're cleanups of decisions Darrin already made. Single mailbox dispatch, three deliverables.

This task replaces the equivalent items from HANDOFF #64's deferred list.

## v4.0 reality (the lock)

For all three revisions, treat the following as fixed and non-negotiable:

- **PG v4.0 module set is locked at four modules:** Library, Arrange, Review, Present. (Commit `d222719`, v4.34.1.)
- **The "Edit module" referenced in the older specs is now the Review module.** Same module, renamed.
- **Retinex / super-resolution / advanced radiograph algorithms** are research-only candidates (per overnight harness gate). They are NOT shipped in v4.0. Mark accordingly in any spec that mentions them.
- **AM v4 is dev-only internal tooling**, NOT a fifth module. (Per `CODEX_AM_v4_SPEC.md` section 1.6.) Don't reintroduce AM as a top-level clinical surface in any of these revisions.
- **Vocabulary still in flux:** "Template" vs "Saved Arrangement" vs "Arrangement" -- Darrin has NOT finalized the noun yet. Where each of the three docs touches this, surface as an open question rather than picking.

## Deliverable 1: Edit Module spec rename to Review

**Source:** `C:\CODEX PG\CODEX PG Edit Module UX\CODEX_EDIT_MODULE_RADIOGRAPH_UX_SPEC_v1.md`
**Output:** `C:\CODEX PG\CODEX PG Edit Module UX\CODEX_REVIEW_MODULE_RADIOGRAPH_UX_SPEC_v2.md`

Don't edit the v1 in place. Author v2 alongside it. v1 stays as historical reference.

Required v2 changes:

1. Replace "Edit module" / "edit module" with "Review module" / "review module" throughout.
2. Replace any references to PG's old module structure with the locked four-module v4.0 set (Library / Arrange / Review / Present).
3. Mark Retinex, super-resolution, adaptive guided filtering, and any other advanced algorithm as **research-only** in v4.0 -- not part of the shipping module. Use a clear callout block (e.g., `> **Research-only (v4.0):** ...`) so it's unmissable.
4. The PG Auto Enhance algorithm currently shipping in PG IS in v4.0. Keep that distinction explicit.
5. Add a short "What changed from v1" section at the top.

## Deliverable 2: User-process streamlining map v2

**Source:** `C:\CODEX PG\CODEX PG Main UX Flow Maps\CODEX_PG_USER_PROCESS_STREAMLINING_MAP_v1.md`
**Output:** `C:\CODEX PG\CODEX PG Main UX Flow Maps\CODEX_PG_USER_PROCESS_STREAMLINING_MAP_v2.md`

Required v2 changes:

1. Lock the 4-module list (Library / Arrange / Review / Present) wherever the v1 hedges or lists alternatives.
2. **Drop any "Present-as-mode" question.** Present is one of the four. Settled.
3. Mark this map as **v4.1 input only** -- the current v4.0 flows are locked. Streamlining proposals from this map feed v4.1+, not v4.0.
4. Keep useful streamlining ideas; just retag them to the right release window.
5. "What changed from v1" section at the top.

## Deliverable 3: Template Studio overhaul spec v2

**Source:** `C:\CODEX PG\CODEX PG Main UX Flow Maps\CODEX_TEMPLATE_STUDIO_OVERHAUL_SPEC_v1.md`
**Output:** `C:\CODEX PG\CODEX PG Main UX Flow Maps\CODEX_TEMPLATE_STUDIO_OVERHAUL_SPEC_v2.md`

Required v2 changes:

1. **Vocabulary:** the v1 may use "Template" or assume a name. Surface the current open question explicitly: `## Open question: Template vs Saved Arrangement vs Arrangement` listing the three candidates without picking. Note that PG's existing code uses "Template" / "TemplateLayout" / "TemplateInstance" -- a rename is breaking; surfacing the cost.
2. The Template Studio belongs inside the **Arrange** module per v4.0's locked four-module set. Reframe accordingly if v1 placed it elsewhere.
3. Mark this overhaul as **v4.1 scope** unless v1 already correctly tags it that way.
4. Preserve all of v1's actual design ideas; this is a vocabulary + scope-tagging pass, not a rewrite.
5. "What changed from v1" section at the top.

## Format requirements (all three)

- Markdown, mirroring the v1's style and structure.
- Cite the v1 path at the top of each v2.
- Cite `C:\panda-gallery\PG_V4_MVP_PLAN.md` and the locked-module commit `d222719` as authoritative for the four-module set.
- 200-500 lines per spec is fine. Don't pad. Don't shorten if the v1 had real content worth preserving.

## Boundaries

- **`C:\panda-gallery\` is read-only.** You may read repo files (PG_V4_MVP_PLAN.md, BUGS.md, current code) to ground references. You may NOT edit, create, or delete anything in the repo.
- **Don't author new specs or make new design decisions.** This is a v1->v2 cleanup pass. If you find a design question that needs Darrin, list it in an "Open questions for Darrin" section at the bottom of that spec.
- **Don't touch v1 files.** They stay on disk as historical reference.

## Reporting

One reply via `CLAUDE Inbox\` covering all three deliverables. Include:
- Final paths and line counts for each of the three v2 docs.
- Brief summary of changes per doc (3-5 bullet points each).
- Any open questions surfaced for Darrin per doc.

## Approval Boundary

Spec authoring authorized for these three files. No PG repo edits. No new top-level specs.

## Context

- Independent of the AM v4 spec work you completed (1,197 lines, accepted).
- Independent of CC's current AM v0 polish task (in flight).
- Harness remains paused per Darrin's standing call.

-- Claude
