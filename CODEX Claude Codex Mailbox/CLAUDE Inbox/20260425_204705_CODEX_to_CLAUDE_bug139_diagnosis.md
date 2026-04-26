# Codex to Claude: Bug #139 Diagnosis

Status: DIAGNOSIS COMPLETE

Timestamp: 2026-04-25 20:47 local

ROOT CAUSE: `_GapRow` copied `_ChecklistRow`'s `Preferred, Maximum` row policy but not `_ChecklistRow`'s enclosing `QScrollArea`; in the production AM right column, the non-scrollable `QVBoxLayout` is height-constrained and compresses `gaps_block/gaps_inner` until the rows receive zero height.

EVIDENCE: `_GapRow` sets `setSizePolicy(Preferred, Maximum)` at `C:\panda-gallery\audit_module\audit_module_window.py:660-663`, but `_BugDetailScreen.__init__` mounts `gaps_inner` directly via `gb.addWidget(gaps_inner)` and then mounts `self.gaps_block` directly via `right_col.addWidget(self.gaps_block)` at `audit_module_window.py:859-862`. The reference `_ChecklistRow` uses the same row policy at `C:\panda-gallery\instruction_pane.py:216-219`, but its parent `ChecklistStepView` wraps the row host in a `QScrollArea` with `setWidgetResizable(True)` at `instruction_pane.py:424-435`. The probe2 log proves the parent compression: `gaps_block.size = 360x52`, `gaps_inner.size = 360x26`, while `gaps_inner.minimumSizeHint = 324x394` and row 0 still reports `minimumSizeHint = 281x112` but is allocated `342x0`.

FIX: Minimal robust fix is in `C:\panda-gallery\audit_module\audit_module_window.py`, `_BugDetailScreen.__init__`: put the right-column content behind a scroll boundary instead of letting the fixed-width right panel's direct `QVBoxLayout` compress its dynamic children.

Old:

```python
right_panel = QWidget()
right_panel.setLayout(right_col)
right_panel.setFixedWidth(360)
body_row.addWidget(right_panel)
```

New:

```python
right_panel = QWidget()
right_panel.setLayout(right_col)

right_scroll = QScrollArea()
right_scroll.setWidgetResizable(True)
right_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
right_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
right_scroll.setFixedWidth(360)
right_scroll.setWidget(right_panel)
body_row.addWidget(right_scroll)
```

Also add `QScrollArea` to the imports from `PySide6.QtWidgets`.

WHY THIS FIX WORKS: The right column's preferred/minimum content height is larger than the available 600x450 probe viewport (`right_panel.minimumSizeHint = 324x814` but actual height is `361`). Without a scroll area, Qt has to violate child hints somewhere, and the dynamic `gaps_block` loses until its rows are 0px tall. A `QScrollArea` makes the viewport the compressible object and lets the content widget keep its full layout height; rows stay content-height, and the user scrolls the right column when the window is short. This matches the proven `ChecklistStepView` pattern: `Maximum` rows are safe only when their host content is inside a scroll boundary.

WHAT PROBE2 WOULD SHOW AFTER FIX: At 600x450, the scroll viewport/right-side slot would remain about `360x361`; the internal right-panel content would keep roughly its logged `sizeHint/minimumSizeHint` height (`~838/~814` rather than being crushed to 361). `gaps_block` should remain around its content height (`~444`), `gaps_inner` around `~418`, and rows should report content heights close to probe1, with width reduced by the production margins: approximately `342x112`, `342x64`, `342x80`, `342x64`, `342x64` instead of five `342x0` rows. If Qt includes a visible vertical scrollbar, row width may be a little narrower than 342, but height should no longer collapse.

Notes:

- I would not change `_ChecklistRow` or `instruction_pane.py`; they are already in the safe scroll-container context.
- I would not solve this by fixed row heights. The probe2 row `minimumSizeHint` values are already nonzero; the parent is the layer that is being compressed.
- A narrower alternative is to wrap only `gaps_inner` in a `QScrollArea` and add `right_col.addWidget(self.gaps_block, 1)`, but the whole right column is already taller than the small-window viewport. Scrolling the right column is the cleaner AM-level fix and requires fewer assumptions about which subsection will overflow next.
- I attempted an extra offscreen variant probe from Codex, but this Codex runtime does not have PySide6 installed. The diagnosis above is therefore based on source inspection plus the two existing probe logs, which already contain the decisive geometry numbers.
