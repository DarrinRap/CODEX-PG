---
schema_version: 1
id: CLAUDE-20260428-162000-a53-relay-setup-mockups
thread_id: A53-RELAY-TESTER-SETUP-UX
created_at: '2026-04-28T16:20:00-07:00'
from: claude_desktop
to: codex
type: dispatch
priority: high
status: shipped
thread_status: active
action_owner: codex
requires_darrin_decision: false
approval_boundary: darrin_go_required_before_implementation
tier: extra_high
---

# Claude Desktop -> Codex: A53 — Relay Tester Setup UX Mockups

## Task

Produce a single comprehensive HTML mockup file covering all 9 screens of the
Relay tester setup flow, presented in Q&A format with full-screen renders and
graphical decision snippets. This is a UX design deliverable — not implementation.

**Deliverable:**
`C:\panda-gallery\workflows\design\pg_general_mockups\relay_tester_setup_v1.html`

---

## Mandatory reading — complete ALL of these before writing a single line of HTML

Read in this exact order. Do not skip any. Each one informs the next.

### 1. Design Bible (canonical visual authority)
`C:\panda-gallery\workflows\design\PG_DESIGN_BIBLE_v1.md`
Read end-to-end. Every color, font, spacing, component, and philosophy decision
you make must be grounded here. Pay particular attention to:
- §1 Design philosophy (medical, restrained, clinical precision)
- §2 Color system (full token table — use ONLY these hex values)
- §3 Typography (two-family system, type scale, mono usage rules)
- §4 Spacing, radius, motion
- §6 Component grammar (`.gbtn`, `.setup-screen` patterns, `.mock-window`, etc.)
- §8 Empty-state voice
- §10 Non-negotiables (12 rules — every mockup must pass all 12)
- §14 Visual verification protocol

### 2. Q&A decisions addendum (the locked UX decisions)
`C:\panda-gallery\workflows\design\RELAY_TESTER_SETUP_QA_ADDENDUM_v1.html`
Open and read in a browser or as raw HTML. This contains:
- Q1–Q9: every locked UX decision for the setup flow
- Issue fixes 1–12: corrections to earlier decisions (these supersede anything that contradicts them)
- The standing design principle: layered UX — automated surface, hidden diagnostics
- Exact copy strings, error messages, and button labels approved by Darrin
- The code format spec: PG- + 2 uppercase letters + 2 digits, excludes O/I/0/1

### 3. Relay spec (feature and workflow authority)
`C:\CODEX PG\CODEX Canonical Specs\RELAY_SPEC_v0.2.md`
Focus on:
- §3 Screen anatomy (Screens 1–7)
- §4 Relay Settings (recipients, auto-ack, role config)
- §5 File/folder structure
- §8 Hub layout and role architecture
- §9 Developer hub
- §14 Tester hub
- §15 Workflow steppers

### 4. Existing Relay mockup (visual baseline)
`C:\panda-gallery\workflows\design\pg_general_mockups\relay_module_v1.html`
Open and study. Your mockup must feel like it belongs in the same app.
Inherit shell chrome, statusbar, panel grammar, and palette from this file.

### 5. Screen C design decisions
`C:\panda-gallery\workflows\design\RELAY_SCREEN_C_DESIGN_v1.md`
Q1–Q10 locked hub decisions. Relevant for Darrin's Settings panel (Screen 9).

### 6. Dropbox integration verification
`C:\panda-gallery\scripts\dropbox_integration_test.py`
Read the docstring and test suite. Understand what the PKCE auth flow actually
does so the Step 1 mockup (Connect Dropbox) accurately reflects what happens:
- `DropboxOAuth2FlowNoRedirect` with `use_pkce=True` and `token_access_type='offline'`
- Browser opens, user clicks Allow, pastes an auth code back into PG
- No app secret required
- Token stored via QSettings — persists across sessions

---

## The new-user lens (mandatory perspective for every design decision)

You are designing for **Rebecca Chen** — a remote dental practice employee who:
- Has never used Panda Gallery before
- Is not a developer or technical user
- Has received one email from Darrin with a 6-character code
- Has just downloaded and opened PG for the first time
- Does not know what Dropbox is, what PKCE means, or what a "channel path" is
- Will get confused if anything requires her to make a technical decision

**The core UX test:** At every screen, ask yourself:
1. Does Rebecca know exactly what to do next without reading anything carefully?
2. Is there exactly one obvious action?
3. If something goes wrong, does she know what happened and what to do?
4. Could she complete this setup in under 3 minutes with zero prior knowledge?

If the answer to any of these is "maybe" — redesign until the answer is "yes."

This is not a developer tool. It is not the Audit Module. It is a non-technical
user's first experience with PG. Every pixel must serve that reality.

---

## The 9 screens to mockup

Each screen is a full-screen render (1280×800px design viewport) of the Relay
setup window at that moment. The setup window is NOT the full PG app shell —
it is a focused setup wizard window, clean, centered, no module tabs, no tool strip.

