"""
RAG Engine - Glavni koordinator za Retrieval-Augmented Generation.

Integriše sve komponente: PDF processing, chunking, embeddings, 
vector search, reranking i LLM inference.
"""

from typing import List, Dict, Optional, Any
from pathlib import Path
import time
import logging

# Konfiguriši logger
logger = logging.getLogger(__name__)

from .pdf_processor import PDFProcessor
from .chunking import get_chunking_strategy, ChunkingStrategy
from .embedding_service import EmbeddingService
from .qdrant_service import QdrantService
from .reranker import Reranker
from .cyrillic_to_latin import convert_to_latin, is_cyrillic


class RAGEngine:
    """Glavni RAG engine koji koordinira sve komponente."""
    
    def __init__(
        self,
        embedding_model: str = "BAAI/bge-m3",
        reranker_model: str = "BAAI/bge-reranker-v2-m3",
        qdrant_path: str = "./qdrant_data",
        device: Optional[str] = None,
        convert_cyrillic: bool = True
    ):
        """
        Inicijalizuje RAG engine.
        
        Args:
            embedding_model: Model za embeddings
            reranker_model: Model za reranking
            qdrant_path: Putanja za Qdrant bazu
            device: Device za GPU ('cuda', 'cpu', ili None za auto)
            convert_cyrillic: Da li konvertovati ćirilicu u latinicu
        """
        logger.info("Inicijalizujem RAG Engine...")
        
        # Inicijalizuj komponente
        self.pdf_processor = PDFProcessor(convert_cyrillic=convert_cyrillic)
        self.embedding_service = EmbeddingService(
            model_name=embedding_model,
            device=device
        )
        self.reranker = Reranker(
            model_name=reranker_model,
            device=device
        )
        self.qdrant_service = QdrantService(path=qdrant_path)
        
        self.convert_cyrillic = convert_cyrillic
        
        logger.info("RAG Engine inicijalizovan")
    
    def process_pdf(
        self,
        pdf_path: str,
        collection_name: str,
        chunking_strategy: str = "semantic",
        chunk_size: int = 500,
        overlap: int = 50,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Procesira PDF dokument i dodaje ga u vektorsku bazu.
        
        Args:
            pdf_path: Putanja do PDF fajla
            collection_name: Naziv kolekcije
            chunking_strategy: Strategija za chunking ('semantic', 'fixed', 'sentence')
            chunk_size: Veličina chunk-a
            overlap: Preklapanje između chunk-ova
            metadata: Dodatni metapodaci
            
        Returns:
            Dict sa rezultatima procesiranja
        """
        start_time = time.time()
        
        logger.info(f"Procesiram PDF: {pdf_path}")
        
        # 1. Ekstraktuj tekst iz PDF-a
        logger.info("1. Ekstrakcija teksta...")
        text = self.pdf_processor.extract_text(pdf_path)
        logger.info(f"   Ekstraktovano {len(text)} karaktera")
        
        # 2. Podeli tekst na chunk-ove
        logger.info(f"2. Chunking ({chunking_strategy})...")
        chunker = get_chunking_strategy(
            chunking_strategy,
            chunk_size=chunk_size,
            overlap=overlap
        )
        chunks = chunker.chunk(text)
        logger.info(f"   Kreirano {len(chunks)} chunk-ova")
        
        # 3. Generiši embeddings
        logger.info("3. Generisanje embeddings...")
        chunk_texts = [chunk['text'] for chunk in chunks]
        embeddings = self.embedding_service.encode_documents(
            chunk_texts,
            show_progress=True
        )
        logger.info(f"   Generisano {len(embeddings)} embeddings")
        
        # 4. Kreiraj kolekciju ako ne postoji
        if not self.qdrant_service.collection_exists(collection_name):
            logger.info(f"4. Kreiranje kolekcije '{collection_name}'...")
            vector_size = self.embedding_service.embedding_dim
            if vector_size is None:
                raise ValueError("Embedding dimension is None")
            self.qdrant_service.create_collection(
                collection_name=collection_name,
                vector_size=vector_size,
                distance="Cosine"
            )
        
        # 5. Dodaj u vektorsku bazu
        logger.info("5. Dodavanje u vektorsku bazu...")
        
        # Pripremi payloads
        payloads = []
        for i, chunk in enumerate(chunks):
            payload = {
                'text': chunk['text'],
                'chunk_id': chunk['id'],
                'char_count': chunk['char_count'],
                'chunk_type': chunk['type'],
                'pdf_path': pdf_path,
                'pdf_name': Path(pdf_path).name
            }
            
            # Dodaj custom metadata ako postoji
            if metadata:
                payload.update(metadata)
            
            payloads.append(payload)
        
        # Dodaj vektore (konvertuj numpy array u listu)
        vectors_list = [embeddings[i] for i in range(len(embeddings))]
        success = self.qdrant_service.add_vectors(
            collection_name=collection_name,
            vectors=vectors_list,
            payloads=payloads
        )
        
        elapsed_time = time.time() - start_time
        
        result = {
            'success': success,
            'pdf_path': pdf_path,
            'collection_name': collection_name,
            'chunks_count': len(chunks),
            'embeddings_count': len(embeddings),
            'processing_time': elapsed_time,
            'chunking_strategy': chunking_strategy,
            'chunk_size': chunk_size,
            'overlap': overlap
        }
        
        logger.info(f"PDF procesiran za {elapsed_time:.2f}s")
        
        return result
    
    def search(
        self,
        query: str,
        collection_name: str,
        top_k: int = 5,
        use_reranking: bool = True,
        rerank_top_k: Optional[int] = None,
        score_threshold: Optional[float] = None
    ) -> List[Dict]:
        """
        Pretražuje vektorsku bazu.
        
        Args:
            query: Query tekst
            collection_name: Naziv kolekcije
            top_k: Broj rezultata za vraćanje
            use_reranking: Da li koristiti reranking
            rerank_top_k: Broj rezultata za reranking (None = top_k * 3)
            score_threshold: Minimalni score
            
        Returns:
            Lista rezultata
        """
        start_time = time.time()
        
        # Konvertuj query u latinicu ako je potrebno
        if self.convert_cyrillic and is_cyrillic(query):
            query = convert_to_latin(query)
        
        # 1. Generiši query embedding
        query_embedding = self.embedding_service.encode_queries([query])[0]
        
        # 2. Pretraži vektorsku bazu
        # Ako koristimo reranking, uzmi više rezultata
        search_limit = rerank_top_k if use_reranking and rerank_top_k else (top_k * 3 if use_reranking else top_k)
        
        results = self.qdrant_service.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            limit=search_limit,
            score_threshold=score_threshold
        )
        
        # 3. Reranking ako je potrebno
        if use_reranking and results:
            results = self.reranker.rerank_search_results(
                query=query,
                search_results=results,
                text_field='text',
                top_k=top_k,
                combine_scores=True,
                rerank_weight=0.7
            )
        else:
            # Samo ograniči na top_k
            results = results[:top_k]
        
        elapsed_time = time.time() - start_time
        
        # Dodaj metadata
        for result in results:
            result['search_time'] = elapsed_time
            result['query'] = query
        
        return results
    
    def get_context(
        self,
        query: str,
        collection_name: str,
        top_k: int = 3,
        use_reranking: bool = True
    ) -> str:
        """
        Dobija kontekst za query (za LLM prompt).
        
        Args:
            query: Query tekst
            collection_name: Naziv kolekcije
            top_k: Broj rezultata
            use_reranking: Da li koristiti reranking
            
        Returns:
            Formatiran kontekst string
        """
        results = self.search(
            query=query,
            collection_name=collection_name,
            top_k=top_k,
            use_reranking=use_reranking
        )
        
        if not results:
            return "Nema pronađenih relevantnih dokumenata."
        
        # Formatiraj kontekst
        context_parts = []
        for i, result in enumerate(results, 1):
            text = result['payload']['text']
            score = result.get('combined_score', result.get('score', 0))
            
            context_parts.append(f"[Dokument {i}] (relevantnost: {score:.3f})\n{text}")
        
        return "\n\n".join(context_parts)
    
    def get_device_info(self) -> Dict:
        """Vraća informacije o device-ima."""
        return {
            'embedding_service': self.embedding_service.get_device_info(),
            'reranker': self.reranker.get_device_info()
        }
    
    def clear_cache(self):
        """Čisti GPU cache."""
        self.embedding_service.clear_cache()
        self.reranker.clear_cache()
    
    def get_collection_info(self, collection_name: str) -> Optional[Dict]:
        """Vraća informacije o kolekciji."""
        return self.qdrant_service.get_collection_info(collection_name)
    
    def list_collections(self) -> List[str]:
        """Vraća listu svih kolekcija."""
        return self.qdrant_service.list_collections()
    
    def delete_collection(self, collection_name: str) -> bool:
        """Briše kolekciju."""
        return self.qdrant_service.delete_collection(collection_name)

# Made with Bob
