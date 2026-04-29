---
schema_version: 1
id: CLAUDE-20260428-170000-relay-spec-v03-amendment
thread_id: RELAY-SPEC-V03
created_at: '2026-04-28T17:00:00-07:00'
from: claude_desktop
to: codex
type: dispatch
priority: high
status: shipped
thread_status: active
action_owner: codex
requires_darrin_decision: false
approval_boundary: coordination_only
tier: high
---

# Claude Desktop -> Codex: RELAY_SPEC v0.3 amendment

## Task

Produce `RELAY_SPEC_v0.3.md` by amending `RELAY_SPEC_v0.2.md` with all
decisions locked in the Relay tester setup Q&A (session 86). Update the
master spec index to mark v0.3 canonical and v0.2 superseded.

**Deliverables:**
- `C:\CODEX PG\CODEX Canonical Specs\RELAY_SPEC_v0.3.md`
- `C:\CODEX PG\CODEX Canonical Specs\CODEX_MASTER_SPEC_INDEX.md` updated

---

## Mandatory reading before starting

1. `C:\CODEX PG\CODEX Canonical Specs\RELAY_SPEC_v0.2.md` — base document to amend
2. `C:\panda-gallery\workflows\design\RELAY_TESTER_SETUP_QA_ADDENDUM_v1.html` —
   the full Q&A decisions addendum (open as raw HTML or in browser). This is the
   source of truth for all v0.3 changes. Read it end-to-end, especially:
   - Q1–Q9 locked decisions
   - Issue fixes 1–12 (these supersede anything contradicting them in v0.2)
   - The standing design principle (layered UX, hidden diagnostics)
   - Code format spec table
   - Error message table with exact copy

---

## What v0.3 must add or change

### New §16 — Tester Setup Flow

Add a complete new section §16 covering the tester onboarding wizard.
The section must specify:

**§16.1 — Overview**
The tester setup flow is a standalone 3-step wizard window (not the full PG
app shell). It runs once on first Relay use by a tester-role install.
Steps: Connect Dropbox → Enter invite code → Say hello.

**§16.2 — Prerequisites**
- Tester requires a Dropbox account only — no Dropbox desktop app required.
- Auth uses PKCE flow (`DropboxOAuth2FlowNoRedirect`, `use_pkce=True`,
  `token_access_type='offline'`) — same as Remote Testing. No app secret.
- The browser opens for Dropbox auth; the user clicks Allow and pastes the
  auth code back into PG. This is step 1 of the wizard.

**§16.3 — Invite code system**
- Darrin generates an invite code for each tester in Relay Settings.
- Code format: `PG-` prefix + 2 uppercase letters + 2 digits.
  - Total length: 7 characters including prefix.
  - Always uppercase — no case sensitivity.
  - Excluded characters: O, I (letters) · 0, 1 (digits) to prevent misreading.
  - Valid charset: A–Z minus O and I · digits 2–9.
  - Keyspace: 24² × 8² = 36,864 combinations.
  - Example: `PG-X4K9`
- Codes are permanent until Darrin explicitly revokes them.
  - Permanent codes allow Rebecca to reconnect after reinstalling PG without
    requesting a new code from Darrin.
  - Darrin can revoke any code from the Testers section of Relay Settings.
- PG decodes the channel path from the code internally. The tester never
  sees or types a Dropbox folder path.

**§16.4 — Invite delivery**
- Darrin invites a tester by entering their name and email address in Relay
  Settings → Invite a tester.
- PG generates the invite code and opens Darrin's default email client
  via a `mailto:` link (Python `webbrowser.open("mailto:...")`) with the
  To, Subject, and body pre-filled.
- Darrin reviews the pre-filled email and hits Send. No copy-paste required.
- The pre-filled email body includes:
  1. The installer download URL (configurable in Relay Settings, default:
     `github.com/[repo]/releases/latest`).
  2. The invite code rendered prominently.
  3. The instruction: "Open Relay and enter your code. PG will walk you
     through the rest."
- If no default email client is configured, a clipboard fallback button
  copies the full invite text so Darrin can paste it anywhere.
- Installer download URL is a Relay Setting (`relay/installerDownloadUrl`).
  Default: `github.com/[repo]/releases/latest`. Darrin updates this once
  if distribution moves — all future invites pick up the new URL automatically.

**§16.5 — Auto-verification (Step 2)**
- When Rebecca finishes typing her invite code, PG auto-tests the connection
  immediately — no "Test connection" button.
- Two checks run in sequence (invisible to Rebecca):
  1. PG decodes the channel path from the code — fails if code is invalid
     or revoked.
  2. PG verifies Rebecca's Dropbox token can write to that channel path —
     fails if Dropbox auth did not complete successfully.
- Rebecca sees only green (success) or red/amber (failure with specific message).

**§16.6 — End-to-end confirmation (Step 3)**
- On code verification success, PG automatically sends a visible test report
  to Darrin's Relay inbox labelled "Relay setup test."
- If `relay/autoAcknowledgeEnabled` is true (default), Darrin's PG instance
  automatically sends an acknowledgment back to Rebecca.
