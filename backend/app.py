from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os
import json
import logging
import re
from models import (
    init_db, get_roles, create_or_get_role, get_full_session_data,
    get_session_by_id, get_candidate_by_id, get_role_by_id, get_all_sessions,
    get_role_candidates_for_pool
)
from services.analysis_service import run_full_analysis
from services.gemini_service import generate_comparison_explanation
from services.email_service import EmailService

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=['http://localhost:5173'], supports_credentials=True)

# Initialize database on startup
init_db()
logger.info('Database initialized')

# Ensure required directories exist
os.makedirs('uploads', exist_ok=True)
os.makedirs('data', exist_ok=True)


# Response helper functions
def success_response(data, status_code=200):
    """Standard success response format."""
    return jsonify({
        'success': True,
        'data': data
    }), status_code


def error_response(code, message, status_code=400):
    """Standard error response format."""
    return jsonify({
        'success': False,
        'error': {
            'code': code,
            'message': message
        }
    }), status_code


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': {
            'code': 'NOT_FOUND',
            'message': 'Resource not found'
        }
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': {
            'code': 'INTERNAL_ERROR',
            'message': 'An internal error occurred'
        }
    }), 500


# Routes
@app.route('/')
def index():
    return {'message': 'TalentLens AI Backend'}


@app.route('/api/health')
def health_check():
    return success_response({'status': 'ok'})


@app.route('/api/roles', methods=['GET'])
def list_roles():
    """Get all roles with candidate counts."""
    try:
        roles = get_roles()
        return success_response({'roles': roles})
    except Exception as e:
        logger.error(f'Error fetching roles: {e}')
        return error_response('FETCH_ERROR', str(e), 500)


@app.route('/api/roles/<role_id>/candidates', methods=['GET'])
def get_role_candidates(role_id):
    """Get all candidates in a role's pool.

    Returns candidates for the role pool view with name, email,
    match_score, and session date.
    """
    try:
        # Verify role exists
        role = get_role_by_id(role_id)
        if not role:
            return error_response('NOT_FOUND', 'Role not found', 404)

        candidates = get_role_candidates_for_pool(role_id)

        return success_response({
            'role': {
                'id': role['id'],
                'title': role['title']
            },
            'candidates': candidates,
            'total': len(candidates)
        })

    except Exception as e:
        logger.error(f'Error fetching role candidates: {e}')
        return error_response('FETCH_ERROR', str(e), 500)


@app.route('/api/roles', methods=['POST'])
def create_role():
    """Create new role or return existing if normalized title matches."""
    try:
        data = request.get_json()

        if not data or not data.get('title'):
            return error_response('VALIDATION_ERROR', 'Title is required', 400)

        title = data['title'].strip()
        weights = data.get('weights')

        # Validate weights if provided
        if weights:
            required_keys = {'experience', 'projects', 'positions', 'skills', 'education'}
            if set(weights.keys()) != required_keys:
                return error_response('VALIDATION_ERROR', 'Invalid weights keys', 400)
            if sum(weights.values()) != 100:
                return error_response('VALIDATION_ERROR', 'Weights must sum to 100', 400)

        role = create_or_get_role(title, weights)
        return success_response(role, 201 if role['is_new'] else 200)

    except Exception as e:
        logger.error(f'Error creating role: {e}')
        return error_response('CREATE_ERROR', str(e), 500)


@app.route('/api/sessions', methods=['GET'])
def list_sessions():
    """Get all sessions for history page."""
    try:
        sessions = get_all_sessions()
        return success_response({'sessions': sessions})
    except Exception as e:
        logger.error(f'Error fetching sessions: {e}')
        return error_response('FETCH_ERROR', str(e), 500)


@app.route('/api/sessions/<session_id>', methods=['GET'])
def get_session_results(session_id):
    """Get complete session data for dashboard display.

    Returns all data needed by the results dashboard:
    - Session info and role
    - Stats (pool size, eliminated, ranked)
    - Inferred priorities with reasoning
    - Top 6 candidates with scores
    - Eliminated candidates with reasons
    - Why not others explanation
    """
    try:
        data = get_full_session_data(session_id)

        if not data:
            return error_response('NOT_FOUND', 'Session not found', 404)

        return success_response(data)

    except Exception as e:
        logger.error(f'Error fetching session {session_id}: {e}')
        return error_response('FETCH_ERROR', str(e), 500)


