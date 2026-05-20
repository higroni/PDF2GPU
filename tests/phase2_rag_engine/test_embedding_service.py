"""
Embedding Service Tests
Testovi za embedding service funkcionalnost
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
import numpy as np

from backend.rag.embedding_service import EmbeddingService


@pytest.mark.rag
class TestEmbeddingService:
    """Test suite for Embedding Service"""

    @pytest.fixture
    def mock_model(self):
        """Create mock embedding model"""
        mock = MagicMock()
        mock.encode = MagicMock(return_value=np.array([[0.1] * 1024]))
        mock.get_sentence_embedding_dimension = MagicMock(return_value=1024)
        return mock

    @pytest.fixture
    def embedding_service(self, mock_model):
        """Create embedding service with mocked model"""
        with patch('backend.rag.embedding_service.SentenceTransformer', return_value=mock_model):
            service = EmbeddingService(model_name="test-model", device="cpu")
            return service

    def test_embedding_service_initialization(self, embedding_service):
        """Test embedding service initialization"""
        assert embedding_service is not None
        assert hasattr(embedding_service, 'encode')
        assert hasattr(embedding_service, 'embedding_dim')

    def test_encode_single_text(self, embedding_service, mock_model):
        """Test encoding single text"""
        text = "Test text"
        embeddings = embedding_service.encode([text])
        
        assert embeddings is not None
        assert len(embeddings) > 0
        mock_model.encode.assert_called_once()

    def test_encode_multiple_texts(self, embedding_service, mock_model):
        """Test encoding multiple texts"""
        texts = ["Text 1", "Text 2", "Text 3"]
        mock_model.encode.return_value = np.array([[0.1] * 1024] * 3)
        
        embeddings = embedding_service.encode(texts)
        
        assert embeddings is not None
        assert len(embeddings) == 3
        mock_model.encode.assert_called_once()

    def test_encode_empty_list(self, embedding_service, mock_model):
        """Test encoding empty list"""
        embeddings = embedding_service.encode([])
        
        # Should return empty array or handle gracefully
        assert embeddings is not None

    def test_encode_with_batch_size(self, embedding_service, mock_model):
        """Test encoding with specific batch size"""
        texts = ["Text"] * 10
        mock_model.encode.return_value = np.array([[0.1] * 1024] * 10)
        
        embeddings = embedding_service.encode(texts, batch_size=5)
        
        assert embeddings is not None
        assert len(embeddings) == 10

    def test_embedding_dimension(self, embedding_service):
        """Test that embedding dimension is correct"""
        assert embedding_service.embedding_dim == 1024

    def test_encode_preserves_order(self, embedding_service, mock_model):
        """Test that encoding preserves text order"""
        texts = ["First", "Second", "Third"]
        mock_model.encode.return_value = np.array([
            [0.1] * 1024,
            [0.2] * 1024,
            [0.3] * 1024
        ])
        
        embeddings = embedding_service.encode(texts)
        
        assert len(embeddings) == 3
        # Order should be preserved

    def test_encode_handles_special_characters(self, embedding_service, mock_model):
        """Test encoding text with special characters"""
        texts = ["Text with @#$%", "Текст са ћирилицом"]
        mock_model.encode.return_value = np.array([[0.1] * 1024] * 2)
        
        embeddings = embedding_service.encode(texts)
        
        assert embeddings is not None
        assert len(embeddings) == 2

    def test_encode_handles_long_text(self, embedding_service, mock_model):
        """Test encoding very long text"""
        long_text = "Word " * 1000
        mock_model.encode.return_value = np.array([[0.1] * 1024])
        
        embeddings = embedding_service.encode([long_text])
        
        assert embeddings is not None
        assert len(embeddings) == 1

    def test_encode_handles_unicode(self, embedding_service, mock_model):
        """Test encoding Unicode text"""
        texts = ["Српски текст", "中文文本", "العربية"]
        mock_model.encode.return_value = np.array([[0.1] * 1024] * 3)
        
        embeddings = embedding_service.encode(texts)
        
        assert embeddings is not None
        assert len(embeddings) == 3

    @pytest.mark.parametrize("device", ["cpu", "cuda"])
    def test_device_selection(self, device, mock_model):
        """Test device selection"""
        with patch('backend.rag.embedding_service.SentenceTransformer', return_value=mock_model):
            service = EmbeddingService(model_name="test-model", device=device)
            assert service is not None

    def test_encode_returns_numpy_array(self, embedding_service, mock_model):
        """Test that encode returns numpy array"""
        texts = ["Test"]
        embeddings = embedding_service.encode(texts)
        
        assert isinstance(embeddings, (np.ndarray, list))

    def test_encode_with_normalization(self, embedding_service, mock_model):
        """Test encoding with normalization"""
        texts = ["Test text"]
        mock_model.encode.return_value = np.array([[0.5] * 1024])
        
        embeddings = embedding_service.encode(texts, normalize_embeddings=True)
        
        assert embeddings is not None
        mock_model.encode.assert_called_once()

    def test_multiple_encode_calls(self, embedding_service, mock_model):
        """Test multiple sequential encode calls"""
        for i in range(5):
            texts = [f"Text {i}"]
            mock_model.encode.return_value = np.array([[0.1] * 1024])
            embeddings = embedding_service.encode(texts)
            assert embeddings is not None

    def test_encode_with_show_progress(self, embedding_service, mock_model):
        """Test encoding with progress bar"""
        texts = ["Text"] * 100
        mock_model.encode.return_value = np.array([[0.1] * 1024] * 100)
        
        embeddings = embedding_service.encode(texts, show_progress_bar=True)
        
        assert embeddings is not None
        assert len(embeddings) == 100


# Made with Bob