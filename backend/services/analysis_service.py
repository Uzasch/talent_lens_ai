"""Analysis service - Full pipeline orchestration."""

import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from models import (
    create_or_get_role,
    create_session,
    update_session_counts,
    update_session_priorities,
    update_session_eliminations,
    update_session_thresholds,
    update_session_why_not_others,
    store_candidate_with_duplicate_check,
    get_db_connection
)
from services.pdf_parser import process_pdf_file
from services.local_extractor import extract_basic_info
from services.gemini_service import extract_structured_data, detect_job_priorities
from services.pool_manager import get_pool_for_role
from services.ranking_service import (
    process_threshold_elimination,
    rank_with_tie_breakers,
    validate_weights,
    get_tie_breaker_summary
)

logger = logging.getLogger(__name__)

# Progress phases for frontend tracking
ANALYSIS_PHASES = [
    "Extracting resumes",
    "Building candidate pool",
    "Analyzing job requirements",
    "Applying thresholds",
    "Ranking candidates",
    "Generating explanations",
    "Complete"
]


def process_single_resume(file, role_id: str, session_id: str) -> dict | None:
    """Process a single resume through Phase 1.

    Args:
        file: Flask FileStorage object
        role_id: Role UUID
        session_id: Session UUID

    Returns:
        Candidate dict or None if failed
    """
    try:
        # Extract PDF text
        pdf_result = process_pdf_file(file)
        if pdf_result['status'] == 'failed':
            logger.warning(f"Failed to process PDF: {file.filename}")
            return None

        resume_text = pdf_result['text']
        pdf_path = pdf_result.get('file_path')

        # Local extraction (name, email, phone)
        local_data = extract_basic_info(resume_text)

        # Gemini extraction (skills, experience, etc.)
        gemini_data = extract_structured_data(resume_text)

        # Store candidate with duplicate check
        result = store_candidate_with_duplicate_check(
            role_id=role_id,
            session_id=session_id,
            local_data=local_data,
            gemini_data=gemini_data,
            resume_text=resume_text,
            pdf_path=pdf_path
        )

        logger.info(f"Processed: {local_data.get('name')} ({result['status']})")
        return result

    except Exception as e:
        logger.error(f"Resume processing error for {file.filename}: {e}")
        return None


def generate_why_not_others(
    rankings: list,
    eliminated: list,
    pool_size: int
) -> str:
    """Generate explanation for candidates not in top 6.

    Args:
        rankings: All ranked candidates
        eliminated: Eliminated candidates
        pool_size: Total pool size

    Returns:
        Explanation string
    """
    top_6 = rankings[:6]
    below_top_6 = rankings[6:]

    parts = []

    # Total summary
    parts.append(f"{pool_size} candidates in pool.")

    # Eliminated info
    if eliminated:
        elim_count = len(eliminated)
        parts.append(f"{elim_count} eliminated by thresholds.")

    # Below top 6 info
    if below_top_6:
        parts.append(f"{len(below_top_6)} candidates ranked below top 6.")

        # Common gaps
        if len(below_top_6) > 3 and top_6:
            avg_score = sum(c.get('match_score', 0) for c in below_top_6) / len(below_top_6)
            top_6_min = min(c.get('match_score', 0) for c in top_6)
            gap = top_6_min - avg_score
            if gap > 0:
                parts.append(f"Average gap from top 6: {gap:.0f}%.")

    return ' '.join(parts)


