---
schema_version: 1
id: CLAUDE-DESKTOP-20260429-190000-LEDGER-CAPTURE-V1-ALT-MOCKUP
thread_id: PG-LEDGER-CAPTURE-UX
created_at: '2026-04-29T19:00:00-07:00'
from: claude_desktop
to: codex
type: dispatch
priority: normal
status: open
thread_status: active
action_owner: codex
requires_darrin_decision: true
approval_boundary: build_after_darrin_go
reply_to: []
tier: high
target_version: docs-only (mockup file, no version bump)
prerequisite_commit: 3638bb2
---

# Claude Desktop -> Codex: LEDGER_CAPTURE v1_alt states mockup (structural-alternative version)

**Tier:** High · **Estimated time:** ~3 hours · **Target version:** docs-only

> **Status:** LIVE. Fired 2026-04-29 19:00 PDT alongside the paired CC dispatch at `workflows/cc_mailbox/CC Inbox/20260429_190000_CLAUDE_to_CC_ledger_capture_v1_states_mockup.md` (A47/A48 pattern — both arrived in inboxes in the same minute). Build per §3 acceptance criteria; report per §4 deliverables.

---

## TL;DR

Build the **structural-alternative** multi-state HTML mockup for the redesigned Ledger Capture screen. Single file. 10 states (C1–C10). Mirrors the document structure of `AM_screen_a_v4_rebuild.html`. Bug #143 is the source; the redesign brief at `workflows/design/LEDGER_CAPTURE_UX_REDESIGN_BRIEF_v1.md` is the spec.

This is the **Codex version** of a Codex+CC parallel mockup competition (A47/A48 pattern). CC builds `LEDGER_CAPTURE_v1_states.html` in parallel as the AM-pattern-faithful version. Synthesis Q&A with Darrin follows after both ship — the value of running both in parallel is that Darrin sees the same 10 states rendered with different positions on Q2/Q3/Q4/Q5/Q6, picks a structural skeleton, and calls out individual features worth porting from the loser.

**One stepper-orientation note (§1A) before drafting** — Darrin has explicitly chosen horizontal-across-the-top for the workflow stepper. The brief's Q1 text suggests Codex's mockup should "test the alternative" (vertical); that text is **stale**. Q1 is locked horizontal in both mockups. The structural alternatives Codex differs on are Q2, Q3, Q4, Q5, Q6 — see §2.5. Read §1A, then proceed.

---

## §1A — Stepper orientation: horizontal (Darrin pre-decided, applies to BOTH mockups)

The brief's Q1 (stepper orientation) was resolved before this dispatch: **horizontal stepper across the top of the workspace.** Three labeled steps left-to-right, connecting line between steps, active step peach.

This applies to **both** the CC mockup and your alt mockup. The brief's original "Codex's mockup should test the alternative" wording for Q1 is **superseded** — Darrin picked horizontal for both surfaces. The structural alternatives Codex contributes come from Q2/Q3/Q4/Q5/Q6 (see §2.5). Do NOT render a vertical stepper.

This is a known, deliberate deviation from Bible §6.21 (which currently defines stepper as vertical only). The deviation:

- Bible §6.21's anatomy is documented for the vertical pattern; the same component tokens (indicator size, color rules, kind-color forbidden-list) translate to horizontal cleanly.
- A future Bible §6.21 amendment will add the horizontal variant once this Capture surface is locked. **You are not amending the Bible in this dispatch** — that's a separate docs commit downstream.
- Build the horizontal stepper as if §6.21 already documented it. Apply the existing §6.21 rules where they translate. The translated rules are listed in §1A.1 below — read them carefully because earlier sessions paraphrased §6.21 loosely and produced mockups that drifted from the Bible.

### §1A.1 — Bible §6.21 rules that translate to horizontal (read this carefully)

This stepper is **active mode** (the user IS in the workflow). Per Bible §6.21 Color rules, active mode has four step states: pending, active, complete, disabled. The Capture stepper uses three of them: pending (steps not yet reached), active (the current step), complete (steps already passed). Disabled is not used here.

