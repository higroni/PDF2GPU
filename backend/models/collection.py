"""
Collection Model
Metadata o Qdrant kolekcijama
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, UTC

from backend.database import Base


class Collection(Base):
    """Model za Qdrant kolekcije"""
    __tablename__ = "collections"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)
    is_active = Column(Boolean, default=False, nullable=False, index=True)
    vectors_count = Column(Integer, default=0, nullable=False)
    pdfs_count = Column(Integer, default=0, nullable=False)
    
    # Relationships
    pdfs = relationship("PDF", back_populates="collection", cascade="all, delete-orphan")
    test_examples = relationship("TestExample", back_populates="collection", cascade="all, delete-orphan")
    evaluations = relationship("Evaluation", back_populates="collection", cascade="all, delete-orphan")
    session_logs = relationship("SessionLog", back_populates="collection", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Collection(id={self.id}, name='{self.name}', active={self.is_active})>"

# Made with Bob
