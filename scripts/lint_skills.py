#!/usr/bin/env python3
"""
lint_skills.py
Comprehensive Quality & Spec Linter for Antigravity AI Agent Skills
Audits skills against Antigravity architectural guidelines and best practices.
"""

import sys
import os
import re
import argparse
from pathlib import Path

WORKSPACE_ROOT = Path("C:/Users/atpad/.gemini/antigravity-ide/scratch/my-skills-workspace")
GLOBAL_CONFIG = Path(os.path.expanduser("~/.gemini/config"))

def lint_skill(skill_dir: Path) -> dict:
    skill_name = skill_dir.name
    skill_md = skill_dir / "SKILL.md"

    report = {
        "name": skill_name,
        "path": str(skill_md),
        "score": 100,
        "errors": [],
        "warnings": [],
        "info": []
    }

    if not skill_md.exists():
        report["score"] = 0
        report["errors"].append("SKILL.md is missing in directory.")
        return report

    try:
        content = skill_md.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        report["score"] = 0
        report["errors"].append(f"Failed to read SKILL.md: {e}")
        return report

    lines = content.splitlines()
    line_count = len(lines)

    # 1. Frontmatter check
    fm_match = re.search(r'^---\r?\n(.*?)\r?\n---', content, re.DOTALL)
    if not fm_match:
        report["score"] -= 40
        report["errors"].append("Missing or malformed YAML frontmatter (must begin and end with '---').")
    else:
        fm_text = fm_match.group(1)

        # Check name
        name_match = re.search(r'name:\s*([^\r\n]+)', fm_text)
        if not name_match:
            report["score"] -= 20
            report["errors"].append("Frontmatter is missing 'name' field.")
        else:
            declared_name = name_match.group(1).strip().strip('"\'')
            if declared_name != skill_name:
                report["score"] -= 10
                report["warnings"].append(f"Frontmatter name '{declared_name}' does not match directory name '{skill_name}'.")
            if not re.match(r'^[a-z0-9_-]+$', declared_name):
                report["score"] -= 10
                report["warnings"].append(f"Skill name '{declared_name}' should be lowercase-hyphenated.")

        # Check description
        desc_match = re.search(r'description:\s*(?:>-\s*)?(.*?)(?:\n[a-zA-Z0-9_-]+:|$)', fm_text, re.DOTALL)
        if not desc_match or not desc_match.group(1).strip():
            report["score"] -= 25
            report["errors"].append("Frontmatter is missing or has empty 'description' field.")
        else:
            desc_val = " ".join(desc_match.group(1).split())
            if len(desc_val) < 20:
                report["score"] -= 10
                report["warnings"].append("Description is very short (< 20 chars). Add specific trigger conditions.")
            if not re.search(r'\b(use|when|trigger|agent)\b', desc_val, re.IGNORECASE):
                report["score"] -= 5
                report["warnings"].append("Description should ideally specify 'Use when...' or 'Use this skill when...' to guide the agent.")

    # 2. Token economy & progressive disclosure
    has_refs = (skill_dir / "references").exists() and any((skill_dir / "references").iterdir())
    if line_count > 500:
        if not has_refs:
            report["score"] -= 15
            report["warnings"].append(f"SKILL.md is long ({line_count} lines) without a 'references/' directory. Move deep documentation to references/ to save context window tokens.")
        else:
            report["info"].append(f"Long SKILL.md ({line_count} lines) — verify if details can be moved to references/.")

    # 3. Check internal relative links
    rel_links = re.findall(r'\[([^\]]+)\]\((?!https?://)([^)]+)\)', content)
    for text, link in rel_links:
        # Strip anchor
        clean_link = link.split('#')[0].strip()
        if not clean_link:
            continue
        target_path = (skill_dir / clean_link).resolve()
        if not target_path.exists():
            report["score"] -= 10
            report["warnings"].append(f"Broken internal link '{link}' (referenced as '{text}'). Target file does not exist.")

    # 4. Check for companion README and directories
    has_readme = (skill_dir / "README.md").exists()
    has_scripts = (skill_dir / "scripts").exists()

    if not has_readme:
        report["score"] -= 5
        report["warnings"].append("Missing README.md in skill root for human documentation.")

    if has_scripts:
        report["info"].append(f"Contains executable scripts in {skill_dir / 'scripts'}.")
    if has_refs:
        report["info"].append(f"Implements progressive disclosure with {skill_dir / 'references'}.")

    report["score"] = max(0, min(100, report["score"]))
    return report

def run_linter(target_path: Path):
    if target_path.is_file() and target_path.name == "SKILL.md":
        targets = [target_path.parent]
    elif (target_path / "SKILL.md").exists():
        targets = [target_path]
    else:
        # Scan subdirectories
        targets = [d for d in target_path.iterdir() if d.is_dir() and (d / "SKILL.md").exists()]

    if not targets:
        print(f"No skills with SKILL.md found in {target_path}")
        return

    print("=================================================")
    print(f" Antigravity Skill Linter — Auditing {len(targets)} Skill(s)")
    print("=================================================")
    print()

    total_score = 0
    passed_count = 0

    for skill_dir in sorted(targets, key=lambda x: x.name):
        res = lint_skill(skill_dir)
        total_score += res["score"]

        status = "PASS" if res["score"] >= 80 else ("WARN" if res["score"] >= 60 else "FAIL")
        print(f"[{status}] {res['name']:30} Score: {res['score']:3}/100")

        for err in res["errors"]:
            print(f"       ERROR: {err}")
        for warn in res["warnings"]:
            print(f"       WARN : {warn}")
        for info in res["info"]:
            print(f"       INFO : {info}")

        if res["score"] >= 80:
            passed_count += 1
        print()

    avg_score = total_score / len(targets)
    print("=================================================")
    print(f" Linter Summary: {passed_count}/{len(targets)} Skills Passed (Avg Score: {avg_score:.1f}/100)")
    print("=================================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lint and audit Antigravity AI Agent skills.")
    parser.add_argument("path", nargs="?", default=str(WORKSPACE_ROOT / ".agents/skills"), help="Path to a skill directory or folder of skills")
    args = parser.parse_args()

    run_linter(Path(args.path))
