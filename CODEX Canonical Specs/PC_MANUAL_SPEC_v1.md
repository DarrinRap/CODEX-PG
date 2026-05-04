# PC Manual Spec v1 — PANDA Collaborator Setup Guide PDF

**Status:** Implementation dispatch to CC
**Date:** 2026-05-05
**Author:** CD
**Output:** `C:\CODEX PG\CODEX PANDA Collaborator\PANDA_Collaborator_Setup_Guide.pdf`
**Audience:** Darrin and Pam — non-technical end users

---

## 0. Guiding Principle

The PDF must look like a real product manual. Every page must answer a question
the reader actually has. Simple language, large clear headings, annotated
screenshots of the live app, and no clutter.

---

## 1. Step 0 — Read These Files Before Writing Anything

CC must read all five before touching Python:

1. `C:\CODEX PG\CODEX PANDA Collaborator\PANDA_COLLABORATOR_SETUP_STEPS.md`
   — authoritative content for all setup and daily-use steps
2. `C:\CODEX PG\CODEX PANDA Collaborator\CODEX settings\panda_collaborator_settings.local.json`
   — exact field values for Darrin and Pam; use these verbatim in all field tables
3. `C:\CODEX PG\CODEX PANDA Collaborator\web\index.html` first 100 lines
   — real CSS design tokens (colours, fonts); all UI illustrations must match these exactly
4. `C:\CODEX PG\CODEX PANDA Collaborator\mockups\pc_redesign_v1\pc_main_operational.html`
   — CC's own redesigned mockup; use this as the visual authority for component layout
5. `C:\CODEX PG\CODEX PANDA Collaborator\CODEX_user_setup_smoke.png`
   — existing real screenshot (1366×768); use as reference for crop coordinates

---

## 2. Screenshots — Capture Strategy

### 2.1 Launch the app

```powershell
Start-Process python -ArgumentList `
  '"C:\CODEX PG\CODEX PANDA Collaborator\panda_collaborator.py" --port 8788'
Start-Sleep 4
```

Note: `--no-browser` is not a recognised flag in `panda_collaborator.py` —
the script is a pure server with no browser-open logic. Drop the flag.

The app is now available at `http://127.0.0.1:8788/` on this machine.
CC runs on the same machine, so it can access localhost.

### 2.2 Capture screenshots via Playwright

Install if needed:
```powershell
pip install playwright --break-system-packages
python -m playwright install chromium
```

Capture script pattern:
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1366, "height": 768})
    page.goto("http://127.0.0.1:8788/")
    page.wait_for_load_state("networkidle")
    page.screenshot(path="shot_hub.png", full_page=False)
    browser.close()
```

### 2.3 Required screenshots

Capture these specific states. If the app shows a different state than described
(e.g. registration screen instead of hub), capture what is actually shown and
note it in the RTC.

| ID | URL / Action | Filename | Notes |
|----|---|---|---|
| S1 | Main hub page, as-found | `shot_hub.png` | Shows whatever state the app is in |
| S2 | Click "GO / Switch to" User 1 button | `shot_darrin_active.png` | Darrin name + amber theme in header |
| S3 | Click "GO / Switch to" User 2 button | `shot_pam_active.png` | Pam name + cyan theme in header |
| S4 | The Create Handoff form (centre panel) | `shot_handoff_form.png` | Zoom into the CREATE HANDOFF section |

If Playwright is unavailable, fall back to the existing smoke screenshot
(`CODEX_user_setup_smoke.png`) and annotated illustrations. Flag this in RTC.

### 2.4 Crop map for the hub screenshot

From the full hub screenshot (1366×768), cut these regions before embedding:

| Crop ID | x | y | w | h | PDF use |
|---|---|---|---|---|---|
| C-HEADER | 0 | 0 | 950 | 75 | Showing the active-user header |
| C-HUB-PANEL | 0 | 95 | 275 | 370 | Left panel with user switcher buttons |
| C-HANDOFF | 305 | 195 | 465 | 265 | Create Handoff form |
| C-FULL | 0 | 0 | 1366 | 768 | Full hub, scaled to 90% page width |

Scale all crops to fit within the page margins (max width 7 inches / 504pt).

### 2.5 Callout annotations

For every screenshot that introduces a UI element, add annotated callout labels
using Pillow before embedding in ReportLab.

```python
from PIL import Image, ImageDraw, ImageFont

