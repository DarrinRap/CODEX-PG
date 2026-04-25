# TASK: Instruction Pane UX v2 Spec

Generated: 2026-04-25 12:55:00 -07:00
From: Claude
To: Codex
Status: Response Requested (deliverable: spec doc)
Recommended tier: Extra-High

## Summary

Author a spec proposing concrete UX revisions to the Panda Gallery Instruction Pane (`instruction_pane.py`, schema in `TESTING_SECTION_SPEC.md`) to address pain surfaced today during real use. The pane is currently the only manual-test venue for PG, and today's AM v0 polish smoke proved it's blocking — Darrin abandoned the pane mid-run and reverted to pen-and-paper. Two concrete bugs were filed (#135 Esc resets progress, #136 no PASS-with-note path), but the underlying ask is a coherent UX spec, not three patches.

## Background — what just happened

Claude authored a 15-step pane plan (`workflows/instructions_latest.json`) for the AM v0 polish smoke. Darrin started the run, hit several frictions, and reported back:

> "I didnt check everything. too many tests and no way to make notes on pass but were errors like background text were wrong. why are there just click questions? also bug - pressing esc can force questionnaire to restart. also many questions unclear like what is table B?"

Then, after we filed the bugs:

> "the INSTRUCTION system is super clunky. Work with CODEX on UX enhancements"

Darrin built a paper checklist as a workaround (`C:\panda-gallery\workflows\audit\AM_v0_smoke_checklist.html`) and is using that for the immediate AM smoke. The pane needs to be good enough to displace paper.

## What the spec should diagnose

Real failure modes from today, in priority order:

1. **Esc resets the entire run** — Mid-run Esc returned the pane to step 1, discarding all prior PASS/FAIL answers with no confirmation. Filed as bug #135. Likely a `keyPressEvent` that hits a reset path on `Qt.Key_Escape` without checking inline-panel state.

2. **No "PASS with note" affordance** — When a step broadly passes but has a small caveat (e.g. layout right but a label color is wrong), the tester has only PASS or FAIL. FAIL contaminates pass-rate metrics; PASS loses the observation. Filed as bug #136. Today's only workaround was hitting FAIL with explanatory text, which marked otherwise-working steps as broken.

3. **Long runs are unworkable** — 15 steps was too many. Steps lack a way to skim ahead, jump back without losing context, or get a summary view of "what have I done so far / how many left." Tester loses track and abandons.

4. **Action-only steps feel like noise** — `kind: "action"` steps with one "Got it" button broke flow; tester wondered why they existed at all. Either action steps need to be more clearly differentiated, or they should be foldable into adjacent steps' bodies, or the kind itself should be reconsidered.

5. **Authoring tolerance is loose** — Bad authoring (Claude copied "B1 — Menu open F12" from the spec template into AM tests where there's no Table B) reaches the tester unchecked. The pane has no way to surface "this step makes no sense" feedback short of FAIL.

6. **Paper alternative was needed** — The fact that a paper checklist became the working venue is itself signal. The pane needs an export path: render the current `instructions_latest.json` as a printable single-page HTML that can be filled in with pen and photographed back. Then results can be re-ingested OR Claude can read the photo directly. (See "Paper-mode export" below.)

## Suggested spec scope

Codex to scope and decide structure, but Claude expects:

1. **Diagnosis section** — name the failures, ground in today's evidence and prior spec history (the spec is on Draft 6; what's working, what isn't).

2. **Esc handling** — single dispatcher that checks inline-panel state before falling through to any reset behavior. Reset, if it stays as a feature, requires DarkConfirmDialog confirmation. Update spec §5.4 keyboard map.

3. **Outcome model extension** — add `PASS_WITH_NOTE` to the outcome enum. Per-step at the footer (not per-checklist-item). Renders as a third button or a quiet "+ note" affordance next to PASS — Codex to recommend. Schema impact in §7. Treat as PASS for advance / dot-strip / pass-rate purposes; expose `note` field in the same shape as FAIL detail.

4. **Long-run navigation** — review-all screen exists per §5.7 but tester can't reach it mid-run. Propose a way to: see where you are, jump to any step (without losing answers), see a "remaining" count. Could be a header dot strip, a slide-out index, or a compact "step N of M with green/red/grey dots" persistent header.

5. **Action step kind** — keep, kill, or restyle? Today's smoke had three action steps that all could've been folded into adjacent body text. If kept, they need a stronger visual signal that they're informational, not gating. If killed, migration path for existing v2 files using them.

6. **Authoring guardrails** — what can the loader catch that today it doesn't? Examples to consider: titles that look like template placeholders ("B1 — ...", "Step N — ..."), checklists with items that read as sequential actions, expecteds that paraphrase rather than quote, bodies with "and" joining two imperatives. Doesn't have to be enforced rejection — could be lint-style warnings surfaced in the About panel.

7. **Paper-mode export** — generate `workflows/audit/<run_id>_paper.html` from the current instructions file. Print-styled, ☐ checkboxes per item, PASS/FAIL pair per step, notes column. Tester prints, fills in, photographs, sends to Claude. Could be a button in the pane header, or a CLI flag. Re-ingestion is optional (Claude can read the photo as image input); the export is the must-have.

8. **Open questions** — surface explicitly per Codex protocol. Examples: should `PASS_WITH_NOTE` show a different dot color in the strip (amber)? Should the action step kind survive at all, or is it an authoring error every time? Should paper-mode be an automatic dual-output every time the pane loads a file, or opt-in?

## Constraints

- **Repo is read-only for Codex.** Output to `C:\CODEX PG\CODEX Canonical Specs\CODEX_INSTRUCTION_PANE_UX_v2_SPEC.md`. No edits to `panda-gallery\TESTING_SECTION_SPEC.md` directly — propose changes by section, Claude/CC will land them.
- **Don't rewrite the whole spec.** TESTING_SECTION_SPEC.md is on Draft 6 and contains a lot of working architecture (MCP passive-read, results auto-archive, schema v2 XOR enforcement). Treat that as ground truth and propose deltas.
- **Migration story required.** Existing v2 instructions files in `workflows/` and any pane-extension bugs (#90 etc.) must continue to load. If a schema change breaks them, propose a v2.1 with backward compat.
- **Visual proposals welcome but not required.** If Codex wants to mock up a header dot strip or PASS-with-note button placement in HTML/CSS, that's useful but optional. Words first.

## Inputs Codex should read first

- `C:\panda-gallery\TESTING_SECTION_SPEC.md` (Draft 6, the canonical pane spec)
- `C:\panda-gallery\GUIDED_TESTING_STYLE.md` (decision principles, CAN/CAN'T matrix)
- `C:\panda-gallery\skills\pg-instruction-pane-author\SKILL.md` (current authoring rules — the post-#87 format Claude is supposed to follow)
- `C:\panda-gallery\BUGS.md` entries #135 and #136 (filed today; Claude is writing them now in parallel — may not be in BUGS.md at the moment Codex starts but will be by the time spec lands)
- `C:\panda-gallery\workflows\instructions_latest.json` (today's offending 15-step plan, kept as evidence)
- `C:\panda-gallery\workflows\audit\AM_v0_smoke_checklist.html` (the paper workaround Darrin actually used)

## Approval Boundary

Spec authoring only. No implementation. Output stays in `C:\CODEX PG\`. Claude reviews the spec before it's surfaced to Darrin for `go` per generator+critic pattern. Implementation, if approved, will be a separate CC dispatch citing this spec.

— Claude
