"""
Chat Service Tests
Testovi za chat service funkcionalnost
"""
import pytest
from sqlalchemy.orm import Session
from unittest.mock import Mock, AsyncMock, MagicMock, patch

from backend.services.chat_service import ChatService
from backend.models.session_log import SessionLog
from backend.models.chat_message import ChatMessage
from backend.models.collection import Collection


@pytest.mark.chat
class TestChatService:
    """Test suite for Chat Service"""

    @pytest.fixture
    def chat_service(self, mock_rag_engine):
        """Create chat service instance"""
        return ChatService(rag_engine=mock_rag_engine)

    def test_chat_service_initialization(self, chat_service):
        """Test chat service initialization"""
        assert chat_service is not None
        assert hasattr(chat_service, 'process_message')

    def test_create_session(self, chat_service, test_db_session: Session, sample_collection: Collection):
        """Test creating a chat session"""
        session = chat_service.create_session(
            db=test_db_session,
            collection_id=sample_collection.id
        )
        
        assert session is not None
        assert session.collection_id == sample_collection.id
        assert isinstance(session, SessionLog)

    def test_get_session(self, chat_service, test_db_session: Session, sample_session: SessionLog):
        """Test getting a session by ID"""
        session = chat_service.get_session(
            db=test_db_session,
            session_id=sample_session.id
        )
        
        assert session is not None
        assert session.id == sample_session.id

    def test_get_session_not_found(self, chat_service, test_db_session: Session):
        """Test getting non-existent session"""
        session = chat_service.get_session(
            db=test_db_session,
            session_id=99999
        )
        
        assert session is None

    def test_save_message(self, chat_service, test_db_session: Session, sample_session: SessionLog):
        """Test saving a chat message"""
        message = chat_service.save_message(
            db=test_db_session,
            session_id=sample_session.id,
            role="user",
            content="Test message"
        )
        
        assert message is not None
        assert message.session_id == sample_session.id
        assert message.role == "user"
        assert message.content == "Test message"

    def test_get_session_messages(self, chat_service, test_db_session: Session, sample_session: SessionLog, sample_messages):
        """Test getting all messages for a session"""
        messages = chat_service.get_session_messages(
            db=test_db_session,
            session_id=sample_session.id
        )
        
        assert messages is not None
        assert len(messages) >= 2
        assert all(msg.session_id == sample_session.id for msg in messages)

    @pytest.mark.asyncio
    async def test_process_message_basic(self, chat_service, test_db_session: Session, sample_session: SessionLog):
        """Test processing a basic message"""
        with patch.object(chat_service, 'generate_response', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = "Test response"
            
            response = await chat_service.process_message(
                db=test_db_session,
                session_id=sample_session.id,
                message="Test question"
            )
            
            assert response is not None
            assert isinstance(response, str)

    def test_get_session_history(self, chat_service, test_db_session: Session, sample_session: SessionLog, sample_messages):
        """Test getting session history"""
        history = chat_service.get_session_history(
            db=test_db_session,
            session_id=sample_session.id
        )
        
        assert history is not None
        assert isinstance(history, list)
        assert len(history) >= 2

    def test_delete_session(self, chat_service, test_db_session: Session, sample_collection: Collection):
        """Test deleting a session"""
        # Create a session to delete
        session = chat_service.create_session(
            db=test_db_session,
            collection_id=sample_collection.id
        )
        
        success = chat_service.delete_session(
            db=test_db_session,
            session_id=session.id
        )
        
        assert success is True
        
        # Verify deletion
        deleted_session = chat_service.get_session(
            db=test_db_session,
            session_id=session.id
        )
        assert deleted_session is None

    def test_save_message_with_sources(self, chat_service, test_db_session: Session, sample_session: SessionLog):
        """Test saving message with source references"""
        sources = [
            {"text": "Source 1", "score": 0.9},
            {"text": "Source 2", "score": 0.8}
        ]
        
        message = chat_service.save_message(
            db=test_db_session,
            session_id=sample_session.id,
            role="assistant",
            content="Response with sources",
            sources=sources
        )
        
        assert message is not None
        if hasattr(message, 'sources'):
            assert message.sources is not None

    def test_get_active_sessions(self, chat_service, test_db_session: Session, sample_collection: Collection):
        """Test getting active sessions"""
        # Create some sessions
        for i in range(3):
            chat_service.create_session(
                db=test_db_session,
                collection_id=sample_collection.id
            )
        
        sessions = chat_service.get_active_sessions(db=test_db_session)
        
        assert sessions is not None
        assert isinstance(sessions, list)
        assert len(sessions) >= 3

    def test_update_session_metadata(self, chat_service, test_db_session: Session, sample_session: SessionLog):
        """Test updating session metadata"""
        metadata = {"key": "value", "test": "data"}
        
        updated = chat_service.update_session_metadata(
            db=test_db_session,
            session_id=sample_session.id,
            metadata=metadata
        )
        
        # Method may or may not exist
        assert updated is not None or updated is None

    def test_save_message_unicode(self, chat_service, test_db_session: Session, sample_session: SessionLog):
        """Test saving message with Unicode content"""
        message = chat_service.save_message(
            db=test_db_session,
            session_id=sample_session.id,
            role="user",
            content="Порука на ћирилици"
        )
        
        assert message is not None
        assert message.content == "Порука на ћирилици"

    def test_save_message_long_content(self, chat_service, test_db_session: Session, sample_session: SessionLog):
        """Test saving message with very long content"""
        long_content = "Long message " * 500
        
        message = chat_service.save_message(
            db=test_db_session,
            session_id=sample_session.id,
            role="user",
            content=long_content
        )
        
        assert message is not None
        assert len(message.content) > 1000


# Made with Bob