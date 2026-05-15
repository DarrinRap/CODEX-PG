# CODEX PAH Post-Vellum Holding Queue

Created: 2026-05-10

Purpose: PAH-domain issues acknowledged by Codex but intentionally held until the active Vellum bug campaign closes and CD/Darrin re-authorize PAH work.

## Held Items

### PAH-DUPLICATE-SERVER-30S-FLASH-20260510

Source mail: `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\20260510_0210_CLAUDE_to_CODEX_pah_duplicate_server_30s_window_flash_report.md`

Status: held / no action authorized.

Summary:

- Darrin observed windows opening and closing on a roughly 30-second cadence.
- CD reports two simultaneous `CODEX_agent_hub.py` pythonw instances on port 8765 with `--no-port-fallback`.
- The duplicate processes used different Python interpreter paths.
- Symptom reportedly stopped after killing PAH/tray-related processes.

Post-Vellum questions to investigate:

- What enforces `--no-port-fallback`, and should a bind-losing process fail fast?
- What launch sources can spawn PAH server/tray instances?
- Should PAH normalize to one known Python interpreter?
- Which process created the 30-second visible window flash?

### PAH-CODEX-COUNT-MISMATCH-20260510

Source mail: `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\20260510_0150_CLAUDE_to_CODEX_pah_count_mismatch_spec_held_post_vellum.md`

Status: held for post-Vellum routing by CD.

Summary:

- Codex authored a spec for the Codex `19` vs `18` count mismatch.
- CD accepted the spec shape but held routing to avoid splitting CC away from Vellum.
- Any future implementation requires explicit CD/Darrin UI-touch authorization.

### PAH-REBOOT-AUTOSTART-20260509

Source mail: `C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\20260509_1010_CLAUDE_to_CODEX_pah_autostart_repair_spec.md`

Status: held / no process start authorized.

Summary:

- CD authored a Task Scheduler based no-console login autostart repair spec.
- Later Darrin direction currently forbids starting PAH/tray/watchers unless explicitly requested.
- Codex repaired only the visible desktop launcher tile by replacing a plain `.url` with a real `.lnk` launcher.
- True Task Scheduler autostart remains unimplemented and requires explicit re-authorization after Vellum or if Darrin elevates it sooner.
