"""
Document Extraction Service for SmartRecruit CV Processing Pipeline.

Extracts normalized raw text and metadata from CV documents in various formats:
- PDF: PyMuPDF (fitz)
- DOCX: python-docx
- TXT: Built-in Python handling with multi-encoding fallback
- DOC: Headless LibreOffice conversion to DOCX if available
"""

import io
import os
import re
import shutil
import subprocess
import tempfile
import unicodedata
from pathlib import Path
from typing import Any, BinaryIO

from app.core.config import settings


# ==============================================================================
# EXCEPTIONS
# ==============================================================================

class DocumentExtractionError(Exception):
    """Base exception for all document extraction errors."""
    pass


class UnsupportedFormatError(DocumentExtractionError):
    """Raised when the document format or extension is not supported."""
    pass


class EmptyDocumentError(DocumentExtractionError):
    """Raised when the document contains 0 bytes or no pages."""
    pass


class CorruptedDocumentError(DocumentExtractionError):
    """Raised when the document is malformed or corrupted."""
    pass


class PasswordProtectedError(DocumentExtractionError):
    """Raised when the document (e.g. PDF) is encrypted or password-protected."""
    pass


class NoExtractableTextError(DocumentExtractionError):
    """Raised when a valid document structure contains no extractable text (e.g., scanned image)."""
    pass


class LibreOfficeNotFoundError(DocumentExtractionError):
    """Raised when LibreOffice is required for .doc conversion but not found on the system."""
    pass


class DocumentConversionError(DocumentExtractionError):
    """Raised when external conversion of a document fails."""
    pass


class FileSizeExceededError(DocumentExtractionError):
    """Raised when a file exceeds the maximum allowed size."""
    pass


# ==============================================================================
# SERVICE IMPLEMENTATION
# ==============================================================================

