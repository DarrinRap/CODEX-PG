# LEDGER_CAPTURE_COMPLIANCE_ADDENDUM_v1

Created: 2026-05-02
Owner: Codex
Audience: Claude Code
Source dispatch: CLAUDE-DESKTOP-20260501-183000-CODEX-BUGS150-151-SPEC
Scope: focused addendum for Bugs #150 and #151 after L28 ships

## Purpose

This addendum narrows L28's Ledger Bible compliance work to the Capture screen surfaces that are easiest to miss: Capture-specific action buttons and notification/badge labels. It does not replace `C:\CODEX PG\CODEX Canonical Specs\LEDGER_BIBLE_COMPLIANCE_SPEC_v1.md`; it is a completion checklist for CC after L28's central role taxonomy and notification selectors are in place.

## Sources Read

- `C:\panda-gallery\panda_ledger\capture\capture_screen.py`
- `C:\panda-gallery\panda_ledger\capture\qa_pair_widget.py`
- `C:\panda-gallery\panda_ledger\capture\bible_picker.py`
- `C:\panda-gallery\panda_ledger\capture\snippet_widget.py`
- `C:\panda-gallery\panda_ledger\styles.py`
- `C:\CODEX PG\CODEX Canonical Specs\LEDGER_BIBLE_COMPLIANCE_SPEC_v1.md`
- `C:\panda-gallery\workflows\design\PG_DESIGN_BIBLE_v1.md`

## Bug #150 - Capture action buttons need explicit Bible roles

### Current Finding

`LEDGER_BIBLE_COMPLIANCE_SPEC_v1.md` already defines the central role taxonomy and calls out Capture action buttons in the Button Role Taxonomy section. Current source confirms the Capture buttons generally have object names but no explicit `role` dynamic property assignment. `panda_ledger/styles.py:66-83` still has one generic `QPushButton` selector plus a one-off `QPushButton#capture_lock_button`, so role-specific styling cannot be verified from source.

### Expected Capture Button Role Inventory

| Button | File and lines | Current source state | Expected `role` |
|---|---:|---|---|
| Load staging draft | `panda_ledger/capture/capture_screen.py:154-156` | `QPushButton("Load staging draft...")`, objectName `capture_load_staging`; no role property | `secondary` |
| Discard | `panda_ledger/capture/capture_screen.py:322-325` | objectName `capture_discard_button`; no role property | `destructive` |
| Save draft | `panda_ledger/capture/capture_screen.py:330-335` | objectName `capture_save_draft`; no role property | `secondary` |
| Lock decision | `panda_ledger/capture/capture_screen.py:340-345` | objectName `capture_lock_button`; one-off QSS exists in `styles.py:76-83`; no role property | `primary` |
| Unlock decision | `panda_ledger/capture/capture_screen.py:349-353` | objectName `capture_unlock_button`; no role property | `recovery` |
| Amend | `panda_ledger/capture/capture_screen.py:358-361` | objectName `capture_amend_button`; no role property | `secondary` |
| Supersede | `panda_ledger/capture/capture_screen.py:363-367` | objectName `capture_supersede_button`; no role property | `secondary` |
| Retire | `panda_ledger/capture/capture_screen.py:369-374` | objectName `capture_retire_button`; no role property | `destructive` |
| Related decisions Add | `panda_ledger/capture/capture_screen.py:738-741` | objectName `related_picker_add`; no role property | `utility` or `secondary`; choose `utility` if kept compact beside a combo |
| Add Bible section | `panda_ledger/capture/bible_picker.py:60-62` | objectName `bible_picker_add`; no role property | `secondary` or `utility`; choose `secondary` unless it is styled as a compact picker control |
| Remove Q&A pair | `panda_ledger/capture/qa_pair_widget.py:65-68` | objectName `qa_pair_remove`; no role property; fixed width 24 | `destructive` |
| + Add Q&A pair | `panda_ledger/capture/qa_pair_widget.py:119-122` | objectName `qa_pair_add`; no role property | `secondary` |
| Browse snippet image | `panda_ledger/capture/snippet_widget.py:139-142` | objectName `snippet_paste_browse`; no role property | `utility` |

