import sqlite3
import uuid
import json
import os
from config import Config


def get_db_connection():
    """Get database connection with Row factory."""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables."""
    os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create roles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS roles (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            normalized_title TEXT NOT NULL,
            weights TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(normalized_title)
        )
    ''')

    # Create sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            role_id TEXT NOT NULL,
            job_description TEXT NOT NULL,
            candidates_added INTEGER NOT NULL,
            pool_size_at_analysis INTEGER NOT NULL,
            inferred_priorities TEXT,
            priority_reasoning TEXT,
            thresholds_config TEXT,
            eliminated_count INTEGER DEFAULT 0,
            elimination_breakdown TEXT,
            why_not_others TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (role_id) REFERENCES roles(id)
        )
    ''')

    # Create candidates table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id TEXT PRIMARY KEY,
            role_id TEXT NOT NULL,
            session_id TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            resume_text TEXT,
            pdf_path TEXT,
            skills TEXT,
            experience_years REAL,
            experience_details TEXT,
            education TEXT,
            projects TEXT,
            positions TEXT,
            rank INTEGER,
            match_score INTEGER,
            education_score INTEGER,
            experience_score INTEGER,
            projects_score INTEGER,
            positions_score INTEGER,
            skills_score INTEGER,
            summary TEXT,
            why_selected TEXT,
            compared_to_pool TEXT,
            status TEXT DEFAULT 'active',
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_ranked_at TIMESTAMP,
            FOREIGN KEY (role_id) REFERENCES roles(id),
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    ''')

    # Create indexes
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_candidates_role
        ON candidates(role_id, status)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_candidates_email
        ON candidates(email)
    ''')

    conn.commit()
    conn.close()


# CRUD Functions for Roles

def normalize_role_title(title):
    """Normalize role title for matching."""
    title = title.lower().strip()

    # Remove common punctuation
    title = title.replace('.', '').replace(',', '')

    # Expand common abbreviations
    abbreviations = {
        'dev': 'developer',
        'sr': 'senior',
        'jr': 'junior',
        'mgr': 'manager',
        'eng': 'engineer',
        'sw': 'software',
        'fe': 'frontend',
        'be': 'backend',
        'fs': 'fullstack',
    }

    words = title.split()
    normalized = [abbreviations.get(w, w) for w in words]
    return ' '.join(normalized)


def get_candidate_count(role_id):
    """Get count of active candidates for a role."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT COUNT(*) FROM candidates WHERE role_id = ? AND status = ?',
        (role_id, 'active')
    )
    count = cursor.fetchone()[0]
    conn.close()
    return count


def create_role(title, weights=None):
    """Create a new role with UUID."""
    role_id = str(uuid.uuid4())
    normalized_title = normalize_role_title(title)
    weights_json = json.dumps(weights) if weights else None
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO roles (id, title, normalized_title, weights) VALUES (?, ?, ?, ?)',
        (role_id, title, normalized_title, weights_json)
    )
    conn.commit()
    conn.close()
    return role_id


def create_or_get_role(title, weights=None):
    """Create role or return existing if normalized title matches."""
    normalized = normalize_role_title(title)
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check for existing
    cursor.execute(
        'SELECT * FROM roles WHERE normalized_title = ?',
        (normalized,)
    )
    existing = cursor.fetchone()

    if existing:
        conn.close()
        return {
            **dict(existing),
            'is_new': False,
            'candidate_count': get_candidate_count(existing['id'])
        }

    # Create new
    role_id = str(uuid.uuid4())
    weights_json = json.dumps(weights) if weights else None

    cursor.execute('''
        INSERT INTO roles (id, title, normalized_title, weights)
        VALUES (?, ?, ?, ?)
    ''', (role_id, title, normalized, weights_json))

    conn.commit()
    conn.close()

    return {
        'id': role_id,
        'title': title,
        'normalized_title': normalized,
        'weights': weights_json,
        'is_new': True,
        'candidate_count': 0
    }


