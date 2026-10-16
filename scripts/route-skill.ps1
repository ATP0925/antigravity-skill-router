# route-skill.ps1
# Interactive/Automated Skill Matcher and Router for Antigravity AI Agent
param(
    [Parameter(Mandatory=$true)]
    [string]$Query,

    [int]$Top = 5
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Skill Router - Intent Matcher Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "User Query: `"$Query`"" -ForegroundColor Yellow
Write-Host ""

# Clean and split keywords
$stopWords = @("a","an","the","in","on","at","to","for","of","with","by","is","am","are","karo","karna","hai","mera","meri","kaise","karein","aur","ko","ke","se","banao","likho","fix","debug","help")
$rawTokens = $Query.ToLower() -replace '[^\w\s-]', ' ' -split '\s+'
$tokens = $rawTokens | Where-Object { $_.Length -gt 1 -and $stopWords -notcontains $_ }

Write-Host "Extracted Query Keywords: $($tokens -join ', ')" -ForegroundColor DarkGray

# 1. Collect skills from Workspace, Plugins, and Global
$roots = @(
    @{ Name = "Workspace"; Path = ".agents\skills" },
    @{ Name = "Global"; Path = "$env:USERPROFILE\.gemini\config\skills" },
    @{ Name = "Plugins"; Path = "$env:USERPROFILE\.gemini\config\plugins" }
)

$candidates = [System.Collections.Generic.List[PSCustomObject]]::new()

# Fast search using directory names and frontmatter
foreach ($root in $roots) {
    if (-not (Test-Path $root.Path)) { continue }

    if ($root.Name -eq "Plugins") {
        $skillFiles = Get-ChildItem -Path $root.Path -Filter "SKILL.md" -Recurse -Depth 4 -ErrorAction SilentlyContinue
    } else {
        $skillFiles = Get-ChildItem -Path $root.Path -Filter "SKILL.md" -Recurse -Depth 2 -ErrorAction SilentlyContinue
    }

    foreach ($sf in $skillFiles) {
        $skillDir = $sf.Directory.Name
        $score = 0
        $matchedWords = [System.Collections.Generic.List[string]]::new()

        # Check name matches
        foreach ($token in $tokens) {
            if ($skillDir.ToLower() -match [regex]::Escape($token)) {
                $score += 15
                $matchedWords.Add("name:$token")
            }
        }

        # Check frontmatter description
        $headLines = Get-Content -Path $sf.FullName -TotalCount 25 -ErrorAction SilentlyContinue
        $headText = ($headLines -join " ").ToLower()

        foreach ($token in $tokens) {
            if ($headText -match "\b$([regex]::Escape($token))\b") {
                $score += 5
                if (-not $matchedWords.Contains("desc:$token")) {
                    $matchedWords.Add("desc:$token")
                }
            }
        }

        if ($score -gt 0) {
            # Extract description snippet
            $descMatch = [regex]::Match(($headLines -join "`n"), '(?s)description:\s*(?:>-\s*)?(.*?)(?:\n---|\n#)')
            $snippet = if ($descMatch.Success) {
                ($descMatch.Groups[1].Value -replace '\s+', ' ').Trim()
            } else {
                "No description available."
            }
            if ($snippet.Length -gt 120) { $snippet = $snippet.Substring(0, 117) + "..." }

            $candidates.Add([PSCustomObject]@{
                SkillName = $skillDir
                Score = $score
                Source = $root.Name
                Path = $sf.FullName
                Matched = ($matchedWords -join ", ")
                Description = $snippet
            })
        }
    }
}

# Sort candidates by score descending
$sorted = $candidates | Sort-Object -Property Score -Descending | Select-Object -First $Top

if ($sorted.Count -gt 0) {
    Write-Host "Found $($candidates.Count) potential match(es). Top recommendations:" -ForegroundColor Green
    Write-Host ""
    $rank = 1
    foreach ($c in $sorted) {
        Write-Host "[$rank] $($c.SkillName) (Score: $($c.Score)) [$($c.Source)]" -ForegroundColor White -NoNewline
        Write-Host " - Matches: $($c.Matched)" -ForegroundColor DarkCyan
        Write-Host "    Path: $($c.Path)" -ForegroundColor DarkGray
        Write-Host "    Desc: $($c.Description)" -ForegroundColor Gray
        Write-Host ""
        $rank++
    }

    Write-Host "Action: Agent should auto-activate option [1] ($($sorted[0].SkillName))" -ForegroundColor Green
} else {
    Write-Host "No matching skills found for query." -ForegroundColor Yellow
    Write-Host "GAP DETECTED: Prompt user whether to install/create a custom skill for: $Query" -ForegroundColor Magenta
}
