"""
Coding Assistance Routes (Phase 9).

Provides module-wise starter code generation, stack-trace error diagnosis,
and unit test scaffolding.
"""

from fastapi import APIRouter, HTTPException
from backend.app.schemas.coding_assistant import (
    CodeGenerateRequest,
    CodeGenerateResponse,
    CodeDebugRequest,
    CodeDebugResponse,
)
from backend.app.services.code_assistant import CodeAssistantService

router = APIRouter(prefix="/coding", tags=["Coding Assistance"])


@router.post("/generate", response_model=CodeGenerateResponse)
async def generate_starter_code(req: CodeGenerateRequest):
    """Generate production-ready starter code and unit tests for a specific module."""
    try:
        service = CodeAssistantService()
        return await service.generate_starter_code(req)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to generate code: {str(exc)}")


@router.post("/debug", response_model=CodeDebugResponse)
async def debug_code(req: CodeDebugRequest):
    """Analyze code snippet and error traceback to return root cause and drop-in fix."""
    try:
        service = CodeAssistantService()
        return await service.debug_code(req)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to debug code: {str(exc)}")
