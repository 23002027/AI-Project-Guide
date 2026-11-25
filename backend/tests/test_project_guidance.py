"""
Automated unit & integration tests for Full Project Guidance Mode (Phase 3).
Tests all 7 endpoints using mocked Claude responses to ensure zero API cost.
"""

import json
from unittest.mock import AsyncMock, patch, MagicMock
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

# ---------------------------------------------------------------------------
# Mock Response Payloads
# ---------------------------------------------------------------------------

MOCK_ANALYSIS_DATA = {
    "project_title": "AgriVision: Crop Disease Detection",
    "domain": "AI / Machine Learning",
    "problem_statement": "Smallholder farmers experience 30% yield loss due to delayed diagnosis of leaf blight.",
    "existing_limitations": ["Visual inspection requires agronomists who are unavailable in remote areas."],
    "proposed_solution": "A computer vision mobile system providing real-time crop disease classification and remedy advice.",
    "target_users": ["Smallholder farmers", "Agricultural extension officers"],
    "main_objectives": ["Train a lightweight MobileNetV3 model with >90% precision", "Build an offline-first PWA"],
    "expected_outcomes": ["Functional mobile interface", "Evaluated inference latency under 500ms on edge device"],
    "unique_selling_proposition": "Combines offline edge inference with regional language audio guidance.",
    "innovation_opportunities": ["Federated learning across regional farming clusters to improve model robustness."],
    "feasibility_assessment": "Highly viable within 3 months using transfer learning on public PlantVillage datasets.",
    "project_complexity": "Moderate",
    "follow_up_questions": []
}

MOCK_TECH_STACK_DATA = {
    "project_title": "AgriVision: Crop Disease Detection",
    "technology_recommendations": [
        {
            "technology_name": "FastAPI",
            "category": "Backend Framework",
            "why_suitable": "High throughput, lightweight, native async Python support for model serving",
            "role_in_project": "API Gateway serving model inference endpoints",
            "implementation_guide": "Install fastapi, expose POST /predict with UploadFile payload",
            "cost_tier": "100% Free / Open Source",
            "alternatives": ["Flask"]
        }
    ],
    "ai_tool_advisors": [
        {
            "tool_name": "Claude 3.5 Sonnet",
            "development_activity": "Model Evaluation & Remedial Advice Generation",
            "how_to_use": "Generate treatment plans based on identified disease classes",
            "when_to_use": "Phase 5 (AI Integration)",
            "free_alternative": "Hugging Face Inference API"
        }
    ],
    "rationale_summary": "Optimized for low-bandwidth mobile execution and rapid API prototyping."
}

MOCK_ARCHITECTURE_DATA = {
    "project_title": "AgriVision: Crop Disease Detection",
    "high_level_overview": "Client-Server Edge Hybrid Architecture with TensorFlow Lite client and FastAPI server.",
    "frontend_backend_flow": "Mobile client captures leaf image, runs local inference; if confidence < 80%, uploads to FastAPI.",
    "database_architecture": "PostgreSQL schema storing user submissions, telemetry, and verified disease records.",
    "module_breakdown": [
        {
            "module_name": "Inference Engine",
            "responsibility": "Classifies plant diseases from leaf imagery",
            "technologies_used": ["TensorFlow Lite", "OpenCV"],
            "inputs": "224x224 RGB image",
            "outputs": "Disease label and confidence score"
        }
    ],
    "api_endpoint_suggestions": [
        {
            "method": "POST",
            "path": "/api/v1/diagnose",
            "description": "Upload image file and receive disease classification"
        }
    ],
    "data_flow_explanation": "Images pass from phone camera -> client preprocessing -> inference -> persistent audit log.",
    "mermaid_diagram": "flowchart TD\n    Farmer[\"Farmer (Mobile Client)\"] -->|Upload Image| API[\"FastAPI Server\"]\n    API --> Model[\"PyTorch/TF Model\"]\n    API --> DB[(\"PostgreSQL\")]"
}

