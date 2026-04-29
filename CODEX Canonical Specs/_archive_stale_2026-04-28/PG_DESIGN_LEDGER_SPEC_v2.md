# PG Design Ledger — System Spec v2 (DRAFT FOR REVIEW)

**Status:** DRAFT v2 — supersedes v1. Pending Codex and CC review before build dispatch.
**Authored:** 2026-04-28
**Author:** Desktop Claude (with Darrin)
**Supersedes:** `PG_DESIGN_LEDGER_SPEC_v1.md` (architectural rewrite — applets → native Python app).
**Purpose:** Authoritative specification for the PG Design Ledger system — a Python desktop application that captures, enforces, and verifies design decisions across the PG codebase.

---

## Changelog from v1

The v1 draft proposed a system of three browser-based HTML applets sharing a JSON spec file. Self-review identified a critical architectural flaw: the Filesystem MCP is Claude Desktop's tool, not the browser's tool. Static HTML files opened via `file://` cannot reliably read or write disk. Persistence, search, snapshot capture, file scanning, decision linking — every core feature hit that wall.

v2 resolves this by making the Ledger a **native PySide6 desktop application** that runs alongside PG (or standalone). Direct filesystem access. Imports `pg_design_lint` in-process. Reuses PG's existing dark theme, palette tokens, dialog widgets, QSS. Talks to a running PG instance via a small IPC channel for live introspection.

Other fixes from v1 self-review now incorporated:

- **Legacy backlog policy** explicitly defined (§4.10)
- **Score formula** normalized by lines of code (§7.5)
- **Amendment vs supersession** distinction added (§3.5)
- **Bible/JSON sync ownership** assigned to a generated workflow (§2.3)
- **Test assertions** disambiguated — separate human-readable + machine-runnable (§3.4)
- **Scope cuts** — snapshots, score dashboard, trace path view, three index files all moved to v2-future (§9)
- **Persistence architecture** resolved by native app (Python file I/O)
- **Naming** — "snippet" vs "snapshot" overlap resolved (§1)
- **Decision ID padding** — fixed at 4 digits, supports up to 9999 (§3.2)
- **Authors field** validated against allowlist (§3.2)
- **Spec.json freshness check** added (§2.3)

---

## 0 — Executive summary

### 0.1 — The problem

Design refinement sessions take real time. The chain from Q&A → spec → mockup → dispatch → CC implementation → CC report → commit has many failure points. A48's missing `✦ Triage with AI` button on 2026-04-28 is the worked example: a decision implicit in a layout-hierarchy diagram was lost in dispatch translation; CC built every explicit thing and missed the implicit one.

Four root causes:

1. Decisions live in many places (Bible, specs, mockups, dispatches, code comments, chat history) with no single index
2. Implicit decisions are routinely lost in translation; only explicit numbered acceptance criteria reliably ship
3. No automatic enforcement — only manual review at the end of the chain, when fixes are most expensive
4. No durable, searchable record across sessions

### 0.2 — The system

**PG Design Ledger** (`panda_ledger/`) is a Python desktop application with three integrated workflows plus a companion lint tool:

| Workflow / tool | What it does | Where it lives |
|---|---|---|
| **Capture** (in-app tab) | Q&A authoring with structured snippet, writes decision markdown | `panda_ledger/capture/` |
| **Verify** (in-app tab) | Per-state checklist + Bible reference + manual sign-off gate | `panda_ledger/verify/` |
| **Browse** (in-app tab) | Searchable list of all decisions, read-only detail view | `panda_ledger/browse/` |
| **Lint** (CLI + in-app) | Static analysis on `.py` files, blocks bad commits | `pg_design_lint/` (separate package, importable) |

All four read from a shared spec file `workflows/design/pg_design_spec.json` derived from `PG_DESIGN_BIBLE_v1.md`. The Ledger app itself is built using PG's design language (dark theme, peach accent, Bible tokens) — eating its own dog food.

### 0.3 — Why one app instead of three tools

v1 proposed three browser applets. v2 collapses Capture, Verify, and Browse into one Qt desktop app for these reasons:

| Reason | v1 (3 applets) | v2 (1 app) |
|---|---|---|
| **Filesystem access** | Blocked by `file://` browser sandbox | Direct disk I/O |
| **Lint integration** | Subprocess + parse stdout | In-process Python import |
| **Live PG introspection** | Impossible without sidecar | Q t IPC channel |
| **Snapshot capture of running app** | Manual paste only | `QScreen.grabWindow()` |
| **Reuses PG infrastructure** | Reimplements dark theme in CSS | Reuses `palette.py`, `styles.py`, `DarkConfirmDialog` |
| **Mental model** | Three apps to remember | One app, three tabs |
| **Codex/CC review effort** | Reviewing HTML+JS | Reviewing Python (their native lang) |

Lint stays as a separate Python package because it needs to run from the pre-commit hook (no GUI dependency). The Ledger app imports it for in-app violation reports.

### 0.4 — Lifecycle

```
[ Q&A session in Capture ]
       ↓
[ Decision file written: status=proposed → locked ]
       ↓
[ Dispatch cites DECISION_NNNN: status=dispatched ]
       ↓
[ CC commits with reference: status=shipped ]
       ↓
[ Lint runs on commit: blocks or passes ]            (automatic)
       ↓
[ Verify checklist + Darrin sign-off ]               (manual gate)
       ↓
[ Decision: status=verified ]
```

States can branch to `amended` (small fixes, no version bump) or `superseded` (replaced by new decision) or `retired` (removed without replacement). Full state machine in §3.5.

---

## 1 — Glossary

| Term | Definition |
|---|---|
| **Ledger app** | The Python application at `panda_ledger/`. Run via `python -m panda_ledger`. |
| **Decision** | A locked, recorded, traceable design choice. Has a unique ID `DECISION_NNNN`, a markdown file, a status, and a lifecycle. |
| **Decision file** | The markdown file at `workflows/decisions/DECISION_NNNN_<slug>.md`. Authoritative artifact. |
| **Snippet** | A *visual reference* attached to a decision (image / mockup region / sketch). Stored in `workflows/decisions/snippets/`. Always image-like. |
| **Baseline** | A *pixel reference* of a UI surface used for regression testing. Stored in `workflows/decisions/baselines/`. v2-future feature. (Renamed from "snapshot" in v1 to avoid overloading.) |
| **Q&A transcript** | The captured back-and-forth that produced a decision. Verbatim in the decision body. |
| **Citation** | A `DECISION_NNNN` reference inside another file (dispatch, code comment, Bible amendment, another decision, mockup HTML). |
| **Lifecycle state** | One of: `proposed`, `locked`, `dispatched`, `shipped`, `verified`, `amended`, `superseded`, `retired`. See §3.5. |
| **Amendment** | A small clarification or update to a locked decision (typo, new commit SHA, additional related decision). Does NOT create a new decision file. Tracked in `amendments:` frontmatter list. |
| **Supersession** | A new decision that replaces an old one. Creates a new file; old file's status becomes `superseded`. |
| **Inviolable rule** | One of the 23 hard rules in `CLAUDE.md`. Lint enforces the code-checkable subset. |
| **Bible section** | A numbered subsection of `PG_DESIGN_BIBLE_v1.md`. Decisions cite Bible sections; Lint references them in error messages. |
| **Per-state widget inventory** | Inviolable Rule #23 table that every UI dispatch must include. Verify renders this as a checklist. |
| **Trace** | The full chain from decision → dispatch → commit → code → verification. Verify can render it as a list. |
| **Spec.json** | The machine-readable extract of the Bible at `workflows/design/pg_design_spec.json`. Read by all four tools. |
| **Spec.json freshness** | A check that `pg_design_spec.json._meta.bible_hash` matches the current `PG_DESIGN_BIBLE_v1.md` SHA. Stale → warning at app startup, error in pre-commit. |

