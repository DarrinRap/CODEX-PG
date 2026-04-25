# CODEX Audit Issue Schema v1

Generated: 2026-04-24

Status: Codex canonical draft for PG Testing + Audit MVP v1.

Scope: defines the output of AI issue extraction and the human review/approval/email/archive lifecycle. Issues must link to session package evidence IDs from `CODEX_SESSION_PACKAGE_SCHEMA_v1.md`.

## Goals

- Convert packaged tester sessions into reviewable, evidence-linked issues.
- Preserve AI suggestions separately from reviewer edits and final approved text.
- Make approval, email delivery, closure, and archive records searchable and auditable.
- Support local prototype first, then backend/database implementation.

## Non-Goals

- No provider-specific AI API schema.
- No live email sending requirement in v1 local prototype.
- No permission to process real PHI without a compliance addendum and explicit decision.

## Issue Extraction Result

File: `audit_issue_extraction_v1.json`

```json
{
  "schema": "pg.audit_issue_extraction.v1",
  "schema_version": 1,
  "extraction_id": "extract_20260424_201500_b43a",
  "package_id": "pkg_20260424_201255_8f3b2a",
  "session_id": "session_20260424_194422",
  "run_id": "run_20260424_194435",
  "created_at": "2026-04-24T20:15:00-07:00",
  "created_by": {
    "type": "ai_model",
    "provider": "provider_name",
    "model": "model_name",
    "prompt_version": "pg.audit_extract.prompt.v1"
  },
  "issues": [],
  "dedupe_groups": [],
  "warnings": []
}
```

## Audit Issue Object

```json
{
  "issue_id": "iss_20260424_201500_0001",
  "package_id": "pkg_20260424_201255_8f3b2a",
  "session_id": "session_20260424_194422",
  "run_id": "run_20260424_194435",
  "title": "Region capture discard did not remove evidence reference",
  "summary": "The tester discarded a manual region capture, but the step still displayed the removed evidence reference.",
  "category": "evidence_integrity",
  "priority": "P1",
  "confidence": 0.82,
  "status": "needs_review",
  "source_steps": [1],
  "evidence_ids": ["ev_region_0001", "ev_step_auto_0001"],
  "transcript_refs": ["tr_0003"],
  "observed_behavior": "What the tester saw or what the evidence shows.",
  "expected_behavior": "What should have happened.",
  "impact": "Why this matters for PG quality, approval speed, or audit integrity.",
  "suggested_response": {
    "subject": "Testing finding: evidence reference after discard",
    "body_markdown": "Concise draft response for the shared team email.",
    "tone": "clear_direct"
  },
  "reviewer": {
    "assigned_to": null,
    "reviewed_by": null,
    "reviewed_at": null,
    "reviewer_notes": null,
    "edited_title": null,
    "edited_summary": null,
    "edited_response_markdown": null
  },
  "lineage": {
    "created_by_model": true,
    "model_reasoning_summary": "Short, non-chain-of-thought summary of evidence basis.",
    "dedupe_group_id": null,
    "supersedes_issue_ids": [],
    "related_issue_ids": []
  },
  "audit": {
    "created_at": "2026-04-24T20:15:00-07:00",
    "updated_at": "2026-04-24T20:15:00-07:00",
    "events": []
  }
}
```

## Categories

| Category | Use When |
| --- | --- |
| `functional_bug` | Feature behaves incorrectly. |
| `ui_ux` | Layout, clarity, discoverability, visual polish, or interaction issue. |
| `workflow_break` | Tester cannot complete intended workflow or is blocked. |
| `evidence_integrity` | Screenshots, transcript, results, package, or links are wrong/missing/stale. |
| `performance` | Lag, slow processing, excessive resource use. |
| `stability` | Crash, hang, traceback, shutdown/runtime error. |
| `accessibility` | Keyboard, focus, contrast, screen-size, or assistive workflow issue. |
| `documentation` | Spec, handoff, instruction, or user-facing text mismatch. |
| `compliance_privacy` | PHI, retention, access control, transmission, logging, or redaction concern. |
| `test_authoring` | Test step is ambiguous, unobservable, too broad, or incorrectly structured. |
| `unknown` | Use only when evidence is real but category is unclear. |

## Priority

| Priority | Meaning |
| --- | --- |
| `P0` | Blocks safe use, causes data loss/privacy exposure, or prevents audit workflow from functioning. |
| `P1` | High-impact bug or integrity failure that should be addressed before MVP use. |
| `P2` | Meaningful issue with workaround; should be scheduled. |
| `P3` | Polish, clarity, or low-risk improvement. |

Priority rules:

- Evidence integrity failures are at least `P1` if they can mislead approval or archive search.
- PHI exposure or upload of unapproved real data is `P0`.
- Cosmetic UI issues are usually `P3` unless they block tester completion.

## Status Lifecycle

| Status | Meaning |
| --- | --- |
| `needs_review` | AI-created or imported issue awaiting PG review. |
| `in_review` | A reviewer has opened or assigned the issue. |
| `approved` | Reviewer approved the issue and response for communication/archive. |
| `changes_requested` | Reviewer wants AI/person to revise issue or draft response. |
| `rejected` | Reviewer decided this is not a valid issue. |
| `deferred` | Valid but intentionally postponed. |
| `email_queued` | Approved response is queued for shared team email. |
| `email_sent` | Email delivery succeeded. |
| `email_failed` | Email delivery failed; error record required. |
| `closed` | Issue workflow is complete. |
| `archived` | Immutable archive/search record has been written. |

