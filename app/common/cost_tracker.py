"""
Per-call token and cost tracker (Module 02).

Logs every LLM call to the console (student mode) or a JSON file that the
observability dashboard reads later (Module 13).

Cost figures are approximations based on OpenRouter public pricing.
They are used for learning/budgeting — not billing.
"""
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from app.config.settings import get_settings

logger = logging.getLogger(__name__)

# Approximate cost per 1000 tokens in USD (input / output)
# Update these if OpenRouter pricing changes
_COST_PER_1K: dict[str, tuple[float, float]] = {
    "openai/gpt-4o-mini":           (0.00015, 0.00060),
    "openai/gpt-4o":                (0.00250, 0.01000),
    "anthropic/claude-sonnet-4-6":  (0.00300, 0.01500),
}
_DEFAULT_COST = (0.00100, 0.00300)  # fallback if model not in table


def estimate_cost(model_id: str, prompt_tokens: int, completion_tokens: int) -> float:
    input_rate, output_rate = _COST_PER_1K.get(model_id, _DEFAULT_COST)
    return (prompt_tokens / 1000 * input_rate) + (completion_tokens / 1000 * output_rate)


def record_call(model_id: str, response) -> None:
    usage = getattr(response, "usage", None)
    if not usage:
        return

    prompt_tokens = usage.prompt_tokens
    completion_tokens = usage.completion_tokens
    total_tokens = usage.total_tokens
    cost_usd = estimate_cost(model_id, prompt_tokens, completion_tokens)

    logger.info(
        "cost_tracker | model=%s prompt=%d completion=%d total=%d est_cost=$%.6f",
        model_id, prompt_tokens, completion_tokens, total_tokens, cost_usd,
    )

    s = get_settings()
    if s.is_enterprise:
        _append_to_log(model_id, prompt_tokens, completion_tokens, total_tokens, cost_usd)


def _append_to_log(
    model_id: str,
    prompt_tokens: int,
    completion_tokens: int,
    total_tokens: int,
    cost_usd: float,
) -> None:
    log_path = Path("data/cost_log.jsonl")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "model": model_id,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "cost_usd": cost_usd,
    }
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
