# Story 7.3: Sessions List API

Status: review

## Story

As a **frontend**,
I want **to fetch past sessions**,
So that **I can display history**.

## Acceptance Criteria

1. **AC7.3.1:** GET /api/sessions returns array of sessions
2. **AC7.3.2:** Each session includes: id, role_id, role_title, created_at
3. **AC7.3.3:** Each session includes: candidates_added, pool_size_at_analysis
4. **AC7.3.4:** Each session includes: top_match_score, thresholds_used, inferred_priorities
5. **AC7.3.5:** Results sorted by date descending

## Tasks / Subtasks

- [ ] **Task 1: Create GET /api/sessions endpoint** (AC: 7.3.1-7.3.5)
  - [ ] Add to `backend/app.py`:
    ```python
    @app.route('/api/sessions', methods=['GET'])
    def get_sessions():
        try:
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
                        SELECT MAX(match_score)
                        FROM candidates
                        WHERE session_id = s.id AND status = 'active'
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
                session['inferred_priorities'] = json.loads(
                    session.get('inferred_priorities') or '{}'
                )
                session['thresholds_config'] = json.loads(
                    session.get('thresholds_config') or '{}'
                )
                sessions.append(session)

            return success_response({'sessions': sessions})

        except Exception as e:
            logger.error(f'Error fetching sessions: {e}')
            return error_response('FETCH_ERROR', str(e), 500)
    ```

- [ ] **Task 2: Create GET /api/roles endpoint** (AC: 7.3.1)
  - [ ] Add to `backend/app.py`:
    ```python
    @app.route('/api/roles', methods=['GET'])
    def get_roles_list():
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT
                    r.id,
                    r.title,
                    r.created_at,
                    COUNT(DISTINCT CASE WHEN c.status = 'active' THEN c.id END) as candidate_count,
                    COUNT(DISTINCT s.id) as session_count,
                    MAX(s.created_at) as last_analyzed
                FROM roles r
                LEFT JOIN candidates c ON r.id = c.role_id
                LEFT JOIN sessions s ON r.id = s.role_id
                GROUP BY r.id
                ORDER BY last_analyzed DESC NULLS LAST
            ''')

            roles = [dict(row) for row in cursor.fetchall()]
            conn.close()

            return success_response({'roles': roles})

        except Exception as e:
            logger.error(f'Error fetching roles: {e}')
            return error_response('FETCH_ERROR', str(e), 500)
    ```

- [ ] **Task 3: Add frontend API functions**
  - [ ] Add to `src/services/api.js`:
    ```javascript
    export const getSessions = async () => {
      const response = await api.get('/sessions');
      return response.data;
    };

    export const getRoles = async () => {
      const response = await api.get('/roles');
      return response.data;
    };

    export const getRoleCandidates = async (roleId) => {
      const response = await api.get(`/roles/${roleId}/candidates`);
      return response.data;
    };
    ```

- [ ] **Task 4: Add models.py helper functions**
  - [ ] Add query helpers:
    ```python
    def get_all_sessions() -> list:
        """Get all sessions with role info."""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                s.*,
                r.title as role_title
            FROM sessions s
            JOIN roles r ON s.role_id = r.id
            ORDER BY s.created_at DESC
        ''')

        sessions = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return sessions

    def get_all_roles_with_stats() -> list:
        """Get all roles with candidate and session counts."""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                r.id,
                r.title,
                r.created_at,
                COUNT(DISTINCT CASE WHEN c.status = 'active' THEN c.id END) as candidate_count,
                COUNT(DISTINCT s.id) as session_count,
                MAX(s.created_at) as last_analyzed
            FROM roles r
            LEFT JOIN candidates c ON r.id = c.role_id
            LEFT JOIN sessions s ON r.id = s.role_id
            GROUP BY r.id
            ORDER BY last_analyzed DESC NULLS LAST
        ''')

        roles = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return roles
    ```

