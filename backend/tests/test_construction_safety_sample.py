"""
End-to-End Mocked Verification for Sample Project:
'AI Construction Safety Monitoring' (Python, React, SQL; Beginner; 3-Month Deadline; Team of 3).
Tests all 7 endpoints of Phase 3 with zero API credit usage.
"""

import json
from unittest.mock import AsyncMock, patch, MagicMock
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

SAMPLE_PROJECT_INPUT = {
    "title": "AI Construction Safety Monitoring",
    "description": "Real-time computer vision system using site camera streams to detect worker PPE (hardhats, reflective vests) and alert on danger zone trespassing.",
    "domain": "AI / Machine Learning",
    "skills": ["Python", "React", "SQL"],
    "experience_level": "Beginner (1st/2nd Year Student)",
    "budget": "Free / Open Source tier",
    "deadline": "3 months",
    "is_team": True,
    "team_size": 3
}

MOCK_ANALYSIS = {
    "project_title": "AI Construction Safety Monitoring",
    "domain": "AI / Machine Learning",
    "problem_statement": "Construction sites account for over 20% of industrial worker fatalities due to PPE non-compliance and unauthorized entry into heavy machinery zones.",
    "existing_limitations": [
        "Manual safety inspections are intermittent and cover less than 15% of active work hours.",
        "Human safety officers cannot monitor multiple camera feeds simultaneously."
    ],
    "proposed_solution": "An edge-compatible AI video analytics system that continuously audits CCTV RTSP streams, detects missing PPE in real time, and logs safety violations to a dashboard with instant alerts.",
    "target_users": ["Site Safety Officers", "Construction Project Managers", "General Contractors"],
    "main_objectives": [
        "Fine-tune a lightweight YOLOv8 object detector for hardhat and vest compliance with >88% mAP.",
        "Build a React frontend displaying live safety violation alerts and compliance metrics.",
        "Implement an asynchronous Python backend with PostgreSQL storing violation timestamps and video clips."
    ],
    "expected_outcomes": [
        "Working web dashboard with live camera preview and bounding boxes.",
        "Automated safety audit report generator exporting PDF incident summaries.",
        "Sub-second alert latency upon PPE violation detection."
    ],
    "unique_selling_proposition": "Combines zero-cost open-source YOLOv8 with automated incident clip archiving and real-time dashboard push notifications.",
    "innovation_opportunities": [
        "Geofenced danger zones using polygon coordinates on video frames.",
        "SMS/WhatsApp incident alert dispatch via free webhook tiers."
    ],
    "feasibility_assessment": "Highly feasible for a 3-student beginner team over 3 months using pre-trained YOLO models and transfer learning on Roboflow PPE datasets.",
    "project_complexity": "Moderate",
    "follow_up_questions": []
}

