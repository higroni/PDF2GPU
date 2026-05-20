"""
Evaluation Service
Business logika za evaluaciju test primera
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.models.evaluation import Evaluation
from backend.models.test_example import TestExample
from backend.models.test_example_result import TestExampleResult
from backend.services.chat_service import ChatService
from backend.utils.metrics import calculate_all_metrics, calculate_exact_match, calculate_word_overlap

logger = logging.getLogger(__name__)


class EvaluationService:
    """Service za evaluaciju test primera"""
    
    def __init__(self, db: Session):
        self.db = db
        self.chat_service = ChatService(db)
    
    async def create_evaluation(
        self,
        name: str,
        description: Optional[str] = None,
        test_example_ids: Optional[List[int]] = None
    ) -> Evaluation:
        """
        Kreira novu evaluaciju
        
        Args:
            name: Naziv evaluacije
            description: Opis evaluacije
            test_example_ids: Lista ID-jeva test primera (None = svi aktivni)
            
        Returns:
            Kreirana evaluacija
        """
        evaluation = Evaluation(
            name=name,
            description=description,
            status="pending",
            created_at=datetime.utcnow()
        )
        
        self.db.add(evaluation)
        self.db.commit()
        self.db.refresh(evaluation)
        
        logger.info(f"Created evaluation: {evaluation.id} - {name}")
        return evaluation
    
    async def run_evaluation(
        self,
        evaluation_id: int,
        test_example_ids: Optional[List[int]] = None,
        collection_id: Optional[int] = None
    ) -> Evaluation:
        """
        Pokreće evaluaciju
        
        Args:
            evaluation_id: ID evaluacije
            test_example_ids: Lista ID-jeva test primera (None = svi aktivni)
            collection_id: ID kolekcije za RAG (opciono)
            
        Returns:
            Ažurirana evaluacija
        """
        evaluation = self.db.query(Evaluation).filter(
            Evaluation.id == evaluation_id
        ).first()
        
        if not evaluation:
            raise ValueError(f"Evaluation {evaluation_id} not found")
        
        # Ažuriraj status
        evaluation.status = "running"
        evaluation.started_at = datetime.utcnow()
        self.db.commit()
        
        try:
            # Dohvati test primere
            query = self.db.query(TestExample).filter(TestExample.is_active == True)
            
            if test_example_ids:
                query = query.filter(TestExample.id.in_(test_example_ids))
            
            test_examples = query.all()
            
            if not test_examples:
                raise ValueError("No active test examples found")
            
            # Postavi total_examples odmah na početku
            evaluation.total_examples = len(test_examples)
            evaluation.completed_examples = 0
            self.db.commit()
            
            logger.info(f"Running evaluation {evaluation_id} on {len(test_examples)} test examples")
            
            # Pokreni evaluaciju za svaki test primer
            results = []
            for i, test_example in enumerate(test_examples, 1):
                try:
                    result = await self._evaluate_single_example(
                        evaluation_id=evaluation_id,
                        test_example=test_example,
                        collection_id=collection_id
                    )
                    results.append(result)
                    
                    # Ažuriraj completed_examples nakon svakog primera
                    evaluation.completed_examples = i
                    self.db.commit()
                except Exception as e:
                    logger.error(f"Error evaluating test example {test_example.id}: {e}")
                    # Nastavi sa ostalim primerima
                    continue
            
            # Izračunaj agregatne metrike
            # total_examples je već postavljen na početku
            evaluation.completed_examples = len(results)
            
            if results:
                # Prosečne metrike
                evaluation.avg_bleu_score = self._calculate_avg_metric(results, 'bleu_score')
                evaluation.avg_rouge_1 = self._calculate_avg_metric(results, 'rouge_1')
                evaluation.avg_rouge_2 = self._calculate_avg_metric(results, 'rouge_2')
                evaluation.avg_rouge_l = self._calculate_avg_metric(results, 'rouge_l')
                evaluation.avg_bert_score = self._calculate_avg_metric(results, 'bert_score_f1')
                
                # Exact match procenat
                exact_matches = sum(1 for r in results if r.exact_match)
                evaluation.exact_match_percentage = (exact_matches / len(results)) * 100
            
            # Završi evaluaciju
            evaluation.status = "completed"
            evaluation.completed_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(evaluation)
            
            logger.info(f"Evaluation {evaluation_id} completed: {evaluation.completed_examples}/{evaluation.total_examples} examples")
            return evaluation
            
        except Exception as e:
            logger.error(f"Error running evaluation {evaluation_id}: {e}")
            evaluation.status = "failed"
            evaluation.completed_at = datetime.utcnow()
            self.db.commit()
            raise
    
    async def _evaluate_single_example(
        self,
        evaluation_id: int,
        test_example: TestExample,
        collection_id: Optional[int] = None
    ) -> TestExampleResult:
        """
        Evaluira jedan test primer
        
        Args:
            evaluation_id: ID evaluacije
            test_example: Test primer
            collection_id: ID kolekcije za RAG
            
        Returns:
            Rezultat evaluacije
        """
        logger.info(f"Evaluating test example {test_example.id}: {test_example.question[:50]}...")
        
        # Generiši odgovor koristeći ChatService
        # Koristimo collection_id ako je prosleđen, inače None
        generated_answer = await self.chat_service.generate_answer(
            query=test_example.question,
            collection_id=collection_id,
            session_id=f"eval_{evaluation_id}_{test_example.id}"
        )
        
        # Izračunaj metrike
        metrics = calculate_all_metrics(
            reference=test_example.expected_answer,
            hypothesis=generated_answer
        )
        
        # Dodatne metrike
        exact_match = calculate_exact_match(
            reference=test_example.expected_answer,
            hypothesis=generated_answer
        )
        
        word_overlap = calculate_word_overlap(
            reference=test_example.expected_answer,
            hypothesis=generated_answer
        )
        
        # Kreiraj rezultat
        result = TestExampleResult(
            evaluation_id=evaluation_id,
            test_example_id=test_example.id,
            generated_answer=generated_answer,
            bleu_score=metrics.get('bleu_score'),
            rouge_1=metrics.get('rouge_1'),
            rouge_2=metrics.get('rouge_2'),
            rouge_l=metrics.get('rouge_l'),
            bert_score_precision=metrics.get('bert_score_precision'),
            bert_score_recall=metrics.get('bert_score_recall'),
            bert_score_f1=metrics.get('bert_score_f1'),
            exact_match=1 if exact_match else 0,
            word_overlap=word_overlap,
            execution_time_ms=None,
            created_at=datetime.utcnow()
        )
        
        self.db.add(result)
        self.db.commit()
        self.db.refresh(result)
        
        logger.info(f"Test example {test_example.id} evaluated: BLEU={metrics.get('bleu_score'):.3f}, Exact Match={exact_match}")
        return result
    
    def _calculate_avg_metric(self, results: List[TestExampleResult], metric_name: str) -> Optional[float]:
        """Računa prosečnu vrednost metrike"""
        values = [getattr(r, metric_name) for r in results if getattr(r, metric_name) is not None]
        if not values:
            return None
        return sum(values) / len(values)
    
    def get_evaluation(self, evaluation_id: int) -> Optional[Evaluation]:
        """Dohvata evaluaciju po ID-ju"""
        return self.db.query(Evaluation).filter(
            Evaluation.id == evaluation_id
        ).first()
    
    def list_evaluations(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[Evaluation]:
        """
        Lista evaluacija
        
        Args:
            skip: Broj evaluacija za preskočiti
            limit: Maksimalan broj evaluacija
            status: Filter po statusu
            
        Returns:
            Lista evaluacija
        """
        query = self.db.query(Evaluation)
        
        if status:
            query = query.filter(Evaluation.status == status)
        
        return query.order_by(Evaluation.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_evaluation_results(
        self,
        evaluation_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[TestExampleResult]:
        """
        Dohvata rezultate evaluacije
        
        Args:
            evaluation_id: ID evaluacije
            skip: Broj rezultata za preskočiti
            limit: Maksimalan broj rezultata
            
        Returns:
            Lista rezultata
        """
        return self.db.query(TestExampleResult).filter(
            TestExampleResult.evaluation_id == evaluation_id
        ).offset(skip).limit(limit).all()
    
    def delete_evaluation(self, evaluation_id: int) -> bool:
        """
        Briše evaluaciju i sve njene rezultate
        
        Args:
            evaluation_id: ID evaluacije
            
        Returns:
            True ako je uspešno obrisano
        """
        evaluation = self.get_evaluation(evaluation_id)
        if not evaluation:
            return False
        
        # Briši rezultate
        self.db.query(TestExampleResult).filter(
            TestExampleResult.evaluation_id == evaluation_id
        ).delete()
        
        # Briši evaluaciju
        self.db.delete(evaluation)
        self.db.commit()
        
        logger.info(f"Deleted evaluation: {evaluation_id}")
        return True
    
    def get_statistics(self, evaluation_id: int) -> Dict[str, Any]:
        """
        Dohvata detaljne statistike evaluacije
        
        Args:
            evaluation_id: ID evaluacije
            
        Returns:
            Dict sa statistikama
        """
        evaluation = self.get_evaluation(evaluation_id)
        if not evaluation:
            raise ValueError(f"Evaluation {evaluation_id} not found")
        
        results = self.get_evaluation_results(evaluation_id, limit=10000)
        
        if not results:
            return {
                "evaluation_id": evaluation_id,
                "status": evaluation.status,
                "total_examples": 0,
                "metrics": {}
            }
        
        # Izračunaj statistike
        stats = {
            "evaluation_id": evaluation_id,
            "name": evaluation.name,
            "status": evaluation.status,
            "total_examples": len(results),
            "started_at": evaluation.started_at.isoformat() if evaluation.started_at else None,
            "completed_at": evaluation.completed_at.isoformat() if evaluation.completed_at else None,
            "metrics": {
                "bleu_score": self._metric_stats(results, 'bleu_score'),
                "rouge_1": self._metric_stats(results, 'rouge_1'),
                "rouge_2": self._metric_stats(results, 'rouge_2'),
                "rouge_l": self._metric_stats(results, 'rouge_l'),
                "bert_score_f1": self._metric_stats(results, 'bert_score_f1'),
                "exact_match": {
                    "count": sum(1 for r in results if r.exact_match == 1),
                    "percentage": (sum(1 for r in results if r.exact_match == 1) / len(results)) * 100
                },
                "word_overlap": self._metric_stats(results, 'word_overlap')
            }
        }
        
        return stats
    
    def _metric_stats(self, results: List[TestExampleResult], metric_name: str) -> Dict[str, float]:
        """Računa statistike za metriku"""
        values = [getattr(r, metric_name) for r in results if getattr(r, metric_name) is not None]
        
        if not values:
            return {"avg": 0.0, "min": 0.0, "max": 0.0, "count": 0}
        
        return {
            "avg": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
            "count": len(values)
        }


# Made with Bob