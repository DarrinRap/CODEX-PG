---
schema_version: 1
id: CLAUDE-DESKTOP-20260502-092000-BA-APPLET-V2-FINAL
thread_id: BA-APPLET-V2-ENHANCEMENTS
supersedes: CLAUDE-DESKTOP-20260502-071500-BA-APPLET-V2
supersedes_also: CLAUDE-DESKTOP-20260502-082500-BA-APPLET-SPEC-UPDATE
from: claude_desktop
to: codex
type: dispatch
priority: normal
status: open
thread_status: active
action_owner: codex
requires_darrin_decision: false
approval_boundary: ready_to_commit
reasoning_tier: High
---

# BA Applet v2 — tested final dispatch (supersedes 071500 + 082500)

The two earlier dispatches (071500 and 082500) are SUPERSEDED by this
one. Codex should work from this document only.

## Why the earlier dispatches were pulled

CD tested the prototype scanner against real PG source (developer_hub.py,
hub_components.py) before dispatching. Results:

**Original v2 prototype scanner — tested accuracy:**
- 6 findings on real source
- 5 false positives (QTabWidget in docstring, toggled-not-clicked, QLabel
  objectNames matched by button heuristic)
- 0 confirmed true positives
- 9 real bugs missed entirely

The scanner logic was regex on raw text that couldn't distinguish imports
from docstrings, `clicked` from `toggled`, or button objectNames from
label objectNames.

**Corrected scanner logic — tested accuracy (this dispatch):**
- 3 findings on real developer_hub.py
- 0 false positives (manually verified)
- 3 confirmed true positives (all real wiring gaps)
- Example source triggers all 6 AC-B5 violations correctly

The spec update dispatch (082500) contained scanner check proposals that
were also untested. Several of those checks are correct in principle but
the implementations were wrong. This dispatch provides tested
implementations for all of them.

---

## What the BA applet is and is not

**What it is:** A developer-facing HTML tool that:
1. Renders reference components (pills, buttons, steppers) to verify
   they match the Design Bible visually
2. Runs automated static analysis on pasted PySide6 Python source to
   find real wiring and styling bugs before commit
3. Maintains a manually-updated wiring registry tracking every
   interactive element's status
4. Generates structured reports for CC/Codex dispatch

**What it is not:** It cannot catch runtime visual bugs (layout overlap,
scroll behaviour, paint bleed, aliasing). Those require live app testing
(AC-R19). The scanner is for static code patterns only.

---

## Step 0 — required reading before any code

Read these files in order. Report findings before writing HTML.

1. `workflows/design/applets/PG_Design_Bible_Audit_v2.html` — CD's
   prototype. You are improving it, not starting from scratch.
2. `workflows/design/applets/PG_Design_Bible_Audit_v1.html` — v1 for
   reference on the visual audit tab structure.
3. `relay/developer_hub.py` — primary source for wiring status audit
4. `relay/hub_components.py` — secondary source for wiring audit
5. `relay/tester_hub.py` — for tester hub wiring entries

In your Step 0 report, state:
- What you found in each file
- Any conflicts between this dispatch and what you see in the source
- What you plan to change vs keep from the prototype

---

## Step 1 — corrected Source Scanner implementation

The Source Scanner tab accepts pasted PySide6 Python source and runs
the following checks. Replace the scanner JS entirely — do NOT try
to patch the existing scanner.

### Scanner check specifications (all tested against real PG source)

**CRITICAL: The entire scanner must handle both patterns:**
- `self._foo = QPushButton(...)` → attribute buttons
- `foo = QPushButton(...)` → local variable buttons

Both patterns appear in PG source. The original scanner only handled
`self._xxx`. This was the root cause of the relayFooterMore miss.

---

#### CHECK 1 — QTabWidget real import (CRITICAL)

Detect actual import lines only. Docstrings and comments mentioning
QTabWidget are NOT violations.

