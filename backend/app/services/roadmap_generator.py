"""
Development Roadmap & Deployment Advisor Service (Features 5 & 9).
Generates an adaptable 9-phase college project roadmap,
complete with dependency management, phase checklists, testing strategies,
and step-by-step deployment instructions.
"""

import json
from typing import Optional
from backend.app.schemas.project_guidance import (
    ProjectIdeaInput,
    DevelopmentRoadmapResponse,
)
from backend.app.services.claude_service import ClaudeService


class RoadmapGeneratorService:
    """Specialized service for 9-phase project roadmap and deployment planning."""

    def __init__(self, claude_service: Optional[ClaudeService] = None):
        self.claude = claude_service or ClaudeService()

    def _build_system_prompt(self) -> str:
        return """You are an Agile Technical Project Manager and Final-Year University Project Coordinator.
Your task is to create a realistic, phased development roadmap that helps students deliver their capstone project on time.

CRITICAL INSTRUCTIONS:
1. Respond ONLY with a single valid JSON object adhering strictly to the schema.
2. Structure the roadmap across the 9 standard college project phases:
   - Phase 1: Research and requirements
   - Phase 2: UI/UX design
   - Phase 3: Backend development
   - Phase 4: Frontend development
   - Phase 5: AI/ML integration
   - Phase 6: Database integration
   - Phase 7: Testing
   - Phase 8: Deployment
   - Phase 9: Documentation and final presentation
3. Calibrate durations realistically according to the student's stated deadline and skill level.
4. Include actionable completion checklists and explicit dependency links between phases.
5. Provide practical, zero-cost cloud deployment steps (e.g. Vercel for frontend, Render/Railway for backend, Neon/Supabase for PostgreSQL)."""

    def _build_user_prompt(self, idea_input: ProjectIdeaInput) -> str:
        schema_sample = {
            "project_title": idea_input.title,
            "total_estimated_duration": idea_input.deadline,
            "phases": [
                {
                    "phase_number": 1,
                    "phase_title": "Phase 1: Research and Requirements Engineering",
                    "estimated_duration": "Week 1",
                    "tasks": [
                        "Define core functional and non-functional requirements",
                        "Conduct literature review of existing approaches"
                    ],
                    "dependencies": ["None"],
                    "required_tools": ["Notion", "Google Scholar", "Figma"],
                    "expected_output": "Software Requirements Specification (SRS) document",
                    "completion_checklist": [
                        "Problem statement finalized",
                        "Key stakeholder personas identified"
                    ]
                }
            ],
            "deployment_and_testing": {
                "hosting_platform": "Vercel (Frontend) + Render Free Tier (Backend) + Neon (Serverless Postgres)",
                "environment_variables_checklist": [
                    "DATABASE_URL",
                    "ANTHROPIC_API_KEY",
                    "ENVIRONMENT=production"
                ],
                "step_by_step_deployment": [
                    "Step 1: Push verified code to a private GitHub repository",
                    "Step 2: Connect repository to Render and configure Web Service build command",
                    "Step 3: Connect repository to Vercel for continuous frontend deployments"
                ],
                "testing_strategy": [
                    "Unit tests with pytest for all API routes and services",
                    "Frontend component tests with React Testing Library",
                    "End-to-end integration tests on staging environment"
                ],
                "maintenance_practices": [
                    "Enable automated GitHub Actions CI pipeline on push",
                    "Monitor uptime and latency using free tools like UptimeRobot"
                ]
            }
        }

        return f"""Generate a detailed 9-phase development roadmap and deployment strategy for:

PROJECT CONTEXT:
- Title: {idea_input.title}
- Description: {idea_input.description or 'None provided'}
- Domain: {idea_input.domain.value}
- Student Skills: {', '.join(idea_input.skills)}
- Experience Level: {idea_input.experience_level.value}
- Total Available Deadline: {idea_input.deadline}
- Team Size: {idea_input.team_size} member(s)

REQUIRED JSON SCHEMA:
{json.dumps(schema_sample, indent=2)}

Return ONLY valid JSON."""

    async def generate_roadmap(self, idea_input: ProjectIdeaInput) -> DevelopmentRoadmapResponse:
        """Executes roadmap generation and validates against schema."""
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(idea_input)

        return await self.claude.complete_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=DevelopmentRoadmapResponse,
            max_tokens=4096
        )

    # Alias for agent orchestrator compatibility
    generate = generate_roadmap
