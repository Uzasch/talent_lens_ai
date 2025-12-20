# Story 4.2: Job-Inferred Priority Detection (Level 1)

Status: review

## Story

As a **system**,
I want **Gemini to analyze the job description and determine dimension priorities**,
So that **ranking focuses on what the job actually needs**.

## Acceptance Criteria

1. **AC4.2.1:** Gemini analyzes job description text
2. **AC4.2.2:** Returns priority for each dimension: CRITICAL, IMPORTANT, NICE_TO_HAVE, LOW_PRIORITY
3. **AC4.2.3:** Includes reasoning text explaining priority assignments
4. **AC4.2.4:** Priorities stored in session for dashboard display

## Tasks / Subtasks

- [x] **Task 1: Add priority detection to gemini_service.py** (AC: 4.2.1, 4.2.2)
  - [ ] Add priority detection prompt:
    ```python
    PRIORITY_DETECTION_PROMPT = """Analyze this job description and determine the importance of each dimension for candidate evaluation.

    JOB DESCRIPTION:
    {job_description}

    For each dimension, assign ONE priority level:
    - CRITICAL: The JD explicitly requires this, candidates MUST be strong here
    - IMPORTANT: Valuable and mentioned, but not mandatory
    - NICE_TO_HAVE: Would be a bonus, briefly mentioned or implied
    - LOW_PRIORITY: Not mentioned in the JD at all

    Return ONLY valid JSON (no markdown):
    {{
      "inferred_priorities": {{
        "experience": "CRITICAL|IMPORTANT|NICE_TO_HAVE|LOW_PRIORITY",
        "skills": "CRITICAL|IMPORTANT|NICE_TO_HAVE|LOW_PRIORITY",
        "projects": "CRITICAL|IMPORTANT|NICE_TO_HAVE|LOW_PRIORITY",
        "positions": "CRITICAL|IMPORTANT|NICE_TO_HAVE|LOW_PRIORITY",
        "education": "CRITICAL|IMPORTANT|NICE_TO_HAVE|LOW_PRIORITY"
      }},
      "reasoning": "2-3 sentence explanation of why you assigned these priorities based on the JD"
    }}

    Examples of what to look for:
    - "5+ years experience required" → Experience = CRITICAL
    - "React, Node.js, TypeScript" → Skills = CRITICAL
    - "Team lead experience preferred" → Positions = IMPORTANT
    - "Built scalable systems" → Projects = IMPORTANT
    - "CS degree preferred" → Education = NICE_TO_HAVE
    - No mention of education → Education = LOW_PRIORITY
    """
    ```

- [x] **Task 2: Implement priority detection function** (AC: 4.2.1-4.2.3)
  - [ ] Add function to gemini_service.py:
    ```python
    def detect_job_priorities(job_description: str) -> dict:
        """Analyze JD to determine dimension priorities.

        Args:
            job_description: Full job description text

        Returns:
            Dict with inferred_priorities and reasoning
        """
        default_response = {
            "inferred_priorities": {
                "experience": "IMPORTANT",
                "skills": "IMPORTANT",
                "projects": "IMPORTANT",
                "positions": "IMPORTANT",
                "education": "NICE_TO_HAVE"
            },
            "reasoning": "Default priorities applied - could not analyze JD",
            "detection_error": None
        }

        if not job_description or len(job_description.strip()) < 50:
            default_response["detection_error"] = "Job description too short"
            return default_response

        try:
            model = genai.GenerativeModel(MODEL_NAME)
            prompt = PRIORITY_DETECTION_PROMPT.format(job_description=job_description)

            response = model.generate_content(prompt)
            response_text = response.text.strip()

            # Parse JSON response
            data = parse_gemini_response(response_text)

            # Validate priorities
            valid_levels = {'CRITICAL', 'IMPORTANT', 'NICE_TO_HAVE', 'LOW_PRIORITY'}
            dimensions = ['experience', 'skills', 'projects', 'positions', 'education']

            priorities = data.get('inferred_priorities', {})
            for dim in dimensions:
                if dim not in priorities or priorities[dim] not in valid_levels:
                    priorities[dim] = 'IMPORTANT'  # Default

            return {
                "inferred_priorities": priorities,
                "reasoning": data.get('reasoning', 'Analysis completed'),
                "detection_error": None
            }

        except Exception as e:
            logger.error(f"Priority detection error: {e}")
            default_response["detection_error"] = str(e)
            return default_response
    ```

- [x] **Task 3: Add priority validation helpers**
  - [ ] Add validation functions:
    ```python
    PRIORITY_LEVELS = {
        "CRITICAL": 4,
        "IMPORTANT": 3,
        "NICE_TO_HAVE": 2,
        "LOW_PRIORITY": 1
    }

    def get_priority_weight(priority: str) -> int:
        """Get numeric weight for priority level."""
        return PRIORITY_LEVELS.get(priority, 2)

    def get_critical_dimensions(priorities: dict) -> list:
        """Get list of dimensions marked as CRITICAL."""
        return [dim for dim, level in priorities.items() if level == 'CRITICAL']

    def validate_priorities(priorities: dict) -> dict:
        """Ensure all dimensions have valid priorities."""
        dimensions = ['experience', 'skills', 'projects', 'positions', 'education']
        valid_levels = set(PRIORITY_LEVELS.keys())

        validated = {}
        for dim in dimensions:
            level = priorities.get(dim, 'IMPORTANT')
            validated[dim] = level if level in valid_levels else 'IMPORTANT'

        return validated
    ```