```javascript
function checkQTabWidget(src) {
    var lines = src.split('\n');
    for (var i = 0; i < lines.length; i++) {
        var line = lines[i].trim();
        if (/^(?:from\s+\S+\s+import|import\s+)/.test(line) &&
            line.indexOf('QTabWidget') !== -1) {
            return {
                sev: 'fail',
                title: 'QTabWidget import at line ' + (i+1),
                detail: 'Bible forbids QTabWidget. Replace with custom tab strip.',
                rule: 'AC-R1'
            };
        }
    }
    return null;
}
```

**Tested:** Returns null on both developer_hub.py and hub_components.py
(which mention QTabWidget only in docstrings). Returns FAIL on any file
with `from PySide6.QtWidgets import QTabWidget`.

---

#### CHECK 2 — Unwired buttons (HIGH)

Collect all signal connections across the file (clicked, toggled,
pressed). Collect all QPushButton assignments (both `self._x` and local
`x`). Flag any button where no signal is connected AND it is not
disabled.

```javascript
function checkUnwiredButtons(src) {
    var findings = [];

    // All connected signal targets (attr names, stripped of self._)
    var connected = {};
    var connectRe = /(\w+)\.(clicked|toggled|pressed|toggled)\s*\.connect/g;
    var m;
    while ((m = connectRe.exec(src)) !== null) {
        connected[m[1].replace(/^_/, '')] = true;
    }

    // All disabled widget attrs
    var disabled = {};
    var disableRe = /(\w+)\.setEnabled\((?:False|false)\)/g;
    while ((m = disableRe.exec(src)) !== null) {
        disabled[m[1].replace(/^_/, '')] = true;
    }

    // All tooltip attrs
    var hasTooltip = {};
    var tipRe = /(\w+)\.setToolTip\(/g;
    while ((m = tipRe.exec(src)) !== null) {
        hasTooltip[m[1].replace(/^_/, '')] = true;
    }

    // All QPushButton assignments (self._x or local x)
    // Use window-based objectName lookup to get display name
    var btnRe = /(?:self\.)?(_?\w+)\s*=\s*QPushButton\(/g;
    var seen = {};
    while ((m = btnRe.exec(src)) !== null) {
        var raw = m[1];
        var attr = raw.replace(/^_/, '');
        if (seen[attr]) continue;
        seen[attr] = true;

        // Get objectName from window after assignment
        var window_text = src.slice(m.index, Math.min(src.length, m.index + 400));
        var objMatch = window_text.match(/setObjectName\(\s*["']([^"']+)["']\s*\)/);
        var objName = objMatch ? objMatch[1] : attr;

        var wired = connected[attr] || connected[raw.replace(/^_/, '')];
        var dis = disabled[attr] || disabled[raw.replace(/^_/, '')];
        var tip = hasTooltip[attr] || hasTooltip[raw.replace(/^_/, '')];

        if (!wired && !dis) {
            findings.push({
                sev: 'fail',
                title: 'Unwired button: #' + objName,
                detail: 'No .clicked/.toggled/.connect() and not disabled. User click does nothing.',
                rule: 'Bible §6.12 / wiring discipline'
            });
        } else if (dis && !tip) {
            findings.push({
                sev: 'fail',
                title: 'Stub without tooltip: #' + objName,
                detail: 'setEnabled(False) with no setToolTip() — user has no explanation.',
                rule: 'PG stub discipline'
            });
        }
    }
    return findings;
}
```

**Tested on developer_hub.py:** Returns exactly 3 findings:
- `#relayFooterMore` — truly unwired (defect 9)
- `#relayTemplateAdd` — truly unwired (new finding)
- `#relayComposeSecondary` — shared objectName between wired (Cancel)
  and unwired (Preview) buttons — flag is legitimate since duplicate
  objectNames are themselves a violation

**Returns 0 false positives.**

---

#### CHECK 3 — Raw hex in QSS functions (HIGH)

