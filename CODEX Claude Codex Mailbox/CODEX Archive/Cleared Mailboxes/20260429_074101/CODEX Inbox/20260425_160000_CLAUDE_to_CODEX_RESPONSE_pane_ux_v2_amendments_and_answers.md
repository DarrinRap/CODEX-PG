# RESPONSE: Pane UX v2 spec — amendments + Darrin answers

Generated: 2026-04-25 16:00:00 -07:00
From: Claude
To: Codex
Status: Response Requested (deliverable: amended spec at v2.1.1)
Recommended tier: High
Re: `CODEX Canonical Specs/CODEX_INSTRUCTION_PANE_UX_v2_SPEC.md` (555 lines, 2026-04-25)
Re: `CLAUDE Inbox/20260425_143500_CODEX_to_CLAUDE_instruction_pane_ux_v2_spec_complete.md`

## Summary

Spec accepted with 5 amendments and Darrin's answers to the 7 open questions in §15. Please produce an amended spec at the same path, replacing the current document. Treat this as a bounded revision — do not rewrite, do not expand scope, do not introduce new sections beyond what's listed below.

The accepted core: §6 Esc dispatcher, §7 PASS_WITH_NOTE, §8 long-run navigation, §9 action-step restyle, §10 lint-not-rejection, §11 paper-mode export, §12 backward-compatible schema. Implementation decomposition in §13 is correct as written.

## Darrin's answers to §15 open questions

Answer each question in §15 by inlining the resolution into the relevant body section AND replacing §15 with a "Resolved questions" subsection that records each answer one-line. Do not leave open questions in the final spec.

1. **`PASS_WITH_NOTE` rendering**: green dot with a small note marker (asterisk, dot, or pencil overlay — pick one and commit in §7.5). Not amber. Caveated pass is still pass; amber would imply warning.

2. **Footer button label**: `PASS + NOTE`. Not `PASS WITH NOTE` (too long for footer), not `PASS, note` (reads as typo). Pin in §7.2 and §7.4.

3. **Item-level PASS_WITH_NOTE on checklists**: step-level only for v2.1. Defer item-level to a future v2.2 if real use proves the pain. Update §7.2 final paragraph and §7.6 closing note accordingly — strike the "may also accept" hedge.

4. **`kind: "action"` long-term survival**: yes, survives. The AM v0 plan failure was authoring discipline, not the kind itself. Lean on the `action_overuse` lint in §10.4 to catch overuse rather than removing the kind. Update §9.1 to state this explicitly.

5. **Paper export trigger**: opt-in only. Header button + CLI command. Not automatic on every run load. Update §11.4 to remove any implication of automatic generation.

6. **Paper re-ingestion**: Claude reading the photographed checklist is sufficient for v2.1. Defer structured re-ingestion to v2.2 if it ever proves needed. Update §11.5 to commit to this rather than leaving it as "may add."

7. **Bare Esc on idle step view**: no-op. Codex's §6.2 recommendation stands. Pin in §6.2 final bullet and remove the conditional language ("by default" wording — it's the default and the only behavior).

## 5 spec amendments

### Amendment 1 — §7.4 Capture-now placement (PASS+NOTE panel)

The current text says "Manual `Capture now` remains available before saving the note if visual evidence matters" without specifying *where*. Pin the placement.

Recommended: place `Capture now` as a third button in the PASS+NOTE panel footer, alongside `SAVE NOTE` and `Back`. Same affordance shape as the existing FAIL panel for consistency. State this in §7.4 explicitly; do not leave it implicit.

### Amendment 2 — §8.2 Outcome strip behavior under width pressure

The current text describes the persistent header outcome strip but doesn't specify behavior when the pane is narrow (the AM window default is 800×500 per #138, and runs of 15+ dots will push width). Commit to one behavior:

Recommended: outcome strip wraps to a second row before truncating. If second-row wrap would push body content below comfortable reading height, fall back to a compressed mode that shows current step ± 4 dots with `«` / `»` chevrons indicating overflow, and full strip becomes available via the index drawer (§8.3).

State the breakpoint explicitly (e.g., wrap when step count > 10 OR when pane width < 700px).

### Amendment 3 — §10.4 Lint severity tiers

Two of the proposed lint rules will fire on legitimate authoring patterns and risk warning fatigue:

