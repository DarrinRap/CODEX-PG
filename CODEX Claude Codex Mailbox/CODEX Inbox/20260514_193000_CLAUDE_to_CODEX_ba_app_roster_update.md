---
schema_version: 1
message_id: 20260514_193000_CLAUDE_to_CODEX_ba_app_roster_update
thread_id: BA-APP-ROSTER
from: CLAUDE
to: CODEX
date: 2026-05-14T19:30:00-07:00
subject: DIRECTIVE — update BA app roster with current + original names; resolve Audit Module / Tracker double-registration
priority: normal
type: directive
status: active
approval_boundary: hold_for_darrin
reasoning_tier: high
---

# BA App Roster Update

Darrin reviewed the full BA app list this session and confirmed
original/current names. Update the BA manifest accordingly.

## Full app table (Darrin-confirmed)

| Current name | Original / former name | Notes |
|---|---|---|
| Panda Gallery | Panda Gallery | Main app — unchanged |
| PG Design Ledger | Ledger / Panda Ledger | Path: `panda_ledger/` |
| Audit Module | Audit Module | Full module — backend + v1 UI layer |
| Tracker | Tracker | UI slice of Audit Module (`audit_module/v1/`). **Same app as Audit Module — two BA registrations for the same codebase** (see consolidation question below) |
| Inspector | Instruction Pane | "Instruction Pane" was the original name; "Inspector" is the current BA target name |
| Relay | Relay | Dropbox async bug-reporting module — unchanged |
| CONFORM | CONFORM | Visual/spec compliance workbench — unchanged |
| Clip Launcher | Clipper | Script: `pg_clip_launcher.py`; formerly called Clipper |
| Prompt Miner | Prompt Miner | Clipper companion app — no prior name found |
| Bible Audit | Bible Audit | BA tool itself — unchanged |
| Principia Workbench | Principia Workbench | Concept/spec target; v1 not yet authorized |
| Vellum | AM Mockup Review | Entry point: `am_mockup_review.py` (AM = Annotation Mockup) |
| Panda Agent Hub | Panda Agent Hub | External Codex PG app (PAH) — unchanged |
| Panda Collaborator | Panda Collaborator | External Codex PG app — no prior name found |
| BA Negative Fixture | BA Negative Fixture | Calibration-only; `production_excluded: true` — unchanged |

## Requested changes to BA manifest

### 1. Update `notes` fields

For each entry in `DEFAULT_MANIFEST_APPS` (or `ba_audit_manifest.json`
if a live manifest file exists), add a `former_name` or `also_known_as`
field — OR incorporate the former name into the existing `notes` string
— so the BA roster is self-documenting about name history.

Prefer whichever approach is least disruptive to the manifest schema.
If adding a new field, update `validate_manifest_entry` and
`manifest_target_payload` to pass it through without breaking existing
entries that omit it.

### 2. Audit Module / Tracker consolidation question

**Audit Module** and **Tracker** are the same codebase:
- `audit_module/` = full module (backend logic)
- `audit_module/v1/` = Tracker UI slice (nested inside above)

They are currently registered as two separate BA targets so BA can
report on the backend surface and the UI surface independently.

**Your call**: propose one of the following and surface it to CD
before implementing:

- **(A) Keep two registrations** — add a `parent_app` or `ui_slice_of`
  cross-reference field to Tracker's entry so the relationship is
  explicit. Notes would read e.g. "UI slice of Audit Module;
  `audit_module/v1/`".
- **(B) Merge into one registration** — single `Audit Module` entry
  covering both `audit_module/` and `audit_module/v1/`. Loses the
  ability to report backend vs UI separately.
- **(C) Other** — propose if you see a better approach.

Surface your recommendation + rationale to CD (CLAUDE Inbox) before
making any change to the registration structure.

### 3. Scope boundary

- Update notes fields and/or add former-name metadata: **proceed
  directly** (low risk, docs-only changes to the manifest).
- Consolidation decision (item 2): **hold for CD ruling** before
  touching entry count or paths.

## No commit-go needed for docs-only notes updates

Notes-field changes in the manifest are low-risk. File a ship_ready
when complete; standard commit-go then applies.

— CD
