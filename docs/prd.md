# resume-shortlister - Product Requirements Document

**Author:** Uzasch
**Date:** 2025-11-30
**Version:** 1.0

---

## Executive Summary

An AI-powered resume shortlisting tool that transforms how HR professionals evaluate candidates. Built for the reality that hiring decisions worth lakhs of rupees are made by exhausted reviewers doing 30-second skim reads - with no system that truly understands candidate fit.

**The Core Problem:**
HR professionals face decision fatigue after reviewing 50+ resumes. Current tools (ATS, job portals, spreadsheets) only do keyword matching - they can't distinguish between two candidates who both list "React" when one built production apps for 10K users and the other completed a tutorial. Worse, they can't explain their rankings, leaving HR to justify choices on gut feeling.

**The Solution:**
This tool uses Gemini AI to semantically analyze resumes against job descriptions, surfacing the top 6 candidates with transparent reasoning. For each candidate, HR sees:
- Match score breakdown (Education / Experience / Projects)
- WHY they ranked higher than similar candidates
- Specific tie-breaker logic (project scale, leadership, recency)

### What Makes This Special

**Transparent AI Reasoning** - not a black box. When two candidates look identical on paper, the system explains the difference: "Rahul ranked #1 because his React project served 10K users vs. Amit's 100-user side project. Rahul also led a 3-person team; Amit worked solo."

This is what LinkedIn Recruiter, Greenhouse, and Workable don't do. They process - this tool *thinks with* the HR professional.

---

## Project Classification

**Technical Type:** Web Application (React SPA + Flask API)
**Domain:** General (HR/Recruitment)
**Complexity:** Low

This is a greenfield college project using modern web technologies. The tech stack is beginner-friendly but demonstrates real-world patterns:
- **Frontend:** React + Tailwind CSS + shadcn/ui components + Recharts for data visualization
- **Theming:** Semantic CSS variables in `index.css` for light/dark mode switching
- **Backend:** Flask (Python) REST API
- **AI Engine:** Google Gemini API for semantic resume analysis
- **Database:** SQLite (zero-config, file-based)
- **Email:** Gmail SMTP for interview invitations

---

## Success Criteria

**For a College Project, success means:**

1. **Working Demo** - The complete flow works end-to-end: Upload resumes → AI analyzes → Dashboard shows ranked candidates with explanations → Email sends
2. **AI Integration Visible** - Gemini API is clearly doing the heavy lifting (semantic analysis, not just keyword matching)
3. **The "WHY" is Clear** - For each top candidate, the reasoning is displayed and makes sense
4. **Polished UI** - Clean, professional look using Tailwind CSS and Recharts visualizations
5. **Evaluator Impressed** - Demo can be completed in 5 minutes and the differentiator (transparency) is obvious

**Functional Success Metrics:**

| Metric | Target |
|--------|--------|
| Resume upload | Handles 50+ PDFs via batch processing |
| Analysis time | ~30 seconds per batch of 10-15 resumes |
| Top candidates | Surfaces exactly 6 candidates with rankings |
| Match breakdown | Shows Education/Experience/Projects scores |
| AI reasoning | Each candidate has 2-3 sentence explanation |
| Email send | One-click sends interview invite to all Top 6 |
| History | Past sessions are saved and viewable |

**The "Wow" Moment:**
When the evaluator sees two candidates with similar skills and the AI explains: "Candidate A ranked higher because their project handled 10K users while Candidate B's was a tutorial project" - that's when they understand this isn't just another CRUD app.

---

## Product Scope

### MVP - Minimum Viable Product

The MVP focuses on the core loop: **Upload → Analyze → Dashboard → Email**