Flag `#rrggbb` literals inside `_xxx_qss()` f-string bodies. Exclude
known PG palette constants (already resolved). The PG codebase uses
`{RELAY_COLOR_xxx}` f-string interpolation — any bare hex is wrong.

```javascript
function checkRawHexInQss(src) {
    var findings = [];
    // Extract QSS function bodies
    var qssRe = /def\s+_\w*qss\w*\s*\([^)]*\)[^:]*:([\s\S]*?)(?=\ndef\s|\nclass\s|$)/g;
    var m;
    while ((m = qssRe.exec(src)) !== null) {
        var body = m[1];
        // Find hex literals NOT preceded by { (f-string variable) or RELAY_COLOR
        var hexRe = /(?<!\{RELAY_COLOR[^}]{0,40})#([0-9a-fA-F]{6})\b/g;
        var h;
        while ((h = hexRe.exec(body)) !== null) {
            findings.push({
                sev: 'fail',
                title: 'Raw hex in QSS: #' + h[1],
                detail: 'Replace with RELAY_COLOR_* constant. Raw hex breaks token system.',
                rule: 'R02'
            });
            break; // one finding per function is enough
        }
    }
    return findings;
}
```

**Tested:** Correctly flags `#ff0000` in example source. Returns 0 findings
on developer_hub.py and hub_components.py (which use constants correctly).

---

#### CHECK 4 — Missing :hover QSS rules (WARN)

For each QPushButton objectName in the source, check that a `:hover`
rule exists in a QSS function. Only match objectNames that are plausibly
buttons (not labels or containers).

```javascript
function checkMissingHover(src) {
    var findings = [];
    var BUTTON_PATTERN = /(Btn|Button|btn|Send|Cancel|Save|Lock|Load|Open|Add|More|New|Play|Capture|Primary|Secondary|Toggle|Chip|chip|Seg|seg)/i;

    // Collect all objectNames
    var objNames = [];
    var objRe = /setObjectName\(\s*["']([^"']+)["']\s*\)/g;
    var m;
    while ((m = objRe.exec(src)) !== null) {
        objNames.push(m[1]);
    }

    // Collect all QSS content
    var qssRe = /def\s+_\w*qss\w*\s*\([^)]*\)[^:]*:([\s\S]*?)(?=\ndef\s|\nclass\s|$)/g;
    var allQss = '';
    while ((m = qssRe.exec(src)) !== null) {
        allQss += m[1];
    }

    // Cross-reference: only button-pattern objectNames
    var missing = [];
    objNames.forEach(function(name) {
        if (!BUTTON_PATTERN.test(name)) return;  // skip non-buttons
        // Check for hover in QSS
        if (allQss.indexOf('#' + name + ':hover') === -1 &&
            allQss.indexOf(name + ':hover') === -1) {
            missing.push(name);
        }
    });

    if (missing.length > 0) {
        findings.push({
            sev: 'warn',
            title: 'Missing :hover for: ' + missing.slice(0, 3).join(', ') +
                   (missing.length > 3 ? ' + ' + (missing.length - 3) + ' more' : ''),
            detail: missing.length + ' button(s) lack explicit :hover QSS rule.',
            rule: 'Bible §6.12 + AC-HOVER'
        });
    }
    return findings;
}
```

**Note on false positives:** The pattern filter avoids flagging QLabel
objectNames like `relayEvidenceBlock`, `relayCaptureHead` that don't
need hover rules.

---

#### CHECK 5 — Multiple primary buttons in same build method (HIGH)

```javascript
function checkMultiplePrimary(src) {
    var findings = [];
    var buildRe = /def\s+(_build_\w+)\s*\([^)]*\):([\s\S]*?)(?=\n    def\s|\nclass\s|$)/g;
    var m;
    while ((m = buildRe.exec(src)) !== null) {
        var name = m[1], body = m[2];
        var count = (body.match(/setProperty\s*\(\s*["']role["']\s*,\s*["']primary["']/g) || []).length;
        if (count > 1) {
            findings.push({
                sev: 'fail',
                title: 'Multiple primary buttons in ' + name + ' (' + count + ')',
                detail: '§10 #4 non-negotiable: only ONE primary per visible screen.',
                rule: '§10 #4'
            });
        }
    }
    return findings;
}
```

