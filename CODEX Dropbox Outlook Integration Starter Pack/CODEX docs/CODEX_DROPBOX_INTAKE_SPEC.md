# CODEX Dropbox Intake Spec

## Official API Concepts Used

Dropbox uses OAuth 2.0. For desktop/background use, Dropbox recommends OAuth code flow with PKCE and refresh tokens. Access tokens are short-lived; refresh tokens are used to obtain new access tokens.

Dropbox file detection can be implemented with folder cursors from list_folder/list_folder_continue, long polling, or webhooks. MVP should start with polling/cursors because it is easier and does not require a public webhook endpoint.

## Required Dropbox Scopes

Exact scopes depend on the Dropbox app configuration, but intake generally needs file read access to the selected app folder or configured audit folder.

Recommended principle: least privilege. Use an app folder or one narrow incoming audit folder rather than broad Dropbox access when possible.

## Incoming Folder Convention

Recommended remote folder:

/Panda Gallery Audit/Incoming/

Each submission:

/Panda Gallery Audit/Incoming/pkg_<timestamp>_<id>/
  _PACKAGE_READY.json
  session_package_manifest.json
  source/
  evidence/
  derived/
  logs/

## Completion Marker

The Audit Module should process only folders that contain _PACKAGE_READY.json.

Marker example:

{
  "schema": "pg.dropbox_completion_marker.v1",
  "package_id": "pkg_20260424_201255_8f3b2a",
  "created_at": "2026-04-24T20:14:10-07:00",
  "file_count": 17,
  "manifest_sha256": "hex"
}

## Intake Algorithm

1. Refresh Dropbox access token if needed.
2. list_folder on configured incoming folder.
3. For each child folder, check for _PACKAGE_READY.json.
4. Download marker and manifest.
5. Validate package ID and expected file list.
6. Download package into local staging.
7. Write local intake record.
8. Mark package as analysis_ready.

## Error Handling

- 401 unauthorized: refresh token or ask user to reconnect Dropbox.
- 403 insufficient_scope: show required scope and stop.
- 404 path/not_found: show remote folder path and setup hint.
- 409 conflict: package path changed or file missing; rescan.
- 429 rate limited: obey Retry-After/backoff.
- Missing marker: leave folder in partial state.
- Missing manifest: mark package invalid and do not analyze.

## First MVP Recommendation

Build a polling-based client first. Add webhooks only after local intake and package validation are stable.
