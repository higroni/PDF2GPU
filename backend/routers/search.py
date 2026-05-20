"""
Search API Router - Endpoints za pretragu dokumenata.
"""

from typing import List, Optional, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.database import get_db
from backend.services.search_service import SearchService
from backend.dependencies import get_search_service


router = APIRouter(prefix="/search", tags=["search"])


# Pydantic schemas
class SearchRequest(BaseModel):
    """Schema za search zahtev."""
    query: str
    collection_id: Optional[int] = None
    top_k: int = 5
    use_reranking: bool = True
    score_threshold: Optional[float] = None


class SearchResponse(BaseModel):
    """Schema za search response."""
    query: str
    collection_id: int
    collection_name: str
    results_count: int
    results: List[Dict[str, Any]]
    use_reranking: bool


class ContextRequest(BaseModel):
    """Schema za context zahtev."""
    query: str
    collection_id: Optional[int] = None
    top_k: int = 3
    use_reranking: bool = True


class ContextResponse(BaseModel):
    """Schema za context response."""
    query: str
    collection_id: int
    collection_name: str
    context: str
    top_k: int


class MultiSearchRequest(BaseModel):
    """Schema za multi-collection search."""
    query: str
    collection_ids: List[int]
    top_k_per_collection: int = 3
    use_reranking: bool = True


class MultiSearchResponse(BaseModel):
    """Schema za multi-search response."""
    query: str
    collections_searched: int
    total_results: int
    results: List[Dict[str, Any]]


class SimilarRequest(BaseModel):
    """Schema za similar documents zahtev."""
    document_text: str
    collection_id: Optional[int] = None
    top_k: int = 5
    exclude_self: bool = True


# Endpoints
@router.post("/", response_model=SearchResponse)
def search(
    request: SearchRequest,
    db: Session = Depends(get_db),
    service: SearchService = Depends(get_search_service)
):
    """
    Pretražuje dokumente.
    
    - **query**: Query tekst
    - **collection_id**: ID kolekcije (None = aktivna kolekcija)
    - **top_k**: Broj rezultata
    - **use_reranking**: Da li koristiti reranking
    - **score_threshold**: Minimalni score (opciono)
    """
    try:
        result = service.search(
            db=db,
            query=request.query,
            collection_id=request.collection_id,
            top_k=request.top_k,
            use_reranking=request.use_reranking,
            score_threshold=request.score_threshold
        )
        return SearchResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/context", response_model=ContextResponse)
def get_context(
    request: ContextRequest,
    db: Session = Depends(get_db),
    service: SearchService = Depends(get_search_service)
):
    """
    Dobija kontekst za query (za LLM prompt).
    
    - **query**: Query tekst
    - **collection_id**: ID kolekcije (None = aktivna)
    - **top_k**: Broj rezultata
    - **use_reranking**: Da li koristiti reranking
    """
    try:
        result = service.get_context(
            db=db,
            query=request.query,
            collection_id=request.collection_id,
            top_k=request.top_k,
            use_reranking=request.use_reranking
        )
        return ContextResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/multiple", response_model=MultiSearchResponse)
def search_multiple(
    request: MultiSearchRequest,
    db: Session = Depends(get_db),
    service: SearchService = Depends(get_search_service)
):
    """
    Pretražuje više kolekcija odjednom.
    
    - **query**: Query tekst
    - **collection_ids**: Lista ID-jeva kolekcija
    - **top_k_per_collection**: Broj rezultata po kolekciji
    - **use_reranking**: Da li koristiti reranking
    """
    try:
        result = service.search_multiple_collections(
            db=db,
            query=request.query,
            collection_ids=request.collection_ids,
            top_k_per_collection=request.top_k_per_collection,
            use_reranking=request.use_reranking
        )
        return MultiSearchResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/similar", response_model=SearchResponse)
def find_similar(
    request: SimilarRequest,
    db: Session = Depends(get_db),
    service: SearchService = Depends(get_search_service)
):
    """
    Pronalazi slične dokumente.
    
    - **document_text**: Tekst dokumenta
    - **collection_id**: ID kolekcije (None = aktivna)
    - **top_k**: Broj rezultata
    - **exclude_self**: Da li isključiti isti dokument
    """
    try:
        result = service.similar_documents(
            db=db,
            document_text=request.document_text,
            collection_id=request.collection_id,
            top_k=request.top_k,
            exclude_self=request.exclude_self
        )
        return SearchResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# Made with Bob
