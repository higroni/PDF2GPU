"""
FastAPI Dependencies - Dependency injection za servise.
"""

from functools import lru_cache
from fastapi import Depends
from backend.rag import RAGEngine
from backend.services.collection_service import CollectionService
from backend.services.pdf_service import PDFService
from backend.services.search_service import SearchService
from backend.config import Settings


# Global singletons
_settings: Settings | None = None
_rag_engine: RAGEngine | None = None


def get_settings() -> Settings:
    """Dobija settings instancu (singleton)."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def get_rag_engine() -> RAGEngine:
    """
    Dobija RAG Engine instancu (singleton).
    
    Ova instanca se kreira samo jednom i deli između svih zahteva.
    """
    global _rag_engine
    if _rag_engine is not None:
        return _rag_engine
    
    settings = get_settings()
    qdrant_path = settings.QDRANT_PATH or "./data/qdrant_storage"
    
    try:
        _rag_engine = RAGEngine(
            embedding_model=settings.EMBEDDING_MODEL,
            reranker_model=settings.RERANKER_MODEL,
            qdrant_path=qdrant_path,
            device=None,  # Auto-detect (PyTorch 2.11.0+ supports RTX 5060 Ti sm_120)
            convert_cyrillic=True
        )
        return _rag_engine
    except Exception as e:
        print(f"WARNING: Failed to initialize RAG Engine: {e}")
        print("Creating minimal RAG Engine instance...")
        raise RuntimeError(f"RAG Engine initialization failed: {e}")


def get_collection_service() -> CollectionService:
    """Dobija Collection Service instancu."""
    rag_engine = get_rag_engine()
    return CollectionService(rag_engine=rag_engine)


def get_pdf_service() -> PDFService:
    """Dobija PDF Service instancu."""
    rag_engine = get_rag_engine()
    return PDFService(rag_engine=rag_engine)


def get_search_service() -> SearchService:
    """Dobija Search Service instancu."""
    rag_engine = get_rag_engine()
    return SearchService(rag_engine=rag_engine)

# Made with Bob
