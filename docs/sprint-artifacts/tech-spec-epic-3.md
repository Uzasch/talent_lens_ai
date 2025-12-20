# Epic Technical Specification: Phase 1 - Data Extraction

Date: 2025-12-20
Author: Uzasch
Epic ID: 3
Status: Draft

---

## Overview

Epic 3 implements Phase 1 of the two-phase analysis architecture - extracting structured data from uploaded PDF resumes. This is the critical data preparation layer that feeds into the comparative ranking system in Epic 4.

The extraction pipeline uses a hybrid approach: local processing (PyMuPDF, regex, spaCy) handles basic extraction to minimize API costs, while Gemini AI extracts complex structured data that requires semantic understanding.

## Objectives and Scope

### In Scope

- PDF text extraction using PyMuPDF (fitz)
- Local extraction of email, phone, name using regex + spaCy NER
- Gemini API integration for structured data extraction (skills, experience, education, projects, positions)
- Candidate storage in SQLite database
- Duplicate detection by email address
- Error handling for corrupted/unparseable PDFs
- PDF file storage in uploads/ directory

### Out of Scope

- Comparative ranking (Epic 4)
- Multi-candidate Gemini prompts (Epic 4)
- Score generation (Epic 4)
- UI for viewing extracted data (Epic 5)
- Batch optimization strategies

## System Architecture Alignment

This epic implements Phase 1 of the Two-Phase Analysis Architecture:

```
PDF File
    │
    ▼
PyMuPDF ──► Raw Text
    │
    ▼
Local Extraction (Regex/spaCy)
    ├── Email (regex)
    ├── Phone (regex)
    └── Name (spaCy NER)
    │
    ▼
Gemini API (Individual)
    ├── Extract skills
    ├── Parse experience details
    ├── Parse education details
    └── Extract project details
    │
    ▼
Store in SQLite (candidates table)
```

| Architecture Component | Story | Notes |
|------------------------|-------|-------|
| PDF Parser Service | 3.1 | PyMuPDF (fitz) extraction |
| Local Extractor Service | 3.2 | Regex + spaCy pipeline |
| Gemini Service | 3.3 | Structured JSON extraction |
| Candidate Storage | 3.4 | SQLite with duplicate detection |

**Constraints from Architecture:**
- Local extraction BEFORE Gemini API (cost optimization)
- Gemini only for intelligence-required tasks
- Candidates linked to role_id and session_id
- Duplicate detection by email within role pool

## Detailed Design

### Services and Modules

| Module | Location | Responsibility | Dependencies |
|--------|----------|----------------|--------------|
| **pdf_parser.py** | backend/services/ | Extract text from PDF files | PyMuPDF (fitz) |
| **local_extractor.py** | backend/services/ | Extract name, email, phone locally | spaCy, regex |
| **gemini_service.py** | backend/services/ | Extract structured data via Gemini | google-generativeai |
| **models.py** | backend/ | Candidate CRUD operations | sqlite3 |

### Data Models and Contracts

**Candidate Table Schema (from Story 1.3):**
```sql
CREATE TABLE candidates (
    id TEXT PRIMARY KEY,
    role_id TEXT NOT NULL,
    session_id TEXT NOT NULL,

    -- Basic info (extracted locally)
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    resume_text TEXT,

    -- Extracted data (from Gemini Phase 1)
    skills TEXT,           -- JSON array
    experience_years REAL,
    experience_details TEXT,  -- JSON array
    education TEXT,        -- JSON array
    projects TEXT,         -- JSON array
    positions TEXT,        -- JSON array

    -- Scores (populated in Epic 4)
    rank INTEGER,
    match_score INTEGER,
    education_score INTEGER,
    experience_score INTEGER,
    projects_score INTEGER,
    positions_score INTEGER,
    skills_score INTEGER,

    -- Explanations (populated in Epic 4)
    summary TEXT,
    why_selected TEXT,
    compared_to_pool TEXT,

    -- Metadata
    status TEXT DEFAULT 'active',
    pdf_path TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_ranked_at TIMESTAMP,

    FOREIGN KEY (role_id) REFERENCES roles(id),
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);
```

**Local Extraction Output:**
```python
{
    "name": "Sara Ahmed",
    "email": "sara.ahmed@email.com",
    "phone": "+92-300-1234567"
}
```

