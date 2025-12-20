# Epic Technical Specification: Results Dashboard

Date: 2025-12-20
Author: Uzasch
Epic ID: 5
Status: Draft

---

## Overview

Epic 5 implements the Results Dashboard - the "wow" moment of TalentLens AI where HR professionals see ranked candidates with complete transparency into the multi-level ranking decisions. This is where the comparative analysis becomes visible and actionable.

The dashboard displays pool statistics, inferred priorities, top 6 candidates with scores and explanations, eliminated candidates, and enables side-by-side comparison of any two candidates.

## Objectives and Scope

### In Scope

- Dashboard page layout with pool statistics
- Inferred priorities display with badges
- Top 6 candidate cards with rank, scores, summaries
- 5-dimension score breakdown with priority labels
- Expandable WHY sections with tie-breaker info
- Eliminated candidates section (collapsible)
- Why Not Others section
- Side-by-side candidate comparison
- Comparison API with AI explanation
- Loading states and error handling

### Out of Scope

- Email functionality (Epic 6)
- Session history navigation (Epic 7)
- Export/download features
- Mobile-optimized views

## System Architecture Alignment

This epic implements the Dashboard screen per UX specification:

```
┌─────────────────────────────────────────────────────────────┐
│                    DASHBOARD PAGE                            │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ Pool: 45 │ │ New: 10  │ │Elim: 13  │ │Ranked: 32│       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
├─────────────────────────────────────────────────────────────┤
│  Inferred Priorities:                                        │
│  [CRITICAL] Experience  [CRITICAL] Skills                   │
│  [IMPORTANT] Projects   [NICE] Positions  [LOW] Education   │
├─────────────────────────────────────────────────────────────┤
│  TOP CANDIDATES                                              │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐│
│  │ #1 Sara Ahmed   │ │ #2 Ali Khan     │ │ #3 John Doe     ││
│  │ 94% Match       │ │ 91% Match ⚖️    │ │ 88% Match       ││
│  │ [Score Bars]    │ │ [Score Bars]    │ │ [Score Bars]    ││
│  │ [WHY Section]   │ │ [WHY Section]   │ │ [WHY Section]   ││
│  └─────────────────┘ └─────────────────┘ └─────────────────┘│
├─────────────────────────────────────────────────────────────┤
│  ▼ Eliminated by Thresholds (13)                            │
│  ▼ Why Not Others?                                          │
└─────────────────────────────────────────────────────────────┘
```

| Architecture Component | Story | Notes |
|------------------------|-------|-------|
| Dashboard Layout | 5.1 | Page structure, stat cards |
| Priority Badges | 5.2 | CRITICAL/IMPORTANT/etc. display |
| Candidate Cards | 5.3 | Rank, name, match %, summary |
| Score Breakdown | 5.4 | 5-dimension bars with labels |
| WHY Section | 5.5 | Expandable explanations |
| Eliminated Section | 5.6 | Collapsible list |
| Why Not Others | 5.7 | Pool context explanation |
| Data Integration | 5.8 | API calls, loading states |
| Comparison Selection | 5.9 | Select 2 candidates |
| Comparison View | 5.10 | Side-by-side modal |
| Comparison API | 5.11 | AI explanation endpoint |

## Detailed Design

### Services and Modules

| Module | Location | Responsibility | Dependencies |
|--------|----------|----------------|--------------|
| **DashboardPage** | frontend/src/pages/ | Main dashboard container | React Router |
| **StatCard** | frontend/src/components/ | Pool statistics display | shadcn/ui Card |
| **PriorityBadges** | frontend/src/components/ | Priority level display | shadcn/ui Badge |
| **CandidateCard** | frontend/src/components/ | Individual candidate display | shadcn/ui Card |
| **ScoreBar** | frontend/src/components/ | Dimension score bars | shadcn/ui Progress |
| **WhySection** | frontend/src/components/ | Expandable explanations | shadcn/ui Collapsible |
| **EliminatedSection** | frontend/src/components/ | Threshold failures | shadcn/ui Accordion |
| **ComparisonModal** | frontend/src/components/ | Side-by-side view | shadcn/ui Dialog |
| **app.py** | backend/ | GET /api/sessions/:id, POST /api/compare | Flask |

### Data Models and Contracts

**Dashboard Data Structure:**
```javascript
{
  session: {
    id: "uuid",
    role_title: "Python Developer",
    job_description: "...",
    created_at: "2025-12-20T10:00:00Z"
  },
  stats: {
    total_in_pool: 45,
    added_this_session: 10,
    eliminated_count: 13,
    ranked_count: 32
  },
  inferred_priorities: {
    experience: "CRITICAL",
    skills: "CRITICAL",
    projects: "IMPORTANT",
    positions: "NICE_TO_HAVE",
    education: "LOW_PRIORITY"
  },
  priority_reasoning: "...",
  top_candidates: [...],
  eliminated: {
    count: 13,
    breakdown: { experience: 8, skills: 5 },
    candidates: [...]
  },
  why_not_others: "..."
}
```

