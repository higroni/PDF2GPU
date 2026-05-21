"""
Evaluations Router
API endpoints za evaluaciju test primera
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from backend.database import get_db
from backend.services.evaluation_service import EvaluationService
from backend.models.evaluation import Evaluation
from backend.models.test_example_result import TestExampleResult

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/evaluations", tags=["evaluations"])


# Pydantic schemas
class EvaluationCreate(BaseModel):
    """Schema za kreiranje evaluacije"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


class EvaluationRun(BaseModel):
    """Schema za pokretanje evaluacije"""
    test_example_ids: Optional[List[int]] = None
    collection_id: Optional[int] = None


class EvaluationResponse(BaseModel):
    """Schema za evaluaciju response"""
    id: int
    name: str
    description: Optional[str]
    status: str
    created_at: str
    started_at: Optional[str]
    completed_at: Optional[str]
    total_examples: Optional[int]
    completed_examples: Optional[int]
    avg_bleu_score: Optional[float]
    avg_rouge_1: Optional[float]
    avg_rouge_2: Optional[float]
    avg_rouge_l: Optional[float]
    avg_bert_score: Optional[float]
    exact_match_percentage: Optional[float]
    
    class Config:
        from_attributes = True


class TestExampleResultResponse(BaseModel):
    """Schema za rezultat test primera"""
    id: int
    evaluation_id: int
    test_example_id: int
    generated_answer: str
    bleu_score: Optional[float]
    rouge_1: Optional[float]
    rouge_2: Optional[float]
    rouge_l: Optional[float]
    bert_score_precision: Optional[float]
    bert_score_recall: Optional[float]
    bert_score_f1: Optional[float]
    exact_match: bool
    word_overlap: Optional[float]
    created_at: str
    
    class Config:
        from_attributes = True


@router.post("/", response_model=EvaluationResponse)
async def create_evaluation(
    data: EvaluationCreate,
    db: Session = Depends(get_db)
):
    """
    Kreira novu evaluaciju
    """
    try:
        service = EvaluationService(db)
        evaluation = await service.create_evaluation(
            name=data.name,
            description=data.description
        )
        
        return EvaluationResponse(
            id=evaluation.id,
            name=evaluation.name,
            description=evaluation.description,
            status=evaluation.status,
            created_at=evaluation.created_at.isoformat(),
            started_at=None,
            completed_at=None,
            total_examples=None,
            completed_examples=None,
            avg_bleu_score=None,
            avg_rouge_1=None,
            avg_rouge_2=None,
            avg_rouge_l=None,
            avg_bert_score=None,
            exact_match_percentage=None
        )
    except Exception as e:
        logger.error(f"Error creating evaluation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _run_evaluation_background(
    evaluation_id: int,
    test_example_ids: Optional[List[int]],
    collection_id: Optional[int]
):
    """Helper function to run evaluation in background with new DB session"""
    from backend.database import SessionLocal
    db = SessionLocal()
    try:
        service = EvaluationService(db)
        await service.run_evaluation(
            evaluation_id=evaluation_id,
            test_example_ids=test_example_ids,
            collection_id=collection_id
        )
    except Exception as e:
        logger.error(f"Background evaluation error: {e}")
    finally:
        db.close()


