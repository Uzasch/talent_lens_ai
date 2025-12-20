# Story 3.2: Local Data Extraction Service

Status: review

## Story

As a **developer**,
I want **to extract basic info locally without API**,
So that **API costs are reduced**.

## Acceptance Criteria

1. **AC3.2.1:** Email is extracted using regex pattern `[\w.-]+@[\w.-]+\.\w+`
2. **AC3.2.2:** Phone is extracted using regex pattern (with/without country code)
3. **AC3.2.3:** Candidate name is extracted using spaCy NER (PERSON entity)
4. **AC3.2.4:** Results returned as structured dict: `{name, email, phone}`
5. **AC3.2.5:** Missing fields return None (not errors)

## Tasks / Subtasks

- [x] **Task 1: Create local_extractor.py service file** (AC: 3.2.1-3.2.5)
  - [x] Create `backend/services/local_extractor.py`:
    ```python
    import re
    import spacy
    import logging

    logger = logging.getLogger(__name__)

    # Load spaCy model once at module level
    nlp = None

    def get_nlp():
        """Lazy load spaCy model."""
        global nlp
        if nlp is None:
            nlp = spacy.load("en_core_web_sm")
        return nlp
    ```

- [x] **Task 2: Implement email extraction** (AC: 3.2.1)
  - [x] Add email regex function:
    ```python
    def extract_email(text: str) -> str | None:
        """Extract email using regex.

        Args:
            text: Resume text content

        Returns:
            Email address or None if not found
        """
        pattern = r'[\w.-]+@[\w.-]+\.\w+'
        match = re.search(pattern, text)
        return match.group(0).lower() if match else None
    ```

- [x] **Task 3: Implement phone extraction** (AC: 3.2.2)
  - [x] Add phone regex function:
    ```python
    def extract_phone(text: str) -> str | None:
        """Extract phone number using regex.

        Handles formats:
        - +1-123-456-7890
        - (123) 456-7890
        - 123.456.7890
        - +92 300 1234567
        - 10+ digit numbers

        Args:
            text: Resume text content

        Returns:
            Phone number or None if not found
        """
        patterns = [
            r'\+?[\d]{1,3}[-.\s]?[\d]{3}[-.\s]?[\d]{3}[-.\s]?[\d]{4}',
            r'\+?[\d]{1,3}[-.\s]?[\d]{3}[-.\s]?[\d]{7}',
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\d{10,13}',
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                # Clean up the phone number
                phone = match.group(0).strip()
                return phone

        return None
    ```

- [x] **Task 4: Implement name extraction with spaCy** (AC: 3.2.3)
  - [x] Add name extraction function:
    ```python
    def extract_name(text: str) -> str | None:
        """Extract candidate name using spaCy NER.

        Strategy:
        1. Look for PERSON entities in first 1000 chars
        2. Prefer entities at the start of the document
        3. Fallback to first non-empty line if no entity found

        Args:
            text: Resume text content

        Returns:
            Candidate name or None if not found
        """
        try:
            nlp = get_nlp()

            # Process only first 1000 chars for speed (name usually at top)
            doc = nlp(text[:1000])

            # Find PERSON entities
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    name = ent.text.strip()
                    # Basic validation: should be 2+ words, reasonable length
                    if len(name.split()) >= 2 and len(name) < 50:
                        return name

            # Fallback: first non-empty line might be name
            lines = text.strip().split('\n')
            for line in lines[:5]:
                line = line.strip()
                # Heuristic: name is usually short, no special chars
                if line and len(line) < 40 and not any(c in line for c in ['@', '|', '•', ':']):
                    # Check if it looks like a name (mostly letters and spaces)
                    if re.match(r'^[A-Za-z\s.-]+$', line):
                        return line

            return None

        except Exception as e:
            logger.error(f"spaCy name extraction failed: {e}")
            return None
    ```

- [x] **Task 5: Create main extraction function** (AC: 3.2.4, 3.2.5)
  - [x] Add wrapper function:
    ```python
    def extract_basic_info(text: str) -> dict:
        """Extract name, email, phone from resume text.

        Args:
            text: Resume text content

        Returns:
            Dict with name, email, phone (None for missing fields)
        """
        if not text or not text.strip():
            return {
                "name": None,
                "email": None,
                "phone": None
            }

        return {
            "name": extract_name(text),
            "email": extract_email(text),
            "phone": extract_phone(text)
        }
    ```

