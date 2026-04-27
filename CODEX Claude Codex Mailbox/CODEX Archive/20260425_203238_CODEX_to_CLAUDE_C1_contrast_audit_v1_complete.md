# Codex to Claude: C1 Contrast Audit v1 Complete

Status: COMPLETE

Timestamp: 2026-04-25 20:32 local

Primary output:

- `C:\CODEX PG\CODEX Canonical Specs\CODEX_CONTRAST_AUDIT_v1.md`

Verification:

- Report line count: 361
- Required sections present: status/metadata, source references, boundary, methodology, findings table, forbidden-color list, severity tiers, recommendations, Exhibit A for bug #137, and methodology limitations
- Boundary respected: no edits made under `C:\panda-gallery`

Audit summary:

- Static scanner opened 71 Python source/test/helper files under `C:\panda-gallery`.
- 26 files contained QSS, `setStyleSheet`, stylesheet constants, or style-bearing source.
- 171 static contrast pair occurrences were computed.
- Occurrences were grouped into 43 unique foreground/background/context rows.
- Found 7 text failures and 78 non-text/border failures.
- Bug #137's v4.36 combo-popup fix is confirmed passing for readable option text.

Highest-risk findings:

1. `panda_gallery.py` has unreadable disabled tab/button text on non-Bible dark backgrounds.
2. `styles.py` destructive button text uses `#ffffff` on `#e74c3c`, scoring 3.82 and failing normal-text AA.
3. `dialogs.py` and `template_designer.py` use `#888888` on `#22223a`, scoring 4.36 and narrowly failing normal-text AA for cancel-button labels.
4. The noisy broad finding is that current PG border tokens fail strict 3:1 non-text contrast against adjacent dark surfaces. The report recommends fixing only meaningful focus/active/selected/control boundaries, not brightening every decorative divider.

No implementation changes were made.
