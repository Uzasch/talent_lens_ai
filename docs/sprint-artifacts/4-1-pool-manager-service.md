# Story 4.1: Pool Manager Service

Status: review

## Story

As a **developer**,
I want **to fetch all active candidates for a role**,
So that **comparative analysis can be performed**.

## Acceptance Criteria

1. **AC4.1.1:** Function fetches ALL active candidates for a role_id
2. **AC4.1.2:** Includes candidates from current + past sessions
3. **AC4.1.3:** Excludes candidates with status superseded/hired/withdrew
4. **AC4.1.4:** Returns formatted summaries suitable for Gemini prompt
5. **AC4.1.5:** Handles empty pool gracefully

## Tasks / Subtasks

- [x] **Task 1: Create pool_manager.py service** (AC: 4.1.1-4.1.3)
  - [ ] Create `backend/services/pool_manager.py`:
    ```python
    import json
    import logging
    from models import get_db_connection

    logger = logging.getLogger(__name__)

    def get_pool_for_role(role_id: str) -> list[dict]:
        """Get all active candidates for a role.

        Args:
            role_id: UUID of the role

        Returns:
            List of candidate dicts with extracted data
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                id, name, email,
                skills, experience_years, experience_details,
                education, projects, positions,
                session_id, uploaded_at
            FROM candidates
            WHERE role_id = ? AND status = 'active'
            ORDER BY uploaded_at DESC
        ''', (role_id,))

        rows = cursor.fetchall()
        conn.close()

        candidates = []
        for row in rows:
            candidate = dict(row)
            # Parse JSON fields
            for field in ['skills', 'experience_details', 'education', 'projects', 'positions']:
                if candidate.get(field):
                    try:
                        candidate[field] = json.loads(candidate[field])
                    except json.JSONDecodeError:
                        candidate[field] = []
            candidates.append(candidate)

        logger.info(f"Fetched {len(candidates)} active candidates for role {role_id}")
        return candidates
    ```

- [x] **Task 2: Add pool count function** (AC: 4.1.1)
  - [ ] Add count function:
    ```python
    def get_pool_count(role_id: str) -> int:
        """Get count of active candidates in pool."""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT COUNT(*) FROM candidates
            WHERE role_id = ? AND status = 'active'
        ''', (role_id,))

        count = cursor.fetchone()[0]
        conn.close()
        return count
    ```

- [x] **Task 3: Create Gemini formatting function** (AC: 4.1.4)
  - [ ] Add format_pool_for_gemini function:
    ```python
    def format_pool_for_gemini(candidates: list) -> str:
        """Format candidate pool as text for Gemini prompt.

        Args:
            candidates: List of candidate dicts

        Returns:
            Formatted string for Gemini context
        """
        if not candidates:
            return "No candidates in pool."

        summaries = []
        for i, c in enumerate(candidates, 1):
            skills = c.get('skills', [])
            skills_str = ', '.join(skills[:10]) if skills else 'Not specified'

            exp_years = c.get('experience_years', 0)

            # Get position progression
            positions = c.get('positions', [])
            if positions:
                pos_str = ' → '.join([p.get('title', '') for p in positions[:4]])
            else:
                pos_str = 'Not specified'

            # Count projects
            projects = c.get('projects', [])
            proj_count = len(projects)

            # Get education
            education = c.get('education', [])
            if education:
                edu_str = education[0].get('degree', 'Not specified')
            else:
                edu_str = 'Not specified'

            summary = f"""
Candidate {i} (ID: {c['id']}):
  Name: {c.get('name', 'Unknown')}
  Experience: {exp_years} years
  Skills: {skills_str}
  Career Path: {pos_str}
  Projects: {proj_count} projects
  Education: {edu_str}
"""
            summaries.append(summary.strip())

        return '\n\n'.join(summaries)
    ```

- [x] **Task 4: Add compressed format for large pools** (AC: 4.1.4)
  - [ ] Add compression for 50+ candidates:
    ```python
    def format_pool_compressed(candidates: list, max_detailed: int = 50) -> str:
        """Format pool with compression for large pools.

        First N candidates get full details, rest get summaries.
        """
        if len(candidates) <= max_detailed:
            return format_pool_for_gemini(candidates)

        # Detailed for first max_detailed
        detailed = format_pool_for_gemini(candidates[:max_detailed])

        # Summary for rest
        remaining = candidates[max_detailed:]
        avg_exp = sum(c.get('experience_years', 0) for c in remaining) / len(remaining)

        all_skills = []
        for c in remaining:
            all_skills.extend(c.get('skills', []))
        common_skills = list(set(all_skills))[:10]

        summary = f"""
--- Remaining {len(remaining)} candidates (summarized) ---
Average experience: {avg_exp:.1f} years
Common skills: {', '.join(common_skills)}
Note: These candidates have similar profiles to the detailed list above.
"""
        return detailed + '\n\n' + summary
    ```

