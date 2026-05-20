"""
Collection Service - Biznis logika za upravljanje kolekcijama.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, UTC

from backend.models.collection import Collection
from backend.rag import RAGEngine


class CollectionService:
    """Servis za upravljanje kolekcijama."""
    
    def __init__(self, rag_engine: RAGEngine):
        """
        Inicijalizuje Collection servis.
        
        Args:
            rag_engine: RAG Engine instanca
        """
        self.rag_engine = rag_engine
    
    def create_collection(
        self,
        db: Session,
        name: str,
        description: Optional[str] = None
    ) -> Collection:
        """
        Kreira novu kolekciju.
        
        Args:
            db: Database session
            name: Naziv kolekcije
            description: Opis kolekcije
            
        Returns:
            Collection instanca
            
        Raises:
            ValueError: Ako kolekcija sa tim imenom već postoji
        """
        # Proveri da li kolekcija već postoji
        existing = db.query(Collection).filter(Collection.name == name).first()
        if existing:
            raise ValueError(f"Kolekcija '{name}' već postoji")
        
        # Kreiraj kolekciju u bazi
        collection = Collection(
            name=name,
            description=description,
            is_active=False
        )
        db.add(collection)
        db.commit()
        db.refresh(collection)
        
        # Kreiraj kolekciju u Qdrant-u
        try:
            vector_size = self.rag_engine.embedding_service.embedding_dim
            if vector_size is None:
                raise ValueError("Embedding dimension is None")
                
            success = self.rag_engine.qdrant_service.create_collection(
                collection_name=name,
                vector_size=vector_size,
                distance="Cosine"
            )
            
            if not success:
                # Rollback ako Qdrant kreiranje nije uspelo
                db.delete(collection)
                db.commit()
                raise Exception("Neuspešno kreiranje Qdrant kolekcije")
            
            return collection
            
        except Exception as e:
            # Rollback ako dođe do greške
            db.delete(collection)
            db.commit()
            raise
    
    def get_collection(self, db: Session, collection_id: int) -> Optional[Collection]:
        """
        Dobija kolekciju po ID-u.
        
        Args:
            db: Database session
            collection_id: Collection ID
            
        Returns:
            Collection instanca ili None
        """
        return db.query(Collection).filter(Collection.id == collection_id).first()
    
    def get_collection_by_name(self, db: Session, name: str) -> Optional[Collection]:
        """
        Dobija kolekciju po imenu.
        
        Args:
            db: Database session
            name: Naziv kolekcije
            
        Returns:
            Collection instanca ili None
        """
        return db.query(Collection).filter(Collection.name == name).first()
    
    def get_all_collections(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Collection]:
        """
        Dobija sve kolekcije.
        
        Args:
            db: Database session
            skip: Broj zapisa za preskočiti
            limit: Maksimalan broj zapisa
            
        Returns:
            Lista Collection instanci
        """
        return db.query(Collection)\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    def update_collection(
        self,
        db: Session,
        collection_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Optional[Collection]:
        """
        Ažurira kolekciju.
        
        Args:
            db: Database session
            collection_id: Collection ID
            name: Novi naziv (opciono)
            description: Novi opis (opciono)
            
        Returns:
            Ažurirana Collection ili None
        """
        collection = self.get_collection(db, collection_id)
        if not collection:
            return None
        
        if name is not None:
            # Proveri da li novo ime već postoji
            existing = db.query(Collection)\
                .filter(Collection.name == name, Collection.id != collection_id)\
                .first()
            if existing:
                raise ValueError(f"Kolekcija '{name}' već postoji")
            collection.name = name  # type: ignore
        
        if description is not None:
            collection.description = description  # type: ignore
        
        db.commit()
        db.refresh(collection)
        
        return collection
    
    def delete_collection(self, db: Session, collection_id: int) -> bool:
        """
        Briše kolekciju.
        
        Args:
            db: Database session
            collection_id: Collection ID
            
        Returns:
            True ako je uspešno obrisano
        """
        collection = self.get_collection(db, collection_id)
        if not collection:
            return False
        
        # Obriši iz Qdrant-a
        try:
            self.rag_engine.qdrant_service.delete_collection(collection.name)  # type: ignore
        except Exception as e:
            print(f"Greška pri brisanju Qdrant kolekcije: {e}")
        
        # Obriši iz baze (cascade će obrisati i PDF-ove)
        db.delete(collection)
        db.commit()
        
        return True
    
    def set_active_collection(
        self,
        db: Session,
        collection_id: int
    ) -> Optional[Collection]:
        """
        Postavlja kolekciju kao aktivnu.
        
        Args:
            db: Database session
            collection_id: Collection ID
            
        Returns:
            Ažurirana Collection ili None
        """
        collection = self.get_collection(db, collection_id)
        if not collection:
            return None
        
        # Deaktiviraj sve ostale kolekcije
        db.query(Collection).update({Collection.is_active: False})
        
        # Aktiviraj ovu kolekciju
        collection.is_active = True  # type: ignore
        
        db.commit()
        db.refresh(collection)
        
        return collection
    
    def get_active_collection(self, db: Session) -> Optional[Collection]:
        """
        Dobija aktivnu kolekciju.
        
        Args:
            db: Database session
            
        Returns:
            Aktivna Collection ili None
        """
        return db.query(Collection).filter(Collection.is_active == True).first()
    
    def get_collection_statistics(
        self,
        db: Session,
        collection_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Dobija statistiku o kolekciji.
        
        Args:
            db: Database session
            collection_id: Collection ID
            
        Returns:
            Dict sa statistikom ili None
        """
        collection = self.get_collection(db, collection_id)
        if not collection:
            return None
        
        # Dobij info iz Qdrant-a
        qdrant_info = self.rag_engine.qdrant_service.get_collection_info(
            collection.name  # type: ignore
        )
        
        # Dobij broj PDF-ova
        pdf_count = len(collection.pdfs)  # type: ignore
        
        # Dobij ukupan broj chunk-ova iz PDF-ova
        total_chunks = sum(pdf.chunks_count or 0 for pdf in collection.pdfs)  # type: ignore
        
        return {
            'id': collection.id,
            'name': collection.name,
            'description': collection.description,
            'is_active': collection.is_active,
            'created_at': collection.created_at.isoformat() if collection.created_at else None,  # type: ignore
            'pdf_count': pdf_count,
            'total_chunks': total_chunks,
            'qdrant_info': qdrant_info
        }
    
    def clear_collection(self, db: Session, collection_id: int) -> bool:
        """
        Čisti sve vektore iz kolekcije (ali ne briše kolekciju).
        
        Args:
            db: Database session
            collection_id: Collection ID
            
        Returns:
            True ako je uspešno
        """
        collection = self.get_collection(db, collection_id)
        if not collection:
            return False
        
        # Očisti Qdrant kolekciju
        try:
            self.rag_engine.qdrant_service.clear_collection(collection.name)  # type: ignore
        except Exception as e:
            print(f"Greška pri čišćenju Qdrant kolekcije: {e}")
            return False
        
        # Obriši sve PDF-ove iz baze
        for pdf in collection.pdfs:  # type: ignore
            db.delete(pdf)
        
        db.commit()
        
        return True

# Made with Bob
