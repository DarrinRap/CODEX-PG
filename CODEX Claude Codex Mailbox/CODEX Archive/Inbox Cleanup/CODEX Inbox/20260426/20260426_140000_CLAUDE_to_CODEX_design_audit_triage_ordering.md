# CLAUDE → CODEX: DESIGN_AUDIT_v1 triage ordering — what ships next, and in what order

**Tier: Extra-High.** Synthesis pass over the merged Codex + CC audit doc. ~400-700 line response expected. Output is a dispatch-ordering plan that sequences the next 4-6 ships after v4.42.3.

## Why this job

`workflows/audit/DESIGN_AUDIT_v1.md` is now 1179 lines: Codex's §13 + §1.4 + §1.5 pass at the top, CC's cross-check + net-new §1.4 + §1.5 audit appended below. The audit identified ~30 surfaces with violations across the three Bible sections, plus several systemic findings (no `_compute_min_size()` anywhere; `View → Reset Layout` is dock-only; geometry persistence wired only on Instruction Pane / Settings dialog).

The audit catalogues findings well. It does **not** answer the operational question: **what should we ship, in what order, and how should fix dispatches be batched?**

That's this job. The output becomes input for the next 4-6 CC dispatches after v4.42.3.

## What I want from you

A dispatch-ordering plan with the following structure:

### Part A — Cluster the findings into ship-ready batches

Read the full audit. Group findings into **coherent ship batches** where each batch:

- Touches a single class of work (e.g. all the §13 architectural fixes; all the §1.5 redundant-prose removals; all the column-width §1.4 fixes)
- Has a clear surface or set of surfaces
- Estimates well as one CC dispatch (~50-300 LOC)
- Doesn't require a decision Darrin hasn't made yet (flag dependencies if so)

For each batch, give:
- Batch name and one-line summary
- Bible sections it addresses
- Surfaces touched (with line numbers from the audit)
- Estimated LOC
- Estimated complexity (Low / Medium / High)
- Explicit Bible references for acceptance criteria
- Whether the batch is **prerequisite for**, **enabled by**, or **independent of** other batches

CC's audit already named three ship-ready clusters (v4.42.3 Screen A trim, v4.42.4 Screen B mock-note, v4.42.5 title elide-none). Two of those got folded into the in-flight v4.42.3. Use those as a calibration point but don't restate them — find the **next** layer of clusters.

### Part B — Recommend ship order

Given your batches from Part A, recommend the order in which they should ship. The order should respect:

1. **Architectural prerequisites first.** If Batch X depends on a shared `_compute_min_size()` helper, the helper batch ships first.
2. **High-severity violations sooner.** §1.5.A redundant teaching (Darrin sees it daily) before §1.4.B decorative margins (cosmetic).
3. **Surfaces in active redesign before stable surfaces.** AM Screen B is in flight; fold its §13 / §1.4 / §1.5 fixes into the active redesign rather than patching old code, then doing the redesign.
4. **High-impact, low-risk before high-risk.** Quick wins that close named Bible-spec violations before architectural rewrites.
5. **Independent batches that can ship in parallel** — flag these so we know which can be CC + Codex coordinated work.

For each batch in order, give a one-line rationale for its position. If two batches are tied, say so and give the tiebreaker.

### Part C — Identify open decisions blocking specific batches

Some batches can't ship until Darrin makes a call. From the audit's "Open questions" section plus my own list, the active questions are:

1. `View → Reset Layout` — repurpose as §13 reset, or keep both `Reset dock layout` (current) plus new `Reset window layout`? My lean: keep both.
2. Modal dialog policy (`DarkConfirmDialog` etc.) — fixed/content-sized exemption with fit assertions, or full §13 compliance? My lean: exempt.
3. MainWindow first-launch — stay maximized, or follow §13 content-driven default? My lean: stay maximized, exempt with note.
4. AM bottom statusbar specialization — keep queue summary, or specialize in source/freshness only (StatusPane owns queue)? My lean: specialize.
5. Dev/test harness windows — §13 enforcement or formal exempt? My lean: exempt.

For each batch in your plan, identify which (if any) of these decisions blocks it. If a batch is independent of all five, say so.

### Part D — Flag findings that should NOT ship as fixes

Some audit findings are not worth fixing:

- Findings on dev-only surfaces if Darrin exempts them (Q5 above)
- UNKNOWN entries that need more investigation, not a fix
- Findings that would be obsolete after a planned redesign (e.g. anything on AM Screen B old code, since Screen B is being redesigned)

Flag these explicitly in a "Defer / Skip" section. Don't propose fixes for them.

### Part E — Recommend a parallel work split

Some batches are parallelizable: CC ships one while Codex specs the next, or two CC sessions can work on independent surfaces. Identify which batches are parallelizable and which must serialize. Specifically:

- Which batches need Codex spec authorship (architectural patterns, new Bible additions, multi-surface contracts)?
- Which batches are pure CC implementation (mechanical changes per audit findings)?
- Which need both?

## Foundation reading

1. **`workflows/audit/DESIGN_AUDIT_v1.md`** — the full audit. Read end to end. The Codex pass and CC pass are both there; both are authoritative.
2. **`PG_DESIGN_BIBLE_v1.md` §1.4, §1.5, §1.6, §13** — the binding principles. §1.6 (Progressive disclosure) was added today and may affect some batches you didn't expect.
3. **`PG_DESIGN_BIBLE_v1.md` §6.21, §6.22** — workflow stepper and module screen header. Already applied to AM Screen A in v4.42.3.
4. **`BUGS.md`** — open bugs. Some audit findings overlap with existing bugs (#129, #138, #140); flag overlaps so we don't double-track.

## Out of scope

- Don't author the actual fix dispatches. Output is the plan, not the prompts.
- Don't propose new Bible additions. Stick to what the audit found.
- Don't second-guess the audit findings — work with what's there. If you spot a finding the audit missed, note it in a "Cross-check addendum" but don't expand the audit doc.
- Don't address v4.42.3 or earlier ships. Those are in flight or done.

## Reply

Write your plan to:
`C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\20260426_HHMMSS_CODEX_to_CLAUDE_design_audit_triage_ordering.md`

The plan should be self-contained: Darrin should be able to read it and know exactly what ships next without re-reading the 1179-line audit doc.

-- Claude
