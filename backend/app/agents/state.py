"""
Shared workflow state passed between all agents in the LangGraph StateGraph.

Each field is Optional so agents can be run independently or as part of a
full pipeline.  The supervisor reads `workflow_type` to decide which agent
chain to invoke.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional
from typing_extensions import TypedDict


class AgentWorkflowState(TypedDict, total=False):
    # ── Identity ──────────────────────────────────────────────────────────
    session_id: str
    workflow_type: Literal["project", "hackathon", "full_project", "full_hackathon"]

    # ── Raw user input (passes into the first agent) ──────────────────────
    user_input: Dict[str, Any]

    # ── Per-agent outputs (populated as the graph executes) ───────────────
    # Project Guidance Agents
    project_analysis: Optional[Dict[str, Any]]
    technology_stack: Optional[Dict[str, Any]]
    architecture: Optional[Dict[str, Any]]
    roadmap: Optional[Dict[str, Any]]
    coding_prompts: Optional[Dict[str, Any]]
    documentation: Optional[Dict[str, Any]]
    test_plan: Optional[Dict[str, Any]]

    # Hackathon Guidance Agents
    hackathon_analysis: Optional[Dict[str, Any]]
    generated_ideas: Optional[Dict[str, Any]]
    idea_evaluation: Optional[Dict[str, Any]]
    mvp_plan: Optional[Dict[str, Any]]
    team_allocation: Optional[Dict[str, Any]]
    dev_guidance: Optional[Dict[str, Any]]
    pitch: Optional[Dict[str, Any]]

    # ── Execution metadata ────────────────────────────────────────────────
    completed_agents: List[str]        # names of agents that have finished
    pending_approval: bool             # True when a step needs user sign-off
    approval_target: Optional[str]     # which agent/step is awaiting approval
    error: Optional[str]               # last error message if any agent failed
    current_agent: Optional[str]       # name of the agent currently running
