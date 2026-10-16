# AGENTS.md — Universal Agent Instructions

## Skill Router Orchestration
This repository integrates with the **Universal AI Skill Router**.
All agents (Antigravity, Claude Code, Cursor, Windsurf, Copilot, Cline) must query `scripts/skill_hub.py` before executing complex multi-step tasks.

### Commands:
- Single skill lookup: `python scripts/skill_hub.py route "<query>"`
- Multi-step DAG pipeline: `python scripts/skill_hub.py pipeline "<query>"`
- System status check: `python scripts/skill_hub.py status`
