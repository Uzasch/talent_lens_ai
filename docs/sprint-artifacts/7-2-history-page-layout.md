# Story 7.2: History Page Layout

Status: review

## Story

As a **HR professional**,
I want **to see past sessions and role pools**,
So that **I can manage hiring pipeline**.

## Acceptance Criteria

1. **AC7.2.1:** History page has two tabs/sections: Sessions and Role Pools
2. **AC7.2.2:** Sessions show: role, date, candidates added, pool size at time
3. **AC7.2.3:** Role pools show: title, total candidates, last analyzed
4. **AC7.2.4:** Empty states shown when no data exists

## Tasks / Subtasks

- [ ] **Task 1: Create HistoryPage component** (AC: 7.2.1)
  - [ ] Create `src/pages/HistoryPage.jsx`:
    ```jsx
    import { useState, useEffect } from 'react';
    import { useNavigate } from 'react-router-dom';
    import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
    import { Clock, Users } from 'lucide-react';
    import { getSessions, getRoles } from '@/services/api';
    import SessionsList from '@/components/SessionsList';
    import RolePoolsList from '@/components/RolePoolsList';

    function HistoryPage() {
      const [sessions, setSessions] = useState([]);
      const [roles, setRoles] = useState([]);
      const [loading, setLoading] = useState(true);
      const [error, setError] = useState(null);

      useEffect(() => {
        fetchData();
      }, []);

      const fetchData = async () => {
        setLoading(true);
        setError(null);

        try {
          const [sessionsRes, rolesRes] = await Promise.all([
            getSessions(),
            getRoles()
          ]);

          if (sessionsRes.success) {
            setSessions(sessionsRes.data.sessions);
          }
          if (rolesRes.success) {
            setRoles(rolesRes.data.roles);
          }
        } catch (err) {
          console.error('Failed to fetch history:', err);
          setError('Failed to load history');
        } finally {
          setLoading(false);
        }
      };

      return (
        <div className="container mx-auto px-4 py-8 max-w-4xl">
          <h1 className="text-2xl font-bold mb-6">History</h1>

          <Tabs defaultValue="sessions" className="w-full">
            <TabsList className="grid w-full grid-cols-2 mb-6">
              <TabsTrigger value="sessions" className="flex items-center gap-2">
                <Clock className="h-4 w-4" />
                Sessions ({sessions.length})
              </TabsTrigger>
              <TabsTrigger value="pools" className="flex items-center gap-2">
                <Users className="h-4 w-4" />
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

- [ ] **Task 2: Create SessionsList component** (AC: 7.2.2)
  - [ ] Create `src/components/SessionsList.jsx`:
    ```jsx
    import { useNavigate } from 'react-router-dom';
    import { Calendar, Users, TrendingUp, ChevronRight, FileText } from 'lucide-react';
    import { Card, CardContent } from '@/components/ui/card';
    import { Skeleton } from '@/components/ui/skeleton';
    import { formatDate } from '@/lib/utils';

    function SessionsList({ sessions, loading }) {
      const navigate = useNavigate();

      if (loading) {
        return (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <Card key={i}>
                <CardContent className="p-4">
                  <Skeleton className="h-6 w-48 mb-2" />
                  <Skeleton className="h-4 w-72" />
                </CardContent>
              </Card>
            ))}
          </div>
        );
      }

      if (sessions.length === 0) {
        return <EmptySessionsState />;
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
                  <div className="space-y-2">
                    <h3 className="font-semibold text-lg">
                      {session.role_title}
                    </h3>

                    <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Calendar className="h-4 w-4" />
                        {formatDate(session.created_at)}
                      </span>

                      <span className="flex items-center gap-1">
                        <FileText className="h-4 w-4" />
                        {session.candidates_added} added
                      </span>

                      <span className="flex items-center gap-1">
                        <Users className="h-4 w-4" />
                        {session.pool_size_at_analysis} total
                      </span>

                      {session.top_match_score && (
                        <span className="flex items-center gap-1 text-primary font-medium">
                          <TrendingUp className="h-4 w-4" />
                          Top: {session.top_match_score}%
                        </span>
                      )}
                    </div>
                  </div>

                  <ChevronRight className="h-5 w-5 text-muted-foreground flex-shrink-0" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      );
    }

    function EmptySessionsState() {
      const navigate = useNavigate();

      return (
        <div className="text-center py-16">
          <Clock className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-medium mb-2">No analysis sessions yet</h3>
          <p className="text-muted-foreground mb-6">
            Upload resumes on the home page to create your first session.
          </p>
          <button
            onClick={() => navigate('/')}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-lg"
          >
            Go to Upload
          </button>
        </div>
      );
    }

    export default SessionsList;
    ```

- [ ] **Task 3: Create RolePoolsList component** (AC: 7.2.3)
  - [ ] Create `src/components/RolePoolsList.jsx`:
    ```jsx
    import { useState } from 'react';
    import { useNavigate } from 'react-router-dom';
    import { Users, Clock, Briefcase, ChevronDown, ChevronUp } from 'lucide-react';
    import { Card, CardContent } from '@/components/ui/card';
    import { Skeleton } from '@/components/ui/skeleton';
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

      if (loading) {
        return (
          <div className="space-y-3">
            {[1, 2].map((i) => (
              <Card key={i}>
                <CardContent className="p-4">
                  <Skeleton className="h-6 w-48 mb-2" />
                  <Skeleton className="h-4 w-64" />
                </CardContent>
              </Card>
            ))}
          </div>
        );
      }

      if (roles.length === 0) {
        return <EmptyRolePoolsState />;
      }

      return (
        <div className="space-y-3">
          {roles.map((role) => (
            <Card key={role.id}>
              <CardContent className="p-0">
                <button
                  className="w-full p-4 flex items-center justify-between hover:bg-muted/50 transition-colors text-left"
                  onClick={() => handleRoleClick(role.id)}
                >
                  <div className="space-y-2">
                    <h3 className="font-semibold text-lg">{role.title}</h3>

                    <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Users className="h-4 w-4" />
                        {role.candidate_count} candidates
                      </span>

                      <span className="flex items-center gap-1">
                        <Briefcase className="h-4 w-4" />
                        {role.session_count} sessions
                      </span>

                      {role.last_analyzed && (
                        <span className="flex items-center gap-1">
                          <Clock className="h-4 w-4" />
                          Last: {formatDate(role.last_analyzed)}
                        </span>
                      )}
                    </div>
                  </div>

                  {expandedRole === role.id ? (
                    <ChevronUp className="h-5 w-5 text-muted-foreground" />
                  ) : (
                    <ChevronDown className="h-5 w-5 text-muted-foreground" />
                  )}
                </button>

                {expandedRole === role.id && (
                  <div className="border-t px-4 py-4">
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

    function EmptyRolePoolsState() {
      const navigate = useNavigate();

      return (
        <div className="text-center py-16">
          <Users className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-medium mb-2">No role pools yet</h3>
          <p className="text-muted-foreground mb-6">
            Roles are created when you analyze resumes.
          </p>
          <button
            onClick={() => navigate('/')}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-lg"
          >
            Start Analysis
          </button>
        </div>
      );
    }

    export default RolePoolsList;
    ```

- [ ] **Task 4: Add formatDate utility** (AC: 7.2.2, 7.2.3)
  - [ ] Add to `src/lib/utils.js`:
    ```javascript
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

- [ ] **Task 5: Add Tabs component from shadcn** (AC: 7.2.1)
  - [ ] Run: `npx shadcn@latest add tabs`

- [ ] **Task 6: Test history page**
  - [ ] Verify tabs switch correctly
  - [ ] Verify sessions display all fields
  - [ ] Verify role pools display all fields
  - [ ] Verify empty states shown when no data
  - [ ] Verify clicking session navigates to dashboard

## Dev Notes

### Architecture Alignment

This story creates the History page UI:
- **Tabs:** Sessions vs Role Pools views
- **Data:** Fetched from GET /api/sessions and GET /api/roles
- **Navigation:** Click session to go to dashboard

### Page Layout

```
┌─────────────────────────────────────────────────────────────┐
│ History                                                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ [Sessions (5)]  [Role Pools (3)]                            │
│ ═══════════════                                              │
│                                                              │
│ Sessions Tab:                                                │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Python Developer                                      > │ │
│ │ Dec 20, 2025 │ 10 added │ 45 total │ Top: 94%          │ │
│ ├─────────────────────────────────────────────────────────┤ │
│ │ React Developer                                       > │ │
│ │ Dec 18, 2025 │ 8 added │ 23 total │ Top: 89%           │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Session Card Fields

| Field | Source |
|-------|--------|
| Role title | session.role_title |
| Date | session.created_at |
| Added | session.candidates_added |
| Total | session.pool_size_at_analysis |
| Top score | session.top_match_score |

### Role Pool Card Fields

| Field | Source |
|-------|--------|
| Title | role.title |
| Candidates | role.candidate_count |
| Sessions | role.session_count |
| Last analyzed | role.last_analyzed |

### Empty State Conditions

| State | Condition |
|-------|-----------|
| No sessions | sessions.length === 0 |
| No pools | roles.length === 0 |

### References

- [Source: docs/sprint-artifacts/tech-spec-epic-7.md#History-Page]
- [Source: docs/epics.md#Story-7.2]
- [Source: docs/prd.md#FR66]

## Dev Agent Record

### Context Reference

docs/sprint-artifacts/7-2-history-page-layout.md

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- History page loads with tabs switching correctly
- Sessions tab shows: role title, date (Dec 20, 2025), candidates added (5), pool size (10)
- Role Pools tab shows: title, 0 candidates, 1 sessions, Last: Dec 20, 2025
- APIs tested: GET /api/sessions returns session list, GET /api/roles returns roles with session_count and last_analyzed

### Completion Notes List

- All 4 acceptance criteria satisfied:
  - AC7.2.1: History page has Sessions and Role Pools tabs ✅
  - AC7.2.2: Sessions show role, date, candidates added, pool size, top score ✅
  - AC7.2.3: Role pools show title, candidate count, session count, last analyzed ✅
  - AC7.2.4: Empty states implemented for both tabs ✅
- Added GET /api/sessions endpoint for listing all sessions
- Updated GET /api/roles to include session_count and last_analyzed
- Added formatDate utility function
- Created SessionsList and RolePoolsList components with loading skeletons

### File List

**Created:**
- frontend/src/pages/HistoryPage.jsx (updated from placeholder)
- frontend/src/components/SessionsList.jsx
- frontend/src/components/RolePoolsList.jsx

**Modified:**
- frontend/src/lib/utils.js (added formatDate function)
- frontend/src/services/api.js (added getSessions, getRoleCandidates functions)
- backend/app.py (added GET /api/sessions endpoint)
- backend/models.py (added get_all_sessions, updated get_roles with session_count/last_analyzed)

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-12-20 | SM Agent (Bob) | Initial draft created |
| 2025-12-20 | Dev Agent (Amelia) | Implementation complete - all ACs satisfied |
