"""Agent 10: Pitch Agent — wraps HackathonService.generate_pitch."""

from __future__ import annotations

from backend.app.agents.state import AgentWorkflowState
from backend.app.services.hackathon_service import HackathonService
from backend.app.schemas.hackathon_guidance import HackathonInput


async def pitch_agent(state: AgentWorkflowState) -> AgentWorkflowState:
    """Generate multi-tier pitch scripts and populate state['pitch']."""
    try:
        user_input = state.get("user_input", {})
        hackathon_input = HackathonInput(**user_input)
        service = HackathonService()
        result = await service.generate_pitch(hackathon_input)
        state["pitch"] = result.model_dump()
        completed = list(state.get("completed_agents", []))
        completed.append("pitch")
        state["completed_agents"] = completed
        state["current_agent"] = "pitch"
        state["error"] = None
    except Exception as exc:
        state["error"] = f"pitch failed: {exc}"
    return state
