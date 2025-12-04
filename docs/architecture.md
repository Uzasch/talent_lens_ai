# Resume Shortlister - Architecture Document

**Date:** 2025-11-30
**Author:** Uzasch
**Version:** 1.0

---

## Executive Summary

A simple two-tier web application architecture: **React SPA frontend** communicating with a **Flask REST API backend**. Data persists in SQLite. The Gemini API handles AI analysis, and Gmail SMTP handles email delivery.

This architecture prioritizes **simplicity** and **beginner-friendliness** - perfect for a college project that needs to work reliably for demos.

---

## Project Initialization

### Step 1: Create Project Root
```bash
mkdir resume-shortlister
cd resume-shortlister
```

### Step 2: Initialize Frontend
```bash
npm create vite@latest frontend -- --template react
cd frontend
npm install

# Tailwind CSS
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# shadcn/ui
npx shadcn@latest init

# Additional dependencies
npm install react-router-dom axios recharts react-dropzone lucide-react

cd ..
```

### Step 3: Initialize Backend
```bash
mkdir backend
cd backend
python -m venv venv

# Activate virtual environment
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

pip install flask flask-cors python-dotenv google-generativeai PyMuPDF

# Create directory structure
mkdir -p data uploads
touch app.py config.py

cd ..
```

### Step 4: Environment Setup
Create `backend/.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GMAIL_ADDRESS=your_email@gmail.com
GMAIL_APP_PASSWORD=your_app_password_here
FLASK_ENV=development
```

---

## Decision Summary

| Category | Decision | Version | Affects FRs | Rationale |
|----------|----------|---------|-------------|-----------|
| Frontend Framework | React + Vite | React 18.x, Vite 5.x | All UI FRs | Fast dev, beginner-friendly |
| Styling | Tailwind CSS | 3.x | All UI FRs | Utility-first, shadcn compatible |
| UI Components | shadcn/ui | Latest | FR20-24 | Pre-built accessible components |
| Charts | Recharts | 2.x | FR18, FR22 | React-native charts library |
| Backend Framework | Flask | 3.x | All API FRs | Python, simple, well-documented |
| Database | SQLite | 3.x | FR34-41 | Zero config, file-based |
| AI Provider | Google Gemini | gemini-1.5-flash | FR8-16, FR25-28 | Free tier, good for analysis |
| PDF Parsing | PyMuPDF (fitz) | 1.24.x | FR8 | Fast, reliable PDF extraction |
| Email | Gmail SMTP | - | FR29-33 | Free, simple setup |
| HTTP Client | Axios | 1.x | All API calls | Promise-based, interceptors |
| Routing | React Router | 6.x | Navigation | Standard React routing |
| File Upload | react-dropzone | 14.x | FR3-6 | Drag-drop support |

---

## Project Structure

```
resume-shortlister/
├── frontend/                    # React application
│   ├── public/
│   │   └── vite.svg
│   ├── src/
│   │   ├── components/          # Reusable components
│   │   │   ├── ui/              # shadcn/ui components
│   │   │   │   ├── button.jsx
│   │   │   │   ├── card.jsx
│   │   │   │   ├── input.jsx
│   │   │   │   ├── textarea.jsx
│   │   │   │   ├── dialog.jsx
│   │   │   │   ├── toast.jsx
│   │   │   │   ├── progress.jsx
│   │   │   │   ├── badge.jsx
│   │   │   │   └── skeleton.jsx
│   │   │   ├── CandidateCard.jsx
│   │   │   ├── DropZone.jsx
│   │   │   ├── StatCard.jsx
│   │   │   ├── ScoreBar.jsx
│   │   │   └── Navbar.jsx
│   │   ├── pages/               # Page components
│   │   │   ├── HomePage.jsx     # Upload screen
│   │   │   ├── DashboardPage.jsx # Results screen
│   │   │   └── HistoryPage.jsx  # Past sessions
│   │   ├── services/            # API calls
│   │   │   └── api.js           # Axios instance + endpoints
│   │   ├── lib/                 # Utilities
│   │   │   └── utils.js         # Helper functions (cn, etc.)
│   │   ├── App.jsx              # Router setup
│   │   ├── main.jsx             # Entry point
│   │   └── index.css            # Tailwind + theme variables
│   ├── components.json          # shadcn config
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── vite.config.js
│   ├── package.json
│   └── index.html
│
├── backend/                     # Flask application
│   ├── app.py                   # Main Flask app + routes
│   ├── config.py                # Configuration
│   ├── models.py                # SQLite models/queries
│   ├── services/
│   │   ├── pdf_parser.py        # PDF text extraction
│   │   ├── gemini_service.py    # Gemini API integration
│   │   └── email_service.py     # Gmail SMTP
│   ├── data/
│   │   └── app.db               # SQLite database (auto-created)
│   ├── uploads/                 # Uploaded PDF files
│   ├── requirements.txt         # Python dependencies
│   ├── .env                     # Environment variables (gitignored)
│   └── venv/                    # Virtual environment (gitignored)
│
├── .gitignore
└── README.md
```

