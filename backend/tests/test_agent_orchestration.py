"""
Phase 5 — Multi-Agent Orchestration Tests

All Claude API calls are mocked.  Zero paid API credits consumed.
LangGraph is mocked out at the orchestrator level so the tests run even
if the langgraph package is not fully available in CI.
"""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# App client
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    """Import app for testing agent orchestration endpoints."""
    from backend.app.main import app
    return TestClient(app)


# ---------------------------------------------------------------------------
# Shared mock helpers
# ---------------------------------------------------------------------------

PROJECT_INPUT = {
    "project_title": "AI Construction Safety Monitor",
    "description": "Real-time hard-hat and safety vest detection on construction sites using computer vision.",
    "domain": "AI/ML",
    "programming_skills": "Python, React, SQL",
    "experience_level": "beginner",
    "budget": "free",
    "deadline": "3 months",
    "is_team_project": True,
    "team_size": 3,
}

HACKATHON_INPUT = {
    "hackathon_name": "Smart City Hack 2026",
    "problem_statement": "Reduce road accident fatalities by detecting hazardous driving behavior in real time.",
    "duration": "24 hours",
    "team_size": 3,
    "team_skills": ["Python", "OpenCV", "React"],
    "experience_level": "intermediate",
}

MOCK_ANALYSIS = {
    "problem_statement": "Construction sites lack real-time PPE compliance monitoring.",
    "existing_limitations": ["Manual inspections are slow", "High accident rates"],
    "proposed_solution": "Computer vision model detecting safety gear compliance.",
    "target_users": ["Site managers", "Safety officers"],
    "main_objectives": ["Detect hard hats", "Detect safety vests"],
    "expected_outcomes": ["30% reduction in PPE violations"],
    "unique_selling_proposition": "Real-time edge inference with sub-200ms latency.",
    "innovation_opportunities": ["IoT integration", "Mobile dashboard"],
    "feasibility_assessment": "High — YOLOv8 runs on CPU.",
    "project_complexity": "Moderate",
}

MOCK_TECH_STACK = {
    "technologies": [
        {
            "tech_name": "FastAPI",
            "category": "Backend",
            "why_recommended": "Fast async Python web framework",
            "role": "REST API server",
            "how_to_implement": "pip install fastapi",
            "is_free": True,
            "alternatives": ["Flask"],
        }
    ],
    "ai_tools": ["GitHub Copilot", "Claude"],
    "summary": "Free-first stack using Python, React, and SQLite.",
}

MOCK_ARCH = {
    "mermaid_diagram": "graph TD\n  A[React UI] --> B[FastAPI]\n  B --> C[YOLOv8]\n  B --> D[SQLite]",
    "components": ["React Frontend", "FastAPI Backend", "YOLOv8 Inference", "SQLite DB"],
    "database_schema": "CREATE TABLE detections (id INTEGER PRIMARY KEY, timestamp TEXT, label TEXT, confidence REAL);",
    "api_endpoints": ["POST /api/detect", "GET /api/results"],
    "deployment_strategy": "Render backend + Vercel frontend",
}

MOCK_ROADMAP = {
    "phases": [
        {"phase_name": "Setup", "duration": "Week 1", "tasks": ["Init repo", "Set up FastAPI"]},
        {"phase_name": "Model Integration", "duration": "Week 2-4", "tasks": ["Train YOLOv8", "Build inference API"]},
        {"phase_name": "Frontend", "duration": "Week 5-8", "tasks": ["React dashboard", "Live video feed"]},
        {"phase_name": "Testing & Deploy", "duration": "Week 9-12", "tasks": ["Write tests", "Deploy to Render"]},
    ],
    "estimated_completion": "3 months",
    "milestones": ["MVP API", "Frontend complete", "Deployed"],
}

MOCK_CODING = {
    "modules": [
        {
            "module_name": "Detection API",
            "implementation_steps": ["Create /api/detect route", "Load YOLOv8 model", "Return JSON detections"],
            "claude_prompt": "Write a FastAPI route that accepts an image and runs YOLOv8 inference.",
            "chatgpt_prompt": "Create a Python function that runs YOLOv8 on an uploaded image.",
            "cursor_prompt": "Scaffold a FastAPI endpoint for image classification.",
        }
    ]
}