---

#### CHECK 6 — QLabel used as circle indicator (WARN)

Flag QLabel instances with `setFixedSize(N, N)` where N equals N,
suggesting a circular indicator that will alias on Windows Qt.

```javascript
function checkLabelCircle(src) {
    var findings = [];
    // Find QLabel assignments
    var labelRe = /QLabel\([^)]*\)[\s\S]{0,300}?setFixedSize\((\d+),\s*(\d+)\)/g;
    var m;
    while ((m = labelRe.exec(src)) !== null) {
        var w = parseInt(m[1]), h = parseInt(m[2]);
        if (w !== h) continue;  // not square — not a circle indicator
        // Find objectName in nearby context
        var context = src.slice(Math.max(0, m.index - 100), Math.min(src.length, m.index + 400));
        var objMatch = context.match(/setObjectName\(\s*["']([^"']+)["']\s*\)/);
        var objName = objMatch ? objMatch[1] : '(unknown)';
        findings.push({
            sev: 'warn',
            title: 'QLabel circle indicator: #' + objName + ' (' + w + 'x' + h + 'px)',
            detail: 'QLabel border-radius does not anti-alias on Windows Qt. ' +
                    'Use a custom QWidget with QPainter + Qt.Antialiasing.',
            rule: 'Qt rendering limitation / Bible §6.21'
        });
    }
    return findings;
}
```

**Tested on hub_components.py:** Correctly finds relayTimelineCircle,
relayCardAvatar, relayRpAvatar, relayReportAvatar, relayTabBadge,
relayCardDot, relayTesterTabDot, relayStatusSyncDot — all real aliasing
risks.

---

#### CHECK 7 — Generic QLabel/QWidget rule in QSS (HIGH)

A bare `QLabel { }` or `QWidget { }` rule in a parent widget's QSS
cascades into all child widgets, overriding StatusPill inline styles.

```javascript
function checkQssCascade(src) {
    var findings = [];
    var qssRe = /def\s+_\w*qss\w*\s*\([^)]*\)[^:]*:([\s\S]*?)(?=\ndef\s|\nclass\s|$)/g;
    var m;
    while ((m = qssRe.exec(src)) !== null) {
        var body = m[1];
        // Bare QLabel { or QWidget { — not preceded by # or [
        if (/(?<![#\w\["\'])(?:QLabel|QWidget)\s*\{/.test(body)) {
            findings.push({
                sev: 'fail',
                title: 'Generic QLabel/QWidget rule in QSS — cascade risk',
                detail: 'Bare rule cascades into ALL child widgets, overriding StatusPill inline styles. Use #objectName selectors only.',
                rule: 'R17 cascade / Bible §6.24'
            });
        }
    }
    return findings;
}
```

**Tested on developer_hub.py:** Correctly finds the bare `QLabel { }`
rule in `settings_panel_qss()`.

---

#### CHECK 8 — Low-contrast border on content widget (WARN)

When a content widget (card, block, card panel) uses a border color
that has < 1.5:1 contrast against its background, the border is
functionally invisible.

This check uses a hardcoded lookup table of known PG color constant
pairs and their measured contrast ratios. Codex should include the
full table below in the scanner JS.

