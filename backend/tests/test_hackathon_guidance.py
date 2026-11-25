"""
Automated unit & integration tests for Hackathon Guidance Mode (Phase 4).
Tests the 3 required competition scenarios with zero paid API credit usage.
"""

import json
from unittest.mock import AsyncMock, patch, MagicMock
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

# ---------------------------------------------------------------------------
# Test Scenarios Definitions
# ---------------------------------------------------------------------------

SCENARIO_1_INPUT = {
    "hackathon_name": "E-Commerce Trust Hack 2026",
    "problem_statement": "Detect coordinated fake reviews, bot-generated ratings, and review bombing on e-commerce platforms to restore consumer trust.",
    "domain": "E-Commerce & NLP",
    "duration": "24 hours",
    "team_size": 4,
    "team_skills": ["Python", "React", "basic ML"],
    "experience_level": "Intermediate",
    "budget": "Free Tier only"
}

SCENARIO_2_INPUT = {
    "hackathon_name": "Smart City Mobility Sprint",
    "problem_statement": "Identify road hazards, potholes, and debris in real time from dashcam feeds to alert drivers and inform municipal repair crews.",
    "domain": "Computer Vision & Smart Cities",
    "duration": "36 hours",
    "team_size": 3,
    "team_skills": ["Python", "OpenCV", "React"],
    "experience_level": "Intermediate",
    "budget": "Free Tier only"
}

SCENARIO_3_INPUT = {
    "hackathon_name": "AgriTech Innovators Cup",
    "problem_statement": "Diagnose crop diseases from leaf photographs, calculate infection severity, and generate local-language organic treatment recommendations.",
    "domain": "AgriTech & Edge AI",
    "duration": "48 hours",
    "team_size": 2,
    "team_skills": ["Python", "basic ML", "frontend"],
    "experience_level": "Beginner",
    "budget": "Free Tier only"
}


# ---------------------------------------------------------------------------
# Mock Response Helpers
# ---------------------------------------------------------------------------

def make_mock_block(payload_dict: dict):
    b = MagicMock()
    b.type = "text"
    b.text = json.dumps(payload_dict)
    r = MagicMock()
    r.content = [b]
    return r


# ---------------------------------------------------------------------------
# Tests: Scenario 1 - Fake Review Detection (24h, 4 members)
# ---------------------------------------------------------------------------

MOCK_S1_ANALYSIS = {
    "hackathon_name": "E-Commerce Trust Hack 2026",
    "problem_summary": "E-commerce platforms are infiltrated by syndicates generating deceptive reviews, distorting purchase decisions.",
    "target_users": ["Online Shoppers", "E-commerce Merchant Trust & Safety Teams"],
    "existing_challenges": ["Heuristic filtering fails against modern LLM-synthesized reviews.", "Volume exceeds human audit bandwidth."],
    "core_requirements": ["Identify bot/syndicate linguistic fingerprints", "Sub-second inference for chrome extension/API"],
    "expected_solution": "A dual-stage NLP pipeline scoring review authenticity and clustering burst patterns.",
    "constraints": ["24-hour development clock", "Zero-cost compute constraint"],
    "potential_opportunities": ["Browser extension showing real-time Trust Score badge on Amazon/Shopify product pages."]
}

