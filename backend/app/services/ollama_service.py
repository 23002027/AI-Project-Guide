"""
Ollama Local LLM Service
========================
Single Project Planning Agent that routes all structured generation through
a locally-running Ollama instance via its HTTP API.

Dedicated Hardware Target:
- NVIDIA GeForce MX550 (2GB VRAM GDDR6) + 64GB+ System RAM
- Model: qwen3:4b (Q4_K_M quantization, 4.0B parameters)
- Context window: 8192 tokens
- Temperature: 0.2

Features:
- Progressive JSON extraction handling <think>...</think> tags and markdown blocks.
- Uses Ollama's native `"format": "json"` grammar enforcement.
- Real-time connection and model availability probes.
- Strict Pydantic model validation.
- Descriptive error handling for timeouts, disconnects, and malformed outputs.
"""

import json
import re
import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Type

import httpx
from pydantic import BaseModel, ValidationError

from backend.app.config import get_settings

# ---------------------------------------------------------------------------
# Module logger — all LLM activity is tagged [OllamaService]
# ---------------------------------------------------------------------------
logger = logging.getLogger("ollama_service")


# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------

class OllamaUnavailableError(Exception):
    """Raised when the Ollama service cannot be reached at the configured URL."""
    pass


class OllamaServiceError(Exception):
    """Raised on unexpected HTTP or communication errors from Ollama."""
    pass


class OllamaInvalidResponseError(Exception):
    """Raised when Ollama's output cannot be parsed into the expected JSON schema."""
    pass


# ---------------------------------------------------------------------------
# Ollama Service
# ---------------------------------------------------------------------------

