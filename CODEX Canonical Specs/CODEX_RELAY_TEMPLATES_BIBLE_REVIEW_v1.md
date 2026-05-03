# CODEX Relay Templates Bible Review v1

Generated: 2026-05-03
Reviewer: CODEX
Scope: Read-only Bible compliance review of Relay Templates redesign spec and mockups
Input spec: C:\panda-gallery\workflows\cc_mailbox\CC Inbox\20260503_050000_CLAUDE_to_CC_relay_templates_redesign_spec.md
Mockups:
- C:\panda-gallery\workflows\design\pg_general_mockups\relay_templates_redesign_v1.html
- C:\panda-gallery\workflows\design\pg_general_mockups\relay_templates_redesign_v2_with_guidance.html
Bible: C:\panda-gallery\workflows\design\PG_DESIGN_BIBLE_v1.md

## 1. Executive Summary

The Relay Templates redesign spec is directionally strong and solves the right UX problems, but it is not ready for direct implementation as a definitive CC task without amendment. The large layout, dead-control repairs, primary action rationale, placeholder-chip grammar, and feedback additions are mostly Bible-aligned. However, the spec has action-level conflicts around color-token discipline, a mode-zone color misuse, canonical mockup mismatch, Pattern 23 encoding safety, and acceptance criteria gaps. Recommended verdict: revise the spec before implementation; CC can use this review as Step 0 context, but should not treat the current spec as clean authority.

## 2. Confirmed Items

- Two-panel layout: The 240px left template list plus 1fr editor is compatible with PG dense tool surfaces and the Bible preference for scannable operational panels over card-heavy layouts.
- Guidance bar: A narrow operational guidance strip earns presence under Bible sections 1.4 and 1.5 because it explains the relationship between templates and report dispatch, which is otherwise not obvious.
- One primary button: The `Save changes` primary button is acceptable under the R13 single-primary rule because Templates and Compose are mutually exclusive pages in the Relay Developer Hub stack.
- Dead controls: Converting `Use`, `Reset`, `Discard`, placeholder chips, and `+ New template` into real `QPushButton` controls is Bible-aligned. It fixes action affordance and enables hover/pressed/disabled feedback.
- Tertiary reset treatment: A borderless link-style reset button is allowed by Bible section 6.12 as a tertiary inline action, provided disabled state and tooltip/fallback feedback are clear.
- Placeholder chips: 12px-radius chip controls with accent hover are consistent with Bible section 6.14 when treated as chip micro-actions rather than primary actions. They must not visually compete with the primary save button.
- Section heads: The target 11px, 700 weight, 1.2px letter spacing, accent, all-caps section heading matches Bible section 3.3. In Qt, the label text itself must be uppercase because QLabel/QSS cannot reliably apply CSS `text-transform`.
- StatusPill base shape: The implementation note to keep status pills at 999px radius is compliant with Bible section 6.24. The canonical mockup does not yet match this; see Flag 4.
- Feedback additions: Char count, last-edited timestamp, dirty row dot, dirty save state, and post-action enable/disable changes are the right category of feedback for the frequent wiring/regression issues Darrin has reported.
- Hover requirements: The spec correctly calls out explicit hover rules for every new QPushButton family, including placeholder chips.

## 3. Flags Requiring Action

### FLAG 1

SECTION: Status pill color table / `need_more_info`

ITEM: Proposed `need_more_info` pill uses Review teal via `RELAY_COLOR_MODE_REVIEW` or raw `#5fa0a8`.

PROBLEM: Bible section 2.6 says mode-zone colors appear in two places only: active module-tab underline and status-bar mode label. Other UI must not pick up mode colors. Section 6.24 also explicitly says no `--info`, `--info-soft`, or `--info-border` status color exists. Using Review teal for a Relay template status pill violates both rules unless the Bible creates an approved semantic alias for this exact use.

SUGGESTED FIX: Remove `need_more_info` from this implementation, or map it to an existing Bible status row. If it must exist, ask CD for an explicit Bible amendment defining a non-mode semantic status token before implementation.

### FLAG 2

SECTION: Scope / token source of truth

