# Docker Quick Reference

## Prerequisites
- Docker Desktop installed and running
- `.env` file created from `.env.example` with `OPENROUTER_API_KEY` set

---

## Student mode (local, no cloud)

### Start everything
```bash
docker compose --profile student up
```
This starts:
- API server at http://localhost:8000
- Streamlit UI at http://localhost:8501

### Start in background
```bash
docker compose --profile student up -d
```

### Stop
```bash
docker compose --profile student down
```

### Rebuild after code changes
```bash
docker compose --profile student up --build
```

---

## Enterprise mode (Postgres + Redis)

### Start everything
```bash
docker compose --profile enterprise up
```
This starts:
- Postgres at localhost:5432
- Redis at localhost:6379
- API server at http://localhost:8000
- Streamlit UI at http://localhost:8501

### Run migrations after first start
```bash
# Wait for Postgres to be healthy, then:
docker compose --profile enterprise exec app-enterprise python -m alembic upgrade head
```

### Stop and remove volumes (full reset)
```bash
docker compose --profile enterprise down -v
```

---

## Common commands (both modes)

### View running containers
```bash
docker compose ps
```

### View logs
```bash
docker compose logs -f                        # all services
docker compose logs -f app-student            # one service
```

### Open a shell inside the container
```bash
docker compose --profile student exec app-student bash
```

### Check container health
```bash
docker ps --format "table {{.Names}}\t{{.Status}}"
```

---

## Building the image manually

```bash
# Build
docker build -f docker/Dockerfile -t enterprise-ai .

# Run standalone (student mode)
docker run -p 8000:8000 --env-file .env enterprise-ai
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `port already in use` | Stop the local uvicorn server before starting Docker |
| `connection refused` to Postgres | Wait for the `healthy` status — run `docker compose ps` |
| Code change not picked up | Run with `--build` flag |
| Container exits immediately | Run `docker compose logs` to see the error |
| `MODULE_NOTES says MODE=enterprise but I see SQLite` | Check `.env` — `MODE=enterprise` must be set |

---

## Student mode vs Enterprise mode — what runs where

| Component | Student mode | Enterprise mode |
|---|---|---|
| Database | SQLite file (`data/app.db`) | Postgres container |
| Vector store | Chroma (local disk) | pgvector (in Postgres) |
| Queue | asyncio BackgroundTasks | Redis container |
| Secrets | `.env` file | HashiCorp Vault (Module 14) |
| Tracing | Console logs | Langfuse (Module 13) |
