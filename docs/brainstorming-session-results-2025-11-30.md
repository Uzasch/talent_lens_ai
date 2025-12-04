# Brainstorming Session Results

**Session Date:** 2025-11-30
**Facilitator:** Business Analyst Mary
**Participant:** Uzasch

## Session Start

**Approach:** AI-Recommended Techniques

**Areas to Explore:**
1. User Problems & Pain Points
2. Features & Capabilities
3. Differentiators
4. Technical Approaches
5. UX/UI Design
6. Business Value

**Techniques Selected:**
- Mind Mapping (structured) - Visual ecosystem mapping
- Five Whys (deep) - Root cause analysis for user problems
- Role Playing (collaborative) - Stakeholder perspective exploration
- SCAMPER Method (structured) - Systematic feature innovation
- What If Scenarios (creative) - Breakthrough possibility thinking

## Executive Summary

**Topic:** AI Resume Shortlister - College Project

**Session Goals:** Explore all aspects - User Problems, Features, Differentiators, Technical, UX/UI, Business Value

**Techniques Used:** Five Whys, SCAMPER, Role Playing (HR Persona), Mind Mapping, What If Scenarios

**Total Ideas Generated:** 50+ ideas across 6 areas, refined to 9 MVP features

### Key Themes Identified:

1. **Transparency is the killer feature** - HR needs to know WHY candidates are ranked, especially when skills are similar
2. **Decision fatigue is real** - Current tools don't help, they just dump data
3. **Simple beats complex** - 3 screens can deliver full value
4. **AI explains, not just ranks** - The comparison logic is the differentiator
5. **One-click actions** - Email all Top 6 with one button

## Technique Sessions

### Area 1: User Problems & Pain Points
**Technique Used:** Five Whys + Role Playing (HR Persona: Priya)

**Why Chain:**
1. Going through each resume manually but still not picking the best candidates
2. Root causes:
   - Mental fatigue after ~50 resumes
   - No holistic comparison (one-by-one reading)
   - Keyword hunting vs actual skill assessment
3. Current tools fail because:
   - ATS = fancy keyword filter (rejects "React.js" vs "ReactJS")
   - Spreadsheets = candidates blur together, no memory
   - Job portals = just dump resumes, no intelligence
   - No true comparison capability
4. Stakes are high:
   - Wrong hire = hiring manager blame
   - New hire quits in 3 months
   - Process restarts, performance suffers
   - Great candidates go to competitors
5. **ROOT CAUSE:** Million-rupee decisions based on 30-second skim reads while exhausted. No system that UNDERSTANDS fit and explains WHY.

**Opportunities Identified:**
- AI that comprehends context, not just keywords
- Visual side-by-side candidate comparison
- Smart pre-filtering to reduce decision fatigue
- Match reasoning & transparency ("why this candidate")
- Confidence scoring to reduce fear of missing talent

---

### Area 2: Features & Capabilities
**Technique Used:** SCAMPER Method

**S - Substitute:**
- Reading full resumes → AI-generated candidate summaries
- Manual keyword search → Semantic understanding (Gemini/NLP)
- Static PDF viewing → Interactive candidate cards
- Email scheduling → One-click calendar integration

**C - Combine:**
- Resume parsing + JD analysis = Auto-match percentage
- Candidate ranking + Reasoning = "Why #1" transparency
- Dashboard + Email system = One-click interview invite
- Analytics + Historical data = "Candidates like X worked out"

**A - Adapt (from other domains):**
- Tinder → Quick yes/no/maybe swipe on candidates
- Netflix → "Based on your past hires, consider..."
- Google Maps → Hiring probability score
- Spotify → Candidate shortlists by role/team

**M - Modify/Magnify:**
- Skills radar chart, experience timeline, culture fit meter
- Side-by-side comparison (up to 5 candidates)
- Smart filters: "candidates who could grow into role"
- Handle 500+ resumes via auto-tiering
- Match score breakdown: Skills/Experience/Education %

**P - Put to Other Uses:**
- Internal employee skill inventory
- Internal mobility matching
- Executive hiring pipeline reports
- Talent pool for future openings
- Onboarding meeting scheduler

**E - Eliminate:**
- Manual upload → Auto-import from email/portals
- Full resume reading → 3 bullet AI summary
- Back-and-forth scheduling → Candidate picks slots
- Spreadsheet tracking → Single dashboard
- Culture fit guesswork → AI communication style analysis

**R - Reverse:**
- HR finds → Candidates auto-ranked and presented
- Review then shortlist → Auto-shortlist, review top tier only
- Schedule after selection → Pre-book tentative, one-click confirm
- Silent rejection → Auto-personalized rejection emails
- Linear process → Parallel multi-manager review

**Top Feature Candidates:**
1. AI-generated candidate summaries (3 bullets)
2. Skills radar chart + match breakdown
3. Auto-import from email/portals
4. One-click interview scheduling with slot picker
5. Side-by-side comparison (up to 5)
6. Tiered auto-shortlisting
7. Saved talent pool for future roles

