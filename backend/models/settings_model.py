"""
Settings Model
Sistemske postavke
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime, UTC

from backend.database import Base


class SettingsModel(Base):
    """Model za postavke"""
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)  # JSON string
    category = Column(String, nullable=False, index=True)  # rag, llm, system
    description = Column(String, nullable=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)
    
    def __repr__(self):
        return f"<SettingsModel(id={self.id}, key='{self.key}', category='{self.category}')>"

# Made with Bob