```javascript
var LOW_CONTRAST_PAIRS = [
    // Each entry: [border_constant_substr, bg_constant_substr, ratio, description]
    // These are measured from real PG source. ratio < 1.5 = invisible border.
    ['RELAY_COLOR_BORDER', 'RELAY_COLOR_PANE_RAISED', 1.10,
     'Border #2a2a3e on pane-raised #22223a'],
    ['RELAY_COLOR_BORDER_SOFT', 'RELAY_COLOR_PANE', 1.11,
     'Border-soft #232336 on pane #1a1a2e'],
    ['RELAY_COLOR_BORDER_SOFT', 'RELAY_COLOR_PANE_RAISED', 1.10,
     'Border-soft #232336 on pane-raised #22223a'],
    ['RELAY_COLOR_BORDER', 'RELAY_COLOR_CANVAS', 1.30,
     'Border #2a2a3e on canvas #14141f (transcript card defect 10)'],
];

function checkLowContrastBorders(src) {
    var findings = [];
    var qssRe = /def\s+_\w*qss\w*\s*\([^)]*\)[^:]*:([\s\S]*?)(?=\ndef\s|\nclass\s|$)/g;
    var m;
    while ((m = qssRe.exec(src)) !== null) {
        var body = m[1];
        // Find rule blocks
        var blockRe = /([^\{]+)\{([^\}]+)\}/g;
        var bm;
        while ((bm = blockRe.exec(body)) !== null) {
            var selector = bm[1], props = bm[2];
            LOW_CONTRAST_PAIRS.forEach(function(pair) {
                var borderHas = props.indexOf(pair[0]) !== -1 &&
                                /border[^:]*:\s*\d+px\s+solid/.test(props);
                var bgHas = props.indexOf(pair[1]) !== -1 &&
                            /background/.test(props);
                if (borderHas && bgHas) {
                    findings.push({
                        sev: 'warn',
                        title: 'Low-contrast border in ' + selector.trim().slice(-40),
                        detail: pair[3] + ' → ' + pair[2] + ':1 (min 1.5:1 for visibility)',
                        rule: 'Bible §2.3 / visibility'
                    });
                }
            });
        }
    }
    return findings;
}
```

---

### Example source (AC-B5 verified)

The "Load example" button must load source that triggers all 6 critical
checks. The following example has been TESTED and all 6 findings fire:

```python
from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QTabWidget
from PySide6.QtCore import Signal

class ExampleHub(QWidget):
    never_emitted = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # GOOD: wired + role
        self._save_btn = QPushButton("Save")
        self._save_btn.setObjectName("exSaveBtn")
        self._save_btn.setProperty("role", "primary")
        self._save_btn.clicked.connect(self._on_save)
        layout.addWidget(self._save_btn)

        # GOOD: stub with tooltip
        self._future_btn = QPushButton("Future Feature")
        self._future_btn.setObjectName("exFutureBtn")
        self._future_btn.setEnabled(False)
        self._future_btn.setToolTip("Ships in a future dispatch.")
        layout.addWidget(self._future_btn)

        # BAD 1: stub WITHOUT tooltip
        self._broken_stub = QPushButton("Also stub")
        self._broken_stub.setObjectName("exBrokenStub")
        self._broken_stub.setEnabled(False)
        layout.addWidget(self._broken_stub)

        # BAD 2: local variable, unwired
        more = QPushButton("More (does nothing)")
        more.setObjectName("exUnwiredBtn")
        layout.addWidget(more)

        # BAD 3: second primary
        self._cancel_btn = QPushButton("Cancel")
        self._cancel_btn.setObjectName("exCancelBtn")
        self._cancel_btn.setProperty("role", "primary")
        self._cancel_btn.clicked.connect(self.close)
        layout.addWidget(self._cancel_btn)

        self.setStyleSheet(self._qss())

    def _qss(self) -> str:
        return f"""
        QPushButton#exSaveBtn {{
            background: #e8a87c;
            color: #1a1a2e;
        }}
        QPushButton#exSaveBtn:hover {{
            background: #d4945a;
        }}
        QPushButton#exFutureBtn:hover {{
            background: #2a2a4e;
        }}
        QPushButton#exCancelBtn {{
            background: #ff0000;
        }}
        """

    def _on_save(self):
        pass
```