---

### Area 3: Differentiators
**Technique Used:** What If Scenarios + Competitive Analysis

**Competitor Landscape:**
- LinkedIn Recruiter: Search & InMail
- Workday/Greenhouse: ATS, pipeline tracking
- HireVue: Video interviews, basic AI
- Zoho Recruit: Affordable ATS
- Skillate: AI resume parsing
- **Gap:** All still make HR do the hard thinking!

**What If Scenarios → Differentiators:**

1. **Transparent AI Reasoning**
   - "I ranked Rahul #1 because: His React project matches your microservices requirement. His 2-year gap? Freelancing - built 5 client projects. Red flag: No testing experience."
   - Why rare: Most AIs are black boxes

2. **Smart JD Reality Check**
   - "Your JD says 5 years, but your last 3 hires had 2-3 years. Consider expanding?"
   - Why rare: No one questions the job posting

3. **Hidden Gem Detection (Potential Over Credentials)**
   - "No degree but: 500+ GitHub contributions, 3 open source projects, 94% skill match"
   - Why rare: Everyone filters by keywords/degrees

4. **Hiring Intelligence Insights**
   - "Similar candidates had 73% offer acceptance when interviewed within 5 days"
   - Why rare: Predictions, not just processing

5. **Candidate Experience Champion**
   - Auto-personalized rejection with helpful feedback
   - Why rare: Most tools ignore rejected candidates

6. **Speed-to-Interview**
   - One-click scheduling with time slots
   - Why rare: Most require manual back-and-forth

**Selected Differentiators:** ALL ✓

---

### Area 4: Technical Approaches
**Technique Used:** Mind Mapping

**Architecture Components:**

```
RESUME SHORTLISTER - Tech Stack
├── Frontend: React
├── AI/NLP: Gemini API
├── Backend: Flask (Python)
├── Database: SQLite
└── External Services
```

**Selected Stack:**

| Layer | Choice | Reasoning |
|-------|--------|-----------|
| **Frontend** | React | Popular, great ecosystem, employable skill |
| **AI/NLP Engine** | Gemini API | Free tier, powerful, semantic understanding |
| **Backend** | Flask (Python) | Simple, well-documented, Python-native |
| **Database** | SQLite | Zero setup, perfect for college project |
| **Email** | Gmail SMTP | Free, simple integration |
| **Resume Parsing** | PyMuPDF + Gemini | Extract text → Gemini understands |
| **Calendar** | Google Calendar API | Free, slot-based scheduling |
| **File Storage** | Local filesystem | Simple for MVP |

**Gemini API Will Handle:**
- Resume text extraction & understanding
- JD-to-resume semantic matching
- Generate candidate summaries (3 bullets)
- Explain match reasoning (transparency)
- Write personalized rejection emails
- Hidden gem detection
- Skills gap analysis

**Flask API Endpoints Needed:**
- POST /upload-resumes
- POST /job-description
- GET /candidates (ranked list)
- GET /candidate/:id (full analysis)
- POST /shortlist
- POST /schedule-interview
- GET /dashboard/:id
- POST /send-emails

---

### Area 5: UX/UI Design
**Technique Used:** Role Playing + Mind Mapping

**User Flow:**
```
Login → Create Job + JD → Upload Resumes → Dashboard/Ranking → Schedule/Email
                                               ↓
                                    Compare View | Candidate Detail
```

**Key Screens Designed:**

1. **Dashboard (Main)**
   - Active jobs list with status
   - Quick stats: resumes, shortlisted, scheduled
   - One-click access to each job's candidates

2. **Candidate Ranking View**
   - Cards with photo, match %, 3-bullet summary
   - Skills progress bars
   - AI reasoning ("WHY" section)
   - Filter: All/Top 10/Maybe/Rejected
   - Sort by match %

3. **Candidate Detail View**
   - Full profile with contact info
   - Skills radar chart
   - AI analysis: strengths, gaps, insights
   - Experience timeline (visual)
   - Action buttons: Reject/Maybe/Shortlist

4. **Compare View (Side-by-Side)**
   - Up to 5 candidates
   - Row-by-row comparison: exp, skills, leadership
   - AI recommendation for each
   - Quick select buttons

5. **Schedule Interview Modal**
   - Calendar with available slots
   - Multi-slot selection for candidate to choose
   - Email preview (AI-generated)
   - Google Meet link integration
   - One-click send

**Aesthetic Choices:**
- Color Scheme: Clean blues + whites, green (success), orange (attention)
- Typography: Inter or Poppins
- Cards: Rounded corners, subtle shadows, hover effects
- Animations: Smooth transitions, loading skeletons
- Charts: Recharts (React library)
- Icons: Lucide React or Heroicons
- UI Library: Tailwind CSS + shadcn/ui

---

### Area 6: Business Value & Final Scope
**Technique Used:** Simplification + Role Playing

**Simplified MVP - Core Features Only:**