---

## 2 — Architecture

### 2.1 — File layout

```
panda-gallery/
├── panda_ledger/                          ← NEW: the Ledger app
│   ├── __init__.py
│   ├── __main__.py                        ← entry point: python -m panda_ledger
│   ├── window.py                          ← LedgerWindow (Qt main window with 3 tabs)
│   ├── capture/
│   │   ├── __init__.py
│   │   ├── capture_screen.py              ← Q&A authoring screen
│   │   ├── snippet_widget.py              ← three-mode snippet capture
│   │   ├── qa_pair_widget.py              ← single Q/A card
│   │   ├── bible_picker.py                ← Bible-section autocomplete
│   │   └── decision_writer.py             ← markdown + frontmatter serialization
│   ├── verify/
│   │   ├── __init__.py
│   │   ├── verify_screen.py               ← checklist + mockup viewer + reference panel
│   │   ├── checklist_widget.py            ← per-state widget inventory table
│   │   ├── reference_panel.py             ← palette swatches, fonts, spacing, animations
│   │   ├── mockup_viewer.py               ← QWebEngineView for mockup HTML
│   │   └── pg_introspect.py               ← talks to running PG instance
│   ├── browse/
│   │   ├── __init__.py
│   │   ├── browse_screen.py               ← searchable list of all decisions
│   │   └── decision_detail.py             ← read-only detail view
│   ├── shared/
│   │   ├── __init__.py
│   │   ├── decision_model.py              ← DecisionFile dataclass, YAML round-trip
│   │   ├── spec_loader.py                 ← reads pg_design_spec.json
│   │   ├── decision_index.py              ← in-memory index for fast search
│   │   ├── lint_runner.py                 ← in-process call to pg_design_lint
│   │   └── ipc.py                         ← QLocalSocket channel to running PG
│   ├── styles.py                          ← Ledger-specific QSS (subset of PG's)
│   └── tests/
│       ├── test_decision_model.py
│       ├── test_capture_flow.py
│       ├── test_verify_checklist.py
│       └── ...
│
├── pg_design_lint/                        ← NEW: standalone lint package
│   ├── __init__.py
│   ├── __main__.py                        ← entry point: python -m pg_design_lint
│   ├── lint.py                            ← orchestrator
│   ├── score.py                           ← score computation
│   ├── rules/
│   │   ├── __init__.py
│   │   ├── base.py                        ← Rule base class
│   │   ├── R01_forbidden_colors.py
│   │   ├── R02_off_palette_hex.py
│   │   └── ... (one file per rule)
│   ├── violations.py                      ← Violation dataclass
│   ├── report.py                          ← output formatters (text, JSON, IDE)
│   └── tests/
│       └── ...
│
├── workflows/
│   ├── decisions/                         ← decision files live here
│   │   ├── README.md                      ← format + contribution guide
│   │   ├── INDEX.md                       ← auto-generated rolled-up changelog
│   │   ├── DECISION_0001_<slug>.md
│   │   ├── DECISION_0002_<slug>.md
│   │   ├── ...
│   │   ├── staging/                       ← drafts in flight
│   │   │   └── <slug>.md
│   │   ├── snippets/                      ← visual references for decisions
│   │   │   ├── decision_0001_<slug>.png
│   │   │   ├── decision_0002_<slug>.svg
│   │   │   └── ...
│   │   └── verifications/                 ← Verify session outputs
│   │       └── <dispatch_id>_<timestamp>.md
│   │
│   ├── design/
│   │   ├── PG_DESIGN_BIBLE_v1.md
│   │   ├── PG_DESIGN_LEDGER_SPEC_v2.md    ← this file
│   │   ├── pg_design_spec.json            ← machine-readable extract
│   │   └── applets/                       ← legacy HTML applets (read-only references)
│   │       ├── PG_Design_Bible_Audit_v1.html
│   │       └── archive/
│   │
│   └── tools/
│       ├── pre_commit.py                  ← MODIFIED: invokes pg_design_lint
│       ├── pg_dispatch_lint.py            ← unchanged
│       ├── pg_decision_index.py           ← regenerates INDEX.md
│       ├── pg_spec_freshness.py           ← Bible-vs-spec.json hash check
│       └── ...
```

### 2.2 — Process model

The Ledger app is a separate process from PG, intentionally. Two reasons:

1. **Concurrent operation.** Verify needs to introspect a running PG instance. Two separate processes communicate over a local IPC channel.
2. **Independent crashes.** The Ledger crashing does not affect PG, and vice versa.

When the Ledger app starts, it:
1. Reads `pg_design_spec.json`, validates schema, runs freshness check
2. Builds in-memory decision index by scanning `workflows/decisions/*.md`
3. Opens its main window
4. Optionally connects to a running PG instance via `QLocalSocket` (if the introspection feature is requested by the user)

PG itself exposes a tiny IPC server (`panda_gallery/ledger_bridge.py`, opt-in flag `--ledger-bridge`) that responds to introspection queries from the Ledger. v2 implements one query: "list visible widgets in the currently focused module screen, by objectName, with visibility/enabled/geometry per widget."

### 2.3 — Shared spec file (`pg_design_spec.json`)

Single machine-readable extract of the Bible. Hand-authored in v2; derived-from-Bible script is v3 work.

Authority hierarchy:

1. **`PG_DESIGN_BIBLE_v1.md`** is the human source of truth. Always wins on conflict.
2. **`pg_design_spec.json`** is a derived extract used by tools. Must stay in sync with the Bible.

**Sync ownership.** When the Bible amends, the Bible amender (Claude Desktop or Codex) must update `pg_design_spec.json` in the same commit. The `_meta.bible_hash` field stores the SHA of the Bible at the time of the spec extract.

**Freshness check.** `pg_spec_freshness.py` computes the current Bible's SHA and compares to `_meta.bible_hash`. Mismatch produces:
- A warning at Ledger app startup ("spec.json is stale; tool output may diverge from Bible")
- An error in the pre-commit hook (blocks commits where the Bible is touched without updating spec.json)

The freshness check ships as a pre-commit check independently of `pg_design_lint`.

Schema sections are unchanged from v1 (already on disk in `pg_design_spec.json`):