MOCK_TECH_STACK = {
    "project_title": "AI Construction Safety Monitoring",
    "technology_recommendations": [
        {
            "technology_name": "FastAPI (Python)",
            "category": "Backend Framework",
            "why_suitable": "Native Python ecosystem for OpenCV/PyTorch model inference, high async performance, and automatic Swagger docs for beginners.",
            "role_in_project": "Handles video stream frame processing, violation ingestion API, and database operations.",
            "implementation_guide": "Initialize with pip install fastapi uvicorn opencv-python ultralytics; expose /api/stream and /api/violations.",
            "cost_tier": "100% Free / Open Source",
            "alternatives": ["Flask"]
        },
        {
            "technology_name": "React + Tailwind CSS",
            "category": "Frontend Framework",
            "why_suitable": "Beginner-friendly component model with pre-built UI components for dashboard cards, tables, and video players.",
            "role_in_project": "Renders real-time safety metrics, alert toast notifications, and incident review logs.",
            "implementation_guide": "Setup using Vite (npm create vite@latest), install Lucide icons and Tailwind CSS.",
            "cost_tier": "100% Free / Open Source",
            "alternatives": ["Streamlit"]
        },
        {
            "technology_name": "PostgreSQL / SQLite",
            "category": "Database",
            "why_suitable": "Relational structure ideal for safety violation records with timestamps, camera IDs, and confidence scores.",
            "role_in_project": "Stores camera metadata, violation event logs, and user credentials.",
            "implementation_guide": "Use SQLAlchemy ORM with SQLite for local dev, migrate to Neon/Supabase PostgreSQL for deployment.",
            "cost_tier": "100% Free / Open Source",
            "alternatives": ["MySQL"]
        },
        {
            "technology_name": "YOLOv8 Nano (Ultralytics)",
            "category": "AI/ML Model",
            "why_suitable": "Lightweight object detection model capable of 30+ FPS on standard CPU/laptops without expensive GPUs.",
            "role_in_project": "Classifies hardhats, vests, persons, and machinery in video frames.",
            "implementation_guide": "Load pre-trained weights via ultralytics Python package, fine-tune on Roboflow Construction PPE dataset.",
            "cost_tier": "100% Free / Open Source (AGPL-3.0)",
            "alternatives": ["MobileNet-SSD"]
        }
    ],
    "ai_tool_advisors": [
        {
            "tool_name": "Claude 3.5 Sonnet",
            "development_activity": "Architecture Refinement & Edge Case Troubleshooting",
            "how_to_use": "Provide OpenCV stream loop snippets to Claude for memory leak and thread bottleneck debugging.",
            "when_to_use": "Phase 3 (Backend) and Phase 5 (AI Integration)",
            "free_alternative": "Hugging Face Chat"
        },
        {
            "tool_name": "Antigravity",
            "development_activity": "Agentic Scaffold & Multi-Module Integration",
            "how_to_use": "Use Antigravity workflows to scaffold FastAPI routes, SQLAlchemy models, and React components simultaneously.",
            "when_to_use": "Phases 1 through 6",
            "free_alternative": "VS Code + Copilot Free"
        }
    ],
    "rationale_summary": "This stack leverages the team's existing knowledge of Python, React, and SQL, avoiding GPU cloud costs by utilizing YOLOv8n CPU inference."
}

MOCK_ARCHITECTURE = {
    "project_title": "AI Construction Safety Monitoring",
    "high_level_overview": "Three-tier architecture comprising a React Safety Dashboard client, FastAPI inference & coordination backend, and PostgreSQL relational database.",
    "frontend_backend_flow": "React client polls or receives WebSocket feeds of violation events from FastAPI; video frames are processed asynchronously in the backend inference worker.",
    "database_architecture": "Normalized relational schema with Cameras, Violations, ViolationTypes, and Users tables.",
    "module_breakdown": [
        {
            "module_name": "Video Ingestion & Detection Worker",
            "responsibility": "Reads video streams, runs YOLOv8 frame-by-frame, and detects missing PPE.",
            "technologies_used": ["OpenCV", "Ultralytics YOLOv8", "Python Threading"],
            "inputs": "RTSP stream / local MP4 video file",
            "outputs": "Bounding boxes, violation event payload"
        },
        {
            "module_name": "Safety Alert REST API",
            "responsibility": "Exposes endpoints for querying violations, camera status, and safety statistics.",
            "technologies_used": ["FastAPI", "Pydantic", "SQLAlchemy"],
            "inputs": "Client HTTP requests",
            "outputs": "JSON violation history and summary metrics"
        }
    ],
    "api_endpoint_suggestions": [
        {"method": "GET", "path": "/api/v1/cameras", "description": "List all active site cameras and statuses"},
        {"method": "GET", "path": "/api/v1/violations", "description": "Get paginated list of PPE violation events"},
        {"method": "POST", "path": "/api/v1/detect/frame", "description": "Process a single test frame and return detections"}
    ],
    "data_flow_explanation": "CCTV Stream -> OpenCV capture -> YOLO inference -> Violation filter -> DB Write & WebSocket broadcast -> React Dashboard.",
    "mermaid_diagram": "flowchart TD\n    Camera[\"CCTV / Video Stream\"] -->|Frames| Ingest[\"FastAPI Ingestion Worker\"]\n    Ingest -->|Frames| YOLO[\"YOLOv8 Detection Engine\"]\n    YOLO -->|Violations| API[\"FastAPI Gateway\"]\n    API --> DB[(\"PostgreSQL Database\")]\n    API -->|Live Alerts| UI[\"React Dashboard\"]"
}

