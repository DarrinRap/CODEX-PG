# PG Design Ledger — Parallel Build Plan v1

**Status:** DRAFT — pending Darrin approval before dispatch.
**Authored:** 2026-04-28
**Author:** Desktop Claude (with Darrin)
**Companion to:** `PG_DESIGN_LEDGER_SPEC_v2.md`
**Purpose:** Coordinate parallel development of the Ledger system across three AI builders (Claude Desktop, Codex, CC) with zero file overlap and clean modular reassembly.

---

## 0 — Executive summary

The PG Design Ledger is a substantial system: ~7500–8000 LOC across ~50 files. Building it serially would take days. Building it in parallel — Claude Desktop, Codex, and CC all working at the same time on disjoint file sets — finishes in roughly the time of the slowest single AI.

This plan splits the build along clean fault lines so:

1. **No two AIs touch the same file.** All ownership is exclusive.
2. **No build-order dependencies block parallelism.** A frozen contracts module is the only shared input; once locked, all three build independently.
3. **Modular reassembly is automatic.** Each package delivers independently testable artifacts that snap together via well-defined Python imports and IPC protocols.
4. **No human intervention is required mid-build.** Every ambiguity is resolved in this plan or the v2 spec; every question is answered before dispatch; every interface is locked.

The integration step at the end is mine — I run a smoke harness, fix any contract drift, and present Darrin a single bundle for commit-go.

---

## 1 — Work-split principles

### 1.1 — The natural fault lines

The Ledger system has four disjoint slices:

| Slice | Scope | Best owner | Why |
|---|---|---|---|
| **Lint package** | Standalone Python, CLI-driven, no GUI | Codex | Mechanical, exhaustive, requires reading the full Bible and translating every rule into Python checks. Codex's strength. |
| **Ledger app shell + Capture + Browse** | Qt window, Q&A authoring, decision browsing | Claude Desktop | UI/UX iteration, Bible-conformant visual design, file I/O — all things I'm well-positioned to build with Darrin's live review. |
| **Verify tab + IPC bridge** | Qt screen with QWebEngineView + QLocalSocket; PG-side bridge | CC | Needs running-PG repo context, Qt deep dive, integration with the existing PG entry point. |
| **Pre-commit and ancillary tools** | `pre_commit.py` modifications, `pg_spec_freshness.py` | Codex | Lives next to existing tooling Codex already maintains (`pg_dispatch_lint.py`). |

### 1.2 — Why Browse goes with Capture (not Verify)

Browse is essentially a read-only view of decision files plus search and trace rendering. Capture writes decision files; Browse reads them. Both share:

- The same `DecisionFile` dataclass
- The same in-memory decision index
- The same snippet rendering logic
- The same frontmatter parser
- Filename / path conventions

Splitting Browse from Capture would create artificial sync overhead. Keeping them together makes one AI responsible for the full read/write story of decision files.

### 1.3 — Why the IPC bridge goes with Verify (not PG)

The IPC bridge has two halves: PG-side (`panda_gallery/ledger_bridge.py`) and Ledger-side (`panda_ledger/shared/ipc.py`). Both must speak the same wire protocol. CC owns both files because:

- The protocol must match exactly across the wire
- CC has the PG repo context to wire `--ledger-bridge` into the existing CLI without breaking anything
- Single-author for both sides eliminates ambiguity about who owns the message format

The protocol is locked in `contracts.py` (mine) so even though CC writes both halves, they build against a frozen interface.

---

## 2 — Pre-dispatch artifacts (Phase 0, mine)

Before any AI starts building, I produce these artifacts. Together they constitute the complete contract surface.

### 2.1 — `pg_design_spec.json` v2 update

Add three fields to the existing spec.json:

- `_meta.bible_hash` — SHA-256 of the current Bible
- `_meta.min_lint_version` — minimum compatible Lint version (e.g. "1.0.0")
- `bible_sections[].suggested_questions` — list of starter Q&A prompts per Bible section (empty initially; populated over time)

### 2.2 — `panda_ledger/shared/contracts.py` — the FROZEN interface module

This is the single shared interface point. Locked before dispatch; no AI may modify it during build. Defines:

```python
# Decision lifecycle
class DecisionStatus(Enum): proposed, locked, dispatched, shipped, verified, amended, superseded, retired

# Decision file model
@dataclass(frozen=True)
class DecisionFile:
    id: str
    slug: str
    title: str
    status: DecisionStatus
    created_at: datetime
    locked_at: datetime | None
    authors: list[str]
    related_bible_sections: list[str]
    related_specs: list[str]
    related_dispatches: list[str]
    related_decisions: RelatedDecisions
    implementation: ImplementationBlock
    verification: VerificationBlock
    amendments: list[Amendment]
    tags: list[str]
    human_checklist: list[str]
    machine_assertions: str | None
    summary: str
    qa_pairs: list[QAPair]
    rationale: str
    forbidden_alternatives: str
    visual_snippet: SnippetReference
    body_notes: str

# Sub-types
@dataclass(frozen=True)
class QAPair: question: str; answer: str
@dataclass(frozen=True)
class SnippetReference: mode: Literal["paste", "mockup", "sketch"]; path: str; selector: str | None; caption: str
@dataclass(frozen=True)
class RelatedDecisions: supersedes: list[str]; superseded_by: str | None; related: list[str]; amends: list[str]
@dataclass(frozen=True)
class ImplementationBlock: status: str; commits: list[CommitRef]; files: list[str]
@dataclass(frozen=True)
class CommitRef: sha: str; version: str; date: str
@dataclass(frozen=True)
class VerificationBlock: required: bool; status: str; history: list[VerificationRecord]
@dataclass(frozen=True)
class VerificationRecord: verified_at: datetime; verified_by: str; report_path: str
@dataclass(frozen=True)
class Amendment: amended_at: datetime; by: str; summary: str; fields_changed: list[str]

# Lint model
class Severity(Enum): error, warning, info
@dataclass(frozen=True)
class Violation:
    rule_id: str
    severity: Severity
    file: Path
    line: int
    col: int
    message: str
    suggestion: str | None
    spec_ref: str
    can_autofix: bool

@dataclass(frozen=True)
class LintReport:
    violations: list[Violation]
    files_scanned: int
    spec_version: str
    lint_version: str
    timestamp: datetime

@dataclass(frozen=True)
class ScoreReport:
    overall: float
    per_module: dict[str, float]
    per_file: dict[str, float]
    baseline_violations_count: int
    new_violations_count: int

# IPC protocol (Ledger ↔ PG)
class IPCQueryType(Enum): get_widget_tree, get_active_state, screenshot, ping
@dataclass(frozen=True)
class IPCQuery:
    query_type: IPCQueryType
    scope: str | None  # for get_widget_tree: an objectName prefix
    request_id: str

@dataclass(frozen=True)
class IPCResponse:
    request_id: str
    success: bool
    payload: dict | None
    error: str | None

@dataclass(frozen=True)
class WidgetState:
    object_name: str
    class_name: str
    visible: bool
    enabled: bool
    geometry: tuple[int, int, int, int]  # x, y, w, h
    children: list["WidgetState"]

# Verify model
@dataclass(frozen=True)
class ChecklistItem:
    item_id: str
    widget_name: str
    description: str
    expected: Literal["visible", "hidden", "disabled"]
    state_group: str
    auto_check_assertion: str | None

@dataclass(frozen=True)
class ChecklistResult:
    item_id: str
    result: Literal["pass", "fail", "skip", "pending"]
    note: str
    timestamp: datetime
    auto_checked: bool

@dataclass(frozen=True)
class VerificationReport:
    dispatch_id: str | None
    decision_ids: list[str]
    started_at: datetime
    completed_at: datetime | None
    items: list[ChecklistItem]
    results: list[ChecklistResult]
    overall_outcome: Literal["pass", "fail", "incomplete"]
    verifier: str
    notes: str

# Spec loader contract
@dataclass(frozen=True)
class DesignSpec:
    meta: SpecMeta
    palette: dict
    typography: dict
    spacing: dict
    radius: dict
    motion: dict
    buttons: dict
    inviolable_rules: list[InviolableRule]
    bible_sections: list[BibleSection]
    vocabulary_lock: dict
    ledger_decision_statuses: list[dict]

@dataclass(frozen=True)
class InviolableRule:
    id: int
    title: str
    category: str
    code_check: bool
    summary: str | None
    lint_pattern: str | None

@dataclass(frozen=True)
class BibleSection:
    id: str
    title: str
    suggested_questions: list[str]
```

This file is THE contract. Every AI imports from it. None modifies it.

### 2.3 — `panda_ledger/shared/conventions.md` — coding standards