**Gemini Extraction Output:**
```python
{
    "skills": ["Python", "Django", "FastAPI", "PostgreSQL", "AWS"],
    "experience_years": 4.5,
    "experience_details": [
        {
            "role": "Senior Developer",
            "company": "TechCorp",
            "duration": "2 years",
            "highlights": ["Led team of 5", "Built microservices API"]
        }
    ],
    "education": [
        {
            "degree": "B.Tech Computer Science",
            "institution": "IIT Delhi",
            "year": 2018
        }
    ],
    "projects": [
        {
            "name": "E-commerce Platform",
            "description": "Full-stack e-commerce with 50K users",
            "technologies": ["Python", "React", "PostgreSQL"],
            "impact": "Increased sales 30%"
        }
    ],
    "positions": [
        {"title": "Junior Developer", "year": 2018},
        {"title": "Mid Developer", "year": 2020},
        {"title": "Senior Developer", "year": 2022}
    ]
}
```

### APIs and Interfaces

**Internal Service Interfaces:**

```python
# pdf_parser.py
def extract_text_from_pdf(file_path: str) -> str:
    """Extract text content from PDF file."""
    pass

# local_extractor.py
def extract_basic_info(text: str) -> dict:
    """Extract name, email, phone from resume text."""
    pass

def extract_email(text: str) -> str | None:
    """Extract email using regex."""
    pass

def extract_phone(text: str) -> str | None:
    """Extract phone using regex."""
    pass

def extract_name(text: str) -> str | None:
    """Extract name using spaCy NER."""
    pass

# gemini_service.py
def extract_structured_data(resume_text: str) -> dict:
    """Extract structured data from resume using Gemini."""
    pass

# models.py
def create_candidate(role_id: str, session_id: str, data: dict) -> dict:
    """Create new candidate record."""
    pass

def get_candidate_by_email(role_id: str, email: str) -> dict | None:
    """Find existing candidate by email in role pool."""
    pass

def supersede_candidate(candidate_id: str) -> None:
    """Mark candidate as superseded (replaced by newer resume)."""
    pass
```

### Workflows and Sequencing

**Story Dependency Flow:**

```
Story 3.1 (PDF Parser) ──────►┐
                              │
Story 3.2 (Local Extractor) ──┼──► Story 3.4 (Candidate Storage)
                              │
Story 3.3 (Gemini Service) ───┘
```

**Development Sequence:**
1. Story 3.1 (PDF Parser) - no dependencies
2. Story 3.2 (Local Extractor) - no dependencies, can parallel with 3.1
3. Story 3.3 (Gemini Service) - no dependencies, can parallel with 3.1-3.2
4. Story 3.4 (Candidate Storage) - depends on 3.1, 3.2, 3.3

**Extraction Pipeline Flow:**

```
1. Save uploaded PDF to uploads/
        │
        ▼
2. PyMuPDF extracts raw text
        │
        ├── If extraction fails → Log error, skip file
        │
        ▼
3. Local extraction (parallel):
   ├── extract_email(text)
   ├── extract_phone(text)
   └── extract_name(text)
        │
        ▼
4. Gemini extraction:
   └── extract_structured_data(text)
        │
        ├── If Gemini fails → Log error, store with partial data
        │
        ▼
5. Duplicate check:
   └── get_candidate_by_email(role_id, email)
        │
        ├── If exists → supersede_candidate(old_id)
        │
        ▼
6. Store candidate in database
```

## Non-Functional Requirements

### Performance

| Metric | Target | Source |
|--------|--------|--------|
| PDF text extraction | < 500ms per file | Best practice |
| Local extraction | < 100ms per resume | Best practice |
| Gemini API call | < 5 seconds per resume | API typical |
| Total per resume | < 6 seconds | Sum of above |
| Batch of 10 resumes | < 15 seconds (parallel) | PRD target |

**Implementation Notes:**
- PDF extraction is CPU-bound, parallelize with ThreadPoolExecutor
- Gemini calls can be parallelized (API allows concurrent requests)
- Local extraction is fast, run sequentially

### Security

| Requirement | Implementation | Source |
|-------------|----------------|--------|
| API key protection | Load from .env, never log | Architecture |
| File validation | Only process .pdf files | PRD FR8 |
| SQL injection | Parameterized queries | Architecture |
| PII handling | Email/phone stored encrypted? | Future consideration |

