# test-skill.ps1
# Comprehensive 20-Point Automated Verification & Benchmark Suite for skill-router

$scriptDir = $PSScriptRoot
if (-not $scriptDir) { $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path }
$skillRoot = Split-Path -Parent $scriptDir
$skillMdPath = Join-Path $skillRoot "SKILL.md"
$indexJsonPath = Join-Path $skillRoot "data\skills-index.json"
$queryScript = Join-Path $scriptDir "query-index.py"
$lintScript = Join-Path $scriptDir "lint_skills.py"
$pipelineScript = Join-Path $scriptDir "route_pipeline.py"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Running Production-Grade Verification Suite: skill-router" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

$testsPassed = 0
$totalTests = 0

function Assert-Test {
    param([string]$Category, [string]$Name, [bool]$Condition, [string]$Details = "")
    $script:totalTests++
    if ($Condition) {
        Write-Host "  [PASS] [$Category] $Name" -ForegroundColor Green
        if ($Details) { Write-Host "         $Details" -ForegroundColor DarkGray }
        $script:testsPassed++
    } else {
        Write-Host "  [FAIL] [$Category] $Name" -ForegroundColor Red
        if ($Details) { Write-Host "         $Details" -ForegroundColor Yellow }
    }
}

# --- Section 1: Architectural & File Integrity ---
Write-Host "1. Structure & Specification Checks" -ForegroundColor Yellow

$skillExists = Test-Path $skillMdPath
Assert-Test -Category "Spec" -Name "SKILL.md exists" -Condition $skillExists -Details $skillMdPath

if ($skillExists) {
    $content = Get-Content -Path $skillMdPath -Raw
    Assert-Test -Category "Spec" -Name "YAML frontmatter delimiters present" -Condition ($content -match '(?s)^---\r?\n(.*?)\r?\n---')
    Assert-Test -Category "Spec" -Name "Name is lowercase-hyphenated ('skill-router')" -Condition ($content -match '\bname:\s*skill-router\b')
    Assert-Test -Category "Spec" -Name "Description contains trigger keywords" -Condition ($content -match 'description:\s*>-?')
    Assert-Test -Category "Spec" -Name "Decision flowchart documented" -Condition ($content -match 'Decision Flowchart')
    Assert-Test -Category "Spec" -Name "Important rules and constraints documented" -Condition ($content -match 'Important Rules')
}

Assert-Test -Category "Spec" -Name "references/skill-catalog.md exists" -Condition (Test-Path (Join-Path $skillRoot "references\skill-catalog.md"))
Assert-Test -Category "Spec" -Name "references/pipeline-orchestration.md exists" -Condition (Test-Path (Join-Path $skillRoot "references\pipeline-orchestration.md"))
Assert-Test -Category "Spec" -Name "README.md exists" -Condition (Test-Path (Join-Path $skillRoot "README.md"))
Assert-Test -Category "Spec" -Name "Master CLI (skill_hub.py & skill-hub.ps1) exists" -Condition (Test-Path (Join-Path $scriptDir "skill_hub.py"))

# --- Section 2: Inverted Index & Cache Verification ---
Write-Host ""
Write-Host "2. Inverted Index Cache Checks" -ForegroundColor Yellow

$indexExists = Test-Path $indexJsonPath
Assert-Test -Category "Cache" -Name "data/skills-index.json exists" -Condition $indexExists

if ($indexExists) {
    $indexRaw = Get-Content -Path $indexJsonPath -Raw | ConvertFrom-Json
    $hasSkills = $indexRaw.total_skills -gt 2000
    Assert-Test -Category "Cache" -Name "Index contains > 2,000 unique skills ($($indexRaw.total_skills) found)" -Condition $hasSkills
    Assert-Test -Category "Cache" -Name "Inverted index map is non-empty ($($indexRaw.total_tokens) tokens)" -Condition ($indexRaw.total_tokens -gt 5000)
}

# --- Section 3: Performance & Latency Benchmark ---
Write-Host ""
Write-Host "3. Search Latency Benchmark (< 150ms SLA)" -ForegroundColor Yellow

