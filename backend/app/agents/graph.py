"""
LangGraph StateGraph Engine (In-tree compatible implementation).
Provides StateGraph, END, START, and conditional edge routing matching
the langgraph.graph API specification so workflows run natively in any environment.
"""

from __future__ import annotations

import inspect
from typing import Any, Callable, Dict, List, Optional, Set, Union

END = "__END__"
START = "__START__"


class CompiledGraph:
    """Compiled LangGraph workflow runner supporting sync invoke and async ainvoke."""

    def __init__(
        self,
        nodes: Dict[str, Callable],
        edges: Dict[str, str],
        conditional_edges: Dict[str, tuple[Callable, Dict[str, str]]],
        entry_point: Optional[str] = None,
    ):
        self.nodes = nodes
        self.edges = edges
        self.conditional_edges = conditional_edges
        self.entry_point = entry_point

    async def ainvoke(self, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        """Asynchronously execute the state graph starting from entry_point."""
        current_state = dict(initial_state)
        current_node_name = self.entry_point

        visited_nodes: Set[str] = set()
        max_steps = 100
        step_count = 0

        while current_node_name and current_node_name != END and step_count < max_steps:
            step_count += 1
            if current_node_name not in self.nodes:
                break

            node_fn = self.nodes[current_node_name]
            
            # Execute node
            if inspect.iscoroutinefunction(node_fn):
                res = await node_fn(current_state)
            else:
                res = node_fn(current_state)

            if isinstance(res, dict):
                current_state.update(res)

            # Check if workflow was paused by human approval checkpoint
            if current_state.get("pending_approval") is True:
                break

            # Determine next node
            if current_node_name in self.conditional_edges:
                condition_fn, branch_map = self.conditional_edges[current_node_name]
                if inspect.iscoroutinefunction(condition_fn):
                    branch_key = await condition_fn(current_state)
                else:
                    branch_key = condition_fn(current_state)
                next_node = branch_map.get(branch_key, END)
            elif current_node_name in self.edges:
                next_node = self.edges[current_node_name]
            else:
                next_node = END

            current_node_name = next_node

        return current_state

    def invoke(self, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronously execute the state graph."""
        import asyncio
        return asyncio.run(self.ainvoke(initial_state))


class StateGraph:
    """
    LangGraph StateGraph builder.
    Enables adding nodes, directed edges, conditional edges, and compiling.
    """

    def __init__(self, state_schema: Any = None):
        self.state_schema = state_schema
        self.nodes: Dict[str, Callable] = {}
        self.edges: Dict[str, str] = {}
        self.conditional_edges: Dict[str, tuple[Callable, Dict[str, str]]] = {}
        self.entry_point: Optional[str] = None

    def add_node(self, name: str, action: Callable):
        """Add a named node to the graph."""
        self.nodes[name] = action
        return self

    def set_entry_point(self, name: str):
        """Set the start node of the graph."""
        self.entry_point = name
        return self

    def add_edge(self, start_key: str, end_key: str):
        """Add a directed edge between two nodes."""
        if start_key == START:
            self.entry_point = end_key
        else:
            self.edges[start_key] = end_key
        return self

    def add_conditional_edges(
        self,
        source: str,
        path: Callable,
        path_map: Dict[str, str],
    ):
        """Add a conditional branching edge from source node."""
        self.conditional_edges[source] = (path, path_map)
        return self

    def compile(self) -> CompiledGraph:
        """Compile the graph into a runnable instance."""
        return CompiledGraph(
            nodes=self.nodes,
            edges=self.edges,
            conditional_edges=self.conditional_edges,
            entry_point=self.entry_point,
        )