Read by all three AIs. Covers:

- Python version (3.10+)
- Type hints required everywhere
- `dataclasses` over plain classes for data
- Path objects from `pathlib`, never `os.path`
- Logging: `logging.getLogger(__name__)`, no `print()` in production code
- Exception handling: catch specific exceptions, never bare `except:`
- File I/O: always specify `encoding="utf-8"`, always use context managers
- YAML: `ruamel.yaml` (preserves comments) for round-tripping decision files; `pyyaml` for read-only
- Qt patterns: parent passing, signal/slot connections, no `lambda` slots without `partial`
- Test framework: pytest, fixtures in `conftest.py`
- Test naming: `test_<thing_under_test>_<condition>_<expected_outcome>()`
- Docstrings: Google style, all public functions documented
- Imports: stdlib first, third-party second, local third; `from __future__ import annotations` at top
- Error messages: include file path + line where relevant
- No external network calls in test code
- All file writes go through `panda_ledger.shared.atomic_write` (write to tempfile, fsync, rename) for crash safety

### 2.4 — Stub files at every interface point

Empty `.py` files with ownership headers like:

```python
"""verify_screen.py — owned by CC.

This file is part of the panda_ledger.verify package.
Owner: Claude Code (CC) — this file must NOT be modified by Claude Desktop or Codex.

See: PG_DESIGN_LEDGER_SPEC_v2.md §6 for the full specification.
See: panda_ledger.shared.contracts for the locked data contracts.
"""
```

Stubs prevent accidental file collisions. Each AI knows immediately whether a file is theirs.

### 2.5 — `panda_ledger/INTEGRATION_TEST_HARNESS.py`

A Python smoke test that all three packages must pass. Run by me at integration time. Tests:

1. All packages import without error
2. `LedgerWindow` instantiates, all three tabs construct
3. `pg_design_lint.lint(path)` returns a `LintReport` matching the contracts
4. `panda_ledger.shared.ipc.connect(socket_name)` succeeds against a mock server
5. A round-trip decision file: write via Capture model, read via Browse model, fields match
6. A round-trip checklist: load from dispatch, render, mark items, generate report
7. The Bible section autocomplete returns ≥40 sections
8. Spec.json freshness check works against the locked Bible hash

Any AI's deliverable that fails the harness goes back for fixes. The harness is not in any AI's scope — it's mine.

### 2.6 — Recall existing dispatches

The two existing Codex dispatches (`20260428_200000_CLAUDE_to_CODEX_ledger_lint_build.md` and `20260428_200500_CLAUDE_to_CODEX_recall_and_review_ledger_spec.md`) are both superseded. I write a single recall message that voids both and points at the new build dispatch.

### 2.7 — Three new build dispatches

One per AI, each with:

- Reference to v2 spec
- Reference to `contracts.py` and `conventions.md`
- Exclusive file ownership list
- Forbidden file list ("do not touch these — they are owned by AI X")
- Contracts imported (specific dataclass names)
- Tests required
- Delivery format (impl report markdown + uncommitted code)
- Integration harness expectations
- Estimated LOC and time

---

## 3 — File ownership matrix (zero overlap)

### 3.1 — Claude Desktop owns

```
panda_ledger/
├── __init__.py                           [CD]
├── __main__.py                           [CD]
├── window.py                             [CD]
├── styles.py                             [CD]
├── INTEGRATION_TEST_HARNESS.py           [CD]
│
├── shared/
│   ├── __init__.py                       [CD]
│   ├── contracts.py                      [CD] ← FROZEN before dispatch
│   ├── conventions.md                    [CD] ← FROZEN before dispatch
│   ├── decision_model.py                 [CD]
│   ├── spec_loader.py                    [CD]
│   ├── decision_index.py                 [CD]
│   ├── lint_runner.py                    [CD]
│   ├── ipc.py                            [CD] ← client side; CC writes server
│   ├── atomic_write.py                   [CD]
│   └── logging_setup.py                  [CD]
│
├── capture/
│   ├── __init__.py                       [CD]
│   ├── capture_screen.py                 [CD]
│   ├── snippet_widget.py                 [CD]
│   ├── qa_pair_widget.py                 [CD]
│   ├── bible_picker.py                   [CD]
│   └── decision_writer.py                [CD]
│
├── browse/
│   ├── __init__.py                       [CD]
│   ├── browse_screen.py                  [CD]
│   ├── decision_detail.py                [CD]
│   └── trace_view.py                     [CD]
│
└── tests/
    ├── shared/                           [CD]
    ├── capture/                          [CD]
    └── browse/                           [CD]

workflows/tools/
├── pg_decision_index.py                  [CD]

workflows/decisions/
├── README.md                             [CD]
└── (initial directory structure)         [CD]

workflows/design/
├── PG_DESIGN_LEDGER_SPEC_v2.md           [CD] (already exists)
├── PG_LEDGER_PARALLEL_BUILD_PLAN_v1.md   [CD] (this file)
└── pg_design_spec.json                   [CD] (v2 update)
```

