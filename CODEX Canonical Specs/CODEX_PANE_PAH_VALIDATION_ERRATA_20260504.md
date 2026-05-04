# CODEX Pane / PAH Inspector Validation Errata

Created: 2026-05-04

Status: active errata for spec-readiness review

Scope:

- `C:\CODEX PG\CODEX Canonical Specs\CODEX_PANE_v3_DESIGN_SPEC.md`
- `C:\CODEX PG\CODEX Agent Hub\CODEX_PAH_MAIL_AND_INSPECTOR_UX_SPEC.md`
- Live read-only validation against `C:\panda-gallery` pane/result code
- Live validation against PAH smoke, Inspector, and server smoke checks

## Validation Evidence

Commands run on 2026-05-04:

- `python C:\CODEX PG\CODEX Agent Hub\CODEX_run_smoke_tests.py`
- `python C:\CODEX PG\CODEX Agent Hub\CODEX_pah_inspector.py`
- `& C:\CODEX PG\CODEX Agent Hub\CODEX_run_server_smoke.ps1`
- `python -m pytest tests\test_inspector_i1_rename.py tests\test_inspector_i2_phases1_3.py tests\test_inspector_i3_phases4_8.py tests\test_results_writer.py -q`

Results:

- PAH smoke tests passed.
- PAH Inspector ran and returned `42 pass / 2 warn / 0 fail`.
- PAH server smoke returned `readiness_ok:true`, `performance_ok:true`, `diagnostics_ok:false`.
- Panda Gallery pane-focused tests passed: `120 passed`.

Conclusion:

- The live Panda Gallery pane/result behavior is test-passing for the focused pane test set.
- The PAH Inspector works as a warning-state health surface.
- Do not claim PAH is fully healthy/green while `diagnostics_ok:false` and Inspector warnings remain.

## Errata 1: Pane v3 Is Aspirational, Not Live

`CODEX_PANE_v3_DESIGN_SPEC.md` is a draft v3 design contract, not a verified description of the current live Panda Gallery pane.

Current live evidence:

- `C:\panda-gallery\instruction_pane.py` supports `SUPPORTED_SCHEMA_VERSIONS = {1, 2}`.
- The v3 spec introduces `schema_version: 3`.

Impact:

- Future agents must not treat the v3 spec as implemented runtime behavior.
- Any implementation task based on Pane v3 must first define a migration/spec update path from the current v1/v2 runtime.

## Errata 2: PASS_WITH_NOTE Conflict

`CODEX_PANE_v3_DESIGN_SPEC.md` says a PASS with a note remains persisted as `outcome: "PASS"` plus a separate `note` field, and says not to introduce `PASS_WITH_NOTE`.

Current live evidence:

- `C:\panda-gallery\instruction_pane.py` defines and uses `PASS_WITH_NOTE`.
- `C:\panda-gallery\results_writer.py` advertises `pass_with_note` in result capabilities.
- Existing focused pane tests assert `PASS_WITH_NOTE` behavior.

Impact:

- The v3 spec conflicts with shipped live behavior and tests.
- Before implementation, decide whether v3 supersedes live behavior or whether the spec should be amended to preserve `PASS_WITH_NOTE`.

## Errata 3: Pane Size Drift

`CODEX_PANE_v3_DESIGN_SPEC.md` recommends default size `720 by 680` and minimum size `520 by 560`.

Current live evidence:

- `C:\panda-gallery\instruction_pane.py` uses `DEFAULT_SIZE = (640, 640)`.
- `C:\panda-gallery\instruction_pane.py` uses `MIN_SIZE = (420, 480)`.

Impact:

- Treat spec sizing as a design target, not current behavior.
- Any size change needs visual verification, especially because prior pane work deliberately supported a narrower two-row action bar.

## Errata 4: Checklist Required-Item Ambiguity

`CODEX_PANE_v3_DESIGN_SPEC.md` says checklist derivation depends on "required items," but the schema section does not define whether checklist items can be optional or how optional items are encoded.

Impact:

- Checklist outcome derivation is ambiguous for v3 authoring and runtime validation.
- The spec should define either all checklist items as required, or add an explicit optional-item field and derivation rules.

## Errata 5: PAH Mail Default And Draft Ambiguity

`CODEX_PAH_MAIL_AND_INSPECTOR_UX_SPEC.md` describes Mail as the default landing surface, while its known gaps state Mail exists as an overlay and is not yet the default landing surface.

The same spec requires per-message draft preservation, but also says current draft-clearing behavior is acceptable only as an early prototype.

Impact:

- Current PAH Mail should be classified as prototype/partial for these requirements.
- Acceptance criteria should distinguish "current allowed gap" from "must be true before completion."

## Errata 6: PAH Inspector Works But Is Warn-State

Current validation proves Inspector runs, endpoint checks work, mailroom canary works, read-state can be written, reply tombstones are created, and interaction ledger evidence exists.

Current warnings:

- CC sidecar readiness warning.
- Communication backlog warning.

Current server smoke:

- `diagnostics_ok:false`

Impact:

- Inspector can be described as functional.
- PAH cannot be described as fully healthy until the warning/diagnostics state is resolved or explicitly accepted as a known condition.

## Review Iterations

Round 1 found Pane v3/live drift:

- `schema_version: 3` versus live `{1, 2}` support.
- `PASS_WITH_NOTE` prohibition versus live `PASS_WITH_NOTE`.
- v3 recommended sizing versus live sizing.

Round 2 found PAH acceptance ambiguity:

- Mail default surface versus current overlay.
- Draft preservation requirement versus accepted prototype behavior.
- Inspector acceptance must include deeper evidence than endpoint existence.

Round 3 found remaining significant issues:

- Checklist "required item" semantics are undefined.
- Automated/API validation did not include a live browser visual pass.
- PAH remains warning-state with `diagnostics_ok:false`.

Round 4 found no new significant errors beyond the issues above.

