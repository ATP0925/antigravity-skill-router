# lint-skills.ps1
# PowerShell wrapper for lint_skills.py
param(
    [string]$Path = ".agents/skills"
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pyScript = Join-Path $scriptDir "lint_skills.py"

& py $pyScript $Path
