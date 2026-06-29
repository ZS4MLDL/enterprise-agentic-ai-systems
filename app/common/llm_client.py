"""
Provider-agnostic LLM wrapper (Module 02).
All modules call the LLM through this client — never directly via the SDK.
"""
import time
import logging
from typing import Generator

from openai import OpenAI, APIStatusError, APIConnectionError

from app.config.settings import get_settings
from app.config.model_registry import ModelTier, get_model
from app.common.cost_tracker import record_call

logger = logging.getLogger(__name__)

_MAX_RETRIES = 3
_BACKOFF_BASE = 2


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
    Send a chat completion request via OpenRouter.

    Returns the full response object (stream=False) or a chunk generator (stream=True).
    Raises ValueError on auth failure, RuntimeError after retries exhausted.
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
                record_call(model_id, response)
            return response

        except APIStatusError as e:
            if e.status_code == 401:
                raise ValueError(
                    f"Invalid API key — check OPENROUTER_API_KEY in your .env file. Detail: {e.message}"
                ) from e
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
    logger.warning(
        "Transient LLM error (attempt %d/%d), retrying in %ds: %s",
        attempt, _MAX_RETRIES, wait, exc,
    )
    time.sleep(wait)
