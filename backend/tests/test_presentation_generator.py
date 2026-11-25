"""
Phase 8 — Automated Documentation & PowerPoint Generator Tests.

Verifies:
- 10-slide OOXML valid PowerPoint archive generation
- Presence of required OOXML parts: [Content_Types].xml, presentation.xml, slides 1-10
- 15-section IEEE academic thesis report compilation
- FastAPI endpoints for presentation and report downloads
"""

import io
import zipfile
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.pptx_generator import PresentationGenerator
from backend.app.services.report_generator import AcademicReportGenerator


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


SAMPLE_PROJECT = {
    "title": "AI Construction Safety Monitoring",
    "domain": "AI / Machine Learning",
    "author": "Capstone Team 3",
    "institution": "National Engineering Institute",
    "analysis": {
        "problem_statement": "Manual inspections on construction sites lead to missed safety violations.",
        "proposed_solution": "Computer vision pipeline detecting hard hats and vests in real-time.",
        "unique_selling_proposition": "Multi-agent autonomous guidance with free-first tooling.",
        "main_objectives": [
            "Real-time video feed ingestion",
            "YOLO detection model for PPE compliance",
            "Instant alert dispatcher",
        ],
        "existing_limitations": ["Human latency", "High accident rates"],
        "expected_outcomes": ["Sub-100ms inference", "Reduced job-site accidents"],
    },
    "technology_stack": {
        "summary": "Free-first stack with Python, React, and SQLite.",
        "technologies": [
            {"tech_name": "FastAPI", "category": "Backend", "role": "REST API"},
            {"tech_name": "React 19", "category": "Frontend", "role": "UI"},
            {"tech_name": "SQLite", "category": "Database", "role": "Storage"},
        ],
    },
    "architecture": {
        "architecture_pattern": "Modular Monolith",
        "frontend_layer": "React + Tailwind",
        "backend_layer": "FastAPI Async",
        "data_layer": "SQLite Relational",
        "mermaid_diagram": "graph TD\\n    A --> B",
    },
}


def test_generate_pptx_package_structure():
    """Verify that generated PPTX is a valid OOXML ZIP with 10 slides."""
    pptx_bytes = PresentationGenerator.generate_project_pptx(SAMPLE_PROJECT)
    assert isinstance(pptx_bytes, bytes)
    assert len(pptx_bytes) > 1000

    # Parse as ZIP archive
    with zipfile.ZipFile(io.BytesIO(pptx_bytes), "r") as zf:
        namelist = zf.namelist()
        assert "[Content_Types].xml" in namelist
        assert "_rels/.rels" in namelist
        assert "ppt/presentation.xml" in namelist
        assert "ppt/theme/theme1.xml" in namelist

        # Exactly 10 slides
        for i in range(1, 11):
            assert f"ppt/slides/slide{i}.xml" in namelist

        # Verify slide content
        slide1_xml = zf.read("ppt/slides/slide1.xml").decode("utf-8")
        assert "AI Construction Safety Monitoring" in slide1_xml
        assert "Capstone Team 3" in slide1_xml


def test_generate_academic_report():
    """Verify that generated academic report contains all 15 required sections."""
    report = AcademicReportGenerator.generate_markdown_report(SAMPLE_PROJECT)
    assert isinstance(report, str)
    assert len(report) > 500

    required_sections = [
        "1. Abstract",
        "2. Problem Statement",
        "3. Project Objectives",
        "4. Existing System & Limitations",
        "5. Proposed System & Innovation",
        "6. Technology Stack & Free-First Tooling",
        "7. System Architecture & Topology",
        "8. Main Module Descriptions",
        "9. Database Design & Entity Relationships",
        "10. Implementation Methodology",
        "11. Testing & Quality Assurance Strategy",
        "12. Expected Outcomes & Experimental Results",
        "13. Future Enhancements",
        "14. Academic Conclusion",
        "15. References & Literature Review",
    ]

    for section in required_sections:
        assert section in report, f"Missing section: {section}"

    assert "AI Construction Safety Monitoring" in report
    assert "YOLO detection model for PPE compliance" in report


def test_presentation_endpoints(client: TestClient):
    """Verify PPTX and Report export REST endpoints."""
    # 1. Download PPTX endpoint
    pptx_resp = client.post(
        "/api/presentation/generate-pptx",
        json=SAMPLE_PROJECT,
    )
    assert pptx_resp.status_code == 200
    assert "application/vnd.openxmlformats-officedocument.presentationml.presentation" in pptx_resp.headers["content-type"]
    assert len(pptx_resp.content) > 1000

    # 2. Download Markdown report endpoint
    report_resp = client.post(
        "/api/presentation/generate-report",
        json=SAMPLE_PROJECT,
    )
    assert report_resp.status_code == 200
    assert "text/markdown" in report_resp.headers["content-type"]
    assert "1. Abstract" in report_resp.text
