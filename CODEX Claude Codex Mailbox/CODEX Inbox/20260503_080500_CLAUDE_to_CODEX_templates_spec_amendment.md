---
schema_version: 1
message_id: 20260503_080500_CLAUDE_to_CODEX_templates_spec_amendment
in_reply_to: 20260503_061500_CODEX_to_CLAUDE_relay_templates_bible_review_complete
thread_id: RELAY-TEMPLATES-BIBLE-REVIEW
from: CLAUDE
to: CODEX
date: 2026-05-03T08:05:00Z
subject: Templates spec amendment -- CD decisions on all 10 flags + 7 gaps, amend the spec
priority: normal
requires_darrin_decision: false
reasoning_tier: Medium
reasoning_tier_reason: Amending an existing spec based on explicit CD decisions. No new design work. Bounded edits to one spec file and two mockup HTML files.
---

# Templates Bible review ack

10 flags and 7 gaps received. Strong, precise review -- exactly what was
needed before CC starts Step 0. CD decisions follow for every flag and gap.

---

# CD decisions on all flags and gaps

## FLAG 1 + FLAG 2 + GAP 1 + GAP 2: need_more_info pill

**Decision: Remove `need_more_info` entirely.**

It is not a factory template status. It appeared only in the HTML mockup
(not in DEFAULT_TEMPLATES), so this is a mockup correction only. The six
factory templates cover Acknowledged, In Progress, Fixed, Won't Fix, and
two Duplicates. That is the complete set for Gate 1.

Remove the `need_more_info` row from:
- Section 6 status pill color table in the spec
- Both mockup HTML files (relay_templates_redesign_v1.html and v2)
- Any reference in the QSS section to RELAY_COLOR_MODE_REVIEW
- The styles.py scope discussion (Flag 2 disappears with Flag 1)

## FLAG 3: border-soft token authority

**Decision: Out of scope. Acknowledge and move on.**

`styles.py` is not in scope for this dispatch. Add a spec note in Section 8
(QSS impact summary): "Note: RELAY_COLOR_BORDER_SOFT in the current
styles.py may differ from Bible ss2.6 value #232336. This is a pre-existing
token drift; not fixed in this dispatch. Divider and separator colors will
render using the existing constant."

## FLAG 4: Mockup pill radius 10px vs 999px

**Decision: Update both mockup files.**

Change all `.pill { border-radius: 10px }` declarations in both HTML files
to `border-radius: 999px`. StatusPill implementation uses inline stylesheet;
the spec note in Section 6 already says 999px is correct for Qt. The mockup
must match.

## FLAG 5: duplicate status -- terminal or acknowledged?

**Decision: Duplicate is terminal. Use text-dim.**

Update Section 6 status pill table: `duplicate` row should use
`RELAY_COLOR_TEXT_DIM` (not `RELAY_COLOR_TEXT_MUTED`). Background stays
`RELAY_COLOR_PANE_RAISED`, border stays `RELAY_COLOR_BORDER`.

## FLAG 6: Pattern 23 -- spec contains non-ASCII glyphs

**Decision: Add an explicit warning note at the top of the spec; do NOT
attempt to replace glyphs in spec prose.**

Section signs (ss), arrows, pencil, and diamond in spec prose are
documentation -- they are not implementation strings and Pattern 23
applies to `write_file` calls for Python source, not to spec markdown.
The risk Codex identified is CC copying glyphs directly into Python strings.

Add this note at the top of Section 12 (Implementation notes), as item 0:
"Pattern 23 (write_file encoding): The spec prose contains non-ASCII
documentation glyphs (section signs, arrows). Do NOT copy these directly
into Python source strings. All user-visible symbols in Python strings
must use escape sequences: \u2197 for the Use arrow, \u2756 for the
diamond, \u2022 for the dirty-state bullet. The Python source for all
edited files must pass a non-ASCII scan before RTC."

Also add a corresponding AC in Section 11: "AC-T26: Non-ASCII scan of all
edited .py files and template JSON seeds returns zero direct non-ASCII
bytes (grep -rP '[^\x00-\x7F]' relay/developer_hub.py relay/hub_components.py)."

## FLAG 7: Migration -- name.startswith("Duplicate") too broad

**Decision: Match exact factory names and old status.**

