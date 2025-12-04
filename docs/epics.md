# TalentLens AI - Epics & Stories

**Date:** 2025-12-04
**Author:** Uzasch
**Version:** 2.1
**Client:** Yoboho Company HR Department

---

## Overview

| Epic | Title | Stories | FRs Covered |
|------|-------|---------|-------------|
| 1 | Foundation | 5 | Infrastructure |
| 2 | Upload & Role Management | 6 | FR1-FR11 |
| 3 | Phase 1: Data Extraction | 4 | FR12-FR18 |
| 4 | Phase 2: Multi-Level Ranking | 7 | FR19-FR33 |
| 5 | Results Dashboard | 8 | FR34-FR51 |
| 6 | Email Candidates | 4 | FR52-FR57 |
| 7 | Session & Pool History | 5 | FR58-FR69 |
| **Total** | | **39 stories** | **69 FRs** |

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
And flask, flask-cors, python-dotenv, google-generativeai, PyMuPDF, spacy are installed
And spaCy model en_core_web_sm is downloaded
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
**So that** roles, sessions, and candidates can be stored.

**Acceptance Criteria:**

```gherkin
Given the backend project is set up
When I initialize the database
Then a roles table is created with columns: id, title, normalized_title, weights, created_at
And a sessions table is created with columns: id, role_id, job_description, candidates_added, pool_size_at_analysis, created_at
And a candidates table is created with all extraction and scoring fields
And foreign key relationships exist between tables
And indexes are created for fast pool queries
And the database file is created at data/app.db
```

**Technical Notes:**
- Use SQLite3 with Python's sqlite3 module
- Create `models.py` with functions for CRUD operations
- Auto-create tables on first run if not exists
- See architecture.md for full schema

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

# Epic 2: Upload & Role Management

**Goal:** User can create/select roles and upload resumes with job description.

**User Value:** Foundation for role-based candidate pools.

**FRs Covered:** FR1-FR11

---

## Story 2.1: Role Selection/Creation

**As a** HR professional,
**I want** to enter or select a role title,
**So that** candidates are grouped into the correct pool.

**Acceptance Criteria:**

```gherkin
Given I am on the Home page
When I view the role input
Then I see an autocomplete input for "Role Title" with placeholder "e.g., Python Developer"
And existing roles appear as suggestions as I type
And I can create a new role by typing a new title
And the system normalizes role titles (e.g., "Python Dev" → "Python Developer")
When I select/create a role
Then it is stored in state for the analysis
```

**Technical Notes:**
- Use shadcn/ui `Combobox` or `Command` for autocomplete
- Call GET /api/roles for suggestions
- Normalize: lowercase, trim, expand common abbreviations
- Store selected role_id or new title in state

**Prerequisites:** Story 1.5
**FRs:** FR1, FR2, FR3

---

## Story 2.2: Job Description Input

**As a** HR professional,
**I want** to enter the job description for this analysis session,
**So that** candidates can be matched against it.

**Acceptance Criteria:**

```gherkin
Given I have selected/created a role
When I view the job description input
Then I see a textarea with placeholder "Paste the full job description here..."
And the textarea is required
And the styling matches Spotify Dark theme
```

**Technical Notes:**
- Use shadcn/ui `Textarea` component
- Store value in React state
- Form is centered, max-width 600px (per UX spec)

**Prerequisites:** Story 2.1
**FRs:** FR4

---

## Story 2.3: Weight Configuration (Optional)

**As a** HR professional,
**I want** to optionally configure scoring weights,
**So that** I can prioritize certain dimensions.

**Acceptance Criteria:**

```gherkin
Given I am on the Home page
When I click "Customize Weights" (collapsed by default)
Then I see 5 sliders for: Experience, Projects, Positions, Skills, Education
And each slider ranges from 0-100
And the total automatically redistributes to equal 100%
And default is 20% each
When I don't customize
Then default weights are used
```

**Technical Notes:**
- Use shadcn/ui `Slider` components
- Create `WeightConfig.jsx` component
- Use `Collapsible` to hide by default
- Store weights in state, pass to API

**Prerequisites:** Story 2.2
**FRs:** FR5, FR6

---

## Story 2.4: File Dropzone Component

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

**Prerequisites:** Story 1.5
**FRs:** FR7, FR8

---

## Story 2.5: File List with Remove

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

**Prerequisites:** Story 2.4
**FRs:** FR9, FR10, FR11

