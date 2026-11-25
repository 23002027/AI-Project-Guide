"""Agent 4: Technology Advisor — wraps TechnologyAdvisorService."""

from __future__ import annotations

from backend.app.agents.state import AgentWorkflowState
from backend.app.services.technology_advisor import TechnologyAdvisorService
from backend.app.schemas.project_guidance import ProjectInput


async def technology_advisor_agent(state: AgentWorkflowState) -> AgentWorkflowState:
    """Recommend technology stack and populate state['technology_stack']."""
    try:
        user_input = state.get("user_input", {})
        project_input = ProjectInput.from_flexible_dict(user_input)
        service = TechnologyAdvisorService()
        result = await service.recommend(project_input)
        state["technology_stack"] = result.model_dump()
        completed = list(state.get("completed_agents", []))
        completed.append("technology_advisor")
        state["completed_agents"] = completed
        state["current_agent"] = "technology_advisor"
        state["error"] = None
    except Exception as exc:
        state["error"] = f"technology_advisor failed: {exc}"
    return state
