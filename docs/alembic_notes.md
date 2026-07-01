# Alembic Quick Reference

Alembic manages database schema changes through versioned migration files.
Every schema change gets a migration file — never alter tables manually.

## Setup (first time only)
```bash
# Create the data directory if it doesn't exist
mkdir data

# Set PYTHONPATH so alembic can find the app module
$env:PYTHONPATH="."       # Windows PowerShell
export PYTHONPATH="."     # macOS / Linux
```

---

## Daily commands

### Apply all pending migrations (migrate up)
```bash
python -m alembic upgrade head
```
Run this after cloning a new module branch to bring your DB up to date.

### Check current migration version
```bash
python -m alembic current
```

### See migration history
```bash
python -m alembic history --verbose
```

---

## Creating a new migration

### Auto-generate from model changes (recommended)
```bash
python -m alembic revision --autogenerate -m "describe_what_changed"
```
Always review the generated file in `alembic/versions/` before applying it.

### Create an empty migration (manual)
```bash
python -m alembic revision -m "describe_what_changed"
```

---

## Rolling back

### Roll back one migration
```bash
python -m alembic downgrade -1
```

### Roll back to a specific version
```bash
python -m alembic downgrade <revision_id>
```

### Roll back everything
```bash
python -m alembic downgrade base
```

---

## Student mode vs Enterprise mode

Alembic reads the database URL from your `.env` file automatically.

```
MODE=student    → migrates SQLite at SQLITE_PATH (./data/app.db)
MODE=enterprise → migrates PostgreSQL at DATABASE_URL
```

No code change needed — just switch MODE in `.env` and run the same commands.

---

## Migration file location
```
alembic/
├── env.py              ← reads settings, connects to DB
├── script.py.mako      ← template for new migration files
└── versions/
    └── xxxx_description.py   ← one file per migration
```

---

## Common mistakes

| Mistake | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'app'` | Set `$env:PYTHONPATH="."` first |
| `unable to open database file` | Run `mkdir data` first |
| Auto-generate shows no changes | Make sure models are imported in `alembic/env.py` |
| Migration applied but table missing | Check the generated file — auto-generate sometimes misses things |