---

## Story 2.6: Roles API

**As a** frontend,
**I want** to manage roles via API,
**So that** candidate pools can be created and fetched.

**Acceptance Criteria:**

```gherkin
Given I call GET /api/roles
Then I receive a list of existing roles with id, title, candidate count
Given I call POST /api/roles with a new title
Then a role is created (or existing returned if normalized title matches)
And the role includes weights if specified
```

**Technical Notes:**
- Normalize title before checking for duplicates
- Return existing role if normalized title matches
- Include candidate count in response

**Prerequisites:** Story 1.3
**FRs:** FR1, FR2, FR3

---

# Epic 3: Phase 1 - Data Extraction

**Goal:** Extract data from resumes using local processing and Gemini.

**User Value:** Prepare candidate data for comparative analysis.

**FRs Covered:** FR12-FR18

---

## Story 3.1: PDF Text Extraction Service

**As a** developer,
**I want** to extract text from PDF files locally,
**So that** resume content can be analyzed.

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
- Handle edge cases: scanned PDFs, corrupted files

**Prerequisites:** Story 1.2
**FRs:** FR12

---

## Story 3.2: Local Data Extraction Service

**As a** developer,
**I want** to extract basic info locally without API,
**So that** API costs are reduced.

**Acceptance Criteria:**

```gherkin
Given resume text is extracted
When local extraction runs
Then email is extracted using regex pattern
And phone is extracted using regex pattern
And candidate name is extracted using spaCy NER
And results are returned as structured data
```

**Technical Notes:**
- Create `services/local_extractor.py`
- Email regex: `[\w.-]+@[\w.-]+\.\w+`
- Phone regex: common patterns (with/without country code)
- Use spaCy `en_core_web_sm` model for NER
- Function: `extract_basic_info(text) -> {name, email, phone}`

**Prerequisites:** Story 1.2
**FRs:** FR13, FR14, FR15

---

## Story 3.3: Gemini Structured Extraction

**As a** developer,
**I want** Gemini to extract structured data from resumes,
**So that** rich candidate profiles are created.

**Acceptance Criteria:**

```gherkin
Given resume text is available
When I call Gemini extraction service
Then it returns structured JSON with:
  - skills (array)
  - experience_years (number)
  - experience_details (array of role objects)
  - education (array of degree objects)
  - projects (array of project objects)
  - positions (array of career progression)
And errors are caught and logged
```

**Technical Notes:**
- Create `services/gemini_service.py`
- Use `gemini-1.5-flash` model
- Create detailed extraction prompt (see architecture.md)
- Parse JSON response from Gemini
- Validate response structure

**Prerequisites:** Story 1.2
**FRs:** FR16

---

## Story 3.4: Candidate Storage and Duplicate Detection

**As a** system,
**I want** to store extracted candidates and detect duplicates,
**So that** the pool remains clean.

**Acceptance Criteria:**

```gherkin
Given extracted data is available for a candidate
When storing to database
Then candidate is linked to correct role
And candidate is linked to current session
When candidate email already exists in pool
Then new resume replaces old (mark old as superseded)
And extraction data is updated
```

**Technical Notes:**
- Check for existing email in role's pool
- Mark previous candidate as `status='superseded'`
- Insert new candidate with `status='active'`
- Store all extracted fields

**Prerequisites:** Story 1.3, Story 3.3
**FRs:** FR17, FR18

---

# Epic 4: Phase 2 - Multi-Level Ranking

**Goal:** Rank all candidates using 4-level intelligent ranking system.

**User Value:** Fair, transparent ranking that understands what the job REALLY needs!

**FRs Covered:** FR19-FR33

---

## Story 4.1: Pool Manager Service

**As a** developer,
**I want** to fetch all active candidates for a role,
**So that** comparative analysis can be performed.

**Acceptance Criteria:**

```gherkin
Given a role_id
When I call the pool manager
Then ALL active candidates for that role are returned
And candidates from current + past sessions are included
And candidates marked as superseded/hired/withdrew are excluded
And candidate summaries are formatted for Gemini prompt
```

**Technical Notes:**
- Create `services/pool_manager.py`
- Query: `SELECT * FROM candidates WHERE role_id=? AND status='active'`
- Format candidates as structured summaries
- Handle token limits (see architecture.md for strategies)

**Prerequisites:** Story 1.3, Story 3.4
**FRs:** FR19, FR20

---