---

## FR Category to Architecture Mapping

| FR Category | Frontend | Backend | Database |
|-------------|----------|---------|----------|
| Job & Resume Input (FR1-7) | `HomePage.jsx`, `DropZone.jsx` | `app.py: /api/analyze` | - |
| AI Analysis (FR8-16) | `DashboardPage.jsx` (loading state) | `gemini_service.py`, `pdf_parser.py` | - |
| Dashboard Overview (FR17-19) | `DashboardPage.jsx`, `StatCard.jsx` | `app.py: /api/sessions/<id>` | `sessions` table |
| Top 6 Candidates (FR20-24) | `CandidateCard.jsx`, `ScoreBar.jsx` | Response from `/api/analyze` | `candidates` table |
| Transparency (FR25-28) | `CandidateCard.jsx` (WHY section) | Gemini prompt engineering | - |
| Email (FR29-33) | `DashboardPage.jsx` (modal) | `email_service.py`, `app.py: /api/send-emails` | - |
| Session History (FR34-37) | `HistoryPage.jsx` | `app.py: /api/sessions` | `sessions`, `candidates` tables |
| Data Management (FR38-41) | - | `models.py` | All tables |

---

## Technology Stack Details

### Frontend Stack

**React 18 + Vite**
- Fast HMR (Hot Module Replacement)
- ES modules for faster builds
- Simple configuration

**Tailwind CSS 3**
- Utility-first CSS
- Dark mode via CSS variables
- Responsive design utilities

**shadcn/ui**
- Copy-paste components
- Radix UI primitives (accessible)
- Customizable via Tailwind

**Recharts**
- React-native charting
- Responsive
- Used for score breakdown bars

### Backend Stack

**Flask 3.x**
- Lightweight Python web framework
- Simple routing
- Good documentation

**SQLite 3**
- Zero configuration
- File-based database
- Perfect for single-user apps

**PyMuPDF (fitz)**
- Fast PDF text extraction
- Handles various PDF formats
- Pure Python

**Google Generative AI (Gemini)**
- Free tier available
- Good for text analysis
- Simple Python SDK

---

## API Contracts

### Base URL
```
Development: http://localhost:5000/api
```

### Endpoints

#### POST /api/analyze
Analyze resumes against a job description.

**Request:**
```json
{
  "job_title": "Senior React Developer",
  "job_description": "We are looking for...",
  "files": [/* multipart form data - PDF files */]
}
```