ITEM: `RELAY_COLOR_MODE_REVIEW` fallback or styles.py addition.

PROBLEM: The spec says the implementation is limited to `relay/developer_hub.py`, `relay/hub_components.py`, and tests, but also allows adding `RELAY_COLOR_MODE_REVIEW` to `styles.py` if clean. That is a scope conflict. It is also downstream of Flag 1, where the token itself appears inappropriate for a status pill.

SUGGESTED FIX: Delete the `RELAY_COLOR_MODE_REVIEW` addition path if `need_more_info` is removed. If CD keeps the status, explicitly authorize `styles.py` and the Bible amendment in the dispatch.

### FLAG 3

SECTION: Border token discipline

ITEM: `RELAY_COLOR_BORDER_SOFT` use for guidance divider, splitter handle, disabled borders, and status pills.

PROBLEM: The Bible defines `--border-soft` as `#232336`, but the current runtime constant `PG_COLOR_BORDER_SOFT` / `RELAY_COLOR_BORDER_SOFT` is `#2a2a4e`, which is the pane-selected color. The v2 mockup uses `#232336`, while the implementation spec uses the existing constant. That means a visually compliant mockup can become a stronger, wrong divider in Qt.

SUGGESTED FIX: Decide token authority before implementation. Best fix is to correct the shared `PG_COLOR_BORDER_SOFT` value to the Bible value under a separate authorized styles.py task, then use `RELAY_COLOR_BORDER_SOFT` normally. If styles.py is out of scope, the spec must acknowledge that the Qt result will not match the canonical mockup/Bible value.

### FLAG 4

SECTION: Canonical mockup v2 / status pill shape

ITEM: `.pill { border-radius: 10px; }` in the v2 mockup.

PROBLEM: Bible section 6.24 requires pills to use radius 12px or 999px. The implementation spec says StatusPill uses 999px, but the canonical visual reference still shows 10px pills. That creates a spec/mockup conflict.

SUGGESTED FIX: Update the canonical v2 mockup to 12px minimum, preferably 999px for status pills, or add an explicit note that the mockup pill radius is illustrative and the Qt StatusPill implementation wins.

### FLAG 5

SECTION: Duplicate status semantics

ITEM: New `duplicate` pill uses neutral acknowledged-style colors: pane-raised, border, text-muted.

PROBLEM: Bible section 6.24 gives separate neutral rows for Acknowledged and Won't Fix / Closed. A duplicate report is normally terminal/closed, not merely acknowledged. The current spec does not explain why duplicate should inherit acknowledged text-muted instead of closed text-dim.

SUGGESTED FIX: If duplicate is terminal, use the Closed row: `RELAY_COLOR_PANE_RAISED`, `RELAY_COLOR_BORDER_SOFT`, `RELAY_COLOR_TEXT_DIM`. If duplicate is an informational nonterminal state, document that explicitly.

### FLAG 6

SECTION: Pattern 23 / encoding safety

ITEM: Spec contains direct non-ASCII characters: section sign, north-east arrow, pencil, and diamond.

PROBLEM: The spec correctly warns about Pattern 23 and says to use unicode escapes for template strings, but the spec itself still contains 27 direct non-ASCII characters: 19 section signs, 4 north-east arrows, 3 pencil glyphs, and 1 diamond. If CC copies snippets through an unsafe write path, this can reintroduce mojibake.

SUGGESTED FIX: Replace implementation-adjacent glyphs with ASCII text or escape forms. Use `section` instead of the section sign in comments, `\u2197` if the Use arrow is kept, remove the Edit pencil because Edit is deleted, and use `\u2756` consistently for the Send update diamond in code strings.

### FLAG 7

SECTION: Duplicate migration

ITEM: `_migrate_duplicate_template_status` matches `name.startswith("Duplicate")`.

PROBLEM: This can incorrectly migrate user-created templates whose names begin with `Duplicate` but are not factory duplicate templates. The spec also does not define behavior for corrupted JSON, partially migrated data, or preserving user data when seeding defaults after a parse failure.