For each C-state in §2.4, the steps that are "past" are in **complete** state, the current step is **active**, and steps not yet reached are **pending**. Translated to horizontal, here is the canonical rendering:

**Indicator (18×18 round, mono 10px weight 700):**

| Step state | Indicator bg | Indicator border | Indicator content |
|---|---|---|---|
| Pending | `--pane-raised` | `--border` | numeral in `--text-muted` |
| Active | `--accent` | `--accent` | numeral in `--accent-ink` |
| Complete | `--accent-soft` | `--accent-border` | **peach `✓` checkmark in `--accent`** (NOT a numeral — Bible §6.21 explicitly: "the indicator becomes a peach checkmark (✓)" in active-mode complete state) |

**Label color:**

| Step state | Label color |
|---|---|
| Pending | `--text-muted` |
| Active | `--text` |
| Complete | `--text-muted` |

**Rail (1px line connecting indicator centers — horizontal in this dispatch, vertical in Bible canonical):**

| Position | Color |
|---|---|
| Rail segment between two complete steps, or between complete and active | `--accent-border` (peach progress) |
| Rail segment after the active step (before pending steps) | `--border-soft` |
| Rail segment between two pending steps | `--border-soft` |

This progress-tracking rail color is from Bible §6.21: "rail color carries lightweight progress information in active mode (peach for completed segments, soft border for pending segments)". A uniform `--border-soft` rail across all C-states is **wrong** — it loses progress information.

**Other §6.21 rules that carry over:** plain numerals 1, 2, 3 in pending/active states (not Unicode glyphs); ✓ checkmark only in complete state (no other icon swaps); no animation on state transitions; no kind colors (gap_design / ok / err) on indicators or labels — kind belongs to count rows, not stepper steps.

**Horizontal-segment length** (the one parameter §6.21 doesn't dictate because §6.21 is vertical): your call. Pick whatever reads cleanly at 1280×800 — long enough that the connecting line reads as continuous between 18px indicators (Bible §6.21's vertical-rail equivalent is 22px tall; horizontal needs to be at least visually proportional). Document your chosen length in the per-state commentary.

**No vertical stepper anywhere** in this file. Q1 is locked horizontal.

---

## §1 — Authority

Read all of these end-to-end before drafting any HTML. Bible §10 non-negotiable #1 ("Inherit from the gold-standard files") and §12.1 ("Authoring a new mockup") are the canonical authorship rules — read both first.

1. **`workflows/design/LEDGER_CAPTURE_UX_REDESIGN_BRIEF_v1.md`** — the redesign brief. Read end-to-end. Q1 stance is overridden by §1A above; Q2–Q6 stances are flipped per §2.5 (you take the alternative on each axis).

2. **`workflows/design/PG_DESIGN_BIBLE_v1.md`** — canonical visual grammar. Required end-to-end reads:
   - §1.4 (every pixel earns its presence) and §1.4.1 (screen real estate budget; viewport test at 1280×800)
   - §1.5 (every design feature reflects a true purpose)
   - §1.6 (progressive disclosure — three states for any affordance)
   - §2 (color tokens — surface scale, accent scale, semantic scale, gap-kind scale)
   - §3 (typography — peach all-caps section header, mono color usage)
   - §4 (spacing, radius, motion timings)
   - §6.21 (workflow stepper — anatomy/sizing/colors/forbidden-chrome that translates to horizontal per §1A.1)
   - §6.22 (module screen header — strict and sparse, no second prose line)
   - §8 (empty state voice — **especially relevant for your Q5 stance, see §2.5**)
   - §10 (non-negotiables, all 13)
   - §12.1 (authoring a new mockup)
   - §13 (sizing invariants — relevant to picker dialog)
   - §14 (visual verification protocol)

3. **`workflows/design/pg_general_mockups/AM_screen_a_v4_rebuild.html`** — canonical PG v4 surface pattern. Mirror its document structure exactly: doc chrome + zoom bar + state badges + window blocks + commentary. Read end-to-end.

