# PAH Troubleshooting Notes

## 2026-05-08 - PAH port open but dashboard/API hang

Symptoms:
- PAH process starts and binds `127.0.0.1:8765`.
- `/api/ping`, `/api/health`, and `/` time out.
- CPU may rise on the PAH Python process.
- Tray can report Down/Conflict even though the port briefly appears open.

Confirmed root cause:
- PAH mailbox parsing hung in `pah_core/schema.py::parse_legacy_metadata`.
- Trigger message:
  `C:\panda-gallery\workflows\cc_mailbox\CC Inbox\CLAUDE-20260506-014100-pc-full-mockup-coverage.md`
- Trigger line:
  `**The approved v2 mockups ARE the spec for visual design. Every existing and new mockup must match the PG Design Bible exactly. Bible takes precedence over any prior CC implementation decision.**`
- The legacy bold-metadata regex treated early bold prose as possible metadata and catastrophically backtracked because the line did not match the expected `**Key:** value` shape.

Evidence used:
- Direct PAH launch proved the server could bind the port.
- `/api/ping` still timed out, proving the problem was not only health payload generation.
- A stack probe showed `notification_loop -> run_notification_scan -> load_messages -> parse_message -> extract_message_metadata -> parse_legacy_metadata -> re.match`.
- A no-notification-loop A/B probe returned `/api/ping` immediately.
- `load_messages()` alone timed out before the fix.
- Isolated regex timing on the trigger line timed out.

Fix applied:
- In `pah_core/schema.py`, bound the bold metadata key regex:
  `^\*\*([^:*]{1,120}):\*\*\s*(.*)$`
- This makes normal bold prose fail fast and still supports `**Key:** value` legacy metadata lines.

Validation after fix:
- Exact trigger line parsed in about `0.000101s`.
- `load_messages()` loaded `175` messages in about `0.138s`.
- PAH `/api/ping` returned `200`; warm responses were about `2ms`.
- PAH `/api/health` returned `200`.
- PAH dashboard root `/` returned `200` and contained `PANDA Agent Hub`.

If this happens again:
1. Check whether port `8765` is listening.
2. Test `/api/ping`; if it times out while the port is listening, suspect handler/thread blocking.
3. Time `load_messages()` before testing full notification delivery.
4. Look for newly added early bold Markdown prose in mailbox messages.
5. Do not edit mailbox files as the first fix; fix parser behavior or quarantine only after diagnosis is proven.

## 2026-05-08 - Detached tray launch with paths containing spaces

Symptom:
- A detached/manual tray launch exits immediately and leaves no PAH tray/server process.
- Redirected stderr may show:
  `Processing -File 'C:\CODEX' failed because the file does not have a '.ps1' extension.`

Cause:
- The `-File` script path was passed to `powershell.exe` without quoting.
- Because the PAH path contains a space (`C:\CODEX PG\...`), PowerShell saw only `C:\CODEX`.

Fix/check:
- Quote the script argument when using `Start-Process` manually:
  `'-File', "`"C:\CODEX PG\CODEX Agent Hub\CODEX_start_agent_hub_tray.ps1`""`
- Verified correct quoted launch keeps the tray alive as an attached or owned tray, depending on whether a PAH server already exists.