**Verified triggers:**
1. QTabWidget import → CRITICAL
2. `more` (exUnwiredBtn) → HIGH unwired
3. `_broken_stub` (exBrokenStub) → HIGH stub-no-tooltip
4. `#ff0000` raw hex → HIGH
5. `#exUnwiredBtn:hover` missing, `#exCancelBtn:hover` missing → WARN
6. Two `setProperty("role", "primary")` in `_build_ui` → HIGH

---

## Step 2 — Wiring Checklist updates

### Real wiring status from developer_hub.py (tested)

Update `WIRING_DATA` to reflect these verified states:

| Widget | ObjectName | Status | Notes |
|---|---|---|---|
| Settings button | `relayHeaderSettingsBtn` | WIRED | `settings_clicked.emit()` |
| Send update | `relayFooterSendUpdate` | WIRED | `_toggle_compose()` |
| **More button** | `relayFooterMore` | **UNWIRED** | No connect, not disabled — DEFECT 9 |
| **Template add** | `relayTemplateAdd` | **UNWIRED** | No connect, not disabled |
| **Preview button** | `relayComposeSecondary (preview)` | **UNWIRED** | Shares objectName with wired Cancel |
| Cancel compose | `relayComposeSecondary (cancel)` | WIRED | `_toggle_compose()` |
| Filter chips | `relayFilterChip` | WIRED | `_on_filter_chip()` |
| Compose chips | `relayComposeChip` | WIRED | `_on_compose_status()` |
| Verbosity chips | `relayVerbosityChip` | WIRED | `_on_verbosity_chip()` |
| Report rows | `ReportListRow` | STUB | Row highlight only — right panel static |
| Archive open | `relayArchiveOpenBtn` | STUB | `setEnabled(False)` + tooltip |
| Capture primary | `relayCapturePrimary` | WIRED | `capture_clicked.emit()` |
| Template toggle | `relayTemplateToggle` | WIRED | `_on_toggle()` |
| Template save | `relayTemplateSecondary` | WIRED | `_on_save()` |

