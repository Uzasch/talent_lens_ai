# Story 3.4: Candidate Storage and Duplicate Detection

Status: review

## Story

As a **system**,
I want **to store extracted candidates and detect duplicates**,
So that **the pool remains clean**.

## Acceptance Criteria

1. **AC3.4.1:** Candidate record is created with role_id and session_id
2. **AC3.4.2:** All extracted fields (local + Gemini) are stored in database
3. **AC3.4.3:** Before insert, check if email exists in role's pool
4. **AC3.4.4:** If duplicate found, mark old candidate as 'superseded'
5. **AC3.4.5:** New candidate is stored with status='active'
6. **AC3.4.6:** PDF path is stored for reference

## Tasks / Subtasks

- [x] **Task 1: Add candidate CRUD functions to models.py** (AC: 3.4.1, 3.4.2, 3.4.5)
  - [ ] Add create_candidate function:
    ```python
    import uuid
    import json
    from datetime import datetime

    def create_candidate(role_id: str, session_id: str, local_data: dict,
                         gemini_data: dict, resume_text: str = None,
                         pdf_path: str = None) -> dict:
        """Create new candidate record with extracted data.

        Args:
            role_id: Role UUID
            session_id: Session UUID
            local_data: Dict with name, email, phone
            gemini_data: Dict with skills, experience, etc.
            resume_text: Raw text from PDF
            pdf_path: Path to stored PDF file

        Returns:
            Dict with candidate id and status
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        candidate_id = str(uuid.uuid4())

        cursor.execute('''
            INSERT INTO candidates (
                id, role_id, session_id,
                name, email, phone, resume_text,
                skills, experience_years, experience_details,
                education, projects, positions,
                status, pdf_path, uploaded_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            candidate_id,
            role_id,
            session_id,
            local_data.get('name') or 'Unknown',
            local_data.get('email'),
            local_data.get('phone'),
            resume_text,
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

        return {
            "id": candidate_id,
            "name": local_data.get('name'),
            "email": local_data.get('email'),
            "status": "created"
        }
    ```

- [x] **Task 2: Add duplicate detection function** (AC: 3.4.3)
  - [ ] Add get_candidate_by_email function:
    ```python
    def get_candidate_by_email(role_id: str, email: str) -> dict | None:
        """Find existing active candidate by email in role pool.

        Args:
            role_id: Role UUID to search within
            email: Email address to search for

        Returns:
            Candidate dict or None if not found
        """
        if not email:
            return None

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, name, email, status, uploaded_at
            FROM candidates
            WHERE role_id = ? AND email = ? AND status = 'active'
        ''', (role_id, email.lower()))

        row = cursor.fetchone()
        conn.close()

        return dict(row) if row else None
    ```

- [x] **Task 3: Add supersede function** (AC: 3.4.4)
  - [ ] Add supersede_candidate function:
    ```python
    def supersede_candidate(candidate_id: str) -> bool:
        """Mark candidate as superseded (replaced by newer resume).

        Args:
            candidate_id: UUID of candidate to supersede

        Returns:
            True if successful
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE candidates
            SET status = 'superseded'
            WHERE id = ?
        ''', (candidate_id,))

        affected = cursor.rowcount
        conn.commit()
        conn.close()

        return affected > 0
    ```

- [x] **Task 4: Create candidate storage wrapper** (AC: 3.4.1-3.4.6)
  - [ ] Add store_candidate_with_duplicate_check function:
    ```python
    def store_candidate_with_duplicate_check(
        role_id: str,
        session_id: str,
        local_data: dict,
        gemini_data: dict,
        resume_text: str = None,
        pdf_path: str = None
    ) -> dict:
        """Store candidate with duplicate detection.

        If email already exists in pool, supersedes old candidate.

        Args:
            role_id: Role UUID
            session_id: Session UUID
            local_data: Dict with name, email, phone
            gemini_data: Dict with structured extraction
            resume_text: Raw resume text
            pdf_path: Path to PDF file

        Returns:
            Dict with candidate info and duplicate status
        """
        import logging
        logger = logging.getLogger(__name__)

        email = local_data.get('email')
        result = {
            "candidate_id": None,
            "is_duplicate": False,
            "superseded_id": None,
            "status": "failed"
        }

        # Check for existing candidate with same email
        if email:
            existing = get_candidate_by_email(role_id, email)
            if existing:
                result["is_duplicate"] = True
                result["superseded_id"] = existing['id']
                supersede_candidate(existing['id'])
                logger.info(f"Superseding existing candidate {existing['id']} with email {email}")

        # Create new candidate
        candidate = create_candidate(
            role_id=role_id,
            session_id=session_id,
            local_data=local_data,
            gemini_data=gemini_data,
            resume_text=resume_text,
            pdf_path=pdf_path
        )

        result["candidate_id"] = candidate['id']
        result["name"] = candidate.get('name')
        result["email"] = candidate.get('email')
        result["status"] = "created"

        return result
    ```

- [x] **Task 5: Add helper functions for candidate retrieval**
  - [ ] Add get_candidate_by_id:
    ```python
    def get_candidate_by_id(candidate_id: str) -> dict | None:
        """Get full candidate record by ID."""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM candidates WHERE id = ?', (candidate_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        candidate = dict(row)

        # Parse JSON fields
        for field in ['skills', 'experience_details', 'education', 'projects', 'positions', 'summary']:
            if candidate.get(field):
                try:
                    candidate[field] = json.loads(candidate[field])
                except json.JSONDecodeError:
                    pass

        return candidate
    ```
  - [ ] Add get_candidates_by_session:
    ```python
    def get_candidates_by_session(session_id: str) -> list:
        """Get all candidates added in a session."""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, name, email, status, uploaded_at
            FROM candidates
            WHERE session_id = ?
            ORDER BY uploaded_at DESC
        ''', (session_id,))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]
    ```

