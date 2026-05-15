---
schema_version: 1
message_id: 20260508_CODEX_ba_r27_r28_r29_impl_spec
thread_id: BA-VELLUM-ANTIPATTERNS-v1
from: CODEX
to: CLAUDE
date: 2026-05-08T22:55:00-07:00
subject: SPEC - BA R27/R28/R29 implementation for CC
type: spec
priority: normal
tier: Medium
---

# SPEC - BA R27/R28/R29 Implementation

Codex role note: this is a spec only. No production code should be committed by Codex. CC should implement the production changes in `scripts/ba_audit_runner.py` and `tests/test_ba_audit_runner.py`.

## Goal

Add three static BA rules to `pg_design_lint` supplemental scanning:

- R27 FAIL: `addStretch()` on the actual body layout of a `QScrollArea` with `setWidgetResizable(True)`.
- R28 WARN: tooltip text advertises unfinished, placeholder, or unwired functionality.
- R29 WARN: hardcoded count `QLabel(...0...)` has no clear runtime update path.

These rules should run for every BA target where `pg_design_lint` is enabled.

## File Scope

Production implementation:

- `scripts/ba_audit_runner.py`

Tests:

- `tests/test_ba_audit_runner.py`

No Vellum application files should be changed as part of this BA-rules task.

## Integration Point

In `scripts/ba_audit_runner.py`, integrate the new checks inside the existing `lint_checks(target, files)` path after the existing `pg_design_lint` engine returns.

Required behavior:

1. Run existing `pg_design_lint.run_checks(...)`.
2. Run new supplemental Python AST checks for R27/R28/R29 against the same `files`.
3. If both existing lint engine violations and supplemental findings are empty, return the existing pass row.
4. If either has findings, append both sets into the returned `pg_design_lint` check list.
5. Supplemental IDs should continue the existing `BA-LINT-{slug(target.name)}-{seq:04d}` sequence after the existing lint violations.

Recommended function names:

- `pg_design_lint_antipattern_checks(target, files, start_seq=1)`
- `ast_call_name(node)`
- `ast_stringish(node)`
- `qscrollarea_stretch_findings(tree)`
- `tooltip_phrase_findings(tree)`
- `qlabel_count_findings(tree)`

Add `import ast` at the top of `ba_audit_runner.py`.

## R27 - QScrollArea Body Layout Has addStretch

### Output

Status: `fail`

Severity: `error`

Title: `R27 error`

Message:

`R27: addStretch() in a QScrollArea body layout suppresses the scrollbar. Remove addStretch() or use addSpacerItem(QSpacerItem(..., Minimum, Expanding)) only at the bottom of a non-scroll layout.`

Recommendation:

`Remove addStretch() from the scroll-area body layout or move spacer behavior outside the scroll body.`

Evidence line: the `addStretch(...)` call.

### Required Detection Algorithm

Use AST, not string search.

For each `FunctionDef` or `AsyncFunctionDef`:

1. Track variables that are `QScrollArea` instances:
   - `scroll = QScrollArea(...)`
   - `self._scroll = QScrollArea(...)`
2. Track scroll variables that call `.setWidgetResizable(True)`.
3. Track body widget variables passed to a resizable scroll:
   - `scroll.setWidget(body)`
   - `self._scroll.setWidget(self._body)`
4. Track layout variables that are attached to a body widget:
   - `layout = QVBoxLayout(body)`
   - `layout = QHBoxLayout(body)`
   - `body.setLayout(layout)`
   - same for `self._layout` / `self._body`
5. Emit R27 only when `.addStretch(...)` is called on a layout variable proven to be attached to the widget passed to `scroll.setWidget(...)`.

Order inside the method must not matter. A method should still be detected if `layout.addStretch(...)` appears before `scroll.setWidget(body)`, because AST collection can gather method facts before emitting findings.

Important false-positive guard:

- Do not flag `addStretch()` on inner row layouts, header layouts, status-row layouts, or annotation-row layouts unless that exact layout is the body layout attached to the scroll widget.
- This guard is required because `widgets.py` contains legitimate row-level stretches in a method that also contains a scroll area. The old broad same-method heuristic would falsely flag those.

### R27 Pseudocode

