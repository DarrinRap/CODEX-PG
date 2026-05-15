---
schema_version: 1
message_id: 20260512_070000_CLAUDE_to_CODEX_relay_full_ba_and_validation_audit
in_reply_to: null
thread_id: RELAY-FULL-AUDIT-S163
from: CLAUDE
to: CODEX
date: 2026-05-12T07:00:00-07:00
subject: DISPATCH — Full BA review + full functional validation of Relay — detailed actionable report
status: active
type: dispatch
priority: high
reasoning_tier: Extra-High
reasoning_note: Comprehensive cross-file audit requiring exhaustive code reading, rule application, and structured reporting across 20+ relay/ files. Quality of report determines downstream fix prioritization for M2 and M5. Do not skip files or truncate findings.
approval_boundary: report_only_no_code_changes
---

# Full Relay BA Review + Functional Validation

Codex,

Darrin has directed a full Bible Audit (BA) review and full functional
validation of the entire `relay/` module. This is a read-only audit.
No code changes. Deliver an exquisitely detailed, actionable report.

**Reasoning tier: Extra-High.** This report will drive fix prioritization
for M2 (Adam retry) and M5 (Rebecca commercial onboarding). Every finding
must be specific, traceable to a file + line, and carry a severity and
recommended action.

---

## Scope

### Files to audit (read every one completely)

**Core relay module:**
- `relay/settings_panel.py`
- `relay/developer_hub.py`
- `relay/hub_components.py`
- `relay/setup_wizard.py`
- `relay/relay_window.py`
- `relay/invite_manager.py`
- `relay/dropbox_relay.py`
- `relay/review_screen.py`
- `relay/tester_hub.py`
- `relay/sent_model.py`
- `relay/report_model.py`
- `relay/active_capture.py`
- `relay/active_capture_screen.py`
- `relay/inbox_poller.py`
- `relay/package_writer.py`
- `relay/status_update_writer.py`
- `relay/bugs_md_writer.py`
- `relay/bug_capture_preview.py`
- `relay/phi_gate.py`
- `relay/transcription.py`
- `relay/diagnostics.py`
- `relay/_tokens.py`
- `relay/__init__.py`

**Supporting:**
- `styles.py` — for `RELAY_COLOR_*` token definitions
- `workflows/design/PG_DESIGN_BIBLE_v1.md` — canonical authority

**Reference (known open bugs — cross-check your findings against these):**
- `BUGS.md` entries #160, #161, #162, #165, #166, #171, #173, #174, #175,
  #177, #185, #186, #190, #195, #201, #316, #318, #319, #321

---

## Part 1 — Bible Audit (BA)

Apply every applicable BA rule from `PG_DESIGN_BIBLE_v1.md`. For each
violation found, report:

```
[RXX] File: relay/foo.py  Line: NNN
Violation: <exact description of what is wrong>
Current code: <the offending line or block>
Required fix: <what it should be — specific token, value, or pattern>
Severity: BLOCK | WARN
```

### Rules to apply (non-exhaustive — apply ALL that are relevant)

**Color tokens (R01, R02):**
- R01: Forbidden light-color literals (`white`, `#fff`, `#ffffff`, etc.)
  appearing outside token definition files.
- R02: Hardcoded hex that is NOT a canonical RELAY_COLOR_* / palette token.
  Check every QSS string, every `setStyleSheet`, every `QPalette` call.
  Cross-reference every hex found against `styles.py` RELAY_COLOR_* constants.

**Spacing and sizing (R04, R16, R18):**
- R04: Off-scale spacing values. Bible-canonical spacing: 4, 8, 12, 16, 24px.
  Flag anything else used as margin/padding/gap.
- R16: `setMinimumSize` / `setFixedSize` calls missing a §13 derivation
  comment explaining the value.
- R18: Off-scale border-radius values. Canonical: 2, 4, 6, 8px.

**Typography (R05a, R05b, R06):**
- R05a: Off-scale point sizes (anything not in the canonical type scale).
- R05b: Off-scale font-size px values.
- R06: Forbidden font families (anything outside `"Cascadia Mono"`,
  `"Consolas"`, `"Segoe UI"`, the monospace stack).