- [x] **Task 5: Handle empty pool** (AC: 4.1.5)
  - [ ] Add empty pool handling:
    ```python
    def get_pool_summary(role_id: str) -> dict:
        """Get pool statistics.

        Returns:
            Dict with count, experience range, common skills
        """
        candidates = get_pool_for_role(role_id)

        if not candidates:
            return {
                "count": 0,
                "experience_range": None,
                "common_skills": [],
                "is_empty": True
            }

        exp_years = [c.get('experience_years', 0) for c in candidates]
        min_exp = min(exp_years)
        max_exp = max(exp_years)

        all_skills = []
        for c in candidates:
            all_skills.extend(c.get('skills', []))

        # Count skill occurrences
        skill_counts = {}
        for skill in all_skills:
            skill_counts[skill] = skill_counts.get(skill, 0) + 1

        # Top 10 skills
        top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            "count": len(candidates),
            "experience_range": f"{min_exp}-{max_exp} years",
            "common_skills": [s[0] for s in top_skills],
            "is_empty": False
        }
    ```

- [x] **Task 6: Test pool manager**
  - [ ] Test with populated pool:
    ```python
    candidates = get_pool_for_role("role-uuid")
    assert isinstance(candidates, list)
    ```
  - [ ] Test with empty pool:
    ```python
    candidates = get_pool_for_role("nonexistent-role")
    assert candidates == []
    ```
  - [ ] Test Gemini formatting
  - [ ] Test compressed format for large pools

## Dev Notes

### Architecture Alignment

This story implements the pool manager per architecture.md:
- **Purpose:** Fetch all active candidates for comparative ranking
- **Scope:** Current session + all past sessions
- **Filter:** Only status='active' candidates

### Pool Query

```sql
SELECT * FROM candidates
WHERE role_id = ? AND status = 'active'
ORDER BY uploaded_at DESC
```

### Candidate Summary Format

For Gemini prompt efficiency:
```
Candidate 1 (ID: uuid-123):
  Name: Sara Ahmed
  Experience: 4.5 years
  Skills: Python, Django, AWS, Docker
  Career Path: Junior → Mid → Senior
  Projects: 3 projects
  Education: B.Tech Computer Science
```

### Token Efficiency

| Pool Size | Strategy |
|-----------|----------|
| < 50 | Full details for all |
| 50-100 | First 50 detailed, rest summarized |
| > 100 | Consider pre-filtering |

### References

- [Source: docs/sprint-artifacts/tech-spec-epic-4.md#Pool-Manager]
- [Source: docs/architecture.md#Role-Based-Candidate-Pools]
- [Source: docs/epics.md#Story-4.1]
- [Source: docs/prd.md#FR19-FR20]

## Dev Agent Record

### Context Reference

None (proceeded without story context file)

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- Python syntax check passed
- All functional tests passed:
  - Empty pool returns empty list
  - Empty pool count is 0
  - Empty pool formatted correctly
  - Empty pool summary correct
  - Pool fetches all active candidates ordered by upload
  - Pool count matches
  - Gemini formatting includes all fields
  - Pool summary with experience range and common skills
  - Compression works for large pools
  - Analysis bundle contains all required fields

### Completion Notes List

- All 6 tasks completed successfully
- All 5 acceptance criteria satisfied:
  - AC4.1.1: Fetches ALL active candidates for role_id
  - AC4.1.2: Includes candidates from current + past sessions
  - AC4.1.3: Excludes superseded/hired/withdrew candidates
  - AC4.1.4: Returns formatted summaries suitable for Gemini prompt
  - AC4.1.5: Handles empty pool gracefully
- Added get_candidates_for_analysis() convenience function
- Compressed format for pools with 50+ candidates
- Pool summary includes experience range and skill frequency

### File List

**Created:**
- backend/services/pool_manager.py

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-12-20 | SM Agent (Bob) | Initial draft created |
| 2025-12-20 | Dev Agent (Amelia) | Implementation complete - all ACs satisfied |
