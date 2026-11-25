"""
Agent 9: Testing Agent — NEW agent for automated test-plan generation.

Generates a comprehensive testing strategy for the project: unit tests,
integration tests, and end-to-end test scaffolding using Claude.
"""

from __future__ import annotations

from backend.app.agents.state import AgentWorkflowState
from backend.app.services.claude_service import ClaudeService
from backend.app.schemas.project_guidance import ProjectInput
from pydantic import BaseModel, Field
from typing import List


class TestingStrategy(BaseModel):
    """Structured testing strategy output."""
    unit_tests: List[str] = Field(description="Unit test cases to implement")
    integration_tests: List[str] = Field(description="Integration test cases")
    e2e_tests: List[str] = Field(description="End-to-end test scenarios")
    testing_tools: List[str] = Field(description="Recommended testing frameworks and tools")
    ci_pipeline_steps: List[str] = Field(description="CI/CD pipeline testing steps")
    coverage_targets: str = Field(description="Recommended code coverage targets")
    testing_advice: str = Field(description="General testing strategy advice for the project")


async def testing_agent(state: AgentWorkflowState) -> AgentWorkflowState:
    """Generate a testing strategy for the project."""
    try:
        user_input = state.get("user_input", {})
        project_input = ProjectInput.from_flexible_dict(user_input)

        # Build a context-rich prompt using existing analysis if available
        analysis_ctx = ""
        if state.get("project_analysis"):
            pa = state["project_analysis"]
            analysis_ctx = f"\nProject analysis summary: {pa.get('proposed_solution', '')}"
        if state.get("technology_stack"):
            ts = state["technology_stack"]
            tech_names = [t.get("tech_name", "") for t in ts.get("technologies", [])]
            analysis_ctx += f"\nTechnology stack: {', '.join(tech_names)}"

        system_prompt = (
            "You are a Senior QA Engineer and testing expert. Generate a comprehensive, "
            "actionable testing strategy for the described project. Focus on practical "
            "test cases a college student or small team can implement."
        )
        user_prompt = (
            f"Project: {project_input.title}\n"
            f"Domain: {project_input.domain}\n"
            f"Skills: {', '.join(project_input.skills)}\n"
            f"Experience level: {project_input.experience_level}\n"
            f"{analysis_ctx}\n\n"
            "Generate a full testing strategy including unit, integration, and E2E tests, "
            "recommended tools, CI pipeline steps, and coverage targets."
        )

        service = ClaudeService()
        result = await service.complete_structured(system_prompt, user_prompt, TestingStrategy)
        state["test_plan"] = result.model_dump()
        completed = list(state.get("completed_agents", []))
        completed.append("testing")
        state["completed_agents"] = completed
        state["current_agent"] = "testing"
        state["error"] = None
    except Exception as exc:
        state["error"] = f"testing failed: {exc}"
    return state
