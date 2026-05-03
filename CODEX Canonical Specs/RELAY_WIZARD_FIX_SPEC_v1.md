# RELAY_WIZARD_FIX_SPEC_v1

Created: 2026-05-02
Owner: Codex
Audience: Claude Code
Source dispatch: CLAUDE-DESKTOP-20260501-175000-L27-RELAY-FIX-SPEC
Scope: implementation brief for the Relay tester setup wizard fix pass

## Purpose

This brief converts the L26 Relay wizard audit findings into a narrow CC implementation pass. It covers only the five accepted gaps below. Do not bundle unrelated Relay cleanup, visual redesign, or broader receive-loop architecture work into this pass.

## Source Material Read

- `C:\panda-gallery\relay\setup_wizard.py`
- `C:\panda-gallery\relay\dropbox_relay.py`
- `C:\panda-gallery\relay\invite_manager.py`
- `C:\panda-gallery\relay\relay_window.py`
- `C:\panda-gallery\relay\settings_panel.py`
- `C:\panda-gallery\panda_gallery.py`
- `C:\panda-gallery\settings_keys.py`
- `C:\panda-gallery\workflows\design\RELAY_TESTER_SETUP_IMPL_SPEC_v1.md`
- `C:\panda-gallery\workflows\design\RELAY_TESTER_SETUP_QA_ADDENDUM_v1.html`

## Constraints

- Edit only the relevant Panda Gallery implementation and test files for the five gaps.
- Preserve normal report behavior. Setup-test handling must not create normal bug cards, transcript rows, or unrelated report side effects.
- `relay/autoAcknowledgeEnabled` defaults on and must be respected.
- Keep UI changes pure Qt/QSS. No new dependency for the progress indicator.
- Do not change the locked Q9 product wording.

## Gap 1 - Screen 3 advances without waiting for Darrin ack

Severity: Major
Audit reference: Q4

### Current Evidence

- `C:\panda-gallery\relay\setup_wizard.py:65-69` defines `ERROR_ACK_TIMEOUT` but current Screen 3 flow does not use it.
- `C:\panda-gallery\relay\setup_wizard.py:497-498` enters Screen 3 and immediately calls `_send_setup_test()`.
- `C:\panda-gallery\relay\setup_wizard.py:500-527` uploads the setup-test package, shows success copy immediately, stores `relay/connectedAt`, then uses `QTimer.singleShot(1000, lambda: self.stack.setCurrentIndex(3))`.
- `C:\panda-gallery\workflows\design\RELAY_TESTER_SETUP_IMPL_SPEC_v1.md:318-324` says Darrin's PG should auto-ack incoming `setup_test`, and Rebecca's PG should poll for the ack every 5 seconds.
- `C:\panda-gallery\workflows\design\RELAY_TESTER_SETUP_IMPL_SPEC_v1.md:334-338` locks the 90-second timeout warning copy.

### Required Change

Replace the unconditional one-second success advance with an ack wait state:

1. After upload succeeds, show a waiting status instead of final success.
2. Poll the tester channel for a `setup_test_ack` payload from Darrin's PG.
3. Use a 5-second poll interval and a 90-second timeout.
4. On ack received, show the existing success text, set `KEY_RELAY_CONNECTED_AT`, and advance to the final screen.
5. On timeout, show `ERROR_ACK_TIMEOUT`, reveal retry, and do not set `KEY_RELAY_CONNECTED_AT` or advance.

Implementation shape can stay local to `RelaySetupWizard`: hold a `QTimer`, deadline/start timestamp, and original setup relay id so the ack can be matched by `original_relay_id` or `report_type == "setup_test_ack"` in the channel's `received/` path.

### Acceptance Criteria

- Screen 3 does not advance to the final screen until a `setup_test_ack` is detected.
- With no ack, Screen 3 remains on the hello step for 90 seconds, then shows the `ERROR_ACK_TIMEOUT` copy and the retry button.
- With an ack present within the timeout, Screen 3 shows success and advances to final screen.
- Tests cover success-after-ack and timeout-with-retry behavior.

## Gap 2 - Handshake channel_path is derived from tester name instead of relay/channelName

Severity: Major
Audit reference: Q2

