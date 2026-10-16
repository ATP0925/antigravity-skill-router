#!/usr/bin/env python3
"""
scaffold_skill.py
Automated Skill Generator & Installer for Antigravity AI Agent
Creates 100% compliant Antigravity skills with progressive disclosure.
"""

import sys
import os
import re
import argparse
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = Path.cwd() if (Path.cwd() / ".agents").exists() else Path("C:/Users/atpad/.gemini/antigravity-ide/scratch/my-skills-workspace")
GLOBAL_CONFIG = Path(os.path.expanduser("~/.gemini/config"))

TEMPLATES = {
    "workflow": """---
name: {name}
description: >-
  Use this skill when {description_trigger}.
  Triggers on keywords: {keywords}.
---

# {title}

{overview}

## Core Procedures

### 1. Pre-Flight Checks
- [ ] Confirm prerequisite tools and configurations are present.
- [ ] Check active workspace context and parameters.

### 2. Execution Steps
1. **Analyze input**: Inspect requirements, files, or environment.
2. **Execute core logic**:
   - Run helper script: [`helper.ps1`](./scripts/helper.ps1)
   - Follow domain guidelines in [`references/workflow-guide.md`](./references/workflow-guide.md).
3. **Verify outcome**:
   - Verify artifacts or outputs against validation checklist.

### 3. Post-Action Verification
- Ensure zero errors or unhandled warnings.
- Report concise summary of changes and actions taken to user.

## Limitations & Edge Cases
- Do not make assumptions about external dependencies without verifying.
- Preserves user safety: prompt before any destructive file or database modifications.
""",
    "tool": """---
name: {name}
description: >-
  Use this skill when {description_trigger}.
  Triggers on: {keywords}.
---

# {title}

## Purpose
Provides automated tooling and helper scripts for {name}.

## Available Scripts
- [`scripts/helper.ps1`](./scripts/helper.ps1): Primary automation script.

## Usage
Execute script with specific actions:
```powershell
powershell.exe -ExecutionPolicy Bypass -File "./scripts/helper.ps1" -Action "run"
```

## Validation Checklist
- [ ] Script exited with code 0.
- [ ] Expected output files created.
""",
    "audit": """---
name: {name}
description: >-
  Use this skill when {description_trigger}.
  Triggers on: {keywords}, audit, review, check, verify.
---

# {title}

## Audit Workflow

### 1. Scope Definition
- Identify target files, endpoints, or components to inspect.

### 2. Inspection Matrix
| Area | Checkpoint | Severity | Action |
| :--- | :--------- | :------- | :----- |
| Syntax / Spec | Frontmatter, formatting, rules | High | Fix or report |
| Reliability | Edge cases, timeouts, exceptions | Medium | Add safeguards |
| Quality | Best practices & token budget | Low | Refactor |

### 3. Findings Report
Generate structured report with actionable remediations.
"""
}

def clean_skill_name(name: str) -> str:
    cleaned = re.sub(r'[^a-zA-Z0-9-]', '-', name.lower().strip())
    cleaned = re.sub(r'-+', '-', cleaned).strip('-')
    return cleaned

def scaffold_skill(name: str, description: str, scope: str = "workspace", template: str = "workflow", keywords: str = ""):
    skill_name = clean_skill_name(name)
    if not skill_name:
        print("Error: Invalid skill name.", file=sys.stderr)
        return False

    if scope.lower() == "global":
        target_dir = GLOBAL_CONFIG / "skills" / skill_name
    else:
        target_dir = WORKSPACE_ROOT / ".agents" / "skills" / skill_name

    if target_dir.exists():
        print(f"Error: Skill '{skill_name}' already exists at {target_dir}", file=sys.stderr)
        return False

    print(f"Creating skill '{skill_name}' at: {target_dir}")

    # Prepare template variables
    title = " ".join(word.capitalize() for word in skill_name.split("-"))
    desc_clean = description.strip()
    if not desc_clean.lower().startswith("use"):
        desc_clean = f"the user wants to {desc_clean}"
    else:
        desc_clean = re.sub(r'^(use this skill when|use when)\s*', '', desc_clean, flags=re.IGNORECASE)

    kw_list = [k.strip() for k in keywords.split(",") if k.strip()] if keywords else skill_name.split("-")
    kw_str = ", ".join(kw_list)

    tmpl = TEMPLATES.get(template.lower(), TEMPLATES["workflow"])
    skill_content = tmpl.format(
        name=skill_name,
        title=title,
        description_trigger=desc_clean,
        keywords=kw_str,
        overview=f"Automated workflow and runbook for **{title}**."
    )

    # Directories
    scripts_dir = target_dir / "scripts"
    refs_dir = target_dir / "references"
    target_dir.mkdir(parents=True, exist_ok=True)
    scripts_dir.mkdir(exist_ok=True)
    refs_dir.mkdir(exist_ok=True)

    # 1. SKILL.md
    (target_dir / "SKILL.md").write_text(skill_content, encoding="utf-8")

    # 2. README.md
    readme_content = f"""# {title}

## Description
{desc_clean}

## Directory Layout
- `SKILL.md`: Main instructions and triggers for the agent.
- `references/workflow-guide.md`: Detailed guidance and references.
- `scripts/helper.ps1`: Automation helper script.

## Installation Scope
Scope: `{scope.upper()}`
Location: `{target_dir}`
"""
    (target_dir / "README.md").write_text(readme_content, encoding="utf-8")

    # 3. references/workflow-guide.md
    ref_content = f"""# {title} — Reference Guide

This document contains deep technical guidance, best practices, and extended
examples for `{skill_name}`.

## Architectural Notes
- Keep heavy instructions here to optimize main SKILL.md token usage.
- Progressive disclosure ensures the agent only loads this when needed.
"""
    (refs_dir / "workflow-guide.md").write_text(ref_content, encoding="utf-8")

    # 4. scripts/helper.ps1
    helper_content = f"""# Helper script for {skill_name}
param([string]$Action = "status")

Write-Host "[{skill_name}] Executing action: $Action" -ForegroundColor Cyan
switch ($Action.ToLower()) {{
    "status" {{ Write-Host "Skill is installed and operational." -ForegroundColor Green }}
    default  {{ Write-Host "Action $Action completed successfully." -ForegroundColor Yellow }}
}}
"""
    (scripts_dir / "helper.ps1").write_text(helper_content, encoding="utf-8")

    print(f"Skill '{skill_name}' successfully created!")
    print(f"  - SKILL.md")
    print(f"  - README.md")
    print(f"  - references/workflow-guide.md")
    print(f"  - scripts/helper.ps1")

    # Update index cache automatically
    try:
        from scripts import build_index
    except ImportError:
        # Run build-index.py script
        script_path = WORKSPACE_ROOT / ".agents/skills/skill-router/scripts/build-index.py"
        if script_path.exists():
            print("Refreshing skills index...")
            os.system(f'py "{script_path}"')

    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scaffold a new Antigravity AI Agent skill.")
    parser.add_argument("-n", "--name", required=True, help="Name of the skill (lowercase, hyphenated)")
    parser.add_argument("-d", "--description", required=True, help="When the skill should trigger / what it does")
    parser.add_argument("-s", "--scope", default="workspace", choices=["workspace", "global"], help="Workspace or Global installation")
    parser.add_argument("-t", "--template", default="workflow", choices=["workflow", "tool", "audit"], help="Template type")
    parser.add_argument("-k", "--keywords", default="", help="Comma-separated trigger keywords")

    args = parser.parse_args()
    scaffold_skill(args.name, args.description, args.scope, args.template, args.keywords)
