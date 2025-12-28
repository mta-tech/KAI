'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { SessionSidebar } from '@/components/chat/session-sidebar';
import { AgentMessage } from '@/components/chat/agent-message';
import { ChatInput } from '@/components/chat/chat-input';
import { TodoList } from '@/components/chat/todo-list';
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
    setSession(session.id, session.db_connection_id);
    clearMessages();
  };

  const handleNewSession = (connId: string) => {
    createSessionMutation.mutate(connId);
  };

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
