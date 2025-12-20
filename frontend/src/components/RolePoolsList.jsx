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

                  {role.session_count !== undefined && (
                    <span className="flex items-center gap-1">
                      <Briefcase className="h-4 w-4" />
                      {role.session_count} sessions
                    </span>
                  )}

                  {role.last_analyzed && (
                    <span className="flex items-center gap-1">
                      <Clock className="h-4 w-4" />
                      Last: {formatDate(role.last_analyzed)}
                    </span>
                  )}

                  {role.created_at && !role.last_analyzed && (
                    <span className="flex items-center gap-1">
                      <Clock className="h-4 w-4" />
                      Created: {formatDate(role.created_at)}
                    </span>
                  )}
                </div>
              </div>

              {expandedRole === role.id ? (
                <ChevronUp className="h-5 w-5 text-muted-foreground flex-shrink-0" />
              ) : (
                <ChevronDown className="h-5 w-5 text-muted-foreground flex-shrink-0" />
              )}
            </button>

            {expandedRole === role.id && (
              <div className="border-t">
                <div className="px-4 py-2 bg-muted/30 flex items-center justify-between">
                  <span className="text-sm font-medium">
                    {candidates.length} candidates in pool
                  </span>
                  <span className="text-xs text-muted-foreground">
                    Sorted by match score
                  </span>
                </div>
                <div className="px-4 py-4">
                  <PoolCandidatesTable
                    candidates={candidates}
                    loading={loadingCandidates}
                  />
                </div>
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
        className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
      >
        Start Analysis
      </button>
    </div>
  );
}

export default RolePoolsList;