**Candidate Card Data:**
```javascript
{
  id: "uuid",
  rank: 1,
  name: "Sara Ahmed",
  email: "sara@email.com",
  match_score: 94,
  scores: {
    experience: 95,
    skills: 92,
    projects: 98,
    positions: 90,
    education: 85
  },
  summary: [
    "5 years Python at Google",
    "Led team of 5 on ML project",
    "Promoted Junior→Senior in 3 years"
  ],
  why_selected: "...",
  compared_to_pool: "...",
  tie_breaker_applied: false,
  tie_breaker_reason: null
}
```

### APIs and Interfaces

**GET /api/sessions/:id**
```json
{
  "success": true,
  "data": {
    "session": {...},
    "stats": {...},
    "inferred_priorities": {...},
    "top_candidates": [...],
    "eliminated": {...},
    "why_not_others": "..."
  }
}
```

**POST /api/compare**
```json
// Request
{
  "session_id": "uuid",
  "candidate_id_1": "uuid",
  "candidate_id_2": "uuid"
}

// Response
{
  "success": true,
  "data": {
    "candidate_1": {...},
    "candidate_2": {...},
    "dimension_winners": {
      "experience": "candidate_1",
      "skills": "candidate_2",
      ...
    },
    "overall_winner": "candidate_1",
    "explanation": "...",
    "key_differences": [...]
  }
}
```

### Workflows and Sequencing

**Story Dependency Flow:**

```
5.1 (Layout) ──────────────────────────────────────────────►┐
                                                            │
5.2 (Priorities) ──────────────────────────────────────────►┤
                                                            │
5.3 (Cards) ──► 5.4 (Scores) ──► 5.5 (WHY) ────────────────►┼──► 5.8 (Integration)
                                                            │
5.6 (Eliminated) ──────────────────────────────────────────►┤
                                                            │
5.7 (Why Not) ─────────────────────────────────────────────►┘

5.9 (Selection) ──► 5.10 (View) ──► 5.11 (API)
```

**Development Sequence:**
1. Story 5.1 (Layout) - page structure
2. Story 5.2 (Priorities) - can parallel
3. Story 5.3 (Cards) - depends on 5.1
4. Story 5.4 (Scores) - depends on 5.3
5. Story 5.5 (WHY) - depends on 5.3
6. Story 5.6 (Eliminated) - can parallel
7. Story 5.7 (Why Not) - can parallel
8. Story 5.8 (Integration) - depends on all above
9. Story 5.9 (Selection) - depends on 5.3
10. Story 5.10 (View) - depends on 5.9
11. Story 5.11 (API) - can parallel with 5.10

## Non-Functional Requirements

### Performance

| Metric | Target | Source |
|--------|--------|--------|
| Dashboard load | < 1 second after data received | PRD |
| Session API response | < 500ms | Best practice |
| Comparison API | < 3 seconds | Gemini latency |
| Animation smoothness | 60fps | UX quality |

### Security

| Requirement | Implementation |
|-------------|----------------|
| Session access | Validate session_id exists |
| Candidate access | Validate candidates belong to session |

### Reliability

| Scenario | Handling |
|----------|----------|
| Session not found | 404 with friendly message |
| No candidates | Empty state with guidance |
| Comparison API fails | Error toast, retry option |

## Dependencies and Integrations

### Frontend Components (shadcn/ui)

| Component | Usage | Install Command |
|-----------|-------|-----------------|
| `Card` | Candidate cards, stat cards | Already installed |
| `Badge` | Priority labels | `npx shadcn@latest add badge` |
| `Progress` | Score bars | `npx shadcn@latest add progress` |
| `Collapsible` | WHY sections | Already installed |
| `Accordion` | Eliminated section | `npx shadcn@latest add accordion` |
| `Dialog` | Comparison modal | `npx shadcn@latest add dialog` |
| `Skeleton` | Loading states | `npx shadcn@latest add skeleton` |
| `Checkbox` | Email selection | `npx shadcn@latest add checkbox` |

### External Libraries

| Package | Purpose |
|---------|---------|
| lucide-react | Icons (already installed) |
| recharts | Score visualization (already installed) |

## Acceptance Criteria (Authoritative)

### Story 5.1: Dashboard Page Layout
1. **AC5.1.1:** Stat cards show: Total in Pool, Added This Session, Eliminated, Ranked
2. **AC5.1.2:** Role title and job description displayed
3. **AC5.1.3:** Layout uses responsive grid
4. **AC5.1.4:** Loading skeleton shown while fetching

