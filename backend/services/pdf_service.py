"""
PDF Service - Biznis logika za upravljanje PDF dokumentima.
"""

from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime, UTC
from sqlalchemy.orm import Session
import shutil

from backend.models.pdf import PDF
from backend.models.collection import Collection
from backend.rag import RAGEngine


class PDFService:
    """Servis za upravljanje PDF dokumentima."""
    
    def __init__(self, rag_engine: RAGEngine):
        """
        Inicijalizuje PDF servis.
        
        Args:
            rag_engine: RAG Engine instanca
        """
        self.rag_engine = rag_engine
        self.upload_dir = Path("./uploads")
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    def upload_pdf(
        self,
        db: Session,
        file_path: str,
        original_filename: str,
        collection_id: int,
        chunking_strategy: str = "semantic",
        chunk_size: int = 500,
        overlap: int = 50
    ) -> PDF:
        """
        Upload-uje i procesira PDF dokument.
        
        Args:
            db: Database session
            file_path: Putanja do privremenog fajla
            original_filename: Originalni naziv fajla
            collection_id: ID kolekcije
            chunking_strategy: Strategija za chunking
            chunk_size: Veličina chunk-a
            overlap: Preklapanje
            
        Returns:
            PDF model instanca
            
        Raises:
            ValueError: Ako kolekcija ne postoji
            Exception: Ako dođe do greške pri procesiranju
        """
        # Proveri da li kolekcija postoji
        collection = db.query(Collection).filter(Collection.id == collection_id).first()
        if not collection:
            raise ValueError(f"Kolekcija sa ID {collection_id} ne postoji")
        
        # Kopiraj fajl u upload direktorijum
        file_name = f"{datetime.now(UTC).timestamp()}_{original_filename}"
        destination = self.upload_dir / file_name
        shutil.copy2(file_path, destination)
        
        # Kreiraj PDF zapis u bazi
        pdf = PDF(
            filename=original_filename,
            filepath=str(destination),
            size_bytes=destination.stat().st_size,
            pages=0,  # Will be updated after processing
            collection_id=collection_id,
            status="processing"
        )
        db.add(pdf)
        db.commit()
        db.refresh(pdf)
        
        try:
            # Procesiraj PDF sa RAG engine-om
            result = self.rag_engine.process_pdf(
                pdf_path=str(destination),
                collection_name=collection.name,
                chunking_strategy=chunking_strategy,
                chunk_size=chunk_size,
                overlap=overlap,
                metadata={
                    'pdf_id': pdf.id,
                    'collection_id': collection_id,
                    'original_filename': original_filename
                }
            )
            
            # Ažuriraj PDF zapis
            pdf.status = "completed"
            pdf.chunks_count = result['chunks_count']
            pdf.processing_time = result['processing_time']
            pdf.processed_at = datetime.now(UTC)
            
            db.commit()
            db.refresh(pdf)
            
            return pdf
            
        except Exception as e:
            # Označi kao failed
            pdf.status = "failed"
            pdf.error_message = str(e)
            db.commit()
            raise
    
    def get_pdf(self, db: Session, pdf_id: int) -> Optional[PDF]:
        """
        Dobija PDF po ID-u.
        
        Args:
            db: Database session
            pdf_id: PDF ID
            
        Returns:
            PDF instanca ili None
        """
        return db.query(PDF).filter(PDF.id == pdf_id).first()
    
    def get_pdfs_by_collection(
        self,
        db: Session,
        collection_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[PDF]:
        """
        Dobija sve PDF-ove u kolekciji.
        
        Args:
            db: Database session
            collection_id: Collection ID
            skip: Broj zapisa za preskočiti
            limit: Maksimalan broj zapisa
            
        Returns:
            Lista PDF instanci
        """
        return db.query(PDF)\
            .filter(PDF.collection_id == collection_id)\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    def get_all_pdfs(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[PDF]:
        """
        Dobija sve PDF-ove.
        
        Args:
            db: Database session
            skip: Broj zapisa za preskočiti
            limit: Maksimalan broj zapisa
            
        Returns:
            Lista PDF instanci
        """
        return db.query(PDF)\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    def delete_pdf(self, db: Session, pdf_id: int) -> bool:
        """
        Briše PDF dokument.
        
        Args:
            db: Database session
            pdf_id: PDF ID
            
        Returns:
            True ako je uspešno obrisano
        """
        pdf = self.get_pdf(db, pdf_id)
        if not pdf:
            return False
        
        # Obriši fajl sa diska
        try:
            file_path = Path(pdf.filepath)  # type: ignore
            if file_path.exists():
                file_path.unlink()
        except Exception as e:
            print(f"Greška pri brisanju fajla: {e}")
        
        # Obriši iz baze
        db.delete(pdf)
        db.commit()
        
        return True
    
    def get_pdf_statistics(self, db: Session, pdf_id: int) -> Optional[Dict[str, Any]]:
        """
        Dobija statistiku o PDF dokumentu.
        
        Args:
            db: Database session
            pdf_id: PDF ID
            
        Returns:
            Dict sa statistikom ili None
        """
        pdf = self.get_pdf(db, pdf_id)
        if not pdf:
            return None
        
        return {
            'id': pdf.id,
            'filename': pdf.filename,
            'file_size': pdf.size_bytes,  # type: ignore
            'chunks_count': pdf.chunks_count,
            'processing_time': None,  # Not stored in model
            'status': pdf.status,
            'uploaded_at': pdf.uploaded_at.isoformat() if pdf.uploaded_at else None,
            'processed_at': pdf.processed_at.isoformat() if pdf.processed_at else None,
            'collection_id': pdf.collection_id,
            'collection_name': pdf.collection.name if pdf.collection else None
        }
    
    def reprocess_pdf(
        self,
        db: Session,
        pdf_id: int,
        chunking_strategy: Optional[str] = None,
        chunk_size: Optional[int] = None,
        overlap: Optional[int] = None
    ) -> PDF:
        """
        Ponovo procesira PDF dokument.
        
        Args:
            db: Database session
            pdf_id: PDF ID
            chunking_strategy: Nova strategija (opciono)
            chunk_size: Nova veličina (opciono)
            overlap: Novo preklapanje (opciono)
            
        Returns:
            Ažuriran PDF
            
        Raises:
            ValueError: Ako PDF ne postoji
        """
        pdf = self.get_pdf(db, pdf_id)
        if not pdf:
            raise ValueError(f"PDF sa ID {pdf_id} ne postoji")
        
        # Koristi postojeće parametre ako nisu prosleđeni novi
        strategy = chunking_strategy or "semantic"
        size = chunk_size or 500
        ovlp = overlap or 50
        
        # Označi kao processing
        pdf.status = "processing"
        pdf.error_message = None
        db.commit()
        
        try:
            # Procesiraj ponovo
            result = self.rag_engine.process_pdf(
                pdf_path=pdf.file_path,
                collection_name=pdf.collection.name,
                chunking_strategy=strategy,
                chunk_size=size,
                overlap=ovlp,
                metadata={
                    'pdf_id': pdf.id,
                    'collection_id': pdf.collection_id,
                    'original_filename': pdf.filename
                }
            )
            
            # Ažuriraj
            pdf.status = "completed"
            pdf.chunks_count = result['chunks_count']
            pdf.processing_time = result['processing_time']
            pdf.processed_at = datetime.now(UTC)
            
            db.commit()
            db.refresh(pdf)
            
            return pdf
            
        except Exception as e:
            pdf.status = "failed"
            pdf.error_message = str(e)
            db.commit()
            raise

# Made with Bob
