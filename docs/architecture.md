# TalentLens AI - Architecture Document

**Date:** 2025-12-04
**Author:** Uzasch
**Version:** 2.0
**Client:** Yoboho Company HR Department

---

## Executive Summary

A simple two-tier web application architecture: **React SPA frontend** communicating with a **Flask REST API backend**. Data persists in SQLite. The Gemini API handles AI analysis, and Gmail SMTP handles email delivery.

### Key Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| **Two-Phase Analysis** | Phase 1: Extract data locally. Phase 2: Comparative analysis via Gemini |
| **Role-Based Candidate Pools** | All candidates for a role are compared together (current + past sessions) |
| **Gemini Only for AI Tasks** | PDF parsing, regex extraction done locally. API only for intelligence |
| **Comparative Ranking** | Candidates ranked relative to each other, not scored in isolation |

---

## AI Strategy: What Uses Gemini vs Local Processing

### Local Processing (No API)

| Task | Tool | Why Local |
|------|------|-----------|
| PDF text extraction | PyMuPDF | Just reading file, no intelligence needed |
| Name extraction | Regex + spaCy NER | Pattern matching |
| Email extraction | Regex | Simple pattern: `[\w.-]+@[\w.-]+` |
| Phone extraction | Regex | Pattern matching |
| Database storage | SQLite | Storage, no AI |
| Email sending | Gmail SMTP | Not AI related |

### Gemini API (Intelligence Required)

| Task | Why API Needed |
|------|----------------|
| **Skill extraction** | Understanding context ("React" vs "reactive") |
| **Experience parsing** | Understanding "2+ years" vs "led team for 3 years" |
| **Project quality assessment** | Judging impact, not just counting |
| **Comparative ranking** | "Who is BEST among all candidates?" |
| **Score generation** | Context-aware scoring relative to pool |
| **Summary generation** | Natural language bullet points |
| **WHY explanations** | Reasoning about selection |

---

## Two-Phase Analysis Architecture

### Phase 1: Individual Data Extraction

```
┌─────────────────────────────────────────────────────────┐
│ PHASE 1: Extract Data (Per Resume)                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  PDF File                                                │
│      │                                                   │
│      ▼                                                   │
│  PyMuPDF ──► Raw Text                                   │
│      │                                                   │
│      ▼                                                   │
│  Local Extraction (Regex/spaCy)                         │
│      ├── Name (regex patterns)                          │
│      ├── Email (regex)                                  │
│      └── Phone (regex)                                  │
│      │                                                   │
│      ▼                                                   │
│  Gemini API (Individual)                                │
│      ├── Extract skills                                 │
│      ├── Parse experience details                       │
│      ├── Parse education details                        │
│      └── Extract project details                        │
│      │                                                   │
│      ▼                                                   │
│  Store in SQLite (candidates table)                     │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Phase 2: Comparative Analysis (Role-Based Pool)

```
┌─────────────────────────────────────────────────────────┐
│ PHASE 2: Comparative Ranking (All Candidates Together)  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Fetch ALL candidates for this role from DB             │
│  (Current batch + All past sessions)                    │
│      │                                                   │
│      ▼                                                   │
│  Build Candidate Pool Summary                           │
│  ┌────────────────────────────────────────────┐         │
│  │ Role: "Python Developer"                   │         │
│  │ Total Candidates: 45                       │         │
│  │                                            │         │
│  │ Candidate 1: Ali                           │         │
│  │   - 2yr exp, 3 projects, Junior→Mid       │         │
│  │   - Skills: Python, Django, PostgreSQL    │         │
│  │                                            │         │
│  │ Candidate 2: Sara                          │         │
│  │   - 4yr exp, 5 projects, Mid→Senior       │         │
│  │   - Skills: Python, FastAPI, AWS          │         │
│  │                                            │         │
│  │ ... (all 45 candidates)                   │         │
│  └────────────────────────────────────────────┘         │
│      │                                                   │
│      ▼                                                   │
│  Send to Gemini (Single Prompt with Full Context)       │
│  "Given this job description and ALL 45 candidates:     │
│   - Rank them considering experience, projects,         │
│     positions, skills, education                        │
│   - Score relative to the candidate pool                │
│   - Explain WHY top candidates are best                 │
│   - Explain WHY others weren't selected"                │
│      │                                                   │
│      ▼                                                   │
│  Gemini Returns: Rankings + Scores + Explanations       │
│      │                                                   │
│      ▼                                                   │
│  Update candidates in DB with ranks/scores              │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Role-Based Candidate Pool System