MOCK_S1_IDEAS = {
    "hackathon_name": "E-Commerce Trust Hack 2026",
    "ideas": [
        {
            "idea_id": 1,
            "project_title": "TrustLens: Real-Time Shopper Extension",
            "problem_solved": "Shoppers cannot discern AI-generated product reviews on live e-commerce stores.",
            "proposed_solution": "Chrome extension analyzing on-page reviews via FastAPI backend returning an instant Trust Score.",
            "innovation_angle": "Direct in-situ visual feedback badge on product listings.",
            "key_features": ["Browser extension popup", "Linguistic burst detection", "Trust score gauge"],
            "suggested_tech_stack": ["FastAPI", "React", "Hugging Face DistilBERT"],
            "technical_feasibility": "High",
            "expected_impact": "Prevents immediate buyer remorse for online consumers.",
            "demo_potential": "Very High (Live demo on a live product webpage)"
        },
        {
            "idea_id": 2,
            "project_title": "SyndicateBuster: Review Temporal Burst Graph",
            "problem_solved": "Detects coordinated review fraud rings posting 50 reviews within 10 minutes.",
            "proposed_solution": "Graph-based clustering of reviewer account creation times and IP/language overlap.",
            "innovation_angle": "Visual temporal heatmaps and network graph visualization.",
            "key_features": ["Network graph visualizer", "Temporal burst detector", "Merchant audit table"],
            "suggested_tech_stack": ["Python", "NetworkX", "React-Force-Graph"],
            "technical_feasibility": "Moderate",
            "expected_impact": "Identifies coordinated vendor attack syndicates.",
            "demo_potential": "High (Interactive animated graph)"
        },
        {
            "idea_id": 3,
            "project_title": "AuthenticAI: Multi-Model Stylometric Verifier",
            "problem_solved": "Distinguishes human vs LLM writing styles in product feedback.",
            "proposed_solution": "Stylometric perplexity and burstiness analyzer scoring probability of machine generation.",
            "innovation_angle": "Transparent linguistic explanations highlighting synthetic phrasing.",
            "key_features": ["Perplexity calculator", "Phrase highlighter", "Fraud report export"],
            "suggested_tech_stack": ["FastAPI", "NLTK", "Tailwind CSS"],
            "technical_feasibility": "High",
            "expected_impact": "Educational transparency for marketplace moderators.",
            "demo_potential": "Moderate"
        },
        {
            "idea_id": 4,
            "project_title": "ReviewGuard: Merchant API Webhook Gateway",
            "problem_solved": "Merchants need automated pre-moderation before reviews go live.",
            "proposed_solution": "Shopify app webhook that automatically quarantines suspicious reviews for human review.",
            "innovation_angle": "B2B SaaS integration pattern.",
            "key_features": ["Webhook receiver", "Quarantine dashboard", "CSV bulk auditor"],
            "suggested_tech_stack": ["FastAPI", "SQLite", "React"],
            "technical_feasibility": "High",
            "expected_impact": "Protects marketplace integrity at source.",
            "demo_potential": "Moderate"
        },
        {
            "idea_id": 5,
            "project_title": "CrowdTruth: Community-Powered Review Fact-Checker",
            "problem_solved": "Enables consumers to cross-reference verified buyer purchase receipts.",
            "proposed_solution": "Zero-knowledge receipt verification system combined with sentiment scoring.",
            "innovation_angle": "Decentralized consensus verification mechanism.",
            "key_features": ["Receipt hash validator", "Community consensus feed", "Leaderboard"],
            "suggested_tech_stack": ["Python", "React", "Web3.py"],
            "technical_feasibility": "Moderate",
            "expected_impact": "Grassroots consumer protection.",
            "demo_potential": "High"
        }
    ]
}


@pytest.mark.asyncio
async def test_scenario_1_analyze_and_ideas():
    """Scenario 1: Verify problem analysis and 5+ distinct ideas generation for 24h fake review detection."""
    with patch("backend.app.services.claude_service.AsyncAnthropic") as mock_anthropic:
        mock_instance = mock_anthropic.return_value
        with patch("backend.app.config.Settings.is_anthropic_configured", True):
            # Test /analyze
            mock_instance.messages.create = AsyncMock(return_value=make_mock_block(MOCK_S1_ANALYSIS))
            r_an = client.post("/api/hackathon/analyze", json=SCENARIO_1_INPUT)
            assert r_an.status_code == 200
            d_an = r_an.json()
            assert "reviews" in d_an["problem_summary"].lower()
            assert len(d_an["problem_summary"]) > 40
            assert len(d_an["target_users"]) >= 2
            assert any("shopper" in u.lower() for u in d_an["target_users"])
            assert len(d_an["existing_challenges"]) >= 2
            assert len(d_an["core_requirements"]) >= 2
            assert any("24" in c for c in d_an["constraints"])
            assert len(d_an["potential_opportunities"]) >= 1

            # Test /ideas: Verify at least 5 genuinely distinct concepts
            mock_instance.messages.create = AsyncMock(return_value=make_mock_block(MOCK_S1_IDEAS))
            r_id = client.post("/api/hackathon/ideas", json=SCENARIO_1_INPUT)
            assert r_id.status_code == 200
            d_id = r_id.json()
            assert len(d_id["ideas"]) >= 5

            # Distinctness checks
            titles = [i["project_title"] for i in d_id["ideas"]]
            assert len(set(titles)) == len(d_id["ideas"]), "Every idea must have a unique title"
            solutions = [i["proposed_solution"] for i in d_id["ideas"]]
            assert len(set(solutions)) == len(d_id["ideas"]), "Every idea must have a unique technical approach"

            # Structure and viability checks
            for idea in d_id["ideas"]:
                assert idea["idea_id"] >= 1
                assert len(idea["key_features"]) >= 3
                assert len(idea["suggested_tech_stack"]) >= 2
                assert idea["technical_feasibility"] in ["High", "Moderate", "Challenging"]
                assert len(idea["expected_impact"]) > 15
                assert len(idea["demo_potential"]) >= 3, "demo_potential must be a non-empty meaningful string (e.g. 'High', 'Moderate', 'Low')"