### Screen 1 — The invite email (Rebecca's inbox)
What Rebecca sees BEFORE opening PG. Not a PG screen — her email client.
Show a realistic email with:
- From: Darrin's email address (darrin@[practice].com)
- Subject: "I've added you to Panda Gallery Relay"
- Body: install link (github.com/[repo]/releases/latest) + invite code PG-X4K9
- The code rendered large and peach, prominent
- "PG will walk you through the rest. Takes about 2 minutes."
Style as a light-background email client (contrast with PG's dark UI — the email
is OUTSIDE PG). Shows the world Rebecca is coming from.

### Screen 2 — First open: Relay welcome
First PG screen Rebecca sees. The setup wizard has not started yet.
Shows a clean welcome with:
- PG brand mark + "Panda Gallery" wordmark (peach gradient, Bible §3.5)
- "Relay" label as the module context
- Hero: "You've been invited to Relay"
- Sub-copy: "Darrin has set up a reporting channel. It takes about 2 minutes to connect."
- Single primary button: "Get started →"
- No other options, no settings access, no navigation
Empty-state voice (Bible §8): welcoming, walkthrough, not error-toned.

### Screen 3 — Step 1: Connect Dropbox (idle state)
The wizard at Step 1 of 3. Progress bar visible at top.
- Wizard progress: ① Connect Dropbox · ─ · ② Enter code · ─ · ③ Say hello
- Step 1 active (peach circle)
- Title: "Connect your Dropbox"
- Sub: "You just need a free Dropbox account. No app to install — it all happens in your browser."
- Primary button: "Open Dropbox in browser →"
- Below button: "Don't have an account? Create one free at dropbox.com" (dim, small)
- No other options or distractions

### Screen 4 — Step 1: Browser opened, waiting for auth code
State transition: Darrin clicked "Open Dropbox" and a browser tab opened.
PG is now waiting for the auth code. This is the PKCE flow in progress.
- Same wizard layout
- Status: amber spinner + "Your browser is open — sign in to Dropbox and click Allow"
- Below: collapsible "Didn't see the browser?" with "Open again" link
- A code input field labeled: "Paste the authorisation code here" (this is the PKCE code
  that Dropbox shows after the user clicks Allow — a short alphanumeric string)
- Submit button greyed until code is pasted
- This screen must not alarm Rebecca. The copy must feel like "almost done" not "technical step"

### Screen 5 — Step 2: Enter invite code (idle state)
Auth complete. Now entering the channel invite code.
- Wizard: Step 1 done (green ✓) · Step 2 active (peach) · Step 3 pending
- Title: "Enter your invite code"
- Sub: "Darrin sent you a 6-character code in his email."
- Large code input field: monospace, peach text, center-aligned
- Placeholder text: "PG-XXXX" in dim
- Auto-advances when 6 valid characters are entered (no Submit button needed)
- Below: "Need the code? Check the email from Darrin." (small, dim)

### Screen 6 — Step 2: Code entered, auto-testing
Transition state after Rebecca finishes typing. Tests are running automatically.
- Same layout
- Code field shows "PG-X4K9" (filled, locked — not editable during test)
- Status: peach spinner + "Checking code…"
- No button visible — this is fully automatic
- Duration: visually implies "a few seconds" — not scary

### Screen 7 — Step 3: Saying hello (in-flight)
Connection verified. Auto-sending the test hello to Darrin.
- Wizard: Steps 1+2 done (green ✓) · Step 3 active (peach)
- Title: "Say hello to Darrin"
- Sub: "Sending a quick test to confirm everything works…" + dim note "usually takes a few seconds"
- Status: peach spinner + "Waiting for Darrin to confirm…"
- Darrin's Relay inbox card shown (smaller, to the right or below):
  "📬 Relay setup test · Rebecca is finishing setup · [Got it ✓]"
  Label it: "What Darrin sees in his Relay app"
- This dual-view helps Rebecca understand WHY she's waiting

### Screen 8 — Setup complete
All steps done. Darrin confirmed.
- Wizard: all 3 steps done (green ✓)
- Large green checkmark
- Title: "You're all set!"
- Sub: "Darrin got your hello. You're connected."
- Separator + "WHEN YOU FIND A BUG" section:
  1 · Open Relay and tap the New Report tab
  2 · Record what you saw — just speak naturally
  3 · Tap Send to Darrin — done
- Primary button: "Open Relay →"
- These 3 steps shown ONCE only — never again

### Screen 9 — Darrin's Settings: Invite a tester
Darrin's view in Relay Settings. Separate from Rebecca's flow.
Full-width panel showing:
- "TESTERS" section head (peach caps)
- Rebecca Chen row: avatar initials "RC", code PG-X4K9, Active status (green dot), Connected date, Revoke button
- "+ Invite another tester" area with: Name field, Email field, "Open invite in email →" primary button
- Below the button: "Opens your email app with the message already written. Just hit Send."
- "Advanced diagnostics" collapsed disclosure (Bible layered UX principle):
  Shows when expanded: Token status, Last sync, Channel path, SDK version, ↻ Force re-test, View full sync log
- "Installer download URL" field in Settings showing github.com/[repo]/releases/latest with a Change button

