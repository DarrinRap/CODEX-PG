# CODEX Specification Review Heading Digest

Generated: 2026-04-24 19:08:44 -07:00

This digest extracts headings and key review markers from canonical specification documents. Duplicate `workflows\project_knowledge_sync_2026-04-23` snapshots are excluded from review scope.

## ARCHITECTURE.md

Bytes: 32183

1: # Panda Gallery Architecture
8: ## 1. Edit-State Data Model
58: ## 2. Rendering Pipeline
98: ## 3. Undo Model
144: ## 4. Storage Format
183: ## 5. Panel / Dock Architecture
195: **Dock setup completeness.** Two of three docks have `DockWidgetFloatable` enabled. `tool_dock` is intentionally locked via `NoDockWidgetFeatures` (`panda_gallery.py:281`). Both floatable docks also have `setAllowedAreas(RightDockWidgetArea | LeftDockWidgetArea)` `[CODE panda_gallery.py:299-301, panda_gallery.py:480-482]`.
225: ## 6. Signal-to-Render Latency
266: ## 7. MVP-2 Readiness Assessment
268: ### 7.1 DICOM Pipeline
272: ### 7.2 Installer
276: ### 7.3 HIPAA Posture
283: ### 7.4 Data Migration
287: ### 7.5 Scale
296: ## 8. Known Unknowns

## GUIDED_TESTING_STYLE.md

Bytes: 17672

1: # GUIDED_TESTING_STYLE.md
23: ## Core principle
41: ## Testability matrix — what the pane CAN and CANNOT cover
48: ### CAN be tested in-pane
78: ### CANNOT be tested in-pane (today)
84: this. Until then, QSettings-gated behavior is deferred to
110: ### If a test falls in the CAN'T column
120: field. "QSettings fallback path deferred to Settings-dialog
126: ## Hard rules
190: ## Anti-patterns: bad step → good step
197: ### Registry editing
216: ### Helper-script shell-out
232: ### Vague timing
253: ### Paraphrased transient text
267: ### Branchy setup
284: ### Mega-step
304: ### Internal state check
318: ### Pre-filled PASS/FAIL prose (post-#87 regression)
344: ## Workflow for Claude writing a pane plan
374: 9. **Note any deferred coverage in the plan's `context` field,**
380: ## History

## HANDOFF_FORMAT_SPEC.md

Bytes: 10746

