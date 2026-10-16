# route-pipeline.ps1
# PowerShell wrapper for route_pipeline.py
param(
    [Parameter(Mandatory=$true)]
    [string]$Query
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pyScript = Join-Path $scriptDir "route_pipeline.py"

& py $pyScript $Query
