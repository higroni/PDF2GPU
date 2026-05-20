"""
Backend Configuration
Centralna konfiguracija za PDF2GPU backend
"""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Glavne postavke aplikacije"""
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    PDF_DIR: Path = DATA_DIR / "pdfs"
    QDRANT_DIR: Path = DATA_DIR / "qdrant_storage"
    CONFIG_DIR: Path = BASE_DIR / "project_configs"
    
    # Database
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'pdf2gpu.db'}"
    
    # Qdrant
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_PATH: Optional[str] = str(QDRANT_DIR)
    
    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    DEFAULT_LLM_MODEL: str = "qwen2.5:14b"
    
    # Embedding Model
    EMBEDDING_MODEL: str = "BAAI/bge-m3"
    EMBEDDING_DIMENSIONS: int = 1024
    EMBEDDING_BATCH_SIZE: int = 128
    EMBEDDING_DEVICE: str = "cuda"  # cuda ili cpu
    
    # Reranker Model
    RERANKER_MODEL: str = "BAAI/bge-reranker-v2-m3"
    RERANKER_BATCH_SIZE: int = 32
    
    # RAG Config
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    CHUNKING_STRATEGY: str = "semantic"  # semantic, fixed, sentence
    
    SEARCH_TYPE: str = "hybrid"  # hybrid, semantic, bm25
    SEMANTIC_WEIGHT: float = 0.7
    BM25_WEIGHT: float = 0.3
    TOP_K: int = 10
    
    RERANKING_ENABLED: bool = True
    RERANKING_TOP_N: int = 5
    
    # LLM Config
    LLM_MODEL: str = "qwen2.5:14b"
    LLM_TEMPERATURE: float = 0.1
    LLM_TOP_P: float = 0.9
    LLM_TOP_K: int = 40
    LLM_MAX_TOKENS: int = 2048
    LLM_CONTEXT_WINDOW: int = 32768
    
    # System
    LOG_LEVEL: str = "INFO"
    DEBUG: bool = False
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True
    
    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]


# Singleton instance
settings = Settings()


def ensure_directories():
    """Kreira potrebne direktorijume ako ne postoje"""
    settings.DATA_DIR.mkdir(exist_ok=True)
    settings.PDF_DIR.mkdir(exist_ok=True)
    settings.QDRANT_DIR.mkdir(exist_ok=True)
    settings.CONFIG_DIR.mkdir(exist_ok=True)


# Kreiraj direktorijume pri importu
ensure_directories()

# Made with Bob
