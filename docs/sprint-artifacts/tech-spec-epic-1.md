# Epic Technical Specification: Foundation

Date: 2025-12-20
Author: Uzasch
Epic ID: 1
Status: Draft

---

## Overview

Epic 1 establishes the foundational infrastructure for TalentLens AI, an AI-powered resume shortlisting application. This epic creates the core project structure, database schema, API foundation, and frontend routing that all subsequent features will build upon.

The Foundation epic is critical path - no other epic can begin implementation until these 5 stories are complete. It establishes the React + Vite frontend, Flask backend, SQLite database, and the communication layer between them.

## Objectives and Scope

### In Scope

- React + Vite frontend project initialization with Tailwind CSS and shadcn/ui
- Flask backend project initialization with virtual environment and dependencies
- SQLite database schema creation (roles, sessions, candidates tables)
- Basic API structure with CORS configuration and health endpoint
- React Router setup with 3 placeholder pages (Home, Dashboard, History)
- Spotify Dark theme CSS variables in index.css
- Project folder structure per architecture.md

### Out of Scope

- Actual UI component implementation (Epic 2+)
- Resume upload functionality (Epic 2)
- AI analysis features (Epic 3-4)
- Business logic beyond basic setup
- Authentication (explicitly not in MVP per PRD)

## System Architecture Alignment

This epic implements the foundational layer of the two-tier architecture:

| Architecture Component | Story | Notes |
|------------------------|-------|-------|
| React SPA (Vite) | 1.1 | Creates frontend project structure |
| Flask REST API | 1.2 | Creates backend project structure |
| SQLite Database | 1.3 | Implements schema from architecture.md |
| API Layer | 1.4 | Establishes /api/* endpoints pattern |
| React Router | 1.5 | Sets up SPA navigation |

**Constraints from Architecture:**
- Must use exact folder structure defined in architecture.md
- CSS variables must match UX specification color system
- CORS must allow localhost:5173 (Vite dev server)
- API responses must follow `{success: true/false, data/error}` format

## Detailed Design

### Services and Modules

| Module | Location | Responsibility | Dependencies |
|--------|----------|----------------|--------------|
| **Frontend App** | frontend/src/App.jsx | Root component, router setup | react-router-dom |
| **Main Entry** | frontend/src/main.jsx | React DOM render | React 18 |
| **Theme Styles** | frontend/src/index.css | Tailwind + CSS variables | Tailwind CSS |
| **API Service** | frontend/src/services/api.js | Axios instance, API calls | axios |
| **Flask App** | backend/app.py | Route definitions, CORS | Flask, flask-cors |
| **Config** | backend/config.py | Environment variables | python-dotenv |
| **Models** | backend/models.py | Database CRUD operations | sqlite3 |

### Data Models and Contracts

From architecture.md, the database schema:

```sql
-- Roles table (for candidate pool grouping)
CREATE TABLE roles (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    normalized_title TEXT NOT NULL,
    weights TEXT,  -- JSON string
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(normalized_title)
);

-- Sessions table
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    role_id TEXT NOT NULL,
    job_description TEXT NOT NULL,
    candidates_added INTEGER NOT NULL,
    pool_size_at_analysis INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

-- Candidates table
CREATE TABLE candidates (
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

-- Indexes
CREATE INDEX idx_candidates_role ON candidates(role_id, status);
CREATE INDEX idx_candidates_email ON candidates(email);
```

### APIs and Interfaces

**Story 1.4 establishes the base API structure:**

| Endpoint | Method | Purpose | Response |
|----------|--------|---------|----------|
| `/api/health` | GET | Health check | `{"status": "ok"}` |

**Standard Response Format (all endpoints):**

```json
// Success
{
  "success": true,
  "data": { /* response data */ }
}

// Error
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message"
  }
}
```

**Error Handlers:**
- 404: `{"success": false, "error": {"code": "NOT_FOUND", "message": "Resource not found"}}`
- 500: `{"success": false, "error": {"code": "INTERNAL_ERROR", "message": "..."}}`

### Workflows and Sequencing

**Story Dependency Flow:**

```
Story 1.1 (Frontend Setup)  ─┐
                              ├─► Story 1.5 (Routing)
Story 1.2 (Backend Setup) ───┼─► Story 1.4 (API Structure)
                              │
