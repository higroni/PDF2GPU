"""
Pytest Configuration and Shared Fixtures
Zajedničke fixtures za sve testove
"""
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, MagicMock
import tempfile
import os

from backend.database import Base, get_db
from backend.main import app
from backend.models.collection import Collection
from backend.models.pdf import PDF
from backend.models.session_log import SessionLog
from backend.models.chat_message import ChatMessage
from backend.models.feedback import Feedback
from backend.models.evaluation import Evaluation
import shutil



# Test Database Setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def test_db_engine():
    """Create test database engine"""
    engine = create_engine(
        SQLALCHEMY_TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function", autouse=True)
def cleanup_qdrant_storage():
    """Clean up Qdrant storage before each test"""
    qdrant_path = "data/qdrant_storage"
    if os.path.exists(qdrant_path):
        try:
            shutil.rmtree(qdrant_path)
        except Exception:
            pass  # Ignore errors if directory is in use
    yield
    # Cleanup after test as well
    if os.path.exists(qdrant_path):
        try:
            shutil.rmtree(qdrant_path)
        except Exception:
            pass


@pytest.fixture(scope="function")
def test_db_session(test_db_engine) -> Generator[Session, None, None]:
    """Create test database session"""
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_db_engine
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def mock_rag_engine():
    """Mock RAG Engine for tests"""
    mock = MagicMock()
    
    # Mock embedding service
    mock.embedding_service = MagicMock()
    mock.embedding_service.embedding_dim = 1024
    mock.embedding_service.encode = MagicMock(return_value=[[0.1] * 1024])
    
    # Mock Qdrant service
    mock.qdrant_service = MagicMock()
    mock.qdrant_service.get_collection_info = MagicMock(return_value={
        "vectors_count": 100,
        "points_count": 100
    })
    mock.qdrant_service.collection_exists = MagicMock(return_value=True)
    mock.qdrant_service.create_collection = MagicMock(return_value=True)
    mock.qdrant_service.delete_collection = MagicMock(return_value=True)
    
    # Mock other methods
    mock.get_device_info = MagicMock(return_value={
        "embedding_service": {"device": "cpu"},
        "reranker": {"device": "cpu"}
    })
    mock.clear_cache = MagicMock(return_value=None)
    
    return mock


@pytest.fixture(scope="function")
def test_client(test_db_session, mock_rag_engine) -> Generator[TestClient, None, None]:
    """Create test client with test database and mocked dependencies"""
    from backend.dependencies import get_rag_engine, get_collection_service, get_pdf_service, get_search_service
    from backend.services.collection_service import CollectionService
    from backend.services.pdf_service import PDFService
    from backend.services.search_service import SearchService
    
    def override_get_db():
        try:
            yield test_db_session
        finally:
            pass
    
    def override_get_rag_engine():
        return mock_rag_engine
    
    def override_get_collection_service():
        return CollectionService(rag_engine=mock_rag_engine)
    
    def override_get_pdf_service():
        return PDFService(rag_engine=mock_rag_engine)
    
    def override_get_search_service():
        return SearchService(rag_engine=mock_rag_engine)
    
    # Override dependencies
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_rag_engine] = override_get_rag_engine
    app.dependency_overrides[get_collection_service] = override_get_collection_service
    app.dependency_overrides[get_pdf_service] = override_get_pdf_service
    app.dependency_overrides[get_search_service] = override_get_search_service
    
    # Disable startup/shutdown events during tests
    app.router.on_startup = []
    app.router.on_shutdown = []
    
    # Create client with raise_server_exceptions=False to see actual errors
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client
    
    # Clear overrides
    app.dependency_overrides.clear()


# Mock Fixtures

@pytest.fixture
def mock_qdrant_client():
    """Mock Qdrant client"""
    mock = MagicMock()
    mock.get_collection = MagicMock(return_value=MagicMock(vectors_count=100))
    mock.search = MagicMock(return_value=[])
    mock.upsert = MagicMock(return_value=None)
    mock.delete_collection = MagicMock(return_value=None)
    return mock