# ---------------------------------------------------------------------------
# Tests: Scenario 2 - AI Road Hazard Detection (36h, 3 members)
# ---------------------------------------------------------------------------

MOCK_S2_EVALUATION = {
    "scoring_method": "Default Balanced Matrix (Relevance 20%, Innovation 20%, Feasibility 20%, Impact 15%, Demo 15%, Time 10%)",
    "ranked_ideas": [
        {
            "idea_id": 1,
            "project_title": "PotholeVision: Dashcam Hazard Mapper",
            "problem_relevance": 9.5,
            "innovation": 8.5,
            "technical_feasibility": 9.0,
            "social_business_impact": 9.0,
            "demo_potential": 9.5,
            "time_feasibility": 8.5,
            "weighted_total_score": 9.05,
            "strengths": ["Instant visual wow-factor with bounding boxes on dashcam video", "Feasible in 36h with OpenCV"],
            "risks_and_pitfalls": ["Keep frame resolution at 480p to prevent CPU lag"]
        },
        {
            "idea_id": 2,
            "project_title": "AcousticRoad: Tire Vibration Audio Detector",
            "problem_relevance": 7.0,
            "innovation": 9.0,
            "technical_feasibility": 6.5,
            "social_business_impact": 7.5,
            "demo_potential": 6.0,
            "time_feasibility": 6.0,
            "weighted_total_score": 7.05,
            "strengths": ["Novel acoustic sensing approach"],
            "risks_and_pitfalls": ["Difficult to demo audio vibrations live to judges in a noisy competition hall"]
        }
    ],
    "recommended_idea_id": 1,
    "recommended_idea_title": "PotholeVision: Dashcam Hazard Mapper",
    "recommendation_rationale": "PotholeVision scores highest on Demo Potential (9.5) and Technical Feasibility (9.0), providing instant visual proof on video compared to acoustic sensing.",
    "disclaimer": "No win is guaranteed. Scoring reflects alignment with feasibility, innovation, and demo polish."
}

MOCK_S2_MVP = {
    "project_title": "PotholeVision: Dashcam Hazard Mapper",
    "core_mvp_summary": "A working video ingestion and hazard mapping flow detecting potholes from uploaded dashcam footage.",
    "must_have_features": [
        "Upload sample dashcam MP4 video",
        "Real-time OpenCV/YOLO bounding boxes around potholes and road cracks",
        "Interactive Leaflet road map with geo-pinned hazard markers"
    ],
    "should_have_features": [
        "Hazard severity score badge (Critical, Moderate, Low)",
        "Summary PDF export for municipality reports"
    ],
    "nice_to_have_features": [
        "Live GPS hardware integration (simulate with test coordinates)",
        "Mobile driver voice alerts (defer)",
        "Multi-city synchronization database (defer)"
    ],
    "minimal_demo_flow": [
        "1. Upload a 10-second test dashcam video clip",
        "2. Watch AI bounding boxes detect 3 potholes in real time",
        "3. See geo-markers automatically appear on the live road hazard map"
    ],
    "potential_failure_points": [
        "Video processing latency -> Pre-transcode video to 640x360 resolution",
        "Network disconnect -> Run backend and React frontend locally on 127.0.0.1"
    ]
}

MOCK_S2_ROADMAP = {
    "hackathon_duration": "36 hours",
    "total_hours": 36,
    "time_blocks": [
        {
            "time_window": "Hours 0 - 6",
            "focus_milestone": "Architecture Setup & Video Processing Pipeline",
            "frontend_tasks": ["Setup React dashboard with Leaflet map container"],
            "backend_ai_tasks": ["FastAPI endpoint for video upload and OpenCV frame extractor"],
            "integration_and_testing": ["Verify video frame uploads and client preview"],
            "deliverable": "Working video upload and map render"
        },
        {
            "time_window": "Hours 6 - 20",
            "focus_milestone": "Core Hazard Detection & Coordinate Mapping",
            "frontend_tasks": ["Render bounding boxes over video canvas", "Pin dynamic markers on map"],
            "backend_ai_tasks": ["Load fine-tuned pothole detection weights", "Calculate hazard severity"],
            "integration_and_testing": ["End-to-end video processing test"],
            "deliverable": "Live hazard detection functioning on test clips"
        },
        {
            "time_window": "Hours 20 - 28",
            "focus_milestone": "UI Polish & Incident Table",
            "frontend_tasks": ["Add alert summary stats, filterable table, dark mode theme"],
            "backend_ai_tasks": ["Performance profiling and frame skipping"],
            "integration_and_testing": ["Stress test with 3 consecutive video uploads"],
            "deliverable": "Feature-complete prototype locked for final polish"
        },
        {
            "time_window": "Hours 28 - 36 (CRITICAL BUFFER)",
            "focus_milestone": "Code Freeze, Pitch Deck & Live Demo Rehearsals",
            "frontend_tasks": ["Zero new features; UI visual polish and clean loading states"],
            "backend_ai_tasks": ["Seed local fallback demo data"],
            "integration_and_testing": ["Rehearse 3-minute pitch 3 times; record 60-second backup video"],
            "deliverable": "Final slide deck, recorded backup video, and rehearsed live demo"
        }
    ],
    "reserved_buffer_hours": 8.0,
    "submission_checklist": [
        "Repository pushed with clean commit history",
        "60-second screen recording backup saved on USB/Cloud",
        "Devpost submission submitted 45 minutes before deadline"
    ]
}


