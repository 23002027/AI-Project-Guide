"""
System Architecture Generator Service (Feature 4).
Generates high-level blueprints, client-server interaction designs,
database schemas, API endpoint suggestions, and valid Mermaid diagrams.
"""

import json
from typing import Optional
from backend.app.schemas.project_guidance import (
    ProjectIdeaInput,
    ArchitectureGeneratorResponse,
)
from backend.app.services.claude_service import ClaudeService


class ArchitectureGeneratorService:
    """Specialized service for system architecture and diagram generation."""

    def __init__(self, claude_service: Optional[ClaudeService] = None):
        self.claude = claude_service or ClaudeService()

    def _build_system_prompt(self) -> str:
        return """You are a Principal Software Architect and Systems Design Mentor.
Your task is to design a robust, clean, and modern system architecture for an undergraduate engineering project.

CRITICAL INSTRUCTIONS:
1. Respond ONLY with a single valid JSON object adhering strictly to the schema.
2. Produce clean, maintainable architectural tiers: Client Tier, API Gateway/Backend Tier, Business/AI Agent Tier, and Data Tier.
3. For the Mermaid diagram, produce valid `flowchart TD` or `flowchart LR` syntax. Ensure all node labels with spaces or symbols are enclosed in quotes (e.g. `Client["Next.js Web UI"]`).
4. Avoid overly complex microservice designs when a modular monolith is more suitable for college deadlines.
5. Provide specific, practical API endpoint suggestions with HTTP methods and clear paths."""

    def _build_user_prompt(self, idea_input: ProjectIdeaInput) -> str:
        schema_sample = {
            "project_title": idea_input.title,
            "high_level_overview": "Comprehensive architectural overview explaining tiers and communication protocols...",
            "frontend_backend_flow": "Step-by-step communication lifecycle: client triggers REST/WebSocket request, FastAPI processes async task, returns structured JSON...",
            "database_architecture": "Database model design, entity relationships, indexing, and persistence strategy...",
            "module_breakdown": [
                {
                    "module_name": "Authentication & User Management",
                    "responsibility": "Handles secure signup, login, JWT token issuance and RBAC",
                    "technologies_used": ["FastAPI", "Passlib", "PostgreSQL"],
                    "inputs": "User credentials (email, password)",
                    "outputs": "Signed JWT access token and user session object"
                },
                {
                    "module_name": "Core AI Orchestration Engine",
                    "responsibility": "Executes prompt pipelines, parses outputs, and handles fallback logic",
                    "technologies_used": ["Python", "Anthropic Claude SDK", "Pydantic"],
                    "inputs": "Parsed user request parameters",
                    "outputs": "Structured validated domain responses"
                }
            ],
            "api_endpoint_suggestions": [
                {
                    "method": "POST",
                    "path": "/api/v1/auth/token",
                    "description": "Authenticate user credentials and issue JWT"
                },
                {
                    "method": "POST",
                    "path": "/api/v1/analyze",
                    "description": "Trigger core analysis pipeline"
                }
            ],
            "data_flow_explanation": "Detailed walk-through of data ingress, transformation, storage, and egress...",
            "mermaid_diagram": "flowchart TD\\n    Client[\"Frontend UI (Next.js)\"] -->|HTTPS / REST| API[\"API Gateway (FastAPI)\"]\\n    API --> Core[\"Business Logic & AI Engine\"]\\n    Core --> DB[(\"PostgreSQL Database\")]"
        }

        return f"""Generate a complete system architecture blueprint for the following project:

PROJECT SPECIFICATIONS:
- Title: {idea_input.title}
- Description: {idea_input.description or 'None provided'}
- Domain: {idea_input.domain.value}
- Student Skills: {', '.join(idea_input.skills)}
- Experience Level: {idea_input.experience_level.value}
- Deadline: {idea_input.deadline}
- Team Size: {idea_input.team_size} member(s)

REQUIRED JSON SCHEMA:
{json.dumps(schema_sample, indent=2)}

Return ONLY valid JSON."""

    async def generate_architecture(self, idea_input: ProjectIdeaInput) -> ArchitectureGeneratorResponse:
        """Executes architecture generation and validates against schema."""
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(idea_input)

        return await self.claude.complete_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=ArchitectureGeneratorResponse,
            max_tokens=4096
        )

    # Alias for agent orchestrator compatibility
    generate = generate_architecture
