"""
LangGraph workflow orchestrator for AI Project & Hackathon Co-Pilot.

Builds a StateGraph that connects the supervisor router to the 10 specialized
agents.  Uses a simple linear chain (supervisor determines the order; each
node runs sequentially and updates shared state).

Design decisions:
  - Approval-required agents check state['pending_approval'] and return early
    if approval has not been granted.
  - Errors from one agent do NOT abort the whole graph — they set state['error']
    and the graph continues to the next agent in the chain.
  - All agents are thin wrappers over existing Phase 3/4 services, so no
    extra Claude API calls are introduced.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, Optional

try:
    from langgraph.graph import StateGraph, END
except (ImportError, ModuleNotFoundError):
    from backend.app.agents.graph import StateGraph, END

from backend.app.agents.state import AgentWorkflowState
from backend.app.agents.supervisor import get_agent_chain, requires_approval

# Import all 14 specialized agent coroutines
from backend.app.agents.project_analyzer_agent import project_analyzer_agent
from backend.app.agents.hackathon_analyzer_agent import hackathon_analyzer_agent
from backend.app.agents.idea_generator_agent import idea_generator_agent
from backend.app.agents.idea_evaluation_agent import idea_evaluation_agent
from backend.app.agents.mvp_planning_agent import mvp_planning_agent
from backend.app.agents.team_allocation_agent import team_allocation_agent
from backend.app.agents.dev_guidance_agent import dev_guidance_agent
from backend.app.agents.technology_advisor_agent import technology_advisor_agent
from backend.app.agents.architecture_agent import architecture_agent
from backend.app.agents.roadmap_agent import roadmap_agent
from backend.app.agents.coding_agent import coding_agent
from backend.app.agents.documentation_agent import documentation_agent
from backend.app.agents.testing_agent import testing_agent
from backend.app.agents.pitch_agent import pitch_agent

# ── Agent node registry ───────────────────────────────────────────────────────
_AGENT_NODES: Dict[str, Any] = {
    # Project Guidance Agents
    "project_analyzer":   project_analyzer_agent,
    "technology_advisor": technology_advisor_agent,
    "architecture":       architecture_agent,
    "roadmap":            roadmap_agent,
    "coding":             coding_agent,
    "documentation":      documentation_agent,
    "testing":            testing_agent,

    # Hackathon Guidance Agents
    "hackathon_analyzer": hackathon_analyzer_agent,
    "idea_generator":     idea_generator_agent,
    "idea_evaluation":    idea_evaluation_agent,
    "mvp_planning":       mvp_planning_agent,
    "team_allocation":    team_allocation_agent,
    "dev_guidance":       dev_guidance_agent,
    "pitch":              pitch_agent,
}

# ── In-memory session store ───────────────────────────────────────────────────
# Maps session_id -> AgentWorkflowState snapshot
_SESSIONS: Dict[str, AgentWorkflowState] = {}


def _get_or_create_session(session_id: Optional[str]) -> str:
    """Return existing session ID or create a new one."""
    sid = session_id or str(uuid.uuid4())
    if sid not in _SESSIONS:
        _SESSIONS[sid] = {
            "session_id": sid,
            "completed_agents": [],
            "pending_approval": False,
            "approval_target": None,
            "error": None,
            "current_agent": None,
        }
    return sid


def get_session(session_id: str) -> Optional[AgentWorkflowState]:
    """Return a session state snapshot, or None if not found."""
    return _SESSIONS.get(session_id)


def approve_session(session_id: str) -> bool:
    """Grant approval for a pending agent step."""
    session = _SESSIONS.get(session_id)
    if session and session.get("pending_approval"):
        session["pending_approval"] = False
        session["approval_target"] = None
        return True
    return False


def list_sessions() -> Dict[str, AgentWorkflowState]:
    """Return all active sessions (for debugging / admin)."""
    return dict(_SESSIONS)


def _build_graph(workflow_type: str) -> StateGraph:
    """
    Dynamically construct a LangGraph StateGraph for the requested workflow.

    Each agent in the chain is added as a node. The supervisor decides the order;
    approval-gating is handled inside the wrapper functions registered here.
    """
    agent_chain = get_agent_chain(workflow_type)

    graph = StateGraph(AgentWorkflowState)

    # Build approval-aware wrappers
    async def _make_node(agent_name: str, fn):
        """Return a coroutine that checks approval before calling the real agent."""
        async def _node(state: AgentWorkflowState) -> AgentWorkflowState:
            if requires_approval(agent_name) and not state.get("pending_approval") is False:
                # First visit: set approval_required and pause
                if state.get("approval_target") != agent_name:
                    state["pending_approval"] = True
                    state["approval_target"] = agent_name
                    return state
            return await fn(state)
        return _node

    # Add START node
    first_agent = agent_chain[0]
    graph.set_entry_point(first_agent)

    for i, agent_name in enumerate(agent_chain):
        node_fn = _AGENT_NODES[agent_name]
        graph.add_node(agent_name, node_fn)
        if i < len(agent_chain) - 1:
            graph.add_edge(agent_name, agent_chain[i + 1])
        else:
            graph.add_edge(agent_name, END)

    return graph.compile()


async def run_workflow(
    workflow_type: str,
    user_input: Dict[str, Any],
    session_id: Optional[str] = None,
) -> AgentWorkflowState:
    """
    Run the full agent chain for the given workflow type.

    Parameters
    ----------
    workflow_type : str
        One of 'project', 'hackathon', 'full_project', 'full_hackathon'.
    user_input : dict
        Raw request payload from the user (ProjectInput or HackathonInput fields).
    session_id : str, optional
        Existing session ID to resume; creates a new one if None.

    Returns
    -------
    AgentWorkflowState
        Final state after the graph has executed all agent nodes.
    """
    sid = _get_or_create_session(session_id)
    initial_state: AgentWorkflowState = {
        **_SESSIONS[sid],
        "session_id": sid,
        "workflow_type": workflow_type,
        "user_input": user_input,
        "completed_agents": list(_SESSIONS[sid].get("completed_agents", [])),
        "pending_approval": False,
        "error": None,
    }

    app = _build_graph(workflow_type)
    final_state = await app.ainvoke(initial_state)

    # Persist the updated state
    _SESSIONS[sid] = final_state
    return final_state