Total: ~3000 LOC + ~600 LOC tests. ~25 files.

### 3.2 — Codex owns

```
pg_design_lint/                           [CODEX — entire package]
├── __init__.py
├── __main__.py
├── lint.py
├── score.py
├── violations.py                         ← imports from contracts.py
├── report.py
├── rules/
│   ├── __init__.py
│   ├── base.py
│   ├── R01_forbidden_colors.py
│   ├── R02_off_palette_hex.py
│   ├── R03_native_dialogs.py
│   ├── R04_off_scale_spacing.py
│   ├── R05_off_scale_font_sizes.py
│   ├── R06_forbidden_font_families.py
│   ├── R07_forbidden_motion.py
│   ├── R08_vocabulary_lock.py
│   ├── R09_stale_file_references.py
│   ├── R10_section_header_divider.py
│   ├── R11_label_vcenter.py
│   ├── R12_slider_label_alignment.py
│   ├── R13_multiple_primaries.py
│   ├── R14_decision_citation.py
│   ├── R15_qss_styled_background.py
│   ├── R16_hardcoded_dimensions.py
│   ├── R17_inline_styles.py
│   ├── R18_off_scale_radius.py
│   ├── R19_empty_state_voice.py
│   ├── R20_todo_without_bug_id.py
│   ├── R21_spec_freshness.py
│   ├── R22_decision_schema.py
│   └── R23_per_state_inventory.py
└── tests/

workflows/tools/
├── pre_commit.py                         [CODEX modifies — adds R21 + Lint hooks]
├── pg_spec_freshness.py                  [CODEX]
└── lint_baseline_writer.py               [CODEX]
```

Total: ~2000 LOC + ~700 LOC tests. ~30 files.

### 3.3 — CC owns

```
panda_ledger/
├── verify/                               [CC — entire subpackage]
│   ├── __init__.py
│   ├── verify_screen.py
│   ├── checklist_widget.py
│   ├── reference_panel.py
│   ├── mockup_viewer.py                  ← QWebEngineView
│   └── pg_introspect.py                  ← IPC client extending shared/ipc.py
│
└── tests/
    └── verify/                           [CC]

panda_gallery/
├── ledger_bridge.py                      [CC] ← PG side of IPC; new file
└── (modifications to existing entry point to wire --ledger-bridge flag)
```

Total: ~2500 LOC + ~500 LOC tests + ~300 LOC PG-side bridge. ~10 files.

### 3.4 — Forbidden lists (defensive)

Every dispatch explicitly says: "Do NOT touch these files — they are owned by [other AI]."

- Codex's dispatch lists `panda_ledger/**`, `panda_gallery/ledger_bridge.py` as forbidden
- CC's dispatch lists `pg_design_lint/**`, `panda_ledger/capture/**`, `panda_ledger/browse/**`, `panda_ledger/shared/**`, `panda_ledger/window.py`, `panda_ledger/styles.py` as forbidden
- My own work plan lists `pg_design_lint/**`, `panda_ledger/verify/**`, `panda_gallery/ledger_bridge.py` as forbidden for me

---

## 4 — Build sequencing

### 4.1 — Phase 0 (mine, ~1–2 hours, BEFORE dispatch)

