"""
Chunking Tests
Testovi za text chunking funkcionalnost
"""
import pytest
from backend.rag.chunking import (
    SemanticChunking,
    FixedSizeChunking,
    SentenceChunking,
    get_chunking_strategy
)


@pytest.mark.rag
class TestSemanticChunking:
    """Test suite for semantic chunking"""

    @pytest.fixture
    def chunker(self):
        """Create semantic chunker instance"""
        return SemanticChunking(chunk_size=500, overlap=50)

    def test_semantic_chunking_initialization(self, chunker):
        """Test semantic chunker initialization"""
        assert chunker is not None
        assert chunker.chunk_size == 500
        assert chunker.overlap == 50

    def test_semantic_chunk_basic(self, chunker):
        """Test basic semantic chunking"""
        text = "This is paragraph one.\n\nThis is paragraph two.\n\nThis is paragraph three."
        chunks = chunker.chunk(text)
        
        assert len(chunks) > 0
        assert all(isinstance(chunk, dict) for chunk in chunks)
        assert all('text' in chunk for chunk in chunks)
        assert all('id' in chunk for chunk in chunks)
        assert all('type' in chunk for chunk in chunks)

    def test_semantic_chunk_empty_string(self, chunker):
        """Test chunking empty string"""
        chunks = chunker.chunk("")
        
        assert len(chunks) == 0

    def test_semantic_chunk_short_text(self, chunker):
        """Test chunking text shorter than chunk size"""
        text = "Short text"
        chunks = chunker.chunk(text)
        
        assert len(chunks) == 1
        assert chunks[0]['text'] == text

    def test_semantic_chunk_preserves_paragraphs(self, chunker):
        """Test that semantic chunking preserves paragraph structure"""
        text = "Paragraph 1.\n\nParagraph 2.\n\nParagraph 3."
        chunks = chunker.chunk(text)
        
        assert len(chunks) > 0
        assert all('text' in chunk for chunk in chunks)

    def test_semantic_chunk_large_paragraph(self):
        """Test chunking of large paragraphs"""
        text = "This is a very long sentence. " * 100
        chunker = SemanticChunking(chunk_size=200, overlap=20)
        chunks = chunker.chunk(text)
        
        assert len(chunks) > 1
        assert all(chunk['char_count'] <= 220 for chunk in chunks)  # Allow for overlap


@pytest.mark.rag
class TestFixedSizeChunking:
    """Test suite for fixed size chunking"""

    @pytest.fixture
    def chunker(self):
        """Create fixed size chunker instance"""
        return FixedSizeChunking(chunk_size=100, overlap=20)

    def test_fixed_chunking_initialization(self, chunker):
        """Test fixed chunker initialization"""
        assert chunker is not None
        assert chunker.chunk_size == 100
        assert chunker.overlap == 20

    def test_fixed_chunk_basic(self, chunker):
        """Test basic fixed size chunking"""
        text = "a" * 500
        chunks = chunker.chunk(text)
        
        assert len(chunks) > 0
        assert all(isinstance(chunk, dict) for chunk in chunks)
        assert all('text' in chunk for chunk in chunks)

    def test_fixed_chunk_with_overlap(self):
        """Test that overlap works correctly"""
        chunker = FixedSizeChunking(chunk_size=100, overlap=20)
        text = "a" * 300
        chunks = chunker.chunk(text)
        
        # With overlap, we should have more chunks
        assert len(chunks) >= 3

    def test_fixed_chunk_empty_string(self, chunker):
        """Test chunking empty string"""
        chunks = chunker.chunk("")
        
        assert len(chunks) == 0 or (len(chunks) == 1 and chunks[0]['text'] == "")


@pytest.mark.rag
class TestSentenceChunking:
    """Test suite for sentence chunking"""

    @pytest.fixture
    def chunker(self):
        """Create sentence chunker instance"""
        return SentenceChunking(chunk_size=200, overlap_sentences=1)

    def test_sentence_chunking_initialization(self, chunker):
        """Test sentence chunker initialization"""
        assert chunker is not None
        assert chunker.chunk_size == 200
        assert chunker.overlap_sentences == 1

    def test_sentence_chunk_basic(self, chunker):
        """Test basic sentence chunking"""
        text = "First sentence. Second sentence. Third sentence. Fourth sentence."
        chunks = chunker.chunk(text)
        
        assert len(chunks) > 0
        assert all(isinstance(chunk, dict) for chunk in chunks)
        assert all('text' in chunk for chunk in chunks)
        assert all('sentence_count' in chunk for chunk in chunks)

    def test_sentence_chunk_preserves_sentences(self, chunker):
        """Test that sentence boundaries are preserved"""
        text = "Sentence one. Sentence two. Sentence three."
        chunks = chunker.chunk(text)
        
        assert len(chunks) > 0
        # Each chunk should contain complete sentences
        for chunk in chunks:
            assert '.' in chunk['text'] or chunk['text'].endswith('.')


@pytest.mark.rag
class TestChunkingFactory:
    """Test suite for chunking strategy factory"""

    def test_get_semantic_strategy(self):
        """Test getting semantic strategy"""
        strategy = get_chunking_strategy('semantic', chunk_size=500, overlap=50)
        
        assert isinstance(strategy, SemanticChunking)
        assert strategy.chunk_size == 500
        assert strategy.overlap == 50

    def test_get_fixed_strategy(self):
        """Test getting fixed size strategy"""
        strategy = get_chunking_strategy('fixed', chunk_size=100, overlap=20)
        
        assert isinstance(strategy, FixedSizeChunking)
        assert strategy.chunk_size == 100
        assert strategy.overlap == 20

    def test_get_sentence_strategy(self):
        """Test getting sentence strategy"""
        strategy = get_chunking_strategy('sentence', chunk_size=200, overlap_sentences=2)
        
        assert isinstance(strategy, SentenceChunking)
        assert strategy.chunk_size == 200
        assert strategy.overlap_sentences == 2

    def test_invalid_strategy_raises_error(self):
        """Test that invalid strategy raises ValueError"""
        with pytest.raises(ValueError, match="Nepoznata strategija"):
            get_chunking_strategy('invalid_strategy')

    @pytest.mark.parametrize("strategy_name,strategy_class", [
        ('semantic', SemanticChunking),
        ('fixed', FixedSizeChunking),
        ('sentence', SentenceChunking)
    ])
    def test_all_strategies_work(self, strategy_name, strategy_class):
        """Test that all strategies can be created and used"""
        strategy = get_chunking_strategy(strategy_name)
        
        assert isinstance(strategy, strategy_class)
        
        text = "Test text. " * 50
        chunks = strategy.chunk(text)
        
        assert len(chunks) > 0
        assert all(isinstance(chunk, str) for chunk in chunks)


# Made with Bob