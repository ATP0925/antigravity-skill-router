#!/usr/bin/env bash
# skill-hub.sh
# Universal Master CLI for AI Agent Skill Router
# Works across all Unix, macOS, Linux, and WSL environments.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Select available python interpreter
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    if command -v python &> /dev/null; then
        PYTHON_CMD="python"
    elif command -v py &> /dev/null; then
        PYTHON_CMD="py"
    else
        echo "Error: Python 3 is required to run skill-router." >&2
        exit 1
    fi
fi

exec "$PYTHON_CMD" "$SCRIPT_DIR/skill_hub.py" "$@"