---

## Format requirements

### Full-screen renders
Each of the 9 screens must render as a **full 1280×800px window** — not a thumbnail,
not a card. The user should be able to look at each screen and immediately understand
what Rebecca (or Darrin) would see on their actual monitor.

### Q&A format alongside each screen
Each screen section in the HTML must include:
1. **Screen title and number** (e.g. "Screen 3 — Step 1: Connect Dropbox")
2. **The UX question it answers** (e.g. "How does PG ask Rebecca to connect Dropbox without requiring technical knowledge?")
3. **The full-screen render** of that screen
4. **A UX analysis block** (small, below the render) answering:
   - What decision does this screen make for Rebecca?
   - What's the single obvious action?
   - What happens if something goes wrong here?
5. **A "new user test" verdict** — a one-line plain-English assessment:
   "Pass: Rebecca knows exactly what to do." or flag any concern.

### Document structure
```
[Doc header: title, date, authority docs read, status]
[Introduction: the new-user lens — who is Rebecca?]
[Screen 1] → [Screen 2] → ... → [Screen 9]
[UX synthesis: overall flow assessment]
[Outstanding questions for Darrin]
```

---

## Design constraints (non-negotiable)

1. **Bible §10 — all 12 non-negotiables apply.** Every screen passes before you
   consider it done. Run the removal test on every element.

2. **Bible §1.4 — screen real estate budget.** The setup wizard is focused.
   No wasted chrome. No decorative elements. No redundant labels.

3. **Bible §1.5 — every element earns its presence.** If removing an element
   loses nothing of substance, remove it.

4. **Bible §1.6 — progressive disclosure.** Only show what Rebecca needs right
   now. Future steps are shown in the progress bar but not detailed. Past steps
   are shown as complete but not editble.

5. **Single primary action per screen.** One `.gbtn.primary` maximum. Never two
   competing peach buttons.

6. **Copy must be plain English.** No jargon. No "PKCE", no "OAuth", no "channel
   path", no "token". If you catch yourself writing a technical term that Rebecca
   would not understand, rewrite it.

7. **Error states must be specific.** Q7 decisions locked: each failure type gets
   its own plain-English message + one next step. Do not write generic "Something
   went wrong" messages.

8. **The setup wizard window is standalone.** It does not have PG's module tabs,
   tool strip, filmstrip, or right panel. It has: a title bar (PG brand mark +
   "Relay Setup"), the wizard content, and the statusbar. Nothing else.

9. **Darrin's screens (Screen 9) use the full PG module shell.** Settings is
   inside PG's normal app chrome. The tester setup flow (Screens 2–8) is the
   standalone wizard.

10. **All hex values from the Bible token table only.** No off-palette colors.
    The Bible tokens are the complete palette — do not introduce new values.

---

## Code format spec (use consistently across all screens)

```
Format:    PG- + 2 uppercase letters + 2 digits
Example:   PG-X4K9
Length:    7 characters including prefix
Case:      Always uppercase
Excluded:  O, I (letters) · 0, 1 (digits)
Charset:   A-Z minus O,I · digits 2-9
```

The code appears on Screens 1, 5, 6, 9. It must be visually identical across
all screens: monospace, peach color (`--accent #e8a87c`), large enough to read
without squinting, prominent but not oversized.

---

## Error states to include

Each of the following must appear somewhere in the mockup as an error state
variant (can be shown as a small state panel below the relevant screen, not
a full-screen render):

| Error | Message | One next step |
|---|---|---|
| Dropbox auth failed | "Dropbox didn't authorise PG" | Click Allow on the Dropbox page |
| Wrong/revoked code | "Code not recognised" | Ask Darrin to resend |
| No internet | "No internet connection" | Connect to wifi and try again |
| Hello not received | "Darrin hasn't confirmed yet" (amber, not red) | Ask Darrin to open PG and check his Relay inbox |

---

## What Codex should NOT do

- Do not invent new colors, spacing values, or component patterns
- Do not add decorative elements (gradients, glows, shadows not in the Bible)
- Do not write UI copy that uses technical jargon
- Do not add features not in the Q&A addendum or Relay spec
- Do not produce a partial mockup and ask for feedback mid-task — deliver
  the complete 9-screen document in one report
- Do not write implementation code (Python, Qt, etc.) — this is HTML mockup only
- Do not make assumptions about decisions not in the Q&A addendum — flag them
  as open questions in the "Outstanding questions for Darrin" section

---

## Tier

Extra-High. Reasoning: 9 full-screen mockups, Q&A format, new-user UX analysis,
error state variants, Bible compliance verification, synthesis section. This is
the most complex single-screen set we've dispatched. Take the time to do it right.

---

## Reply format

When complete, write to `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\`
with:
- Confirmation that all 6 authority docs were read before starting
- Path to the delivered file
- List of any open questions for Darrin
- Your own UX assessment: did Rebecca pass the new-user test at every screen?
- Any Bible compliance concerns you identified and how you resolved them

Do NOT commit. Darrin reviews mockup before any implementation dispatch.

-- Claude Desktop
