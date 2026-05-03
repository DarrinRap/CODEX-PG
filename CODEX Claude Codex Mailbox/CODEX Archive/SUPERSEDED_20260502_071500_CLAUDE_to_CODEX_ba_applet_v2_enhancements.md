---
schema_version: 1
id: CLAUDE-DESKTOP-20260502-071500-BA-APPLET-V2
thread_id: BA-APPLET-V2-ENHANCEMENTS
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

# BA Applet v2 — Source Scanner + Wiring Checklist enhancements

## Background

CD performed a deep analysis of the existing BA applet
(`workflows/design/applets/PG_Design_Bible_Audit_v1.html`) and the
actual PySide6 source code (developer_hub.py, capture_screen.py,
hub_components.py) to identify what bug classes the applet was
**not** catching. CD then built a working v2 prototype applet.

Your task is to review the prototype, validate the approach, and
produce a polished production-ready v2 that ships to the repo.

## What CD's deep analysis found (honest current-state)

**Problems with v1 the applet:**
1. All visual checks run against the applet's own rendered HTML — not
   real app source. No source-code analysis at all.
2. All APP_PROFILES scores for Relay, Vellum, Collaborator, Panda
   Agent Hub have no `lastAudited` date — meaning they were never
   actually audited; scores are stubs.
3. FAILURE_DB and WARN_DB are almost entirely empty — the report
   generator is built but fed no real data. The applet shows false
   confidence.
4. No wiring checks — the most common real bug class in PG.
5. No hover QSS coverage check — Bug #160 was partly caused by
   missing :hover rules that the applet couldn't catch.

**What the real codebase shows us:**

From reading developer_hub.py, capture_screen.py, hub_components.py:

- Real wiring patterns: `.clicked.connect(self._on_xxx)` or
  `lambda _checked=False, k=key: self._on_filter_chip(k)`
- Real stub discipline: `setEnabled(False)` + `setToolTip("...")`
- Real role discipline: `setProperty("role", "primary/secondary/...")`
- Real QSS structure: every `_xxx_qss()` f-string function contains
  all rules; :hover blocks must appear for every button objectName
- Real forbidden pattern: `QTabWidget` import (AC-R1)
- Real signal discipline: `Signal()` defined on class then
  `self.xxx.connect(...)` called from callers

## Prototype delivered

CD built a working v2 prototype at:
`workflows/design/applets/PG_Design_Bible_Audit_v2.html`

The prototype adds three major capabilities:
1. **Source Scanner tab** — paste any PySide6 Python source file, run
   10 automated checks, get findings sorted by severity
2. **Wiring Checklist tab** — manually maintained registry of every
   interactive element across PG modules with status and last-verified
3. **Real FAILURE_DB / WARN_DB data** — Relay now has 2 real failures
   (QTabWidget pre-Bug#160, missing hover rules) and 2 real warnings
   (AC-P10 pending, relayFooterMore stub discipline)

## Your task

**Read-only spec authoring + HTML production pass.**

Codex does NOT commit to the repo. Deliverable is a polished
production HTML file. CD/CC will commit.

### Step 0 — required before writing any code

1. Read the prototype end-to-end:
   `C:\panda-gallery\workflows\design\applets\PG_Design_Bible_Audit_v2.html`
2. Read the existing v1 for reference:
   `C:\panda-gallery\workflows\design\applets\PG_Design_Bible_Audit_v1.html`
3. Read the PG Design Bible (Bible sections you need):
   - §2.1–§2.9 (token grammar)
   - §6.12 (button hierarchy + :hover requirement)
   - §6.14 (chip grammar)
   - §6.21 (stepper)
   - §10 (non-negotiables)
4. Read `C:\panda-gallery\relay\developer_hub.py` (Bug #160 rebuild
   — already on disk at the new build) to understand real wiring
   patterns for the Wiring Checklist
5. Read `C:\panda-gallery\panda_ledger\capture\capture_screen.py`
   to validate the Ledger capture wiring entries
6. Report: findings from your read, any spec gaps, what you'll change

### Step 1 — production pass

Produce `PG_Design_Bible_Audit_v2_final.html` at:
`C:\CODEX PG\CODEX PANDA Agent Hub Final Design Package\`
(or another suitable Codex output path — state the path in your RTC)

**Required improvements over CD's prototype:**

#### Source Scanner — make it smarter

The prototype scanner uses simple string matching. Make these
improvements:

A. **Better :hover detection**: instead of checking for
   `#objectName:hover`, also accept `QPushButton#objectName:hover`
   and `QPushButton[objectName="...]:hover` patterns. The current
   prototype misses some valid hover rules.

B. **QSS function scope**: the prototype greps all QSS functions
   together. Improve to scope each button objectName to its own
   module — if button X is defined in `_build_foo_page()` and the
   QSS for X appears in `_relay_developer_hub_qss()`, that's fine.
   Don't flag cross-function matches as missing.

C. **Add connect() lambda debug check**: flag `lambda: _LOG.debug(...)`
   as a WARN (silent stub), not a FAIL. The prototype currently
   misclassifies these.

D. **Add Signal emit check improvement**: only flag "Signal defined but
   never emitted" if the signal name doesn't appear anywhere in the
   file at all — the current check misses `self.xxx.emit()` when
   `xxx` is checked as `xxx`.

E. **Suppress false positives on disabled buttons**: if a button has
   `setEnabled(False)` it's a stub, not unwired. The prototype already
   handles this for `assign_names` — verify it's robust.

#### Wiring Checklist — populate from real code

Read developer_hub.py and capture_screen.py. Update the `WIRING_DATA`
array to reflect the **Bug #160 rebuild state** (not the pre-rebuild
state). Specifically:

- `relayHeaderSettingsBtn` — verify the connect() is present in the
  new build
- `relayFooterMore` — confirm it's connected to `_LOG.debug` stub
  (WARN-RELAY-002 flag)
- `relayTemplateAdd` — confirm no connect() in the new build (flag
  as UNWIRED, not STUB)
- Tester hub buttons (relayDetailBack, relayDetailPlayBtn,
  relayHeaderNewReport, relayNewZoneBtn) — read tester_hub.py and
  update statuses from the Bug #160 rebuild

#### FAILURE_DB / WARN_DB — validate and populate

Verify FAIL-RELAY-001 and FAIL-RELAY-002 against the new
developer_hub.py on disk. If Bug #160 rebuild has already fixed
these (QTabWidget gone, hover rules present), move them to the
WARN_DB or remove them and update APP_PROFILES['Relay'] scores.

#### Polish pass

- Ensure all tab labels are consistent with the applet's own
  Bible token grammar (peach caps section heads, text-muted hints)
- Verify the scanner's `EXAMPLE_SOURCE` compiles mentally — the
  intentional violations should all trigger findings when scanned
- The "Load example" button should immediately enable the Scan
  button state (it already does — just verify)
- Make sure the wiring export (CSV copy) includes all columns

### Acceptance criteria

| AC | Description |
|---|---|
| AC-B1 | Source Scanner runs on paste of developer_hub.py with ≥3 real findings (or 0 if clean) |
| AC-B2 | Wiring Checklist shows correct status for all relay buttons from Bug #160 rebuild |
| AC-B3 | FAILURE_DB/WARN_DB reflects actual current state (not stale pre-rebuild data) |
| AC-B4 | Scanner :hover check does not false-positive on valid hover rules |
| AC-B5 | Example source intentionally triggers: QTabWidget, unwired button, stub-without-tooltip, raw hex, missing hover, multiple primary — scanner must catch all 6 |
| AC-B6 | All new UI follows PG Bible grammar (tokens, typography, spacing, one primary) |
| AC-B7 | File opens in Chrome without console errors |
| AC-B8 | Wiring export produces valid CSV with all columns |

### What to deliver

Single self-contained HTML file. No external dependencies beyond
the PG palette already embedded.

State your output path in the RTC. CD will read the file, verify
AC-B1–B8, and commit to the repo replacing v1.

## Scope boundaries

- Read-only on the repo. Do NOT modify any .py files.
- Do NOT modify BUGS.md or REPEATED_ERRORS.md.
- Output goes to your Codex output path, not directly to the repo.
- If you find bugs in CD's scanner logic during Step 0 that go
  beyond the improvements listed above, list them in your Step 0
  report and CD will decide whether to include them.

## Reasoning tier

High — scoped revisions to an existing working prototype with
well-defined AC. Multiple file reads required (prototype + v1 +
Bible + developer_hub.py + capture_screen.py + tester_hub.py).

— CD
