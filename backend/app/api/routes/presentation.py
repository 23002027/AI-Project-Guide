"""
Presentation & Academic Report Export Routes (Phase 8).

Provides downloadable 10-slide PowerPoint presentations (.pptx)
and 15-section IEEE-aligned academic thesis reports (.md).
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Response, HTTPException
from pydantic import BaseModel, Field

from backend.app.services.pptx_generator import PresentationGenerator
from backend.app.services.report_generator import AcademicReportGenerator

router = APIRouter(prefix="/presentation", tags=["Presentation & Documentation"])


class GeneratePPTXRequest(BaseModel):
    title: str = Field(default="AI Project & Hackathon Co-Pilot")
    domain: Optional[str] = Field(default="AI / Machine Learning")
    author: Optional[str] = Field(default="Student Engineering Team")
    institution: Optional[str] = Field(default="National Engineering Institute")
    analysis: Optional[Dict[str, Any]] = Field(default_factory=dict)
    technology_stack: Optional[Dict[str, Any]] = Field(default_factory=dict)
    architecture: Optional[Dict[str, Any]] = Field(default_factory=dict)
    roadmap: Optional[Dict[str, Any]] = Field(default_factory=dict)


@router.post("/generate-pptx")
async def generate_pptx_endpoint(req: GeneratePPTXRequest):
    """
    Generate an editable 10-slide Microsoft PowerPoint (.pptx) file.
    Returns binary OOXML presentation stream ready for download.
    """
    try:
        pptx_bytes = PresentationGenerator.generate_project_pptx(req.model_dump())
        filename = f"{req.title.lower().replace(' ', '_')[:30]}_defense.pptx"

        return Response(
            content=pptx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to generate presentation: {str(exc)}")


@router.post("/generate-report")
async def generate_report_endpoint(req: GeneratePPTXRequest):
    """
    Generate a 15-section academic capstone / viva defense report in Markdown.
    """
    try:
        report_md = AcademicReportGenerator.generate_markdown_report(req.model_dump())
        filename = f"{req.title.lower().replace(' ', '_')[:30]}_report.md"

        return Response(
            content=report_md,
            media_type="text/markdown",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(exc)}")
