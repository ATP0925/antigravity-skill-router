#!/usr/bin/env python3
"""
route_pipeline.py
Multi-Skill Pipeline & DAG Decomposition Engine for Antigravity AI Agent
Breaks complex requests into ordered execution stages with matched skills.
"""

import sys
import json
import re
import time
import os
from pathlib import Path
SCRIPT_DIR = Path(__file__).resolve().parent
LOCAL_DATA_FILE = SCRIPT_DIR.parent / "data" / "skills-index.json"
GLOBAL_DATA_FILE = Path(os.path.expanduser("~/.gemini/config/skills/skill-router/data/skills-index.json"))
DATA_FILE = LOCAL_DATA_FILE if LOCAL_DATA_FILE.exists() else GLOBAL_DATA_FILE

# 5 Standard Engineering Stages
STAGES = [
    {
        "stage": 1,
        "name": "Architecture & Scaffold",
        "keywords": ["scaffold", "setup", "arch", "architecture", "structure", "api-design", "boilerplate", "clean-code", "init", "create", "fullstack", "app", "application"]
    },
    {
        "stage": 2,
        "name": "Data Model & Backend / Auth",
        "keywords": ["database", "schema", "postgres", "sql", "prisma", "auth", "supabase", "clerk", "jwt", "backend", "orm", "api"]
    },
    {
        "stage": 3,
        "name": "Frontend & UI Design",
        "keywords": ["frontend", "ui", "ux", "react", "nextjs", "tailwind", "css", "component", "styling", "design", "shadcn", "client"]
    },
    {
        "stage": 4,
        "name": "Testing & Validation",
        "keywords": ["test", "testing", "tdd", "jest", "pytest", "unit", "e2e", "playwright", "coverage", "a11y", "validation", "lint"]
    },
    {
        "stage": 5,
        "name": "DevOps & CI/CD",
        "keywords": ["docker", "deploy", "ci", "cd", "github-actions", "kubernetes", "k8s", "vercel", "aws", "terraform", "container"]
    }
]

# Meta-Agent Workflow Stages (Autonomous Execution Loop)
META_STAGES = [
    {
        "stage": 1,
        "name": "Task Planning & Checklist",
        "keywords": ["plan", "plane", "planning", "checklist", "breakdown", "roadmap", "strategy", "indirect", "patahi"],
        "target_skills": ["concise-planning", "writing-plans", "plan-writing"]
    },
    {
        "stage": 2,
        "name": "Goal Loop & Autonomy Scope",
        "keywords": ["goal", "gole", "autonomous", "loop", "target", "objective"],
        "target_skills": ["goal-loop", "spec-driven-loop"]
    },
    {
        "stage": 3,
        "name": "Phased Execution & Implementation",
        "keywords": ["execute", "execution", "implement", "build", "install", "publish", "run", "karo", "karna"],
        "target_skills": ["executing-plans", "subagent-driven-development", "implement"]
    },
    {
        "stage": 4,
        "name": "Ground-Truth Verification & Review",
        "keywords": ["verify", "verification", "check", "audit", "validate", "review", "test-pass", "done", "poora"],
        "target_skills": ["verification-before-completion", "dos-verify-done-claims", "lint-and-validate"]
    }
]

