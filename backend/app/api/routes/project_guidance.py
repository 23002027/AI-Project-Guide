"""
Project Guidance API Endpoints (Phase 3).
Dedicated routes for deep project analysis, technology advising,
architecture diagrams, roadmaps, coding walkthroughs, academic documentation,
and full blueprints.
"""

import asyncio
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status

logger = logging.getLogger("project_guidance_routes")

from backend.app.schemas.project_guidance import (
    ProjectIdeaInput,
    ProjectAnalysisResponse,
    TechStackAdvisorResponse,
    ArchitectureGeneratorResponse,
    DevelopmentRoadmapResponse,
    AICodingPromptsResponse,
    ProjectDocumentationResponse,
    FullProjectBlueprintResponse,
)
from backend.app.services.claude_service import (
    AnthropicNotConfiguredError,
    AnthropicServiceError,
    InvalidAIResponseError,
)
from backend.app.services.project_analyzer import ProjectAnalyzerService
from backend.app.services.technology_advisor import TechnologyAdvisorService
from backend.app.services.architecture_generator import ArchitectureGeneratorService
from backend.app.services.roadmap_generator import RoadmapGeneratorService
from backend.app.services.coding_prompt_generator import CodingPromptGeneratorService
from backend.app.services.documentation_generator import DocumentationGeneratorService

router = APIRouter(prefix="/project", tags=["Project Guidance"])


def _handle_service_exceptions(err: Exception) -> HTTPException:
    """Helper to convert domain exceptions to appropriate HTTP errors."""
    err_msg = str(err)
    if "Ollama" in err_msg and ("unavailable" in err_msg.lower() or "cannot connect" in err_msg.lower() or "not running" in err_msg.lower()):
        logger.error("[LLM-GUIDANCE] ❌ LLM NOT WORKING | Ollama unavailable: %s", err_msg)
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "ollama_unavailable",
                "message": err_msg,
                "resolution": (
                    "Start Ollama: open a terminal and run `ollama serve`. "
                    "Then verify the model is downloaded: `ollama pull qwen3:4b`. "
                    "Check GPU usage: `ollama ps`."
                )
            }
        )
    if isinstance(err, AnthropicNotConfiguredError):
        logger.error("[LLM-GUIDANCE] ❌ LLM NOT CONFIGURED: %s", err_msg)
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "ai_service_unconfigured",
                "message": str(err),
                "resolution": "Set AI_PROVIDER=ollama and ensure Ollama is running, or add a valid API key."
            }
        )
    if isinstance(err, AnthropicServiceError):
        logger.error("[LLM-GUIDANCE] ❌ LLM SERVICE ERROR: %s", err_msg)
        return HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "error": "ai_api_error",
                "message": str(err)
            }
        )
    if isinstance(err, InvalidAIResponseError):
        logger.error("[LLM-GUIDANCE] ❌ LLM PARSE/VALIDATION ERROR: %s", err_msg)
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "ai_response_parse_error",
                "message": str(err)
            }
        )
    logger.error("[LLM-GUIDANCE] ❌ UNEXPECTED ERROR: %s", err_msg)
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={
            "error": "unexpected_error",
            "message": f"An unexpected error occurred: {str(err)}"
        }
    )


@router.post(
    "/analyze",
    response_model=ProjectAnalysisResponse,
    summary="Analyze project idea and formulate problem statement",
    description="Evaluates limitations of existing work, proposed solution, objectives, USP, feasibility, and complexity."
)
async def analyze_project_idea(payload: ProjectIdeaInput) -> ProjectAnalysisResponse:
    service = ProjectAnalyzerService()
    try:
        return await service.analyze_project(payload)
    except Exception as err:
        raise _handle_service_exceptions(err)


