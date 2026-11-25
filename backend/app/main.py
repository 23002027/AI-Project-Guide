"""
AI Project Guide - FastAPI Entrypoint
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import get_settings
from .api.routes.health import router as health_router
from .api.routes.ai import router as ai_router
from .api.routes.project_guidance import router as project_router
from .api.routes.hackathon_guidance import router as hackathon_router
from .api.routes.agent_orchestration import router as agent_router
from .api.routes.auth import router as auth_router
from .api.routes.projects import router as projects_router
from .api.routes.presentation import router as presentation_router
from .api.routes.coding import router as coding_router
from .api.routes.github import router as github_router
from .db.database import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("main")

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("==================================================================")
    logger.info(" AI Project Guide API Started")
    logger.info(" AI Provider: %s | Model: %s", settings.AI_PROVIDER, settings.primary_model)
    logger.info(" Host: %s | Port: %s", settings.HOST, settings.PORT)
    logger.info("==================================================================")
    yield
    logger.info("AI Project Guide API Shutting Down")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend API powering the AI Project Guide local AI application.",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure Cross-Origin Resource Sharing (CORS) for frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(health_router, prefix="/api")
app.include_router(ai_router, prefix="/api")
app.include_router(project_router, prefix="/api")
app.include_router(hackathon_router, prefix="/api")
app.include_router(agent_router)        # Phase 5: Multi-Agent Orchestration (/api/agent/...)
app.include_router(auth_router, prefix="/api")         # Phase 7: Authentication (/api/auth/...)
app.include_router(projects_router, prefix="/api")     # Phase 7: Multi-Tenant Projects (/api/projects/...)
app.include_router(presentation_router, prefix="/api") # Phase 8: PowerPoint & Report Exporter (/api/presentation/...)
app.include_router(coding_router, prefix="/api")       # Phase 9: Coding Assistance (/api/coding/...)
app.include_router(github_router, prefix="/api")       # Phase 9: GitHub Integration (/api/github/...)


@app.get("/", tags=["Root"])
async def root():
    """Root landing endpoint providing service metadata."""
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "documentation": "/docs",
        "health_check": "/api/health",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