def get_role_by_id(role_id):
    """Fetch a single role by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM roles WHERE id = ?', (role_id,))
    role = cursor.fetchone()
    conn.close()
    return dict(role) if role else None


def get_roles():
    """Get all roles with candidate counts, session counts, and last analyzed date."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            r.id,
            r.title,
            r.normalized_title,
            r.weights,
            r.created_at,
            COUNT(DISTINCT c.id) as candidate_count,
            COUNT(DISTINCT s.id) as session_count,
            MAX(s.created_at) as last_analyzed
        FROM roles r
        LEFT JOIN candidates c ON r.id = c.role_id AND c.status = 'active'
        LEFT JOIN sessions s ON r.id = s.role_id
        GROUP BY r.id
        ORDER BY r.created_at DESC
    ''')

    roles = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return roles


# CRUD Functions for Sessions

def create_session(role_id, job_description, candidates_added, pool_size):
    """Create a new session with UUID."""
    session_id = str(uuid.uuid4())
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO sessions
           (id, role_id, job_description, candidates_added, pool_size_at_analysis)
           VALUES (?, ?, ?, ?, ?)''',
        (session_id, role_id, job_description, candidates_added, pool_size)
    )
    conn.commit()
    conn.close()
    return session_id


def get_session_by_id(session_id):
    """Fetch a single session by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM sessions WHERE id = ?', (session_id,))
    session = cursor.fetchone()
    conn.close()
    return dict(session) if session else None


def get_all_sessions():
    """Get all sessions with role info for history page.

    Returns:
        List of session dicts with role_title, top_match_score, priorities, and thresholds
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            s.id,
            s.role_id,
            r.title as role_title,
            s.job_description,
            s.candidates_added,
            s.pool_size_at_analysis,
            s.inferred_priorities,
            s.thresholds_config,
            s.created_at,
            (
                SELECT MAX(c.match_score)
                FROM candidates c
                WHERE c.session_id = s.id AND c.status = 'active'
            ) as top_match_score
        FROM sessions s
        JOIN roles r ON s.role_id = r.id
        ORDER BY s.created_at DESC
    ''')

    rows = cursor.fetchall()
    conn.close()

    sessions = []
    for row in rows:
        session = dict(row)
        # Parse JSON fields
        if session.get('inferred_priorities'):
            try:
                session['inferred_priorities'] = json.loads(session['inferred_priorities'])
            except json.JSONDecodeError:
                session['inferred_priorities'] = {}
        else:
            session['inferred_priorities'] = {}

        if session.get('thresholds_config'):
            try:
                session['thresholds_config'] = json.loads(session['thresholds_config'])
            except json.JSONDecodeError:
                session['thresholds_config'] = {}
        else:
            session['thresholds_config'] = {}

        sessions.append(session)

    return sessions


# CRUD Functions for Candidates

def create_candidate(data_dict):
    """Create a new candidate record."""
    candidate_id = str(uuid.uuid4())
    conn = get_db_connection()
    cursor = conn.cursor()

    # Build dynamic insert from data_dict
    data_dict['id'] = candidate_id
    columns = ', '.join(data_dict.keys())
    placeholders = ', '.join(['?' for _ in data_dict])
    values = list(data_dict.values())

    cursor.execute(
        f'INSERT INTO candidates ({columns}) VALUES ({placeholders})',
        values
    )
    conn.commit()
    conn.close()
    return candidate_id


def get_candidates_by_role(role_id, status='active'):
    """Fetch all candidates for a role with given status."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM candidates WHERE role_id = ? AND status = ? ORDER BY rank ASC',
        (role_id, status)
    )
    candidates = cursor.fetchall()
    conn.close()
    return [dict(row) for row in candidates]


def get_role_candidates_for_pool(role_id: str) -> list:
    """Get all active candidates for a role's pool with session info.

    Args:
        role_id: Role UUID

    Returns:
        List of candidates with name, email, match_score, session_date, etc.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            c.id,
            c.name,
            c.email,
            c.phone,
            c.match_score,
            c.rank,
            c.session_id,
            c.uploaded_at,
            c.status,
            s.created_at as session_date
        FROM candidates c
        LEFT JOIN sessions s ON c.session_id = s.id
        WHERE c.role_id = ? AND c.status = 'active'
        ORDER BY c.match_score DESC NULLS LAST, c.uploaded_at DESC
    ''', (role_id,))

    candidates = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return candidates


