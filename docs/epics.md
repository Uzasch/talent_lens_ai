# Resume Shortlister - Epics & Stories

**Date:** 2025-11-30
**Author:** Uzasch
**Version:** 1.0

---

## Overview

| Epic | Title | Stories | FRs Covered |
|------|-------|---------|-------------|
| 1 | Foundation | 5 | Infrastructure |
| 2 | Upload & Analyze | 7 | FR1-FR16 |
| 3 | Results Dashboard | 6 | FR17-FR28 |
| 4 | Email Candidates | 4 | FR29-FR33 |
| 5 | Session History | 5 | FR34-FR41 |
| **Total** | | **27 stories** | **41 FRs** |

---

# Epic 1: Foundation

**Goal:** Establish project structure, database, and basic infrastructure so all subsequent features can be built.

**User Value:** Necessary foundation for greenfield project.

---

## Story 1.1: Frontend Project Setup

**As a** developer,
**I want** the React frontend project initialized with all dependencies,
**So that** I can start building UI components.

**Acceptance Criteria:**

```gherkin
Given I have Node.js 18+ installed
When I run the setup commands in the frontend directory
Then a Vite + React project is created
And Tailwind CSS is configured with dark theme variables
And shadcn/ui is initialized
And react-router-dom, axios, recharts, react-dropzone, lucide-react are installed
And the project runs on localhost:5173
```

**Technical Notes:**
- Use `npm create vite@latest frontend -- --template react`
- Configure `index.css` with Spotify Dark theme CSS variables (see UX spec)
- Set up folder structure: `components/`, `pages/`, `services/`, `lib/`
- Initialize shadcn/ui with dark theme

**Prerequisites:** None (first story)

---

## Story 1.2: Backend Project Setup

**As a** developer,
**I want** the Flask backend project initialized with all dependencies,
**So that** I can start building API endpoints.

**Acceptance Criteria:**

```gherkin
Given I have Python 3.10+ installed
When I run the setup commands in the backend directory
Then a Flask project is created with virtual environment
And flask, flask-cors, python-dotenv, google-generativeai, PyMuPDF are installed
And the project structure has app.py, config.py, models.py, services/
And .env file is created with placeholder variables
And the server runs on localhost:5000
```

**Technical Notes:**
- Create `requirements.txt` with all dependencies
- Set up `.env` with GEMINI_API_KEY, GMAIL_ADDRESS, GMAIL_APP_PASSWORD
- Configure Flask-CORS to allow localhost:5173
- Create `uploads/` and `data/` directories

**Prerequisites:** None

---

## Story 1.3: Database Schema Setup

**As a** developer,
**I want** the SQLite database schema created,
**So that** sessions and candidates can be stored.

**Acceptance Criteria:**

```gherkin
Given the backend project is set up
When I initialize the database
Then a sessions table is created with columns: id, job_title, job_description, total_analyzed, created_at
And a candidates table is created with columns: id, session_id, rank, name, email, match_score, education_score, experience_score, projects_score, summary, why_selected, resume_text, created_at
And foreign key relationship exists between candidates and sessions
And the database file is created at data/app.db
```

**Technical Notes:**
- Use SQLite3 with Python's sqlite3 module
- Create `models.py` with functions: `init_db()`, `create_session()`, `create_candidate()`, `get_sessions()`, `get_session_by_id()`
- Auto-create tables on first run if not exists

**Prerequisites:** Story 1.2

---

## Story 1.4: API Structure and Health Check

**As a** developer,
**I want** the basic API structure with CORS and health endpoint,
**So that** frontend can communicate with backend.

**Acceptance Criteria:**

```gherkin
Given the backend is running
When I make a GET request to /api/health from localhost:5173
Then I receive a 200 response with {"status": "ok"}
And CORS headers allow the frontend origin
And all API responses follow the standard format: {success: true/false, data/error}
```

**Technical Notes:**
- Configure Flask-CORS for localhost:5173
- Create standard response helpers in `app.py`
- Set up error handlers for 404, 500

**Prerequisites:** Story 1.2

---

## Story 1.5: Frontend Routing and Layout

**As a** user,
**I want** to navigate between the three screens,
**So that** I can access all features of the app.

**Acceptance Criteria:**

```gherkin
Given I open the app in my browser
When the app loads
Then I see the Home/Upload page at route "/"
And I can navigate to Dashboard at route "/dashboard/:sessionId"
And I can navigate to History at route "/history"
And a simple navbar shows navigation links
And the dark theme (Spotify Dark) is applied globally
```

