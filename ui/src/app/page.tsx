'use client';

import { useQuery } from '@tanstack/react-query';
import { Database, Table2, Layers, MessageSquare } from 'lucide-react';
import { StatsCard } from '@/components/dashboard/stats-card';
import { QuickActions } from '@/components/dashboard/quick-actions';
import { connectionsApi } from '@/lib/api/connections';
import { mdlApi } from '@/lib/api/mdl';
import { agentApi } from '@/lib/api/agent';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export default function DashboardPage() {
  const { data: connections = [] } = useQuery({
    queryKey: ['connections'],
    queryFn: connectionsApi.list,
  });

  const { data: manifests = [] } = useQuery({
    queryKey: ['mdl-manifests'],
    queryFn: () => mdlApi.list(),
  });

  const { data: sessionsData } = useQuery({
    queryKey: ['agent-sessions'],
    queryFn: () => agentApi.listSessions(),
  });

  const sessions = sessionsData?.sessions || [];

  return (
    <div className="h-full overflow-auto p-6 space-y-6">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Connections"
          value={connections.length}
          description="Active database connections"
          icon={Database}
        />
        <StatsCard
          title="MDL Manifests"
          value={manifests.length}
          description="Semantic layer definitions"
          icon={Layers}
        />
        <StatsCard
          title="Active Sessions"
          value={sessions.filter(s => s.status === 'active').length}
          description="Chat sessions"
          icon={MessageSquare}
        />
        <StatsCard
          title="Tables Scanned"
          value="-"
          description="With AI descriptions"
          icon={Table2}
        />
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <QuickActions />

        <Card>
          <CardHeader>
            <CardTitle>Recent Sessions</CardTitle>
          </CardHeader>
          <CardContent>
            {sessions.length === 0 ? (
              <p className="text-sm text-muted-foreground">No recent sessions</p>
            ) : (
              <div className="space-y-2">
                {sessions.slice(0, 5).map((session) => (
                  <div
                    key={session.id}
                    className="flex items-center justify-between rounded-md border p-2"
                  >
                    <div>
                      <p className="text-sm font-medium">
                        {session.title || `Session ${session.id.slice(0, 8)}`}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {new Date(session.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <Badge variant={session.status === 'active' ? 'default' : 'secondary'}>
                      {session.status}
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
