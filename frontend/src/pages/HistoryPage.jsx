import { useState, useEffect } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent } from '@/components/ui/card';
import { Clock, Users, AlertCircle } from 'lucide-react';
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
        getSessions().catch(() => ({ success: false })),
        getRoles().catch(() => ({ success: false }))
      ]);

      if (sessionsRes.success) {
        setSessions(sessionsRes.data.sessions || []);
      }
      if (rolesRes.success) {
        setRoles(rolesRes.data.roles || []);
      }
    } catch (err) {
      console.error('Failed to fetch history:', err);
      setError('Failed to load history');
    } finally {
      setLoading(false);
    }
  };

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="text-center py-16">
          <AlertCircle className="h-12 w-12 text-destructive mx-auto mb-4" />
          <h3 className="text-lg font-medium mb-2">Error loading history</h3>
          <p className="text-muted-foreground mb-6">{error}</p>
          <button
            onClick={fetchData}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <h1 className="text-3xl mb-6">History</h1>

      <Card className="border-border shadow-lg">
        <CardContent className="p-6">
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
        </CardContent>
      </Card>
    </div>
  );
}

export default HistoryPage;
