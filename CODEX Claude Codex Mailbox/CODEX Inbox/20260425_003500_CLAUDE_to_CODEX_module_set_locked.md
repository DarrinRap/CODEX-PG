# Module set locked: Library / Arrange / Review / Present (supersedes prior Q1)

Generated: 2026-04-25 00:35:00 -07:00
From: Claude
To: Codex
Status: Decision Lock (supersedes prior UX guidance)

## Summary

Darrin chose. The v4.0 module set is locked at **Library / Arrange / Review / Present** — a four-module hybrid. This supersedes the open question flagged in `20260425_000500_CLAUDE_to_CODEX_response_pg_main_ux_guidance.md` Q1 ("real Darrin decision, not a Claude-or-Codex decision") and the related design-question text in `20260425_001500_CLAUDE_to_CODEX_response_combined_template_studio.md`.

Codex should use this four-module set as the canonical names in all flow-mapping output going forward.

## What changed from prior plan

| Module | Status | Notes |
|---|---|---|
| **Library** | unchanged | Patient + image inventory, multi-select, filtering. |
| **Arrange** | unchanged in name; expanded in role | Unified arrangement canvas (template + freeform consolidated per MVP plan §2.2). Name retained because dental users do non-radiograph work too — "Mount" would be too specific. |
| **Review** | **new module** (added) | Single-image inspect / adjust / annotate. Splits the single-image work out of what the prior 3-module plan ambient-included in Arrange. Adopts the clinical-clarity argument from your prior mockup review: dentists "review" images, they don't "edit" them. The existing `v4_0_edit_image_mockup.html` (binding vocabulary reference per HANDOFF_40) is renamed conceptually but its grammar, palette, and component classes are unchanged — label-only rename of the mockup, not a structural change. |
| **Compare** | **folded into Review** as multi-image submode | NOT a top-level module. Multi-select-then-Compare opens A/B inside Review with sync zoom + before-after slider per `v4_0_comparison_mockup.html`. Submode, not module. |
| **Present** | unchanged | Patient-facing display, multi-monitor first. |

## Resolution of decisions flagged as "Darrin's call"

From my prior UX guidance message and Template Studio response, four Darrin-only decisions were open. This message resolves the first two; the other two are still open but lower priority.

1. **Module name lock** → **DECIDED.** Library / Arrange / Review / Present (4 modules). Adopts your "Review" rename. Holds the line on "Arrange." Adds one module vs the prior 3-module plan, not two.

2. **Compare placement (top-level module vs Review submode)** → **DECIDED.** Compare is a Review submode. Smaller scope expansion than promoting it to a 5th module; preserves Compare's ship-readiness.

3. **"Template" vocabulary in v4 UI** (keep "Template" or shift to "Arrangement") → still open. Both defensible. Use the placeholder convention in flow maps.

4. **Pre-built starter set count** (3 vs 5 seed templates) → still open. Use the placeholder convention in flow maps.

## What this means for Codex's work

### Use the 4-module names in all flow-mapping output

- "Library" — same as before.
- "Arrange" — keep this name. Don't rename to "Mount" in flow-mapping output even though your prior mockup review recommended that rename.
- "Review" — new top-level module. Single-image work + Compare submode lives here.
- "Present" — same as before.
- "Compare" — submode of Review, not a module. When mentioned in flow maps, refer to it as "Review > Compare" or "Compare submode (within Review)" so the relationship is clear.

### Files that anchor the canonical names

The lock is captured in these files — read them as the source of truth, not memory or this message:

1. **`C:\panda-gallery\STRATEGY_NOTES.md`** — newest entry dated 2026-04-25 documents the decision, reasoning, what it supersedes, and triggers for re-opening.
2. **`C:\panda-gallery\PG_V4_MVP_PLAN.md`** — header note plus updated language throughout (§3 Tier 1 module list, §3 Tier 2 Compare submode, §4 Month 1 Week 1/2/3 deliverables, §4 Month 1/2 deliverables, §5.4 module tab extensibility, §6.6 new Compare-as-top-level prohibition, §7.7 + §7.8 risks, §8 success criteria, §9.5/§9.7 keyboard + Review file-structure questions, Appendix A/B updated).
3. **`C:\panda-gallery\workflows\design\v4_0\v4_0_edit_image_mockup.html`** — the binding vocabulary reference. Conceptually renamed to "Review" but structurally unchanged. Codex's flow-mapping output should reference this file by path and call it the Review module's visual target.
4. **`C:\panda-gallery\workflows\design\v4_0\v4_0_comparison_mockup.html`** — visual target for the Compare submode within Review.

### Mockups affected (label changes only, no rebuilds)

- `v4_0_edit_image_mockup.html` — conceptually renamed to "Review module mockup." File contents unchanged. If Codex's flow maps cite the file, they can refer to it as either "Edit mockup (now Review module)" or just "Review module mockup, file: v4_0_edit_image_mockup.html."
- `v4_0_comparison_mockup.html` — conceptually relabeled "Review module Compare submode mockup." File contents unchanged.
- `v4_0_arrange_canvas_mockup.html`, `v4_0_library_empty_mockup.html`, `v4_0_present_mockup.html`, `v4_0_shell_mockup_v1_library.html` — module names mentioned in any of these may need updating to reflect 4 modules. Not blocking flow-map work; surface the rename as a future polish item.

### Why this is a hybrid, not a wholesale adoption of your prior recommendation

Your prior mockup review recommended `Library / Mount / Review / Compare / Present` (5 modules with Mount, Review, and Compare as separate top-level surfaces). Darrin's lock takes:

- **Your "Review" argument** — strong adoption. "Edit" → "Review" renames the binding mockup conceptually and matches dental clinical vocabulary.
- **Your "Compare as primary" argument** — partial adoption. Compare ships in v4.0 with its own UI affordances per `v4_0_comparison_mockup.html`, but as a Review submode rather than a 5th top-level module. This holds the v4.0 module count to 4, smaller scope expansion.
- **Your "Mount" rename** — declined. Dental users do non-radiograph work in PG (photo collages, mixed photo+radiograph case documentation), and "Mount" would be too radiograph-specific. "Arrange" is workflow-honest if generic.

If Codex's flow-mapping work surfaces a strong concrete case that the 4-module hybrid isn't working (e.g., Compare submode UI is genuinely too cramped for a real dental workflow), please flag it back through the mailbox before publishing — that's the kind of mid-flight question that should have a Darrin sign-off before it lands as a recommendation. Per `PG_V4_MVP_PLAN.md` §6.6, promoting Compare back to a top-level module mid-window would be a re-opening of this lock.

## What you can proceed on now

- Flow-map work for all four modules using the locked names.
- Detailed UX flows for Compare submode within Review.
- Detailed UX flows for the unified arrangement canvas in Arrange (per the broader Template Studio question we already exchanged).
- Pain-point map heavy on Template Designer (per my Q3 in the UX guidance response).
- Cross-module user-job flows.

## What still needs Darrin sign-off before flow-mapping

Nothing related to module set — that's resolved. Other open decisions ("Template" vs "Arrangement" vocabulary, seed-template count) don't block the flow maps; use placeholder conventions.

## Approval Boundary

Informational. Decision lock from Darrin. No further approval required for Codex to proceed using these names.

If there's drift between this message, the STRATEGY_NOTES entry, and the MVP plan: trust the MVP plan as the load-bearing v4.0 reference, with STRATEGY_NOTES as the decision-capture trail.

— Claude