### Current Evidence

- `C:\panda-gallery\relay\invite_manager.py:81-83` defines `channel_path_for_name(name)` as `/Panda Gallery Relay/{channel_name_for_tester(name)}/`.
- `C:\panda-gallery\relay\invite_manager.py:184` calls `channel_path_for_name(tester_name)` when creating the handshake.
- `C:\panda-gallery\relay\invite_manager.py:185` already reads `KEY_RELAY_CHANNEL_NAME` for `developer_id`, proving settings are available in this code path.
- `C:\panda-gallery\settings_keys.py:53` defines `KEY_RELAY_CHANNEL_NAME = "relay/channelName"`.
- `C:\panda-gallery\workflows\design\RELAY_TESTER_SETUP_IMPL_SPEC_v1.md:462-463` requires `channel_path` to follow `/Panda Gallery Relay/[channel_name]/`, where `channel_name` is the QSettings `relay/channelName` value on Darrin's install.

### Required Change

Change invite channel-path generation so the handshake path comes from Darrin's configured `relay/channelName`, not the tester's display name.

Recommended implementation:

1. Replace or supplement `channel_path_for_name(name)` with a helper that accepts a channel name, for example `channel_path_for_channel_name(channel_name: str) -> str`.
2. In `InviteManager.create_invite()`, read `KEY_RELAY_CHANNEL_NAME` from `self.settings` once, defaulting to `"Darrin"` if empty.
3. Build `channel_path` from that settings value.
4. Keep tester-name sanitization only for places that truly need a tester slug; do not use it for handshake `channel_path`.
5. Update tests that currently expect tester-name-derived channel paths.

### Acceptance Criteria

- For `relay/channelName = "Darrin Ops"` and tester name `"Rebecca Chen"`, the handshake contains `"channel_path": "/Panda Gallery Relay/Darrin Ops/"` or the existing canonical sanitized form if path sanitation is required by the path helper, but it must be based on `relay/channelName`, not `Rebecca Chen`.
- Existing invite creation still writes the handshake and stores a tester record.
- Revocation keeps using the stored record path and remains compatible with invites created before this change.

## Gap 3 - Progress indicator is static text, not current-step state

Severity: Minor
Audit reference: Q5

### Current Evidence

- `C:\panda-gallery\relay\setup_wizard.py:248-250` creates a single static label: `Connect Dropbox    Enter code    Say hello`.
- `C:\panda-gallery\relay\setup_wizard.py:416`, `:425`, `:453`, `:497`, and `:527` move the `QStackedWidget` between pages, but no progress state updates with page changes.

### Required Change

Replace the static progress label with a three-step indicator that changes with the current `QStackedWidget` page.

Recommended implementation:

1. Keep it simple with QLabel/QSS only. No new dependency.
2. Represent the three labels as either three QLabel widgets in a row or one rich-text QLabel.
3. Connect `self.stack.currentChanged` to a helper such as `_update_progress_step(index)`.
4. Highlight the active step using the existing accent color/bold weight and keep inactive steps muted.

### Acceptance Criteria

- Opening the wizard highlights Step 1 / Connect Dropbox.
- After Dropbox auth or existing valid token, Step 2 / Enter code is highlighted.
- After invite code validation and transition to hello, Step 3 / Say hello is highlighted.
- Returning to Start over updates the indicator back to Step 1.

## Gap 4 - Final screen copy says "New Report" instead of "New Report tab"

Severity: Minor
Audit reference: Q9

### Current Evidence

- `C:\panda-gallery\relay\setup_wizard.py:399` currently says `1. Open Relay and use New Report.`
- `C:\panda-gallery\workflows\design\RELAY_TESTER_SETUP_QA_ADDENDUM_v1.html:403` records the Issue 9 fix: change the affordance to `New Report tab`.
- `C:\panda-gallery\workflows\design\RELAY_TESTER_SETUP_QA_ADDENDUM_v1.html:427` summarizes Q9 as `New Report tab -> record -> Send to Darrin`.

### Required Change

Replace the final screen string with the locked wording.

Exact target copy:

`1. Open Relay and use the New Report tab.`

### Acceptance Criteria

