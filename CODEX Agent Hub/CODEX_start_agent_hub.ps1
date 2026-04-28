$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$App = Join-Path $ScriptRoot 'CODEX_agent_hub.py'
python "$App"