**Gemini API Key Usage:**
```python
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
```

### Reliability/Availability

| Scenario | Handling |
|----------|----------|
| PDF corrupted/unreadable | Log error, skip file, notify user |
| PDF is scanned image (no text) | Detect empty text, skip, notify |
| Gemini API rate limited | Implement retry with exponential backoff |
| Gemini API returns invalid JSON | Log error, store partial data |
| Duplicate email in pool | Supersede old candidate, keep new |

### Observability

| Signal | Implementation |
|--------|----------------|
| Extraction progress | Log each file processed |
| Gemini API calls | Log request/response times |
| Extraction failures | Log with file name and error |
| Duplicate detections | Log when superseding |

```python
import logging
logger = logging.getLogger(__name__)

logger.info(f"Phase 1: Extracting {filename}")
logger.info(f"Gemini extraction completed in {elapsed}s")
logger.error(f"Failed to extract text from {filename}: {error}")
logger.info(f"Duplicate detected: superseding {old_id} with {new_id}")
```

## Dependencies and Integrations

### Backend Dependencies (already installed in Epic 1)

| Package | Version | Purpose |
|---------|---------|---------|
| PyMuPDF (fitz) | 1.24.x | PDF text extraction |
| spaCy | 3.x | Named Entity Recognition |
| en_core_web_sm | 3.x | spaCy English model |
| google-generativeai | latest | Gemini API SDK |
| python-dotenv | latest | Environment variables |

### External Services

| Service | Purpose | Rate Limits |
|---------|---------|-------------|
| Gemini API | Structured data extraction | 60 requests/minute (free tier) |

### Database Tables

| Table | Used For | Created In |
|-------|----------|------------|
| roles | Role lookup for candidate association | Epic 1, Story 1.3 |
| sessions | Session creation for batch tracking | Epic 1, Story 1.3 |
| candidates | Store extracted candidate data | Epic 1, Story 1.3 |

## Acceptance Criteria (Authoritative)

### Story 3.1: PDF Text Extraction Service
1. **AC3.1.1:** PDF file uploaded to backend is saved to uploads/ directory
2. **AC3.1.2:** Text content is extracted using PyMuPDF (fitz)
3. **AC3.1.3:** Extracted text is returned as a string
4. **AC3.1.4:** If extraction fails, error is logged and file is skipped
5. **AC3.1.5:** Function handles edge cases: scanned PDFs (empty text), corrupted files

### Story 3.2: Local Data Extraction Service
1. **AC3.2.1:** Email is extracted using regex pattern `[\w.-]+@[\w.-]+\.\w+`
2. **AC3.2.2:** Phone is extracted using regex (with/without country code)
3. **AC3.2.3:** Candidate name is extracted using spaCy NER (PERSON entity)
4. **AC3.2.4:** Results returned as structured dict: `{name, email, phone}`
5. **AC3.2.5:** Missing fields return None (not errors)

### Story 3.3: Gemini Structured Extraction
1. **AC3.3.1:** Resume text is sent to Gemini with extraction prompt
2. **AC3.3.2:** Gemini returns structured JSON with: skills, experience_years, experience_details, education, projects, positions
3. **AC3.3.3:** Response is parsed and validated for required fields
4. **AC3.3.4:** API errors are caught and logged
5. **AC3.3.5:** Uses gemini-1.5-flash model for cost efficiency

### Story 3.4: Candidate Storage and Duplicate Detection
1. **AC3.4.1:** Candidate record is created with role_id and session_id
2. **AC3.4.2:** All extracted fields (local + Gemini) are stored
3. **AC3.4.3:** Before insert, check if email exists in role's pool
4. **AC3.4.4:** If duplicate found, mark old candidate as 'superseded'
5. **AC3.4.5:** New candidate is stored with status='active'
6. **AC3.4.6:** PDF path is stored for reference

## Traceability Mapping

| AC | FR | Spec Section | Component | Test Approach |
|----|-------|--------------|-----------|---------------|
| AC3.1.1-5 | FR12 | Detailed Design | pdf_parser.py | Unit: mock PDF files |
| AC3.2.1-5 | FR13-FR15 | Detailed Design | local_extractor.py | Unit: sample texts |
| AC3.3.1-5 | FR16 | Detailed Design | gemini_service.py | Integration: mock API |
| AC3.4.1-6 | FR17-FR18 | Data Models | models.py | Integration: SQLite |