## Story 4.2: Job-Inferred Priority Detection (Level 1)

**As a** system,
**I want** Gemini to analyze the job description and determine dimension priorities,
**So that** ranking focuses on what the job actually needs.

**Acceptance Criteria:**

```gherkin
Given a job description
When Gemini analyzes it
Then it assigns priority to each dimension:
  - CRITICAL: JD explicitly requires this
  - IMPORTANT: Valuable but not mandatory
  - NICE_TO_HAVE: Bonus points
  - LOW_PRIORITY: Not mentioned
And returns reasoning for priority assignments
And these priorities influence ranking decisions
```

**Technical Notes:**
- Extract priority from Gemini response's `inferred_priorities` field
- Store priorities in session for transparency
- Display on dashboard for user understanding

**Prerequisites:** Story 4.1
**FRs:** FR21, FR22

---

## Story 4.3: Threshold Configuration UI

**As a** HR professional,
**I want** to set minimum thresholds for dimensions,
**So that** unqualified candidates are automatically eliminated.

**Acceptance Criteria:**

```gherkin
Given I am on the Home page
When I expand "Advanced Settings"
Then I see threshold inputs for each dimension
And each has: checkbox to enable + slider for minimum (0-100)
And default is all disabled (no thresholds)
When I set Experience threshold to 60%
Then candidates scoring below 60% in Experience will be eliminated
```

**Technical Notes:**
- Add to `WeightConfig.jsx` component
- Store thresholds in state with weights
- Pass to API in analyze request

**Prerequisites:** Story 2.3
**FRs:** FR23

---

## Story 4.4: Threshold Elimination Logic (Level 2)

**As a** system,
**I want** to eliminate candidates below thresholds before ranking,
**So that** only qualified candidates are considered.

**Acceptance Criteria:**

```gherkin
Given thresholds are configured
When Phase 2 ranking runs
Then Gemini first scores all candidates on each dimension
Then candidates below any threshold are eliminated
And elimination reasons are recorded
And remaining candidates proceed to weighted ranking
```

**Technical Notes:**
- Include thresholds in Gemini prompt
- Parse elimination data from response
- Store eliminated count and reasons in session

**Prerequisites:** Story 4.2
**FRs:** FR24, FR25

---

## Story 4.5: Weighted Comparative Scoring (Level 3)

**As a** system,
**I want** Gemini to score candidates relative to the pool,
**So that** scores reflect standing among actual competitors.

**Acceptance Criteria:**

```gherkin
Given remaining candidates after threshold filtering
When Gemini scores them
Then scores are RELATIVE (80% = better than 80% of pool)
And 5-dimension scores are generated
And overall match score uses configured weights
And 3-bullet summaries highlight strengths
```

**Technical Notes:**
- Use weights from request (or defaults)
- Relative scoring instruction in prompt
- Validate score ranges in response

**Prerequisites:** Story 4.4
**FRs:** FR26, FR27, FR28, FR29

---

## Story 4.6: Tie-Breaker Logic (Level 4)

**As a** system,
**I want** Gemini to explain tie-breaker decisions,
**So that** close rankings are transparent.

**Acceptance Criteria:**

```gherkin
Given two candidates score within 5%
When Gemini ranks them
Then it applies tie-breaker rules:
  1. Higher CRITICAL dimension score wins
  2. Project impact/scale
  3. Career progression speed
  4. Leadership indicators
  5. Recency of experience
And explains the tie-breaker decision
And marks candidate as "tie_breaker_applied: true"
```

**Technical Notes:**
- Tie-breaker rules in prompt
- Parse `tie_breaker_applied` and `tie_breaker_reason` from response
- Display on candidate cards

**Prerequisites:** Story 4.5
**FRs:** FR30, FR31, FR32

---

## Story 4.7: Analysis API Endpoint (Full Pipeline)

**As a** frontend,
**I want** to call POST /api/analyze to trigger full multi-level analysis,
**So that** candidates are processed through all 4 levels.

**Acceptance Criteria:**

```gherkin
Given I submit role, job description, files, thresholds, and weights
When I call POST /api/analyze
Then the backend:
  1. Creates/fetches role
  2. Creates session with thresholds config
  3. Phase 1: Extracts data from each PDF
  4. Phase 1: Stores candidates to pool
  5. Phase 2: Fetches full pool
  6. Phase 2 Level 1: Gemini infers priorities from JD
  7. Phase 2 Level 2: Applies thresholds, eliminates candidates
  8. Phase 2 Level 3: Scores remaining candidates with weights
  9. Phase 2 Level 4: Applies tie-breakers for close scores
  10. Stores all results
  11. Returns full response
And progress shows "Extracting..." → "Ranking..." → "Finalizing..."
```

