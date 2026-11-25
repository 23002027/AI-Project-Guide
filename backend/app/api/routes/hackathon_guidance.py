"""
Hackathon Guidance API Endpoints (Phase 4).
Dedicated routes for hackathon problem analysis, multi-idea generation,
weighted idea evaluation, MVP scoping, hourly roadmaps,
team task distribution, pitch generation, and full strategies.
"""

from fastapi import APIRouter, HTTPException, status

from backend.app.schemas.hackathon_guidance import (
    HackathonInput,
    HackathonAnalysisResponse,
    HackathonIdeasResponse,
    IdeaEvaluationResponse,
    MVPPlanResponse,
    HackathonRoadmapResponse,
    TeamAllocationResponse,
    HackathonDevGuidanceResponse,
    PitchAndDemoResponse,
    FullHackathonStrategyResponse,
)
from backend.app.services.claude_service import (
    AnthropicNotConfiguredError,
    AnthropicServiceError,
    InvalidAIResponseError,
)
from backend.app.services.hackathon_service import HackathonService

router = APIRouter(prefix="/hackathon", tags=["Hackathon Guidance"])


def _handle_service_exceptions(err: Exception) -> HTTPException:
    """Helper to convert domain exceptions to appropriate HTTP errors."""
    if isinstance(err, AnthropicNotConfiguredError):
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "ai_service_unconfigured",
                "message": str(err),
                "resolution": "Add a valid ANTHROPIC_API_KEY to your .env file."
            }
        )
    if isinstance(err, AnthropicServiceError):
        return HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "error": "anthropic_api_error",
                "message": str(err)
            }
        )
    if isinstance(err, InvalidAIResponseError):
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "ai_response_parse_error",
                "message": str(err)
            }
        )
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={
            "error": "unexpected_error",
            "message": f"An unexpected error occurred during hackathon guidance: {str(err)}"
        }
    )


@router.post(
    "/analyze",
    response_model=HackathonAnalysisResponse,
    summary="Analyze hackathon problem statement",
    description="Deconstructs the problem statement, user personas, existing challenges, core requirements, constraints, and innovation angles."
)
async def analyze_hackathon_problem(payload: HackathonInput) -> HackathonAnalysisResponse:
    service = HackathonService()
    try:
        return await service.analyze_problem(payload)
    except Exception as err:
        raise _handle_service_exceptions(err)


@router.post(
    "/ideas",
    response_model=HackathonIdeasResponse,
    summary="Generate 5+ distinct hackathon project ideas",
    description="Brainstorms at least five genuinely different, high-impact concepts tailored to the team's skills and timeframe."
)
async def generate_hackathon_ideas(payload: HackathonInput) -> HackathonIdeasResponse:
    service = HackathonService()
    try:
        return await service.generate_ideas(payload)
    except Exception as err:
        raise _handle_service_exceptions(err)


@router.post(
    "/evaluate",
    response_model=IdeaEvaluationResponse,
    summary="Evaluate and rank hackathon ideas",
    description="Scores ideas across Relevance, Innovation, Feasibility, Impact, Demo, and Time using official or default balanced weights, recommending the strongest concept."
)
async def evaluate_hackathon_ideas(payload: HackathonInput) -> IdeaEvaluationResponse:
    service = HackathonService()
    try:
        return await service.evaluate_ideas(payload)
    except Exception as err:
        raise _handle_service_exceptions(err)


@router.post(
    "/mvp",
    response_model=MVPPlanResponse,
    summary="Generate MoSCoW MVP plan & demo flow",
    description="Divides features into Must-Have, Should-Have, and Nice-to-Have, outlining a 3-step live demo flow and failure mitigations."
)
async def plan_hackathon_mvp(payload: HackathonInput) -> MVPPlanResponse:
    service = HackathonService()
    try:
        return await service.plan_mvp(payload)
    except Exception as err:
        raise _handle_service_exceptions(err)


@router.post(
    "/roadmap",
    response_model=HackathonRoadmapResponse,
    summary="Generate time-boxed hourly development schedule",
    description="Calculates milestone time windows calibrated to hackathon duration, reserving explicit buffer time for integration, testing, and pitch rehearsal."
)
async def generate_hackathon_roadmap(payload: HackathonInput) -> HackathonRoadmapResponse:
    service = HackathonService()
    try:
        return await service.generate_roadmap(payload)
    except Exception as err:
        raise _handle_service_exceptions(err)


@router.post(
    "/team",
    response_model=TeamAllocationResponse,
    summary="Allocate tasks across team members",
    description="Maps team member skills to parallelized responsibilities, tasks, and deliverables, designating a Demo/Pitch owner."
)
async def allocate_hackathon_team(payload: HackathonInput) -> TeamAllocationResponse:
    service = HackathonService()
    try:
        return await service.allocate_team(payload)
    except Exception as err:
        raise _handle_service_exceptions(err)


@router.post(
    "/pitch",
    response_model=PitchAndDemoResponse,
    summary="Generate multi-duration pitch scripts & demo defense",
    description="Creates 30s, 1-min, 3-min, and 5-min pitch scripts, a 2-minute live demo sequence, and anticipated judge Q&A defense."
)
async def generate_hackathon_pitch(payload: HackathonInput) -> PitchAndDemoResponse:
    service = HackathonService()
    try:
        return await service.generate_pitch(payload)
    except Exception as err:
        raise _handle_service_exceptions(err)


@router.post(
    "/dev-guidance",
    response_model=HackathonDevGuidanceResponse,
    summary="Generate free-first tech recommendations & copy-ready prompts",
    description="Recommends free/open-source stacks, database schemas, and copy-ready prompts for Claude and Antigravity."
)
async def generate_hackathon_dev_guidance(payload: HackathonInput) -> HackathonDevGuidanceResponse:
    service = HackathonService()
    try:
        return await service.generate_dev_guidance(payload)
    except Exception as err:
        raise _handle_service_exceptions(err)


@router.post(
    "/strategy",
    response_model=FullHackathonStrategyResponse,
    summary="Generate complete end-to-end hackathon strategy",
    description="Asynchronously coordinates all guidance dimensions into an integrated winning game plan."
)
@router.post(
    "/full-strategy",
    response_model=FullHackathonStrategyResponse,
    include_in_schema=False
)
async def generate_full_hackathon_strategy(payload: HackathonInput) -> FullHackathonStrategyResponse:
    service = HackathonService()
    try:
        return await service.generate_full_strategy(payload)
    except Exception as err:
        raise _handle_service_exceptions(err)