### Story 5.2: Inferred Priorities Display
1. **AC5.2.1:** Each dimension shows priority badge
2. **AC5.2.2:** CRITICAL = red, IMPORTANT = orange, NICE_TO_HAVE = gray, LOW = dim
3. **AC5.2.3:** Reasoning shown in tooltip or expandable
4. **AC5.2.4:** Section appears above candidate cards

### Story 5.3: Candidate Card Component
1. **AC5.3.1:** Rank badge in top-left (#1, #2, etc.)
2. **AC5.3.2:** Tie-breaker icon (⚖️) if applicable
3. **AC5.3.3:** Name, match %, 3-bullet summary displayed
4. **AC5.3.4:** Checkbox for email selection
5. **AC5.3.5:** Card #1 has visual emphasis

### Story 5.4: Score Breakdown
1. **AC5.4.1:** 5 horizontal progress bars
2. **AC5.4.2:** Priority label next to CRITICAL/IMPORTANT bars
3. **AC5.4.3:** CRITICAL bars highlighted
4. **AC5.4.4:** Percentage shown at end of each bar

### Story 5.5: Expandable WHY Section
1. **AC5.5.1:** Clickable header "WHY #1?"
2. **AC5.5.2:** Expands to show why_selected, compared_to_pool
3. **AC5.5.3:** Tie-breaker section if applicable
4. **AC5.5.4:** Smooth expand/collapse animation

### Story 5.6: Eliminated Candidates Section
1. **AC5.6.1:** Shows total eliminated count
2. **AC5.6.2:** Breakdown by reason (e.g., "8: Experience < 60%")
3. **AC5.6.3:** Collapsible list of names
4. **AC5.6.4:** Collapsed by default

### Story 5.7: Why Not Others Section
1. **AC5.7.1:** Shows below top 6 cards
2. **AC5.7.2:** Distinguishes eliminated vs below top 6
3. **AC5.7.3:** Mentions pool context

### Story 5.8: Dashboard Data Integration
1. **AC5.8.1:** Fetches /api/sessions/:id on mount
2. **AC5.8.2:** Shows loading skeleton during fetch
3. **AC5.8.3:** Handles 404 gracefully
4. **AC5.8.4:** All components receive correct data

### Story 5.9: Comparison Selection
1. **AC5.9.1:** "Compare" button on each card
2. **AC5.9.2:** First click selects, shows "selected" state
3. **AC5.9.3:** Second click opens comparison modal
4. **AC5.9.4:** Max 2 candidates selected

### Story 5.10: Comparison View
1. **AC5.10.1:** Side-by-side display of both candidates
2. **AC5.10.2:** All 5 dimension scores compared
3. **AC5.10.3:** Winner highlighted per dimension
4. **AC5.10.4:** Overall winner indicated
5. **AC5.10.5:** Close button returns to dashboard

### Story 5.11: Comparison API
1. **AC5.11.1:** POST /api/compare accepts session_id, candidate_ids
2. **AC5.11.2:** Returns scores, dimension_winners, overall_winner
3. **AC5.11.3:** AI explanation of key differences
4. **AC5.11.4:** References CRITICAL dimensions

## Traceability Mapping

| AC | FR | Component | Test Approach |
|----|-------|-----------|---------------|
| AC5.1.1-4 | FR34-39 | DashboardPage | E2E: page load |
| AC5.2.1-4 | FR38 | PriorityBadges | Unit: render |
| AC5.3.1-5 | FR40-41, FR45-46 | CandidateCard | Unit: props |
| AC5.4.1-4 | FR42-43 | ScoreBar | Unit: render |
| AC5.5.1-4 | FR44, FR47-48 | WhySection | E2E: expand |
| AC5.6.1-4 | FR36, FR50 | EliminatedSection | E2E: toggle |
| AC5.7.1-3 | FR49, FR51 | WhyNotOthers | Unit: render |
| AC5.8.1-4 | - | DashboardPage | Integration: API |
| AC5.9.1-4 | FR52 | CandidateCard | E2E: select |
| AC5.10.1-5 | FR53-54, FR57 | ComparisonModal | E2E: modal |
| AC5.11.1-4 | FR55-56 | app.py | Integration: API |

## Risks, Assumptions, Open Questions

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Complex state management | Medium | Medium | Use React Context |
| Slow comparison API | Low | Low | Show loading state |
| Cluttered UI with all info | Medium | Medium | Progressive disclosure |

### Assumptions

1. Top 6 candidates always displayed (not configurable)
2. Comparison limited to 2 candidates at a time
3. All dashboard data comes from single API call
4. Session ID from URL params

### Open Questions

1. **Q1:** Should comparison allow more than 2 candidates?
   - **Recommendation:** Keep 2 for MVP, clear comparison

2. **Q2:** Cache comparison results?
   - **Recommendation:** No cache, always fresh for MVP

---

_Generated by BMAD BMM Epic Tech Context Workflow_
_Epic: 5 - Results Dashboard_
_Date: 2025-12-20_