@pytest.mark.asyncio
async def test_scenario_2_evaluation_mvp_roadmap():
    """Scenario 2: Verify idea evaluation, MoSCoW MVP planning, and 36h time-boxed roadmap."""
    candidate_ideas = [
        {
            "idea_id": 1,
            "project_title": "PotholeVision: Dashcam Hazard Mapper",
            "problem_solved": "Potholes and road hazards",
            "proposed_solution": "OpenCV dashcam detection with interactive map pin",
            "innovation_angle": "Real-time edge bounding box display",
            "key_features": ["Video processor", "Hazard map", "PDF export"],
            "suggested_tech_stack": ["FastAPI", "React", "OpenCV"],
            "technical_feasibility": "High",
            "expected_impact": "Prevents vehicular damage and road accidents",
            "demo_potential": "Very High"
        }
    ]

    with patch("backend.app.services.claude_service.AsyncAnthropic") as mock_anthropic:
        mock_instance = mock_anthropic.return_value
        with patch("backend.app.config.Settings.is_anthropic_configured", True):
            # Test /evaluate with candidate_ideas in payload
            mock_instance.messages.create = AsyncMock(return_value=make_mock_block(MOCK_S2_EVALUATION))
            s2_payload = {**SCENARIO_2_INPUT, "candidate_ideas": candidate_ideas}
            r_ev = client.post("/api/hackathon/evaluate", json=s2_payload)
            assert r_ev.status_code == 200
            d_ev = r_ev.json()
            assert len(d_ev["ranked_ideas"]) >= 2

            # Deep evaluation criteria score checks (0 to 10 scale)
            for idea_score in d_ev["ranked_ideas"]:
                assert 0.0 <= idea_score["problem_relevance"] <= 10.0
                assert 0.0 <= idea_score["innovation"] <= 10.0
                assert 0.0 <= idea_score["technical_feasibility"] <= 10.0
                assert 0.0 <= idea_score["social_business_impact"] <= 10.0
                assert 0.0 <= idea_score["demo_potential"] <= 10.0
                assert 0.0 <= idea_score["time_feasibility"] <= 10.0
                assert 0.0 <= idea_score["weighted_total_score"] <= 10.0
                assert len(idea_score["strengths"]) >= 1
                assert len(idea_score["risks_and_pitfalls"]) >= 1

            # Verification of best-fit recommendation logic
            assert d_ev["ranked_ideas"][0]["weighted_total_score"] > d_ev["ranked_ideas"][1]["weighted_total_score"]
            assert d_ev["recommended_idea_title"] == d_ev["ranked_ideas"][0]["project_title"]
            assert len(d_ev["recommendation_rationale"]) > 30, "Recommendation rationale must be thoroughly justified"
            assert "no win is guaranteed" in d_ev["disclaimer"].lower(), "Mandatory ethical disclaimer must be present"

            # Test /mvp: Verify MoSCoW prioritization, demo flow, and risk mitigation
            mock_instance.messages.create = AsyncMock(return_value=make_mock_block(MOCK_S2_MVP))
            r_mvp = client.post("/api/hackathon/mvp", json=SCENARIO_2_INPUT)
            assert r_mvp.status_code == 200
            d_mvp = r_mvp.json()
            assert len(d_mvp["must_have_features"]) >= 3, "Must have prioritized core MVP features"
            assert len(d_mvp["should_have_features"]) >= 1
            assert len(d_mvp["nice_to_have_features"]) >= 2, "Must explicitly list cut/deferred features"
            assert len(d_mvp["minimal_demo_flow"]) >= 3, "Must provide minimal sequential demo flow"
            assert len(d_mvp["potential_failure_points"]) >= 2, "Must provide failure mitigations"

            # Test /roadmap: Verify realistic hourly sprint and reserved buffer
            mock_instance.messages.create = AsyncMock(return_value=make_mock_block(MOCK_S2_ROADMAP))
            r_rd = client.post("/api/hackathon/roadmap", json=SCENARIO_2_INPUT)
            assert r_rd.status_code == 200
            d_rd = r_rd.json()
            assert d_rd["total_hours"] == 36
            assert len(d_rd["time_blocks"]) >= 4
            assert "0" in d_rd["time_blocks"][0]["time_window"]
            assert "36" in d_rd["time_blocks"][-1]["time_window"]
            # Verify at least 20% buffer reserved (0.20 * 36 = 7.2 hours)
            assert d_rd["reserved_buffer_hours"] >= 7.2
            assert any(word in d_rd["time_blocks"][-1]["focus_milestone"].lower() for word in ["buffer", "freeze", "rehearsal"])
            assert len(d_rd["submission_checklist"]) >= 3