**Response:**
```json
{
  "success": true,
  "session_id": "uuid-string",
  "data": {
    "job_title": "Senior React Developer",
    "total_analyzed": 47,
    "analysis_time_seconds": 45,
    "overview": {
      "experience_range": "2-8 years",
      "top_skills": ["React", "TypeScript", "Node.js"],
      "average_match": 72
    },
    "top_candidates": [
      {
        "rank": 1,
        "name": "Rahul Sharma",
        "email": "rahul@email.com",
        "match_score": 92,
        "scores": {
          "education": 85,
          "experience": 95,
          "projects": 90
        },
        "summary": ["5 years React experience", "Led team of 5", "Built apps for 50K users"],
        "why_selected": "Best combination of leadership experience and technical depth. Only candidate with microservices experience matching the job requirements."
      }
      // ... 5 more candidates
    ],
    "why_not_others": "Remaining 41 candidates scored below 75% match. Common gaps: insufficient React experience, no leadership background, or missing key skills like TypeScript."
  }
}
```

#### GET /api/sessions
Get list of past analysis sessions.

**Response:**
```json
{
  "success": true,
  "sessions": [
    {
      "id": "uuid-string",
      "job_title": "Senior React Developer",
      "created_at": "2025-11-30T10:30:00Z",
      "total_candidates": 47,
      "top_match_score": 92
    }
  ]
}
```

#### GET /api/sessions/:id
Get a specific session's full results.

**Response:** Same structure as POST /api/analyze response.

#### POST /api/send-emails
Send interview invitations to top candidates.

**Request:**
```json
{
  "session_id": "uuid-string",
  "candidate_emails": ["rahul@email.com", "priya@email.com"],
  "message": "Dear {name},\n\nWe would like to invite you for an interview..."
}
```

**Response:**
```json
{
  "success": true,
  "sent": 6,
  "failed": 0,
  "results": [
    {"email": "rahul@email.com", "status": "sent"},
    {"email": "priya@email.com", "status": "sent"}
  ]
}
```

### Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "GEMINI_API_ERROR",
    "message": "Failed to analyze resumes. Please try again."
  }
}
```

---

## Data Architecture

### SQLite Schema

```sql
-- Sessions table
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    job_title TEXT NOT NULL,
    job_description TEXT NOT NULL,
    total_analyzed INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Candidates table
CREATE TABLE candidates (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    rank INTEGER,
    name TEXT NOT NULL,
    email TEXT,
    match_score INTEGER NOT NULL,
    education_score INTEGER,
    experience_score INTEGER,
    projects_score INTEGER,
    summary TEXT,  -- JSON array as string
    why_selected TEXT,
    resume_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);
```

### Data Flow

```
User uploads PDFs
        │
        ▼
┌─────────────────┐
│  Flask Backend  │
│  /api/analyze   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   PDF Parser    │ ──► Extract text from each PDF
│   (PyMuPDF)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Gemini API     │ ──► Analyze in batches of 10-15
│  (Batch Process)│ ──► Score: Education, Experience, Projects
└────────┬────────┘ ──► Generate WHY explanations
         │
         ▼
┌─────────────────┐
│    SQLite       │ ──► Save session + candidates
│    Database     │
└────────┬────────┘
         │
         ▼
   JSON Response to Frontend
```

---

## Implementation Patterns

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| React components | PascalCase | `CandidateCard.jsx` |
| React files | PascalCase | `HomePage.jsx` |
| JS functions | camelCase | `fetchCandidates()` |
| CSS classes | kebab-case (Tailwind) | `bg-card text-foreground` |
| Python files | snake_case | `gemini_service.py` |
| Python functions | snake_case | `analyze_resumes()` |
| Python classes | PascalCase | `GeminiService` |
| API endpoints | kebab-case | `/api/send-emails` |
| Database tables | snake_case, plural | `candidates` |
| Database columns | snake_case | `match_score` |
| Environment vars | SCREAMING_SNAKE | `GEMINI_API_KEY` |

### File Organization

**Frontend:**
- One component per file
- Pages in `pages/` folder
- Reusable components in `components/`
- API calls centralized in `services/api.js`
- shadcn components in `components/ui/`

**Backend:**
- Routes in `app.py`
- Business logic in `services/`
- Database operations in `models.py`
- Configuration in `config.py`

### API Response Format

All API responses follow this structure:

```javascript
// Success
{
  "success": true,
  "data": { /* actual response data */ }
}