- Final setup screen contains the phrase `New Report tab`.
- No other Q9 final-screen wording changes are included unless required for grammar around this exact phrase.

## Gap 5 - autoAcknowledgeEnabled helper exists but is not wired into production processing

Severity: Major
Audit reference: Q4 / spec section 5.6 / AC-6

### Current Evidence

- `C:\panda-gallery\relay\dropbox_relay.py:155-173` builds a setup-test ack payload with `report_type: "setup_test_ack"`.
- `C:\panda-gallery\relay\dropbox_relay.py:176-202` defines `auto_acknowledge_setup_test()`.
- `C:\panda-gallery\relay\dropbox_relay.py:186-191` reads `KEY_RELAY_AUTO_ACKNOWLEDGE_ENABLED`, defaults true, and returns false unless the incoming metadata has `report_type == "setup_test"`.
- `C:\panda-gallery\tests\relay\test_dropbox_relay.py:74-89` and `:101-106` test the helper directly.
- Read-only search of current Python sources found no production call site for `auto_acknowledge_setup_test()` outside tests.
- `C:\panda-gallery\relay\relay_window.py:174-199` has a developer hub placeholder, but no visible Dropbox receive/poll loop.
- `C:\panda-gallery\workflows\design\RELAY_TESTER_SETUP_IMPL_SPEC_v1.md:559-561` requires Darrin's PG to treat `report_type == "setup_test"` as setup-only and auto-ack immediately when enabled.
- `C:\panda-gallery\workflows\design\RELAY_TESTER_SETUP_IMPL_SPEC_v1.md:666-668` defines AC-6: auto-ack defaults on and Darrin's PG auto-acks the setup test report on receipt.

### Required Change

Wire `auto_acknowledge_setup_test()` into the developer-side incoming report processing path. Because the current Relay module does not yet expose a concrete receive loop, CC should attach this to whichever production path first detects or imports Dropbox Relay reports for Darrin's developer install.

Required logic at that boundary:

1. When an incoming package/report metadata file is detected, load its metadata before normal report card creation.
2. If `metadata.get("report_type") == "setup_test"`, call `auto_acknowledge_setup_test(settings=..., dropbox_adapter=..., setup_metadata=metadata, tester_channel_path=..., refresh_token=..., developer_name=...)`.
3. Skip normal report-card/transcript/BUGS processing for setup tests.
4. If the helper returns true, record/log only a safe operational status. Do not log secrets or refresh tokens.
5. If auto-ack is disabled, do not ack; leave normal setup timeout behavior to Rebecca's Screen 3.
6. Preserve normal report handling when `report_type` is missing or not `"setup_test"`.

If CC creates a new receive/poll loop as part of this fix pass, keep it minimal and testable. The loop should be the smallest production bridge needed to process `received/*/metadata.json` and invoke existing helper behavior.

### Acceptance Criteria

- With `relay/autoAcknowledgeEnabled = true`, an incoming setup-test metadata payload produces a `setup_test_ack` in the tester channel within the same receive/poll cycle.
- With `relay/autoAcknowledgeEnabled = false`, no ack is written.
- Normal reports without `report_type == "setup_test"` continue through the existing report-processing path.
- Setup-test reports do not create normal bug/report cards.
- Tests cover enabled setup-test ack, disabled setup-test no-op, and normal-report no-op.

## Suggested Test Coverage

- `tests/relay/test_setup_wizard.py`: Screen 3 waits for ack; timeout shows `ERROR_ACK_TIMEOUT`; Q9 copy includes `New Report tab`; progress indicator tracks page index.
- `tests/relay/test_invite_manager.py`: handshake `channel_path` comes from `KEY_RELAY_CHANNEL_NAME`; tester name no longer controls the channel path.
- `tests/relay/test_dropbox_relay.py`: keep existing helper tests and add a production-boundary test once the receive/poll call site exists.
- Any new developer receive/poll module should have focused unit tests with fake settings and fake Dropbox adapter.

## Non-goals

- No redesign of Relay hub screens.
- No Dropbox credential or token logging changes beyond avoiding leaks in new code.
- No two-PC Adam/Darrin confidence test in this pass.
- No unrelated cleanup in `relay/`.
