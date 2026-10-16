#!/usr/bin/env python3
"""
build-index.py
High-speed Skill Catalog Indexer for Antigravity AI Agent
Scans workspace, global, and plugin skills and produces an inverted-index
JSON cache for sub-50ms intelligent routing.
"""

import os
import sys
import json
import re
import time
from pathlib import Path

# Paths configuration
SCRIPT_DIR = Path(__file__).resolve().parent
GLOBAL_CONFIG = Path(os.path.expanduser("~/.gemini/config"))
DATA_DIR = SCRIPT_DIR.parent / "data"
OUTPUT_FILE = DATA_DIR / "skills-index.json"
CWD_WORKSPACE = Path.cwd() / ".agents/skills"
DEFAULT_WORKSPACE = Path("C:/Users/atpad/.gemini/antigravity-ide/scratch/my-skills-workspace/.agents/skills")
WORKSPACE_SKILLS = CWD_WORKSPACE if CWD_WORKSPACE.exists() else DEFAULT_WORKSPACE

STOP_WORDS = {
    "a", "an", "the", "in", "on", "at", "to", "for", "of", "with", "by", "is",
    "am", "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "do", "does", "did", "and", "or", "but", "if", "then", "else", "when",
    "up", "down", "in", "out", "over", "under", "again", "further", "then",
    "once", "here", "there", "all", "any", "both", "each", "few", "more",
    "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same",
    "so", "than", "too", "very", "can", "will", "just", "should", "now",
    # Hindi/Hinglish stop words
    "karo", "karna", "karein", "hai", "hain", "mera", "meri", "mere", "kaise",
    "aur", "ko", "ke", "ki", "ka", "se", "banao", "likho", "batao", "chahiye",
    "yeh", "woh", "isme", "usme", "mai", "mein", "par", "pe"
}

CATEGORY_MAP = {
    "frontend": ["react", "vue", "angular", "nextjs", "css", "html", "tailwind", "ui", "ux", "component", "web", "svelte", "dom"],
    "backend": ["api", "fastapi", "django", "express", "node", "golang", "rust", "python", "backend", "endpoint", "rest", "graphql", "trpc", "csharp", "dotnet"],
    "devops": ["docker", "kubernetes", "k8s", "aws", "azure", "gcp", "terraform", "ci", "cd", "deploy", "pipeline", "actions", "server", "linux", "bash"],
    "database": ["postgres", "postgresql", "sql", "bigquery", "prisma", "database", "orm", "mysql", "redis", "mongodb", "sqlite", "query", "migration"],
    "security": ["security", "audit", "vulnerability", "pentest", "auth", "pci", "xss", "injection", "sast", "compliance", "hardening"],
    "testing": ["test", "testing", "tdd", "e2e", "playwright", "cypress", "jest", "pytest", "k6", "load", "benchmark", "debug"],
    "mobile": ["flutter", "react-native", "expo", "ios", "android", "swift", "swiftui", "dart", "mobile"],
    "ai_ml": ["ai", "llm", "rag", "agent", "prompt", "embedding", "langchain", "langgraph", "langfuse", "model", "eval", "vector", "huggingface"],
    "git": ["git", "github", "gitlab", "pr", "commit", "branch", "merge", "pull-request"],
    "docs_design": ["docs", "readme", "documentation", "design", "canvas", "art", "diagram", "slide", "presentation", "markdown"],
    "marketing_seo": ["seo", "marketing", "growth", "content", "copywriting", "analytics", "cro", "email", "tracking"]
}

def clean_tokens(text: str) -> list[str]:
    words = re.findall(r'[a-zA-Z0-9_-]{2,}', text.lower())
    result = []
    for w in words:
        w_clean = w.strip('_-')
        if len(w_clean) >= 2 and w_clean not in STOP_WORDS and not w_clean.isdigit():
            result.append(w_clean)
            if '-' in w_clean:
                for sub in w_clean.split('-'):
                    if len(sub) >= 2 and sub not in STOP_WORDS and not sub.isdigit():
                        result.append(sub)
            if '_' in w_clean:
                for sub in w_clean.split('_'):
                    if len(sub) >= 2 and sub not in STOP_WORDS and not sub.isdigit():
                        result.append(sub)
    return list(dict.fromkeys(result))

