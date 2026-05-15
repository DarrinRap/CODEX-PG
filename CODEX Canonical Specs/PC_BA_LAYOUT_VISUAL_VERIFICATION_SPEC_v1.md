# PC BA Layout + Visual Verification Spec v1

## 0. Purpose

PANDA Collaborator (PC) needs a repeatable way to answer Darrin's practical question: "Is this UI actually safe to bless, or did it only look okay in notes?"

This spec defines a BA-backed verification gate for PC. The goal is to move as much of the mechanical UI inspection as possible into BA and the existing `CODEX_ui_layout_applet.py`, while keeping one small human visual pass for judgment calls that automation cannot reliably make yet.

This is a spec only. It does not authorize production code edits, commits, staging, cleanup, or CC implementation. Any implementation must route through CD.

## 1. Current Problem

PC has a dedicated layout applet and substantial UI rules, but PC should not be called excellent merely because earlier notes sounded positive.

Known risks:

1. PC has active dirty files in `C:\CODEX PG\CODEX PANDA Collaborator\`, including the applet, production spec, tests, and `web/index.html`.
2. A prior BA pass exposed a scanner coverage problem: BA initially looked at the launcher/wrapper surface instead of the active HTML UI in `web/index.html`.
3. Many PC regressions are layout/visual issues: overlapping controls, clipped button text, hidden overflow, passive pills that behave like buttons, and readiness colors applied to identity markers.
4. Some failures are best found with a browser geometry probe, not static source scanning.
5. Some quality calls remain human-facing: visual hierarchy, polish, cramped composition, and whether a screen feels coherent in actual use.

## 2. Desired Outcome

BA should be able to produce an evidence-backed PC readiness verdict with three layers:

1. Static rule coverage: source-level checks for PC Bible rules and control semantics.
2. Runtime/browser geometry coverage: rendered checks across representative viewport widths and modal states.
3. Human visual-review prompt: a short checklist and screenshot packet for the final sanity pass.

The final PC status vocabulary should be:

- `excellent`: all BA/app-layout checks pass, required screenshots are current, and a human visual pass found no blocking polish or usability issue.
- `structurally_clean`: automated BA/app-layout checks pass and the screenshot packet is current, but the human visual pass has not been completed.
- `blocked`: one or more hard BA/app-layout failures exist.
- `unknown`: BA could not run required automated checks, screenshot evidence is missing/stale, or required evidence cannot be trusted.

## 3. Scope

In scope:

- PC app registration in BA must include both `panda_collaborator.py` and `web/index.html`.
- BA must invoke or mirror `CODEX_ui_layout_applet.py` for PC-specific layout checks.
- BA must report static and rendered PC checks separately.
- BA must verify the active UI surface, not only the launcher/wrapper.
- BA must generate or reference a screenshot packet for the human visual pass.
- BA must explicitly say when the human pass is still required.

Out of scope:

- No changes to PC product behavior in this spec.
- No restore automation, branch switching, git mutation, merge/rebase, deletion, or force push.
- No replacement of human review for subjective polish.
- No toaster/PAH notification changes.
- No CC implementation dispatch from Codex.

## 4. BA App Registration Requirements

PC registration must define:

- App name: `PANDA Collaborator`
- Static source files:
  - `C:\CODEX PG\CODEX PANDA Collaborator\panda_collaborator.py`
  - `C:\CODEX PG\CODEX PANDA Collaborator\web\index.html`
  - `C:\CODEX PG\CODEX PANDA Collaborator\PRODUCTION_SPEC.md`
- Applet command, executed with cwd `C:\CODEX PG\CODEX PANDA Collaborator`:
  - `python "C:\CODEX PG\CODEX PANDA Collaborator\CODEX_ui_layout_applet.py"`
- Unit test command, executed with cwd `C:\CODEX PG\CODEX PANDA Collaborator`:
  - `python -m unittest -v tests.test_panda_collaborator`
- Screenshot evidence source:
  - preferred: browser-driven capture command for PC states described in section 7
  - allowed bridge: an existing screenshot packet whose freshness can be proven against `web/index.html`
  - if neither exists, report `screenshots: missing` and overall status `unknown`.

BA must not silently fall back to only `panda_collaborator.py`. If `web/index.html` is missing from the scan packet, PC status must become `unknown` with a hard evidence message.

## 5. Static Rule Coverage

BA must check or consume applet checks for these PC-specific rules:

1. Action buttons are rectangular or lightly rounded, never pill-shaped.
2. Passive status chips may be pill-shaped but must not perform work when clicked.
3. Clickable controls must have visible action-button styling.
4. Green is reserved for enabled safe actions and positive completion states.
5. User identity colors, such as amber/cyan or test-mode Bob/Karen colors, must not be used as readiness/action colors.
6. Every action control has a click handler or intentionally disabled explanation.
7. Disabled future actions remain action-shaped, not passive chips.
8. Required setup controls are present: Setup Users / Handover Users, Register User 1, Register User 2, Browse controls, Scan repository, Create safe handoff.
9. Workflow panels show visible progression state: pending, ready, complete, or blocked.
10. Handover controls do not duplicate confusing user identity text in the visible button label.

Severity:

- Failing rules 1-7 are hard failures.
- Missing controls in rule 8 are hard failures.
- Rule 9 is hard failure when no progression state is visible; warning when state exists but is weak.
- Rule 10 is warning unless it causes clipping, overlap, or ambiguity, in which case it is hard failure.

## 6. Runtime / Rendered Geometry Coverage

The existing PC applet already contains a rendered browser probe using Node, Playwright, and a local Edge/Chrome executable. BA should either invoke that applet directly or adopt the same geometry checks into a BA runtime adapter.

Runtime checks must cover at least these states:

1. Main PC shell at desktop viewport.
2. Main PC shell at medium viewport.
3. Main PC shell at narrow viewport.
4. Setup wizard open.
5. User 1 and User 2 registration panels visible together.
6. User registration panels expanded.
7. Collaborator Hub cards visible.
8. Test mode active.
9. Emergency Pause visible.
10. Create Handoff panel with prerequisites incomplete and complete, if synthetic state allows.

Runtime probes must use an isolated synthetic state or restore any local PC settings files from a timestamped backup. A BA verification run must not leave PC in a different user/setup state than it found.

Minimum viewport widths:

- 1750 px
- 1366 px
- 1280 px
- 1100 px
- 940 px
- 820 px

Runtime geometry failures:

- Any horizontal document overflow is hard failure.
- Any button text clipping is hard failure.
- Any overlap between visible action controls and labels is hard failure.
- Any setup footer covering required fields is hard failure.
- Any modal action escaping modal bounds is hard failure.
- Any required panel inaccessible without a scrollable containing region is hard failure.
- Any applet/runtime dependency missing is `unknown`, not pass.

## 7. Screenshot Packet Requirement

BA should generate or reference a screenshot packet so the human visual pass is short and evidence-based.

Minimum packet:

1. `PC_MAIN_DESKTOP.png` — main shell at 1366 px or wider.
2. `PC_MAIN_NARROW.png` — main shell at 940 px or 820 px.
3. `PC_SETUP_USERS.png` — setup wizard with User 1 and User 2 visible.
4. `PC_USER2_REGISTER.png` — User 2 registration state.
5. `PC_TEST_MODE.png` — test mode with Bob/Karen identity treatment.
6. `PC_EMERGENCY_PAUSE.png` — emergency pause state.
7. `PC_CREATE_HANDOFF_READY.png` — create handoff state when prerequisites are synthetically satisfied, if available.

Each screenshot record must include:

- generated timestamp
- source commit or working tree marker
- viewport size
- synthetic state used
- command used to capture it
- whether the screenshot is current relative to the scanned files

If screenshots are missing or stale relative to `web/index.html`, PC status cannot be `excellent` or `structurally_clean`; the overall status must be `unknown` until fresh screenshot evidence exists. BA may still report the automated sub-result separately as `static: pass` or `runtime_geometry: pass`.

## 8. Human Visual Pass Boundary

BA should not claim it can judge every design-quality issue. It should instead produce a short visual pass checklist:

1. Does the main screen feel visually coherent and uncluttered?
2. Is the next action obvious in the left-to-right workflow?
3. Do buttons look like commands and chips look like information?
4. Are setup and handover flows understandable without reading developer notes?
5. Are identity colors helpful rather than distracting?
6. Do modal and narrow-screen states still feel intentional?
7. Is anything technically passing but awkward, cramped, or visually noisy?

A human reviewer must answer this checklist before PC can be marked `excellent`.

The visual pass evidence record must include:

- reviewer name or role
- review timestamp
- screenshot packet reviewed
- viewport(s) reviewed live, if any
- pass/fail verdict
- one-line note for each concern or explicit `no blocking visual concerns found`

## 9. BA Report Format

BA should report PC as:

```text
PANDA Collaborator
status: blocked | structurally_clean | excellent | unknown
static: pass/fail/unknown
runtime_geometry: pass/fail/unknown
screenshots: current/stale/missing
human_visual_pass: complete/pending
```

For each finding:

- rule id
- severity: fail/warn/unknown/evidenced
- source: static, applet, rendered, screenshot, human
- file path or screenshot path
- viewport/state when applicable
- one-line explanation
- recommended next action

Example:

```text
PC-GEOMETRY-001 fail rendered 940px setup_users
Setup footer overlaps User 2 required fields. Keep setup body scrollable or reduce footer height.
```

## 10. Integration Options

Option A — BA invokes the existing PC layout applet.

Pros:

- Lowest implementation risk.
- Reuses checks already tailored to PC.
- Avoids duplicating browser geometry logic.
- Works well as a near-term bridge.

Cons:

- Applet output must be normalized into BA finding schema.
- PC remains special-cased unless BA gets a general applet-adapter interface.

Option B — BA ports PC applet checks into `ba_audit_runner.py`.

Pros:

- Single BA implementation surface.
- Consistent finding schema.

Cons:

- Higher regression risk.
- Duplicates logic already working in the PC applet.
- Makes BA more app-specific.

Option C — BA defines a general `external_check` adapter.

Pros:

- Lets PC, PAH, and future applets plug into BA without hard-coding.
- Preserves app-specific knowledge in app-specific tools.
- Gives BA a unified schema and status vocabulary.

Cons:

- Requires a small adapter contract.
- Requires each external applet to emit machine-readable JSON or a stable parseable format.

Recommendation: Option C, with Option A as the first implementation. BA should invoke `CODEX_ui_layout_applet.py`, collect its output, and normalize failures into BA findings. Later, the PC applet should gain a JSON mode so BA does not parse human text.

## 11. External Check Contract

Each app-level layout checker should support:

```text
command: list[str]
cwd: path
timeout_seconds: int
output_mode: text | json
finding_map: app-specific parser or native JSON schema
required: true | false
```

Recommended JSON shape:

```json
{
  "app": "PANDA Collaborator",
  "check_id": "pc_layout_applet",
  "status": "pass",
  "findings": [
    {
      "id": "PC-GEOMETRY-001",
      "severity": "fail",
      "source": "rendered",
      "state": "setup_users",
      "viewport": "940x800",
      "message": "Setup footer overlaps registration content."
    }
  ],
  "evidence": {
    "screenshots": [],
    "commands": []
  }
}
```

BA must treat a required external check that cannot run as `unknown`, not pass.

## 12. Acceptance Criteria

The spec is implemented when:

- BA registers PC with both launcher and active HTML UI surface.
- BA invokes the PC layout applet or equivalent external check.
- Applet failures appear in BA report using normal BA finding severity.
- Missing applet dependencies produce `unknown`, not pass.
- Runtime geometry checks cover the minimum viewport/state matrix.
- Screenshot packet freshness is checked.
- BA distinguishes `structurally_clean` from `excellent`.
- Human visual pass remains an explicit final gate.
- The report can explain in plain language why PC is or is not blessable.

## 13. Non-Regression Rules

The BA/PC verification gate must never:

- mutate PC settings or user data without restoring them from a timestamped backup or using an isolated synthetic settings root;
- launch duplicate browser tabs during automated checks;
- require real user credentials, tokens, or patient data;
- mark screenshot-only comparison as sufficient for semantic behavior;
- suppress hard geometry failures because screenshots look acceptable;
- call PC excellent without a current screenshot packet and human visual pass.

## 14. Recommended Next Step

After Vellum MVP work clears the current project lane, CD should decide whether this narrow PC verification spec becomes:

1. A CC implementation dispatch for BA external-check support, or
2. A Codex-owned spec refinement paired with the broader PySide6 runtime BA framework spec. This PC spec should feed that framework; it should not fork a competing runtime-BA architecture.

Until then, PC can be described as promising but not fully blessed unless a fresh applet run and visual pass are performed and recorded.





