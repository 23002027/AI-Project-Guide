"""Agent: MVP Planning Agent — wraps HackathonService.plan_mvp."""

from __future__ import annotations

from backend.app.agents.state import AgentWorkflowState
from backend.app.services.hackathon_service import HackathonService
from backend.app.schemas.hackathon_guidance import HackathonInput


async def mvp_planning_agent(state: AgentWorkflowState) -> AgentWorkflowState:
    """Scope MoSCoW MVP features and populate state['mvp_plan']."""
    try:
        user_input = dict(state.get("user_input", {}))
        hackathon_input = HackathonInput(**user_input)
        service = HackathonService()
        result = await service.plan_mvp(hackathon_input)
        state["mvp_plan"] = result.model_dump()
        completed = list(state.get("completed_agents", []))
        completed.append("mvp_planning")
        state["completed_agents"] = completed
        state["current_agent"] = "mvp_planning"
        state["error"] = None
    except Exception as exc:
        state["error"] = f"mvp_planning failed: {exc}"
    return state
