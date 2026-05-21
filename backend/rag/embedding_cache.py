"""
Embedding Cache - In-memory LRU cache za embeddings.

Koristi hashlib za generisanje cache key-eva i functools.lru_cache za storage.
"""

import hashlib
import logging
from typing import Optional, List
from functools import lru_cache
import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingCache:
    """LRU cache za embeddings sa hash-based key generation."""
    
    def __init__(self, max_size: int = 10000):
        """
        Inicijalizuje embedding cache.
        
        Args:
            max_size: Maksimalan broj cached embeddings
        """
        self.max_size = max_size
        self._cache = {}
        self._access_order = []
        self.hits = 0
        self.misses = 0
        
        logger.info(f"Embedding cache initialized with max_size={max_size}")
    
    def _generate_key(self, text: str, model_name: str) -> str:
        """
        Generiše cache key na osnovu teksta i modela.
        
        Args:
            text: Tekst za embedding
            model_name: Naziv modela
            
        Returns:
            MD5 hash kao cache key
        """
        # Kombinuj text i model name za unique key
        combined = f"{text}|{model_name}"
        return hashlib.md5(combined.encode('utf-8')).hexdigest()
    
    def get(self, text: str, model_name: str) -> Optional[np.ndarray]:
        """
        Dohvata embedding iz cache-a.
        
        Args:
            text: Tekst
            model_name: Naziv modela
            
        Returns:
            Cached embedding ili None ako ne postoji
        """
        key = self._generate_key(text, model_name)
        
        if key in self._cache:
            self.hits += 1
            # Update access order (LRU)
            self._access_order.remove(key)
            self._access_order.append(key)
            return self._cache[key]
        
        self.misses += 1
        return None
    
    def put(self, text: str, model_name: str, embedding: np.ndarray):
        """
        Dodaje embedding u cache.
        
        Args:
            text: Tekst
            model_name: Naziv modela
            embedding: Embedding vektor
        """
        key = self._generate_key(text, model_name)
        
        # Proveri da li je cache pun
        if len(self._cache) >= self.max_size and key not in self._cache:
            # Ukloni najstariji (LRU)
            oldest_key = self._access_order.pop(0)
            del self._cache[oldest_key]
        
        # Dodaj novi ili update postojeći
        if key in self._cache:
            self._access_order.remove(key)
        
        self._cache[key] = embedding
        self._access_order.append(key)
    
    def get_batch(self, texts: List[str], model_name: str) -> tuple[List[Optional[np.ndarray]], List[int]]:
        """
        Dohvata batch embeddings iz cache-a.
        
        Args:
            texts: Lista tekstova
            model_name: Naziv modela
            
        Returns:
            Tuple (embeddings, missing_indices)
            - embeddings: Lista embeddings (None za missing)
            - missing_indices: Indeksi tekstova koji nisu u cache-u
        """
        embeddings = []
        missing_indices = []
        
        for i, text in enumerate(texts):
            embedding = self.get(text, model_name)
            embeddings.append(embedding)
            if embedding is None:
                missing_indices.append(i)
        
        return embeddings, missing_indices
    
    def put_batch(self, texts: List[str], model_name: str, embeddings: List[np.ndarray]):
        """
        Dodaje batch embeddings u cache.
        
        Args:
            texts: Lista tekstova
            model_name: Naziv modela
            embeddings: Lista embeddings
        """
        for text, embedding in zip(texts, embeddings):
            self.put(text, model_name, embedding)
    
    def clear(self):
        """Briše sve iz cache-a."""
        self._cache.clear()
        self._access_order.clear()
        self.hits = 0
        self.misses = 0
        logger.info("Embedding cache cleared")
    
    def get_stats(self) -> dict:
        """
        Vraća statistiku cache-a.
        
        Returns:
            Dict sa statistikom
        """
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'size': len(self._cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'total_requests': total_requests
        }
    
    def __len__(self) -> int:
        """Vraća broj cached embeddings."""
        return len(self._cache)


# Global cache instance
_global_cache: Optional[EmbeddingCache] = None


def get_global_cache(max_size: int = 10000) -> EmbeddingCache:
    """
    Dohvata ili kreira global cache instance.
    
    Args:
        max_size: Maksimalan broj cached embeddings
        
    Returns:
        Global cache instance
    """
    global _global_cache
    if _global_cache is None:
        _global_cache = EmbeddingCache(max_size=max_size)
    return _global_cache


def clear_global_cache():
    """Briše global cache."""
    global _global_cache
    if _global_cache is not None:
        _global_cache.clear()


# Made with Bob