MOCK_ROADMAP_DATA = {
    "project_title": "AgriVision: Crop Disease Detection",
    "total_estimated_duration": "3 months",
    "phases": [
        {
            "phase_number": 1,
            "phase_title": "Phase 1: Research and Requirements",
            "estimated_duration": "Weeks 1-2",
            "tasks": ["Dataset collection and validation", "Literature survey on CNN architectures"],
            "dependencies": ["None"],
            "required_tools": ["Kaggle", "PlantVillage Dataset"],
            "expected_output": "Approved dataset split and SRS document",
            "completion_checklist": ["Dataset downloaded", "Baseline model researched"]
        }
    ],
    "deployment_and_testing": {
        "hosting_platform": "Render Free Tier (API) + Vercel (Web)",
        "environment_variables_checklist": ["DATABASE_URL", "MODEL_PATH"],
        "step_by_step_deployment": ["Containerize with Dockerfile", "Deploy on Render"],
        "testing_strategy": ["Unit tests on image preprocessing", "Model accuracy verification"],
        "maintenance_practices": ["Monitor drift on field samples"]
    }
}

MOCK_CODING_PROMPTS_DATA = {
    "project_title": "AgriVision: Crop Disease Detection",
    "module_walkthroughs": [
        {
            "module_name": "Prediction Router",
            "purpose": "Receives image, validates format, triggers model inference",
            "folder_structure": "backend/app/api/routes/predict.py",
            "implementation_steps": ["Read image bytes", "Call inference service", "Return diagnosis JSON"],
            "example_code_snippet": "@router.post('/diagnose')\nasync def diagnose(file: UploadFile): ...",
            "required_dependencies": ["fastapi", "pillow", "numpy"],
            "testing_instructions": "Send sample image via TestClient",
            "common_errors_and_solutions": ["Error: Corrupt image -> Fix: Add PIL.Image.verify() check"]
        }
    ],
    "copy_ready_prompts": [
        {
            "target_tool": "Claude 3.5 Sonnet",
            "use_case": "Model Serving Pipeline",
            "prompt_text": "Write a clean FastAPI service class to load a TensorFlow Lite model and run async inference..."
        }
    ]
}

MOCK_DOCUMENTATION_DATA = {
    "project_title": "AgriVision: Crop Disease Detection",
    "abstract": "Agricultural crop disease represents a critical bottleneck for food security...",
    "introduction": "Agriculture contributes over 18% of global GDP in developing nations...",
    "problem_statement": "The lack of accessible, timely phytopathological expertise leaves rural farmers vulnerable...",
    "literature_review_outline": [
        "Traditional hand-crafted visual feature extraction methods",
        "Deep convolutional neural networks for leaf lesion classification",
        "Edge inference trade-offs between quantized models and cloud APIs"
    ],
    "objectives": [
        "To train a deep CNN capable of identifying 10 major crop diseases",
        "To develop an accessible cross-platform mobile client"
    ],
    "methodology": "Transfer learning using MobileNetV3 fine-tuned on the PlantVillage dataset...",
    "proposed_architecture_summary": "Two-tier client-server architecture with on-device caching...",
    "implementation_plan_summary": "Divided into data preparation, model optimization, API construction, and field evaluation...",
    "testing_methodology": "10-fold cross validation, inference latency profiling, and user acceptance testing with 20 farmers...",
    "results_section_template": "Evaluation table comparing Precision, Recall, F1-Score, Model Size (MB), and Latency (ms)...",
    "conclusion": "AgriVision provides a scalable, low-cost technological intervention for early crop disease detection...",
    "future_scope": [
        "Integration with IoT soil sensors",
        "Multilingual voice interface in 5 regional dialects"
    ]
}


def create_mock_block(payload_dict: dict):
    """Helper creating a mocked Anthropic text block."""
    mock_block = MagicMock()
    mock_block.type = "text"
    mock_block.text = json.dumps(payload_dict)
    mock_response = MagicMock()
    mock_response.content = [mock_block]
    return mock_response


