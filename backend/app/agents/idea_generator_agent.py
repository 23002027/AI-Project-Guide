"""Agent 3: Idea Generator — wraps HackathonService.generate_ideas."""

from __future__ import annotations

from backend.app.agents.state import AgentWorkflowState
from backend.app.services.hackathon_service import HackathonService
from backend.app.schemas.hackathon_guidance import HackathonInput


async def idea_generator_agent(state: AgentWorkflowState) -> AgentWorkflowState:
    """Generate hackathon ideas and populate state['generated_ideas']."""
    try:
        user_input = state.get("user_input", {})
        hackathon_input = HackathonInput(**user_input)
        service = HackathonService()
        result = await service.generate_ideas(hackathon_input)
        state["generated_ideas"] = result.model_dump()
        completed = list(state.get("completed_agents", []))
        completed.append("idea_generator")
        state["completed_agents"] = completed
        state["current_agent"] = "idea_generator"
        state["error"] = None
    except Exception as exc:
        state["error"] = f"idea_generator failed: {exc}"
    return state