@router.post(
    "/technology-stack",
    response_model=TechStackAdvisorResponse,
    summary="Recommend optimal technology stack and AI tools",
    description="Recommends frontend, backend, database, AI models, auth, hosting, and AI developer tools with pricing and role details."
)
@router.post(
    "/tech-stack",
    response_model=TechStackAdvisorResponse,
    include_in_schema=False
)
async def recommend_technologies(payload: ProjectIdeaInput) -> TechStackAdvisorResponse:
    service = TechnologyAdvisorService()
    try:
        return await service.recommend_tech_stack(payload)
    except Exception as err:
        raise _handle_service_exceptions(err)


@router.post(
    "/architecture",
    response_model=ArchitectureGeneratorResponse,
    summary="Generate system architecture and Mermaid diagram",
    description="Designs multi-tier system architecture, API suggestions, data flow, and Mermaid flowchart syntax."
)
async def generate_architecture(payload: ProjectIdeaInput) -> ArchitectureGeneratorResponse:
    service = ArchitectureGeneratorService()
    try:
        return await service.generate_architecture(payload)
    except Exception as err:
        raise _handle_service_exceptions(err)


@router.post(
    "/roadmap",
    response_model=DevelopmentRoadmapResponse,
    summary="Generate 9-phase development roadmap and deployment guide",
    description="Builds phased roadmap from research to deployment and testing, adapted to student deadlines."
)
async def generate_roadmap(payload: ProjectIdeaInput) -> DevelopmentRoadmapResponse:
    service = RoadmapGeneratorService()
    try:
        return await service.generate_roadmap(payload)
    except Exception as err:
        raise _handle_service_exceptions(err)


@router.post(
    "/coding-prompts",
    response_model=AICodingPromptsResponse,
    summary="Generate module-wise coding steps and copy-ready AI prompts",
    description="Provides module walkthroughs and ready-to-use prompts for Claude, Antigravity, GitHub Copilot, and Cursor."
)
async def generate_coding_prompts(payload: ProjectIdeaInput) -> AICodingPromptsResponse:
    service = CodingPromptGeneratorService()
    try:
        return await service.generate_coding_prompts(payload)
    except Exception as err:
        raise _handle_service_exceptions(err)


@router.post(
    "/documentation",
    response_model=ProjectDocumentationResponse,
    summary="Generate final-year academic report synopsis",
    description="Drafts academic abstract, literature review framework, objectives, methodology, and future scope without fabricated citations."
)
async def generate_documentation(payload: ProjectIdeaInput) -> ProjectDocumentationResponse:
    service = DocumentationGeneratorService()
    try:
        return await service.generate_documentation(payload)
    except Exception as err:
        raise _handle_service_exceptions(err)


@router.post(
    "/full-blueprint",
    response_model=FullProjectBlueprintResponse,
    summary="Generate master project blueprint (all dimensions)",
    description="Coordinates all guidance services concurrently using asyncio.gather to deliver a complete project development blueprint."
)
async def generate_full_blueprint(payload: ProjectIdeaInput) -> FullProjectBlueprintResponse:
    analyzer = ProjectAnalyzerService()
    tech_advisor = TechnologyAdvisorService()
    arch_gen = ArchitectureGeneratorService()
    roadmap_gen = RoadmapGeneratorService()
    coding_gen = CodingPromptGeneratorService()
    doc_gen = DocumentationGeneratorService()

    try:
        analysis, tech_stack, arch, roadmap, coding_prompts, doc = await asyncio.gather(
            analyzer.analyze_project(payload),
            tech_advisor.recommend_tech_stack(payload),
            arch_gen.generate_architecture(payload),
            roadmap_gen.generate_roadmap(payload),
            coding_gen.generate_coding_prompts(payload),
            doc_gen.generate_documentation(payload),
        )

        return FullProjectBlueprintResponse(
            project_title=payload.title,
            analysis=analysis,
            technology_stack=tech_stack,
            architecture=arch,
            roadmap=roadmap,
            coding_and_prompts=coding_prompts,
            coding_prompts=coding_prompts,
            documentation=doc,
            metadata={
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "domain": payload.domain.value,
                "deadline": payload.deadline,
            }
        )
    except Exception as err:
        raise _handle_service_exceptions(err)
