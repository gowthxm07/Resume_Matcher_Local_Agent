"""
Local embedding service abstraction utilizing Ollama.
Ensures zero external cloud embedding API dependencies.
Used to embed resume sections, job description requirements, and project evidence.
"""

import time
from typing import List, Dict, Any, Optional
import httpx
from app.core.config import settings
from app.core.logging import logger


class EmbeddingService:
    """
    Service responsible for computing text embeddings locally via Ollama.
    Supports single queries and batch embedding generation.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[float] = None,
    ):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or settings.OLLAMA_EMBED_MODEL
        self.timeout = timeout or settings.OLLAMA_REQUEST_TIMEOUT

    async def check_availability(self) -> Dict[str, Any]:
        """Verify if the embedding model is available on the local Ollama instance."""
        start_time = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                latency_ms = (time.perf_counter() - start_time) * 1000.0

                if response.status_code == 200:
                    models = [m.get("name", "").lower() for m in response.json().get("models", [])]
                    target = self.model.lower()
                    target_base = target.split(":")[0]
                    exists = any(m == target or m.startswith(f"{target_base}:") for m in models)
                    return {
                        "available": exists,
                        "model": self.model,
                        "latency_ms": round(latency_ms, 2),
                        "installed_models": models,
                        "error": None if exists else f"Embedding model '{self.model}' not found in Ollama",
                    }
                return {
                    "available": False,
                    "model": self.model,
                    "latency_ms": round(latency_ms, 2),
                    "error": f"Ollama returned HTTP {response.status_code}",
                }
        except Exception as exc:
            return {
                "available": False,
                "model": self.model,
                "latency_ms": None,
                "error": str(exc),
            }

    async def get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for a single text chunk using local Ollama.

        Args:
            text: Input string to embed

        Returns:
            List[float] representing dense semantic vector
        """
        if not text or not text.strip():
            raise ValueError("Cannot generate embedding for empty text")

        start_time = time.perf_counter()
        payload = {
            "model": self.model,
            "prompt": text,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/embeddings",
                    json=payload,
                )

                latency_ms = (time.perf_counter() - start_time) * 1000.0

                if response.status_code != 200:
                    raise RuntimeError(
                        f"Ollama embeddings endpoint returned {response.status_code}: {response.text}"
                    )

                data = response.json()
                embedding = data.get("embedding", [])
                if not embedding:
                    raise RuntimeError("Ollama returned an empty embedding vector")

                logger.debug(
                    f"Generated embedding (dim={len(embedding)}) in {latency_ms:.1f}ms for text length {len(text)}"
                )
                return embedding

        except Exception as exc:
            logger.error(f"Failed to generate embedding with local Ollama: {exc}")
            raise

    async def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings sequentially or concurrently for a list of text chunks.
        """
        embeddings: List[List[float]] = []
        for text in texts:
            emb = await self.get_embedding(text)
            embeddings.append(emb)
        return embeddings


# Singleton embedding service instance
embedding_service = EmbeddingService()