# ---------------------------------------------------------------------------
# Tests: Scenario 3 - Smart Agriculture Disease Detection (48h, 2 members)
# ---------------------------------------------------------------------------

MOCK_S3_TEAM = {
    "project_title": "AgriScan: 48h Crop Care",
    "team_size": 2,
    "member_assignments": [
        {
            "member_identifier": "Member 1 (AI & Backend Lead)",
            "assigned_role": "AI Engineer & API Developer",
            "key_responsibilities": ["FastAPI server", "PyTorch/TFLite model serving", "Local database"],
            "specific_tasks": ["Expose POST /diagnose endpoint", "Pre-load model weights", "Format disease remedies"],
            "expected_deliverables": ["Tested API returning diagnosis JSON under 500ms"]
        },
        {
            "member_identifier": "Member 2 (Frontend & Pitch Lead)",
            "assigned_role": "UI Engineer & Pitch Presenter",
            "key_responsibilities": ["React application", "Image upload UI", "Slide deck & pitch rehearsal"],
            "specific_tasks": ["Build camera capture & preview", "Display remedy treatment cards", "Design pitch deck"],
            "expected_deliverables": ["Polished responsive frontend & 3-minute pitch deck"]
        }
    ],
    "coordination_practices": [
        "Use Git feature branches",
        "Designate Member 2 as pitch lead starting at Hour 36"
    ]
}

MOCK_S3_PITCH = {
    "project_title": "AgriScan: 48h Crop Care",
    "pitch_30_seconds": "Every season, smallholder farmers lose 30% of crops to leaf diseases they can't diagnose in time. AgriScan turns any phone camera into an instant agronomist, giving accurate organic remedies in seconds with zero expensive hardware.",
    "pitch_1_minute": "In developing agricultural regions, access to plant pathologists is non-existent. Farmers rely on guesswork, applying harmful chemicals too late. AgriScan solves this with instant edge leaf image analysis. In our live demo today, a farmer snaps a diseased leaf; within 400 milliseconds, AgriScan diagnoses early blight and prescribes an organic treatment. We empower farmers to protect their harvest and their livelihood.",
    "pitch_3_minute": "0:00-0:40: Hook on global food security & farmer crop losses...\n0:40-1:50: Live Demonstration with actual leaf samples showing diagnosis & remedy...\n1:50-2:30: Technical Architecture: FastAPI async pipeline & MobileNet model...\n2:30-3:00: Scalability, open-source tech, and future multilingual roadmap.",
    "pitch_5_minute": "Detailed 5-minute pitch including market sizing, technical edge quantization deep-dive, live demo, business model, and social impact...",
    "live_demo_walkthrough": [
        "1. Open AgriScan mobile-responsive web UI on smartphone",
        "2. Upload leaf photo with visible fungal spot symptoms",
        "3. Watch instant classification: 'Tomato Early Blight - 94% Confidence'",
        "4. Display step-by-step organic neem-oil remedy instructions in local dialect"
    ],
    "technical_explanation": "MobileNetV3 convolutional neural network fine-tuned on PlantVillage dataset, quantized to 4MB for instant CPU inference, served via asynchronous FastAPI backend.",
    "innovation_explanation": "Combines lightweight edge inference with localized vernacular treatment advice rather than generic chemical recommendations.",
    "judge_qa_preparation": [
        {
            "anticipated_question": "How will farmers use this in remote fields without cellular data?",
            "suggested_answer": "Our frontend is a Progressive Web App (PWA) with cached model weights in IndexedDB, enabling 100% offline local inference in the field.",
            "highlight_aspect": "Offline Edge Feasibility"
        }
    ],
    "future_scope": [
        "IoT soil moisture and weather sensor telemetry integration",
        "Supply chain marketplace connecting farmers directly to organic suppliers"
    ]
}


