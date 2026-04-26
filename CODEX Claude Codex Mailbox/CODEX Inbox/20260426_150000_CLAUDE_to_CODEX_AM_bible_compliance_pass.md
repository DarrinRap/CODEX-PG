# CLAUDE → CODEX: Audit Module — comprehensive Bible compliance pass

**Tier: Extra-High.** Multi-section design synthesis. Output is a complete spec doc plus HTML mockups for every AM screen at three widths. ~800-1500 line response expected. This is the largest design job dispatched to date.

## Why this job

Today's AM ships (v4.41 through v4.42.3) tightened individual surfaces but the module as a whole still violates Bible principles in ways one-off patches won't fix. Live screenshots reveal:

**Screen A:**
- Workflow stepper rails are 8px tall — visually too thin to read as connecting lines (§1.5 violation: feature doesn't reflect its purpose because it's too small to do its job)
- Bug list metadata columns waste horizontal real estate at wide window widths (§1.4)
- Title column still elides with `…` despite v4.42.3's `setTextElideMode(Qt.ElideNone)` — Qt elides in painter, not data model; needs custom delegate (§13.6)

**Screen B (the one that triggered this):**
- Massive vertical whitespace in the right column (~600px of air between "Untriaged" button and "Build Fix Prompt" — §1.4)
- "Ready to triage" status card duplicates the UNTRIAGED state shown three other places (§1.5)
- Mock-provider banner ("Mock provider (mock-deterministic) — v0...") is filler (§1.5)
- "Build Fix Prompt" button enabled despite bug being UNTRIAGED (§1.6 violation — exactly the worked example §1.6 was written for)
- Three competing button styles with no visual hierarchy (§6.13)
- No §6.22 module screen header anatomy — just an inline title row, no proper separator, no quiet utility actions
- Section grammar is flat (Files/Reproduce/Expected/Actual all at same visual weight) — §3 typography violation
- Right pane doesn't behave responsively at narrow widths (§13)

The fix isn't another patch. It's a coherent design pass that applies the Bible end-to-end across AM and produces a single shipping plan.

## Foundation reading (MANDATORY — read before writing)

Read these in order. Don't skim. Many of them are recent.

1. **`PG_DESIGN_BIBLE_v1.md`** — entire document. The binding contract. Pay particular attention to:
   - §1.1 Medical, not playful
   - §1.2 Restraint over flourish
   - §1.3 Clinical precision via monospace
   - §1.4 Every pixel earns its presence
   - §1.5 Every design feature reflects a true purpose
   - §1.6 Progressive disclosure — hide / disable / enable as three states (added today)
   - §2 Color system (tokens)
   - §3 Typography
   - §4 Spacing scale
   - §6 Components (especially §6.13 buttons, §6.21 workflow stepper, §6.22 module screen header — both added today)
   - §7 Module-zone semantics
   - §8 Empty states
   - §13 Resize and persistence behavior

2. **`workflows/audit/DESIGN_AUDIT_v1.md`** — both Codex's and CC's audit passes. Pay attention to AM-specific findings (`AuditModuleWindow`, `_BugListScreen`, `_BugDetailScreen`, `_ArchiveScreen`).

