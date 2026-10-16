# 🧭 Antigravity Skill Router

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Skills Indexed](https://img.shields.io/badge/Skills%20Indexed-2%2C250%2B-blue.svg)](data/skills-index.json)
[![Latency](https://img.shields.io/badge/Search%20Latency-%3C%2050ms-brightgreen.svg)](#-benchmarks)
[![Tests Passing](https://img.shields.io/badge/Tests-34%2F34%20Passing-success.svg)](#-automated-verification-suite)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-blueviolet.svg)](#-installation)
[![Antigravity](https://img.shields.io/badge/Ecosystem-Google%20Antigravity%20IDE-orange.svg)](https://deepmind.google)

**Antigravity Skill Router** is an intelligent meta-skill and autonomous orchestrator for [Google Antigravity](https://deepmind.google) AI agents (and Claude Code / Codex agent environments).

It intercepts every user prompt, extracts semantic intent, performs sub-50ms inverted-index search across **2,250+ skills**, automatically activates the exact right specialist skill, and orchestrates complex multi-stage workflows via Directed Acyclic Graph (DAG) pipelines — eliminating prompt bloat and manual skill invocation.

---

## ⚡ Why Skill Router?

Modern agent workspaces often contain dozens of specialized skills (frontend, backend, testing, security, databases, DevOps). Manually remembering and activating skills with `/skill <name>` slows down workflows and causes context fragmentation.

**Skill Router solves this completely:**
- 🔍 **Zero-Friction Discovery**: Matches intent against 2,250+ skills in **~30ms** using a pre-computed inverted index.
- 🗣️ **Hinglish & Natural Language Bridge**: Native support for colloquial Hinglish/Hindi phrasing (*"code phat gaya"*, *"website banana hai"*, *"git pe daal do"*).
- 🎯 **Auto-Activation**: Reads skill frontmatter, matches triggers, and silently loads the best skill without user intervention.
- ⛓️ **Multi-Skill DAG Pipelines**: Decomposes complex compound tasks or autonomous loops (*Plan ➔ Goal ➔ Execute ➔ Verify*) into an ordered DAG.
- 🔄 **Self-Healing & Auto-Staleness Watcher**: Automatically rebuilds index if cache is missing or older than 24 hours.
- 🚨 **Gap Detection & Self-Scaffolding**: Detects when a required capability is missing, notifies the user, and automatically scaffolds a compliant new skill with a 100/100 quality score.
- 🛡️ **Built-in Quality Linter**: Audits skills against naming conventions, YAML spec, documentation standards, and script validity.

---

## 🏗️ Architecture & Decision Flow

```mermaid
graph TD
    User([User Prompt / Request]) --> Extract[Extract Keywords, Domain & Action Type]
    Extract --> Search[Query Inverted Index < 50ms]
    
    Search --> Decision{Confidence Score}
    
    Decision -->|Strong Single Match >= 35| AutoAct[Silently Load SKILL.md & Execute Instructions]
    Decision -->|Multiple Close Matches| Interactive[Present Top 3 Ranked Choices to User]
    Decision -->|Compound Complex Request| Pipeline[Decompose into 5-Phase DAG Execution Plan]
    Decision -->|Autonomous Workflow| MetaDAG[Plan ➔ Goal ➔ Execute ➔ Verify DAG]
    Decision -->|No Match / Gap Detected| Gap[Notify User & Offer Auto-Scaffold / Install]
    
    Interactive --> AutoAct
    Pipeline --> AutoAct
    MetaDAG --> AutoAct
    Gap --> Scaffold[Scaffold New Compliant Skill]
    Scaffold --> AutoAct
```

---

## 📦 Directory Structure

```text
antigravity-skill-router/
├── SKILL.md                         # Core agent instructions & routing policy
├── README.md                        # Documentation & guides
├── LICENSE                          # MIT License
├── data/
│   └── skills-index.json            # 2,250+ skill inverted-index cache (sub-50ms lookup)
├── references/
│   ├── skill-catalog.md             # Curated catalog across 25+ domains
│   └── pipeline-orchestration.md    # Multi-skill 5-stage DAG decomposition guide
└── scripts/
    ├── skill-hub.ps1 / skill_hub.py # Master unified CLI entrypoint
    ├── query-index.py               # Ultra-fast BM25-style inverted-index search engine
    ├── route_pipeline.py            # Automated multi-skill DAG pipeline planner
    ├── scaffold-skill.ps1 / .py     # Interactive & automated skill scaffolder
    ├── lint-skills.ps1 / .py        # Quality & spec auditor (100/100 score)
    ├── build-index.py               # Rebuilds the 2,250+ skill index cache
    ├── route-skill.ps1              # PowerShell fast skill query wrapper
    ├── route-pipeline.ps1           # PowerShell pipeline wrapper
    └── test-skill.ps1               # 34-point automated test & benchmark suite
```

---

## 🚀 Installation

### 1. Global Installation (Recommended for Antigravity IDE)

To make `skill-router` available across all your Antigravity conversations and workspaces:

```bash
# Windows PowerShell
git clone https://github.com/ATP0925/antigravity-skill-router.git "$HOME\.gemini\config\skills\skill-router"

# Linux / macOS
git clone https://github.com/ATP0925/antigravity-skill-router.git ~/.gemini/config/skills/skill-router
```

### 2. Workspace-Specific Installation

To install only for a specific project repository:

```bash
git clone https://github.com/ATP0925/antigravity-skill-router.git .agents/skills/skill-router
```

Once installed, restart your IDE session or start a new conversation. Antigravity will automatically detect `skill-router` in its available skills.

---

## 🛠️ Master CLI Usage (`skill-hub`)

A unified cross-platform CLI tool (`skill-hub.ps1` for Windows / `skill_hub.py` for Python/Linux/macOS) is included for manual operations, benchmarks, and maintenance:

### 1. System Status Dashboard
Check health, cache age, scope distribution, and live latency ping:
```bash
# Universal Python
python scripts/skill_hub.py status

# Windows PowerShell
powershell -ExecutionPolicy Bypass -File scripts/skill-hub.ps1 status
```

### 2. Intent Route Search (< 50ms)
Find the best matching skill for any intent or error message:
```bash
# PowerShell
powershell -ExecutionPolicy Bypass -File scripts/skill-hub.ps1 route "Docker container restart loop fix karo"

# Python / Universal
python scripts/skill_hub.py route "PostgreSQL query slow chal rahi hai index optimization"
```

### 3. Deep Explain Diagnostic Mode
Inspect exact match signals, token weights, and decision reasoning:
```bash
python scripts/skill_hub.py explain "Docker container crash"
```

### 4. Filter Skills by Domain or Scope
```bash
python scripts/skill_hub.py list frontend
python scripts/skill_hub.py list security
python scripts/skill_hub.py list global
```

### 5. Multi-Skill DAG Pipeline Planning
Decompose complex compound tasks into a sequenced multi-skill pipeline:
```bash
# Tech stack pipeline
python scripts/skill_hub.py pipeline "Next.js 15 app with Supabase Auth and Jest E2E tests"

# Autonomous meta-workflow loop
python scripts/skill_hub.py pipeline "pehle plan karo fir goal fix karo fir execute and verify karo"
```

### 6. Automated Skill Scaffolding
Create a brand new, spec-compliant skill with template files, scripts, and references:
```bash
python scripts/skill_hub.py scaffold -n "cloud-deployer" -d "Automates AWS and GCP container deployments"
```

### 7. Spec & Quality Linter (Audit)
Lint any skill or the entire skills folder to ensure 100% compliance with Antigravity standards:
```bash
python scripts/skill_hub.py lint
```

### 8. Automated Verification Suite (34/34 Tests)
Run the 34-point benchmark and test suite:
```bash
# PowerShell
powershell -ExecutionPolicy Bypass -File scripts/test-skill.ps1
```

### 9. Rebuild Inverted Index Cache
Re-index your workspace and global plugins after adding new skills:
```bash
python scripts/build-index.py
```

---

## 📊 Benchmarks

| Metric | Result | Target SLA | Status |
| :--- | :--- | :--- | :--- |
| **Algorithm Search Latency** | **35.20 ms** | < 150 ms | 🟢 **4x Faster than SLA** |
| **Skills Indexed** | **2,249 Skills** | > 1,000 | 🟢 **Production Scale** |
| **Index Token Size** | **10,735 Inverted Tokens** | > 5,000 | 🟢 **Comprehensive** |
| **Linter Score** | **100 / 100** | >= 90 | 🟢 **Flawless Quality** |
| **Test Suite Pass Rate** | **34 / 34 (100%)** | 100% | 🟢 **Fully Verified** |

---

## 🎯 Usage Examples

### Example 1: DevOps & Containers
- **User Input:** *"Container bar bar restart ho raha hai, logs check karke solve karo."*
- **Skill Router Output:**
  - Matched: `docker-expert` (Confidence: 45) + `container-security-hardening`
  - Action: Silently activates `docker-expert`, analyzes crash logs, diagnoses OOM/entrypoint misconfiguration, and applies fix.

### Example 2: Performance Tuning
- **User Input:** *"Hamare React components bohot re-render ho rahe hain aur page slow lag raha hai."*
- **Skill Router Output:**
  - Matched: `react-component-performance` (Confidence: 50)
  - Action: Profiling re-renders with React DevTools hooks, applies `memo` and memoized selector patterns.

### Example 3: Fullstack Application Pipeline
- **User Input:** *"Ek fullstack e-commerce store banao Next.js, Stripe payments, aur Supabase database ke saath."*
- **Skill Router Output:**
  - 5-Phase DAG Pipeline:
    1. Phase 1 (Architecture & UI): `frontend-design` + `nextjs-app-router-patterns`
    2. Phase 2 (Backend & DB): `nextjs-supabase-auth` + `database-design`
    3. Phase 3 (Payments): `stripe-integration`
    4. Phase 4 (QA & Testing): `test-driven-development` + `e2e-testing-patterns`
    5. Phase 5 (Production & SEO): `seo-audit` + `vercel-deployment`

---

## 🤝 Contributing

Contributions, feedback, and new skill patterns are always welcome!
1. Fork this repository.
2. Create a feature branch: `git checkout -b feature/new-pattern`.
3. Verify your changes pass the linter: `python scripts/skill_hub.py lint`.
4. Commit your changes: `git commit -m "feat: add new domain capability"`.
5. Push to the branch and open a Pull Request.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE) &copy; 2026 **Pratik Maruti Atpadkar (ATP0925)**.