@pytest.mark.asyncio
async def test_scenario_3_team_and_pitch():
    """Scenario 3: Verify 2-person team allocation and multi-tier pitch generation for 48h AgriTech hackathon."""
    with patch("backend.app.services.claude_service.AsyncAnthropic") as mock_anthropic:
        mock_instance = mock_anthropic.return_value
        with patch("backend.app.config.Settings.is_anthropic_configured", True):
            # Test /team: Verify parallelized delivery and designated demo/pitch owner
            mock_instance.messages.create = AsyncMock(return_value=make_mock_block(MOCK_S3_TEAM))
            r_tm = client.post("/api/hackathon/team", json=SCENARIO_3_INPUT)
            assert r_tm.status_code == 200
            d_tm = r_tm.json()
            assert d_tm["team_size"] == 2
            assert len(d_tm["member_assignments"]) == 2

            for m in d_tm["member_assignments"]:
                assert len(m["assigned_role"]) > 5
                assert len(m["key_responsibilities"]) >= 2
                assert len(m["specific_tasks"]) >= 2
                assert len(m["expected_deliverables"]) >= 1

            assert any("pitch" in m["assigned_role"].lower() or "pitch" in " ".join(m["key_responsibilities"]).lower() for m in d_tm["member_assignments"])
            assert len(d_tm["coordination_practices"]) >= 2

            # Test /pitch: Verify multi-tier pitches, demo walkthrough, and judge defense
            mock_instance.messages.create = AsyncMock(return_value=make_mock_block(MOCK_S3_PITCH))
            r_pt = client.post("/api/hackathon/pitch", json=SCENARIO_3_INPUT)
            assert r_pt.status_code == 200
            d_pt = r_pt.json()

            # Pitch duration progression checks
            assert 50 < len(d_pt["pitch_30_seconds"]) < 400
            assert len(d_pt["pitch_1_minute"]) > len(d_pt["pitch_30_seconds"])
            # 3-minute pitch uses timestamped sections, not necessarily longer in raw chars than 1-minute prose.
            # Assert it has multiple timestamped segments and covers key content areas.
            assert "0:00" in d_pt["pitch_3_minute"], "3-minute pitch must include timestamped structure"
            assert d_pt["pitch_3_minute"].count(":") >= 4, "3-minute pitch must have multiple timestamp markers"
            assert any(marker in d_pt["pitch_3_minute"].lower() for marker in ["demo", "architecture", "scope"])
            assert len(d_pt["pitch_5_minute"]) > 100

            # Demo walkthrough & Judge defense
            assert len(d_pt["live_demo_walkthrough"]) >= 4
            assert any("leaf" in step.lower() or "upload" in step.lower() for step in d_pt["live_demo_walkthrough"])
            assert len(d_pt["judge_qa_preparation"]) >= 1
            qa = d_pt["judge_qa_preparation"][0]
            assert len(qa["anticipated_question"]) > 10
            assert len(qa["suggested_answer"]) > 20
            assert len(qa["highlight_aspect"]) > 5
            assert len(d_pt["technical_explanation"]) > 30
            assert len(d_pt["innovation_explanation"]) > 30
            assert len(d_pt["future_scope"]) >= 2