- `_meta` — version, bible_version, bible_hash, generated_from, last_updated, consumers
- `palette` — surface, border, text, accent, semantic, mode_zones, sensor_sizes, gap_kinds, forbidden
- `typography` — families, scale, section_head, mono_color_rules
- `spacing` — scale, legitimate_off_scale
- `radius` — scale
- `motion` — timings, forbidden
- `buttons` — gbtn, gbtn_primary, primary_per_screen_max
- `inviolable_rules` — 23 rules with `code_check` boolean
- `bible_sections` — index for autocomplete
- `vocabulary_lock` — terms and forbidden substitutes
- `ledger_decision_statuses` — lifecycle state definitions

v2 adds:

- `_meta.bible_hash` — SHA-256 of the Bible at extract time
- `_meta.min_lint_version` — minimum compatible Lint version (versioning between spec and Lint)
- `bible_sections[].suggested_questions` — Bible-aware Q&A starter prompts (used by Capture)

---

## 3 — Decisions: schema, identity, lifecycle

### 3.1 — Decision file structure

Frontmatter is YAML; body is markdown. Full template in `workflows/decisions/README.md`. Key changes from v1:

- ID is 4-digit zero-padded (`DECISION_0001` through `DECISION_9999`)
- Single `implementation` block with `status` + `commits` (plural — superseded decisions may have multiple historical commits)
- Single `verification` block with `status` + history list
- `amendments:` list captures small fixes that don't warrant supersession
- `test_assertions:` is split into two distinct fields:
  - `human_checklist:` — list of strings rendered as Verify checklist items
  - `machine_assertions:` — Python code block runnable by Verify against introspection data

```markdown
---
id: DECISION_0001
slug: am-screen-b-collapsed-bug-card
title: Bug card collapsed by default in AM Screen B
status: locked
created_at: 2026-04-28T14:30:00-07:00
locked_at: 2026-04-28T15:10:00-07:00
authors:
  - claude_desktop
  - darrin
related_bible_sections:
  - "§1.6"
  - "§6.22"
related_specs:
  - "AM_SCREEN_B_SYNTHESIS_v1.md"
related_dispatches:
  - "CLAUDE-20260428-130000-a48-am-screen-b-implementation"
related_decisions:
  supersedes: []
  superseded_by: null
  related: []
  amends: []
implementation:
  status: shipped
  commits:
    - sha: 2eef1ad
      version: v4.60
      date: 2026-04-28
  files:
    - audit_module/v1/screen_b.py
verification:
  required: true
  status: pending
  history: []
amendments: []
tags:
  - audit-module
  - screen-b
  - progressive-disclosure
human_checklist:
  - "Bug card renders collapsed (title + meta strip only) on first open"
  - "▾ expand toggle is visible and clickable"
  - "Meta strip remains visible when card is collapsed"
machine_assertions: |
  # Run via pg_introspect IPC channel
  state = ipc.query("screen_b_state")
  assert state["bug_card.collapsed"] is True
  assert state["bug_card.meta_strip.visible"] is True
  assert state["bug_card.expand_block.visible"] is False
---

# DECISION_0001 — Bug card collapsed by default in AM Screen B

## Summary
[one paragraph]

## Q&A transcript
[verbatim]

## Visual snippet
![collapsed bug card](snippets/decision_0001_<slug>.png)
> caption

## Rationale
[bullet points citing Bible]

## Forbidden alternatives
[what we rejected and why]

## Implementation binding
[spec / mockup / code / commit references]

## Notes
[follow-ups, clarifications]
```

### 3.2 — Identity rules

- **ID format:** `DECISION_NNNN` where NNNN is 4 digits zero-padded. Sequence starts at 0001. Maximum 9999. (If we exceed, v3 amendment.)
- **Sequence allocation:** at lock time, Capture computes `max(NNNN) + 1` from `workflows/decisions/DECISION_*.md`. Sequence is permanent; never reused.
- **Slug:** kebab-case, generated from title, max 60 chars, user-overridable.
- **File name:** `DECISION_<NNNN>_<slug>.md`. The slug part is for human readability; tooling matches by ID prefix only.
- **Authors:** values come from a fixed allowlist in `pg_design_spec.json.author_aliases`. Currently: `darrin`, `claude_desktop`, `claude_code`, `codex`. New aliases require a Bible/spec amendment.

### 3.3 — Citation conventions

| Source | Citation format | Example |
|---|---|---|
| Spec docs (markdown) | `DECISION_NNNN` plus optional link | "Per `DECISION_0023`, evidence blocks collapse by default." |
| Dispatches (YAML frontmatter) | `related_decisions: [DECISION_0023]` | listed in frontmatter |
| Code comments | `# Per DECISION_NNNN, ...` | `# Per DECISION_0023, evidence is collapsed at construction.` |
| Bible amendments | "Implements DECISION_NNNN" in version note | "v1.4: §6.22.5 added per DECISION_0087." |
| Other decisions | `related_decisions.related: [DECISION_NNNN]` | YAML frontmatter |
| Mockups (HTML comments) | `<!-- DECISION_NNNN: <reason> -->` | inside the relevant region |

Lint rule R14 verifies every citation:
1. Format matches `DECISION_\d{4}`
2. File exists in `workflows/decisions/` OR in `workflows/decisions/staging/` (staging draft is acceptable for in-progress code)
3. Status is not `retired` (warning if cited)
4. Status is not `superseded` (warning; severity escalates if the citation is in code from a commit younger than the supersession)

### 3.4 — Test assertions: split into two fields

v1 conflated machine-runnable assertions with human checklist items. v2 separates them:

**`human_checklist`** — list of strings. Each string is a checklist item shown to Darrin in the Verify tab. Always present if `verification.required: true`.

**`machine_assertions`** — optional Python code block. If present, the Verify tab runs it against introspection data from the running PG (via `pg_introspect.py`). If introspection is unavailable, items derived from `machine_assertions` show as "auto-check unavailable; verify manually" in the checklist.

Both can be present. They complement each other — `human_checklist` covers visual/aesthetic items that machines can't judge ("the layout feels balanced"), `machine_assertions` covers structural items ("widget X has property Y").

### 3.5 — Lifecycle state machine

```
                 ┌─────────────┐
                 │  proposed   │  (Capture draft, in staging/)
                 └──────┬──────┘
                        │ Q&A complete + lock action
                        ▼
                 ┌─────────────┐
        ┌────────│   locked    │  (file in workflows/decisions/)
        │        └──────┬──────┘
        │               │ dispatch sent + cites this ID
        │               ▼
        │        ┌─────────────┐
        │   ┌────│ dispatched  │
        │   │    └──────┬──────┘
        │   │           │ commit cites this ID
        │   │           ▼
        │   │    ┌─────────────┐
        │   │ ┌──│   shipped   │
        │   │ │  └──────┬──────┘
        │   │ │         │ Verify sign-off
        │   │ │         ▼
        │   │ │  ┌─────────────┐
        │   │ │  │  verified   │  (terminal happy state)
        │   │ │  └──────┬──────┘
        │   │ │         │
        │   │ │         │ small fix (typo, new commit, etc.)
        │   │ │         ▼
        │   │ │  ┌─────────────┐
        │   │ │  │   amended   │  (same file, amendments[] grows)
        │   │ │  └─────────────┘
        │   │ │         │
        │   │ │         │ replaced by new decision
        │   │ │         ▼
        ├───┴─┴───┌─────────────┐
        │         │ superseded  │  (terminal; new file gets new ID)
        │         └─────────────┘
        │
        │  any state can transition to:
        ▼
 ┌─────────────┐
 │   retired   │  (decision dropped without replacement; reason required)
 └─────────────┘
```

