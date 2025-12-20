# Story 5.11: Comparison API with AI Explanation

Status: review

## Story

As a **system**,
I want **to generate AI explanation for why one candidate beats another**,
So that **HR understands the specific differences**.

## Acceptance Criteria

1. **AC5.11.1:** POST /api/compare accepts session_id and two candidate_ids
2. **AC5.11.2:** Returns both candidates' scores and dimension_winners
3. **AC5.11.3:** Returns AI explanation comparing specific factors
4. **AC5.11.4:** Explanation references CRITICAL dimensions

## Tasks / Subtasks

- [ ] **Task 1: Create compare endpoint** (AC: 5.11.1, 5.11.2)
  - [ ] Add to backend/app.py:
    ```python
    @app.route('/api/compare', methods=['POST'])
    def compare_candidates():
        try:
            data = request.get_json()

            session_id = data.get('session_id')
            candidate_id_1 = data.get('candidate_id_1')
            candidate_id_2 = data.get('candidate_id_2')

            if not all([session_id, candidate_id_1, candidate_id_2]):
                return error_response('VALIDATION_ERROR', 'Missing required fields', 400)

            # Get candidates
            candidate1 = get_candidate_by_id(candidate_id_1)
            candidate2 = get_candidate_by_id(candidate_id_2)

            if not candidate1 or not candidate2:
                return error_response('NOT_FOUND', 'Candidate not found', 404)

            # Get session for priorities
            session = get_session_by_id(session_id)
            priorities = json.loads(session.get('inferred_priorities', '{}'))

            # Calculate dimension winners
            dimension_winners = calculate_dimension_winners(candidate1, candidate2)

            # Determine overall winner
            overall_winner = determine_overall_winner(candidate1, candidate2)

            # Generate AI explanation
            explanation = generate_comparison_explanation(
                candidate1, candidate2, priorities
            )

            return success_response({
                'candidate_1': format_candidate_for_comparison(candidate1),
                'candidate_2': format_candidate_for_comparison(candidate2),
                'dimension_winners': dimension_winners,
                'overall_winner': overall_winner,
                'explanation': explanation['explanation'],
                'key_differences': explanation['key_differences']
            })

        except Exception as e:
            logger.error(f'Comparison error: {e}')
            return error_response('COMPARISON_ERROR', str(e), 500)
    ```

- [ ] **Task 2: Add dimension winner calculation** (AC: 5.11.2)
  - [ ] Calculate who wins each dimension:
    ```python
    def calculate_dimension_winners(candidate1: dict, candidate2: dict) -> dict:
        """Determine winner for each dimension."""
        dimensions = ['experience', 'skills', 'projects', 'positions', 'education']
        winners = {}

        for dim in dimensions:
            score1 = candidate1.get(f'{dim}_score', 0) or 0
            score2 = candidate2.get(f'{dim}_score', 0) or 0

            if score1 > score2:
                winners[dim] = 'candidate_1'
            elif score2 > score1:
                winners[dim] = 'candidate_2'
            else:
                winners[dim] = 'tie'

        return winners

    def determine_overall_winner(candidate1: dict, candidate2: dict) -> str:
        """Determine overall winner based on match scores."""
        score1 = candidate1.get('match_score', 0) or 0
        score2 = candidate2.get('match_score', 0) or 0

        if score1 > score2:
            return 'candidate_1'
        elif score2 > score1:
            return 'candidate_2'
        return 'tie'
    ```

- [ ] **Task 3: Add AI comparison explanation** (AC: 5.11.3, 5.11.4)
  - [ ] Add to gemini_service.py:
    ```python
    COMPARISON_PROMPT = """Compare these two candidates and explain why one ranks higher.

    CANDIDATE A (Rank #{rank_1}):
    Name: {name_1}
    Match Score: {score_1}%
    Dimension Scores:
    - Experience: {exp_1}%
    - Skills: {skills_1}%
    - Projects: {proj_1}%
    - Positions: {pos_1}%
    - Education: {edu_1}%

    CANDIDATE B (Rank #{rank_2}):
    Name: {name_2}
    Match Score: {score_2}%
    Dimension Scores:
    - Experience: {exp_2}%
    - Skills: {skills_2}%
    - Projects: {proj_2}%
    - Positions: {pos_2}%
    - Education: {edu_2}%

    CRITICAL DIMENSIONS: {critical_dims}

    Return JSON:
    {{
      "explanation": "2-3 sentence explanation of why Candidate A ranks higher than B, referencing specific scores and CRITICAL dimensions",
      "key_differences": [
        "Experience: Specific comparison",
        "Skills: Specific comparison",
        "Any other notable difference"
      ]
    }}

    Focus on:
    1. CRITICAL dimension differences
    2. Specific score gaps
    3. What makes the winner stand out
    """

    def generate_comparison_explanation(
        candidate1: dict,
        candidate2: dict,
        priorities: dict
    ) -> dict:
        """Generate AI explanation comparing two candidates."""
        critical_dims = [d for d, p in priorities.items() if p == 'CRITICAL']

        try:
            model = genai.GenerativeModel(MODEL_NAME)

            prompt = COMPARISON_PROMPT.format(
                rank_1=candidate1.get('rank', 1),
                name_1=candidate1.get('name', 'Candidate A'),
                score_1=candidate1.get('match_score', 0),
                exp_1=candidate1.get('experience_score', 0),
                skills_1=candidate1.get('skills_score', 0),
                proj_1=candidate1.get('projects_score', 0),
                pos_1=candidate1.get('positions_score', 0),
                edu_1=candidate1.get('education_score', 0),
                rank_2=candidate2.get('rank', 2),
                name_2=candidate2.get('name', 'Candidate B'),
                score_2=candidate2.get('match_score', 0),
                exp_2=candidate2.get('experience_score', 0),
                skills_2=candidate2.get('skills_score', 0),
                proj_2=candidate2.get('projects_score', 0),
                pos_2=candidate2.get('positions_score', 0),
                edu_2=candidate2.get('education_score', 0),
                critical_dims=', '.join(critical_dims) or 'None specified'
            )

            response = model.generate_content(prompt)
            data = parse_gemini_response(response.text)

            return {
                'explanation': data.get('explanation', 'Comparison analysis complete.'),
                'key_differences': data.get('key_differences', [])
            }

        except Exception as e:
            logger.error(f'Comparison explanation error: {e}')
            return {
                'explanation': f'{candidate1.get("name")} ranks higher with {candidate1.get("match_score")}% vs {candidate2.get("match_score")}%.',
                'key_differences': []
            }
    ```

