# CODEX PC UI/UX Redesign Spec v1

Status: Draft for Claude Code implementation planning
Date: 2026-05-04
Owner: Codex
Target app: PANDA Collaborator
Audience: Claude Code

## 1. Purpose

Redesign the appearance and interaction grammar of the PANDA Collaborator UI so it feels consistent with the PG Bible design system while preserving all PC production requirements.

This is a UI/UX redesign spec only. It does not authorize backend behavior changes, safety model changes, handoff package format changes, git workflow changes, or broad refactors. The redesign must make the existing PC workflow clearer, calmer, and safer without reducing evidence, guardrails, or operator confidence.

The redesign must preserve PC's current launch model, local-only operating assumptions, health endpoint behavior, and evidence-writing locations unless a separate approved PC production spec changes them.

## 2. Source Requirements

Claude Code must treat these files as normative input before implementation:

- `C:\CODEX PG\CODEX PANDA Collaborator\PRODUCTION_SPEC.md`
- `C:\CODEX PG\CODEX PANDA Collaborator\PC_ACTION_TEST_SPEC.md`
- `C:\CODEX PG\CODEX PANDA Collaborator\CODEX_ACCEPTANCE_REPORT.md`
- `C:\CODEX PG\CODEX Agent Hub\CODEX_PAH_RELIABILITY_AND_DESIGN_SPEC.md`
- `C:\CODEX PG\CODEX BA Disposition Ledger\CODEX_PC_LAST_VALIDATION.json`
- Current PC UI implementation and applets under `C:\CODEX PG\CODEX PANDA Collaborator`

If any instruction in this spec conflicts with PC safety requirements, PC safety wins. If a visual preference conflicts with PG Bible design requirements, PG Bible wins. If current implementation differs from this spec, Claude Code must document the delta before changing code.

## 3. Non-Negotiable Safety Rules

The redesign must preserve PC's safety-first contract.

Forbidden behavior:

- Do not run or expose destructive git operations:
  - `git reset --hard`
  - `git clean -fd`
  - `git clean -xdf`
  - `git push --force`
  - `git checkout .`
  - `git restore .`
  - local or remote branch deletion
- Do not create any UI that implies PC can safely restore or mutate a working tree unless the underlying production spec explicitly supports it.
- Do not convert passive indicators into controls.
- Do not make any action look safer than it is.
- Do not hide blocked, warning, dirty, or unknown states behind decorative styling.
- Do not remove evidence surfaces, manifests, logs, package IDs, or handoff details.
- Do not touch `C:\panda-gallery` or Relay files while implementing this redesign unless Darrin explicitly authorizes that scope.

Required behavior:

- PC must leave the target tree untouched when creating safe handoff packages.
- PC must create protection branches at HEAD without checking them out.
- PC must keep stable package IDs.
- Package inspection must remain read-only.
- Create Safe Handoff must remain the dominant primary action and must only appear ready when prerequisites are satisfied.
- Disabled actions must remain visibly disabled and non-clickable.
- Warnings and danger must be visually explicit.

## 4. Design North Star

PANDA Collaborator should feel like a shared-workstation control room: quiet, precise, durable, and impossible to misread under pressure.

The redesign should not feel like a marketing page, dashboard demo, decorative hero, or playful consumer app. It should prioritize repeated operational use:

- Fast scanning
- Clear current user identity
- Clear handoff readiness
- Clear blocked state reasons
- Clear separation between information and actions
- Clear distinction between User 1/User 2 identity and semantic readiness
- Stable layouts that do not jump while status changes

## 5. PG Bible Visual Requirements

### 5.1 Typography

Use the PG Bible UI font stack:

`Segoe UI`, `SF Pro Display`, `SF Pro Text`, `Noto Sans`, system sans-serif

Use monospace only for precision data:

- Paths
- Package IDs
- Branch names
- Commit SHAs
- Timestamps
- Counts
- File names
- Shortcuts
- Versions
- Log excerpts

Do not use monospace for normal labels, headings, button text, instructions, or panel copy.

### 5.2 Color Tokens

Use dark Bible surfaces only:

- `#14141f`
- `#161625`
- `#1a1a2e`
- `#22223a`
- `#2a2a4e`

Required text and semantic colors:

- Text: `#e0ddd5`
- Muted text: `#888888`
- Dim text: `#555555`
- Accent: `#e8a87c`
- Warning: `#f39c12`
- Error: `#e74c3c`