**Technical Notes:**
- Use react-router-dom v6 with BrowserRouter
- Create `Navbar.jsx` component with links
- Apply CSS variables from `index.css`
- Create placeholder pages: `HomePage.jsx`, `DashboardPage.jsx`, `HistoryPage.jsx`

**Prerequisites:** Story 1.1

---

# Epic 2: Upload & Analyze

**Goal:** User can upload resumes with a job description and get AI-powered analysis.

**User Value:** Core functionality - this is why users come to the app!

**FRs Covered:** FR1-FR16

---

## Story 2.1: Job Input Form

**As a** HR professional,
**I want** to enter the job title and description,
**So that** the AI knows what to match candidates against.

**Acceptance Criteria:**

```gherkin
Given I am on the Home page
When I view the form
Then I see a text input for "Job Title" with placeholder "e.g., Senior React Developer"
And I see a textarea for "Job Description" with placeholder "Paste the full job description here..."
And both fields are required
And the form uses shadcn/ui Input and Textarea components
And the styling matches Spotify Dark theme (dark background, light text)
```

**Technical Notes:**
- Use shadcn/ui `Input` and `Textarea` components
- Store values in React state
- Form is centered, max-width 600px (per UX spec - Centered Minimal)

**Prerequisites:** Story 1.5
**FRs:** FR1, FR2

---

## Story 2.2: File Dropzone Component

**As a** HR professional,
**I want** to drag and drop resume files,
**So that** I can quickly upload multiple resumes.

**Acceptance Criteria:**

```gherkin
Given I am on the Home page
When I drag PDF files over the dropzone
Then the dropzone border turns green (#1DB954)
And the background shows a subtle green tint
When I drop the files
Then they are added to the file list
When I click the dropzone
Then a file picker opens filtered to PDF files
And only .pdf files are accepted (others show error toast)
```

**Technical Notes:**
- Use `react-dropzone` library
- Create `DropZone.jsx` component
- Accept only `application/pdf` MIME type
- Show upload icon (Lucide `Upload` or `FileText`)
- Dropzone text: "Drop resumes here" / "or click to browse • PDF files • Up to 50 resumes"

**Prerequisites:** Story 1.5
**FRs:** FR3, FR4

---

## Story 2.3: File List with Remove

**As a** HR professional,
**I want** to see uploaded files and remove unwanted ones,
**So that** I can control which resumes are analyzed.

**Acceptance Criteria:**

```gherkin
Given I have uploaded files
When I view the file list
Then I see each filename displayed
And I see the total count "X files selected"
And each file has an X button to remove it
When I click the X button
Then the file is removed from the list
And the count updates
When all files are removed
Then the dropzone shows the default state again
```

**Technical Notes:**
- Display file list below dropzone
- Use Lucide `X` icon for remove button
- Store files in React state as array
- Show file size in human-readable format (optional)

**Prerequisites:** Story 2.2
**FRs:** FR5, FR6, FR7

---

## Story 2.4: PDF Text Extraction Service

**As a** developer,
**I want** to extract text from PDF files,
**So that** the AI can analyze resume content.

**Acceptance Criteria:**

```gherkin
Given a PDF file is uploaded to the backend
When the extraction service processes it
Then text content is extracted using PyMuPDF
And the extracted text is returned as a string
And if extraction fails, an error is logged and the file is skipped
And the original PDF is saved to uploads/ directory
```

**Technical Notes:**
- Create `services/pdf_parser.py`
- Use `fitz` (PyMuPDF) to extract text
- Function: `extract_text_from_pdf(file_path) -> str`
- Handle edge cases: scanned PDFs (return empty with warning), corrupted files
- Save uploaded PDFs with UUID filenames

**Prerequisites:** Story 1.2
**FRs:** FR8

---

## Story 2.5: Gemini API Integration

**As a** developer,
**I want** to integrate with Gemini API for resume analysis,
**So that** candidates can be scored and ranked.

**Acceptance Criteria:**

```gherkin
Given I have resume text and a job description
When I call the Gemini service
Then it sends a prompt requesting analysis on Education, Experience, Projects
And it returns a structured response with:
  - match_score (0-100)
  - education_score (0-100)
  - experience_score (0-100)
  - projects_score (0-100)
  - summary (3 bullet points)
  - why_selected (explanation text)
  - candidate_name (extracted from resume)
  - candidate_email (extracted from resume)
And errors are caught and logged
```

