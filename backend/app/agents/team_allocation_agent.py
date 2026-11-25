"""Agent: Team Allocation Agent — wraps HackathonService.allocate_team."""

from __future__ import annotations

from backend.app.agents.state import AgentWorkflowState
from backend.app.services.hackathon_service import HackathonService
from backend.app.schemas.hackathon_guidance import HackathonInput


async def team_allocation_agent(state: AgentWorkflowState) -> AgentWorkflowState:
    """Allocate team roles, tasks, and deliverables, populating state['team_allocation']."""
    try:
        user_input = dict(state.get("user_input", {}))
        hackathon_input = HackathonInput(**user_input)
        service = HackathonService()
        result = await service.allocate_team(hackathon_input)
        state["team_allocation"] = result.model_dump()
        completed = list(state.get("completed_agents", []))
        completed.append("team_allocation")
        state["completed_agents"] = completed
        state["current_agent"] = "team_allocation"
        state["error"] = None
    except Exception as exc:
        state["error"] = f"team_allocation failed: {exc}"
    return state
