"""Gemini API service for structured resume data extraction."""

import os
import json
import time
import logging
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
logger = logging.getLogger(__name__)

# Configure Gemini API
API_KEY = os.getenv('GEMINI_API_KEY')
if not API_KEY or API_KEY == 'your_gemini_api_key_here':
    logger.warning("GEMINI_API_KEY not configured in environment")
else:
    genai.configure(api_key=API_KEY)

# Model configuration
MODEL_NAME = 'models/gemini-2.5-flash'

# Extraction prompt template
EXTRACTION_PROMPT = """Extract structured data from this resume text.

Resume Text:
{resume_text}

Return ONLY valid JSON with this exact structure (no markdown, no explanation):
{{
  "skills": ["skill1", "skill2", ...],
  "experience_years": 4.5,
  "experience_details": [
    {{
      "role": "Job Title",
      "company": "Company Name",
      "duration": "2 years",
      "highlights": ["Achievement 1", "Achievement 2"]
    }}
  ],
  "education": [
    {{
      "degree": "Degree Name",
      "institution": "University Name",
      "year": 2020
    }}
  ],
  "projects": [
    {{
      "name": "Project Name",
      "description": "Brief description",
      "technologies": ["tech1", "tech2"],
      "impact": "Measurable impact if mentioned"
    }}
  ],
  "positions": [
    {{"title": "Position Title", "year": 2018}}
  ]
}}

Rules:
- Extract ALL skills mentioned (programming languages, frameworks, tools, soft skills)
- experience_years should be TOTAL years of professional work experience
- positions should show career progression chronologically (earliest first)
- Include all jobs in experience_details, most recent first
- For projects, include personal, academic, and professional projects
- If information is not found, use empty arrays [] or 0 for numbers
- Return ONLY the JSON object, no other text or markdown
"""


def parse_gemini_response(response_text: str) -> dict:
    """Parse Gemini response, handling markdown code blocks.

    Args:
        response_text: Raw response from Gemini

    Returns:
        Parsed dict or empty structure on failure
    """
    try:
        # Remove markdown code blocks if present
        text = response_text.strip()

        if text.startswith('```json'):
            text = text[7:]
        elif text.startswith('```'):
            text = text[3:]

        if text.endswith('```'):
            text = text[:-3]

        text = text.strip()

        # Parse JSON
        data = json.loads(text)

        # Validate types
        if not isinstance(data.get('skills'), list):
            data['skills'] = []
        if not isinstance(data.get('experience_years'), (int, float)):
            data['experience_years'] = 0
        if not isinstance(data.get('experience_details'), list):
            data['experience_details'] = []
        if not isinstance(data.get('education'), list):
            data['education'] = []
        if not isinstance(data.get('projects'), list):
            data['projects'] = []
        if not isinstance(data.get('positions'), list):
            data['positions'] = []

        return data

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini response as JSON: {e}")
        logger.debug(f"Response was: {response_text[:500]}")
        return {}


def extract_structured_data(resume_text: str) -> dict:
    """Extract structured data from resume using Gemini API.

    Args:
        resume_text: Raw text content of resume

    Returns:
        Dict with extracted structured data
    """
    # Default structure for failures
    default_response = {
        "skills": [],
        "experience_years": 0,
        "experience_details": [],
        "education": [],
        "projects": [],
        "positions": [],
        "extraction_error": None
    }

    if not resume_text or not resume_text.strip():
        default_response["extraction_error"] = "Empty resume text"
        return default_response

    if not API_KEY or API_KEY == 'your_gemini_api_key_here':
        default_response["extraction_error"] = "GEMINI_API_KEY not configured"
        return default_response

    try:
        # Truncate very long resumes to avoid token limits
        max_chars = 10000
        if len(resume_text) > max_chars:
            resume_text = resume_text[:max_chars]
            logger.info(f"Resume text truncated to {max_chars} chars")

        # Create model and generate
        model = genai.GenerativeModel(MODEL_NAME)
        prompt = EXTRACTION_PROMPT.format(resume_text=resume_text)

        response = model.generate_content(prompt)

        # Parse response
        response_text = response.text.strip()
        data = parse_gemini_response(response_text)

        # Merge with defaults for missing fields
        for key in default_response:
            if key not in data and key != "extraction_error":
                data[key] = default_response[key]

        logger.info("Gemini extraction successful")
        return data

    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        default_response["extraction_error"] = str(e)
        return default_response


def extract_with_retry(resume_text: str, max_retries: int = 2) -> dict:
    """Extract with retry on failure.

    Args:
        resume_text: Resume text content
        max_retries: Maximum retry attempts

    Returns:
        Extracted data dict
    """
    last_error = None

    for attempt in range(max_retries + 1):
        try:
            result = extract_structured_data(resume_text)

            # Check if extraction was successful
            if not result.get("extraction_error"):
                return result

            last_error = result.get("extraction_error")
            logger.warning(f"Extraction attempt {attempt + 1} failed: {last_error}")

        except Exception as e:
            last_error = str(e)
            logger.warning(f"Extraction attempt {attempt + 1} error: {e}")

        # Wait before retry (exponential backoff)
        if attempt < max_retries:
            wait_time = 2 ** attempt
            logger.info(f"Retrying in {wait_time} seconds...")
            time.sleep(wait_time)

    # Return with error after all retries
    return {
        "skills": [],
        "experience_years": 0,
        "experience_details": [],
        "education": [],
        "projects": [],
        "positions": [],
        "extraction_error": f"Failed after {max_retries + 1} attempts: {last_error}"
    }


