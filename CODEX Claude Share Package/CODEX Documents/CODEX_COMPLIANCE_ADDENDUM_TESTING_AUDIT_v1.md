# CODEX Compliance Addendum: Testing + Audit v1

Generated: 2026-04-24

Status: Codex canonical draft for PG Testing + Audit MVP v1.

Scope: defines privacy, compliance, and safety guardrails for the Testing + Audit MVP pipeline: session packaging, Dropbox transfer, AI issue extraction, approval workflow, shared email communication, and searchable archive.

This is an engineering and product guardrail document, not legal advice. Before processing real patient data, Darrin should confirm the final workflow, vendors, agreements, retention policy, and operating procedures with appropriate compliance/legal support.

## Current Reference Sources Checked

The following public sources were checked on 2026-04-24:

- HHS Security Rule overview: https://www.hhs.gov/hipaa/for-professionals/security/index.html
- HHS Summary of the HIPAA Security Rule: https://www.hhs.gov/hipaa/for-professionals/security/laws-regulations/index.html
- HHS de-identification guidance: https://www.hhs.gov/hipaa/for-professionals/privacy/special-topics/de-identification/index.html
- Dropbox BAA help page: https://help.dropbox.com/account-settings/business-associate-agreement

Key interpretation for this project:

- HHS describes the Security Rule as requiring administrative, physical, and technical safeguards for electronic protected health information.
- HHS de-identification guidance identifies two recognized de-identification methods: Expert Determination and Safe Harbor.
- Dropbox documents that eligible team admins can sign a Business Associate Agreement through the admin console, but the project must verify the actual account, plan, agreement, folder policy, and configuration before any real PHI transfer.

## Default Rule

Until explicitly changed:

```text
Testing + Audit MVP development is synthetic/de-identified only.
No real PHI may be uploaded to Dropbox, sent to AI, emailed, or archived by the prototype.
```

This default applies even if the UI, package schema, or transfer adapter technically supports the action.

## Data Classification

Every package and evidence record should be treated as one of these classes:

| Class | Meaning | Allowed In Local Prototype |
| --- | --- | --- |
| `synthetic` | Fabricated data that cannot identify a real person. | Yes |
| `deidentified_claimed` | Data claimed to be de-identified, but method not verified in the app. | Yes with warning |
| `deidentified_verified` | Data de-identified under a documented process. | Yes |
| `limited_or_sensitive` | May contain dates, clinical context, device metadata, or indirect identifiers. | Local only, warning required |
| `phi_known` | Contains identifiable patient or health information. | No, unless compliance mode is explicitly approved |
| `unknown` | Privacy state not reviewed. | Local only, warning required |

Schema alignment:

- Package/evidence privacy fields should default to `unknown` unless explicitly set.
- The dashboard must surface `unknown`, `limited_or_sensitive`, and `phi_known` states before upload, AI, email, or archive actions.

## PHI Risk In Testing Evidence

Testing evidence may contain PHI even when it is not obvious.

High-risk evidence types:

- screenshots of patient lists,
- screenshots of dental images with names/chart IDs visible,
- transcripts that mention patient names or treatment details,
- filenames containing patient names or chart IDs,
- metadata JSON with machine/user/path identifiers,
- email drafts containing patient-specific clinical context,
- archive search text generated from issue summaries or transcripts.

Rules:

- Do not assume screenshots are safe because they came from testing.
- Do not assume transcript snippets are safe because they are short.
- Do not put long transcript excerpts into issue, email, or archive records.
- Do not include raw local usernames, machine names, tokens, or absolute patient paths in external payloads unless reviewed.

## Local Prototype Permissions

Allowed for synthetic/de-identified local prototype:

- create session packages under `C:\CODEX PG`,
- hash copied files,
- generate evidence IDs,
- generate AI extraction input JSON,
- validate packages,
- create fixture/mock issue extraction results,
- create local approval records,
- create draft-only email records,
- create local archive JSONL records,
- build local dashboard UI against those files.

Not allowed until explicitly approved:

- upload real data to Dropbox,
- call an AI provider with real data,
- send real emails,
- archive real PHI,
- store provider credentials in git,
- write logs containing PHI or secrets,
- silently process privacy `unknown` evidence as safe.

## Dropbox Guardrails

Dropbox integration is not just a transport task.

Before enabling real Dropbox upload:

1. Confirm the exact Dropbox account/team and plan.
2. Confirm whether a Business Associate Agreement is required and signed for the account.
3. Confirm folder root, access groups, admin ownership, retention, and audit logging.
4. Confirm whether test packages may include PHI.
5. Confirm completion marker behavior: `_PACKAGE_READY.json` must be written last.
6. Confirm token storage outside git and outside package records.
7. Confirm upload retry behavior does not create partial duplicate packages.
8. Confirm deletion/retention policy for test packages.

Prototype rule:

- Dropbox adapter stays disabled or local-mock-only until the above checklist is complete.

UI rule:

- `Queue Upload` and `Upload` actions must be disabled for packages with privacy `unknown`, `limited_or_sensitive`, or `phi_known` unless an explicit compliance mode is enabled.

## AI Provider Guardrails

AI extraction must be provider-neutral until provider and compliance decisions are made.

Before enabling real AI calls:

1. Confirm provider, model, account, and data processing terms.
2. Confirm whether a BAA or equivalent agreement is required and in place.
3. Confirm whether prompts, inputs, outputs, and logs are retained by the provider.
4. Confirm whether screenshots, transcripts, metadata, and archive text may be sent.
5. Confirm redaction/de-identification process before transmission.
6. Confirm local logging excludes secrets and long PHI text.
7. Confirm AI output validation blocks invented evidence IDs.
8. Confirm reviewer approval is required before email/archive closure.

