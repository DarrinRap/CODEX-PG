# CODEX AM v0.2 Polish Spec v1

Date: 2026-04-26
Author: Codex
Status: Spec only. No Python, HTML, or runtime code changed.

## 1. Overview

AM v0.2 polish covers three user-visible fixes that did not make the v0.1 ship:
Back / Refresh controls need lower visual weight, Screen B bug detail needs
collapsible sections for long bugs, and Screen A severity cells need a clear
placeholder when severity is unset. These matter because they reduce false
visual priority, make dense bugs scannable, and prevent blank table cells from
looking like rendering errors.

In scope:

- AM Screen A list polish for Refresh and Severity.
- AM Screen B current detail polish only where it does not fight Screen B v2.
- Implementation guidance for QSS, widgets, signal/slot behavior, and tests.

Out of scope:

- No Screen B redesign work.
- No triage AI logic changes.
- No BUGS.md schema changes.
- No parser rewrite.
- No Archive search changes.
- No code changes as part of this spec task.

Source discrepancy:

- Claude's brief says Back and Refresh are in the detail toolbar.
- Current code has Refresh on Screen A and Back on Screen B.
- Treat them as one utility-control style, but implement on their actual
  current surfaces.

Sources read: `BUGS.md`, `audit_module_window.py`,
`PG_DESIGN_BIBLE_v1.md`, and `STRATEGY_NOTES.md`.

## 2. Item 1: Back / Refresh Visual Weight

### Surface Affected

File:

- `C:\panda-gallery\audit_module\audit_module_window.py`

Classes / ranges:

- `_BugListScreen.__init__`, approx. lines 334-353:
  `self.refresh_btn = QPushButton("Refresh")`.
- `_BugDetailScreen.__init__`, approx. lines 757-786:
  `self.back_btn = QPushButton("← Back")`.
- AM stylesheet where neutral buttons and section styling are defined.

### Current Behavior

Refresh is a full neutral button beside the Screen A "Bug list" title. Back is
a full neutral button at the top-left of Screen B. Both read as medium-weight
commands, so they compete with more important workflow actions such as triage,
fix-prompt generation, and move-state buttons.

### Desired Behavior

Back and Refresh should read as navigation / utility chrome:

- Visible, legible, and keyboard-focusable.
- Lower weight than primary and secondary AM actions.
- Subtle hover / pressed feedback.
- No accent fill or strong button box at rest.
- Same behavior as today.

### Implementation Approach

Add quiet AM utility object names:

- `amUtilityButton` for Refresh.
- `amNavButton` for Back.

Recommended QSS intent:

```css
QPushButton#amUtilityButton,
QPushButton#amNavButton {
    background: transparent;
    border: 1px solid transparent;
    color: var(--text-dim);
    padding: 4px 8px;
    min-height: 24px;
}

QPushButton#amUtilityButton:hover,
QPushButton#amNavButton:hover {
    background: var(--pane-raised);
    border-color: var(--border-subtle);
    color: var(--text-main);
}
```

Use real AM token values from the current stylesheet rather than literal CSS
variables if QSS does not support them directly.

Design Bible alignment:

- `.vc-btn` small inline utility control, approx. line 503.
- Button hierarchy / one primary per screen, approx. lines 471-499.
- `--text-dim` for utility / placeholder tone, approx. line 93.

Labels:

- Keep `← Back` unless Screen B v2 changes navigation language.
- Keep `Refresh` or use quiet icon+text such as `↻ Refresh`.
- Do not make either icon-only in v0.2.

Tooltips:

- Preserve existing Back and Refresh tooltips.

### Acceptance Criteria

1. Refresh reads as a quiet title-row utility, not a command button.
2. Back reads as navigation, not as a competing Screen B action.
3. Hover, pressed, disabled, and keyboard-focus states remain visible.
4. Labels fit at the current AM default window size.
5. Refresh and Back behavior is unchanged.

### Test Plan

