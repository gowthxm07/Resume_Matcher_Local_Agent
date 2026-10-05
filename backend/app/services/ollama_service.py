"""
Dedicated Ollama service abstraction for local LLM inference.
Zero external cloud/LLM API calls.
Provides health checking, model verification, synchronous & async generation,
structured latency logging, and error handling.
"""

import time
from typing import Dict, Any, Optional, List
import httpx
from app.core.config import settings
from app.core.logging import logger, sanitize_for_log


class OllamaService:
    """
    Client service for local LLM inference via Ollama.
    Decoupled from agent implementations so it can be swapped or enhanced cleanly.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[float] = None,
    ):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL
        self.timeout = timeout or settings.OLLAMA_REQUEST_TIMEOUT

    async def check_availability(self) -> Dict[str, Any]:
        """
        Check if the local Ollama server is running and reachable.
        Returns reachability, response latency in ms, and error if any.
        """
        start_time = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                latency_ms = (time.perf_counter() - start_time) * 1000.0
                if response.status_code == 200:
                    return {
                        "reachable": True,
                        "latency_ms": round(latency_ms, 2),
                        "error": None,
                    }
                return {
                    "reachable": False,
                    "latency_ms": round(latency_ms, 2),
                    "error": f"Ollama returned HTTP {response.status_code}",
                }
        except httpx.ConnectError:
            return {
                "reachable": False,
                "latency_ms": None,
                "error": f"Could not connect to Ollama at {self.base_url}. Ensure Ollama is running locally.",
            }
        except Exception as exc:
            return {
                "reachable": False,
                "latency_ms": None,
                "error": str(exc),
            }

    async def list_models(self) -> List[str]:
        """Retrieve list of locally downloaded model names."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    models = [m.get("name", "") for m in data.get("models", [])]
                    return models
                return []
        except Exception as exc:
            logger.warning(f"Failed to fetch model list from Ollama: {exc}")
            return []

    async def model_exists(self, model_name: Optional[str] = None) -> bool:
        """Check whether the target model is installed locally in Ollama."""
        target = (model_name or self.model).lower()
        models = await self.list_models()
        # Handle matching with or without tag e.g. llama3.2:3b vs llama3.2
        target_base = target.split(":")[0]
        return any(
            m.lower() == target or m.lower().startswith(f"{target_base}:")
            for m in models
        )

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Generate a completion using the local Ollama LLM.

        Args:
            prompt: User/instruction prompt
            system_prompt: Optional system context
            model: Target model (defaults to configured model)
            temperature: Sampling temperature (default 0.2 for analytical tasks)
            max_tokens: Optional max token limit

        Returns:
            Dict containing response_text, latency_ms, tokens, and model details.
        """
        target_model = model or self.model
        start_time = time.perf_counter()

        payload: Dict[str, Any] = {
            "model": target_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
            },
        }

        if system_prompt:
            payload["system"] = system_prompt
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens

        logger.info(
            f"Sending prompt to local Ollama (model={target_model}, prompt_len={len(prompt)})"
        )

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                )

                latency_ms = (time.perf_counter() - start_time) * 1000.0

                if response.status_code != 200:
                    err_msg = f"Ollama HTTP {response.status_code}: {response.text}"
                    logger.error(err_msg)
                    return {
                        "success": False,
                        "response_text": "",
                        "latency_ms": round(latency_ms, 2),
                        "model": target_model,
                        "error": err_msg,
                    }

                data = response.json()
                response_text = data.get("response", "").strip()

                logger.info(
                    f"Ollama generation completed in {latency_ms:.1f}ms (eval_count={data.get('eval_count', 0)})"
                )

                return {
                    "success": True,
                    "response_text": response_text,
                    "latency_ms": round(latency_ms, 2),
                    "model": target_model,
                    "total_duration_ns": data.get("total_duration"),
                    "eval_count": data.get("eval_count"),
                    "error": None,
                }

        except httpx.TimeoutException:
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            err_msg = f"Ollama request timed out after {self.timeout}s"
            logger.error(err_msg)
            return {
                "success": False,
                "response_text": "",
                "latency_ms": round(latency_ms, 2),
                "model": target_model,
                "error": err_msg,
            }
        except httpx.ConnectError:
            err_msg = f"Cannot reach Ollama at {self.base_url}. Is Ollama running locally?"
            logger.error(err_msg)
            return {
                "success": False,
                "response_text": "",
                "latency_ms": 0.0,
                "model": target_model,
                "error": err_msg,
            }
        except Exception as exc:
            err_msg = f"Unexpected error during Ollama generation: {exc}"
            logger.error(err_msg)
            return {
                "success": False,
                "response_text": "",
                "latency_ms": 0.0,
                "model": target_model,
                "error": err_msg,
            }


# Singleton service instance
ollama_service = OllamaService()
