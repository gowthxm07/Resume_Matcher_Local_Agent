"""
Local LLM configuration for CrewAI agents.
Ensures 100% air-gapped, zero-cloud execution strictly using local Ollama.
"""

from typing import Any
from app.core.config import settings
from app.core.logging import logger

try:
    from crewai import LLM
except ImportError:
    LLM = None


def get_crewai_llm(temperature: float = 0.1) -> Any:
    """
    Return a CrewAI LLM instance strictly configured for local Ollama inference.
    Zero external network calls or cloud API tokens.
    """
    if LLM is None:
        logger.warning("CrewAI LLM class not available.")
        return None

    # Model format for LiteLLM/CrewAI Ollama integration: ollama/<model_name>
    model_str = f"ollama/{settings.OLLAMA_MODEL}"
    base_url = settings.OLLAMA_BASE_URL

    logger.debug(f"Initializing CrewAI LLM: {model_str} at {base_url}")
    return LLM(
        model=model_str,
        base_url=base_url,
        temperature=temperature,
        timeout=int(settings.OLLAMA_REQUEST_TIMEOUT),
    )