### Concept

Instead of analyzing candidates per session, we maintain a **persistent pool per role**:

```
Role: "Python Developer"
├── Session 1 (Nov 28): 20 resumes uploaded
├── Session 2 (Nov 30): 15 resumes uploaded
├── Session 3 (Dec 02): 10 resumes uploaded
└── Total Pool: 45 candidates

When Session 3 is analyzed:
  → Gemini sees ALL 45 candidates
  → Ranks them against each other
  → New candidates compared fairly to existing pool
```

### Benefits

| Benefit | Description |
|---------|-------------|
| **Fair Comparison** | New candidate with 3yr exp ranked against all others with similar exp |
| **AI-Fluff Detection** | If everyone claims "expert", Gemini finds who actually proves it |
| **Pool-Relative Scoring** | 80% in strong pool ≠ 80% in weak pool |
| **Historical Context** | "This is the best Python candidate we've seen across 3 hiring rounds" |

### Role Normalization

To avoid duplicate pools for similar roles:

| Input | Normalized Role |
|-------|-----------------|
| "Python Dev" | "Python Developer" |
| "Python Developer" | "Python Developer" |
| "Sr. Python Developer" | "Senior Python Developer" |
| "python developer" | "Python Developer" |

---

## Multi-Level Ranking System

The ranking system uses 4 levels to determine the best candidates:

```
┌─────────────────────────────────────────────────────────┐
│ Level 1: Job-Inferred Priority                          │
│          Gemini reads JD → determines what matters most │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Level 2: Minimum Thresholds (Optional)                  │
│          Eliminate candidates below minimum scores      │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Level 3: Weighted Scoring                               │
│          Apply weights to calculate overall match %     │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Level 4: Tie-Breaker Logic                              │
│          Gemini explains subtle differences             │
└─────────────────────────────────────────────────────────┘
```

---

### Level 1: Job-Inferred Priority

Gemini analyzes the job description and automatically determines which dimensions are most important:

| JD Contains | Gemini Infers |
|-------------|---------------|
| "5+ years experience", "senior" | Experience = CRITICAL |
| "React, Node.js, TypeScript" | Skills = CRITICAL |
| "team lead", "manage developers" | Positions = IMPORTANT |
| "built scalable systems" | Projects = IMPORTANT |
| "CS degree preferred" | Education = NICE-TO-HAVE |
| No mention of education | Education = LOW PRIORITY |

**Output Format:**
```json
{
  "inferred_priorities": {
    "experience": "CRITICAL",
    "skills": "CRITICAL",
    "positions": "IMPORTANT",
    "projects": "IMPORTANT",
    "education": "NICE_TO_HAVE"
  },
  "reasoning": "JD emphasizes 5+ years and specific tech stack, mentions team lead. No education requirements stated."
}
```

---

### Level 2: Minimum Thresholds (Optional)

HR can set minimum scores for any dimension. Candidates below threshold are eliminated.

| Dimension | Threshold | Effect |
|-----------|-----------|--------|
| Experience | ≥ 60% | Below = eliminated from ranking |
| Skills | ≥ 50% | Below = eliminated from ranking |
| Projects | ≥ 40% | Below = eliminated from ranking |
| Positions | No minimum | Just contributes to score |
| Education | No minimum | Just contributes to score |

**Example:**
```
Pool: 45 candidates
After thresholds: 32 candidates remain
Eliminated: 13 candidates
  - 8 candidates: Experience < 60%
  - 5 candidates: Skills < 50%
```

