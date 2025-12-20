# Story 4.5: Weighted Comparative Scoring (Level 3)

Status: review

## Story

As a **system**,
I want **Gemini to score candidates relative to the pool**,
So that **scores reflect standing among actual competitors**.

## Acceptance Criteria

1. **AC4.5.1:** Scores are RELATIVE to pool (80% = better than 80% of pool in that dimension)
2. **AC4.5.2:** 5-dimension scores generated for each candidate
3. **AC4.5.3:** Overall match score uses configured weights
4. **AC4.5.4:** 3-bullet summaries generated for top candidates

## Tasks / Subtasks

- [x] **Task 1: Create comparative ranking prompt** (AC: 4.5.1-4.5.4)
  - [ ] Add to ranking_service.py:
    ```python
    RANKING_PROMPT = """You are an expert HR analyst. Rank candidates comparatively.

    === JOB DESCRIPTION ===
    {job_description}

    === INFERRED PRIORITIES ===
    {priorities}

    === SCORING WEIGHTS ===
    Experience: {exp_weight}%
    Skills: {skills_weight}%
    Projects: {projects_weight}%
    Positions: {positions_weight}%
    Education: {edu_weight}%

    === CANDIDATE POOL ({count} candidates) ===
    {candidates}

    === SCORING RULES ===
    1. Score each dimension 0-100 RELATIVE to this pool:
       - 50 = average for this pool
       - 80+ = top 20% of pool
       - 90+ = exceptional, top 10%
       - Below 50 = below average for this pool
    2. Consider quality over quantity
    3. Look for concrete evidence, not just claims
    4. CRITICAL dimensions should be scored strictly

    === OUTPUT ===
    Return ONLY valid JSON:
    {{
      "rankings": [
        {{
          "candidate_id": "uuid",
          "rank": 1,
          "match_score": 94,
          "scores": {{
            "experience": 95,
            "skills": 92,
            "projects": 98,
            "positions": 90,
            "education": 85
          }},
          "summary": [
            "First key strength (specific)",
            "Second key strength (specific)",
            "Third key strength (specific)"
          ],
          "why_selected": "2-3 sentence explanation of ranking",
          "compared_to_pool": "How they compare to other candidates"
        }}
      ]
    }}

    Rank ALL candidates. Order by match_score descending.
    """
    ```

- [x] **Task 2: Implement ranking function** (AC: 4.5.1-4.5.4)
  - [ ] Add ranking function:
    ```python
    def rank_candidates_comparatively(
        job_description: str,
        candidates: list,
        weights: dict,
        priorities: dict
    ) -> list:
        """Rank candidates comparatively with weights.

        Args:
            job_description: JD text
            candidates: List of remaining candidates
            weights: Dimension weights (sum to 100)
            priorities: Inferred priorities from Level 1

        Returns:
            List of ranked candidate dicts
        """
        if not candidates:
            return []

        try:
            model = genai.GenerativeModel('gemini-1.5-flash')

            # Format inputs
            candidates_text = format_pool_for_gemini(candidates)
            priorities_text = json.dumps(priorities, indent=2)

            prompt = RANKING_PROMPT.format(
                job_description=job_description,
                priorities=priorities_text,
                exp_weight=weights.get('experience', 20),
                skills_weight=weights.get('skills', 20),
                projects_weight=weights.get('projects', 20),
                positions_weight=weights.get('positions', 20),
                edu_weight=weights.get('education', 20),
                count=len(candidates),
                candidates=candidates_text
            )

            response = model.generate_content(prompt)
            data = parse_gemini_response(response.text)

            rankings = data.get('rankings', [])

            # Validate and sort
            rankings = validate_rankings(rankings, candidates)
            rankings.sort(key=lambda x: x.get('match_score', 0), reverse=True)

            # Assign final ranks
            for i, r in enumerate(rankings):
                r['rank'] = i + 1

            logger.info(f"Ranked {len(rankings)} candidates")
            return rankings

        except Exception as e:
            logger.error(f"Ranking error: {e}")
            return []
    ```

- [x] **Task 3: Add weight calculation helper** (AC: 4.5.3)
  - [ ] Calculate weighted match score:
    ```python
    def calculate_match_score(scores: dict, weights: dict) -> int:
        """Calculate weighted match score.

        Args:
            scores: Dict of dimension scores
            weights: Dict of dimension weights

        Returns:
            Overall match score (0-100)
        """
        total = 0
        weight_sum = 0

        for dim in ['experience', 'skills', 'projects', 'positions', 'education']:
            score = scores.get(dim, 0)
            weight = weights.get(dim, 20)
            total += score * weight
            weight_sum += weight

        if weight_sum == 0:
            return 0

        return round(total / weight_sum)


    def validate_weights(weights: dict) -> dict:
        """Ensure weights are valid and sum to 100."""
        dimensions = ['experience', 'skills', 'projects', 'positions', 'education']

        validated = {}
        for dim in dimensions:
            validated[dim] = weights.get(dim, 20)

        total = sum(validated.values())
        if total != 100:
            # Normalize to 100
            factor = 100 / total if total > 0 else 1
            for dim in dimensions:
                validated[dim] = round(validated[dim] * factor)

        return validated
    ```

