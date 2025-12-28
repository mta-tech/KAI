import { useCallback, useRef } from 'react';
import { useChatStore } from '@/stores/chat-store';
import { agentApi } from '@/lib/api/agent';
import type { AgentEvent } from '@/lib/api/types';

export function useChat() {
  const abortRef = useRef<(() => void) | null>(null);

  const {
    sessionId,
    connectionId,
    messages,
    currentTodos,
    isStreaming,
    setSession,
    addUserMessage,
    startAssistantMessage,
    appendToAssistantMessage,
    updateTodos,
    addEvent,
    finishAssistantMessage,
    setStreaming,
    clearMessages,
  } = useChatStore();

  const sendMessage = useCallback(
    async (content: string) => {
      if (!sessionId || isStreaming) return;

      addUserMessage(content);
      const assistantId = `assistant-${Date.now()}`;
      startAssistantMessage(assistantId);

      const handleEvent = (event: AgentEvent) => {
        addEvent(assistantId, event);

        switch (event.type) {
          case 'token':
            if (event.content) {
              appendToAssistantMessage(assistantId, event.content);
            }
            break;
          case 'todo_update':
            if (event.todos) {
              updateTodos(event.todos);
            }
            break;
          case 'done':
            finishAssistantMessage(assistantId);
            break;
          case 'error':
            appendToAssistantMessage(assistantId, `\n\nError: ${event.error}`);
            finishAssistantMessage(assistantId);
            break;
        }
      };

      const handleError = (error: Error) => {
        appendToAssistantMessage(assistantId, `\n\nConnection error: ${error.message}`);
        finishAssistantMessage(assistantId);
      };

      const handleComplete = () => {
        finishAssistantMessage(assistantId);
      };

      abortRef.current = agentApi.streamTask(
        sessionId,
        content,
        handleEvent,
        handleError,
        handleComplete
      );
    },
    [
      sessionId,
      isStreaming,
      addUserMessage,
      startAssistantMessage,
      appendToAssistantMessage,
      updateTodos,
      addEvent,
      finishAssistantMessage,
    ]
  );

  const stopStreaming = useCallback(() => {
    if (abortRef.current) {
      abortRef.current();
      abortRef.current = null;
      setStreaming(false);
    }
  }, [setStreaming]);

  return {
    sessionId,
    connectionId,
    messages,
    currentTodos,
    isStreaming,
    setSession,
    sendMessage,
    stopStreaming,
    clearMessages,
  };
}
