"""
TestExample Model
Test pitanja i očekivani odgovori za evaluaciju
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, UTC

from backend.database import Base


class TestExample(Base):
    """Model za test primere"""
    __tablename__ = "test_examples"
    
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, nullable=False)
    expected_answer = Column(String, nullable=False)
    category = Column(String, nullable=True, index=True)
    difficulty = Column(String, default="medium", nullable=False)  # easy, medium, hard
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)
    collection_id = Column(Integer, ForeignKey("collections.id"), nullable=False, index=True)
    
    # Relationships
    collection = relationship("Collection", back_populates="test_examples")
    
    def __repr__(self):
        return f"<TestExample(id={self.id}, difficulty='{self.difficulty}')>"

# Made with Bob
