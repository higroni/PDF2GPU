"""
Evaluation Service
Business logika za evaluaciju test primera
"""
import logging
import time
import json
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.models.evaluation import Evaluation
from backend.models.test_example import TestExample
from backend.models.test_example_result import TestExampleResult
from backend.services.chat_service import ChatService
from backend.utils.metrics import calculate_all_metrics, calculate_exact_match, calculate_word_overlap
from backend.rag.legal_metrics import (
    calculate_legal_term_accuracy,
    calculate_citation_accuracy,
    calculate_completeness_score
)

logger = logging.getLogger(__name__)

# Import log broadcaster (will be set after router is loaded)
_log_broadcaster = None

# Track cancelled evaluations
_cancelled_evaluations: set = set()

def set_log_broadcaster(broadcaster):
    """Set the log broadcaster instance"""
    global _log_broadcaster
    _log_broadcaster = broadcaster

async def broadcast_log(evaluation_id: int, level: str, message: str):
    """Broadcast log message if broadcaster is available"""
    if _log_broadcaster:
        try:
            await _log_broadcaster.broadcast_log(evaluation_id, level, message)
        except Exception as e:
            logger.error(f"Failed to broadcast log: {e}")

def cancel_evaluation(evaluation_id: int):
    """Mark evaluation as cancelled"""
    global _cancelled_evaluations
    _cancelled_evaluations.add(evaluation_id)
    logger.info(f"Evaluation {evaluation_id} marked for cancellation")

def is_evaluation_cancelled(evaluation_id: int) -> bool:
    """Check if evaluation is cancelled"""
    return evaluation_id in _cancelled_evaluations

def clear_cancellation(evaluation_id: int):
    """Clear cancellation flag"""
    global _cancelled_evaluations
    _cancelled_evaluations.discard(evaluation_id)


