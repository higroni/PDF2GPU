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

# Create engine with WAL mode and proper connection handling
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={
        "check_same_thread": False,  # Potrebno za SQLite
        "timeout": 30,  # Timeout za database lock (30 sekundi)
    },
    pool_pre_ping=True,  # Proveri konekciju pre korišćenja
    pool_recycle=3600,  # Recycle konekcije nakon 1h
    echo=settings.DEBUG
)

# Enable WAL mode for better concurrency
from sqlalchemy import event

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Set SQLite pragmas for better concurrency and crash recovery"""
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
    cursor.execute("PRAGMA synchronous=NORMAL")  # Faster writes, still safe
    cursor.execute("PRAGMA busy_timeout=30000")  # 30 second timeout
    cursor.close()

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
        from backend.models import pdf, chat_message, test_example, test_example_result, feedback, evaluation, collection, settings_model, session_log
        
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
