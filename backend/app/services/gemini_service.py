"""
Google Gemini AI Service
Handles communication with the official google-genai Python SDK,
prompt formatting, error handling, model fallbacks, and structured response validation.
"""

import os
import json
import re
import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Type, List
from pydantic import BaseModel, ValidationError

from google import genai
from google.genai import types
from google.genai.errors import APIError

from backend.app.config import get_settings
from backend.app.schemas.ai_plan import PlanRequest, PlanResponse, PlanMode

logger = logging.getLogger("gemini_service")


class GeminiNotConfiguredError(Exception):
    """Raised when the Gemini API key is missing or unconfigured."""
    pass


class GeminiServiceError(Exception):
    """Raised when an error occurs while communicating with Google Gemini API."""
    pass


class InvalidAIResponseError(Exception):
    """Raised when Gemini's response cannot be parsed into the expected JSON schema."""
    pass


class GeminiService:
    """Service wrapping official Google GenAI SDK interactions."""

    FALLBACK_MODELS = [
        "gemini-3.1-flash-lite",
        "gemini-3.5-flash-lite",
        "gemini-3.5-flash",
    ]

    def __init__(self, client: Optional[genai.Client] = None):
        self.settings = get_settings()
        self._client = client

    def get_client(self) -> genai.Client:
        """Returns the genai.Client or raises if unconfigured."""
        if self._client is not None:
            return self._client

        if not self.settings.is_gemini_configured:
            raise GeminiNotConfiguredError(
                "Gemini API key is not configured. Please set GEMINI_API_KEY in your backend/.env file."
            )

        self._client = genai.Client(
            api_key=self.settings.GEMINI_API_KEY,
            http_options=types.HttpOptions(timeout=45000)
        )
        return self._client

    def _build_system_prompt(self, mode: PlanMode) -> str:
        """Build the specialized system prompt for the specified mode."""
        base_instructions = """You are an expert Senior AI Engineer, Multi-Agent Systems Architect, and Technical Mentor for university engineering students.
Your task is to take a student's idea or problem statement and produce a production-quality, rigorous project plan.

CRITICAL INSTRUCTIONS:
1. You MUST respond ONLY with a single valid JSON object adhering exactly to the specified JSON schema.
2. Do NOT output any introductory text, pleasantries, markdown explanations, or trailing commentary outside the JSON block.
3. Be practical and realistic based on the student's skill level, time constraints, and team size.
4. For Mermaid diagrams, produce valid `graph TD` or `flowchart TD` syntax with quoted labels where appropriate.
5. In your recommendations, explain WHY each tool and technology is suitable, and offer viable alternatives.
"""
        if mode == PlanMode.HACKATHON:
            mode_guidance = """
HACKATHON SPECIFIC FOCUS:
- Focus on building a Minimum Viable Product (MVP) that can be realistically demoed within the allotted hours.
- Clearly divide features into core must-haves vs features to cut/defer.
- Address hackathon judging metrics: Innovation, Technical Depth, UI/UX polish, Real-world Impact, and Feasibility.
- Include a 2-3 minute live demo walkthrough, a punchy 30-second opening hook for judges, and fallback risk mitigations (e.g., if live APIs or Wi-Fi fail).
- Populate the `hackathon_guidance` object completely in your JSON response.
"""
        else:
            mode_guidance = """
COLLEGE PROJECT SPECIFIC FOCUS:
- Focus on academic depth, robust engineering, database normalization, maintainable architecture, and final-year evaluation criteria.
- Produce a structured multi-week or multi-month development roadmap.
- Set `hackathon_guidance` to null in your JSON response.
"""
        return base_instructions + mode_guidance

    def _build_user_prompt(self, req: PlanRequest) -> str:
        """Construct the prompt containing all user constraints and schema requirements."""
        schema_sample = {
            "project_title": "Concise Project Title",
            "mode": req.mode.value,
            "problem_analysis": "Detailed problem analysis...",
            "recommended_solution": "Recommended solution overview...",
            "technology_stack": [
                {
                    "name": "FastAPI",
                    "category": "Backend",
                    "reason": "High-performance async framework with automatic OpenAPI docs",
                    "alternatives": ["Express.js", "Django Ninja"]
                }
            ],
            "ai_tools": [
                {
                    "tool_name": "Google Gemini 3.5 Flash",
                    "recommended_for": "Backend agent logic and planning",
                    "purpose": "Orchestrates multi-agent workflows"
                }
            ],
            "architecture": {
                "overview": "Microservice/modular monolith description",
                "frontend_layer": "Next.js/React frontend...",
                "backend_layer": "FastAPI async REST endpoints...",
                "data_layer": "Relational schema...",
                "ai_agent_layer": "LangGraph multi-agent orchestrator...",
                "mermaid_diagram": "flowchart TD\n    User[User Client] --> UI[Frontend]\n    UI --> API[FastAPI Server]\n    API --> DB[(Database)]"
            },
            "roadmap": [
                {
                    "phase_number": 1,
                    "phase_name": "Phase 1: Setup & Architecture",
                    "estimated_duration": "Hours 0-4 or Week 1",
                    "goals": ["Goal 1", "Goal 2"],
                    "action_items": ["Action 1", "Action 2"]
                }
            ],
            "estimated_completion_time": req.available_time,
            "hackathon_guidance": None if req.mode == PlanMode.PROJECT else {
                "mvp_core_features": ["Feature A", "Feature B"],
                "cut_features": ["Feature X to defer", "Feature Y to defer"],
                "judging_alignment": [
                    {
                        "criterion": "Innovation",
                        "score_potential": "High",
                        "how_to_maximize": "Highlight novel agent orchestration"
                    }
                ],
                "team_allocation": [
                    {
                        "role": "Full-Stack Lead",
                        "responsibilities": ["API Integration", "UI wireframe"],
                        "hours_breakdown": "50% backend, 50% frontend"
                    }
                ],
                "live_demo_script": ["Step 1: Open dashboard", "Step 2: Trigger live generation"],
                "pitch_hook": "Imagine an assistant that turns any idea into a deployed project in minutes...",
                "risk_mitigation": ["Keep pre-recorded video backup in case Wi-Fi drops"]
            }
        }

        return f"""Analyze the following project request and return a comprehensive plan matching the exact JSON format below:

USER REQUEST:
- Mode: {req.mode.value}
- Project Idea / Problem Statement: {req.idea}
- Skill Level: {req.skill_level.value}
- Available Time: {req.available_time}
- Team Size: {req.team_size} member(s)
- Budget: {req.budget or 'Free Tier / Open Source'}
- Preferred Technologies: {', '.join(req.preferred_tech) if req.preferred_tech else 'None specified'}

EXPECTED JSON SCHEMA TEMPLATE:
{json.dumps(schema_sample, indent=2)}

Remember: Return ONLY valid JSON, with no wrapping explanations outside the JSON."""

    def _extract_json(self, raw_text: str) -> Dict[str, Any]:
        """Extract and parse JSON from Gemini's text response, handling markdown blocks."""
        cleaned = raw_text.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
            cleaned = re.sub(r"\s*```$", "", cleaned)
            cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as exc:
            # Fallback regex search for outer-most { ... }
            match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    pass
            raise InvalidAIResponseError(f"Failed to parse Gemini response as JSON: {str(exc)}") from exc

    def _get_candidate_models(self) -> List[str]:
        """Return list of models to try in order."""
        primary = self.settings.GEMINI_MODEL
        models = [primary]
        for fb in self.FALLBACK_MODELS:
            if fb not in models:
                models.append(fb)
        return models

    async def complete_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: Type[BaseModel],
        max_tokens: int = 4096
    ) -> Any:
        """
        Calls Gemini with system and user prompts, extracts JSON,
        and validates against the provided Pydantic response_model.
        """
        logger.info("[LLM-INSTANCE: GEMINI] >>> REQUEST START | Target Schema: %s", response_model.__name__)
        client = self.get_client()
        models = self._get_candidate_models()
        last_error = None

        for model_name in models:
            t0 = time.perf_counter()
            try:
                logger.info("[LLM-INSTANCE: GEMINI] Attempting inference with model: %s", model_name)
                config = types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    max_output_tokens=max_tokens,
                    temperature=0.2,
                )

                response = await client.aio.models.generate_content(
                    model=model_name,
                    contents=user_prompt,
                    config=config,
                )

                elapsed = time.perf_counter() - t0
                raw_text = response.text or ""
                if not raw_text.strip():
                    logger.warning("[LLM-INSTANCE: GEMINI] ⚠️  Model %s returned empty response after %.2fs", model_name, elapsed)
                    raise GeminiServiceError(f"Received an empty response from Gemini model {model_name}.")

                data = self._extract_json(raw_text)
                validated = response_model.model_validate(data)
                logger.info("[LLM-INSTANCE: GEMINI] ✅ WORKING PROPERLY | Model %s succeeded in %.2fs -> %s", model_name, elapsed, response_model.__name__)
                return validated

            except (APIError, Exception) as err:
                elapsed = time.perf_counter() - t0
                err_str = str(err)
                logger.warning("[LLM-INSTANCE: GEMINI] ❌ Model %s NOT WORKING (Error after %.2fs): %s", model_name, elapsed, err_str[:200])
                if any(x in err_str for x in ["503", "504", "404", "429", "RESOURCE_EXHAUSTED", "quota", "limit exceeded", "UNAVAILABLE", "DEADLINE_EXCEEDED", "NOT_FOUND"]):
                    last_error = err
                    continue
                if isinstance(err, (json.JSONDecodeError, InvalidAIResponseError)):
                    raise InvalidAIResponseError(str(err)) from err
                if isinstance(err, ValidationError):
                    raise InvalidAIResponseError(f"Schema validation error on {model_name}: {err}") from err
                raise GeminiServiceError(f"Gemini API communication error with {model_name}: {err_str}") from err

        logger.error("[LLM-INSTANCE: GEMINI] ❌ NOT WORKING | All candidate models failed. Last error: %s", last_error)
        raise GeminiServiceError(
            f"All candidate Gemini models failed. Last error: {last_error}"
        )

    async def generate_plan(self, req: PlanRequest) -> PlanResponse:
        """
        Calls Google Gemini API to generate a structured project or hackathon plan.
        """
        logger.info("[LLM-INSTANCE: GEMINI] >>> PLAN GENERATION START | Mode: %s", req.mode.value)
        client = self.get_client()
        system_prompt = self._build_system_prompt(req.mode)
        user_prompt = self._build_user_prompt(req)
        models = self._get_candidate_models()
        last_error = None

        for model_name in models:
            t0 = time.perf_counter()
            try:
                logger.info("[LLM-INSTANCE: GEMINI] Attempting plan generation with model: %s", model_name)
                config = types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    max_output_tokens=4096,
                    temperature=0.2,
                )

                response = await client.aio.models.generate_content(
                    model=model_name,
                    contents=user_prompt,
                    config=config,
                )

                elapsed = time.perf_counter() - t0
                raw_text = response.text or ""
                if not raw_text.strip():
                    logger.warning("[LLM-INSTANCE: GEMINI] ⚠️  Model %s returned empty response after %.2fs", model_name, elapsed)
                    raise GeminiServiceError(f"Received an empty response from Gemini ({model_name}).")

                data = self._extract_json(raw_text)

                data["metadata"] = {
                    "model_used": model_name,
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "mode": req.mode.value
                }

                validated = PlanResponse.model_validate(data)
                logger.info("[LLM-INSTANCE: GEMINI] ✅ WORKING PROPERLY | Plan generated with model %s in %.2fs", model_name, elapsed)
                return validated

            except (APIError, Exception) as err:
                elapsed = time.perf_counter() - t0
                err_str = str(err)
                logger.warning("[LLM-INSTANCE: GEMINI] ❌ Model %s NOT WORKING for plan generation (after %.2fs): %s", model_name, elapsed, err_str[:200])
                if any(x in err_str for x in ["503", "504", "404", "429", "RESOURCE_EXHAUSTED", "quota", "limit exceeded", "UNAVAILABLE", "DEADLINE_EXCEEDED", "NOT_FOUND"]):
                    last_error = err
                    continue
                if isinstance(err, (json.JSONDecodeError, InvalidAIResponseError)):
                    raise InvalidAIResponseError(str(err)) from err
                if isinstance(err, ValidationError):
                    raise InvalidAIResponseError(f"Schema validation error: {err}") from err
                raise GeminiServiceError(f"Gemini plan generation error with {model_name}: {err_str}") from err

        logger.error("[LLM-INSTANCE: GEMINI] ❌ NOT WORKING | All candidate models failed for plan generation. Last error: %s", last_error)
        raise GeminiServiceError(f"All candidate Gemini models failed. Last error: {last_error}")
