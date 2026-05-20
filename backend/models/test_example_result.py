"""
TestExampleResult Model
Rezultati evaluacije pojedinačnih test primera
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, UTC

from backend.database import Base


class TestExampleResult(Base):
    """Model za rezultate evaluacije pojedinačnih test primera"""
    __tablename__ = "test_example_results"
    
    id = Column(Integer, primary_key=True, index=True)
    test_example_id = Column(Integer, ForeignKey("test_examples.id"), nullable=False, index=True)
    evaluation_id = Column(Integer, ForeignKey("evaluations.id"), nullable=True, index=True)  # Opciono, za bulk
    
    # Generated answer
    generated_answer = Column(Text, nullable=False)
    
    # Metrics
    bleu_score = Column(Float, nullable=True)
    rouge_1 = Column(Float, nullable=True)
    rouge_2 = Column(Float, nullable=True)
    rouge_l = Column(Float, nullable=True)
    bert_score_precision = Column(Float, nullable=True)
    bert_score_recall = Column(Float, nullable=True)
    bert_score_f1 = Column(Float, nullable=True)
    exact_match = Column(Integer, nullable=False, default=0)  # 0 ili 1 (boolean kao int)
    word_overlap = Column(Float, nullable=True)
    
    # Performance breakdown (per pipeline phase)
    query_processing_ms = Column(Float, nullable=True)
    search_ms = Column(Float, nullable=True)
    reranking_ms = Column(Float, nullable=True)
    llm_generation_ms = Column(Float, nullable=True)
    total_latency_ms = Column(Float, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)  # Legacy field, kept for compatibility
    
    # Context
    context_used = Column(Text, nullable=True)  # JSON string sa sources
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False, index=True)
    
    # Relationships
    test_example = relationship("TestExample", back_populates="results")
    evaluation = relationship("Evaluation", back_populates="results")
    
    def __repr__(self):
        return f"<TestExampleResult(id={self.id}, test_example_id={self.test_example_id}, bleu={self.bleu_score:.3f if self.bleu_score else 'N/A'})>"

# Made with Bob