```text
for each method:
    qscroll_vars = vars assigned from QScrollArea(...)
    resizable_scrolls = qscroll_vars where var.setWidgetResizable(True)
    scroll_body_vars = body vars passed to resizable_scroll.setWidget(body)

    body_layout_vars = {}
    for layout assignment:
        if value is QVBoxLayout(body) or QHBoxLayout(body):
            if body in scroll_body_vars:
                body_layout_vars.add(layout_var)

    for call body.setLayout(layout):
        if body in scroll_body_vars:
            body_layout_vars.add(layout)

    for call layout.addStretch(...):
        if layout in body_layout_vars:
            emit R27 fail at addStretch line
```

Variable identity should support:

- local names: `body`, `layout`, `scroll`
- simple `self` attributes: `self._body`, `self._layout`, `self._scroll`

Represent both as normalized strings:

- `Name("body")` -> `body`
- `Attribute(Name("self"), "_body")` -> `self._body`

### R27 Known Limitations

- V1 can be same-method only. Cross-helper tracing is not required for this task unless CC can add it cleanly without weakening the false-positive guard.
- Dynamic aliases such as `widgets[0].setLayout(layout)` may be missed.
- The rule should prefer missing a deeply dynamic case over falsely flagging unrelated row-layout stretches as hard failures.

## R28 - Tooltip Contains Unimplemented Marker

### Output

Status: `warn`

Severity: `warning`

Title: `R28 warning`

Message:

`R28: Tooltip contains unimplemented-marker text ('<phrase>'). Either implement the feature or remove the control before shipping.`

Recommendation:

`Remove placeholder/stub wording from shipped tooltips, or hide the unfinished control.`

Evidence line: the `setToolTip(...)` call or constructor call containing `tooltip=`.

### Phrases

Case-insensitive:

- `phase 2`
- `phase 3`
- `phase 4`
- `not yet wired`
- `not wired`
- `todo`
- `stub`
- `coming soon`
- `placeholder`

### Required Detection Algorithm

Use AST and inspect string literal values:

1. Find calls where function name or attribute name is `setToolTip`.
2. Inspect the first positional argument if present.
3. Find any call keyword named `tooltip`.
4. Inspect that keyword value.
5. Convert supported string-like nodes to text:
   - `ast.Constant` string
   - `ast.JoinedStr` using literal pieces plus `{}` placeholders
   - string concatenation via `ast.BinOp(..., ast.Add, ...)` when both sides are string-like
6. Lowercase the text and search for each phrase.
7. Emit one R28 warning per tooltip call, using the first matching phrase.

### R28 Pseudocode

```text
for each ast.Call:
    candidates = []
    if call.func name is setToolTip and call.args:
        candidates.append(call.args[0])
    for keyword in call.keywords:
        if keyword.arg == "tooltip":
            candidates.append(keyword.value)

    for candidate in candidates:
        text = static_string_value(candidate)
        if text contains any phrase case-insensitively:
            emit R28 warn at call line with phrase
            break
```

### R28 Known Limitations

- Dynamic tooltip text built through variables or function calls is out of scope for V1.
- Comments and non-tooltip strings should not be scanned.

## R29 - Hardcoded Count QLabel Without Update Path

### Output

Status: `warn`

Severity: `warning`

Title: `R29 warning`

Message:

`R29: QLabel initialized with a hardcoded count ('0') and no setText() update path found. Store as self._<name> and call setText() when data changes.`

Recommendation:

`Store the count label on self and update it from the data refresh path, or replace the literal count with non-count empty-state copy.`

Evidence line: the `QLabel(...)` call.

### Required Detection Algorithm

Use AST, scoped per `ClassDef`.

Find `QLabel(...)` calls where the first argument is a static string-like value containing a count initialized to literal `0`.

Count-string examples to flag:

- `QLabel("CAPTURED  0")`
- `QLabel("Count: 0")`
- `QLabel("0 items")`
- `QLabel("Results 0")`

Do not flag:

- `QLabel("No items found")`
- `QLabel("")`
- `QLabel("Ready")`
- `QLabel("100%")` unless surrounded by count wording listed below

Count wording should include at least:

- `captured`
- `count`
- `items`
- `results`
- `errors`
- `warnings`
- `mockups`

Detection steps:

1. In each class, find `QLabel(...)` calls whose first argument matches a count-zero pattern.
2. If the call is assigned to a local variable only, emit R29. Local-only labels have no reliable update path.
3. If the call is directly nested with no assignment, emit R29. Example: `layout.addWidget(QLabel("Count: 0"))`.
4. If the call is assigned to `self.<attr>`, scan other methods in the same class for a call to `self.<attr>.setText(...)`.
5. If no external update exists, emit R29.
6. If an external update exists in another method, do not emit R29.

