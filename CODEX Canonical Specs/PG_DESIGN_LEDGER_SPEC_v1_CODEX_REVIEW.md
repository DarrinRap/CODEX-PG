# PG Design Ledger Spec v1 - Codex Review

Review date: 2026-04-28
Reviewer: Codex
Source dispatch: `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\20260428_200500_CLAUDE_to_CODEX_recall_and_review_ledger_spec.md`
Primary reviewed file: `C:\panda-gallery\workflows\design\PG_DESIGN_LEDGER_SPEC_v1.md`

## 1. Summary Verdict

**Hold for major rework before implementation.**

The lint concept is sound and worth building, but v1 should not be used as implementation authority. There are two blockers:

1. `C:\panda-gallery\workflows\design\PG_DESIGN_LEDGER_SPEC_v2.md` already exists and self-identifies as "supersedes v1" at lines 1-7. It also says v1's three-browser-applet architecture has a critical filesystem flaw at v2 lines 11-15. The dispatch asks for v1, so the authority chain is currently inconsistent.
2. v1 depends on static HTML applets opened via `file://` talking to Filesystem MCP for draft persistence, decision search, verification writes, lint execution, and snapshot management (v1 lines 411-412, 624-628, 648, 661-664, 682). A browser applet cannot use Claude Desktop's MCP tools directly. That turns several core v1 requirements into non-implementable requirements unless a native app or explicit local sidecar is added.

Recommendation: do not build from v1. Either re-dispatch against v2 as the new base, or explicitly demote/archive v2 and amend v1 with a real filesystem/runtime architecture. The `pg_design_lint.py` subset can proceed after the authority conflict, JSON sync, severity model, baseline policy, and rule definitions are tightened.

## 2. Contradictions Found

- **Authority conflict: v1 dispatch vs v2 file.** The dispatch identifies `PG_DESIGN_LEDGER_SPEC_v1.md` as primary authority, but `PG_DESIGN_LEDGER_SPEC_v2.md` says "supersedes v1" and changes the architecture from applets to a native Python app (v2 lines 1-7, 11-15). This must be resolved before any build.

- **Lifecycle section reference is wrong.** v1 line 71 says lifecycle states are formalized in section 3.5, but the lifecycle state machine is in section 2.4 at lines 260-309. Section 3.5 is Capture visual design at lines 417-428.

- **Commit order conflicts with PG process.** The lifecycle diagram says "CC implements, commits with reference" before Lint and Verify (v1 lines 59-65), but Verify is defined as after CC delivery and before commit-go (v1 lines 593-595, 677-685), and `CLAUDE.md` forbids commits unless Darrin says "commit" or "go" (CLAUDE.md commit rules). Reorder to implementation report -> Verify -> commit-go -> pre-commit lint -> commit -> shipped.

- **`retired` exists in prose but not JSON.** The glossary includes `retired` as a lifecycle state (v1 lines 86-87), and the state machine has `retired` (v1 lines 293-307). `pg_design_spec.json.ledger_decision_statuses` only lists proposed, locked, dispatched, shipped, verified, superseded (JSON lines 287-294).

- **JSON "single source of truth" wording conflicts with Bible authority.** v1 calls JSON the shared single source for all three tools (v1 lines 31, 136-139), but also says the Bible is the human source and JSON is extracted/regenerated from it (v1 lines 138, 154-156). The Bible itself lists source-of-truth files in order of authority at Bible lines 27-35. Use "Bible is canonical; JSON is generated machine-readable artifact."

- **Strict mode contradicts the severity table.** v1 says warnings do not block (lines 472-473), then says `--strict` promotes warnings to errors (line 539), and pre-commit runs strict changed-only (line 570). That makes warning rules block commits despite the table saying they do not.

- **Applet version mismatch in JSON.** v1 file layout names `ledger_verify_v1.html` (v1 line 122), but `pg_design_spec.json` lists `ledger_verify_v2.html` as a consumer (JSON line 11). Neither ledger applet exists in the current applets directory.

- **State-consistency lint is promised but not specified as a rule.** v1 line 309 says Lint verifies lifecycle state consistency on every commit. R01-R20 do not include a state-machine consistency rule beyond decision citation validity (R14 at v1 line 489).

- **Suggested questions are specified but absent in JSON.** Capture requires `pg_design_spec.json.bible_sections[].suggested_questions` (v1 line 395), but the current JSON `bible_sections` entries contain only `id` and `title` (JSON lines 207-275).

## 3. Gaps Identified

- **No realistic v1 persistence model.** Capture save, autosave, lock/promote, decision search, supersession updates, Verify report saving, and verification timestamp writes all assume filesystem access from a static applet. v1 needs native Python, a local server, or a clearly specified sidecar.