# Extended Candidate Functions for Story 3.4

def get_candidate_by_email(role_id: str, email: str) -> dict | None:
    """Find existing active candidate by email in role pool.

    Args:
        role_id: Role UUID to search within
        email: Email address to search for

    Returns:
        Candidate dict or None if not found
    """
    if not email:
        return None

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, name, email, status, uploaded_at
        FROM candidates
        WHERE role_id = ? AND LOWER(email) = ? AND status = 'active'
    ''', (role_id, email.lower()))

    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None


def supersede_candidate(candidate_id: str) -> bool:
    """Mark candidate as superseded (replaced by newer resume).

    Args:
        candidate_id: UUID of candidate to supersede

    Returns:
        True if successful
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE candidates
        SET status = 'superseded'
        WHERE id = ?
    ''', (candidate_id,))

    affected = cursor.rowcount
    conn.commit()
    conn.close()

    return affected > 0


def create_candidate_from_extraction(
    role_id: str,
    session_id: str,
    local_data: dict,
    gemini_data: dict,
    resume_text: str = None,
    pdf_path: str = None
) -> dict:
    """Create new candidate record with extracted data.

    Args:
        role_id: Role UUID
        session_id: Session UUID
        local_data: Dict with name, email, phone
        gemini_data: Dict with skills, experience, etc.
        resume_text: Raw text from PDF
        pdf_path: Path to stored PDF file

    Returns:
        Dict with candidate id and status
    """
    from datetime import datetime
    import logging
    logger = logging.getLogger(__name__)

    conn = get_db_connection()
    cursor = conn.cursor()

    candidate_id = str(uuid.uuid4())

    cursor.execute('''
        INSERT INTO candidates (
            id, role_id, session_id,
            name, email, phone, resume_text, pdf_path,
            skills, experience_years, experience_details,
            education, projects, positions,
            status, uploaded_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        candidate_id,
        role_id,
        session_id,
        local_data.get('name') or 'Unknown',
        local_data.get('email'),
        local_data.get('phone'),
        resume_text,
        pdf_path,
        json.dumps(gemini_data.get('skills', [])),
        gemini_data.get('experience_years', 0),
        json.dumps(gemini_data.get('experience_details', [])),
        json.dumps(gemini_data.get('education', [])),
        json.dumps(gemini_data.get('projects', [])),
        json.dumps(gemini_data.get('positions', [])),
        'active',
        datetime.utcnow().isoformat()
    ))

    conn.commit()
    conn.close()

    logger.info(f"Created candidate {candidate_id} for role {role_id}")

    return {
        "id": candidate_id,
        "name": local_data.get('name'),
        "email": local_data.get('email'),
        "status": "created"
    }


def store_candidate_with_duplicate_check(
    role_id: str,
    session_id: str,
    local_data: dict,
    gemini_data: dict,
    resume_text: str = None,
    pdf_path: str = None
) -> dict:
    """Store candidate with duplicate detection.

    If email already exists in pool, supersedes old candidate.

    Args:
        role_id: Role UUID
        session_id: Session UUID
        local_data: Dict with name, email, phone
        gemini_data: Dict with structured extraction
        resume_text: Raw resume text
        pdf_path: Path to PDF file

    Returns:
        Dict with candidate info and duplicate status
    """
    import logging
    logger = logging.getLogger(__name__)

    email = local_data.get('email')
    result = {
        "candidate_id": None,
        "is_duplicate": False,
        "superseded_id": None,
        "status": "failed"
    }

    # Check for existing candidate with same email
    if email:
        existing = get_candidate_by_email(role_id, email)
        if existing:
            result["is_duplicate"] = True
            result["superseded_id"] = existing['id']
            supersede_candidate(existing['id'])
            logger.info(f"Superseding existing candidate {existing['id']} with email {email}")

    # Create new candidate
    candidate = create_candidate_from_extraction(
        role_id=role_id,
        session_id=session_id,
        local_data=local_data,
        gemini_data=gemini_data,
        resume_text=resume_text,
        pdf_path=pdf_path
    )

    result["candidate_id"] = candidate['id']
    result["name"] = candidate.get('name')
    result["email"] = candidate.get('email')
    result["status"] = "created"

    return result


def get_candidate_by_id(candidate_id: str) -> dict | None:
    """Get full candidate record by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM candidates WHERE id = ?', (candidate_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    candidate = dict(row)

    # Parse JSON fields
    for field in ['skills', 'experience_details', 'education', 'projects', 'positions', 'summary']:
        if candidate.get(field):
            try:
                candidate[field] = json.loads(candidate[field])
            except json.JSONDecodeError:
                pass

    return candidate


def get_candidates_by_session(session_id: str) -> list:
    """Get all candidates added in a session."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, name, email, status, uploaded_at
        FROM candidates
        WHERE session_id = ?
        ORDER BY uploaded_at DESC
    ''', (session_id,))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def create_session_for_upload(role_id: str, job_description: str = '') -> dict:
    """Create new analysis session for upload.

    Args:
        role_id: Role UUID
        job_description: JD text (optional at upload time)

    Returns:
        Dict with session id
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    session_id = str(uuid.uuid4())

    cursor.execute('''
        INSERT INTO sessions (id, role_id, job_description, candidates_added, pool_size_at_analysis)
        VALUES (?, ?, ?, 0, 0)
    ''', (session_id, role_id, job_description))

    conn.commit()
    conn.close()

    return {"id": session_id}


def update_session_counts(session_id: str, candidates_added: int, pool_size: int) -> None:
    """Update session with final counts after processing."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE sessions
        SET candidates_added = ?, pool_size_at_analysis = ?
        WHERE id = ?
    ''', (candidates_added, pool_size, session_id))

    conn.commit()
    conn.close()


def update_session_priorities(session_id: str, priorities: dict, reasoning: str) -> None:
    """Store inferred priorities in session.

    Args:
        session_id: Session UUID
        priorities: Dict with dimension priorities
        reasoning: Explanation of priority assignments
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE sessions
        SET inferred_priorities = ?, priority_reasoning = ?
        WHERE id = ?
    ''', (json.dumps(priorities), reasoning, session_id))

    conn.commit()
    conn.close()


