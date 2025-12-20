# Story 4.4: Threshold Elimination Logic (Level 2)

Status: review

## Story

As a **system**,
I want **to eliminate candidates below thresholds before ranking**,
So that **only qualified candidates are considered**.

## Acceptance Criteria

1. **AC4.4.1:** Gemini first scores all candidates on each dimension (0-100)
2. **AC4.4.2:** Candidates below any enabled threshold are eliminated
3. **AC4.4.3:** Elimination reasons recorded per candidate
4. **AC4.4.4:** Eliminated count and breakdown returned in response

## Tasks / Subtasks

- [x] **Task 1: Create ranking_service.py** (AC: 4.4.1-4.4.4)
  - [ ] Create `backend/services/ranking_service.py`:
    ```python
    import json
    import logging
    from services.gemini_service import detect_job_priorities
    from services.pool_manager import get_pool_for_role, format_pool_for_gemini

    logger = logging.getLogger(__name__)

    def apply_thresholds(candidates: list, thresholds: dict, scores: dict) -> tuple:
        """Apply threshold elimination to candidates.

        Args:
            candidates: List of candidate dicts
            thresholds: Dict with dimension thresholds
            scores: Dict mapping candidate_id to dimension scores

        Returns:
            Tuple of (remaining_candidates, eliminated_candidates)
        """
        remaining = []
        eliminated = []

        for candidate in candidates:
            cid = candidate['id']
            candidate_scores = scores.get(cid, {})

            elimination_reason = None

            for dim, config in thresholds.items():
                if not config.get('enabled', False):
                    continue

                minimum = config.get('minimum', 0)
                score = candidate_scores.get(dim, 0)

                if score < minimum:
                    elimination_reason = f"{dim.title()} score {score}% < minimum {minimum}%"
                    break

            if elimination_reason:
                eliminated.append({
                    'id': cid,
                    'name': candidate.get('name', 'Unknown'),
                    'reason': elimination_reason
                })
            else:
                remaining.append(candidate)

        logger.info(f"Threshold elimination: {len(eliminated)} eliminated, {len(remaining)} remaining")
        return remaining, eliminated
    ```

- [x] **Task 2: Add scoring prompt for threshold check** (AC: 4.4.1)
  - [ ] Add initial scoring function:
    ```python
    import google.generativeai as genai

    SCORING_PROMPT = """Score each candidate on the 5 dimensions (0-100).
    Scores should be RELATIVE to the pool - 50 is average, 80+ is excellent.

    JOB DESCRIPTION:
    {job_description}

    CANDIDATES:
    {candidates}

    Return ONLY valid JSON:
    {{
      "scores": {{
        "candidate_id_1": {{
          "experience": 75,
          "skills": 80,
          "projects": 65,
          "positions": 70,
          "education": 60
        }},
        "candidate_id_2": {{ ... }}
      }}
    }}
    """

    def score_candidates_for_thresholds(job_description: str, candidates: list) -> dict:
        """Get dimension scores for all candidates.

        Args:
            job_description: JD text
            candidates: List of candidate dicts

        Returns:
            Dict mapping candidate_id to dimension scores
        """
        if not candidates:
            return {}

        try:
            model = genai.GenerativeModel('gemini-1.5-flash')

            # Format candidates
            candidate_text = format_pool_for_gemini(candidates)

            prompt = SCORING_PROMPT.format(
                job_description=job_description,
                candidates=candidate_text
            )

            response = model.generate_content(prompt)
            response_text = response.text.strip()

            # Parse response
            data = parse_gemini_response(response_text)
            return data.get('scores', {})

        except Exception as e:
            logger.error(f"Scoring error: {e}")
            return {}
    ```

- [x] **Task 3: Add elimination summary function** (AC: 4.4.3, 4.4.4)
  - [ ] Create elimination summary:
    ```python
    def get_elimination_summary(eliminated: list) -> dict:
        """Generate summary of eliminations.

        Args:
            eliminated: List of eliminated candidate dicts

        Returns:
            Summary with counts and breakdown
        """
        if not eliminated:
            return {
                "count": 0,
                "breakdown": {},
                "candidates": []
            }

        # Count by reason dimension
        breakdown = {}
        for e in eliminated:
            reason = e.get('reason', 'Unknown')
            # Extract dimension from reason
            dim = reason.split()[0].lower() if reason else 'unknown'
            breakdown[dim] = breakdown.get(dim, 0) + 1

        return {
            "count": len(eliminated),
            "breakdown": breakdown,
            "candidates": [
                {"id": e['id'], "name": e['name'], "reason": e['reason']}
                for e in eliminated
            ]
        }
    ```