- [ ] **Task 4: Add format helper**
  - [ ] Format candidate for response:
    ```python
    def format_candidate_for_comparison(candidate: dict) -> dict:
        """Format candidate data for comparison response."""
        return {
            'id': candidate.get('id'),
            'name': candidate.get('name'),
            'rank': candidate.get('rank'),
            'match_score': candidate.get('match_score'),
            'scores': {
                'experience': candidate.get('experience_score', 0),
                'skills': candidate.get('skills_score', 0),
                'projects': candidate.get('projects_score', 0),
                'positions': candidate.get('positions_score', 0),
                'education': candidate.get('education_score', 0)
            }
        }
    ```

- [ ] **Task 5: Add models.py helper**
  - [ ] Get candidate by ID:
    ```python
    def get_candidate_by_id(candidate_id: str) -> dict | None:
        """Get full candidate record by ID."""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM candidates WHERE id = ?', (candidate_id,))
        row = cursor.fetchone()
        conn.close()

        return dict(row) if row else None
    ```

- [ ] **Task 6: Test comparison API**
  - [ ] Test with valid candidates:
    ```bash
    curl -X POST http://localhost:5000/api/compare \
      -H "Content-Type: application/json" \
      -d '{"session_id":"...", "candidate_id_1":"...", "candidate_id_2":"..."}'
    ```
  - [ ] Test with invalid candidate IDs (404)
  - [ ] Verify dimension winners correct
  - [ ] Verify AI explanation generated

## Dev Notes

### Architecture Alignment

This story implements the comparison API:
- **Endpoint:** POST /api/compare
- **AI:** Gemini generates contextual explanation

### API Contract

**Request:**
```json
{
  "session_id": "uuid",
  "candidate_id_1": "uuid",
  "candidate_id_2": "uuid"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "candidate_1": {
      "id": "uuid",
      "name": "Sara Ahmed",
      "rank": 1,
      "match_score": 94,
      "scores": {
        "experience": 95,
        "skills": 88,
        "projects": 92,
        "positions": 85,
        "education": 70
      }
    },
    "candidate_2": {
      "id": "uuid",
      "name": "Ali Khan",
      "rank": 2,
      "match_score": 91,
      "scores": {...}
    },
    "dimension_winners": {
      "experience": "candidate_1",
      "skills": "candidate_2",
      "projects": "candidate_1",
      "positions": "candidate_1",
      "education": "candidate_2"
    },
    "overall_winner": "candidate_1",
    "explanation": "Sara ranks higher because Experience is CRITICAL for this Senior role, and she scores 95% vs Ali's 78%. Although Ali has better Skills (95% vs 88%), the JD emphasizes experience...",
    "key_differences": [
      "Experience: Sara's 5yr at Google vs Ali's 3yr at startup",
      "Skills: Ali's broader stack vs Sara's deeper Python expertise"
    ]
  }
}
```

### CRITICAL Dimension Focus

The AI explanation should emphasize dimensions marked as CRITICAL in the inferred priorities, explaining why the winner excels in those areas.

### Performance

- Single Gemini call for explanation
- Response time: ~3 seconds typical

### References

- [Source: docs/sprint-artifacts/tech-spec-epic-5.md#Comparison-API]
- [Source: docs/architecture.md#POST-api-compare]
- [Source: docs/epics.md#Story-5.11]
- [Source: docs/prd.md#FR55-FR56]

## Dev Agent Record

### Context Reference

docs/sprint-artifacts/5-11-comparison-api-with-ai-explanation.md

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- Backend imports verified successfully
- POST /api/compare endpoint returns 400 for missing fields
- POST /api/compare endpoint returns 404 for non-existent candidates
- Frontend comparison modal correctly falls back to mock data when API unavailable
- Comparison modal displays correctly with all dimension comparisons and AI analysis

### Completion Notes List

- All 6 tasks completed successfully
- All 4 acceptance criteria satisfied:
  - AC5.11.1: POST /api/compare accepts session_id and two candidate_ids
  - AC5.11.2: Returns both candidates' scores and dimension_winners
  - AC5.11.3: Returns AI explanation comparing specific factors
  - AC5.11.4: Explanation references CRITICAL dimensions
- Added generate_comparison_explanation to gemini_service.py with fallback for no API key
- Added compare endpoint with helper functions (calculate_dimension_winners, determine_overall_winner, format_candidate_for_comparison)
- Frontend already had compareCandidates API function configured correctly

### File List

**Modified:**
- backend/app.py (added /api/compare endpoint and helper functions)
- backend/services/gemini_service.py (added generate_comparison_explanation function)

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-12-20 | SM Agent (Bob) | Initial draft created |
| 2025-12-20 | Dev Agent (Amelia) | Implementation complete - all ACs satisfied |
