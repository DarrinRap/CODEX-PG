---
schema_version: 1
message_id: 20260514_180700_CLAUDE_to_CODEX_archived_thumbnail_spec
in_reply_to: null
thread_id: PG-SPEC-ARCHIVED-THUMBNAIL
from: CLAUDE
to: CODEX
date: 2026-05-14T18:07:00-07:00
subject: DISPATCH — add archived thumbnail treatment to Bible + Principia
priority: normal
type: dispatch
reasoning_tier: high
status: active
approval_boundary: hold_for_commit_go
---

# Add Archived Thumbnail Treatment to Bible + Principia

CD ruling (s178) replaced the previous `#aa4444` red tint on archived/
deleted thumbnails with a gray-wash + badge treatment. This ruling must
be captured as a canonical P-rule in Principia and a Bible entry.

## Ruling summary

Archived/deleted image thumbnails in the Library grid use:

1. **Gray overlay**: semi-transparent black wash over the full thumbnail
   bounds — `QColor(0, 0, 0, 140)` (~55% opacity). Applied in
   `ImageThumbnail.paintEvent` after drawing the source image.
2. **"ARCHIVED" text badge**: centered on thumbnail.
   - Text: `ARCHIVED`
   - Font: Cascadia Mono (monospace fallback), 9px, weight 600
   - Color: `#888888` (palette token `text_muted`)
   - No background fill — text over the washed image directly
3. **`#aa4444` red tint: removed entirely.** Red is reserved for
   errors and danger states. Archived = inactive/historical, not
   dangerous.

## Rationale (for spec prose)

Red creates alarm-fatigue risk in clinical workflows. Gray-wash +
badge is the industry-standard "inactive" treatment (used by Lightroom,
Capture One, Romexis, and virtually all medical imaging platforms).
Archived images are safely stored — not erroneous.

## Task A — PG_DESIGN_BIBLE_v1.md

Find the appropriate section for Library thumbnail states or image
display rules (likely §Library, §ImageThumbnail, or §Archived states).
If no archived-state section exists, add one.

Add a rule along these lines (rewrite in Bible prose style):

> **Archived thumbnail treatment.** When an image or series is marked
> archived, `ImageThumbnail.paintEvent` renders a `QColor(0,0,0,140)`
> overlay over the full thumbnail rect, followed by an `ARCHIVED` text
> badge centered at 9px Cascadia Mono weight 600 in `text_muted`
> (`#888888`). No background fill on the badge. The former `#aa4444`
> red pen tint is removed — red is reserved for errors and danger
> states. This treatment matches the industry standard for
> inactive/historical content in clinical imaging platforms.

## Task B — PG_PRINCIPIA_v1.md

Add a new P-rule in the appropriate section (Library image grid,
thumbnail states, or a new Archived States subsection). Assign the
next available P-rule number after P-322.

Rule content (adapt to Principia format):

> **P-NNN — Archived thumbnail: gray-wash + badge, not red.**
> `ImageThumbnail.paintEvent` on archived/deleted images: (1) draw
> source image; (2) paint `QColor(0,0,0,140)` rect over full bounds;
> (3) draw `ARCHIVED` centered, 9px Cascadia Mono 600,
> `text_muted #888888`, no fill. Former `#aa4444` tint: removed.
> Source: s178 CD ruling. Mockup authority: v3 (when rendered).

## Task C — pg_design_spec.json

Also add `viewport_pane: "#111118"` to the palette section. This is a
companion ruling from the same s178 Phase 1.1 session — the Library
viewport background color gets a proper palette name.

## Commit

Single atomic commit covering all three files:

```
docs: add archived thumbnail gray-wash+badge rule to Bible + Principia (P-NNN); add viewport_pane #111118 palette token
```

Run `pg_spec_freshness.py --update` before committing to refresh
Bible hash.

Report SHA to CLAUDE Inbox when pushed. No commit-go issued here —
file ship-ready first.

— CD