**Configuration:**
```json
{
  "thresholds": {
    "experience": { "enabled": true, "minimum": 60 },
    "skills": { "enabled": true, "minimum": 50 },
    "projects": { "enabled": false },
    "positions": { "enabled": false },
    "education": { "enabled": false }
  }
}
```

---

### Level 3: Weighted Scoring

After filtering, apply weights to remaining candidates:

| Factor | Default Weight | What Gemini Evaluates |
|--------|----------------|----------------------|
| **Experience** | 20% | Years, relevance, progression, responsibilities |
| **Projects** | 20% | Quality, impact, scale, relevance to job |
| **Positions** | 20% | Career growth (Junior→Mid→Senior), leadership |
| **Skills** | 20% | Match with job requirements, depth vs breadth |
| **Education** | 20% | Degree relevance, institution, certifications |

**Custom Weights Example:**
```json
{
  "weights": {
    "experience": 30,
    "projects": 25,
    "skills": 20,
    "positions": 15,
    "education": 10
  }
}
```

**Score Calculation:**
```
Overall Match = (Experience × 0.30) + (Projects × 0.25) +
                (Skills × 0.20) + (Positions × 0.15) +
                (Education × 0.10)
```

---

### Level 4: Tie-Breaker Logic

When candidates have similar overall scores (within 5%), Gemini applies tie-breaker logic:

| Tie-Breaker Factor | How It's Used |
|--------------------|---------------|
| **CRITICAL dimension scores** | Higher score in CRITICAL dimension wins |
| **Project impact/scale** | 10K users > 100 users |
| **Career progression speed** | Junior→Senior in 3yr > 5yr |
| **Leadership indicators** | Led team > worked in team |
| **Recency of experience** | Recent experience > old experience |
| **Company reputation** | Known companies may indicate quality |

**Example:**
```
Ali: 85% overall
Sara: 84% overall
Difference: 1% (within tie-breaker range)

Tie-breaker decision:
"Ali ranks higher because Experience is CRITICAL for this
Senior role, and Ali scores 90% vs Sara's 70% in Experience.
Although Sara has better Skills (95% vs 60%), the JD
emphasizes '5+ years in enterprise environment' which
Ali's Google experience directly matches."
```

---

## Scoring Factors Detail

| Factor | What Gemini Looks For | High Score Indicators |
|--------|----------------------|----------------------|
| **Experience** | Years, relevance, depth | 5+ years in relevant field, progressive responsibility |
| **Projects** | Quality over quantity | Production apps, user scale, measurable impact |
| **Positions** | Career trajectory | Clear growth path, leadership roles, promotions |
| **Skills** | Match + depth | Required skills present + demonstrated proficiency |
| **Education** | Relevance | Degree in field, certifications, continuous learning |

---

## Token Limit Handling

Gemini has token limits. For large candidate pools (100+):

### Strategy: Tiered Summarization

```
If candidates > 50:
  1. Send first 50 candidates with full details
  2. Send remaining as compressed summaries:
     "Candidate 51-100: Similar profiles, avg 2yr exp,
      skills overlap with top 50, no standout factors"
  3. Gemini ranks top 50, flags if any from 51-100 need review
```

### Alternative: Rolling Window

```
For very large pools (200+):
  1. Pre-filter using local scoring (Sentence Transformers)
  2. Send top 75 to Gemini for detailed comparative analysis
  3. Store pre-filter scores for transparency
```

---

## Duplicate Detection

Same candidate applying multiple times:

| Check | Method |
|-------|--------|
| Email match | Exact match on email address |
| Name + Phone | Fuzzy match if email differs |

**Behavior:** Keep latest resume, mark previous as "superseded"

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

pip install flask flask-cors python-dotenv google-generativeai PyMuPDF spacy

