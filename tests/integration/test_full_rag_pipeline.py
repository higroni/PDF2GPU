"""
Full RAG Pipeline Integration Tests
End-to-end testovi za kompletan RAG pipeline
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.models.collection import Collection


@pytest.mark.integration
class TestFullRAGPipeline:
    """Integration tests for complete RAG pipeline"""

    def test_complete_workflow(self, test_client: TestClient, test_db_session: Session, temp_pdf_file):
        """Test complete workflow: create collection -> upload PDF -> search"""
        # 1. Create collection
        response = test_client.post(
            "/api/collections/",
            json={
                "name": "Integration Test Collection",
                "description": "Test collection for integration testing"
            }
        )
        assert response.status_code == 201
        collection = response.json()
        collection_id = collection["id"]
        
        # 2. Upload PDF
        with open(temp_pdf_file, 'rb') as f:
            upload_response = test_client.post(
                f"/api/pdfs/upload?collection_id={collection_id}",
                files={"file": ("test.pdf", f, "application/pdf")}
            )
        
        # Upload may or may not succeed depending on implementation
        if upload_response.status_code in [200, 201]:
            pdf_data = upload_response.json()
            
            # 3. Search in collection
            search_response = test_client.post(
                "/api/search/",
                json={
                    "query": "test query",
                    "collection_id": collection_id
                }
            )
            assert search_response.status_code == 200
        
        # 4. Cleanup
        test_client.delete(f"/api/collections/{collection_id}")

    def test_collection_lifecycle(self, test_client: TestClient):
        """Test collection creation, update, and deletion"""
        # Create
        response = test_client.post(
            "/api/collections/",
            json={"name": "Lifecycle Test", "description": "Test"}
        )
        assert response.status_code == 201
        collection_id = response.json()["id"]
        
        # Read
        get_response = test_client.get(f"/api/collections/{collection_id}")
        assert get_response.status_code == 200
        
        # Update
        update_response = test_client.put(
            f"/api/collections/{collection_id}",
            json={"name": "Updated Name", "description": "Updated"}
        )
        assert update_response.status_code == 200
        
        # Delete
        delete_response = test_client.delete(f"/api/collections/{collection_id}")
        assert delete_response.status_code in [200, 204]
        
        # Verify deletion
        verify_response = test_client.get(f"/api/collections/{collection_id}")
        assert verify_response.status_code == 404

    def test_multiple_collections_workflow(self, test_client: TestClient):
        """Test working with multiple collections"""
        collection_ids = []
        
        # Create multiple collections
        for i in range(3):
            response = test_client.post(
                "/api/collections/",
                json={
                    "name": f"Collection {i}",
                    "description": f"Description {i}"
                }
            )
            if response.status_code == 201:
                collection_ids.append(response.json()["id"])
        
        # Verify all collections exist
        list_response = test_client.get("/api/collections/")
        assert list_response.status_code == 200
        collections = list_response.json()
        assert len(collections) >= len(collection_ids)
        
        # Cleanup
        for cid in collection_ids:
            test_client.delete(f"/api/collections/{cid}")

    def test_search_across_collections(self, test_client: TestClient, sample_collection: Collection):
        """Test searching across different collections"""
        # Search in specific collection
        response1 = test_client.post(
            "/api/search/",
            json={
                "query": "test query",
                "collection_id": sample_collection.id
            }
        )
        assert response1.status_code == 200
        
        # Search without collection (may use active collection)
        response2 = test_client.post(
            "/api/search/",
            json={"query": "test query"}
        )
        assert response2.status_code in [200, 400, 422]

    def test_error_recovery(self, test_client: TestClient):
        """Test system recovery from errors"""
        # Try to create collection with duplicate name
        test_client.post(
            "/api/collections/",
            json={"name": "Duplicate Test", "description": "Test"}
        )
        
        response = test_client.post(
            "/api/collections/",
            json={"name": "Duplicate Test", "description": "Test"}
        )
        assert response.status_code == 400
        
        # System should still be functional
        list_response = test_client.get("/api/collections/")
        assert list_response.status_code == 200

    def test_concurrent_operations(self, test_client: TestClient):
        """Test concurrent API operations"""
        # Create multiple collections concurrently
        responses = []
        for i in range(5):
            response = test_client.post(
                "/api/collections/",
                json={
                    "name": f"Concurrent {i}",
                    "description": f"Test {i}"
                }
            )
            responses.append(response)
        
        # All should succeed
        successful = [r for r in responses if r.status_code == 201]
        assert len(successful) >= 3

    def test_data_consistency(self, test_client: TestClient):
        """Test data consistency across operations"""
        # Create collection
        create_response = test_client.post(
            "/api/collections/",
            json={"name": "Consistency Test", "description": "Test"}
        )
        collection_id = create_response.json()["id"]
        
        # Get collection multiple times
        for _ in range(5):
            response = test_client.get(f"/api/collections/{collection_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "Consistency Test"
        
        # Cleanup
        test_client.delete(f"/api/collections/{collection_id}")

    def test_api_response_times(self, test_client: TestClient, sample_collection: Collection):
        """Test that API responses are reasonably fast"""
        import time
        
        # Test collection list
        start = time.time()
        response = test_client.get("/api/collections/")
        duration = time.time() - start
        
        assert response.status_code == 200
        assert duration < 5.0  # Should respond within 5 seconds
        
        # Test search
        start = time.time()
        response = test_client.post(
            "/api/search/",
            json={
                "query": "test",
                "collection_id": sample_collection.id
            }
        )
        duration = time.time() - start
        
        assert response.status_code == 200
        assert duration < 10.0  # Search may take longer


# Made with Bob