**Technical Notes:**
- Extend analyze endpoint to accept thresholds
- Store inferred_priorities in session
- Store eliminated candidates info
- Return comprehensive response

**Prerequisites:** Story 4.6
**FRs:** FR33 + all Phase 2 FRs

---

# Epic 5: Results Dashboard

**Goal:** User sees ranked candidates with multi-level ranking transparency.

**User Value:** The "wow" moment - see EXACTLY how candidates were ranked!

**FRs Covered:** FR34-FR51

---

## Story 5.1: Dashboard Page Layout with Multi-Level Stats

**As a** HR professional,
**I want** to see comprehensive pool statistics including ranking insights,
**So that** I understand exactly how ranking decisions were made.

**Acceptance Criteria:**

```gherkin
Given analysis is complete and I'm on the Dashboard
When the page loads
Then I see stat cards showing:
  - Total in Pool (e.g., "45 candidates")
  - Added This Session (e.g., "10 new")
  - Eliminated by Thresholds (e.g., "13 eliminated")
  - Remaining Ranked (e.g., "32 candidates")
And I see the role title and job description
And I see inferred priority badges (CRITICAL, IMPORTANT, etc.)
```

**Technical Notes:**
- Create `StatCard.jsx` component
- Fetch data from `/api/sessions/:sessionId`
- Use CSS grid for stat cards
- Show priority badges with color coding

**Prerequisites:** Story 1.5, Story 4.7
**FRs:** FR34, FR35, FR36, FR37, FR38, FR39

---

## Story 5.2: Inferred Priorities Display

**As a** HR professional,
**I want** to see what dimensions Gemini determined as CRITICAL for this job,
**So that** I understand the ranking logic.

**Acceptance Criteria:**

```gherkin
Given I am on the Dashboard
When I view the priorities section
Then I see each dimension with its priority level:
  - Experience: CRITICAL (red badge)
  - Skills: CRITICAL (red badge)
  - Projects: IMPORTANT (orange badge)
  - Positions: NICE_TO_HAVE (gray badge)
  - Education: LOW_PRIORITY (dim gray badge)
And I see reasoning text explaining why
And this section appears above candidate cards
```

**Technical Notes:**
- Create `PriorityBadges.jsx` component
- Color code: CRITICAL=red, IMPORTANT=orange, NICE_TO_HAVE=gray
- Show reasoning in tooltip or expandable section

**Prerequisites:** Story 5.1
**FRs:** FR38

---

## Story 5.3: Candidate Card Component with Priority Labels

**As a** HR professional,
**I want** to see each top candidate with dimension priority indicators,
**So that** I know where they excel in CRITICAL areas.

**Acceptance Criteria:**

```gherkin
Given I am viewing the Dashboard
When I look at the candidate cards
Then each card shows:
  - Rank badge (1-6) in top-left
  - Tie-breaker indicator if applicable (⚖️)
  - Candidate name (bold)
  - Match percentage (large, green)
  - 3-bullet summary
  - Checkbox for email selection
And Card #1 has visual emphasis
And cards have hover effect
```

**Technical Notes:**
- Create `CandidateCard.jsx` component
- Use shadcn/ui `Card` as base
- Add tie-breaker icon when `tie_breaker_applied: true`

**Prerequisites:** Story 5.1
**FRs:** FR40, FR41, FR45, FR46

---

## Story 5.4: 5-Dimension Score Breakdown with Priority Labels

**As a** HR professional,
**I want** to see score breakdown with priority indicators,
**So that** I know which scores matter most for this job.

**Acceptance Criteria:**

```gherkin
Given I am viewing a candidate card
When I look at the scores section
Then I see 5 horizontal progress bars:
  - Experience: [CRITICAL] [bar] 95%
  - Skills: [CRITICAL] [bar] 88%
  - Projects: [IMPORTANT] [bar] 92%
  - Positions: [bar] 85%
  - Education: [bar] 70%
And CRITICAL dimensions are highlighted
And bars use primary green color
And priority labels match inferred priorities
```

**Technical Notes:**
- Create `ScoreBar.jsx` component
- Show priority badge next to CRITICAL/IMPORTANT dimensions
- Highlight CRITICAL bars with border or glow

