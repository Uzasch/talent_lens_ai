# Epic 7: Session & Pool History - Technical Specification

## Epic Overview

| Attribute | Value |
|-----------|-------|
| Epic ID | 7 |
| Title | Session & Pool History |
| Goal | User can view past sessions and manage candidate pools |
| User Value | Don't lose work - manage hiring pipeline! |
| FRs Covered | FR65-FR76 |
| Stories | 5 |
| Status | contexted |

---

## Architecture Context

### Component Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    History & Pool Management                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  History Page (/history)                                         │
│  ┌──────────────────────────────────────────────────────┐       │
│  │ [Sessions] [Role Pools]                               │       │
│  ├──────────────────────────────────────────────────────┤       │
│  │                                                       │       │
│  │  Sessions Tab:                                        │       │
│  │  ┌─────────────────────────────────────────────────┐ │       │
│  │  │ Python Developer        Dec 20, 2025            │ │       │
│  │  │ 10 added │ 45 total │ Top: 94%        [View →] │ │       │
│  │  ├─────────────────────────────────────────────────┤ │       │
│  │  │ React Developer         Dec 18, 2025            │ │       │
│  │  │ 8 added │ 23 total │ Top: 89%         [View →] │ │       │
│  │  └─────────────────────────────────────────────────┘ │       │
│  │                                                       │       │
│  │  Role Pools Tab:                                      │       │
│  │  ┌─────────────────────────────────────────────────┐ │       │
│  │  │ Python Developer                                 │ │       │
│  │  │ 45 candidates │ 3 sessions │ Last: Dec 20      │ │       │
│  │  ├─────────────────────────────────────────────────┤ │       │
│  │  │ React Developer                                  │ │       │
│  │  │ 23 candidates │ 2 sessions │ Last: Dec 18      │ │       │
│  │  └─────────────────────────────────────────────────┘ │       │
│  │                                                       │       │
│  └──────────────────────────────────────────────────────┘       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
                    History Page
                         │
           ┌─────────────┴─────────────┐
           ▼                           ▼
    Sessions Tab                 Role Pools Tab
           │                           │
           ▼                           ▼
  GET /api/sessions          GET /api/roles
           │                           │
           ▼                           ▼
  List of sessions           List of roles with
  with stats                 candidate counts
           │                           │
           ▼                           ▼
  Click session              Click role
           │                           │
           ▼                           ▼
  Navigate to                GET /api/roles/:id/candidates
  /dashboard/:sessionId              │
           │                           ▼
           ▼                   Pool view with
  Full dashboard             all candidates
  with saved data
```

---

## Stories Summary

| Story | Title | Focus | FRs |
|-------|-------|-------|-----|
| 7.1 | Save Session After Analysis | Persist session data | FR65, FR71-FR76 |
| 7.2 | History Page Layout | Tabs for sessions and pools | FR66 |
| 7.3 | Sessions List API | GET /api/sessions endpoint | FR66 |
| 7.4 | View Role Pool | Pool candidates view | FR68-FR70 |
| 7.5 | View Past Session Dashboard | Navigate to saved dashboard | FR67 |

---

## Technical Components

### Database Schema (Existing)

```sql
-- Sessions table (stores analysis snapshots)
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    role_id TEXT NOT NULL,
    job_description TEXT NOT NULL,
    candidates_added INTEGER NOT NULL,
    pool_size_at_analysis INTEGER NOT NULL,
    inferred_priorities TEXT,        -- JSON
    priority_reasoning TEXT,
    thresholds_config TEXT,          -- JSON
    why_not_others TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

-- Roles table (for candidate pool grouping)
CREATE TABLE roles (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    normalized_title TEXT NOT NULL,
    weights TEXT,                    -- JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(normalized_title)
);

-- Candidates table (persistent pool per role)
CREATE TABLE candidates (
    id TEXT PRIMARY KEY,
    role_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    resume_text TEXT,
    -- ... scores, summaries, etc.
    status TEXT DEFAULT 'active',
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id),
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);
```

### API Endpoints

#### GET /api/sessions

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
                (SELECT MAX(match_score) FROM candidates
                 WHERE session_id = s.id) as top_match_score
            FROM sessions s
            JOIN roles r ON s.role_id = r.id
            ORDER BY s.created_at DESC
        ''')

        sessions = [dict(row) for row in cursor.fetchall()]
        conn.close()

        # Parse JSON fields
        for session in sessions:
            session['inferred_priorities'] = json.loads(
                session.get('inferred_priorities') or '{}'
            )
            session['thresholds_config'] = json.loads(
                session.get('thresholds_config') or '{}'
            )

        return success_response({'sessions': sessions})

    except Exception as e:
        logger.error(f'Error fetching sessions: {e}')
        return error_response('FETCH_ERROR', str(e), 500)
```