Story 1.3 (Database) ────────┘
```

**Development Sequence:**
1. Stories 1.1 and 1.2 can run in parallel (no dependencies)
2. Story 1.3 requires 1.2 (backend must exist)
3. Story 1.4 requires 1.2 (backend must exist)
4. Story 1.5 requires 1.1 (frontend must exist)

## Non-Functional Requirements

### Performance

| Metric | Target | Source |
|--------|--------|--------|
| Initial page load | < 3 seconds | PRD |
| Vite HMR update | < 500ms | Industry standard |
| API health check | < 100ms | Best practice |

**Implementation Notes:**
- Vite provides fast HMR out of the box
- SQLite is performant for single-user scenarios
- No heavy operations in this epic

### Security

| Requirement | Implementation | Source |
|-------------|----------------|--------|
| API Keys protected | .env file, gitignored | Architecture ADR |
| CORS restricted | Only localhost:5173 allowed | Architecture |
| No secrets in code | python-dotenv for env vars | Best practice |

**Security Checklist for Story 1.2:**
- [ ] Create .env with placeholders
- [ ] Add .env to .gitignore
- [ ] Configure Flask-CORS properly

### Reliability/Availability

| Scenario | Handling |
|----------|----------|
| Database file missing | Auto-create on first run |
| Port already in use | Show clear error message |
| Missing .env | Flask shows warning, uses defaults |

**Development Mode Behavior:**
- Flask runs with debug=True
- Vite runs with HMR enabled
- Database auto-initializes

### Observability

| Signal | Implementation |
|--------|----------------|
| Health endpoint | GET /api/health returns status |
| Console logging | Python logging module |
| Frontend errors | Console.error (dev mode) |

**Logging Setup (Story 1.2):**
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

## Dependencies and Integrations

### Frontend Dependencies (package.json)

| Package | Version | Purpose |
|---------|---------|---------|
| react | ^18.x | UI framework |
| react-dom | ^18.x | React DOM renderer |
| react-router-dom | ^6.x | Client-side routing |
| axios | ^1.x | HTTP client |
| tailwindcss | ^3.x | Utility CSS |
| postcss | ^8.x | CSS processing |
| autoprefixer | latest | CSS prefixing |
| lucide-react | latest | Icons |
| recharts | ^2.x | Charts (for later epics) |
| react-dropzone | ^14.x | File upload (for Epic 2) |

### Backend Dependencies (requirements.txt)

| Package | Version | Purpose |
|---------|---------|---------|
| flask | ^3.x | Web framework |
| flask-cors | latest | CORS handling |
| python-dotenv | latest | Environment variables |
| google-generativeai | latest | Gemini API (Epic 3) |
| PyMuPDF | ^1.24.x | PDF parsing (Epic 3) |
| spacy | ^3.x | NER extraction (Epic 3) |

### System Requirements

- Node.js 18+
- Python 3.10+
- Git

## Acceptance Criteria (Authoritative)

### Story 1.1: Frontend Project Setup
1. AC1.1.1: Vite + React project created in `frontend/` directory
2. AC1.1.2: Tailwind CSS configured with dark theme variables
3. AC1.1.3: shadcn/ui initialized with dark theme
4. AC1.1.4: All npm dependencies installed (react-router-dom, axios, recharts, react-dropzone, lucide-react)
5. AC1.1.5: Project runs on localhost:5173
6. AC1.1.6: Folder structure matches architecture.md (components/, pages/, services/, lib/)

### Story 1.2: Backend Project Setup
1. AC1.2.1: Flask project created in `backend/` directory
2. AC1.2.2: Virtual environment created and activated
3. AC1.2.3: All pip dependencies installed
4. AC1.2.4: spaCy model en_core_web_sm downloaded
5. AC1.2.5: Project structure has app.py, config.py, models.py, services/
6. AC1.2.6: .env file created with placeholder variables
7. AC1.2.7: Server runs on localhost:5000

### Story 1.3: Database Schema Setup
1. AC1.3.1: roles table created with correct columns
2. AC1.3.2: sessions table created with foreign key to roles
3. AC1.3.3: candidates table created with all fields from architecture
4. AC1.3.4: Indexes created for role queries and email lookup
5. AC1.3.5: Database auto-creates at data/app.db on first run
6. AC1.3.6: models.py contains CRUD helper functions

### Story 1.4: API Structure and Health Check
1. AC1.4.1: GET /api/health returns `{"status": "ok"}` with 200
2. AC1.4.2: CORS allows requests from localhost:5173
3. AC1.4.3: Standard response format helpers created
4. AC1.4.4: 404 and 500 error handlers return proper format

### Story 1.5: Frontend Routing and Layout
1. AC1.5.1: Route "/" shows HomePage placeholder
2. AC1.5.2: Route "/dashboard/:sessionId" shows DashboardPage placeholder
3. AC1.5.3: Route "/history" shows HistoryPage placeholder
4. AC1.5.4: Navbar component with navigation links
5. AC1.5.5: Spotify Dark theme (CSS variables) applied globally

## Traceability Mapping

| AC | Spec Section | Component | Test Approach |
|----|--------------|-----------|---------------|
| AC1.1.1-6 | Detailed Design > Frontend | frontend/* | Manual: npm run dev succeeds |
| AC1.2.1-7 | Detailed Design > Backend | backend/* | Manual: python app.py succeeds |
| AC1.3.1-6 | Data Models | backend/models.py, data/app.db | Unit: pytest schema tests |
| AC1.4.1-4 | APIs and Interfaces | backend/app.py | Integration: pytest API tests |
| AC1.5.1-5 | Workflows > Routing | frontend/src/App.jsx | E2E: Playwright navigation |

## Risks, Assumptions, Open Questions

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Node/Python version mismatch | Medium | High | Document exact versions in README |
| shadcn/ui breaking changes | Low | Medium | Pin to stable version |
| Port conflicts (5000/5173) | Low | Low | Document alternative ports |

### Assumptions

1. Developer has Node.js 18+ and Python 3.10+ installed
2. Developer has basic familiarity with npm and pip
3. macOS or Linux environment (Windows paths may differ)
4. Internet access for package downloads

### Open Questions

1. **Q1:** Should we add a README.md to root directory in this epic?
   - **Recommendation:** Yes, add basic setup instructions

2. **Q2:** Should we configure ESLint/Prettier in Story 1.1?
   - **Recommendation:** Defer to later - keep MVP simple

## Test Strategy Summary

### Unit Tests (pytest)
- Database schema validation
- CRUD helper function tests
- Response format helper tests

### Integration Tests (pytest + Flask test client)
- /api/health endpoint returns correct response
- CORS headers present for frontend origin
- Error handlers return proper format

### E2E Tests (Playwright) - Deferred
- Navigation between routes works
- Theme applied correctly

**Test Infrastructure Setup:**
- pytest and pytest-cov for backend
- Vitest for frontend (if adding unit tests)
- Playwright configured but tests written in Epic 5

**Coverage Target:** 80% for backend Python code

---

_Generated by BMAD BMM Epic Tech Context Workflow_
_Epic: 1 - Foundation_
_Date: 2025-12-20_
