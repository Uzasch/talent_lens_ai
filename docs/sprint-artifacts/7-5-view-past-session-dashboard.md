# Story 7.5: View Past Session Dashboard

Status: review

## Story

As a **HR professional**,
I want **to click on a past session to view its dashboard**,
So that **I can review previous analyses**.

## Acceptance Criteria

1. **AC7.5.1:** Clicking a session in History navigates to /dashboard/:sessionId
2. **AC7.5.2:** Dashboard loads with that session's data
3. **AC7.5.3:** All data is restored (stats, top candidates, explanations)
4. **AC7.5.4:** Email selection still works for past sessions

## Tasks / Subtasks

- [ ] **Task 1: Ensure session click navigates to dashboard** (AC: 7.5.1)
  - [ ] Already implemented in SessionsList:
    ```jsx
    import { useNavigate } from 'react-router-dom';

    function SessionsList({ sessions, loading }) {
      const navigate = useNavigate();

      return (
        <div className="space-y-3">
          {sessions.map((session) => (
            <Card
              key={session.id}
              className="cursor-pointer hover:border-primary transition-colors"
              onClick={() => navigate(`/dashboard/${session.id}`)}
            >
              {/* ... card content ... */}
            </Card>
          ))}
        </div>
      );
    }
    ```

- [ ] **Task 2: Ensure GET /api/sessions/:id returns full data** (AC: 7.5.2, 7.5.3)
  - [ ] Verify endpoint returns all required data:
    ```python
    @app.route('/api/sessions/<session_id>', methods=['GET'])
    def get_session_results(session_id):
        try:
            session = get_session_by_id(session_id)
            if not session:
                return error_response('NOT_FOUND', 'Session not found', 404)

            role = get_role_by_id(session['role_id'])
            top_candidates = get_top_candidates(session_id, limit=6)
            eliminated = get_eliminated_candidates(session_id)
            stats = get_session_stats(session_id)

            return success_response({
                'session': {
                    'id': session['id'],
                    'role_id': session['role_id'],
                    'job_description': session['job_description'],
                    'created_at': session['created_at']
                },
                'role': {
                    'id': role['id'],
                    'title': role['title']
                },
                'stats': stats,
                'inferred_priorities': session.get('inferred_priorities', {}),
                'priority_reasoning': session.get('priority_reasoning'),
                'top_candidates': top_candidates,
                'eliminated': eliminated,
                'why_not_others': session.get('why_not_others')
            })

        except Exception as e:
            logger.error(f'Error fetching session: {e}')
            return error_response('FETCH_ERROR', str(e), 500)
    ```

- [ ] **Task 3: Add helper functions for session data** (AC: 7.5.3)
  - [ ] Add to `models.py`:
    ```python
    def get_top_candidates(session_id: str, limit: int = 6) -> list:
        """Get top ranked candidates for a session."""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                c.*
            FROM candidates c
            WHERE c.session_id = ?
              AND c.status = 'active'
              AND c.rank IS NOT NULL
            ORDER BY c.rank ASC
            LIMIT ?
        ''', (session_id, limit))

        candidates = []
        for row in cursor.fetchall():
            candidate = dict(row)
            # Parse JSON fields
            candidate['summary'] = json.loads(candidate.get('summary') or '[]')
            candidate['skills'] = json.loads(candidate.get('skills') or '[]')
            candidates.append(candidate)

        conn.close()
        return candidates

    def get_eliminated_candidates(session_id: str) -> dict:
        """Get eliminated candidates info for a session."""
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get candidates that were eliminated (rank is NULL or status is eliminated)
        cursor.execute('''
            SELECT
                c.id,
                c.name,
                c.email
            FROM candidates c
            WHERE c.session_id = ?
              AND c.rank IS NULL
              AND c.status = 'active'
        ''', (session_id,))

        eliminated_candidates = [dict(row) for row in cursor.fetchall()]
        conn.close()

        # For now, return basic structure
        # Full elimination tracking would need additional fields
        return {
            'count': len(eliminated_candidates),
            'candidates': eliminated_candidates
        }

    def get_session_stats(session_id: str) -> dict:
        """Get statistics for a session."""
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get session info
        cursor.execute('''
            SELECT
                candidates_added,
                pool_size_at_analysis
            FROM sessions
            WHERE id = ?
        ''', (session_id,))

        session_row = cursor.fetchone()

        # Get ranked count
        cursor.execute('''
            SELECT COUNT(*)
            FROM candidates
            WHERE session_id = ?
              AND rank IS NOT NULL
              AND status = 'active'
        ''', (session_id,))

        ranked_count = cursor.fetchone()[0]

        conn.close()

        if not session_row:
            return {}

        return {
            'total_in_pool': session_row['pool_size_at_analysis'],
            'added_this_session': session_row['candidates_added'],
            'ranked_count': ranked_count,
            'eliminated_count': session_row['pool_size_at_analysis'] - ranked_count
        }
    ```

