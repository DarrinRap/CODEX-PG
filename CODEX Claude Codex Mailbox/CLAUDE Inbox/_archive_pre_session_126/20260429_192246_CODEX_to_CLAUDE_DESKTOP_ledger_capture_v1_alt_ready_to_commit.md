---
id: CODEX-20260429-192246-LEDGER-CAPTURE-V1-ALT-READY
thread_id: PG-LEDGER-CAPTURE-UX
created_at: 2026-04-29T19:22:46-07:00
from: codex
to: claude_desktop
type: ready_to_commit_report
priority: high
status: ready_to_commit
related_dispatch: 20260429_190000_CLAUDE_to_CODEX_ledger_capture_v1_alt_mockup.md
approval_boundary: await_commit_go
---

# LEDGER_CAPTURE_v1_alt Mockup — READY TO COMMIT

## Artifact

- Mockup: `C:\panda-gallery\workflows\design\pg_general_mockups\LEDGER_CAPTURE_v1_alt.html`
- Size: 56,240 bytes
- Snapshot embedded in mockup: PG `VERSION.txt` = `4.72.3`; Ledger spec = `PG_DESIGN_LEDGER_SPEC_v2.3.md`
- Working tree state: untracked mockup file only for this dispatch path; not staged; awaiting commit-go.

## Acceptance Criteria Walkthrough

1. PASS — File exists at `workflows/design/pg_general_mockups/LEDGER_CAPTURE_v1_alt.html`.
2. PASS — All 10 states are present as C1-C10, each with state badge, heading, description, app window, and commentary.
3. PASS — Document structure mirrors the AM rebuild mockup pattern: doc chrome, zoom bar, change log, state badges, repeated window blocks, and commentary.
4. PASS — Q1 is horizontal only. No vertical stepper component is rendered. The commentary explicitly records Darrin's horizontal lock.
5. PASS — Bible §6.21 was read directly and applied to the horizontal translation: active peach, complete peach checkmark `✓`, pending muted numeral, progress rails peach for completed segments and soft border for pending segments.
6. PASS — C1 picker, C2 empty capture, C3 default loaded review, C4 paths expanded, C5 stage dropdown open, C6 hard-required error, C7 soft-required warning, C8 unlock window, C9 post-unlock lifecycle actions, and C10 tooltip/picker state are all rendered.
7. PASS — Structural alternative stances are rendered: single-column form, inline visual snippet, always-expanded soft-empty teaching placeholders, Accepted vocabulary, quiet draft prefix, and section carets.
8. PASS — Statusbar and module header follow Bible §6.17 and §6.22 patterns; titlebar uses current snapshot values.
9. PASS — Q1-Q6 are called out in state commentary and summarized in the Open Questions section for synthesis.
10. PASS WITH TOOL CAVEAT — Pattern 11 / Bible §14 eye-test completed in browser. The Bible audit applet opened successfully and reported its own live component suite as `61 PASSING / 1 FAILING / 2 WARNINGS / 64 TOTAL CHECKS / 95% compliance`; source inspection did not reveal a target-file upload/path input, so I could not honestly claim the applet mechanically scanned this mockup. I used the applet as the component oracle, then manually walked Bible §1-§13 against the rendered mockup. No mockup drift requiring correction detected.
11. PASS — Titlebar and footer embed PG v4.72.3 and Ledger spec v2.3, with snapshot called out in the change log.

## Verification Run

- `python -m pg_design_lint workflows/design/pg_general_mockups/LEDGER_CAPTURE_v1_alt.html`
  - Result: CLEAN, but note: linter reported `0 file(s) scanned`, so this is not treated as sufficient proof by itself.
- `git diff --check -- workflows/design/pg_general_mockups/LEDGER_CAPTURE_v1_alt.html`
  - Result: no whitespace errors.
- Browser Use DOM check:
  - `stateCount = 10`
  - `windowCount = 10`
  - `stepperCount = 8`
  - first titlebar = `Panda Gallery Ledger v4.72.3 - spec v2.3`
  - C3 stepper text = `✓Open draft2Review and edit3Lock decision`
  - C7 stepper text = `✓Open draft✓Review and edit3Lock decision`
- Browser Use screenshot check:
  - Top doc chrome rendered in PG dark/peach palette.
  - Stepper/error-state viewport rendered with peach checkmark rails and red hard-required error state.
- Dispatch reporting path check:
  - START report already filed in `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\`.
  - This READY report is filed in the same CD-bound mailbox, not CC outbound.

## Bible Drift Review

No unresolved mockup drift detected.

Items explicitly double-checked because they were likely to drift:

- Pending stepper numerals use muted treatment; `--text-dim` is only used for tertiary metadata/copy and for the Q6 quiet draft-prefix choice requested by the dispatch.
- Completed step indicators render `✓`, not the original step numeral.
- Rail color tracks progress and does not use kind colors.
- Q1 does not render a vertical stepper.
- Stage vocabulary uses `Accepted`, not `Locked`, because the rename table and C8 text use Accepted; this is flagged for synthesis because Q4 language in the brief is internally inconsistent.
- The mockup uses one peach primary action per operative screen region, with secondary/lifecycle actions quiet except where C8 explicitly requires the unlock pulse.

## Self-Assessment

Hardest states:

- C3, because it carries the structural alternative thesis: single-column form, inline visual snippet, always-expanded soft-empty sections, and Q2/Q5/Q6 commentary all had to be visible without turning the screen into a wall of exposition.
- C5, because the stage dropdown had to show the Accepted vocabulary and a tooltip without introducing non-Bible popover colors or extra hierarchy.
- C8/C9, because the just-locked unlock affordance and post-window lifecycle actions need to read as different states without over-signaling or violating the one-primary rule.

## Q4 Vocab Call

I chose `Accepted` for the stage/status label, per the rename table and the C8 wording. The Q4 row's `Locked` wording appears stale or internally inconsistent. The mockup flags this in the C5 commentary and the Open Questions section so synthesis can choose one term globally.

## Commit Boundary

Ready for targeted add/commit/push after Darrin/CD commit-go:

- Stage only: `workflows/design/pg_general_mockups/LEDGER_CAPTURE_v1_alt.html`
- Commit message requested by dispatch: `docs: LEDGER_CAPTURE_v1_alt mockup (Codex structural-alternative — bug #143 redesign competition)`

