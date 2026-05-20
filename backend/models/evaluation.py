"""
Evaluation Model
Rezultati evaluacija sistema
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, UTC

from backend.database import Base


class Evaluation(Base):
    """Model za evaluacije"""
    __tablename__ = "evaluations"
    
    id = Column(Integer, primary_key=True, index=True)
    version_name = Column(String, nullable=False, index=True)
    collection_id = Column(Integer, ForeignKey("collections.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False, index=True)
    duration_seconds = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    correct_answers = Column(Integer, nullable=False)
    accuracy = Column(Float, nullable=False)
    precision = Column(Float, nullable=False)
    recall = Column(Float, nullable=False)
    f1_score = Column(Float, nullable=False)
    avg_response_time_ms = Column(Integer, nullable=False)
    gpu_utilization_avg = Column(Float, nullable=False)
    config_snapshot = Column(Text, nullable=False)  # JSON string
    
    # Relationships
    collection = relationship("Collection", back_populates="evaluations")
    
    def __repr__(self):
        return f"<Evaluation(id={self.id}, version='{self.version_name}', accuracy={self.accuracy:.2f})>"

# Made with Bob
