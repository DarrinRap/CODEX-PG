# CLAUDE → CODEX: AM Screen B UX redesign — mockup task

**Reasoning tier:** **Extra-High.** This is spec authoring + multi-state design + reasoning about user-facing copy + grounding in an existing design language. Don't shortcut — this is the kind of task this tier was meant for.

**Task:** Produce ONE HTML/CSS mockup for the AM (Audit Module) Screen B UX redesign.

This is **not** a code task. **Do not** modify any Python files. Deliverable is a single HTML file.

**Brief:** Read `C:\panda-gallery\workflows\design\AM_UX_REDESIGN_BRIEF_v1.md` IN FULL before starting. The brief specifies design principles, required flow states, deliverable format, and reference reading. The brief is canonical — this dispatch is just a wrapper.

**Deliverable:** `workflows/design/pg_general_mockups/AM_screen_b_v2_codex.html`

**Required reading before designing:**
1. `workflows/design/AM_UX_REDESIGN_BRIEF_v1.md` — the full brief (design principles, what must be in the mockup, what's out of scope)
2. `workflows/design/PG_DESIGN_BIBLE_v1.md` — color palette, typography, spacing, canonical PG component patterns. Hard constraints.
3. `audit_module/audit_module_window.py` — current implementation. Context only, NOT a template. The whole point is to redesign this.
4. `instruction_pane.py` — find `_ChecklistRow` and `ChecklistStepView`. This is the canonical PG pattern for "list of actionable items in a side panel." Borrow visual language and density, not literal markup.
5. Skim 3–4 OPEN bugs in `BUGS.md` so your example data is realistic.

**What's required (paraphrased — the brief is canonical):**
- A single HTML file, dark theme matching PG_DESIGN_BIBLE.
- 5–7 distinct flow states stacked vertically, each labeled. Untriaged → mid-triage (with progress feedback) → post-triage with unresolved gaps → mid-resolution → all-gaps-resolved → reclassify path → status-pane states.
- A persistent status pane that gives feedback on every action (no more invisible toasts).
- Top-of-screen step guidance (e.g. ① Triage → ② Resolve gaps (3 of 5) → ③ Build prompt) per Darrin's request for "key words and numbers/arrows" guidance.
- Gray-out unavailable options (button states reflecting workflow phase).
- Plain language with tooltips for industry terms ("readiness gap" stays IF accompanied by a clear plain-English tooltip).
- Rename or restructure "Move → Feature" / "Move → Amendment" — current labels are obtuse to a non-implementor.
- Annotations under each novel UI element explaining design rationale in 1–2 sentences.

**What's out of scope:**
- Python code. Don't write any.
- Qt-specific markup or JavaScript interactivity. Static HTML/CSS rendering only.
- Screen A (bug list), Screen C (Archive search) — those are fine.
- The triage logic, API contract, BUGS.md format, sidecar JSON. Don't touch any of that.

**Process:**
- This is a **parallel** dispatch — CC is producing a competing mockup independently. Please do NOT collaborate or peek at CC's output. Divergent ideas are the point.
- Darrin reviews tomorrow morning, picks a winner, then dispatches a separate scoped implementation task.

**User's verbatim feedback (the source of this task):**
> "It's the most confusing UX I've seen."
> "There is no feedback to the user when buttons are pressed."
> "What is a readiness gap" (jargon unexplained at the surface).
> "Buttons within a window is new to me."
> "Move feature and move amendment is obtuse — what is it."
> "Are all buttons necessary?"
> "Looks and feels out of place" (vs the rest of PG's v4 builds).
> "Use your expertise to analyze the horrendous UX and work with CC and Codex to make something magical, beautiful and INTUITIVE not intimidating."

Make something Darrin would WANT to use, not something he has to grind through.

**Why Extra-High tier:**
- The redesign is a multi-state flow, not a single screen. Each state must be coherent with the others, and the transitions between them are part of the design.
- The brief includes specific user complaints that must each find an answer in the mockup. Don't drop any.
- PG has a strong existing visual language (the Design Bible). The mockup must extend it, not contradict it. Reasoning about consistency vs invention matters.
- Copy matters as much as layout. The "what does this button do" problem is solved through wording, hierarchy, and contextual hints — not through more pixels.

**Reply when done:** Drop a CODEX→CLAUDE report at `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\<timestamp>_CODEX_to_CLAUDE_AM_screen_b_v2_mockup_report.md` summarizing your design rationale, key decisions, the trade-offs you considered, and any open questions for Darrin. Reference the deliverable path.