MOCK_DOCS = {
    "readme": "# AI Construction Safety Monitor\n\nReal-time PPE detection using YOLOv8.",
    "api_documentation": "## POST /api/detect\n\nAccepts an image file and returns detected PPE items.",
    "project_report_outline": ["Abstract", "Introduction", "Methodology", "Results", "Conclusion"],
    "deployment_guide": "Deploy backend on Render: connect GitHub repo, set env vars.",
    "user_manual": "1. Open dashboard\n2. Upload site image\n3. View detections",
}

MOCK_TEST_PLAN = {
    "unit_tests": ["Test YOLOv8 inference function", "Test /api/detect endpoint"],
    "integration_tests": ["Test full image upload → detection pipeline"],
    "e2e_tests": ["User uploads image and sees results on dashboard"],
    "testing_tools": ["pytest", "httpx", "React Testing Library"],
    "ci_pipeline_steps": ["Run pytest", "Lint with ruff", "Build Docker image"],
    "coverage_targets": "80% minimum coverage on backend services",
    "testing_advice": "Mock external model calls for unit tests to avoid slow inference.",
}


def _make_mock_block(data: dict):
    """Return a mock Anthropic API response wrapping JSON-encoded data."""
    import json
    mock_block = MagicMock()
    mock_block.type = "text"
    mock_block.text = json.dumps(data)
    mock_response = MagicMock()
    mock_response.content = [mock_block]
    return mock_response


# ---------------------------------------------------------------------------
# Helper: mock the entire orchestrator.run_workflow
# ---------------------------------------------------------------------------

def _full_project_state(session_id: str = "test-session-123"):
    return {
        "session_id": session_id,
        "workflow_type": "full_project",
        "completed_agents": ["project_analyzer", "technology_advisor", "architecture", "roadmap", "coding", "documentation", "testing"],
        "pending_approval": False,
        "approval_target": None,
        "error": None,
        "current_agent": "testing",
        "user_input": PROJECT_INPUT,
        "project_analysis": MOCK_ANALYSIS,
        "technology_stack": MOCK_TECH_STACK,
        "architecture": MOCK_ARCH,
        "roadmap": MOCK_ROADMAP,
        "coding_prompts": MOCK_CODING,
        "documentation": MOCK_DOCS,
        "test_plan": MOCK_TEST_PLAN,
    }