Prototype rule:

- Use fixture/mock AI extraction for local prototype.
- Real AI calls remain off by default.

AI output rule:

- AI may suggest issues, but it cannot approve, send, archive, or override reviewer decisions.

## Email Guardrails

Shared team email is a high-risk disclosure path.

Before enabling live email:

1. Confirm email provider and shared inbox ownership.
2. Confirm whether the inbox is approved for PHI if PHI is in scope.
3. Confirm recipient list and access controls.
4. Confirm message retention and audit logging.
5. Confirm no real PHI appears in subject lines unless explicitly approved.
6. Confirm approval record is required before queue/send.
7. Confirm retry/failure behavior preserves approved content.
8. Confirm sent message IDs are recorded without leaking credentials.

Prototype rule:

- Email records are draft-only.
- Live send is disabled.

UI rule:

- Email send/queue actions are disabled until provider and compliance state are configured.
- Email text must come from reviewer-approved fields, not raw AI output.

## Archive Guardrails

Archive records are intended to be searchable and auditable, which also makes them risky if they include PHI.

Rules:

- Archive records must be append-oriented or immutable for MVP.
- Archived records must include hashes/immutability metadata.
- Archive search text should be concise and avoid long transcript text.
- Real PHI archive retention policy must be defined before real PHI use.
- Corrections after archive should create a superseding record instead of mutating the old record.
- Archive records should preserve package/issue/approval lineage.

Before real PHI archive:

- define retention period,
- define deletion/export policy,
- define access controls,
- define backup policy,
- define audit log access,
- define breach/incident workflow.

## Logging Rules

Logs are for operations, not raw data storage.

Allowed log content:

- package ID,
- session ID,
- run ID,
- issue ID,
- evidence ID,
- event type,
- component,
- state transition,
- validation result,
- short non-PHI message.

Disallowed log content unless explicitly reviewed:

- patient names,
- chart IDs,
- birth dates,
- full transcripts,
- raw screenshot OCR text,
- API keys/tokens,
- Dropbox paths containing patient identifiers,
- email body text containing PHI,
- provider request/response payloads containing PHI.

## Access Control Expectations

Local prototype:

- single-user developer/reviewer assumption,
- no real PHI,
- no network providers,
- files under `C:\CODEX PG` only.

Before real deployment:

- named reviewer identity,
- role separation for reviewer/admin if needed,
- local storage permissions,
- encrypted storage decision,
- credential storage decision,
- audit events for material actions,
- backup and retention policy.

## Dashboard Warning Requirements

The audit dashboard must warn or block before risky actions.

Block actions when:

- package hash validation fails,
- issue references missing evidence,
- package is not in the required state,
- upload/send/AI provider is not configured,
- known PHI is present and compliance mode is not enabled.

Warn actions when:

- privacy state is `unknown`,
- transcript is missing,
- optional metadata is missing,
- AI confidence is low,
- email subject/body might include sensitive details,
- archive search text includes transcript-derived content.

## Compliance Mode Concept

A future compliance mode may be added, but it must be explicit.

Minimum compliance mode settings:

```json
{
  "schema": "pg.audit_compliance_config.v1",
  "real_phi_allowed": false,
  "dropbox_baa_confirmed": false,
  "ai_baa_confirmed": false,
  "email_phi_approved": false,
  "archive_phi_approved": false,
  "retention_policy": null,
  "reviewer_identity_required": true,
  "redaction_required_before_external_transfer": true
}
```

Rules:

- Defaults must be false or null.
- Config must not contain secrets.
- Changing compliance mode should create an audit/config event.
- UI should display compliance mode status when upload, AI, email, or archive actions are visible.

## Redaction And De-identification

Development may use synthetic data immediately.

For real data, redaction/de-identification needs a documented process.

Minimum redaction review targets:

- patient name,
- date of birth,
- chart ID,
- address/phone/email,
- dates where not allowed,
- filenames and folder paths,
- window title bars,
- sidebar patient lists,
- transcript mentions,
- image overlays/burned-in identifiers,
- email subject/body.

Do not label data `deidentified_verified` unless the method and reviewer are recorded.

## Implementation Acceptance Criteria

Compliance guardrails are ready for local MVP when:

1. Package schema preserves privacy state per evidence item.
2. Dashboard surfaces privacy state before review/upload/email/archive.
3. Dropbox, AI, and email adapters default to disabled/mock mode.
4. Logs avoid PHI and secrets.
5. Approval records preserve reviewer identity and event history.
6. Archive records are immutable or append-only.
7. Unknown privacy state creates visible warnings.
8. Real PHI requires explicit compliance configuration before external transfer.

## Stop Conditions

Claude, Codex, or any implementer should stop and notify Darrin before continuing if:

- a task asks to upload, email, or send to AI any real/unknown patient data,
- provider terms or BAA status are unknown,
- a shortcut would bypass package validation,
- a shortcut would allow AI issues without evidence IDs,
- a shortcut would overwrite AI fields with reviewer fields,
- a shortcut would hide warnings to make workflow faster,
- requirements conflict with this addendum or the dashboard UX spec.

## Open Compliance Decisions

| Decision | Default Until Decided |
| --- | --- |
| Can real PHI be used in Testing + Audit? | No |
| Is Dropbox approved for PHI in this workflow? | Not yet |
| Is an AI provider approved for PHI in this workflow? | Not yet |
| Is shared email approved for PHI in this workflow? | Not yet |
| What is the archive retention policy? | Undefined, local synthetic only |
| Who is the named reviewer identity source? | Manual local string |
| Is de-identification Safe Harbor, Expert Determination, or other internal process? | Undefined |
| Are screenshots automatically redacted? | No |