def get_session_priorities(session_id: str) -> dict | None:
    """Get inferred priorities for a session.

    Args:
        session_id: Session UUID

    Returns:
        Dict with priorities and reasoning, or None if not set
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT inferred_priorities, priority_reasoning
        FROM sessions
        WHERE id = ?
    ''', (session_id,))

    row = cursor.fetchone()
    conn.close()

    if not row or not row['inferred_priorities']:
        return None

    return {
        "inferred_priorities": json.loads(row['inferred_priorities']),
        "reasoning": row['priority_reasoning']
    }


def update_session_eliminations(session_id: str, elimination_data: dict) -> None:
    """Store elimination results in session.

    Args:
        session_id: Session UUID
        elimination_data: Dict with count and breakdown from threshold elimination
    """
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


def update_session_thresholds(session_id: str, thresholds_config: dict) -> None:
    """Store thresholds configuration in session.

    Args:
        session_id: Session UUID
        thresholds_config: Dict with threshold settings used in analysis
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE sessions
        SET thresholds_config = ?
        WHERE id = ?
    ''', (json.dumps(thresholds_config), session_id))

    conn.commit()
    conn.close()


def update_session_why_not_others(session_id: str, why_not_others: str) -> None:
    """Store why-not-others explanation in session.

    Args:
        session_id: Session UUID
        why_not_others: AI-generated explanation text
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE sessions
        SET why_not_others = ?
        WHERE id = ?
    ''', (why_not_others, session_id))

    conn.commit()
    conn.close()


