---
schema_version: 1
id: CLAUDE-DESKTOP-20260502-082500-BA-APPLET-SPEC-UPDATE
thread_id: BA-APPLET-V2-ENHANCEMENTS
in_reply_to: CLAUDE-DESKTOP-20260502-071500-BA-APPLET-V2
from: claude_desktop
to: codex
type: dispatch
priority: normal
status: open
thread_status: active
action_owner: codex
requires_darrin_decision: false
approval_boundary: ready_to_commit
reasoning_tier: Medium
---

# BA Applet v2 — spec update from Bug #160 live testing

## Context

Darrin did a live visual walkthrough of the Bug #160 relay hub rebuild
today (2026-05-02). 11 defects were found that required pre-commit
dispatches back to CC. This is exactly the class of bugs the BA applet
is supposed to surface BEFORE live testing.

This dispatch adds new checks to the BA applet spec based on every
defect that slipped through. If all checks below had existed in the
Source Scanner and Wiring Checklist, the defects would have been caught
by CC before filing any RTC.

Incorporate these into the BA applet v2 production pass (your current
active dispatch `CLAUDE-DESKTOP-20260502-071500-BA-APPLET-V2`).

---

## New Source Scanner checks to add

### Check A — QLabel border-radius aliasing (CRITICAL)

**What it catches:** Defect 6 (aliased stepper circles).
`QLabel` with `border-radius` does not anti-alias on Windows Qt. Any
QLabel used as a circular indicator (common pattern: `setFixedSize(N,N)`
+ `border-radius: N/2 px`) will render with jagged edges.