@pytest.fixture
def mock_embedding_model():
    """Mock embedding model"""
    mock = MagicMock()
    mock.encode = MagicMock(return_value=[[0.1] * 1024])
    return mock


@pytest.fixture
def mock_reranker():
    """Mock reranker model"""
    mock = MagicMock()
    mock.compute_score = MagicMock(return_value=[[0.9]])
    return mock


@pytest.fixture
def mock_ollama_response():
    """Mock Ollama API response"""
    return {
        "model": "qwen2.5:14b",
        "response": "Test response",
        "done": True
    }


@pytest.fixture
async def mock_ollama_stream():
    """Mock Ollama streaming response"""
    async def stream_generator():
        tokens = ["Test", " response", " from", " LLM"]
        for token in tokens:
            yield {"response": token, "done": False}
        yield {"response": "", "done": True}
    return stream_generator()


# Test Data Fixtures

@pytest.fixture
def sample_collection(test_db_session) -> Collection:
    """Create sample collection"""
    collection = Collection(
        name="Test Collection",
        description="Test collection for testing"
    )
    test_db_session.add(collection)
    test_db_session.commit()
    test_db_session.refresh(collection)
    return collection


@pytest.fixture
def sample_pdf(test_db_session, sample_collection) -> PDF:
    """Create sample PDF"""
    pdf = PDF(
        filename="test.pdf",
        filepath="/tmp/test.pdf",
        size_bytes=1024,
        collection_id=sample_collection.id,
        pages=10,
        status="completed"
    )
    test_db_session.add(pdf)
    test_db_session.commit()
    test_db_session.refresh(pdf)
    return pdf




@pytest.fixture
def sample_session(test_db_session, sample_collection) -> SessionLog:
    """Create sample chat session"""
    session = SessionLog(
        collection_id=sample_collection.id
    )
    test_db_session.add(session)
    test_db_session.commit()
    test_db_session.refresh(session)
    return session


@pytest.fixture
def sample_messages(test_db_session, sample_session) -> list[ChatMessage]:
    """Create sample chat messages"""
    messages = [
        ChatMessage(
            session_id=sample_session.id,
            role="user",
            content="Test question?"
        ),
        ChatMessage(
            session_id=sample_session.id,
            role="assistant",
            content="Test answer."
        )
    ]
    for msg in messages:
        test_db_session.add(msg)
    test_db_session.commit()
    for msg in messages:
        test_db_session.refresh(msg)
    return messages


# File Fixtures

@pytest.fixture
def temp_pdf_file():
    """Create temporary PDF file"""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        # Write minimal PDF content
        f.write(b"%PDF-1.4\n")
        f.write(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
        f.write(b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n")
        f.write(b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\nendobj\n")
        f.write(b"xref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n")
        f.write(b"0000000058 00000 n\n0000000115 00000 n\ntrailer\n")
        f.write(b"<< /Size 4 /Root 1 0 R >>\nstartxref\n190\n%%EOF\n")
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def temp_upload_dir():
    """Create temporary upload directory"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    import shutil
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


# Async Fixtures

@pytest.fixture
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Faker Fixture

@pytest.fixture
def faker_instance():
    """Create Faker instance"""
    from faker import Faker
    return Faker()


# WebSocket Fixtures

@pytest.fixture
def mock_websocket():
    """Mock WebSocket connection"""
    mock = AsyncMock()
    mock.accept = AsyncMock()
    mock.send_text = AsyncMock()
    mock.send_json = AsyncMock()
    mock.receive_text = AsyncMock(return_value='{"type": "ping"}')
    mock.receive_json = AsyncMock(return_value={"type": "ping"})
    mock.close = AsyncMock()
    return mock


# Cleanup Fixtures

@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Cleanup after each test"""
    yield
    # Add any cleanup logic here
    pass

# Made with Bob
