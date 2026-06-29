# Module 01 — Enterprise AI Systems and Design Principles

## What this module covers
- Why agentic systems are different from traditional applications
- Enterprise architecture principles applied to AI
- Introduction to the platform you will build over 15 modules
- Repository structure walkthrough

## What to do in this module

### Step 1 — Clone and explore the repo
```bash
git clone https://github.com/ZS4MLDL/enterprise-agentic-ai-systems.git
cd enterprise-agentic-ai-systems
git checkout module/01
```
Open the folder in your editor and walk through the structure below.

### Step 2 — Understand the repository structure
```
enterprise-ai-app/
│
├── app/                        ← all application code lives here
│   ├── agents/                 ← stateful agents (Module 03)
│   ├── api/                    ← FastAPI endpoints (Module 03 onward)
│   │   └── v1/                 ← versioned API routes
│   ├── config/                 ← settings, model registry, MODE switch
│   ├── common/                 ← shared utilities — llm_client, cost tracker
│   ├── schemas/                ← shared Pydantic data contracts (Module 05)
│   ├── prompts/                ← versioned prompt templates (Module 05)
│   ├── tools/                  ← tool implementations (Module 06)
│   ├── mcp/                    ← MCP gateway (Module 06)
│   ├── workflows/              ← LangGraph state machines (Module 07)
│   ├── routing/                ← intent classification and routing (Module 08)
│   ├── multi_agent/            ← manager-worker patterns (Module 09)
│   ├── memory/                 ← short and long-term memory (Module 10)
│   ├── rag/                    ← retrieval-augmented generation (Module 11)
│   ├── model_adaptation/       ← adapters and fallback chains (Module 12)
│   ├── eval/                   ← evaluation harness (Module 13)
│   ├── observability/          ← tracing and cost dashboard (Module 13)
│   ├── governance/             ← access control, PII, audit (Module 14)
│   ├── workers/                ← background task workers (Module 09)
│   ├── storage/                ← document storage abstraction (Module 11)
│   └── ui/                     ← Streamlit chat UI (Module 03 onward)
│
├── tests/
│   ├── unit/                   ← per-component tests (Module 02 onward)
│   └── integration/            ← cross-component tests (Module 04 onward)
│
├── docs/
│   └── adr/                    ← Architecture Decision Records
│       ├── 0001-dual-mode-runtime.md
│       ├── 0002-postgres-vs-sqlite.md
│       ├── 0003-redis-for-queues.md
│       ├── 0004-langgraph-for-workflows.md
│       └── 0005-openrouter-for-llm-access.md
│
├── docker/
│   └── Dockerfile              ← container definition (Module 03)
│
├── deployments/                ← Terraform / cloud configs (Module 15)
├── scripts/                    ← utility scripts (init_db, compare_models...)
├── notebooks/                  ← experimentation notebooks
│
├── docker-compose.yml          ← student + enterprise profiles (Module 04)
├── requirements.txt            ← pinned core dependencies
├── requirements-vector.txt     ← Module 10/11 (needs C++ Build Tools)
├── requirements-enterprise-db.txt  ← Module 04 enterprise mode
├── requirements-observability.txt  ← Module 13
├── .env.example                ← copy to .env and add your API key
├── pytest.ini                  ← test configuration
└── MODULE_NOTES.md             ← this file — what to do each module
```

### Step 3 — Read the Architecture Decision Records
```
docs/adr/0001-dual-mode-runtime.md
docs/adr/0002-postgres-vs-sqlite.md
docs/adr/0003-redis-for-queues.md
docs/adr/0004-langgraph-for-workflows.md
docs/adr/0005-openrouter-for-llm-access.md
```
For each ADR read the Context, Decision, and Tradeoffs sections.
This is how real engineering decisions get documented on production teams.

### Step 4 — Read the Day-1 specification
Open README.md. This is what the platform looks like when all 15 modules are complete.
Every module adds one piece. Keep this picture in mind throughout the course.

## Nothing to run yet
Module 01 is architecture and design — no code to execute.
The first runnable module is Module 02.

## Key files introduced this module
| File | Purpose |
|---|---|
| `README.md` | Student setup instructions and module branch table |
| `docs/adr/` | Five Architecture Decision Records |
| `requirements.txt` | Pinned core dependencies |
| `.env.example` | Environment variable template |
| `docker-compose.yml` | Student and enterprise runtime profiles |
| `MODULE_NOTES.md` | Per-module instructions (this file) |

## Diagram (see PowerPoint slides)
- Traditional application vs agentic AI system — side by side flowchart
- Repository structure annotated with which module fills each folder
- Dual-mode runtime (student vs enterprise) side by side
- 15-module build progression timeline

## Discussion questions
1. Why run one codebase in two modes instead of two separate projects?
2. Look at the repo structure — what would break first if you removed the config/ folder?
3. Pick one ADR — what would you have decided differently and why?
