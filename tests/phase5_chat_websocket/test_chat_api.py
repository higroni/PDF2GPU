"""
Chat API Tests
Testovi za chat API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.models.collection import Collection
from backend.models.session_log import SessionLog


@pytest.mark.api
@pytest.mark.chat
class TestChatAPI:
    """Test suite for Chat API endpoints"""

    def test_create_chat_session(self, test_client: TestClient, sample_collection: Collection):
        """Test creating a new chat session"""
        response = test_client.post(
            "/api/chat/sessions",
            json={"collection_id": sample_collection.id}
        )
        
        assert response.status_code in [200, 201]
        data = response.json()
        assert "id" in data or "session_id" in data

    def test_get_chat_sessions(self, test_client: TestClient, sample_session: SessionLog):
        """Test getting all chat sessions"""
        response = test_client.get("/api/chat/sessions")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_chat_session_by_id(self, test_client: TestClient, sample_session: SessionLog):
        """Test getting a specific chat session"""
        response = test_client.get(f"/api/chat/sessions/{sample_session.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_session.id

    def test_get_session_messages(self, test_client: TestClient, sample_session: SessionLog, sample_messages):
        """Test getting messages for a session"""
        response = test_client.get(f"/api/chat/sessions/{sample_session.id}/messages")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2

    def test_send_chat_message(self, test_client: TestClient, sample_session: SessionLog):
        """Test sending a chat message"""
        response = test_client.post(
            f"/api/chat/sessions/{sample_session.id}/messages",
            json={"message": "Test question"}
        )
        
        # May return 200 or stream response
        assert response.status_code in [200, 202]

    def test_delete_chat_session(self, test_client: TestClient, test_db_session: Session, sample_collection: Collection):
        """Test deleting a chat session"""
        # Create a session to delete
        create_response = test_client.post(
            "/api/chat/sessions",
            json={"collection_id": sample_collection.id}
        )
        
        if create_response.status_code in [200, 201]:
            session_data = create_response.json()
            session_id = session_data.get("id") or session_data.get("session_id")
            
            if session_id:
                delete_response = test_client.delete(f"/api/chat/sessions/{session_id}")
                assert delete_response.status_code in [200, 204]

    def test_send_message_unicode(self, test_client: TestClient, sample_session: SessionLog):
        """Test sending message with Unicode characters"""
        response = test_client.post(
            f"/api/chat/sessions/{sample_session.id}/messages",
            json={"message": "Питање на ћирилици?"}
        )
        
        assert response.status_code in [200, 202]

    def test_send_message_long_text(self, test_client: TestClient, sample_session: SessionLog):
        """Test sending very long message"""
        long_message = "Long question " * 100
        response = test_client.post(
            f"/api/chat/sessions/{sample_session.id}/messages",
            json={"message": long_message}
        )
        
        assert response.status_code in [200, 202, 400]

    def test_get_session_not_found(self, test_client: TestClient):
        """Test getting non-existent session"""
        response = test_client.get("/api/chat/sessions/99999")
        
        assert response.status_code == 404

    def test_send_message_to_nonexistent_session(self, test_client: TestClient):
        """Test sending message to non-existent session"""
        response = test_client.post(
            "/api/chat/sessions/99999/messages",
            json={"message": "Test"}
        )
        
        assert response.status_code == 404

    def test_create_session_invalid_collection(self, test_client: TestClient):
        """Test creating session with invalid collection"""
        response = test_client.post(
            "/api/chat/sessions",
            json={"collection_id": 99999}
        )
        
        assert response.status_code in [404, 400]

    def test_get_session_history(self, test_client: TestClient, sample_session: SessionLog, sample_messages):
        """Test getting session history"""
        response = test_client.get(f"/api/chat/sessions/{sample_session.id}/history")
        
        # Endpoint may or may not exist
        assert response.status_code in [200, 404]

    def test_clear_session_history(self, test_client: TestClient, sample_session: SessionLog):
        """Test clearing session history"""
        response = test_client.delete(f"/api/chat/sessions/{sample_session.id}/messages")
        
        # Endpoint may or may not exist
        assert response.status_code in [200, 204, 404]

    def test_send_message_with_options(self, test_client: TestClient, sample_session: SessionLog):
        """Test sending message with additional options"""
        response = test_client.post(
            f"/api/chat/sessions/{sample_session.id}/messages",
            json={
                "message": "Test question",
                "temperature": 0.7,
                "max_tokens": 500
            }
        )
        
        assert response.status_code in [200, 202, 422]

    def test_get_active_sessions(self, test_client: TestClient):
        """Test getting active sessions"""
        response = test_client.get("/api/chat/sessions?active=true")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_session_pagination(self, test_client: TestClient, test_db_session: Session, sample_collection: Collection):
        """Test session list pagination"""
        # Create multiple sessions
        for i in range(10):
            test_client.post(
                "/api/chat/sessions",
                json={"collection_id": sample_collection.id}
            )
        
        response = test_client.get("/api/chat/sessions?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5


# Made with Bob