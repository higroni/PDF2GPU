"""
SessionLog Model
Logovi sesija za analizu
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, UTC

from backend.database import Base


class SessionLog(Base):
    """Model za chat sesije"""
    __tablename__ = "session_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    collection_id = Column(Integer, ForeignKey("collections.id"), nullable=True, index=True)
    started_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False, index=True)
    ended_at = Column(DateTime, nullable=True)
    
    # Relationships
    collection = relationship("Collection", back_populates="session_logs")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SessionLog(id={self.id}, collection_id={self.collection_id})>"

# Made with Bob
