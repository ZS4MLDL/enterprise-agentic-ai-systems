# Module 01 — Enterprise AI Systems and Design Principles

## What this module covers
- Why agentic systems are different from traditional applications
- Enterprise architecture principles applied to AI
- Introduction to the platform you will build over 15 modules
- Repository structure walkthrough

## What to do in this module

### Step 1 — Read the architecture decision records
```
docs/adr/0001-dual-mode-runtime.md
docs/adr/0002-postgres-vs-sqlite.md
docs/adr/0003-redis-for-queues.md
docs/adr/0004-langgraph-for-workflows.md
docs/adr/0005-openrouter-for-llm-access.md
```
For each ADR: understand the **Context → Decision → Tradeoffs** structure.
This is how real engineering decisions get documented.

### Step 2 — Walk the repo skeleton
Open the project in your editor and explore:
```
app/          ← one folder per platform capability
tests/        ← unit and integration tests (empty now, fills each module)
docs/adr/     ← architecture decisions
docker/       ← Dockerfile (used from Module 03)
docker-compose.yml  ← student + enterprise profiles (used from Module 04)
requirements.txt    ← pinned dependencies
```

### Step 3 — Read the Day-1 specification
Review the README — this is what the platform looks like when complete.
Every module adds one piece. Keep this picture in mind throughout the course.

## Nothing to run yet
Module 01 is architecture and design — no code to execute.
The first runnable module is **Module 02**.

## Key files introduced this module
| File | Purpose |
|---|---|
| `README.md` | Student setup instructions |
| `docs/adr/` | Architecture Decision Records |
| `requirements.txt` | Pinned dependencies |
| `.env.example` | Environment variable template |
| `docker-compose.yml` | Student + enterprise runtime profiles |

## Diagram (see PowerPoint slides)
- Enterprise AI Platform — end-to-end architecture overview
- Dual-mode runtime (student vs enterprise) side by side
- 15-module build progression timeline

## Discussion questions
1. Why run one codebase in two modes instead of two separate projects?
2. What would break first if you skipped the MODE switch and hardcoded SQLite everywhere?
3. Pick one ADR — what would you have decided differently and why?
