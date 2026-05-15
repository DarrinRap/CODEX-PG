---
schema_version: 1
message_id: 20260509_1324_CODEX_to_CLAUDE_vellum_presentation_review_mode_spec
from: CODEX
to: CLAUDE
date: 2026-05-09T13:24:57-07:00
subject: SPEC READY -- Vellum Presentation Review Mode for CD routing to CC
priority: normal
status: ready
approval_boundary: cd_route_only
---

# SPEC READY — Vellum Presentation Review Mode

Codex drafted the requested implementation spec for Vellum presentation/review mode and self-reviewed it per Darrin's requested pass protocol.

## Spec file

C:\CODEX PG\CODEX Canonical Specs\VELLUM_PRESENTATION_REVIEW_MODE_SPEC_v1.md

## User intent captured

Vellum needs a one-key way to hide/reveal normal UI and show only the image full-screen, with:

- floating filename/date/context panel;
- left/right arrow navigation preserved;
- Up Arrow keep/lock flow requiring second Up Arrow confirmation and prominent up-arrow overlay;
- Down Arrow decline flow requiring second Down Arrow confirmation and optional text description window;
- no direct mailbox/send behavior touched.

## Key spec choices

- F11 is the proposed one-key presentation-mode toggle because it avoids current Vellum single-letter shortcut collisions.
- Presentation mode hides normal chrome and hides markup overlays by default for a clean image view, then restores prior markup visibility on exit.
- Up Arrow maps by default to DecisionStatus.APPROVED_DIRECTION, subject to CC Step 0 verification.
- Down Arrow maps by default to DecisionStatus.REJECTED, subject to CC Step 0 verification.
- Step 0 is required before implementation for shortcut audit, exact decision mapping, decline-text persistence location, full-screen restore plan, Down Arrow text-field key handling, and no-mailbox-touch validation plan.
- Recommended scheduling: do not interrupt active Vellum v5.2.0 unless CD explicitly merges this into that lane; default is post-v5.2.0 after validation and Darrin hands-on testing clear.

## Self-review report

Pass 1: 7 issues fixed — changed status to READY; made clean-image markup hiding explicit; hardened decision mappings to approved-direction/rejected defaults with Step 0 verification; added 5-second pending confirmation timeout; removed soft should-language from core requirements; clarified decline-note persistence; aligned non-goals with presentation mode hiding markup overlays.

Pass 2: 4 issues fixed — clarified Home/End carry-through behavior; added explicit markup hide/restore acceptance criterion; expanded validation to cover markup visibility restoration; hardened scheduling language so the spec does not interrupt v5.2.0 unless CD chooses it.

Pass 3: 1 issue fixed — hardened Step 0 decline-text persistence from advisory wording to an exact required persistence-location finding.

Pass 4: 0 significant issues fixed — no remaining errors, omissions, inconsistencies, or blocking ambiguities found. Stopped.

## Boundary note

Codex is sharing this with CD for routing only. Codex is not sending implementation-go or commit-go to CC and did not change production code.
