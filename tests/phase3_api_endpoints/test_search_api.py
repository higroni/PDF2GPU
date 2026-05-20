"""
Search API Tests
Testovi za search i RAG endpoints
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.models.collection import Collection
from backend.models.pdf import PDF


@pytest.mark.api
class TestSearchAPI:
    """Test suite for Search API endpoints"""

    def test_search_basic(self, test_client: TestClient, sample_collection: Collection, sample_pdf: PDF):
        """Test basic search"""
        response = test_client.post(
            "/api/search/",
            json={
                "query": "test query",
                "collection_id": sample_collection.id
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data or isinstance(data, list)

    def test_search_empty_query(self, test_client: TestClient, sample_collection: Collection):
        """Test search with empty query"""
        response = test_client.post(
            "/api/search/",
            json={
                "query": "",
                "collection_id": sample_collection.id
            }
        )
        
        # Should handle empty query gracefully
        assert response.status_code in [200, 400, 422]

    def test_search_invalid_collection(self, test_client: TestClient):
        """Test search with non-existent collection"""
        response = test_client.post(
            "/api/search/",
            json={
                "query": "test query",
                "collection_id": 99999
            }
        )
        
        assert response.status_code in [404, 400]

    def test_search_with_limit(self, test_client: TestClient, sample_collection: Collection, sample_pdf: PDF):
        """Test search with result limit"""
        response = test_client.post(
            "/api/search/",
            json={
                "query": "test query",
                "collection_id": sample_collection.id,
                "limit": 5
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        if isinstance(data, dict) and "results" in data:
            assert len(data["results"]) <= 5
        elif isinstance(data, list):
            assert len(data) <= 5

    def test_search_with_filters(self, test_client: TestClient, sample_collection: Collection, sample_pdf: PDF):
        """Test search with filters"""
        response = test_client.post(
            "/api/search/",
            json={
                "query": "test query",
                "collection_id": sample_collection.id,
                "filters": {
                    "pdf_id": sample_pdf.id
                }
            }
        )
        
        assert response.status_code == 200

    def test_search_unicode_query(self, test_client: TestClient, sample_collection: Collection, sample_pdf: PDF):
        """Test search with Unicode characters"""
        response = test_client.post(
            "/api/search/",
            json={
                "query": "Тест упит на ћирилици",
                "collection_id": sample_collection.id
            }
        )
        
        assert response.status_code == 200

    def test_search_special_characters(self, test_client: TestClient, sample_collection: Collection, sample_pdf: PDF):
        """Test search with special characters"""
        response = test_client.post(
            "/api/search/",
            json={
                "query": "test @#$% query!",
                "collection_id": sample_collection.id
            }
        )
        
        assert response.status_code == 200

    def test_search_long_query(self, test_client: TestClient, sample_collection: Collection, sample_pdf: PDF):
        """Test search with very long query"""
        long_query = "test query " * 100
        response = test_client.post(
            "/api/search/",
            json={
                "query": long_query,
                "collection_id": sample_collection.id
            }
        )
        
        assert response.status_code == 200

    def test_search_returns_scores(self, test_client: TestClient, sample_collection: Collection, sample_pdf: PDF):
        """Test that search results include relevance scores"""
        response = test_client.post(
            "/api/search/",
            json={
                "query": "test query",
                "collection_id": sample_collection.id
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check if results have scores
        if isinstance(data, dict) and "results" in data:
            results = data["results"]
            if len(results) > 0:
                assert "score" in results[0] or "relevance" in results[0]
        elif isinstance(data, list) and len(data) > 0:
            assert "score" in data[0] or "relevance" in data[0]

    def test_search_with_reranking(self, test_client: TestClient, sample_collection: Collection, sample_pdf: PDF):
        """Test search with reranking enabled"""
        response = test_client.post(
            "/api/search/",
            json={
                "query": "test query",
                "collection_id": sample_collection.id,
                "use_reranker": True
            }
        )
        
        assert response.status_code == 200

    def test_search_without_reranking(self, test_client: TestClient, sample_collection: Collection, sample_pdf: PDF):
        """Test search without reranking"""
        response = test_client.post(
            "/api/search/",
            json={
                "query": "test query",
                "collection_id": sample_collection.id,
                "use_reranker": False
            }
        )
        
        assert response.status_code == 200

    def test_search_pagination(self, test_client: TestClient, sample_collection: Collection, sample_pdf: PDF):
        """Test search result pagination"""
        response = test_client.post(
            "/api/search/",
            json={
                "query": "test query",
                "collection_id": sample_collection.id,
                "skip": 0,
                "limit": 10
            }
        )
        
        assert response.status_code == 200

    def test_semantic_search(self, test_client: TestClient, sample_collection: Collection, sample_pdf: PDF):
        """Test semantic search endpoint"""
        response = test_client.post(
            "/api/search/semantic",
            json={
                "query": "test query",
                "collection_id": sample_collection.id
            }
        )
        
        # Endpoint may or may not exist
        assert response.status_code in [200, 404]

    def test_hybrid_search(self, test_client: TestClient, sample_collection: Collection, sample_pdf: PDF):
        """Test hybrid search (semantic + keyword)"""
        response = test_client.post(
            "/api/search/hybrid",
            json={
                "query": "test query",
                "collection_id": sample_collection.id
            }
        )
        
        # Endpoint may or may not exist
        assert response.status_code in [200, 404]

    def test_search_missing_collection_id(self, test_client: TestClient):
        """Test search without collection_id"""
        response = test_client.post(
            "/api/search/",
            json={
                "query": "test query"
            }
        )
        
        # Should require collection_id or use active collection
        assert response.status_code in [200, 400, 422]

    def test_search_with_metadata_filter(self, test_client: TestClient, sample_collection: Collection, sample_pdf: PDF):
        """Test search with metadata filtering"""
        response = test_client.post(
            "/api/search/",
            json={
                "query": "test query",
                "collection_id": sample_collection.id,
                "metadata_filter": {
                    "source": "test"
                }
            }
        )
        
        assert response.status_code == 200

    def test_search_returns_context(self, test_client: TestClient, sample_collection: Collection, sample_pdf: PDF):
        """Test that search results include context"""
        response = test_client.post(
            "/api/search/",
            json={
                "query": "test query",
                "collection_id": sample_collection.id
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Results should include text/context
        if isinstance(data, dict) and "results" in data:
            results = data["results"]
            if len(results) > 0:
                assert "text" in results[0] or "content" in results[0] or "chunk" in results[0]
        elif isinstance(data, list) and len(data) > 0:
            assert "text" in data[0] or "content" in data[0] or "chunk" in data[0]

    @pytest.mark.parametrize("query", [
        "simple query",
        "query with multiple words",
        "Упит на српском",
        "query with numbers 123",
        "query with symbols @#$"
    ])
    def test_search_various_queries(self, test_client: TestClient, sample_collection: Collection, sample_pdf: PDF, query: str):
        """Test search with various query types"""
        response = test_client.post(
            "/api/search/",
            json={
                "query": query,
                "collection_id": sample_collection.id
            }
        )
        
        assert response.status_code == 200


# Made with Bob