class EvaluationService:
    """Service za evaluaciju test primera"""
    
    def __init__(self, db: Session):
        self.db = db
        self.chat_service = ChatService(db)
    
    async def create_evaluation(
        self,
        name: str,
        description: Optional[str] = None,
        test_example_ids: Optional[List[int]] = None,
        collection_id: Optional[int] = None,
        config_snapshot: Optional[Dict[str, Any]] = None
    ) -> Evaluation:
        """
        Kreira novu evaluaciju
        
        Args:
            name: Naziv evaluacije
            description: Opis evaluacije
            test_example_ids: Lista ID-jeva test primera (None = svi aktivni)
            collection_id: ID kolekcije za evaluaciju
            config_snapshot: JSON snapshot RAG konfiguracije
            
        Returns:
            Kreirana evaluacija
        """
        evaluation = Evaluation(
            name=name,
            description=description,
            status="pending",
            collection_id=collection_id,
            config_snapshot=json.dumps(config_snapshot) if config_snapshot else None,
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
        
        # Broadcast start log
        await broadcast_log(evaluation_id, "INFO", f"Pokrenuta evaluacija '{evaluation.name}'")
        
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
            await broadcast_log(evaluation_id, "INFO", f"Pronađeno {len(test_examples)} test primera za evaluaciju")
            
            # Pokreni evaluaciju za svaki test primer
            results = []
            for i, test_example in enumerate(test_examples, 1):
                # Check if evaluation was cancelled
                if is_evaluation_cancelled(evaluation_id):
                    await broadcast_log(evaluation_id, "WARNING", f"Evaluacija zaustavljena od strane korisnika nakon {i-1}/{len(test_examples)} primera")
                    evaluation.status = "cancelled"
                    evaluation.completed_at = datetime.utcnow()
                    self.db.commit()
                    clear_cancellation(evaluation_id)
                    logger.info(f"Evaluation {evaluation_id} cancelled by user")
                    return evaluation
                
                try:
                    await broadcast_log(evaluation_id, "INFO", f"Evaluacija primera {i}/{len(test_examples)}: {test_example.question}")
                    
                    result = await self._evaluate_single_example(
                        evaluation_id=evaluation_id,
                        test_example=test_example,
                        collection_id=collection_id
                    )
                    results.append(result)
                    
                    # Log generisanog odgovora (povećan limit na 500 karaktera)
                    answer_preview = result.generated_answer[:500] + "..." if len(result.generated_answer) > 500 else result.generated_answer
                    await broadcast_log(evaluation_id, "INFO", f"Generisani odgovor: {answer_preview}")
                    
                    # Ažuriraj completed_examples nakon svakog primera
                    evaluation.completed_examples = i
                    self.db.commit()
                    
                    bleu_str = f"{result.bleu_score:.3f}" if result.bleu_score is not None else "N/A"
                    await broadcast_log(evaluation_id, "INFO", f"Primer {i}/{len(test_examples)} završen - BLEU: {bleu_str}")
                except Exception as e:
                    logger.error(f"Error evaluating test example {test_example.id}: {e}")
                    await broadcast_log(evaluation_id, "ERROR", f"Greška pri evaluaciji primera {i}: {str(e)}")
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
        logger.info(f"Evaluating test example {test_example.id}: {test_example.question}")
        
        # Generiši odgovor koristeći ChatService sa performance metrikama
        result_data = await self.chat_service.generate_answer(
            query=test_example.question,
            collection_id=collection_id,
            session_id=f"eval_{evaluation_id}_{test_example.id}",
            return_metrics=True
        )
        
        # Ekstraktuj odgovor i metrike
        generated_answer = result_data["answer"]
        perf_metrics = result_data["metrics"]
        
        # Izračunaj metrike kvaliteta
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
        
        # Calculate legal-specific metrics
        try:
            legal_term_metrics = calculate_legal_term_accuracy(
                generated_answer,
                test_example.expected_answer
            )
            citation_acc = calculate_citation_accuracy(
                generated_answer,
                test_example.expected_answer
            )
            completeness = calculate_completeness_score(
                generated_answer,
                test_example.expected_answer
            )
        except Exception as e:
            logger.warning(f"Failed to calculate legal metrics: {e}")
            legal_term_metrics = {"precision": None, "recall": None, "f1": None}
            citation_acc = None
            completeness = None
        
        # Kreiraj rezultat sa performance metrikama
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
            legal_term_precision=legal_term_metrics.get("precision"),
            legal_term_recall=legal_term_metrics.get("recall"),
            legal_term_f1=legal_term_metrics.get("f1"),
            citation_accuracy=citation_acc,
            completeness_score=completeness,
            query_processing_ms=perf_metrics.get('query_processing_ms'),
            search_ms=perf_metrics.get('search_ms'),
            reranking_ms=perf_metrics.get('reranking_ms'),
            llm_generation_ms=perf_metrics.get('llm_generation_ms'),
            total_latency_ms=perf_metrics.get('total_latency_ms'),
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
    
    async def create_with_config(
        self,
        name: str,
        collection_id: int,
        test_example_ids: List[int],
        config: Dict[str, Any],
        description: Optional[str] = None
    ) -> Evaluation:
        """
        Kreira evaluaciju sa RAG config snapshot-om
        
        Args:
            name: Naziv evaluacije
            collection_id: ID kolekcije
            test_example_ids: Lista ID-jeva test primera
            config: RAG konfiguracija (pipeline parametri)
            description: Opis evaluacije
            
        Returns:
            Kreirana evaluacija
        """
        return await self.create_evaluation(
            name=name,
            description=description,
            test_example_ids=test_example_ids,
            collection_id=collection_id,
            config_snapshot=config
        )
    
    async def run_with_config(
        self,
        evaluation_id: int,
        config: Optional[Dict[str, Any]] = None
    ) -> Evaluation:
        """
        Pokreće evaluaciju sa timing tracking-om
        
        Args:
            evaluation_id: ID evaluacije
            config: RAG konfiguracija (opciono, ako nije u snapshot-u)
            
        Returns:
            Ažurirana evaluacija sa performance metrikama
        """
        evaluation = self.get_evaluation(evaluation_id)
        if not evaluation:
            raise ValueError(f"Evaluation {evaluation_id} not found")
        
        # Ako config nije prosleđen, pokušaj iz snapshot-a
        if not config and evaluation.config_snapshot:
            config = json.loads(evaluation.config_snapshot)
        
        # TODO: Primeni config na RAG engine pre pokretanja
        # Ovo zahteva refaktorisanje RAG engine-a da prihvata runtime config
        
        # Za sada, pokreni standardnu evaluaciju
        evaluation_start = time.time()
        result = await self.run_evaluation(
            evaluation_id=evaluation_id,
            collection_id=evaluation.collection_id
        )
        evaluation_end = time.time()
        
        # Izračunaj ukupno vreme
        result.total_evaluation_time_seconds = evaluation_end - evaluation_start
        
        # Izračunaj prosečne performance metrike iz rezultata
        results = self.get_evaluation_results(evaluation_id, limit=10000)
        if results:
            result.avg_query_processing_ms = self._calculate_avg_metric(results, 'query_processing_ms')
            result.avg_search_ms = self._calculate_avg_metric(results, 'search_ms')
            result.avg_reranking_ms = self._calculate_avg_metric(results, 'reranking_ms')
            result.avg_llm_generation_ms = self._calculate_avg_metric(results, 'llm_generation_ms')
            result.avg_total_latency_ms = self._calculate_avg_metric(results, 'total_latency_ms')
        
        self.db.commit()
        self.db.refresh(result)
        
        logger.info(f"Evaluation {evaluation_id} completed with timing: {result.total_evaluation_time_seconds:.2f}s")
        return result
    
    def compare_evaluations(
        self,
        evaluation_id_1: int,
        evaluation_id_2: int
    ) -> Dict[str, Any]:
        """
        Poredi dve evaluacije
        
        Args:
            evaluation_id_1: ID prve evaluacije
            evaluation_id_2: ID druge evaluacije
            
        Returns:
            Dict sa poređenjem config-a, metrika i performance-a
        """
        eval1 = self.get_evaluation(evaluation_id_1)
        eval2 = self.get_evaluation(evaluation_id_2)
        
        if not eval1 or not eval2:
            raise ValueError("One or both evaluations not found")
        
        # Parse config snapshots
        config1 = json.loads(eval1.config_snapshot) if eval1.config_snapshot else {}
        config2 = json.loads(eval2.config_snapshot) if eval2.config_snapshot else {}
        
        # Config diff
        config_diff = self._compare_configs(config1, config2)
        
        # Metrics comparison
        metrics_comparison = {
            "bleu_score": {
                "eval1": eval1.avg_bleu_score,
                "eval2": eval2.avg_bleu_score,
                "diff": (eval2.avg_bleu_score - eval1.avg_bleu_score) if eval1.avg_bleu_score and eval2.avg_bleu_score else None,
                "improvement_pct": ((eval2.avg_bleu_score - eval1.avg_bleu_score) / eval1.avg_bleu_score * 100) if eval1.avg_bleu_score and eval2.avg_bleu_score and eval1.avg_bleu_score > 0 else None
            },
            "rouge_l": {
                "eval1": eval1.avg_rouge_l,
                "eval2": eval2.avg_rouge_l,
                "diff": (eval2.avg_rouge_l - eval1.avg_rouge_l) if eval1.avg_rouge_l and eval2.avg_rouge_l else None,
                "improvement_pct": ((eval2.avg_rouge_l - eval1.avg_rouge_l) / eval1.avg_rouge_l * 100) if eval1.avg_rouge_l and eval2.avg_rouge_l and eval1.avg_rouge_l > 0 else None
            },
            "bert_score": {
                "eval1": eval1.avg_bert_score,
                "eval2": eval2.avg_bert_score,
                "diff": (eval2.avg_bert_score - eval1.avg_bert_score) if eval1.avg_bert_score and eval2.avg_bert_score else None,
                "improvement_pct": ((eval2.avg_bert_score - eval1.avg_bert_score) / eval1.avg_bert_score * 100) if eval1.avg_bert_score and eval2.avg_bert_score and eval1.avg_bert_score > 0 else None
            },
            "exact_match": {
                "eval1": eval1.exact_match_percentage,
                "eval2": eval2.exact_match_percentage,
                "diff": (eval2.exact_match_percentage - eval1.exact_match_percentage) if eval1.exact_match_percentage and eval2.exact_match_percentage else None
            }
        }
        
        # Performance comparison
        performance_comparison = {
            "query_processing_ms": {
                "eval1": eval1.avg_query_processing_ms,
                "eval2": eval2.avg_query_processing_ms,
                "diff": (eval2.avg_query_processing_ms - eval1.avg_query_processing_ms) if eval1.avg_query_processing_ms and eval2.avg_query_processing_ms else None
            },
            "search_ms": {
                "eval1": eval1.avg_search_ms,
                "eval2": eval2.avg_search_ms,
                "diff": (eval2.avg_search_ms - eval1.avg_search_ms) if eval1.avg_search_ms and eval2.avg_search_ms else None
            },
            "reranking_ms": {
                "eval1": eval1.avg_reranking_ms,
                "eval2": eval2.avg_reranking_ms,
                "diff": (eval2.avg_reranking_ms - eval1.avg_reranking_ms) if eval1.avg_reranking_ms and eval2.avg_reranking_ms else None
            },
            "llm_generation_ms": {
                "eval1": eval1.avg_llm_generation_ms,
                "eval2": eval2.avg_llm_generation_ms,
                "diff": (eval2.avg_llm_generation_ms - eval1.avg_llm_generation_ms) if eval1.avg_llm_generation_ms and eval2.avg_llm_generation_ms else None
            },
            "total_latency_ms": {
                "eval1": eval1.avg_total_latency_ms,
                "eval2": eval2.avg_total_latency_ms,
                "diff": (eval2.avg_total_latency_ms - eval1.avg_total_latency_ms) if eval1.avg_total_latency_ms and eval2.avg_total_latency_ms else None
            },
            "total_evaluation_time_seconds": {
                "eval1": eval1.total_evaluation_time_seconds,
                "eval2": eval2.total_evaluation_time_seconds,
                "diff": (eval2.total_evaluation_time_seconds - eval1.total_evaluation_time_seconds) if eval1.total_evaluation_time_seconds and eval2.total_evaluation_time_seconds else None
            }
        }
        
        return {
            "evaluation_1": {
                "id": eval1.id,
                "name": eval1.name,
                "status": eval1.status,
                "collection_id": eval1.collection_id
            },
            "evaluation_2": {
                "id": eval2.id,
                "name": eval2.name,
                "status": eval2.status,
                "collection_id": eval2.collection_id
            },
            "config_1": config1,
            "config_2": config2,
            "config_diff": config_diff,
            "metrics_comparison": metrics_comparison,
            "performance_comparison": performance_comparison
        }
    
    def _compare_configs(self, config1: Dict[str, Any], config2: Dict[str, Any]) -> Dict[str, Any]:
        """Poredi dva config objekta i vraća razlike"""
        diff = {
            "changed": {},
            "added_in_2": {},
            "removed_from_1": {}
        }
        
        # Proveri sve ključeve iz config1
        for key in config1:
            if key not in config2:
                diff["removed_from_1"][key] = config1[key]
            elif config1[key] != config2[key]:
                diff["changed"][key] = {
                    "from": config1[key],
                    "to": config2[key]
                }
        
        # Proveri nove ključeve u config2
        for key in config2:
            if key not in config1:
                diff["added_in_2"][key] = config2[key]
        
        return diff


# Made with Bob