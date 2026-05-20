"""
Evaluation Model
Rezultati evaluacija sistema
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from backend.database import Base


class Evaluation(Base):
    """Model za evaluacije test primera"""
    __tablename__ = "evaluations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="pending", index=True)  # pending, running, completed, failed
    
    # Configuration
    collection_id = Column(Integer, ForeignKey("collections.id"), nullable=True, index=True)
    config_snapshot = Column(Text, nullable=True)  # JSON snapshot of RAG config
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Statistike
    total_examples = Column(Integer, nullable=True)
    completed_examples = Column(Integer, nullable=True)
    
    # Prosečne metrike
    avg_bleu_score = Column(Float, nullable=True)
    avg_rouge_1 = Column(Float, nullable=True)
    avg_rouge_2 = Column(Float, nullable=True)
    avg_rouge_l = Column(Float, nullable=True)
    avg_bert_score = Column(Float, nullable=True)
    exact_match_percentage = Column(Float, nullable=True)
    
    # Performance metrics (average across all test examples)
    avg_query_processing_ms = Column(Float, nullable=True)
    avg_search_ms = Column(Float, nullable=True)
    avg_reranking_ms = Column(Float, nullable=True)
    avg_llm_generation_ms = Column(Float, nullable=True)
    avg_total_latency_ms = Column(Float, nullable=True)
    total_evaluation_time_seconds = Column(Float, nullable=True)
    
    # Relationships
    collection = relationship("Collection", back_populates="evaluations")
    results = relationship("TestExampleResult", back_populates="evaluation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Evaluation(id={self.id}, name='{self.name}', status='{self.status}')>"


# Made with Bob
