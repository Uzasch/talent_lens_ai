# Epic Technical Specification: Phase 2 - Multi-Level Ranking

Date: 2025-12-20
Author: Uzasch
Epic ID: 4
Status: Draft

---

## Overview

Epic 4 implements Phase 2 of the two-phase analysis architecture - the Multi-Level Ranking System that comparatively ranks all candidates in a role's pool. This is the core intelligence layer that differentiates TalentLens AI from simple keyword-matching ATS tools.

The ranking system uses 4 levels:
1. **Job-Inferred Priority** - Gemini determines what dimensions matter most for this job
2. **Minimum Thresholds** - Eliminate candidates below configurable minimums
3. **Weighted Scoring** - Score remaining candidates relative to pool
4. **Tie-Breaker Logic** - Explain close ranking decisions

## Objectives and Scope

### In Scope

- Pool Manager service to fetch all active candidates for a role
- Gemini prompt for job-inferred priority detection
- Threshold configuration UI (collapsible, per-dimension)
- Threshold elimination logic
- Weighted comparative scoring
- Tie-breaker logic and explanations
- Full analysis API endpoint orchestrating the pipeline
- Progress tracking during analysis

### Out of Scope

- Dashboard UI (Epic 5)
- Email functionality (Epic 6)
- Session history views (Epic 7)
- Batch optimization for very large pools (100+)

## System Architecture Alignment

This epic implements Phase 2 of the Two-Phase Analysis Architecture:

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 2: Comparative Ranking (All Candidates Together)      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Fetch ALL active candidates for this role from DB          │
│  (Current batch + All past sessions)                        │
│         │                                                    │
│         ▼                                                    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Level 1: Job-Inferred Priority                      │    │
│  │ Gemini reads JD → marks dimensions as CRITICAL/etc. │    │
│  └─────────────────────────────────────────────────────┘    │
│         │                                                    │
│         ▼                                                    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Level 2: Minimum Thresholds                         │    │
│  │ Eliminate candidates below configured minimums      │    │
│  └─────────────────────────────────────────────────────┘    │
│         │                                                    │
│         ▼                                                    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Level 3: Weighted Scoring                           │    │
│  │ Score candidates RELATIVE to pool with weights      │    │
│  └─────────────────────────────────────────────────────┘    │
│         │                                                    │
│         ▼                                                    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Level 4: Tie-Breaker Logic                          │    │
│  │ Explain subtle differences for close scores         │    │
│  └─────────────────────────────────────────────────────┘    │
│         │                                                    │
│         ▼                                                    │
│  Store rankings and update candidates in DB                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

| Architecture Component | Story | Notes |
|------------------------|-------|-------|
| Pool Manager | 4.1 | Fetch all active candidates |
| Job-Inferred Priority | 4.2 | Level 1 - Gemini JD analysis |
| Threshold Config UI | 4.3 | Frontend sliders |
| Threshold Elimination | 4.4 | Level 2 - Filter logic |
| Weighted Scoring | 4.5 | Level 3 - Comparative scoring |
| Tie-Breaker Logic | 4.6 | Level 4 - Close score decisions |
| Analysis API | 4.7 | Full pipeline orchestration |

## Detailed Design

### Services and Modules

| Module | Location | Responsibility | Dependencies |
|--------|----------|----------------|--------------|
| **pool_manager.py** | backend/services/ | Fetch and format candidate pool | models.py |
| **ranking_service.py** | backend/services/ | Multi-level ranking orchestration | gemini_service.py, pool_manager.py |
| **gemini_service.py** | backend/services/ | Extended for ranking prompts | google-generativeai |
| **ThresholdConfig** | frontend/src/components/ | Threshold UI sliders | shadcn/ui |
| **app.py** | backend/ | POST /api/analyze endpoint | All services |

### Data Models and Contracts

**Priority Levels:**
```python
PRIORITY_LEVELS = {
    "CRITICAL": 4,      # Must be strong, JD explicitly requires
    "IMPORTANT": 3,     # Valuable but not mandatory
    "NICE_TO_HAVE": 2,  # Bonus points
    "LOW_PRIORITY": 1   # Not mentioned in JD
}
```

**Threshold Configuration:**
```python
{
    "thresholds": {
        "experience": {"enabled": True, "minimum": 60},
        "skills": {"enabled": True, "minimum": 50},
        "projects": {"enabled": False, "minimum": 0},
        "positions": {"enabled": False, "minimum": 0},
        "education": {"enabled": False, "minimum": 0}
    }
}
```