1. Launch AM and inspect Screen A.
2. Confirm Refresh is visible but lower weight than workflow actions.
3. Hover and tab-focus Refresh.
4. Open a bug and inspect Screen B Back.
5. Hover and tab-focus Back.
6. Click Refresh and Back; confirm behavior is unchanged.

## 3. Item 2: Collapsible Bug Detail Sections

### Surface Affected

File:

- `C:\panda-gallery\audit_module\audit_module_window.py`

Class / ranges:

- `_BugDetailScreen.__init__`, approx. lines 798-807:
  creates one "Bug content" section and one read-only `QTextEdit`.
- `_BugDetailScreen._refresh`, approx. lines 945-981:
  calls `self.detail.setPlainText(...)`.
- `_BugDetailScreen._format_bug_text`, approx. lines 983-1000:
  flattens Files, Reproduce, Expected, Actual, Fix direction, Notes, Relates.
- `_section_header` / `_add_section`, approx. lines 265-280.

### Current Behavior

Screen B renders structured bug content as one monolithic read-only text editor.
Reproduce, Expected, Actual, Notes, Files, and related fields are visible inside
that one expanded block. Long bugs force a lot of scrolling and make it hard to
focus on one field at a time.

### Desired Behavior

Render bug content as discrete collapsible sections:

- Files
- Reproduce
- Expected
- Actual
- Fix direction
- Notes
- Relates

Each section needs:

- Clickable header.
- Disclosure arrow / chevron.
- Title.
- Optional dim hint such as `3 lines`, `8 files`, or `empty`.
- Body content that preserves line breaks.

Default state:

- Sections with 8 logical lines or fewer default expanded.
- Sections over 8 logical lines default collapsed.
- Sections over roughly 700 characters default collapsed.
- Files / Relates with more than 6 items default collapsed.
- Absent sections may be hidden.

### Implementation Approach

Do not attempt clickable subsections inside the current plain `QTextEdit`.
Replace the single text editor with a scrollable stack of section widgets.

Recommended changes:

- Replace `_format_bug_text(parsed)` with `_bug_detail_sections(parsed)`.
- Return section records with `title`, `body`, `kind`, `hint`,
  `default_expanded`.
- Add `_CollapsibleBugSection(QWidget)` or equivalent.
- Put the section stack inside a `QScrollArea` in the current left column.

Suggested section widget:

- Header: checkable `QToolButton` or `QPushButton`, full-width clickable.
- Header text: arrow + title + optional hint.
- Body: selectable `QLabel` or read-only `QTextEdit` sized to content.
- Toggle: header click changes body visibility and arrow state.

Design Bible alignment:

- Section header / body / collapsed pattern, approx. lines 412-422.
- Peach all-caps section language, approx. lines 193-210.
- Dim mono hints via `.hint` pattern.

Persistence:

- Recommendation: no cross-session persistence for v0.2.
- Reset expansion by content length each time a bug opens.
- Optional in-memory state during one Screen B session is acceptable.
- Do not add QSettings unless Claude explicitly chooses to mirror BUG #118.

Missing fields:

- Hide absent sections by default.
- If all structured detail is empty, show one quiet placeholder:
  `No structured bug detail parsed.`

### Acceptance Criteria

1. Screen B bug content is separate sections, not one text blob.
2. Clicking a header toggles only that section.
3. Short sections default expanded.
4. Long sections default collapsed using the thresholds above.
5. Section bodies preserve line breaks and allow practical text selection.

### Test Plan

1. Open a short bug; verify short sections are expanded.
2. Open a long bug; verify long sections are collapsed with useful hints.
3. Toggle every section open and closed.
4. Confirm right-rail triage controls still work.
5. Confirm Back still returns to Screen A.
6. Confirm no BUGS.md content changes from toggling.

## 4. Item 3: Severity Column N/A Handling

### Surface Affected

File:

- `C:\panda-gallery\audit_module\audit_module_window.py`

Class / ranges:

- `_BugListScreen`, approx. lines 407-425:
  table columns `["#", "Title", "Severity", "State", "Files"]`.
- `_BugListScreen.reload`, approx. lines 520-550:
  builds row dictionaries.
