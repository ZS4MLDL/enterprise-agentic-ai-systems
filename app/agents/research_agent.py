"""
Research Agent — first stateful agent (Module 03).

Builds a LangGraph StateGraph with one node: call_llm.
State is persisted via a checkpointer so conversations survive restarts.
The same thread_id resumes the exact conversation from where it left off.
"""
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END

from app.agents.state import AgentState
from app.agents.checkpointer import get_checkpointer
from app.common.llm_client import chat
from app.config.model_registry import ModelTier

SYSTEM_PROMPT = (
    "You are an enterprise research assistant. "
    "Answer questions clearly and concisely. "
    "If you do not know something, say so rather than guessing."
)


def call_llm(state: AgentState) -> dict:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in state["messages"]:
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        messages.append({"role": role, "content": msg.content})

    response = chat(messages, tier=ModelTier.DEFAULT)
    reply = response.choices[0].message.content

    return {
        "messages": [{"role": "assistant", "content": reply}],
        "turn_count": state.get("turn_count", 0) + 1,
    }


def build_graph():
    checkpointer = get_checkpointer()
    graph = StateGraph(AgentState)
    graph.add_node("call_llm", call_llm)
    graph.set_entry_point("call_llm")
    graph.add_edge("call_llm", END)
    return graph.compile(checkpointer=checkpointer)


# Module-level compiled graph — shared across requests
_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


def run(session_id: str, user_message: str) -> str:
    """Run one turn and return the assistant reply."""
    graph = get_graph()
    config = {"configurable": {"thread_id": session_id}}
    state = {"messages": [HumanMessage(content=user_message)], "session_id": session_id}
    result = graph.invoke(state, config=config)
    return result["messages"][-1].content


def stream(session_id: str, user_message: str):
    """Stream one turn, yielding text chunks as they arrive."""
    graph = get_graph()
    config = {"configurable": {"thread_id": session_id}}
    state = {"messages": [HumanMessage(content=user_message)], "session_id": session_id}
    for chunk in graph.stream(state, config=config, stream_mode="values"):
        messages = chunk.get("messages", [])
        if messages:
            last = messages[-1]
            if hasattr(last, "content") and last.content:
                yield last.content