class DocumentExtractionService:
    """Service responsible for extracting normalized raw text from CV files."""

    SUPPORTED_FORMATS = {"pdf", "docx", "doc", "txt"}

    def __init__(self, max_file_size_mb: int | None = None):
        """
        Initialize the extraction service.
        
        :param max_file_size_mb: Optional maximum file size in megabytes.
                                 Defaults to settings.MAX_CV_FILE_SIZE_MB or 10 MB.
        """
        max_mb = max_file_size_mb or getattr(settings, "MAX_CV_FILE_SIZE_MB", 10)
        self.max_file_size_bytes = max_mb * 1024 * 1024

    def extract(self, file: Any) -> dict[str, Any]:
        """
        Extract normalized raw text and metadata from an uploaded or local CV file.

        :param file: Can be:
                     - A FastAPI / Starlette `UploadFile`
                     - A string or Path pointing to a local file
                     - A file-like object with a `.filename` or `.name` attribute
                     - A tuple of (filename, bytes_data)
        :return: Normalized dictionary containing:
                 {
                     "text": "Cleaned CV text...",
                     "metadata": {
                         "filename": "candidate_cv.pdf",
                         "format": "pdf",
                         "character_count": 1234,
                         "word_count": 210
                     }
                 }
        :raises DocumentExtractionError or its subclasses on validation or extraction failure.
        """
        filename, file_bytes = self._read_file_payload(file)

        # 1. Validate file size
        if len(file_bytes) == 0:
            raise EmptyDocumentError(f"The document '{filename}' is empty (0 bytes).")

        if len(file_bytes) > self.max_file_size_bytes:
            mb_size = len(file_bytes) / (1024 * 1024)
            limit_mb = self.max_file_size_bytes / (1024 * 1024)
            raise FileSizeExceededError(
                f"File '{filename}' ({mb_size:.2f} MB) exceeds maximum allowed size of {limit_mb:.0f} MB."
            )

        # 2. Determine and validate extension
        extension = self._get_extension(filename)
        if extension not in self.SUPPORTED_FORMATS:
            raise UnsupportedFormatError(
                f"Unsupported CV format: '.{extension}'. Supported formats are: "
                f"{', '.join(sorted(self.SUPPORTED_FORMATS)).upper()}."
            )

        # 3. Validate content signature (magic bytes)
        self._validate_content_signature(file_bytes, extension, filename)

        # 4. Dispatch to appropriate extraction method
        if extension == "pdf":
            raw_text = self._extract_pdf(file_bytes, filename)
        elif extension == "docx":
            raw_text = self._extract_docx(file_bytes, filename)
        elif extension == "doc":
            raw_text = self._extract_doc(file_bytes, filename)
        elif extension == "txt":
            raw_text = self._extract_txt(file_bytes, filename)
        else:
            raise UnsupportedFormatError(f"Unsupported CV format: '.{extension}'.")

        # 5. Normalize text
        clean_text = self._normalize_text(raw_text)

        if not clean_text:
            raise NoExtractableTextError(
                f"No extractable text found in '{filename}'. "
                "The file may contain only scanned images or non-text elements."
            )

        return {
            "text": clean_text,
            "metadata": {
                "filename": filename,
                "format": extension,
                "character_count": len(clean_text),
                "word_count": len(clean_text.split()),
            },
        }

    # --------------------------------------------------------------------------
    # PAYLOAD & VALIDATION HELPERS
    # --------------------------------------------------------------------------

    def _read_file_payload(self, file: Any) -> tuple[str, bytes]:
        """Extract filename and raw bytes from various file representations."""
        # Tuple of (filename, bytes)
        if isinstance(file, tuple) and len(file) == 2 and isinstance(file[1], (bytes, bytearray)):
            return str(file[0]), bytes(file[1])

        # Local file path (str or Path)
        if isinstance(file, (str, Path)):
            path = Path(file)
            if not path.is_file():
                raise DocumentExtractionError(f"File not found on disk: '{file}'.")
            try:
                content = path.read_bytes()
            except Exception as e:
                raise DocumentExtractionError(f"Failed to read file '{file}': {str(e)}") from e
            return path.name, content

        # FastAPI / Starlette UploadFile
        if hasattr(file, "filename") and hasattr(file, "file"):
            filename = getattr(file, "filename") or "uploaded_file"
            try:
                underlying = file.file
                underlying.seek(0)
                content = underlying.read()
                underlying.seek(0)
            except Exception as e:
                raise DocumentExtractionError(f"Failed to read uploaded file '{filename}': {str(e)}") from e
            return filename, content

        # Generic file-like object with .read()
        if hasattr(file, "read"):
            filename = getattr(file, "name", "document")
            filename = os.path.basename(str(filename)) if filename else "document"
            try:
                if hasattr(file, "seek"):
                    file.seek(0)
                content = file.read()
                if hasattr(file, "seek"):
                    file.seek(0)
                if isinstance(content, str):
                    content = content.encode("utf-8")
            except Exception as e:
                raise DocumentExtractionError(f"Failed to read file-like object: {str(e)}") from e
            return filename, content

        # Raw bytes passed directly
        if isinstance(file, (bytes, bytearray)):
            return "document.txt", bytes(file)

        raise DocumentExtractionError(f"Unsupported file input type: {type(file).__name__}")

    def _get_extension(self, filename: str) -> str:
        """Extract lowercase file extension without leading dot."""
        parts = filename.lower().rsplit(".", 1)
        if len(parts) > 1 and parts[1].strip():
            return parts[1].strip()
        return ""

    def _validate_content_signature(self, file_bytes: bytes, extension: str, filename: str) -> None:
        """
        Verify header magic bytes where practical to prevent disguised files.
        """
        # PDF magic bytes: %PDF- (often starts at byte 0, but can be preceded by small header)
        if extension == "pdf":
            header_sample = file_bytes[:1024]
            if b"%PDF-" not in header_sample:
                raise CorruptedDocumentError(
                    f"File '{filename}' does not contain a valid PDF signature."
                )

        # DOCX is a zip archive: starts with PK\x03\x04
        elif extension == "docx":
            if not file_bytes.startswith(b"PK\x03\x04"):
                raise CorruptedDocumentError(
                    f"File '{filename}' does not contain a valid DOCX/ZIP signature."
                )

        # Legacy DOC is an OLE Compound Document: \xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1
        elif extension == "doc":
            ole_signature = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"
            if not file_bytes.startswith(ole_signature):
                raise CorruptedDocumentError(
                    f"File '{filename}' does not contain a valid legacy DOC signature."
                )

        # TXT files should not start with binary executables or standard zip headers
        elif extension == "txt":
            # Check for Windows PE executable or Zip masquerading as txt
            if file_bytes.startswith(b"MZ") or file_bytes.startswith(b"PK\x03\x04"):
                raise CorruptedDocumentError(
                    f"File '{filename}' appears to be a binary executable or archive, not a text file."
                )

    # --------------------------------------------------------------------------
    # FORMAT-SPECIFIC EXTRACTORS
    # --------------------------------------------------------------------------

    def _extract_pdf(self, file_bytes: bytes, filename: str) -> str:
        """Extract text from PDF using PyMuPDF (fitz)."""
        try:
            try:
                import pymupdf as fitz
            except ImportError:
                import fitz
        except ImportError as e:
            raise DocumentExtractionError(
                "PyMuPDF library is not installed. Please install PyMuPDF to extract PDF documents."
            ) from e

        doc = None
        try:
            try:
                doc = fitz.open(stream=file_bytes, filetype="pdf")
            except Exception as e:
                raise CorruptedDocumentError(f"Corrupted or invalid PDF file '{filename}': {str(e)}") from e

            # Check password protection
            if doc.is_encrypted or doc.needs_pass:
                raise PasswordProtectedError(
                    f"The PDF file '{filename}' is password-protected and cannot be read."
                )

            if doc.page_count == 0:
                raise EmptyDocumentError(f"The PDF file '{filename}' contains no pages.")

            pages_text: list[str] = []
            for page_idx in range(doc.page_count):
                try:
                    page = doc[page_idx]
                    page_text = page.get_text("text")
                    if page_text and page_text.strip():
                        pages_text.append(page_text)
                except Exception as e:
                    # Log page error but attempt remaining pages
                    continue

            return "\n\n".join(pages_text)

        finally:
            if doc is not None:
                try:
                    doc.close()
                except Exception:
                    pass

    def _extract_docx(self, file_bytes: bytes, filename: str) -> str:
        """Extract text from DOCX using python-docx."""
        try:
            import docx
            from docx.opc.exceptions import PackageNotFoundError
        except ImportError as e:
            raise DocumentExtractionError(
                "python-docx library is not installed. Please install python-docx to extract DOCX documents."
            ) from e

        try:
            stream = io.BytesIO(file_bytes)
            doc = docx.Document(stream)
        except (PackageNotFoundError, Exception) as e:
            raise CorruptedDocumentError(
                f"Corrupted or invalid DOCX document '{filename}': {str(e)}"
            ) from e

        chunks: list[str] = []

        # 1. Paragraph text
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                chunks.append(text)

        # 2. Table text (frequently used in CVs for education/work layout)
        for table in doc.tables:
            for row in table.rows:
                cells = [c.text.strip() for c in row.cells if c.text.strip()]
                if cells:
                    # De-duplicate consecutive merged cells
                    unique_cells: list[str] = []
                    for cell in cells:
                        if not unique_cells or cell != unique_cells[-1]:
                            unique_cells.append(cell)
                    chunks.append(" | ".join(unique_cells))

        return "\n\n".join(chunks)

    def _extract_txt(self, file_bytes: bytes, filename: str) -> str:
        """Extract plain text with multi-encoding fallback."""
        encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "iso-8859-1"]
        for enc in encodings:
            try:
                decoded = file_bytes.decode(enc)
                # Check for excessive NUL bytes (corrupted binary)
                if "\x00" in decoded and decoded.count("\x00") > 5:
                    continue
                return decoded
            except UnicodeDecodeError:
                continue

        raise CorruptedDocumentError(
            f"Unable to decode text file '{filename}' with supported encodings (UTF-8, Latin-1, CP1252)."
        )

    def _extract_doc(self, file_bytes: bytes, filename: str) -> str:
        """
        Extract text from legacy .doc files using LibreOffice in headless mode.
        If LibreOffice is not available, raises LibreOfficeNotFoundError.
        """
        libreoffice_bin = self._find_libreoffice_executable()
        if not libreoffice_bin:
            raise LibreOfficeNotFoundError(
                f"LibreOffice is required to extract legacy .doc files ('{filename}') "
                "but is not installed or not found in system PATH. "
                "Please convert your document to .docx or .pdf."
            )

        with tempfile.TemporaryDirectory(prefix="cv_extract_") as temp_dir:
            temp_path = Path(temp_dir)
            input_doc_path = temp_path / "input.doc"
            input_doc_path.write_bytes(file_bytes)

            try:
                cmd = [
                    libreoffice_bin,
                    "--headless",
                    "--invisible",
                    "--nologo",
                    "--convert-to",
                    "docx",
                    "--outdir",
                    str(temp_path),
                    str(input_doc_path),
                ]

                result = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=35,
                    check=False,
                )

                converted_docx = temp_path / "input.docx"
                if result.returncode != 0 or not converted_docx.is_file():
                    err_msg = result.stderr.decode("utf-8", errors="ignore").strip()
                    raise DocumentConversionError(
                        f"LibreOffice conversion failed for '{filename}': {err_msg or 'unknown conversion error'}"
                    )

                docx_bytes = converted_docx.read_bytes()
                return self._extract_docx(docx_bytes, filename)

            except subprocess.TimeoutExpired as e:
                raise DocumentConversionError(
                    f"LibreOffice conversion timed out after 35 seconds for '{filename}'."
                ) from e
            except DocumentExtractionError:
                raise
            except Exception as e:
                raise DocumentConversionError(
                    f"Error converting legacy .doc file '{filename}': {str(e)}"
                ) from e

    def _find_libreoffice_executable(self) -> str | None:
        """Locate LibreOffice executable across Linux, macOS, and Windows."""
        # 1. Check PATH
        for cmd in ["soffice", "libreoffice"]:
            found = shutil.which(cmd)
            if found:
                return found

        # 2. Check standard system installation paths
        known_paths = [
            # Linux
            "/usr/bin/libreoffice",
            "/usr/bin/soffice",
            "/usr/lib/libreoffice/program/soffice",
            "/opt/libreoffice/program/soffice",
            # Windows
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
            # macOS
            "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        ]

        for p in known_paths:
            if os.path.isfile(p) and os.access(p, os.X_OK if os.name != "nt" else os.R_OK):
                return p

        return None

    # --------------------------------------------------------------------------
    # TEXT NORMALIZATION
    # --------------------------------------------------------------------------

    def _normalize_text(self, text: str) -> str:
        """
        Clean and normalize raw extracted text:
        - Normalize Unicode (NFKC)
        - Normalize line breaks to \n
        - Normalize whitespace and non-breaking spaces
        - Remove excessive empty lines while preserving paragraph boundaries
        """
        if not text:
            return ""

        # Normalize Unicode characters
        normalized = unicodedata.normalize("NFKC", text)

        # Standardize line breaks
        normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")
        normalized = normalized.replace("\x0c", "\n").replace("\x0b", "\n")

        # Replace non-breaking spaces and tabs with standard space
        normalized = normalized.replace("\xa0", " ").replace("\u200b", "")
        normalized = re.sub(r"[^\S\n]+", " ", normalized)

        # Process line by line: trim whitespace
        cleaned_lines = [line.strip() for line in normalized.split("\n")]

        # Collapse more than 2 consecutive newlines into 2 (preserves paragraph separation)
        text_joined = "\n".join(cleaned_lines)
        text_joined = re.sub(r"\n{3,}", "\n\n", text_joined)

        return text_joined.strip()