SAMPLE_REQUEST_PAYLOAD = {
    "title": "AgriVision: Crop Disease Detection",
    "description": "An AI platform for automated plant leaf disease diagnosis and treatment planning.",
    "domain": "AI / Machine Learning",
    "skills": ["Python", "FastAPI", "React"],
    "experience_level": "Intermediate (3rd/4th Year B.Tech Student)",
    "budget": "Free / Open Source tier",
    "deadline": "3 months",
    "is_team": True,
    "team_size": 3
}


# ---------------------------------------------------------------------------
# Endpoint Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_analyze_project_endpoint():
    """Verify POST /api/project/analyze."""
    with patch("backend.app.services.claude_service.AsyncAnthropic") as mock_anthropic:
        mock_instance = mock_anthropic.return_value
        mock_instance.messages.create = AsyncMock(return_value=create_mock_block(MOCK_ANALYSIS_DATA))

        with patch("backend.app.config.Settings.is_anthropic_configured", True):
            res = client.post("/api/project/analyze", json=SAMPLE_REQUEST_PAYLOAD)
            assert res.status_code == 200
            data = res.json()
            assert data["project_title"] == "AgriVision: Crop Disease Detection"
            assert "problem_statement" in data
            assert len(data["existing_limitations"]) >= 1
            assert len(data["target_users"]) >= 1
            assert len(data["main_objectives"]) >= 1


@pytest.mark.asyncio
async def test_technology_stack_endpoint():
    """Verify POST /api/project/technology-stack."""
    with patch("backend.app.services.claude_service.AsyncAnthropic") as mock_anthropic:
        mock_instance = mock_anthropic.return_value
        mock_instance.messages.create = AsyncMock(return_value=create_mock_block(MOCK_TECH_STACK_DATA))

        with patch("backend.app.config.Settings.is_anthropic_configured", True):
            res = client.post("/api/project/technology-stack", json=SAMPLE_REQUEST_PAYLOAD)
            assert res.status_code == 200
            data = res.json()
            assert len(data["technology_recommendations"]) >= 1
            assert len(data["ai_tool_advisors"]) >= 1
            assert "rationale_summary" in data


@pytest.mark.asyncio
async def test_architecture_endpoint():
    """Verify POST /api/project/architecture."""
    with patch("backend.app.services.claude_service.AsyncAnthropic") as mock_anthropic:
        mock_instance = mock_anthropic.return_value
        mock_instance.messages.create = AsyncMock(return_value=create_mock_block(MOCK_ARCHITECTURE_DATA))

        with patch("backend.app.config.Settings.is_anthropic_configured", True):
            res = client.post("/api/project/architecture", json=SAMPLE_REQUEST_PAYLOAD)
            assert res.status_code == 200
            data = res.json()
            assert "high_level_overview" in data
            assert len(data["module_breakdown"]) >= 1
            assert "mermaid_diagram" in data
            assert len(data["api_endpoint_suggestions"]) >= 1


@pytest.mark.asyncio
async def test_roadmap_endpoint():
    """Verify POST /api/project/roadmap."""
    with patch("backend.app.services.claude_service.AsyncAnthropic") as mock_anthropic:
        mock_instance = mock_anthropic.return_value
        mock_instance.messages.create = AsyncMock(return_value=create_mock_block(MOCK_ROADMAP_DATA))

        with patch("backend.app.config.Settings.is_anthropic_configured", True):
            res = client.post("/api/project/roadmap", json=SAMPLE_REQUEST_PAYLOAD)
            assert res.status_code == 200
            data = res.json()
            assert len(data["phases"]) >= 1
            assert "deployment_and_testing" in data
            assert "hosting_platform" in data["deployment_and_testing"]


