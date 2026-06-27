"""
Base agent class (Module 04) — all specialist agents inherit from this.
Defines the contract: state schema, lifecycle hooks, and tool dispatch.
"""
from abc import ABC, abstractmethod
from typing import Any


class AgentState(dict):
    """Typed dict for LangGraph state — subclass to add fields."""
    pass


class BaseAgent(ABC):
    """
    Minimal agent contract.

    Subclasses implement `build_graph()` which returns a compiled LangGraph
    StateGraph.  The runtime (app/agents/runtime.py) calls `.run()` and
    `.stream()` — subclasses should not override those.
    """

    def __init__(self, session_id: str, config: dict | None = None):
        self.session_id = session_id
        self.config = config or {}
        self._graph = None

    def _ensure_graph(self):
        if self._graph is None:
            self._graph = self.build_graph()

    @abstractmethod
    def build_graph(self):
        """Return a compiled LangGraph StateGraph."""
        ...

    def run(self, input_state: dict) -> dict:
        self._ensure_graph()
        return self._graph.invoke(input_state, config={"configurable": {"thread_id": self.session_id}})

    def stream(self, input_state: dict):
        self._ensure_graph()
        return self._graph.stream(input_state, config={"configurable": {"thread_id": self.session_id}})
