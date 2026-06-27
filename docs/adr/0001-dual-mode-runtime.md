# ADR 0001 — Dual-Mode Runtime (MODE=student / MODE=enterprise)

## Context

Students need to run the full platform on a laptop (8 GB RAM, no cloud account) while the
course simultaneously demonstrates production-grade infrastructure.  Two separate codebases
would diverge instantly and double maintenance burden.

## Decision

A single environment variable `MODE` selects the backend at startup.  All module code branches
on `settings.is_enterprise`.  No feature flags, no runtime toggles — just one env var.

```
MODE=student    → SQLite · Chroma · asyncio BackgroundTasks · .env secrets · console logging
MODE=enterprise → PostgreSQL/pgvector · Redis · Dramatiq workers · Vault/SOPS · Langfuse/OTel
```

## Consequences

**Benefits**
- One codebase to teach, maintain, and test.
- Students see the exact production code path — not a toy version.
- Integration tests can run both modes in CI.

**Tradeoffs**
- Every module must be written with the branch in mind (`if settings.is_enterprise`).
- Adding a third runtime (e.g., GCP-native) requires extending the enum and each branch —
  acceptable given the course's two-environment scope.