MOCK_ROADMAP = {
    "project_title": "AI Construction Safety Monitoring",
    "total_estimated_duration": "3 months",
    "phases": [
        {
            "phase_number": 1,
            "phase_title": "Phase 1: Research and Requirements",
            "estimated_duration": "Weeks 1-2",
            "tasks": ["Acquire Roboflow PPE dataset", "Formulate SRS document with safety criteria"],
            "dependencies": ["None"],
            "required_tools": ["Roboflow", "Google Colab"],
            "expected_output": "Verified dataset with hardhat/vest annotations and SRS document",
            "completion_checklist": ["Dataset split into 70/20/10 train/val/test", "SRS approved by guide"]
        },
        {
            "phase_number": 2,
            "phase_title": "Phase 2: UI/UX Design",
            "estimated_duration": "Week 3",
            "tasks": ["Design site map view and violation alert feed in Figma"],
            "dependencies": ["Phase 1"],
            "required_tools": ["Figma"],
            "expected_output": "High-fidelity dashboard wireframe",
            "completion_checklist": ["Dashboard layout approved", "Color palette and alert badges styled"]
        },
        {
            "phase_number": 3,
            "phase_title": "Phase 3: Backend Development",
            "estimated_duration": "Weeks 4-5",
            "tasks": ["Scaffold FastAPI app", "Implement database models and CRUD routes"],
            "dependencies": ["Phase 1"],
            "required_tools": ["FastAPI", "SQLAlchemy", "SQLite"],
            "expected_output": "Tested REST API with Swagger documentation",
            "completion_checklist": ["All CRUD endpoints return HTTP 200/201", "Automated pytest passing"]
        },
        {
            "phase_number": 4,
            "phase_title": "Phase 4: Frontend Development",
            "estimated_duration": "Weeks 6-7",
            "tasks": ["Build React dashboard", "Connect API endpoints via Axios"],
            "dependencies": ["Phase 2", "Phase 3"],
            "required_tools": ["React", "Vite", "Tailwind CSS"],
            "expected_output": "Responsive client displaying live data and camera cards",
            "completion_checklist": ["UI renders real data from backend", "Zero console errors"]
        },
        {
            "phase_number": 5,
            "phase_title": "Phase 5: AI/ML Integration",
            "estimated_duration": "Weeks 8-9",
            "tasks": ["Train YOLOv8n model on Colab", "Integrate model weights into FastAPI inference pipeline"],
            "dependencies": ["Phase 3"],
            "required_tools": ["PyTorch", "Ultralytics", "OpenCV"],
            "expected_output": "Trained best.pt model running at >20 FPS on CPU",
            "completion_checklist": ["Precision > 85%", "End-to-end frame detection working"]
        },
        {
            "phase_number": 6,
            "phase_title": "Phase 6: Database Integration",
            "estimated_duration": "Week 10",
            "tasks": ["Connect PostgreSQL instance", "Implement automatic video frame snapshot saving"],
            "dependencies": ["Phase 3", "Phase 5"],
            "required_tools": ["PostgreSQL", "SQLAlchemy"],
            "expected_output": "Persistent violation storage with query indexing",
            "completion_checklist": ["Data persists across server restarts", "Indexes on timestamp column"]
        },
        {
            "phase_number": 7,
            "phase_title": "Phase 7: Testing",
            "estimated_duration": "Week 11",
            "tasks": ["Unit tests for backend and frontend", "Stress test inference pipeline with multiple video clips"],
            "dependencies": ["Phase 4", "Phase 5", "Phase 6"],
            "required_tools": ["pytest", "Jest"],
            "expected_output": "Test coverage report > 80%",
            "completion_checklist": ["No memory leaks during 1-hour stream loop", "All tests passing"]
        },
        {
            "phase_number": 8,
            "phase_title": "Phase 8: Deployment",
            "estimated_duration": "Week 12",
            "tasks": ["Deploy backend to Render", "Deploy React frontend to Vercel"],
            "dependencies": ["Phase 7"],
            "required_tools": ["Render", "Vercel", "Docker"],
            "expected_output": "Live public URLs for demo",
            "completion_checklist": ["CORS configured between Vercel and Render", "Live demo verified on mobile"]
        },
        {
            "phase_number": 9,
            "phase_title": "Phase 9: Documentation & Presentation",
            "estimated_duration": "Week 12",
            "tasks": ["Write final-year project thesis report", "Create PowerPoint slides and 3-minute demo video"],
            "dependencies": ["Phase 8"],
            "required_tools": ["LaTeX / MS Word", "PowerPoint"],
            "expected_output": "Bound project report and presentation deck",
            "completion_checklist": ["Guide approval signature obtained", "Viva slide deck rehearsed"]
        }
    ],
    "deployment_and_testing": {
        "hosting_platform": "Render (FastAPI backend) + Vercel (React frontend) + Neon (Serverless Postgres)",
        "environment_variables_checklist": ["DATABASE_URL", "CORS_ORIGINS", "MODEL_PATH"],
        "step_by_step_deployment": [
            "1. Push backend and frontend to GitHub in separate folders or monorepo.",
            "2. Create new Web Service on Render pointing to backend/, start command: uvicorn app.main:app --host 0.0.0.0 --port 10000.",
            "3. Create Vercel project pointing to frontend/, set VITE_API_URL to Render service domain."
        ],
        "testing_strategy": [
            "Automated API testing with pytest covering all endpoints.",
            "Synthetic test video suite evaluating detection under low-light and occlusion conditions."
        ],
        "maintenance_practices": [
            "Log monitoring on Render dashboard.",
            "Periodic retraining with false-positive frames collected during pilot runs."
        ]
    }
}

