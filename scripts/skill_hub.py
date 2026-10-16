#!/usr/bin/env python3
"""
skill_hub.py
Unified Command-Line Interface (CLI) for Antigravity AI Agent Skill Router
Single master entrypoint for routing, pipelining, scaffolding, linting, and testing.
"""

import sys
import os
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()

BANNER = """
===========================================================
   Antigravity Skill Router Hub — Master Control Interface
===========================================================
"""

HELP_TEXT = """
Available Commands:

  route <query> [--top N] [--json]
    Find and rank the best matching skill(s) for a user request in < 100ms.

  pipeline <query>
    Decompose a complex multi-domain task into a 5-phase DAG of skills.

  index [--rebuild]
    Rebuild the full inverted-index cache across workspace, global & plugins.

  scaffold -n <name> -d <description> [-s workspace|global] [-t workflow|tool|audit]
    Interactively or automatically generate a 100% compliant Antigravity skill.

  lint [path]
    Audit skills for YAML frontmatter, token economy, links, and structure.

  test
    Run the complete automated 20+ test suite and verification benchmark.

Examples:
  py skill_hub.py route "Docker container crash ho raha hai fix karo"
  py skill_hub.py pipeline "Next.js app with Supabase and Jest"
  py skill_hub.py scaffold -n "my-new-skill" -d "automated testing helper"
  py skill_hub.py lint
  py skill_hub.py test
"""

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        print(BANNER)
        print(HELP_TEXT)
        sys.exit(0)

    cmd = sys.argv[1].lower()
    args = sys.argv[2:]

    if cmd == "route":
        if not args:
            print("Error: Please provide a query string. E.g.: py skill_hub.py route \"debug python API\"")
            sys.exit(1)
        script = SCRIPT_DIR / "query-index.py"
        subprocess.run([sys.executable, str(script)] + args)

    elif cmd == "pipeline":
        if not args:
            print("Error: Please provide a prompt. E.g.: py skill_hub.py pipeline \"Fullstack app with DB and CI\"")
            sys.exit(1)
        script = SCRIPT_DIR / "route_pipeline.py"
        subprocess.run([sys.executable, str(script)] + args)

    elif cmd == "index":
        script = SCRIPT_DIR / "build-index.py"
        subprocess.run([sys.executable, str(script)] + args)

    elif cmd == "scaffold":
        script = SCRIPT_DIR / "scaffold_skill.py"
        subprocess.run([sys.executable, str(script)] + args)

    elif cmd == "lint":
        script = SCRIPT_DIR / "lint_skills.py"
        subprocess.run([sys.executable, str(script)] + args)

    elif cmd == "test":
        script = SCRIPT_DIR / "test-skill.ps1"
        subprocess.run(["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", str(script)] + args)

    else:
        print(f"Unknown command: '{cmd}'\n")
        print(HELP_TEXT)
        sys.exit(1)

if __name__ == "__main__":
    main()