- Rebecca's wizard shows a waiting state ("Waiting for Darrin to confirm…")
  then a success state ("Darrin got it — you're all set!") on receipt of the ack.
- Expected time: under 10 seconds when Darrin has PG running. If PG is
  closed, the ack fires on next PG launch.
- If ack is not received within 60 seconds, Rebecca sees the amber warning
  state (see §16.7 error messages) and is directed to ask Darrin to open PG.

**§16.7 — Error messages (exact copy, non-negotiable)**
Each failure state has a specific plain-English message and exactly one next step.
No generic "something went wrong" messages.

| Failure | Message | One next step |
|---|---|---|
| Dropbox auth failed | "Dropbox didn't authorise PG" | Click "Open Dropbox in browser" again and make sure you click Allow on the Dropbox page |
| Wrong or revoked code | "Code not recognised" | Double-check the code Darrin sent. Ask Darrin to resend it if needed |
| No internet | "No internet connection" | Connect to wifi and try again |
| Ack not received (60s timeout) | "Darrin hasn't confirmed yet" (amber, not red) | Ask Darrin to open Panda Gallery and check his Relay inbox |

**§16.8 — Wizard presentation**
- One step at a time. Full screen for each step. Three screens total.
- A wizard progress bar at the top shows all 3 steps with connectors.
  Active step: peach circle. Complete step: green ✓. Pending: muted circle.
- The standalone wizard window has: PG title bar (brand mark + "Relay Setup"),
  wizard content, statusbar. No module tabs, tool strip, filmstrip, or right panel.

**§16.9 — Final screen**
After successful connection, the wizard shows a completion screen with:
- Large green checkmark and "You're all set!"
- "Darrin got your hello. You're connected."
- A "WHEN YOU FIND A BUG" section showing exactly 3 plain steps:
  1. Open Relay and tap the New Report tab
  2. Record what you saw — just speak naturally
  3. Tap Send to Darrin — done
- Primary button: "Open Relay →"
- These 3 steps are shown once only on this screen. They do not repeat.

**§16.10 — Layered UX principle (standing design rule)**
All Relay surfaces follow a two-layer UX architecture:
- Surface layer (tester/default view): Fully automatic. Zero decisions. Zero
  jargon. Every step happens without the user choosing anything technical.
  Errors are plain English with one next step.
- Hidden layer (Darrin's diagnostics): Behind an "Advanced diagnostics"
  collapsible in Relay Settings: raw Dropbox sync log, token status, channel
  path, SDK version, force re-test, manual retry. Present but invisible
  unless needed.
This principle applies across all of Relay — not just setup. Every Relay
screen defaults to the simplest possible surface. Troubleshooting tools
exist but are disclosed progressively.

### Updates to existing sections

**§4 Relay Settings — add new keys:**
- `relay/installerDownloadUrl` — string, default `github.com/[repo]/releases/latest`.
  The installer download URL included in invite emails. Configurable so Darrin
  can update it if distribution moves without touching code.
- `relay/inviteCodesJson` — JSON blob storing all active invite codes with
  tester name, email, channel path mapping, created_at, and revoked flag.

**§4.9 Role Configuration — amendment:**
Add: "When a tester-role install opens Relay for the first time with no stored
Dropbox token, it enters the setup wizard (§16) before the tester hub."

**§6.5 Settings / QSettings — add keys:**
```
relay/installerDownloadUrl
relay/inviteCodesJson
```

**§8 Hub Layout — tester section amendment:**
Add: "A tester-role install that has not completed setup (no stored Dropbox
token and no verified invite code) enters the §16 setup wizard on first launch
rather than the tester hub."

---

## What v0.3 must NOT change

- All v0.2 decisions that are not listed above remain unchanged.
- The developer hub layout, tab strip, duplicate detection, compose flow,
  template system, Dropbox sync states, and delivery receipts are v0.2
  decisions — do not amend without a new dispatch.
- §5 file/folder structure, §13 Dropbox sync, §14 tester hub view (post-setup),
  §15 workflow steppers — all unchanged.

---

## Validation checklist (run before delivering)

1. §16 is present with all 10 subsections (§16.1–§16.10).
2. Invite code format table is present with all fields (prefix, body, length,
   case, excluded chars, charset, keyspace, example).
3. Error message table is present with all 4 failure states and exact copy.
4. `relay/installerDownloadUrl` and `relay/inviteCodesJson` appear in §4 and §6.5.
5. The layered UX principle (§16.10) is present.
6. Master spec index updated: v0.3 canonical, v0.2 superseded.
7. No v0.2 decisions outside the amendment scope have been changed.

---

## Tier: High

Scoped amendment — adding one new section (§16) and updating 3 existing
sections (§4, §6.5, §8). Source material (Q&A addendum) is fully locked.
No ambiguity to resolve.

---

## Reply format

Write to `C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox\` with:
- Confirmation that both source files were read before starting
- Paths to both deliverables
- Validation checklist results (all 7 items)
- Any genuine ambiguities encountered (flag, do not guess)

-- Claude Desktop
