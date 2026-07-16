"""
LangGraph workflow definitions for agentic AI orchestration.

Each workflow is a directed state graph with typed nodes and edges.
"""

from dataclasses import dataclass, field
from typing import Any
from typing import AsyncGenerator


@dataclass
class AgentState:
    """Typed state passed through a LangGraph workflow.

    Attributes:
        messages:     Conversation history as a list of message dicts.
        context:      Retrieved documents and contextual data.
        metadata:     Arbitrary workflow-specific state.
        step_outputs: Outputs from individual graph nodes.
    """

    messages: list[dict[str, Any]] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    step_outputs: dict[str, Any] = field(default_factory=dict)


class BaseWorkflow:
    """Abstract base for all LangGraph workflows.

    Subclasses define nodes and edges in `build_graph()`.
    """

    def __init__(self, name: str) -> None:
        ...

    def build_graph(self) -> None:
        """Constructs the LangGraph state graph (nodes + edges)."""
        ...

    async def run(self, initial_state: AgentState) -> AgentState:
        """Executes the workflow graph with the given initial state."""
        ...

    async def stream(self, initial_state: AgentState) -> AsyncGenerator[AgentState, None]:
        """Yields intermediate states for real-time streaming."""
        ...


class WorkflowRouter:
    """Routes incoming requests to the appropriate workflow definition."""

    def __init__(self) -> None:
        ...

    def register(self, name: str, workflow: BaseWorkflow) -> None:
        """Registers a workflow under a given name."""
        ...

    def get_workflow(self, name: str) -> BaseWorkflow:
        """Returns the registered workflow by name."""
        ...
