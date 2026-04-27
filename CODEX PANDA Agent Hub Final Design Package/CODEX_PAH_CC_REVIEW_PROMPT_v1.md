# Prompt For Claude Code / CC: Review PANDA Agent Hub Final Spec and UX Mockups

Please review the complete PANDA Agent Hub (PAH) design package from Codex.

This is a design/spec review only. Do not implement code. Do not modify PAH runtime files. Do not write to `C:\panda-gallery`. Do not run live headless Claude Code tasks, paid API calls, SMS sends, installs, commits, or pushes.

## Context

Project name: **PANDA Agent Hub**

Short name: **PAH**

Purpose:

PAH is intended to streamline and automate parallel AI-assisted development with minimal Darrin input. It should coordinate Codex, Claude Desktop, Claude Code / CC, and future agents through a local-first control plane.

Darrin's governance rule:

- Darrin is not the right person to answer low-level technical architecture questions.
- Codex, Claude Desktop, and Claude Code / CC should vote, decide, and recommend on technical details.
- Darrin will generally follow the agent recommendation.
- Darrin must be consulted on UX appearance/functionality, dental/product judgment, clinical/dental correctness, phone/SMS interruption tolerance, safety boundaries, credentials/cost, external communication, writes to `C:\panda-gallery`, commits/pushes/publishing, and other protected actions.

Current implementation boundary:

- No PAH app implementation is approved yet.
- The current request is to review the spec and mockups, identify errors, and recommend improvements before Darrin approves coding.

## Primary Files To Review

Final design spec:

`C:\CODEX PG\CODEX PANDA Agent Hub Final Design Package\CODEX_PAH_FINAL_DESIGN_SPEC_v1.md`

Integration/access research:

`C:\CODEX PG\CODEX PANDA Agent Hub Final Design Package\CODEX_PAH_INTEGRATION_ACCESS_RESEARCH_v0_2.md`

UX mockup HTML:

`C:\CODEX PG\CODEX PANDA Agent Hub Final Design Package\CODEX_PAH_UX_MOCKUPS_v1.html`

Screenshot manifest:

`C:\CODEX PG\CODEX PANDA Agent Hub Final Design Package\CODEX_PAH_SCREENSHOT_MANIFEST_v1.md`

Machine screenshot manifest:

`C:\CODEX PG\CODEX PANDA Agent Hub Final Design Package\CODEX_PAH_SCREENSHOT_MANIFEST_v1.json`

Existing Codex design review:

`C:\CODEX PG\CODEX PANDA Agent Hub Final Design Package\CODEX_PAH_DESIGN_REVIEW_6C_BIBLE_v1.md`

Screenshot folder:

`C:\CODEX PG\CODEX PANDA Agent Hub Final Design Package\CODEX mockup screenshots`

## Important Prior Review Findings Already Patched

Codex patched the spec after a deep review. Please verify these are actually resolved and identify any remaining problems:

1. `thread_status: waiting_on_darrin` is now defined in Message Schema v1.
2. Ambiguous `local_codex_pg_write` was renamed to `codex_workspace_write_allowed`.
3. Write-capable approval boundaries now require explicit path roots through `write_scope`.
4. Headless Claude Code adapter now requires restrictive `--tools`, strict MCP isolation, settings isolation, temporary worktree, and command preview capture.
5. Approval record schema now defines scope, paths, command/provider, budget, expiry, one-time use, revocation, and hash binding.
6. PAH is router-only in v1 and not addressable through `PAH Inbox`.
7. Duplicate message IDs with different content hashes are quarantined as provenance conflicts.
8. `cross_check` now has payload fields and an auto-resolution rule.
9. Quarantine now requires atomic move, sidecar, tombstone, stable reason codes, and preservation of original bytes/hash.

## Requested Review

Please perform a rigorous design review of the entire PAH package.

Prioritize:

- correctness
- safety
- implementation practicality
- schema completeness
- routing/provenance integrity
- headless Claude Code risk
- MCP/hook sequencing
- notification/SMS risk
- Darrin decision queue clarity
- whether the UX supports the intended workflow
- whether the spec is concrete enough to start coding after Darrin approval

Please especially look for:

- contradictions between sections
- undefined fields or enums
- ambiguous names
- unsafe defaults
- missing approval gates
- paths or folder names that could be confused
- places where PAH might accidentally spoof agent provenance
- places where a bad/malformed message could poison refresh loops
- places where duplicate messages, replay, or restart could retrigger actions
- places where live Claude Code/Codex adapter work could bypass Darrin
- UX elements that violate Panda Gallery design doctrine
- anything missing from the acceptance criteria
- anything likely to become expensive, brittle, or risky to implement

## UX Review Instructions

Please review both:

- the static HTML mockup
- the rendered screenshots

Use the PG design doctrine and 6 C's where relevant:

- Correct
- Complete
- Clear
- Clean
- Checkable
- Contextual

For UX, please judge whether PAH feels like:

- a clinical development cockpit
- dense but readable
- operational rather than decorative
- clear about what needs Darrin
- clear about what agents can decide
- safe around protected actions

Please flag:

- unclear labels
- overcrowding
- bad information hierarchy
- missing expected controls
- misleading disabled/enabled states
- any workflow that would annoy Darrin or create too much interruption

## Output Format

Please respond with:

1. **Verdict**
   - approve
   - approve with changes
   - request changes

2. **Top Findings**
   - order by severity
   - include file path and line number when possible
   - use P0/P1/P2/P3 priority labels
   - explain why the issue matters
   - suggest the exact fix

3. **Schema and Routing Review**
   - message schema
   - participant registry
   - Darrin queue triggers
   - cross_check / counter_proposal / escalation
   - approval records
   - idempotency and quarantine

4. **Claude Code / Adapter Safety Review**
   - headless pilot
   - MCP
   - hooks
   - Remote Control / Dispatch assumptions
   - Codex adapter assumptions

5. **UX Review**
   - screenshots/mockup
   - 6 C's
   - PG Design Bible/doctrine fit
   - recommended improvements

6. **Implementation Readiness**
   - what must be fixed before coding
   - what can wait
   - recommended first implementation milestone
   - who should own which pieces: Codex vs CC vs Claude Desktop

7. **Out-of-the-box Enhancements**
   - anything that would make PAH substantially better at coordinating parallel development
   - only include ideas that preserve safety and low Darrin burden

## Expected Ownership Question

Darrin asked whether Codex or CC should code this.

Current Codex recommendation:

- Codex should build the PAH core because it lives under `C:\CODEX PG` and is primarily a local coordination/dashboard app.
- CC should review schema, safety gates, routing, lint integration, and any Claude Code bridge work before live use.
- CC should own or explicitly approve any implementation path touching `C:\panda-gallery`.

Please agree, disagree, or refine this ownership split.

