# Skill Catalog & Installation Reference

This document serves as the extended reference for `skill-router`.
It contains guidelines for discovering, cataloging, and installing skills
from various sources.

---

## Skill Discovery Paths

The router scans these paths in priority order:

| Priority | Location                                  | Scope     | Description                          |
| :------- | :---------------------------------------- | :-------- | :----------------------------------- |
| 1        | `.agents/skills/*/SKILL.md`               | Workspace | Project-specific skills (VCS shared) |
| 2        | `~/.gemini/config/skills/*/SKILL.md`      | Global    | User-wide skills (all projects)      |
| 3        | `~/.gemini/config/plugins/*/skills/*/SKILL.md` | Global | Plugin-bundled skills                |
| 4        | Built-in system skills                    | System    | Pre-loaded by Antigravity            |

---

## How to Install a New Skill

### Option A: Workspace-Level (This Project Only)

```powershell
# Create skill directory
New-Item -ItemType Directory -Path ".agents/skills/<skill-name>" -Force

# Create SKILL.md with frontmatter
@"
---
name: <skill-name>
description: >-
  Use this skill when [trigger condition].
---

# <Skill Title>

## Instructions
1. Step 1
2. Step 2
"@ | Set-Content ".agents/skills/<skill-name>/SKILL.md"
```

### Option B: Global-Level (All Projects)

```powershell
# Create skill directory
$skillPath = "$env:USERPROFILE\.gemini\config\skills\<skill-name>"
New-Item -ItemType Directory -Path $skillPath -Force

# Create SKILL.md
@"
---
name: <skill-name>
description: >-
  Use this skill when [trigger condition].
---

# <Skill Title>

## Instructions
1. Step 1
2. Step 2
"@ | Set-Content "$skillPath\SKILL.md"
```

---

## Skill Quality Checklist

Before installing or recommending a skill, verify:

- [ ] `SKILL.md` has valid YAML frontmatter with `name` and `description`
- [ ] `description` starts with "Use this skill when..." or "Use when..."
- [ ] Instructions are clear, step-by-step, and verifiable
- [ ] No sensitive credentials or secrets hardcoded
- [ ] Total SKILL.md is under 500 lines (use `references/` for more)

---

## Common Skill Categories

| Category       | Example Skills                                | Typical Triggers                          |
| :------------- | :-------------------------------------------- | :---------------------------------------- |
| Frontend       | react-patterns, nextjs-best-practices, shadcn | "React", "component", "UI", "frontend"   |
| Backend        | fastapi-pro, django-pro, golang-pro           | "API", "server", "backend", "endpoint"   |
| DevOps         | docker-expert, kubernetes-architect, terraform | "deploy", "container", "infrastructure"  |
| Security       | security-auditor, vulnerability-scanner       | "security", "audit", "vulnerability"     |
| Database       | postgres-best-practices, sql-pro              | "database", "SQL", "query", "migration"  |
| Testing        | tdd-workflow, playwright-skill, e2e-testing   | "test", "debug", "coverage", "assertion" |
| Documentation  | docs-generator, readme, wiki-builder          | "document", "readme", "wiki", "docs"     |
| Git/GitHub     | github, git-pr-review, pr-writer              | "PR", "commit", "branch", "merge"        |
| SEO/Marketing  | seo-audit, content-creator, schema-markup     | "SEO", "marketing", "content", "ranking" |
| AI/ML          | rag-engineer, prompt-engineering, langfuse     | "AI", "model", "embedding", "LLM"       |
