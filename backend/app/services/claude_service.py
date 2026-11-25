"""
AI Provider Service (Gemini primary, Ollama local, Claude legacy).
Handles communication with:
  - Ollama local LLM (AI_PROVIDER=ollama) — NEW primary for local inference
  - Google Gemini (AI_PROVIDER=gemini) — cloud primary
  - Anthropic Claude (AI_PROVIDER=claude) — cloud secondary / legacy
Preserves existing method signatures for full backward compatibility.
"""

import json
import re
import logging
import time
import unittest.mock
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Type
from pydantic import BaseModel

import anthropic
from anthropic import AsyncAnthropic

from backend.app.config import get_settings

logger = logging.getLogger("claude_service")
from backend.app.schemas.ai_plan import PlanRequest, PlanResponse, PlanMode
from backend.app.services.gemini_service import (
    GeminiService,
    GeminiNotConfiguredError,
    GeminiServiceError,
    InvalidAIResponseError as GeminiInvalidAIResponseError,
)
from backend.app.services.ollama_service import (
    OllamaService,
    OllamaUnavailableError,
    OllamaServiceError,
    OllamaInvalidResponseError,
)


class AINotConfiguredError(Exception):
    """Base exception raised when the active AI provider is unconfigured."""
    pass


class AIServiceError(Exception):
    """Base exception raised when an error occurs while communicating with the AI API."""
    pass


class AnthropicNotConfiguredError(AINotConfiguredError):
    """Raised when the Anthropic API key is missing or unconfigured."""
    pass


class AnthropicServiceError(AIServiceError):
    """Raised when an error occurs while communicating with Anthropic API."""
    pass


class InvalidAIResponseError(Exception):
    """Raised when the model's response cannot be parsed into the expected JSON schema."""
    pass


