# Story 4.6: Tie-Breaker Logic (Level 4)

Status: review

## Story

As a **system**,
I want **Gemini to explain tie-breaker decisions**,
So that **close rankings are transparent**.

## Acceptance Criteria

1. **AC4.6.1:** When candidates score within 5%, tie-breaker rules apply
2. **AC4.6.2:** Tie-breaker considers: CRITICAL dimension scores, project scale, career progression, leadership, recency
3. **AC4.6.3:** tie_breaker_applied flag set to true for affected candidates
4. **AC4.6.4:** tie_breaker_reason explains the decision

## Tasks / Subtasks

- [x] **Task 1: Add tie-breaker rules to ranking prompt** (AC: 4.6.1-4.6.2)
  - [ ] Extend RANKING_PROMPT in ranking_service.py:
    ```python
    TIE_BREAKER_RULES = """
    === TIE-BREAKER RULES ===
    When candidates are within 5% match score, apply these rules in order:

    1. CRITICAL Dimension Winner
       - Higher score in any CRITICAL dimension wins
       - Example: If Experience is CRITICAL and A has 90% vs B's 75%, A wins

    2. Project Impact/Scale
       - Production apps > side projects
       - 10K users > 100 users
       - Measurable impact (revenue, efficiency)

    3. Career Progression Speed
       - Junior→Senior in 3 years > 5 years
       - Promotions and growing responsibility

    4. Leadership Indicators
       - Led team > worked in team
       - Mentored others
       - Technical leadership

    5. Recency of Experience
       - Recent experience > old experience
       - Current skills more valuable

    For tie-breaker candidates, set:
    - tie_breaker_applied: true
    - tie_breaker_reason: "Explanation of why this candidate ranks higher despite similar score"
    """
    ```

- [x] **Task 2: Add tie-breaker detection function** (AC: 4.6.1, 4.6.3)
  - [ ] Detect close scores:
    ```python
    def detect_tie_breaker_candidates(rankings: list, threshold: float = 5.0) -> list:
        """Identify candidates with close scores needing tie-breaker.

        Args:
            rankings: Sorted list of ranked candidates
            threshold: Score difference threshold (default 5%)

        Returns:
            List of candidate IDs that need tie-breaker explanation
        """
        tie_breaker_ids = set()

        for i in range(len(rankings) - 1):
            current = rankings[i]
            next_candidate = rankings[i + 1]

            current_score = current.get('match_score', 0)
            next_score = next_candidate.get('match_score', 0)

            if abs(current_score - next_score) <= threshold:
                tie_breaker_ids.add(current['candidate_id'])
                tie_breaker_ids.add(next_candidate['candidate_id'])

        return list(tie_breaker_ids)
    ```

- [x] **Task 3: Enhance ranking with tie-breaker info** (AC: 4.6.3, 4.6.4)
  - [ ] Add tie-breaker fields to ranking response:
    ```python
    def apply_tie_breaker_flags(rankings: list, priorities: dict) -> list:
        """Apply tie-breaker flags to rankings.

        Args:
            rankings: Ranked candidates list
            priorities: Inferred priorities

        Returns:
            Rankings with tie-breaker fields
        """
        tie_breaker_ids = detect_tie_breaker_candidates(rankings)

        for ranking in rankings:
            cid = ranking.get('candidate_id')

            if cid in tie_breaker_ids:
                # Check if Gemini provided tie-breaker info
                if not ranking.get('tie_breaker_applied'):
                    ranking['tie_breaker_applied'] = True

                if not ranking.get('tie_breaker_reason'):
                    # Generate default reason based on CRITICAL dimensions
                    critical_dims = [d for d, p in priorities.items() if p == 'CRITICAL']
                    scores = ranking.get('scores', {})

                    if critical_dims:
                        best_critical = max(critical_dims, key=lambda d: scores.get(d, 0))
                        score = scores.get(best_critical, 0)
                        ranking['tie_breaker_reason'] = (
                            f"Higher {best_critical} score ({score}%) in CRITICAL dimension"
                        )
                    else:
                        ranking['tie_breaker_reason'] = "Based on overall profile strength"
            else:
                ranking['tie_breaker_applied'] = False
                ranking['tie_breaker_reason'] = None

        return rankings
    ```

- [x] **Task 4: Add detailed tie-breaker prompt** (AC: 4.6.4)
  - [ ] Create focused tie-breaker prompt for close candidates:
    ```python
    TIE_BREAKER_PROMPT = """Two candidates have similar scores. Explain why one ranks higher.

    CANDIDATE A (Rank {rank_a}): {name_a}
    Match Score: {score_a}%
    Scores: {scores_a}

    CANDIDATE B (Rank {rank_b}): {name_b}
    Match Score: {score_b}%
    Scores: {scores_b}

    CRITICAL Dimensions: {critical_dims}

    Explain in 2-3 sentences why Candidate A ranks higher, referencing:
    - CRITICAL dimension performance
    - Specific differentiating factors
    - Concrete evidence from their profiles

    Return JSON:
    {{
      "tie_breaker_reason": "Your explanation"
    }}
    """

    def generate_tie_breaker_explanation(
        candidate_a: dict,
        candidate_b: dict,
        priorities: dict
    ) -> str:
        """Generate detailed tie-breaker explanation.

        Args:
            candidate_a: Higher ranked candidate
            candidate_b: Lower ranked candidate
            priorities: Inferred priorities

        Returns:
            Explanation string
        """
        critical_dims = [d for d, p in priorities.items() if p == 'CRITICAL']

        try:
            model = genai.GenerativeModel('gemini-1.5-flash')

            prompt = TIE_BREAKER_PROMPT.format(
                rank_a=candidate_a.get('rank', 1),
                name_a=candidate_a.get('name', 'Candidate A'),
                score_a=candidate_a.get('match_score', 0),
                scores_a=json.dumps(candidate_a.get('scores', {})),
                rank_b=candidate_b.get('rank', 2),
                name_b=candidate_b.get('name', 'Candidate B'),
                score_b=candidate_b.get('match_score', 0),
                scores_b=json.dumps(candidate_b.get('scores', {})),
                critical_dims=', '.join(critical_dims) or 'None specified'
            )

            response = model.generate_content(prompt)
            data = parse_gemini_response(response.text)

            return data.get('tie_breaker_reason', 'Based on overall profile strength')

        except Exception as e:
            logger.error(f"Tie-breaker explanation error: {e}")
            return "Based on overall profile assessment"
    ```

