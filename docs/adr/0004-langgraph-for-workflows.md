# ADR 0004 — LangGraph for Workflow Orchestration

## Context

The platform needs a workflow engine that supports: conditional branching, parallel node
execution, human-in-the-loop checkpoints, and crash-resumable state.  Options: LangGraph,
Prefect, Temporal, plain asyncio state machines, AWS Step Functions.

## Decision

**LangGraph** (LangChain ecosystem) is used for all workflow orchestration.

Reasons:
- Native LLM-aware primitives — nodes are just Python functions that receive/return state dicts.
- Built-in checkpointer abstraction (SQLite for student, Postgres for enterprise) — crash
  resumability is a first-class feature, not a bolt-on.
- Human-in-the-loop interrupts are supported without external tooling.
- Aligns with the course's LangChain/LangGraph skill track.

## Consequences

**Benefits**
- Checkpoint-based resume is available from Module 07 with no extra infrastructure.
- The same graph runs locally and in containers without code changes.
- Conditional branching is expressed as pure Python — no YAML DSL to learn.

**Tradeoffs**
- LangGraph is newer and evolving fast; API surface may change between course iterations.
- Not suitable for very high-throughput workflows (Temporal/Prefect scale better there).
- Tighter coupling to the LangChain ecosystem than a neutral orchestrator (e.g., Temporal).