MOCK_DEV_GUIDE = {
    "project_title": "AgriScan: 48h Crop Care",
    "recommended_tech_stack": [
        {
            "tech_name": "FastAPI",
            "category": "Backend Framework",
            "license_type": "Open-Source",
            "why_recommended": "Fastest async framework with auto-generated Swagger UI",
            "free_tier_limits": "100% Free / Self-hosted",
            "free_alternative": "Flask"
        },
        {
            "tech_name": "Vercel",
            "category": "Frontend Hosting",
            "license_type": "Freemium",
            "why_recommended": "Zero-config Git deployment for React with automated SSL",
            "free_tier_limits": "Hobby Free Tier (100GB bandwidth/month)",
            "free_alternative": "Localhost ngrok tunnel"
        },
        {
            "tech_name": "Enterprise Cloud GPU Cluster",
            "category": "Model Training",
            "license_type": "Paid",
            "why_recommended": "High-speed distributed model training if budget allows",
            "free_tier_limits": "No free tier ($1.20/hour)",
            "free_alternative": "Google Colab Free T4 GPU / Kaggle Kernels (30 hrs/wk free)"
        }
    ],
    "database_design_summary": "Minimal SQLite schema for storing disease classifications.",
    "suggested_api_endpoints": ["POST /api/diagnose (Accepts leaf image and returns classification)"],
    "integration_quickstart_guide": ["1. Start FastAPI backend", "2. Connect React frontend"],
    "copy_ready_claude_prompt": "Act as a Senior Python Engineer. I am participating in 'AgriTech Innovators Cup' with a 48 hours deadline. Write a production-ready asynchronous FastAPI route in backend/app/api/routes/diagnose.py that accepts a leaf image UploadFile, runs lightweight TFLite inference, validates with Pydantic schema, and returns disease severity with organic treatment recommendations. Include error handling for corrupt images and disconnected streams.",
    "copy_ready_antigravity_prompt": "Scaffold an end-to-end AgriTech hackathon MVP called 'AgriScan: 48h Crop Care' with a React frontend and FastAPI backend. Technical requirements: 1) Responsive camera capture component with mobile viewport, 2) Instant disease diagnosis badge with confidence percentage, 3) Step-by-step vernacular treatment remedy cards, and 4) Offline mock data fallback in IndexedDB if the network disconnects.",
    "testing_and_sanity_checks": ["Test /diagnose endpoint with curl before connecting frontend", "Verify model runs under 500ms on local CPU"],
    "deployment_plan": "Deploy on Render and Vercel free tiers."
}


@pytest.mark.asyncio
async def test_full_hackathon_strategy_endpoint():
    """Verify POST /api/hackathon/strategy coordinates all hackathon modules."""
    def mock_side_effect(*args, **kwargs):
        sys_prompt = kwargs.get("system", "")
        if "judging committee advisor" in sys_prompt.lower():
            return make_mock_block(MOCK_S1_ANALYSIS)
        elif "elite hackathon strategist" in sys_prompt.lower():
            return make_mock_block(MOCK_S1_IDEAS)
        elif "chief hackathon judge" in sys_prompt.lower():
            return make_mock_block(MOCK_S2_EVALUATION)
        elif "lean startup mvp architect" in sys_prompt.lower():
            return make_mock_block(MOCK_S2_MVP)
        elif "agile sprint master" in sys_prompt.lower():
            return make_mock_block(MOCK_S2_ROADMAP)
        elif "technical team lead" in sys_prompt.lower():
            return make_mock_block(MOCK_S3_TEAM)
        elif "practical full-stack ai engineer" in sys_prompt.lower():
            return make_mock_block(MOCK_DEV_GUIDE)
        else:
            return make_mock_block(MOCK_S3_PITCH)

    with patch("backend.app.services.claude_service.AsyncAnthropic") as mock_anthropic:
        mock_instance = mock_anthropic.return_value
        mock_instance.messages.create = AsyncMock(side_effect=mock_side_effect)

        with patch("backend.app.config.Settings.is_anthropic_configured", True):
            res = client.post("/api/hackathon/strategy", json=SCENARIO_1_INPUT)
            assert res.status_code == 200
            data = res.json()
            assert data["hackathon_name"] == "E-Commerce Trust Hack 2026"
            assert "analysis" in data
            assert len(data["ideas"]["ideas"]) >= 5
            assert "evaluation" in data
            assert "mvp_plan" in data
            assert "roadmap" in data
            assert "team_allocation" in data
            assert "development_guidance" in data
            assert "pitch_and_demo" in data
            assert "generated_at" in data["metadata"]


# ---------------------------------------------------------------------------
# Error Handling and Validation Tests
# ---------------------------------------------------------------------------

def test_hackathon_validation_errors():
    """Verify malformed requests return HTTP 422."""
    # Problem statement too short (< 15 chars)
    r1 = client.post("/api/hackathon/analyze", json={"problem_statement": "short"})
    assert r1.status_code == 422

    # Invalid team size (<= 0)
    r2 = client.post("/api/hackathon/analyze", json={"problem_statement": "A valid length hackathon statement.", "team_size": 0})
    assert r2.status_code == 422

    # Missing required problem_statement field
    r3 = client.post("/api/hackathon/analyze", json={"hackathon_name": "Hack 2026"})
    assert r3.status_code == 422

    # Team size exceeding maximum (> 10)
    r4 = client.post("/api/hackathon/analyze", json={"problem_statement": "A valid length hackathon statement.", "team_size": 15})
    assert r4.status_code == 422