**Weights Configuration:**
```python
{
    "weights": {
        "experience": 25,
        "projects": 20,
        "positions": 15,
        "skills": 25,
        "education": 15
    }
    # Must sum to 100
}
```

**Gemini Ranking Response:**
```python
{
    "inferred_priorities": {
        "experience": "CRITICAL",
        "skills": "CRITICAL",
        "projects": "IMPORTANT",
        "positions": "NICE_TO_HAVE",
        "education": "LOW_PRIORITY"
    },
    "priority_reasoning": "JD emphasizes 5+ years experience and specific tech stack...",
    "eliminated": {
        "count": 13,
        "candidates": [
            {"id": "...", "name": "...", "reason": "Experience score 45% < minimum 60%"}
        ]
    },
    "rankings": [
        {
            "candidate_id": "uuid-1",
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
            "why_selected": "Highest Experience score (CRITICAL)...",
            "compared_to_pool": "Outranks 44 candidates. Top 5% in Experience...",
            "tie_breaker_applied": False,
            "tie_breaker_reason": None
        }
    ],
    "why_not_others": "32 candidates ranked. 13 eliminated by thresholds..."
}
```

### APIs and Interfaces

**POST /api/analyze**

Request:
```json
{
    "role_title": "Python Developer",
    "job_description": "We are looking for...",
    "weights": {
        "experience": 25,
        "projects": 20,
        "positions": 15,
        "skills": 25,
        "education": 15
    },
    "thresholds": {
        "experience": {"enabled": true, "minimum": 60},
        "skills": {"enabled": true, "minimum": 50}
    },
    "files": ["multipart PDF files"]
}
```

Response:
```json
{
    "success": true,
    "data": {
        "session_id": "uuid",
        "role": {
            "id": "uuid",
            "title": "Python Developer",
            "total_in_pool": 45
        },
        "new_candidates": 10,
        "inferred_priorities": {...},
        "eliminated": {
            "count": 13,
            "reasons": {...}
        },
        "top_candidates": [...],
        "why_not_others": "..."
    }
}
```

**Internal Service Interfaces:**

```python
# pool_manager.py
def get_pool_for_role(role_id: str) -> list[dict]:
    """Get all active candidates for a role."""
    pass

def format_pool_for_gemini(candidates: list, job_description: str) -> str:
    """Format candidate pool for Gemini prompt."""
    pass

# ranking_service.py
def analyze_job_priorities(job_description: str) -> dict:
    """Level 1: Get inferred priorities from JD."""
    pass

def apply_thresholds(candidates: list, thresholds: dict, scores: dict) -> tuple[list, list]:
    """Level 2: Eliminate candidates below thresholds."""
    pass

def rank_candidates(candidates: list, job_description: str, weights: dict, priorities: dict) -> list:
    """Level 3 & 4: Score and rank with tie-breakers."""
    pass

def run_full_analysis(role_id: str, session_id: str, job_description: str,
                      weights: dict, thresholds: dict) -> dict:
    """Orchestrate full multi-level ranking."""
    pass
```

### Workflows and Sequencing

**Story Dependency Flow:**

```
Story 4.1 (Pool Manager) ─────────────────────────────►┐
                                                       │
Story 4.2 (Priority Detection) ────────────────────────┤
                                                       │
Story 4.3 (Threshold UI) ──► Story 4.4 (Elimination) ──┤
                                                       ├──► Story 4.7 (Analysis API)
Story 4.5 (Weighted Scoring) ──────────────────────────┤
                                                       │
Story 4.6 (Tie-Breaker) ───────────────────────────────┘
```

**Development Sequence:**
1. Story 4.1 (Pool Manager) - foundation for all ranking
2. Story 4.2 (Priority Detection) - can parallel with 4.1
3. Story 4.3 (Threshold UI) - frontend, can parallel
4. Story 4.4 (Threshold Elimination) - depends on 4.2
5. Story 4.5 (Weighted Scoring) - depends on 4.4
6. Story 4.6 (Tie-Breaker) - depends on 4.5
7. Story 4.7 (Analysis API) - integrates all above

**Full Analysis Pipeline:**

