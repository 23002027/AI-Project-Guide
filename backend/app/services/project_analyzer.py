"""
Project Idea Analyzer Service (Feature 1).
Evaluates university capstone and engineering project concepts,
providing academic rigor, problem statement formulation, feasibility,
and innovation opportunities.
"""

import json
from typing import Optional
from backend.app.schemas.project_guidance import (
    ProjectIdeaInput,
    ProjectAnalysisResponse,
)
from backend.app.services.claude_service import ClaudeService


class ProjectAnalyzerService:
    """Specialized service for deep project idea analysis."""

    def __init__(self, claude_service: Optional[ClaudeService] = None):
        self.claude = claude_service or ClaudeService()

    def _build_system_prompt(self) -> str:
        return """You are a Senior AI Engineer, University Capstone Project Guide, and Technical Evaluator.
Your goal is to thoroughly analyze a college student's project idea, helping them frame it with academic rigor and engineering excellence.

CRITICAL INSTRUCTIONS:
1. Respond ONLY with a single valid JSON object adhering strictly to the expected schema.
2. No conversational greetings, preamble, or markdown wrapper outside the JSON block.
3. Be realistic and constructive based on the student's stated skill level, team size, and deadline.
4. Highlight concrete innovation opportunities that will make the project stand out to final-year project examiners.
5. If essential details are missing or vague, provide targeted follow-up questions."""

    def _build_user_prompt(self, idea_input: ProjectIdeaInput) -> str:
        schema_sample = {
            "project_title": idea_input.title,
            "domain": idea_input.domain.value,
            "problem_statement": "Concise, academically sound problem definition...",
            "existing_limitations": [
                "Limitation 1 of current solutions",
                "Limitation 2 of current solutions"
            ],
            "proposed_solution": "Detailed engineering approach...",
            "target_users": ["Primary user group 1", "Secondary user group 2"],
            "main_objectives": [
                "Objective 1: Measurable technical milestone",
                "Objective 2: Integration milestone"
            ],
            "expected_outcomes": [
                "Outcome 1: Working web dashboard",
                "Outcome 2: Evaluated model accuracy report"
            ],
            "unique_selling_proposition": "What sets this project apart from textbook projects...",
            "innovation_opportunities": [
                "Opportunity 1: Agentic workflow automation",
                "Opportunity 2: Real-time edge inference"
            ],
            "feasibility_assessment": "Realistic evaluation of whether this can be completed in the given timeframe with the stated skills...",
            "project_complexity": "Moderate | High | Advanced",
            "follow_up_questions": [
                "Question 1 (only if critical requirements need clarification)"
            ]
        }

        return f"""Analyze the following university project idea and return a structured JSON report matching the schema below:

STUDENT PROJECT PROFILE:
- Title / Idea: {idea_input.title}
- Detailed Description: {idea_input.description or 'None provided'}
- Domain: {idea_input.domain.value}
- Student Skills: {', '.join(idea_input.skills)}
- Experience Level: {idea_input.experience_level.value}
- Available Budget: {idea_input.budget or 'Free Tier'}
- Project Deadline: {idea_input.deadline}
- Project Type: {'Team project (' + str(idea_input.team_size) + ' members)' if idea_input.is_team else 'Individual project'}

REQUIRED JSON SCHEMA:
{json.dumps(schema_sample, indent=2)}

Return ONLY valid JSON."""

    async def analyze_project(self, idea_input: ProjectIdeaInput) -> ProjectAnalysisResponse:
        """Executes Claude analysis and validates against ProjectAnalysisResponse."""
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(idea_input)

        return await self.claude.complete_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=ProjectAnalysisResponse,
            max_tokens=4096
        )

    # Alias for agent orchestrator compatibility
    analyze = analyze_project
