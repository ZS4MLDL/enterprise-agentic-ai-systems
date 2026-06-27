# ADR 0003 — Redis for Background Queues (enterprise mode)

## Context

Long-running multi-agent tasks must not block the HTTP request cycle.  A task queue is needed
for enterprise mode.  Options considered: Celery+Redis, Dramatiq+Redis, RQ, SQS/Azure Service Bus.

## Decision

**Dramatiq + Redis** for enterprise mode; Python `asyncio.BackgroundTasks` (FastAPI built-in)
for student mode.

Reasons Dramatiq was chosen over Celery:
- Simpler API — a single `@dramatiq.actor` decorator, no `celery.task` + app factory boilerplate.
- Better fit for an AI-focused course; Celery's general-purpose feature surface (beat scheduler,
  canvas primitives, result backends) is noise here.
- First-class async support without the Celery 5 caveats.
- Dead-letter queue built in via the `Retries` middleware.

## Consequences

**Benefits**
- Students see the queue/worker pattern with minimal framework overhead.
- Dead-letter queue behaviour is teachable with a one-line middleware config.
- Redis is already in the enterprise stack (also used for response caching in Module 10).

**Tradeoffs**
- Dramatiq is less common in industry than Celery — students may need to translate patterns.
- Requires Redis in enterprise mode; student mode uses asyncio (no queue durability guarantee).
