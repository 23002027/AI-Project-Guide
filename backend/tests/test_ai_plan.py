"""
Automated tests for AI Planning endpoint and Claude Service.
Uses mocked Anthropic SDK responses to avoid live API calls and costs.
"""

import json
from unittest.mock import AsyncMock, patch, MagicMock
import pytest
from fastapi.testclient import TestClient
from anthropic import APIConnectionError

from backend.app.main import app
from backend.app.services.claude_service import ClaudeService, InvalidAIResponseError

client = TestClient(app)

MOCK_PROJECT_PLAN_JSON = {
    "project_title": "AI Automated Code Reviewer & Mentor",
    "mode": "project",
    "problem_analysis": "Computer science students submit code assignments without immediate feedback, creating a bottleneck for professors and slowing learning cycles.",
    "recommended_solution": "A multi-agent automated review system providing instant syntax, security, and algorithmic complexity feedback with guided hints.",
    "technology_stack": [
        {
            "name": "FastAPI",
            "category": "Backend",
            "reason": "High-performance asynchronous REST API framework ideal for agent workflows.",
            "alternatives": ["Django Ninja", "Express.js"]
        },
        {
            "name": "PostgreSQL",
            "category": "Database",
            "reason": "ACID-compliant relational database with pgvector support for semantic code embeddings.",
            "alternatives": ["MySQL", "MongoDB"]
        }
    ],
    "ai_tools": [
        {
            "tool_name": "Claude 3.5 Sonnet",
            "recommended_for": "AST analysis and code explanation generation",
            "purpose": "Powers the core pedagogical feedback agent."
        }
    ],
    "architecture": {
        "overview": "Microservice-ready modular architecture with an async job queue.",
        "frontend_layer": "Next.js 14 dashboard with Monaco Editor for live code editing.",
        "backend_layer": "FastAPI async endpoints coordinating review agents.",
        "data_layer": "PostgreSQL relational schema storing assignments, reviews, and metrics.",
        "ai_agent_layer": "LangGraph state machine routing code through linting, security, and explanation agents.",
        "mermaid_diagram": "flowchart TD\n    Student[Student Client] --> UI[Next.js App]\n    UI --> API[FastAPI Gateway]\n    API --> DB[(PostgreSQL)]"
    },
    "roadmap": [
        {
            "phase_number": 1,
            "phase_name": "Phase 1: Project Setup & Schemas",
            "estimated_duration": "Week 1",
            "goals": ["Establish repo structure", "Define database schemas"],
            "action_items": ["Initialize FastAPI", "Configure PostgreSQL connection"]
        }
    ],
    "estimated_completion_time": "3 months",
    "hackathon_guidance": None
}