**Prerequisites:** Story 5.3
**FRs:** FR42, FR43

---

## Story 5.5: Expandable WHY Section with Tie-Breaker

**As a** HR professional,
**I want** to see WHY including tie-breaker reasoning,
**So that** I understand close ranking decisions.

**Acceptance Criteria:**

```gherkin
Given I am viewing a candidate card
When I see the "WHY" section
Then it shows clickable header "WHY #1?"
When I click it
Then it expands to show:
  - why_selected explanation
  - compared_to_pool context
  - If tie_breaker_applied: shows tie-breaker reasoning
And expansion uses smooth animation
```

**Technical Notes:**
- Use shadcn/ui `Collapsible`
- Show tie-breaker section conditionally
- Highlight tie-breaker in different color

**Prerequisites:** Story 5.3
**FRs:** FR44, FR47, FR48

---

## Story 5.6: Eliminated Candidates Section

**As a** HR professional,
**I want** to see which candidates were eliminated by thresholds,
**So that** I have complete transparency.

**Acceptance Criteria:**

```gherkin
Given thresholds were applied
When I view the Dashboard
Then I see "Eliminated by Thresholds" section
And it shows:
  - Total eliminated count
  - Breakdown by reason (e.g., "8: Experience < 60%", "5: Skills < 50%")
  - Collapsible list of eliminated candidate names
And section is collapsible (default collapsed)
```

**Technical Notes:**
- Parse `eliminated` data from API response
- Create `EliminatedSection.jsx` component
- Show as accordion/collapsible

**Prerequisites:** Story 5.1
**FRs:** FR36, FR50

---

## Story 5.7: Why Not Others Section

**As a** HR professional,
**I want** to know why remaining candidates didn't make top 6,
**So that** I have complete transparency.

**Acceptance Criteria:**

```gherkin
Given I am on the Dashboard
When I scroll below the top 6 cards
Then I see "Why Not Others?" section
And it distinguishes between:
  - Eliminated by thresholds (link to section above)
  - Below top 6 after ranking (with common gaps)
And mentions pool context
```

**Technical Notes:**
- Content from `why_not_others` in API response
- Link to eliminated section if applicable

**Prerequisites:** Story 5.6
**FRs:** FR49, FR51

---

## Story 5.8: Dashboard Data Integration

**As a** HR professional,
**I want** the dashboard to load all multi-level ranking data,
**So that** I see the complete analysis.

**Acceptance Criteria:**

```gherkin
Given I navigate to /dashboard/:sessionId
When the page loads
Then it fetches comprehensive data including:
  - inferred_priorities
  - eliminated candidates
  - ranked candidates with tie-breaker info
  - why_not_others
And shows loading skeleton while fetching
And handles errors gracefully
```

**Technical Notes:**
- Extended API response structure
- Show Skeleton components
- Handle 404 response

**Prerequisites:** Story 5.1 through 5.7

---

# Epic 6: Email Candidates

**Goal:** User can send interview invitations to selected candidates.

**User Value:** Take action directly from results!

**FRs Covered:** FR52-FR57

---

## Story 6.1: Email Service Setup

**As a** developer,
**I want** to send emails via Gmail SMTP,
**So that** interview invitations can be delivered.

**Acceptance Criteria:**

```gherkin
Given Gmail credentials are configured in .env
When I call the email service
Then email is sent via Gmail SMTP
And email has proper subject line
And success/failure status is returned
```

**Technical Notes:**
- Create `services/email_service.py`
- Use `smtplib` with Gmail SMTP
- Use App Password for Gmail

**Prerequisites:** Story 1.2
**FRs:** FR55

---

## Story 6.2: Email Selection and Confirmation Modal

**As a** HR professional,
**I want** to select candidates and preview before sending,
**So that** I control who receives emails.

**Acceptance Criteria:**

```gherkin
Given I am on the Dashboard
When I check candidates' checkboxes
And click "Email Selected" button
Then a modal appears showing:
  - Selected recipients (names and emails)
  - Editable message template with {name}, {job_title} placeholders
  - Cancel and Send buttons
```

**Technical Notes:**
- Use shadcn/ui `Dialog` component
- Track selected candidates in state
- Default message template included

**Prerequisites:** Story 5.3
**FRs:** FR52, FR54, FR57

---

## Story 6.3: Send Emails API

