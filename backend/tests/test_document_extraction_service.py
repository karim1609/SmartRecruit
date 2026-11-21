"""
Unit tests for DocumentExtractionService.

Tests PDF, DOCX, TXT, DOC, edge cases, error conditions, and text normalization.
"""

import io
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.services.document_extraction_service import (
    DocumentExtractionService,
    DocumentExtractionError,
    UnsupportedFormatError,
    EmptyDocumentError,
    CorruptedDocumentError,
    PasswordProtectedError,
    NoExtractableTextError,
    LibreOfficeNotFoundError,
    DocumentConversionError,
    FileSizeExceededError,
)


@pytest.fixture
def service():
    """Create a fresh DocumentExtractionService instance."""
    return DocumentExtractionService(max_file_size_mb=5)


# ==============================================================================
# 1. VALID PDF EXTRACTION
# ==============================================================================

def test_extract_valid_pdf(service):
    """Test extracting text from a valid PDF document."""
    try:
        import pymupdf as fitz
    except ImportError:
        import fitz

    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 72), "John Doe\nSenior Backend Engineer\nSkills: Python, FastAPI, Docker")
    pdf_bytes = doc.tobytes()
    doc.close()

    result = service.extract(("john_doe_cv.pdf", pdf_bytes))

    assert "John Doe" in result["text"]
    assert "Senior Backend Engineer" in result["text"]
    assert "FastAPI" in result["text"]
    assert result["metadata"]["filename"] == "john_doe_cv.pdf"
    assert result["metadata"]["format"] == "pdf"
    assert result["metadata"]["character_count"] > 0
    assert result["metadata"]["word_count"] > 0


# ==============================================================================
# 2. VALID DOCX EXTRACTION
# ==============================================================================

def test_extract_valid_docx(service):
    """Test extracting text from a valid DOCX document (including tables)."""
    import docx

    doc = docx.Document()
    doc.add_heading("Jane Smith - CV", level=1)
    doc.add_paragraph("Experienced DevOps Engineer with AWS and Kubernetes expertise.")

    # Add a table to test table extraction
    table = doc.add_table(rows=2, cols=2)
    table.cell(0, 0).text = "Education"
    table.cell(0, 1).text = "Degree"
    table.cell(1, 0).text = "UC Berkeley"
    table.cell(1, 1).text = "B.S. Computer Science"

    stream = io.BytesIO()
    doc.save(stream)
    docx_bytes = stream.getvalue()

    result = service.extract(("jane_smith_cv.docx", docx_bytes))

    assert "Jane Smith - CV" in result["text"]
    assert "DevOps Engineer" in result["text"]
    assert "UC Berkeley" in result["text"]
    assert "B.S. Computer Science" in result["text"]
    assert result["metadata"]["filename"] == "jane_smith_cv.docx"
    assert result["metadata"]["format"] == "docx"


# ==============================================================================
# 3. VALID TXT EXTRACTION
# ==============================================================================

def test_extract_valid_txt(service):
    """Test extracting text from a valid TXT document."""
    txt_content = (
        "Alex Morgan\n"
        "Full-Stack Developer\n\n"
        "Work Experience:\n"
        "Software Engineer at TechCorp (2020-Present)\n"
        "- Built React and Node.js microservices."
    )
    txt_bytes = txt_content.encode("utf-8")

    result = service.extract(("alex_morgan.txt", txt_bytes))

    assert "Alex Morgan" in result["text"]
    assert "Full-Stack Developer" in result["text"]
    assert "TechCorp" in result["text"]
    assert result["metadata"]["filename"] == "alex_morgan.txt"
    assert result["metadata"]["format"] == "txt"


def test_extract_txt_latin1_encoding(service):
    """Test extracting TXT with non-UTF8 encoding (Latin-1)."""
    txt_content = "Développeur Logiciel - Expérience professionnelle à Montréal"
    txt_bytes = txt_content.encode("latin-1")

    result = service.extract(("french_cv.txt", txt_bytes))
    assert "Développeur Logiciel" in result["text"]


# ==============================================================================
# 4. UNSUPPORTED EXTENSION
# ==============================================================================

def test_extract_unsupported_extension(service):
    """Test that unsupported file formats raise UnsupportedFormatError."""
    with pytest.raises(UnsupportedFormatError) as exc_info:
        service.extract(("cv.exe", b"MZDummyExecutableContent"))
    assert "Unsupported CV format" in str(exc_info.value)

    with pytest.raises(UnsupportedFormatError):
        service.extract(("portfolio.png", b"\x89PNG\r\n\x1a\n"))

    with pytest.raises(UnsupportedFormatError):
        service.extract(("presentation.pptx", b"PK\x03\x04..."))