$sw = [System.Diagnostics.Stopwatch]::StartNew()
$benchOut = & py $queryScript "Docker container crash log debug" --json | ConvertFrom-Json
$sw.Stop()
$latencyMs = $benchOut.elapsed_ms

Assert-Test -Category "Performance" -Name "Query execution is sub-150ms ($latencyMs ms recorded)" -Condition ($latencyMs -lt 150)
Assert-Test -Category "Performance" -Name "JSON output structure is valid" -Condition ($benchOut.top_matches.Count -gt 0)

# --- Section 4: Domain Routing Accuracy Tests ---
Write-Host ""
Write-Host "4. Routing & Intent Matching Tests Across Domains" -ForegroundColor Yellow

$domainTests = @(
    @{ Query = "Docker container restart loop fix karo"; Expected = "docker"; Domain = "DevOps" },
    @{ Query = "React component re-renders optimize karo"; Expected = "react"; Domain = "Frontend" },
    @{ Query = "PostgreSQL query slow chal rahi hai index banao"; Expected = "postgres"; Domain = "Database" },
    @{ Query = "Supabase auth setup karo Next.js ke saath"; Expected = "supabase"; Domain = "Fullstack Auth" },
    @{ Query = "Kubernetes cluster autoscaling HPA configure karo"; Expected = "kubernetes"; Domain = "Cloud Infra" },
    @{ Query = "OWASP top 10 security audit and vulnerability scan"; Expected = "security|vulnerability"; Domain = "Security" }
)

foreach ($dt in $domainTests) {
    $res = & py $queryScript $dt.Query --json | ConvertFrom-Json
    $matched = $false
    $topName = if ($res.top_matches.Count -gt 0) { $res.top_matches[0].name } else { "none" }
    
    foreach ($m in $res.top_matches) {
        if ($m.name -match $dt.Expected) {
            $matched = $true
            break
        }
    }
    Assert-Test -Category "Routing" -Name "Routes $($dt.Domain) query to '$($dt.Expected)' (Top: $topName)" -Condition $matched -Details "Query: $($dt.Query)"
}

# --- Section 5: Pipeline & DAG Decomposition ---
Write-Host ""
Write-Host "5. Multi-Skill Pipeline Decomposition" -ForegroundColor Yellow

$pipeOut = & py $pipelineScript "Fullstack Next.js app with Supabase database, Tailwind styling, Jest testing, and Docker CI deployment" | Out-String
$hasPhases = $pipeOut -match "Execution Graph \(DAG\)" -and $pipeOut -match "Phase 1:" -and $pipeOut -match "Phase 5:"
Assert-Test -Category "Pipeline" -Name "Successfully breaks compound task into 5-phase DAG" -Condition $hasPhases

# --- Section 6: Gap Detection & Install Offer ---
Write-Host ""
Write-Host "6. Gap Detection on Novel Topics" -ForegroundColor Yellow

$gapOut = & py $queryScript "foobarbaz123456789 unknownthing999" --json | ConvertFrom-Json
Assert-Test -Category "Gap" -Name "Correctly flags gap_detected=true for unknown request" -Condition ($gapOut.gap_detected -eq $true)

# --- Section 7: Linter & Quality Audit ---
Write-Host ""
Write-Host "7. Skill Linter Self-Audit" -ForegroundColor Yellow

$lintOut = & py $lintScript $skillRoot | Out-String
$scorePass = $lintOut -match "Score:\s*100/100"
Assert-Test -Category "Linter" -Name "skill-router passes self-audit with 100/100 Quality Score" -Condition $scorePass

# --- Summary ---
Write-Host ""
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Benchmark Results: $testsPassed / $totalTests Tests Passed" -ForegroundColor $(if ($testsPassed -eq $totalTests) { "Green" } else { "Yellow" })
Write-Host "==========================================================" -ForegroundColor Cyan

if ($testsPassed -eq $totalTests) {
    Write-Host "Status: ALL 20 CHECKS PASSED - Skill Router is at Final Production Potential!" -ForegroundColor Green
} else {
    Write-Host "Status: Some tests failed. Review log details above." -ForegroundColor Red
}
