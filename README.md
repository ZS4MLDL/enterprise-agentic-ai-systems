# Enterprise Research and Knowledge Assistant Platform

## Student Setup — Do This Once Per Module

Each module is a separate branch. The workflow is always the same 4 steps:

```bash
# 1. Clone (first time only) or switch to the module branch
git clone <repo-url>
cd enterprise-ai-app
git checkout module/02        # change number for each module

# 2. Create a virtual environment INSIDE the project folder
python -m venv .venv

# 3. Activate it
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Set up your .env
cp .env.example .env
# Open .env and add your OPENROUTER_API_KEY

# 6. Run the app
python scripts/init_db.py           # first time only
uvicorn app.main:app --reload       # API server
streamlit run app/ui/chat_app.py    # UI (separate terminal)
```

## Module Branches

| Branch | What's added |
|---|---|
| `module/01` | Repo skeleton, ADRs, architecture |
| `module/02` | LLM client, model registry, settings, unit tests |
| `module/03` | Stateful agent, FastAPI, Streamlit UI, Docker |
| `module/04` | Docker Compose, Alembic migrations, API versioning |
| `module/05` | Prompt library, structured outputs, regression tests |
| `module/06` | Tools, MCP gateway |
| `module/07` | LangGraph workflows, human-in-the-loop |
| `module/08` | Intent routing, model routing |
| `module/09` | Multi-agent, background workers |
| `module/10` | Memory (short-term + semantic) |
| `module/11` | RAG pipeline, document storage |
| `module/12` | Model adaptation, fallback chains |
| `module/13` | Evaluation, observability, circuit breakers |
| `module/14` | Governance, access control, PII, audit |
| `module/15` | Production deployment, CI/CD |

## Extra Requirements (install when you reach that module)

```bash
# Module 10/11 — vector store (Windows needs C++ Build Tools first)
pip install -r requirements-vector.txt

# Module 04 enterprise mode — Postgres drivers
pip install -r requirements-enterprise-db.txt

# Module 13 — observability
pip install -r requirements-observability.txt
```

## Running Modes

```bash
# Student mode (default) — SQLite, Chroma, local secrets
MODE=student uvicorn app.main:app --reload

# Enterprise mode — Postgres, Redis, Vault, Langfuse
docker compose --profile enterprise up
```