# ==============================================================================
# 5. EMPTY DOCUMENT
# ==============================================================================

def test_extract_empty_file_zero_bytes(service):
    """Test that an empty 0-byte file raises EmptyDocumentError."""
    with pytest.raises(EmptyDocumentError) as exc_info:
        service.extract(("empty_cv.pdf", b""))
    assert "empty (0 bytes)" in str(exc_info.value)


def test_extract_pdf_empty_pages(service):
    """Test that a PDF with 0 pages raises EmptyDocumentError."""
    try:
        import pymupdf as fitz_mod
    except ImportError:
        import fitz as fitz_mod

    doc = fitz_mod.open()
    doc.new_page()
    pdf_bytes = doc.tobytes()
    doc.close()

    # Mock page_count to 0 to simulate a document with no pages
    mock_doc = MagicMock()
    mock_doc.is_encrypted = False
    mock_doc.needs_pass = False
    mock_doc.page_count = 0

    with patch.object(fitz_mod, "open", return_value=mock_doc):
        with pytest.raises(EmptyDocumentError) as exc_info:
            service.extract(("empty_pages.pdf", pdf_bytes))
        assert "contains no pages" in str(exc_info.value)


# ==============================================================================
# 6. CORRUPTED DOCUMENT
# ==============================================================================

def test_extract_corrupted_pdf(service):
    """Test that a corrupted PDF raises CorruptedDocumentError."""
    corrupted_pdf = b"%PDF-1.4\nCorrupted binary junk that cannot be parsed by fitz \x00\xff\xfe"
    with pytest.raises(CorruptedDocumentError):
        service.extract(("broken.pdf", corrupted_pdf))


def test_extract_corrupted_docx(service):
    """Test that invalid zip data with docx signature raises CorruptedDocumentError."""
    # Starts with PK\x03\x04 but is truncated/corrupted
    corrupted_docx = b"PK\x03\x04" + b"invalid broken payload" * 10
    with pytest.raises(CorruptedDocumentError):
        service.extract(("broken.docx", corrupted_docx))


def test_extract_disguised_file_signature_mismatch(service):
    """Test that a file renamed to .pdf with non-PDF content is rejected."""
    fake_pdf = b"This is just plain text renamed to .pdf"
    with pytest.raises(CorruptedDocumentError) as exc_info:
        service.extract(("fake.pdf", fake_pdf))
    assert "valid PDF signature" in str(exc_info.value)


# ==============================================================================
# 7. PASSWORD-PROTECTED PDF
# ==============================================================================

def test_extract_password_protected_pdf(service):
    """Test that encrypted/password-protected PDFs raise PasswordProtectedError."""
    try:
        import pymupdf as fitz
    except ImportError:
        import fitz

    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 72), "Confidential Resume")

    # Encrypt the PDF
    perm = int(
        fitz.PDF_PERM_ACCESSIBILITY
        | fitz.PDF_PERM_PRINT
        | fitz.PDF_PERM_COPY
        | fitz.PDF_PERM_ANNOTATE
    )
    pdf_bytes = doc.tobytes(
        encryption=fitz.PDF_ENCRYPT_AES_256,
        user_pw="mysecretpassword",
        owner_pw="ownerpassword",
        permissions=perm,
    )
    doc.close()

    with pytest.raises(PasswordProtectedError) as exc_info:
        service.extract(("protected.pdf", pdf_bytes))
    assert "password-protected" in str(exc_info.value)


# ==============================================================================
# 8. SCANNED / IMAGE-ONLY PDF (NO TEXT)
# ==============================================================================

def test_extract_scanned_pdf_no_text(service):
    """Test that a PDF with blank pages or only drawings/images raises NoExtractableTextError."""
    try:
        import pymupdf as fitz
    except ImportError:
        import fitz

    doc = fitz.open()
    # Add a blank page with no text
    doc.new_page(width=595, height=842)
    pdf_bytes = doc.tobytes()
    doc.close()

    with pytest.raises(NoExtractableTextError) as exc_info:
        service.extract(("scanned_image.pdf", pdf_bytes))
    assert "No extractable text found" in str(exc_info.value)


# ==============================================================================
# 9. LEGACY DOC BEHAVIOR WHEN LIBREOFFICE IS UNAVAILABLE
# ==============================================================================

def test_extract_doc_when_libreoffice_unavailable(service):
    """Test that .doc raises LibreOfficeNotFoundError when LibreOffice is not installed."""
    ole_header = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"\x00" * 512

    with patch.object(service, "_find_libreoffice_executable", return_value=None):
        with pytest.raises(LibreOfficeNotFoundError) as exc_info:
            service.extract(("legacy_resume.doc", ole_header))
        assert "LibreOffice is required" in str(exc_info.value)
        assert ".docx or .pdf" in str(exc_info.value)


