"""
Phase 9 — Coding Assistance & GitHub Integration Tests.

All AI calls mocked with deterministic fixtures. Zero paid credits consumed.
Verifies:
- Production starter code generation with unit tests
- Traceback diagnosis and drop-in code fix generation
- GitHub repository scaffolding (README, .gitignore, directory tree, issue templates)
- Safety rules: offline scaffolding when unconfigured, no unintended repo mutations
- REST endpoints for coding and GitHub services
"""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.schemas.coding_assistant import (
    CodeGenerateRequest,
    CodeGenerateResponse,
    CodeDebugRequest,
    CodeDebugResponse,
    GitHubScaffoldRequest,
)
from backend.app.services.code_assistant import CodeAssistantService
from backend.app.services.github_service import GitHubService


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


MOCK_CODE_RESPONSE = CodeGenerateResponse(
    module_name="VideoIngestionWorker",
    language="python",
    file_path="backend/app/services/video_worker.py",
    starter_code="""
import cv2
import asyncio

class VideoIngestionWorker:
    def __init__(self, rtsp_url: str):
        self.rtsp_url = rtsp_url
        self.is_running = False

    async def start(self):
        self.is_running = True
        cap = cv2.VideoCapture(self.rtsp_url)
        while self.is_running and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            await asyncio.sleep(0.03)
        cap.release()
""",
    implementation_steps=[
        "1. Install opencv-python in virtual environment",
        "2. Add RTSP stream URL to .env",
        "3. Instantiate worker in FastAPI lifespan startup hook",
    ],
    code_explanation="Asynchronous video capture loop reading frames from RTSP camera feeds.",
    unit_test_code="""
import pytest
from backend.app.services.video_worker import VideoIngestionWorker

@pytest.mark.asyncio
async def test_worker_initialization():
    worker = VideoIngestionWorker('rtsp://fake/stream')
    assert worker.rtsp_url == 'rtsp://fake/stream'
    assert worker.is_running is False
""",
    security_tips=["Always authenticate RTSP feeds using credentials in environment variables."],
)

MOCK_DEBUG_RESPONSE = CodeDebugResponse(
    error_analysis="IndexError: list index out of range when accessing detected bounding box list.",
    root_cause="The YOLO model returned an empty detection tensor for a frame with zero objects, causing boxes[0] to fail.",
    suggested_fix_code="""
if len(detections) > 0:
    primary_box = detections[0]
else:
    primary_box = None
""",
    explanation="Added a guard check verifying that the detections list is non-empty before indexing.",
    prevention_advice=["Always validate tensor or list lengths before index lookups."],
)


# ---------------------------------------------------------------------------
# Unit Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_code_assistant_generate_starter():
    service = CodeAssistantService()
    req = CodeGenerateRequest(
        module_name="VideoIngestionWorker",
        language="python",
        framework="OpenCV + FastAPI",
        description="Ingest live surveillance video frames asynchronously.",
        project_context="AI Construction Safety Monitoring",
    )

    with patch.object(service.claude, "complete_structured", new=AsyncMock(return_value=MOCK_CODE_RESPONSE)):
        res = await service.generate_starter_code(req)

    assert res.module_name == "VideoIngestionWorker"
    assert "class VideoIngestionWorker" in res.starter_code
    assert "test_worker_initialization" in res.unit_test_code
    assert len(res.implementation_steps) >= 3


@pytest.mark.asyncio
async def test_code_assistant_debug_code():
    service = CodeAssistantService()
    req = CodeDebugRequest(
        code_snippet="primary = detections[0]",
        error_traceback="IndexError: list index out of range",
        language="python",
        expected_behavior="Handle empty detections gracefully",
    )

    with patch.object(service.claude, "complete_structured", new=AsyncMock(return_value=MOCK_DEBUG_RESPONSE)):
        res = await service.debug_code(req)

    assert "IndexError" in res.error_analysis
    assert "if len(detections) > 0:" in res.suggested_fix_code
    assert len(res.prevention_advice) >= 1


def test_github_scaffold_generation():
    service = GitHubService()
    req = GitHubScaffoldRequest(
        repo_name="smart-traffic-copilot",
        project_title="Smart City Traffic AI",
        description="Real-time multi-agent reinforcement learning traffic signal controller.",
        tech_stack=["Python", "FastAPI", "React", "PyTorch"],
    )

    scaffold = service.generate_scaffold(req)
    assert scaffold.repo_name == "smart-traffic-copilot"
    assert "Smart City Traffic AI" in scaffold.readme_content
    assert "FastAPI" in scaffold.readme_content
    assert ".venv/" in scaffold.suggested_gitignore
    assert "node_modules/" in scaffold.suggested_gitignore
    assert "backend/" in scaffold.suggested_directory_tree
    assert "frontend/" in scaffold.suggested_directory_tree
    assert len(scaffold.suggested_issues) >= 5
    assert "git init" in scaffold.setup_commands[0]


# ---------------------------------------------------------------------------
# API Endpoint Tests
# ---------------------------------------------------------------------------

def test_github_endpoints(client: TestClient):
    # 1. Status endpoint
    status_resp = client.get("/api/github/status")
    assert status_resp.status_code == 200
    assert "configured" in status_resp.json()

    # 2. Scaffold endpoint
    scaffold_resp = client.post(
        "/api/github/scaffold",
        json={
            "repo_name": "ai-safety-monitor",
            "project_title": "AI Safety Monitor",
            "description": "PPE detection system for construction sites.",
            "tech_stack": ["Python", "OpenCV", "FastAPI", "React"],
        },
    )
    assert scaffold_resp.status_code == 200
    data = scaffold_resp.json()
    assert data["repo_name"] == "ai-safety-monitor"
    assert "README.md" not in data["suggested_gitignore"]
    assert len(data["suggested_issues"]) == 5


def test_coding_endpoints(client: TestClient):
    with patch(
        "backend.app.services.claude_service.ClaudeService.complete_structured",
        new=AsyncMock(return_value=MOCK_CODE_RESPONSE),
    ):
        gen_resp = client.post(
            "/api/coding/generate",
            json={
                "module_name": "VideoIngestionWorker",
                "language": "python",
                "description": "Ingest live camera video stream.",
            },
        )
        assert gen_resp.status_code == 200
        assert gen_resp.json()["module_name"] == "VideoIngestionWorker"

    with patch(
        "backend.app.services.claude_service.ClaudeService.complete_structured",
        new=AsyncMock(return_value=MOCK_DEBUG_RESPONSE),
    ):
        dbg_resp = client.post(
            "/api/coding/debug",
            json={
                "code_snippet": "primary = detections[0]",
                "error_traceback": "IndexError: list index out of range",
                "language": "python",
            },
        )
        assert dbg_resp.status_code == 200
        assert "IndexError" in dbg_resp.json()["error_analysis"]
