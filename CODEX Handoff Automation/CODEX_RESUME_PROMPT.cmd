@echo off
powershell -ExecutionPolicy Bypass -File "%~dp0CODEX_run_handoff.ps1" -Mode ResumePrompt
notepad "C:\CODEX PG\CODEX Docs\CODEX_RESUME_PROMPT.txt"

