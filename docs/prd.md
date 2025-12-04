# TalentLens AI - Product Requirements Document

**Author:** Uzasch
**Date:** 2025-12-04
**Version:** 2.0
**Client:** Yoboho Company HR Department

---

## Executive Summary

An AI-powered resume shortlisting tool that transforms how HR professionals evaluate candidates. Built for the reality that hiring decisions worth lakhs of rupees are made by exhausted reviewers doing 30-second skim reads - with no system that truly understands candidate fit.

**The Core Problem:**
HR professionals face decision fatigue after reviewing 50+ resumes. Current tools (ATS, job portals, spreadsheets) only do keyword matching - they can't distinguish between two candidates who both list "React" when one built production apps for 10K users and the other completed a tutorial. Worse, they can't explain their rankings, leaving HR to justify choices on gut feeling.

**The Solution:**
This tool uses Gemini AI to semantically analyze resumes against job descriptions, surfacing the top candidates with transparent reasoning. What makes this special:

### Key Innovations

| Innovation | How It Works |
|------------|--------------|
| **Two-Phase Analysis** | Phase 1: Extract structured data. Phase 2: Comparative ranking with full context |
| **Role-Based Candidate Pools** | All candidates for a role (current + past sessions) are compared together |
| **Comparative Ranking** | Candidates scored relative to each other, not in isolation |
| **Transparent AI Reasoning** | Explains WHY - not a black box |

### What Makes This Special

**Comparative Analysis** - When two candidates look identical on paper, the system has context of ALL candidates for this role (even from previous sessions). "Rahul ranked #1 because compared to the 45 other Python developers in our pool, his React project served 10K users vs. the pool average of 500 users. Rahul also led a 3-person team; most candidates worked solo."

This is what LinkedIn Recruiter, Greenhouse, and Workable don't do. They process candidates in isolation - this tool *compares across the entire hiring pool*.

---

## Project Classification

**Technical Type:** Web Application (React SPA + Flask API)
**Domain:** General (HR/Recruitment)
**Complexity:** Medium

This is a greenfield college project using modern web technologies. The tech stack is beginner-friendly but demonstrates real-world patterns:
- **Frontend:** React + Tailwind CSS + shadcn/ui components + Recharts for data visualization
- **Theming:** Semantic CSS variables in `index.css` for light/dark mode switching
- **Backend:** Flask (Python) REST API
- **AI Engine:** Google Gemini API for semantic resume analysis
- **Local Processing:** PyMuPDF + Regex + spaCy for extraction
- **Database:** SQLite (zero-config, file-based)
- **Email:** Gmail SMTP for interview invitations

---

## Success Criteria

**For a College Project, success means:**

1. **Working Demo** - The complete flow works end-to-end: Upload resumes → AI analyzes → Dashboard shows ranked candidates with explanations → Email sends
2. **AI Integration Visible** - Gemini API is clearly doing the heavy lifting (semantic analysis, comparative ranking)
3. **The "WHY" is Clear** - For each top candidate, the reasoning compares them to the pool
4. **Role-Based Pools Work** - Candidates from past sessions appear in current rankings
5. **Polished UI** - Clean, professional look using Tailwind CSS and Recharts visualizations
6. **Evaluator Impressed** - Demo can be completed in 5 minutes and the differentiator (comparative analysis) is obvious

**Functional Success Metrics:**

| Metric | Target |
|--------|--------|
| Resume upload | Handles 50+ PDFs via batch processing |
| Analysis time | ~30-45 seconds per batch of 10-15 resumes |
| Candidate pool | Persists across sessions per role |
| Top candidates | Surfaces top 6 candidates ranked against entire pool |
| Score breakdown | Shows 5 dimensions: Education/Experience/Projects/Positions/Skills |
| AI reasoning | Each candidate has comparison to pool |
| Email send | One-click sends interview invite to selected candidates |
| History | Past sessions are saved and viewable |

**The "Wow" Moment:**
When the evaluator uploads 10 new resumes and sees them ranked against 35 candidates from previous sessions with the AI explaining: "This candidate is #3 in our pool of 45 Python developers because their project scale exceeds 80% of the pool" - that's when they understand this isn't just another CRUD app.

