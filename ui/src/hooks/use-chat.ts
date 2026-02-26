import { useCallback, useRef } from 'react';
import { useChatStore } from '@/stores/chat-store';
import { agentApi } from '@/lib/api/agent';
import type { AgentEvent, ChunkType } from '@/lib/api/types';

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
    appendStructuredContent,
    updateProcessStatus,
    updateTodos,
    addEvent,
    finishAssistantMessage,
    setStreaming,
    clearMessages,
  } = useChatStore();

  const sendMessage = useCallback(
    async (content: string) => {
      // Get current state directly from store to avoid stale closure
      const storeState = useChatStore.getState();
      const { isStreaming: currentlyStreaming, sessionId: currentSessionId } = storeState;

      if (!currentSessionId || currentlyStreaming) {
        return;
      }

      addUserMessage(content);
      const assistantId = `assistant-${Date.now()}`;
      startAssistantMessage(assistantId);

      const handleEvent = (event: AgentEvent) => {
        addEvent(assistantId, event);

        switch (event.type) {
          case 'token':
            if (event.content) {
              const chunkType = event.chunk_type as ChunkType;
              if (chunkType && chunkType !== 'text') {
                appendStructuredContent(assistantId, chunkType, event.content);
              } else {
                appendToAssistantMessage(assistantId, event.content);
              }
            }
            break;

          // Structured chunk types from backend SSE
          case 'sql':
          case 'summary':
          case 'insights':
          case 'chart_recommendations':
          case 'reasoning':
            if (event.content) {
              appendStructuredContent(assistantId, event.type as ChunkType, event.content);
            }
            break;

          case 'text':
            if (event.content) {
              appendToAssistantMessage(assistantId, event.content);
            }
            break;

          case 'status':
            if (event.message) {
              updateProcessStatus(assistantId, event.message);
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
            appendToAssistantMessage(assistantId, `\n\nError: ${event.error || event.message}`);
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
        currentSessionId,
        content,
        handleEvent,
        handleError,
        handleComplete
      );
    },
    [
      addUserMessage,
      startAssistantMessage,
      appendToAssistantMessage,
      appendStructuredContent,
      updateProcessStatus,
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
