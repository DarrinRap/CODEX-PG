# BA + PAH Swiss Army Upgrade Spec v1 - Deep Review 1

Generated: 2026-05-02
Reviewer: Codex
Lens: technical correctness, feasibility, testability

## Findings

1. Static BA cannot directly use PAH write APIs from `file://`.

This is not a bug in PAH; it is the correct security posture. PAH requires a same-origin write token/cookie. The spec resolves this by adding PAH-hosted BA at `/ba-applet` instead of broadening CORS. This is the correct fix.

2. "All buttons give feedback" cannot be proven for every external app from static BA alone.

PySide handlers can emit signals or trigger indirect state updates. BA should flag likely silent handlers, not fail them as conclusive defects. The spec correctly sets the new scanner rule to `warn`.

3. Dispatch buttons must not auto-send on page load or after analysis.

The spec keeps dispatch user-initiated only. This avoids accidental representational communication and keeps PAH as the action gate.

4. BA should avoid becoming a second PAH Inspector.

The spec keeps runtime mailbox health in PAH. BA focuses on design/wiring/report-quality checks and dispatch generation. This avoids duplicated state models.

5. The "Swiss army" phrase risks uncontrolled feature growth.

The spec defines a bounded v1 slice and explicitly defers app-specific browser automation. This prevents a brittle static HTML page from trying to become a universal test runner.

6. Run log privacy risk is low but should remain local.

The run log contains app diagnostic text and possibly pasted reports. localStorage is acceptable for a local-only tool, but export/dispatch remains user-triggered.

## Corrections Applied To Spec

- Added same-origin hosting route instead of CORS.
- Made action-feedback scanner warning severity.
- Added explicit non-goals for editing `C:\panda-gallery` and weakening PAH security.
- Added file-loaded BA fallback behavior.
- Added verification requirements for contradictory-report detection.

## Remaining Risk

BA still cannot conclusively prove that an arbitrary external app's click changes visible state. That requires a later app-specific browser or PySide runtime harness. The v1 implementation should be honest in labels and report wording.

