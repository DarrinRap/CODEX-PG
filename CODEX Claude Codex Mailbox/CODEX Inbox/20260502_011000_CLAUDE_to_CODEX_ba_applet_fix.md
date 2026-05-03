---
schema_version: 1
id: CLAUDE-DESKTOP-20260502-011000-BA-APPLET-FIX
thread_id: BA-APPLET-FIX
from: claude_desktop
to: codex
type: dispatch
priority: high
status: open
thread_status: active
action_owner: codex
requires_darrin_decision: false
reasoning_tier: Medium
---

# Codex dispatch: BA applet — fix copy-report button conflict + consolidate scripts

## Background

The Bible Audit applet (`C:\panda-gallery\workflows\design\applets\PG_Design_Bible_Audit_v1.html`)
has accumulated multiple `<script>` blocks appended over several sessions due to
CRLF encoding issues preventing in-place edits. This has caused a conflict:
multiple `addEventListener('click', ...)` calls on `#copy-report-btn`, where
the FIRST handler (old plain report) fires and the LAST handler (new rich report)
is ignored.

Symptom: Copy Report produces the old plain format instead of the new structured
FAIL/WARN/PASS format with CC action, Bible ref, and fix target fields.

## Task

Rewrite the file cleanly. You have full write access to the applet path.
Do NOT use edit_file — use write_file to produce a clean single output.

## What to preserve (do not change)

1. All HTML structure (tabs, panels, score-grid, modal, app-scope controls)
2. All CSS (`:root` variables, all class styles)
3. All audit check definitions (`check(...)` calls)
4. The per-tab check arrays (`badge-checks`, `pill-checks`, etc.)
5. The tab-switching, stepper-building, gap-table JS
6. `renderAppScopeControls()` and app-scope state management
7. `APP_PROFILES` and `renderScores()` dynamic score logic
8. `buildRichReport()` and `applyRichToModal()` — the rich report format
9. `FAILURE_DB` and `WARN_DB` data (keep placeholder data for now — Codex will
   update with real data in a separate audit dispatch)
10. The `Audit Results` tab divider style (border-right, margin-right, padding-right)

## What to fix / consolidate

### Fix 1 — Single copy-report-btn handler

Remove ALL existing `addEventListener` calls on `#copy-report-btn` and replace
with ONE handler that calls `buildRichReport()`:

```javascript
document.getElementById('copy-report-btn').addEventListener('click', function() {
  var btn = this;
  var text = buildRichReport();
  var ta = document.createElement('textarea');
  ta.value = text;
  ta.setAttribute('readonly', '');
  ta.style.cssText = 'position:fixed;top:-9999px;left:-9999px';
  document.body.appendChild(ta);
  ta.focus();
  ta.select();
  var ok = false;
  try { ok = document.execCommand('copy'); } catch(e) {}
  document.body.removeChild(ta);
  if (ok) {
    btn.textContent = '\u2713 Copied';
    btn.style.background = 'var(--ok)';
    btn.style.borderColor = 'var(--ok)';
    btn.style.color = '#1a1a2e';
    window.setTimeout(function() {
      btn.textContent = 'Copy Report';
      activateCopyReady();
    }, 1600);
    var st = document.getElementById('copy-report-status');
    if (st) {
      st.textContent = '\u2713 Rich report copied \u2014 paste into CC/Codex dispatch';
      st.style.color = 'var(--ok)';
      st.style.display = 'inline';
      window.clearTimeout(st._t);
      st._t = window.setTimeout(function() { st.style.display = 'none'; }, 4000);
    }
  }
});
```

### Fix 2 — Single view-report-btn handler

One handler only, calling `applyRichToModal(buildRichReport())`.

### Fix 3 — Single score-grid click handler

One handler only, calling `showScoreDetails(kind)`.

### Fix 4 — Remove inline-report-sec HTML section

Remove the `<div class="sec" id="inline-report-sec" ...>` section entirely —
this was the old inline scroll approach, replaced by the modal.
Also remove `renderInlineReport()` function entirely.

### Fix 5 — Remove old static score-grid.innerHTML block

The original score-grid render block (before `getScoreItems` / `getScoreMeta`
functions) wrote static numbers. Remove the innerHTML assignment and
the static fill/progress-label lines — `renderScores()` handles all of this.
Keep the `var passes / fails / warns / total / pct` variable declarations
(they're still used by `getScoreMeta` and `buildAuditReport`).

### Fix 6 — Single consolidated `<script>` block

Produce exactly ONE `<script>` block in the output. No appended blocks.
Order within the script:
1. App state management (localStorage, appNames, selectedAppScope)
2. `renderAppScopeControls()`
3. `escapeHtml()`
4. Audit engine: `results`, `check()`, `lum()`, `contrast()`
5. All `check(...)` calls
6. Variable declarations: `passes`, `fails`, `warns`, `total`, `pct`
7. `getScoreItems()`, `getScoreMeta()`
8. `buildAuditReport()` (keep — used internally by modal score-card filter views)
9. `showCopyStatus()`, `doCopy()`
10. `APP_PROFILES`, `getAppProfile()`, `renderScores()`
11. `FAILURE_DB`, `WARN_DB`
12. `buildRichReport()`, `applyRichToModal()`
13. `activateCopyReady()`
14. `showScoreDetails()`, `closeScoreDetails()`
15. All event listeners (one per button/control — no duplicates)
16. `renderAppScopeControls()` initial call
17. `renderChecks()` + all per-tab check arrays
18. Type scale, gap token table, stepper builders
19. Tab switching
20. `renderScores()` initial call

## Acceptance

- File is valid HTML with one `<script>` block
- Copy Report button produces the rich structured format (FAIL-XXX entries
  with Problem / Bible ref / Fix target / CC action / Codex note fields)
- View Report button opens modal with same rich content, colored correctly
- Score cards update dynamically when app chip is clicked (no page scroll)
- Copy Report button is muted/grey until an app is selected, then turns peach
- Modal Copy button works
- No JS errors in console

## Deliverable

Overwrite `C:\panda-gallery\workflows\design\applets\PG_Design_Bible_Audit_v1.html`
with the clean consolidated version.

Report to CD on completion with:
1. Confirmation of fix
2. Line count of output file
3. Any issues encountered

Then ask CD for next direction.

— CD