// Error
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message"
  }
}
```

### Error Handling

**Frontend:**
```javascript
try {
  const response = await api.post('/analyze', formData);
  if (response.data.success) {
    // Handle success
  }
} catch (error) {
  toast.error(error.response?.data?.error?.message || 'Something went wrong');
}
```

**Backend:**
```python
@app.errorhandler(Exception)
def handle_error(error):
    return jsonify({
        'success': False,
        'error': {
            'code': 'INTERNAL_ERROR',
            'message': str(error)
        }
    }), 500
```

### Loading States

- Button shows spinner when submitting
- Full-screen loader with progress for analysis
- Skeleton loaders for data fetching
- Toast notifications for success/error

---

## Consistency Rules

### Date/Time
- Store as ISO 8601 strings in database
- Display in user-friendly format: "Nov 30, 2025"
- Use `date-fns` or native `Intl.DateTimeFormat` for formatting

### Colors (CSS Variables)
All colors via CSS variables in `index.css`:
```css
--primary: #1DB954;
--background: #121212;
--card: #282828;
/* etc. */
```

### Logging (Backend)
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"Analyzing {len(files)} resumes for job: {job_title}")
logger.error(f"Gemini API error: {str(e)}")
```

### Environment Variables
- All secrets in `.env` file
- Never commit `.env` to git
- Use `python-dotenv` to load
- Use `import.meta.env` in Vite

---

## Security Considerations

| Concern | Approach |
|---------|----------|
| API Keys | Stored in `.env`, never in code |
| CORS | Flask-CORS allows only `localhost:5173` |
| File Uploads | Only accept `.pdf` files, validate MIME type |
| SQL Injection | Use parameterized queries |
| XSS | React escapes by default |

**Note:** No authentication for MVP (single-user demo). Add auth if deploying publicly.

---

## Performance Considerations

| Concern | Approach |
|---------|----------|
| Large file uploads | Client-side file size validation (max 10MB per file) |
| Many resumes | Batch processing (10-15 per Gemini API call) |
| Slow AI analysis | Progress indicator, batch status updates |
| Database queries | SQLite is fast enough for single-user |

---

## Development Environment

### Prerequisites
- Node.js 18+ (for frontend)
- Python 3.10+ (for backend)
- Git

### Running Locally

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python app.py
# Runs on http://localhost:5000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
# Runs on http://localhost:5173
```

### Environment Variables

**backend/.env:**
```env
GEMINI_API_KEY=your_key_here
GMAIL_ADDRESS=your_email@gmail.com
GMAIL_APP_PASSWORD=your_app_password
FLASK_ENV=development
```

---

## Architecture Decision Records (ADRs)

### ADR-001: Separate Frontend and Backend
**Decision:** Use separate React (Vite) and Flask projects instead of a monolithic approach.
**Rationale:** Clearer separation of concerns, easier to understand for beginners, standard industry pattern.

### ADR-002: SQLite over PostgreSQL
**Decision:** Use SQLite instead of PostgreSQL.
**Rationale:** Zero configuration, file-based, perfect for single-user college project. No need for a database server.

### ADR-003: Flask over FastAPI
**Decision:** Use Flask instead of FastAPI.
**Rationale:** More beginner-friendly, extensive documentation, widely taught in courses. FastAPI's async benefits not needed for this use case.

### ADR-004: Gmail SMTP over Email Services
**Decision:** Use Gmail SMTP instead of SendGrid/Resend.
**Rationale:** Free, no additional account setup, sufficient for demo purposes. Uses App Passwords for security.

### ADR-005: Gemini over OpenAI
**Decision:** Use Google Gemini API instead of OpenAI.
**Rationale:** Generous free tier, good for text analysis, simple Python SDK. Cost-effective for a college project.

### ADR-006: No Authentication
**Decision:** Skip user authentication for MVP.
**Rationale:** Single-user demo application. Adding auth would increase complexity without benefit for college evaluation.

---

_Generated by BMAD Decision Architecture Workflow v1.0_
_Date: 2025-11-30_
_For: Uzasch_
