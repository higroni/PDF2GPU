"""
Feedback Model
Feedback korisnika na odgovore
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, UTC

from backend.database import Base


class Feedback(Base):
    """Model za feedback"""
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("chat_messages.id"), nullable=False, unique=True, index=True)
    accuracy_rating = Column(Integer, nullable=False)  # 1-5
    language_rating = Column(Integer, nullable=False)  # 1-5
    chunk_relevance_rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    
    # Relationships
    message = relationship("ChatMessage", back_populates="feedback")
    
    def __repr__(self):
        return f"<Feedback(id={self.id}, message_id={self.message_id}, accuracy={self.accuracy_rating})>"

# Made with Bob
