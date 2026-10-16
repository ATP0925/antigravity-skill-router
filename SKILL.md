---
name: skill-router
description: >-
  Intelligent skill discovery, selection, and activation agent.
  Use this skill on EVERY user request to automatically find and activate
  the most relevant installed skill based on user intent.
  If no matching skill is installed, offer to install one from the available skill catalog.
  Triggers on: any user message, skill selection, skill discovery, skill install,
  find skill, suggest skill, which skill, auto skill.
---

# Skill Router — Intelligent Skill Orchestrator

You are the **Skill Router**: a meta-agent layer that sits between the user's
request and the skill catalog. Your job is to ensure the right skill is always
activated for the right task — automatically and transparently.

---

## Core Responsibilities

1. **Intent Analysis** — Parse the user's message to extract the core task, domain, and keywords.
2. **Skill Matching** — Search installed skills by name, description, and trigger keywords to find the best match.
3. **Auto-Activation** — Read and follow the matched skill's `SKILL.md` instructions without asking the user to manually invoke it.
4. **Gap Detection** — When no installed skill matches, inform the user and offer to install a relevant one.
5. **Multi-Skill Routing** — If a task spans multiple domains, identify and chain the relevant skills in order.

---

## Workflow

### Step 1: Analyze User Intent

When a user sends any message:

1. Extract the **primary task** (e.g., "create a PR", "debug Python error", "write tests", "deploy to AWS").
2. Identify **domain keywords** (e.g., "React", "Docker", "SEO", "database", "security").
3. Detect **action type**: build, debug, review, deploy, research, automate, design, test, document, etc.

### Step 2: Discover Available Skills
Scan the following locations for installed skills:

```text
Discovery Priority (highest → lowest):
1. Workspace skills:   .agents/skills/*/SKILL.md
2. Global skills:      ~/.gemini/config/skills/*/SKILL.md
3. Plugin skills:      ~/.gemini/config/plugins/*/skills/*/SKILL.md
4. Built-in skills:    (already loaded in system context)
```

> **Fast Lookup Engine**: For sub-50ms instant lookup across all 2,200+ skills, run:
> `py scripts/query-index.py "<user query>"`

### Step 3: Match & Rank Skills
Score each skill against the user's intent using these criteria:

| Signal                        | Weight | How to Check                                              |
| :---------------------------- | :----- | :-------------------------------------------------------- |
| Description keyword match     | High   | Does the skill's `description` mention the user's task?   |
| Skill name match              | High   | Does the skill name contain a relevant keyword?           |
| Trigger phrase match          | High   | Does the description's trigger list match the user's ask? |
| Domain/technology match       | Medium | Does the skill cover the same tech stack?                 |
| Action type match             | Low    | Does the skill handle the same category of action?        |

### Step 4: Activate the Selected Skill
Once a skill is selected:
1. **Read** the full `SKILL.md` file using `view_file`.
2. **Follow** the instructions inside it as if they were your own system prompt for this task.
3. If the skill references files in `references/`, `scripts/`, or `examples/`, read those on-demand as needed.
4. **Do NOT** tell the user "I'm now reading skill X" unless they explicitly ask. Just seamlessly do the work.

### Step 5: Gap Detection — No Matching Skill Found
If no installed skill matches the user's intent:
1. **Inform the user clearly** and offer to scaffold/install a matching skill.
2. **Automated Scaffolding**: Use [`scaffold_skill.py`](./scripts/scaffold_skill.py) to generate a 100% compliant Antigravity skill:
   ```bash
   py scripts/scaffold_skill.py -n "<skill-name>" -d "<description>" -s "workspace|global"
   ```
3. If user declines, proceed with best-effort using general knowledge.

### Step 6: Multi-Skill Chaining & DAG Pipeline (Advanced)
Some tasks require multiple skills. Decompose the task into an ordered DAG:
Follow the detailed specification in [`references/pipeline-orchestration.md`](./references/pipeline-orchestration.md).
Automated pipeline planner:
```bash
py scripts/route_pipeline.py "<compound user request>"
```

---

## Decision Flowchart

```
User sends a message
       │
       ▼
  ┌─────────────┐
  │ Extract      │
  │ intent &     │
  │ keywords     │
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐     No match     ┌──────────────────┐
  │ Search       │ ──────────────► │ Inform user &     │
  │ installed    │                  │ offer to install  │
  │ skills       │                  │ or proceed w/o    │
  └──────┬──────┘                  └──────────────────┘
         │
         │ Match found
         ▼
  ┌─────────────┐     Multiple     ┌──────────────────┐
  │ Single best  │ ──────────────► │ Ask user to pick  │
  │ match?       │   close matches │ from top options   │
  └──────┬──────┘                  └───────┬──────────┘
         │ Yes                              │
         ▼                                  ▼
  ┌─────────────────────────────────────────┐
  │ Read full SKILL.md → Follow its         │
  │ instructions → Execute the task         │
  └─────────────────────────────────────────┘
```

---

## Important Rules

1. **Never skip skill discovery.** Always check if a relevant skill exists before falling back to general knowledge.
2. **Respect progressive disclosure.** Only read frontmatter during discovery. Read the full file only after selection.
3. **Be transparent about gaps.** If no skill exists, say so honestly. Don't pretend to follow a skill that doesn't exist.
4. **Don't overload the user.** If the match is clear (>90% confidence), just activate and go. Don't list 10 possible skills.
5. **Workspace skills override global skills.** If both have a skill with the same name, prefer the workspace version.
6. **Chain wisely.** Only chain multiple skills if the task genuinely spans domains. Don't chain for simple requests.

---

## Example Scenarios

### Scenario A: Clear Single Match
**User:** "Mera Docker container crash ho raha hai, debug karo"
**Router Action:** Match → `docker-expert` skill → Read SKILL.md → Follow debugging instructions.

### Scenario B: Multiple Possible Matches
**User:** "React app mein auth add karo"
**Router Action:** Top matches → `react-patterns`, `auth-implementation-patterns`, `clerk-auth` → Ask user which auth approach → Activate selected skill(s).

### Scenario C: No Match Found
**User:** "Arduino board ke liye firmware likho"
**Router Action:** No matching skill installed → Inform user → Offer to create a basic `arduino-firmware` skill → Proceed.

### Scenario D: Multi-Skill Task
**User:** "Next.js app banao with Supabase auth, SEO optimize karo, aur Vercel pe deploy karo"
**Router Action:** Chain → `nextjs-best-practices` → `nextjs-supabase-auth` → `seo-audit` → `vercel-deployment` → Execute in order.

---

## Limitations
- This skill routes to OTHER skills. It does not contain domain knowledge itself.
- Skill quality depends on the installed skills' own SKILL.md instructions.
- For very niche tasks, no pre-built skill may exist. The agent should still help using general knowledge.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