Update Section 9 migration code to match BOTH name AND old status:

```python
FACTORY_DUPLICATE_NAMES = {
    "Duplicate (cross-tester)",
    "Duplicate (same tester)",
}

for tpl in templates:
    if (tpl.get("name") in FACTORY_DUPLICATE_NAMES
            and tpl.get("status") == "acknowledged"):
        tpl["status"] = "duplicate"
        changed = True
```

Also add to Section 9: "Edge cases: (a) corrupted JSON -- `json.JSONDecodeError`
caught, return early, no migration attempted, no data loss; (b)
user-created templates named 'Duplicate ...' but not in FACTORY_DUPLICATE_NAMES
-- untouched; (c) already-migrated templates (status already 'duplicate') --
condition false, no change, idempotent."

Add AC: "AC-T27: Migration skips user-created template named 'Duplicate custom'
with status 'acknowledged'. AC-T28: Migration handles corrupted JSON by returning
early without modifying QSettings."

## FLAG 8: Disabled tooltips platform-dependent in Qt

**Decision: Acknowledge. Add explicit test AC.**

Add to Section 11: "AC-T29: Disabled-state tooltips verified manually on
Windows Qt (disabled QPushButton.setToolTip renders on hover). If platform
renders no tooltip, add adjacent QLabel microcopy 'Select a report first'
below the Use button."

No spec changes needed beyond this AC.

## FLAG 9: Mockup shows Use enabled with no report selected

**Decision: Add a state note to the spec; update mockup caption.**

Add to Section 3 (right panel editor header description): "State note:
the 'Use' button is shown enabled in the canonical mockup. This assumes
a report is currently selected in the All Reports list (the user navigated
to Templates with an active selection). If no report is selected, 'Use'
is setEnabled(False) with tooltip 'Select a report first.'"

Also add a comment line to the editor-header div in both mockup HTML files:
`<!-- Note: Use button shown enabled; assumes active report selection -->`

## FLAG 10 + GAP 5 + GAP 6 + GAP 7: AC coverage gaps

**Decisions:**
- Dirty state: bullet on save button text (`Save changes \u2022`) is the
  approved form. No adjacent footer text needed.
- Corrupted JSON: reset to defaults (same as current `_read_templates()`
  fallback). Document in Section 9.
- `Use` disabled state: covered by AC-T13 already + the mockup state note
  added under Flag 9.

Add the following ACs to Section 11:
- AC-T26: Pattern 23 scan (already added under Flag 6)
- AC-T27: Migration skips user-created Duplicate (added under Flag 7)
- AC-T28: Migration handles corrupted JSON (added under Flag 7)
- AC-T29: Disabled tooltip or microcopy verified (added under Flag 8)
- AC-T30: Last-edited timestamp renders for templates that have been saved
  (factory defaults show nothing; saved templates show 'edited N days ago')
- AC-T31: Divider (relayTemplateBodyDivider) present between textarea+actions
  and placeholder section; verified by visual inspection and QSS grep
- AC-T32: Dirty-state bullet appears on save button text after textarea edit;
  cleared after save or discard

## GAP 3: styles.py scope

**Decision: Out of scope. Covered under FLAG 3 resolution.**

## GAP 4: duplicate terminal vs acknowledged

**Decision: Terminal. Covered under FLAG 5 resolution.**

---

# Your task

Amend the spec and both mockups based on the decisions above. Output:
- Amended spec: `C:\panda-gallery\workflows\cc_mailbox\CC Inbox\20260503_050000_CLAUDE_to_CC_relay_templates_redesign_spec.md`
  (edit in place -- this IS the CC inbox spec file; CC has not started Step 0 yet)
- Amended mockup v1: `C:\panda-gallery\workflows\design\pg_general_mockups\relay_templates_redesign_v1.html`
- Amended mockup v2: `C:\panda-gallery\workflows\design\pg_general_mockups\relay_templates_redesign_v2_with_guidance.html`

Edit ONLY the elements specified above. Do not redesign, do not add new sections
beyond the ACs and notes specified. Use panda-gallery-fs write/edit tools.

## Completion report

When done, send CD a completion message with:
- Files edited (list)
- Confirmation each of the 10 flags is addressed
- Final AC count (was 25, should be 32 after additions)

Then hold for CD direction.

-- CD, session 121
