"""
Test Database Models
Testira sve SQLAlchemy modele
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from backend.database import Base
from backend.models import (
    Collection, PDF, TestExample, ChatMessage, 
    Feedback, Evaluation, SettingsModel, SessionLog
)


@pytest.fixture
def db_session():
    """Kreira test database session"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_collection_model(db_session):
    """Test Collection model"""
    collection = Collection(
        name="test_collection",
        description="Test collection",
        is_active=True,
        vectors_count=100,
        pdfs_count=5
    )
    db_session.add(collection)
    db_session.commit()
    
    assert collection.id is not None
    assert collection.name == "test_collection"
    assert collection.is_active is True
    assert collection.vectors_count == 100
    

def test_pdf_model(db_session):
    """Test PDF model"""
    # Prvo kreiraj collection
    collection = Collection(name="test_collection", is_active=True)
    db_session.add(collection)
    db_session.commit()
    
    # Kreiraj PDF
    pdf = PDF(
        filename="test.pdf",
        filepath="/path/to/test.pdf",
        size_bytes=1024,
        pages=10,
        chunks_count=50,
        collection_id=collection.id,
        category="zakoni",
        language="sr",
        status="completed"
    )
    db_session.add(pdf)
    db_session.commit()
    
    assert pdf.id is not None
    assert pdf.filename == "test.pdf"
    assert pdf.status == "completed"
    assert pdf.collection_id == collection.id


def test_test_example_model(db_session):
    """Test TestExample model"""
    collection = Collection(name="test_collection", is_active=True)
    db_session.add(collection)
    db_session.commit()
    
    example = TestExample(
        question="Test pitanje?",
        expected_answer="Test odgovor",
        category="porezi",
        difficulty="easy",
        collection_id=collection.id
    )
    db_session.add(example)
    db_session.commit()
    
    assert example.id is not None
    assert example.question == "Test pitanje?"
    assert example.difficulty == "easy"


def test_chat_message_model(db_session):
    """Test ChatMessage model"""
    collection = Collection(name="test_collection", is_active=True)
    db_session.add(collection)
    db_session.commit()
    
    message = ChatMessage(
        session_id="session_123",
        role="user",
        content="Test poruka",
        collection_id=collection.id,
        model_name="qwen2.5:14b",
        retrieved_chunks=5,
        response_time_ms=1500
    )
    db_session.add(message)
    db_session.commit()
    
    assert message.id is not None
    assert message.role == "user"
    assert message.session_id == "session_123"


def test_feedback_model(db_session):
    """Test Feedback model"""
    collection = Collection(name="test_collection", is_active=True)
    db_session.add(collection)
    db_session.commit()
    
    message = ChatMessage(
        session_id="session_123",
        role="assistant",
        content="Test odgovor",
        collection_id=collection.id
    )
    db_session.add(message)
    db_session.commit()
    
    feedback = Feedback(
        message_id=message.id,
        accuracy_rating=5,
        language_rating=4,
        chunk_relevance_rating=5,
        comment="Odličan odgovor"
    )
    db_session.add(feedback)
    db_session.commit()
    
    assert feedback.id is not None
    assert feedback.accuracy_rating == 5
    assert feedback.message_id == message.id


def test_evaluation_model(db_session):
    """Test Evaluation model"""
    collection = Collection(name="test_collection", is_active=True)
    db_session.add(collection)
    db_session.commit()
    
    evaluation = Evaluation(
        version_name="phase1_baseline",
        collection_id=collection.id,
        duration_seconds=120,
        total_questions=50,
        correct_answers=42,
        accuracy=0.84,
        precision=0.86,
        recall=0.82,
        f1_score=0.84,
        avg_response_time_ms=1500,
        gpu_utilization_avg=0.75,
        config_snapshot='{"llm_temperature": 0.1}'
    )
    db_session.add(evaluation)
    db_session.commit()
    
    assert evaluation.id is not None
    assert evaluation.accuracy == 0.84
    assert evaluation.version_name == "phase1_baseline"


def test_settings_model(db_session):
    """Test SettingsModel"""
    setting = SettingsModel(
        key="llm_temperature",
        value="0.1",
        category="llm",
        description="LLM temperature setting"
    )
    db_session.add(setting)
    db_session.commit()
    
    assert setting.id is not None
    assert setting.key == "llm_temperature"
    assert setting.category == "llm"


def test_session_log_model(db_session):
    """Test SessionLog model"""
    collection = Collection(name="test_collection", is_active=True)
    db_session.add(collection)
    db_session.commit()
    
    log = SessionLog(
        session_id="session_123",
        event_type="query",
        event_data='{"query": "test"}',
        collection_id=collection.id
    )
    db_session.add(log)
    db_session.commit()
    
    assert log.id is not None
    assert log.event_type == "query"
    assert log.session_id == "session_123"


def test_relationships(db_session):
    """Test relationships između modela"""
    # Kreiraj collection
    collection = Collection(name="test_collection", is_active=True)
    db_session.add(collection)
    db_session.commit()
    
    # Kreiraj PDF
    pdf = PDF(
        filename="test.pdf",
        filepath="/path/to/test.pdf",
        size_bytes=1024,
        pages=10,
        collection_id=collection.id,
        status="completed"
    )
    db_session.add(pdf)
    
    # Kreiraj test example
    example = TestExample(
        question="Test?",
        expected_answer="Answer",
        collection_id=collection.id
    )
    db_session.add(example)
    
    # Kreiraj chat message
    message = ChatMessage(
        session_id="session_123",
        role="user",
        content="Test",
        collection_id=collection.id
    )
    db_session.add(message)
    db_session.commit()
    
    # Proveri relationships
    assert len(collection.pdfs) == 1
    assert len(collection.test_examples) == 1
    assert len(collection.chat_messages) == 1
    assert pdf.collection == collection
    assert example.collection == collection
    assert message.collection == collection


def test_cascade_delete(db_session):
    """Test cascade delete"""
    collection = Collection(name="test_collection", is_active=True)
    db_session.add(collection)
    db_session.commit()
    
    pdf = PDF(
        filename="test.pdf",
        filepath="/path/to/test.pdf",
        size_bytes=1024,
        pages=10,
        collection_id=collection.id,
        status="completed"
    )
    db_session.add(pdf)
    db_session.commit()
    
    collection_id = collection.id
    pdf_id = pdf.id
    
    # Obriši collection
    db_session.delete(collection)
    db_session.commit()
    
    # Proveri da je PDF takođe obrisan (cascade)
    deleted_pdf = db_session.query(PDF).filter(PDF.id == pdf_id).first()
    assert deleted_pdf is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# Made with Bob