MOCK_HACKATHON_PLAN_JSON = {
    "project_title": "QuickPulse: AI Disaster Dispatcher",
    "mode": "hackathon",
    "problem_analysis": "During emergencies, 911 dispatch lines are flooded with repetitive calls, delaying urgent triage.",
    "recommended_solution": "An AI emergency triage assistant that clusters caller reports and geo-tags priority rescues in real time.",
    "technology_stack": [
        {
            "name": "FastAPI",
            "category": "Backend",
            "reason": "Fastest setup for real-time WebSocket and REST endpoints.",
            "alternatives": ["Node.js"]
        }
    ],
    "ai_tools": [
        {
            "tool_name": "Claude 3.5 Sonnet",
            "recommended_for": "Caller transcription & priority categorization",
            "purpose": "Classifies emergency severity into Red, Yellow, Green triage buckets."
        }
    ],
    "architecture": {
        "overview": "Lightweight event-driven MVP designed for rapid 24-hour deployment.",
        "frontend_layer": "React dashboard with interactive Leaflet emergency heat map.",
        "backend_layer": "FastAPI receiving simulated emergency reports via REST.",
        "data_layer": "SQLite in-memory for zero-latency competition demo setup.",
        "ai_agent_layer": "Single orchestrator agent scoring urgency in under 2 seconds.",
        "mermaid_diagram": "flowchart LR\n    Caller --> Ingest[FastAPI Ingestion]\n    Ingest --> Agent[Triage Agent]\n    Agent --> Map[Dispatcher Map]"
    },
    "roadmap": [
        {
            "phase_number": 1,
            "phase_name": "Sprint 1: Core Ingestion & Triage Agent",
            "estimated_duration": "Hours 0-8",
            "goals": ["Working ingestion endpoint", "Claude prompt scoring emergency severity"],
            "action_items": ["Set up FastAPI", "Prompt test on sample emergency transcripts"]
        }
    ],
    "estimated_completion_time": "24 hours",
    "hackathon_guidance": {
        "mvp_core_features": [
            "Real-time emergency report submission form",
            "AI urgency classification (Immediate, Urgent, Standard)",
            "Live dispatcher map showing emergency clusters"
        ],
        "cut_features": [
            "SMS gateway integration (simulate via web UI)",
            "Multi-language voice synthesis (defer to post-hackathon)",
            "Complex authentication (use role selector dropdown for demo)"
        ],
        "judging_alignment": [
            {
                "criterion": "Innovation",
                "score_potential": "High",
                "how_to_maximize": "Show automated deduplication of 50 simultaneous callers into 1 incident cluster."
            },
            {
                "criterion": "Technical Depth",
                "score_potential": "High",
                "how_to_maximize": "Demonstrate sub-second structured JSON triage responses."
            }
        ],
        "team_allocation": [
            {
                "role": "Team Lead & AI Specialist",
                "responsibilities": ["Claude prompt engineering", "Triage scoring pipeline"],
                "hours_breakdown": "Hours 0-16: Dev, Hours 17-24: Testing & Pitch Prep"
            },
            {
                "role": "Frontend & Demo Lead",
                "responsibilities": ["React dashboard", "Map visualization", "Slide Deck"],
                "hours_breakdown": "Hours 0-14: UI Dev, Hours 15-24: Polish & Pitch Deck"
            }
        ],
        "live_demo_script": [
            "0:00 - 0:30: State problem: 300 callers flood a 911 dispatch center during a flash flood.",
            "0:30 - 1:30: Trigger 10 simulated emergency reports; watch AI cluster them on map into 1 incident.",
            "1:30 - 2:00: Show response time savings and conclude with tech stack slide."
        ],
        "pitch_hook": "When seconds count, emergency lines shouldn't be busy. QuickPulse triages disasters before humans can pick up the phone.",
        "risk_mitigation": [
            "Pre-cache 5 demo incidents in local storage in case network drops during the presentation.",
            "Screen-record a 60-second backup video showing full functionality."
        ]
    }
}


def create_mock_claude_response(text_content: str):
    """Helper to mock an Anthropic messages.create response."""
    mock_block = MagicMock()
    mock_block.type = "text"
    mock_block.text = text_content

    mock_response = MagicMock()
    mock_response.content = [mock_block]
    return mock_response


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_ai_plan_project_mode_success():
    """Verify POST /api/ai/plan returns a valid project plan when mocked."""
    mock_response = create_mock_claude_response(json.dumps(MOCK_PROJECT_PLAN_JSON))

    with patch("backend.app.services.claude_service.AsyncAnthropic") as mock_anthropic_cls:
        mock_instance = mock_anthropic_cls.return_value
        mock_instance.messages.create = AsyncMock(return_value=mock_response)

        with patch("backend.app.config.Settings.is_anthropic_configured", True):
            payload = {
                "mode": "project",
                "idea": "An AI-powered automated grading and feedback assistant for university programming assignments.",
                "skill_level": "intermediate",
                "available_time": "3 months",
                "team_size": 2,
                "budget": "Free / Open Source tier",
                "preferred_tech": ["FastAPI", "Next.js"]
            }

            response = client.post("/api/ai/plan", json=payload)
            assert response.status_code == 200
            data = response.json()

            assert data["project_title"] == "AI Automated Code Reviewer & Mentor"
            assert data["mode"] == "project"
            assert len(data["technology_stack"]) >= 1
            assert len(data["ai_tools"]) >= 1
            assert "mermaid_diagram" in data["architecture"]
            assert len(data["roadmap"]) >= 1
            assert data["hackathon_guidance"] is None
            assert "model_used" in data["metadata"]


