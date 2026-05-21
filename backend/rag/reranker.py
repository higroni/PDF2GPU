"""
Reranker Service - Poboljšanje relevantnosti rezultata pretrage.

Koristi BAAI/bge-reranker-v2-m3 sa GPU akceleracijom.
"""

from typing import List, Dict, Optional, Tuple
import torch
from sentence_transformers import CrossEncoder
import numpy as np
import logging

# Konfiguriši logger
logger = logging.getLogger(__name__)


class Reranker:
    """Servis za reranking rezultata pretrage."""
    
    def __init__(
        self,
        model_name: str = "BAAI/bge-reranker-v2-m3",
        device: Optional[str] = None,
        batch_size: int = 32
    ):
        """
        Inicijalizuje reranker.
        
        Args:
            model_name: Naziv modela (default: BAAI/bge-reranker-v2-m3)
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
        logger.info(f"Ucitavam reranker model: {model_name}")
        logger.info(f"Device: {self.device}")
        
        self.model = CrossEncoder(
            model_name,
            device=self.device,
            trust_remote_code=True
        )
        
        # Proveri GPU memoriju ako je dostupna
        if self.device == "cuda":
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            logger.info(f"GPU memorija: {gpu_memory:.2f} GB")
    
    def rerank(
        self,
        query: str,
        documents: List[str],
        top_k: Optional[int] = None
    ) -> List[Tuple[int, float]]:
        """
        Rerank-uje dokumente prema relevantnosti za query.
        
        Args:
            query: Query tekst
            documents: Lista dokumenata za reranking
            top_k: Broj top rezultata (None = svi)
            
        Returns:
            Lista tuple-ova (index, score) sortiranih po score-u
        """
        if not documents:
            return []
        
        # Kreiraj parove (query, document)
        pairs = [[query, doc] for doc in documents]
        
        # Predvidi score-ove
        scores = self.model.predict(
            pairs,
            batch_size=self.batch_size,
            show_progress_bar=False
        )
        
        # Sortiraj po score-u (descending)
        ranked_results = sorted(
            enumerate(scores),
            key=lambda x: float(x[1]),
            reverse=True
        )
        
        # Konvertuj u float tuple-ove
        ranked_results = [(idx, float(score)) for idx, score in ranked_results]
        
        # Vrati top_k rezultata ako je specificiran
        if top_k is not None:
            ranked_results = ranked_results[:top_k]
        
        return ranked_results
    
    def rerank_with_documents(
        self,
        query: str,
        documents: List[Dict],
        text_field: str = 'text',
        top_k: Optional[int] = None
    ) -> List[Dict]:
        """
        Rerank-uje dokumente i vraća ih sa score-om.
        
        Args:
            query: Query tekst
            documents: Lista dokumenata (dict-ova)
            text_field: Naziv polja sa tekstom u dokumentu
            top_k: Broj top rezultata
            
        Returns:
            Lista dokumenata sa dodanim 'rerank_score' poljem
        """
        if not documents:
            return []
        
        # Ekstraktuj tekstove
        texts = [doc.get(text_field, '') for doc in documents]
        
        # Rerank
        ranked_results = self.rerank(query, texts, top_k=top_k)
        
        # Dodaj score-ove dokumentima
        reranked_docs = []
        for idx, score in ranked_results:
            doc = documents[idx].copy()
            doc['rerank_score'] = float(score)
            doc['original_rank'] = idx
            reranked_docs.append(doc)
        
        return reranked_docs
    
    def rerank_search_results(
        self,
        query: str,
        search_results: List[Dict],
        text_field: str = 'text',
        top_k: Optional[int] = None,
        combine_scores: bool = True,
        rerank_weight: float = 0.7
    ) -> List[Dict]:
        """
        Rerank-uje rezultate pretrage i kombinuje score-ove.
        
        Args:
            query: Query tekst
            search_results: Rezultati pretrage sa 'score' poljem
            text_field: Naziv polja sa tekstom
            top_k: Broj top rezultata
            combine_scores: Da li kombinovati search i rerank score
            rerank_weight: Težina rerank score-a (0-1)
            
        Returns:
            Lista reranked rezultata
        """
        if not search_results:
            return []
        
        # Rerank
        reranked = self.rerank_with_documents(
            query=query,
            documents=search_results,
            text_field=text_field,
            top_k=None  # Rerank sve, pa onda kombinuj
        )
        
        # Kombinuj score-ove ako je potrebno
        if combine_scores:
            for doc in reranked:
                original_score = doc.get('score', 0.0)
                rerank_score = doc.get('rerank_score', 0.0)
                
                # Normalizuj rerank score (može biti negativan)
                # Sigmoid funkcija za normalizaciju u [0, 1]
                normalized_rerank = 1 / (1 + np.exp(-rerank_score))
                
                # Kombinuj score-ove
                combined_score = (
                    rerank_weight * normalized_rerank +
                    (1 - rerank_weight) * original_score
                )
                
                doc['combined_score'] = float(combined_score)
                doc['original_score'] = original_score
            
            # Sortiraj po kombinovanom score-u
            reranked.sort(key=lambda x: x.get('combined_score', 0), reverse=True)
        else:
            # Sortiraj samo po rerank score-u
            reranked.sort(key=lambda x: x.get('rerank_score', 0), reverse=True)
        
        # Vrati top_k rezultata
        if top_k is not None:
            reranked = reranked[:top_k]
        
        return reranked
    
    def get_device_info(self) -> dict:
        """
        Vraća informacije o device-u.
        
        Returns:
            Dict sa informacijama o device-u
        """
        info = {
            'device': self.device,
            'model_name': self.model_name,
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


class HybridReranker:
    """
    Hybrid reranker koji kombinuje više strategija.
    
    Može kombinovati:
    - Dense reranking (CrossEncoder)
    - Keyword matching
    - Custom scoring
    """
    
    def __init__(
        self,
        reranker_model: str = "BAAI/bge-reranker-v2-m3",
        device: Optional[str] = None,
        batch_size: int = 32
    ):
        """
        Inicijalizuje hybrid reranker.
        
        Args:
            reranker_model: Model za dense reranking
            device: Device za izvršavanje
            batch_size: Veličina batch-a
        """
        self.reranker = Reranker(
            model_name=reranker_model,
            device=device,
            batch_size=batch_size
        )
    
    def rerank(
        self,
        query: str,
        search_results: List[Dict],
        text_field: str = 'text',
        top_k: Optional[int] = None,
        rerank_weight: float = 0.7
    ) -> List[Dict]:
        """
        Rerank-uje rezultate koristeći hybrid pristup.
        
        Args:
            query: Query tekst
            search_results: Rezultati pretrage
            text_field: Naziv polja sa tekstom
            top_k: Broj top rezultata
            rerank_weight: Težina rerank score-a
            
        Returns:
            Lista reranked rezultata
        """
        return self.reranker.rerank_search_results(
            query=query,
            search_results=search_results,
            text_field=text_field,
            top_k=top_k,
            combine_scores=True,
            rerank_weight=rerank_weight
        )
    
    def get_device_info(self) -> dict:
        """Vraća informacije o device-u."""
        return self.reranker.get_device_info()
    
    def clear_cache(self):
        """Čisti GPU cache."""
        self.reranker.clear_cache()

# Made with Bob
