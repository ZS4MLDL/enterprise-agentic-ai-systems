"""
Module 02 — unit tests for llm_client and cost_tracker.
All tests use mocked responses — no real API calls are made.
"""
from unittest.mock import MagicMock, patch

import pytest

from app.common.llm_client import chat
from app.common.cost_tracker import estimate_cost


# ── llm_client tests ──────────────────────────────────────────────────────────

@patch("app.common.llm_client._make_client")
@patch("app.common.llm_client.record_call")
def test_chat_returns_response(mock_record, mock_make_client):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Hello!"))]
    mock_response.usage = MagicMock(prompt_tokens=10, completion_tokens=5, total_tokens=15)

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_make_client.return_value = mock_client

    result = chat([{"role": "user", "content": "Hi"}])

    assert result.choices[0].message.content == "Hello!"
    mock_record.assert_called_once()


@patch("app.common.llm_client._make_client")
def test_chat_raises_value_error_on_invalid_key(mock_make_client):
    from openai import APIStatusError

    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = APIStatusError(
        "Unauthorized",
        response=MagicMock(status_code=401),
        body={"error": {"message": "Invalid API key"}},
    )
    mock_make_client.return_value = mock_client

    with pytest.raises(ValueError, match="Invalid API key"):
        chat([{"role": "user", "content": "Hi"}])


@patch("app.common.llm_client._make_client")
@patch("app.common.llm_client.record_call")
@patch("app.common.llm_client.time.sleep")
def test_chat_retries_on_429(mock_sleep, mock_record, mock_make_client):
    from openai import APIStatusError

    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="OK"))]
    mock_response.usage = MagicMock(prompt_tokens=5, completion_tokens=3, total_tokens=8)

    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = [
        APIStatusError("Rate limited", response=MagicMock(status_code=429), body={}),
        mock_response,
    ]
    mock_make_client.return_value = mock_client

    result = chat([{"role": "user", "content": "Hi"}])
    assert result.choices[0].message.content == "OK"
    assert mock_sleep.call_count == 1


@patch("app.common.llm_client._make_client")
@patch("app.common.llm_client.time.sleep")
def test_chat_raises_after_all_retries(mock_sleep, mock_make_client):
    from openai import APIStatusError

    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = APIStatusError(
        "Server error", response=MagicMock(status_code=500), body={}
    )
    mock_make_client.return_value = mock_client

    with pytest.raises(RuntimeError, match="failed after"):
        chat([{"role": "user", "content": "Hi"}])


# ── cost_tracker tests ────────────────────────────────────────────────────────

def test_estimate_cost_known_model():
    cost = estimate_cost("openai/gpt-4o-mini", prompt_tokens=1000, completion_tokens=500)
    assert cost > 0
    assert cost < 0.01


def test_estimate_cost_unknown_model_uses_fallback():
    cost = estimate_cost("unknown/model-xyz", prompt_tokens=1000, completion_tokens=500)
    assert cost > 0


def test_estimate_cost_zero_tokens():
    cost = estimate_cost("openai/gpt-4o", prompt_tokens=0, completion_tokens=0)
    assert cost == 0.0
