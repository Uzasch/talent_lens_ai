"""Ranking service for multi-level candidate evaluation."""

import json
import logging
import time
import google.generativeai as genai
from services.gemini_service import parse_gemini_response, MODEL_NAME, MAX_RETRIES, INITIAL_RETRY_DELAY, REQUEST_DELAY
from services.pool_manager import format_pool_for_gemini

logger = logging.getLogger(__name__)

# Dimensions for scoring
DIMENSIONS = ['experience', 'skills', 'projects', 'positions', 'education']


# Scoring prompt for threshold evaluation
SCORING_PROMPT = """Score each candidate on the 5 dimensions (0-100).
Scores should be RELATIVE to the job requirements - 50 is meets basic requirements, 80+ is excellent match.

JOB DESCRIPTION:
{job_description}

CANDIDATES:
{candidates}

Return ONLY valid JSON (no markdown):
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

Scoring Guidelines:
- experience: Based on years and relevance to the role
- skills: How well technical skills match JD requirements
- projects: Quality, complexity, and relevance of projects
- positions: Career progression and leadership roles
- education: Degree level and relevance to role

Use the actual candidate IDs from the input.
"""


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
                'reason': elimination_reason,
                'scores': candidate_scores
            })
        else:
            remaining.append(candidate)
            # Attach scores to remaining candidates
            candidate['_scores'] = candidate_scores

    logger.info(f"Threshold elimination: {len(eliminated)} eliminated, {len(remaining)} remaining")
    return remaining, eliminated


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
        # Add delay before API call to stay under rate limits
        time.sleep(REQUEST_DELAY)

        model = genai.GenerativeModel(MODEL_NAME)

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
        scores = data.get('scores', {})

        logger.info(f"Scored {len(scores)} candidates")
        return scores

    except Exception as e:
        logger.error(f"Scoring error: {e}")
        return {}


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
        # Extract dimension from reason (first word, lowercase)
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

    if not candidates:
        logger.info("No candidates to process")
        return {
            "remaining": [],
            "eliminated": [],
            "scores": {},
            "summary": get_elimination_summary([])
        }

    # Score all candidates
    logger.info(f"Scoring {len(candidates)} candidates for threshold check")
    scores = score_candidates_for_thresholds(job_description, candidates)

    # If scoring failed, return all candidates (fail open)
    if not scores:
        logger.warning("Scoring failed, skipping threshold elimination")
        return {
            "remaining": candidates,
            "eliminated": [],
            "scores": {},
            "summary": get_elimination_summary([]),
            "scoring_error": "Failed to score candidates"
        }

    # Apply thresholds
    remaining, eliminated = apply_thresholds(candidates, thresholds, scores)

    return {
        "remaining": remaining,
        "eliminated": eliminated,
        "scores": scores,
        "summary": get_elimination_summary(eliminated)
    }