- [ ] **Task 4: Verify DashboardPage loads session data** (AC: 7.5.2)
  - [ ] Ensure useParams gets sessionId:
    ```jsx
    import { useParams } from 'react-router-dom';
    import { getSession } from '@/services/api';

    function DashboardPage() {
      const { sessionId } = useParams();
      const [data, setData] = useState(null);
      const [loading, setLoading] = useState(true);

      useEffect(() => {
        if (sessionId) {
          fetchSessionData();
        }
      }, [sessionId]);

      const fetchSessionData = async () => {
        setLoading(true);
        try {
          const response = await getSession(sessionId);
          if (response.success) {
            setData(response.data);
          }
        } catch (error) {
          console.error('Failed to load session:', error);
        } finally {
          setLoading(false);
        }
      };

      // ... render dashboard with data
    }
    ```

- [ ] **Task 5: Show session date on dashboard** (AC: 7.5.2)
  - [ ] Add session timestamp to header:
    ```jsx
    function DashboardHeader({ session, role }) {
      return (
        <div className="mb-6">
          <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
            <Calendar className="h-4 w-4" />
            Analysis from {formatDate(session.created_at)}
          </div>
          <h1 className="text-2xl font-bold">{role.title}</h1>
          <p className="text-muted-foreground mt-1 line-clamp-2">
            {session.job_description}
          </p>
        </div>
      );
    }
    ```

- [ ] **Task 6: Ensure email works for past sessions** (AC: 7.5.4)
  - [ ] Verify sessionId is passed to EmailModal:
    ```jsx
    <EmailModal
      open={showEmailModal}
      onClose={() => setShowEmailModal(false)}
      selectedCandidates={selectedForEmail}
      sessionId={sessionId}  // Pass the sessionId
      jobTitle={data?.role?.title}
    />
    ```

- [ ] **Task 7: Test past session viewing**
  - [ ] Navigate to History page
  - [ ] Click on a past session
  - [ ] Verify dashboard loads with correct data
  - [ ] Verify stats show correctly
  - [ ] Verify candidates display correctly
  - [ ] Verify priorities and explanations show
  - [ ] Test email selection works

## Dev Notes

### Architecture Alignment

This story enables viewing saved analysis sessions:
- **Navigation:** History → Click session → Dashboard
- **Data:** Full session data from GET /api/sessions/:id
- **Functionality:** All dashboard features work

### Navigation Flow

```
History Page
     │
     ▼
SessionsList
     │
     └── onClick={() => navigate(`/dashboard/${session.id}`)}
           │
           ▼
     DashboardPage
           │
           └── useParams() → sessionId
                 │
                 └── getSession(sessionId)
                       │
                       └── Full dashboard renders
```

### Data Restoration

| Component | Data Source |
|-----------|-------------|
| Stats | stats object |
| Priorities | inferred_priorities |
| Priority reasoning | priority_reasoning |
| Candidate cards | top_candidates array |
| Eliminated section | eliminated object |
| Why not others | why_not_others text |

### Session-Specific Display

When viewing a past session, the dashboard should show:
- Session date in header
- "Viewing past analysis" indicator (optional)
- All original analysis results frozen in time

### Email for Past Sessions

Email still works because:
- Candidates remain in database with their data
- sessionId is passed for context
- Job title comes from role data

### References

- [Source: docs/sprint-artifacts/tech-spec-epic-7.md#Session-Dashboard]
- [Source: docs/epics.md#Story-7.5]
- [Source: docs/prd.md#FR67]

## Dev Agent Record

### Context Reference

docs/sprint-artifacts/7-5-view-past-session-dashboard.md

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- Clicking session in History navigates to /dashboard/:sessionId
- Dashboard shows "Analysis from Dec 20, 2025" header with session date
- All session data loads: stats, priorities, eliminated section, why not others
- Email button is present and functional for past sessions

### Completion Notes List

- All 4 acceptance criteria satisfied:
  - AC7.5.1: Clicking session navigates to /dashboard/:sessionId ✅
  - AC7.5.2: Dashboard loads with session data including date ✅
  - AC7.5.3: All data restored (stats, priorities, candidates, explanations) ✅
  - AC7.5.4: Email selection works for past sessions ✅
- Most functionality already existed from previous stories
- Added session date display to dashboard header with Calendar icon
- Imported formatDate utility and Calendar icon

### File List

**Modified:**
- frontend/src/pages/DashboardPage.jsx (added session date in header with Calendar icon)

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-12-20 | SM Agent (Bob) | Initial draft created |
| 2025-12-20 | Dev Agent (Amelia) | Implementation complete - all ACs satisfied |