MOCK_CODING_PROMPTS = {
    "project_title": "AI Construction Safety Monitoring",
    "module_walkthroughs": [
        {
            "module_name": "Inference & Stream Processing Worker",
            "purpose": "Captures CCTV frames, performs YOLOv8 inference, filters out detections below 0.6 confidence, and triggers DB logging for missing PPE.",
            "folder_structure": "backend/app/services/\n├── detector.py\n├── stream_worker.py\n└── __init__.py",
            "implementation_steps": [
                "1. Load YOLOv8n weights into memory on application startup.",
                "2. Run a background OpenCV VideoCapture loop extracting every 3rd frame to reduce CPU load.",
                "3. Check detected bounding boxes: if a 'person' is detected without an overlapping 'hardhat' or 'vest', flag a violation.",
                "4. Write violation record with timestamp and cropped violation snapshot to DB."
            ],
            "example_code_snippet": "from ultralytics import YOLO\nimport cv2\n\nclass SafetyDetector:\n    def __init__(self, model_path: str = 'models/best.pt'):\n        self.model = YOLO(model_path)\n\n    def process_frame(self, frame):\n        results = self.model(frame, conf=0.5)\n        return results[0].boxes",
            "required_dependencies": ["ultralytics>=8.0.0", "opencv-python-headless>=4.8.0", "numpy>=1.24.0"],
            "testing_instructions": "Execute pytest tests/test_detector.py with a sample static test image containing a worker without a helmet.",
            "common_errors_and_solutions": [
                "Error: OpenCV HighGUI / Qt error in headless server -> Fix: Use opencv-python-headless instead of opencv-python.",
                "Error: High CPU usage (100%) -> Fix: Add frame skipping (e.g. cv2.waitKey or analyze 5 FPS instead of 30 FPS)."
            ]
        }
    ],
    "copy_ready_prompts": [
        {
            "target_tool": "Claude 3.5 Sonnet",
            "use_case": "FastAPI Background Stream Worker Implementation",
            "prompt_text": "I am building an 'AI Construction Safety Monitoring' system in Python for my college final year project. I need an asynchronous background worker using OpenCV and Ultralytics YOLOv8 that processes video streams without blocking FastAPI's event loop. Please write a thread-safe implementation with clean error handling when a camera stream disconnects."
        },
        {
            "target_tool": "Antigravity",
            "use_case": "React Dashboard Scaffolding with Live Violation Stream",
            "prompt_text": "Scaffold a modern React + Tailwind CSS dashboard for 'AI Construction Safety Monitoring'. The dashboard must display: 1) Active camera feeds with status badges, 2) Total safety violations today counter, 3) Real-time alert list with severity tags (High, Medium, Low), and 4) A table of recent incident snapshots."
        },
        {
            "target_tool": "GitHub Copilot",
            "use_case": "Pytest Test Suite for Safety Violation Filtering",
            "prompt_text": "Write comprehensive pytest test cases for the SafetyDetector service. Mock the Ultralytics YOLO model output to simulate: 1) Compliant worker (has helmet and vest), 2) Non-compliant worker (missing helmet), and 3) Empty frame. Assert expected violation payloads."
        }
    ]
}

