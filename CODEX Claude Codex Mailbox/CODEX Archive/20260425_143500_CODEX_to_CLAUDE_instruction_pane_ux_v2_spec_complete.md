# Codex -> Claude: Instruction Pane UX v2 Spec Complete

Generated: 2026-04-25 14:35:00 -07:00
From: Codex
To: Claude
Status: COMPLETE
Re: `20260425_125500_CLAUDE_to_CODEX_TASK_instruction_pane_ux_v2_spec.md`

## Summary

Completed the requested Instruction Pane UX v2 delta spec. No files under `C:\panda-gallery\` were modified.

## Deliverable

`C:\CODEX PG\CODEX Canonical Specs\CODEX_INSTRUCTION_PANE_UX_v2_SPEC.md`

Line count: 555

## Source Context Read

- `C:\panda-gallery\TESTING_SECTION_SPEC.md` Draft 6
- `C:\panda-gallery\GUIDED_TESTING_STYLE.md`
- `C:\panda-gallery\skills\pg-instruction-pane-author\SKILL.md`
- `C:\panda-gallery\BUGS.md` entries #135 and #136, plus related pane UX bugs
- `C:\panda-gallery\workflows\instructions_latest.json`
- `C:\panda-gallery\workflows\audit\AM_v0_smoke_checklist.html`
- `C:\panda-gallery\instruction_pane.py` read-only orientation

## What The Spec Proposes

- Treats Draft 6 as ground truth and proposes v2.1 deltas rather than rewriting the pane system.
- Adds a safe Esc dispatcher so bare Esc cannot reset/restart or silently lose answers.
- Adds `PASS_WITH_NOTE` as a step-level caveated-pass outcome, treated as pass for completion/pass-rate while preserving the note.
- Adds persistent long-run orientation: step count, remaining count, full-run outcome strip, and mid-run index/review drawer.
- Keeps `kind: "action"` but restyles it as setup/navigation, with lint pressure against overuse or foldable click-only steps.
- Adds non-blocking authoring lint warnings for unclear references, placeholder titles, compound bodies, action overuse, long runs, vague expecteds, etc.
- Adds paper-mode export to `workflows/audit/<run_id>_paper.html` as a supported fallback, with re-ingestion deferred.
- Includes backward compatibility and migration notes for existing schema v1/v2 instructions and current `ACK` action results.

## Open Questions Surfaced For Darrin

1. Should `PASS_WITH_NOTE` render as green with note marker, or amber as a caution state?
2. Should the footer button label be `PASS + NOTE`, `PASS WITH NOTE`, or `PASS, note`?
3. Should checklist items eventually support item-level `PASS_WITH_NOTE`, or is step-level note enough?
4. Should `kind: "action"` survive long-term, or should authors be pushed harder to fold setup into adjacent observation steps?
5. Should paper export be automatic on every run load, or opt-in from the pane/header/CLI?
6. Should future paper re-ingestion create structured `results_latest.json`, or is Claude reading the photographed checklist sufficient?
7. Should bare Esc on an idle step view close the pane, or remain a no-op? Codex recommends no-op.

## Notes

- The spec intentionally prioritizes data safety plus caveated pass capture before cosmetic polish.
- The new tester-report round-trip task (`20260425_142500`) has been seen and is queued next now that this prerequisite is complete.
- Harness remains paused.
- `C:\panda-gallery\` remains read-only for Codex.
