"""PDF text extraction service using PyMuPDF."""

import fitz  # PyMuPDF
import logging
import os
import uuid
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)

UPLOAD_FOLDER = 'uploads'


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text content from PDF file.

    Args:
        file_path: Path to the PDF file

    Returns:
        Extracted text as string, or empty string if extraction fails
    """
    try:
        if not os.path.exists(file_path):
            logger.error(f"PDF file not found: {file_path}")
            return ""

        doc = fitz.open(file_path)
        text = ""

        for page in doc:
            text += page.get_text()

        doc.close()

        if not text.strip():
            logger.warning(f"No text extracted from PDF (possibly scanned): {file_path}")

        return text.strip()

    except Exception as e:
        logger.error(f"Failed to extract text from PDF {file_path}: {e}")
        return ""


def save_uploaded_pdf(file) -> str | None:
    """Save uploaded PDF file to uploads directory.

    Args:
        file: Flask FileStorage object

    Returns:
        Path to saved file, or None if save fails
    """
    try:
        # Ensure uploads directory exists
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        # Generate unique filename
        original_name = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4()}_{original_name}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_name)

        # Save file
        file.save(file_path)
        logger.info(f"Saved PDF to: {file_path}")

        return file_path

    except Exception as e:
        logger.error(f"Failed to save PDF: {e}")
        return None


def is_valid_pdf(file_path: str) -> bool:
    """Check if file is a valid PDF.

    Args:
        file_path: Path to the PDF file

    Returns:
        True if valid PDF with at least one page, False otherwise
    """
    try:
        doc = fitz.open(file_path)
        page_count = doc.page_count
        doc.close()
        return page_count > 0
    except Exception:
        return False


def has_extractable_text(file_path: str) -> bool:
    """Check if PDF has extractable text (not just images).

    Args:
        file_path: Path to the PDF file

    Returns:
        True if PDF has substantial extractable text
    """
    text = extract_text_from_pdf(file_path)
    # Minimum character threshold
    return len(text.strip()) > 50


def process_pdf_file(file) -> dict:
    """Process uploaded PDF file: save and extract text.

    Args:
        file: Flask FileStorage object

    Returns:
        Dict with file_path, text, and status
    """
    result = {
        "file_path": None,
        "text": "",
        "status": "failed",
        "error": None,
        "original_name": file.filename
    }

    # Save file
    file_path = save_uploaded_pdf(file)
    if not file_path:
        result["error"] = "Failed to save file"
        return result

    result["file_path"] = file_path

    # Validate PDF
    if not is_valid_pdf(file_path):
        result["error"] = "Invalid or corrupted PDF"
        logger.error(f"Invalid PDF: {file.filename}")
        return result

    # Extract text
    text = extract_text_from_pdf(file_path)
    result["text"] = text

    if not text.strip():
        result["status"] = "warning"
        result["error"] = "No text extracted (possibly scanned image)"
        logger.warning(f"No text in PDF: {file.filename}")
    else:
        result["status"] = "success"
        logger.info(f"Extracted {len(text)} chars from {file.filename}")

    return result
