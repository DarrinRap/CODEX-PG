---
spec_id: CODEX-PAH-V2-REWRITE-CC-SPEC-v0.1
title: "PANDA Agent Hub v2 Rewrite Specification"
status: DRAFT_FOR_CD_REVIEW
author: CODEX
created: 2026-05-10
approval_boundary: CD owns CC routing; Codex does not send implementation-go or commit-go directly to CC.
sequencing: Hold for CC implementation until Vellum active work is complete or Darrin explicitly reopens PAH.
---

# PANDA Agent Hub v2 Rewrite Specification

## 1. Purpose

PAH v1 is no longer trustworthy enough to sit in the critical path for PG, Vellum, CC routing, or project truth. The observed failures are reliability and architecture failures, not isolated polish defects.

This spec defines a replacement-grade PAH v2 core. The goal is not to repair every v1 surface. The goal is to replace the reliability core with a boring, testable, explicit system that can later support dashboard and mailbox features without hiding stale or false status.

This is a CD-review spec for future CC routing. It is not implementation authorization. If CC receives this spec, it should be through CD-owned routing only, after Vellum work is complete or Darrin explicitly reopens PAH.

## 2. Current Failure Evidence

Observed during 2026-05-10 PAH incident diagnosis:

- PAH was unreachable: no listener on `127.0.0.1:8765`, `8766`, or `8788`.
- `/api/health` probes were actively refused while stale health artifacts still claimed prior success.
- The latest server start had logged `Running`, then transitioned to `Down` without a normal tray-exit event or useful stderr.
- The tray launch path used the WindowsApps `pythonw.exe` shim, which spawned a real child Python process and left process ownership ambiguous.
- The restart logic reclassified a tray-owned dead server as `offline`, then refused restart because it was no longer classified as `owned_server`.
- The automated verifier displayed a blocking Windows MessageBox during a test path.
- Health mixed process availability, stale inspector age, mailbox backlog, dirty git state, and agent-progress warnings into one operational signal.
- PAH screens/popups spawned repeatedly enough that Darrin asked to kill PAH.

Conclusion: PAH v1 should be frozen as noncritical infrastructure. It may be used only manually and cautiously until v2 exists.

## 3. Non-Goals

PAH v2 core rewrite must not include:

- tray application or Windows Startup integration in v1 of the rewrite;
- automatic watchers;
- automatic mailbox cleanup or archive mutation;
- direct CC implementation-go or commit-go routing;
- broad UI/dashboard rebuild;
- PG product UI work;
- Vellum implementation work;
- writes to `C:\panda-gallery` unless Darrin/CD explicitly authorizes a specific write;
- dependency on stale JSON snapshots as proof of current health;
- popups, modal dialogs, or GUI side effects from automated tests.

## 4. Required Architecture

PAH v2 must start as one boring local server process.

Required properties:

- one executable entry point;
- one configured host and port;
- one explicit runtime directory for local state/logs;
- one process owner model;
- explicit start and stop commands;
- no shell quoting tricks involving paths with spaces;
- no WindowsApps Python shim when a real Python executable is available;
- no implicit tray-owned child process in v2 core;
- no background auto-start until the start/stop lifecycle has passed repeated verification.

Recommended process command:

```text
python.exe <pah_v2_entrypoint> --host 127.0.0.1 --port <port>
```

The entry point may later be wrapped by a tray or launcher only after the core lifecycle is proven.

## 5. Health Contract

PAH v2 health must not collapse unrelated facts into a single ambiguous truth.

Expose separate endpoints:

| Endpoint | Meaning | Must Be Fast |
| --- | --- | --- |
| `/api/ping` | process is alive and serving HTTP | yes |
| `/api/ready` | server initialized and can serve core endpoints | yes |
| `/api/health/process` | process, port, pid, uptime, version | yes |
| `/api/health/mail-state` | current mailbox scan validity and age | yes |
| `/api/health/backlog` | advisory project/agent backlog summary | yes |
| `/api/health/full` | composed diagnostic view | bounded |

Top-level `/api/health` must return a structured summary:

```json
{
  "ok": true,
  "process_alive": true,
  "api_ready": true,
  "mail_state_valid": true,
  "blocking_failures": [],
  "advisories": []
}
```

Rules:

- `process_alive` and `api_ready` must never depend on mailbox contents.
- stale inspector reports must be advisories, not process failures.
- dirty git state must be advisory, not process failure.
- mailbox backlog must be advisory unless mailbox parsing itself fails.
- stale cached files must be labeled stale and must never be presented as current proof.

## 6. Logging Contract

PAH v2 must log lifecycle events as JSONL.

Required events:

- `server_start_requested`
- `server_started`
- `server_ready`
- `server_stop_requested`
- `server_stopped`
- `server_failed_to_start`
- `server_exception`
- `health_probe`
- `mail_scan_started`
- `mail_scan_finished`
- `mail_scan_failed`

Every lifecycle event must include:

- timestamp with timezone;
- pid;
- host;
- port;
- executable path;
- argv;
- working directory;
- version or git commit when available.

