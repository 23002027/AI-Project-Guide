"""
API routes for multi-agent orchestration.

Endpoints
---------
POST /api/agent/run          — Start or resume a multi-agent workflow session
GET  /api/agent/status/{id}  — Get current state of a session
GET  /api/agent/history/{id} — Get completed agent steps for a session
POST /api/agent/approve/{id} — Approve a pending agent step
POST /api/agent/retry/{id}   — Retry a failed agent step
"""

from __future__ import annotations

from typing import Any, Dict, Literal, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.app.agents.orchestrator import (
    run_workflow,
    get_session,
    approve_session,
)
from backend.app.config import get_settings

router = APIRouter(prefix="/api/agent", tags=["Multi-Agent Orchestration"])


# ── Request / Response models ─────────────────────────────────────────────────

class WorkflowRunRequest(BaseModel):
    workflow_type: Literal["project", "hackathon", "full_project", "full_hackathon"] = Field(
        default="project",
        description="Which agent chain to execute."
    )
    user_input: Dict[str, Any] = Field(
        description="Project or hackathon input fields (matches ProjectInput or HackathonInput)."
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Existing session ID to resume; omit to create a new session."
    )


class WorkflowRunResponse(BaseModel):
    session_id: str
    workflow_type: str
    completed_agents: list
    pending_approval: bool
    approval_target: Optional[str]
    error: Optional[str]
    results: Dict[str, Any]


class ApprovalResponse(BaseModel):
    session_id: str
    approved: bool
    message: str


# ── Helper ────────────────────────────────────────────────────────────────────

def _session_to_response(state: dict) -> WorkflowRunResponse:
    """Extract only the result fields from raw state."""
    result_keys = [
        # Project Guidance Agent outputs
        "project_analysis", "technology_stack", "architecture",
        "roadmap", "coding_prompts", "documentation", "test_plan",
        # Hackathon Guidance Agent outputs
        "hackathon_analysis", "generated_ideas", "idea_evaluation",
        "mvp_plan", "team_allocation", "dev_guidance", "pitch",
    ]
    return WorkflowRunResponse(
        session_id=state.get("session_id", ""),
        workflow_type=state.get("workflow_type", ""),
        completed_agents=state.get("completed_agents", []),
        pending_approval=state.get("pending_approval", False),
        approval_target=state.get("approval_target"),
        error=state.get("error"),
        results={k: state.get(k) for k in result_keys if state.get(k) is not None},
    )


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/run", response_model=WorkflowRunResponse)
async def run_agent_workflow(request: WorkflowRunRequest):
    """
    Start or resume a multi-agent workflow.

    The supervisor automatically routes to the correct chain of specialized
    agents based on `workflow_type`.  Returns the aggregated results of all
    completed agents plus the session ID for future status/approval calls.
    """
    current_settings = get_settings()
    if not current_settings.is_anthropic_configured:
        raise HTTPException(
            status_code=503,
            detail={"error": "ai_service_unconfigured",
                    "message": "ANTHROPIC_API_KEY is not set. Add it to your .env file."},
        )
    try:
        final_state = await run_workflow(
            workflow_type=request.workflow_type,
            user_input=request.user_input,
            session_id=request.session_id,
        )
        return _session_to_response(final_state)
    except Exception as exc:
        raise HTTPException(status_code=500, detail={"error": "workflow_failed", "message": str(exc)})


@router.get("/status/{session_id}", response_model=WorkflowRunResponse)
async def get_workflow_status(session_id: str):
    """Return the current state of a workflow session."""
    state = get_session(session_id)
    if state is None:
        raise HTTPException(status_code=404, detail={"error": "session_not_found",
                                                      "message": f"Session '{session_id}' does not exist."})
    return _session_to_response(state)


@router.get("/history/{session_id}")
async def get_workflow_history(session_id: str):
    """Return completed agent steps for a session."""
    state = get_session(session_id)
    if state is None:
        raise HTTPException(status_code=404, detail={"error": "session_not_found",
                                                      "message": f"Session '{session_id}' does not exist."})
    return {
        "session_id": session_id,
        "workflow_type": state.get("workflow_type"),
        "completed_agents": state.get("completed_agents", []),
        "current_agent": state.get("current_agent"),
        "error": state.get("error"),
    }


@router.post("/approve/{session_id}", response_model=ApprovalResponse)
async def approve_workflow_step(session_id: str):
    """
    Approve a pending agent step.

    When an agent that requires approval (e.g., architecture, roadmap) is
    reached, the workflow pauses and sets `pending_approval=True`.  Call this
    endpoint to grant approval and allow the graph to continue.
    """
    state = get_session(session_id)
    if state is None:
        raise HTTPException(status_code=404, detail={"error": "session_not_found",
                                                      "message": f"Session '{session_id}' does not exist."})
    approved = approve_session(session_id)
    if not approved:
        return ApprovalResponse(
            session_id=session_id,
            approved=False,
            message="No pending approval found for this session.",
        )
    return ApprovalResponse(
        session_id=session_id,
        approved=True,
        message=f"Approved. Resume the workflow by calling POST /api/agent/run with session_id='{session_id}'.",
    )


@router.post("/retry/{session_id}", response_model=WorkflowRunResponse)
async def retry_workflow(session_id: str):
    """
    Retry a failed workflow from the last successful agent step.

    Clears the `error` field and re-runs the graph, which will skip completed
    agents and restart from the failed one.
    """
    state = get_session(session_id)
    if state is None:
        raise HTTPException(status_code=404, detail={"error": "session_not_found",
                                                      "message": f"Session '{session_id}' does not exist."})
    current_settings = get_settings()
    if not current_settings.is_anthropic_configured:
        raise HTTPException(
            status_code=503,
            detail={"error": "ai_service_unconfigured",
                    "message": "ANTHROPIC_API_KEY is not set."},
        )
    try:
        final_state = await run_workflow(
            workflow_type=state.get("workflow_type", "project"),
            user_input=state.get("user_input", {}),
            session_id=session_id,
        )
        return _session_to_response(final_state)
    except Exception as exc:
        raise HTTPException(status_code=500, detail={"error": "retry_failed", "message": str(exc)})
