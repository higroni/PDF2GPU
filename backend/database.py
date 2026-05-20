"""
Database Setup
SQLAlchemy konfiguracija i session management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from typing import Generator
import logging

from backend.config import settings

logger = logging.getLogger(__name__)

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # Potrebno za SQLite
    echo=settings.DEBUG
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class za modele
class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    """
    Dependency za FastAPI endpoints
    Kreira novu database session za svaki request
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Inicijalizuje database - kreira sve tabele
    Poziva se pri pokretanju aplikacije
    """
    try:
        # Import svih modela da bi Base.metadata.create_all() radio
        from backend.models import pdf, chat_message, test_example, feedback, evaluation, collection, settings_model, session_log
        
        # Kreiraj sve tabele
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def drop_db():
    """
    Briše sve tabele - koristi se samo za development/testing
    """
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("Database dropped successfully")
    except Exception as e:
        logger.error(f"Failed to drop database: {e}")
        raise


def reset_db():
    """
    Reset database - briše i ponovo kreira sve tabele
    Koristi se samo za development/testing
    """
    drop_db()
    init_db()

# Made with Bob