- [x] **Task 4: Add session storage for priorities** (AC: 4.2.4)
  - [ ] Add to models.py:
    ```python
    def update_session_priorities(session_id: str, priorities: dict, reasoning: str) -> None:
        """Store inferred priorities in session."""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE sessions
            SET inferred_priorities = ?, priority_reasoning = ?
            WHERE id = ?
        ''', (json.dumps(priorities), reasoning, session_id))

        conn.commit()
        conn.close()
    ```
  - [ ] Update sessions table schema (if needed):
    ```sql
    ALTER TABLE sessions ADD COLUMN inferred_priorities TEXT;
    ALTER TABLE sessions ADD COLUMN priority_reasoning TEXT;
    ```

- [x] **Task 5: Test priority detection**
  - [ ] Test with senior developer JD:
    ```python
    jd = """
    Senior Python Developer
    Requirements:
    - 5+ years Python experience
    - Strong knowledge of Django/FastAPI
    - Experience leading technical projects
    - CS degree preferred
    """
    result = detect_job_priorities(jd)
    assert result['inferred_priorities']['experience'] == 'CRITICAL'
    assert result['inferred_priorities']['skills'] == 'CRITICAL'
    ```
  - [ ] Test with minimal JD
  - [ ] Test with empty JD (should return defaults)

## Dev Notes

### Architecture Alignment

This story implements Level 1 of the Multi-Level Ranking System:
- **Purpose:** Understand what the job REALLY needs
- **Output:** Priority levels per dimension
- **Usage:** Influences scoring and tie-breaker decisions

### Priority Level Definitions

| Level | Meaning | Example JD Text |
|-------|---------|-----------------|
| CRITICAL | Must have, explicitly required | "5+ years required", "Must know React" |
| IMPORTANT | Valuable, clearly mentioned | "Experience with AWS preferred" |
| NICE_TO_HAVE | Bonus, briefly mentioned | "Familiarity with Docker a plus" |
| LOW_PRIORITY | Not mentioned at all | (absence of education requirements) |

### Example JD Analysis

**JD:**
```
Senior Python Developer
- 5+ years Python experience in enterprise environment
- Strong React, Node.js, TypeScript skills
- Led technical teams of 3+ developers
- Built systems serving 10K+ users
- CS degree preferred
```

**Expected Output:**
```json
{
  "inferred_priorities": {
    "experience": "CRITICAL",
    "skills": "CRITICAL",
    "projects": "IMPORTANT",
    "positions": "IMPORTANT",
    "education": "NICE_TO_HAVE"
  },
  "reasoning": "JD explicitly requires 5+ years experience and specific tech stack (CRITICAL). Team leadership and project scale mentioned as expectations (IMPORTANT). Education only preferred, not required (NICE_TO_HAVE)."
}
```

### Integration with Later Levels

- Level 2: Thresholds applied per dimension
- Level 3: CRITICAL dimensions influence weighted scoring
- Level 4: Tie-breaker prioritizes CRITICAL dimension scores

### References

- [Source: docs/sprint-artifacts/tech-spec-epic-4.md#Level-1]
- [Source: docs/architecture.md#Multi-Level-Ranking]
- [Source: docs/epics.md#Story-4.2]
- [Source: docs/prd.md#FR21-FR22]

## Dev Agent Record

### Context Reference

None (proceeded without story context file)

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- Python syntax check passed
- All functional tests passed:
  - Priority level weights correct
  - Critical dimensions extraction works
  - Validation fixes invalid/missing priorities
  - Short JD returns default priorities
  - Session priority storage and retrieval works
  - Gemini API priority detection successful

### Completion Notes List

- All 5 tasks completed successfully
- All 4 acceptance criteria satisfied:
  - AC4.2.1: Gemini analyzes job description text
  - AC4.2.2: Returns CRITICAL/IMPORTANT/NICE_TO_HAVE/LOW_PRIORITY per dimension
  - AC4.2.3: Includes reasoning text explaining priority assignments
  - AC4.2.4: Priorities stored in session for dashboard display
- Added PRIORITY_LEVELS constant with numeric weights
- Helper functions: get_priority_weight, get_critical_dimensions, validate_priorities
- Session storage with update_session_priorities and get_session_priorities
- Tested with real JD: correctly identified Experience and Skills as CRITICAL

### File List

**Modified:**
- backend/services/gemini_service.py (added priority detection)
- backend/models.py (added session priority storage)

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-12-20 | SM Agent (Bob) | Initial draft created |
| 2025-12-20 | Dev Agent (Amelia) | Implementation complete - all ACs satisfied |
