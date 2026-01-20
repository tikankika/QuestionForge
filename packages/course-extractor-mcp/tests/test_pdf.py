"""
Unit tests for CourseExtractor MCP Server

Run with: pytest tests/test_pdf.py -v
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, PropertyMock
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from server import _extract_pdf_impl as extract_pdf


def test_extract_pdf_file_not_found():
    """Test file not found error"""
    result = extract_pdf(file_path="/nonexistent.pdf")
    assert "error" in result
    assert "hittades inte" in result["error"]


def test_extract_pdf_not_pdf():
    """Test non-PDF file"""
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
        f.write(b"not a pdf")
        temp_path = f.name

    try:
        result = extract_pdf(file_path=temp_path)
        assert "error" in result
        assert "måste vara en PDF" in result["error"]
    finally:
        Path(temp_path).unlink()


def test_extract_pdf_too_large():
    """Test file size limit"""
    # Create actual temp file with valid PDF extension
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(b"%PDF-1.4\n")  # Minimal PDF header
        temp_path = f.name

    try:
        # Mock only the stat call to return large size
        original_stat = Path.stat

        def mock_stat(self, **kwargs):  # Accept keyword args like follow_symlinks
            if str(self).endswith('.pdf'):
                mock = MagicMock()
                mock.st_size = 101 * 1024 * 1024  # 101 MB
                return mock
            return original_stat(self)

        with patch.object(Path, 'stat', mock_stat):
            result = extract_pdf(file_path=temp_path)
            assert "error" in result
            assert "för stor" in result["error"]
    finally:
        Path(temp_path).unlink()


def test_extract_pdf_encrypted():
    """Test encrypted PDF rejection"""
    # Create temp PDF file
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(b"%PDF-1.4\n")
        temp_path = f.name

    try:
        # Patch at the location where it's imported in server.py
        with patch('server.fitz.open') as mock_open:
            mock_doc = MagicMock()
            mock_doc.is_encrypted = True
            mock_open.return_value = mock_doc

            # Use allowed output folder
            result = extract_pdf(file_path=temp_path, output_folder="/tmp/test_encrypted")
            assert "error" in result
            assert "Krypterad" in result["error"]
    finally:
        Path(temp_path).unlink()


def test_output_path_whitelist():
    """Test output path security"""
    # Create temp PDF file
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(b"%PDF-1.4\n")
        temp_path = f.name

    try:
        result = extract_pdf(
            file_path=temp_path,
            output_folder="/etc/cron.d"  # Dangerous path!
        )

        assert "error" in result
        assert "måste vara under" in result["error"]
    finally:
        Path(temp_path).unlink()


@pytest.mark.skipif(not Path("examples/sample.pdf").exists(),
                    reason="Requires examples/sample.pdf")
def test_extract_pdf_basic():
    """Test basic PDF extraction (requires real PDF)"""
    result = extract_pdf(
        file_path="examples/sample.pdf",
        output_folder="/tmp/test_course_extractor"
    )

    # Should succeed
    assert "error" not in result
    assert "text_markdown" in result
    assert "images" in result
    assert "metadata" in result
    assert result["metadata"]["pages"] > 0

    # Images should be simple list (no page parsing)
    if result["images"]:
        img = result["images"][0]
        assert "index" in img
        assert "saved_path" in img
        assert "format" in img
        assert "filename" in img


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