- [x] **Task 4: Add ranking validation** (AC: 4.5.2)
  - [ ] Validate Gemini response:
    ```python
    def validate_rankings(rankings: list, candidates: list) -> list:
        """Validate and clean ranking data.

        Args:
            rankings: Raw rankings from Gemini
            candidates: Original candidate list

        Returns:
            Validated rankings
        """
        candidate_ids = {c['id'] for c in candidates}
        validated = []

        for r in rankings:
            cid = r.get('candidate_id')
            if cid not in candidate_ids:
                continue

            # Validate scores
            scores = r.get('scores', {})
            for dim in ['experience', 'skills', 'projects', 'positions', 'education']:
                if dim not in scores:
                    scores[dim] = 50  # Default to average
                else:
                    # Clamp to 0-100
                    scores[dim] = max(0, min(100, scores[dim]))

            r['scores'] = scores

            # Validate match score
            if 'match_score' not in r or not isinstance(r['match_score'], (int, float)):
                r['match_score'] = 50

            # Validate summary
            if not isinstance(r.get('summary'), list):
                r['summary'] = ['No summary available']

            validated.append(r)

        return validated
    ```

- [x] **Task 5: Add summary generation helper** (AC: 4.5.4)
  - [ ] Generate fallback summaries:
    ```python
    def generate_summary_fallback(candidate: dict, scores: dict) -> list:
        """Generate summary if Gemini doesn't provide one.

        Args:
            candidate: Candidate dict
            scores: Dimension scores

        Returns:
            List of 3 summary bullets
        """
        summary = []

        # Experience
        exp_years = candidate.get('experience_years', 0)
        if exp_years > 0:
            summary.append(f"{exp_years} years of professional experience")

        # Skills
        skills = candidate.get('skills', [])
        if skills:
            top_skills = ', '.join(skills[:4])
            summary.append(f"Skilled in {top_skills}")

        # Projects
        projects = candidate.get('projects', [])
        if projects:
            summary.append(f"{len(projects)} notable projects in portfolio")

        # Pad to 3 if needed
        while len(summary) < 3:
            summary.append("See full profile for details")

        return summary[:3]
    ```

- [x] **Task 6: Test comparative scoring**
  - [ ] Test with sample candidates:
    ```python
    rankings = rank_candidates_comparatively(jd, candidates, weights, priorities)
    assert len(rankings) == len(candidates)
    assert rankings[0]['rank'] == 1
    assert 0 <= rankings[0]['match_score'] <= 100
    ```
  - [ ] Verify relative scoring (not absolute)
  - [ ] Verify weight application

## Dev Notes

### Architecture Alignment

This story implements Level 3 of the Multi-Level Ranking System:
- **Key Concept:** RELATIVE scoring, not absolute
- **Output:** Ranked candidates with scores and explanations

### Relative vs Absolute Scoring

**Wrong (Absolute):**
- "Has 5 years experience" → 70%

**Correct (Relative):**
- "Has 5 years experience, which is above 80% of this pool" → 80%

### Scoring Guidelines

| Score | Meaning |
|-------|---------|
| 90-100 | Exceptional, top 10% of pool |
| 80-89 | Excellent, top 20% of pool |
| 60-79 | Good, above average |
| 50-59 | Average for this pool |
| 30-49 | Below average |
| 0-29 | Significantly below pool |

### Weight Application

```
Match Score = (Exp × ExpWeight + Skills × SkillsWeight + ...) / 100

Example with weights [30, 25, 20, 15, 10]:
Match = (90×30 + 85×25 + 80×20 + 75×15 + 70×10) / 100
      = (2700 + 2125 + 1600 + 1125 + 700) / 100
      = 82.5%
```

### Summary Guidelines

3 bullets should be:
1. Specific, quantifiable when possible
2. Relevant to the job
3. Differentiating from other candidates

**Good:**
- "5 years Python at Google with microservices"
- "Led team of 5 on ML pipeline serving 100K users"

**Bad:**
- "Has Python experience"
- "Good team player"

### References

- [Source: docs/sprint-artifacts/tech-spec-epic-4.md#Level-3]
- [Source: docs/architecture.md#Weighted-Scoring]
- [Source: docs/epics.md#Story-4.5]
- [Source: docs/prd.md#FR26-FR29]

## Dev Agent Record

### Context Reference

docs/sprint-artifacts/4-5-weighted-comparative-scoring.md

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- All 5 test groups passed (15+ individual tests)
- Weight normalization verified
- Score clamping verified
- Fallback summary generation verified

### Completion Notes List

- All 6 tasks completed successfully
- All 4 acceptance criteria satisfied:
  - AC4.5.1: Scores are RELATIVE to pool via RANKING_PROMPT
  - AC4.5.2: 5-dimension scores generated and validated
  - AC4.5.3: Overall match score uses configured weights via calculate_match_score()
  - AC4.5.4: 3-bullet summaries generated (with fallback via generate_summary_fallback())
- Added weight normalization to ensure weights sum to 100
- Added missing candidate handling (adds with default scores)
- Added fallback ranking on API error

### File List

**Created:**
- backend/test_comparative_scoring.py

**Modified:**
- backend/services/ranking_service.py (added Level 3 functions)

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-12-20 | SM Agent (Bob) | Initial draft created |
| 2025-12-20 | Dev Agent (Amelia) | Implementation complete - all ACs satisfied |