```
1. User submits: role, JD, files, weights, thresholds
           │
           ▼
2. Create/get role (from Epic 2)
           │
           ▼
3. Create session record
           │
           ▼
4. Phase 1: Extract each PDF (from Epic 3)
   └── Store candidates in pool
           │
           ▼
5. Fetch full pool (current + past sessions)
           │
           ▼
6. Level 1: Gemini analyzes JD → inferred priorities
           │
           ▼
7. Level 2: Apply thresholds → eliminate candidates
           │
           ▼
8. Level 3: Gemini scores remaining → weighted ranking
           │
           ▼
9. Level 4: Apply tie-breakers → final ranking
           │
           ▼
10. Store rankings, update session
           │
           ▼
11. Return comprehensive response
```

## Non-Functional Requirements

### Performance

| Metric | Target | Source |
|--------|--------|--------|
| Pool fetch | < 100ms for 100 candidates | Best practice |
| Priority detection | < 5 seconds | Gemini API |
| Full ranking (50 candidates) | < 30 seconds | PRD target |
| Full ranking (100 candidates) | < 45 seconds | Acceptable |

**Implementation Notes:**
- Single Gemini call for ranking (not per-candidate)
- Pool summary compressed for token efficiency
- Consider chunking for 100+ candidates

### Security

| Requirement | Implementation | Source |
|-------------|----------------|--------|
| API key protection | Environment variables | Architecture |
| Input validation | Validate weights sum to 100 | Business rule |
| SQL injection | Parameterized queries | Standard |

### Reliability/Availability

| Scenario | Handling |
|----------|----------|
| Gemini API timeout | Retry with backoff, then fail gracefully |
| Invalid Gemini response | Parse what's possible, log errors |
| Empty pool | Return early with appropriate message |
| All candidates eliminated | Return empty rankings with explanation |

### Observability

| Signal | Implementation |
|--------|----------------|
| Analysis progress | Log each phase completion |
| Gemini latency | Log request/response times |
| Elimination counts | Log threshold filtering results |
| Ranking completion | Log final candidate count and top score |

## Dependencies and Integrations

### Backend Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| google-generativeai | latest | Gemini API (from Epic 3) |
| Flask | 3.x | API endpoints (from Epic 1) |

### Frontend Components (shadcn/ui)

| Component | Usage | Install Command |
|-----------|-------|-----------------|
| `Slider` | Threshold minimum values | Already installed |
| `Switch` | Enable/disable thresholds | `npx shadcn@latest add switch` |
| `Collapsible` | Hide threshold section | Already installed |

### Database Tables

| Table | Used For |
|-------|----------|
| candidates | Read pool, update scores/ranks |
| sessions | Store analysis results |
| roles | Role lookup |

## Acceptance Criteria (Authoritative)

### Story 4.1: Pool Manager Service
1. **AC4.1.1:** Function fetches ALL active candidates for a role_id
2. **AC4.1.2:** Includes candidates from current + past sessions
3. **AC4.1.3:** Excludes candidates with status superseded/hired/withdrew
4. **AC4.1.4:** Returns formatted summaries suitable for Gemini prompt
5. **AC4.1.5:** Handles empty pool gracefully

### Story 4.2: Job-Inferred Priority Detection (Level 1)
1. **AC4.2.1:** Gemini analyzes job description
2. **AC4.2.2:** Returns priority for each dimension: CRITICAL/IMPORTANT/NICE_TO_HAVE/LOW_PRIORITY
3. **AC4.2.3:** Includes reasoning for priority assignments
4. **AC4.2.4:** Priorities stored in session for dashboard display

### Story 4.3: Threshold Configuration UI
1. **AC4.3.1:** "Advanced Settings" section collapsed by default
2. **AC4.3.2:** Each dimension has: checkbox to enable + slider for minimum (0-100)
3. **AC4.3.3:** Default is all disabled (no thresholds)
4. **AC4.3.4:** Threshold values passed to API in analyze request

### Story 4.4: Threshold Elimination Logic (Level 2)
1. **AC4.4.1:** Gemini first scores all candidates on each dimension
2. **AC4.4.2:** Candidates below any threshold are eliminated
3. **AC4.4.3:** Elimination reasons recorded per candidate
4. **AC4.4.4:** Eliminated count and breakdown returned in response

### Story 4.5: Weighted Comparative Scoring (Level 3)
1. **AC4.5.1:** Scores are RELATIVE to pool (80% = better than 80% of pool)
2. **AC4.5.2:** 5-dimension scores generated for each candidate
3. **AC4.5.3:** Overall match score uses configured weights
4. **AC4.5.4:** 3-bullet summaries generated for top candidates

