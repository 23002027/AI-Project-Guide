"""
Module Coding Guidance & AI Prompt Generator Service (Features 6 & 7).
Provides module-wise coding steps, folder structures, example code snippets,
and copy-ready prompts for Claude, Antigravity, GitHub Copilot, and Cursor.
"""

import json
from typing import Optional
from backend.app.schemas.project_guidance import (
    ProjectIdeaInput,
    AICodingPromptsResponse,
)
from backend.app.services.claude_service import ClaudeService


class CodingPromptGeneratorService:
    """Specialized service for module coding walkthroughs and AI assistant prompts."""

    def __init__(self, claude_service: Optional[ClaudeService] = None):
        self.claude = claude_service or ClaudeService()

    def _build_system_prompt(self) -> str:
        return """You are a Senior Technical Lead and Pair Programming Mentor.
Your task is to provide concrete module-by-module implementation guidance and copy-ready AI prompts for an engineering student.

CRITICAL INSTRUCTIONS:
1. Respond ONLY with a single valid JSON object adhering strictly to the schema.
2. For module guidance, include real, syntactically correct code snippets (not pseudo-code).
3. Include realistic directory structures, dependencies, testing instructions, and common pitfalls with solutions.
4. For AI prompts (Claude, Antigravity, GitHub Copilot, Cursor), generate COMPLETE, context-rich, copy-ready prompts that mention the project's actual domain, constraints, and architecture. Never output generic placeholders like '[Insert code here]'."""

    def _build_user_prompt(self, idea_input: ProjectIdeaInput) -> str:
        schema_sample = {
            "project_title": idea_input.title,
            "module_walkthroughs": [
                {
                    "module_name": "API Gateway & Router Module",
                    "purpose": "Centralizes incoming HTTP requests, performs input validation, and enforces CORS policies",
                    "folder_structure": "backend/app/api/\n├── routes/\n│   ├── auth.py\n│   └── core.py\n└── __init__.py",
                    "implementation_steps": [
                        "1. Create APIRouter instance with appropriate prefix",
                        "2. Define Pydantic request models with field validation",
                        "3. Implement async route handler with structured exception handling"
                    ],
                    "example_code_snippet": "@router.post('/process')\nasync def process(payload: RequestModel):\n    return await service.execute(payload)",
                    "required_dependencies": ["fastapi", "pydantic", "uvicorn"],
                    "testing_instructions": "Run pytest tests/test_routes.py using FastAPI TestClient",
                    "common_errors_and_solutions": [
                        "Error: 422 Unprocessable Entity -> Fix: Check that request JSON keys match Pydantic field names exactly"
                    ]
                }
            ],
            "copy_ready_prompts": [
                {
                    "target_tool": "Claude 3.5 Sonnet",
                    "use_case": "Backend Core Pipeline Development",
                    "prompt_text": f"Act as a Senior Python Engineer. I am building a project called '{idea_input.title}' in the domain of '{idea_input.domain.value}'. Write an asynchronous FastAPI service class that..."
                },
                {
                    "target_tool": "Antigravity",
                    "use_case": "Agent Workflow Scaffolding",
                    "prompt_text": f"Scaffold a multi-agent workflow for '{idea_input.title}' using clean modular Python services. Include error boundaries and pytest test cases..."
                },
                {
                    "target_tool": "GitHub Copilot",
                    "use_case": "Automated Unit Test Generation",
                    "prompt_text": "Write pytest test cases for the following FastAPI endpoint, mocking all external services and asserting HTTP 200, 422, and 500 status codes..."
                }
            ]
        }

        return f"""Generate module coding guidance and copy-ready AI prompts for:

PROJECT DETAILS:
- Title: {idea_input.title}
- Description: {idea_input.description or 'None provided'}
- Domain: {idea_input.domain.value}
- Skills: {', '.join(idea_input.skills)}
- Experience Level: {idea_input.experience_level.value}
- Deadline: {idea_input.deadline}

REQUIRED JSON SCHEMA:
{json.dumps(schema_sample, indent=2)}

Return ONLY valid JSON."""

    async def generate_coding_prompts(self, idea_input: ProjectIdeaInput) -> AICodingPromptsResponse:
        """Executes prompt generation and validates against schema."""
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(idea_input)

        return await self.claude.complete_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=AICodingPromptsResponse,
            max_tokens=4096
        )

    # Alias for agent orchestrator compatibility
    generate = generate_coding_prompts