def test_hackathon_optional_budget_handling():
    """Verify that omitting budget or setting budget to None works cleanly."""
    with patch("backend.app.services.claude_service.AsyncAnthropic") as mock_anthropic:
        mock_instance = mock_anthropic.return_value
        with patch("backend.app.config.Settings.is_anthropic_configured", True):
            mock_instance.messages.create = AsyncMock(return_value=make_mock_block(MOCK_S1_ANALYSIS))

            # 1. Budget completely omitted from payload
            payload_no_budget = {
                "hackathon_name": "No Budget Hack",
                "problem_statement": "Valid problem statement text explaining the challenge to solve.",
                "duration": "24 hours",
                "team_size": 3
            }
            res1 = client.post("/api/hackathon/analyze", json=payload_no_budget)
            assert res1.status_code == 200

            # 2. Budget explicitly passed as None
            payload_none_budget = {**payload_no_budget, "budget": None}
            res2 = client.post("/api/hackathon/analyze", json=payload_none_budget)
            assert res2.status_code == 200


@pytest.mark.asyncio
async def test_scenario_3_free_first_tech_and_prompts():
    """Scenario 3: Verify free-first technology advisor and copy-ready prompts."""
    with patch("backend.app.services.claude_service.AsyncAnthropic") as mock_anthropic:
        mock_instance = mock_anthropic.return_value
        with patch("backend.app.config.Settings.is_anthropic_configured", True):
            mock_instance.messages.create = AsyncMock(return_value=make_mock_block(MOCK_DEV_GUIDE))

            # Test dedicated dev-guidance endpoint
            res = client.post("/api/hackathon/dev-guidance", json=SCENARIO_3_INPUT)
            assert res.status_code == 200
            data = res.json()

            # 1. Verify Free/Open-Source tools prioritized
            open_source_tools = [t for t in data["recommended_tech_stack"] if t["license_type"] in ["Free", "Open-Source"]]
            assert len(open_source_tools) >= 1, "Must prioritize free/open-source tools"
            assert open_source_tools[0]["tech_name"] == "FastAPI"

            # 2. Verify Freemium tools with documented free tiers
            freemium_tools = [t for t in data["recommended_tech_stack"] if t["license_type"] == "Freemium"]
            assert len(freemium_tools) >= 1
            assert len(freemium_tools[0]["free_tier_limits"]) > 10

            # 3. Verify Paid tools are explicitly labelled and supply free alternatives
            paid_tools = [t for t in data["recommended_tech_stack"] if t["license_type"] == "Paid"]
            assert len(paid_tools) >= 1, "Must explicitly label paid tools"
            for pt in paid_tools:
                assert pt["free_alternative"] is not None and len(pt["free_alternative"]) > 10, "Paid tools must provide actionable free alternatives"

            # 4. Verify Claude prompt contains real project context & technical requirements
            claude_prompt = data["copy_ready_claude_prompt"]
            assert "agritech innovators cup" in claude_prompt.lower()
            assert "48 hours" in claude_prompt.lower()
            assert "fastapi" in claude_prompt.lower()
            assert "pydantic" in claude_prompt.lower()
            assert "tflite" in claude_prompt.lower() or "inference" in claude_prompt.lower()
            assert len(claude_prompt) > 100, "Claude prompt must be rich and actionable"

            # 5. Verify Antigravity prompt contains UI & MVP requirements
            antigravity_prompt = data["copy_ready_antigravity_prompt"]
            assert "agriscan" in antigravity_prompt.lower()
            assert "react" in antigravity_prompt.lower()
            assert "camera" in antigravity_prompt.lower()
            assert "offline" in antigravity_prompt.lower()
            assert len(antigravity_prompt) > 100, "Antigravity prompt must be rich and actionable"

            # 6. Verify Testing & Deployment Guidance
            assert len(data["testing_and_sanity_checks"]) >= 2
            assert "Render" in data["deployment_plan"]


def test_hackathon_unconfigured_credentials():
    """Verify HTTP 503 is returned when API key is missing."""
    with patch("backend.app.config.Settings.is_anthropic_configured", False):
        endpoints = [
            "/api/hackathon/analyze",
            "/api/hackathon/ideas",
            "/api/hackathon/evaluate",
            "/api/hackathon/mvp",
            "/api/hackathon/roadmap",
            "/api/hackathon/team",
            "/api/hackathon/pitch",
            "/api/hackathon/strategy"
        ]
        for ep in endpoints:
            res = client.post(ep, json=SCENARIO_1_INPUT)
            assert res.status_code == 503
            assert res.json()["detail"]["error"] == "ai_service_unconfigured"