MOCK_DOCUMENTATION = {
    "project_title": "AI Construction Safety Monitoring",
    "abstract": "Occupational safety compliance on construction jobsites remains an urgent global concern, with non-compliance in Personal Protective Equipment (PPE) causing thousands of preventable injuries annually. This paper presents 'AI Construction Safety Monitoring', an automated edge-assisted computer vision framework designed to audit worker PPE compliance and restricted area incursions in real time. Utilizing a lightweight YOLOv8 neural network integrated with an asynchronous FastAPI backend and a React monitoring dashboard, the system processes multi-camera feeds at 25+ frames per second on commodity hardware. The prototype achieves an empirical mean Average Precision (mAP@0.5) of 89.2% on custom PPE datasets with alert dispatch latency under 450ms. Experimental validation confirms that automated continuous surveillance provides a 6x increase in safety audit coverage compared to traditional manual inspections.",
    "introduction": "The construction sector is classified among the most hazardous industrial environments worldwide. Despite strict regulatory mandates, compliance tracking relies heavily on periodic physical walkthroughs by safety inspectors. These inspections suffer from severe coverage gaps and observer bias. Advances in deep learning and real-time edge computer vision offer an unprecedented opportunity to transform passive surveillance cameras into proactive safety sentinels.",
    "problem_statement": "How can an automated, low-cost computer vision system be engineered to detect missing PPE and safety perimeter breaches from existing CCTV infrastructure in real time without requiring dedicated high-cost GPU workstations?",
    "literature_review_outline": [
        "Classical computer vision approaches (HOG, Haar Cascades) and their susceptibility to illumination variations on outdoor sites.",
        "Two-stage detectors (Faster R-CNN) versus one-stage detectors (YOLO, SSD) in real-time edge deployment trade-offs.",
        "Existing commercial safety analytics solutions and barriers to adoption for small-to-medium enterprise (SME) contractors.",
        "Privacy preservation techniques in worker video surveillance."
    ],
    "objectives": [
        "To construct an annotated dataset covering hardhats, safety vests, boots, and danger perimeter zones.",
        "To train and quantize an efficient object detection model capable of real-time inference on edge CPUs.",
        "To build a modular, reactive web dashboard for safety officers providing instant alerts and compliance analytics.",
        "To validate the system under diverse real-world lighting and occlusion conditions."
    ],
    "methodology": "The methodology adopts an end-to-end engineering pipeline: 1) Data collection and augmentation using Roboflow, 2) Transfer learning on pre-trained YOLOv8 weights with focal loss optimization, 3) FastAPI asynchronous service architecture with non-blocking video worker threads, and 4) React single-page interface leveraging Tailwind CSS for state visualization.",
    "proposed_architecture_summary": "Three-tier architecture comprising edge ingestion, API coordination with relational persistence, and interactive web visualization.",
    "implementation_plan_summary": "Executed across 9 structured sprints spanning requirements formulation, model training, API construction, UI design, stress testing, and cloud deployment.",
    "testing_methodology": "Quantitative validation using precision, recall, and mAP metrics; performance benchmarking measuring inference latency and memory footprint; and qualitative usability evaluation with safety personnel.",
    "results_section_template": "Comparative performance table detailing Model Architecture, Input Resolution, Precision (%), Recall (%), mAP@0.5 (%), and Latency (ms) across distinct testing scenarios (full daylight, dusk, partial occlusion).",
    "conclusion": "AI Construction Safety Monitoring demonstrates that state-of-the-art deep learning can be democratized for construction worker safety on accessible hardware, offering an effective automated shield against site hazards.",
    "future_scope": [
        "Integration of worker fall detection and slip hazard identification.",
        "Deployment on solar-powered drone surveillance systems for expansive civil engineering projects."
    ]
}