**Technical Notes:**
- Create `services/gemini_service.py`
- Use `google-generativeai` package
- Model: `gemini-1.5-flash` (fast, good for analysis)
- Create detailed prompt that:
  - Extracts name and email from resume
  - Scores on 3 dimensions
  - Generates 3-bullet summary
  - Explains why this candidate matches or doesn't
- Parse JSON response from Gemini

**Prerequisites:** Story 1.2
**FRs:** FR11, FR12, FR13, FR14, FR15

---

## Story 2.6: Batch Processing with Progress

**As a** HR professional,
**I want** to see analysis progress,
**So that** I know the system is working on large batches.

**Acceptance Criteria:**

```gherkin
Given I submit 50 resumes for analysis
When the backend processes them
Then it processes in batches of 10-15 resumes
And the frontend shows "Analyzing batch 2/5..."
And a progress bar shows overall completion percentage
And if a single resume fails, processing continues with others
When all batches complete
Then I am redirected to the Dashboard with results
```

**Technical Notes:**
- Backend: Process in batches to respect Gemini rate limits
- Frontend: Poll `/api/analyze/status/:jobId` or use simple loading state
- For MVP: Can use simple "Analyzing..." with spinner if polling is complex
- Show skeleton loader while waiting

**Prerequisites:** Story 2.5
**FRs:** FR9, FR10

---

## Story 2.7: Analysis API Endpoint

**As a** frontend,
**I want** to call POST /api/analyze with job details and files,
**So that** the analysis process begins.

**Acceptance Criteria:**

```gherkin
Given I submit the form with job title, description, and PDF files
When I call POST /api/analyze
Then the backend:
  - Saves uploaded PDFs to uploads/
  - Extracts text from each PDF
  - Sends to Gemini API (in batches)
  - Ranks all candidates by match_score
  - Selects top 6 candidates
  - Saves session and candidates to database
  - Returns session_id and full results
And the response includes:
  - session_id
  - total_analyzed count
  - overview stats
  - top_candidates array (6 items)
  - why_not_others explanation
```

**Technical Notes:**
- Use `multipart/form-data` for file upload
- Frontend: Use `FormData` with axios
- Implement ranking logic: sort by match_score descending, take top 6
- Generate `why_not_others` summary using Gemini
- Return structured JSON per API contract in architecture.md

**Prerequisites:** Story 2.4, Story 2.5, Story 2.6, Story 1.3
**FRs:** FR16

---

# Epic 3: Results Dashboard

**Goal:** User sees the analysis results with ranked candidates and transparent explanations.

**User Value:** The "wow" moment - seeing WHY candidates are ranked!

**FRs Covered:** FR17-FR28

---

## Story 3.1: Dashboard Page Layout

**As a** HR professional,
**I want** to see an overview of the analysis,
**So that** I understand the candidate pool at a glance.

**Acceptance Criteria:**

```gherkin
Given analysis is complete and I'm on the Dashboard page
When the page loads
Then I see 4 stat cards at the top:
  - Total Resumes Analyzed (number)
  - Top Candidates (6)
  - Average Match (percentage)
  - Experience Range (e.g., "3-7 yrs")
And I see the job title displayed for context
And the layout is centered (per UX spec)
And stats use the StatCard component with Spotify green accent
```

