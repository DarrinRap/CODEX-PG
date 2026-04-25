# CODEX PG Interface Storyboard Notes v1

This folder contains Codex-owned visual planning for the PG Testing + Audit desktop interface. It is separate from Claude's `C:\panda-gallery` workspace.

## Design Goal

The interface should feel like a professional desktop tool for guided testing and audit review. The tester should move quickly through a session without managing files. PG should receive a calm, searchable, evidence-backed approval queue.

## Core Experience Principles

1. One obvious next action

   Every state should make the next action visually clear. Secondary controls stay visible but quieter. This is especially important for testers who are trying to focus on the app under test, not the testing harness.

2. Evidence stays attached to decisions

   A failure, screenshot, transcript timestamp, and AI summary should travel together. The user should not need to remember where a screenshot was saved or which transcript line explains it.

3. Capture is fast by default

   Region capture should save immediately. Review is useful, but optional. This keeps Shift+F12 feeling lightweight, close to the speed of Win+Shift+S.

4. AI organizes, PG approves

   AI should split sessions into issues, categorize them, and draft response language. It should not silently send anything. PG approval remains the trust checkpoint.

5. The archive is part of the product

   Closed issues should become searchable audit records with evidence and response history. This supports future debugging, repeat issue recognition, and accountability.

## Step-by-Step Interface Rationale

### 1. Preflight

The preflight screen exists to prevent bad sessions. It confirms microphone, transcript, screenshot capture, and Dropbox readiness before the tester starts. This is calmer than discovering a missing transcript or upload failure after the session.

### 2. Guided Testing Pane

The guided pane should stay compact and predictable. The tester reads the instruction, performs the action in the real app, then answers PASS, FAIL, or SKIP. The bottom action bar should stay visually stable across states.

### 3. Region Capture

Shift+F12 opens a dim overlay on the active display. The selected area is shown as a bright cutout with a peach border. The banner keeps the mode understandable and makes Esc cancellation obvious.

### 4. Capture Review

After capture, a toast confirms success. Clicking the toast opens review. If the tester ignores the toast, the image remains saved and attached.

Review choices:

- Save: close dialog, keep file as-is.
- Discard: delete file and remove it from session JSON.
- Re-capture: delete file and immediately re-enter capture mode.

### 5. Fail With Evidence

When FAIL is selected, the interface asks for a concise note and shows attached evidence. The screenshot and transcript timestamp should be visible near the note so the tester sees exactly what will be sent into audit processing.

### 6. Package and Upload

At session end, the user sees a simple package manifest and upload progress. This makes the workflow feel trustworthy without exposing raw folder structure.

Required package contents:

- Transcript with timestamps
- Screenshots
- Fail notes
- Step results
- Metadata

### 7. AI Triage Queue

The queue is the first PG-facing view after backend processing. It should show priority, issue summary, evidence count, transcript anchor, and review status. The right panel previews the selected issue.

### 8. Approval

PG reviews evidence and the drafted response side by side. The response can be edited before sending. The send action should clearly indicate that it uses the shared team email.

### 9. Searchable Archive

Resolved issues move into an archive that is searchable by phrase, category, priority, date, and status. Each archive record should preserve original evidence, transcript anchors, and the approved response.

## Visual Language

The storyboard follows the existing Panda Gallery vocabulary:

- Dark shell background
- Compact panes
- Low-radius controls
- Muted borders
- Peach active accent
- Green pass state
- Red fail state
- Quiet grey secondary text
- Hairline row separators instead of heavy cards

## Files

- `CODEX_step_by_step_ui_storyboard_v1.html`: visual storyboard with nine user interface states.
- `CODEX_interface_storyboard_notes_v1.md`: this design explanation document.