def _hackathon_state(session_id: str = "hack-session-456"):
    return {
        "session_id": session_id,
        "workflow_type": "hackathon",
        "completed_agents": [
            "hackathon_analyzer", "idea_generator", "idea_evaluation",
            "mvp_planning", "team_allocation", "dev_guidance", "pitch"
        ],
        "pending_approval": False,
        "approval_target": None,
        "error": None,
        "current_agent": "pitch",
        "user_input": HACKATHON_INPUT,
        "hackathon_analysis": {"problem_summary": "Hazardous driving behavior detection challenge."},
        "generated_ideas": {"ideas": [{"idea_id": 1, "project_title": "DriveGuard AI"}]},
        "idea_evaluation": {"recommended_idea_title": "DriveGuard AI", "weighted_total_score": 9.2},
        "mvp_plan": {"must_have_features": ["Video feed", "Accident warning"]},
        "team_allocation": {"member_assignments": [{"member_name": "Dev 1", "assigned_role": "Backend"}]},
        "dev_guidance": {"recommended_tech_stack": [{"tech_name": "FastAPI", "license_type": "Open-Source"}]},
        "pitch": {"pitch_30_seconds": "DriveGuard AI detects reckless driving in real time."},
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestAgentOrchestrationEndpoints:
    """Test the /api/agent/* REST endpoints."""

    def test_run_project_workflow(self, client):
        """POST /api/agent/run with workflow_type=full_project returns aggregated results."""
        with patch("backend.app.api.routes.agent_orchestration.run_workflow",
                   new=AsyncMock(return_value=_full_project_state())), \
             patch("backend.app.config.Settings.is_anthropic_configured", True):
            res = client.post("/api/agent/run", json={
                "workflow_type": "full_project",
                "user_input": PROJECT_INPUT,
            })
        assert res.status_code == 200
        data = res.json()
        assert data["session_id"] == "test-session-123"
        assert data["workflow_type"] == "full_project"
        assert "project_analyzer" in data["completed_agents"]
        assert "technology_advisor" in data["completed_agents"]
        assert "architecture" in data["completed_agents"]
        assert "roadmap" in data["completed_agents"]
        assert "coding" in data["completed_agents"]
        assert "documentation" in data["completed_agents"]
        assert "testing" in data["completed_agents"]
        assert len(data["completed_agents"]) == 7
        assert data["pending_approval"] is False
        assert data["error"] is None

    def test_run_hackathon_workflow(self, client):
        """POST /api/agent/run with workflow_type=hackathon returns hackathon results."""
        with patch("backend.app.api.routes.agent_orchestration.run_workflow",
                   new=AsyncMock(return_value=_hackathon_state())), \
             patch("backend.app.config.Settings.is_anthropic_configured", True):
            res = client.post("/api/agent/run", json={
                "workflow_type": "hackathon",
                "user_input": HACKATHON_INPUT,
            })
        assert res.status_code == 200
        data = res.json()
        assert data["workflow_type"] == "hackathon"
        assert "hackathon_analyzer" in data["completed_agents"]
        assert "idea_generator" in data["completed_agents"]
        assert "pitch" in data["completed_agents"]
        assert "results" in data
        assert "hackathon_analysis" in data["results"]
        assert "pitch" in data["results"]

    def test_run_workflow_unconfigured_api(self, client):
        """POST /api/agent/run returns 503 when API key is missing."""
        with patch("backend.app.config.Settings.is_anthropic_configured", False):
            res = client.post("/api/agent/run", json={
                "workflow_type": "project",
                "user_input": PROJECT_INPUT,
            })
        assert res.status_code == 503
        assert res.json()["detail"]["error"] == "ai_service_unconfigured"

    def test_get_session_status(self, client):
        """GET /api/agent/status/{session_id} returns session state."""
        with patch("backend.app.api.routes.agent_orchestration.get_session",
                   return_value=_full_project_state("status-test-999")):
            res = client.get("/api/agent/status/status-test-999")
        assert res.status_code == 200
        data = res.json()
        assert data["session_id"] == "status-test-999"
        assert len(data["completed_agents"]) == 7

    def test_get_session_status_not_found(self, client):
        """GET /api/agent/status with unknown ID returns 404."""
        with patch("backend.app.api.routes.agent_orchestration.get_session", return_value=None):
            res = client.get("/api/agent/status/nonexistent-id")
        assert res.status_code == 404
        assert res.json()["detail"]["error"] == "session_not_found"

    def test_get_workflow_history(self, client):
        """GET /api/agent/history/{session_id} returns completed agent list."""
        with patch("backend.app.api.routes.agent_orchestration.get_session",
                   return_value=_full_project_state("history-test-777")):
            res = client.get("/api/agent/history/history-test-777")
        assert res.status_code == 200
        data = res.json()
        assert data["session_id"] == "history-test-777"
        assert "completed_agents" in data
        assert len(data["completed_agents"]) == 7

    def test_approve_pending_step(self, client):
        """POST /api/agent/approve/{session_id} grants approval for pending step."""
        with patch("backend.app.api.routes.agent_orchestration.get_session",
                   return_value={**_full_project_state("approve-test"),
                                 "pending_approval": True,
                                 "approval_target": "architecture"}), \
             patch("backend.app.api.routes.agent_orchestration.approve_session",
                   return_value=True):
            res = client.post("/api/agent/approve/approve-test")
        assert res.status_code == 200
        data = res.json()
        assert data["approved"] is True
        assert "approve-test" in data["message"] or "Resume" in data["message"]

    def test_approve_no_pending(self, client):
        """POST /api/agent/approve when nothing is pending returns approved=False."""
        with patch("backend.app.api.routes.agent_orchestration.get_session",
                   return_value=_full_project_state("no-pending")), \
             patch("backend.app.api.routes.agent_orchestration.approve_session",
                   return_value=False):
            res = client.post("/api/agent/approve/no-pending")
        assert res.status_code == 200
        data = res.json()
        assert data["approved"] is False

    def test_retry_failed_workflow(self, client):
        """POST /api/agent/retry/{session_id} re-runs the workflow."""
        failed_state = {**_full_project_state("retry-test"), "error": "architecture failed: timeout"}
        with patch("backend.app.api.routes.agent_orchestration.get_session",
                   return_value=failed_state), \
             patch("backend.app.api.routes.agent_orchestration.run_workflow",
                   new=AsyncMock(return_value=_full_project_state("retry-test"))), \
             patch("backend.app.config.Settings.is_anthropic_configured", True):
            res = client.post("/api/agent/retry/retry-test")
        assert res.status_code == 200
        data = res.json()
        assert data["error"] is None


class TestAgentSupervisor:
    """Test the supervisor routing logic (no Claude calls needed)."""

    def test_project_chain(self):
        from backend.app.agents.supervisor import get_agent_chain
        chain = get_agent_chain("project")
        assert "project_analyzer" in chain
        assert "technology_advisor" in chain
        assert "architecture" in chain

    def test_hackathon_chain(self):
        from backend.app.agents.supervisor import get_agent_chain
        chain = get_agent_chain("hackathon")
        assert "hackathon_analyzer" in chain
        assert "idea_generator" in chain
        assert "idea_evaluation" in chain
        assert "mvp_planning" in chain
        assert "team_allocation" in chain
        assert "dev_guidance" in chain
        assert "pitch" in chain
        assert len(chain) == 7

    def test_full_project_chain_includes_testing(self):
        from backend.app.agents.supervisor import get_agent_chain
        chain = get_agent_chain("full_project")
        assert "project_analyzer" in chain
        assert "technology_advisor" in chain
        assert "architecture" in chain
        assert "roadmap" in chain
        assert "coding" in chain
        assert "documentation" in chain
        assert "testing" in chain
        assert len(chain) == 7

    def test_full_hackathon_chain_includes_pitch(self):
        from backend.app.agents.supervisor import get_agent_chain
        chain = get_agent_chain("full_hackathon")
        assert "pitch" in chain
        assert "mvp_planning" in chain
        assert len(chain) == 7

    def test_approval_required_agents(self):
        from backend.app.agents.supervisor import requires_approval
        assert requires_approval("architecture") is True
        assert requires_approval("roadmap") is True
        assert requires_approval("project_analyzer") is False
        assert requires_approval("pitch") is False

    def test_unknown_workflow_defaults_to_project(self):
        from backend.app.agents.supervisor import get_agent_chain
        chain = get_agent_chain("unknown_type")
        assert "project_analyzer" in chain


class TestAgentState:
    """Test that AgentWorkflowState TypedDict is correctly structured."""

    def test_state_accepts_all_fields(self):
        from backend.app.agents.state import AgentWorkflowState
        state: AgentWorkflowState = {
            "session_id": "test-123",
            "workflow_type": "project",
            "user_input": {"project_title": "Test"},
            "project_analysis": None,
            "hackathon_analysis": None,
            "generated_ideas": None,
            "technology_stack": None,
            "architecture": None,
            "roadmap": None,
            "coding_prompts": None,
            "documentation": None,
            "test_plan": None,
            "pitch": None,
            "completed_agents": [],
            "pending_approval": False,
            "approval_target": None,
            "error": None,
            "current_agent": None,
        }
        assert state["session_id"] == "test-123"
        assert state["workflow_type"] == "project"
        assert state["completed_agents"] == []


class TestResultsStructure:
    """Verify that the response payload contains all expected result keys."""

    def test_project_results_contain_all_keys(self, client):
        """Full project workflow response contains all 7 result sections."""
        with patch("backend.app.api.routes.agent_orchestration.run_workflow",
                   new=AsyncMock(return_value=_full_project_state())), \
             patch("backend.app.config.Settings.is_anthropic_configured", True):
            res = client.post("/api/agent/run", json={
                "workflow_type": "full_project",
                "user_input": PROJECT_INPUT,
            })
        data = res.json()
        results = data["results"]
        assert "project_analysis" in results
        assert "technology_stack" in results
        assert "architecture" in results
        assert "roadmap" in results
        assert "coding_prompts" in results
        assert "documentation" in results
        assert "test_plan" in results
        # Verify nested content
        assert results["project_analysis"]["problem_statement"] is not None
        assert len(results["technology_stack"]["technologies"]) >= 1
        assert "mermaid_diagram" in results["architecture"]
        assert len(results["roadmap"]["phases"]) >= 2
        assert len(results["test_plan"]["unit_tests"]) >= 1

    def test_hackathon_results_contain_pitch(self, client):
        """Hackathon workflow response contains pitch and ideas."""
        with patch("backend.app.api.routes.agent_orchestration.run_workflow",
                   new=AsyncMock(return_value=_hackathon_state())), \
             patch("backend.app.config.Settings.is_anthropic_configured", True):
            res = client.post("/api/agent/run", json={
                "workflow_type": "hackathon",
                "user_input": HACKATHON_INPUT,
            })
        data = res.json()
        results = data["results"]
        assert "hackathon_analysis" in results
        assert "generated_ideas" in results
        assert "pitch" in results
        assert len(results["pitch"]["pitch_30_seconds"]) > 10


class TestStateGraphEngine:
    """Test the in-tree LangGraph-compatible StateGraph execution."""

    @pytest.mark.asyncio
    async def test_linear_graph_execution(self):
        from backend.app.agents.graph import StateGraph, END

        async def step_a(state):
            state["step_a"] = True
            return state

        async def step_b(state):
            state["step_b"] = True
            return state

        graph = StateGraph()
        graph.add_node("a", step_a)
        graph.add_node("b", step_b)
        graph.set_entry_point("a")
        graph.add_edge("a", "b")
        graph.add_edge("b", END)

        app = graph.compile()
        result = await app.ainvoke({"input": "test"})
        assert result.get("step_a") is True
        assert result.get("step_b") is True

    @pytest.mark.asyncio
    async def test_conditional_edges(self):
        from backend.app.agents.graph import StateGraph, END

        async def router_node(state):
            return state

        def decide_path(state):
            return "high" if state.get("priority") > 5 else "low"

        async def high_node(state):
            state["route"] = "high_priority"
            return state

        async def low_node(state):
            state["route"] = "low_priority"
            return state

        graph = StateGraph()
        graph.add_node("router", router_node)
        graph.add_node("high", high_node)
        graph.add_node("low", low_node)
        graph.set_entry_point("router")
        graph.add_conditional_edges("router", decide_path, {"high": "high", "low": "low"})
        graph.add_edge("high", END)
        graph.add_edge("low", END)

        app = graph.compile()
        high_res = await app.ainvoke({"priority": 9})
        assert high_res["route"] == "high_priority"

        low_res = await app.ainvoke({"priority": 2})
        assert low_res["route"] == "low_priority"

    @pytest.mark.asyncio
    async def test_pause_on_pending_approval(self):
        from backend.app.agents.graph import StateGraph, END

        async def step_1(state):
            state["step_1"] = "done"
            state["pending_approval"] = True
            return state

        async def step_2(state):
            state["step_2"] = "done"
            return state

        graph = StateGraph()
        graph.add_node("s1", step_1)
        graph.add_node("s2", step_2)
        graph.set_entry_point("s1")
        graph.add_edge("s1", "s2")
        graph.add_edge("s2", END)

        app = graph.compile()
        res = await app.ainvoke({"pending_approval": False})
        assert res.get("step_1") == "done"
        assert "step_2" not in res  # Paused because pending_approval became True


class TestIndividualAgents:
    """Verify each of the 14 agents independently."""

    @pytest.mark.asyncio
    async def test_testing_agent(self):
        from backend.app.agents.testing_agent import testing_agent
        state = {
            "user_input": PROJECT_INPUT,
            "project_analysis": MOCK_ANALYSIS,
            "technology_stack": MOCK_TECH_STACK,
            "completed_agents": [],
        }
        with patch("backend.app.services.claude_service.AsyncAnthropic") as mock_anthropic, \
             patch("backend.app.config.Settings.is_anthropic_configured", True):
            mock_anthropic.return_value.messages.create = AsyncMock(
                return_value=_make_mock_block(MOCK_TEST_PLAN)
            )
            res = await testing_agent(state)
        assert res.get("error") is None
        assert "testing" in res["completed_agents"]
        assert "test_plan" in res
        assert len(res["test_plan"]["unit_tests"]) >= 1

    @pytest.mark.asyncio
    async def test_idea_evaluation_agent(self):
        from backend.app.agents.idea_evaluation_agent import idea_evaluation_agent
        from backend.app.schemas.hackathon_guidance import IdeaEvaluationResponse
        mock_eval = {
            "scoring_method": "Default Matrix",
            "ranked_ideas": [{
                "idea_id": 1,
                "project_title": "Idea 1",
                "problem_relevance": 9.0,
                "innovation": 9.0,
                "technical_feasibility": 9.0,
                "social_business_impact": 9.0,
                "demo_potential": 9.0,
                "time_feasibility": 9.0,
                "weighted_total_score": 9.0,
                "strengths": ["High accuracy"],
                "risks_and_pitfalls": ["Dataset bias"]
            }],
            "recommended_idea_id": 1,
            "recommended_idea_title": "Idea 1",
            "recommendation_rationale": "High impact",
            "disclaimer": "No win is guaranteed."
        }
        state = {"user_input": HACKATHON_INPUT, "completed_agents": []}
        with patch.object(
            __import__("backend.app.services.hackathon_service", fromlist=["HackathonService"]).HackathonService,
            "evaluate_ideas",
            new=AsyncMock(return_value=IdeaEvaluationResponse(**mock_eval))
        ):
            res = await idea_evaluation_agent(state)
        assert res.get("error") is None
        assert "idea_evaluation" in res["completed_agents"]
        assert res["idea_evaluation"]["recommended_idea_title"] == "Idea 1"

    @pytest.mark.asyncio
    async def test_mvp_planning_agent(self):
        from backend.app.agents.mvp_planning_agent import mvp_planning_agent
        from backend.app.schemas.hackathon_guidance import MVPPlanResponse
        mock_mvp = {
            "project_title": "Road Hazard AI",
            "core_mvp_summary": "Minimal working hazard detector",
            "must_have_features": ["Video stream"],
            "should_have_features": ["Export report"],
            "nice_to_have_features": ["Hardware radar"],
            "minimal_demo_flow": ["Upload video", "View bounding box"],
            "potential_failure_points": ["Backup MP4 demo ready"]
        }
        state = {"user_input": HACKATHON_INPUT, "completed_agents": []}
        with patch.object(
            __import__("backend.app.services.hackathon_service", fromlist=["HackathonService"]).HackathonService,
            "plan_mvp",
            new=AsyncMock(return_value=MVPPlanResponse(**mock_mvp))
        ):
            res = await mvp_planning_agent(state)
        assert res.get("error") is None
        assert "mvp_planning" in res["completed_agents"]
        assert len(res["mvp_plan"]["must_have_features"]) >= 1

    @pytest.mark.asyncio
    async def test_team_allocation_agent(self):
        from backend.app.agents.team_allocation_agent import team_allocation_agent
        from backend.app.schemas.hackathon_guidance import TeamAllocationResponse
        mock_team = {
            "project_title": "Road Hazard AI",
            "team_size": 3,
            "member_assignments": [
                {
                    "member_identifier": "Member 1 (AI Lead)",
                    "assigned_role": "AI Lead",
                    "key_responsibilities": ["Train YOLO model", "FastAPI endpoint"],
                    "specific_tasks": ["Setup weights", "Build route"],
                    "expected_deliverables": ["Working inference API"]
                }
            ],
            "coordination_practices": ["Hourly standups", "Git branches"]
        }
        state = {"user_input": HACKATHON_INPUT, "completed_agents": []}
        with patch.object(
            __import__("backend.app.services.hackathon_service", fromlist=["HackathonService"]).HackathonService,
            "allocate_team",
            new=AsyncMock(return_value=TeamAllocationResponse(**mock_team))
        ):
            res = await team_allocation_agent(state)
        assert res.get("error") is None
        assert "team_allocation" in res["completed_agents"]
        assert res["team_allocation"]["team_size"] == 3

    @pytest.mark.asyncio
    async def test_dev_guidance_agent(self):
        from backend.app.agents.dev_guidance_agent import dev_guidance_agent
        from backend.app.schemas.hackathon_guidance import HackathonDevGuidanceResponse
        mock_dev = {
            "project_title": "AgriScan",
            "recommended_tech_stack": [
                {
                    "tech_name": "FastAPI",
                    "category": "Backend",
                    "license_type": "Open-Source",
                    "why_recommended": "Fast async inference",
                    "free_tier_limits": "100% Free",
                    "free_alternative": "Flask"
                }
            ],
            "database_design_summary": "SQLite schema",
            "suggested_api_endpoints": ["POST /diagnose"],
            "integration_quickstart_guide": ["Run backend"],
            "copy_ready_claude_prompt": "Scaffold FastAPI route",
            "copy_ready_antigravity_prompt": "Scaffold React frontend",
            "testing_and_sanity_checks": ["Run pytest"],
            "deployment_plan": "Vercel + Render"
        }
        state = {"user_input": HACKATHON_INPUT, "completed_agents": []}
        with patch.object(
            __import__("backend.app.services.hackathon_service", fromlist=["HackathonService"]).HackathonService,
            "generate_dev_guidance",
            new=AsyncMock(return_value=HackathonDevGuidanceResponse(**mock_dev))
        ):
            res = await dev_guidance_agent(state)
        assert res.get("error") is None
        assert "dev_guidance" in res["completed_agents"]
        assert len(res["dev_guidance"]["recommended_tech_stack"]) >= 1