**Technical Notes:**
- Create `StatCard.jsx` component
- Fetch data from `/api/sessions/:sessionId`
- Use CSS grid for 4-column stat row (responsive: 2x2 on mobile)
- Match score in primary green color (#1DB954)

**Prerequisites:** Story 1.5, Story 2.7
**FRs:** FR17, FR18, FR19

---

## Story 3.2: Candidate Card Component

**As a** HR professional,
**I want** to see each top candidate in a clear card format,
**So that** I can quickly evaluate them.

**Acceptance Criteria:**

```gherkin
Given I am viewing the Dashboard
When I look at the candidate cards
Then I see 6 cards in a 3-column grid (responsive: 1 column mobile)
And each card shows:
  - Rank badge (1-6) in top-left corner
  - Candidate name (bold)
  - Match percentage (large, green)
  - 3-bullet summary
And Card #1 has visual emphasis (slightly larger or highlighted border)
And cards have hover effect (slight lift/shadow)
```

**Technical Notes:**
- Create `CandidateCard.jsx` component
- Use shadcn/ui `Card` as base
- Rank badge: absolute positioned, green circle with white number
- Use Lucide icons if needed
- Apply hover transform: `translateY(-2px)`

**Prerequisites:** Story 3.1
**FRs:** FR20, FR21, FR24

---

## Story 3.3: Score Breakdown Bars

**As a** HR professional,
**I want** to see score breakdown by category,
**So that** I understand where each candidate is strong or weak.

**Acceptance Criteria:**

```gherkin
Given I am viewing a candidate card
When I look at the scores section
Then I see 3 horizontal progress bars:
  - Education: [bar] XX%
  - Experience: [bar] XX%
  - Projects: [bar] XX%
And bars are filled proportionally to the score
And bars use the primary green color
And the background is subtle dark gray
```

**Technical Notes:**
- Create `ScoreBar.jsx` component
- Use shadcn/ui `Progress` or custom div with width percentage
- Labels in muted text color
- Each bar ~6-8px height

**Prerequisites:** Story 3.2
**FRs:** FR22

---

## Story 3.4: Expandable WHY Section

**As a** HR professional,
**I want** to see WHY each candidate was selected,
**So that** I can understand the AI's reasoning.

**Acceptance Criteria:**

```gherkin
Given I am viewing a candidate card
When I see the "WHY" section
Then it shows a clickable header "WHY #1?" (or respective rank)
When I click it
Then it expands to show the full reasoning text
And the reasoning explains specific factors (leadership, project scale, etc.)
When I click again
Then it collapses
And expansion uses smooth animation
```

**Technical Notes:**
- Use shadcn/ui `Collapsible` or simple React state toggle
- WHY section has subtle green background tint
- Use Lucide `ChevronDown`/`ChevronUp` icons
- Initial state: collapsed (to reduce cognitive load)

**Prerequisites:** Story 3.2
**FRs:** FR23, FR25, FR26, FR28

---

## Story 3.5: Why Not Others Section

**As a** HR professional,
**I want** to know why other candidates didn't make the top 6,
**So that** I have complete transparency.

**Acceptance Criteria:**

```gherkin
Given I am on the Dashboard
When I scroll below the top 6 cards
Then I see a section titled "Why Not Others?"
And it shows a summary explaining:
  - How many candidates were not selected (e.g., "41 candidates scored below 75%")
  - Common gaps (e.g., "insufficient React experience", "no leadership background")
And this section is collapsible (default collapsed)
```

**Technical Notes:**
- Place below candidate cards grid
- Use muted text color
- Collapsible with shadcn/ui or simple toggle
- Content comes from `why_not_others` field in API response

**Prerequisites:** Story 3.1
**FRs:** FR27

---

## Story 3.6: Dashboard Data Integration

**As a** HR professional,
**I want** the dashboard to load real data from the API,
**So that** I see actual analysis results.

**Acceptance Criteria:**

```gherkin
Given I navigate to /dashboard/:sessionId
When the page loads
Then it fetches data from GET /api/sessions/:sessionId
And shows loading skeleton while fetching
And populates all components with real data
And handles errors gracefully (toast message, retry option)
When sessionId is invalid
Then shows "Session not found" message with link to History
```

**Technical Notes:**
- Use axios in `services/api.js`
- Create custom hook `useDashboardData(sessionId)` or use useEffect
- Show Skeleton components while loading
- Handle 404 response

**Prerequisites:** Story 3.1, Story 3.2, Story 3.3, Story 3.4, Story 3.5
**FRs:** All FR17-FR28 integration

---

# Epic 4: Email Candidates

**Goal:** User can send interview invitations to top candidates with one click.

**User Value:** Take action directly from the results!

**FRs Covered:** FR29-FR33

---

## Story 4.1: Email Service Setup

**As a** developer,
**I want** to send emails via Gmail SMTP,
**So that** interview invitations can be delivered.

**Acceptance Criteria:**

```gherkin
Given Gmail credentials are configured in .env
When I call the email service with recipient and message
Then an email is sent via Gmail SMTP
And the email has proper subject line (e.g., "Interview Invitation - {Job Title}")
And the email body includes the custom message
And success/failure status is returned
```

**Technical Notes:**
- Create `services/email_service.py`
- Use `smtplib` with Gmail SMTP (smtp.gmail.com:587)
- Use App Password (not regular password) for Gmail
- Function: `send_email(to_email, subject, body) -> bool`
- Handle SMTP exceptions gracefully

**Prerequisites:** Story 1.2
**FRs:** FR31

---

## Story 4.2: Email Confirmation Modal

**As a** HR professional,
**I want** to preview and confirm before sending emails,
**So that** I don't accidentally send messages.

**Acceptance Criteria:**

```gherkin
Given I am on the Dashboard
When I click "Email All Top 6" button
Then a modal dialog appears
And shows list of recipients (6 names and emails)
And shows a default message template with {name} placeholder
And I can edit the message in a textarea
And I see "Cancel" and "Send Emails" buttons
When I click "Cancel"
Then the modal closes without sending
```

**Technical Notes:**
- Use shadcn/ui `Dialog` component
- Default message: "Dear {name},\n\nWe are pleased to invite you for an interview for the {job_title} position..."
- List recipients as checkboxes (optional: allow deselecting some)

**Prerequisites:** Story 3.1
**FRs:** FR30, FR33

---

## Story 4.3: Send Emails API

**As a** frontend,
**I want** to call POST /api/send-emails,
**So that** emails are sent to selected candidates.

**Acceptance Criteria:**

```gherkin
Given I click "Send Emails" in the modal
When the API is called with session_id, candidate_emails, and message
Then the backend:
  - Personalizes message for each candidate (replaces {name})
  - Sends email to each address
  - Returns status for each (sent/failed)
And the response includes:
  - sent count
  - failed count
  - results array with per-email status
```

**Technical Notes:**
- Loop through candidates, send individually
- Replace `{name}` and `{job_title}` placeholders in message
- Log failures but continue sending to others
- Return detailed results

**Prerequisites:** Story 4.1
**FRs:** FR29

---

## Story 4.4: Email Status Feedback

**As a** HR professional,
**I want** to see the result of sending emails,
**So that** I know if it worked.

**Acceptance Criteria:**

```gherkin
Given I click "Send Emails" and the API responds
When emails are sent successfully
Then modal closes
And a success toast appears: "✓ 6 emails sent successfully"
When some emails fail
Then toast shows: "⚠️ 4 sent, 2 failed"
And failed recipients are listed
When all emails fail
Then error toast shows: "✗ Failed to send emails. Please try again."
```

**Technical Notes:**
- Use shadcn/ui `Toast` or simple toast component
- Show loading state on button while sending
- Disable button during send to prevent double-send

**Prerequisites:** Story 4.2, Story 4.3
**FRs:** FR32

---

# Epic 5: Session History

**Goal:** User can view and revisit past analysis sessions.

**User Value:** Don't lose your work - come back anytime!

**FRs Covered:** FR34-FR41

---

## Story 5.1: Save Session After Analysis

**As a** system,
**I want** to save analysis results to the database,
**So that** users can revisit them later.

**Acceptance Criteria:**

```gherkin
Given an analysis completes successfully
When the results are generated
Then a session record is created with job_title, job_description, total_analyzed
And candidate records are created for ALL analyzed candidates (not just top 6)
And the session_id is returned to the frontend
And PDF files remain in uploads/ directory
```

**Technical Notes:**
- This happens in Story 2.7, but ensuring data persistence for all candidates
- Store all candidates with their scores (for potential future "show more" feature)
- Use transactions to ensure atomicity

**Prerequisites:** Story 1.3, Story 2.7
**FRs:** FR34, FR37, FR38, FR39, FR40, FR41

---

## Story 5.2: History Page Layout

**As a** HR professional,
**I want** to see a list of my past analyses,
**So that** I can find and review previous work.

**Acceptance Criteria:**

```gherkin
Given I navigate to /history
When the page loads
Then I see a list of past sessions
And each session shows:
  - Job title
  - Date (formatted: "Nov 30, 2025")
  - Number of candidates analyzed
  - Top match score
And sessions are ordered by date (newest first)
And each session is clickable
When there are no past sessions
Then I see "No past sessions yet" message with link to Home
```

**Technical Notes:**
- Create `HistoryPage.jsx`
- Use shadcn/ui `Card` for each session item
- Format dates with `Intl.DateTimeFormat` or simple string formatting
- Empty state with call-to-action

**Prerequisites:** Story 1.5
**FRs:** FR35

---

## Story 5.3: Sessions List API

**As a** frontend,
**I want** to fetch the list of past sessions,
**So that** I can display them on the History page.

**Acceptance Criteria:**

```gherkin
Given I call GET /api/sessions
When the request completes
Then I receive an array of session objects
And each object includes: id, job_title, created_at, total_candidates, top_match_score
And results are sorted by created_at descending
```

**Technical Notes:**
- Query sessions table with count of candidates per session
- Get top score from candidates table (MAX match_score WHERE session_id)
- Return ISO date strings

**Prerequisites:** Story 1.3
**FRs:** FR35

---

## Story 5.4: View Past Session Dashboard

**As a** HR professional,
**I want** to click on a past session and see its dashboard,
**So that** I can review previous analysis results.

**Acceptance Criteria:**

```gherkin
Given I am on the History page
When I click on a session card
Then I navigate to /dashboard/:sessionId
And the Dashboard loads with that session's data
And all data is restored (stats, top 6 cards, WHY explanations)
```

**Technical Notes:**
- Use React Router's `useNavigate()` or `<Link>`
- Dashboard already handles loading by sessionId (Story 3.6)
- No additional work needed if Dashboard is properly implemented

**Prerequisites:** Story 5.2, Story 3.6
**FRs:** FR36

---

## Story 5.5: Session Detail API

**As a** frontend,
**I want** to fetch full details of a specific session,
**So that** the Dashboard can display complete results.

**Acceptance Criteria:**

```gherkin
Given I call GET /api/sessions/:id
When the session exists
Then I receive the full session data including:
  - job_title, job_description
  - total_analyzed
  - overview stats
  - top_candidates array (top 6 by score)
  - why_not_others text
When the session doesn't exist
Then I receive 404 with error message
```

**Technical Notes:**
- Query session by ID
- Join with candidates table
- Order candidates by match_score DESC, LIMIT 6 for top candidates
- Generate or retrieve why_not_others (may need to store this on session creation)

**Prerequisites:** Story 1.3
**FRs:** FR36

---

# FR Coverage Matrix

| FR | Description | Epic | Story |
|----|-------------|------|-------|
| FR1 | Job title input | 2 | 2.1 |
| FR2 | Job description input | 2 | 2.1 |
| FR3 | Drag-drop upload | 2 | 2.2 |
| FR4 | PDF format only | 2 | 2.2 |
| FR5 | File count display | 2 | 2.3 |
| FR6 | Remove files | 2 | 2.3 |
| FR7 | Validate files exist | 2 | 2.3 |
| FR8 | PDF text extraction | 2 | 2.4 |
| FR9 | Batch processing | 2 | 2.6 |
| FR10 | Progress display | 2 | 2.6 |
| FR11 | Gemini API call | 2 | 2.5 |
| FR12 | 3-dimension scoring | 2 | 2.5 |
| FR13 | Match score | 2 | 2.5 |
| FR14 | 3-bullet summary | 2 | 2.5 |
| FR15 | WHY reasoning | 2 | 2.5 |
| FR16 | Rank top 6 | 2 | 2.7 |
| FR17 | Total count display | 3 | 3.1 |
| FR18 | Overview stats | 3 | 3.1 |
| FR19 | Job context display | 3 | 3.1 |
| FR20 | Top 6 cards | 3 | 3.2 |
| FR21 | Card content | 3 | 3.2 |
| FR22 | Score bars | 3 | 3.3 |
| FR23 | Expandable WHY | 3 | 3.4 |
| FR24 | Visual ranking | 3 | 3.2 |
| FR25 | WHY explanations | 3 | 3.4 |
| FR26 | Tie-breaker logic | 3 | 3.4 |
| FR27 | Why not others | 3 | 3.5 |
| FR28 | Natural language | 3 | 3.4 |
| FR29 | One-click email | 4 | 4.3 |
| FR30 | Confirmation modal | 4 | 4.2 |
| FR31 | Email content | 4 | 4.1 |
| FR32 | Send status | 4 | 4.4 |
| FR33 | Custom message | 4 | 4.2 |
| FR34 | Save sessions | 5 | 5.1 |
| FR35 | View session list | 5 | 5.2, 5.3 |
| FR36 | View past dashboard | 5 | 5.4, 5.5 |
| FR37 | SQLite storage | 5 | 5.1 |
| FR38 | Store job descriptions | 5 | 5.1 |
| FR39 | Store results | 5 | 5.1 |
| FR40 | Store resume text | 5 | 5.1 |
| FR41 | Store PDFs | 5 | 5.1 |

**✅ All 41 FRs covered by stories**

---

_Generated by BMAD Epics & Stories Workflow v1.0_
_Date: 2025-11-30_
_For: Uzasch_
