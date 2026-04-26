# Codex to Claude: Pane v3 Design Spec v1 Complete

Status: COMPLETE

Completed: 2026-04-25 19:22 local

Primary output:

- `C:\CODEX PG\CODEX Canonical Specs\CODEX_PANE_v3_DESIGN_SPEC.md`

Verification:

- Spec line count: 996
- Boundary respected: no edits made under `C:\panda-gallery`
- Source files were read-only references only

Core decisions resolved:

1. PASS with note remains `outcome: "PASS"` plus separate `note`; no persisted `PASS_WITH_NOTE` enum.
2. Acknowledgement persists as a compact recent-activity strip, not a timer-only toast.
3. Mid-run navigation is a pane-native index drawer plus compact progress header.
4. Action/setup steps remain `kind: "action"`, render as SETUP with DONE, and persist machine outcome `ACK`.
5. v3 lint runs at write-time and load-time; v3 lint errors block load, while v1/v2 legacy files remain readable.
6. Instruction files move to `schema_version: 3`; v1/v2 render in legacy-compatible mode with no runtime auto-migration.
7. Paper-mode export is retained and improved around the v3 fields.

Implementation sequence recommended in the spec:

1. Schema and lint fixtures
2. Result-note compatibility
3. Version-gated v3 renderer
4. Inline notes replacing FAIL modal notes
5. Action bar advancement and acknowledgements
6. Stable checklist row controls
7. Index drawer
8. v3 paper export
9. Regression checks for retained safety behavior

Notes:

- The spec treats `CODEX_INSTRUCTION_PANE_UX_v2_SPEC.md` as retained-context only, not as the v3 design template.
- The minimum useful v3 is schema v3 plus inline notes plus acknowledged advance.
- The full v3 is schema v3 plus inline notes, action bar advancement, index drawer, stable checklist rows, legacy mode, and paper export.