### Required Change

After L28 adds central selectors in `panda_ledger/styles.py`, assign `button.setProperty("role", "...")` for every button in the table above. Keep the object names for test hooks and any one-off layout targeting, but do not rely on object names alone to imply visual hierarchy. Remove the special `QPushButton#capture_lock_button` styling once `role="primary"` covers the lock button, unless CC documents a narrow one-off exception.

### Acceptance Criteria

- Every Capture action button listed above has an explicit `role` property assignment in source.
- `panda_ledger/styles.py` includes central selectors for the L28 roles: `primary`, `secondary`, `destructive`, `utility`, and `recovery`, including disabled variants.
- No Capture action button depends on default unstyled `QPushButton` appearance for its semantic hierarchy.
- The Capture screen has exactly one visible primary action in the normal draft-loaded state: `Lock decision`.
- Destructive actions (`Discard`, `Retire`, Q&A remove) are visually restrained but semantically distinct from secondary actions.

## Bug #151 - Capture notification and badge labels need Bible-conformant shape treatment

### Current Finding

L28 already calls out `capture_status_banner` in the Notification and Badge Shape Cleanup section. Current source shows the banner and Step 1 feedback label are QLabel notifications with object names and text/level behavior, but the active stylesheet only colors the banner text by level. It does not provide a central semantic notification shape with background, border, radius, padding, and typography.

### Expected Capture Notification Inventory

| Element | File and lines | Current styling gap | Required fix |
|---|---:|---|---|
| Step 1 feedback label | `panda_ledger/capture/capture_screen.py:157-163`; populated by Bug #149 as inline feedback such as `[i] No staging drafts found.` | objectName `capture_step1_feedback`; no dynamic notification role/level shown in construction; needs central notification styling rather than ad hoc inline text treatment | Keep objectName, add a semantic property such as `kind="notification"` and `level="info"` / `warn` / `error` where text is set; style centrally in `styles.py` |
| Capture status banner | `panda_ledger/capture/capture_screen.py:309-313`, `662-671` | objectName `capture_status_banner`; `_show_banner()` sets `level`, but `styles.py:84-86` only maps level to text color | Convert to central notification selector with background, border, radius, padding, and typography; retain `level` property and repolish cycle |
| Capture statusbar widget | `panda_ledger/capture/capture_screen.py:378-382`, implementation in `_capture_widgets.py` covered by L28 | Structural status surface, not a pill; covered by L28 local-QSS migration | Cross-check after L28 that it is a rectangular status surface, not a pill/badge, and uses central selectors |
| Related/Bible/Q&A helper add/remove micro-controls | `capture_screen.py:738-741`, `bible_picker.py:60-62`, `qa_pair_widget.py:65-68`, `119-122` | These are actions, not badges. Risk is styling them as pill-like chips. | Style through button roles from Bug #150; keep rectangular action-button shape |

### Required Change

Implement a central notification/badge selector set in `panda_ledger/styles.py` as part of L28, then wire Capture labels to it:

- Use stable object names plus dynamic properties, for example `kind="notification"` and `level="info" | "ok" | "warn" | "error"`.
- Use Bible radius values only. For notification banners, use a low-radius rectangle such as 4px unless a true informational pill is explicitly desired by the Bible section.
- Use central color tokens. Do not put raw hex or widget-local QSS in `capture_screen.py`.
- Preserve the existing `_show_banner()` repolish cycle for dynamic `level` updates.
- The Step 1 inline feedback label should be visually informational and passive. It must not look like an action button.

### Acceptance Criteria

- `capture_step1_feedback` and `capture_status_banner` both render via central `styles.py` selectors, not widget-local QSS.
- Notification labels have Bible-conformant padding, border/background, radius, color tokens, and typography.
- The status banner still changes semantic color based on `level`.
- The Step 1 feedback text is passive notification styling, not a clickable pill or button-like control.
- No Capture widget file contains raw color hex or local QSS for these notification elements.

## Handoff Note For CC

Run L28 first. Then use this addendum as the Capture-specific completeness checklist before reporting Bugs #150/#151 resolved.
