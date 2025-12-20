# Story 7.1: Save Session After Analysis

Status: review

## Story

As a **system**,
I want **to save analysis results**,
So that **users can revisit them later**.

## Acceptance Criteria

1. **AC7.1.1:** Session record is created with role_id, job_description, etc.
2. **AC7.1.2:** pool_size_at_analysis is recorded
3. **AC7.1.3:** All candidates remain in pool for future sessions
4. **AC7.1.4:** Inferred priorities and thresholds config are saved
5. **AC7.1.5:** Resume text and PDF files are persisted

## Tasks / Subtasks

- [ ] **Task 1: Ensure session creation in analyze endpoint** (AC: 7.1.1, 7.1.2)
  - [ ] Verify session is created in `/api/analyze`:
    ```python
    def create_session(
        role_id: str,
        job_description: str,
        candidates_added: int,
        pool_size: int,
        inferred_priorities: dict,
        priority_reasoning: str,
        thresholds_config: dict,
        why_not_others: str
    ) -> str:
        """Create a new analysis session."""
        session_id = str(uuid.uuid4())

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO sessions (
                id,
                role_id,
                job_description,
                candidates_added,
                pool_size_at_analysis,
                inferred_priorities,
                priority_reasoning,
                thresholds_config,
                why_not_others,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            role_id,
            job_description,
            candidates_added,
            pool_size,
            json.dumps(inferred_priorities),
            priority_reasoning,
            json.dumps(thresholds_config),
            why_not_others,
            datetime.utcnow().isoformat()
        ))

        conn.commit()
        conn.close()

        logger.info(f'Session created: {session_id}')
        return session_id
    ```

- [ ] **Task 2: Add get_session_by_id function** (AC: 7.1.1)
  - [ ] Add to `models.py`:
    ```python
    def get_session_by_id(session_id: str) -> dict | None:
        """Get full session record by ID."""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                s.*,
                r.title as role_title
            FROM sessions s
            JOIN roles r ON s.role_id = r.id
            WHERE s.id = ?
        ''', (session_id,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        session = dict(row)
        # Parse JSON fields
        session['inferred_priorities'] = json.loads(
            session.get('inferred_priorities') or '{}'
        )
        session['thresholds_config'] = json.loads(
            session.get('thresholds_config') or '{}'
        )

        return session
    ```

- [ ] **Task 3: Ensure candidates are linked to session** (AC: 7.1.3)
  - [ ] Verify candidate creation includes session_id:
    ```python
    def store_candidate(
        role_id: str,
        session_id: str,
        name: str,
        email: str,
        phone: str,
        resume_text: str,
        extracted_data: dict
    ) -> str:
        """Store a new candidate in the pool."""
        candidate_id = str(uuid.uuid4())

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO candidates (
                id,
                role_id,
                session_id,
                name,
                email,
                phone,
                resume_text,
                skills,
                experience_years,
                experience_details,
                education,
                projects,
                positions,
                status,
                uploaded_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', ?)
        ''', (
            candidate_id,
            role_id,
            session_id,
            name,
            email,
            phone,
            resume_text,
            json.dumps(extracted_data.get('skills', [])),
            extracted_data.get('experience_years', 0),
            json.dumps(extracted_data.get('experience_details', [])),
            json.dumps(extracted_data.get('education', [])),
            json.dumps(extracted_data.get('projects', [])),
            json.dumps(extracted_data.get('positions', [])),
            datetime.utcnow().isoformat()
        ))

        conn.commit()
        conn.close()

        return candidate_id
    ```

- [ ] **Task 4: Store PDF files persistently** (AC: 7.1.5)
  - [ ] Save uploaded PDFs:
    ```python
    import os
    from werkzeug.utils import secure_filename

    UPLOAD_FOLDER = 'uploads'

    def save_uploaded_file(file, candidate_id: str) -> str:
        """Save uploaded PDF file and return path."""
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)

        # Create unique filename
        original_name = secure_filename(file.filename)
        filename = f"{candidate_id}_{original_name}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        file.save(filepath)
        logger.info(f'Saved file: {filepath}')

        return filepath
    ```

