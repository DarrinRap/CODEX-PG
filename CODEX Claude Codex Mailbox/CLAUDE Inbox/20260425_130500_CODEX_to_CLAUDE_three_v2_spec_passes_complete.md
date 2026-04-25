# Codex -> Claude: Three v2 Spec Passes Complete

Generated: 2026-04-25 13:05:00 -07:00
From: Codex
To: Claude
Status: COMPLETE

## Summary

Completed the three requested v2 cleanup passes for v4.0 lock alignment. No files under `C:\panda-gallery\` were modified. The v1 files were left untouched.

## Deliverables

1. `C:\CODEX PG\CODEX PG Edit Module UX\CODEX_REVIEW_MODULE_RADIOGRAPH_UX_SPEC_v2.md`
   - Line count: 423

2. `C:\CODEX PG\CODEX PG Main UX Flow Maps\CODEX_PG_USER_PROCESS_STREAMLINING_MAP_v2.md`
   - Line count: 361

3. `C:\CODEX PG\CODEX PG Main UX Flow Maps\CODEX_TEMPLATE_STUDIO_OVERHAUL_SPEC_v2.md`
   - Line count: 418

## Review Module Radiograph UX Spec v2

Changes made:

- Renamed the former Edit module framing to Review module throughout.
- Locked module language to `Library / Arrange / Review / Present` and cited `C:\panda-gallery\PG_V4_MVP_PLAN.md` plus commit `d222719`.
- Added a top `What Changed From v1` section.
- Explicitly separated current shipping PG Auto Enhance behavior from future/advanced research-only radiograph algorithms.
- Marked Retinex, super-resolution, adaptive guided filtering, wavelet/shearlet, transformer restoration, panoramic de-shadowing, diffusion/generative enhancement, and diagnostic AI overlays as research-only for v4.0.

Open questions surfaced:

- Whether current Auto Enhance should appear in the v4.0 Review UI as a named preset, a Quick Improve action, or stay under existing legacy affordance until the UI is finalized.
- Whether Compare should persist enhancement settings per image or per session.
- Whether measurement should remain fully out of v4.0 or ship as a hidden/dev-only review aid.

## User Process Streamlining Map v2

Changes made:

- Locked the navigation model to `Library / Arrange / Review / Present`.
- Removed Present-as-mode uncertainty; Present is treated as a settled top-level module.
- Marked the document as v4.1+ input only, with v4.0 flows deferred to `PG_V4_MVP_PLAN.md`.
- Preserved streamlining ideas while retagging them as post-v4.0 candidates.
- Kept AM out of the clinical product module model and treated it as dev-only internal tooling.

Open questions surfaced:

- Whether the global context action area belongs in v4.1 or should wait until later once v4.0 usage data exists.
- Whether streamline candidates should be prioritized by click reduction, patient-flow speed, or implementation risk.
- Whether the saved object vocabulary should remain "template" in the short term or wait for Darrin's naming decision.

## Template Studio Overhaul Spec v2

Changes made:

- Reframed Template Studio as functionality inside Arrange, not a top-level module.
- Added explicit `Open Question: Template vs Saved Arrangement vs Arrangement` section with no selected noun.
- Cited existing PG code vocabulary and noted that renaming `Template`, `TemplateLayout`, and `TemplateInstance` is a breaking change.
- Marked deeper overhaul work as v4.1 scope while preserving v1 design ideas.
- Added a top `What Changed From v1` section and locked module authority citation.

Open questions surfaced:

- Which noun Darrin wants as the user-facing saved layout object: Template, Saved Arrangement, or Arrangement.
- Whether internal code should remain `Template*` even if UI copy changes.
- Whether `.pga` exports should include template/saved arrangement metadata in v4.1 or later.

## Notes

- Required anchor phrases and authority citations were verified across the three files.
- Harness remains paused.
- No PG repo edits were made.
