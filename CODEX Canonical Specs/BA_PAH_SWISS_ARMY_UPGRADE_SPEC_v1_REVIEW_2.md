# BA + PAH Swiss Army Upgrade Spec v1 - Deep Review 2

Generated: 2026-05-02
Reviewer: Codex
Lens: UX, ambiguity, conflict, and operational workflow

## Findings

1. BA needs one obvious workflow, not a wall of tools.

The spec's panel structure works if the first screen still shows audit results and the added panels are task-specific: Action Feedback, Report QA, Fix Dispatch, Run Log. This keeps the existing user path intact.

2. Dispatch wording must be strict enough to be useful.

"Fix this" is too vague. The generated dispatch must require the recipient to read the attached report, write a fix spec, perform two deep reviews, implement, verify, and report. The spec now includes those required body fields.

3. "SEND FIX CD" in the user request appears to be a typo/duplicate.

To avoid confusing UI, v1 should expose `SEND FIX TO CC` and `SEND FIX TO CD`. The generated body can still mention PAH routing. A third duplicate CD button would increase error chance without new capability.

4. Report consistency checks must be explainable.

If BA flags a contradiction, it should show exactly which text/counts conflict. Generic "bad report" warnings are not enough. The implementation should include details in each finding and in the dispatch body.

5. PAH topbar is already dense.

Adding `Bible Audit` to the topbar is useful, but it should be a normal secondary action and not another primary. The primary remains Mail. This prevents visual priority conflict.

6. Button feedback should be visual and textual.

Border pulse alone is too easy to miss. The global last-action strip and dated run log make the feedback auditable.

7. Copy fallback is mandatory.

When BA is opened from disk, sending through PAH may fail. The user should still receive a useful generated message rather than a dead error.

## Corrections Applied To Spec

- Kept only two dispatch buttons: CC and CD.
- Required full dated status after each action.
- Required copy fallback when direct send fails.
- Kept PAH button secondary.
- Required explicit contradiction descriptions.

## Final Recommendation

Implement v1 now. It is high leverage, low risk, and does not conflict with CC relay work because it stays inside `CODEX BA Applet v2` and PAH integration code. Do not attempt a universal runtime click harness until v2.

