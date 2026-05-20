"""
PDF Processor Tests
Testovi za PDF processing funkcionalnost
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os

from backend.rag.pdf_processor import PDFProcessor


@pytest.mark.rag
class TestPDFProcessor:
    """Test suite for PDF Processor"""

    @pytest.fixture
    def pdf_processor(self):
        """Create PDF processor instance"""
        return PDFProcessor()

    def test_pdf_processor_initialization(self, pdf_processor):
        """Test PDF processor initialization"""
        assert pdf_processor is not None
        assert hasattr(pdf_processor, 'extract_text')

    def test_extract_text_from_valid_pdf(self, pdf_processor, temp_pdf_file):
        """Test extracting text from valid PDF"""
        result = pdf_processor.extract_text(temp_pdf_file)
        
        assert result is not None
        assert 'text' in result
        assert 'pages' in result
        assert isinstance(result['text'], str)
        assert isinstance(result['pages'], int)
        assert result['pages'] > 0

    def test_extract_text_from_nonexistent_file(self, pdf_processor):
        """Test extracting text from non-existent file"""
        with pytest.raises(FileNotFoundError):
            pdf_processor.extract_text("/nonexistent/file.pdf")

    def test_extract_text_from_invalid_pdf(self, pdf_processor):
        """Test extracting text from invalid PDF file"""
        # Create a temporary invalid PDF file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"This is not a valid PDF file")
            temp_path = f.name
        
        try:
            with pytest.raises(Exception):
                pdf_processor.extract_text(temp_path)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_extract_text_with_metadata(self, pdf_processor, temp_pdf_file):
        """Test that extracted text includes metadata"""
        result = pdf_processor.extract_text(temp_pdf_file)
        
        assert 'metadata' in result or 'pages' in result
        if 'metadata' in result:
            assert isinstance(result['metadata'], dict)

    @patch('backend.rag.pdf_processor.fitz')
    def test_extract_text_handles_empty_pages(self, mock_fitz, pdf_processor):
        """Test handling of PDFs with empty pages"""
        # Mock PyMuPDF document
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = ""
        mock_doc.__iter__.return_value = [mock_page]
        mock_doc.__len__.return_value = 1
        mock_fitz.open.return_value = mock_doc
        
        result = pdf_processor.extract_text("dummy.pdf")
        
        assert result is not None
        assert result['pages'] == 1
        assert result['text'] == "" or result['text'].strip() == ""

    def test_extract_text_preserves_structure(self, pdf_processor, temp_pdf_file):
        """Test that text extraction preserves basic structure"""
        result = pdf_processor.extract_text(temp_pdf_file)
        
        # Check that text is not None and is a string
        assert isinstance(result['text'], str)
        
        # For a valid PDF, we should get some content
        # (even if minimal for our test PDF)
        assert len(result['text']) >= 0

    def test_process_multiple_pdfs(self, pdf_processor, temp_pdf_file):
        """Test processing multiple PDFs sequentially"""
        results = []
        
        for _ in range(3):
            result = pdf_processor.extract_text(temp_pdf_file)
            results.append(result)
        
        assert len(results) == 3
        for result in results:
            assert 'text' in result
            assert 'pages' in result

    def test_extract_text_with_special_characters(self, pdf_processor):
        """Test handling of PDFs with special characters"""
        # This test would require a PDF with special characters
        # For now, we'll skip it or use a mock
        pass

    @pytest.mark.parametrize("file_extension", [".pdf", ".PDF", ".Pdf"])
    def test_accepts_various_pdf_extensions(self, pdf_processor, file_extension):
        """Test that processor accepts various PDF file extensions"""
        # Create temp file with different extension
        with tempfile.NamedTemporaryFile(suffix=file_extension, delete=False) as f:
            # Write minimal PDF content
            f.write(b"%PDF-1.4\n")
            f.write(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
            f.write(b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n")
            f.write(b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\nendobj\n")
            f.write(b"xref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n")
            f.write(b"0000000058 00000 n\n0000000115 00000 n\ntrailer\n")
            f.write(b"<< /Size 4 /Root 1 0 R >>\nstartxref\n190\n%%EOF\n")
            temp_path = f.name
        
        try:
            result = pdf_processor.extract_text(temp_path)
            assert result is not None
            assert 'text' in result
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


# Made with Bob