- [x] **Task 6: Add session creation helper**
  - [ ] Add create_session function:
    ```python
    def create_session(role_id: str, job_description: str) -> dict:
        """Create new analysis session.

        Args:
            role_id: Role UUID
            job_description: JD text

        Returns:
            Dict with session id
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        session_id = str(uuid.uuid4())

        cursor.execute('''
            INSERT INTO sessions (id, role_id, job_description, candidates_added, pool_size_at_analysis)
            VALUES (?, ?, ?, 0, 0)
        ''', (session_id, role_id, job_description))

        conn.commit()
        conn.close()

        return {"id": session_id}
    ```
  - [ ] Add update_session_counts function:
    ```python
    def update_session_counts(session_id: str, candidates_added: int, pool_size: int) -> None:
        """Update session with final counts after processing."""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE sessions
            SET candidates_added = ?, pool_size_at_analysis = ?
            WHERE id = ?
        ''', (candidates_added, pool_size, session_id))

        conn.commit()
        conn.close()
    ```

- [x] **Task 7: Test candidate storage**
  - [ ] Test create_candidate with all fields:
    ```python
    local_data = {"name": "John Smith", "email": "john@test.com", "phone": "+1-555-1234"}
    gemini_data = {"skills": ["Python"], "experience_years": 3}

    result = create_candidate("role-123", "session-456", local_data, gemini_data)
    assert result["status"] == "created"
    ```
  - [ ] Test duplicate detection:
    ```python
    # Create first candidate
    store_candidate_with_duplicate_check("role-1", "sess-1", {"email": "test@test.com"}, {})

    # Create duplicate - should supersede
    result = store_candidate_with_duplicate_check("role-1", "sess-2", {"email": "test@test.com"}, {})
    assert result["is_duplicate"] == True
    assert result["superseded_id"] is not None
    ```
  - [ ] Test candidate retrieval

## Dev Notes

### Architecture Alignment

This story implements candidate storage per architecture.md:
- **Database:** SQLite with candidates table (created in Epic 1)
- **Duplicate Detection:** By email within role pool
- **Status Values:** active, superseded, hired, withdrew

### Candidate Status Flow

```
Upload Resume
      │
      ▼
Check Email in Pool
      │
      ├── Not Found ──► Create with status='active'
      │
      └── Found ──► Mark existing as 'superseded'
                          │
                          ▼
                    Create new with status='active'
```

### Database Schema Reference

```sql
CREATE TABLE candidates (
    id TEXT PRIMARY KEY,
    role_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    resume_text TEXT,
    skills TEXT,           -- JSON array
    experience_years REAL,
    experience_details TEXT,  -- JSON array
    education TEXT,           -- JSON array
    projects TEXT,            -- JSON array
    positions TEXT,           -- JSON array
    status TEXT DEFAULT 'active',
    pdf_path TEXT,
    uploaded_at TIMESTAMP,
    -- ... scoring fields added in Epic 4
    FOREIGN KEY (role_id) REFERENCES roles(id),
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);
```

### JSON Field Storage

All complex fields are stored as JSON strings:
```python
# Storing
cursor.execute('INSERT ... VALUES (?)', (json.dumps(skills_list),))

# Retrieving
skills = json.loads(row['skills'])
```

### Status Values

| Status | Meaning |
|--------|---------|
| `active` | Current candidate in pool |
| `superseded` | Replaced by newer resume |
| `hired` | Marked as hired (future feature) |
| `withdrew` | Candidate withdrew (future feature) |

### Duplicate Detection Logic

1. Only check if email is provided
2. Only check within same role_id
3. Only match against status='active'
4. Case-insensitive email matching

### Transaction Safety

Each function uses its own connection and commits immediately. For batch operations, consider using transactions:

```python
conn = get_db_connection()
try:
    # Multiple operations
    conn.commit()
except:
    conn.rollback()
    raise
finally:
    conn.close()
```

### Dependencies

- Story 1.3 (Database Schema) - candidates table must exist
- Story 3.1, 3.2, 3.3 - extraction data to store

### References

- [Source: docs/sprint-artifacts/tech-spec-epic-3.md#Candidate-Storage]
- [Source: docs/architecture.md#SQLite-Schema]
- [Source: docs/epics.md#Story-3.4]
- [Source: docs/prd.md#FR17-FR18]

## Dev Agent Record

### Context Reference

None (proceeded without story context file)

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- Python syntax check passed
- All functional tests passed:
  - Create role and session
  - Create candidate with extraction data
  - Duplicate detection by email (case-insensitive)
  - Supersede candidate
  - Store with duplicate check
  - Get candidate by ID with JSON parsing
  - Get candidates by session
  - Update session counts
  - Get candidate count for role

### Completion Notes List

- All 7 tasks completed successfully
- All 6 acceptance criteria satisfied:
  - AC3.4.1: Candidate record created with role_id and session_id
  - AC3.4.2: All extracted fields (local + Gemini) stored in database
  - AC3.4.3: Before insert, checks if email exists in role's pool
  - AC3.4.4: Duplicate found marks old candidate as 'superseded'
  - AC3.4.5: New candidate stored with status='active'
  - AC3.4.6: PDF path stored for reference
- Added pdf_path column to candidates table schema
- Case-insensitive email matching for duplicate detection
- JSON parsing for complex fields on retrieval

### File List

**Modified:**
- backend/models.py (added candidate storage functions and pdf_path column)

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-12-20 | SM Agent (Bob) | Initial draft created |
| 2025-12-20 | Dev Agent (Amelia) | Implementation complete - all ACs satisfied |
