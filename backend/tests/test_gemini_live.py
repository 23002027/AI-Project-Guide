"""
Live Integration Tests for Google Gemini AI Provider and LangGraph Agents.
Uses the user's configured GEMINI_API_KEY from backend/.env.
Never exposes or logs the API key.
"""

import pytest
import os
from backend.app.config import get_settings

settings = get_settings()
pytestmark = pytest.mark.skipif(
    not settings.is_gemini_configured,
    reason="Google Gemini cloud API key not configured; active provider is local Ollama"
)
from backend.app.services.gemini_service import GeminiService
from backend.app.services.project_analyzer import ProjectAnalyzerService
from backend.app.services.hackathon_service import HackathonService
from backend.app.schemas.project_guidance import ProjectIdeaInput, ProjectDomain, ExperienceLevel
from backend.app.schemas.hackathon_guidance import HackathonInput
from backend.app.agents.orchestrator import run_workflow


@pytest.mark.asyncio
async def test_real_gemini_api_request():
    """Verify live Gemini API connectivity using the official google-genai SDK."""
    settings = get_settings()
    assert settings.is_gemini_configured, "Gemini API key must be configured in backend/.env"

    service = GeminiService()
    client = service.get_client()

    response = await client.aio.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents="Respond with 'GEMINI_CONNECTED' in plain text.",
    )
    assert response.text is not None
    assert len(response.text.strip()) > 0
    assert "GEMINI" in response.text.upper() or "CONNECTED" in response.text.upper() or len(response.text.strip()) > 0


@pytest.mark.asyncio
async def test_project_guidance_real_output():
    """Test Project Guidance analysis using real Gemini request."""
    service = ProjectAnalyzerService()

    idea = ProjectIdeaInput(
        title="Smart Campus Electric Vehicle Shuttle Tracker",
        domain=ProjectDomain.IOT_EMBEDDED,
        description="A real-time GPS tracking and passenger capacity predictor for university EV campus shuttles.",
        skills=["Python", "FastAPI", "React", "MQTT"],
        experience_level=ExperienceLevel.INTERMEDIATE,
        budget="Free Tier",
        deadline="2 months",
        is_team=True,
        team_size=3
    )

    analysis = await service.analyze_project(idea)

    assert analysis.project_title is not None
    assert len(analysis.problem_statement) > 20
    assert len(analysis.target_users) >= 1
    assert len(analysis.main_objectives) >= 1
    assert len(analysis.expected_outcomes) >= 1
    assert analysis.project_complexity in ["Moderate", "High", "Advanced", "Low", "Simple"]


@pytest.mark.asyncio
async def test_hackathon_guidance_real_output():
    """Test Hackathon Guidance problem analysis using real Gemini request."""
    service = HackathonService()

    hack_input = HackathonInput(
        hackathon_name="CleanTech Hack 2026",
        problem_statement="Reduce food waste in university dining halls by dynamically matching surplus meals to food pantries.",
        duration="24 hours",
        team_size=4,
        team_skills=["Python", "React Native", "Tailwind"],
        experience_level="intermediate"
    )

    analysis = await service.analyze_problem(hack_input)

    assert analysis.hackathon_name == "CleanTech Hack 2026"
    assert len(analysis.problem_summary) > 20
    assert len(analysis.core_requirements) >= 1
    assert len(analysis.target_users) >= 1


@pytest.mark.asyncio
async def test_agent_orchestrator_project_workflow():
    """Test LangGraph orchestrator executing project agents with Gemini."""
    user_input = {
        "title": "Automated Medical Lab Report Summarizer",
        "description": "Extracts key biomarkers from lab test PDFs and generates plain-English summaries for patients.",
        "domain": "Healthcare",
        "skills": ["Python", "FastAPI", "React"],
        "experience_level": "intermediate",
        "budget": "Free",
        "deadline": "3 months",
        "is_team": True,
        "team_size": 2,
    }

    final_state = await run_workflow(
        workflow_type="project",
        user_input=user_input
    )

    assert final_state["session_id"] is not None
    assert "project_analyzer" in final_state.get("completed_agents", [])
    assert final_state.get("project_analysis") is not None
    assert "problem_statement" in final_state["project_analysis"]