Safe/ready green may be used for enabled safe actions and ready state borders or glyphs. Use a restrained, Bible-compatible green token already present in PC if available; otherwise introduce one token and reuse it consistently.

Do not introduce pale, white, cream, tan, or beige panels. Do not use gradient orbs, bokeh, decorative hero treatments, or one-note purple/blue wash styling.

Do not add new icon, CSS, frontend build, CDN, package manager, or network dependencies for appearance alone. If icons are already available locally, they may be used sparingly. Otherwise use text labels and existing local assets.

### 5.3 Semantic Color Rules

Semantic color must communicate state, not decoration.

- Green: enabled safe action, ready, successful completion
- Grey/muted: disabled, inactive, unavailable, not yet configured
- Amber/warning: caution, needs attention, partially complete, pending operator review
- Red/error: dangerous, blocked, failed, emergency, destructive risk
- User colors: identity only

User identity colors must not be used as readiness colors. User 1/User 2 accents may appear in rails, borders, avatars, tiny badges, section headers, or non-action identity markers. They must not be used as filled primary action backgrounds.

Passive success or ready indicators may use green text, borders, dots, or glyphs, but they must not use the same filled green treatment as enabled safe action buttons. In verification, "green non-actions" means passive elements that visually read as clickable green action buttons.

### 5.4 Shape Grammar

Passive information uses rounded pill chips.

Examples:

- Current branch
- HEAD SHA
- Dirty/clean status
- Package ID
- User role
- Readiness state label
- Test mode label

Actions use squared or lightly rectangular buttons.

Examples:

- Start Session
- Open Folder
- Browse
- Scan Working Tree
- Create Safe Handoff
- Open Package
- Copy Summary
- End Session
- Emergency Pause

Pills must never perform work. Clickable pill-looking controls are visual bugs.

Buttons should follow PG Bible `.gbtn` grammar or a PC-local equivalent:

- Height around 28px for compact controls
- Radius around 4px
- Dark Bible surface background
- Semantic border and text
- UI-font labels
- Icon plus text only where it improves scan speed

Large primary actions may be taller than 28px, but must preserve the rectangular button grammar.

Large primary actions should use a stable height appropriate to their panel, typically 40-52px. They should not resize based on transient status text, loading text, or path length.

## 6. Information Architecture

The UI should keep the current PC workflow visible as an operational sequence:

1. Setup users
2. Select or confirm working tree
3. Start session
4. Review activity and messages
5. Create safe handoff
6. Inspect package
7. End or hand over session

The redesign should make this flow legible without duplicating the same controls in multiple places.

### 6.1 Header and Status Bar

The top region must show:

- App name: PANDA Collaborator
- Active user name in large uppercase text
- Active user role or slot
- Current project or working tree path
- Current branch
- HEAD SHA
- Dirty/clean/unknown state
- Test mode state when applicable

Use a PG Bible chrome/statusbar treatment. A compact statusbar band around 26px high is preferred for precision status. Long paths must truncate in the middle or be placed in a stable horizontal scroller area that does not create page-level horizontal overflow.

### 6.2 Workflow Guide

The five-panel left-to-right guide from PC requirements must remain available on desktop widths. Each panel should represent a real workflow stage, with arrow progression and semantic state:

- Not started
- Ready
- Active
- Needs attention
- Complete
- Blocked

On narrow widths, the guide may collapse into a vertical stepper or compact progress rail. It must not force a desktop column layout that clips or overflows.

Do not duplicate button labels or state copy inside every panel. Each stage should have one short label, one state indicator, and at most one concise reason or next step.

### 6.3 Setup and User Identity

User 1 and User 2 setup must remain side-by-side on desktop and stacked on narrow widths.

Each user setup area must show:

- Display name
- Local path
- Account/git identity evidence
- Registration status
- Handover availability

Use complementary identity accents only as identity markers. Examples:

- Left border stripe
- Small avatar ring
- Header underline
- Tiny role badge border

Do not fill normal safe action buttons with User 1/User 2 accent colors. Handover buttons may include user accent as a border, icon, or small identity stripe, but their enabled/disabled state must still use the semantic action grammar.

### 6.4 Hub Cards

Hub cards should act as compact operational summaries, not decorative cards.

Each Hub card should show:

- User identity
- Setup completeness
- Current path
- Git identity status
- Session state
- Last handoff or last activity
- One clear next action when applicable

Avoid nested cards. Avoid oversized cards. Keep radius at or below 8px unless an existing PC component requires otherwise.

### 6.5 Working Tree Panel

The Working Tree panel must make risk visible.

Required content:

- Selected root
- Branch
- HEAD
- Dirty/clean/unknown
- Untracked/modified count when available
- Last scan time
- Scan errors or blocked reasons
- Path picker controls
- Scan Working Tree action

Layout requirements:

- Path picker owns its own row.
- Browse/Open controls must have stable widths.
- Scan controls must be visually separate from path picker controls.
- Long paths must not expand the page.
- Dirty and unknown states must be prominent without using filled red/amber panels.

### 6.6 Session Controls

Start Session and End Session should be clear, stable, and easy to distinguish.

Start Session:

- Safe action grammar
- Green only when ready
- Grey when blocked
- Shows blocked reason nearby as passive text or chip

End Session:

- Warning grammar when it has consequences
- Must not look like the primary handoff action
- Must preserve any confirmation required by existing PC behavior

### 6.7 Primary Handoff Area

Create Safe Handoff is the dominant primary action.

Required appearance:

- Full-width or wide enough to be visually primary in its panel
- Rectangular action button
- Green when ready
- Grey when blocked
- Clear disabled reason nearby
- No user identity fill color
- No duplicate second primary handoff button elsewhere

The surrounding panel must show exactly what will be included in the handoff package:

- Git root
- Branch
- HEAD
- Protection branch name or status
- Binary patch status
- File copy status
- Manifest status
- Handoff note/status
- Output package path

Use passive pills for these facts.

### 6.8 Package Inspector

Package Inspector must remain read-only.

Required content:

- Stable package ID
- Package path
- Created time
- Source branch and HEAD
- Manifest summary
- Included file count
- Binary patch presence
- Handoff note presence
- Any validation warnings

Allowed actions:

- Open package folder
- Copy package ID
- Copy summary
- View manifest

Disallowed actions:

- Restore package
- Apply patch
- Checkout branch
- Delete package
- Clean working tree

Any future restore preview must be explicitly labeled preview-only unless a separately approved production spec authorizes mutation.

View Manifest is an allowed read-only action. It must not be styled as a restore/apply workflow and must not imply that manifest contents can be edited from the inspector.

### 6.9 Messages and Activity

The messages/status window must have a single visible scrollbar. Nested scrolling regions are allowed only if a contained log viewer genuinely needs its own scroll and does not trap normal page navigation.

Required behavior:

- New messages should not cause layout jumps.
- Status text should not overlap buttons.
- Long log lines should wrap or scroll inside a bounded mono log area.
- Search and filters should be compact and predictable.

Message rows should distinguish:

- Info
- Success
- Warning
- Error
- Waiting on user
- Waiting on other collaborator
- No action needed

### 6.10 Project Manager View

The Project Manager view should be an operational overview of sessions, handoffs, and collaborator state.

Required content:

- Active users
- Recent handoffs
- Open sessions
- Warnings or blocked items
- Daily report/archive links
- Search
- Recommendations
- Collaborator activity

Do not turn this into a landing page. It should remain dense, quiet, and scannable.

### 6.10.1 Plain-English and Technical Views

Where PC already exposes Plain-English and Technical views, the redesign must preserve both.

Plain-English view:

- Explains current state in operator language
- Avoids jargon unless required for safety
- Keeps next action visible

Technical view:

- Shows branch, HEAD, paths, package IDs, manifests, logs, and precise evidence
- Uses monospace only for precision data
- Does not hide safety warnings behind expert-only affordances

Switching views must not reset unsaved inputs, clear logs, change selected paths, or start/stop any session behavior.

### 6.11 Test Mode

TEST MODE must remain visually unmistakable and safely reversible.

Required content:

- TEST MODE state chip
- Bob/Karen fake user state when active
- Sandbox path or clear sandbox indicator
- Quit Test Mode control
- Evidence output status
- Alert colors matching PC action test requirements

TEST MODE must not visually resemble production readiness. Test identity colors must not be confused with User 1/User 2 production identity colors.

### 6.12 Emergency Pause

Emergency Pause must be visually distinct from normal warning states.

Required appearance:

- Red/error semantic treatment
- Rectangular action control
- Clear current pause state
- Clear explanation of what is paused
- Clear path to resume if existing PC behavior supports resume

Do not hide Emergency Pause inside menus or low-contrast secondary areas.

## 7. Interaction Requirements

### 7.1 Button States

Every action button must have:

- Default state
- Hover state
- Focus-visible state
- Active/pressed state
- Disabled state
- Loading state where async work occurs
- Success or failure feedback

Disabled buttons must not be focus traps. Loading states must prevent duplicate submissions where duplicate execution would be unsafe.

### 7.2 Blocked Reasons

Whenever a primary or safe action is disabled, the UI must show the reason close to the action.

Examples:

- Missing User 1 setup
- Missing User 2 setup
- No working tree selected
- Working tree scan failed
- Dirty state unknown
- Session not started
- Package output unavailable
- Test mode active

Use passive text or chips for blocked reasons, not clickable controls.

### 7.3 Keyboard and Focus

Required keyboard behavior:

- Visible focus ring on all interactive controls
- Logical tab order matching visual order
- Escape clears transient focus/search where current applets require it
- Escape returns scroll to origin where current PC layout applet requires it
- No keyboard-only access to disabled or hidden unsafe actions

### 7.4 Copy and Labeling

Use direct operational labels.

Preferred:

- Create Safe Handoff
- Scan Working Tree
- Open Package Folder
- Copy Package ID
- Start Session
- End Session
- Emergency Pause

Avoid vague labels:

- Go
- Submit
- Continue
- Fix
- Magic
- Sync

Copy should state what happened, what is blocked, or what to do next. Do not add visible in-app text describing the visual design system.

## 8. Responsive Layout Requirements

Minimum viewport review set:

- 1750px desktop
- 1366px desktop
- 1100px constrained desktop
- 940px narrow desktop/tablet
- 820px minimum operational width

At every viewport:

- No horizontal page overflow
- No clipped button text
- No overlapping UI text
- No hidden primary action
- No status chip covering another control
- No desktop-only multi-column grid forced onto narrow widths
- Long paths, IDs, and SHAs remain readable or intentionally truncated
- The primary handoff action remains discoverable

If PC must support widths below 820px, Claude Code must add an explicit mobile layout plan before implementation.

## 9. Accessibility Requirements

The redesign must preserve operational accessibility:

- Color cannot be the only state cue.
- Every semantic state needs text, icon, border, or shape reinforcement.
- Contrast must be sufficient against Bible dark surfaces.
- Focus-visible styling must be obvious.
- Buttons must have stable hit targets.
- Tooltips may clarify unfamiliar icons but cannot contain required safety information.
- Reduced-motion users must not depend on animation to understand state.

## 10. Implementation Boundaries for Claude Code

Claude Code should keep changes scoped to PANDA Collaborator UI files and directly related tests/applets.

Before editing, Claude Code must record `git status --short --branch` for `C:\CODEX PG` and identify unrelated dirty files, if any. Unrelated dirty files must not be staged, reverted, reformatted, or folded into the redesign.

Likely allowed files:

- `C:\CODEX PG\CODEX PANDA Collaborator\web\index.html`
- PC-local CSS/JS files if split from `index.html`
- `C:\CODEX PG\CODEX PANDA Collaborator\CODEX_ui_identity_applet.py`
- `C:\CODEX PG\CODEX PANDA Collaborator\CODEX_ui_layout_applet.py`
- `C:\CODEX PG\CODEX PANDA Collaborator\CODEX_pc_action_test_applet.py`
- `C:\CODEX PG\CODEX PANDA Collaborator\tests\test_panda_collaborator.py`
- PC-local documentation or acceptance evidence files

Claude Code must not broaden scope into unrelated CODEX PG subsystems unless a failing test proves a shared dependency must change.

Claude Code must preserve current PC persistence and evidence paths. UI redesign work must not relocate logs, reports, handoff packages, test evidence, or archive files unless explicitly required by an approved production spec update.

If an existing applet or test conflicts with this redesign spec, Claude Code must determine whether the applet is enforcing a production safety requirement or an outdated visual detail. Safety requirements stay. Outdated visual assertions may be updated only with a short note explaining why the new expectation is more faithful to PC requirements and PG Bible rules.

## 11. Recommended Implementation Sequence