## Risks, Assumptions, Open Questions

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Gemini API rate limits hit | Medium | High | Implement rate limiting, queue |
| Poor quality PDF extraction | Medium | Medium | Log and allow manual review |
| spaCy name extraction inaccurate | Medium | Low | Fall back to first line of resume |
| Gemini returns invalid JSON | Low | Medium | Retry once, then store partial |

### Assumptions

1. All PDFs are text-based (not scanned images)
2. Resumes are in English
3. Gemini API remains available and within free tier limits
4. Email is unique identifier for duplicate detection
5. 10-15 resumes per batch is typical use case

### Open Questions

1. **Q1:** Should we extract PDF metadata (author, creation date)?
   - **Recommendation:** Not for MVP, low value

2. **Q2:** How to handle resumes with no extractable email?
   - **Recommendation:** Store anyway, use name + session as identifier

3. **Q3:** Gemini token limits for very long resumes?
   - **Recommendation:** Truncate to first 10,000 characters

## Test Strategy Summary

### Unit Tests (pytest)

**pdf_parser.py:**
- Test extraction from valid PDF
- Test handling of corrupted PDF
- Test handling of image-only PDF (empty text)

**local_extractor.py:**
- Test email regex with various formats
- Test phone regex with international formats
- Test spaCy NER name extraction
- Test handling of missing fields

**gemini_service.py:**
- Mock Gemini API responses
- Test JSON parsing
- Test error handling for API failures

### Integration Tests (pytest)

**models.py:**
- Test candidate creation
- Test duplicate detection by email
- Test superseding logic
- Test data integrity (foreign keys)

### Full Pipeline Test

- Upload PDF → Extract text → Local extraction → Gemini → Store
- Verify all fields populated correctly
- Verify duplicate handling works

**Test Priority:**
1. PDF extraction (foundation)
2. Gemini integration (critical path)
3. Duplicate detection (data integrity)
4. Local extraction (can have fallbacks)

## Implementation Code Examples

### PDF Parser (services/pdf_parser.py)

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

### Local Extractor (services/local_extractor.py)

```python
import re
import spacy
import logging

logger = logging.getLogger(__name__)

# Load spaCy model once at module level
nlp = spacy.load("en_core_web_sm")

def extract_email(text: str) -> str | None:
    """Extract email using regex."""
    pattern = r'[\w.-]+@[\w.-]+\.\w+'
    match = re.search(pattern, text)
    return match.group(0) if match else None

def extract_phone(text: str) -> str | None:
    """Extract phone number using regex."""
    # Patterns for various phone formats
    patterns = [
        r'\+?[\d]{1,3}[-.\s]?[\d]{3}[-.\s]?[\d]{3}[-.\s]?[\d]{4}',  # +1-123-456-7890
        r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # (123) 456-7890
        r'\d{10,}',  # Simple 10+ digit number
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return None

def extract_name(text: str) -> str | None:
    """Extract candidate name using spaCy NER."""
    try:
        # Process only first 1000 chars for speed (name usually at top)
        doc = nlp(text[:1000])

        # Find PERSON entities
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                return ent.text

        # Fallback: first non-empty line might be name
        lines = text.strip().split('\n')
        for line in lines[:3]:
            line = line.strip()
            if line and len(line) < 50:  # Reasonable name length
                return line

        return None

    except Exception as e:
        logger.error(f"spaCy name extraction failed: {e}")
        return None

def extract_basic_info(text: str) -> dict:
    """Extract name, email, phone from resume text."""
    return {
        "name": extract_name(text) or "Unknown",
        "email": extract_email(text),
        "phone": extract_phone(text)
    }
```

### Gemini Service (services/gemini_service.py)

