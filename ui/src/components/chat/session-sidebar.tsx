'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { EmptyState } from '@/components/ui/empty-state';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Plus, MessageSquare, Trash2, Menu } from 'lucide-react';
import { useConnections } from '@/hooks/use-connections';
import { useSidebarStore } from '@/stores/sidebar-store';
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
  const [isOpen, setIsOpen] = useState(false);
  const queryClient = useQueryClient();
  const { isMobile } = useSidebarStore();

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
      // Close sheet on mobile after creating session
      if (isMobile) {
        setIsOpen(false);
      }
    }
  };

  const handleSelectSession = (session: AgentSession) => {
    onSelectSession(session);
    // Close sheet on mobile after selecting session
    if (isMobile) {
      setIsOpen(false);
    }
  };

  const handleDeleteSession = (e: React.MouseEvent, sessionId: string) => {
    e.stopPropagation();
    deleteMutation.mutate(sessionId);
  };

  // Desktop sidebar - always visible
  if (!isMobile) {
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
              <div className="p-4">
                <EmptyState
                  icon={MessageSquare}
                  title="No chat sessions yet"
                  description="Start a new conversation with your database to begin analyzing data."
                  action={{
                    label: "Start New Session",
                    onClick: handleNewSession,
                    variant: connectionId ? "default" : "secondary",
                  }}
                />
              </div>
            ) : (
              sessions.map((session) => (
                <div
                  key={session.id}
                  className={cn(
                    'group flex items-center justify-between rounded-md p-2 text-sm hover:bg-muted',
                    selectedSessionId === session.id && 'bg-muted'
                  )}
                >
                  <Button
                    variant="ghost"
                    className="flex flex-1 items-center gap-2 justify-start px-2 h-auto hover:bg-accent"
                    onClick={() => handleSelectSession(session)}
                    aria-label={`Open ${session.title || `Session ${session.id.slice(0, 8)}`}`}
                  >
                    <MessageSquare className="h-4 w-4" aria-hidden="true" />
                    <span className="truncate">
                      {session.title || `Session ${session.id.slice(0, 8)}`}
                    </span>
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="opacity-0 group-hover:opacity-100 h-8 w-8 p-0"
                    onClick={(e) => handleDeleteSession(e, session.id)}
                    aria-label={`Delete ${session.title || `Session ${session.id.slice(0, 8)}`}`}
                  >
                    <Trash2 className="h-3 w-3" aria-hidden="true" />
                  </Button>
                </div>
              ))
            )}
          </div>
        </ScrollArea>
      </div>
    );
  }

  // Mobile sidebar - sheet/drawer
  return (
    <Sheet open={isOpen} onOpenChange={setIsOpen}>
      <SheetTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          className="h-11 w-11 shrink-0"
          aria-label="Open chat sessions"
        >
          <Menu className="h-5 w-5" />
        </Button>
      </SheetTrigger>
      <SheetContent side="left" className="w-full sm:w-80 p-0 flex flex-col">
        <SheetHeader className="border-b p-4 space-y-3">
          <SheetTitle>Chat Sessions</SheetTitle>
          <div className="space-y-2">
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
              size="default"
              onClick={handleNewSession}
              disabled={!connectionId}
            >
              <Plus className="mr-2 h-4 w-4" />
              New Session
            </Button>
          </div>
        </SheetHeader>

        <ScrollArea className="flex-1">
          <div className="p-3 space-y-2">
            {sessions.length === 0 ? (
              <div className="py-8">
                <EmptyState
                  icon={MessageSquare}
                  title="No chat sessions yet"
                  description="Start a new conversation with your database to begin analyzing data."
                  action={{
                    label: "Start New Session",
                    onClick: handleNewSession,
                    variant: connectionId ? "default" : "secondary",
                  }}
                />
              </div>
            ) : (
              sessions.map((session) => (
                <div
                  key={session.id}
                  className={cn(
                    'group flex items-center gap-2 rounded-lg p-3 text-sm transition-colors',
                    selectedSessionId === session.id
                      ? 'bg-muted border border-border'
                      : 'hover:bg-muted/50 border border-transparent'
                  )}
                >
                  <Button
                    variant="ghost"
                    className="flex flex-1 items-center gap-3 justify-start px-2 h-12 hover:bg-transparent"
                    onClick={() => handleSelectSession(session)}
                    aria-label={`Open ${session.title || `Session ${session.id.slice(0, 8)}`}`}
                  >
                    <MessageSquare className="h-5 w-5 shrink-0" aria-hidden="true" />
                    <span className="truncate font-medium">
                      {session.title || `Session ${session.id.slice(0, 8)}`}
                    </span>
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-11 w-11 shrink-0 hover:bg-destructive/10 hover:text-destructive"
                    onClick={(e) => handleDeleteSession(e, session.id)}
                    aria-label={`Delete ${session.title || `Session ${session.id.slice(0, 8)}`}`}
                  >
                    <Trash2 className="h-4 w-4" aria-hidden="true" />
                  </Button>
                </div>
              ))
            )}
          </div>
        </ScrollArea>
      </SheetContent>
    </Sheet>
  );
}
