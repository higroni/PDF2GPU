"""
Collections API Router - Endpoints za upravljanje kolekcijama.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.database import get_db
from backend.services.collection_service import CollectionService
from backend.services.pdf_service import PDFService
from backend.dependencies import get_collection_service, get_pdf_service


router = APIRouter(prefix="/collections", tags=["collections"])


# Pydantic schemas
class CollectionCreate(BaseModel):
    """Schema za kreiranje kolekcije."""
    name: str
    description: Optional[str] = None


class CollectionUpdate(BaseModel):
    """Schema za ažuriranje kolekcije."""
    name: Optional[str] = None
    description: Optional[str] = None


class CollectionResponse(BaseModel):
    """Schema za response kolekcije."""
    id: int
    name: str
    description: Optional[str]
    is_active: bool
    created_at: str
    
    class Config:
        from_attributes = True


class CollectionStatistics(BaseModel):
    """Schema za statistiku kolekcije."""
    id: int
    name: str
    description: Optional[str]
    is_active: bool
    created_at: Optional[str]
    pdf_count: int
    total_chunks: int
    qdrant_info: Optional[dict]


# Endpoints
@router.post("/", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
def create_collection(
    collection: CollectionCreate,
    db: Session = Depends(get_db),
    service: CollectionService = Depends(get_collection_service)
):
    """
    Kreira novu kolekciju.
    
    - **name**: Naziv kolekcije (unique)
    - **description**: Opis kolekcije (opciono)
    """
    try:
        new_collection = service.create_collection(
            db=db,
            name=collection.name,
            description=collection.description
        )
        return CollectionResponse(
            id=new_collection.id,
            name=new_collection.name,  # type: ignore
            description=new_collection.description,  # type: ignore
            is_active=new_collection.is_active,  # type: ignore
            created_at=new_collection.created_at.isoformat()  # type: ignore
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/", response_model=List[CollectionResponse])
def get_collections(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    service: CollectionService = Depends(get_collection_service)
):
    """
    Dobija sve kolekcije.
    
    - **skip**: Broj zapisa za preskočiti
    - **limit**: Maksimalan broj zapisa
    """
    collections = service.get_all_collections(db=db, skip=skip, limit=limit)
    return [
        CollectionResponse(
            id=c.id,
            name=c.name,  # type: ignore
            description=c.description,  # type: ignore
            is_active=c.is_active,  # type: ignore
            created_at=c.created_at.isoformat()  # type: ignore
        )
        for c in collections
    ]


@router.get("/active", response_model=Optional[CollectionResponse])
def get_active_collection(
    db: Session = Depends(get_db),
    service: CollectionService = Depends(get_collection_service)
):
    """Dobija aktivnu kolekciju."""
    collection = service.get_active_collection(db=db)
    if not collection:
        return None
    
    return CollectionResponse(
        id=collection.id,
        name=collection.name,  # type: ignore
        description=collection.description,  # type: ignore
        is_active=collection.is_active,  # type: ignore
        created_at=collection.created_at.isoformat()  # type: ignore
    )


@router.get("/{collection_id}", response_model=CollectionResponse)
def get_collection(
    collection_id: int,
    db: Session = Depends(get_db),
    service: CollectionService = Depends(get_collection_service)
):
    """Dobija kolekciju po ID-u."""
    collection = service.get_collection(db=db, collection_id=collection_id)
    if not collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kolekcija nije pronađena")
    
    return CollectionResponse(
        id=collection.id,
        name=collection.name,  # type: ignore
        description=collection.description,  # type: ignore
        is_active=collection.is_active,  # type: ignore
        created_at=collection.created_at.isoformat()  # type: ignore
    )


@router.get("/{collection_id}/statistics", response_model=CollectionStatistics)
def get_collection_statistics(
    collection_id: int,
    db: Session = Depends(get_db),
    service: CollectionService = Depends(get_collection_service)
):
    """Dobija statistiku o kolekciji."""
    stats = service.get_collection_statistics(db=db, collection_id=collection_id)
    if not stats:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kolekcija nije pronađena")
    
    return CollectionStatistics(**stats)


@router.put("/{collection_id}", response_model=CollectionResponse)
def update_collection(
    collection_id: int,
    collection: CollectionUpdate,
    db: Session = Depends(get_db),
    service: CollectionService = Depends(get_collection_service)
):
    """
    Ažurira kolekciju.
    
    - **name**: Novi naziv (opciono)
    - **description**: Novi opis (opciono)
    """
    try:
        updated = service.update_collection(
            db=db,
            collection_id=collection_id,
            name=collection.name,
            description=collection.description
        )
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kolekcija nije pronađena")
        
        return CollectionResponse(
            id=updated.id,
            name=updated.name,  # type: ignore
            description=updated.description,  # type: ignore
            is_active=updated.is_active,  # type: ignore
            created_at=updated.created_at.isoformat()  # type: ignore
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{collection_id}/activate", response_model=CollectionResponse)
def activate_collection(
    collection_id: int,
    db: Session = Depends(get_db),
    service: CollectionService = Depends(get_collection_service)
):
    """Postavlja kolekciju kao aktivnu."""
    collection = service.set_active_collection(db=db, collection_id=collection_id)
    if not collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kolekcija nije pronađena")
    
    return CollectionResponse(
        id=collection.id,
        name=collection.name,  # type: ignore
        description=collection.description,  # type: ignore
        is_active=collection.is_active,  # type: ignore
        created_at=collection.created_at.isoformat()  # type: ignore
    )


@router.delete("/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_collection(
    collection_id: int,
    db: Session = Depends(get_db),
    service: CollectionService = Depends(get_collection_service)
):
    """Briše kolekciju."""
    success = service.delete_collection(db=db, collection_id=collection_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kolekcija nije pronađena")
    
    return None


@router.post("/{collection_id}/clear", status_code=status.HTTP_204_NO_CONTENT)
def clear_collection(
    collection_id: int,
    db: Session = Depends(get_db),
    service: CollectionService = Depends(get_collection_service)
):
    """Čisti sve vektore iz kolekcije."""
    success = service.clear_collection(db=db, collection_id=collection_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kolekcija nije pronađena")
    
    return None


@router.get("/{collection_id}/pdfs", response_model=List[dict])
def get_collection_pdfs(
    collection_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    service: PDFService = Depends(get_pdf_service)
):
    """Dohvata sve PDF-ove iz kolekcije."""
    pdfs = service.get_pdfs_by_collection(
        db=db,
        collection_id=collection_id,
        skip=skip,
        limit=limit
    )
    
    return [
        {
            "id": pdf.id,
            "filename": pdf.filename,
            "file_size": pdf.size_bytes,
            "collection_id": pdf.collection_id,
            "status": pdf.status,
            "chunks_count": pdf.chunks_count,
            "processing_time": None,
            "uploaded_at": pdf.uploaded_at.isoformat() if pdf.uploaded_at is not None else None,
            "processed_at": pdf.processed_at.isoformat() if pdf.processed_at is not None else None,
            "error_message": pdf.error_message
        }
        for pdf in pdfs
    ]

# Made with Bob
