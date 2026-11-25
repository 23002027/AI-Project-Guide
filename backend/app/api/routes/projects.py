"""
Project & Task Management Endpoints.

Provides local single-user project CRUD operations and milestone task tracking.
Supports seamless unauthenticated local access while preserving token compatibility.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, status

from backend.app.auth.security import get_optional_user_claims, get_current_user_claims
from backend.app.db.database import DatabaseService

router = APIRouter(prefix="/projects", tags=["Project Management"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class CreateProjectRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    domain: str = Field(default="AI / Machine Learning")
    description: Optional[str] = Field(default="")
    experience_level: Optional[str] = Field(default="Intermediate")
    deadline: Optional[str] = Field(default="3 months")
    budget: Optional[str] = Field(default="Free Tier")
    is_team: Optional[bool] = Field(default=False)
    team_size: Optional[int] = Field(default=1, ge=1, le=20)


class UpdateProjectRequest(BaseModel):
    title: Optional[str] = None
    domain: Optional[str] = None
    description: Optional[str] = None
    progress: Optional[int] = Field(default=None, ge=0, le=100)
    deadline: Optional[str] = None
    budget: Optional[str] = None
    team_size: Optional[int] = None


class AddTaskRequest(BaseModel):
    title: str = Field(..., min_length=2)
    category: Optional[str] = Field(default="backend")


class UpdateTaskStatusRequest(BaseModel):
    status: str = Field(..., pattern="^(pending|in_progress|completed)$")


# ---------------------------------------------------------------------------
# Project Endpoints
# ---------------------------------------------------------------------------

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_project(
    req: CreateProjectRequest,
    claims: Optional[Dict[str, Any]] = Depends(get_optional_user_claims),
):
    """
    Create a new project. In local single-user mode, automatically associates
    with the local workspace user without requiring login.
    """
    user_id = claims["sub"] if (claims and claims.get("sub")) else DatabaseService.get_default_user_id()
    project = await DatabaseService.create_project(user_id, req.model_dump())
    return project


@router.get("")
async def list_user_projects(
    claims: Optional[Dict[str, Any]] = Depends(get_optional_user_claims),
):
    """
    List all projects in the workspace.
    Returns all workspace projects without mandatory authentication.
    """
    user_id = claims.get("sub") if claims else None
    projects = await DatabaseService.list_projects(user_id)
    return {"projects": projects, "count": len(projects)}


@router.get("/{project_id}")
async def get_project(
    project_id: str,
    claims: Optional[Dict[str, Any]] = Depends(get_optional_user_claims),
):
    """Retrieve a project by ID."""
    project = await DatabaseService.get_project(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
    if claims and claims.get("sub") and project.get("user_id") != claims["sub"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
    return project


@router.put("/{project_id}")
async def update_project(
    project_id: str,
    req: UpdateProjectRequest,
    claims: Optional[Dict[str, Any]] = Depends(get_optional_user_claims),
):
    """Update project metadata or progress."""
    user_id = claims.get("sub") if claims else None
    updates = {k: v for k, v in req.model_dump().items() if v is not None}
    updated = await DatabaseService.update_project(project_id, updates, user_id=user_id)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found or unauthorized.")
    return updated


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    claims: Optional[Dict[str, Any]] = Depends(get_optional_user_claims),
):
    """Delete a project."""
    user_id = claims.get("sub") if claims else None
    success = await DatabaseService.delete_project(project_id, user_id=user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found or unauthorized.")
    return {"status": "deleted", "project_id": project_id}


# ---------------------------------------------------------------------------
# Task & Milestone Endpoints
# ---------------------------------------------------------------------------

@router.post("/{project_id}/tasks", status_code=status.HTTP_201_CREATED)
async def add_task(
    project_id: str,
    req: AddTaskRequest,
    claims: Optional[Dict[str, Any]] = Depends(get_optional_user_claims),
):
    """Add a task or milestone to the project."""
    project = await DatabaseService.get_project(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
    if claims and claims.get("sub") and project.get("user_id") != claims["sub"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    task = await DatabaseService.add_task(project_id, req.title, req.category or "backend")
    return task


@router.get("/{project_id}/tasks")
async def list_tasks(
    project_id: str,
    claims: Optional[Dict[str, Any]] = Depends(get_optional_user_claims),
):
    """List all tasks and milestones for a project."""
    project = await DatabaseService.get_project(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
    if claims and claims.get("sub") and project.get("user_id") != claims["sub"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    tasks = await DatabaseService.list_project_tasks(project_id)
    return {"tasks": tasks, "count": len(tasks)}


@router.put("/{project_id}/tasks/{task_id}")
@router.patch("/{project_id}/tasks/{task_id}")
async def update_task_status(
    project_id: str,
    task_id: str,
    req: UpdateTaskStatusRequest,
    claims: Optional[Dict[str, Any]] = Depends(get_optional_user_claims),
):
    """Update task completion status (pending, in_progress, completed)."""
    project = await DatabaseService.get_project(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
    if claims and claims.get("sub") and project.get("user_id") != claims["sub"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    updated_task = await DatabaseService.update_task_status(task_id, req.status)
    if not updated_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")
    return updated_task


@router.delete("/{project_id}/tasks/{task_id}")
async def delete_task(
    project_id: str,
    task_id: str,
    claims: Optional[Dict[str, Any]] = Depends(get_optional_user_claims),
):
    """Delete a task from the project."""
    project = await DatabaseService.get_project(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
    if claims and claims.get("sub") and project.get("user_id") != claims["sub"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    deleted = await DatabaseService.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")
    return {"status": "deleted", "task_id": task_id}
