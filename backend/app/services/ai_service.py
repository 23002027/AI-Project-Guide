"""
Unified AI Service Provider Interface.
Exports OllamaService (local), GeminiService (cloud), ClaudeService, and unified exceptions.
"""

from backend.app.services.ollama_service import (
    OllamaService,
    OllamaUnavailableError,
    OllamaServiceError,
    OllamaInvalidResponseError,
)
from backend.app.services.gemini_service import (
    GeminiService,
    GeminiNotConfiguredError,
    GeminiServiceError,
    InvalidAIResponseError,
)
from backend.app.services.claude_service import (
    ClaudeService,
    AIService,
    AINotConfiguredError,
    AIServiceError,
    AnthropicNotConfiguredError,
    AnthropicServiceError,
)

__all__ = [
    # Ollama local LLM
    "OllamaService",
    "OllamaUnavailableError",
    "OllamaServiceError",
    "OllamaInvalidResponseError",
    # Gemini cloud
    "GeminiService",
    "GeminiNotConfiguredError",
    "GeminiServiceError",
    # Unified
    "AIService",
    "ClaudeService",
    "AINotConfiguredError",
    "AIServiceError",
    "AnthropicNotConfiguredError",
    "AnthropicServiceError",
    "InvalidAIResponseError",
]
