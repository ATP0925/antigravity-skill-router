# Multi-Skill Pipeline & DAG Orchestration Guide

When a user request involves multiple steps across distinct technical domains (e.g. Frontend + Database + Auth + CI/CD), activating a single skill leads to incomplete or suboptimal execution.

The **Skill Router Pipeline Engine** decomposes complex requests into an ordered **Directed Acyclic Graph (DAG)** of skills.

---

## Standard Execution Stages

Skill execution follows a 5-phase dependency order:

```text
[Phase 1: Architecture & Scaffold]
             │
             ▼
[Phase 2: Data Model & Backend / Auth]
             │
             ▼
[Phase 3: Frontend & UI Design]
             │
             ▼
[Phase 4: Quality, Testing & A11y]
             │
             ▼
[Phase 5: CI/CD & Deployment]
```

### Stage Mapping Matrix

| Stage | Focus Area | Candidate Skills |
| :--- | :--- | :--- |
| **Stage 1: Architecture** | Framework setup, folder structure, API design | `nextjs-best-practices`, `api-design-principles`, `fastapi-templates` |
| **Stage 2: Core Data / Auth** | Database schemas, ORM, Auth providers | `postgres-best-practices`, `nextjs-supabase-auth`, `clerk-auth`, `sql-pro` |
| **Stage 3: UI / Components** | Component library, styling, accessibility | `tailwind-patterns`, `shadcn`, `frontend-design`, `ui-a11y` |
| **Stage 4: Testing** | Unit tests, E2E tests, mocking, coverage | `tdd-workflow`, `jest-skill`, `playwright-skill`, `pytest-skill` |
| **Stage 5: DevOps / Ship** | Containers, CI/CD, deployment platforms | `docker-expert`, `github-actions-templates`, `vercel-deployment` |

---

## Pipeline Execution Rules

1. **Context Economy**: Load only the current phase's `SKILL.md`. Do not load all skills simultaneously into context.
2. **Phase Gates**: Verify each stage passes before proceeding to the next.
   - Stage 1 Gate: Project builds and structure conforms to conventions.
   - Stage 2 Gate: Schema compiles and auth client initializes.
   - Stage 3 Gate: Components render without TypeScript or styling warnings.
   - Stage 4 Gate: Test suite executes with code 0.
   - Stage 5 Gate: Workflow configuration validated against linter.
3. **Transparent Reporting**: Present the generated pipeline to the user before starting multi-phase tasks.

---

## Example Pipeline Run

**User Prompt:**
> "Build a Next.js 15 app with Supabase authentication, styled with Tailwind CSS, tested with Jest, and automated with GitHub Actions."

**Generated Execution Plan:**
```markdown
### 🚀 Multi-Skill Execution Pipeline

1. **Phase 1: Architecture Setup** → `nextjs-best-practices`
   - Setup App Router conventions, directory structure, and TypeScript strict mode.

2. **Phase 2: Authentication & Database** → `nextjs-supabase-auth`
   - Configure Supabase client, SSR middleware, and session management.

3. **Phase 3: Design & Styling** → `tailwind-patterns`
   - Configure Tailwind v4 tokens, responsive layouts, and dark mode.

4. **Phase 4: Testing Suite** → `jest-skill`
   - Setup Jest runner, mock handlers, and unit test critical auth routes.

5. **Phase 5: CI/CD Pipeline** → `github-actions-templates`
   - Create .github/workflows/ci.yml with test & lint automation.
```