@router.post("/{evaluation_id}/run", response_model=EvaluationResponse)
async def run_evaluation(
    evaluation_id: int,
    data: EvaluationRun,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Pokreće evaluaciju (u pozadini)
    """
    try:
        service = EvaluationService(db)
        
        # Proveri da li evaluacija postoji
        evaluation = service.get_evaluation(evaluation_id)
        if not evaluation:
            raise HTTPException(status_code=404, detail="Evaluation not found")
        
        # Pokreni evaluaciju u pozadini sa NOVOM DB session
        background_tasks.add_task(
            _run_evaluation_background,
            evaluation_id=evaluation_id,
            test_example_ids=data.test_example_ids,
            collection_id=data.collection_id
        )
        
        # Vrati trenutni status
        return EvaluationResponse(
            id=evaluation.id,
            name=evaluation.name,
            description=evaluation.description,
            status="running",
            created_at=evaluation.created_at.isoformat(),
            started_at=None,
            completed_at=None,
            total_examples=None,
            completed_examples=None,
            avg_bleu_score=None,
            avg_rouge_1=None,
            avg_rouge_2=None,
            avg_rouge_l=None,
            avg_bert_score=None,
            exact_match_percentage=None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running evaluation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[EvaluationResponse])
async def list_evaluations(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Lista svih evaluacija
    """
    try:
        service = EvaluationService(db)
        evaluations = service.list_evaluations(skip=skip, limit=limit, status=status)
        
        return [
            EvaluationResponse(
                id=e.id,
                name=e.name,
                description=e.description,
                status=e.status,
                created_at=e.created_at.isoformat(),
                started_at=e.started_at.isoformat() if e.started_at else None,
                completed_at=e.completed_at.isoformat() if e.completed_at else None,
                total_examples=e.total_examples,
                completed_examples=e.completed_examples,
                avg_bleu_score=e.avg_bleu_score,
                avg_rouge_1=e.avg_rouge_1,
                avg_rouge_2=e.avg_rouge_2,
                avg_rouge_l=e.avg_rouge_l,
                avg_bert_score=e.avg_bert_score,
                exact_match_percentage=e.exact_match_percentage
            )
            for e in evaluations
        ]
    except Exception as e:
        logger.error(f"Error listing evaluations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{evaluation_id}", response_model=EvaluationResponse)
async def get_evaluation(
    evaluation_id: int,
    db: Session = Depends(get_db)
):
    """
    Dohvata evaluaciju po ID-ju
    """
    try:
        service = EvaluationService(db)
        evaluation = service.get_evaluation(evaluation_id)
        
        if not evaluation:
            raise HTTPException(status_code=404, detail="Evaluation not found")
        
        return EvaluationResponse(
            id=evaluation.id,
            name=evaluation.name,
            description=evaluation.description,
            status=evaluation.status,
            created_at=evaluation.created_at.isoformat(),
            started_at=evaluation.started_at.isoformat() if evaluation.started_at else None,
            completed_at=evaluation.completed_at.isoformat() if evaluation.completed_at else None,
            total_examples=evaluation.total_examples,
            completed_examples=evaluation.completed_examples,
            avg_bleu_score=evaluation.avg_bleu_score,
            avg_rouge_1=evaluation.avg_rouge_1,
            avg_rouge_2=evaluation.avg_rouge_2,
            avg_rouge_l=evaluation.avg_rouge_l,
            avg_bert_score=evaluation.avg_bert_score,
            exact_match_percentage=evaluation.exact_match_percentage
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting evaluation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{evaluation_id}/results", response_model=List[TestExampleResultResponse])
async def get_evaluation_results(
    evaluation_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Dohvata rezultate evaluacije
    """
    try:
        service = EvaluationService(db)
        results = service.get_evaluation_results(evaluation_id, skip=skip, limit=limit)
        
        return [
            TestExampleResultResponse(
                id=r.id,
                evaluation_id=r.evaluation_id,
                test_example_id=r.test_example_id,
                generated_answer=r.generated_answer,
                bleu_score=r.bleu_score,
                rouge_1=r.rouge_1,
                rouge_2=r.rouge_2,
                rouge_l=r.rouge_l,
                bert_score_precision=r.bert_score_precision,
                bert_score_recall=r.bert_score_recall,
                bert_score_f1=r.bert_score_f1,
                exact_match=r.exact_match,
                word_overlap=r.word_overlap,
                created_at=r.created_at.isoformat()
            )
            for r in results
        ]
    except Exception as e:
        logger.error(f"Error getting evaluation results: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{evaluation_id}/statistics")
async def get_evaluation_statistics(
    evaluation_id: int,
    db: Session = Depends(get_db)
):
    """
    Dohvata detaljne statistike evaluacije
    """
    try:
        service = EvaluationService(db)
        stats = service.get_statistics(evaluation_id)
        return stats
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting evaluation statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{evaluation_id}/stop")
async def stop_evaluation(
    evaluation_id: int,
    db: Session = Depends(get_db)
):
    """
    Zaustavlja evaluaciju koja je u toku
    """
    try:
        from backend.services.evaluation_service import cancel_evaluation
        
        service = EvaluationService(db)
        evaluation = service.get_evaluation(evaluation_id)
        
        if not evaluation:
            raise HTTPException(status_code=404, detail="Evaluation not found")
        
        if evaluation.status != "running":
            raise HTTPException(status_code=400, detail="Evaluation is not running")
        
        # Mark evaluation for cancellation
        cancel_evaluation(evaluation_id)
        logger.info(f"Stop requested for evaluation {evaluation_id}")
        
        return {"message": "Evaluation stop requested"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping evaluation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{evaluation_id}")
async def delete_evaluation(
    evaluation_id: int,
    db: Session = Depends(get_db)
):
    """
    Briše evaluaciju i sve njene rezultate
    """
    try:
        service = EvaluationService(db)
        success = service.delete_evaluation(evaluation_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Evaluation not found")
        
        return {"message": "Evaluation deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting evaluation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# New FAZA 9 endpoints

class EvaluationWithConfigCreate(BaseModel):
    """Schema za kreiranje evaluacije sa config-om"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    collection_id: int
    test_example_ids: List[int]
    config: dict  # RAG pipeline configuration


class EvaluationRunWithConfig(BaseModel):
    """Schema za pokretanje evaluacije sa config-om"""
    config: Optional[dict] = None  # Opciono, ako nije u snapshot-u


@router.post("/with-config", response_model=EvaluationResponse)
async def create_evaluation_with_config(
    data: EvaluationWithConfigCreate,
    db: Session = Depends(get_db)
):
    """
    Kreira evaluaciju sa RAG config snapshot-om
    """
    try:
        service = EvaluationService(db)
        evaluation = await service.create_with_config(
            name=data.name,
            collection_id=data.collection_id,
            test_example_ids=data.test_example_ids,
            config=data.config,
            description=data.description
        )
        
        return EvaluationResponse(
            id=evaluation.id,
            name=evaluation.name,
            description=evaluation.description,
            status=evaluation.status,
            created_at=evaluation.created_at.isoformat(),
            started_at=None,
            completed_at=None,
            total_examples=None,
            completed_examples=None,
            avg_bleu_score=None,
            avg_rouge_1=None,
            avg_rouge_2=None,
            avg_rouge_l=None,
            avg_bert_score=None,
            exact_match_percentage=None
        )
    except Exception as e:
        logger.error(f"Error creating evaluation with config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{evaluation_id}/run-with-config", response_model=EvaluationResponse)
async def run_evaluation_with_config(
    evaluation_id: int,
    data: EvaluationRunWithConfig,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Pokreće evaluaciju sa timing tracking-om (u pozadini)
    """
    try:
        service = EvaluationService(db)
        
        # Proveri da li evaluacija postoji
        evaluation = service.get_evaluation(evaluation_id)
        if not evaluation:
            raise HTTPException(status_code=404, detail="Evaluation not found")
        
        # Pokreni evaluaciju u pozadini
        background_tasks.add_task(
            service.run_with_config,
            evaluation_id=evaluation_id,
            config=data.config
        )
        
        # Vrati trenutni status
        return EvaluationResponse(
            id=evaluation.id,
            name=evaluation.name,
            description=evaluation.description,
            status="running",
            created_at=evaluation.created_at.isoformat(),
            started_at=None,
            completed_at=None,
            total_examples=None,
            completed_examples=None,
            avg_bleu_score=None,
            avg_rouge_1=None,
            avg_rouge_2=None,
            avg_rouge_l=None,
            avg_bert_score=None,
            exact_match_percentage=None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running evaluation with config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compare/{evaluation_id_1}/{evaluation_id_2}")
async def compare_evaluations(
    evaluation_id_1: int,
    evaluation_id_2: int,
    db: Session = Depends(get_db)
):
    """
    Poredi dve evaluacije (config, metrike, performance)
    """
    try:
        service = EvaluationService(db)
        comparison = service.compare_evaluations(evaluation_id_1, evaluation_id_2)
        return comparison
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error comparing evaluations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Made with Bob