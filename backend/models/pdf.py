"""
PDF Model
Metadata o uploadovanim PDF fajlovima
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, UTC

from backend.database import Base


class PDF(Base):
    """Model za PDF fajlove"""
    __tablename__ = "pdfs"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    size_bytes = Column(Integer, nullable=False)
    pages = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    processed_at = Column(DateTime, nullable=True)
    chunks_count = Column(Integer, default=0, nullable=False)
    collection_id = Column(Integer, ForeignKey("collections.id"), nullable=False, index=True)
    category = Column(String, nullable=True)
    language = Column(String, default="sr", nullable=False)
    status = Column(String, default="pending", nullable=False, index=True)  # pending, processing, completed, failed
    error_message = Column(String, nullable=True)
    
    # Relationships
    collection = relationship("Collection", back_populates="pdfs")
    
    def __repr__(self):
        return f"<PDF(id={self.id}, filename='{self.filename}', status='{self.status}')>"

# Made with Bob
