"""
Application Configuration Module
Loads and validates settings from environment variables and .env file.
"""

import os
import socket
from pathlib import Path
from functools import lru_cache
from typing import List
from dotenv import load_dotenv

# Prioritize IPv4 resolution to prevent Windows IPv6 SYN timeout when local network lacks IPv6 routing
try:
    _orig_getaddrinfo = socket.getaddrinfo

    def _ipv4_first_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        # Prefer AF_INET if family is unspecified (0)
        resolved_family = socket.AF_INET if family == 0 else family
        try:
            return _orig_getaddrinfo(host, port, resolved_family, type, proto, flags)
        except socket.gaierror:
            return _orig_getaddrinfo(host, port, family, type, proto, flags)

    socket.getaddrinfo = _ipv4_first_getaddrinfo
except Exception:
    pass

# Locate project root and backend directory to search for .env
BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent

# Check backend/.env first, then root .env
if (BASE_DIR / ".env").is_file():
    load_dotenv(BASE_DIR / ".env")
elif (ROOT_DIR / ".env").is_file():
    load_dotenv(ROOT_DIR / ".env")
else:
    load_dotenv()  # Fallback to system environment


class Settings:
    """Application runtime settings."""

    def __init__(self):
        # Reload environment from file if present
        if (BASE_DIR / ".env").is_file():
            load_dotenv(BASE_DIR / ".env", override=False)
        elif (ROOT_DIR / ".env").is_file():
            load_dotenv(ROOT_DIR / ".env", override=False)

        self.PROJECT_NAME: str = os.getenv("PROJECT_NAME", "AI Project Guide API")
        self.VERSION: str = "1.0.0"
        self.ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
        self.DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

        self.HOST: str = os.getenv("HOST", "127.0.0.1")
        self.PORT: int = int(os.getenv("PORT", "8000"))

        # AI Provider Selection: 'ollama' (default local), 'gemini', or 'claude'
        self.AI_PROVIDER: str = os.getenv("AI_PROVIDER", "ollama").lower()

        # Google Gemini AI Model Configuration (Optional / Legacy)
        self.GEMINI_API_KEY: str = (
            os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
        )
        self.GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")

        # Anthropic Claude AI Model Configuration (Optional / Legacy)
        self.ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
        self.ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

        # ----------------------------------------------------------------
        # Ollama Local LLM Configuration (Active AI Provider)
        # Dedicated hardware: NVIDIA GeForce MX550 (2GB VRAM) + 64GB RAM
        # ----------------------------------------------------------------
        self.OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen3:4b")
        # Context window: 8192 tokens tailored for 2GB VRAM + system RAM
        self.OLLAMA_CONTEXT_WINDOW: int = int(os.getenv("OLLAMA_CONTEXT_WINDOW", "8192"))
        # Temperature for structured project planning (0.2 for deterministic JSON)
        self.OLLAMA_TEMPERATURE: float = float(os.getenv("OLLAMA_TEMPERATURE", "0.2"))
        # Generation timeout in seconds
        self.OLLAMA_TIMEOUT_SECONDS: int = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "600"))

    # CORS configuration for Frontend connectivity
    @property
    def cors_origins(self) -> List[str]:
        raw_origins = os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173"
        )
        return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

    @property
    def is_gemini_configured(self) -> bool:
        """Check whether the Gemini API key has been supplied."""
        return bool(
            self.GEMINI_API_KEY
            and self.GEMINI_API_KEY != "your_gemini_api_key_here"
            and not self.GEMINI_API_KEY.startswith("your_")
        )

    @property
    def is_anthropic_configured(self) -> bool:
        """Check whether the Anthropic API key has been supplied."""
        return bool(
            self.ANTHROPIC_API_KEY
            and self.ANTHROPIC_API_KEY != "your_anthropic_api_key_here"
            and not self.ANTHROPIC_API_KEY.startswith("your_")
        )

    @property
    def is_ollama_configured(self) -> bool:
        """Ollama is 'configured' whenever AI_PROVIDER=ollama is set."""
        return self.AI_PROVIDER == "ollama"

    @property
    def is_ai_configured(self) -> bool:
        """Check whether the active AI provider is configured."""
        if self.AI_PROVIDER == "ollama":
            return True  # Connection check is done at request time
        if self.AI_PROVIDER == "gemini":
            return self.is_gemini_configured
        elif self.AI_PROVIDER == "claude":
            return self.is_anthropic_configured
        return self.is_gemini_configured or self.is_anthropic_configured

    @property
    def primary_model(self) -> str:
        """Return the active AI model name."""
        if self.AI_PROVIDER == "ollama":
            return self.OLLAMA_MODEL
        if self.AI_PROVIDER == "gemini":
            return self.GEMINI_MODEL
        return self.ANTHROPIC_MODEL


@lru_cache()
def get_settings() -> Settings:
    """Singleton getter for application settings."""
    return Settings()

settings = get_settings()
