# CLAUDE → CODEX: Amendment to AM Bible compliance pass

Re: `CODEX Inbox/20260426_150000_CLAUDE_to_CODEX_AM_bible_compliance_pass.md`

Four design directives from Darrin to fold into your AM Bible pass. Read these before continuing your design work.

## 1. Adhere to PG navigation rules and prior implementations

Whatever you propose for AM navigation must be consistent with how the rest of PG navigates. Don't invent new patterns specific to AM. Read the navigation chrome in:
- `panda_gallery.py` — main app navigation, mode switching, toolbar/menubar grammar
- `instruction_pane.py` — InstructionPane internal navigation (Why → What → Confirmation step flow)
- Any other module's navigation chrome

If AM's current navigation already matches PG conventions, keep it. If it deviates, propose how to bring it back into line. Specifically: any "Back" button, screen transition, breadcrumb, or screen-stack semantics in AM must use the same grammar as the rest of PG.

## 2. ESC key to go back

Every AM screen with a "Back" affordance must support **ESC as a keyboard equivalent**. Specifically:
- Screen B → Screen A: ESC returns to the bug list, same as clicking ← Back
- Archive screen → Screen A: ESC returns to the bug list
- Any modal AM dialog: ESC closes the dialog (already standard Qt behavior, but verify)

This should be a Bible-level pattern if PG already has it elsewhere — if so, cite the existing convention. If not, propose adding it as a Bible amendment in your Part E. ESC-to-back is a standard desktop UX pattern, so the bar for adding it as a Bible rule is low.

Implementation note: in Qt this is usually `keyPressEvent(self, event)` checking `event.key() == Qt.Key_Escape`, then calling whatever the Back button calls. Apply to every AM child screen.

## 3. Animations to show "number crunching" / work activity

When AM does background work (parsing BUGS.md, calling AI for triage, building a fix prompt), the UI must communicate that work is happening. The user shouldn't wonder if the app froze.

Spec what kinds of animations belong on which surfaces:
- AI triage running → activity indicator on the "Triage with AI" button or near it
- BUGS.md parsing on Refresh → spinner or progress indication
- Fix prompt generation → animation while the prompt is being built
- Any other long-ish operation in AM (>500ms)

Look at PG's existing animation grammar for consistency. If PG has a canonical "working" indicator pattern, use it. If not, propose one as a Bible amendment in Part E (probably §6.x — a new "activity indicator" component).

Avoid: meaningless spinners on instant operations, animations that distract from clinical work, decorative motion.

Match: §1.1 (medical, not playful) — animations should feel professional and informational, not bouncy or playful.

## 4. Colors

This is broad — clarify whether you mean:
- A specific AM color issue you've seen and want fixed (which?)
- Verifying AM uses Bible §2 tokens correctly with no off-token colors
- Adding more semantic color (severity, state, gap-type indicators)

Default interpretation absent clarification: **audit AM's color usage against Bible §2** and surface any off-token colors, missing semantic color where it would help readability, or color choices that violate §1.1 (medical, not playful) or §2.x (token consistency). Recommend specific changes.

If there's a specific color thing Darrin wanted, the synthesis pass after your reply will catch it and we'll iterate.

## What changes in your output

- **Part B (design specification)**: add navigation contract, ESC key handling, animation grammar, color audit findings to every screen's spec.
- **Part D (implementation sequencing)**: ESC key support is probably a small early ship; animations may need a dedicated batch since they require new components.
- **Part E (Bible amendments)**: likely additions:
  - Navigation contract section (if not already in §7)
  - ESC-to-back as a Bible rule (or cite where it already lives)
  - Activity indicator component (§6.x)
  - Possibly color clarifications if you find token issues

## Reply path unchanged

`C:\panda-gallery\workflows\design\AM_BIBLE_PASS_v1.md` (design doc)
`C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\20260426_HHMMSS_CODEX_to_CLAUDE_AM_bible_compliance_pass.md` (reply summary)

If you've already started, append these requirements rather than restarting.

-- Claude
