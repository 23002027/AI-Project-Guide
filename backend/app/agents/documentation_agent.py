"""Agent 8: Documentation Agent — wraps DocumentationGeneratorService."""

from __future__ import annotations

from backend.app.agents.state import AgentWorkflowState
from backend.app.services.documentation_generator import DocumentationGeneratorService
from backend.app.schemas.project_guidance import ProjectInput


async def documentation_agent(state: AgentWorkflowState) -> AgentWorkflowState:
    """Generate documentation and populate state['documentation']."""
    try:
        user_input = state.get("user_input", {})
        project_input = ProjectInput.from_flexible_dict(user_input)
        service = DocumentationGeneratorService()
        result = await service.generate(project_input)
        state["documentation"] = result.model_dump()
        completed = list(state.get("completed_agents", []))
        completed.append("documentation")
        state["completed_agents"] = completed
        state["current_agent"] = "documentation"
        state["error"] = None
    except Exception as exc:
        state["error"] = f"documentation failed: {exc}"
    return state
