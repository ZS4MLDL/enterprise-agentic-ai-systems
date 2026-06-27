# ADR 0002 — PostgreSQL (enterprise) vs SQLite (student)

## Context

The platform needs a relational store for agent checkpoints, prompt versions, audit logs, and
session data.  Students cannot be required to run a Postgres server locally.

## Decision

- **Student mode:** SQLite via `aiosqlite` + SQLAlchemy async.  Zero-install, file-backed,
  works on Windows/macOS/Linux without Docker.
- **Enterprise mode:** PostgreSQL 16 with the `pgvector` extension, run via Docker Compose.
  Same SQLAlchemy models — only the `DATABASE_URL` changes.

Alembic manages migrations for both backends from a single migration history.

## Consequences

**Benefits**
- Students learn real SQL and ORM patterns, not an in-memory mock.
- The Postgres swap requires zero code changes — only `DATABASE_URL` in `.env`.
- pgvector co-locates relational data and vector embeddings, reducing infrastructure surface
  in enterprise mode.

**Tradeoffs**
- SQLite has no native vector support — Chroma fills that gap in student mode, requiring a
  two-backend abstraction in `app/memory/` and `app/rag/`.
- SQLite's write concurrency limits mean the student mode is unsuitable for load testing.
