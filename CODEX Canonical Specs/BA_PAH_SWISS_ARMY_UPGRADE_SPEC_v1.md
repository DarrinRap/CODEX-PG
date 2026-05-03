# BA + PAH Swiss Army Upgrade Spec v1

Generated: 2026-05-02
Owner: Codex
Scope: CODEX BA Applet v2 + PAH same-origin integration

## 1. Problem Statement

BA is useful as a static Design Bible source scanner, but it is not yet the definitive "what is wrong, how bad is it, who fixes it, and did the tool respond" cockpit. PAH is already the communication cockpit and should stay lean, but it needs a safe bridge that lets BA send fix requests through the existing PAH mailbox protocol.

Recent observed failures motivate this upgrade:

- BA reports can contradict themselves, such as a summary saying failures exist while the failure list says "None."
- Button/tool wiring issues recur across PAH, PC, Relay, and BA.
- Users cannot tell at a glance whether a button did anything unless the app gives timestamped feedback.
- Fix dispatch handoff is still too manual: BA can identify a problem, but sending it to CC/CD requires copy/paste and context reconstruction.
- Static-file BA cannot safely POST into PAH because PAH write routes are protected by same-origin cookie/origin rules.

## 2. Upgrade Goals

1. BA should catch common application failures before commit:
   - unwired active buttons;
   - active buttons with no visible feedback affordance;
   - disabled stubs without explanation;
   - hardcoded QSS colors;
   - duplicate/contradictory report summaries;
   - Design Bible visual/layout risks already covered by the existing scanner.

2. BA should provide clear visible feedback for every BA action:
   - button border/color pulse on activation;
   - one-line status with full date/time stamp;
   - persistent local run log for comparison across runs.

3. BA should dispatch fix work through PAH:
   - `SEND FIX TO CC` creates a PAH message on the Codex-to-Claude-Code route.
   - `SEND FIX TO CD` creates a PAH message on the Codex-to-Claude-Desktop route.
   - The generated message includes the relevant audit/report evidence and a required workflow: read report, write fix spec, perform two heavy reviews, implement, verify, and report.
   - If BA is opened as a local file and cannot reach protected PAH write APIs, it must fall back to a copy-ready message and tell the user to open BA through PAH.

4. PAH should serve BA under the same local origin:
   - `/ba-applet` serves `CODEX BA Applet v2/PG_Design_Bible_Audit_v2.html`.
   - Response sets the normal `pah_write_token` cookie.
   - No CORS broadening is introduced.

## 3. Non-Goals

- Do not weaken PAH write-token or origin checks.
- Do not edit `C:\panda-gallery`.
- Do not make BA responsible for actually modifying application source code.
- Do not replace PAH Inspector or PAH communication speed testing; BA may link/dispatch, but PAH remains the owner of runtime mailbox health.
- Do not claim runtime proof from static scanning alone.

## 4. Functional Requirements

### 4.1 BA Action Feedback Layer

Every BA button click must visibly respond.

Minimum behavior:

- clicked button receives a short-lived active border/color pulse;
- a global status line records action name and full timestamp;
- important actions also update a nearby status element;
- each action writes an entry to the BA local run log.

Acceptance:

- Clicking `Scan`, `Refresh`, `Copy Report`, `Export CSV`, `Run Feedback Audit`, `Analyze Report`, and dispatch buttons changes visible UI state.
- Local run log records timestamp, action, status, and detail.

### 4.2 BA Static Scanner Extension

Add an additional scanner rule for silent button feedback risk.

Heuristic:

- collect active `QPushButton` definitions already discovered by the scanner;
- ignore disabled buttons with tooltip;
- inspect each connected handler body where statically discoverable;
- warn if the handler lacks obvious visible feedback markers such as `setText`, `setToolTip`, `setProperty`, `setStyleSheet`, `status`, `notice`, `toast`, `render`, `update`, `reload`, `refresh`, `showMessage`, `QMessageBox`, `emit`, or app-specific visible-state calls.

