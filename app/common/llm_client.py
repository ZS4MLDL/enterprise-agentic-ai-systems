"""
Provider-agnostic LLM wrapper (Module 02).
All modules call the LLM through this client — never directly via the SDK.

Handles:
- OpenRouter (OpenAI-compatible endpoint)
- Basic retry with exponential backoff on transient errors (429, 5xx)
- Token/cost logging per call
"""
import time
import logging
from typing import Generator

from openai import OpenAI, APIStatusError, APIConnectionError

from app.config.settings import get_settings
from app.config.model_registry import ModelTier, get_model

logger = logging.getLogger(__name__)

_MAX_RETRIES = 3
_BACKOFF_BASE = 2  # seconds


def _make_client() -> OpenAI:
    s = get_settings()
    return OpenAI(
        api_key=s.OPENROUTER_API_KEY,
        base_url=s.OPENROUTER_BASE_URL,
    )


def chat(
    messages: list[dict],
    *,
    model: str | None = None,
    tier: ModelTier = ModelTier.DEFAULT,
    stream: bool = False,
    temperature: float = 0.7,
    max_tokens: int = 2048,
) -> dict | Generator:
    """
    Send a chat request and return the response dict (or a stream generator).

    Args:
        messages: OpenAI-format message list.
        model: Explicit model ID — overrides tier if provided.
        tier: Logical model tier (cheap / default / powerful).
        stream: Return a streaming generator instead of a full response.
        temperature: Sampling temperature.
        max_tokens: Max completion tokens.

    Returns:
        Full response dict when stream=False; generator of chunks when stream=True.

    Raises:
        ValueError: On invalid API key (401).
        RuntimeError: After all retries exhausted.
    """
    model_id = model or get_model(tier)
    client = _make_client()

    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            response = client.chat.completions.create(
                model=model_id,
                messages=messages,
                stream=stream,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            if not stream:
                _log_usage(model_id, response)
            return response

        except APIStatusError as e:
            if e.status_code == 401:
                raise ValueError(f"Invalid API key or unauthorized: {e.message}") from e
            if e.status_code == 429 or e.status_code >= 500:
                _handle_retryable(attempt, e)
            else:
                raise
        except APIConnectionError as e:
            _handle_retryable(attempt, e)

    raise RuntimeError(f"LLM request failed after {_MAX_RETRIES} attempts.")


def _handle_retryable(attempt: int, exc: Exception) -> None:
    if attempt == _MAX_RETRIES:
        raise RuntimeError(f"LLM request failed after {_MAX_RETRIES} attempts.") from exc
    wait = _BACKOFF_BASE ** attempt
    logger.warning("LLM transient error (attempt %d/%d), retrying in %ds: %s", attempt, _MAX_RETRIES, wait, exc)
    time.sleep(wait)


def _log_usage(model_id: str, response) -> None:
    usage = getattr(response, "usage", None)
    if usage:
        logger.info(
            "LLM call | model=%s prompt_tokens=%d completion_tokens=%d total=%d",
            model_id,
            usage.prompt_tokens,
            usage.completion_tokens,
            usage.total_tokens,
        )