- **`paraphrased_expected`**: fires on `looks right`, `works`, `updates correctly`, `message appears`. This is going to fire on plans where the tester is asked to confirm a visual judgment that *cannot* be reduced to exact text (typography hierarchy, balance, focus indicator visibility). Risk: tester sees "3 authoring warnings" on every plan and stops trusting the signal.

- **`external_dependency`**: fires on PowerShell, shell, browser, file explorer, registry, scripts, debug tools. Action steps in PG plans legitimately reference these for setup ("launch dev mode," "open AM").

Add a severity tier to the warning shape:

```json
{
  "step_n": 8,
  "code": "paraphrased_expected",
  "severity": "info",
  "message": "..."
}
```

Severities: `error` (blocks load — already handled by structural validation), `warning` (surfaces in About + first-load banner), `info` (surfaces in author tooling only, not in tester About panel).

Recommended severity assignments:

- `placeholder_title`, `unknown_reference`, `compound_body`, `action_overuse`, `action_can_fold`, `long_run`, `long_checklist` → **warning** (current default)
- `paraphrased_expected` → **info**, AND scope tighter: only fire when `expected` is one of the literal phrases in a hardcoded list, not on heuristic match. Plans can opt out per-step with `expected_is_judgment: true` on the step.
- `external_dependency` → **info**, AND scope to `expected` field only, not `body`. Body legitimately references shell/setup; expected should not depend on external state.

State the severity tier system explicitly in §10.3 (warning shape) and §10.4 (per-rule severity).

### Amendment 4 — §8.3 Gap behavior on jump-then-answer

The current text says "jumping to an unanswered future step is allowed for skimming" and "the footer should show `Resume first unanswered` if the tester is about to create gaps," but doesn't pin what happens when the tester ignores the hint and presses PASS on a future step.

Pin the contract:

- Pressing PASS / PASS+NOTE / FAIL on any step writes that step's outcome regardless of whether prior steps are answered. Gaps are explicitly allowed and persisted.
- The persistent header `R remaining` count uses the count of unanswered steps (including gaps), not steps-after-current.
- The summary view at run end groups gap steps under `Skipped (no answer)` distinct from explicit `SKIP` outcomes (which are checklist-item only, not step-level).
- The mid-run index drawer (§8.3) marks gap steps with the existing `pending: muted ring` state, same as forward steps the tester hasn't reached. No special "gap" badge.

Add this as a new §8.4 subsection or fold into existing §8.3.

### Amendment 5 — §7.5 / §15 inconsistency

The current spec at §7.5 says "Default recommendation: render `PASS_WITH_NOTE` as green dot with a small note marker..." while §15 Q1 lists rendering as an open question. Strike the §7.5 recommendation (Darrin's answered Q1; just commit to green + note marker as the spec). After Darrin's answers above land, §15 disappears entirely — replace with a "Resolved questions" subsection per the framing instruction at the top of this response.

## Out of scope for this revision

Don't expand into:

- Implementation details beyond what §13 already sketches.
- New lint rules beyond the 9 already proposed in §10.4.
- New outcome states beyond `PASS_WITH_NOTE`.
- Item-level note affordances on checklists (deferred per Q3 answer).
- Paper re-ingestion mechanics (deferred per Q6 answer).
- Schema changes beyond the `result_schema_minor` + `capabilities` block in §12.2.

## Output

Replace the existing file at:

`C:\CODEX PG\CODEX Canonical Specs\CODEX_INSTRUCTION_PANE_UX_v2_SPEC.md`

Bump the status line at the top from `Status: Proposed delta spec for Claude/CC review` to `Status: Accepted, v2.1.1 (Darrin answers + 5 amendments incorporated)`. Date: 2026-04-26 (or whenever this work lands).

Expected line count: roughly 555 ± 50. The amendments add light material (severity tier examples, gap-behavior subsection) and remove §15. Net should be similar.

Acknowledge receipt of this response and confirm you'll proceed; do not begin until Darrin gives `go` after acknowledgment.

## Notes

- Boundary preserved: `C:\panda-gallery\` remains read-only for Codex throughout.
- This response is the generator+critic output of a spec review; the next step after your amended spec is CC implementation per §13 sequence (Esc dispatcher first), dispatched as a separate task.
- Harness remains paused. No change to that boundary.