# ==============================================================================
# 10. LEGACY DOC CONVERSION WHEN LIBREOFFICE IS AVAILABLE (MOCKED)
# ==============================================================================

def test_extract_doc_when_libreoffice_available_mocked(service):
    """Test that .doc converts and extracts properly when LibreOffice succeeds."""
    ole_header = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"\x00" * 512

    # Create a valid target docx bytes
    import docx

    dummy_doc = docx.Document()
    dummy_doc.add_paragraph("Converted Legacy Word Resume Content")
    stream = io.BytesIO()
    dummy_doc.save(stream)
    converted_docx_bytes = stream.getvalue()

    def fake_subprocess_run(cmd, *args, **kwargs):
        # find the outdir in cmd
        outdir_idx = cmd.index("--outdir") + 1
        outdir = Path(cmd[outdir_idx])
        (outdir / "input.docx").write_bytes(converted_docx_bytes)
        mock_res = MagicMock()
        mock_res.returncode = 0
        return mock_res

    with patch.object(service, "_find_libreoffice_executable", return_value="/usr/bin/soffice"):
        with patch("subprocess.run", side_effect=fake_subprocess_run):
            result = service.extract(("legacy_resume.doc", ole_header))

            assert "Converted Legacy Word Resume Content" in result["text"]
            assert result["metadata"]["filename"] == "legacy_resume.doc"
            assert result["metadata"]["format"] == "doc"


def test_extract_doc_libreoffice_conversion_failure(service):
    """Test that a failing LibreOffice process raises DocumentConversionError."""
    ole_header = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"\x00" * 512

    mock_res = MagicMock()
    mock_res.returncode = 1
    mock_res.stderr = b"Fatal Error: Conversion aborted"

    with patch.object(service, "_find_libreoffice_executable", return_value="/usr/bin/soffice"):
        with patch("subprocess.run", return_value=mock_res):
            with pytest.raises(DocumentConversionError) as exc_info:
                service.extract(("legacy_resume.doc", ole_header))
            assert "LibreOffice conversion failed" in str(exc_info.value)


# ==============================================================================
# 11. FILE SIZE LIMIT
# ==============================================================================

def test_extract_file_size_exceeded():
    """Test that files exceeding max_file_size_mb raise FileSizeExceededError."""
    small_service = DocumentExtractionService(max_file_size_mb=1)  # 1 MB limit
    big_data = b"%PDF-" + b"A" * (2 * 1024 * 1024)  # 2 MB

    with pytest.raises(FileSizeExceededError) as exc_info:
        small_service.extract(("huge_cv.pdf", big_data))
    assert "exceeds maximum allowed size" in str(exc_info.value)


# ==============================================================================
# 12. TEXT NORMALIZATION
# ==============================================================================

def test_text_normalization(service):
    """Test that text normalization cleans spacing, line breaks, and excessive blank lines."""
    raw_text = (
        "  Line 1 with \t tabs and non-breaking\xa0space.   \r\n\r\n"
        "\r\n\r\n\r\n"
        "Line 2 after huge gap.  \r\n"
        "Line 3.\n"
    )
    normalized = service._normalize_text(raw_text)

    # Should not have carriage returns
    assert "\r" not in normalized
    # Should not have non-breaking space
    assert "\xa0" not in normalized
    # Should preserve paragraph separation without more than 2 consecutive newlines
    assert "\n\n\n" not in normalized
    assert "Line 1 with tabs and non-breaking space." in normalized
    assert "Line 2 after huge gap." in normalized


# ==============================================================================
# 13. FASTAPI UPLOADFILE AND LOCAL PATH SUPPORT
# ==============================================================================

def test_extract_from_local_file_path(service):
    """Test extracting directly from a file path on disk."""
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w", encoding="utf-8") as f:
        f.write("Local Disk Resume Content for Testing")
        f_path = f.name

    try:
        result = service.extract(f_path)
        assert "Local Disk Resume Content for Testing" in result["text"]
        assert result["metadata"]["format"] == "txt"
    finally:
        if os.path.exists(f_path):
            os.remove(f_path)


def test_extract_from_fastapi_uploadfile(service):
    """Test extracting from a mock FastAPI UploadFile object."""
    mock_upload = MagicMock()
    mock_upload.filename = "candidate.txt"
    mock_upload.file = io.BytesIO(b"Candidate Content through UploadFile")

    result = service.extract(mock_upload)
    assert "Candidate Content through UploadFile" in result["text"]
    assert result["metadata"]["filename"] == "candidate.txt"