def annotate(img_path, out_path, callouts, scale=1.0):
    """
    callouts: list of dict with keys:
        label   — short text (max 6 words)
        tip     — (x, y) on the image where the arrow points
        anchor  — (x, y) where the label box sits
        color   — RGB tuple, default (232, 168, 124) amber
    """
    img = Image.open(img_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    for c in callouts:
        tip = c["tip"]
        anc = c["anchor"]
        col = c.get("color", (232, 168, 124))
        # Line
        draw.line([anc, tip], fill=col, width=2)
        # Arrowhead (small filled triangle at tip)
        _draw_arrowhead(draw, anc, tip, col, size=8)
        # Label background
        font = ImageFont.load_default()
        # Modern Pillow: use textbbox instead of deprecated textsize
        bbox = draw.textbbox((anc[0], anc[1]), c["label"], font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        pad = 5
        box = [anc[0]-pad, anc[1]-pad, anc[0]+tw+pad, anc[1]+th+pad]
        draw.rectangle(box, fill=(20, 20, 31), outline=col, width=1)
        draw.text((anc[0], anc[1]), c["label"], fill=(224, 221, 213), font=font)
    img.save(out_path)

def _draw_arrowhead(draw, from_pt, to_pt, color, size=8):
    import math
    dx = to_pt[0] - from_pt[0]
    dy = to_pt[1] - from_pt[1]
    length = math.hypot(dx, dy)
    if length == 0:
        return
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    p1 = (to_pt[0] - ux*size + px*size//2, to_pt[1] - uy*size + py*size//2)
    p2 = (to_pt[0] - ux*size - px*size//2, to_pt[1] - uy*size - py*size//2)
    draw.polygon([to_pt, p1, p2], fill=color)
```

Required callouts for **S2 (Darrin active hub)**:

NOTE: The pixel coordinates below are approximate, based on the existing
1366×768 smoke screenshot. After capturing the actual S2 screenshot, CC must
open it and verify that each tip coordinate lands on the correct UI element
before generating the final annotated image. Adjust as needed.

| Label | Tip (approx px in 1366×768) | Anchor |
|---|---|---|
| "Active user — Darrin" | (320, 35) | (500, 15) |
| "Switch users here" | (83, 370) | (290, 355) |
| "Start your session" | (460, 421) | (620, 410) |
| "End session / Handoff" | (460, 456) | (620, 445) |

Required callouts for each **registration form illustration** (see §3.2):

| Label | Element |
|---|---|
| "Type your name here" | Name field |
| "Already filled in" | Repo path field |
| "Click when all fields are green" | Register button |

---

## 3. PDF Content — Page by Page

### 3.1 Page 1 — Cover + Introduction

**Cover panel** (full page-width dark band, 100pt tall):
- Background: `#14141f`
- Left: "PANDA Collaborator" · 24pt Helvetica-Bold · white
- Right: "Setup & Daily Use Guide" · 12pt Helvetica · `#888888`
- Below the band: 2pt rule in amber `#e8a87c`

**Two user chips** (side-by-side, immediately below the cover band):
- Left chip: amber-tinted background, amber border.
  Text: "Darrin · User 1 · Amber theme"
  Draw a 10pt filled circle in amber `#e8a87c` to the left of the text.
  Do NOT use emoji — ReportLab's built-in fonts do not render them.
- Right chip: cyan-tinted background `rgba(95,160,168,0.14)`, cyan border `#5fa0a8`.
  Text: "Pam · User 2 · Cyan theme"
  Draw a 10pt filled circle in cyan `#5fa0a8` to the left of the text.

**One-paragraph introduction** (10pt Helvetica, dark body text):
"PANDA Collaborator helps Darrin and Pam share an AI coding workspace safely.
When one person finishes and the other takes over, PANDA creates a safe handoff
record so nothing is lost. First-time setup takes about 3 minutes and is done
once. Daily use takes about 30 seconds."

**Table of contents** (clean 3-column grid, no heavy borders):

| Part | Title | When to use |
|---|---|---|
| 1 | First-Time Setup | Once only — registers Darrin and Pam |
| 2 | Daily Use | Every session — 30 seconds |
| 3 | Creating a Handoff | When you finish working |
| 4 | Troubleshooting | If something goes wrong |

### 3.2 Pages 1–2 — Part 1: First-Time Setup

Section rule: 3pt amber line above "Part 1 — First-Time Setup" heading.

**Step cards** — every step uses this layout:

```
┌────────┬────────────────────────────────────────────────────┐
│  [N]   │  Step title (12pt bold)                             │
│ colour │  Detail body text (10pt, light background)          │
└────────┴────────────────────────────────────────────────────┘
```

Left column (40pt wide): step number in 15pt white Helvetica-Bold, coloured background.
Right column: step title in 12pt Helvetica-Bold, body in 10pt Helvetica, `#f9fafb` background.
Outer border: 1pt `#e5e7eb`. Corner rounding: 5pt (via Table wrapping).

Step number background colours:
- Step 1 (launch): dark `#1a1a2e`
- Steps 2–3 (Darrin registration + confirmation): amber `#d97706`
- Step 4 (Pam registration): cyan `#0891b2`
- Any completion/success sub-element: green `#16a34a`

---

**STEP 1 · Open PANDA Collaborator** [dark background]

"Double-click the PANDA Collaborator icon on your Desktop. Your browser opens
automatically within a few seconds."

URL block (monospaced, dark panel, rounded corners):
```
http://127.0.0.1:8788/
```

Info box (blue tint): "The app runs entirely on your computer — nothing is sent
to the internet."

---

**STEP 2 · Register Darrin (User 1)** [amber background]

"The registration form opens automatically on first launch. Fill in Darrin's
details below. Most fields are pre-filled — you only need to type the name."

**Registration form illustration for Darrin.**

CC must produce this as a Pillow-drawn image (not a ReportLab Table), so that
callout arrows can be drawn on top of it, then embed the result as an image.

The illustration must show a realistic form panel in the app's dark style:
- Dark title bar (`#14141f`): "PANDA Collaborator" left, "Setup — Register Users" right
- Section header: "Register Darrin" in `#e8a87c` (amber), 13pt bold
- Field rows (alternating `#1a1a2e` / `#22223a` backgrounds):

  | Label | Value | Style |
  |---|---|---|
  | Name | [empty cursor field] | Empty — user types here |
  | Repo path | C:\CODEX PG | Pre-filled, dimmer text |
  | Handoff agent | Codex | Pre-filled |
  | Handoff title | Darrin handoff | Pre-filled |
  | Codex account | Codex (Darrin) | Pre-filled |
  | Claude account | Claude (Darrin) | Pre-filled |
  | Claude Desktop | C:\Users\drrap\...\claude.exe | Pre-filled, truncated |
  | Claude Code | C:\Users\drrap\...\claude.CMD | Pre-filled, truncated |
  | Git name | Codex Backup | Pre-filled |
  | Git email | codex-backup@local | Pre-filled |

- Register button: amber `#d97706` background, white text, "Register User 1 and continue →"

Apply callout arrows as specified in §2.5 before embedding.

**Warning box** (amber tint): "If the Register button is grey, scroll down —
a required field may be below the visible area. The footer shows which fields
are missing."

---

**STEP 3 · See the Confirmation** [green background]

"PANDA shows a confirmation screen with Darrin's saved details. Check that
everything looks right, then click Continue to User 2."

**Confirmation screen illustration** (Pillow-drawn, dark panel):
- Green checkmark + "User 1 registered: Darrin" in green `#7fb069`
- Three info rows: Name · Darrin, Repo · C:\CODEX PG, Git · Codex Backup
- Amber "Continue to User 2 →" button

---

**STEP 4 · Register Pam (User 2)** [cyan background]

"The same form appears for Pam. Fill in Pam's details."

**Registration form illustration for Pam** (same layout as Darrin's, cyan header):

  | Label | Value |
  |---|---|
  | Name | [empty cursor field] |
  | Repo path | C:\CODEX PG |
  | Handoff agent | Claude |
  | Handoff title | CD handoff |
  | Codex account | Codex (Pam) |
  | Claude account | Claude (Pam) |
  | Claude Desktop | C:\Users\drrap\...\claude.exe |
  | Claude Code | C:\Users\drrap\...\claude.CMD |
  | Git name | Pam Rapoport |
  | Git email | darrinpam@comcast.net |

- Register button: cyan `#5fa0a8` background, white text, "Register User 2 and open Hub →"

**Success box** (green tint): "Once both users are registered, the Hub opens
automatically. You won't need to register again."

### 3.3 Page 3 — Part 2: Daily Use

Section rule: 3pt cyan line above heading.

Intro: "Every time you open PANDA Collaborator, follow these steps. The whole
thing takes about 30 seconds."

**Steps 1–5:**

1 [dark] · **Open PANDA Collaborator**
"Double-click the desktop icon. Your browser opens the Hub."

2 [amber] · **Click the right Handover button**
"Press GO / Switch to Darrin if Darrin is working, or GO / Switch to Pam if Pam
is. PANDA switches the colour theme and loads that person's settings."

3 [dark] · **Confirm the name at the top of the screen**
"The large name at the top shows who is active. Amber = Darrin. Cyan = Pam.
Always check this before starting work."

4 [green] · **Click Start Session / Start Work**
"PANDA scans the project and shows a plain-English summary of what happened last
time — concerns, achievements, and what to do next. Read it before starting."

5 [dark] · **Do your work, then return to PANDA when done**
"Work in Claude, Codex, or any other tool. Come back to PANDA when you finish."

**Hub screenshot (S2 — Darrin active, annotated)**

Embed the annotated screenshot from §2.5 here at 90% page width.
Caption (8pt, grey, centred): "The Collaborator Hub with Darrin active (amber theme).
Pam's button is always visible on the left — one click switches the active user."

### 3.4 Page 4 — Part 3: Creating a Handoff

Section rule: 3pt green line above heading.

Intro: "When you finish working, create a handoff so the next person has full
context."

**Steps 1–4:**

1 [dark] · **Click End Session / Handoff**
"Find this button in the Collaborator Hub. Click it."

2 [dark] · **Enter a short title** (optional)
"Describe what you did — for example: 'Tracker filter fix, combo UX done'.
Leave blank to use the default."

3 [dark] · **Add notes** (optional)
"Briefly note what you finished, any open issues, and what to do next."

4 [green] · **Click Create safe handoff**
"PANDA saves a protection branch, patch files for unsaved changes, file copies,
and a plain-English HANDOFF summary."

**Handoff form screenshot:**
Prefer the fresh S4 screenshot (`shot_handoff_form.png`) if live capture succeeded.
If Playwright was unavailable, use crop C-HANDOFF from the smoke file (§2.4).
Either way, crop to show just the CREATE HANDOFF form area before annotating.

Add two callout arrows:
- "Describe your work here" → TITLE field
- "Click to save the handoff" → Create safe handoff button

Caption: "The Create Handoff form. Fill in the title and any notes, then click
the button. PANDA handles the rest."

**Safety box** (green tint): "PANDA never deletes files, force-pushes, or
discards unsaved work. It is always safe to click Create safe handoff."

### 3.5 Page 5 — Part 4: Troubleshooting

Section rule: 3pt red `#e74c3c` line above heading.

Six issue cards. Each card has:
- Left column (35pt): short text label in coloured background (no emoji):
  [!] red · [?] blue · [>] grey · [o] grey · [P] blue · [W] amber
- Right column: bold title + 10pt detail body, light background

| Left label | Title | Detail |
|---|---|---|
| [!] red | Something looks wrong — click Emergency Pause | Click the red Emergency Pause button. This stops all work and flags the issue. Nothing is deleted. |
| [?] blue | The browser didn't open | Double-click the desktop icon again. If it still won't open, type http://127.0.0.1:8788/ into your browser. |
| [>] grey | The app says it is already running | That's fine. Open your browser and go to http://127.0.0.1:8788/ |
| [o] grey | A button is grey and won't click | A required field is missing. For registration buttons, scroll down inside the form — some fields may be below the visible area. The footer names missing fields. |
| [P] blue | Reading an old handoff | Click Packages in the left panel, pick a package, then click Inspect package. Read-only — no files are changed. |
| [W] amber | Never enter passwords into PANDA | PANDA stores names and email addresses only. Never type passwords, API keys, or tokens. |

### 3.6 Page 6 — Quick Reference

"Quick Reference" heading, no rule (this is a utility page).

Full-width 3-column table:

| Task | What to do | Where |
|---|---|---|
| Open the app | Double-click PANDA Collaborator on the Desktop | Desktop |
| App won't open | Go to http://127.0.0.1:8788/ in your browser | Browser |
| Switch to Darrin | Click GO / Switch to Darrin, then check name at top | Hub |
| Switch to Pam | Click GO / Switch to Pam, then check name at top | Hub |
| Start working | Click Start Session / Start Work | Hub |
| Finish working | Click End Session / Handoff, then Create safe handoff | Hub |
| Something is wrong | Click Emergency Pause (red button) | Hub |
| Read old handoffs | Click Packages, pick one, click Inspect package | Hub left panel |
| App already running | Open browser, go to http://127.0.0.1:8788/ | Browser |

Table style:
- Header row: `#14141f` background, white text, 10pt Helvetica-Bold
- Alternating rows: white / `#f9fafb`
- 1pt `#e5e7eb` grid lines
- 9pt body text

Footer (centred, 7pt, grey): "PANDA Collaborator · Setup & Daily Use Guide · Darrin and Pam · May 2026"

---

## 4. Design System

All colours used in illustrated UI elements must come from the real CSS tokens.
Read `web\index.html` for the full list. Key tokens:

| Name | Hex | Use in PDF |
|---|---|---|
| `--bg` | `#14141f` | Dark panel backgrounds, cover band |
| `--surface` | `#1a1a2e` | Card surfaces in illustrations |
| `--surface-2` | `#22223a` | Alternating field rows |
| `--line` | `#2a2a3e` | Borders in illustrations |
| `--text` | `#e0ddd5` | Text on dark backgrounds |
| `--muted` | `#888888` | Secondary/label text |
| `--accent` | `#e8a87c` | Darrin / User 1 amber |
| `--accent-2` | `#5fa0a8` | Pam / User 2 cyan |
| `--ok` | `#7fb069` | Success / green buttons |
| `--bad` | `#e74c3c` | Emergency / red |

PDF page background: white `#ffffff`
PDF body text: `#111827`
PDF Helvetica replaces Segoe UI; Courier replaces Cascadia Mono.

**Font rule:** Do not use emoji characters anywhere. ReportLab's built-in
Helvetica and Courier fonts do not support emoji glyphs and will render them as
solid black boxes. Use drawn shapes (filled circles, rectangles) or plain ASCII
text symbols instead.

---

## 5. Technical Requirements

### 5.1 Libraries

```python
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image as RLImage, HRFlowable, KeepTogether, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from PIL import Image, ImageDraw, ImageFont
import os, json, subprocess, time
```

### 5.2 Image pipeline

All screenshots and illustrations go through this pipeline before embedding:
1. Capture or draw at 1x pixel resolution
2. Annotate with callouts using Pillow (§2.5)
3. Save as PNG to a temp directory
4. Embed via `RLImage(path, max_width, max_height)` — never exceed page margins
5. Wrap in a Table with `BOX` border to create the framed screenshot look

### 5.3 Page layout

- Page: US Letter (612 × 792pt)
- Margins: 0.75in all sides (54pt)
- Usable width: 504pt (7 inches)
- Usable height: 684pt

### 5.4 Callout font

`ImageFont.load_default()` is acceptable if TrueType fonts are unavailable.
If available, use `ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 18)` for
cleaner label text. Check for existence before using TrueType.

---

## 6. Output and Delivery

### 6.1 Output files

1. Primary: `C:\CODEX PG\CODEX PANDA Collaborator\PANDA_Collaborator_Setup_Guide.pdf`
2. Temp images: save working PNGs to `C:\CODEX PG\CODEX PANDA Collaborator\tmp_pdf_build\`.
   Create this folder if it does not exist. It can be deleted after the PDF is built.

### 6.2 No git commit

Do not commit the PDF to any repository. It is a binary deliverable file only.
Do not run `git add` on it.

### 6.3 RTC requirements

File an RTC to `C:\panda-gallery\workflows\cc_mailbox\CLAUDE Inbox\` containing:

1. Confirmation that all 5 source files in §1 were read before writing code.
2. Screenshot status: which of S1–S4 were live-captured vs illustrated; if
   Playwright failed, explain why.
3. Per-part checklist (Parts 1–4 + Quick Reference): ✓ complete / ✗ not done.
4. Page count of the generated PDF.
5. Confirmation that no emoji characters appear anywhere in the PDF.
6. Any deviations from this spec and the reason.

Hold for `go pc-manual done`. No commit needed — just file delivery.

---

## 7. Acceptance Criteria

1. PDF opens cleanly in Edge and prints without errors.
2. Every field value for Darrin and Pam exactly matches the settings JSON.
3. No tofu boxes (missing glyphs) anywhere in the PDF.
4. At least one live or annotated screenshot of the real app is embedded.
5. Callout arrows are visible and point to the correct UI elements.
6. Every numbered step uses the step-card layout from §3.2.
7. User colour identity (amber = Darrin, cyan = Pam) is consistent on every page.
8. Quick Reference table is complete with all 9 rows.
9. PDF file size is under 15 MB.
10. Output file exists at the path in §6.1.