Allowed happy path:

```text
needs_review -> in_review -> approved -> email_queued -> email_sent -> closed -> archived
```

Allowed alternatives:

```text
needs_review -> rejected -> archived
needs_review -> deferred -> archived
in_review -> changes_requested -> needs_review
approved -> email_failed -> email_queued
```

## Review Event Object

Every material state change appends an event to `audit.events[]`.

```json
{
  "event_id": "evt_20260424_201700_0001",
  "event_type": "status_changed",
  "actor": {
    "actor_type": "human",
    "display_name": "Darrin",
    "email": null
  },
  "created_at": "2026-04-24T20:17:00-07:00",
  "from_status": "needs_review",
  "to_status": "approved",
  "note": "Approved after title edit.",
  "diff_summary": "Title shortened; response draft edited."
}
```

Event types:

- `created`
- `assigned`
- `opened`
- `field_edited`
- `status_changed`
- `evidence_added`
- `evidence_removed`
- `comment_added`
- `email_queued`
- `email_sent`
- `email_failed`
- `closed`
- `archived`

## Approval Record

```json
{
  "approval_id": "appr_20260424_201800_0001",
  "issue_id": "iss_20260424_201500_0001",
  "approved_by": {
    "display_name": "Darrin",
    "email": null
  },
  "approved_at": "2026-04-24T20:18:00-07:00",
  "approved_title": "Evidence reference remains after discard",
  "approved_summary": "Reviewer-approved issue summary.",
  "approved_response_markdown": "Reviewer-approved team response.",
  "evidence_ids": ["ev_region_0001", "ev_step_auto_0001"],
  "approval_notes": "Ready to send."
}
```

## Email Delivery Record

```json
{
  "email_id": "email_20260424_201900_0001",
  "issue_id": "iss_20260424_201500_0001",
  "approval_id": "appr_20260424_201800_0001",
  "provider": "not_configured_local_prototype",
  "shared_inbox": "team@example.invalid",
  "to": ["team@example.invalid"],
  "cc": [],
  "subject": "Evidence reference remains after discard",
  "body_markdown": "Approved response body.",
  "state": "draft_only",
  "queued_at": null,
  "sent_at": null,
  "provider_message_id": null,
  "error": null
}
```

Email states:

- `draft_only`
- `queued`
- `sent`
- `failed`
- `cancelled`

## Archive Search Record

File option for local prototype: JSONL records under a Codex-owned archive folder.

```json
{
  "schema": "pg.audit_archive_record.v1",
  "archive_id": "arch_20260424_202000_0001",
  "issue_id": "iss_20260424_201500_0001",
  "package_id": "pkg_20260424_201255_8f3b2a",
  "session_id": "session_20260424_194422",
  "run_id": "run_20260424_194435",
  "closed_at": "2026-04-24T20:20:00-07:00",
  "closed_by": "Darrin",
  "close_reason": "sent_to_team",
  "title": "Evidence reference remains after discard",
  "summary": "Final approved summary.",
  "category": "evidence_integrity",
  "priority": "P1",
  "status": "archived",
  "evidence_ids": ["ev_region_0001", "ev_step_auto_0001"],
  "search_text": "normalized searchable text from title summary approved response notes",
  "tags": ["region-capture", "manual-screenshot", "discard"],
  "immutability": {
    "record_sha256": "hex",
    "source_issue_sha256": "hex"
  }
}
```

## AI Extraction Rules

AI extraction must follow these constraints:

1. Do not invent evidence. Every issue must reference at least one valid `evidence_id` or be emitted as a warning instead of an issue.
2. Keep issue title concrete and observable.
3. Separate observed behavior from expected behavior.
4. Assign confidence from `0.0` to `1.0`.
5. Deduplicate issues that describe the same root problem in the same package.
6. Do not include long transcript excerpts. Use transcript refs.
7. Mark privacy/compliance uncertainty explicitly instead of assuming it away.
8. Prefer `test_authoring` when the problem is with the test instruction, not the app.

## Validation Rules

Minimum validation:

1. `schema` equals `pg.audit_issue_extraction.v1`.
2. Every `issue_id` is unique.
3. Every `issue.evidence_ids[]` exists in the package manifest.
4. `priority` and `category` values are from the allowed lists.
5. `confidence` is numeric between `0.0` and `1.0`.
6. `status` is from the lifecycle list.
7. Reviewer-edited fields do not overwrite AI-suggested fields.
8. Approval records preserve the approved text exactly as approved.
9. Archive records include enough text for search without requiring AI/provider access.

## Local Prototype Storage

Recommended first local storage under `C:\CODEX PG`:

```text
CODEX Audit Prototype/
  CODEX Session Packages/
  CODEX Issue Extractions/
  CODEX Approval Records/
  CODEX Email Drafts/
  CODEX Archive/
```

Each folder starts with `CODEX` where it is Codex-created. The parent prototype folder also starts with `CODEX`.