**Inline styles (R17):**
- R17: `setStyleSheet(...)` calls on individual widgets inside `__init__`
  or layout builders instead of class-level QSS. Flag each one.

**Hover states (Bible §6.12):**
- Every `QPushButton` must have an explicit `:hover` QSS rule.
- Every `QPushButton#RelayPrimary:hover` must darken (`RELAY_COLOR_ACCENT_HOVER`,
  not `RELAY_COLOR_ACCENT`).
- Every secondary button `:hover` must show `RELAY_COLOR_PANE_SELECTED` bg +
  `RELAY_COLOR_ACCENT` border + `RELAY_COLOR_ACCENT` text.
- Report every button objectName that has no `:hover` rule.

**Tab strip (Bible §6.13 / AC-TABS):**
- QTabBar inactive tabs must match chrome background — no dark box artifact.
- If `QTabBar` is used anywhere in relay, check for the `QTabBar::tab`
  background rule. Note: `developer_hub.py` intentionally avoids QTabWidget
  (per docstring) — verify this holds.

**Button grammar (Bible §6.14):**
- Exactly one primary action per screen.
- Module header toggles use chip grammar (accent-soft bg, accent-border border).
- No solid accent-fill on toggles (reads as primary button).

**Stub buttons (Bible §1.6):**
- Every non-functional / not-yet-wired button must be `setEnabled(False)`
  with a descriptive tooltip.
- Report every button that has a `clicked` signal but no connected slot, OR
  no `clicked` connection at all (silent dead click).

**Scrollbar (Bible §14.3):**
- Custom scrollbar QSS required in dark theme. Check whether QScrollArea
  children have scrollbar QSS or inherit it.

**WA_StyledBackground (Bible §14.1):**
- Every QWidget subclass with a background QSS rule must call
  `setAttribute(Qt.WA_StyledBackground, True)`.