Same-method `setText` immediately after construction should not be treated as a data-refresh update path. The update path must be in a different method.

### R29 Pseudocode

```text
for each class:
    for each assignment or direct call containing QLabel(count_zero_text):
        if no assignment target:
            emit R29 at QLabel line
        elif target is local name:
            emit R29 at QLabel line
        elif target is self.attr:
            creation_method = method containing QLabel line
            if no other method calls self.attr.setText(...):
                emit R29 at QLabel line
```

### R29 Known Limitations

- V1 does not need full alias tracking from local variables to later `self` attributes.
- V1 does not need dataflow proof that `setText(...)` is called on every state change. It only proves that an update path exists.
- Module-level builder functions without a class are out of scope for V1 unless CC can add them cleanly.
- Formatted expressions inside f-strings do not need to be evaluated for V1. Literal f-string text may be scanned, but `{count}` or `{0}` expression evaluation is out of scope.

## Test Fixtures To Add

Add helper in `tests/test_ba_audit_runner.py`:

```python
def antipattern_checks_for(tmp_path, source):
    py_file = tmp_path / "fixture.py"
    py_file.write_text(source, encoding="utf-8")
    target = ba.AppTarget("Antipattern Fixture", (py_file,), lint=True, scanners=("pg_design_lint",))
    return ba.pg_design_lint_antipattern_checks(target, [py_file])
```

### R27 Positive - Body Layout addStretch

```python
def test_pg_design_lint_r27_flags_scroll_area_body_add_stretch(tmp_path):
    checks = antipattern_checks_for(
        tmp_path,
        '''
from PySide6.QtWidgets import QScrollArea, QWidget, QVBoxLayout

class Panel:
    def build(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        body = QWidget()
        layout = QVBoxLayout(body)
        layout.addStretch(1)
        scroll.setWidget(body)
        ''',
    )
    r27 = [check for check in checks if check["title"] == "R27 error"]
    assert [check["status"] for check in r27] == ["fail"]
    assert "suppresses the scrollbar" in r27[0]["message"]
```

### R27 Negative - No addStretch

```python
def test_pg_design_lint_r27_allows_scroll_area_without_add_stretch(tmp_path):
    checks = antipattern_checks_for(
        tmp_path,
        '''
from PySide6.QtWidgets import QScrollArea, QWidget, QVBoxLayout

class Panel:
    def build(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        body = QWidget()
        layout = QVBoxLayout(body)
        layout.addWidget(QWidget())
        scroll.setWidget(body)
        ''',
    )
    assert not any(check["title"] == "R27 error" for check in checks)
```

### R27 Negative - Inner Row Layout Stretch Is Allowed

```python
def test_pg_design_lint_r27_allows_inner_row_layout_stretch(tmp_path):
    checks = antipattern_checks_for(
        tmp_path,
        '''
from PySide6.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QHBoxLayout, QLabel

class Panel:
    def build(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        body = QWidget()
        body_layout = QVBoxLayout(body)
        row = QHBoxLayout()
        row.addWidget(QLabel("Status"))
        row.addStretch(1)
        body_layout.addLayout(row)
        scroll.setWidget(body)
        ''',
    )
    assert not any(check["title"] == "R27 error" for check in checks)
```

### R27 Positive - Body setLayout Pattern

```python
def test_pg_design_lint_r27_flags_body_set_layout_add_stretch(tmp_path):
    checks = antipattern_checks_for(
        tmp_path,
        '''
from PySide6.QtWidgets import QScrollArea, QWidget, QVBoxLayout

class Panel:
    def build(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        body = QWidget()
        layout = QVBoxLayout()
        body.setLayout(layout)
        scroll.setWidget(body)
        layout.addStretch(1)
        ''',
    )
    r27 = [check for check in checks if check["title"] == "R27 error"]
    assert [check["status"] for check in r27] == ["fail"]
```

### R28 Positive

```python
def test_pg_design_lint_r28_flags_unimplemented_tooltip_text(tmp_path):
    checks = antipattern_checks_for(
        tmp_path,
        '''
class Panel:
    def build(self, button):
        button.setToolTip("Phase 2 - not yet wired")
        ''',
    )
    r28 = [check for check in checks if check["title"] == "R28 warning"]
    assert [check["status"] for check in r28] == ["warn"]
    assert "phase 2" in r28[0]["message"]
```

### R28 Positive - tooltip Keyword

