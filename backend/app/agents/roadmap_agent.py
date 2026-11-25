"""Agent 6: Roadmap Agent — wraps RoadmapGeneratorService."""

from __future__ import annotations

from backend.app.agents.state import AgentWorkflowState
from backend.app.services.roadmap_generator import RoadmapGeneratorService
from backend.app.schemas.project_guidance import ProjectInput


async def roadmap_agent(state: AgentWorkflowState) -> AgentWorkflowState:
    """Generate development roadmap and populate state['roadmap']."""
    try:
        user_input = state.get("user_input", {})
        project_input = ProjectInput.from_flexible_dict(user_input)
        service = RoadmapGeneratorService()
        result = await service.generate(project_input)
        state["roadmap"] = result.model_dump()
        completed = list(state.get("completed_agents", []))
        completed.append("roadmap")
        state["completed_agents"] = completed
        state["current_agent"] = "roadmap"
        state["error"] = None
    except Exception as exc:
        state["error"] = f"roadmap failed: {exc}"
    return state
