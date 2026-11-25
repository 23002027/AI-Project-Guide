"""Agent 5: Architecture Agent — wraps ArchitectureGeneratorService."""

from __future__ import annotations

from backend.app.agents.state import AgentWorkflowState
from backend.app.services.architecture_generator import ArchitectureGeneratorService
from backend.app.schemas.project_guidance import ProjectInput


async def architecture_agent(state: AgentWorkflowState) -> AgentWorkflowState:
    """Generate system architecture and populate state['architecture']."""
    try:
        user_input = state.get("user_input", {})
        project_input = ProjectInput.from_flexible_dict(user_input)
        service = ArchitectureGeneratorService()
        result = await service.generate(project_input)
        state["architecture"] = result.model_dump()
        completed = list(state.get("completed_agents", []))
        completed.append("architecture")
        state["completed_agents"] = completed
        state["current_agent"] = "architecture"
        state["error"] = None
    except Exception as exc:
        state["error"] = f"architecture failed: {exc}"
    return state
