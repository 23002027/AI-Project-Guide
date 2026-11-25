"""Agent: Development Guidance Agent — wraps HackathonService.advise_technologies."""

from __future__ import annotations

from backend.app.agents.state import AgentWorkflowState
from backend.app.services.hackathon_service import HackathonService
from backend.app.schemas.hackathon_guidance import HackathonInput


async def dev_guidance_agent(state: AgentWorkflowState) -> AgentWorkflowState:
    """Generate free-first tech stack & copy-ready prompts, populating state['dev_guidance']."""
    try:
        user_input = dict(state.get("user_input", {}))
        hackathon_input = HackathonInput(**user_input)
        service = HackathonService()
        result = await service.generate_dev_guidance(hackathon_input)
        state["dev_guidance"] = result.model_dump()
        completed = list(state.get("completed_agents", []))
        completed.append("dev_guidance")
        state["completed_agents"] = completed
        state["current_agent"] = "dev_guidance"
        state["error"] = None
    except Exception as exc:
        state["error"] = f"dev_guidance failed: {exc}"
    return state
