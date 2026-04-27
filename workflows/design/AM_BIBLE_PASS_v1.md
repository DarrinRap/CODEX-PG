# AM_BIBLE_PASS_v1

Date: 2026-04-26
Author: Codex
Scope: Audit Module Bible compliance pass for Screen A, Screen B, Archive, and AM shell
Write location: `C:\CODEX PG\workflows\design\AM_BIBLE_PASS_v1.md`
Reference code is read-only: `C:\panda-gallery`

## Summary

The Audit Module has already absorbed several v4.42.x improvements: Screen A now has a one-row module header, a left summary pane, compact table columns, an empty-state stack, and a canonical bottom status bar. The remaining Bible risks are concentrated in four places: the workflow stepper implementation still uses the old 8px rail despite the Bible now requiring 22px; Screen A still lets the bottom status bar mirror queue counts owned by the Inbox StatusPane; Screen B still carries the pre-redesign right-column structure from bug #140; and the AM window shell still uses hardcoded size/minimum geometry rather than the shared Section 13 helper that Darrin already selected.

The correct AM direction is not another prose patch. AM should use the same strict module grammar everywhere: one-row module screen headers, no descriptive subtitle under headers, source/freshness in the bottom bar, queue/workflow state in the left or right status surfaces, and visible actions only when they apply to the current bug state. Screen B needs the most structural work: convert the triage assistant from a long mixed column into a compact triage rail with a single StatusPane, a verdict/state card, conditional action blocks, and no mock-provider filler.

This pass assumes the current Bible is authoritative, including Section 1.4, 1.5, 1.6, 6.13, 6.21, 6.22, 7, 8, and 13. It also folds in Darrin's AM amendment: align with PG navigation, add ESC as Back where Back exists, add restrained activity indicators for operations over 500ms, and audit colors against Section 2.

## Part A - AM Compliance Audit

### AM Shell - `AuditModuleWindow`

Evidence:

- `audit_module_window.py:2789` declares `AuditModuleWindow(QMainWindow)`.
- `audit_module_window.py:2798` calls `self.resize(800, 560)`.
- `audit_module_window.py:2802` calls `self.setMinimumSize(800, 500)`.
- `audit_module_window.py:2828-2829` wires detail/archive Back signals.
- `audit_module_window.py:2858-2867` returns to Screen A by reloading list and switching the stack.

Violations:

- High, Section 13: hardcoded default and minimum sizes remain. This is temporarily accepted by bug #138, but should be superseded by Darrin's shared geometry-helper batch.
- High, Section 13.3/13.4: no geometry persistence, off-screen sanity check, or `View -> Reset window layout` registration exists on AM.
- Medium, navigation: stack transitions are conventional, but AM child screens do not yet implement ESC-to-back. PG has a precedent in `panda_gallery.py:422-444` and `instruction_pane.py:1357-1358`.

Design requirement:

- Keep AM as a top-level dev window until integrated into the v4 module shell.
- First geometry ship: use shared `pg_geometry.py` helper, register `AuditModuleWindow/geometry`, and keep bug #138's 800x560 as the computed fallback target until the helper can derive a content floor.
- Add `keyPressEvent` in `AuditModuleWindow` or child screens: if current widget is Screen B or Archive, ESC invokes the same method as Back.

### Screen A - Bug List

Evidence:

- Header has already been converted to Section 6.22 one-row anatomy at `audit_module_window.py:795-833`.
- Filter row begins at `audit_module_window.py:835`.
- Table setup is at `audit_module_window.py:892-934`.
- Fixed columns are now `#=72`, `Severity=112`, `State=148`, `Files=56` at `audit_module_window.py:923-931`.
- `setWordWrap(True)` and `setTextElideMode(Qt.ElideNone)` are at `audit_module_window.py:932-933`.
- StatusPane tally logic is at `audit_module_window.py:1303-1338`.
- Bottom status bar still includes queue counts at `audit_module_window.py:1344-1360`.

Violations:

- Medium, Section 6.21: the Screen A workflow stepper consumes `_WorkflowStepper`, but `_components.py:267` and `_components.py:423-435` still document and render an 8px rail. The Bible now requires 22px.
- High, Section 13.6: the live observation says `QTableWidget` can still elide title text even after `Qt.ElideNone`. The current code is necessary but not sufficient; a no-elide word-wrap delegate is required.
- Medium, Section 1.5.D: bottom status bar still mirrors queue counts (`OPEN`, `FIXED`, `untriaged`) that the left StatusPane/count rows own. Decision log says the bottom bar specializes in source/freshness.
- Low, Section 1.4: Screen A's fixed columns are much improved. At wide widths, keep title stretch and do not let metadata columns grow.

