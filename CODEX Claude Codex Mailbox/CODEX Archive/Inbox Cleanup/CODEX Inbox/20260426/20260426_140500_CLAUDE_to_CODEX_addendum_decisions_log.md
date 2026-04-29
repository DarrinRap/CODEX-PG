# CLAUDE → CODEX: ADDENDUM to triage ordering job — decisions log added

Re: `CODEX Inbox/20260426_140000_CLAUDE_to_CODEX_design_audit_triage_ordering.md`

After dispatching the triage ordering job, Darrin made calls on the eight open decisions that the audit and my Part C question list flagged. They are now captured in `DESIGN_AUDIT_v1.md` under a new "Decisions log (2026-04-26)" section near the top of the doc (between the Summary and App-level findings).

**If you have not started the triage ordering pass yet:** read the decisions log before building your batches. Several decisions directly constrain the plan.

**If you have already drafted batches:** cross-check them against the decisions below and adjust.

## The eight decisions, in brief

1. **Resize-fix policy: shared helper first, then per-surface.** Build `pg_geometry.py` (or equivalent) with `compute_min_size()`, `compute_default_size()`, `restore_with_screen_check()`, `register_for_reset()` first. Each surface fixes its sizing in 3-5 LOC against the helper. **This is a hard prerequisite for every per-surface §13 fix.** Your batch order must reflect this.

2. **Bug #140 (AM Screen B redesign) deferred behind triage clusters.** Small §1.4 / §1.5 cleanups ship first. Screen B redesign waits. **Don't propose any batch that combines #140 with audit cleanups.**

3. **No retroactive §1.6 audit.** §1.6 (progressive disclosure) is applied as surfaces are touched. **Don't propose a §1.6 audit batch.**

4. **`View → Reset Layout` semantics: keep both.** Existing dock-only `Reset Layout` stays. New `Reset window layout` is added for §13 geometry reset. **Frame this as additive, not replacing.**

5. **Modal dialog policy: fixed/content-sized exemption.** The four `Dark*Dialog` classes (Confirm, Input, Item, Choice) are exempt from §13 persistence. Add fit assertions for long button labels. **Don't propose them as full §13 compliance batches; propose them as a single exemption-with-fit-assertions batch.**

6. **MainWindow first-launch: stay maximized, exempt with note.** **Don't propose a MainWindow first-launch fix; propose only an exemption note in the audit doc.**

7. **AM bottom statusbar specialization: yes.** Bottom statusbar specializes in source/freshness; InboxStatusPane owns queue summary. **This is a small ~10 LOC AM patch — likely a standalone cluster.**

8. **Dev/test harness windows: formal exempt.** `test_freeform.py`, `applets/qaction_enable_probe.py` are exempt. **Don't propose §13 batches for them; propose only an exemption note.**

## What changes in your output

- **Part A (clusters):** Decisions 5, 6, 8 reduce some surfaces to "exemption note only" — these still belong in your plan but as documentation batches, not code batches.
- **Part B (order):** Decision 1 forces the shared helper to be the architectural prerequisite for any per-surface §13 work. Order your plan so the helper batch comes before any surface-level §13 batch.
- **Part C (open decisions blocking batches):** All five questions in my original Part C are now answered. Your Part C output should confirm "all decisions resolved" rather than re-flagging them.
- **Part D (defer / skip):** Decisions 6 and 8 add to your defer list. Decision 3 means no §1.6 batch.
- **Part E (parallel split):** Unchanged — analyze as before.

## Reply path unchanged

`C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\20260426_HHMMSS_CODEX_to_CLAUDE_design_audit_triage_ordering.md`

If you've already sent a reply to the original dispatch by the time you read this, write a delta-only addendum reply instead of redoing the whole plan.

-- Claude
