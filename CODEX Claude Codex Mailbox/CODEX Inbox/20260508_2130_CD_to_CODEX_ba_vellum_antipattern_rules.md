---
schema_version: 1
message_id: 20260508_2130_CD_to_CODEX_ba_vellum_antipattern_rules
thread_id: BA-VELLUM-ANTIPATTERNS-v1
from: CLAUDE
to: CODEX
date: 2026-05-08T21:30:00-07:00
subject: TASK -- BA: add 3 new static rules to catch Vellum-class UI bugs
type: task
priority: high
tier: High
---

# Task — BA new rules: Vellum antipattern detection

## Background

Vellum (am_mockup_review.py) shipped with 8 confirmed UX bugs that were not
caught by the existing BA or smoke suite. Three of those bugs represent
*antipatterns that are statically detectable* — they leave fingerprints in the
source code that a static rule can find. Codex should:

1. **Run the existing BA** (`scripts/ba_audit_runner.py`) against the Vellum
   applet files and report all findings in the RTC. Include the full BA output.
   Files to scan:
   - `workflows/design/applets/am_mockup_review.py`
   - `workflows/design/applets/vellum_approval/widgets.py`
   - `workflows/design/applets/vellum_approval/models.py`
   - `workflows/design/applets/vellum_approval/packet_io.py`
   - `workflows/design/applets/vellum_approval/split_view.py`
   - `workflows/design/applets/vellum_approval/validators.py`
   - `workflows/design/applets/vellum_approval/exporter.py`
   - `workflows/design/applets/vellum_approval/inbox.py`
   - `workflows/design/applets/vellum_approval/queueing.py`

2. **Add three new BA rules** (R27, R28, R29) as specified below, then re-run
   BA against the same files and include the updated output in the RTC.

CD will use the combined BA report to write the CC fix dispatch.
Do NOT send any dispatch or commit-go to CC — that is CD's job.

The three antipatterns are:

1. **QScrollArea body has addStretch** — kills scrolling silently
2. **Tooltip contains unimplemented-marker text** — shipped UI elements
   advertising unfinished functionality
3. **QLabel count widget hardcoded and never updated** — a label initialized
   to a literal "0" in __init__ with no update path

---

## Rule R27 — QScrollArea body has addStretch (FAIL)

### What it catches
When a QScrollArea is configured with `setWidgetResizable(True)` and its
body widget's QVBoxLayout (or QHBoxLayout) calls `addStretch()`, the stretch
forces the body to expand to exactly fill the viewport. The scroll area never
detects overflow and the scrollbar never appears. The content is silently
clipped.

### Pattern to detect
In the same method scope:
- A QScrollArea is created and `setWidgetResizable(True)` is called on it.
- A widget is created and passed to `scroll.setWidget(widget)`.
- In the same method, a layout is created for that widget and
  `layout.addStretch(...)` is called.

All three steps may appear in the same method body or in a helper called
directly. The key signal is: `addStretch` on a layout whose parent widget is
the `.setWidget()` argument of a QScrollArea.

### Simplified detection approach
Scan each Python method for:
1. Any call to `.setWidgetResizable(True)`.
2. Any call to `.addStretch(` in the same method body.

If both are present in the same method, flag as R27 FAIL with the line number
of `addStretch` and the message:
"R27: addStretch() in a QScrollArea body layout suppresses the scrollbar.
Remove addStretch() or use addSpacerItem(QSpacerItem(..., Minimum, Expanding))
only at the bottom of a non-scroll layout."

### Priority: FAIL (hard error, same as R17/R02)

---

## Rule R28 — Tooltip contains unimplemented-marker text (WARN)

### What it catches
Tooltip strings that contain phrases indicating the control is a placeholder or
stub. These phrases mark UI elements that are displayed to users but do not
function as labeled. They are production ships waiting to mislead users.

### Phrases to flag (case-insensitive)
- `phase 2`
- `phase 3`
- `phase 4`
- `not yet wired`
- `not wired`
- `todo`
- `stub`
- `coming soon`
- `placeholder`

### Pattern to detect
Scan for `setToolTip(` calls (or `.setToolTip(` calls) where the string
argument contains any of the above phrases.

Also scan for strings that are passed as the `tooltip` parameter in widget
constructors if the codebase uses that pattern.

### Flag format
R28 WARN at the line of the `setToolTip` call:
"R28: Tooltip contains unimplemented-marker text ('<phrase>'). Either implement
the feature or remove the control before shipping."

### Priority: WARN (not a hard FAIL, but must be visible in BA summary)

---

## Rule R29 — QLabel count widget hardcoded to literal '0' with no update path (WARN)

### What it catches
A QLabel initialized with a string containing a literal digit `0` as a count
(e.g. `"CAPTURED  0"`, `"0 items"`, `"Count: 0"`) inside `__init__` or a
builder method, where the same label is never referenced again in any other
method of the same class. This pattern indicates a count label that is set
once at construction and never updated — the count is permanently wrong after
the first data change.

### Pattern to detect
1. Find `QLabel("...")` or `QLabel(f"...")` calls where the string matches
   the pattern: contains one or more digits AND the digits represent a count
   value (surrounded by space, at start/end, or following a word like
   "captured", "count", "items", "results", "errors", "warnings").
2. If the label is assigned to a local variable only (not `self._something`),
   it cannot be updated — flag immediately.
3. If the label is assigned to `self._something`, check whether any other
   method of the class references `self._something` and calls `.setText(` on
   it. If no other method updates it, flag.

### Flag format
R29 WARN at the label creation line:
"R29: QLabel initialized with a hardcoded count ('0') and no setText() update
path found. Store as self._<name> and call setText() when data changes."

### Priority: WARN

---

## Implementation notes

### Where to add
`scripts/ba_audit_runner.py` — the existing runner handles R01–R26. Add
R27–R29 following the same pattern.

### Scope
Scan all Python files that the existing BA runner covers. Do NOT limit to
Vellum files only — these antipatterns can appear anywhere in the codebase.

### Test fixtures
Add test cases to `tests/test_ba_audit_runner.py`:
- R27: a small synthetic snippet with QScrollArea + setWidgetResizable + addStretch → expect FAIL
- R27 negative: QScrollArea + setWidgetResizable, NO addStretch → expect PASS
- R28: setToolTip("Phase 2 — not yet wired") → expect WARN
- R28 negative: setToolTip("Click to approve") → expect PASS
- R29: QLabel("CAPTURED  0") assigned to local only → expect WARN
- R29: QLabel("CAPTURED  0") assigned to self._cap_head, setText called elsewhere → expect PASS
- R29 negative: QLabel("No items found") (no count digit) → expect PASS

### Self-review
Perform 2 passes before filing RTC. Fix all findings inline.

### Hold gate
File RTC to CD before any commit. CD must issue commit-go.

— CD