3. **`workflows/audit/DESIGN_AUDIT_v1.md` § "Decisions log (2026-04-26)"** — eight binding decisions made today. Decision 2 (Bug #140 deferred behind triage clusters) is **superseded** by this dispatch — Screen B redesign is now part of the AM Bible pass, not a separate later ship.

4. **`audit_module/audit_module_window.py`** — the entire file. ~2500 LOC. You need a full picture of what AM is today before designing what it should be.

5. **`audit_module/_components.py`** — `StatusPane`, `_WorkflowStepper`, `_ChecklistRow`, `_GapRow`. Every shared AM component.

6. **`BUGS.md`** — entries #114, #129, #138, #140 specifically. AM-relevant bugs.

7. **`workflows/cc_mailbox/CLAUDE Inbox/20260426_124500_CC_to_CLAUDE_v4_42_3_report.md`** — what just shipped on Screen A.

## Live observations to address

These are observed in the live build today (2026-04-26). They are not speculation; they are what Darrin sees on his screen. Your design must address each.

### Screen A
1. **Workflow stepper rails too thin.** Currently 1px wide × 8px tall. Visually disappear between 18×18 indicators. The stepper fails its purpose: it does not visually connect the steps. Bible §6.21 currently specifies "1×8px" — this is a spec error caught in live verification. Recommend new dimensions in your design pass with visual rationale.
2. **Wide-window column waste.** At ~1400px window width, SEVERITY/STATE/FILES columns retain their fixed widths and TITLE column wraps unnecessarily. Wrapping should happen only when truly necessary at narrower widths. Consider proportional behavior, breakpoints, or dynamic minimum widths.
3. **Title elision despite ElideNone.** Live screenshot shows "AM Screen B UX is confusing for new users; needs full ..." with `…` truncation. v4.42.3 set `Qt.ElideNone` — but Qt's `QTableWidget` elides in the paint engine regardless of data-model elide mode. Specify a fix that actually works (likely `QStyledItemDelegate` subclass that paints with `Qt.TextWordWrap | Qt.AlignTop` and never calls `elidedText`).
4. **Empty states.** Inbox-clear, all-untriaged-cleared, etc. Currently uncovered. Apply §8.

### Screen B (the major redesign)
1. **Vertical whitespace.** Right column has ~600px of empty air. Either populate with operational data (per §1.5 only if it earns its presence) or restructure so the column shrinks to content.
2. **Triage Assistant card redundancy.** "Ready to triage / Run AI triage to classify this bug and surface any blockers." duplicates the UNTRIAGED state shown elsewhere. §1.5 violation.
3. **Mock provider banner.** Filler. Either kill or convert to operational provider info that updates when real AI lands (§1.5).
4. **Button affordance state.** "Build Fix Prompt" enabled when bug is UNTRIAGED. §1.6 says: hide when contextually irrelevant OR disable-with-tooltip when state-blocked. This is the worked example.
5. **Button visual hierarchy.** Three competing styles (giant peach fill, dark UNTRIAGED, peach Build Fix Prompt). Apply §6.13 grammar.
6. **Module screen header.** Currently inline title with no separator, no §6.22 anatomy. Missing the strict-and-sparse one-row header.
7. **Section typography.** Files/Reproduce/Expected/Actual all read at same weight. Apply §3 hierarchy (sections as `.section-head`-style peach caps; body prose as `.body`).
8. **State badges and labels.** "Open · Medium · new navigation-history module suggested; panda_gallery.py · UNTRIAGED" — that meta-row is information-dense but visually flat. Restructure.

### Archive screen
1. Audit against §13 (resize/persistence). Currently inherits AM window's missing geometry persistence.
2. Apply §8 empty states.
3. Verify §1.5 on archive entry rows.

### AM module shell
1. **Bottom statusbar specialization.** Decision 7 in audit doc: bottom bar specializes in source/freshness, InboxStatusPane owns queue summary. Apply across all three AM screens.
2. **Window geometry.** §13 fixes here are deferred to the architectural shared-helper batch (Decision 1). But your design pass should specify *what behavior is correct* so the architectural batch knows what to build.

## What I want from you

Five deliverables in one combined output:

### Part A — Comprehensive AM Bible compliance audit

For each AM surface (Screen A, Screen B, Archive, AM shell, all AM-owned dialogs), produce a violation-by-violation list against every relevant Bible section. This is more focused than DESIGN_AUDIT_v1.md — go deep on AM specifically, not broad across the app.

For each violation, note:
- Bible section
- Specific evidence (line numbers in `audit_module_window.py` or `_components.py`)
- Severity (Critical / High / Medium / Low)

### Part B — Design specification (per surface)

For each AM surface, write what it *should* look and behave like.

**Screen A** (bug list):
- Header (§6.22 anatomy — title, optional non-redundant status, utility actions)
- Filter row
- Bug list table (column behavior at three widths; row behavior; pill behavior; truncation policy with delegate fix)
- Summary pane (StatusPane, workflow stepper, count rows — already shipped, but verify against §1.4/§1.5/§1.6)
- Empty states (§8)

**Screen B** (bug detail) — the major redesign:
- Header (§6.22 anatomy)
- Bug content panel (left)
- Triage panel (right) — fix the whitespace, fix button hierarchy, apply §1.6 to every action
- Section typography (§3)
- Affordance state machine: which buttons hide / disable / enable in which bug states
- Empty states for missing fields

**Archive screen:**
- Header
- List behavior
- Detail behavior

**Module shell:**
- Bottom statusbar specialization
- Resize behavior contract (input to architectural batch)
- Inter-screen navigation chrome

For each, specify:
- Bible tokens used (no new tokens)
- Component grammar (which §6 components apply)
- Behavior at three widths: narrow (~1000px right pane), default (~1280px), wide (~1800px)
- Affordance states per §1.6 (which buttons are visible/hidden/disabled in which states)
- Acceptance test: §1.5 removal test for every sub-element

### Part C — HTML mockups

Render your design pass at:
`C:\panda-gallery\workflows\design\pg_general_mockups\AM_bible_pass_v1.html`

Single self-contained HTML file. Include:
- Screen A at narrow / default / wide widths
- Screen B at narrow / default / wide widths, with at least three bug states represented (UNTRIAGED, READY, FIXED) showing the §1.6 affordance state machine
- Archive at default width
- Empty states for each screen

Use Bible tokens. Use real PG-style chrome. Show the workflow stepper with whatever rail dimensions you recommend (§6.21 will be updated to match). Show the §6.22 module screen header on every screen.

These mockups are how the design gets verified before any code ships. Treat them as production-grade.

### Part D — Implementation sequencing

Recommend the order in which fixes ship. AM is multi-screen and big — this can't be one v4.42.4 patch. Likely 4-6 ships:

- Some are straightforward cleanups (kill mock-provider banner, fix stepper rails)
- Some need new infrastructure (custom title delegate for `…` fix; affordance state machine for §1.6)
- Some are full screen redesigns (Screen B)

For each ship batch:
- Ship name (e.g. v4.42.4, v4.43, v4.44)
- Surfaces touched
- Bible sections addressed
- Estimated LOC
- Dependencies (which batches must ship first)
- Acceptance gates (smoke + visual)

### Part E — Bible amendments needed

Some live findings are spec errors, not implementation errors:
- §6.21 rail dimensions (8px is too thin)
- Possibly others you find

For each, propose the Bible amendment text. I'll review and apply before the implementation batch ships.

## Out of scope

- Don't write fix dispatches. Output is the design + sequencing, not the prompts to CC.
- Don't propose new tokens.
- Don't redesign non-AM surfaces. Other modules get their own Bible passes later.
- Don't second-guess Bible principles — work within them. If a principle conflicts with what AM needs, flag it as an amendment in Part E, don't override.

## Reply

Write your full design doc to:
`C:\panda-gallery\workflows\design\AM_BIBLE_PASS_v1.md`

Reply summary (2-3 paragraphs + pointer at the design doc + pointer at the HTML mockup) to:
`C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\20260426_HHMMSS_CODEX_to_CLAUDE_AM_bible_compliance_pass.md`

This is parallel work to your in-flight DESIGN_AUDIT triage ordering job. Both can run; they don't conflict (the audit triage is whole-app priority ordering; this is AM-specific deep design).

-- Claude