Design requirement:

- Preserve the one-row header and compact filters.
- Add `NoElideWordWrapDelegate` for the Title column. Delegate paints with `Qt.TextWordWrap | Qt.AlignTop` and never calls `elidedText`.
- Update `_WorkflowStepper` rail from 8px to 22px in code comments, size, and visual tests.
- Bottom status bar message should be source/freshness only: `BUGS.md parsed 10:08:48` plus fixed/open source metadata if needed. Queue summary remains in the left pane.
- Empty states follow Section 8: no OPEN bugs means one short tutorial line plus Refresh/Show fixed affordances; filtered-zero remains a table/filter state, not a full empty state.

### Screen B - Bug Detail And Triage

Evidence:

- Header is currently Back + title + meta subtitle at `audit_module_window.py:1770-1789`.
- Body is left content plus right triage assistant at `audit_module_window.py:1797-1817`.
- StatusPane begins as `Ready to triage` at `audit_module_window.py:1823-1831`.
- The mock provider note is at `audit_module_window.py:1837-1842`.
- Primary triage button is at `audit_module_window.py:1845-1852`.
- Legacy state badge is at `audit_module_window.py:1854-1858`, including direct color `#8a8a9a`.
- Result block uses fixed 110px height at `audit_module_window.py:1862-1875`.
- Gaps block uses scroll area at `audit_module_window.py:1879-1906`.
- `right_col.addStretch(1)` at `audit_module_window.py:1908` creates the known large air gap before bottom actions.
- Build Prompt button is visible but disabled at `audit_module_window.py:1911-1919`.
- `_render_triage_state` enables Build Prompt when state is ready/amend at `audit_module_window.py:2074-2075`.
- Work activity during triage currently changes button text and StatusPane shimmer at `audit_module_window.py:2176-2188`.

Violations:

- Critical, Section 1.6: action visibility does not match workflow state. Build Prompt is visible on untriaged bugs when it is not yet contextually useful. Move actions are visible too early.
- High, Section 1.5: `Ready to triage` StatusPane and `UNTRIAGED` badge duplicate the same state in nearby surfaces.
- High, Section 1.5: mock-provider note is filler in v0.1+ unless converted into live provider/source status.
- High, Section 1.4: stretch at line 1908 creates the large right-column void called out in bug #140.
- Medium, Section 6.22: Screen B header still uses title + meta subtitle instead of the strict module screen header. Metadata should move into a compact meta row/card, not a subtitle under the header.
- Medium, Section 3: Files/Reproduce/Expected/Actual content is rendered in one readonly text box, flattening section hierarchy.
- Medium, Section 2: direct hex colors remain in badge/QLineEdit styling (`#8a8a9a`, `#0d0d18`, `#14141f`, `#e8a87c`). Some are Bible tokens, but should be referenced through token names or documented as exceptions.

Design requirement:

- Header: one row only. Left: Back. Center: `BUG #129` or `BUG DETAIL`. Right: compact state pill and optional utility copy button. Separator directly below.
- Under header: a compact mono metadata strip: priority, files count, source line, current state. This earns its presence; it is operational data, not a header subtitle.
- Left content: split the bug fields into peach-caps sections: Files, Reproduce, Expected, Actual, Notes. Empty field shows a one-line muted placeholder, not a blank block.
- Right rail: replace filler with three compact zones:
  1. Work StatusPane: only current work phase (`Ready`, `Calling Claude API`, `Prompt built`, `Failed`).
  2. Verdict/state card: triage classification and readiness gaps. This owns `UNTRIAGED`, `READY`, `DESIGN`, `CLARIFY`, `FIXED`.
  3. Action stack: visible actions determined by Section 1.6.
- Remove `right_col.addStretch(1)` as the spacing mechanism. Let the triage rail hug content; if there is extra height, the left content gets the space.

Screen B action state machine:

| Bug state | Triage with AI | Resolve gaps | Build Fix Prompt | Move actions |
|---|---|---|---|---|
| No bug loaded | Hidden | Hidden | Hidden | Hidden |
| Untriaged | Visible enabled | Hidden | Hidden | Hidden |
| Triage running | Visible disabled with activity | Hidden | Hidden | Hidden |
| Design/clarify gaps | Visible secondary "Re-triage" | Visible enabled | Visible disabled with reason | Conditional: move if classification suggests |
| Ready, no unresolved gaps | Visible secondary "Re-triage" | Hidden | Visible enabled primary | Conditional secondary |
| Amend only | Hidden or secondary re-triage | Hidden | Visible enabled primary "Build Amendment Prompt" | Hidden |
| Feature request redirect | Hidden | Hidden | Hidden | Visible enabled "Move to Backlog" |
| Fixed | Hidden | Hidden | Hidden | Hidden; read-only archive affordance if needed |

Disabled reasons must be adjacent text or tooltip. Example: `3 gaps still need decisions before a prompt can be built.`

### Archive Screen

Evidence:

- Archive class begins at `audit_module_window.py:2461`.
- Header Back + title + subtitle is at `audit_module_window.py:2494-2512`.
- Search field direct styling is at `audit_module_window.py:2527-2531`.
- Status label uses `amStatusBar` at `audit_module_window.py:2559`.

Violations:

- Medium, Section 6.22: header has a subtitle. Archive should use the one-row module header and move operational status to result count/source row.
- Medium, navigation: Back exists but ESC-to-back is not implemented.
- Low, Section 8: `No archived items yet` exists as a status label, not a full Section 8 empty state.
- Low, Section 2: search QLineEdit styling repeats token hexes locally.

Design requirement:

- Header: Back + `ARCHIVE` + utility `Refresh index`, separator.
- Search row: search field + count text. Search field placeholder is operational and acceptable.
- Body: two-pane list/detail stays.
- Empty archive: centered Section 8 panel: `No archived fixes yet.` Secondary line: `Fixed bugs appear here after they are moved out of OPEN.` Actions: `Refresh`.
- No-match state: keep list pane, show `No matches for "..."` in the result area with `Clear search`.

### AM-Owned Dialogs

AM uses the shared dark modal family and dark_message. Per Darrin's decision log, fixed/content-sized modal popovers are exempt from full Section 13 persistence but need fit assertions for long labels. AM-specific guidance:

- ESC closes modal dialogs, relying on standard Qt behavior.
- Any AM modal that may include long file paths or provider errors must use wrapping text and a copied-to-clipboard affordance if the text is long.
- Do not create native `QMessageBox`; continue using dark dialogs.

## Part B - Design Specification

### Shared AM Grammar

Tokens:

- Background: `--canvas #14141f`, `--panel #1a1a2e`, `--panel-raised #22223a`, `--chrome #0a0a14`.
- Text: `--text #e0ddd5`, `--text-muted #8a8a9a`, `--text-dim #5f5f6f`.
- Accent: `--accent #e8a87c`, `--accent-soft rgba(232,168,124,.10)`, `--accent-border rgba(232,168,124,.35)`.
- States: green `--ok`, red `--err`, amber `--warn`, and existing AM gap-kind colors only when semantically tied to a gap/classification.

Components:

- Section 6.13 buttons: one peach-fill primary per screen state. Utility actions are transparent/neutral.
- Section 6.21 workflow stepper: Screen A reference mode, 18px indicators, 22px rail segments.
- Section 6.22 module screen header: one row only; no subtitle under header.
- StatusPane: work phase only, not a duplicate state badge.
- Bottom status bar: source/freshness, parse time, provider availability; not queue counts.

Navigation:

- Back buttons remain left-aligned in child-screen headers.
- ESC is equivalent to Back on Screen B and Archive.
- Screen A has no Back target, so ESC falls through to the window/app.
- Modal ESC closes/cancels.
- This matches existing PG patterns: `panda_gallery.py` forwards Escape to active views, and InstructionPane maps ESC to cancel/back behavior.

Activity:

- Operations over 500ms show a restrained activity indicator.
- Refresh/parse: Refresh button text changes to `Refreshing...`; bottom status bar dot turns peach; no full-screen overlay.
- AI triage: StatusPane enters `working`, button label `Triaging...`, shimmer/progress bar visible.
- Prompt build: Build button label `Building...`; status pane `Building prompt`; success toast/status then restore.
- No animation on instant filters, row selection, or screen transitions.

Colors:

- Move `_AM_SHELL_DEEP = #0d0d18` either into Bible as `--stage-deep` or back to `--canvas`. Until then, document it as AM-specific and do not spread it.
- Replace direct badge/search hexes with `AM_TOKENS`.
- Use red only for error/clarification gap, green only for ready/fixed/pass, peach for focus/primary/actionable design work.

### Screen A At Three Widths

Narrow, about 1000px right-pane area:

- Summary pane remains 240px unless the AM window hits the Section 13 floor.
- Table fixed columns stay #72, Severity112, State148, Files56; title gets remaining width and wraps to two lines.
- Filter row remains one line until floor; Show fixed can move after result count only if needed by a narrow variant.

Default, about 1280px:

- Current layout is close: summary pane, separator, center table.
- Title column should rarely wrap; if live Qt still elides, delegate is the fix.
- Workflow stepper rails visibly connect steps.

Wide, about 1800px:

- Metadata columns do not expand.
- Title column gets the space.
- Row height may grow with wrapped titles only when needed; otherwise stays compact.

Removal tests:

- Header title: remove it and the module loses location. Keep.
- Refresh: remove it and the source reload affordance disappears. Keep.
- Header subtitle: already removed. Correct.
- Count rows: remove them and queue scanning slows. Keep.
- Bottom queue counts: remove them and no information is lost because StatusPane owns queue. Remove.

### Screen B At Three Widths

Narrow, about 1000px content area:

- Use a two-column split with right rail min 280/max 340.
- If below the computed floor, stack triage rail below content only as an explicit narrow variant, not by accidental squeeze.
- Back/header/meta remain visible.

Default, about 1280px:

- Left content gets roughly 2fr, triage rail 320px.
- Right rail hugs content; no stretch gap before actions.
- Gaps scroll internally when many gaps exist.

Wide, about 1800px:

- Left content grows.
- Right rail remains capped; it should not become a wide empty column.
- Metadata strip can display more fields in one row.

Removal tests:

- Mock provider note: remove it and no workflow loss occurs. Remove.
- StatusPane plus state badge duplication: one must own work phase, one must own triage state. Keep both only after their jobs diverge.
- Build Prompt visible while untriaged: hide it; no loss.
- Gaps scroll area: keep; #139 proved it prevents collapse.
- Right-column stretch: remove; it creates empty air.

### Archive At Three Widths

Narrow:

- Back + ARCHIVE header one row.
- Search field full width above list/detail if needed.
- Detail pane can stack below list at narrow floor.

Default:

- List/detail splitter as today.
- Result count and source freshness near search row.

Wide:

- List remains content-capped; detail gets width.
- No giant list row spacing.

Removal tests:

- Subtitle under header: remove and move useful detail to search/status row. No loss.
- Detail pane: keep; archive is read/inspect.
- Status label: keep only if it reports result counts or loading/errors.

### Module Shell

- Correct default: first AM open should fit near PG host window and remember its geometry. Bug #138's 800x560 is the fallback until helper math lands.
- Register `AuditModuleWindow/geometry` with global `Reset window layout`.
- The AM stack remains Screen A -> Screen B/Archive -> Screen A. No breadcrumbs; Back is enough.

## Part C - HTML Mockup

Mockup file:

`C:\CODEX PG\workflows\design\pg_general_mockups\AM_bible_pass_v1.html`

It shows:

- Screen A narrow/default/wide, including 22px workflow rails and specialized bottom status bar.
- Screen B states: untriaged, ready, fixed, with Section 1.6 action changes.
- Archive default and empty/no-match patterns.

## Part D - Implementation Sequencing

### v4.42.4 - AM Stepper And Statusbar Finish

Surfaces: Screen A, `_WorkflowStepper`, bottom status bar.

Bible sections: 1.4, 1.5, 6.21, 6.22.

Estimated LOC: 35-70.

Dependencies: none.

Acceptance:

- `_WorkflowStepper` rail height is 22px in code and visual smoke.
- Screen A bottom status bar no longer includes `untriaged` queue count.
- Screen A still shows queue tally in StatusPane and count rows.

### v4.42.5 - AM Title Delegate And Empty States

Surfaces: Screen A table, empty states.

Bible sections: 8, 13.6.

Estimated LOC: 80-140.

Dependencies: v4.42.4 recommended but not required.

Acceptance:

- Title column uses a custom delegate that never elides.
- Screenshot at narrow/default/wide shows no `...` in title cells.
- No OPEN bugs empty state uses Section 8 voice.