- **No baseline/migration policy for existing violations.** The codebase already contains many patterns a design lint would flag, including native `QFileDialog`/`QColorDialog` usage and hardcoded geometry. A blocking pre-commit hook without a baseline will stop unrelated commits. Follow the existing dispatch-lint precedent: current `pre_commit.py` keeps dispatch lint warn-only during Phase A (pre_commit.py lines 125-135).

- **No JSON generator or freshness check.** v1 says the JSON is regenerated from the Bible (v1 line 154) but does not define the generator, canonical extraction rules, version bump ownership, or a `--check` mode. Risk mitigation line 880 admits this is future/manual for now.

- **No decision ID allocation safety.** "max(NNN) + 1" (v1 line 375) can collide if two sessions lock decisions in parallel or if a draft is promoted after another draft. Need lockfile or atomic create semantics.

- **No rule test corpus shape.** Phase 1 requires tests for every rule (v1 line 831), but the spec does not define fixtures, expected JSON output, suppression fixtures, or golden reports.

- **No scope filter policy.** The linter targets `.py` files (v1 line 444), but rules will encounter tests, scripts, debug probes, generated files, historical docs, and old mailboxes. Need explicit include/exclude defaults and per-rule target scopes.

- **No suppression hygiene.** Inline and file-level exemptions require reasons (v1 lines 515-529), but there is no rule for invalid rule IDs, stale exemptions, unused exemptions, missing reasons, or expiration/review.

- **No CI story.** The open question asks about CI (v1 lines 586, 922), but the spec should decide at least Phase A: local pre-commit plus GitHub Actions report-only, then blocking after baseline burn-in.

- **No integration contract with existing `pg_dispatch_lint.py`.** Existing dispatch lint has its own frontmatter vocabulary and parser (pg_dispatch_lint.py lines 53-69). Ledger decision files and dispatch references should either reuse or explicitly extend those conventions.

## 4. Ambiguity Flags

- **"Screen" in R13.** A Python file can contain multiple screens/classes, and a screen can span multiple files. "More than one primary per screen" needs a concrete ownership boundary.

- **"New code" in R14.** v1 says superseded decisions are warning if cited in existing code and error if cited from new code (v1 lines 324-327, 787-792). Define whether "new" means staged diff lines, files added after baseline, or commits after a cutoff.

- **R05 font units.** `setPointSize(N)` is points, while `font-size: Npx` and the JSON type scale are pixels (v1 line 480; JSON lines 85-93). The rule needs separate `size_pt` and `size_px` policy or it will misfire on HiDPI systems.

- **R01 pure black.** The Bible forbids pure black as a surface except splash (Bible lines 311-312), but existing image/radiograph/letterbox fills use `#000000`. R01 should check role/context, not every black literal.

- **R04 spacing allows no zero.** JSON spacing scale lacks `0` (JSON lines 118-129), but Qt layouts commonly use zero margins/spacing intentionally. Add `0` as an allowed structural value or define when it is permitted.

- **R16 hardcoded dimensions.** The rule as written would flag legitimate component grammar values like 1px dividers, 26px status bars, 28px buttons, fixed rail widths, and test resize sizes. It needs to distinguish component constants from resizable-window/default-size policy.

- **Decision citation wildcard.** The markdown link format uses `DECISION_023_*.md` (v1 line 317). Wildcards are not normal clickable file links and make validation fuzzy. Prefer exact path after lock plus bare `DECISION_NNN` before lock.

- **"Verify can run assertions."** The sample assertion block references live Python objects (v1 lines 244-253), but an HTML applet cannot execute those against a running Qt app without a Python sidecar/native app.

- **Snippet vs snapshot.** v1 defines visual snippets (lines 83, 361-369) and snapshot baselines (lines 93, 658-665). They are distinct but close enough that storage, naming, and lifecycle should be clearer.

## 5. Implementability Concerns Per Rule