# ============================================================================
# Level 3: Weighted Comparative Scoring
# ============================================================================

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
Return ONLY valid JSON (no markdown):
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
Use the actual candidate IDs from the input.
"""


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

    for dim in DIMENSIONS:
        score = scores.get(dim, 0)
        weight = weights.get(dim, 20)
        total += score * weight
        weight_sum += weight

    if weight_sum == 0:
        return 0

    return round(total / weight_sum)


def validate_weights(weights: dict) -> dict:
    """Ensure weights are valid and sum to 100.

    Args:
        weights: Raw weights dict

    Returns:
        Validated weights summing to 100
    """
    validated = {}
    for dim in DIMENSIONS:
        validated[dim] = weights.get(dim, 20)

    total = sum(validated.values())
    if total != 100 and total > 0:
        # Normalize to 100
        factor = 100 / total
        for dim in DIMENSIONS:
            validated[dim] = round(validated[dim] * factor)

        # Fix rounding errors
        diff = 100 - sum(validated.values())
        if diff != 0:
            validated['experience'] += diff

    return validated


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
            logger.warning(f"Unknown candidate_id in ranking: {cid}")
            continue

        # Validate scores
        scores = r.get('scores', {})
        for dim in DIMENSIONS:
            if dim not in scores:
                scores[dim] = 50  # Default to average
            else:
                # Clamp to 0-100
                scores[dim] = max(0, min(100, int(scores[dim])))

        r['scores'] = scores

        # Validate match score
        if 'match_score' not in r or not isinstance(r['match_score'], (int, float)):
            r['match_score'] = 50
        else:
            r['match_score'] = max(0, min(100, int(r['match_score'])))

        # Validate summary
        if not isinstance(r.get('summary'), list):
            r['summary'] = ['No summary available']
        else:
            # Ensure at least some content
            r['summary'] = [s for s in r['summary'] if s][:3]
            if not r['summary']:
                r['summary'] = ['No summary available']

        # Validate why_selected
        if not r.get('why_selected'):
            r['why_selected'] = 'See scores for details'

        # Validate compared_to_pool
        if not r.get('compared_to_pool'):
            r['compared_to_pool'] = ''

        validated.append(r)

    return validated


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
    if exp_years and exp_years > 0:
        summary.append(f"{exp_years} years of professional experience")

    # Skills
    skills = candidate.get('skills', [])
    if isinstance(skills, str):
        try:
            skills = json.loads(skills)
        except json.JSONDecodeError:
            skills = []
    if skills:
        top_skills = ', '.join(str(s) for s in skills[:4])
        summary.append(f"Skilled in {top_skills}")

    # Projects
    projects = candidate.get('projects', [])
    if isinstance(projects, str):
        try:
            projects = json.loads(projects)
        except json.JSONDecodeError:
            projects = []
    if projects:
        summary.append(f"{len(projects)} notable projects in portfolio")

    # Education
    education = candidate.get('education', [])
    if isinstance(education, str):
        try:
            education = json.loads(education)
        except json.JSONDecodeError:
            education = []
    if education and len(education) > 0:
        edu = education[0] if isinstance(education[0], str) else education[0].get('degree', '')
        if edu:
            summary.append(f"Education: {edu}")

    # Pad to 3 if needed
    while len(summary) < 3:
        summary.append("See full profile for details")

    return summary[:3]


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

    # Validate weights
    validated_weights = validate_weights(weights)

    # Process in batches if too many candidates (Gemini can't handle 80+ at once)
    BATCH_SIZE = 20
    if len(candidates) > BATCH_SIZE:
        logger.info(f"Processing {len(candidates)} candidates in batches of {BATCH_SIZE}")
        all_rankings = []

        for i in range(0, len(candidates), BATCH_SIZE):
            batch = candidates[i:i + BATCH_SIZE]
            logger.info(f"Ranking batch {i // BATCH_SIZE + 1}: {len(batch)} candidates")
            batch_rankings = _rank_single_batch(
                job_description, batch, validated_weights, priorities
            )
            all_rankings.extend(batch_rankings)

        # Re-sort all rankings by match_score and assign final ranks
        all_rankings.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        for i, r in enumerate(all_rankings):
            r['rank'] = i + 1

        logger.info(f"Ranked {len(all_rankings)} candidates across batches")
        return all_rankings

    return _rank_single_batch(job_description, candidates, validated_weights, priorities)


def _rank_single_batch(
    job_description: str,
    candidates: list,
    validated_weights: dict,
    priorities: dict
) -> list:
    """Rank a single batch of candidates."""
    if not candidates:
        return []

    model = genai.GenerativeModel(MODEL_NAME)

    # Format inputs
    candidates_text = format_pool_for_gemini(candidates)
    priorities_text = json.dumps(priorities, indent=2) if priorities else "{}"

    prompt = RANKING_PROMPT.format(
        job_description=job_description,
        priorities=priorities_text,
        exp_weight=validated_weights.get('experience', 20),
        skills_weight=validated_weights.get('skills', 20),
        projects_weight=validated_weights.get('projects', 20),
        positions_weight=validated_weights.get('positions', 20),
        edu_weight=validated_weights.get('education', 20),
        count=len(candidates),
        candidates=candidates_text
    )

    # Retry logic for rate limits
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            # Add delay before API call to stay under rate limits
            time.sleep(REQUEST_DELAY)

            response = model.generate_content(prompt)
            logger.info(f"Gemini ranking response (first 1000 chars): {response.text[:1000]}")
            data = parse_gemini_response(response.text)
            logger.info(f"Parsed rankings data keys: {data.keys() if data else 'None'}")
            logger.info(f"Number of rankings in response: {len(data.get('rankings', []))}")

            rankings = data.get('rankings', [])

            # Validate rankings
            rankings = validate_rankings(rankings, candidates)
            logger.info(f"After validation: {len(rankings)} rankings remain")

            # Recalculate match scores with our weights
            for r in rankings:
                r['match_score'] = calculate_match_score(r['scores'], validated_weights)

            # Sort by match score
            rankings.sort(key=lambda x: x.get('match_score', 0), reverse=True)

            # Assign final ranks
            for i, r in enumerate(rankings):
                r['rank'] = i + 1

            # Handle missing candidates (Gemini might skip some)
            ranked_ids = {r['candidate_id'] for r in rankings}
            for candidate in candidates:
                if candidate['id'] not in ranked_ids:
                    logger.warning(f"Candidate {candidate['id']} missing from rankings, adding with default scores")
                    default_scores = {dim: 50 for dim in DIMENSIONS}
                    rankings.append({
                        'candidate_id': candidate['id'],
                        'rank': len(rankings) + 1,
                        'match_score': calculate_match_score(default_scores, validated_weights),
                        'scores': default_scores,
                        'summary': generate_summary_fallback(candidate, default_scores),
                        'why_selected': 'Unable to fully evaluate',
                        'compared_to_pool': ''
                    })

            # Re-sort and re-rank after adding missing
            rankings.sort(key=lambda x: x.get('match_score', 0), reverse=True)
            for i, r in enumerate(rankings):
                r['rank'] = i + 1

            logger.info(f"Ranked {len(rankings)} candidates")
            return rankings

        except Exception as e:
            error_str = str(e)
            last_error = e
            if "429" in error_str or "quota" in error_str.lower():
                # Rate limit - wait and retry
                delay = INITIAL_RETRY_DELAY * (2 ** attempt)
                logger.warning(f"Ranking rate limit hit, retrying in {delay}s (attempt {attempt + 1}/{MAX_RETRIES})")
                time.sleep(delay)
            else:
                # Other error - break out of retry loop
                logger.error(f"Ranking error: {e}")
                break

    # All retries exhausted or non-retryable error
    logger.error(f"Ranking failed after retries: {last_error}")
    fallback = []
    for i, candidate in enumerate(candidates):
        default_scores = {dim: 50 for dim in DIMENSIONS}
        fallback.append({
            'candidate_id': candidate['id'],
            'rank': i + 1,
            'match_score': 50,
            'scores': default_scores,
            'summary': generate_summary_fallback(candidate, default_scores),
            'why_selected': 'Ranking unavailable due to error',
            'compared_to_pool': ''
        })
    return fallback


# ============================================================================
# Level 4: Tie-Breaker Logic
# ============================================================================

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

Return ONLY valid JSON (no markdown):
{{
  "tie_breaker_reason": "Your explanation"
}}
"""