---

## Product Scope

### MVP - Minimum Viable Product

The MVP focuses on the core loop: **Upload → Analyze → Dashboard → Email**

| # | Feature | Description |
|---|---------|-------------|
| 1 | **Role Selection/Creation** | Enter role title (e.g., "Python Developer"). System normalizes and creates/fetches pool |
| 2 | **Job Description Input** | Text area to paste/type the JD for this analysis session |
| 3 | **Resume Upload** | Drag & drop multiple PDFs (supports 50+ resumes) |
| 4 | **Two-Phase AI Analysis** | Phase 1: Extract data locally + Gemini. Phase 2: Comparative ranking against full pool |
| 5 | **Dashboard - Pool Overview** | Stats for entire candidate pool (total count, pool quality, skill distribution) |
| 6 | **Dashboard - Top Candidates** | Ranked cards with match %, 3-bullet summary, 5-dimension score breakdown |
| 7 | **Dashboard - WHY Section** | AI explanation comparing each candidate to the pool |
| 8 | **Dashboard - Why Not Others** | Brief note on why remaining candidates didn't make top 6 |
| 9 | **Configurable Weights** | Optional: HR can set weights for each scoring dimension |
| 10 | **One-Click Email** | Send interview invite to selected candidates |
| 11 | **Session History** | View past shortlisting sessions (saved dashboards) |
| 12 | **Pool Management** | View all candidates in a role's pool |

**Screens:** 3 total
1. **Home/Upload** - Role selection + Job details + resume upload + optional weights
2. **Dashboard** - Pool overview, Top candidates, explanations, email button
3. **History** - List of past sessions + Role pools

### Growth Features (Post-MVP)

Features to add if time permits or for future enhancement:

| Feature | Value |
|---------|-------|
| Side-by-side Compare View | Compare up to 5 candidates row-by-row |
| Skills Radar Chart | Visual skill match using radar/spider chart |
| Candidate Detail Page | Full profile with experience timeline |
| Google Calendar Integration | Slot-based scheduling instead of just email |
| Personalized Rejection Emails | AI-generated polite rejection with feedback |
| LinkedIn Profile Import | Pull candidate data from LinkedIn URL |
| Remove Candidate from Pool | Mark as hired, withdrew, or not interested |

### Vision (Future)

If this project grows beyond college:

- **Multi-user SaaS** - Teams, roles, shared candidate pools
- **Video Interview Analysis** - AI analyzes recorded interviews
- **Skill Assessments** - Built-in coding/aptitude tests
- **Hiring Analytics** - Track which candidates accepted, performed well
- **Mobile App** - Review candidates on the go

---

## Web Application Specific Requirements

### Application Type
**Single Page Application (SPA)** - The entire app loads once. When navigating between Upload → Dashboard → History, React swaps components instantly without full page reloads. This makes the app feel fast and smooth.

*How it works:* One `index.html` file + React Router handles all navigation client-side.

### Browser Support

| Browser | Support Level |
|---------|---------------|
| Chrome (latest) | Full - Primary development target |
| Firefox (latest) | Full |
| Safari (latest) | Full |
| Edge (latest) | Full |
| Mobile browsers | Basic responsive support |

*Note: For college demo, modern browsers only. No IE11 or legacy support needed.*

### Responsive Design
- **Desktop-first** - Primary demo will be on laptop/desktop
- **Tablet** - Dashboard should be usable on iPad
- **Mobile** - Basic functionality, not optimized (stretch goal)

### Performance Targets

| Metric | Target |
|--------|--------|
| Initial page load | < 3 seconds |
| File upload response | Immediate feedback (progress bar) |
| API response (per batch) | < 30 seconds |
| Dashboard render | < 1 second after data received |

### SEO Strategy
**Not applicable** - This is a tool, not a content site. No public pages need indexing.

### Accessibility
**Basic level** - Good contrast, keyboard navigation for forms, semantic HTML. Full WCAG compliance is a stretch goal, not MVP.

---

## User Experience Principles

### Visual Personality
**Clean, Professional, Data-Confident** - The UI should feel like a smart assistant, not a cluttered admin panel.

