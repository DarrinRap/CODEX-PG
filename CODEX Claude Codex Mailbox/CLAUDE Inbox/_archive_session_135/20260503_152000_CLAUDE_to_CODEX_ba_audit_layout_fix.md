---
schema_version: 1
message_id: 20260503_152000_CLAUDE_to_CODEX_ba_audit_layout_fix
from: CLAUDE
to: CODEX
date: 2026-05-03T22:20:00Z
subject: FIX — PG_Design_Bible_Audit_v1.html layout overflow + element repositioning
status: dispatched
thread_id: ba_audit_layout_fix_v1
requires_darrin_decision: false
approval_boundary: rtc
---

# Fix: Bible Audit Applet — Layout Overflow + Element Repositioning

## What Darrin reported

Darrin took a screenshot showing only the titlebar strip of the applet:

```
| Panda Bible Audit – v1.4.0          [EVIDENCE AUDIT] |
```

The titlebar is the thin macOS-style mock window header (the `.titlebar` div inside `.window`).
The issue: **the content overflows the viewport, requiring scrolling.** Everything must fit in one viewport with no scroll.

## File

`C:\panda-gallery\workflows\design\applets\PG_Design_Bible_Audit_v1.html`

## Root cause

The current page structure has decorative outer content ABOVE the `.window` div:

```html
<div class="page-title">Bible Audit - Compact UX</div>
<div class="page-sub">PG - live production shell aligned to CC Compact UX v3</div>
<div class="state-eyebrow" id="state-eyebrow">BA - LIVE SERVER</div>
<div class="state-title" id="state-title">Evidence-backed single-app audit console</div>
<div class="state-sub" id="state-sub">Run exactly one selected app...</div>
<div class="window">
  <div class="titlebar">
    ...
    <div class="titlebar-title">Panda Bible Audit - v1.4.0</div>
    <div class="mode-badge" id="mode-badge">EVIDENCE AUDIT</div>
  ...
```

These outer elements push the `.window` downward and cause the page to be taller than 100vh.

## Required fix

### 1. Remove the outer decorative elements

Delete (or hide) these elements from the DOM — they add no functional value and cause overflow:

- `.page-title` ("Bible Audit - Compact UX")
- `.page-sub` ("PG - live production shell...")
- `.state-eyebrow`
- `.state-title`
- `.state-sub`

### 2. Make the `.window` fill the full viewport

Update `.window` CSS so it fills the entire browser window:

```css
.window {
  width: 100vw;
  height: 100vh;
  margin: 0;
  border: none;
  border-radius: 0;
  box-shadow: none;
  overflow: hidden;
  display: grid;
  grid-template-rows: 30px 2px minmax(0, 1fr);
}
```

Remove the `width: min(1280px, calc(100vw - 64px))`, `height: calc(100vh - 260px)`, and `margin: 0 32px 28px` values that currently constrain it.

### 3. Update body

```css
body {
  margin: 0;
  overflow: hidden;
  height: 100vh;
}
```

### 4. The titlebar elements stay where they are

Darrin said "move these" — meaning the titlebar ("Panda Bible Audit – v1.4.0" + "EVIDENCE AUDIT" badge) should remain inside `.titlebar` exactly as now. The fix is removing everything ABOVE the window, not moving the titlebar contents.

The `.titlebar` layout is already correct:
```css
.titlebar {
  display: grid;
  grid-template-columns: 92px minmax(0,1fr) auto;
  align-items: center;
  height: 30px;
}
```
- Col 1: traffic lights (left)
- Col 2: `titlebar-title` "Panda Bible Audit – v1.4.0" (center)
- Col 3: `mode-badge` "EVIDENCE AUDIT" (right)

Do not change this layout.

### 5. Verify no scrolling

After the fix, `body { overflow: hidden }` and `.window { height: 100vh }` together must prevent any scrollbar from appearing. Test at 1080p and 768p viewport heights.

## Mockup required

Per standing mockup protocol: produce `ba_audit_layout_fix_v1.html` in `C:\panda-gallery\workflows\design\mockups\ba_audit_fix_v1\` showing:

| State | Description |
|-------|-------------|
| Fixed layout | Full-viewport applet — titlebar at top, content fills rest, no scrollbar visible |

The mockup should show the full applet at 1280×768 viewport. One state only.

File RTC with mockup path. No edits to `PG_Design_Bible_Audit_v1.html` until Darrin approves the mockup.

## AC

- AC-1M: Mockup shows the applet filling the full viewport with no vertical scrollbar visible.
- AC-2M: "Panda Bible Audit – v1.4.0" and "EVIDENCE AUDIT" are visible in the titlebar at the top of the window.
- AC-3M: No outer decorative elements (page-title, page-sub, state-eyebrow, state-title, state-sub) visible.

— CD · 2026-05-03 · session 129