**As a** frontend,
**I want** to call POST /api/send-emails,
**So that** emails are sent to selected candidates.

**Acceptance Criteria:**

```gherkin
Given I click "Send Emails" in the modal
When the API is called
Then the backend:
  - Personalizes message for each candidate
  - Sends email to each address
  - Returns status for each
And response includes sent/failed counts
```

**Technical Notes:**
- Replace placeholders in message
- Continue sending even if some fail
- Return detailed results

**Prerequisites:** Story 6.1
**FRs:** FR53

---

## Story 6.4: Email Status Feedback

**As a** HR professional,
**I want** to see the result of sending emails,
**So that** I know if it worked.

**Acceptance Criteria:**

```gherkin
Given emails are sent
When successful
Then success toast appears
When some fail
Then warning toast shows count
When all fail
Then error toast with retry option
```

**Technical Notes:**
- Use shadcn/ui `Toast`
- Disable button during send

**Prerequisites:** Story 6.2, Story 6.3
**FRs:** FR56

---

# Epic 7: Session & Pool History

**Goal:** User can view past sessions and manage candidate pools.

**User Value:** Don't lose work - manage hiring pipeline!

**FRs Covered:** FR58-FR69

---

## Story 7.1: Save Session After Analysis

**As a** system,
**I want** to save analysis results,
**So that** users can revisit them later.

**Acceptance Criteria:**

```gherkin
Given an analysis completes
When results are generated
Then session record is created with role_id, job_description, etc.
And pool_size_at_analysis is recorded
And all candidates remain in pool for future sessions
```

**Technical Notes:**
- This happens in Story 4.4
- Session captures snapshot of pool state

**Prerequisites:** Story 4.7
**FRs:** FR58, FR64, FR65, FR66, FR67, FR68, FR69

---

## Story 7.2: History Page Layout

**As a** HR professional,
**I want** to see past sessions and role pools,
**So that** I can manage hiring pipeline.

**Acceptance Criteria:**

```gherkin
Given I navigate to /history
When the page loads
Then I see two tabs/sections:
  - Sessions: List of past analyses
  - Role Pools: List of roles with candidate counts
And sessions show: role, date, candidates added, pool size at time
And role pools show: title, total candidates, last analyzed
```

**Technical Notes:**
- Create tabs or sections in `HistoryPage.jsx`
- Use shadcn/ui `Tabs` component
- Format dates nicely

**Prerequisites:** Story 1.5
**FRs:** FR59

---

## Story 7.3: Sessions List API

**As a** frontend,
**I want** to fetch past sessions,
**So that** I can display history.

**Acceptance Criteria:**

```gherkin
Given I call GET /api/sessions
Then I receive array of sessions with:
  - id, role_id, role_title
  - created_at
  - candidates_added
  - pool_size_at_analysis
  - top_match_score
  - thresholds_used
  - inferred_priorities
And results sorted by date descending
```

**Technical Notes:**
- Join sessions with roles table
- Get top score from candidates
- Include threshold and priority data

**Prerequisites:** Story 1.3
**FRs:** FR59

---

## Story 7.4: View Role Pool

**As a** HR professional,
**I want** to view all candidates in a role's pool,
**So that** I can see full hiring pipeline.

**Acceptance Criteria:**

```gherkin
Given I click on a role in History
When the pool view loads
Then I see all active candidates for that role
And each shows: name, email, match score, session date
And I can see candidates from all sessions
```

**Technical Notes:**
- Call GET /api/roles/:id/candidates
- Show in table or card grid

**Prerequisites:** Story 7.2
**FRs:** FR61

---

## Story 7.5: View Past Session Dashboard

**As a** HR professional,
**I want** to click on a past session to view its dashboard,
**So that** I can review previous analyses.

**Acceptance Criteria:**

```gherkin
Given I am on History page
When I click on a session
Then I navigate to /dashboard/:sessionId
And Dashboard loads with that session's data
And all data is restored (stats, top candidates, explanations)
```

**Technical Notes:**
- Use React Router navigation
- Dashboard handles loading by sessionId

**Prerequisites:** Story 7.2, Story 5.8
**FRs:** FR60

---

# FR Coverage Matrix

