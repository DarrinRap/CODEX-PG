# Bug #139 — AM gap rows collapse in production but not in isolation

**From:** Claude (desktop)
**To:** Codex
**Reasoning tier requested:** Extra-High
**Reason:** Deep Qt layout puzzle. Two failed fixes already. Need fresh eyes.

---

## TL;DR

`_GapRow` (custom QWidget) renders correctly in a 360×N container alone (probe1: rows 360x64..112). When wrapped in the production `_BugDetailScreen` hierarchy and given a smaller window, rows collapse to **size 342x0** and `gaps_inner` collapses to **360x26**. I cannot identify which layer is responsible.

I need you to read the code, read the probe data below, and tell me what's wrong. Don't guess — read the code and confirm.

---

## Repo

`C:\panda-gallery` — current HEAD `5436cc2` (v4.40 shipped). Bug #139 was added to BUGS.md in that commit.

## Files to read

1. `audit_module/audit_module_window.py`
   - `_GapRow` class (around lines 622–745 in the read I just did, search for `class _GapRow`)
   - `_BugDetailScreen.__init__` — especially the right_col gaps_block construction
   - `_AM_LOCAL_QSS` — the QSS at the top of the file
2. `instruction_pane.py` — `_ChecklistRow` is the canonical pattern `_GapRow` was modeled on
3. `bug139_probe.py` — probe1 (works correctly)
4. `bug139_probe2.py` — probe2 (reproduces the bug)
5. `bug139_probe_log.txt` and `bug139_probe2_log.txt` — geometry dumps

## Probe results

**Probe 1** — `_GapRow` directly inside `setFixedWidth(360)` container, window 420x600:
```
Row 0 design  size=360x112 OK
Row 1 scope   size=360x64  OK
Row 2 tech    size=360x80  OK
Row 3 test    size=360x64  OK
Row 4 desc    size=360x64  OK
```
Visual: all five rows render perfectly with kind tags, full label text, buttons.

**Probe 2** — full production hierarchy replica (`right_panel(360fixed) → right_col(QVBoxLayout) → triage section + mock_note + triage_btn + state_badge + result_block(110px) + addSpacing + gaps_block(QWidget) → gb(QVBoxLayout) → section_header + sep + spacing + gaps_inner(QWidget) → gaps_holder(QVBoxLayout) → 5 _GapRow + addStretch(1) + build_btn + move_row`), window 600x450:
```
Row 0 design  size=342x0
Row 1 scope   size=342x0
Row 2 tech    size=342x0
Row 3 test    size=342x0
Row 4 desc    size=342x0

gaps_block.size  = 360x52   visible=True
gaps_inner.size  = 360x26   visible=True
gaps_holder.count = 5
```

**Probe 2 with `right_col.addStretch(1)` removed** — same numbers (Row 0 size=342x0, gaps_inner.size=360x26). **Stretch is not the cause.**

In probe 2 with window 800x560 (matched AM default), the bug DOESN'T appear — `gaps_block=360x420`, `gaps_inner=360x394`, rows render. Bug only appears at 600x450.

## What I've ruled out

- ❌ `_GapRow` class itself is broken (probe1 disproves)
- ❌ `right_col.addStretch(1)` (removing it changes nothing)
- ❌ `setFixedWidth(360)` on right_panel (same in both probes)

## Suspicious observations

- Width drop 360 → 342 = exactly QGridLayout's contentsMargins(10, 8, 8, 8) horizontal sum (10+8=18). The grid's margins are eating row width.
- `gaps_inner.size = 360x26` — getting full 360 width but only 26px tall. Section header (~20px) + sep (1px) + spacing — that's all that fits in `gaps_block`'s 52px.
- `gaps_block` itself is 52px tall. Its parent `right_col` is squeezing it.
- **`_GapRow.setSizePolicy(Preferred, Maximum)`** — Maximum vertical means "I'll be at most my sizeHint, but I can be smaller." This may be letting Qt shrink the rows to zero when vertical space is contested.

## Hypothesis I'm leaning toward (but want you to check)

The combination of `(Preferred, Maximum)` size policy on `_GapRow` + `gaps_inner` having no size policy + nesting through 4 layers is causing Qt to compress rows to zero when the parent is space-constrained. The `_ChecklistRow` reference pattern in `instruction_pane.py` may use a different policy or wrap rows in a QScrollArea.

## What I need

1. Read `_ChecklistRow` (`instruction_pane.py`) — what's the EXACT size policy? Is it wrapped in a QScrollArea? Is the parent container constrained or unconstrained vertically?
2. Read `_GapRow` and `_BugDetailScreen.__init__` in `audit_module_window.py`. Find the actual root cause.
3. Propose the minimal fix. Confirm by predicting what probe2 numbers would become with the fix applied.
4. Don't guess. Read the code and tell me the answer.

## Constraints on the fix

- Must NOT change `_ChecklistRow` or `instruction_pane.py` — they work and are widely used
- Must keep AM's right panel at fixedWidth 360 (design constraint)
- Must keep gap rows hugging their content height (no fixed pixel heights on rows)
- Must work at window sizes 600x450 through whatever the user maximizes to
- Ideally a 1-line or small change in `_BugDetailScreen.__init__` or `_GapRow.__init__`

## Output format requested

```
ROOT CAUSE: <one sentence>
EVIDENCE: <which line of which file proves it>
FIX: <exact code change with file path and old → new>
WHY THIS FIX WORKS: <one paragraph>
WHAT PROBE2 WOULD SHOW AFTER FIX: <predicted numbers>
```

Thanks. I've been spinning on this for an hour. Need a clean diagnosis.
