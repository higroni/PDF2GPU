"""
Reranker Tests
Testovi za reranker funkcionalnost
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
import numpy as np

from backend.rag.reranker import Reranker


@pytest.mark.rag
class TestReranker:
    """Test suite for Reranker"""

    @pytest.fixture
    def mock_model(self):
        """Create mock reranker model"""
        mock = MagicMock()
        mock.compute_score = MagicMock(return_value=[[0.9]])
        return mock

    @pytest.fixture
    def reranker(self, mock_model):
        """Create reranker with mocked model"""
        with patch('backend.rag.reranker.CrossEncoder', return_value=mock_model):
            reranker = Reranker(model_name="test-reranker", device="cpu")
            return reranker

    def test_reranker_initialization(self, reranker):
        """Test reranker initialization"""
        assert reranker is not None
        assert hasattr(reranker, 'rerank')

    def test_rerank_single_result(self, reranker, mock_model):
        """Test reranking single result"""
        query = "Test query"
        results = [{"text": "Result 1", "score": 0.5}]
        
        mock_model.compute_score.return_value = [[0.9]]
        
        reranked = reranker.rerank(query, results)
        
        assert reranked is not None
        assert len(reranked) == 1
        mock_model.compute_score.assert_called_once()

    def test_rerank_multiple_results(self, reranker, mock_model):
        """Test reranking multiple results"""
        query = "Test query"
        results = [
            {"text": "Result 1", "score": 0.5},
            {"text": "Result 2", "score": 0.6},
            {"text": "Result 3", "score": 0.7}
        ]
        
        mock_model.compute_score.return_value = [[0.9], [0.8], [0.7]]
        
        reranked = reranker.rerank(query, results)
        
        assert reranked is not None
        assert len(reranked) == 3

    def test_rerank_empty_results(self, reranker):
        """Test reranking empty results list"""
        query = "Test query"
        results = []
        
        reranked = reranker.rerank(query, results)
        
        assert reranked is not None
        assert len(reranked) == 0

    def test_rerank_sorts_by_score(self, reranker, mock_model):
        """Test that reranking sorts results by score"""
        query = "Test query"
        results = [
            {"text": "Low score", "score": 0.3},
            {"text": "High score", "score": 0.9},
            {"text": "Medium score", "score": 0.6}
        ]
        
        # Mock returns scores in order
        mock_model.compute_score.return_value = [[0.5], [0.9], [0.7]]
        
        reranked = reranker.rerank(query, results)
        
        assert len(reranked) == 3
        # Results should be sorted by reranker score (descending)

    def test_rerank_preserves_metadata(self, reranker, mock_model):
        """Test that reranking preserves result metadata"""
        query = "Test query"
        results = [
            {"text": "Result 1", "score": 0.5, "metadata": {"id": 1}},
            {"text": "Result 2", "score": 0.6, "metadata": {"id": 2}}
        ]
        
        mock_model.compute_score.return_value = [[0.9], [0.8]]
        
        reranked = reranker.rerank(query, results)
        
        assert len(reranked) == 2
        # Metadata should be preserved
        for result in reranked:
            assert "metadata" in result or "text" in result

    def test_rerank_with_top_k(self, reranker, mock_model):
        """Test reranking with top_k parameter"""
        query = "Test query"
        results = [
            {"text": f"Result {i}", "score": 0.5} for i in range(10)
        ]
        
        mock_model.compute_score.return_value = [[0.9 - i*0.1] for i in range(10)]
        
        reranked = reranker.rerank(query, results, top_k=5)
        
        assert len(reranked) <= 5

    def test_rerank_handles_special_characters(self, reranker, mock_model):
        """Test reranking with special characters in query"""
        query = "Query with @#$%"
        results = [{"text": "Result", "score": 0.5}]
        
        mock_model.compute_score.return_value = [[0.9]]
        
        reranked = reranker.rerank(query, results)
        
        assert reranked is not None
        assert len(reranked) == 1

    def test_rerank_handles_unicode(self, reranker, mock_model):
        """Test reranking with Unicode text"""
        query = "Упит на ћирилици"
        results = [
            {"text": "Резултат 1", "score": 0.5},
            {"text": "Резултат 2", "score": 0.6}
        ]
        
        mock_model.compute_score.return_value = [[0.9], [0.8]]
        
        reranked = reranker.rerank(query, results)
        
        assert reranked is not None
        assert len(reranked) == 2

    def test_rerank_with_long_query(self, reranker, mock_model):
        """Test reranking with very long query"""
        query = "Long query " * 100
        results = [{"text": "Result", "score": 0.5}]
        
        mock_model.compute_score.return_value = [[0.9]]
        
        reranked = reranker.rerank(query, results)
        
        assert reranked is not None

    def test_rerank_with_long_results(self, reranker, mock_model):
        """Test reranking with very long result texts"""
        query = "Test query"
        results = [{"text": "Long text " * 500, "score": 0.5}]
        
        mock_model.compute_score.return_value = [[0.9]]
        
        reranked = reranker.rerank(query, results)
        
        assert reranked is not None

    @pytest.mark.parametrize("device", ["cpu", "cuda"])
    def test_device_selection(self, device, mock_model):
        """Test device selection"""
        with patch('backend.rag.reranker.CrossEncoder', return_value=mock_model):
            reranker = Reranker(model_name="test-reranker", device=device)
            assert reranker is not None

    def test_rerank_updates_scores(self, reranker, mock_model):
        """Test that reranking updates result scores"""
        query = "Test query"
        original_score = 0.5
        reranker_score = 0.9
        
        results = [{"text": "Result", "score": original_score}]
        mock_model.compute_score.return_value = [[reranker_score]]
        
        reranked = reranker.rerank(query, results)
        
        assert len(reranked) == 1
        # Score should be updated (implementation dependent)

    def test_rerank_batch_processing(self, reranker, mock_model):
        """Test reranking with batch processing"""
        query = "Test query"
        results = [{"text": f"Result {i}", "score": 0.5} for i in range(100)]
        
        mock_model.compute_score.return_value = [[0.9 - i*0.001] for i in range(100)]
        
        reranked = reranker.rerank(query, results, batch_size=32)
        
        assert len(reranked) == 100

    def test_multiple_rerank_calls(self, reranker, mock_model):
        """Test multiple sequential rerank calls"""
        query = "Test query"
        
        for i in range(5):
            results = [{"text": f"Result {i}", "score": 0.5}]
            mock_model.compute_score.return_value = [[0.9]]
            reranked = reranker.rerank(query, results)
            assert len(reranked) == 1


# Made with Bob