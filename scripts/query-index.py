#!/usr/bin/env python3
"""
query-index.py
High-speed Sub-10ms Skill Intent Matcher & Router
Uses pre-compiled inverted index for instant matching.
"""

import sys
import os
import json
import re
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
LOCAL_DATA_FILE = SCRIPT_DIR.parent / "data" / "skills-index.json"
GLOBAL_DATA_FILE = Path(os.path.expanduser("~/.gemini/config/skills/skill-router/data/skills-index.json"))
DATA_FILE = LOCAL_DATA_FILE if LOCAL_DATA_FILE.exists() else GLOBAL_DATA_FILE

STOP_WORDS = {
    "a", "an", "the", "in", "on", "at", "to", "for", "of", "with", "by", "is",
    "am", "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "do", "does", "did", "and", "or", "but", "if", "then", "else", "when",
    "up", "down", "in", "out", "over", "under", "again", "further", "then",
    "once", "here", "there", "all", "any", "both", "each", "few", "more",
    "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same",
    "so", "than", "too", "very", "can", "will", "just", "should", "now",
    # Hindi/Hinglish stop words and common conversation fillers
    "karo", "karna", "karein", "hai", "hain", "mera", "meri", "mere", "kaise",
    "aur", "ko", "ke", "ki", "ka", "se", "banao", "likho", "batao", "chahiye",
    "yeh", "woh", "isme", "usme", "mai", "mein", "par", "pe", "kar", "raha", "rahi",
    "rahe", "hoga", "hogi", "bhi", "toh", "to", "kuch", "mujhe", "humko", "aap",
    "tum", "tu", "bhai", "yaar", "sir", "please", "plz", "chal", "nahi", "na", "theek",
    "wala", "wali", "wale", "kardo", "kardiya", "dekh", "liye", "gaya", "gayi",
    "kisi", "tarah", "aagar", "agar", "fir", "phir", "but", "also", "eisme", "isme",
    "kya", "kyu", "kyun", "kab", "kisko", "kaha", "kahin", "me", "kare", "karega",
    "karegi", "karenge", "apna", "apne", "apni", "de", "do", "dena", "diya"
}

INTENT_SYNONYMS = {
    # Hindi/Hinglish action & domain colloquialisms
    "banana": ["build", "create", "scaffold"],
    "banao": ["build", "create", "scaffold"],
    "phat": ["crash", "error", "bug", "debug"],
    "phata": ["crash", "error", "bug", "debug"],
    "fat": ["crash", "error", "bug", "debug"],
    "fata": ["crash", "error", "bug", "debug"],
    "toot": ["broken", "error", "bug", "debug"],
    "toota": ["broken", "error", "bug", "debug"],
    "rok": ["stop", "pause", "kill"],
    "roko": ["stop", "pause", "kill"],
    "bhejo": ["push", "deploy", "commit"],
    "bhejna": ["push", "deploy", "commit"],
    "daal": ["push", "commit", "save", "git"],
    "daalo": ["push", "commit", "save", "git"],
    "chala": ["run", "test", "execute"],
    "chalao": ["run", "test", "execute"],
    "chalana": ["run", "test", "execute"],
    "jodo": ["integrate", "connect", "api"],
    "jodna": ["integrate", "connect", "api"],
    "slow": ["performance", "speed", "profile", "latency"],
    "hang": ["performance", "memory", "leak", "freeze"],
    "dikkat": ["bug", "error", "debug", "issue"],
    "gadbad": ["bug", "error", "debug", "issue"],
    "sudhar": ["fix", "refactor", "clean", "simplify"],
    "sudharo": ["fix", "refactor", "clean", "simplify"],
    "safai": ["cleanup", "refactor", "clean"],
    "samjhao": ["explain", "documentation", "guide"],
    "suraksha": ["security", "audit", "vulnerability"],
    "jaanch": ["test", "audit", "verify", "validate"],
    "uda": ["delete", "remove", "clean"],
    "hata": ["delete", "remove", "clean"],
    "hatao": ["delete", "remove", "clean"],
    "gandi": ["design", "ui", "ux", "frontend"],
    "mast": ["high-end", "design", "ui", "ux"],
    "sundar": ["design", "ui", "ux", "frontend"],
}

def clean_tokens(text: str) -> list[str]:
    words = re.findall(r'[a-zA-Z0-9_-]{2,}', text.lower())
    result = []
    expanded = []
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
            if w_clean in INTENT_SYNONYMS:
                expanded.extend(INTENT_SYNONYMS[w_clean])

    combined = result + expanded
    return list(dict.fromkeys(combined))

