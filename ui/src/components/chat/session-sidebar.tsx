'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Plus, MessageSquare, Trash2 } from 'lucide-react';
import { useConnections } from '@/hooks/use-connections';
import { agentApi } from '@/lib/api/agent';
import type { AgentSession } from '@/lib/api/types';
import { cn } from '@/lib/utils';

interface SessionSidebarProps {
  selectedSessionId: string | null;
  onSelectSession: (session: AgentSession) => void;
  onNewSession: (connectionId: string) => void;
}

export function SessionSidebar({
  selectedSessionId,
  onSelectSession,
  onNewSession,
}: SessionSidebarProps) {
  const [connectionId, setConnectionId] = useState<string>('');
  const queryClient = useQueryClient();

  const { data: connections = [] } = useConnections();
  const { data: sessionsData } = useQuery({
    queryKey: ['agent-sessions', connectionId],
    queryFn: () => agentApi.listSessions(connectionId || undefined),
  });

  const deleteMutation = useMutation({
    mutationFn: agentApi.deleteSession,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agent-sessions'] });
    },
  });

  const sessions = sessionsData?.sessions || [];

  const handleNewSession = () => {
    if (connectionId) {
      onNewSession(connectionId);
    }
  };

  return (
    <div className="flex h-full w-64 flex-col border-r">
      <div className="space-y-2 border-b p-3">
        <Select value={connectionId} onValueChange={setConnectionId}>
          <SelectTrigger>
            <SelectValue placeholder="Select connection" />
          </SelectTrigger>
          <SelectContent>
            {connections.map((conn) => (
              <SelectItem key={conn.id} value={conn.id}>
                {conn.alias || conn.id.slice(0, 8)}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Button
          className="w-full"
          size="sm"
          onClick={handleNewSession}
          disabled={!connectionId}
        >
          <Plus className="mr-2 h-4 w-4" />
          New Session
        </Button>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-2 space-y-1">
          {sessions.length === 0 ? (
            <p className="p-2 text-sm text-muted-foreground">
              No sessions yet
            </p>
          ) : (
            sessions.map((session) => (
              <div
                key={session.id}
                className={cn(
                  'group flex items-center justify-between rounded-md p-2 text-sm hover:bg-muted',
                  selectedSessionId === session.id && 'bg-muted'
                )}
              >
                <button
                  className="flex flex-1 items-center gap-2 text-left"
                  onClick={() => onSelectSession(session)}
                >
                  <MessageSquare className="h-4 w-4" />
                  <span className="truncate">
                    {session.title || `Session ${session.id.slice(0, 8)}`}
                  </span>
                </button>
                <Button
                  variant="ghost"
                  size="sm"
                  className="opacity-0 group-hover:opacity-100"
                  onClick={() => deleteMutation.mutate(session.id)}
                >
                  <Trash2 className="h-3 w-3" />
                </Button>
              </div>
            ))
          )}
        </div>
      </ScrollArea>
    </div>
  );
}