### v4.43 - AM Navigation And Activity

Surfaces: AM shell, Screen B, Archive.

Bible sections: 1.1, 1.6, 6.13, 7.

Estimated LOC: 90-160.

Dependencies: none.

Acceptance:

- ESC from Screen B returns to Screen A.
- ESC from Archive returns to Screen A.
- Triage, refresh, and prompt build show restrained working state when operation exceeds 500ms.
- No decorative or playful animation.

### v4.44 - Screen B Structural Redesign

Surfaces: `_BugDetailScreen`.

Bible sections: 1.4, 1.5, 1.6, 2, 3, 6.13, 6.22, 8.

Estimated LOC: 250-450.

Dependencies: v4.43 activity pattern helps; can ship without global geometry helper.

Acceptance:

- No mock-provider filler.
- No large right-column void.
- Header follows Section 6.22.
- Actions follow the state machine in this doc.
- At least three visual states: untriaged, ready, fixed.

### v4.45 - Archive Polish

Surfaces: `_ArchiveScreen`.

Bible sections: 6.22, 8, 13.

Estimated LOC: 80-150.

Dependencies: v4.43 navigation if ESC is centralized.

Acceptance:

- Header one row, no subtitle.
- Empty archive and no-match states are distinct.
- Search status is operational, not filler.

### v4.46 - AM Geometry Helper Integration

Surfaces: `AuditModuleWindow`; shared helper lives outside AM.

Bible sections: 13.1-13.8.

Estimated LOC: 120-220 for helper plus 20-40 AM-specific.

Dependencies: shared `pg_geometry.py` batch from the whole-app audit decision log.

Acceptance:

- AM registers geometry key.
- First open is content-driven fallback near 800x560.
- Restore checks connected screens.
- Global reset window layout clears AM geometry.

## Part E - Bible Amendments Needed

### Amendment 1 - Workflow Stepper Rail Correction

Bible Section 6.21 already says 22px in the current file, but the reusable widget still contains old 8px comments and implementation. No new Bible text is needed; implementation must catch up.

Implementation note to attach to dispatch:

```text
Update `_WorkflowStepper._build_rail_segment()` from 8px to 22px and update its docstring. This is not a redesign; it is aligning the widget with PG_DESIGN_BIBLE_v1 Section 1.4 and 6.21.
```

### Amendment 2 - ESC-To-Back Navigation

Proposed Bible text under Section 7:

```text
Desktop Back behavior: any PG screen that shows a visible Back affordance must support Escape as the keyboard equivalent, unless text editing focus has a documented reason to consume Escape first. Escape must call the same handler as the Back control. Modal dialogs keep standard Escape-to-cancel behavior. Screens with no Back target do not invent one.
```

### Amendment 3 - Activity Indicator Component

Proposed Bible text under Section 6:

```text
Activity indicator (`.activity-indicator`). Use only for operations expected to exceed 500ms or operations that cross process/network boundaries. The indicator is informational, not decorative. Accepted forms: button label swap to present participle (`Refreshing...`, `Triaging...`), a 10px status dot in the working color, or a 3px restrained shimmer/progress bar inside StatusPane. Motion timing is 1.5s linear pulse/sweep. Forbidden: bouncing loaders, spinners on instant actions, blocking overlays for non-blocking work, or animation that remains after work completes.
```

### Amendment 4 - AM Deep Canvas Token

Option A: promote `#0d0d18` as `--stage-deep` for AM/developer utility surfaces only.

Option B: remove the AM-specific value and use `--canvas #14141f`.

Codex recommendation: Option B unless Darrin specifically prefers the deeper AM shell. The Audit Module is part of PG and should avoid an AM-only background token unless the darker stage has a diagnostic purpose.

## Open Questions For Claude

- Should the v4.42.4 pre-staged patch include only the stepper/statusbar corrections, or should it also include the no-elide delegate?
- Should Screen B keep a separate state badge once the verdict card exists, or should the verdict card fully replace it?
- Should `Re-triage` remain visible on fixed bugs for developer correction, or should fixed be read-only?

## Final Recommendation

Ship v4.42.4 as the smallest AM Bible-alignment patch: 22px stepper rails, statusbar specialization, and no new visual concepts. Then ship the no-elide title delegate. After that, do Screen B as a coherent structural redesign with the action state machine, ESC/back, and activity pattern in place.
