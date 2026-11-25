"""
GitHub Integration Routes (Phase 9).

Provides repository scaffolding, README and gitignore generation,
and GitHub connectivity status check.
"""

from fastapi import APIRouter
from backend.app.schemas.coding_assistant import (
    GitHubScaffoldRequest,
    GitHubScaffoldResponse,
)
from backend.app.services.github_service import GitHubService

router = APIRouter(prefix="/github", tags=["GitHub Integration"])


@router.post("/scaffold", response_model=GitHubScaffoldResponse)
async def generate_github_scaffold(req: GitHubScaffoldRequest):
    """
    Generate complete GitHub repository assets: professional README.md,
    language-specific .gitignore, directory tree, and milestone issue templates.
    """
    service = GitHubService()
    return service.generate_scaffold(req)


@router.get("/status")
async def get_github_status():
    """Check whether a GitHub token is configured for live repository operations."""
    service = GitHubService()
    profile = await service.get_user_profile() if service.is_configured else None
    return {
        "configured": service.is_configured,
        "user_profile": profile,
        "message": "GitHub personal access token configured" if service.is_configured else "Unconfigured (running in local offline scaffolding mode)",
    }