| Rule | Assessment | Notes |
|---|---|---|
| R01 Forbidden colors | Implementable with amendments | Regex/string scan works, but pure black must be context-aware: surface vs image/letterbox/splash. Include RGB/RGBA forms, QColor names, and token allowlists. |
| R02 Off-palette hex | Implementable | Good warning rule. Needs allowed token set from JSON, case normalization, optional ignore for docs/tests, and handling for RGBA strings. |
| R03 Native Qt dialogs | Implementable, expand list | AST import/name/call detection is strong. Include `QColorDialog`, `QFontDialog`, `QPrintDialog`, `QProgressDialog`, and any `QDialog` subclasses if native/light. Current code has `QColorDialog` in `panels.py`. |
| R04 Off-scale spacing | Implementable for literals only | Direct calls are easy. Add `0` and distinguish layout margins from app-shell grid constants. Variables need best-effort resolution or info findings only. |
| R05 Off-scale font sizes | Needs unit clarification | Point sizes and CSS pixels are not interchangeable. Split Qt point-size policy from CSS pixel policy before shipping. |
| R06 Forbidden font families | Implementable | Check `QFont(...)`, QSS `font-family`, and `setFont` where literals are visible. Allow fallback families and font database aliases. |
| R07 Forbidden motion patterns | Implementable | Regex plus AST checks for `QEasingCurve` values. Add Qt easing names like `OutBack`, `OutBounce`, `InElastic`, not just prose words. |
| R08 Vocabulary lock | Implementable with sink filtering | Only user-facing strings should count: `setText`, `setWindowTitle`, menu/action labels, tooltips, placeholders. Do not flag identifiers, class names, comments, or legacy `TemplateLayout` code names. |
| R09 Stale file references | Implementable | Better as info. Needs configured stale-reference list and should scan comments/docs separately from code strings. |
| R10 Section header without divider | Heuristic only | Ship as info first. Promote only when detecting known helpers/patterns, otherwise it will create false positives. |
| R11 Label without VCenter | Heuristic only | Keep info. Adjacency in Qt layouts is hard to infer reliably without deeper layout modeling. |
| R12 Slider label not right-aligned | Heuristic only | Warning is probably too strong until the rule recognizes existing slider-row helpers. Start info/warn-on-known-patterns. |
| R13 Multiple primary buttons | Needs boundary definition | Counting per file is unsafe. Count per widget class/screen container, or require explicit screen annotations/properties. |
| R14 Decision citation validity | Implementable with decision index | Needs `workflows/decisions` parser/cache, baseline policy for old citations, exact-path rules, and behavior when no decisions exist yet. |
| R15 WA_StyledBackground fallback | Implementable as warning | Useful, but heuristic. Detect `Qt.WA_StyledBackground` and `Qt.WidgetAttribute.WA_StyledBackground`; avoid flagging widgets with custom `paintEvent` that intentionally paints all pixels. |
| R16 Hardcoded dimensions | Needs rewrite | Current wording is too broad. Limit blocking to top-level/resizable window default/minimum sizing. Component constants should need names/comments, not blanket warnings. |
| R17 Inline styles | Implementable as info | Good migration signal. Existing PG uses inline styles heavily, so keep non-blocking and aggregate by module. |
| R18 Off-scale radius | Implementable | Check QSS border-radius. Add permitted `0`, `50%`, and token equivalents for circular avatars/pills. |
| R19 Empty states | Heuristic only | Info is appropriate. It needs known empty-state container/string patterns and should not block. |
| R20 TODO/FIXME without bug ID | Implementable | Straightforward comment scan. Decide whether `#NNN`, `BUGS.md #NNN`, and GitHub issue links all satisfy it. |

## 6. Additional Rules Suggested

- **R03 expansion: all native dialogs.** Existing code uses `QColorDialog` in `panels.py`; R03 lists `QInputDialog`, `QMessageBox`, `QFileDialog`, and `QErrorMessage` only. This would miss a real dark-dialog violation.

- **Resizable-surface compliance rule.** Add a rule for Bible section 13.1-13.7: top-level windows/dialogs should have computed min size, default size policy, QSettings persistence, multi-monitor sanity check, and reset path. R16 only catches hardcoded dimensions; it does not verify the positive requirements.

- **Visual-dispatch metadata rule in `pg_dispatch_lint.py`.** Bible section 14.6 requires `visual_verification` blocks for visual changes. This belongs in dispatch lint, not design lint.

- **Mode-zone color locality.** Bible non-negotiable #6 says mode-zone color appears only in active module-tab underline and `.sb-mode` status-bar label (Bible line 1202). No R01-R20 rule covers that semantic misuse.

- **Mono misuse.** Bible non-negotiable #3 says mono is for precision data only, not prose/buttons/headings (Bible line 1199). No current rule catches broad mono misuse.

- **Dynamic counts on second line.** Inviolable Rule #21 requires count labels to be on a second line. No current rule catches inline count labels like `All (12)` in user-facing strings.

- **Suppression hygiene.** Add a meta-rule for invalid `pg-lint:allow` syntax, missing reason, unknown rule ID, unused allow, unclosed allow-block, or file-level allow without audit reason.

- **Spec freshness check.** Add `pg_design_spec_check.py` or a `pg_design_lint --check-spec` mode that verifies JSON freshness against Bible version and generator metadata before other rules run.

## 7. Open Question Answers

1. **Heuristic rule severity (R10/R11):** default both to `info`. Allow targeted subcases to become `warning` only when the detector is precise. Do not block commits on broad layout heuristics during v1.

2. **Auto-fix output format:** use unified diff for machine-applicable fixes, with human text around it. I would split flags: `--fix-suggestions` for prose suggestions, `--fix-diff` for unified diff suitable for `git apply`.

