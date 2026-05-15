---
schema_version: 1
message_id: 20260511_000500_CODEX_to_CD_vellum_science_ux_audit_rubric
thread_id: VELLUM-BUGFIX-20260508
from: CODEX
to: CLAUDE
date: 2026-05-11T00:05:00-07:00
subject: ADDENDUM -- Vellum science-based UX audit rubric for one visible screen
in_reply_to: 20260510_201500_CODEX_to_CD_vellum_bible_failures_line_list
type: rtc_addendum
priority: high
status: report_only
---

# Addendum — Science-Based UX Audit Rubric for Vellum

Darrin supplied a Top 50 science-based UX principle list and asked Codex to proceed. This addendum is Vellum-only and does not reopen broad UI/UX, PAH, PC, PG overhaul, Relay, or cleanup work.

## Why this is separate from BA

BA answers: does Vellum violate the PG Design Bible?

This rubric answers: even if Bible-compliant, does the one visible Vellum screen feel usable, discoverable, forgiving, and trustworthy when Darrin uses it?

This should be used as a second-pass screen audit alongside the existing gate:

mockup target -> real PySide screenshot -> compare deltas -> fix/verify loop

## Recommended Vellum UX Audit Scope

Audit only the current one-screen Vellum result, not the whole app. For each item below, compare the intended mockup contract against the real PySide screen and record visible deltas.

### 1. Trust and Feedback

Relevant principles: visibility of system status, immediate feedback, clear loading states, perceived performance, non-blocking background tasks.

Checks:

- Packet load state is visible and unambiguous.
- Decision save state is visible immediately after action.
- Export action shows success/failure/progress feedback.
- BA preflight chip state is readable and not stale-looking.
- Long operations do not freeze the UI without feedback.
- Status bar text explains current mode/action plainly.

### 2. Discoverability and Recognition

Relevant principles: recognition over recall, signifiers, affordances, tooltips/inline help, discoverability of advanced features.

Checks:

- Split, flip, export, filter, approve/reject, notes, and checklist controls are visible or discoverable without memorizing shortcuts.
- Icons/buttons visually suggest their function.
- Tooltips explain actions without placeholder/stub language.
- Keyboard shortcut hints are present where useful but do not clutter the screen.
- Advanced controls do not hide the primary path.

### 3. Cognitive Load and Information Hierarchy

Relevant principles: reduce cognitive load, chunking, progressive disclosure, Hick's Law, strong information hierarchy, minimalist design.

Checks:

- The screen has one obvious primary task: evaluate the real PySide screenshot against the target/mockup.
- Decision panel, notes, checklist, status, and preview are grouped clearly.
- Secondary controls do not compete visually with the screenshot comparison.
- Text density is scan-friendly.
- The user does not need to infer which item is active, reviewed, blocked, or ready.

### 4. Error Prevention and Recovery

Relevant principles: error prevention, undo/recovery, user control/freedom, inline validation, plain-language errors, useful confirmation.

Checks:

- Invalid decisions are prevented while split/flip modes are active.
- Destructive actions require useful confirmation only when needed.
- Undo/redo exists for annotations and is easy to find.
- Packet errors explain what is wrong and what to do next.
- Failed live capture/export/file operations give plain-language recovery steps.
- User can back out of accidental decisions or pending confirmations.

### 5. Layout, Targets, and Accessibility

Relevant principles: Fitts's Law, large click targets, natural mapping, keyboard navigation, visible focus states, accessibility by default, contrast, readable typography, responsive desktop layouts, density control, reduced motion.

Checks:

- Primary controls are large enough and easy to hit.
- Controls sit near the content/state they affect.
- Keyboard focus is visible on all interactive controls.
- Tab order follows the visible workflow.
- Contrast is sufficient in the actual PySide screenshot, not just the HTML mockup.
- Resizing the window does not clip critical controls or text.
- Any motion clarifies state and respects reduced-motion expectations.

### 6. Workspace Memory and Expert Flow

Relevant principles: persistent workspace memory, search everywhere/command palette where relevant, keyboard shortcuts, context menus, predictable navigation.

Checks:

- Window/pane state persistence is either implemented or explicitly out of scope for this one-screen gate.
- Shortcuts shown in UI actually work.
- Context actions are available where expected, but not required for the primary path.
- Navigation and active item state remain stable after decisions, filters, split/flip toggles, and exports.

## Highest-Risk Vellum Screens/States To Capture

For the one-screen visible-result loop, capture real PySide screenshots for:

1. Default loaded packet, actual-size view, first actionable item selected.
2. Split-view active with actual/mockup labels visible.
3. Flip mode active with decision controls disabled.
4. Decision confirmation pending state.
5. Export success or failure state.
6. Malformed/no-packet empty/error state.

## CD Recommendation

Use this rubric to classify screenshot deltas into:

- `blocker`: prevents Darrin from trusting or completing the one visible review task.
- `must-fix-before-demo`: visible usability/design issue on the primary screen.
- `defer`: valid UX debt outside the one-screen Vellum result.

Do not dispatch broad UX polish. Dispatch only defects that are visible in the real PySide screenshot or directly block the one-screen Vellum review workflow.

— Codex