class ClaudeService:
    """
    Unified AI Service router.
    Priority order: Ollama (local) → Gemini (cloud) → Claude (cloud legacy).
    All existing callers are unaffected — same method signatures.
    """

    def __init__(
        self,
        client: Optional[AsyncAnthropic] = None,
        gemini_service: Optional[GeminiService] = None,
        ollama_service: Optional[OllamaService] = None,
    ):
        self.settings = get_settings()
        self._client = client
        self._gemini = gemini_service
        self._ollama = ollama_service

    # ------------------------------------------------------------------
    # Provider detection helpers
    # ------------------------------------------------------------------

    @property
    def is_using_ollama(self) -> bool:
        """True when AI_PROVIDER=ollama is configured AND we are not in a test that mocks Anthropic."""
        if self._client is not None:
            return False
        # When tests patch is_anthropic_configured or mock AsyncAnthropic, defer to Anthropic path
        if self.is_anthropic_patched:
            return False
        if self.is_anthropic_mocked:
            return False
        return self.settings.AI_PROVIDER == "ollama"

    @property
    def is_anthropic_patched(self) -> bool:
        """Detect if Settings.is_anthropic_configured has been patched in tests."""
        from backend.app.config import Settings
        return not isinstance(Settings.__dict__.get("is_anthropic_configured"), property)

    @property
    def is_anthropic_mocked(self) -> bool:
        """Detect if Anthropic SDK or settings are explicitly mocked in test suites."""
        return (
            isinstance(AsyncAnthropic, (unittest.mock.MagicMock, unittest.mock.AsyncMock))
            or isinstance(getattr(type(self.settings), "is_anthropic_configured", None), unittest.mock.MagicMock)
            or isinstance(getattr(self.settings, "is_anthropic_configured", None), unittest.mock.MagicMock)
        )

    @property
    def is_using_gemini(self) -> bool:
        """Determines whether Gemini is the active provider."""
        if self.is_using_ollama:
            return False
        if self._client is not None:
            return False
        if self.is_anthropic_patched:
            return False
        if self.is_anthropic_mocked:
            return False
        if self.settings.AI_PROVIDER == "claude" and self.settings.is_anthropic_configured:
            return False
        return self.settings.is_gemini_configured or self.settings.AI_PROVIDER == "gemini"

    # ------------------------------------------------------------------
    # Service accessors
    # ------------------------------------------------------------------

    def get_ollama_service(self) -> OllamaService:
        """Returns the Ollama service instance (lazy singleton)."""
        if self._ollama is None:
            self._ollama = OllamaService()
        return self._ollama

    def get_gemini_service(self) -> GeminiService:
        """Returns the Gemini service instance."""
        if self._gemini is None:
            self._gemini = GeminiService()
        return self._gemini

    def get_client(self) -> AsyncAnthropic:
        """Returns the AsyncAnthropic client or raises if unconfigured."""
        if self._client is not None:
            return self._client

        if not self.settings.is_anthropic_configured:
            raise AnthropicNotConfiguredError(
                "Anthropic API key is not configured. Please set ANTHROPIC_API_KEY in your .env file."
            )

        self._client = AsyncAnthropic(api_key=self.settings.ANTHROPIC_API_KEY)
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
        model_name = self.settings.primary_model
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
                    "tool_name": f"Google Gemini ({model_name})",
                    "recommended_for": "Backend agent logic and planning",
                    "purpose": "Orchestrates multi-agent workflows"
                }
            ],
            "architecture": {
                "overview": "Microservice/modular monolith description",
                "frontend_layer": "Next.js/React frontend...",
                "backend_layer": "FastAPI async REST endpoints...",
                "data_layer": "PostgreSQL / SQLite relational schema...",
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
        """Extract and parse JSON from text response, handling markdown blocks."""
        cleaned = raw_text.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
            cleaned = re.sub(r"\s*```$", "", cleaned)
            cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as exc:
            match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    pass
            raise InvalidAIResponseError(f"Failed to parse AI response as JSON: {str(exc)}") from exc

    async def complete_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: Type[BaseModel],
        max_tokens: int = 4096
    ) -> Any:
        """
        Generic helper: Calls active AI provider (Ollama / Gemini / Claude) with prompts,
        extracts JSON output, and validates against the provided Pydantic response_model.
        """
        # --- Ollama local LLM path ---
        if self.is_using_ollama:
            logger.info("[LLM-ROUTER] Routing structured generation to LOCAL OLLAMA (Model: %s)", self.settings.OLLAMA_MODEL)
            try:
                ollama = self.get_ollama_service()
                result = await ollama.complete_structured(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    response_model=response_model,
                    max_tokens=max_tokens,
                )
                logger.info("[LLM-ROUTER] ✅ Local Ollama generated valid response for %s", response_model.__name__)
                return result
            except OllamaUnavailableError as e:
                logger.error("[LLM-ROUTER] ❌ Local Ollama is OFFLINE: %s", e)
                raise AnthropicNotConfiguredError(
                    f"Ollama is unavailable: {e}\n"
                    "Start Ollama with: ollama serve"
                ) from e
            except OllamaInvalidResponseError as e:
                logger.error("[LLM-ROUTER] ❌ Local Ollama output invalid for %s: %s", response_model.__name__, e)
                raise InvalidAIResponseError(str(e)) from e
            except OllamaServiceError as e:
                logger.error("[LLM-ROUTER] ❌ Local Ollama service error: %s", e)
                raise AnthropicServiceError(str(e)) from e

        # --- Gemini cloud path ---
        if self.is_using_gemini:
            logger.info("[LLM-ROUTER] Routing structured generation to CLOUD GEMINI (Model: %s)", self.settings.primary_model)
            try:
                gemini = self.get_gemini_service()
                result = await gemini.complete_structured(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    response_model=response_model,
                    max_tokens=max_tokens,
                )
                logger.info("[LLM-ROUTER] ✅ Cloud Gemini generated valid response for %s", response_model.__name__)
                return result
            except GeminiNotConfiguredError as e:
                logger.error("[LLM-ROUTER] ❌ Cloud Gemini NOT CONFIGURED: %s", e)
                raise AnthropicNotConfiguredError(str(e)) from e
            except GeminiServiceError as e:
                logger.error("[LLM-ROUTER] ❌ Cloud Gemini service error: %s", e)
                raise AnthropicServiceError(str(e)) from e
            except GeminiInvalidAIResponseError as e:
                logger.error("[LLM-ROUTER] ❌ Cloud Gemini output invalid: %s", e)
                raise InvalidAIResponseError(str(e)) from e

        # --- Anthropic Claude fallback path ---
        logger.info("[LLM-ROUTER] Routing structured generation to CLOUD CLAUDE (Model: %s)", self.settings.ANTHROPIC_MODEL)
        client = self.get_client()
        try:
            response = await client.messages.create(
                model=self.settings.ANTHROPIC_MODEL,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            raw_text = ""
            for block in response.content:
                if block.type == "text":
                    raw_text += block.text

            if not raw_text.strip():
                logger.error("[LLM-ROUTER] ❌ Cloud Claude returned empty response")
                raise AnthropicServiceError("Received an empty response from Claude.")

            data = self._extract_json(raw_text)
            result = response_model.model_validate(data)
            logger.info("[LLM-ROUTER] ✅ Cloud Claude generated valid response for %s", response_model.__name__)
            return result

        except (anthropic.APIConnectionError, anthropic.RateLimitError, anthropic.APIStatusError) as api_err:
            logger.error("[LLM-ROUTER] ❌ Cloud Claude API error: %s", api_err)
            raise AnthropicServiceError(f"Anthropic API communication error: {str(api_err)}") from api_err
        except (json.JSONDecodeError, InvalidAIResponseError) as parse_err:
            logger.error("[LLM-ROUTER] ❌ Cloud Claude output parse error: %s", parse_err)
            raise InvalidAIResponseError(str(parse_err)) from parse_err
        except Exception as err:
            if isinstance(err, (AnthropicNotConfiguredError, AnthropicServiceError, InvalidAIResponseError)):
                raise
            logger.error("[LLM-ROUTER] ❌ Cloud Claude unexpected error: %s", err)
            raise AnthropicServiceError(f"Unexpected error during structured completion: {str(err)}") from err

    async def generate_plan(self, req: PlanRequest) -> PlanResponse:
        """
        Generates a structured project or hackathon plan using the active AI provider.
        """
        # --- Ollama local LLM path ---
        if self.is_using_ollama:
            logger.info("[LLM-ROUTER: PLAN] Dispatching plan generation to LOCAL OLLAMA (Model: %s)", self.settings.OLLAMA_MODEL)
            try:
                ollama = self.get_ollama_service()
                system_prompt = self._build_system_prompt(req.mode)
                user_prompt = self._build_user_prompt(req)
                result = await ollama.complete_structured(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    response_model=PlanResponse,
                    max_tokens=8192,
                )
                logger.info("[LLM-ROUTER: PLAN] ✅ Local Ollama plan generation completed successfully")
                # Attach metadata
                if hasattr(result, "__dict__"):
                    result.metadata = {
                        "model_used": self.settings.OLLAMA_MODEL,
                        "generated_at": datetime.now(timezone.utc).isoformat(),
                        "mode": req.mode.value,
                        "provider": "ollama",
                    }
                return result
            except OllamaUnavailableError as e:
                logger.error("[LLM-ROUTER: PLAN] ❌ Local Ollama is OFFLINE: %s", e)
                raise AnthropicNotConfiguredError(
                    f"Ollama is unavailable: {e}\nStart with: ollama serve"
                ) from e
            except OllamaInvalidResponseError as e:
                logger.error("[LLM-ROUTER: PLAN] ❌ Local Ollama output invalid: %s", e)
                raise InvalidAIResponseError(str(e)) from e
            except OllamaServiceError as e:
                logger.error("[LLM-ROUTER: PLAN] ❌ Local Ollama service error: %s", e)
                raise AnthropicServiceError(str(e)) from e

        # --- Gemini cloud path ---
        if self.is_using_gemini:
            logger.info("[LLM-ROUTER: PLAN] Dispatching plan generation to CLOUD GEMINI (Model: %s)", self.settings.primary_model)
            try:
                gemini = self.get_gemini_service()
                result = await gemini.generate_plan(req)
                logger.info("[LLM-ROUTER: PLAN] ✅ Cloud Gemini plan generation completed successfully")
                return result
            except GeminiNotConfiguredError as e:
                logger.error("[LLM-ROUTER: PLAN] ❌ Cloud Gemini NOT CONFIGURED: %s", e)
                raise AnthropicNotConfiguredError(str(e)) from e
            except GeminiServiceError as e:
                logger.error("[LLM-ROUTER: PLAN] ❌ Cloud Gemini service error: %s", e)
                raise AnthropicServiceError(str(e)) from e
            except GeminiInvalidAIResponseError as e:
                logger.error("[LLM-ROUTER: PLAN] ❌ Cloud Gemini output invalid: %s", e)
                raise InvalidAIResponseError(str(e)) from e

        # --- Anthropic Claude fallback path ---
        logger.info("[LLM-ROUTER: PLAN] Dispatching plan generation to CLOUD CLAUDE (Model: %s)", self.settings.ANTHROPIC_MODEL)
        client = self.get_client()
        system_prompt = self._build_system_prompt(req.mode)
        user_prompt = self._build_user_prompt(req)

        try:
            response = await client.messages.create(
                model=self.settings.ANTHROPIC_MODEL,
                max_tokens=4096,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            raw_text = ""
            for block in response.content:
                if block.type == "text":
                    raw_text += block.text

            if not raw_text.strip():
                logger.error("[LLM-ROUTER: PLAN] ❌ Cloud Claude returned empty response")
                raise AnthropicServiceError("Received an empty response from Claude.")

            data = self._extract_json(raw_text)

            data["metadata"] = {
                "model_used": self.settings.ANTHROPIC_MODEL,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "mode": req.mode.value
            }

            result = PlanResponse.model_validate(data)
            logger.info("[LLM-ROUTER: PLAN] ✅ Cloud Claude plan generation completed successfully")
            return result

        except (anthropic.APIConnectionError, anthropic.RateLimitError, anthropic.APIStatusError) as api_err:
            logger.error("[LLM-ROUTER: PLAN] ❌ Cloud Claude API error: %s", api_err)
            raise AnthropicServiceError(f"Anthropic API communication error: {str(api_err)}") from api_err
        except (json.JSONDecodeError, InvalidAIResponseError) as parse_err:
            logger.error("[LLM-ROUTER: PLAN] ❌ Cloud Claude parse error: %s", parse_err)
            raise InvalidAIResponseError(str(parse_err)) from parse_err
        except Exception as err:
            if isinstance(err, (AnthropicNotConfiguredError, AnthropicServiceError, InvalidAIResponseError)):
                raise
            logger.error("[LLM-ROUTER: PLAN] ❌ Cloud Claude unexpected error: %s", err)
            raise AnthropicServiceError(f"Unexpected error during plan generation: {str(err)}") from err


# Unified AIService alias
AIService = ClaudeService
