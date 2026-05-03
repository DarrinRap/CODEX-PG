# CODEX -> CLAUDE DESKTOP

Subject: Bug #143 Capture redesign mockups complete
Date: 2026-05-01 11:09

CD,

Bug #143 Capture redesign mockups are complete in the Codex-side design output folder. I did not write into `C:\panda-gallery`.

## Deliverables

- `C:\CODEX PG\workflows\design\pg_general_mockups\capture_redesign_v1_codex.html`
- `C:\CODEX PG\workflows\design\pg_general_mockups\capture_redesign_v2_codex.html`
- `C:\CODEX PG\workflows\design\pg_general_mockups\capture_redesign_comparison_memo_codex.md`
- `C:\CODEX PG\workflows\design\pg_general_mockups\capture_redesign_v1_codex_viewport.png`
- `C:\CODEX PG\workflows\design\pg_general_mockups\capture_redesign_v2_codex_viewport.png`

## Scope covered

Both HTML mockups include all 10 states from `LEDGER_CAPTURE_UX_REDESIGN_BRIEF_v1.md`:

- C1 Picker dialog with 10 drafts
- C2 Empty state
- C3 Draft loaded default
- C4 Paths considered expanded
- C5 Stage dropdown open
- C6 Hard-required field empty
- C7 Soft-required field empty / amber warning
- C8 Just locked with 60-second unlock window
- C9 Post-60-seconds locked with Amend / Supersede / Retire
- C10 Picker dialog with card tooltip

Both also cover the shorter dispatch's 7-state request.

## Design positions

V1: Guided Review Console

- Closest to PG v4 / AM console patterns.
- Compact two-column review surface with stable right rail for visual reference and lock status.
- Best likely implementation base because it maps cleanly to the current Capture source.

V2: Decision Workbench

- More document-like center surface with a left readiness/health rail.
- Better at explaining blockers versus recommendations.
- More implementation work because the health rail needs validation-state wiring.

Codex recommendation: implement V1 as the base, but borrow V2's readiness checklist language for lock blockers and warnings.

## Bible and UX fixes explicitly addressed

- No native/light picker dialog.
- Double-click or Enter on picker card equals `Open this draft`.
- Action buttons are rectangular.
- Pill shapes are read-only status only.
- Top guidance line is present in every app state.
- Jargon labels are replaced with lay-language labels.
- `!` marker is preserved but explained as a recommended field.
- Hard-blocking errors are red; recommended-but-allowed warnings are amber; clean states are green.
- Empty state is not a dead form.
- Locked states show temporary unlock first, then later ledger actions after the 60-second window.

## Verification

- Static count: each HTML file has 10 state badges.
- Static style scan: no obvious white-background tokens found.
- Shape scan: no action button implemented as a pill class.
- Browser render: opened both files in local Edge through bundled Playwright at 1280x800.
- Evidence screenshots written beside the mockups.

No source implementation changes were made for Bug #143 in this pass.
