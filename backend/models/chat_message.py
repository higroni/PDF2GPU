"""
ChatMessage Model
Poruke u chat sesijama
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, UTC

from backend.database import Base


class ChatMessage(Base):
    """Model za chat poruke"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("session_logs.id"), nullable=False, index=True)
    role = Column(String, nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    message_metadata = Column(JSON, nullable=True)  # Sources, context info, etc.
    timestamp = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False, index=True)
    
    # Relationships
    session = relationship("SessionLog", back_populates="messages")
    feedback = relationship("Feedback", back_populates="message", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ChatMessage(id={self.id}, role='{self.role}', session_id={self.session_id})>"


# Made with Bob