"""
AI Planning API Endpoints
Provides route handlers for project idea analysis, architecture recommendations,
and hackathon MVP planning.
"""

import logging
from fastapi import APIRouter, HTTPException, status
from backend.app.schemas.ai_plan import PlanRequest, PlanResponse
from backend.app.services.claude_service import (
    ClaudeService,
    AnthropicNotConfiguredError,
    AnthropicServiceError,
    InvalidAIResponseError,
)

logger = logging.getLogger("ai_plan_route")

router = APIRouter(prefix="/ai", tags=["AI Planning"])


@router.post(
    "/plan",
    response_model=PlanResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate a comprehensive Project or Hackathon plan",
    description="Analyzes an idea/problem statement and generates tech recommendations, system architecture, development roadmap, and (in hackathon mode) MVP scoping, task allocation, and judging alignment.",
)
async def create_ai_plan(payload: PlanRequest) -> PlanResponse:
    """
    Endpoint accepting user constraints and returning a structured AI-engineered project plan.
    """
    logger.info("[LLM-AI-PLAN] Incoming plan request: '%s' (mode: %s)", payload.idea[:60] if payload.idea else "No Idea", payload.mode.value)
    service = ClaudeService()

    try:
        plan = await service.generate_plan(payload)
        logger.info("[LLM-AI-PLAN] ✅ Plan generated successfully for '%s'", plan.project_title)
        return plan

    except AnthropicNotConfiguredError as err:
        logger.error("[LLM-AI-PLAN] ❌ LLM NOT CONFIGURED: %s", err)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "ai_service_unconfigured",
                "message": str(err),
                "resolution": "Add a valid ANTHROPIC_API_KEY to your .env file."
            }
        )

    except AnthropicServiceError as err:
        logger.error("[LLM-AI-PLAN] ❌ LLM SERVICE ERROR: %s", err)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "error": "anthropic_api_error",
                "message": str(err)
            }
        )

    except InvalidAIResponseError as err:
        logger.error("[LLM-AI-PLAN] ❌ LLM PARSE/VALIDATION ERROR: %s", err)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "ai_response_parse_error",
                "message": str(err)
            }
        )

    except Exception as err:
        logger.error("[LLM-AI-PLAN] ❌ UNEXPECTED ERROR: %s", err)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "unexpected_error",
                "message": f"An unexpected error occurred while generating the plan: {str(err)}"
            }
        )