3. **Block-level exemption syntax:** yes, worth it for multi-line QSS and legacy transition blocks. Syntax should require rule IDs and reason on the opening line, require an explicit end marker, and error on unclosed or unused blocks.

4. **CI beyond pre-commit:** yes, but phased. Phase A: GitHub Actions report-only full-repo lint artifact plus local pre-commit changed-only. Phase B: block on new error-level violations after baseline. Phase C: optionally strict/blocking once false positives are under control.

5. **Rule execution order:** output should be deterministic R01-R20, but implementation should use dependency-driven prepasses first: load JSON once, parse AST once per file, build comments/strings/QSS indexes, build decision index once. Rules then consume shared context and report in stable order.

6. **Score formula:** `100 - 5e - w - 0.2i` is okay for a trend toy but too forgiving as a quality signal. Keep gate status separate from score: any error means "non-compliant" regardless of score. Suggested scoring: cap max score at 89 if any error exists, subtract about 10 per error, 2 per warning, 0.25 per info, and normalize or bucket for file size so large files are not unfairly punished.

7. **Performance target:** changed-only under 2 seconds is achievable for typical commits if AST parsing, JSON load, decision index, regex compilation, and git diff are all cached/precomputed once. It is not achievable if each rule independently reads the spec, scans the decisions directory, or shells out. Full repo under 10 seconds is realistic for static rules, not for snapshot/pixel-diff work.

Additional discovered questions:

- Is `PG_DESIGN_LEDGER_SPEC_v2.md` the real implementation base now? If yes, re-dispatch against v2 and archive v1.
- Should legacy violations be grandfathered through a baseline file, or should any touched file be required to fully clean up before commit?
- Should tests, debug scripts, docs, generated files, and archived mailboxes be linted by default?
- Who owns the Bible-to-JSON generator, and what exact command verifies freshness?
- Should decision IDs remain `NNN` or move to four digits as v2 proposes?

## 8. Suggested Amendments

- **Authority:** At v1 line 3, either mark v1 superseded by v2 or delete/archive v2. The repo cannot contain a self-superseding v2 while dispatches cite v1 as primary.

- **Architecture:** Replace v1 lines 27-31, 411-412, 624-628, 648, 661-664, and 682 with a native PySide6 app or explicit local sidecar architecture. If v2 is accepted, use v2's native app model.

- **Lifecycle:** Replace v1 lines 53-68 with: Capture locks decision -> dispatch cites decision -> CC/Codex implements and reports -> optional lint dry-run -> Verify before commit-go -> Darrin issues commit-go -> pre-commit lint runs -> commit created -> status becomes shipped -> Darrin live verifies -> status becomes verified.

- **Bad section ref:** Change v1 line 71 from section 3.5 to section 2.4.

- **JSON authority wording:** Rewrite v1 lines 136-156 to say: "Bible is canonical; `pg_design_spec.json` is generated machine-readable projection; generator command and freshness check are required before tools trust it."

- **Lifecycle statuses:** Add `retired` to `pg_design_spec.json.ledger_decision_statuses` after JSON line 293, or remove `retired` from v1 line 86 and the state machine. Prefer adding it.

- **Suggested questions:** Add `suggested_questions` arrays to JSON `bible_sections`, or remove the Capture requirement at v1 line 395 until the generator supplies them.

- **Rule severity/pre-commit:** Reconcile v1 lines 472-473, 539, and 570. Recommended: pre-commit blocks error-level findings only; `--strict` is CI/manual. During baseline Phase A, pre-commit should block only new errors, not historical warnings.

- **Rule amendments:** Update R03 to include all native dialogs; update R04/R18 allowed values with `0` and percent/pill cases; rewrite R05 unit handling; narrow R16 to resizable windows/default sizing; set R10/R11/R12/R19 to info until calibrated.

- **Decision citation:** Replace wildcard markdown link at v1 line 317 with exact path once locked and bare `DECISION_NNN` for pre-lock references.

- **Pre-commit mutation:** Reconsider v1 line 744 auto-staging generated `DECISIONS.md` from inside pre-commit. Safer pattern: generator runs in check mode and tells the user to run a separate update command, or the commit wrapper runs the generator before staging.

- **JSON consumer path:** Fix JSON line 11 to match the actual intended Verify app name/version after resolving v1 vs v2.

- **Build phase:** Change Phase 1 line 827 from "Build all 20 rules" to "Build core blocking rules first (R01, R03, R08, R14) plus report-only baseline for the rest"; then promote rules after false-positive review.

Bottom line: the project is valuable, but v1 is not stable enough to build. The fastest safe path is to make v2 the authority, preserve this lint review's rule-level amendments, and issue the implementation dispatch only after the architecture and JSON sync model are locked.