4. **`workflows/design/applets/PG_Design_Bible_Audit_v1.html`** — Bible audit applet (64 checks, 8 tabs). Run against the mockup before declaring ready-to-commit per §3 acceptance criterion 10.

If any of these reads surface ambiguity in the brief that you can't resolve, **stop and report** before drafting. Do not invent fills.

**Pattern 4 reminder (REPEATED_ERRORS):** when this dispatch references a Bible section, read the Bible section directly before applying it. Don't trust the dispatch's summary alone. CD reproduced this exact error in the prior session drafting these dispatches — the first version of the CC dispatch had five Bible-fidelity errors slip through because §6.21's anatomy was paraphrased loosely. The §1A.1 anatomy table above is a re-read of Bible §6.21; verify it against the Bible yourself before building.

---

## §2 — Scope

### 2.1 — Deliverable

**One single multi-state HTML file** at:

```
workflows/design/pg_general_mockups/LEDGER_CAPTURE_v1_alt.html
```

Note the filename: `_alt`, not `_states`. This is the alternative mockup. The CC mockup at `LEDGER_CAPTURE_v1_states.html` is owned by CC — do not touch it.

### 2.2 — Document structure

Mirror `AM_screen_a_v4_rebuild.html` top-to-bottom:

1. **Doc chrome** — eyebrow ("PANDA GALLERY • LEDGER • CAPTURE"), title ("Ledger Capture v1_alt — multi-state mockup (structural alternative)"), subtitle (one sentence noting the structural-alternative role and which Q-axes differ from the CC mockup), change-log box (single entry: "v1_alt — initial alternative mockup per redesign brief").
2. **Zoom bar** — fixed-position top, range slider 40–100%, default 100%. JS scales body content via CSS transform. Match `AM_screen_a_v4_rebuild.html`'s implementation.
3. **State sections** — one per state (see §2.4). Each has:
   - A peach STATE BADGE (uppercase mono pill: `STATE C1`, `STATE C2`, …)
   - A state heading (Segoe UI 18px regular)
   - A one-paragraph description of what the state demonstrates
   - The complete `.window` block at 1280×800 (per §10 non-negotiable #13 + §1.4.1 viewport test)
   - Below each window: 2–4 sentence italic commentary explaining design choices and Bible references. Use `[Q1]`–`[Q6]` markers wherever a stance shows.
4. **Open questions section** at the bottom — Q1–Q6 with stance per question, one short paragraph each, including which states demonstrate that stance. Q1 entry notes the §1A horizontal-only decision (same as CC). Q2–Q6 entries explicitly state where Codex differs from CC and the design rationale for each flip.
5. **Comparison memo pointer** — bottom of the file, one short section noting that the comparison memo (`LEDGER_CAPTURE_v1_comparison_memo.md`) will be authored by whoever ships second per the brief's "Mockup deliverables" §3. Codex authors the memo if Codex ships second; otherwise CC authors it.

### 2.3 — Window block (per-state shape)

Each `.window` block:

- **Titlebar** — `--chrome` `#161625`, dark traffic-light buttons left, title centered. **Read live values at build time:** read `VERSION.txt` for app version; read the most recent `workflows/design/PG_DESIGN_LEDGER_SPEC_v*.md` filename or its frontmatter for spec version. Title format: `Panda Gallery Ledger v<VERSION> — spec v<SPEC_VERSION>`. Note in the change-log entry which version snapshot the mockup uses (so synthesis knows whether the mockup is stale).
- **Module header strip** — Bible §6.22. Single row. Peach all-caps title (`LEDGER · CAPTURE` or just `CAPTURE` — pick what reads better, explain in commentary). Spacer. Optional `.msh-status` line if the state has genuinely operational status (e.g. C3: `Loaded 14:39:22 from staging/proposed_<slug>`); omit otherwise per §6.22's "default to absent" rule. Up to 3 utility actions right (e.g. Refresh, Settings, Help) — pick what's actually useful, not filler.
- **Stepper** — horizontal across the top of the workspace, below the module header. **Render per the §1A.1 anatomy table.** Three steps left-to-right. Indicator bg/border/content per step state. Label color per step state. Rail color tracks progress (peach `--accent-border` for completed segments, `--border-soft` for pending). Active-mode complete state renders the indicator content as **`✓` peach checkmark, NOT a numeral** — this is Bible §6.21 explicit. Plain numerals 1, 2, 3 only for pending and active states. No animation. No kind colors.
- **Active-step status line** — directly under stepper, one line, italic, lay-language. Per the brief: e.g. "Pick a draft from the list to load it for review.", "Read the decision. Edit if anything's wrong. Click Lock when ready.", etc.
- **Workspace** — **single-column** layout per §2.5 Q2. Form fields fill the workspace width; snippet preview is integrated as a collapsible inline section ("Visual snippet") at the bottom of the form rather than a fixed right column. Section headers use §3.3 peach all-caps treatment with `▾`/`▸` collapse caret. See §2.5 Q2 for full rationale and the snippet integration approach.
- **Bottom button row** — Save draft (secondary `.gbtn`) + Lock (peach primary `.gbtn.primary`) anchored to the workspace bottom. One peach primary per screen per §10 non-negotiable #4. Visibility/disabled state per brief's progressive disclosure rules and §1.6. Tooltips per brief's plain-language rename table.
- **Statusbar** — Bible §6.17. `[CAPTURE]` mode tag peach mono left, source/freshness center, version right. No queue counts (§1.4.1 duplication test — version is already in titlebar; surface only one).

### 2.4 — The 10 states

Each state maps to the brief's §"States to mock up". Do **not** invent new states. Do **not** skip states. If a state can't be rendered cleanly because the brief is ambiguous, stop and report.

For each state, the per-step indicator content per §1A.1:

| State | Stepper | Step 1 | Step 2 | Step 3 | Description |
|---|---|---|---|---|---|
| **C1** | n/a (picker dialog overlays nothing) | — | — | — | Picker dialog with N=10 drafts, one selected, OK/Cancel footer. DarkConfirmDialog-derived per brief. Cards (not raw QListWidget items). Double-click and Enter both equal OK per brief. |
| **C2** | Step 1 active | `1` (active) | `2` (pending) | `3` (pending) | Empty state, no draft loaded. Bible §8 voice. Wordmark gradient on a key word. Lock + Save disabled with §1.6 explanatory tooltips. |
| **C3** | Step 2 active | `✓` (complete) | `2` (active) | `3` (pending) | Draft loaded (D8 — `decision-schema-strictness-layered`, the canonical example per brief). Default expanded/collapsed states per §2.5 Q5 (always-expanded with §8 placeholder when empty — your stance differs from CC). Lock enabled. |
| **C4** | Step 2 active | `✓` (complete) | `2` (active) | `3` (pending) | Same draft as C3. **Paths considered** section expanded with rejected-alternatives content. Demonstrates collapse mechanics. |
| **C5** | Step 2 active | `✓` (complete) | `2` (active) | `3` (pending) | Same draft as C3. **Stage dropdown open** showing all 5 stages with one tooltip rendered explicitly to demonstrate the pattern. |
| **C6** | Step 2 active | `✓` (complete) | `2` (active) | `3` (pending) | Lock attempted with hard-required field empty (Title) — red `--err` outline + inline error + red status banner. Bible §2.5. |
| **C7** | Step 3 active (with warning) | `✓` (complete) | `✓` (complete) | `3` (active) | Lock succeeded with soft-required field empty (Rationale) — amber `--warn` status banner + warning surfaced. |
| **C8** | Step 3 active (just-locked) | `✓` (complete) | `✓` (complete) | `3` (active) | Locked state, Unlock window open, 60-second countdown, peach Unlock button with subtle 1.5s pulse per §6.18 / §4.3. All fields read-only / grey-tinted. |
| **C9** | Step 3 active (post-60s) | `✓` (complete) | `✓` (complete) | `3` (active) | Past Unlock window. Amend / Supersede / Retire buttons replace Unlock. Retire is destructive variant per §6.12. |
| **C10** | n/a (picker overlay) | — | — | — | Same picker as C1 with a draft card hovered — tooltip popover visible showing full title + summary preview + slug + timestamp. |

**Rail color per state** (per §1A.1):
- C2: rail-1→2 = `--border-soft`; rail-2→3 = `--border-soft` (no progress yet)
- C3/C4/C5/C6: rail-1→2 = `--accent-border` (step 1 complete); rail-2→3 = `--border-soft` (step 3 pending)
- C7/C8/C9: rail-1→2 = `--accent-border` (complete-to-complete); rail-2→3 = `--accent-border` (complete-to-active)

### 2.5 — Open questions Q1–Q6 (Codex stances — flipped from CC on Q2–Q6)

The point of running CC and Codex in parallel is that synthesis sees both positions side by side on each Q-axis. CC takes the brief's lean on Q2–Q6; **Codex takes the alternative.** Q1 is locked horizontal for both per §1A.

| Q | CC stance (do NOT replicate) | **Codex stance (build this)** | Mark with |
|---|---|---|---|
| Q1 | Horizontal (locked per §1A) | **Horizontal (same — locked per §1A)** | `[Q1]` callout in C2/C3 commentary noting orientation choice; same as CC |
| Q2 | Two-column (form left, snippet right) | **Single-column with snippet integrated as a collapsible inline section at the bottom of the form.** Rationale: maximizes form width on a 1280×800 viewport; eliminates the dead right column on states C2 (empty) and C6 (validation error) where the snippet is irrelevant; tests whether the snippet earns its own column under Bible §1.4 ("every pixel earns its presence"). | `[Q2]` callout in C3 commentary explaining the single-column choice + the snippet collapse-when-empty behavior |
| Q3 | Hover-on-label with subtle dotted underline | **Small `?` icons next to each field label** (10×10 mono-superscript style, `--text-dim` color, peach on hover). Rationale: discoverability — a hover-only affordance is invisible to a first-time user; the `?` icon is industry-standard and self-documenting. Tests whether visible-but-quiet beats invisible-but-clean for tooltip discovery. | `[Q3]` callout in C5 commentary explaining the `?`-icon choice |
| Q4 | `Locked` (verb-noun consistency with the Lock button) | **`Accepted`** (matches the `accepted` schema value in the underlying staging files; reads as a status the decision *has* rather than an action that was *done to it*; aligns with how the rest of the world labels accepted decisions in design-decision systems). The brief's design-principles item 2 rename-table tooltip + C8 description use `Accepted` (e.g. "Locking moves it to 'Accepted'"); the brief's Q4 lean uses `Locked`. The brief is internally inconsistent on this; flag in the bottom Open Questions section so synthesis can resolve it. | `[Q4]` callout in C5 commentary + Open Questions note flagging brief inconsistency |
| Q5 | Collapse if empty, expand if non-empty | **Always-expanded with a Bible §8 empty-state placeholder** when a soft-required section has no content. Rationale: stronger §1.6 alignment — the placeholder text teaches the user what each section is *for* before they have content for it (an inline form of progressive disclosure). CC's collapse-if-empty is also valid (the section header with ▸ caret stays visible and discoverable; not a §1.6 violation), but the always-expanded variant front-loads the teaching. Tests whether visible inline documentation beats collapsed-by-default for first-time clarity. Hard-required and always-shown sections behave identically to CC's stance (always expanded). | `[Q5]` callout in C3 commentary explaining the always-expanded choice + §8 placeholder text rendered in C3 for at least one empty section |
| Q6 | Small peach badge `[Draft]` matching stage pill style | **Italic dim-text `(Draft)` prefix** in `--text-dim` rendered before the title in the related-decisions list. Rationale: the badge variant adds visual weight to a row whose primary content is the title; the italic-dim variant reads as parenthetical metadata and lets the title remain the visual anchor. Tests whether the prefix needs to be loud or quiet. | `[Q6]` callout in C3 (related-decisions section) commentary |

If during build you find a strong reason to deviate from any default, add a note in the bottom Open Questions section with justification. Do not silently invent.

**Synthesis aid:** the bottom Open Questions section in your file should explicitly say, for each Q-axis, "CC took position X; this mockup takes position Y; here's the design tradeoff." That framing is what makes the synthesis Q&A productive — Darrin reads both files, sees the same axis presented as a deliberate fork on each side, and can pick.

### 2.6 — Out of scope (DO NOT touch)

- **CC's mockup file** (`LEDGER_CAPTURE_v1_states.html`) — CC owns it. If it doesn't exist yet when you build, fine; don't reference it directly (you can reference it in commentary by filename only).
- **Capture screen Python source** — `panda_ledger/capture/*.py`. Mockup is HTML-only.
- **Bible source** — `workflows/design/PG_DESIGN_BIBLE_v1.md` is read-only authority. The §1A horizontal-stepper amendment is a future commit, not part of this dispatch.
- **Brief source** — `workflows/design/LEDGER_CAPTURE_UX_REDESIGN_BRIEF_v1.md` is read-only authority. (The brief's Q1 wording about Codex testing vertical is stale; §1A overrides; do not edit the brief.)
- **Any other mockup files** in `workflows/design/pg_general_mockups/`.

---

## §3 — Acceptance criteria

1. **File exists** at `workflows/design/pg_general_mockups/LEDGER_CAPTURE_v1_alt.html`.
2. **All 10 states present** (C1–C10), each with state badge + heading + description + window block + commentary.
3. **Doc chrome present** matching `AM_screen_a_v4_rebuild.html` structure (eyebrow + title + subtitle + change-log + zoom bar). Title and subtitle make clear this is the structural-alternative file (not the AM-faithful file).
4. **Zoom bar functional** (CSS transform on body content, range 40–100%, default 100%).
5. **Horizontal stepper rendered** consistently across all C2–C9 states per §1A and §1A.1; only the active step changes per state per the §2.4 table. **Completed steps render `✓` peach checkmark, NOT numerals** (Bible §6.21 active-mode complete state). **Rail color tracks progress** (peach `--accent-border` between complete steps and from complete to active; `--border-soft` from active to pending and between pending steps). **No vertical stepper anywhere** in this file — Q1 is locked horizontal per §1A.
6. **Window blocks render at 1280×800** per §10 non-negotiable #13 and §1.4.1 viewport test.
7. **Bible token compliance** — every color resolves to a §2 named token. If a new local-context shade is needed, derive it via `rgba()` from a §2 token rather than introducing a new hex. Every font size resolves to §3.2. Every spacing value to §4.1. No off-scale magic numbers in component code. Specifically for the stepper: pending-step numeral color is `--text-muted`, NOT `--text-dim` (Bible §6.21 Active mode Pending row).
8. **`pg_design_lint` passes.** Run `python -m pg_design_lint workflows/design/pg_general_mockups/LEDGER_CAPTURE_v1_alt.html` against the rendered file. Note: R29 (mockup annotation completeness) is a dispatch-side rule that fires against dispatch frontmatter with `related_mockups`, not against this HTML file directly. The HTML-applicable rules from `pg_design_lint/rules/` are the ones that matter here — pass them all.
9. **All Q1–Q6 stances rendered** with `[Q]` callouts in commentary. Bottom Open Questions section lists each Q with stance + which state(s) demonstrate it. Q4 vocab inconsistency with the brief flagged per §2.5.
10. **Pattern 11 + Bible §14 pre-push eye-test (REQUIRED, not optional):**
    - Run `workflows/design/applets/PG_Design_Bible_Audit_v1.html` against the mockup file in a browser. Capture the applet's PASS/FAIL output for inclusion in the READY-TO-COMMIT report.
    - Manually walk Bible §1–§13 against your rendered mockup. List every potential drift item.
    - Address ALL FAILs and ALL drift items before submitting.
    - Pattern 11 (commit `f150d8d`) is the rule that just shipped; this is its first dispatch-level enforcement on the Codex side.
    - Bible §14.4 sign-off workflow: this is a static HTML mockup, not a Qt surface, so live visual sign-off (§14.2 row 6) is not required at this stage — the Qt implementation dispatch downstream gets that gate. The Bible audit applet IS required at this stage.
11. **Title bar version snapshot** — at build time, read `VERSION.txt` and the most recent `PG_DESIGN_LEDGER_SPEC_v*.md` filename. Embed both values as text in the HTML. Document the snapshot in the change-log entry so synthesis knows whether the mockup is stale.

---

## §4 — Deliverables

All Codex-to-CD reports go to **Codex's outbound CLAUDE Inbox at `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\`** with filename pattern `YYYYMMDD_HHMMSS_CODEX_to_CLAUDE_DESKTOP_<topic_slug>.md`. This is the path Codex uses for all CD-bound reports (matches the recent PAH-protocol traffic from earlier today). Do NOT drop reports into `panda-gallery/workflows/cc_mailbox/CLAUDE Inbox/` — that's CC's outbound mailbox.

1. **Mockup file** at the path in §2.1.
2. **START report** at `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\<timestamp>_CODEX_to_CLAUDE_DESKTOP_ledger_capture_v1_alt_start.md` when work begins (REPORTING DISCIPLINE rule).
3. **READY-TO-COMMIT report** at `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\<timestamp>_CODEX_to_CLAUDE_DESKTOP_ledger_capture_v1_alt_ready_to_commit.md`. Include:
   - File path and size of the mockup
   - Walk through acceptance criteria 1–11 with PASS/FAIL per item
   - Pattern 11 + §14 eye-test result: list every Bible drift item caught, or "no drift detected" with audit applet output snippet
   - Self-assessment: which states were hardest to render and why
   - Q4 vocab inconsistency in the brief (rename-table tooltip + C8 say `Accepted`, Q4 lean says `Locked`): your call (`Accepted` per §2.5) + reasoning, for synthesis
   - Q2/Q3/Q5/Q6 design rationale per axis: why the alternative position is design-defensible, not just "we flipped because we were told to"
   - Working tree state (uncommitted; await commit-go)
4. **Comparison memo** (`workflows/design/LEDGER_CAPTURE_v1_comparison_memo.md`) — author this **only if you ship second**. Per the brief's "Mockup deliverables" §3, whichever side ships second writes the memo. Memo contents: structural differences between the two mockups + recommendation on which to synthesize from. If you ship first, skip this; CC will write it.
5. **SHIPPED report** after `git push`, at `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\<timestamp>_CODEX_to_CLAUDE_DESKTOP_ledger_capture_v1_alt_shipped.md`.

After Darrin says "go": targeted `git add` of the mockup file only (and the comparison memo if authored by you), commit with message `docs: LEDGER_CAPTURE_v1_alt mockup (Codex structural-alternative — bug #143 redesign competition)`, push.

---

## §5 — Estimated time

~3 hours Codex time. Reference scale: `AM_screen_b_v3_cc.html` is 87 KB on disk (verified) and is comparable in scope (10 panels, 1280×800 windows, full state coverage) — use it as your scale benchmark since `AM_screen_b_v3_codex.html` does not exist as a sibling on disk, and recent Codex mockups have been comparable in size to the CC equivalents. The alternative-axis design rationale work in §2.5 adds ~20–30 minutes versus a straight clone of the brief's lean on every axis — that's the cost of doing the structural-alternative work properly. Don't optimize for terseness; optimize for fidelity. The mockup is the spec for synthesis Q&A; ambiguity in the mockup becomes ambiguity in the implementation.

---

## §6 — Status

**LIVE.** Begin per §3 acceptance criteria. CC's parallel `LEDGER_CAPTURE_v1_states.html` dispatch fires alongside this one (A47/A48 pattern). Both sides run independently — your work doesn't depend on CC's, and vice versa. The comparison memo (§4 deliverable 4) and synthesis Q&A happen after both ship.

— Claude Desktop, 2026-04-29 19:00 PDT