1. Inventory current UI components and classify each visible element as passive info, safe action, warning action, dangerous action, identity marker, or log/evidence.
2. Add or normalize PC-local design tokens for PG Bible surfaces, text, semantic states, identity accents, radius, button heights, and focus rings.
3. Convert clickable pill-looking controls into rectangular buttons.
4. Convert passive status/button-lookalikes into non-clickable chips.
5. Correct safe action color grammar so enabled safe actions use green and disabled safe actions use grey.
6. Remove user-colored filled action backgrounds. Replace with identity borders, stripes, badges, or header accents.
7. Redesign header/statusbar and active user presentation.
8. Redesign setup, hub, and handover areas.
9. Redesign Working Tree panel and scan controls.
10. Redesign Create Safe Handoff area as the single dominant primary action.
11. Redesign Package Inspector as read-only.
12. Redesign messages/activity/status window for single-scrollbar behavior.
13. Redesign Project Manager, Test Mode, and Emergency Pause surfaces.
14. Update applets/tests only where they encode superseded visual grammar, not to hide regressions.
15. Run full verification and capture before/after evidence.

## 12. Required Verification

Claude Code must run or document why it cannot run:

- `python -m unittest -v tests.test_panda_collaborator`
- `python CODEX_ui_identity_applet.py`
- `python CODEX_ui_layout_applet.py`
- `python CODEX_pc_action_test_applet.py`
- `.\CODEX_test_panda_collaborator.ps1`

Claude Code should also run the PC BA audit/validator path if an established command exists in the repository at implementation time. If no trusted PC BA command is available, do not claim BA coverage closure; report the remaining coverage gap explicitly.

Claude Code must inspect the live app in a browser after changes. Browser review must cover:

- 1750px width
- 1366px width
- 1100px width
- 940px width
- 820px width

For each viewport, inspect:

- Header/statusbar
- Setup/User 1/User 2 area
- Hub cards
- Working Tree panel
- Workflow guide
- Messages/status window
- Create Safe Handoff area
- Package Inspector
- Project Manager view
- Test Mode
- Emergency Pause

Claude Code must explicitly check for:

- Overlap
- Clipping
- Hidden horizontal overflow
- Duplicate primary actions
- Clickable pill-looking controls
- Green non-actions
- Passive success indicators styled like filled action buttons
- User identity colors used as readiness colors
- Light/cream panels
- Narrow grids forcing desktop columns
- Buttons with truncated or unreadable labels
- Missing blocked reasons
- Missing focus-visible behavior

## 13. Acceptance Criteria

The redesign is acceptable only when all of the following are true:

- PC safety behavior is unchanged.
- Create Safe Handoff remains dominant, rectangular, and green only when ready.
- Disabled primary/safe actions are grey and include nearby blocked reasons.
- Passive chips/pills never perform work.
- Action buttons never look like passive chips.
- User identity colors are not used as readiness colors.
- User 1/User 2 setup remains side-by-side on desktop and stacks cleanly on narrow widths.
- Working Tree controls are separated and do not overflow.
- Messages/status window has one primary visible scrollbar.
- Package Inspector is visibly read-only.
- TEST MODE is unmistakable and reversible.
- Emergency Pause is prominent and semantically red/error.
- No PG Bible color/font/surface requirements are violated.
- Required tests/applets pass or any failure is documented as unrelated with evidence.
- Live browser review confirms no significant visual defects at required widths.
- PC BA validation coverage gap is not worsened; if practical, the redesign should reduce or close the current PC coverage gap.

## 14. Deliverables

Claude Code should deliver:

- Summary of UI files changed
- Summary of tests/applets changed
- Before/after screenshots or viewport notes
- Verification command output
- Pre-edit and post-edit git status summaries
- Any remaining visual risks
- Any PC spec questions that blocked implementation
- Explicit statement that `C:\panda-gallery` and Relay were not touched, unless Darrin authorized that separately

## 15. Open Decisions

Claude Code should resolve these conservatively during implementation:

- Whether to preserve current class names or introduce a PC-local `.gbtn` equivalent. Either is acceptable if rendered behavior matches PG Bible grammar.
- Whether the minimum supported width remains 820px or must extend lower. Do not assume lower-width support without adding explicit layout requirements.
- Whether the current PC BA coverage gap can be closed by applet/test updates during redesign. Do not weaken the validator or mark unknown evidence as trusted without real coverage.
