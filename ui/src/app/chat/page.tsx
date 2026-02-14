'use client';

import { useState, useEffect } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { SessionSidebar } from '@/components/chat/session-sidebar';
import { AgentMessage } from '@/components/chat/agent-message';
import { ChatInput } from '@/components/chat/chat-input';
import { TodoList } from '@/components/chat/todo-list';
import { MissionPlan } from '@/components/chat/mission-plan';
import { MissionFeedback } from '@/components/chat/mission-feedback';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useChat } from '@/hooks/use-chat';
import { agentApi } from '@/lib/api/agent';
import type { AgentSession } from '@/lib/api/types';

export default function ChatPage() {
  const queryClient = useQueryClient();
  const {
    sessionId,
    messages,
    currentTodos,
    isStreaming,
    setSession,
    sendMessage,
    stopStreaming,
    clearMessages,
  } = useChat();

  const [showMissionPanel, setShowMissionPanel] = useState(false);

  const createSessionMutation = useMutation({
    mutationFn: (connId: string) =>
      agentApi.createSession({ db_connection_id: connId }),
    onSuccess: (data, connId) => {
      setSession(data.session_id, connId);
      clearMessages();
      queryClient.invalidateQueries({ queryKey: ['agent-sessions'] });
    },
  });

  const handleSelectSession = (session: AgentSession) => {
    setSession(session.id, session.db_connection_id || '');
    clearMessages();
    setShowMissionPanel(false);
  };

  const handleNewSession = (connId: string) => {
    createSessionMutation.mutate(connId);
    setShowMissionPanel(false);
  };

  // Get the last assistant message to check for mission events
  const lastAssistantMessage = messages.filter(m => m.role === 'assistant').pop();
  const missionEvents = lastAssistantMessage?.missionEvents || [];
  const hasMissionEvents = missionEvents.length > 0;
  const isMissionComplete = missionEvents.some(e => e.type === 'mission_complete');

  // Auto-show mission panel when mission completes
  useEffect(() => {
    if (isMissionComplete && hasMissionEvents && !showMissionPanel) {
      setShowMissionPanel(true);
    }
  }, [isMissionComplete, hasMissionEvents, showMissionPanel]);

  const latestMissionId = missionEvents.length > 0 ? missionEvents[0].mission_id : sessionId || '';

  return (
    <div className="flex h-full">
      <SessionSidebar
        selectedSessionId={sessionId}
        onSelectSession={handleSelectSession}
        onNewSession={handleNewSession}
      />

      <div className="flex flex-1 flex-col">
        {!sessionId ? (
          <div className="flex flex-1 items-center justify-center text-muted-foreground">
            Select or create a session to start chatting
          </div>
        ) : (
          <>
            {isStreaming && currentTodos.length > 0 && (
              <div className="border-b p-4">
                <TodoList todos={currentTodos} />
              </div>
            )}

            <ScrollArea className="flex-1 p-4">
              <div className="space-y-4">
                {messages.map((message) => (
                  <AgentMessage key={message.id} message={message} />
                ))}
              </div>
            </ScrollArea>

            {/* Mission Controls Panel */}
            {hasMissionEvents && (
              <div className="border-t">
                <button
                  onClick={() => setShowMissionPanel(!showMissionPanel)}
                  className="w-full px-4 py-2 text-left text-sm font-medium text-muted-foreground hover:bg-accent/50 transition-colors"
                >
                  {showMissionPanel ? '▼' : '▶'} Mission Controls
                </button>
                {showMissionPanel && (
                  <div className="border-t p-4 space-y-4 max-h-96 overflow-y-auto">
                    {/* Mission Plan Inspection */}
                    <MissionPlan missionEvents={missionEvents} missionId={latestMissionId} />

                    {/* Feedback Form */}
                    <MissionFeedback missionId={latestMissionId} />
                  </div>
                )}
              </div>
            )}

            <div className="border-t p-4">
              <ChatInput
                onSend={sendMessage}
                onStop={stopStreaming}
                isStreaming={isStreaming}
                disabled={!sessionId}
              />
            </div>
          </>
        )}
      </div>
    </div>
  );
}

// Import useState
import { useState } from 'react';