| # | Feature | Description |
|---|---------|-------------|
| 1 | **Resume Upload** | Drag & drop multiple PDFs (supports 50+ resumes) |
| 2 | **Job Description Input** | Text area to paste/type the JD |
| 3 | **AI Analysis with Batch Processing** | Gemini analyzes resumes in batches of 10-15 to handle large volumes and avoid API rate limits. Progress indicator shows "Analyzing batch 2/5..." |
| 4 | **Dashboard - Overview** | Stats for ALL candidates (total count, skill distribution, experience spread) |
| 5 | **Dashboard - Top 6** | Ranked cards with match %, 3-bullet summary, score breakdown bars |
| 6 | **Dashboard - WHY Section** | AI explanation for each top candidate's ranking |
| 7 | **Dashboard - Why Not Others** | Brief note on why remaining candidates didn't make top 6 |
| 8 | **One-Click Email** | Send interview invite to all Top 6 with one button |
| 9 | **Session History** | View past shortlisting sessions (saved dashboards) |

**Screens:** 3 total
1. **Home/Upload** - Job details + resume upload
2. **Dashboard** - All results, Top 6, explanations, email button
3. **History** - List of past sessions with links to saved dashboards

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
- **Theming:** Semantic CSS variables in `index.css` for quick theme switching (light/dark mode ready)
- **Color Scheme:** Blues and whites (trust, professionalism), green for success states, orange for attention/warnings
- **Typography:** Inter (shadcn default) - modern, readable
- **Cards:** shadcn Card components with consistent styling
- **Data Viz:** Recharts with theme-aware color palette

**Why shadcn/ui:**
- Pre-built accessible components (Button, Card, Dialog, Toast, etc.)
- Copy-paste into your project - you own the code
- CSS variables make theme switching trivial
- Looks professional out of the box

### Design Philosophy
1. **Information Density Done Right** - Dashboard shows a lot, but organized clearly
2. **Progressive Disclosure** - Overview first, details on demand
3. **Confidence Through Clarity** - Every number has context, every ranking has reasoning

### Key Interactions

| Interaction | UX Approach |
|-------------|-------------|
| **Resume Upload** | Drag & drop zone with visual feedback. Show file count, upload progress bar |
| **Analysis Wait** | Skeleton loading + "Analyzing batch 2/5..." - user knows system is working |
| **Candidate Cards** | Hover to highlight, click to expand. Match % prominently displayed |
| **Score Breakdown** | Horizontal progress bars for Education/Experience/Projects - instantly scannable |
| **WHY Section** | Expandable panel under each candidate - click to reveal AI reasoning |
| **Email Send** | Single button → confirmation modal → success toast. Minimal friction |
| **History List** | Cards with job title, date, candidate count. Click to view saved dashboard |

### The 3-Screen Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   HOME/UPLOAD   │ ──▶ │    DASHBOARD    │ ──▶ │     HISTORY     │
│                 │     │                 │     │                 │
│ • Job Title     │     │ • Overview Stats│     │ • Past Sessions │
│ • Job Desc      │     │ • Top 6 Cards   │     │ • Click to View │
│ • Upload PDFs   │     │ • WHY Sections  │     │                 │
│ • [Analyze]     │     │ • [Email Top 6] │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## Functional Requirements

*These define WHAT the system can do. Each FR is a testable capability.*

---

### Job & Resume Input

- **FR1:** User can enter a job title for the position being filled
- **FR2:** User can enter/paste a job description (text area, no character limit)
- **FR3:** User can upload multiple resume files via drag-and-drop interface
- **FR4:** System accepts PDF format resumes
- **FR5:** System displays count of uploaded files with file names
- **FR6:** User can remove individual files before submitting
- **FR7:** System validates that at least one resume is uploaded before analysis

---

### AI Analysis & Processing

- **FR8:** System extracts text content from PDF resumes using PyMuPDF
- **FR9:** System processes resumes in batches of 10-15 to handle large volumes
- **FR10:** System displays batch processing progress ("Analyzing batch 2/5...")
- **FR11:** System sends resume text + job description to Gemini API for analysis
- **FR12:** Gemini AI evaluates each candidate on three dimensions: Education, Experience, Projects
- **FR13:** Gemini AI generates a match score (0-100%) for each candidate
- **FR14:** Gemini AI generates a 3-bullet summary for each candidate
- **FR15:** Gemini AI generates reasoning explaining WHY each candidate received their score
- **FR16:** System identifies and ranks the top 6 candidates from all analyzed resumes

