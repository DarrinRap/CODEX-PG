# REVIEW RETURN - PAH Phase 2 Spec v0.2

From: Codex
To: CD
Timestamp: 
2026-05-07 21:00:58 -07:00

CD requested four scoped amendments before Darrin approval/CC dispatch. Codex incorporated them into v0.2.

Spec: `
C:\CODEX PG\CODEX Canonical Specs\CODEX_PAH_PHASE2_OBSERVABILITY_RESILIENCE_CC_SPEC_v0.2.md
`

Amendments incorporated:

1. Added `schema_version: 1` to health-details required fields.
2. Locked recovery journal retention to 1,000 events, rotate-on-write; removed vague 5 MB / whichever-is-easier wording.
3. Defined health-details access method as local-only `GET /health/details` on `127.0.0.1`, with Step 0 conflict check against startup/tray spec.
4. Added definition of PAH-related processes and command-line sanitization requirement.

Requested CD action: final review of v0.2 before any Darrin approval presentation or CC dispatch.

Boundary: PAH implementation remains paused. This is not implementation-go, commit-go, or CC dispatch.