def validate_extraction(data: dict) -> dict:
    """Validate and clean extracted data.

    Args:
        data: Extracted data dict

    Returns:
        Validated data with quality score
    """
    quality_score = 0
    issues = []

    # Check skills
    if data.get('skills') and len(data['skills']) > 0:
        quality_score += 20
    else:
        issues.append("No skills extracted")

    # Check experience
    if data.get('experience_years', 0) > 0:
        quality_score += 20
    if data.get('experience_details') and len(data['experience_details']) > 0:
        quality_score += 20
    else:
        issues.append("No experience details")

    # Check education
    if data.get('education') and len(data['education']) > 0:
        quality_score += 20

    # Check projects
    if data.get('projects') and len(data['projects']) > 0:
        quality_score += 20

    data['_quality_score'] = quality_score
    data['_quality_issues'] = issues

    return data


# Priority Detection for Multi-Level Ranking (Story 4.2)

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

# Priority level weights for scoring
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

    if not API_KEY or API_KEY == 'your_gemini_api_key_here':
        default_response["detection_error"] = "GEMINI_API_KEY not configured"
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

        logger.info(f"Priority detection successful: {priorities}")
        return {
            "inferred_priorities": priorities,
            "reasoning": data.get('reasoning', 'Analysis completed'),
            "detection_error": None
        }

    except Exception as e:
        logger.error(f"Priority detection error: {e}")
        default_response["detection_error"] = str(e)
        return default_response


# Candidate Comparison Explanation (Story 5.11)

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

Return ONLY valid JSON (no markdown):
{{
  "explanation": "2-3 sentence explanation of why {winner_name} ranks higher than {loser_name}, referencing specific scores and CRITICAL dimensions",
  "key_differences": [
    "Experience: Specific comparison between candidates",
    "Skills: Specific comparison between candidates",
    "Any other notable difference"
  ]
}}

Focus on:
1. CRITICAL dimension differences (these matter most)
2. Specific score gaps
3. What makes the winner stand out
"""


def generate_comparison_explanation(
    candidate1: dict,
    candidate2: dict,
    priorities: dict
) -> dict:
    """Generate AI explanation comparing two candidates.

    Args:
        candidate1: First candidate data
        candidate2: Second candidate data
        priorities: Inferred priorities dict with dimension levels

    Returns:
        Dict with explanation and key_differences
    """
    # Determine winner based on match scores
    score1 = candidate1.get('match_score', 0) or 0
    score2 = candidate2.get('match_score', 0) or 0

    if score1 >= score2:
        winner_name = candidate1.get('name', 'Candidate A')
        loser_name = candidate2.get('name', 'Candidate B')
    else:
        winner_name = candidate2.get('name', 'Candidate B')
        loser_name = candidate1.get('name', 'Candidate A')

    # Get critical dimensions
    critical_dims = [d for d, p in priorities.items() if p == 'CRITICAL']

    # Build fallback explanation
    score_diff = abs(score1 - score2)
    fallback = {
        'explanation': f'{winner_name} ranks higher with a {score_diff}% score advantage. The weighted scoring considers dimension importance based on the job requirements.',
        'key_differences': [
            f"Overall: {candidate1.get('name')} {score1}% vs {candidate2.get('name')} {score2}%"
        ]
    }

    if not API_KEY or API_KEY == 'your_gemini_api_key_here':
        logger.warning("GEMINI_API_KEY not configured - using fallback comparison")
        return fallback

    try:
        model = genai.GenerativeModel(MODEL_NAME)

        prompt = COMPARISON_PROMPT.format(
            rank_1=candidate1.get('rank', 1),
            name_1=candidate1.get('name', 'Candidate A'),
            score_1=score1,
            exp_1=candidate1.get('experience_score', 0) or 0,
            skills_1=candidate1.get('skills_score', 0) or 0,
            proj_1=candidate1.get('projects_score', 0) or 0,
            pos_1=candidate1.get('positions_score', 0) or 0,
            edu_1=candidate1.get('education_score', 0) or 0,
            rank_2=candidate2.get('rank', 2),
            name_2=candidate2.get('name', 'Candidate B'),
            score_2=score2,
            exp_2=candidate2.get('experience_score', 0) or 0,
            skills_2=candidate2.get('skills_score', 0) or 0,
            proj_2=candidate2.get('projects_score', 0) or 0,
            pos_2=candidate2.get('positions_score', 0) or 0,
            edu_2=candidate2.get('education_score', 0) or 0,
            critical_dims=', '.join(critical_dims) if critical_dims else 'None specified',
            winner_name=winner_name,
            loser_name=loser_name
        )

        response = model.generate_content(prompt)
        data = parse_gemini_response(response.text)

        logger.info("Comparison explanation generated successfully")
        return {
            'explanation': data.get('explanation', fallback['explanation']),
            'key_differences': data.get('key_differences', fallback['key_differences'])
        }

    except Exception as e:
        logger.error(f'Comparison explanation error: {e}')
        return fallback