---

### Dashboard - Overview Statistics

- **FR17:** Dashboard displays total count of resumes analyzed
- **FR18:** Dashboard displays overall statistics (experience range, skill distribution)
- **FR19:** Dashboard displays the job title and description for context

---

### Dashboard - Top 6 Candidates

- **FR20:** Dashboard displays the top 6 candidates as ranked cards
- **FR21:** Each candidate card shows: name, match percentage, 3-bullet summary
- **FR22:** Each candidate card shows score breakdown bars (Education / Experience / Projects)
- **FR23:** Each candidate card has expandable section showing AI reasoning ("WHY this ranking")
- **FR24:** Cards are visually ranked (#1 most prominent, descending emphasis)

---

### Transparency & Reasoning

- **FR25:** System explains WHY each top candidate was selected over others
- **FR26:** System explains tie-breaker logic when candidates have similar skills (project scale, leadership, recency, etc.)
- **FR27:** Dashboard includes section explaining why other candidates didn't make top 6
- **FR28:** All AI reasoning is displayed in natural language, not just scores

---

### Email & Communication

- **FR29:** User can send interview invitation emails to all top 6 candidates with one click
- **FR30:** System displays email confirmation modal before sending
- **FR31:** Email includes job title, company context, and interview invitation message
- **FR32:** System displays success/failure status for each email sent
- **FR33:** User can customize email message before sending (optional)

---

### Session History

- **FR34:** System saves each analysis session (job + candidates + results)
- **FR35:** User can view list of past sessions with job title, date, and candidate count
- **FR36:** User can click on a past session to view the saved dashboard
- **FR37:** Past sessions are stored locally in SQLite database

---

### Data Management

- **FR38:** System stores job descriptions in database
- **FR39:** System stores candidate analysis results in database
- **FR40:** System stores extracted resume text for reference
- **FR41:** Uploaded PDF files are stored in local filesystem

---

**Total: 41 Functional Requirements**

---

## Non-Functional Requirements

*Only requirements that matter for a college project demo are included.*

---

### Performance

| Metric | Requirement |
|--------|-------------|
| Initial page load | < 3 seconds on standard connection |
| File upload feedback | Immediate (progress bar appears within 500ms) |
| AI analysis per batch | < 30 seconds for 10-15 resumes |
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

*Note: User authentication is NOT in MVP scope. This is a single-user demo application.*

---

### Reliability

| Scenario | Handling |
|----------|----------|
| Gemini API fails | Display error message, allow retry |
| PDF parsing fails | Skip problematic file, continue with others, notify user |
| Email send fails | Show which emails failed, allow retry for failed ones |
| Network timeout | Show timeout message with retry option |
| Empty resume text | Flag as "could not extract text", exclude from ranking |

---

### Usability

| Requirement | Implementation |
|-------------|----------------|
| Loading states | Skeleton loaders and progress indicators for all async operations |
| Error messages | Human-readable errors, not technical stack traces |
| Empty states | Helpful messages when no data (e.g., "No past sessions yet") |
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
| **Project** | AI Resume Shortlister |
| **Type** | Web Application (React SPA + Flask API) |
| **Core Value** | Transparent AI reasoning - explains WHY, not just WHO |
| **Screens** | 3 (Upload → Dashboard → History) |
| **Functional Requirements** | 41 |
| **Tech Stack** | React, Tailwind, shadcn/ui, Recharts, Flask, SQLite, Gemini API, Gmail SMTP |

**The One-Liner:**
An AI-powered resume shortlister that doesn't just rank candidates - it explains its reasoning, solving the black-box problem that plagues every ATS on the market.

---

_This PRD captures the essence of resume-shortlister - transparent AI that thinks WITH the HR professional, not just for them._

_Created through collaborative discovery between Uzasch and AI facilitator._
_Generated: 2025-11-30_