Severity:

- `warn`, not `fail`, because static inspection cannot prove runtime feedback in PySide code.

Acceptance:

- Example source produces a feedback warning for handlers that are effectively silent.
- Existing scanner output includes the new rule without hiding prior rules.

### 4.3 BA Report Consistency Analyzer

Add a Report QA panel that accepts pasted audit/report text and flags contradictions.

Required checks:

- summary failure count greater than zero while Failures section says `None`;
- warnings count greater than zero while Warnings section says `None`;
- pass/fail/warn/total arithmetic mismatch;
- report says "All pass" while fail or warn counts are nonzero;
- missing generated timestamp or target.

Acceptance:

- The contradictory 99% report pattern is flagged.
- Analyzer returns dated result status and adds a run-log entry.

### 4.4 BA Fix Dispatch Center

Add a Dispatch Fix panel.

Required controls:

- route target buttons: `SEND FIX TO CC`, `SEND FIX TO CD`;
- generated subject;
- generated body preview;
- dispatch status with timestamp;
- copy fallback.

Generated message requirements:

- route:
  - CC: `codex_to_claude_code`;
  - CD: `codex_to_claude`;
- status: response/action request rather than passive info;
- subject identifies BA fix request and current report class;
- body includes:
  - source of evidence;
  - current BA report text or report analyzer summary;
  - instructions to write fix spec, perform two heavy reviews, implement, verify, and report;
  - boundary: do not edit outside the implicated app unless explicitly authorized.

Acceptance:

- When loaded from PAH `/ba-applet`, clicking either send button posts to `/api/create-message`.
- When loaded from file, BA does not pretend send succeeded; it copies the message and explains that PAH-hosted BA is required for direct dispatch.

### 4.5 BA Local Run Log

Add a Run Log panel.

Storage:

- localStorage key: `ba_upgrade_run_log_v1`;
- bounded to the latest 80 events.

Display:

- newest first;
- timestamp, action, status, detail;
- copy/export button.

Acceptance:

- Scan/report/analyzer/dispatch actions appear in log.
- Log survives page reload.

### 4.6 PAH BA Hosting Route

Add PAH GET route:

- `/ba-applet`
- `/ba-applet/`
- `/ba`
- `/ba/`

Behavior:

- serve BA HTML file if present;
- set `pah_write_token` cookie exactly as main PAH page does;
- return a clear local HTML error if BA file is missing.

Acceptance:

- `http://127.0.0.1:8765/ba-applet` opens BA.
- Same-origin BA can POST protected `/api/create-message` calls.

### 4.7 PAH UI Entry Point

Add a topbar action button for BA:

- label: `Bible Audit`;
- opens `/ba-applet` in a new tab/window;
- gives PAH notice with timestamp.

Acceptance:

- PAH smoke test sees the button and route token.

## 5. Security and Confirmation Boundaries

- BA dispatch buttons are user-initiated; implementation does not send anything automatically.
- No credential, payment, medical, legal, or telemetry data is collected.
- No CORS wildcard is allowed.
- PAH protected writes continue to require cookie/token and same-origin.
- File-loaded BA must not silently bypass PAH security.

## 6. Verification Plan

Required automated checks:

- `python -m py_compile CODEX_agent_hub.py`
- PAH smoke tests
- BA static checks via script or browser DOM probe:
  - new panels exist;
  - dispatch buttons exist;
  - scanner override exists;
  - report analyzer flags the known contradiction;
  - run log functions exist.

Required manual sanity:

- Open PAH, click `Bible Audit`, verify BA loads.
- Click `Run Feedback Audit`, verify timestamp/status and log row.
- Paste contradictory report into Report QA, verify warnings.
- Click dispatch button only when a real fix request should be sent.

## 7. Implementation Slice for v1

Implement the complete BA static/dispatch surface and PAH hosting route. Defer deeper browser automation of arbitrary Panda apps to a later v2 because it requires app-specific launch contracts and should not be hand-rolled inside a static HTML page.

