"""
Health check endpoints for system uptime, diagnostics, and monitoring.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional, Any, Dict
from fastapi import APIRouter
from pydantic import BaseModel
from ...config import get_settings

logger = logging.getLogger("health_route")

router = APIRouter(prefix="/health", tags=["Health"])


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    environment: str
    timestamp: str
    ai_configured: bool
    ai_model: str
    ai_provider: Optional[str] = None
    anthropic_configured: Optional[bool] = False
    # Ollama-specific fields (only populated when AI_PROVIDER=ollama)
    ollama_reachable: Optional[bool] = None
    ollama_model_available: Optional[bool] = None
    ollama_gpu_info: Optional[Dict[str, Any]] = None


@router.get("", response_model=HealthResponse)
@router.get("/", response_model=HealthResponse, include_in_schema=False)
async def get_health_status() -> HealthResponse:
    """
    Returns the operational status of the backend API.
    When AI_PROVIDER=ollama, performs a live connectivity check to the local Ollama instance.
    """
    settings = get_settings()

    ollama_reachable = None
    ollama_model_available = None
    ollama_gpu_info = None

    if settings.AI_PROVIDER == "ollama":
        try:
            from backend.app.services.ollama_service import OllamaService
            svc = OllamaService()
            conn = await asyncio.wait_for(svc.check_connection(), timeout=5.0)
            ollama_reachable = conn.get("reachable", False)
            ollama_model_available = conn.get("model_available", False)
            ollama_gpu_info = conn.get("gpu_info")
            if ollama_reachable and ollama_model_available:
                logger.info("[LLM-HEALTH] ✅ LLM IS WORKING | Provider: ollama | Model: %s | Reachable: True | Available: True", settings.OLLAMA_MODEL)
            elif ollama_reachable:
                logger.warning("[LLM-HEALTH] ⚠️  Ollama reachable but target model '%s' not loaded", settings.OLLAMA_MODEL)
            else:
                logger.error("[LLM-HEALTH] ❌ LLM NOT WORKING | Ollama service unreachable at %s", settings.OLLAMA_BASE_URL)
        except Exception as exc:
            ollama_reachable = False
            ollama_model_available = False
            logger.error("[LLM-HEALTH] ❌ LLM NOT WORKING | Health probe exception: %s", exc)
    else:
        logger.info(
            "[LLM-HEALTH] Provider: %s | Primary Model: %s | AI Configured: %s",
            settings.AI_PROVIDER,
            settings.primary_model,
            settings.is_ai_configured,
        )

    return HealthResponse(
        status="ok",
        service=settings.PROJECT_NAME,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        timestamp=datetime.now(timezone.utc).isoformat(),
        ai_configured=settings.is_ai_configured,
        ai_model=settings.primary_model,
        ai_provider=settings.AI_PROVIDER,
        anthropic_configured=settings.is_anthropic_configured,
        ollama_reachable=ollama_reachable,
        ollama_model_available=ollama_model_available,
        ollama_gpu_info=ollama_gpu_info,
    )
