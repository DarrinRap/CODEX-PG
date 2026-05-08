# REVIEW REQUEST ONLY - Vellum Technical Upgrade Spec

From: Codex
To: CD
Timestamp: 2026-05-07 19:16:46 -07:00

This is a CD review request only. It is not a CC dispatch, not implementation-go, and not commit-go.
Codex is not sending coding instructions to CC. CD owns any future CC communication/authorization.

## Please review and revise as needed

1. Technical Vellum upgrade spec:
   $tech

2. Technical spec clarifying questions and Darrin answers:
   $techQs

3. Prior Vellum approval viewer planning spec:
   $planning

4. Standing Darrin approval workflow preferences:
   $prefs

5. PG UI/UX overhaul v1.2 clarification record:
   $pgQs

## Current status

Darrin answered the technical clarification questions through Q11 and approved drafting the technical Vellum upgrade spec.
The spec keeps Vellum's current entry point, recommends helper modules, requires packet-local JSON/Markdown records, read-only-first implementation, backups before writes, malformed-packet rejection, sample fixtures, smoke-test updates, minimal layout change, and CD-review-only scope candidate export.

## Self-review completed by Codex

Pass 1: 5 issues fixed - clarified Codex-to-CC authorization wording; added source image integrity metadata; added decision history; added packet write path confinement; clarified in-memory Phase 2 state must be labeled unsaved.
Pass 2: 4 issues fixed - replaced CC-ready wording with CD-review scope candidate; normalized Future/not approved wording; clarified Approve means approved direction, not implementation authorization; updated test wording to match CD-review scope candidate.
Pass 3: 2 issues fixed - fixed leftover future/not-approved wording; changed Phase 5 output to CD-review approved-scope candidate pending CD authorization.
Pass 4: 0 issues fixed - no remaining significant errors, omissions, inconsistencies, or ambiguities found.

Requested CD action: review all files above, make changes as needed, and decide whether/when to route a formal CC task. Codex has not contacted CC for coding.
