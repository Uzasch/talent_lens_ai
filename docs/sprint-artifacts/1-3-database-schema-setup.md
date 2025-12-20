# Story 1.3: Database Schema Setup

Status: review

## Story

As a **developer**,
I want **the SQLite database schema created with all required tables**,
so that **roles, sessions, and candidates can be stored and retrieved**.

## Acceptance Criteria

1. **AC1.3.1:** `roles` table created with columns: id, title, normalized_title, weights, created_at
2. **AC1.3.2:** `sessions` table created with foreign key reference to roles
3. **AC1.3.3:** `candidates` table created with all fields from architecture specification
4. **AC1.3.4:** Indexes created for role queries (`idx_candidates_role`) and email lookup (`idx_candidates_email`)
5. **AC1.3.5:** Database auto-creates at `data/app.db` on first run
6. **AC1.3.6:** `models.py` contains CRUD helper functions for all tables

## Tasks / Subtasks

- [x] **Task 1: Create database initialization function** (AC: 1.3.5)
  - [x] Add `init_db()` function to `models.py`
  - [x] Create `data/` directory if not exists
  - [x] Implement auto-creation of `data/app.db`
  - [x] Call `init_db()` on app startup in `app.py`

- [x] **Task 2: Create roles table** (AC: 1.3.1)
  - [x] Define schema:
    ```sql
    CREATE TABLE IF NOT EXISTS roles (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        normalized_title TEXT NOT NULL,
        weights TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(normalized_title)
    );
    ```
  - [x] Add to `init_db()` function

- [x] **Task 3: Create sessions table** (AC: 1.3.2)
  - [x] Define schema:
    ```sql
    CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY,
        role_id TEXT NOT NULL,
        job_description TEXT NOT NULL,
        candidates_added INTEGER NOT NULL,
        pool_size_at_analysis INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (role_id) REFERENCES roles(id)
    );
    ```
  - [x] Add to `init_db()` function

- [x] **Task 4: Create candidates table** (AC: 1.3.3)
  - [x] Define schema with all fields:
    ```sql
    CREATE TABLE IF NOT EXISTS candidates (
        id TEXT PRIMARY KEY,
        role_id TEXT NOT NULL,
        session_id TEXT NOT NULL,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        resume_text TEXT,
        skills TEXT,
        experience_years REAL,
        experience_details TEXT,
        education TEXT,
        projects TEXT,
        positions TEXT,
        rank INTEGER,
        match_score INTEGER,
        education_score INTEGER,
        experience_score INTEGER,
        projects_score INTEGER,
        positions_score INTEGER,
        skills_score INTEGER,
        summary TEXT,
        why_selected TEXT,
        compared_to_pool TEXT,
        status TEXT DEFAULT 'active',
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_ranked_at TIMESTAMP,
        FOREIGN KEY (role_id) REFERENCES roles(id),
        FOREIGN KEY (session_id) REFERENCES sessions(id)
    );
    ```
  - [x] Add to `init_db()` function

- [x] **Task 5: Create indexes** (AC: 1.3.4)
  - [x] Create role/status index:
    ```sql
    CREATE INDEX IF NOT EXISTS idx_candidates_role ON candidates(role_id, status);
    ```
  - [x] Create email index:
    ```sql
    CREATE INDEX IF NOT EXISTS idx_candidates_email ON candidates(email);
    ```

- [x] **Task 6: Implement CRUD helper functions** (AC: 1.3.6)
  - [x] `get_db_connection()` - returns sqlite3 connection
  - [x] `create_role(title, weights=None)` - creates role with UUID
  - [x] `get_role_by_id(role_id)` - fetches single role
  - [x] `get_roles()` - fetches all roles
  - [x] `create_session(role_id, job_description, candidates_added, pool_size)` - creates session
  - [x] `get_session_by_id(session_id)` - fetches single session
  - [x] `create_candidate(data_dict)` - creates candidate record
  - [x] `get_candidates_by_role(role_id, status='active')` - fetches pool

- [x] **Task 7: Add UUID generation utility**
  - [x] Import `uuid` module
  - [x] Use `str(uuid.uuid4())` for all ID generation

- [x] **Task 8: Verify database creation**
  - [x] Run `python app.py`
  - [x] Confirm `data/app.db` file is created
  - [x] Use SQLite browser to verify table structures
  - [x] Test one CRUD function manually

## Dev Notes

### Architecture Alignment

This story implements the database layer per architecture.md:
- **Database:** SQLite (file-based, beginner-friendly)
- **Location:** `data/app.db`
- **Schema:** 3 tables with foreign key relationships
- **IDs:** UUID strings for all primary keys

### Database Schema Diagram

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│   roles     │       │  sessions   │       │ candidates  │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ id (PK)     │◄──────│ role_id (FK)│◄──────│ role_id (FK)│
│ title       │       │ id (PK)     │       │ session_id  │
│ normalized  │       │ job_desc    │       │ id (PK)     │
│ weights     │       │ candidates  │       │ name, email │
│ created_at  │       │ pool_size   │       │ scores...   │
└─────────────┘       │ created_at  │       │ status      │
                      └─────────────┘       └─────────────┘
```

### models.py Structure

```python
import sqlite3
import uuid
import os
from config import Config

def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs('data', exist_ok=True)
    conn = get_db_connection()
    # Execute CREATE TABLE statements
    conn.close()

# CRUD functions...
```

### Dependency on Story 1.2

This story requires the backend project structure from Story 1.2 to be complete.

[Source: docs/sprint-artifacts/tech-spec-epic-1.md#Workflows-and-Sequencing]

### References

- [Source: docs/architecture.md#Database-Schema]
- [Source: docs/sprint-artifacts/tech-spec-epic-1.md#Data-Models-and-Contracts]
- [Source: docs/sprint-artifacts/tech-spec-epic-1.md#Story-1.3]
- [Source: docs/epics.md#Story-1.3]

## Dev Agent Record

### Context Reference

None (proceeded without story context file)

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- Updated config.py to use absolute paths (BASE_DIR) for database and uploads
- All 3 tables verified with sqlite3 CLI
- Both indexes (idx_candidates_role, idx_candidates_email) confirmed
- CRUD test passed: create_role and get_role_by_id working

### Completion Notes List

- All 8 tasks completed successfully
- All 6 acceptance criteria satisfied
- Database auto-creates at backend/data/app.db
- 8 CRUD functions implemented in models.py
- init_db() called on app startup

### File List

**Modified:**
- backend/models.py (complete rewrite with schema and CRUD)
- backend/config.py (added BASE_DIR for absolute paths)
- backend/app.py (added init_db() call on startup)

**Created:**
- backend/data/app.db (auto-generated)

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-12-20 | SM Agent (Bob) | Initial draft created |
| 2025-12-20 | Dev Agent (Amelia) | Implementation complete - all ACs satisfied |
