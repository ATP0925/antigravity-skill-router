# scaffold-skill.ps1
# PowerShell wrapper for scaffold_skill.py
param(
    [Parameter(Mandatory=$true)]
    [string]$Name,

    [Parameter(Mandatory=$true)]
    [string]$Description,

    [ValidateSet("workspace", "global")]
    [string]$Scope = "workspace",

    [ValidateSet("workflow", "tool", "audit")]
    [string]$Template = "workflow",

    [string]$Keywords = ""
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pyScript = Join-Path $scriptDir "scaffold_skill.py"

& py $pyScript -n $Name -d $Description -s $Scope -t $Template -k $Keywords