def detect_tie_breaker_candidates(rankings: list, threshold: float = 5.0) -> set:
    """Identify candidates with close scores needing tie-breaker.

    Args:
        rankings: Sorted list of ranked candidates
        threshold: Score difference threshold (default 5%)

    Returns:
        Set of candidate IDs that need tie-breaker explanation
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

    return tie_breaker_ids


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
        model = genai.GenerativeModel(MODEL_NAME)

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


def rank_with_tie_breakers(
    job_description: str,
    candidates: list,
    weights: dict,
    priorities: dict,
    generate_detailed_explanations: bool = False
) -> list:
    """Rank candidates with tie-breaker logic.

    Args:
        job_description: JD text
        candidates: Remaining candidates after threshold
        weights: Dimension weights
        priorities: Inferred priorities
        generate_detailed_explanations: Whether to call Gemini for detailed tie-breaker explanations

    Returns:
        Ranked candidates with tie-breaker info
    """
    # Get base rankings
    rankings = rank_candidates_comparatively(
        job_description, candidates, weights, priorities
    )

    if not rankings:
        return rankings

    # Apply tie-breaker flags
    rankings = apply_tie_breaker_flags(rankings, priorities)

    # Optionally generate detailed explanations for tie-breaker pairs
    if generate_detailed_explanations:
        for i in range(len(rankings) - 1):
            current = rankings[i]
            next_c = rankings[i + 1]

            if (current.get('tie_breaker_applied') and
                next_c.get('tie_breaker_applied')):

                # Only generate if we don't have a good explanation yet
                if current.get('tie_breaker_reason', '').startswith('Higher ') or \
                   current.get('tie_breaker_reason', '').startswith('Based on'):
                    explanation = generate_tie_breaker_explanation(
                        current, next_c, priorities
                    )
                    current['tie_breaker_reason'] = explanation

    logger.info(f"Ranked {len(rankings)} candidates with tie-breaker logic")
    return rankings


def get_tie_breaker_summary(rankings: list) -> dict:
    """Get summary of tie-breaker applications.

    Args:
        rankings: Ranked candidates list

    Returns:
        Summary dict with counts and affected candidates
    """
    tie_breaker_candidates = [
        r for r in rankings if r.get('tie_breaker_applied')
    ]

    return {
        "count": len(tie_breaker_candidates),
        "affected_ranks": [r.get('rank') for r in tie_breaker_candidates],
        "candidates": [
            {
                "candidate_id": r.get('candidate_id'),
                "rank": r.get('rank'),
                "match_score": r.get('match_score'),
                "reason": r.get('tie_breaker_reason')
            }
            for r in tie_breaker_candidates
        ]
    }
