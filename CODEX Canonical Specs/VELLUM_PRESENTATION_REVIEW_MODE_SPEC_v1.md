---
spec_id: CODEX-VELLUM-PRESENTATION-REVIEW-MODE-v1
status: READY
author: CODEX
intended_assignee: CC
created: 2026-05-09
source_user_request: "Vellum needs one-key presentation mode with full-screen image, metadata panel, arrow navigation, keep/decline confirmations"
approval_boundary: CD routes to CC; Codex does not issue implementation-go or commit-go
---

# Vellum Presentation Review Mode Spec v1

## 1. Purpose

Add a one-key Vellum presentation/review mode for fast visual triage. The mode hides normal review chrome, shows the current mockup image as large as possible, preserves left/right navigation, and provides simple keyboard decisions:

- Up Arrow: keep / lock, with a required second Up Arrow confirmation.
- Down Arrow: decline, with an optional description text window and a required second Down Arrow confirmation.

This spec is for CD review and routing to CC. Codex is not authorizing implementation directly.

## 2. Current Context

Vellum already has these relevant surfaces in `workflows/design/applets/am_mockup_review.py`:

- `AMReviewWindow` as the main review window.
- `ImageCanvas` as the central image display.
- left/right arrow shortcuts for previous/next mockup navigation.
- `canvas_filename_bar`, status bar, `RatingNoteStrip`, filmstrip, palette/approval panels, and toolbar chrome.
- approval decision flow through `approval_panel` and `_on_decision_button_clicked(...)`.
- `DarkConfirmDialog` and related dialog helpers for guarded/destructive actions.

The presentation mode must reuse existing Vellum surfaces and persistence paths wherever they can represent the requested behavior without ambiguity. It must not create a parallel review system.

## 3. User Experience

### Entry and Exit

Use `F11` as the required one-key toggle for Presentation Review Mode.

Rationale:

- It is a standard full-screen key on Windows.
- It does not collide with the existing Vellum single-letter tool shortcuts such as `P`, `F`, `Q`, `N`, or `Space`.
- It satisfies the "one key press" requirement.

Behavior:

- Press `F11` from normal Vellum review mode: enter presentation mode immediately.
- Press `F11` again: exit presentation mode and restore the prior window state and visible panels.
- Press `Esc`: exit presentation mode unless a keep/decline confirmation is pending; if confirmation is pending, `Esc` cancels the pending decision first.

### Presentation Layout

When presentation mode is active:

- The image fills the screen or available full-screen window area.
- Normal Vellum chrome is hidden:
  - toolbar;
  - palette rail;
  - approval/right panel;
  - filmstrip;
  - rating/note strip;
  - status bar;
  - standard filename bar.
- The canvas uses fit-to-view behavior after each image load or navigation.
- Markup overlays must be hidden by default while presentation mode is active so the screen shows the image cleanly. CC must save the prior markup visibility state on entry and restore it on exit.
- A floating metadata panel remains visible over the image.

### Floating Metadata Panel

A compact floating panel must show key context while preserving the image-first view.

Required fields:

- filename;
- image index and total count, such as `12 / 48`;
- date if available from packet metadata;
- fallback date from file modified time if packet date is unavailable;
- current decision state if one exists;
- optional note/decline summary if one exists, truncated cleanly.

Panel rules:

- It floats over the image, preferably top-left or bottom-left.
- It must not cover the center of the image.
- It must be readable on light or dark images. Use a restrained translucent dark panel with high-contrast text.
- It must auto-resize within screen bounds and elide long filenames rather than overflow.
- It remains visible during normal navigation and pending decision states.

## 4. Keyboard Behavior

### Navigation

In presentation mode:

- Right Arrow moves to the next image.
- Left Arrow moves to the previous image.
- Home and End must continue to work in presentation mode if they are already wired in normal mode; this spec does not require adding new Home/End behavior if it does not already exist.
- Navigation must cancel any pending keep/decline confirmation before changing images.
- Navigation must update the floating metadata panel immediately.

### Up Arrow: Keep / Lock

Up Arrow is a two-press confirmation flow.

First Up Arrow:

- Does not write a decision.
- Enters a pending keep state for the current image.
- Shows a very prominent up-arrow confirmation overlay.
- Overlay text must be short: `Press Up again to KEEP / LOCK`.
- Floating metadata panel remains visible.
- `Esc`, Left Arrow, Right Arrow, Down Arrow, or a 5-second timeout cancels the pending keep state.

Second Up Arrow while pending keep:

- Writes the keep/lock decision through the existing Vellum decision/persistence path.
- Shows a short success overlay, such as `KEPT / LOCKED`.
- Does not auto-advance in v1. Auto-advance is out of scope unless CD explicitly amends this spec.

Decision mapping:

- Default mapping is `DecisionStatus.APPROVED_DIRECTION` or the current equivalent approval enum used by `_on_decision_button_clicked(...)`.
- CC must verify the exact enum/status name at Step 0. If `APPROVED_DIRECTION` is not the correct keep/lock value, CC must file an RTC to CD with mapping options before implementing this part.

### Down Arrow: Decline With Optional Description

Down Arrow is also a two-press confirmation flow, but first press opens an optional description window.

First Down Arrow:

- Does not write a decision.
- Opens a focused decline description panel/dialog.
- The panel must show a very prominent down-arrow symbol.
- The panel contains an optional multi-line text field.
- Text hint: `Optional reason for decline`.
- It shows the instruction: `Press Down again to DECLINE`.
- `Esc` cancels decline without writing.

Typing behavior:

- While the decline description field is focused, normal text entry must work.
- The Down Arrow key must still confirm decline when the decline panel is open. If the text field consumes Down Arrow by default, CC must intercept it at the dialog/window level for this mode.
- Enter must insert a newline or be inert, not confirm by accident.
- Ctrl+Enter is not required for v1 and must not be the only confirmation path.

Second Down Arrow while decline panel is open:

- Writes the decline decision through the existing Vellum decision/persistence path.
- Persists the optional description as the decision note or decline note using the existing packet/handoff note route identified at Step 0.
- Shows a short success overlay, such as `DECLINED`.
- Closes the decline panel.
- Does not auto-advance in v1.

Decision mapping:

- Default mapping is `DecisionStatus.REJECTED` or the current equivalent rejected/declined enum used by `_on_decision_button_clicked(...)`.
- CC must verify the exact enum/status name at Step 0. If `REJECTED` is not the correct declined value, CC must file an RTC to CD with mapping options before implementing this part.

## 5. Visual Design Requirements

Presentation mode must feel like a focused image review surface, not a separate app.

Required visual elements:

- full-screen image view;
- floating metadata panel;
- pending keep overlay with a large up-arrow symbol;
- pending decline overlay/panel with a large down-arrow symbol and optional text field;
- subtle success overlay after confirmation.

Design rules:

- No decorative cards, gradients, or extra explanatory UI.
- Use clear symbols for arrows. The up/down confirmation symbols must be visually dominant.
- Do not make the metadata panel compete with the image.
- Do not hide the cursor permanently in v1.
- Keep all text inside its container at common Windows display scales, including HiDPI.

Suggested default placement:

- metadata panel: top-left, 16 px from screen edge;
- pending keep overlay: centered near top third, large up arrow above text;
- decline panel: centered, with large down arrow at top, text box below, concise confirm/cancel footer.

## 6. State and Persistence

Presentation mode must not create a second source of truth.

- Decisions must use the existing Vellum approval decision persistence path.
- Optional decline description must use the existing note/handoff mechanism identified at Step 0.
- Existing approval panel state must refresh after exiting presentation mode.
- Existing rating/note state must remain intact.
- Pending confirmation state is volatile and must not survive navigation, exit, or app restart.

If current Vellum decision APIs cannot record `keep/locked` and `declined` semantics without ambiguity, CC must stop at Step 0 and ask CD for the mapping before implementation.

## 7. Step 0 Requirements for CC

Before implementation, CC must file a Step 0 RTC to CD with:

1. Shortcut collision audit:
   - confirm `F11`, Up Arrow, Down Arrow, Left Arrow, Right Arrow, and `Esc` behavior in normal Vellum mode;
   - list any current shortcuts or widget handlers that would conflict.
2. Decision mapping:
   - identify exact status enum/value for keep/locked;
   - identify exact status enum/value for declined;
   - identify the exact persistence location for optional decline text.
3. UI ownership plan:
   - list which widgets will be hidden/restored;
   - identify whether implementation uses `showFullScreen()` or a maximized borderless fallback;
   - identify how previous window state and panel visibility will be restored.
4. Text-field key handling plan:
   - explain how second Down Arrow confirms decline while the optional description field is focused.
5. Test plan:
   - list smoke or manual checks that will prove no real mailbox/send path is touched.

Do not begin implementation until CD clears Step 0.

## 8. Implementation Guidance

Likely implementation touch points:

- `AMReviewWindow`:
  - add presentation mode state;
  - add `F11` shortcut;
  - hide/restore chrome widgets;
  - route arrow key presentation decisions;
  - update metadata panel;
  - call existing decision persistence.