**Scanner pattern:**
Scan for `setFixedSize` calls followed by a `border-radius` QSS rule
targeting the same objectName. If the `border-radius` value equals
`fixedSize / 2` (i.e., it's trying to make a circle), flag it.

```
FAIL — QLabel circle-indicator uses border-radius (will alias on Windows)
Detail: Use a custom QWidget subclass with QPainter + Antialiasing hint instead.
Rule: Qt rendering limitation / Bible §6.21
```

**Heuristic in scanner JS:**
```javascript
// Flag any QLabel with fixed square size where border-radius ≈ half the size
var label_circle_re = /setFixedSize\((\d+),\s*\1\)/g;
// If matched, check nearby QSS for border-radius: N/2 px on same objectName
// Flag as FAIL
```

---

### Check B — Stub button missing tooltip (HIGH)

**What it catches:** Defect 9 (`relayFooterMore` — no tooltip, no connect).
Already partially in scanner as "unwired button" check. Strengthen it:
a button that has NEITHER `.clicked.connect()` NOR `setEnabled(False)`
NOR `setToolTip()` is a CRITICAL issue, not just HIGH.

**Updated severity:** Upgrade unwired-with-no-tooltip from HIGH → CRITICAL.

**Add sub-check:** If `setEnabled(False)` IS present but `setToolTip()` is
absent on the SAME button, flag as HIGH (not just a warning).

---

### Check C — Generic QLabel rule in setStyleSheet (HIGH)

**What it catches:** Defects 1 (template pills), 10 (transcript border cascade).
When `setStyleSheet()` is called on a parent widget with a bare
`QLabel { ... }` or `QWidget { ... }` rule (no objectName selector),
it cascades into ALL child QLabel/QWidget descendants — including
StatusPills, which use inline `setStyleSheet` that gets overridden.

**Scanner pattern:**
```javascript
// In any _xxx_qss() function, look for unqualified QLabel { or QWidget {
// (not preceded by # or [ — i.e., no objectName or property selector)
var cascade_re = /(?<![#\w\[])QLabel\s*\{|(?<![#\w\[])QWidget\s*\{/g;
if (cascade_re.test(qss_body)) {
    findings.push({
        sev: 'fail',
        title: 'Generic QLabel/QWidget rule in QSS — cascade risk',
        detail: 'Bare QLabel { } or QWidget { } rules cascade into ALL child widgets including StatusPills. Use #objectName selectors only.',
        rule: 'R17 cascade / Bible §6.24'
    });
}
```

---

### Check D — Widget background contrast (HIGH)

**What it catches:** Defect 10 (transcript card border invisible against
pane-raised background).

Near-zero contrast between a widget's border color and its parent's
background color is a layout invisibility bug. The specific failure:
`RELAY_COLOR_BORDER` (#2a2a3e) against `RELAY_COLOR_PANE_RAISED`
(#22223a) has contrast ratio < 1.3:1 — effectively invisible.

**Scanner pattern:**
Look for pairs of adjacent color constants in QSS where both are from
the PG border/pane family. Flag if the contrast ratio between them
would be < 1.5:1.

Add a lookup table of known low-contrast PG pairs to the scanner:

```javascript
var LOW_CONTRAST_PAIRS = [
    // [border_color_name, bg_color_name, ratio]
    ['RELAY_COLOR_BORDER', 'RELAY_COLOR_PANE_RAISED', 1.25],
    ['RELAY_COLOR_BORDER_SOFT', 'RELAY_COLOR_PANE', 1.15],
    ['RELAY_COLOR_BORDER_SOFT', 'RELAY_COLOR_PANE_RAISED', 1.10],
];
// If a QSS rule uses a known low-contrast pair for border + background,
// flag as WARN with the specific pair and measured ratio.
```

---

### Check E — Layout overlap risk: indicator above label with no spacing (HIGH)

**What it catches:** Defect 7 (stepper "3" overlapping "Capture" text).

When a QVBoxLayout stacks a fixed-size widget (indicator circle) above
a QLabel with no `setSpacing()` or explicit margin, the label text can
overlap the indicator on certain platforms/DPI settings.

**Scanner pattern:**
```javascript
// Look for QVBoxLayout patterns where setSpacing(0) or setContentsMargins(0,0,0,0)
// is set AND a fixed-size widget is added before a QLabel.
// Flag as WARN if no explicit spacing is set between them.
var no_spacing_re = /setSpacing\(0\)|setContentsMargins\(0,\s*0,\s*0,\s*0\)/g;
```

Flag as WARN: "QVBoxLayout with spacing=0 stacking a fixed widget above
a QLabel — label text may overlap the widget at certain DPI settings.
Add setSpacing(4) minimum."

---

### Check F — QScrollArea child not height-capped (MED)

**What it catches:** Defect 8 (EvidenceBlock "▴ hide" button scrolls away).

When a collapsible widget's body is added to a parent `QScrollArea`
without an internal scroll or height cap, the toggle button (in the
header) scrolls out of view as the user scrolls down. Pattern:
a widget with a toggle button in its header should cap its body content
height OR use an internal QScrollArea.

**Scanner pattern:**
Look for custom QWidget classes that have:
1. A toggle QPushButton in `_build_ui`
2. A `self._body` child widget that is added to the outer layout WITHOUT
   a `setMaximumHeight()` call or a wrapping `QScrollArea`.

Flag as WARN: "Collapsible widget body has no height cap and no internal
scroll — toggle button may scroll out of reach in a parent scroll area."

---

### Check G — Widget painting outside bounds (MED)

**What it catches:** Defect 3 (seg control bleeding orange triangles below
RelayHeadBar into the tab strip).

When a `QWidget` with `setFixedHeight(N)` contains buttons that have
`min-height: N` but `max-height` is not set, Qt Fusion may paint
selection indicators outside the widget's clip rect.

**Scanner pattern:**
Look for `setFixedHeight(N)` on a QWidget where child buttons have
`min-height` >= N-4 in the associated QSS. Flag as WARN.

```javascript
// Find setFixedHeight(N) on widgets
var fh_re = /setFixedHeight\((\d+)\)/g;
// For each N, check if associated QSS has min-height >= N-4
// Flag: "Widget fixed height N px but child button min-height approaches N — add max-height to buttons to prevent paint bleed"
```

---

## New Wiring Checklist rules to add

### Wiring Rule 1 — Every interactive element must update visible state on interaction

**What it catches:** Defect 11 (clicking left rail report rows doesn't update right panel).

Add to the Wiring Checklist column schema a new field:
**"Updates UI on click"** — yes/no/partial.

For every WIRED entry, this field must be "yes" or "partial (stub)".
If it is blank or "no", flag as UNWIRED even if `.clicked.connect()`
exists — a wired button that silently does nothing visible to the user
is functionally unwired from the user's perspective.

Add these entries to WIRING_DATA with "Updates UI on click: partial":
```javascript
{
    module: 'relay',
    widget: 'ReportListRow (All Reports rail)',
    expected: 'Selects row visually AND updates right panel header/content',
    status: 'stub',   // was 'wired' — now correctly 'stub' since right panel doesn't update
    verified: null,
    notes: 'Row selection highlight works but right panel content is static stub. Defect 11.',
    updatesUI: 'partial'
}
```

### Wiring Rule 2 — Sticky-header check

**What it catches:** Defect 8 (hide button scrolls away).

Add a new column to WIRING_DATA: **"Sticky on scroll"** — for any
toggle/expand button that controls collapsible content inside a scroll
area, this must be "yes" or flagged.

---

## New visual reference check tab: "Layout Safety"

Add a new tab to the BA applet called **"Layout Safety"** with 8 checks:

| Check | Rule | Severity |
|---|---|---|
| QLabel border-radius → use QPainter instead | Qt limitation | CRITICAL |
| No bare `QLabel {}` / `QWidget {}` in parent setStyleSheet | Cascade risk | HIGH |
| Widget fixed-height + child button min-height approaching parent height | Paint bleed | HIGH |
| Collapsible body in scroll area: must have height cap or internal scroll | Toggle visibility | HIGH |
| Layout spacing=0 between fixed indicator and QLabel | Overlap risk | MED |
| Border color vs parent bg contrast ≥ 1.5:1 | Visibility | MED |
| Every interactive element that changes state must update visible UI | UX completeness | HIGH |
| Sticky toggle: collapsible headers must remain visible when body scrolls | UX reachability | MED |

These are presented as manual checkboxes (like the existing component
tabs) with red/orange/green dot indicators. The developer checks each
one off after verifying in the live app.

---

## Summary of scope changes to BA applet v2

In addition to the existing Step 0 / Step 1 items already dispatched:

1. **Source Scanner:** Add checks A–G above (7 new scanner checks)
2. **Wiring Checklist:** Add `updatesUI` field + update `ReportListRow`
   entry to `stub` with defect 11 note
3. **New tab:** "Layout Safety" with 8 manual checks
4. **FAILURE_DB update:** Add all 11 Bug #160 pre-commit defects to
   Relay's FAILURE_DB with correct fix targets. This ensures the report
   generated for "Relay" is honest and complete.

Relay APP_PROFILES score after all 11 defects: `{pass: 53, fail: 9, warn: 4}`
(approximate — Codex to compute exact from FAILURE_DB entries).

---

## Delivery

Same output path as the v2 dispatch — single self-contained HTML file.
File one RTC covering both the original v2 dispatch and this spec update
together. No need to file two separate RTCs.

— CD