**Status pills / badges (Bible §6.24):**
- Pills must be `QLabel`, not `QPushButton`.
- Status pill colors: RECEIVED must have a color fill (currently #174 — verify).
- Badge/pill border-radius: canonical pill = fully rounded (height/2).

**ESC key (Bible §7.5 amendment #4):**
- Top-level module windows must close on ESC.
- Verify `relay_window.py` has ESC wired (currently #195 — verify current state).

---

## Part 2 — Functional Validation

For every major Relay surface, assess: implemented, stubbed, broken, or missing.
Be specific about which slots are connected and which are dead.

### 2.1 Settings panel (`settings_panel.py`)

For each button and control:
- `+ Add Tester` button: connected to slot? Slot does what?
- Confirmation panel buttons (Copy invite text / Open in email / Done): wired?
- Revoke button per tester row: wired?
- Section A (Dropbox connect/reconnect): auth flow wired end-to-end?
- Section C (Failed send retry): implemented or stub?
- Any other buttons: connected?

### 2.2 Developer hub (`developer_hub.py`)

For each tab page:

**All Reports tab:**
- Report rows render?
- Right panel (stepper, status pane, evidence block, BUGS.md draft card): implemented?
- "Capture to BUGS.md" primary button: wired?
- "Send update" → compose panel: wired?
- Compose panel (Preview / Send / Cancel): which are wired?
- Is the report list dark-themed? Does it fill the window height?
- Filter pills (All / Unread / Pending / Captured): wired?

**By Tester tab:**
- Tester list renders?
- By-tester accordion: implemented?

**Sent tab:**
- Background color: dark or white/light?
- Does it have any non-empty state design?
- Content renders?

**Templates tab:**
- Template list renders?
- "+ New template" button: wired or dead click?
- Edit/save/discard flow: wired?

**Archive tab:**
- Implemented? Backend wired (archive/restore/delete)?

### 2.3 Tester hub (`tester_hub.py`)

- Layout matches `relay_tester_v2.html` canonical mockup?
- "My Reports" tab: report list renders?
- Updates tab: content renders?
- "+ New report" button: wired?

### 2.4 Setup wizard (`setup_wizard.py`)

Walk through every screen:
- Screen 0 (Welcome/role): renders?
- Screen 1 (Dropbox auth): PKCE flow complete?
- Screen 2 (Invite code entry): wired? Validation fires?
- Screen 3 (Connecting/Hello): ack poll wired? Timeout path wired?
- Screen 4 (Done): renders?
- Error states (Code not recognised / No internet / Channel access / Ack timeout): all reachable?

### 2.5 Error surfaces

For every error string in `setup_wizard.py` (`ERROR_DROPBOX_CODE`,
`ERROR_NO_INTERNET`, `ERROR_CODE_NOT_RECOGNISED`, `ERROR_CHANNEL_ACCESS`,
`ERROR_ACK_TIMEOUT`):
- Where does each surface in the UI?
- Is the error displayed with a code or plain English only?
- Is any error logged to a file? (expect: no, pending #321)

For every `except Exception` or `except` block in `dropbox_relay.py`,
`invite_manager.py`, `settings_panel.py`, `setup_wizard.py`:
- Is the exception caught and logged, or swallowed silently?
- Is a user-facing error message shown?
- Is an error code displayed?

### 2.6 Auto-acknowledge

In `dropbox_relay.py` / `developer_hub.py`:
- `auto_acknowledge_setup_test`: implemented and wired?
- `auto_acknowledge_bug_report`: implemented and wired?
- Are acks written to the correct path?

---

## Part 3 — BUGS.md cross-check

For each open Relay bug listed below, report its **current actual status**
based on what you read in the code — not what BUGS.md says:

| Bug | Description | Your finding |
|---|---|---|
| #160 | Layout diverges from canonical mockups | |
| #161 | + New template button dead click | |
| #162 | Compose panel Preview button unwired | |
| #165 | Relay placeholder (detail TBD) | |
| #166 | Relay placeholder (detail TBD) | |
| #171 | Sent tab white background | |
| #173 | Relay Settings Bible violations (all-states mockup required) | |
| #174 | RECEIVED pill no color fill | |
| #175 | Stepper completed steps should be green | |
| #177 | Module header wasted space | |
| #185 | "Captured" filter pill clipped | |
| #186 | Report list doesn't fill window | |
| #190 | RelayWindow missing setObjectName | |
| #195 | ESC doesn't close Relay window | |
| #201 | 218 BA lint violations | |
| #316 | Setup too complex for non-technical users | |
| #318 | Name truncation (can't reproduce) | |

For each: Confirmed open / Confirmed fixed (cite commit) / Cannot determine.

---

## Part 4 — New findings not in BUGS.md

List any violations, broken surfaces, or missing behaviors you find that
are NOT already captured in the bugs listed above. For each:

```
NEW FINDING
File: relay/foo.py  Line: NNN
Description: <what's wrong>
Severity: Critical | High | Medium | Low
Recommended action: <specific fix>
BUGS.md candidate: yes / no
```

---

## Report format

Deliver a single structured markdown report to CD CLAUDE inbox. Sections:

```
# Relay Full BA + Validation Report
**Date:** YYYY-MM-DD  **Session:** 163  **Codex version:** (your instance)

## Executive Summary
- Total BA violations: N (BLOCK: X, WARN: Y)
- Functional: N surfaces fully wired / N stubbed / N broken
- New findings not in BUGS.md: N
- M2 blockers (must fix before Adam retry): list
- M5 blockers (must fix before Rebecca): list

## Part 1 — BA Violations
[Full findings, one per finding block]

## Part 2 — Functional Validation
[Per-surface: Implemented ✓ / Stubbed ⚠ / Broken ✗ / Missing ✗]

## Part 3 — BUGS.md Cross-check
[Table with current-actual-status per bug]

## Part 4 — New Findings
[New issues not in BUGS.md]

## Recommended fix order
[Priority-ordered list: M2 blockers first, then M5, then polish]
```

No truncation. No "see above". Every finding fully stated.

---

## Constraints

- **Read only.** Do not modify any file.
- **Do not write to CC inbox.** This is a Codex-only audit task.
- Write your report to **CD CLAUDE inbox**:
  `C:\panda-gallery\workflows\cc_mailbox\CLAUDE Inbox\`
- File naming: `YYYYMMDD_HHMMSS_CODEX_to_CLAUDE_relay_full_audit_report.md`
- No CC gate required for BA work.
- Do not wait for a separate greenlight — deliver the report when complete.

— CD
