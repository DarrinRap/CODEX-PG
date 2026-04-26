# CODEX -> CLAUDE: AM Screen B v2 cross-review of CC mockup

## 1. What CC Did Better

### 1. Canonical PG right-pane discipline

CC kept the redesign inside a PG-native 320px right-pane grammar instead of widening the assistant into a larger two-column workspace. The mockup feels closer to `v4_0_edit_image_mockup.html`: same section rhythm, same status-bar language, same compact right-side density.

**Why it is better:** Darrin's "looks and feels out of place" complaint matters as much as the confusion complaint. My mockup solved confusion partly by giving the assistant more space, but that risks making AM feel like a separate tool. CC proves the UX can be clarified inside the PG visual contract.

**Recommendation:** Steal as-is as the implementation base, with one caveat: keep the current AM 360px width available if real Qt text wrapping makes 320px too cramped.

### 2. Step bar as a real workflow model

CC's top guidance bar does more than show "1 Triage -> 2 Resolve gaps -> 3 Build prompt." It changes labels and counts with the state: "Triage running...", "Resolve gaps (2 of 5)", "Build prompt", or "Reclassify" when the verdict branches.

**Why it is better:** This directly answers "It's the most confusing UX I've seen." The user is not just seeing decorative breadcrumbs; the chrome tells them what AM currently wants from them. My version had the right concept but less precise state vocabulary.

**Recommendation:** Steal as-is.

### 3. Disabled-button promise text

CC puts explanatory status text directly under the CTA: "Available once all 5 gaps are resolved," "3 gaps still need a decision," "All gaps resolved. Ready to ship to Claude Code." That turns a disabled button into an instruction.

**Why it is better:** "Are all buttons necessary?" is partly a button-presence problem, but also a "why is this button here now?" problem. Promise text makes a greyed-out button teach the rule instead of becoming dead chrome.

**Recommendation:** Steal as-is. This should be in v4.41.

### 4. Gap-row action model

CC uses `_ChecklistRow` more faithfully: thin left stripe, hairline separators, one visible `Decide...` button, and one quiet "Already addressed" text affordance. My selected-gap footer reduces per-row buttons, but creates distance between the gap and its action.

**Why it is better:** For a fresh user, the action lives where the blocker lives. It avoids the old stacked mini-button pile while keeping the interaction local. It also addresses "buttons within a window is new to me" more gently than my larger footer action area.

**Recommendation:** Adapt with changes. Use CC's inline row action model, but keep row actions visually sparse and consider moving to a selected-row footer if a bug has very long gap text or many gaps.

### 5. Reclassify pane with full-sentence choices

CC's reclassify state is much stronger than mine. It unfolds an inline pane with plain-language choices, destination subtext, and a `RECOMMENDED` chip. "Move -> Feature" disappears completely.

**Why it is better:** This is the cleanest answer to "Move feature and move amendment is obtuse - what is it." It uses language a non-implementor can understand and makes the recommended path obvious without hiding alternatives.

**Recommendation:** Steal the inline choice pane. For the final file-moving action, still use a confirmation step that names the destination.

### 6. Verdict card translation

CC translates internal classifications into user-facing verdicts like "Needs your input first" while preserving the underlying class as a small mono tag for verification. My mockup exposed more raw classification language.

**Why it is better:** It reduces jargon at the surface without removing precision. That is exactly the move needed for "What is a readiness gap" and the general first-user confusion.

**Recommendation:** Steal as-is.

### 7. Bottom status bar feels more PG-native

CC reused the PG status-bar grammar as the persistent feedback surface: mode label, pulse dot, message, mono meta. My larger status pane is clearer in isolation but less native to the PG shell.

**Why it is better:** "There is no feedback" needs a persistent answer, but the answer should not feel bolted on. CC's status bar looks like it belongs to PG.

**Recommendation:** Adapt. Use CC's bottom status bar as the always-on feedback surface, and reserve larger inline status cards for error/recovery or first-run explanations.

## 2. What My Mockup Got Wrong By Comparison

### 1. I over-widened the assistant surface

**What I did:** I deliberately broke out of the current 360px right-column convention and made Screen B feel like a wider split workspace.

**What CC did instead:** CC stayed inside the canonical PG right-pane size and made the content work through sharper hierarchy and copy.

**Assessment:** My instinct was understandable because the current AM pane is cramped, but CC's result is more implementation-ready and more faithful to the Design Bible. I retract the width change as the default implementation recommendation.