SUGGESTED FIX: Match only known factory duplicate template identities, preferably by exact factory names plus old status, or introduce a schema/version marker. Add tests for user-created `Duplicate custom...`, corrupted JSON, already-migrated data, and mixed old/new template lists.

### FLAG 8

SECTION: Disabled controls / feedback

ITEM: Disabled `Use`, `Reset`, `Discard`, and hover/disabled states rely mainly on QToolTip and QSS.

PROBLEM: Bible section 1.6 requires disabled controls to answer "why not?" with tooltip or adjacent status. Disabled QPushButton tooltips can be platform-dependent in Qt, and the reset button's enabled default text color and disabled color are both effectively dim, making the disabled state weak.

SUGGESTED FIX: Add an adjacent one-line status or footer microcopy for the current disabled reason, or explicitly verify disabled tooltips in Qt tests/manual checks. Make reset's enabled state distinguishable from disabled through hover, focus, or an adjacent status line.

### FLAG 9

SECTION: Canonical mockup v2 / `Use` button state

ITEM: The v2 mockup shows `Use` enabled even though the page context does not show a selected report.

PROBLEM: The spec says `Use` must be disabled when no report is selected. The canonical mockup therefore depicts either an unstated selected-report state or a contradictory enabled state.

SUGGESTED FIX: Amend the mockup/spec caption to say a report is selected, or provide a no-report mockup state with `Use` disabled and visible reason feedback.

### FLAG 10

SECTION: Acceptance criteria coverage

ITEM: Several defects have no direct AC or only indirect coverage.

PROBLEM: DEFECT-T13 last-edited timestamp, DEFECT-T18 divider, Pattern 23 scan, migration edge cases, disabled tooltip behavior, and full button feedback are not sufficiently pinned by acceptance criteria. The spec's checklist mentions hover rules, but the AC table should make them testable and nonoptional.

SUGGESTED FIX: Add explicit AC rows for last-edited timestamp, divider presence and token, Pattern 23 zero-direct-glyph scan for implementation files, migration edge cases, disabled reason feedback, and action-button feedback after activation.

## 4. Gaps / Questions For CD Before CC Implements

1. Should `need_more_info` exist at all for Relay templates, or should templates stay limited to the Bible section 6.24 status set?
2. If `need_more_info` exists, is CD authorizing a Bible amendment for a new semantic status token, or should it reuse an existing non-mode status color?
3. Is styles.py in scope for this task to correct `PG_COLOR_BORDER_SOFT` to the Bible value `#232336`, or must CC avoid shared token edits?
4. Is `duplicate` semantically terminal/closed or merely acknowledged? This determines whether it should use `text-dim` or `text-muted`.
5. Should dirty state be shown inside the primary button text as `Save changes *`, or should dirty state stay adjacent to controls via row dot, footer text, and button border/fill changes?
6. What is the required behavior if saved template JSON is corrupted: preserve and warn, reset to defaults, or backup then reset?
7. Should the canonical mockup include both selected-report and no-report states so `Use` disabled behavior is unambiguous?

## 5. Pattern 23 Scan Result

Verdict: Not clean.

The implementation guidance in the spec is partially correct: default template body strings should use ASCII hyphens and unicode escapes for intentional symbols. However, the spec file itself contains direct non-ASCII glyphs in implementation-adjacent prose and snippets:

- `section sign` U+00A7: 19 occurrences
- `north-east arrow` U+2197: 4 occurrences
- `pencil` U+270E: 3 occurrences
- `diamond` U+2726: 1 occurrence

Recommended Pattern 23 rule for this dispatch: CC should avoid copying any direct glyph from the spec into Python source. All user-visible glyphs in Python strings should be escaped (`\u2197`, `\u2756`) or replaced with ASCII text. The final implementation verification should include a targeted non-ASCII scan of edited Python files and template JSON seeds.

## 6. Bottom Line

Flag count: 10
Gap/question count: 7

The redesign is close in UX architecture but not yet Bible-definitive. The highest-priority fixes are: remove or formally authorize the Review-teal `need_more_info` status, resolve `border-soft` token authority, clean Pattern 23 risk, tighten duplicate migration, and add acceptance criteria for feedback/regression-sensitive behavior.