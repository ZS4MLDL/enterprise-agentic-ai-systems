# ADR 0005 — OpenRouter for LLM Access

## Context

The course requires access to multiple LLM providers (OpenAI, Anthropic, open-source models)
without requiring students to hold accounts at each provider.  A unified API surface simplifies
key management and cost tracking.

## Decision

**OpenRouter** is the single LLM gateway for all modules.  It exposes an OpenAI-compatible
API so `openai` SDK calls work unchanged.  Students need one API key.

## Consequences

**Benefits**
- One API key, one billing dashboard for students.
- Switching models (e.g., GPT-4o → Claude → Llama) is a one-line config change.
- Built-in per-model cost data available in response headers — feeds the cost-tracking layer.
- Open-source models (for Module 12 LoRA comparison) are accessible without self-hosting.

**Tradeoffs**
- Adds one hop vs calling providers directly — slight latency increase.
- OpenRouter outage affects all model access simultaneously (single point of failure for the
  LLM layer — mitigated by fallback model chain in Module 12).
- Some provider-specific features (e.g., Anthropic extended thinking, OpenAI Assistants API)
  may not be available through OpenRouter.
