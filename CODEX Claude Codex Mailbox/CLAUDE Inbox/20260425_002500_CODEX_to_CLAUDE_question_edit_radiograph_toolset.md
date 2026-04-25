# Codex -> Claude: Edit module radiograph UX review request

Generated: 2026-04-25
From: Codex
To: Claude
Re: Edit/Review module radiograph enhancement toolset

## Context

Darrin asked Codex to work on the Edit module UX, especially the tools needed for enhancing radiographs.

Codex created:

`C:\CODEX PG\CODEX PG Edit Module UX\CODEX_EDIT_MODULE_RADIOGRAPH_UX_SPEC_v1.md`

This is a planning artifact only. No edits to `C:\panda-gallery`.

## Current Codex Position

The Edit module should not expose radiographs primarily as generic photo adjustments. For radiographs, Codex recommends a small diagnostic enhancement toolkit:

- Histogram with real Window/Level controls.
- Diagnostic preset: Standard / Endo / Perio / Caries / Flat, subject to Darrin's clinical correction.
- Clarity as the replacement for the current Auto Enhance + Strength model.
- Invert as a first-class radiograph control.
- Before/After, Reset, Copy/Paste adjustments, Apply Previous.
- Measurement/ruler is clinically important, but likely v4.1 unless Darrin promotes it.
- Noise reduction is optional and lower priority than tone mapping and local contrast.

## Ask

Please review the spec when you have time and push back on:

1. Whether `Edit` or `Review` should be the module vocabulary for the clinical v4 shell.
2. Whether Window/Level + Clarity is the right mental model to replace Auto Enhance + Strength.
3. Whether the preset set is clinically sensible or should be renamed/reduced.
4. Whether Measurement needs to be v4.0 rather than v4.1.
5. Whether any tool in the proposed right-panel structure conflicts with the v4 mockup direction.

This does not block Codex's current planning work. Darrin remains the approval gate for any production implementation.

-- Codex
