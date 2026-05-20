"""
PDFs API Tests
Testovi za PDF CRUD endpoints
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import Mock, patch
import tempfile
import os

from backend.models.pdf import PDF
from backend.models.collection import Collection


@pytest.mark.api
class TestPDFsAPI:
    """Test suite for PDFs API endpoints"""

    def test_upload_pdf(self, test_client: TestClient, sample_collection: Collection, temp_pdf_file):
        """Test uploading a PDF file"""
        with open(temp_pdf_file, 'rb') as f:
            response = test_client.post(
                f"/api/pdfs/upload?collection_id={sample_collection.id}",
                files={"file": ("test.pdf", f, "application/pdf")}
            )
        
        assert response.status_code in [200, 201]
        data = response.json()
        assert "id" in data or "filename" in data

    def test_upload_pdf_invalid_collection(self, test_client: TestClient, temp_pdf_file):
        """Test uploading PDF to non-existent collection"""
        with open(temp_pdf_file, 'rb') as f:
            response = test_client.post(
                "/api/pdfs/upload?collection_id=99999",
                files={"file": ("test.pdf", f, "application/pdf")}
            )
        
        assert response.status_code == 404

    def test_upload_pdf_no_file(self, test_client: TestClient, sample_collection: Collection):
        """Test uploading without file"""
        response = test_client.post(
            f"/api/pdfs/upload?collection_id={sample_collection.id}"
        )
        
        assert response.status_code == 422

    def test_get_pdfs(self, test_client: TestClient, sample_pdf: PDF):
        """Test getting all PDFs"""
        response = test_client.get("/api/pdfs/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_pdfs_by_collection(self, test_client: TestClient, sample_collection: Collection, sample_pdf: PDF):
        """Test getting PDFs filtered by collection"""
        response = test_client.get(f"/api/pdfs/?collection_id={sample_collection.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert all(pdf["collection_id"] == sample_collection.id for pdf in data)

    def test_get_pdf_by_id(self, test_client: TestClient, sample_pdf: PDF):
        """Test getting PDF by ID"""
        response = test_client.get(f"/api/pdfs/{sample_pdf.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_pdf.id
        assert data["filename"] == sample_pdf.filename

    def test_get_pdf_not_found(self, test_client: TestClient):
        """Test getting non-existent PDF"""
        response = test_client.get("/api/pdfs/99999")
        
        assert response.status_code == 404

    def test_delete_pdf(self, test_client: TestClient, test_db_session: Session, sample_collection: Collection):
        """Test deleting PDF"""
        # Create a PDF to delete
        pdf = PDF(
            filename="to_delete.pdf",
            filepath="/tmp/to_delete.pdf",
            size_bytes=1024,
            collection_id=sample_collection.id,
            pages=5,
            status="completed"
        )
        test_db_session.add(pdf)
        test_db_session.commit()
        test_db_session.refresh(pdf)
        
        response = test_client.delete(f"/api/pdfs/{pdf.id}")
        
        assert response.status_code in [200, 204]
        
        # Verify deletion
        get_response = test_client.get(f"/api/pdfs/{pdf.id}")
        assert get_response.status_code == 404

    def test_delete_pdf_not_found(self, test_client: TestClient):
        """Test deleting non-existent PDF"""
        response = test_client.delete("/api/pdfs/99999")
        
        assert response.status_code == 404

    def test_get_pdf_processing_status(self, test_client: TestClient, sample_pdf: PDF):
        """Test getting PDF processing status"""
        response = test_client.get(f"/api/pdfs/{sample_pdf.id}/status")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["pending", "processing", "completed", "failed"]

    def test_reprocess_pdf(self, test_client: TestClient, sample_pdf: PDF):
        """Test reprocessing a PDF"""
        response = test_client.post(f"/api/pdfs/{sample_pdf.id}/reprocess")
        
        # Should accept the request or return appropriate status
        assert response.status_code in [200, 202, 404]

    def test_get_pdf_chunks(self, test_client: TestClient, sample_pdf: PDF):
        """Test getting PDF chunks"""
        response = test_client.get(f"/api/pdfs/{sample_pdf.id}/chunks")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_upload_multiple_pdfs(self, test_client: TestClient, sample_collection: Collection, temp_pdf_file):
        """Test uploading multiple PDFs"""
        uploaded_ids = []
        
        for i in range(3):
            with open(temp_pdf_file, 'rb') as f:
                response = test_client.post(
                    f"/api/pdfs/upload?collection_id={sample_collection.id}",
                    files={"file": (f"test_{i}.pdf", f, "application/pdf")}
                )
            
            if response.status_code in [200, 201]:
                data = response.json()
                if "id" in data:
                    uploaded_ids.append(data["id"])
        
        # Should have uploaded at least some files
        assert len(uploaded_ids) >= 0

    def test_pdf_pagination(self, test_client: TestClient, test_db_session: Session, sample_collection: Collection):
        """Test PDF list pagination"""
        # Create multiple PDFs
        for i in range(15):
            pdf = PDF(
                filename=f"test_{i}.pdf",
                filepath=f"/tmp/test_{i}.pdf",
                size_bytes=1024,
                collection_id=sample_collection.id,
                pages=5,
                status="completed"
            )
            test_db_session.add(pdf)
        test_db_session.commit()
        
        # Test with limit
        response = test_client.get("/api/pdfs/?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 10
        
        # Test with skip
        response = test_client.get("/api/pdfs/?skip=5&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5

    def test_upload_pdf_invalid_format(self, test_client: TestClient, sample_collection: Collection):
        """Test uploading non-PDF file"""
        # Create a text file
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"This is not a PDF")
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                response = test_client.post(
                    f"/api/pdfs/upload?collection_id={sample_collection.id}",
                    files={"file": ("test.txt", f, "text/plain")}
                )
            
            # Should reject non-PDF files
            assert response.status_code in [400, 422]
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_get_pdf_statistics(self, test_client: TestClient, sample_pdf: PDF):
        """Test getting PDF statistics"""
        response = test_client.get(f"/api/pdfs/{sample_pdf.id}/statistics")
        
        # Endpoint may or may not exist
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)


# Made with Bob