def store_rankings(session_id: str, rankings: list) -> None:
    """Store ranking results in candidates table.

    Args:
        session_id: Session UUID
        rankings: List of ranked candidates
    """
    if not rankings:
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    for r in rankings:
        scores = r.get('scores', {})
        cursor.execute('''
            UPDATE candidates
            SET rank = ?,
                match_score = ?,
                experience_score = ?,
                skills_score = ?,
                projects_score = ?,
                positions_score = ?,
                education_score = ?,
                summary = ?,
                why_selected = ?,
                compared_to_pool = ?,
                last_ranked_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            r.get('rank'),
            r.get('match_score'),
            scores.get('experience'),
            scores.get('skills'),
            scores.get('projects'),
            scores.get('positions'),
            scores.get('education'),
            json.dumps(r.get('summary', [])),
            r.get('why_selected'),
            r.get('compared_to_pool'),
            r.get('candidate_id')
        ))

    conn.commit()
    conn.close()
    logger.info(f"Stored rankings for {len(rankings)} candidates")


def run_full_analysis(
    role_title: str,
    job_description: str,
    files: list,
    weights: dict,
    thresholds: dict
) -> dict:
    """Run complete analysis pipeline.

    Phase 1: Extract data from each PDF
    Phase 2: Multi-level ranking

    Args:
        role_title: Title of the role
        job_description: Job description text
        files: List of Flask FileStorage objects
        weights: Dimension weights
        thresholds: Threshold configuration

    Returns:
        Complete analysis result
    """
    logger.info(f"Starting analysis for role: {role_title}")

    # Validate and normalize weights
    weights = validate_weights(weights)

    # Step 1: Create/get role
    role = create_or_get_role(role_title, weights)
    role_id = role['id']
    logger.info(f"Role: {role_id} (is_new: {role.get('is_new')})")

    # Step 2: Create session
    session_id = create_session(role_id, job_description, 0, 0)
    logger.info(f"Session: {session_id}")

    # Step 3: Phase 1 - Extract data from PDFs (concurrent processing)
    logger.info(f"Phase 1: Extracting {len(files)} resumes with concurrent processing")
    new_candidates = []
    extraction_errors = []

    # Use ThreadPoolExecutor for concurrent PDF processing
    # Limit to 1 worker to stay within Gemini free tier rate limits
    max_workers = 1

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all files for processing
        future_to_file = {
            executor.submit(process_single_resume, file, role_id, session_id): file
            for file in files
        }

        # Collect results as they complete
        for i, future in enumerate(as_completed(future_to_file)):
            file = future_to_file[future]
            try:
                candidate = future.result()
                if candidate:
                    new_candidates.append(candidate)
                else:
                    extraction_errors.append(file.filename)
            except Exception as e:
                logger.error(f"Error processing {file.filename}: {e}")
                extraction_errors.append(file.filename)

            # Log progress every 10 resumes
            if (i + 1) % 10 == 0:
                logger.info(f"Progress: {i + 1}/{len(files)} resumes processed")

    logger.info(f"Phase 1 complete: {len(new_candidates)} candidates extracted")
    if extraction_errors:
        logger.warning(f"Failed to extract: {extraction_errors}")

    # Step 4: Fetch full pool
    pool = get_pool_for_role(role_id)
    pool_size = len(pool)
    logger.info(f"Pool size: {pool_size} candidates")

    # Step 5: Level 1 - Infer priorities
    logger.info("Phase 2 Level 1: Detecting priorities")
    priority_result = detect_job_priorities(job_description)
    priorities = priority_result.get('inferred_priorities', {})
    priority_reasoning = priority_result.get('reasoning', '')

    # Store priorities in session
    update_session_priorities(session_id, priorities, priority_reasoning)

    # Step 6: Level 2 - Apply thresholds
    logger.info("Phase 2 Level 2: Applying thresholds")
    threshold_result = process_threshold_elimination(
        job_description, pool, thresholds
    )
    remaining = threshold_result['remaining']
    eliminated = threshold_result['eliminated']
    elimination_summary = threshold_result['summary']

    # Store thresholds config and elimination results
    update_session_thresholds(session_id, thresholds)
    update_session_eliminations(session_id, elimination_summary)

    # Step 7: Level 3 & 4 - Rank with tie-breakers
    logger.info(f"Phase 2 Level 3-4: Ranking {len(remaining)} candidates")
    rankings = []
    if remaining:
        rankings = rank_with_tie_breakers(
            job_description, remaining, weights, priorities
        )

    # Step 8: Store rankings
    if rankings:
        store_rankings(session_id, rankings)

    # Step 9: Update session with results
    update_session_counts(session_id, len(new_candidates), pool_size)

    # Step 10: Build response
    top_candidates = rankings[:6]  # Top 6 for dashboard

    # Get tie-breaker summary
    tie_breaker_info = get_tie_breaker_summary(rankings) if rankings else {"count": 0}

    # Generate and store why-not-others explanation
    why_not_others_text = generate_why_not_others(rankings, eliminated, pool_size)
    update_session_why_not_others(session_id, why_not_others_text)

    return {
        "session_id": session_id,
        "role": {
            "id": role_id,
            "title": role_title,
            "is_new": role.get('is_new', False),
            "total_in_pool": pool_size
        },
        "extraction": {
            "uploaded": len(files),
            "processed": len(new_candidates),
            "failed": len(extraction_errors),
            "errors": extraction_errors if extraction_errors else None
        },
        "inferred_priorities": priorities,
        "priority_reasoning": priority_reasoning,
        "eliminated": elimination_summary,
        "rankings_summary": {
            "total_ranked": len(rankings),
            "tie_breakers_applied": tie_breaker_info['count']
        },
        "top_candidates": format_top_candidates(top_candidates, pool),
        "why_not_others": why_not_others_text
    }


def format_top_candidates(top_candidates: list, pool: list) -> list:
    """Format top candidates with additional info from pool.

    Args:
        top_candidates: List of ranking dicts
        pool: Full candidate pool

    Returns:
        Formatted candidate list
    """
    # Create lookup for pool data
    pool_lookup = {c['id']: c for c in pool}

    formatted = []
    for ranking in top_candidates:
        cid = ranking.get('candidate_id')
        pool_data = pool_lookup.get(cid, {})

        formatted.append({
            "candidate_id": cid,
            "rank": ranking.get('rank'),
            "name": pool_data.get('name', 'Unknown'),
            "email": pool_data.get('email'),
            "match_score": ranking.get('match_score'),
            "scores": ranking.get('scores', {}),
            "summary": ranking.get('summary', []),
            "why_selected": ranking.get('why_selected'),
            "compared_to_pool": ranking.get('compared_to_pool'),
            "tie_breaker_applied": ranking.get('tie_breaker_applied', False),
            "tie_breaker_reason": ranking.get('tie_breaker_reason')
        })

    return formatted