def create_block(data):
    b = MagicMock()
    b.type = "text"
    b.text = json.dumps(data)
    r = MagicMock()
    r.content = [b]
    return r


# ---------------------------------------------------------------------------
# Test Functions
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_sample_project_analysis():
    """Verify Problem Analysis on Construction Safety project."""
    with patch("backend.app.services.claude_service.AsyncAnthropic") as mock_anthropic:
        mock_instance = mock_anthropic.return_value
        mock_instance.messages.create = AsyncMock(return_value=create_block(MOCK_ANALYSIS))

        with patch("backend.app.config.Settings.is_anthropic_configured", True):
            res = client.post("/api/project/analyze", json=SAMPLE_PROJECT_INPUT)
            assert res.status_code == 200
            data = res.json()
            assert data["project_title"] == "AI Construction Safety Monitoring"
            assert "20% of industrial worker fatalities" in data["problem_statement"]
            assert len(data["existing_limitations"]) == 2
            assert len(data["target_users"]) == 3
            assert data["project_complexity"] == "Moderate"


@pytest.mark.asyncio
async def test_sample_project_tech_stack():
    """Verify Technology Recommendations on Construction Safety project."""
    with patch("backend.app.services.claude_service.AsyncAnthropic") as mock_anthropic:
        mock_instance = mock_anthropic.return_value
        mock_instance.messages.create = AsyncMock(return_value=create_block(MOCK_TECH_STACK))

        with patch("backend.app.config.Settings.is_anthropic_configured", True):
            res = client.post("/api/project/technology-stack", json=SAMPLE_PROJECT_INPUT)
            assert res.status_code == 200
            data = res.json()
            assert len(data["technology_recommendations"]) == 4
            assert any(t["technology_name"].startswith("FastAPI") for t in data["technology_recommendations"])
            assert any("YOLOv8" in t["technology_name"] for t in data["technology_recommendations"])
            assert len(data["ai_tool_advisors"]) == 2


@pytest.mark.asyncio
async def test_sample_project_architecture():
    """Verify System Architecture & Mermaid Diagram on Construction Safety project."""
    with patch("backend.app.services.claude_service.AsyncAnthropic") as mock_anthropic:
        mock_instance = mock_anthropic.return_value
        mock_instance.messages.create = AsyncMock(return_value=create_block(MOCK_ARCHITECTURE))

        with patch("backend.app.config.Settings.is_anthropic_configured", True):
            res = client.post("/api/project/architecture", json=SAMPLE_PROJECT_INPUT)
            assert res.status_code == 200
            data = res.json()
            assert "flowchart TD" in data["mermaid_diagram"]
            assert len(data["module_breakdown"]) == 2
            assert len(data["api_endpoint_suggestions"]) == 3


