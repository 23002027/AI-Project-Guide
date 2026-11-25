"""
Technology Stack & AI Development Tool Advisor Service (Features 2 & 3).
Provides tailored, student-viable technology and AI tooling recommendations
with exact role descriptions, rationale, implementation guides, and pricing transparency.
"""

import json
from typing import Optional
from backend.app.schemas.project_guidance import (
    ProjectIdeaInput,
    TechStackAdvisorResponse,
)
from backend.app.services.claude_service import ClaudeService


class TechnologyAdvisorService:
    """Specialized service for curated tech stack and AI tool recommendations."""

    def __init__(self, claude_service: Optional[ClaudeService] = None):
        self.claude = claude_service or ClaudeService()

    def _build_system_prompt(self) -> str:
        return """You are a Principal Software Architect and Technical Mentor for engineering students.
Your task is to recommend the optimal, most practical technology stack and AI developer tools for a student's project.

CRITICAL INSTRUCTIONS:
1. Respond ONLY with a single valid JSON object adhering strictly to the schema.
2. Do NOT recommend technologies simply because they are popular or trending. Every recommendation MUST directly serve the student's constraints (budget, skill level, and deadline).
3. Always emphasize generous free tiers (e.g. Supabase Free Tier, Vercel Hobby, Neon DB, Hugging Face free inference, Render free tier). Never fabricate pricing.
4. Recommend modern AI developer tools (e.g. Claude for complex reasoning/agent architecture, Antigravity for agentic development, Cursor/Copilot for coding, v0 for UI prototyping, Figma for design) and specify exact project phases where each shines.
5. Provide viable alternative technologies for students who prefer another language or framework."""

    def _build_user_prompt(self, idea_input: ProjectIdeaInput) -> str:
        schema_sample = {
            "project_title": idea_input.title,
            "technology_recommendations": [
                {
                    "technology_name": "FastAPI",
                    "category": "Backend Framework",
                    "why_suitable": "Asynchronous, fast, automatic Swagger OpenAPI docs, and native Python AI integration",
                    "role_in_project": "Coordinates REST endpoints, agent pipelines, and database operations",
                    "implementation_guide": "Install via pip install fastapi uvicorn, set up APIRouter, run with uvicorn main:app --reload",
                    "cost_tier": "100% Free / Open Source",
                    "alternatives": ["Django Ninja", "Express.js (Node.js)"]
                },
                {
                    "technology_name": "Next.js (React)",
                    "category": "Frontend Framework",
                    "why_suitable": "Component-based architecture, Tailwind CSS support, robust ecosystem",
                    "role_in_project": "Interactive dashboard for end-user interaction and real-time visualization",
                    "implementation_guide": "Initialize via npx create-next-app@latest, connect to backend using fetch/Axios",
                    "cost_tier": "100% Free / Open Source",
                    "alternatives": ["Vite + React", "SvelteKit"]
                }
            ],
            "ai_tool_advisors": [
                {
                    "tool_name": "Claude 3.5 Sonnet",
                    "development_activity": "Complex Multi-Agent Architecture & Pedagogical Guidance",
                    "how_to_use": "Use Anthropic Python SDK with structured Pydantic output schemas",
                    "when_to_use": "Phase 3 (Backend) and Phase 5 (AI Integration)",
                    "free_alternative": "Hugging Face Inference API / Mistral 7B Free Tier"
                },
                {
                    "tool_name": "Antigravity",
                    "development_activity": "AI-assisted agent development and automated project scaffolding",
                    "how_to_use": "Utilize agentic workflows to build, test, and iterate codebase modules",
                    "when_to_use": "Across all development phases",
                    "free_alternative": "VS Code with open-source extensions"
                }
            ],
            "rationale_summary": "Comprehensive architectural rationale explaining why this stack maximizes development speed and academic evaluation impact..."
        }

        return f"""Analyze the student's project profile and recommend the optimal technology stack and AI tools:

STUDENT PROFILE & CONSTRAINTS:
- Project Title: {idea_input.title}
- Description: {idea_input.description or 'None provided'}
- Domain: {idea_input.domain.value}
- Student Skills: {', '.join(idea_input.skills)}
- Experience Level: {idea_input.experience_level.value}
- Budget: {idea_input.budget or 'Free Tier'}
- Deadline: {idea_input.deadline}
- Team Size: {idea_input.team_size} member(s)

REQUIRED JSON SCHEMA:
{json.dumps(schema_sample, indent=2)}

Return ONLY valid JSON."""

    async def recommend_tech_stack(self, idea_input: ProjectIdeaInput) -> TechStackAdvisorResponse:
        """Executes Claude tech stack recommendation and validates against schema."""
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(idea_input)

        return await self.claude.complete_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=TechStackAdvisorResponse,
            max_tokens=4096
        )

    # Alias for agent orchestrator compatibility
    recommend = recommend_tech_stack