### 2. My selected-gap footer added indirection

**What I did:** I removed actions from gap rows and put `Record decision` / `Mark resolved` in a selected-gap footer.

**What CC did instead:** CC kept one direct `Decide...` action on each gap row and made the secondary path a quiet link.

**Assessment:** My version reduces button clutter, but CC's version is probably easier for a new user. A user can see a blocker and act on it immediately. My footer model is better only if rows become too dense in Qt.

### 3. My reclassify path was too modal-first

**What I did:** I showed a destination confirmation modal as the main reclassify experience.

**What CC did instead:** CC showed an inline decision pane with full-sentence choices and a recommended option.

**Assessment:** CC is better for understanding. My modal is still appropriate as the last confirmation before moving files, but it should not be the first reclassification surface.

### 4. My status pane was clearer but less native

**What I did:** I created a prominent persistent status pane in the assistant column.

**What CC did instead:** CC used the PG-style bottom status bar plus inline CTA status text.

**Assessment:** My status pane is a good teaching surface, but CC's status bar is a better default surface. I would keep a compact inline status card only for first-run explanation, errors, or file-write confirmation.

### 5. I underused promise text

**What I did:** I greyed unavailable actions and added some explanatory selected-gap copy.

**What CC did instead:** CC put explicit "what unlocks this" text under disabled actions.

**Assessment:** CC is plainly better. Disabled affordances need reasons, not just dim styling.

## 3. What I Still Believe My Mockup Got Right

### 1. Spaciousness is not the enemy

I retract the widened layout as the default, but not the concern behind it. AM can produce real five-gap or longer cases, and if the Qt implementation wraps into tiny fragments at 320px, the implementation should not preserve 320px out of purity. CC's copy discipline makes 320px plausible; user testing should decide whether it is comfortable.

### 2. A separate selected-gap detail area is still useful for complex gaps

CC's row-local actions are better for the common case. My selected-gap area is still worth keeping in reserve if future gap rows need richer detail, long evidence excerpts, or multi-line decision previews. Do not ship it for v4.41 unless the row model proves too cramped.

### 3. Final confirmation should stay explicit

CC's inline reclassify pane is better for choosing a path. My modal confirmation is still the safer final step before AM moves a bug out of `BUGS.md` or into the backlog. The synthesis should be: inline choice first, confirmation second.

### 4. Error and file-safety copy should stay explicit

Both mockups do this, but I still think the implementation must say whether files changed after failures: "No files were changed" is not optional. AM edits `BUGS.md`; user trust depends on exact file-side-effect copy.

### 5. Do not steal CC's dimmed left-column idea wholesale

In CC State 2, the left bug content dims during triage. It looks nice and focuses attention, but in a real tool the user may want to keep reading while the 30-second call runs. I would not dim the bug content strongly in implementation; disable controls, not reading.

## 4. Synthesis Recommendation

Recommendation: **CC base + selected Codex additions.**

Use CC as the structural and visual base for v4.41:

- 320px PG-native right pane unless Qt wrapping fails.
- CC's state-aware step bar.
- CC's verdict card and plain-language classification labels.
- CC's gap rows: left stripe, one `Decide...` button, quiet "Already addressed" link.
- CC's disabled-button promise text.
- CC's bottom status bar plus inline CTA status line.
- CC's inline reclassify pane with full-sentence options and recommended chip.

Port these Codex additions into that base:

- Stronger explicit file-safety copy for errors and write confirmations.
- A final confirmation dialog for reclassify actions that actually move files.
- A fallback selected-gap detail pattern if row-local actions prove too cramped with real Qt text.
- Keep the option to widen AM's right pane to the existing 360px if 320px fails in implementation testing.

This is not a 50/50 blend. CC's mockup is the better implementation foundation because it solves confusion while staying inside PG's established surface grammar. Codex's useful contribution is mostly safety copy, confirmation flow, and a pressure-relief option for dense gap detail.

## 5. Open Questions For Darrin

1. Should AM v4.41 target the canonical 320px right pane, or preserve the current AM 360px width for readability?
2. Should reclassification use CC's inline pane plus a final confirmation dialog, or should the first shipped version use the existing `DarkChoiceDialog` path for implementation speed?
3. Should gap rows always show `Decide...`, or should only the active/selected gap show an action?
4. During triage, should the bug content remain fully readable, or dim to focus attention on the running API call?
5. Is "Already addressed" the right plain-language replacement for "Resolve without decision," or does Darrin prefer "Mark resolved"?
