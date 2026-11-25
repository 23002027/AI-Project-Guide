"""Agent 1: Project Analyzer — wraps ProjectAnalyzerService."""

from __future__ import annotations

from backend.app.agents.state import AgentWorkflowState
from backend.app.services.project_analyzer import ProjectAnalyzerService
from backend.app.schemas.project_guidance import ProjectInput


async def project_analyzer_agent(state: AgentWorkflowState) -> AgentWorkflowState:
    """Analyze the user's project idea and populate state['project_analysis']."""
    try:
        user_input = state.get("user_input", {})
        project_input = ProjectInput.from_flexible_dict(user_input)
        service = ProjectAnalyzerService()
        result = await service.analyze(project_input)
        state["project_analysis"] = result.model_dump()
        completed = list(state.get("completed_agents", []))
        completed.append("project_analyzer")
        state["completed_agents"] = completed
        state["current_agent"] = "project_analyzer"
        state["error"] = None
    except Exception as exc:
        state["error"] = f"project_analyzer failed: {exc}"
    return state
