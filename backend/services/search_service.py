"""
Search Service - Biznis logika za pretragu dokumenata.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.models.collection import Collection
from backend.rag import RAGEngine


class SearchService:
    """Servis za pretragu dokumenata."""
    
    def __init__(self, rag_engine: RAGEngine):
        """
        Inicijalizuje Search servis.
        
        Args:
            rag_engine: RAG Engine instanca
        """
        self.rag_engine = rag_engine
    
    def search(
        self,
        db: Session,
        query: str,
        collection_id: Optional[int] = None,
        top_k: int = 5,
        use_reranking: bool = True,
        score_threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Pretražuje dokumente.
        
        Args:
            db: Database session
            query: Query tekst
            collection_id: ID kolekcije (None = aktivna kolekcija)
            top_k: Broj rezultata
            use_reranking: Da li koristiti reranking
            score_threshold: Minimalni score
            
        Returns:
            Dict sa rezultatima pretrage
            
        Raises:
            ValueError: Ako kolekcija ne postoji ili nije specificirana
        """
        # Dobij kolekciju
        if collection_id:
            collection = db.query(Collection).filter(Collection.id == collection_id).first()
            if not collection:
                raise ValueError(f"Kolekcija sa ID {collection_id} ne postoji")
        else:
            # Koristi aktivnu kolekciju
            collection = db.query(Collection).filter(Collection.is_active == True).first()
            if not collection:
                raise ValueError("Nema aktivne kolekcije")
        
        # Pretraži
        results = self.rag_engine.search(
            query=query,
            collection_name=collection.name,  # type: ignore
            top_k=top_k,
            use_reranking=use_reranking,
            score_threshold=score_threshold
        )
        
        return {
            'query': query,
            'collection_id': collection.id,
            'collection_name': collection.name,
            'results_count': len(results),
            'results': results,
            'use_reranking': use_reranking
        }
    
    def get_context(
        self,
        db: Session,
        query: str,
        collection_id: Optional[int] = None,
        top_k: int = 3,
        use_reranking: bool = True
    ) -> Dict[str, Any]:
        """
        Dobija kontekst za query (za LLM prompt).
        
        Args:
            db: Database session
            query: Query tekst
            collection_id: ID kolekcije (None = aktivna)
            top_k: Broj rezultata
            use_reranking: Da li koristiti reranking
            
        Returns:
            Dict sa kontekstom
        """
        # Dobij kolekciju
        if collection_id:
            collection = db.query(Collection).filter(Collection.id == collection_id).first()
            if not collection:
                raise ValueError(f"Kolekcija sa ID {collection_id} ne postoji")
        else:
            collection = db.query(Collection).filter(Collection.is_active == True).first()
            if not collection:
                raise ValueError("Nema aktivne kolekcije")
        
        # Dobij kontekst
        context = self.rag_engine.get_context(
            query=query,
            collection_name=collection.name,  # type: ignore
            top_k=top_k,
            use_reranking=use_reranking
        )
        
        return {
            'query': query,
            'collection_id': collection.id,
            'collection_name': collection.name,
            'context': context,
            'top_k': top_k
        }
    
    def search_multiple_collections(
        self,
        db: Session,
        query: str,
        collection_ids: List[int],
        top_k_per_collection: int = 3,
        use_reranking: bool = True
    ) -> Dict[str, Any]:
        """
        Pretražuje više kolekcija odjednom.
        
        Args:
            db: Database session
            query: Query tekst
            collection_ids: Lista ID-jeva kolekcija
            top_k_per_collection: Broj rezultata po kolekciji
            use_reranking: Da li koristiti reranking
            
        Returns:
            Dict sa rezultatima iz svih kolekcija
        """
        all_results = []
        
        for collection_id in collection_ids:
            collection = db.query(Collection).filter(Collection.id == collection_id).first()
            if not collection:
                continue
            
            try:
                results = self.rag_engine.search(
                    query=query,
                    collection_name=collection.name,  # type: ignore
                    top_k=top_k_per_collection,
                    use_reranking=use_reranking
                )
                
                # Dodaj collection info svakom rezultatu
                for result in results:
                    result['collection_id'] = collection.id
                    result['collection_name'] = collection.name
                
                all_results.extend(results)
                
            except Exception as e:
                print(f"Greška pri pretrazi kolekcije {collection.name}: {e}")
                continue
        
        # Sortiraj sve rezultate po score-u
        if use_reranking:
            all_results.sort(
                key=lambda x: x.get('combined_score', x.get('score', 0)),
                reverse=True
            )
        else:
            all_results.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return {
            'query': query,
            'collections_searched': len(collection_ids),
            'total_results': len(all_results),
            'results': all_results
        }
    
    def similar_documents(
        self,
        db: Session,
        document_text: str,
        collection_id: Optional[int] = None,
        top_k: int = 5,
        exclude_self: bool = True
    ) -> Dict[str, Any]:
        """
        Pronalazi slične dokumente.
        
        Args:
            db: Database session
            document_text: Tekst dokumenta
            collection_id: ID kolekcije (None = aktivna)
            top_k: Broj rezultata
            exclude_self: Da li isključiti isti dokument
            
        Returns:
            Dict sa sličnim dokumentima
        """
        # Koristi search sa dokumentom kao query-jem
        return self.search(
            db=db,
            query=document_text,
            collection_id=collection_id,
            top_k=top_k + 1 if exclude_self else top_k,
            use_reranking=False  # Ne treba reranking za similarity
        )

# Made with Bob