def match_skills(query: str, top_k: int = 5, json_output: bool = False, explain: bool = False, force_reindex: bool = False):
    start_time = time.time()
    build_script = SCRIPT_DIR / "build-index.py"
    
    # Self-healing & staleness check: if index missing, empty, stale (>24h), or requested
    needs_rebuild = force_reindex or not DATA_FILE.exists() or DATA_FILE.stat().st_size == 0
    if not needs_rebuild and DATA_FILE.exists():
        age_hours = (time.time() - DATA_FILE.stat().st_mtime) / 3600.0
        if age_hours > 24.0:
            needs_rebuild = True

    if needs_rebuild and build_script.exists():
        import subprocess
        subprocess.run([sys.executable, str(build_script)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if not DATA_FILE.exists():
        print(f"Error: Index file not found at {DATA_FILE}. Run build-index.py first.", file=sys.stderr)
        sys.exit(1)

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    skills = data["skills"]
    inverted_index = data["inverted_index"]

    tokens = clean_tokens(query)
    if not tokens:
        if json_output:
            print(json.dumps({"status": "empty_query", "matches": []}))
        else:
            print("Query contains no searchable tokens.")
        return

    # Score calculation
    candidate_scores = {}
    matched_tokens_per_skill = {}

    for token in tokens:
        # Exact token matches in index
        if token in inverted_index:
            for skill_idx in inverted_index[token]:
                candidate_scores[skill_idx] = candidate_scores.get(skill_idx, 0) + 12
                matched_tokens_per_skill.setdefault(skill_idx, set()).add(f"token:{token}")

        # Prefix / substring matches in token vocabulary for flexibility
        for vocab_token, skill_indices in inverted_index.items():
            if len(token) >= 4 and len(vocab_token) >= 4 and (token in vocab_token or vocab_token in token) and token != vocab_token:
                for skill_idx in skill_indices:
                    candidate_scores[skill_idx] = candidate_scores.get(skill_idx, 0) + 4
                    matched_tokens_per_skill.setdefault(skill_idx, set()).add(f"fuzzy:{token}~{vocab_token}")

    # Name-specific weighting and workspace priority
    for skill_idx, score in candidate_scores.items():
        skill = skills[skill_idx]
        skill_name = skill["name"].lower()
        
        # Exact or strong name match
        for token in tokens:
            if token == skill_name:
                candidate_scores[skill_idx] += 60
                matched_tokens_per_skill[skill_idx].add(f"exact_name:{token}")
            elif token in skill_name.split("-"):
                # Clean word boundary in hyphenated name (e.g., 'docker' in 'docker-expert')
                candidate_scores[skill_idx] += 35
                matched_tokens_per_skill[skill_idx].add(f"name_word:{token}")
            elif token in skill_name:
                candidate_scores[skill_idx] += 15
                matched_tokens_per_skill[skill_idx].add(f"sub_name:{token}")

        # Penalty if skill is platform-specific (apple/macos/ios) and query does NOT mention it
        platform_keywords = {"apple", "macos", "mac", "ios", "windows", "linux", "android"}
        for pk in platform_keywords:
            if pk in skill_name and pk not in tokens:
                candidate_scores[skill_idx] -= 25

        # Workspace priority
        if skill["scope"] == "workspace":
            candidate_scores[skill_idx] += 15

    # Filter and rank
    ranked_indices = sorted(candidate_scores.keys(), key=lambda i: candidate_scores[i], reverse=True)
    
    results = []
    for idx in ranked_indices[:top_k]:
        skill = skills[idx]
        score = candidate_scores[idx]
        results.append({
            "name": skill["name"],
            "score": score,
            "category": skill["category"],
            "scope": skill["scope"],
            "path": skill["path"],
            "description": skill["description"],
            "matched_terms": list(matched_tokens_per_skill.get(idx, []))
        })

    elapsed_ms = (time.time() - start_time) * 1000

    # Compound query detection (spans multiple major categories)
    top_categories = list(dict.fromkeys(r["category"] for r in results[:4]))
    compound_detected = len(top_categories) >= 2 and any(c in top_categories for c in ["frontend", "backend", "database", "devops", "security", "ai_ml"])

    if json_output:
        out = {
            "query": query,
            "tokens": tokens,
            "elapsed_ms": round(elapsed_ms, 2),
            "total_matches": len(ranked_indices),
            "gap_detected": len(results) == 0 or results[0]["score"] < 10,
            "compound_detected": compound_detected,
            "categories_spanned": top_categories if compound_detected else [],
            "top_matches": results
        }
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return

    print("========================================")
    print("  Skill Router - Fast Intent Matcher")
    print("========================================")
    print(f"Query: \"{query}\"")
    print(f"Extracted Keywords: {', '.join(tokens)}")
    print(f"Search Latency: {elapsed_ms:.2f} ms")
    print()

    if not results or results[0]["score"] < 10:
        print("[!] GAP DETECTED: No strong matching skill installed.")
        print(f"Suggested Action: Offer to install or scaffold a new skill for: '{query}'")
        print("Scaffold Command: .\\scripts\\scaffold-skill.ps1 -Name <skill-name> -Description <desc>")
    else:
        print(f"Found {len(ranked_indices)} matching candidate(s). Top recommendations:\n")
        for i, res in enumerate(results, 1):
            print(f"[{i}] {res['name']} (Score: {res['score']}) [{res['scope'].upper()}] - Category: {res['category']}")
            if explain:
                print(f"    Match Signals: {', '.join(res['matched_terms'])}")
            else:
                print(f"    Matches : {', '.join(res['matched_terms'][:5])}")
            print(f"    Path    : {res['path']}")
            print(f"    Desc    : {res['description'][:130]}...")
            print()

        if compound_detected:
            print(f"💡 Multi-Domain Workflow Detected across: {', '.join(top_categories)}")
            print(f"   Suggestion: Run 'py scripts/route_pipeline.py \"{query}\"' to generate an ordered execution DAG!\n")

        print(f"Action: Agent should activate option [1] ({results[0]['name']})")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python query-index.py \"<user query>\" [--json] [--top <N>] [--explain] [--reindex]")
        sys.exit(1)

    raw_query = sys.argv[1]
    is_json = "--json" in sys.argv
    is_explain = "--explain" in sys.argv
    do_reindex = "--reindex" in sys.argv
    top = 5
    if "--top" in sys.argv:
        try:
            top = int(sys.argv[sys.argv.index("--top") + 1])
        except (ValueError, IndexError):
            pass

    match_skills(raw_query, top_k=top, json_output=is_json, explain=is_explain, force_reindex=do_reindex)

