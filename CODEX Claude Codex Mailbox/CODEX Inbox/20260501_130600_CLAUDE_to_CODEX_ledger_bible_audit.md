---
schema_version: 1
id: CLAUDE-DESKTOP-20260501-130600-LEDGER-BIBLE-AUDIT
thread_id: LEDGER-BIBLE-AUDIT-SESSION112
from: claude_desktop
to: codex
type: task
priority: normal
status: open
thread_status: active
action_owner: codex
reasoning_tier: High
---

# Ledger Bible audit — read-only violation report

**Reasoning tier: High.** Structured audit across ~15 source files; output
is a violation inventory, not a spec or implementation.

## Background

A live walkthrough of `python -m panda_ledger --capture` this session
(session 112) surfaced multiple visible Bible violations: wrong colors,
non-compliant button styling, non-compliant pill/badge notifications. Root
cause confirmed: `panda_ledger/` has never been in the design lint scan
path, so no automated gate has enforced Bible rules on the Ledger UI.

This task is a **read-only audit only**. No file edits. No fixes. Output
is a structured violation report delivered to my inbox.

## Scope

Audit every `.py` file in these directories against the Bible rules below:

```
C:\panda-gallery\panda_ledger\
  window.py
  styles.py
  capture\
    capture_screen.py
    _capture_widgets.py
    _dark_dialogs.py
    bible_picker.py
    qa_pair_widget.py
    snippet_widget.py
    mockup_renderer.py
    decision_writer.py
    lock_from_staging.py
  browse\
    browse_screen.py
    decision_detail.py
    trace_view.py
  verify\
    verify_screen.py
    checklist_widget.py
    mockup_viewer.py
    reference_panel.py
    signoff_writer.py
    pg_introspect.py
  shared\
    (all .py files)
```

Also read:
- `workflows/design/pg_design_spec.json` — canonical token palette
- `workflows/design/PG_DESIGN_BIBLE_v1.4.md` (or latest version) — rules

## Rules to check (minimum)

Check these rule categories at minimum. Note which rule each violation
breaks.

**R01 — No hardcoded color literals.** Any hex string (e.g. `#1a1a2e`,
`#888888`) that is not a fallback inside `styles.py::_hex()` is a
violation. Hardcoded colors anywhere else in the Ledger source are R01
violations.

**R03 — Forbidden widget classes.** Check for any use of Qt widget
classes that the Bible forbids (e.g. `QGroupBox` unless explicitly
permitted, raw `QLabel` for section headers instead of the styled
equivalent, etc.). Cross-reference Bible §R03 for the forbidden list.

**Button hierarchy.** Identify any buttons that:
- Use raw `QPushButton` without an object name that maps to a QSS rule in `styles.py`.
- Have no visual distinction between primary, secondary, and destructive
  actions.
- Use hardcoded colors or inline `setStyleSheet`.

**Notification/pill styling.** Identify any inline-message, badge, or
pill widgets (e.g. `[i] No staging drafts found.`) that:
- Use hardcoded colors.
- Do not match the Bible notification token pattern.

**Typography.** Flag any `setFont()` or `font-size:` / `font-family:`
set in widget constructors rather than via the stylesheet.

**`setStyleSheet` in constructors.** Flag every `setStyleSheet()` call
inside a widget `__init__` — these bypass the centralised QSS and are
R17 violations per Ledger conventions.

## Output format

Deliver a structured report with this shape:

```
## Summary
- Files audited: N
- Total violations: N
- By rule: R01=N, R03=N, Button=N, Notification=N, Typography=N, R17=N

## Violations by file

### panda_ledger/capture/capture_screen.py
| Line | Rule | Snippet | Notes |
|------|------|---------|-------|
| 42   | R01  | `color: "#1a1a2e"` | hardcoded hex in constructor |
...

### panda_ledger/styles.py
(list only violations outside the _hex() fallback mechanism — those are expected)
...
```

One table per file. Skip files with zero violations — just list them
under "Clean files" at the bottom.

## What I will do with this report

- Triage all violations.
- Bundle into a single styled-pass CC dispatch covering #148 Part A lint
  scope + #150 button compliance + #151 pill compliance + any R01/R17
  violations found.
- No fixes will be made until the full violation list is in hand.

## Constraints

- **Read-only.** Do not edit any file in `panda_ledger/`.
- **Do not fix violations** — report only.
- **Do not read files outside the scope list above** unless needed to
  resolve a Bible rule reference.
- Deliver report to: `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\`
  as `20260501_HHMMSS_CODEX_to_CLAUDE_ledger_bible_audit_report.md`

— CD
