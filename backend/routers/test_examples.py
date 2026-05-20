"""
Test Examples Router
API endpoints za test primere
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from backend.database import get_db
from backend.services.test_example_service import TestExampleService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/test-examples", tags=["test-examples"])


# Pydantic schemas
class TestExampleCreate(BaseModel):
    """Schema za kreiranje test primera"""
    collection_id: int = Field(..., description="ID kolekcije")
    question: str = Field(..., min_length=1, max_length=1000, description="Pitanje")
    expected_answer: str = Field(..., min_length=1, max_length=5000, description="Očekivani odgovor")
    category: Optional[str] = Field(None, max_length=100, description="Kategorija")
    difficulty: str = Field("medium", pattern="^(easy|medium|hard)$", description="Težina")


class TestExampleUpdate(BaseModel):
    """Schema za ažuriranje test primera"""
    question: Optional[str] = Field(None, min_length=1, max_length=1000)
    expected_answer: Optional[str] = Field(None, min_length=1, max_length=5000)
    category: Optional[str] = Field(None, max_length=100)
    difficulty: Optional[str] = Field(None, pattern="^(easy|medium|hard)$")


class TestExampleResponse(BaseModel):
    """Schema za response"""
    id: int
    collection_id: int
    question: str
    expected_answer: str
    category: Optional[str]
    difficulty: str
    is_active: bool
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class BulkImportRequest(BaseModel):
    """Schema za bulk import"""
    collection_id: int
    test_examples: List[dict]


def get_test_example_service(db: Session = Depends(get_db)) -> TestExampleService:
    """Dependency za TestExampleService"""
    return TestExampleService(db)


@router.post("/", response_model=TestExampleResponse, status_code=201)
async def create_test_example(
    data: TestExampleCreate,
    service: TestExampleService = Depends(get_test_example_service)
):
    """Kreira novi test primer"""
    try:
        test_example = service.create_test_example(
            collection_id=data.collection_id,
            question=data.question,
            expected_answer=data.expected_answer,
            category=data.category,
            difficulty=data.difficulty
        )
        return TestExampleResponse(
            id=test_example.id,
            collection_id=test_example.collection_id,
            question=test_example.question,
            expected_answer=test_example.expected_answer,
            category=test_example.category,
            difficulty=test_example.difficulty,
            is_active=test_example.is_active,
            created_at=test_example.created_at.isoformat(),
            updated_at=test_example.updated_at.isoformat()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating test example: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[TestExampleResponse])
async def get_test_examples(
    collection_id: Optional[int] = Query(None, description="Filter po kolekciji"),
    category: Optional[str] = Query(None, description="Filter po kategoriji"),
    difficulty: Optional[str] = Query(None, description="Filter po težini"),
    skip: int = Query(0, ge=0, description="Broj za preskočiti"),
    limit: int = Query(100, ge=1, le=1000, description="Maksimalan broj rezultata"),
    service: TestExampleService = Depends(get_test_example_service)
):
    """Dohvata listu test primera"""
    try:
        test_examples = service.get_test_examples(
            collection_id=collection_id,
            category=category,
            difficulty=difficulty,
            skip=skip,
            limit=limit
        )
        return [
            TestExampleResponse(
                id=te.id,
                collection_id=te.collection_id,
                question=te.question,
                expected_answer=te.expected_answer,
                category=te.category,
                difficulty=te.difficulty,
                is_active=te.is_active,
                created_at=te.created_at.isoformat(),
                updated_at=te.updated_at.isoformat()
            )
            for te in test_examples
        ]
    except Exception as e:
        logger.error(f"Error getting test examples: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{test_example_id}", response_model=TestExampleResponse)
async def get_test_example(
    test_example_id: int,
    service: TestExampleService = Depends(get_test_example_service)
):
    """Dohvata pojedinačni test primer"""
    test_example = service.get_test_example(test_example_id)
    if not test_example:
        raise HTTPException(status_code=404, detail="Test primer nije pronađen")
    
    return TestExampleResponse(
        id=test_example.id,
        collection_id=test_example.collection_id,
        question=test_example.question,
        expected_answer=test_example.expected_answer,
        category=test_example.category,
        difficulty=test_example.difficulty,
        is_active=test_example.is_active,
        created_at=test_example.created_at.isoformat(),
        updated_at=test_example.updated_at.isoformat()
    )


@router.put("/{test_example_id}", response_model=TestExampleResponse)
async def update_test_example(
    test_example_id: int,
    data: TestExampleUpdate,
    service: TestExampleService = Depends(get_test_example_service)
):
    """Ažurira test primer"""
    try:
        test_example = service.update_test_example(
            test_example_id=test_example_id,
            question=data.question,
            expected_answer=data.expected_answer,
            category=data.category,
            difficulty=data.difficulty
        )
        return TestExampleResponse(
            id=test_example.id,
            collection_id=test_example.collection_id,
            question=test_example.question,
            expected_answer=test_example.expected_answer,
            category=test_example.category,
            difficulty=test_example.difficulty,
            is_active=test_example.is_active,
            created_at=test_example.created_at.isoformat(),
            updated_at=test_example.updated_at.isoformat()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating test example: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{test_example_id}", status_code=204)
async def delete_test_example(
    test_example_id: int,
    service: TestExampleService = Depends(get_test_example_service)
):
    """Briše test primer"""
    success = service.delete_test_example(test_example_id)
    if not success:
        raise HTTPException(status_code=404, detail="Test primer nije pronađen")
    return None


@router.post("/bulk-import")
async def bulk_import(
    data: BulkImportRequest,
    service: TestExampleService = Depends(get_test_example_service)
):
    """Bulk import test primera iz JSON-a"""
    try:
        # Prihvati i 'test_examples' i 'examples' kao ključ
        examples_data = data.test_examples if hasattr(data, 'test_examples') and data.test_examples else []
        result = service.bulk_import(data.collection_id, examples_data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error bulk importing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/json")
async def export_to_json(
    collection_id: Optional[int] = Query(None, description="Filter po kolekciji"),
    service: TestExampleService = Depends(get_test_example_service)
):
    """Export test primera u JSON format"""
    try:
        data = service.export_to_json(collection_id=collection_id)
        return JSONResponse(content=data)
    except Exception as e:
        logger.error(f"Error exporting: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary")
async def get_statistics(
    collection_id: Optional[int] = Query(None, description="Filter po kolekciji"),
    service: TestExampleService = Depends(get_test_example_service)
):
    """Dohvata statistiku test primera"""
    try:
        stats = service.get_statistics(collection_id=collection_id)
        return stats
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Made with Bob