- [x] **Task 5: Integrate tie-breaker into ranking flow**
  - [ ] Update ranking function:
    ```python
    def rank_with_tie_breakers(
        job_description: str,
        candidates: list,
        weights: dict,
        priorities: dict
    ) -> list:
        """Rank candidates with tie-breaker logic.

        Args:
            job_description: JD text
            candidates: Remaining candidates after threshold
            weights: Dimension weights
            priorities: Inferred priorities

        Returns:
            Ranked candidates with tie-breaker info
        """
        # Get base rankings
        rankings = rank_candidates_comparatively(
            job_description, candidates, weights, priorities
        )

        # Apply tie-breaker flags
        rankings = apply_tie_breaker_flags(rankings, priorities)

        # Generate detailed explanations for tie-breaker pairs
        for i in range(len(rankings) - 1):
            current = rankings[i]
            next_c = rankings[i + 1]

            if (current.get('tie_breaker_applied') and
                next_c.get('tie_breaker_applied') and
                not current.get('tie_breaker_reason_detailed')):

                explanation = generate_tie_breaker_explanation(
                    current, next_c, priorities
                )
                current['tie_breaker_reason'] = explanation

        return rankings
    ```

- [x] **Task 6: Test tie-breaker logic**
  - [ ] Test detection with close scores:
    ```python
    rankings = [
        {'candidate_id': 'a', 'match_score': 85},
        {'candidate_id': 'b', 'match_score': 83},  # Within 5%
        {'candidate_id': 'c', 'match_score': 70},  # Not within 5%
    ]
    tie_ids = detect_tie_breaker_candidates(rankings)
    assert 'a' in tie_ids
    assert 'b' in tie_ids
    assert 'c' not in tie_ids
    ```
  - [ ] Test flag application
  - [ ] Test explanation generation

## Dev Notes

### Architecture Alignment

This story implements Level 4 of the Multi-Level Ranking System:
- **Purpose:** Transparent decisions for close candidates
- **Trigger:** Match scores within 5% of each other
- **Output:** Flags and explanations on affected candidates

### Tie-Breaker Decision Tree

```
Scores within 5%?
      │
      ├── No → Normal ranking, no tie-breaker
      │
      └── Yes → Apply tie-breaker rules:
                 │
                 ├── 1. CRITICAL dimension scores
                 ├── 2. Project impact/scale
                 ├── 3. Career progression speed
                 ├── 4. Leadership indicators
                 └── 5. Recency of experience
```

### Example Tie-Breaker Scenario

**Candidate A:** 85% match
**Candidate B:** 83% match (within 5%)

**Explanation:**
> "Candidate A ranks higher because Experience is CRITICAL for this Senior role, and A scores 90% vs B's 75% in Experience. Although B has slightly better Skills (95% vs 88%), the JD emphasizes '5+ years in enterprise environment' which A's Google experience directly matches."

### Tie-Breaker Fields

```json
{
  "candidate_id": "uuid",
  "rank": 2,
  "match_score": 83,
  "tie_breaker_applied": true,
  "tie_breaker_reason": "Candidate ranked #1 has higher Experience score (90% vs 75%) in CRITICAL dimension"
}
```

### UI Display

On dashboard, tie-breaker candidates show:
- ⚖️ icon indicating tie-breaker
- Expandable explanation section
- Comparison to adjacent candidate

### References

- [Source: docs/sprint-artifacts/tech-spec-epic-4.md#Level-4]
- [Source: docs/architecture.md#Tie-Breaker-Logic]
- [Source: docs/epics.md#Story-4.6]
- [Source: docs/prd.md#FR30-FR32]

## Dev Agent Record

### Context Reference

docs/sprint-artifacts/4-6-tie-breaker-logic.md

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- All 6 test groups passed (20+ individual tests)
- Tie-breaker detection verified with various score scenarios
- Flag application and reason generation verified
- Edge cases (boundary, empty, single) handled

### Completion Notes List

- All 6 tasks completed successfully
- All 4 acceptance criteria satisfied:
  - AC4.6.1: Candidates within 5% trigger tie-breaker (detect_tie_breaker_candidates)
  - AC4.6.2: TIE_BREAKER_RULES defines: CRITICAL dims, project scale, career progression, leadership, recency
  - AC4.6.3: tie_breaker_applied flag set on affected candidates
  - AC4.6.4: tie_breaker_reason explains decision (auto-generated or from Gemini)
- Added get_tie_breaker_summary() for dashboard display
- Added rank_with_tie_breakers() as main entry point
- Existing reasons preserved when already set

### File List

**Created:**
- backend/test_tie_breaker.py

**Modified:**
- backend/services/ranking_service.py (added Level 4 functions)

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-12-20 | SM Agent (Bob) | Initial draft created |
| 2025-12-20 | Dev Agent (Amelia) | Implementation complete - all ACs satisfied |