def get_session_eliminations(session_id: str) -> dict | None:
    """Get elimination data for a session.

    Args:
        session_id: Session UUID

    Returns:
        Dict with count and breakdown, or None if not set
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT eliminated_count, elimination_breakdown
        FROM sessions
        WHERE id = ?
    ''', (session_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    breakdown = {}
    if row['elimination_breakdown']:
        try:
            breakdown = json.loads(row['elimination_breakdown'])
        except json.JSONDecodeError:
            pass

    return {
        "count": row['eliminated_count'] or 0,
        "breakdown": breakdown
    }


def get_top_candidates(role_id: str, limit: int = 6) -> list:
    """Get top ranked candidates for a role.

    Args:
        role_id: Role UUID
        limit: Number of top candidates to return

    Returns:
        List of candidate dicts with all fields needed for dashboard
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, name, email, rank, match_score,
               experience_score, skills_score, projects_score,
               positions_score, education_score,
               summary, why_selected, compared_to_pool
        FROM candidates
        WHERE role_id = ? AND status = 'active' AND rank IS NOT NULL
        ORDER BY rank ASC
        LIMIT ?
    ''', (role_id, limit))

    rows = cursor.fetchall()
    conn.close()

    candidates = []
    for row in rows:
        candidate = dict(row)
        # Parse summary JSON if it exists
        if candidate.get('summary'):
            try:
                candidate['summary'] = json.loads(candidate['summary'])
            except json.JSONDecodeError:
                candidate['summary'] = []
        else:
            candidate['summary'] = []

        # Build scores object
        candidate['scores'] = {
            'experience': candidate.pop('experience_score') or 0,
            'skills': candidate.pop('skills_score') or 0,
            'projects': candidate.pop('projects_score') or 0,
            'positions': candidate.pop('positions_score') or 0,
            'education': candidate.pop('education_score') or 0
        }

        # Check for tie-breaker (same match_score as adjacent candidate)
        candidate['tie_breaker_applied'] = False

        candidates.append(candidate)

    # Mark tie-breakers (candidates with same match_score)
    for i, c in enumerate(candidates):
        if i > 0 and c['match_score'] == candidates[i - 1]['match_score']:
            c['tie_breaker_applied'] = True
            candidates[i - 1]['tie_breaker_applied'] = True

    return candidates


def get_eliminated_candidates(role_id: str, session_id: str) -> dict:
    """Get eliminated candidates for a session.

    Args:
        role_id: Role UUID
        session_id: Session UUID

    Returns:
        Dict with count, breakdown, and candidate details
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get session elimination data
    cursor.execute('''
        SELECT eliminated_count, elimination_breakdown
        FROM sessions
        WHERE id = ?
    ''', (session_id,))

    session_row = cursor.fetchone()

    if not session_row:
        conn.close()
        return {"count": 0, "breakdown": {}, "candidates": []}

    count = session_row['eliminated_count'] or 0
    breakdown = {}
    if session_row['elimination_breakdown']:
        try:
            breakdown = json.loads(session_row['elimination_breakdown'])
        except json.JSONDecodeError:
            pass

    # Get eliminated candidates (status = 'eliminated')
    cursor.execute('''
        SELECT name, why_selected as reason
        FROM candidates
        WHERE role_id = ? AND status = 'eliminated'
        ORDER BY name ASC
    ''', (role_id,))

    eliminated_rows = cursor.fetchall()
    conn.close()

    candidates = []
    for row in eliminated_rows:
        candidates.append({
            "name": row['name'],
            "reason": row['reason'] or "Below threshold"
        })

    return {
        "count": count,
        "breakdown": breakdown,
        "candidates": candidates
    }


def get_session_stats(session_id: str) -> dict:
    """Get statistics for a session.

    Args:
        session_id: Session UUID

    Returns:
        Dict with total_in_pool, added_this_session, eliminated_count, ranked_count
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT candidates_added, pool_size_at_analysis, eliminated_count
        FROM sessions
        WHERE id = ?
    ''', (session_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return {
            "total_in_pool": 0,
            "added_this_session": 0,
            "eliminated_count": 0,
            "ranked_count": 0
        }

    pool_size = row['pool_size_at_analysis'] or 0
    eliminated = row['eliminated_count'] or 0
    added = row['candidates_added'] or 0

    return {
        "total_in_pool": pool_size,
        "added_this_session": added,
        "eliminated_count": eliminated,
        "ranked_count": pool_size - eliminated
    }


def get_full_session_data(session_id: str) -> dict | None:
    """Get complete session data for dashboard display.

    Args:
        session_id: Session UUID

    Returns:
        Dict with all dashboard data or None if session not found
    """
    # Get session
    session = get_session_by_id(session_id)
    if not session:
        return None

    role_id = session['role_id']

    # Get role
    role = get_role_by_id(role_id)
    if not role:
        return None

    # Get stats
    stats = get_session_stats(session_id)

    # Get priorities
    priorities_data = get_session_priorities(session_id)
    inferred_priorities = priorities_data['inferred_priorities'] if priorities_data else {}
    priority_reasoning = priorities_data['reasoning'] if priorities_data else ''

    # Get top candidates
    candidates = get_top_candidates(role_id, limit=6)

    # Get eliminated data
    eliminated = get_eliminated_candidates(role_id, session_id)

    # Get stored why_not_others or generate fallback
    why_not_others = session.get('why_not_others')
    if not why_not_others:
        why_not_others = generate_why_not_others_text(stats, eliminated)

    # Parse thresholds config if stored
    thresholds_config = {}
    if session.get('thresholds_config'):
        try:
            thresholds_config = json.loads(session['thresholds_config'])
        except json.JSONDecodeError:
            pass

    return {
        "session": {
            "id": session['id'],
            "role_title": role['title'],
            "job_description": session['job_description'],
            "created_at": session['created_at'],
            "thresholds_config": thresholds_config
        },
        "stats": stats,
        "inferred_priorities": inferred_priorities,
        "priority_reasoning": priority_reasoning,
        "candidates": candidates,
        "eliminated": eliminated,
        "why_not_others": why_not_others,
        "common_gaps": []  # TODO: Generate from analysis data
    }


def generate_why_not_others_text(stats: dict, eliminated: dict) -> str:
    """Generate AI-style explanation for non-selected candidates.

    Args:
        stats: Session statistics
        eliminated: Elimination data

    Returns:
        Explanation text
    """
    total = stats.get('total_in_pool', 0)
    eliminated_count = stats.get('eliminated_count', 0)
    ranked = stats.get('ranked_count', 0)
    below_top_6 = max(0, ranked - 6)

    if total <= 6 and eliminated_count == 0:
        return f"All {total} candidates in the pool are displayed above."

    parts = [f"{total} candidates evaluated in this pool."]

    if eliminated_count > 0:
        breakdown = eliminated.get('breakdown', {})
        reasons = []
        for dim, count in breakdown.items():
            reasons.append(f"{count} for {dim}")
        if reasons:
            parts.append(f"{eliminated_count} were eliminated for not meeting minimum thresholds ({', '.join(reasons)}).")
        else:
            parts.append(f"{eliminated_count} were eliminated for not meeting minimum thresholds.")

    if below_top_6 > 0:
        parts.append(f"The remaining {below_top_6} candidates passed thresholds but ranked below the top 6 due to lower weighted scores in CRITICAL dimensions.")

    return " ".join(parts)
