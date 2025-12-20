"""Pool manager service for fetching and formatting candidate pools."""

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

        summary = f"""Candidate {i} (ID: {c['id']}):
  Name: {c.get('name', 'Unknown')}
  Experience: {exp_years} years
  Skills: {skills_str}
  Career Path: {pos_str}
  Projects: {proj_count} projects
  Education: {edu_str}"""
        summaries.append(summary)

    return '\n\n'.join(summaries)


def format_pool_compressed(candidates: list, max_detailed: int = 50) -> str:
    """Format pool with compression for large pools.

    First N candidates get full details, rest get summaries.

    Args:
        candidates: List of candidate dicts
        max_detailed: Maximum candidates to show in detail

    Returns:
        Formatted string with detailed + summarized sections
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
Note: These candidates have similar profiles to the detailed list above."""

    return detailed + '\n\n' + summary


def get_pool_summary(role_id: str) -> dict:
    """Get pool statistics.

    Args:
        role_id: UUID of the role

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


def get_candidates_for_analysis(role_id: str) -> dict:
    """Get candidates and formatted pool for analysis.

    Convenience function that returns both raw data and formatted text.

    Args:
        role_id: UUID of the role

    Returns:
        Dict with candidates list, formatted text, and summary
    """
    candidates = get_pool_for_role(role_id)

    return {
        "candidates": candidates,
        "formatted_text": format_pool_compressed(candidates),
        "summary": get_pool_summary(role_id),
        "count": len(candidates)
    }