def decompose_prompt(query: str):
    start_time = time.time()

    if not DATA_FILE.exists():
        print(f"Error: Index file not found at {DATA_FILE}. Run build-index.py first.", file=sys.stderr)
        sys.exit(1)

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    skills = data["skills"]
    inverted_index = data["inverted_index"]

    # Match tokens in query
    query_lower = query.lower()
    raw_tokens = re.findall(r'[a-zA-Z0-9_-]{2,}', query_lower)

    matched_stages = []

    # 1. Check Meta-Workflow Stages (Plan -> Goal -> Execute -> Verify)
    is_meta = any(w in query_lower for w in ["plan", "plane", "goal", "gole", "execute", "verify", "indirect", "patahi"])
    if is_meta:
        for stage_info in META_STAGES:
            stage_num = stage_info["stage"]
            stage_name = stage_info["name"]
            stage_kws = stage_info["keywords"]
            targets = stage_info["target_skills"]

            # Check if this meta stage is hit
            if any(re.search(r'\b' + re.escape(kw) + r'\b', query_lower) for kw in stage_kws) or any(t in raw_tokens for t in stage_kws):
                # Find matching target skill from loaded skills
                found_skill = None
                for t in targets:
                    for s in skills:
                        if s["name"].lower() == t:
                            found_skill = s
                            break
                    if found_skill:
                        break

                if found_skill:
                    matched_stages.append({
                        "stage": stage_num,
                        "stage_name": stage_name,
                        "triggered_by": [kw for kw in stage_kws if kw in query_lower],
                        "skill": found_skill["name"],
                        "category": found_skill["category"],
                        "path": found_skill["path"],
                        "description": found_skill["description"][:120] + "..."
                    })

    # 2. Check Standard Engineering Stages (Architecture -> DB -> UI -> Test -> DevOps)
    if not matched_stages:
        for stage_info in STAGES:
            stage_num = stage_info["stage"]
            stage_name = stage_info["name"]
            stage_kws = stage_info["keywords"]

            # Check if query matches this stage's domain
            stage_hits = [kw for kw in stage_kws if re.search(r'\b' + re.escape(kw) + r'\b', query_lower)]

            # Stage category constraints
            stage_categories = {
                1: ["frontend", "backend", "docs_design", "general"],
                2: ["backend", "database", "security"],
                3: ["frontend", "docs_design"],
                4: ["testing"],
                5: ["devops", "git"]
            }
            allowed_cats = stage_categories.get(stage_num, [])

            if stage_hits or any(token in stage_kws for token in raw_tokens):
                # Find best skill for this specific stage
                candidate_scores = {}
                for kw in stage_hits:
                    if kw in inverted_index:
                        for s_idx in inverted_index[kw]:
                            if not allowed_cats or skills[s_idx]["category"] in allowed_cats:
                                candidate_scores[s_idx] = candidate_scores.get(s_idx, 0) + 20

                # Score matching query tokens
                for token in raw_tokens:
                    if token in inverted_index:
                        for s_idx in inverted_index[token]:
                            if not allowed_cats or skills[s_idx]["category"] in allowed_cats:
                                candidate_scores[s_idx] = candidate_scores.get(s_idx, 0) + 10

                # Bonus for skill name matching stage keyword
                for s_idx in list(candidate_scores.keys()):
                    s_name = skills[s_idx]["name"].lower()
                    for token in raw_tokens:
                        if token in s_name.split("-"):
                            candidate_scores[s_idx] += 30

                # Find top skill
                if candidate_scores:
                    best_idx = max(candidate_scores.keys(), key=lambda i: candidate_scores[i])
                    best_skill = skills[best_idx]
                    matched_stages.append({
                        "stage": stage_num,
                        "stage_name": stage_name,
                        "triggered_by": stage_hits,
                        "skill": best_skill["name"],
                        "category": best_skill["category"],
                        "path": best_skill["path"],
                        "description": best_skill["description"][:120] + "..."
                    })

    elapsed_ms = (time.time() - start_time) * 1000

    print("=================================================")
    print(" Multi-Skill Execution Pipeline (DAG Planner)")
    print("=================================================")
    print(f"Goal Prompt : \"{query}\"")
    print(f"Planner Time: {elapsed_ms:.2f} ms")
    print(f"Identified  : {len(matched_stages)} Phased Stages\n")

    if not matched_stages:
        print("[!] Task does not require multi-skill chaining. Use single skill route:")
        print(f"    py scripts/query-index.py \"{query}\"")
        return

    print("Execution Graph (DAG):")
    print("-------------------------------------------------")
    for s in matched_stages:
        print(f"Phase {s['stage']}: {s['stage_name']}")
        print(f"  --> Active Skill : {s['skill']} ({s['category']})")
        print(f"      Path         : {s['path']}")
        print(f"      Description  : {s['description']}")
        print()

    print("-------------------------------------------------")
    print("Pipeline Ready: Execute Phase 1 -> Phase 2 -> ... sequentially.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: py route_pipeline.py \"<complex user request>\"")
        sys.exit(1)

    decompose_prompt(sys.argv[1])