- **UI Library:** shadcn/ui components (built on Radix UI + Tailwind)
- **Theming:** Semantic CSS variables in `index.css` for quick theme switching (Spotify Dark theme)
- **Color Scheme:** #1DB954 primary (green), #121212 background, #282828 cards
- **Typography:** Inter (shadcn default) - modern, readable
- **Cards:** shadcn Card components with consistent styling
- **Data Viz:** Recharts with theme-aware color palette

**Why shadcn/ui:**
- Pre-built accessible components (Button, Card, Dialog, Toast, Slider, etc.)
- Copy-paste into your project - you own the code
- CSS variables make theme switching trivial
- Looks professional out of the box

### Design Philosophy
1. **Information Density Done Right** - Dashboard shows a lot, but organized clearly
2. **Progressive Disclosure** - Overview first, details on demand
3. **Confidence Through Clarity** - Every number has context, every ranking has comparison to pool

### Key Interactions

| Interaction | UX Approach |
|-------------|-------------|
| **Role Selection** | Autocomplete with existing roles, or create new |
| **Weight Config** | Slider for each dimension (optional, collapsible) |
| **Resume Upload** | Drag & drop zone with visual feedback. Show file count, upload progress |
| **Analysis Wait** | Two-phase progress: "Extracting data..." → "Ranking candidates..." |
| **Candidate Cards** | Hover to highlight, click to expand. Match % prominently displayed |
| **Score Breakdown** | Horizontal progress bars for 5 dimensions - instantly scannable |
| **WHY Section** | Expandable panel with comparison to pool |
| **Email Send** | Select candidates → confirmation modal → success toast |
| **History List** | Cards with role title, date, candidate count. Click to view saved dashboard |

### The 3-Screen Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   HOME/UPLOAD   │ ──▶ │    DASHBOARD    │ ──▶ │     HISTORY     │
│                 │     │                 │     │                 │
│ • Role Title    │     │ • Pool Overview │     │ • Past Sessions │
│ • Job Desc      │     │ • Top Candidates│     │ • Role Pools    │
│ • Upload PDFs   │     │ • WHY Sections  │     │ • Click to View │
│ • Weights (opt) │     │ • [Email]       │     │                 │
│ • [Analyze]     │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## Functional Requirements

*These define WHAT the system can do. Each FR is a testable capability.*

---

### Role & Job Input

- **FR1:** User can enter/select a role title for the position being filled
- **FR2:** System normalizes role titles (e.g., "Python Dev" → "Python Developer")
- **FR3:** System creates new role pool or fetches existing pool based on normalized title
- **FR4:** User can enter/paste a job description for the current analysis session
- **FR5:** User can optionally configure scoring weights for this session (Experience, Projects, Positions, Skills, Education)
- **FR6:** Default weights are equal (20% each) if not specified

---

### Resume Upload

- **FR7:** User can upload multiple resume files via drag-and-drop interface
- **FR8:** System accepts PDF format resumes
- **FR9:** System displays count of uploaded files with file names
- **FR10:** User can remove individual files before submitting
- **FR11:** System validates that at least one resume is uploaded before analysis

---

### Phase 1: Data Extraction

- **FR12:** System extracts text content from PDF resumes using PyMuPDF (local)
- **FR13:** System extracts email from resume text using regex (local)
- **FR14:** System extracts phone from resume text using regex (local)
- **FR15:** System extracts candidate name using spaCy NER (local)
- **FR16:** System sends resume text to Gemini to extract structured data: skills, experience details, education, projects, positions
- **FR17:** System stores extracted data in database for the candidate
- **FR18:** System detects duplicate candidates by email and keeps latest resume

---

### Phase 2: Multi-Level Ranking

#### Level 1: Job-Inferred Priority

- **FR19:** System fetches ALL active candidates for the role (current + past sessions)
- **FR20:** System builds candidate pool summary with extracted data
- **FR21:** Gemini analyzes job description to infer priority for each dimension (CRITICAL/IMPORTANT/NICE_TO_HAVE/LOW_PRIORITY)
- **FR22:** System displays inferred priorities to user for transparency

