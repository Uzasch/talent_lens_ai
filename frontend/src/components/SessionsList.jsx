import { useNavigate } from 'react-router-dom';
import { Calendar, Users, FileText, TrendingUp, ChevronRight, Clock } from 'lucide-react';
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
        className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
      >
        Go to Upload
      </button>
    </div>
  );
}

export default SessionsList;
