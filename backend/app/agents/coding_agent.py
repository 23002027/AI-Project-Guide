"""Agent 7: Coding Agent — wraps CodingPromptGeneratorService."""

from __future__ import annotations

from backend.app.agents.state import AgentWorkflowState
from backend.app.services.coding_prompt_generator import CodingPromptGeneratorService
from backend.app.schemas.project_guidance import ProjectInput


async def coding_agent(state: AgentWorkflowState) -> AgentWorkflowState:
    """Generate coding prompts and populate state['coding_prompts']."""
    try:
        user_input = state.get("user_input", {})
        project_input = ProjectInput.from_flexible_dict(user_input)
        service = CodingPromptGeneratorService()
        result = await service.generate(project_input)
        state["coding_prompts"] = result.model_dump()
        completed = list(state.get("completed_agents", []))
        completed.append("coding")
        state["completed_agents"] = completed
        state["current_agent"] = "coding"
        state["error"] = None
    except Exception as exc:
        state["error"] = f"coding failed: {exc}"
    return state