#### Level 2: Minimum Thresholds

- **FR23:** User can optionally set minimum threshold for any dimension (e.g., Experience ≥ 60%)
- **FR24:** System eliminates candidates scoring below any threshold before ranking
- **FR25:** System reports how many candidates were eliminated and why

#### Level 3: Weighted Scoring

- **FR26:** Gemini evaluates each candidate on 5 dimensions: Education, Experience, Projects, Positions, Skills
- **FR27:** Gemini generates scores RELATIVE to other candidates in the pool
- **FR28:** System calculates overall match score using configured weights
- **FR29:** Gemini generates a 3-bullet summary for each top candidate

#### Level 4: Tie-Breaker Logic

- **FR30:** When candidates score within 5%, system applies tie-breaker rules
- **FR31:** Tie-breaker considers: CRITICAL dimension scores, project scale, career progression, leadership
- **FR32:** System explains tie-breaker reasoning for affected candidates
- **FR33:** System updates candidates in database with ranks, scores, and tie-breaker info

---

### Dashboard - Pool Overview

- **FR34:** Dashboard displays total candidates in role's pool
- **FR35:** Dashboard displays candidates added in this session
- **FR36:** Dashboard displays candidates eliminated by thresholds (with reasons)
- **FR37:** Dashboard displays pool quality summary (experience range, skill distribution)
- **FR38:** Dashboard displays inferred priority dimensions from job description
- **FR39:** Dashboard displays the job title and description for context

---

### Dashboard - Top Candidates

