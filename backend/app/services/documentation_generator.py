"""
Project Documentation & Academic Report Generator Service (Feature 8).
Generates structured final-year project documentation and synopsis reports
including abstract, literature review outline, methodology, and future scope,
while strictly upholding academic integrity without fabricated citations.
"""

import json
from typing import Optional
from backend.app.schemas.project_guidance import (
    ProjectIdeaInput,
    ProjectDocumentationResponse,
)
from backend.app.services.claude_service import ClaudeService


class DocumentationGeneratorService:
    """Specialized service for capstone project documentation and reports."""

    def __init__(self, claude_service: Optional[ClaudeService] = None):
        self.claude = claude_service or ClaudeService()

    def _build_system_prompt(self) -> str:
        return """You are a Professor, Academic Project Guide, and Senior Research Mentor.
Your task is to draft an academic project report outline for a final-year B.Tech / undergraduate engineering project.

CRITICAL ACADEMIC INTEGRITY INSTRUCTIONS:
1. Respond ONLY with a single valid JSON object adhering strictly to the schema.
2. NEVER fabricate non-existent research papers, fake citations, fictional DOI numbers, or synthetic experimental metric results.
3. For literature review, outline real conceptual paradigms and open research challenges in the domain (e.g. LLM latency, privacy constraints, retrieval-augmented generation limits).
4. For results, provide a clean evaluation template (metrics table structure with placeholders like Accuracy, Latency, Throughput) rather than inventing unverified numbers.
5. Ensure the language is formal, scholarly, and suitable for submission to university project examination committees."""

    def _build_user_prompt(self, idea_input: ProjectIdeaInput) -> str:
        schema_sample = {
            "project_title": idea_input.title,
            "abstract": "Academic abstract summarizing the problem, proposed methodology, key architectural contributions, and anticipated impact (150-250 words)...",
            "introduction": "Comprehensive introduction introducing the domain, background context, and motivation for the study...",
            "problem_statement": "Formal, rigorous problem formulation defining the specific technical challenge...",
            "literature_review_outline": [
                "Current state of rule-based and classical approaches",
                "Evolution toward deep learning and Transformer models",
                "Key limitations of existing commercial and open-source systems"
            ],
            "objectives": [
                "To design an automated, fault-tolerant ingestion pipeline",
                "To build a modular API service with sub-second response times",
                "To deploy and evaluate the prototype under realistic load"
            ],
            "methodology": "Step-by-step description of data collection, preprocessing, model selection, system integration, and verification procedures...",
            "proposed_architecture_summary": "Summary of the multi-tier system architecture and module interactions...",
            "implementation_plan_summary": "Overview of development sprints, tooling choices, and integration milestones...",
            "testing_methodology": "Explanation of unit testing, integration testing, boundary validation, and user acceptance testing...",
            "results_section_template": "Evaluation framework describing metrics to measure (e.g. Response Latency in ms, Memory Footprint in MB, Task Completion Rate in %) with guidelines for reporting...",
            "conclusion": "Formal summary of project contributions and implications...",
            "future_scope": [
                "Extension 1: Offline edge deployment on IoT/mobile devices",
                "Extension 2: Multi-modal support for audio and visual inputs"
            ]
        }

        return f"""Draft an academic project report outline for the following student project:

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

    async def generate_documentation(self, idea_input: ProjectIdeaInput) -> ProjectDocumentationResponse:
        """Executes academic documentation generation and validates against schema."""
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(idea_input)

        return await self.claude.complete_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=ProjectDocumentationResponse,
            max_tokens=4096
        )

    # Alias for agent orchestrator compatibility
    generate = generate_documentation