1. Update `pg_design_spec.json` with v2 fields
2. Write `panda_ledger/shared/contracts.py` (the frozen module)
3. Write `panda_ledger/shared/conventions.md`
4. Create directory structure for `panda_ledger/`, `pg_design_lint/`, `workflows/decisions/`
5. Write stub files at every interface point with ownership headers
6. Write `INTEGRATION_TEST_HARNESS.py`
7. Recall existing under-baked Codex dispatches
8. Write three new build dispatches
9. Send Codex dispatch immediately
10. Send CC dispatch (queued behind A48 + #131)

### 4.2 — Phase 1 (parallel, ~4–8 hours wall-clock)

All three AIs build simultaneously, no coordination needed:

- **Claude Desktop:** builds shell + Capture + Browse + shared/ + tests for those
- **Codex:** builds entire `pg_design_lint/` package + pre-commit hook integration + tests
- **CC (after A48 + #131 commit):** builds Verify tab + IPC bridge + tests

Each delivers an impl report when done. No commits.

### 4.3 — Phase 2 (mine, integration, ~30 min)

1. Pull all three deliverables into the working tree
2. Run `INTEGRATION_TEST_HARNESS.py`
3. Fix any contract drift (rare if Phase 0 was thorough)
4. Run the full pytest suite
5. Run the running PG app against a freshly built Ledger
6. Walk through one full decision capture → verify → sign-off cycle
7. Present Darrin a single bundle for commit-go

### 4.4 — Phase 3 (Darrin, commit-go)

1. Darrin runs the eye-test
2. Issues commit-go
3. Single git commit lands the entire system
4. Lint baseline is established
5. CLAUDE.md and WORKING_RULES_v1.md updated to reference the new tools

---

## 5 — Risk mitigations

### 5.1 — Contract drift

**Risk:** an AI changes a contract during build to make their code easier; integration breaks.

**Mitigation:** `contracts.py` has a hash check at the top of every dependent file:

```python
# CONTRACTS_HASH: a3f9e1b2  ← do not modify; verified at integration time
```

Integration harness verifies hashes match. Mismatch fails integration.

### 5.2 — One AI finishes much earlier than others

**Risk:** dead time wastes parallel advantage.

**Mitigation:** the early finisher's "extra" time goes to test coverage, edge cases, and documentation. No one is permitted to start work outside their assigned scope.

### 5.3 — One AI hits an unexpected blocker

**Risk:** Codex discovers Bible §6.22 doesn't quite fit a rule check; CC finds the IPC API needs a method not in the contract.

**Mitigation:** every AI has explicit instructions: "If you discover a contracts.py issue, DO NOT modify contracts.py. Stop, write a contract-amendment-request to your delivery report, deliver the rest, and Claude Desktop integrates the amendment in Phase 2."

### 5.4 — Dependency on running PG for Verify testing

**Risk:** CC can't test the IPC bridge without a running PG, but PG isn't released until A48 commits.

**Mitigation:** CC writes a mock IPC server in tests/. Real PG integration deferred to Phase 2 integration; the mock proves the protocol works.

### 5.5 — Files I forgot to assign

**Risk:** some file falls between cracks; no AI owns it.

**Mitigation:** the integration harness imports every expected module by name. If anything is missing, the harness fails immediately with a clear "module X expected at path Y not found" message. I patch the gap in Phase 2.

### 5.6 — Three AIs all running at once consume context

**Risk:** my own context window gets stretched coordinating three deliveries.

**Mitigation:** all three deliveries land in mailboxes I read at session start of the next chat. I don't try to coordinate live; I receive completed work asynchronously.

### 5.7 — Specs go stale during the build

**Risk:** during the ~6 hours of parallel work, Bible amendments or other spec changes slip in and invalidate something.

**Mitigation:** spec freezing announcement at dispatch time: "PG_DESIGN_BIBLE_v1.md, pg_design_spec.json, PG_DESIGN_LEDGER_SPEC_v2.md, and contracts.py are FROZEN until integration completes. No amendments to these files during the build window."

---

## 6 — Time budget

### 6.1 — Phase 0 (Claude Desktop)

| Task | Estimate |
|---|---|
| Update spec.json with v2 fields | 15 min |
| Write contracts.py | 30 min |
| Write conventions.md | 20 min |
| Create directories + stubs | 15 min |
| Write integration harness | 30 min |
| Recall + write three dispatches | 30 min |
| **Total Phase 0** | **2.5 hours** |

### 6.2 — Phase 1 (parallel)

| AI | Estimate |
|---|---|
| Claude Desktop (shell + Capture + Browse + shared) | 6 hours |
| Codex (Lint + rules + pre-commit) | 5 hours |
| CC (Verify + IPC bridge, after A48+131 ~tomorrow morning) | 5 hours |
| **Wall-clock Phase 1** | **~6 hours** (gated by slowest, but CC starts later) |

### 6.3 — Phase 2 (Claude Desktop integration)

| Task | Estimate |
|---|---|
| Pull deliverables, run harness | 15 min |
| Fix drift (if any) | 30 min |
| Full pytest suite | 5 min |
| Manual smoke test in running app | 20 min |
| Bundle for Darrin commit-go | 10 min |
| **Total Phase 2** | **~1.5 hours** |

### 6.4 — Total elapsed wall-clock

- If Phase 0 starts now (evening 2026-04-28): finishes ~midnight
- Phase 1 begins immediately for Codex and me; I work overnight
- CC's Phase 1 begins tomorrow morning after A48 + #131 commit
- All three Phase 1 deliveries arrive by tomorrow afternoon
- Phase 2 integration tomorrow afternoon
- Darrin's commit-go by tomorrow evening

**Roughly 18–24 wall-clock hours from approval to landed commit.**

---

## 7 — Success criteria

The plan succeeds if:

1. All three deliveries arrive without any AI having modified a file outside their ownership scope
2. The integration harness passes on first run (no contract drift)
3. The full pytest suite passes
4. Darrin can run the Ledger app, capture a decision, see it in Browse, run Verify against a dispatch, and produce a verification report — all in one session
5. Lint runs clean (or with documented baseline) on the codebase
6. No modifications to PG behavior outside the optional `--ledger-bridge` flag

If any of these fail, Phase 2 expands to fix; no Darrin intervention required unless the failure is architectural.

---

## 8 — What Darrin does

After approval of this plan, Darrin's involvement until commit-go:

1. **Approve the plan** (5 min — read this doc, give thumbs up)
2. **Wait** (~24 hours wall-clock; ~5 min of active attention to confirm nothing's blocked)
3. **Eye-test the integrated system** (~20 min — run Ledger, capture a decision, Verify a dispatch)
4. **Commit-go** (one chat message)

That's it. No mid-build interruptions, no per-AI question handling, no coordination.

---

## 9 — Approval gates

Before I dispatch:

- [ ] Darrin approves the parallel build plan (this document)
- [ ] Darrin confirms Phase 0 starts tonight (or specifies different start time)
- [ ] Darrin confirms scope: full v2 (Capture + Browse + Verify + Lint + IPC) vs tight v2 (Capture + Browse + Lint, defer Verify + IPC)
- [ ] Darrin confirms CC sequencing: Verify after A48 + #131, OR Verify deprioritizes #131
- [ ] Darrin confirms recall of existing Codex dispatches

---

## 10 — Summary diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PHASE 0 (Claude Desktop)                    │
│  spec.json v2 update                                                │
│  contracts.py FROZEN                                                │
│  conventions.md FROZEN                                              │
│  stub files + directories                                           │
│  INTEGRATION_TEST_HARNESS.py                                        │
│  three dispatches written                                           │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ (~2.5 hours, my work)
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         PHASE 1 (parallel)                          │
│                                                                     │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐         │
│  │ Claude Desktop │  │     Codex      │  │       CC       │         │
│  │                │  │                │  │  (after A48)   │         │
│  │  shell.py      │  │  Lint package  │  │  Verify tab    │         │
│  │  Capture/      │  │  23 rules      │  │  IPC bridge    │         │
│  │  Browse/       │  │  pre-commit    │  │  Mock server   │         │
│  │  shared/       │  │  freshness     │  │                │         │
│  │  ~3000 LOC     │  │  ~2000 LOC     │  │  ~2500 LOC     │         │
│  └────────────────┘  └────────────────┘  └────────────────┘         │
│                                                                     │
│             ALL BUILD AGAINST contracts.py (frozen)                 │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ (~6 hours wall-clock)
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  PHASE 2 (Claude Desktop integration)               │
│  Pull all three deliveries                                          │
│  Run INTEGRATION_TEST_HARNESS.py                                    │
│  Fix drift if any                                                   │
│  Manual smoke test                                                  │
│  Bundle for commit-go                                               │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ (~1.5 hours, my work)
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         PHASE 3 (Darrin)                            │
│  Eye-test                                                           │
│  Commit-go                                                          │
│  Single git commit lands the system                                 │
└─────────────────────────────────────────────────────────────────────┘

TOTAL: ~24 hours wall-clock from plan approval to landed commit.
TOTAL DARRIN TIME: ~30 min (approval + eye-test + commit-go).
```

---

## END OF PLAN

Status: ready for Darrin approval. After approval, Phase 0 begins immediately.