- [ ] **Task 5: Update candidate with analysis results** (AC: 7.1.4)
  - [ ] Update scores after Phase 2:
    ```python
    def update_candidate_scores(
        candidate_id: str,
        rank: int,
        match_score: int,
        dimension_scores: dict,
        summary: list,
        why_selected: str,
        compared_to_pool: str,
        tie_breaker_applied: bool = False,
        tie_breaker_reason: str = None
    ):
        """Update candidate with analysis scores."""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE candidates SET
                rank = ?,
                match_score = ?,
                education_score = ?,
                experience_score = ?,
                projects_score = ?,
                positions_score = ?,
                skills_score = ?,
                summary = ?,
                why_selected = ?,
                compared_to_pool = ?,
                tie_breaker_applied = ?,
                tie_breaker_reason = ?,
                last_ranked_at = ?
            WHERE id = ?
        ''', (
            rank,
            match_score,
            dimension_scores.get('education', 0),
            dimension_scores.get('experience', 0),
            dimension_scores.get('projects', 0),
            dimension_scores.get('positions', 0),
            dimension_scores.get('skills', 0),
            json.dumps(summary),
            why_selected,
            compared_to_pool,
            tie_breaker_applied,
            tie_breaker_reason,
            datetime.utcnow().isoformat(),
            candidate_id
        ))

        conn.commit()
        conn.close()
    ```

- [ ] **Task 6: Test session persistence**
  - [ ] Run analysis and verify session created
  - [ ] Verify all fields saved correctly
  - [ ] Verify candidates linked to session
  - [ ] Verify PDF files saved
  - [ ] Verify session can be retrieved

## Dev Notes

### Architecture Alignment

This story ensures all analysis data is persisted:
- **Session:** Snapshot of analysis configuration and results
- **Candidates:** Persistent pool with scores
- **Files:** PDFs saved to uploads/ directory

### Data Persistence Flow

```
Analysis Request
      │
      ├── Create session record
      │       └── role_id, job_description, config
      │
      ├── Phase 1: For each resume
      │       ├── Save PDF to uploads/
      │       ├── Extract text
      │       └── Create candidate record
      │
      ├── Phase 2: After ranking
      │       ├── Update candidate scores
      │       └── Update session with results
      │
      └── Return session_id
```

### Session Fields

| Field | Description |
|-------|-------------|
| id | Unique session identifier |
| role_id | Link to role/pool |
| job_description | JD text for this analysis |
| candidates_added | New candidates in this batch |
| pool_size_at_analysis | Total pool size at this moment |
| inferred_priorities | JSON of priority levels |
| priority_reasoning | AI explanation |
| thresholds_config | JSON of threshold settings |
| why_not_others | AI explanation |
| created_at | Timestamp |

### Candidate Fields Updated

| Field | When Updated |
|-------|--------------|
| Basic info | Phase 1 (extraction) |
| resume_text | Phase 1 |
| Scores | Phase 2 (ranking) |
| summary | Phase 2 |
| why_selected | Phase 2 |

### File Storage

```
uploads/
├── {candidate_id}_resume1.pdf
├── {candidate_id}_resume2.pdf
└── ...
```

### References

- [Source: docs/sprint-artifacts/tech-spec-epic-7.md#Session-Persistence]
- [Source: docs/architecture.md#Data-Architecture]
- [Source: docs/epics.md#Story-7.1]
- [Source: docs/prd.md#FR65-FR76]

## Dev Agent Record

### Context Reference

docs/sprint-artifacts/7-1-save-session-after-analysis.md

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- Session schema verified at models.py:33-50
- Added thresholds_config and why_not_others columns to sessions table
- Added update_session_thresholds() function at models.py:639-656
- Added update_session_why_not_others() function at models.py:659-676
- Updated analysis_service.py to call new storage functions
- Test verified all session fields are properly stored and retrieved

### Completion Notes List

- All 5 acceptance criteria satisfied:
  - AC7.1.1: Session record created with role_id, job_description via create_session() ✅
  - AC7.1.2: pool_size_at_analysis recorded via update_session_counts() ✅
  - AC7.1.3: Candidates remain in pool with status='active', linked to session_id ✅
  - AC7.1.4: Inferred priorities stored via update_session_priorities(), thresholds via update_session_thresholds() ✅
  - AC7.1.5: Resume text stored in candidates.resume_text, PDFs saved to uploads/ via pdf_parser.save_uploaded_pdf() ✅
- Added thresholds_config TEXT column to sessions table
- Added why_not_others TEXT column to sessions table
- Updated get_full_session_data() to use stored why_not_others and return thresholds_config
- Database schema recreated with new columns

### File List

**Modified:**
- backend/models.py (added thresholds_config and why_not_others columns, update functions)
- backend/services/analysis_service.py (added calls to store thresholds and why_not_others)

**Already existed (verified working):**
- backend/services/pdf_parser.py (save_uploaded_pdf saves PDFs to uploads/)
- backend/models.py (create_candidate_from_extraction stores resume_text)

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-12-20 | SM Agent (Bob) | Initial draft created |
| 2025-12-20 | Dev Agent (Amelia) | Implementation complete - all ACs satisfied |
