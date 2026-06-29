"""
Module 03 — unit tests for the stateful research agent.
LLM calls and the compiled graph are mocked — no real API or DB needed.
"""
from unittest.mock import MagicMock, patch
from langchain_core.messages import HumanMessage, AIMessage


# ── call_llm node tests ───────────────────────────────────────────────────────

@patch("app.agents.research_agent.chat")
def test_call_llm_returns_reply(mock_chat):
    from app.agents.research_agent import call_llm

    mock_chat.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="Paris is the capital of France."))]
    )
    state = {
        "messages": [HumanMessage(content="Capital of France?")],
        "session_id": "s1",
        "turn_count": 0,
    }
    result = call_llm(state)
    assert result["turn_count"] == 1
    assert any("Paris" in m["content"] for m in result["messages"] if isinstance(m, dict))


@patch("app.agents.research_agent.chat")
def test_turn_count_increments(mock_chat):
    from app.agents.research_agent import call_llm

    mock_chat.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="Answer"))]
    )
    state = {
        "messages": [HumanMessage(content="Hello")],
        "session_id": "s2",
        "turn_count": 4,
    }
    result = call_llm(state)
    assert result["turn_count"] == 5


# ── run() / stream() with graph mocked ───────────────────────────────────────

@patch("app.agents.research_agent.get_graph")
def test_run_returns_last_message(mock_get_graph):
    from app.agents.research_agent import run

    mock_graph = MagicMock()
    mock_graph.invoke.return_value = {
        "messages": [
            HumanMessage(content="Q"),
            AIMessage(content="The answer is 42."),
        ],
        "turn_count": 1,
        "session_id": "s3",
    }
    mock_get_graph.return_value = mock_graph

    reply = run("s3", "What is the answer?")
    assert reply == "The answer is 42."


@patch("app.agents.research_agent.get_graph")
def test_run_called_twice_same_session(mock_get_graph):
    """Same session_id should invoke the graph twice (resume simulation)."""
    from app.agents.research_agent import run

    mock_graph = MagicMock()
    mock_graph.invoke.return_value = {
        "messages": [AIMessage(content="OK")],
        "turn_count": 1,
        "session_id": "s4",
    }
    mock_get_graph.return_value = mock_graph

    run("s4", "First message")
    run("s4", "Second message")
    assert mock_graph.invoke.call_count == 2


# ── FastAPI endpoint tests ────────────────────────────────────────────────────

@patch("app.agents.research_agent.run")
def test_chat_endpoint_returns_reply(mock_run):
    from fastapi.testclient import TestClient
    from app.main import app

    mock_run.return_value = "The capital is Paris."
    client = TestClient(app)

    response = client.post(
        "/api/v1/chat",
        json={"session_id": "abc", "message": "Capital of France?"},
    )
    assert response.status_code == 200
    assert response.json()["reply"] == "The capital is Paris."


@patch("app.agents.research_agent.run")
def test_chat_endpoint_handles_auth_error(mock_run):
    from fastapi.testclient import TestClient
    from app.main import app

    mock_run.side_effect = ValueError("Invalid API key")
    client = TestClient(app)

    response = client.post(
        "/api/v1/chat",
        json={"session_id": "abc", "message": "Hello"},
    )
    assert response.status_code == 401


@patch("app.agents.research_agent.run")
def test_chat_endpoint_handles_llm_timeout(mock_run):
    from fastapi.testclient import TestClient
    from app.main import app

    mock_run.side_effect = RuntimeError("LLM request failed after 3 attempts.")
    client = TestClient(app)

    response = client.post(
        "/api/v1/chat",
        json={"session_id": "abc", "message": "Hello"},
    )
    assert response.status_code == 503
