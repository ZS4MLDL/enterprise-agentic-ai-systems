# Module 04 — Agent Runtime + Docker Compose + Alembic Migrations

## What this module covers
- Building a reusable agent runtime that tracks session lifecycle in the database
- Managing database schema changes with Alembic migrations (up, down, rollback)
- Docker Compose profiles for running the full stack locally in student or enterprise mode
- API versioning so existing clients never break when the API evolves
- Graceful degradation — the app returns a degraded status instead of crashing when the DB is unreachable

## What to do in this module

### Step 1 — Setup
```bash
git clone https://github.com/ZS4MLDL/enterprise-agentic-ai-systems.git
cd enterprise-agentic-ai-systems
git checkout module/04
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# add OPENROUTER_API_KEY to .env

# if you get ModuleNotFoundError run this first:
$env:PYTHONPATH="."
```

### Step 2 — Run the migration
```bash
mkdir data
python -m alembic upgrade head
```
This creates two tables in `data/app.db`: `conversation_sessions` and `audit_log`.
Open the DB with any SQLite viewer to inspect what was created.

### Step 3 — Start the API and UI
```bash
uvicorn app.main:app --reload        # terminal 1
streamlit run app/ui/chat_app.py     # terminal 2
```

### Step 4 — Check the health endpoint
```bash
curl http://localhost:8000/api/v1/health
```
Expected response:
```json
{"status": "ok", "mode": "student", "db": "connected"}
```

### Step 5 — Test graceful degradation
Rename `data/app.db` temporarily, then call the health endpoint again.
The app returns `{"status": "degraded"}` instead of a 500 error.

### Step 6 — Run the tests
```bash
pytest tests/unit/ -v
```
28 tests, all green. Migration tests run up, down, and up again against a temp SQLite file.

### Step 7 — Alembic reference
See `docs/alembic_notes.md` for all migration commands you will need throughout the course.

### Step 8 — Docker reference
See `docs/docker_notes.md` for all Docker and Docker Compose commands for running the full stack in student or enterprise mode.

---

## All files in this module

| Status | File | What to explain to students |
|---|---|---|
| NEW | `app/db/base.py` | SQLAlchemy `DeclarativeBase` — all models inherit from this. One import that ties the ORM together. |
| NEW | `app/db/models.py` | Two tables: `ConversationSession` tracks active sessions, `AuditLog` is the append-only event log that grows each module. |
| NEW | `app/db/session.py` | Session factory — returns the correct engine based on MODE. `check_db_connection()` powers graceful degradation. |
| NEW | `app/agents/runtime.py` | Session lifecycle — creates sessions in the DB, increments turn counts. Wraps the agent with persistence. |
| NEW | `app/api/v1/health.py` | Health endpoint that reports DB status. Returns `degraded` not `500` when DB is unreachable. |
| NEW | `alembic/env.py` | Configured to read `DATABASE_URL` from settings — same migration file works for SQLite and Postgres. |
| NEW | `alembic/versions/xxxx_create_*.py` | First migration — creates `conversation_sessions` and `audit_log` tables. |
| NEW | `docs/alembic_notes.md` | Quick reference for all Alembic commands students will use throughout the course. |
| NEW | `docs/docker_notes.md` | Quick reference for Docker and Docker Compose commands — student profile vs enterprise profile, troubleshooting, log viewing. |
| NEW | `tests/unit/test_config_switch.py` | Confirms student and enterprise modes load different backends without any code change. |
| NEW | `tests/unit/test_migrations.py` | Runs migrate-up, rollback, re-migrate against a temp SQLite file. Proves the migration is reversible. |
| NEW | `tests/unit/test_health.py` | Tests health endpoint returns `ok` when DB is up and `degraded` when it is not. |
| UPDATED | `app/main.py` | Now registers the health router alongside the chat router. |
| EXISTS | `docker-compose.yml` | Student and enterprise profiles already defined — enterprise profile starts Postgres and Redis containers. |

---

## What changed from Module 03
- The platform now has a proper database schema managed by Alembic — not just a SQLite file for checkpoints
- Sessions are tracked in a table, not just in-memory
- The health endpoint tells you the real status of the system rather than always returning `ok`
- The app degrades gracefully instead of crashing when the database is unreachable

## Failure scenarios to test
| Scenario | How to trigger | Expected behaviour |
|---|---|---|
| DB unreachable at startup | Rename `data/app.db` before starting | `/api/v1/health` returns `degraded`, chat still attempts to work |
| Migration fails mid-deploy | Manually corrupt a migration file | `alembic upgrade head` fails cleanly, DB stays at previous version |
| Rollback needed | `python -m alembic downgrade -1` | Tables removed cleanly, re-migrate restores them |

## Cost to watch
No additional LLM cost in this module. The new code is all infrastructure — DB, migrations, health checks.

## Diagram (see PowerPoint slides)
- Alembic migration lifecycle — revision, upgrade, downgrade flow
- Docker Compose architecture — student profile vs enterprise profile side by side
- Database schema — `conversation_sessions` and `audit_log` table structure
- Graceful degradation flow — what happens at each layer when the DB is down

## Discussion questions
1. Why use Alembic instead of just running `CREATE TABLE` SQL manually?
2. The health endpoint returns HTTP 200 even when the DB is degraded. Why not return 503?
3. In enterprise mode, Alembic migrates Postgres using the same migration files as SQLite. What could go wrong with this assumption?