- `_BugListScreen.reload`, approx. lines 572-575:
  filters by severity using `row["severity"].lower()`.
- `_BugListScreen._populate_table`, approx. lines 591-592:
  renders `row["severity"] or "—"`.
- `_BugListScreen._severity_color`, approx. lines 607-615:
  returns muted color for unknown severity.

### Current Behavior

The table rendering path already falls back to `—` for missing severity in at
least one place, and fixed-row construction also normalizes missing severity to
`—`. However, the row model mixes raw values and display values. Open rows carry
`bug["severity"]` directly, while filtering calls `.lower()` on the row value,
which is fragile if the parsed severity is `None` or empty.

### Desired Behavior

Missing severity should display a clear placeholder. Recommendation: use `—`,
not `N/A`.

Reason:

- The code already uses `—`.
- `—` reads as unset.
- `N/A` can imply the field does not apply.
- The Design Bible uses dim text for placeholders.

The placeholder should be dim and should have a tooltip explaining that severity
is unset.

### Implementation Approach

Separate raw severity from display severity.

Recommended row fields:

- `severity_raw`: normalized source value or `""`.
- `severity_display`: source value or `—`.

Normalization:

```python
severity_raw = (bug.get("severity") or "").strip()
severity_display = severity_raw or "—"
```

Filtering:

- Use `severity_raw`.
- `all` includes unset severity rows.
- Concrete severity filters exclude unset severity rows.
- Never call `.lower()` on a possible `None`.

Rendering:

- Cell text uses `severity_display`.
- Empty raw severity uses Design Bible dim / placeholder color.
- Tooltip: `Severity not set in BUGS.md.`
- Known severities keep existing severity color mapping.

### Acceptance Criteria

1. Bugs with no severity show `—` in the Severity column.
2. The placeholder uses dim placeholder styling.
3. Placeholder tooltip says severity is not set in BUGS.md.
4. `all` filter includes unset-severity bugs.
5. Severity-specific filters exclude unset-severity bugs without errors.

### Test Plan

1. Load Screen A with at least one bug lacking severity.
2. Verify the Severity cell shows `—`.
3. Hover the cell and confirm tooltip.
4. Test `all`, `Critical`, `High`, `Medium`, and `Low` filters.
5. Confirm no exception occurs when filtering.

## 5. Conflict Check with Screen B v2

### Item 1: Back / Refresh

Status:

- Refresh: no conflict. Screen A only.
- Back: conflict. Screen B header is part of Screen B v2.

Decision:

- Refresh ships independently.
- Back should roll into Screen B v2 if v2 is imminent.
- If v2 is delayed, apply quiet `amNavButton` to current Back as a low-risk
  bridge.

### Item 2: Collapsible Bug Detail Sections

Status:

- Conflict. This changes Screen B left-pane structure.

Decision:

- Screen B v2 wins.
- Make collapsible detail sections a required Screen B v2 behavior.
- Only ship a v0.2 bridge if Screen B v2 is delayed.

### Item 3: Severity Placeholder

Status:

- No conflict. Screen A table / row-model behavior.

Decision:

- Ship independently before or alongside Screen B v2.

## 6. Sequencing

1. Ship severity placeholder first. It is Screen A only, low risk, and cleans up
   fragile filtering on unset values.
2. Ship Refresh visual polish next. It is Screen A only and can establish the
   quiet utility style.
3. Handle Back with Screen B v2 unless v2 is delayed.
4. Handle collapsible bug detail sections inside Screen B v2. It is the highest
   structural change and should not churn the current Screen B twice.

## 7. Open Questions for Darrin

1. Severity placeholder copy:
   recommendation is `—`, not `N/A` or `Unset`.
2. Collapsible persistence:
   recommendation is no cross-session persistence for v0.2; reset on bug open.
3. Back / Refresh treatment:
   recommendation is quiet text or icon+text utility buttons, not icon-only.
4. Screen B v2 timing:
   if v2 is shipping immediately, roll Back and collapsible sections into v2;
   otherwise implement them as a narrow bridge.
