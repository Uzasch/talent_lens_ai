# Story 2.6: Roles API

Status: review

## Story

As a **frontend application**,
I want **to manage roles via REST API**,
so that **candidate pools can be created, fetched, and matched**.

## Acceptance Criteria

1. **AC2.6.1:** GET /api/roles returns list of existing roles with id, title, and candidate_count
2. **AC2.6.2:** POST /api/roles creates new role if normalized title doesn't exist, otherwise returns existing
3. **AC2.6.3:** Role includes weights JSON if specified in request
4. **AC2.6.4:** Response includes is_new flag indicating if role was created or matched

## Tasks / Subtasks

- [x] **Task 1: Add role normalization function to models.py** (AC: 2.6.2)
  - [x] Add normalization logic:
    ```python
    def normalize_role_title(title):
        """Normalize role title for matching."""
        title = title.lower().strip()

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
    ```

- [x] **Task 2: Add role CRUD functions to models.py** (AC: 2.6.1, 2.6.2)
  - [x] Add get_roles function:
    ```python
    def get_roles():
        """Get all roles with candidate counts."""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT r.id, r.title, r.normalized_title, r.weights, r.created_at,
                   COUNT(c.id) as candidate_count
            FROM roles r
            LEFT JOIN candidates c ON r.id = c.role_id AND c.status = 'active'
            GROUP BY r.id
            ORDER BY r.created_at DESC
        ''')

        roles = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return roles
    ```
  - [x] Add create_or_get_role function:
    ```python
    import uuid
    import json

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
    ```

- [x] **Task 3: Implement GET /api/roles endpoint** (AC: 2.6.1)
  - [x] Add to app.py:
    ```python
    from models import get_roles

    @app.route('/api/roles', methods=['GET'])
    def list_roles():
        try:
            roles = get_roles()
            return success_response({'roles': roles})
        except Exception as e:
            logger.error(f'Error fetching roles: {e}')
            return error_response('FETCH_ERROR', str(e), 500)
    ```

- [x] **Task 4: Implement POST /api/roles endpoint** (AC: 2.6.2, 2.6.3, 2.6.4)
  - [x] Add to app.py:
    ```python
    from flask import request
    from models import create_or_get_role

    @app.route('/api/roles', methods=['POST'])
    def create_role():
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
    ```

- [x] **Task 5: Add helper function for candidate count**
  - [x] Add to models.py:
    ```python
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
    ```

- [x] **Task 6: Test API endpoints**
  - [x] Test GET /api/roles (empty list initially):
    ```bash
    curl http://localhost:5000/api/roles
    # Expected: {"success": true, "data": {"roles": []}}
    ```
  - [x] Test POST /api/roles (create new):
    ```bash
    curl -X POST http://localhost:5000/api/roles \
      -H "Content-Type: application/json" \
      -d '{"title": "Python Dev"}'
    # Expected: {"success": true, "data": {"id": "...", "is_new": true}}
    ```
  - [x] Test POST /api/roles (match existing):
    ```bash
    curl -X POST http://localhost:5000/api/roles \
      -H "Content-Type: application/json" \
      -d '{"title": "Python Developer"}'
    # Expected: {"success": true, "data": {"id": "...", "is_new": false}}
    ```

## Dev Notes

### Architecture Alignment

This story implements the Roles API per architecture.md:
- **Endpoints:** GET and POST /api/roles
- **Normalization:** Server-side title normalization
- **Response Format:** Standard success/error format from Story 1.4

### API Contracts

**GET /api/roles**
```json
{
  "success": true,
  "data": {
    "roles": [
      {
        "id": "uuid-1",
        "title": "Python Developer",
        "normalized_title": "python developer",
        "weights": null,
        "candidate_count": 15,
        "created_at": "2025-12-20T10:00:00"
      }
    ]
  }
}
```

**POST /api/roles**
```json
// Request
{
  "title": "Python Dev",
  "weights": {
    "experience": 25,
    "projects": 20,
    "positions": 15,
    "skills": 25,
    "education": 15
  }
}

// Response
{
  "success": true,
  "data": {
    "id": "uuid-new",
    "title": "Python Dev",
    "normalized_title": "python developer",
    "is_new": true,
    "candidate_count": 0
  }
}
```

### Normalization Examples

| Input | Normalized |
|-------|------------|
| "Python Dev" | "python developer" |
| "Sr. React Engineer" | "senior react engineer" |
| "Jr Python Dev" | "junior python developer" |
| "FE Developer" | "frontend developer" |

### Development Sequence

This story should be implemented BEFORE Story 2.1 since the frontend depends on the API. However, Story 2.1 can use mock data during parallel development.

### References

- [Source: docs/sprint-artifacts/tech-spec-epic-2.md#APIs-and-Interfaces]
- [Source: docs/architecture.md#API-Contracts]
- [Source: docs/epics.md#Story-2.6]
- [Source: docs/prd.md#FR1-FR3]

## Dev Agent Record

### Context Reference

None (proceeded without story context file)

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- Python syntax check passed
- Direct model tests passed for normalization and CRUD functions

### Completion Notes List

- All 6 tasks completed successfully
- All 4 acceptance criteria satisfied:
  - AC2.6.1: GET /api/roles returns list with id, title, and candidate_count
  - AC2.6.2: POST /api/roles creates new or returns existing based on normalized title
  - AC2.6.3: Role includes weights JSON if specified in request
  - AC2.6.4: Response includes is_new flag
- Normalization handles abbreviations (dev->developer, sr->senior, etc.)
- Punctuation removed before normalization (Sr. -> senior)
- Weights validation ensures correct keys and sum to 100

### File List

**Modified:**
- backend/models.py (added normalize_role_title, get_candidate_count, create_or_get_role, updated get_roles with candidate_count JOIN)
- backend/app.py (added GET and POST /api/roles endpoints)

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-12-20 | SM Agent (Bob) | Initial draft created |
| 2025-12-20 | Dev Agent (Amelia) | Implementation complete - all ACs satisfied |