### Story 4.6: Tie-Breaker Logic (Level 4)
1. **AC4.6.1:** When candidates score within 5%, tie-breaker rules apply
2. **AC4.6.2:** Tie-breaker considers: CRITICAL scores, project scale, career progression
3. **AC4.6.3:** tie_breaker_applied flag set to true for affected candidates
4. **AC4.6.4:** tie_breaker_reason explains the decision

### Story 4.7: Analysis API Endpoint
1. **AC4.7.1:** POST /api/analyze accepts: role, JD, files, weights, thresholds
2. **AC4.7.2:** Orchestrates Phase 1 extraction + Phase 2 ranking
3. **AC4.7.3:** Returns session_id, inferred_priorities, eliminated, top_candidates, why_not_others
4. **AC4.7.4:** Progress trackable (Phase 1 → Phase 2 → Complete)

## Traceability Mapping

| AC | FR | Component | Test Approach |
|----|-------|-----------|---------------|
| AC4.1.1-5 | FR19-FR20 | pool_manager.py | Unit: mock DB |
| AC4.2.1-4 | FR21-FR22 | ranking_service.py | Integration: Gemini |
| AC4.3.1-4 | FR23 | ThresholdConfig.jsx | E2E: UI interaction |
| AC4.4.1-4 | FR24-FR25 | ranking_service.py | Unit: threshold logic |
| AC4.5.1-4 | FR26-FR29 | ranking_service.py | Integration: Gemini |
| AC4.6.1-4 | FR30-FR32 | ranking_service.py | Integration: Gemini |
| AC4.7.1-4 | FR33 | app.py | E2E: full pipeline |

## Risks, Assumptions, Open Questions

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Gemini token limits for large pools | Medium | High | Compress candidate summaries |
| Inconsistent Gemini scoring | Medium | Medium | Validate score ranges |
| Slow analysis for 100+ candidates | Medium | Medium | Show progress, optimize prompt |

### Assumptions

1. Pool size typically 20-50 candidates
2. Gemini returns valid JSON (with retry)
3. Weights and thresholds are optional
4. Top 6 candidates displayed on dashboard

### Open Questions

1. **Q1:** How to handle pools > 100 candidates?
   - **Recommendation:** Compress to summaries, flag for review

2. **Q2:** Should tie-breaker threshold be configurable?
   - **Recommendation:** Keep fixed at 5% for MVP

## Gemini Prompt Templates

### Level 1: Priority Detection Prompt

```
Analyze this job description and determine the priority of each dimension.

JOB DESCRIPTION:
{job_description}

For each dimension, assign a priority:
- CRITICAL: JD explicitly requires this, must be strong
- IMPORTANT: Valuable but not mandatory
- NICE_TO_HAVE: Bonus points
- LOW_PRIORITY: Not mentioned in JD

Return JSON:
{
  "inferred_priorities": {
    "experience": "CRITICAL|IMPORTANT|NICE_TO_HAVE|LOW_PRIORITY",
    "skills": "...",
    "projects": "...",
    "positions": "...",
    "education": "..."
  },
  "reasoning": "Explanation of why you assigned these priorities"
}
```

### Level 2-4: Full Ranking Prompt

```
You are an expert HR analyst. Rank candidates using the multi-level system.

=== JOB DESCRIPTION ===
{job_description}

=== INFERRED PRIORITIES ===
{priorities}

=== THRESHOLDS ===
{thresholds}

=== WEIGHTS ===
{weights}

=== CANDIDATE POOL ({count} candidates) ===
{candidate_summaries}

=== TASK ===

1. Score each candidate on 5 dimensions (0-100, RELATIVE to pool)
2. Eliminate candidates below thresholds
3. Calculate weighted match scores
4. Apply tie-breakers for scores within 5%
5. Return top 6 with explanations

Return JSON with rankings, eliminations, and explanations.
```

## Test Strategy Summary

### Unit Tests (pytest)

- Pool Manager: fetch and format logic
- Threshold elimination logic
- Weight calculation
- Response parsing

### Integration Tests (pytest)

- Full ranking with mock Gemini responses
- Database updates after ranking
- Session creation and updates

### E2E Tests (Playwright)

- Threshold UI configuration
- Full analysis flow (upload → results)
- Progress indicator during analysis

**Test Priority:**
1. Analysis API endpoint (critical path)
2. Pool Manager (foundation)
3. Gemini response parsing
4. Threshold UI

---

_Generated by BMAD BMM Epic Tech Context Workflow_
_Epic: 4 - Phase 2: Multi-Level Ranking_
_Date: 2025-12-20_