@pytest.mark.asyncio
async def test_coding_prompts_endpoint():
    """Verify POST /api/project/coding-prompts."""
    with patch("backend.app.services.claude_service.AsyncAnthropic") as mock_anthropic:
        mock_instance = mock_anthropic.return_value
        mock_instance.messages.create = AsyncMock(return_value=create_mock_block(MOCK_CODING_PROMPTS_DATA))

        with patch("backend.app.config.Settings.is_anthropic_configured", True):
            res = client.post("/api/project/coding-prompts", json=SAMPLE_REQUEST_PAYLOAD)
            assert res.status_code == 200
            data = res.json()
            assert len(data["module_walkthroughs"]) >= 1
            assert len(data["copy_ready_prompts"]) >= 1


@pytest.mark.asyncio
async def test_documentation_endpoint():
    """Verify POST /api/project/documentation."""
    with patch("backend.app.services.claude_service.AsyncAnthropic") as mock_anthropic:
        mock_instance = mock_anthropic.return_value
        mock_instance.messages.create = AsyncMock(return_value=create_mock_block(MOCK_DOCUMENTATION_DATA))

        with patch("backend.app.config.Settings.is_anthropic_configured", True):
            res = client.post("/api/project/documentation", json=SAMPLE_REQUEST_PAYLOAD)
            assert res.status_code == 200
            data = res.json()
            assert "abstract" in data
            assert "literature_review_outline" in data
            assert len(data["future_scope"]) >= 1


@pytest.mark.asyncio
async def test_full_blueprint_endpoint():
    """Verify POST /api/project/full-blueprint coordinates all 6 services."""
    def side_effect_mock(*args, **kwargs):
        system_text = kwargs.get("system", "")
        if "evaluator" in system_text.lower():
            return create_mock_block(MOCK_ANALYSIS_DATA)
        elif "architect and technical mentor" in system_text.lower():
            return create_mock_block(MOCK_TECH_STACK_DATA)
        elif "systems design mentor" in system_text.lower():
            return create_mock_block(MOCK_ARCHITECTURE_DATA)
        elif "agile technical project manager" in system_text.lower():
            return create_mock_block(MOCK_ROADMAP_DATA)
        elif "pair programming mentor" in system_text.lower():
            return create_mock_block(MOCK_CODING_PROMPTS_DATA)
        else:
            return create_mock_block(MOCK_DOCUMENTATION_DATA)

    with patch("backend.app.services.claude_service.AsyncAnthropic") as mock_anthropic:
        mock_instance = mock_anthropic.return_value
        mock_instance.messages.create = AsyncMock(side_effect=side_effect_mock)

        with patch("backend.app.config.Settings.is_anthropic_configured", True):
            res = client.post("/api/project/full-blueprint", json=SAMPLE_REQUEST_PAYLOAD)
            assert res.status_code == 200
            data = res.json()
            assert data["project_title"] == "AgriVision: Crop Disease Detection"
            assert "analysis" in data
            assert "technology_stack" in data
            assert "architecture" in data
            assert "roadmap" in data
            assert "coding_and_prompts" in data
            assert "documentation" in data
            assert "generated_at" in data["metadata"]


def test_project_endpoints_unconfigured_credentials():
    """Verify endpoints safely return HTTP 503 when API key is missing."""
    with patch("backend.app.config.Settings.is_anthropic_configured", False):
        endpoints = [
            "/api/project/analyze",
            "/api/project/technology-stack",
            "/api/project/architecture",
            "/api/project/roadmap",
            "/api/project/coding-prompts",
            "/api/project/documentation",
            "/api/project/full-blueprint"
        ]
        for ep in endpoints:
            res = client.post(ep, json=SAMPLE_REQUEST_PAYLOAD)
            assert res.status_code == 503
            assert res.json()["detail"]["error"] == "ai_service_unconfigured"


def test_project_input_validation():
    """Verify Pydantic input validation blocks malformed requests with HTTP 422."""
    # 1. Title too short (< 3 chars)
    res1 = client.post("/api/project/analyze", json={"title": "ab"})
    assert res1.status_code == 422

    # 2. Invalid team size (<= 0)
    res2 = client.post("/api/project/analyze", json={"title": "Valid Title", "team_size": 0})
    assert res2.status_code == 422
