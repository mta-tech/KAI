'use client';

import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { agentApi } from '@/lib/api/agent';
import { useConnections } from '@/hooks/use-connections';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Search, Database, Code, FileText, Clock } from 'lucide-react';
import type { SessionMessage } from '@/lib/api/types';

interface ExecutionLog extends SessionMessage {
  session_id: string;
  db_connection_id: string;
}

export default function LogsPage() {
  const [selectedConnection, setSelectedConnection] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');

  const { data: connections, isLoading: connectionsLoading } = useConnections();

  // Fetch all sessions to get execution logs
  const { data: sessionsData, isLoading: sessionsLoading } = useQuery({
    queryKey: ['agent-sessions', selectedConnection],
    queryFn: async () => {
      const connectionId = selectedConnection === 'all' ? undefined : selectedConnection;
      return agentApi.listSessions(connectionId);
    },
  });

  // Flatten all messages from all sessions into a single logs array
  const allLogs: ExecutionLog[] = (sessionsData?.sessions || []).flatMap((session) =>
    session.messages?.map((msg) => ({
      ...msg,
      session_id: session.id,
      db_connection_id: session.db_connection_id || '',
    })) || []
  );

  // Filter logs by search query
  const filteredLogs = allLogs.filter((log) => {
    if (!searchQuery) return true;
    const searchLower = searchQuery.toLowerCase();
    return (
      log.query?.toLowerCase().includes(searchLower) ||
      log.sql?.toLowerCase().includes(searchLower) ||
      log.analysis?.toLowerCase().includes(searchLower)
    );
  });

  // Sort by timestamp descending (newest first)
  const sortedLogs = [...filteredLogs].sort(
    (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );

  const isLoading = connectionsLoading || sessionsLoading;

  if (isLoading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="space-y-4">
            <Skeleton className="h-12 w-full" />
            <Skeleton className="h-32 w-full" />
            <Skeleton className="h-32 w-full" />
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-muted-foreground">
            View query execution logs and analysis history.
          </p>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Search queries, SQL, or analysis..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9"
                />
              </div>
            </div>
            <Select value={selectedConnection} onValueChange={setSelectedConnection}>
              <SelectTrigger className="w-[200px]">
                <SelectValue placeholder="All connections" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All connections</SelectItem>
                {connections?.map((conn) => (
                  <SelectItem key={conn.id} value={conn.id}>
                    {conn.alias}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Logs List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Execution Logs ({sortedLogs.length})</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {sortedLogs.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <FileText className="mb-4 h-12 w-12 text-muted-foreground" />
              <h3 className="mb-2 text-lg font-semibold">No execution logs found</h3>
              <p className="text-sm text-muted-foreground">
                {searchQuery
                  ? 'Try adjusting your search filters'
                  : 'Start a chat session to see query execution logs here'}
              </p>
            </div>
          ) : (
            <ScrollArea className="h-[600px]">
              <div className="space-y-4">
                {sortedLogs.map((log) => {
                  const connection = connections?.find(
                    (c) => c.id === log.db_connection_id
                  );

                  return (
                    <div
                      key={log.id}
                      className="rounded-lg border p-4 hover:bg-muted/50 transition-colors"
                    >
                      {/* Header */}
                      <div className="mb-3 flex items-start justify-between">
                        <div className="flex items-center gap-2">
                          <Database className="h-4 w-4 text-muted-foreground" />
                          <span className="text-sm font-medium">
                            {connection?.alias || 'Unknown connection'}
                          </span>
                          <Badge variant="outline" className="text-xs">
                            Session {log.session_id.slice(0, 8)}
                          </Badge>
                        </div>
                        <div className="flex items-center gap-1 text-xs text-muted-foreground">
                          <Clock className="h-3 w-3" />
                          {new Date(log.timestamp).toLocaleString()}
                        </div>
                      </div>

                      {/* Query */}
                      <div className="mb-2">
                        <div className="mb-1 text-xs font-semibold text-muted-foreground">
                          Query
                        </div>
                        <div className="rounded bg-muted p-2 text-sm">
                          {log.query}
                        </div>
                      </div>

                      {/* SQL */}
                      {log.sql && (
                        <div className="mb-2">
                          <div className="mb-1 flex items-center gap-1 text-xs font-semibold text-muted-foreground">
                            <Code className="h-3 w-3" />
                            Generated SQL
                          </div>
                          <div className="rounded bg-muted p-2 font-mono text-xs">
                            <pre className="overflow-x-auto whitespace-pre-wrap">
                              {log.sql}
                            </pre>
                          </div>
                        </div>
                      )}

                      {/* Results Summary */}
                      {log.results_summary && (
                        <div className="mb-2">
                          <div className="mb-1 text-xs font-semibold text-muted-foreground">
                            Results Summary
                          </div>
                          <div className="rounded bg-muted p-2 text-sm">
                            {log.results_summary}
                          </div>
                        </div>
                      )}

                      {/* Analysis */}
                      {log.analysis && (
                        <div>
                          <div className="mb-1 text-xs font-semibold text-muted-foreground">
                            Analysis
                          </div>
                          <div className="rounded bg-muted p-2 text-sm">
                            {log.analysis}
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </ScrollArea>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