1: # HANDOFF format spec
3: ## Problem
7: BUGS.md. Signal-bearing parts (deferred items, next candidates, rare
13: ## Design principles
23: 4. **Three content sections only.** Deferred, Next candidates, Lessons.
31: ## File: `C:\panda-gallery\HANDOFF.md`
35: ### Schema
43: ## Deferred
62: ### Size caps
66: | Deferred | 1 line per item, no item count cap (flag if >10) |
74: ### Section rules
78: - Deferred = carried from prior + new. Claude shows prior list verbatim
84: ### What is NOT in HANDOFF.md
98: ## Defense layers
108: ### Claude self-check (pre-write)
117: 5. Every deferred item traceable to prior handoff OR Darrin-named new
125: ### `pgc` validator (pre-commit)
138: `## Deferred`, `## Next candidates`, `## Lessons`.
154: ## Workflow: Session close (Claude-side)
158: session number, deferred items, next candidates.
160: - Of prior deferred items: which are done? which still open?
172: ### What Claude must never do
176: - Auto-mark deferred items done without Darrin confirmation.
180: ## Workflow: Session close (script-side -- `pgc`)
193: ## Workflow: Session open (script-side -- `pgs`)
204: ## Workflow: Session open (Claude-side, pg-session-manager skill)
213: ## Rollback
225: ## Migration (two commits)
227: ### Commit A (this commit) -- spec + seed
234: - NEW: `HANDOFF.md` at repo root, seeded with session = 51, deferred
247: ### Commit B (next session) -- tooling rewrite
271: ### Post-migration
278: ## Impact summary

## PANDA_GALLERY_AUTOTRANSCRIBE_SPEC.md

Bytes: 25431

1: # PANDA_GALLERY_AUTOTRANSCRIBE_SPEC.md
7: **Status:** Draft v3 — attribute names verified against HEAD `fea184c` via Step 0 (v1 had two wrong names, now corrected). Ready for implementation.
13: ## 1. Purpose
19: Goal: one-session ship. Manual test plan runs end-to-end before commit.
23: ## 2. Non-goals (explicit)
25: Out of scope for v3.46:
40: ## 3. Design decisions (resolved in draft)
42: ### 3.1 Always-on vs. opt-in
48: ### 3.2 Subprocess shape
78: ### 3.3 Poll-for-completion strategy
96: ### 3.4 Single in-flight subprocess per manager
102: - Serializing would require a queue and "transcription N of M" UI. Out of scope.
107: ### 3.5 App-close behavior
117: ### 3.6 Error handling
131: ## 4. User-facing behavior
133: ### 4.1 Start-session dialog
137: ### 4.2 During session
141: ### 4.3 Stop session (Ctrl+Alt+S) — new behavior
147: 2. Existing v3.43 status: `"Saved N frames + audio.wav (T seconds)"` — **unchanged**, flashed immediately when save completes.
161: ### 4.4 Abort (Ctrl+Alt+A)
165: ### 4.5 Delete last (Ctrl+Alt+Backspace)
175: ## 5. Implementation outline
189: ### 5.1 New module-level constants
196: ### 5.2 `WorkflowCaptureManager.__init__` additions
207: ### 5.3 `stop_session` — tail addition
219: ### 5.4 New method `_maybe_start_transcribe`
283: ### 5.5 New method `_poll_transcribe_proc`
325: ### 5.6 `shutdown()` — no changes
331: ### 5.7 Imports
337: ## 6. Filesystem layout
355: ## 7. Step 0 verification
372: ## 8. Edge cases & failure modes
396: ## 9. Testing plan (sequential, all PASS before commit)
437: ## 10. Commit plan
460: ## 11. Follow-ups (not v3.46)

## PANDA_GALLERY_COMPLIANCE_SPEC.md

Bytes: 23495

1: # PANDA_GALLERY_COMPLIANCE_SPEC.md
7: **Status:** Draft — awaiting review. Not legal advice. Before any commercial deployment or engagement with a second practice, this document must be reviewed by a healthcare-technology attorney. Claude authored the draft based on publicly documented HIPAA requirements; the current-state assessment is based on what Claude can observe in the repo at commit `5ee73eb` (v3.45).
15: ## 1. Context
25: The goal of this document is to track where PG stands against each HIPAA requirement, what gaps exist, and what the priority is for closing them before each inflection point.
29: ## 2. PHI in Panda Gallery — what data is actually at risk
49: ## 3. HIPAA Security Rule — Technical Safeguards (45 CFR 164.312)
51: ### 3.1 Access Control (§ 164.312(a))
55: **Current status:** ⚠️ Partial / Unverified
57: - Unique user IDs: unknown from code inspection. If PG has a login screen, it is not visible in the CLAUDE.md entry-point description. Solo-operator use means "user identification" is currently "whoever unlocked the Windows session."
68: ### 3.2 Audit Controls (§ 164.312(b))
72: **Current status:** ❌ Not Started
86: ### 3.3 Integrity (§ 164.312(c))
90: **Current status:** ⚠️ Partial
102: - Consider signed integrity checks for exported files (out of MVP scope).
104: ### 3.4 Transmission Security (§ 164.312(e))
108: **Current status:** ✅ N/A (no transmission today)
123: ## 4. HIPAA Security Rule — Administrative Safeguards (45 CFR 164.308)
125: ### 4.1 Security Management Process (§ 164.308(a)(1))
129: **Current status:** ❌ Not Started
141: ### 4.2 Workforce Security (§ 164.308(a)(3))
145: **Current status:** ❌ Not Started (N/A single-operator)
153: ### 4.3 Information Access Management (§ 164.308(a)(4))
157: **Current status:** ❌ Not Started (currently: all users see all data)
164: ### 4.4 Security Awareness and Training (§ 164.308(a)(5))
168: **Current status:** N/A (single-operator; developer is trained)
172: ### 4.5 Security Incident Procedures (§ 164.308(a)(6))
176: **Current status:** ❌ Not Started
185: ### 4.6 Contingency Plan (§ 164.308(a)(7))
189: **Current status:** ⚠️ Partial
201: ### 4.7 Evaluation (§ 164.308(a)(8))
205: **Current status:** ❌ Not Started
209: ### 4.8 Business Associate Contracts (§ 164.308(b))
213: **Current status:** ❌ Not Started. No BAA template exists.
224: ## 5. HIPAA Security Rule — Physical Safeguards (45 CFR 164.310)
226: ### 5.1 Facility Access Controls (§ 164.310(a))
230: **Current status:** Covered entity's responsibility, not PG's. Dental practice controls physical access to workstations.
234: ### 5.2 Workstation Use (§ 164.310(b))
238: **Current status:** Covered entity's responsibility.
242: ### 5.3 Workstation Security (§ 164.310(c))
246: **Current status:** Covered entity's responsibility.
248: ### 5.4 Device and Media Controls (§ 164.310(d))
252: **Current status:** ❌ Not Started (for PG's exports / backups)
262: ## 6. HIPAA Privacy Rule — Selected Elements Relevant to PG
266: ### 6.1 Minimum Necessary (§ 164.502(b))
270: **Current status:** ❌ Not Started (currently: all users see all data)
274: ### 6.2 Patient Rights — Access, Amendment, Accounting of Disclosures (§ 164.524, §164.526, §164.528)
278: **Current status:** ⚠️ Partial
286: ### 6.3 De-Identification (§ 164.514(b))
290: **Current status:** ❌ Not Started, no feature
294: ### 6.4 Notice of Privacy Practices
298: **Current status:** Covered entity's responsibility. Document in deployment guide.
302: ## 7. Operational Safeguards (not codified in the regulation but real-world necessary)
304: ### 7.1 Data Retention and Destruction
308: **Current status:** ❌ Not Started
321: ### 7.2 Logging That Could Contain PHI
323: **Current status:** ⚠️ Unverified
336: ### 7.3 Third-Party Processor Risk
340: **Current status:** ✅ Clean today (Whisper runs locally, no PHI leaves the machine)
351: ## 8. Summary — Gap Prioritization by Inflection Point
353: ### Before next major internal milestone (no external deployment):
358: ### Before second-practice deployment (the HARD line):
369: ### Before commercial release:
378: ### Triggered by future features:
385: ## 9. Not in Scope (intentionally deferred)
395: ## 10. Living-document protocol
415: ## 11. Next Actions (for Darrin's queue)
417: The list below is the concrete to-do to get this document out of draft status:

## PANDA_GALLERY_FREEFORM_SPEC.txt

Bytes: 40374

1: # ══════════════════════════════════════════════════════════════════════════════
2: #  PANDA GALLERY — FREEFORM CANVAS SPECIFICATION
3: #  Drag-and-drop image arrangement with smart guides
4: #  Addendum to PANDA_GALLERY_v4_SPEC
5: # ══════════════════════════════════════════════════════════════════════════════
8: # ─────────────────────────────────────────────────────────────────────────────
9: #  OVERVIEW
10: # ─────────────────────────────────────────────────────────────────────────────
12: #  Freeform Canvas is an alternative to the rigid grid-based Template
13: #  Designer. Instead of designing a blank grid then filling it with
14: #  images, users drag images directly onto a canvas and arrange them
15: #  freely — like placing physical films on a lightbox.
17: #  Two modes for the same data:
18: #    GRID MODE: images locked into template slot positions (existing behavior)
19: #    FREEFORM MODE: images freely draggable with smart snap guides
21: #  Both modes read/write the same series data. A freeform arrangement
22: #  can be saved as a template. A template can be opened in freeform
23: #  mode for adjustment. They're two views, not separate features.
25: #  DESIGN PHILOSOPHY:
26: #    Think PowerPoint/Figma slide editor, not Photoshop.
27: #    Drag, drop, snap, align. Zero learning curve.
28: #    Smart enough to prevent mistakes (no overlap, minimum spacing)
29: #    but flexible enough for any clinical layout.
31: #  USE CASES:
32: #    - Periodontist clusters images by quadrant with spacing
33: #    - Before/after pairs placed side by side
34: #    - Mixed sensor sizes arranged anatomically
35: #    - Custom presentations for patient education
36: #    - Quick one-off arrangements without designing a template first
39: # ─────────────────────────────────────────────────────────────────────────────
40: #  CANVAS LAYOUT
41: # ─────────────────────────────────────────────────────────────────────────────
43: #  ┌──────────────────────────────────────────────────────────────────────┐
44: #  │  CANVAS TOOLBAR                                                     │
45: #  │  [Grid] [Freeform] | [Auto-Arrange] [Save Layout] [Clear All]      │
46: #  ├──────────────────────────────────────────────────────────────────────┤
47: #  │                                                                      │
48: #  │                    CANVAS (black background)                         │
49: #  │                                                                      │
50: #  │    ┌──────┐            ┌──────┐                                     │
51: #  │    │ img1 │            │ img2 │     ← freely placed images          │
52: #  │    │      │   ┌──────┐ │      │                                     │
53: #  │    └──────┘   │ img3 │ └──────┘     ← smart guides appear           │
54: #  │               │      │              between images during drag      │
55: #  │               └──────┘                                              │
56: #  │                                                                      │
57: #  │         ┌──────┐ ┌──────┐                                           │
58: #  │         │ img4 │ │ img5 │                                           │
59: #  │         └──────┘ └──────┘                                           │
60: #  │                                                                      │
61: #  ├──────────────────────────────────────────────────────────────────────┤
62: #  │  FILMSTRIP (resizable, patient images)                              │
63: #  │  [IMAGES] [+ Mount]  [img] [img] [img] [img] [img] ◄ scroll ►     │
64: #  └──────────────────────────────────────────────────────────────────────┘
67: # ─────────────────────────────────────────────────────────────────────────────
68: #  CANVAS TOOLBAR
69: # ─────────────────────────────────────────────────────────────────────────────
71: #  Left side — mode toggle:
72: #    [Grid] [Freeform] — toggle between template grid and freeform
73: #    Active mode highlighted with accent color.
74: #    Switching modes preserves images but rearranges positions:
75: #      Grid → Freeform: images unlock from grid, keep current positions
76: #      Freeform → Grid: images snap to nearest grid slot positions
77: #        (if more images than grid slots, extras go to filmstrip)
79: #  Center — actions:
80: #    [Auto-Arrange] — one click snaps all placed images into a clean
81: #      grid based on image count and aspect ratios. Like "auto-layout"
82: #      in Figma. Respects minimum spacing. Undoable.
83: #    [Save Layout] — save current arrangement as a reusable template.
84: #      Opens dialog: name, description, save. Positions stored in
85: #      layout_json with absolute (x, y) coordinates per image slot.
86: #    [Clear All] — remove all images from canvas back to filmstrip.
87: #      Confirmation dialog: "Clear all images? They return to filmstrip."
88: #      Undoable as one action.
90: #  Right side — view controls:
91: #    [Fit All] (Home key) — zoom to show all placed images
92: #    Zoom +/- controls (or use mouse wheel)
95: # ─────────────────────────────────────────────────────────────────────────────
96: #  DRAG AND DROP — FROM FILMSTRIP TO CANVAS
97: # ─────────────────────────────────────────────────────────────────────────────
99: #  FIRST IMAGE PLACEMENT:
100: #    Drag an image from the filmstrip onto the empty canvas.
101: #    Drop anywhere — the image centers at the drop position.
102: #    This first image establishes the invisible alignment grid:
103: #      - Vertical and horizontal center lines through the image
104: #      - Edge lines (top, bottom, left, right)
105: #    These become snap guides for future images.
107: #  SUBSEQUENT IMAGE PLACEMENT:
108: #    Drag from filmstrip → canvas shows smart guides as you hover:
109: #      - Dotted blue lines when the dragged image's edges or center
110: #        align with any existing image's edges or center
111: #      - Gentle magnetic snap (15px threshold) — image pulls toward
112: #        the guide when close, like PowerPoint smart guides
113: #    Drop the image — it locks at the final position.
114: #    If the drop position would cause overlap → image bounces back
115: #    to the filmstrip with a brief red flash (invalid placement).
117: #  HOLD ALT WHILE DRAGGING:
118: #    Disables all snap guides — true freeform placement.
119: #    Image can be placed at any position (still no overlap allowed).
121: #  PLACEMENT RULES:
122: #    - Images CANNOT overlap (hard rule, enforced always)
123: #    - Minimum 8px gap between any two images (configurable)
124: #    - No maximum distance — images can be spaced far apart
125: #    - Images can be placed anywhere on the infinite canvas
126: #    - Canvas auto-extends as images are placed further out
128: #  VISUAL FEEDBACK DURING DRAG:
129: #    - Ghost image follows cursor at 50% opacity
130: #    - Valid drop zone: green border glow on the ghost image
131: #    - Invalid (too close / overlap): red border glow, "×" cursor
132: #    - Distance indicator: small "8px" label appears between the
133: #      dragged image and the nearest existing image when close
134: #    - Snap guides: dotted blue lines (alignment) with small
135: #      "aligned" indicator where lines intersect
138: # ─────────────────────────────────────────────────────────────────────────────
139: #  SMART GUIDES (PowerPoint/Figma style)
140: # ─────────────────────────────────────────────────────────────────────────────
142: #  Smart guides appear automatically when dragging or moving images.
143: #  They show alignment relationships between images.
145: #  EDGE ALIGNMENT:
146: #    Left edge of dragged image aligns with left edge of any other image

## PANDA_GALLERY_IMAGE_INFO_SPEC.txt

Bytes: 19555

1: # ══════════════════════════════════════════════════════════════════════════════
2: #  PANDA GALLERY — IMAGE INFO PANEL SPECIFICATION
3: #  Editable image metadata fields + custom fields
4: #  Addendum to PANDA_GALLERY_v3_SPEC
5: # ══════════════════════════════════════════════════════════════════════════════
8: # ─────────────────────────────────────────────────────────────────────────────
9: #  OVERVIEW
10: # ─────────────────────────────────────────────────────────────────────────────
12: #  The Info tab in the right panel displays image metadata. Currently
13: #  all fields are read-only. This spec adds:
14: #    1. Editable fields — click to edit, auto-save on blur
15: #    2. Custom fields — user-defined key/value pairs per image
16: #    3. Notes field — multi-line free-text annotation
18: #  DESIGN PRINCIPLE: Same in-place editing pattern used in the
19: #  patient detail card. Click a value → it becomes editable →
20: #  press Enter or click away to save. No "Edit" button needed.
23: # ─────────────────────────────────────────────────────────────────────────────
24: #  CURRENT FIELDS (with editability)
25: # ─────────────────────────────────────────────────────────────────────────────
27: #  ┌──────────────────────────────────────────────────────────────────┐
28: #  │  Field             │ Editable │ Control          │ Notes         │
29: #  ├──────────────────────────────────────────────────────────────────┤
30: #  │  Name              │ YES      │ Inline text      │ Display name  │
31: #  │  Date              │ YES      │ Date picker      │ Captured date │
32: #  │  Size (px)         │ NO       │ Read-only label  │ From file     │
33: #  │  File (KB/MB)      │ NO       │ Read-only label  │ From file     │
34: #  │  Type              │ YES      │ Dropdown         │ Photo/Radio   │
35: #  │  Category          │ YES      │ Dropdown         │ See below     │
36: #  └──────────────────────────────────────────────────────────────────┘
38: #  READ-ONLY fields: Size (pixels) and File (size in KB/MB) are
39: #  derived from the actual image file and cannot be changed by the
40: #  user. They are displayed as plain text with --fg-dim (#888) color.
42: #  EDITABLE fields: shown with a subtle underline or faint pencil
43: #  icon on hover to indicate they are clickable/editable.
46: # ─────────────────────────────────────────────────────────────────────────────
47: #  FIELD DETAILS
48: # ─────────────────────────────────────────────────────────────────────────────
50: #  NAME:
51: #    Default: original filename (without extension)
52: #    Click value → inline QLineEdit appears in place of label
53: #    Enter or focus-out → saves to database immediately
54: #    Escape → cancels edit, reverts to previous value
55: #    Max length: 255 characters
56: #    Used in: export filename, library tooltip, search
57: #    Changing the display name does NOT rename the original file
58: #    (Rule 2: never modify original files)
60: #  DATE:
61: #    Two dates tracked (per main spec Section 19):
62: #      captured_date — clinical date (user-editable, shown as "Date")
63: #      created_at — import date (read-only, shown as "Imported")
64: #    Click date value → QDateTimeEdit popup (calendar picker)
65: #    Format: MM/DD/YYYY HH:MM AM/PM (clinic-friendly)
66: #    Default: EXIF date if available, otherwise import date
67: #    Library grid sorts by captured_date
68: #    Both dates visible in Info tab:
69: #      Date: 04/13/2026 02:33 PM     (editable)
70: #      Imported: 04/13/2026 02:33 PM  (read-only, --fg-dim)
72: #  TYPE:
73: #    Dropdown: Photo | Radiograph
74: #    Default: auto-detected on import (grayscale → Radiograph)
75: #    User override allowed (auto-detect isn't always right)
76: #    Changing type affects:
77: #      - Canvas background color (black vs dark gray)
78: #      - Available adjustment tools (Invert, Window/Level vs Vibrance)
79: #      - Auto-enhance algorithm (CLAHE for radiographs)
80: #      - Library filter tab categorization
82: #  CATEGORY:
83: #    Dropdown with predefined + custom options:
84: #      Predefined: Radiograph, Photo, Document, Scan, Other
85: #      Future: admin-configurable category list
86: #    Affects library filter tab placement
87: #    Default: auto-detected from file type and grayscale detection
90: # ─────────────────────────────────────────────────────────────────────────────
91: #  NOTES FIELD
92: # ─────────────────────────────────────────────────────────────────────────────
94: #  Multi-line free-text field below the metadata fields.
95: #  Equivalent to the Notes field on the patient detail card.
97: #  ┌──────────────────────────────────────────────────────────────────┐
98: #  │  NOTES                                          [+ Add Note]    │
99: #  ├──────────────────────────────────────────────────────────────────┤
100: #  │  Watch distal of #14 — Dr. Smith, Apr 11, 2026                 │
101: #  │  Possible early caries — Dr. Smith, Oct 15, 2025               │
102: #  │                                                                 │
103: #  │  (Click to add a note)                                          │
104: #  └──────────────────────────────────────────────────────────────────┘
106: #  BEHAVIOR:
107: #    Click "+ Add Note" or the placeholder text → text area appears
108: #    Type note → press Enter or click away to save
109: #    Each note auto-stamped: "{text} — {user}, {date}"
110: #    Notes displayed most recent first
111: #    Right-click note → Edit | Delete
112: #    Delete = archive (Rule 1: never lose data)
113: #    Notes searchable via universal patient search
114: #    Quick note shortcut: N key (per main spec) adds note to
115: #    currently selected image without switching to Info tab
117: #  STORAGE:
118: #    Stored in patient_images table, notes_json column:
119: #    [
120: #      {"id": 1, "text": "Watch distal of #14",
121: #       "user": "Dr. Smith", "date": "2026-04-11T09:30:00",
122: #       "deleted": false},
123: #      ...
124: #    ]
127: # ─────────────────────────────────────────────────────────────────────────────
128: #  CUSTOM FIELDS (user-defined per image)
129: # ─────────────────────────────────────────────────────────────────────────────
131: #  Up to 10 custom key/value pairs per image. User-defined labels
132: #  for clinic-specific metadata that doesn't fit the standard fields.
134: #  ┌──────────────────────────────────────────────────────────────────┐
135: #  │  CUSTOM FIELDS                                                  │
136: #  ├──────────────────────────────────────────────────────────────────┤
137: #  │  Tooth #:        14                                             │
138: #  │  Region:         Upper Right                                    │
139: #  │  Procedure:      Root Canal                                     │
140: #  │                                                                 │
141: #  │  [+ Add Field]                                                  │
142: #  └──────────────────────────────────────────────────────────────────┘
144: #  ADDING A FIELD:
145: #    Click "+ Add Field"
146: #    Two inline text inputs appear side by side:

## PANDA_GALLERY_MCP_SESSION_INGEST_SPEC_draft2.md

Bytes: 38434

1: # PANDA GALLERY — MCP SESSION INGEST SPEC
12: **Status:** Draft 2, 2026-04-22. Draft 1 had a selection algorithm built
19: ## 0. Executive summary
35: ## 1. Problem statement
37: ### 1.1 What's broken today
50: ### 1.2 What already works (do not rebuild)
67: ### 1.3 Design constraints — the image-budget picture (honest version)
97: ## 2. Goals and non-goals
99: ### 2.1 Goals
113: corrupt metadata, locked files, image-read errors.
121: ### 2.2 Non-goals
128: 2026-04-21). Out of scope.
142: ## 3. Terminology
167: ## 4. Architecture
169: ### 4.1 Components
193: ### 4.2 Flow
220: ### 4.3 Surface differences
244: ## 5. Selection strategy
252: ### 5.1 Inputs
262: ### 5.2 Decision tree
275: ### 5.3 Transcript-guided scoring (preferred when N > cap)
347: ### 5.4 Heuristic fallback (N > cap, no transcript or unparseable)
356: ### 5.5 User override
373: ## 6. Output shape
376: ## Session: session_20260422_141530
380: ### Selection
388: ### Transcript summary
392: ### Per-frame observations
398: ### Patterns / findings
402: ### Next step
419: ## 7. Edge cases and error modes
421: ### 7.1 `LATEST.txt` missing or empty
430: ### 7.2 Transcription not yet complete
443: ### 7.3 Zero frames (session with no F12 presses)
451: ### 7.4 Screenshots-only session (no audio)
459: ### 7.5 Corrupt or version-mismatched `metadata.json`
473: ### 7.6 Transcript parse failure
483: ### 7.7 Individual frame read fails (OS error, file lock)
494: ### 7.8 Frame read exceeds token cap (Claude Code, MAX_MCP_OUTPUT_TOKENS)
508: ### 7.9 Oversized ingest on desktop Claude — pagination
522: ### 7.10 Mid-chat re-ingest
537: ## 8. Skill file — `skills/pg-mcp-ingest/SKILL.md`
539: ### 8.1 Purpose
546: ### 8.2 Trigger phrases (registered in CLAUDE.md)
578: ### 8.3 Skill-file skeleton (to be fully authored at implementation time)
581: # PG MCP Session Ingest — skill
585: ## Step 1 — Resolve session path
591: ## Step 2 — Read metadata
600: ## Step 3 — Read transcript (optional)
610: ## Step 4 — Select frames
619: ## Step 5 — Read selected frames
630: ## Step 6 — Emit response
635: ## Guardrails
654: ## 9. Changes outside the skill file
656: ### 9.1 `CLAUDE.md` edit
683: ### 9.2 Desktop-Claude memory rule
699: ### 9.3 No other edits
711: ## 10. Ship plan
713: ### 10.1 Commits
732: ### 10.2 Behavioral verification
779: ### 10.3 Rollback
791: ## 11. Follow-ups (explicitly not v1)
793: ### 11.1 Thumbnail lane (future, if cap bites in practice)
802: ### 11.2 Auto-watch
806: surprise context injection. Deferred indefinitely unless Darrin
809: ### 11.3 Cross-session analysis
814: ### 11.4 Feature-request BUGS.md entry (optional)
819: ### #NN — Feature: thumbnail lane + oversized-session handling for MCP ingest
820: **Status:** Open — deferred
835: ### 11.5 Domain-aware bug-signal phrase list
845: ## 12. Open questions (reviewer decisions before C2 ships)
880: ## 13. Summary
894: ## 14. Changes from draft 1

## PANDA_GALLERY_MULTIMONITOR_SPEC.txt

Bytes: 15073

1: # ══════════════════════════════════════════════════════════════════════════════
2: #  PANDA GALLERY — MULTI-MONITOR PRESENTATION MODE SPECIFICATION
3: #  Patient-facing display for chairside consultation
4: #  Addendum to PANDA_GALLERY_v4_SPEC
5: # ══════════════════════════════════════════════════════════════════════════════
8: # ─────────────────────────────────────────────────────────────────────────────
9: #  OVERVIEW
10: # ─────────────────────────────────────────────────────────────────────────────
12: #  Presentation Mode turns secondary monitors into patient-facing displays.
13: #  The dentist works in Panda Gallery on their primary monitor (full UI,
14: #  panels, tools) while one or more secondary monitors show a clean,
15: #  full-screen view of the current image — no UI chrome, no panels,
16: #  just the image on a black background. Like PowerPoint's presenter
17: #  view vs slideshow view.
19: #  USE CASES:
20: #    - Chairside consultation: "Let me show you what I see on this X-ray"
21: #    - Treatment presentation: walk patient through before/after images
22: #    - Series review: show full FMX on ceiling monitor while annotating
23: #    - Multi-screen operatory: monitors on both sides of chair + ceiling
25: #  DESIGN PRINCIPLE: Zero friction. F5 and you're presenting. The patient
26: #  sees exactly what the dentist is looking at, in real time. No setup,
27: #  no configuration, no extra clicks during the appointment.
30: # ─────────────────────────────────────────────────────────────────────────────
31: #  LAUNCHING PRESENTATION MODE
32: # ─────────────────────────────────────────────────────────────────────────────
34: #  KEYBOARD SHORTCUTS:
35: #    F5 — Toggle presentation on the next available secondary monitor.
36: #      First press: opens full-screen presentation on monitor 2.
37: #      Press again: closes presentation.
38: #      If only one monitor connected: shows notification
39: #      "No secondary monitor detected."
41: #    Shift+F5 — Opens monitor picker dialog (for 3+ monitors):
42: #      ┌─────────────────────────────────────────────┐
43: #      │  Present on External Monitors           ✕   │
44: #      ├─────────────────────────────────────────────┤
45: #      │                                             │
46: #      │  ☐ Monitor 2 — "ASUS VG27AQ" (2560×1440)  │
47: #      │  ☐ Monitor 3 — "LG 27UK850" (3840×2160)   │
48: #      │  ☐ Monitor 4 — "Samsung T55" (1920×1080)  │
49: #      │                                             │
50: #      │              [Cancel]  [Present]             │
51: #      └─────────────────────────────────────────────┘
52: #      Check one or more monitors. Click Present.
53: #      Monitor names and resolutions auto-detected from OS.
55: #  MENU BAR:
56: #    View → "Present on External Monitor" (same as F5 for single
57: #    secondary, same as Shift+F5 picker for multiple).
58: #    Discoverable entry point for first-time users.
60: #  STATUS BAR INDICATOR:
61: #    When presenting: "📺 2" or "📺 2, 3" appears in status bar.
62: #    Click the indicator → closes presentation on that monitor.
63: #    No indicator shown when not presenting.
65: #  CLOSING PRESENTATION:
66: #    F5 again — closes all presentation windows.
67: #    Click status bar indicator — closes specific monitor.
68: #    Escape on main monitor does NOT close presentation
69: #    (Escape is already "go back one level" in the app).
72: # ─────────────────────────────────────────────────────────────────────────────
73: #  PRESENTATION WINDOW — WHAT THE PATIENT SEES
74: # ─────────────────────────────────────────────────────────────────────────────
76: #  LAYOUT:
77: #    Full-screen borderless window on the target monitor.
78: #    Pure black background (#000000).
79: #    Image centered and fitted to fill maximum area while
80: #    maintaining aspect ratio (letterboxed if needed).
81: #    No title bar, no menu, no panels, no toolbar, no status bar.
82: #    No mouse cursor visible (hidden on the patient screen).
83: #    Just the image on black — clean clinical presentation.
85: #  WHAT IS SHOWN:
86: #    - Single image: full-screen, fitted
87: #    - Series/template: full composite layout on black
88: #    - Comparison mode: same side-by-side layout as main screen
89: #    - Annotations: visible in real-time as they are drawn
90: #    - Adjustments: visible in real-time as sliders move
91: #    - When zoomed into a template slot: patient screen zooms too
93: #  WHAT IS NOT SHOWN:
94: #    - Any UI elements (panels, toolbars, menus, filmstrip)
95: #    - Mouse cursor on the patient screen
96: #    - Toast notifications
97: #    - Dialogs or popups
98: #    - The library grid (only images/series/comparisons)
100: #  WHEN NO IMAGE IS OPEN:
101: #    Patient screen shows black with a subtle centered clinic logo
102: #    (from Practice Info settings). If no logo configured, just black.
103: #    This avoids the patient seeing a blank app or UI elements
104: #    between images.
107: # ─────────────────────────────────────────────────────────────────────────────
108: #  SYNC BEHAVIOR — MAIN SCREEN ↔ PATIENT SCREEN
109: # ─────────────────────────────────────────────────────────────────────────────
111: #  DEFAULT: SYNCED
112: #    Whatever the dentist sees on the main canvas, the patient sees
113: #    on their screen. Real-time, no delay perceptible to the user.
115: #    Synced actions:
116: #      - Select/open an image → patient screen shows it
117: #      - Draw an annotation → appears on patient screen immediately
118: #      - Adjust brightness/contrast → patient sees the change live
119: #      - Zoom in/out → patient screen zooms in sync
120: #      - Pan → patient screen pans in sync
121: #      - Open a series → patient sees the composite
122: #      - Double-click a template slot → patient zooms into that slot
123: #      - Escape back to template grid → patient sees full grid
124: #      - Switch to comparison mode → patient sees side-by-side
125: #      - Before/After toggle (\) → patient sees the toggle
127: #    NOT synced (main screen only):
128: #      - Panel interactions (tab switching, slider hovering)
129: #      - Filmstrip scrolling/selection (until image is opened)
130: #      - Patient list browsing
131: #      - Dialog boxes (export, template picker, etc.)
132: #      - Menu interactions
133: #      - Right-click context menus
135: #  PIN MODE (freeze patient screen):
136: #    Keyboard shortcut: P (toggle)
137: #    Status bar shows: "📺 2 📌" when pinned.
139: #    When pinned:
140: #      - Patient screen freezes on the current image
141: #      - Dentist can freely navigate, browse filmstrip, open other
142: #        images, make adjustments — patient screen doesn't change
143: #      - Useful for: finding the next image to show, making
144: #        preliminary adjustments before revealing to patient,
145: #        checking other patient data without the patient seeing

## PANDA_GALLERY_REMOTE_TESTING_SPEC_draft4.md

Bytes: 86859

1: # PANDA GALLERY — REMOTE TESTING PLATFORM
2: # Full module spec, draft 4 — April 20, 2026
3: # Status: FOR DARRIN REVIEW
4: # Supersedes: draft 3 (adversarial review found 3 new blockers, 3 new
5: #             high-severity issues that draft 3 missed; draft 4 corrects
6: #             them all)
7: # Source: 40 design decisions locked in chat session 2026-04-20
8: # Target PG version: v3.50 (Phase 1) through v3.54 (Phase 5)
9: # Current HEAD: v3.49 (workflow_capture v6 + auto-transcribe shipped)
13: ## 0. ABOUT THIS DOCUMENT
16: Every locked decision from the chat session appears here, assigned to
57: so Phase 4 deferred-upload only fires when transcript.md exists.
75: ## 1. PURPOSE & VISION
77: ### 1.1 The problem today
95: ### 1.2 The vision
106: ### 1.3 Explicit terminology
123: ## 2. THE 40 LOCKED DECISIONS — INDEX
177: ## 3. SHARED ARCHITECTURE (applies across phases)
179: ### 3.1 New modules introduced by this spec
189: ### 3.2 Module ownership rules (STYLE.md §3)
205: ### 3.3 State ownership (STYLE.md §4)
223: ### 3.4 QSettings keys
237: ### 3.5 Screen-capture exclusion (core technical trick)
252: ### 3.6 Cross-cutting style rules applied
278: ### 3.7 Dependencies to add
291: # ═══════════════════════════════════════════════════════════════════
292: #  PHASE 1 — FLOATING HELP WINDOW (CORE)
293: # ═══════════════════════════════════════════════════════════════════
297: Locked decisions in this phase: 1, 2, 3, 4, 5, 6, 11, 21, 23, 39.
299: Goal: ship a pane that opens, reads instructions from disk, shows them
302: ## 4. PHASE 1 DETAIL
304: ### 4.1 Architecture decision: built-in module (locked #1, #39)
314: ### 4.2 Window behavior (locked #21)
365: ### 4.3 Instruction file schema (locked #2)
416: ### 4.4 Pane UI (locked #4, #11)
438: Button behavior (locked #4):
465: ### 4.5 Flow (locked #3, #5, #6)
477: Summary screen (locked #6) — Phase 1 minimum:
498: ### 4.6 Keyboard shortcut (locked #23)
527: ### 4.7 Life cycle
543: ### 4.8 New module skeleton
574: ### 4.9 Step 0 for Claude Code (Phase 1)
618: ### 4.10 Manual test plan (Phase 1)
657: ### 4.11 Phase 1 deliverables
671: # ═══════════════════════════════════════════════════════════════════
672: #  PHASE 2 — SESSION WORKFLOW & PANE POLISH
673: # ═══════════════════════════════════════════════════════════════════
677: Locked decisions: 17, 18, 19, 20, 22, 24, 26, 37.
679: Goal: make the pane useful during a real workflow-capture session. Add
683: ## 5. PHASE 2 DETAIL
685: ### 5.1 Scope summary
691: ### 5.2 Geometry persistence (locked #22)
703: ### 5.3 Cancel Session with cleanup (locked #17, #18)
736: ### 5.4 Pause / Resume (locked #19)
760: ### 5.5 Settings panel in PG menu (locked #20)
799: (Earlier draft included an opacity slider here; that was not a locked
802: ### 5.6 Live capture stats (locked #24)
828: ### 5.7 Help / About section (locked #26)
855: ### 5.8 Shortcuts in main menu items (locked #37)
875: ### 5.9 Step 0 for Claude Code (Phase 2)
919: ### 5.10 Manual test plan (Phase 2)
955: ### 5.11 Phase 2 deliverables
971: # ═══════════════════════════════════════════════════════════════════
972: #  PHASE 3 — SMART MICROPHONE HANDLING
973: # ═══════════════════════════════════════════════════════════════════
978: Locked decisions: 27, 28, 29, 30, 31, 32, 33, 34, 35, 36.
980: Goal: replace today's hard-coded "Headset Microphone (Arctis 7 Chat)"
984: ## 6. PHASE 3 DETAIL
986: ### 6.1 Scope summary (locked #28, #35)
990: (locked #35; workflow_capture v6 already handles this).
992: ### 6.2 Auto-detect on first launch (locked #27)
1012: ### 6.3 Settings: device dropdown + Test Microphone (locked #29, #34, #36)
1052: Dropdown entries display **name + sample rate + channel count** (locked
1067: explicitly out of scope per locked #28).
1069: test (locked #34), show an amber warning: "Mic level is low.
1076: ### 6.4 Mic level meter (locked #32, #33) — horizontal bar graph
1110: ### 6.5 Persistence (locked #30)
1119: ### 6.6 Mid-session disconnect (locked #31, #35)
1132: screenshots only." (locked #31)
1138: ### 6.7 New module skeleton
1174: ### 6.8 Step 0 for Claude Code (Phase 3)
1189: ### 6.9 Manual test plan (Phase 3)
1217: ### 6.10 Phase 3 deliverables
1232: # ═══════════════════════════════════════════════════════════════════
1233: #  PHASE 4 — DROPBOX UPLOAD & TESTER IDENTITY
1234: # ═══════════════════════════════════════════════════════════════════
1238: Locked decisions: 7, 8, 9, 10, 12, 13, 14, 15, 16, 25, 40.
1240: Goal: after a session ends, package it, upload it to Dropbox, show
1243: ## 7. PHASE 4 DETAIL
1245: ### 7.1 Tester name entry (locked #13)
1264: ### 7.2 Dropbox as destination (locked #8)
1275: ### 7.3 OAuth2 flow (locked #9)
1307: ### 7.4 Folder structure (locked #10, #14)
1321: Session folder name (locked #14): `session_<datetime>_<tester_name>`
1327: ### 7.5 Auto-upload with toggle (locked #7, #15)
1352: single deferred follow-up upload of `transcript.md` via the
1371: **Signal listener lifecycle — critical.** For the deferred transcript
1391: On success (locked #15):
1414: ### 7.6 test_report.md generation (locked #12)
1449: ### 7.7 Retry + View Folder (locked #16, #25)
1489: View Folder (locked #25):
1495: ### 7.8 New module skeleton
1520: ### 7.9 Step 0 for Claude Code (Phase 4)
1543: the Phase 4 deferred-upload path is dead code. Report.
1545: ### 7.10 Manual test plan (Phase 4)
1576: T10 Deferred transcript upload. Run a session with audio long enough
1585: ### 7.11 Phase 4 deliverables
1595: - [ ] Deferred transcript.md upload hooked to that signal
1603: # ═══════════════════════════════════════════════════════════════════
1604: #  PHASE 5 — TRIAGE DASHBOARD (YOUR SIDE)
1605: # ═══════════════════════════════════════════════════════════════════
1609: Locked decisions: 38.
1611: Goal: when sessions accumulate in your Dropbox folder, give you a
1615: ## 8. PHASE 5 DETAIL
1617: ### 8.1 Architecture decision: separate codebase
1626: ### 8.2 Data model
1647: ### 8.3 Scanner
1659: ### 8.4 Dashboard UI
1681: ### 8.5 Feedback channel
1708: testers are explicitly out of scope.

## PANDA_GALLERY_SESSION_MANAGER_SKILL_SPEC.md

Bytes: 34324

1: # PANDA_GALLERY_SESSION_MANAGER_SKILL_SPEC.md
7: **Status:** Draft. Pending implementation approval.
13: ## 1. Purpose
25: ## 2. What a "skill" is, concretely (v1 review §P1 fix)
39: ## 3. Scope (v1 P3 scope-down)
41: ### 3.1 In scope for v1
49: ### 3.2 Out of scope for v1
59: ### 3.3 Explicit v1 simplification vs v1-draft
67: ## 4. Trigger keywords
81: ### 4.1 Collision check with existing skill
89: ## 5. User-facing behavior
91: ### 5.1 Session open — step-by-step (v1 P4 fix)
127: ### 5.2 Session close — step-by-step
173: Select-String -Path BUGS.md -Pattern 'Status:\*\* Open' | Measure-Object | Select-Object -ExpandProperty Count
178: ### 5.3 Partial flows
186: ## 6. HANDOFF template (v1 P6 fix — matches HANDOFF_22 markdown style)
193: # HANDOFF_{N} — {YYYY-MM-DD} {time_descriptor}
195: ## Session-start pulse check for next chat
201: Select-String -Path BUGS.md -Pattern 'Status:\*\* Open' | Measure-Object | Select-Object -ExpandProperty Count
204: ## Repo state at session close
211: ## What shipped this session
214: ### Commits ({N} total)
219: ### Bugs closed
223: ### Bugs logged / rescoped
229: ## Known open glitches / bugs
232: ### Bug #{N} — {title}
236: ### {feature} verification pending
239: ## Workflow lessons from this session
242: ### {lesson title}
247: ## Next-session candidates (ranked)
253: ## Deferred / open reminders
257: ## Environment / machinery notes
264: ### 6.1 Style consistency notes
273: ## 7. Skill file structure
289: ### 7.1 SKILL.md content
297: # Panda Gallery Session Manager Skill
301: ## Workflow: Session open
310: ### Session-open output format
328: ## Workflow: Session close
341: ## Critical rules
349: ## Files in this skill
356: ### 7.2 next_handoff_number.py
399: ## 8. Skill discovery — how does Claude know this skill exists? (v1 O1 fix, v2 revised)
405: ### 8.1 Desktop Claude discovery — via memory rule pointer
411: > PG session-lifecycle keywords (`session start`, `session close`, `end session`, `pulse check`, `handoff`, `draft handoff`, `wrap up`, `wrapping up`, or pasted pulse-check output) trigger the pg-session-manager skill. Read `C:\panda-gallery\skills\pg-session-manager\SKILL.md` via MCP and follow its workflow. Supersedes the prose description in memory rule #20.
417: ### 8.2 Claude Code discovery — via CLAUDE.md SKILLS section
421: ### 8.3 Phase ordering for discovery setup
446: ### 8.4 Memory rule coordination
460: ## 9. Date handling (v1 O4 fix)
470: ## 10. Error handling
480: ### 10.1 Fresh-chat mid-session interaction (v1 O3 fix)
494: ## 11. Interaction with existing conventions
512: ## 12. Implementation plan
559: ## 13. Testing plan
593: ### 13.1 Testing notes
601: ## 14. Commit plan
611: ## 15. Follow-ups (not v1)
624: ## 16. Open questions (remaining after v2)
631: All 4 v1 open questions now closed in v2.

## PANDA_GALLERY_SPLIT_TEMPLATE_SPEC.txt

Bytes: 22153

1: # ══════════════════════════════════════════════════════════════════════════════
2: #  PANDA GALLERY — SPLIT TEMPLATE FEATURE SPECIFICATION
3: #  Extracts individual radiographs from composite/grouped images
4: # ══════════════════════════════════════════════════════════════════════════════
7: # ─────────────────────────────────────────────────────────────────────────────
8: #  OVERVIEW
9: # ─────────────────────────────────────────────────────────────────────────────
11: #  Dentists frequently receive radiographs from referring offices as a
12: #  single composite image — multiple radiographs arranged on a black
13: #  background in one file (e.g., an FMX with 18 images in one JPEG).
15: #  "Split Template" extracts each individual radiograph from the
16: #  composite and imports them as separate image files into PG.
18: #  The original composite is ALWAYS preserved (Rule 2).
19: #  Extracted images are NEW files — copies, not modifications.
21: #  USE CASES:
22: #    - Referral from another dentist sends a composite FMX image
23: #    - Legacy imaging system exported composites, not individual files
24: #    - Patient brings a CD/USB with composite radiograph images
25: #    - Scanned film-based radiograph montages
28: # ─────────────────────────────────────────────────────────────────────────────
29: #  WORKFLOW — WHERE IT FITS
30: # ─────────────────────────────────────────────────────────────────────────────
32: #  Split Template is an IMPORT-TIME feature. Three entry points:
34: #  1. AUTO-DETECT ON IMPORT:
35: #     User imports an image file via file picker, drag-drop, or paste.
36: #     PG analyzes the image and detects it may be a composite:
37: #       - Large image dimensions (wider than 2000px AND taller than 1500px)
38: #       - Contains significant black/dark background regions
39: #       - Multiple distinct rectangular regions detected
40: #     If detected, shows prompt:
41: #       ┌─────────────────────────────────────────────────────────┐
42: #       │  Composite Image Detected                           ✕  │
43: #       │                                                        │
44: #       │  This image appears to contain 7 individual            │
45: #       │  radiographs arranged in a composite layout.           │
46: #       │                                                        │
47: #       │  [Auto-Split]  [Manual Split]  [Import As-Is]          │
48: #       └─────────────────────────────────────────────────────────┘
49: #     "Import As-Is" imports the composite as a single image (no split).
50: #     User can always split later via method 2 or 3.
52: #  2. RIGHT-CLICK IN LIBRARY:
53: #     Right-click any image in the library grid →
54: #     "Split Template — Extract Individual Images"
55: #     Opens the split interface for that image.
57: #  3. MENU BAR:
58: #     Tools → "Split Template" → file picker to select a composite image.
59: #     Or if an image is currently selected, splits that image.
62: # ─────────────────────────────────────────────────────────────────────────────
63: #  AUTO-SPLIT MODE
64: # ─────────────────────────────────────────────────────────────────────────────
66: #  PG analyzes the composite image and automatically detects individual
67: #  radiographs within it.
69: #  DETECTION ALGORITHM:
70: #    1. Convert image to grayscale
71: #    2. Threshold: pixels below brightness 30 → "background" (black gaps)
72: #    3. Find connected regions of non-background pixels (contours)
73: #    4. Filter regions by minimum size (at least 100×100px — reject noise)
74: #    5. Compute bounding rectangles for each valid region
75: #    6. Each bounding rectangle = one detected radiograph
76: #    7. Sort detected regions: left-to-right, top-to-bottom
77: #       (reading order — matches how templates are typically arranged)
79: #  PREVIEW SCREEN:
80: #    ┌─────────────────────────────────────────────────────────────────┐
81: #    │  Split Template — Auto-Detect Results                      ✕  │
82: #    ├─────────────────────────────────────────────────────────────────┤
83: #    │                                                                │
84: #    │  ┌──────┬──────┬──────┐                                       │
85: #    │  │  1   │  2   │  3   │   Detected regions shown with         │
86: #    │  │ ┄┄┄┄ │ ┄┄┄┄ │ ┄┄┄┄ │   numbered accent-color outlines     │
87: #    │  ├──────┼──────┼──────┼──────┐                                │
88: #    │  │  4   │  5   │  6   │  7   │                                │
89: #    │  │ ┄┄┄┄ │ ┄┄┄┄ │ ┄┄┄┄ │ ┄┄┄┄ │                                │
90: #    │  └──────┴──────┴──────┴──────┘                                │
91: #    │                                                                │
92: #    │  Found: 7 images                                               │
93: #    │                                                                │
94: #    │  [Adjust Regions]  [Accept & Split]  [Switch to Manual]       │
95: #    └─────────────────────────────────────────────────────────────────┘
97: #    Each detected region: numbered, outlined in accent color (#e8a87c)
98: #    on top of the original composite image.
100: #    "Accept & Split" → extracts all detected regions as individual files.
101: #    "Adjust Regions" → enters adjustment mode (see below).
102: #    "Switch to Manual" → opens Manual Split mode.
104: #  ADJUSTMENT MODE:
105: #    After auto-detect, user can refine the detection:
106: #    - Click a region outline to select it (handles appear)
107: #    - Drag handles to resize the extraction rectangle
108: #    - Drag the rectangle to reposition it
109: #    - Right-click region → "Delete" (remove false detection)
110: #    - Click "Add Region" → draw a new rectangle for missed image
111: #    - Regions auto-renumber after any add/delete
112: #    - "Re-detect" button → runs auto-detection again (reset)
113: #    - "Accept & Split" when satisfied
116: # ─────────────────────────────────────────────────────────────────────────────
117: #  MANUAL SPLIT MODE
118: # ─────────────────────────────────────────────────────────────────────────────
120: #  User manually draws rectangles around each radiograph.
121: #  Used when auto-detect fails (unusual layouts, non-black background,
122: #  overlapping images, film scans with irregular spacing).
124: #  INTERFACE:
125: #    ┌─────────────────────────────────────────────────────────────────┐
126: #    │  Split Template — Manual Mode                              ✕  │
127: #    ├─────────────────────────────────────────────────────────────────┤
128: #    │                                                                │
129: #    │  Composite image displayed at fit-to-window size               │
130: #    │  Zoom/pan available (mouse wheel, Space+drag)                  │
131: #    │                                                                │
132: #    │  Click and drag to draw a rectangle around each radiograph.    │
133: #    │  Each rectangle numbered automatically in drawing order.       │
134: #    │                                                                │
135: #    │  Status: 4 regions defined                                     │
136: #    │                                                                │
137: #    │  [Clear All]  [Undo Last]  [Split]  [Cancel]                  │
138: #    └─────────────────────────────────────────────────────────────────┘
140: #  DRAWING BEHAVIOR:
141: #    Click and drag → draws a rectangle with accent-color outline
142: #    Rectangle auto-numbered (1, 2, 3...)
143: #    Selected rectangle: resize handles (8 points), drag to move
144: #    Right-click rectangle: Delete, Renumber
145: #    Undo (Ctrl+Z): remove last drawn rectangle

## PANDA_GALLERY_TEMPLATE_SPEC.txt

Bytes: 67015

1: # ══════════════════════════════════════════════════════════════════════════════
2: #  PANDA GALLERY — TEMPLATE SYSTEM DEFINITIVE SPECIFICATION
3: #  This replaces Section 8 of the main spec entirely.
4: #  Claude Code: DELETE all existing template code and rebuild from this spec.
5: # ══════════════════════════════════════════════════════════════════════════════
8: # ─────────────────────────────────────────────────────────────────────────────
9: #  OVERVIEW
10: # ─────────────────────────────────────────────────────────────────────────────
12: #  The template system arranges 2–30 dental radiographs into structured
13: #  diagnostic layouts. Think of it as building with Lego blocks — each
14: #  block is a dental sensor-sized rectangle that you drag from a palette
15: #  onto a canvas to build your layout.
17: #  ╔════════════════════════════════════════════════════════════════════╗
18: #  ║  CRITICAL: TWO SEPARATE SCREENS — NEVER CONFUSE THEM            ║
19: #  ╠════════════════════════════════════════════════════════════════════╣
20: #  ║                                                                  ║
21: #  ║  1. TEMPLATE DESIGNER (template_designer.py)                         ║
22: #  ║     Purpose: DESIGN the grid layout                              ║
23: #  ║     Slots ARE movable — drag to rearrange                        ║
24: #  ║     Drag NEW sensors from palette to add slots                   ║
25: #  ║     Resize slots, change sensor sizes, edit labels               ║
26: #  ║     Save/rename template layouts                                 ║
27: #  ║     NO patient images here — blank slots only                    ║
28: #  ║                                                                  ║
29: #  ║  2. TEMPLATE VIEW (template_view.py)                             ║
30: #  ║     Purpose: POPULATE layout with patient images                 ║
31: #  ║     Slots are FIXED — you do NOT move them here                  ║
32: #  ║     Drag IMAGES from filmstrip into slots                        ║
33: #  ║     Adjust brightness/contrast on placed images                  ║
34: #  ║     Add annotations to placed images                             ║
35: #  ║     Export/print the populated template                          ║
36: #  ║                                                                  ║
37: #  ║  SLOT DRAGGING CODE BELONGS ONLY IN THE EDITOR.                  ║
38: #  ║  NEVER add movable slot functionality to the view.               ║
39: #  ║                                                                  ║
40: #  ╚════════════════════════════════════════════════════════════════════╝
42: #  NAVIGATING BETWEEN EDITOR AND VIEW:
44: #    View → Editor:
45: #      Right-click template background → "Edit Template"
46: #        Opens current layout in Template Designer for modification.
47: #        Changes saved back to the same template.
48: #      Right-click template background → "Edit Template (Save as New)"
49: #        Opens current layout in Template Designer AND prompts for a
50: #        new name. Original template is preserved unchanged.
51: #        Creates a new template based on the current layout.
52: #      Templates tab → pencil icon "Edit Layout" button
53: #        Same as right-click "Edit Template".
55: #    Editor → View:
56: #      After saving in the editor, user returns to the Template View.
57: #      If editing the current template: view refreshes with new layout.
58: #      If "Save as New": view switches to the new series.
60: #  TERMINOLOGY:
61: #    Template = blank reusable layout (designed in Template Designer)
62: #    Series = patient's mounted images using a template
63: #    Mount = the act of placing images into a series
64: #    UI: "New Series", "Mount All", "Series (3)" filter tab
65: #    Never use "Template Instance", "Composite", or "Layout" in UI.
68: # ─────────────────────────────────────────────────────────────────────────────
69: #  DENTAL SENSOR SIZES (built-in, not configurable)
70: # ─────────────────────────────────────────────────────────────────────────────
72: #  Five standard dental radiograph sensor sizes, pre-loaded:
74: #  ┌──────────────────────────────────────────────────────────────────┐
75: #  │  Name          │ Label      │ Width  │ Height │ Aspect Ratio     │
76: #  ├──────────────────────────────────────────────────────────────────┤
77: #  │  Size 0        │ Pediatric  │ 22mm   │ 35mm   │ 0.629 (portrait) │
78: #  │  Size 1        │ Anterior   │ 24mm   │ 40mm   │ 0.600 (portrait) │
79: #  │  Size 2        │ Adult      │ 31mm   │ 41mm   │ 0.756 (portrait) │
80: #  │  Size 3        │ Bitewing   │ 27mm   │ 54mm   │ 0.500 (portrait) │
81: #  │  Size 4        │ Occlusal   │ 57mm   │ 76mm   │ 0.750 (portrait) │
82: #  └──────────────────────────────────────────────────────────────────┘
84: #  DEFAULT: Size 2 (most common in general dentistry)
85: #  SECOND MOST COMMON: Size 1
87: #  Every sensor can be used in PORTRAIT or LANDSCAPE orientation.
88: #  Portrait: width < height (vertical rectangle)
89: #  Landscape: width > height (horizontal rectangle) — just rotated 90°
91: #  The aspect ratio is LOCKED per slot. When you resize a slot larger
92: #  or smaller, the proportions stay correct for that sensor size.
93: #  You cannot stretch a slot into a non-sensor aspect ratio.
96: # ─────────────────────────────────────────────────────────────────────────────
97: #  PATIENT ID CARD
98: # ─────────────────────────────────────────────────────────────────────────────
100: #  A special slot type that displays patient and clinic identification
101: #  information within the template. Not a radiograph — an info card.
103: #  IN THE SENSOR PALETTE:
104: #    Shown as a separate item below the 5 sensor sizes:
105: #    ┌─────────────────┐
106: #    │  📋 ID Card      │
107: #    │  Patient Info    │
108: #    └─────────────────┘
109: #    Drag onto canvas like any sensor. Snaps to grid.
110: #    Default aspect ratio: ~3.5:2 (business card proportions).
111: #    Resizable like any slot. Typically placed in top-left or
112: #    bottom of template.
114: #  AUTO-GENERATED CONTENT (default):
115: #    ┌─────────────────────────────────────────┐
116: #    │  [LOGO]  Dr. Smith Family Dentistry     │
117: #    │          123 Main Street                │
118: #    │          Bellevue, WA 98004             │
119: #    │          (425) 555-1234                 │
120: #    │                                         │
121: #    │  Patient: Alice Johnson                 │
122: #    │  DOB: 03/15/1985                        │
123: #    │  Date: Apr 11, 2026                     │
124: #    │  Template: Full Mouth Series            │
125: #    └─────────────────────────────────────────┘
127: #    Clinic info pulled from Practice Info (setup wizard Step 5).
128: #    Patient info pulled from patient record automatically.
129: #    Date = series visit date.
130: #    Template name = the template being used.
131: #    NO MANUAL ENTRY NEEDED — everything mounts.
133: #  CUSTOMIZATION (Preferences → ID Card Settings):
134: #    Clinic fields: logo, name, address, phone, email, website
135: #    Patient fields toggleable: name, DOB, patient ID, insurance
136: #    Image fields toggleable: date, template name, provider name
137: #    Font: family, size, color (default matches app theme)
138: #    Background: color picker or transparent
139: #    Layout: left-aligned, centered, or custom arrangement
140: #    Card style toggle:
141: #      "Generated" — built from fields above (default)
142: #      "Custom Image" — user uploads their own designed card image

## PANDA_GALLERY_TRANSCRIPT_V2_SPEC.md

Bytes: 11755

1: # PANDA_GALLERY_TRANSCRIPT_V2_SPEC.md
7: **Status:** Draft — pending Claude Code implementation.
13: ## 1. Purpose
23: ## 2. Scope
31: Out of scope (do not touch in v3.45):
41: ## 3. Output format changes
43: ### 3.1 Frame heading — add duration
57: ### 3.2 Segment bullet — add screen-trace when it crosses a boundary
82: ### 3.3 Pre-F12 segment — add short-form annotation when it straddles
102: ### 3.4 Silence frames — unchanged from v3.44
108: ### 3.5 Frame-contained segments — unchanged from v3.44
114: ## 4. Implementation
116: ### 4.1 Separation of concerns
124: ### 4.2 Screen-trace computation
137: ### 4.3 Frame-duration computation
149: ### 4.4 Error handling
158: ### 4.5 No configuration flag
164: ## 5. Testing
188: ## 6. Not in scope (deferred, logged in spec only)
190: Items considered and explicitly deferred:
199: ## 7. Commit plan
211: ## 8. Follow-ups (potential v3.46+)

## PANDA_GALLERY_TRANSCRIPTION_SPEC.md

Bytes: 18849

1: # PANDA_GALLERY_TRANSCRIPTION_SPEC.md
7: **Status:** Draft — pending Claude Code implementation.
13: ## 1. Purpose
19: Invoked manually from the command line. Not integrated into `workflow_capture.py` in v1. Future integration (e.g., auto-transcribe at `Ctrl+Alt+S`) is deferred — the v1 script is designed to be trivially subprocess-able from MainWindow if that time comes.
23: ## 2. File location
31: ## 3. Dependencies
33: ### 3.1 New runtime dependency
37: ### 3.2 Installation
50: ### 3.3 Model
61: ## 4. Command-line interface
63: ### 4.1 Invocation (PowerShell)
70: ### 4.2 Arguments
89: ### 4.3 Exit codes
97: ## 5. Input
99: ### 5.1 Session resolution
120: ### 5.2 metadata.json schema (v6) — fields consumed
150: ### 5.3 audio.wav
158: ## 6. Frame-to-audio alignment
160: ### 6.1 Frame time mapping
171: ### 6.2 Segment assignment rule
183: ### 6.3 Edge cases
193: ## 7. Whisper configuration
220: ## 8. Output — transcript.md
222: ### 8.1 Location
226: ### 8.2 Skip-or-overwrite logic
232: ### 8.3 File format
235: # Transcript — session_20260419_141233
246: ## Pre-F12 Narration
250: ## Frame 1 — 001.png @ 00:03.12
255: ## Frame 2 — 002.png @ 00:14.45
259: ## Frame 3 — 003.png @ 00:17.80
264: ### 8.4 Timestamp format
268: ### 8.5 Header fields
274: ## 9. Error handling
276: ### 9.1 Robustness requirements (CLAUDE.md CODE QUALITY STANDARDS §Robustness compliance)
286: ### 9.2 Defensive code must cite a realistic failure
300: ## 10. Progress output
327: ## 11. Module structure
352: # faster-whisper imported inside main() to allow missing-dep error to fire
353: # before argparse parses; see error handling §9.
389: ## 12. Testing
391: ### 12.1 Manual test plan
412: ### 12.2 Not tested in v1
416: - Non-English audio (language="en" hardcoded; other languages would need a `--language` flag, deferred).
420: ## 13. Follow-ups (not v1)
427: - **Word-level timestamps:** `word_timestamps=True` with clickable `[MM:SS.CS]` links in transcript.md. Deferred — segment-level is sufficient for review.
428: - **GPU path:** `device="cuda"` or `device="dml"` for DirectML. Deferred — CPU int8 is fast enough for typical <5-minute sessions.
432: ## 14. Commit plan

## PANDA_GALLERY_v4_SPEC_1.md

Bytes: 105620

1: # ══════════════════════════════════════════════════════════════════════════════
2: #  PANDA GALLERY v4.0 — COMPLETE DEVELOPMENT SPECIFICATION
3: #  Dental Patient Image & Document Management System
4: # ══════════════════════════════════════════════════════════════════════════════
6: #  This document is the complete, authoritative specification for building
7: #  Panda Gallery. It incorporates:
8: #    - Lessons from iterative prototyping (DPI, rendering, performance)
9: #    - A detailed Q&A with the product owner covering 40+ design decisions
10: #    - Architecture guidance from professional desktop app development
11: #    - The phased build strategy (hardest thing first)
12: #    - Complete UI walkthrough from login to every interaction mode
13: #    - Data safety and recovery systems
14: #    - PMS bridge integration for 5 dental systems
15: #    - First-time setup wizard
16: #    - Sharing and referral workflow
18: #  Every question that would cause a developer to guess has been answered.
19: #  19 sections. ~150 checklist items. 7 build phases.
21: # ══════════════════════════════════════════════════════════════════════════════
24: # ─────────────────────────────────────────────────────────────────────────────
25: #  1. VISION & IDENTITY
26: # ─────────────────────────────────────────────────────────────────────────────
28: #  Panda Gallery is an Adobe Lightroom / Photoshop LITE clone purpose-
29: #  built for dentistry. It combines:
31: #    1. A full NON-DESTRUCTIVE image editor — Lightroom-style adjustment
32: #       sliders + Photoshop-style vector annotation/drawing tools
33: #    2. A RADIOGRAPH TEMPLATE system — arrange 2–30 images into
34: #       diagnostic layouts with user-defined resizable grids
35: #    3. An IMAGE COMPARISON MODE — 2–10 images side by side with
36: #       synchronized zoom/pan, saveable as new templates
37: #    4. A PATIENT DATABASE — scheduling, archiving, audit trails,
38: #       multi-user role-based access across multiple clinic locations
39: #    5. A DOCUMENT MANAGEMENT system — store text docs, spreadsheets,
40: #       PDFs alongside images with thumbnail preview
42: #  Think of it as:
43: #    Adobe Photoshop Elements (editing model)
44: #    + Dental systems like Sidexis (data model)
45: #    + Custom template system (radiograph layouts)
46: #    + Multi-location clinic infrastructure
48: #  DESIGN PHILOSOPHY:
50: #    ULTRAMODERN, SLICK, INTUITIVE. Match the quality of Adobe Creative
51: #    Suite's dark UI. Not a clunky medical application. Every panel,
52: #    button, slider, and dialog must feel polished and professional.
53: #    A dental assistant with no technical training should be productive
54: #    within minutes of first launch.
56: #    CUSTOMIZABLE BY DEFAULT. Wherever feasible:
57: #      - Template layouts (create, edit, save, reuse)
58: #      - Export file naming conventions (user-defined patterns)
59: #      - Annotation defaults (color, brush size, font)
60: #      - Window layout (dockable panels, collapsible sections)
61: #      - Keyboard shortcuts (displayed in menus)
62: #      - Image organization (custom categories, libraries)
63: #      - Color swatches in drawing panel (user add/remove)
64: #      - Default adjustments per image category
65: #      - Template grid dimensions, gap, background color
66: #      - Session timeout duration (10min default, up to 8hr disable)
67: #      - Print header/footer visibility
68: #      - Paper size selection
69: #      - Patient form fields (required/optional/hidden, custom fields)
70: #      - Login policy (admin-controlled per clinic)
72: #    ALL ACTIONS REVERSIBLE. Undo/redo for everything. Non-destructive
73: #    editing means original files are never modified. Archive is
74: #    reversible. Delete means hide, never destroy.
76: #  TARGET USERS: Dentists, hygienists, assistants, administrators.
77: #  TARGET SCALE: 15+ concurrent users across multiple clinic locations.
80: #  ╔════════════════════════════════════════════════════════════════════╗
81: #  ║  INVIOLABLE DESIGN RULES — THESE OVERRIDE ALL OTHER DECISIONS    ║
82: #  ╚════════════════════════════════════════════════════════════════════╝
84: #  RULE 1: NEVER LOSE PATIENT DATA.
85: #    Every operation must be recoverable. There is no "permanent delete"
86: #    in the user-facing UI. "Delete" means archive/hide. Only a system
87: #    admin with direct database access can truly purge data, and even
88: #    then only after a configurable retention period (default 7 years).
89: #    All database writes are transactional. All state changes are logged.
91: #  RULE 2: NO ORIGINAL IMAGE CAN BE LOST, DELETED, OR PERMANENTLY EDITED.
92: #    Original image files are NEVER modified, overwritten, or removed
93: #    from storage. Edits are stored as parameters (JSON). "Deleting"
94: #    an image hides it from the UI but preserves the file and its
95: #    database record with a "deleted" status flag. The original can
96: #    always be recovered. Export creates a NEW file — never touches
97: #    the original. This rule has no exceptions.
99: #  RULE 3: NETWORK RESILIENCE — OFFLINE-FIRST ARCHITECTURE.
100: #    The app must function FULLY when the network goes down.
101: #    Implementation:
102: #      - Each workstation maintains a LOCAL SQLite database as a cache
103: #      - All edits, new patients, imports write to local DB first
104: #      - Background sync service pushes changes to central PostgreSQL
105: #        when network connection is available
106: #      - On network loss: app continues working seamlessly from local
107: #        cache. No error dialogs. No blocked workflows.
108: #      - On network restore: automatic background upload of all
109: #        queued changes to the server. Conflict resolution: last-write-
110: #        wins with full audit trail of both versions.
111: #      - Images imported offline are stored locally and uploaded to
112: #        the shared server when connection returns
113: #      - Status bar indicator: 🟢 Connected / 🟡 Syncing / 🔴 Offline
114: #      - User should never have to think about network state
116: #  RULE 4: WHEN IN DOUBT, DO WHAT ADOBE LIGHTROOM / PHOTOSHOP DOES.
118: #  RULE 5: WHEN IN DOUBT ABOUT UI, CHOOSE THE MOST MODERN AND
119: #          USER-FRIENDLY APPROACH.
122: # ─────────────────────────────────────────────────────────────────────────────
123: #  2. TECHNOLOGY STACK
124: # ─────────────────────────────────────────────────────────────────────────────
126: #  Language:        Python 3.10+
127: #  GUI Framework:   PySide6 (Qt 6 for Python)
128: #  Canvas/Scene:    QGraphicsView + QGraphicsScene + QGraphicsItem
129: #  Image Process:   Pillow (PIL) + OpenCV (optional, advanced filters)
130: #  Database:        PostgreSQL (production) / SQLite (dev + local cache)
131: #  ORM:             SQLAlchemy (same code, swap connection string)
132: #  Scanner:         TWAIN protocol (ScanX and other dental hardware)
133: #  Target OS:       Windows 10/11 primary, macOS/Linux compatible
134: #  Target Display:  4K (3840×2160) with full HiDPI support
135: #  Delivery:        Source .py files + compiled .exe (PyInstaller)
136: #  Updates:         Manual deployment to workstations (auto-update future)
138: #  Install (dev):   pip install PySide6 Pillow SQLAlchemy psycopg2
140: #  WHY PYSIDE6 (proven by prototyping):
141: #    Iteration counts: DPI 4→0, Overflow 3→0, Flicker 2→0, Annotations 3→0
142: #    Native: zoom, pan, hit-testing, layers, HW accel, 4K, drag-drop,
143: #    undo (QUndoStack), printing (QPrinter), dockable panels, QSS styling
145: #  4K: setAttribute(Qt.AA_EnableHighDpiScaling/UseHighDpiPixmaps)
146: #      SVG icons. No hardcoded pixels. Dynamic QSS.

## PG_V4_MVP_PLAN.md

Bytes: 25709

1: # Panda Gallery v4.0 — MVP Plan
3: **Status:** Active planning document. Authoritative for v4.0 scope and sequencing.
10: ## 0. Purpose of this document
14: STRATEGY_NOTES.md remains the decision-capture log (why we chose X over Y). This document is the reference for what we're building and in what order. If the two disagree, this document is the current truth for v4.0 scope; STRATEGY_NOTES entries dated before 2026-04-23 that contradict this plan are superseded by the 2026-04-23 MVP redefinition entry.
16: This plan is hard-gated. Scope locked today. Requests to expand scope during the 3-month window get deferred to v4.1 by default, with rare explicit exceptions recorded in STRATEGY_NOTES.
20: ## 1. The MVP redefinition
22: ### Previous framing (superseded)
23: STRATEGY_NOTES 2026-04-17 framed the MVP around Rebecca's commercial partnership: PG had to be "clinically useful for any general dentist Rebecca recommends it to," with installer, DICOM import, HIPAA basics, and professional exports as MVP-defining. That framing treated Rebecca as both a commercial partner AND a product authority.
25: ### Current framing (2026-04-23)
26: Darrin is the product authority. 25+ years of clinical practice including board-certified periodontics, plus shipping Panda Perio, make his product instinct the primary design input for PG. Rebecca is a commercial partner and a clinician trainer — her input is market signal to weigh, not an MVP veto.
28: ### What the market actually needs
36: ### What is NOT MVP-defining anymore
37: Installer, DICOM import, and HIPAA-basics are **distribution-layer** work, not MVP-defining. They ship in v4.1 after v4.0 is proven internally. Packaging an app for external clinicians before the app itself is differentiated is the wrong order.
41: ## 2. Architectural decisions locked this session
45: ### 2.1 AI scope — groundwork-only for v4.0
52: Picking the actual model/vendor is deferred to v4.1. Model landscape is moving too fast to commit in April 2026.
54: ### 2.2 Unified arrangement canvas
59: ### 2.3 Split approach — branch-and-burn UI shell, Ship-of-Theseus features
65: ### 2.4 Three-month hard-gated window
66: Ship target: 2026-07-23. Scope defined here is locked. Scope expansion during the window gets deferred to v4.1 by default. Exceptions require a STRATEGY_NOTES entry recording why.
70: ## 3. Three-tier sequencing
72: ### Tier 1 — Foundation / Spine (Month 1)
79: ### Tier 2 — Heart of PG (Month 2)
86: ### Tier 3 — Polish on working spine (Month 3)
96: ## 4. Month-by-month breakdown
98: ### Month 1 — 2026-04-23 to 2026-05-23 — Foundation
118: ### Month 2 — 2026-05-23 to 2026-06-23 — Heart of PG
139: ### Month 3 — 2026-06-23 to 2026-07-23 — Polish and ship
152: - Release notes. Versioned splash (bug #51 territory). v4.0 tag. HANDOFF to v4.1 with backlog of deferred items (installer, DICOM, HIPAA-basics, visible AI features, control-layout polish items, remaining UX items).
158: ## 5. Architectural groundwork that v4.0 must include
162: ### 5.1 AI plumbing (split across two landings to avoid double DB migration)
175: ### 5.2 Arrangement extensibility (lands Month 2 Weeks 5–6)
179: ### 5.3 Presentation extensibility (lands Month 2 Week 7)
183: ### 5.4 Module tab extensibility (lands Month 1 Week 3)
186: ### 5.5 Navigation history extensibility (lands Month 1 Week 3)
191: ## 6. Hard gates — what does NOT go in v4.0
193: These are deferred to v4.1 by explicit decision today. Attempts to sneak them into v4.0 scope should be refused unless explicitly re-opened via STRATEGY_NOTES.
195: ### 6.1 Distribution-layer work
202: ### 6.2 Visible AI features
203: - No tooth-number detection. No caries detection. No auto-sort radiograph-vs-photo. No AI-assisted segmentation. No AI-suggested arrangements. All deferred to v4.1+. The plumbing ships; the features don't.
205: ### 6.3 Low-priority UX and cosmetic bugs
206: - #102 / #103 / #100 / #89 / #46 / #105 / #79 / #97 / #90. Every one of these is real but none is MVP-defining. They ride in v4.1 as a polish pass.
210: ### 6.4 Template designer v2 / freeform spec refinements
213: ### 6.5 Clinical-consultant gated features
218: ## 7. Risks and mitigations
220: ### 7.1 Scope creep within the 3-month window
224: ### 7.2 UI shell rewrite takes longer than Week 2
228: ### 7.3 Unified canvas migration breaks existing data
232: ### 7.4 Presentation module multi-monitor edge cases
236: ### 7.5 Rebecca disagreement on the MVP redefinition
240: ### 7.6 Reliability work in Tier 1 and Tier 3 uncovers deep architectural debt
241: **Risk:** a shutdown-error fix reveals the real problem needs a bigger rewrite than MVP scope allows.
242: **Mitigation:** time-box reliability work. If a fix exceeds its time budget, defer to v4.1 and live with the defect. The MVP ship matters more than any single defect.
244: ### 7.7 Darrin-as-solo-product-authority blind spots
250: ## 8. Success criteria
269: ## 9. Open questions to resolve before Month 1 starts
273: ### 9.1 UI shell mockup authority
276: ### 9.2 Keyboard shortcut conflicts
279: ### 9.3 Arrangement file format
280: Saved arrangements: SQLite rows (current approach) or separate on-disk `.pga` (Panda Gallery Arrangement) files users can email/share? My recommendation: SQLite for v4.0, file-based export as a v4.1 feature. Keeps data-layer simple for MVP.
282: ### 9.4 Presentation mode keyboard shortcut
285: ### 9.5 Module tab keyboard navigation
288: ### 9.6 What happens to workflow_capture / instruction pane in v4.0?
289: These are dev tooling, not user-facing features. Question: do they stay visible in the production build, or do they hide behind the --dev flag (bug #97, currently deferred)?
298: ## 10. Tracking and accountability
302: - **Month 1 deliverable:** `[ ] v3.90 target — status: not started`
303: - **Month 2 deliverable:** `[ ] v3.95 target — status: not started`
304: - **Month 3 deliverable:** `[ ] v4.0 target — status: not started`
312: ## Appendix A — Decisions recap for quick reference
321: | MVP authority | Darrin (§1) |
322: | Distribution layer | Deferred to v4.1 (§6.1) |
323: | Visible AI features | Deferred to v4.1+ (§6.2) |
329: ## Appendix B — File and module impact

## STYLE.md

Bytes: 18581

1: # Panda Gallery — STYLE.md
8: The goal is to prevent new spaghetti while letting cleanup ride along with feature work. Dedicated refactor commits tend to be abandoned; opportunistic refactor piggybacks on feature testing and actually ships.
12: ## 1. Purpose and scope
18: - STYLE.md does NOT cover formatting (Black), commit message style (CLAUDE.md), branching, or Python version policy. See section 11 for the full non-goals list.
23: ## 2. Module size
40: ## 3. Class responsibility
56: ## 4. State ownership
72: ## 5. Signal and slot naming
89: ## 6. Styling and palette
106: ### QSS cascade gotcha
109: ### Widget sizing — minimum width and wrap breakpoints
126: ## 7. Docstrings
128: **Rule:** Docstrings describe external behavior only — what callers need to know. No implementation notes, no history, no TODOs inside docstrings.
142: **Example (violation):** A 20-line docstring covering internal PIL handling, a history of when each parameter was added, and a "TODO: batch loader" note — all of which belong in the code, git log, and DEV_LOG respectively.
146: ## 8. Comments
153: - TODO comments include bug number or design doc reference.
157: ## 9. Testing expectations
169: ## 10. Opportunistic refactor approach
185: ## 11. Non-goals
194: ## 12. Open questions
201: ## 13. Enforcement
212: ## 14. Versioned commit workflow
216: ### Install (one-time per workstation)
223: ### Usage
239: ### Why this replaced the prepare-commit-msg hook (v2.91 → v2.94)
243: ### Bypassing

## TESTING_SECTION_SPEC.md

Bytes: 75615

1: # Testing Section Spec — PASS/FAIL instruction flow + authoring rules
3: **Status:** Draft 6
5: **Supersedes parts of:** `PANDA_GALLERY_REMOTE_TESTING_SPEC_draft4.md` (§4 pane), `WORKFLOW_CAPTURE_SPEC.md` (§6 test loop, if present)
17: - Supersedes the 2026-04-21 STRATEGY_NOTES "Phase 4.5 — Instant Feedback" PASS/FAIL/SKIP design. Checklist is the richer model; per-step single PASS/FAIL is just a 1-item special case (and for single observations, authors use `expected` instead per §9.11). Phase 4.5's scope narrows to Dropbox transport + `test_report.md` rendering layer OVER `results_latest.json` — not a parallel data model.
32: - §11.4 new: Level 3 (live chat) explicitly deferred with architectural limitation documented.
47: ## 1. Goals
58: ## 2. Non-goals
65: ## 3. Architecture
81: ## 4. Schema v2 — `instructions_latest.json`
83: ### 4.1 Top-level
93: ### 4.2 Step object (v2)
117: ### 4.3 v1 backward compatibility
126: ### 4.4 v2 loader strictness
149: ### 4.5 Step kind — checklist and action (v3.65.2+ / v4.00+)
218: ## 5. UI design
220: ### 5.1 Step view (primary screen) — two-row conditional surface
271: ### 5.2 FAIL flow
310: ### 5.3 Summary view
347: ### 5.4 About panel + full keyboard map
393: ### 5.5 Navigation model
408: ### 5.6 Editable prior answers
435: ### 5.7 Review-all screen (before summary)
450: │  Step 4 · C1   ✗ FAIL — modal blocked [Review]   │
467: ### 5.8 Auto-screenshot on FAIL + "Capture now" button (v3.68)
495: ### 5.9 File watcher for instructions reload (v3.68)
510: ### 5.10 Claude-authored follow-up questions (v3.69)
603: ### 5.11 Checklist step view (v3.65.2+)
750: ## 6. Clipboard payload format (secondary, for external sharing only)
758: C1: FAIL — modal dialog blocked Ctrl+Alt+R
770: C1: FAIL — modal dialog blocked Ctrl+Alt+R
776: ## 7. Results file — `workflows/results_latest.json`
778: ### 7.1 Format
844: "note": "modal dialog blocked Ctrl+Alt+R",
873: ### 7.2 Archive-on-load
888: ### 7.3 Claude access via MCP
895: ## 8. Implementation plan
897: ### v3.65 — UI shell: PASS/FAIL buttons + EXPECTED + schema v2
909: - **Header reorganization to §5.1 Row 1 layout is DEFERRED to v3.68**, which also adds the 📷 Capture-now button and Row 2 conditional surface (claude_questions badge, new-instructions banner, Resume banner). Doing the reorg together with those additions keeps all header changes in one commit instead of two.
912: ### v3.65.2 — Checklist step kind
925: - **Supersedes** the 2026-04-21 STRATEGY_NOTES "Phase 4.5 — Instant Feedback" plan for per-step PASS/FAIL/SKIP buttons. Phase 4.5 scope is now narrowed to Dropbox transport + `test_report.md` rendering layer over `results_latest.json`.
927: ### v3.66 — Backend: results file + archive + review + summary
940: ### v3.67 — FAIL panel polish: chips + report + hint protection
948: ### v3.68 — Header reorg + About panel + auto-screenshot + Capture now + file watcher + Resume
959: ### v3.69 — Bidirectional Q&A: Claude-authored follow-up questions
971: ## 9. Instruction authoring rules
975: ### 9.1 Every v2 step MUST have observable PASS criteria
978: ### 9.2 `expected` is observable, not inferred
986: ### 9.3 `expected` states one thing
989: ### 9.4 `test_id` is short, stable, mnemonic
995: ### 9.5 `fail_chips` cover the 2-3 most common FAIL modes
1003: ### 9.6 `report` is what Claude needs, expressed as a prompt to the tester
1009: ### 9.7 `context` sets the scene, not the mechanics
1015: ### 9.8 Step body is one unambiguous action
1022: ### 9.9 No prose-level test descriptions in chat
1025: ### 9.10 Script-level acceptance checklist (pre-paste self-review)
1039: ### 9.11 When to use `checklist` vs. multi-step
1089: ### 9.12 When to use `kind: "action"` (v4.00+)
1128: ## 10. Claude-side memory rules (added by version)
1130: ### 10.1 v3.66 baseline rule
1147: ### 10.2 v3.69 amendment
1170: ## 11. Open questions
1172: ### 11.1 Resume timer on Change Answer
1175: ### 11.2 Screenshot of failing action vs. failing state
1183: ### 11.3 Multi-user / Rebecca testing
1186: ### 11.4 Level 3 (live chat) deferred — architectural limitation
1187: During Draft 4 review, the question of a full bidirectional chat drawer came up. Deferred indefinitely for a specific reason:
1193: ## 12. Summary

## drafts\WORKFLOW_CAPTURE_SPEC.md

Bytes: 27699

1: # WORKFLOW_CAPTURE_SPEC v6 — Mouse Position + Audio Sync
5: Status: SPEC v4 — READY FOR CLAUDE CODE
24: Design goal: one-session ship. Full 16-test pass before commit.
27: NON-GOALS (explicit)
30: Out of scope for v6:
118: - Status: "Captured frame N"
138: g. Status: "Saved N frames + audio.wav (T seconds)" or
390: log.warning(f"Audio callback status: {status}")
547: E7. F12 blocked by Qt context menu (BUG #80, v5) → unchanged.

## workflows\design\region_capture_v1_DRAFT.md

Bytes: 18074

1: # PG REGION CAPTURE SPEC v1 — Shift+F12 region screenshot
3: **Status:** SPEC LOCKED 2026-04-24. Awaiting Phase 1 implementation.
6: **Touches:** `panda_gallery.py` (shortcut wiring + menu entry), new `region_capture.py` module, `instruction_pane.py` (`_active_step_n` getter + `step_state_changed` fire on manual_screenshots write), `workflow_capture.py` (cursor-toggle integration; recording-session integration deferred), `results_writer.py` (new `append_manual_screenshot` + `remove_manual_screenshot`), `TESTING_SECTION_SPEC.md` (manual_screenshots schema reference if not already covering manual region captures)
10: ## Goal
14: Modeled on Win+Shift+S (drag-with-dimmed-overlay + see-through cutout + drag-to-release-to-capture) with an inline review affordance via toast notification. Annotation deferred — out of scope for v1.
16: ## Hotkey (LOCKED)
22: ## Cursor visibility (LOCKED — addition #5)
26: ## Interaction flow
28: ### State 1 — Idle (default)
32: ### State 2 — Region selection (Shift+F12 pressed)
34: 1. Translucent dark overlay paints on the screen containing the cursor at the moment Shift+F12 fires (LOCKED: cursor's display only — see "Multi-monitor" below). Overlay opacity ~70% (matches Win+Shift+S baseline). Overlay is its own top-level Qt widget with `Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool` and `WA_TranslucentBackground`.
47: ### State 2.5 — Re-trigger guard (LOCKED — addition #3)
51: ### State 3 — Capture (mouse release after drag)
63: **Failure path (LOCKED — addition #4):**
70: ### State 4 — Review (toast clicked, optional)
72: LOCKED: Toast click is the ONLY path to the review dialog. No "Review last capture" View menu entry.
80: ### State 4.1 — Discard cleanup (LOCKED — addition #1)
89: ### State 4.2 — Toast race (LOCKED — addition #2)
95: ## File path policy
97: ### Active session (Ctrl+Alt+R running OR Instruction Pane has a current step)
103: LOCKED: After `append_manual_screenshot`, fire `step_state_changed` on the pane so desktop Claude auto-reads new screenshots mid-step. Same auto-read mechanism as today; the `manual_screenshots` arrival is treated as a state change.
105: ### No active session
111: ## Wiring
113: ### `panda_gallery.py`
119: ### New module `region_capture.py`
129: ### `instruction_pane.py`
137: ### `workflow_capture.py`
139: If a recording session is active (`_recording=True`), the captured PNG is appended to the session's frame list (via existing frame-add path) so the region capture appears in the session timeline alongside F12 frames. **Deferred for v1** — if scope creep, defer. Default v1: region captures bypass `workflow_capture.frame-add` and go directly to `manual_screenshots` only.
143: ### `results_writer.py`
159: ## Multi-monitor (LOCKED)
163: v1.1 (deferred): all-display overlay + cross-monitor regions. File a follow-up; do not block v1.
165: ## Edge cases
179: ## Out of scope for v1
191: ## Acceptance criteria
210: ## Scope estimate (revised after additions)
220: ## Implementation order
228: Phase 4: Pane test plan, manual verification (16 acceptance criteria → 7-8 step plan). ~45min.
232: ## Visual-first artifact
244: Future mockup additions deferred (would require v2): error-toast variant, toast-replace animation. The v1 spec text alone is enough to wire these correctly.
246: ## Open questions — RESOLVED
248: 1. **Overlay scope.** LOCKED: cursor's display only.
249: 2. **Review dialog access.** LOCKED: toast click only.
250: 3. **Auto-read trigger.** LOCKED: fire `step_state_changed` after `append_manual_screenshot` AND after `remove_manual_screenshot` (Discard) so Claude reads mid-step.
251: 4. **Discard cleanup.** LOCKED: unlink + remove from JSON + state_changed fire.
252: 5. **Toast race.** LOCKED: replace silently.
253: 6. **Re-trigger guard.** LOCKED: ignore Shift+F12 while overlay is up.
254: 7. **Save failure.** LOCKED: error toast (5s, destructive style, non-clickable).
255: 8. **Cursor visibility.** LOCKED: honor `capture/includeCursor`.
259: ## Next steps

## workflows\design\v4_0\PG_V4_CUSTOMIZATION_PLAN.md

Bytes: 18476

1: # Panda Gallery — User Customization Plan
3: **Status:** Proposal — co-developed during v4.0 Week 1 mockup review
9: ## 0. Philosophy
17: This document separates those clean escape hatches (worth building) from the noisy ones (worth declining). It also proposes a **tiered rollout** — a handful of "invisible" customizations land in v4.0 (state persistence, already infrastructure we have), the bigger ticket items are v4.1+, and a few are deliberately declined or deferred indefinitely.
21: ## 1. The three tiers of customization
23: ### Tier 1 — State persistence (invisible, zero UI surface)
26: ### Tier 2 — Preferences dialog (v4.1 MVP)
29: ### Tier 3 — Deep customization (v4.1 stretch / v4.2)
34: ## 2. Tier 1 — State persistence (v4.0 scope where noted)
45: | Right panel collapsible section state (which subsections are expanded) | v4.0 | Addresses bug #118 / UX §1.6. Already locked in. |
66: ## 3. Tier 2 — Preferences dialog (v4.1 MVP)
70: ### Tab A — General
78: ### Tab B — Library
86: ### Tab C — Editor
97: ### Tab D — Arrangement
105: ### Tab E — Presentation
113: ### Tab F — Appearance
124: ## 4. Tier 3 — Deep customization (v4.2+ territory)
126: These are the dentist-control-freak accommodations. Each has its own UI surface, not just a checkbox in Preferences. **None of these are v4.0 or v4.1 MVP.** Listed roughly in order of likely value.
128: ### 4.1 User-defined adjustment presets
135: ### 4.2 User-defined arrangement templates
139: - Import / export as `.pga` files for sharing between clinicians (PG_V4_MVP_PLAN §9.3 deferred this)
142: ### 4.3 Custom image categories
148: ### 4.4 Custom patient fields
155: ### 4.5 Custom keyboard shortcuts
162: ### 4.6 Custom workspaces
168: ### 4.7 Custom annotation templates / "stamps"
169: - Not a MVP priority but a strong v4.2+ play
174: ### 4.8 Custom export presets
180: ### 4.9 Custom filters (saved library filters)
185: ### 4.10 Custom auto-enhance pipelines
188: - Not MVP. Likely <5% of users. But the ones who want it will really want it.
192: ## 5. Things I am deliberately NOT proposing
204: ## 6. What a "customization-friendly" architecture looks like
208: ### 6.1 Centralized, namespaced settings
215: ### 6.2 Palette as parameterized QSS
218: ### 6.3 Preferences as data, UI generated from it
239: ## 7. Rollout phasing
244: | **v4.1 Alpha** (v4.0 + 4-6 weeks) | Tier 2 Preferences dialog with General / Library / Editor / Arrange / Presentation tabs. Appearance tab deferred. Preferences schema architecture (§6.3). | Medium — ~1 week UI work + 1 week per tab of real settings behavior |
248: | **v5.0 consideration** | Annotation stamps (4.7), custom auto-enhance pipelines (4.10), plugin API (deferred) | Deep work |
252: ## 8. Open questions to resolve before v4.1 planning
264: ## 9. Why this plan respects the MVP hard-gate
272: Everything in Tier 2 and Tier 3 is explicitly deferred to v4.1+. This plan is the **backlog document**, not a scope expansion.

