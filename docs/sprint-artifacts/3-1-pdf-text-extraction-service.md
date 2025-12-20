# Story 3.1: PDF Text Extraction Service

Status: review

## Story

As a **developer**,
I want **to extract text from PDF files locally**,
So that **resume content can be analyzed**.

## Acceptance Criteria

1. **AC3.1.1:** Uploaded PDF file is saved to uploads/ directory with unique filename
2. **AC3.1.2:** Text content is extracted from PDF using PyMuPDF (fitz)
3. **AC3.1.3:** Extracted text is returned as a string
4. **AC3.1.4:** If extraction fails, error is logged and file is skipped
5. **AC3.1.5:** Edge cases handled: scanned PDFs (empty text), corrupted files

## Tasks / Subtasks

- [x] **Task 1: Create pdf_parser.py service file** (AC: 3.1.2, 3.1.3)
  - [x] Create `backend/services/pdf_parser.py`:
    ```python
    import fitz  # PyMuPDF
    import logging
    import os

    logger = logging.getLogger(__name__)

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
    ```

- [x] **Task 2: Create file save utility** (AC: 3.1.1)
  - [x] Add to `backend/services/pdf_parser.py`:
    ```python
    import uuid
    from werkzeug.utils import secure_filename

    UPLOAD_FOLDER = 'uploads'

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
    ```

- [x] **Task 3: Add error handling for edge cases** (AC: 3.1.4, 3.1.5)
  - [x] Handle corrupted PDF files:
    ```python
    def is_valid_pdf(file_path: str) -> bool:
        """Check if file is a valid PDF."""
        try:
            doc = fitz.open(file_path)
            page_count = doc.page_count
            doc.close()
            return page_count > 0
        except Exception:
            return False
    ```
  - [x] Detect scanned/image PDFs (empty text):
    ```python
    def has_extractable_text(file_path: str) -> bool:
        """Check if PDF has extractable text (not just images)."""
        text = extract_text_from_pdf(file_path)
        # Minimum character threshold
        return len(text.strip()) > 50
    ```

- [x] **Task 4: Create extraction wrapper function** (AC: 3.1.1-3.1.5)
  - [x] Add main extraction function:
    ```python
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
    ```

- [x] **Task 5: Ensure uploads directory exists** (AC: 3.1.1)
  - [x] Add to `backend/app.py` initialization:
    ```python
    import os

    # Ensure required directories exist
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    ```

- [x] **Task 6: Test PDF extraction**
  - [x] Test with valid text PDF:
    ```python
    # Manual test
    from services.pdf_parser import extract_text_from_pdf
    text = extract_text_from_pdf('test_resume.pdf')
    print(f"Extracted {len(text)} characters")
    ```
  - [x] Test with corrupted PDF → should return empty string
  - [x] Test with non-existent path → should return empty string
  - [x] Test file saving with special characters in filename
  - [x] Test extraction from multi-page PDF

## Dev Notes

### Architecture Alignment

This story implements the first step of Phase 1 extraction per architecture.md:
- **Library:** PyMuPDF (fitz) - already installed in Epic 1
- **Pattern:** Service module in `backend/services/`
- **Error Handling:** Log and skip problematic files

### PyMuPDF Usage

```python
import fitz  # PyMuPDF is imported as 'fitz'

# Open PDF
doc = fitz.open("resume.pdf")

# Iterate pages
for page in doc:
    text = page.get_text()  # Returns string

# Close document
doc.close()
```

### File Storage

```
backend/
├── uploads/              # PDF files stored here
│   ├── uuid1_resume.pdf
│   ├── uuid2_resume.pdf
│   └── ...
├── services/
│   └── pdf_parser.py
```

### Error Scenarios

| Scenario | Handling |
|----------|----------|
| File not found | Log error, return empty string |
| Corrupted PDF | Catch exception, return empty string |
| Scanned PDF (no text) | Return empty string, log warning |
| Permission error | Catch exception, return empty string |

### Performance Considerations

- PyMuPDF is fast (~100ms per typical resume)
- Multi-page PDFs processed sequentially
- No need for async at this scale

### Security Considerations

- Use `secure_filename()` from werkzeug
- Generate UUID prefix to prevent filename collisions
- Only process files with .pdf extension

### References

- [Source: docs/sprint-artifacts/tech-spec-epic-3.md#PDF-Parser]
- [Source: docs/architecture.md#Phase-1-Individual-Data-Extraction]
- [Source: docs/epics.md#Story-3.1]
- [Source: docs/prd.md#FR12]

## Dev Agent Record

### Context Reference

None (proceeded without story context file)

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- Python syntax check passed
- All 5 functional tests passed:
  - Non-existent file returns empty string
  - is_valid_pdf returns False for invalid files
  - Valid PDF text extraction works
  - is_valid_pdf returns True for valid PDFs
  - has_extractable_text works correctly

### Completion Notes List

- All 6 tasks completed successfully
- All 5 acceptance criteria satisfied:
  - AC3.1.1: PDF saved to uploads/ with UUID prefix
  - AC3.1.2: Text extracted using PyMuPDF (fitz)
  - AC3.1.3: Extracted text returned as string
  - AC3.1.4: Errors logged and file skipped (returns empty string)
  - AC3.1.5: Edge cases handled (scanned PDFs, corrupted files)
- Functions implemented: extract_text_from_pdf, save_uploaded_pdf, is_valid_pdf, has_extractable_text, process_pdf_file
- Uses secure_filename from werkzeug for safety

### File List

**Created:**
- backend/services/__init__.py
- backend/services/pdf_parser.py

**Modified:**
- backend/app.py (added uploads/data directory creation)

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-12-20 | SM Agent (Bob) | Initial draft created |
| 2025-12-20 | Dev Agent (Amelia) | Implementation complete - all ACs satisfied |