- [ ] **Task 5: Add pagination support (optional)**
  - [ ] Support limit and offset:
    ```python
    @app.route('/api/sessions', methods=['GET'])
    def get_sessions():
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)

        # ... query with LIMIT and OFFSET
        cursor.execute('''
            SELECT ...
            ORDER BY s.created_at DESC
            LIMIT ? OFFSET ?
        ''', (limit, offset))

        # Get total count for pagination
        cursor.execute('SELECT COUNT(*) FROM sessions')
        total = cursor.fetchone()[0]

        return success_response({
            'sessions': sessions,
            'total': total,
            'limit': limit,
            'offset': offset
        })
    ```

- [ ] **Task 6: Test sessions list API**
  - [ ] Test GET /api/sessions returns sessions:
    ```bash
    curl http://localhost:5000/api/sessions
    ```
  - [ ] Verify sessions sorted by date DESC
  - [ ] Verify JSON fields parsed correctly
  - [ ] Verify top_match_score calculated
  - [ ] Test GET /api/roles returns roles

## Dev Notes

### Architecture Alignment

This story creates the history data APIs:
- **GET /api/sessions:** List all analysis sessions
- **GET /api/roles:** List all roles with stats
- **Sorting:** Most recent first

### API Response: GET /api/sessions

```json
{
  "success": true,
  "data": {
    "sessions": [
      {
        "id": "session-uuid",
        "role_id": "role-uuid",
        "role_title": "Python Developer",
        "job_description": "We are looking for...",
        "candidates_added": 10,
        "pool_size_at_analysis": 45,
        "inferred_priorities": {
          "experience": "CRITICAL",
          "skills": "CRITICAL"
        },
        "thresholds_config": {
          "experience": {"enabled": true, "minimum": 60}
        },
        "top_match_score": 94,
        "created_at": "2025-12-20T10:30:00Z"
      }
    ]
  }
}
```

### API Response: GET /api/roles

```json
{
  "success": true,
  "data": {
    "roles": [
      {
        "id": "role-uuid",
        "title": "Python Developer",
        "candidate_count": 45,
        "session_count": 3,
        "last_analyzed": "2025-12-20T10:30:00Z",
        "created_at": "2025-12-15T08:00:00Z"
      }
    ]
  }
}
```

### Query Optimizations

| Query | Index Used |
|-------|------------|
| Sessions list | sessions.created_at DESC |
| Roles list | roles.id GROUP BY |
| Candidate count | idx_candidates_role |

### JSON Field Handling

Fields stored as JSON strings in SQLite:
- `inferred_priorities` → parsed to dict
- `thresholds_config` → parsed to dict

### References

- [Source: docs/sprint-artifacts/tech-spec-epic-7.md#API-Endpoints]
- [Source: docs/architecture.md#API-Contracts]
- [Source: docs/epics.md#Story-7.3]
- [Source: docs/prd.md#FR66]

## Dev Agent Record

### Context Reference

docs/sprint-artifacts/7-3-sessions-list-api.md

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- GET /api/sessions already implemented in Story 7-2
- Updated get_all_sessions() to include inferred_priorities and thresholds_config
- JSON parsing added for both fields with error handling
- API tested: returns all required fields with proper JSON parsing

### Completion Notes List

- All 5 acceptance criteria satisfied:
  - AC7.3.1: GET /api/sessions returns array of sessions ✅
  - AC7.3.2: Each session includes id, role_id, role_title, created_at ✅
  - AC7.3.3: Each session includes candidates_added, pool_size_at_analysis ✅
  - AC7.3.4: Each session includes top_match_score, thresholds_config, inferred_priorities ✅
  - AC7.3.5: Results sorted by created_at DESC ✅
- Most implementation already done in Story 7-2
- Added JSON parsing for inferred_priorities and thresholds_config fields
- Frontend API functions (getSessions, getRoles) already added in Story 7-2

### File List

**Modified:**
- backend/models.py (updated get_all_sessions to include and parse priorities/thresholds)

**Already existed from Story 7-2:**
- backend/app.py (GET /api/sessions endpoint)
- frontend/src/services/api.js (getSessions, getRoles functions)

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-12-20 | SM Agent (Bob) | Initial draft created |
| 2025-12-20 | Dev Agent (Amelia) | Implementation complete - added missing fields to API |
