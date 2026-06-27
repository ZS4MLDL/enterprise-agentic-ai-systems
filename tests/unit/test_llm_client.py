"""
Module 02 — unit test: LLM client returns expected schema for a mocked response.
"""
from unittest.mock import MagicMock, patch

import pytest

from app.common.llm_client import chat


@patch("app.common.llm_client._make_client")
def test_chat_returns_response(mock_make_client):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Hello!"))]
    mock_response.usage = MagicMock(prompt_tokens=10, completion_tokens=5, total_tokens=15)

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_make_client.return_value = mock_client

    result = chat([{"role": "user", "content": "Hi"}])

    assert result.choices[0].message.content == "Hello!"


@patch("app.common.llm_client._make_client")
def test_chat_raises_on_invalid_key(mock_make_client):
    from openai import APIStatusError
    import httpx

    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = APIStatusError(
        "Unauthorized",
        response=MagicMock(status_code=401),
        body={"error": {"message": "Invalid API key"}},
    )
    mock_make_client.return_value = mock_client

    with pytest.raises(ValueError, match="Invalid API key"):
        chat([{"role": "user", "content": "Hi"}])