If the server exits normally, log exit reason before exit. If it crashes, capture traceback to stderr and a JSONL `server_exception` event where possible.

Logs must be append-only during normal operation. Tests may write to temporary test log directories, but must not erase production logs.

## 7. Mailbox Model

PAH v2 must begin read-only.

Required read-only behavior:

- scan configured mailbox roots;
- parse messages with bounded parsers only;
- reject or quarantine parse failures in memory, not by moving files;
- report parse errors with file path, line number if available, and reason;
- preserve source files untouched;
- distinguish physical files, parsed messages, visible messages, read-state, and acknowledged messages.
- impose per-file and total scan timeouts so one malformed message cannot block `/api/ping` or `/api/ready`.

Forbidden in v2 core:

- automatic archive moves;
- automatic read-state mutation;
- automatic reply/tombstone writes;
- automatic CC/CD dispatch;
- implementation-go or commit-go generation.

## 8. Minimal Dashboard

The first PAH v2 UI, if any, should be a plain status page.

Required sections:

- Process: pid, uptime, port, version.
- API: ping/ready status.
- Mail state: scan time, message count, parse errors.
- Backlog advisory: counts only.
- Logs: latest lifecycle event summary.

No action buttons in the first UI except refresh.

## 9. Start/Stop Commands

Provide explicit commands:

```text
start-pah-v2
stop-pah-v2
status-pah-v2
smoke-pah-v2
```

Implementation may use scripts, but scripts must:

- quote paths correctly;
- avoid shell-dependent path splitting;
- record the actual child pid;
- verify the port owner matches the expected pid;
- fail loudly if the port is occupied by another process.

## 10. Test Requirements

Required automated tests:

- start server on an unused test port;
- `/api/ping` returns alive;
- `/api/ready` returns ready;
- `/api/health/process` returns pid/port/version;
- stop server and verify port closes;
- server refuses to start on occupied port;
- mailbox parser handles normal Markdown;
- mailbox parser handles bold prose without catastrophic backtracking;
- malformed message reports parse error without blocking ping;
- stale cache is labeled stale;
- automated tests create no popups.
- automated tests use temporary mailbox/log/state directories, not live mailbox mutation.

Required manual verification before any tray/autostart work:

- start from a path containing spaces;
- stop cleanly;
- restart cleanly;
- run for at least 60 minutes without spawning screens;
- verify health remains truthful after mailbox changes.

## 11. Migration Plan

Phase 0: Freeze PAH v1

- Do not rely on PAH v1 for Vellum work.
- Do not add new PAH v1 features.
- Do not route CC implementation through PAH v1.

Phase 1: PAH v2 core

- Implement server lifecycle, ping/ready/process health, and JSONL logging.
- No dashboard beyond a plain read-only status page.
- No tray.
- Must live beside PAH v1 or in a new clearly named v2 folder until CD/Darrin approves replacing v1 entry points.

Phase 2: Read-only mailbox scan

- Add bounded message parsing.
- Add mailbox-state health.
- Add parse error reporting.
- Preserve all files.

Phase 3: Advisory dashboard

- Add read-only status dashboard.
- Add refresh only.
- No writes.

Phase 4: Optional controlled actions

- Only after Darrin/CD approval.
- Add narrowly scoped actions one at a time with tests.
- Every write action must have a dry-run mode first.

Phase 5: Optional tray

- Only after v2 core has proven stable.
- Tray must attach to an already-running server or start exactly one server with verified pid ownership.
- No Windows Startup integration until repeated manual verification passes.

## 12. Acceptance Criteria For PAH v2 Core

PAH v2 core is acceptable when:

- server start/stop is deterministic;
- ping and ready are fast and independent of mailbox parsing;
- health clearly separates blocking failures from advisories;
- mailbox parse failure cannot take down process health;
- stale artifacts are labeled stale;
- process pid and port owner are correct;
- tests do not display GUI;
- no automatic mailbox mutation occurs;
- smoke tests prove start, ping, health, and stop;
- Darrin can understand whether PAH is up without reading stale logs.
- the implementation report names all files changed and confirms no Vellum or PG product files were changed.

## 13. CD / CC Routing

Recommended CD action:

- Review this spec.
- Hold CC implementation until current Vellum work is complete unless Darrin explicitly reopens PAH earlier.
- Route to CC as a rewrite task, not a repair task.
- Instruct CC to ignore v1 dashboard feature parity until the v2 reliability core passes.

Codex must not send implementation-go or commit-go directly to CC.

## 14. Self-Review Log

Pass 1: 5 issues fixed — clarified CD-only routing to CC; added explicit runtime state/log directory; required append-only production logs; added mailbox scan timeouts; required tests to use temporary mailbox/log/state directories and report no Vellum/PG product file changes.

Pass 2: 2 issues fixed — required v2 to live beside v1 until replacement is approved; required dry-run-first behavior for any future write action.

Pass 3: 0 significant issues fixed — no remaining blocking errors, omissions, inconsistencies, or ambiguities found.