- [x] **Task 4: Add threshold processing wrapper** (AC: 4.4.1-4.4.4)
  - [ ] Create main processing function:
    ```python
    def process_threshold_elimination(
        job_description: str,
        candidates: list,
        thresholds: dict
    ) -> dict:
        """Process Level 2 threshold elimination.

        Args:
            job_description: JD text
            candidates: List of candidate dicts
            thresholds: Threshold configuration

        Returns:
            Dict with remaining, eliminated, scores, and summary
        """
        # Check if any thresholds enabled
        enabled_thresholds = {
            k: v for k, v in thresholds.items()
            if v.get('enabled', False)
        }

        if not enabled_thresholds:
            logger.info("No thresholds enabled, skipping elimination")
            return {
                "remaining": candidates,
                "eliminated": [],
                "scores": {},
                "summary": get_elimination_summary([])
            }

        # Score all candidates
        logger.info(f"Scoring {len(candidates)} candidates for threshold check")
        scores = score_candidates_for_thresholds(job_description, candidates)

        # Apply thresholds
        remaining, eliminated = apply_thresholds(candidates, thresholds, scores)

        return {
            "remaining": remaining,
            "eliminated": eliminated,
            "scores": scores,
            "summary": get_elimination_summary(eliminated)
        }
    ```

- [x] **Task 5: Store elimination results**
  - [ ] Add to models.py:
    ```python
    def update_session_eliminations(session_id: str, elimination_data: dict) -> None:
        """Store elimination results in session."""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE sessions
            SET eliminated_count = ?,
                elimination_breakdown = ?
            WHERE id = ?
        ''', (
            elimination_data.get('count', 0),
            json.dumps(elimination_data.get('breakdown', {})),
            session_id
        ))

        conn.commit()
        conn.close()
    ```

- [x] **Task 6: Test threshold elimination**
  - [ ] Test with no thresholds enabled:
    ```python
    result = process_threshold_elimination(jd, candidates, {})
    assert result['remaining'] == candidates
    assert result['eliminated'] == []
    ```
  - [ ] Test with threshold eliminating some:
    ```python
    thresholds = {'experience': {'enabled': True, 'minimum': 60}}
    result = process_threshold_elimination(jd, candidates, thresholds)
    # Should have some eliminated
    ```
  - [ ] Test elimination reason format

## Dev Notes

### Architecture Alignment

This story implements Level 2 of the Multi-Level Ranking System:
- **Purpose:** Filter out unqualified candidates before ranking
- **Input:** Candidates + threshold configuration
- **Output:** Remaining candidates + elimination records

### Elimination Flow

```
All Pool Candidates (45)
         │
         ▼
Score on 5 dimensions (Gemini)
         │
         ▼
Apply enabled thresholds
         │
         ├── Experience < 60% → Eliminated (8)
         ├── Skills < 50% → Eliminated (5)
         │
         ▼
Remaining candidates (32) → Level 3
```

### Threshold Logic

```python
for each candidate:
    for each enabled_threshold:
        if score[dimension] < threshold.minimum:
            eliminate(candidate, reason)
            break  # One failure is enough
```

### Elimination Record Format

```json
{
  "id": "candidate-uuid",
  "name": "John Doe",
  "reason": "Experience score 45% < minimum 60%"
}
```

### Summary Format

```json
{
  "count": 13,
  "breakdown": {
    "experience": 8,
    "skills": 5
  },
  "candidates": [...]
}
```

### Edge Cases

| Scenario | Handling |
|----------|----------|
| No thresholds enabled | Skip elimination, return all |
| All candidates eliminated | Return empty remaining |
| Candidate missing score | Treat as 0, likely eliminated |

### References

- [Source: docs/sprint-artifacts/tech-spec-epic-4.md#Level-2]
- [Source: docs/architecture.md#Minimum-Thresholds]
- [Source: docs/epics.md#Story-4.4]
- [Source: docs/prd.md#FR24-FR25]

## Dev Agent Record

### Context Reference

docs/sprint-artifacts/4-4-threshold-elimination-logic.md

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- All 7 threshold elimination tests passed
- Warning about google.generativeai deprecation (non-blocking)

### Completion Notes List

- All 6 tasks completed successfully
- All 4 acceptance criteria satisfied:
  - AC4.4.1: Gemini scores all candidates on each dimension (0-100) via SCORING_PROMPT
  - AC4.4.2: Candidates below any enabled threshold are eliminated via apply_thresholds()
  - AC4.4.3: Elimination reasons recorded per candidate (format: "Dimension score X% < minimum Y%")
  - AC4.4.4: Eliminated count and breakdown returned in response via get_elimination_summary()
- Added fail-open behavior when scoring fails (returns all candidates)
- Scores attached to remaining candidates for downstream use

### File List

**Created:**
- backend/services/ranking_service.py
- backend/test_threshold_elimination.py

**Modified:**
- backend/models.py (added update_session_eliminations, get_session_eliminations functions)

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-12-20 | SM Agent (Bob) | Initial draft created |
| 2025-12-20 | Dev Agent (Amelia) | Implementation complete - all ACs satisfied |