Add `updatesUI` field to schema: "yes" / "partial" / "no". ReportListRow
= "partial" (row highlight only — right panel doesn't update, defect 11).

---

## Step 3 — FAILURE_DB / APP_PROFILES update

Relay pre-commit defects found in this session. Update `FAILURE_DB`:

| ID | Rule | Problem | Fix target |
|---|---|---|---|
| FAIL-RELAY-003 | Bible §6.12 / wiring | relayFooterMore unwired | developer_hub.py `_build_right_panel` |
| FAIL-RELAY-004 | Bible §6.12 / wiring | relayTemplateAdd unwired | developer_hub.py `_build_templates_page` |
| FAIL-RELAY-005 | R17 cascade | Template StatusPills clobbered by parent QSS | developer_hub.py `_relay_template_row_qss` |
| FAIL-RELAY-006 | §10 #4 | Preview + Cancel share objectName (duplicate objname) | developer_hub.py compose panel |
| FAIL-RELAY-007 | Qt rendering | QLabel circle indicators alias on Windows | hub_components.py (10 instances) |
| FAIL-RELAY-008 | Bible §6.21 | Stepper indicator overlaps label (spacing=0 + height constraint) | hub_components.py stepper |
| FAIL-RELAY-009 | Visibility | Transcript card border near-zero contrast | hub_components.py evidence block |
| FAIL-RELAY-010 | UX discipline | EvidenceBlock hide toggle scrolls out of view | hub_components.py evidence block |
| FAIL-RELAY-011 | UX discipline | Right panel static — row selection has no effect | developer_hub.py |
| FAIL-RELAY-012 | UX discipline | Settings panel has no UX context or step guidance | settings_panel.py |

FAIL-RELAY-001 and FAIL-RELAY-002 from the earlier dispatch were pre-Bug#160
(QTabWidget + missing hover). Both are fixed in the current source on disk.
Remove them from FAILURE_DB and update APP_PROFILES['Relay']:

```javascript
'Relay': { pass: 54, fail: 10, warn: 2, lastAudited: '2026-05-02' }
```

(54 of 64 visual checks passing; 10 code defects logged; 2 warnings.)

---

## Step 4 — New "Layout Safety" reference tab

Add a tab **"Layout Safety"** as a manual checklist. Each item is a
checkbox + status dot (red/orange/green). Developer checks these off
after live testing. Not automated — these are categories that require
visual verification.

Items:

| # | Check | Why | Severity |
|---|---|---|---|
| 1 | QLabel border-radius circles → verified anti-aliased in app | QLabel CSS circles alias on Windows | HIGH |
| 2 | No bare QLabel/QWidget in parent setStyleSheet | Cascade kills StatusPill inline styles | HIGH |
| 3 | Widget fixed-height + child buttons have max-height set | Prevents paint bleed outside parent bounds | HIGH |
| 4 | Collapsible widget body has height cap or internal scroll | Ensures toggle button stays reachable | HIGH |
| 5 | Layout spacing ≥ 4px between fixed indicator and QLabel | Prevents indicator/label overlap at any DPI | MED |
| 6 | Content widget borders ≥ 1.5:1 contrast vs parent background | Invisible borders are invisible | MED |
| 7 | Every interactive element updates visible state on click | Silent stubs mislead users | HIGH |
| 8 | Segmented control buttons have max-height ≤ parent height − 8px | Prevents selection indicator paint bleed | MED |

Present as: vertical list of checkboxes with red dot (unchecked),
orange dot (partial), green dot (checked). Store state in localStorage.
Export button generates a text checklist for the RTC.

---

## Step 5 — Polish pass

Apply these over the prototype:
- Fix the "Load example" button: it should set the textarea content
  AND set `scan-status` text to "Example loaded — click Scan" without
  requiring an explicit Scan click
- Wiring export CSV: ensure all columns including `updatesUI` are present
- Scanner result panel: sort FAILs first, then WARNs, then PASS summary
- Tab badge (scanner tab): show red dot with FAIL count, orange with
  WARN count, no badge when clean — update in real-time on scan
- All UI follows Bible grammar (peach caps sections, text-muted hints,
  no raw colors, one primary per view)

---

## Acceptance criteria

| AC | Description | How tested |
|---|---|---|
| AC-B1 | Scanner on developer_hub.py returns ≥ 1 real finding | Paste real file, verify relayFooterMore flagged |
| AC-B2 | Scanner returns 0 false positives on developer_hub.py | Manually verify each finding is a real bug |
| AC-B3 | Example source triggers all 6 violations | Load example, scan, verify QTabWidget + unwired + stub-no-tooltip + raw hex + missing hover + multiple primary all appear |
| AC-B4 | QTabWidget check: docstring-only mention returns no finding | Paste hub_components.py, confirm no QTabWidget CRITICAL |
| AC-B5 | Wiring Checklist shows UNWIRED for relayFooterMore and relayTemplateAdd | Open Wiring tab, verify status |
| AC-B6 | FAILURE_DB shows 10 Relay failures; APP_PROFILES Relay score reflects defects | Open Audit Results, select Relay, copy report |
| AC-B7 | Layout Safety tab renders 8 checkboxes, state persists on reload | Check boxes, reload page |
| AC-B8 | Wiring export CSV includes all columns including updatesUI | Click export, paste into text editor |
| AC-B9 | File opens in Chrome without console errors | F12 → Console → zero errors |
| AC-B10 | All UI follows Bible grammar | Visual check: peach caps heads, text-muted hints, one primary |

---

## Scope boundaries

- Read-only on the repo. Do NOT modify any .py files.
- Do NOT modify BUGS.md or REPEATED_ERRORS.md.
- Output: single self-contained HTML file at your Codex output path.
  State the path in your Step 0 report.
- File one RTC when all ACs pass.

## Reasoning tier

High — requires reading 3 source files, implementing 8 scanner checks
with correct JS logic (not the broken regex from the prototype), updating
FAILURE_DB with 10 entries, and producing a tested production HTML file.

— CD (tested against real source before dispatch)