```python
import os
import json
import logging
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

EXTRACTION_PROMPT = """Extract structured data from this resume text.

Resume Text:
{resume_text}

Return ONLY valid JSON with this structure (no markdown, no explanation):
{{
  "skills": ["skill1", "skill2", ...],
  "experience_years": 4.5,
  "experience_details": [
    {{
      "role": "Job Title",
      "company": "Company Name",
      "duration": "2 years",
      "highlights": ["Achievement 1", "Achievement 2"]
    }}
  ],
  "education": [
    {{
      "degree": "Degree Name",
      "institution": "University Name",
      "year": 2020
    }}
  ],
  "projects": [
    {{
      "name": "Project Name",
      "description": "Brief description",
      "technologies": ["tech1", "tech2"],
      "impact": "Measurable impact if mentioned"
    }}
  ],
  "positions": [
    {{"title": "Position Title", "year": 2018}}
  ]
}}

Rules:
- Extract all relevant information from the resume
- experience_years should be total years of work experience
- positions should show career progression chronologically
- If information is not found, use empty arrays or null
- Return ONLY the JSON, no other text
"""

def extract_structured_data(resume_text: str) -> dict:
    """Extract structured data from resume using Gemini API.

    Args:
        resume_text: Raw text content of resume

    Returns:
        Dict with extracted structured data
    """
    try:
        # Truncate very long resumes to avoid token limits
        if len(resume_text) > 10000:
            resume_text = resume_text[:10000]
            logger.info("Resume text truncated to 10000 chars")

        model = genai.GenerativeModel('gemini-1.5-flash')

        prompt = EXTRACTION_PROMPT.format(resume_text=resume_text)
        response = model.generate_content(prompt)

        # Parse JSON from response
        response_text = response.text.strip()

        # Remove markdown code blocks if present
        if response_text.startswith('```'):
            response_text = response_text.split('\n', 1)[1]
        if response_text.endswith('```'):
            response_text = response_text.rsplit('\n', 1)[0]
        response_text = response_text.strip()

        data = json.loads(response_text)

        # Validate required fields exist
        default_structure = {
            "skills": [],
            "experience_years": 0,
            "experience_details": [],
            "education": [],
            "projects": [],
            "positions": []
        }

        # Merge with defaults for missing fields
        for key in default_structure:
            if key not in data:
                data[key] = default_structure[key]

        logger.info("Gemini extraction successful")
        return data

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini response as JSON: {e}")
        return {
            "skills": [],
            "experience_years": 0,
            "experience_details": [],
            "education": [],
            "projects": [],
            "positions": [],
            "extraction_error": str(e)
        }

    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return {
            "skills": [],
            "experience_years": 0,
            "experience_details": [],
            "education": [],
            "projects": [],
            "positions": [],
            "extraction_error": str(e)
        }
```

### Candidate Storage (models.py additions)

```python
import uuid
import json
from datetime import datetime

def create_candidate(role_id: str, session_id: str, local_data: dict,
                     gemini_data: dict, pdf_path: str = None) -> dict:
    """Create new candidate record with extracted data."""
    conn = get_db_connection()
    cursor = conn.cursor()

    candidate_id = str(uuid.uuid4())

    cursor.execute('''
        INSERT INTO candidates (
            id, role_id, session_id, name, email, phone,
            skills, experience_years, experience_details,
            education, projects, positions,
            status, pdf_path, uploaded_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        candidate_id,
        role_id,
        session_id,
        local_data.get('name', 'Unknown'),
        local_data.get('email'),
        local_data.get('phone'),
        json.dumps(gemini_data.get('skills', [])),
        gemini_data.get('experience_years', 0),
        json.dumps(gemini_data.get('experience_details', [])),
        json.dumps(gemini_data.get('education', [])),
        json.dumps(gemini_data.get('projects', [])),
        json.dumps(gemini_data.get('positions', [])),
        'active',
        pdf_path,
        datetime.utcnow().isoformat()
    ))

    conn.commit()
    conn.close()

    return {"id": candidate_id, "status": "created"}

def get_candidate_by_email(role_id: str, email: str) -> dict | None:
    """Find existing active candidate by email in role pool."""
    if not email:
        return None

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM candidates
        WHERE role_id = ? AND email = ? AND status = 'active'
    ''', (role_id, email))

    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None

def supersede_candidate(candidate_id: str) -> None:
    """Mark candidate as superseded (replaced by newer resume)."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE candidates SET status = 'superseded'
        WHERE id = ?
    ''', (candidate_id,))

    conn.commit()
    conn.close()

def store_resume_text(candidate_id: str, resume_text: str) -> None:
    """Store extracted resume text for reference."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE candidates SET resume_text = ?
        WHERE id = ?
    ''', (resume_text, candidate_id))

    conn.commit()
    conn.close()
```

---

_Generated by BMAD BMM Epic Tech Context Workflow_
_Epic: 3 - Phase 1: Data Extraction_
_Date: 2025-12-20_