| # | Feature | Description |
|---|---------|-------------|
| 1 | Upload resumes + JD | Input - drag & drop resumes, paste JD |
| 2 | AI Analysis | Gemini analyzes Education + Experience + Projects |
| 3 | Analytics Dashboard | Overview of ALL candidates + Top 6-7 |
| 4 | Transparent Ranking | WHY these candidates, NOT others (even with similar skills) |
| 5 | One-click Email | Send interview invite to all Top 6 |
| 6 | History | View past shortlisting sessions (saved dashboards) |

**Dashboard Must Show:**
1. Overall analysis of ALL resumes (stats, skills spread, experience distribution)
2. Top 6-7 candidates with breakdown (Education/Experience/Projects bars)
3. WHY each top candidate was chosen over similar candidates
4. Why others didn't make the cut
5. One button to email all Top 6

**AI Tie-Breaker Logic (when skills are similar):**
- Open source contributions > personal projects > none
- Production scale (10K users > 100 users)
- Leadership experience > individual contributor
- Exact tech match > similar tech
- Recent experience > old experience
- Certifications > self-learned

**Simple Flow:**
```
Upload → AI Analyzes All → Dashboard (overview + top 6 + why) → Email Top 6
                                         ↓
                              History (saved dashboards)
```

**3-4 Screens Total:**
1. Home/Upload
2. Dashboard (main screen with everything)
3. History (past sessions)

---

## Idea Categorization

### Immediate Opportunities (MVP - Must Have)

1. Resume upload with drag & drop
2. Job description input
3. Gemini API integration for analysis
4. Dashboard with overall stats
5. Top 6-7 ranking with visual breakdown
6. "Why this candidate" AI explanations
7. "Why not others" transparency
8. One-click email to top candidates
9. Save/view past sessions

### Future Innovations (Phase 2)

1. Compare view (side-by-side)
2. Skills radar charts
3. Google Calendar integration
4. Candidate profile photos
5. Personalized rejection emails
6. LinkedIn profile import

### Moonshots (If Project Grows)

1. Video interview AI analysis
2. Built-in skill assessments
3. Multi-company SaaS platform
4. Mobile app for on-the-go review

### Insights and Learnings

1. **Transparency is key** - HR needs to know WHY, not just WHO
2. **Similar skills problem** - The real value is explaining tie-breakers
3. **Keep it simple** - 3-4 screens can do everything needed
4. **One-click actions** - Reduce friction at every step
5. **History matters** - HR wants to reference past decisions

## Action Planning

### Top 3 Priority Ideas

#### #1 Priority: Transparent AI Dashboard

- Rationale: Core differentiator - shows WHY candidates are ranked, handles similar-skills problem
- Next steps: Design Gemini prompts, build React dashboard with Recharts
- Resources needed: Gemini API key, React + Tailwind setup
- Priority: CRITICAL - this IS the product

#### #2 Priority: Smart Resume Analysis

- Rationale: Foundation for everything - AI must understand Education/Experience/Projects
- Next steps: Build Flask API, integrate PyMuPDF + Gemini for parsing
- Resources needed: Sample resumes for testing, Gemini API
- Priority: CRITICAL - enables the dashboard

#### #3 Priority: One-Click Interview Email

- Rationale: Closes the loop - makes the tool actionable, not just informational
- Next steps: Gmail SMTP integration, email template design
- Resources needed: Gmail app password, email templates
- Priority: HIGH - completes the user flow

## Reflection and Follow-up

### What Worked Well

- Five Whys revealed the REAL problem (decision fatigue + no transparency)
- SCAMPER generated practical feature ideas
- Role Playing (HR persona Priya) kept ideas grounded in reality
- Simplification at the end focused the scope perfectly

### Areas for Further Exploration

- Gemini API prompt engineering for accurate resume parsing
- How to handle non-standard resume formats
- Email deliverability (avoiding spam filters)

### Recommended Follow-up

- **Next workflow:** Research (technical deep-dive on Gemini API)
- **Then:** PRD to formalize all requirements

### Questions That Emerged

1. How will Gemini handle resumes in different formats (PDF, DOCX, images)?
2. What's the best prompt structure for comparing similar candidates?
3. How to handle bulk resumes (100+) without hitting API limits?
4. Should there be user authentication or keep it simple for college demo?

---

## Final Summary

**Project:** AI Resume Shortlister

**Core Value:** Transparent AI-powered candidate ranking that explains WHY - not just WHO

**Tech Stack:**
- Frontend: React + Tailwind + Recharts
- Backend: Flask (Python)
- AI: Gemini API
- Database: SQLite
- Email: Gmail SMTP

**MVP Features:**
1. Upload resumes + Job Description
2. AI analyzes all (Education/Experience/Projects)
3. Dashboard: Overall stats + Top 6 + WHY explanations
4. One-click email to Top 6
5. History of past sessions

**Screens:** 3 (Upload → Dashboard → History)

---

_Session facilitated using the BMAD CIS brainstorming framework_
