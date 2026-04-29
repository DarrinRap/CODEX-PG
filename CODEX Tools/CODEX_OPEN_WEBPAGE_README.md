# CODEX Open Webpage

Use this when a clickable Markdown link inside Codex chat does not open.

## Open PAH

```powershell
& 'C:\CODEX PG\CODEX Tools\CODEX_open_webpage.ps1' 'http://127.0.0.1:8765/'
```

## Open Any URL

```powershell
& 'C:\CODEX PG\CODEX Tools\CODEX_open_webpage.ps1' 'https://example.com/'
```

The `.cmd` wrapper is available for cases where PowerShell quoting is awkward:

```cmd
"C:\CODEX PG\CODEX Tools\CODEX_open_webpage.cmd" "https://example.com/"
```

Known Codex Desktop issue: chat-rendered link buttons may not launch reliably. The Windows `Start-Process` route is the stable fallback.
