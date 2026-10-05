"""
Local vector store abstraction for CareerCrew.
Enforces local-only storage (ChromaDB / FAISS) with zero cloud vector store dependencies.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.core.logging import logger


class VectorStoreBase(ABC):
    """Abstract interface defining operations for local vector storage."""

    @abstractmethod
    def initialize(self) -> None:
        """Initialize the vector database storage client."""
        pass

    @abstractmethod
    def add_texts(
        self,
        collection_name: str,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """Insert embedded text records into a named collection."""
        pass

    @abstractmethod
    def query(
        self,
        collection_name: str,
        query_embedding: List[float],
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Search for top_k nearest neighbors by embedding vector."""
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Inspect storage health, collection counts, and persistence path."""
        pass


class ChromaVectorStore(VectorStoreBase):
    """
    Lightweight local Chroma vector database implementation.
    Persists vectors directly to disk in data/embeddings/chroma.
    """

    def __init__(self, persist_directory: Optional[Path] = None):
        self.persist_directory = persist_directory or settings.VECTOR_STORE_DIR
        self._client = None
        self._initialized = False

    def initialize(self) -> None:
        """Initialize or connect to local Chroma persistent storage."""
        if self._initialized:
            return

        try:
            self.persist_directory.mkdir(parents=True, exist_ok=True)
            import chromadb
            from chromadb.config import Settings as ChromaSettings

            self._client = chromadb.PersistentClient(
                path=str(self.persist_directory),
                settings=ChromaSettings(anonymized_telemetry=False, is_persistent=True),
            )
            self._initialized = True
            logger.info(
                f"Local Chroma vector store initialized at: {self.persist_directory}"
            )
        except Exception as exc:
            logger.error(f"Failed to initialize Chroma vector store: {exc}")
            self._initialized = False
            raise

    def get_collection(self, collection_name: str):
        """Retrieve or create a local collection."""
        if not self._initialized:
            self.initialize()
        return self._client.get_or_create_collection(name=collection_name)

    def add_texts(
        self,
        collection_name: str,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """Store documents and their pre-computed embeddings."""
        if not self._initialized:
            self.initialize()

        import uuid

        if ids is None:
            ids = [uuid.uuid4().hex for _ in texts]
        if metadatas is None:
            metadatas = [{} for _ in texts]

        # Sanitize metadata to ensure no None values or invalid types for Chroma
        clean_metadatas = []
        for meta in metadatas:
            clean = {}
            for k, v in meta.items():
                if isinstance(v, (str, int, float, bool)):
                    clean[k] = v
                elif v is not None:
                    clean[k] = str(v)
            clean_metadatas.append(clean)

        collection = self.get_collection(collection_name)
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=clean_metadatas,
        )
        return ids

    def query(
        self,
        collection_name: str,
        query_embedding: List[float],
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Query nearest neighbors by vector similarity."""
        if not self._initialized:
            self.initialize()

        collection = self.get_collection(collection_name)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_metadata if filter_metadata else None,
        )

        formatted_results: List[Dict[str, Any]] = []
        if results and results.get("ids") and len(results["ids"]) > 0:
            for idx in range(len(results["ids"][0])):
                formatted_results.append({
                    "id": results["ids"][0][idx],
                    "document": results["documents"][0][idx] if results.get("documents") else "",
                    "metadata": results["metadatas"][0][idx] if results.get("metadatas") else {},
                    "distance": results["distances"][0][idx] if results.get("distances") else None,
                })

        return formatted_results

    def get_stats(self) -> Dict[str, Any]:
        """Inspect vector store status."""
        try:
            if not self._initialized:
                self.initialize()

            collections = self._client.list_collections()
            collection_names = [c.name for c in collections]

            return {
                "status": "healthy",
                "store_type": "chroma",
                "storage_path": str(self.persist_directory),
                "collection_count": len(collection_names),
                "collections": collection_names,
                "error": None,
            }
        except Exception as exc:
            return {
                "status": "degraded",
                "store_type": "chroma",
                "storage_path": str(self.persist_directory),
                "collection_count": 0,
                "collections": [],
                "error": str(exc),
            }


# Singleton vector store instance
vector_store = ChromaVectorStore()
