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
      const currentlyStreaming = storeState.isStreaming;
      const currentSessionId = storeState.sessionId;
      console.log('[useChat] sendMessage called:', {
        content,
        currentSessionId,
        currentlyStreaming,
        messageCount: storeState.messages.length
      });

      if (!currentSessionId || currentlyStreaming) {
        console.log('[useChat] sendMessage blocked:', { currentSessionId, currentlyStreaming });
        return;
      }

      console.log('[useChat] sendMessage starting:', { currentSessionId, content });
      addUserMessage(content);
      const assistantId = `assistant-${Date.now()}`;
      startAssistantMessage(assistantId);

      const handleEvent = (event: AgentEvent) => {
        addEvent(assistantId, event);

        switch (event.type) {
          case 'token':
            if (event.content) {
              // Check if this is a structured chunk
              const chunkType = event.chunk_type as ChunkType;
              if (chunkType && chunkType !== 'text') {
                // Route to structured content handler
                appendStructuredContent(assistantId, chunkType, event.content);
              } else {
                // Plain text content
                appendToAssistantMessage(assistantId, event.content);
              }
            }
            break;
          case 'status':
            // Process status updates (e.g., "Analyzing query...", "Generating SQL...")
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