#### GET /api/roles

```python
@app.route('/api/roles', methods=['GET'])
def get_roles():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                r.id,
                r.title,
                r.created_at,
                COUNT(DISTINCT c.id) as candidate_count,
                COUNT(DISTINCT s.id) as session_count,
                MAX(s.created_at) as last_analyzed
            FROM roles r
            LEFT JOIN candidates c ON r.id = c.role_id AND c.status = 'active'
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

#### GET /api/roles/:id/candidates

```python
@app.route('/api/roles/<role_id>/candidates', methods=['GET'])
def get_role_candidates(role_id):
    try:
        role = get_role_by_id(role_id)
        if not role:
            return error_response('NOT_FOUND', 'Role not found', 404)

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                c.id,
                c.name,
                c.email,
                c.match_score,
                c.rank,
                c.session_id,
                c.uploaded_at,
                s.created_at as session_date
            FROM candidates c
            JOIN sessions s ON c.session_id = s.id
            WHERE c.role_id = ? AND c.status = 'active'
            ORDER BY c.match_score DESC NULLS LAST
        ''', (role_id,))

        candidates = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return success_response({
            'role': role,
            'candidates': candidates,
            'total': len(candidates)
        })

    except Exception as e:
        logger.error(f'Error fetching role candidates: {e}')
        return error_response('FETCH_ERROR', str(e), 500)
```

---

## Frontend Components

### HistoryPage

```jsx
// src/pages/HistoryPage.jsx
import { useState, useEffect } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { getSessions, getRoles } from '@/services/api';
import SessionsList from '@/components/SessionsList';
import RolePoolsList from '@/components/RolePoolsList';

function HistoryPage() {
  const [sessions, setSessions] = useState([]);
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [sessionsRes, rolesRes] = await Promise.all([
        getSessions(),
        getRoles()
      ]);

      if (sessionsRes.success) setSessions(sessionsRes.data.sessions);
      if (rolesRes.success) setRoles(rolesRes.data.roles);
    } catch (error) {
      console.error('Failed to fetch history:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <h1 className="text-2xl font-bold mb-6">History</h1>

      <Tabs defaultValue="sessions">
        <TabsList className="grid w-full grid-cols-2 mb-6">
          <TabsTrigger value="sessions">
            Sessions ({sessions.length})
          </TabsTrigger>
          <TabsTrigger value="pools">
            Role Pools ({roles.length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="sessions">
          <SessionsList sessions={sessions} loading={loading} />
        </TabsContent>

        <TabsContent value="pools">
          <RolePoolsList roles={roles} loading={loading} />
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default HistoryPage;
```

### SessionsList Component

```jsx
// src/components/SessionsList.jsx
import { useNavigate } from 'react-router-dom';
import { Calendar, Users, TrendingUp, ChevronRight } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { formatDate } from '@/lib/utils';

function SessionsList({ sessions, loading }) {
  const navigate = useNavigate();

  if (loading) return <SessionsListSkeleton />;

  if (sessions.length === 0) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        <p>No analysis sessions yet.</p>
        <p className="text-sm mt-2">
          Upload resumes on the home page to create your first session.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {sessions.map((session) => (
        <Card
          key={session.id}
          className="cursor-pointer hover:border-primary transition-colors"
          onClick={() => navigate(`/dashboard/${session.id}`)}
        >
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <h3 className="font-semibold">{session.role_title}</h3>
                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                  <span className="flex items-center gap-1">
                    <Calendar className="h-4 w-4" />
                    {formatDate(session.created_at)}
                  </span>
                  <span className="flex items-center gap-1">
                    <Users className="h-4 w-4" />
                    {session.candidates_added} added
                  </span>
                  <span>
                    {session.pool_size_at_analysis} total
                  </span>
                  {session.top_match_score && (
                    <span className="flex items-center gap-1 text-primary">
                      <TrendingUp className="h-4 w-4" />
                      Top: {session.top_match_score}%
                    </span>
                  )}
                </div>
              </div>
              <ChevronRight className="h-5 w-5 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
```

### RolePoolsList Component

```jsx
// src/components/RolePoolsList.jsx
import { useState } from 'react';
import { Users, Clock, ChevronDown, ChevronUp } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { getRoleCandidates } from '@/services/api';
import { formatDate } from '@/lib/utils';
import PoolCandidatesTable from '@/components/PoolCandidatesTable';

function RolePoolsList({ roles, loading }) {
  const [expandedRole, setExpandedRole] = useState(null);
  const [candidates, setCandidates] = useState([]);
  const [loadingCandidates, setLoadingCandidates] = useState(false);

  const handleRoleClick = async (roleId) => {
    if (expandedRole === roleId) {
      setExpandedRole(null);
      return;
    }

    setExpandedRole(roleId);
    setLoadingCandidates(true);

    try {
      const response = await getRoleCandidates(roleId);
      if (response.success) {
        setCandidates(response.data.candidates);
      }
    } catch (error) {
      console.error('Failed to fetch candidates:', error);
    } finally {
      setLoadingCandidates(false);
    }
  };

  if (loading) return <RolePoolsListSkeleton />;

  if (roles.length === 0) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        <p>No role pools yet.</p>
        <p className="text-sm mt-2">
          Roles are created when you analyze resumes.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {roles.map((role) => (
        <Card key={role.id}>
          <CardContent className="p-0">
            <button
              className="w-full p-4 flex items-center justify-between hover:bg-muted/50 transition-colors"
              onClick={() => handleRoleClick(role.id)}
            >
              <div className="space-y-1 text-left">
                <h3 className="font-semibold">{role.title}</h3>
                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                  <span className="flex items-center gap-1">
                    <Users className="h-4 w-4" />
                    {role.candidate_count} candidates
                  </span>
                  <span>{role.session_count} sessions</span>
                  {role.last_analyzed && (
                    <span className="flex items-center gap-1">
                      <Clock className="h-4 w-4" />
                      Last: {formatDate(role.last_analyzed)}
                    </span>
                  )}
                </div>
              </div>
              {expandedRole === role.id ? (
                <ChevronUp className="h-5 w-5" />
              ) : (
                <ChevronDown className="h-5 w-5" />
              )}
            </button>

            {expandedRole === role.id && (
              <div className="border-t p-4">
                <PoolCandidatesTable
                  candidates={candidates}
                  loading={loadingCandidates}
                />
              </div>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
```

---

## API Response Formats

### GET /api/sessions Response

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
          "skills": "CRITICAL",
          "projects": "IMPORTANT"
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

### GET /api/roles Response

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

### GET /api/roles/:id/candidates Response

```json
{
  "success": true,
  "data": {
    "role": {
      "id": "role-uuid",
      "title": "Python Developer"
    },
    "candidates": [
      {
        "id": "candidate-uuid",
        "name": "Sara Ahmed",
        "email": "sara@email.com",
        "match_score": 94,
        "rank": 1,
        "session_id": "session-uuid",
        "uploaded_at": "2025-12-20T10:30:00Z",
        "session_date": "2025-12-20T10:30:00Z"
      }
    ],
    "total": 45
  }
}
```

---

## Session Data Persistence

### What Gets Saved

| Data | Storage Location | When Saved |
|------|------------------|------------|
| Session metadata | sessions table | After analysis |
| Job description | sessions.job_description | After analysis |
| Inferred priorities | sessions.inferred_priorities | After analysis |
| Thresholds config | sessions.thresholds_config | After analysis |
| Why not others | sessions.why_not_others | After analysis |
| Candidates | candidates table | During Phase 1 |
| Scores & rankings | candidates table | After Phase 2 |
| Resume text | candidates.resume_text | During Phase 1 |
| PDF files | uploads/ directory | During upload |

### Session Snapshot

When a session is created, it captures:
- Pool size at that moment
- Number of new candidates added
- Analysis results frozen in time

Future sessions see the updated pool but don't modify past session data.

---

## Navigation Flow

```
History Page
     │
     ├── Sessions Tab
     │   │
     │   └── Click session card
     │       │
     │       └── Navigate to /dashboard/:sessionId
     │           │
     │           └── Dashboard loads with saved data
     │
     └── Role Pools Tab
         │
         └── Click role card
             │
             └── Expand to show candidates
                 │
                 └── Table with all pool candidates
```

---

## Empty States

### No Sessions

```
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│              No analysis sessions yet.                       │
│                                                              │
│    Upload resumes on the home page to create your first     │
│    session.                                                  │
│                                                              │
│                    [Go to Upload →]                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### No Role Pools

```
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│              No role pools yet.                              │
│                                                              │
│    Roles are created when you analyze resumes.               │
│                                                              │
│                    [Start Analysis →]                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Date Formatting

Use consistent date formatting across the app:

```javascript
// src/lib/utils.js
export function formatDate(dateString) {
  if (!dateString) return '';

  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });
}

// Output: "Dec 20, 2025"
```

---

## Dependencies

### Frontend
- react-router-dom (navigation)
- shadcn/ui Tabs, Card, Table
- lucide-react icons

### Backend
- Existing SQLite database
- Existing models.py functions

---

## References

- [Source: docs/architecture.md#Session-History]
- [Source: docs/prd.md#FR65-FR76]
- [Source: docs/epics.md#Epic-7]

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-12-20 | SM Agent (Bob) | Initial tech spec created |