class OllamaService:
    """
    Single Project Planning Agent backed by a locally-running Ollama instance.
    Routes all structured generation for university project blueprints.
    """

    def __init__(self):
        self.settings = get_settings()
        self._base_url: str = self.settings.OLLAMA_BASE_URL.rstrip("/")
        self._model: str = self.settings.OLLAMA_MODEL
        self._timeout: float = float(self.settings.OLLAMA_TIMEOUT_SECONDS)
        self._context_window: int = self.settings.OLLAMA_CONTEXT_WINDOW
        self._temperature: float = self.settings.OLLAMA_TEMPERATURE

    # ------------------------------------------------------------------
    # Connection health check & GPU inspection
    # ------------------------------------------------------------------

    async def check_connection(self) -> Dict[str, Any]:
        """
        Verifies Ollama is reachable, the configured model is pulled,
        and inspects process / GPU offloading info.
        Returns a dictionary for consumption by API health probes.
        """
        logger.info("[LLM-CHECK] Probing Ollama at %s (model: %s)", self._base_url, self._model)

        result: Dict[str, Any] = {
            "reachable": False,
            "model_available": False,
            "model": self._model,
            "base_url": self._base_url,
            "details": None,
            "gpu_info": None,
            "error": None,
            "available_models": [],
        }

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # 1. Verify Ollama tags
                tags_resp = await client.get(f"{self._base_url}/api/tags")
                tags_resp.raise_for_status()
                result["reachable"] = True
                logger.info("[LLM-CHECK] ✅ Ollama reachable at %s", self._base_url)

                tags_data = tags_resp.json()
                models = tags_data.get("models", [])
                available_names = [m.get("name", "") for m in models]
                result["available_models"] = available_names
                logger.info("[LLM-CHECK] Available models: %s", available_names)

                model_base = self._model.split(":")[0]
                model_match = next(
                    (m for m in models if m.get("name") == self._model or m.get("name", "").startswith(model_base)),
                    None
                )
                if model_match:
                    result["model_available"] = True
                    result["details"] = model_match.get("details", {})
                    logger.info("[LLM-CHECK] ✅ Target model '%s' is available", self._model)
                else:
                    logger.warning("[LLM-CHECK] ⚠️  Target model '%s' NOT found in Ollama. Available: %s", self._model, available_names)

                # 2. Inspect active process table (GPU VRAM offload)
                try:
                    ps_resp = await client.get(f"{self._base_url}/api/ps")
                    if ps_resp.status_code == 200:
                        ps_data = ps_resp.json()
                        running = ps_data.get("models", [])
                        active_model = next(
                            (m for m in running if model_base in m.get("name", "")),
                            None
                        )
                        if active_model:
                            vram_mb = round(active_model.get("size_vram", 0) / (1024 * 1024), 2)
                            total_mb = round(active_model.get("size", 0) / (1024 * 1024), 2)
                            result["gpu_info"] = {
                                "model": active_model.get("name"),
                                "size_vram_bytes": active_model.get("size_vram", 0),
                                "size_vram_mb": vram_mb,
                                "total_size_mb": total_mb,
                                "context_length": active_model.get("context_length"),
                                "runner": active_model.get("runner", "llamacpp"),
                            }
                            logger.info("[LLM-CHECK] 🖥️  GPU offload: %.1f MB VRAM / %.1f MB total", vram_mb, total_mb)
                        else:
                            logger.info("[LLM-CHECK] Model not currently loaded in GPU memory (will load on first request)")
                except Exception as ps_err:
                    logger.debug("[LLM-CHECK] Could not read /api/ps: %s", ps_err)

        except httpx.ConnectError:
            result["error"] = (
                f"Cannot connect to Ollama at {self._base_url}. "
                "Ensure Ollama is running (`ollama serve`)."
            )
            logger.error("[LLM-CHECK] ❌ Cannot connect to Ollama at %s — is `ollama serve` running?", self._base_url)
        except httpx.TimeoutException:
            result["error"] = f"Ollama health check timed out at {self._base_url}."
            logger.error("[LLM-CHECK] ❌ Connection timed out to Ollama at %s", self._base_url)
        except Exception as exc:
            result["error"] = f"Ollama health check failed: {exc}"
            logger.error("[LLM-CHECK] ❌ Unexpected error during health check: %s", exc)

        return result

    # ------------------------------------------------------------------
    # JSON extraction helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _strip_think_blocks(text: str) -> str:
        """Remove <think>...</think> reasoning blocks emitted by qwen3 models."""
        cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
        # Also clean up unclosed <think> tag if output was cut off
        cleaned = re.sub(r"<think>.*", "", cleaned, flags=re.DOTALL)
        return cleaned.strip()

    @staticmethod
    def _extract_json(raw_text: str) -> Dict[str, Any]:
        """
        Robust JSON extraction pipeline:
        1. Strip <think> reasoning blocks.
        2. Strip markdown fences (` ```json ... ``` `).
        3. Attempt direct parse.
        4. Fallback to scanning for the outermost matching `{ ... }`.
        """
        cleaned = OllamaService._strip_think_blocks(raw_text).strip()

        # Remove markdown fences
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
            cleaned = re.sub(r"\s*```$", "", cleaned)
            cleaned = cleaned.strip()

        # Direct json.loads
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # Regex scan for outermost curly braces
        match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        raise OllamaInvalidResponseError(
            f"Could not extract valid JSON from Ollama response. "
            f"Snippet: {raw_text[:300]!r}"
        )

    # ------------------------------------------------------------------
    # Core completion method
    # ------------------------------------------------------------------

    async def complete_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: Type[BaseModel],
        max_tokens: int = 8192,
    ) -> Any:
        """
        Sends system + user prompts to local Ollama via /api/chat,
        forces JSON formatting, extracts JSON, and validates with response_model.
        """
        req_start = time.perf_counter()
        logger.info(
            "[LLM-INSTANCE: OLLAMA] >>> INFERENCE REQUEST START | Model: %s | Target Schema: %s | Max Tokens: %d",
            self._model,
            response_model.__name__,
            max_tokens,
        )

        await self._assert_reachable()

        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "format": "json",
            "think": False,
            "stream": False,
            "options": {
                "temperature": self._temperature,
                "num_ctx": self._context_window,
                "num_predict": max_tokens,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    f"{self._base_url}/api/chat",
                    json=payload,
                )

                elapsed = time.perf_counter() - req_start

                if response.status_code != 200:
                    logger.error(
                        "[LLM-INSTANCE: OLLAMA] ❌ NOT WORKING | HTTP %d from %s/api/chat after %.2fs | Body: %s",
                        response.status_code,
                        self._base_url,
                        elapsed,
                        response.text[:300],
                    )
                    raise OllamaServiceError(
                        f"Ollama returned HTTP {response.status_code}: {response.text[:300]}"
                    )

                resp_data = response.json()
                raw_text: str = (
                    resp_data.get("message", {}).get("content", "")
                    or resp_data.get("response", "")
                )

                if not raw_text.strip():
                    logger.error(
                        "[LLM-INSTANCE: OLLAMA] ❌ NOT WORKING | Empty response received from model '%s' after %.2fs",
                        self._model,
                        elapsed,
                    )
                    raise OllamaInvalidResponseError(
                        f"Ollama returned an empty response for model '{self._model}'."
                    )

                logger.info(
                    "[LLM-INSTANCE: OLLAMA] ⚡ RAW OUTPUT RECEIVED | Length: %d chars | Latency: %.2fs",
                    len(raw_text),
                    elapsed,
                )

                data = self._extract_json(raw_text)

                try:
                    validated = response_model.model_validate(data)
                    logger.info(
                        "[LLM-INSTANCE: OLLAMA] ✅ WORKING PROPERLY | Generation + Validation Succeeded in %.2fs | Model: %s -> %s",
                        elapsed,
                        self._model,
                        response_model.__name__,
                    )
                    return validated
                except ValidationError as ve:
                    logger.error(
                        "[LLM-INSTANCE: OLLAMA] ❌ NOT WORKING (SCHEMA MISMATCH) | Pydantic validation failed for %s after %.2fs: %s",
                        response_model.__name__,
                        elapsed,
                        ve,
                    )
                    raise OllamaInvalidResponseError(
                        f"Pydantic validation failed for {response_model.__name__}: {ve}"
                    ) from ve

        except httpx.ConnectError as exc:
            elapsed = time.perf_counter() - req_start
            logger.error(
                "[LLM-INSTANCE: OLLAMA] ❌ NOT WORKING (OFFLINE/UNREACHABLE) | Cannot connect to Ollama at %s after %.2fs",
                self._base_url,
                elapsed,
            )
            raise OllamaUnavailableError(
                f"Cannot connect to Ollama at {self._base_url}. "
                "Please verify Ollama is running: `ollama serve`"
            ) from exc
        except httpx.TimeoutException as exc:
            elapsed = time.perf_counter() - req_start
            logger.error(
                "[LLM-INSTANCE: OLLAMA] ❌ NOT WORKING (TIMEOUT) | Request timed out after %.2fs (limit: %ss)",
                elapsed,
                self._timeout,
            )
            raise OllamaServiceError(
                f"Ollama generation timed out after {self._timeout}s. "
                "Consider reducing context length or increasing OLLAMA_TIMEOUT_SECONDS."
            ) from exc
        except (OllamaUnavailableError, OllamaServiceError, OllamaInvalidResponseError):
            raise
        except Exception as exc:
            elapsed = time.perf_counter() - req_start
            logger.error(
                "[LLM-INSTANCE: OLLAMA] ❌ NOT WORKING (UNEXPECTED ERROR) | %s after %.2fs",
                exc,
                elapsed,
            )
            raise OllamaServiceError(
                f"Unexpected error communicating with Ollama: {exc}"
            ) from exc

    # ------------------------------------------------------------------
    # Pre-flight check
    # ------------------------------------------------------------------

    async def _assert_reachable(self) -> None:
        """Fails fast with clear instructions if Ollama is offline."""
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                r = await client.get(f"{self._base_url}/api/tags")
                r.raise_for_status()
                logger.debug("[LLM-INSTANCE: OLLAMA] Pre-flight reachability check PASSED at %s", self._base_url)
        except httpx.ConnectError:
            logger.error("[LLM-INSTANCE: OLLAMA] ❌ NOT WORKING | Ollama is OFFLINE at %s", self._base_url)
            raise OllamaUnavailableError(
                f"Ollama is not running at {self._base_url}.\n"
                "To start Ollama on Windows:\n"
                "  1. Open a terminal and run: ollama serve\n"
                "  2. Verify the model is downloaded: ollama pull qwen3:4b\n"
                "  3. Check active model & GPU: ollama ps"
            )
        except Exception as exc:
            logger.error("[LLM-INSTANCE: OLLAMA] ❌ NOT WORKING | Pre-flight check failed: %s", exc)
            raise OllamaUnavailableError(
                f"Ollama pre-flight check failed: {exc}"
            ) from exc