- [x] **Task 6: Add validation helpers**
  - [x] Add email validation:
    ```python
    def is_valid_email(email: str) -> bool:
        """Validate email format."""
        if not email:
            return False
        pattern = r'^[\w.-]+@[\w.-]+\.\w{2,}$'
        return bool(re.match(pattern, email))
    ```

- [x] **Task 7: Test local extraction**
  - [x] Test email extraction with various formats:
    ```python
    # Test cases
    assert extract_email("Contact: john@example.com") == "john@example.com"
    assert extract_email("Email: john.doe@company.co.uk") == "john.doe@company.co.uk"
    assert extract_email("No email here") is None
    ```
  - [x] Test phone extraction with various formats:
    ```python
    assert extract_phone("+1-555-123-4567") is not None
    assert extract_phone("(555) 123-4567") is not None
    assert extract_phone("+92 300 1234567") is not None
    ```
  - [x] Test name extraction with spaCy:
    ```python
    text = "John Smith\nSoftware Engineer\njohn@email.com"
    assert extract_name(text) == "John Smith"
    ```

## Dev Notes

### Architecture Alignment

This story implements local extraction per architecture.md:
- **Purpose:** Reduce Gemini API costs by extracting simple patterns locally
- **Library:** spaCy with en_core_web_sm model (installed in Epic 1)
- **Pattern:** Regex for structured patterns, NER for names

### Local vs API Extraction

| Field | Method | Why Local |
|-------|--------|-----------|
| Email | Regex | Simple pattern matching |
| Phone | Regex | Simple pattern matching |
| Name | spaCy NER | Pre-trained model, no API needed |

### Regex Patterns

**Email Pattern:** `[\w.-]+@[\w.-]+\.\w+`
- Matches: `john.doe@example.com`, `user-123@company.co.uk`
- Case insensitive matching recommended

**Phone Patterns:**
```
+1-123-456-7890    → International with dashes
(123) 456-7890     → US format with parentheses
123.456.7890       → Dots separator
+92 300 1234567    → Pakistani format
```

### spaCy NER

```python
import spacy
nlp = spacy.load("en_core_web_sm")

doc = nlp("John Smith is a software engineer")
for ent in doc.ents:
    print(ent.text, ent.label_)
# Output: John Smith PERSON
```

### Performance Notes

- spaCy model loads once at module level
- Process only first 1000 chars for name (speed optimization)
- Regex is extremely fast, no optimization needed

### Edge Cases

| Scenario | Handling |
|----------|----------|
| No email in resume | Return None |
| Multiple emails | Return first match |
| Non-standard phone format | Try multiple patterns |
| Name with titles (Dr., Mr.) | spaCy handles this |
| Empty text input | Return all None values |

### Dependencies

- `spacy` (installed in Epic 1)
- `en_core_web_sm` model (downloaded in Epic 1)
- Python `re` module (built-in)

### References

- [Source: docs/sprint-artifacts/tech-spec-epic-3.md#Local-Extractor]
- [Source: docs/architecture.md#Local-Processing]
- [Source: docs/epics.md#Story-3.2]
- [Source: docs/prd.md#FR13-FR15]

## Dev Agent Record

### Context Reference

None (proceeded without story context file)

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- Python syntax check passed
- All functional tests passed:
  - Email extraction: 4/4 test cases
  - Phone extraction: 5/5 test cases (various formats)
  - Name extraction: 3/3 test cases with spaCy NER
  - Full extraction: successfully extracted all fields
  - Empty input: returns all None values
  - Email validation: 4/4 test cases

### Completion Notes List

- All 7 tasks completed successfully
- All 5 acceptance criteria satisfied:
  - AC3.2.1: Email extracted using regex pattern
  - AC3.2.2: Phone extracted using multiple regex patterns
  - AC3.2.3: Name extracted using spaCy NER (PERSON entity)
  - AC3.2.4: Results returned as structured dict
  - AC3.2.5: Missing fields return None (not errors)
- spaCy model loaded lazily for performance
- Name extraction processes only first 1000 chars for speed
- Fallback to first line if spaCy NER doesn't find PERSON entity

### File List

**Created:**
- backend/services/local_extractor.py

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-12-20 | SM Agent (Bob) | Initial draft created |
| 2025-12-20 | Dev Agent (Amelia) | Implementation complete - all ACs satisfied |
