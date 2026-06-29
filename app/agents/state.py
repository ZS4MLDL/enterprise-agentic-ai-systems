"""
Agent state schema (Module 03).
All LangGraph nodes read from and write to this TypedDict.
"""
from typing import Annotated
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]   # full conversation history
    session_id: str                            # ties state to a user session
    turn_count: int                            # how many user turns so far
