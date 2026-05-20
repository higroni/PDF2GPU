"""
PDFs API Router - Endpoints za upravljanje PDF dokumentima.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
import tempfile
import os

from backend.database import get_db
from backend.services.pdf_service import PDFService
from backend.dependencies import get_pdf_service


router = APIRouter(prefix="/pdfs", tags=["pdfs"])


# Pydantic schemas
class PDFResponse(BaseModel):
    """Schema za response PDF-a."""
    id: int
    filename: str
    file_size: int
    collection_id: int
    status: str
    chunks_count: Optional[int]
    processing_time: Optional[float]
    uploaded_at: str
    processed_at: Optional[str]
    error_message: Optional[str]
    
    class Config:
        from_attributes = True


class PDFStatistics(BaseModel):
    """Schema za statistiku PDF-a."""
    id: int
    filename: str
    file_size: int
    chunks_count: Optional[int]
    processing_time: Optional[float]
    status: str
    uploaded_at: Optional[str]
    processed_at: Optional[str]
    collection_id: int
    collection_name: Optional[str]


class ReprocessRequest(BaseModel):
    """Schema za reprocessing zahtev."""
    chunking_strategy: Optional[str] = None
    chunk_size: Optional[int] = None
    overlap: Optional[int] = None


# Endpoints
@router.post("/upload", response_model=PDFResponse, status_code=status.HTTP_201_CREATED)
async def upload_pdf(
    file: UploadFile = File(...),
    collection_id: int = Form(...),
    chunking_strategy: str = Form("semantic"),
    chunk_size: int = Form(500),
    overlap: int = Form(50),
    db: Session = Depends(get_db),
    service: PDFService = Depends(get_pdf_service)
):
    """
    Upload-uje i procesira PDF dokument.
    
    - **file**: PDF fajl
    - **collection_id**: ID kolekcije
    - **chunking_strategy**: Strategija za chunking (semantic, fixed, sentence)
    - **chunk_size**: Veličina chunk-a u karakterima
    - **overlap**: Preklapanje između chunk-ova
    """
    # Proveri da li je PDF fajl
    if not file.filename or not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fajl mora biti PDF"
        )
    
    # Sačuvaj u privremeni fajl
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Procesiraj PDF
        pdf = service.upload_pdf(
            db=db,
            file_path=tmp_path,
            original_filename=file.filename,
            collection_id=collection_id,
            chunking_strategy=chunking_strategy,
            chunk_size=chunk_size,
            overlap=overlap
        )
        
        # Obriši privremeni fajl
        os.unlink(tmp_path)
        
        return PDFResponse(
            id=pdf.id,  # type: ignore
            filename=pdf.filename,  # type: ignore
            file_size=pdf.size_bytes,  # type: ignore
            collection_id=pdf.collection_id,  # type: ignore
            status=pdf.status,  # type: ignore
            chunks_count=pdf.chunks_count,  # type: ignore
            processing_time=None,  # Not stored in model
            uploaded_at=pdf.uploaded_at.isoformat(),  # type: ignore
            processed_at=pdf.processed_at.isoformat() if pdf.processed_at else None,  # type: ignore
            error_message=pdf.error_message  # type: ignore
        )
        
    except ValueError as e:
        if 'tmp_path' in locals():
            os.unlink(tmp_path)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        if 'tmp_path' in locals():
            os.unlink(tmp_path)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/", response_model=List[PDFResponse])
def get_pdfs(
    collection_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    service: PDFService = Depends(get_pdf_service)
):
    """
    Dobija PDF-ove.
    
    - **collection_id**: Filter po kolekciji (opciono)
    - **skip**: Broj zapisa za preskočiti
    - **limit**: Maksimalan broj zapisa
    """
    if collection_id:
        pdfs = service.get_pdfs_by_collection(
            db=db,
            collection_id=collection_id,
            skip=skip,
            limit=limit
        )
    else:
        pdfs = service.get_all_pdfs(db=db, skip=skip, limit=limit)
    
    return [
        PDFResponse(
            id=pdf.id,  # type: ignore
            filename=pdf.filename,  # type: ignore
            file_size=pdf.file_size,  # type: ignore
            collection_id=pdf.collection_id,  # type: ignore
            status=pdf.status,  # type: ignore
            chunks_count=pdf.chunks_count,  # type: ignore
            processing_time=pdf.processing_time,  # type: ignore
            uploaded_at=pdf.uploaded_at.isoformat(),  # type: ignore
            processed_at=pdf.processed_at.isoformat() if pdf.processed_at else None,  # type: ignore
            error_message=pdf.error_message  # type: ignore
        )
        for pdf in pdfs
    ]


@router.get("/{pdf_id}", response_model=PDFResponse)
def get_pdf(
    pdf_id: int,
    db: Session = Depends(get_db),
    service: PDFService = Depends(get_pdf_service)
):
    """Dobija PDF po ID-u."""
    pdf = service.get_pdf(db=db, pdf_id=pdf_id)
    if not pdf:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PDF nije pronađen")
    
    return PDFResponse(
        id=pdf.id,  # type: ignore
        filename=pdf.filename,  # type: ignore
        file_size=pdf.size_bytes,  # type: ignore
        collection_id=pdf.collection_id,  # type: ignore
        status=pdf.status,  # type: ignore
        chunks_count=pdf.chunks_count,  # type: ignore
        processing_time=None,  # type: ignore
        uploaded_at=pdf.uploaded_at.isoformat(),  # type: ignore
        processed_at=pdf.processed_at.isoformat() if pdf.processed_at else None,  # type: ignore
        error_message=pdf.error_message  # type: ignore
    )


@router.get("/{pdf_id}/statistics", response_model=PDFStatistics)
def get_pdf_statistics(
    pdf_id: int,
    db: Session = Depends(get_db),
    service: PDFService = Depends(get_pdf_service)
):
    """Dobija statistiku o PDF-u."""
    stats = service.get_pdf_statistics(db=db, pdf_id=pdf_id)
    if not stats:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PDF nije pronađen")
    
    return PDFStatistics(**stats)


@router.post("/{pdf_id}/reprocess", response_model=PDFResponse)
def reprocess_pdf(
    pdf_id: int,
    request: ReprocessRequest,
    db: Session = Depends(get_db),
    service: PDFService = Depends(get_pdf_service)
):
    """
    Ponovo procesira PDF dokument.
    
    - **chunking_strategy**: Nova strategija (opciono)
    - **chunk_size**: Nova veličina (opciono)
    - **overlap**: Novo preklapanje (opciono)
    """
    try:
        pdf = service.reprocess_pdf(
            db=db,
            pdf_id=pdf_id,
            chunking_strategy=request.chunking_strategy,
            chunk_size=request.chunk_size,
            overlap=request.overlap
        )
        
        return PDFResponse(
            id=pdf.id,  # type: ignore
            filename=pdf.filename,  # type: ignore
            file_size=pdf.file_size,  # type: ignore
            collection_id=pdf.collection_id,  # type: ignore
            status=pdf.status,  # type: ignore
            chunks_count=pdf.chunks_count,  # type: ignore
            processing_time=pdf.processing_time,  # type: ignore
            uploaded_at=pdf.uploaded_at.isoformat(),  # type: ignore
            processed_at=pdf.processed_at.isoformat() if pdf.processed_at else None,  # type: ignore
            error_message=pdf.error_message  # type: ignore
        )
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{pdf_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pdf(
    pdf_id: int,
    db: Session = Depends(get_db),
    service: PDFService = Depends(get_pdf_service)
):
    """Briše PDF dokument."""
    success = service.delete_pdf(db=db, pdf_id=pdf_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PDF nije pronađen")
    
    return None

# Made with Bob
