# TASK: Tester-Report Round-Trip v1 Spec — **CANCELLED 2026-04-25 15:30**

> **STATUS: CANCELLED — DO NOT EXECUTE.**
>
> Reason: realignment to PG_V4_MVP_PLAN.md scope. The Tester Report system is distribution-adjacent dev tooling, not v4.0 MVP scope. Per MVP plan §6.1 distribution work is deferred to v4.1. The existing pane workflow is sufficient for Darrin's solo dogfooding through v4.0 ship (2026-07-23).
>
> The brief at `C:\panda-gallery\workflows\audit\TESTER_REPORT_ROUNDTRIP_BRIEF_v1.md` is preserved for v4.1 dispatch — when Tier B HIPAA architecture work is greenlit, this brief feeds the v4.1 Codex spec.
>
> If Codex has already started reading inputs for this task, stop. Move on to the next task in `CODEX Inbox/` (UI shell mockup, dispatched 2026-04-25 15:35).
>
> Original task content preserved below for the audit trail.
>
> -- Claude

---

Generated: 2026-04-25 14:25:00 -07:00
From: Claude
To: Codex
Status: Response Requested (deliverable: spec doc)
Recommended tier: Extra-High
Sequencing: Defer until Pane UX v2 spec (`20260425_125500_CLAUDE_to_CODEX_TASK_instruction_pane_ux_v2_spec.md`) is complete. The Pane UX work touches `instruction_pane.py`, which is a candidate home for tester-side UI surfaces in this spec; sequencing prevents drift.

## Summary

Author a v1 architectural spec for an end-to-end tester-report round-trip system in Panda Gallery. Testers capture audio + screenshots during normal PG sessions, review and ship structured bundles to a cloud destination (Dropbox in v1), and the developer's Audit Module polls, ingests, and responds. Both sides track sent/received state in their own local databases. The cloud is a transport pipe; local DBs are the systems of record.

The brief that locks the goal lives at `C:\panda-gallery\workflows\audit\TESTER_REPORT_ROUNDTRIP_BRIEF_v1.md` — read it first, treat its §4 (Locked decisions) as inviolable, and surface its §6 (Open questions) explicitly in the spec for Darrin decision.

## Output

Spec doc at: `C:\CODEX PG\CODEX Canonical Specs\CODEX_TESTER_REPORT_ROUNDTRIP_v1_SPEC.md`

Shape per the brief's §9 (matches `CODEX_AM_v4_SPEC.md` skeleton): goal statement, same-binary-different-mode reminder, locked decisions, architecture + module breakdown, bundle lifecycle state machine, data shapes, pluggable transport interface (Dropbox v1 + brief eval of alternatives), bundle pipeline + redaction hook, polling + atomic-write trap, UX shape (anchored on brief §5), failure modes, open questions surfaced explicitly, Tier A → Tier B migration path sketched, smoke-test shape.

## Key constraints (also in brief §7)

- **Read-only on `C:\panda-gallery\`.** Output to `C:\CODEX PG\CODEX Canonical Specs\` per standing boundary.
- **Compose with shipped infrastructure** (`workflow_capture.py`, transcribe pipeline, transcript v2, AM v0/v0.1, codex_audit). Do NOT propose changes to those modules.
- **Tester-side code does NOT live in `audit_module/`.** Per `PG_TRUTH_v1.md`, AM is dev-only with a hard `--dev` gate. Propose a tester-side code home (likely `tester_reports/` peer module + `workflow_capture.py` extension); Darrin confirms during review.
- **Pluggable transport.** Dropbox v1, but the interface must accommodate Tier B HIPAA-compliant transport later as a config swap, not a rewrite. Brief evaluates Google Drive desktop / OneDrive / SMB as alternative v1 options (open question §6.11).
- **Scope is v1.** Tier B HIPAA architecture is sketched, not specified. Separate v2 spec dispatches when Darrin decides to fund the compliance work.

## Inputs to read

In recommended order (brief first, then existing infrastructure, then standing references):

1. `C:\panda-gallery\workflows\audit\TESTER_REPORT_ROUNDTRIP_BRIEF_v1.md` (the goal lock — read first, follow throughout)
2. `C:\panda-gallery\workflow_capture.py` (capture session lifecycle — likely tester-side code home)
3. `C:\panda-gallery\scripts\transcribe_latest.py` (transcribe subprocess pattern)
4. `C:\panda-gallery\PANDA_GALLERY_AUTOTRANSCRIBE_SPEC.md` (auto-transcribe v3.46+)
5. `C:\panda-gallery\PANDA_GALLERY_TRANSCRIPT_V2_SPEC.md` (transcript format — locked input)
6. `C:\panda-gallery\PANDA_GALLERY_COMPLIANCE_SPEC.md` (Stage 2 redaction context)
7. `C:\panda-gallery\codex_audit\` (existing package builder pattern)
8. `C:\panda-gallery\audit_module\` (AM v0/v0.1 surface; Reports section lands here on dev side only)
9. `C:\panda-gallery\BUGS.md` entries #134 (absolute-path redaction; this spec inherits) and #97 (`--dev` flag context)
10. `C:\panda-gallery\workflows\audit\PG_TRUTH_v1.md` (locked: AM is dev-only, harness paused, vocabulary unresolved)

## Approval Boundary

Spec authoring only. No implementation. Output stays in `C:\CODEX PG\`. Claude reviews the spec before it's surfaced to Darrin for `go` per generator+critic pattern. Implementation, if approved, will be a separate CC dispatch citing this spec.

— Claude