Transitions:

| From → To | Trigger | Authority | Allowed mid-lifecycle |
|---|---|---|---|
| (none) → `proposed` | Capture creates draft | Anyone | — |
| `proposed` → `locked` | Lock & promote action | Darrin or Claude (with Darrin's approval) | — |
| `locked` → `dispatched` | dispatch's `related_decisions:` cites this ID | Auto (Lint detects) | — |
| `dispatched` → `shipped` | commit message cites this ID OR `implementation.commits[]` updated | Auto (Lint detects) or manual | — |
| `shipped` → `verified` | Verify generates sign-off report | Darrin in Verify tab | — |
| `verified` → `amended` | Small fix recorded; `amendments[]` appended | Anyone with Darrin's confirmation | Yes — amendments allowed in any post-locked state |
| any → `superseded` | New decision with `supersedes: [this_id]` | Anyone authoring the replacement | — |
| any → `retired` | `retirement_reason` field added | Darrin only | — |
| any earlier state → `locked` | Recall (e.g. dispatch was canceled) | Darrin only | — |

**Amendments vs supersessions.** Use amendment for: typo fixes, new commit SHA added, new related_decision link, additional notes. Use supersession for: change to the rationale, change to the answer, change to the visual snippet, anything Darrin would call "we changed our mind."

### 3.6 — Amendment record format

Each amendment appended to the `amendments:` list:

```yaml
amendments:
  - amended_at: 2026-05-01T10:15:00-07:00
    by: darrin
    summary: "Added commit SHA for v4.61 follow-up fix"
    fields_changed:
      - implementation.commits
```

Lint never warns on amendments. Capture's "amend" mode lets Darrin edit a locked decision and writes the amendment record automatically.

---

## 4 — Tool 1: Lint (`pg_design_lint`)

### 4.1 — Purpose

Static-analysis Python package. Reads `.py` files and flags violations of the design language. Two consumers:

1. **Pre-commit hook** — blocks bad commits.
2. **Ledger app** — in-process import; renders violation reports in the Browse and Verify tabs.

### 4.2 — Architecture

Each rule is a self-contained Python module in `pg_design_lint/rules/`. The orchestrator discovers rules at startup via `pkgutil.iter_modules`. Adding a new rule is a one-file change.

Each rule subclasses `pg_design_lint.rules.base.Rule`:

```python
class Rule:
    rule_id: str           # "R03"
    title: str             # "Native Qt dialogs forbidden"
    severity: str          # "error" | "warning" | "info"
    bible_ref: str         # "Inviolable Rule #22"
    fix_suggestion: str    # text shown after violation
    file_pattern: str      # glob for files this rule applies to (default: "**/*.py")
    requires_ast: bool     # if False, rule operates on raw text only
    requires_decisions: bool  # if True, in-memory decision index is passed in
    
    def check(self, file_path, source, ast_tree, spec, decisions=None) -> list[Violation]:
        ...
```

The orchestrator parses each `.py` file to AST once, loads `pg_design_spec.json` once, and (if any rule requires it) builds the decision index once per run. Rules consume the cached state.

### 4.3 — Rules (v2)

Same 20 rules from v1 with the following changes:

- **R10, R11** ship as `info` severity by default (previously `warning`). Heuristic rules with known false-positive risk should not block builds. Promote to `warning` after one month of clean runs.
- **R14** is unchanged but now references decision index (loaded once per run, not per file) for performance.
- New: **R21 — Spec.json freshness** — error if spec.json's `_meta.bible_hash` doesn't match the current Bible SHA.
- New: **R22 — Decision file schema validity** — runs only on files in `workflows/decisions/`. Validates frontmatter against the schema in §3.1, including required fields, status transitions, sequence allocation.
- New: **R23 — Inviolable rule citation in dispatch** — runs on dispatch markdown files (in `workflows/cc_mailbox/` and `C:\CODEX PG\...`). Requires per-state widget inventory tables when Inviolable Rule #23 applies.

R12, R13, R19 stay as `warning`. R09, R17, R20 stay as `info`.

### 4.4 — Severity scale and exit codes

| Severity | What it means | Pre-commit blocks? |
|---|---|---|
| `error` | Definite violation. Cannot ship. | Yes (blocks always) |
| `warning` | Probable violation. Investigate. | Yes in `--strict` mode |
| `info` | Heuristic or stylistic. Inform. | No |

Exit codes:
- 0 — clean (no errors; warnings allowed in non-strict)
- 1 — errors found
- 2 — warnings found in strict mode
- 3 — script error (couldn't read spec, etc.)

### 4.5 — Inline escape hatch

Per-line:
```python
self.setStyleSheet("background: #ff0000;")  # pg-lint:allow R02 mockup-only debug color
```

Per-block (new in v2):
```python
# pg-lint:allow-block R02 — token definition file
RAW_HEX_VALUES = {
    "canvas": "#14141f",
    ...
}
# pg-lint:end-allow-block
```

Whole-file:
```python
# pg-lint:allow-file R02 R04 — token definition module
```

The reason after the rule ID is required. Reasons longer than 80 characters are ignored — keep them brief.

### 4.6 — CLI

```
python -m pg_design_lint [path] [flags]
```

Flags from v1 plus:

- `--changed-only-since <ref>` — git-diff-based filter, ref defaults to `HEAD`
- `--severity-floor <error|warning|info>` — only show violations at or above this severity
- `--exemption-report` — list all `pg-lint:allow*` comments and their reasons (audit aid)

### 4.7 — Pre-commit integration

`workflows/tools/pre_commit.py` adds two new checks:

```python
CHECKS = [
    ast_parse_staged_python_files,
    pg_dispatch_lint,
    vbump_check,
    pytest_full_suite,
    pg_spec_freshness_check,            # NEW — Bible vs spec.json hash
    pg_design_lint_strict_changed_only, # NEW — Lint on staged .py files
]
```

`pg_design_lint_strict_changed_only` runs `python -m pg_design_lint --strict --changed-only --severity-floor warning` on staged files only.

Performance budget: <2s for typical commits (5–20 staged files). Achieved by the changed-only filter and shared AST/spec/decision-index loading.

### 4.8 — Auto-fix output (Codex's open question 2 from v1)

`--fix-suggestions` outputs textual suggestions inline with violations. v2 does NOT generate a unified diff — too risky, and the rules with auto-fix potential (R02 hex codes, R06 font names) need contextual judgment that's hard to automate. Reasoned fix suggestions inline are sufficient; the developer applies them manually.

### 4.9 — Rule execution order (Codex's open question 5)

Rules run in dependency order, not strict numeric order. Dependency graph:

1. R21 (spec freshness) runs first. If spec is stale, abort (no other rules trustable).
2. R22 (decision schema) runs second on decision files, building the decision index for later rules.
3. R14 (decision citation validity) runs third on `.py` files, using the index from R22.
4. All other rules run in any order (they have no inter-dependencies).

Within each tier, deterministic numeric order is preserved for reproducible output.

### 4.10 — Legacy backlog policy (NEW in v2)

When Lint ships, the existing PG codebase will fail thousands of checks. Policy:

1. **Initial run produces a baseline report.** `python -m pg_design_lint --baseline` writes a JSON file `workflows/decisions/lint_baseline_<date>.json` listing every existing violation by `(file, line, rule_id)`.
2. **Pre-commit ignores baseline violations.** A staged commit only fails if it introduces new violations OR changes a line that previously had a baselined violation (i.e. you touched the line, you fix it).
3. **Baseline shrinks over time.** Each commit that fixes a baselined violation auto-updates the baseline file (new violations don't auto-add — only fixes auto-apply, and the baseline auto-stages itself for the same commit).
4. **Score Card tracks baseline trend.** "Repo started at 1247 baselined violations; today 891."
5. **Periodic baseline pruning.** Every 30 days, a CLI sweep removes baseline entries for files that no longer exist or lines that no longer match the rule.

This is the "ratchet" model — old code is tolerated, new code must be clean, and the ratchet pulls the codebase toward zero violations over time without a single big-bang fix.

---

## 5 — Tool 2: Capture (Ledger app, Capture tab)

### 5.1 — Purpose

In-app Q&A authoring. Walks Darrin and Claude through structured decision capture. Outputs a markdown decision file plus snippet, ready for review and lock.

### 5.2 — Layout

Three-pane Qt layout, Bible-conformant:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🐼 PG Design Ledger — Capture                       [● Draft]    [_  □  ✕]  │ <- title bar (44px)
├────────┬────────┬────────┬───────────────────────────────────────────────────┤
│Capture │ Verify │ Browse │                                                   │ <- module tabs (38px)
├────────┴────────┴────────┴───────────────────────────────────────────────────┤
│ DECISION METADATA       │ Q&A AUTHORING                  │ VISUAL SNIPPET    │
│ ──────────────────────  │ ─────────────────────────────  │ ───────────────── │
│ status: [Proposed   v]  │ # title field ──────────────── │ [Paste|Mockup|Sketch] <- snippet tabs
│                         │ slug: am-screen-b-...           │                   │
│ tags: [+ tag]           │                                │ ┌───────────────┐ │
│  · audit-module         │ ── SUMMARY ─────              │ │  drop zone    │ │
│  · screen-b             │ [textarea]                    │ │  or pasted    │ │
│                         │                                │ │   image       │ │
│ Bible §s: [+]           │ ── Q&A ──────────────────     │ │               │ │
│  · §1.6                 │ ┌─ Q1 ──────────────────────┐ │ └───────────────┘ │
│  · §6.22                │ │ Q: [textarea]              │ │ caption: [...]    │
│                         │ │ A: [textarea]              │ │                   │
│ Specs:                  │ │              [✕ remove]    │ │                   │
│ AM_SCREEN_B_SYNTH...    │ └────────────────────────────┘ │                   │
│ AM_SCREEN_B_UX_REF...   │ [+ Add another Q/A]          │                   │
│                         │                                │                   │
│ Dispatches:             │ ── RATIONALE ───              │                   │
│ CLAUDE-20260428-...     │ [textarea]                    │                   │
│                         │                                │                   │
│ Related decisions:      │ ── FORBIDDEN ALTERNATIVES ──  │                   │
│ [+ link]                │ [textarea]                    │                   │
│                         │                                │                   │
│ Authors:                │ ── HUMAN CHECKLIST ───        │                   │
│ darrin, claude_desktop  │ [list editor]                 │                   │
│                         │                                │                   │
│                         │ ── MACHINE ASSERTIONS ──      │                   │
│                         │ [code editor with syntax HL]  │                   │
├─────────────────────────┴────────────────────────────────┴───────────────────┤
│ Required: title, summary, ≥1 Q/A, snippet, ≥1 Bible §       [Validation: OK]│ <- bottom bar (32px)
│                          [📄 Preview MD] [💾 Save draft] [✦ Lock & promote] │
└──────────────────────────────────────────────────────────────────────────────┘
```

Sizes follow Bible §13 (sizing invariants):
- Window minimum width derived from button-cluster + multi-line input floors, NOT hardcoded
- Default size = floor × 1.15
- Persistence via `QSettings("PandaGallery", "Ledger")` per Bible §13.3
- ESC closes the screen (drops to last unsaved state with confirmation if dirty)

### 5.3 — Q&A flow

Required fields enforced before lock:
1. Title and slug (slug auto-generated, editable)
2. Summary (≥10 words)
3. ≥1 complete Q/A pair
4. Visual snippet (one of three modes)
5. ≥1 Bible section
6. Tags (≥1)
7. Authors (defaults from app settings)

Optional but encouraged:
8. Rationale (markdown, with Bible-section autocomplete on `§`)
9. Forbidden alternatives
10. Human checklist (used by Verify)
11. Machine assertions (Python; syntax-highlighted)
12. Related specs / dispatches / decisions
13. Implementation binding (often empty at lock time, filled later via amendments)

Validation indicator at the bottom shows running tally. Lock button enables only when all required fields are present.

### 5.4 — Visual snippet capture

Three modes (selected via tabs at the top of the right pane):

**Mode A — Paste image.** `QLabel` drop zone accepts paste (Ctrl+V) or drag-drop. Image saved as `workflows/decisions/snippets/decision_<NNNN>_<slug>.png`. Caption field below.

**Mode B — Mockup reference.** `QFileDialog` (using `DarkInputDialog`) restricted to `pg_general_mockups/`. User picks an HTML file. Optional CSS selector field. The decision file stores both the path and selector. Verify uses these to auto-scroll the mockup viewer to the right region.

**Mode C — Sketch.** A `QGraphicsView` canvas with a `QGraphicsScene` and a small toolbox: rectangle, line, text, accent color, dim color, clear, undo. Output saved as a `.svg` file in `snippets/` (NOT inline — addresses v1 issue G4). Caption field below.

Switching modes preserves data — the user can experiment.

### 5.5 — Persistence

- **Auto-save:** every 30 seconds while dirty. Writes to `staging/<slug>.md.autosave`. Recovered on restart.
- **Save draft:** writes to `staging/<slug>.md`. Idempotent.
- **Lock & promote:** computes next sequence ID, renames file, moves to `workflows/decisions/`, sets status=`locked`, updates the in-memory index, refreshes the Browse tab.

If the user closes the app while a draft is dirty, a confirmation dialog (`DarkConfirmDialog`) asks: "Save draft? Discard? Cancel close?"

### 5.6 — Bible-aware question suggestions

When a Bible section is added to `related_bible_sections`, the right side of the Q&A area shows a collapsible "Starter questions" panel pulled from `pg_design_spec.json.bible_sections[].suggested_questions`. Click a suggestion to pre-fill a new Q. Suggestions are read-only prompts; the user always edits the text.

### 5.7 — Decision linking

A "+ link" button in the Related decisions section opens a search dialog (`DarkInputDialog` with autocomplete). Search by title, ID, or tag against the in-memory index. Clicking a result adds it to the appropriate frontmatter field.

For supersession: a separate "Supersedes..." button opens the same picker but performs the bidirectional link (writes `supersedes: [old_id]` on the new draft, sets `superseded_by: new_id` on the old file at lock time).

### 5.8 — Markdown preview

A Preview button opens a modal dialog showing the generated markdown verbatim, with a "Copy to clipboard" action. Uses the existing PG dark dialog pattern.

---

## 6 — Tool 3: Verify (Ledger app, Verify tab)

### 6.1 — Purpose

Manual sign-off gate before commit-go on UI work. Combines per-state widget checklists with the Bible reference and produces a verification report.

### 6.2 — Layout

Three panes, similar to Capture but different content:

```
┌────────┬────────┬────────┬───────────────────────────────────────────────────┐
│Capture │ Verify │ Browse │                                                   │
├────────┴────────┴────────┴───────────────────────────────────────────────────┤
│ CHECKLIST           │ MOCKUP / RUNNING APP            │ BIBLE REFERENCE      │
│ ─────────────────   │ ─────────────────────────────   │ ─────────────────    │
│ Loaded from:        │ ┌──────────────────────────┐    │ PALETTE              │
│ [Dispatch ▼]        │ │                          │    │ ▣ canvas  #14141f    │
│ A48 — AM Screen B   │ │   QWebEngineView with    │    │ ▣ chrome  #161625    │
│                     │ │   mockup HTML loaded     │    │ ▣ pane    #1a1a2e    │
│ STATE 1 (UNTRIAGED) │ │                          │    │ ...                  │
│ ┌─────────────────┐ │ │                          │    │                      │
│ │ ✓ ✗ Re-triage   │ │ └──────────────────────────┘    │ TYPOGRAPHY           │
│ │ ✓ ✗ Stepper     │ │ Toggle: [Mockup|App|Side]       │ Display 28/300/0.3   │
│ │ ✓ ✗ Status pane │ │                                  │ ...                  │
│ │ ⚠ ✗ Triage CTA  │ │                                  │                      │
│ │   [PASS][FAIL]  │ │                                  │ SPACING              │
│ │ ◯ ◯ Bug card    │ │ INTROSPECTION (if PG running):  │ xs sm md lg xl 2xl   │
│ │ ◯ ◯ Evidence    │ │   ✓ Connected to PG (port 9876) │ 4  8  12 16 24 32    │
│ └─────────────────┘ │   Auto-checks: 3 PASS / 1 FAIL  │                      │
│                     │   (failed: Triage CTA missing)  │ MOTION               │
│ STATE 3 (GAPS)      │                                  │ ◉ pulse 1.5s         │
│ ...                 │                                  │ ◉ shimmer            │
│                     │                                  │                      │
│                     │                                  │ INVIOLABLE RULES (v) │
│                     │                                  │ #1 Never lose data   │
│                     │                                  │ #9 No white bg ✓     │
│                     │                                  │ #22 Dark dialogs ✓   │
│                     │                                  │ ...                  │
├─────────────────────┴──────────────────────────────────┴──────────────────────┤
│ 12/14 PASS · 1 FAIL · 1 PENDING        [📋 Generate report]  [✦ Sign off]   │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 6.3 — Loading a verification session

User picks the source from a dropdown:
1. **From a dispatch file** — paste dispatch ID; Verify loads the per-state widget inventory from the dispatch's frontmatter or body table.
2. **From a decision file** — paste decision ID; Verify loads `human_checklist` and `machine_assertions` blocks.
3. **From a saved verification session** — list of past sessions in `workflows/decisions/verifications/`.

The dropdown remembers the last 10 loaded sources for fast re-verification.

### 6.4 — Mockup / running-app comparison

The center pane uses `QWebEngineView` to render the mockup HTML directly (works offline, full DOM access). A toolbar above it switches between three views:

1. **Mockup only** — the approved reference
2. **Running app only** — uses `QScreen.grabWindow()` to capture the focused PG window
3. **Side-by-side** — split view, mockup left, running app right

The "running app" mode requires PG to be running with the `--ledger-bridge` flag. Without the bridge, Verify falls back to manual paste (user uses Win+Shift+S, pastes into a drop zone).

### 6.5 — Live introspection

If `--ledger-bridge` is active, Verify connects to PG via `QLocalSocket` and queries widget state. Returned data includes:
- Widget tree by `objectName`
- Per-widget visibility, enabled state, geometry
- Active screen / module / state if applicable

Verify uses this to:
- Auto-check items in `machine_assertions` blocks
- Highlight checklist items in green if introspection confirms PASS
- Show "auto-check unavailable" for items that depend on visual judgment

### 6.6 — Bible reference panel

Always-visible right pane. Sections:

- **Palette** — every token from spec.json. Hover to see name+role; click to copy hex.
- **Typography** — every type-scale entry rendered at correct size with sample text.
- **Spacing** — visual ruler showing scale tokens.
- **Motion** — three live demos (pulse, shimmer, sweep). Click to play.
- **Inviolable rules** — collapsible cards with title, Bible link, "find violations" button (runs Lint inline against the codebase, shows results).

The reference panel is read-only. It's the cheat sheet, not an editor.

### 6.7 — Sign-off and report

Sign-off button is disabled until all required checklist items are PASS. (Items can be marked SKIP with a reason, which counts as PASS for sign-off but is recorded separately in the report.)

On sign-off:
1. Confirmation dialog: "All N items resolved. Confirm sign-off?"
2. Generate report markdown
3. Save to `workflows/decisions/verifications/<dispatch_id>_<timestamp>.md`
4. Update `verification.history[]` on every cited decision file
5. Output a one-line message Darrin can paste to Claude Desktop chat: "Verified A48 — issue commit-go." This is the integration with the existing chat-driven commit-go flow (Verify does NOT write directly to CC's mailbox — Darrin still drives commit-go through Claude Desktop, but Verify provides the evidence).

---

## 7 — Tool 4: Browse (Ledger app, Browse tab)

### 7.1 — Purpose

Read-only searchable index of all decisions. The "what did we decide?" answer.

### 7.2 — Layout

Two-pane Qt layout:

```
┌────────┬────────┬────────┬───────────────────────────────────────────────────┐
│Capture │ Verify │ Browse │                                                   │
├────────┴────────┴────────┴───────────────────────────────────────────────────┤
│ DECISION LIST (320px)            │ DECISION DETAIL (read-only)                │
│ ───────────────────────────────  │ ─────────────────────────────────────────  │
│ [Search...               ]       │ # DECISION_0023 — Evidence block...        │
│                                  │                                            │
│ Filter: [All status v]           │ Status: ● shipped                          │
│         [All Bible §s v]         │ Locked: 2026-04-28 by darrin               │
│         [All tags v]             │                                            │
│                                  │ ## Summary                                 │
│ ● 0023 Evidence block...         │ [content]                                  │
│ ● 0022 ALL chip neutral cream    │                                            │
│ ◐ 0021 Triage CTA centered       │ ## Q&A transcript                          │
│ ✓ 0020 Bug card collapsed        │ [content]                                  │
│ ✓ 0019 ...                       │                                            │
│ ⊘ 0018 (superseded)              │ ## Visual snippet                          │
│ ...                              │ [embedded image]                           │
│                                  │                                            │
│                                  │ ## Trace                                   │
│                                  │ Decision → Spec ✓ → Mockup ✓ →             │
│                                  │ Dispatch ✓ → Commit 2eef1ad ✓ →            │
│                                  │ Code ✓ → Verification ⏳ pending           │
│                                  │                                            │
│                                  │ [Open file in editor] [Amend...] [Copy ID] │
└──────────────────────────────────┴────────────────────────────────────────────┘
```

### 7.3 — Search

Full-text search across:
- ID
- Title
- Summary
- Q&A transcript
- Rationale
- Tags
- Bible sections

Results ranked by recency. Search uses Python's stdlib (no external dependencies); index is rebuilt on every save (cheap — one read per decision file).

### 7.4 — Filters

Status, Bible section, tag — all multi-select. Filters compose (AND).

### 7.5 — Detail view

Read-only render of the decision file. Markdown rendered to HTML for display. "Open file in editor" launches the user's default editor on the file. "Amend..." opens the Capture tab in amend mode (loads the decision, lets the user edit specific fields, on save adds an amendment record).

### 7.6 — Trace rendering

For each decision, Browse computes the trace by:
1. Searching all spec docs (`workflows/design/*.md`) for the decision ID — list of citations
2. Searching all dispatches for `related_decisions:` entries — list of dispatches
3. Searching git log for commit messages mentioning the decision ID — list of commits
4. Searching `*.py` files for `# Per DECISION_NNNN` comments — list of code citations
5. Reading `verification.history[]` from the decision file — list of verifications

Each row in the trace is clickable; clicking opens the file at the right line in the user's editor.

Missing links are highlighted (red row, "no citation found"). Useful for catching decisions that "shipped" but were never cited.

---

## 8 — Cross-cutting features (v2 minimal)

### 8.1 — INDEX.md auto-generated changelog

Single auto-generated file at `workflows/decisions/INDEX.md`. Run by `pg_decision_index.py` from a pre-commit hook.

Contents:
- TOC: counts by status (proposed/locked/dispatched/shipped/verified/amended/superseded/retired)
- Chronological list of every decision (newest first)
- Per-decision: ID, title, status icon, locked date, Bible refs, tags

The file is stable — same input produces same output — so its diff is reviewable. The pre-commit hook regenerates it and auto-stages the change with the commit.

v2 ships ONE index file. The "by Bible section" and "by tag" indices are deferred to v3.

### 8.2 — Score Card (basic)

Lint computes a score per file using LOC normalization (addresses v1 D7):

```
violations_per_100_loc = (errors × 5 + warnings × 1 + info × 0.2) × 100 / loc
score = max(0, 100 - violations_per_100_loc)
```

A 200-line file with 5 warnings scores 97.5. A 2000-line file with 50 warnings also scores 97.5 — fair.

The Browse tab has a small Score panel showing:
- Repo-wide score
- Per-module scores (panda_ledger, audit_module, library_module, etc.)
- Top 3 highest- and lowest-scoring files

No sparklines, no trend graphs in v2. Deferred to v3.

### 8.3 — IPC channel to running PG

`panda_gallery/ledger_bridge.py` is a new file in PG (NOT in panda_ledger — it's PG's side of the bridge). Activated by the `--ledger-bridge` CLI flag. Opens a `QLocalServer` on a deterministic socket name (`pg_ledger_bridge_<pid>`).

Verify connects via `QLocalSocket` and sends JSON queries. PG responds with widget state. Queries supported in v2:

- `get_widget_tree(scope)` — returns `objectName`, geometry, visibility, enabled for every widget under scope
- `get_active_state()` — returns active module, screen, sub-state (e.g. "audit_module / screen_b / state_3")
- `screenshot()` — captures the focused window using `QScreen.grabWindow()` and returns a base64 PNG

The IPC protocol is simple line-delimited JSON. No authentication (localhost only). v3 may add a wider query surface.

---

## 9 — Out of scope (v2)

Explicitly deferred to v3 to keep v2 shippable:

- Snapshot baselines for visual regression (renamed from "snapshots" in v1; the whole pixel-diff system)
- Score Card with sparklines, trend graphs, per-commit deltas
- Trace path visualization (a fancy widget — text trace in §7.6 is sufficient for v2)
- Decision templates (premature; build after we have 30 real decisions to learn from)
- BY_BIBLE_SECTION.md and BY_TAG.md indices (single INDEX.md is enough for v2)
- Real-time collaboration (one user at a time)
- Cross-repo decision sharing
- Decision import/export
- AI-generated decision drafts (Claude can suggest Q&A starters; does not auto-author)
- Automated migration of existing chat-locked decisions (manual backfill in Phase 4)
- Bible-section auto-update from decisions
- Email notifications (per WORKING_RULES_v1.md)
- Block-level lint exemption syntax (per-line + per-file is sufficient for v2)

---

## 10 — Build phases

### 10.1 — Phase 0: Foundation

- This spec written ✓
- Codex and CC review (next step)
- Reconcile, lock as v2
- `pg_design_spec.json` already exists; add `bible_hash`, `min_lint_version`, `suggested_questions`
- Directory creation: `workflows/decisions/`, `staging/`, `snippets/`, `verifications/`, `archive/`, `pg_design_lint/rules/`, `panda_ledger/...`
- README files

Owner: Claude Desktop. Effort: half day after reviews are reconciled.

### 10.2 — Phase 1: Lint package (`pg_design_lint/`)

- Codex builds. Extra-High tier.
- 23 rules in separate modules
- Orchestrator + score + report formatters
- Pre-commit hook integration (R21 + main lint)
- Tests for every rule
- Baseline run against existing codebase
- Deliver impl report

Estimated effort: ~2000 LOC + ~700 LOC tests + per-rule docs.

### 10.3 — Phase 2: Ledger app skeleton + Capture tab

- Claude Desktop builds with Darrin live.
- LedgerWindow shell, three-tab structure
- Capture tab fully functional
- Decision schema model (`decision_model.py`)
- In-memory decision index
- Snippet capture (paste, mockup ref, sketch)
- Lock & promote flow
- Bible-aware question suggestions
- Tests for capture flow

Estimated effort: ~3000 LOC + ~600 LOC tests.

### 10.4 — Phase 3: Browse tab

- Claude Desktop or CC builds (TBD based on capacity)
- Search + filter
- Read-only detail view
- Trace rendering (file scanning)
- Open-in-editor integration
- Amend flow

Estimated effort: ~1500 LOC.

### 10.5 — Phase 4: Verify tab + IPC bridge

- CC builds (after capacity to assist with PG-side bridge)
- Verify checklist UI
- Mockup viewer (`QWebEngineView`)
- Bible reference panel
- IPC bridge in PG (`panda_gallery/ledger_bridge.py`)
- Live introspection client
- Sign-off + report generation
- Integration with chat-driven commit-go flow

Estimated effort: ~2500 LOC + ~500 LOC for the PG bridge.

### 10.6 — Phase 5: Migration and integration

- CLAUDE.md update (Inviolable Rule #23 references Capture)
- WORKING_RULES_v1.md update (Verify sign-off required for UI commit-go)
- Backfill ~30 historical decisions retroactively
- Lint baseline established and committed
- INDEX.md generated

---

## 11 — Risks and mitigations

| Risk | Mitigation |
|---|---|
| Decision capture becomes overhead and gets skipped | Capture is fast (≤5 minutes for typical decision), Bible-aware question suggestions reduce blank-page paralysis, templates deferred to v3 once we know what's common |
| Lint false positives erode trust | Heuristic rules ship as `info`, ratchet model means existing code doesn't suddenly break, exemption syntax is documented |
| Verify becomes a bottleneck | Pre-loads checklists from dispatch, Bible reference always visible, keyboard shortcuts for PASS/FAIL |
| Bible/spec.json drift | R21 freshness check fails the pre-commit hook on Bible touches that don't update spec.json |
| Decisions accumulate without retirement | INDEX.md shows superseded decisions distinctly, Lint warns on stale citations |
| IPC bridge is fragile | v2 ships with manual fallback (paste screenshot); bridge is opt-in via `--ledger-bridge` |
| `QWebEngineView` adds large dependency | Already used elsewhere in PG (region capture); no new dep |
| Snippet files balloon repo size | PNG snippets target ≤500KB, SVG sketches target ≤50KB, Lint warns on oversized snippets |
| Q&A gets too long, decisions diluted | Capture warns when Q or A exceeds 500 words; placeholder copy encourages conciseness |
| Ledger app itself drifts from Bible | Ledger uses PG's existing `palette.py` and `styles.py`; if PG's design language changes, Ledger inherits |

---

## 12 — Success criteria (v2)

Six weeks after launch:

1. ≥ 30 decisions captured, all with snippet + Q&A + Bible refs
2. Pre-commit Lint blocks ≥ 1 commit per week (proves it's catching real violations)
3. Zero "I forgot we decided that" incidents in chat (Darrin can search the ledger)
4. Every UI dispatch since launch cites at least one DECISION_NNNN
5. Every UI commit-go has a Verify report attached
6. Repo-wide design score has improved by ≥ 10 points from baseline
7. CC and Codex consistently produce dispatches with per-state widget inventories (Inviolable Rule #23)

If any unmet, retrospective at week 6.

---

## 13 — Versioning

- v2 is this document. Supersedes v1.
- Token / minor changes: `git vcommit` versioned ship
- Architectural changes: explicit Darrin sign-off + amendment of this spec
- Lifecycle state changes: migration plan for existing decisions
- New Lint rules: backfill assessment (does existing codebase pass? if not, baseline absorbs)
- Schema changes to decision files: migration script in `workflows/tools/`

---

## Appendix A — Open questions for review

### For Codex (Lint focus)

1. R10/R11 ship as `info` — agree?
2. Auto-fix output as text only (no diff) — agree?
3. Block-level exemption syntax in v2 — kept (was a gap in v1)
4. CI environments: pre-commit hook only for v2; GitHub Actions deferred. Confirm scope?
5. Rule execution order: dependency-driven with deterministic numeric within tiers — confirm?
6. Score formula `100 - vp100loc` (LOC-normalized) — agree?
7. Performance target <2s for changed-only — achievable with shared AST + decision index?
8. R22 (decision schema lint) on `workflows/decisions/*.md` files — does this overlap with `pg_dispatch_lint.py`'s schema check?
9. R23 (per-state widget inventory) on dispatch markdown — heuristic or rigorous?

### For CC (Verify focus + Ledger architecture)

1. `QWebEngineView` for mockup rendering — any blockers in current PG dep set?
2. `QLocalSocket` IPC — is the auth-free localhost approach safe enough?
3. `QScreen.grabWindow()` for active app screenshot — works on Windows for non-PG processes?
4. Live introspection scope — `get_widget_tree`, `get_active_state`, `screenshot` enough for v2?
5. Should Verify share its decision-index instance with Capture (single in-process index across tabs)?
6. PG-side bridge file (`ledger_bridge.py`) lives where in PG? Top-level or under a subdir?
7. Verify performance with hundreds of checklist items — chunked rendering needed?

### For Darrin (governance)

1. Approval workflow — Capture's "Lock & promote" sufficient, or separate approval step?
2. Decision retirement criteria — specific examples?
3. Score targets — what's the floor? 80? 90?
4. Backfill scope — which historical decisions should be captured retroactively?
5. Bible-amendment ownership — who keeps `pg_design_spec.json` in sync? You? Me? Codex?

---

## Appendix B — Significant changes from v1 (for reviewer context)

| v1 element | v2 change | Reason |
|---|---|---|
| Three browser applets | One Qt app + standalone Lint package | Filesystem MCP unavailable to browsers |
| Snapshot baselines in Verify | Deferred to v3 | Scope cut; pixel-diff is its own subsystem |
| Score Card with sparklines | Basic score panel only | Scope cut; v2 ships data, dashboard later |
| Trace path view | Text-only trace in Browse | Scope cut; visualization deferred |
| Three index files | Single INDEX.md | Scope cut; one is enough |
| Templates | Deferred to v3 | Premature without real data |
| `test_assertions:` ambiguous | Split into `human_checklist:` + `machine_assertions:` | v1 D6 |
| 3-digit IDs | 4-digit IDs | Scale (v1 N2) |
| "snapshot" overloaded | Renamed to "baseline"; "snippet" reserved for visual references | v1 N1 |
| Score formula not LOC-normalized | LOC-normalized | v1 D7 |
| No legacy backlog policy | Ratchet model with baseline | v1 G1 |
| No amendment vs supersession distinction | `amended` lifecycle state added | v1 G5 |
| Bible/spec.json sync ownership unclear | Bible amender updates spec.json same commit; R21 enforces | v1 G6 |
| Authors free-form | Allowlist in spec.json | v1 U4 |
| No spec.json validity check | R21 freshness check | v1 U1 |
| No spec.json/Lint version compatibility | `_meta.min_lint_version` | v1 U2 |
| Inline SVG sketches | Saved as `.svg` files | v1 G4 |

---

## END OF SPEC v2 DRAFT

Status: ready for Codex and CC review.