```python
def test_pg_design_lint_r28_flags_tooltip_keyword_text(tmp_path):
    checks = antipattern_checks_for(
        tmp_path,
        '''
class Panel:
    def build(self, factory):
        factory.button(text="Later", tooltip="Coming soon")
        ''',
    )
    r28 = [check for check in checks if check["title"] == "R28 warning"]
    assert [check["status"] for check in r28] == ["warn"]
    assert "coming soon" in r28[0]["message"]
```

### R28 Negative

```python
def test_pg_design_lint_r28_allows_normal_tooltip_text(tmp_path):
    checks = antipattern_checks_for(
        tmp_path,
        '''
class Panel:
    def build(self, button):
        button.setToolTip("Click to approve")
        ''',
    )
    assert not any(check["title"] == "R28 warning" for check in checks)
```

### R29 Positive - Local Hardcoded Count Label

```python
def test_pg_design_lint_r29_flags_local_hardcoded_count_label(tmp_path):
    checks = antipattern_checks_for(
        tmp_path,
        '''
from PySide6.QtWidgets import QLabel

class Panel:
    def __init__(self):
        cap_head = QLabel("CAPTURED  0")
        self.child = cap_head
        ''',
    )
    r29 = [check for check in checks if check["title"] == "R29 warning"]
    assert [check["status"] for check in r29] == ["warn"]
    assert "hardcoded count" in r29[0]["message"]
```

### R29 Positive - Nested Hardcoded Count Label

```python
def test_pg_design_lint_r29_flags_unassigned_hardcoded_count_label(tmp_path):
    checks = antipattern_checks_for(
        tmp_path,
        '''
from PySide6.QtWidgets import QLabel, QVBoxLayout

class Panel:
    def __init__(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Count: 0"))
        ''',
    )
    r29 = [check for check in checks if check["title"] == "R29 warning"]
    assert [check["status"] for check in r29] == ["warn"]
    assert "hardcoded count" in r29[0]["message"]
```

### R29 Positive - Same-method setText Is Not Enough

```python
def test_pg_design_lint_r29_flags_same_method_set_text_only(tmp_path):
    checks = antipattern_checks_for(
        tmp_path,
        '''
from PySide6.QtWidgets import QLabel

class Panel:
    def __init__(self):
        self._cap_head = QLabel("CAPTURED  0")
        self._cap_head.setText("CAPTURED  0")
        ''',
    )
    r29 = [check for check in checks if check["title"] == "R29 warning"]
    assert [check["status"] for check in r29] == ["warn"]
```

### R29 Negative - self Label Has External Update Path

```python
def test_pg_design_lint_r29_allows_self_label_with_update_path(tmp_path):
    checks = antipattern_checks_for(
        tmp_path,
        '''
from PySide6.QtWidgets import QLabel

class Panel:
    def __init__(self):
        self._cap_head = QLabel("CAPTURED  0")

    def refresh(self, count):
        self._cap_head.setText(f"CAPTURED  {count}")
        ''',
    )
    assert not any(check["title"] == "R29 warning" for check in checks)
```

### R29 Negative - Non-count Empty Label

```python
def test_pg_design_lint_r29_allows_non_count_empty_label(tmp_path):
    checks = antipattern_checks_for(
        tmp_path,
        '''
from PySide6.QtWidgets import QLabel

class Panel:
    def __init__(self):
        empty = QLabel("No items found")
        self.child = empty
        ''',
    )
    assert not any(check["title"] == "R29 warning" for check in checks)
```

## Validation Commands

CC should run:

```powershell
python -m py_compile scripts\ba_audit_runner.py
python -m pytest tests\test_ba_audit_runner.py -q
python -m pytest -q
python scripts\ba_audit_runner.py --app Vellum --summary
```

Expected BA result after implementation depends on whether Vellum fixes have already landed:

- Before Vellum fixes, R27/R28/R29 should reveal Vellum antipattern findings.
- After Vellum fixes, the refined R27 rule should not flag legitimate row-layout stretches in `vellum_approval/widgets.py`.

## Self-review Record

Pass 1: 3 issues fixed - clarified R27 is order-independent within a method; added R27 `body.setLayout(layout)` fixture; removed inconsistent R29 f-string constant-evaluation example and documented f-string expression limits.

Pass 2: 1 issue fixed - added R29 fixture proving same-method `setText(...)` is not enough to count as a refresh/update path.

Pass 3: 1 issue fixed - replaced pending self-review placeholder with this completed review record.

Pass 4: 0 significant issues fixed - required sections, expected output strings, fixtures, limitations, and no unresolved placeholders verified.
