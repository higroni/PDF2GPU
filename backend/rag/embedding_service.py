"""
Embedding Service - Generisanje vektorskih reprezentacija teksta.

Koristi BAAI/bge-m3 model sa GPU akceleracijom za najbolje performanse.
"""

from typing import List, Optional
import torch
from sentence_transformers import SentenceTransformer
import numpy as np
import logging

# Konfiguriši logger
logger = logging.getLogger(__name__)


class EmbeddingService:
    """Servis za generisanje embeddings-a."""
    
    def __init__(
        self,
        model_name: str = "BAAI/bge-m3",
        device: Optional[str] = None,
        batch_size: int = 32
    ):
        """
        Inicijalizuje embedding servis.
        
        Args:
            model_name: Naziv modela (default: BAAI/bge-m3)
            device: Device za izvršavanje ('cuda', 'cpu', ili None za auto)
            batch_size: Veličina batch-a za procesiranje
        """
        self.model_name = model_name
        self.batch_size = batch_size
        
        # Automatski detektuj device ako nije specificiran
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        # Učitaj model
        logger.info(f"Ucitavam embedding model: {model_name}")
        logger.info(f"Device: {self.device}")
        
        try:
            # Pokušaj da učitaš model sa trust_remote_code
            self.model = SentenceTransformer(
                model_name,
                device=self.device,
                trust_remote_code=True
            )
        except Exception as e:
            logger.warning(f"Failed to load model on {self.device}: {e}")
            logger.info("Falling back to CPU...")
            self.device = "cpu"
            self.model = SentenceTransformer(
                model_name,
                device="cpu",
                trust_remote_code=True
            )
        
        # Dobij dimenzionalnost embeddings-a
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        print(f"Embedding dimenzija: {self.embedding_dim}")
        
        # Proveri GPU memoriju ako je dostupna
        if self.device == "cuda":
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            print(f"GPU memorija: {gpu_memory:.2f} GB")
    
    def encode(
        self,
        texts: List[str],
        show_progress: bool = False,
        normalize: bool = True
    ) -> np.ndarray:
        """
        Generiše embeddings za listu tekstova.
        
        Args:
            texts: Lista tekstova za enkodiranje
            show_progress: Da li prikazati progress bar
            normalize: Da li normalizovati vektore (za cosine similarity)
            
        Returns:
            NumPy array sa embeddings-ima (shape: [len(texts), embedding_dim])
        """
        if not texts:
            return np.array([])
        
        # Generiši embeddings
        embeddings = self.model.encode(
            texts,
            batch_size=self.batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True,
            normalize_embeddings=normalize
        )
        
        return embeddings
    
    def encode_single(self, text: str, normalize: bool = True) -> np.ndarray:
        """
        Generiše embedding za jedan tekst.
        
        Args:
            text: Tekst za enkodiranje
            normalize: Da li normalizovati vektor
            
        Returns:
            NumPy array sa embedding-om (shape: [embedding_dim])
        """
        embedding = self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=normalize
        )
        
        return embedding
    
    def encode_queries(
        self,
        queries: List[str],
        normalize: bool = True
    ) -> np.ndarray:
        """
        Generiše embeddings za query-je.
        
        Neki modeli (kao BGE) imaju specijalne instrukcije za query-je.
        
        Args:
            queries: Lista query-ja
            normalize: Da li normalizovati vektore
            
        Returns:
            NumPy array sa embeddings-ima
        """
        # Za BGE modele, dodaj query prefix
        if "bge" in self.model_name.lower():
            queries = [f"Represent this sentence for searching relevant passages: {q}" for q in queries]
        
        return self.encode(queries, normalize=normalize)
    
    def encode_documents(
        self,
        documents: List[str],
        show_progress: bool = False,
        normalize: bool = True
    ) -> np.ndarray:
        """
        Generiše embeddings za dokumente.
        
        Args:
            documents: Lista dokumenata
            show_progress: Da li prikazati progress bar
            normalize: Da li normalizovati vektore
            
        Returns:
            NumPy array sa embeddings-ima
        """
        return self.encode(documents, show_progress=show_progress, normalize=normalize)
    
    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Računa cosine similarity između dva embeddings-a.
        
        Args:
            embedding1: Prvi embedding
            embedding2: Drugi embedding
            
        Returns:
            Cosine similarity (0-1)
        """
        # Ako su embeddings-i normalizovani, cosine similarity je samo dot product
        return float(np.dot(embedding1, embedding2))
    
    def batch_similarity(
        self,
        query_embedding: np.ndarray,
        document_embeddings: np.ndarray
    ) -> np.ndarray:
        """
        Računa similarity između query-ja i svih dokumenata.
        
        Args:
            query_embedding: Query embedding (shape: [embedding_dim])
            document_embeddings: Document embeddings (shape: [n_docs, embedding_dim])
            
        Returns:
            Array sa similarity scores (shape: [n_docs])
        """
        # Matrix multiplication za batch cosine similarity
        return np.dot(document_embeddings, query_embedding)
    
    def get_device_info(self) -> dict:
        """
        Vraća informacije o device-u.
        
        Returns:
            Dict sa informacijama o device-u
        """
        info = {
            'device': self.device,
            'model_name': self.model_name,
            'embedding_dim': self.embedding_dim,
            'batch_size': self.batch_size
        }
        
        if self.device == "cuda":
            info['cuda_available'] = torch.cuda.is_available()
            info['cuda_device_count'] = torch.cuda.device_count()
            info['cuda_device_name'] = torch.cuda.get_device_name(0)
            info['cuda_memory_total'] = torch.cuda.get_device_properties(0).total_memory / 1024**3
            info['cuda_memory_allocated'] = torch.cuda.memory_allocated(0) / 1024**3
            info['cuda_memory_reserved'] = torch.cuda.memory_reserved(0) / 1024**3
        
        return info
    
    def clear_cache(self):
        """Čisti GPU cache ako je dostupan."""
        if self.device == "cuda":
            torch.cuda.empty_cache()
            logger.info("GPU cache ociscen")


class HybridEmbeddingService:
    """
    Hybrid embedding servis koji kombinuje dense i sparse embeddings.
    
    Dense embeddings: Semantička sličnost (BGE-M3)
    Sparse embeddings: Keyword matching (BM25-like)
    """
    
    def __init__(
        self,
        dense_model: str = "BAAI/bge-m3",
        device: Optional[str] = None,
        batch_size: int = 32
    ):
        """
        Inicijalizuje hybrid embedding servis.
        
        Args:
            dense_model: Model za dense embeddings
            device: Device za izvršavanje
            batch_size: Veličina batch-a
        """
        self.dense_service = EmbeddingService(
            model_name=dense_model,
            device=device,
            batch_size=batch_size
        )
    
    def encode_dense(
        self,
        texts: List[str],
        show_progress: bool = False
    ) -> np.ndarray:
        """Generiše dense embeddings."""
        return self.dense_service.encode(texts, show_progress=show_progress)
    
    def encode_query_dense(self, query: str) -> np.ndarray:
        """Generiše dense embedding za query."""
        return self.dense_service.encode_queries([query])[0]
    
    def get_device_info(self) -> dict:
        """Vraća informacije o device-u."""
        return self.dense_service.get_device_info()
    
    def clear_cache(self):
        """Čisti GPU cache."""
        self.dense_service.clear_cache()

# Made with Bob
