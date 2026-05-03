---
schema_version: 1
id: CLAUDE-DESKTOP-20260502-010000-BA-FAILURE-DB-AUDIT
thread_id: BA-FAILURE-DB-AUDIT
from: claude_desktop
to: codex
type: dispatch
priority: normal
status: open
thread_status: active
action_owner: codex
requires_darrin_decision: false
reasoning_tier: Medium
---

# Codex dispatch: Bible Audit applet — accurate per-app FAILURE_DB + WARN_DB

## Background

The Bible Audit applet (`workflows/design/applets/PG_Design_Bible_Audit_v1.html`)
now has per-app score profiles and a structured rich report format (FAILURE_DB /
WARN_DB). The current data in those databases is **placeholder** — I wrote
representative-sounding entries to define the schema, but they are not verified
against actual source code.

This dispatch asks Codex to do a **read-only audit pass** across each PG app's
source files and produce accurate, verified replacement data for FAILURE_DB and
WARN_DB.

## Scope

Audit the following apps against PG Design Bible v1.4:

| App | Primary source path |
|---|---|
| Panda Gallery | `panda_gallery/` |
| PG Design Ledger | `panda_ledger/` |
| Relay Wizard | Look in `panda_relay/` if it exists; otherwise note as not-yet-implemented |
| PANDA Vellum | `panda_vellum/` if exists |
| PANDA Collaborator | `panda_collab/` if exists |
| Clip Launcher | `scripts/pg_clip_launcher.py` |
| Audit Module | `panda_gallery/` audit_module screens |
| Bible Applets | `workflows/design/applets/` |

For apps that don't exist as source yet (Relay Wizard, PANDA Vellum, PANDA
Collaborator), note "not yet implemented — scores estimated" and produce
empty arrays `[]` for their FAILURE_DB and WARN_DB entries.

## What to audit

For each app, scan for violations of these Bible rules (the ones most commonly
violated in PySide6 Qt apps):

- **§2.1** Surface scale: wrong background level on containers
- **§2.4** Accent-soft misuse (full accent where soft required)
- **§2.9** Hardcoded color literals in QSS strings (grep for `#[0-9a-fA-F]{3,6}` in setStyleSheet calls)
- **§3.3** Section head: wrong size / weight / spacing / transform
- **§3.4** Mono font: font-ui on precision data (filenames, dates, IDs, versions)
- **§4.1** Off-scale spacing values
- **§4.2** Wrong border-radius (buttons 4px, chips 12px, pills 8px, badges 3px)
- **§4.3** Wrong transition timing (only 0.15s / 0.4s / 1.5s allowed)
- **§6.12** Button hierarchy: multiple primaries, wrong hover state, wrong height (28px)
- **§6.14** Chip active state: full accent fill instead of accent-soft
- **§6.17** Status bar: missing border-top or wrong height (26px)
- **§6.21** Stepper: wrong indicator size, rail width, or connector color
- **§1.5/§1.6** Progressive disclosure: disabled instead of hidden, or action shown in wrong state
- **§10 #4** More than one primary button per screen

## Output format required

Produce a JSON file at:
`C:\CODEX PG\CODEX Canonical Specs\BA_FAILURE_DB_v1.json`

Schema:
```json
{
  "generated": "ISO datetime",
  "bible_version": "PG Design Bible v1.4",
  "note": "Verified against source code by Codex read-only audit pass",
  "FAILURE_DB": {
    "Panda Gallery": [
      {
        "id": "FAIL-PG-001",
        "rule": "§2.9",
        "description": "plain English — what is wrong",
        "bibleRef": "§2.9: exact rule text",
        "fixTarget": "relative/file/path.py — specific class or method or QSS selector",
        "ccAction": "one-line implementation instruction for CC",
        "codexNote": "None OR design question / spec gap note"
      }
    ]
  },
  "WARN_DB": {
    "Panda Gallery": []
  }
}
```

Rules for entries:
- Only include **verified** violations — things you can point to with a file + line number
- `fixTarget` must name the actual file and the specific thing (class name, method, QSS string location)
- `ccAction` must be a concrete one-liner CC can act on without reading the spec
- `codexNote` is only populated if there's a genuine spec ambiguity or design decision needed; otherwise "None"
- IDs: FAIL-[APP_PREFIX]-[NNN] and WARN-[APP_PREFIX]-[NNN], zero-padded 3 digits
- App prefixes: PG (Panda Gallery), LD (Ledger), RW (Relay), VL (Vellum), PC (Collaborator), CL (Clip), AM (Audit Module), BA (Bible Applets)

## Scores

Also update the per-app score profiles — produce a second JSON section:
```json
"APP_PROFILES": {
  "Panda Gallery": { "pass": N, "fail": N, "warn": N }
}
```

Counts must be consistent: pass + fail + warn should equal 64 (the total check count).

## Acceptance criteria

- JSON is valid (parseable)
- Every FAILURE_DB entry has a real file path that exists in the repo
- Every FAIL entry has a corresponding score entry where fail > 0
- Apps not yet implemented have empty arrays and a note
- Deliverable at `C:\CODEX PG\CODEX Canonical Specs\BA_FAILURE_DB_v1.json`

## On completion

Report to CD with:
1. Summary table: app name / failures found / warnings found / verified?
2. Any apps where source doesn't exist (mark estimated)
3. Any spec gaps you found during the audit (note for Bible amendment)
4. Path to deliverable JSON

Then ask CD for next direction.

— CD
