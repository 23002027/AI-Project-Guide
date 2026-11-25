"""Agent 2: Hackathon Analyzer — wraps HackathonService.analyze_problem."""

from __future__ import annotations

from backend.app.agents.state import AgentWorkflowState
from backend.app.services.hackathon_service import HackathonService
from backend.app.schemas.hackathon_guidance import HackathonInput


async def hackathon_analyzer_agent(state: AgentWorkflowState) -> AgentWorkflowState:
    """Analyze hackathon problem statement and populate state['hackathon_analysis']."""
    try:
        user_input = state.get("user_input", {})
        hackathon_input = HackathonInput(**user_input)
        service = HackathonService()
        result = await service.analyze_problem(hackathon_input)
        state["hackathon_analysis"] = result.model_dump()
        completed = list(state.get("completed_agents", []))
        completed.append("hackathon_analyzer")
        state["completed_agents"] = completed
        state["current_agent"] = "hackathon_analyzer"
        state["error"] = None
    except Exception as exc:
        state["error"] = f"hackathon_analyzer failed: {exc}"
    return state