| FR | Description | Epic | Story |
|----|-------------|------|-------|
| FR1 | Role title input | 2 | 2.1 |
| FR2 | Role normalization | 2 | 2.1, 2.6 |
| FR3 | Create/fetch role pool | 2 | 2.1, 2.6 |
| FR4 | Job description input | 2 | 2.2 |
| FR5 | Configure weights | 2 | 2.3 |
| FR6 | Default weights | 2 | 2.3 |
| FR7 | Drag-drop upload | 2 | 2.4 |
| FR8 | PDF format only | 2 | 2.4 |
| FR9 | File count display | 2 | 2.5 |
| FR10 | Remove files | 2 | 2.5 |
| FR11 | Validate files exist | 2 | 2.5 |
| FR12 | PDF text extraction | 3 | 3.1 |
| FR13 | Email extraction (regex) | 3 | 3.2 |
| FR14 | Phone extraction (regex) | 3 | 3.2 |
| FR15 | Name extraction (spaCy) | 3 | 3.2 |
| FR16 | Gemini structured extraction | 3 | 3.3 |
| FR17 | Store extracted data | 3 | 3.4 |
| FR18 | Duplicate detection | 3 | 3.4 |
| FR19 | Fetch all pool candidates | 4 | 4.1 |
| FR20 | Build pool summary | 4 | 4.1 |
| FR21 | Infer priorities from JD | 4 | 4.2 |
| FR22 | Display inferred priorities | 4 | 4.2 |
| FR23 | Configure thresholds | 4 | 4.3 |
| FR24 | Eliminate below threshold | 4 | 4.4 |
| FR25 | Report eliminations | 4 | 4.4 |
| FR26 | 5-dimension scoring | 4 | 4.5 |
| FR27 | Relative scores | 4 | 4.5 |
| FR28 | Weighted match score | 4 | 4.5 |
| FR29 | 3-bullet summary | 4 | 4.5 |
| FR30 | Tie-breaker rules | 4 | 4.6 |
| FR31 | Tie-breaker factors | 4 | 4.6 |
| FR32 | Tie-breaker explanation | 4 | 4.6 |
| FR33 | Store ranks with tie-breaker | 4 | 4.7 |
| FR34 | Display pool total | 5 | 5.1 |
| FR35 | Display session additions | 5 | 5.1 |
| FR36 | Display eliminated count | 5 | 5.1, 5.6 |
| FR37 | Display pool quality | 5 | 5.1 |
| FR38 | Display inferred priorities | 5 | 5.1, 5.2 |
| FR39 | Display job context | 5 | 5.1 |
| FR40 | Top 6 cards | 5 | 5.3 |
| FR41 | Card content | 5 | 5.3 |
| FR42 | 5-dimension score bars | 5 | 5.4 |
| FR43 | Priority labels on scores | 5 | 5.4 |
| FR44 | Expandable WHY | 5 | 5.5 |
| FR45 | Tie-breaker indicator | 5 | 5.3, 5.5 |
| FR46 | Visual ranking | 5 | 5.3 |
| FR47 | WHY explanations | 5 | 5.5 |
| FR48 | Tie-breaker reasoning | 5 | 5.5 |
| FR49 | Why not others | 5 | 5.7 |
| FR50 | Eliminated section | 5 | 5.6 |
| FR51 | Pool context in explanations | 5 | 5.7 |
| FR52 | Candidate selection | 6 | 6.2 |
| FR53 | Send emails | 6 | 6.3 |
| FR54 | Confirmation modal | 6 | 6.2 |
| FR55 | Email content | 6 | 6.1 |
| FR56 | Send status | 6 | 6.4 |
| FR57 | Custom message | 6 | 6.2 |
| FR58 | Save sessions | 7 | 7.1 |
| FR59 | View session list | 7 | 7.2, 7.3 |
| FR60 | View past dashboard | 7 | 7.5 |
| FR61 | View role pool | 7 | 7.4 |
| FR62 | Store roles | 7 | 7.1 |
| FR63 | Store candidates per role | 7 | 7.1 |
| FR64 | Store job descriptions | 7 | 7.1 |
| FR65 | Store thresholds config | 7 | 7.1 |
| FR66 | Store inferred priorities | 7 | 7.1 |
| FR67 | Store analysis results | 7 | 7.1 |
| FR68 | Store resume text | 7 | 7.1 |
| FR69 | Store PDFs | 7 | 7.1 |

**All 69 FRs covered by 39 stories**

---

_Generated by BMAD Epics & Stories Workflow v2.1_
_Date: 2025-12-04_
_For: Uzasch_
_Client: Yoboho Company HR Department_