- `ImageCanvas`:
  - ensure clean-image fit-to-view after entering mode and after navigation;
  - avoid breaking existing zoom, saved markup data, and DPR behavior.
- New small helper widgets inside `am_mockup_review.py` are acceptable if local style follows existing QSS helper patterns:
  - presentation metadata panel;
  - keep confirmation overlay;
  - decline confirmation panel/dialog.

Do not alter unrelated Vellum tool behavior, existing Space flip-swap behavior, or middle-click pan behavior.

## 9. Acceptance Criteria

Functional:

- `F11` enters presentation mode with one key press.
- `F11` exits presentation mode and restores prior Vellum layout.
- `Esc` exits presentation mode or cancels the current pending decision.
- In presentation mode, the image fills the screen and Vellum chrome is hidden.
- Floating metadata panel shows filename, index/total, date/fallback date, and decision/note context.
- Markup overlays are hidden on presentation entry and the previous markup visibility state is restored on exit.
- Left and Right Arrow navigation still works.
- Left/Right navigation cancels pending keep/decline confirmation safely.
- First Up Arrow shows a prominent pending keep/lock confirmation overlay and writes nothing.
- Second Up Arrow confirms keep/lock through the approved-direction decision route verified at Step 0.
- First Down Arrow opens optional decline description UI and writes nothing.
- Second Down Arrow confirms declined through the rejected/declined decision route verified at Step 0 and persists the optional description.
- `Esc` cancels pending Up/Down state without writing.
- Exiting presentation mode refreshes normal Vellum panels to reflect decisions made in presentation mode.

Safety:

- No real mailbox dispatches or send routes are touched by presentation decisions.
- No patient data assumptions are introduced.
- No existing decision shortcuts regress.
- Existing `Space` flip-swap and middle-click pan behavior remains unchanged.
- Existing v5.1.0 DPR fixes remain intact.

Visual:

- Metadata panel is readable and does not cover the center of the image.
- Up/down confirmation symbols are visually prominent.
- Decline text window is large enough for a useful optional note.
- UI works at Windows HiDPI scale without clipped text.

## 10. Validation Requirements

Required validation before READY-FOR-REVIEW:

1. Unit or smoke coverage for entering/exiting presentation mode state.
2. Manual or automated check that hidden widgets and prior markup visibility restore correctly.
3. Manual or automated check for Left/Right navigation in presentation mode.
4. Manual or automated check that first Up writes nothing and second Up writes keep/lock.
5. Manual or automated check that first Down writes nothing and second Down writes declined with optional text.
6. Regression check that normal mode shortcuts still work after exiting.
7. Vellum smoke test remains clean at the current expected count.
8. BA Vellum summary has 0 hard-fails.
9. HiDPI visual pass on Darrin's display or explicit DEFERRED-TO-HANDS-ON note for metadata/overlay readability.

If any check requires live Windows visual confirmation, mark it `DEFERRED-TO-HANDS-ON` in the CC READY-FOR-REVIEW report with exact instructions for Darrin.

## 11. Non-Goals

- No redesign of the normal Vellum review layout.
- No change to Space flip-swap design ruling.
- No new send/export/mailbox route.
- No automatic image export.
- No requirement to auto-advance after keep/decline in v1.
- No separate secondary clean-image mode beyond presentation mode hiding markup overlays by default.

## 12. Recommended Scheduling

This spec must not interrupt active Vellum v5.2.0 work unless CD explicitly chooses to merge it into that lane. Recommended default:

- park this as a post-v5.2.0 Vellum enhancement;
- route to CC after v5.2.0 validation and Darrin hands-on testing clear;
- require Step 0 before implementation because decision mapping and Down Arrow text handling need confirmation.

## 13. Self-Review Log

- Pass 1: 7 issues fixed — changed status to READY; made clean-image markup hiding explicit; hardened decision mappings to approved-direction/rejected defaults with Step 0 verification; added 5-second pending confirmation timeout; removed soft should-language from core requirements; clarified decline-note persistence; aligned non-goals with presentation mode hiding markup overlays.
- Pass 2: 4 issues fixed — clarified Home/End carry-through behavior; added explicit markup hide/restore acceptance criterion; expanded validation to cover markup visibility restoration; hardened scheduling language so the spec does not interrupt v5.2.0 unless CD chooses it.
- Pass 3: 1 issue fixed — hardened Step 0 decline-text persistence from advisory wording to an exact required persistence-location finding.
- Pass 4: 0 significant issues fixed — no remaining errors, omissions, inconsistencies, or blocking ambiguities found.