- **FR40:** Dashboard displays the top 6 candidates ranked against entire pool
- **FR41:** Each candidate card shows: name, rank, match percentage, 3-bullet summary
- **FR42:** Each candidate card shows score breakdown bars for all 5 dimensions
- **FR43:** Each candidate card shows dimension priority labels (CRITICAL/IMPORTANT/etc.)
- **FR44:** Each candidate card has expandable section showing AI reasoning (comparison to pool)
- **FR45:** Cards show tie-breaker indicator if ranking was decided by tie-breaker
- **FR46:** Cards are visually ranked (#1 most prominent, descending emphasis)

---

### Transparency & Reasoning

- **FR47:** System explains WHY each top candidate was selected compared to pool
- **FR48:** System explains tie-breaker logic when candidates have similar profiles
- **FR49:** Dashboard includes section explaining why other candidates didn't make top 6
- **FR50:** Dashboard shows eliminated candidates section with threshold failures
- **FR51:** All AI reasoning includes comparison to pool (e.g., "outranks 90% of pool on project scale")

---

### Side-by-Side Comparison

- **FR52:** User can select any 2 candidates from top 6 to compare side-by-side
- **FR53:** Comparison view shows both candidates' scores on all 5 dimensions visually
- **FR54:** Comparison view highlights which candidate is stronger in each dimension
- **FR55:** Comparison view shows Gemini's explanation of WHY one candidate ranks higher
- **FR56:** Comparison explains specific factors: "Rahul's 5yr Google exp > Sara's 3yr startup exp"
- **FR57:** User can close comparison and return to dashboard

---

### Email & Scheduling

- **FR58:** User can select which candidates to email (checkbox on cards)
- **FR59:** User can add interview time slots (date + time) in the email modal
- **FR60:** User can add multiple slots for candidates to choose from
- **FR61:** System displays email confirmation modal with slots and message preview
- **FR62:** Email includes job title, company context, and available interview slots
- **FR63:** System displays success/failure status for each email sent
- **FR64:** User can customize email message before sending

---

### Session History

- **FR65:** System saves each analysis session (role, job description, thresholds, results, timestamp)
- **FR66:** User can view list of past sessions with role title, date, and candidate count
- **FR67:** User can click on a past session to view the saved dashboard
- **FR68:** User can view all candidates in a role's pool (across all sessions)

---

### Data Management

- **FR69:** System stores roles with normalized titles in database
- **FR70:** System stores candidates persistently per role (pool)
- **FR71:** System stores job descriptions per session
- **FR72:** System stores threshold configuration per session
- **FR73:** System stores inferred priorities per session
- **FR74:** System stores candidate analysis results and scores
- **FR75:** System stores extracted resume text for reference
- **FR76:** Uploaded PDF files are stored in local filesystem

---

**Total: 76 Functional Requirements**

---

## Non-Functional Requirements

*Only requirements that matter for a college project demo are included.*

---

### Performance

| Metric | Requirement |
|--------|-------------|
| Initial page load | < 3 seconds on standard connection |
| File upload feedback | Immediate (progress bar appears within 500ms) |
| Phase 1 (extraction) | < 15 seconds for 10-15 resumes |
| Phase 2 (ranking) | < 30 seconds for pool of 50 candidates |
| Dashboard render | < 1 second after data received |
| Navigation between screens | Instant (SPA behavior) |

---

### Security

| Concern | Approach |
|---------|----------|
| API Keys | Gemini API key stored in environment variables, never in code |
| Gmail Credentials | App password in environment variables, not committed to git |
| File Uploads | Only PDF files accepted; basic validation on file type |
| SQL Injection | Use parameterized queries with SQLite |
| CORS | Flask-CORS configured to allow only the React frontend origin |
| Duplicate Detection | Check email before adding to pool |

*Note: User authentication is NOT in MVP scope. This is a single-user demo application.*

---

### Reliability

| Scenario | Handling |
|----------|----------|
| Gemini API fails | Display error message, allow retry |
| PDF parsing fails | Skip problematic file, continue with others, notify user |
| Email send fails | Show which emails failed, allow retry for failed ones |
| Network timeout | Show timeout message with retry option |
| Empty resume text | Flag as "could not extract text", exclude from pool |
| Duplicate candidate | Keep latest resume, mark previous as superseded |

---

### Usability

| Requirement | Implementation |
|-------------|----------------|
| Loading states | Two-phase progress: "Extracting data..." → "Ranking candidates..." |
| Error messages | Human-readable errors, not technical stack traces |
| Empty states | Helpful messages when no data (e.g., "No candidates in pool yet") |
| Responsive feedback | Button states (loading, disabled), toast notifications |

---

### Maintainability

| Aspect | Approach |
|--------|----------|
| Code organization | Separate folders for components, pages, services |
| API structure | RESTful endpoints with consistent naming |
| Environment config | `.env` file for all configuration (API keys, ports) |
| Comments | Key functions documented, complex logic explained |

---

## Summary

| Aspect | Details |
|--------|---------|
| **Project** | TalentLens AI |
| **Client** | Yoboho Company HR Department |
| **Type** | Web Application (React SPA + Flask API) |
| **Core Value** | Comparative AI ranking - compares candidates to entire pool |
| **Key Innovations** | Multi-Level Ranking + Side-by-Side Comparison + Interview Scheduling |
| **Screens** | 3 (Upload → Dashboard → History) |
| **Functional Requirements** | 76 |
| **Tech Stack** | React, Tailwind, shadcn/ui, Recharts, Flask, SQLite, Gemini API, PyMuPDF, spaCy, Gmail SMTP |

### Multi-Level Ranking System

| Level | What It Does |
|-------|--------------|
| **Level 1: Job-Inferred Priority** | Gemini reads JD → marks dimensions as CRITICAL/IMPORTANT/NICE_TO_HAVE |
| **Level 2: Minimum Thresholds** | HR sets minimums → candidates below are eliminated |
| **Level 3: Weighted Scoring** | Apply weights → calculate overall match % |
| **Level 4: Tie-Breaker** | For similar scores → explain subtle differences |

### Additional Key Features

| Feature | What It Does |
|---------|--------------|
| **Side-by-Side Comparison** | Compare any 2 candidates with visual score comparison + AI explanation |
| **Interview Scheduling** | Add date/time slots in email for candidates to choose from |

**The One-Liner:**
An AI-powered resume shortlister that understands what the job REALLY needs, compares candidates head-to-head, and schedules interviews with top picks.

---

_This PRD captures the essence of TalentLens AI - intelligent multi-level ranking that thinks WITH the HR professional._

_Created through collaborative discovery between Uzasch and AI facilitator._
_Generated: 2025-12-04_
_Version: 2.2_