# Download spaCy model for NER (name extraction)
python -m spacy download en_core_web_sm

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
| NER | spaCy | 3.x | Name extraction | Local, accurate |
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
│   │   │   │   ├── slider.jsx        # For weight adjustment
│   │   │   │   └── skeleton.jsx
│   │   │   ├── CandidateCard.jsx
│   │   │   ├── DropZone.jsx
│   │   │   ├── StatCard.jsx
│   │   │   ├── ScoreBar.jsx
│   │   │   ├── WeightConfig.jsx      # Weight preferences UI
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
│   │   ├── pdf_parser.py        # PDF text extraction (PyMuPDF)
│   │   ├── local_extractor.py   # Regex + spaCy extraction
│   │   ├── gemini_service.py    # Gemini API integration
│   │   ├── pool_manager.py      # Role-based candidate pool logic
│   │   └── email_service.py     # Gmail SMTP
│   ├── data/
│   │   └── app.db               # SQLite database (auto-created)
│   ├── uploads/                 # Uploaded PDF files
│   ├── requirements.txt         # Python dependencies
│   ├── .env                     # Environment variables (gitignored)
│   └── venv/                    # Virtual environment (gitignored)
│
├── docs/                        # Documentation
│   ├── prd.md
│   ├── architecture.md
│   ├── epics.md
│   └── ux-design-specification.md
│
├── .gitignore
└── README.md
```

---

## FR Category to Architecture Mapping

| FR Category | Frontend | Backend | Database |
|-------------|----------|---------|----------|
| Job & Resume Input (FR1-7) | `HomePage.jsx`, `DropZone.jsx` | `app.py: /api/analyze` | `roles` table |
| AI Analysis (FR8-16) | `DashboardPage.jsx` (loading state) | `gemini_service.py`, `pdf_parser.py`, `local_extractor.py`, `pool_manager.py` | `candidates` table |
| Dashboard Overview (FR17-19) | `DashboardPage.jsx`, `StatCard.jsx` | `app.py: /api/sessions/<id>` | `sessions` table |
| Top Candidates (FR20-24) | `CandidateCard.jsx`, `ScoreBar.jsx` | Response from `/api/analyze` | `candidates` table |
| Transparency (FR25-28) | `CandidateCard.jsx` (WHY section) | Gemini comparative prompt | - |
| Email (FR29-33) | `DashboardPage.jsx` (modal) | `email_service.py`, `app.py: /api/send-emails` | - |
| Session History (FR34-37) | `HistoryPage.jsx` | `app.py: /api/sessions` | `sessions`, `candidates` tables |
| Data Management (FR38-41) | - | `models.py` | All tables |

---

## API Contracts

### Base URL
```
Development: http://localhost:5000/api
```

### Endpoints

#### POST /api/roles
Create or get a role (for candidate pool management).

**Request:**
```json
{
  "title": "Python Developer",
  "weights": {
    "experience": 30,
    "projects": 35,
    "positions": 15,
    "skills": 15,
    "education": 5
  }
}
```

**Response:**
```json
{
  "success": true,
  "role": {
    "id": "uuid-string",
    "title": "Python Developer",
    "normalized_title": "python developer",
    "total_candidates": 45,
    "weights": { ... }
  }
}
```

#### POST /api/analyze
Analyze resumes against a job description.

**Request:**
```json
{
  "role_id": "uuid-string",
  "job_description": "We are looking for...",
  "files": [/* multipart form data - PDF files */],
  "weights": { /* optional, overrides role defaults */ }
}
```

**Response:**
```json
{
  "success": true,
  "session_id": "uuid-string",
  "data": {
    "role": {
      "id": "uuid-string",
      "title": "Python Developer",
      "total_in_pool": 45
    },
    "new_candidates": 10,
    "analysis_time_seconds": 45,
    "overview": {
      "pool_experience_range": "1-8 years",
      "top_skills_in_pool": ["Python", "Django", "FastAPI"],
      "average_match": 72,
      "pool_quality": "Strong pool with 12 highly qualified candidates"
    },
    "top_candidates": [
      {
        "rank": 1,
        "name": "Sara Ahmed",
        "email": "sara@email.com",
        "match_score": 94,
        "scores": {
          "education": 85,
          "experience": 95,
          "projects": 98,
          "positions": 90,
          "skills": 92
        },
        "summary": [
          "4 years Python experience with FastAPI and AWS",
          "Led team of 5 on ML pipeline project",
          "Career progression from Junior to Senior in 3 years"
        ],
        "why_selected": "Strongest project portfolio in the pool. Only candidate with production ML experience matching the job requirements. Clear career growth trajectory.",
        "compared_to_pool": "Outranks 44 other candidates due to superior project impact and leadership experience."
      }
      // ... more candidates
    ],
    "why_not_others": "Remaining 39 candidates scored below 75% match. Common gaps: insufficient project scale, no leadership experience, or missing key skills like FastAPI. 5 candidates were close but lacked production deployment experience."
  }
}
```

#### GET /api/roles/:id/candidates
Get all candidates in a role's pool.

**Response:**
```json
{
  "success": true,
  "role": {
    "id": "uuid-string",
    "title": "Python Developer"
  },
  "candidates": [
    {
      "id": "uuid-string",
      "name": "Sara Ahmed",
      "email": "sara@email.com",
      "match_score": 94,
      "session_id": "uuid-string",
      "uploaded_at": "2025-12-02T10:30:00Z"
    }
    // ... all candidates
  ],
  "total": 45
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
      "role_id": "uuid-string",
      "role_title": "Python Developer",
      "created_at": "2025-12-02T10:30:00Z",
      "candidates_added": 10,
      "pool_size_at_analysis": 45,
      "top_match_score": 94
    }
  ]
}
```

#### GET /api/sessions/:id
Get a specific session's full results.

**Response:** Same structure as POST /api/analyze response.

#### POST /api/send-emails
Send interview invitations to selected candidates.

**Request:**
```json
{
  "session_id": "uuid-string",
  "candidate_emails": ["sara@email.com", "ali@email.com"],
  "message": "Dear {name},\n\nWe would like to invite you for an interview..."
}
```

**Response:**
```json
{
  "success": true,
  "sent": 2,
  "failed": 0,
  "results": [
    {"email": "sara@email.com", "status": "sent"},
    {"email": "ali@email.com", "status": "sent"}
  ]
}
```

#### DELETE /api/candidates/:id
Remove a candidate from the pool (e.g., hired, withdrew).

**Response:**
```json
{
  "success": true,
  "message": "Candidate removed from pool"
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
-- Roles table (for candidate pool grouping)
CREATE TABLE roles (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    normalized_title TEXT NOT NULL,  -- lowercase, trimmed for matching
    weights TEXT,  -- JSON string for scoring weights
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

-- Candidates table (persistent pool per role)
CREATE TABLE candidates (
    id TEXT PRIMARY KEY,
    role_id TEXT NOT NULL,
    session_id TEXT NOT NULL,  -- which session added this candidate

    -- Basic info (extracted locally)
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    resume_text TEXT,

    -- Extracted data (from Gemini Phase 1)
    skills TEXT,           -- JSON array
    experience_years REAL,
    experience_details TEXT,  -- JSON: roles, companies, durations
    education TEXT,        -- JSON: degrees, institutions
    projects TEXT,         -- JSON: project details
    positions TEXT,        -- JSON: position history

    -- Scores (from Gemini Phase 2 comparative analysis)
    rank INTEGER,
    match_score INTEGER,
    education_score INTEGER,
    experience_score INTEGER,
    projects_score INTEGER,
    positions_score INTEGER,
    skills_score INTEGER,

    -- Explanations
    summary TEXT,          -- JSON array of 3 bullet points
    why_selected TEXT,
    compared_to_pool TEXT,

    -- Metadata
    status TEXT DEFAULT 'active',  -- active, hired, withdrew, superseded
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_ranked_at TIMESTAMP,

    FOREIGN KEY (role_id) REFERENCES roles(id),
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);

-- Index for fast pool queries
CREATE INDEX idx_candidates_role ON candidates(role_id, status);
CREATE INDEX idx_candidates_email ON candidates(email);
```

### Data Flow

```
User uploads PDFs + enters job description
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│  PHASE 1: Individual Extraction                         │
├─────────────────────────────────────────────────────────┤
│  For each PDF:                                          │
│    1. PyMuPDF extracts text                             │
│    2. Regex extracts: email, phone                      │
│    3. spaCy NER extracts: name                          │
│    4. Gemini extracts: skills, experience, projects     │
│    5. Store in candidates table                         │
└─────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│  PHASE 2: Comparative Analysis                          │
├─────────────────────────────────────────────────────────┤
│  1. Fetch ALL candidates for this role (current + past) │
│  2. Build candidate pool summary                        │
│  3. Send to Gemini with job description:                │
│     "Rank these candidates against each other"          │
│  4. Gemini returns: ranks, scores, explanations         │
│  5. Update candidates with ranks/scores                 │
└─────────────────────────────────────────────────────────┘
        │
        ▼
   JSON Response to Frontend
```

---

## Gemini Prompt Engineering

### Phase 1 Prompt (Individual Extraction)

```
Extract structured data from this resume text.

Resume Text:
{resume_text}

Return JSON:
{
  "skills": ["Python", "Django", ...],
  "experience_years": 4.5,
  "experience_details": [
    {"role": "Senior Developer", "company": "TechCorp", "duration": "2 years", "highlights": ["Led team", "Built API"]}
  ],
  "education": [
    {"degree": "B.Tech Computer Science", "institution": "IIT Delhi", "year": 2018}
  ],
  "projects": [
    {"name": "E-commerce Platform", "description": "Built for 50K users", "technologies": ["Python", "React"], "impact": "Increased sales 30%"}
  ],
  "positions": [
    {"title": "Junior Developer", "year": 2018},
    {"title": "Mid Developer", "year": 2020},
    {"title": "Senior Developer", "year": 2022}
  ]
}
```

### Phase 2 Prompt (Multi-Level Comparative Ranking)

```
You are an expert HR analyst. Analyze and rank candidates using a 4-level ranking system.

=== JOB DESCRIPTION ===
{job_description}

=== LEVEL 1: INFER PRIORITY DIMENSIONS ===
Analyze the job description and determine priority for each dimension:
- CRITICAL: Must be strong in this area (JD explicitly requires it)
- IMPORTANT: Valuable but not mandatory
- NICE_TO_HAVE: Bonus points
- LOW_PRIORITY: Not mentioned in JD

=== LEVEL 2: MINIMUM THRESHOLDS ===
{thresholds_config}
Eliminate any candidate scoring below these minimums.

=== LEVEL 3: SCORING WEIGHTS ===
- Experience: {experience_weight}%
- Projects: {projects_weight}%
- Positions: {positions_weight}%
- Skills: {skills_weight}%
- Education: {education_weight}%

=== LEVEL 4: TIE-BREAKER RULES ===
When candidates score within 5% of each other:
1. Higher score in CRITICAL dimensions wins
2. Project impact/scale (10K users > 100 users)
3. Career progression speed
4. Leadership indicators
5. Recency of experience

=== CANDIDATE POOL ({total_candidates} candidates) ===
{candidate_summaries}

=== TASK ===

STEP 1: Output your inferred priorities
{
  "inferred_priorities": {
    "experience": "CRITICAL|IMPORTANT|NICE_TO_HAVE|LOW_PRIORITY",
    "skills": "...",
    "projects": "...",
    "positions": "...",
    "education": "..."
  },
  "priority_reasoning": "Why you assigned these priorities based on JD"
}

STEP 2: Apply thresholds and report eliminations
{
  "eliminated_candidates": [
    {"id": "...", "reason": "Experience score 45% < minimum 60%"}
  ],
  "remaining_count": 32
}

STEP 3: Score and rank remaining candidates
For each candidate, score RELATIVE to the pool (not in isolation).
A score of 80% means "better than 80% of this pool in this dimension".

STEP 4: Apply tie-breaker for similar scores
When two candidates are within 5%, explain why one ranks higher.

STEP 5: Return final rankings
{
  "inferred_priorities": { ... },
  "priority_reasoning": "...",
  "eliminated": {
    "count": 13,
    "reasons": {
      "experience_below_threshold": 8,
      "skills_below_threshold": 5
    }
  },
  "rankings": [
    {
      "candidate_id": "...",
      "rank": 1,
      "match_score": 94,
      "scores": {
        "experience": 95,
        "projects": 98,
        "positions": 90,
        "skills": 92,
        "education": 85
      },
      "summary": [
        "5 years Python at Google with microservices",
        "Led team of 5 on ML pipeline serving 100K users",
        "Promoted Junior→Senior in 3 years"
      ],
      "why_selected": "Highest Experience score (CRITICAL for this Senior role). Only candidate with enterprise-scale production experience matching JD requirements.",
      "compared_to_pool": "Outranks 44 candidates. Top 5% in Experience, top 10% in Projects. Leadership experience exceeds 90% of pool.",
      "tie_breaker_applied": false
    },
    {
      "candidate_id": "...",
      "rank": 2,
      "match_score": 93,
      "scores": { ... },
      "summary": [ ... ],
      "why_selected": "...",
      "compared_to_pool": "...",
      "tie_breaker_applied": true,
      "tie_breaker_reason": "Scored 93% vs Candidate C's 92%. Won tie-breaker because Skills (CRITICAL) score of 95% exceeds C's 88%, and project served 50K users vs C's 5K."
    }
  ],
  "why_not_others": "32 candidates ranked. 13 eliminated by thresholds (8 for Experience < 60%, 5 for Skills < 50%). Remaining 26 below top 6 due to: insufficient project scale (15), no leadership experience (8), skills gaps in required tech stack (3)."
}

=== IMPORTANT RULES ===
- Score candidates RELATIVE to each other, not in isolation
- Consider quality over quantity (1 impactful project > 5 trivial ones)
- Account for AI-polished resumes - look for concrete evidence
- CRITICAL dimensions should heavily influence ranking
- Always explain tie-breaker decisions
- Include pool comparison percentages ("top 5% in Experience")
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
- Phase indicators: "Extracting data..." → "Analyzing candidates..."
- Skeleton loaders for data fetching
- Toast notifications for success/error

---

## Consistency Rules

### Date/Time
- Store as ISO 8601 strings in database
- Display in user-friendly format: "Dec 4, 2025"
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

logger.info(f"Phase 1: Extracting data from {len(files)} resumes")
logger.info(f"Phase 2: Comparative analysis for role '{role_title}' with {pool_size} candidates")
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
| Duplicate Detection | Check email before adding to pool |

**Note:** No authentication for MVP (single-user demo). Add auth if deploying publicly.

---

## Performance Considerations

| Concern | Approach |
|---------|----------|
| Large file uploads | Client-side file size validation (max 10MB per file) |
| Many resumes | Batch processing in Phase 1 (10-15 per Gemini call) |
| Large candidate pools | Tiered summarization for 100+ candidates |
| Slow AI analysis | Two-phase progress indicator, batch status updates |
| Database queries | SQLite is fast enough for single-user |
| Token limits | Compress older candidates if pool > 50 |

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

### ADR-007: Two-Phase Analysis Architecture
**Decision:** Split analysis into Phase 1 (individual extraction) and Phase 2 (comparative ranking).
**Rationale:** Enables role-based candidate pools, comparative ranking, and better token management. Local extraction reduces API costs.

### ADR-008: Role-Based Candidate Pools
**Decision:** Persist candidates per role across sessions for comparative analysis.
**Rationale:** Enables fair comparison against historical candidates, detects AI-polished resumes, provides pool-relative scoring. Better hiring decisions through context.

### ADR-009: Local Extraction + Gemini Intelligence
**Decision:** Use regex/spaCy for basic extraction, Gemini only for understanding.
**Rationale:** Reduces API costs, faster processing, API used only where true intelligence is needed. Satisfies requirement to minimize API usage.

---

_Generated by BMAD Decision Architecture Workflow v2.0_
_Date: 2025-12-04_
_For: Uzasch_
_Client: Yoboho Company HR Department_