@app.route('/api/analyze', methods=['POST'])
def analyze_resumes():
    """Full analysis pipeline endpoint.

    Accepts multipart/form-data with:
    - role_title: string (required)
    - job_description: string (required)
    - weights: JSON string (optional)
    - thresholds: JSON string (optional)
    - files: PDF files (required, at least one)

    Returns complete analysis with rankings.
    """
    try:
        # Parse request
        role_title = request.form.get('role_title', '').strip()
        job_description = request.form.get('job_description', '').strip()

        # Parse JSON fields
        weights_str = request.form.get('weights', '{}')
        thresholds_str = request.form.get('thresholds', '{}')

        try:
            weights = json.loads(weights_str) if weights_str else {}
        except json.JSONDecodeError:
            return error_response('VALIDATION_ERROR', 'Invalid weights JSON', 400)

        try:
            thresholds = json.loads(thresholds_str) if thresholds_str else {}
        except json.JSONDecodeError:
            return error_response('VALIDATION_ERROR', 'Invalid thresholds JSON', 400)

        files = request.files.getlist('files')

        # Validate required fields
        if not role_title:
            return error_response('VALIDATION_ERROR', 'Role title is required', 400)
        if not job_description:
            return error_response('VALIDATION_ERROR', 'Job description is required', 400)
        if not files or len(files) == 0:
            return error_response('VALIDATION_ERROR', 'At least one resume file is required', 400)

        # Filter out empty files
        valid_files = [f for f in files if f and f.filename]
        if not valid_files:
            return error_response('VALIDATION_ERROR', 'No valid files provided', 400)

        # Run analysis pipeline
        logger.info(f"Starting analysis: {len(valid_files)} files for '{role_title}'")
        result = run_full_analysis(
            role_title=role_title,
            job_description=job_description,
            files=valid_files,
            weights=weights,
            thresholds=thresholds
        )

        logger.info(f"Analysis complete: session {result['session_id']}")
        return success_response(result)

    except Exception as e:
        logger.error(f'Analysis error: {e}', exc_info=True)
        return error_response('ANALYSIS_ERROR', str(e), 500)


# Helper functions for comparison endpoint

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


def format_candidate_for_comparison(candidate: dict) -> dict:
    """Format candidate data for comparison response."""
    return {
        'id': candidate.get('id'),
        'name': candidate.get('name'),
        'rank': candidate.get('rank'),
        'match_score': candidate.get('match_score'),
        'scores': {
            'experience': candidate.get('experience_score', 0) or 0,
            'skills': candidate.get('skills_score', 0) or 0,
            'projects': candidate.get('projects_score', 0) or 0,
            'positions': candidate.get('positions_score', 0) or 0,
            'education': candidate.get('education_score', 0) or 0
        }
    }


@app.route('/api/compare', methods=['POST'])
def compare_candidates():
    """Compare two candidates with AI explanation.

    Request body:
    {
        "session_id": "uuid",
        "candidate_id_1": "uuid",
        "candidate_id_2": "uuid"
    }

    Returns comparison data with dimension winners and AI explanation.
    """
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
        if not session:
            return error_response('NOT_FOUND', 'Session not found', 404)

        priorities_str = session.get('inferred_priorities', '{}')
        try:
            priorities = json.loads(priorities_str) if priorities_str else {}
        except json.JSONDecodeError:
            priorities = {}

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


# Email validation helper
def is_valid_email(email: str) -> bool:
    """Basic email format validation."""
    if not email:
        return False
    pattern = r'^[\w.+-]+@[\w.-]+\.\w+$'
    return bool(re.match(pattern, email))


@app.route('/api/send-emails', methods=['POST'])
def send_emails():
    """Send interview invitation emails to candidates.

    Request body:
    {
        "session_id": "uuid",
        "candidate_emails": [{"name": "...", "email": "..."}],
        "interview_slots": [{"date": "...", "time": "..."}],
        "message_template": "Dear {name}...",
        "job_title": "...",
        "company": "..."
    }

    Returns sent/failed counts and per-recipient results.
    """
    try:
        data = request.get_json()

        session_id = data.get('session_id')
        recipients = data.get('candidate_emails', [])
        slots = data.get('interview_slots', [])
        message_template = data.get('message_template', '')
        job_title = data.get('job_title', '')
        company = data.get('company', 'Our Company')

        # Validation
        if not recipients:
            return error_response(
                'VALIDATION_ERROR',
                'No recipients specified',
                400
            )

        if not slots:
            return error_response(
                'VALIDATION_ERROR',
                'No interview slots specified',
                400
            )

        if not message_template:
            return error_response(
                'VALIDATION_ERROR',
                'Message template is required',
                400
            )

        # Validate email formats and log warnings
        valid_recipients = []
        for recipient in recipients:
            email = recipient.get('email', '')
            if is_valid_email(email):
                valid_recipients.append(recipient)
            else:
                logger.warning(f'Invalid email format skipped: {email}')

        if not valid_recipients:
            return error_response(
                'VALIDATION_ERROR',
                'No valid email addresses provided',
                400
            )

        # Get session for context (optional - for job title fallback)
        if session_id and not job_title:
            session = get_session_by_id(session_id)
            if session:
                role = get_role_by_id(session['role_id'])
                job_title = role['title'] if role else 'the position'

        # Ensure we have a job title
        if not job_title:
            job_title = 'the position'

        # Log email batch start
        logger.info(f'Email batch started: {len(valid_recipients)} recipients')
        logger.info(f'Interview slots: {json.dumps(slots)}')

        # Send emails
        email_service = EmailService()
        result = email_service.send_bulk(
            recipients=valid_recipients,
            job_title=job_title,
            company=company,
            slots=slots,
            message_template=message_template
        )

        logger.info(
            f'Emails sent: {result["sent"]} success, {result["failed"]} failed'
        )

        return success_response(result)

    except Exception as e:
        logger.error(f'Email send error: {e}')
        return error_response('EMAIL_ERROR', str(e), 500)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