@pytest.mark.asyncio
async def test_create_ai_plan_hackathon_mode_success():
    """Verify POST /api/ai/plan includes hackathon guidance when mode='hackathon'."""
    # Test with markdown code-fenced JSON to ensure extractor handles ```json ... ```
    raw_markdown = f"```json\n{json.dumps(MOCK_HACKATHON_PLAN_JSON)}\n```"
    mock_response = create_mock_claude_response(raw_markdown)

    with patch("backend.app.services.claude_service.AsyncAnthropic") as mock_anthropic_cls:
        mock_instance = mock_anthropic_cls.return_value
        mock_instance.messages.create = AsyncMock(return_value=mock_response)

        with patch("backend.app.config.Settings.is_anthropic_configured", True):
            payload = {
                "mode": "hackathon",
                "idea": "A real-time emergency 911 dispatch triage assistant for natural disaster response.",
                "skill_level": "intermediate",
                "available_time": "24 hours",
                "team_size": 3
            }

            response = client.post("/api/ai/plan", json=payload)
            assert response.status_code == 200
            data = response.json()

            assert data["mode"] == "hackathon"
            assert data["hackathon_guidance"] is not None
            hg = data["hackathon_guidance"]
            assert len(hg["mvp_core_features"]) >= 1
            assert len(hg["cut_features"]) >= 1
            assert len(hg["judging_alignment"]) >= 1
            assert len(hg["team_allocation"]) >= 1
            assert len(hg["live_demo_script"]) >= 1
            assert hg["pitch_hook"] != ""
            assert len(hg["risk_mitigation"]) >= 1


def test_create_ai_plan_unconfigured_api_key():
    """Verify endpoint returns HTTP 503 when the API key is not configured."""
    with patch("backend.app.config.Settings.is_anthropic_configured", False):
        payload = {
            "mode": "project",
            "idea": "A college campus event recommendation and student engagement platform.",
            "available_time": "1 month"
        }
        response = client.post("/api/ai/plan", json=payload)
        assert response.status_code == 503
        data = response.json()
        assert data["detail"]["error"] == "ai_service_unconfigured"


def test_create_ai_plan_input_validation():
    """Verify Pydantic input validation blocks malformed requests with HTTP 422."""
    # 1. Idea too short (< 10 chars)
    res1 = client.post("/api/ai/plan", json={"mode": "project", "idea": "short"})
    assert res1.status_code == 422

    # 2. Invalid mode
    res2 = client.post("/api/ai/plan", json={"mode": "invalid_mode", "idea": "Valid length project idea text."})
    assert res2.status_code == 422

    # 3. Invalid team size (<= 0)
    res3 = client.post("/api/ai/plan", json={"idea": "Valid length project idea text.", "team_size": 0})
    assert res3.status_code == 422


@pytest.mark.asyncio
async def test_create_ai_plan_api_connection_error():
    """Verify endpoint returns HTTP 502 when Anthropic connection fails."""
    with patch("backend.app.services.claude_service.AsyncAnthropic") as mock_anthropic_cls:
        mock_instance = mock_anthropic_cls.return_value
        mock_instance.messages.create = AsyncMock(
            side_effect=APIConnectionError(request=MagicMock(), message="Connection refused by remote host")
        )

        with patch("backend.app.config.Settings.is_anthropic_configured", True):
            payload = {
                "mode": "project",
                "idea": "An AI platform for autonomous code debugging.",
                "available_time": "1 month"
            }
            response = client.post("/api/ai/plan", json=payload)
            assert response.status_code == 502
            data = response.json()
            assert data["detail"]["error"] == "anthropic_api_error"


def test_claude_service_json_extraction():
    """Verify the JSON extractor parses various raw and code-fenced inputs."""
    service = ClaudeService()

    # Plain JSON string
    res1 = service._extract_json('{"key": "value"}')
    assert res1 == {"key": "value"}

    # Markdown wrapped ```json ... ```
    res2 = service._extract_json('```json\n{"status": "ok"}\n```')
    assert res2 == {"status": "ok"}

    # Invalid text raises InvalidAIResponseError
    with pytest.raises(InvalidAIResponseError):
        service._extract_json("Not a json string at all")
