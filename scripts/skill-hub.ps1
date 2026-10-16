# skill-hub.ps1
# Master PowerShell CLI for Antigravity AI Agent Skill Router
param(
    [Parameter(Position=0)]
    [string]$Command = "help",

    [Parameter(Position=1, ValueFromRemainingArguments=$true)]
    [string[]]$ArgsList
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pyScript = Join-Path $scriptDir "skill_hub.py"

& py $pyScript $Command $ArgsList