def infer_category(name: str, desc: str) -> str:
    combined = (name + " " + desc).lower()
    best_cat = "general"
    max_hits = 0
    for cat, kws in CATEGORY_MAP.items():
        hits = sum(1 for kw in kws if re.search(r'\b' + re.escape(kw) + r'\b', combined))
        if hits > max_hits:
            max_hits = hits
            best_cat = cat
    return best_cat

def parse_skill_md(file_path: Path, scope: str) -> dict | None:
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None

    # Parse YAML frontmatter
    fm_match = re.search(r'^---\r?\n(.*?)\r?\n---', content, re.DOTALL)
    if not fm_match:
        # Fallback: check first heading
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        name = file_path.parent.name
        desc = title_match.group(1) if title_match else f"Skill for {name}"
    else:
        fm_text = fm_match.group(1)
        name_match = re.search(r'name:\s*([^\r\n]+)', fm_text)
        name = name_match.group(1).strip().strip('"\'') if name_match else file_path.parent.name

        desc_match = re.search(r'description:\s*(?:>-\s*)?(.*?)(?:\n[a-zA-Z0-9_-]+:|$)', fm_text, re.DOTALL)
        if desc_match:
            desc = " ".join(desc_match.group(1).split())
        else:
            desc = f"Skill for {name}"

    name_clean = name.strip()
    desc_clean = desc.strip()
    category = infer_category(name_clean, desc_clean)
    tokens = clean_tokens(name_clean + " " + desc_clean)

    return {
        "name": name_clean,
        "scope": scope,
        "path": str(file_path.resolve()).replace("\\", "/"),
        "dir": str(file_path.parent.resolve()).replace("\\", "/"),
        "description": desc_clean,
        "category": category,
        "tokens": tokens,
        "has_scripts": (file_path.parent / "scripts").exists(),
        "has_references": (file_path.parent / "references").exists(),
    }

def build_index():
    start_time = time.time()
    print(f"Scanning skills across workspace, global config, and plugins...")

    scan_targets = [
        (WORKSPACE_SKILLS, "workspace", 2),
        (GLOBAL_CONFIG / "skills", "global", 2),
        (GLOBAL_CONFIG / "plugins", "plugins", 5),
    ]

    skills_dict = {}  # name -> skill_data (workspace overrides global)
    seen_paths = set()

    for base_dir, scope, max_depth in scan_targets:
        if not base_dir.exists():
            continue

        for root, dirs, files in os.walk(base_dir):
            # calculate depth
            rel_path = Path(root).relative_to(base_dir)
            if len(rel_path.parts) > max_depth:
                dirs.clear()
                continue

            if "SKILL.md" in files:
                skill_path = Path(root) / "SKILL.md"
                resolved = skill_path.resolve()
                if resolved in seen_paths:
                    continue
                seen_paths.add(resolved)

                skill_data = parse_skill_md(skill_path, scope)
                if skill_data:
                    name = skill_data["name"]
                    # Workspace priority: workspace always overwrites global/plugin
                    if name not in skills_dict or scope == "workspace":
                        skills_dict[name] = skill_data

    skills_list = list(skills_dict.values())

    # Build inverted index
    inverted_index = {}
    for idx, skill in enumerate(skills_list):
        for token in skill["tokens"]:
            if token not in inverted_index:
                inverted_index[token] = []
            inverted_index[token].append(idx)

    # Categories index
    categories_index = {}
    for idx, skill in enumerate(skills_list):
        cat = skill["category"]
        if cat not in categories_index:
            categories_index[cat] = []
        categories_index[cat].append(idx)

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    manifest = {
        "version": "1.0.0",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "generation_time_ms": int((time.time() - start_time) * 1000),
        "total_skills": len(skills_list),
        "total_tokens": len(inverted_index),
        "categories": {k: len(v) for k, v in categories_index.items()},
        "skills": skills_list,
        "inverted_index": inverted_index
    }

    OUTPUT_FILE.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    elapsed = time.time() - start_time

    print(f"Index built successfully in {elapsed:.2f}s!")
    print(f"Total Unique Skills: {len(skills_list)}")
    print(f"Total Indexed Tokens: {len(inverted_index)}")
    print(f"Categories Breakdown:")
    for cat, count in sorted(manifest["categories"].items(), key=lambda x: x[1], reverse=True):
        print(f"  - {cat:15}: {count} skills")
    print(f"Cache saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    build_index()