@pytest.mark.asyncio
async def test_sample_project_roadmap():
    """Verify 9-Phase Development Roadmap on Construction Safety project."""
    with patch("backend.app.services.claude_service.AsyncAnthropic") as mock_anthropic:
        mock_instance = mock_anthropic.return_value
        mock_instance.messages.create = AsyncMock(return_value=create_block(MOCK_ROADMAP))

        with patch("backend.app.config.Settings.is_anthropic_configured", True):
            res = client.post("/api/project/roadmap", json=SAMPLE_PROJECT_INPUT)
            assert res.status_code == 200
            data = res.json()
            assert len(data["phases"]) == 9
            assert data["total_estimated_duration"] == "3 months"
            assert "Render" in data["deployment_and_testing"]["hosting_platform"]


@pytest.mark.asyncio
async def test_sample_project_coding_prompts():
    """Verify Module-Wise Coding Steps & Prompts on Construction Safety project."""
    with patch("backend.app.services.claude_service.AsyncAnthropic") as mock_anthropic:
        mock_instance = mock_anthropic.return_value
        mock_instance.messages.create = AsyncMock(return_value=create_block(MOCK_CODING_PROMPTS))

        with patch("backend.app.config.Settings.is_anthropic_configured", True):
            res = client.post("/api/project/coding-prompts", json=SAMPLE_PROJECT_INPUT)
            assert res.status_code == 200
            data = res.json()
            assert len(data["module_walkthroughs"]) == 1
            assert len(data["copy_ready_prompts"]) == 3
            assert any(p["target_tool"] == "Antigravity" for p in data["copy_ready_prompts"])


@pytest.mark.asyncio
async def test_sample_project_documentation():
    """Verify Academic Report Draft on Construction Safety project."""
    with patch("backend.app.services.claude_service.AsyncAnthropic") as mock_anthropic:
        mock_instance = mock_anthropic.return_value
        mock_instance.messages.create = AsyncMock(return_value=create_block(MOCK_DOCUMENTATION))

        with patch("backend.app.config.Settings.is_anthropic_configured", True):
            res = client.post("/api/project/documentation", json=SAMPLE_PROJECT_INPUT)
            assert res.status_code == 200
            data = res.json()
            assert "Occupational safety compliance" in data["abstract"]
            assert len(data["literature_review_outline"]) == 4
            assert len(data["future_scope"]) == 2


@pytest.mark.asyncio
async def test_sample_project_full_blueprint():
    """Verify Master Blueprint on Construction Safety project."""
    def mock_side_effect(*args, **kwargs):
        sys_prompt = kwargs.get("system", "")
        if "evaluator" in sys_prompt.lower():
            return create_block(MOCK_ANALYSIS)
        elif "technical mentor" in sys_prompt.lower():
            return create_block(MOCK_TECH_STACK)
        elif "systems design mentor" in sys_prompt.lower():
            return create_block(MOCK_ARCHITECTURE)
        elif "project manager" in sys_prompt.lower():
            return create_block(MOCK_ROADMAP)
        elif "pair programming" in sys_prompt.lower():
            return create_block(MOCK_CODING_PROMPTS)
        else:
            return create_block(MOCK_DOCUMENTATION)

    with patch("backend.app.services.claude_service.AsyncAnthropic") as mock_anthropic:
        mock_instance = mock_anthropic.return_value
        mock_instance.messages.create = AsyncMock(side_effect=mock_side_effect)

        with patch("backend.app.config.Settings.is_anthropic_configured", True):
            res = client.post("/api/project/full-blueprint", json=SAMPLE_PROJECT_INPUT)
            assert res.status_code == 200
            data = res.json()
            assert data["project_title"] == "AI Construction Safety Monitoring"
            assert data["analysis"]["project_complexity"] == "Moderate"
            assert len(data["technology_stack"]["technology_recommendations"]) == 4
            assert "flowchart TD" in data["architecture"]["mermaid_diagram"]
            assert len(data["roadmap"]["phases"]) == 9
            assert len(data["coding_and_prompts"]["copy_ready_prompts"]) == 3
            assert "Occupational safety compliance" in data["documentation"]["abstract"]
